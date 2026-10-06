# PREREG DRAFT (stream S): short EURUSD 12:50-13:00 London on Fridays (the ECB pre-fix slot)

Draft written 2026-10-06 by stream S of round 15. Not a registration: the lead decides, re-implements and hashes.
HOLD (2025-01..2026-09) was not opened by stream S.

**Tier: DEMO by the numbers (meets every DEMO condition; meets every LIVE condition except power: 2.04 on the IS
size, 2.08 on the VAL size, bar 3).** It is a **post hoc** lead, and a **subset of E1**, whose HOLD was opened in round
13. Stream S recommends against registering it as a HOLD test. Read the caveats first.

## Rule (exact)
- Symbol EURUSD. Days: Fridays by the London calendar date, except 24 Dec - 1 Jan. Holidays are not skipped (see
  caveat 5 for TARGET2 closures).
- Sell at market at 12:50:00 Europe/London (DST-aware), buy back at market at 13:00:00 London (= 13:50-14:00 CET,
  the 10 minutes before the V of the ECB reference-rate window). One position per Friday, no stop, fixed default lot.
- Quote = close of the last M1 bar ending at or before the time (at most 10 minutes stale, otherwise no trade). Cost =
  half the actual spread at entry + half at exit + 0.6 bp commission.

## How it was found (selection path, all disclosed)
1. Declared scan (HYPOTHESES_S.md): 85,225 cells (5 FX pairs x 8 benchmark anchors x starts within +-30 min x lengths
   1/2/3/5/10 min x 7 day types), side = sign of the PRE 2004-15 mean. The declared path found nothing beyond chance
   (set A: 25 / 409 IS confirmations vs a null 95th percentile of 30).
2. Post hoc "loose carry": cells with |t_PRE| >= 2 (9,111), side from PRE. Best IS net t per anchor x symbol: for
   ECB x EURUSD (pool 572) it was 12:55-13:00 Fridays (IS net +0.95, t 4.31). Among 10-minute Friday windows the IS-
   best was 12:50-13:00 (IS net +1.13, t 3.81). VAL was in view when these tables were printed (table (c) filtered on
   net VAL > 0). This draft uses the 10-minute window because the 5-minute one fails the latency test in VAL (+1 min:
   -0.51 bp).
3. Chance for the pool: IS sign-flip null of the max side t over the 9,111 cells: median 3.70, 95 % 4.27; this cell's
   IS mid t is 5.95 (12:55-13:00: 7.18).

## Numbers (mid = before costs; PRE = Dukascopy bid + IC 2016-17 spread profile by New York minute + 0.6 bp)
| era | trades | mid bp (t) | cost | net bp (t) | x1.5 spread | +1 min (both fills) | years net > 0 | net Sharpe | power |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 | 611 | +0.58 (2.52) | 0.66 | -0.08 (-0.33) | -0.11 | +0.10 | 5/12 | -0.013 | -0.13 |
| IS 2016-21 | 305 | +1.76 (5.95) | 0.63 | **+1.13 (3.81)** | +1.11 | +0.96 | 6/6 | 0.218 | 2.04 |
| VAL 2022-24 | 153 | +1.95 (4.10) | 0.64 | **+1.31 (2.74)** | +1.28 | +0.70 | 2/3 (2024 -0.1) | 0.221 | 2.08 |

- By year, net bp: IS 0.3, 2.1, 1.8, 0.8, 0.2, 1.6; VAL 2.9, 1.1, -0.1 (falling inside VAL).
- VAL/IS 1.11 (mid). IS/PRE 3.0: the size is not stable from PRE (PRE net is below cost).
- Random-entry control (same Fridays, same side, 10-minute windows starting uniformly 07:00-17:00 London, 200 seeds):
  beats 100 % in IS and 100 % in VAL (random median net -0.58 / -0.65).
- Robustness: winsorised 2.5/97.5 IS +1.66, VAL +2.05; median +1.52 / +2.01; share > 0 67 % / 69 %; without
  month-end and holiday-adjacent Fridays +2.21 (t 5.7) / +2.43 (t 4.4).
- Plateau (Fridays, net IS / VAL): 12:45-13:00 +1.47 / +1.52; 12:48 +1.25 / +1.46; 12:50 +1.13 / +1.31; 12:52
  +0.98 / +0.91; 12:55 +0.95 / +0.65; 12:56 +0.60 / -0.10. Exit 13:01 or 13:02 costs 0.1-0.4 bp.
- Correlation with C3 (IS + VAL): daily +0.023, monthly -0.058.
- **Expected HOLD t** (about 90 Fridays in 2025-01..2026-09): 2.08 on the VAL size, 2.04 on the IS size.

## Why Friday (mechanism, partly post hoc)
Friday enlarges both legs of the ECB-fix V in IS and VAL: pre-leg (short 12:50-13:00) Friday minus Mon-Thu +1.18 bp
(t 3.48) IS, +1.36 (t 2.60) VAL; post-leg (long 13:00-13:15) Friday +1.16 / +1.71 against +0.05..+1.05 on other days.
A larger Friday fix flow (weekly settlement and hedge rolls benchmarked to the ECB rate) would do this; no source
found that measures it. In PRE the Friday difference is +0.34 (t 1.32), and the V sat 15 minutes later.

## Caveats (read before registering)
1. **Post hoc.** Friday and the 12:50 start were chosen on IS, with VAL in view. Only the side came from PRE.
2. **Subset of E1** (short 11:00-13:00 London every weekday, round 13). E1's HOLD was opened on 2026-10-06, so a HOLD
   test of this subset is not blind: E1's HOLD showed most of its edge in the entry/exit minute (both fills +1 minute:
   -0.00), and its exit is this rule's exit (13:00 London).
3. **PRE does not support the size.** PRE net is -0.08 at PRE costs; the 15-minute shift of the ECB V at the 2015/16
   boundary (verified in this round with Dukascopy 2016-17 = IC 2016-17) means a clock-fixed practice can move again.
4. **Power < 3** at ~52 trades a year: it cannot reach LIVE on HOLD alone (expected t ~2.1).
5. TARGET2 closing days (Good Friday is one) have no ECB reference rate and E1 reverses on them (round 14 R:
   -3.9 bp, t -2.7). Skipping Good Friday is justified by the mechanism alone; the tested rule does not skip it.
6. Information only: the Friday two-leg trade (short 12:50-13:00, long 13:00-13:15, two round trips) nets +1.65
   (t 3.60) IS, +2.38 (t 3.78) VAL, power 1.93 / 2.87; PRE -2.33 because the PRE V sat at 13:13-13:15. Its post-leg
   side contradicts PRE; not a candidate under this round's protocol.

## DEMO plan, stop and promotion rules (if the lead registers it anyway)
- Expected demo trades: about 50 a year.
- Stop rule: stop after >= 50 demo trades if the pooled HOLD + demo net t <= -1.0, or if the realised mean round-trip
  cost exceeds 1.0 bp.
- Promotion rule: HOLD + demo pooled day-clustered net t >= 2.5 at the costs actually paid, net > 0 at spread x1.5,
  >= 100 demo trades. At the VAL Sharpe (0.22) that needs about 130 trades, i.e. HOLD (~90) plus about a year of demo.

## Code (scratchpad `.../scratchpad/r15/S/`)
`scommon.py` (on top of round 13 M's `mcommon.py`), `scan.py`, `step2.py`, `step3.py` (tables (b), (c)), `step4.py`
(this rule's numbers, random control, C3 correlation, weekday split, pool null), `step5.py` (robustness, plateau),
`step6.py` (two-leg information line). Outputs `*.out` alongside.
