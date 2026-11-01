# Round 54 stream E hypotheses: blackout selling (H-STK) and large-cap post-earnings drift

Declared 2026-10-30 10:09:25 UTC (file written; `date -u` read at 10:08:45), before any stock or index return was loaded. Same LIVE /
DEMO bars as research/PROMPT.md (no RELAXED). HOLD 2025-01-01..2026-09-24 stays closed: every series is cut at
2024-12-31 at load (IC ts < 1735689600000; Dukascopy files 2016-2024 only, from stream D), EDGAR facts filed after
2024-12-31 and 8-Ks dated after 2024-12-31 are dropped at parse, under python -I.

## Universe rule
- Firms in stream D's `symbols.csv` (Dukascopy US stock CFDs with daily data before 2019) that have a CIK, at least
  one 8-K item 2.02 with an acceptance time, and an XBRL stock-compensation fact. Data from each firm's first
  Dukascopy day (2016-01 at the earliest; most from 2017-01..2018-02). IS = first data..2021-12-31, VAL = 2022-24.
- A firm-day is usable only if D's file has bid and ask open / close for days -1..+6 around it and D has not
  flagged a split in that span (split-flagged events are dropped, not repaired).

## Events (earnings releases)
- Source: 8-K filings with item 2.02 (round 47 B `ea_8k202.csv` for its 333 CIKs; submissions JSON for D's firms
  that are missing), acceptance time in UTC converted to US/Eastern.
- Pre-announcement filter (round 47 A1): the release counts only if it is the first 8-K 2.02 that comes 10-100
  days after the firm's latest fiscal period end (period ends from the firm's XBRL 10-Q / 10-K facts). One event per
  firm per fiscal quarter.
- Day 0 = the first session whose 09:30 ET open is after the acceptance time (release before 09:30 -> that day;
  after 09:30 -> next session). Sessions = days on which D has a candle for the stock and IC US500 has 09:30-16:00 bars.

## Stock-compensation measure (as filed)
- SBC_q = the firm's quarterly `us-gaap:ShareBasedCompensation` (cash-flow add-back). Fallback when the firm has no
  ShareBasedCompensation fact for that quarter: `us-gaap:AllocatedShareBasedCompensationExpense`. Facts are YTD in
  10-Qs: quarter = duration 80-100 days if filed, else YTD minus the prior YTD with the same start, and Q4 = FY minus
  the 9-month YTD.
- Taken from the **latest fiscal quarter whose fact was filed strictly before day 0** (normally the quarter before
  the one being announced; no look-ahead).
- Market cap = `dei:EntityCommonStockSharesOutstanding` of the latest cover page filed before day 0, times the
  stock's Dukascopy close (bid) on that cover page's filing date (shares and price at the same date, so an
  unadjusted price series cannot mix pre- and post-split units). Sanity check against D's split flags.
- Signal S = SBC_q / market cap. Rank: percentile of S among all universe firms with a valid S as of day -1 (each
  firm's latest filed value; cross-section on the same date, no future information). Top quintile = pct >= 0.80,
  top decile = pct >= 0.90; the paper's top 5 % (>= 0.95) is reported, not counted.

## H1 (H-STK): short high stock compensation after the blackout lifts (Hartzmark & Solomon 2022, NBER WP 30688)
- Mechanism: employees' vested shares cannot be sold during the pre-earnings blackout; the trading window opens
  ~1 day after the release and employees sell, a predictable price pressure proportional to stock compensation.
  Paper: top 5 % stock-expense firms, days t+1..t+3, -87.5 bp (t -5.77); t0..t+3 -116.5 bp (t -5.50); 2002-20,
  all US firms (small caps included); not in the AER 2025 version.
- Side: **short** (fixed by the mechanism). Hedge: **long US500 1:1 dollar** (IC M1 bid / ask at 09:30 / 16:00 ET);
  USTEC as the declared alternative hedge.
- Entry: short at the **open of day 1** (the first open after the day-0 session, ~1 day after the release, when the
  blackout lifts), exit at the close of day h.
- Counted cells (10): {top quintile, top decile} x exit close of day {1, 3, 5} with US500 hedge (6); entry at the open
  of day 0, exit close of day 3 (paper's t0..t+3), quintile and decile (2); USTEC hedge, day 1 open -> day 3 close,
  quintile and decile (2). Primary: top quintile, day 1 open -> day 3 close, US500 hedge.
- Reported, not counted: the top 5 %; the mechanism contrast top quintile minus bottom quintile on the same dates;
  +1 day delay (entry open of day 2); spread x1.5; ex-2020-03/04; by year; random-entry control (200 draws: same
  entry dates, random firms from D's list with a usable firm-day, same hedge and costs).
- Expected size in IC's list (large caps only): 20-60 bp, i.e. under the paper's 87.5 bp all-firm top 5 %.

## H2 (PEAD at 1-5 days for large caps)
- Reaction: R_oc = day-0 open-to-close stock return minus US500's 09:30-16:00 return (the brief's measure);
  secondary R_ear = day -1 close to day-0 close minus US500 (standard announcement return). Each scaled by the
  firm's trailing 60-session sd of daily abnormal close-to-close returns (days -61..-2), z = R / sd.
- Selection: z >= IS 80th percentile of z (all IS events) -> follow long; z <= IS 20th percentile -> follow short.
  Thresholds from the IS signal distribution only.
- Side: **follow (continuation)**, the PEAD direction (Bernard & Thomas 1989; Chordia, Goyal, Sadka, Sadka &
  Shivakumar 2009 find the large-cap drift weak). Declared alternative: **reverse** (Milian 2015, "Unexpected
  earnings and returns": the drift reverses in heavily traded / optionable stocks after ~2000; Martineau 2022 finds
  PEAD gone for large caps). Both sides are counted.
- Entry at the close of day 0 (bid / ask of the close), exit at the close of day h, h in {1, 3, 5}. Hedge: opposite
  US500 position 1:1 dollar.
- Counted cells (12): {R_oc, R_ear} x h {1, 3, 5} x side {follow, reverse}. Primary: R_oc, h = 3, follow.
- Reported: +1 day delay (entry close of day 1), spread x1.5, ex-2020-03/04, by year, random control (same dates,
  random firms, the same long / short mix).

## Costs (from stream D's cost model; declared form)
- Stock leg: Dukascopy bid / ask at the entry and exit quote (short sells the bid, covers the ask) as the IC spread
  proxy; IC commission USD 0.02 per share per side (bp = 2 / price in cents, i.e. 0.02 / price per side); financing
  per night held: long pays (benchmark + 3 %) / 360, short receives (benchmark - 3 %) / 360 (negative when
  benchmark < 3 %); benchmark = US fed funds (effective) by month, or D's stocklib value if it differs (then D's).
  Dividends are a wash in the CFD (adjusted both sides), so return is price only and ex-dividend drops are added back
  if D gives dividends; else noted as a short-side bias (shorts gain the drop, ~1-3 bp a trade for these firms).
- Hedge leg: IC US500 / USTEC M1 bid / ask at the bars, index swap -2 bp a night long (rounds 42 / 44).
- If D's stocklib.py defines the cost model differently, D's version is used and the difference is stated.

## Statistics
- Net bp per trade (stock leg + hedge leg), t day-clustered by entry day; per-trade Sharpe; power = net Sharpe x
  sqrt(expected HOLD trades) at the VAL size.
- Chance benchmark: per-entry-day sign flip shared by all cells of a family, 1,000 draws, 95 % quantile of the max IS
  net t over the counted cells (H1 10, H2 12, pooled 22).

## Power arithmetic (before returns)
Assume ~220 firms x 4 releases = ~880 events a year (fewer after the filters, ~700), IS ~4.5 years of data per firm,
HOLD 1.73 years, hedged 3-day sd ~350 bp (large caps, after earnings; high-SBC firms are tech, higher vol).

| cell | events / yr | IS n | HOLD n | LIVE: Sharpe needed (net bp at sd 350) | DEMO: IS t 2 needs Sharpe (net bp) |
|---|---|---|---|---|---|
| H1 top quintile, 3 d | ~140-175 | ~700 | ~260 | 0.19 (65 bp) | 0.076 (27 bp) |
| H1 top decile, 3 d | ~70-90 | ~350 | ~130 | 0.26 (92 bp) | 0.11 (37 bp) |
| H1 top 5 % (reported) | ~35-45 | ~175 | ~65 | 0.37 (130 bp) | 0.15 (53 bp) |
| H2 quintile tails, 3 d | ~280-350 | ~1,400 | ~520 | 0.13 (46 bp) | 0.053 (19 bp) |

Cost ~8-15 bp a round trip (both legs). LIVE for H1 needs the paper's full top-5 % effect (~90 bp) on a whole
quintile of large caps: unlikely (expect LIVE ~5 %). DEMO is reachable if large caps carry about a third of the
paper's effect. H2: the literature's large-cap drift at 1-5 days is a few bp, so LIVE is out from the count and DEMO
needs ~20 bp net: unlikely. Concurrent positions: H1 top quintile ~150 events a year in ~24 earnings-season weeks,
~6 a week with a 3-day hold, so ~4 open at a time, peaks ~10: one bot per stock (or ~4 bots at 3 positions each);
counted on the events before returns.

## Addendum A1 (2026-10-30T10:18:31Z), before any return
Seen before any return: stream D's partial symbols.csv gives a median Dukascopy spread at the **open of 60-100 bp**
(close 8-16 bp) for the first names. An open entry is then mostly a cost question. HS 2022's t+1..t+3 is a sum of
CRSP daily close-to-close returns, i.e. close of day 0 to close of day 3, so a close entry is the paper's own window.
- Added and counted (6): H1 short {top quintile, top decile} from the **close of day 0** to the close of day
  {1, 3, 5}, US500 hedge at 16:00. H1 is now 16 counted cells, the pooled grid 28. The declared primary stays the
  open-of-day-1 cell; the close-entry d3 cell is reported next to it.
- Implementation detail fixed now: the stock leg uses stream D's stocklib (`_leg`: entry / exit at the Dukascopy
  bid / ask of that open or close, split-adjusted prices, commission on the raw price, financing from FRED DFF + / -
  3 %); the hedge leg stays the declared IC US500 / USTEC (09:30 / 16:00 ET M1 bid / ask, -2 bp a night long,
  -0.5 bp short). Market cap uses raw (unadjusted) close bid at the share-count filing date. ETFs are excluded from
  the universe and the random pool. Events whose hold spans a D jump flag are dropped.
- Dividends are not in the data: a short gains the ex-date drop (bias in H1's favour of ~0.5-2 bp a 3-day trade
  for these low-yield firms), the long US500 hedge loses ~1.5 bp; stated, not corrected.

## Addendum A2 (2026-10-30T10:39:56Z), before any return
D's READY (10:39 UTC) says the Dukascopy open spread is the day's first quote (median 65 bp) and offers
`open_spread="close"` (the close spread charged at the open) as the optimistic bound. Every open-entry / open-exit
cell also reports net with that bound ("optb"), as a cost sensitivity: not a new cell, the verdict uses the declared
Dukascopy open spread. IS is effectively 2017-21 (data from 2016-09-26, most names from 2017-01..2017-11).
