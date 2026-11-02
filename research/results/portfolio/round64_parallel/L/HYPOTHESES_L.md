# Stream L (round 64): Coinbase listing fade, a replication of K2 on another venue

Written 2026-11-01 10:01 UTC (`date -u`), before any Coinbase candle was requested and before any return was computed.
HOLD (2025-01-01..) is never requested, loaded or counted: every Coinbase request ends 2024-12-31 23:59:59 UTC and
every series is cut at ts < 2025-01-01 at load.

## Mechanism
A Coinbase Exchange listing opens a coin to US retail (Coinbase app users see it once trading opens; the "Coinbase
effect"). Attention buying overshoots on every venue, including the Binance perp, and fades once the new demand is
met. Same mechanism as K2 (Upbit KRW listing), different retail venue. Side fixed: short the Binance alt perp,
long BTCUSDT perp, equal USD notional. Known risk: the round 60 squeeze tail (a just-listed alt can run +100 % more)
and Coinbase announces "inbound transfers" before trading opens, so much of the pump precedes the entry.

## Event (declared now)
- Coinbase Exchange products from `GET /products` with quote USD (`<COIN>-USD`). L = start of the first 1h candle
  of `<COIN>-USD` (found with daily candles, then one 1h request on the first day). The first candle is the first
  trade, i.e. the start of limit-only / full trading (the post-only phase prints no trades).
- Coin must have a Binance USDT-M perp (map: `<COIN>USDT`, or `1000<COIN>USDT`; name collisions guarded: a Binance
  perp whose price differs from the Coinbase USD close at L + 1 h by more than a factor 2 after the 1000x scale is
  dropped, as K dropped BTT).
- **Main set (K2 frozen filter): perp's first daily kline >= 7 days before L.** Secondary set (the brief's wording):
  perp >= 1 day before L (adds the events with a 1-6 day old perp); reported separately, not used to choose anything.
- One event per coin. Coins whose `<COIN>-USD` history starts before 2019-12-20 (before BTC perp 1m data) are not
  events. Exclude stablecoins / wrapped / fiat (USDT, USDC, DAI, PAX, BUSD, GUSD, WBTC, CBETH...).
- Robustness (not a cell): drop events where another quote product of the same base (BTC, USDT, USDC, EUR, GBP)
  printed a candle >= 1 day before L (then L is not the listing).
- Survivorship: `/products` may omit delisted products (to be checked: if it lists `status: delisted`, they are
  used). Missing delisted listings are probably coins that faded, so the bias runs against the short (conservative),
  as for K2.

## Trade (frozen from K2: K/PREREG_DRAFT_K_upbit_listing_fade.md, K/code/k2.py sha256 f671e399...)
- Short alt perp, long BTCUSDT perp at the close of the 1m bar starting at L + 1 h (fill at L + 61 min).
- Exit at the close of the 1m bar starting at entry + 72 h (main) or + 24 h (declared sibling, as K reported).
- Costs 42 bp (4 taker x 5 bp + 2 x 10 bp alt half-spread + 2 x 1 bp BTC), funding of both legs at the real stamps.
- Checks: costs x1.5, entry L + 1 h + 5 min, entry L + 2 h. K2's `trade()`, `btc_px`, `fsum` and `fills.price_at`
  are imported unchanged; only the fetch / cache paths are mine (research/data/coinbase/).
- Grid: 2 cells (H24, H72), the hold was chosen by K on Upbit IS (H72); I keep H72 as the primary, no new choice.
  No parameter is chosen on Coinbase data.

## Statistics
Net bp per trade, t clustered by entry day (k2/kdata `cl_t`). Eras IS 2020-01..2021-12, VAL 2022-01..2024-12. Years
positive. Random benchmark as K2 (gross on 1h closes, 500 draws): (a) other perps (Upbit/K universe plus L's own
symbols, listed >= 30 d) shorted at the same hour, (b) the same coin at random hours 30-180 d after L. Overlap with
K2 = same coin with K2 event within 7 days; report L without overlaps and pooled K2 + L (overlaps counted once, K2's
trade kept). C3 daily-P&L correlation if DEMO numbers.

## Bars (unchanged)
LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, random >= 95 %, HOLD power at VAL size >= 3.
DEMO: IS t >= 2.0, VAL net > 0, random >= 90 %, positive at costs x1.5 and one step late.

## Power arithmetic (before building)
Guess of events (main set): Coinbase listed ~20 assets in 2020, ~70 in 2021, ~40 in 2022, ~15-20 in 2023 and 2024;
perhaps 40-60 % had a Binance perp a week earlier -> IS ~25-45, VAL ~25-45 events.
- 72 h alt-vs-BTC sd after a listing pump: ~1000-1700 bp (K2: 909 IS / 1666 VAL).
- HOLD pace maybe 15-30 Coinbase listings / yr of coins with a perp -> n_HOLD ~ 27-55.
- LIVE needs S >= 3 / sqrt(n_HOLD) = 0.40-0.58 per trade, i.e. net >= ~500-900 bp at sd 1300 bp. K2's VAL S was
  0.25. **L alone can at most reach DEMO** unless the Coinbase effect is about twice K2's VAL Sharpe.
- Pooled K2 + L: n_HOLD ~ 45-75, LIVE needs S >= 0.35-0.45: still out of reach at K2's VAL S (0.25 -> power ~1.7-2.2).
So the realistic question is whether the fade replicates (DEMO numbers on an independent venue), which would make
K2's DEMO case less likely to be noise.
