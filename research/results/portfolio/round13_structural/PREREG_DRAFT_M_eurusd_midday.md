# PREREG DRAFT (stream M): E1, short EURUSD 11:00-13:00 London every weekday

Draft written 2026-10-06 ~01:40 UTC by stream M. Not a registration: the lead decides, re-implements and hashes. HOLD
(2025-01..2026-09) was not opened by stream M.

**Tier: DEMO (meets every DEMO number; meets every LIVE number except power: 1.78 on the IS size, 1.88 on the VAL size,
bar 3).** It is a weak candidate; the caveats below matter as much as the table.

## Rule (exact)
- Symbol EURUSD. Days: Monday-Friday by the London calendar date, except 24 Dec - 1 Jan. Holidays are not skipped.
- Sell at 11:00:00 Europe/London (DST-aware: 10:00 UTC in summer, 11:00 UTC in winter), at the bid; buy back at
  13:00:00 London, at the ask. One position per day; no stop in the test (see "Operations").
- Lot: one fixed default lot, never dependent on capital (no sizing by signal).
- Side fixed from PRE 2004-2015 (sign of the PRE mean); window chosen on IS as the best IS t among the 500 PRE-carried
  cells; VAL was in view when it was picked (disclosed).

## Mechanism and sources
European-midday weakness of the euro against the dollar, ending at the V around 14:00 CET where EUR then rises into
the 14:15 CET ECB reference rate (rounds 4, 10, 12 measured that rise). Sources: home-hours depreciation (Ranaldo 2009;
Breedon & Ranaldo 2013), fix flows (Krohn, Mueller & Whelan 2024). The window's last 15 minutes (12:45-13:00 London =
13:45-14:00 CET) carry about 60 % of the IS/VAL mean.

## Numbers (mid = before costs; net = half the actual IC spread at entry and exit + 0.6 bp; PRE = Dukascopy bid + IC
2016-17 spread profile by New York minute + 0.6 bp)
| era | trades | mid bp (t) | net bp (t) | x1.5 spread | +1 min | years net > 0 | per-trade net Sharpe | power |
|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 | 3,054 | +1.69 (5.21) | +1.02 (3.15) | +0.98 | +0.85 | 11/12 | 0.057 | 1.20 |
| IS 2016-21 | 1,525 | +1.80 (5.08) | +1.17 (3.29) | +1.15 | +1.08 | 5/6 | 0.084 | 1.78 |
| VAL 2022-24 | 765 | +1.97 (3.59) | +1.35 (2.46) | +1.34 | +1.04 | 3/3 | 0.089 | 1.88 |

- One trade per day, so the day-clustered t equals the trade t.
- Ratios: IS/PRE 1.07, VAL/IS 1.10 (not decaying by era). By year (mid): IS 3.7, 2.0, 1.5, 2.1, -0.1, 1.6; VAL 3.5,
  1.6, 0.8 (falling inside VAL).
- Random-entry control (same days, same side, 2-h windows starting at random on the 15-min grid 07:00-16:00 London, 200
  seeds): beats 100 % (IS) and 99 % (VAL); random median net -0.33 / -0.34 bp.
- Multiple testing: the cell came from K = 270,086 PRE cells (max |t_PRE| 10.98 vs permutation 95 % 5.46), then the
  best IS t among the 500 carried cells: 5.08 vs the sign-flip permutation 95 % of the carried-set max, 3.66.
- Correlation with C3 (IS + VAL): daily +0.043, monthly +0.055.
- **Expected HOLD t** (about 445 trades in 2025-01..2026-09): 1.88 on the VAL size, 1.77 on the IS size. HOLD cannot
  confirm this rule at the LIVE level; it can only fail it.

## Caveats (read before registering)
1. **The plateau is narrow.** Neighbouring 2-h windows give +0.6..0.9 bp in IS (10:45-12:45 +0.62, 11:15-13:15
   +0.88), 11:00-12:00 +0.68, 11:00-15:00 +0.89. The edge sits at the two ends: 11:00-11:15 and, above all,
   12:45-13:00 London (IS +1.09, t 5.9; VAL +1.12, t 4.5), followed by a reversal at 13:00-13:15 (IS -0.72, VAL -0.81).
2. **PRE supports the rule's mean, not its composition.** In PRE the mean comes from 11:45-12:00 London (+1.25 bp,
   t 11.0, every year 2004-2015, then about 0 from 2016: IS +0.08, VAL -0.03) and the V around the fix sat 15 min later
   (EUR fell 13:00-13:15 London and rose 13:15-13:30 until 2015, while from 2016 it falls 12:45-13:00 and rises
   13:00-13:15). E1 minus 11:45-12:00: PRE +0.43 (t 1.41), IS +1.71, VAL +2.00. E1 minus both slots: PRE -0.09,
   IS +0.62 (t 2.21), VAL +0.88 (t 1.89). An institutional timing changed at the 2015/16 boundary; the same can
   happen again.
3. **Known effect.** The 14:00-14:15 CET EUR rise and the ECB-fix V were tested in rounds 3, 4, 10 and 12 (break-even
   0.73 / 0.85 bp, sub-cost). E1 differs by holding the 2 h before the V's low, which adds drift at the same cost.
4. Power is below 3 with one symbol. The family is stopped (brief): no pooling or sizing was searched. USDJPY long in
   the same window is stable (+1.08 / +0.88 / +0.95 bp) but nets +0.14 / +0.25; USDCHF long decays in VAL (+0.59);
   GBPUSD is unstable (+0.20 / +0.76 / +1.65).

## DEMO plan, stop and promotion rules
- Expected demo trades: about 254 a year (one per London business day).
- Stop rule: stop the demo if, after 250 demo trades, the net mean per trade is <= 0, or at any time if the cumulative
  net t < -2.0.
- Promotion rule: HOLD + demo pooled net t >= 2.5. At the VAL Sharpe (0.089) that needs about 790 trades, i.e. HOLD
  (~445) plus ~1.4 years of demo.
- Operations: the test has no stop. If the bot needs a protective stop, put it far (>= 100 bp, about 7 sd of the 2-h
  return) and have the lead measure its effect on IS/VAL before registering.

## Code (stream M scratchpad, `.../scratchpad/r13/M/`)
`mcommon.py` (grids, clocks, day types, windows, costs), `scan1.py` (PRE scan), `step2.py` (carried sets, IS
confirmation, permutation nulls), `step3.py` (this rule's numbers, control, C3 correlation), `step4.py`, `step4b.py`,
`step4c.py` (plateau, slots, decomposition). Outputs `*.out` alongside.
