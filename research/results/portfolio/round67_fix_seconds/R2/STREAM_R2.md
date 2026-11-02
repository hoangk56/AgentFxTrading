# Stream R2 (round 67): rotation out of Upbit-heavy coins after an Upbit KRW-listing notice

Written Sun Nov 1 15:17 UTC 2026 (from `date -u`). The hypotheses and the 6 cells were declared in
[HYPOTHESES_R2.md](HYPOTHESES_R2.md) at 14:54:41 UTC, before any price was requested. HOLD (2025-01-01..) was never
requested, loaded or counted: every series is cut at ts < 2025-01-01, and every fapi request asserted
endTime < 2025-01-01.

## Answer first: none (no LIVE, no DEMO), because IS fails. VAL is strong
**No cell reaches IS t 2.0**, so none qualifies for DEMO or LIVE, and no PREREG_DRAFT is written.
- **IS pick:** BTC-L1H, the cell with the highest IS t.
  - IS +91 bp per notice, t 1.09, n 9.
  - VAL +60 bp, t 3.29, n 32.
- **The rotation itself is real in both eras.** In the gross numbers, Upbit-heavy coins fall against BTC from the
  notice to the KRW open, and every cell beats 89-100 % of random draws in both eras.
- **IS cannot carry the bar.** It has 9 notices, and 6 of them were posted 4 min before the KRW open. Those 6 trades
  are 2-minute holds that only pay the ~30 bp cost (-21 bp net, t -1.94). The 3 IS notices with a real lead time make
  +275 bp net (t 0.86, n 3).
- **BTC-L in VAL passes every VAL-side LIVE bar.** It is not selectable, because its IS t is only 0.74:
  - +71 bp per notice, t 3.96, SR 0.70, n 32.
  - It beats 100 % of 2,000 random books (z 5.5).
  - At costs x 1.5 it makes +56. One bar late it makes +72 (t 4.24). Entry 5 min late gives +61.
  - Without the best trade it makes +63.
  - Years positive: 4 / 5 (2020 is the only losing year, with 3 notices that hold 2 to 37 min).
  - Power at VAL size: 3.09.
- **Max-over-6-cells null, random books, net of cost:**
  - IS: median t -0.12, 95th percentile 1.28.
  - VAL: median t -0.69, 95th percentile 0.75.
  - The VAL t of 2.0-4.0 on the BTC cells sits far outside the VAL null.
- **C3 daily-P&L correlation** (information only, since no cell has DEMO numbers):
  - BTC-L: -0.008 (IS) and -0.020 (VAL).
  - BTC-L1H: -0.007 (IS) and -0.019 (VAL).

## Data
**Events.** round65 A's notice_events_L.csv (read-only) gives 41 notices: IS 9 notices on 9 days, VAL 32 on 32 days.
- SRM is dropped, because its L is unknown.
- L = the earliest KRW open among the notice's coins. MATIC uses SOL's L. STG and BONK use stated + 5 min.

**Basket.** Stream R's point-in-time panel (research/data/korea_hours/panel.npz and rdata.py, read-only).
- Universe: the top-60 perps by mean daily quote volume over days d-30..d-1.
- Share: 30-day Upbit KRW value (in USD) / Binance perp quote volume.
- High tercile = the top floor(n/3) of the Upbit-listed coins (6.4 coins on average in IS, 7.6 in VAL); low tercile =
  the bottom floor(n/3). The listed coin and BTC are excluded.
- Typical high-tercile coins:
  - 2020-21: XRP, QTUM, IOST, ADA, XLM, SAND.
  - 2022-23: WAVES, MTL, KAVA, STX, SAND.
  - 2024: STX, SEI, 1000SHIB, XRP, ETC.

**1m prices.**
- Local research/data/binance_1m_wicks/npz covers 10,662 of the 13,534 (symbol, window) pairs.
- fapi.binance.com /fapi/v1/klines fetched the remaining 2,872, plus 5 re-fetches of windows that shared a start
  with another window.
  - Totals: 2,876 requests with status 200 and 1 timeout (retried); no 403, 418, 429 or 503.
  - Requests started >= 0.3 s apart (shared lock, 3 threads); the pull ran 14:56-15:16 UTC.
  - robots.txt was logged first. It disallows only named search engines.
- Funding comes from stream R's hourly grid.
- Every real trade has its full basket priced; no coin was dropped.

## Rule (as declared)
- **Entry:** the close of the first 1m bar that opens at or after N + 60 s, i.e. 2-3 min after the notice.
- **Position:** short the high-share tercile (equal weight, $1) and long the hedge ($1). The hedge is BTCUSDT perp or
  the low-share tercile.
- **Exit:** at L (the KRW open), at L + 1 h, or at L + 6 h.
- **Cost:** taker 5 bp per side per leg, plus a half-spread of 1 bp for BTC, 3 bp for volume rank < 20 and 5 bp
  otherwise. That is about 30 bp round trip for the BTC cells and about 36 bp for the LOW cells. Real funding is
  added.
- **t:** clustered by notice day.
- **Random benchmark:** 20 draws per notice. Each draw uses the same basket, hedge, minute of day and entry -> exit
  offsets, on a random KST weekday within ±60 days that is >= 2 days from any notice, in the same era. The percentile
  is of the real gross mean among 2,000 books, each book taking one draw per notice.
- **Power:** VAL SR x sqrt(19.5). HOLD n is estimated at the VAL rate of 10.7 notices a year x 1.83 years.

## Results (r2_output.txt, r2_results.json; net bp per notice)
- **x1.5:** net at costs x 1.5.
- **late:** entry and exit one 1m bar later.
- **late5:** entry 5 min later. In the IS -L cells only 3 notices still have entry < L.
- **hold:** median entry -> exit in minutes.

| cell | era | n | net | t | SR | gross | cost | x1.5 | late (t) | late5 | rand % | hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-L | IS | 9 | +77 | 0.74 | 0.25 | +107 | 30 | +62 | +63 (0.70) | +271 (n 3) | 100 | 2 |
| BTC-L | VAL | 32 | **+71** | **3.96** | **0.70** | +102 | 31 | +56 | +72 (4.24) | +61 | 100 | 155 |
| **BTC-L1H (IS pick)** | IS | 9 | +91 | 1.09 | 0.36 | +120 | 30 | +76 | +88 (1.05) | +81 | 100 | 62 |
| BTC-L1H | VAL | 32 | +60 | 3.29 | 0.58 | +91 | 31 | +45 | +59 (3.31) | +50 | 100 | 215 |
| BTC-L6H | IS | 9 | +31 | 0.32 | 0.11 | +60 | 30 | +16 | +28 (0.29) | +21 | 90 | 362 |
| BTC-L6H | VAL | 32 | +54 | 2.04 | 0.36 | +85 | 31 | +39 | +50 (1.91) | +44 | 100 | 515 |
| LOW-L | IS | 9 | +10 | 0.32 | 0.11 | +45 | 36 | -8 | +7 (0.30) | +90 (n 3) | 100 | 2 |
| LOW-L | VAL | 32 | +26 | 2.54 | 0.45 | +63 | 37 | +8 | +29 (2.87) | +20 | 100 | 155 |
| LOW-L1H | IS | 9 | +21 | 0.84 | 0.28 | +56 | 36 | +3 | +21 (0.86) | +18 | 98 | 62 |
| LOW-L1H | VAL | 32 | +28 | 2.28 | 0.40 | +65 | 37 | +10 | +26 (2.21) | +21 | 100 | 215 |
| LOW-L6H | IS | 9 | +35 | 1.01 | 0.34 | +70 | 36 | +17 | +29 (0.80) | +31 | 89 | 362 |
| LOW-L6H | VAL | 32 | +25 | 1.25 | 0.22 | +62 | 37 | +6 | +21 (1.06) | +18 | 99 | 515 |

**By year** (net bp; n = 3 / 6 / 3 / 9 / 20 notices in 2020-24):

| cell | 2020 | 2021 | 2022 | 2023 | 2024 | yrs + | power |
|---|---|---|---|---|---|---|---|
| BTC-L | -48 | +140 | +143 | +88 | +53 | 4/5 | **3.09** |
| BTC-L1H | -61 | +167 | +116 | +102 | +33 | 4/5 | 2.57 |
| BTC-L6H | -112 | +103 | +70 | +88 | +36 | 4/5 | 1.59 |
| LOW-L | -26 | +28 | +25 | +51 | +16 | 4/5 | 1.98 |
| LOW-L1H | -32 | +47 | +13 | +56 | +18 | 4/5 | 1.78 |
| LOW-L6H | -8 | +56 | +9 | +36 | +22 | 4/5 | 0.98 |

**Gross path** (long BTC / short the high tercile, from the price 1-2 min before N; mean bp, with the same-basket
random-day mean in brackets):

| | entry | +5 m | +15 m | +30 m | +60 m | L | L + 1 h | L + 6 h |
|---|---|---|---|---|---|---|---|---|
| IS | +5 (+1) | +16 (0) | +22 (+1) | +57 (+1) | +54 (+1) | +115 (0) | +127 (0) | +66 (-15) |
| VAL | +2 (-1) | +11 (0) | +23 (0) | +37 (+1) | +36 (0) | +107 (-2) | +96 (0) | +96 (-2) |

- **The move is gradual, not a jump.** There is almost nothing between before the notice and the entry 2-3 min later.
  The fall then builds through the lead time: in VAL it is +28 / +40 / +70 / +102 bp at 25 / 50 / 75 / 100 % of the
  way from entry to L.
- **It stops at L and does not revert within 6 h.** Rotation cash is raised before the KRW open.
- **The random-day path is flat**, so the move is not the stream R Korean-day rhythm. The draws match the minute of
  day and the weekday.

## Post hoc (information only; r2_posthoc.txt, code/posthoc.py)
**Random books (20,000).** BTC-L gross is z 8.7 (IS) and z 5.5 (VAL) above the random-mean distribution. The
largest random VAL mean is +83 bp, against +102 real.

**Lead time.**

| cell | split | n | net | t |
|---|---|---|---|---|
| BTC-L | IS, lead >= 30 min | 3 | +275 | 0.86 |
| BTC-L | IS, lead < 30 min | 6 | -21 | -1.94 |
| BTC-L | VAL, lead >= 120 min | 19 | +91 | 3.51 |
| BTC-L | VAL, lead < 120 min | 13 | +42 | 1.97 |
| LOW-L | VAL, lead >= 120 min | 19 | +48 | 3.45 |
| LOW-L | VAL, lead < 120 min | 13 | -5 | -0.40 |

The lead-time splits fit the mechanism: the longer the window before the open, the more cash is raised.

**VAL halves (BTC-L).** 2022-23: +102 bp (t 2.82, n 12). 2024: +53 bp (t 2.85, n 20). The effect weakens as
Upbit lists more often, but it holds in both halves.

## Why it fails the bar
1. **The IS sample is structural, not noisy.** In 2020-21 Upbit usually posted the notice when the market opened
   (lag 4 min), so 6 of the 9 IS trades are 2-minute holds. These give the same answer in every cell: about -cost.
   IS t >= 2.0 would need an IS per-notice SR of about 0.7 on 9 trades. That was flagged as near impossible in the
   power arithmetic before the run.
2. **The IS t rests on one notice.** 1INCH / AAVE (2021-10-27) makes +912 bp in BTC-L. Without it, IS BTC-L is
   -27 bp.
3. **The bar picks the cell on IS.** The IS pick, BTC-L1H, has VAL power 2.57, which is below 3. The best VAL cell,
   BTC-L, cannot be chosen from VAL.

## Pitfalls met / biases
- **Self-matching waiters.** Wait loops built on `pgrep -f "<script path>"` matched their own shell command line and
  never ended. They were killed, and the wait was done by PID instead. No data impact.
- **File-name collisions in the raw cache.** fapi windows were saved under symbol + start time. 122 pairs share a
  start but have different ends; 5 of those were truncated and were re-fetched. After the re-run only two
  random means moved, by 0.2 bp; net and t did not change.
- **Survivorship.** The Upbit share uses stream K's current-only Upbit market list. Coins delisted from Upbit before
  2026, for example LUNA and EOS, are missing from the baskets, while WAVES, MTL and others are present. Delisting
  candidates tend to be Upbit-heavy and weak, so the direction of the bias is unclear. The notice list itself comes
  from Upbit's notices and has no survivorship.
- **Basket size.** The high tercile averages 6-8 coins, so one coin's news can move a trade: IMX 2023-07 -65 bp,
  BIGTIME 2024-09 -62 bp.
- **Entry delay.** Entry is at the close of the first bar opening at or after N + 60 s, i.e. 2-3 min after the
  notice. That is slower than a bot, but the move is gradual, so a faster entry would add little (+2 to +5 bp from
  before N to entry).

## What a user decision could unlock
- **A HOLD test of BTC-L as a VAL-discovered rule.** IS 2020-21 cannot test this mechanism: Upbit posted at the open.
  The coordinator could pre-register BTC-L unchanged for HOLD and state plainly that IS failed. That is a bar
  exception, and it is the coordinator's or user's call, not mine.
  - VAL: SR 0.70, power 3.09 at the VAL notice rate, about 4.2 if HOLD lists as often as 2024 (n ~37).
  - Its C3 correlation is about 0.
  - Expected HOLD net: about +50 bp per notice at the 2024 level.
- **More events from the same mechanism.** The trade does not need the listed coin to have a Binance perp. Stream A
  dropped KRW listings of coins with no perp or with BTC/USDT-only markets: SAND, STX, FLOW, APT, SUI, SEI, MNT, ZRO
  and others, about 20 more notices in 2020-24.
  - A declared re-run on those notices, which were never priced here, would be an out-of-sample check inside 2020-24
    before HOLD.
  - The notice bodies are already in research/data/upbit_announce/ (A/notice_events.csv), and the KRW open needs the
    Upbit candle API.
- **Execution.** The move takes hours (lead median 155 min in VAL), so taker execution of a 7-coin basket is enough.
  No seconds-level race is needed. Maker entry would cut the ~30 bp cost.

## Files
- **This folder:** HYPOTHESES_R2.md, STREAM_R2.md, r2_output.txt, r2_results.json, r2_posthoc.txt.
- **code/:**
  - build.py: notices, baskets, random shifts, windows.
  - fetch.py: polite fapi pull.
  - fetch_dups.py: truncated-window refetch.
  - run.py: cells, checks, random benchmark, max null.
  - posthoc.py
- **research/data/upbit_rotation/:**
  - plan.json, windows.csv
  - raw/ (2,856 fapi responses)
  - requests.log, robots_fapi.txt, fetch.out, invalid_syms.json (empty)
  - trades.npy (per-cell net per notice, for C3 / coordinator)
