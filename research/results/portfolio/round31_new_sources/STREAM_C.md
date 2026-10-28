# Round 31, stream C: crypto non-price data (positioning, open interest, exchange flows, liquidations) -> BTCUSD / ETHUSD at IC

Written 2026-10-27 20:22 UTC (`date -u`). Hypotheses declared first in [HYPOTHESES_C.md](HYPOTHESES_C.md) (18:22-18:40
UTC, before any return). HOLD 2025-26 never loaded: every series was requested or filtered to end 2024-12-31 and IC M1
was cut at ts < 2025-01-01.

## Answer

**No LIVE, no DEMO, no PREREG_DRAFT.** Results by family:
- Free crypto positioning and flow series can be had back to 2011 (CoinMetrics exchange flows) and 2016 (Bitfinex
  margin positions). Binance's open interest and long/short ratios start only 2020-09 for BTC and 2021-12 for ETH.
- No family has a side, fixed by its mechanism, that holds from IS to VAL after IC's costs.
- The best IS cell is CoinMetrics net exchange deposits (X1 BTC k 2.0, 1 day): net +132 bp, t 2.64. It keeps
  only 9 % of that in VAL (+11 bp, t 0.33), loses 20 % of VAL random entries and is flat on PRE (2012-17, mid +20
  bp, t 0.33). Its data are also not point-in-time: CoinMetrics recomputed the whole history in April 2026 with
  today's exchange-address labels.
- The only effect visible at mid in both eras is retail crowding on Binance at 4 h (N1): fade the global account
  long/short ratio at \|z\| > 1.5-2.
  - BTC IS gross +18 bp (t 2.13), VAL +8 (t 2.28); ETH VAL +12-20 (t 2.2-2.5).
  - Net per trade is +4-12 bp at t <= 1.54, and power at the VAL size is <= 1.1 (the bar is 3).
  - The series starts 2020-09, so the 2016-21 IS bar cannot be met anyway.
- Measured liquidations (Binance coin-margined snapshots, 2023-06..2024-10) are followed by **continuation**, not
  reversal: BTC -6 bp per 4 h, ETH -17. The open-interest flush rule (N4) does no better than the same events
  defined on price alone, which is round 3's rule.
- Contrarian on leverage build-up (N3) has the wrong sign. In VAL the side that built the open interest kept
  winning (net -142 bp, t -2.13 at 3 days), i.e. crypto momentum, C1's family.

## Sources

| source | what was fetched | span loaded | usable? |
|---|---|---|---|
| CoinMetrics community API v4 (`/timeseries/asset-metrics`, no key) | BTC, ETH daily FlowInExNtv, FlowOutExNtv, SplyExNtv, SplyCur, PriceUSD, AdrActCnt, CapMVRVCur, AssetEODCompletionTime | BTC 2010-01..2024-12-31 (flows from 2011-04-24), ETH 2015-07-30..2024-12-31 | yes, but **not point-in-time**: every flow row has `status-time` 2026-04-0x. Real-time completion of day D was ~04:00-05:30 UTC on D+1 (2022-24), so the rules enter at 08:00 UTC |
| CoinMetrics: miner flows, stablecoin exchange balances, market open interest / liquidations | catalog | - | not in the community tier (absent, or 403 on `market-openinterest` / `market-liquidations`). Stablecoin SplyCur exists, but issuance was tested in round 7 C / round 12 C (excluded) |
| Bitfinex public API `stats1/pos.size:1m:tBTCUSD:{long,short}/hist` | total margin longs and shorts, 1-min | 2016-11-06 21:12 .. 2024-12-31 (4.29 M rows each) | yes (logged live). ETH series **not pulled**: about 1.8 h at the allowed rate, and ETH's IS cost (median spread 89-254 bp in 2018-20) rules out any IS pass (family X on ETH: IS net -60..-250 bp per trade) |
| Bitfinex `liquidations/hist` | per-position liquidations, all pairs | starts 2019-07-28; only 2019-07-28..08-15 pulled | **not usable in this session**: limit 500 per page (~2 days of all pairs), and the endpoint answers 429 at more than ~6 requests a minute, so 2019-24 would take 3-4 h or more unattended. L1 (8 cells) was not run. Even complete, its IS is only 2019-08..2021 (DEMO at most) |
| Bitfinex `pos.size:1h` | hourly variant | starts 2021-02 | too short |
| Binance Vision `futures/um/daily/metrics/{BTCUSDT,ETHUSDT}` | 5-min open interest (contracts, USD), top-trader account / position L/S, global account L/S, taker L/S | BTCUSDT 2020-09-01..2024-12-31 (0 days missing); ETHUSDT **2021-12-01**..2024-12-31 (earlier days 404) | yes; BTC IS = 16 months, ETH has no IS. Taker ratio not used (round 4) |
| Binance Vision `futures/cm/daily/liquidationSnapshot/{BTCUSD_PERP,ETHUSD_PERP}` | liquidation orders (side, quantity in $100 / $10 contracts) | 2023-06-25..2024-10-14 (the archive stops there); no USDT-M snapshots exist | VAL only: information |
| IC M1 BTCUSD / ETHUSD (local cache) | prices, spreads | BTC from 2017-08-28, ETH from 2017-09-25, to 2024-12-31 | yes |

Unreachable or needing an account (not tried beyond the catalog): Coinglass, Coinalyze, CryptoQuant, Glassnode,
Santiment, Kaiko, Laevitas (paid or key). OKX / Bybit public archives hold trades and candles, not positioning. BitMEX
has no free open-interest or liquidation history. 5,044 requests are logged in `web/requests.log`.

## Method
As declared in HYPOTHESES_C:
- Signal time t, entry at the IC bar labelled t (the price at t+1 min). Exit at the last IC quote at or before
  t + hold, never beyond 5 days.
- Signals that fire while IC crypto is closed (weekends until 2024-04) are skipped. One trade at a time per rule.
- Costs: half the actual spread at each leg, no commission.
- Financing: IC crypto swap from research/specs.SWAPS (BTC long -38.61 USD/unit, short 0; ETH long -1.135, short 0).
  Used as **long -5.0 bp per 17:00 NY rollover, short 0, x3 on Friday** (round 23 N's ~5 bp). The `ssw` column
  charges shorts -5 bp too; it never changes a verdict.
- Checks: +1 min on both legs; half spreads x1.5.
- Statistics: t clustered by entry day. Random control: 200 seeds, same count and hold, random times on the rule's
  clock, side recomputed from the signal at the random time.
- Momentum control: OLS with past 1 / 7 / 28-day returns (family X).
- Eras: IS 2017-09..2021 (from the series start where later), VAL 2022-24. PRE 2012-2017-08 for X only, at mid, on
  CoinMetrics PriceUSD (entry at the end-of-day reference of D+1).

## Results (net in bp per trade at IC; sd per trade from the same trades)

| hypothesis | eras | mid IS / VAL (bp, t) | cost IS / VAL | net IS / VAL (t) | VAL / IS | Sharpe/trade IS / VAL; power at IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| X1 BTC net exchange deposits, z > 2 short / < -2 long, 1 d (best IS cell of 9) | PRE mid, IS, VAL | +145 (2.89) / +18 (0.51); PRE +20 (0.33) | 13 / 6 | +132 (2.64) / +11 (0.33) | 0.09 | 0.32 / 0.04; 1.68 / 0.25 | 98 % / 80 % | none (decays; VAL random 80 %; not point-in-time) |
| X1 BTC k 1.5, 5 d | same | +241 (2.12) / +70 (1.03); PRE +109 (0.96) | 23 / 17 | +218 (1.92) / +53 (0.78) | 0.24 | 0.22 / 0.09; 1.22 / 0.59 | 98 / 90 | none |
| X2 BTC gross inflow spike z > 2 -> short, 5 d | PRE, IS, VAL | +560 (1.60) / -198 (-1.20); PRE -655 (-3.61) | 12 / 4 | +548 (1.56) / -202 (-1.23) | < 0 | - | 98 / 14 | none (sign flips; PRE opposite) |
| X3 BTC exchange balance 30-d trend, daily 1 d | IS, VAL | +9 (0.67) / +8 (0.76) | 15 / 5 | -6 (-0.41) / +2 (0.22) | - | -0.01 / 0.01 | 50 / 50 | none |
| X1-X3 ETH | IS, VAL | IS best X3 +27 (1.69) | 135-160 / 15-28 | IS all < 0 (to -232) / best VAL X1 k 1.5 3 d +149 (1.73) | - | - | - | none (IS cost) |
| B1 BTC Bitfinex longs/shorts ratio, contrarian \|z\| > 2, 1 d | IS, VAL | +41 (1.16) / +42 (1.32) | 14 / 5 | +27 (0.76) / +37 (1.17) | 1.4 | 0.06 / 0.10; 0.48 / 0.89 | 92 / 92 | none (IS t < 2) |
| B1 BTC \|z\| > 2, 3 d | IS, VAL | +78 (1.08) / +94 (1.13) | 18 / 8 | +59 (0.82) / +86 (1.03) | 1.5 | 0.10 / 0.13; 0.52 / 0.79 | 92 / 94 | none |
| B2 BTC squeeze fuel (24-h build-up of shorts -> long, of longs -> short) | IS, VAL | best IS +19 (0.23) | 16-20 / 6-10 | IS <= -0.3 / VAL +48 (0.98) at k 2, 1 d | - | <= 0 IS | 49-74 / 52-88 | none |
| B3 BTC B1 at 4 h | IS, VAL | +0.5 (0.14) / +1.1 (0.31) | 14 / 4 | -13.7 (-3.33) / -2.9 (-0.83) | - | - | 68 / 78 | none |
| N1 BTC Binance global-account L/S, contrarian \|z\| > 1.5, 4 h | IS 2020-09.., VAL | +18.0 (2.13) / +8.1 (2.28) | 6.0 / 3.7 | +12.0 (1.42) / +4.4 (1.25) | 0.37 | 0.065 / 0.035; - / 0.91 | 71 / 97 | none (net t, power; truncated IS) |
| N1 BTC \|z\| > 2, 4 h | same | +11.4 (0.69) / +14.0 (2.10) | 6.4 / 3.8 | +5.0 (0.30) / +10.2 (1.54) | 2.0 | 0.02 / 0.07; - / 1.13 | 42 / 96 | none |
| N1 BTC daily cells (6) | same | best IS k 1.5 3 d +159 (1.50) | 7-11 / 5-11 | +148 (1.41) / +56 (1.19) | 0.37 | 0.22 / 0.11; - / 0.91 | 86 / 70 | none |
| N1 ETH 4 h (VAL only) | VAL | +12.0 (2.45), +19.9 (2.22) | 15 | -2.6 / +4.7 (0.53) | - | -0.02 / 0.03 | 98 / 99 | information |
| N2 BTC large accounts vs crowd, follow large | same | IS <= +10 (0.28) | 8-11 | IS <= +2.3 / VAL +17..+58 (<= 1.64) | - | IS <= 0.01 | 27-55 / 58-82 | none (IS) |
| N3 BTC open-interest build-up, against the builders | same | IS -95..-29 / VAL -23..-145 | 4-10 | VAL -142 (-2.13) at k 1.5, 3 d | - | < 0 | 6-45 | none: **wrong sign** (= momentum) |
| N4 BTC open-interest flush (1-h OI z < -2) -> fade the 1-h move, 4 h | same | +17.6 (1.43) / +5.6 (1.04) | 9.4 / 5.2 | +8.2 (0.67) / +0.4 (0.07) | 0.05 | 0.04 / 0.00 | 87 / 88 | none; price-only control +11.6 / -10.0 (same) |
| N4 other cells (k 3, 24 h), ETH | same | IS <= +11 | | all IS net <= +0.1, ETH VAL < 0 | | | | none |
| L2 Binance cm liquidations, top-1 % hour -> fade, 4 h / 24 h (VAL only, look-ahead threshold) | VAL 2023-06..2024-10 | BTC -6.2 (-0.67) / -21.4 (-0.71); ETH -17.4 (-1.47) / -14.8 (-0.45) | 4.5-13.5 | BTC -10.7 / -27.5; ETH -29.5 (-2.46) / -28.3 | - | < 0 | 8-34 % | none (continuation) |
| L1 Bitfinex liquidations | - | - | - | not run (rate limit, see Sources) | | | | not tested |

Full cell outputs, per year and every grid point: scratchpad `r31/C/out/fam_x.txt`, `fam_b_btc.txt`, `fam_n_btc.txt`,
`fam_n_eth.txt`, `fam_l2.txt`.

Momentum regressions for family X (next 1-day IC return on the signal, bp per sd of signal, IS / VAL):
- BTC: X1 +20.0 (t 1.49) / -0.4; with past 1 / 7 / 28-day returns +21.4 (t 1.59) / -1.0. X2 +0.9 / -0.5. X3 +9.1 /
  +9.5 (t 0.96).
- ETH: X1 -15.0 / +15.6. X3 +27.5 (t 1.72) / +17.0 (t 1.37), the most persistent sign of the family, but at ETH's
  IC cost.

## Cells and chance
- Cells run, by family:
  - X: 28 (BTC + ETH).
  - B: 12 (BTC; the 12 ETH cells not run, reason above).
  - N: 40 (BTC 20 with a 16-month IS; ETH 20 VAL-only).
  - L: L1's 8 cells not run; L2 has 4 information cells (2 declared BTC + 2 ETH added for information).
  - In total 80 registered cells were evaluated, plus 4 information cells.
- Best \|IS net t\| per family against the expected max of K independent cells:
  - X: 2.64, expected 2.30 for K = 28 (95 % 3.12).
  - B: 0.82, expected 1.96 for K = 12.
  - N (BTC 20): 1.42, expected ~2.1.
  - All 80: 2.64, expected 2.7.
- The family maxima are what chance gives. No cell passes both eras.

## What this says
- **Point-in-time positioning (Bitfinex since 2016, Binance since 2020) carries no 1-5 day edge for BTC.** Rules
  that fade crowded leverage have the right sign about as often as the wrong one. The Bitfinex ratio rule (B1, k 2)
  is positive in both eras but at t ~1 and power < 1. Binance open-interest build-ups continue rather than reverse
  (N3 VAL t -2.1), the same finding as round 4's funding result: crypto positioning series mostly re-express
  momentum.
- **Retail crowding at 4 h is a small real effect at mid** (BTC t 2.1-2.3 in both eras, ETH 2.2-2.5 in VAL, beating
  96-99 % of random entries in VAL). It is 8-20 bp gross on a 95-130 bp 4-h sd, i.e. ~0.07 sd. Power 3 would need
  about 3x that net. It fits the PROMPT pattern "real at mid, smaller than what LIVE needs".
- **Forced flows (liquidations, OI flushes) do not mean-revert at IC's fills.** Measured liquidations are followed by
  more of the same move over 4-24 h. The OI condition adds nothing to round 3's price-only event, so the
  liquidation-cascade family stays closed with measured data too.
- **Exchange-flow data (CoinMetrics) is the only source with PRE years.** Its one IS-strong cell decays to 9 % in VAL
  and is flat on PRE. Gross-inflow spikes even reverse sign between PRE / IS / VAL. Because the history is restated
  with 2026 labels, these backtests are optimistic: the true real-time effect is likely smaller still.

## Directions that need the user (value = chance the direction yields a LIVE candidate)
- Point-in-time exchange flows (CryptoQuant / Glassnode / Coin Metrics Pro, paid). Needed before any CoinMetrics-based
  rule could be registered. Value ~1 %: the restated data already fail VAL.
- Aggregated derivatives positioning and liquidations 2019+ across exchanges (Coinglass, Coinalyze, Kaiko, Laevitas;
  account and usually paid). Value ~2 %: Binance alone, the largest venue, shows only the 4-h retail effect at ~0.07 sd.
- A long unattended pull of Bitfinex liquidations (free, no account, 3-4 h at <= 6 requests a minute) and of
  Bitfinex ETH positions (~2 h). Value < 1 %: the IS is only 2019-08..21, and Binance liquidations show
  continuation.
- None of these is recommended ahead of other round-31 streams.

## Process notes
- Disclosure: from 18:21 to 18:51 UTC the Binance metrics pull and the liquidation-snapshot pull ran at the same
  time. A `pgrep` guard failed (zsh pattern error), so data.binance.vision got about 2 requests a second instead
  of <= 1. It answered 3,671 x 200, 456 x 404 (ETH days before 2021-12), 2 x 403 and no 429 / 503. Bitfinex
  answered 13 x 429; I backed off for 120-300 s each time and then stopped.
- The power column uses each era's trade rate. For Binance-based rules the IS rate is understated (IS starts
  2020-09); read the VAL-size power.
- No survivor, so no C3 correlation was computed.
- Downloads: scratchpad `r31/C/web/` (368 MB; parsed with `python -I`). Derived npz: `r31/C/data/`.
- Scripts: `r31/C/scripts/` (`fetch.py`, `pull_bv.py`, `pull_bv_liq.py`, `pull_bfx.py`, `parse_cm.py`,
  `parse_bv.py`, `r31c.py` engine, `fam_x.py`, `fam_b.py`, `fam_n.py`, `fam_l2.py`, `fam_l.py` (unrun),
  `chance.py`).
- Scratchpad root:
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r31/C/
