# HYPOTHESES_WA: Whale Alert Telegram posts -> Binance USDT-M perp, 5-60 min

Written 2026-11-02 14:25:43 UTC (from `date -u`), after 19 id-probe pages and before any price was requested.
Stream WA of round 74 (BRIEF.md). HOLD (2025-01-01..2026-10-29) stays closed: posts with time >= 2025-01-01 are
dropped right after parsing; no price request ends after 2024-12-31 23:59:59 UTC.

## What is different from rounds 53, 31 and 48
- Round 53 timed USDT mints by the **chain block** (+ 2 min) and only mints (Omni + Tron USDT). Here the clock is the
  **Telegram post time** of Whale Alert (what traders actually saw and what bots key on), entry at seconds-minutes
  after it, and USDC mints / burns join USDT.
- Rounds 31 / 48 used **daily, not point-in-time** exchange-flow totals (CoinMetrics community). Here each large
  transfer is an event with its own second stamp, **direction** (unknown wallet -> exchange = inflow, exchange ->
  unknown wallet = outflow) and **size** in USD as posted.

## Mechanism (side fixed before data)
- A large BTC / ETH deposit to an exchange from an unknown wallet is read as an intent to sell (coins move to an
  exchange to be sold); the post itself is seen by many traders and bots, who may front-run the expected sale.
  -> **short** that coin's perp. A large withdrawal to an unknown wallet = coins leaving for cold storage (less supply
  on the venue) -> **long**.
- A USDT / USDC mint = new dollars about to buy crypto -> **long BTCUSDT**; a burn = dollars leaving -> **short**.
- Prior: weak. Whale Alert is the most-watched on-chain feed, so any post-time reaction may be priced in seconds
  (before a 1-minute entry) or be noise; round 53 found mints follow price.

## Data
- Events: t.me/s/whale_alert_io via the shared round-74 fetcher (coord/tg.py, one lock, >= 1.5 s gap), raw pages in
  research/data/telegram_hist/raw/whale_alert_io/. Ids are dense (probe: 20 posts per page; page 1 has 10).
  Era boundaries from probes: 2020-01-01 ~ id 6,960; 2022-01-01 ~ id 56,870; 2025-01-01 ~ id 85,500 (top ~104,490).
  So IS 2020-21 ~ 49,900 posts (~2,495 pages), VAL 2022-24 ~ 28,630 posts (~1,430 pages). 2019 is not used
  (perps: BTCUSDT from 2019-09, ETHUSDT from 2019-11; IS is the brief's default 2020-2021).
- Prices: Binance USDT-M perp **1-minute klines** BTCUSDT / ETHUSDT from data.binance.vision (monthly zips,
  2020-01..2024-12), logged in research/data/whale_alert/requests.log. Justification: 1,800 days x 2 symbols of daily
  perp aggTrades is ~250 GB; the events cover almost every day. Exits are 5-60 min, so a <= 60 s entry delay is
  small against the horizon and is conservative for a "front-run the dump" mechanism (any first-minute move is given
  up, not captured). Seconds check: if a cell passes IS on 1-minute data, its IS and VAL entries are re-done at the
  first aggTrade at or after post + 5 s from fapi `/fapi/v1/aggTrades?startTime=..&limit=1` (keyless) and exits from
  the same endpoint, and that number is the one reported against the bars.

## Sampling plan (declared before the pull)
- Systematic page sample by id: a page = ids [b - 20, b - 1] fetched as `?before=b`.
  IS: b = 56,860 - 80 j while b > 6,960 (every 4th page, ~624 pages, ~12,500 posts).
  VAL: b = 85,500 - 40 j while b > 56,870 (every 2nd page, ~716 pages, ~14,300 posts).
  Total ~1,340 pages (+19 probes already saved). VAL is sampled denser because VAL size sets the HOLD power figure.
  Posts outside the era of their page are assigned by their own time; posts >= 2025-01-01 are dropped at parse.
  Pages already present (probes) are reused. A page sample is an unbiased (cluster) sample of posts; t is
  clustered by day anyway.

## Event parsing (fixed)
- Regex on the post text: `<amount> #<COIN> (<usd> USD) transferred from <A> to <B>` and
  `<amount> #<COIN> (<usd> USD) (minted|burned) at <X>`. Edited posts dropped (count reported).
- Exchange = label containing one of: Binance, Coinbase, Kraken, Bitfinex, Bitstamp, OKEx, OKX, Huobi, HTX, Gemini,
  Bittrex, Poloniex, Bithumb, Upbit, KuCoin, Bybit, FTX, Gate, CryptoCom / Crypto.com, BitMEX, Deribit, Bitget, MEXC,
  Bitflyer, Coincheck, Bitso, Bitpanda, Binance.US, Liquid, HitBTC, Kucoin; excluding labels with "Custody".
  Unknown = label starting with "unknown". Inflow: unknown -> exchange; outflow: exchange -> unknown.
  Exchange -> exchange and unknown -> unknown are not events.
- Coins: BTC (#BTC only, not WBTC) and ETH (#ETH only). Mint / burn: #USDT or #USDC with "minted" / "burned" (any
  treasury label).

## Rules and grid (sides from the mechanism, nothing else)
| id | event | trade |
|---|---|---|
| BI | BTC inflow | short BTCUSDT |
| BO | BTC outflow | long BTCUSDT |
| EI | ETH inflow | short ETHUSDT |
| EO | ETH outflow | long ETHUSDT |
| F | BI + BO + EI + EO pooled (each trades its own coin, its own side) | primary hypothesis (largest n) |
| M | USDT / USDC mint | long BTCUSDT |
| B | USDT / USDC burn | short BTCUSDT |
Size buckets: all posted sizes, and USD >= 100 M (as posted). Horizons: +5, +15, +60 min.
7 x 2 x 3 = **42 cells**. Report the max-over-cells null (expected max |t| of 42 correlated cells from the random-time
benchmark).
- Entry: open of the first 1-minute bar starting at or after post + 5 s (1-minute data); exit: open of the bar
  h minutes after the entry bar. One trade at a time per cell and coin: events arriving while a trade of the same
  cell and coin is open are skipped.
- Costs: 5 bp taker a side + 1 bp a side slippage (BTC / ETH perps, spread ~0.1-0.5 bp) = 12 bp round trip;
  checks at x1.5 (18 bp) and one step late (1-minute data: next bar, i.e. +60 s; seconds re-check: +5 s).
- Statistics: per-trade net in bp; t clustered by UTC day (day sums, CR1 SE); per-year nets 2020..2024;
  random benchmark: 1,000 draws of the same number of trades, same side, same coin, entry times uniform within the
  same UTC days as the real trades (keeps day drift), same exit rule; percentile of the real mean net.
- Parameters picked on IS only (the bucket and horizon of the best IS cell per rule), checked on VAL unchanged.

## Power arithmetic (before data)
- Post rate: VAL ~9,540 posts / yr; HOLD (ids ~85,500..~104,490 over 1.83 yr) ~10,400 posts / yr. If a cell is a
  fraction f of posts, HOLD has ~19,000 f events (fewer trades after the one-at-a-time rule).
- LIVE needs net Sharpe per trade x sqrt(HOLD n) >= 3. f = 5 % -> n ~ 950 -> Sharpe >= 0.097 per trade. BTC 5-min
  return sd ~ 15-25 bp, 60-min ~ 50-80 bp: the 5-min cell needs net >= ~2 bp (gross >= ~14 bp), the 60-min cell net
  >= ~6 bp (gross >= ~18 bp) per trade, on every trade-sized event. f = 1 % (>= $100 M) -> n ~ 190 -> Sharpe >= 0.22,
  i.e. net >= ~4 bp at 5 min / ~13 bp at 60 min. Day clustering lowers effective n further, so these are floors.
- IS sample t: with ~12,500 IS posts sampled and f = 5 %, n ~ 625 trades; t 2.5 needs per-trade Sharpe ~0.10, the
  same size as the HOLD bar; so IS and HOLD bars bind together.
- Expected HOLD trades for a passing cell = (VAL trades per year in the sample) x 2 (VAL sampling 1/2) x 1.83 x
  (10,400 / 9,540), stated as an upper bound (full-rate trades overlap more).

## Addendum 2026-11-02 15:44:43 UTC (after the 1-minute results, before any seconds data)
- No cell passed IS on 1-minute data (results/cells.csv), so the seconds re-check is not required by the plan; it is
  run anyway to test the one way the 1-minute design could hide an edge (a move inside the first minute).
- fapi `/aggTrades` serves only the last 2 days (-4166) and spot `/api/v3/aggTrades` returns [] for 2020 windows,
  so the check uses data.binance.vision USDT-M **daily aggTrades** on a random sample of 30 event days per era
  (seed 74), all events on those days (no one-at-a-time filter): side-signed return from the first aggTrade at or
  after post + 5 s to post + 65 s (the part the 1-minute entry gives up), to post + 305 / 905 / 3605 s (seconds-entry
  trades), and the +10 s late entry. No parameter is chosen from it.
