# Stream CL (round 74): listings on Bithumb / Coinbase / Robinhood / others, timed by third-party Telegram posts

Written Mon Nov 2 15:00:55 UTC 2026 (`date -u`). Rules, regexes, grid and power were declared in
[HYPOTHESES_CL.md](HYPOTHESES_CL.md) at 14:47 UTC, before any price was requested. HOLD (2025-01-01..) was never
priced. Only per-class title counts were taken, plus one format slip, noted under Pitfalls.

## Answer first: none (no class reaches the DEMO bar)
- **The feed is late: the coin has usually moved before the post.** The burst onset is the first alt trade with alt
  vs BTC >= +2 %, measured from T - 10 min.
  - Coinbase announcements: **100 % of events moved before T + 5 s, in IS and VAL**. The median onset was **34 s
    (IS) / 39 s (VAL) before the post**.
  - Bithumb: 77 % (IS) / 79 % (VAL) moved before T + 5 s. The median onset was 63 s / **200 s** before the post.
  - Coinbase go-live: 62 % / 29 %. Most VAL go-lives have no burst at all.
  - So @coin_listing (2020-23) and @newlistingsfeed (2024) relayed these venues 30 s to minutes after the market
    knew. On Upbit, by contrast, round 73 measured a 1 s lag.
- **Graded cells** (long alt perp / short BTC perp, entry T + 5 s, 22 bp + slippage + funding, t by post day). Each
  class's declared choice is its better IS-t exit:

  | class (choice) | IS n (days) | IS net bp | IS t | VAL n (days) | VAL net bp | VAL t | years + | random IS / VAL | power at VAL size |
  |---|---|---|---|---|---|---|---|---|---|
  | BH Bithumb KRW (60m) | 13 (12) | +105 | 1.32 | 19 (15) | +24 | 0.49 | 3 / 3 | 99.6 / 89.8 % | 0.11 x sqrt(64) = 0.88 |
  | CBA Coinbase announcement (5m) | 28 (21) | +173 | 1.14 | 23 (21) | +5 | 0.07 | 3 / 4 | 100 / 100 % | 0.06 |
  | CBL Coinbase go-live (5m) | 24 (15) | -15 | -0.24 | 21 (19) | -21 | -0.81 | 2 / 5 | 92.8 / 70.8 % | -0.69 |

  - The DEMO bar needs IS t >= 2.0. The best IS t of the 6 cells is 1.32, below the random max-over-6-cells null's
    95th percentile (1.46 IS, 1.12 VAL).
  - The gross IS means beat random (the events are real news), but after entry the move is mostly spent.
- **Robinhood** (RH) cannot be tested: pre-2025 there are 5 events on 2 days, all in VAL 2024-11/12. Descriptive only:
  +58 bp (5m), +399 bp (60m, carried by PEPE). HOLD has 22 Robinhood titles. It is a forward-only idea at best.
- **Others** (Huobi "will list", 7 events): -296 / -395 bp IS. None.
- No PREREG_DRAFT. HOLD untouched.

## Data
- **Posts.**
  - @coin_listing: round 73's complete read-only cache of t.me/s pages (research/data/telegram_upbit/raw/coin_listing,
    588 pages). The coordinator's round 74 pages override it per post id (77 pages present when the events were
    built). The rebuild check is at the end of this file.
  - @newlistingsfeed: pulled by me with the shared fetcher (`coord/pageback.py newlistingsfeed 400`).
    - 165 pages, 14:24-14:42 UTC, reached id 1, all 200.
    - research/data/telegram_hist/raw/newlistingsfeed; log research/data/telegram_hist/requests.log; progress
      pull_CL_newlistingsfeed.out.
  - Cut at T < 2025-01-01 right after parsing.
- **Coverage per venue pre-2025** (this is the binding constraint):
  - Bithumb: 2020-01..2021-08 (coin_listing notice relays), then **2024-07..12 only** (newlistingsfeed).
  - Coinbase: 2020-05..2022-02 (blog relays), 2022-06..2023-03 (tweet relays), 2024-04..12 (newlistingsfeed).
  - Robinhood: 2024-11/12.
  - From 2023-05 to 2024-12, @coin_listing posts almost only Binance and Upbit.
- **Prices.** data.binance.vision futures/um daily aggTrades, 197 files, 200 / 200 OK plus one logged read timeout
  (retried). No 403 / 418 / 429.
  - Every file is dated <= 2024-12-24.
  - Alt windows are [T - 15 min, T + 65 min], plus 1 s day series.
  - research/data/tg_cl/npz (140 MB); log research/data/tg_cl/requests.log; zips deleted.
  - BTC days reuse local futures-aggTrades caches (upbit_latency, upbit_census, btc_treasury_8k, upbit_bybit_notice)
    where present.
  - Funding: local files (no fapi call was needed).

## Events (code/events.py; CL/events.csv, CL/events_all.csv)
| class | first posts per coin (all) IS / VAL | with a Binance perp >= 7 d: IS / VAL | per year 2020 / 21 / 22 / 23 / 24 | HOLD titles (distinct class-coin) |
|---|---|---|---|---|
| BH | 65 / 37 | 13 / 19 | 3 / 10 / 0 / 0 / 19 | 125 |
| CBA | 101 / 101 | 28 / 23 | 6 / 22 / 14 / 1 / 8 | 66 |
| CBL | 66 / 100 | 24 / 21 | 4 / 20 / 13 / 2 / 6 | 85 |
| RH | 0 / 5 | 0 / 5 | 0 / 0 / 0 / 0 / 5 | 22 |
| OTH | 40 / 23 | 5 / 2 | 1 / 4 / 2 / 0 / 0 | - |

- Most Coinbase listings are of coins whose Binance perp did not yet exist or was < 7 d old. So only ~25 % qualify,
  and the expected HOLD sizes are small (CBA ~15, CBL ~18 events).
- **Venue open stated in the post:** among events with a perp, only a handful of 2024 Coinbase "listed on Coinbase
  spot: <date> at <time>" posts state an open, and none of them had a >= 7 d perp. So the open cell was not gradable.
- **Edited posts:** 1 event (FLOKI CBA 2024). Dropping it changes CBA VAL 5m from +5 to +8 bp.

## Path and "already moved" (results.txt; ref = T - 10 min; median r alt vs BTC, bp)
| class | era | n | moved before T + 5 s | onset median (q25, q75) s vs T | r(T - 60 s) | r(T) | r(T + 5 s) | r(+60 s) | r(+5 m) | r(+60 m) |
|---|---|---|---|---|---|---|---|---|---|---|
| BH | IS | 13 | 10 (77 %) | -63 (-234, -32) | 52 | 261 | 241 | 202 | 245 | 328 |
| BH | VAL | 19 | 15 (79 %) | -200 (-340, -123) | 251 | 489 | 415 | 451 | 550 | 454 |
| CBA | IS | 28 | 28 (100 %) | -34 (-102, -31) | 75 | 812 | 804 | 1193 | 933 | 1063 |
| CBA | VAL | 23 | 23 (100 %) | -39 (-86, -32) | 29 | 273 | 345 | 262 | 326 | 256 |
| CBL | IS | 24 | 15 (62 %) | -27 (-31, -13) | 14 | 186 | 198 | 232 | 213 | 154 |
| CBL | VAL | 21 | 6 (29 %) | -351 (-522, -95) | 9 | 37 | 37 | 29 | 30 | -9 |
| RH | VAL | 5 | 3 (60 %) | -82 | 233 | 140 | 136 | 143 | 140 | 506 |

- **The -30 s cluster.** The 2021 Coinbase and Bithumb relays sit at a nearly constant **~31 s after the onset**. That
  looks like a fixed polling / RSS delay of @coin_listing for those sources. It is not news reaching the market early.
- **CBA IS still drifted after entry:** +125 bp median, +252 mean from T + 5 s to + 60 s. That is why its gross beats
  random. In VAL the drift is -28 median / +23 mean, and after costs it is gone.
- **Newer fast relays exist only in 2024:** ZK and IO roadmap posts on newlistingsfeed had onset +0.4 / +0.5 s. Both
  trades lost (-420 / -212 bp at 5 m), because the spike faded within a minute.

## All cells (net bp; costs 22 bp + alt slippage + funding)
| cell | era | n (days) | gross | slip | net | t | median | SR | x1.5 | late 10 s | no edit | no multi-coin | years |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH-5m | IS | 13 (12) | 46 | 8 | 17 | 0.32 | -28 | 0.09 | 2 | 18 | 17 | 51 | 2020 -7, 2021 +24 |
| BH-5m | VAL | 19 (15) | 22 | 12 | -12 | -0.40 | -36 | -0.10 | -29 | -10 | -12 | 29 | 2024 -12 |
| BH-60m | IS | 13 (12) | 135 | 7 | 105 | 1.32 | -28 | 0.31 | 90 | 106 | 105 | 148 | +86, +111 |
| BH-60m | VAL | 19 (15) | 55 | 9 | 24 | 0.49 | 37 | 0.11 | 8 | 26 | 24 | 188 | 2024 +24 |
| CBA-5m | IS | 28 (21) | 232 | 38 | 173 | 1.14 | 62 | 0.24 | 143 | 134 | 173 | 348 | +324, +131 |
| CBA-5m | VAL | 23 (21) | 49 | 22 | 5 | 0.07 | -70 | 0.01 | -17 | 9 | 8 | 66 | 2022 -51, 2023 +291 (1), 2024 +67 |
| CBA-60m | IS | 28 (21) | 270 | 29 | 219 | 1.08 | 36 | 0.22 | 194 | 184 | 219 | 296 | +280, +203 |
| CBA-60m | VAL | 23 (21) | 131 | 17 | 92 | 0.45 | -119 | 0.09 | 72 | 98 | 77 | 249 | -56, -192 (1), +387 |
| CBL-5m | IS | 24 (15) | 20 | 13 | -15 | -0.24 | 34 | -0.07 | -33 | -5 | -15 | 150 | +133, -44 |
| CBL-5m | VAL | 21 (19) | 6 | 5 | -21 | -0.81 | -37 | -0.16 | -35 | -12 | -21 | -12 | -44, -26, +29 |
| CBL-60m | IS | 24 (15) | -8 | 11 | -41 | -0.24 | -114 | -0.06 | -58 | -33 | -41 | 84 | +348, -119 |
| CBL-60m | VAL | 21 (19) | -83 | 4 | -110 | -3.82 | -65 | -0.55 | -123 | -100 | -110 | -91 | -106, -63, -132 |

- **Random benchmark** (same coin / day, gross percentile):
  - IS: BH 99.9 / 99.6, CBA 100 / 100, CBL 92.8 / 30.7.
  - VAL: BH 94.2 / 89.8, CBA 100 / 99.7, CBL 70.8 / 1.1.
- **Max-over-6-cells null** (95th percentile of net t): 1.46 IS, 1.12 VAL.
- **CBA VAL 60m +92 bp** comes from 2024 MOODENG (+4,258) alone. Its median is -119.

## What failed and why
1. **Timing source.** The Telegram stamp is point in time, but for these venues the third-party relay is 30 s to
   minutes behind the market's first reaction. A T + 5 s entry is a late entry by construction.
   - This differs from Upbit, where the same channel matched Upbit's own stamp within ~1 s and A2's burst began after
     N.
   - The test therefore measures "trade the relay", not "trade the announcement".
2. **Coverage.**
   - Bithumb has no relayed history in 2022-23, so VAL is 19 events from 2024-07..12 only.
   - Coinbase VAL relies on 10 months of tweet relays plus 2024.
3. **Perp eligibility.** About 75 % of Coinbase listings precede a >= 7 d Binance perp. The qualifying events are
   large, already-perped coins with smaller pops.
4. **Coinbase go-live is not news.** It comes 1-3 days after the announcement; median VAL r(T) is 37 bp, and the
   60-min drift is negative.

## Cross-checks
- **newlistingsfeed vs coin_listing**, 2024 overlap (Coinbase only; coin_listing has no 2024 Bithumb):
  - PRCL roadmap stamps: 00:50:46 vs 00:50:48 (2 s apart).
  - IO (2024-10-08): newlistingsfeed "listed on Coinbase spot" 16:04:00; coin_listing "will add support" 16:06:13.
  - Too few overlaps for a lag table.
- **The ~31 s constant offset in 2021** (onset - T, CBL q25 -31.3, CBA q75 -30.8) is the clearest sign of a relay
  delay rather than a market lead.

## Pitfalls
- Before HYPOTHESES_CL.md I printed the 20 newest @coin_listing titles (2026-10) to learn the format. They were titles
  only, with no prices or counts used. Everything after that read HOLD only as the class counts above.
- Multi-coin posts give one event per coin on the same second. t is clustered by post day, but n overstates
  independence; the "no multi-coin" column is noisy.
- `perps.perp_for` checks age at day precision (as in A2).
- **BTC leg** uses the 1 s last price, not the first trade after T + 5 s (~1 bp error). BTC slippage is fixed at
  1 bp a fill.

## What a user decision could unlock
- **A first-party source for these venues.** Speed only matters when timed from the venue itself:
  - Bithumb's notice API is keyless but keeps only ~20 notices (round 66 B2). The Bithumb Telegram alert channel was
    not found in t.me/s.
  - Coinbase's own X/Twitter account or its status/asset API would need an account or a live logger.
  - A forward logger (Bithumb notices + Coinbase roadmap / X) would timestamp them first-hand. It would accumulate
    new-era events only.
  - On this evidence, the best class (BH-60m) is +24 bp in VAL even with a late entry. The prior for a first-hand
    feed is "maybe a seconds burst like Upbit's, then nothing". Round 65 H's small Bithumb run-up agrees.
- **Robinhood:** HOLD-era only (22 titles), so it is forward-only.

## Files
- `CL/HYPOTHESES_CL.md`, `CL/STREAM_CL.md`.
- `CL/results.txt` (all tables + per event), `CL/cells.json`, `CL/trades.csv`, `CL/events.csv`, `CL/events_all.csv`.
- `CL/code/`:
  - load.py: page parsing and the 2025 cut;
  - events.py: classes, regexes, HOLD counts;
  - pull.py: aggTrades;
  - analyze.py: path, onset, cells, random;
  - net.py: fetcher.
- Data:
  - research/data/tg_cl/{npz, requests.log, pull.out};
  - research/data/telegram_hist/raw/newlistingsfeed.

## Rebuild check against the coordinator's coin_listing pull (15:05 UTC)
- At 15:05 UTC the coordinator's pull held 175 / ~590 pages, 2,326 pre-2025 posts, ids 8683-11042 (2022-06..2024-12).
- On that overlap, round 73's and round 74's pages are identical: 0 time, 0 text and 0 edited-flag differences, and
  no post missing or new.
- So every VAL coin_listing event is confirmed on round 74 pages. The IS ids (3900-7900) were not yet re-pulled.
- Re-run to confirm IS: `python -I CL/code/events.py`. It prefers round 74 pages per id. If CL/events.csv is
  unchanged, the results stand without re-pricing.
