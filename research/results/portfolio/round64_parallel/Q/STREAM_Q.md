# Stream Q: derivative-vs-derivative basis on Binance (round 64)

Written Sun Nov 1 10:31 UTC 2026 (from `date -u`). Declared in [HYPOTHESES_Q.md](HYPOTHESES_Q.md) (08:54 UTC;
addendum 1 08:57 UTC, addendum 2 09:01 UTC, both before any P&L was computed). HOLD (2025+) never requested,
downloaded or loaded: monthly files <= 2024-12, daily 1m <= 2024-12-31, dapi funding end 2022-06-30, every series cut
at ts < 2025-01-01 at load.

## Answer
- **Q1 (COIN-M perp vs USDT-M perp), IS-chosen cell k100_H72: DEMO (formal pass), not LIVE.** At 1m entry T + 1 min:
  IS +439.8 bp/trade (t 2.20, n 54, 22 days), VAL +77.7 (t 3.82, n 181, 33 days), 5 / 5 years positive, x1.5 and
  T + 2 min positive in both eras, beats 100 % of random entries. LIVE fails on IS t (2.20 < 2.5) and power: per
  trade 5.11 but per event-day only **1.47**. Draft: [PREREG_DRAFT_Q_cm_um_perp_gap.md](PREREG_DRAFT_Q_cm_um_perp_gap.md).
  It is a **crash-day rule**: top 5 days = 95 % of IS and 98 % of VAL P&L (2021-04-18, 2021-05-19, LUNA 2022-05-11/12,
  FTX 2022-11-10). Outside the declared crash windows VAL is +12.6 bp (t 0.29). Weak DEMO, like B.
- **Q2 (delivery future vs USDT-M perp, term premium removed): none.** Every cell IS t <= 0.4, VAL <= 0.
- **Q2b (last-24 h convergence to delivery): none.** k10 / k20 negative in both eras, k30 has 5 trades per era.
- Daily P&L correlation of Q1_k100_H72 with C3: IS -0.006, VAL +0.008.

## Setup (as declared)
50 COIN-M perps (2020-08..2024-12, incl. delisted LUNA, FTM, MATIC) paired with their USDT-M perps; 167 COIN-M
quarterlies (BTC / ETH / ADA / LINK from 200925, BCH / BNB / DOT / LTC / XRP from 201225, EOS / ETC / FIL / TRX two
contracts, SOL 2) and 32 USDT-M BTC / ETH quarterlies (210326..241227), each vs its USDT-M perp. Bars valid with >= 20
trades on both legs. Signals on 1h closes; graded on 1m opens at T + 1 min (late T + 2, info T + 5), exit at the 1m open
1 min after the exit hour; bad-print guard (1h close = last 1m close within 1 bp on both legs). Funding at the real
stamps on both perps. Costs: 20 bp taker round trip + 2 x half-spread per leg (USDT-M 0.5 / 2 bp, COIN-M perp 1 / 3,
USDT-M quarterly 1.5, COIN-M quarterly 2 / 5); x1.5 reported. t clustered by entry UTC day. Random: matched contract /
era / hold length, side = fade of the residual at the random hour, 1,000 replications, on 1h opens (both sides).
Addendum 2: the 1h screen produced ~38k trades; 1m data was pulled for every trade of the Q1 k60 / k100 and Q2b
cells and of Q2_k100_H72 (capped 400 / era), and for 150 random trades / era of the other cells (8,458 daily files).

## All 15 cells (net bp per trade, t day-clustered)
| cell | IS 1h screen n / net (t) | IS 1m n / net (t) | VAL 1h screen n / net (t) | VAL 1m n / net (t) | x1.5 IS / VAL (1m) | T+2 min IS / VAL | random % IS / VAL |
|---|---|---|---|---|---|---|---|
| Q1_k30_H24 | 1159 / +18.3 (1.38) | 342 / +10.5 (0.89) | 2694 / -14.6 (-5.31) | 400 / -13.1 (-4.45) | -4.4 / -28.1 | +0.7 / -11.5 | 100 / 100 |
| Q1_k30_H72 | 1152 / +18.7 (1.41) | 335 / +9.9 (0.65) | 2560 / -14.1 (-4.87) | 397 / -18.4 (-7.86) | -5.1 / -33.4 | -1.0 / -20.9 | 100 / 100 |
| Q1_k60_H24 | 149 / +213.1 (2.32) | 121 / +215.9 (2.25) | 419 / +30.1 (1.67) | 400 / +22.5 (1.53) | +201.0 / +7.6 | +164.9 / +29.9 | 100 / 100 |
| Q1_k60_H72 | 146 / +218.2 (2.34) | 121 / +215.9 (2.24) | 373 / +35.2 (1.90) | 373 / +27.6 (1.91) | +201.0 / +12.7 | +164.9 / +35.6 | 100 / 100 |
| Q1_k100_H24 | 62 / +472.8 (2.39) | 54 / +439.8 (2.20) | 182 / +100.1 (3.39) | 182 / +82.9 (4.61) | +424.9 / +68.0 | +314.3 / +97.2 | 100 / 100 |
| **Q1_k100_H72** | 61 / +480.2 (**2.40**) | 54 / **+439.8 (2.20)** | 181 / +95.1 (3.06) | 181 / **+77.7 (3.82)** | +424.9 / +62.8 | +314.3 / +92.1 | 100 / 100 |
| Q2_k30_H24 | 10792 / -21.3 (-14.3) | 144 / -32.1 (-6.83) | 13236 / -25.8 (-52.2) | 148 / -21.7 (-7.71) | - | - | 100 / 100 |
| Q2_k30_H72 | 7659 / -17.9 (-10.4) | 146 / -29.0 (-4.90) | 10752 / -25.2 (-47.6) | 150 / -16.6 (-3.73) | - | - | 100 / 100 |
| Q2_k60_H24 | 5134 / -15.8 (-3.97) | 149 / -18.0 (-3.21) | 3416 / -21.8 (-15.6) | 149 / -20.1 (-5.85) | - | - | 100 / 100 |
| Q2_k60_H72 | 3370 / -10.0 (-2.35) | 148 / -11.5 (-1.49) | 2503 / -19.2 (-11.4) | 145 / -20.8 (-3.28) | - | - | 100 / 100 |
| Q2_k100_H24 | 2579 / -4.9 (-0.42) | 112 / -20.7 (-1.54) | 1127 / -13.7 (-3.39) | 118 / -9.2 (-1.36) | - | - | 100 / 100 |
| Q2_k100_H72 | 1619 / +4.9 (0.39) | 395 / +6.9 (0.36) | 748 / -6.7 (-1.34) | 393 / -1.3 (-0.25) | -9.2 / -17.6 | +2.0 / -3.4 | 100 / 100 |
| Q2b_k10 | 30 / -46.5 (-4.80) | 30 / -32.1 (-2.73) | 52 / -35.0 (-4.16) | 52 / -22.3 (-2.03) | - | - | 7 / 54 |
| Q2b_k20 | 13 / -32.9 (-3.40) | 13 / -18.8 (-0.59) | 17 / -23.1 (-1.66) | 17 / -10.0 (-0.66) | - | - | 53 / 95 |
| Q2b_k30 | 5 / +41.9 (0.44) | 5 / +6.7 (0.06) | 5 / +1.9 (0.06) | 5 / +52.3 (2.27) | -7.8 / +37.8 | -1.4 / +51.9 | 73 / 47 |
1m n for Q1_k30 and Q2 cells (other than Q2_k100_H72) are random subsamples (addendum 2). Max-over-15-cells random-entry
t: IS p50 0.39 / p95 1.37, VAL p50 0.08 / p95 0.57. Random entries lose ~-27..-33 bp (= costs), so "beats random" only
says the signal beats paying costs at random hours (same degenerate null as B). Q2 random % is 100 because random
loses more than the cell, not because the cell is positive. Full output: out/cells_1h.json, out/cells_1m.json,
out/trades_<cell>.csv.

## Q1_k100_H72 in detail (1m, T + 1 min)
- Years (n, net): 2020 (4, +88), 2021 (50, +468), 2022 (160, +84), 2023 (17, +10), 2024 (4, +107). Median IS +82,
  VAL +57; win 81 % / 88 %. Split VAL: price +105.8, funding +1.7, costs -29.8 bp.
- One minute of delay costs a lot in IS: T + 1 min +440 vs 1h open +534 (same trades), T + 2 +314 (t 1.56), T + 5 +180
  (t 1.58). In VAL the gap persists (T + 1 +78, T + 2 +92, T + 5 +89).
- Side: IS long COIN-M (COIN-M cheap) n 26 +670, short COIN-M n 28 +226; VAL long COIN-M n 140 +90, short n 41 +35.
  In VAL the gap opens mostly with the inverse perp below the linear perp, consistent with coin-collateral liquidations (a falling coin
  shrinks the collateral of long inverse positions, a cascade the linear book does not have); it closes
  within 1 h on 45 / 54 IS and 67 / 181 VAL trades.
- Concentration: top 5 days 95 % of IS (2021-04-18 52 %, 2021-05-19 38 %), 98 % of VAL (2022-05-11 35 %, 05-12 33 %,
  2022-11-10 24 %). Top coins IS EGLD, ETC, BCH, LTC, UNI; VAL LUNA, SOL, FTM, ROSE, DOT. Ex crash windows (B's list,
  information only): IS n 34 +432 (t 1.36; 2021-04-18 is not in the list), VAL n 38 +12.6 (t 0.29, median +34.6).
- Fill proxy: |open(T+1m) / close(T..T+1m) - 1| on the COIN-M leg median 5.2 / 5.7 bp, p90 34 / 38 bp (IS / VAL),
  USDT-M leg 2.0 / 1.0 bp (p90 28 / 6). The declared COIN-M alt half-spread (3 bp) is below the median jump; with a 15
  bp COIN-M half-spread (5x, information) the cell is IS +416, VAL +54 bp.
- Power at VAL size: 60 trades / yr on 11 event-days / yr; per trade SR 0.49 x sqrt(110) = 5.11, per event-day SR 0.33
  x sqrt(20) = 1.47. Trades on one crash day are one bet, so 1.47 is the honest figure: LIVE is out of reach even if IS
  t were higher.
- Bad-print guard dropped 7 IS trades (4 because the 2020-09 daily 1m files of ADAUSD_PERP / BNBUSD_PERP are missing in
  the bucket, 3 on mismatched closes); their 1h-open net was +69 bp on average (below the cell mean), so the guard raises the IS mean (1h open: +480 on all 61, +534 on the 54 kept).

## What failed and why
- **Q1 at k30**: the COIN-M / USDT-M gap is a 15-50 bp wedge that the 30 bp round-trip eats (VAL price leg +15 bp vs
  30 bp costs). At k60 VAL is +22 / +28 bp (t 1.5-1.9) but 2023 is negative; IS k100 was chosen on IS t (2.40 vs 2.34).
- **Q2**: after removing the trailing annualised term premium, quarterly residuals are frequent (thousands of > 30 bp
  events, mostly thin COIN-M alt quarterlies) but they do not converge net of costs: the price leg is +4..+57 bp, and
  the short-perp hedge pays funding (-5..-18 bp) when the quarterly is cheap in bull markets. BTC / ETH quarterlies:
  residuals rarely exceed costs. The quarterly basis is a slow-moving rate, not a wedge with a fast anchor.
- **Q2b**: 24 h before expiry the quarterly is within ~10-30 bp of the perp; the remaining convergence (price leg
  -5..+23 bp at k10-k20) is below the 27-28 bp cost of four legs. Delivery is arbitraged; the brief already warned that
  ~4 expiry days / yr cannot reach power.

## Pitfalls for later rounds
- data.binance.vision `futures/cm/monthly/fundingRate` starts only in 2022-07; earlier COIN-M funding came from the
  public dapi `/dapi/v1/fundingRate` (end time 2022-06-30). Without it IS funding on the COIN-M leg would be 0.
- `binance_basis/perp_1h` covers only each coin's top-60 window (e.g. AXS ends 2024-01, ROSE 2022-02..2023-03); full
  USDT-M histories for the 50 coins are now in `research/data/binance_cm/um_klines_1h/`.
- The `/futures/data/delivery-price` endpoints have no end-time parameter (they would return HOLD deliveries); the
  settlement was proxied by the 30-min mean of the quarterly's 1m closes.
- A few daily 1m files are missing in the bucket (121 x 404, mostly 2020-09 COIN-M alts).
- The 1h-open price (B's convention) overstates IS by ~20 % vs T + 1 min on crash days; always reprice on 1m.

## What a user decision could unlock
- Approve opening HOLD for the Q1 draft (DEMO only). Expect few HOLD event-days unless HOLD contains COIN-M liquidation
  cascades; the draft says HOLD with < 3 event-days is inconclusive. Execution needs a COIN-M account with coin
  collateral (or Binance portfolio margin) and fills in thin COIN-M alt books during crashes; a paper bot logging the
  COIN-M book at signals would measure the real half-spread. LIVE odds < 3 %, DEMO odds ~20-30 % (HOLD net > 0 is
  likely if any cascade happens; the rule is mechanical).
- Q1 and B fire on the same crash days (2021-05-19, LUNA, FTX); as a book they are not independent bets.

## Data pulled (research/data/binance_cm/, requests.log 15,740 lines, 647 MB)
- cm_klines_1h/ (50 perps + 167 quarterlies), cm_fundingRate_-/ (50, from 2022-07), cm_funding_dapi/ (50, 2020-07..
  2022-06), um_klines_1h/ (50 USDT-M perps + 32 BTC / ETH quarterlies), m1/{cm,um}/<SYM>/<day>.csv (8,458 daily
  files, t / o / c / n). 08:53-10:30 UTC; non-200: 121 x 404 (missing daily files), ~15 transient
  timeouts / resets (retried), no 403 / 418 / 429. robots.txt: 404 on both hosts (logged). The 1m pull was stopped
  at the declared ~40 min cap with ~100 of 8,560 days not fetched (Q2 sample cells only).
- No WebSearch used.

## Files
HYPOTHESES_Q.md, STREAM_Q.md, PREREG_DRAFT_Q_cm_um_perp_gap.md; code/q.py (loader, rules), code/run.py (screen / 1m
grade / random), code/pull_vision.py, code/pull_m1.py, code/pull_dapi_funding.py, code/prio.py, code/conc.py,
code/info_q1.py, code/corr_c3.py (information); out/cells_1h.json, out/cells_1m.json, out/selection.csv,
out/trades_<cell>.csv.
