# Round 47 stream B: open-window buyback capacity from filed repurchases and true earnings dates -> US500, USTEC, US30 (US2000 control)

Written 2026-10-30 08:19 UTC. Hypotheses were declared before any return, in [HYPOTHESES_B.md](HYPOTHESES_B.md):
- main grid at 08:07:49 UTC;
- addendum A1 at 08:16:38, before returns: a construction fix that ignores pre-announcement 8-K 2.02s;
- addendum A2 at 08:17:37, after the main grid and before its own numbers: by-products B1 and B2.

Same LIVE / DEMO bars as research/PROMPT.md. HOLD stayed closed:
- IC ts < 1735689600000 at load (asserted), and US2000 files < 20250101.
- XBRL facts with `filed` > 2024-12-31 were dropped at parse under python -I: 3,860 dropped; the latest kept is
  2024-12-20.
- 8-K 2.02 filings dated after 2024-12-31 were dropped at parse; the latest kept is 2024-12-19.
- Nothing from 2025-26 was printed.

## Answer
There is no LIVE or DEMO candidate and no PREREG_DRAFT. This is the first round to measure each large firm's own
buyback window, from its 8-K 2.02 release time and fiscal period end, weighted by its filed repurchase dollars.
- **The flow is not in the index returns.**
  - High-capacity days are no better than low-capacity days in IS. US500 10:00-15:30: +0.8 vs +1.7 bp, t -0.19.
  - The best of 48 cells has IS net t 1.47, against a chance benchmark of 2.37.
  - The by-products (12 cells) top out at t 1.66, against 2.03.
- **The premise that true windows differ from the calendar proxy is weak in dollar terms.**
  - Week-of-quarter means explain 94 % of the daily variance of the dollar-weighted open share. Even the top-10 buyers
    alone give 91 %.
  - The weeks where one firm's window differs from the calendar exist, but they carry a small share of the dollars.
  - So this series is mostly round 23 P4's calendar proxy, measured better, and gives the same answer.
- **Earnings-season drift (family 3).** Season days are positive in both eras: US500 10:00-15:30 is +3.2 bp IS and
  +11.3 bp VAL, positive in 8 of 9 years. But within the season, high-capacity days beat low-capacity days by only
  +0.7 to +5.8 bp in IS (t < 0.9). The cells beat only 56-80 % of calendar-matched random entries. The drift is the
  calendar, not the buyback bid.
- LIVE was ruled out by the count before any return was computed: every cell needs 20-130 bp net a trade, against an
  expected 1-3 bp a day.

## Sources (robots and requests)
- **robots.txt, read first (08:04 UTC).**
  - www.sec.gov has only a `User-agent: *` block, with no ClaudeBot / anthropic-ai / Claude-Web entry. /Archives and
    /files are not disallowed.
  - data.sec.gov returns 404 for robots.txt, so it sets no rules.
- **SEC: 1,174 requests, 2026-10-30 08:04:29-08:15:41 UTC, ~121 MB.**
  - User-Agent "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate filing statistics)", with no name or
    e-mail.
  - One sequential process, >= 0.2 s spacing. No 403 / 429 / 503.
  - XBRL company concept, `data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/{PaymentsForRepurchaseOfCommonStock,PaymentsForRepurchaseOfEquity}.json`
    for 333 CIKs: 666 requests. 341 returned 200 and 325 returned 404 (the firm never used that tag).
  - Submissions JSON for the 262 CIKs that round 42 E did not have, plus 244 older `-submissions-NNN.json` pages: all
    200.
  - Log: `web/requests.log`.
- **Reused from disk, with no new requests:**
  - Round 44 I Vanguard 13F ranks (`vg_ranks.csv`, year-ends 2015-23).
  - Round 41 B EDGAR master indexes 2015-24, used for name-to-CIK mapping.
  - Round 42 E submissions for 71 CIKs and its hand CIKs.
- **Universe:** the top 200 issuers by Vanguard 13F value, per year, 2016-24.
  - 1,756 of 1,800 firm-years were mapped, 333 CIKs. 11 hand CIKs were added; foreign 40-F / 20-F filers and funds
    drop out.
  - 142-156 entities a year have a positive run-rate. The universe run-rate is $92-168 bn a quarter, about
    $0.4-0.7 tn a year, which is plausible for the top 200.
  - Releases: 12,298 8-K 2.02 filings; 8,700 assigned as the release that reopens a window, plus 303 10-Q / 10-K
    fallbacks.
- **Unusable or partial:** some firms filed repurchases under other tags in some years (JPM 2011-17, for example), so
  their run-rate is 0 there. This was not patched.
- WebSearch: 0.

## Construction (as declared)
- **Run-rate.** RR_i(t) = TTM repurchases / 4, from facts filed before day t. TTM is FY + YTD - prior YTD.
- **Windows (W14, primary).** Open from 2 trading days after the release session until 14 days before the projected
  next fiscal quarter end, E + 3 months. W0 closes at E + 3 months instead.
- **Signals.** OPEN(t) = RR-weighted open share of U(t). dOPEN3 = its 3-day change.
- **Thresholds**, from IS quantiles of the signal only:

| | HIGH (2/3 q) | LOW (1/3 q) | SURGE (0.9 q of dOPEN3) |
|---|---|---|---|
| W14 | 0.860 | 0.186 | 0.136 |
| W0 | 0.926 | 0.570 | 0.128 |

- **Days a year.** HIGH: 71-95. SURGE: 19-29.
- **Mean OPEN by week-of-quarter (W14, IS):** 0.15 0.15 0.18 0.32 0.62 0.84 0.87 0.89 0.92 0.92 0.80 0.13 0.14 0.15.
  - Spot check, 2019: AAPL open 05-03..06-14, 08-02..09-13, 11-04..12-13. MSFT and GOOGL are similar. JPM opens about
    2 weeks earlier each quarter.
- **Costs.** IC bid / ask at the actual bars and long swap -2 bp a calendar night, as in rounds 42 / 44. US2000 uses a
  fixed 0.34-point spread.
- **Random control.** 200 draws with the same week-of-quarter x weekday mix, in each era.

## Results (net bp per trade, long; t plain, one trade per symbol-day)
These are the best cells per family by IS net t, plus the primary cell. "rnd" is the share of calendar-matched random
draws beaten, IS / VAL. "power" is per-trade net Sharpe x sqrt(HOLD n) at the VAL size.

| hypothesis | sym | mid IS (t) / VAL (t) | cost | net IS (t) / VAL (t) | VAL / IS | x1.5 IS / VAL | +1 min IS / VAL | ex-2020-03/04 IS (t) | years > 0 | Sharpe IS / VAL, power | rnd | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 W14 HIGH, 10:00-15:30 **(primary)** | US500 | +0.8 (0.27) / +1.7 (0.37) | 1.5 | -0.7 (-0.25) / +1.3 (0.28) | - | -1.5 / +1.1 | -1.0 / +1.8 | +0.2 (0.07) | 4/9 | -0.01 / 0.02, 0.21 | 0.07 / 0.96 | none |
| F1 W14 HIGH, close to close 1 d (best F1) | USTEC | +7.7 (1.15) / +13.5 (1.57) | 4.4 | +3.3 (0.49) / +10.1 (1.17) | 3.1 | +2.5 / +9.8 | +3.4 / +9.8 | +4.6 (0.83) | 7/9 | 0.02 / 0.08, 0.89 | 0.70 / 0.95 | none |
| F1 W0 HIGH, 5 d | USTEC | +29.4 (1.07) / +32.5 (0.79) | 16.4 | +13.0 (0.47) / +17.1 (0.41) | 1.3 | +12.2 / +16.7 | +12.5 / +17.6 | +16.5 (0.68) | 6/9 | 0.05 / 0.05, 0.31 | 0.37 / 0.56 | none |
| F2 W0 SURGE, 3 d (best F2) | USTEC | +45.2 (1.51) / -26.9 (-0.43) | 10.5 | +34.8 (1.16) / -36.0 (-0.58) | <0 | +33.9 / -36.3 | +35.1 / -34.5 | +41.9 (1.41) | 5/9 | 0.15 / -0.11, -0.44 | 0.82 / 0.10 | none |
| F2 W14 SURGE, 10:00-15:30 | US500 | -4.1 (-0.88) / -0.1 (-0.01) | 1.6 | -5.7 (-1.21) / -0.6 (-0.06) | - | -6.5 / -0.9 | -5.3 / -0.5 | -5.5 (-1.14) | 3/9 | -0.10 / -0.01 | 0.07 / 0.41 | none (wrong sign IS) |
| F3 W14 high season days, close to close 1 d (best F3) | USTEC | +13.1 (2.14) / +13.6 (0.81) | 4.1 | +9.0 (1.47) / +10.5 (0.62) | 1.2 | +8.3 / +10.2 | +9.3 / +11.6 | +9.0 (1.48) | 7/9 | 0.08 / 0.06, 0.47 | 0.63 / 0.81 | none (calendar) |
| F3 W14 high season days, close to close 1 d | US30 | +10.1 (2.19) / +17.1 (1.73) | 3.4 | +6.7 (1.45) / +14.3 (1.45) | 2.1 | +6.2 / +14.2 | +6.7 / +15.0 | +6.1 (1.37) | 9/9 | 0.08 / 0.15, 1.10 | 0.64 / 0.96 | none (calendar) |
| F3 W14 high season days, 10:00-15:30 | US30 | +4.4 (1.61) / +12.6 (1.54) | 0.8 | +3.5 (1.31) / +12.4 (1.50) | 3.5 | +3.1 / +12.2 | +3.8 / +13.5 | +3.3 (1.21) | 8/9 | 0.07 / 0.15, 1.14 | 0.69 / 0.79 | none (calendar) |
| B1 CAP >= trailing-year 2/3 q, 10:00-15:30 | US30 | +4.0 (1.34) / -2.1 (-0.38) | 0.8 | +3.2 (1.07) / -2.4 (-0.43) | <0 | +2.8 / -2.5 | +3.1 / -1.9 | (1.07) | 7/9 | 0.06 / -0.03 | 0.81 / 0.61 | none |
| B2 top-10 buyers open, season days, 10:00-15:30 (best by-product) | US500 | +6.5 (2.19) / +8.9 (1.12) | 1.6 | +4.9 (1.66) / +8.4 (1.05) | 1.7 | +4.1 / +8.2 | +5.2 / +9.0 | (1.49) | 8/9 | 0.09 / 0.09, 0.80 | 0.86 / 0.80 | none (below DEMO and chance) |
| control: F3 W14, 10:00-15:30 | US2000 | +2.6 (0.65) / +7.1 (0.62) | 2.2 | +0.3 (0.08) / +5.3 (0.47) | - | - | - | - | 4/9 | - | 0.34 / 0.46 | control |
| control: B2, 10:00-15:30 | US2000 | +6.9 (1.60) / +11.6 (1.14) | 2.3 | +4.6 (1.07) / +9.9 (0.97) | - | - | - | (0.60) | 7/9 | - | 0.89 / 0.84 | control (same as large caps) |

All 64 main rows (48 counted + 16 controls) are in `out/grade.log` / `out/cells.csv`, with x1.5, +1 min, ex-2020 and
net by year. The 16 by-product rows are in `out/byproducts.log`. Spread x1.5 and +1 min move no cell by more than
~1 bp at ID, and they change no verdict.

### The mechanism tests (mid, bp per day)
| test | US500 IS | US500 VAL | USTEC IS | US30 IS | reading |
|---|---|---|---|---|---|
| F1: W14 HIGH - LOW days, 10:00-15:30 | -0.9 (t -0.19) | -0.6 (t -0.10) | -2.0 (t -0.37) | -0.3 (t -0.07) | no buyback bid |
| F1: W0 HIGH - LOW days, close to close | -11.7 (t -1.62) | +2.1 (t 0.23) | -14.6 (t -1.72) | -9.3 (t -1.23) | wrong sign IS (open weeks are early-quarter weak days) |
| F3: slope on OPEN with week-of-quarter FE, 10:00-15:30, per +1.0 OPEN | -45.8 (t -1.29) | +48.6 (t 1.25) | -45.0 (t -1.06) | -40.8 (t -1.19) | flips sign IS -> VAL; little residual variance (R2 0.94) |
| F3: high - low season days (W14), 10:00-15:30 | +0.7 (t 0.16) | +11.7 (t 1.09) | +2.8 (t 0.51) | +2.0 (t 0.49) | IS ~0; VAL +11-15 on all four indexes, US2000 included (t ~1.1, one shared draw) |

**What is left after family 3: none in IS.** Holding the week of the quarter fixed, more open buyback capacity does
not raise the index on that day. The VAL contrast is +11 to +15 bp at t ~1.1 on all four indexes, including the
low-buyback US2000 control. The indexes are ~0.9 correlated, so this is one draw, not four.

## Cells tried and chance
- **Main grid: 48 counted cells.** F1 18, F2 18, F3 12. Controls: 16 US2000 cells, not counted.
  - Chance benchmark (per-day sign flip shared by all cells, 1,000 draws): the 95 % quantile of the max IS net t is
    2.37, with a median of 1.23.
  - The best observed is 1.47. 0 cells have IS t >= 2.
- **By-products: 12 counted cells.** The benchmark is 2.03 (median 0.62); the best is 1.66.
- **Pooled 60 cells:** benchmark 2.46.

## What this says
- **The buyback window is mostly the calendar.**
  - Dollar-weighted, the largest IS buyers (AAPL, MSFT, ORCL, CSCO, WFC, BAC, C, JPM, Alphabet, AIG, Intel) report
    within 2-5 weeks of a calendar quarter end.
  - The open share therefore moves from ~0.15 to ~0.90 at nearly the same week every quarter.
  - Off-cycle fiscal years (AAPL, MSFT, ORCL, CSCO) shift the window by days to 2 weeks, not by months.
  - So "true windows" cannot separate the bid from the calendar much better than round 23 P4 did.
- **No buyback bid at the index level.** It is absent intraday, at close to close and over 5 days, and in surges
  after release clusters.
  - The expected 1-3 bp a day is below the noise. Detecting 2 bp at the ~80 bp ID sd needs ~6,000 days per side.
  - It is also below the earnings-season drift, which at +3-11 bp a day on season days is the larger effect, and
    the one round 23 P already saw.
  - Reopening surges (F2) are negative intraday in IS. Their 3-day version flips from +35 bp IS to -36 bp VAL.
- **Earnings-season drift.** Season weeks 2-7 were positive for large caps in both eras. That is an old result (round
  23 P post hoc, round 42 E's "announcement premium" absent at the index). Splitting the season by capacity adds
  ~0-6 bp in IS, under chance, and does not beat calendar-matched random entries (56-80 %).
- **The US2000 control behaves like the large caps.** Small caps buy back little, yet the US2000 shows the same
  season-day returns, F3 and B2. So the season effect is market-wide, not a buyback bid.
- **LIVE was impossible from the count.** ~84 HIGH days a year give ~145 HOLD trades, so LIVE needs ~20 bp net on a
  10:00-15:30 trade. The best HOLD power is 1.14.

## Correlation with C3
Not computed (nothing survived).

## Exhausted (add to PROMPT "Những họ đã cạn")
- Corporate buyback windows measured firm by firm (top 200 US issuers; XBRL repurchase run-rate as filed; 8-K 2.02
  release times; windows W14 / W0) -> US500 / USTEC / US30 (US2000 control), at these horizons and splits:
  - 10:00-15:30, close to close 1 / 3 / 5 days;
  - level, reopening surges and within-season splits;
  - dollar capacity vs its trailing year;
  - the top-10 buyers only.
  The dollar-weighted window is 94 % calendar. The earnings-season drift is market-wide (US2000 shows it too), and no
  capacity effect remains once the week of the quarter is held fixed.

## Pitfalls
- **Pre-announcements.** An 8-K item 2.02 is not always the earnings release. Pre-announcements and revenue warnings
  (AAPL 2019-01-02, for example) would reopen a window weeks early. Require the reopening release to come >= 10 days
  after the period end (addendum A1).
- **XBRL repurchase tags vary.** `PaymentsForRepurchaseOfCommonStock` covers 307 of 310 firms with facts, but some firms
  used other or custom tags in some years (JPM 2011-17, for example). Cash-flow facts are YTD: build TTM as
  FY + YTD - prior YTD.
- **Facts filed after the cut.** companyconcept JSON includes 2025-26 filings, which restate earlier periods. Drop by
  `filed` at parse, not by period end.
- **Name mapping.** Vanguard 13F names are abbreviated (MTR, FINL, RLTY, CMNTYS...). Prefix matching against
  master-index names maps garbage: "BANCORP" normalises to an empty string. Expand the abbreviations and match token
  prefixes against filers active that year.
- **Module name.** A script named `signal.py` shadows the stdlib module. It is named `capsignal.py` here.
- **Speed.** The whole SEC pull (1,174 requests) took 11 minutes at 0.2 s spacing. data.sec.gov has no robots.txt
  (404).

## Directions that need the user
| direction | value |
|---|---|
| Single-stock CFDs (IC MT5 only): trade the big buyers themselves in their open windows vs blackout, firm by firm (where the literature finds the effect, e.g. stock-level returns around the end of the blackout) | LIVE ~2-3 %, DEMO ~10 % (index aggregation is what kills it; unchanged from rounds 25 / 42 / 44) |
| Paid daily buyback execution data (e.g. sell-side desk flow, or 10b-18 daily disclosures that only some countries require) | LIVE < 1 %, DEMO ~2 % (the dollar timing is calendar-bound anyway) |
| Holds over 5 days or a quarterly overlay (open weeks vs blackout weeks over 1-3 weeks) | outside the user's constraints; and the IS HIGH - LOW sign is ~0 or negative: < 1 % |

## Files
- **Scripts:** `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r47/B/scripts/`
  - fetch.py: the SEC fetcher, run under python -I.
  - build_universe.py and cik_names.py: the universe and CIK checks, under python -I.
  - parse_xbrl.py, parse_subs.py and older_pages.py: parsing under python -I, with the HOLD cut.
  - capsignal.py: the run-rate, windows and OPEN signals.
  - grade.py: the 48-cell grid and the mechanism tests.
  - byproducts.py: B1 and B2.
- **Outputs:** `.../scratchpad/r47/B/out/`
  - universe.csv, facts.csv and ea_8k202.csv (all <= 2024).
  - signal.npz and signal.log.
  - grade.log, cells.csv, trades.npz and maxt_null.npy.
  - byproducts.log.
- **Downloads:** `.../scratchpad/r47/B/web/`, with requests.log and robots/.
