# Round 26, stream S: declared hypotheses (scheduled releases on IC ticks)

Declared 2026-10-17 20:15 UTC (`date -u`), before any return of any cell below was computed. Before this point only
direction-free data checks were run: calendar counts and clocks (no prices), the tick file format on a non-event day
(2019-03-05) and energy tick counts per day. The IS norms used to scale the levels are computed after this file is
written, by the formula fixed here. HOLD (2025-01-01..) is never loaded: every tick request is for a UTC day
<= 2024-12-31 (asserted in code), and placebo days or random windows that would reach 2025 are dropped.

Brief: [BRIEF.md](BRIEF.md) row S and its "Execution model"; eras, costs, bars and multiple testing from
round13_structural/BRIEF.md.

## Mechanism and sources
- S1 (straddle): a release moves the price 5-40 bp in its minute (round 25 B0, t 4-9). The side is not known before
  the release, so the order takes it from the market: a buy stop above and a sell stop below. It pays only if the
  move after the fill exceeds IC's release-minute spread, the slippage beyond the stop and spread-spike triggers.
  Literature on the release minute: Andersen, Bollerslev, Diebold & Vega (2003, AER) on the jump at the release;
  Evans & Lyons (2005, AER P&P) and Love & Payne (2008) on order flow and drift in the minutes after; round 3 / round
  10 here: no drift after a first 5-minute move (entry after 5 minutes, minute bars).
- S2 (overshoot fade): the first seconds overshoot and part of the jump reverses (Chaboud, Chernenko & Wright 2008 on
  EBS: the jump is mostly complete within 1 minute and liquidity thins; Rosa 2011 / Fair 2002 on reversals at the
  release; round 10's post-hoc fade of press-conference minutes). S2a rests limits at the far levels before the
  release; S2b fades a large first minute with a market order.

## Events (fixed now)
Calendar: round 25's timed ForexFactory file `r25/shared/cal/ff_events_utc.csv`, rows with a `utc` time, 2016-01-01
..2024-12-31. T = the release minute (bar label T), T_ms = its first millisecond.
- Type list: round 25 B0's 56 included types (`r25/B/out/b0_included.json`, chosen on IS only by the realised-
  surprise move), restricted to USD, AUD and NZD types. Other currencies' types (EUR, GBP, CAD, CNY) are out.
- USD clock fix (official US schedules, declared): USD rows whose New York clock is hh:32 or hh:17 are snapped to
  hh:30 / hh:15 (FF glitches: Retail Sales 2021-03..05, Advance GDP 2020-04-29, ADP 2022-03-02, claims 2023).
- A slot = one (currency, T). Several rows at the same minute are one slot (one position per slot and instrument).
  The slot's dominant type = the slot's type with the largest IS norm on that instrument (below).
- Sets (primary = High impact rows only; secondary = High + Medium rows of the same types):

| set id | events | instruments | notes |
|---|---|---|---|
| USD.<sym>, USD.pool | USD High slots of the 21 USD types | AUDUSD, NZDUSD, XAUUSD, US30, USTEC; pool = all five legs | |
| AUD.AUDUSD | AUD High slots of the 7 AUD types | AUDUSD | |
| NZD.NZDUSD | NZD High slots of the 3 NZD types | NZDUSD | only slots whose span T-2 .. T+17 min lies outside 16:55-18:10 New York (rollover hour avoided); the others are reported as information |
| EIA.XTIUSD, EIA.XBRUSD, EIA.pool | every timed USD "Crude Oil Inventories" row (any FF impact; the brief declares the set) | XTIUSD, XBRUSD | 2018-2024 (ticks from 2017-12-29); IS = 2018-21; events 2020-04-01..2020-04-30 excluded (IC oil glitch, round 13 pitfall), reported with them as information |
| GAS.XNGUSD | every timed USD "Natural Gas Storage" row | XNGUSD | 2018-2024 |
| USDHM.pool (secondary) | USD High + Medium slots of the 21 USD types | the five USD instruments pooled | |
| AUDHM.AUDUSD (secondary) | AUD High + Medium slots | AUDUSD | |

- Data rule (per slot and instrument): skipped if there is no tick in [T-7 min, T-2 min] (no fresh quote at
  placement) or no tick in [T, T+16 min]. A missing exit tick within 10 min of the exit time takes the last tick
  before it.

## Norm (scale of the levels; formula fixed now, numbers computed on IS only)
norm(type, instrument) = IS median over the type's IS slots (2016-21; energies 2018-21; High + Medium rows of the
type) of |mid(last tick < T + 60 s) - mid(last tick < T)| / mid(last tick < T) x 1e4 (bp), the 1-minute release
move. Needs >= 10 IS slots, else the type is dropped for that instrument. Slot norm = max over the slot's types. The
same IS number is used in VAL (no VAL information). For EIA and GAS the type is the report itself.

## Execution model (binding, from the brief)
- Placement at P = T - 120 s. Reference quote = the last tick with ts <= P: bid0, ask0, mid0. Price distances:
  x bp -> x x mid0 x 1e-4. Order window: ticks with P < ts < W, W = T + 120 s for h >= 3 and W = T + 60 s for h = 1
  (orders never outlive the exit).
- Latency variants L: 0 ms (fill on the triggering tick), one tick later (the next tick), 250 ms, 1000 ms (first
  tick with ts >= trigger ts + L). **Primary for the verdict: L = 250 ms.** Stress: L = 1000 ms and spread x1.5.
  L = 0 and one-tick are reported. The same L applies to every market execution of the cell (triggered stop, timed
  exit, protective stop) and to the cancel of the other OCO leg.
- Market fills: a buy at the ASK, a sell at the BID of the fill tick. Spread x1.5: a buy at mid + 0.75 x spread, a
  sell at mid - 0.75 x spread of the fill tick (both legs of the trade).
- Stops trigger server-side: a buy stop when the ASK >= its level, a sell stop when the BID <= its level, on any tick
  after placement (a widening spread alone can trigger; modelled as it happens and counted).
- Limits: a buy limit fills when the ASK <= its level, a sell limit when the BID >= its level, at the level (no price
  improvement); L applies to the cancel of the other leg and to the exit, not to the limit fill.
- OCO: on the first fill the other leg is cancelled; the cancel takes effect at the fill tick (L = 0), one tick after
  it (one-tick), or at fill ts + L (250 / 1000 ms). If the other leg triggers at or before the cancel takes effect
  (including on the same tick) both legs fill and both are held to their exits; the event's P&L is the sum (counted
  as a "double fill"). No new orders after the window.
- Exit: market order at T + h (first tick with ts >= T + h + L; one-tick: the tick after the first tick >= T + h).
- Commission 0.6 bp round trip per leg for AUDUSD, NZDUSD, XAUUSD; 0 for US30, USTEC, XTIUSD, XBRUSD, XNGUSD. No swap
  (all exits <= T + 15 min, none across 21:00/22:00 UTC: AUD/USD/energy slots are far from it; NZD primary avoids it).
- Gross ("mid") per leg = side x (mid at exit fill tick - mid at entry fill tick) / mid0 x 1e4; net per leg = side x
  (exit price - entry price) / mid0 x 1e4 - commission (limit legs: entry price = the level).

## Cells (every cell in full)
Every cell runs on every set above, with the four latencies and spread x1.5 reported.

S1, OCO stop straddle (24 cells per set): buy stop at ask0 + k, sell stop at bid0 - k, placed at T-2 min, cancelled
at W if none triggered; exit at T + h; side = the triggered leg.
- k = m x slot norm, m in {0.25, 0.5, 1.0}
- h in {1, 3, 5, 15} min
- stop variant: ns = none; ps = protective stop at 1.0 x slot norm from the entry fill price (long: sell stop at
  entry - s on the BID; short: buy stop at entry + s on the ASK), checked from the tick after the entry fill to the
  exit, executed with the cell's L.
- ids: S1-m{0.25,0.5,1.0}-h{1,3,5,15}-{ns,ps}.

S2a, resting limit fade (12 cells per set): buy limit at bid0 - k2, sell limit at ask0 + k2, placed at T-2 min,
OCO, cancelled at W if none filled; exit at T + h.
- k2 = m2 x slot norm, m2 in {0.5, 1.0, 2.0}; h in {1, 3, 5, 15}; ids S2a-m{0.5,1.0,2.0}-h{1,3,5,15}.

S2b, market-order fade (9 cells per set): r1 = (mid(last tick < T + 60 s) - mid(last tick < T)) / mid x 1e4. If
|r1| > c x slot norm, enter against r1 at T + 60 s (buy at the ask of the first tick >= T + 60 s + L if r1 < 0, sell
at the bid if r1 > 0), exit at T + h.
- c in {1, 2, 3}; h in {3, 5, 15}; ids S2b-c{1,2,3}-h{3,5,15}. Extra stress for S2b (the round-13 "+1 minute"):
  entry at T + 120 s, same exit.

Count: 45 cells x 12 primary set rows = 540, + 45 x 2 secondary set rows = 90; **630 cells**. Latency and spread
variants are robustness readings of the same cell, not extra cells (the verdict is read at L = 250 ms only).

## Statistics (per cell)
- Per event (slot x instrument; an unfilled event = 0) and per trade (events with a fill): n, fill rate, mean gross
  and net bp, day-clustered t (cluster = UTC date of T), sd, by era (IS 2016-21, energies 2018-21; VAL 2022-24) and
  by year; VAL/IS of net (and of gross); per-trade net Sharpe and per-day net Sharpe (day = sum of the cell's trades
  that UTC day); power = Sharpe x sqrt(1.73 x trades (or trade days) per year), at the IS and at the VAL size.
- Per dominant type (information): n, mean gross / net for the primary cells.
- Robustness (information): median trade, mean trimmed at the IS 1 % / 99 % quantiles, share of P&L from the top 5
  events, with and without 2020-03-01..2020-04-30.
- Fill-model checks (S1): share of triggers before T (pre-release); share of triggers where the mid at the trigger
  tick had moved less than k in the trigger direction (spread-assisted) and where it had not moved in that direction
  at all (spread-only); double-fill share by L; slippage beyond the stop (fill price minus level, bp) median and p90
  by dominant type and L; spread at T-2 and at the trigger tick.

## Controls (same parameters: the event's k / k2 / c and norm, same h, same L)
- Placebo days: the same orders at the same home-local clock (New York for USD and energies, Sydney for AUD,
  Wellington for NZD) on the same weekday 1 and 2 weeks before and after (up to 4 days), in the same era, <=
  2024-12-31, with no High or Medium row of the set's currency within +-60 min (energies: no USD High/Medium row and
  no crude or gas row within +-60 min). For EIA and GAS the same weekday always has the report, so their placebo days
  are Monday, Tuesday and Friday of the same week at the same clock (declared deviation). Reported: placebo fill rate,
  mean net per placebo trade and per placebo opportunity, event minus placebo (t), and the share of 200 seeds (one
  placebo day drawn per event) whose per-trade mean net is below the event's.
- Random times: per slot, 30 candidate whole minutes drawn once (fixed RNG) from [T - 4 h, T + 4 h] on the
  instrument's ticks, excluding minutes within +-60 min of any High/Medium row of the set's currency (energies: also
  crude / gas rows), spans T'-2 .. T'+17 min touching 16:55-18:10 New York, and windows reaching 2025; the same
  candidates for every instrument of a slot. >= 200 seeds, each drawing one candidate per slot; the side and the
  S2b condition are recomputed at the random time. Reported: share of seeds whose per-trade mean net (L = 250 ms) is
  below the event's; also per event.

## Bars (round 13 / PROMPT, unchanged), read at L = 250 ms
- Common: net > 0 in IS and in VAL; still > 0 at spread x1.5 and at L = 1000 ms (S2b: also entry at T + 120 s);
  day-clustered t.
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years net > 0, beats >= 95 % of the random-time control, power >= 3
  (per trade, IS size; the VAL-size power and the expected HOLD t on the VAL effect are reported next to it).
- DEMO: IS t >= 2.0, net > 0 in VAL, beats >= 90 % of the random-time control.
- Placebo-day control reported next to it (a cell that does as well on placebo days is not a release effect).
- A cell meeting LIVE or DEMO stops its family: PREREG_DRAFT_S_<name>.md with the exact rule, cell count, expected
  HOLD events, expected HOLD t on the VAL size and at 0.65 of it, and the C3 daily correlation. HOLD is not opened.

## Multiple testing
K = cells with trades (<= 630). Benchmarks: the 95th percentile of the max |t| of K independent normals, and a
sign-flip permutation null (1,000 draws) that flips each event day's gross returns, shared across all cells, on the
IS gross t. The best IS |t| of each family and of all cells is compared with both.

## PRE (minute level, labelled, information only)
S2b only, on Dukascopy M1 bid closes 2007-2015 (`research/data/duka/m1c`, files AUDUSD / NZDUSD / XAUUSD; the
`*_2026` files are never opened): USD High slots on AUDUSD, NZDUSD, XAUUSD; AUD High on AUDUSD; NZD High on NZDUSD
(rollover rule as above). r1 = close(bar T) - close(bar T-1); entry at close(bar T), exit at close(bar T + h - 1);
gross bid-close bp only, with the IS norm. S1 and S2a need intraminute paths and have no PRE check.

## C3
Daily net P&L correlation (IS + VAL rows only) with research/results/portfolio/trades_C3_gotobi_jpy_basket.csv for
the best cell of each family and for any survivor.

## Addendum 1 (post hoc, information only), 2026-10-17 20:28 UTC (`date -u`)
Written after the declared cells were computed (none passed; the fill check showed that 73-96 % of S1 triggers at
m = 0.25-0.5 on USD releases happen between T-2 and T, i.e. before the number). Not counted as declared cells, no
bar applies, no PREREG can come from them:
- S1-armed: as S1 (same m, h, stop variants, latencies, costs), levels from the T-2 quote, but the stops become
  active only on ticks with ts >= T (a cBot can send the orders a few seconds before T at the T-2 levels).
- S2a-armed: as S2a, limits active only from T.
Event jobs only (no controls), primary sets.
