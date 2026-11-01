# Round 42 stream J hypotheses: BoJ JGB purchase operations (rinban) -> USDJPY, EURJPY, JP225 (XAUUSD control)

Declared 2026-10-30 05:08 UTC (`date -u`), before any operation or schedule datum was joined to a price return.
Rules: round 37 BRIEF (costs, fills, random control, day-clustered t, bars) and round 42 BRIEF stream J row.
HOLD 2025-01-01..2026-09-24 stays closed: IC M1 cut at ts < 1735689600000 at load; BoJ rows with offer date after
2024-12-31 dropped at parse (asserted); no BoJ file for a period after 2024-12 was requested except the schedule index
page (whose post-2024 rows are not parsed).

## Sources (probed 04:54-05:05 UTC; no robots.txt on www.boj.or.jp / www3.boj.or.jp (404); >= 1.3 s spacing)
- BoJ "Market Operations by the Bank of Japan (Monthly)", one file per month:
  https://www.boj.or.jp/en/statistics/boj/fm/ope/m_release/YYYY/opeYYMM.{zip,xlsx}. ZIP(.xls) 2013-06..2016-11, xlsx
  2016-12..2024-12, PDF only before 2013-06 (not used). 139 files, 2013-06-03..2024-12-25. Per operation: offer date,
  maturity bucket, amount offered (planned, public at the offer), competitive bids, successful bids, cut-off ("pro-rata
  or non-pro-rata") yield spread, average yield spread, pro-rata ratio. Fixed-rate (unlimited) operations are flagged.
- BoJ schedule / outline releases (monthly 2014-21, quarterly 2021-24, "Revised", "Addition to the Auction
  Schedule", "Announcement on the Conduct of Fixed-Rate Purchase Operations..."): list on
  https://www.boj.or.jp/en/mopo/measures/mkt_ope/ope_f/index.htm, PDFs under /en/mopo/mpmdeci/mpr_YYYY/ (167 files
  2013-24 being pulled; text extracted with a stdlib inflate).
- Operation timetable https://www.boj.or.jp/en/mopo/measures/mkt_ope/opetime.htm: competitive JGB purchases today:
  offer 10:10 JST, bid cut-off 11:40, results ~12:00 JST; fixed-rate: offer 10:10 or 14:00 JST, results ~15:50.
  I could not confirm the historical result time for 2013-24 (one web search). **Entry clocks are therefore set
  conservatively after any plausible release time** (below). Monthly schedule releases: 17:00 JST on the last business
  day (2017 press coverage); used with entry 17:30 JST.

## Counts (from the parsed data, no returns) and power arithmetic
Conventional competitive operations (buckets 0-1, 1-3, 1-5, 3-5, 5-10, 10-, 10-25, 25-; inflation-indexed, floating
and fixed-rate excluded): operation days per year 2013(Jun-) 70, 2014-17 120, 2018 116, 2019 92, 2020 101, 2021 68,
2022 70, 2023 71, 2024 60. IS (2016-21) 617 op days, VAL (2022-24) 201, PRE (2013-06..2015-12, FX only) 310.
HOLD would hold ~1.73 y x ~60 = ~105 op days.
- F1 (daily offer-to-cover signal): LIVE needs per-day net Sharpe >= 3 / sqrt(105) = 0.29, i.e. ~16 bp net per USDJPY
  D1 trade (sd ~55 bp): not reachable at any literature size (rinban flow effects on JGB yields are fractions of a bp;
  USDJPY's beta to JGB yields was near zero under YCC 2016-22). DEMO needs IS t >= 2 on ~617 days: per-day Sharpe 0.08,
  ~4.4 bp D1 / ~7.6 bp D3 on USDJPY. Expected effect <= 1 bp: DEMO reachable only at ~4x the plausible size.
- F2a (schedule changes): count after the PDFs are parsed (expected ~10-25 changes in IS); DEMO needs per-event Sharpe
  ~0.4-0.6 (30-50 bp on a D3 USDJPY trade): only the largest surprise cuts (2018-01-09 type) are that big.
  LIVE impossible (HOLD has ~5-10 schedule releases with a change).
- F2b (within-month offer-amount changes, no new schedule in between): 2016-21 58 changed ops (39 cuts, 19 raises),
  ~40 days; VAL 2022-24 ~104 ops (2022-23 YCC). DEMO needs IS per-day Sharpe ~0.32 (~17 bp D1 USDJPY). LIVE impossible.
- F3 (YCC defence): IS events ~7 (first-in-run fixed-rate days 2016-11-17, 2017-02-03, 2017-07-07, 2018-02-02,
  2018-07-23 plus 2020-03-16 / 2020-04-23 additions), VAL ~15. Neither bar is reachable on IS (t >= 2 on 7 events needs
  Sharpe 0.76 per event); reported descriptively.

## Common mechanics
- Symbols: USDJPY, EURJPY, JP225 (IC M1, 2016-24); XAUUSD as a control (never eligible). PRE 2013-06..2015-12:
  Dukascopy USDJPY, EURJPY bid (mid), cost = IC 2016-17 cost of the cell + 0.6 bp.
- Fills at the close of the M1 bar starting at the clock (signal data are public before it); costs = half spread at
  entry and exit + 0.6 bp FX / metals commission; swap (research/swing/rates.py swap_frac_at) on rollovers; variants
  spread x1.5 and both legs +1 min. Holds <= 120 h. Day-clustered t on the book's daily net (trades split at UTC
  midnights). Results also without 2020-03/04.
- Business-day exits: "+n" = the n-th weekday after the entry date at the same UTC clock (FX trades on JP holidays).
- Random control: 200 seeds; each trade moved to a random weekday of the same era with the same weekday, clock,
  horizon and its own side (for F1, side was fixed by the op-day Z; a sign-flip-by-day permutation null shared by the
  three symbols is the second control). Multiple testing: best |t| vs the max of K normals.
- C3 correlation: daily net of any surviving cell vs research/results/portfolio/trades_C3_gotobi_jpy_basket.csv
  (IS + VAL).

## F1: offer-to-cover / cut-off surprise (results release -> 1-3 days)
- Mechanism: a high offer-to-cover (bids / amount offered) or a high cut-off yield spread means dealers are eager to
  sell JGBs to the BoJ (inventory heavy, demand weak): upward yield pressure, which the market sees only at the results.
  Side (brief, fixed): high -> JPY up (short USDJPY, short EURJPY), JP225 down (short); low -> the reverse.
- Signals per op: OTC z = (ln(bids/offered) - mean of the previous 20 ops in the same bucket) / their sd (>= 10 prior ops
  required; the 2013-06.. window seeds 2016); CUT z = same on the cut-off yield spread (level, bp). Day value Z = mean of
  the op z over the day's conventional competitive ops. Super-long variant SL: Z from 10-25 / 25- / 10- ops only (OTC).
- Rule: Z >= k -> JPY-up side; Z <= -k -> JPY-down side; k in {0, 0.5, 1.0} (k chosen on IS).
- Clock: entry 05:30 UTC (14:30 JST) on the offer day (after the ~12:00 release; conservative, see Sources);
  exits D1 = +1 weekday 05:30 UTC, D3 = +3 weekdays 05:30 UTC.
- Cells: (OTC, CUT, SL) x k(3) x h(2) x {USDJPY, EURJPY, JP225, pool of the three} = 72; XAUUSD control (side: long XAU
  on the JPY-up side) 18 more, not eligible.

## F2a: schedule changes (monthly / quarterly plan releases, 17:00 JST)
- Event: each schedule / outline release (dated by its file name, 2014-24). Classification from the PDF text only: the
  planned amount per operation per bucket (midpoint of a range) times the planned number of operations per month, summed
  over conventional buckets, new document vs the previous document in force. Δ < -2 % = cut, Δ > +2 % = raise, else no
  trade. If the text cannot be parsed for a document, that document is dropped (logged), never classified from later
  operation results.
- Side: cut -> JPY up (short USDJPY, short EURJPY), JP225 short; raise -> the reverse.
- Clock: entry 08:30 UTC (17:30 JST) on the release date; exits D1 and D3 (weekdays, 08:30 UTC).
- Cells: h(2) x {USDJPY, EURJPY, JP225, pool} = 8 (+ XAU control 2).

## F2b: within-month offer-amount changes revealed at the offer (10:10 JST)
- Event: a conventional competitive op whose amount offered differs by >= 5 % from the previous op in the same bucket,
  with no schedule release (F2a list) dated between the two ops. Day sign = sign of the summed change (100 million yen)
  over the day's changed buckets.
- Side: cut -> JPY up / JP225 short; raise -> the reverse.
- Clock: entry 01:20 UTC (10:20 JST, after the 10:10 offer notice; after the Tokyo fix); exits D1, D3 (01:20 UTC).
- Cells: h(2) x {USDJPY, EURJPY, JP225, pool} = 8 (+ XAU 2).

## F3: YCC defence / unlimited fixed-rate operations and unscheduled additions
- Events: (a) first fixed-rate op day after >= 14 calendar days without one (from the monthly data; entry 06:00 UTC =
  15:00 JST, after the 10:10 / 14:00 JST offers); (b) release dates of "Announcement on the Conduct of Fixed-Rate
  Purchase Operations...", "Addition to the Auction Schedule...", "Additional Auction Schedule", "Change in the Auction
  Schedule", "Market Operations for 10-year JGBs ..." documents (entry 08:30 UTC = 17:30 JST, conservative, since some
  were released with the 17:00 schedules). Same-date (a)/(b) collapse to (a). Excluded: MPM decision-day documents
  ("Increase in the Amounts ...", "Statement on Fixed-Rate Purchase Operations ...", "Market Operation Measures following
  the Monetary Policy Decision"); 2022-06-17 (CTD announcement on an MPM day) reported with and without.
- Side: BoJ caps yields -> JPY down (long USDJPY, long EURJPY), JP225 long.
- Exits D1, D3. Cells: h(2) x {USDJPY, EURJPY, JP225, pool} = 8 (+ XAU 2). Descriptive (no bar reachable on IS count).

Total eligible cells: 96 (F1 72, F2a 8, F2b 8, F3 8); controls 24.

## Amendment 1 (05:14 UTC from `date -u`, before any F2a return; F1 was graded at 05:09-05:10 UTC, F2b and F3 at 05:11 UTC)
F2a parse, mechanical: the PDF text gives the planned amount per auction (range midpoint) for some buckets only, and
the frequency only in some 2020-24 documents. Δ is computed over the buckets parsed in both the new document and the
previous parsed document, as amount x frequency where both state a frequency, else amount per auction. Documents with
no parsed bucket are dropped: that removes all 2016-09..2020-02 outlines (amounts not in their text) and some 2014-15
and 2022-23 documents, so F2a has ~25-30 classified releases in total, about half in IS. Same-date duplicate releases
are merged. The classification never uses operation results. Also noted: F3 random controls use the first clock of the
cell (06:00 UTC) for all of its events.
