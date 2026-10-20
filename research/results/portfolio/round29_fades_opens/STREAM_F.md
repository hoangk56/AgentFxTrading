# Round 29, stream F: fading a fresh minor round level on the European index CFDs no round had used

Written 2026-10-18 01:10 UTC (from `date -u`).
- **Declarations.** Rule, spacings, spread model, cells (24 candidates + 6 book readings), controls, bars and the
  prices-only event counts were declared in [HYPOTHESES_F.md](HYPOTHESES_F.md) at 01:00 UTC, before any return was
  computed. Nothing was added afterwards except the diagnostics marked "information" below.
- **HOLD was never loaded.** zbars file names were filtered to < `20250101` before any file was opened and every bar
  was asserted < 2025-01-01; the seen symbols use round 28 R2's caches (cut at load); no CSV row is dated 2025 or later.
- **Engine and fill checks.**
  - R2's synthetic tests pass unchanged; the new `test_fade.py` (fade sides and prices, x1.5, +1 minute, limit
    trade-through, gap fill, buy-limit ask low, tick array, random-entry side, spread model) passes.
  - An independent minute-by-minute re-simulation (`brute_f.py`) on 11 symbol-years, stop and limit modes, real and
    placebo lattices: 0 event, class or repeat mismatches.
  - Six trades (ES35, STOXX50) recomputed by hand from the raw zbars and the declared spread table: equal to 1e-4 bp.
  - Round 28 reproduced: the seen symbols' minor-cell trigger counts equal R2's, and R2's UK100 minor numbers come out
    exactly (stop-side mid h15 -2.96 bp, t -4.35; net h30 -6.94, t -6.38 IS / -5.23, t -4.52 VAL).
- **One fix after the first run:** the +1-minute entry inherited R2's fallback, which could land on a missing
  16:53 NY cap bar. That made the +1-minute readings of 1 real DE40 limit trade (its three exits) and 348 placebo
  readings NaN. It now uses the last present bar, as the exit rule does. The fix only turned those NaN readings into
  numbers; every other number is unchanged.

## Answer
- **The fade does not pay. No symbol, cell or book meets LIVE or DEMO. No PREREG_DRAFT_F.**
- **The confirmatory book** (ES35, F40, IT40, STOXX50 at equal risk; primary cell = market fade at the trigger
  close, 30-minute exit):

  | era | trades | net | net bp | mid |
  |---|---|---|---|---|
  | IS | 1,779 | -0.124 sd (t -4.96) | -3.60 | +0.047 sd (t 1.90) |
  | VAL | 1,126 | -0.113 sd (t -3.86) | -3.25 | +0.025 sd (t 0.85) |

  - 0 / 9 years net > 0.
  - Power -2.80 IS / -3.22 VAL (per day -2.61 / -2.89).
  - x1.5: -0.209 / -0.181 sd. +1 minute: -0.116 / -0.115 sd.
- **The reversion exists but is far below cost.**
  - After the trigger close the price comes back +1.24 bp in IS and +0.65 bp in VAL by 30 minutes, and +2.44 / +1.80
    bp by 60 minutes.
  - The market fade's round trip on these CFDs is 4.84 bp (IS) / 3.90 bp (VAL).
  - Even at zero cost the best cell (60 minutes) has power 1.46 IS / 1.38 VAL. No cheaper venue makes this LIVE.
- **Controls.**
  - Relative to shifted grids and random times, round levels revert about 1 bp more. The book beats 89 % / 99 % of the
    placebo books (IS / VAL) and 97.5 % / 87 % of the random-entry books.
  - That is the same "less bad than random levels" pattern round 28 found, and it is too small to trade.
- **Every candidate cell fails.**
  - None of the 24 candidate cells has IS net > 0. The best IS net t is -0.39 (STOXX50, limit, 60 minutes).
  - The best IS mid t is +2.59 (F40, market, 15 minutes). The per-day sign-flip null beats it in 7.5 % of draws
    (p95 2.69), so it is within chance.
- **The limit fade is worse.**
  - Book, 30 minutes: IS -0.175 sd (t -5.72), VAL -0.111 sd (t -3.49).
  - Mid -0.011 / +0.021 sd. The limit fills only when the price runs through it (adverse selection).
- **US2000 control: no fade, as predicted.**
  - Fade mid -0.05 / -0.30 bp. Net -2.67 bp (t -3.37) IS, -2.45 bp (t -2.59) VAL.
  - The continuation side loses too: -3.96 / -3.30 bp.
- **Seen symbols (information).**
  - Faded from the trigger close, round 28's six index symbols have mid -0.003 sd in IS and -0.041 sd (t -1.87) in
    VAL.
  - In VAL, JP225, HK50 and US500 continue rather than revert.
- **Why round 28 saw a reversion (information; the motivation of this stream).**
  - R2's minor-level "reversion" is almost entirely the calibrated stop slip (0.837 x s60, from US30 ticks), which
    R2's mid convention puts inside the mid.
  - UK100, IS, 15 minutes: of R2's -2.96 bp, -2.87 is that slip. The price itself closes the trigger minute 0.68 bp
    beyond the level and is back at the level after 15 minutes.
  - Scaling the slip with IC's wide CFD spreads may overstate it (2.9 bp at UK100 against 0.5 bp at US30).
  - Round 28's verdict (no continuation) still stands. At the MAJOR levels of the same six symbols, measured from the
    level, the price continues only +1.35 bp (IS) / +0.88 bp (VAL) at 30 minutes. That is below their 2-3 bp round
    trip even with no slip at all.
- **No rule reached DEMO or LIVE numbers, so the C3 correlation was not computed.** The C3 file exists.

## Results (bp a trade; t clustered by the UTC day of the trigger)
Conventions for every table:
- Minute fills: market fade = enter at the trigger bar's close, exit at the close h bars later. Limit fade = fill at
  the limit after a trade-through by one tick.
- **Placebo** = share of the 200 shifted grids (R2's draws, full rule, fade side) with a lower mean net; per symbol
  subsampled to the real count.
- **Random** = share of the 200 random-entry seeds with a lower mean net. Each seed draws the same era, UTC weekday
  and UTC hour; the side comes from the fresh-extreme rule at the random minute.
- **Power** = per-trade net Sharpe x sqrt(1.73 x trades a year).

### Primary cell per symbol: market fade, 30-minute exit
| symbol | n IS / VAL | mid IS / VAL (t) | **net IS (t)** | **net VAL (t)** | x1.5 IS / VAL | +1 min IS / VAL | years > 0 | VAL/IS | Sharpe IS / VAL | power IS / VAL (per day) | placebo IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ES35 | 679 / 330 | +0.86 (0.77) / +1.18 (0.98) | -4.36 (-3.93) | -3.87 (-3.21) | -6.97 / -6.39 | -3.81 / -3.58 | 0/9 | 0.89 | -0.153 / -0.170 | -2.14 / -2.34 (-2.11 / -2.44) | 0.940 / 1.000 | 0.800 / 0.920 | fail |
| F40 | 528 / 399 | +2.43 (2.16) / +1.05 (0.79) | -1.92 (-1.71) | -1.93 (-1.44) | -4.09 / -3.42 | -1.37 / -2.81 | 2/9 | 1.01 | -0.073 / -0.074 | -0.91 / -1.12 (-0.92 / -1.09) | 0.925 / 0.975 | 0.985 / 0.830 | fail |
| IT40 | 216 / 165 | -1.20 (-0.48) / -0.71 (-0.33) | -5.55 (-2.25) | -3.95 (-1.86) | -7.72 / -5.58 | -5.95 / -3.61 | 0/9 | 0.71 | -0.150 / -0.140 | -1.18 / -1.37 (-1.21 / -1.41) | 0.285 / 0.440 | 0.295 / 0.420 | fail |
| STOXX50 | 356 / 232 | +1.68 (1.20) / +0.15 (0.09) | -3.48 (-2.50) | -4.14 (-2.52) | -6.06 / -6.28 | -4.09 / -3.49 | 0/9 | 1.19 | -0.126 / -0.166 | -1.28 / -1.92 (-1.34 / -1.91) | 0.455 / 0.595 | 0.855 / 0.495 | fail |
| US2000 (control) | 1540 / 1032 | -0.05 (-0.06) / -0.30 (-0.32) | -2.67 (-3.37) | -2.45 (-2.59) | -3.99 / -3.53 | -2.44 / -2.35 | 0/9 | 0.92 | -0.087 / -0.080 | -1.83 / -1.96 (-1.81 / -1.96) | 0.660 / 0.050 | 0.625 / 0.370 | fail |
| UK100 (seen) | 585 / 270 | +1.28 (1.21) / +1.06 (0.93) | -2.11 (-1.99) | -1.19 (-1.04) | -3.80 / -2.32 | -2.21 / -1.53 | 1/9 | 0.57 | -0.078 / -0.065 | -1.01 / -0.81 | 0.865 / 0.985 | 0.895 / 0.820 | fail |
| AUS200 (seen) | 573 / 311 | +0.24 (0.21) / +0.86 (0.97) | -3.13 (-2.71) | -0.57 (-0.64) | -4.82 / -1.29 | -2.52 / -1.40 | 1/9 | 0.18 | -0.128 / -0.036 | -1.65 / -0.48 | 0.555 / 0.810 | 0.595 / 0.805 | fail |
| DE40 (seen) | 1126 / 722 | -0.53 (-0.62) / -0.80 (-0.83) | -2.68 (-3.12) | -1.75 (-1.82) | -3.76 / -2.23 | -2.64 / -1.72 | 1/9 | 0.65 | -0.094 / -0.069 | -1.70 / -1.41 | 0.065 / 0.020 | 0.235 / 0.075 | fail |
| JP225 (seen) | 307 / 224 | +0.30 (0.20) / -3.46 (-1.74) | -3.27 (-2.21) | -5.48 (-2.76) | -5.05 / -6.49 | -3.59 / -5.98 | 1/9 | 1.68 | -0.126 / -0.185 | -1.19 / -2.10 | 0.725 / 0.000 | 0.635 / 0.010 | fail |
| HK50 (seen) | 265 / 135 | -0.16 (-0.08) / -5.49 (-1.58) | -3.46 (-1.80) | -8.45 (-2.42) | -5.11 / -9.93 | -4.64 / -7.16 | 0/9 | 2.44 | -0.111 / -0.208 | -0.97 / -1.83 | 0.735 / 0.000 | 0.465 / 0.040 | fail |
| US500 (seen) | 300 / 264 | -2.17 (-1.33) / -2.93 (-2.26) | -4.03 (-2.47) | -3.69 (-2.84) | -4.95 / -4.07 | -3.97 / -3.69 | 0/9 | 0.92 | -0.142 / -0.174 | -1.32 / -2.14 | 0.000 / 0.000 | 0.010 / 0.010 | fail |

### All six declared cells per symbol: net IS (t) / net VAL (t) [mid IS / VAL]
| symbol | mkt 15 | mkt 30 | mkt 60 | lim 15 | lim 30 | lim 60 |
|---|---|---|---|---|---|---|
| ES35 | -4.80 (-5.81) / -4.90 (-4.98) [+0.36 / +0.08] | -4.36 (-3.93) / -3.87 (-3.21) [+0.86 / +1.18] | -3.25 (-2.34) / -3.03 (-1.74) [+2.07 / +2.10] | -6.83 (-6.63) / -4.44 (-4.06) [-1.79 / +0.39] | -6.94 (-5.14) / -4.17 (-2.91) [-1.84 / +0.70] | -5.39 (-3.18) / -3.23 (-1.46) [-0.19 / +1.71] |
| F40 | -1.94 (-2.13) / -2.34 (-2.32) [+2.37 / +0.64] | -1.92 (-1.71) / -1.93 (-1.44) [+2.43 / +1.05] | -3.03 (-1.79) / +0.19 (0.11) [+1.39 / +3.22] | -1.55 (-1.42) / -2.40 (-2.32) [+2.44 / +0.51] | -1.68 (-1.19) / -1.61 (-1.19) [+2.36 / +1.30] | -3.00 (-1.51) / -0.07 (-0.04) [+1.12 / +2.89] |
| IT40 | -4.37 (-2.55) / -3.10 (-2.04) [-0.03 / +0.14] | -5.55 (-2.25) / -3.95 (-1.86) [-1.20 / -0.71] | -1.39 (-0.52) / -2.96 (-0.99) [+2.96 / +0.29] | -5.79 (-3.47) / -2.96 (-1.87) [-1.47 / +0.27] | -7.39 (-2.83) / -4.64 (-2.04) [-3.07 / -1.42] | -4.34 (-1.60) / -3.67 (-1.14) [-0.02 / -0.45] |
| STOXX50 | -3.89 (-3.94) / -3.79 (-3.15) [+1.20 / +0.45] | -3.48 (-2.50) / -4.14 (-2.52) [+1.68 / +0.15] | -0.81 (-0.46) / -4.40 (-1.92) [+4.42 / -0.02] | -4.02 (-3.23) / -3.81 (-2.54) [+0.91 / +0.25] | -5.63 (-3.13) / -3.82 (-2.03) [-0.65 / +0.29] | -0.88 (-0.39) / -4.78 (-1.86) [+4.19 / -0.61] |
| US2000 | -3.02 (-5.05) / -2.48 (-3.62) [-0.39 / -0.31] | -2.67 (-3.37) / -2.45 (-2.59) [-0.05 / -0.30] | -2.66 (-2.54) / -2.34 (-1.85) [-0.02 / -0.18] | -3.58 (-5.10) / -3.79 (-5.07) [-0.97 / -1.64] | -3.43 (-3.84) / -4.01 (-3.92) [-0.84 / -1.87] | -3.61 (-3.11) / -4.38 (-3.17) [-1.01 / -2.23] |
| UK100 | -2.68 (-4.00) / -1.70 (-2.03) [+0.69 / +0.55] | -2.11 (-1.99) / -1.19 (-1.04) [+1.28 / +1.06] | -1.68 (-1.37) / -1.90 (-1.28) [+1.71 / +0.33] | -2.61 (-3.31) / -2.15 (-2.24) [+0.40 / -0.08] | -1.65 (-1.37) / -1.97 (-1.43) [+1.36 / +0.09] | -1.40 (-1.00) / -3.01 (-1.89) [+1.60 / -0.95] |
| AUS200 | -2.58 (-3.75) / -0.86 (-1.32) [+0.80 / +0.54] | -3.13 (-2.71) / -0.57 (-0.64) [+0.24 / +0.86] | -1.69 (-1.11) / -1.23 (-1.04) [+1.81 / +0.20] | -3.42 (-3.74) / -1.15 (-1.70) [-0.56 / +0.16] | -2.91 (-2.25) / -1.38 (-1.55) [-0.05 / -0.03] | -1.87 (-1.04) / -1.31 (-1.05) [+1.12 / +0.04] |
| DE40 | -2.08 (-3.44) / -0.84 (-1.30) [+0.09 / +0.11] | -2.68 (-3.12) / -1.75 (-1.82) [-0.53 / -0.80] | -2.07 (-1.94) / -2.17 (-1.82) [+0.09 / -1.21] | -3.03 (-4.82) / -1.48 (-2.23) [-1.13 / -0.63] | -3.69 (-4.03) / -1.97 (-2.21) [-1.80 / -1.12] | -2.64 (-2.32) / -2.91 (-2.47) [-0.73 / -2.05] |
| JP225 | -4.22 (-4.02) / -4.61 (-3.35) [-0.61 / -2.61] | -3.27 (-2.21) / -5.48 (-2.76) [+0.30 / -3.46] | -5.42 (-2.56) / -4.86 (-1.50) [-1.87 / -2.82] | -5.75 (-4.77) / -5.20 (-3.34) [-2.20 / -3.25] | -4.85 (-2.88) / -6.82 (-3.12) [-1.33 / -4.84] | -5.70 (-2.30) / -6.06 (-1.68) [-2.17 / -4.06] |
| HK50 | -4.46 (-2.92) / -9.10 (-3.20) [-1.15 / -6.16] | -3.46 (-1.80) / -8.45 (-2.42) [-0.16 / -5.49] | -4.84 (-1.97) / -9.62 (-2.02) [-1.52 / -6.67] | -4.91 (-2.91) / -10.05 (-3.31) [-1.65 / -7.17] | -4.78 (-2.23) / -9.08 (-2.41) [-1.51 / -6.19] | -4.83 (-1.83) / -11.11 (-2.24) [-1.56 / -8.22] |
| US500 | -3.08 (-2.63) / -2.12 (-2.06) [-1.22 / -1.37] | -4.03 (-2.47) / -3.69 (-2.84) [-2.17 / -2.93] | -4.69 (-2.32) / -4.04 (-2.06) [-2.84 / -3.29] | -3.61 (-2.81) / -2.83 (-2.73) [-1.78 / -2.09] | -3.39 (-2.01) / -4.62 (-3.33) [-1.57 / -3.88] | -4.51 (-2.02) / -4.56 (-2.22) [-2.68 / -3.83] |

Controls of the candidate cells (placebo IS / VAL; random IS / VAL):

| symbol | mkt 15 | mkt 30 | mkt 60 | lim 15 | lim 30 | lim 60 |
|---|---|---|---|---|---|---|
| ES35 | 0.93 / 0.95; 0.73 / 0.62 | 0.94 / 1.00; 0.80 / 0.92 | 0.92 / 1.00; 0.92 / 0.97 | 0.37 / 0.99; 0.01 / 0.73 | 0.33 / 1.00; 0.01 / 0.75 | 0.30 / 1.00; 0.39 / 0.88 |
| F40 | 1.00 / 0.67; 1.00 / 0.82 | 0.93 / 0.97; 0.98 / 0.83 | 0.59 / 1.00; 0.84 / 0.97 | 1.00 / 0.81; 1.00 / 0.76 | 0.96 / 1.00; 0.97 / 0.87 | 0.68 / 1.00; 0.75 / 0.96 |
| IT40 | 0.52 / 0.53; 0.56 / 0.65 | 0.28 / 0.44; 0.29 / 0.42 | 0.62 / 0.70; 0.86 / 0.56 | 0.32 / 0.63; 0.16 / 0.66 | 0.12 / 0.42; 0.06 / 0.29 | 0.32 / 0.67; 0.45 / 0.51 |
| STOXX50 | 0.67 / 0.41; 0.82 / 0.66 | 0.46 / 0.59; 0.85 / 0.49 | 0.77 / 0.35; 0.97 / 0.38 | 0.81 / 0.50; 0.74 / 0.56 | 0.21 / 0.73; 0.34 / 0.54 | 0.80 / 0.40; 0.96 / 0.30 |
| US2000 | 0.13 / 0.05; 0.28 / 0.34 | 0.66 / 0.05; 0.62 / 0.37 | 0.01 / 0.02; 0.69 / 0.40 | 0.23 / 0.00; 0.07 / 0.00 | 0.55 / 0.00; 0.19 / 0.01 | 0.02 / 0.00; 0.27 / 0.01 |

### The book and other pooled sets (equal risk, sd units; [bp] = raw mean)
Each symbol's IS sd of the 30-minute market-fade net, used as its risk unit:

| ES35 | F40 | IT40 | STOXX50 | US2000 | UK100 | AUS200 | DE40 | JP225 | HK50 | US500 |
|---|---|---|---|---|---|---|---|---|---|---|
| 28.45 | 26.11 | 37.06 | 27.65 | 30.80 | 27.01 | 24.39 | 28.50 | 25.86 | 31.30 | 28.40 |

| set, cell | n IS / VAL | **net IS (t) [bp]** | **net VAL (t) [bp]** | mid IS / VAL (t) | x1.5 IS / VAL | +1 min IS / VAL | years > 0 | VAL/IS | Sharpe IS / VAL | power IS / VAL | per-day power IS / VAL | placebo IS / VAL | random IS / VAL | near-extreme random IS / VAL (info) | IS without Mar-Apr 2020 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **BOOK, mkt 30 (primary)** | 1779 / 1126 | **-0.124 (-4.96) [-3.60]** | **-0.113 (-3.86) [-3.25]** | +0.047 (1.90) / +0.025 (0.85) | -0.209 / -0.181 | -0.116 / -0.115 | 0/9 | 0.91 | -0.124 / -0.126 | -2.80 / -3.22 | -2.61 / -2.89 | 0.890 / 0.990 | 0.975 / 0.870 | 1.000 / 0.990 | -0.118 (-4.86) | fail |
| BOOK, mkt 15 | 1779 / 1126 | -0.129 (-7.08) [-3.72] | -0.123 (-5.59) [-3.50] | +0.040 (2.21) / +0.013 (0.61) | -0.213 / -0.191 | -0.122 / -0.135 | 0/9 | 0.95 | -0.172 / -0.186 | -3.89 / -4.74 | -3.70 / -4.17 | 1.000 / 0.865 | 1.000 / 0.840 | 1.000 / 0.945 | -0.127 (-7.46) | fail |
| BOOK, mkt 60 | 1779 / 1126 | -0.088 (-2.62) [-2.47] | -0.073 (-1.77) [-2.16] | +0.085 (2.53) / +0.066 (1.61) | -0.175 / -0.143 | -0.087 / -0.079 | 0/9 | 0.83 | -0.067 / -0.059 | -1.51 / -1.52 | -1.39 / -1.34 | 0.905 / 1.000 | 1.000 / 0.980 | 1.000 / 1.000 | -0.089 (-2.76) | fail |
| BOOK, lim 30 | 1353 / 907 | -0.175 (-5.72) [-5.11] | -0.111 (-3.49) [-3.25] | -0.011 (-0.36) / +0.021 (0.66) | -0.257 / -0.177 | -0.122 / -0.090 | 0/9 | 0.63 | -0.165 / -0.125 | -3.26 / -2.87 | -2.99 / -2.61 | 0.625 / 1.000 | 0.250 / 0.825 | - | -0.163 (-5.49) | fail |
| BOOK, lim 15 | 1353 / 907 | -0.155 (-6.59) [-4.52] | -0.117 (-4.89) [-3.35] | +0.007 (0.28) / +0.014 (0.58) | -0.236 / -0.183 | -0.108 / -0.097 | 0/9 | 0.76 | -0.197 / -0.179 | -3.89 / -4.10 | -3.44 / -3.63 | 0.975 / 0.950 | 0.650 / 0.845 | - | -0.151 (-7.13) | fail |
| BOOK, lim 60 | 1353 / 907 | -0.127 (-3.08) [-3.66] | -0.083 (-1.84) [-2.48] | +0.039 (0.96) / +0.050 (1.11) | -0.211 / -0.150 | -0.084 / -0.060 | 0/9 | 0.66 | -0.092 / -0.067 | -1.82 / -1.53 | -1.63 / -1.39 | 0.750 / 0.995 | 0.860 / 0.910 | - | -0.123 (-3.12) | fail |
| book without ES35, mkt 30 | 1100 / 796 | -0.105 (-3.47) [-3.14] | -0.103 (-2.84) [-2.99] | +0.058 (1.90) / +0.018 (0.49) | -0.187 / -0.163 | -0.105 / -0.111 | 0/9 | 0.98 | -0.105 / -0.111 | -1.88 / -2.38 | -1.85 / -2.13 | 0.805 / 0.930 | 0.990 / 0.770 | 1.000 / 0.925 | -0.121 (-4.14) | fail |
| book without F40, mkt 30 | 1251 / 727 | -0.145 (-4.98) [-4.31] | -0.134 (-4.09) [-3.97] | +0.028 (0.96) / +0.016 (0.50) | -0.231 / -0.209 | -0.142 / -0.120 | 0/9 | 0.92 | -0.145 / -0.162 | -2.75 / -3.32 | -2.63 / -3.06 | 0.710 / 0.910 | 0.865 / 0.755 | 0.940 / 0.935 | -0.119 (-4.27) | fail |
| book without IT40, mkt 30 | 1563 / 961 | -0.120 (-4.41) [-3.33] | -0.114 (-3.60) [-3.13] | +0.058 (2.14) / +0.032 (1.03) | -0.209 / -0.186 | -0.110 / -0.118 | 0/9 | 0.95 | -0.120 / -0.124 | -2.55 / -2.93 | -2.32 / -2.70 | 0.930 / 0.995 | 0.985 / 0.895 | 1.000 / 0.985 | -0.114 (-4.47) | fail |
| book without STOXX50, mkt 30 | 1423 / 894 | -0.123 (-4.64) [-3.63] | -0.103 (-3.39) [-3.02] | +0.044 (1.66) / +0.030 (0.98) | -0.207 / -0.169 | -0.108 / -0.112 | 0/9 | 0.84 | -0.123 / -0.116 | -2.49 / -2.63 | -2.46 / -2.56 | 0.945 / 1.000 | 0.965 / 0.925 | 0.995 / 0.990 | -0.118 (-4.61) | fail |
| US2000, mkt 30 | 1540 / 1032 | -0.087 (-3.37) [-2.67] | -0.080 (-2.59) [-2.45] | -0.002 (-0.06) / -0.010 (-0.32) | -0.129 / -0.115 | -0.079 / -0.076 | 0/9 | 0.92 | -0.087 / -0.080 | -1.83 / -1.96 | -1.81 / -1.96 | 0.615 / 0.050 | 0.625 / 0.370 | 0.795 / 0.340 | -0.097 (-3.91) | fail |
| SEEN (6), mkt 30 (info) | 3156 / 1926 | -0.106 (-4.91) [-2.91] | -0.094 (-4.27) [-2.65] | -0.003 (-0.12) / -0.041 (-1.87) | -0.158 / -0.121 | -0.106 / -0.101 | 0/9 | 0.89 | -0.106 / -0.107 | -3.21 / -3.56 | -2.58 / -3.19 | 0.345 / 0.000 | 0.375 / 0.000 | 0.615 / 0.000 | -0.085 (-5.36) | fail |
| SEEN European (UK100, DE40), mkt 30 (info) | 1711 / 992 | -0.089 (-3.46) [-2.49] | -0.057 (-2.08) [-1.60] | +0.004 (0.16) / -0.010 (-0.35) | -0.135 / -0.080 | -0.089 / -0.059 | 1/9 | 0.64 | -0.089 / -0.068 | -1.97 / -1.62 | -1.84 / -1.57 | 0.395 / 0.395 | 0.545 / 0.235 | 0.600 / 0.350 | -0.060 (-2.69) | fail |
| ALL European (book + UK100 + DE40), mkt 30 (info) | 3490 / 2118 | -0.106 (-5.65) [-3.06] | -0.086 (-3.91) [-2.48] | +0.026 (1.39) / +0.009 (0.39) | -0.173 / -0.134 | -0.103 / -0.089 | 0/9 | 0.81 | -0.106 / -0.100 | -3.38 / -3.48 | -2.95 / -2.92 | 0.820 / 0.940 | 0.940 / 0.705 | 0.995 / 0.930 | -0.089 (-5.08) | fail |

- **Years** (book, market fade h30, sd units), 2016-24: -0.161, -0.141, -0.133, -0.094, -0.125, -0.083, -0.098, -0.189,
  -0.061. Every year is negative, and so is every symbol-year of ES35, IT40 and STOXX50. F40 is positive in 2019
  (+0.44 bp) and 2020 (+2.92); `out/years_f.txt` has the rest.
- **Zero-cost power** (mid Sharpe x sqrt(1.73 x trades a year)), book market fade: h15 1.21 / 0.52, h30 1.07 / 0.71,
  h60 1.46 / 1.38 (IS / VAL). Even a free venue would not reach 3.
- **Without March-April 2020** nothing changes (book IS -0.118 sd, t -4.86).
- **By side** (book symbols, market fade h30): after a downward break (the fade buys) is worse in ES35, IT40 and
  STOXX50 (IS -5.56, -7.76, -4.01 bp) than after an upward break (-3.02, -3.30, -2.82). F40's upward breaks are the
  least bad (-1.00 IS / -0.08 VAL). Full split in `out/stream_tables_f.md`.

### US2000 control, both sides: net IS (t) / VAL (t) [mid IS / VAL] (placebo IS / VAL)
| side | 15 | 30 | 60 |
|---|---|---|---|
| fade, market | -3.02 (-5.05) / -2.48 (-3.62) [-0.39 / -0.31] (0.13 / 0.05) | -2.67 (-3.37) / -2.45 (-2.59) [-0.05 / -0.30] (0.66 / 0.05) | -2.66 (-2.54) / -2.34 (-1.85) [-0.02 / -0.18] (0.01 / 0.02) |
| fade, limit | -3.58 (-5.10) / -3.79 (-5.07) [-0.97 / -1.64] (0.23 / 0.00) | -3.43 (-3.84) / -4.01 (-3.92) [-0.84 / -1.87] (0.55 / 0.00) | -3.61 (-3.11) / -4.38 (-3.17) [-1.01 / -2.23] (0.02 / 0.00) |
| continuation (round 28 stop fill) | -3.63 (-5.70) / -3.31 (-4.70) [-1.00 / -1.14] (0.96 / 0.93) | -3.96 (-4.84) / -3.30 (-3.44) [-1.34 / -1.15] (0.53 / 0.94) | -4.00 (-3.73) / -3.43 (-2.69) [-1.36 / -1.27] (1.00 / 0.98) |

The continuation mid includes R2's slip (2.2 / 1.9 bp at US2000). Measured from the level, the price after a US2000
minor break continues +0.95 / +0.73 bp at 30 minutes, the US500-like direction the brief predicted. It is too small
for either side.

## Where the move after a minor break happens (information, `out/diag_f.txt`)
All values are mean bp at mid in the direction of the break (the stop's side), IS | VAL. The stop-side mid is round 28
R2's convention: slip + in-bar + close to exit.

| set | n | slip in R2's mid | in-bar: fill mid to trigger close | level to trigger close | close to exit 15 / 30 / 60 (fade mid = minus this) | level to exit 30 | R2-style stop mid h30 | fade round trip |
|---|---|---|---|---|---|---|---|---|
| book (4) IS | 1779 | -3.88 | +0.69 | +0.76 | -1.07 / -1.24 / -2.44 | -0.48 | -4.43 | 4.84 |
| book (4) VAL | 1126 | -3.19 | +0.52 | +0.60 | -0.37 / -0.65 / -1.80 | -0.05 | -3.32 | 3.90 |
| US2000 IS / VAL | 1540 / 1032 | -2.24 / -1.85 | +0.85 / +0.40 | +0.90 / +0.43 | +0.39 / +0.05 / +0.03; +0.31 / +0.30 / +0.18 | +0.95 / +0.73 | -1.34 / -1.15 | 2.63 / 2.15 |
| UK100 IS / VAL | 585 / 270 | -2.87 / -2.15 | +0.60 / +0.23 | +0.68 / +0.41 | -0.69 / -1.28 / -1.71; -0.55 / -1.06 / -0.33 | -0.60 / -0.65 | -3.55 / -2.98 | 3.39 / 2.25 |
| AUS200 IS / VAL | 573 / 311 | -2.66 / -1.01 | +0.41 / +0.28 | +0.47 / +0.33 | -0.80 / -0.24 / -1.81; -0.54 / -0.86 / -0.20 | +0.23 / -0.54 | -2.49 / -1.59 | 3.37 / 1.44 |
| seen (6) IS / VAL | 3156 / 1926 | -2.41 / -1.27 | +0.78 / +0.46 | +0.89 / +0.58 | -0.03 / +0.10 / -0.10; +0.71 / +1.20 / +1.62 | +0.99 / +1.78 | -1.53 / +0.39 | 2.81 / 1.45 |

- **R2's motivating numbers are reproduced and decomposed.**
  - UK100, 15 minutes: -2.87 (slip) + 0.60 (in-bar) - 0.69 (close to exit) = -2.96, R2's number.
  - AUS200, 15 minutes: -2.66 + 0.41 - 0.80 = -3.05; R2 had -3.06.
  - About 90 % of each is the slip assumption.
- **The slip is real for a stop order but tells nothing about where the price goes.**
  - The price closes the trigger minute 0.3-0.9 bp beyond the level.
  - For the European set it then drifts back by 0.4-2.4 bp over 15-60 minutes.
  - For the US and Asian indices it keeps drifting in the direction of the break in VAL.
- **The fade captures only the close-to-exit part.** That part is 0.4-2.4 bp, against a 3.9-4.8 bp round trip.
- **Major levels of the six seen symbols (same decomposition, `out/diag_major_f.txt`).**
  - From the level, the price continues +1.35 bp (IS) / +0.88 (VAL) at 30 minutes; from the trigger close, +0.60 /
    +0.43.
  - R2's stop-side mids are reproduced: UK100 -4.40, DE40 -1.59, AUS200 -1.69, JP225 +1.58, HK50 -2.08, US500 +0.04
    (IS).

## Cells tried and chance (`out/chance_f.txt`)
- **Candidates:** K = 24 (four book symbols x {market, limit} x {15, 30, 60}).
- **Outcome:** IS net > 0 in 0 cells; IS and VAL net > 0 in 0; IS mid > 0 in 15; VAL mid > 0 in 19. Verdicts: 24 fail.
- **Chance benchmarks:**
  - max |t| of 24 independent normals: p50 2.19, p95 3.06;
  - per-day sign-flip null (1,000 draws, one sign per UTC day shared by the 24 cells): max IS mid t p50 1.64, p95
    2.69. The best observed is +2.59 (F40, market, 15 minutes), exceeded by 7.5 % of draws;
  - max IS net t under the same null: p50 1.63, p95 2.64. The best observed is -0.39.
- **The book's own readings** (6, of the same trades) are all net < 0 with t from -1.77 to -7.08.
- **Not candidates:** the control (9 cells) and the information cells (36 seen-symbol fade cells and 30 continuation
  readings of the other ten symbols); all fail.

## Needs the user
- **Nothing for this verdict.** The fade is below cost on IC's European index CFDs at any modelled spread, and below
  power 3 even at zero cost.
- **Not recommended:** IC ticks for ES35, F40, IT40, STOXX50 from the VPS. They would replace the modelled spreads
  (published averages x DE40's hour profile) and allow a seconds-scale fade inside the trigger minute. But the move
  after the trigger close is 0.4-2.4 bp in either era, so exact spreads would not change the answer.
- **For the lead, not the user.** Round 28's "minor index levels revert" idea is mostly R2's slip term, as
  decomposed above. If round 28's report or the journal repeats that idea as a lead, this section is the correction.

## Untested ideas (not declared, so not candidates)
- **A tick-level fade inside the trigger minute.**
  - On the symbols with IC ticks (US30, USTEC), test whether the spike that makes R2's slip (0.84 s60 at 250 ms) gives
    back by the minute's close. Fade it within seconds and exit at the close or at 15 minutes.
  - On minute data that move is invisible. The bar closes only 0.3-0.9 bp beyond the level on average, so the room is
    small.
- **The relative round-number effect.** Round levels revert about 1 bp more than shifted grids in both eras (book
  placebo 0.89 / 0.99). Round 28 saw the same. It could only matter for an execution that already pays at random
  levels, and none does at IC's costs.
- **Minor-level continuation in the US and Asian indices in VAL** (post hoc, against this stream's side): US500 +2.93,
  HK50 +5.49, JP225 +3.46 bp from the trigger close at 30 minutes; seen set +1.78 bp from the level. It is not stable
  (IS about 0 or negative for HK50 / JP225), and HK50 rests on 135 VAL trades.

## Scripts and outputs
Scripts are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r29/F/code/`
and outputs in `.../r29/F/out/`. Round 28 R2's originals are copied in `code/r28R2_ref/`. Run them from the repo root
with `PYTHONPATH=. research/.venv/bin/python <script>`.

| script | what it does |
|---|---|
| zbload.py | HOLD-guarded loader of `research/data/<SYM>/m1/*.zbars` (names < 20250101 before opening; ts asserted) |
| profile_zb.py, spread_factor.py, spacings_f.py | prices-only structure, the declared DE40 / US500 hour factors, spacings and tick grids -> `out/profile_zb.txt`, `out/spread_factor.*`, `out/spacings.*` |
| common.py, mdata.py, engine.py, fills.py | R2's code, adapted: F symbol sets, zb source + modelled spread, limit-fade mode, the +1-minute cap-bar fix |
| fills_f.py | market / limit fade fills, x1.5, +1 minute, the random-entry side rule |
| events_f.py, count_tables_f.py | real + 200 placebo lattices in both modes (prices only) -> `out/ev_<SYM>.npz`, `out/counts_f.md` |
| test_engine.py (R2's), test_fade.py, brute_f.py | synthetic tests; independent re-simulation -> `out/brute_f.txt` |
| run_f.py | fills of real and placebo trades, the continuation side, random entries (RND, RNX, RNDL) -> `out/res_<SYM>.npz` |
| analyze_f.py | cells, pooled sets, placebo / random shares, chance, verdicts -> `out/cells_f.txt`, `out/book_f.txt`, `out/chance_f.txt`, `out/years_f.txt`, `out/analysis_f.pkl`; `--csv` writes the per-trade CSV |
| diag_f.py, diag_major_f.py, stream_tables_f.py | the decomposition above (minor cell; the seen symbols' major cell) -> `out/diag_f.txt`, `out/diag_major_f.txt`; the tables -> `out/stream_tables_f.md` |

**Per-trade CSV:**
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r29/F/trades_F.csv`
- 90,336 rows: every real minor-cell trade of the 11 symbols, kinds mkt / lim / cont, holds 15 / 30 / 60, IS and
  VAL.
- Columns: sym, set (book / control / seen), kind, hold_min, era, year, t_trigger_ms, trade_side, level_side,
  gross_bp, net_bp, net_x15, net_p1min, sd_is_30min, fill.
- Placebo and random trades are in `out/res_<SYM>.npz`.
