# Round 75: footprint / order-flow setups on Binance perps (U, SI, MN, VC, TF, CF, AB), 2026-11-03

Brief: [round75_order_flow/BRIEF.md](round75_order_flow/BRIEF.md) (15:47 UTC). Method: Trader Dale, *Order Flow
Trading Setups* (2021), written as measurable rules in [research/methods/order-flow-footprint.md](../../methods/order-flow-footprint.md).
Data: Binance USDT-M monthly aggTrades (aggressor side) for BTC, ETH 2020-01..2024-12 and SOL 2020-09..2024-12,
cached as a 1 bp footprint per minute by [coord/code/build_fp.py](round75_order_flow/coord/code/build_fp.py) and read
through the shared [coord/code/fp.py](round75_order_flow/coord/code/fp.py). HOLD (2025-26) was never downloaded.

## Answer first
- **No LIVE or DEMO candidate, no PREREG.** All seven book setups lose money after costs in IS and in VAL, pooled over
  the three symbols: 44 declared cells, best IS t +0.76 (VC rejection clusters), no cell near the DEMO IS bar of 2.0.
- The book's common skeleton (zone from a footprint event, departure, limit on the first retest, 0.15 ATR stop, POC or
  2R target, 24 h time stop) loses ~3-6 bp per trade on **random** levels, so the first retest of a level is not an
  edge by itself. Footprint zones do slightly better than random in two setups (stacked imbalance, rejection
  clusters: +1 to +5 bp gross), always less than one round trip of fees.
- The confirmations (aggressive delta, CVD divergence, big limit orders, absorption) add nothing over entering at the
  test, and the prior day's POC / VAH / VAL score like random rows of that day's range.
- The unfinished-auction "magnet" does not exist once distance and volatility are matched, so its uses in the book (TP
  extension, stop placement, no-trade warning) are void.

| stream (book setup) | best IS cell | IS net bp (t) | VAL net bp (t) | years + | random pct IS / VAL | file |
|---|---|---|---|---|---|---|
| U unfinished auction (#5) | revisit statistic: unfinished - finished | -0.2 pt (t -0.3) at 6 h | -0.8 pt (t -1.1) at 6 h | - | 42 / 10 | [STREAM_U](round75_order_flow/U/STREAM_U.md) |
| U trade toward the level | H12 | -14.8 (-6.8) | -12.4 | 0/5 | 1-12 / 21-64 | same |
| SI stacked imbalance (#4) | floor 0, TP POC | -1.1 (-0.56), n 7,160 | -3.3 (-2.30) | 0/5 | 99.5 / 70.5 | [STREAM_SI](round75_order_flow/SI/STREAM_SI.md) |
| MN multiple nodes (#2) | n 3, 2R | -19.6 (-1.33) | -2.1 (-0.37) | 1/5 | 42 / 94 | [STREAM_MN](round75_order_flow/MN/STREAM_MN.md) |
| VC trend clusters (#1) | c 2, TP POC | -1.2 (-0.22) | -5.2 (-1.58) | 1/5 | 54 / 11 | [STREAM_VC](round75_order_flow/VC/STREAM_VC.md) |
| VC rejection clusters (#1, VP 2-3) | c 3, TP POC | +4.1 (0.76) | +1.0 (0.35) | 4/5 | 80 / 90 | same |
| TF trades filter (#3) | 5 per day, 2R | +0.7 (0.23) | -3.6 (-1.98) | 1/5 | 96.5 / 53.5 | [STREAM_TF](round75_order_flow/TF/STREAM_TF.md) |
| CF delta / CVD at VP levels (C3, C4) | C3 x0.4, 2R | -6.0 (-0.67) | -17.3 (-4.32) | 1/5 | 38.5 / 1 | [STREAM_CF](round75_order_flow/CF/STREAM_CF.md) |
| AB big limit / absorption at VP levels (C1, C2) | bonus m8, 2R | +6.9 (0.44), n 114 | -5.8 (-0.59) | 3/5 | 90 / 75 | [STREAM_AB](round75_order_flow/AB/STREAM_AB.md) |

Costs x1.5 and one step late are worse in every stream. Best real cell vs the max-over-cells random null: 30-87 %
(IS). Power at VAL size is negative or ~0 everywhere.

## Coordinator checks
- Every HYPOTHESES file is stamped 16:52-16:53 UTC; every output that was kept is from 17:02 UTC or later, after the
  BTC fix (16:56) and the hole notice. Streams that had run on the void BTC file deleted or reran it (MN, VC, SI, AB, CF
  say so in their files).
- Independent rebuild of MN's n 2 / 2R cell for ETH from the HYPOTHESES text only
  ([coord/code/verify_mn.py](round75_order_flow/coord/code/verify_mn.py)): IS 817 trades, -7.60 bp; VAL 1,496,
  -2.61 bp, both equal to MN's tables; zone, departure and hole-drop counts equal within 4 zones (expiry edge).
- HOLD: no 2025-26 request in `research/data/footprint/requests.log`, no 2025-26 month file, every loader cuts at
  2025-01-01.

## Pitfalls (data)
- **Key overflow:** `fp_key = minute * 1e5 + floor(1e4 ln p)` overflows for BTC above $22,026 (bucket >= 1e5 carries
  into the minute). Found by stream U; `fp.split_key` undoes it (BTC only: ETH 2020 has real buckets ~44k, so a
  generic "< 50,000" rule would corrupt ETH). [coord/code/check_fp.py](round75_order_flow/coord/code/check_fp.py)
  now checks every month: minutes, bucket inside the minute's range, aggressor volumes. A future cache should use a
  wider key (1e6) or two arrays.
- **Unsorted timestamps:** SOL 2023-11 has timestamps that step back inside a file; the per-minute aggregation must
  sort first. Two SOL months were rebuilt.
- **Day holes:** Binance monthly aggTrades skip whole days (BTC 24 holes > 30 min, 610 h; ETH 7, 170 h; SOL 7-8): take
  ATR from daily klines and drop zones / trades that span a hole.
- At 3-7 bp rows, 64-77 % of 30m swing extremes have both bid and ask on the extreme row ("unfinished"), so the book's
  distinction is mostly noise at this resolution.

## Where the search stands
The book's whole family (setups 1-5, confirmations 1-4, VP levels) is closed on liquid crypto perps at taker / maker
retail fees. The only measurable footprint effect, +1 to +5 bp gross over random levels, is below one fee leg; it
would matter only with near-zero fees, which is a user decision (fee tier), not a research step. Standing unchanged:
C3 is the only LIVE algorithm.
