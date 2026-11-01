# STREAM_W: Kalshi daily high-temperature brackets vs the exact settlement rule (round 63)

Written Sat Oct 31 17:20:51 UTC 2026 (from `date -u`). Rules declared in [HYPOTHESES_W.md](HYPOTHESES_W.md)
(16:11 UTC, before the bulk price pull; two data-logistics amendments before any P&L was computed).

## Answer: none (no LIVE, no DEMO)
All 7 declared cells lose money as a taker in both IS and VAL. Five of them have a significantly negative t. The
reason is one fact: **from 2021 to 2024 Kalshi weather books were very thin.** The median quoted spread was 10 c at
T-1 midnight, 36 c at 15:00 LST and 24 c at 17:00 LST, and only 28 % / 11 % of brackets had a two-sided quote at
15 / 17 LST. Three findings:
- The market already knows which brackets are dead. In 35,080 bracket-hours where the observed max made a bracket
  impossible, the YES bid was empty 99.94 % of the time. In the 20 bracket-hours that had a bid, 10 were cases where
  my METAR max was wrong vs the CLI, and the market bid 65-90 c on those: adverse selection.
- A climatology from hourly METAR loses to the market late in the day (rule a, t -6 to -10). The market sees the
  5-minute / 1-minute ASOS data and the NWS preliminary highs; the hourly METARs in ISD do not have them.
- The favourite-longshot bias exists **at the mid** (buying NO at mid on 10-20 c brackets: IS +2.9 c, t 2.07; VAL
  +3.9 c, t 3.02). But it is smaller than half the spread, so it is a market maker's edge, not a taker's.

The HOLD era was not opened.

## Data
- Kalshi keyless public API (`api.elections.kalshi.com`, which has no robots.txt; docs mark market data
  `security: []`). Pre-2025 history exists only through the archive endpoints: `/historical/markets?event_ticker=`
  and `/historical/markets/{ticker}/candlesticks` (hourly bid / ask / trade OHLC). Two things are missing: a series
  filter on the archive, and event-level or batch candles for archived markets. So the pull used 1 request per
  event plus 1 per bracket.
- The keyless limit is about 4 req/s (429 above that). Pull size: 12,255 requests, 440 of them 429 and retried with
  back-off; 115 MB. It ran 16:16-17:16 UTC, about 60 min, which is over the ~45 min guideline: the 2021-22 tail took
  the last 13 min.
- Every row is cut at `close_time` / candle end < 2025-01-01 at parse. The `KX*` successors were pulled only for
  2024-10-15..2024-12-30.
- **Subsample: odd ordinal dates only** (declared before the analysis). Sample: 1,837 city-days. NY 2021-08..2024-12
  (647), CHI 2021-10..2024-12 (592), AUS 2023-06..2024-12 (298), MIA 2023-06..2024-12 (300). In 2021-22 an event
  had 1-4 brackets; from 2023 it had 6.
- NOAA ISD full files from the public AWS bucket `noaa-isd-pds`, 2005-2024: 80 station-years for Central Park,
  Midway, Austin-Bergstrom and Miami Intl. Sources: METAR / SPECI temperatures, converted from tenths of °C to
  integer °F, and the SOD record's `24 HR MAX TEMP (F)`.
- Settlement check: the SOD max falls in the bracket Kalshi settled YES on 1,637 of 1,638 checkable city-days
  (99.94 %). The one miss is MIA 2024-11-27: SOD 81, settled ">= 84". Separately, MIA 2024-11-05 was settled from
  NWS hourly data because the CLI was not finalised (free text in `expiration_value`).
- Log: `research/data/kalshi_weather/requests.log`. Data: `research/data/kalshi_weather/{events,isd_raw}/`, plus
  `isd_<city>.npz`.

## Results: taker, fee ceil(0.07 C P (1-P)) at C = 10, P&L in cents per contract
t is clustered by date. "rand %" is the share of 300 same-timing random-bracket draws whose mean is below the rule.

| cell | IS n | IS net c | IS t | VAL n | VAL net c | VAL t | rand % IS / VAL | x1.5 IS / VAL | late IS / VAL | maker (mid, no fee) IS / VAL |
|---|---|---|---|---|---|---|---|---|---|---|
| a T15 θ0.05 | 586 | -3.18 | -2.89 | 424 | -2.81 | -1.93 | 100 / 100 | -6.8 / -7.5 | -5.6 / -5.2 | +5.5 (t 2.42, n 265) / +6.0 (t 1.99, n 189) |
| a T15 θ0.10 | 523 | -2.92 | -2.49 | 370 | -1.89 | -1.27 | 100 / 100 | -6.4 / -6.0 | -5.1 / -4.8 | +5.8 (t 2.43) / +6.3 (t 2.01) |
| a T17 θ0.05 | 635 | -5.80 | -9.12 | 487 | -5.13 | -6.55 | 91 / 96 | -8.4 / -7.3 | -5.7 / -4.8 | -3.1 / -4.3 |
| a T17 θ0.10 | 546 | -5.77 | -9.97 | 453 | -4.76 | -5.99 | 97 / 95 | -8.1 / -6.8 | -5.7 / -4.4 | -5.5 / -5.1 |
| b x 3c | 0 | - | - | 1 | -60.9 | - | - | - | - | - |
| b x 5c | 0 | - | - | 1 | -60.9 | - | - | - | - | - |
| c1 NO on 3-10c (T-1) | 339 | -3.00 | -2.33 | 385 | -1.65 | -1.85 | 93 / 99 | -6.0 / -5.4 | -3.3 / -1.9 | +0.2 (t 0.15) / +2.2 (t 2.49) |
| c2 NO on 10-20c (info) | 455 | -3.37 | -2.36 | 446 | -3.45 | -2.63 | 100 / 98 | -9.3 / -10.6 | -4.4 / -4.1 | +2.9 (t 2.07) / +3.9 (t 3.02) |

Per year (taker): every rule is negative in every year 2021-2024. Example: c1 runs -11.6 (n 6) in 2021, -1.1 in
2022, -3.8 in 2023 and -1.65 in 2024. a T17 θ0.05 runs -3.1, -2.3, -8.5 and -5.1.

- **Random benchmark.** The rules "beat" random brackets (91-100 %) only because random brackets pay even wider
  spreads (random mean -6 to -10 c). With a negative net, this does not count toward any bar.
- **Max-over-cells null.** It is moot: the best taker cell (c1 VAL -1.65 c) is negative.
- **Power at VAL size.** It is not defined, because the net is negative. On paper (HYPOTHESES), +2-3 c per contract
  would have given HOLD power > 3. The data show -2 to -6 c.
- **Maker variants are information only, as declared.** They assume a fill at the mid with no adverse selection
  and need a two-sided quote, which roughly halves n for rule (a). The a-T15 maker cell shows +5.5 / +6.0 c (t 2.4
  / 2.0), but a resting order placed at the mid at 15 LST gets filled when the market moves through it, which is
  exactly when the climatology is wrong (rule a at T17 is -3 to -5 c even at the mid). Do not read these numbers
  as an edge without a fill model.

## Why it failed
1. **Thin books and wide spreads (2021-24).** At 15 LST the median quoted spread on a 40-60 c bracket was 84 c.
   Taker edges of a few cents cannot pay that.
2. **Hourly METAR is not the information set.** The CLI max comes from continuous ASOS data. At 17 LST in summer,
   with the temperature still at its max, the final CLI max equals the hourly-METAR max only 17-30 % of the time
   (ISD 2010-21). The market has real-time 5-minute data (and the NWS preliminary highs Kalshi itself points
   traders to), so its late-day prices beat my model.
3. **Dead brackets are already priced dead.** There was nothing to arbitrage. The rare bids on brackets my rule
   called dead came from METAR-vs-CLI disagreements, and the market was right.
4. **Mechanism check.** The FLB at the mid is real: NO on 10-20 c brackets wins about 3-4 c over the mid in both
   eras. It is the edge a liquidity provider earns, and it needs maker fills, not taker trades.

## Pitfalls (for the next pass)
- The archive (`/historical/*`) has no series filter, and `/events?series_ticker=` returns nothing for archived
  events. Build tickers as `<SERIES>-YYMONDD`. The old series are `HIGHNY/HIGHCHI/HIGHAUS/HIGHMIA` until ~2024-10,
  then `KXHIGH*`. DEN, PHIL and HOU start 2024-12. There were no daily-low series before 2025.
- 2021-22 markets have `strike_type` null: parse `yes_sub_title` ("97° or higher" / "93° or lower" / "80° to
  81°"). `expiration_value` can be free text.
- Hourly candles exist only for hours with a quote or trade change, so carry the last close forward. An empty bid
  is 0, an empty ask is 1.
- In the SOD record, `24 HR MAX TEMP (F)` is a fixed 3-character field followed directly by text ("7724 HR MIN"),
  so a naive regex reads 7724.
- METAR max minus 1 °F > CLI max on ~0.1 % of days (ISD 2010-21). Use a margin of at least 1 °F for "dead" logic.
- The Kalshi fee formula used is the current one. The 2021-22 schedule may have differed; this does not change
  the verdict.

## What a user decision could unlock
1. **A maker-quote study** (not declared here, so it would be a new pre-registration). The candidates are the FLB
   at the mid (NO on 10-20 c) and quoting inside the 10-36 c spreads. It needs the archive trade prints
   (`/historical/trades?ticker=`, keyless) to model fills, so it is another ~1-2 h pull at 4 req/s. 2025-26 books
   are far tighter and full of bots, so the 2021-24 spreads will not repeat. The IDEAS_I warning applies: HOLD is
   contaminated by 2025-26 literature and practitioner bots.
2. **A forward log, the honest deciding test**, from 2026-11 on. Every 10 minutes from 09:00 to 23:59 local, log
   the book top (bid, ask, sizes) of every `KXHIGH*` bracket. Also log the 5-minute ASOS from the public NWS API
   and the CLI. Declared rule: taker (b) with a 1 °F margin, and maker (c2) quoting NO at the mid on 10-20 c
   brackets with a fill = a trade print through the quote.
   - Power: at ~20 cities x 30 days = 600 city-days a month, a per-city-day Sharpe of 0.12 reaches power 3 after
     ~1 month; 0.06 needs ~4 months.
   - Collection is keyless and read-only; trading is not possible from Vietnam (below).
3. **Venue: information only.** Kalshi's help centre says the exchange is available only to US residents and runs
   a waitlist for other countries ([help.kalshi.com, "Is Kalshi U.S. only?"](https://help.kalshi.com/faq/is-kalshi-u.s.-only)).
   The October 2025 "140 countries" announcement was web-only and inconsistent
   ([Sportico, 2025](https://www.sportico.com/business/sports-betting/2025/kalshi-international-countries-access-1234874388/)).
   No list I found names Vietnam. In practice a Vietnam resident cannot open a Kalshi account, and Vietnamese
   rules on offshore betting / derivatives add a second barrier. So even a passing rule would not be tradable by
   the owner.

## Files
- [HYPOTHESES_W.md](HYPOTHESES_W.md), this file, [results_W.json](results_W.json), [backtest_out.txt](backtest_out.txt),
  [margin.json](margin.json).
- Code: `code/fetch.py` (logged GET), `code/kalshi_pull.py` (archive puller, 4 req/s, odd dates, < 2025 cut),
  `code/jobs.txt`, `code/isd_pull.py`, `code/isd_parse.py`, `code/model.py` (ISD climatology), `code/backtest.py`
  (rules a/b/c, costs, random draws), `code/check_truth.py`, `code/diag_b.py`.
- No PREREG_DRAFT: no rule passed.
