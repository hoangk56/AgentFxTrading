# PREREG DRAFT (stream S): long GBPJPY 10:28-10:31 New York on the last weekday of the month

Draft written 2026-10-06 by stream S of round 15. Not a registration: the lead decides, re-implements and hashes.
HOLD (2025-01..2026-09) was not opened by stream S.

**Tier: DEMO by the numbers (IS net t 4.34, VAL net > 0, beats 100 % of random entries, > 0 at x1.5 and +1 minute).**
It is a **post hoc**, **decaying** lead with **no known mechanism** and a one-cell-wide plateau. Stream S recommends
against registering it. Expected HOLD t on the VAL size is about 0.6.

## Rule (exact)
- Symbol GBPJPY. Days: the last Monday-Friday of each calendar month (holidays not skipped), December excluded by the
  24 Dec - 1 Jan rule.
- Buy at market at 10:28:00 America/New_York (DST-aware), sell at market at 10:31:00 New York. One position, no stop,
  fixed default lot. Quote = close of the last M1 bar ending at or before the time; cost = half the actual spread at
  entry + half at exit + 0.6 bp.

## How it was found
- Declared scan: 85,225 cells, nothing beyond chance on the declared path (see STREAM_S.md).
- Post hoc loose carry (cells with |t_PRE| >= 2, side from PRE): best IS net t in the NY10 x GBPJPY pool (201 cells).
  PRE gave the side (long, mid +1.32, t 2.90). IS sign-flip null of the max side t over the 9,111-cell pool: 95 %
  4.27; this cell's IS mid t 6.17.

## Numbers
| era | trades | mid bp (t) | cost | net bp (t) | x1.5 | +1 min | years net > 0 | net Sharpe | power |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 | 132 | +1.32 (2.90) | 1.27 | +0.05 (0.11) | -0.28 | -0.12 | 7/12 | 0.010 | 0.04 |
| IS 2016-21 | 66 | +3.51 (6.17) | 1.04 | **+2.48 (4.34)** | +2.26 | +1.09 | 6/6 | 0.535 | 2.33 |
| VAL 2022-24 | 33 | +1.58 (2.60) | 1.11 | **+0.47 (0.77)** | +0.21 | +0.61 | 2/3 | 0.134 | 0.59 |

- Mid by year: IS 5.5, 3.6, 3.5, 1.5, 4.6, 2.5; VAL 2.2, 1.5, 1.0 (falling). **VAL/IS 0.45: decaying.**
- Random-entry control (same days, side, 3-minute windows starting uniformly 07:00-17:00 New York, 200 seeds):
  beats 100 % IS and VAL.
- Placebos, same window on the k-th-last weekday k = 2..5: PRE -0.04..+0.26, IS -0.41..+1.26, VAL -1.85..-0.02.
- **Plateau is one cell wide**: 10:25-10:28 +0.09 / +0.64 / -0.65 and 10:31-10:34 -0.32 / -1.00 / -0.40 (PRE / IS /
  VAL mid). Same on the London clock (15:28-15:31): +1.36 / +3.91 / +1.30.
- Not a quarter-end effect (IS quarter-end +4.06, other month-ends +3.31). Same window: EURJPY +0.26 / +1.31 / +0.62,
  EURUSD +0.34 / +0.81 / +1.09, USDJPY +0.19 / +0.45 / -0.46.
- Winsorised 5/95 IS +3.52; share > 0 79 % IS, 67 % VAL.
- Correlation with C3 (IS + VAL): daily +0.002, monthly +0.030.
- **Expected HOLD t** (about 19 month-ends): 0.59 on the VAL size, 2.33 on the IS size.

## Caveats
1. No mechanism is known for 15:28-15:31 London (10:28-10:31 New York) on month-end. A guess: bank cut-offs for
   month-end WM/R fix orders 30 minutes before the 16:00 fix, with GBP buying hedged early. Not sourced.
2. Post hoc: chosen on IS from a pool of 201 cells (9,111 in all) with VAL in view in table (c).
3. Decaying (IS 3.51 -> VAL 1.58, 2024 1.0) and PRE net about 0 at PRE costs.
4. About 11 trades a year: DEMO evidence accrues slowly (at the VAL Sharpe, pooled t 2.5 needs ~350 trades, i.e.
   decades).

## DEMO plan (only if the lead registers it)
- Expected demo trades: ~11 a year. Stop rule: stop after 24 demo trades if the pooled HOLD + demo net mean <= 0.
  Promotion: HOLD + demo pooled net t >= 2.5 (not reachable in a useful time at the VAL size).

## Code
Scratchpad `.../scratchpad/r15/S/`: `step3.py` (tables (b), (c)), `step4.py` (numbers, control, placebos,
neighbours, other symbols, pool null), `step5.py` (quarter-end split, months, London clock). Outputs `*.out`.
