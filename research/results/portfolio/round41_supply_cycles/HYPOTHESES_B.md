# Round 41 stream B hypotheses: US equity issuance supply from SEC EDGAR -> US500, USTEC, US2000 (US30 control)

Declared 2026-10-30 04:34 UTC (`date -u`: Fri Oct 30 04:33:57 UTC 2026), before any EDGAR row was joined to a
return. One probe file was fetched before writing this (2016 Q1 master.gz, to confirm the form codes exist); no
returns have been computed. Sides, horizons, parameters and the cell grid below are fixed; anything added later is
marked post hoc with its own time.

## Source
- SEC EDGAR quarterly full index, `https://www.sec.gov/Archives/edgar/full-index/<YYYY>/QTR<q>/master.gz`
  (pipe-delimited: CIK | Company Name | Form Type | Date Filed | Filename; same content as form.idx), quarters
  2015 Q1 .. 2024 Q4 only (40 files, ~4-6 MB each; 2015 is only needed for the trailing windows and the 180-day
  lock-up lag). No 2025+ index file is requested; rows with Date Filed > 2024-12-31 are dropped at parse.
- Only index files are requested (no filing documents, no `-index-headers`), so there is no acceptance time and no
  offering size. Timing rule used instead: a filing dated D was accepted no later than 22:00 ET on D (Reg S-T
  232.13: after 17:30 ET most forms take the next business day's date; the latest same-day cut-off of any form is
  22:00 ET). Every entry below is after 22:00 ET of D, so it uses only public filings.
- User-Agent: a generic research string with no name or e-mail; one host, sequential, >= 0.25 s between requests.
  If SEC answers 403 to that UA the stream stops and reports it (no workaround).
- PRE 2004-15: no US index price series exists in research/data before 2016 (Dukascopy h1 is FX + XAU only), so
  there is no PRE era for this stream. IS 2016-01..2021-12, VAL 2022-01..2024-12. HOLD closed (IC cut at
  ts < 1735689600000 at load; US2000 zbars files dated >= 20250101 are never opened).

## Mechanism and literature (side fixed from here)
- New equity supply must be absorbed by investors who sell other holdings or deploy cash to buy it; in an
  inelastic market (Gabaix & Koijen 2021, multiplier ~5) a supply shock should lower prices. At the aggregate level
  the evidence is slow: Baker & Wurgler 2000 (JF, equity share in new issues predicts lower annual market returns),
  Hirshleifer & Jiang 2010 (RFS, the UMO financing factor: issuers underperform repurchasers, monthly), Pontiff &
  Woodgate 2008 (share issuance, cross-section), Loughran & Ritter 1995 (issuer underperformance), Pastor & Veronesi
  2005 (IPO waves follow high market returns: a momentum confound). Stock-level short-run price pressure around
  SEOs: Corwin 2003 (JF), Altinkilic & Hansen 2003; around lock-up expiries Field & Hanka 2001 (JF, -1 to -3 % in the
  stock). Lou 2014 / issuance clustering is cited in the brief; I could not confirm a daily aggregate result there,
  so the daily-aggregate side is my extrapolation of the price-pressure mechanism, not a published daily estimate.
- Declared sides: equity supply (IPOs, shelf takedowns, secondary sales, lock-up expiries) -> **short** the index
  over the next 1-3 days; issuer buybacks (tender offers) -> **long**. These sides do not change after numbers.

## Expected size and power arithmetic (before building)
- Supply size: US IPO + follow-on proceeds 2016-21 ~ $200-400 bn a year, ~ $1-2 bn per trading day; a heavy day
  maybe $3-6 bn. US equity market cap ~ $30-50 trn, daily dollar volume ~ $400-600 bn. Inelastic-market estimate of
  a $5 bn supply surprise: 5 x 5 / 40,000 bn ~ 0.06 %, i.e. ~0.5-6 bp spread over the absorption days. A
  square-root impact model (sigma_day ~ 110 bp x sqrt(5 / 500)) gives ~11 bp as a generous upper bound.
- Counts (assumed before the pull, rechecked below from the index): trigger days z >= 1.0 ~ 16 % of days
  (~240 IS, ~120 VAL, ~70 HOLD per symbol), z >= 1.5 ~ 7 % (~105 IS, ~53 VAL, ~30 HOLD).
- LIVE needs HOLD power = per-trade net Sharpe x sqrt(HOLD trades) >= 3: per-trade Sharpe >= 0.36 at k = 1.0
  (~40 bp per 1-day US500 trade, sd ~110 bp) or >= 0.55 at k = 1.5. The three indices correlate ~0.9, so pooling
  them adds little. **LIVE is out of reach** by 1-2 orders of magnitude against the expected size.
- DEMO needs IS day-clustered t >= 2.0: per-trade Sharpe >= 2 / sqrt(240) = 0.13 (~14 bp on US500 h = 1, ~19 bp on
  US2000) at k = 1.0, or 0.20 (~22 bp) at k = 1.5. That is 2-20x the generous estimate: DEMO is possible only if
  the aggregate effect is much larger than price-pressure theory says. Expected verdict: none. The stream is a
  quick, cheap screen (budget < 1 h of pull).
- Costs (round trip, at the actual entry / exit minute): US500 / USTEC / US30 half spread at entry + half at exit
  from the M1 cache (bid c, ask ca), ~1-2 bp; US2000 (bid-only zbars) 0.34 pt per round trip (round 7 published
  spread), x1.5 variant 0.51 pt. Swap per 17:00 New York rollover from research/swing/rates.swap_frac_at (US2000
  uses US500's), Friday rollover x3. Commission 0.

## Signals (daily, by EDGAR Date Filed D; counted as distinct CIKs per day per group)
Name filter used by IPO / LOCKUP / SHELF groups (declared now, before counts): drop company names matching
`ACQUISITION|FUND|PORTFOLIO|ETF|ETN|TRUST|FUNDING|RECEIVABLES|MORTGAGE|LEASE|LEASING|BANK|FINANCE|CREDIT|SECURITIES|CAPITAL MARKETS`
(SPACs, closed-end / exchange-traded funds, ABS trusts and finance / bank issuers whose 424B filings are mostly debt).
- B1 IPO: forms 424B4 + 424B1 (original filings only), name filter.
- B2 SHELF: form 424B5 (shelf takedowns; includes some corporate debt that the name filter does not remove), name
  filter. 424B2 (bank structured notes, debt) and 424B3 (mergers, resale prospectuses) are excluded.
- B3 SECONDARY: form 424B7 (selling-shareholder shelf takedowns), no filter.
- B4 ALL-EQ: B1 + B2 + B3 counts.
- B5 BUYBACK: form SC TO-I (issuer tender offers; originals, not /A), no filter -> **long**. 8-K item 8.01 buyback
  authorisations need the filing text (not in the index; ~70k 8-Ks a year): dropped as not cheap.
- B6 LOCKUP (scheduled by-product): for every B1 filing on D, a lock-up expiry on L = D + 180 calendar days rolled
  to the next US trading day; count per L. Known >= 6 months ahead.
- Standardisation (trailing only): y = log(1 + count). m_D = mean of y on the same weekday over the previous 12
  weeks; r = y - m; s_D = sd of r over the previous 60 business days (floor 0.25). z_D = (y_D - m_D) / s_D.
  Trigger day: z_D >= k.

## Trades
- Entry clocks: E1 = first US trading day after D (for B6: on L itself) at the 09:31 ET bar (fill at that minute's
  close: bid c / ask ca); E2 = the same day at 04:00 ET (04:00 bar close). Exit at the same clock h US trading days
  later. +1 minute variant: both legs one bar later. Spread x1.5 variant.
- Sides: B1-B4, B6 short; B5 long.
- Parameters (chosen on IS, best-of-N reported): k in {1.0, 1.5}; h in {1, 3} trading days (h = 3 keeps <= 3
  overlapping positions per symbol bot).
- Symbols: US500, USTEC, US2000 (cells); US30 control, reported but not counted.
- Cells: 6 signals x 2 k x 2 h x 2 entries x 3 symbols = **144 cells**.

## Statistics and controls
- Net and mid bp per trade, t clustered by entry day; for h = 3 also a Newey-West (lag 3) t on the trade series;
  the smaller |t| is the one graded. By year; with and without 2020-03/04.
- Random-entry control: >= 200 seeds, same count, side, clock, hold and weekday mix, random US trading days in the
  same era.
- Best-of-N null: 200 circular shifts (offset >= 20 trading days) of every signal series inside the era, all cells
  recomputed, max signed t in the declared direction.
- Mechanism diagnostic (not a cell): OLS slope of next-day (E1 h = 1) US500 mid return on z_D for B4, with and
  without the prior 5-day return as a control (Pastor-Veronesi momentum confound).
- Bars: LIVE / DEMO as research/PROMPT.md. A cell meeting DEMO or LIVE numbers on IS + VAL gets a
  PREREG_DRAFT_B_*.md; HOLD is not opened.

## If the first construction fails (declared now)
Related scheduled-supply by-products available from the same index, with the same machinery and sides (short on
supply): (a) S-1 / F-1 + EFFECT notices as the IPO pipeline known days ahead (count of EFFECT on S-1/F-1 files),
(b) settlement-day version of B1-B4 (entry at the 09:31 ET open of the offering's settlement day = D + 2 trading
days from 2017-09-05, D + 3 before; hold 1 day), (c) supply by week (sum of B4 over the week -> short the next week
Monday-to-Wednesday). Each adds 2 h x 3 symbols x 1 entry (E1) x k = 1.0 only = 6 cells per by-product.

## Addendum 1: parse corrections and event counts (before any return; written 2026-10-30 04:38 UTC per `date -u`)
- Pull: 40 quarterly master.gz files 2015 Q1..2024 Q4, all HTTP 200 with the generic UA, 26 s in total; 0 rows
  dated after 2024-12-31 (none requested).
- Correction 1 (data, not returns): the index lists a co-registrant filing once per CIK with the CIK in the path,
  so "distinct CIKs" counted guarantor subsidiaries (one 424B5 on 2016-06-30 had 646 rows). Counts are now distinct
  accession numbers per day.
- Correction 2 (data, not returns): SC TO-I filers are ~75 % closed-end / interval funds and BDCs (2019: 352 of
  465 rows match the name filter), so B5 BUYBACK now uses the same name filter. What is left (~110 a year, many
  BDCs) is a weak proxy for issuer buybacks; expected uninformative.
- Mean filings per trading day (IS / VAL): IPO 2.02 / 1.61, SHELF 9.82 / 9.09, SEC 0.75 / 0.79, BUY 0.43 / 0.43,
  ALL-EQ 12.6 / 11.5, LOCKUP 1.87 / 1.80. Yearly IPO-group filings 281 (2016) .. 951 (2021), 309 (2022).
- Trigger days per symbol, k = 1.0 (IS / VAL / HOLD at the VAL rate): IPO 271 / 140 / 81, SHELF 211 / 114 / 66,
  SEC 280 / 140 / 81, BUY 300 / 157 / 91, ALL-EQ 202 / 116 / 67, LOCKUP 221 / 90 / 52. k = 1.5: IPO 115 / 47 / 27,
  SHELF 51 / 35 / 20, SEC 140 / 72 / 42, BUY 132 / 87 / 50, ALL-EQ 53 / 33 / 19, LOCKUP 114 / 60 / 35.
- Power with these counts: LIVE needs per-trade net Sharpe >= 3 / sqrt(HOLD n) = 0.31-0.37 at k = 1.0 and
  0.42-0.69 at k = 1.5 (~35-75 bp on a 1-day US500 trade); DEMO needs IS Sharpe >= 2 / sqrt(IS n) = 0.12-0.14
  (k = 1.0) or 0.17-0.28 (k = 1.5). Unchanged conclusion: LIVE impossible at any plausible size, DEMO only if the
  effect is ~10x the price-pressure estimate.

## Addendum 2: by-products run after the first construction failed (written 2026-10-30 04:40 UTC per `date -u`, before their returns)
The 144 main cells are graded (no cell meets DEMO: the two cells with IS t >= 2 and VAL > 0 beat only 76 % of
random entries). Running the three declared by-products, with these exact readings of the declaration:
- (a) IPO pipeline: an EFFECT notice on day D from a CIK that filed an S-1 / F-1 (name filter) in the previous 365
  days and has no IPO-group (424B4 / 424B1) filing before D. Count per trading day, z as above, k = 1.0, short at E1
  of the next trading day, h in {1, 3}; US500, USTEC, US2000 (6 cells).
- (b) settlement day: B4 ALL-EQ trigger days (k = 1.0) shifted to the settlement day: entry at E1 on trading day
  D + 2 (D >= 2017-09-05) or D + 3 (before), short, h in {1, 3} (6 cells). "B1-B4" in the declaration is read as
  the B4 composite, which is what keeps it at 6 cells.
- (c) weekly supply: S_w = sum of B4 counts over Monday-Friday of week w; z of log(1 + S_w) vs the previous 12 weeks
  (sd floor 0.25), k = 1.0; short at E1 on the first trading day of week w + 1, h in {1, 3} (6 cells).
- Same costs, controls and grading. Family total after the by-products: 144 + 18 = 162 cells.
