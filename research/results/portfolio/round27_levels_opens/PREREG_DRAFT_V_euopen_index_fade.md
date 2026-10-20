# PREREG DRAFT (round 27, stream V): fade a large first-minute move at the European cash open in index CFDs

Draft written by 2026-10-17 21:42 UTC (from `date -u`). **Not registered, HOLD not opened.** Recommendation: **do not open HOLD for
this rule**; at most a forward demo log on data after 2026-09-24 (see "Why not"). Source: [HYPOTHESES_V.md](HYPOTHESES_V.md)
(declared at 21:23 UTC before any return), [STREAM_V.md](STREAM_V.md).

## What met the DEMO numbers
Two cells of the declared family EU-OPEN V2 (fade), same spec: w = 60 s, k = 4, h = 15 min, no stop.
- **A, US30 on IC ticks**: IS net +9.26 bp per trade (day-clustered t 2.23, n 59), VAL +4.65 (t 0.85, n 14).
- **B, UK100 at minute level** (IC M1 panel; no UK100 ticks exist locally): IS net +13.15 (t 2.12, n 42), VAL +17.07
  (t 2.40, n 14).
Both pass x1.5 spread, +1 minute and the random-time control (IS 1.00; VAL 0.92 / 1.00). Both are **within chance**.

## Exact rule (both variants)
- Clock T = 08:00:00 Europe/London (DST-aware; the LSE continuous open and the Xetra 09:00 CET opening auction, one
  instant).
- Days: A: weekdays when both the LSE (XLON) and Xetra (XETR) are open; B: LSE trading days.
- Opening move: A: p0 = prevailing mid (last tick) at 07:59:59, p1 = prevailing mid at 08:01:00; B: p0 = mid at the
  close of the M1 bar starting 07:59, p1 = mid at the close of the bar starting 08:00. The p0 quote must be <= 10 min
  old. m = (p1 / p0 - 1) x 1e4 bp; no trade if m = 0.
- Norm N = median |m| over the most recent 60 clean days of the same rule before today (clean = valid m and no
  calendar exclusion in [07:45, 08:03]); needs >= 20 such days.
- **Event: |m| >= 4 N. Side: against m** (sell when m > 0, buy when m < 0).
- Entry: A: first tick at or after 08:01:00.250 (sell at the BID, buy at the ASK); B: the close of the 08:00 bar
  (live: a market order at 08:01:00 + latency; the declared "+1 minute" check enters at the close of the 08:01 bar).
- Exit: 15 min after the entry target (A: first tick at or after 08:16:00.250; B: the close of the bar starting
  08:15), long at the BID, short at the ASK. No stop.
- Exclusions (both variants): any High / Medium timed ForexFactory row of USD, EUR, GBP or "All" in [07:45, 08:18]
  London; central-bank windows [T_cb - 30 min, T_cb + 120 min]; BOJ days 01:30-07:30 UTC (no overlap at 08:00
  London); untimed High / Medium rows of those currencies = the whole UTC day; election / referendum / vote days and
  the next day.
- Costs: actual spreads (A: ticks; B: half the M1 close spread at entry + half at exit); commission 0 (indices).
- Size: fixed lot, one position per index, no capital dependence; hold 16 minutes.

## Parameters and cell count
w = 60 s, k = 4, h = 15 min, L = 250 ms (A) / bar close (B), no stop. Chosen from a declared grid of **3,924 cells**
(306 in the EU-OPEN V2 family: 288 tick + 18 minute). Nothing was tuned after the numbers.

## IS / VAL numbers (bp per trade; t clustered by UTC day)
| | A US30 (ticks) | B UK100 (minute) |
|---|---|---|
| n IS / VAL | 59 / 14 | 42 / 14 |
| mid IS / VAL | +10.42 (2.50) / +4.97 (0.91) | +15.36 (2.46) / +18.37 (2.58) |
| net IS / VAL at the decision latency | **+9.26 (2.23) / +4.65 (0.85)** | **+13.15 (2.12) / +17.07 (2.40)** |
| net IS L0 / L1000 / next tick / +1 min | +9.25 / +9.41 / +9.34 / +7.49 | - / - / - / +12.85 |
| net VAL L0 / L1000 / next tick / +1 min | +4.41 / +4.49 / +4.51 / +1.61 | - / - / - / +23.44 |
| x1.5 spread IS / VAL | +8.67 / +4.48 | +12.05 / +16.42 |
| VAL / IS | 0.50 | 1.30 |
| median net IS / VAL | +1.01 / +4.59 | +6.31 / +12.71 |
| share of trades > 0 IS / VAL | 0.54 / 0.71 | 0.64 / 0.71 |
| IS without March-April 2020 | +2.69 | +5.49 |
| March-April 2020 share of the IS sum | 12 trades, 77 % | 9 trades, 67 % |
| years > 0 | 6 / 9 | 8 / 9 |
| random-time control beaten IS / VAL | 1.00 / 0.92 | 1.00 / 1.00 |
| random-direction control beaten IS / VAL | 1.00 / 0.81 | 0.99 / 0.99 |
| shifted clock 07:30 IS / VAL; 08:30 IS / VAL | +0.24 / -2.57; -4.03 / -2.93 | -1.71 / -9.59; +6.10 / -6.44 |
| venue-shut placebo | n/a (no k = 4 event on the few LSE + Xetra holidays) | n/a |
| power per trade IS / VAL size | 1.20 / 0.65 | 1.14 / 1.82 |

By year (net bp, n):
- A: 2016 -3.8 (1), 2017 +0.5 (2), 2018 +4.5 (21), 2019 -4.0 (7), 2020 +27.4 (17), 2021 +1.5 (11), 2022 -6.6 (8),
  2023 +36.2 (1), 2024 +16.4 (5).
- B: 2016 +18.1 (4), 2017 +18.4 (1), 2018 +11.9 (11), 2019 -1.0 (8), 2020 +20.5 (16), 2021 +5.6 (2), 2022 +20.0 (5),
  2023 +36.1 (3), 2024 +5.2 (6).

## HOLD expectations and correlation
- Expected HOLD events (VAL rate 4.7 a year x 1.73 years): **about 8 per variant.**
- Expected HOLD t: A **0.65** at the VAL per-trade Sharpe (0.227), 0.42 at 0.65 of it; B **1.82** at the VAL Sharpe
  (0.641), 1.18 at 0.65 of it. Neither reaches 2. Round 18's retention for rules picked after seeing VAL (19-31 %)
  would put both near 0.2-0.6.
- Daily net correlation with C3 (IS + VAL rows): A +0.009 over all weekdays, +0.006 over its 73 trade days; B +0.005,
  -0.039 over 56 trade days.
- Demo trades a year: ~5 per variant (~10 for both).

## Demo rules, if the user wants a forward log anyway
- Stop rule: after 12 demo trades of a variant, stop it if its mean net is <= 0.
- Promotion rule: HOLD + demo pooled day-clustered t >= 2.5 (round 13's DEMO rule). At ~5 trades a year this takes
  many years; it is a DEMO idea at most.

## Why not (recommendation)
1. **Within chance.** The best IS net t over the 3,924 declared cells is 2.23, below the per-day sign-flip null's
   **median** of the max (2.31; p95 3.06). Two DEMO-number cells out of 3,924 are what noise gives.
2. **It is a crash-day effect.** Most of each IS sum comes from 9-12 opens in March-April 2020 and from 6 February
   2018; without March-April 2020, A falls to +2.69 bp and B to +5.49.
3. **The siblings disagree.** The same spec on USTEC is IS +1.06 (t 0.32), VAL -7.99 (t -1.58); on the US index pool
   IS +4.99, VAL -3.08; DE40 (minute) IS +17.4 (t 1.85), VAL +8.9 (n 6). A's own VAL t is 0.85, and its h = 5 / 60
   neighbours are negative in VAL.
4. **B is minute-level only.** UK100 has no IC ticks locally, so B's fills are bar closes, not ticks.
5. No PRE era exists locally (no index data before 2016); a Dukascopy index fetch is a user decision.
