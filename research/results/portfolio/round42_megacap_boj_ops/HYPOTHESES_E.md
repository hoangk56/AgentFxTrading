# Round 42 stream E hypotheses: index heavyweight earnings -> USTEC, US500, US30 (DE40 / JP225 controls)

Written 2026-10-30 05:04 UTC (`date -u`), before any return was computed. At this point the EDGAR and 13F data are
loaded and parsed, and IC M1 bars were opened only to read session gaps and median spreads by ET hour (2019). No
price change was computed. Same LIVE / DEMO bars as research/PROMPT.md. HOLD 2025-01-01..2026-09-24 stays closed:
IC ts < 1735689600000 at load, and EDGAR filings dated after 2024-12-31 were dropped at parse (python -I).

## Data (loaded, not yet joined to returns)
- **Company list per year (fixed now).** Vanguard Group 13F-HR info table at the prior year-end (CIK 102909; filed
  each February 2016-2024, 9 files from www.sec.gov/Archives). I summed value by issuer across share classes (e.g.
  GOOGL + GOOG), dropped options and debt lines, and ranked. Then I dropped funds (VANGUARD INDEX FDS) and foreign
  private issuers that file 6-K, not 8-K (ALIBABA), and took the **top 40**. Vanguard's holdings track total US
  market cap, so the rank is a public proxy for index weight. FB and META are the same CIK (1326801). Disney changed
  CIK in 2019-03 (1001039 -> 1744489), and Broadcom Ltd 1649338 became Broadcom Inc 1730168; both CIKs are kept.
  List year Y = holdings at Y-1-12-31.
  - 2016: AAPL MSFT GOOGL XOM JNJ GE WFC AMZN JPM BRK-B PG FB T PFE KO VZ CVX BAC INTC HD PEP DIS V MRK GILD C PM CSCO IBM SPG CMCSA AMGN AGN BMY ORCL MDT MO CVS MCD UNH
  - 2017: AAPL MSFT GOOGL XOM JNJ JPM BRK-B AMZN GE FB T WFC CVX PG VZ BAC PFE KO INTC PEP MRK C CMCSA HD CSCO UNH IBM PM DIS V MO SPG MMM SLB ORCL MCD WMT AMGN MDT ABBV
  - 2018: AAPL MSFT GOOGL AMZN FB JNJ JPM XOM BRK-B BAC WFC CVX T PG INTC PFE VZ HD V UNH CSCO PEP C KO CMCSA DD BA PM ABBV MMM MRK DIS GE WMT MA ORCL MCD MO IBM AMGN
  - 2019: MSFT AAPL GOOGL AMZN BRK-B JNJ JPM XOM FB PFE PG UNH VZ V INTC CVX BAC MRK T CSCO WFC HD KO PEP BA MA WMT CMCSA MCD DIS ABBV ABT MDT DD AMGN MMM C ORCL AMT LLY
  - 2020: MSFT AAPL GOOGL AMZN FB JPM JNJ BRK-B PG V XOM T BAC INTC UNH MA VZ DIS CVX MRK HD CMCSA PFE KO CSCO WFC WMT PEP C AMT MCD BA ABT MDT ADBE BMY ACN AMGN TXN COST
  - 2021: AAPL MSFT AMZN GOOGL FB TSLA JNJ BRK-B V JPM PG UNH DIS MA NVDA HD PYPL CMCSA VZ ADBE WMT BAC PEP NFLX KO MRK INTC PFE ABT T QCOM CRM ABBV CSCO AVGO NKE TMO ACN XOM MCD
  - 2022: AAPL MSFT GOOGL AMZN TSLA META NVDA JPM BRK-B JNJ UNH HD PG V PFE BAC MA AVGO ACN ADBE XOM CSCO DIS COST PEP ABT TMO KO NFLX CMCSA ABBV CRM CVX LLY QCOM WMT INTC PYPL NKE MCD
  - 2023: AAPL MSFT GOOGL AMZN UNH JNJ BRK-B XOM JPM PG V HD NVDA CVX MA LLY TSLA PFE ABBV MRK PEP KO AVGO META BAC WMT CSCO COST MCD TMO ABT NEE ACN LIN BMY TXN DHR CMCSA VZ PLD
  - 2024: AAPL MSFT GOOGL AMZN NVDA META TSLA BRK-B AVGO JPM UNH LLY XOM V JNJ PG HD MA MRK COST ABBV CVX ADBE PEP CRM KO WMT AMD ACN BAC MCD CSCO INTC LIN NFLX TMO ABT CMCSA INTU QCOM
  - "top10" = the first 10 names of each year's list.
- **Release times.** data.sec.gov/submissions JSON for 71 CIKs, plus 159 older pages (230 requests, all HTTP 200).
  I kept form 8-K (no amendments) with item 2.02, filed 2015-10-01..2024-12-31: 2,692 filings. For the list companies
  of each year that leaves 1,510 releases (top40) and 376 (top10). `acceptanceDateTime` is UTC: the hour histogram
  peaks at 10-12 UTC (06-08 ET pre-market) and 20-21 UTC (16-17 ET after the close). Times are converted to ET.
  - Classes by ET acceptance time A: PRE = 04:00-09:29 on a trading day (also weekend / holiday releases, which go
    to the next session); INTRA = 09:30-15:59; POST = 16:00-23:59, or 00:00-03:59 the next day.
  - The news session of a release: PRE / INTRA -> the same session; POST -> the next NYSE session.
- **Session clock (IC M1, read from bar presence in 2019).** US500, USTEC, US30, DE40 and JP225 have no bars at
  16:15-16:29 ET or 16:59-17:59 ET. Median spreads in points at 16:00-20:00 ET: US500 0.6, USTEC 2.0, US30 3.0
  (about 1-2.5 bp); DE40 6-8 and JP225 6-12, both wide out of their home hours.
- POST acceptances by ET time: 16:00-16:14 = 447, 16:15-16:29 = 100, 16:30-16:44 = 67, later = 86 (top40, 2016-24).

## Counts per year (top40 / top10, 2016-24) and power arithmetic (before returns)
- Top40: 150-170 releases a year. That gives 76-98 news sessions a year, 37-59 POST evenings, 52-68 PRE days, and
  16-26 sessions with >= 3 releases.
- Top10: 37-44 releases a year, 27-38 news sessions, 12-26 POST evenings, 1-4 sessions with >= 3 releases.
- HOLD = 1.73 years. Trades per symbol in HOLD at the 2022-24 rate, and the per-trade net Sharpe each count needs:

| cell type | trades/yr | HOLD trades | Sharpe for LIVE (3/sqrt n) | IS trades (6 y) | Sharpe for IS t 2 (DEMO) |
|---|---|---|---|---|---|
| news sessions k >= 1 (top40) | ~88 | ~150 | 0.24 | ~500 | 0.09 |
| POST evenings k=0 (top40) | ~50 | ~85 | 0.33 | ~270 | 0.12 |
| POST evenings with z >= 1 | ~20 | ~35 | 0.51 | ~110 | 0.19 |
| sessions with >= 3 (top40) | ~20 | ~35 | 0.51 | ~130 | 0.18 |
| top10 news sessions | ~32 | ~55 | 0.40 | ~180 | 0.15 |

- The sd of an index CFD trade is ~55 bp from 16:00 to 09:30, ~90 bp from 09:30 to 16:00 and ~110 bp close to close
  (US500; USTEC is ~1.3x). LIVE therefore needs a net **20-35 bp per trade on US500**. That is several times any
  index-level number in the literature (the announcement premium is a few bp a day at the market level and has
  shrunk since 2004, round 25 A). **LIVE is out of reach by count for every cell** unless the effect is
  ~0.25-0.5 sd per event. DEMO needs ~9-19 bp a trade at mid in IS, which is reachable only if the effect is large.
- The three US indexes are ~0.9 correlated on these clocks, so pooling them adds no independent power. Each cell is
  graded per symbol; a three-index basket is reported but not counted.

## Families, sides and parameters (declared now; sides never changed after seeing numbers)
Price at clock T = the close of the M1 bar that starts at T-1 (last quote before T); mid = (bid + ask) / 2. A signal
at T fills at the close of the bar that starts at T (one minute later): buy at the ask, sell at the bid. Latency
variant: both legs one more minute late. Spread x1.5 variant. Swap: long -2 bp per rollover (17:00 ET), short
-0.5 bp, Friday x3; no commission on indices. One trade per symbol per day. Missing quote within 5 min: no trade.

**F1a. After-hours reaction continuation (POST evenings).** Mechanism: price discovery after hours is slower and
noisier than in the regular session (Barclay & Hendershott 2003, RFS 16). Patton & Verardo 2012 (RFS 25) show that
investors learn about other firms from a heavyweight's news ("learning spillovers"), with market betas higher on
announcement days and on the day after. A heavyweight's after-hours news therefore reaches the rest of the index only
when the other stocks trade, so the index reaction continues. **Side = sign of the reaction (continuation).**
- Event: an evening D with >= 1 listed POST release (set top40 or top10).
- P0 = mid at 16:00 ET on D. The reaction R = mid at the entry signal clock minus P0, in bp.
- z = R / sd(R over the prior 250 NYSE days, all days, same clocks; at least 150 days).
- Trade if |z| >= k, with k in {0, 1}.
- Entry E_a = signal 16:45 ET. This needs the evening's last listed acceptance <= 16:43; it crosses the 17:00
  rollover and pays one night of swap.
- Entry E_b = signal 19:00 ET (after the rollover hour, no swap). This needs the last acceptance <= 18:58.
- Exit X1 = 09:30 ET on the next session (fill = close of the 09:29 bar); X2 = 16:00 ET on the next session (fill =
  close of the 15:58 bar).
- Cells: 2 entries x 2 exits x 2 k x 2 sets x 3 symbols = **48**.

**F1b. Open-to-close reversal on news sessions (attention).** Mechanism: on high-attention days retail investors buy
at the open, so the overnight return reverses during the day (Berkman, Koch, Tuttle & Zhang 2012, JFQA 47; also
Lou, Polk & Skouras 2019, JFE 134). A heavyweight's earnings is a high-attention event for the index.
**Side = minus the sign of the overnight gap (reversal).**
- Event: a news session S with >= 1 listed PRE or POST release (set top40 or top10).
- G = mid at 09:30 on S minus mid at 16:00 on the previous session. z is computed against a trailing 250-day sd.
- Trade if |z| >= k, with k in {0, 1}. Entry signal at 09:30 (fill at the close of the 09:30 bar); exit at the
  close of the 15:58 bar. No swap.
- Cells: 2 k x 2 sets x 3 symbols = **12**.

**F2. Index premium on heavyweight announcement days (long).** Mechanism: announcement days carry systematic
risk, so the market risk premium is earned there (Savor & Wilson 2016, JF 71). Chan & Marsh 2021 ("Asset pricing on
earnings announcement days", JFE) find the beta-return slope is positive only on "LEAD" days, when influential large
S&P 500 firms report early in the season. Both imply the index earns a premium on those days. **Side = long.**
- Event: a session S with n_S >= k listed releases, where n_S counts PRE and INTRA releases on S plus POST releases
  on the previous evening.
- Sets: top40 with k in {1, 3}; top10 with k in {1, 2}; and LEAD = top40 with k >= 1, restricted to S within the
  first 10 NYSE sessions of a season. A season starts at the first top40 news session after a gap of >= 20 sessions
  without one.
- Windows: W1 = 16:00 on the previous session -> 16:00 on S (fills at the 15:58 bars), which holds through the
  previous evening's releases and pays one long swap night (x3 over a weekend); W2 = 09:30 -> 16:00 on S, intraday.
- Cells: 5 sets x 2 windows x 3 symbols = **30**.
- **Contamination note:** round 23 P saw (post hoc) the earnings-season half-month as the strongest 10:00-15:30
  window in IS (+6-9 bp a day, t 1.8-2.4) and VAL +0.4. F2's IS is therefore not clean; VAL is the clean test of F2.

**F3. Pre-release drift (positioning / hedging into a heavyweight release, long).** Mechanism: the announcement
premium starts before the release, as attention and hedging demand rise (Barber, De George, Lehavy & Trueman 2013,
JFE 108; Frazzini & Lamont 2007). **Side = long.**
- Event: a day D with >= k listed POST releases that evening. Sets: top40 with k in {1, 2}; top10 with k = 1.
- Windows: W2 = 09:30 -> 16:00 on D (intraday, before the release); W3 = 16:00 on D-1 -> 16:00 on D (one long swap
  night).
- Cells: 3 x 2 x 3 = **18**.

Counted cells: **108** on US500, USTEC and US30. Controls, not counted and never used to select: F1a with E_b, X1,
top40, k in {0, 1} on DE40 and JP225; and the F2 top40 k >= 1 cells with the same clocks on non-news sessions.

## Grading (declared now)
- IS 2016-2021 (parameters), VAL 2022-2024 (check). No PRE era: there is no US index series before 2016 in
  research/data.
- Report mid and net mean in bp and t. There is one trade per day per symbol, so the plain t is the day-clustered t.
- Report per-trade Sharpe, power at the IS and at the VAL size on 1.73 years, years positive, the spread x1.5 and +1
  minute variants, and results with and without 2020-03/04.
- Random-entry control, 200 seeds per graded cell: the same number of trades on random NYSE days of the same era
  with the same weekday mix and the same clocks. Sides are recomputed at the random day (F1a, F1b) or long (F2, F3).
  The control reports the cell's percentile.
- Chance benchmark: the 95 % quantile of the max |IS net t| over the 108 cells under a per-day sign flip shared
  by all symbols and cells (1,000 draws); also the max of 108 normals (~3.0).
- Bars as in research/PROMPT.md: LIVE needs IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, >= 95 % random
  and power >= 3. DEMO needs IS t >= 2.0, VAL net > 0 and >= 90 % random. A cell that meets either bar on IS and VAL
  gets a PREREG_DRAFT_E_*.md; HOLD is not opened. The daily correlation with C3 is reported for any survivor.

## Amendment 2026-10-30 05:06 UTC (before any return)
The declared LEAD season rule ("first news session after a gap of >= 20 sessions") is degenerate. Off-cycle
reporters (ORCL, NKE, CSCO, HD, WMT, COST, ADBE, MDT, ACN) fill the gaps, so only 4 of 36 seasons qualify. It is
replaced, still before returns, by this rule: a season starts at the first top40 news session on or after the 8th of
January, April, July or October. The bank kick-off is around the 12th-15th, and off-cycle reporters sit in the last
month of a quarter. LEAD = top40 news sessions among the first 10 NYSE sessions from that start. Nothing else
changes.

## By-product B1, declared 2026-10-30 05:09 UTC (after the main grid failed; before any B1 return)
The main grid has no cell with IS net t >= 2 on the declared side; the results are in STREAM_E.md. Following the
round 37-41 practice, the stream moves to a related by-product of the same data: the **immediate after-hours
window** around the release minute, which the main grid skipped (its entries started at 16:45 or 19:00).
- Mechanism and side as F1a: continuation. Slow after-hours price discovery (Barclay & Hendershott 2003) and
  learning spillovers (Patton & Verardo 2012) predict that the index keeps moving with the first reaction while the
  other stocks and the futures catch up. The window is minutes, not a day.
- Event: a POST evening D (set top40 or top10), with the evening's last listed acceptance A_last <= 16:40 ET.
- R = mid at signal time T = A_last + 2 min (close of the bar that starts at T-1) minus mid at 16:00 (close of
  15:59). z = R / sd, where sd is F1a E_a's trailing 250-day sd of the 15:59 -> 16:44 window (a common scale).
  Trade if |z| >= k, with k in {0, 1}; side = sign(R).
- Fill at the close of the bar that starts at T. Exit H1 = the close of the bar 10 minutes after the entry bar;
  H2 = the close of the 16:58 bar (before the rollover; a position held through the 16:15-16:29 break is still
  held).
- An H1 exit that would fall in 16:15-16:29 moves to the close of the 16:30 bar.
- Latency: both legs +1 min. Costs, x1.5, swap (none: the exit is before 17:00), the random control (the same rule
  on random NYSE evenings with the same weekday mix, using T = the cell's median entry minute) and the grading are
  as in the main grid.
- Cells: 2 sets x 2 k x 2 exits x 3 symbols = **24** (132 counted in total). The chance benchmark is recomputed
  over these 24.
