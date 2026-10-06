# Stream B: calendar day-of-month x clock windows, PRE 2004-15 discovery -> IS 2016-21 -> VAL 2022-24

Hypotheses and their UTC times: [HYPOTHESES_B.md](HYPOTHESES_B.md). Written 2026-10-06 03:06 UTC. HOLD was never
loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, and era dates stop at 2024-12-23.

## Answer
- **No candidate. No PREREG draft.** None of the 631,915 calendar-day cells clears IS and VAL among the cells the
  brief allows. The eligible IS confirmations are at or below chance: 4 against a null median of 7. All three
  eligible step-3 cells fail VAL, at net -1.41, -3.50 and +0.01 bp.
- **PRE discovery is at the edge of chance.** The max |t_PRE| is 5.73, against a shared sign-flip null with median
  4.86, 95th percentile 5.55 and p 0.025. That cell is USDJPY short 03:15-04:15 London on the 23rd, and it is
  0.0 in IS (t -0.16). By comparison, round 13's every-day clock cells gave 120 cells above that round's threshold.
- **Calendar-day cells are no more stable than business-day cells. Both are at noise level.**
  - Top 500 by |t_PRE| in each class, IS/PRE ratio: CD 0.01, CDL 0.00, PAY 0.08 (0.00 without the gotobi cells).
    Round 13's BD+k/BD-k gives 0.00.
  - The PRE-to-IS t correlation over all cells is 0.06-0.08 for CD, CDL, PAY and BD, against 0.36 for round 13's
    every-day cells.
  - The dates-based structure outside gotobi is not in calendar days either.
- **Information only, related to C3, not a candidate (by the brief):** the 15th, a gotobi date.
  - F15: EURUSD falls 04:00-08:00 New York (09:00-13:00 London) on the 15th, moved back to the previous business day.
    Net IS +5.88 bp (t 2.80), VAL +10.83 bp (t 2.20). It beats 93-98 % of both random controls, and 8 of 9 IS+VAL
    years are > 0. Those are DEMO-like numbers.
  - It is not a gotobi effect: other gotobi days pooled are no different from non-gotobi days in IS (-0.45 bp). It
    is broad USD strength on the 15th. As a 6-pair USD basket it is weaker: net IS +3.73 (t 1.89), VAL +7.69 (t 2.08).
  - It needs a decision by the lead or the user (below).

## Design (as declared)
- Symbols, clocks, windows, exclusions, costs and prices are those of round 13 M, with code reused from
  `r13/M/mcommon.py`:
  - M1 group with 15-minute starts, lengths 15-240 min: EURUSD, USDCHF, USDJPY, EURJPY, GBPJPY.
  - H1 group with hourly starts, lengths 1-4 h: AUDJPY, AUDUSD, GBPUSD, NZDUSD, USDCAD, XAUUSD.
  - Clocks: TOK, LON, NY, SYD, DST-aware.
- 72 day types, on the clock's local date, weekdays only:
  - **CD1-31**: calendar day d.
  - **CDL1-10**: n-th last calendar day.
  - **PAY1-31**: calendar day d, or the previous business day if d is not one. Business days use the clock
    country's holidays (TOK JPY, LON GBP, NY USD, SYD AUD). If d is past the month's end, d is the last day.
- C3 exclusions on JPY pairs:
  - every window overlapping 23:00-02:00 UTC;
  - every event that starts or ends on a Tokyo gotobi date. The gotobi set is wide: 5, 10, 15, 20, 25, 30 and the
    last day, each moved back past weekends, and also past JP holidays.
- Also as round 13: windows touching 16:45-18:15 New York, 24 Dec - 1 Jan, and stale quotes. Cells need at least 30
  PRE events.
- Information-only labels. These cells stay in K and in the nulls:
  - **G-info**: a non-JPY cell with at least 50 % of its PRE events on Tokyo gotobi dates.
  - **Tokyo-fix adjacent**: a non-JPY window overlapping 23:00-02:00 UTC.
- Side: the sign of the PRE mean, fixed before any IS number. IS and VAL statistics were written to a separate file,
  which was opened only after the PRE result was logged.

## Discovery and confirmation, with chance benchmarks
| step | result | chance benchmark |
|---|---|---|
| K | 631,915 cells (500,937 M1, 130,978 H1) | |
| PRE max \|t\| | 5.73: USDJPY short, LON 03:15+60, CD23 | shared sign-flip null, 200 draws: median 4.86, 95 % 5.55, 99 % 5.74 (p 0.025). M1 group 95 % 5.45; H1 group 95 % 5.03 (max 5.04, XAUUSD long, LON 03:00+240, PAY21) |
| set A (overall threshold) / A' (group thresholds) | 1 / 2 cells. **0 confirmed in IS**: USDJPY CD23 IS -0.15 bp (t -0.16); XAU PAY21 IS +4.54 (t 1.64), VAL -5.61 | null count median 0 |
| set B = top 500 (\|t_PRE\| >= 3.72) | **19 confirmed** (t_IS >= 2 on the PRE side); best t_IS 3.42 | IS sign-flip null: median 11, 95 % 22 (p 0.17); null max t_IS 95 % 3.79 |
| set B, eligible (319 cells) | **4 confirmed**, 0 with VAL t >= 1.5 | null median 7, 95 % 17 |
| set B, G-info (121 cells) | 11 confirmed, 7 with VAL t >= 1.5 | null median 2, 95 % 10 (p 0.045) |
| set B, Tokyo-fix adjacent (60 cells) | 4 confirmed, 2 with VAL t >= 1.5 | null median 1, 95 % 4 |
| shrinkage, set B (mean bp on the PRE side) | PRE 5.40, IS 0.17, VAL 0.52 (**IS/PRE 0.03**) | |
| shrinkage, the 19 confirmed | IS 3.53, VAL 3.61 (VAL/IS 1.02). This holds only in the G-info and Tokyo-adjacent cells; the 4 eligible cells go from IS 2.70 to VAL -0.64 | |
| net > 0 in IS and VAL | set B 13.8 % | |

## Matched comparison with round 13 M
For each class: the top 500 cells by |t_PRE|, means on the PRE side. Chance is about 11 confirmations, with a 95 %
point of about 22 for correlated cells.

| class | cells | PRE bp | IS bp | VAL bp | IS/PRE | same sign in IS | IS-confirmed | of which VAL t >= 1.5 |
|---|---|---|---|---|---|---|---|---|
| CD (calendar day) | 267,422 | 5.57 | +0.05 | +0.17 | 0.01 | 0.51 | 14 | 0 |
| CDL (n-th last day) | 88,684 | 5.23 | -0.20 | +0.42 | -0.04 | 0.50 | 16 | 3 |
| PAY (day d, preceding) | 275,809 | 5.30 | +0.41 | +0.38 | 0.08 | 0.61 | 24 | 9 (all G-info) |
| PAY, eligible only | 216,547 | 5.34 | +0.02 | -0.11 | 0.00 | 0.53 | 14 | 0 |
| r13 BD+k / BD-k (business day of month) | 98,960 | 4.45 | -0.01 | +0.24 | -0.00 | 0.56 | 16 | 5 |
| r13 QE / holiday types | 113,096 | 5.86 | +0.15 | +0.40 | 0.03 | 0.49 | 25 | 9 |
| r13 MON..FRI | 47,991 | 2.32 | +0.33 | +0.33 | 0.14 | 0.69 | 51 | 14 |
| r13 ALL (every weekday) | 10,039 | 1.32 | +0.36 | +0.20 | 0.27 | 0.86 | 173 | 55 |

Correlation of t_PRE with t_IS over all cells: CD 0.059, CDL 0.058, PAY 0.078, r13 BD 0.073, r13 ALL 0.363.
Correlation of t_IS with t_VAL: 0.055-0.086 for the calendar classes, 0.332 for ALL.

So calendar-day cells are neither more nor less stable than business-day cells; both are noise at this sample size.
Stability is a property of clocks, not of dates, with gotobi and the 15th below as the exceptions.

## Step-3 cells
Mid bp on the PRE side, with t. Cost = half spread at entry and exit + 0.6 bp. Power = per-trade net Sharpe ×
sqrt(events a year × 1.75).

| cell | PRE / IS / VAL mid | cost IS / VAL | net IS / VAL | VAL/IS | x1.5 / +1 min net IS | years net > 0 (IS+VAL) | random start ±3 h, IS / VAL | day placebo, IS / VAL | power IS / VAL | C3 corr, daily / monthly | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1: EURUSD short, LON 11:15-13:15, PAY22 | +6.52 (4.09) / +3.29 (2.25) / -0.79 (-0.40) | 0.62 / 0.61 | +2.66 (1.82) / -1.41 | -0.24 | +2.65 / +2.56 | 7/9 | 94 % / 14 % | 94 % / 21 % | 0.99 / -0.54 | -0.02 / +0.02 | fails VAL |
| B2: NZDUSD long, TOK 11:00-13:00, CD18 | +6.69 (4.22) / +4.28 (2.22) / -2.34 (-0.55) | 1.26 / 1.16 | +3.02 (1.56) / -3.50 | -0.55 | +2.69 / +4.14 | 6/9 | 81 % / 2 % | 95 % / 34 % | 0.84 / -0.63 | +0.01 / -0.10 | fails VAL |
| B3: EURUSD long, TOK 11:30-12:30, CD27 | +3.61 (3.91) / +1.80 (2.02) / +0.67 (0.68) | 0.69 / 0.66 | +1.11 (1.24) / +0.01 | 0.37 | +1.06 / +1.37 | 6/9 | 100 % / 74 % | 94 % / 59 % | 0.67 / 0.01 | -0.00 / +0.07 | fails: decays, net IS t 1.24 |
| USDCHF short, LON 13:15-13:30, PAY6 | +4.67 (4.22) / +1.45 (2.23) / -0.10 | 1.85 / 2.07 | -0.41 / -2.17 | -0.07 | | | | | | | below cost |

Note on B2: an H1 symbol has no +1-minute PRE number.

None of these had a mechanism written before the data. All three eligible cells look like PRE-era patterns that
faded by 2022.

## Information only (C3-related or Tokyo-fix adjacent; never candidates here)
| cell | PRE / IS / VAL mid | net IS / VAL | excess over the same window on other weekdays, IS / VAL | controls IS / VAL (random start ±3 h; day placebo) | x1.5 / +1 min net IS | power IS / VAL | C3 corr daily / monthly |
|---|---|---|---|---|---|---|---|
| **F15**: EURUSD short, NY 04:00-08:00, PAY15 | +9.06 (3.98) / +6.51 (3.10) / +11.46 (2.33) | +5.88 (2.80) / +10.83 (2.20) | +4.25 (1.97) / +9.42 (1.89) | 93 % / 95 %; 98 % / 98 % | +5.86 / +5.38 | 1.51 / 1.68 | +0.06 / -0.05 |
| T8: USDCHF long, SYD 08:15-12:15, CDL8 (Tokyo morning of the 23rd/24th) | +7.86 (3.98) / +4.71 (3.42) / +7.77 (3.96) | +3.18 (2.34) / +6.38 (3.36) | +4.43 (3.11) / +7.66 (3.68) | 80 % / 75 %; 100 % / 98 % | +2.71 / +3.53 | 1.26 / 2.56 (12 VAL events) | +0.01 / +0.05 |
| G5: USDCHF long, LON 06:30-08:30, PAY5 | +6.20 (3.78) / +2.88 (2.00) / +7.13 (2.42) | +1.86 (1.29) / +6.21 (2.11) | +2.77 (1.87) / +8.12 (2.69) | 93 % / 100 %; 98 % / 100 % | +1.65 / +1.47 | 0.70 / 1.61 | -0.00 / +0.06 |

Notes on T8 and G5:
- T8 is about 7 events a year, because the NY rollover exclusion removes the northern-winter dates. It is net > 0
  in 8 of 9 IS+VAL years. It sits just before the 25th (the Japanese payday, a gotobi date) and overlaps the Tokyo
  fix, so it reads as C3's Tokyo-morning USD demand seen on CHF.
- G5's net IS t is 1.29, under DEMO.

What F15 is (steps 4-5, post hoc, reporting only):
- **Years.**
  - PRE: 11 of 12 years > 0.
  - IS: 6 of 6.
  - VAL: 2022 +14.2, 2023 +21.5, 2024 -3.3 bp.
  - PRE without the SNB day (2015-01-15, which falls inside the window): +8.99 bp (t 3.93).
- **Not a gotobi effect.** Same window, other gotobi days minus non-gotobi days: PRE +1.76, IS -0.45, VAL +2.47 bp.
- **Calendar month.** Not concentrated in coupon or tax months in IS. By month group, IS mid:
  - coupon months Feb/May/Aug/Nov: +4.5;
  - US tax months: +8.9;
  - other months: +5.2.
- **Nominal 15th vs moved-back dates.** IS +7.7 vs +3.8; PRE +7.3 vs +13.0.
- **A USD effect, not a EUR one.** "USD up" excess on the 15th over other days, same window:
  - GBPUSD +4.8 / +4.5 / +7.1 (PRE / IS / VAL);
  - AUDUSD +3.1 / +3.8 / +8.3;
  - NZDUSD +4.0 / +3.5 / +7.7;
  - USDCAD +3.6 / +4.1 / +6.0;
  - USDCHF -2.8 / +2.8 / +2.4;
  - XAU short +2.8 / +5.1 / -0.6.
- **The 6-pair USD basket (EUR, GBP, AUD, NZD, CAD, CHF)**, day-clustered, bp per leg:
  - PRE net +2.74 (t 0.92); without the SNB day +5.04 (t 2.61).
  - IS +3.73 (t 1.89), every year > 0.
  - VAL +7.69 (t 2.08).
  - Day placebo: beaten in 98 % / 96 % / 98 % (PRE / IS / VAL).
  - Power in days: 1.02 on the IS size, 1.59 on the VAL size.
- **Neighbouring-day placebos are not clean.**
  - PAY14 basket: IS -1.31, VAL +8.73 (t 2.36). The 2022-23 USD rally lifts every mid-month European morning.
  - Nominal-15th basket (CD15): PRE +0.52, IS +4.59, VAL +2.22.
- **Selection.** F15 was the best IS cell of a 5-cell family found among 631,915 cells. Its IS t of 3.10 is below
  the set-B null max of 3.79. Its VAL t of 2.33 was seen when it was picked.

## What this says
- Calendar days add nothing over 21 years beyond gotobi and C3's Tokyo morning. Round 13's conclusion now covers
  calendar days as well as business days.
- The only date effect with gotobi-like stability outside JPY pairs is the 15th's European-morning USD strength.
  It sits on a gotobi date but not in Tokyo hours, and the other gotobi days do not show it.
- At about 12 events a year, a single cell has power 1.5-1.7. Even the 6-pair basket on the VAL size has power 1.6.
  So LIVE is out of reach, and a DEMO would need HOLD + demo for any confirmation.

## Directions that need the lead's or the user's decision
1. Whether the 15th's European-morning USD effect may be registered as its own family. If it is registered:
   - as a non-JPY gotobi-day effect it is C3's by this brief;
   - its mechanism is unknown: mid-month US payroll and coupon/tax settlement, or the CPI week, would all fit;
   - VAL was seen, so HOLD would be its only clean test;
   - the expected HOLD t on the VAL size is about 1.7 for F15 and about 1.6 for the basket.
2. Dukascopy M1 2004-15 for GBPUSD, AUDUSD, NZDUSD, USDCAD and XAU (also round 13's request). The H1 PRE cannot see
   15-minute calendar-day effects on those symbols.
3. A US release calendar for 2004-24 (CPI dates) would separate a CPI-week effect from a 15th-of-month effect.

## Scripts and outputs (`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r18/B/`)
- `bcommon.py`: day types CD, CDL and PAY; the wide gotobi set; the JPY gotobi exclusion; labels. It imports
  `r13/M/mcommon.py`.
- `scan1.py`: every cell's PRE stats and the PRE sign-flip null go to `cells_pre.npz` and `perm_pre.npz`; IS/VAL
  go to `cells_isval.npz`. Output: `scan1.out`.
- `show_pre.py`: a PRE-only view. Output: `show_pre.out`.
- `bstep2.py`: carried sets, IS confirmation with the IS sign-flip null, VAL, labels and the matched comparison with
  round 13. Output: `bstep2.out`.
- `bstep3.py`: the step-3 evaluations: eras, years, x1.5, +1 min, excess over other days, both random controls, C3
  correlation and the day-of-month profile. Output: `bstep3.out`.
- `bstep4.py`: F15 by month, by weekday, against other gotobi days, and on the other USD pairs. Output:
  `bstep4.out`.
- `bstep5.py` and `bstep5b.py`: the USD-on-the-15th basket, its placebos, and the PRE numbers without the SNB day.
  Outputs: `bstep5.out` and `bstep5b.out`.
- Peak RAM about 1.4 GB, and each script runs in under 30 s.
