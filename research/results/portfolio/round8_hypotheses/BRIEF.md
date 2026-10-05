# Round 8 brief: strategies built on how symbols affect each other (inter-market / cross-asset)

Written 2026-10-04 17:55 UTC, before any round-8 number was computed. The user asked (Vietnamese): "research thuật
toán, chiến thuật liên quan đến sự tác động của các symbol với nhau" = research algorithms/strategies based on how
the symbols influence each other. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading (research code in research/).

## Read first (to avoid re-testing; 2-3 min skim, not full reads)
- research/JOURNAL.md (all verdicts of rounds 1-7).
- research/results/portfolio/flow_search_2026-09-27.md, section "Cross-asset lead-lag" and "Risk premia" (U1).
- research/results/portfolio/swing_lab_v2_2026-09-27.md, table "What was tried" (pairs mean reversion row).
- research/results/portfolio/round7_new_data_2026-10-05.md, section B (index lead-lag) and "What this says".

Already tested and rejected inter-symbol ideas (do NOT redo them as they were; a genuinely different horizon,
conditioning or construction is fine, say how it differs):
- Daily 26x26 lead-lag on vol-scaled 20:00-UTC closes (max IS |t| 4.1, nothing repeats in VAL).
- US equities -> USD next day (U1; real, USDCHF -4.8 bp per equity sd, but engine R ~0).
- Oil -> USDCAD within the day (30 bp hourly oil move -> next 1-3 h: +0.2..0.5 bp).
- Pairs mean reversion of price LEVELS with <= 5-day hold (WTI/Brent, AUD/NZD, gold/silver, index pairs, BTC/ETH ...,
  14 pairs; half-lives 14 to > 2000 days).
- Cross-sectional D1 momentum (N=20) and cross-sectional FX reversal (2025-26 data only, lab removed).
- US30/USTEC -> US2000 and STOXX50 -> periphery lead-lag (CFDs follow futures; no lead).
- Synthetic vs real JPY crosses differ by < 0.1 bp (no triangular arbitrage at IC quotes).

## Data (shared, read-only; HOLD is NOT in it)
Panel at /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/f73ce3fb-dccf-45e1-b231-7588706e0e6c/scratchpad/r8/panel/
- meta.json: symbols (26, sorted), T0_ms = 2016-01-01 00:00 UTC, minutes N. Minute i starts at T0 + 60 s * i,
  every calendar minute (weekends = NaN).
- mid.npy float32 (26, N): (bid close + ask close)/2 of each M1 bar; NaN = no bar.
- spr.npy float32 (26, N): ask close - bid close in price units (raw ECN spread at the minute's last tick).
- n.npy uint16 (26, N): tick count.
- spread_table.txt: median spreads in bp by symbol and era.
Load with np.load(path, mmap_mode="r") and slice only the rows you need; never np.asarray all 26 rows at float64.
IC data period = 2016-01-01..2024-12-31 (BTC/ETH from 2018; DE40 2016-21 is the old DE30, continuous).
Extra era for FX/metals: Dukascopy 2004-2015 (bid only + IC 2016-17 spread profile convention), git-ignored in
research/data/duka/{h1 (AUDJPY AUDUSD EURJPY EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDCHF USDJPY XAUUSD; keys ts o h l c
ao ah al ac vb va), m1 (USDJPY EURJPY GBPJPY USDCHF EURUSD)}. Early Dukascopy ASK is junk: use bid returns only.
If you load anything from research/data/m1/*.npz directly, cut ts < 1735689600000 (2025-01-01) AT LOAD.
**HOLD (2025-01-01..2026-09) must stay closed.** Do not open it, print it, or plot it, in any stream.

## Eras
IS 2016-01..2021-12 (design, choose parameters), VAL 2022-01..2024-12 (check once per hypothesis family),
PRE 2004-2015 (Dukascopy; optional extra check for FX/metals ideas, H1 resolution for 11 symbols).

## Costs (executable, per round trip, per leg)
- Spread: the actual spr at the entry minute + at the exit minute, halved each (you cross half the spread each way
  from mid), i.e. cost_bp = (spr_in/2 + spr_out/2) / mid * 1e4. Use the spread of the minute you would actually trade
  at (spreads widen after shocks and around 21-22 UTC rollover; don't use medians for event trades).
- Commission 0.6 bp round trip for FX and metals (IC: $30 per $1M per side); 0 for indices, energies, crypto.
- Overnight: holds across 21:00 UTC pay swap. FX: research/swing/rates.py `swap_frac_at(symbol, side, ms)` (fraction
  of price per rollover); indices ~ -2 bp per night long, ~0 short; metals per research/swing/swing.py swap_frac.
  Intraday ideas that close before 20:55 UTC avoid this.
- Fills: decide on a bar close, fill at the next minute (no look-ahead: signal from data up to minute t, trade at
  t+1 or later). Add +1 minute latency variant for anything intraday.
- A two-leg (pairs) trade pays costs on both legs and counts as 2 positions.

## Constraints (user's, fixed)
Lot never depends on account capital (may scale 0.5-2x around a default by signal strength); each position held
<= 5 days; one bot holds <= 3 positions at once. Everything else is free (symbols, timeframe, entry/exit, engine).

## How to judge (same as rounds 3-7)
1. Write each hypothesis (mechanism + source + exact rule or event definition + horizon) into your stream's
   HYPOTHESES file in your stream folder BEFORE computing it. Add new ones as you go, always before their numbers.
2. Screen at MID first (pre-cost): mean bp per event/trade, t (clustered by day: sum R or bp within a UTC day, t
   over days), IS and VAL separately. Report the median executable cost next to it.
3. Executable net: mean net bp and net R if a stop is part of the rule (R = net move / stop distance).
4. Power rule (round 6): a candidate needs per-trade Sharpe >= ~3 / sqrt(expected HOLD trade count) (HOLD = 21
   months; e.g. daily ~0.16, weekly ~0.37). Report the per-trade Sharpe (net mean / net sd) and "power" =
   Sharpe * sqrt(expected HOLD n) for every family's best cell (bar ~3).
5. A candidate (worth a pre-registration) needs ALL of: mechanism written before the data; net > 0 in IS and in VAL
   separately; IS day-clustered t >= 2.5 and VAL t >= 1.5 (net); >= 2/3 of years net > 0; beats >= 95 % of a
   random-entry control (same count, side mix, hold, random times in the same session/weekday mix; >= 200 seeds);
   net > 0 at spread x1.5 and at +1 minute latency; power >= 3. Multiple testing: say how many cells you tried in
   that family and compare the best |t| with what chance gives (e.g. max of K normals).
6. If something meets the bar, STOP that family: write a pre-registration text (rule, parameters, symbols, bar,
   the cell count) into your stream folder and say so in your answer. Do NOT open HOLD; the lead decides.
7. Don't lower the bar. Negative results are results: report the numbers so the next round doesn't redo them.

## Resources (shared Mac: 10 cores, 17 GB RAM, other streams run at the same time)
- At most 2 heavy Python processes at a time per stream, each under ~3 GB RAM (mmap the panel, float32, slice rows).
- research/.venv/bin/python has numpy only (no pandas/scipy/statsmodels); write t-stats/OLS/PCA in numpy.
- Run from the repo root: cd /Users/hoangbk/00.code_base/105.AgentFxTrading && research/.venv/bin/python script.py
- Write scripts and outputs only under your stream folder in the scratchpad (r8/<stream>/). Do NOT edit any file in
  the repo (research/ code, JOURNAL, README, docs, tests). No git commands that change state. No network unless your
  stream says so (literature APIs only).
- Files named REPORT.md are blocked by the harness; name your write-up FINDINGS_<stream>.md.

## What to return (your final message, <= ~1,500 words)
- A table: hypothesis (mechanism, source) | where | IS mid / VAL mid (bp, t) | cost | net | power | verdict.
- The best cell per family with its numbers, the number of cells tried, and the chance benchmark.
- Any candidate's pre-registration path, or "none".
- Anything surprising (data problems, cost-model issues, effects that are real but too small).
- Paths of your scripts and findings file.
