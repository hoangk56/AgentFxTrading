"""Deterministic gates and guards around the /trade LLM call.

Macro TMS cross-lock registry, bot-type detection, the Judas sweep and TMS/ORB cycle gates, the
ADJUST / CLOSE_ALL validators, the per-class breakout-distance limits and the safety fallback.

Split out of app/server.py, which re-exports every name here. The portfolio manager is read through
app.portfolio.get_portfolio_manager() at call time (one shared place: app.portfolio.portfolio_manager),
so a test replaces it there, not on app.server.
"""
import datetime
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.accounts import get_account_registry
from app.portfolio import get_portfolio_manager, is_us_index
from app.trade_models import AgentDecision, MarketSnapshot, StrategyData

logger = logging.getLogger("AgentFxTrading")

# Macro TMS cross-lock published by the bots, one entry per symbol and macro timeframe:
# {"EURUSD": {"Hour": {"bias", "bars_since_cross", "source", "timestamp", "bar_bucket"}}}.
# Only a bot's own macro calculation is recorded. AiAgentBot and FlowRsiBot compute it
# with the same TDI/Stochastic settings, so a FlowRSI bot can borrow a session bot's lock.
_TMS_CROSS_LOCK_REGISTRY: Dict[str, Dict[str, dict]] = {}

# A cross-lock is held until the opposite cross is confirmed, however long that takes: on
# 2026-09-23 GBPUSD, EURUSD, AUDUSD and XAUUSD stayed BULLISH for 31-48 H1 bars while they fell.
# Past this age a lock no longer describes the trend and does not gate. FlowRsiBot replaces such
# a lock by its macro EMA bias itself (TmsSignals.bias_source "ema"). Keep equal to its
# MaxMacroLockAgeBars default.
MACRO_LOCK_MAX_AGE_BARS = 24

_SUB_HOUR_TIMEFRAME_SECONDS = {"Minute": 60, "Minute5": 300, "Minute15": 900, "Minute30": 1800}


def _cross_lock_bar_bucket(timeframe: str, ts: float) -> int:
    """The clock bucket a lock recorded at ts stays valid in.

    A lock covers the macro bars closed so far, so it expires when the next one closes:
    at the top of the hour for H1. H4 and D1 closes depend on the broker's day offset, so
    they expire hourly too, which is early but never late.
    """
    return int(ts // _SUB_HOUR_TIMEFRAME_SECONDS.get(timeframe, 3600))


def update_tms_cross_lock(symbol: str, bias: str, bars_since_cross: int = 0,
                          source: str = "Macro TMS", timeframe: str = "Hour"):
    """Record a bot's own macro TMS cross-lock for (symbol, macro timeframe)."""
    sym = (symbol or "").upper()
    b = (bias or "").upper()
    if not sym or b not in ("BULLISH", "BEARISH"):
        return
    tf = timeframe or "Hour"
    now = time.time()
    _TMS_CROSS_LOCK_REGISTRY.setdefault(sym, {})[tf] = {
        "bias": b,
        "bars_since_cross": max(0, int(bars_since_cross or 0)),
        "timestamp": now,
        "bar_bucket": _cross_lock_bar_bucket(tf, now),
        "source": source,
    }


def get_tms_cross_lock(snapshot: MarketSnapshot) -> Tuple[str, int, str]:
    """
    Returns (locked_bias, bars_since_cross, source) of the macro TMS cross-lock.
    1. The snapshot's own macro TMS, computed by the bot from macro bars: its cross-lock while
       no older than MACRO_LOCK_MAX_AGE_BARS, or the macro EMA bias FlowRsiBot sends in its
       place once the lock is older.
    2. Another bot's lock for the same symbol and macro timeframe, recorded during the
       current macro bar and no older than MACRO_LOCK_MAX_AGE_BARS.
    3. Otherwise NEUTRAL. The gate stays open rather than letting a chart-timeframe
       cross or a multi-timeframe trend_bias stand in for the macro cross-lock.
    """
    if snapshot.tms and (snapshot.tms.bias or "").upper() in ("BULLISH", "BEARISH"):
        if (snapshot.tms.bias_source or "").lower() == "ema":
            return snapshot.tms.bias.upper(), snapshot.tms.bars_since_cross, f"{snapshot.bot_id} (Macro EMA)"
        if snapshot.tms.bars_since_cross <= MACRO_LOCK_MAX_AGE_BARS:
            return snapshot.tms.bias.upper(), snapshot.tms.bars_since_cross, f"{snapshot.bot_id} (Macro TMS)"

    tf = snapshot.tms_timeframe or "Hour"
    cached = _TMS_CROSS_LOCK_REGISTRY.get((snapshot.symbol or "").upper(), {}).get(tf)
    if (cached and cached["bar_bucket"] == _cross_lock_bar_bucket(tf, time.time())
            and cached["bars_since_cross"] <= MACRO_LOCK_MAX_AGE_BARS):
        return cached["bias"], cached["bars_since_cross"], cached["source"]

    return "NEUTRAL", 0, "None"

def detect_swing_market_structure(bars_list: Optional[List[Any]], cur_p: float) -> Tuple[str, float, float]:
    """
    Detects true market structure (BULLISH_HH_HL, BEARISH_LH_LL, SIDEWAYS)
    from fractal swing points in bars_list (newest first).
    Returns (structure_label, recent_high, recent_low).
    """
    if not bars_list or len(bars_list) < 5:
        return "SIDEWAYS", 0.0, 0.0

    chron = list(reversed(bars_list))
    n = len(chron)

    swing_highs = []  # (index, price)
    swing_lows = []   # (index, price)

    for i in range(1, n - 1):
        b_prev, b_curr, b_next = chron[i-1], chron[i], chron[i+1]
        h_prev = getattr(b_prev, 'high', b_prev.get('high', 0.0) if isinstance(b_prev, dict) else 0.0)
        h_curr = getattr(b_curr, 'high', b_curr.get('high', 0.0) if isinstance(b_curr, dict) else 0.0)
        h_next = getattr(b_next, 'high', b_next.get('high', 0.0) if isinstance(b_next, dict) else 0.0)

        l_prev = getattr(b_prev, 'low', b_prev.get('low', 0.0) if isinstance(b_prev, dict) else 0.0)
        l_curr = getattr(b_curr, 'low', b_curr.get('low', 0.0) if isinstance(b_curr, dict) else 0.0)
        l_next = getattr(b_next, 'low', b_next.get('low', 0.0) if isinstance(b_next, dict) else 0.0)

        if h_curr > h_prev and h_curr >= h_next:
            swing_highs.append((i, h_curr))
        if l_curr < l_prev and l_curr <= l_next:
            swing_lows.append((i, l_curr))

    last_h = swing_highs[-1][1] if swing_highs else max(getattr(b, 'high', b.get('high', 0.0) if isinstance(b, dict) else 0.0) for b in chron)
    last_l = swing_lows[-1][1] if swing_lows else min(getattr(b, 'low', b.get('low', 0.0) if isinstance(b, dict) else 0.0) for b in chron)

    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        last_sh, prev_sh = swing_highs[-1][1], swing_highs[-2][1]
        last_sl, prev_sl = swing_lows[-1][1], swing_lows[-2][1]

        if last_sh > prev_sh and last_sl > prev_sl:
            return "BULLISH_HH_HL", last_h, last_l
        elif last_sh < prev_sh and last_sl < prev_sl:
            return "BEARISH_LH_LL", last_h, last_l
        elif last_sh < prev_sh and last_sl > prev_sl:
            return "SIDEWAYS_COMPRESSION", last_h, last_l
        elif last_sh > prev_sh and last_sl < prev_sl:
            return "SIDEWAYS_EXPANSION", last_h, last_l
        else:
            return "SIDEWAYS", last_h, last_l
    elif len(swing_highs) >= 2:
        if swing_highs[-1][1] > swing_highs[-2][1]:
            return "BULLISH_HH", last_h, last_l
        else:
            return "BEARISH_LH", last_h, last_l
    elif len(swing_lows) >= 2:
        if swing_lows[-1][1] > swing_lows[-2][1]:
            return "BULLISH_HL", last_h, last_l
        else:
            return "BEARISH_LL", last_h, last_l

    return "SIDEWAYS", last_h, last_l

def is_judas_sweep_bot(snapshot: MarketSnapshot) -> bool:
    """Detect whether snapshot belongs to an Asian Range Judas Sweep / SMC bot."""
    if snapshot.strategy is not None and (
        snapshot.strategy.asian_high > 0 or 
        snapshot.strategy.killzone_session not in ("NONE", "Outside Killzones", "")
    ):
        return True
    bot_name = (snapshot.bot_id or "").lower()
    return "judas" in bot_name or "asian" in bot_name or "sweep" in bot_name

def is_flow_rsi_bot(snapshot: MarketSnapshot) -> bool:
    """Detect whether snapshot belongs to a FlowRSI / Nested RSI SMC bot."""
    bot_name = (snapshot.bot_id or "").lower()
    if "flowrsi" in bot_name or "flow_rsi" in bot_name or "nestedrsi" in bot_name:
        return True
    if snapshot.fast_rsi is not None and snapshot.slow_rsi is not None:
        return True
    return False

def _resolve_account(snapshot: MarketSnapshot) -> str:
    registry = get_account_registry()
    return registry.upsert_from_bot(
        account_number=snapshot.account_number,
        account_type=snapshot.account_type,
        label=snapshot.account_label,
        balance=snapshot.account_balance,
        equity=snapshot.account_equity,
    )

# ---- Judas position-management guardrails ----
# ADJUST may only lock profit (move SL past entry) after the position has progressed
# at least this far toward TP; prevents premature break-even / panic management.
JUDAS_ADJUST_MIN_TP_PROGRESS = 0.40


def validate_judas_adjust_decision(snapshot: MarketSnapshot, decision_dict: Dict[str, Any]) -> Optional[str]:
    """Validate an LLM ADJUST decision against an open Judas position.

    Returns a rejection reason when the ADJUST must be downgraded to HOLD with the
    position left untouched, or None when the ADJUST is structurally sound.
    Guards against: SL/TP placed on the wrong side of the market (would force a
    Profit-Lock exit or broker reject) and premature profit-locks at tiny profit.
    """
    pos = snapshot.position
    if pos is None:
        return "No open position to adjust (position is FLAT)"
    side = pos.resolved_side
    entry = pos.entry_price or 0.0
    bid = snapshot.bid or 0.0
    ask = snapshot.ask or 0.0
    new_sl = float(decision_dict.get("new_sl_price") or 0.0)
    new_tp = float(decision_dict.get("new_tp_price") or 0.0)
    tp = float(pos.tp_price or pos.tp or 0.0)

    if side == "BUY":
        if new_sl > 0 and new_sl >= bid:
            return (f"new_sl_price {new_sl:g} is at/above market bid {bid:g} on BUY - "
                    "a stop above the market cannot protect a long")
        if new_tp > 0 and new_tp <= ask:
            return f"new_tp_price {new_tp:g} is at/below market ask {ask:g} on BUY"
        if new_sl > 0 and entry > 0 and new_sl > entry and tp > entry:
            progress = (bid - entry) / (tp - entry)
            if progress < JUDAS_ADJUST_MIN_TP_PROGRESS:
                return (f"premature profit-lock: new_sl_price {new_sl:g} above entry {entry:g} while only "
                        f"+{max(bid - entry, 0.0):g} ({progress:.0%} of TP distance < {JUDAS_ADJUST_MIN_TP_PROGRESS:.0%})")
    elif side == "SELL":
        if new_sl > 0 and new_sl <= ask:
            return (f"new_sl_price {new_sl:g} is at/below market ask {ask:g} on SELL - "
                    "a stop below the market cannot protect a short")
        if new_tp > 0 and new_tp >= bid:
            return f"new_tp_price {new_tp:g} is at/above market bid {bid:g} on SELL"
        if new_sl > 0 and entry > 0 and new_sl < entry and tp > 0 and entry > tp:
            progress = (entry - ask) / (entry - tp)
            if progress < JUDAS_ADJUST_MIN_TP_PROGRESS:
                return (f"premature profit-lock: new_sl_price {new_sl:g} below entry {entry:g} while only "
                        f"+{max(entry - ask, 0.0):g} ({progress:.0%} of TP distance < {JUDAS_ADJUST_MIN_TP_PROGRESS:.0%})")
    return None


# ---- TMS position-management guardrails ----
# Allow a protective exit only after this share of the SL distance is given back.
TMS_CLOSE_MIN_ADVERSE_SL_RATIO = 0.60
# Allow a profit-taking exit from this reward:risk ratio onwards.
TMS_CLOSE_MIN_PROFIT_SL_RATIO = 1.00


def validate_tms_close_decision(snapshot: MarketSnapshot, decision_dict: Dict[str, Any]) -> Optional[str]:
    """Validate an LLM CLOSE_ALL against an open TMS/ORB position.

    Returns a rejection reason when the exit must be downgraded to HOLD, or None when valid.
    Accepts the exit only when one of these holds:
      - Macro H1 exit signal is true (BUY -> macro.exit_long, SELL -> macro.exit_short), or
      - Chart exit signal is true IF macro is unavailable (fallback for chart-only tests/setups), or
      - Adverse excursion >= 60% of the SL distance (capital protection), or
      - Profit >= 1:1 R (locking gains).
    Blocks premature exits on minor M15 pullbacks when Macro H1 structure remains intact.
    """
    pos = snapshot.position
    if pos is None:
        return None

    side = pos.resolved_side
    entry = pos.entry_price or 0.0
    bid = snapshot.bid or 0.0
    ask = snapshot.ask or 0.0
    sl = float(pos.sl_price or pos.sl or 0.0)

    chart = snapshot.chart_tms
    macro = snapshot.tms
    # Priority given to Macro H1 exit signals to avoid getting shaken out by M15 minor pullbacks
    if side == "BUY":
        exit_flag_ok = bool(macro and macro.exit_long) if macro else bool(chart and chart.exit_long)
        flag_desc = f"macro_exit_long={bool(macro and macro.exit_long)}, chart_exit_long={bool(chart and chart.exit_long)}"
    elif side == "SELL":
        exit_flag_ok = bool(macro and macro.exit_short) if macro else bool(chart and chart.exit_short)
        flag_desc = f"macro_exit_short={bool(macro and macro.exit_short)}, chart_exit_short={bool(chart and chart.exit_short)}"
    else:
        return None

    if exit_flag_ok:
        return None

    sl_dist = abs(entry - sl) if (entry > 0 and sl > 0) else 0.0
    if sl_dist <= 0:
        return None  # cannot size the excursion -> do not interfere

    adverse = (entry - bid) if side == "BUY" else (ask - entry)
    profit = (bid - entry) if side == "BUY" else (entry - ask)
    if adverse >= TMS_CLOSE_MIN_ADVERSE_SL_RATIO * sl_dist:
        return None
    if profit >= TMS_CLOSE_MIN_PROFIT_SL_RATIO * sl_dist:
        return None

    return (f"no {side}-side exit signal ({flag_desc}) and only "
            f"{adverse / sl_dist:.0%} of SL distance in drawdown "
            f"(protective exit needs >= {TMS_CLOSE_MIN_ADVERSE_SL_RATIO:.0%} or >= 1:1 R profit)")


def evaluate_judas_sweep_gate(snapshot: MarketSnapshot, account_id: Optional[str] = None) -> Optional[AgentDecision]:
    """
    Deterministic Gate for SMC / Asian Range Judas Sweep Bot.
    Filters out invalid setups before querying LLM.
    """
    strat = snapshot.strategy
    if strat is None:
        return None

    has_open_pos = (
        snapshot.position is not None
        or (snapshot.active_positions is not None and len(snapshot.active_positions) > 0)
    )

    # When NO open positions exist (New Entry Discovery Mode):
    if not has_open_pos:
        # Gate 1: No Sweep detected or outside Killzone
        if strat.bias_direction == "NONE":
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                confidence=90.0,
                reason="Judas Sweep Gate: Outside Killzone or no liquidity sweep detected",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

        # Gate 2: Pre-filter mode is MANAGE_ONLY
        if strat.bias_direction == "MANAGE_ONLY":
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                confidence=90.0,
                reason="Judas Sweep Gate: Pre-filter is MANAGE_ONLY with no open positions to manage",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

        # Gate 2b: Structural invalidation. The cBot's Judas Structural Guard locks a sweep
        # side once an M15 bar closes decisively beyond the Asian boundary; the level is then
        # a breakout level, not a sweep level, so mean-reversion entries are dead for the
        # session. Mirrored here so the LLM is never asked for a trade the cBot must reject.
        if strat.bias_direction in ("BUY", "SELL"):
            broken = strat.asian_low_broken if strat.bias_direction == "BUY" else strat.asian_high_broken
            if broken:
                boundary = "Asian Low" if strat.bias_direction == "BUY" else "Asian High"
                return AgentDecision(
                    action="HOLD",
                    volume_lots=0.01,
                    sl_pips=0.0,
                    tp_pips=0.0,
                    confidence=90.0,
                    reason=(
                        f"Judas Sweep Gate: {boundary} was broken by a decisive M15 close this session "
                        f"(breakout day, mean-reversion invalidated). {strat.bias_direction} sweep side locked by the cBot Structural Guard."
                    ),
                    request_id=snapshot.request_id,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe
                )

        # Gate 3: Stale Sweep Signal (> 3 bars since Judas Sweep occurred)
        if strat.signal_window_bars > 3:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                confidence=85.0,
                reason=f"Judas Sweep Gate: Signal is stale ({strat.signal_window_bars} bars elapsed since sweep > 3 max)",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

        # Gate 4: Invalid Asian Range width (too narrow < 20 pips or too wide > 600 pips on Gold)
        # Gate 4: Invalid Asian Range width (symbol-specific bounds)
        if strat.asian_range_pips > 0:
            sym_up = (snapshot.symbol or "").upper()
            if "XAU" in sym_up or "GOLD" in sym_up:
                min_asian_pips, max_asian_pips = 100.0, 10000.0  # $10.00 to $100.00 (or $1.00-$100.00 depending on broker digits)
            elif any(jpy in sym_up for jpy in ["JPY"]):
                min_asian_pips, max_asian_pips = 15.0, 200.0
            elif "BTC" in sym_up:
                min_asian_pips, max_asian_pips = 10000.0, 400000.0  # $100 to $4,000 USD on BTC
            elif any(cr in sym_up for cr in ["ETH", "CRYPTO"]):
                min_asian_pips, max_asian_pips = 800.0, 35000.0     # $8 to $350 USD on ETH
            elif any(idx in sym_up for idx in ["UK100", "GB100"]):
                min_asian_pips, max_asian_pips = 120.0, 800.0       # 12-80 FTSE points (UK100 pip = 0.1 pt)
            elif any(idx in sym_up for idx in ["US30", "USTEC", "DE40", "NAS100", "DJ30", "GER40", "JP225", "NIKKEI", "HK50", "US500"]):
                min_asian_pips, max_asian_pips = 50.0, 4000.0
            else:
                min_asian_pips, max_asian_pips = 12.0, 100.0  # Allow tight 12-20p Asian sessions for EURUSD/GBPUSD
            
            if strat.asian_range_pips < min_asian_pips or strat.asian_range_pips > max_asian_pips:
                return AgentDecision(
                    action="HOLD",
                    volume_lots=0.01,
                    sl_pips=0.0,
                    tp_pips=0.0,
                    confidence=85.0,
                    reason=f"Judas Sweep Gate: Asian Range width abnormal ({strat.asian_range_pips:.0f} pips not in {min_asian_pips:.0f}-{max_asian_pips:.0f}p valid range)",
                    request_id=snapshot.request_id,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe
                )

        # Gate 5: One sweep trade per Asian boundary per session (repeat-liquidity-grab dedupe).
        # Prevents re-entering the same Asian Low/High after it was already swept & traded today.
        if strat.bias_direction in ("BUY", "SELL"):
            side = strat.bias_direction
            try:
                traded = get_portfolio_manager().count_positions_opened_on(
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    side=side,
                    account_id=account_id or snapshot.account_id or "default",
                )
            except Exception as ex:
                logger.warning(f"Judas sweep dedupe query failed: {ex}")
                traded = 0
            if traded > 0:
                boundary = "Asian Low" if side == "BUY" else "Asian High"
                return AgentDecision(
                    action="HOLD",
                    volume_lots=0.01,
                    sl_pips=0.0,
                    tp_pips=0.0,
                    confidence=90.0,
                    reason=f"Judas Sweep Gate: {boundary} sweep already traded {traded}x today ({side}); repeat sweep of the same liquidity level blocked until next session",
                    request_id=snapshot.request_id,
                    bot_id=snapshot.bot_id,
                    symbol=snapshot.symbol,
                    timeframe=snapshot.timeframe
                )

    return None

# A genuine expansion ends chop: allow a fresh, momentum-confirmed ORB breakout to
# bypass the choppy-regime gate instead of waiting for the regime label to catch up.
CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT = 3
# ...but not in an extreme chop regime (too many failed breakouts = chop trap), and
# only when the expansion is large enough relative to volatility.
CHOPPY_OVERRIDE_MAX_OR_FLIPS = 7
CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR = 0.5

# ---- Calibrated breakout-distance limits per asset class (pips) ----
# direct_*: Model 1 (direct breakout entry) ceiling. Beyond it the breakout candle is
#           exhausted and only a qualified Model 2 retest + TDI bounce may enter.
# absolute_*: hard ceiling that ALSO blocks Model 2, i.e. price is at an extreme far from
#             the OR boundary. Both scale with ATR and are bounded by the per-class cap.
BREAKOUT_DISTANCE_LIMITS = (
    # (symbol tokens, prompt label, direct ATR x, direct cap, absolute ATR x, absolute cap)
    (("USTEC", "NAS100"), "USTEC/NAS100", 1.3, 700.0, 3.2, 2100.0),
    (("US30", "DJ30"), "US30/DJ30", 1.5, 950.0, 3.4, 2800.0),
    (("US500", "SPX500"), "US500/SPX500", 1.4, 150.0, 3.4, 450.0),
    (("DE40", "GER40"), "DE40/GER40", 1.5, 700.0, 3.4, 1900.0),
    (("UK100", "GB100"), "UK100/GB100", 1.5, 550.0, 3.4, 1600.0),
    (("JP225", "NIKKEI", "JPN225"), "JP225/Nikkei", 1.8, 3000.0, 3.8, 7000.0),
    (("HK50", "HSI"), "HK50/HangSeng", 1.5, 800.0, 3.4, 2200.0),
    (("XAU", "GOLD"), "Gold", 1.8, 1500.0, 3.6, 3500.0),
    (("BTC", "CRYPTO"), "BTC/Crypto", 1.5, 37500.0, 3.5, 130000.0),
    (("ETH", "SOL", "XRP"), "ETH/SOL/XRP", 1.5, 5250.0, 3.5, 35000.0),
    (("JPY",), "JPY Crosses", 1.6, 55.0, 3.6, 120.0),
    (("EURUSD", "GBPUSD", "USDCAD", "AUDUSD", "NZDUSD", "USDCHF"), "Forex Majors", 1.5, 30.0, 3.4, 70.0),
)

# Model 1 direct-entry window in M15 bars after the ORB breakout. MUST match the cBot
# parameter AiAgentBot.MaxBarsAfterBreakout, which decides `in_entry_window`.
MODEL1_ENTRY_WINDOW_BARS = 8

# Model 2 (retest + TDI bounce) stays valid this many M15 bars after the ORB breakout.
MAX_BARS_SINCE_BREAKOUT_MODEL2 = 20


def resolve_breakout_limits(symbol: str, atr_pips: Optional[float]) -> tuple:
    """(direct ceiling, absolute ceiling) in pips for a symbol, scaled by ATR."""
    sym = (symbol or "").upper()
    for tokens, _label, direct_atr, direct_cap, absolute_atr, absolute_cap in BREAKOUT_DISTANCE_LIMITS:
        if any(token in sym for token in tokens):
            break
    else:
        _tokens, _label, direct_atr, direct_cap, absolute_atr, absolute_cap = BREAKOUT_DISTANCE_LIMITS[-1]
    if atr_pips and atr_pips > 0:
        return min(atr_pips * direct_atr, direct_cap), min(atr_pips * absolute_atr, absolute_cap)
    return direct_cap, absolute_cap


def breakout_distance_prompt() -> str:
    """Per-class Model 1 ceilings for the LLM prompt (single source: BREAKOUT_DISTANCE_LIMITS)."""
    return ", ".join(f"<= {cap:.0f}p on {label}" for _tokens, label, _da, cap, _aa, _acap in BREAKOUT_DISTANCE_LIMITS)
def check_us_index_conflict(symbol: str, snapshot: MarketSnapshot, account_id: str) -> Optional[str]:
    """
    Check if a proposed US index trade direction conflicts with an existing open US index position.
    Returns a description of the opposing open position if a conflict exists, or None.
    """
    if not is_us_index(symbol):
        return None
    try:
        pm = get_portfolio_manager()
        conn = pm._get_conn()
        try:
            cursor = conn.execute(
                "SELECT symbol, side FROM positions WHERE status = 'open' AND account_id = ?",
                (account_id,)
            )
            open_pos = cursor.fetchall()
            if not open_pos:
                return None

            tms_bias = (snapshot.tms.bias or "").upper() if snapshot.tms else ""
            orb_dir = (snapshot.orb.breakout_direction or "").lower() if snapshot.orb else ""

            potential_buy = (tms_bias == "BULLISH" or orb_dir == "up")
            potential_sell = (tms_bias == "BEARISH" or orb_dir == "down")

            opposing = []
            for row in open_pos:
                pos_sym = row[0]
                pos_side = str(row[1]).upper()
                if is_us_index(pos_sym):
                    if pos_side == "BUY" and potential_sell and not potential_buy:
                        opposing.append(f"{pos_sym} ({pos_side})")
                    elif pos_side == "SELL" and potential_buy and not potential_sell:
                        opposing.append(f"{pos_sym} ({pos_side})")

            return ", ".join(opposing) if opposing else None
        finally:
            conn.close()
    except Exception as e:
        logger.debug(f"Error checking US index conflict: {e}")
        return None



def evaluate_cycle_gate(snapshot: MarketSnapshot, account_id: Optional[str] = None) -> Optional[AgentDecision]:
    """
    Deterministic Cycle Gate (Cost Gate) for TMS + ORB Strategy.
    Evaluates whether an expensive LLM call can be safely bypassed with an immediate deterministic action.
    Returns AgentDecision if gated, or None if LLM call is required.
    """
    if not snapshot.tms:
        return None

    # 1. When we HAVE an open position:
    # Trao toan quyen quyet dinh quan ly vi the cho AI (LLM) tren tat ca cac bot.
    # Khong can thiep hoac tu y CLOSE_ALL bang cac rule co hoc cung (nhu TDI M15 cross hay MFE giveback),
    # de AI co khong gian cho lenh tho (breathing room) va quan ly vi the thong minh.
    has_open_pos = (
        snapshot.position is not None
        or (snapshot.active_positions is not None and len(snapshot.active_positions) > 0)
    )
    if has_open_pos:
        return None

    # 2. When we DO NOT have an open position (Flat):
    # Only candidate setups with aligned TMS + ORB should reach LLM.

    # Gate 2.1: Session Gate
    if snapshot.session is not None:
        if not snapshot.session.is_trading_time or snapshot.session.phase in ("pre", "closed"):
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=f"Cycle gate: Market outside trading session (phase={snapshot.session.phase}, is_trading_time={snapshot.session.is_trading_time})"
            )

    # Gate 2.1.1: NYSE Cash Open Buffer (13:10 – 13:35 UTC / 9:10 – 9:35 AM NY)
    # Khung 15 phút trước và 5 phút sau giờ mở sàn Mỹ (9:30 AM NY) là giai đoạn gom hàng / quét thanh khoản
    # có xác suất False Breakout cao nhất trong ngày của phiên New York.
    # Chặn mở lệnh mới (chuyển về HOLD) trong khoảng thời gian này, bảo toàn vốn trước bẫy Pre-market sweep.
    session_name = (snapshot.session.session_name if snapshot.session else "").lower()
    is_ny_session = (
        "newyork" in session_name
        or "ny" in session_name
        or is_us_index(snapshot.symbol)
        or any(s in snapshot.symbol.upper() for s in ["XAU", "GOLD"])
    )

    if is_ny_session:
        current_dt = None
        if snapshot.bars and getattr(snapshot.bars[0], "time", None):
            try:
                t_str = str(snapshot.bars[0].time)
                if "T" in t_str:
                    current_dt = datetime.datetime.fromisoformat(t_str.replace("Z", "+00:00"))
                else:
                    current_dt = datetime.datetime.strptime(t_str[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
            except Exception:
                current_dt = None

        if current_dt is None:
            current_dt = datetime.datetime.now(datetime.timezone.utc)

        is_us_index_sym = is_us_index(snapshot.symbol)
        is_us_index_premarket = False
        is_nyse_buffer = False
        try:
            from zoneinfo import ZoneInfo
            ny_dt = current_dt.astimezone(ZoneInfo("America/New_York"))
            ny_minute = ny_dt.hour * 60 + ny_dt.minute
            # For US Equity Indices: Pre-market & Cash Open M15 formation (before 9:45 AM NY = 585 min)
            is_us_index_premarket = is_us_index_sym and (ny_minute < 585)
            # For general NY session (Gold, FX): 9:10 AM NY (550 min) to 9:35 AM NY (575 min)
            is_nyse_buffer = (550 <= ny_minute <= 575)
        except Exception:
            utc_dt = current_dt.astimezone(datetime.timezone.utc)
            utc_minute = utc_dt.hour * 60 + utc_dt.minute
            # In summer UTC-4: 9:45 AM NY is 13:45 UTC (825 min); in winter UTC-5: 14:45 UTC (885 min)
            is_us_index_premarket = is_us_index_sym and (utc_minute < 825)
            # 13:10 UTC is 790 min; 13:35 UTC is 815 min
            is_nyse_buffer = (790 <= utc_minute <= 815)

        if is_us_index_premarket:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason="Cycle gate: US Index Pre-market / Cash Open Buffer active (trading prohibited before 9:45 AM NY / 13:45 UTC summer). Awaiting Cash Open Range formation."
            )

        if is_nyse_buffer:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason="Cycle gate: NYSE Cash Open Buffer active (13:10 - 13:35 UTC / 9:10 - 9:35 AM NY). Pre-market liquidity sweep protection."
            )


    # Gate 2.1.3: US Index Alignment Gate (Directional Macro Flow)
    # Đảm bảo các chỉ số chứng khoán Mỹ (US30, USTEC, US500) phải giao dịch đồng pha theo dòng tiền vĩ mô.
    # Ngăn chặn quét tín hiệu / gọi LLM khi đang có vị thế chỉ số Mỹ khác mở ngược chiều.
    if is_us_index(snapshot.symbol):
        acc_id = account_id or _resolve_account(snapshot)
        opposing = check_us_index_conflict(snapshot.symbol, snapshot, acc_id)
        if opposing:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=f"Cycle gate: US Index Alignment Guard - opposing open position in {opposing}. All US indices (US30, USTEC, US500) must trade in the same direction."
            )
    # Gate 2.2: Loss Streak Gate (Circuit breaker)
    if snapshot.loss_streak >= 3:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Loss streak active ({snapshot.loss_streak} consecutive losses)"
        )

    # Gate 2.3: TMS Bias Gate. The cross lock never downgrades to NEUTRAL once a confirmed
    # cross exists, so this only fires while the bot has no confirmed macro cross yet.
    bias = snapshot.tms.bias.upper()
    if bias == "NEUTRAL":
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason="Cycle gate: TMS bias is NEUTRAL"
        )

    # Gate 2.3.1: Post-TP Gate (Anti-FOMO / Structural Pullback Re-entry Check)
    if snapshot.tms.post_tp_gate_active:
        blocked_side = (snapshot.tms.post_tp_gate_side or "").upper()
        if (blocked_side == "BUY" and bias == "BULLISH") or (blocked_side == "SELL" and bias == "BEARISH") or not blocked_side:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=f"Cycle gate: Post-TP Protection active (blocking {blocked_side or 're-entry'} until valid structural pullback >= 0.5x ATR occurs)"
            )

    # Gate 2.4: ORB State Gate
    orb = snapshot.orb
    if orb is None or not orb.or_complete or orb.breakout_direction is None:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason="Cycle gate: No active decisive ORB breakout"
        )

    # Check if a qualified TDI Bounce or Dynamic EMA Retest Continuation (Model 2) is active
    chart_tms = snapshot.chart_tms or snapshot.tms
    is_standard_bounce = (
        (bias == "BULLISH" and chart_tms.tdi_bounce_bull and chart_tms.price_above_ema) or
        (bias == "BEARISH" and chart_tms.tdi_bounce_bear and chart_tms.price_below_ema)
    )
    is_ema_retest_continuation = False
    if bias == "BULLISH":
        is_ema_retest_continuation = (
            chart_tms.price_above_ema
            and chart_tms.green_tf_slope > 0
            and chart_tms.green_tf_value >= 48.0
            and not chart_tms.ha_turned_red
            and (chart_tms.long_entry or chart_tms.stoch_bull or chart_tms.angle_ok_long)
        )
    elif bias == "BEARISH":
        is_ema_retest_continuation = (
            chart_tms.price_below_ema
            and chart_tms.green_tf_slope < 0
            and chart_tms.green_tf_value <= 52.0
            and not chart_tms.ha_turned_green
            and (chart_tms.short_entry or chart_tms.stoch_bear or chart_tms.angle_ok_short)
        )
    has_bounce = is_standard_bounce or is_ema_retest_continuation

    # Gate 2.4.1: Calibrated Breakout Distance & Exhaustion Filter per Symbol/Asset Class
    # 1) max_direct_breakout_dist: Max distance for Model 1 Direct Breakout. Beyond this,
    #    the breakout candle is considered exhausted; direct entry is BANNED, requiring
    #    a structural Retest + TDI Bounce (Model 2).
    # 2) max_breakout_dist: Absolute ceiling beyond which even Model 2 Bounce trades are overextended.
    atr_ref = snapshot.atr_pips if snapshot.atr_pips and snapshot.atr_pips > 0 else None
    sym_upper = snapshot.symbol.upper()

    max_direct_breakout_dist, max_breakout_dist = resolve_breakout_limits(snapshot.symbol, atr_ref)

    # 1. Absolute overextension check (applies to both Model 1 and Model 2)
    if orb.breakout_distance_pips > max_breakout_dist:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Breakout overextended ({orb.breakout_distance_pips:.1f}p > max {max_breakout_dist:.1f}p threshold). Avoid chasing at extremes."
        )

    # 2. Exhaustion Breakout check for Model 1 Direct Entry:
    # If the breakout distance exceeds max_direct_breakout_dist, entering directly is chasing an exhaustion move.
    # Entry is strictly prohibited unless a qualified TDI Bounce (Model 2) has formed.
    if orb.breakout_distance_pips > max_direct_breakout_dist and not has_bounce:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=(
                f"Cycle gate: Breakout candle exhausted ({orb.breakout_distance_pips:.1f}p > direct max {max_direct_breakout_dist:.1f}p threshold). "
                f"Model 1 direct entry prohibited; wait for Retest + TDI Bounce (Model 2)."
            )
        )

    # For Gold (XAUUSD / GOLD), enforce minimum decisive breakout distance >= 150.0 pips ($1.50)
    # to filter out minor noise / false breakouts around OR boundaries.
    min_decisive_threshold = 150.0 if ("XAU" in sym_upper or "GOLD" in sym_upper) else None
    if min_decisive_threshold and orb.breakout_distance_pips < min_decisive_threshold and not has_bounce:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Gold breakout not decisive ({orb.breakout_distance_pips:.1f}p < min {min_decisive_threshold:.1f}p / $1.50 threshold)"
        )

    if not orb.is_decisive and not has_bounce:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Breakout not decisive ({orb.breakout_distance_pips:.1f}p < threshold)"
        )

    # Model 2 Bounce / Retest stays valid until MAX_BARS_SINCE_BREAKOUT_MODEL2 bars
    if not orb.in_entry_window:
        if orb.bars_since_breakout > MAX_BARS_SINCE_BREAKOUT_MODEL2:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=f"Cycle gate: Breakout is stale (bars_since_breakout={orb.bars_since_breakout} > {MAX_BARS_SINCE_BREAKOUT_MODEL2}). Re-entry prohibited."
            )
        if not has_bounce:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=f"Cycle gate: Outside entry window (bars_since_breakout={orb.bars_since_breakout}) with no qualified Bounce/Retest"
            )

    # Gate 2.5: Directional Alignment Gate (TMS vs ORB)
    orb_dir = orb.breakout_direction.lower()
    if bias == "BULLISH" and orb_dir != "up":
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Conflict - TMS {bias} vs ORB breakout {orb_dir}"
        )
    if bias == "BEARISH" and orb_dir != "down":
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            reason=f"Cycle gate: Conflict - TMS {bias} vs ORB breakout {orb_dir}"
        )

    # Gate 2.6: Choppy Market Gate (Chop trap brake)
    # The choppy label is backward-looking (it counts failed breakouts / OR flips), so
    # requiring "not choppy" to enter structurally forbids the very breakout that ends
    # the chop. A fresh, momentum-confirmed breakout is therefore allowed to override
    # the block; anything else stays gated.
    if snapshot.market and snapshot.market.regime == "choppy" and snapshot.market.or_flips >= 5:
        chart = snapshot.chart_tms
        fresh_momentum_confirmed = False
        expansion_ok = atr_ref is None or orb.breakout_distance_pips >= (CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR * atr_ref)
        if (
            chart is not None
            and orb.breakout_direction in ("up", "down")
            and orb.bars_since_breakout <= CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT
            and snapshot.market.or_flips <= CHOPPY_OVERRIDE_MAX_OR_FLIPS
            and expansion_ok
        ):
            if orb.breakout_direction == "up":
                fresh_momentum_confirmed = chart.price_above_ema and chart.green_tf_slope > 0 and not chart.ha_turned_red
            else:
                fresh_momentum_confirmed = chart.price_below_ema and chart.green_tf_slope < 0 and not chart.ha_turned_green

        if not fresh_momentum_confirmed:
            return AgentDecision(
                action="HOLD",
                volume_lots=0.01,
                sl_pips=0.0,
                tp_pips=0.0,
                reason=(
                    f"Cycle gate: Market is CHOPPY ({snapshot.market.or_flips} failed OR breakouts) "
                    f"and no fresh momentum-confirmed expansion "
                    f"(bars={orb.bars_since_breakout}, dir={orb.breakout_direction}, "
                    f"dist={orb.breakout_distance_pips:.1f}p, atr={atr_ref if atr_ref else 0:.0f}p, "
                    f"max_flips={CHOPPY_OVERRIDE_MAX_OR_FLIPS}, min_dist={CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR:.1f}x ATR)"
                )
            )
        logger.info(
            f"[CYCLE GATE] {snapshot.bot_id} Choppy override: fresh {orb.breakout_direction} breakout "
            f"(bars_since_breakout={orb.bars_since_breakout}, dist={orb.breakout_distance_pips:.1f}p, "
            f"or_flips={snapshot.market.or_flips}) with aligned momentum -> evaluating entry"
        )

    # All entry criteria met! Valid candidate setup -> Invoke LLM for entry sizing & SL/TP validation
    return None

def generate_fallback_decision(snapshot: MarketSnapshot, error_msg: str) -> AgentDecision:
    """
    Deterministic rule-based fallback when LLM fails (timeout/error).
    Protects open positions instead of passively returning an empty HOLD.
    """
    pos = snapshot.position
    strat = snapshot.strategy or StrategyData()
    sym = snapshot.symbol
    bid = snapshot.bid
    ask = snapshot.ask

    # Flat position -> safe to HOLD
    if not pos:
        return AgentDecision(
            action="HOLD",
            volume_lots=0.01,
            sl_pips=0.0,
            tp_pips=0.0,
            confidence=50.0,
            reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Flat position held.",
            request_id=snapshot.request_id,
            bot_id=snapshot.bot_id,
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe
        )

    side = (pos.resolved_side or pos.type or "").upper()
    entry = pos.entry_price or 0.0
    cur_sl = pos.sl or pos.sl_price or 0.0
    pnl = pos.resolved_pnl or pos.pnl or 0.0

    # 1. Position in profit -> Move SL to Break-Even only if profit is significant (not minor noise)
    sym_up = (sym or "").upper()
    if "BTC" in sym_up:
        min_be_profit_price = 150.0
    elif "ETH" in sym_up:
        min_be_profit_price = 15.0
    elif "XAU" in sym_up or "GOLD" in sym_up:
        min_be_profit_price = 5.0
    elif "JPY" in sym_up:
        min_be_profit_price = 0.20  # ~20 pips
    else:
        min_be_profit_price = 0.0020  # ~20 pips for standard forex

    price_gain = (entry - ask) if side == "SELL" else (bid - entry)
    if price_gain >= min_be_profit_price and entry > 0:
        spread = abs(ask - bid)
        safe_be_sl = round(entry + spread * 0.5, 2) if side == "SELL" else round(entry - spread * 0.5, 2)
        if side == "SELL" and (cur_sl == 0 or cur_sl > safe_be_sl):
            return AgentDecision(
                action="ADJUST",
                new_sl_price=safe_be_sl,
                confidence=75.0,
                reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Position in verified profit (+${price_gain:.2f} >= +${min_be_profit_price:.2f}) -> Moving SL to Break-Even ({safe_be_sl}).",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )
        elif side == "BUY" and (cur_sl == 0 or cur_sl < safe_be_sl):
            return AgentDecision(
                action="ADJUST",
                new_sl_price=safe_be_sl,
                confidence=75.0,
                reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Position in verified profit (+${price_gain:.2f} >= +${min_be_profit_price:.2f}) -> Moving SL to Break-Even ({safe_be_sl}).",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

    # 2. Position in drawdown: check recent swing high/low to tighten SL safely
    if side == "SELL" and strat.recent_high > 0 and ask > 0:
        if strat.recent_high > ask and (cur_sl == 0 or strat.recent_high < cur_sl):
            return AgentDecision(
                action="ADJUST",
                new_sl_price=strat.recent_high,
                confidence=70.0,
                reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Tightening SELL SL to recent swing high ({strat.recent_high}) to cap risk.",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )
    elif side == "BUY" and strat.recent_low > 0 and bid > 0:
        if strat.recent_low < bid and (cur_sl == 0 or strat.recent_low > cur_sl):
            return AgentDecision(
                action="ADJUST",
                new_sl_price=strat.recent_low,
                confidence=70.0,
                reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Tightening BUY SL to recent swing low ({strat.recent_low}) to cap risk.",
                request_id=snapshot.request_id,
                bot_id=snapshot.bot_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe
            )

    # 3. Default fallback: keep position with current protective SL
    return AgentDecision(
        action="HOLD",
        volume_lots=0.01,
        sl_pips=0.0,
        tp_pips=0.0,
        confidence=50.0,
        reason=f"[SAFETY FALLBACK] LLM call failed ({error_msg}). Retaining protective SL ({cur_sl}).",
        request_id=snapshot.request_id,
        bot_id=snapshot.bot_id,
        symbol=snapshot.symbol,
        timeframe=snapshot.timeframe
    )
