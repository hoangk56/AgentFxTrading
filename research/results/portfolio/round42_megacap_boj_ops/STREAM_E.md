# Round 42 stream E: index heavyweight earnings (SEC EDGAR 8-K item 2.02) -> US500, USTEC, US30 (DE40 / JP225 controls)

Written 2026-10-30 (UTC). Hypotheses with `date -u` times, before any return:
[HYPOTHESES_E.md](HYPOTHESES_E.md). The main grid was declared at 05:04, the LEAD season rule amended at 05:06
(degenerate as first written) and by-product B1 declared at 05:09. Same LIVE / DEMO bars as research/PROMPT.md.
HOLD stayed closed: IC ts < 1735689600000 at load, and EDGAR filings dated after 2024-12-31 were dropped at parse
under python -I. The latest filing kept is dated 2024-12-19.

## Answer
There is no LIVE or DEMO candidate and no PREREG_DRAFT. This is the first round to use heavyweight earnings at the
index level: the top 40 US issuers per year by year-end market value, with the 8-K item 2.02 acceptance time to
the second. 132 cells were counted.
- The main grid has 108 cells:
  - F1a: the after-hours index reaction continues to the next open or close.
  - F1b: the open-to-close reversal on news days.
  - F2: the Savor-Wilson / Chan-Marsh index premium on announcement and LEAD days.
  - F3: pre-release drift.
- By-product B1 has 24 cells: the first minutes after the release.
- Results:
  - No cell reaches IS net t >= 2 on its declared side. The best is +1.69 (chance benchmark for the 108 cells: 3.05).
  - 34 of 108 cells are positive in IS, 47 in VAL, 13 in both.
  - B1's best IS t is 1.37, against a benchmark of 1.90.
- LIVE was ruled out by the count before any return was computed. There are 20-90 heavyweight events a year per
  cell, so a 1-day index trade would need 20-35 bp net per trade. The literature's index-level numbers are a few bp.
- The index announcement premium (F2) is not there in VAL. IS showed only the W1 close-to-close +3.6 bp (t 0.8),
  which is the swap-paying window that round 23 P had already seen post hoc as the earnings season.

## Sources
- **SEC EDGAR: 249 requests, all HTTP 200, 2026-10-30 04:57-05:02 UTC.** The User-Agent was "Mozilla/5.0
  (compatible; offline-market-research/1.0; aggregate filing timestamps)", with no name or e-mail. Requests were
  sequential through one process (single host lock), >= 0.25 s apart. The whole pull took ~5 minutes and 139 MB.
  SEC did not block anything.
  - Vanguard Group 13F-HR info tables (CIK 102909), year-ends 2015-2023, 9 files (www.sec.gov/Archives): these give
    the company list.
  - www.sec.gov/files/company_tickers.json, used for CIK mapping. Names that did not match were mapped by hand
    against the EDGAR master index names that round 41 B had already downloaded.
  - data.sec.gov/submissions/CIK##########.json for 71 CIKs, plus 159 older `-submissions-NNN.json` pages: the
    8-K item 2.02 acceptance times.
  - Logs: `web/sec/requests.log`, `web/subs/requests.log`.
- **Unusable:** the iShares IVV historical holdings CSV (`...1467271812596.ajax?...asOfDate=`) now returns an HTML
  page (2 probes). It was replaced by Vanguard's 13F values, which rank issuers by total US market value; S&P float
  weights are not available. I made no WebSearch beyond 1, the Chan & Marsh citation check.
- **Company list** (top 40 per year after dropping funds and 6-K filers; the full lists are in HYPOTHESES_E.md):
  - 2016 starts AAPL MSFT GOOGL XOM JNJ GE WFC AMZN JPM BRK-B PG FB; 2024 starts AAPL MSFT GOOGL AMZN NVDA META TSLA
    BRK-B AVGO JPM.
  - FB and META are one CIK (1326801). Disney's CIK changed in 2019-03 and Broadcom's in 2018-04; both CIKs are kept.
- **Releases:**
  - 2,692 8-K 2.02 filings in 2015-10..2024-12; 1,510 by top40 companies in their list year, 376 by top10.
  - `acceptanceDateTime` is true UTC. The hour histogram peaks at 10-12 UTC (06-08 ET) and 20-21 UTC (16-17 ET).
  - POST releases (after the close): 64 % accepted 16:00-16:14 ET, 14 % 16:15-16:29, 10 % 16:30-16:44. PRE releases
    (before the open): mostly 06:00-08:59 ET.
- **Prices:** IC M1 bid / ask US500, USTEC, US30, DE40, JP225, cut at 2025-01-01. There is no US index series before
  2016 in research/data, so there is no PRE era.

## Counts and power (before returns)
| per symbol | events/yr | HOLD n | LIVE Sharpe/trade | IS n | IS-t-2 Sharpe |
|---|---|---|---|---|---|
| top40 news sessions | ~88 | ~150 | 0.24 | ~500 | 0.09 |
| top40 POST evenings | ~50 | ~85 | 0.33 | ~270 | 0.12 |
| ... with abs z >= 1 | ~20 | ~35 | 0.51 | ~110 | 0.19 |
| sessions with >= 3 releases | ~20 | ~35 | 0.51 | ~130 | 0.18 |
| top10 news sessions | ~32 | ~55 | 0.40 | ~180 | 0.15 |

Trade sds are ~55 bp from 16:00 to 09:30, ~90 bp from 09:30 to 16:00 and ~110 bp close to close (US500). So LIVE
needs 20-35 bp net per trade, and DEMO ~9-19 bp at mid in IS. The three indexes are ~0.9 correlated, so pooling adds
nothing.

Quote coverage cut the realised counts. IC M1 has few 16:44 bars in 2016-17, which matters for E_a. There are no
bars at 16:15-16:29 or 16:59-17:59 ET. The trailing 250-day sd needs 150 finite days, so the k = 1 cells have almost
no 2016-17 trades.

## Results (net per trade in bp, t = day-clustered = plain, one trade per symbol-day)
Best cells per family by IS net t, plus representative full-sample cells. "rnd" is the share of 200 random-entry
draws that the cell beats in IS. "power" is per-trade net Sharpe x sqrt(HOLD n) at the VAL size.

| hypothesis | sym | mid IS (t) / VAL (t) | cost | net IS (t) / VAL (t) | VAL/IS | Sharpe IS/VAL, power VAL | rnd | verdict |
|---|---|---|---|---|---|---|---|---|
| F1a top10, 16:45 -> next 16:00, abs z >= 1 (best F1a) | US500 | +42.8 (1.83) / +23.9 (0.88) | 3.3 | +39.5 (1.69) / +21.8 (0.80) | 0.55 | 0.34 / 0.14, 0.61 | 0.90 | none (n 25 / 32) |
| F1a top10, 16:45 -> 09:30, all | USTEC | +15.0 (2.34) / -14.1 (-1.00) | 4.7 | +10.3 (1.60) / -16.6 (-1.17) | <0 | 0.18 / -0.16, -0.89 | 0.97 | none |
| F1a top40, 16:45 -> 09:30, all | US500 | +1.1 (0.19) / -9.0 (-1.72) | 3.4 | -2.3 (-0.40) / -11.4 (-2.17) | - | -0.03 / -0.19 | 0.69 | none |
| F1a top40, 19:00 -> 09:30, all | US500 | -11.0 (-2.05) / +4.6 (1.08) | 2.1 | -13.1 (-2.43) / +3.5 (0.82) | - | -0.17 / 0.07 | 0.20 | none (IS reverses) |
| F1b top40 reversal, all (best F1b) | US30 | +2.7 (0.84) / -2.2 (-0.45) | 0.9 | +1.8 (0.57) / -2.5 (-0.51) | <0 | 0.03 / -0.03 | 0.62 | none |
| F1b top10 reversal, all | US500 | -11.8 (-2.36) / +4.5 (0.40) | 1.6 | -13.4 (-2.68) / +4.0 (0.36) | - | -0.21 / 0.04 | 0.01 | none (wrong sign IS) |
| F2 LEAD, close -> close long (best F2) | US30 | +13.3 (2.08) / +1.4 (0.13) | 3.4 | +9.9 (1.55) / -1.4 (-0.13) | <0 | 0.12 / -0.01 | 0.84 | none |
| F2 LEAD, close -> close long | US500 | +12.2 (1.81) / -8.8 (-0.70) | 4.1 | +8.1 (1.20) / -11.8 (-0.94) | <0 | 0.09 / -0.11 | 0.77 | none |
| F2 top40 k >= 1, close -> close long | US500 | +7.6 (1.65) / +3.0 (0.45) | 4.0 | +3.6 (0.78) / +0.1 (0.01) | 0.03 | 0.04 / 0.00, 0.01 | 0.69 | none |
| F2 top40 k >= 1, open -> close long | US500 | +0.2 (0.06) / -5.2 (-0.94) | 1.6 | -1.4 (-0.43) / -5.7 (-1.04) | - | -0.02 / -0.06 | 0.33 | none |
| F2 top40 k >= 3, open -> close long | US500 | +3.9 (0.66) / -5.7 (-0.43) | 1.7 | +2.2 (0.38) / -6.3 (-0.47) | <0 | 0.03 / -0.06 | 0.60 | none |
| F3 top10, close -> close long into the release (best F3) | USTEC | +14.2 (1.10) / -1.3 (-0.06) | 4.2 | +10.0 (0.78) / -4.0 (-0.18) | <0 | 0.08 / -0.02 | 0.57 | none |
| F3 top40, open -> close long on release day | US500 | -1.7 (-0.33) / -2.3 (-0.33) | 1.6 | -3.3 (-0.64) / -2.8 (-0.41) | - | -0.04 / -0.03 | 0.21 | none |
| B1 top40, A_last+2 -> 16:58, all (best B1) | US30 | +2.9 (2.07) / +2.1 (1.33) | 1.0 | +1.9 (1.37) / +1.8 (1.13) | 0.91 | 0.13 / 0.12, 0.86 | 0.90 | none |
| B1 top40, A_last+2 -> 16:58, all | USTEC | +2.2 (1.00) / +5.3 (1.84) | 2.5 | -0.3 (-0.15) / +4.1 (1.43) | - | -0.01 / 0.16, 1.09 | 0.64 | none |
| B1 top40, A_last+2 -> 16:58, all | US500 | -0.6 (-0.35) / +3.9 (1.95) | 1.9 | -2.6 (-1.41) / +2.8 (1.42) | - | -0.15 / 0.16, 1.08 | 0.22 | none |
| control: F1a 19:00 -> 09:30 on DE40 | DE40 | -18.8 (-2.65) / +6.5 (1.12) | 3.3 | -22.1 (-3.11) / +4.6 (0.79) | - | - | 0.12 | control |
| control: same on JP225 | JP225 | -12.7 (-1.52) / +3.6 (0.44) | 4.0 | -16.7 (-2.00) / +1.1 (0.13) | - | - | 0.24 | control |

All 108 + 24 rows, with x1.5, +1 min, ex-2020-03/04 t, years positive and per-year counts, are in
`out/grade.log` / `out/cells.csv` and `out/b1.log`. Spread x1.5 and +1 min change no verdict: no cell passes at base
cost. Ex-2020-03/04, the best IS t is 1.52 (F1a top40 16:45 -> 09:30, abs z >= 1, US500), with VAL -10.9.

## Cells tried and chance
- Main grid: 108 counted cells. F1a 48, F1b 12, F2 30, F3 18.
  - Chance benchmark (per-day sign flip shared by all cells, 1,000 draws): the 95 % quantile of the max IS net t
    is 3.05. The best observed is 1.69.
  - 0 cells have IS t >= 2; 4 have IS t <= -2 (wrong side).
- B1: 24 cells (benchmark 1.90, best 1.37). 132 in total. Controls (4 cells on DE40 / JP225) were not counted.

## What this says
- **After-hours continuation (F1a) is not stable.**
  - From the 16:45 entry, the top10 cells are positive in IS: +3 to +40 bp, t up to 1.7.
  - The same cells are negative or near zero in VAL to 09:30: US500 -15, USTEC -17.
  - From the 19:00 entry, every US index *reverses* in IS (t -1.5 to -2.4) and continues in VAL. DE40 and JP225
    do the same at the same clock (-22 / -17 bp IS).
  - So the 19:00 pattern is an evening-session property of 2016-21, not something heavyweight news causes. The
    random control at 0.20 says the same: earnings evenings are no better than random evenings.
- **Attention reversal (F1b) has the wrong sign in IS.** On top10 news days the index *continued* its overnight gap
  intraday in IS: the reversal side lost 13.4 bp (t -2.7, random 0.01). In VAL it was +4.0 (t 0.4), roughly flat.
  This is noise around zero, not a flipped edge: the continuation side would also fail in VAL. The side is not
  flipped.
- **The announcement premium (F2) is not visible at the index level.**
  - Long close-to-close on top40 news days: +3.6 bp IS (t 0.8) and +0.1 VAL. LEAD days: +8 to +10 IS (t 1.2-1.6)
    and -1 to -12 VAL.
  - Intraday (open to close) it is ~0 or negative in both eras.
  - This matches the literature's "disappearing earnings announcement premium" after 2004 (round 25 A). The
    close-to-close IS number sits in the earnings-season window that round 23 P already saw post hoc. It does not
    hold out of sample.
- **Pre-release drift (F3) is absent.** Every intraday cell is negative in IS. Close-to-close is +/- a few bp with
  t < 1.
- **The first minutes after the release (B1) are mid-positive but sub-cost.**
  - Continuation from A_last + 2 min to 16:58 is +2 to +5 bp at mid in VAL (t 1.3-1.95), but 0 to +3 in IS.
  - US500 and USTEC pay 1.9-2.5 bp of spread at 16:00-16:45 ET, so their IS net is <= 0.
  - US30, the cheapest at 1.0 bp, has the most stable cell: +1.9 / +1.8 bp net, t 1.37 / 1.13, Sharpe 0.12 a
    trade, power 0.86 at ~50 HOLD trades. That is below DEMO (IS t 2) and far below LIVE.

## Correlation with C3
Not computed (nothing survived).

## Exhausted (add to PROMPT "Những họ đã cạn")
- Index heavyweight earnings (the top 40 US issuers by year-end 13F value, with 8-K item 2.02 acceptance times)
  -> US500 / USTEC / US30, at these horizons:
  - after-hours reaction continuation to the next open or close (16:45 or 19:00 entry);
  - open-to-close reversal on news days;
  - the index announcement premium on news, cluster (>= 3) and early-season (LEAD) days;
  - pre-release drift on the release day;
  - the first 10-60 minutes after the release.
  The index is priced within minutes, and the remaining after-hours drift (+2-5 bp at mid, VAL only) is below
  IC's after-hours spread.

## Pitfalls
- EDGAR submissions `acceptanceDateTime` is real UTC ("Z"). Convert it to ET: the releases sit at 06-08 ET and
  16:00-16:15 ET. The `recent` block covers only ~1-3 years for megacaps (Form 4 volume), so the older
  `-submissions-NNN.json` pages are needed (159 pages for 63 CIKs).
- The JSON contains 2025-26 filings: filter at parse before printing anything.
- The iShares `.ajax?fileType=csv` holdings link now returns HTML. Vanguard's 13F info table is a clean public
  substitute for year-end market value ranks: sum by issuer across share classes, drop funds and 6-K filers.
- IC index CFDs have no bars at 16:15-16:29 and 16:59-17:59 ET. Few 16:44 bars exist in 2016-17. A 19:00 ET Friday
  quote does not exist. An exit "at 16:59" falls into the rollover gap (B1's +1 min variant of H2 is NaN).
- Off-cycle reporters (ORCL, NKE, CSCO, HD, WMT, COST, ADBE, MDT, ACN) fill the gaps between seasons. A
  "gap >= 20 sessions" season rule finds only 4 of 36 seasons; use a calendar start (the 8th of Jan / Apr / Jul /
  Oct).

## Directions that need the user
| direction | value |
|---|---|
| Single-stock CFDs (IC MT5 only, round 25 A): trade the heavyweight itself after its release (post-earnings drift and employee selling after the blackout, Hartzmark & Solomon) | LIVE ~3-5 %, DEMO ~25 % (unchanged from round 25; this round's index-level null does not speak to stock-level drift) |
| A cheaper after-hours index venue (futures ES / NQ / YM at ~0.25-0.5 bp a side): B1 continuation is +2-5 bp at mid in VAL | LIVE ~1 %, DEMO ~3 % (the IS mid is ~0, so a lower cost alone does not pass IS t 2) |
| Paid S&P float weights and point-in-time earnings calendars with expected dates (to test surprise-sized signals, e.g. reaction / implied move) | LIVE < 1 %, DEMO ~2 % |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r42/E/scripts/`
  - fetch.py: the SEC fetcher, run under python -I.
  - parse_13f.py, map_cik.py, manual_cik.csv, build_list.py: the company list.
  - older_pages.py, parse_subs.py: EDGAR parsing under python -I, with the HOLD cut.
  - events.py, count_events.py, season_check.py, sess_check.py, diag_cov.py: events, counts and checks.
  - grade.py: the main grid. b1.py: by-product B1.
- Outputs: `.../scratchpad/r42/E/out/`
  - top13f.csv, company_list.csv, ea_8k202.csv (2016-24 only);
  - cells.csv, grade.log, b1.log, trades.npz, maxt_null.npy.
- Downloads: `.../scratchpad/r42/E/web/` (sec/, subs/, probe/, each with its requests.log).
