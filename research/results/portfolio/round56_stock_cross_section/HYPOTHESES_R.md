# Round 56 stream R: hypotheses (written 2026-10-30 12:03 UTC, before any return was computed)

Data: round 54 D's `stocks_daily.npz` (Dukascopy daily bid / ask, split-adjusted via `adj`), stocklib cost model,
round 54 E's `events.csv` (8-K item 2.02 acceptance date / time ET). Every row with date >= 2025-01-01 is dropped at
load (asserted). No download. IS = 2016-21 (in practice from mid-2017: SPY starts 2017-02-16 and the beta needs 60
days), VAL = 2022-24. PRE (2016-17) is not separable: 2017 is reported as a year only.

What has been looked at before writing this file: counts only (events per year and per hour, which D stocks lack
8-K 2.02 events, SIC codes from the submissions JSON on disk). No return, spread distribution by cell, or
signal statistic.

## Universe and filters (declared)
- Stocks of D (`is_etf == 0`) that have at least one 8-K 2.02 event in events.csv (206 names; the 14 without are
  foreign private issuers or non-filers: AAL, ABEV, AEP, AZN, BABA, BBD, BIDU, BP, ITUB, PBR, TSM, USO, VALE, XOM).
  ETFs are hedges / sector benchmarks only.
- Eligible on formation day t: valid close bid / ask on t and on each day of the formation window and the day
  before it; raw mid close >= USD 10 on t (commission <= 4 bp a side); Dukascopy close spread on t <= 50 bp; a beta
  is available. A trade whose hold contains a flagged `jump` (spin-off / bad print) or whose exit quote is missing
  is dropped (both rare; noted as a mild look-ahead).

## Signal
- r(i,d) = mid close-to-close return (split-adjusted).
- beta(i,t) = OLS slope of r(i) on r(SPY) over the 250 trading days ending at t-L (before the formation window),
  at least 60 joint observations.
- Primary residual: e(i,d) = r(i,d) - beta(i,t) r(SPY,d). Signal s(i,t) = sum of e(i,d) over d = t-L+1..t,
  L in {1, 5}. Ranked in the cross-section of eligible names on t.
- Sector variant (reported for the primary and best cells only, not a selection cell): e = r(i) - r(sector ETF),
  sector from the SEC SIC code, rules applied in this order: XLV = 2834-2836, 3826, 3841-3851, 5122, 6324,
  8000-8099, 8731; XLE = 1311, 1381-1389, 2911, 4610-4619, 4922-4924; XLU = 4900-4991; IYR = 6500-6599, 6798;
  XLF = 6000-6499; XLK = 3570-3579, 3600-3629, 3640-3699, 3825, 7370-7379; XLP = 2000-2199, 2670-2679,
  2840-2844, 5140-5149, 5331, 5400-5499; XLY = 1531, 2300-2399, 2510-2599, 3021, 3630-3639, 3711, 3714,
  3940-3949, 4700-4799, 5000-5999, 7000-7099, 7389 (PCLN / EXPE type); XLI = 3400-3569, 3580-3599, 3720-3729,
  3760-3769, 3812, 4000-4599; else SPY. Before an ETF has data (XLE, XLK, XLU, XLV, XLY start 2017-11-15) SPY.
- News day: an 8-K 2.02 accepted before 16:00:00 ET on a trading day belongs to that day; at or after 16:00, or on
  a non-trading day, to the next trading day.

## Families and sides (from the literature, fixed now)
- **F1 no-news reversal (Chan 2003; Da, Liu & Schaumburg 2014; Lehmann 1990).** Eligible names with no news day in
  [t-L-1, t] (formation window plus 2 sessions before it). Long the k lowest s (no-news losers), short the k
  highest s (no-news winners), equal dollar per position (dollar-neutral book, no hedge). Enter at the close of t
  (long at the ask, short at the bid), exit at the close of t+h. Grid L in {1, 5}, h in {1, 3, 5}, k in {3, 6, 9}:
  18 cells. Books are formed on non-overlapping dates (every h-th trading day from the first eligible day), so a
  book holds 2k positions at once: bots = 2k / 3 (k = 3, 6, 9 -> 2, 4, 6 bots).
- **F2 news continuation (alternative family; Chan 2003 drift after news).** Event-based: firm i with a news day e;
  entry at the close of t = e + L - 1 (L = 1: the news day's close; L = 5: the 5th session), signal s(i,t) over
  e..t; follow the move (long s > 0, short s < 0). Two books per (L, h): "sign" = every event firm, side = sign of
  s; "k3" = on days with >= 6 entering events, long the top 3, short the bottom 3 of s. Exit at the close of t+h.
  Grid L in {1, 5}, h in {1, 3, 5}, book in {sign, k3}: 12 cells. Formed every day (events are sparse); bots =
  ceil(p99 concurrent positions / 3), reported. Overlaps round 54 E H2 (PEAD follow): any F2 result is not new.
- **F3 Nagel (2012) conditional reversal (declared variant).** F1 restricted to formation dates when SPY's 20-day
  realized volatility (close-to-close mid, t-19..t) is above the 67th percentile of all its earlier values from
  SPY's start (expanding, at least 120 earlier values): reversal as liquidity provision pays more when volatility is
  high. VIX itself is not on disk; realized SPY vol is the declared proxy. Same 18 (L, h, k) cells.
- Total 48 cells. **Primary cell: F1, L = 5, h = 5, k = 9, SPY-beta residual (Lehmann weekly reversal with the
  no-news filter), 6 bots.**

## Costs (stocklib defaults, IC MT5)
Close fills at the Dukascopy close bid / ask of the traded day, USD 0.02 / share / side on the raw price,
financing per calendar night (long EFFR + 3 %, short 3 % - EFFR, per 360). Every position is a full round trip
(conservative: a name that stays in the next book would really be held on); the share of positions that repeat in
the next book (same name, same side) is reported as turnover. Stress: spread x1.5; +1 day delay (signal at the
close of t, entry at the close of t+1, exit t+1+h). Dividends are not in the data: long losers pay the
ex-date drop, short winners gain it; long and short legs are reported separately and the side bias is flagged.

## Controls and statistics
- Per-position net bp, t clustered by formation (entry) date. IS / VAL, by year, ex-2020-03/04.
- Random control per cell: same formation dates, same number of longs and shorts, names drawn from that date's
  eligible pool (F1 / F3: the no-news pool; F2: all eligible names), 200 draws; share of draws the cell beats.
- Chance benchmark: max IS net t over the 48 cells under a null that permutes s across the eligible names on each
  formation date (news status and eligibility kept), 200 permutations; the cell's IS t is compared with the p95 of
  that max.
- Long leg alone + SPY beta hedge: reported for the primary cell (variant, not a cell).
- Alternative start offsets of the non-overlapping schedule: mean over offsets reported for the primary cell.
- C3 correlation for any survivor (daily P&L by exit date vs C3 daily R from trades_C3_gotobi_jpy_basket.csv).

## Bars (research/PROMPT.md; never lowered)
- LIVE: net IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, beats >= 95 % of random draws, and power =
  net Sharpe per trade x sqrt(HOLD trades) >= 3 using the VAL effect size; a "trade" for power is one book date
  (the clustered unit), N_HOLD = 435 trading days / h.
- DEMO: net IS t >= 2.0, VAL net > 0, beats >= 90 % of random draws.
- Also must stay positive with spread x1.5 and with the +1 day delay. HOLD 2025-01..2026-09 stays closed; at most a
  PREREG_DRAFT.

## Power arithmetic (before any return; assumptions, not data)
Assume a per-position residual sd of ~250 bp a day for extreme-ranked large caps (sqrt-time scaling: 433 bp for 3
days, 560 bp for 5), independent positions (optimistic: same-side extremes co-move). Book-date sd of the
per-position mean = sd_h / sqrt(2k). HOLD book dates N = 435 / h (435, 145, 87). Net per position needed for
power 3: m >= 3 sd_h / sqrt(2k N).

| h | k = 3 | k = 6 | k = 9 |
|---|---|---|---|
| 1 | 14.7 bp | 10.4 | 8.5 |
| 3 | 44 | 31 | 25 |
| 5 | 74 | 52 | 42 |

Costs per position at a close fill: spread ~7 bp + commission ~4-5 bp (median price) + financing ~1 bp / night
on average across sides => ~13 bp for h = 1, ~19 bp for h = 5. So LIVE needs gross ~22 bp per position per day at
h = 1 (k = 9) or ~60 bp per 5-day position at h = 5 (k = 9). Prior: the large-cap short-term reversal has shrunk
since the 2000s (Nagel 2012 shows it concentrated in crises), so LIVE is unlikely; the most plausible outcome is
real gross reversal at h = 1 that is below the ~13 bp round trip. F2 has fewer trades (~5 events per firm-year
=> ~1,000 events a year, ~1,800 in HOLD; as book dates ~250 a year) and round 54 E found +17 bp mid at 3 days
(below cost), so F2 is expected to fail.

Pitfall declared up front: signal and fill on the same Dukascopy close (the brief's rule). A reversal signal is
biased by bid-ask bounce and last-minute noise in that close; the +1 day delay variant and the mid-based signal
with ask / bid fills are the checks. A cell that dies at +1 day is treated as a microstructure artefact.
