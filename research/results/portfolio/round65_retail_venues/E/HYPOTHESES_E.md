# Round 65, stream E: hypotheses (HK leveraged / inverse products rebalancing at the close -> HK50)

Written 2026-11-01 11:52-11:53 UTC (file saved 11:53 UTC; first return computed 11:54 UTC) (`date -u` at start of writing: Sun Nov 1 11:52:07 UTC 2026), **before any HK50
return of this stream was computed**. Loaded so far: HK50 M1 minute coverage and median spread by minute and year
(code/coverage.py; timestamps and spreads only, ts < 2025-01-01).

## Prior information (disclosed)
- Round 13 P already ran the sign-only version on HK50: top-decile |z| days, follow the day's move over the last
  15 / 10 minutes into **16:10 HKT** (end of the closing auction). IS net -4.64 bp (t -3.0, the wrong side, every IS
  year negative), VAL +1.68 (t 0.6). So the "into the auction" window is known to fail on the predicted side; it is
  kept below only as a declared replication cell (C3), not as a candidate.
- Round 34 E: measured LETF doses in the US / Japan add nothing tradable (USTEC VAL-only). Japan's X1 failure is the
  prior. P(DEMO) from stream J: ~3 %.
- WebSearch summaries (2 of 15 used so far) quoted 2025-26 HK L&I turnover and a current AUM figure for 7500. These are
  fund statistics inside HOLD, not prices; not saved, not used.

## Mechanism and timing
- HK L&I products (CSOP 7200 / 7500 HSI 2x / -2x from 2016-17, 7226 / 7552 HSTECH 2x / -2x from 2020-12, plus smaller
  Global X / Samsung / ChinaAMC products) target L x the daily return of the **cash index** (HSI close = closing
  auction 16:00-16:10). They are futures-based (spot-month HSI / HSTECH futures). Filings found by search say the
  daily rebalance is done "at or around the close of the trading of the underlying futures market". HKFE's day session
  runs to **16:30 HKT**, i.e. 20 minutes after the cash close is fixed. Dose = AUM x L(L-1) x r: 2x AUM x r for 2x,
  6x AUM x r for -2x, both in the direction of the day's move r.
- So two pressure windows are plausible: before the cash close (15:45-16:10, if issuers pre-hedge the expected close)
  and **after the cash close in futures (16:10-16:30)**, when r is known exactly. Round 13 tested only the first.
- After the futures close, the pressure should revert in the T+1 after-hours session (opens 17:15 HKT).

## Data
- HK50: IC M1 cache research/data/m1/HK50.npz (bid OHLC, ask at the bar's last tick), cut at ts < 2025-01-01. Bars
  are labelled by minute start: "price at 15:45" = close of the bar labelled 15:44. HKT = UTC+8, no DST.
- Coverage (fraction of days with the bar): 15:30-16:00 ~0.97-0.99 all years; 16:00-16:29 only 14-19 % of days in
  2016-17, ~full from 2018; 16:30-17:14 empty (gap); 17:15+ present. Median spread 2.5-4.4 bp (2016-23), 1.0 bp in 2024.
  So cells using minutes after 16:00 have an effective IS of 2018-21 (plus the 2016-17 days that have the bars).
- **AUM / units history: not obtained.** csopasset.com answers 403 even to robots.txt (stop, per the rules; CSOP is
  the dominant issuer). HKEX (via agentFx, robots allow): the ETP pages show current data only; the Monthly Bulletin
  JSON exists only for the last 12 months (2025-09..2026-09, HOLD era, not requested; the 2024-12 file is 404); the
  statistics archive page lists no per-product files. Global X HK robots allow everything, but its HSI / HSTECH L&I
  AUM is a small fraction of CSOP's, so a partial dose would mostly measure the wrong thing; not pulled. **Therefore
  only the sign / size rule is tested; the dose is proxied by |r| (the dose is linear in r for fixed AUM).**

## Definitions (fixed now)
- Trading day: a weekday with the 15:44 bar present (half days have no afternoon and drop out).
- Reference close of the previous trading day P: close mid of the bar labelled 16:09 if present, else 15:59.
- Day move at minute m: r_m = ln(mid at close of bar m / P), mid = (bid c + ask ca) / 2.
- Big day: |r_m| >= the 90th percentile (80th for C6) of |r| at the same minute over the previous 250 trading days
  (at least 120 days of history; strictly past days only). Side = sign(r_m) (follow), or -sign for the fade cell.
- Fills: the signal uses the close of bar m; **entry at the close of bar m+1** (the next minute, tradable after the
  signal); long enters at ask, short at bid; exit at the close of the exit bar at bid (long) / ask (short). Net =
  real spread at both ends; no commission on IC index CFDs. If the entry or exit bar is missing, no trade.
- Stress: spread x1.5 (both ends); one step late (entry bar m+2, exit bar +1).

## Declared cells (6 counted; primary C4)
| cell | signal bar m (HKT) | side | entry bar | exit bar (close) | window note |
|---|---|---|---|---|---|
| C1 | 15:44 (price at 15:45) | follow | 15:45 | 15:59 (= 16:00) | continuous session into the cash close |
| C2 | 15:49 (15:50) | follow | 15:50 | 15:59 | last 10 minutes |
| C3 | 15:44 | follow | 15:45 | 16:09 (= 16:10, CAS end) | replication of round 13 P (known IS reversal) |
| **C4** | 16:09 (r at the cash close) | follow | 16:10 | 16:28 (= 16:29) | futures-only rebalancing window before the 16:30 futures close |
| C5 | 16:09 | **fade** | 16:28 (close of 16:28 bar) | 17:29 (= 17:30, after-hours) | reversion of the C4 pressure; side opposite to r |
| C6 | 16:09 | follow | 16:10 | 16:28 | C4 with the top-quintile threshold (more trades) |

- Eras: IS 2016-01-01..2021-12-31, VAL 2022-01-01..2024-12-31. One trade per cell per day.
- t: per-day observations (one trade a day, so day-clustered = plain); also reported ex 2020-03/04.
- Years positive: count of calendar years with net mean > 0 (IS + VAL).
- Random benchmark (per cell, 1,000 draws): the same signal days, a random start minute in 10:00-11:30 or
  13:15-15:15 HKT, side recomputed as sign of the day's move to that minute (fade for C5), same window length and
  cost model. Report the share of draws whose mean net is below the actual. Second benchmark for C4 / C6: random
  non-big days at the same 16:10-16:29 window ("same minutes, smaller days").
- Chance: shared per-day sign flips across the 6 cells, 1,000 draws; report the null of the max IS net t.
- Information only (not counted): the gross mid by window for all days binned by |r| decile (IS only first), and
  the HSTECH-era split (2021-24 vs 2016-20) for C4.

## Bars (unchanged, research/PROMPT.md)
- DEMO: IS net t >= 2.0, VAL net > 0, beats >= 90 % random; positive at costs x1.5 and one step late.
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, >= 95 % random, HOLD power at VAL size >= 3.

## Power arithmetic (before returns)
- Top decile: ~25 trades a year -> ~45 in HOLD (1.82 years). Power 3 needs a net Sharpe per trade of 3 / sqrt(45) =
  0.45. With a 19-minute window on big days (sd ~15-25 bp) that is +7-11 bp net per trade after ~3 bp round trip:
  far above anything round 13 found at the HK close. Top quintile (C6): ~50 / yr -> 91 in HOLD, Sharpe 0.31 needed.
- So LIVE is essentially out of reach even if the mechanism is real; DEMO needs IS t >= 2 (e.g. +5 bp net at sd 20
  over ~100 IS trades for C4, since 2016-17 are sparse after 16:00).
- If any cell passes, write PREREG_DRAFT_E_<name>.md and stop (no HOLD).

## Addendum (2026-11-01 11:55 UTC, after run.py, disclosed as post hoc)
- The declared random benchmark draws windows *before* 16:09 on days selected by |r| at 16:09 (or before the exit for
  C1-C3), so its windows contain part of the selecting move (the PROMPT pitfall). It is reported as declared. A causal
  shuffled-signal benchmark (random era days, same window, side = sign of r) was added in code/bench2.py and is
  reported beside it; it does not change any bar decision.
