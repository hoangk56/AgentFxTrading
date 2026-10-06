# Round 10 brief: new directions after nine rounds

Written 2026-10-05 17:50 UTC, before any round-10 stream number was computed. The user asked (Vietnamese) for more
research into trading algorithms on the data already in `research/data/`, until a candidate reaches the "live" bar
below; a negative round is not a stopping point, the search must widen. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

## Read first (skim, to avoid re-testing)
- research/JOURNAL.md (verdicts of rounds 1-9) and research/README.md.
- research/results/portfolio/flow_search_2026-09-27.md and flow_search_round4_2026-09-27.md (round 3-4 tables; the
  round-4 minute-precise benchmark scan used 19 times: Tokyo 09:55, CNY 09:15, ECB 14:15, WM/R 16:00, LBMA, NYMEX
  14:30, FX option cuts, cash opens/closes of NY, Xetra, LSE, ASX, HKEX).
- research/results/portfolio/round6_commodity_flows_2026-10-04.md (power table; metals commission is overstated
  before 2025 in the engine: use $30 per $1M per side = 0.6 bp round trip for FX and metals).
- research/results/portfolio/round7_new_data_2026-10-05.md (Dukascopy era, new symbols, literature screen).
- research/results/portfolio/round8_inter_symbol_2026-10-05.md (lead-lag, spillover, relative value; "Pitfalls").
- research/results/portfolio/round9_capital_100k_2026-10-05.md (macro fair value, COT, carry, options).

The standing diagnosis (rounds 3-9): flows other than gotobi are 0.02-3 bp, about IC's round-trip cost; multi-week
premia lose to IC's financing markup; cross-symbol information is priced within the first minute; rare effects (a few
dozen a year) lack power in a 21-month holdout. **Every hypothesis you test must say, in its HYPOTHESES entry, why it
could escape these limits.** Already-rejected ideas are not to be redone unless the construction is genuinely
different (say how).

Round 10 lead's own probe (do not redo): sub-minute lead-lag on IC ticks, 1-second grid, 2019, 1-5 s delay:
USTEC -> AUDUSD +0.1..+0.4 bp after |z| >= 8 leader moves against ~0.9 bp cost; USTEC -> US30 +0.1..+0.4 bp against
~1.2 bp spread. Rejected.

## Data (read-only; HOLD is NOT in the shared panel)
- Panel (round 8's, copied): /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/64fd0f45-a961-42f5-8d1b-dc313a11911f/scratchpad/r10/panel/
  meta.json (26 symbols sorted, T0_ms = 2016-01-01, every calendar minute to 2024-12-31), mid.npy float32 (26, N)
  = (bid close + ask close)/2, spr.npy float32 (26, N) = ask close - bid close at the minute's last tick (price
  units), n.npy uint16 tick count; NaN = no bar. spread_table.txt has median spreads by era. Load with
  np.load(..., mmap_mode="r") and slice the rows you need; never materialise all 26 rows in float64.
- Full M1 caches research/data/m1/<SYM>.npz (ts ms, o h l c = bid, ca = ask close, n): if you load them, cut
  ts < 1735689600000 (2025-01-01) AT LOAD. IC new symbols ES35, F40, IT40, STOXX50, US2000, USDCNH: M1 bid bars only
  (see round 7, section B, for where and their published spreads).
- IC ticks (ms, bid/ask) 2016-2026 for AUDUSD NZDUSD US30 USTEC XAUUSD XAGUSD XPTUSD (and XTI/XBR/XNG from 2018):
  research/ticks.py `load_ticks(symbol, start_date, end_date)`; only load days < 2025-01-01.
- Dukascopy 2004-2015 (era PRE): research/data/duka/m1 (USDJPY EURJPY GBPJPY USDCHF EURUSD, bid usable, early ask is
  junk) and research/data/duka/h1 (AUDJPY AUDUSD EURJPY EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDCHF USDJPY XAUUSD).
  PRE has been used for C3, M1, some FX screens (round 7-8) and as round 9's design era; it is clean for a new
  hypothesis that no round screened there. Cost convention for PRE: IC 2016-17 spread by minute of day + 0.6 bp.
- FRED rates already downloaded: research/data/rates/*.csv. Calendars: a scratch venv with the `holidays` package
  (and numpy) is at .../scratchpad/r10/venv_extra/bin/python (e.g. holidays.China, holidays.financial_holidays("NYSE"),
  holidays.UK, holidays.Japan); write the dates you need to a JSON in your folder and read it from the main venv.
- C3's trade list (for the correlation of any survivor with C3): research/results/portfolio/trades_C3_gotobi_jpy_basket.csv
  (columns t_out_utc, usd_at_100_risk, era ...). Report the daily (and monthly) P&L correlation of any surviving
  candidate with C3 on IS+VAL only.
- Network: allowed for calendars, official publication schedules and literature APIs (OpenAlex, Semantic Scholar,
  arXiv, central-bank and exchange websites). FRED and Yahoo were unreachable in round 9. Never fetch prices for
  2025-2026.

**HOLD (2025-01-01..2026-09) must stay closed.** Do not load, print or plot it, in any stream.

## Eras
IS 2016-01..2021-12 (design: choose parameters here), VAL 2022-01..2024-12 (check), PRE 2004-2015 optional extra
check where data exists. Energies start 2018 (IS = 2018-21). The side of every trade is fixed before you look at the
data (from the mechanism or the literature), not chosen from IS.

## Costs (executable, per leg, per round trip)
- Spread: half the actual spread at the entry minute + half at the exit minute, from the panel/M1 (not medians);
  for the bid-only new symbols use round 7's published spreads.
- Commission 0.6 bp round trip for FX and metals ($30 per $1M per side); 0 for indices, energies, crypto.
- Holds across the 21:00/22:00 UTC rollover pay swap (FX: research/swing/rates.py swap_frac_at; indices about
  -2 bp per night long; energies -2.5 bp, XNG -4 bp per night). Intraday ideas closing before ~20:55 UTC avoid it.
- Fills: signal on data up to minute t, fill at t+1 or later. Always also run +1 minute latency and spread x1.5.

## Constraints (user's, fixed)
Lot never depends on account capital (may scale 0.5-2x around a default by signal strength); each position held
<= 5 days; one bot holds <= 3 positions at once. Everything else is free (symbols, timeframe, entry/exit, engine,
symbols per bot).

## Bars (the user's; do not lower them)
Common: an economic basis (flows, settlement, risk premium...), not a chart pattern; parameters chosen on IS,
checked on VAL; the side fixed before looking; net > 0 in IS and VAL; still > 0 at spread x1.5 and +1 minute; t
clustered by UTC day.
- **LIVE**: IS day-clustered t >= 2.5, VAL >= 1.5; >= 2/3 of years net > 0; beats >= 95 % of a random-entry
  control (same count, side mix, hold, random times in the same session/weekday mix, >= 200 seeds); and power =
  per-trade net Sharpe x sqrt(expected HOLD trade count) >= 3 (HOLD = 1.73 years). Also report the power on
  day-clustered units (per-day Sharpe x sqrt(HOLD days)): C3 itself has a per-leg power of 2.9 but day-clustered
  t only 3.5 IS / 2.3 VAL / 1.9 HOLD.
- **DEMO** (real but too rare for the holdout, e.g. a few dozen events a year): IS day-clustered t >= 2.0, net > 0
  in VAL, beats >= 90 % of random entries; no power requirement.
- Multiple testing: report how many cells each family tried and compare the best |t| with what chance gives (max of
  K normals, or a permutation null that flips signs per day, shared by all symbols).

## How to work
1. Write each hypothesis (mechanism, source, why it may escape the standing limits, exact rule, side, horizon) into
   your stream's HYPOTHESES_<stream>.md in the round folder BEFORE computing it, with the UTC time. Add new ones as
   you go, always before their numbers; mark additions made after seeing data as post hoc.
2. Screen at mid first (bp per event, day-clustered t, IS and VAL separately, cost next to it), then executable net.
3. Per family: best cell, cells tried, chance benchmark, per-trade Sharpe and power.
4. If a family meets the LIVE or DEMO bar on IS/VAL, STOP that family and write a pre-registration draft (exact rule,
   parameters, symbols, bar, cell count, expected HOLD trades, for DEMO also expected demo trades per year) as
   PREREG_DRAFT_<stream>_<name>.md in the round folder. Do NOT open HOLD; the lead registers and runs it.
5. Negative results are results: report the numbers so the next round doesn't redo them.
6. Pitfalls from round 8: spiky CFD quotes break day-clustered t (winsorise or use a permutation null); IC glitches
   (UK100 2017-04-17, ETH 2019-05-01, BTC/ETH 2017-12-22, XTI/XBR April 2020); never filter multi-leg trades on
   quotes at exit; fill missing quotes at the first/last available quote instead of dropping weeks; XBR opens an
   hour after XTI on Sunday; HK50 has a lunch gap.

## Resources (shared Mac: 10 cores, 16 GB RAM, three streams at once)
- At most 2 heavy Python processes at a time per stream, each under ~3 GB RAM.
- research/.venv/bin/python has numpy only (no pandas/scipy); write t-stats/OLS in numpy.
- Run from the repo root with PYTHONPATH=. (e.g. `cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=. research/.venv/bin/python <script>`).
- Scripts and outputs only under your stream folder in the scratchpad (.../scratchpad/r10/<stream>/). In the repo,
  write ONLY your HYPOTHESES_<stream>.md and PREREG_DRAFT_* files in research/results/portfolio/round10_new_directions/.
  Do not edit any other repo file; no git commands that change state.
- Files named REPORT.md or FINDINGS.md may be blocked: name your write-up STREAM_<stream>.md (scratchpad folder).

## What to return (final message, <= ~1,500 words)
- A table: hypothesis (mechanism, source) | where | IS mid / VAL mid (bp, t) | cost | net IS / VAL | power | verdict.
- Best cell per family, cells tried, chance benchmark; any PREREG_DRAFT path, or "none".
- Anything surprising (data problems, cost-model issues, effects real but too small).
- Paths of your scripts and STREAM file.

## Round 11 addendum (2026-10-06, written before any round-11 number)
The user asked to keep going until a LIVE candidate is found. Round 10 found nothing (report:
research/results/portfolio/round10_new_directions_2026-10-06.md — read its "Answer", "feasibility frontier", "What
this says" and "Pitfalls" first). Round-11 streams F, G, H use this same brief, write HYPOTHESES_<F|G|H>.md and
PREREG_DRAFT_* in research/results/portfolio/round10_new_directions/, and keep scripts in .../scratchpad/r10/<F|G|H>/.
Reusable inputs from round 10 (scratchpad/r10/): B/calendar/cb_calendar.json (1,877 central-bank events 2004-24 with
UTC times and sources), E/cal/releases.json (16 non-US macro release types 2016-24, ~130/yr), B/calendar/holidays.json.
Holiday-type tests must cluster by holiday block and use other countries' holidays as placebo (round-10 pitfall).
