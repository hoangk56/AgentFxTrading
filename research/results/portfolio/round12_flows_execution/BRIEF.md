# Round 12 brief: hedge-rebalancing flows, other executions and conditions for sub-cost effects, literature 2018-2026

Written 2026-10-06 00:52 UTC (file time; an earlier header gave a later, estimated time), before any round-12 number was computed. The user asked (Vietnamese, `research/PROMPT.md`)
to keep researching trading algorithms on the data already in `research/data/` until a candidate reaches the LIVE bar
below. A negative round is not a stopping point. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

## Read first (skim, to avoid re-testing)
- research/JOURNAL.md (verdicts of rounds 1-11) and research/README.md.
- research/results/portfolio/round10_new_directions_2026-10-06.md: "Answer", "The feasibility frontier", "What this
  says", "Pitfalls". Its brief (round10_new_directions/BRIEF.md) has the data/cost conventions this brief reuses.
- research/results/portfolio/round11_multiday_cross_section_index_scan_2026-10-06.md.
- For your stream's topic, the earlier tables: flow_search_2026-09-27.md (round 3), flow_search_round4_2026-09-27.md,
  round6_commodity_flows_2026-10-04.md (power table, passive execution S4), round7_new_data_2026-10-05.md,
  round8_inter_symbol_2026-10-05.md, round9_capital_100k_2026-10-05.md, round10_new_directions/STREAM_*.md.

Standing diagnosis (rounds 3-11): flows other than gotobi are 0.02-3 bp, about IC's round-trip cost; multi-week
premia lose to IC's financing markup; cross-symbol information is priced within the first minute; rare effects (a
few dozen a year) lack power in the 21-month holdout; at 1-5 days there is no signal (round 11). **Every hypothesis
must say, in its HYPOTHESES entry, why it could escape these limits, and how it differs from the tested version.**

### The arithmetic every hypothesis must face (round 10, stream D)
LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3, HOLD = 1.73 years: Sharpe >= 0.144 at 250 trades a year,
0.32 at 50, 0.072 at 1,000 (only if trades are independent; cluster by day). Gross edge needed for one trade a day
(cost + Sharpe x sd), bp: EURUSD 15 min 1.4, 1 h 2.1, 1 d 6.8; USDJPY 1.4 / 2.2 / 8.0; US30 2.6 / 4.3 / 14.6; XAUUSD
2.7 / 4.2 / 13.5; full table in round10_new_directions/STREAM_D_outputs.md. A LIVE effect held constant would show
IS (6 years) net t of about 3 x sqrt(6 / 1.73) = 5.6, so it must be something no earlier scan conditioned on.

### Real effects found so far that are smaller than their cost (mid, IS / VAL)
- SGE gold morning auction, long XAU 02:15-02:23 UTC: +0.93 bp (t 7.9) / +0.72 (t 4.5); cost 1.6 / 1.05; +0.65 bp
  larger on active mornings; does not revert within an hour (round 10 A, E).
- Sydney-open V, AUD/NZD around 10:00 Sydney: NZDUSD -1.7 bp in the 15 min before (t -13 IS / -9 VAL); short
  09:45-10:00 on volatile days +2.52 (t 5.9) / +2.12 (t 7.2) against a 2.0-2.3 bp cost (rounds 4, 10 E); a passive
  limit-buy version filled 85-93 % of days and 0/48 cells were net > 0 (round 6 S4).
- EUR rises into the ECB 14:15 CET fix: -0.73 bp on the USD side (t -5.3 / -4.1) against ~0.65-0.8 bp (round 10 E).
- Gold/silver momentum into the COMEX settlement (leveraged-ETF rebalancing): gold slope t +6.8 / +2.6; big days
  +2.31 bp against 1.30 (sd 11.8) IS, +1.00 against 0.96 VAL (round 6 S1; engine metals commission overstated, the
  true one is 0.6 bp).
- FX residual / currency-strength reversal +1.2..+2.7 bp against 1.2-1.5 bp (round 8); dollar catch-up, adaptive
  periodicity (round 10 C, round 7 C).
- AUS200: fade the 16:00-16:12 Sydney move over 16:13-16:30 +0.82 (t 2.17) / +0.71 (t 2.71) against 2.18 / 1.58;
  USTEC: follow the MOC imbalance window 15:50-16:00 ET +1.53 (t 2.71) / +1.00 (t 1.54) against 1.67 / 0.65 (round 11 H2).
- USDCNH Asian-hours drift +1.17 / +2.03 bp against ~1 bp (round 7 B).
- Crypto intraday momentum (day return -> last 30 min before 00:00 UTC): BTC +8.8 bp (t 4.1) / +2.6 (t 1.9) against
  3.5-17 bp in the IS years and ~1.8 bp now (round 3).

## Data (read-only; HOLD is NOT in the shared panel)
- Panel (copy of round 8/10's): /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r12/shared/panel/
  meta.json (26 symbols, T0_ms = 2016-01-01, every calendar minute to 2024-12-31), mid.npy float32 (26, N) = (bid
  close + ask close) / 2, spr.npy float32 (26, N) = ask close - bid close at the minute's last tick (price units),
  n.npy uint16 tick count; NaN = no bar. spread_table.txt has median spreads by era. Load with np.load(...,
  mmap_mode="r") and slice the rows you need; never materialise all 26 rows in float64.
- Full M1 caches research/data/m1/<SYM>.npz (ts ms, o h l c = bid, ca = ask close, n): if you load them, cut
  ts < 1735689600000 (2025-01-01) AT LOAD. IC new symbols ES35, F40, IT40, STOXX50, US2000, USDCNH: M1 bid bars only
  (round 7, section B, has their published spreads).
- IC ticks (ms, bid/ask) 2016-2026 for AUDUSD NZDUSD US30 USTEC XAUUSD XAGUSD XPTUSD (and XTI/XBR/XNG from 2018):
  `research/ticks.py` `load_ticks(symbol, start_date, end_date)`; only load days < 2025-01-01.
- Dukascopy 2004-2015 (era PRE): research/data/duka/m1 (USDJPY EURJPY GBPJPY USDCHF EURUSD; bid usable, early ask is
  junk) and research/data/duka/h1 (AUDJPY AUDUSD EURJPY EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDCHF USDJPY XAUUSD).
  No index or commodity data before 2016 except XAU H1. Cost convention for PRE: IC 2016-17 spread by minute of day
  + 0.6 bp.
- Calendars (reusable, in .../scratchpad/r12/shared/cal/): cb_calendar.json (1,877 central-bank decisions 2004-24
  with UTC times and sources), releases.json (16 non-US macro release types 2016-24), holidays.json, sources.txt. A
  scratch venv with the `holidays` package: .../scratchpad/r12/shared/venv_extra/bin/python (write the dates you
  need to a JSON in your folder and read it from the main venv).
- FRED rates already downloaded: research/data/rates/*.csv (policy / short rates only).
- C3's trade list: research/results/portfolio/trades_C3_gotobi_jpy_basket.csv (columns symbol, side, era, t_in_utc,
  t_out_utc, ..., usd_at_100_risk). Report the daily and monthly P&L correlation of any surviving candidate with C3
  on IS + VAL only.
- Network: allowed for calendars, official publication schedules and literature APIs (OpenAlex, Semantic Scholar,
  arXiv, central-bank and exchange websites). FRED and Yahoo were unreachable in round 9. Never fetch prices for
  2025-2026; fetching any new price series (other symbols, other venues) is a user decision: write it down as a
  direction that needs the user, do not do it. (Probe already done: DTCC's public FX-option trade reports are
  downloadable only from 2024-12; earlier files are in S3 Deep Archive. Do not use them.)

**HOLD (2025-01-01..2026-09) must stay closed.** Do not load, print or plot it, in any stream.

## Eras
IS 2016-01..2021-12 (design: choose parameters here), VAL 2022-01..2024-12 (check), PRE 2004-2015 optional extra
check where data exists. Energies start 2018 (IS = 2018-21). The side of every trade is fixed before you look at the
data (from the mechanism or the literature), not chosen from IS.

## Costs (executable, per leg, per round trip)
- Spread: half the actual spread at the entry minute + half at the exit minute, from the panel/M1 (not medians); for
  the bid-only new symbols use round 7's published spreads. At tick level: buy at the ask, sell at the bid.
- Commission 0.6 bp round trip for FX and metals ($30 per $1M per side; the engine's metals commission is overstated
  before 2025, do not use it); 0 for indices, energies, crypto.
- Holds across the 21:00/22:00 UTC rollover pay swap (FX: research/swing/rates.py swap_frac_at; indices about -2 bp
  per night long; energies -2.5 bp, XNG -4 bp per night). Intraday ideas closing before ~20:55 UTC avoid it.
- Fills: signal on data up to minute t, fill at t+1 or later. Always also run +1 minute latency and spread x1.5.
- Passive (limit) fills, if you model them: a buy limit fills only when the ask trades through the limit price (a
  touch is not enough unless you justify it), a sell limit when the bid trades through; no fill = no trade, and the
  unfilled days count in the random-entry control.

## Constraints (user's, fixed)
Lot never depends on account capital (may scale 0.5-2x around a default by signal strength); each position held
<= 5 days; one bot holds <= 3 positions at once. Everything else is free (symbols, timeframe, entry/exit, engine,
symbols per bot, several bots per algorithm).

## Bars (the user's; do not lower them)
Common: an economic basis (flows, settlement, risk premium...), not a chart pattern; parameters chosen on IS, checked
on VAL; the side fixed before looking; net > 0 in IS and VAL at the era's own costs; still > 0 at spread x1.5 and
+1 minute; t clustered by UTC day (by event block for holidays).
- **LIVE**: IS day-clustered t >= 2.5, VAL >= 1.5; >= 2/3 of years net > 0; beats >= 95 % of a random-entry control
  (same count, side mix, hold, random times in the same session/weekday mix, >= 200 seeds); and power = per-trade
  net Sharpe x sqrt(expected HOLD trade count) >= 3. Also report power on day-clustered units.
- **DEMO** (real but too rare for the holdout, e.g. a few dozen events a year): IS day-clustered t >= 2.0, net > 0
  in VAL, beats >= 90 % of random entries; no power requirement.
- Multiple testing: report how many cells each family tried and compare the best |t| with what chance gives (max of
  K normals, or a permutation null that flips signs per day, shared by all symbols).

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| I | month-end (and quarter-end) hedge-rebalancing flows at the WM/R 16:00 London fix, with the USD side predicted from month-to-date equity returns (Melvin & Prins 2015) | round 3 tested the month-end fix unconditionally (F1 reversal, M1 USD demand) and U1 daily; a flow whose direction and size are predictable from public data is what made gotobi work; month-end is the largest hedge-rebalancing date |
| J | other executions of the real-but-sub-cost effects listed above: entry/exit minute inside the flow window chosen for spread, passive limit entries where the move that fills you is the known uninformed flow, holding one trade through several same-sign flows, lot 0.5-2x by the conditional forecast | the user asked for this explicitly; cost, not the mid edge, is what kills these effects |
| K | literature 2018-2026: intraday / short-horizon flow and premium anomalies in FX, index futures, commodities, crypto not yet tested in rounds 3-11; screen the untested ones with the papers' sides | rounds 7 C and 8 X covered 2010-2026 broadly; this pass targets dealer/hedger inventory, benchmark/auction design, settlement, and post-2020 market structure (0DTE, leveraged ETFs, crypto at today's costs) |
| L | conditions that scale the strong-but-sub-cost flows by >= 3x (state variables chosen from each mechanism before looking: day type, prior moves, activity, events, holidays in the other venue, month-end, option expiry...) | the effects are real at t 4-13; round 10 E found 1.5x from volatility alone; a flow-size proxy closer to each mechanism could find the days where the flow clears the cost |

## How to work
1. Write each hypothesis (mechanism, source, why it may escape the standing limits, exact rule, side, horizon, cell
   count) into HYPOTHESES_<stream>.md in research/results/portfolio/round12_flows_execution/ BEFORE computing it, with
   the UTC time. Add new ones as you go, always before their numbers; mark additions made after seeing data as post hoc.
2. Screen at mid first (bp per event, day-clustered t, IS and VAL separately, cost next to it), then executable net.
3. Per family: best cell, cells tried, chance benchmark, per-trade Sharpe and power.
4. If a family meets the LIVE or DEMO bar on IS/VAL, STOP that family and write a pre-registration draft (exact rule,
   parameters, symbols, bar, cell count, expected HOLD trades, for DEMO also expected demo trades per year, a stop
   rule and the promotion rule "HOLD + demo pooled t >= 2.5") as PREREG_DRAFT_<stream>_<name>.md in the round folder.
   Do NOT open HOLD; the lead registers and runs it.
5. Negative results are results: report the numbers so the next round doesn't redo them.
6. Pitfalls (rounds 8-11): spiky CFD quotes break day-clustered t (winsorise or use a permutation null); IC glitches
   (UK100 2017-04-17, ETH 2019-05-01, BTC/ETH 2017-12-22, XTI/XBR April 2020); never filter multi-leg trades on quotes
   at exit; fill missing quotes at the first/last available quote instead of dropping weeks; XBR opens an hour after
   XTI on Sunday; HK50 has a lunch gap; holiday tests cluster by holiday block and use other countries' holidays as a
   placebo; rerun a conditional side at every shift of a time placebo; a cost gate beats random entries by
   construction; causal vol terciles drift with the regime (36 % of VAL days in the top IS tercile); check which clock
   time a "close" means; oil quotes on Good Friday are IC artefacts.

## Resources (shared Mac: 10 cores, 16 GB RAM, four streams at once)
- At most 2 heavy Python processes at a time per stream, each under ~2.5 GB RAM.
- research/.venv/bin/python has numpy only (no pandas/scipy); write t-stats/OLS in numpy.
- Run from the repo root with PYTHONPATH=. (e.g. `cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=. research/.venv/bin/python <script>`).
- Scripts and outputs only under your stream folder in the scratchpad
  (/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r12/<stream>/).
  In the repo, write ONLY your HYPOTHESES_<stream>.md, STREAM_<stream>.md and PREREG_DRAFT_* files in
  research/results/portfolio/round12_flows_execution/. Do not edit any other repo file; no git commands that change state.
- Files named REPORT.md or FINDINGS.md may be blocked: name your write-up STREAM_<stream>.md.

## What to return (final message, <= ~1,500 words)
- A table: hypothesis (mechanism, source) | where | IS mid / VAL mid (bp, t) | cost | net IS / VAL | power | verdict.
- Best cell per family, cells tried, chance benchmark; any PREREG_DRAFT path, or "none".
- Anything surprising (data problems, cost-model issues, effects real but too small).
- Directions that would need the user's decision (new data, symbols, VPS), with what they would test.
- Paths of your scripts and STREAM file.
