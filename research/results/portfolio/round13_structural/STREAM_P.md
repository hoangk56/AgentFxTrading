# Round 13, stream P: the gold big-day settlement mechanism (L4) on other closes and settlements

2026-10-06. The hypotheses, with the rule, side, gate, windows, benchmarks and cell count, were written at 01:29 UTC,
before any return was computed: [HYPOTHESES_P.md](HYPOTHESES_P.md). Before writing them I looked only at quote
coverage. HOLD was never loaded: the panel ends 2024-12-31, and the US2000 cache is cut at 2025-01-01 at load. There
is no PRE era because the data have no index or energy series before 2016.

## Answer
- **LIVE: none. DEMO: none. No PREREG draft.**
- Rule: follow the day's move into the close or settlement on top-decile |z| days. This is gold's L4-G-d rule
  unchanged. It was tested on 11 symbol-benchmarks x 2 windows, plus 3 pooled cells: **25 counted cells, and 4
  information-only cells** (US500, US2000).
  - No counted cell reaches IS net t 2.0 with VAL net > 0.
  - Every top-decile scale-up in IS comes from 2020. Without 2020, the IS top-decile mid is -1.8 to +1.7 bp for the
    stock indices.
  - The US indices reverse on big days in VAL.
- **What is real is not tradable.**
  - **DE40** is the one symbol where the dose slope is positive in both eras: t +3.3 IS / +4.0 VAL at w = 15.
  - It is not a close flow, though. Random windows on the same days, with the side recomputed, earn as much or more:
    net +1.47 actual vs +2.36 random mean in IS, +3.42 vs +3.20 in VAL; the actual cell beats only 28 % / 54 % of
    500 seeds.
  - It is big-day intraday trend, available at any hour.
- **JP225 follows the day's move in the quarter-hour after the Tokyo cash close (15:00-15:15).** This is the strongest
  all-days effect: +3.39 bp (t 5.6) IS.
  - It decayed to +0.59 (t 1.0) in VAL, a ratio of 0.17.
  - It does not scale up with |z|: the top decile is 1.0x the all-day mean.
  - The cost is 3.1 / 1.9 bp.

## How this differs from the earlier tests
| earlier | what it tested | here |
|---|---|---|
| r3 Nikkei LETF at the Tokyo close | all days; "nothing" (fade after the close, IS t -3.6) | top decile of z, measured from the previous close and scaled by 60-day vol; dose bins; TSE close and OSE futures close as separate cells; TSE 15:30 from 2024-11-05 |
| r4 Baltussen, US close | last 30 min, all days and \|z\| > 2: USTEC +0.7 / +1.1, big days +10.0 (t 1.2) / +3.1 | causal top decile; 10-15 min windows; a 1-minute lag after the signal; both fills +1 min |
| r6 S1 energies | all days and \|z\| > 1 (XTI +5.6 t 2.0 / +1.8) | top decile at actual spreads; XBR on ICE days and London clock; April 2020 dropped |
| r11 H2 USTEC MOC | the 15:50 imbalance-minute move | the day's move (LETF rebalancing is close-to-close) |
| r12 L6-LETF | USTEC top quintile of the 09:30-15:50 move; net +1.94 (1.3) / +3.11 (1.8) | previous-close reference, vol-scaled, top decile, 10 more venues, shared null |

Pipeline check: this code reproduces gold's L4-G-d. IS n 149, mid +4.91, net +3.50 (t 3.19); round 12 had 150,
+4.74, +3.31 (3.02). VAL matches exactly: n 78, mid +3.14, net +2.11 (t 1.70).

## All cells
- **Units.** All numbers are in bp. t is clustered by UTC day; it equals the per-trade t for single-symbol cells.
- **Costs.** Net = mid - half the actual spread at entry - half at exit. No commission (indices and energies).
- **Columns.**
  - "x all" = top-decile mid / all-days mid. It is meaningless when the all-days mean is about 0.
  - Power = per-trade net Sharpe x sqrt(1.73 x trades a year). The VAL column is the expected HOLD t at the VAL size.
    Pooled cells use UTC-day units ("d").
  - VAL/IS net is shown only where IS net > 0.
- **Eras.** IS is 2016-21, and 2018-21 for the energies.

| cell | w | all-days mid IS / VAL (t) | dose slope t IS / VAL | top-decile n/yr | top-decile mid IS (t) | x all | VAL (t) | x all | cost IS / VAL | net IS (t) | net VAL (t) | VAL/IS net | +1 min net IS / VAL | x1.5 IS / VAL | power IS / VAL | yrs > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| XTI | 15 | +4.81 (+2.2) / +1.86 (+1.4) | +1.0 / -1.9 | 24 / 25 | +18.17 (+2.1) | 3.8 | -2.66 (-0.5) | -1.4 | 7.80 / 3.38 | +10.37 (+1.2) | -6.05 (-1.2) | -0.58 | +3.83 / -4.85 | +6.47 / -7.74 | +0.81 / -0.92 | 4/7 |
| XTI | 10 | +2.65 (+1.4) / +3.48 (+3.0) | +1.4 / +0.1 | 25 / 25 | +11.99 (+1.4) | 4.5 | +7.57 (+1.7) | 2.2 | 7.70 / 3.33 | +4.29 (+0.5) | +4.24 (+1.0) | +0.99 | +1.28 / +0.06 | +0.44 / +2.58 | +0.35 / +0.73 | 5/7 |
| XBR | 15 | +0.43 (+0.3) / +0.99 (+0.8) | +0.7 / -2.0 | 25 / 24 | +2.62 (+0.5) | 6.1 | -2.85 (-0.6) | -2.9 | 6.30 / 2.40 | -3.69 (-0.8) | -5.26 (-1.1) | | -8.68 / -3.60 | -6.84 / -6.46 | -0.52 / -0.87 | 3/7 |
| XBR | 10 | -0.80 (-0.7) / +1.50 (+1.5) | +0.6 / +0.8 | 25 / 24 | +4.15 (+0.9) | | +4.32 (+1.1) | 2.9 | 6.42 / 2.41 | -2.27 (-0.5) | +1.91 (+0.5) | | -2.53 / -1.73 | -5.48 / +0.70 | -0.35 / +0.36 | 3/7 |
| XNG | 15 | +3.18 (+1.2) / +6.24 (+2.3) | -0.0 / +0.5 | 30 / 24 | +0.50 (+0.0) | 0.2 | -6.19 (-0.7) | -1.0 | 12.19 / 40.17 | -11.69 (-1.1) | -46.36 (-5.2) | | -18.20 / -52.69 | -17.78 / -66.45 | -0.92 / -3.97 | 2/7 |
| XNG | 10 | +1.80 (+0.8) / +7.61 (+3.4) | -0.6 / +1.7 | 25 / 25 | -5.71 (-0.6) | | +2.98 (+0.4) | 0.4 | 12.06 / 40.47 | -17.77 (-1.7) | -37.49 (-4.7) | | -23.06 / -49.90 | -23.80 / -57.72 | -1.42 / -3.56 | 2/7 |
| US30 | 15 | +0.87 (+1.2) / -0.52 (-0.8) | +3.2 / -0.9 | 26 / 25 | +7.41 (+1.4) | 8.6 | -1.99 (-0.9) | | 1.00 / 0.30 | +6.41 (+1.2) | -2.30 (-1.0) | -0.36 | +2.61 / -1.69 | +5.91 / -2.45 | +0.66 / -0.76 | 3/9 |
| US30 | 10 | +0.91 (+1.5) / -0.43 (-0.7) | +4.6 / -1.2 | 27 / 24 | +7.17 (+1.8) | 7.8 | -3.56 (-1.5) | | 1.00 / 0.31 | +6.16 (+1.6) | -3.87 (-1.6) | -0.63 | +0.67 / -1.85 | +5.66 / -4.02 | +0.87 / -1.23 | 3/9 |
| USTEC | 15 | +1.45 (+1.7) / +0.50 (+0.6) | +3.5 / -0.3 | 27 / 28 | +7.71 (+1.4) | 5.3 | -1.60 (-0.5) | -3.2 | 1.66 / 0.64 | +6.05 (+1.1) | -2.23 (-0.8) | -0.37 | +1.84 / -3.68 | +5.23 / -2.55 | +0.60 / -0.58 | 3/9 |
| USTEC | 10 | +1.32 (+1.9) / +1.07 (+1.3) | +4.1 / -0.1 | 27 / 28 | +9.86 (+2.3) | 7.4 | -2.04 (-0.7) | -1.9 | 1.66 / 0.65 | +8.20 (+1.9) | -2.69 (-1.0) | -0.33 | +2.65 / -2.58 | +7.37 / -3.02 | +1.06 / -0.74 | 3/9 |
| JP225t (TSE close) | 15 | -0.08 (-0.2) / +0.34 (+0.7) | +2.1 / +0.0 | 26 / 24 | +1.06 (+0.6) | | -0.04 (-0.0) | | 3.07 / 1.82 | -2.02 (-1.1) | -1.86 (-0.8) | | -3.05 / -0.06 | -3.55 / -2.78 | -0.60 / -0.64 | 2/9 |
| JP225t | 10 | -0.51 (-1.6) / -0.03 (-0.1) | -0.2 / -2.5 | 25 / 24 | -1.19 (-0.9) | | -3.18 (-1.3) | | 3.08 / 1.82 | -4.27 (-3.3) | -5.00 (-2.1) | | -6.33 / -3.18 | -5.81 / -5.92 | -1.83 / -1.59 | 0/9 |
| JP225o (OSE close) | 15 | +3.39 (+5.6) / +0.59 (+1.0) | +3.2 / +1.0 | 27 / 25 | +3.51 (+1.2) | 1.0 | +1.16 (+0.5) | 2.0 | 3.14 / 1.87 | +0.37 (+0.1) | -0.71 (-0.3) | -1.90 | +0.22 / -3.83 | -1.20 / -1.64 | +0.07 / -0.25 | 4/9 |
| JP225o | 10 | +2.70 (+6.3) / +0.12 (+0.3) | +2.4 / -0.3 | 26 / 26 | +2.71 (+1.3) | 1.0 | -0.22 (-0.1) | | 3.03 / 1.87 | -0.32 (-0.2) | -2.10 (-1.3) | | -2.99 / -3.35 | -1.84 / -3.03 | -0.09 / -1.02 | 3/9 |
| DE40 | 15 | +0.96 (+2.1) / +1.64 (+3.6) | **+3.3 / +4.0** | 26 / 26 | +2.66 (+1.4) | 2.8 | +3.94 (+2.1) | 2.4 | 1.19 / 0.52 | +1.47 (+0.8) | +3.42 (+1.8) | +2.33 | +1.54 / +3.78 | +0.87 / +3.16 | +0.41 / +1.36 | 4/9 |
| DE40 | 10 | +1.16 (+3.1) / +1.06 (+2.7) | +2.4 / +3.3 | 27 / 25 | +2.01 (+1.1) | 1.7 | +3.17 (+1.7) | 3.0 | 1.20 / 0.53 | +0.81 (+0.5) | +2.65 (+1.4) | +3.26 | +0.33 / +3.72 | +0.21 / +2.38 | +0.25 / +1.06 | 4/9 |
| UK100 | 15 | +0.81 (+1.7) / +0.38 (+0.9) | +0.5 / +1.0 | 28 / 26 | -0.64 (-0.3) | | +0.85 (+0.5) | 2.3 | 2.44 / 1.70 | -3.09 (-1.4) | -0.84 (-0.5) | | -3.53 / -1.51 | -4.31 / -1.69 | -0.76 / -0.36 | 3/9 |
| UK100 | 10 | +0.48 (+1.1) / +0.11 (+0.3) | +0.4 / +0.2 | 27 / 27 | -1.23 (-0.6) | | +0.54 (+0.3) | | 2.44 / 1.67 | -3.67 (-1.8) | -1.13 (-0.7) | | -4.89 / -0.67 | -4.89 / -1.97 | -0.97 / -0.51 | 1/9 |
| HK50 | 15 | -0.92 (-2.3) / +0.57 (+0.8) | -3.3 / -0.1 | 28 / 27 | -4.64 (-3.0) | | +1.68 (+0.6) | 2.9 | 3.36 / 2.82 | -8.00 (-5.2) | -1.14 (-0.4) | | -5.54 / -3.44 | -9.68 / -2.55 | -2.86 / -0.32 | 1/9 |
| HK50 | 10 | -0.51 (-1.4) / +0.21 (+0.3) | -2.7 / -1.1 | 27 / 27 | -2.73 (-2.1) | | -1.29 (-0.5) | | 3.37 / 2.87 | -6.10 (-4.7) | -4.15 (-1.5) | | -3.88 / -1.38 | -7.78 / -5.58 | -2.61 / -1.20 | 1/9 |
| AUS200 | 15 | +1.14 (+1.6) / +0.26 (+0.7) | +3.3 / -1.3 | 25 / 26 | +4.92 (+1.7) | 4.3 | -1.11 (-0.7) | | 1.88 / 1.17 | +3.04 (+1.1) | -2.28 (-1.3) | -0.75 | +3.19 / -2.22 | +2.10 / -2.87 | +0.62 / -1.02 | 3/9 |
| AUS200 | 10 | +0.18 (+0.3) / -0.34 (-1.0) | +3.9 / -2.9 | 25 / 25 | +4.83 (+1.8) | | -3.44 (-2.3) | | 1.93 / 1.16 | +2.90 (+1.1) | -4.60 (-3.0) | -1.58 | +1.82 / -3.78 | +1.94 / -5.18 | +0.63 / -2.30 | 2/9 |
| POOL-ALL (11) | 15 | +1.28 (+3.7) / +1.18 (+3.2) | | 245 / 277 | +3.52 (+1.8) | 2.7 | -0.76 (-0.6) | | 3.36 / 5.02 | +0.16 (+0.1) | -5.78 (-4.4) | | -1.62 / -6.54 | -1.52 / -8.29 | +0.05d / -3.34d | 1/9 |
| POOL-EQ (7) | 15 | +1.09 (+3.3) / +0.49 (+1.9) | | 177 / 181 | +2.89 (+1.4) | 2.6 | +0.42 (+0.5) | 0.8 | 2.11 / 1.29 | +0.78 (+0.4) | -0.87 (-0.9) | -1.11 | -0.07 / -1.79 | -0.27 / -1.51 | +0.20d / -0.71d | 2/9 |
| POOL-EN (3) | 15 | +2.77 (+2.0) / +3.03 (+2.6) | | 67 / 73 | +7.44 (+1.4) | 2.7 | -3.90 (-1.0) | | 8.55 / 15.32 | -1.11 (-0.2) | -19.23 (-4.5) | | -7.09 / -20.39 | -5.39 / -26.89 | -0.14d / -3.39d | 1/7 |
| info: US500 | 15 | +0.60 (+0.8) / +0.97 (+1.3) | +3.3 / -1.8 | 27 / 25 | +6.11 (+1.2) | 10.3 | -3.57 (-1.3) | | 1.82 / 0.51 | +4.29 (+0.8) | -4.08 (-1.5) | -0.95 | +0.43 / -5.54 | +3.38 / -4.33 | +0.46 / -1.13 | 3/9 |
| info: US500 | 10 | +0.72 (+1.2) / +1.10 (+1.6) | +4.3 / -1.7 | 27 / 25 | +6.14 (+1.6) | 8.6 | -3.13 (-1.2) | | 1.85 / 0.51 | +4.29 (+1.1) | -3.64 (-1.4) | -0.85 | -1.44 / -2.33 | +3.37 / -3.89 | +0.61 / -1.03 | 3/9 |
| info: US2000 | 15 | +1.70 (+2.1) / +0.05 (+0.1) | +1.9 / -1.6 | 27 / 23 | +4.02 (+0.9) | 2.4 | -6.93 (-2.4) | | 2.25 / 1.79 | +1.76 (+0.4) | -8.73 (-3.1) | -4.94 | -0.68 / -9.46 | +0.64 / -9.62 | +0.22 / -2.33 | 4/9 |
| info: US2000 | 10 | +1.74 (+2.5) / +0.87 (+1.2) | +3.5 / -1.7 | 27 / 26 | +3.40 (+0.9) | 2.0 | -2.74 (-1.0) | | 2.26 / 1.79 | +1.13 (+0.3) | -4.53 (-1.6) | -3.99 | -4.37 / -3.50 | +0.00 / -5.42 | +0.17 / -1.21 | 4/9 |

## Dose-response (w = 15)
Mean signed momentum in bp by |z| bin (t in brackets; n per bin is in analyze_out.txt). The bins are 0-0.5, 0.5-1,
1-1.5, 1.5-2, 2-3 and > 3.

| symbol | era | 0-0.5 | 0.5-1 | 1-1.5 | 1.5-2 | 2-3 | > 3 |
|---|---|---|---|---|---|---|---|
| USTEC | IS | +1.06 | +1.65 | -1.84 | +0.66 | -3.84 | **+49.3 (2.4), n 27** |
| USTEC | VAL | +0.05 | +1.36 | +0.99 | +4.57 | **-11.6 (-3.1)** | +8.1, n 6 |
| US30 | IS / VAL > 3 and 2-3 | | | | | -3.6 / -7.0 (-2.0) | +30.1 / -11.2 |
| JP225o | IS | +1.77 (2.4) | +3.53 (3.6) | +7.68 (4.5) | +5.59 | +0.61 | +18.6 |
| JP225o | VAL | -0.01 | +1.17 | +0.55 | -0.10 | +2.19 | +12.8, n 4 |
| DE40 | IS | +0.33 | +1.17 | +1.76 | -1.33 | +1.08 | +25.8 (2.3), n 18 |
| DE40 | VAL | +0.04 | +2.30 (2.5) | +3.19 (3.4) | +0.67 | +5.99 (2.2) | +15.8, n 8 |
| HK50 | IS | -0.29 | -0.29 | -1.37 | -2.28 | -3.68 | -12.6 (reversal) |
| AUS200 | IS / VAL > 3 | | | | | | +30.8 (2.0) / -8.1 |
| pooled 10 symbols (ex XNG) | IS | +1.15 (3.9) | +0.70 | +0.31 | +0.65 | +0.58 | **+21.8 (4.2), n 212** |
| pooled | VAL | +0.56 | +1.00 (2.1) | +1.15 (1.9) | +0.63 | -1.45 | **-2.9, n 81** |

**Gold's dose shape is absent everywhere.**
- Gold had a clean step at 2-3 sd in both eras (+5.3 bp, t 3.5 / 2.6). Here no symbol has a 2-3 bin that is positive
  and significant in both eras.
- The IS "scale-up" is the > 3 bin, which is almost entirely March-April 2020.
- **Without 2020**, the IS top-decile mid is:
  - US30 +1.7 (t 0.7), USTEC -1.8, DE40 -0.1, AUS200 +0.2, JP225o -0.8, US500 -0.2;
  - XTI +12.8 (t 2.0), which nets +6.8 (t 1.1) (checks_out.txt).
- On VAL big days, the US indices **reverse** into the close: USTEC -11.6 bp at 2-3 sd, US30 -7.0.

## Chance (perm.py; 25 counted cells + 4 information cells in a shared null)
| statistic | best observed | null 95 % of max | p |
|---|---|---|---|
| IS mid \|t\|, per-UTC-day sign flip shared by all cells | 3.00, HK50 w15, the **wrong side** (reversal) | 2.89 | 0.038 |
| IS net t, same flips (net null = flipped mid - cost) | +1.93, USTEC w10 (VAL -2.69) | +1.90 | 0.045 |
| VAL net t | +1.81, DE40 w15 | +2.26 | 0.16 |
| uplift t (top decile vs other days, label permutation within symbol-era), IS | +2.25, USTEC w10 | 2.63 | 0.19 |
| uplift t, VAL | +1.32, DE40 w15 | 2.94 | 0.93 |
| max of 25 normals, one-sided / two-sided 95 % | | 2.85 / 3.08 | |

The two IS cells that clear the shared null are a reversal (HK50, the opposite of the predicted side) and a cell whose
VAL is negative (USTEC). Nothing clears it in VAL.

## Random-entry control (random_ctrl.py; only the cells net > 0 in both eras)
Method:
- The days are the same top-decile days as the actual cell.
- On each day, the window ends at a random minute T' in the venue session, at least 15 min from B.
- The side is recomputed from the previous benchmark price to T'-w-1, so there is no look-ahead.
- The hold is the same w minutes, at actual spreads. 500 seeds.

| cell | IS actual / random mean / 90 % | beats | VAL actual / random mean / 90 % | beats |
|---|---|---|---|---|
| DE40 w15 | +1.47 / +2.36 / +4.39 | 28 % | +3.42 / +3.20 / +5.61 | 54 % |
| DE40 w10 | +0.81 / +1.22 / +2.75 | 36 % | +2.65 / +2.07 / +4.37 | 65 % |
| XTI w10 | +4.29 / -1.96 / +3.68 | 91 % | +4.24 / +0.19 / +4.28 | 89 % |

- **DE40's effect is not at the close.** On big days, following the day's direction pays as much at any intraday
  hour. That is trend persistence on high-vol days, not a flow at the benchmark. Its VAL rests on 2022: +17.1 bp, then
  -2.8 in 2023 and -1.7 in 2024.
- XTI w10 nearly passes the random control, but its IS net t is 0.5 and its +1 minute net is +1.3 / +0.1.
- C3 correlation for the three best cells (IS+VAL, information only): DE40 w15 daily +0.010, monthly +0.015; XTI w10
  -0.006 / +0.033; USTEC w10 -0.031 / +0.054.

## Per family
There is one family (P1). The table above has the cell-level numbers; this is how each symbol behaves.
- **Best cell by IS net t:** USTEC w10, +8.20 (t 1.93). Its VAL is -2.69.
- **Best cell net > 0 in both eras:** DE40 w15, +1.47 (t 0.8) / +3.42 (t 1.8). Power is 0.41 / 1.36, and 1.36 is
  the expected HOLD t at the VAL size. It fails the random control.
- **Energies.**
  - XTI's big days are large at mid (+18 bp IS, w15) but lie inside 7.8 bp of cost, and turn negative in VAL.
  - XBR has nothing; its dose bins flip.
  - XNG costs 12 / 40 bp.
  - Round 6's oil-depends-on-2020 caveat repeats: ex 2020, XTI w15 nets +6.8 (t 1.1).
- **US indices.**
  - IS dose slopes are t +3.2 to +4.6, the Baltussen sign. Without 2020 the slope t falls to -0.4..+2.1.
  - In VAL every US slope is negative (-0.1..-1.8), and big days reverse.
  - Decay: VAL / IS net = -0.33..-0.63.
  - Round 12's L6-LETF and round 4's "big days +10 bp" were the same 2020 tail.
- **JP225, TSE close (14:45-15:00).** Nothing: all-days -0.08 / +0.34, top decile +1.1 / -0.0.
- **JP225, OSE futures close (15:00-15:15, after the cash close).**
  - All-days follow-through is +3.4 bp (t 5.6) IS. By year: +4.9, +1.5, +2.5, +2.1, +7.8, +1.8 for 2016-21, then
    +0.5, +0.5, +0.7 for 2022-24.
  - It does not scale with |z| (x1.0), and its cost is 3.1 / 1.9.
  - It is a decayed all-days effect, not a big-day flow. It is post hoc as an all-days cell (the counted cell was the
    top decile), so it is reported, not proposed.
- **UK100.** Flat: all-days +0.8 / +0.4, top decile -0.6 / +0.9, cost 2.4 / 1.7.
- **HK50.** In IS, big days reverse into the 16:10 close: -4.6 bp (t -3.0), dose slope t -3.3, every IS year
  negative. In VAL, +1.7. That is the opposite of the prediction and does not repeat.
- **AUS200.** IS +4.9 (t 1.7) comes from 2020 (+25 bp). VAL -1.1 / -3.4.

## What this says
- **The gold settlement rule does not travel.** On ten venues with LETF or MOC flows, follow-into-the-close on
  top-decile days is a 2020 phenomenon in IS and absent or reversed in VAL. Gold had a dose step at 2-3 sd in both
  eras; that is the feature that made it a DEMO candidate, and it is not seen here.
- **Prior ranking was wrong.** JP225 and USTEC, where LETF AUM is largest, show no big-day scale-up net of 2020. The
  JP225 OSE quarter-hour is the one structural-looking effect: positive in each IS year, at all |z|. It then decayed
  to a fifth after 2021, which is round 12's decay lesson again.
- **US big-day reversal in VAL** (USTEC 2-3 sd: -11.6 bp, t -3.1) fits the post-2022 shift in dealer gamma (0DTE
  options) as a possible cause, but it was not hypothesised. It would need its own pre-registration, on new data.

## Directions that need the user
1. **LETF flow sizes instead of |z|:**
   - daily shares outstanding / AUM of TQQQ/SQQQ, UPRO/SPXU, UDOW/SDOW, TNA/TZA (issuer files);
   - NEXT FUNDS 1570/1357 (Nomura AM daily NAV and units).
   With these, L(L-1) x AUM x r gives the rebalancing size in currency, scaled by the index futures' closing volume.
   This is external non-price data, so it is the user's call. It is the only way left to test the mechanism directly
   rather than through |z|.
2. **JP225 15:00-15:15 Tokyo, all days.** A decayed effect (+3.4 -> +0.6 bp) at 1.2-1.9 bp cost in 2023-24. It is
   not a candidate. Pre-2016 Nikkei futures M1 (a new price series) would show whether 2016-21 was a regime or the
   norm.

## Scripts and outputs (scratchpad r13/P/)
- coverage.py: quote coverage only, run before the hypotheses.
- make_cal.py -> cal_P.json: XNYS, IFEU, XJPX, XETR, XLON, XHKG and XASX from holidays 0.105, plus HK Lunar New
  Year's Eve.
- libp.py, specs.py: helpers and cell specifications.
- p1.py -> rows_P1.pkl: rows for every cell and window.
- analyze.py -> analyze_out.txt, res_P1.pkl: cells, pooled cells, dose bins, years.
- perm.py -> perm_out.txt; random_ctrl.py -> random_out.txt; c3corr.py -> c3corr_out.txt.
- checks.py -> checks_out.txt: gold reproduction, ex-2020, JP225 by year.
- table.py -> table_out.md.
