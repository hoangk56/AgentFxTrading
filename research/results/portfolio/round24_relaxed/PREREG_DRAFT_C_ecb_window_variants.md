# PREREG DRAFT (round 24, stream C): the EURUSD ECB-fix window variants F2, F3, F4, F5. Tier RELAXED (and DEMO numbers)

Draft written 2026-10-15 12:05 UTC (`date -u`). HOLD (2025-01 onwards) was not opened. Rules as recorded in rounds
13-15 and re-declared in [HYPOTHESES_C.md](HYPOTHESES_C.md) (11:53-11:55 UTC); nothing chosen here. All four are the
mechanism of the registered DEMO candidate E1 (PREREG_M: short EURUSD 11:00-13:00 London; EUR is sold into the ECB
reference rate at 14:15 CET): they overlap E1 in time on the same symbol and are **not independent of E1 or of each
other**.

## Rules (exact; quotes = close of the last M1 bar ending at or before the time, <= 10 min stale; cost = half spread in
+ half out + 0.6 bp; Monday-Friday by the local date; 24 Dec-1 Jan excluded)
- **F2** (round 14 Q, side from PRE): EURUSD short 04:00 -> 08:00 New York.
- **F3** (round 14 R O1 USD-TOP, declared selector): E1 (11:00 -> 13:00 London) only on days when U = mean of the
  USDJPY and USDCHF log returns from 18:00 New York on the previous weekday to 07:00 London is >= the 67th percentile
  (np.percentile, linear) of U over the previous 250 trading days (>= 60).
- **F4** (round 14 R O2, side from PRE): EURUSD short 12:45 -> 13:00 London, TARGET2 closing days excluded.
- **F5** (round 15 S, **post hoc**): EURUSD short 12:50 -> 13:00 London, Fridays only (an earlier unregistered draft:
  [round15_short_windows/PREREG_DRAFT_S_eurusd_friday_ecb_prefix.md](../round15_short_windows/PREREG_DRAFT_S_eurusd_friday_ecb_prefix.md)).

## Numbers (net bp per trade, t clustered by day)
| row | IS n | IS mid / net (t) | VAL n | VAL mid / net (t) | x1.5 IS / VAL | +1 min IS / VAL | random IS / VAL | power VAL (IS) | VAL/IS mid | C3 corr daily / monthly |
|---|---|---|---|---|---|---|---|---|---|---|
| F2 | 1525 | +2.46 / +1.82 (3.57) | 765 | +2.48 / +1.85 (2.34) | +1.79 / +1.84 | +1.61 / +1.33 | 100 / 98 % | 1.77 (1.92) | 1.01 | +0.040 / +0.179 |
| F3 | 381 | +3.02 / +2.39 (3.29) | 207 | +3.63 / +3.01 (2.60) | +2.38 / +3.00 | +2.29 / +2.66 | 100 / 99.5 % | 1.98 (1.77) | 1.20 | +0.051 / +0.101 |
| F4 | 1509 | +1.11 / +0.44 (2.41) | 757 | +1.14 / +0.52 (2.09) | +0.41 / +0.51 | +0.44 / +0.25 | 100 / 100 % | 1.59 (1.30) | 1.03 | +0.026 / +0.043 |
| F5 | 305 | +1.76 / +1.13 (3.81) | 153 | +1.95 / +1.31 (2.74) | +1.11 / +1.28 | +0.96 / +0.70 | 100 / 100 % | 2.08 (2.04) | 1.11 | +0.036 / -0.054 |
| E1 (reference, registered) | 1525 | +1.80 / +1.17 (3.29) | 765 | +1.97 / +1.35 (2.46) | +1.15 / +1.34 | +1.08 / +1.04 | 100 / 98 % | 1.87 (1.77) | 1.10 | +0.043 / +0.064 |

By year (net): F2 2016 +2.81 ... 2022 +4.18, 2023 +1.14, **2024 +0.24**; F3 2022 +4.99, 2023 +2.51, 2024 +1.67;
F4 2020 -1.04, **2024 +0.00**; F5 **2024 -0.05**. 2024 is the weak year for the whole window, as for E1 (+0.19).

## Tiers
- All four pass **RELAXED** and meet the **DEMO** numbers (IS t >= 2.0, VAL net > 0, random >= 90 %, x1.5 and +1 min
  > 0). None reaches LIVE: VAL-size power 1.59-2.08 < 3. Cost needed for LIVE: F2 none (-0.65 bp), F3 none (-0.94),
  F4 +0.16 bp round trip, F5 +0.07 (IC's is 0.62-0.64), i.e. only a venue without the 0.6 bp commission.
- Multiple testing: these are 4 of 60 recomputed rows; F3's selector was one of 96 round-14 R cells (family p 0.08),
  F5 the best Friday slot of round 15's post-hoc leads.

## Expected HOLD (2025-01..2026-09)
| row | HOLD trades | exp. HOLD t at VAL size | at 0.65 of VAL mid | at 0.25 of VAL mid |
|---|---|---|---|---|
| F2 | ~441 | 1.77 | 0.94 | -0.01 |
| F3 | ~119 | 1.98 | 1.14 | 0.19 |
| F4 | ~437 | 1.59 | 0.37 | -1.02 |
| F5 (post hoc: 0.25 applies) | ~88 | 2.08 | - | -0.25 |

**What is already known about HOLD for this window:** E1's HOLD was opened on 2026-10-06 (PREREG_M): mid +1.28 bp
(0.65 of VAL), net +0.64 (t 0.99), and **0.00 when both fills are 1 minute late**. F2-F5 trade the same days and
mostly the same minutes, so their HOLD would largely re-read that result (the 0.65 column is the realistic one).

## Recommendation to the lead
- Do not open four more HOLD looks for one mechanism. If one is opened, it should be the one fixed before the data
  and least overlapping with E1's measured HOLD: **F3** (declared selector, expected HOLD t 1.14 at E1's retention,
  1.98 at the VAL size). The others add almost nothing beyond E1's HOLD.
- Cheaper route with no HOLD look: E1 is already a DEMO candidate; log on the demo whether each E1 day was a USD-TOP
  day (F3) and the 12:45-13:00 sub-window (F4/F5), and judge them on the demo trades alone.

## Demo (if one is registered; demo account only, fixed small risk; at most one EURUSD position from this family a day)
- Expected demo trades: F2 / F4 ~250 a year, F3 ~65, F5 ~50.
- Stop rule: after 100 demo trades (F3/F5: 60), stop if HOLD + demo pooled net t <= -1.0, or if the realised mean
  round-trip cost exceeds 1.5 bp (F4/F5: 1.0 bp, since their edge is ~1.1-1.9 bp mid).
- Promotion rule (RELAXED -> LIVE): HOLD + demo pooled day-clustered net t >= 2.5 at the costs paid and net > 0 at
  spread x1.5, with at least 100 demo trades. At IC's costs that needs 2-6 years at the VAL size (E1: 24-37 months for
  t 2-2.5 at VAL size, round 16 X).
