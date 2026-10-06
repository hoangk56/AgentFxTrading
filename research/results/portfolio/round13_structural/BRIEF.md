# Round 13 brief: structural (non-decaying) flows, structural calendars, the big-day flow mechanism elsewhere

Written 2026-10-06 01:24 UTC (file time; an earlier header gave a later, estimated time), before any round-13 number was computed. The user asked (Vietnamese, `research/PROMPT.md`)
to keep researching until a candidate reaches the LIVE bar; a negative round is not a stopping point. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading.

## Read first
- research/JOURNAL.md (rounds 1-12) and research/README.md.
- research/results/portfolio/round12_flows_execution_2026-10-06.md ("Answer", "What this says", "Pitfalls") and its
  folder (BRIEF.md has the arithmetic every hypothesis must face and the list of real-but-sub-cost effects;
  STREAM_J.md has break-even costs; STREAM_L.md the gold settlement big-day rule).
- round10_new_directions_2026-10-06.md (frontier, pitfalls), round11 report, and for your topic the earlier tables
  (flow_search_2026-09-27.md, flow_search_round4_2026-09-27.md, round6_commodity_flows_2026-10-04.md,
  round7_new_data_2026-10-05.md, round8_inter_symbol_2026-10-05.md, round9_capital_100k_2026-10-05.md).

## The lesson of round 12 that shapes this round
Every flow anomaly that cleared IS/VAL in twelve rounds, except gotobi, was weaker in VAL than in IS and weaker
again in HOLD 2025-26 (month-end WM/R +6.8 -> +1.7 -> -0.2 bp; Sydney dip mid +1.54 -> +1.53 -> +0.48; gold settlement
big days +3.5 -> +2.1 -> +1.7). Gotobi held over 2004-2026 because it comes from a fixed institutional practice
(Japanese corporate settlement on 5/10 days at the bank's TTM fix). This round looks for effects with the same
property. **Report for every cell the effect size by era (PRE 2004-15 where data exists, IS, VAL) and by year, and
the ratio VAL / IS; treat a cell whose VAL effect is well below IS as decaying, and say so.** Before any
pre-registration, compute the expected HOLD t on the VAL effect size, not the IS one.

The arithmetic (unchanged): LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3 (Sharpe 0.144 at 250 trades a
year, 0.32 at 50); full frontier table in round10_new_directions/STREAM_D_outputs.md. HOLD 2025-01..2026-09 was
opened three more times in round 12; new data after 2026-09-24 needs the user.

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
| M | stability-first scan: FX and gold calendar/clock cells (weekday x time of day x day-of-month type, local exchange and fixing clocks, DST-aware) that have the same sign and similar size in PRE 2004-15 (Dukascopy M1: USDJPY EURJPY GBPJPY USDCHF EURUSD; H1: 11 symbols incl. XAU), IS and VAL; discovery on PRE, parameters on IS, check on VAL. Exclude anything overlapping the Tokyo fix (00:00-01:00 UTC +- 1 h) on JPY pairs, which is C3's | earlier scans (90k, 48k, 16k cells) were on IS/VAL only; an effect stable over 21 years is structural like gotobi and is less likely to decay in HOLD; PRE gives 12 more years of power to see small stable effects, which then must clear cost |
| N | structural calendar flows: tax and fiscal deadlines (US corporate tax dates 15 Apr/Jun/Sep/Dec, Australian FY end 30 Jun, UK tax year, Japanese fiscal half-years if not gotobi/fix), US Treasury coupon and bill settlement days (mid-month and month-end; large settlements drain USD), bond-index month-end extension days, quarter-end bank balance-sheet window dressing, pooled across countries for count | these come from law, settlement systems and index rules that do not change when someone trades them; rounds 3-4 tested auction days, month-end and turn of month, not settlement or tax dates |
| P | the round-12 L4 mechanism elsewhere: flows proportional to the day's move executed at a settlement or close (leveraged and inverse ETFs, settlement-benchmarked orders), gated on the top decile of the day's move z: XTI/XBR at the NYMEX/ICE settlement, US30/US500/USTEC/US2000 into the 16:00 ET close, JP225 into the Tokyo close (Nikkei leveraged ETFs are very large), DE40 into the Xetra close, UK100, HK50, AUS200 | round 6 and round 3 tested these flows on all days or |z| > 1-2, where they were small; L4 found a 7-12x scale-up in gold in the top decile; a dose-response test is new for these symbols; the rebalancing rule of leveraged ETFs is fixed by their prospectus |

## How to work
1. Write each hypothesis (mechanism, source, why it may escape the limits incl. decay, exact rule, side, horizon,
   cell count) into HYPOTHESES_<stream>.md in research/results/portfolio/round13_structural/ BEFORE computing it, with
   the UTC time (check `date -u`). Add new ones as you go, always before their numbers; mark post-hoc additions.
2. Screen at mid first (bp per event, day-clustered t, by era and year, cost next to it), then executable net.
3. Per family: best cell, cells tried, chance benchmark, per-trade Sharpe and power (on the VAL size too).
4. If a family meets the LIVE or DEMO bar on IS/VAL, STOP that family and write PREREG_DRAFT_<stream>_<name>.md in
   the round folder (exact rule, parameters, symbols, bar, cell count, expected HOLD trades and expected HOLD t on the
   VAL size, for DEMO also expected demo trades per year, a stop rule and the promotion rule "HOLD + demo pooled
   t >= 2.5"). Do NOT open HOLD; the lead registers and runs it.
5. Negative results are results: report the numbers so the next round doesn't redo them.
6. Pitfalls (rounds 8-12): spiky CFD quotes break day-clustered t (winsorise or use a permutation null); IC glitches
   (UK100 2017-04-17, ETH 2019-05-01, BTC/ETH 2017-12-22, XTI/XBR April 2020); never filter multi-leg trades on quotes
   at exit; fill missing quotes at the first/last available quote; XBR opens an hour after XTI on Sunday; HK50 has a
   lunch gap; holiday tests cluster by holiday block with other countries' holidays as placebo; rerun a conditional
   side at every shift of a time placebo; random-entry controls for data-dependent sides must recompute the side at
   the random time or sample after the signal; a cost gate beats random entries by construction; IC's wide-spread
   hour after the 17:00 New York rollover moves against Asian clocks with DST (split by New York time); bar-start vs
   bar-end minute labels; check momentum-into-a-benchmark rules with both fills one minute late; oil quotes on Good
   Friday are IC artefacts.

## Resources (shared Mac: 10 cores, 16 GB RAM, three streams at once)
- At most 2 heavy Python processes at a time per stream, each under ~3 GB RAM.
- research/.venv/bin/python has numpy only (no pandas/scipy); write t-stats/OLS in numpy.
- Run from the repo root with PYTHONPATH=. (e.g. `cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=. research/.venv/bin/python <script>`).
- Scripts and outputs only under your stream folder in the scratchpad
  (/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r13/<stream>/).
  In the repo, write ONLY your HYPOTHESES_<stream>.md, STREAM_<stream>.md and PREREG_DRAFT_* files in
  research/results/portfolio/round13_structural/. Do not edit any other repo file; no git commands that change state.
- Files named REPORT.md or FINDINGS.md may be blocked: name your write-up STREAM_<stream>.md.

## What to return (final message, <= ~1,500 words)
- A table: hypothesis (mechanism, source) | where | PRE / IS / VAL mid (bp, t) | cost | net IS / VAL | VAL/IS ratio |
  power (IS and VAL size) | verdict.
- Best cell per family, cells tried, chance benchmark; any PREREG_DRAFT path, or "none".
- Anything surprising; directions that need the user's decision; paths of your scripts and STREAM file.
