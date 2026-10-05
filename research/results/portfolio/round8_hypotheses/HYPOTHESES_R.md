# Stream R hypotheses: exact rules and cell grids (written 2026-10-04 ~18:10 UTC, before any return was computed)

Mechanisms and sources are in STREAM_R.md (R1-R5). This file fixes the exact definitions and every cell, so the
cell counts in the findings are the real search size. Data looked at before writing this: only data-quality facts
(trading hours per symbol, first dates, price-jump glitches; scripts r0_*.py), no strategy returns.

## Common definitions (all families)
- Bars from the shared M1 panel: M5 close = log mid of the bar's last minute, forward-filled; M15/H1 = the M5 bar that
  ends them. A symbol is "quoted" at a decision if it had a quote in the last 5 minutes. Returns are taken between
  consecutive bars where all symbols of the construction are quoted (joint bars), so closed periods are skipped and
  the reopening gap lands in the first joint bar.
- Data errors: spike-and-revert closes > max(10 %, 50 x median |r5|) from both the previous and next 24 quoted
  closes are treated as unquoted (UK100 2017-04-17 00:00-01:05 also nulled by hand: a -41 % quote for 55 min).
- Decision at a bar close, fill at the first quoted minute after it (within 5 min) at mid +- half the actual spread
  of that minute; +1 min latency variant. Commission 0.6 bp per round trip for FX and metals, 0 otherwise.
- Swap: every weekday 17:00 New York rollover in (entry, exit] costs swap_frac_at(symbol, side, entry day) per leg
  (triple on Wednesday for FX/metals, Friday for the others, as research/specs.rollovers).
- Statistics: per trade bp at mid (gross) and net; t clustered by entry UTC day; per-trade Sharpe = net mean / net
  sd; power = Sharpe x sqrt(expected HOLD trades = IS+VAL trades per month x 21). A pair trade's bp are per unit of
  Y notional with |beta| units of X (sign and scale do not change t, Sharpe or net-vs-cost).
- Eras: IS 2016-2021 (choose), VAL 2022-2024 (check once per family). HOLD never loaded.

## R1 intraday pairs (return spread, rolling hedge ratio)
Pairs (Y/X): EURUSD/GBPUSD, EURUSD/USDCHF, AUDUSD/NZDUSD, XAUUSD/XAGUSD, XAUUSD/XPTUSD, XTIUSD/XBRUSD, US30/US500,
US500/USTEC, DE40/UK100, US500/DE40, JP225/HK50, BTCUSD/ETHUSD, AUDUSD/XAUUSD, USDCAD/XTIUSD, USDJPY/JP225.
- beta_d: no-intercept OLS of joint 15-min r_Y on r_X over the 20 trading days before day d (refit 00:00 UTC).
- e_t = r_Y - beta_d r_X on joint bars of B in {M5, M15, H1}. S_t = sum of e over the last W days of joint bars,
  W in {1, 3, 5} (W days = W x the pair's median joint bars per weekday in 2016-2017 for that B).
- sigma_d = sqrt(W) x RMS of the rolling 1-day residual sum (beta_d applied) sampled at every H1 joint bar of the
  20 days before d. z_t = S_t / sigma_d.
- Entry: |z| crosses up through z_in in {2, 2.5, 3} (fresh crossing, flat). Short the spread if z > 0.
- Exit (first of): z back through x in {0, 0.5} toward zero; time T in {4 h, 1 d, 5 d}; stop variant {off, on: |z|
  >= z_in + 2 in the entry direction}.
- Legs: both (pair) or one-leg (the leg with the lower median IS round-trip cost, side implied by the spread).
- Cells: 15 x 3 B x 3 W x 3 z_in x 2 x x 3 T x 2 stop x 2 legs = 9,720.
- R1-diag (no trading): variance ratio of e at 1 h, 4 h, 1 d, 5 d vs its M5 variance, IS and VAL (< 1 = reversion).

## R2 factor-residual stat-arb (Avellaneda & Lee 2010) on H1
- Blocks: B13 = 10 FX + XAU XAG XPT; B8 = 8 indices; B26 = all 26 (a symbol joins a window only if quoted on >= 90
  % of its H1 bars). H1 returns on bars where >= half the block is quoted (zero for a closed symbol, gap at reopen).
- Refit 00:00 UTC on the trailing 60 calendar days: standardize, correlation PCA, top k in {1, 2, 3} eigenportfolios
  (Q = v / sigma), factor returns F; per symbol OLS of R on [1, F] -> residual eps; X = cumsum eps; AR(1) of X on the
  OU window (60 d, or the last 5 d) -> b, a, var(zeta); valid if 0 < b < 1 and 1/kappa < half the OU window; m =
  a/(1-b), sigma_eq = sqrt(var zeta / (1-b^2)). Intraday: X_t = X_end + cumsum of today's eps (day-start fit);
  s = (X_t - m) / sigma_eq.
- Trading each H1 close: enter |s| > s_in in {1.25, 2.0} against s (largest |s| first, <= 3 open per block); exit
  long at s > -0.5, short at s < 0.5, or after 5 days, or when the next refit is invalid.
- Variants: single (trade the symbol) vs hedged (P&L = residual eps: symbol minus beta x factor basket; costs of
  all basket legs; diagnostic only, it needs up to 26 legs and breaks the 3-position cap).
- Cells: 3 blocks x 3 k x 2 OU windows x 2 s_in x 2 variants = 72.

## R3 currency strength meter (H1)
- 10 FX pairs (all quoted); 8 currency returns = pinv(A) r (A: +1 base, -1 quote; min-norm = sum to zero).
- Strength over L in {4, 8, 24} H1 bars. The traded pair = the quoted pair with the largest |strength(base) -
  strength(quote)| (= strongest/weakest when that pair is quoted). Momentum: long the stronger; reversal: opposite.
- Hold H in {4, 8, 24} h, one position at a time, re-enter at the exit bar; no entries with decision hour 20:00-
  22:59 UTC (rollover spreads), positions may be held through.
- Filter variant: enter only when that gap >= the 90th percentile of the max-gap series over the previous 60 days.
- Cells: 3 L x 3 H x 2 directions x 2 filters = 36 (18 independent: the directions are sign mirrors at mid).

## R4 commodity-currency fair value (H1)
- Models: AUDUSD ~ XAUUSD + US500; USDCAD ~ XTIUSD + US500; NZDUSD ~ AUDUSD. No-intercept OLS of joint H1 returns
  over the 60 days before d (refit 00:00 UTC). Residual e; S over the last W in {1, 3, 5} days; sigma as R1 (sqrt(W)
  x RMS of rolling 1-day residual sums over the 60-day window); z = S / sigma.
- Entry |z| crosses up through z_in in {2, 2.5}: trade the currency toward fair value (short Y if z > 0). Exit z
  through 0 or T in {1 d, 5 d}.
- Variants: single (Y only) vs hedged (Y + beta-weighted regressors: 3 legs, 2 for NZD/AUD).
- Cells: 3 models x 3 W x 2 z_in x 2 T x 2 variants = 72.

## R5 index dispersion (session residuals)
- Groups and sessions: US {US30, US500, USTEC} 09:30-16:00 New York; Europe {DE40, UK100} 08:00-16:30 London;
  Asia {JP225, HK50, AUS200} 01:30-05:00 UTC (inside all three cash sessions all year).
- Session return r_i = close at session end - close at session start (M5 closes). Factor f = equal-weight mean of
  the group; u_i = r_i - beta_i f, beta_i = OLS over the previous 60 sessions. Leader = max u, laggard = min u.
- Trades decided at the session end: pair (long laggard / short leader for reversal, the reverse for continuation,
  equal notional), laggard only, leader only. Horizons: close -> next session close (pays the night), and next
  session open -> close (no night). Filter: all sessions vs leader-laggard gap >= its trailing 60-session median.
- Cells: 3 groups x 3 constructions x 2 directions x 2 horizons x 2 filters = 72 (36 independent).

Selection and verdict: per family, the best IS cell by net day-clustered t (and per pair/model for R1/R4) is shown
with its VAL; any cell that clears the brief's full bar gets the random-entry control (>= 200 seeds), spread x1.5,
+1 min latency, years, and power before a pre-registration is written.

Note added before computing (18:20 UTC): "day" in R1/R2/R4 is the FX trading day that starts at 22:00 UTC (so the
Sunday-evening open belongs to Monday); the daily refits happen at that boundary instead of 00:00 UTC. Same
causality (only data before the boundary).

Note (R5, before any Asia number): HK50 is not quoted at 04:00-05:00 UTC (Hong Kong lunch), so no Asia session
could be formed with a 05:00 end; the Asia window becomes 01:30-03:55 UTC (HK50 cannot be traded in the minute after 04:00; still inside all three cash sessions).

## Post-hoc follow-ups (written 2026-10-04 ~19:10 UTC, AFTER the R1-R5 IS and VAL numbers were seen; not pre-registered)
Seen: R2 B13 single k3/5d has a small mid edge in both eras (+2.3/+2.4 bp, t 2.4/1.8) eaten by cost (XAG/XPT
trades cost 4-20 bp), and by entry hour the mid edge sits in 03-17 UTC while 18-23 UTC entries lose (rollover
spreads). R3 short-horizon reversal (L4 H8) is +1.7/+1.9 bp at mid, t 2.7/2.2, net ~+0.3/+0.6.
- R2b: Avellaneda-Lee on B11 = 10 FX + XAUUSD (the PRE universe; drops XAG/XPT), k = 3, OU 5 d, s_in 1.25, exit
  |s| < 0.5 or 5 d, <= 3 positions, single symbol. Cells: entries any hour / entries 07:00-16:59 UTC only (2 cells).
- R3b: R3 reversal L4 H8 (no filter) with entries 07:00-16:59 UTC only (1 cell).
Because IS and VAL were both seen, they cannot validate these. The only clean test is PRE (Dukascopy 2004-2015 H1
bid, 11 symbols, never opened in this stream), registered here before any PRE number:
- PRE costs: bid-close to bid-close returns on H1 bars (fill at the decision bar's close, zero latency) + half of
  IC's 2016-17 median spread by UTC hour at each end + 0.6 bp commission; swap = 1 %/yr markup per side per
  rollover (-0.28 bp, triple Wednesday; no FRED rates before 2014 are local and no network), carry differential
  ignored (sides are ~random vs carry). The IC IS/VAL numbers are also reported on this same close-to-close
  convention so the eras compare.
- PRE bar (for the 07-17 UTC cells; the all-hours cell is reported only): net > 0 with day-clustered t >= 2.0
  over 2004-2015, >= 8/12 years net > 0, net > 0 at spread x1.5, and pooled per-trade Sharpe giving power >= 3 at
  the IC trade rate. If it passes, a pre-registration text is written and HOLD stays closed (the lead decides).
