# Round 71 stream FS: crash-wick fade on Binance SPOT coins without a USDT-M perp, hypotheses

Written 2026-11-01 17:52 UTC (from `date -u`), before any price, volume or return of this stream was read. At this
time only robots.txt of data.binance.vision (404) and the data.binance.vision index page (HTML shell) had been
fetched; the S3 listing host answered 403 to robots.txt and is not used again (403 = stop). HOLD is never requested:
every request ends at 2024-12-31 23:59:59 UTC (monthly files <= 2024-12, daily files <= 2024-12-31) and every series
is cut at ts < 2025-01-01 at load. F's coord/ folder and research/data/binance_1m_wicks_hold/ are never opened.

## Disclosure: the same mechanism failed HOLD on perps
Round 64 F faded >= 5 % idiosyncratic 1-minute wicks on top-40 USDT-M perps (T5 idio H60, enter at the close of
e+1). It passed every LIVE bar on IS / VAL (IS +273 bp t 4.05, VAL +271 bp t 3.76) and **failed its registered HOLD**
(per the round 66 F0 report: +42 bp, t 1.17, n 2,080). Round 66 F0 (entry at the first trade after the event bar's
close) is a forward-only registration because F's HOLD is known. This stream tests the same fade on a disjoint event
set (spot coins with no USDT-M perp at the time) whose HOLD has never been opened. The prior that a passing IS / VAL
result here survives HOLD is therefore low: F showed that a ~+270 bp IS / VAL edge on this design can shrink to ~+40
bp out of sample. A pass here is a candidate for one HOLD test, not evidence on its own.

## Mechanism and side (fixed now)
A thin spot book hit by a large market sell (stop-loss cascade, an isolated / cross margin liquidation on Binance spot
margin, or one holder dumping) prints a 1-minute close below what information justifies; the book refills over
minutes to an hour and liquidity providers who buy the overshoot earn it (Nagel 2012; Grossman-Miller). Without a
perp there is no perp liquidation engine and no perp-spot arbitrage to refill the book quickly, so the overshoot may
be larger and slower, or (if there is no forced flow at all) it may be informed selling that does not revert.
**Side: long only after a crash** (spot cannot be shorted without borrow; no spike shorts).

## Data
- Spot symbol list: data-api.binance.vision `/api/v3/exchangeInfo` (all statuses, quote USDT), robots.txt read and
  logged first (round 64 X / V used this host; api.binance.com robots.txt is Disallow: /). Delisted pairs absent from
  exchangeInfo cannot be listed (the S3 listing is closed): survivorship is reported (count of known delisted
  perp-named spot pairs found vs missing).
- Daily quote volume (universe only): data-api.binance.vision `/api/v3/klines` 1d, startTime 2019-11-01, endTime
  2024-12-31 23:59:59.999, <= 2 requests per symbol; if a symbol has no API klines, data.binance.vision spot monthly
  1d files for the months it is needed. Only the quote-volume and trade-count columns are used for the universe.
- Perp listing days: research/data/binance/perp_1d (886 USDT-M perps incl. delisted), first kline day per coin, read
  only. Coin mapping perp -> spot base: strip a leading 1000000 / 1000 / 1M; LUNA2 -> LUNA.
- 1m klines: data.binance.vision spot monthly 1m (`data/spot/monthly/klines/<SYM>/1m/`) for every symbol-month in
  the universe on any day (plus BTCUSDT every month 2020-01..2024-12), compact npz (minute, o h l c, quote volume,
  trades) under research/data/spot_wicks/npz/, zips deleted. If the projected pull exceeds ~45 min, an addendum
  (written before any 1m file is opened) declares the subsample: complete months in a fixed seeded order.
- aggTrades: data.binance.vision spot daily aggTrades for event symbol-days only, streamed and kept only inside the
  windows [close_e - 2 min, close_e + 63 min] (rows: time, price, qty, is_buyer_maker) as F0 did; npz under
  research/data/spot_wicks/agg/. Same 45-min rule (declared seeded IS / VAL interleaved order).
- All requests: >= 0.3 s between request starts (global), back off on 418 / 429 / 503, 403 = stop, logged in
  research/data/spot_wicks/requests.log (UTC time, URL, status, bytes). Downloads parsed under `python -I`.

## Universe (each UTC day d, 2020-01-01..2024-12-31)
- Spot pairs <BASE>USDT. Excluded bases: stablecoins / fiat / gold (USDC BUSD TUSD USDP PAX DAI UST USTC FDUSD SUSD
  USDS USDSB EUR GBP AUD TRY BRL AEUR EURI XUSD USD1 PAXG XAUT, plus round 60 EXCL_BASE), leveraged tokens (base ends
  in DOWN / BULL / BEAR, or ends in UP and base[:-2] + "DOWN" is also a listed base).
- Excluded: any coin with a USDT-M perp whose first daily kline is on or before day d (stricter than "before": a perp
  listed on day d also excludes d), whether or not the perp was later delisted.
- Rank by mean daily quote volume over d-30..d-1 (all 30 days must have a spot daily kline, i.e. listed >= 30 days and
  trading on d-1). **Top 40 among the eligible pairs** (the eligible set is ranked; perp coins are not counted).

## Event (bar e, minutes since 2020-01-01; consecutive bars e-1 and e both present)
- r_e = c_e / c_{e-1} - 1 <= -X, X in {5 %, 8 %}; coin in the universe on e's UTC day.
- Idiosyncratic: |r_BTCUSDT spot, e| <= 0.2 |r_e| (BTC bar present).
- Bar e has >= 10 trades and quote volume > 0.
- Bad-print guard (F's, moved to the entry trade): p0 = price of the first aggTrade with time >= close_e (= open time
  of e+1) must be <= c_{e-1} (1 + r_e / 2) (still beyond half-way). Events with no aggTrade data are dropped and
  counted; events with no trade within 60 s after close_e are dropped (not tradable at once) and counted.
- De-duplication per cell threshold: after an accepted event, the same coin's events in bars e+1..e+60 are ignored.

## Trade
- **Entry (cell rule):** buy at p0, the first spot aggTrade >= close_e.
- **Declared check (one step late):** buy at the close of bar e+1 (kline), same event, same exit.
- **Exit:** close of bar e+1+H (H60: e+61; H15: e+16). A missing exit bar uses the last close within 5 minutes
  before it, else the trade is dropped.
- Gross = exit / entry - 1. No funding (spot), no borrow.

## Costs (declared)
- Spot taker fee 10 bp a side (20 bp round trip).
- Entry half-spread hs_in, measured per event from aggTrades: (buyer-taker VWAP - seller-taker VWAP) / their mean / 2
  over trades in [entry time, +1 s); if either side has no trade there, widen to +10 s, then +60 s; if still missing,
  50 bp. Floored at 0.
- Exit half-spread hs_out: the same measure over [open of bar e+2+H, +10 s), widened to +60 s, else 25 bp; floored at 0.
- Net = gross - 20 bp - hs_in - hs_out. Robustness: all costs x 1.5; the one-step-late entry (its hs_in measured at
  [close_{e+1}, +1 s) with the same widening).
- Reported (not in the net): the median USD notional traded in the entry second, the median measured hs_in.

## Cells (4, all declared now)
X in {5 %, 8 %} x H in {15, 60}. The selected cell is the best day-clustered IS t; VAL is checked unchanged; all 4
are reported with years, x1.5, late, random %.

## Statistics and bars
- IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31; t clustered by entry UTC day; years 2020..2024.
- Random benchmark (per cell, 200 replications), as F restricted to the long side: for each event, a random minute of
  the same coin, same era, in the universe on that day, with a negative 1m return (fading it = long), in the same
  decile of the trailing-1,440-minute sd of 1m returns (>= 1,000 valid minutes; deciles per coin-era over the pool;
  missing sd -> top decile). Random entry = open of the next bar (the first trade after the random minute's close),
  exit = close of bar +1+H, cost = the event's measured cost. Random % = share of replications whose mean net is below
  the real mean net. Max-over-4-cells null: per replication the max IS t over the 4 random cells.
- Pitfall checks: IS without 2020-03-12..13 and without 2021-05-19; VAL without the LUNA (2022-05) and FTX (2022-11)
  months; drop top-3 coins; drop top-5 days; share of events on days with >= 5 events; new listings (< 90 days).
- Bars (BRIEF): LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive (4 of 5), >= 95 % random, HOLD power at VAL
  size >= 3, net > 0 at x1.5 and one step late; DEMO t >= 2.0 IS, net > 0 VAL, >= 90 % random. A pass writes
  PREREG_DRAFT_FS_<name>.md and stops; HOLD is never opened here.

## Power arithmetic (before data)
- HOLD 2025-01..2026-10 is ~22 months against VAL's 36: n_H ~ 0.61 n_VAL **if the event rate holds**. It may not:
  in 2025-26 Binance lists a USDT-M perp for almost every new spot coin within days, so the no-perp universe in HOLD
  is likely thinner and smaller than in 2020-22. I report the VAL rate by year (2022 / 2023 / 2024) as the HOLD guide
  and use the 2024 rate if it is below the VAL mean.
- Power = S x sqrt(n_H), S = net mean / sd per trade at VAL size; needed S >= 3 / sqrt(n_H):
  n_H = 150 -> S >= 0.245; 300 -> 0.173; 600 -> 0.122.
- F's per-trade S at T5 idio H60 was 0.16-0.22 with per-trade sd ~1,200-1,700 bp. Unless the no-perp event rate is
  >= ~500 per VAL (>= ~300 in HOLD) with S >= 0.17, LIVE power is out of reach; the 8 % cells (fewer events) can
  reach LIVE power only with S >= ~0.25. Day clustering lowers it further (F: 3.53 per trade vs 2.93 clustered), so
  I report both.

## Addendum 1 (2026-11-01 18:01 UTC, before any 1m file or price was read)
- Symbol list: data-api exchangeInfo has 775 USDT spot pairs (519 TRADING, 256 BREAK); old delisted pairs are
  present (ERD, BCHABC, NPXS, SRM, KEEP, BTT...), so survivorship from the list is small. 700 pass the base filters,
  697 had no perp before 2020-01-02. Daily klines (quote volume and trade count kept, prices discarded at parse):
  464 symbols have 2019-11..2024 data; 233 return none (listed 2025-26); 2 symbols with non-ASCII names (2025 listings)
  failed to encode and are irrelevant to 2020-24. 999 requests, 0 x 403 / 418 / 429 on data-api.
- Universe: 40 pairs every day (329 distinct symbols; distinct per year 139 / 175 / 178 / 182 / 130 for 2020..2024);
  median trailing-30-day quote volume of the 40th pair $0.5 M / day in 2020, $13 M in 2021, $4.9 M in 2022,
  $1.6 M in 2023, $2.4 M in 2024. Pull list: 3,813 symbol-months (incl. BTCUSDT x 60).
- 1m pull order and subsample (declared now): BTCUSDT months first, then odd calendar months (Jan, Mar, ...) of all
  years, then even months, symbol order within a month alphabetical; budget 45 min wall. If the budget ends first, only
  complete months (every pull-list symbol of the month present or 404) are used and the dropped months are listed.
- The aggTrades pull (budget 45 min) runs over all candidates (before guard / de-duplication) in a seed-7171 IS / VAL
  interleaved random order; if it does not finish, the events not reached are missing at random and are counted.
