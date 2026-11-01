# Round 47 stream B hypotheses: open-window buyback capacity from filed repurchases and true earnings dates

Declared 2026-10-30 08:07:49 UTC (`date -u`), during the SEC pull and **before any return was computed or any price file
was opened**. Bars: LIVE / DEMO of research/PROMPT.md (no RELAXED tier). HOLD 2025-01-01..2026-09-24 stays closed: IC
ts < 1735689600000 and US2000 files < 20250101 at load; XBRL facts with `filed` > 2024-12-31 and EDGAR filings dated
after 2024-12-31 are dropped at parse (python -I), before anything is printed. No change to this file after numbers,
except dated addenda declared before their own numbers.

## Mechanism and prior evidence
US firms repurchase ~$0.8-1 tn a year, concentrated in the largest index weights. Most corporate insider-trading
policies and the sell-side buyback desks (Goldman Sachs corporate desk commentary; e.g. "the blackout window" notes)
put open-market repurchases on hold from a few weeks before quarter end until ~2 business days after the earnings
release (10b5-1 plans continue, so the blackout is partial). The flow is price-insensitive in the short run and its
timing is set by each firm's own calendar. Order-of-size: open-window execution of ~$4-5 bn / day against ~$2 bn in
blackout is ~0.5 % of US cash volume; with an inelastic-market multiplier ~5 (Gabaix-Koijen 2021) a $2-3 bn / day
difference moves a ~$45 tn market by ~2-3 bp / day. So the expected high-minus-low capacity effect is **~1-3 bp a day**.
Round 23 P4 used a calendar proxy and found blackout days as strong as open days (the earnings-season drift dominates).
This round measures each firm's own window and dollar run-rate.

## Universe (fixed now)
- Membership by year Y (2016..2024): the top 200 issuers by Vanguard Group 13F-HR value at year-end Y-1 (round 44 I
  `vg_ranks.csv`, already on disk), funds / ETFs dropped, names mapped to CIKs through the EDGAR master index 10-Q /
  10-K filer names (round 41 B downloads) plus round 42 E's hand CIKs and 11 hand CIKs (out/universe.csv). Foreign
  40-F / 20-F filers (TD, RBC, Alibaba, Shopify, ...) have no US XBRL cash-flow facts and drop out (RR = 0). 1,756 of
  1,800 firm-years mapped, 333 CIKs.
- Weight of firm i on day t: its quarterly repurchase run-rate RR_i(t) (below). Firm i is in U(t) iff in the top 200
  of year(t).

## Repurchase run-rate (no look-ahead)
- XBRL company concept `us-gaap:PaymentsForRepurchaseOfCommonStock` (10-Q / 10-K / amendments), falling back to
  `PaymentsForRepurchaseOfEquity` when the first has no fact for the firm's latest filed period. A fact is usable on
  day t only if its `filed` date < t (strictly before the trading day).
- TTM at the latest filed period end E: a ~12-month fact ending at E if present; else YTD(E) + FY(prior) - YTD(E - 1y)
  from facts already filed; else YTD(E) x 12 / months. RR = TTM / 4 (>= 0). If the latest period end is more than 200
  days before t, RR = 0.

## Window convention (declared before returns; two conventions, primary W14)
- Releases: 8-K item 2.02 acceptance times (submissions JSON). Release session s = the acceptance day if accepted
  before 09:30 ET on a trading day, else the next trading day. Fallback when no 8-K 2.02 falls in (E, E + 70 days]: the
  first 10-Q / 10-K filing date for period E.
- Each release is assigned the latest fiscal period end E < release date (period ends from the firm's XBRL facts).
- **W14 (primary; insider-policy convention):** the window is open from trading day s + 2 (two full trading days after
  the release session) until the day before E + 3 months - 14 calendar days (two weeks before the next projected
  fiscal quarter end); closed otherwise (also closed before a firm's first observed release).
- **W0 (alternative):** as W14 but the window closes at the projected quarter end E + 3 months (Goldman desk
  convention "from quarter end to ~48 h after earnings" without the pre-quarter-end weeks).
- If the next release has not happened by E + 3 months + 75 days, the firm is treated as closed (missing data).

## Signals (known before the open of day t)
- OPEN(t) = sum over U(t) of RR_i(t) x open_i(t) / sum over U(t) of RR_i(t) (dollar share of the universe's buyback
  run-rate whose window is open). Window states for day t depend only on releases on or before t - 2 and on dates.
- CAP(t) = sum of open RR_i(t) / sum of Vanguard values of U(t): reported, not separately graded (same daily shape).
- dOPEN3(t) = OPEN(t) - OPEN(t - 3 trading days).
- Thresholds are quantiles of the **IS (2016-21) distribution of the signal itself** (no returns used); their values
  are written in an addendum before returns: HIGH = OPEN >= IS 2/3 quantile; LOW = OPEN <= IS 1/3 quantile;
  SURGE = dOPEN3 >= IS 0.90 quantile.
- Earnings season (F3) = calendar weeks 2-7 of each calendar quarter (trading days from the 8th of Jan / Apr / Jul /
  Oct to day 49 of the quarter). Week-of-quarter = (calendar days since quarter start) // 7, 0..13.

## Families (sides fixed now: always LONG; one trade per symbol-day; trades counted on IS and VAL)
Horizons: ID = 10:00 -> 15:30 ET mid (same day t); CC1 = 15:58 ET of t-1 -> 15:58 ET of t; CC3 = 15:58 t-1 -> 15:58 t+2
(non-overlapping: a trigger inside a running hold is skipped); CC5 = 15:58 t-1 -> 15:58 t+4 (non-overlapping).
Counted symbols: US500, USTEC, US30. US2000 is the low-buyback control (graded, not counted; the mechanism predicts a
weaker effect there).
- **F1 high open capacity -> long.** Days with OPEN(t) >= HIGH. Conventions {W14, W0} x horizons {ID, CC1, CC5} x 3
  symbols = **18 cells**. Mechanism contrast (information, not a trade): mean of HIGH days minus LOW days, and OLS slope
  of the daily return on OPEN.
- **F2 reopening surges -> long.** Days with dOPEN3(t) >= SURGE. {W14, W0} x {ID, CC1, CC3} x 3 = **18 cells**.
- **F3 within the earnings season.** Season days only; a day is "high" when OPEN(t) is above the IS median OPEN of
  its week-of-quarter (median from the signal only). Tradable cell: long high season days. {W14, W0} x {ID, CC1} x 3 =
  **12 cells**. Declared comparison (the separation test): high-minus-low season days, and the OLS slope of daily
  return on OPEN with week-of-quarter fixed effects (14 dummies) over all days. This says how much of any F1 effect is
  left once the calendar is held fixed.
- Total counted: **48 cells**. Primary cell: F1 W14 ID US500.

## Grading (round 37-46 conventions)
- Costs: IC bid / ask at the actual bars (half spread at entry and exit), spread x1.5, +1 minute (both legs), long
  swap -2 bp per calendar night (as rounds 42 / 44). US2000 fixed spread 0.34 points (round 44).
- Net IS (2016-21) / VAL (2022-24), t plain (one trade per day) and Newey-West for overlapping regressions, ex
  2020-03/04, by year.
- Random-entry control: >= 200 draws of the same number of IS (and VAL) days with the same **week-of-quarter and
  weekday** mix (calendar-matched, since the signal follows the earnings calendar); share of draws beaten.
- Chance benchmark: per-day sign flip shared by all 48 cells, 1,000 draws, 95 % quantile of the max IS net t.
- Power at HOLD size: per-trade net Sharpe x sqrt(HOLD n), HOLD n = VAL n / 3 x 1.73.
- Correlation with C3 daily P&L only if a cell survives.

## Power arithmetic (before returns)
Trading days: IS ~1,511, VAL ~753, HOLD ~435. Trade sds (rounds 23 / 42): ID ~75-85 bp, CC1 ~100-110 bp, CC5 ~230 bp.
| cell | days / yr | HOLD n | LIVE Sharpe | LIVE net needed | IS n | DEMO (IS t 2) Sharpe | DEMO net needed |
|---|---|---|---|---|---|---|---|
| F1 HIGH, ID | ~84 | ~145 | 0.25 | ~20 bp | ~500 | 0.089 | ~7 bp (cost ~1.5-2) |
| F1 HIGH, CC1 | ~84 | ~145 | 0.25 | ~27 bp | ~500 | 0.089 | ~10 bp (cost ~4) |
| F1 HIGH, CC5 | ~17 | ~29 | 0.56 | ~130 bp | ~100 | 0.20 | ~46 bp |
| F2 SURGE, ID / CC1 | ~25 | ~43 | 0.46 | ~37-50 bp | ~150 | 0.16 | ~13-18 bp |
| F2 SURGE, CC3 | ~12 | ~21 | 0.65 | ~110 bp | ~75 | 0.23 | ~40 bp |
| F3 high season, ID / CC1 | ~25 | ~45 | 0.45 | ~36-50 bp | ~150 | 0.16 | ~13-18 bp |
Against the expected ~1-3 bp / day, **LIVE is out of reach in every cell before any return**; DEMO needs 3-10x the
expected size. A pass would be a surprise and is checked against the calendar-matched control first.

## If the first construction fails
Declared by-products, from the same downloads only (each declared in a dated addendum before its numbers):
B1 dollar-weighted capacity CAP (not share) level vs its trailing-year median; B2 the 8-K item 8.01 / press-release
buyback authorisations are out of scope (need per-filing documents).

## Addendum A1, 2026-10-30 08:16:38 UTC (before any return; only the signal had been built)
- Construction fix: a spot check of the window spans showed Apple's 2019-01-02 revenue warning (an 8-K item 2.02) opening
  its window 4 weeks before the real release. The release that reopens a window must now be the first 8-K 2.02 accepted
  **at least 10 calendar days after** the period end E (and <= E + 70 days); earlier 8-K 2.02s (pre-announcements) are
  ignored. Nothing else changes.
- Signal-only facts seen before returns (from the first build): 307 firms report `PaymentsForRepurchaseOfCommonStock`, 21
  `...OfEquity`; 142-156 of the 200 entities a year have RR > 0; the universe run-rate is ~$92-168 bn a quarter. Coverage
  gap: some firms used other tags in some years (e.g. JPM 2011-17), so their RR is 0 there; accepted, not patched.
- **The dollar-weighted OPEN share is 94 % explained by week-of-quarter means (IS R2 0.943 W14, 0.940 W0).** The true
  firm windows differ from the calendar proxy far less than the brief assumed, so F3 (within week-of-quarter variation)
  has little signal variance to work with; expected to have low power.
- Threshold values (IS quantiles of the signal, rule as declared) are printed by capsignal.py and recorded in
  STREAM_B.md after the rebuild.

## Addendum A2, 2026-10-30 08:17:37 UTC (main grid graded: no cell reaches IS net t 2; by-products declared before their numbers)
Same horizons (ID, CC1), symbols (US500, USTEC, US30 counted; US2000 control), costs, controls and side (long) as the
main grid. 12 counted cells; own chance benchmark (sign flip, 1,000 draws) and the pooled 60-cell one reported.
- **B1 dollar capacity vs its own trailing year.** CAP_W14(t) (open run-rate / universe 13F value) >= the 2/3 quantile
  of CAP_W14 over the previous 252 trading days (needs >= 200 finite) -> long. Removes the year-level buyback intensity
  drift. 2 horizons x 3 = 6 cells.
- **B2 mega-buyer windows.** OPEN_TOP10(t) = RR-weighted open share (W14) of the 10 entities with the largest RR(t) in
  U(t) (Apple, Alphabet, Microsoft, Meta, the big banks... chosen by RR known at t). Fewer firms and off-cycle fiscal
  calendars (AAPL, MSFT, ORCL, CSCO) give it more non-calendar variation. Season days (as F3) with OPEN_TOP10 above its
  IS week-of-quarter median -> long. 2 x 3 = 6 cells. Its IS R2 on week-of-quarter means is printed before grading.
