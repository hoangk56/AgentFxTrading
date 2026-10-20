# Round 28 brief: the gold round-level cascade on the major round levels of the other IC symbols, pooled for power

Written 2026-10-17 22:08 UTC (from `date -u`), before any round-28 return was computed (the only numbers computed so
far are the IS median PRICES below, which choose the level spacings; no return was looked at). Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same task and bars as rounds 25-27 (the user's original LIVE and DEMO
bars, research/PROMPT.md; no RELAXED tier).

**Read first and follow for everything not changed here**: research/results/portfolio/round13_structural/BRIEF.md
(eras, costs, constraints, bars, multiple testing, pitfalls, resources, what to return); research/PROMPT.md;
research/JOURNAL.md (rounds 18-27 at the top); research/results/portfolio/round27_levels_opens_2026-10-17.md,
round27_levels_opens/STREAM_G.md, HYPOTHESES_G.md and PREREG_DRAFT_G_gold_round50_cascade.md (the rule this round
generalises, its fill model, its placebos) and round26_tick_events/BRIEF.md (the binding tick fill model).

## Why
Round 27 G: gold continues after it breaks a fresh $50 / $100 level (Osler 2003 / 2005 stop-loss clusters at round
numbers; Lucey & O'Connor 2016), not at ordinary $10 levels. With a resting stop at the level + 0.5 spread and a
30-minute exit: IS +5.99 bp (t 2.66), VAL +3.27 (t 1.81), 9 / 9 years > 0, PRE +5.35 (t 3.12), random level grids
beaten 96 / 99.5 %. Only power fails: ~60 breaks a year give 1.45 against 3. If the major round levels of other
instruments carry the same continuation, a book of independent breaks reaches LIVE power (e.g. ~700 breaks a year at
a per-trade net Sharpe of 0.1 gives ~3.5). Round 3 (FX big figures) and round 25 C (index 100-point levels) found
nothing at MINOR levels; round 27 found nothing at gold's minor levels either. Major levels elsewhere were never tested.

## The declared rule (identical in both streams; nothing here may be tuned on returns)
- **Level spacings.** Sequence S = {1, 5} x 10^k. Major spacing M = the element of S nearest in log to 0.034 x the
  symbol's IS (2016-21) median mid (0.034 = gold's $50 / its IS median, rounded); minor m = the next smaller element,
  super = the next larger. BTCUSD only: the same rule applied to the trailing 250-trading-day median daily close,
  recomputed on the first trading day of each month (its price ranged 3.4k-63k). Resulting spacings (median price;
  minor / MAJOR / super):

  | symbol | IS median | minor / MAJOR / super | symbol | IS median | minor / MAJOR / super |
  |---|---|---|---|---|---|
  | XAUUSD | 1,324 | 10 / **50** / 100 | US30 | 25,367 | 500 / **1,000** / 5,000 |
  | EURUSD | 1.1359 | 0.01 / **0.05** / 0.10 | US500 | 2,827 | 50 / **100** / 500 |
  | GBPUSD | 1.3103 | 0.01 / **0.05** / 0.10 | USTEC | 7,301 | 100 / **500** / 1,000 |
  | AUDUSD | 0.7372 | 0.01 / **0.05** / 0.10 | DE40 | 12,369 | 100 / **500** / 1,000 |
  | NZDUSD | 0.6894 | 0.01 / **0.05** / 0.10 | UK100 | 7,119 | 100 / **500** / 1,000 |
  | USDCAD | 1.3104 | 0.01 / **0.05** / 0.10 | JP225 | 21,985 | 500 / **1,000** / 5,000 |
  | USDCHF | 0.9747 | 0.01 / **0.05** / 0.10 | HK50 | 26,269 | 500 / **1,000** / 5,000 |
  | USDJPY | 109.64 | 1 / **5** / 10 | AUS200 | 6,040 | 50 / **100** / 500 |
  | EURJPY | 125.41 | 1 / **5** / 10 | XTIUSD | 59.17 | 0.5 / **1** / 5 |
  | GBPJPY | 144.12 | 1 / **5** / 10 | XBRUSD | 65.23 | 0.5 / **1** / 5 |
  | AUDJPY | 80.82 | 1 / **5** / 10 | BTCUSD | adaptive | e.g. 100 / **500** / 1,000 at ~9.4k |

  Out of the book (already failed or too costly): XAGUSD and XPTUSD (round 27: no barrier / 20-35 bp), XNGUSD,
  ETHUSD (spreads), USDCNH (bid only).
- **Event and order (round 27's G1-XAU50 rule, scaled).** mid = (bid + ask) / 2. Arming band b = 0.15 % of the mid
  (gold's $2 at its IS median). The bot arms only while flat and >= 60 min after its last trigger on that symbol, on
  the nearest MINOR level L within b of the mid: an upper L if L is above the highest mid of the previous 1,440 clock
  minutes, a lower L if below the lowest; only if L has not triggered in the previous 1,440 minutes and the order is
  not marketable when placed. Upper: buy stop at L + 0.5 x s60; lower: sell stop at L - 0.5 x s60 (s60 = median
  last-tick spread of the 60 minutes before arming; minute data: the median minute spread). Cancel when the mid leaves
  the band or an exclusion starts. **A trade is taken only when L is a multiple of the MAJOR spacing** (a trigger at a
  minor level is not traded but still starts the 60-minute busy window and counts for the 1,440-minute rule).
- **Exit**: market order 30 minutes after the trigger (the hold round 27 picked after looking in gold, disclosed;
  declared here for every other symbol before their numbers). Secondary exits 15 and 60 min. No protective stop.
- **Exclusions**: arming within +-15 min of a High-impact calendar minute of the symbol's currencies and USD (timed
  calendar .../scratchpad/r25/shared/cal/ff_events_utc.csv; indices: the home currency and USD; metals, oil, BTC: USD);
  16:55-18:10 New York (rollover); 15 min after a quote gap > 60 min; **JPY pairs 23:00-02:00 UTC (C3's territory)**.
  Positions never cross 17:00 New York (exit early at 16:54 NY if needed, counted as such).
- **Dose cells (declared)**: major (primary), super, minor (all minor levels that are not major), repeat touches of a
  major level (a major level that triggered and failed within the previous 5 days), and the side split down / up
  (mechanism: long-biased holders' stop-loss sells sit below round levels, so downward breaks should be stronger in
  gold, indices and BTC; no prior for FX).
- **Placebo**: 200 grids per symbol of the same rule with the major grid shifted by an offset that lies strictly
  between minor levels (offset = (k + u) x m, k uniform in {0 .. M/m - 1}, u uniform in [0.3, 0.7]); the book-level
  placebo sums the same draw index across symbols. Report the share of draws the real book beats.
- **Costs and fills**: tick symbols use round 26's binding fill model (buy at the ASK / sell at the BID of the first
  tick at or after trigger + latency; latency 0 / 250 / 1,000 ms and one tick later; 0.6 bp commission FX and metals;
  0 for indices, oil, BTC). Minute-only symbols use a minute fill model: the stop fills at max(stop price, the first
  available price beyond it) + a slippage term calibrated on the tick symbols (compare the minute model with the tick
  fills on XAUUSD, AUDUSD and US30 for the same events and report the bias); buy at ask = bid + the minute's spread.
  Also spread x1.5 and both fills +1 minute.
- **Pooling (the book)**: equal risk per trade: each symbol's per-trade net bp divided by that symbol's IS per-trade
  sd of the 30-minute return (computed from the real events of IS only, fixed for VAL). Book statistics per trade and
  per UTC day; t clustered by day; power = per-trade net Sharpe x sqrt(1.73 x trades a year) and the per-day version,
  on the IS and the VAL size. Bars: LIVE and DEMO as in round 13's brief, applied to the book; also report every symbol
  and each class (FX, JPY crosses, US indices, other indices, oil, BTC, gold).
- **Eras**: IS 2016-21, VAL 2022-24, PRE 2004-15 at minute level (Dukascopy) for EURUSD, USDJPY, USDCHF, EURJPY,
  GBPJPY (research/data/duka/m1) and AUDUSD, NZDUSD, XAUUSD (research/data/duka/m1c). HOLD (2025-01..) is never
  loaded.

## Streams
| stream | symbols | notes |
|---|---|---|
| R1 | tick symbols: XAUUSD (re-run under this rule, to pool consistently), AUDUSD, NZDUSD, US30, USTEC, XTIUSD, XBRUSD | tick fill model; also writes the minute-vs-tick fill calibration for XAUUSD, AUDUSD, US30 |
| R2 | minute-only symbols: EURUSD, GBPUSD, USDCAD, USDCHF, USDJPY, EURJPY, GBPJPY, AUDJPY, US500, DE40, UK100, JP225, HK50, AUS200, BTCUSD; and the PRE (minute) runs for all eight Dukascopy symbols | minute fill model, calibrated itself on AUDUSD and US30 ticks (R1 runs at the same time) |

Both streams: HYPOTHESES_<R1|R2>.md in research/results/portfolio/round28_round_levels/ with `date -u` times before
numbers (restate the rule, list the symbols' spacings and event counts per year computed from prices before any
return, count cells); STREAM_<R1|R2>.md at the end (per symbol and class: IS / VAL / PRE mid and net per latency,
VAL/IS, years > 0, power, placebo share, dose and side splits; "needs the user"; "untested ideas"; script paths); and
**a per-trade CSV for the lead's pooling** at .../scratchpad/r28/<stream>/trades_<stream>.csv with columns sym, cls,
cell (major / super / minor / repeat / placebo_<k>), era, year, t_trigger_ms, side, gross_bp, net_L0, net_L250,
net_L1000, net_x15, net_p1min, sd_is_30min (the symbol's IS per-trade sd), fill (tick / minute). Do not pool across
streams yourselves beyond your own symbols; the lead pools. PREREG_DRAFT_<stream>_* only for a rule that meets LIVE or
DEMO on IS / VAL for your own symbols. Do NOT open HOLD.

Rules: scripts and outputs only under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/<stream>/.
In the repo write ONLY your HYPOTHESES / STREAM / PREREG_DRAFT files in research/results/portfolio/round28_round_levels/.
Run Python from the repo root (`cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=.
research/.venv/bin/python <script>`, numpy only). Two streams at once: at most 2 heavy processes per stream, each
under ~3 GB RAM. Round 27 G's engine is in .../scratchpad/r27/G/code/ (engine.py, fills.py, run_real.py, run_rand.py,
analyze.py, pre_minute.py, verify_brute.py): copy and adapt it rather than rewriting; keep its synthetic tests. No
price fetches, no git commands that change state, no edits to research/ code. Never put the user's e-mail address or
any personal data into a web request. Files named REPORT.md or FINDINGS.md may be blocked.
