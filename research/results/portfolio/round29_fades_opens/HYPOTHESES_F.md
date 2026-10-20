# Round 29, stream F: fading a fresh minor round level on index CFDs no round has used (declared before returns)

Brief: [BRIEF.md](BRIEF.md), stream F and "Both streams". **Declaration written 2026-10-18 01:00 UTC (`date -u`
01:00:28), before any return of any kind was computed in this stream.** No PRE exists for these symbols.

HOLD (2025-01-01 onwards) is never loaded:
- the zb loader (`code/zbload.py`) lists `research/data/<SYM>/m1/`, keeps only file names < `20250101` BEFORE
  opening any file, and asserts every bar timestamp < 2025-01-01 00:00 UTC (the last bars read: 2024-12-31 for ES35,
  F40, US2000; 2024-12-30 for IT40, STOXX50);
- the seen symbols use round 28 R2's minute caches, built from `research/data/m1/*.npz` cut at ts < 2025-01-01 at load;
- every event time is asserted < 2025-01-01.

What was looked at before this declaration (prices only; no price change was turned into a return):
- the quoted hours, bar counts and price grids of the five zb symbols (`out/profile_zb.txt`);
- the IS 2016-21 minute spreads of DE40 and US500 (the factor table below; spreads only);
- the IS median mids and the spacings (`out/spacings.txt`);
- the event counts below, the spread at the trigger and exit bars of the market fade (cost only), the share of exits
  that fall back to another bar;
- synthetic tests: round 28 R2's `test_engine.py` (passes unchanged on the adapted engine) and the new
  `code/test_fade.py` (fade sides and prices, x1.5, +1 minute, the limit trade-through rule, its gap fill, the buy
  limit's ask low, the tick array, the random-entry side, the spread model): all pass;
- an independent minute-by-minute re-simulation (`code/brute_f.py`, R2's brute.py + the zb source + the limit mode)
  on 11 symbol-years: ES35 2018 stop and limit, F40 2020 limit, IT40 2022 stop, STOXX50 2016 limit, US2000 2021 stop
  and limit, F40 2023 stop (placebo 7), STOXX50 2022 limit (placebo 33), UK100 2019 limit, DE40 2022 limit (placebo
  5). **0 event, class or repeat mismatches** (`out/brute_f.txt`);
- the seen symbols' minor-cell trigger counts equal R2's exactly (UK100 855, DE40 1,848, JP225 531, HK50 400,
  US500 564, AUS200 884).

R2's per-symbol minor-cell results are known (they motivate this stream): UK100 and AUS200 minor levels revert, the
European group IS -0.051 sd / VAL -0.012 sd at the stop entry, US500 +0.061 / +0.111. No result of ES35, F40, IT40,
STOXX50 or US2000 at round levels has been computed by any round.

## Symbols and data
| set | symbols | data | spread |
|---|---|---|---|
| **confirmatory book** | ES35, F40, IT40, STOXX50 | IC M1 bid bars (`research/data/<SYM>/m1/*.zbars`, round 7 pull), 2016-2024 | modelled (below) |
| control | US2000 | same | modelled |
| information only, **already seen** (round 28) | UK100, AUS200, DE40, JP225, HK50, US500 | IC M1 bid + ask close (`research/data/m1`), via round 28 R2's caches | actual minute spread |

Quoted hours from the bars (UTC; EU summer / winter time): ES35 07:00-17:59 / 08:00-18:59; F40 and STOXX50
06:00-19:59 / 07:00-20:59; IT40 07:00-15:59 core, extended to about 19:59 / 20:59 from 2019-21 (its bar count grows
from 124k in 2016 to 201k in 2024); US2000 about 23 hours. STOXX50 has many missing minutes (40-57 bars an hour).

## The rule (round 28's event, minor cell; bar-start labels)
The bot is round 28 R2's minute engine (`code/engine.py`, unchanged in stop mode):
- **Levels.** Spacings from round 28's rule on the IS 2016-21 median mid (S = {1, 5} x 10^k; MAJOR = the element
  nearest in log to 0.034 x median; minor = the next smaller):

  | symbol | IS median mid | minor / MAJOR / super | minor, % of price | band b = 0.15 % of median | traded levels |
  |---|---|---|---|---|---|
  | ES35 | 9,059.6 | 100 / 500 / 1,000 | 1.10 | 13.6 (0.136 minor) | multiples of 100 not of 500 |
  | F40 | 5,279.1 | 50 / 100 / 500 | 0.95 | 7.9 (0.158) | odd multiples of 50 |
  | IT40 | 21,523.5 | 500 / 1,000 / 5,000 | 2.32 | 32.3 (0.065) | odd multiples of 500 |
  | STOXX50 | 3,417.8 | 50 / 100 / 500 | 1.46 | 5.1 (0.103) | odd multiples of 50 |
  | US2000 | 1,539.0 | 10 / 50 / 100 | 0.65 | 2.3 (0.231) | multiples of 10 not of 50 |
  | UK100, AUS200, DE40, JP225, HK50, US500 | R2's | R2's (100/500, 50/100, 100/500, 500/1,000, 500/1,000, 50/100) | | | minor, not major |

  mid = bid + spread / 2 (zb: the modelled spread).
- **Arming** at the close of bar i (R2's rule, unchanged): bar present, next minute not excluded, warm-up done, flat
  and >= 60 minutes after the last trigger, on the nearest minor level within b = 0.15 % of the mid; upper L above the
  max mid-high of the previous 1,440 minutes (bars i-1439..i), lower L below the min mid-low; L not triggered in the
  previous 1,440 minutes; not marketable. Order: buy stop at L + 0.5 s60 (upper) / sell stop at L - 0.5 s60 (lower),
  s60 = median minute spread of the previous 60 bars. Cancelled at an exclusion or when the mid close leaves the band.
- **Trigger** (R2's minute test): the bar's ask high (bid high + spread) >= the buy stop / bid low <= the sell stop.
  Every trigger starts the 60-minute busy window and the level's 1,440-minute block. **A trade is taken only at a
  minor level that is not a major level** (round 28's "minor" cell).
- **Exclusions** (round 28's): +-15 min of a High-impact timed calendar minute (r25 `ff_events_utc.csv`) of EUR and
  USD (ES35, F40, IT40, STOXX50) or USD (US2000); the seen symbols keep R2's currencies (UK100 GBP+USD, AUS200
  AUD+USD, DE40 EUR+USD, JP225 JPY+USD, HK50 CNY+USD, US500 USD); 16:55-18:10 New York; the 15 minutes after a quote
  gap > 60 min. Positions never cross 17:00 New York (exit capped at the bar labelled 16:53 NY).

### Trades (fade side sf = minus the stop's side: sell after an upward break, buy after a downward break)
- **Primary, market fade (mkt):** at the close of the trigger bar k, sell at the bid close (upward break) / buy at the
  ask close = bid close + spread (downward break). Exit at market at the close of bar k + 30: a short buys at the ask
  close, a long sells at the bid close. A missing exit bar uses the first present bar within 10 minutes (not beyond
  the cap), else the last present bar before it (R2's rule; this is how trades near a session close exit).
- **Secondary exits:** k + 15 and k + 60.
- **Limit fade (lim):** the same bot with the stop replaced by a resting limit at the stop's price thr (sell limit at
  L + 0.5 s60, buy limit at L - 0.5 s60). It fills only when the price trades through by at least one tick: sell, the
  bar's bid high >= thr + tick; buy, the bar's ask low (bid low + spread) <= thr - tick. A touch, or a crossing of
  the stop level alone, is not a fill. Fill price thr, or the bar's opening bid (sell) / ask (buy) if the bar opens
  through the limit by >= one tick. The fill is the bot's trigger (busy window, 1,440-minute rule). Exits as above
  from the fill bar. Same minor-cell rule. The tick is, per symbol and year, the coarsest of {1, 0.5, 0.25, 0.1,
  0.05, 0.01} on which >= 99 % of that year's bid closes lie (ES35 and IT40: 1 in 2016-17, 0.1 later; F40 0.1 to 2018,
  0.01 2019-23, 0.05 2024; STOXX50 0.1, 1 in 2017, 0.01 in 2024; US2000 0.1 to 2018, then 0.01; seen symbols in
  `out/spacings.txt`).
- **Readings of every cell:** gross (mid to mid); net; **spread x1.5** (entry and exit each a further quarter of their
  bar's spread worse; for the limit the entry quarter is charged too, conservatively); **+1 minute** (entry by market
  at the close of the next present bar, exit at that bar + h; for the limit cells: the market entry at the close of the
  bar after the fill bar).
- **Costs:** no commission on indices; no swap (no position crosses 17:00 NY). net = sf x (exit - entry) / entry mid x
  1e4; mid = sf x (exit mid - entry mid) / entry mid x 1e4.

## The declared spread model (zb symbols; fixed now)
ask = bid + IC's published average spread (round 7: ES35 4.2, F40 1.79, STOXX50 1.5, US2000 0.34 index points;
IT40 9.0 fixed) x an hour-of-day factor.
- The factor is the IC minute-spread profile of DE40 (for ES35, F40, STOXX50) or US500 (for US2000), IS 2016-21,
  weekdays: the median spread in each UTC hour divided by the median in the main cash session (Xetra 09:00-17:30
  Frankfurt; NYSE 09:30-16:00 New York).
- **Implementation choice, declared:** the table is taken separately for the home exchange's summer-time and
  winter-time days, because the cash session moves by one UTC hour with DST (the pooled 24-hour table blends the two;
  it is in `out/spread_factor.txt`). Hours with no reference quotes take the table's maximum.
- IT40: factor 1 in all its quoted hours.

DE40 factor (cash median 1.0 point):

| UTC hour | 00-05 | 06 | 07-14 | 15 | 16 | 17-19 | 20 | 21 | 22-23 |
|---|---|---|---|---|---|---|---|---|---|
| EU summer (CEST) | 6.0 | 1.0 | 1.0 | 1.2 | 2.0 | 2.0 | 8.0 | 8.0 (not quoted) | 8.0 |
| EU winter (CET) | 6.0 | 6.0 | 1.0 | 1.0 | 1.0 | 2.0 | 2.0 | 8.0 | 8.0 |

US500 factor (cash median 0.40 point):

| UTC hour | 00-12 | 13 | 14 | 15-19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|
| NY summer (EDT) | 1.5 | 1.25 | 1.0 | 1.0 | 1.5 | 1.5 (not quoted) | 1.5 | 1.5 |
| NY winter (EST) | 1.5 | 1.5 | 1.25 | 1.0 | 1.0 | 1.5 | 1.5 (not quoted) | 1.5 |

So in the European quoted hours ES35 pays 4.2 points until 17:00 local, 5.0 in the hour after the cash close in
summer and 8.4 after 18:00 local; F40 1.79 / 2.15 / 3.58; STOXX50 1.5 / 1.8 / 3.0. US2000 0.34 in the NY cash session,
0.43 in its first hour, 0.51 otherwise.

**Round trip of the market fade** (half the spread at the trigger bar + half at the 30-minute exit bar, bp of the mid;
cost only), median IS / VAL: ES35 4.77 / 4.62, F40 3.54 / 2.54, IT40 4.19 / 3.27, STOXX50 4.61 / 3.62, US2000
2.41 / 2.04; seen symbols (actual spreads): UK100 1.82 / 1.37, AUS200 1.96 / 1.14, DE40 0.92 / 0.37, JP225 3.27 /
2.11, HK50 2.91 / 3.25, US500 1.86 / 0.57.

## Event counts from prices (minor cell; no returns)
Per year: market-fade trades (= stop-bot minor triggers) | limit-fade fills | mean of the 200 placebo grids (stop bot).

| symbol | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | IS / yr | VAL / yr | down / up | limit IS / VAL per yr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ES35 | 143 \| 100 \| 124 | 102 \| 83 \| 104 | 121 \| 87 \| 111 | 90 \| 61 \| 98 | 121 \| 93 \| 120 | 102 \| 80 \| 101 | 117 \| 89 \| 116 | 108 \| 87 \| 99 | 105 \| 78 \| 112 | 113.2 | 110.0 | 523 / 486 | 84.0 / 84.7 |
| F40 | 97 \| 74 \| 85 | 58 \| 44 \| 65 | 86 \| 72 \| 89 | 69 \| 53 \| 79 | 118 \| 100 \| 115 | 100 \| 78 \| 98 | 158 \| 131 \| 141 | 114 \| 91 \| 111 | 127 \| 105 \| 112 | 88.0 | 133.0 | 476 / 451 | 70.2 / 109.0 |
| IT40 | 31 \| 24 \| 35 | 30 \| 23 \| 24 | 37 \| 28 \| 35 | 31 \| 22 \| 27 | 45 \| 37 \| 43 | 42 \| 39 \| 47 | 59 \| 47 \| 63 | 52 \| 46 \| 53 | 54 \| 48 \| 55 | 36.0 | 55.0 | 180 / 201 | 28.8 / 47.0 |
| STOXX50 | 71 \| 49 \| 63 | 45 \| 28 \| 41 | 51 \| 41 \| 57 | 49 \| 32 \| 48 | 70 \| 52 \| 76 | 70 \| 53 \| 63 | 87 \| 62 \| 91 | 60 \| 51 \| 70 | 85 \| 72 \| 74 | 59.3 | 77.3 | 314 / 274 | 42.5 / 61.7 |
| **book (4), mkt \| lim** | 342 \| 247 | 235 \| 178 | 295 \| 228 | 239 \| 168 | 354 \| 282 | 314 \| 250 | 421 \| 329 | 334 \| 275 | 371 \| 303 | **296.5** | **375.3** | | 225.5 / 302.3 |
| US2000 (control) | 184 \| 153 \| 198 | 156 \| 130 \| 164 | 245 \| 209 \| 246 | 226 \| 205 \| 231 | 333 \| 288 \| 326 | 396 \| 359 \| 403 | 399 \| 354 \| 418 | 317 \| 271 \| 316 | 316 \| 278 \| 330 | 256.7 | 344.0 | 1293 / 1279 | 224.0 / 301.0 |
| UK100 (seen) | 103 \| 87 \| 95 | 65 \| 52 \| 63 | 92 \| 84 \| 97 | 101 \| 85 \| 89 | 137 \| 119 \| 135 | 87 \| 67 \| 94 | 96 \| 82 \| 118 | 75 \| 66 \| 87 | 99 \| 89 \| 87 | 97.5 | 90.0 | 431 / 424 | 82.3 / 79.0 |
| AUS200 (seen) | 93 \| 60 \| 82 | 68 \| 45 \| 57 | 83 \| 60 \| 80 | 92 \| 83 \| 77 | 135 \| 119 \| 141 | 102 \| 94 \| 99 | 120 \| 106 \| 121 | 88 \| 82 \| 94 | 103 \| 95 \| 101 | 95.5 | 103.7 | 459 / 425 | 76.8 / 94.3 |
| DE40 (seen) | 163 \| 145 \| 166 | 131 \| 115 \| 131 | 190 \| 174 \| 183 | 171 \| 162 \| 165 | 257 \| 230 \| 253 | 214 \| 192 \| 212 | 283 \| 262 \| 278 | 206 \| 193 \| 200 | 233 \| 222 \| 228 | 187.7 | 240.7 | 920 / 928 | 169.7 / 225.7 |
| JP225 (seen) | 47 \| 35 \| 42 | 34 \| 28 \| 29 | 56 \| 43 \| 52 | 44 \| 36 \| 39 | 61 \| 57 \| 57 | 65 \| 57 \| 67 | 60 \| 51 \| 67 | 74 \| 62 \| 66 | 90 \| 85 \| 91 | 51.2 | 74.7 | 249 / 282 | 42.7 / 66.0 |
| HK50 (seen) | 26 \| 18 \| 30 | 32 \| 27 \| 28 | 55 \| 48 \| 54 | 41 \| 35 \| 41 | 57 \| 46 \| 52 | 54 \| 46 \| 54 | 45 \| 41 \| 54 | 44 \| 37 \| 43 | 46 \| 45 \| 43 | 44.2 | 45.0 | 215 / 185 | 36.7 / 41.0 |
| US500 (seen) | 39 \| 32 \| 32 | 29 \| 24 \| 22 | 48 \| 44 \| 52 | 37 \| 33 \| 43 | 78 \| 71 \| 83 | 69 \| 68 \| 74 | 115 \| 107 \| 110 | 71 \| 64 \| 67 | 78 \| 77 \| 79 | 50.0 | 88.0 | 286 / 278 | 45.3 / 82.7 |

Exit fallbacks at 30 minutes (session close or missing exit bar): ES35 3.2 %, F40 2.0 %, IT40 5.8 %, STOXX50 10.4 %
(its missing minutes), US2000 2.0 %; seen 2.9-11.1 %. Exits capped at 16:54 NY: <= 1.1 %.

## Cells (declared and counted)
- **Per symbol, 6 cells:** entry {market at the trigger close, limit at the stop's price} x exit {15, 30, 60}.
  Spread x1.5 and +1 minute are readings of each cell (the bars require both > 0), not cells.
- **Confirmatory candidates:** ES35, F40, IT40, STOXX50 x 6 = **24 symbol cells**; the book (the four at equal risk)
  gives **6 pooled readings** of the same trades. **Primary: book, market fade, 30-minute exit.**
- **Control, US2000 (not a candidate):** the 6 fade cells and the continuation side, i.e. round 28's own stop fill
  (stop + 0.837 x s60 slip, R2's index calibration) at the same minor levels, exits 15 / 30 / 60: 9 cells.
- **Information only, already seen (not candidates):** UK100, AUS200, DE40, JP225, HK50, US500 x 6 fade cells = 36,
  and their pooled set.
- **Readings, not cells:** down / up split, years, without March-April 2020, the continuation side of every symbol.
- **Not declared (will not become candidates):** any other spacing, band, stop offset, limit offset, hold, session or
  year filter, protective stop, major / super levels.

## Controls
- **Placebo: round 28's 200 shifted grids per symbol, fade side.** Offsets (k + w) x minor, k uniform in {0 .. R-1},
  w uniform in [0.3, 0.7], `engine.placebo_draws` (seed 280000 + the symbol's position in R2's list; the five new
  symbols are appended to it at positions 18-22, so the seen symbols get R2's own draws). Each draw runs the full bot
  (both fill modes) and its minor cell is faded with the same fills. Per symbol: the share of draws whose mean net
  (subsampled to the real count when larger, seeded) lies below the real mean; book: the same draw index summed
  across the four in sd units, no subsampling (R2's pooling).
- **Random entries (round 13 style), 200 seeds:** for every real trade, one random minute of the same era, the same
  UTC weekday and the same UTC hour, among minutes with a bar, not in an exclusion window, after the warm-up. **The
  side is recomputed at the random minute from the fresh-extreme rule:** the nearer of the 24-hour mid high M24 and low
  m24 (the bot's own freshness arrays) is taken as the break, so nearer the high the fade sells, nearer the low it
  buys. Entry at that bar's close by market, same exits and costs. Share of seeds whose mean net is below the real
  mean, per symbol and for the book (seed-wise pooling in sd units). For the limit cells the same draw is matched to
  the limit fills' times (a market entry; declared, weaker than the placebo).
- **Information only:** random entries restricted to minutes whose mid lies within the band b of its 24-hour high or
  low (fresh-extreme vicinity, no round level).

## Book, statistics, bars
- **Equal risk:** each trade's net / its symbol's IS per-trade sd of the 30-minute market-fade net (IS real minor
  cell; fixed for VAL; used for every cell and reading).
- **t** clustered by the UTC day of the trigger bar. **Power** = per-trade net Sharpe x sqrt(1.73 x trades a year),
  at the IS rate (6 years) and the VAL rate (3 years); **per-day power** = the same on daily sums (sd units).
- **LIVE** (per symbol cell and book), all of: IS net t >= 2.5; VAL net t >= 1.5; >= 6 of the 9 years net > 0; net
  > 0 at x1.5 and at +1 minute in IS and in VAL; beats >= 95 % of the placebo draws AND >= 95 % of the random seeds,
  in IS and in VAL; power at the VAL rate >= 3.
- **DEMO**, all of: IS net t >= 2.0; VAL net > 0; net > 0 at x1.5 and +1 minute in IS and VAL; beats >= 90 % of the
  placebo AND of the random seeds, in IS and VAL.
- Requiring both controls is stricter than either alone; each share is reported.
- **Chance:** max |t| of K = 24 independent normals; a sign-flip null (1,000 draws, one sign per UTC day shared by all
  24 candidate cells) on the IS mid and on the IS net; the best observed IS t of each is compared.
- **VAL / IS** ratio of the net, per cell; a VAL well below IS is read as decay.
- **C3:** for a rule that meets DEMO or LIVE numbers, the daily and monthly P&L correlation with
  `research/results/portfolio/trades_C3_gotobi_jpy_basket.csv` (IS + VAL rows) if the file exists.
- **Draft:** PREREG_DRAFT_F_<name>.md only for a rule that meets LIVE or DEMO on IS / VAL (exact rule, expected HOLD
  trades and HOLD t on the VAL size and at 0.65 of it, demo rate, stop rule, promotion rule). HOLD is not opened.

## Expected sign and size (from the mechanism, before any return)
- **Mechanism (declared by the brief):** stop-loss orders resting just beyond a fresh round level fire as market
  orders when it breaks; liquidity providers absorb them at a temporary price concession, and the price reverts
  (temporary price pressure). Osler (2003) places take-profit clusters at the round number itself, which caps the
  move, and stop-loss clusters just beyond it. Gold is the known exception (round 27: the stops cascade at $50 / $100).
- **Expected sign: fade > 0 at mid** in the four European indices (all four sides of the break), and no fade in
  US2000 (the US500 lead in round 28 went the other way: minor-level continuation +0.061 / +0.111 sd), i.e. a US2000
  fade mid <= 0 and a continuation mid >= 0.
- **Expected size:** small. Round 28's European minor cell at the stop entry was -0.051 sd (IS) / -0.012 (VAL), i.e.
  ~1 bp of reversion; UK100's 15-minute -2.96 bp was the largest. The market fade enters at the trigger close, after
  part of any reversion inside the trigger minute. Its round trip is 2.5-4.8 bp (median) on the four, so the net is
  expected near or below zero unless the reversion is several times round 28's European reading.
- **Power arithmetic:** the book has ~297 trades a year in IS and ~375 in VAL (limit ~226 / ~302). LIVE power 3 needs
  a per-trade net Sharpe of 0.132 at the IS rate and **0.118 at the VAL rate** (limit 0.152 / 0.131): about +3 bp net
  per trade at a 25 bp sd. Per symbol it needs 0.20-0.31 (ES35 0.217, F40 0.198, IT40 0.308, STOXX50 0.259 at VAL).

## Scripts (scratchpad `r29/F/code/`)
zbload.py (HOLD-guarded zbars loader), profile_zb.py, spread_factor.py, spacings_f.py, mdata.py / engine.py /
fills.py / common.py (round 28 R2's, adapted: zb source + modelled spread, limit mode, F symbol sets), fills_f.py
(fade fills, random side), events_f.py (real + 200 placebo lattices, both modes; prices only), count_tables_f.py,
test_engine.py (R2's) and test_fade.py, brute_f.py; to come: run_f.py (fills, continuation side, random entries) and
analyze_f.py.
