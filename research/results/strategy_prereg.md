# Pre-registration (written before any 2026 result of these rules was looked at) — 2026-09-25

Discovery used 2025 only (P1). Holdout = 2026-01-01..2026-09-24 (P2 = Jan–May, P3 = Jun–Sep).

## K1 (primary): FX weekly fade
8 FX pairs (AUDUSD EURUSD GBPUSD USDCAD AUDJPY EURJPY GBPJPY USDJPY). D1 bars cut at 22:00 UTC.
z = (C - C[5]) / ATR20(D1, SMA of TR). |z| > 1.5 -> trade against z at the next bar open.
SL = C -/+ 3 x ATR20, no TP, time exit at the close of the 5th D1 bar after the signal. One position per pair.
2025: n 220, mean ~ +0.10R.
Pass (holdout): 2026 pooled mean R > 0 with t >= 2; P2 > 0 and P3 > 0; >= 5/8 pairs mean > 0 in 2026.
K1b = same with SL 2 x ATR (sizing-feasible variant), reported, not a separate pass.

## Grid check
The 2025 D1 grid (L 3-6, H 2-6, Z 1-2, SL 2/3) and H4 grid rerun on 2026: report corr(IS, OOS) across cells
and the fraction of cells positive OOS.

## K2 (exploratory, weak IS): index ORB candle N60, exit at session close
US30 USTEC DE40 UK100; direction of the first 60-min candle, entry at its close, stop at the other end of the
range. 2025: n 1025, +0.13R, t 2.3 (best of 16 ORB variants -> expected to shrink).
Pass: same as K1 (2026 t >= 2, P2 > 0, P3 > 0, >= 3/4 indices positive).

## Result of K1/K2 on 2026: both FAIL (K1 2026 -0.073R t -1.8, 1/8 pairs; K2 +0.005R). FX fade grid: 0 % of D1
cells positive in 2026, corr(IS, OOS) -0.40 -> 2025 FX mean reversion was a regime, it flipped in 2026.

## Wide bank (552 configs x groups, all 3 periods seen): 0 strict passes. Best consistent clusters:
BTC shock-bar follow (M15-H1), XAU H4 trend. Chosen from a 2025-2026 plateau:

## BTC-S1 (pre-registered before looking at Sep-Dec 2024 or any tick-level sizing)
BTCUSD M15 bid bars. move = (C - C[1]) / ATR20(M15, SMA of TR). |move| > 2.5 -> follow at the next bar open.
SL = C -/+ 2 x ATR20, TP = C +/- 2 x ATR20, time exit at the close of bar i + 12 (3 h). One position at a time.
Unseen test: Sep-Dec 2024 M15 zbars (bar-level, spread = 2025 median). Pass: mean R > 0.

## BTC-S1 result on Sep-Dec 2024: n 60, +0.218R, t +1.8 -> pass (mean > 0). Tick-level $2000: 2025 +0.100R
(+10.4 %, DD $103), 2026 +0.093R (+8.4 %, DD $67), 15/21 months positive.

## XAU-T1 (pre-registered before Jul-Dec 2024 and before any long/short split)
XAUUSD H4 bid bars (UTC-aligned). Close above the prior 30-bar high (first bar of the break) -> buy; below the
prior 30-bar low -> sell; entry at the next bar open. SL 1.5 x ATR20(H4), no TP, time exit after 12 H4 bars.
Unseen test: Jul-Dec 2024 M15 zbars resampled to H4, spread 0.10. Pass: mean R > 0.

## Round 2 (2026-09-25, "find more candidates")
Pairs/stat-arb (14 pairs, M15/H1, z-score of rolling-OLS log spread): nothing in 2025, not even gross. Dropped.
Lead-lag M1/M5: significant correlations but 1-2 spreads in size; rule tests: only BTC->USTEC M5 mildly +.

### X1 (pre-registered before any 2026 look): cross-sectional FX reversal
8 FX pairs, H4 bars (UTC-aligned, closes avoid the 21-22 UTC rollover). Currency strengths = least-squares fit of
the 30-bar log returns of the 8 pairs (6 currencies, sum 0). Pair score = strength(base) - strength(quote),
divided by the pair's ATR20/price. Every 30 bars (5 days): trade the 3 pairs with the largest |score| AGAINST
the score, hold 30 bars, no SL. 2025: n 159, +0.74 ATR/trade, t 2.4.
Pass: 2026 pooled mean > 0 with t >= 2, P2 > 0, P3 > 0.
X1 result: 2026 pooled -0.086 (P2 -0.25, P3 +0.13) -> FAIL.

### VB1 (pre-registered): index volatility breakout
US30 USTEC DE40 UK100 cash sessions. Stop entry at session open +/- 0.35 x mean range of the last 5 sessions
(first side touched, filled at the next minute open), SL at the session open, exit at the session close.
Pass: 2026 pooled mean R > 0 with t >= 2, P2 > 0, P3 > 0, >= 3/4 indices positive in 2026.
VB1 result: P1 +0.099 (t 2.1), P2 +0.081, P3 -0.138 (t -1.9); 2026 pooled -0.017 -> FAIL.

### WF1 (pre-registered procedure, fixed before running): walk-forward ridge model
Per symbol, bid bars of TF (M15 main; H1 variant). Features at the close of bar i (causal): r1, r4, r16, r64
(C - C[i-k]) / ATR20; range position over 20 bars; ATR5/ATR20 - 1; body/range; (C - EMA50)/ATR20; RSI14/50 - 1;
tick-activity ratio (bar ticks / mean of last 96 bars) - 1; r1 x activity; shock = sign(r1) * [|r1| > 2];
sin/cos hour of day. Target: (C[i+4] - C[i]) / ATR20[i]. Ridge on standardized features, lambda = 0.1 x n,
trained on the 6 months before each calendar month, refit monthly; OOS = Jul 2025 .. Sep 2026.
Trade: |pred| above the 90th percentile of |pred| on the training months -> follow sign(pred) at the next bar open,
SL 2 x ATR20, exit after 4 bars. Symbols: all 15 (report low-cost group US30 USTEC DE40 BTC XAU separately).
Pass: OOS pooled mean R > 0, t >= 2, and each of H2-2025 / P2 / P3 > 0 for the group.
WF1 result: M15 all -0.084R (t -17.5), low-cost group -0.005R; H1 all -0.037R -> FAIL.

### FXM1 (pre-registered): regime-switching FX weekly rule ("strategy momentum")
8 FX pairs, D1 bars cut at 00:00 UTC (away from the rollover). Base signal: z = (C - C[5]) / ATR20, |z| > 1.5,
base side = -sign(z) (fade). Direction d = sign(sum R of the base FADE trades, all 8 pairs, closed in the 120
calendar days before the signal); trade side = base side x d. SL 3 x ATR20, exit after 5 bars.
Pass: pooled t >= 2 over the months with a trailing window (from ~May 2025), and H2-2025, P2, P3 each > 0.
FXM1 result: May-Dec 2025 +0.110 (t 2.9), P2 -0.102 (t -2.3), P3 -0.004 -> FAIL (switch lags the flip).

### LC1 (pre-registered): US index last-30-min fade of the mid-session move
US30, USTEC cash sessions (NY). mid = C(15:30) - C(10:00). Side = -sign(mid) at the 15:30 close (next minute open),
exit at the 16:00 session close. SL = 2 x ATR20 of 30-min bars at entry. From 2025: rank corr(mid, last30)
-11/-13 %, stable in both halves and without April.
### GF1 (pre-registered): US index opening-gap fade
US30, USTEC. gap = open(9:30) - close(prev 16:00). If |gap| > 0.1 x mean session range of the last 5 sessions:
side = -sign(gap) at the 9:31 open; TP at the previous close, SL = open +/- 1 x |gap|... (sign-wise beyond the
open by the gap size), exit at the session close. From 2025: rank corr(gap, open->close) -7/-14 %.
Pass (each): 2026 pooled mean R > 0, t >= 2, P2 > 0, P3 > 0.
LC1 result: P1 +0.040 (t 2.2), P2 +0.019 (t 0.8), P3 +0.025 (t 1.0); 2026 pooled +0.022 t 1.3 -> fails t >= 2, sign
consistent. GF1: 2026 +0.046 t 0.8 -> FAIL.
LC1 unseen check (pre-registered now): Jul-Dec 2024 US30/USTEC M15 zbars, spreads 1.2/1.0: pass = mean R > 0.
LC1 unseen Jul-Dec 2024: n 250, -0.001R -> FAIL.

### Literature anomalies (pre-registered from the papers, parameters not fitted here)
OD1 "overnight drift" (Boyarchenko, Larsen, Whelan 2023): US30, USTEC long 02:00 -> 03:00 New York, Mon-Fri;
SL 2 x ATR20(H1). OD1c: only when the prior cash session (09:30-16:00) closed below its open.
TOM turn-of-month: US30, USTEC, DE40 long over the cash session on the last trading day and the first 3 trading
days of each month (intraday, no swap); compare with the other days (long every day) as control.
MEF month-end fix (Melvin & Prins 2015): last business day of the month, 10:00 -> 16:00 London; if US30 beat
DE40 in USD over the month (US equities outperformed), sell USD (buy EURUSD, GBPUSD, AUDUSD, sell USDCAD, USDJPY);
else buy USD. SL 2 x ATR20(H1).
Pass: mean R > 0 with t >= 2 over all data (2025-2026) and positive in 2025 and in 2026; 2024 zbars where available.
Results: OD1 2025 -0.006 / 2026 +0.029 (t 2.6) -> FAIL (sign flip). OD1c same pattern -> FAIL.
TOM (R = 3 %): 2025 +0.041 (t 1.7), 2026 +0.088 (t 3.0), all +0.061 (t 3.3); other days -0.008 -> promising.
MEF: 20 events, +0.15R t 1.0 -> too few.
TOM unseen check (pre-registered now): Jul-Dec 2024 US30 USTEC DE40 M15 zbars, same rule; pass = mean > 0.

## Confirmation on 2023-2024 (pre-registered 2026-09-25, before the data arrives; cache-fill jobs #105-#114)
Rules run UNCHANGED (parameters above). Years evaluated separately and pooled.
- BTC-S1 (tick level, $2000 start each year, live sizing guardrails): pass = mean R > 0 in 2023 AND in 2024,
  and pooled 2023-2024 t >= 2.
- XAU-T1 (M1 engine, R per unit): pass = mean R > 0 in 2023 AND 2024, pooled t >= 2; the short side is
  reported separately (trend skill claim needs short-side mean R >= 0 pooled).
- TOM (US30 USTEC DE40, M1 engine, R = 3 %): pass = mean > 0 in 2023 AND 2024, pooled t >= 2, and TOM days
  above the other days in both years.

### BTC-S1 confirmation result (2026-09-25 ~14:00 UTC, ticks from jobs #105/#106)
2023: n 222, mean R +0.0001 (t 0.0), net -0.3 %, max DD $295 (Jun-Aug 2023 -25.8R); 2024: n 197, +0.107 (t 1.5),
+10.8 %. Pooled 2023-2024 +0.050 (t 1.0) -> FAIL (needs t >= 2). Spread was 5.7 bp (2023) / 4.3 bp (2024) vs
2.4 bp (2025) / 1.7 bp (2026). All four years: 0.00 / +0.11 / +0.10 / +0.09R.

### XAU-T1 / TOM confirmation result (2026-09-25 ~15:00 UTC, ticks from jobs #107-#114; DE40 needed the auto-rerun)
XAU-T1: 2023 n 64 +0.102R (t 0.5), 2024 n 56 +0.087 (t 0.5); pooled 2023-24 +0.095 (t 0.7) -> FAIL (t < 2).
  Short side pooled 2023-24 -0.092 (2023 +0.095, 2024 -0.359) -> mostly gold beta, not trend skill.
TOM: 2023 +0.047 (t 2.3) but other days +0.021 (t 2.0); 2024 -0.014 (other days +0.006) -> FAIL.
BTC-S1 (earlier): FAIL. No candidate passed the 2023-2024 confirmation.

Fixed-lot view (not a pass criterion): XAU-T1 0.01 lot $ +39 / +154 / +283 / +665 (2023..2026), max DD $387;
TOM 0.1 lot x 3 indices $ +393 / -179 / +582 / +986, max DD $369; BTC-S1 0.1 lot $ -103 / +1164 / +2154 / +260.
Post-hoc combined book (NOT pre-registered): $ +329 / +1139 / +3019 / +1911, max DD $649, 33/45 months positive.
