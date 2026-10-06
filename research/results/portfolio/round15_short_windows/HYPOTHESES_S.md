# Round 15, stream S: hypotheses (written before their numbers)

Times are UTC (`date -u`). HOLD (2025-01-01 onwards) is never loaded: Dukascopy M1 ends 2015-12-31, the shared panel
ends 2024-12-31, the C3 trade list is read with rows on or after 2025-01-01 skipped, and no IC M1 cache or tick file
is read past 2024-12-31.

## S0. Data alignment check (02:04 UTC, before any scan number)
Dukascopy M1 (PRE) and the IC panel (IS/VAL) are both used as "price at boundary m = close of the bar labelled
m-1" (bar-START labels, as round 13 M). Before scanning, verify:
1. IC panel labels against IC ticks (AUDUSD, a few 2016-2024 days): which label convention reproduces the panel close.
2. Dukascopy vs IC on the 2016-17 overlap (USDJPY, EURJPY, GBPJPY in `research/data/duka/m1_1617`): lag of the
   maximum 1-minute return correlation (expect 0).
3. A known effect in both sources: (a) the US 08:30 ET release minute (NFP Fridays): the bar with the largest mean
   |1-minute return| must carry the same label in PRE (Dukascopy) and IS (IC); (b) the ECB V in EURUSD around
   13:00-13:15 London, by minute, PRE vs IS (round 13 M said the V moved 15 minutes at the 2015/16 boundary: check
   whether that is a labelling artefact; on the 2016-17 overlap compare EURJPY's V in Dukascopy vs IC, same days).
The result decides the grids; it is reported in STREAM_S.md.

## Common design (02:04 UTC)
- Symbols: EURUSD, USDCHF (all hours); USDJPY, EURJPY, GBPJPY with every window overlapping 23:00-02:00 UTC removed
  (C3's Tokyo fix). No gotobi day types. Every window touching 16:45-18:15 New York removed. 24 Dec - 1 Jan removed.
- Anchors (declared benchmark minutes, DST-aware local clocks):

| id | anchor | clock | mechanism (source) |
|---|---|---|---|
| ECB | 14:15 CET ECB reference rate (concertation 14:10) | Europe/Berlin | pre-fix euro selling, post-fix rebound (Ranaldo 2009; Krohn, Mueller & Whelan 2024) |
| WMR | 16:00 London WM/Reuters fix (5-minute window from Feb 2015) | Europe/London | fixing orders concentrated in the fix window; pre-fix drift and post-fix reversal (Evans 2018; Melvin & Prins 2015) |
| NY10 | 10:00 New York option cut, also 10:00 ET data minute | America/New_York | option expiry hedging and pinning; data drift |
| TOK15 | 15:00 Tokyo option cut | Asia/Tokyo | option expiry hedging |
| LON08 | London 08:00 open = Frankfurt 09:00 CET (same UTC minute all year since UK/EU DST are synchronised; counted once) | Europe/London | liquidity onset, European order flow |
| NY0830 | 08:30 ET US data minute (all days) | America/New_York | release / pre-release positioning |
| CME14 | 14:00 ET | America/New_York | CME FX futures close / settlement flows |
| CME15 | 15:00 ET | America/New_York | CME FX futures close / settlement flows |

- Cells: every window of length 1, 2, 3, 5, 10 minutes whose start is within -30..+30 minutes of an anchor (local
  clock), deduplicated per clock (NY 14:30 starts appear once). Day types: ALL weekdays, MON..FRI, ME (last weekday
  of the month). Expected K ~ 5 symbols x 7 day types x ~487 starts x 5 lengths ~ 85k (minus JPY exclusions).
- Return: log price change between the window boundaries; PRE = Dukascopy bid, IS/VAL = panel mid. One trade per day
  per cell, so a plain t over days is day-clustered.
- Costs: IS/VAL: half the actual panel spread at the entry boundary + half at the exit boundary + 0.6 bp. PRE: IC
  2016-17 mean spread by New York minute of day + 0.6 bp (round 7 / round 13 convention). Stale quotes (> 10 min) drop
  the day.
- Side: the sign of the PRE mean, fixed before any IS number is computed for that cell.

## Steps and pre-declared thresholds (02:04 UTC)
1. Discovery (PRE only): |t_PRE| for every cell. Chance: sign-flip permutation, one sign per PRE date shared by all
   cells of the stream, 200 draws -> distribution of max |t|. Set A = cells with |t_PRE| >= the null's 95th
   percentile. Set B = top 300 cells by |t_PRE|.
2. IS confirmation on the PRE side: t_IS >= 2.0. Chance: sign-flip per IS date (200 draws, shared) for the count of
   confirmations in A and in B and for the max side-t.
3. VAL check of the confirmed cells: t_VAL on the PRE side, VAL/IS ratio, net IS and VAL.
4. Candidates = confirmed cells with net IS > 0 and net VAL > 0, grouped into families (symbol x anchor x side, nearby
   starts); per family the best cell by IS net t (VAL shown, not used for choice). Full evaluation: by year, x1.5
   spread, both fills +1 minute (no FX ticks for these symbols: +10 s / +30 s not possible, stated), random-entry
   control (same days, same side and length, entry minute drawn uniformly from the same clock's 07:00-17:00 local
   window, 200 seeds), C3 correlation (IS+VAL daily/monthly), per-trade net Sharpe, power on the IS and the VAL size
   (Sharpe x sqrt(expected HOLD trades = trades per year x 1.73)), overlap with E1 (11:00-13:00 London) / the ECB slot.
5. Bars as round 13 (LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years net > 0, beats >= 95 % random, power >= 3;
   DEMO: IS t >= 2.0, VAL net > 0, beats >= 90 %). A family that meets one gets PREREG_DRAFT_S_<name>.md and stops.

## Hypotheses (02:04 UTC)
- **S1 (ECB)**: EUR pairs (EURUSD, EURJPY; USDCHF as the mirror) have a concentrated move in 1-10-minute windows
  around 14:10-14:15 CET; the 15-minute ECB effect (+0.73 / +0.85 bp, round 10/12) may sit in a few minutes where
  the per-trade Sharpe is higher. Overlap: windows starting 13:45-14:00 CET (12:45-13:00 London) are inside E1's
  last 15 minutes / the ECB pre-fix slot.
- **S2 (WMR)**: concentrated pre-fix / in-fix / post-fix moves around 16:00 London, all days and month-end (the
  month-end WM/R USD effect of rounds 3-4 decayed at 15-60 minutes; a 1-5-minute slice may differ).
- **S3 (option cuts NY10 / TOK15)**: pinning / hedging moves in the minutes before and after the cut.
- **S4 (opens LON08)**: minutes after the London / Frankfurt open.
- **S5 (US data minutes NY0830 / NY10 on all days)**: average drift into or after the release minute (no surprise
  sign used; days without a release dilute it).
- **S6 (CME14 / CME15)**: futures close / settlement flows.
- **S-control**: EURUSD, ALL weekdays, every 1, 2, 3, 5-minute window of the day on the London clock (starts every
  minute, rollover hour removed), PRE discovery with its own sign-flip null; question: are |t_PRE| at the benchmark
  minutes larger than elsewhere? Control cells above its own null 95th percentile are confirmed on IS/VAL the same
  way and reported as a separate family.

## S0 result (02:05 UTC; data check, not a hypothesis)
Both sources use bar-START labels (bar L = [L, L+1)): the panel close of label L equals the last IC tick in [L, L+1)
on 4/4 AUDUSD days (100 %), against 3-7 % for [L-1, L); Dukascopy 2016-17 vs IC 1-minute returns correlate 0.99 at
lag 0 and -0.02 at lags +-1; the NFP |return| peaks in bar 08:30 ET in PRE and IS. The ECB V moved in the market,
not in the data: Dukascopy and IC agree on EURJPY 2016-17 (drop 12:55-13:00 London in both), while Dukascopy
2004-15 has its big drop at 13:13-13:14 London. Grids as declared (no shift). Details in STREAM_S.md.

## Step-2 outcome and post hoc additions (02:07 UTC, after the step-2 numbers, before the step-3 numbers)
Step 2 (declared path): set A 25 / 409 IS confirmations against a sign-flip null 95th percentile of 30, set B 20 / 300
against 27: not beyond chance; no confirmed cell is net > 0 in both IS and VAL. Control (EURUSD all windows): 58 / 361
against 15. Post hoc (marked as such in STREAM_S.md, information only, cannot produce a registrable rule):
- (a) best PRE cell per anchor x symbol with its IS / VAL; (b) best IS net t per anchor x symbol among cells with
  |t_PRE| >= 2 (loose carry, side still from PRE); (c) every cell with |t_PRE| >= 2 and net > 0 in IS and VAL;
  (d) hindsight two-sided upper bound per anchor against the LIVE line (cost + 0.144 sd); (e) month-end WM/R cells;
  (f) shrinkage by anchor; (g) share of cells net > 0 by length.
- Full evaluation (by year, x1.5, +1 minute, random entries, C3 correlation, E1 overlap) of the two cells closest to
  the bar in step 2: EURUSD short 12:55-13:00 London every weekday, EURUSD short 12:57-13:00 London Fridays.

## Post hoc evaluation of the step-3 (b)/(c) leads (02:08 UTC, after step-3 numbers; post hoc, marked)
Two leads came out of the loose carry (selected on IS net t, side from PRE): EURUSD short 12:50-13:00 / 12:55-13:00
London on Fridays (the ECB pre-fix slot, inside E1) and GBPJPY long 10:28-10:31 New York on the last weekday of the
month. Evaluated with the declared step-4 battery (by year, x1.5, +1 minute, random-entry control, C3 correlation,
E1 overlap) plus: weekday split of the same window in PRE / IS / VAL; for GBPJPY the same window on the k-th-last
weekdays (k = 2..5) as placebos and the neighbouring starts; a selection-adjusted chance level = the IS sign-flip null
of the max side-t over the whole loose pool (all cells with |t_PRE| >= 2).

## Extra checks of the two leads (02:10 UTC, after step-4 numbers; post hoc)
- EURUSD Friday ECB pre-slot: does Friday also enlarge the post-fix leg (long 13:00-13:15 London) and the whole V,
  as a bigger Friday fix flow would? Robustness: winsorised mean, median, share > 0, Friday month-ends and
  holiday-adjacent Fridays removed, start/end plateau (12:45..12:56 starts x 13:00..13:02 ends).
- GBPJPY month-end 10:28-10:31 NY: by quarter-end vs other month-ends, by calendar month, winsorised, and the window
  on the London clock (15:28-15:31) vs New York clock.

## Post hoc information line (02:10 UTC, after step-5 numbers)
Friday enlarges both legs of the IS/VAL ECB V (pre-leg short 12:50-13:00, post-leg long 13:00-13:15 London). Compute
the Friday two-leg trade (short 12:50 -> buy 13:00 -> long to 13:15; costs = two round trips) and the all-days
version: net, t, Sharpe, power, x1.5, +1 minute, by year. Information only: the post-leg side contradicts PRE (where
13:00-13:15 fell, the V sat at 13:13-13:15), and Friday was chosen after IS and VAL were seen.
