# Round 29 brief: the round-level fade on index CFDs no round has used, and the Asian venue opens left from round 27

Written 2026-10-18 00:42 UTC (from `date -u`), before any round-29 return was computed. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same task and bars as rounds 25-28 (the user's LIVE and DEMO bars in
research/PROMPT.md; no RELAXED tier). **This is the last round of this session**: the user asked to stop after round 29.

**Read first and follow for everything not changed here**:
- research/results/portfolio/round13_structural/BRIEF.md: eras, costs, constraints, bars, multiple testing, pitfalls,
  resources, what to return.
- research/PROMPT.md.
- research/JOURNAL.md, the entries for rounds 18-28 and the gold HOLD look of 2026-10-18 at the top.
- research/results/portfolio/round26_tick_events/BRIEF.md: the binding tick fill model.
- Stream F: research/results/portfolio/round28_round_levels/BRIEF.md (the level rule), STREAM_R2.md (its minute fill
  model and the "Untested ideas" that motivate F) and STREAM_R1.md (the minute-vs-tick calibration).
- Stream O: research/results/portfolio/round27_levels_opens/BRIEF.md, HYPOTHESES_V.md and STREAM_V.md (the method
  and its "Untested ideas" that list O's clocks).

## Stream F: fade a fresh minor round level on the European index CFDs no round has used
**Why.**
- Round 28 R2 found that, on the index CFDs, a resting stop beyond a fresh MINOR round level loses after the fill:
  - UK100 100-point levels: mid at 15 min -2.96 bp (t -4.35) IS, -2.47 (t -2.87) VAL;
  - AUS200 50-point levels: -3.06 (t -4.24) IS, -1.27 (t -2.01) VAL;
  - the European group as a whole: -0.051 sd (t -1.89) IS, -0.012 (t -0.43) VAL;
  - US500 went the other way (+0.061 / +0.111 sd).
- That is post hoc and on the opposite side of the declared hypothesis.
- Mechanism for the fade (declared here): stop-loss orders resting beyond a fresh round level fire as market orders;
  liquidity providers absorb them and the price reverts (temporary price pressure; Osler 2003's take-profit clusters
  sit at the level itself). Gold is the exception that round 27 found, where the stops cascade.
- The only clean test of a post-hoc pattern without HOLD is symbols nobody has looked at. IC M1 bid bars for ES35, F40,
  IT40, STOXX50 and US2000 (2016-2026, `research/data/<SYM>/m1/*.zbars`, pulled in round 7) were never used for round
  levels.

**Declared set.**
- Confirmatory book: the four European index CFDs, ES35, F40, IT40, STOXX50, with the fade side.
- Control: US2000. The US500 lead predicts no fade there; report both sides.
- Information only, labelled as already seen: the fade side re-run on round 28's index symbols (UK100, AUS200, DE40,
  JP225, HK50, US500), with the same code.

**Rule.**
- Levels: round 28's spacing rule, computed from each fresh symbol's IS median price. Declare the spacings and event
  counts per year in HYPOTHESES_F.md, computed from prices before any return.
- Event: round 28's event, the "minor" cell. The bot arms at the nearest minor level; trades are taken only at minor
  levels that are not major levels. Arming band 0.15 % of mid, fresh 24-hour high or low, 60-minute busy window,
  1,440-minute level rule, round 28's exclusions. The home currency is EUR for the European indices and USD for
  US2000.
- **Primary trade.** When the round-28 stop would trigger (R2's minute trigger test), go the OPPOSITE way at market at
  the close of the trigger minute: sell at the bid after an upward break, buy at the ask after a downward break. Exit
  at market 30 minutes later.
- Secondary variants:
  - exits at 15 and 60 minutes;
  - entry one minute later (the close of the next minute);
  - a resting limit fade at the stop's price. It fills only when the price trades through: for a sell, the bar's bid
    high must exceed the limit by at least one tick; for a buy, the bar's ask low must be at least one tick below it.
  - spread x1.5.
- Costs. The bars are bid only, so ask = bid + a declared spread: IC's published average spreads from round 7 (ES35
  4.2, IT40 9.0 fixed, F40 1.79, STOXX50 1.5, US2000 0.34 index points), times an hour-of-day factor.
  - The factor is the IC minute-spread profile of DE40 (for the European indices) or US500 (for US2000) over 2016-21:
    the median spread in each UTC hour divided by its median in the main cash session.
  - IT40's spread is fixed, so its factor is 1 in its quoted hours.
  - There is no commission on indices.
  - Fix the factor table in HYPOTHESES_F.md before any return.
- Controls:
  - round 28's 200 shifted grids per symbol, fade side;
  - random entries as in round 13: same symbol, side from the same fresh-extreme rule at the random time, same hold.
- Book: equal risk per trade (net / the symbol's IS per-trade sd of the 30-minute return); t clustered by UTC day;
  power on the IS and VAL size, per trade and per day; LIVE and DEMO bars on the book and per symbol.
- Eras: IS 2016-21, VAL 2022-24. No PRE exists for these symbols. HOLD (2025-01..) is never loaded: assert ts <
  2025-01-01 on load.
- Code: adapt round 28 R2's code (`.../scratchpad/r28/R2/code/`: mdata.py, engine.py, fills.py, run_sym.py,
  spacings.py, analyze.py) rather than rewriting it. Keep its synthetic tests; add tests for the fade fills.

## Stream O: the direction of the first seconds at the Asian venue clocks round 27 left untested
**Why.**
- Round 27 V: at 8 venue clocks the direction of the first seconds carries information at mid beyond chance (max mid
  t p 0.009), but nothing survives costs.
- V listed three untested clocks:
  - the 23:00 / 00:00 UTC cluster (ASX 10:00 Sydney, TSE 09:00 JST), seen in round 26's jump counts in AUD, NZD, gold
    and the US indices;
  - the A-share / HKEX opens (09:30 and 13:00 Beijing / Hong Kong);
  - the SGE night-session start (20:00 Beijing).
- O tests these with V's method, unchanged.

**Clocks** (DST-aware; trading days of the named venue only):
- ASX-OPEN, 10:00 Sydney (23:00 UTC under AEDT, 00:00 UTC under AEST).
- TSE-OPEN, 09:00 JST (00:00 UTC). Under AEST it coincides with ASX-OPEN; report the coinciding days as one event
  labelled ASX+TSE as well as by venue.
- CNHK-AM, 09:30 Beijing / Hong Kong (01:30 UTC), days when SSE or HKEX opens.
- CNHK-PM, 13:00 Beijing / Hong Kong (05:00 UTC).
- SGE-NIGHT, 20:00 Beijing (12:00 UTC), SGE night-session days (round 27's CN_night calendar is the SHFE 21:00 one;
  build SGE's from SGE's notices or use the same holiday rule and say so).
- Information only: TSE-PM, 12:30 JST (03:30 UTC).

**Instruments** (IC ticks 2016-24):
- ASX / TSE: AUDUSD, NZDUSD, XAUUSD, US30, USTEC.
- CNHK: AUDUSD, XAUUSD, US30, USTEC.
- SGE-NIGHT: XAUUSD, XAGUSD.

**Method.**
- Round 27 V's cells (follow V1 / fade V2, windows, k thresholds, holds), fill model, latencies, controls (shifted
  clocks, venue-holiday placebos), sign-flip max-t null and bars.
- Copy and adapt `.../scratchpad/r27/V/code/` (common_v.py, cal_v.py, pass_v.py, analyze_v.py, info_v.py,
  minute_v.py, report_v.py, test_sim_v.py) rather than rewriting it.
- Holiday calendars for ASX, TSE and HKEX are not in `.../scratchpad/r25/shared/cal/venue_calendars_2015_2024.json`.
  Build them from the exchanges' own published holiday lists 2016-24, or from the package that round 27 used for that
  file, and record the source.
- Eras: IS 2016-21, VAL 2022-24. HOLD never loaded.

## Both streams
- **Files to write.** HYPOTHESES_<F|O>.md in research/results/portfolio/round29_fades_opens/, with `date -u` times,
  before any return:
  - restate the rule;
  - declare the cells and count them;
  - give the event counts per year, computed without returns;
  - state the expected sign from the mechanism.

  Then STREAM_<F|O>.md at the end:
  - per symbol (or clock) and for the pooled set: IS / VAL mid and net per latency or variant, VAL / IS, years > 0,
    power on the IS and VAL size, placebo and random shares, spread x1.5, +1 minute;
  - a "needs the user" section and an "untested ideas" section;
  - script paths.

  PREREG_DRAFT_<F|O>_* only for a rule that meets LIVE or DEMO on IS / VAL. Do NOT open HOLD.
- **C3 correlation.** For any rule that meets DEMO or LIVE numbers, report the correlation of its daily P&L with C3's
  (research/results/portfolio/trades_C3_gotobi_jpy_basket.csv if present, else say so).
- **Where to write.** Scripts and outputs only under
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r29/<F|O>/.
  In the repo, write ONLY your HYPOTHESES / STREAM / PREREG_DRAFT files.
- **How to run.** Run Python from the repo root (`cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=.
  research/.venv/bin/python <script>`), numpy only. At most 2 heavy processes per stream, each under ~3 GB RAM.
- **Forbidden.**
  - No price fetches. Exchange holiday pages are allowed for O.
  - No git commands that change state, no edits to research/ code.
  - Never put the user's e-mail address or any personal data into a web request.
- Files named REPORT.md or FINDINGS.md may be blocked.
