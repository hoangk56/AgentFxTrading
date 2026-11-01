# Round 54 stream I: hypotheses (insider purchases on the firm itself -> the firm's Dukascopy / IC stock CFD)

Declared 2026-10-30 10:12 UTC (`date -u` at drafting start: Fri Oct 30 10:10:28 UTC 2026), after the Form 4 parse and
the event counts on a proxy universe, **before any stock price was loaded or any event was joined to a return**. Stream
D's price file did not exist yet when this was written. Bars: LIVE / DEMO from research/PROMPT.md (no RELAXED tier).
HOLD 2025-01-01..2026-09-24 closed: filings dated after 2024-12-31 are dropped at parse (asserted, 0 found), prices will
be cut at 2024-12-31 at load.

## Data
- SEC DERA Insider Transactions Data Sets, Form 4 only: round 44's 2014 Q1..2024 Q4 zips (read-only, on disk) plus
  **2013 Q1..Q4 fetched now** (4 zips, HTTP 200, 2026-10-30 10:08:18-10:08:23 UTC, robots.txt read first: `User-agent: *`
  only, no ClaudeBot entry, `/files/` allowed; generic research UA, no e-mail, >= 0.3 s spacing; log
  `.../scratchpad/r54/I/web/requests.log`). 2013 is needed so that 2016 filings can be classified with three prior years.
- Parse (`parse_owner.py`, python -I): non-derivative code P + A (open-market purchase) and S + D (open-market sale),
  shares > 0, 0 < price < 1e6; one row per (accession, reporting owner, code) with the earliest transaction date. 795,299
  owner-rows 2013-24. Owners kept: officers and directors (pure 10 % owners / "other" dropped, as in round 44).
- Universe: stream D's US stock CFDs with daily data before 2019 (D's `symbols.csv`, matched on CIK; the counts below use
  a ticker match on D's instrument metadata, 263 names with first daily candle < 2019, as a proxy).

## Classification (Cohen, Malloy & Pomorski 2012, JF 67(3), "Decoding inside information"), fixed now
- Per reporting owner (by owner CIK, across all issuers), per calendar year Y, look at the calendar months in which the
  owner made any open-market purchase or sale (transaction month; filing month if the transaction date is missing or
  implausible) in Y-1, Y-2 and Y-3.
- Classifiable = at least one trade in each of the three prior years. **Routine** = classifiable and there is a
  calendar month in which the owner traded in all three prior years. **Opportunistic** = classifiable and not routine.
  Everyone else is unclassified (the majority: most large-cap insider buyers are directors who buy once or twice).
- The classification of year Y applies to every purchase filed in Y (known on 1 January of Y: no look-ahead).

## Events (firm-days, filing date = Section 16 date)
- An event is (firm, filing date D) with at least one officer / director Form 4 reporting a code-P purchase.
- **Filing-date rule** (round 44): a Form 4 accepted by 22:00 ET is dated that day (Reg S-T 232.13), so a filing dated D
  is public by 22:00 ET on D. The data sets have no acceptance times. **Entry at the first regular-session open after
  D** (D's daily open, ask for a long), never on D itself.
- Families (side long in all, from the literature):
  - **ALL**: any officer / director purchase.
  - **OPP** (primary family): at least one opportunistic buyer that day.
  - **CEOCFO**: a purchase by an officer whose title names CEO / CFO / chief executive / chief financial, who is not
    routine (opportunistic or unclassified; requiring "opportunistic" would leave ~5 events a year).
  - **CLUSTER**: >= 2 distinct non-routine officer / director buyers of the same firm with filing dates within 7
    calendar days (~5 trading days); the event is the filing date that brings the count to 2; re-arms after 30 days.
  - Diagnostic only (not a counted cell, not selectable): ROUT = only routine buyers that day (CMP's placebo, expected ~0).
- No minimum dollar size (CMP use none). Median event value ~$250k, p10 $26k, p90 $2.6 M.

## Trade rule (fixed now)
- Long the firm at the open of the first trading day after D, exit at the open h trading days later, h in {1, 3, 5}
  (h 5 = 5 trading days, 7 calendar days over a weekend; the user's 5-day limit is read as 5 trading days, as in rounds
  37-53; stated in the write-up).
- One position per firm: a new event while that firm's position is open is skipped.
- **Unhedged** (U) and **hedged** (H): H shorts US500 (IC M1, same notional) at the same entry and exit minutes (the
  stock open timestamp, US500 M1 bar open, bid / ask). If D's stocklib provides a declared market hedge instead, the
  US500 leg is still the graded one; an equal-weight D-universe return is reported only as a diagnostic.
- Costs: stock leg from D's cost model (Dukascopy bid / ask at the open as the spread proxy, IC USD 0.02 per share per
  side, long financing at benchmark + 3 % a year per night, using D's benchmark series or 0 % in 2016-21 / the realised
  US policy rate in 2022-24 if D gives none). US500 leg: bid / ask at the M1 bar, financing on the short leg -0.5 bp per
  night (conservative assumption; IC's short-index swap is near zero to slightly positive in 2023-24).
- Variants reported for each graded cell: spread x1.5 on both legs; +1 day delay (entry the second open after D, exit
  h days after that); ex 2020-03/04 (99 of 236 ALL events in 2020 fall in March / April); by year.

## Cells and selection
- Counted cells: 4 families x 3 horizons x 2 hedge = **24**. Primary cell declared now: **OPP h5 H** (the paper's
  construction at the user's maximum hold). Cell selection on IS net t only; VAL checks the selected cell.
- Eras: IS 2016-21 (filing dates), VAL 2022-24. HOLD not touched.
- t: day-clustered (trades summed per entry date, t over dates), as in round 13.
- Random-entry control: for each event, the same entry / exit dates with a firm drawn at random from D's list among
  names with prices on those dates (not the event firm), same hedge and cost model; >= 500 seeds; report the share of
  seeds the cell beats (DEMO >= 90 %, LIVE >= 95 %).
- Chance benchmark: the same random-firm seeds recomputed for all 24 cells, max IS net t per seed -> the null
  distribution of the best-of-24; report P(max >= observed).
- C3 correlation (daily returns, `trades_C3_gotobi_jpy_basket.csv`) for any surviving cell.

## Counts (proxy universe, firm-days by filing year; no prices)
| year | ALL | OPP | ROUT (diag) | CEOCFO | CLUSTER |
|---|---|---|---|---|---|
| 2016 | 212 | 38 | 19 | 21 | 29 |
| 2017 | 194 | 25 | 16 | 24 | 27 |
| 2018 | 206 | 32 | 9 | 33 | 24 |
| 2019 | 268 | 52 | 8 | 37 | 34 |
| 2020 | 236 | 55 | 11 | 31 | 28 |
| 2021 | 136 | 23 | 8 | 16 | 16 |
| 2022 | 149 | 29 | 14 | 32 | 21 |
| 2023 | 166 | 28 | 11 | 35 | 22 |
| 2024 | 108 | 11 | 12 | 9 | 15 |
| IS / VAL / HOLD est. | 1,252 / 423 / ~245 | 225 / 68 / ~39 | - | 162 / 76 / ~44 | 158 / 58 / ~33 |
HOLD estimate = VAL rate x 1.73 years. Fewer trades after the one-position-per-firm rule (mostly at h5).

## Power arithmetic (before returns)
- Hedged daily idiosyncratic sd of a large US stock ~150-200 bp, so hedged sd ~180 bp at h1, ~310 bp at h3, ~400 bp at
  h5 (assumed; unhedged slightly higher).
- **LIVE** needs net per-trade Sharpe >= 3 / sqrt(HOLD n): OPP n ~39 -> 0.48 (~190 bp net at h5); CEOCFO / CLUSTER n
  ~33-44 -> 0.45-0.52 (~180-210 bp); ALL n ~245 -> 0.19 (~77 bp at h5, ~35 bp at h1). Plus t >= 2.5 IS and >= 1.5 VAL.
- **DEMO** needs IS net t >= 2: OPP n ~225 -> Sharpe 0.13 (~53 bp net at h5); CEOCFO / CLUSTER n ~160 -> 0.16 (~63 bp);
  ALL n ~1,250 -> 0.057 (~23 bp net at h5, ~10 bp at h1).
- Literature size (from memory, order of size): CMP 2012 report value-weighted abnormal returns of roughly +0.8 % a
  month for opportunistic purchases and ~0 for routine ones; the insider-purchase literature (Jeng, Metrick &
  Zeckhauser 2003; Lakonishok & Lee 2001) puts most of the excess return in small firms and spreads it over months, with
  a filing-date jump that our next-open entry partly misses. For large caps a 1-5 day hedged drift of ~10-50 bp after
  the filing is the generous end. Round-trip cost ~6-10 bp at h1 and ~15-25 bp at h5 (spread + commission + financing
  + hedge leg).
- So **LIVE is out of reach** for OPP / CEOCFO / CLUSTER (needs ~4x the generous literature size after cost) and for ALL
  (needs ~77 bp net at h5 on 245 trades). DEMO is reachable only for ALL at h5 (needs ~23 bp net, i.e. ~40-45 bp gross,
  the generous end) or for OPP at ~70 bp gross. Expected: no candidate; DEMO at best.
- Concurrent positions: ALL at h5 averages ~4 open positions (200 a year x 5 / 252) with peaks of tens in 2020-03; the
  rule needs a book of bots (one per 3 concurrent positions, or a cap on concurrency); counted in the write-up.

## Not tested here
- Holds > 5 days (where the CMP effect lives), small caps (not on Dukascopy / IC's list in 2016-18), sales (CMP find the
  routine / opportunistic split matters less for sales and the short side pays dividends and borrow).

## Addendum 1, 2026-10-30 10:23 UTC (before any return; after reading D's stocklib.py and symbols.csv header only)
- Stock leg costs and prices come from D's `stocklib.Stocks._leg` via `S.trade(..., entry_at="open", exit_at="open")`:
  split-adjusted mid +/- spread_mult x the Dukascopy half spread of the open candle, USD 0.02 per share per side on the
  raw price, financing (EFFR + 3 %) / 360 per calendar night (FRED DFF). This is the "D's benchmark" branch declared
  above. The default `open_spread="duka"` (the actual opening spread) is graded; the optimistic `"close"` spread is not.
- The hedge stays the declared IC US500 M1 leg (09:30 ET bar, my code). SPY from D's list is not used.
- Trades whose hold spans a D-flagged non-round > 40 % overnight jump (`jump`, likely bad print or spin-off) are dropped
  from every cell and control (data cleaning; the count is reported).
- Dukascopy daily data for these names starts 2017-01..2018-02 (`duka_first_daily`), so IS is effectively 2017-21 and
  IS counts are ~5/6 of the HYPOTHESES table. Universe = D's final `symbols.csv` with `is_etf == 0`, matched on CIK
  (issuer CIK of the Form 4); the random-firm pool is the same non-ETF list.

## Addendum 2, 2026-10-30 10:41 UTC (after the 24 open-to-open cells were graded; before any close-entry number)
The open-to-open cells lose ~80-100 bp a trade to the Dukascopy opening spread (D: median open spread 65 bp vs 7 bp at
the close), which no rule at the open can survive. A new, separately counted family is declared now, before its numbers:
- **Close entry (C)**: long at the close (ask) of the first trading day after the filing date D, exit at the close (bid)
  h trading days later, h in {1, 3, 5}; same four families (ALL, OPP, CEOCFO, CLUSTER), unhedged and hedged; hedge =
  short IC US500 at the 15:59 ET M1 bar close (bid / ask), same notional, -0.5 bp a night. D's cost model with the
  actual closing spread (default `open_spread="duka"` applied to the close candle). One position per firm. 24 more
  cells; **the chance benchmark is taken over all 48 cells** (max IS net t over open + close cells per seed).
- It misses the first day's open-to-close move by construction (the open cells' h1 mid of ~+25 bp may sit there).
- Same variants (spread x1.5, +1 day delay = entry at the second close after D, ex 2020-03/04, by year), random-firm
  control, bars unchanged. Primary close cell: OPP h5 H, as for the open family.
