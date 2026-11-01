# Round 48, stream N: Bitcoin network fundamentals (hashrate, difficulty, hashprice, fees, mempool) -> BTCUSD

Written 2026-10-30 08:40 UTC. Hypotheses, signal counts and power arithmetic were declared first in
[HYPOTHESES_N.md](HYPOTHESES_N.md) (08:28 UTC; addendum 1 at 08:31 UTC, before its numbers). HOLD stays closed:
every series was cut at ts < 2025-01-01 at parse and IC M1 at load, before anything was printed.

## Answer
**No LIVE, no DEMO, no PREREG_DRAFT.**
- No cell of 37 reaches IS net t 2. The best \|IS net t\| is 1.88, and it has the wrong sign (mempool spike, fade the
  3-day move, 1 d: -182 bp). Chance gives 2.40 for K = 37 (95 % 3.20).
- The folk rule, hash ribbons (Edwards 2019), fires 1-2 times a year. Its long signal after capitulation is:
  - negative in IS: cross-back 5 d, net -135 bp, t -0.32, n 7;
  - positive in VAL: +253 bp, t 1.09, n 5;
  - Edwards' price-filtered version: +283 bp (t 1.05) / +215 (t 0.65) on 6 / 3 trades.
  
  That is coin-flip evidence on 3-7 trades. HOLD would hold ~2-3 trades, so it cannot be graded at any bar.
- **Difficulty adjustments** (exact block timestamps) look good in VAL only. Rel-all, long after a below-trend
  retarget and short after an above-trend one:
  - VAL net +72 / +93 / +138 bp at 1 / 3 / 5 d (t 1.88 / 1.58 / 1.73), beating 97-99 % of random entries.
  - IS: -50 / -14 / -24 (t -1.21 / -0.21 / -0.26).
  - PRE mid 2012-17: -29 / -90 / -128 (t -0.8 to -1.5).
  
  The sign flips across eras, so this is noise and not a decayed or emerging edge. At 27 retargets a year, LIVE would
  also need ~137 bp net per trade.
- **Hashprice at a 90-day low -> short** is the price-low rule relabelled. The price-only control behaves the same:
  IS positive, VAL negative.
  - Fresh-low, 1 d: IS +122 (t 0.45), VAL -168 (t -1.76).
  - Price-only, 1 d: IS +214, VAL -218.
  - State rule: IS -25, VAL -50.
- **Fee / mempool congestion** has no stable side:
  - primary short: fee share VAL -24 bp (t -0.72); mempool IS +38 (t 0.39), VAL +46 (t 1.07);
  - exhaustion vs continuation, mempool 1 d: IS favours continuation (+146, t 1.54, 100 % random), but VAL is
    -12 bp;
  - fee share 3 d: IS favours fade (+132, t 0.72), VAL +74 (t 1.15). That is VAL t < 1.5 on 41 trades, and the 1-d
    version is IS t 0.23.
- What is left in the daily families (A2, linear, next-day mid return per sd of each series) is \|slope\| <= 30 bp
  per sd at \|t\| <= 1.18 in IS. Adding past 1 / 7 / 28-day returns as controls gives at most t 1.87 (hashprice, IS
  +54 bp per sd), which flips to -20 (t -1.35) in VAL. Every VAL slope is \|t\| <= 1.07. No daily family carries a
  1-day signal above BTC's noise.

## Sources (all fetched 2026-10-30 08:23-08:25 UTC; 13 requests, log in scratchpad `web/requests.log`)
| source | robots / terms | what | span loaded (after cut) | point-in-time |
|---|---|---|---|---|
| Coin Metrics community API v4 (`community-api.coinmetrics.io`, no key) | robots.txt 404 (no rules); community data CC BY-NC (research use) | BTC daily HashRate, BlkCnt, FeeTotNtv, IssTotNtv, IssTotUSD, PriceUSD, TxCnt. Not in the community tier: DiffMean / DiffLast, RevUSD, RevHash*, FeeTotUSD, block size | 2010-01-01..2024-12-31 | Block-derived and immutable, so computable at 00:00 D+1. Used at D+1 02:00 UTC (2 h guard). PriceUSD is the 00:00 reference |
| mempool.space `/api/v1/mining/difficulty-adjustments/all`, `/hashrate/all` | `/robots.txt` serves the app's HTML (no rules); public API, no key | every retarget [header ts, height, difficulty, ratio]: 421 rows to 2024-12-29; daily hashrate (cross-check only) | 2009..2024 | Exact. Used at header ts + 2 h |
| blockchain.com charts API (`api.blockchain.info/charts/...`) | `/robots.txt` serves the API docs page (no rules); www.blockchain.com robots allows `*` except search pages | mempool-size and mempool-count (15-min snapshots), hash-rate, transaction-fees | mempool from 2016-06-14; others 2009.. | Mempool snapshots were recorded live. Used the last snapshot <= 00:00 D+1, at 02:00 |
| IC M1 BTCUSD / ETHUSD / US500 / XAUUSD (local) | - | prices, actual spreads | BTC 2017-08-28.., ETH 2017-09-25.. | - |

No host disallows ClaudeBot / anthropic-ai / Claude-Web. web.archive.org was not used, and no account, key or email
was involved.

## Method (as declared)
- Entry: the first IC bar at or after the signal (daily series D+1 02:00 UTC; retarget at header + 2 h), whatever
  the gap up to 3 days. Weekend signals before 2024-04 enter at the Sunday / Monday open.
- Exit: the last bar at or before entry + h, with h of 1 / 3 / 5 d. One open trade per cell.
- Cost: half spread per leg at the actual bars. Swap: specs.SWAPS / `swap_frac_at`, BTC long -4.96 bp per rollover
  (x3 Friday), short 0, with a sensitivity check charging shorts -5 bp.
- Eras: IS 2017-09..2021 (IC data start), VAL 2022-24, PRE 2012-01..2017-08 at mid on Coin Metrics PriceUSD (00:00
  reference at or after the signal).
- Statistics: t clustered by entry day. Random control: 300 seeds, same count and hold at the cell's clock; fixed
  sides kept, r3 sides recomputed.

## Results (BTCUSD, bp per trade; net = mid - spread cost + swap)
| hypothesis | PRE mid (t) n | IS n: mid (t) / cost / net (t) | VAL n: mid (t) / cost / net (t) | VAL/IS | Sharpe/trade IS / VAL; power at HOLD n (VAL Sharpe) | x1.5 / +1 min IS; VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| F1a ribbon cross long 5 d | +105 (0.34) 6 | 7: -106 (-0.25) / 8 / -135 (-0.32) | 5: +279 (1.22) / 5 / +253 (1.09) | < 0 | -0.12 / 0.49; 0.8 (n 3) | -139 / -131; 250 / 259 | 24 / 80 % | none |
| F1a Edwards buy long 5 d | +235 (0.87) 6 | 6: +314 (1.17) / 10 / +283 (1.05) | 3: +242 (0.73) / 6 / +215 (0.65) | 0.76 | 0.43 / 0.38; 0.5 (n 2) | 278 / 282; 211 / 218 | 71 / 73 | none (n 6 / 3; IS t 1.05) |
| F1b capitulation onset short 5 d | -90 (-0.48) 6 | 7: -169 (-0.40) / 7 / -176 (-0.42) | 6: +246 (0.50) / 4 / +242 (0.49) | < 0 | -0.16 / 0.20 | | 47 / 84 | none |
| F1c capitulation state short 1 d | -42 (-2.05) 141 | 290: +3 (0.10) / 11 / -8 (-0.25) | 200: +8 (0.33) / 4 / +5 (0.19) | - | -0.02 / 0.02; 0.2 | -13 / -7; 3 / 5 | 90 / 84 | none |
| F2 difficulty rel-all 1 d | -29 (-0.83) 160 | 116: -34 (-0.82) / 14 / -50 (-1.21) | 80: +79 (2.05) / 4 / +72 (1.88) | < 0 | -0.11 / 0.21; 1.43 (n 46) | -57 / -49; 70 / 73 | 22 / 99 | none (sign flips IS / PRE) |
| F2 rel-all 5 d | -128 (-1.51) 160 | 116: +1 (0.02) / 14 / -24 (-0.26) | 80: +154 (1.93) / 4 / +138 (1.73) | < 0 | -0.02 / 0.19 | | 48 / 98 | none |
| F2 rel-big (\|rel\| >= 5 pp) 5 d | -172 (-1.26) 75 | 52: +40 (0.27) / 17 / +12 (0.09) | 18: +180 (1.13) / 3 / +163 (1.01) | 13 | 0.01 / 0.24 | | 61 / 87 | none |
| F2 raw drop (<= -2 %) long 1 d | +99 (1.80) 11 | 18: -71 (-0.61) / 9 / -84 (-0.72) | 15: +98 (1.51) / 3 / +89 (1.38) | < 0 | -0.17 / 0.36 | | 23 / 86 | none |
| F2 raw drop long 5 d | +347 (2.62) 11 | 18: -3 (-0.01) / 10 / -34 (-0.13) | 15: +146 (1.44) / 3 / +121 (1.19) | < 0 | -0.03 / 0.31 | | 32 / 71 | none (IS < 0) |
| F3 hashprice fresh 90-d low short 1 d | -44 (-0.94) 24 | 19: +145 (0.53) / 23 / +122 (0.45) | 16: -164 (-1.72) / 4 / -168 (-1.76) | < 0 | 0.10 / -0.44 | | 92 / 3 | none |
| F3 fresh low short 3 d | -214 (-2.45) 24 | 19: +258 (0.98) / 17 / +241 (0.91) | 16: -185 (-1.15) / 4 / -189 (-1.18) | < 0 | 0.21 / -0.30 | | 97 / 11 | none |
| F3 state short 1 d | -24 (-1.38) 518 | 222: -0 (0.00) / 25 / -25 (-0.50) | 132: -45 (-1.21) / 5 / -50 (-1.34) | - | -0.04 / -0.13 | | 69 / 10 | none |
| (control) price fresh 90-d low short 1 d | +194 (0.83) 6 | 10: +241 (1.80) / 28 / +214 (1.58) | 10: -212 (-1.32) / 6 / -218 (-1.37) | < 0 | | | 97 / 2 | same pattern as F3 |
| F4 fee share z > 2 short 1 d (primary) | -40 (-1.41) 153 | 81: -52 (-0.67) / 17 / -69 (-0.89) | 86: -19 (-0.59) / 4 / -24 (-0.72) | - | -0.10 / -0.08 | | 29 / 39 | none |
| F4 fee share short 3 d | -101 (-1.52) 87 | 36: -301 (-1.68) / 18 / -320 (-1.76) | 41: +9 (0.14) / 4 / +4 (0.07) | - | -0.29 / 0.01 | | 3 / 69 | none |
| F4 fee share fade r3 3 d | -12 (-0.17) 87 | 36: +157 (0.85) / 18 / +132 (0.72) | 41: +84 (1.30) / 4 / +74 (1.15) | 0.56 | 0.12 / 0.18; 0.9 (n 25) | 123 / 139; 72 / 48 | 92 / 91 | none (IS t 0.72) |
| F4 mempool z > 2 short 1 d (primary) | -75 (-2.28) 17 | 61: +54 (0.55) / 16 / +38 (0.39) | 39: +51 (1.17) / 4 / +46 (1.07) | 1.2 | 0.05 / 0.18; 0.8 (n 22) | 29 / 37; 44 / 44 | 91 / 92 | none (IS t 0.39) |
| F4 mempool follow r3 1 d | -6 (-0.16) 17 | 61: +164 (1.72) / 16 / +146 (1.54) | 39: -6 (-0.13) / 4 / -12 (-0.27) | < 0 | 0.20 / -0.05 | 137 / 149; | 100 / 35 | none (VAL < 0) |
| F4 mempool fade r3 1 d | +6 (0.16) 17 | 61: -164 (-1.72) / 16 / -182 (-1.88) | 39: +6 (0.13) / 4 / -1 (-0.02) | - | -0.24 / 0.00 | | 0 / 64 | none |
| BOOK (sum of declared sides) 1 d | -36 (-2.94) 843 | 645: -2 (-0.07) / 16 / -18 (-0.81) | 451: -3 (-0.21) / 4 / -8 (-0.46) | - | -0.04 / -0.02 | -26 / -19; -10 / -8 | 84 / 66 | none |
| A1 hashrate shock (7 d <= 0.9 x 30 d) short 1 / 3 d (addendum) | - | 8: -134 / 14 / -148 (-0.57); 3 d +56 (0.16) | 0 events | - | | | 25 / - | none (n 8; no VAL events) |

The remaining cells (F1a / F1b at 1 / 3 d, F2 rel-all 3 d, rel-big 1 / 3 d, raw drop 3 d, F4 short / fade / follow at
the other holds) are all IS \|net t\| <= 1.76. Full output is in scratchpad `out/res_btc.json` and `res_add.json`;
print it with `scripts/table.py`.
- Ex-2020-03/04 changes no verdict. F1 cells move by 100-250 bp because 2020-03 holds one capitulation episode.
- The short-swap -5 bp sensitivity moves only the short cells, and by <= 5 bp per day held.
- Positive-year counts are <= 3/4 in IS for every cell.
- Random percentiles for fixed-side shorts in the IS bull (85-90 %) only mean "less bad than random shorts". Read them
  with the net.

Second leg and controls (primary cells, net):
- **ETHUSD:**
  - IS cost is 141-215 bp, so every IS net is negative: BOOK -172 (t -6.0), F1c -201 (t -4.8).
  - VAL best is F2 rel-all 3 d, +100 bp (t 1.22, random 97 %), the same VAL-only pattern as BTC.
  - F3 fresh low 1 d is VAL -250 (t -2.50).
  - Nothing else in VAL exceeds t 1.2.
- **US500** (does the BTC network state carry risk-off information?):
  - IS: BOOK -15 (t -2.25), F1c -30 (t -2.75), F1b 5 d -176 (t -4.35 on 7 trades, the 2020-03 episode).
  - VAL: all \|t\| <= 1.97. Fee share short is -20 (t -1.97), against the IS sign of -22 (t -0.85).
  - That is no stable spillover. The IS F1c / F1b values come from the 2018 and 2020 risk-off episodes.
- **XAUUSD:** everything is \|t\| <= 2.1. F1c IS -15 (t -2.12) has VAL -0, and mempool VAL +25 (t 1.75) has IS +6
  (t 0.53). Nothing.

## Cells and chance
- 35 declared cells plus 2 addendum cells = **37 BTC cells**: F1 10, F2 9, F3 3, F4 12 (3 mirror pairs, so ~31
  independent), BOOK 1, A1 2.
  - Information rows not counted: 3 price-only controls, 10 ETH, 10 US500, 10 XAU, and 5 A2 slopes.
- Best \|IS net t\| is 1.88 (sign wrong). Best positive IS net t is 1.54 (mempool follow 1 d), which is -12 in VAL.
- Best VAL net t is 1.88 (F2 rel-all 1 d), which is -1.21 in IS.
- Expected max \|t\| for K = 37 independent cells is 2.40 (95 % 3.20); for K = 31 it is 2.34.
- Every family maximum is below what chance gives.

## What this says
- **BTC network fundamentals carry no 1-5 day BTC edge at IC.** That holds for the practitioner rule (hash ribbons),
  the exact retarget clock, hashprice lows and congestion spikes.
- Miner selling is real but small next to spot turnover (~900 BTC a day before 2024-04, ~450 after). Its timing is
  also discretionary: miners sell through OTC desks over days, not at the retarget block.
- Hashprice in USD is mostly price, so its rules inherit the round 2 / 7 / 11 momentum and reversal results.
- The retarget is predictable days ahead from block times, so any margin relief is priced before the block. This
  explains why the exact, dated retarget timestamp did not help.
- **Power ceiling, even if real:** event rules fire 2-27 times a year (HOLD n 2-46). The daily state rules (n 76-115)
  would need ~90-110 bp net per day for LIVE. The 645-trade BOOK would need ~60 bp per day and delivers -18 / -8.
- This direction is closed.

## Pitfalls
- Coin Metrics community has no difficulty, revenue or hashprice metrics. Compute hashprice as (IssTotNtv +
  FeeTotNtv) x PriceUSD / HashRate.
- mempool.space `difficulty-adjustments/all` rows are [ts, height, difficulty, ratio]. It includes the genesis row
  (height 0) and runs to today, so cut at parse. Its `/robots.txt` and api.blockchain.info's `/robots.txt` return
  HTML pages, meaning no rules.
- blockchain.com `mempool-size` is ~11 MB of 15-min snapshots from 2016-06-14 to today. Parse with the cut, never
  `head` it.
- BTC-denominated hashprice sits at a 90-day low on 80-100 % of days (hashrate growth), so it is not an event series.
  It was dropped before any return.
- The F2 relative change needs a trend reference: raw retarget changes are positive in 72 % of epochs (2017-24 median
  +3.2 %, sd 6.6). Declare the reference before looking.
- Fixed-side rules in a trending era beat most same-side random entries while losing money. Report the net with the
  random percentile.
- IC crypto was closed at weekends until 2024-04. Friday / Saturday daily signals enter up to ~2 days late; A2 keeps
  only weekday-to-weekday days (n 653 IS).

## Directions that need the user
| direction | value |
|---|---|
| Paid miner-flow data (CryptoQuant / Glassnode miner-to-exchange flows, miner reserves; point-in-time versions) | LIVE < 1 %, DEMO ~1 % |
| Pool-level payout / OTC desk data (e.g. Luxor hashprice index history, F2Pool / Foundry payouts; accounts) | LIVE < 1 %, DEMO < 1 % |
| None needed to close this direction: the free block data are complete and exact | - |

## Files
- [HYPOTHESES_N.md](HYPOTHESES_N.md), this file.
- Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r48/N/`:
  - `scripts/`: fetch.py, pull.py, pull2.py, parse.py (the cut), signals.py, engine.py, run.py, addendum.py, table.py;
  - `out/`: cut series, res_*.json, logs;
  - `web/`: raw downloads, requests.log.
