# Round 28, stream R2: the gold round-level cascade on the minute-only IC symbols

Written 2026-10-17 22:56 UTC (from `date -u`).
- **Declarations.** Every cell was declared in [HYPOTHESES_R2.md](HYPOTHESES_R2.md) at 22:40 UTC, before any return
  was computed: 270 candidate cells, 126 pooled readings, 200 placebo grids per symbol, PRE for seven Dukascopy pairs.
  Addendum 1 (22:47 UTC) records the calibration before any R2 symbol's return was computed.
- **HOLD was never loaded.** IC minute files are cut at ts < 2025-01-01 at load and asserted; tick days are asserted
  < 2025-01-01; Dukascopy is cut at 2016-01-01; the `*_2026` Dukascopy files were never opened.
- **Engine checks.** The vectorised minute engine matches an independent minute-by-minute re-simulation exactly on
  12 symbol-years (0 event, class or repeat mismatches). Hand recomputation of three trades matches to 1e-3 bp.
- **CSV check.** The lead's `pool.py` reproduces this stream's set-level numbers exactly from `trades_R2.csv`.

## Answer
- **The gold rule does not generalise to the minute-only symbols.**
  - At MAJOR round levels, i.e. the gold $50 analogue (FX 0.05, JPY 5 yen, US500 100, DE40 / UK100 500, JP225 / HK50
    1,000, AUS200 100, BTC adaptive), a resting stop just beyond a fresh level shows no continuation over 15-60
    minutes in any class.
  - **The R2 set, primary cell (major, 30 min):**
    - IS: 3,157 trades, net -0.128 sd (t -7.19), -4.63 bp; mid -0.029 sd (t -1.65).
    - VAL: 2,134 trades, net -0.059 sd (t -3.44), -1.63 bp; mid -0.008 sd (t -0.46).
    - Power at the VAL size: -2.67. 0 of 9 years positive. PRE 2004-15 (seven FX pairs): -0.72 bp (t -1.86).
- **No symbol, class or set meets LIVE or DEMO.** All 267 testable cells fail (EURUSD's 3 repeat cells have fewer
  than 10 IS trades).
  - The best IS net t of the 267 is +1.58 (EURUSD up h60), with VAL t -0.24. Only 14 cells are net > 0 in both IS
    and VAL, all with t < 1.7.
  - The best IS mid t (+2.26, BTC super h60) sits at the 88th percentile of the per-day sign-flip null's maximum
    (p95 3.72).
  - **No PREREG_DRAFT_R2.**
- **No dose response.** At the set level, mid at h30 (sd units, IS / VAL):

  | minor | major | super |
  |---|---|---|
  | -0.021 / +0.013 | -0.029 / -0.008 | -0.054 / -0.007 |

  Gold's monotone $10 < $50 <= $100 pattern is absent in every class.
- **The declared side prior fails.** Downward breaks were expected to be stronger in indices and BTC. They are weaker
  or the same (set IS: down -0.056 sd t -2.10, up -0.003).
  - BTC goes the other way: up breaks +14.5 bp mid in IS and +7.6 in VAL; down breaks -10.5 and -5.3.
- **The placebo is beaten only relatively.** The real set beats 88.5 % / 85.5 % / 98.0 % of placebo books (IS / VAL
  / PRE).
  - The reason: placebo levels revert a little more at the fill (placebo book mid median IS -0.051 sd, VAL -0.025,
    against the real -0.029 / -0.008), not a real continuation.
  - Round levels are "less bad" than random levels by ~0.02 sd (~0.5 bp), far below cost.
- **Costs.**

  | | FX, JPY | indices | BTC |
  |---|---|---|---|
  | round trip excluding slippage | 0.7-1.3 bp | 0.7-3.6 bp | 19.4 bp IS / 4.1 bp VAL |
  | slippage | +0.56 bp | +0.7-2.5 bp | +3.8 bp |

  Even with no cost the mid is about 0, so cost is not what fails.

## Calibration of the minute model (AUDUSD, US30 ticks; addendum 1)
Every minute-model order was replayed on IC ticks while the minute rule kept it alive.

| | AUDUSD | US30 |
|---|---|---|
| minute triggers that also trigger on ticks in the same minute | 96.9 % | 98.1 % |
| minute triggers that never trigger on ticks | 0.4 % | 0.1 % |
| slip, tick fill at 250 ms - minute base fill, mean (median, p90) | +0.558 bp (+0.31, +1.65) | +0.837 s60 = +0.50 bp (0.50 s60, 2.7 s60) |
| **bias** (minute mean net - tick mean net, own triggers), h30, all levels / major | **+0.03 / -0.005 bp** | **-0.09 / +0.00 bp** |
| bias h15 / h60, all levels | -0.22 / -0.09 | -0.01 / -0.09 |

- **The slip unit for FX.** IC's FX 60-minute median spread is 0 in 23-64 % of minutes (EURUSD 64 %), so the
  declared spread-unit slip is undefined there and the FX slip is in bp. Indices and BTC use the declared s60 units.
- **The closes-only model** (the m1c PRE reading for AUDUSD and NZDUSD), at h30, all levels / major:

  | reading | bias vs ticks |
  |---|---|
  | (b) close entry, no slip | -0.45 / -1.44 bp (lower bound) |
  | (a) stop + 0.73 bp | +1.08 / +0.68 bp (upper bound) |

- **Comparison with R1.**
  - R1's file (read 22:46 UTC) recommends the close entry for its closes-only bot, whose stop reading is biased up by
    +1.7 to +3.5 bp. On closes only, crossings that reverse inside the minute are invisible.
  - My model reads bar highs and lows, so it sees those crossings. The tick comparison shows no such bias.
  - **I used my own calibration** for OHLC data, and R1's recommended close entry where only closes exist (m1c PRE).
  - My numbers are within the +-0.4 bp band R1 gives for its own minute model under the null.

## Results
Conventions for every table:
- bp per trade, t clustered by the UTC day of the trigger.
- Minute fills have no latency, so L0 = L250 = L1000.
- Placebo = share of the 200 shifted grids (subsampled to the real count) with a lower mean net.
- Power = per-trade net Sharpe x sqrt(1.73 x trades a year).

### Primary cell per symbol: MAJOR levels, 30-minute exit

| symbol | n IS / VAL | mid IS / VAL (t) | **net IS (t)** | **net VAL (t)** | x1.5 IS / VAL | +1 min IS / VAL | years > 0 | VAL/IS | Sharpe IS / VAL | power IS / VAL | placebo IS / VAL | PRE n | PRE mid (t) | PRE net (t) | PRE yrs > 0 | PRE placebo | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 71 / 65 | +1.16 (0.61) / -1.88 (-1.21) | +0.47 (0.25) | -2.52 (-1.62) | +0.42 / -2.54 | -0.07 / -2.64 | 3/9 | -5.40 | +0.029 / -0.201 | +0.13 / -1.23 | 0.99 / 0.10 | 354 | +0.04 (0.05) | -0.61 (-0.71) | 6/12 | 0.67 | fail |
| GBPUSD | 173 / 86 | +1.20 (0.59) / -0.31 (-0.20) | +0.24 (0.12) | -1.11 (-0.71) | +0.06 / -1.20 | +0.62 / -1.94 | 2/9 | -4.57 | +0.009 / -0.076 | +0.06 / -0.54 | 0.97 / 0.41 | - | - | - | - | - | fail |
| USDCAD | 128 / 73 | -0.40 (-0.40) / -0.17 (-0.19) | -1.33 (-1.31) | -0.95 (-1.06) | -1.49 / -1.04 | -0.77 / -0.61 | 4/9 | +0.72 | -0.116 / -0.124 | -0.71 / -0.81 | 0.54 / 0.53 | - | - | - | - | - | fail |
| USDCHF | 94 / 56 | -1.89 (-1.74) / -1.89 (-1.44) | -2.90 (-2.67) | -2.86 (-2.17) | -3.11 / -3.05 | -2.74 / -2.42 | 2/9 | +0.99 | -0.276 / -0.290 | -1.43 / -1.65 | 0.14 / 0.36 | 319 | +1.67 (1.42) | +0.48 (0.41) | 6/12 | 0.95 | fail |
| USDJPY | 98 / 80 | -0.69 (-0.47) / +1.48 (0.97) | -1.47 (-1.00) | +0.74 (0.49) | -1.56 / +0.67 | -0.52 / +0.14 | 3/9 | -0.50 | -0.101 / +0.054 | -0.54 / +0.37 | 0.45 / 0.61 | 232 | -0.31 (-0.28) | -1.18 (-1.04) | 6/12 | 0.29 | fail |
| EURJPY | 123 / 93 | +1.84 (0.88) / +0.44 (0.28) | +0.92 (0.45) | -0.48 (-0.30) | +0.76 / -0.64 | -0.26 / -1.41 | 3/9 | -0.52 | +0.040 / -0.032 | +0.24 / -0.23 | 1.00 / 0.48 | 381 | +1.26 (1.23) | +0.23 (0.22) | 6/12 | 0.92 | fail |
| GBPJPY | 194 / 104 | -1.90 (-1.55) / +2.71 (1.47) | -3.22 (-2.59) | +1.58 (0.86) | -3.58 / +1.32 | -3.09 / +3.04 | 2/9 | -0.49 | -0.186 / +0.084 | -1.39 / +0.65 | 0.00 / 0.99 | 454 | +0.91 (0.87) | -0.41 (-0.39) | 3/12 | 0.79 | fail |
| AUDJPY | 103 / 68 | -0.99 (-0.68) / -2.32 (-1.64) | -2.15 (-1.48) | -3.41 (-2.41) | -2.43 / -3.66 | -2.58 / -3.42 | 1/9 | +1.59 | -0.146 / -0.292 | -0.79 / -1.83 | 0.36 / 0.09 | - | - | - | - | - | fail |
| US500 | 272 / 246 | +0.04 (0.02) / +0.64 (0.49) | -1.79 (-1.25) | -0.10 (-0.08) | -2.70 / -0.48 | -1.01 / -0.07 | 4/9 | +0.06 | -0.076 / -0.005 | -0.67 / -0.06 | 0.91 / 0.70 | - | - | - | - | - | fail |
| DE40 | 289 / 171 | -1.59 (-1.12) / -2.09 (-1.26) | -3.79 (-2.58) | -3.03 (-1.84) | -4.89 / -3.50 | -3.32 / -1.76 | 0/9 | +0.80 | -0.152 / -0.141 | -1.39 / -1.40 | 0.34 / 0.18 | - | - | - | - | - | fail |
| UK100 | 148 / 83 | -4.40 (-1.83) / -0.53 (-0.27) | -7.99 (-3.23) | -3.25 (-1.60) | -9.78 / -4.61 | -6.18 / -1.20 | 1/9 | +0.41 | -0.265 / -0.176 | -1.73 / -1.22 | 0.17 / 0.55 | - | - | - | - | - | fail |
| JP225 | 257 / 211 | +1.58 (0.72) / +0.92 (0.46) | -2.00 (-0.91) | -1.08 (-0.54) | -3.79 / -2.09 | -1.23 / +0.09 | 3/9 | +0.54 | -0.057 / -0.037 | -0.49 / -0.41 | 0.98 / 0.98 | - | - | - | - | - | fail |
| HK50 | 254 / 125 | -2.08 (-1.14) / -0.23 (-0.07) | -5.45 (-3.00) | -3.21 (-1.06) | -7.14 / -4.70 | -2.70 / -0.58 | 2/9 | +0.59 | -0.188 / -0.095 | -1.61 / -0.81 | 0.34 / 0.80 | - | - | - | - | - | fail |
| AUS200 | 527 / 325 | -1.69 (-1.35) / -1.26 (-1.35) | -5.15 (-4.03) | -2.70 (-2.89) | -6.88 / -3.42 | -2.99 / -1.55 | 0/9 | +0.52 | -0.184 / -0.160 | -2.26 / -2.19 | 0.55 / 0.29 | - | - | - | - | - | fail |
| BTCUSD | 426 / 348 | +5.32 (0.95) / +2.30 (0.64) | -14.09 (-2.48) | -1.77 (-0.49) | -23.80 / -3.80 | -3.86 / -2.89 | 2/8 | +0.13 | -0.115 / -0.026 | -1.51 / -0.36 | 1.00 / 0.90 | - | - | - | - | - | fail |
| AUDUSD (PRE only) | - | - | - | - | - | - | - | - | - | - | - | 285 | -0.84 (-0.78) | -1.93 (-1.80); (a) +0.16 | 4/12 | 0.48 | PRE |
| NZDUSD (PRE only) | - | - | - | - | - | - | - | - | - | - | - | 252 | -1.10 (-0.82) | -2.60 (-1.93); (a) +0.07 | 4/12 | 0.86 | PRE |

AUDUSD and NZDUSD IS / VAL belong to R1. Their PRE is the closes-only reading (b) (`minute_close`); (a) is the upper
bracket.

### Classes and the R2 set, major h30
Pooled in sd units: net / the symbol's IS sd of the 30-minute net. [bp] is the raw mean.

| group | n IS / VAL | net IS sd (t) [bp] | net VAL sd (t) [bp] | mid IS / VAL sd (t) | x1.5 IS / VAL | +1 min IS / VAL | years > 0 | power IS / VAL | per-day power IS / VAL | placebo IS / VAL | PRE n | PRE net sd (t) [bp] | PRE placebo | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FX USD pairs | 466 / 280 | -0.080 (-1.75) [-0.79] | -0.125 (-2.79) [-1.75] | -0.018 (-0.40) / -0.071 (-1.58) | -0.091 / -0.132 | -0.063 / -0.121 | 1/9 | -0.92 / -2.19 | -0.94 / -2.14 | 0.905 / 0.275 | 673 | +0.001 (0.02) [-0.10] | 0.960 | fail |
| JPY pairs | 518 / 345 | -0.108 (-2.81) [-1.69] | -0.012 (-0.24) [-0.15] | -0.044 (-1.15) / +0.045 (0.93) | -0.123 / -0.023 | -0.111 / -0.007 | 2/9 | -1.32 / -0.19 | -1.52 / -0.19 | 0.085 / 0.655 | 1067 | -0.024 (-0.68) [-0.35] | 0.800 | fail |
| US500 | 272 / 246 | -0.076 (-1.25) [-1.79] | -0.004 (-0.08) [-0.10] | +0.001 (0.02) / +0.027 (0.49) | -0.114 / -0.020 | -0.043 / -0.003 | 4/9 | -0.67 / -0.06 | -0.67 / -0.06 | 0.915 / 0.730 | - | - | - | fail |
| European indices | 437 / 254 | -0.190 (-3.92) [-5.21] | -0.117 (-2.44) [-3.10] | -0.092 (-1.95) / -0.062 (-1.29) | -0.240 / -0.145 | -0.157 / -0.061 | 0/9 | -2.14 / -1.80 | -2.11 / -1.85 | 0.245 / 0.210 | - | - | - | fail |
| Asian indices | 1038 / 661 | -0.153 (-4.63) [-4.44] | -0.078 (-2.43) [-2.28] | -0.037 (-1.14) / -0.015 (-0.48) | -0.211 / -0.109 | -0.086 / -0.030 | 1/9 | -2.65 / -1.89 | -2.49 / -1.84 | 0.715 / 0.960 | - | - | - | fail |
| BTC | 426 / 348 | -0.115 (-2.48) [-14.09] | -0.014 (-0.49) [-1.77] | +0.043 (0.95) / +0.019 (0.64) | -0.194 / -0.031 | -0.031 / -0.024 | 2/8 | -1.27 / -0.36 | -1.32 / -0.37 | 1.000 / 0.900 | - | - | - | fail |
| **R2 set (15)** | 3157 / 2134 | **-0.128 (-7.19) [-4.63]** | **-0.059 (-3.44) [-1.63]** | -0.029 (-1.65) / -0.008 (-0.46) | -0.172 / -0.080 | -0.085 / -0.038 | 0/9 | -3.87 / -2.67 | -3.86 / -2.63 | 0.885 / 0.855 | 1740 | -0.014 (-0.46) [-0.25] | 0.985 | fail |
| PRE all 7 pairs | - | - | - | - | - | - | - | - | - | - | 2277 | -0.056 (-1.86) [-0.72] | 0.980 | (info) |

The R2 set's other exits: h15 IS -0.14 sd (t -9.0), VAL -0.06 (t -4.7); h60 IS -0.13 (t -5.5), VAL -0.06 (t -2.7).

### Dose and side splits: mid at h30 in sd units (t)

| group | IS minor | IS major | IS super | IS repeat | IS down | IS up | VAL minor | VAL major | VAL super | VAL repeat | VAL down | VAL up |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FX USD pairs | -0.025 (-1.28) | -0.018 (-0.40) | -0.085 (-1.36) | -0.081 (-1.24) | -0.094 (-1.20) | +0.048 (0.91) | -0.005 (-0.16) | -0.071 (-1.58) | -0.090 (-1.33) | -0.028 (-0.26) | -0.053 (-0.88) | -0.092 (-1.37) |
| JPY pairs | +0.049 (1.95) | -0.044 (-1.15) | -0.116 (-2.31) | +0.015 (0.17) | -0.061 (-0.98) | -0.028 (-0.60) | +0.030 (0.98) | +0.045 (0.93) | +0.064 (0.95) | -0.120 (-1.24) | +0.127 (1.44) | -0.030 (-0.66) |
| US500 | +0.061 (0.90) | +0.001 (0.02) | -0.114 (-0.49) | +0.160 (1.32) | +0.033 (0.32) | -0.029 (-0.44) | +0.111 (1.98) | +0.027 (0.49) | +0.182 (1.58) | -0.176 (-1.33) | +0.069 (0.93) | -0.013 (-0.17) |
| European indices | -0.051 (-1.89) | -0.092 (-1.95) | -0.089 (-1.24) | -0.157 (-1.62) | -0.170 (-2.46) | +0.010 (0.17) | -0.012 (-0.43) | -0.062 (-1.29) | -0.084 (-1.06) | -0.146 (-1.61) | -0.127 (-1.57) | -0.014 (-0.24) |
| Asian indices | -0.079 (-2.74) | -0.037 (-1.14) | -0.005 (-0.08) | +0.019 (0.28) | +0.001 (0.03) | -0.078 (-1.62) | +0.021 (0.61) | -0.015 (-0.48) | -0.055 (-0.78) | +0.006 (0.08) | -0.022 (-0.46) | -0.008 (-0.19) |
| BTC | -0.077 (-2.20) | +0.043 (0.95) | +0.147 (1.78) | +0.071 (0.54) | -0.085 (-1.40) | +0.118 (1.89) | -0.023 (-0.76) | +0.019 (0.64) | +0.028 (0.38) | -0.085 (-1.28) | -0.043 (-1.00) | +0.062 (1.57) |
| R2 set | -0.021 (-1.82) | -0.029 (-1.65) | -0.054 (-2.11) | -0.010 (-0.28) | -0.056 (-2.10) | -0.003 (-0.12) | +0.013 (0.88) | -0.008 (-0.46) | -0.007 (-0.23) | -0.069 (-1.81) | -0.006 (-0.21) | -0.010 (-0.46) |
| PRE all 7 | +0.021 (1.25) | +0.021 (0.69) | +0.034 (0.81) | - | +0.034 (0.78) | +0.006 (0.16) | | | | | | |

The PRE row gives PRE values (it has no IS / VAL); its repeat cell is in `out/classes.txt`.

### Net at h30 by cell per symbol, IS / VAL (bp, t)

| symbol | major | super | minor | repeat | down | up | best of 18 by IS net t (VAL t) |
|---|---|---|---|---|---|---|---|
| EURUSD | +0.47 (0.25) / -2.52 (-1.62) | -2.14 (-1.44) / -2.10 (-0.98) | -0.96 (-2.21) / +0.00 | +2.39 (0.84) / -1.62 (-0.38) | -2.10 (-1.23) / -3.90 (-1.85) | +3.59 (0.99) / -0.58 (-0.25) | up h60: +1.58 (-0.24) |
| GBPUSD | +0.24 (0.12) / -1.11 (-0.71) | -0.05 / +1.02 (0.39) | -0.82 (-1.46) / -1.25 (-1.33) | -3.90 (-1.88) / -2.09 (-0.81) | +0.41 (0.10) / -2.67 (-1.46) | +0.10 (0.07) / +1.42 (0.51) | down h60: +0.24 (+0.25) |
| USDCAD | -1.33 (-1.31) / -0.95 (-1.06) | -0.79 / -2.06 | -1.29 (-2.78) / -1.27 (-2.42) | -0.22 / +3.72 (1.62) | -1.78 / +0.46 | -0.93 / -2.49 (-2.32) | repeat h60: +1.10 (+1.35) |
| USDCHF | -2.90 (-2.67) / -2.86 (-2.17) | -4.18 (-3.91) / -3.61 (-2.18) | -1.82 (-3.11) / -0.88 | -4.62 (-3.39) / -4.53 | -5.48 (-3.00) / -1.16 | -1.07 / -3.96 (-2.43) | minor h60: -0.73 (-1.02) |
| USDJPY | -1.47 (-1.00) / +0.74 (0.49) | -3.35 (-2.17) / +0.85 | +0.01 / +1.06 (0.95) | -2.60 / -2.20 | -2.62 / +1.09 | -0.33 / +0.49 | minor h60: +0.79 (+1.24) |
| EURJPY | +0.92 (0.45) / -0.48 (-0.30) | -1.26 / +1.29 | -0.61 / +0.15 | -1.97 / +0.23 | +2.98 (0.78) / -0.87 | -1.04 / -0.19 | major h15: +0.88 (-1.08) |
| GBPJPY | -3.22 (-2.59) / +1.58 (0.86) | -4.40 (-2.56) / +1.00 | -0.29 / -0.73 | -0.87 / -4.54 | -3.80 / +4.74 (1.64) | -2.64 / -2.72 | repeat h60: -0.07 (-0.01) |
| AUDJPY | -2.15 (-1.48) / -3.41 (-2.41) | -1.58 / -3.06 | -0.04 / -2.51 (-2.72) | +2.70 / -5.48 | -3.00 / -2.92 | -1.17 / -3.82 (-2.06) | repeat h60: +1.18 (-3.59) |
| US500 | -1.79 (-1.25) / -0.10 (-0.08) | -4.72 / +3.57 (1.31) | -0.40 / +1.87 (1.41) | +1.99 / -4.76 (-1.52) | -1.09 / +0.88 | -2.47 / -1.04 | repeat h60: +1.56 (-1.08) |
| DE40 | -3.79 (-2.58) / -3.03 (-1.84) | -2.70 / -2.63 | -2.57 (-2.90) / -0.46 | -6.41 (-2.22) / -5.04 | -6.19 (-2.92) / -4.26 | -0.89 / -2.22 | up h60: +0.46 (-0.54) |
| UK100 | -7.99 (-3.23) / -3.25 (-1.60) | -9.31 (-2.35) / -7.14 (-2.14) | -6.94 (-6.38) / -5.23 (-4.52) | -8.38 / -7.02 (-3.58) | -8.65 (-2.30) / -6.15 (-2.65) | -6.99 (-2.76) / -0.55 | repeat h30: -1.60 (-3.58) |
| JP225 | -2.00 (-0.91) / -1.08 (-0.54) | +1.89 / -7.17 | -6.02 (-3.93) / -0.22 | +3.37 / -5.93 | -2.12 / -2.80 | -1.87 / +0.81 | repeat h30: +0.60 (-1.21) |
| HK50 | -5.45 (-3.00) / -3.21 (-1.06) | -6.41 / -1.27 | -5.27 (-2.77) / +1.44 | +0.16 / +10.68 (1.65) | -6.22 (-2.26) / -4.74 | -4.65 (-1.96) / -1.59 | repeat h30: +0.04 (+1.65) |
| AUS200 | -5.15 (-4.03) / -2.70 (-2.89) | -4.32 / -4.24 (-2.11) | -5.87 (-5.14) / -3.03 (-3.48) | -6.08 (-2.58) / -3.25 | -2.70 / -1.67 | -7.63 (-4.56) / -3.94 (-3.75) | down h30: -1.42 (-1.14) |
| BTCUSD | -14.09 (-2.48) / -1.77 (-0.49) | -0.73 / -0.94 | -26.07 (-5.84) / -7.25 (-1.97) | -12.26 / -13.98 | -33.57 (-4.46) / -9.73 (-1.83) | -2.73 / +3.72 (0.77) | super h60: +0.76 (+0.43) |

### PRE 2004-15 (Dukascopy, minute level, labelled): net bp at h30 (t) [mid]
The five m1 pairs use the OHLC model with IC 2016-17 modelled spreads + 0.558 bp slip. AUDUSD and NZDUSD use
closes-only reading (b).

| pair | major | super | minor | repeat | down | up |
|---|---|---|---|---|---|---|
| EURUSD | -0.61 (-0.71) [+0.04] | +0.06 (0.05) [+0.71] | -0.15 (-0.41) [+0.50] | +0.96 (0.59) [+1.63] | -1.68 (-1.58) [-1.02] | +0.69 (0.50) [+1.35] |
| USDJPY | -1.18 (-1.04) [-0.31] | -1.38 (-0.95) [-0.51] | +0.19 (0.27) [+1.06] | -0.82 (-0.41) [+0.06] | -1.67 (-0.93) [-0.81] | -0.71 (-0.50) [+0.16] |
| USDCHF | +0.48 (0.41) [+1.67] | -0.38 (-0.23) [+0.81] | -0.58 (-1.04) [+0.62] | +2.51 (1.04) [+3.71] | -0.92 (-0.51) [+0.28] | +1.89 (1.26) [+3.08] |
| EURJPY | +0.23 (0.22) [+1.26] | -0.00 [+1.02] | -0.40 (-0.78) [+0.63] | -0.32 (-0.17) [+0.71] | +1.66 (0.96) [+2.68] | -1.30 (-1.23) [-0.26] |
| GBPJPY | -0.41 (-0.39) [+0.91] | +0.33 (0.22) [+1.65] | -0.79 (-1.76) [+0.53] | -0.55 (-0.29) [+0.77] | +1.63 (0.98) [+2.94] | -2.75 (-2.37) [-1.43] |
| AUDUSD (b) | -1.93 (-1.80) [-0.84] | -1.22 (-0.70) [-0.12] | -1.29 (-2.35) [-0.20] | -1.92 (-0.82) [-0.82] | -1.33 (-0.92) [-0.24] | -2.52 (-1.58) [-1.43] |
| NZDUSD (b) | -2.60 (-1.93) [-1.10] | -1.84 (-0.90) [-0.35] | -2.25 (-3.82) [-0.74] | +0.03 (0.01) [+1.53] | -2.08 (-1.17) [-0.58] | -3.20 (-1.54) [-1.70] |

- **PRE carries a small positive mid at round levels in the five m1 pairs.** Pooled mid at major levels is +0.053 sd
  (t 1.67), and +0.041 (t 2.41) at minor levels. The per-pair major mids run from -0.31 to +1.67 bp, all with
  t < 1.5: below cost, and gone in 2016-24.
- **No dose response in PRE either.** Major ~ minor ~ super.
- Gold's PRE (round 27: +5.35 bp, t 3.12 at $50 levels) has no counterpart here.

## Cells tried and chance (out/chance.txt)
- **Cells.** K = 267 testable candidate cells (270 declared; EURUSD's 3 repeat cells have 8 IS trades). IS mid > 0
  in 106; IS net > 0 in 46; IS and VAL net > 0 in 14; DEMO 0, LIVE 0.
- **Best readings.**
  - Best IS net t: +1.58 (EURUSD up h60; VAL -0.24).
  - Best IS mid t: +2.26 (BTC super h60).
  - Largest |IS mid t|: -4.35 (UK100 minor h15: a reversal, the opposite side; VAL -2.87).
- **Chance benchmarks.**
  - Max |t| of 267 independent normals: p50 3.01, p95 3.73.
  - Per-day sign-flip null (1,000 draws, shared by all cells): max IS mid t p50 2.72, p95 3.72. The best observed
    +2.26 is exceeded by 88 % of draws.
- **The verdict holds against chance.** The continuation side shows nothing beyond chance. The one beyond-chance
  reading, UK100 minor, is a fade, not the declared side.

## Fill diagnostics (major and all triggers; out/fill_diag.md)
| symbol | slip applied, median bp | entry gapped past the stop at the bar open | exit bar missing (fallback used) | exit capped at 16:54 NY | cost = mid - net, major h30, IS / VAL bp |
|---|---|---|---|---|---|
| FX and JPY pairs | +0.56 | 0.6-1.8 % | <= 0.2 % | 0.4-1.4 % | 0.63-1.32 |
| US500 / DE40 / UK100 | +1.05 / +0.69 / +1.59 | 3.9-5.1 % | 2.8-4.0 % | <= 0.8 % | 1.82 / 0.74; 2.20 / 0.94; 3.58 / 2.72 |
| JP225 / HK50 / AUS200 | +2.48 / +2.50 / +1.47 | 8.1 / 1.4 / 17.5 % | 5.3 / 8.1 / 11.4 % | <= 0.4 % | 3.58 / 2.01; 3.37 / 2.98; 3.46 / 1.44 |
| BTCUSD | +3.79 | 10.5 % | 0.4 % | 1.2 % | 19.41 / 4.07 |

- **The cost column** excludes the slip, which sits inside the mid as measured at the fill (round 27's convention).
- **Exit fallbacks** at AUS200 and HK50 come from their session breaks. A fallback uses the next bar within 10
  minutes, else the last bar before.
- **The largest trades** come from the Brexit-referendum night (2016-06-24: GBPUSD +303 bp, EURJPY +215, UK100 -243,
  JP225 -146) and March 2020. They inflate GBPUSD's IS sd (26.7 bp).

## Per-trade CSV for the lead
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/R2/trades_R2.csv`:
- 1,561,829 rows, 175 MB, in the BRIEF's columns.
- **Real rows**, 33,944 in all: major 7,568, super 2,934, minor 22,151, repeat 1,291.
  - Eras IS / VAL for the 15 symbols, PRE for the seven pairs.
  - All at the 30-minute exit.
  - A super or repeat trade appears again under its own cell name.
- **Placebo rows** (placebo_0..199, major cell): 1,527,885, all eras.
- **Fill column.**
  - The three latency columns carry the same minute value.
  - fill = `minute`, or `minute_close` for the AUDUSD / NZDUSD PRE rows.
  - Those PRE rows use my IC-minute IS sd (AUDUSD 12.2, NZDUSD 11.3 bp). The lead may prefer R1's tick sd.
- **sd_is_30min** (bp; IS major 30-minute net sd):

  | EURUSD | GBPUSD | USDCAD | USDCHF | USDJPY | EURJPY | GBPJPY | AUDJPY |
  |---|---|---|---|---|---|---|---|
  | 15.96 | 26.70 | 11.44 | 10.54 | 14.49 | 22.90 | 17.32 | 14.75 |

  | US500 | DE40 | UK100 | JP225 | HK50 | AUS200 | BTCUSD |
  |---|---|---|---|---|---|---|
  | 23.65 | 24.95 | 30.09 | 35.35 | 29.01 | 28.04 | 122.87 |

  Every symbol has >= 71 IS major trades, so no fallback was used.
- **Check.** `r28/lead/pool.py` on this file alone (an empty R1 file) gives:
  - BOOK IS -0.128 sd (t -7.19), VAL -0.059 (t -3.45), PRE -0.056 (t -1.86);
  - placebo beaten 0.885 / 0.855 / 0.980.

## Needs the user
- Nothing for this stream's verdict.
- IC ticks for EURUSD, GBPUSD, USDJPY and the crosses would remove the minute model. The calibration bias is about
  +-0.2 bp against a set mid of about 0 and costs of 1-4 bp, so they would not change the answer. Not recommended for
  this mechanism.

## Untested ideas (not declared, so not candidates)
- **Fading minor index levels.** UK100 100-point levels reverse at 15-30 minutes in both eras: mid IS -2.96 bp
  (t -4.35), VAL -2.47 (t -2.87). AUS200 50-point levels do the same: IS -3.06 (t -4.24), VAL -1.27 (t -2.01). Ideas
  this suggests:
  - a resting limit fade at minor index levels (round 27 G2-style), declared on fresh data;
  - checking whether it survives IC's 1.4-3.5 bp round trip and limit-fill adverse selection (round 27 G2 found the
    gold fade run over).
- **BTC upward breaks of major / super levels.** Mid IS +14.5 bp (t 1.89) and VAL +7.6 (t 1.57) at h30, against a
  2016-21 round trip of ~19 bp. The VAL-era cost (4 bp) is close. This is post hoc, and the side contradicts the
  declared prior.
- **First-minute reversal after the stop fill.** The +1-minute variant is less negative than the stop fill in most
  index and BTC cells (set IS -0.085 vs -0.128 sd). The minute right after a stop triggers at a round level tends to
  give back. That is the opposite of gold's fast cascade.

## Scripts and outputs
Scripts are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/R2/code/`
and outputs in `.../r28/R2/out/`. Round 27 G's code is copied in `code/r27G_ref/`. Run them from the repo root with
`PYTHONPATH=. research/.venv/bin/python <script>`.

| script | what it does |
|---|---|
| common.py | constants of the declared rule, HOLD guards, calendar, NY clock, clustered t, power |
| mdata.py | dense minute arrays (IC m1, closes-only, Dukascopy m1 / m1c, modelled PRE spreads), exclusions, 16:54 NY cap, BTC monthly spacing -> `cache/` |
| engine.py | the declared bot on a level lattice (real / placebo), candidate-driven forward search |
| fills.py | minute fill model (stop / open-gap entry + slip, bar-close exits, x1.5, +1 minute, closes-only readings) |
| test_engine.py | synthetic tests (all pass) |
| brute.py | independent minute-by-minute re-simulation (12 symbol-years, 0 mismatches) |
| spacings.py, count_events.py, count_tables.py, check_masks.py | prices-only checks and the declared counts -> `out/spacings.txt`, `out/counts.txt` |
| tick_calib.py, calib_analyze.py | tick replay of every minute order (AUDUSD, US30, AUDUSD closes) -> `out/calibration.txt` |
| run_sym.py | real + 200 placebo lattices per symbol / source -> `out/real_*.npz`, `out/plc_*.npz` |
| analyze.py | every cell, placebo shares, pooled classes, chance, verdicts, the CSV -> `out/cells.txt`, `out/classes.txt`, `out/chance.txt`, `trades_R2.csv` |
| stream_tables.py | the tables above -> `out/stream_tables.md`; `out/fill_diag.md` |
