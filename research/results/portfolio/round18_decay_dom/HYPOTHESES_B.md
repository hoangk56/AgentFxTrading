# Stream B hypotheses: calendar day-of-month x clock windows (PRE discovery -> IS -> VAL)

Written 2026-10-06 02:58 UTC (`date -u` 02:57:48), before any stream-B number was computed. HOLD (2025-01-01 onwards)
is never loaded: the panel ends 2024-12-31, Dukascopy files end 2015-12-31, era dates stop at 2024-12-23 (24 Dec -
1 Jan excluded).

## B0. Mechanism and why it may escape decay
- Mechanism: payments fixed on calendar days, not business days: paydays (25th in Japan, 15th/last in the US, the
  "n-th of the month" in many corporate payment terms), pension / social-security dates (e.g. US Social Security on
  the 3rd and on 2nd-4th Wednesdays; Japanese pensions on the 15th of even months), rent and coupon dates, invoice
  terms of "end of month + n days". The usual convention moves a non-business day to the previous business day
  ("preceding"), which is what gotobi does. If any such practice produces an FX conversion executed at a fixed clock
  time, it would be structural like gotobi and would not decay when traded.
- Gap: round 13 M scanned business-day-of-month (k-th weekday from start/end), month/quarter ends and holidays, not
  calendar days. Round 3 scanned IS/VAL only. Calendar days 1-31 are the last unscanned calendar dimension on the
  existing data.
- Expected size, written now: round 13 M found calendar day types add nothing beyond clocks over 21 years; a
  calendar-day cell has ~100 PRE events (one a month, weekdays only), so only effects of several bp (t >= ~5.5 needs
  ~8 bp at sd 15 bp) can pass PRE discovery family-wise. At ~8-9 events a year, a single cell has ~15 HOLD trades:
  LIVE needs a per-trade net Sharpe >= 0.77, which is not realistic, so a single cell can at best meet DEMO; LIVE
  would need a pooled rule (several symbols / days with one mechanism).
- Caveat written now: CD-d and PAY-d share most dates (PAY-d = CD-d on business days plus the Friday/pre-holiday shift),
  and every CD cell's window also contains the every-day clock effect of round 13 (e.g. E1). Discovery is on raw
  returns (comparable with round 13); for survivors the excess over the same window on all other days is reported and
  a day-placebo control is required (below).

## B1. The scan (exact design, fixed now)
**Symbols / data.** As round 13 M: M1 group (PRE = Dukascopy M1 bid) EURUSD, USDCHF, USDJPY, EURJPY, GBPJPY; H1 group
(PRE = Dukascopy H1 bid) AUDJPY, AUDUSD, GBPUSD, NZDUSD, USDCAD, XAUUSD. IS 2016-21 / VAL 2022-24: shared panel mid.
Code reused from round 13 M (`r13/M/mcommon.py`: grids, clocks, window matrices, costs).

**Clocks.** TOK, LON, NY, SYD (zoneinfo, offset at local noon). A window = local start h:m on local date D.

**Windows.** M1 group: starts every 15 min (96), lengths 15, 30, 60, 120, 240 min. H1 group: hourly starts (24),
lengths 60, 120, 180, 240 min. Return = 1e4 ln(P_end / P_start).

**Day types (72), on the clock's local date; weekends never form a day.**
- CD1..CD31: the local date's day of month is d (weekday; holidays not removed, as round 13).
- CDL1..CDL10: the n-th last calendar day of the month (CDL1 = last day), weekday.
- PAY1..PAY31: "calendar day d, or the previous business day if d is not one" (preceding convention). Business day =
  weekday that is not a holiday of the clock's country (TOK: JPY, LON: GBP, NY: USD, SYD: AUD; holidays.json). If d
  exceeds the month's length, d = the month's last day (so PAY29-31 coincide in February; PAY31 = last day adjusted).
- No "every day" type: that is round 13's.

**Exclusions (fixed now).**
- C3: on JPY pairs (USDJPY, EURJPY, GBPJPY, AUDJPY), every window overlapping 23:00-02:00 UTC on any day (round 13
  rule), and every event whose window starts or ends on a Tokyo-local gotobi date. Gotobi dates (wide, to be
  conservative): nominal 5, 10, 15, 20, 25, 30 and the last day, each moved to the previous weekday, and also to the
  previous weekday that is not a JP holiday (both dates are excluded when they differ).
- As round 13: windows touching 16:45-18:15 New York; local dates 24 Dec - 1 Jan; stale endpoints (> 10 min without a
  quote; missing H1 bar in PRE). Cells with < 30 PRE events dropped.

**Information-only labels (cells stay in K and in the nulls, never candidates).**
- "G-info": a non-JPY cell with >= 50 % of its PRE events on a Tokyo gotobi date (start or end of the window). Reported
  separately as C3-related information.
- "Tokyo-fix adjacent": a non-JPY cell overlapping 23:00-02:00 UTC (round 13's label; C3's mechanism on USD pairs).
- XAUUSD and AUDUSD cells stay as round 13 decided (their HOLD hour-of-day means were printed in round 3, but that was
  for every-day cells; calendar-day cells are allowed as candidates).

**Discovery (PRE only).** t_PRE = mean / (sd / sqrt n), one event per local date. Side of each cell = sign(mean_PRE),
fixed before any IS number. Chance: sign-flip permutation, one sign per date (era-date index) shared by all symbols,
clocks, types and windows, 200 draws, max |t_PRE| overall and per group. Set A = |t_PRE| >= the null's 95th
percentile; set B = top 500 by |t_PRE|. IS and VAL statistics are written by the scan into a separate file that is
opened only after the PRE result is logged here.

**Confirmation (IS) and check (VAL).** Same side. Confirm = t_IS >= 2.0. Chance: IS sign-flip permutation (200) over the
carried cells (null count of confirmations, null max t_IS). VAL: same side, count of t_VAL >= 1.5 among confirmed vs
the ~6.7 % expected. Shrinkage: mean IS/PRE and VAL/IS on the PRE side for sets A and B and the confirmed cells.
Stable = same sign in all eras and both ratios >= 0.5.

**Costs.** IS/VAL: half the panel spread at entry + exit minute + 0.6 bp. PRE: IC 2016-17 mean spread by New York
minute + 0.6 bp (round 13). Variants: spread x1.5; both fills +1 minute.

**Survivors (step 3).** Candidates = set-A or set-B cells confirmed in IS with net IS > 0, not information-only; one per
family (same symbol, side and day type, overlapping UTC windows), the best IS t. For each: per-era mid / net / t,
by year, PRE sub-periods, x1.5, +1 min, 2.5 % winsorised mean, the excess over the same window on all other weekdays
(per era), the day-of-month profile of the same window (neighbouring days, CD vs PAY versions, reporting only),
random-entry controls (200 seeds): (a) the brief's: same dates, same length and side, start drawn on the window grid
within +- 3 h of the real start (excluded windows skipped); (b) day placebo: the same window on the same number of
random other weekdays of the era with the same weekday mix. A cell is called a calendar-day effect only if it beats
>= 90 % of (b) as well as the bar's share of (a). Power = per-trade net Sharpe x sqrt(events a year x 1.75) on the IS
and the VAL size; daily / monthly correlation with C3 (IS + VAL).
Bars: the brief's LIVE / DEMO. A pooled rule across symbols or days (one mechanism) may be formed from IS only and is
marked post hoc.

**Comparison with round 13 M.** Matched statistics for round 13's business-day types (BD+1..5, BD-1..5) from its
cells.npz and for this scan's CD, CDL and PAY classes: top-500 by |t_PRE| per class, IS same-sign rate, IS
confirmations (chance ~2.3 % = 11.5 of 500), mean IS/PRE and VAL/IS. Hypothesis written now: calendar-day cells are no
more stable than business-day cells (IS/PRE about 0.2 or lower).

## After the PRE scan, before any IS or VAL number was read (2026-10-06 03:00 UTC)
- PRE scan done: K = 631,915 cells with >= 30 PRE events (500,937 M1 group, 130,978 H1 group). Only PRE numbers
  have been printed (`show_pre.out`); `cells_isval.npz` has not been opened.
- PRE max |t| 5.73 (USDJPY short 03:15-04:15 London on CD23) against the shared sign-flip null: median 4.86, 95 %
  5.55, 99 % 5.74 (M1 group 95 % 5.45, H1 group 5.03). Set A = 1 cell (2 with group thresholds: + XAUUSD long
  03:00-07:00 London on PAY21, t 5.04). The PRE discovery is at the edge of chance (round 13's every-day clock cells
  gave 120 above its threshold). Set B = top 500, |t_PRE| >= 3.72, as declared.
- Labelling fixed now, from the PRE list and the calendar only: many top cells are macro-release days at a fixed
  clock time (CD16 / PAY15-16 at 08:15-08:45 New York contain the US CPI release around the 15th at 08:30 ET; CD22
  USDCAD 07:00-09:00 New York contains Canadian CPI / retail sales). A news response has no fixed sign from a payment
  mechanism, so a survivor whose window contains 08:30 New York on days 10-17 or 08:30 New York / 07:00 London on
  other days with a monthly release is labelled "release-time" and is reported but not proposed as a calendar-payment
  candidate unless its sign has a written mechanism. Set B has 121 G-info and 128 Tokyo-fix-adjacent cells
  (information only, kept in the counts and nulls).

## Step 2 in one line and the step-3 plan (2026-10-06 03:01 UTC, before any step-3 number)
- Step 2 printed IS and VAL together for the confirmed cells (as round 13 did), so VAL was in view when the cells
  below were picked (disclosed). Picking uses the declared rule only (IS-confirmed, IS net > 0, best IS t per family).
- Set A (1 cell) and A' (2 cells): 0 confirmed. Set B: 19 / 500 confirmed in IS (null median 11, 95 % 22, p 0.17), i.e.
  at chance. Of the 19: 4 eligible (null median 7 for the eligible subset), 11 G-info, 4 Tokyo-fix adjacent.
- Step-3 cells, eligible (side from PRE): EURUSD short 11:15-13:15 London on PAY22; NZDUSD long 11:00-13:00 Tokyo on
  CD18; EURUSD long 11:30-12:30 Tokyo on CD27. (USDCHF short 13:15-13:30 London on PAY6 has IS net < 0: reported in the
  table only.) No mechanism was written for these days before the data: they are data-first and judged on the bar,
  the controls and VAL.
- Information-only evaluations (C3-related or Tokyo-fix adjacent, never candidates), same statistics:
  - F15: EURUSD short 04:00-08:00 New York on PAY15 (best IS t of its 5-cell family, all European-morning windows on the
    15th). Added for interpretation: the same window on each other gotobi day (PAY5, 10, 20, 25, 30, 31), on all
    gotobi days pooled, and on the 15th by month (to tell a gotobi effect from a mid-month effect: the 15th is also a
    US/semi-monthly payday and, in Feb/May/Aug/Nov, a Treasury coupon settlement date).
  - USDCHF long 08:15-12:15 Sydney on CDL8 (Tokyo morning of the 23rd/24th) and USDCHF long 06:30-08:30 London on PAY5.
- Comparison (step 2 printed): the matched top-500 classes are reported as computed; the every-day clock class of round
  13 is the only class with a PRE-IS t correlation well above 0 (0.36 vs 0.06-0.08 for CD, CDL, PAY and round 13's BD).

## Step 3 in one line and step 4 (2026-10-06 03:02 UTC, before any step-4 number; reporting only)
- Eligible cells B1-B3 all fail VAL (net -1.41, -3.50, +0.01 bp): no candidate, no PREREG draft from the scan.
- Information-only F15 (EURUSD short 04:00-08:00 New York on PAY15) has DEMO-like numbers (net IS +5.88 t 2.80, VAL
  +10.83 t 2.20, controls >= 93 %), but it is a non-JPY gotobi-day cell: by the brief, information only, not a
  candidate, no draft. Step 4 describes it, nothing in it can turn it into a candidate:
  - the 15th by calendar month (coupon months Feb/May/Aug/Nov, US tax months Mar/Apr/Jun/Sep/Dec, others), by weekday,
    nominal 15th vs moved-back dates;
  - the same window on the other gotobi days pooled (PAY5, 10, 20, 25, 30, 31) vs non-gotobi days;
  - the same window on the 15th for the other USD pairs (USDCHF, USDJPY excluded by rule, GBPUSD, AUDUSD, NZDUSD,
    USDCAD, XAUUSD; sides = "USD up"), to tell a EUR effect from a USD effect;
  - F15 minus its every-day part: the window's mean on other weekdays is subtracted per era (already printed as
    "excess").

## Step 4 in one line and step 5 (2026-10-06 03:03 UTC, post hoc, reporting only, before any step-5 number)
- Step 4: F15 is not a general gotobi-day effect (other gotobi days minus non-gotobi days, same window: PRE +1.76,
  IS -0.45, VAL +2.47 bp) and it is broad USD strength, not EUR: the same window on the 15th gives "USD up" excess
  over other days of +3 to +8 bp in IS and VAL on GBPUSD, AUDUSD, NZDUSD, USDCAD and USDCHF (USDCHF wrong sign in
  PRE; XAU wrong sign in VAL).
- Step 5 (post hoc, VAL already seen; it describes the information-only finding for the lead and cannot create a
  candidate in this stream): a "USD on the 15th" basket, long USD 04:00-08:00 New York on PAY15 on EURUSD, GBPUSD,
  AUDUSD, NZDUSD, USDCAD, USDCHF (no JPY pairs, no XAU), one equal-weight leg each, day-clustered net (bp per leg),
  per era and year, x1.5, +1 min (M1 legs only in PRE), day-placebo control (same window on random other weekdays
  with the same weekday mix), power on IS and VAL size in days, C3 correlation. Also the same basket on the nominal
  15th only, and on PAY14 / PAY16 (neighbours) as a placebo.
