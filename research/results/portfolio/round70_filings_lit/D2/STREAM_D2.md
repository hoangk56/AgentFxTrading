# Round 70, stream D2: funding-formula carry, long Deribit perp / short Binance perp

Declared in [HYPOTHESES_D2.md](HYPOTHESES_D2.md) (17:44 UTC, timing amended 17:46 UTC, before any return). Code in
[code/](code/), outputs in [out/](out/). HOLD not opened. No 2025-26 data requested or loaded.

## Answer
- **The three always-on cells (BTC, ETH, BTC + ETH) pass the declared LIVE bar on IS / VAL**, including the cash bar
  (excess over DFF t >= 1.5). That bar is cleared only narrowly. I wrote **[PREREG_DRAFT_D2_ON.md](PREREG_DRAFT_D2_ON.md)**
  (registered cell: BTC + ETH ON) and stopped.
- **The economics are weak, and I expect the rule to earn the cash rate in HOLD.**
  - VAL excess over cash on C = N is only +1.37 %/yr (t 1.83), and it was negative in 2023.
  - HOLD power on the excess is 1.76, below 3.
  - About half the VAL net is spot-perp carry on the coin collateral (round 58's A1), not the D2 mechanism.
  - The Binance-Deribit funding gap itself shrank to ~1-2 %/yr for BTC in 2023-24.
- **F7 cells (on when the trailing 7-day gap > 0): none.** They meet the raw DEMO bar, but VAL excess over cash is
  negative (-0.18 to -0.75 %/yr). The ON cells dominate them, because F7 switches often and costs 3-4 %/yr.

## Funding formulas (data: research/data/deribit_funding/raw/docs/)
- **Deribit.** The 8h-rate is min(cap, max(-cap, max(0.025 %, P) + min(-0.025 %, P))), with P = (mark - index) / index.
  - The cap is ±0.5 % for BTC, ±1 % for ETH and ±5 % for the USDC perps.
  - Funding accrues continuously and has no interest leg (support articles 31424939178397 and 31424954847133).
  - I found no dated history of changes to the damper (2 WebSearches; an old Insights post mentions ±0.05 %).
  - The test uses realised hourly `interest_1h`. `interest_8h` is the trailing 8-hour sum (correlation 0.9999).
  - Daily sums agree with `get_funding_rate_value` to within ~4 % (window convention, 4 days checked).
- **Binance.** F = P + clamp(0.01 % - P, ±0.05 %) per 8h, from secondary sources (no primary page fetched). The test
  uses the realised stamps stored locally.
- **Realised levels by year (%/yr; Binance / Deribit / gap).** The share of Binance stamps at exactly 0.01 % was
  26-57 %, and the share of Deribit hours at exactly zero was 6-37 %.

| | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| BTC | 17.2 / 9.2 / **8.0** | 30.6 / 16.5 / **14.1** | 4.2 / -2.3 / **6.4** | 7.9 / 6.9 / **1.0** | 11.9 / 10.3 / **1.6** |
| ETH | 27.4 / 6.3 / **21.2** | 37.5 / 17.3 / **20.2** | 0.8 / -6.1 / **6.9** | 8.3 / 7.9 / **0.4** | 12.9 / 8.4 / **4.6** |

The Deribit USDC linear perps (from 2022-03) paid about what the inverse perps paid (BTC 2023: 5.3 vs 6.9; 2024:
10.5 vs 10.3). Switching to them would not change the conclusion.

## Construction
- **Positions.**
  - Short the Binance USDT perp, with USDT margin m = N/2.
  - Long the Deribit inverse perp with coin collateral m. The inverse size is V = N - M S, so that the account's USD
    delta is N, the same as the Binance leg.
- **Marks and trades.** Daily marks are at 00:00 UTC (close of the 23:00 1h bar). Trades happen at the mark, and the
  signal uses data up to 23:00.
- **Rebalancing.** The delta band is 5 %. Capital moves between the venues when either equity leaves [0.6, 1.6] m.
- **Costs.** Binance 0.06 % and Deribit 0.085 % per side, including half spread. Coin conversion costs 0.10 %.
- **Grading.** Capital C = N (L = 2), graded on excess over DFF.

## Results (net %/yr on N, NW t lag 10; excess over DFF on C = N)
| Cell | IS net (t, SR) | VAL net (t, SR) | VAL years | IS excess (t) | VAL excess (t) | x1.5 / late (VAL) | HOLD power raw / excess |
|---|---|---|---|---|---|---|---|
| BTC ON | 17.99 (7.11, 6.44) | 5.30 (6.79, 4.75) | 4.89, 4.59, 6.44 | 17.76 (7.05) | 1.35 (1.71) | 5.11 / 5.30 | 6.42 / 1.63 |
| ETH ON | 27.41 (8.75, 9.54) | 5.34 (6.39, 4.44) | 3.05, 4.44, 8.55 | 27.19 (8.70) | 1.39 (1.68) | 5.07 / 5.34 | 6.00 / 1.56 |
| BOTH ON | 22.70 (8.30, 8.65) | 5.32 (7.11, 5.07) | 3.97, 4.51, 7.50 | 22.47 (8.24) | 1.37 (1.83) | 5.09 / 5.32 | 6.85 / 1.76 |
| BTC F7 | 14.53 (5.60, 4.95) | 3.20 (3.52, 2.72) | 2.16, 2.82, 4.64 | 14.31 (5.52) | -0.75 (-0.84) | 1.36 / 2.91 | 3.68 / -0.86 |
| ETH F7 | 25.28 (8.03, 8.80) | 3.78 (4.07, 3.03) | 1.47, 2.71, 7.15 | 25.05 (7.97) | -0.18 (-0.20) | 2.34 / 3.71 | 4.09 / -0.20 |
| BOTH F7 | 19.91 (7.30, 7.56) | 3.49 (4.35, 3.36) | 1.82, 2.76, 5.90 | 19.68 (7.23) | -0.47 (-0.59) | 1.85 / 3.31 | 4.54 / -0.61 |

- **IS years.** Every IS year is positive in every cell.
- **Random benchmark.**
  - F7 with circular shifts of the on/off mask: IS beaten 98.2 / 98.8 / 95.0 % (BTC / ETH / BOTH), VAL 100 %.
  - ON: there is no timing to randomise. The random-side benchmark is weak and is beaten simply because net > 0.
- **Max-over-6-cells null.** The best cell's t is 8.75 in IS and 7.11 in VAL. The bootstrap 95th percentiles of the
  null maximum t are 2.42 and 2.48 (p < 0.001).

### Decomposition (%/yr of N)
| Era / cell | Binance funding received | Deribit funding paid | price leg | costs | pure gap f_B - f_D (on N) |
|---|---|---|---|---|---|
| IS BOTH ON | 29.70 | 5.77 | -0.38 | 0.85 | 15.87 |
| VAL BOTH ON | 7.95 | 1.96 | -0.21 | 0.46 | 3.47 |
| VAL BTC ON | 8.28 | 2.31 | -0.29 | 0.37 | 3.02 |

- **The price leg is close to zero.** The two perps (and the index under the collateral) do not drift apart on a
  daily book.
- **The funding leg is two things.** With coin collateral, Deribit funding is paid on V = N/2 only, while Binance
  funding is received on all of N. So the book is:
  - the D2 gap on N/2;
  - plus Binance funding on N/2 against spot coins, i.e. round 58's spot-perp carry.
- **The pure pair is weaker.** I ran it with USD-stable Deribit collateral, so that Deribit funding is paid on all of
  N (descriptive only). VAL net was BTC +4.01 (t 3.62) and ETH +4.94 (t 4.07). VAL excess over cash was BTC +0.06 %
  (t 0.05) and ETH +0.98 % (t 0.79). **On its own, the D2 mechanism did not beat cash in VAL.**
- **Excess over cash by VAL year (BOTH ON).** 2022 +2.28, 2023 -0.51, 2024 +2.34 (mean DFF 1.69 / 5.03 / 5.14 %).
- **Leverage sensitivity (BOTH ON, VAL).** In this construction, lower leverage means more coin collateral, and so
  more spot carry.

  | L | Capital | VAL excess | t |
  |---|---|---|---|
  | 1.5 | 1.33 N | +0.93 | 1.21 |
  | 2 | N | +1.37 | 1.83 |
  | 3 | 2/3 N | +1.79 | 2.46 |

## What failed and why, pitfalls
- **Premium arbitrage closed the anchor gap.** After 2022, Deribit's perp premium settled about 0.025 % above the
  index, so Deribit longs pay roughly Binance's anchor. The gap fell from 8-21 %/yr (2020-21) to 0.4-4.6 %/yr
  (2023-24). This is the same closing pattern as rounds 59 B1 / B2.
- **The inverse leg's coin collateral is a spot holding.** Any construction with Deribit inverse perps and coin margin
  mixes in spot-perp carry. Spot-perp carry is a cash-rate trade (round 58).
- **Liquidation at 2x per venue.** On daily marks with 1h last-price extremes, the check flags these IS days:
  - BTC 2020-03-12;
  - ETH 2020-03-12, 2021-01-03 and 2021-05-19;
  - ETH 2020-03-13, a 323 USDT last-trade wick on Binance (Binance liquidates on mark price).

  A live book needs intraday margin moves. Capital transfers in the simulation are instant at the mark, which is
  optimistic.
- **Fees.** The Deribit taker fee of 0.075 % applies to all years, which is conservative (the current schedule is
  0.05 %). Its dates of change were not found.
- **Data.** binance_basis/perp_1h ETHUSDT starts 2020-01-18, so I used binance_1h_full/1h. It matches binance_basis on
  99.995 % of the overlapping bars.

## What a user decision could unlock
The rule can only be LIVE as a cash-plus trade with venue risk at both Deribit and Binance. It earned about +1.4 %/yr
over cash in VAL and lost against cash in 2023. If HOLD (opened by the coordinator) shows excess t < 1.5, the
cross-venue funding family is closed at the cash rate.

## Files
- **Stream folder.**
  - [HYPOTHESES_D2.md](HYPOTHESES_D2.md), [PREREG_DRAFT_D2_ON.md](PREREG_DRAFT_D2_ON.md).
  - [code/](code/): fetch.py, pull.py, parse.py, d2.py, run.py, diag.py, usdc.py, hold_run.py (not run; guarded by
    `D2_HOLD=1`).
  - [out/](out/): report.txt, diag.txt, usdc.txt.
- **Data (research/data/deribit_funding/, 45 MB).**
  - requests.log: 238 requests, all 200 except the 404 for www.deribit.com/robots.txt (no robots file there), ≥ 0.6 s
    apart, plain UA, no e-mail.
  - raw/ (funding monthly, chart 200-day pages, docs, probes).
  - funding_*.csv and chart1h_*.csv for BTC / ETH inverse (2019-12..2024-12-31 23:00) and USDC perps (2022-03..).
