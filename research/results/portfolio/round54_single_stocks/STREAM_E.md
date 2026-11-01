# Round 54 stream E: blackout selling (Hartzmark & Solomon 2022) and large-cap post-earnings drift on Dukascopy US stock CFDs

Written 2026-10-30 (UTC). Hypotheses with `date -u` times, before any return: [HYPOTHESES_E.md](HYPOTHESES_E.md).
The main grid was declared at 10:09:25. Addendum A1 (10:18:31, before any return) added 6 close-entry cells for H1.
Addendum A2 (10:39:56, after D's READY, before any return) added the optimistic open-spread bound as a reported cost
sensitivity. Same LIVE / DEMO bars as research/PROMPT.md.

HOLD stayed closed:
- stocklib cuts at 2024-12-31 at load; IC US500 / USTEC ts < 1735689600000 at load (asserted);
- XBRL facts filed after 2024-12-31 were dropped at parse under python -I (13,576 dropped; latest kept 2024-12-20);
- 8-K 2.02 filings after 2024-12-31 were dropped at parse (latest kept 2024-12-19).

## Answer
There is no LIVE or DEMO candidate and no PREREG_DRAFT.
- **H1, blackout selling (H-STK), has the wrong sign even at mid.** In IC-sized large caps 2017-24, shorting the top
  quintile of stock compensation over market cap after the release loses at mid:
  - IS -29.5 bp (t -1.52) and VAL -29.1 bp (t -1.14) from the day-1 open to the day-3 close;
  - the top 5 % loses -36 / -40 bp;
  - on the same dates the bottom quintile is ~0 (IS -4.3, VAL +10.9).
  So high-SBC large caps *outperform* the index after their releases. The paper's -87.5 bp (all US firms, 2002-20)
  is not in these names.
- **Costs alone kill every cell.**
  - With an open entry, the Dukascopy first-quote open spread costs 46 bp a stock leg, and the round trip comes to
    56-83 bp.
  - With a close entry it is 29-43 bp, because IC's USD 0.02 per share costs 12 bp a round trip on these names
    (median price $61, and cheap names such as GPS, M, KSS, CTL and MAT sit in the top quintile).
  - Every H1 cell is net negative in both eras, with IS t -2.0 to -5.6.
- **H2, PEAD at 1-5 days:**
  - Following the full announcement return (R_ear) shows a small large-cap drift at mid: +17.1 bp (t 1.62) IS and
    +9.9 bp (t 0.76) VAL at 3 days. That is below the 27-33 bp cost, so net is -10.0 / -23.5.
  - The brief's open-to-close reaction (R_oc) has no drift (mid -3 / -3).
  - The reverse side (Milian 2015) is negative at mid.
  - All 12 cells are net negative.
- **Chance.** No counted cell has positive IS net. The best IS net t is -0.94 (H2 ear follow 3 d). The benchmarks
  are 2.61 (H1, 16 cells), 2.55 (H2, 12 cells) and 2.80 (pooled 28).

## Sources (robots and requests)
- **robots.txt, read first (10:09 UTC).**
  - www.sec.gov has only a `User-agent: *` block, with no ClaudeBot / anthropic-ai / Claude-Web entry. /files and
    /Archives are not disallowed.
  - data.sec.gov returns 404 for robots.txt.
- **SEC requests.**
  - 1,272 requests, 10:10:00-10:19:40 UTC, 39.6 MB: 1,117 HTTP 200 and 155 HTTP 404 (the firm never used that tag).
    No 403 / 429 / 503.
  - User-Agent "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate filing statistics)", with no name or
    e-mail. One sequential process, >= 0.16 s spacing. Stream D's SEC fetches ran at the same time, and nothing was
    throttled.
  - XBRL companyconcept: `us-gaap/ShareBasedCompensation`, `us-gaap/AllocatedShareBasedCompensationExpense` and
    `dei/EntityCommonStockSharesOutstanding` for 388 CIKs (round 47's 333 plus 55 from D's list): 1,164 requests.
  - Submissions JSON for 55 new CIKs, plus 53 older pages: 8-K 2.02 times for 38 firms.
  - company_tickers.json: 1 request.
- **Reused from disk:** round 47 B `ea_8k202.csv` (12,298 8-K 2.02 filings for 333 CIKs) and its universe CIKs.
- **Prices:** stream D's `stocks_daily.npz`, with Dukascopy daily bid / ask for 219 stocks. Data start 2016-09-26,
  most names 2017-01..11, all names from 2018. IC US500 / USTEC M1 at 09:30 / 16:00 ET serve as the hedge.
- **Coverage:**
  - Events: 5,340 releases for 204 firms after the pre-announcement filter (first 8-K 2.02 10-100 days after the
    period end).
  - 3,838 of them (72 %) have an S rank. The missing 28 % are mostly banks and insurers without the
    ShareBasedCompensation tag, and firms whose dei share count is missing or stale.
- WebSearch: 0.

## Counts and power (before returns; events from EDGAR and D's calendar)
| cell | IS n | VAL n | VAL / yr | HOLD n (1.73 y) | LIVE Sharpe needed |
|---|---|---|---|---|---|
| H1 top quintile | 446 | 308 | 103 | ~178 | 0.22 |
| H1 top decile | 227 | 162 | 54 | ~93 | 0.31 |
| H1 top 5 % (reported) | 118 | 83 | 28 | ~48 | 0.43 |
| H2 quintile tails (per measure) | ~1,170 | ~900-990 | ~310 | ~540 | 0.13 |

Concurrency, primary H1 quintile with a 3-day hold: on active days there are on average 2.2 positions open, p95 5 and
max 11. That needs ~4 bots of 3 positions each, or one bot per stock.

## Results (net bp per trade, hedged 1:1 with US500 unless stated; t day-clustered by entry day)
"rnd" is the share of 200 same-date random-firm draws that the cell beats, stock leg, IS / VAL. "optb" is net with
the close spread charged at the open (A2). "power" is per-trade net Sharpe x sqrt(HOLD n) at the VAL size.

| hypothesis | mid IS (t) / VAL (t) | cost IS / VAL | net IS (t) / VAL (t) | x1.5 IS / VAL | +1 d IS / VAL | optb IS / VAL | ex-2020-03/04 IS (t) | yrs > 0 | Sharpe IS / VAL, power | rnd | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 Q, d1 open -> d3 close **(primary)** | -29.5 (-1.52) / -29.1 (-1.14) | 63.7 / 70.3 | -93.2 (-4.75) / -99.4 (-3.67) | -116 / -126 | -90 / -90 | -60.6 / -64.5 | -91.3 (-4.68) | 0/8 | -0.23 / -0.23, -3.1 | 0.00 / 0.00 | none |
| H1 Q, d1 open -> d1 close | -11.8 (-1.00) / -24.1 (-1.78) | 56.0 / 68.7 | -67.8 (-5.63) / -92.7 (-6.28) | -91 / -120 | -74 / -73 | -35.7 / -58.6 | -69.6 (-5.77) | 0/8 | -0.28 / -0.35 | 0.01 / 0.00 | none |
| H1 Q, d1 open -> d5 close | -24.8 (-1.03) / -45.6 (-1.62) | 69.3 / 73.8 | -94.1 (-3.89) / -119.3 (-4.04) | -117 / -145 | -101 / -93 | -61.8 / -84.7 | -90.3 (-3.87) | 0/8 | -0.20 / -0.25 | 0.07 / 0.01 | none |
| H1 Q, d0 open -> d3 close (paper t0..t+3) | -28.4 (-1.07) / -47.6 (-1.55) | 78.0 / 79.0 | -106.5 (-3.91) / -126.6 (-3.93) | -135 / -156 | -102 / -119 | -64.3 / -88.1 | -103.5 (-3.76) | 0/8 | -0.19 / -0.23 | 0.00 / 0.00 | none |
| H1 Q, d1 open -> d3 close, USTEC hedge | -26.3 (-1.30) / -28.2 (-1.10) | 63.3 / 70.4 | -89.6 (-4.37) / -98.6 (-3.65) | -112 / -125 | -68 / -83 | -57.0 / -63.8 | -86.8 (-4.27) | 0/8 | -0.21 / -0.23 | 0.00 / 0.00 | none |
| H1 Q, d0 close -> d3 close (A1, paper's t+1..t+3) | -29.2 (-1.44) / -18.3 (-0.70) | 36.1 / 40.2 | -65.3 (-3.22) / -58.5 (-2.16) | -72 / -68 | -59 / -57 | = net | -66.4 (-3.35) | 0/8 | -0.15 / -0.14, -1.8 | 0.03 / 0.07 | none |
| H1 Q, d0 close -> d1 close (A1) | -13.3 (-0.98) / -14.8 (-1.01) | 28.9 / 39.5 | -42.2 (-3.09) / -54.2 (-3.51) | -49 / -65 | -42 / -43 | = net | -48.7 (-3.75) | 0/8 | -0.15 / -0.20 | 0.07 / 0.01 | none |
| H1 D, d1 open -> d3 close | -42.8 (-1.33) / +1.2 (+0.03) | 68.2 / 76.4 | -111.0 (-3.42) / -75.2 (-1.99) | -135 / -103 | -106 / -72 | -75.8 / -39.2 | -117.1 (-3.58) | 1/8 | -0.23 / -0.16 | 0.01 / 0.21 | none |
| H1 D, d0 close -> d3 close (A1) | -33.1 (-0.94) / +20.1 (+0.56) | 37.2 / 45.1 | -70.2 (-1.98) / -25.0 (-0.67) | -77 / -35 | -76 / -48 | = net | -87.7 (-2.64) | 1/8 | -0.14 / -0.05 | 0.01 / 0.59 | none |
| H1 D, d0 close -> d1 close (A1, best VAL mid) | -28.4 (-1.21) / +14.1 (+0.65) | 30.5 / 46.1 | -59.0 (-2.50) / -32.0 (-1.38) | -66 / -44 | -36 / -43 | = net | -72.2 (-3.25) | 0/8 | -0.17 / -0.11 | 0.02 / 0.38 | none |
| H1 top 5 %, d1 open -> d3 close (reported) | -35.9 (-1.07) / -39.8 (-0.70) | 74.0 / 86.6 | -109.8 (-3.30) / -126.4 (-2.00) | - | -123 / -91 | -70.5 / -84.8 | -112.4 (-3.35) | 1/8 | -0.31 / -0.23 | 0.02 / 0.01 | rep |
| H1 top 5 %, d0 close -> d3 close (reported) | -20.2 (-0.56) / -27.6 (-0.48) | 38.5 / 50.4 | -58.7 (-1.63) / -78.0 (-1.27) | - | -87 / -78 | = net | -72.0 (-2.12) | 2/8 | -0.15 / -0.15 | 0.15 / 0.10 | rep |
| contrast: bottom quintile, same short, d1 open -> d3 close | -4.3 (-0.30) / +10.9 (+0.65) | 46.1 / 52.4 | -50.4 / -41.5 | - | - | -25.9 / -15.2 | - | 0/8 | - | - | rep |
| H2 R_ear follow, d0 close -> d3 close (best H2) | +17.1 (+1.62) / +9.9 (+0.76) | 27.1 / 33.4 | -10.0 (-0.94) / -23.5 (-1.79) | -15 / -32 | -30 / -34 | = net | -12.0 (-1.15) | 3/8 | -0.03 / -0.06 | 0.98 / 0.84 | none |
| H2 R_ear follow, d0 close -> d1 close | +9.5 (+1.47) / +7.1 (+0.88) | 21.0 / 31.3 | -11.5 (-1.76) / -24.1 (-2.91) | -17 / -35 | -14 / -26 | = net | -11.6 (-1.81) | 2/8 | -0.06 / -0.10 | 0.98 / 0.50 | none |
| H2 R_ear follow, d0 close -> d5 close | +7.2 (+0.63) / +9.6 (+0.70) | 32.4 / 38.5 | -25.2 (-2.18) / -28.9 (-2.08) | -31 / -38 | -35 / -31 | = net | -27.8 (-2.45) | 1/8 | -0.07 / -0.07 | 0.83 / 0.80 | none |
| H2 R_oc follow, d0 close -> d3 close **(primary)** | -2.9 (-0.30) / -2.6 (-0.20) | 27.6 / 33.3 | -30.5 (-3.16) / -35.9 (-2.74) | -36 / -45 | -35 / -41 | = net | -29.4 (-3.08) | 1/8 | -0.09 / -0.10 | 0.42 / 0.43 | none |
| H2 R_oc reverse, d0 close -> d5 close (best reverse) | +5.6 (+0.46) / +20.8 (+1.43) | 32.6 / 38.6 | -27.0 (-2.19) / -17.8 (-1.21) | -33 / -27 | -26 / -6 | = net | -26.0 (-2.17) | 1/8 | -0.07 / -0.04 | 0.67 / 0.91 | none |
| H2 R_ear reverse, d0 close -> d3 close | -17.1 (-1.62) / -9.9 (-0.76) | 26.9 / 33.4 | -44.1 (-4.17) / -43.3 (-3.32) | -49 / -52 | -23 / -28 | = net | -41.7 (-4.02) | 0/8 | -0.13 / -0.12 | 0.02 / 0.10 | none |

All 28 counted rows and 4 reported rows, with by-year nets, are in `out/grade.log` and `out/cells.csv`.

By year, net (bp), for the primary H1 quintile row (d1 open -> d3 close):

| 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| -43 | -75 | -89 | -150 | -71 | -152 | -41 | -103 |

The H2 R_ear follow 3 d row by year:

| 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| +60 | -14 | -24 | -15 | +6 | +11 | -58 | -23 |

Stock-leg costs for the primary H1 row:
- open spread 46.4 bp (close entry: 14.2);
- commission 12.2 bp;
- financing 0.6 bp.

On day 0 the event names' close spread (median 10.6 bp) is wider than the other names' (6.9 bp) on the same days.

## Cells tried and chance
- **H1: 16 counted cells**, 10 declared and 6 from A1. The chance benchmark (per-entry-day sign flip shared by all
  cells, 1,000 draws) is 2.61, with a median of 1.36. The best IS net t is -1.98. 0 cells have IS net > 0.
- **H2: 12 counted cells.** The benchmark is 2.55 (median 1.46). The best IS net t is -0.94. 0 cells have IS net > 0.
- **Pooled 28 cells:** the benchmark is 2.80.
- Reported, not counted: 4 rows (top 5 % x 2 and the bottom-quintile contrast x 2), and the optb, x1.5 and +1 day
  variants of every row.

## What this says
- **The HS 2022 blackout-selling pressure is not in IC-sized large caps.**
  - The paper's effect comes from all US firms, small caps included, over 2002-20, and it is not in the AER 2025
    version.
  - In the 204 Dukascopy names from 2017 to 2024, the top-SBC/mcap quintile *rises* relative to US500 and USTEC
    after the blackout lifts: -29 bp for the short in both eras at mid. The bottom quintile is flat.
  - The top-SBC names are mostly tech (CRM, QCOM, ORCL, CSCO, INTC, ADSK, PYPL, AMZN, INTU, AVGO, TSLA), and they had
    good post-earnings runs in 2017-24.
  - The sign was declared from the mechanism, so it is not flipped. Flipping it on this evidence would be a post-hoc
    side choice, and even flipped it does not pay: +29 bp at mid against a 36-64 bp cost.
- **Large-cap PEAD exists at mid but is far below cost.**
  - Following the full 1-day reaction earns +10-17 bp at mid over 3 days, IS t 1.6, VAL 0.8.
  - IC's per-share commission and the post-earnings spread cost ~27-33 bp a round trip on these names.
  - The brief's open-to-close reaction has no drift. Milian's reversal is negative at mid.
- **The cost structure is the binding constraint for single-stock CFDs at IC on 1-5 day holds.**
  - The Dukascopy open spread is the day's first quote (median 65 bp; 46 bp a leg on the day after earnings). The
    optimistic close-spread bound halves the H1 open cost, and every cell is still negative.
  - Commission is USD 0.02 a share: 12 bp a round trip at the event names' prices, and ~40 bp under $10.
  - A stock trade needs a >= 30 bp per-trade edge at a close entry. No large-cap effect in this literature is that
    large at 1-5 days.

## Correlation with C3
Not computed: nothing survived. `research/results/portfolio/trades_C3_gotobi_jpy_basket.csv` is present.

## Exhausted (add to PROMPT "Những họ đã cạn")
- Single-stock CFDs (Dukascopy daily bid / ask, IC MT5 cost model; 204 US large caps 2017-24, 8-K 2.02 release
  times, XBRL stock comp / cover shares as filed):
  - employee selling after the earnings blackout (HS 2022): short the top quintile / decile of SBC over market cap,
    from the day-0 or day-1 open or the day-0 close, held 1 / 3 / 5 days, hedged with US500 / USTEC. It has the wrong
    sign at mid in both eras.
  - post-earnings drift at 1-5 days, following or reversing the open-to-close or the full 1-day reaction (z-scored,
    IS quintile tails). Mid +10-17 bp on the full-reaction follow side, under 27-33 bp of cost.

## Pitfalls
- **Dukascopy open quotes.** The daily candle's open is the session's first quote: a median spread of 65 bp, and
  46 bp a leg on post-earnings mornings. Any open-entry stock rule must use the close spread only as an optimistic
  bound.
- **IC commission.** USD 0.02 per share per side is not small for these names. The top SBC/mcap quintile is loaded
  with cheap, small-cap-for-the-list names (GPS, M, KSS, MAT, CTL, TEVA, HPQ), where the commission alone is
  20-40 bp a round trip.
- **Missing S ranks.** 28 % of events have no rank: banks and insurers often lack the `ShareBasedCompensation` tag,
  and some firms have no `dei:EntityCommonStockSharesOutstanding` in a 10-Q / 10-K within 200 days.
- **SBC seasonality.** BAC and other banks book retirement-eligible grants in Q1, so their Q1 quarter is outsized.
  Quarters are derived from YTD (Q = YTD - prior YTD; Q4 = FY - 9M).
- **Market cap units.** Cover-page shares x the raw (unadjusted) close on the cover filing date keeps both in pre- or
  post-split units. D's split-adjusted prices would mix units here.
- **Old tickers.** Dukascopy uses old tickers (FB, PCLN, CTL, HCN, GPS). D's symbols.csv carries hand CIKs for 11
  of them.
- **Old parser.** Round 47's parse_xbrl picked up repurchase concepts when its web directory was added; this
  stream's parser keeps them but the grader ignores them.
- **Shared SEC host.** Streams D and E hit SEC at the same time without throttling. Keep each process at >= 0.15 s.

## Directions that need the user
| direction | value |
|---|---|
| A US share venue without per-share commission and with real opening spreads (e.g. DMA / futures-style pricing, ~5-8 bp a round trip): the large-cap full-reaction drift is +10-17 bp at mid | LIVE < 1 %, DEMO ~3 % (IS t 1.6 at mid, VAL 0.8; it would need the IS size to hold) |
| Small caps (where HS 2022 and the classic PEAD live): not in IC's or Dukascopy's lists | LIVE ~1 % (small-cap spreads and borrow eat the effect for a retail CFD) |
| Paid consensus data (I/B/E/S SUE) for a surprise-sorted PEAD in large caps | LIVE < 1 %, DEMO ~2 % (the reaction already proxies the surprise; Martineau 2022 finds large-cap PEAD gone) |

## Files
- Hypotheses: `research/results/portfolio/round54_single_stocks/HYPOTHESES_E.md`
- **Scripts:** `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/E/scripts/`
  - fetch.py: the SEC fetcher, under python -I. chain.sh: the fetch order.
  - parse_xbrl.py: SBC quarters and cover shares, with the HOLD cut.
  - events.py: releases, with the pre-announcement filter.
  - idx_daily.py: US500 / USTEC 09:30 / 16:00 quotes.
  - grade.py: the 28-cell grid, chance benchmark, random control and concurrency.
  - sanity.py and costparts.py: checks.
- **Outputs:** `.../scratchpad/r54/E/out/`
  - sbc_q.csv, shares.csv, pends.csv, ea_new.csv, events.csv, idx_daily.npz;
  - grade.log, grade_run.log, cells.csv, trades.npz.
- **Downloads:** `.../scratchpad/r54/E/web/`, with requests.log and robots/.
