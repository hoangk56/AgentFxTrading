# Stream VC (round 75) hypotheses: volume clusters in a trend leg or a rejection, first retest

Written Tue Nov 3 16:52:56 UTC 2026 (from `date -u`). At this point I have read BRIEF.md, the method file, fp.py and
looked at array shapes of BTCUSDT minutes / tf30 footprint (row counts, dtypes, gaps). **No zone, no test and no
return has been computed.** HOLD (2025-01-01..) is never read: only fp.py loaders (cut at 2025-01-01) and the funding
CSV filtered to t < 2025-01-01 are used. Daily ATR is built from the 1m bars of fp.py (not from perp_1d, which holds
2025-26 rows).

## Mechanism and side (fixed before data)
- **Trend (book setup #1, VP2):** inside a directional leg, the price band where unusually much volume traded is where
  the trend's buyers (up leg) built positions. On the first return they defend their average price and late sellers
  who sold into the leg cover there, so the band acts as support. Up leg -> support -> **long**; down leg -> resistance
  -> **short**.
- **Rejection (book setup #1R, VP3):** a fast swing that reverses fast leaves its heaviest volume where the reversal
  started; the absorbing side defends it on the first retest. Trade **in the direction of the reversal** (bullish
  reversal -> support -> long; bearish -> resistance -> short).
- A zone is traded only on the side given by its leg (an up-leg cluster is only ever a support; if price leaves it
  downward it never departs and is never traded).

## Events (30m bars = fp.bars(minutes, 30), footprint = fp.load_fp(sym, 30), k = 3 / 4 / SOL's k bp rows)
- **ATR14** (price units) for a day d: mean of the UTC-day true range (max(h, prev c) - min(l, prev c), days built from
  the 1m bars) of the 14 available days before d. Legs use the ATR14 of the day containing the leg's last bar start;
  stops use the ATR14 of the entry day. No ATR (first 14 days) -> no event / no trade.
- Bars must be consecutive (start step 30 min) inside a leg window; windows with a missing bar are skipped.
- **Trend leg:** 8 consecutive 30m bars i0..i0+7 with |c(i0+7) - o(i0)| >= 0.5 x ATR14 and >= 6 of the 8 bars closing
  in the leg direction (c > o for an up leg, c < o down). Scanned forward in time, greedy and non-overlapping: when the
  window ending at bar j qualifies it is a leg, and the next window must start at j + 1.
- **Rejection, bullish** (mirror for bearish), confirmed at the close of bar e: L = the bar with the lowest low among
  e-3..e-1 (lowest index on a tie), low(e) > low(L); swing down: max(high(L-3..L)) - low(L) >= 0.4 x ATR14 (swing spans
  <= 4 bars); reversal: c(e) - low(L) >= 0.4 x ATR14 (reversal leg L..e, 2-4 bars). e is the first bar where this
  holds; the leg is bars L..e. Greedy non-overlapping: the next rejection must have L' > e. If a bullish and a bearish
  rejection are both confirmed at the same e (both conditions true), both are kept.
- **Profile / cluster:** sum of the leg bars' footprint cells (bid + ask) by row, over every row from the leg's lowest
  to highest row (rows without trades count as 0). Median row volume = median over those rows. Cluster = the max-volume
  row (lowest on a tie) plus the contiguous rows around it with volume >= c x median, c in {2, 3}; the max row must
  itself be >= c x median, else no zone.
- **Extreme-row exclusion (declared reading of the brief):** if the cluster contains the profile's lowest or highest row
  (the leg's first / last bar extremes: a turning point, not a cluster), the leg gives no zone. Counts reported.
- Zone [lo, hi] = row_price(low row, low edge), row_price(high row, high edge). Formation = close of the leg's last bar.

## Execution (common model of the brief, unchanged except where stated)
- Usable at the close of the 2nd full 30m bar after the formation bar that lies entirely beyond the zone (support: bar
  low > hi; resistance: bar high < lo); touches before that are ignored (literal common model). Expires 10,080 min
  (336 bars) after formation; usable time must be before expiry.
- First test = first 1m bar with start >= usable time and before expiry whose range reaches the near edge (support:
  low <= hi). It consumes the zone. Filled only if low <= hi x (1 - 1e-4) (short: high >= lo x (1 + 1e-4)); entry =
  limit at hi (support) / lo (resistance), maker 2 bp.
- One open trade per symbol per cell; a zone whose test minute is <= the open trade's exit minute is consumed without
  a trade. Two zones tested in the same minute: the earlier-formed one trades (the other is consumed).
- Stop distance D = 0.15 x ATR14(entry day). Stop fill = stop, or the 1m open if it gaps beyond, minus slippage 1 bp
  (BTC, ETH) / 2 bp (SOL), taker 5 bp.
- TP cells: **TPV**: POC rows (fp.poc) of the 48 completed 30m bars before the entry minute; long: TP_r = low edge of row
  r - 1 (one row below the POC row); candidates with entry + D <= TP_r <= entry + 3D; TP = the nearest (smallest);
  none -> TP = entry + 2D. Short mirror: TP_r = high edge of row r + 1, entry - 3D <= TP_r <= entry - D, nearest.
  **2R**: TP = entry +- 2D. TP is a maker limit, filled only if a 1m bar trades through it (high > TP long, low < TP
  short).
- In the fill minute only the stop can trigger (low <= stop -> exit at stop - slippage). Later minutes: stop checked
  before TP. Time stop: if neither, exit at the close of the last minute with start <= t0 + 1,440 (taker 5 bp).
- Funding: every funding stamp in the CSV with entry time (t0 x 60 s) < stamp <= exit time; long pays rate x 1e4 bp,
  short receives it. Trades whose 24 h window passes the end of the 2024 data are dropped.
- Net bp = side x (exit / entry - 1) x 1e4 - fees - funding; also in R (net bp / (D / entry x 1e4)).
- **Costs x1.5:** maker 3, taker 7.5 bp. **One step late:** for the same filled tests, enter with a market order at
  the close of the fill minute (taker 5 bp), stop / TP recomputed from that entry with the same D, the trade starts in
  the next minute (both can trigger there, stop first), time stop t0 + 1,440.
- Era of a trade = its entry minute (IS 2020-2021, VAL 2022-2024). t clustered by UTC entry day (CR1, days shared
  across symbols when pooled).

## Random benchmark (required)
For each real zone (w rows), a zone of the same width formed at the same bar, centred on a row x drawn uniformly from
the rows spanned by the 48 30m bars ending at the formation bar, x not in the real zone's rows (low row = x - (w-1)//2);
same side as the real zone; departure, first test, execution unchanged. 200 draws per (setup, c), both TP cells from the
same draw. Reported: percentile of the real pooled net t among the 200 random pooled net t (per era), and the
max-over-8-cells null (95th percentile of the max IS t over cells per draw).

## Cells (8, declared) and selection
{trend, rejection} x c {2, 3} x TP {TPV, 2R}. Book parameters: c = 3 is my reading of "much heavier than around"
(method file's example), c = 2 the looser one. Verdict per rule (trend, rejection): the cell with the highest pooled
IS t of its 4 is the rule; it is checked on VAL unchanged. All 8 cells are reported in every era / symbol.

## Bars (unchanged)
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive (years 2020-2024 of the pooled net), random >= 95 %, power
>= 3. DEMO: t >= 2.0 IS, net > 0 VAL, random >= 90 %. Both: net > 0 IS and VAL, > 0 at costs x1.5 and one step late.

## Power arithmetic (before data)
Power = (VAL net mean / sd per trade) x sqrt(VAL trades x 22 / 36). Example: with 1,000 pooled VAL trades (611 HOLD
trades) power 3 needs mean / sd >= 0.12 per trade, i.e. with sd ~ 1.2 R (stop / 2R / time stop mix) a net mean of
>= 0.15 R. With 300 VAL trades it needs 0.22 per trade. Rounds 58-66 suggest HOLD t ~ 1/4 of VAL t; that will be stated
with any candidate.

## Pitfalls I will check
- Cluster / leg only known at the leg's last bar close; departure bars must close before use; POCs for TPV only from
  bars closed before entry.
- One-trade-per-cell applied after zones are tested in time order.
- SOL only after research/data/footprint/derived/SOL_READY exists.

## Addendum Tue Nov  3 16:57:11 UTC 2026 (before any return was read)
- The first BTC run (16:55 UTC) used the pre-fix BTC footprint (bucket carry, BRIEF fix note). Only zone / test counts
  were printed (no return looked at); its outputs were deleted. All BTC numbers come from the rebuilt
  derived/BTCUSDT_tf30.npz loaded with fp.load_fp. ETH was unaffected.
- Hand trace of 4 ETH trend trades (code/check.py) matches the rules (departure, first test, fill, stop, TPV, fees).
- Random draws seeds: BTC 7501, ETH 7502, SOL 7503 (numpy default_rng), 200 draws.

## Addendum 2 Tue Nov  3 17:02:48 UTC 2026 (coordinator data notice; rules otherwise unchanged)
- What I had seen before this change: the pooled BTC + ETH **IS** table of the first full run (1m-built ATR, no hole
  rule). No VAL number and no SOL file had been read. That run is superseded; no parameter, cell or selection rule is
  changed because of it.
- **ATR14 now from research/data/binance/perp_1d/<SYM>.csv** (rows with t >= 2025-01-01 dropped right after reading,
  never used): TR = max(h, prev c) - min(l, prev c), ATR for day d = mean TR of the 14 kline days before d (needs 14).
  Used for leg thresholds (day of the leg's last bar) and stops (entry day), as before.
- **Holes:** a hole is a gap > 30 min between consecutive 1m bars of the cache (BTC 24 holes / 610 h, ETH 7). A zone is
  dropped (no trade, it does not consume or block anything) if [start of its leg's first bar, first-test minute +
  24 h] overlaps a hole; counts per cell in out/<SYM>_counts.json ("hole_dropped"). Leg windows already require
  consecutive 30m bars. Random zones use the same rule with the real zone's leg start.
