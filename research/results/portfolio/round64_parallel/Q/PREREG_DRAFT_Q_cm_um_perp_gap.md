# PREREG DRAFT Q1: COIN-M perp vs USDT-M perp gap reversion on Binance (Q1_k100_H72), DEMO tier only

Draft written by stream Q (round 64), time in [STREAM_Q.md](STREAM_Q.md) header. HOLD (2025-01-01..2026-10-29) NOT
opened, not requested, not downloaded; the coordinator opens it once. Tier: **DEMO** (IS t 2.20 < 2.5 rules out LIVE;
power per event-day 1.47 < 3). Heavy caveats (crash-day concentration, COIN-M book depth) in STREAM_Q.md.

## Rule (frozen; code `code/q.py` load() / simulate(pairs, "Q1", 100, 72), priced by `code/run.py` price_1m)
- Universe: every Binance COIN-M perpetual <COIN>USD_PERP (inverse) with a USDT-M perpetual <COIN>USDT trading at the
  same hour (50 pairs 2020-08..2024-12, incl. delisted LUNA, FTM, MATIC). No volume rank filter.
- Hourly gap g = ln(close COIN-M perp / close USDT-M perp); a bar is valid when both legs have >= 20 trades in the
  hour. Reference m_h = median of g over the previous 168 h (>= 120 valid).
- Event: |g_h - m_h| > 100 bp at the close of hour h, and both legs' 1h closes equal their last 1m close within 1 bp
  (bad-print guard). Side fixed: long the cheap perp, short the rich perp, equal USD notional. One open trade per coin.
- Entry: both legs at the open of the 1m bar starting 1 minute after the hourly close (T + 1 min).
- Exit: at the first hourly close c >= h+1 with |g_c - m_h| <= |g_h - m_h| / 2 (same side), else after 72 h; both legs
  at the open of the 1m bar starting 1 minute after the next hour boundary.
- P&L per unit notional: side x [(COIN-M exit / entry - 1) - (USDT-M exit / entry - 1)] (the inverse leg's coin P&L
  converted at the exit price equals a linear leg), + funding of both perps on stamps in (entry, exit] signed by
  position, - 20 bp taker fees (5 bp x 2 sides x 2 legs) - 2 x (half-spread COIN-M + half-spread USDT-M) with
  COIN-M 1 bp (BTC / ETH) / 3 bp (others), USDT-M 0.5 / 2 bp. The COIN-M coin collateral is assumed hedged by a
  standing USDT-M short outside the trade.

## IS / VAL numbers (declared cell, 1m pricing at T + 1 min, taker)
| era | screen n | graded n (guard / no 1m) | event-days | net bp | median | t (day) | x1.5 | T + 2 min | T + 5 min (info) | random beaten (1h opens) |
|---|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 61 | 54 (7 dropped) | 22 | +439.8 | +82.0 | 2.20 | +424.9 (t 2.13) | +314.3 (t 1.56) | +180.2 (t 1.58) | 100 % (random -27 bp) |
| VAL 2022-24 | 181 | 181 | 33 | +77.7 | +57.4 | 3.82 | +62.8 (t 3.09) | +92.1 (t 2.88) | +89.5 (t 3.05) | 100 % (random -28 bp) |
Years (n, net bp): 2020 (4, +88), 2021 (50, +468), 2022 (160, +84), 2023 (17, +10), 2024 (4, +107): 5 / 5 positive.
Max-over-15-cells random-entry t: p95 IS 1.37, VAL 0.57. Daily P&L correlation with C3: IS -0.006, VAL +0.008.
Concentration: top 5 days = 95 % of IS P&L (2021-04-18 52 %, 2021-05-19 38 %), 98 % of VAL P&L (2022-05-11 / 12 LUNA
68 %, 2022-11-10 FTX 24 %). Outside the declared crash windows: IS n 34 +432 (t 1.36, driven by 2021-04-18), VAL n 38
+12.6 (t 0.29).

## Power at VAL size
VAL 60 trades / yr on 11 event-days / yr; HOLD ~1.83 yr. Per trade SR 0.49 x sqrt(110) = 5.11, but trades of one
day are one bet: per event-day SR 0.33 x sqrt(20) = **1.47**. Graded power 1.47 (< 3), tier DEMO.

## HOLD pass bar (DEMO)
HOLD net > 0 per trade at T + 1 min 1m pricing, taker costs; report t (day cluster), median, T + 2 min, x1.5, top-5
days share, and the number of event-days. Fail if net <= 0. If HOLD has fewer than 3 event-days the result is
"inconclusive" (no demo promotion on HOLD alone). Run once on 2025-01-01..2026-10-29; the coordinator must pull the
same series for 2025-26 (data.binance.vision futures/cm monthly 1h + fundingRate, futures/um monthly 1h, daily 1m
around the events; USDT-M funding).

## Demo plan (if HOLD passes)
- Paper or demo bot on hourly closes, both legs within the first minutes after the close; log the book (best bid /
  ask and depth for 1x trade size) of both legs at the signal, fill prices, funding, and the coin collateral hedge.
- Expected ~60 signals / yr on ~11 days / yr (crash days); size so one event-day loses at most the demo risk unit.
- Stop rule: stop if cumulative net after 8 demo event-days < 0, or if the median COIN-M fill is more than 20 bp
  worse than the 1m open used here.
- Live rule: HOLD + demo pooled, t (day cluster) >= 2.5 on >= 15 event-days.

## Code hashes (`python -m research.tools.prereg_hashes`, Sun Nov 1 10:31 UTC 2026; re-check before HOLD)
- `research/results/portfolio/round64_parallel/Q/code/q.py` 5ed796533eff92fd
- `research/results/portfolio/round64_parallel/Q/code/run.py` f986e7bcb37fc4bc
- `research/results/portfolio/round64_parallel/Q/code/pull_vision.py` 7b412d1fde3d30b3
- `research/results/portfolio/round64_parallel/Q/code/pull_m1.py` a27648f00b342fa1
- `research/results/portfolio/round64_parallel/Q/code/pull_dapi_funding.py` 5e67e59cebb31d22
For HOLD, q.py's CUT / ERAS and the pull scripts' 2024-12 caps must be widened in a copy; the rule functions
(build_pair, simulate, price_1m, leg) stay unchanged.
