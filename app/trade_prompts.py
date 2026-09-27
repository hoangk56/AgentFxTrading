"""LLM prompts of the /trade endpoint (TMS/ORB system and user prompts, Judas sweep prompts) and price formatting.

Split out of app/server.py, which re-exports every name here.
"""
from typing import Optional

from app.trade_gates import MAX_BARS_SINCE_BREAKOUT_MODEL2, MODEL1_ENTRY_WINDOW_BARS, breakout_distance_prompt
from app.trade_models import MarketSnapshot, StrategyData, TmsSignals

def _pip_size_for_symbol(sym_up: str) -> float:
    """
    Fallback pip scale per asset class.

    Broker digit conventions for indices/commodities vary, so the authoritative value is the
    Symbol.PipSize the cBot reports in the snapshot; this table only covers bots that omit it.
    Verified against live Asian ranges: USTEC 0.1, UK100 0.1, XAUUSD 0.01, GBPUSD 0.0001.
    """
    if any(idx in sym_up for idx in ["US30", "USTEC", "DE40", "NAS100", "DJ30", "GER40", "UK100", "GB100", "JP225", "NIKKEI", "JPN225", "HK50", "HSI", "US500", "SPX500"]):
        return 0.1
    if any(k in sym_up for k in ["BTC", "ETH", "XAU", "GOLD", "JPY"]):
        return 0.01
    return 0.0001

def format_price(price: Optional[float], symbol: str) -> str:
    """Format price dynamically according to symbol asset class and decimal convention."""
    if price is None:
        return "0.0"
    sym = (symbol or "").upper()
    if "JPY" in sym:
        return f"{price:.3f}"
    elif any(k in sym for k in ["XAU", "GOLD", "US30", "USTEC", "DE40", "NAS100", "DJ30", "GER40", "UK100", "GB100", "JP225", "NIKKEI", "JPN225", "HK50", "HSI", "US500", "SPX500", "BTC", "ETH", "SOL", "XRP"]):
        return f"{price:.2f}"
    else:
        return f"{price:.5f}"

def build_system_prompt(snapshot: MarketSnapshot) -> str:
    """
    Dynamic System Prompt Factory (inspired by dnse-kash architecture).
    Bakes live asset characteristics, market regime guidelines, and quantitative edge-case rules directly into context.
    """
    sym_up = snapshot.symbol.upper()
    is_gold = "XAU" in sym_up or "GOLD" in sym_up
    is_crypto = any(cr in sym_up for cr in ["BTC", "ETH", "SOL", "XRP", "CRYPTO"])
    is_index = any(idx in sym_up for idx in ["US30", "USTEC", "DE40", "NAS100", "DJ30", "GER40", "UK100", "GB100", "JP225", "NIKKEI", "JPN225", "HK50", "HSI", "US500", "SPX500"])

    if is_crypto:
        asset_type = "Cryptocurrency (High Volatility Momentum)"
    elif is_gold:
        asset_type = "Gold (Commodity/Metals)"
    elif is_index:
        asset_type = "Stock Index (High Beta Momentum)"
    else:
        asset_type = "Forex Major/Cross"

    current_regime = snapshot.market.regime if snapshot.market else "mixed"
    regime_guideline = ""
    if current_regime == "trending":
        regime_guideline = (
            "• CURRENT REGIME IS TRENDING: The execution engine (cBot) automatically DISABLES fixed TP (Trend TP Disabled). "
            "Your trade will ride the full momentum wave managed by dynamic Trailing Stop and Giveback Floor. "
            "Focus on accurate entry timing & direction — SL/TP are sized by the ATR engine."
        )
    elif current_regime == "choppy":
        regime_guideline = (
            "• CURRENT REGIME WAS CHOPPY (High failed breakouts / OR flips): The market was oscillating and hunting stops, "
            "but a chop label is backward-looking. A FRESH decisive ORB breakout (few bars since breakout) with aligned "
            "momentum slope means the chop is ending - treat that Model 1 breakout as valid, do not wait for the regime "
            "label to flip. Avoid entering stale/retest setups and never chase extended moves in a choppy regime."
        )
    else:
        regime_guideline = (
            "• CURRENT REGIME IS MIXED/FORMING: Maintain standard trading discipline; entry only on confirmed setups."
        )

    return f"""You are an AUTONOMOUS quantitative trading agent running the TMS (Trend Momentum Signal) + ORB (Opening Range Breakout) strategy for {snapshot.symbol} ({asset_type}).

## Core Contract: "LLM proposes, Code disposes"
You analyze market structure and propose trade actions. The deterministic execution harness (cBot + Portfolio Manager) enforces hard guardrails (spread checks, correlation limits, trailing stops, and EOD force-flatten). Always output valid structured JSON.

## SL/TP AND SIZING ARE COMPUTED DETERMINISTICALLY BY THE ENGINE
- The cBot overrides any sl_pips / tp_pips you return with ATR-based distances.
- Return sl_pips = 0, tp_pips = 0, and volume_lots = 0.0. Your job is strictly DIRECTION (action) and TIMING — never pip targets or lot sizing.

## Strategy Logic

### 1. TMS (Trend Momentum Signal) = DIRECTIONAL BIAS
- The bias is a CROSS LOCK: the most recent confirmed cross (TDI Green/Red cross + Heikin Ashi direction + Stochastic K vs D on the same bar) sets the direction and is HELD until the next confirmed reverse cross. There is no "lines intertwined" NEUTRAL bias.
- **NEUTRAL** is therefore reported only while no confirmed cross exists yet (insufficient history). NEVER enter when the bias is NEUTRAL.
- Entries MUST align with the current TMS bias.

### 2. ORB (Opening Range Breakout) = ENTRY TRIGGER
- Opening Range (OR) defines the high/low of the first 15 minutes of the active session.
- Valid entry requires price closing beyond OR boundary in the direction of TMS bias.
- Breakout must be DECISIVE (breakout_distance_pips >= threshold) and within entry window (bars_since_breakout <= {MODEL1_ENTRY_WINDOW_BARS}).
- A breakout that has re-entered the range is reported as NO breakout (direction = none) — never trade a failed breakout.

### 3. ENTRY MODELS (DIRECT BREAKOUT vs RETEST + TDI BOUNCE)
- **Model 1: Direct Momentum Breakout**: Price closes decisively beyond OR boundary with steep TDI slope in bias direction. Valid when in entry window (`bars_since_breakout <= {MODEL1_ENTRY_WINDOW_BARS}`) AND distance is within fresh direct breakout threshold (`breakout_distance <= 1.0x - 1.5x ATR` or symbol direct cap). If the breakout candle is already oversized/exhausted (`> direct breakout limit`), Model 1 direct entry is strictly PROHIBITED; you MUST wait for Model 2 (Retest + TDI Bounce).
- **Model 2: Breakout Retest / Continuation (High R:R Continuation)**:
  - Price broke out of OR, pulled back toward OR boundary / EMA5 without breaking opposite structure.
  - **Continuation Triggers**: Verified TDI Bounce (`tdi_bounce_bull` / `tdi_bounce_bear`) OR Dynamic EMA Retest Continuation (price holds EMA5 with momentum re-accelerating in trend direction).
  - **Strict Price Action Verification**: Only valid when price is properly positioned relative to the 5 EMA (`price_above_ema = true` for BUY, `price_below_ema = true` for SELL), `bars_since_breakout <= {MAX_BARS_SINCE_BREAKOUT_MODEL2}`, and distance is NOT overextended beyond max ceiling. NEVER enter a trade when price is overextended far from EMA5 or floating at extreme exhaustion levels.
### 4. Market Regime (Kaufman Efficiency Ratio & Chop Detection)
- **er_session / er_recent**: Kaufman Efficiency Ratio (|net move| / total path, 1.0 = pure directional trend, ~0 = pure oscillation).
- **or_flips**: Number of times price broke outside OR and closed back inside (flips >= 5 indicates chop trap day).
{regime_guideline}

### 5. Quantitative Edge-Case Rules (Battle-Tested Discipline)
- **EXHAUSTION BREAKOUT GUARD & ANTI-OVEREXTENSION**: NEVER chase extended breakouts. Direct entry (Model 1) requires price to be close to the OR boundary (breakout distance {breakout_distance_prompt()}). If the breakout candle exceeded this threshold, it is an Exhaustion Breakout -> declare HOLD. Entering on an exhausted breakout without a retest is strictly forbidden, even if the TMS bias cross just occurred.
- **BIAS-FRESH Rule**: A fresh TMS cross (`bars_since_cross <= 1`) validates trend initiation, but does NOT override the Exhaustion Breakout Guard. If the initial breakout candle traveled too far, wait for the first pullback and TDI Bounce / EMA Retest (Model 2) to enter with favorable Risk:Reward.
- **TDI BOUNCE / RETEST EXCEPTION TO ANTI-CHASE**: Standard Anti-Chase blocks entry when `bars_since_breakout >= 4` without a pullback. However, if a valid **TDI Bounce / Dynamic EMA Retest** is confirmed AND `bars_since_breakout <= {MAX_BARS_SINCE_BREAKOUT_MODEL2}` AND price is near EMA5, the pullback has occurred and resolved in favor of the trend -> Enter on the bounce/retest.
- **ANTI-CHASE Rule**: When bars_since_breakout >= 4 under an OLD bias (bars_since_cross >= 5) without a pullback/bounce, DO NOT chase at extremes. Declare HOLD.
- **POST-TP GATE (Anti-FOMO)**: Once a trade hits Take Profit or closes after a major win, the deterministic engine ARMS a blocker (`post_tp_gate_active = true`) preventing immediate re-entry in the same direction (`post_tp_gate_side`). It unlocks automatically only when a real Pullback (>= 0.5x ATR), OR Touch, or Bias Flip occurs. Never re-enter immediately at the peak of a move without a structural pullback.
- **POSITION BREATHING ROOM & PATIENCE**:
  - Trading requires room for normal market fluctuations. Never prematurely cut an open position on minor pullbacks or single-candle noise if price is still structurally valid and aligned with the macro trend. Stop Loss and Trailing Stop are dynamically managed by the engine via ATR.
- **POSITION MEMORY & GIVEBACK FLOOR (PROFIT LOCK-IN)**:
  - position.mfe_pips = PEAK floating profit reached.
  - position.giveback_pips = Profit given back from peak (MFE - Current PnL).
- **Golden Rule (2-Tier Profit Lock-in & Trailing Stop)**:
  - **Tier 1 (Moderate Gains - Trend Inception)**: Provides generous breathing room for the trend to develop through normal pullbacks. Activates when MFE >= 0.8x ATR (Forex/Metals) with 40% giveback cap, or MFE >= 1.5x ATR (min 1000p on US30 / 300p on USTEC) with 55% giveback cap for indices. Trailing stop tracks at standard 1.2x - 1.5x ATR.
  - **Tier 2 (Large Gains / Deep Trend Run)**: Activates when MFE >= 2.5x ATR (or >= 1200p on US30, >= 600p on USTEC, >= 400p on DE40, or >= 65% distance to TP). In Tier 2, giveback tolerance strictly tightens from 55% down to 35% (indices) and 30% (forex/metals), and trailing distance tightens to 0.9x ATR. When a position achieves large floating gains (e.g. +$15+ on US30), lock in at least 65% of peak gains; NEVER let a major win slip below +$11.
- **ASSET SCALE & RISK DISCIPLINE (CRYPTO / INDICES / METALS / FOREX)**:
  - Stop Loss is hard-capped by ATR guardrails and max dollar risk ($10–$15 max per trade on a $700 account).
  - On Gold (XAUUSD), 1 pip = $0.01. Do NOT trade with massive SLs > 1200 pips ($12).
  - On Crypto and Indices, several hundred pips is minimal noise (a small fraction of 1 ATR). Evaluate the actual chart trend structure.
### 6. Risk & Sizing (handled 100% by the engine — context only)
- SL/TP distances are computed by the cBot ATR engine (ATR on the chart timeframe); you do NOT provide them.
- Position volume is computed strictly by the cBot engine from risk-per-trade % (0.2%) and ATR-based SL. Always output volume_lots = 0.0.
## Decision Rules Summary

### Entry Criteria (ALL must be satisfied):
1. TMS Bias is clearly BULLISH (for BUY) or BEARISH (for SELL).
2. Valid Entry Trigger (Any of the following models):
   - **Model 1 (Direct Breakout)**: ORB Breakout (is_decisive = true, in_entry_window = true) AND price agrees with 5 EMA (price_above_ema = true for BUY, price_below_ema = true for SELL) AND breakout distance is NOT exhausted (<= 1.0x ATR / direct limit).
   - **Model 2 (Retest + TDI Bounce / EMA Continuation)**: Breakout Retest/Continuation with confirmed TDI Bounce (`tdi_bounce_bull` for BUY, `tdi_bounce_bear` for SELL) OR Dynamic EMA Retest with momentum slope aligned AND price alignment with 5 EMA (`price_above_ema` for BUY, `price_below_ema` for SELL).
   - **Model 3 (Fakeout Trap / Liquidity Sweep)**: Market is choppy (`or_flips > 0`), price recently broke opposite to Macro Bias (hunting liquidity), but immediately recovered back over 50% OR to trigger a Breakout aligned with Macro Bias.
3. Session is active (not ending / not closed).
4. Loss streak < 3.
5. **US Indices Alignment**: For US indices (US30, USTEC, US500), all open positions MUST align in the same direction. Conflicting trades (e.g. BUY USTEC while US30 is open SELL) are strictly PROHIBITED.
-> Any mismatch or conflicting signal -> HOLD.
### Exit Criteria:
1. session.phase = "ending" -> CLOSE_ALL (EOD safety).
2. Confirmed Reversal Signal: Macro H1 structural reversal (Macro exit_long=true for BUY, Macro exit_short=true for SELL) -> CLOSE_ALL. Intra-timeframe chart noise (M15 pullbacks while Macro H1 trend is intact) MUST be held (HOLD) to allow ATR Trailing Stop and OR range to work.
3. Significant Giveback on Winning Trade: Giveback reaches Tier 1 (40% Forex / 55% Indices) or Tier 2 (30% Forex / 35% Indices on large gains >= 2.5x ATR / 65% TP) with momentum stall or reversal -> CLOSE_ALL (Lock-in profit).
4. Otherwise (trade in normal consolidation or healthy pullback within trend) -> HOLD (let ATR SL/TP and Trailing Stop manage the trade).

## Output Format (JSON only)

{{
  "action": "BUY" | "SELL" | "CLOSE_ALL" | "HOLD",
  "volume_lots": 0.0,
  "sl_pips": 0,
  "tp_pips": 0,
  "reason": "Clear, concise technical justification (TMS bias, ORB breakout, Regime ER, Momentum slope)"
}}
"""


def build_judas_sweep_system_prompt(snapshot: MarketSnapshot) -> str:
    return "You are an elite Algorithmic Trading AI Co-Pilot for cTrader. Analyze the real-time market snapshot and output strictly valid JSON format with keys: \"action\" (\"BUY\"|\"SELL\"|\"HOLD\"|\"ADJUST\"|\"CLOSE_ALL\"), \"volume_lots\" (number), \"sl_pips\" (number), \"tp_pips\" (number), \"new_sl_price\" (number), \"new_tp_price\" (number), \"confidence\" (number between 0 and 100), \"reason\" (concise technical rationale). MANDATORY FOR BUY/SELL/ADJUST: You MUST provide the exact target price in \"new_tp_price\" (e.g. 2524.00 for ETH, 80120.00 for BTC) and protective stop in \"new_sl_price\" (e.g. 2454.00 for ETH, 79600.00 for BTC), NEVER 0.0. Output NO markdown explanations outside the JSON object."
def build_judas_sweep_user_prompt(snapshot: MarketSnapshot) -> str:
    strat = snapshot.strategy or StrategyData()
    sym_up = snapshot.symbol.upper()
    if "XAU" in sym_up or "GOLD" in sym_up:
        spread_pips = round(abs(snapshot.ask - snapshot.bid) / 0.01, 1)
    elif any(idx in sym_up for idx in ["US30", "USTEC", "DE40", "NAS100", "UK100", "GB100", "JP225", "NIKKEI", "HK50", "US500", "SPX500"]):
        spread_pips = round(abs(snapshot.ask - snapshot.bid), 1)
    elif any(cr in sym_up for cr in ["BTC", "ETH"]):
        spread_pips = round(abs(snapshot.ask - snapshot.bid), 1)
    elif "JPY" in sym_up:
        spread_pips = round(abs(snapshot.ask - snapshot.bid) / 0.01, 1)
    else:
        spread_pips = round(abs(snapshot.ask - snapshot.bid) / 0.0001, 1)

    if strat.atr > 0:
        if "JPY" in sym_up:
            atr_pips = strat.atr / 0.01 if strat.atr < 5.0 else strat.atr
        elif "XAU" in sym_up or "GOLD" in sym_up:
            atr_pips = strat.atr / 0.01 if strat.atr < 100.0 else strat.atr
        elif any(idx in sym_up for idx in ["US30", "USTEC", "DE40", "NAS100", "UK100", "GB100", "JP225", "NIKKEI", "HK50", "US500", "SPX500"]):
            atr_pips = strat.atr
        elif any(cr in sym_up for cr in ["BTC", "ETH", "SOL", "XRP"]):
            atr_pips = strat.atr / 0.01 if "ETH" in sym_up and strat.atr < 100.0 else strat.atr
        else:
            atr_pips = strat.atr / 0.0001 if strat.atr < 1.0 else strat.atr
    else:
        atr_pips = snapshot.atr_pips or 0.0
    open_pos_count = len(snapshot.active_positions) if snapshot.active_positions else (1 if snapshot.position else 0)
    has_open_pos = open_pos_count > 0 or snapshot.position is not None

    # 1. Format 50 chronological bars
    # 1. Format 50 chronological bars with Volume Delta approximation
    bar_lines = []
    if snapshot.bars:
        max_bars = min(50, len(snapshot.bars))
        chronological_bars = snapshot.bars[-max_bars:]
        for i, b in enumerate(chronological_bars):
            bar_idx = -(max_bars - 1 - i)
            o_val = b.open if b.open is not None else 0.0
            h_val = b.high if b.high is not None else 0.0
            l_val = b.low if b.low is not None else 0.0
            c_val = b.close if b.close is not None else 0.0
            v_val = b.volume if b.volume is not None else 0.0
            # Calculate Volume Delta & Imbalance:
            hl_range = h_val - l_val
            if hl_range > 0:
                buy_ratio = max(0.0, min(1.0, (c_val - l_val) / hl_range))
                delta_vol = v_val * (2.0 * buy_ratio - 1.0)
                delta_str = f" | Delta={'+' if delta_vol >= 0 else ''}{delta_vol:.0f}"
            else:
                delta_str = ""
            bar_lines.append(f"Bar[{bar_idx}]: O={format_price(o_val, snapshot.symbol)}, H={format_price(h_val, snapshot.symbol)}, L={format_price(l_val, snapshot.symbol)}, C={format_price(c_val, snapshot.symbol)}, V={v_val:.0f}{delta_str}")
    bars_formatted = "\n".join(bar_lines) if bar_lines else "No OHLCV bars available."

    # 2. Format recent trade history
    history_formatted = "No recent trades in the last 24h."
    if snapshot.recent_history:
        total_pnl = sum(h.pnl for h in snapshot.recent_history)
        win_count = sum(1 for h in snapshot.recent_history if h.pnl > 0)
        loss_count = sum(1 for h in snapshot.recent_history if h.pnl < 0)
        summary_header = f"[Session Performance: 24h PnL = {'+' if total_pnl >= 0 else ''}${total_pnl:.2f} | Wins: {win_count}, Losses: {loss_count}]"
        hist_lines = [
            f"  - {h.trade_type} {h.volume:.2f} lots @ {format_price(h.entry_price, snapshot.symbol)} -> Exit {format_price(h.exit_price, snapshot.symbol)} | PnL: {'+' if h.pnl >= 0 else ''}${h.pnl:.2f} | Closed: {h.exit_time}"
            for h in snapshot.recent_history
        ]
        history_formatted = summary_header + "\n" + "\n".join(hist_lines)

    # 3. Multi-timeframe summary
    mtf_summary = "Current Timeframe Only"
    if snapshot.multi_timeframe:
        cur = snapshot.multi_timeframe.current_tf
        h1 = snapshot.multi_timeframe.h1_tf
        h4 = snapshot.multi_timeframe.h4_tf
        lines = []
        for tf_ctx, label in [(cur, f"Current ({cur.timeframe if cur and cur.timeframe else 'M15'})"), (h1, "Higher TF (H1)"), (h4, "Major TF (H4)")]:
            if tf_ctx:
                sw_str = ""
                if tf_ctx.swing_structure:
                    sw = tf_ctx.swing_structure
                    sw_str = (
                        f" | Swings: High={format_price(sw.last_swing_high, snapshot.symbol)} ({sw.swing_high_type or 'N/A'}), "
                        f"Low={format_price(sw.last_swing_low, snapshot.symbol)} ({sw.swing_low_type or 'N/A'}), "
                        f"PrevH={format_price(sw.prev_swing_high, snapshot.symbol)}, "
                        f"PrevL={format_price(sw.prev_swing_low, snapshot.symbol)} "
                        f"[Struct: {sw.market_structure or 'SIDEWAYS'}]"
                    )
                adx_str = f" | ADX={tf_ctx.adx:.1f}" if hasattr(tf_ctx, "adx") and tf_ctx.adx > 0 else ""
                lines.append(f"- {label}: Bias={tf_ctx.trend_bias} | FastMA={format_price(tf_ctx.fast_tema, snapshot.symbol)} | SlowMA={format_price(tf_ctx.slow_tema, snapshot.symbol)} | RSI={tf_ctx.rsi:.1f}{adx_str}{sw_str}")
        if lines:
            mtf_summary = "\n".join(lines)

    # Mirror of the cBot Judas Structural Guard. A decisive M15 close beyond a boundary
    # converts the sweep level into a breakout level: the mean-reversion side is dead.
    if strat.asian_low_broken and strat.asian_high_broken:
        structural_note = "BOTH Asian boundaries decisively broken -> breakout day, all sweep entries LOCKED. Output 'HOLD'."
    elif strat.asian_low_broken:
        structural_note = "Asian Low decisively broken (M15 close) -> BUY sweep side LOCKED, mean-reversion long invalidated."
    elif strat.asian_high_broken:
        structural_note = "Asian High decisively broken (M15 close) -> SELL sweep side LOCKED, mean-reversion short invalidated."
    else:
        structural_note = "Both Asian boundaries intact (sweep entries permitted)."

    if not has_open_pos:
        return f"""You are a World-Class Institutional Forex Specialist & Quantitative Trader using SMART MONEY CONCEPTS (SMC) & Asian Range Judas Sweep.

=== NEW ENTRY DISCOVERY MODE ===
The cBot currently HAS NO OPEN POSITIONS. Your mission is to analyze the Asian Range Liquidity Sweep and identify high-probability Sniper entries.

=== 1. MARKET SNAPSHOT ===
- Symbol: {snapshot.symbol} | Timeframe: {snapshot.timeframe}
- Current Market Prices: Ask={format_price(snapshot.ask, snapshot.symbol)}, Bid={format_price(snapshot.bid, snapshot.symbol)} | Spread: {spread_pips:.1f} pips
- Account: Balance=${snapshot.account_balance:.2f} | Equity=${snapshot.account_equity:.2f}

=== 2. ASIAN RANGE & JUDAS SWEEP GATE CONTEXT ===
- Asian Session Range (00:00 - 06:00 UTC): High={format_price(strat.asian_high, snapshot.symbol)} | Low={format_price(strat.asian_low, snapshot.symbol)} | Range={strat.asian_range_pips:.0f} pips
- Active Killzone Window: {strat.killzone_session}
- Gate Signal Trigger: {strat.traditional_signal} (Bias: {strat.bias_direction})
- Bars Since Sweep: {strat.signal_window_bars} bar(s)
- Structural State: {structural_note}
⚠️ CONSTRAINT:
  - Gate=BUY -> Price swept Asian Low & rejected back up. You MAY ONLY suggest 'BUY' or 'HOLD'. NEVER 'SELL'.
  - Gate=SELL -> Price swept Asian High & rejected back down. You MAY ONLY suggest 'SELL' or 'HOLD'. NEVER 'BUY'.
  - Gate=MANAGE_ONLY -> Do NOT open new positions. Only 'ADJUST', 'HOLD', or 'CLOSE_ALL'.
  - Bars Since Sweep > 3 -> Signal is STALE. Strongly prefer 'HOLD'.
  - A LOCKED sweep side -> The boundary was already broken on a decisive M15 close. The Judas mean-reversion thesis is dead for this session; output 'HOLD'. NEVER propose an entry against a locked side.
  - volume_lots -> Always output 0. Volume is controlled by the cBot risk engine.

=== 3. MULTI-TIMEFRAME SMC SWING STRUCTURE (HH, HL, LH, LL) & BIAS ===
{mtf_summary}

=== 4. TECHNICAL INDICATORS & SWINGS ===
- Fast EMA: {format_price(strat.tema1, snapshot.symbol)} | Slow EMA: {format_price(strat.tema2, snapshot.symbol)}
- RSI (14): {strat.rsi:.1f}{f' | ADX: {strat.adx:.1f}' if strat.adx > 0 else ''}
- ATR (14 Volatility): {atr_pips:.1f} pips{f' ({format_price(strat.atr, snapshot.symbol)} price move)' if strat.atr > 0 else ''}
- Major Swing High (BSL / Resistance): {format_price(strat.recent_high, snapshot.symbol)}
- Major Swing Low (SSL / Support): {format_price(strat.recent_low, snapshot.symbol)}
=== 5. RECENT OHLCV CANDLE SEQUENCE (Last {len(bar_lines)} bars, chronological) ===
{bars_formatted}

=== 6. RECENT TRADE HISTORY (Last 24h, Max 5 trades) ===
{history_formatted}

=== 7. SMART MONEY CONCEPTS (SMC) & JUDAS SWEEP RULES ===
1. Judas Swing Reversal: Price fakeouts above Asian High or below Asian Low during London/NY Killzones, sweeps liquidity (BSL/SSL), and rejects back inside range.
2. Entry Confirmation: Validated Order Block, Fair Value Gap (FVG), or pinbar rejection on M15.
3. Technical SL & TP (MANDATORY EXACT PRICES):
   - new_tp_price: Targeted at opposing Asian Range boundary (Asian High for BUY, Asian Low for SELL) or target liquidity pool. You MUST provide the exact price in "new_tp_price".
   - new_sl_price: Placed safely beyond the sweep extreme spike (min floor 200 pips). You MUST provide the exact price in "new_sl_price".
   - sl_pips & tp_pips: Must match the distance between entry and new_sl_price / new_tp_price.

=== 8. VALID ACTIONS ===
- BUY: Validated Bullish Judas Sweep (Asian Low fakeout) + Order Block bounce. Must set new_tp_price and new_sl_price!
- SELL: Validated Bearish Judas Sweep (Asian High fakeout) + Order Block rejection. Must set new_tp_price and new_sl_price!
- HOLD: Choppy consolidation inside Asian Range, no sweep, or conflicting HTF bias.

=== 9. REFERENCE FEW-SHOT EXAMPLES ===
Example 1 (High-Probability Asian Low Sweep -> BUY with exact prices):
{{
  "action": "BUY",
  "volume_lots": 0.0,
  "sl_pips": 2500.0,
  "tp_pips": 5100.0,
  "new_sl_price": 2454.00,
  "new_tp_price": 2524.00,
  "confidence": 88.0,
  "reason": "Price swept Asian Low during London Open, printed pinbar rejection with positive Delta (+450), and aligned with H1 bullish order block. SL below sweep spike at 2454.00, TP at Asian High 2524.00."
}}

Example 2 (False Breakout / Stale Signal -> HOLD):
{{
  "action": "HOLD",
  "volume_lots": 0.0,
  "sl_pips": 0.0,
  "tp_pips": 0.0,
  "new_sl_price": 0.0,
  "new_tp_price": 0.0,
  "confidence": 85.0,
  "reason": "Sweep occurred 4 bars ago without swift displacement back inside range; negative Delta indicates heavy absorption. Holding flat."
}}
Reply strictly with JSON object."""
    else:
        pos_lines = []
        if snapshot.position:
            pos = snapshot.position
            cur_p = pos.current_price or snapshot.bid
            pos_lines.append(f"- Primary Position: {pos.resolved_side} {pos.volume or 0.01:.2f} lots @ Entry={format_price(pos.entry_price, snapshot.symbol)} | CurrentPrice={format_price(cur_p, snapshot.symbol)} | PnL=${pos.resolved_pnl:.2f} | SL={format_price(pos.sl or pos.sl_price, snapshot.symbol)} | TP={format_price(pos.tp or pos.tp_price, snapshot.symbol)} | Duration={pos.duration_minutes:.1f} mins")
        if snapshot.active_positions:
            for p in snapshot.active_positions:
                pos_lines.append(f"- Position ID {p.id}: {p.trade_type} {p.volume:.2f} lots @ Entry={format_price(p.entry_price, snapshot.symbol)} | SL={format_price(p.sl, snapshot.symbol)} | TP={format_price(p.tp, snapshot.symbol)} | Opened={p.entry_time}")
        running_pos_str = "\n".join(pos_lines) if pos_lines else "No position details."

        return f"""You are a World-Class Institutional Forex Specialist & Quantitative Risk Manager using SMART MONEY CONCEPTS (SMC) & Price Action.

=== ACTIVE POSITION MANAGEMENT MODE ===
The cBot currently HAS OPEN POSITIONS in the order book. Your PRIMARY MISSION is to EVALUATE AND MANAGE THESE EXISTING POSITIONS (Protect capital, lock in profits, adjust SL/TP, or exit safely).

=== 1. ACTIVE ORDER BOOK SNAPSHOT ===
- Symbol: {snapshot.symbol} | Timeframe: {snapshot.timeframe}
- Current Market Prices: Ask={format_price(snapshot.ask, snapshot.symbol)}, Bid={format_price(snapshot.bid, snapshot.symbol)} | Spread: {spread_pips:.1f} pips
- Account: Balance=${snapshot.account_balance:.2f} | Equity=${snapshot.account_equity:.2f}
- Running Positions:
{running_pos_str}

=== 2. TRADITIONAL STRATEGY GATE — MANDATORY CONSTRAINT ===
- Gate Direction: {strat.bias_direction}
- Signal Type: {strat.traditional_signal}
- Bars Since Cross: {strat.signal_window_bars} bar(s)
- Structural State: {structural_note}
⚠️ CONSTRAINT:
  - Gate=MANAGE_ONLY → Focus on managing existing positions. Do NOT open new ones.
  - volume_lots → Always output 0. Volume is controlled by the cBot risk engine.

=== 3. MULTI-TIMEFRAME SMC SWING STRUCTURE (HH, HL, LH, LL) & BIAS ===
{mtf_summary}

=== 4. TECHNICAL INDICATORS & SWINGS ===
- Fast EMA: {format_price(strat.tema1, snapshot.symbol)} | Slow EMA: {format_price(strat.tema2, snapshot.symbol)}
- RSI (14): {strat.rsi:.1f}{f' | ADX: {strat.adx:.1f}' if strat.adx > 0 else ''}
- ATR (14 Volatility): {atr_pips:.1f} pips{f' ({format_price(strat.atr, snapshot.symbol)} price move)' if strat.atr > 0 else ''}
- Major Swing High (Resistance): {format_price(strat.recent_high, snapshot.symbol)}
- Major Swing Low (Support): {format_price(strat.recent_low, snapshot.symbol)}
=== 5. RECENT OHLCV CANDLE SEQUENCE (Last {len(bar_lines)} bars, chronological) ===
{bars_formatted}

=== 6. POSITION MANAGEMENT EVALUATION RULES ===
1. Trend & Structure Health: Check if current structure still favors the open position.
   - Do NOT panic on minor 1-2 bar pullbacks or wicks on M15 if Higher Timeframe (H1) trend remains aligned and structure is intact. Let the position breathe towards TP!
2. Action Decisions:
   - HOLD: Position healthy and progressing towards TP. (Default choice during normal fluctuations).
   - ADJUST: Move SL to Break-Even OR Trailing Stop behind a verified structural swing/Order Block.
     ⚠️ CRITICAL STOP LOSS GEOMETRY CONSTRAINT:
       * For an open BUY position: new_sl_price MUST BE STRICTLY LESS THAN Current Bid (new_sl_price < {format_price(snapshot.bid, snapshot.symbol)}). A stop at or above market price is geometrically impossible and rejected!
       * For an open SELL position: new_sl_price MUST BE STRICTLY GREATER THAN Current Ask (new_sl_price > {format_price(snapshot.ask, snapshot.symbol)}). A stop at or below market price is geometrically impossible and rejected!
       * If an open position is UNDERWATER and technical structure breaks against it, NEVER attempt to tighten SL past the market price! You MUST output action "CLOSE_ALL" instead!
     ⚠️ MANDATORY PROFIT LOCK-IN & BREAK-EVEN RULES:
       * When a position reaches >= 40% of the distance to TP (or >= 1.0x R:R), you MUST ADJUST SL to Break-Even or trail behind the nearest M15 swing!
       * Minimum profit required BEFORE moving SL to Break-Even / Trailing:
         - BTCUSD: Position in profit by at least +$60.00 price gain (6,000 pips) OR >= 40% distance to TP.
         - ETHUSD: Position in profit by at least +$6.00 price gain (600 pips) OR >= 40% distance to TP.
         - XAUUSD: Position in profit by at least +$3.00 price gain (300 pips) OR >= 40% distance to TP.
         - Forex: Position in profit by at least +15 to +20 pips OR >= 40% distance to TP.
       * SPREAD BUFFER ON BREAK-EVEN: When moving SL to protect an order, set SL with breathing room beyond entry (e.g. entry + $10 on BTC, entry + $1 on ETH, entry + $0.50 on Gold for BUY) to lock in commission/spread!
     ⚠️ MANDATORY OUTPUT: You MUST specify the exact absolute price level in "new_sl_price" (e.g. 2475.50 for ETHUSD, 79900.00 for BTCUSD, 2898.50 for XAUUSD) and/or "new_tp_price". NEVER leave new_sl_price as 0.0 when ADJUSTing!
   - CLOSE_ALL: Exit immediately at market if:
       a) Position is UNDERWATER and M15/H1 technical structure breaks against the trade (e.g. price broke below Asian Low / entry for BUY, or opposing CHoCH). Cut losses immediately at market; NEVER hold all the way to full SL or attempt impossible stops!
       b) Trade was in substantial profit and reverses, printing a confirmed opposing CHoCH on M15 (e.g. decisive close back below Asian Low / entry for BUY). Do NOT hold all the way to full SL!
       c) Major opposing H1/H4 structural reversal occurs.
   - BUY / SELL: Scale-in ONLY if trend is extremely strong with fresh unmitigated Order Block.
=== 7. ASSET-SPECIFIC PIP & PRICE RULES ===
- Crypto (ETHUSD, BTCUSD): 1 pip = 0.01 ($0.01 move). Always calculate and output exact absolute price in "new_sl_price" and "new_tp_price".
- Gold (XAUUSD): 1 pip = 0.01 ($1.00 move = 100 pips). Always output exact absolute price in "new_sl_price".
- Forex (EURUSD, GBPUSD): 1 pip = 0.0001 (EURJPY, GBPJPY: 1 pip = 0.01).

Reply strictly with JSON object."""


def build_user_prompt(snapshot: MarketSnapshot) -> str:
    """Build structured prompt from pre-computed signals."""
    tms = snapshot.tms or TmsSignals()
    macro_tf = snapshot.tms_timeframe or "Macro"

    lines = [
        f"## Market: {snapshot.symbol} | Chart: {snapshot.timeframe} | Macro TMS: {macro_tf}",
        f"**Price**: Ask={snapshot.ask:.5f}, Bid={snapshot.bid:.5f}",
        "",
        f"### Macro TMS Signals ({macro_tf} - Directional Bias)",
        f"- **Macro Bias**: {tms.bias}",
        f"- Bars since cross ({macro_tf}): {tms.bars_since_cross}",
        f"- Cross direction: {tms.cross_direction or 'none'}",
        f"- TDI level: {tms.tdi_level}",
        f"- Macro Green Slope: {tms.green_tf_slope:.3f}",
        f"- Macro TDI Bounce: Bull={tms.tdi_bounce_bull}, Bear={tms.tdi_bounce_bear}",
        f"- Macro Exit Signals ({macro_tf}): exit_long={tms.exit_long}, exit_short={tms.exit_short} ({tms.exit_reason or 'none'})",
        f"- Post-TP Gate Active: {tms.post_tp_gate_active} (Blocking {tms.post_tp_gate_side or 'None'})",
    ]
    # Chart execution TMS signals (e.g. M15/M5)
    if snapshot.chart_tms:
        ctms = snapshot.chart_tms
        lines.extend([
            "",
            f"### Chart Execution Signals ({snapshot.timeframe} - Timing & Momentum)",
            f"- Chart HA Turned Green: {ctms.ha_turned_green}, Turned Red: {ctms.ha_turned_red}",
            f"- Price > EMA5: {ctms.price_above_ema}, Price < EMA5: {ctms.price_below_ema}",
            f"- Chart Stoch Bull: {ctms.stoch_bull}, Bear: {ctms.stoch_bear}",
            f"- Chart Green Momentum Value: {ctms.green_tf_value:.2f}",
            f"- Chart Green Momentum Slope: {ctms.green_tf_slope:.3f} (positive=rising, negative=falling)",
            f"- Chart TDI Bounce: Bull={ctms.tdi_bounce_bull}, Bear={ctms.tdi_bounce_bear}",
            f"- Chart Exit Signals: exit_long={ctms.exit_long}, exit_short={ctms.exit_short} ({ctms.exit_reason or 'none'})",
        ])
    else:
        lines.extend([
            "",
            f"**Exit signals:**",
            f"- exit_long: {tms.exit_long}",
            f"- exit_short: {tms.exit_short}",
            f"- exit_reason: {tms.exit_reason or 'none'}",
        ])
    if snapshot.orb:
        orb = snapshot.orb
        lines.extend([
            "",
            "### ORB (Opening Range Breakout)",
            f"- OR High: {orb.or_high:.5f}",
            f"- OR Low: {orb.or_low:.5f}",
            f"- OR Complete: {orb.or_complete}",
            f"- Breakout: {orb.breakout_direction or 'none'}",
            f"- Breakout distance: {orb.breakout_distance_pips:.1f} pips",
            f"- Is decisive: {orb.is_decisive}",
            f"- Bars since breakout: {orb.bars_since_breakout}",
            f"- In entry window: {orb.in_entry_window}",
            f"- Price position: {orb.price_position}",
        ])

    # Market regime info
    if snapshot.market:
        mkt = snapshot.market
        er_sess_str = f"{mkt.er_session:.2f}" if mkt.er_session is not None else "N/A"
        er_rec_str = f"{mkt.er_recent:.2f}" if mkt.er_recent is not None else "N/A"
        lines.extend([
            "",
            "### Market Regime",
            f"- Regime: {mkt.regime}",
            f"- ER Session: {er_sess_str}",
            f"- ER Recent (1h): {er_rec_str}",
            f"- OR Flips (Failed Breakouts): {mkt.or_flips}",
        ])

    # Position info
    if snapshot.position:
        pos = snapshot.position
        lines.extend([
            "",
            "### Position",
            f"- Side: {pos.side}",
            f"- Entry: {pos.entry_price:.5f}",
            f"- PnL: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_pips:.1f} pips)",
            f"- Peak MFE: {pos.mfe_pips:.1f} pips | Giveback: {pos.giveback_pips:.1f} pips",
            f"- SL: {pos.sl_price:.5f} | TP: {pos.tp_price:.5f}",
            f"- Bars held: {pos.bars_held}",
        ])
    else:
        lines.extend(["", "### Position: None"])

    # Session info
    if snapshot.session:
        sess = snapshot.session
        lines.extend([
            "",
            "### Session",
            f"- Name: {sess.session_name}",
            f"- Phase: {sess.phase}",
            f"- Minutes to end: {sess.minutes_to_end}",
            f"- Is trading time: {sess.is_trading_time}",
        ])

    # Day stats
    lines.extend([
        "",
        "### Day Stats",
        f"- Loss streak: {snapshot.loss_streak}",
        f"- Day PnL: {snapshot.day_pnl:.2f}",
        f"- Trades today: {snapshot.trades_today}",
    ])

    lines.extend([
        "",
        "---",
        "",
        "## YOUR TASK",
        "",
        "Based on the pre-computed signals:",
        "1. If session.phase = 'ending' and position open → CLOSE_ALL",
        "2. If position is open and a confirmed reversal occurred (exit_long=true for BUY, exit_short=true for SELL) → CLOSE_ALL",
        "3. If position is open and within normal trend fluctuation → HOLD (allow ATR Stop Loss / Trailing Stop to operate)",
        "4. If long_entry=true and TMS BULLISH and ORB breakout UP and is_decisive → BUY",
        "5. If short_entry=true and TMS BEARISH and ORB breakout DOWN and is_decisive → SELL",
        "6. If loss_streak >= 3 → HOLD",
        "7. Otherwise → HOLD",
        "",
        "SL/TP pips are ignored by the engine (ATR-based) — set sl_pips/tp_pips to 0.",
        "",
        "Output JSON decision.",
    ])

    return "\n".join(lines)
