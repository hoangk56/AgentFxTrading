# Round 24, stream B: long history with fetched data (Dukascopy 2004-15)

Written 2026-10-15 16:53 UTC. Hypotheses declared in [HYPOTHESES_B.md](HYPOTHESES_B.md) at 12:01 UTC, before any
return was computed. Two later additions are disclosed there: a venue check, which is information only, and a narrowed
fetch scope, which changed no cell. No 2025-26 price was loaded: the IC panel ends 2024-12-31, and the Dukascopy fetch
stops at 2016-02 for calibration and 2016-12 for AUD/NZD.

## Answer
- **No LIVE or RELAXED candidate.**
  - The turn-of-year basket B4 (gold long plus USD short over the second half of December) and its gold-only variant
    B2 meet the DEMO numbers on IS / VAL. The random-entry control passes only on IS, and on IS + VAL pooled.
  - Both fail RELAXED: their VAL t is 0.04 / 0.35. Both also fail on 2004-15, which nobody had seen.
  - Drafted as [PREREG_DRAFT_B_turn_of_year.md](PREREG_DRAFT_B_turn_of_year.md), **not recommended**.
- **(a) The Sydney V is not a 21-year structure.**
  - Round 16 named this as the decision to price. The mid is about 0.3 bp a year in 2004-10, grows to 1-2 bp from 2011
    and peaks in 2020-22.
  - It is then falling: 2024 was 0.9 bp, and AUDUSD's HOLD was 0.48 bp.
  - Dukascopy reproduces IC's 2016 Sydney V exactly (venue check below), so the small early size is real, not a quote
    artefact.
  - At a 0.4 bp venue the 2004-15 pooled pre-leg would net about +0.36 bp, and about 0 in 2004-10. This weakens the
    "venue cost" route, the only route round 16 found to LIVE.
- **(a) Gold.**
  - The settlement big-day rule L4-G-d shows what its mechanism predicts. In 2009-15, the leveraged-ETF years, it is
    +2.86 bp mid (t 2.08) and +1.35 net (t 0.98). In 2004-08, before the ETFs, it is -0.77 (t -0.39).
  - The LBMA PM and AM fix drops are stable over 2004-15 (+1.36 bp, t 8.5; +1.29, t 13.8) but below cost.
  - The silver fix drop is real from 2008 (+1.6 to +8.3 bp a year). Dukascopy silver is unreliable before 2008.
  - The SGE 02:15 UTC long is a venue effect. It is +0.22 bp (t 1.9) before the auction existed, against +0.93 in IS.
- **(b, c)**
  - The gold autumn effect (Baur 2013) is +437 bp per month in 2004-10, inside Baur's sample. It is -218 bp per month
    (t -2.8) in 2011-24: reversed, as the 2024 replication reported.
  - The Santa Claus rally (US indices) is +66 bp net (t 4.2) in IS and -74 bp in VAL, with only 8 events.
  - The gold January effect and the dollar's January rebound fail.

## Results (bp per trade; t clustered by UTC day, or by year / event for seasonals; IS = design, VAL = check)
| cell | source | where | PRE mid / net (t) | IS mid / net (t) | VAL mid / net (t) | cost PRE / IS / VAL | VAL-size power | tier |
|---|---|---|---|---|---|---|---|---|
| A1 Sydney pre-leg | r16 F19 | AUD+NZD short 09:45-10:00 Syd | +0.76 (6.3) / -0.86 (-7.2) | +1.66 (13.3) / -0.16 (-1.3) | +1.47 (10.0) / -1.12 (-6.2) | 1.62 / 1.82 / 2.60 | -4.7 | none |
| A2 Sydney post-leg | r16 F21 | AUD+NZD long 10:00-10:15 Syd | +0.58 (4.2) / -0.94 (-6.8) | +1.32 (7.9) / -0.18 (-1.1) | +1.50 (6.3) / -0.31 (-1.3) | 1.52 / 1.50 / 1.81 | -1.0 | none |
| A3 J5c | PREREG_J | AUDUSD short, off-rollover days | +0.60 (3.7) / -0.61 (-3.8) | +1.54 (8.8) / +0.44 (2.54) | +1.53 (7.5) / +0.76 (3.77) | 1.21 / 1.10 / 0.77 | 2.86 | DEMO on IS/VAL as registered; HOLD already failed; PRE net < 0 |
| A4 L4-G-d | PREREG_L | XAU into the COMEX settle, top decile | 2009-15 +2.86 (2.1) / +1.35 (0.98); 2004-08 -0.77 / -2.28 | +5.19 (4.6) / +3.76 (3.35) | +3.14 (2.5) / +2.11 (1.70) | 1.51 / 1.43 / 1.03 | 1.29 | DEMO as registered; RELAXED misses only on power (1.29 < 1.5) |
| A5 L4-G-q | r12 L | same, top quintile | 2009-15 +1.46 (1.6) / -0.05; 2004-08 0.00 | +2.60 (3.8) / +1.19 (1.7) | +1.89 (2.4) / +0.89 (1.1) | 1.51 / 1.41 / 1.01 | 0.87 | none (VAL random 75 %) |
| A6 LBMA PM | r15 V (M8) | XAU short 14:59-15:01 London | +1.36 (8.5) / -0.21 (-1.3) | +1.09 (5.2) / -0.36 | +0.94 (2.7) / -0.08 | 1.57 / 1.45 / 1.02 | -0.2 | none (stable, at cost) |
| A7 LBMA silver | r15 V (M9) | XAG short 11:59-12:01 London | +1.02 (2.2) / -3.62 | +2.69 (8.3) / -1.51 | +2.72 (9.1) / -1.88 | 4.64 / 4.19 / 4.60 | -4.7 | none; PRE 2008-15 +1.6..+8.3 a year, 2004-07 < 0 on sparse quotes |
| A8 LBMA AM | r15 V (M10) | XAU short 10:29-10:31 London | +1.29 (13.8) / -0.23 (-2.5) | +0.88 (8.2) / -0.56 | +0.24 (1.9) / -0.75 | 1.52 / 1.44 / 0.99 | -4.5 | none (strong 2004-21, gone in VAL) |
| A9 COMEX open fade | r15 V5 (M11) | XAU fade 08:10-08:20, 08:20-08:30 ET | +0.02 (0.1) / -1.54 | +0.94 (3.1) / -0.79 | +0.95 (2.3) / -0.24 | 1.56 / 1.74 / 1.19 | -0.4 | none; absent in PRE |
| A10 China-session gold | r10 A6 (M3) | XAU long 01:00-03:30 UTC, SSE days | +1.13 (2.2) / -0.63 | +1.98 (2.8) / +0.33 (0.5) | +1.67 (1.8) / +0.61 (0.7) | 1.76 / 1.65 / 1.06 | 0.50 | none |
| A11 China-close fade | r10 A2-close (M4) | XAU fade 06:30-07:00, 07:00-07:30 UTC | +0.90 (3.1) / -0.67 | +0.93 (3.0) / -0.59 | +0.96 (2.0) / -0.06 | 1.57 / 1.52 / 1.03 | -0.1 | none (stable 11/12 PRE years, at cost) |
| A12 SGE placebo | r10 A1-flip (M1) | XAU long 02:15-02:23 UTC | +0.22 (1.9) / -1.50 | +0.93 (8.0) / -0.67 | +0.72 (4.5) / -0.33 | 1.72 / 1.60 / 1.04 | -1.5 | placebo: 0.24x of IS before the SGE auction, so the effect is the venue |
| A13 W1 | r3 W1 (F27) | long the high-yielder 12:00-16:55 NY Wed, 9 pairs | +0.72 (0.7) / -0.59 | +0.52 (0.7) / -0.48 | +1.58 (1.4) / +0.64 (0.6) | 1.31 / 1.00 / 0.94 | 0.43 | none; IS does not reproduce round 3's +2.2 (9 pairs, 0.25 pp gate) |
| **B4** primary | Seasonax; FOREX.com; Gulseven 2016; WGC 2023 | 7 USD legs short + XAU long, 15 Dec -> last weekday of Dec | +30.9 / +26.8 (0.69), 6/12 | +108.3 / **+99.8 (4.08)**, 6/6 | +17.0 / +3.7 (0.04) | 4.1 / 8.5 / 13.3 | 0.03 | DEMO numbers (random IS 100 %, IS+VAL 99.5 %, VAL 60 %); RELAXED fails |
| B1 | same | the 7 USD legs only | +28.2 / +25.2 (0.68) | +82.9 / +74.7 (2.70) | +10.4 / -1.3 | 2.9 / 8.2 / 11.7 | -0.0 | none |
| B2 | same | XAU long, same window | +46.3 / +34.3 (0.47), 5/12 | +285.8 / **+275.8 (15.8)**, 6/6 | +63.0 / +38.7 (0.35) | 11.9 / 10.1 / 24.3 | 0.27 | DEMO numbers (VAL random 54 %); RELAXED fails |
| B3 | WGC 2023; Gulseven 2016 | XAU long, first 20 weekdays of January | +137 / +115 (0.73) | +159 / +141 (0.97) | -77 / -107 (-1.9) | 22 / 19 / 30 | -1.7 | none |
| C1 | Baur 2013 | XAU long, 20 weekdays from 1 Sep and 1 Nov | +165 / +144 (1.23) | -284 / -300 (-3.83) | +72 / +28 (0.15) | 21 / 17 / 44 | 0.11 | none; 2004-10 +437 (t 3.8), 2011-24 -218 (t -2.8) |
| C2 | Hirsch, Stock Trader's Almanac | US500+US30+USTEC long, last 5 + first 2 NYSE days | n/a (IC only) | +90.5 / +66.3 (4.19), n 6 | -36.0 / -74.0 (-1.06), n 2 | - / 24 / 38 | -1.0 | none |
| C3 | Seasonax (January rebound) | 7 USD legs long, first 20 weekdays of January | +101 / +87 (1.38) | -13 / -17 | +31 / +31 (0.28) | 14 / 4 / 0.4 | 0.21 | none |

- **Spread x1.5 and +1 minute.** Neither changes a verdict.
  - B4: IS +99.6 / +100.2, VAL +3.6 / +1.5.
  - A4: VAL +1.90 / +1.38.
- **Random-entry control.** Rule net mean against 200 seeds, each shifted ±1-180 minutes (intraday) or placed on a
  random weekday of the same year (seasonals).
- **PRE / IS mid ratio.**

  | cells | ratio |
  |---|---|
  | A1 / A2 / A3 | 0.46 / 0.44 / 0.39 |
  | A4 (2009-15) | 0.55 |
  | A6 / A8 | 1.25 / 1.47 |
  | A10 / A11 | 0.57 / 0.97 |
  | A12 (placebo) | 0.24 |
- **IS / VAL reproduce the recorded numbers.** A3 is exact: 1,020 trades, +1.54 / +0.44 (t 2.54), VAL +0.76
  (t 3.77). A1 +1.66 (t 13.3) against +1.65 (13.1); A6, A7, A8, A12 match. A4 has 150 IS trades against the record's
  150 (net +3.76 against +3.48; warm-up from Dukascopy 2015). A11 is +0.93 against the recorded +1.21. A13 does not
  reproduce, as stated above.
- **Yearly mid of the Sydney pre-leg (A1).**

  | era | yearly mid, bp |
  |---|---|
  | 2004-10 | -0.34, 0.27, 0.38, 0.33, 0.79, -0.37, 0.23 |
  | 2011-15 | 1.03, 1.24, 2.07, 1.93, 1.53 |
  | IS | 0.85, 1.50, 1.76, 1.76, 2.56, 1.51 |
  | VAL | 2.30, 1.23, 0.89 |

  J5c (A3) is the same: -1.39..+0.93 in 2004-10, +0.6..+2.2 in 2011-15.

## Cells tried and chance
- 20 declared cells (13 in (a), 4 in (b), 3 in (c)); no cell was added after numbers.
- Chance max |t| for 20 normals: median 2.12, p95 3.03.
- The cells above chance on IS (A3, A4, B4, B2, C2) are all small-n or previously registered:
  - B2's t 15.8 rests on 6 yearly observations (5 degrees of freedom) and does not survive VAL or PRE;
  - C2 rests on 6.

## PREREG drafts
- [PREREG_DRAFT_B_turn_of_year.md](PREREG_DRAFT_B_turn_of_year.md): B4 (B2 as variant).
  - DEMO numbers on IS / VAL; not recommended.
  - Expected HOLD t is about 0.02 at the VAL Sharpe and 0.37 at the 2004-24 Sharpe (1 event in HOLD).
- No other draft. A3 and A4 are already registered (PREREG_J rejected in HOLD; PREREG_L a DEMO candidate) and are
  stream C's to re-score. Stream B adds their PRE readings: A3 PRE net -0.61 (t -3.8); A4 PRE 2009-15 net +1.35 (t 0.98)
  with a flat no-ETF placebo.

## Correlation with C3 (IS + VAL; seasonal P&L on the entry day)
| cell | daily | monthly |
|---|---|---|
| B4 | +0.015 | +0.012 |
| B2 | +0.018 | +0.128 |
| A4 | +0.032 | -0.163 |
| A3 | +0.009 | -0.057 |

## Data fetched
- **Dukascopy M1, 2004-01..2015-12**, at research/data/duka/m1c/<SYM>.npz (git-ignored, `data/` in .gitignore). Keys:
  int64 ts ms bar start, float32 bid / ask close (ask NaN where missing), uint16 n = 1 for active minutes. Only active
  minutes are stored.

  | symbol | days fetched | active minutes | size | missing days |
  |---|---|---|---|---|
  | AUDUSD | Sunday-Friday | 4.34 M | 26.5 MB | 16 (0.5 %) |
  | NZDUSD | Sunday-Friday | 4.46 M | 27.3 MB | 18 (0.6 %) |
  | XAUUSD | Monday-Friday | 3.98 M | 26.9 MB | 8 (0.3 %) |
  | XAGUSD | Monday-Friday | 3.47 M | 18.0 MB | 17 (0.5 %) |
  | GBPUSD | Wednesdays only | 0.86 M | 5.0 MB | 25 Wednesdays (4 %) |
  | USDCAD | Wednesdays only | 0.90 M | 5.0 MB | none |

  Total about 109 MB. XAU and XAG have no ASK files for 2004-09.
  - Why the scope was narrowed: Dukascopy throttled to 0.3-3 files/s (requests at 1-11 s, many 503s that a fresh
    connection then served; a 503 is not always "missing"). XAU/XAG were cut to Monday-Friday and GBP/CAD to Wednesdays
    at 14:19 UTC.
  - Missing days are days whose file still failed after 5 fresh connections; they were not repaired.
- **Calibration and venue check**, Dukascopy 2016 against IC, in the scratchpad (dl/cal16):
  - minute alignment 0 (shift ±1 is 10x worse);
  - median |mid diff| 0.07 bp (AUD, GBP, CAD), 0.14 (NZD), 0.17 (XAU), 1.05 (XAG);
  - 1-minute return correlation 0.992-0.996 (XAG 0.93);
  - Dukascopy spreads are 1.5-3x IC's (XAG 21 bp against 7). PRE costs use IC's 2016-17 spreads, as declared.
- **Ask validity (declared rule).** AUD 2011-15, NZD 2012-15 and XAU 2011 + 2013-15 are priced on the mid; all other
  years on the bid, and XAG on the bid throughout. Bid-only reruns change no PRE number by more than 0.1 bp.
- **FRED short rates 2003-2024** (8 series, the same as rates.py, coed 2024-12-31) in the scratchpad (rates_fred/), for
  swaps and W1. They were fetched while the downloader was paused, to keep at most 4 connections.

## Surprises
1. The Sydney V first appears around 2011, and it fits a rise-and-fall regime (2011-2023), not a fixed institutional
   practice like gotobi. Dukascopy and IC agree to the decimal on 2016 (A1 +0.49 vs +0.52, A3 +0.84 vs +0.84, daily
   correlation 1.00; Mondays left out because Sunday files were not fetched for 2016).
2. Gold's settlement big-day effect is absent before leveraged gold ETFs existed (2004-08) and present after. This is
   the first dose-in-time check of that mechanism.
3. Gold's turn-of-year gain is a 2016-2023 phenomenon: 12 earlier years net about 0 with 2012-15 all negative. The
   autumn effect of 2004-10 reversed to a loss in 2011-24.
4. The SGE morning long is about 4x smaller before the 2016 auction, so the venue causes it.
5. Two once-a-year declared seasonals (B4, C2) show IS t > 4 and then nothing in VAL. With 6 IS events, IS t carries
   little information.

## Directions needing the user
- **Venue route (round 16).** Its premise of a stable 21-year Sydney V fails: the V is about 0 before 2011 and falling
  after 2022. A low-cost venue decision should be judged on 2025-26 data only (HOLD AUDUSD 0.48 bp). Expected value:
  lower than round 16 assumed.
- **B4 / B2 as a once-a-year demo.** Not recommended. One event a year and PRE t 0.7. If wanted, data after
  2026-09-24 (December 2026) is the clean test.
- **A4 (gold settlement big days, DEMO).** PRE supports the mechanism (placebo flat, LETF years positive) but net t is
  only 0.98 at PRE cost. The existing demo decision stands.

## Files
- Scratchpad
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r24/B/`:
  - scripts/:
    - `duka_dl.py`: the fetcher (keep-alive, UA, 503 means a reconnect);
    - `convert.py`;
    - `lib.py`: dense 2004-24 series, clocks, PRE cost table, swap;
    - `cells_a.py`, `cells_bc.py`, `assess.py`, `corr_c3.py`, `calib.py`, `venue2016.py`;
    - `repair.py` (not run).
  - out/:
    - `res_a_*_declared.json` and `res_bc_declared.json`;
    - `bc_declared_final.txt`;
    - `assess.md`, the tier table;
    - `rows_*.npz`.
  - dl/: `requests.log` (30,443 m1 requests) and the cal16 files. cal/cal_B.json holds the England and SSE holidays.
- Repo:
  - HYPOTHESES_B.md, this file, PREREG_DRAFT_B_turn_of_year.md;
  - the data in research/data/duka/m1c/.
  - No other repo file was touched.
