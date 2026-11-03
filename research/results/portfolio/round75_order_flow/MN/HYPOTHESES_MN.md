# HYPOTHESES_MN: multiple nodes (book setup #2), round 75

Written 2026-11-03 16:53 UTC (from `date -u`), before any return was computed. Only the npz field layout was looked at.

## Mechanism
A price row that is the POC (max-volume row) of >= n consecutive 30m bars is a price where both sides traded heavily
for an hour or more: an accepted price / inventory node. The book's claim: once price leaves the node decisively, the
participants who built positions there defend it on the first return (they add at their average price, short
covering / profit taking stalls), so the first retest gives a reaction toward the departure side. Side is fixed by the
departure: node below price (support) -> long on the first test from above; node above price -> short.
Prior: low. Rounds 4 / 17 / 63 found no flow -> return predictability; the random-level control below decides
whether any edge comes from the footprint node or just from the first retest of any level.

## Zone definition (declared)
- 30m footprint from `fp.load_fp(sym, 30)` (BTC k = 3 bp, ETH k = 4 bp, SOL k from its derived file). POC per bar by
  `fp.poc` (lowest row on a tie).
- Run: consecutive 30m bars (start minutes differ by exactly 30) with the same POC row. A zone is formed at the close
  of the n-th bar of a run (n in {2, 3}); a longer run gives one zone only (same row). A run broken by one bar and
  resumed gives a new zone (separate formation). Zone = that single row, [lo, hi] = `row_price(r)` low / high edges.
- No context filter (the book allows the node before a trend, in a trend, or in a rejection).
- Departure: count the full 30m bars after the formation bar that lie entirely above hi (bar low > hi) and those
  entirely below lo (bar high < lo); bars need not be consecutive. The first side to reach 2 bars sets the zone
  type (above -> support, below -> resistance); the zone becomes usable at the close of that 2nd bar. Departure bars
  must close before expiry = formation-bar close + 336 x 30 min.
- First test: the first 1m bar starting at or after the usable time and before expiry whose range reaches the near
  edge (support: low <= hi; resistance: high >= lo) consumes the zone. Fill only if that minute trades >= 1 bp
  through (support: low <= hi (1 - 1e-4); resistance: high >= lo (1 + 1e-4)); otherwise the zone is gone, no trade.

## Execution (common model of the BRIEF, with the declarations below)
- Entry = limit at the near edge (long at hi, short at lo), maker 2 bp.
- ATR14 = mean of the true ranges of the 14 UTC days before the entry day, daily bars built from the 1m bars (same
  data as the trades; days with < 14 prior days -> no trade). Stop = entry -/+ 0.15 ATR14.
- Fill minute: only the stop can trigger (low <= stop for a long -> exit at the stop price).
- Later minutes up to the time stop: stop fill = stop price, or the 1m open if the open is already beyond it, minus
  slippage 1 bp (BTC, ETH) / 2 bp (SOL), taker 5 bp. TP (limit, maker 2 bp) only if the minute trades through it
  (high > TP for a long, low < TP for a short). A minute reaching both: stop first.
- Time stop: close of the last 1m bar with start <= fill minute + 1440, taker 5 bp, no slippage.
- TP cells:
  - TPV: POC rows of the 48 completed 30m bars before the entry minute's bar. For a long, candidate TP = lower edge
    of the row one below each POC row (`row_price(r - 1)`); for a short, upper edge of the row one above
    (`row_price(r + 1, "high")`). Keep candidates with 1R <= |TP - entry| <= 3R on the trade side; take the nearest.
    None -> TP = 2R. (I apply the 1R test to the TP price after the one-row offset, so R:R >= 1 always.)
  - 2R: TP = entry +/- 2 x stop distance.
- Funding: every stamp in research/data/binance/funding/<SYM>.csv with fill minute < stamp <= exit minute
  (minute resolution): long pays rate, short receives it.
- One open trade per symbol per cell: zones' potential trades are sorted by fill minute (ties: earlier formation
  first), a trade is taken only if its fill minute is after the exit minute of the previous taken trade; others are
  consumed without a trade.
- Net bp per trade (log-free simple return x 1e4 of the price path, minus fees, slippage, funding) and net in R
  (net bp / stop distance bp).
- Stress: fees and slippage x 1.5. One step late: market entry at the close of the fill minute (taker 5 bp), stop and
  TP price levels unchanged, path starts at the next minute; if that close is already beyond the stop or the TP, the
  trade exits at the next minute's open (stop rules, taker). R stays the planned stop distance.
- Eras by fill minute: IS 2020-01-01..2021-12-31 (SOL from 2020-09), VAL 2022-01-01..2024-12-31. HOLD never loaded
  (fp.py cuts at 2025-01-01; I also cut the funding file and daily bars there).

## Cells (4) and selection
n in {2, 3} x TP in {TPV, 2R}. Book parameters only, no other knob. The candidate is the cell with the best pooled IS
t (three symbols pooled, t clustered by UTC day of the fill); VAL is read unchanged for all four cells. Each symbol
is reported separately. Max-over-cells null: in each random draw take the max pooled t over the 4 cells; report the
percentile of the real best-cell t in that distribution.

## Random benchmark
For every real zone (each n), 200 draws: a 1-row zone formed in the same bar, its row drawn uniformly from the rows
covering [min low, max high] of the 48 30m bars ending at the formation bar (inclusive), excluding the real row.
Departure, first test, fill rule, execution, one-trade filter and costs unchanged. Percentile = share of draws whose
pooled net t (same cell, same era) is below the real t. Bar uses the 2020-24 (IS + VAL) t; IS and VAL percentiles are
reported too.

## Statistics
t clustered by UTC day: t = sum(x - mean) per day... i.e. se^2 = sum_days (sum_{i in day} (x_i - mean))^2 / N^2.
Years positive over 2020-2024 (SOL 2020 counted from September). Bars from the BRIEF unchanged.

## Power arithmetic (before data)
Stop ~0.15 x daily ATR: BTC ~3-4 % ATR -> ~45-60 bp stop. Round trip cost ~4 bp (TP), ~8 bp (stop) => ~0.1-0.15R of
cost per trade. Guess 200-500 trades / symbol / year in VAL (n = 2), so pooled VAL ~2,000-4,000 trades, HOLD
(x 22/36) ~1,200-2,400. With a per-trade sd ~1.1R, power 3 needs net mean >= 3 / sqrt(1,200..2,400) x 1.1R
~0.07-0.095R per trade net, i.e. a gross reaction of ~0.2R beyond the random-level first retest. Expect HOLD t at
~1/4 of VAL size (rounds 58-66), so even a passing VAL t ~3 would project HOLD t ~0.75: I will say so.
n = 3 has roughly 1/3-1/5 the trades of n = 2, so it needs ~2x the per-trade edge for the same power.

## Addendum 2026-11-03 16:57 UTC (from `date -u`), still before any return was looked at
- A first BTC plumbing run (counts only, no return read) used the BTC footprint that the coordinator has since
  declared void (fp_key carry bug); its output was deleted. Everything is rerun on the rebuilt derived files, and the
  code now asserts that every 30m bar's POC row lies inside the bar's [low, high] rows.
- The 1m cache is not gap-free: BTC misses 23 whole UTC days (2020-04/05, 2020-11, 2022-08..11), ETH 7 (2022-08..11).
  Two hygiene rules, applied identically to real and random zones:
  1. ATR14 comes from the daily klines `research/data/binance/perp_1d/<SYM>.csv` (complete, cut at 2025-01-01),
     true range on consecutive days, mean of the 14 days before the entry day. (Replaces "daily bars built from 1m
     bars", which would void 14 days after every gap.)
  2. A zone whose life from its formation bar start to its test minute contains a 1m-data gap > 30 minutes is
     dropped (its first test may sit in the hole), and so is a trade whose window from the fill minute to its
     24 h time-stop minute contains such a gap (path unknown). Counts dropped are reported.
