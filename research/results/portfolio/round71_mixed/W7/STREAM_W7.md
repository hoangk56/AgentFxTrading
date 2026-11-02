# Stream W7 (round 71): withdrawal-closed window of new Binance spot listings, result

Written Sun Nov 1 18:42 UTC 2026 (from `date -u`).
- Hypotheses: [HYPOTHESES_W7.md](HYPOTHESES_W7.md), 18:30:03 UTC, before any price file or return. No change after it.
- HOLD (2025-01-01..) was never requested or loaded. The last requested day is 2024-12-18, every series is cut at
  ts < 2025-01-01, and no URL in requests.log contains "2025-".
- Code: `code/` (net.py, robots.py, meta.py event list, pull.py trade files, fund.py funding, analyze.py cells /
  random, path.py gap path). Outputs: `out/results.txt` (every graded number), `out/desc.txt`, `out/path.txt`,
  `out/cells.json`, `out/trades.csv`.

## Answer: none. IS has 1 tradable event, so no cell can reach DEMO or LIVE; VAL cells hold 1-5 trades

- **Events.** 76 new coins (2020-24) had a reference perp on or before the spot listing day: IS 5, VAL 71.
- **Few have a perp live at the signal.** Binance usually opens the coin's USDT-M perp **30-300 min after** spot
  (median ~+120 min in 2024). So at L0 + 15 / 60 min only 35 / 40 events have a reference:
  - IS: 2 (both Bybit).
  - VAL: 33 / 38 (Binance 10 / 15, Bybit 23 / 23).
- **Discounts are rare.** d <= -50 bp at +15 min: IS 1, VAL 5 (only 1 at <= -100). At +60 min: IS 0, VAL 4 (2 at
  <= -100).
  - Premia are twice as common: >= +50 bp in 10 VAL events. They close within ~2 h, as the inward (deposit) route
    allows.
- **Every traded event was hedged on Bybit.** No Binance-perp event showed a discount.
- IS has n <= 1 in every cell, so no IS t exists. Parameters cannot be picked on IS. LIVE and DEMO both fail on the
  IS bar, as the hypotheses expected. No PREREG_DRAFT.

| cell | era | n (days) | net bp | median | t (day) | SR | x1.5 | late +60 s | spot leg | hedge leg | funding | fees | W-4h / W+4h | random % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S15_k50_X0 | IS | 1 (1) | +22 | +22 | - | - | -2 | +4 | -876 | +916 | +18 | 35 | +41 / +54 | 97.7 | |
| | VAL | 5 (5) | +151 | +22 | 0.85 | 0.38 | +128 | +43 | -637 | +809 | +13 | 32 | +93 / +155 | 100.0 | 0.67 |
| S15_k50_X30 | IS | 1 (1) | +43 | +43 | - | - | +24 | +25 | -816 | +876 | +18 | 35 | | 96.9 | |
| | VAL | 5 (5) | +134 | +36 | 0.88 | 0.40 | +109 | +26 | -626 | +781 | +13 | 32 | +93 / +155 | 100.0 | 0.69 |
| S15_k100_X0 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 1 | +839 | | - | - | +799 | +494 | +77 | +792 | +3 | 31 | +591 / +862 | 100.0 | - |
| S15_k100_X30 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 1 | +717 | | - | - | +677 | +375 | -60 | +807 | +3 | 31 | | 100.0 | - |
| S60_k50_X0 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 4 (4) | -43 | -17 | -0.94 | -0.47 | -63 | -101 | -1136 | +1117 | +9 | 31 | -98 / -44 | 17.0 | -0.73 |
| S60_k50_X30 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 4 (4) | -72 | -73 | -1.67 | -0.83 | -93 | -130 | -1113 | +1065 | +9 | 31 | | 18.2 | -1.30 |
| S60_k100_X0 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 2 (2) | -96 | -96 | -1.24 | -0.88 | -120 | -188 | -1719 | +1653 | +3 | 31 | -190 / -102 | 10.3 | -0.97 |
| S60_k100_X30 | IS | 0 | | | | | | | | | | | | | |
| | VAL | 2 (2) | -146 | -146 | -15.5 | -10.9 | -170 | -237 | -1721 | +1605 | +3 | 31 | | 10.9 | -12.1 |

- **Years.** All VAL trades fall in 2022 (WOO) and 2024 (METIS, SCR, PNUT, USUAL, AXL). The 2023 count is 0.
  The S15 VAL mean comes from one trade: SCRUSDT 2024-10-11, d = -1,409 bp, net +839. Without it, S15_k50_X0 VAL is
  4 trades at -21 bp.
- **Legs.** The spot leg alone loses heavily: new coins fall in their first day (-640 to -1,720 bp per trade). The
  short perp gains almost as much. So the hedge, not the discount, carries the variance (N0's continuation, on the
  downside). Funding paid the short +3 to +29 bp.
- **Max-over-8-cells null of t.** VAL real max 0.88; null median 0.51, p95 1.30, p 0.12. IS undefined (n <= 1).
- **Power at VAL size.** <= 0.69 against the bar of 3. At 5 trades per 3 years, HOLD n ~ 3.
- **Withdrawal-clock sensitivity** (exit at W ± 4 h) does not change the signs. The ARB drop is moot: ARB never
  showed a discount.

## The gap after the signal (out/path.txt; median d in bp, same reference as the signal; information only)
| bucket at +15 min | n | S | +5 m | +30 m | +2 h | +6 h | +12 h | W-1h | W | W+1h | W+4h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d <= -50 | 6 | -76 | -86 | -74 | -40 | -29 | -37 | -41 | -38 | -26 | -36 |
| -50 < d < 50 | 19 | +8 | +6 | 0 | -3 | +2 | -13 | -6 | -4 | -2 | -8 |
| d >= +50 | 10 | +322 | +300 | +62 | -4 | -2 | 0 | -2 | -12 | -12 | -4 |

- **Discounts.** They halve in the first ~2 h, while withdrawals are still closed. There is no visible snap when the
  withdrawal clock opens: at W and W+4h the gap is still ~ -30 bp. The mechanism predicts the opposite timing (hold
  until W, close at W). With n = 6 and Bybit as the reference, this is weak evidence. A Bybit perp also carries a
  venue basis that the withdrawal lock does not touch.
- **Premia.** They close within 2 h: deposits are open, so the inward route works, as IB7 said.

## Why it failed
1. **IS does not exist.** In 2020-21, only 5 new Binance coins had a perp by listing day, and only 2 had one live
   15-60 min after the open (BICO, SPELL on Bybit). Binance launched new USDT-M perps with the spot only from 2023
   on, and then typically 2-4 h after spot.
2. **The declared signal times are before the Binance perp exists.** The clean hedge (Binance perp) is live at
   +15 / +60 min in only 10 / 15 VAL events, and none of those showed a discount.
3. **Discounts are small and rare.** The new-listing spot book usually trades at or above the perp. The
   withdrawal lock does not create systematic cheapness; airdrop sellers are matched by first-day buyers.

## Random benchmark notes
- Same coin, same reference, a random entry second in [L0 + 15 min, L0 + 23 h], the same exit, the same taker-print
  fills and the same costs. 400 draws per event, 1,000 cell-sized sets.
- S15 cells beat 97-100 % of random sets, but n = 1 / 5, and SCR alone drives it. S60 cells beat 10-18 %.

## Pitfalls
- **spot_first.csv lists only coins that ever had a Binance USDT-M perp** (884 symbols; 410 of them have no spot
  pair). IB7's counts are that subset. Here the universe added the other data.binance.vision USDT symbols of coins
  with a Bybit perp. Coins with no perp anywhere cannot be hedged, so they were not needed.
- **The new-coin filter matters.** 27 / 18 / 4 / 13 / 0 USDT pairs (2020-24) were USDT pairs added for coins that
  already traded on Binance in another quote. Withdrawals were open for those, so they were dropped.
- **Renames / swaps** (13, e.g. EGLD, AAVE, RENDER, POL) were dropped. The declared list was corrected before any
  price data (see HYPOTHESES).
- **Listing clocks.** All 76 first prints fall exactly on round times (05:00 .. 18:00 UTC), so L0 is clean. W is still
  an approximation (L0 + 24 h).
- **Funding cadence.** Binance new perps from 2023 often had 4 h funding stamps (~15 stamps in 3 days). Real stamps
  were used (fapi / Bybit v5, pulled per window).
- **The S3 bucket host** (s3-ap-northeast-1.amazonaws.com) answered 403 to /robots.txt. Under the 403 rule it was not
  used; metadata came from data.binance.vision file probes (404s are probes of non-existent months).

## What a user decision could unlock
- **Little.** A registrable variant would move the signal to "Binance perp launch + k min" (so the Binance hedge
  exists). That is a new rule chosen after seeing these launch clocks. Its IS would still be ~0 events (2020-21 perps
  came weeks later), so it could only be a forward registration, at ~40-50 events a year with an unknown sign.
- **Exact withdrawal-open times** (the Zenodo file, IB L1) would not rescue the test. The discount events are too few
  regardless of W.

## Data and pull (research/data/listing_window/, git-ignored, 300 MB npz)
- **requests.log:** 2,314 lines, 18:18:50-18:38:45 UTC (~20 min).
  - data.binance.vision: 958 x 200, 918 x 404. The 404s are metadata month probes plus the robots.txt request.
  - public.bybit.com: 315 x 200, 1 x 404 (robots). api.bybit.com: 54 x 200, 1 x 404 (robots). fapi.binance.com:
    66 x 200.
  - s3 host: 1 x 403 (robots only).
  - No 418 / 429 / 503. Download total 8.1 GB; all zips / gz deleted (tmp empty).
- **npz/:** 76 spot, 65 Binance perp and 54 Bybit perp files: 1 s series over the listing day and the next day.
  Also meta/ (events_meta.csv, pull_list.csv, probe cache) and funding/ (119 files).
- **Subsample:** none. Web searches: 0.
