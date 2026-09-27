import os
import sys
from pathlib import Path
import uvicorn
import json
import logging
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env
load_dotenv(PROJECT_ROOT / ".env", override=True)

import datetime
import asyncio
import logging.handlers
import threading
import time
from typing import Optional, List, Dict, Any, Union, Tuple

# The log format, the GMT+7 formatter, the daily file handler and the uvicorn access-log filter live
# in app/logging_setup.py. Logging is still configured here, at import time, before the app modules load.
from app.logging_setup import (_LOG_FORMAT, GMT7Formatter, DailyDateFileHandler, is_running_under_test,
                               setup_agent_logging, SkipCommandPollAccessLog)

setup_agent_logging(logging.INFO)
logger = logging.getLogger("AgentFxTrading")


logging.getLogger("uvicorn.access").addFilter(SkipCommandPollAccessLog())
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Optional, List

from app.bot_controls import sanitize_bot_id  # shared with the dashboard's bot-facing routes
from app.llm_client import create_llm_client, JSONResponseParser, describe_llm_error, _clean_env_float, _clean_env_int, _clean_env_bool
from app.portfolio import init_portfolio, get_portfolio_manager, is_us_index
from app.dashboard import router as dashboard_router, broadcast_update, broadcast_tick, broadcast_event, broadcast_decision, record_ai_decision, manager as ws_manager, WebSocketLogHandler, tick_levels
from app.accounts import init_account_registry, get_account_registry
from app.cbot_watchdog import record_bot_snapshot, record_bot_tick

# The /trade models, gates and prompts and the bot-reporting routes live in their own modules
# (app/trade_models.py, app/trade_gates.py, app/trade_prompts.py, app/portfolio_api.py). Every name
# stays importable from app.server. The singletons and TRADE_LLM_* settings below stay here: /trade
# reads them from this module's globals, which is where tests patch them.
from app.trade_models import (BarData, TmsSignals, MarketRegimeInfo, OrbData, PositionInfo, SessionInfo,
                              StrategyData, SwingStructure, TimeframeContext, MultiTimeframeData,
                              ActivePosition, HistoricalTrade, MarketSnapshot, AgentDecision)
from app.trade_gates import (_TMS_CROSS_LOCK_REGISTRY, MACRO_LOCK_MAX_AGE_BARS, _SUB_HOUR_TIMEFRAME_SECONDS,
                             _cross_lock_bar_bucket, update_tms_cross_lock, get_tms_cross_lock,
                             detect_swing_market_structure, is_judas_sweep_bot, is_flow_rsi_bot,
                             _resolve_account, JUDAS_ADJUST_MIN_TP_PROGRESS, validate_judas_adjust_decision,
                             TMS_CLOSE_MIN_ADVERSE_SL_RATIO, TMS_CLOSE_MIN_PROFIT_SL_RATIO,
                             validate_tms_close_decision, evaluate_judas_sweep_gate,
                             CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT, CHOPPY_OVERRIDE_MAX_OR_FLIPS,
                             CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR, BREAKOUT_DISTANCE_LIMITS,
                             MODEL1_ENTRY_WINDOW_BARS, MAX_BARS_SINCE_BREAKOUT_MODEL2,
                             resolve_breakout_limits, breakout_distance_prompt, check_us_index_conflict,
                             evaluate_cycle_gate, generate_fallback_decision)
from app.trade_prompts import (_pip_size_for_symbol, format_price, build_system_prompt,
                               build_judas_sweep_system_prompt, build_judas_sweep_user_prompt,
                               build_user_prompt)
from app.portfolio_api import (router as portfolio_router, handle_telemetry_tick, handle_cbot_event,
                               _positive_number, _level_price, report_position, get_open_positions,
                               get_portfolio_status, api_dashboard_accounts, api_tms_cross_locks)


# Attach WebSocket live log handler to root logger
_ws_handler = WebSocketLogHandler(ws_manager)
_ws_handler.setFormatter(GMT7Formatter(_LOG_FORMAT, datefmt="%H:%M:%S"))
_ws_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(_ws_handler)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        loop = asyncio.get_running_loop()
        ws_manager.set_event_loop(loop)
    except Exception as e:
        logger.warning(f"Failed to set event loop for ws_manager: {e}")

    # Start cBot Watchdog service for automatic relogin and crash recovery
    from app.cbot_watchdog import cbot_watchdog
    watchdog_task = asyncio.create_task(cbot_watchdog.run_loop())

    # Backtest worker. Never under pytest: it removes every container labelled agentfx.backtest whose
    # job is not running in *its* DB, and a test run points at a throwaway SQLite file.
    from app.backtest_worker import backtest_worker
    backtest_task = None
    if not is_running_under_test():
        backtest_task = asyncio.create_task(backtest_worker.run_loop())

    yield

    # Shutdown watchdog cleanly
    cbot_watchdog.stop()
    watchdog_task.cancel()
    try:
        await watchdog_task
    except asyncio.CancelledError:
        pass
    if backtest_task:
        backtest_worker.stop()
        backtest_task.cancel()
        try:
            await backtest_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="TMS+ORB Agent Server", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")

# Mount dashboard router
app.include_router(dashboard_router)
from app.backtest_api import router as backtest_router
app.include_router(backtest_router)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = PROJECT_ROOT / "static" / "favicon.png"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return ""
# Initialize Account Registry
account_registry = init_account_registry()
account_registry.seed_from_env()

# Initialize Portfolio Manager. Code reads it through get_portfolio_manager() at call time, so
# app.portfolio.portfolio_manager is the one place to replace it; this name is kept for importers.
portfolio_manager = init_portfolio()
# Create LLM client based on LLM_PROVIDER env variable
# Supports: "qwen", "openai", "anthropic", "deepseek", "openai_compatible"
llm_client = create_llm_client()

# /trade answers a cBot that is waiting on the other end of an HTTP call (FlowRsiBot gives
# up after 60 s), so the client-wide LLM_TIMEOUT x LLM_MAX_RETRIES budget (90 s x 4 tries)
# is far too long here: the bot would time out before the safety fallback ever reached it.
# Each attempt gets its own timeout, and a hard deadline caps retries plus backoff.
TRADE_LLM_TIMEOUT = _clean_env_float("LLM_TRADE_TIMEOUT", 40.0)
TRADE_LLM_MAX_RETRIES = _clean_env_int("LLM_TRADE_MAX_RETRIES", 1)
TRADE_LLM_DEADLINE = _clean_env_float("LLM_TRADE_DEADLINE", 55.0)
# qwen3.7-flash thinks by default: 1,250-3,200 hidden reasoning tokens per /trade call, 18-39 s
# instead of 2-3 s, and the Judas prompt ran past the deadline. The answer is a small JSON verdict.
TRADE_LLM_ENABLE_THINKING = _clean_env_bool("LLM_TRADE_ENABLE_THINKING", False)


@app.post("/trade", response_model=AgentDecision)
async def trade_decision(snapshot: MarketSnapshot):
    account_id = _resolve_account(snapshot)
    is_flowrsi = is_flow_rsi_bot(snapshot)
    is_judas = False if is_flowrsi else is_judas_sweep_bot(snapshot)
    # Heartbeat for the watchdog's stale-bar-feed check: it compares this against the
    # bot's own session window to catch a cBot that is up but no longer processing bars.
    record_bot_snapshot(f"{account_id}/{snapshot.bot_id}")
    
    pos_data = None
    if snapshot.position:
        pos_data = {
            "side": snapshot.position.resolved_side,
            "entry_price": snapshot.position.entry_price,
            "unrealized_pnl": snapshot.position.resolved_pnl,
            "unrealized_pnl_pips": snapshot.position.resolved_pnl_pips,
            "mfe_pips": snapshot.position.mfe_pips,
            "giveback_pips": snapshot.position.giveback_pips,
            "sl_price": snapshot.position.sl or snapshot.position.sl_price,
            "tp_price": snapshot.position.tp or snapshot.position.tp_price,
        }
    get_portfolio_manager().update_market_price(snapshot.symbol, snapshot.bid, snapshot.ask, bot_id=snapshot.bot_id, position_data=pos_data, account_id=account_id)
    # Only a cross-lock is shared: an EMA bias standing in for a stale lock is not one.
    if (snapshot.tms and snapshot.tms.bias and snapshot.tms.bias.upper() in ("BULLISH", "BEARISH")
            and (snapshot.tms.bias_source or "").lower() != "ema"):
        update_tms_cross_lock(
            snapshot.symbol, snapshot.tms.bias.upper(), snapshot.tms.bars_since_cross,
            source=f"{snapshot.bot_id} (Macro TMS)", timeframe=snapshot.tms_timeframe,
        )

    if is_flowrsi:
        pos_str = f"{snapshot.position.resolved_side} pnl=${snapshot.position.resolved_pnl:.2f}" if snapshot.position else "FLAT"
        rsi_cross = snapshot.rsi_cross_signal or "None"
        fvg_str = f"FVG={snapshot.fvg_type}" if snapshot.in_fvg_zone else "FVG=None"
        zone_str = "Discount" if snapshot.is_discount else ("Premium" if snapshot.is_premium else "Eq")
        cand_str = snapshot.candidate_action or "NONE"
        tms_bias, tms_age, tms_src = get_tms_cross_lock(snapshot)

        logger.info(
            f"[SNAPSHOT FLOW_RSI] {account_id}/{snapshot.bot_id} | {snapshot.symbol} {snapshot.timeframe} | "
            f"Bid={snapshot.bid:g} Ask={snapshot.ask:g} | RSI_Cross={rsi_cross} (F={snapshot.fast_rsi} S={snapshot.slow_rsi}) | "
            f"{fvg_str} | Zone={zone_str} | Candidate={cand_str} | Pos={pos_str} | TMS_Lock={tms_bias} (age={tms_age}, src={tms_src})"
        )

        # Gate Check 1: If no entry candidate and no open position, gate as HOLD without calling LLM
        if cand_str == "NONE" and not snapshot.position:
            logger.info(
                f"[FLOW_RSI GATE] {account_id}/{snapshot.bot_id} -> GATED: HOLD | "
                f"Reason: No active Nested RSI setup (Fast={snapshot.fast_rsi}, Slow={snapshot.slow_rsi}, Signal={rsi_cross})"
            )
            return AgentDecision(action="HOLD", confidence=85.0, reason=f"No active setup (RSI={rsi_cross}, FVG={snapshot.fvg_type})")

        # Gate Check 2: TMS Cross-Lock Directional Bias Gatekeeper
        if not snapshot.position:
            if cand_str == "BUY" and tms_bias == "BEARISH":
                gate_reason = (
                    f"Blocked by TMS Cross-Lock Gatekeeper: Macro TMS is LOCKED BEARISH "
                    f"(age={tms_age} bars, source={tms_src}). Counter-trend BUY entry strictly prohibited."
                )
                logger.warning(f"[FLOW_RSI TMS GATE] {account_id}/{snapshot.bot_id} -> GATED: HOLD | {gate_reason}")
                return AgentDecision(
                    action="HOLD",
                    confidence=85.0,
                    reason=gate_reason,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe,
                    request_id=snapshot.request_id,
                )
            if cand_str == "SELL" and tms_bias == "BULLISH":
                gate_reason = (
                    f"Blocked by TMS Cross-Lock Gatekeeper: Macro TMS is LOCKED BULLISH "
                    f"(age={tms_age} bars, source={tms_src}). Counter-trend SELL entry strictly prohibited."
                )
                logger.warning(f"[FLOW_RSI TMS GATE] {account_id}/{snapshot.bot_id} -> GATED: HOLD | {gate_reason}")
                return AgentDecision(
                    action="HOLD",
                    confidence=85.0,
                    reason=gate_reason,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe,
                    request_id=snapshot.request_id,
                )

        # Build specialized FlowRSI system & user prompt
        system_prompt = (
            "You are an elite Quantitative FX Co-Pilot specializing in Nested RSI momentum and SMC market structure.\n"
            "Analyze the real-time market snapshot and output strictly valid JSON format with keys:\n"
            '{"action": "BUY"|"SELL"|"HOLD"|"ADJUST"|"CLOSE_ALL", "volume_lots": 0.0, "sl_pips": 0.0, "tp_pips": 0.0, '
            '"new_sl_price": null, "new_tp_price": null, "confidence": 0-100, "reason": "concise rationale"}\n'
            "Rule: Volume is 100% managed by cBot risk engine; keep volume_lots=0.0.\n"
            "Rule: ENTRY STOPS AND TARGETS ARE THE ENGINE'S, NOT YOURS. For BUY/SELL return "
            "sl_pips=0, tp_pips=0, new_sl_price=null, new_tp_price=null — the cBot's ATR/structural "
            "engine sizes them (it is the 'Proposed Technical Setup' shown below, given as context "
            "for your confidence, not as a number to restate or improve). Anything you return on a "
            "BUY/SELL is discarded. Your job there is DIRECTION and TIMING only.\n"
            "Rule: On ADJUST you DO own the stop, but express it as new_sl_price / new_tp_price in "
            "absolute price. Never as pips: your pip scale is not the broker's.\n"
            "=== POSITION MANAGEMENT DISCIPLINE ===\n"
            "1. GIVE POSITIONS BREATHING ROOM (HOLD): Allow open positions breathing room for normal pullbacks and market noise. "
            "Do NOT panic-close or micro-manage positions that are flat, slightly underwater (e.g. within normal spread/minor pullback), or in early development.\n"
            "2. CUT LOSS EARLY (CLOSE_ALL): Only execute CLOSE_ALL when an open position suffers MEANINGFUL adverse movement "
            "(loss >= 0.5R or >= 10 pips FX / >= 100 pips Gold) AND clear market structure decisively breaks against it "
            "(e.g. sustained opposing RSI crossover with structural swing breakdown). Never exit early on minor noise.\n"
            "3. PROTECT PROFITS (ADJUST or CLOSE_ALL): When an open position has captured significant profit (>= 1.0 R:R or >= 15 pips FX / >= 150 pips Gold) "
            "and displays clear momentum exhaustion or structural reversal, lock in gains by adjusting SL or closing. Do not exit prematurely for petty cents.\n"
            "4. NEW ENTRIES: If candidate_action is BUY/SELL, confirm with confidence >= 75% only when Nested RSI cross and SMC zone align."
        )
        # SMC Swing Structure & Multi-timeframe / Indicator context
        flow_sw_str = ""
        if snapshot.multi_timeframe:
            flow_lines = []
            cur_tf = snapshot.multi_timeframe.current_tf
            h1_tf = snapshot.multi_timeframe.h1_tf
            h4_tf = snapshot.multi_timeframe.h4_tf
            for tf_ctx, label in [(cur_tf, f"Current ({cur_tf.timeframe if cur_tf and cur_tf.timeframe else snapshot.timeframe})"), (h1_tf, "Higher TF (H1)"), (h4_tf, "Major TF (H4)")]:
                if tf_ctx:
                    sw_sub = ""
                    if tf_ctx.swing_structure:
                        sw = tf_ctx.swing_structure
                        sw_sub = (
                            f" | Swings: High={format_price(sw.last_swing_high, snapshot.symbol)} ({sw.swing_high_type or 'N/A'}), "
                            f"Low={format_price(sw.last_swing_low, snapshot.symbol)} ({sw.swing_low_type or 'N/A'}), "
                            f"PrevH={format_price(sw.prev_swing_high, snapshot.symbol)}, "
                            f"PrevL={format_price(sw.prev_swing_low, snapshot.symbol)} "
                            f"[Struct: {sw.market_structure or 'SIDEWAYS'}]"
                        )
                    flow_lines.append(f"- {label}: Bias={tf_ctx.trend_bias} | FastMA={format_price(tf_ctx.fast_tema, snapshot.symbol)} | SlowMA={format_price(tf_ctx.slow_tema, snapshot.symbol)} | RSI={tf_ctx.rsi:.1f}{sw_sub}")
            if flow_lines:
                flow_sw_str = "SMC Swing Structure (Multi-Timeframe):\n" + "\n".join(flow_lines) + f"\n- TMS Cross-Lock Macro Bias: {tms_bias} (age={tms_age} bars, source={tms_src})\n"
        else:
            cur_p = snapshot.bid or snapshot.ask
            st_lbl, rec_h, rec_l = detect_swing_market_structure(snapshot.bars, cur_p)
            if (rec_h <= 0 or rec_l <= 0) and snapshot.strategy:
                rec_h = snapshot.strategy.recent_high if rec_h <= 0 else rec_h
                rec_l = snapshot.strategy.recent_low if rec_l <= 0 else rec_l
            flow_sw_str = (
                f"SMC Swing Structure (Current {snapshot.timeframe}):\n"
                f"- Swings: High={format_price(rec_h, snapshot.symbol)} (Resistance/BSL), "
                f"Low={format_price(rec_l, snapshot.symbol)} (Support/SSL) [Struct: {st_lbl}]\n"
                f"- TMS Cross-Lock Macro Bias: {tms_bias} (age={tms_age} bars, source={tms_src})\n"
            )

        atr_info_str = ""
        if snapshot.strategy and snapshot.strategy.atr > 0:
            atr_val = snapshot.strategy.atr
            sym_u = snapshot.symbol.upper()
            if "XAU" in sym_u or "GOLD" in sym_u:
                atr_p = atr_val / 0.01 if atr_val < 100.0 else atr_val
            elif any(k in sym_u for k in ["US30", "USTEC", "DE40", "UK100", "BTC", "ETH"]):
                atr_p = atr_val
            elif "JPY" in sym_u:
                atr_p = atr_val / 0.01 if atr_val < 5.0 else atr_val
            else:
                atr_p = atr_val / 0.0001 if atr_val < 1.0 else atr_val
            atr_info_str = f" | ATR (14): {atr_p:.1f} pips ({format_price(atr_val, snapshot.symbol)} price move)"

        user_prompt = (
            f"Symbol: {snapshot.symbol} ({snapshot.timeframe})\n"
            f"Current Bid={snapshot.bid:g}, Ask={snapshot.ask:g}, Spread={snapshot.spread_pips or 0:.1f}p{atr_info_str}\n"
            f"{flow_sw_str}"
            f"Nested RSI: Fast={snapshot.fast_rsi}, Slow={snapshot.slow_rsi}, Signal={snapshot.rsi_cross_signal}\n"
            f"SMC: Zone={zone_str}, InFVG={snapshot.in_fvg_zone} ({snapshot.fvg_type}), LiquiditySwept={snapshot.liquidity_swept} ({snapshot.swept_liquidity_type})\n"
            f"Proposed Technical Setup: Candidate={cand_str}, SL={snapshot.technical_sl_price}, TP={snapshot.technical_tp_price}, RR={snapshot.technical_risk_reward}\n"
            f"Open Position Status: {pos_str}\n"
            f"Carefully evaluate Open Position Status: Give trades breathing room; protect gains if >=1.0R; cut loss only on decisive structural breakdown; else HOLD or confirm entry."
        )
    elif is_judas:
        strat = snapshot.strategy
        asian_str = f"Asian=[{strat.asian_low:g}...{strat.asian_high:g}] ({strat.asian_range_pips:.0f}p)" if strat else "Asian=N/A"
        kz_str = strat.killzone_session if strat else "N/A"
        bias_str = f"{strat.bias_direction} ({strat.traditional_signal})" if strat else "N/A"
        pos_str = f"{snapshot.position.resolved_side} pnl=${snapshot.position.resolved_pnl:.2f}" if snapshot.position else "FLAT"
        # The cBot's Judas Structural Guard state, so a blocked-looking BUY is explainable
        # from the server log alone instead of requiring the container logs.
        locked = []
        if strat and strat.asian_low_broken:
            locked.append("Low->BUY_LOCKED")
        if strat and strat.asian_high_broken:
            locked.append("High->SELL_LOCKED")
        lock_str = ",".join(locked) if locked else "none"
        pip_str = f"{strat.pip_size:g}" if strat and strat.pip_size > 0 else "n/a"

        logger.info(
            f"[SNAPSHOT SMC] {account_id}/{snapshot.bot_id} | {snapshot.symbol} {snapshot.timeframe} | "
            f"Bid={snapshot.bid:g} Ask={snapshot.ask:g} | {asian_str} | Locked={lock_str} | PipSize={pip_str} | "
            f"KZ={kz_str} | Gate={bias_str} | Pos={pos_str}"
        )

        # SMC Judas Sweep Gate Evaluation
        gated_decision = evaluate_judas_sweep_gate(snapshot, account_id=account_id)
        if gated_decision is not None:
            logger.info(f"[JUDAS GATE] {account_id}/{snapshot.bot_id} -> GATED: {gated_decision.action} | Reason: {gated_decision.reason}")
            return gated_decision

        system_prompt = build_judas_sweep_system_prompt(snapshot)
        user_prompt = build_judas_sweep_user_prompt(snapshot)
    else:
        # TMS + ORB Strategy Flow
        regime_str = snapshot.market.regime if snapshot.market else "N/A"
        er_str = f"{snapshot.market.er_session:.2f}" if snapshot.market and snapshot.market.er_session is not None else "N/A"
        pos_str = f"{snapshot.position.resolved_side} pnl={snapshot.position.unrealized_pnl_pips:.1f}p" if snapshot.position else "FLAT"
        sess_str = f"{snapshot.session.phase} ({snapshot.session.minutes_to_end}m)" if snapshot.session else "N/A"
        
        ha_str = "N/A"
        tdi_str = "N/A"
        stoch_str = "N/A"
        if snapshot.bars and len(snapshot.bars) > 0:
            b = snapshot.bars[0]
            if b.ha_color is not None:
                ha_icon = "🟢" if str(b.ha_color).lower() == "green" else "🔴" if str(b.ha_color).lower() == "red" else str(b.ha_color)
                ha_str = f"HA={ha_icon}"
            if b.tdi_green is not None and b.tdi_red is not None:
                tdi_str = f"TDI_G={b.tdi_green:.2f} TDI_R={b.tdi_red:.2f}"
            if b.stoch_k is not None and b.stoch_d is not None:
                stoch_str = f"Stoch=%K={b.stoch_k:.1f} %D={b.stoch_d:.1f}"
        
        or_str = "OR=N/A"
        if snapshot.orb:
            or_str = f"OR=[{snapshot.orb.or_low:g}...{snapshot.orb.or_high:g}]"

        logger.info(
            f"[SNAPSHOT TMS] {account_id}/{snapshot.bot_id} | {snapshot.symbol} {snapshot.timeframe} | "
            f"Bid={snapshot.bid:g} | {or_str} | {ha_str} {tdi_str} {stoch_str} | "
            f"TMS={snapshot.tms.bias if snapshot.tms else 'N/A'} (age={snapshot.tms.bars_since_cross if snapshot.tms else 0}) | "
            f"Regime={regime_str} (ER={er_str}) | Pos={pos_str} | Session={sess_str}"
        )

        gated_decision = evaluate_cycle_gate(snapshot, account_id=account_id)
        if gated_decision is not None:
            logger.info(f"[CYCLE GATE] {account_id}/{snapshot.bot_id} -> GATED: {gated_decision.action} | Reason: {gated_decision.reason}")
            return gated_decision

        system_prompt = build_system_prompt(snapshot)
        user_prompt = build_user_prompt(snapshot)

    # Check portfolio risk before allowing new trades
    has_open = snapshot.position is not None or (snapshot.active_positions is not None and len(snapshot.active_positions) > 0)
    # Check News Blackout Shield (e.g. Red news or EIA Crude Oil inventories) before opening new positions
    if not has_open:
        try:
            from app.news_service import is_news_blackout_active
            is_bo, bo_title, bo_mins = await is_news_blackout_active(snapshot.symbol, pause_before_mins=30, pause_after_mins=30)
            if is_bo:
                logger.info(f"[{account_id}/{snapshot.bot_id}] News Blackout Shield active: {bo_title} ({bo_mins}m remaining). Gated HOLD.")
                return AgentDecision(
                    action="HOLD",
                    volume_lots=0.01,
                    sl_pips=0,
                    tp_pips=0,
                    reason=f"News Blackout Shield active: {bo_title} ({bo_mins}m remaining)",
                    request_id=snapshot.request_id,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe
                )
        except Exception as ex_news:
            logger.warning(f"[{account_id}/{snapshot.bot_id}] Error checking news blackout shield: {ex_news}")

    if not has_open:
        # Only FlowRSI states its direction up front; elsewhere the LLM picks it. Guessing
        # "BUY" refused aligned US-index SELLs here, so an unknown side skips the alignment
        # check and the Risk Guard below applies it to the final decision.
        pre_side = snapshot.candidate_action if is_flowrsi and snapshot.candidate_action in ("BUY", "SELL") else None
        can_trade, reason = get_portfolio_manager().check_risk(
            symbol=snapshot.symbol,
            side=pre_side,
            volume=0.01,
            account_balance=snapshot.account_balance,
            account_id=account_id,
            used_margin=snapshot.account_margin,
            bot_id=snapshot.bot_id,
        )
        
        if not can_trade:
            logger.warning(f"[{account_id}/{snapshot.bot_id}] Portfolio risk check failed: {reason}")
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0,
                tp_pips=0,
                reason=f"Portfolio constraint: {reason}",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {"temperature": 0.1, "timeout": TRADE_LLM_TIMEOUT, "max_retries": TRADE_LLM_MAX_RETRIES,
                  **llm_client.thinking_options(TRADE_LLM_ENABLE_THINKING)}
        if hasattr(llm_client, 'client') and hasattr(llm_client.client, 'chat'):
            kwargs["response_format"] = {"type": "json_object"}
        
        try:
            result_str = await asyncio.wait_for(llm_client.chat(messages, **kwargs), timeout=TRADE_LLM_DEADLINE)
        except asyncio.TimeoutError:
            raise TimeoutError(f"no LLM answer within the {TRADE_LLM_DEADLINE:.0f}s /trade deadline") from None
        decision_dict = JSONResponseParser.parse(result_str)
        
        # Inject metadata if not in response
        if "request_id" not in decision_dict or not decision_dict["request_id"]:
            decision_dict["request_id"] = snapshot.request_id
        if "bot_id" not in decision_dict or not decision_dict["bot_id"]:
            decision_dict["bot_id"] = snapshot.bot_id
        if "symbol" not in decision_dict or not decision_dict["symbol"]:
            decision_dict["symbol"] = snapshot.symbol
        if "timeframe" not in decision_dict or not decision_dict["timeframe"]:
            decision_dict["timeframe"] = snapshot.timeframe
        if "confidence" not in decision_dict:
            decision_dict["confidence"] = 80.0
        if is_flowrsi:
            action_val = str(decision_dict.get("action", "HOLD")).upper()
            pip_size = (
                snapshot.pip_size if snapshot.pip_size > 0
                else _pip_size_for_symbol((snapshot.symbol or "").upper())
            )

            if action_val in ("BUY", "SELL"):
                # Safety Guard: Ensure LLM did not propose a counter-trend trade against TMS Cross-Lock
                tms_bias, tms_age, tms_src = get_tms_cross_lock(snapshot)
                if action_val == "BUY" and tms_bias == "BEARISH":
                    logger.warning(
                        f"[{account_id}/{snapshot.bot_id}] [FLOW_RSI TMS GUARD] Model BUY overridden -> HOLD: "
                        f"TMS is locked BEARISH (age={tms_age}, source={tms_src})."
                    )
                    decision_dict["action"] = "HOLD"
                    decision_dict["reason"] = f"Overridden by TMS Cross-Lock Guard: TMS is LOCKED BEARISH ({tms_src}, age={tms_age} bars)."
                    action_val = "HOLD"
                elif action_val == "SELL" and tms_bias == "BULLISH":
                    logger.warning(
                        f"[{account_id}/{snapshot.bot_id}] [FLOW_RSI TMS GUARD] Model SELL overridden -> HOLD: "
                        f"TMS is locked BULLISH (age={tms_age}, source={tms_src})."
                    )
                    decision_dict["action"] = "HOLD"
                    decision_dict["reason"] = f"Overridden by TMS Cross-Lock Guard: TMS is LOCKED BULLISH ({tms_src}, age={tms_age} bars)."
                    action_val = "HOLD"

                # "LLM proposes, Code disposes": on an entry the ATR/structural engine owns
                # the stop and the target. FlowRsiBot prefers decision.new_sl_price over its
                # own fallbackSL, so leaving the model's levels in place hands it the whole
                # risk leg -- and it prices them on its own pip scale (ETHUSD 295.4p against
                # the 2891.3p actually placed, BTCUSD 731.02p against 76042.4p). Clear them
                # and the bot falls back to the technicalSL/technicalTP it computed.
                proposed = [decision_dict.get(k) for k in ("sl_pips", "tp_pips", "new_sl_price", "new_tp_price")]
                if any(proposed):
                    logger.info(
                        f"[{account_id}/{snapshot.bot_id}] [FLOW_RSI SL/TP AUTHORITY] Discarded model levels "
                        f"(sl={proposed[0]} tp={proposed[1]} sl_price={proposed[2]} tp_price={proposed[3]}); "
                        f"engine stop {snapshot.technical_sl_price} / target {snapshot.technical_tp_price} stands."
                    )
                decision_dict["sl_pips"] = 0.0
                decision_dict["tp_pips"] = 0.0
                decision_dict["new_sl_price"] = 0.0
                decision_dict["new_tp_price"] = 0.0

            elif action_val == "ADJUST":
                # Managing an open position is the model's call, but only against a price.
                # A bare sl_pips carries no scale: FlowRsiBot multiplies it by Symbol.PipSize,
                # which would turn BTCUSD's 731.02 into a $7.31 stop. Re-derive the pips from
                # the price the model gave, measured where the bot measures them (a long is
                # closed at the bid, a short at the ask), and refuse an adjustment with no price.
                try:
                    new_sl = float(decision_dict.get("new_sl_price") or 0.0)
                    new_tp = float(decision_dict.get("new_tp_price") or 0.0)
                except (TypeError, ValueError):
                    new_sl = new_tp = 0.0
                pos_side = snapshot.position.resolved_side if snapshot.position else "BUY"
                exit_ref = snapshot.bid if pos_side == "BUY" else snapshot.ask

                decision_dict["sl_pips"] = round(abs(new_sl - exit_ref) / pip_size, 1) if new_sl > 0 else 0.0
                decision_dict["tp_pips"] = round(abs(new_tp - exit_ref) / pip_size, 1) if new_tp > 0 else 0.0

                if new_sl <= 0 and new_tp <= 0:
                    logger.warning(
                        f"[{account_id}/{snapshot.bot_id}] [FLOW_RSI ADJUST GUARD] ADJUST -> HOLD: no "
                        f"new_sl_price/new_tp_price to anchor the move; bare pips carry no reliable scale."
                    )
                    decision_dict["action"] = "HOLD"
                    decision_dict["reason"] = (
                        f"[ADJUST Guard] No target price supplied. {decision_dict.get('reason', '')}"
                    )
        if is_judas:
            action_val = str(decision_dict.get("action", "HOLD")).upper()
            sym_up = (snapshot.symbol or "").upper()
            pip_size = (
                snapshot.strategy.pip_size
                if snapshot.strategy and snapshot.strategy.pip_size > 0
                else _pip_size_for_symbol(sym_up)
            )
            entry_ref = snapshot.ask if action_val == "BUY" else snapshot.bid

            # Structural Guard mirror: never forward an entry against a boundary the cBot's
            # Judas Structural Guard already locked (decisive M15 close beyond it). Without
            # this the server logs a confident BUY that the cBot silently discards.
            if snapshot.strategy and action_val in ("BUY", "SELL"):
                locked = (
                    snapshot.strategy.asian_low_broken if action_val == "BUY"
                    else snapshot.strategy.asian_high_broken
                )
                if locked:
                    boundary = "Asian Low" if action_val == "BUY" else "Asian High"
                    logger.warning(
                        f"[{account_id}/{snapshot.bot_id}] [JUDAS STRUCTURAL GUARD] {action_val} blocked -> HOLD: "
                        f"{boundary} already broken by a decisive M15 close this session."
                    )
                    decision_dict["action"] = "HOLD"
                    decision_dict["reason"] = (
                        f"[Structural Guard] {boundary} broken by a decisive M15 close this session. "
                        f"Sweep side locked. {decision_dict.get('reason', '')}"
                    )
                    action_val = "HOLD"

            if action_val in ("BUY", "SELL"):
                try:
                    new_tp = float(decision_dict.get("new_tp_price") or 0.0)
                    new_sl = float(decision_dict.get("new_sl_price") or 0.0)
                    tp_p = float(decision_dict.get("tp_pips") or 0.0)
                    sl_p = float(decision_dict.get("sl_pips") or 0.0)
                    strat = snapshot.strategy

                    # 1. Target TP price fallback to Asian boundary if omitted
                    if new_tp <= 0 and strat:
                        if action_val == "BUY" and strat.asian_high > snapshot.ask:
                            new_tp = strat.asian_high
                            decision_dict["new_tp_price"] = new_tp
                        elif action_val == "SELL" and strat.asian_low > 0 and strat.asian_low < snapshot.bid:
                            new_tp = strat.asian_low
                            decision_dict["new_tp_price"] = new_tp

                    # 2. Harmonize tp_pips with new_tp_price or correct crypto pip scale
                    if new_tp > 0:
                        calc_tp_pips = round(abs(new_tp - entry_ref) / pip_size, 1)
                        if tp_p <= 0 or abs(tp_p - calc_tp_pips) > calc_tp_pips * 0.4:
                            decision_dict["tp_pips"] = calc_tp_pips
                    elif any(c in sym_up for c in ["BTC", "ETH"]) and strat and strat.asian_range_pips > 1000:
                        if 0 < tp_p < 800 and (tp_p * 10) <= strat.asian_range_pips * 1.5:
                            decision_dict["tp_pips"] = tp_p * 10

                    # 3. Harmonize sl_pips with new_sl_price
                    if new_sl > 0:
                        calc_sl_pips = round(abs(entry_ref - new_sl) / pip_size, 1)
                        if sl_p <= 0 or abs(sl_p - calc_sl_pips) > calc_sl_pips * 0.4:
                            decision_dict["sl_pips"] = calc_sl_pips
                except Exception as ex:
                    logger.warning(f"Error harmonizing Judas decision: {ex}")

            # ADJUST Guard: deterministic protection against LLM position-management overreach.
            # Downgrade to HOLD (position untouched) when the proposed SL/TP is geometrically
            # invalid for the open side, or when locking profit before >= 40% progress to TP.
            if action_val == "ADJUST":
                try:
                    adjust_reject_reason = validate_judas_adjust_decision(snapshot, decision_dict)
                except Exception as ex:
                    logger.warning(f"Judas ADJUST validation error: {ex}")
                    adjust_reject_reason = None
                if adjust_reject_reason:
                    pos = snapshot.position
                    underwater = pos and (
                        pos.resolved_pnl < -0.1 or 
                        (pos.entry_price and snapshot.bid and pos.resolved_side == "BUY" and snapshot.bid < pos.entry_price) or
                        (pos.entry_price and snapshot.ask and pos.resolved_side == "SELL" and snapshot.ask > pos.entry_price)
                    )
                    reason_text = str(decision_dict.get("reason", "")).lower()
                    structural_invalidation = any(k in reason_text for k in ["break", "broke", "invalid", "fail", "exit", "close", "reversal", "underwater"])
                    wrong_side_sl = "a stop above the market cannot protect a long" in adjust_reject_reason or "a stop below the market cannot protect a short" in adjust_reject_reason

                    if underwater and wrong_side_sl and structural_invalidation:
                        logger.warning(
                            f"[{account_id}/{snapshot.bot_id}] [JUDAS ADJUST GUARD] LLM attempted impossible SL on underwater position ({adjust_reject_reason}) due to structural breakdown. Converting ADJUST -> CLOSE_ALL to protect capital."
                        )
                        decision_dict["action"] = "CLOSE_ALL"
                        decision_dict["reason"] = (
                            f"[ADJUST Guard -> Emergency Exit] Structural breakdown on underwater position with impossible SL ({adjust_reject_reason}). Converted to CLOSE_ALL. "
                            f"{decision_dict.get('reason', '')}"
                        )
                    else:
                        logger.warning(
                            f"[{account_id}/{snapshot.bot_id}] [JUDAS ADJUST GUARD] ADJUST rejected -> HOLD: "
                            f"{adjust_reject_reason}. Position left untouched."
                        )
                        decision_dict["action"] = "HOLD"
                        decision_dict["reason"] = (
                            f"[ADJUST Guard] {adjust_reject_reason}. Position left untouched. "
                            f"{decision_dict.get('reason', '')}"
                        )
        # Server-side Guardrail: Block BUY/SELL entries with low confidence (< 75.0%)
        min_conf_threshold = 75.0
        action_str = str(decision_dict.get("action", "HOLD")).upper()
        conf_val = float(decision_dict.get("confidence", 80.0) or 0.0)
        if action_str in ("BUY", "SELL") and conf_val < min_conf_threshold:
            logger.warning(
                f"[{account_id}/{snapshot.bot_id}] Guardrail blocked low-confidence {action_str}: "
                f"{conf_val:.1f}% < {min_conf_threshold:.1f}%. Fallback to HOLD."
            )
            decision_dict["action"] = "HOLD"
            decision_dict["reason"] = f"[Guardrail Blocked] Confidence {conf_val:.1f}% < {min_conf_threshold:.1f}% threshold. {decision_dict.get('reason', '')}"

        # Server-side Guardrail: US Index Alignment & Portfolio Risk Check on final decision
        if action_str in ("BUY", "SELL"):
            can_trade, risk_reason = get_portfolio_manager().check_risk(
                symbol=snapshot.symbol,
                side=action_str,
                volume=float(decision_dict.get("volume_lots") or 0.01),
                account_balance=snapshot.account_balance,
                account_id=account_id,
                used_margin=snapshot.account_margin,
                bot_id=snapshot.bot_id,
            )
            if not can_trade:
                logger.warning(
                    f"[{account_id}/{snapshot.bot_id}] [RISK GUARD] {action_str} rejected -> HOLD: {risk_reason}"
                )
                decision_dict["action"] = "HOLD"
                decision_dict["reason"] = f"[Risk Guard] {risk_reason}. {decision_dict.get('reason', '')}"

        # TMS/ORB CLOSE_ALL Guard: block panic exits with a wrong-side or missing reversal signal.
        if not is_judas and not is_flowrsi and action_str == "CLOSE_ALL":
            close_reject_reason = validate_tms_close_decision(snapshot, decision_dict)
            if close_reject_reason:
                logger.warning(
                    f"[{account_id}/{snapshot.bot_id}] [TMS CLOSE GUARD] CLOSE_ALL rejected -> HOLD: "
                    f"{close_reject_reason}. Position left untouched."
                )
                decision_dict["action"] = "HOLD"
                decision_dict["reason"] = (
                    f"[CLOSE Guard] {close_reject_reason}. Position left untouched. "
                    f"{decision_dict.get('reason', '')}"
                )

        vol_display = "Auto (Risk Engine)" if float(decision_dict.get('volume_lots', 0) or 0) == 0 else f"{decision_dict.get('volume_lots')} lots"
        logger.info(
            f"[LLM DECISION] {account_id}/{snapshot.bot_id} -> Action: {decision_dict.get('action', 'HOLD')} | "
            f"Vol: {vol_display} | SL: {decision_dict.get('sl_pips', 0)}p | "
            f"TP: {decision_dict.get('tp_pips', 0)}p | Conf: {decision_dict.get('confidence', 80.0):.1f}% | "
            f"Reason: {decision_dict.get('reason', '')}"
        )

        try:
            record_ai_decision(decision_dict)
            await broadcast_decision(decision_dict)
        except Exception:
            pass

        return AgentDecision(**decision_dict)
    except Exception as e:
        error_desc = describe_llm_error(e)
        logger.error(f"[{account_id}/{snapshot.bot_id}] LLM Error: {error_desc}")
        fallback = generate_fallback_decision(snapshot, error_desc)
        logger.info(
            f"[FALLBACK DECISION] {account_id}/{snapshot.bot_id} -> Action: {fallback.action} | "
            f"new_sl_price: {fallback.new_sl_price} | Conf: {fallback.confidence:.1f}% | Reason: {fallback.reason}"
        )
        # Record it like a model decision so the dashboard shows the bot running on the fallback.
        try:
            fallback_dict = fallback.model_dump()
            fallback_dict["is_fallback"] = True
            record_ai_decision(fallback_dict)
            await broadcast_decision(fallback_dict)
        except Exception:
            pass
        return fallback

# Bot telemetry and portfolio reporting routes (app/portfolio_api.py). Included here so they keep
# their place right after /trade in the route table.
app.include_router(portfolio_router)


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "false").lower() in ("true", "1", "yes")
    uvicorn.run("app.server:app", host=host, port=port, reload=reload, reload_dirs=["app"] if reload else None)
