# Round 75 stream AB: hypotheses (written before any return)

Written 2026-11-03 16:52 UTC (from `date -u`). No return has been computed when this file is written. Data checked so
far: file shapes only (BTC k = 3 bp, ETH k = 4 bp on both tf30 and tf5; same row grid on 5m and 30m).

## Mechanism
Trader Dale confirmations #1 and #2 at Volume Profile levels. Yesterday's POC / VAH / VAL are prices where the market
accepted (POC) or stopped accepting (VA edges) value. When price comes back to such a level for the first time on the
next day, a large passive participant defending it shows on the footprint as a heavy cell on the passive side
(C1: big bids at support = aggressive sellers filled by a passive buyer) or as a cell heavy on both sides while price
does not go on (C2: absorption). The book's best case adds aggressive flow in the trade direction afterwards (bonus).
If passive size at the level carries information about the next hours, the long-after-big-bid (short-after-big-ask)
trade earns more than the same trade without the confirmation and more than the same confirmation at a random level.
Side is fixed by the book before data: support (level reached from above) -> long, resistance -> short.

## Levels and tests (own code, from the BRIEF's CF definition)
- Day profile of UTC day d - 1: sum of bid + ask per row over the 30m footprint bars of that day (rows from the lowest
  to the highest row traded; rows with no trade count as 0). POC = row with the largest volume (lowest row on a tie).
- Value area 70 %: start at the POC row; repeatedly compare the next untaken row above and the next untaken row below,
  add the larger one (tie -> above; if one side is exhausted add the other), until the taken volume >= 70 % of the
  day's total. VAH = highest taken row, VAL = lowest taken row. Levels of day d: POC, VAH, VAL (one row each, pooled).
  A day d - 1 with fewer than 40 of its 48 30m bars present gives no levels (outage days).
- Test: level row L covers [lo, hi] = [row_price(L), row_price(L, "high")]. State of minute t = +1 if its close > hi,
  -1 if close < lo, 0 inside. The state before 00:00 of day d is that of the last minute of day d - 1. The test is the
  first 1m bar of day d with (state of the previous minute = +1 and low <= hi) -> support, or (previous state = -1 and
  high >= lo) -> resistance. One test per level per day (the first); no test on day d -> nothing. A day that opens
  inside the row waits until a minute closes outside, then the next reach is the test.
- No departure rule (the CF definition replaces the common model's "2 bars beyond"; the level is usable from 00:00 of
  d and expires at the end of day d).

## Confirmations (5m footprint, same k rows as 30m)
- Zone rows for the check: L - 1, L, L + 1.
- Window: the 5m bar containing the test minute (B0) and the next 5 bars (B0..B5, the last closes <= 30 min after
  the test). Bars missing from the data are skipped.
- Reference: mean of all non-zero side values (each non-zero bid value and each non-zero ask value of every row is one
  "cell") of the 12 5m bars before B0 (all rows). Fewer than 6 of those 12 bars present -> no confirmation possible.
  Declared reason: the footprint shows bid x ask as two numbers per row, and C1 compares one side value with it.
- C1 (big limit), threshold m: support -> some zone row in bar Bi has bid >= m x ref; resistance -> ask >= m x ref.
  Confirmation at the close of the first such Bi.
- C2 (absorption), m: some zone row in Bi has bid >= m x ref and ask >= m x ref, and Bi closes inside the zone or on
  the level's side (support: close >= low edge of row L - 1; resistance: close <= high edge of row L + 1). First such Bi.
- Bonus, m: a bar Bi meeting C1 or C2, then a bar Bj, i < j <= i + 3 (next 15 minutes, may run past B5), with delta
  (sum ask - sum bid over all rows) > 0 for support / < 0 for resistance. Confirmation at the close of the earliest
  such Bj.
- m in {4, 8}.

## Execution (common model, changes marked)
- Entry: market (taker 5 bp) at the close of the confirming 5m bar = close of its last 1m bar present. Stop / TP are
  checked from the next minute on.
- Stop: 0.15 x ATR14 from entry, ATR14 = mean daily true range of the 14 UTC days before the entry day, computed from
  the 1m bars. Stop fill = stop price, or the 1m open if it gaps beyond, minus slippage 1 bp (BTC, ETH) / 2 bp (SOL),
  taker 5 bp.
- TP cells: TPV = nearest POC of the 48 completed 30m bars before entry whose near edge lies beyond entry + 1R (long:
  low edge of the POC row > entry + R), TP one row before it (long: low edge of row POC - 1; short: high edge of row
  POC + 1), maker limit, fills only if a 1m bar trades through it; if that TP is beyond 3R or no such POC -> TP = 2R.
  2R = fixed 2 x stop distance. If a minute reaches both stop and TP, the stop comes first.
- Time stop: 1m close 24 h after entry, taker. Funding at each funding stamp in (entry, exit]: long pays rate.
- One open trade per symbol per cell; a confirmation while a trade is open is skipped (the level is used up).
- Market entries pay no slippage in the base case (common model text: slippage on stop fills only); the x1.5 fee stress
  is the cost check, and a variant with +1 bp / 2 bp slippage on market entries and time stops is reported as
  information.
- One step late: enter at market at the close of the 1m bar after the confirming bar's close; stop and TP keep the
  same prices as the on-time trade (risk recomputed for R units).

## Cells (12, the verdict set)
{C1, C2, bonus} x m {4, 8} x TP {TPV, 2R}. Pooled BTC + ETH + SOL; each symbol reported.

## Controls (not cells)
- N0 (no confirmation): the same tests, limit at the near edge of the level row (support: hi), filled only if the test
  minute trades >= 1 bp through it (low <= hi x (1 - 1e-4)), only the stop can trigger in the fill minute; maker 2 bp
  entry. x TP {TPV, 2R}.
- N0m (information): market entry at the close of B0 (the earliest moment a confirmation could fire).
- Random levels: for each real level of day d, a level row drawn uniformly from day d - 1's traded rows [min row, max
  row], excluding the real zone rows L - 1..L + 1; tests, confirmations, execution unchanged. 200 draws (one draw =
  one random row per real level, all symbols). Per cell: percentile of the real pooled net t among the 200 random
  pooled net t. Max-over-cells null: the distribution of max t over the 12 cells across draws vs the real max.
  The random percentile is computed in IS and in VAL separately; the LIVE / DEMO random bar must hold in both.
- Trades whose 24 h window runs past 2024-12-31 are cut at the last 2024 minute (no 2025 data exists in the cache).

## Eras, statistics, bars
- IS 2020-01-01..2021-12-31 (SOL from its first month; first usable day needs 14 prior days for ATR), VAL
  2022-01-01..2024-12-31, by entry time. HOLD not touched (fp.py cuts at 2025-01-01).
- Parameters fixed above; there is no IS tuning beyond the 12 declared cells. A cell selected on IS is read on VAL
  unchanged.
- t clustered by UTC entry day. Net bp per trade and in R. Years 2020..2024 positive (pooled): need >= 2/3.
- LIVE: IS t >= 2.5, VAL t >= 1.5, net > 0 IS and VAL, positive at fees x1.5 and one step late (IS and VAL), >= 2/3
  years positive, random percentile >= 95 %, HOLD power >= 3 where power = VAL net mean / sd x sqrt(n_VAL x 22 / 36).
- DEMO: IS t >= 2.0, VAL net > 0, random percentile >= 90 % (plus the common conditions).
- Expect HOLD t at ~1/4 of the VAL size (lesson of rounds 58-66); reported next to the power.

## Power arithmetic (before data)
- About 3 levels per day per symbol, perhaps 50-70 % tested on day d -> ~1.5-2 tests / day / symbol. Confirmation
  rates guessed 20-60 % (m = 4) and 5-30 % (m = 8). Pooled IS (BTC, ETH 2 y + SOL 1.3 y ~ 1,900 symbol-days) gives
  ~300-1,500 trades per cell; VAL (3 symbols x 3 y ~ 3,300 symbol-days) ~500-3,000.
- R = 0.15 x ATR14 ~ 40-70 bp on BTC / ETH, more on SOL. Round-trip cost ~ 7-11 bp (taker in, maker or taker+slip out)
  ~ 0.15-0.25 R. Per-trade sd ~ 1-1.3 R.
- Power >= 3 with n_VAL = 1,500 needs HOLD n ~ 917 and mean / sd >= 0.10, i.e. net ~ +0.1-0.13 R (~5-8 bp) per trade
  after costs; IS t 2.5 with n ~ 800 trades needs mean / sd ~ 0.09 too. So the confirmation must add a gross edge of
  about 0.3 R per trade over zero. Earlier signed-flow tests in this repo gave ~1/20 of costs; prior is low.

## What would kill it
- No cell with IS t >= 2: none.
- Confirmation cells not better than N0 at real levels, or real-level t below the 90th / 95th percentile of random
  levels: the footprint confirmation or the VP level carries nothing beyond a generic first retest.

## Notes added before any return
- 2026-11-03 ~17:00 UTC: coordinator notice, BTC footprint rebuilt (carry bug). This stream had read only file shapes;
  all runs use the rebuilt `derived/BTCUSDT_tf30/tf5` via `fp.load_fp`; no `fp_key` read directly.
- One step late, final form (set before any return): enter at the close of the next 1m bar with the stop and TP at the
  same distances from the late fill (not the same prices), so no trade is dropped.
- 2026-11-03 17:02 UTC: coordinator notice on day-sized holes in the 1m cache (before any return was read;
  the first ETH / BTC run made at 17:1x UTC was discarded unread and rerun). Changes: ATR14 now from
  research/data/binance/perp_1d daily klines (rows >= 2025-01-01 cut on load; TR with the previous kline close; mean of
  the 14 days before the entry day). Hole = run of > 30 missing 1m bars. Day d gets no levels if day d - 1 or day d
  touches a hole. A trade is dropped (before the one-open filter) if a hole lies between 60 min before its entry and
  its exit. Counts: BTC 24 holes, 610 h, 28 UTC days touched; ETH 7 holes, 170 h, 9 days; SOL: in STREAM_AB.md.
