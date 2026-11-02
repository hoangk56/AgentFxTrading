# Stream S (round 64): stablecoin peg reversion on Binance spot

Written 2026-11-01 10:28 UTC (from `date -u`). Hypotheses (09:52 UTC, before any data):
[HYPOTHESES_S.md](HYPOTHESES_S.md), with an addendum on the fill check. HOLD not opened, no 2025-26 file downloaded.

## Answer
- **LIVE: none.** **DEMO: one cell, k = 100 bp / H = 7 days ("peg100")**, draft in
  [PREREG_DRAFT_S_peg100.md](PREREG_DRAFT_S_peg100.md). It passes the DEMO bars on paper (IS t 4.5-7.0 by episode, VAL
  net > 0, x1.5 and one bar late positive, beats 99-100 % of random entries), but LIVE fails on VAL t (1.29-1.34)
  and power (HOLD ~2.4 episodes, power 0.71).
- Three caveats make it a weak DEMO: (1) VAL is 4 episodes and its net comes from one (SVB weekend, March 2023);
  without it VAL is -8 bp; (2) 21 of the 29 IS episodes are 2018-19, when Binance stablecoin pairs were thin and the
  discounts were mostly USDT's own premium; (3) a standing book that keeps its capital idle in USDT on Binance earned
  less than the cash rate in VAL (+337 bp / yr per unit vs ~395 bp / yr cash).
- Shallow cells (k = 10, 30) lose at the standard 10 bp taker fee in every era (reversion of 4-13 bp gross vs ~21 bp
  costs). Only with the documented zero-fee promotion on stablecoin pairs (from 2023-07) does k = 30 / H = 7 turn
  positive in VAL (+11.9 bp, t 4.0, taker fill), but IS has no zero-fee period to choose it on: information only.

## Data
data.binance.vision spot monthly 1m klines 2018-01..2024-12 (robots.txt 404, logged), 1,104 requests (577 x 200,
516 x 404 = months not listed, 11 timeouts retried; no 418 / 429 / 403), 341 MB, in
research/data/binance_stables/ (raw zips, npz, requests.log). Cut ts < 2025-01-01 at parse.

| pair | 1m data | note |
|---|---|---|
| USDCUSDT | 2018-12..2024-12 | gap 2022-10..2023-02 (Binance auto-converted USDC to BUSD) |
| BUSDUSDT | 2019-09..2023-12 | bad prints 2019-09-20 (0.0005 / 306); harmless to the long rule (entry at the next bar) |
| TUSDUSDT | 2018-05..2024-12 | thin in IS (12 % zero-trade bars) |
| PAXUSDT / USDPUSDT | 2018-10..2021-09 / 2021-09..2024-12 | USDP 65 % zero-trade bars |
| FDUSDUSDT | 2023-07..2024-12 | VAL only |
| DAIUSDT | 2020-07..2020-08 only | DAI was rich the whole time (never cheap) |
| USDSUSDT, USDSBUSDT | 2019-02..2020-06, 2019-06..09 | very thin (89-98 % zero-trade bars) |
BTC 1h for the cross: BTCUSDT, BTCBUSD, BTCUSDC, BTCTUSD.

## Rule and grid (declared)
d = 1 - close of X/USDT 1m bar; enter at the next bar's close when d >= k; exit at the next close after d <= k/2, or
after H days; one trade per pair; fees 10 bp taker per side + half-spread 0.5 / 1 bp; minus DFF over the hold.
Grid k {10, 30, 100} x H {1, 7}. t clustered by episode (trades in any pair within 24 h of each other).
Fill check added after a first look (addendum): taker-VWAP fill = entry at the entry bar's taker-buy average price,
exit at the exit bar's taker-sell average price (from the kline's taker-buy volume columns), fees only.

## Results: excess over cash, bp per trade (close fill / taker fill), t by episode
| cell | era | n | episodes (pos) | close | t | taker | t | x1.5 taker | late taker |
|---|---|---|---|---|---|---|---|---|---|
| k10 H1 | IS | 8966 | 58 (0) | -17.8 | -35.5 | -20.0 | -37.6 | -30.0 | -20.2 |
| k10 H1 | VAL | 1024 | 34 (1) | -18.3 | -12.5 | -18.0 | -13.6 | -28.0 | -17.8 |
| k10 H7 | IS | 8204 | 58 (0) | -17.5 | -35.8 | -19.7 | -34.8 | -29.7 | -20.0 |
| k10 H7 | VAL | 564 | 34 (2) | -15.5 | -5.4 | -15.5 | -5.9 | -25.5 | -15.1 |
| k30 H1 | IS | 2111 | 43 (2) | -14.0 | -11.0 | -18.7 | -11.7 | -28.7 | -18.6 |
| k30 H1 | VAL | 219 | 30 (3) | -9.4 | -1.6 | -9.9 | -2.0 | -19.9 | -11.0 |
| k30 H7 | IS | 1805 | 43 (3) | -12.9 | -10.7 | -17.8 | -10.8 | -27.8 | -18.0 |
| k30 H7 | VAL | 119 | 29 (3) | +0.6 | +0.1 | -0.2 | -0.0 | -10.2 | -1.7 |
| k100 H1 | IS | 218 | 31 (24) | +11.7 | +2.9 | +5.9 | +1.6 | -4.1 | +4.7 |
| k100 H1 | VAL | 61 | 4 (2) | +6.5 | +0.2 | +2.7 | +0.1 | -7.3 | +2.4 |
| **k100 H7** | **IS** | 163 | 29 (25) | **+22.1** | **7.0** | **+15.2** | **4.5** | +5.2 | +13.5 |
| **k100 H7** | **VAL** | 20 | 4 (2) | **+65.4** | **1.34** | **+50.6** | **1.29** | +40.6 | +53.0 |

Gross reversion (close fill, before fees) k100 H7: IS +44.2 bp, VAL +90.8 bp. Worst fill (buy at the bar high, sell
at the bar low) k100 H7: IS +0.1 bp, VAL +48.9 bp: the true IS edge sits between +0 and +22 bp, taker fill +15.
Max-over-6-cells null: the IS-best cell (k100 H7) beats 99.8 % (IS) / 100 % (VAL) of random max-over-cells draws.
Random benchmarks (k100 H7): uniform random minutes, same pair / era / hold: rand mean -22 / -26 bp, beaten 100 %;
random minutes in the same discount bucket: rand mean -3 / +25 bp, beaten 100 % / 99.4 %.

## k100 H7 detail
- Years (taker): 2018 +12.6, 2019 +12.0, 2020 +24.8, 2021 +20.3, 2022 no trade, 2023 +86.9, 2024 -3.9.
- Pairs IS (close): USDC +25.0 (n 31), TUSD +28.4 (36), PAX +30.2 (17), BUSD +17.4 (4), USDS +18.8 (69), USDSB -13.2 (6).
- Subsets (taker): IS 2020-21 only n 40, 8 episodes (8 pos), +24.5, t 4.38; IS 2018-19 n 123, 21 episodes, +12.1,
  t 3.15; IS without USDS / USDSB n 88, 18 episodes, +22.8, t 6.57; USDC + BUSD only n 35, 14 episodes, +16.8, t 3.82;
  IS without 2020-03..04 n 131, +13.7, t 3.49.
- VAL episodes: SVB 2023-03-11..13 (USDC bought at 0.9136, sold at 0.9950 -> +866 bp, USDP +244, TUSD mixed, BUSD +30): sum +1,378 bp;
  USDP 2023-11-09 (one 4-minute print, -44); TUSD 2024-01-15..02-29 (the slow TUSD depeg: five 7-day time stops at
  -42 to -108 bp, then +83 and +216 when it recovered): about -9 bp per trade; FDUSD 2024-03-05 +28.
  VAL without the SVB week: -8.4 bp (t -1.21). VAL net > 0 rests on one event.
- Entry-bar quote volume: median 3.7k USDT (IS), 17k (VAL): capacity per signal is small.
- Max concurrent positions 5 (IS) / 4 (VAL). Daily P&L correlation with C3: IS +0.004, VAL +0.035.

## Cash: the trade is graded on excess, the book is not free
Each trade's DFF over its hold is subtracted (that is the table). But the capital must wait on Binance in USDT,
which earns nothing, to be bought into a depeg within minutes. Sum of taker-fill excess per year for one unit of
notional per pair: IS +608 bp / yr, VAL +337 bp / yr. Average DFF: 2018 1.83 %, 2019 2.16, 2020 0.37, 2021 0.08, 2022
1.69, 2023 5.03, 2024 5.14 %. One unit of standby capital in VAL costs ~395 bp / yr of cash, more than the rule
earned with one unit per pair (and the rule needs up to 4-5 units concurrently). As a book, peg100 beat cash in IS
(near zero rates) and lost to cash in VAL. It is worth running only if the standby capital can earn close to the
cash rate while staying deployable (e.g. a flexible yield product that can be redeemed within minutes; not tested).

## Information (not candidates)
- USDT's own discount, BTC cross (1h, BTCUSDT / BTCX): matches the direct pairs (corr 0.95-0.99, median gap 0.7-2.3
  bp). IS: USDT vs USDC median -3.2 bp, p5 -45, p95 +55 bp (8.7 % of hours USDT > 30 bp cheap, 7.5 % > 30 bp rich);
  VAL: median -0.8, p5 -9, p95 +12 bp. The IS discounts that drive peg100 hit PAX, TUSD and USDC at the same time
  (2018-12, 2019-04, 2019-05, 2020-03): USDT was rich, not the stablecoin cheap. SVB 2023 was USDC itself.
- Mirror side (X rich, sell X for USDT, needs X inventory; bad prints > 20 % dropped), k100 H7: IS n 192, 25 episodes,
  +32.6 bp close / +18.4 taker (t 3.81); VAL n 61, 19 episodes, +59.7 / +36.3 (t 1.92 / 1.15), taker power at VAL
  size 1.00; VAL comes mainly from USDP (45 of 61 trades, 65 % zero-trade bars). Declared as information only, so
  not promoted; a two-sided "hold the cheaper stablecoin" book could be declared in a later round.
- Zero-fee promotion (Binance: USD stablecoin pairs, from 2023-06-30; FDUSD from 2023-07-26): VAL k30 H7 +11.9 bp
  (t 4.0), k10 H7 +2.1 (t 1.0) with taker fills. No IS exists for it.

## What failed and why
- k = 10 / 30: reversion is real (gross +4 to +13 bp, t 2-15) but smaller than a 21 bp standard round trip.
- k100 H1: the 1-day stop cuts trades before the reversion (VAL t 0.1).
- k100 VAL: only four independent depeg episodes in 2022-24; the slow TUSD depeg (an anchor that failed) is the
  loss mode, and the rule re-enters every 7 days into it.

## Pitfalls hit
- Close-to-close reversion on thin pairs includes bid / ask bounce: the declared 0.5-1 bp half-spread was too low
  for 2018-20 (median 1m range 2-12 bp). The taker-VWAP fill from the kline's taker-buy columns is a usable fix.
- BUSDUSDT 1m has bad prints (0.0005 / 306) in 2019-09; BTCTUSD 1h too. Long-only entry at the next bar is immune;
  the mirror side is not (filtered).
- Pair gaps (USDC 2022-10..2023-02 auto-conversion to BUSD) must close trades, not bridge them.
- data.binance.vision was slow (11 timeouts); the 1m pull of 9 pairs took ~28 minutes.

## What a user decision could unlock
- Whether standby capital on Binance can earn near the cash rate and still be used within minutes. Without that,
  peg100 does not beat cash at 2023-24 rates whatever HOLD shows.
- Whether the account gets the stablecoin zero-fee promotion today (would make k = 30 viable; needs a new DISCOVERY /
  TEST registration because IS has no zero-fee period).
- Holding a stablecoin inventory (USDC / FDUSD) beside USDT would allow the mirror side (two-sided book).

## Files
- [HYPOTHESES_S.md](HYPOTHESES_S.md), [PREREG_DRAFT_S_peg100.md](PREREG_DRAFT_S_peg100.md)
- Code: code/fetch.py (download + log), code/parse.py (zip -> npz), code/peg.py (rule, costs, episodes, random),
  code/run.py (grid tables), code/extra.py (subsets, mirror), code/diag.py (bounce check), code/c3corr.py,
  code/info_usdt.py (BTC cross)
- Output: out/summary.txt, out/extra.txt, out/mirror.txt, out/usdt_cross.txt, out/trades_k100.csv (all-cell trades in
  research/data/binance_stables/trades_all_cells.csv)
