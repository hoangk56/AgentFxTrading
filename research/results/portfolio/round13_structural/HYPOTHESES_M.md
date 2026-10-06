# Stream M hypotheses: stability-first calendar / clock scan (PRE discovery -> IS -> VAL)

Written 2026-10-06 01:28 UTC, before any stream-M number was computed. HOLD (2025-01-01 onwards) is never loaded:
the panel ends 2024-12-31 and Dukascopy files end 2015-12-31.

## M0. Mechanism class and why it may escape the decay of rounds 3-12
- Mechanism: flows tied to fixed institutional calendars and clocks (local business hours of Tokyo, London, New York,
  Sydney; month start / end and quarter end; national holidays), the class gotobi belongs to. Sources: Ranaldo 2009
  and Breedon & Ranaldo 2013 (home-hours depreciation, a clock flow), Evans 2018 / Melvin & Prins 2015 (month-end
  fixes), round 3's calendar x window scan (IS/VAL only, 90k cells).
- Why it may escape the decay: the cell is chosen on 2004-2015 (PRE), an era no earlier selection used, and must then
  keep its sign and size in 2016-21 (IS) and 2022-24 (VAL). A cell that is the same size over 21 years is more likely
  structural than one picked on IS. The cost: round 3 says hour-scale calendar flows are 0.5-3 bp; a 21-year effect
  can be small, so every survivor is reported with its break-even cost.
- Caveats written now: (1) the hour-of-day literature (Ranaldo 2009) used 1993-2005 data, so PRE is not out of sample
  for that mechanism; (2) round 3 printed HOLD hour-of-day means for XAUUSD and AUDUSD, so their "ALL days" cells are
  information only, never candidates, and are kept in K and in the null.

## M1 (the scan). Exact design
**Symbols.** M1 group (PRE = Dukascopy M1 bid): USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD. H1 group (PRE = Dukascopy H1
bid): AUDJPY, AUDUSD, GBPUSD, NZDUSD, USDCAD, XAUUSD (the other five H1 symbols are the M1 group's, not repeated).
IS/VAL: shared panel mid (IC M1), 2016-01..2021-12 / 2022-01..2024-12.

**Clocks.** TOK (Asia/Tokyo, UTC+9 fixed), LON (Europe/London), NY (America/New_York), SYD (Australia/Sydney), DST from
zoneinfo, the local UTC offset taken at local noon of the date. A window is "local start time h:m on local date D".

**Windows.** M1 group: start every 15 min of the local day (96), length 15, 30, 60, 120, 240 min (480 windows per clock).
H1 group: start every hour (24), length 60, 120, 180, 240 min (96 per clock). Return r = 1e4 ln(P_end / P_start), P =
the quote at the boundary minute (close of the minute / hour bar ending there): Dukascopy bid in PRE, panel mid in
IS/VAL.

**Exclusions (all fixed now).**
- JPY pairs (USDJPY EURJPY GBPJPY AUDJPY): every window overlapping 23:00-02:00 UTC on any day (C3's Tokyo-fix area).
- All symbols: every window intersecting 16:45-18:15 New York time (IC's post-rollover wide-spread hour, Dukascopy's
  rollover bid dip, swap).
- Local dates Dec 24 - Jan 1 (thin holiday markets); Saturdays and Sundays (local date) never form a day.
- An event is dropped if either endpoint has no real quote in the 10 minutes before it (M1 / panel) or the hour bar
  ending at it is missing (H1 PRE). Cells with < 30 PRE events are dropped.
- No day type is defined by gotobi days.

**Day types** (local date of the clock; weekday = Mon-Fri, holidays not removed from the business-day count, as in
round 3): ALL; MON..FRI; BD+1..BD+5 (k-th weekday of the month); BD-1..BD-5 (k-th last weekday, -1 = last); QE-1..QE-3
(k-th last weekday of Mar/Jun/Sep/Dec); for C in USD, GBP, JPY (shared calendars holidays.json): HOL_C (a weekday that
is a C holiday), PRE_C (last weekday before a C holiday block that is not itself a C holiday), POST_C (first weekday
after the block). 28 day types.

**Cell count.** M1 group 5 x 4 clocks x 28 x 480 = 268,800 nominal; H1 group 6 x 4 x 28 x 96 = 64,512 nominal (the
exclusions remove some; the exact K is reported).

**Discovery (PRE only).** t_PRE = mean / (sd / sqrt n) over the cell's events (one per date, so day-clustered within a
symbol). The side of each cell is fixed now as sign(mean_PRE); IS and VAL are judged on that side only.
- Chance benchmark: sign-flip permutation, one random sign per local date shared by all symbols, clocks and windows,
  200 permutations; distribution of max |t_PRE| over all cells (and per group).
- Set A (carried): |t_PRE| >= the 95th percentile of the permutation max |t| (family-wise 5 %).
- Set B (carried, looser): the top 500 cells by |t_PRE|.

**Confirmation (IS) and check (VAL).** Same side; mean mid bp, t, net bp. A cell "confirms" if t_IS >= 2.0 on the PRE
side. Chance benchmark for this step: the same sign-flip permutation on IS dates (200), giving the null count of
confirmations and the null max t_IS within each carried set. Then VAL: same side, mean and t.
- Stability numbers for every survivor: IS/PRE and VAL/IS ratios of the mean, means by year, PRE sub-periods
  2004-07 / 2008-11 / 2012-15. "Stable" = same sign in all three eras and both ratios >= 0.5; a VAL/IS < 0.5 is called
  decaying.

**Costs.** IS/VAL: half the panel spread at the entry minute + half at the exit minute (bp of mid) + 0.6 bp
commission. PRE: IC's 2016-17 mean spread by minute of day + 0.6 bp, as round 7, except that the profile is indexed by
New York clock minute (round 12 pitfall: IC's wide hour moves with New York DST). Variants: spread x1.5; both fills one
minute late. Break-even cost = the PRE-side mid mean.

**Bars.** As the brief (LIVE / DEMO), plus for a survivor: day-clustered t pooled over symbols if several symbols form
one rule, random-entry control (same window length on random other weekdays of the same day-type mix and same
session, >= 200 seeds), power = per-trade net Sharpe x sqrt(expected HOLD trades) on the IS and on the VAL size.
Nothing is pre-registered unless it meets DEMO or LIVE on IS/VAL with the side fixed from PRE.

## Additions after the PRE scan, before any IS or VAL number was read (2026-10-06 01:31 UTC)
- PRE scan done (K = 270,086 cells with >= 30 PRE events; permutation max |t_PRE|: median 4.71, 95 % 5.46). Only PRE
  numbers have been printed. Set A = |t_PRE| >= 5.46; set B = top 500 by |t_PRE|, as declared.
- Side effect of the Dec 24 - Jan 1 exclusion, noted now: December's last weekdays are excluded, so BD-1..BD-5 lose
  December and QE-k has 3 quarter-ends a year.
- Labelling fixed now (post-hoc w.r.t. PRE, before IS): on the non-JPY pairs, a cell whose window overlaps 23:00-02:00
  UTC is labelled "Tokyo-fix adjacent" (C3's mechanism on USD pairs: the top PRE cells include EURUSD rising
  01:00-03:00 UTC). Such cells stay in the scan and are reported, but are not a new mechanism; any survivor there gets
  its C3 correlation and is not proposed as a new algorithm. XAUUSD and AUDUSD "ALL" cells stay information only.
- The top PRE cells look like the ECB-fix and home-hours effects of rounds 3-10 (EURUSD falling into 13:15 London,
  USDCHF falling 13:15-13:30 London) and gold's Asian-afternoon rise; they are judged by the declared protocol, not
  re-selected.

## Step 2 result in one line and the step-3 plan (2026-10-06 01:32 UTC, before any step-3 number)
- Step 2 (IS confirmation of the PRE-carried sets) printed IS and VAL together for the confirmed cells, so VAL was in
  view when the step-3 cells below were picked (disclosed). Picking used the IS columns only: IS t on the PRE side,
  and IS net > 0.
- Step-3 cells (side from PRE, window from the IS-best confirmed cell of each family; family = same symbol, same side,
  overlapping UTC window):
  - E1 EURUSD short 11:00-13:00 London, every weekday (best IS t of all 500 carried cells). Mechanism: home-hours
    depreciation of the euro in the European midday / USD demand into the 14:15 CET ECB reference rate (Ranaldo 2009;
    Breedon & Ranaldo 2013; Krohn, Mueller & Whelan 2024). Clock alternatives reported, not chosen: NY 06:00-08:00,
    TOK 19:00-21:00 (= 10:00-12:00 UTC).
  - E2 USDCHF long 19:00-21:00 Tokyo (10:00-12:00 UTC), the only USDCHF European-midday cell with IS net > 0; same
    mechanism for CHF.
  - E3 basket (post-hoc combination, marked as such): E1 + USDCHF long 11:00-13:00 London on the same days, one bot,
    day-clustered.
  - G1 GBPJPY long 17:30-21:30 London (US afternoon), best IS t of its family. Mechanism unknown before the data
    (yen weakening into the New York afternoon; risk-on / carry rebuilding); flagged as data-first.
  - Not candidates: the Tokyo-fix-adjacent USD cells (C3's mechanism), cells with IS net <= 0, and cells whose VAL/IS
    < 0.5 (decaying), which are reported in the family table only.
- For each: per-era mid and net (actual spreads), years, PRE sub-periods, weekday split, spread x1.5, +1 minute,
  2.5 % winsorised mean, random-entry control (same days, same length, same side, start drawn uniformly on the
  15-minute grid of the same session: 07:00-16:00 London starts for E1-E3, 12:00-16:45 New York ends for G1; 200 seeds;
  the real cell is not excluded from the draw), power on the IS and on the VAL size with 1.75 years of HOLD trades,
  and the daily / monthly P&L correlation with C3 on IS + VAL.

## Step 3 outcome and step 4 (2026-10-06 01:34 UTC, before any step-4 number)
- Step 3: E1 meets every DEMO number and every LIVE number except power (IS 1.78, VAL 1.88 < 3). E2, E3, G1 fail.
  Per the brief the E1 family (EUR / European-midday clock flow) STOPS here: no further variants are searched for it;
  PREREG_DRAFT_M_eurusd_midday.md is written.
- Step 4 (reporting only, nothing below can change E1's rule):
  - plateau: EURUSD London-clock windows with start 10:00-12:00 (15-min grid) and length 60-240, all three eras;
  - the same 11:00-13:00 London window on all 11 symbols (EUR vs USD or a broad USD move?);
  - E1 by day type (month-end, quarter-end, holidays, weekday), information only;
  - an automatic family table of the 139 IS-confirmed set-B cells (same symbol and side, same day type, overlapping
    UTC windows at standard-time offsets), with each family's best IS cell, its eras, net and ratios;
  - XAUUSD long 11:00-15:00 Tokyo on the weekday before a UK holiday (set-B IS-confirmed, net > 0 in IS and VAL,
    VAL/IS 0.22): full numbers, judged as decaying unless VAL says otherwise.

## Post-hoc reporting additions (2026-10-06 01:37 UTC, written after the step-4 numbers and after the two decompositions below were run; not a selection)
- The E1 plateau is not smooth (neighbouring 2-h windows are 0.6-0.9 bp in IS), so two decompositions were added,
  reporting only: (a) EURUSD 15-minute slots 09:00-15:00 London by era; (b) the slots that dominate E1 (11:45-12:00
  and 12:45-13:00 London) by year, and E1 minus those slots by era. They cannot change E1's rule; they go into the
  draft's caveats.
