# Stream K (round 64): Korean venue (Upbit) flows -> Binance USDT-M perps

Written 2026-11-01 ~10:00 UTC. Hypotheses declared in [HYPOTHESES_K.md](HYPOTHESES_K.md) at 08:57 UTC, before any premium
or return was computed. HOLD (2025-01-01..) was never requested, loaded or counted.

## Answer first
**K1 (coin-specific kimchi premium): none.**
- No cell reaches IS t 2.0. The best is L-DEV-k200-H72: IS +51 bp, t 1.78; VAL -25 bp, t -0.77.
- That is inside the max-of-16-cells null (~2.0-2.4).
- **The gap closes on the Upbit side.** Korea's coin price falls back. The Binance leg, the only part we can earn,
  carries ~20-25 % of the closing in IS and nothing (or less) in VAL.
- The r < -k (short) side flips sign: IS negative in every cell, VAL positive in 2024.

**K2 (fade the Upbit KRW listing pump on Binance): DEMO candidate, not LIVE.**
- Rule: short the alt perp / long BTC perp at L + 1 h, hold 72 h (IS-chosen).
- IS +1094 bp/trade, t 3.16 (n 11). VAL +423 bp, t 1.37 (n 29).
- 5 / 5 years positive. Beats 100 % of random entries (other alts at the same time, and the same coin at other
  times).
- Positive at costs x1.5 and with late entries.
- Power at VAL size ≈ 1.07, so it cannot reach LIVE.
- [PREREG_DRAFT_K_upbit_listing_fade.md](PREREG_DRAFT_K_upbit_listing_fade.md) is written. The coordinator opens
  HOLD.

## Data (all public, no key, no e-mail; research/data/upbit/requests.log)
**Upbit (api.upbit.com).**
- robots.txt returned 404 (no file; logged 08:53:07).
- 2809 requests, >= 0.26 s apart, 3 threads with a shared lock.
- `/v1/market/all`: 299 KRW markets. 139 of them have a Binance USDT-M perp that started before 2025.
- 240-minute candles cover 97 coins with KRW history before 2025, from max(2019-12-20, perp start - 8 d) to
  2024-12-31 20:00.
- 60-minute candles were pulled for the first hours of 40 listings.

**Binance.**
- fapi REST: 6401 requests. These fetched 1m klines around every K1 / K2 entry and exit, 1h klines for MORPHO and
  ZETA, and funding for 15 symbols with no local file.
  - fapi robots.txt disallows only named search engines.
- data.binance.vision: BTCUSDT perp 1m monthly zips for 2020-01..2024-12. There is no 2019-12 file (404).
- Local 1h perp klines and funding files (binance_1h_full, binance_basis, binance/perp_1h) were cut at
  ts < 2025-01-01 at load.

**Failures.** 3 × 404 (robots ×2, one zip), 14 timeouts / URL errors, all retried. No 403, 418 or 429.

**Deviation (declared before computing).** K1 uses Upbit 240-minute candles instead of 1h.
- A 60-minute pull ran at 1.2 req/s (0.7 s latency) and needed ~14.5k requests, about 3.3 h.
- Signals are on 4h closes (00/04/... UTC). Fills are on 1m bars 1 minute after the bucket end.

**Name-collision guard.** It dropped one coin, BTT: median |r| = 6.9, a 1000x redenomination mismatch with Binance's
old BTTUSDT. 95 coins remain in K1.

## K1 results
**Rule.** `r = ln(U_coin/U_BTC) - ln(B_coin/B_BTC)` at 4h closes, with an Upbit KRW value >= 40 M per bucket.
- RAW signal: r. DEV signal: r minus its trailing 42-bucket median.
- Long the alt perp / short BTC perp when the signal is > k. Exit when it halves, or after H.
- Short cells mirror this for signal < -k.
- Costs: 32 bp plus real funding.

Columns below:
- **m1**: 1m fill at T + 1 min (main).
- **m5**: fill at T + 6 min.
- **h1**: fill at the next 1h close.
- **rand**: percentile of the h1 gross against 500 draws of the same coin, same quarter and same holding, at random
  times.
- **du / db**: mean change of the Upbit leg / Binance leg (log, bp) from signal to exit bucket.

Full output: k1_table.txt, k1_results.json.

| cell | era | n | gross | fund | **net** | **t** | SR | net x1.5 | m5 | h1 | rand % | du | db | years net |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L-RAW-k200-H24 | IS | 682 | +46 | +2 | +16 | 0.76 | 0.04 | +0 | +18 | +9 | 95 | -128 | +32 | 2020 -58, 2021 +49 |
| | VAL | 822 | +5 | +12 | -15 | -0.65 | -0.03 | -31 | -16 | -25 | 64 | -156 | -6 | -24, -30, +43 |
| L-RAW-k200-H72 | IS | 493 | +62 | +4 | +34 | 1.21 | 0.06 | +18 | +37 | +27 | 95 | -185 | +45 | -60, +71 |
| | VAL | 536 | +1 | +20 | -11 | -0.34 | -0.02 | -27 | -13 | -18 | 65 | -263 | -12 | -23, -41, +61 |
| L-RAW-k500-H24 | IS / VAL | 343 / 403 | | | -11 / -8 | -0.40 / -0.29 | | | | | 49 / 88 | | | |
| L-RAW-k500-H72 | IS / VAL | 193 / 207 | | | +16 / +9 | 0.36 / 0.18 | | | | | 74 / 92 | -269 / -371 | +22 / -5 | |
| L-DEV-k200-H24 | IS | 525 | +62 | +2 | +32 | 1.27 | 0.07 | +16 | +38 | +18 | 98 | -170 | +53 | -13, +48 |
| | VAL | 620 | +4 | +12 | -15 | -0.57 | -0.03 | -31 | -16 | -25 | 60 | -160 | -6 | -1, -49, +3 |
| **L-DEV-k200-H72 (best IS)** | IS | 449 | +81 | +3 | **+51** | **1.78** | 0.10 | +35 | +57 | +33 | 98 | -203 | +66 | +25, +60 |
| | VAL | 471 | -11 | +18 | **-25** | **-0.77** | -0.05 | -41 | -24 | -27 | 48 | -230 | -18 | -12, -72, +8 |
| L-DEV-k500-H24 | IS / VAL | 147 / 228 | | | +5 / +2 | 0.13 / 0.05 | | | | | 76 / 88 | | | |
| L-DEV-k500-H72 | IS / VAL | 112 / 155 | | | +24 / -32 | 0.38 / -0.73 | | | | | 68 / 76 | | | |
| S-RAW-k200-H24 | IS / VAL | 161 / 179 | | | -61 / +33 | -1.17 / 1.51 | | | | | 7 / 99 | +227 / +22 | +2 / -73 | VAL 2024: 151 trades |
| S-RAW-k200-H72 | IS / VAL | 139 / 93 | | | -71 / +114 | -1.19 / 2.77 | | | | | 10 / 99 | +271 / +12 | +7 / -162 | |
| S-RAW-k500-H24 | IS / VAL | 19 / 141 | | | -83 / +6 | -0.56 / 0.24 | | | | | 87 / 82 | | | |
| S-RAW-k500-H72 | IS / VAL | 18 / 59 | | | -72 / +92 | -0.55 / 1.68 | | | | | 91 / 89 | | | |
| S-DEV-k200-H24 | IS / VAL | 257 / 325 | | | -63 / -12 | -1.59 / -0.48 | | | | | 9 / 80 | | | |
| S-DEV-k200-H72 | IS / VAL | 207 / 197 | | | -37 / +6 | -0.73 / 0.15 | | | | | 30 / 81 | | | |
| S-DEV-k500-H24 | IS / VAL | 65 / 135 | | | -75 / +13 | -0.89 / 0.40 | | | | | 38 / 92 | | | |
| S-DEV-k500-H72 | IS / VAL | 45 / 76 | | | -111 / +82 | -0.97 / 1.22 | | | | | 23 / 96 | | | |

**Why K1 fails.**
- **The mover is Korea.** In the long cells the Upbit leg falls 130-400 bp and the Binance leg moves +22..+66 bp in
  IS and -29..+10 bp in VAL. So the Binance share of the closed gap is ~15-25 % in IS and ≈ 0 or negative in VAL.
  This is the same structure as round 63 BX: the anchor side does not move.
- **The IS edge before costs is 46-81 bp.** It is a 2021-only effect (2020 negative in most cells), and it is gone
  in 2022-23.
- **A few coins with long wallet suspensions dominate.** IOTA (Chrysalis migration), KAVA and WAVES give 614 of the
  1511 L-RAW-k200-H24 trades. Arbitrage was impossible there, so no Binance buying flow existed.
- **The short side (Korean discount) is positive only in VAL.** Mostly 2024: 151 of 179 trades in S-RAW-k200-H24.
  It is negative in IS in every cell: a sign flip, not a candidate.
- **Cell choice by IS.** The best IS cell is L-DEV-k200-H72 at t 1.78. With 16 correlated cells, the expected max |t|
  under the null is ~2.0-2.4, so nothing in IS clears chance.
- **Not run.** The declared robustness checks (trailing beta, excluding 2020-03 / 2021-05) only apply to a passing
  cell, and none passed.

## K2 results
**Rule.** Event L = the first Upbit KRW 60-minute candle of a coin whose Binance perp is >= 7 days old. There are 40
events in 2020-04..2024-12: 11 in IS, 29 in VAL; list in k2_events.csv.
- Short the alt perp / long BTCUSDT perp at the 1m close at L + 1 h.
- Hold 24 or 72 h.
- Costs: 42 bp plus real funding.

Full output: k2_output.txt, k2_random.txt, k2_pumpctrl.txt.

| cell | era | n | gross | fund | **net** | **t** | median | sd | SR | x1.5 | +5 min | L + 2 h | years |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H72** | IS | 11 | +1150 | -14 | **+1094** | **3.16** | +1054 | 909 | 1.20 | +1073 | +997 (2.87) | +913 (2.94) | 2020 +555 (4), 2021 +1402 (7) |
| | VAL | 29 | +570 | -105 | **+423** | **1.37** | +619 | 1666 | 0.254 | +402 | +399 (1.31) | +431 (1.55) | 2022 +378 (3), 2023 +1026 (9), 2024 +111 (17) |
| H24 | IS | 11 | +729 | -14 | +673 | 2.22 | +477 | 791 | 0.85 | +652 | +565 (1.84) | +473 (1.80) | +185, +952 |
| | VAL | 29 | +518 | -87 | +389 | 1.96 | +384 | 1069 | 0.36 | +368 | +378 (1.92) | +392 (2.29) | -5, +601, +346 |

**Random benchmark** (gross on 1h closes, 500 draws):
- H72 events beat 100 % of draws in both eras, against two kinds of draw:
  - other universe alts at the same hour: medians -143 bp IS, -72 bp VAL;
  - the same coin at random hours 30-180 days after listing: medians -47 / -17 bp.
- H24 also beats 100 % of draws.

**Post-hoc control (it chose nothing).** Shorting any alt after a non-listing 24 h run-up of 10 % or 20 % loses on
the mean: H72 -81 to -293 bp, t -2.3 to -3.0, with positive medians. That is the round 60 squeeze-tail pattern. So
the listing fade is specific to the listing.

**Run-up.** From L - 24 h to the entry the alt gains +21.5 % against BTC: Upbit announces before trading opens, and
the pump is already in.

**Tails** (VAL H72 worst trades): ID -4669, CKB -3098, MEW -1002 bp. Without the best trade: IS +895, VAL +266.

**Bars for H72 (chosen on IS: t 3.16 vs 2.22).**
- **LIVE: fails.**
  - Passed: IS t 3.16 >= 2.5; years 5 / 5; random 100 %.
  - VAL t 1.37 < 1.5.
  - Power = 0.254 × sqrt(9.7/yr × 1.83) ≈ **1.07** < 3. Even at 30 listings a year in HOLD it would be ~1.9.
- **DEMO: passes**, on IS t >= 2, VAL net > 0, random >= 90 %, x1.5 costs and late entries.
- **The case is thin.** IS is 11 trades on 9 days, with fat tails.

**C3 daily-P&L correlation:** IS -0.003, VAL -0.034 (H24: -0.002 / -0.007).

## Biases from Upbit's current-only market list
**Missing markets.** Delisted Upbit markets and renamed old codes are missing.
- K1 long: flattered, since survivors are the Korean winners. It failed anyway.
- K1 short: loses its delisting-dump episodes.
- K2 short: probably conservative, since listings that later faded and were delisted are absent.

**K2 universe.** Only coins that had a Binance perp >= 7 days before their KRW listing.

## Pitfalls met
- **Network.** Upbit latency was ~0.7 s per request with network contention from the other streams, which forced
  the 240-minute choice.
- **Name collisions.** BTT (old vs redenominated) needed the declared guard. Upbit's TON (Tokamak) never matched,
  because there is no TONUSDT perp before 2025 in our list.
- **BTC 1m gap.** BTCUSDT perp 1m for 2019-12 is missing on data.binance.vision. A few Dec-2019 K1 trades were
  dropped for lack of BTC fills.
- **Delisted renames.** Upbit RENDER 2024-12-05 04:00 UTC is a genuine KRW listing: Upbit's announcement says
  13:00 KST, during the RNDR -> RENDER migration (bloomingbit / Blockmedia). One WebSearch was used.

## What a user decision could unlock
- **Paper bot for K2.** K2 needs only perps (no borrow). Building it would mean: poll Upbit `/v1/market/all`, and when
  a new KRW market appears for a coin with a Binance perp, short at L + 1 h and hold 72 h. It would measure the real
  first-hour spread.
- **Power stays below LIVE** at any plausible listing pace. Pooling with other venue-listing fades (Bithumb KRW,
  Coinbase listings) is a separate, new hypothesis.

Code: round64_parallel/K/code/ (kdata, k1, k1run, k2, fills, net, pull_upbit, pull_binance, k2_pumpctrl, c3corr).
