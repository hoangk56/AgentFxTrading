"""Bot telemetry and portfolio reporting routes: /api/tick, /portfolio/*, account list.

The portfolio manager is read through app.portfolio.get_portfolio_manager() at call time (one shared
place: app.portfolio.portfolio_manager), so a test replaces it there.
"""
import logging
from typing import Optional

from fastapi import APIRouter

from app.accounts import get_account_registry
from app.bot_controls import sanitize_bot_id
from app.cbot_watchdog import record_bot_tick
from app.dashboard import broadcast_event, broadcast_tick, broadcast_update, tick_levels
from app.logging_setup import log_throttled
from app.portfolio import get_portfolio_manager

logger = logging.getLogger("AgentFxTrading")

router = APIRouter()


def _unreadable(bot_id: str, field: str, value) -> None:
    """A field the bot sent that the server cannot read: dropped as before, but logged (once a minute per bot and
    field), so a cBot build that sends garbage shows in the log instead of quietly losing data."""
    log_throttled(logger, logging.WARNING, ("unreadable", bot_id, field),
                  f"Bot {bot_id} sent an unreadable {field}: {value!r}; ignored")


def _number(payload: dict, key: str, bot_id: str, field: Optional[str] = None) -> Optional[float]:
    """A number from a bot's payload; None when missing (null or ""), and when unreadable."""
    value = payload.get(key)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        _unreadable(bot_id, field or key, value)
        return None


def _broadcast_failed(kind: str, e: Exception) -> None:
    """The report is booked either way; the dashboard only misses this refresh."""
    log_throttled(logger, logging.WARNING, ("broadcast", kind, type(e).__name__),
                  f"Dashboard {kind} broadcast failed: {type(e).__name__}: {e}")


@router.post("/api/tick")
@router.post("/api/telemetry_tick")
async def handle_telemetry_tick(request: dict):
    """
    Direct tick telemetry endpoint from cBots (Gotobi or Crypto Donchian).
    Updates account equity/balance and live market prices in portfolio manager.
    """
    try:
        bot_id = sanitize_bot_id(request.get("bot_id", "default"))
        account_number = str(request.get("account_number", "0"))
        registry = get_account_registry()
        account_type = request.get("account_type")
        if not account_type:
            account_type = registry.get_account_type(account_number) or "demo"
        account_type = str(account_type)
        account_label = request.get("account_label")
        balance = float(request.get("balance", request.get("equity", 0.0)) or 0.0)
        equity = float(request.get("equity", request.get("balance", 0.0)) or 0.0)
        
        account_id = registry.upsert_from_bot(
            account_number=account_number,
            account_type=account_type,
            label=account_label,
            balance=balance,
            equity=equity
        )
        
        symbol = request.get("symbol")
        bid = float(request.get("bid", 0.0) or 0.0)
        ask = float(request.get("ask", 0.0) or 0.0)
        if symbol and (bid > 0 or ask > 0):
            get_portfolio_manager().update_market_price(symbol, bid, ask, bot_id=bot_id)
            record_bot_tick(bot_id, request.get("last_bar"))

        # A tick carries its own P&L sample, so refreshing the dashboard costs one small
        # broadcast instead of rebuilding the whole positions payload for three account
        # scopes from the database (~86 ms of CPU per tick - a 1 Hz stream cannot afford it).
        pnl = _number(request, "pnl", bot_id)
        pips = _number(request, "pips", bot_id)
        # The bots post a `positions` list instead of flat fields; its first entry is the
        # position the dashboard row shows (one per bot).
        levels = tick_levels(request)
        positions = request.get("positions")
        if pnl is None and isinstance(positions, list) and positions and isinstance(positions[0], dict):
            first = positions[0]
            pnl = _number(first, "net_profit", bot_id, "positions[0].net_profit")
            pips = _number(first, "pips", bot_id, "positions[0].pips")
            levels = tick_levels(first)
        if pnl is not None:
            get_portfolio_manager().update_position_metrics(bot_id, pnl, pips or 0.0, account_id=account_id,
                                                            levels=levels)

        try:
            await broadcast_tick(symbol=symbol, bid=bid, ask=ask, account_id=account_id,
                                 bot_id=bot_id, pnl=pnl, pips=pips, levels=levels)
        except Exception as e:
            _broadcast_failed("tick", e)
            
        return {"status": "ok", "account_id": account_id}
    except Exception as e:
        logger.error(f"Telemetry tick error: {e}")
        return {"status": "error", "message": str(e)}


def _positive_number(payload: dict, key: str, bot_id: str) -> Optional[float]:
    """A price, size or distance from a bot report; None when missing, unreadable or not positive."""
    number = _number(payload, key, bot_id)
    return number if number is not None and number > 0 else None


def _level_price(payload: dict, key: str, bot_id: str) -> Optional[float]:
    """An SL/TP price from a bot report; cTrader has no level as null, older bots send 0."""
    return _positive_number(payload, key, bot_id)


@router.post("/portfolio/report")
async def report_position(request: dict):
    """
    Report position changes from cBot.
    Expected format: {"bot_id": "...", "action": "open|close", "symbol": "...", ...}
    """
    try:
        bot_id = sanitize_bot_id(request.get("bot_id", "default"))
        action = request.get("action")
        symbol = request.get("symbol")

        # The cBot has always sent this; it now narrows the close / partial-close updates
        # to one position instead of every open row for the (bot_id, symbol) pair.
        raw_ctrader_id = request.get("ctrader_id") or request.get("position_id") or request.get("pos_id") or request.get("id")
        try:
            ctrader_id = int(raw_ctrader_id) if raw_ctrader_id not in (None, "") else None
        except (TypeError, ValueError):
            _unreadable(bot_id, "ctrader_id", raw_ctrader_id)
            ctrader_id = None
        
        account_number = str(request.get("account_number", "0"))
        registry = get_account_registry()
        account_type = request.get("account_type")
        if not account_type:
            account_type = registry.get_account_type(account_number) or "demo"
        account_type = str(account_type)
        account_label = request.get("account_label")
        account_balance = float(request.get("account_balance", 0) or 0)
        account_equity = float(request.get("account_equity", 0) or 0)
        
        account_id = registry.upsert_from_bot(
            account_number=account_number,
            account_type=account_type,
            label=account_label,
            balance=account_balance,
            equity=account_equity
        )
        
        if action == "open":
            side = request.get("side")
            volume = request.get("volume", 0.01)
            entry_price = request.get("entry_price")
            sl_pips = request.get("sl_pips")
            tp_pips = request.get("tp_pips")
            
            success = get_portfolio_manager().register_position(
                sl_price=_level_price(request, "sl_price", bot_id),
                tp_price=_level_price(request, "tp_price", bot_id),
                bot_id=bot_id,
                symbol=symbol,
                side=side,
                volume=volume,
                entry_price=entry_price,
                sl_pips=sl_pips,
                tp_pips=tp_pips,
                account_id=account_id,
                ctrader_id=ctrader_id
            )
            
            if success:
                logger.info(f"[PORTFOLIO EVENT] OPEN | {account_id}/{bot_id} | {symbol} {side} {volume} lots @ {entry_price} | SL={sl_pips}p TP={tp_pips}p")
                try:
                    await broadcast_update(account_id=account_id)
                except Exception as e:
                    _broadcast_failed("update", e)
                try:
                    await broadcast_event("TRADE_OPEN", f"OPEN {symbol} {side} {volume}L {bot_id}", bot_id=bot_id, account_id=str(account_id))
                except Exception as e:
                    _broadcast_failed("event", e)
                return {"status": "success", "message": "Position registered"}
            else:
                return {"status": "error", "message": "Failed to register position"}
        
        elif action in ("ping", "sync"):
            logger.info(f"[PORTFOLIO EVENT] SYNC | {account_id}/{bot_id} | Balance: ${account_balance:.2f} | Equity: ${account_equity:.2f}")
            try:
                await broadcast_update(account_id=account_id)
            except Exception as e:
                _broadcast_failed("update", e)
            return {"status": "success", "message": f"Account {account_id} synced", "account_id": account_id}
        
        elif action == "close":
            exit_price = request.get("exit_price")
            pnl = request.get("pnl", 0)
            if not exit_price or exit_price == 0:
                latest = get_portfolio_manager().get_latest_price(symbol)
                if latest:
                    exit_price = latest.get("bid") or latest.get("ask")
            
            # The bots send `reason` (older reports used `close_reason`): free text composed by the
            # bot (cTrader's close reason plus the bot's own exit rule).
            close_reason = (request.get("close_reason") or request.get("reason") or "").strip() or None
            success = get_portfolio_manager().close_position(
                bot_id=bot_id,
                symbol=symbol,
                exit_price=exit_price,
                pnl=pnl,
                account_id=account_id,
                ctrader_id=ctrader_id,
                close_reason=close_reason,
                sl_price=_level_price(request, "sl_price", bot_id),
                tp_price=_level_price(request, "tp_price", bot_id),
                # Lets the server book the position if its open report never arrived.
                side=request.get("side"),
                volume=_positive_number(request, "volume", bot_id),
                entry_price=_positive_number(request, "entry_price", bot_id),
                entry_time=request.get("entry_time"),
                sl_pips=_positive_number(request, "sl_pips", bot_id),
            )
            
            if success:
                try:
                    await broadcast_update(account_id=account_id)
                except Exception as e:
                    _broadcast_failed("update", e)
                logger.info(f"[PORTFOLIO EVENT] CLOSE | {account_id}/{bot_id} | {symbol} | PnL: ${pnl:.2f}")
                try:
                    await broadcast_event("TRADE_CLOSE", f"CLOSE {symbol} {bot_id} PnL: ${pnl:.2f}", bot_id=bot_id, account_id=str(account_id))
                except Exception as e:
                    _broadcast_failed("event", e)
                return {"status": "success", "message": "Position closed"}
            else:
                return {"status": "error", "message": "Failed to close position"}

        log_throttled(logger, logging.WARNING, ("unknown-action", bot_id, str(action)),
                      f"Bot {bot_id} sent an unknown report action: {action!r}; ignored")
        return {"status": "error", "message": f"Unknown action: {action}"}
    
    except Exception as e:
        logger.error(f"Portfolio report error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/portfolio/status")
async def get_portfolio_status(account_id: Optional[str] = None):
    """Get current portfolio status."""
    try:
        status = get_portfolio_manager().get_portfolio_status(account_id=account_id)
        return status
    except Exception as e:
        logger.error(f"Portfolio status error: {e}")
        return {"error": str(e)}

@router.get("/api/dashboard/accounts")
async def api_dashboard_accounts():
    """List all accounts for dashboard selector."""
    try:
        registry = get_account_registry()
        return {"accounts": registry.list_accounts()}
    except Exception as e:
        logger.error(f"Dashboard accounts error: {e}")
        return {"error": str(e)}
