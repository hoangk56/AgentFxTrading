# Round 55 stream M: hypotheses (insider-purchase day-1 drift, intraday entry after the opening auction)

Declared 2026-10-30 (`date -u` at drafting start: Fri Oct 30 10:48:44 UTC 2026), after counting event dates from round
54 I's events.csv and D's daily validity mask, **before any Dukascopy M1 file was requested or loaded** (the two
scale / timestamp probe days in the Data section are checked after this file is written, on non-event days, and only
bar times and price levels against D's daily candles are compared). Bars: LIVE / DEMO from research/PROMPT.md (no
RELAXED tier). HOLD 2025-01-01..2026-09-24 closed: no 2025 / 2026 M1 file will be requested; every series is cut at
ts < 2025-01-01 00:00 UTC at parse, before anything is printed.

## Honesty note (what was seen before this design)
Round 54 I saw the D+1 daily open -> close return at mid in both IS and VAL: all buys +17.6 / +19.7 bp, CEO / CFO
+46.5 / +59.3, cluster +45.6 / +42.8, OPP +17.4 / +27.5, all beating 0.96-1.00 of random firms; nothing after the D+1
close. **The intraday-entry rule below is designed after that look**, in both eras. To limit the damage: the side
(long), the four families and their definitions (ALL, OPP, CEOCFO, CLUSTER; ROUT placebo) are unchanged from round 54
I (events.csv reused read-only); the entry offsets, exit times, hedge, costs, cells and the primary cell are fixed
here before any M1 return is loaded; and the HOLD expectation is sized at **1/4 of the VAL effect** (round 18 rule:
rules chosen after a VAL look kept 19-31 % of VAL size at holdout) in the power arithmetic below and in the write-up.

## Data
- Events: round 54 I's `events.csv` (firm, filing date D, family flags; CMP classification as in HYPOTHESES_I.md).
  D+1 = first trading day of D's daily grid strictly after D (Form 4 dated D is public by 22:00 ET on D).
  Kept when the firm has a valid daily candle on D+1 (and D+2 for the overnight variant). Counts (valid D+1
  firm-days, no returns seen): ALL 1,336 (2017 58, 2018 200, 2019 268, 2020 235, 2021 135, 2022 157, 2023 169,
  2024 114); OPP 240; CEOCFO 208; CLUSTER 165; ROUT 82. 859 distinct D+1 dates. IS 2017-21 (data start), VAL 2022-24.
- Prices: Dukascopy M1 bid / ask, `datafeed/{SYM}/{YYYY}/{MM0}/{DD}/{BID|ASK}_candles_min_1.bi5` (MM0 zero-based),
  browser UA (the approved datafeed exception; robots.txt checked first), only for: each event firm on D+1 and D+2;
  a random-firm pool of 3 non-ETF names per distinct D+1 date (drawn now with numpy seed 55 among names with a valid
  daily candle on D+1 and D+2 that have no ALL event filed on D; same names pulled on D+2, pool of 2 for D+2 if the
  pull runs long). Price scale and timestamp convention are verified on 2 known non-event days against D's daily
  candles before the bulk pull (expected: scale 1e3, bar time = start of minute, regular session 09:30-16:00 ET).
  Zero-volume flat minutes are no trading.
- Hedge: IC US500 M1 from `research/data/m1/US500.npz` (local, bid open + mean spread as ask, cut at load), the same
  minutes as the stock legs. SPY M1 is not pulled (pull budget); IC US500 is the tradeable hedge.
- Rates: FRED DFF (D's stocklib).

## Trade rule (fixed now)
- Long the event firm on D+1. **Entry offsets: 09:35, 09:45, 10:00 ET**: the first M1 bar with volume whose start
  time is at or after the offset and before offset + 5 min, filled at that bar's **ask open**; no such bar -> no trade
  (counted).
- **Exit E1 (primary): 15:55 ET on D+1** at the bid open of the first bar with volume in [15:55, 16:00); no bar -> no
  trade. **Exit E2 (declared variant): 15:55 ET on D+2**, same rule; financing (EFFR + 3 %)/360 per calendar night on
  the long (Fri -> Mon = 3), hedge short -0.5 bp a night; one position per firm (an event on a firm already held is
  skipped); trades whose hold spans a D-flagged split or jump are dropped.
- Hedge: H = short IC US500 at the stock legs' entry and exit minutes (short at bid open, cover at bid open + mean
  spread; the US500 bar at the same minute, else the next within 3 min, else the trade is dropped from H cells and its
  U twin is kept), same notional; U = unhedged.
- Costs: Dukascopy bid / ask of the traded bars (entry ask, exit bid), plus IC commission USD 0.02 per share per side on
  the raw intraday price (M1 prices are raw; checked against D's raw daily). No financing on E1 (flat before the
  rollover).
- Variants for every graded cell: spread x1.5 (half spread x1.5 around mid on both legs); **+1 minute** (entry at
  offset + 1 min, exit 15:56); ex 2020-03/04; by year.

## Cells and selection
- Counted cells: 4 families x 3 offsets x 2 exits x 2 hedge = **48**. ROUT (routine-only buys, CMP placebo) is run on
  the same 12 offset x exit x hedge combinations and not counted.
- **Primary cell: ALL, 09:45, E1, H** (the family with the most events; middle offset; the round 54 finding was a
  same-day effect; hedged because the effect is firm-specific). Declared now, not chosen on results. Cell selection,
  if any, on IS net t only; VAL checks.
- t: day-clustered (trades summed per entry date). Eras: IS 2017-21, VAL 2022-24.
- Random-firm control: for each event, the same date, minutes, hedge and costs with a firm drawn from that date's
  pool (never the event firm); 1,000 seeds; report the share of seeds the cell beats (DEMO >= 90 %, LIVE >= 95 %).
  The pool is only 3 names per date, so seed draws are correlated: stated as a limit.
- Chance benchmark: per seed, all 48 cells recomputed with the random firms; null distribution of the best-of-48 IS
  net t; report P(null max >= observed max).
- Drift decomposition (diagnostic, not counted): mid return from the first 09:30 bar to 15:55, and from each offset to
  15:55, as a share of round 54's daily open -> close mid; plus the 09:30 -> offset part.
- Spread profile (diagnostic): median bid / ask spread in bp at the bar opens 09:30, 09:31, 09:32, 09:33, 09:35,
  09:40, 09:45, 09:50, 10:00, 10:15, 10:30 ET, for event firms and the random pool, by year.
- Bots: same-day exit -> concurrent positions = events per D+1 date; E2 -> events over two days. Reported as mean /
  max / share of days > 3.
- C3 daily-return correlation for any surviving cell (`trades_C3_gotobi_jpy_basket.csv`).

## Power arithmetic (before any M1 return)
- Per-trade sd: round 54's D+1 open -> close at mid implies ~270 bp (ALL) to ~320 bp (CEOCFO) unhedged; from 09:45
  to 15:55 assume ~230 bp hedged (ALL) and ~300 bp (CEOCFO / CLUSTER).
- HOLD trades (VAL rate x 1.73 years): ALL ~254, OPP ~39, CEOCFO ~46, CLUSTER ~33.
- **1/4 rule:** take the VAL day-1 mid (ALL +19.7, CEOCFO +59.3, CLUSTER +42.8, OPP +27.5) and assume all of it lies
  after the offset (generous) and none is lost to cost; HOLD expectation = 1/4: ALL ~5 bp, CEOCFO ~15, CLUSTER ~11,
  OPP ~7. HOLD power at **zero cost**: ALL 5/230 x sqrt(254) = 0.35; CEOCFO 15/300 x sqrt(46) = 0.34; CLUSTER 0.21;
  OPP 0.19. At full VAL size and zero cost: ALL 1.4, CEOCFO 1.3. **LIVE (power >= 3) is out of reach by the count
  before any return**; it would need ~8x the VAL effect after cost.
- DEMO needs IS net t >= 2: ALL IS n ~896 -> net per-trade Sharpe 0.067, ~15 bp net at sd 230; CEOCFO IS n ~129 ->
  0.18, ~53 bp; CLUSTER n ~106 -> 0.19, ~58 bp; OPP n ~172 -> 0.15, ~46 bp. Expected cost at 09:45 (assumed before
  the spread profile): Dukascopy spread 8-20 bp + commission 11-15 bp round trip + hedge ~1 bp = ~20-35 bp. So DEMO
  needs ALL mid after 09:45 of ~35-50 bp (IS day-1 total is +17.6 from the first quote) or CEOCFO ~75-90 bp (IS total
  +46.5): **expected none**; DEMO only if the day-1 drift is back-loaded and the 09:45 spread is near the close spread.

## Not tested here
Ticks inside the first minutes (M1 only), entries before 09:35 (the opening-auction / first-quote spread is what
round 54 already graded), exits after D+2, SPY hedge, small caps.
