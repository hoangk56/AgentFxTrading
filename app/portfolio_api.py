"""Bot telemetry and portfolio reporting routes: /api/tick, /api/cbot_event, /portfolio/*, account list, cross-locks.

Split out of app/server.py (which includes this router right after /trade, keeping the route order, and
re-exports every name here). The portfolio manager is read through app.portfolio.get_portfolio_manager()
at call time (one shared place: app.portfolio.portfolio_manager), so a test replaces it there.
"""
import logging
import time
from typing import Optional

from fastapi import APIRouter

from app.accounts import get_account_registry
from app.bot_controls import sanitize_bot_id
from app.cbot_watchdog import record_bot_tick
from app.dashboard import broadcast_event, broadcast_tick, broadcast_update, tick_levels
from app.portfolio import get_portfolio_manager
from app.trade_gates import _TMS_CROSS_LOCK_REGISTRY

logger = logging.getLogger("AgentFxTrading")

router = APIRouter()


@router.post("/api/tick")
@router.post("/api/telemetry_tick")
async def handle_telemetry_tick(request: dict):
    """
    Direct tick telemetry endpoint from cBots (TMS or Judas Sweep).
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
        try:
            pnl = float(request["pnl"]) if request.get("pnl") is not None else None
            pips = float(request["pips"]) if request.get("pips") is not None else None
        except (TypeError, ValueError):
            pnl = pips = None
        # FlowRsiBot posts a `positions` list instead of flat fields; its first entry is the
        # position the dashboard row shows (one per bot).
        levels = tick_levels(request)
        positions = request.get("positions")
        if pnl is None and isinstance(positions, list) and positions and isinstance(positions[0], dict):
            first = positions[0]
            try:
                pnl = float(first["net_profit"]) if first.get("net_profit") is not None else None
                pips = float(first["pips"]) if first.get("pips") is not None else None
            except (TypeError, ValueError):
                pnl = pips = None
            levels = tick_levels(first)
        if pnl is not None:
            get_portfolio_manager().update_position_metrics(bot_id, pnl, pips or 0.0, account_id=account_id,
                                                            levels=levels)

        try:
            await broadcast_tick(symbol=symbol, bid=bid, ask=ask, account_id=account_id,
                                 bot_id=bot_id, pnl=pnl, pips=pips, levels=levels)
        except Exception:
            pass
            
        return {"status": "ok", "account_id": account_id}
    except Exception as e:
        logger.error(f"Telemetry tick error: {e}")
        return {"status": "error", "message": str(e)}
@router.post("/api/cbot_event")
async def handle_cbot_event(request: dict):
    """
    Direct event telemetry endpoint from cBots (guardrail blocks, custom warnings, execution failures).
    """
    try:
        bot_id = sanitize_bot_id(request.get("bot_id", "default"))
        event_type = request.get("event_type", "GUARDRAIL")
        message = request.get("message", "")
        account_number = str(request.get("account_number", "0"))
        logger.info(f"[CBOT EVENT] {account_number}/{bot_id} | Type: {event_type} | Message: {message}")
        try:
            await broadcast_event(event_type=event_type, message=message, bot_id=bot_id, account_id=account_number)
        except Exception:
            pass
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error handling cbot event: {e}")
        return {"status": "error", "message": str(e)}


def _positive_number(value) -> Optional[float]:
    """A price, size or distance from a bot report; None when missing, invalid or not positive."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _level_price(value) -> Optional[float]:
    """An SL/TP price from a bot report; cTrader has no level as null, older bots send 0."""
    return _positive_number(value)


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
                sl_price=_level_price(request.get("sl_price")),
                tp_price=_level_price(request.get("tp_price")),
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
                except Exception:
                    pass
                try:
                    await broadcast_event("TRADE_OPEN", f"OPEN {symbol} {side} {volume}L {bot_id}", bot_id=bot_id, account_id=str(account_id))
                except Exception:
                    pass
                return {"status": "success", "message": "Position registered"}
            else:
                return {"status": "error", "message": "Failed to register position"}
        
        elif action in ("ping", "sync"):
            logger.info(f"[PORTFOLIO EVENT] SYNC | {account_id}/{bot_id} | Balance: ${account_balance:.2f} | Equity: ${account_equity:.2f}")
            try:
                await broadcast_update(account_id=account_id)
            except Exception:
                pass
            return {"status": "success", "message": f"Account {account_id} synced", "account_id": account_id}
        
        elif action == "partial_close":
            # cTrader's Positions.Closed does not fire on a partial close, so the bot
            # reports it explicitly: bank the realised P&L on the still-open row and
            # shrink its volume to what is actually left running.
            remaining_volume = float(request.get("remaining_volume", 0) or 0)
            realized_pnl = float(request.get("realized_pnl", 0) or 0)
            closed_volume = float(request.get("closed_volume", 0) or 0)

            success = get_portfolio_manager().record_partial_close(
                bot_id=bot_id,
                symbol=symbol,
                remaining_volume=remaining_volume,
                realized_pnl=realized_pnl,
                account_id=account_id,
                ctrader_id=ctrader_id
            )

            if success:
                logger.info(
                    f"[PORTFOLIO EVENT] PARTIAL CLOSE | {account_id}/{bot_id} | {symbol} | "
                    f"closed {closed_volume} lots for ${realized_pnl:.2f} | {remaining_volume} lots remaining"
                )
                try:
                    await broadcast_update(account_id=account_id)
                except Exception:
                    pass
                try:
                    await broadcast_event(
                        "TRADE_PARTIAL_CLOSE",
                        f"PARTIAL {symbol} {bot_id} {closed_volume}L PnL: ${realized_pnl:.2f}",
                        bot_id=bot_id,
                        account_id=str(account_id),
                    )
                except Exception:
                    pass
                return {"status": "success", "message": "Partial close recorded"}
            else:
                return {"status": "error", "message": "Failed to record partial close"}

        elif action == "close":
            exit_price = request.get("exit_price")
            pnl = request.get("pnl", 0)
            if not exit_price or exit_price == 0:
                latest = get_portfolio_manager().get_latest_price(symbol)
                if latest:
                    exit_price = latest.get("bid") or latest.get("ask")
            
            # FlowRsiBot sends `reason`; the other bots send `close_reason`. Both are free text
            # composed by the bot (cTrader's close reason plus the bot's own exit rule).
            close_reason = (request.get("close_reason") or request.get("reason") or "").strip() or None
            success = get_portfolio_manager().close_position(
                bot_id=bot_id,
                symbol=symbol,
                exit_price=exit_price,
                pnl=pnl,
                account_id=account_id,
                ctrader_id=ctrader_id,
                close_reason=close_reason,
                sl_price=_level_price(request.get("sl_price")),
                tp_price=_level_price(request.get("tp_price")),
                # Lets the server book the position if its open report never arrived.
                side=request.get("side"),
                volume=_positive_number(request.get("volume")),
                entry_price=_positive_number(request.get("entry_price")),
                entry_time=request.get("entry_time"),
                sl_pips=_positive_number(request.get("sl_pips")),
            )
            
            if success:
                try:
                    await broadcast_update(account_id=account_id)
                except Exception:
                    pass
                logger.info(f"[PORTFOLIO EVENT] CLOSE | {account_id}/{bot_id} | {symbol} | PnL: ${pnl:.2f}")
                try:
                    await broadcast_event("TRADE_CLOSE", f"CLOSE {symbol} {bot_id} PnL: ${pnl:.2f}", bot_id=bot_id, account_id=str(account_id))
                except Exception:
                    pass
                return {"status": "success", "message": "Position closed"}
            else:
                return {"status": "error", "message": "Failed to close position"}
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    except Exception as e:
        logger.error(f"Portfolio report error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/portfolio/open-positions")
async def get_open_positions(bot_id: str, account_number: str = "0"):
    """
    Open positions with the stop distance recorded at entry.

    A restarting cBot uses this to rebuild its in-RAM initial-SL map: without it, a
    position already moved to break-even looks like it was opened with a ~0.5 pip
    stop, and every R-based decision (trailing trigger, partial close) runs on a
    fabricated R.
    """
    try:
        registry = get_account_registry()
        account_type = registry.get_account_type(str(account_number)) or "demo"
        account_id = registry.resolve_account_id(str(account_number), account_type)
        if not account_id:
            return {"status": "success", "positions": []}
        rows = get_portfolio_manager().get_open_positions(
            bot_id=sanitize_bot_id(bot_id), account_id=account_id
        )
        return {"status": "success", "positions": rows}
    except Exception as e:
        logger.error(f"Open positions lookup error: {e}")
        return {"status": "error", "message": str(e), "positions": []}


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

@router.get("/api/tms/cross-locks")
async def api_tms_cross_locks():
    """Return live TMS cross-lock directional bias cache across all symbols."""
    return {
        "status": "ok",
        "cross_locks": _TMS_CROSS_LOCK_REGISTRY,
        "timestamp": time.time(),
    }
