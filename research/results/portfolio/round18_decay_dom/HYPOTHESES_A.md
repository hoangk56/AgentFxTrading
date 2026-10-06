# Round 18, stream A: decay forensics, hypotheses and methods

Written 2026-10-06 02:58 UTC (from `date -u`), before any round-18 number was computed. Stream A rebuilds the
yearly mid effect of existing effects from prices, so it fixes its trend tests here first. HOLD (2025-01-01 onwards)
is not loaded: the IC panel ends 2024-12-31, Dukascopy M1/H1 is cut at 2016-01-01, the C3 trade list is filtered to
IS + VAL rows at read time. Published HOLD readings (PREREG files of rounds 12-13, prereg_swing_v2.md,
prereg_month_end_usd_2026-09-27.md) are used as published numbers only.

## Effects rebuilt (rows of round16_income_flows/STREAM_X.md, same side and window as the source)
Order of priority (data and power first):
1. Reference: **C3** gotobi JPY basket. (a) mean R per leg by year from trades_C3_gotobi_jpy_basket.csv (IS + VAL
   rows only), the unit of the published HOLD retention 0.88; (b) mid bp per leg rebuilt on the rule (long 18:00 UTC
   d-1 -> 00:55 UTC, short 00:55 -> 02:55 UTC, gotobi days as `swing_rules.gotobi_days`, no stop) on the panel
   2016-24 and on Dukascopy M1 2004-15.
2. Registered rules with a published HOLD: **E1** (F1), **L4-G-d** (M5), **J5c** (F20), **I** (F17), **M1** (month-end
   value-date USD, 3rd-to-last weekday, buy USD 10:00-13:00 UTC on USDJPY, USDCHF, EURUSD; rebuilt at mid without the
   stop, PRE from Dukascopy M1).
3. The other STREAM_X rows that are clock windows on panel symbols: F2, F4, F5, F6, F7, F9, F10, F11, F12, F13, F14,
   F15, F16, F18, F19, F21, F22, F23, M1-SGE, M2, M3, M6, M7, M8, M9, M10, M11, M12, I1-I10, I13, E1-XTI, E2, C1.
   Rows whose rule needs data or a definition I cannot rebuild faithfully (F3, F8 selectors, F24-F29, M4, I11, I12,
   C2) are reused from earlier rounds' saved daily rows if they exist, else listed as not rebuilt.
4. PRE 2004-15 where Dukascopy covers the symbol at the needed resolution: M1 for EURUSD, USDJPY, EURJPY, GBPJPY,
   USDCHF; H1 for hour-aligned windows on GBPUSD (F16). No PRE for AUD/NZD 15-min legs, metals intraday minutes,
   indices, energies, crypto.

Each effect is reused from saved daily rows of rounds 12-15 (rows_*.pkl, r15/V G.npy) where they exist; otherwise
rebuilt with the same convention (price at time t = close of the last M1 bar ending at or before t, at most 10 min
stale; mid in the panel, Dukascopy bid in PRE).

## Unit and yearly series
- Per event: the mid move in bp on the fixed side; multi-leg rules (Sydney AUD+NZD, I, M1, C3 basket) are summed per
  UTC day and expressed per leg (day sum / legs), with t clustered by day.
- Year y: mean m_y, se_y = sd / sqrt(days), n_y.

## Trend model (fixed now)
- **T1 (primary)**: weighted least squares of m_y on (y - 2020) over 2016-2024 (9 points), weights 1 / se_y^2. Slope b
  in bp per year, se scaled by max(1, sqrt(chi2 / dof)) (over-dispersion between years), t = b / se.
- **T2**: same over 2004-2024 where PRE exists (21 points).
- **Break tests** (Welch t on day-level values, one-sided reading = decay): B16: PRE 2004-15 vs 2016-24; B20: 2016-19
  vs 2020-24; B21: 2016-20 vs 2021-24. Both B20 and B21 are reported (2 tests; |t| >= 2.24 needed at 5 % for the pair).
- **Ratio** L3/F3 = mean 2022-24 / mean 2016-18 (day-level pooled means); PRE: mean 2013-15 / mean 2004-06 too.

## Forecast for 2025-26 (fixed now)
- HOLD = 2025-01-01..2026-09-24, centre ~2025-11 (x* = 5.36 years after mid-2020 in T1's units, i.e. 2025.86 minus
  the 0.5 year-centre offset).
- **F-trend (primary)**: T1 extrapolated to x*: f = a + b x*. Interval for the expected effect: f +/- 1.645 se_fit
  (90 %). Predictive interval for a 1.73-year HOLD reading: f +/- 1.645 sqrt(se_fit^2 + sd^2 / n_HOLD), n_HOLD =
  1.73 x trades a year.
- F-flat: the VAL mean (2022-24); F-all: the 2016-24 mean. Reported next to F-trend; the trend forecast is the
  decay-adjusted one.
- Forecast net Sharpe per trade = (f - c) / sd_VAL; power = Sharpe x sqrt(1.73 x trades a year). Costs: c = IC's
  VAL-era cost as in STREAM_X column "cost IS / VAL" (scenario a) and STREAM_X's venue cost (scenario d). Power also
  at the lower and upper ends of the 90 % interval of f.

## Classification (fixed now)
- **Flat (gotobi-like)**: T1 slope t > -1.0 AND L3/F3 >= 0.7 AND neither B20 nor B21 t <= -2.0 (and, where PRE
  exists, PRE mean > 0 with B16 t > -2.0 or PRE larger, which is decay into 2016 and is reported separately).
- **Decaying**: T1 slope t <= -2.0, OR L3/F3 < 0.5 with B21 t <= -2.0.
- **Unclear**: everything else.
- Expectation written before computing: C3 flat; E1 flat (PRE-discovered, VAL/IS 1.09); Sydney V flat in 2016-24
  (VAL/IS 0.90-1.12) despite J5c's HOLD 0.31; L4-G-d, I, M1, the WM/R GBPUSD leg, HK50, JP225, XTI, BTC decaying.

## The question (fixed now)
Do flat-trend effects predict the HOLD retention of the registered rules? For the six registered rules with a
published HOLD (C3 0.88 in R, E1 0.65, L4-G-d 0.81, J5c 0.31, I 0.18, M1 0.19 in R), compare (i) the class, (ii) the
F-trend forecast retention f / VAL mean, with (iii) the published HOLD / VAL. The answer is "yes" if the flat rules
have higher published retention than the decaying ones and the published HOLD mid lies inside the predictive interval
for most rules; "no" if retention is unrelated to the class (e.g. J5c flat yet 0.31). With 6 rules this is
descriptive: Spearman rank of forecast vs published retention is reported, not tested.

## Pre-registration rule
A fresh PREREG_DRAFT is written only if an effect meets LIVE or DEMO on IS/VAL with its forecast size (F-trend, IC
cost): IS net t >= 2.5 / VAL net t >= 1.5 / power >= 3 on the forecast size for LIVE; IS net t >= 2.0, VAL net > 0 and
forecast net > 0 for DEMO, and it must not be an already registered rule. The random-entry control and x1.5 / +1 min
checks of the source round are cited, not redone.

## Multiple testing
~50 effects x 3 tests (T1, B20, B21): about 2.5 trend t-values beyond 2 by chance in either direction; read single
slopes with that in mind. The ranking is descriptive.

## Post-hoc addition (written 2026-10-06 03:05 UTC, after the bp tables were seen)
Seen first: C3 in bp has L3/F3 0.65 (2016 alone +9.3 bp) while C3 in R (stop = 3 x ATR, i.e. volatility-scaled) has
0.85. A bp effect can shrink because volatility fell, not because the flow left. Added, for every effect: the yearly
per-trade Sharpe at mid (mean_y / sd_y), its trend (WLS on year, weights n_y, i.e. se_y ~ 1 / sqrt(n_y)), its L3/F3,
and a forecast of the 2025-26 mid Sharpe by the same extrapolation. Power at a cost is then f_Sharpe - cost / sd_VAL.
This is a robustness reading of the classification, not a new test; the bp classification stays the primary one.

## Post-hoc addition 2 (written 2026-10-06 03:07 UTC, after the yearly series were seen)
Seen first: 2024 is the lowest year since 2016 for the three Sydney V legs and below 2016-23 for most rows. Added,
descriptive only: per effect, z of the 2024 mean against 2016-23 (Welch), the count of rows with 2024 below 2016-23,
and the forecast power if 2025-26 stays at the 2024 level (for the rows that rank highest at a venue or at IC). Not a
test (one year, chosen after looking; rows overlap).
