# Stream R hypotheses: mechanism-derived conditions that double the stable clock effects

Written 2026-10-06 01:49-01:52 UTC (`date -u`), before any stream-R number was computed. HOLD
(2025-01-01 onwards) is never loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, and every date range
stops at 2024-12-31.

## R0. What was already seen (disclosed, so these splits are NOT clean tests here)
Read before writing this file: STREAM_M.md, stream M's step2/3/4/4b/4c outputs, round 10 STREAM_E, round 12 STREAM_L.
They show for E1 (EURUSD short 11:00-13:00 London):
- by weekday (PRE / IS / VAL), by business day of month (BD+1..5, BD-1..5), quarter-end QE-1..3, and on / before /
  after USD, GBP and JPY holidays;
- by 15-minute slot (PRE edge in 11:45-12:00, IS/VAL edge in 12:45-13:00 London), and the plateau;
- the same window on all 11 symbols (USDJPY long +1.08 / +0.88 / +0.95, USDCHF long +1.27 / +1.61 / +0.59);
- E2 (USDCHF long 10:00-12:00 UTC) and G1 (GBPJPY long 17:30-21:30 London) by weekday and year.
So weekday, month-end / quarter-end and USD / GBP / JPY holiday conditions are reported as information only and are
not counted as tests. Round 12 L3 printed the ECB fix window (14:00-14:15 CET) at month-end; round 10 E1 printed it
by 20-day RV and pre-window activity terciles.

## R1. Arithmetic (target written now)
- LIVE power = per-trade net Sharpe x sqrt(1.73 x trades per year) >= 3. E1 (all weekdays, ~250/yr) has net Sharpe
  0.084 IS / 0.089 VAL, power 1.8 / 1.9.
- A selector keeping a fraction f of days needs per-trade net Sharpe >= 3 / sqrt(1.73 x 250 f):
  f = 1: 0.144; f = 0.67: 0.176; f = 0.5: 0.204; f = 0.33: 0.250. With E1's sd (~14 bp) that is a net mean of
  about 2.0 / 2.5 / 2.9 / 3.5 bp, i.e. a mid of ~2.6 / 3.1 / 3.5 / 4.1 bp against E1's 1.8-2.0 (x1.4 / x1.6 / x1.8 /
  x2.1) if the sd of the selected days is unchanged. Exclusion filters (f ~ 0.95) can only add ~10-20 % to the
  Sharpe (by dropping high-variance news days), so they cannot reach LIVE alone; they are tested because they
  identify the mechanism and could combine with a selector.

## R2. Objects (fixed from stream M; side and window not re-optimised)
| id | rule | mechanism | why here |
|---|---|---|---|
| O1 | EURUSD short 11:00-13:00 London (E1) | euro home-hours weakness (Ranaldo 2009; Breedon & Ranaldo 2013) into the pre-ECB-fix USD bid (Krohn, Mueller & Whelan 2024) | DEMO, net > 0 every era |
| O2 | EURUSD short 12:45-13:00 London (ECB pre-leg slot) | pre-fix USD demand (KMW) | the IS/VAL core of E1 (PRE was in 11:45-12:00: disclosed) |
| O3 | USDJPY long 11:00-13:00 London | same window, USD up vs JPY over European midday (stream M: break-even 0.88 / 0.95 vs cost 0.77 / 0.73) | stable, at cost |
| O4 | USDCHF long 10:00-12:00 UTC (E2) | CHF home-hours weakness (Ranaldo: CHF is a home currency in this window) | stable, at cost (1.0-1.1 vs 0.9) |
| O5 | GBPJPY long 17:30-21:30 London (G1) | JPY weakens / risk-on drift in the New York afternoon; no fixing mechanism, the weakest prior | stable, cost 1.1-1.2 |

Eras: PRE 2004-15 (Dukascopy M1 bid; IC 2016-17 spread by NY minute + 0.6 bp), IS 2016-21, VAL 2022-24 (panel mid,
actual spread half in + half out + 0.6 bp). Weekdays, 24 Dec-1 Jan excluded, stream M's exclusions (rollover
16:45-18:15 NY, quotes > 10 min stale).

## R3. Conditions, predicted direction, levels (all causal: data to the minute before entry)
"Signed" = multiplied by the object's side, so > 0 means "the pair already moved in the effect's direction".

Selectors (each in two levels: HALF = signed variable > 0; TOP = signed variable >= its trailing 250-day 67th
percentile for that object, min 60 days of history):
- **S1 MORN** (O1-O5): the pair's own move over the 4 hours before entry, ending 1 minute before entry (O1, O3:
  07:00-10:59 London; O2: 08:45-12:44 London; O4: 06:00-09:59 UTC; O5: 13:30-17:29 London). Predicted: **larger
  effect when the pair already moved in the effect direction** (home-hours flow is persistent within the day: Breedon
  & Ranaldo find local-hours order flow drives the depreciation through the session; a dealer who absorbed it lays it
  off). Competing story (inventory reversal) predicts the opposite; the registered side is continuation.
- **S2 PREV** (O1-O5): yesterday's same-window move (previous weekday with data), signed. Predicted: **larger after a
  same-direction window yesterday** (flow persists day to day).
- **S3 TRAIL** (O1-O5): mean of the signed same-window return over the previous 20 trading days. Predicted: **larger
  when the trailing 20-day mean is > 0** (net portfolio-outflow regimes last weeks, so the flow behind the clock
  effect has regimes).
- **S4 USD** (O1-O4): the dollar's overnight move, previous day 18:00 New York -> 06:59 London, measured on the USD
  pairs other than the object's (O1, O2: mean of USDJPY and USDCHF; O3: mean of -EURUSD and USDCHF; O4: mean of
  -EURUSD and USDJPY), signed so > 0 = USD up = the objects' direction. Predicted: **larger after a USD-up night**
  (dollar demand that starts in Asia continues into the European fix; weak prior, the hedge-rebalancing story says
  the opposite).
- **S5 RISK** (O5 only, IS/VAL only, no PRE data): US500 move 09:30-12:29 New York, signed long. Predicted: **larger
  when US equities rose in the morning** (yen crosses follow risk appetite; market intraday momentum, Gao, Han, Li &
  Zhou 2018).

Exclusion filters (one level each; the cell is "all days except ..."; predicted: the excluded days have a smaller or
unsigned effect):
- **X1 ECB** (O1-O4): ECB monetary-policy decision days (cb_calendar.json; 13:45 CET = 12:45 London through Jun 2022,
  i.e. inside O1/O2; 14:15 CET after). Predicted: on decision days the window is news, not flow: mean ~0, sd much
  larger, so excluding them raises the Sharpe.
- **X2 ECB-1** (O1-O4): the weekday before an ECB decision. Predicted smaller (positions and hedges wait for the
  decision).
- **X3 HOME-HOL** (O1-O3: TARGET2 closing days, i.e. Good Friday, Easter Monday, 1 May; the ECB publishes no
  reference rates then, so the pre-fix leg should be 0. O4: Zurich holidays. O5: US federal / NYSE holidays). Predicted
  effect ~0 on those days.
- **X4 DE-ONLY-HOL** (O1-O3): German (Hesse) holidays on which TARGET is open (Ascension, Whit Monday, Corpus Christi,
  3 Oct): the fix is published but German clients are away. Predicted smaller.
- **X5 DST4** (O1-O4): days when London-New York is 4 h (US on DST, UK not: ~2nd Sunday March to last Sunday March,
  and last Sunday Oct to 1st Sunday Nov, from 2007). Then 11:00-13:00 London is 07:00-09:00 NY and holds the 08:30 ET
  releases. Predicted smaller / noisier. (PRE 2004-06 had 6 h weeks instead; reported separately, not counted.)
- **XC composite** (O1-O4): all of X1, X3, X5 excluded together.

Secondary, counted: each selector level combined with XC (S x XC), O1-O4.

Placebo (not a candidate): JPY, AUD (NSW), CAD (ON), NZD holidays that are not EUR/GBP/CHF/USD holidays, for O1-O4;
predicted no difference. Clustered by holiday block.

Not done, and why: realised-vol terciles (round 10 E's construction; the mechanism gives ~1.5x with spreads rising);
weekday, month-end, US/GBP/JPY holidays (seen, information only).

## R4. Cell count (declared now)
- O1-O4: selectors S1-S4 x 2 levels = 8; exclusions X1-X5 + XC = 6; S x XC = 8. 22 per object, 88.
- O5: S1-S3 x 2 + S5 x 2 = 8; X3 (US holiday) = 1. 9.
- **K = 97 counted cells.** Placebo and information cells are reported but not counted.
- Correction 01:53 UTC, before any number: X4 (DE-only holidays) is declared for O1-O3 only, so O4 has 21 cells and
  **K = 96**. Information cells (not counted): holiday placebo (O1-O5), US-holiday exclusion (O1-O4, seen in round 13),
  DST 6 h weeks 2004-06 (O1-O4).

## R5. Statistics and bars
- Per cell and era: n, mid bp (t, day-clustered = one trade per day), cost, net (t), per-trade net Sharpe, trades
  per year, power at that frequency (IS and VAL size), and the uplift = mean(selected) - mean(rest), Welch t, signed so
  > 0 = predicted direction. By year for anything that passes.
- Pass gate to be called a survivor (all fixed now): uplift > 0 in PRE (where data exist), IS and VAL; selected net
  > 0 in IS and VAL; then the LIVE / DEMO bars of the round-13 brief (IS net t >= 2.5, VAL >= 1.5, 2/3 of years > 0,
  random control >= 95 %, power >= 3 on the VAL size for LIVE). A rule that only meets DEMO and is a subset of E1 is
  not a new candidate (E1 is already registered at DEMO); it gets a draft only if it reaches LIVE.
- Survivors: spread x1.5, both fills +1 minute, look-ahead-free random-entry control (random start among the
  15-minute London starts 07:00-16:00 of the same length; the selector recomputed at the random start from the 4 h /
  yesterday / 20 days before it; >= 200 seeds), VAL/IS ratio, expected HOLD t on the VAL size, C3 correlation (IS+VAL).
- Chance: one shared null over all 97 cells: (a) selected-cell net t, per-UTC-date sign flips shared by all cells;
  (b) uplift t, random circular shifts of every condition flag within each era (one shift per draw, shared). Report
  the max-statistic 95th percentile against the best observed.

## R6. Post-hoc additions (written after the r1-r3 numbers, 01:57 UTC; not counted, not candidates)
- Holiday cells re-reported with t clustered by holiday block (dates within 4 days = one block), pooled 2004-24,
  because the per-era counts are 8-43 days.
- Arithmetic only: E1 every day with the lot 2x on selector days and 0.5x otherwise (the allowed lot range), to bound
  what the selectors could add as sizing instead of filtering.
- O5 with S1 flipped (GBPJPY long in the New York afternoon after the pair FELL in the New York morning), because S1's
  uplift had the wrong sign in all three eras.
- The random-entry control is not valid for O5 RISK-TOP (US500 09:30-12:29 NY overlaps the random windows starting
  08:00-12:45 NY); reported as n/a.
