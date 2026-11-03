# Round 75 stream TF: trades filter (book setup #3), hypotheses

Written 2026-11-03 16:52 UTC (from `date -u`), before any return was computed. The only data looked at before this
file: big-trade counts per month and the implied monthly Q for BTC / ETH (no prices after a zone, no returns).

## Mechanism
A single aggressive order of unusual size (an aggTrade, i.e. one taker order, >= Q notional) marks a price where a
large participant traded. The book (setup #3, "trades filter") claims such a price becomes support / resistance: when
price leaves the level and returns for the first time, the large participant (or others who saw the print) defends it
and price reacts. Direction comes from the side of the test (from above -> long), not from the side of the big trade.
If the effect exists it should beat the first retest of a random level of the same width (random benchmark).

## Event (zone formation)
- Big trades: `fp.load_big(sym)` (aggTrades >= $100k notional, cut before 2025-01-01).
- Q per calendar month m = the N-th largest notional among the aggTrades of month m - 1, N = R x (days in month m - 1),
  R in {5, 10} (point in time; "R big trades per day" counts aggTrades, not zones). A month whose previous month has
  fewer than N stored trades (>= $100k) uses Q = $100k; every such month is listed in STREAM_TF.md. The first cached
  month of each symbol (BTC / ETH 2020-01, SOL 2020-09) has no previous month: no zones that month. For BTC / ETH the
  floor never binds (checked: ETH 2020-01 has 14 stored trades per day).
- Big trade -> row = (floor(1e4 ln p)) // k (k of the 30m footprint: BTC 3, ETH 4, SOL from its derived file).
- Merge: big trades in the same 30m bar whose rows are adjacent (a chain of rows with gaps <= 1 row, i.e. r and r + 1)
  form one zone [lo row, hi row]. Different bars are never merged (the same row in two bars gives two zones).
- Zone price edges: lo = `row_price(lo row, k, "low")`, hi = `row_price(hi row, k, "high")`. Formation bar = the 30m bar
  of the trades. Each zone keeps its counts of aggressive-buy and aggressive-sell big trades (information split).

## Departure, test, execution (common model of the BRIEF, with the details it leaves open)
- 30m and 1m bars are put on dense UTC grids (missing bars = no data, never "beyond" and never "touching").
- Departure: counting 30m bars after the formation bar (not necessarily consecutive), the zone becomes a support at
  the close of the 2nd bar with low > hi, a resistance at the close of the 2nd bar with high < lo; whichever side
  reaches 2 bars first wins. Bars inside / across the zone in between are allowed. Must happen before expiry.
- Expiry: formation bar close + 336 x 30 minutes. The test minute must start before expiry.
- First test: the first 1m bar starting at or after the usable time whose range reaches the near edge (support: low <=
  hi; resistance: high >= lo) consumes the zone. Fill only if that minute trades >= 1 bp through (support low <= hi x
  (1 - 1e-4); resistance high >= lo x (1 + 1e-4)); entry = the edge price (limit, maker). Not filled -> no trade, zone
  gone.
- Stop = 0.15 x ATR14 from entry, ATR14 = mean of the true range of the 14 UTC days before the entry day (days built
  from the 1m bars; a trade without 14 prior days is dropped). Stop fill = stop, or the 1m open if it gaps beyond,
  then 1 bp (BTC, ETH) / 2 bp (SOL) slippage against, taker fee.
- TP cells:
  - TPV: POC rows (`fp.poc`) of the 48 completed 30m bars before the entry (bars ending at or before the fill minute
    start). Long: candidate POC rows whose lower edge > entry + 1R; take the lowest; TP = one row below its lower edge
    (`row_price(p - 1, k, "low")`), maker. If no candidate or the candidate's lower edge > entry + 3R -> TP = entry + 2R.
    Short mirrored: POC rows whose upper edge < entry - 1R, take the highest, TP = `row_price(p + 1, k, "high")`;
    none within 3R -> entry - 2R.
  - 2R: TP = entry +- 2 x stop distance.
  TP fills only if a 1m bar trades through it (long: high > TP), at TP, maker.
- Time stop: close of the 1m bar starting at fill minute + 1439 (24 h after the start of the fill minute), taker. If
  that minute is missing, the last minute before it.
- Same-minute rule: in the fill minute only the stop can trigger; later, a minute that reaches both stop and TP is a
  stop.
- One open trade per symbol per cell: zones are processed in order of test minute (ties: earlier formation first); a
  zone whose test minute is <= the exit minute of the open trade is consumed without a trade.
- Fees per side: maker 2 bp (entry, TP), taker 5 bp (stop, time stop, late entry). Funding: every funding stamp in the
  csv with fill-minute start < stamp <= exit-minute start; a long pays the rate (short receives). The funding csv is
  cut at t < 2025-01-01 when read.
- Era of a trade = era of its fill minute. VAL trades must fill before 2024-12-31 00:00 UTC (24 h window stays inside
  VAL); later tests are ignored.
- Stress: fees x 1.5 (maker 3, taker 7.5; slippage unchanged). One step late: the same trades enter with a market order
  at the close of the fill minute (taker 5 bp); stop and TP keep the absolute prices of the base trade; the fill
  minute's own range is then not used (exits start the next minute; a gap beyond the stop fills at that minute's open).
- Net per trade in bp (of entry price) and in R (net bp / stop distance bp). t clustered by UTC day of the fill:
  t = sum(x) / sqrt(G/(G-1) x sum_d (S_d - n_d xbar)^2).

## Cells (4, declared)
R in {5, 10} x TP in {TPV, 2R}. Pooled verdict over BTC, ETH, SOL (all trades of the three symbols, day clusters
across symbols); each symbol reported. The cell for the verdict is picked on IS (best pooled IS t); VAL checks it
unchanged, and all four are reported in both eras.

Information only (no verdict): zones split by the side of their big trades (all aggressive-buy, all aggressive-sell,
mixed), and within that by test direction (support / resistance).

## Random benchmark (required)
For each real zone (of the cell's R), a random zone of the same width in rows, formed in the same bar, centred on a row
drawn uniformly from the rows of that bar's 48-bar range (the 48 bars ending with the formation bar, lowest low row to
highest high row) excluding the real zone's rows; the random zone's rows = [c - floor((w - 1) / 2), ... + w - 1].
Departure, first test, execution, one-open-trade and costs unchanged. 200 draws (seeded). Report the percentile of the
real pooled net t among the 200 random pooled t, per cell and era, and the max-over-4-cells null (per draw the max t over
the 4 cells, compared with the best real cell).

## Bars (unchanged, from the BRIEF)
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % of random, HOLD power at VAL size >= 3, positive
at costs x 1.5 and one step late, net > 0 IS and VAL. DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % of random.
Power = VAL net mean / sd per trade x sqrt(HOLD trades), HOLD trades = VAL pace x 22 / 36. Rounds 58-66 suggest HOLD t
~1/4 of VAL size; I report power both at VAL size and at 1/4 of it.

## Power arithmetic (before data)
Expect ~3-8 zones per day per symbol after merging, of which perhaps half depart and get tested within 7 days, and the
one-open-trade rule (trades last up to 24 h) keeps about 1 trade per day per symbol: IS ~700 (BTC, ETH) + ~480 (SOL),
VAL ~1,000 per symbol (~3,000 pooled). HOLD ~ 3,000 x 22 / 36 ~ 1,830 trades. Power 3 needs net / sd >= 3 / sqrt(1,830)
= 0.070 per trade; with sd ~1.2 R that is ~0.085 R net (~5 bp at a ~60 bp BTC stop). At 1/4 of VAL size the VAL edge
would have to be ~0.34 R per trade, which no retest effect of this kind has shown before; so a LIVE verdict would need a
very large VAL effect.

## Pitfalls I guard against
- Zone and Q only from closed bars / the previous month; departure counted on closed bars; POCs for TPV from bars that
  closed before the fill.
- Limit fill requires 1 bp through; no fill = no trade.
- No 2025-26 data: fp.py cuts, funding csv cut on read, daily ATR from the 1m cache (not perp_1d, which runs into
  2025-26).

## Addendum 2026-11-03 16:58 UTC (before any return was read)
- The coordinator rebuilt `derived/BTCUSDT_tf30` (BTC bucket carry above $22,026). All TF runs that produce returns
  were started after the rebuild; checked: every BTC / ETH 30m POC row lies inside its bar's low / high rows.
- Big trades are read month by month from the same arrays as `fp.load_big` (same HOLD cut), keeping only trades >= the
  month's Q, because `load_big` holds all ~34M stored BTC trades (> 1 GB). Same definition, less memory.

## Addendum 2 2026-11-03 17:10 UTC (coordinator notice on 1m holes; no TF return read yet)
- The 1m cache has day-sized holes (Binance monthly files skip days). Hole = > 30 consecutive missing minutes.
- ATR14 now from `research/data/binance/perp_1d/<SYM>.csv` daily klines (rows cut at t < 2025-01-01 on read), true
  range of UTC days, mean of the 14 days before the entry day.
- A candidate trade is dropped (it does not block other trades either) when the span from its zone's formation bar
  start to its exit minute contains any hole minute. Counts per symbol / cell in STREAM_TF.md and out/<SYM>_meta.txt.
- Monthly Q: N = round(R x days actually present in the previous month), days present = present 1m bars / 1440.
- The BTC / ETH runs made before this addendum are discarded unread (overwritten).
