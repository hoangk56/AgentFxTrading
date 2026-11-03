# Stream CF hypotheses: aggressive delta (C3) and CVD divergence (C4) at prior-day Volume Profile levels

Written 2026-11-03 16:52 UTC (from `date -u`), before any return was computed. Data: BTCUSDT, ETHUSDT (develop),
SOLUSDT (once `derived/SOL_READY` exists). Eras: IS 2020-01-01..2021-12-31 (SOL from its first month), VAL
2022-01-01..2024-12-31. HOLD is not opened by this stream. Funding rows are read only while t < 2025-01-01.

## Mechanism
The prior day's POC / VAH / VAL are where the most volume traded (POC) or where the accepted value ended (VAH / VAL).
Participants who traded there defend those prices on the first return. The book says not to trade such a level blind
but to wait for a footprint confirmation: C3, aggressive traders hitting in the trade direction right at the level
(the defence is visible), or C4, price makes a new low while cumulative delta does not (the selling that should push
it lower is absent: exhaustion). The side is fixed by the side the test comes from: from above -> support -> long,
from below -> resistance -> short. If the confirmation adds information, confirmed entries beat (a) the same levels
without confirmation and (b) confirmed entries at random levels of the same day.

## Levels (declared)
- Profile of UTC day d-1: sum bid + ask per row over the 30m footprint bars (`load_fp(sym, 30)`, k = 3 bp BTC, 4 bp
  ETH, SOL k from its file) whose start lies in day d-1. Rows from the day's lowest to highest row, empty rows = 0.
- POC = row with the largest volume (lowest row on a tie, same as `fp.poc`).
- Value area 70 %: start at the POC row; repeatedly add the next row above or the next row below, whichever has the
  larger volume (tie -> the row above; when one side is exhausted take the other), until the area holds >= 70 % of the
  day's volume. VAH = top row of the area, VAL = bottom row.
- Each level is a zone of one row: [lo, hi] = `row_price(r, k, "low")`, `row_price(r, k, "high")`. Usable from 00:00
  UTC of day d, valid until 23:59 of day d (no "departure" rule: the level is known at the close of day d-1).
- Test: the first 1m bar of day d whose range, extended to the previous 1m close (so gaps count), intersects [lo, hi]:
  min(low, prev close) <= hi and max(high, prev close) >= lo. Side from the previous 1m close: > hi -> support (long),
  < lo -> resistance (short), inside the zone (only possible at 00:00) -> the level is skipped that day. One test per
  level per day; later touches are ignored.
- 1m bars: the cache is dense by trade; minutes without trades are filled with the previous close and zero volume.

## Confirmations (within 30 minutes after the test minute t)
- C3(x), x in {0.2, 0.4}: epoch-aligned 5m bars that overlap [t, t + 30 min), i.e. from the bar containing t to the
  bar containing t + 29. Delta = aggressive buy qty - aggressive sell qty of the 5m bar. Confirmed by the first bar
  with delta > 0 (long) / < 0 (short) and |delta| >= x x (buy + sell qty). Entry: market at that bar's close.
- C4 (declared swing rule): reference = the minute m* with the lowest low in [t - 30, t - 1] (first on a tie) and its
  low L*. A swing low is a 1m bar j with low_j < low of each of the 2 bars before and low_j <= low of each of the 2 bars
  after (fractal 2, known at the close of j + 2). Confirmed by the first swing low with j in [t, t + 29], low_j < L*
  and CVD higher: sum of 1m delta over (m*, j] > 0, i.e. CVD(j) > CVD(m*). The daily 00:00 reset is not applied
  between the two points (a reset inside the window would compare unrelated numbers; the sum is what "CVD higher low"
  measures). Mirror for resistance (swing high, high_j > H*, delta sum < 0). Entry: market at the close of j + 2.
- none (control, a cell): entry at the test with the common model: limit at the near edge (support: hi), filled only
  if the test minute trades >= 1 bp through it (low <= hi x (1 - 1e-4)); otherwise no trade. Maker fee.
- none-mkt (information only, not a cell): market at the close of the test minute. It is the like-for-like control
  for the confirmed cells (same order type, same costs).

## Execution (common model; changes declared)
- Stop 0.15 x ATR14 from the entry (ATR14 = mean daily true range of the 14 UTC days before the entry day, from 1m
  data). Stop fill = stop price, or the 1m open if it gaps beyond, minus slippage 1 bp (BTC, ETH) / 2 bp (SOL), taker.
- TP cells: TPV = nearest POC (of the 48 30m bars that closed before the entry) whose near edge lies beyond
  entry + 1R and within entry + 3R in the trade direction; TP = one row before that POC row (long:
  `row_price(r - 1, "low")`, short: `row_price(r + 1, "high")`), limit, maker; none within 3R -> TP = 2R. 2R = fixed
  2 x stop distance. TP fills only if a 1m bar trades through it (long: high > TP).
- Time stop: the 1m close 24 h after entry (taker + slippage). Funding paid / received at each stamp held
  (entry < stamp <= exit). One open trade per symbol per cell: a test whose entry falls while a trade is open is
  consumed without a trade.
- Ordering: market entries start at the minute after the entry close. For the limit fill minute only the stop can
  trigger; later, a minute that reaches both stop and TP is a stop.
- Fees: maker 2 bp, taker 5 bp per side. **Change (conservative):** market entries also pay the slippage (1 / 2 bp),
  like the stop; time-stop exits too. Stress: fees x1.5. One step late: confirmed cells enter at the close of the 1m
  bar after the confirmation close; `none` enters with a market order at the close of the fill minute.
- Net per trade in bp (simple return x 1e4 minus fees, slippage, funding) and in R (net bp / stop distance in bp).
  t clustered by UTC day of entry (pooled symbols share day clusters), with G / (G - 1) correction.

## Cells (8)
{C3 x = 0.2, C3 x = 0.4, C4, none} x {TPV, 2R}. Parameters are the book's / the brief's; nothing is fitted. The
"selected" rule = the cell with the highest pooled IS t; it is then checked on VAL unchanged. All 8 are reported.

## Random benchmark (>= 200 draws)
For each real level (day d-1, row r), a random level of the same width (1 row) formed on the same day, on a row drawn
uniformly from day d-1's range [lowest row, highest row] excluding the three real level rows (POC, VAH, VAL).
Test, side, confirmation and execution unchanged. 200 draws (seeded). Reported: percentile of each real cell's pooled
IS and VAL t among the draws of that cell, and the max-over-8-cells null (distribution of the best cell t per draw)
against the best real cell.

## Bars (unchanged, from BRIEF)
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive (2020-2024, 5 years: >= 4), >= 95 % of random, net > 0 IS and
VAL, > 0 at fees x1.5 and one step late, HOLD power at VAL size >= 3 (power = mean / sd per trade at VAL x
sqrt(VAL trades x 22 / 36)). DEMO: t >= 2.0 IS, net > 0 VAL, >= 90 % of random. Pooled 3 symbols for the verdict.

## Power arithmetic (before data)
Expected tests: ~3 levels x ~70 % tested per day -> ~2 tests / day / symbol; with the one-open-trade rule and holds of
hours, ~1 trade / day / symbol for C3 (C3 0.2 confirms most tests), fewer for C3 0.4 and C4 (guess 0.3 / day).
IS pooled (BTC + ETH 731 days, SOL ~480) ~ 1,900 C3 trades. sd per trade ~ 1.2 R (stop -1R, TP up to +2-3R, time
stop). t = 2.5 IS needs mean >= 2.5 x 1.2 / sqrt(1,900) ~ 0.07 R ~ 4-5 bp at R ~ 60-70 bp (BTC 2020-21). Costs:
taker entry 5 + 1 slippage + exit 2-6 bp ~ 9-12 bp ~ 0.15 R, so a gross edge ~ 0.22 R is needed. HOLD power at VAL
size: VAL ~ 3,000 trades -> HOLD ~ 1,830; power 3 needs mean / sd >= 3 / sqrt(1,830) ~ 0.07, and expecting HOLD at ~1/4
of VAL size (rounds 58-66), a decision-grade HOLD would need VAL mean / sd ~ 0.28: far above anything order flow has
shown here. Prior: none.

## Note 2026-11-03 16:57 UTC
The coordinator's BTC footprint fix (BRIEF "Fix 2026-11-03") arrived while I was checking level construction (no
return computed yet). The only BTC footprint input here is `load_fp("BTCUSDT", 30)`, reloaded after the rebuild;
1m bars are unaffected. Rules above unchanged.

## Change 2026-11-03 17:02 UTC (coordinator notice: day-sized holes in the 1m cache)
A first BTC + ETH run (1m-based ATR14, no hole rule) had already been computed; it is superseded and not reported
as a result. Only these data-hygiene changes are made, no rule or cell changes:
- ATR14 from `research/data/binance/perp_1d/<SYM>.csv` daily klines (rows >= 2025-01-01 skipped unread): mean true
  range of the 14 UTC days before the entry day; missing if any of those 14 days is absent.
- Hole = a run of > 30 consecutive minutes without trades in the 1m cache. Day d gets no levels (real or random) if
  day d-1 or day d contains a hole minute. A trade is dropped if any hole minute lies in [entry - 31 min, exit] (its
  life or its confirmation window); a dropped trade does not block later tests. Counts are in STREAM_CF.md.
