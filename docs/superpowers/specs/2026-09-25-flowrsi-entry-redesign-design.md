# FlowRSI Entry Redesign — Design

**Date:** 2026-09-25
**Status:** Approved in chat section by section, awaiting spec review
**Follows:** `2026-09-25-flowrsi-pair-optimization-design.md` (phase 1 result: no parameter change makes
FlowRSI profitable; the user chose to redesign the entry signal instead of running phase 2)

## Goal

Find an entry signal for the 15 FlowRSI bots that has a real edge, by screening a fixed list of candidate
entries offline on tick data first, and only then coding the single winner into `FlowRsiBot.cs`.

## Why

Baseline #27–#41 (live presets, $2000, ticks, 01/01–24/09/2026): all 14 trading pairs negative, pooled
4037 positions mean −0.13R (t −7.3). 45 % of positions reach +1R before −1R, below a coin flip. Trend-aligned
entries lose more than counter-trend ones (AUDJPY −0.25R vs −0.03R). Macro off and a wider SL floor only
shrink the loss (−0.08R). XAUUSD takes 0 trades at $2000 (min-lot guard).

## Decisions taken in the brainstorm

| Question | Decision |
|---|---|
| Scope | Screen candidate entries on data first, then code one into the cBot |
| Exit model while screening | Both: fixed ATR SL/TP (X1) and the FlowRSI exit replica (X2) |
| Pass bar | Strict: pooled mean R > 0 with t ≥ 2 in each of 3 periods, positive on ≥ 60 % of pairs |
| Research code | `research/` in the repo, with small tests; committed only when the user asks |
| Approach | numpy on the Mac, cTrader only to confirm the winner |
| Account size | **Every pair is simulated and backtested at $2000**, like the live demo (~$1650) |

## 1. Data and simulator

### Layout

```
research/
  requirements.txt      numpy only (the app's requirements.txt is not touched)
  .venv/                git-ignored
  data/                 git-ignored; tick cache copied from the VPS
  ticks.py              decode .zticks, forward-fill
  bars.py               bid M15 / H1 / H4 bars from ticks, spread at bar close
  indicators.py         RSI, ATR (simple MA of TR, as the cBot), EMA, Bollinger, ADX, Donchian
  specs.py              per-pair lot size, min volume, volume step, pip size, commission, USD conversion
  sim.py                sizing + guardrails, exits X1 and X2, one position per pair
  signals.py            C0–C2 and E1–E5
  screen.py             runs configs × pairs × periods, writes a results table
  tests/                bars vs .zbars, SL/TP ordering, sizing guard, R accounting
```

`research/data/` and `research/.venv/` are added to `.gitignore`.

### Data

- Cache: `/var/lib/docker/volumes/agentfx-bt-cache/_data/V1/demo_e5322e87/<SYMBOL>/t1/YYYYMMDD.zticks`
  (gzip int64 triplets: ts ms UTC, bid×1e5, ask×1e5; 0 = unchanged, forward-fill). Root-owned: copy with
  `ssh forge@… 'sudo -n tar cf - -C <dir> t1' | tar xf -`, no remote shell glob.
- 2026 (01/01–24/09): all 15 pairs are cached.
- 2025: cached for AUDJPY, AUDUSD, EURJPY, EURUSD, GBPJPY, GBPUSD, USDJPY. The other 8 (BTCUSD, ETHUSD,
  DE40, UK100, US30, USTEC, USDCAD, XAUUSD) need one cTrader backtest each on 01/01–31/12/2025 at **$2000**
  with live presets (~40 min VPS). That fills the cache and gives their 2025 baseline. XAU will likely
  take 0 trades; its ticks are still downloaded in the loading phase.
- Ticks stay gzip-compressed on disk (34 GB free on the Mac); one pair is decoded at a time.

### Costs

- Spread: real bid/ask from ticks (buy at ask, sell at bid, SL/TP checked on the side that closes).
- Commission: per unit of volume per pair, derived from reports #27–#42 (commission ÷ volume). Indices and
  crypto show 0, forex and XAU do not.
- Swaps ignored (−0.02…−0.1R per pair over 9 months); noted as a caveat.

### Sizing and guardrails (as `CalculateDynamicVolumeInUnits`, FlowRsiBot.cs:1812)

- Start $2000 per pair, compounding like a single backtest; target risk = min(0.5 % × equity, $50).
- Units = target ÷ (SL pips × USD pip value per unit), normalized to the volume step, clamped to min volume.
- Refuse the entry if actual risk > `MaxRiskPerTradeMoney` ($50) or > 1.5 × target (`MaxMinLotRiskMultiple`).
- USD pip value: pip size × quote→USD rate from EURUSD / GBPUSD / USDJPY / USDCAD ticks at entry.
- Per-pair lot size, min volume, step and pip size are read from the volumes in reports #27–#42.

### Entry timing

Signals are computed on the closed M15 bid bar; the order fills at the first tick after the bar close,
matching `OnBarClosed`. One open position per pair (`MaxPositions=1`); a signal while a position is open is
dropped.

### Exits

- **X1 fixed:** `SlMode=ATR_Multiplier`, `AtrSlMultiplier=1.5`, SL distance = max(1.5·ATR14, `MinSlFloorPips`,
  1·ATR14), TP = 1.5 × SL distance; break-even, partial close and trailing off. Maps 1:1 to existing cBot
  parameters, so X1 needs no new exit code. If SL and TP fall inside the same tick, SL counts first.
- `MinSlFloorPips` stays at each pair's preset value under both exits (no tuning), **except XAUUSD: 500
  ($5) instead of 1500** in every screening config other than C0 (user's decision 2026-09-25). At $2000 the
  1 oz minimum still refuses any XAU entry whose SL is over $15 (1.5 × $10); in #42 the swing SL had a
  median of $20.9 and hit the floor only 3 % of the time, so XAU will mostly trade in quiet periods or
  with short-SL exits like X1. C0 keeps 1500 so the calibration replays job #93 as it ran.
- **X2 FlowRSI replica** (FlowRsiBot.cs:1860–2003), per tick: BE at 1R and ≥ `MinBreakEvenPips` to entry +
  `BreakEvenExtraPips`; partial close `PartialCloseRatio` at BE unless the remainder would fall below min
  volume; trailing armed at min(1.2R, 0.8 × TP R) with distance max(`TrailingStopDistancePips`, initial SL),
  × 0.6 from 2.5R, step 10 % of the distance; TP removed once trailing after a partial.

### Metric

R per position = net $ ÷ (0.5 % × equity at entry), as in the baseline analysis. Also reported: $ net,
positions, refused entries, trades per pair per month.

### Calibration gate (before any screening result is used)

Replay C0 (current signal, `EnableMacroTmsFilter=false`) with X2 on 2026 and compare to the cTrader
macro-off jobs #43–#56 (14 pairs, $2000) and #93 (XAUUSD, $10k, `MaxRiskPerTradeMoney=1000`). The
macro-on baseline #27–#41 is not used: replicating the ~300-line Macro TMS (FlowRsiBot.cs:948) would serve
no candidate, and every screening config runs with the macro filter off.
- ≥ 90 % of cTrader positions matched (same direction, entry within one bar) on every pair, and
- ≥ 95 % of matched positions with the same volume (checks the $2000 sizing and guardrails), and
- pooled mean R within ±0.03R of cTrader's.

If it fails, fix the simulator and rerun; no screening output is trusted until it passes.

## 2. Candidates and scoring

Parameters are fixed here, at most two variants per idea, no tuning after results are seen.

### Controls (never deployed)

- **C0** current FlowRSI signal with `EnableMacroTmsFilter=false` (calibration and reference).
- **C1** C0 with `EnableMacroTmsFilter=false` and SL floor 25 (forex) / 30 (JPY): phase-1 best.
- **C2** random entries: at each M15 close enter with the probability that matches C0's signal rate,
  random direction; 20 seeds. Gives the no-edge result with these costs and exits.

### Candidates

| | Idea | a | b |
|---|---|---|---|
| E1 | Reverse FlowRSI: trade against the C0 signal (macro off) | every signal | only crosses with slow RSI < 30 or > 70 |
| E2 | Trend pullback: trend = close above (below) EMA50 on the higher TF and EMA50 rising (falling); buy when M15 RSI14 closes back above 40 after closing below it (sell: back below 60) | trend on H1 | trend on H4 |
| E3 | RSI(2) mean reversion: buy M15 RSI2 < 10, sell > 90 | only with the H1 EMA50 trend | no trend filter |
| E4 | Bollinger fade: a close outside BB(20, 2), then the next close back inside → trade back toward the middle | only when ADX14 < 20 | no ADX filter |
| E5 | Donchian breakout with trend: M15 close beyond the N-bar high (low) with H4 EMA50 in the same direction | N = 20 | N = 48 |

10 candidates × 2 exits = 20 configs, plus the controls.

### Periods

P1 = 01/01–31/12/2025, P2 = 01/01–31/05/2026, P3 = 01/06–24/09/2026. All 15 pairs, $2000.

### Pass bar

A config passes only if all hold:
1. In each of P1, P2, P3: pooled mean R > 0 and t ≥ 2.
2. Pair mean R over P1–P3 combined > 0 on ≥ 9/15 pairs; a pair with no positions counts as not positive.
3. Pooled positions ÷ (15 pairs × months) ≥ 2.
4. Pooled mean R above C2's (mean over the 20 seeds) in every period.

With several passing, pick the one whose lowest t across P1–P3 is highest. For 20 configs, a no-edge config
passing t ≥ 2 in three independent periods by luck is ~20 × 0.023³ ≈ 0.02 %.

## 3. Confirmation and deployment

Only for the one winner:

1. **cBot:** add an `EntryMode` parameter to `FlowRsiBot.cs` (`Legacy` default + the winner) and the winner's
   own parameters with their screening values as defaults. Presets do not set `EntryMode`, so live bots keep
   the legacy entry even after a watchdog restart. Compile check on the VPS with ctrader-console in a temp
   dir (no dotnet on the Mac).
2. **No-regression check:** back up the old .algo, build the new one, rerun job #27's spec (AUDJPY, $2000,
   01/01–24/09/2026): must give the identical 269 positions and −615.05.
3. **Confirmation backtests:** 15 pairs × (2025, 01/01–24/09/2026) = 30 runs at $2000 with `EntryMode` and
   the winner's exit overrides (XAU also `MinSlFloorPips=500`; if XAU passes, its preset floor becomes 500). Must meet the same pass bar on the cTrader reports (2026 split into P2/P3),
   and the simulator must match ≥ 90 % of cTrader's entries.
4. **Deploy:** `app/cbot_presets.py` + `docs/docker-instances.md` + preset sync tests set `EntryMode` and the new
   parameters only on pairs whose cTrader mean R ≥ 0 in both 2025 and 2026; the other FlowRSI bots are
   stopped. Push a branch; the user opens the PR (main is protected). After merge on the VPS: pull, build
   .algo with a backup, restart `agentfx`, the user flattens FlowRSI positions, recreate the bots with
   `PUT /api/bots/{name}`. The AI gate stays behind the new signal live; backtests run without it.

### Stop rules

- No config passes screening → no cBot change. Report, with a recommendation to stop or keep the FlowRSI
  bots on demo; the user decides.
- Winner fails cTrader confirmation → no deploy. One round of simulator-vs-cTrader mismatch debugging, then stop.

## Git

Nothing is committed or pushed unless the user asks; only this work's files are staged (other sessions share
the checkout). This spec lives in git-ignored `docs/`.

## Caveats

- Backtests and the simulator run without the AI gate and the news filter.
- Swaps are ignored in the simulator.
- Min-lot positions can risk up to 1.5× the target, so their R is overstated; the same rule applies to all configs.
- ATR in the cBot is a simple MA of true range (FlowRsiBot.cs:532); the simulator must use the same.

## Calibration result (2026-09-25, research/calibrate.py)

Two changes to this spec, both decided by the user after the first gate run:
- **Swaps are modelled** (the "Swaps ignored" line above no longer holds): USD per unit per 17:00 New York
  rollover, per pair and side, triple on Wednesday (forex, XAU) or Friday (indices, crypto), least-squares
  fitted on reports #43–#56, #93 (`research/specs.py` SWAPS). Rates are constant, so 2025 swaps are approximate.
- **Volume gate** sizes each matched stop at cTrader's own balance. On the simulated equity path, a few
  extra or missing positions shift equity and one volume step then changes the exit path (partial or not).
  That path figure is reported for information.

| Job | Pair | cTrader pos | sim pos | matched | mean R cTrader | mean R sim |
|---|---|---|---|---|---|---|
| 43 | AUDJPY | 412 | 414 | 98.3 % | −0.106 | −0.119 |
| 44 | AUDUSD | 292 | 292 | 98.3 % | +0.059 | +0.058 |
| 45 | BTCUSD | 793 | 790 | 99.4 % | −0.088 | −0.080 |
| 46 | DE40 | 650 | 648 | 98.5 % | −0.003 | +0.004 |
| 47 | ETHUSD | 556 | 554 | 99.6 % | −0.224 | −0.224 |
| 48 | EURJPY | 394 | 389 | 96.7 % | −0.140 | −0.149 |
| 49 | EURUSD | 343 | 345 | 98.8 % | −0.118 | −0.105 |
| 50 | GBPJPY | 437 | 439 | 97.9 % | −0.148 | −0.147 |
| 51 | GBPUSD | 429 | 432 | 99.5 % | −0.086 | −0.083 |
| 52 | UK100 | 547 | 522 | 93.2 % | −0.017 | −0.022 |
| 53 | US30 | 616 | 618 | 96.1 % | −0.073 | −0.061 |
| 54 | USDCAD | 313 | 324 | 96.8 % | −0.133 | −0.178 |
| 55 | USDJPY | 370 | 370 | 99.7 % | −0.026 | −0.027 |
| 56 | USTEC | 708 | 705 | 95.3 % | −0.075 | −0.104 |
| 93 | XAUUSD ($10k) | 546 | 546 | 100.0 % | −0.040 | −0.041 |

Volume match at cTrader's balance 99.8 % (95.8 % on the simulated equity path); pooled mean R −0.081 cTrader
vs −0.085 sim (diff −0.003). **PASS.** Known gaps: USDCAD sim is 0.045R more pessimistic (its swap fit is the
loosest); 3 AUDJPY Sunday-open buys at 17:01 New York that cTrader did not take are unexplained.

## Screening result (2026-09-25, research/screen.py, 14.5 min)

**Verdict: no candidate passed.** Per the stop rules: no cBot change.

Every candidate is negative in every period. None beats the random-entry control C2 consistently. The current
signal C0 is at or slightly below random.

Controls behaved as expected:
- C0/X2 2026 ≈ cTrader's macro-off result (−0.100 / −0.070 vs −0.084).
- C1 is at or above C0.
- C2 is negative everywhere.

C2 measures the cost drag of an M15 entry with ~1–1.5 ATR stops: spread, commission and swap on a no-edge
entry. It runs from about −0.03R per trade (USTEC, US30, DE40, BTC, XAU) to −0.11…−0.16R (JPY crosses,
ETHUSD). Any entry on this timeframe has to beat that before it earns anything.

| Config | P1 mR (t) | P2 mR (t) | P3 mR (t) | +pairs | pos/pair/mo | Verdict |
|---|---|---|---|---|---|---|
| C2/X1 (seed mean) | -0.085 | -0.087 | -0.091 | | | control |
| C0/X1 | -0.084 (-8.1) | -0.104 (-6.2) | -0.066 (-3.3) | 0/15 | 78.39 | control |
| C1/X1 | -0.066 (-6.0) | -0.084 (-4.6) | -0.050 (-2.3) | 0/15 | 68.52 | control |
| E1a/X1 | -0.082 (-8.1) | -0.101 (-6.0) | -0.101 (-5.2) | 2/15 | 81.02 | fail |
| E1b/X1 | -0.056 (-1.3) | -0.021 (-0.3) | -0.029 (-0.4) | 4/15 | 4.84 | fail |
| E2a/X1 | -0.106 (-6.1) | -0.061 (-2.2) | -0.126 (-3.9) | 1/15 | 27.26 | fail |
| E2b/X1 | -0.115 (-8.0) | -0.122 (-5.3) | -0.115 (-4.3) | 0/15 | 41.13 | fail |
| E3a/X1 | -0.076 (-7.1) | -0.064 (-3.7) | -0.088 (-4.2) | 2/15 | 74.05 | fail |
| E3b/X1 | -0.075 (-9.3) | -0.078 (-5.8) | -0.076 (-4.8) | 0/15 | 127.14 | fail |
| E4a/X1 | -0.095 (-5.5) | -0.022 (-0.7) | -0.116 (-3.5) | 2/15 | 27.48 | fail |
| E4b/X1 | -0.083 (-8.3) | -0.084 (-5.1) | -0.053 (-2.7) | 3/15 | 82.51 | fail |
| E5a/X1 | -0.095 (-7.9) | -0.099 (-4.9) | -0.107 (-4.8) | 3/15 | 55.90 | fail |
| E5b/X1 | -0.077 (-5.4) | -0.088 (-3.7) | -0.069 (-2.5) | 3/15 | 40.23 | fail |
| C2/X2 (seed mean) | -0.064 | -0.067 | -0.057 | | | control |
| C0/X2 | -0.085 (-7.5) | -0.100 (-5.5) | -0.070 (-3.2) | 1/15 | 55.13 | control |
| C1/X2 | -0.071 (-6.2) | -0.083 (-4.3) | -0.056 (-2.4) | 1/15 | 52.11 | control |
| E1a/X2 | -0.053 (-3.3) | -0.084 (-3.2) | -0.058 (-1.9) | 2/15 | 28.72 | fail |
| E1b/X2 | +0.000 (+0.0) | -0.110 (-1.4) | -0.102 (-1.1) | 7/15 | 2.53 | fail |
| E2a/X2 | -0.115 (-7.1) | -0.043 (-1.6) | -0.095 (-3.1) | 1/15 | 25.51 | fail |
| E2b/X2 | -0.118 (-8.5) | -0.118 (-4.9) | -0.092 (-3.4) | 0/15 | 35.09 | fail |
| E3a/X2 | -0.077 (-7.2) | -0.078 (-4.5) | -0.093 (-4.6) | 1/15 | 62.10 | fail |
| E3b/X2 | -0.084 (-10.5) | -0.083 (-6.5) | -0.077 (-5.0) | 0/15 | 111.22 | fail |
| E4a/X2 | -0.102 (-6.2) | -0.048 (-1.7) | -0.111 (-3.5) | 2/15 | 25.76 | fail |
| E4b/X2 | -0.081 (-8.0) | -0.096 (-5.9) | -0.074 (-3.7) | 1/15 | 68.46 | fail |
| E5a/X2 | -0.076 (-3.7) | -0.074 (-2.2) | -0.074 (-1.9) | 4/15 | 16.58 | fail |
| E5b/X2 | -0.065 (-2.7) | -0.114 (-2.9) | -0.015 (-0.3) | 4/15 | 11.85 | fail |

