# Round 17, stream Y: quote-based order-flow imbalance (OFI) on IC ticks

2026-10-06, 02:40-02:55 UTC (Mac `date -u`). Rules in [HYPOTHESES_Y.md](HYPOTHESES_Y.md), written before the numbers;
post-hoc additions marked there. HOLD (2025-01-01 on) was never loaded: the tick loader asserts every requested day is
< 2025-01-01 and the minute grid ends 2024-12-31 23:59.

## Answer
- **No LIVE candidate.** One cell meets the **DEMO numbers** formally: US30, US morning (HI window), |30-min OFI z|
  >= IS P99.9, continuation, 15-min hold. IS +8.11 bp (t 2.11, 53 trades), VAL +10.07 (t 5.77, 10 trades).
  It is weak: inside chance for a 1,680-cell family, knife-edge on the threshold in IS, two days carry IS.
  Draft: [PREREG_DRAFT_Y_us30_open_ofi.md](PREREG_DRAFT_Y_us30_open_ofi.md). Family stopped, HOLD not opened.
- **Data limit.** The IC cache has prices only (no sizes or depth), so OFI is the CKS (2014) form with unit depth:
  sign(dBid) + sign(dAsk). Its correlation with the tick rule on mid changes is 0.91-0.997, so the two measures are
  nearly the same thing. In VAL the index quotes move both sides together almost always (0.997).
- **Unconditionally, signed quote flow predicts reversal, not the registered continuation.** In FX and metals the next
  1-15 min move against the last 1-15 min of flow: AUDUSD k5 h5 -0.057 bp per z (t -8.9) IS, -0.026 (t -2.6) VAL.
  This comes from the own-return reversal:
  - The 30-min return predicts more strongly than the flow: AUDUSD -0.078 (t -9.9).
  - **Holding the return fixed, the flow predicts continuation** (partial OFI given RET, h = 1 at +1 s):
    - IS: > 0 in 7/7 symbols, t 2.3-6.8;
    - VAL: > 0 in 7/7, t 1.2-4.3 (NZDUSD 1.2, the rest >= 2.3).

    That is Hasbrouck's persistent-flow sign, but it is 0.01-0.06 bp per z in FX/metals and 0.08-0.25 bp in XTI.
- **Decay with latency.** The slope barely changes from L = 0 to +1 s (AUDUSD k5 h5: -0.064 to -0.057). It is still
  significant at +60 s in FX/metals (AUDUSD k1 h1 -0.009, t -6.0 IS / -2.4 VAL). So predictability does outlive the
  first minute, but at 0.01-0.1 bp per z against 0.7-1.5 bp of FX/metals cost.
  - The indices show a sub-minute pattern: k1 h1 slope + at +5 s (USTEC +0.031, t 8.7), - at +30/60 s
    (-0.011, t -3.7). Those are hundredths of a bp.
- **Executable rules:** 1,680 cells. Only 4 IS cells have net t >= 2 at +1 s (fewer than chance). 40 are net > 0 in
  both eras, all with |t| < 2 in at least one era except the DEMO cell above.

## 1. Measures and data
Measures:
- OFI_k = sum of sign(dBid) + sign(dAsk) over the IC quote rows of the last k minutes, k in 1, 5, 15, 30.
- TR_k = the tick rule on mid changes.
- RI = quote updates in the window / the mean for the same UTC hour over the previous 28 days (intensity).
- R_k = the window's own mid return.

z = X / RMS(X) over the previous 28 calendar days. Target: the mid return from t + L to t + L + h, with h = 1, 5, 15,
30, 60 min and L = 0 (not tradable), +1 s, +5 s, +30 s, +60 s; the mid is the last quote before that instant.

Data rules:
- No signal or forward window touches 16:30-18:10 New York or the weekend.
- XTI uses 2018 on and excludes 2020-04-15..30.
- Screen returns are winsorised at ±10 robust sd per year; z is clipped at ±8.

corr(OFI_5, RET_5) is 0.44-0.93 and corr(OFI, TR) 0.91-0.997, so the signed count is mostly a coarse version of the
return.

## 2. Screen: slope of the next-h mid return on z (bp per unit z, day-clustered t)
Decay with latency, OFI, ALL times (IS | VAL):

| sym | k1 h1, L=0 | k1 h1, +1 s | k1 h1, +60 s | k5 h5, L=0 | k5 h5, +1 s | k5 h5, +60 s | k30 h60, +1 s |
|---|---|---|---|---|---|---|---|
| AUDUSD | -0.012 (-6.5) \| +0.001 | -0.009 (-5.1) \| -0.001 | -0.009 (-6.0) \| -0.006 (-2.4) | -0.064 (-10.1) \| -0.030 (-3.0) | -0.057 (-8.9) \| -0.026 (-2.6) | -0.049 (-7.6) \| -0.026 (-2.7) | -0.055 (-1.0) \| +0.007 |
| NZDUSD | -0.010 (-5.0) \| +0.005 | -0.007 (-3.7) \| +0.001 | -0.007 (-4.6) \| -0.004 (-1.8) | -0.057 (-8.7) \| -0.021 (-2.2) | -0.052 (-8.0) \| -0.020 (-2.1) | -0.043 (-6.9) \| -0.016 | -0.023 \| +0.015 |
| XAUUSD | -0.017 (-7.2) \| -0.006 | -0.010 (-4.1) \| -0.007 (-2.1) | -0.011 (-5.2) \| -0.010 (-3.3) | -0.018 (-2.0) \| +0.006 | -0.014 (-1.5) \| +0.008 | -0.004 \| +0.016 | +0.122 (1.3) \| +0.161 (1.0) |
| XAGUSD | -0.032 (-5.7) \| +0.007 | -0.008 (-1.4) \| +0.008 | -0.029 (-6.0) \| -0.030 (-4.0) | -0.105 (-5.2) \| -0.078 (-2.5) | -0.085 (-4.2) \| -0.070 (-2.3) | -0.084 (-4.3) \| -0.059 (-1.9) | -0.558 (-2.9) \| +0.150 |
| US30 | +0.006 (1.8) \| +0.003 | +0.006 (2.0) \| +0.001 | -0.010 (-3.8) \| -0.007 (-2.0) | -0.020 (-1.8) \| -0.018 | -0.015 \| -0.015 | -0.013 \| -0.020 | +0.153 (1.3) \| -0.009 |
| USTEC | +0.019 (5.3) \| +0.026 (5.4) | +0.017 (4.6) \| +0.020 (4.1) | -0.011 (-3.7) \| -0.015 (-3.3) | +0.004 \| -0.022 | +0.007 \| -0.017 | +0.003 \| -0.030 | +0.395 (2.8) \| -0.146 |
| XTIUSD | -0.010 \| -0.004 | -0.003 \| +0.017 | -0.037 (-4.1) \| -0.028 (-3.2) | -0.074 (-2.0) \| -0.024 | -0.078 (-2.1) \| -0.016 | -0.040 \| +0.009 | +0.684 (1.7) \| +0.522 (1.2) |

OFI against the own return (k5, +1 s, ALL; IS | VAL):

| sym | h | RET | OFI | OFI given RET |
|---|---|---|---|---|
| AUDUSD | 1 | -0.027 (-13.7) \| -0.014 (-4.3) | -0.016 (-10.5) \| -0.005 (-1.8) | +0.013 (4.2) \| +0.014 (3.0) |
| XAUUSD | 1 | -0.039 (-11.7) \| -0.030 (-7.4) | -0.008 (-3.9) \| -0.004 | +0.019 (6.6) \| +0.011 (3.1) |
| XAGUSD | 5 | -0.197 (-6.8) \| -0.154 (-4.5) | -0.085 (-4.2) \| -0.070 (-2.3) | +0.150 (3.7) \| +0.061 (1.3) |
| US30 | 1 | -0.017 (-5.3) \| -0.013 (-2.7) | -0.004 \| +0.000 | +0.021 (4.5) \| +0.013 (2.7) |
| USTEC | 1 | -0.010 (-2.8) \| -0.010 | +0.003 \| +0.004 | +0.020 (4.2) \| +0.014 (2.3) |
| XTIUSD | 5 | -0.120 (-2.7) \| -0.095 (-2.5) | -0.078 (-2.1) \| -0.016 | +0.253 (2.3) \| +0.179 (2.0) |

Chance: a day-flip permutation null shared by all symbols, 200 draws, run on the 2,240 tradable OFI cells per era.

| era | observed max \|t\| | null max \|t\| (median / p95) | cells with \|t\| >= 3 | null cells with \|t\| >= 3 (median / p95) |
|---|---|---|---|---|
| IS | 10.3 | 3.08 / 3.76 | 248 | 1 / 23 |
| VAL | 4.8 | 3.11 / 3.80 | 51 | 1 / 22 |

The screen is far from chance, but on the wrong side: 214 of the 250 IS cells with |t| >= 3 are negative (reversal).
On the registered sides, 308 cells have IS t >= 2 and 384 have t <= -2.

By hypothesis (OFI, +1 s, 140 cells per condition):
- **Y1** (continuation, ALL): rejected. 44 % of IS cells are positive (11 with t >= 2, 54 with t <= -2).
- **Y2** (reversal at k1 h1): right sign in FX/metals. The P95 rule makes +0.04-0.05 bp gross (t 4.4-5.5) against a
  0.9-1.2 bp cost.
- **Y3** (continuation in the HI window): 67 % of IS cells positive (19 with t >= 2, 11 with t <= -2); VAL 46 %
  (3 vs 0). Weak; it gives the DEMO cell.
- **Y4** (THIN, reversal): right in IS (51 cells with t <= -2), gone in VAL (13 vs 1, mixed).
- **Y5** (high intensity, continuation): wrong side. 23 % of IS cells positive; the IS cells say reversal.

## 3. Executable rules (|OFI z| >= IS P95 / P99 / P99.9)
Entry and exit at the tick bid/ask; 0.6 bp commission for FX/metals; one position at a time.

Rule-grid counts:
- 1,680 cells x 4 latencies.
- At +1 s, 114 of 1,596 IS cells are net > 0 and 4 have net t >= 2.
- On the gross (registered side), 110 cells have t >= 2 and 131 have t <= -2.

IS-chosen cell per symbol and condition, at +1 s. Net is bp per trade (t); power is per-trade Sharpe x
sqrt(trades/yr x 1.73).

| sym | cond | k/h/cut | IS n/yr | IS gross (t) | cost IS / VAL | net IS (t) | net VAL (t) | VAL/IS gross | power IS / VAL | VAL +60 s | VAL x1.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDUSD | HI | 30/60/P99 | 69 | +1.26 (1.2) | 0.91 / 0.69 | +0.35 (0.3) | +0.60 (0.4) | 1.01 | 0.2 / 0.3 | +0.81 | +0.55 |
| AUDUSD | ALL | 30/60/P99.9 | 42 | +1.30 (0.7) | 0.98 / 0.70 | +0.32 (0.2) | -0.51 | 0.15 | 0.1 / -0.2 | -0.45 | -0.56 |
| NZDUSD | HINT | 30/60/P99 | 13 | +5.16 (1.7) | 1.45 / 1.56 | +3.71 (1.3) | -6.24 (-0.9) | -0.91 | 0.6 / -0.7 | -5.73 | -6.72 |
| XAUUSD | HI | 30/30/P99 | 50 | +4.62 (3.8) | 1.37 / 1.00 | +3.25 (2.7) | -0.59 (-0.4) | 0.09 | 1.4 / -0.3 | -0.69 | -0.79 |
| XAGUSD | ALL | 15/60/P99.9 | 44 | +0.43 | 4.85 / 4.78 | -4.42 | -12.68 | - | -0.5 / -1.0 | -13.80 | -14.72 |
| **US30** | **HI** | **30/15/P99.9** | **9** | **+9.13 (2.4)** | **1.02 / 0.28** | **+8.11 (2.1)** | **+10.07 (5.8)** | **1.13** | **0.9 / 2.8** | **+8.14** | **+9.93** |
| US30 | HINT | 15/60/P95 | 90 | +4.49 (3.1) | 1.13 / 0.32 | +3.36 (2.3) | -0.41 | -0.02 | 1.1 / -0.1 | +0.03 | -0.57 |
| US30 | THIN | 15/60/P99 | 38 | +3.46 (2.0) | 1.30 / 0.43 | +2.15 (1.2) | -7.66 (-3.4) | -2.09 | 0.7 / -2.6 | -7.82 | -7.87 |
| USTEC | ALL | 30/60/P99 | 242 | +3.71 (3.2) | 1.97 / 0.71 | +1.74 (1.5) | -1.77 (-1.0) | -0.29 | 0.8 / -0.7 | -1.34 | -2.12 |
| XTIUSD | ALL | 15/60/P99.9 | 65 | +13.46 (1.3) | 6.76 / 3.49 | +6.70 (0.7) | +8.01 (0.9) | 0.85 | 0.6 / 0.8 | +9.80 | +6.33 |
| XTIUSD | HI | 15/15/P99.9 | 13 | +23.51 (2.0) | 6.49 / 3.25 | +17.03 (1.5) | +9.16 (0.6) | 0.53 | 0.9 / 0.6 | +8.57 | +7.60 |

The full 28-row table is in out/summary_rules.md.
- **Short-horizon rules (h = 1-5) never clear the cost.** Their best gross is +0.04-0.4 bp in FX/metals and +0.5-2 bp
  in XTI, against costs of 0.9-1.5 and 6.4-8.3 bp.
- **Latency hardly matters at this size.** The mean P99 gross barely moves from +1 s to +60 s (AUDUSD -0.23 / -0.15 /
  -0.13 / -0.14 bp; USTEC +0.49 / +0.57 / +0.56 / +0.45).

## 4. The DEMO-number cell, checked
US30, HI window, k30, h15, |z| >= 6.795 (IS P99.9), continuation. Checks:
- **Latency:** at +5 / +30 / +60 s, IS +7.49 / +6.19 / +7.29 (t 1.91 / 1.62 / 1.77) and VAL +9.50 / +9.39 / +8.14.
- **Spread x1.5:** IS +7.58 (t 1.97), VAL +9.93.
- **Years:** 7 of 9 net > 0 (2017 -10 bp, 2021 -2 bp).
- **Random entries,** side recomputed, 500 seeds:
  - (a) same NY half-hour and weekday on a random day: beats 100 % IS, 95.4 % VAL;
  - (b) the same day at a random time in the window: beats 85.8 % IS, 94.4 % VAL.
- **C3 correlation:** daily +0.05, monthly +0.05.

Against it:
- **Threshold:** in IS the cell is positive only at P99.9; P99 gives -0.15 and P99.5 -0.01. VAL is positive at all
  three cuts (+1.51 / +4.38 / +10.07).
- **Concentration:** IS is +6.43 (t 1.67) without 2018-02-06 and +4.53 (t 1.44) without 2020.
- **Post hoc, return instead of flow:** the same rule on the return z loses (IS -1.03 at P99.9).
- **Post hoc, USTEC:** +3.90 (t 1.27) in IS, and only 1 VAL trade.
- **Expected HOLD t:** about 6-15 HOLD trades at the pooled per-trade Sharpe of 0.25 give 0.6-1.0.

Verdict: real-looking big-day continuation after the US open, too rare and too fragile. The lead decides on the draft.

## Scripts and outputs
All in /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r17/Y/.

| script | does |
|---|---|
| y1_features.py | per-minute OFI, TR, update count and bid/ask at +0/1/5/30/60 s from ticks, month by month, asserts days < 2025 |
| ycommon.py | z, intensity, clocks, conditions, forward returns |
| y2_screen.py | slopes |
| y3_null.py | day-flip null |
| y4_rules.py | executable rules |
| y5_summary.py, y6_rules_summary.py | summaries |
| y7_check.py | DEMO-cell checks |
| y8_posthoc.py | PH1 / PH2 |

Outputs in out/: summary_screen.md, null.txt, summary_rules.md, check_US30_HI.txt, posthoc.txt, screen_*.tsv,
rules_*.tsv.
