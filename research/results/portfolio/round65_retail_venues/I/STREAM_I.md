# Stream I (round 65): retail venues with dated listings (scouting, no backtest)

Written 2026-11-01 10:52 UTC (`date -u` at 10:51:15). Hypotheses and planned checks are in
[HYPOTHESES_I.md](HYPOTHESES_I.md), written at 10:38 UTC before any venue request. HOLD was never requested: every
candle request ends <= 2024-12-31 and every series is cut at ts < 2025-01-01 at parse. No trade P&L was computed.

## Answer first
**No scouted venue has the thing K2 depends on: a pump before entry.** Seven venues have usable data:
- 2020-24 history.
- A visible first candle.
- An estimated 14-35 listings a year of coins that already had a Binance perp.

But in 2-5 example listings per venue, the alt's move vs BTC on Binance from L - 24 h to L + 1 h has a median of
**-6 % to +2.5 %**. That is Coinbase's level (+4-7 %, stream L failed), far from Upbit's +21.5 % (K2). Local first-hour
premiums are small too (median -3 % to +4 %). So these listings do not move the global price.

By K and L's evidence (no pump means no fade, and generic pump-shorts lose), a K2-style test on these venues is
expected to fail. **I recommend not running K2 replications on them.**

If the coordinator still wants extra events for pooling, the cleanest data is on **BtcTurk** and **Indodax** (deep
history, first candle visible, delisted markets still served). **Bitkub** is next: delisted markets appear in its
list with a `created_at` date. **Bitvavo** has the most events but hides delisted markets. Bithumb (stream H)
remains the only same-mechanism (Korean) candidate. Coinone is Korean, but its examples show no pump.

## Ranking (usable independent events per year 2020-24, estimated)
Events = listings 2020-24 of a coin whose Binance USDT-M perp was >= 7 days old at L.

The estimate is the current market-list overlap with pre-2025 perps, times the event share in a random sample of
those coins (seed 65/66), spread over 5 years. Venues that hide delisted markets are undercounted.

"Indep." is the share of overlapping coins that are not Upbit KRW markets today. None of the 22 example events had an
Upbit K2 listing within 7 days.

Pump = alt vs BTC on Binance local 1h perp opens, L - 24 h to L + 1 h. L = the first venue 1h candle with volume > 0.

| rank | venue | history (keyless) | first candle | delisted visible | overlap / sample events | est. events/yr | indep. | pump median (examples) | caveats |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Bitvavo (EU, EUR) | 1d from 2019-03; 1h; 1440 bars/req | yes | **no** (MATIC-EUR "market invalid") | 232 / 4 of 5 | ~30-37 | 50 % | +1.9 % (n 3: GRT -8.9, EDU +2.7, ONDO +1.9; MAV n/a) | survivor-only list; EU listings follow global launch |
| 2 | Indodax (ID, IDR) | 1d from 2017; 1h; 1000 bars/req | yes | **yes** (MATICIDR served) | 215 / 3 of 3 known (3 truncated) | ~21-43 | ~50 % | +1.0 % (n 2: HIGH +3.0, JASMY -1.0; PORTAL n/a) | robots.txt disallows /api (only /tradingview/history_v2 used); market list from sitemap only |
| 3 | BtcTurk (TR, TRY) | 1d from 2017; 1h; no cap seen | yes | **yes** (MATICTRY served) | 126 / 5 of 6 | ~21 | 39 % | +0.8 % (n 5: ENJ +6.4, ZRX +0.8, FLOKI -1.6, NEAR +0.1, KAVA +2.0) | exchangeinfo lists current markets only, so delisted tickers must come from elsewhere; listings cluster in 2023-24, often years after the perp |
| 4 | Bitkub (TH, THB) | 1h/1d from 2018-05 (tradingview) | yes | **yes** (112 "stopped" markets listed, candles served) | `created_at` gives 92 events 2020-24 (9/16/14/16/37) | ~18 | 53 % | -1.8 % (n 5: SAND -2.9, WLD +2.3, CYBER -1.8, ENA +9.0, APT -12.8) | `created_at` precedes the first trade by 3 d to 7 months, so it cannot date L; APT's first print is 9.9e8 THB (garbage open) |
| 5 | CoinDCX (IN, INR) | 1d from 2020; 1h; 1000 bars/req; intervals 1m/15m/1h/1d | yes | **no** ("Invalid pair") | 210 / 2 of 3 known (3 truncated) | ~14-28 | 51 % | +2.5 % (n 2: REN +2.4, PEPE +2.5) | first 1d/1h bars can have open 0; survivor-only |
| 6 | Coinone (KR, KRW) | 1d from 2017-08; 1h; 500 bars/req; 1w in one request | yes, after one zero-volume placeholder week | **no** ("Unknown CryptoCurrency") | 175 / 4 of 10 | ~14 | 34 % | +1.0 % (n 4: AVAX +6.3, SUSHI +11.9, GRT -4.5, STX -4.3) | 66 % of its coins are also Upbit KRW (overlap risk with K2 in other events); 1h candles sparse |
| 7 | bitbank (JP, JPY) | from 2017; one request per day (1h) or year (1d) | yes | not tested | 37 / OP 2023-12, GALA 2023-03; SUI not before 2025 | ~2-4 | 27 % | -6.2 % (n 2: GALA -6.1, OP -6.3) | Japanese listings come years after the perp; too few events |
| - | Coins.ph (PH) | 1d only from 2022-10-29 | n/c | n/c | 89 | - | - | - | history too short for IS |
| - | BTC Markets (AU) 36, GMO Coin (JP) 15, BitoPro (TW) 16, Bitso (MX) 7 | market list only | n/c | n/c | overlap in brackets | < 3 | - | - | too few markets; not checked further |

Not usable:
- **Stopped at 403.** WazirX (api); Mercado Bitcoin (Cloudflare 1009, country blocked); Paribu (www); GOPAX (api); MAX
  (api). Not retried.
- **Korbit.** api.korbit.co.kr robots.txt answered 503 three times (6 requests with back-off). Left alone.
- **Disallowed by robots.txt.** Coincheck and Bitstamp both disallow `/api` (Bitstamp: `Disallow: /api/`).
- **No candle API.** bitFlyer has no keyless candle API (executions cover only 31 days) and only 9 markets.
- Bithumb: skipped (stream H).

## Example listings (1h windows only, ts < 2025-01-01; research/data/retail_venues/pump_examples.json)
- **Pump vs BTC on Binance, L - 24 h → L + 1 h.**
  - Medians by venue: Bitkub -1.8 %, Bitvavo +1.9 %, BtcTurk +0.8 %, CoinDCX +2.5 %, Coinone +1.0 %, Indodax +1.0 %,
    bitbank -6.2 %.
  - The largest values: Coinone SUSHI +11.9 % (2021-01, in an alt rally), ENA on Bitkub +9.0 %, AVAX on Coinone
    +6.3 %, ENJ on BtcTurk +6.4 %.
  - None comes close to K2's +21.5 % mean.
- **Most of each move is before the venue opens** (column "pre-open" in the pump.py output). It is general market
  drift, not a reaction to the listing.
- **Local first-hour premium** (venue / Binance at L, relative to the same ratio at L + 48 h): mostly -3 % to +10 %.
  Bitkub APT +13 % comes from a bad first print. Local buyers overpay a little on their own book, and the global
  price does not follow.
- **Listing lag.** Many listings come years after the perp: BtcTurk KAVA 1507 d, NEAR 1393 d, ZRX 1143 d; Coinone and
  Bitkub 25-276 d. Mature coins with deep global books are unlikely to be pushed by one regional venue.

## What a K2-style test could use, and what it would need
- **Data feasibility.** BtcTurk, Indodax, Bitkub (all with delisted markets) and Bitvavo, CoinDCX, Coinone
  (survivors only) can each date L to the hour.
- **Cost of a full pull.** One request per market finds the first day:
  - one 1w request on Coinone;
  - one 1d request on BtcTurk / Bitkub;
  - one or two on Indodax / CoinDCX / Bitvavo (bar caps).
  - Then one 1h window per event.
  - That is about 200-500 requests per venue at 0.3 s.
- **Mechanism check first.** A full pull should come only after a pre-registered "pump >= X" check. The examples say
  the pump is absent, and K's post-hoc control showed that shorting a generic pump loses. So I would not spend a
  stream on it.
- **Power.** Pooling 4 venues gives ~100 events/yr. At an L-like Sharpe per trade (0.12) and 1.83 HOLD years, power
  would be ~0.12 × sqrt(183) ≈ 1.6. LIVE needs 3, so even a positive VAL would not reach LIVE unless the per-trade
  Sharpe were K2-sized (0.25 × sqrt(183) ≈ 3.4). That needs the pump these venues lack.

## Requests (research/data/retail_venues/requests.log)
- **147 fetcher requests**, >= 0.30 s apart per host, plain UA, no key, no e-mail.
  - 114 × 200, 19 × 404 (robots files absent), 5 × 403 (hosts stopped; blocked_hosts.txt), 6 × 503 (Korbit), 7 × 422
    and 1 × 400 (invalid interval / delisted market tests).
  - Plus 5 WebFetch docs reads (GitHub), logged by hand.
- WebSearch: 2 of 15.
- Bodies are saved per venue under research/data/retail_venues/<venue>/ and parsed with `python -I`.
- Derived files: sample_coins.json, bitkub/events_created_at.csv, pump_examples.json.

## Pitfalls met
- **Bitkub `created_at` is not the listing time.** Several markets share one batch timestamp (ALPHA / GRT / SAND
  2021-03-24 17:03), and SAND first trades 7 months later.
- **Coinone placeholder week.** It prints a flat, zero-volume weekly candle the week before trading starts. Filter on
  volume > 0. Its 1h candles are sparse (premium n/a for GRT, STX).
- **Bar caps hide early listings.** CoinDCX and Indodax return at most 1000 bars and Bitvavo 1440, so a 2020-24 range
  of daily bars truncates early listings. Locate with 1w bars or two windows.
- **Mistakes on my side.**
  - CoinDCX rejects 1w bars (only 1m/15m/1h/1d), which cost 6 wasted 422 requests.
  - My first Bitkub 1h windows were placed at `created_at`, before trading started. They are unused but logged.
- **Missing Binance data.** Local 1h files lack MAV (sparse) and PORTAL around L, so their pump is n/a.
- **Thin examples.** 2-5 per venue: the medians are indicative, not estimates.

## Files
- HYPOTHESES_I.md and STREAM_I.md (this file).
- Code in I/code/:
  - fetch.py: polite fetcher.
  - perps.py: perp starts.
  - overlap.py, minor_venues.py: market-list overlap.
  - sample.py, sample2.py: random example picks.
  - sample_eval.py: first candle vs perp start.
  - bitkub_events.py: `created_at` counts.
  - candles.py: per-venue parsers.
  - pull_windows.py: 1h windows.
  - pump.py: pump and premium.
