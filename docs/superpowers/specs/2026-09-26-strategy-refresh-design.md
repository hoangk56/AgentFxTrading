# Strategy Refresh — TMS + ORB, Asian Range Judas Sweep, literature candidates — Design

**Date:** 2026-09-26
**Status:** Approved in chat section by section, awaiting spec review
**Follows:** `2026-09-25-strategy-lab-design.md` (the lab this runs in) and `research/STRATEGIES.md`
(66 catalogued strategies, nothing robust; live-bot ports JUDAS −$12.1k and TMSORB −$18.0k over 2023–2026)

## Goal

1. Rebuild **TMS + ORB** and **Asian Range Judas Sweep** from the canonical definitions of their names, not
   from the live cBots' code (the user judged that code does not follow the algorithms). The existing ports
   `research/lab/strategies/tmsorb.py` and `judas.py` stay untouched as the record of the live bots.
2. Add four strategies from the literature / trading canon that the catalog has not tested yet.
3. Test all of them once, in the strategy lab, against a bar written down before any result is seen.

Nothing in this round touches the cBots, the VPS, the production database or git history. If a variant
passes, bringing it into a cBot is a separate plan.

## Decisions taken in the brainstorm

| Question | Decision |
|---|---|
| Output | Lab first; cBot changes only for a variant that passes, in its own plan |
| New-strategy scope | Intraday session/event rules and multi-day rules, chosen by the strength of published evidence, excluding everything the catalog already rejected |
| Old TMS+ORB / Judas code | Ignored. New code follows the canonical definitions below |
| Parameters | Fixed now from the sources. No tuning. A change after results are seen is a new variant and counts against the budget |
| Budget | 14 tests: T1–T5, J1–J5, N1–N4 |

Candidates considered and dropped (recorded in the catalog as `rejected` with the reason, not run):
pre-FOMC drift (gone after 2015, Kurov/Wolfe/Gilbert), FX weekend-gap fade (gaps > 20 pips are rare, Sunday
open spreads are wide), plain 60-min index ORB (K2/VB1 already failed), **FX carry** (moved out after the
design review: the lab's swaps are the 2026 rates held constant — `research/lab/costs.py` — so the carry
ranking would be one static basket and 2023–25 carry could not be measured; replaced by N4).

## Periods, account, costs

- **Check period** 2023-01-01 → 2024-12-31. Used only to check the code (trade counts, hand-inspected sample
  trades) before the full run. Bugs found there are fixed; parameters are not changed.
- **Holdout** 2025-01-01 → 2026-09-24 (end of data). Every variant runs on it once, in the full run.
- Lab rules unchanged: $10k, fixed units per symbol (`research/lab/universe.py` FIXED_UNITS), tick level,
  bid/ask fills, commission, swaps (2026 rates), one position at a time per strategy × symbol, no loss limits.
- All times below are local exchange / city times, converted with `zoneinfo` (Asia/Tokyo, Europe/London,
  Europe/Berlin, America/New_York), so daylight saving is exact. Bars are bid bars from `ctx.bars(minutes)`
  (UTC-aligned buckets; H4 buckets start at 00/04/08/12/16/20 UTC).

## Pass bar (pre-registered)

The unit is one variant pooled over its universe. It **passes** only if all hold:

1. Holdout: at least 100 trades; mean net R > 0 with **t ≥ 2.5** (t of per-trade net R; 2.5 instead of 2
   because 14 variants are tested).
2. Holdout: net $ > 0 in 2025 **and** in 2026 (Jan–Sep) separately.
3. Check period: mean net R > 0.
4. Holdout pooled net $ beats ≥ 95 % of the 20 random-entry control seeds (`research/lab/control.py`).
5. Mirrored prices, holdout: net $ > 0 — for rules that read price direction (all except N1 and N2, which
   trade a fixed direction by clock time).
6. Breadth: net $ > 0 over the holdout on ≥ 60 % of the variant's symbols (not applied to N2, one symbol).

The week-shuffle flag is computed and reported but is not part of the bar (it keeps intraday structure, so it
does not separate clock-time rules from noise). A pass means "worth a demo forward test", not "proven".

## Shared definitions

Added to `research/indicators.py` (or a new `research/lab/strategies/canon.py` for the lab-only helpers):

- **RSI(n)**: Wilder RSI of the bar close (exists: `research.indicators.rsi`; verify it is Wilder).
- **TDI** (Dean Malone defaults, the TMS template 13/34/2/7): RSI(13) of the close; **green** = SMA(2) of RSI,
  **red** = SMA(7) of RSI. The market base line (SMA 34) and the 1.6185 σ bands are not used by any rule.
- **Heiken Ashi**: ha_close = (O+H+L+C)/4, ha_open = (ha_open[−1] + ha_close[−1])/2 seeded with (O0+C0)/2.
  Bullish bar: ha_close > ha_open. TDI and Stoch are computed on the regular bars (as on an MT4 chart,
  where HA is a display overlay).
- **Stoch(8,3,3)**: raw %K = 100 (C − LL8)/(HH8 − LL8), slow %K = SMA3(raw), %D = SMA3(slow %K).
  "Pointing up" = slow %K > %D.
- **ATR20**: SMA(20) of the true range of the bars named (`research.indicators.atr_sma`, as the catalog's
  other rules). Only the protective stops of N1–N3 use it.
- **TMS state** on timeframe TF at time τ (last TF bar closed before τ): **bull** if green > red, green > 50
  and the HA bar is bullish; **bear** if green < red, green < 50 and the HA bar is bearish; otherwise none.
- **Fractal** (M5): a swing low at bar k if low[k] < low[k−1] and low[k] < low[k+1] (swing high mirrored);
  it is known from the close of bar k+1.
- **FVG** (3 bars a, a+1, a+2): bearish if low[a] > high[a+2], gap = [high[a+2], low[a]]; bullish if
  high[a] < low[a+2], gap = [high[a], low[a+2]].
- **Breakout by ticks**: a long triggers at the first tick with bid > level (fills at that tick's ask); a
  short at the first tick with bid < level (fills at the bid). Stops/targets follow the engine's rules
  (`research/lab/engine.py`).
- **Protective stop for R**: rules without a structural stop (N1–N3) carry one so every trade has a risk
  figure; it is part of the rule and can be hit.

## Family T — TMS + ORB

Sources: TMS = "Trading Made Simple" (eelfranz / BigE, ForexFactory 2011; template summarised on ProRealCode
and BabyPips): Heiken Ashi candles, TDI 13/2/7/34 with 32/50/68 levels, Stoch for confirmation; enter on
candle 1 or 2 after green crosses red, never candle 3+; stop beyond the nearest swing; exit when green
crosses back (or flattens/hooks — not mechanised); H4 is the author's timeframe, H1 the common alternative.
ORB = Toby Crabel's opening range breakout: the range of the first minutes of the session, stop entries at its
high and low, the first side filled is the trade, stop at the other side, out at the close.

**Sessions** (live preset groups kept; synthetic crosses use their preset donor's group):

| Group | Symbols | Opening range (local) | Session end (local) |
|---|---|---|---|
| Tokyo | USDJPY, AUDJPY, AUDUSD, CADJPY, AUDCAD | 09:00–09:15 Tokyo | 15:00 Tokyo |
| London | EURUSD, GBPUSD, EURJPY, GBPJPY, EURGBP, EURAUD, GBPAUD, EURCAD, GBPCAD, UK100 | 08:00–08:15 London | 16:30 London |
| Frankfurt | DE40 | 09:00–09:15 Berlin | 17:30 Berlin |
| New York FX | USDCAD, XAUUSD | 08:00–08:15 New York | 16:00 New York |
| New York cash | US30, USTEC, BTCUSD, ETHUSD | 09:30–09:45 New York | 16:00 New York |

BTC/ETH move from the live preset's FX New York session to the US cash open: crypto has no open of its own,
and the cash open is its main daily liquidity event.

**T1 — ORB** (all 22 symbols). Opening range (OR) = bid high/low of the OR window's ticks. From the OR end
for 3 hours (never past the session end) the first breakout of either side is the trade. SL = the other side
of the OR. No target. Exit at the session end. One trade per session. Skip the session if the OR width is
below 3 × the median spread of the OR window, or if the OR window has no ticks.

**T2 — TMS + ORB** (all 22). T1, but only a breakout **in the direction of the TMS state on H1** at the
breakout tick. A breakout event is the first tick beyond a level; that level re-arms once bid is back inside
the OR. An event against the state, or with state none, is skipped and does not end the session: a later event
in the TMS direction inside the window still trades.

**T3 — TMS + ORB, TMS exit** (all 22). T2, plus exit at the first tick after an H1 bar closes with green
crossed against the position (long: green < red), or at the session end, whichever comes first.

**T4 — TMS on H4** (all 22) and **T5 — TMS on H1** (all 22), the original system with no ORB:
- Cross up at bar i: green[i] > red[i] and green[i−1] ≤ red[i−1] (cross down mirrored).
- Entry decision at the close of bar i (candle 1), else at the close of bar i+1 (candle 2): go long when green
  is still above red, the HA bar just closed is bullish and Stoch is pointing up. Fill at the next tick.
  Neither candle qualifies → no trade until the next cross. (The "bounce off red" re-entry is not mechanised.)
- SL: long = lowest bid low of the last 5 bars up to the decision bar; short = highest bid high of those bars
  plus the spread at entry.
- Exit: the first tick after a bar closes with green crossed back (long: green < red), or the SL. No target;
  positions are held overnight and over weekends (swaps apply). An exit on a cross can be followed by an
  opposite entry decided on the same bar close.

## Family J — Asian Range Judas Sweep (ICT)

Sources: ICT Judas swing / Asian range (LuxAlgo, innercircletrader.net, FX Replay, FXNX summaries):
the Asian range is 20:00–00:00 New York; the New York midnight open is the day's reference price; in the
London killzone (02:00–05:00 New York) price runs one side of the Asian range (the Judas swing), then shifts
market structure on M5 with displacement that leaves a fair value gap; the entry is the retrace into the FVG,
the stop beyond the sweep, the target the opposite side of the Asian range.

Universe: all 22 except BTCUSD and ETHUSD (20 symbols): crypto trades around the clock and has no Asian
session structure. (The live-port result — BTC/ETH −$10.5k of −$12.1k — was seen before this choice; the
holdout decides.) A day is skipped when its Asian window has fewer than 36 of its 48 M5 bars (index CFD
breaks, holidays).

**J1 — ICT core.** For New York trading day d, on M5 bid bars:
1. Asian range = high/low of bars opening in [20:00 of d−1, 00:00 of d) New York. Midnight open = open of the
   first bar at or after 00:00 of d.
2. Sweep (bearish side): a bar in the killzone with high > Asian high. Sweep extreme H* = highest high since
   the first sweep bar; it keeps updating while the leg extends.
3. Reference swing low = the latest fractal low between the Asian-range start and the bar that set H* (its
   confirming bar k+1 at or before the H* bar). None → no setup on this side until H* updates.
4. MSS: a later bar inside the killzone closes below the reference swing low. A new high above H* first resets
   steps 2–4 with the new extreme.
5. FVG: the last bearish FVG whose third bar lies between the H* bar and the MSS bar (inclusive). None → the
   setup is dropped.
6. Order: sell limit at the FVG's near edge (high of its third bar). Fills at the first tick after the MSS bar
   with bid ≥ the limit, at that tick's bid. SL = H* + the spread at the MSS close (buy side: SL = the sweep low,
   both being hit when the bid reaches the extreme); TP = Asian low. The order is placed only if
   (limit − TP) ≥ (SL − limit). It is cancelled at the killzone end. (Bid cannot pass H* without first reaching
   the limit below it, so the "bid > H*" cancel never fires before a fill at tick level.)
7. Exit: SL, TP, or the first tick at or after 12:00 New York.
8. One filled trade per symbol per day. At most one pending order at a time; after a cancel, later setups in
   the killzone are allowed (either side). The bullish side is the mirror image.

**J2 — J1 + midnight-open filter.** Sell only if the limit is above the midnight open; buy only if below.
**J3 — J1 with TP = 2R** (entry ∓ 2 × the stop distance; no RR check).
**J4 — J1 in two killzones:** London 02:00–05:00 and New York AM 07:00–10:00, same Asian range, still one
filled trade per day.
**J5 — sweep-and-close, no MSS/FVG (ablation).** An M15 bar inside the London killzone with high > Asian high and
close < Asian high → sell at the first tick after its close; SL = highest high since the killzone opened + the
spread; TP = Asian low; skipped if TP distance < SL distance; exit at 12:00 New York; one trade per day. Bullish
mirrored. Tells whether the MSS/FVG step adds anything.

## Family N — literature candidates (one frozen version each)

**N1 — FX fixing reversal, London 16:00 fix** (Krohn, Mueller & Whelan, *Journal of Finance* 2024: the USD
appreciates into the Tokyo, ECB and London fixes and depreciates after them, every year of 21; gross returns
large, negative after indicative-quote spreads, positive at half spreads — so the question is our ECN costs).
Symbols: EURUSD, GBPUSD, AUDUSD, USDCAD, USDJPY. Each weekday: long USD 14:00 → 16:00 London (buy USDJPY and
USDCAD, sell EURUSD, GBPUSD, AUDUSD), then short USD 16:00 → 18:00 London. Protective SL 3 × ATR20(H1).
Time exits at the window ends.

**N2 — Gotobi, USDJPY** (Bessho, Sugimoto & Suzuki 2023: on gotobi days USDJPY rises from about 03:00 to the
09:55 Tokyo fix and falls after it). Gotobi days: the 5th, 10th, 15th, 20th, 25th and the last calendar day of
the month; one falling on a weekend moves to the Friday before (Japanese holidays are not modelled). Long
03:00 → 09:55 Tokyo, then short 09:55 → 11:55 Tokyo. Protective SL 3 × ATR20(H1).

**N3 — Market intraday momentum** (Gao, Han, Li & Zhou, *Journal of Financial Economics* 2018: the first
half-hour return, measured from the previous close, predicts the last half-hour return; also found in
international index ETFs). r1 = bid at open + 30 min / bid at the previous session's close − 1; trade sign(r1)
over the last 30 minutes of the session; skip when r1 = 0 or the previous close is missing (Monday uses Friday).
Sessions: US30, USTEC 09:30–16:00 New York; DE40 09:00–17:30 Berlin; UK100 08:00–16:30 London.
Protective SL 2 × ATR20(30-min bars). Different from the rejected LC1, which fades the 10:00–15:30 move.

**N4 — London breakout of the Asian range (follow)** (the classic retail "London breakout"; the opposite
hypothesis to Judas). FX 15 + XAUUSD. Range = bid high/low 00:00–07:00 London. From 07:00 to 10:00 London the
first breakout of either side is the trade; SL = range midpoint; no target; exit 16:00 London; one trade per
day; skip if the range is below 3 × its median spread.

## Code layout

- `research/indicators.py`: `tdi`, `heikin_ashi`, `stoch`, `atr_wilder` (plus tests in `research/tests/test_indicators.py`).
- `research/lab/strategies/canon.py`: local-time helpers (local day → UTC ms spans), the session table,
  fractals, FVG, the tick-breakout helper, TMS state.
- `research/lab/strategies/tms_orb2.py`: T1–T5. `research/lab/strategies/judas2.py`: J1–J5.
  `research/lab/strategies/literature.py`: N1–N4.
- `research/lab/catalog.py`: one `StrategyInfo` per variant (status `candidate`, origin = this spec, the
  sources), plus the dropped candidates as `rejected` rows with the reason.
- Tests in `research/tests/lab/`: DST-correct session windows (London 08:00 = 07:00 UTC in summer, 08:00 in
  winter; Tokyo fixed), each rule on small synthetic tick fixtures (ORB first-side and SL/exit, TMS candle-1/2
  window, Judas sweep → MSS → FVG → limit fill and the cancel paths, gotobi weekend roll, N3 sign), and a
  no-lookahead test (cutting the ticks after time τ leaves every decision before τ unchanged).
  `test_lab_catalog.py` already runs every catalog entry on a short slice.

## Run procedure

1. Implement with tests (TDD). `research/.venv/bin/python -m pytest research/tests` green.
2. Freeze: write `research/results/prereg_v2.md` = this pass bar + the rule text + the lab code hash, before
   any lab output of the new strategies exists.
3. Check run: real data, 2023–2024 only, into `research/results/lab/v2check`. Inspect trades per strategy ×
   symbol (none / implausibly many = bug) and 3 sample trades per family printed bar by bar against the rules.
   Only bugs are fixed; each fix is logged in `prereg_v2.md` with its reason.
4. Full run into a new dir `research/results/lab/v2` (never `main`): all 22 symbols, 2023–2026, variants real
   + mirror, 20 control seeds; then `--shuffle 20 --into research/results/lab/v2`.
5. Verdict: `research.lab.report` for the standard tables plus a small `research/lab/verdict.py` that applies
   the six pass conditions per variant on the holdout and writes `research/results/lab/v2/verdict.md`.
6. Record findings and statuses in `catalog.py`, re-render `research/STRATEGIES.md` from `main` + `v2`, report
   to the user in Vietnamese. No commit unless the user asks.

## Out of scope

cBot code, VPS backtests, the AI gate, production database, tuning after results, any strategy not listed.

## Limits of the test

- Swaps are the 2026 rates held constant; overnight holders (T4, T5) carry that error in 2023–25.
- The random-entry control draws random M15 closes at any hour, not matched to the session clock.
- Synthetic crosses are built from USD legs with the spread scaled × 1.26.
- Limit fills (J1–J4) are modelled at the first touching tick with no queue position; real fills at the
  exact edge are less certain, which flatters J1–J4 a little.
- Rules like "green goes flat / hooks" and discretionary S/R exits of TMS are not mechanised.
