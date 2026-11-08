# Stream BL (round 74): Binance listing and perp-launch posts on @binance_announcements. None; the channel's stamp is late for listings

Written Mon Nov 2 15:09:08 UTC 2026 (from `date -u`). The rules, grid and costs were declared at 14:24:33 UTC in
[HYPOTHESES_BL.md](HYPOTHESES_BL.md), before any title or price. Counts, regex fixes and the readings were added in
its section 6 at 14:59:28 UTC, still before any price. HOLD was never priced. Only 2025-26 titles were counted, and
every data file is dated < 2025-01-01 (requests.log: 0 URLs dated 2025 or later).

## Answer first
- **L1 (spot listing, long the coin's perp from post + 5 s): none, not gradeable.**
  - Only 4 IS events (2018-21) have a venue with second-level trades (a perp >= 24 h old on Binance, Bybit or OKX). The
    declared gate was n_IS >= 20.
  - VAL has 19. Read-only, the frozen A2-analogue cell XO (exit at the Binance spot open) gives VAL net +542 bp,
    t 1.94, median +88, and 2022 is negative. It **beats only 59 % of random same-day entries**.
- **The Telegram stamp lags the listing jump by minutes.** This is the main finding of the stream.
  - On the perp venue, half of the listing jump is done a median **246 s before N** in VAL (q25 -511 s, q75 -115 s;
    18 of 18 events before N). In IS 2021 it is 84 s before N.
  - The median path from N - 600 s to N - 60 s is +1,183 bp (VAL). From N - 60 s to N + 5 s it adds only +83 bp more.
  - So `@binance_announcements` is a late repost of Binance spot-listing news. Any rule that trades from its stamp
    trades after the move. It is point in time, but slow. A2's Upbit stamp led the burst by 0.2-2.4 s; this one trails it.
- **L2 (perp launch, long Binance spot from post + 5 s): none, not gradeable.**
  - The channel carried 73 "Binance Futures Will Launch" posts in 2019-21, **1 in 2022 (an index) and 0 in 2023-26**.
    So VAL n = 0 and HOLD n = 0.
  - The IS-only reading is positive: X5 net +43 bp, t 2.43, 61 events on 53 days, random 100 %. 2020 is weak (+12).
  - Here the stamp is close to the jump: half-move median +2 s, with half of the events before N.
- No PREREG_DRAFT was written.

## Counts (titles only; HYPOTHESES section 6)
| coins per year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | HOLD 25-26 (count only) |
|---|---|---|---|---|---|---|---|---|---|
| L1 spot listings (regex, minus pegged assets) | 15 | 53 | 19 | 65 | 81 | 21 | 16 | 26 | 32 (26 posts) |
| L1 with a venue >= 24 h before N | 0 | 0 | 0 | 0 | 4 | 3 | 5 | 11 | not checked |
| L2 USDⓈ-M perp launches | - | - | 2 | 38 | 33 | 1 | 0 | 0 | 0 |
| L2 priced (spot >= 7 d old, not an index) | - | - | 2 | 35 | 24 | 0 | - | - | - |

- Channel: 8,941 posts (ids 1..9,107), 6,779 before 2025.
- L1 venues:
  - Bybit perp: 14 events (dumps start 2020; few altcoins before 2021).
  - Binance perp: 6 (all 2023-24).
  - OKX swap: 3 (dumps start 2021-09).
  - An undeclared OKX spot venue would add 4 IS and 8 VAL, so IS would still be 8.
- Edited posts: 0 among the L1 events and 1 among the L2 events (COTI). Results with it included: X5 +43, t 2.43 and
  X60 +72, t 2.00, unchanged (results_l2_with_edited.txt).

## How L1 differs from round 63 D
- Round 63 D required a Binance perp >= 7 d old and had no announcement time, so it timed trades by the first spot
  kline: 0 IS events.
- L1 times trades by the Telegram post. It accepts perps >= 24 h old on Binance, Bybit or OKX, and exits at or before
  the spot open. VAL goes from 7 to 19 events, and IS from 0 to 4.

## Results (net bp per trade; costs per the brief)
Costs: taker fees both sides (Binance perp 5 bp, Bybit 5.5, OKX 5, Binance spot 10), the worst-of-1 s fill on entry and
exit, and real funding where a local file exists. **t is clustered by post day.**

| rule / cell | era | n (days) | gross | fill gap | net | t | median | SR | x1.5 | late (+10 s) | years | rand % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 X5 | IS | 4 (4) | +388 | 11 | +377 | 2.00 | +346 | 0.86 | +366 | +369 | 2021 +377 | 100 |
| | VAL | 19 (18) | +229 | 51 | +218 | 1.48 | +70 | 0.43 | +187 | +243 | -50 / +564 / +134 | 100 |
| L1 X60 | IS | 4 (4) | +650 | 5 | +639 | 2.76 | +809 | 1.19 | +632 | +631 | 2021 +639 | 100 |
| | VAL | 19 (18) | +244 | 40 | +233 | 1.32 | +238 | 0.33 | +208 | +258 | -177 / +777 / +98 | 97.5 |
| **L1 XO (frozen reading)** | IS | 4 (4) | +780 | 6 | +766 | 2.34 | +703 | 1.01 | +758 | +758 | 2021 +766 | 92.2 |
| | VAL | 19 (18) | +544 | 42 | **+542** | **1.94** | +88 | 0.42 | +516 | +567 | -117 / +1503 / +285 | **58.9** |
| L2 X5 | IS | 61 (53) | +63 | 6 | +43 | 2.43 | +27 | 0.31 | +30 | +39 | 2019 -22 (2), 2020 +12, 2021 +95 | 100 |
| L2 X60 | IS | 59 (52) | +94 | 6 | +74 | 2.04 | +30 | 0.27 | +62 | +69 | -1 / +67 / +92 | 100 |
| L2 XP (perp open) | IS | 48 (46) | -42 | 5 | -62 | -0.57 | +7 | -0.08 | -75 | -68 | 2020 -38, 2021 -99 | 44.8 |
| L2 any cell | VAL | 0 | | | | | | | | | | |

**Column and table notes:**
- **years:** VAL years are 2022 / 2023 / 2024.
- **rand %:** percentile of the event gross mean (second-level fills) against 1,000 sets of same-coin, same-UTC-day
  entries outside [N - 1 h, N + 2 h], with the same hold.
- **Max-over-cells null (95th percentile of the max t over the 3 cells):** L1 IS 2.35, VAL 2.73. L2 IS 1.01.
  - The L1 VAL null is high: on listing days, random entries drift up too.
  - L2 X5's IS t 2.43 is beyond its null.
- **Power at VAL size:**
  - L1: SR 0.42 x sqrt(~10-32 HOLD trades) = 1.3-2.4 (< 3).
  - L2: 0 HOLD posts, so power 0.
- **XO holds:** the spot open is 2.7-20.5 h after N (median about 4 h).

## Burst timing (post-hoc check, chooses no cell; lag_l1.txt, lag_l2.txt)
**Median path (bp vs the last price at N - 60 s):**

| rule era (n) | -3600 s | -600 s | -60 s | 0 | +1 | +2 | +3 | +5 | +10 | +30 | +60 | +300 | +3600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 IS (4) | -1358 | -1477 | 0 | +31 | +55 | +51 | +83 | +110 | +103 | +241 | +420 | +479 | +1010 |
| L1 VAL (19) | -1581 | -1183 | 0 | +66 | +57 | +74 | +78 | +83 | +71 | +32 | +51 | +176 | +526 |
| L2 IS (61) | +19 | -6 | 0 | +56 | +56 | +59 | +59 | +58 | +73 | +87 | +128 | +123 | +128 |

**When the jump happens:**
- **Half-move time.** b is the last price at N - 15 min. The half-move time is the first trade with ln(P / b) >= half of
  the window maximum over [N - 10 min, N + 5 min].
  - L1 VAL: median -246 s, 18 / 18 before N. Examples: PEPE / FLOKI about -500 s, BLUR -531 s, WIF -134 s, METIS -69 s.
  - L1 IS: median -84 s.
  - L2 IS: median +2 s (q25 -25, q75 +46). The share before N is 0.62 in 2020-H1, and 0.19 in 2021-H1, when the
    median is +46 s.
- **Largest 10 s rise:** it starts a median 163 s before N in L1 VAL, and 11 s before N in L2 IS.
- **Reading.** For spot listings the Binance site, API or X post reaches traders 1-10 minutes before the Telegram
  repost. The lag was 1-3 min in 2021-22 and often 4-10 min in 2023-24. For the 2019-21 perp-launch posts the Telegram stamp was within about
  ±30 s of the reaction.

## What failed and why
- **L1 IS is empty by structure.**
  - Before late 2021 almost no Binance spot-listing coin had a perp anywhere with public trade dumps: Bybit's 2020-21
    USDT perps were large caps already on Binance, and OKX dumps start in 2021-09.
  - The 2020-21 listing wave (146 coins) has no tradable venue in the allowed data.
- **L1 VAL is not beyond random** (59 % for XO) and depends on 2023, when FLOKI / PEPE / ORDI made +1,503. 2022 is
  negative in every cell. The early part of the jump is gone before N.
- **L2 has no VAL or HOLD in this channel.** Binance stopped posting perp launches to Telegram after 2021-08. The
  IS-only signal (X5 t 2.43) cannot be validated.

## Pitfalls met
- **The channel is a late repost for listings.** Do not treat its stamp as the announcement time when measuring the
  reaction.
- **OKX daily dumps are UTC+8 days**, [date - 8 h, date + 16 h) UTC. The code handles it: the first OKX parse tripped a
  bounds assert.
- **Ticker reuse:** LUNA 2.0 vs the old LUNAUSDT perp. The perp must trade on day(N).
- **Postponed listings:** "Listing Postponed" posts do not move N. XO uses the real first spot trade.
- **Regex fixes before prices:**
  - fiat-gateway titles matched the L1 include, so they are now excluded;
  - the 2019-20 L2 format is "Launches XXX/USDT Perpetual".
- `@binance_futures` on Telegram is an unofficial signals channel, not Binance (1 page probed). `BinanceFutures` is a
  302 redirect.

## What a user decision could unlock
1. **A faster Binance listing feed.** The Binance site / CMS route is robots-banned (`/bapi/`). An official API-key
   announcement stream would need the user's account. Without one, Binance listings cannot be traded at seconds from
   any allowed source, because the Telegram repost is minutes late.
2. **L2 VAL / HOLD:** a perp-launch time source for 2022-26. That means Binance's own feed (decision 1), or allowing the
   perp's first trade as the event, which is a different rule (round 66 N0 tested the perp itself).
3. **An era split for exchange-event rules** (round 63 D's decision 2), for example design on 2022-23 and validate on
   2024. Even then L1 VAL is not beyond random.
4. **More pre-open venues** (Coinbase / Gate / Kucoin public trade history) to fill L1 IS in 2020-21. These sources
   are not in the brief's list.

## Files
- **Code (BL/code/):**
  - net.py: polite fetcher.
  - posts.py: parse pages; cut at 2025.
  - classify.py: regexes and counts.
  - venue.py: L1 venue choice.
  - okx_spot_count.py: HEAD count.
  - pull.py: generic dump cutter (bspot / bum / bybit / okx).
  - pull_l1.py, pull_l2.py.
  - analyze.py: cells, costs, random null, path.
  - lag.py: post-hoc jump timing.
- **Outputs (BL/):**
  - results_l1.txt, results_l2.txt, results_l2_with_edited.txt
  - lag_l1.txt, lag_l2.txt
  - trades_l1.csv, trades_l2.csv, trades_l2_ed.csv
- **Data (research/data/binance_tg_listing/, 86 MB):**
  - posts_pre2025.json, hold_titles.json (titles only), l1/l2 titles, events, venue json
  - npz/: window trades and per-second day arrays
  - requests.log: 1,088 lines, 0 x 403 / 418 / 429
- One t.me request pair (via coord/tg.py, shared lock) for the two futures-channel probes. The binance_announcements
  pages were pulled by the coordinator.
