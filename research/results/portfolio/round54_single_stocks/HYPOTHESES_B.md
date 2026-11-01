# Round 54 stream B hypotheses: firm-level buyback windows on single-stock CFDs

Declared 2026-10-30 10:08:33 UTC (`date -u`), **before any price file was opened or any return computed**. Stream D's
price files did not exist yet at this time (`.../r54/D/out/` had no READY). Bars: LIVE / DEMO of research/PROMPT.md (no
RELAXED tier). HOLD 2025-01-01..2026-09-24 stays closed: stock and US500 series are cut at load (< 2025-01-01, asserted);
round 47's XBRL facts and 8-K files were already cut at parse (filed <= 2024-12-31). No change to this file after
numbers, except dated addenda declared before their own numbers.

## Mechanism and prior evidence
Round 47 B found no buyback bid at the index level: the dollar-weighted open share is 94 % week-of-quarter calendar,
and index returns are dominated by the earnings-season drift. At the index, the bid of one firm is diluted by ~500
others. At the firm, it is not: a top-quintile buyer retires ~4-8 % of its market cap a year, ~1-2 % a quarter, executed
over ~40-45 open trading days. That is ~3-4 bp of market cap a day, ~3-6 % of its daily volume (ADV ~0.7-1 % of market
cap for large caps), and corporate desks front-load the first days after the window reopens. A square-root impact
model (impact ~ 0.5-1 x daily sd x sqrt(Q / V), daily sd ~150 bp, Q / V ~0.05) gives ~15-35 bp of temporary pressure, of
which a persistent share of ~1/3 gives an **expected excess return of ~5-15 bp over the first 3-5 days after the
reopening**, against the market, and the mirror (bid withdrawn at the blackout start) of the same order with the
opposite sign. Expected size is at or below the round-trip cost (below), so a DEMO pass would be a surprise.

## Universe (fixed now)
- Firms: stream D's US stock CFD list (`symbols.csv`, CIK via SEC company_tickers.json) **intersected** with round 47's
  universe entities (top-200 Vanguard 13F issuers of each year 2016-24, `r47/B/out/universe.csv`), since only those have
  filed repurchase facts. Membership in year Y as in round 47 (Vanguard year-end Y-1 rank). Multi-CIK entities keep
  round 47's max-of-CIKs run-rate. A firm-day needs D's bid and ask open / close on every day of the hold.
- Firms in D's list outside that intersection are used only in the same-date cross-section benchmark and the random
  control (both need no buyback data).

## Firm ranking: buyback yield as filed (no look-ahead)
- RR_i(t): round 47's quarterly run-rate (TTM repurchases / 4, `PaymentsForRepurchaseOfCommonStock`, fallback
  `...OfEquity`; a fact counts on day t only if filed before t; 0 if the latest period end is > 200 days old).
- Market cap proxy MV_i(Y): the firm's Vanguard 13F value at year-end Y-1 (the same file that sets membership; 13F
  values are proportional to market cap up to Vanguard's ownership share, ~6-9 % for most large caps, lower for
  dual-class / founder-held firms). No share-count download is made. BY_i(t) = 4 x RR_i(t) / MV_i(Y).
- Rank on each event date t among all universe-intersection firms in D's list on t (RR = 0 firms included):
  **Q5 = BY_i(t) >= the cross-sectional 0.8 quantile on t** (primary); **D10 = >= 0.9 quantile** (variant). Q1-3 =
  BY <= the 0.6 quantile (the low / no-buyback comparison group for the mechanism contrast).

## Window rule (round 47 W14 with addendum A1, unchanged)
- Release session s: the first 8-K item 2.02 accepted >= 10 and <= 70 calendar days after the period end E (E = the
  latest fiscal period end before it); session = acceptance day if accepted before 09:30 ET on a trading day, else the
  next trading day; fallback the first 10-Q / 10-K filing for E (<= E + 100 days).
- **Reopening day r = s + 2 trading days** (two full trading days after the release session). Known at the open of r
  (the release is public on s).
- **Blackout start c** = the first trading day on or after E + 3 months - 14 calendar days (two weeks before the next
  projected fiscal quarter end), if the window was open on c - 1. Known in advance from E.

## Trades (side fixed now)
- **H1 reopen, long (primary family):** buy firm i at the **open of r** (Dukascopy ask at the day's open), sell at the
  **close of r + h - 1** (bid at the close), h in {1, 3, 5} trading days.
- **H2 blackout start, short (the mirror, alternative):** short firm i at the open of c (bid), cover at the close of
  c + h - 1 (ask), h in {1, 3, 5}.
- Firms: Q5 (primary) and D10.
- **Hedge (both declared, both counted):**
  - **XS (same-date cross-section, the confound fix):** the firm's return minus the equal-weighted mid return of every
    stock in D's list with data over exactly the same open -> close span. This holds the date fixed, so the
    week-of-quarter / earnings-season drift that dominated round 47 cancels. Cost = the stock leg only (the basket is a
    benchmark, not a traded leg).
  - **US500 (tradable):** the opposite US500 trade, beta 1, IC US500 at 09:31 ET entry and 15:59 ET exit of the same
    days (IC bid / ask at those bars, IC swap -2 bp per calendar night for a long, the short leg gets 0), stock leg
    cost as below.
- Cells: 2 sides x 2 quantiles x 3 horizons x 2 hedges = **24 counted cells**. **Primary cell: H1 Q5 h = 3, US500
  hedge.** Primary mechanism cell: H1 Q5 h = 3, XS.
- **Declared mechanism contrast (information, not a trade):** XS excess of Q5 reopeners minus XS excess of Q1-3
  reopeners, h = 1 / 3 / 5, both groups reopening on the same date or the same calendar week (date-week fixed effect:
  per-week mean difference, weeks with both groups). Both groups are 2 days after their own release, so post-earnings
  drift common to all reopeners cancels too.

## Costs (stream D's model; declared shape now, D's numbers used as delivered)
- Commission USD 0.02 per share per side (IC MT5), i.e. 200 / price bp per side.
- Spread: Dukascopy bid / ask at the actual open and close (half spread each leg, by construction of bid / ask fills).
- Financing: long pays benchmark + 3 % a year per calendar night held; short receives benchmark - 3 % (D's benchmark
  series; if D gives none, benchmark = 0 for both, i.e. long -3 %, short -3 % a year: conservative for the short).
  h = 1 is intraday (no night).
- Dividends: IC credits longs / debits shorts; Dukascopy CFD prices drop on ex-days. Used as D delivers them (if D's
  prices are not dividend-adjusted, ex-days inside a hold bias long cells down and short cells up by the dividend; the
  share of trades with an ex-day inside is reported).
- Split days flagged by D are excluded from any hold that spans them.
- Stress: spread x1.5 (stock and US500), and **+1 day delay**: entry at the open of r + 1 (c + 1), same h.

## Grading
- Eras: **IS 2016-21 (from first data)**, **VAL 2022-24**. Net bp per trade; t **clustered by entry date** (the mean of
  the trades entering on the same date is one observation; plain t across dates), as D's stocklib provides.
- ex-2020-03/04, by year, years > 0.
- **Random-entry control:** 200 draws; each event keeps its entry date, horizon and side, the firm is replaced by a
  random firm from D's list with data on those days; same costs and hedge. Share of draws whose mean net is beaten.
- **Chance benchmark:** 1,000 draws of a per-entry-date sign flip shared by all 24 cells, applied to the gross hedged
  return before costs; 95 % quantile of the max IS net t over cells.
- Power at HOLD size: per-trade net Sharpe (VAL) x sqrt(HOLD n), HOLD n = VAL events / 3 x 1.73.
- Bots / concurrent positions: max and 95 % quantile of open positions over days, for the cell as defined, and the number
  of distinct firms traded (one bot per stock gives <= 1 position a bot; the US500 hedge needs one bot per concurrent
  hedge leg or a netted hedge).
- C3 correlation (daily P&L vs `research/results/portfolio/trades_C3_gotobi_jpy_basket.csv`) only for a surviving cell.

## Power arithmetic (before returns)
Counts are estimates until D's list is known: the top-200 x D list intersection is assumed ~140-170 firms, so Q5 ~30
firms x 4 reopenings = **~120 events a year** (D10 ~60); IS from Dukascopy's first US stock data (2017-01..2018-02 per
round 25 A) gives ~4.5-5 years ~ **550-600 IS events**, VAL ~360, **HOLD ~207** (D10 ~104). Event clustering (most
reopenings fall in weeks 3-7 of the quarter) cuts effective n for the date-clustered t, by an assumed ~1.5x.
Hedged per-trade sd (stock minus US500): h1 ~130 bp, h3 ~230 bp, h5 ~300 bp. Round-trip cost: commission ~2.6 bp at
USD 150 + spread ~3-6 bp + US500 leg ~1 bp + financing ~1.4 bp a night: **h1 ~7-10 bp, h3 ~10-14 bp, h5 ~13-18 bp**.

| cell | HOLD n | LIVE Sharpe (power 3) | LIVE net needed | IS n (eff.) | DEMO Sharpe (IS t 2) | DEMO net needed |
|---|---|---|---|---|---|---|
| Q5 h1 | ~207 | 0.21 | ~27 bp | ~580 (~390) | 0.10 | ~13 bp |
| Q5 h3 | ~207 | 0.21 | ~48 bp | ~580 (~390) | 0.10 | ~23 bp |
| Q5 h5 | ~207 | 0.21 | ~63 bp | ~580 (~390) | 0.10 | ~30 bp |
| D10 h3 | ~104 | 0.29 | ~67 bp | ~290 (~195) | 0.14 | ~33 bp |

Against an expected ~5-15 bp gross (~0 net), **LIVE is out of reach by the count in every cell before any return**;
DEMO needs ~2-3x the expected gross size. A pass would be checked against the random-firm control and the XS / Q1-3
mechanism contrast before anything else.

## Addendum B1, 2026-10-30 10:37:04 UTC (before any return; only stream D's stocklib.py source and symbols.csv / splits.csv headers read, no price loaded)
- The stock leg is computed with stream D's `stocklib.trade` (entry long at ask / exit at bid, commission USD 0.02 per
  share per side on the raw price, financing per calendar night long (EFFR + 3 %) / 360, short (3 % - EFFR) / 360, EFFR
  = FRED DFF on the entry date). This is the declared cost shape with D's benchmark. Dividends are not in D's prices.
- Trades whose hold spans a D "jump" flag (non-round > 40 % overnight move) are excluded; split days are adjusted by D.
- The XS benchmark is the equal-weighted mid return of D's non-ETF names with quotes on the entry and exit day.
- The random-firm control draws from D's non-ETF names (stocklib.random_control pool), same dates / side / hedge.
- **Information row, not counted:** Dukascopy's opening quotes are much wider than at the close (D's symbols.csv has
  median open spreads several times the close spreads). For the two primary cells only, the net with
  `open_spread='close'` (every fill pays that day's closing spread: optimistic) is reported beside the declared net.
  The declared (open-candle) spread stays the grading cost.
