# Round 46, stream P: hypotheses (declared before any return)

Written 2026-10-30 07:53-08:05 UTC (`date -u` 07:53:19 at the start of writing). Brief: [BRIEF.md](BRIEF.md) row P;
general rules from round37_forced_flows/BRIEF.md. No equity or bond return has been computed or joined when this file
is written. Loaded so far: yield files parsed with the HOLD cut (rows after 2024-12-31 dropped at parse; only row
counts printed) and IC M1 load checks (bar counts only).

## Sources (robots.txt read first, 2026-10-30 07:48 UTC)
| host | robots.txt | used for |
|---|---|---|
| home.treasury.gov | `User-agent: * Allow: /` | daily par yield curve CSV, one request per year 2004..2024 (requests stop at 2024) |
| www.mof.go.jp | 404 (no restrictions) | `english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv`, JGB par yields 1Y-40Y; rows after 2024-12-31 dropped at parse |
| api.statistiken.bundesbank.de | 404 (no restrictions); www.bundesbank.de robots disallows only `/.enodia/challenge` | BBSIS Svensson zero-coupon yield on Federal securities, residual maturity 10.0 years, daily (`endPeriod=2024-12-31`, also cut at parse) |
| www.nber.org | `User-agent: *`, disallows admin / search paths only; no AI-bot rule | w33554 full text (Harvey, Mazzoleni & Melone 2025) |
| data-api.ecb.europa.eu | **disallows ClaudeBot / Claude-Web / anthropic-ai**: not used | - |
| cdn.cboe.com | robots.txt answered 403: treated as off limits, not used | - |

Pulls: 25 files, < 4 MB, ~2 minutes. No web.archive.org, no login, no e-mail in any request, UA
`Mozilla/5.0 (compatible; offline-research-script/1.0)`.

## The paper's construction (w33554, Appendix B and section 1.2; read in full text)
- 60/40 equity-bond portfolio (S&P 500 futures, 10-year Treasury note futures). Weight update
  w_{t+1} = w_t (1 + R^SP_{t+1}) / [w_t (1 + R^SP_{t+1}) + (1 - w_t)(1 + R^10Y_{t+1})].
- Threshold_delta: if |w - 60 %| >= delta the portfolio is reset to 60 % (the signal of that day is the deviation
  before the reset). Threshold signal = mean over delta in {0.0, 0.1, ..., 2.5} % (26 portfolios) of (w - 60 %),
  measured at the end of day t; predicts day t+1.
- Calendar signal: same drift, reset on the last business day of each month; its predictability sits in the last 5
  business days of the month ("week4").
- Size: Table 1 (XA = S&P minus 10y futures, multivariate with momentum and lagged return): Threshold -0.4144
  (t ~ -3.6), Calendar x week4 -0.3029, Calendar 0.0553, Momentum +0.0023, Ret_t -0.0203. 1 sd of Threshold =
  about -20 bp XA next day; split (Table 3): **equity -15.9 bp, bond +4.1 bp per sd** (Calendar: -16.9 / +2.3).
  Threshold signal sd (annualised as printed) 0.08 -> daily-level sd ~0.5 %. Significant only from the early 2000s.
- The paper's trading strategy (Table 6): XA position = mean of (-Threshold / 1.5 %) and a modified Calendar
  (sign(-Calendar) in the last 5 business days, sign(Calendar at T-4) on the first business day of the new month,
  else 0); Sharpe 1.11 in 1997-2023, **skewness 5.23**, 0.90 without 2008-09 and 2020-03 (the effect is concentrated
  in turmoil). 3:30 PM prices give "largely the same results" (footnote 28).
- International (section 3.5, Table D.14): US signals lagged one day predict MSCI ACWI ex-US with similar size.

The round 23 version (P2) set the bond return to 0. This round uses the bond leg.

## Data and timing
- Equity: IC M1 US500, USTEC, US30, JP225, DE40 (bid c / ask ca, mid used for signals and fills),
  2016-01..2024-12 (ts < 1735689600000 at load). FX controls USDJPY, EURUSD.
- Bond daily returns from yields: R_b = carry - D_mod * dy (+ 0.5 * Cx * dy^2), carry = (y10 - y_cash) * days / 365.
  US: par 10Y, D_mod and Cx of a 10-year semiannual par bond at yesterday's yield; y_cash = 3-month bill (futures-like
  excess return). JP: MoF par 10Y, same formula, y_cash = 0. DE: Svensson zero 10Y, D_mod = 10 / (1 + y), y_cash = 0.
  A market day without a yield print (bond holiday) has R_b = 0 and the next print carries the change.
- Equity returns for the signal: IC mid at the signal clock of each trading day (close-to-close of that clock).
- **Two signal timings** (no assumption about intraday bond prices):
  - "full": bonds through day t (Treasury par curve is based on ~15:30 ET quotes and is published in the evening of
    day t; assumed available by 18:00 ET, not verified intraday). Equity at the 16:00 NY close. **Entry 20:00 NY of
    day t, exit 16:00 NY of t+1** (no 17:00 rollover crossed). US only.
  - "lag": bonds through day t-1 (day t's bond return set to 0 in that day's update and restored the next day),
    equity through the signal clock of day t. Entry at the signal clock + 1 min of day t, exit at the close clock of
    t+1. US: signal 15:55 NY, entry bar 15:56, exit bar 16:00 of t+1 (early-close days 12:55 / 12:56 / 13:00).
    JP: TSE 15:00 Tokyo close (15:30 from 2024-11-05): signal bar close - 5 min, entry close bar, exit close bar
    t+1. DE: Xetra 17:30 Frankfurt, same pattern. The MoF and Bundesbank publication times are not verified, so
    JP / DE use "lag" only.
- Trading days: NYSE calendar (holidays.NYSE + the round 23 early-close list), TSE (holidays.Japan + Dec 31 - Jan 3),
  Xetra (Jan 1, Good Friday, Easter Monday, May 1, Dec 24, 25, 26, 31). A day also needs IC bars within 10 min of
  each clock used.
- Signal start 2016-01-04 with w = 60 % for every delta; trades from 2016-04-01 (burn-in, as round 23 P2);
  momentum cell from 2017-01-03 (252-day lookback).
- Costs (round 37-45 convention, `lib.trades_vec` of round 41): half spread at entry bar + half at exit bar (actual
  IC spreads), 0.6 bp commission for FX, 0 for indices, swap per 17:00 NY rollover crossed from
  `research/swing/rates.py swap_frac_at`, Friday x3 for indices, Wednesday x3 for FX.

## Families, cells, sides (fixed now)
Side convention: "short equity when the simulated fund is overweight equities". Every cell holds 1 trading day unless
stated. Hold limit 5 days and 3 concurrent positions respected.

F1, US threshold / calendar rebalancing with the bond leg (signal from US500 and the 10y Treasury)
1. **F1-thr-all-full (PRIMARY)**: every day, side = -sign(Threshold_t), US500, 20:00 t -> 16:00 t+1.
2. F1-thr-all-lag: every day, side = -sign(Threshold^lag_t), US500, 15:56 t -> 16:00 t+1 (paper's close-to-close).
3. F1-thr-top-full: days with |Threshold_t| >= 67th percentile of |Threshold| over all prior days (min 60), side as 1.
4. F1-cal-wk4-full: day t in the last 5 NYSE business days of its month, side = -sign(Calendar_t), as 1.
5. F1-combo-full: the paper's Table 6 position x = mean(-Threshold_t / 1.5 %, CalMod_t); side = sign(x) every day
   (x = 0 never happens in practice; if it does, no trade).
6. F1-paperreg-full: side = sign(f_t), f_t = -0.4144 Thr_t + 0.0553 Cal_t - 0.3029 Cal_t wk4_t + 0.0023 Mom_t
   - 0.0203 XA_t (paper Table 1 col 1 coefficients, no constant; Mom = mean(mean_{h=11..20} sign(XA_h),
   mean_{h in 21,42,63,126,252} sign(XA_h)) with XA_h the trailing h-day stock-minus-bond return), from 2017-01-03.
7. F1-thr-pool3-full: cell 1 pooled over US500 + USTEC + US30 (same US500/UST signal), replication.

F2, risk-parity / vol-target de-leveraging (2-asset book: US500 and the 10y Treasury)
- Book: inverse-vol weights w_e = (1/s_e) / (1/s_e + 1/s_b), w_b = 1 - w_e; leverage L = 10 % / sigma_book with
  sigma_book from the trailing N-day sample covariance (stock-bond correlation included), annualised x sqrt(252),
  capped at 4. Equity exposure E_t = L_t w_e,t. Signal day: dlog E_t in the bottom decile of all prior days' dlog E
  (expanding, min 120 days). Side: short US500. Windows N = 20 and 60 declared; holds 1 and 3 days.
8. F2-rp20-1d, 9. F2-rp60-1d (20:00 t -> 16:00 t+1), 10. F2-rp20-3d, 11. F2-rp60-3d (20:00 t -> 16:00 t+3).
- Overlap check (information): share of F2 signal days that are also bottom-decile days of dlog(1/s_e) alone
  (an equity-only vol-control trigger, round 23 P1's family).

F3, Japan and Germany (own bond leg), lagged-bond timing
12. F3-JP-thr-all-lag: JP225 with JP225 + JGB 10Y signal, TSE close t -> close t+1, side -sign(Thr).
13. F3-DE-thr-all-lag: DE40 with DE40 + Bund 10Y, Xetra close t -> close t+1.
14. F3-US2intl: paper section 3.5: US "full" signal of NY day t, traded on the next local session open -> close
    (JP225 09:00 -> 15:00/15:30 Tokyo; DE40 09:00 -> 17:30 Frankfurt) of the first local trading day after the NY
    day t, pooled.
15. F3-rp60-1d-JPDE: F2 rule with N = 60 on each country's own book, short JP225 / DE40 on their close t -> close t+1
    with lagged bonds, pooled.

Controls (placebos: no domestic rebalancing flow should move these pairs at a fixed side; counted in K)
16. C-USDJPY: USDJPY with side -sign(JP Thr^lag), TSE close t -> close t+1.
17. C-EURUSD: EURUSD with side -sign(DE Thr^lag), Xetra close t -> close t+1.

K = 17 cells for the chance benchmark (max |t| of 17 normals: median ~2.05, 95th ~2.95), plus a sign-flip permutation
per family on IS mid t (500 draws, flips per entry date, shared across the family's cells).

Information rows (not cells): the paper's regression replicated in our data (US500 next-day return and XA
= US500 minus 10y bond next-day return on standardised Threshold, univariate and with Mom), IS and VAL, in bp per
sd, against the paper's -15.9 / -20; equity-leg share = equity slope / XA slope; the round 23 equity-only signal's
correlation with the new signal; correlation of daily P&L with C3.

## Statistics and checks (round 13 / 37 conventions)
- Net and mid bp per trade, t clustered by entry date (pooled cells: same-date trades summed); IS 2016-04..2021,
  VAL 2022-24; by year; spread x1.5 on both legs; entry and exit +1 minute; ex-2020-03/04 row.
- Random-entry control, 200 seeds: every-day cells (1, 2, 5, 6, 7, 12, 13, 14, 16, 17): random sides on the same days
  with the cell's long share (the rule trades every day, so only the side can be randomised); event cells (3, 4,
  8-11, 15): same count of random non-event eligible days in the same era, side recomputed by the cell's rule at the
  random day (F2: always short; 3 / 4: the rule's side at that day). Report the percentile of the net mean.
- Per-trade net Sharpe and power = Sharpe x sqrt(HOLD trades), HOLD trades = trades/yr x 1.73.

## Power arithmetic (before any number)
- Every-day cells: ~250 trades/yr, HOLD ~435. LIVE needs per-trade net Sharpe >= 3 / sqrt(435) = **0.144**. US500
  daily sd ~110-120 bp -> **~16-17 bp net per day**. At the paper's size (-15.9 bp per sd, sign rule mid ~ 15.9 x
  E|z| ~ 13 bp) Sharpe ~0.11 -> HOLD power ~2.3 before cost, IS t ~4 if it held. So an every-day cell cannot reach
  LIVE even at the paper's full size (and the paper's coefficient is conditional on momentum, which predicts the
  other way); DEMO (IS t >= 2) needs ~60 % of the paper's size net of ~1-3 bp cost.
- F1-thr-top (~83/yr, HOLD ~145): LIVE needs Sharpe 0.25 (~35 bp net at the higher sd of big-signal days).
- F1-cal-wk4 (~60/yr, HOLD ~104): LIVE needs Sharpe 0.29. DEMO at most.
- F2 (~25 signal days/yr, HOLD ~43): LIVE needs Sharpe 0.46: impossible; DEMO only (IS t >= 2 needs Sharpe ~0.16 per
  trade over ~150 IS trades, i.e. ~20-30 bp on high-vol days).
- F3 every-day cells: as F1-all; JP225 / DE40 sd ~120-130 bp.
- Pooling the three US indices adds almost nothing (daily correlation ~0.9).
Expected: LIVE is out of reach a priori for every cell; the realistic best outcome is a DEMO-numbers cell.

## Verdict bars
LIVE / DEMO bars of research/PROMPT.md unchanged (no RELAXED). A cell meeting DEMO or LIVE numbers gets a
PREREG_DRAFT_P_*.md; HOLD is not opened.

## Addendum 2026-10-30 07:59 UTC (after the numbers; no cell, side or parameter changed)
- Timestamp: the header's "08:05" end time was an estimate. The file was complete at 07:54:22 UTC (file mtime),
  before the signals were built (07:56 UTC) and before the first grading run (07:57:41 UTC).
- Not foreseen: IC is closed at 20:00 NY on Fridays, so the "full" cells lose Friday signals (423 days). Left as
  declared; reported in STREAM_P.md. The size-weighted threshold position in STREAM_P.md is post-hoc information,
  not a cell.
