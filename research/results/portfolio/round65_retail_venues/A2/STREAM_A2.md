# Stream A2 (round 65): seconds after the Upbit KRW-listing notice. DEMO candidate (D5-L), LIVE missed on power by 0.03

Written Sun Nov 1 12:22:56 UTC 2026 (from `date -u`). Rule, grid, slippage and power were declared at 12:04:44 UTC in
[HYPOTHESES_A2.md](HYPOTHESES_A2.md), before any aggTrade was downloaded. HOLD (2025-01-01..) was never requested,
loaded or counted: only daily files dated 2020-04-07..2024-12-05 were pulled, and every event has N < 2025.

## Answer first
- **The stamp is exact to the second and the Binance burst follows it; it never leads it.** `first_listed_at` has whole
  seconds (+09:00), and it is the publish time (scheduled posts go live at round times). On the alt perp, the first trade
  with alt vs BTC >= +2 % comes a median **0.7 s after N in VAL** (max 2.4 s; 31 of 32 events in 0.2-2.4 s; AGLD's
  -296 s is a dip below the N - 60 s reference, not a leak) and 1.6 s in IS (2020: 5-88 s, slow). Alt vs BTC from N - 60 s
  to N: median -1 bp (VAL), +6 bp (IS). No pre-stamp leak on Binance.
- **The jump is 1-3 seconds long.** VAL median path (bp, alt vs BTC since N - 60 s): 0 s -1, +1 s 476, +2 s 867,
  +3 s 977, +5 s 1289, +10 s 974, +30 s 1194, +60 s 1248, +300 s 1199. Half of the +60 s level is reached at a median
  1.2 s, 90 % at 3.3 s. IS is slower: median +2 s 176, +5 s 288, +30 s 746, +300 s 1139 (half at 11 s).
- **What is left after the jump is positive on average, from fat right tails.** Declared cell choice (best IS t among
  d >= 5 s): **D5-L, long alt / short BTC at the first trade >= N + 5 s, exit at the first trade >= L (KRW open)**:
  - IS +1,296 bp net, t 3.07, n 12 (9 days), SR 1.03, years 2020 +412, 2021 +1,738.
  - VAL **+520 bp, t 1.75, n 32 (32 days), SR 0.31**, years 2022 +210, 2023 +386, 2024 +626 (5 / 5 years positive).
  - Beats 100 % of random same-coin same-day entries in both eras; costs x1.5 +477; one step late (d 10) +454.
  - **HOLD power at VAL size 0.309 x sqrt(92) = 2.97: below LIVE's 3 by 0.03.** Every other LIVE bar passes.
    **Verdict: DEMO** (IS t >= 2.0, VAL > 0, random >= 90 %). PREREG_DRAFT_A2_D5L.md written; HOLD not opened.
- **Per d:** d 2 s: LIVE numbers (VAL +833 / +1,000 bp, t 3.56 / 2.99, power 6.0 / 5.1), but declared as a latency race
  that cannot stand alone. d 5 s: DEMO (selected D5-L); D5-5m has power 3.04. d 10 s: D10-L / D10-5m power 3.03 / 3.13,
  2022 negative (4 / 5 years). d 30 s: none (VAL -59 / +70 bp, t -0.67 / 0.48). So the edge is gone between 10 and 30 s.
- **Cautions** (post-hoc checks, checks.txt): VAL medians are small (D5-L +182, D5-5m +29 bp). The 10 % trimmed mean
  is +267, and the minimum leave-one-out t is 1.53. If the fill is the worst price within 1 s of N + 5 s, VAL drops to
  +373 bp, t 1.34. The prior from round 62 P2 and round 64 F: seconds-level crypto edges decayed in 2025-26, and bots
  multiply. C3 correlation: 0.01 on the 24 shared days.

## Timestamp precision (before prices; HYPOTHESES_A2.md)
- All 80 bodies and 5,953 list rows: `YYYY-MM-DDTHH:MM:SS+09:00`, no milliseconds. Real publish time is in [N, N + 1 s).
- It is the publish time: 4 of 4,199 pre-2025 notices have a later id but an earlier stamp (scheduled at a round time).
  16 % sit at second 00-02 (5 % if uniform). The listing notices in the sample mostly sit at hh:00:00-23 or hh:30:00-08.
- `listed_at` is a later edit time (it differs in 238 rows), so it is not used.
- **Binance confirms the stamp.** In VAL every burst starts 0.2-2.4 s after N. The trade-count onset (definition b)
  is noisy, because thin coins have a 0 / s baseline and the floor of 10 trades / s triggers on random pre-N clusters
  (66 % "negative"). Definition a (price) is the reliable one. Nothing suggests the notice reaches traders before the
  stamp. The fastest reactors (0.2-0.7 s) are bots that read Upbit within a fraction of a second.

## Data (research/data/upbit_latency/, requests.log 91 lines)
- data.binance.vision robots.txt: 404 (logged). There were 4 HEAD size probes, then 85 daily
  `futures/um/daily/aggTrades` zips: 44 alt files and 41 BTCUSDT days, 1.76 GB in total. One read timeout was logged
  and retried. No 403 / 418 / 429. Plain UA `research-script`, >= 0.3 s per request.
- Each zip was streamed to tmp/, parsed with `python -I`, and deleted. npz/ (66 MB) holds the trades in
  [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min], plus a 1 s last-price / count series of the day.
- The pull took ~9.5 min. Funding came from the local research/data/binance/funding files (no fapi request was needed).
- Events: stream A's 44 (A/notice_events_L.csv). SRM is dropped. MATIC uses SOL's L; STG and BONK use stated + 5 min.

## Results (net bp per trade; 20 bp + declared slippage + real funding; t clustered by notice day; results.txt)
| cell | era | n (days) | gross | slip | fund | **net** | **t** | median | SR | x1.5 | late | years (net) | rand % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D2-5m | IS | 12 (9) | 1415 | 44 | 0 | 1351 | 2.97 | 820 | 0.95 | 1319 | 1127 | 2020 +579, 2021 +1737 | 100 | |
| | VAL | 32 (32) | 920 | 67 | 0 | 833 | 3.56 | 616 | 0.63 | 790 | 360 | +295, +697, +976 | 100 | 6.04 |
| D2-L | IS | 12 (9) | 1593 | 47 | 2 | 1528 | 3.15 | 1200 | 1.07 | 1495 | 1296 | +476, +2054 | 100 | |
| | VAL | 32 (32) | 1071 | 68 | 17 | 1000 | 2.99 | 658 | 0.53 | 957 | 520 | +458, +556, +1282 | 100 | 5.07 |
| D5-5m | IS | 12 (9) | 1189 | 42 | 0 | 1127 | 2.84 | 463 | 0.87 | 1095 | 1024 | +514, +1433 | 100 | |
| | VAL | 32 (32) | 444 | 64 | 0 | 360 | 1.79 | 29 | 0.32 | 318 | 303 | +47, +515, +338 | 100 | 3.04 |
| **D5-L** | IS | 12 (9) | 1360 | 46 | 2 | **1296** | **3.07** | 1024 | 1.03 | 1263 | 1191 | +412, +1738 | 100 | |
| | VAL | 32 (32) | 588 | 65 | 17 | **520** | **1.75** | 182 | 0.31 | 477 | 454 | +210, +386, +626 | 100 | **2.97** |
| D10-5m | IS | 12 (9) | 1086 | 42 | 0 | 1024 | 2.69 | 422 | 0.80 | 993 | 503 | +446, +1312 | 100 | |
| | VAL | 32 (32) | 383 | 60 | 0 | 303 | 1.84 | 157 | 0.33 | 263 | -59 | -314, +527, +294 | 100 | 3.13 |
| D10-L | IS | 12 (9) | 1254 | 45 | 2 | 1191 | 2.96 | 892 | 0.97 | 1158 | 674 | +346, +1613 | 100 | |
| | VAL | 32 (32) | 518 | 61 | 17 | 454 | 1.79 | 73 | 0.32 | 414 | 70 | -158, +402, +569 | 100 | 3.03 |
| D30-5m | IS | 12 (9) | 563 | 40 | 0 | 503 | 1.60 | 149 | 0.46 | 473 | 130 | +143, +683 | 100 | |
| | VAL | 32 (32) | 11 | 50 | 0 | -59 | -0.67 | -46 | -0.12 | -94 | -143 | -636, +209, -94 | 89 | -1.13 |
| D30-L | IS | 12 (9) | 735 | 43 | 2 | 674 | 1.73 | 208 | 0.58 | 642 | 301 | +48, +987 | 100 | |
| | VAL | 32 (32) | 124 | 51 | 17 | 70 | 0.48 | -42 | 0.08 | 34 | -12 | -484, +113, +134 | 100 | 0.81 |

**Column notes:**
- **late:** the next d.
- **rand %:** percentile of the gross mean vs 1,000 sets of same-coin same-day random entries with the same hold.
- **power:** SR x sqrt(92).

**Max-over-cells:** the random null's 95th percentile of the max net t over the 8 cells is 0.38 (IS) and -0.21
(VAL). The observed t values are far beyond it. The selection risk is between neighbouring cells, not against noise.

**Slippage.** Half the median 1 s range, summed over 4 fills, comes to 40-68 bp. Ranges are wide during the jump.

## Post-hoc execution checks (checks.txt; labelled post-hoc, they do not choose a cell)
| cell | era | declared fill | aggressor-side fill | worst price of the 1 s | trimmed 10 % | median | min LOO t |
|---|---|---|---|---|---|---|---|
| D5-L | IS | +1296, t 3.07 | +1287, t 3.07 | +1205, t 3.00 | +1130 | +1024 | 2.70 |
| D5-L | VAL | +520, t 1.75 | +516, t 1.73 (power 2.94) | +373, t 1.34 | +267 | +182 | 1.53 |
| D5-5m | VAL | +360, t 1.79 | +355, t 1.76 | +209, t 1.12 | +187 | +29 | 1.45 |
| D2-5m | VAL | +833, t 3.56 | +834, t 3.57 | +453, t 1.91 | +643 | +616 | 3.32 |

- **Fill-time gap.** The first trade after N + d comes within 0.2 s on every event, so there are no stale prints.
- **Capacity: buyer-taker alt notional in the first 1 s after N + 5 s.** The VAL median is $240k (q25 $111k); over 5 s
  it is $1.1M (q25 $648k). In IS it is $91k / $592k. A bot taking ~$10-30k per event is a small share of that flow.
  At VAL size, ~$20k x 520 bp ≈ $1,000 per event.

## What a real bot would need (user decisions)
1. **Notice capture within ~2-3 s of N.**
   - The keyless route is polling `api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=trade`.
     It returned 429 at 0.3 s per request (stream W), and 1.5 s ran clean, so the mean detection lag is ~0.75 s plus
     the RTT.
   - CDN caching of that endpoint is unknown. **A forward test is needed first:** poll from a Tokyo VPS for a few weeks
     and log first-seen time vs `first_listed_at` on live notices.
   - Upbit's developer docs list an official **private WebSocket announcement feed** (`wss://api.upbit.com/websocket/v1/private`,
     push on new or updated notices, rate limit 5 messages / s). It needs an Upbit API key, so it needs an account (a
     user decision). The docs warn that its timing can differ from the web / app.
2. **Parse the coin from the title.** The title carries the ticker, e.g. "(BEAM) KRW 마켓 디지털 자산 추가". Keep only
   KRW-market listings and check that a Binance USDT-M perp exists (an exchangeInfo cache).
   - Pitfalls: BTC- or USDT-only notices; renamed tickers (BEAM -> BEAMXUSDT, SHIB / PEPE / BONK -> 1000x); multi-coin
     notices.
3. **Orders.** A Binance USDT-M account co-located in Tokyo (AWS ap-northeast-1). Send two market orders (long alt,
   short BTC) at once, by N + 5 s at the latest. Exit both at the first Upbit KRW trade (L = stated start + 5 min,
   given in the body) or at a fixed time.
   - Watch the alt's max market-order size and the price-band (PERCENT_PRICE) limits during a +15 % second.
4. **Expect competition.** VAL bursts start 0.2-2.4 s after the stamp. Faster bots already take the first 1-3 s; d 2 s
   is their territory.

## What failed or is weak
- **LIVE misses on power by 0.03** (2.97). Choosing D5-5m or D10-x (3.04-3.13) now would be cell-shopping. With the
  worst-of-second fill, every d >= 5 cell has power < 2.
- **VAL depends on fat tails.** In D5-5m the median is +29 bp and the mean is +360. 2024 brings 20 of 32 events.
- **IS is 9 notice days.** The 2021 batch days carry it (1INCH / AAVE, MATIC / SOL), and 2020 reactions took 5-88 s.
- **n_HOLD = 92 is K2's L-based count.** Multi-coin notice days lower the effective n.
- **2025-26 decay risk is real.** Sub-minute crypto edges (round 62 P2, round 64 F) vanished in HOLD.

## Files
- **Code (A2/code/):**
  - net.py: polite fetcher and log.
  - events.py: stream A's events plus the L fallbacks.
  - pull.py: stream, cut and delete zips.
  - analyze.py: path, onset, 8 cells, random benchmark.
  - checks.py: post-hoc fills, capacity, C3.
- **A2/:**
  - HYPOTHESES_A2.md, STREAM_A2.md, PREREG_DRAFT_A2_D5L.md
  - results.txt, checks.txt, cells.json, trades.csv
- **Data:**
  - research/data/upbit_latency/npz/ (85 files, 66 MB)
  - requests.log, pull.out
