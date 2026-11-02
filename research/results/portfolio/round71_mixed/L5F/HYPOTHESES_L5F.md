# Round 71 stream L5F: quarter-hour opening taker imbalance (hypotheses)

Written 2026-11-01 17:49 UTC (from `date -u`), before any kline was downloaded and before any return was computed.
Forward-only stream (brief): if a cell passes the IS / VAL bars, write PREREG_DRAFT_L5F_<name>.md as a forward
registration from 2026-10-30 and stop. HOLD (2025-01-01..) is never requested, loaded or summarised.

## Source and mechanism
- arXiv 2607.09426 ("The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in
  Cryptocurrency Futures", v2 2026-07-16). Read from the arXiv abstract + HTML pages (2 fetches, no WebSearch):
  six Binance USDT-M perps (BTC, ETH, XRP, SOL, DOGE, ADA), trades 2021-01-01..2024-10-31, out-of-sample forecasts
  from 2021-07. Order imbalance = signed (isBuyerMaker) volume / total volume in the **first 10-second interval** of
  minutes :00 / :15 / :30 / :45. Medium-horizon coefficient is **positive (continuation)** at 4-12 h (peaks 8-12 h);
  first half hour reverses. The paper reports no strategy and no net returns; its sign-weighted forecast target is
  ~0.5 bp per boundary.
- Mechanism: periodic execution algorithms (TWAP / scheduled rebalancers) start child orders at clock marks; an
  unusually one-sided opening burst reveals a large parent order that keeps executing for hours, so price drifts
  in the same direction (order-splitting continuation, Kyle-type information in flow).
- Contamination note: the paper's sample overlaps our IS and VAL, so VAL is not out of sample relative to the
  paper's discovery. That is why the brief makes this forward-only.

## Data
- data.binance.vision futures/um monthly 1m klines, 2020-01..2024-12, keeping open time, open, close, base volume
  (col 5), taker-buy base volume (col 9), quote volume. Rows with open_time >= 2025-01-01 dropped at parse.
- Coins: BTCUSDT, ETHUSDT + the four largest other perps by 2020-01-01..2024-12-31 quote volume in local
  binance/perp_1d (computed before writing this file): **SOLUSDT, XRPUSDT, DOGEUSDT, BNBUSDT** (ADA is 7th). The paper
  uses ADA instead of BNB; I follow the brief. Disclosed: picking by 2020-24 volume uses VAL-era information
  (SOL / DOGE were small in early 2020); all four were top-10 for most of 2021-24.
- Funding: local binance/funding/<SYM>.csv (cut < 2025-01-01).
- Only 1-minute resolution is available keyless at this scale, so the signal is the first **minute**, a diluted
  version of the paper's first 10 seconds (the first minute holds the burst plus ~50 s of ordinary flow).

## Signal (fixed)
- For coin c and quarter-hour mark q (96 per UTC day), bar = the 1m kline opening at q. Imbalance
  I = (2 x takerBuyBase - baseVol) / baseVol in [-1, 1] (skip if baseVol = 0 or bar missing).
- z = (I - mean) / sd over the same coin's values at the **same quarter-hour of day** on the previous 30 UTC days
  (d-30..d-1, >= 25 valid values, sd > 0). Slot = quarter-hour of day (96 slots), so a slot's habitual imbalance is
  removed.
- Side = sign(z) (continuation, as the paper's positive 4-12 h coefficient). Trade if |z| >= k.

## Execution (fixed)
- Signal bar closes at q + 1 min. Entry = close of the 1m bar opening at q + 1 min (i.e. price at ~q + 2 min, one
  full minute after the signal is known). Exit = close of the 1m bar opening at entry_bar + H. If either bar is
  missing, use the nearest later bar within 5 minutes, else drop.
- One position per coin at a time: signals while a coin's position is open are ignored. $1 notional per trade.
- Trades whose exit falls at or after 2025-01-01 are dropped.
- Costs per side: taker 5 bp + half-spread 1 bp (BTC, ETH) / 3 bp (point-in-time rank < 20 by trailing-30-day perp
  quote volume, round 63 C) / 5 bp (rank >= 20). BTC / ETH round trip 12 bp; alts 16-20 bp. Funding: the position
  pays rate x side for every funding stamp in (entry, exit].

## Declared cells (6)
| cell | coins | k | H |
|---|---|---|---|
| A2_4 | all 6 | 2 | 4 h |
| A2_12 | all 6 | 2 | 12 h |
| A3_4 | all 6 | 3 | 4 h |
| A3_12 | all 6 | 3 | 12 h |
| M2_4 | BTC + ETH | 2 | 4 h |
| M2_12 | BTC + ETH | 2 | 12 h |

No other parameter is tuned. Eras: IS 2020-01-01..2021-12-31 (first 30 days per coin are warm-up), VAL
2022-01-01..2024-12-31.

## Statistics and checks
- Net bp per trade; t = cluster-robust t of the per-trade mean, clusters = entry UTC day.
- Per-year net (2020..2024); costs x1.5; one step late = entry one more minute later (close of bar q + 2 min),
  plus +15 min as information.
- Random benchmark: 500 replications; for each cell, the same number of trades per coin and era at uniformly random
  quarter-hour marks of that coin and era (same H, same costs and funding), side drawn with the cell's long share
  per coin. Report the share of replications whose mean net is below the real one. Max-over-6-cells null of the IS
  day-clustered t from the same replications.
- Information only (not cells): reversal side, gross by horizon 30 min / 1 / 4 / 8 / 12 h, non-mark minutes as a
  placebo (z of minute :07 / :22 / :37 / :52).

## How this differs from round 63 O (H3)
- O used the hourly taker buy / sell ratio from the metrics archive on 16 alt perps (ETH + 15 alts) hedged with
  beta x BTC, at ~30 bp round trip, and found |gross| <= 7.5 bp at 4 h. Here: (1) the signal is the clock-mark
  opening minute only, z-scored against the same slot's history (the algorithmic-burst footprint, not an hour's
  aggregate flow); (2) the coins are the six most liquid perps, unhedged, at 12 bp round trip for BTC / ETH;
  (3) the horizon matches the paper (4 / 12 h). Round 7 C tested quarter-hour openings on IC CFDs (price
  continuation, no flow data): no continuation with t >= 2. Prior is low: the paper's own forecast size is ~0.5 bp
  per boundary vs 12 bp cost, so only the |z| >= 2-3 tail could be large enough.

## Power arithmetic (before returns)
- HOLD would be 2025-01-01..2026-10-29 = 22 months vs VAL 36 months: expected HOLD trades = VAL n x 0.61.
- LIVE needs VAL Sharpe per trade x sqrt(HOLD n) >= 3 and the day-clustered analogue (VAL clustered t x sqrt(0.61))
  >= 3, i.e. a VAL day-clustered t >= 3.84. Since the registration here is forward-only, the relevant forward window
  is from 2026-10-30; at ~1 year forward, power = VAL clustered t x sqrt(1/3) >= 3 needs VAL t >= 5.2.
- Rough size: |z| >= 2 hits maybe 3-6 % of the 96 marks -> 3-6 signals per coin-day; with the one-position rule
  ~2-4 trades per coin-day at H = 4 h, ~1-2 at H = 12 h. VAL n ~ 6 coins x 1,096 days x 2-3 ~ 13-20k trades
  (H 4), 6-10k (H 12). With BTC 4 h sd ~ 100 bp and 6 correlated coins (cross-coin correlation ~0.7, so ~2-3
  effective coins), the per-day effective sample is small; a VAL clustered t >= 3.84 over 1,096 days needs a daily
  book Sharpe of ~0.116 (annual ~2.2). At 12 bp cost the gross per trade must exceed ~12 bp plus ~3-5 bp of edge,
  i.e. 20-30 x the paper's average forecast. Prior probability of a LIVE pass: <= 3 %.
