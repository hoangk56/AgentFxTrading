# Hypotheses, stream H (round 65): Bithumb KRW listings, K2's rule frozen

Written 2026-11-01 10:40 UTC (`date -u` printed 10:40:17). Nothing about event returns, pumps or listing dates
has been computed yet. Pulled so far, only to read the API: Bithumb robots.txt (404, no file), `/v1/market/all`
(502 markets, 489 KRW), and 9 probe candle requests. HOLD (2025-01-01..) is never requested, loaded or counted.

## Mechanism
K2's mechanism: Korean retail chases a new KRW listing; the pump starts at the announcement (before trading opens)
and is partly priced on global venues. Arbitrage and the end of the retail rush pull the coin back over ~3 days.
Bithumb is Korea's second venue (roughly 20-40 % of Korean spot volume 2020-24). It lists more often and announces
the same way (notice, then trading opens a few hours later). If the mechanism is about Korean retail attention, not
about Upbit itself, the same short-the-alt / long-BTC trade should earn on Bithumb listings. A pass on
**Bithumb-only** events (no Upbit listing of the coin within 7 days) would be the new, independent evidence.

## Data
- Bithumb public API (no key): `/v1/market/all` (current markets only), `/v1/candles/months|days|minutes/60`.
  The `to` parameter is read as KST (checked: `to=2021-06-01T00:00:00` returns up to the 14:00 UTC hour), so all
  requests use `to=2025-01-01T08:59:59` (= 2024-12-31 23:59:59 UTC) or earlier; every series is cut at
  ts < 2025-01-01 at load. A `Z` suffix is rejected (400).
- Event L for a coin: first month candle -> first day candle in that month -> first 60-minute candle that day.
- Binance: local perp_1d (perp first daily kline), local funding files; 1m fills via fapi through k2rule.px.
  Pre-entry run-up from the same fapi 1m bars.
- Upbit (stream K, read-only): k2_events.csv and data/upbit/pull_m240.out + m240/ first candles, for the overlap.

## Universe and event definition (frozen, as K2)
- Coin = Bithumb KRW code mapped to a Binance USDT-M perp: `<COIN>USDT`, else `1000<COIN>USDT`,
  `1000000<COIN>USDT`, `1M<COIN>USDT` (Binance's scaled contracts). No other mapping.
- Event: L = start of the coin's first Bithumb KRW 60-minute candle, with the perp's first daily kline <= L - 7 d.
  One event per coin. Eras by entry time: IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31, only L < 2024-12-28.
- Guards, declared now, applied before looking at any event's return:
  1. Name collision: drop if (Bithumb coin/BTC in KRW) / (Binance perp/BTC) at the first Bithumb day close is
     outside [1/3, 3] (after the 1000x scale). Upbit's BTT case is the example.
  2. Rename / token swap, not a listing: drop if the coin was already trading on Bithumb KRW under an old code
     (e.g. RNDR -> RENDER, MATIC -> POL, LEND -> AAVE). Flagged when a Binance perp of an old ticker of the same
     project exists, or a search shows a migration; at most a few WebSearches, only on flagged events, decided on
     dates and names only.
- Delisted Bithumb markets: probed by requesting candles for Binance perp coins absent from the current list. If
  they return "Code not found", delisted markets are invisible (survivorship, as with Upbit: probably against the
  short, since faded listings that were later delisted are missing).

## Rule (frozen; no grid, one cell)
`k2rule.trade(sym, L)` unchanged (copied to H/code/k2rule.py; only the log folder changed): short alt perp / long
BTCUSDT perp at the close of the 1m bar starting at L + 1 h (fallback up to 4 later minutes), exit at entry + 72 h,
cost 42 bp, funding at real stamps. Declared siblings for robustness only (they choose nothing): costs x1.5
(cost 0.0063), entry L + 1 h 5 min and L + 2 h, and H24 for reference.
Statistic: mean net bp/trade, t clustered by entry day (k2rule.clt), per-year means, SR per trade.

## Random benchmark (as K2, gross on 1h closes from local 1h perp files; 500 draws)
(a) other universe alts (Bithumb-mapped perps older than 30 d) shorted vs BTC at the same hour; (b) the same coin at
random hours 30-180 d after L (before the cut). Percentile = share of draws whose era mean is below the events'.

## Splits reported
- Overlap with Upbit: "joint" = Upbit's first KRW candle of the coin within +-7 d of the Bithumb L (sub-split
  Bithumb-first / Upbit-first); "Bithumb-only" = the rest (Upbit listed > 7 d earlier, later, or never; Upbit's
  list is current-only, so a delisted Upbit market looks like "never").
- The Bithumb-only result is the independent test. Joint events mostly duplicate K2 trades.
- Pump before entry: alt vs BTC from L - 24 h to entry (Upbit K2: +21.5 %).

## Expected events and power arithmetic
- Expected: Bithumb listed many more coins than Upbit in 2020-24. Of those, only coins with a Binance perp >= 7 d
  old count. Guess 60-120 events (IS 15-35, VAL 45-85), about half joint with Upbit in VAL (Upbit listed many of the
  same coins in 2023-24).
- Bars (unchanged). DEMO: IS t >= 2.0, VAL net > 0, random >= 90 %, positive at costs x1.5 and one step late.
  LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, random >= 95 %, HOLD power >= 3.
- Power = SR per trade (VAL) x sqrt(n_HOLD), n_HOLD = VAL pace per year x 1.83. At K2's VAL SR 0.25, LIVE needs
  n_HOLD >= 144, i.e. ~79 events a year. A Bithumb pace of 25 a year gives n_HOLD ~46 and power ~1.7 at SR 0.25;
  pooled with Upbit's ~10 a year (disjoint events only) ~2.0. So LIVE is out of reach unless the VAL SR per trade
  is >= ~0.45; the realistic aim is DEMO, plus whether Bithumb-only events show the same sign (mechanism check).
- Failure modes expected: Bithumb listings are less "special" (it lists more often, smaller coins), so the pump and
  the fade may be smaller; Bithumb-only events may be coins Upbit already listed (no new retail rush).
