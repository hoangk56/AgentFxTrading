# Round 42 stream J: BoJ JGB purchase operations (rinban) -> USDJPY, EURJPY, JP225 (XAUUSD control), 2026-10-30

Hypotheses: [HYPOTHESES_J.md](HYPOTHESES_J.md). F1-F3 were declared at 05:08 UTC, before any return. Amendment 1
(05:14 UTC, before any F2a return) covers how F2a parses the PDFs. HOLD stayed closed: IC M1 is cut at
ts < 1735689600000 at load, and BoJ rows with an offer date after 2024-12-31 are dropped at parse (asserted). The only
2025-26 material on screen was link file names on two BoJ index pages, never values.

## Answer
**No LIVE or DEMO candidate.** None of the 96 eligible cells reaches IS t 2. The best positive IS t is 1.65, from 7
events. The largest |t| is 2.90, and it has the wrong sign. Chance gives a best |t| of 2.68 (median) for 96 cells.
- Offer-to-cover and cut-off surprises in rinban results carry no 1-3-day signal for the yen or the Nikkei on their
  declared side.
- At the candidate release minutes, tick activity on operation days is the same as on other days. The market does not
  trade the results.
- Within-month changes to the amount offered move EURJPY in all three eras: PRE mid +25.9 bp (t 2.33), IS net +15.4
  (t 1.40), VAL +24.9 (t 1.81). They do not move USDJPY (IS +1.9, VAL -0.2). So it is not the declared JPY mechanism,
  and the cell fails DEMO on IS t. Not registered.
- PREREG_DRAFT: none.

## Sources (04:54-05:12 UTC; 325 requests, ~27.6 MB, 3 failed (404); log in web/requests.log)
| source | span used | rows | notes |
|---|---|---|---|
| BoJ "Market Operations by the Bank of Japan (Monthly)" `m_release/YYYY/opeYYMM.{zip,xlsx}` | 2013-06..2024-12 (139 files; requests stop at 2024-12) | 4,098 JGB purchase rows: 3,316 conventional competitive ops, 389 fixed-rate rows | 3 layouts (xls in zip to 2016-11; xlsx 2016-12..2019-04 with a JGB section; bilingual 2019-05..). Offer date, bucket, amount offered, bids, successful, cut-off and average yield spread, pro-rata. PDF only before 2013-06 (not used) |
| BoJ schedule / outline releases (index `mopo/measures/mkt_ope/ope_f/index.htm`, PDFs `mpmdeci/mpr_YYYY/`) | 2013-04..2024-12 (167 PDFs) | 141 schedule docs, 20 YCC-type announcements | text pulled with a stdlib inflate. Amounts are in the text for 2014-16 and 2020-24 only. The 2016-09..2020-02 outlines put amounts in an attachment that isn't in the text, so they were dropped (Amendment 1). 2020+ docs confirm the release time: "5 p.m." |
| BoJ operation timetable `opetime.htm` | current only | | competitive: offer 10:10, results ~12:00 JST; fixed-rate: results ~15:50. I couldn't find the history of these times (the old www3 daily pages `menuold_o_YYYY.htm` return 404), so entries sit after any plausible release |
No robots.txt on www.boj.or.jp or www3.boj.or.jp (404). Requests were spaced 1.3 s apart, with a browser User-Agent
and no contact data. WebSearch was used 2 times. web.archive.org was not used.

## Power arithmetic (before returns, in HYPOTHESES)
Operation days a year: 120 in 2014-17, falling to 60 in 2024. That gives IS 617, VAL 201 and PRE 310 (FX only); HOLD
would have ~105.
- F1 LIVE: needs a per-day Sharpe of 0.29 (~16 bp net on USDJPY D1). That is unreachable.
- F1 DEMO: needs ~4.4 bp D1, about 4x the plausible size.
- F2a, F2b and F3 have 7-58 IS events each, so LIVE is impossible. F3 can't reach DEMO on its count (7 IS events would
  need a Sharpe of 0.76 per event).

## Results
Net is bp per trade. t is on the book's daily net, clustered by UTC day. PRE is Dukascopy mid, FX only. Random is the
share of 200 random-day seeds with a lower mean (same weekday, clock and horizon, own side). Power is the per-trade or
per-day Sharpe x sqrt(expected HOLD units) at the VAL size. Round-trip cost: FX ~1.2-1.5 bp (0.6 commission + spreads);
JP225 ~5 bp D1 and ~8.6 bp D3 including swap.

| hypothesis | PRE mid (t) | IS mid / net (t) | VAL net (t) | VAL/IS | random IS / VAL | Sharpe VAL, power | verdict |
|---|---|---|---|---|---|---|---|
| F1 OTC z, k 0 (every op day), D1, pool | +0.9 (0.30) | +0.5 / -2.0 (-0.75) | +3.3 (0.60) | n/a | 55 / 91 % | 0.45 | none |
| F1 OTC k 0.5 D3 EURJPY (largest \|t\|) | -19.2 (-2.20) | -14.4 / **-15.9 (-2.90)** | +14.6 (1.18) | sign flip | 1 / 90 % | 0.90 | none (wrong side in PRE and IS, flips in VAL) |
| F1 cut-off z, k 0, D3, pool | -2.4 (-0.52) | -7.7 / -11.7 (-2.37) | -10.8 (-1.24) | | 2 / 27 % | -1.34 | none (JP225 short loses the equity drift) |
| F1 best IS: cut-off k 1 D1 EURJPY | +11.9 (1.30) | +5.8 / +4.6 (1.11) | +2.7 (0.24) | 0.58 | 93 / 67 % | 0.18 | none |
| F1 super-long OTC k 0 D3 pool | +3.7 (0.49) | +8.2 / +4.1 (0.60) | +1.5 (0.16) | 0.37 | 95 / 73 % | 0.12 | none |
| F2a schedule change D1 USDJPY (11 IS events) | -43.2 (-2.00) | +6.9 / +5.8 (0.44) | +12.1 (0.70) | 2.1 | 71 / 67 % | 0.50 | none (PRE opposite) |
| F2a D3 pool | -36.2 (-1.61) | +28.9 / +24.6 (0.71) | +32.4 (0.86) | 1.3 | 88 / 90 % | 0.65 | none |
| F2b within-month amount change D1 USDJPY | +21.6 (1.64) | +3.4 / +1.9 (0.16) | -0.2 (-0.01) | <0 | 62 / 51 % | -0.01 | none |
| **F2b D1 EURJPY** (39 IS / 42 VAL days) | +25.9 (2.33) | +16.6 / **+15.4 (1.40)** | +24.9 (1.81) | 1.6 | 98 / 98 % | Sharpe 0.29, power 1.38 | none (IS t < 2; EUR leg, not JPY) |
| F2b D1 pool | +23.8 (2.16) | +4.2 / +1.4 (0.09) | +11.0 (0.83) | | 74 / 92 % | 0.63 | none |
| F3 YCC defence D1 USDJPY (7 IS / 19 VAL) | n/a | +32.9 / +31.9 (1.65) | +2.2 (0.16) | 0.07 | 97 / 42 % | 0.12 | none (count; decays) |
| F3 D1 JP225 | n/a | -7.5 / -15.0 (-0.26) | -67.6 (-2.37) | | 42 / 2 % | -2.47 | none, wrong sign |
| F3 D1 pool | n/a | +6.2 / +3.0 (0.12) | -27.6 (-1.76) | | 56 / 1 % | -2.22 | none |
| control: F3 D1 XAUUSD (long) | n/a | +93.5 / +91.6 (2.27) | -1.8 (-0.08) | | 100 / 60 % | | control beats candidates: the IS event days are dollar / risk days |

Notes on the table:
- **Fills:** spread x1.5 and +1 min change the FX cells by < 0.3 bp.
- **Without 2020-03/04:** no verdict changes. F2b EURJPY D1 IS becomes +14.5 (t 1.35).
- **F2b EURJPY D1 by year (net bp):** 2016 +7.7, 2017 -1.7, 2018 +67.3, 2019 +13.9, 2020 +17.3, 2021 +29.3, 2022
  +34.5, 2023 +19.0. 2024 has no within-month change.
- **F3 without the 2022-06-17 MPM-day announcement:** changes nothing (out/f23.txt).

## Cells tried and chance
- **Eligible cells:** F1 72 (OTC, cut-off and super-long OTC; k 0 / 0.5 / 1; D1 / D3; 3 symbols + pool), F2a 8, F2b 8,
  F3 8, for 96 in all. Another 24 XAU control cells and 8 F3 cells without 2022-06-17 were run for information.
- **Chance:** the max |N| of 96 has a median of 2.68 and a p95 of 3.47. 0 cells have IS t >= 2. 7 cells have
  IS t <= -2, all in F1 and all on the wrong side (EURJPY on OTC; JP225 on the cut-off). The F1 mean IS t is negative.
  The most negative cell is inside the chance range and flips sign in VAL.
- **C3 daily correlation (IS + VAL):** F2b EURJPY D1 -0.01 (-0.02 on signal days), F3 USDJPY D1 -0.04, F1
  super-long D3 pool +0.03, F2a D3 pool -0.01.

## What this says
- **Rinban results aren't news for FX or the Nikkei.** On operation days, ticks per minute at 03:00-03:20 UTC
  (~12:00 JST) and 04:50-05:20 UTC are 0.90-1.21x other weekdays. The ratio is flat across the minutes, with no spike at
  any of them (scripts/activity.py, activity only). The 1-3-day returns on the declared side are zero or negative in every era. Under QQE / YCC the BoJ
  bought whatever dealers offered within narrow spreads, so offer-to-cover mostly measures the amount offered and
  dealer inventory, not a yield shock that reaches the yen.
- **Schedule and amount changes** are the only part with sizeable moves (tens of bp). They are few (11 classifiable IS
  schedule changes, 39 within-month change days) and noisy.
  - Within-month changes give the same sign in PRE, IS and VAL for EURJPY only. USDJPY, the cleanest JPY channel, is
    flat. An EUR-only response points to something else on those days (the 2018 events average +67 bp), not BoJ supply.
- **YCC defence days** made the yen weaker the next day in IS (6 of 7 events). The 2022-23 run in VAL, which is
  mostly daily scheduled operations and CTD announcements, gives nothing. The gold control is larger in IS than any
  candidate, so the IS days are dollar or risk days rather than a BoJ-channel effect.

## Pitfalls for later rounds
- The BoJ monthly operation files change layout three times: 2016-12 (xlsx), 2017-03 (JGB section with the maturity
  label at the end), and 2019-05 (bilingual, marker column).
  - In the pre-2017 single table, the title continuation lines ("Outright Purchases of Corporate Bonds, ...") look
    like new section titles.
  - Fixed-rate rows have a blank "amount offered" (unlimited), and in 2022-23 they are labelled by issue
    ("10-year JGB #365 : 0.250%").
- Schedule PDFs:
  - The 2016-09..2020-02 outlines carry no amounts in their text.
  - Numbers in the extracted text are split ("4 5 0", "1 , 000"), and Japanese is CID hex.
  - The 2014-16 parse is only partial (some buckets are missing, and the units look inconsistent: the 2016-09 "-82 %"
    is a parse artefact).
  - A proper F2a needs a real PDF table parser, or the Japanese HTML pages if they exist.
- The www3.boj.or.jp daily pages stopped on 2025-10-03, and their old-year menus (`menuold_o_2024.htm`) return 404.
  The history of result release times was not found.

## Directions that need the user
| direction | value |
|---|---|
| Intraday JGB futures / 10Y yield or yen OIS ticks (paid: JPX / Refinitiv), to test whether rinban results move yields at all (the first link of the mechanism) | LIVE < 1 %, DEMO ~1 % |
| A paid or archived history of rinban result release times (would allow an entry at the release instead of 14:30 JST) | DEMO < 1 % (no activity footprint at 12:00 JST) |
| Manual reading of the 2016-20 schedule attachments (ranges per bucket) to grade F2a over the full IS | DEMO ~1 % |

## Scripts and outputs
In `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r42/J/`:
- **Fetching:** `scripts/fetch.py` (logged fetches), `pull.py` (monthly files), `pull_plans.py` (schedule PDFs).
- **Readers:** `xls.py` and `xlsx.py` (stdlib), `parse.py` -> `out/ops.json` (HOLD cut at parse), `pdftext.py`,
  `docs.py` (document dates and titles), `plans.py` -> `out/plans.json`.
- **Events:** `events.py` -> `out/events.json` (F1 day z, amount changes, fixed-rate runs).
- **Grading:** `lib.py` (prices with the HOLD cut, fills, costs, swap), `core.py` (trades, grading, random control);
  `f1.py` -> `out/f1.txt`, `f23.py` -> `out/f23.txt`, `f2a.py` -> `out/f2a.txt`.
- **Summary:** `summ.py` (chance benchmark, C3 correlation); `activity.py` (release-minute tick activity).
- **Downloads:** `web/mrel/` (monthly files), `web/mrel_x/` (extracted xls), `web/plans/` (PDFs), `web/probe/`; log in
  `web/requests.log`.
