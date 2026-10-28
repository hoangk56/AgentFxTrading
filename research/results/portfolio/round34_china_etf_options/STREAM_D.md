# Round 34, stream D: Deribit option flows -> BTCUSD at IC (4 hours to 5 days)

Written 2026-10-28 01:25-01:40 UTC (`date -u`). Hypotheses are in [HYPOTHESES_D.md](HYPOTHESES_D.md):
- round 1 (45 cells) declared 20:33-20:50 UTC, before any return was computed;
- round 2 (10 cells, reconstructed dealer gamma) declared 21:03-21:12 UTC, after the round-1 IS numbers and before any
  VAL number or gamma value.

HOLD was never requested: every API call had `end_timestamp` < 2025-01-01 (last trade loaded 2024-12-31 23:59:54
UTC), and IC M1 was cut at ts < 1735689600000.

## Answer
**No LIVE, no DEMO, no PREREG_DRAFT.**
- No cell of the 55 reaches IS net t 2.0. The best registered IS net t is +1.49 (F3 risk reversal, k 1.5, 5 days),
  and it is -0.01 in VAL.
- **Option-flow signals (net delta demand, put-buy share, skew, VRP, block delta) carry no 1-5 day or 4-hour edge for
  BTC.** Their linear slopes are 0 +- 10 bp per sd in both eras, with or without momentum controls.
- The one real effect is the round 12 K4 lead (fade 07:00-08:00 UTC into the Friday 08:00 Deribit expiry, 08:01-09:00),
  now conditioned with data the free tape provides:
  - Fridays with high expiring near-the-money volume: VAL net +16.7 bp (t 3.24), random 100 %, power 2.47.
  - Fridays with reconstructed negative dealer gamma: VAL net +9.0 (t 2.40), random 91 %; last Fridays +15.3
    (t 3.21), power 2.47.
  - Both fail IS at the 2017-21 IC cost (11-12 bp round trip): IS net t 0.80 and 1.42. In IS, the volume condition
    even points the wrong way (low-volume Fridays have the larger gross).
  - This is the PROMPT pattern again: real at mid and stronger in VAL, but the IS bar cannot be met on 2017-21 BTC
    costs.

## Sources
| source | fetched | span | usable? |
|---|---|---|---|
| history.deribit.com `public/get_last_trades_by_currency_and_time` (currency BTC, kind option, count 10,000, sorting asc), public, no key | every BTC option trade: time, instrument (expiry / strike / C-P), price, amount, taker direction, trade iv, index, mark, block / combo flags | 2017-06-01..2024-12-31: 16.5 M trades (2017 H2 54 k, 2018 187 k, 2019 433 k, 2020 1.32 M, 2021 2.93 M, 2022 2.96 M, 2023 3.57 M, 2024 5.05 M); block trades from 2019 (345 that year, 25-65 k a year from 2021) | yes. Real-time tape, not restated. 1,722 requests x 200, 2 x 404 (robots.txt probes; none exists on either Deribit host), 0 x 429. One job on the host, >= 1.1 s after each response; 20:31-22:20 UTC |
| api.openalex.org, api.semanticscholar.org | 8 literature queries / abstracts | - | Alexander, Deng, Feng & Wan 2022 JFM abstract used. Wei, Koutmos & Zhu 2024 FRL and Shen, Li & Luo 2026 FRL have no free abstract (not used for any side). 1 WebSearch |
| IC M1 BTCUSD (local) | prices, spreads | 2017-08-28..2024-12-31 | yes |

Not pulled:
- **Deribit ETH options.** ETH's IC spread in 2018-20 (89-254 bp) makes any ETH IS net negative (rounds 31 C,
  33 K), so ETH could only be information; the BTC pull used the time.
- **Deribit open interest history.** Not in the free API (current OI only). Dealer positions were reconstructed from
  signed trades instead (round 2).
- Other crypto option venues (OKX, Bybit, CME) were not probed. Their options start 2020-23, which is too short for
  the IS bar.

## Method (round 31 C engine, copied)
- **Prices and fills.** IC mid; entry at signal + 1 min; exit at the last quote at or before the exit time. Weekend
  signals are skipped while IC is closed.
- **Costs.** Half the actual spread at each leg. Swap: long -5 bp per 17:00 NY rollover (x3 Friday), short 0.
- **Checks.** +1 min on both legs; spread x1.5; short swap -5 bp.
- **Statistics.** Non-overlapping trades; t clustered by day; 200-seed random control with the side recomputed at the
  random time.
- **Signal timing.** Daily signals use trades of UTC day D and enter at D+1 00:00. 4-h signals use the bar's trades
  and enter at the bar end. K / G3 use trades up to Friday 07:00 and enter at 08:00.
- **Per trade.** Black-Scholes delta and gamma from the trade's own iv (r = 0, forward ~ index).

## Results (bp per trade, BTC; full output: scratchpad `r34/D/out/run_all.txt`)
| hypothesis (best / notable cell) | eras | mid IS / VAL (t) | cost IS / VAL | net IS / VAL (t) | VAL / IS | Sharpe/trade IS / VAL; power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| F1 net delta demand follow, daily k1.5 1 d (best of 9 daily) | IS 17-21, VAL | +39.3 (1.19) / +5.3 (0.20) | 15.3 / 5.5 | +23.9 (0.73) / -0.2 (-0.01) | ~0 | 0.056 / -0.001; 0.46 / -0.01 | 74 / 55 % | none |
| F1 daily k2.0 3 d | same | -141 (-1.69) / -10 (-0.16) | 16.5 / 10.1 | -158 (-1.88) / -20 (-0.32) | - | < 0 | 11 / 48 % | none (IS sign against the informed side; not in VAL) |
| F1 4-h NDD follow (4 cells) | same | IS -24.7..+3.3; VAL -10.6..+18.6 | 11-15 / 3.5-5.4 | IS -39.7..-10.1 (<= -0.74) / VAL best +13.4 (0.59) | - | <= 0 IS | 6-60 / 22-82 % | none |
| F2 buyer-initiated put share, Pan-Poteshman side, k1.5 1 d (best IS) | same | +25.5 (0.74) / +21.6 (0.75) | 15.7 / 4.9 | +9.8 (0.29) / +16.7 (0.58) | 1.7 | 0.022 / 0.050; 0.18 / 0.44 | 77 / 74 % | none |
| F2 k2.0 1 d | same | -40 (-0.91) / +53 (1.00) | 13.7 / 4.1 | -54 (-1.21) / +49 (0.92) | sign flip | - | 26 / 88 % | none |
| F3 risk reversal follow, k1.5 5 d (best IS of all 55) | same | +174 (1.74) / +12 (0.12) | 26 / 13 | +147 (1.49) / -1 (-0.01) | ~0 | 0.168 / -0.002; 0.94 / -0.01 | 80 / 45 % | none (decays; 2017 = +872 of it) |
| F3 k1.5 1 d | same | +45 (1.08) / +27 (1.01) | 13.9 / 5.4 | +31 (0.75) / +22 (0.81) | 0.70 | 0.055 / 0.062; 0.47 / 0.62 | 73 / 86 % | none |
| F4 VRP high -> long, k1.0 5 d (best IS) | same | +101 (1.04) / -28 (-0.43) | 24.7 / 15.7 | +77 (0.78) / -44 (-0.66) | < 0 | - | 86 / 39 % | none; 1-d OLS slope IS **-36 bp/sd (t -2.25)**, the opposite of the BTZ side, VAL -3.5 |
| F5 block delta follow, k2.0 1 d (IS 2019-21 only) | IS 19-21, VAL | -34 (-0.51) / +78 (1.62) | 8.9 / 5.7 | -43 (-0.64) / +72 (1.50) | sign flip | - / 0.205; - / 1.15 | 26 / 92 % | none (IS < 0) |
| K K4 fade on high expiring near-money volume Fridays (> trailing-26 median), 1 h | IS 17-21, VAL | +17.4 (2.31) / +20.0 (3.90) | 11.4 / 3.3 | +6.1 (0.80) / **+16.7 (3.24)** | 2.7 | 0.067 / 0.345; 0.51 / 2.47 | 31 / 100 % | none (IS net t; IS low-volume half is stronger) |
| K top tercile, all Fridays | same | +21.6 (2.34) / +15.4 (2.92) | 12.4 / 3.4 | +9.2 (0.99) / +12.1 (2.27) | 1.3 | 0.095 / 0.280; 0.63 / 1.74 | 46 / 80 % | none |
| K check: low-volume Fridays / all K4 | same | +29.3 (1.38) / -0.6; all +21.3 (2.48) / +11.2 (3.13) | 12-15 / 3.3 | +14.8 / -3.8; all +8.9 (1.05) / +7.9 (2.20) | - | - | - | information (round 12 K4 reproduced) |
| G1 4-h move: follow when dealer gamma < 0, fade when > 0, k1 4 h | IS 18-21, VAL | -9.9 (-1.66) / +1.7 (0.37) | 14.4 / 4.3 | -24.3 (-3.94) / -2.6 (-0.57) | - | < 0 | 4 / 86 % | none (no gamma-regime effect) |
| G2a / G2b one regime at a time (4 cells) | same | IS gross -8..-20 in all 4 | 13-20 / 4-5 | IS -21..-40 (to -3.22) | - | < 0 | 4-20 % | none |
| G3 K4 on Fridays with dealer gamma < 0 (the paper's condition), all Fridays | same | +29.7 (2.21) / +12.3 (3.30) | 10.9 / 3.3 | +18.8 (1.42) / **+9.0 (2.40)** | 0.48 | 0.133 / 0.199; 0.90 / 1.83 | 88 / 91 % | none (IS net t 1.42) |
| G3 last Fridays, gamma < 0 | same | +44.6 (0.87) / +18.5 (3.92) | 11.2 / 3.3 | +33.4 (0.65) / +15.3 (3.21) | 0.46 | 0.130 / 0.558; 0.42 / 2.47 | 48 / 96 % | none (n 26 / 34) |
| G3 check: gamma > 0 Fridays | same | +8.4 / -5.8 | | -4.0 / -8.8 | | | | information: the reversal sits on negative-gamma Fridays |

Per-year net, K high-volume Fridays: 2017 +13, 2018 -24, 2019 +25, 2020 +7, 2021 +17 | 2022 +6, 2023 +19, 2024 +28.
G3 all Fridays: 2018 -24, 2019 +5, 2020 +13, 2021 +46 | 2022 -0, 2023 +16, 2024 +11. Both lose 2018, when the IC
spread was 16.6 bp.

## Information checks
- **OTM-only NDD (Alexander et al.'s directional channel).** No stronger than all-option NDD: the best is +16.3
  (t 0.69) IS and +12.8 (0.70) VAL.
- **Momentum control.** 1-day OLS on the continuous signal, bp per sd, IS / VAL:

  | signal | slope IS / VAL | with past 1 / 7 / 28-day returns |
  |---|---|---|
  | NDD | +3.4 / -7.0 | +1.5 / +0.7 |
  | NDD OTM | +6.3 / -1.5 | +5.5 / +6.9 |
  | PBS | -1.2 / -1.7 | |
  | RR | +10.5 / -3.5 | |
  | VRP | -31.9 (t -1.94) / -3.3 | |
  | blocks | +0.1 / +10.2 | |

  All t <= 1 except VRP IS. File `out/momctl.txt` (also 3- and 5-day horizons and the IS 2017-19 / 2020-21 split).
- **Dealer gamma**, reconstructed with dealer = - cumulative taker-signed amount. GEX < 0 on 73 % of 4-h bars
  2018-24 (2018 37 %, 2019 43 %, 2020 61 %, 2021 85 %), i.e. by this convention customers were net long options in
  the bull years.
  - The convention is crude: takers are not always customers.
  - The only place gamma separates outcomes is the expiry Friday (G3 vs its check). Continuation / reversal of
    ordinary 4-h moves does not depend on it.

## Cells and chance
- Cells:

  | family | cells | best IS net t |
  |---|---|---|
  | F1 | 13 | +0.73 |
  | F2 | 9 | +0.29 |
  | F3 | 9 | +1.49 |
  | F4 | 6 | +0.78 |
  | F5 | 4 | +0.02 |
  | K | 4 | +0.99 |
  | G | 10 | +1.42 |
  | **total** | **55** (+ 12 information rows) | |

- Expected max |t| of K independent normals (95 %):
  - 13 cells: 1.99 (2.87);
  - 45 cells (round 1): 2.47 (3.26);
  - 55 cells: 2.54 (3.31).
- The best IS net t (+1.49) is below what chance gives for the family alone.
- The VAL t of 3.2 in the K / G3 rows comes from conditioning K4, which round 12 already found at VAL t 2.20 net.
  The registered sides were fixed in advance, but 8 K / G3 cells were tried on the same lead.

## What this says
1. **Deribit option order flow does not forecast BTC at 4 h to 5 days at a tradable size.**
   - Net delta demand, the put-buy share and blocks are all ~0, and the "informed" side is no better than its mirror.
   - Market makers absorb and hedge the flow within the bar. This fits Alexander et al.'s finding that order-imbalance
     effects fade as volume grows, and the 10x volume growth from 2019 to 2021.
2. **Skew and VRP have IS-only effects that vanish in VAL**, which is the usual decay pattern. The VRP slope even has
   the opposite sign to the equity literature in IS.
3. **The Friday expiry reversal is the one option-flow effect that holds.**
   - The tape confirms the paper's conditions: the reversal sits on negative-gamma Fridays and, in VAL, on Fridays with
     heavy near-money expiring volume.
   - It is a 10-20 bp gross effect over one hour, about 50 times a year. At 2017-21 IC costs it is 6-19 bp net,
     t <= 1.42, so it fails IS. The 2022-24 numbers (net t 2.4-3.2, power 1.8-2.5) would be DEMO-grade if IS were
     judged at today's cost, which is a bar change and is not proposed.
   - It also fails LIVE's power 3 at the VAL size.

## Directions that need the user (value = chance the direction yields a LIVE candidate)
- **Judge the K4 / G3 Friday expiry fade on a 2020-24 or 2022-24 design window.** This is a bar change. VAL power is
  2.47, so even then it is DEMO, not LIVE: value ~2 % for LIVE, ~25 % for a DEMO that survives HOLD.
  - A forward demo log needs no bar change. The rule is fixed and can be logged from the live Deribit tape (EXV and
    reconstructed gamma are computable in real time).
- **Paid Deribit OI / Greeks history** (Tardis.dev, Laevitas, Amberdata). It would replace the reconstructed gamma and
  the volume proxy with the paper's true ATM OI and dealer gamma. Value ~2 %: the condition is already visible in the
  free proxy, and the binding constraint is IS cost, not the conditioning variable.
- **ETH options (free, ~1 h pull).** Value < 1 %: IS cost.

## Files
- Hypotheses: research/results/portfolio/round34_china_etf_options/HYPOTHESES_D.md; this file STREAM_D.md (same
  folder). No PREREG_DRAFT.
- Scratchpad root `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r34/D/`:
  - `scripts/`:
    - pulling: pull_trades.py, fetch.py;
    - series: build.py (4-h bars), gex.py (dealer gamma), series.py;
    - engine: deng.py (copy of round 31 C's r31c.py);
    - cells and checks: run_d.py, momctl.py.
  - `out/`: run_all.txt, cells_F1_F2_F3_F4_F5_K_CHK_G.json, momctl.txt, pull_btc.log, is_prelim.txt and
    g_is_prelim.txt (the IS-only runs made before VAL existed).
  - Data: `data/BTC/*.npz` (monthly trades), bars_BTC.npz, gex_BTC.npz. The request log is web/requests.log.
- Process notes:
  - The IS runs were made while 2022-24 was still downloading. The VAL lines of those runs (partial data) were
    filtered out unread.
  - My background waiters used `pgrep -f`, which matched their own command lines, so they never fired. The pull
    finished at 22:20 UTC and the final run started at 01:21. No data was affected.
