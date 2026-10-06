# Round 18, stream A: decay forensics of the effects real at mid

2026-10-06, computed 02:58-03:08 UTC, written 03:09 UTC (times from `date -u`). Hypotheses and methods were fixed
first in [HYPOTHESES_A.md](HYPOTHESES_A.md) (two post-hoc additions are marked there). HOLD (2025-01-01 onwards) was
not loaded: the panel ends 2024-12-31, Dukascopy is cut at 2016-01-01, the C3 trade list was read with its HOLD rows
skipped. The published HOLD readings of the registered rules are used as published numbers only.

## Answer
- **Most effects look flat in 2016-24; that says little.** 49 series were rebuilt (48 effects plus C3 in R). On
  the pre-set rule (bp), 22 are flat, 5 decaying and 22 unclear. Judged on the per-trade Sharpe instead (post hoc,
  free of volatility), 29 are flat and 5 decaying.
  - Nine yearly means are too few to tell a slow decay from noise. The 90 % forecast intervals for 2025-26 run from
    about 0 to about the VAL size for almost every row.
  - The trend tests only catch effects that already collapsed from IS to VAL: the WM/R GBPUSD month-end leg (F16),
    GBPJPY at 10:28 NY on month-ends (F18), rule I (F17), the JP225 close (I9) and the HK50 gap (I8).
- **Flat trends did not predict which registered rules held in HOLD.**
  - Flat: C3 kept 1.03 of its VAL size, but J5c kept 0.31 and M1 0.19.
  - Unclear: E1 kept 0.65, L4-G-d 0.81. Decaying: I kept 0.24.
  - Spearman of the forecast retention against the published retention is +0.26 (bp trend) and -0.20 (Sharpe trend),
    over 6 rules.
  - Every published HOLD reading lies inside its 90 % predictive interval. The intervals are too wide to fail; J5c's
    0.48 bp sits at the lower edge, against an interval of 0.40 to 2.05.
  - **What does separate them (descriptive, n = 6) is how they were found.** Rules declared before looking, or
    discovered in 2004-15, kept 0.65-1.03: C3, E1, L4-G-d. Rules picked post hoc or from a scan with VAL in view kept
    0.19-0.31: J5c, I, M1. A perfect split of 3 vs 3 has chance 1/20.
- **2024 is a common low year (post hoc).** 35 of 49 series are below their 2016-23 mean in 2024 (mean z -0.88).
  - The three Sydney V legs show it most clearly: z -3.1 to -3.6, the lowest year since 2016. That was before HOLD.
  - J5c's HOLD (+0.48) continues that 2024 level (+0.68). A linear 2016-24 trend cannot see a drop in the last year.
  - This undercuts STREAM_X's venue route. At a venue, the trend forecast gives the Sydney pre-leg power 4.2 and J5c
    3.5. At the 2024 level these fall to 2.4 and 1.4; at J5c's HOLD level, to under 1.
- **C3 is the only effect that is flat on every reading.** Over 21 years its mid per leg has PRE +3.49, IS +4.03 and
  VAL +3.44 bp, a 2004-24 trend of -0.07 bp/yr (t -1.3), PRE last-3/first-3 0.93 and a trend in R of -0.001/yr.
  - In bp, C3 is "unclear" only because 2016 was a high-volatility year (+9.3 bp). Its Sharpe and R series are flat.
  - So the bp classification penalises volatility regimes, which is why the Sharpe reading was added.
- **No effect reaches power 3 at IC's costs on its forecast size**, except two that are already disqualified:
  - I7, the AUS200 10:10 drop: 3.75 on the Sharpe trend. Not executable (+1 minute < 0 every year) and its IS net t is
    below 0.
  - F20 (J5c): 3.05 on the Sharpe trend. Registered, and HOLD rejected it.
  - Next best at IC: I2 (USTEC LETF close, top quintile) 1.8-2.1, I3 (US30 post-close) 1.5-1.9, F22 (USDJPY
    16-17 NY) 1.5-2.4, C3 1.4-1.6.
- **No fresh pre-registration.** The rows that would meet DEMO on IS/VAL with their forecast size (STREAM_X flag D and
  forecast net > 0 at IC) are:
  - E1 and L4-G-d, already registered;
  - F2, F4 and F5, which are E1's own window or nested in it (F5 already has round 15's draft);
  - F15, EURJPY at quarter-end, 4 trades a year.
  - None is new, and none would reach LIVE. No PREREG_DRAFT was written.
- **Of the two demos, the forecasts favour gold settlement big days (L4-G-d) a little:**
  - its Sharpe trend is flat (t -0.5);
  - its three forecasts agree (+2.1 to +2.5 bp), and HOLD came in at +2.54;
  - 2024 was a strong year (+6.1);
  - per-trade net Sharpe is about 0.13 at IC, against E1's 0.03-0.05.
  - E1's forecast depends on the window. The 2016-24 trend gives +0.78 bp (net +0.16). The 2004-24 trend is flat
    (+1.49), and so is its Sharpe.
  - Combined with the published HOLD, years of demo alone for t 2.0 are: L4-G-d 8.5-10, E1 5.4 (21-year forecast) to
    24 (2016-24 forecast).
  - Neither can confirm within two years at IC's costs.

## Method (as fixed in HYPOTHESES_A.md; deviations noted)
- Per event, the mid move in bp on the source's side. Multi-leg rules (C3 basket, Sydney AUD+NZD, I, M1) are averaged
  per leg within a UTC day (the cluster). Year y gives a mean and a standard error.
- **Trend T1.** WLS of the yearly means on the year, 2016-24, with inverse-variance weights, the se scaled for
  dispersion between years. Implementation detail not in the hypotheses: each yearly se is floored at half the pooled
  sd / sqrt(n), so a lucky quiet year cannot dominate.
- **T2.** The same fit over 2004-24, where Dukascopy covers the window: M1 for EURUSD, USDJPY, EURJPY, GBPJPY and
  USDCHF; H1 for the hour-aligned GBPUSD and XAU windows.
- **Breaks.** B16 = PRE vs 2016-24, B20 = 2016-19 vs 2020-24, B21 = 2016-20 vs 2021-24 (Welch). L3/F3 = mean 2022-24 /
  mean 2016-18.
- **Forecast.** T1 extrapolated to the HOLD centre (2025-11), with a 90 % interval for the expected effect and a
  predictive interval for a 1.73-year reading.
  - Power = (forecast - cost) / sd_VAL x sqrt(1.73 x trades a year).
  - Costs: STREAM_X's VAL-era IC cost, or the rebuilt VAL cost for C3 and M1, and STREAM_X's venue cost (scenario d).
- **Sharpe reading (post hoc).** Yearly per-trade Sharpe at mid, trended the same way. Its power is (Sharpe forecast -
  cost / sd_VAL) x sqrt(1.73 n).
- **Classes.** Flat: trend t > -1, L3/F3 >= 0.7, no break t <= -2. Decaying: trend t <= -2, or L3/F3 < 0.5 with B21
  t <= -2. Everything else is unclear.
- **Rebuilds check against the sources.** E1 IS/VAL +1.80/+1.97 (source +1.80/+1.97); L4-G-d +4.74/+3.14 (same); SGE
  +0.91/+0.70 (+0.92/+0.70); I +7.42/+1.79 (registered check IS net +6.73: the rebuilt net is +6.73).
- **Deviations.**
  - M7 is round 12 J's 15-minute version.
  - F13 omits round 13's New York 16:45-18:15 exclusion: 203 vs ~250 days a year.
  - F4-F6 skip TARGET closing days.
  - M1 (round 3) is rebuilt in bp without its ATR stop; its published HOLD is in R.
  - C3 in bp has no stop either; C3R is the registered trade list.
- **Not rebuilt**, because their rule needs inputs not on the panel or a definition not saved: F3 and F8 (selector
  subsets of E1 and F7), F24-F29, M4, I11, I12 and C2.

## Main table
PRE = 2004-15 (Dukascopy), IS = 2016-21, VAL = 2022-24, mid in bp per trade (C3R in net R per leg). Trend in bp/yr
on 2016-24 (t). Class: bp rule / Sharpe rule. Forecast = T1 at 2025-26 [90 % for the expected effect]. Power = forecast
net Sharpe x sqrt(1.73 x n/yr), at IC's VAL cost (in brackets) on the bp trend [interval] ; on the Sharpe trend, and at
STREAM_X's venue cost. PRE for F4-F6 is confounded: the ECB V moved about 16 minutes at the end of 2015 (round 15).

| id | effect | n/yr | PRE mid (t) | IS mid (t) | VAL mid (t) | trend bp/yr (t) | B20 / B21 t | L3/F3 bp ; SR | class bp / SR | forecast 2025-26 [90 %] | power IC (cost): trend [lo, hi] ; SR-trend | power venue (cost): trend ; SR-trend |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C3 | C3 gotobi basket, mid bp per leg (no stop) | 71 | +3.49 (+5.3) | +4.03 (+4.3) | +3.44 (+3.3) | -0.098 (-0.4) | -0.9 / -0.6 | +0.65 ; +1.09 | unclear / flat | +2.58 [+0.40, +4.76] | (1.39) +0.88 [-0.73, +2.49] ; +1.59 | - |
| C3R | C3 registered trades, net R per leg | 71 | - | +0.043 (+3.5) | +0.041 (+2.2) | -0.0012 (-0.3) | -0.3 / +0.1 | +0.85 ; +0.81 | flat / flat | +0.036 [-0.004, +0.076] | (0.00) +1.44 [-0.17, +3.06] ; +1.53 | - |
| F1 | E1 EURUSD short 11:00-13:00 London, every weekday | 254 | +1.69 (+5.2) | +1.80 (+5.1) | +1.97 (+3.6) | -0.182 (-1.5) | -1.4 / +0.1 | +0.82 ; +0.83 | unclear / flat | +0.78 [-0.30, +1.86] | (0.62) +0.22 [-1.27, +1.71] ; +0.96 | (0.20) +0.80 ; +1.54 |
| F2 | EURUSD short 09:00-13:00 London (E1, 4 h) | 254 | +1.73 (+3.5) | +2.46 (+4.9) | +2.40 (+3.0) | -0.255 (-1.7) | -1.1 / -0.1 | +0.77 ; +0.74 | unclear / unclear | +0.94 [-0.48, +2.36] | (0.63) +0.29 [-1.05, +1.64] ; +0.94 | (0.20) +0.70 ; +1.35 |
| F4 | ECB pre-fix slot EURUSD short 12:45-13:00 London, every we | 252 | +0.53 (+3.7) | +1.11 (+5.9) | +1.14 (+4.6) | -0.099 (-1.4) | -2.0 / +0.2 | +0.73 ; +0.85 | unclear / flat | +0.63 [+0.02, +1.24] | (0.62) +0.02 [-1.84, +1.88] ; +1.24 | (0.20) +1.30 ; +2.51 |
| F5 | ECB pre-fix slot, Fridays, EURUSD short 12:50-13:00 London | 50 | +0.54 (+2.3) | +1.79 (+5.9) | +2.05 (+4.2) | -0.127 (-1.2) | -0.2 / +0.7 | +0.99 ; +0.82 | unclear / flat | +1.11 [+0.10, +2.13] | (0.64) +0.75 [-0.85, +2.34] ; +1.69 | (0.20) +1.44 ; +2.39 |
| F6 | ECB fix rebound, EURUSD long 13:00-13:15 London (14:00-14: | 252 | -1.22 (-9.0) | +0.72 (+5.3) | +0.85 (+4.1) | -0.004 (-0.1) | -0.7 / -0.1 | +0.86 ; +0.84 | flat / flat | +0.76 [+0.31, +1.22] | (0.64) +0.45 [-1.23, +2.13] ; +0.85 | (0.20) +2.07 ; +2.47 |
| F7 | USDCHF long 10:00-12:00 UTC (E2) | 254 | +1.51 (+4.4) | +1.02 (+3.0) | +1.08 (+2.2) | -0.091 (-0.9) | -0.6 / +0.3 | +0.73 ; +0.73 | flat / flat | +0.48 [-0.50, +1.46] | (0.89) -0.63 [-2.14, +0.88] ; -0.32 | (0.30) +0.27 ; +0.59 |
| F9 | USDCHF short 13:00-13:30 UTC (ECB-fix rebound) | 254 | +0.29 (+1.1) | +0.32 (+1.5) | -0.04 (-0.1) | +0.011 (+0.1) | +0.6 / -0.3 | -0.21 ; -0.16 | unclear / unclear | +0.26 [-0.48, +1.00] | (1.30) -1.98 [-3.38, -0.58] ; -2.02 | (0.30) -0.08 ; -0.12 |
| F10 | USDJPY long 11:00-13:00 London | 254 | +1.08 (+3.5) | +0.88 (+2.7) | +0.95 (+1.7) | +0.024 (+0.2) | -0.3 / -0.1 | +0.76 ; +0.64 | flat / unclear | +0.83 [-0.31, +1.98] | (0.73) +0.13 [-1.38, +1.65] ; +0.14 | (0.20) +0.84 ; +0.84 |
| F11 | EURJPY short 11:00-13:00 London | 254 | +0.58 (+1.5) | +0.92 (+2.3) | +1.01 (+1.5) | -0.200 (-1.3) | -1.0 / +0.1 | +0.88 ; +0.84 | unclear / flat | -0.10 [-1.53, +1.32] | (0.89) -1.15 [-2.81, +0.50] ; -0.69 | (0.30) -0.47 ; -0.00 |
| F12 | GBPJPY long 17:30-21:30 London (G1) | 250 | +2.20 (+4.2) | +1.59 (+3.2) | +1.55 (+2.2) | -0.239 (-1.5) | -1.5 / -0.7 | +0.62 ; +0.65 | unclear / unclear | +0.09 [-1.36, +1.55] | (1.09) -1.05 [-2.59, +0.48] ; -0.68 | (0.45) -0.38 ; +0.00 |
| F13 | GBPJPY long 02:45-06:45 Sydney | 203 | +2.27 (+3.7) | +2.12 (+3.1) | +1.72 (+1.9) | -0.247 (-1.2) | -1.0 / -1.0 | +0.56 ; +0.60 | unclear / unclear | +0.44 [-1.53, +2.40] | (1.09) -0.54 [-2.15, +1.07] ; -0.30 | (0.45) -0.01 ; +0.22 |
| F14 | EURJPY long 16:00-20:00 London | 255 | +2.17 (+3.7) | +1.76 (+3.6) | +1.06 (+1.4) | -0.229 (-1.1) | -1.3 / -1.4 | +0.42 ; +0.42 | unclear / unclear | +0.01 [-1.89, +1.90] | (0.89) -0.87 [-2.74, +1.00] ; -0.75 | (0.30) -0.29 ; -0.17 |
| F15 | EURJPY short 05:00-07:00 London, last weekday of a quarter | 4 | +6.38 (+2.4) | +6.03 (+2.7) | +9.45 (+2.0) | +0.164 (+0.2) | +0.6 / +0.3 | +1.49 ; +1.26 | flat / flat | +6.60 [-0.70, +13.90] | (1.08) +0.91 [-0.29, +2.11] ; +1.55 | (0.30) +1.04 ; +1.68 |
| F16 | GBPUSD long 15:00-16:00 London, last weekday (WM/R month-e | 11 | +8.32 (+3.8) | +9.71 (+2.7) | +1.87 (+0.4) | -3.148 (-3.7) | -2.1 / -3.0 | +0.13 ; +0.13 | decaying / decaying | -7.56 [-15.92, +0.79] | (0.78) -1.51 [-3.01, +0.00] ; -1.83 | (0.30) -1.42 ; -1.75 |
| F17 | Month-end post-fix USD reversal after a large US month (I) | 6 | - | +7.42 (+3.8) | +1.79 (+0.8) | -1.474 (-2.7) | -1.3 / -1.7 | +0.23 ; +0.28 | decaying / unclear | -1.93 [-6.05, +2.19] | (0.66) -0.85 [-2.20, +0.50] ; -0.22 | (0.25) -0.72 ; -0.08 |
| F18 | GBPJPY long 10:28-10:31 New York, last weekday | 11 | +1.32 (+2.9) | +3.51 (+6.2) | +1.58 (+2.6) | -0.371 (-2.6) | -1.3 / -2.3 | +0.38 ; +0.51 | decaying / decaying | +0.51 [-0.75, +1.78] | (1.11) -0.75 [-2.33, +0.84] ; -0.37 | (0.45) +0.08 ; +0.45 |
| R3M1 | M1 month-end value-date USD (3 legs, no stop) | 12 | +2.02 (+1.3) | +5.64 (+4.2) | +8.23 (+2.2) | +0.209 (+0.3) | +0.3 / +0.3 | +1.08 ; +0.67 | flat / unclear | +6.60 [+0.67, +12.54] | (0.73) +1.19 [-0.01, +2.40] ; +2.36 | - |
| F19 | Sydney pre-leg: short AUD+NZD 09:45-10:00 Sydney, all days | 254 | - | +1.65 (+13.1) | +1.48 (+10.0) | -0.054 (-0.9) | +1.3 / -1.0 | +1.09 ; +1.22 | flat / flat | +1.22 [+0.67, +1.78] | (2.43) -6.21 [-9.06, -3.37] ; -4.05 | (0.40) +4.24 ; +6.41 |
| F20 | J5c: short AUDUSD 09:45-10:00 Sydney outside IC's rollover | 170 | - | +1.54 (+8.8) | +1.53 (+7.5) | -0.025 (-0.4) | +1.4 / -0.3 | +1.30 ; +1.25 | flat / flat | +1.22 [+0.57, +1.88] | (0.77) +1.70 [-0.74, +4.14] ; +3.05 | (0.30) +3.46 ; +4.81 |
| F21 | Sydney post-leg: long AUD+NZD 10:00-10:15 Sydney | 254 | - | +1.28 (+7.6) | +1.44 (+6.0) | -0.026 (-0.3) | +0.6 / +0.1 | +1.25 ; +1.12 | flat / flat | +1.07 [+0.30, +1.85] | (1.73) -2.09 [-4.57, +0.38] ; -1.58 | (0.40) +2.15 ; +2.67 |
| F22 | USDJPY long 16:00-17:00 New York (hour after the cash clos | 254 | +0.27 (+1.7) | +0.77 (+4.8) | +1.06 (+3.1) | +0.074 (+0.7) | -0.6 / +1.4 | +0.95 ; +0.72 | flat / flat | +1.38 [+0.38, +2.38] | (0.70) +1.52 [-0.71, +3.74] ; +2.35 | (0.20) +2.63 ; +3.46 |
| F23 | USDCNH long 01:30-08:30 UTC (CNH home hours) | 259 | - | +1.17 (+2.6) | +2.03 (+2.5) | -0.006 (-0.0) | -0.2 / -0.1 | +1.45 ; +1.16 | flat / flat | +1.27 [-0.44, +2.98] | (1.01) +0.25 [-1.36, +1.86] ; +0.65 | (0.60) +0.63 ; +1.04 |
| M1 | SGE auction: XAU long 02:15-02:23 UTC | 228 | - | +0.91 (+7.7) | +0.70 (+4.3) | -0.065 (-1.6) | -1.3 / -1.0 | +0.58 ; +0.54 | unclear / decaying | +0.45 [+0.02, +0.87] | (1.04) -2.73 [-4.67, -0.79] ; -3.02 | (0.60) -0.70 ; -0.99 |
| M2 | SGE auction on dip mornings (L1-DIP-q) | 45 | - | +1.84 (+6.0) | +1.36 (+3.2) | -0.163 (-1.1) | -0.9 / -0.0 | +0.51 ; +0.40 | unclear / unclear | +0.67 [-0.91, +2.24] | (1.04) -0.63 [-3.31, +2.05] ; -1.11 | (0.60) +0.12 ; -0.36 |
| M3 | XAU long 01:00-03:30 UTC, Chinese session (A6) | 236 | - | +1.74 (+2.4) | +1.46 (+1.6) | +0.032 (+0.1) | -0.2 / +1.0 | +0.70 ; +0.77 | unclear / flat | +1.70 [-0.68, +4.07] | (1.06) +0.52 [-1.42, +2.46] ; +0.42 | (0.60) +0.89 ; +0.79 |
| M5 | L4-G-d: XAU follows the day into the COMEX settlement, top | 25 | - | +4.74 (+4.3) | +3.14 (+2.5) | -0.191 (-0.4) | -0.9 / -2.3 | +0.75 ; +0.78 | unclear / flat | +2.06 [-2.39, +6.51] | (1.03) +0.62 [-2.06, +3.31] ; +0.88 | (0.60) +0.88 ; +1.14 |
| M6 | L4-G-q: same, top quintile | 50 | - | +2.34 (+3.3) | +1.89 (+2.4) | -0.160 (-0.5) | -1.8 / -1.4 | +0.56 ; +0.58 | unclear / unclear | +1.02 [-1.92, +3.96] | (1.00) +0.02 [-2.74, +2.79] ; +0.03 | (0.60) +0.40 ; +0.41 |
| M7 | XAU follow the day 15 min into the settlement, all days (J sett) | 244 | - | +0.64 (+2.5) | +0.25 (+0.8) | -0.119 (-0.9) | -2.5 / -1.0 | +0.22 ; +0.23 | unclear / unclear | +0.00 [-1.34, +1.34] | (1.00) -2.38 [-5.57, +0.81] ; -2.32 | (0.60) -1.42 ; -1.37 |
| M8 | XAU short 14:59-15:01 London (LBMA PM auction) | 248 | - | +1.09 (+5.2) | +0.94 (+2.6) | -0.013 (-0.1) | +1.5 / -1.0 | +1.04 ; +0.72 | flat / flat | +0.82 [-0.48, +2.12] | (1.02) -0.43 [-3.21, +2.35] ; -0.64 | (0.60) +0.47 ; +0.26 |
| M9 | XAG short 11:59-12:01 London (LBMA silver auction) | 248 | - | +2.68 (+8.3) | +2.72 (+9.1) | +0.128 (+1.1) | +2.2 / +0.6 | +1.20 ; +1.21 | flat / flat | +2.99 [+1.80, +4.18] | (4.60) -4.08 [-7.10, -1.07] ; -3.94 | (2.00) +2.51 ; +2.66 |
| M10 | XAU short 10:29-10:31 London (LBMA AM auction) | 249 | - | +0.88 (+8.2) | +0.24 (+1.9) | +0.000 (+0.0) | +3.3 / -2.9 | +0.66 ; +0.70 | unclear / flat | +0.39 [-0.53, +1.30] | (0.99) -3.62 [-9.13, +1.89] ; -3.29 | (0.60) -1.27 ; -0.94 |
| M11 | XAU fade the COMEX floor open 08:20-08:30 ET (V5) | 251 | - | +1.01 (+3.3) | +0.85 (+2.1) | +0.108 (+0.8) | +3.1 / +2.1 | +52.45 ; +49.53 | flat / flat | +1.44 [+0.01, +2.86] | (1.19) +0.45 [-2.15, +3.06] ; +0.81 | (0.60) +1.53 ; +1.88 |
| M12 | XAU long 02:00-06:00 UTC on the weekday before a UK holida | 5 | +9.82 (+4.4) | +6.73 (+2.5) | +1.46 (+0.3) | -0.321 (-0.3) | -0.2 / -0.4 | +0.22 ; +0.12 | unclear / unclear | +3.89 [-7.08, +14.86] | (1.04) +0.38 [-1.10, +1.87] ; -0.50 | (0.60) +0.44 ; -0.44 |
| I1 | USTEC follow the MOC imbalance 15:50-16:00 ET | 242 | - | +1.55 (+2.7) | +0.92 (+1.4) | +0.079 (+0.7) | +1.1 / +0.3 | +0.94 ; +0.69 | flat / unclear | +1.40 [+0.13, +2.68] | (0.65) +0.87 [-0.60, +2.33] ; +0.76 | (0.25) +1.33 ; +1.22 |
| I2 | USTEC follow the day 15:52-16:00 ET, top quintile (L6-LETF | 49 | - | +3.62 (+2.5) | +3.79 (+2.2) | +0.519 (+1.4) | +0.6 / -0.3 | +1.27 ; +1.15 | flat / flat | +4.86 [+0.80, +8.93] | (0.68) +1.81 [+0.05, +3.56] ; +2.07 | (0.25) +1.99 ; +2.26 |
| I3 | US30 fade 16:04-16:14 ET (post-close reversal) | 238 | - | +0.58 (+2.4) | +1.05 (+4.2) | +0.050 (+1.0) | +1.4 / +0.7 | +1.90 ; +2.12 | flat / flat | +0.83 [+0.34, +1.31] | (0.31) +1.53 [+0.09, +2.98] ; +1.94 | (0.30) +1.56 ; +1.97 |
| I4 | US500 fade 09:41-09:51 ET (opening overreaction) | 242 | - | +0.99 (+2.3) | +1.68 (+2.3) | +0.100 (+0.9) | +1.7 / +0.6 | +2.19 ; +1.42 | flat / flat | +1.35 [+0.19, +2.50] | (0.49) +0.89 [-0.31, +2.08] ; +1.44 | (0.49) +0.89 ; +1.44 |
| I5 | UK100 fade 16:34-16:39 London (after the closing auction) | 245 | - | +1.65 (+6.5) | +1.17 (+3.9) | -0.067 (-0.9) | +0.6 / -2.2 | +0.76 ; +0.74 | unclear / unclear | +0.78 [+0.04, +1.52] | (2.03) -3.21 [-5.10, -1.31] ; -2.75 | (0.70) +0.20 ; +0.66 |
| I6 | AUS200 fade 16:00-16:12 over 16:13-16:30 Sydney | 219 | - | +0.86 (+2.3) | +0.73 (+2.7) | -0.051 (-0.7) | -0.4 / -0.7 | +0.79 ; +1.28 | flat / flat | +0.46 [-0.13, +1.04] | (1.58) -3.16 [-4.80, -1.53] ; -2.67 | (1.50) -2.94 ; -2.44 |
| I7 | AUS200 short 10:10-10:11 Sydney (ASX open drop) | 235 | - | +1.55 (+7.2) | +2.05 (+9.1) | +0.129 (+1.5) | +4.7 / +2.4 | +1.87 ; +1.95 | flat / flat | +2.08 [+1.25, +2.91] | (1.45) +2.23 [-0.72, +5.17] ; +3.75 | (1.45) +2.23 ; +3.75 |
| I8 | HK50 fade the gap 09:30-09:31 HKT | 236 | - | +2.11 (+6.3) | +0.33 (+0.4) | -0.160 (-0.5) | -0.7 / -2.8 | +0.18 ; +0.10 | decaying / decaying | +0.40 [-3.07, +3.88] | (2.81) -2.35 [-5.73, +1.04] ; -3.28 | (0.60) -0.19 ; -1.13 |
| I9 | JP225 follow the day 15:00-15:15 Tokyo (after the cash clo | 236 | - | +3.39 (+5.6) | +0.59 (+1.0) | -0.326 (-2.0) | -0.5 / -3.2 | +0.21 ; +0.22 | decaying / decaying | +0.02 [-1.55, +1.59] | (1.87) -2.37 [-4.38, -0.36] ; -2.41 | (1.70) -2.15 ; -2.19 |
| I10 | DE40 follow the day 10 min into the Xetra close, all days | 250 | - | +1.16 (+3.1) | +1.06 (+2.7) | +0.003 (+0.0) | +1.7 / -0.5 | +3.12 ; +3.51 | flat / flat | +0.67 [-0.59, +1.92] | (0.53) +0.26 [-2.12, +2.64] ; +1.18 | (0.40) +0.51 ; +1.42 |
| I13 | US500 night premium (close -> open), long | 243 | - | +4.87 (+2.9) | +0.45 (+0.2) | +0.294 (+0.6) | +0.3 / -1.3 | +0.21 ; +0.15 | unclear / unclear | +4.94 [-0.47, +10.34] | (4.20) +0.23 [-1.46, +1.92] ; +0.15 | (1.50) +1.08 ; +0.99 |
| E1 | XTI follow the day 15 min into the NYMEX settlement, all d | 188 | - | +4.81 (+2.2) | +1.86 (+1.4) | -0.558 (-1.3) | -0.1 / -1.3 | +0.77 ; +0.89 | unclear / flat | -0.01 [-3.06, +3.04] | (3.50) -1.73 [-3.24, -0.23] ; -1.36 | (1.50) -0.74 ; -0.37 |
| E2 | XTI fade 14:30-14:31 ET (WTI settlement) | 190 | - | +1.65 (+2.4) | +0.70 (+2.1) | -0.058 (-0.5) | +1.1 / -1.1 | +1.20 ; +1.18 | flat / flat | +0.47 [-0.39, +1.32] | (3.30) -5.54 [-7.22, -3.87] ; -5.21 | (1.50) -2.02 ; -1.69 |
| C1 | BTC follow the day 23:30-24:00 UTC | 177 | - | +7.29 (+3.4) | +2.38 (+1.8) | -0.807 (-1.5) | +0.1 / -0.2 | +0.69 ; +1.37 | unclear / flat | +1.15 [-2.10, +4.39] | (3.20) -1.00 [-2.59, +0.58] ; +0.14 | (3.00) -0.90 ; +0.24 |

Ranking by forecast power on the bp trend:
- **IC:** I7 2.23 (not executable), I2 1.81, F20 1.70 (HOLD failed), I3 1.53, F22 1.52, C3R 1.44, M1 1.19 (HOLD
  failed), F15 0.91, I4 0.89, C3 0.88, I1 0.87, F5 0.75, M5 0.62.
- **Venue:** F19 4.24, F20 3.46, F22 2.63, M9 2.51, I7 2.23, F21 2.15, F6 2.07, I2 1.99, I3 1.56, M11 1.53, F5 1.44.

## Registered rules: forecast vs published HOLD
| rule | VAL (rebuilt) | T1 forecast [90 %] | predictive HOLD [90 %] | T1 / VAL | T2 (2004-24) / VAL | Sharpe forecast / VAL | published HOLD | published HOLD / VAL | class bp / SR | how found |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 (R) | +0.041 | +0.036 [-0.004, +0.076] | [-0.020, +0.091] | 0.87 | (bp: 2004-24 trend t -1.3) | 0.93 | +0.042 | 1.03 | flat / flat | literature (gotobi) |
| E1 | +1.97 | +0.78 [-0.30, +1.86] | [-0.78, +2.33] | 0.39 | 0.76 | 0.67 | +1.28 | 0.65 | unclear / flat | PRE discovery |
| L4-G-d | +3.14 | +2.06 [-2.39, +6.51] | [-3.40, +7.51] | 0.66 | - | 0.79 | +2.54 | 0.81 | unclear / flat | declared selector |
| J5c | +1.53 | +1.22 [+0.57, +1.88] | [+0.40, +2.05] | 0.80 | - | 1.04 | +0.48 | 0.31 | flat / flat | post hoc day filter |
| I | +1.79 | -1.93 [-6.05, +2.19] | [-8.83, +4.97] | <0 | - | 0.00 | +0.43 | 0.24 | decaying / unclear | best of 27 cells, VAL in view |
| M1 (bp rebuilt; HOLD in R) | +8.23 | +6.60 [+0.67, +12.54] | [-1.63, +14.84] | 0.80 | 0.89 | 1.50 | R +0.044 | 0.19 (R) | flat / unclear | 90k-cell scan, VAL in view |

The question was whether flat-trend effects predict HOLD retention. **No.** The flat class contains the best (C3)
and the two worst (J5c, M1) HOLD retentions. The decaying class (I) did fail. How a rule was found separates the six
rules cleanly; its 2016-24 trend does not. Selection (winner's curse) and the common 2024 dip explain the HOLD losses
better than a per-effect trend.

## The 2024 dip (post hoc, descriptive; `y2024_out.txt`)
- **35 of 49 series are below their 2016-23 mean in 2024.** Mean z -0.88. The series overlap, so this is not an
  independent count.
- **Largest drops:**
  - the Sydney legs: F19 -3.55, F20 -3.08, F21 -3.37;
  - the LBMA AM drop (M10) -3.12;
  - EURJPY midday (F11) -2.35;
  - the UK100 post-auction fade (I5) -2.24;
  - the Friday ECB slot (F5) -2.19;
  - E1 -1.69.
- **Up in 2024:** C3 in R (+0.23), gold big days (M5 +0.80), M1 (+0.32), USDJPY midday (F10 +1.08).
- **Power if 2025-26 stays at the 2024 level** (`lvl2024_out.txt`):
  - Sydney pre-leg 2.36 at the venue; J5c 1.41 at the venue, -0.35 at IC; post-leg -0.45 at the venue;
  - E1 0.25 at IC;
  - ECB rebound (F6) 2.97 at the venue;
  - L4-G-d 3.05 at IC, on 22 events with a 2.5 bp se, so meaningless.

## Demos (E1 vs L4-G-d), forecast combined with the published HOLD (`reg18_out.md`)
| demo | forecast used | combined mid (se) | net at IC | per-trade Sharpe | demo power over 1.73 y | years of demo alone for t 2.0 / 2.5 |
|---|---|---|---|---|---|---|
| E1 | T1 2016-24 | +1.00 (0.48) | +0.38 | 0.025 | 0.53 | 24 / 38 |
| E1 | T2 2004-24 | +1.44 (0.35) | +0.82 | 0.054 | 1.13 | 5.4 / 8.4 |
| E1 | Sharpe trend | +1.29 (0.55) | +0.67 | 0.044 | 0.93 | 8.0 / 12.5 |
| L4-G-d | T1 | +2.41 (1.39) | +1.38 | 0.126 | 0.83 | 10.0 / 15.5 |
| L4-G-d | Sharpe trend | +2.52 (1.35) | +1.49 | 0.136 | 0.90 | 8.5 / 13.3 |

At the venue cost (EURUSD 0.20, XAU 0.60): E1 needs 2.4-5.6 years and L4-G-d 5.1-5.8 years for t 2.0.

## Files
Scratch folder: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r18/A/`.
- `lib18.py`: prices (panel mid; Dukascopy M1/H1 bid cut at 2016), event execution, yearly series, WLS trend, breaks,
  forecast, classes, power.
- `build18.py`: every effect's rule. It reuses round 12 J `effects.py` (SGE, Sydney, MOC, ASX, BTC, settlement), the
  round 12 L rows (L1 SGE dip, L4G gold big days, L6L USTEC, L7 CNH), the round 13 P rows (JP225, DE40, XTI) and the
  round 15 V G.npy cells (LBMA, COMEX, index opens and closes, XTI). Output: `rows_<id>.pkl`.
- `c3r.py`: C3's registered trades, IS + VAL rows only, keyed by gotobi day.
- `analyse18.py`, which writes `analyse18_out.md` (per effect: yearly means and every statistic) and `res18.pkl`.
- `table18.py` -> `table18_out.md`; `final18.py` -> `final18_out.md` (the main table).
- `reg18.py` -> `reg18_out.md` (registered rules, Spearman, demo arithmetic).
- Post hoc: `y2024.py` -> `y2024_out.txt`; `lvl2024.py` -> `lvl2024_out.txt`.
- Run from the repo root: `PYTHONPATH=.:<scratch>/r18/A research/.venv/bin/python <scratch>/r18/A/<script>`.
