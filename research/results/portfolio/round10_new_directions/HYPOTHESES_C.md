# Round 10, stream C: combine sub-cost FX effects and trade only when the combined forecast clears that minute's cost

Written 2026-10-05 17:52 UTC, before any stream-C number was computed. HOLD (2025-01..2026-09) stays closed: the
shared panel stops at 2024-12-31 and no other price file is opened past that date. Eras: IS 2016-2021 (all
choices), VAL 2022-2024 (checked once per family for the IS-chosen cell), PRE 2004-2015 (Dukascopy) only as an
optional extra check for a survivor, on the components that its 5 M1 pairs allow.

## Why this could escape the standing limits

Rounds 3-8 judged each FX effect alone; each was 0.02-3 bp at mid against ~0.7-1.5 bp of round-trip cost. A trade
pays its cost once, but the expected returns of (roughly) independent signals add, and the cost varies by minute
(EURUSD's median spread at the minute close is 0.0 bp, so the cost is often just the 0.6 bp commission). A book
that sums several documented signals per pair and enters only when |forecast| exceeds k x the expected executable
cost of that minute could net positive although no component does alone. It also trades often (hundreds to
thousands of trades a year over 10 pairs), which is what the power rule needs. The risk is overfitting: signs come
from the earlier rounds / literature, scales are causal z-scores, and only k, h (and in C2 the ridge weights) are
chosen, on IS only. None of the components uses the Tokyo 09:55 fix or gotobi days (C3's mechanism).

## Common definitions (all hypotheses)

- Universe: the 10 FX pairs of the panel: AUDJPY AUDUSD EURJPY EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDCHF USDJPY.
  Mid = (bid close + ask close)/2 and spread = ask - bid at each minute's last tick (shared panel).
- Decision minutes t: the 15-minute grid (:00 :15 :30 :45). Signals use data up to the close of minute t only. Fill
  at the close of minute t+1 (latency check: t+2), exit at the close of minute t+1+h. Decision windows: 00:00-20:45
  UTC on Mon-Fri and 23:00-23:45 UTC on Sun-Thu (for the Sydney open); a trade is taken only if its exit is at or
  before 20:55 UTC, so no hold crosses the 21:00/22:00 UTC rollover and no swap is paid. Hold h in {15, 60, 240}.
- Quotes: no entry if the pair has no bar at t or at t+1 (known at fill time); the exit uses the last quote at or
  before the exit minute (forward fill, never drop).
- Net P&L per trade (bp of price) = side x mid return - half spread at the fill minute - half spread at the exit
  minute (both the ACTUAL spreads of those minutes) - 0.6 bp commission. Stress: spread x1.5; +1 minute latency.
- Expected cost used by the gate (only information known at t): cost_t = 0.5 x spread observed at minute t + 0.5 x
  the trailing 20-trading-day median spread of that pair at the exit's minute of day + 0.6 bp.
- sigma_h(t): trailing 20-trading-day RMS of the pair's h-minute mid return starting at the same clock time
  (previous days only).
- Bots: one bot per pair, at most 1 open position (no new entry while one is open); C4b is one bot with cap 3. All
  holds <= 4 h (well under 5 days). Lot 1x (a 0.5-2x scaling by forecast strength is reported as a variant only).

## Components (sign fixed before looking: positive x = expected rise of the pair over the hold)

| id | mechanism (source, earlier number) | definition of x at decision t |
|---|---|---|
| REV | short-horizon currency-strength reversal (round 8 R3, 4 h lookback / 8 h hold, mid +1.68 t 2.7 IS / +1.94 t 2.2 VAL) | -(pair mid return over the last 240 min) |
| RES | Avellaneda-Lee residual reversal (round 8 R2, k 3, OU 5 d, mid +2.28 t 2.4 / +2.44 t 1.8) | each UTC day, PCA on the previous 20 days of standardized 15-min grid returns of the 10 pairs, top 3 eigenvectors; residual return = return minus its projection; X = cumulative residual over the last 5 days (480 grid steps); x = -(X_t - mean X over those 5 days) / sd of X over those 5 days (the s-score) |
| USDF | a lagging USD pair catches up with the dollar factor (round 8 L2h-ii, +0.042 bp per sd t 11.8 / +0.035 t 7.1, k1 h15) | 7 USD pairs only: u_j = USD-signed 1-min return at minute t, F = mean of u_j; x = -(u_j - F) converted to the pair's direction; 0 for crosses |
| FIXV | USD rises into a fix and falls after (Krohn, Mueller & Whelan 2024; round 3 ECB 14:15 CET EURUSD +1.1 bp t 2.9 / +1.2 t 2.1; round 4 15 min into the ECB fix t 5.5 / 4.2) | fixes: ECB 14:15 Frankfurt time, WM/R 16:00 London time (DST-aware). Profile g = +1 (USD up) per minute in [fix-30, fix), -1 in [fix, fix+30); x = mean of g over the hold minutes, converted to the pair's direction; 0 for crosses |
| HOME | home-hours depreciation (Ranaldo 2009; earlier: EURUSD European hours -1.5 bp t -2.5 IS) | home hours local 08:00-17:00 for EUR (Frankfurt), CHF (Zurich), GBP (London), USD (New York), CAD (Toronto); 09:00-17:00 for JPY (Tokyo), AUD (Sydney), NZD (Wellington), weekdays. Per currency h_c = -1 inside its home hours; pair g = h_base - h_quote; x = mean of g over the hold minutes |
| WED | high-yielder rises into the Wednesday rollover (round 3 W1, 12:00-16:55 NY: +2.2 bp t 3.1 / +1.4 t 1.6) | g = sign(r_base - r_quote) (FRED short rates of the previous calendar month) inside Wednesday 12:00-16:55 New York time, else 0; x = mean of g over the hold minutes |
| SYD | Sydney-open V (round 4: NZDUSD 15 min before -1.7 bp t -13.2 / -9.3, AUDUSD -1.6 t -13.1 / -7.5; +1.2..+1.7 bp after) | AUDUSD, NZDUSD, AUDJPY only: g = -1 in [09:45, 10:00) Sydney time, +1 in [10:00, 10:15), weekdays (Sydney date); x = mean of g over the hold minutes |
| HKS | adaptive same-slot periodicity (Heston, Korajczyk & Sadka 2010; round 7 C: 40-day slope t EURJPY +4.2 / +2.6, 0.02-0.3 bp per slot) | mean of the pair's mid return over the same clock window [t+1, t+1+h] on the previous 40 weekdays |

z-score (causal): z = clip(x / RMS of x over the previous 60 calendar days of that pair's decision points, -3, 3).
(Deterministic components are 0 most of the time, so they reach the clip when active.)

## C1 equal-weight composite (no fitting of weights or signs)

S = sum of the pair's available z. Enter side sign(S) when |S| >= k x cost_t / sigma_h(t). Grid: h in {15, 60,
240} x k in {1, 2, 4, 8, 16, 32, 64, 128} = 24 cells. Choose the cell with the highest IS day-clustered t of net
P&L among cells with >= 100 trades a year; check that one cell on VAL.

## C2 ridge composite fit on IS

y = forward mid return over [t+1, t+1+h] / sigma_h, regressed on the 8 z's pooled over pairs and IS decision
points, no intercept, ridge lambda = 1e-3 x n. Forecast in bp = (z . beta) x sigma_h. Enter side sign when
|forecast| >= k x cost_t. Grid: h in {15, 60, 240} x k in {1, 1.5, 2, 3} = 12 cells, chosen on IS (in-sample fit;
an expanding walk-forward inside IS, fit on years < y and trade year y for 2018-2021, is reported to show the
in-sample optimism). Report the IS coefficients with day-clustered t; VAL once with the all-IS beta.

## C5 ("CT", cost timing per component; the brief's C3x, renamed to avoid "C3")

Each component alone (8) x h in {15, 60, 240}: enter side sign(z) when |z| >= 2 AND the spread observed at t is
the cheapest available (== 0 where the pair has zero-spread minutes in the trailing 20 days at that minute of
day, otherwise <= that pair's trailing 20-day 10th percentile at that minute of day) AND the tick count at t is >=
its trailing 20-day median at that minute of day. Exit: at the scheduled minute if the spread observed one minute
earlier passes the same cheapness test, otherwise wait up to 10 minutes for a minute whose observed spread passes
and exit one minute after it (forced at +10 or 20:55 UTC). Reference: the same 24 cells without the cost timing.
Question: does any single component net positive once it trades only at the cheapest minutes?

## C4 cross-pair versions

- C4a dollar factor at the cheapest pair: U = mean over the 7 USD pairs of their z-sums converted to USD-signed
  (USD components only: USDF, FIXV, HOME(USD part), plus REV/RES/HKS USD-signed); trade USD in the one USD pair with
  the lowest cost_t when |U| >= k x cost_t / sigma_h of that pair. h in {15, 60, 240} x k in the C1 grid = 24 cells.
  One bot, 1 position.
- C4b one bot, cap 3: at each decision minute rank all pairs by |C2 forecast| / cost_t and open up to 3 positions
  (pairs not already held) whose ratio >= k. h x k as C2 = 12 cells.

## Reporting and bars

Per hypothesis: mid and net bp per trade, day-clustered t (IS, VAL), trades a year, per-trade net Sharpe, power =
Sharpe x sqrt(trades a year x 1.73) and per-day power = daily Sharpe x sqrt(1.73 x trading days a year), years net
positive, random-entry control (200 seeds: same pair, side, hold, weekday and session, random date in the same era
and random 15-min slot in the same session; the share of seeds whose mean net is below the real one), spread x1.5,
+1 minute. Cells tried per family and the chance benchmark (expected max |t| of K normals; for the C1/C2 families
also a sign flip per UTC day shared by all pairs and cells). The C3 correlation (daily and monthly P&L, IS+VAL) for
anything that survives. LIVE / DEMO bars as in the brief; if met, write PREREG_DRAFT_C_<name>.md and stop that family.

## Additions (each written before its numbers)
- 2026-10-05 18:20 UTC, after the per-component mid screen (screen.out) and before any C1/C2/C4/C5 number. Execution
  variant "extend", reported next to the base rule for every C1/C2/C4 cell, not a separate selection: when a
  position reaches its exit decision (t + h, on the grid) and the gate fires again on the same side, the hold is
  extended by h at no cost (the bot simply keeps the position), subject to the same 20:55 UTC cutoff. The chosen
  cell is chosen on the base rule; "extend" is reported for that cell only.
- 2026-10-05 19:05 UTC, post hoc with respect to the pooled C1/C2/C4/C5 results (all negative or below the bar;
  per-pair results not looked at). C6 cheapest pairs only: the C1 and C2 rules unchanged (same z, same IS beta, same
  grids) but traded only in EURUSD and USDJPY, the two pairs with the lowest median minute-close spread in the
  shared spread_table (0.00 and 0.08-0.10 bp), so their cost is mostly the 0.6 bp commission. Selection as C1 / C2
  on IS; VAL once. Plus a diagnostic, not a hypothesis: the commission (bp round trip) at which the IS-chosen and the
  walk-forward C2 cells would break even.

## Outcome (2026-10-05 19:20 UTC)
No family met LIVE or DEMO on IS/VAL; no PREREG draft. Best IS net t +1.65 (C4a h240 k128, VAL -0.66 bp). Numbers
and scripts: scratchpad r10/C/STREAM_C.md.
