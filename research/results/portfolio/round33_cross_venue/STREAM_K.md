# Round 33, stream K: crypto cross-venue premiums and Bitfinex margin funding -> BTCUSD / ETHUSD at IC

Written 2026-10-27 19:27-19:35 UTC. The hypotheses were declared in HYPOTHESES_K.md before their numbers: 72 cells at
19:09, round 2 at 19:25 (8 cells) and a post-hoc round 3 at 19:26 (5 cells). HOLD was not opened. Every new series was
cut at 2024-12-31.

**Verdict: no LIVE or DEMO candidate, and no PREREG_DRAFT.**
- No cell reaches IS net t 2.0. The best is +1.74 (post-hoc) and +1.69 (declared), against a chance level of ~2.7
  for 85 cells.
- One consistent sign does run through all three rounds: **when Coinbase trades rich against an offshore venue
  (Binance in USDT, Bitfinex in USD), BTC tends to rise over the next 1-3 days.**
  - The sign holds in IS and VAL. It is stronger in VAL 2022-24 (net t 2.0-2.7), and every year is positive in the
    best declared cell.
  - It fails the IS bar on a 4.3-year IS: per-trade Sharpe is 0.07-0.13, power 0.9-1.7, and the random-entry
    percentile is 68-95 %.
- The declared Korean "frenzy reverts" side is wrong. A high kimchi premium is followed by BTC rising, not falling, but
  even reversed it is below the IS bar.
- Bitfinex funding rates carry nothing.

## Sources (all public, no key; every fetch in scratchpad `r33/K/web/requests.log`, >= 1.1 s per host, 3 s on Bitfinex)
| series | from | to | use |
|---|---|---|---|
| Coinbase Exchange BTC-USD / ETH-USD 1h candles (api.exchange.coinbase.com) | 2015-07-20 / 2016-05-18 (earlier requests return empty) | 2024-12-31 | US leg |
| Binance spot BTCUSDT / ETHUSDT 1h klines (data.binance.vision monthly zips) | 2017-08-17 | 2024-12-31 | offshore leg (USDT) |
| Upbit KRW-BTC / KRW-ETH 1h candles (api.upbit.com) | 2017-09-25 (beta month thin) | 2024-12-31 | Korean leg |
| ECB euro reference rates, USD/KRW = KRW / USD columns (14:15 CET) | 1999 | cut at 2024-12-31 | FX leg of the kimchi premium |
| Bitfinex funding candles fUSD / fBTC / fETH (a30:p2:p30), tBTCUSD, tUSTUSD 1h | 2016-08-01; tBTCUSD 2013; tUSTUSD 2018-11-27 | 2024-12-31 | funding, Bitfinex leg, USDT/USD |

Unusable or not fetched:
- **GBTC premium.** An SMU 2023 working paper (ink.library.smu.edu.sg/lkcsb_research/7447) calls it the strongest
  BTC daily predictor. Free GBTC prices are out of reach: stooq.com's robots.txt disallows all agents and it serves a
  JavaScript challenge, and Yahoo was unreachable in round 9.
- **Bank of Korea ECOS** needs a key.
- **Bithumb / Korbit** have no deep public history (pre-2017 kimchi premium).
- **Upbit KRW-USDT** starts 2024-06.
- **Bitfinex pos.size** was deliberately left to round 31 C, which declared B1-B3 on it and was pulling it while this
  stream ran. STREAM_C.md did not exist yet; nothing here duplicates it.

**Incident.** The first `head` of the ECB CSV printed its newest row, a single day of 2026-10 EUR reference rates
(EUR/USD, EUR/KRW and the other currencies). No crypto value from 2025-26 was loaded, printed or used. The file was
then cut at 2024-12-31 and the full CSV deleted. No signal here uses EURUSD.

## Timestamp rules (declared before returns)
- **Coinbase premium (CBP).** `ln(Coinbase close / Binance close)` for the same hour bucket, both the last trade
  before the bucket end. It is known at the bucket end, and the IC entry is at the next minute.
- **Kimchi premium (KP).** `ln(Upbit KRW close / (Coinbase USD close x ECB USDKRW))`.
  - Both crypto legs are taken in the hour ending 14:00 CET, and the FX leg is that day's ECB 14:15 CET rate, so the
    legs are 15 minutes apart every day.
  - Daily KP rules enter at 16:00 UTC, after the ECB publication (~16:00 CET).
  - The hourly KP change uses one FX rate on both points, so the FX term cancels.
- **Bitfinex funding.** The volume-weighted daily rate, known at 00:00 UTC the next day.
- **No forward-filling.** Gaps are not forward-filled, and z-scores use only past values.

## Data facts that matter (no returns)
- **Raw CBP is mostly the USDT/USD basis.** It is almost identical for BTC and ETH every year (2018 mean -35 / -38
  bp). Its range shrinks with time: the daily p5-p95 band is 2017 -34..+473 bp, 2020 -15..+20 and 2022-24 about
  -13..+10.
- **The USDT-adjusted CBP is unusable before 2020.** Bitfinex's own USD traded at a discount in 2018-19 (-280 bp in
  Dec 2018).
- **KP by year (BTC).** Mean 2018 +3.6 %, 2019 +0.2, 2020 -0.5, 2021 +3.4, 2022-24 +1.4-2.4 %. p95 was 2017 +24 %,
  2018 +15 % and 2021 +11 %.
- **fBTC funding is ~0 % p.a. on most days of 2023-24,** so FD2-BTC is degenerate in VAL.

## Costs, fills, controls
These are round 31 C's engine and conventions, copied.
- **Prices and fills.** IC M1 mid, entry at signal + 1 minute.
- **Cost.** Half the actual spread at entry and at exit. Long swap is -5 bp per 17:00 New York rollover (x3 Friday),
  short swap 0.
- **Robustness checks.** +1 minute on both legs; half-spread x1.5; short swap -5 bp.
- **Trades and t-stats.** Trades do not overlap, and t is clustered by entry day.
- **Random control.** 200 seeds on the rule's clock, with the side recomputed at the random time.
- **IS window.** IS is 2017-09..2021-12 (4.3 years; KP from 2018-01, KP2 from 2018-10). There is no PRE: the second
  leg of every premium starts in 2017.
- **ETH costs.** IC's ETH spreads of 88-254 bp in 2018-20 make every ETH IS net strongly negative. ETH cells are
  counted, and their gross is reported.

## Power arithmetic (before building)
At the VAL sd, LIVE needs:
- a 43 bp net edge per trade for a daily 1-day rule taken every day;
- 78 bp for |z| > 1 daily rules (Sharpe 0.26);
- 280 bp for 3-day |z| > 2 rules (Sharpe 0.59).

The sources imply much less:
- Makarov & Schoar 2020 report contemporaneous co-movement only.
- Eom 2021 reads the kimchi premium as speculative trading (unstable in a 2023 FRL re-examination).
- Practitioners report corr(KP, forward return) ~ -0.06, i.e. Sharpe ~0.06 and power ~1.2.

So DEMO was the realistic target from the start.

## Results (bp per trade; gross = mid; full output in scratchpad `r33/K/out/run_all.txt`, `run_k2.txt`, `run_k3.txt`)
### Main table: best and notable cells per family
| cell | era | n | gross (t) | cost | net (t) | VAL/IS net | Sharpe, power | random | verdict |
|---|---|---|---|---|---|---|---|---|---|
| CB1 BTC k1.0 h1d (CBP z > 1 follow) | IS | 429 | +41.4 (2.13) | 13.5 | +27.9 (1.44) | 1.33 | 0.070, 0.91 | 88 % | none (IS t < 2) |
| | VAL | 326 | +42.1 (2.35) | 5.0 | +37.1 (2.07) | | 0.115, 1.58 | 77 % | |
| CB2 BTC k2.0 h24h (hourly CBP spike follow) | IS | 300 | +62.4 (2.20) | 15.1 | +47.3 (1.69) | 0.66 | 0.097, 1.07 | 94 % | none |
| | VAL | 265 | +37.8 (1.90) | 6.4 | +31.4 (1.58) | | 0.097, 1.20 | 76 % | |
| CB1 BTC k1.0 h3d | IS / VAL | 204 / 144 | -3.5 / +107.9 (2.75) | 17.0 / 8.6 | -20.5 (-0.44) / +99.3 (2.53) | sign flip | -0.03 / 0.21 | 54 / 88 % | none |
| CB3 BTC 7-day CBP sign, h1d | IS / VAL | 1114 / 779 | +6.1 / +4.2 | 16.2 / 6.2 | -10.1 (-0.73) / -2.0 (-0.18) | | | 48 / 52 % | none |
| CB1 ETH k1.0 h5d | IS / VAL | 136 / 97 | +125 (1.20) / +184 (2.51) | 151 / 23 | -26 (-0.25) / +161 (2.19) | | | 82 / 76 % | none (IS cost) |
| KP1 BTC k1.5 h1d (KP z contrarian) | IS / VAL | 183 / 147 | +24.7 (0.72) / -3.4 | 12.7 / 6.2 | +12.0 (0.35) / -9.5 (-0.43) | < 0 | | 76 / 62 % | none |
| KP2 BTC KP > 1y q90, short, h3d | IS / VAL | 44 / 50 | -156 (-1.25) / -115 (-1.97) | 9.6 / 3.9 | -166 (-1.33) / -119 (-2.04) | | | 6 / 2 % | **wrong side** |
| KP3 BTC k2 h4h (4-h Korean bid surge contrarian) | IS / VAL | 846 / 692 | -11.4 / +3.1 | 14.7 / 4.6 | -26.2 (-3.05) / -1.5 | | | 7 / 68 % | none |
| FD1 BTC fUSD k1.5 h1d (expensive long leverage -> short) | IS / VAL | 248 / 136 | +0.1 / -9.4 | 17.6 / 5.1 | -17.5 (-0.58) / -14.5 (-0.54) | | | 63 / 24 % | none |
| FD2 BTC fBTC k1.5 h3d (expensive short leverage -> long) | IS / VAL | 82 / 78 | +26.6 / +62.9 | 21.0 / 8.8 | +5.6 (0.07) / +54.0 (1.05) | | | 83 / 82 % | none |
| K2-CBUS k1.5 h1d (US-hours CBP follow) | IS / VAL | 156 / 125 | +42.2 (1.31) / +29.4 (1.01) | 12.7 / 6.1 | +29.5 (0.92) / +23.3 (0.80) | 0.79 | 0.074 / 0.071 | 88 / 63 % | none |
| K2-BFX k1.5 h3d (Bitfinex-over-Coinbase follow) | IS / VAL | 115 / 104 | -93 (-1.68) / -160 (-3.56) | 18.1 / 10.9 | -111 (-2.00) / -171 (-3.80) | | | 18 / 1 % | **wrong side** (= Coinbase-rich -> up) |
| K3-CBX hourly k2 h24h (post-hoc composite, Coinbase vs Binance + Bitfinex) | IS | 214 | +77.5 (2.19) | 16.9 | +60.7 (1.74) | 0.94 | 0.119, 1.10 | 93 % | none (post-hoc, IS t < 2) |
| | VAL | 207 | +63.4 (2.53) | 6.5 | +56.9 (2.27) | | 0.158, 1.73 | 95 % | |
| K3-CBX k1.0 h3d (post-hoc) | IS / VAL | 170 / 137 | +31 (0.56) / +131 (2.94) | 17.0 / 9.1 | +14.1 (0.25) / +121.6 (2.74) | 8.6 | 0.02 / 0.235, 2.09 | 80 / 94 % | none |

### Notes on the main cells
- **CB1 BTC k1.0 h1d by year.** Net 2017 +87, 2018 +16, 2019 +37, 2020 +14, 2021 +22, 2022 +22, 2023 +19, 2024 +60
  (8 / 8 positive).
- **CB2 BTC k2.0 h24h by year.** IS 2017 +29, 2018 +2, 2019 +78, 2020 +75, 2021 +31; VAL 2022 +41, 2023 -3,
  2024 +49.
- **Robustness of the CB cells.** The +1 min, x1.5 and short-swap variants move the CB cells by at most ~7 bp, and
  the sign never flips.
- **KP2's declared short lost in both eras.**
  - The reversed side was run as information: long when KP is above its 1-year q90.
  - It gives IS net +8.7 (0.17), +136 (1.09) and +104 (0.56) for 1, 3 and 5 days, against VAL +37 (1.51), +99 (1.71)
    and +198 (1.91).
  - It fails DEMO's IS t 2.0 even reversed. It has 6-32 trades a year.

### Chance and cells per family
| family | cells | best IS net t | E max \|t\| (95 %) of K normals |
|---|---|---|---|
| CB (Coinbase premium, declared) | 30 | +1.69 (CB2 BTC); most negative -11.1 (ETH 4-h, cost) | 2.32 (3.14) |
| KP (kimchi premium) | 26 | +0.35 (BTC); KP3 BTC -3.05, ETH down to -13.8 (cost) | 2.26 (3.09) |
| FD (Bitfinex funding) | 16 | +0.50 (FD2 ETH) | 2.08 (2.97) |
| K2 (round 2: US-hours CBP, Bitfinex premium) | 8 | +0.92 | |
| K3 (round 3, post-hoc composite) | 5 | +1.74 | |
| all | 85 | +1.74 | 2.69 (3.42) |

The large negative ETH t's (-4 to -14) are IC's 2018-20 ETH spreads, not signal. On BTC alone the most negative IS
net t is -3.05 (KP3 k2 h4h: a 4-h hold at 2017-19 spreads), while the declared sides' IS gross t's sit in
-1.7..+2.2.

### Momentum control
OLS of the next-h IC return on the continuous z, with the past 1, 7 and 28-day returns as controls, on
non-overlapping samples (`momctl.txt`).
- **CB1-z BTC h1.** IS +14.4 bp per sd (t 1.27), +13.6 (1.13) with momentum; VAL -0.5 (-0.04), +6.7 (0.51). So the
  CB threshold cells are not a linear premium effect, and momentum does not explain them either (the mom28
  coefficient is ~0).
- **KP1-z BTC h5.** IS +82 bp per sd on the contrarian side (t 1.46), VAL -83 (-1.60): a sign flip between eras.
- **FD.** Nothing. The FD2-ETH OLS t's are an artefact: z explodes when the fETH rate is flat.

## What this says
1. **A cross-venue premium is information about the next 1-3 days, at a size the IC cost does not kill but the
   variance does.**
   - The consistent reading across three constructions: Coinbase rich vs Binance (follow wins), vs Bitfinex (the
     follow-Bitfinex side loses, VAL t -3.8) and the composite. US-venue demand continues, as the CryptoQuant
     practitioner reading says.
   - BTC's daily sd is 300-450 bp, so a 30-60 bp edge gives Sharpe 0.07-0.16 per trade. LIVE needs 0.26-0.6 at these
     trade counts.
   - IS t is 1.4-1.7 on 4.3 years. At the VAL size, the expected HOLD t (power) is 1.2-1.7 in the best cells, ~0.4 at
     round 18's 1/4 retention for the post-hoc composite.
   - The effect grows in VAL (2022-24, with lower spreads and more US institutional flow), the opposite of the decay
     pattern of earlier flows. It still cannot meet "IS t >= 2.0 / 2.5" on 2017-21.
2. **The Korean premium is not a contrarian top signal at 1-5 days.** If anything, an extreme premium is followed by
   further rises: it marks demand that has not finished.
3. **Margin-funding rates on Bitfinex add nothing.** Like perp funding in rounds 4 / 9.

## Directions that need the user
- **A source for GBTC (or other US-listed BTC trust) daily prices before 2024, for the GBTC premium.** The one
  premium the literature reports as a significant daily BTC predictor (SMU 2023 working paper). It is another
  segmented-market premium (US equity accounts), with a mechanism (trust creations, share unlock dates).
  - Stooq is blocked by robots.txt and a JS challenge; Yahoo was unreachable.
  - Value: low-medium. The trust converted to an ETF in 2024, so the series ends there and only a historical test is
    possible, no forward trading: LIVE ~0 %, information value only.
- **Point-in-time tick-level cross-venue data** (Kaiko / Tardis, paid) for a minute-level Coinbase-premium rule.
  Value: low. The daily effect is too small relative to BTC's sd for LIVE, and minute-level premium arbitrage is a
  market-maker game IC cannot play.
- **Accepting an IS from 2020 only** (when CB's net is steadiest) would be a bar change. Not proposed.

## Files
- Hypotheses: research/results/portfolio/round33_cross_venue/HYPOTHESES_K.md. This file:
  research/results/portfolio/round33_cross_venue/STREAM_K.md.
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r33/K/scripts/`):
  - Fetching: fetch.py, pull_cb.py, pull_up.py, pull_bv.py, pull_bfx.py, pull_bfx2.py.
  - Series: build.py, series.py, describe.py.
  - Engine: keng.py (copy of round 31 C's r31c.py).
  - Cells and checks: run_k.py (72 cells), run_k2.py, run_k3.py, momctl.py, years.py.
- Outputs: the same folder's `out/` (describe.txt, run_all.txt, run_k2.txt, run_k3.txt, momctl.txt, years.txt). Raw
  downloads are in `web/` and parsed arrays in `data/raw.npz`, all cut at 2024-12-31.
