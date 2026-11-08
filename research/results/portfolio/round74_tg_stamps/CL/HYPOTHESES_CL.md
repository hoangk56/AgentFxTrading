# Stream CL (round 74) hypotheses: listing posts for Bithumb / Coinbase / Robinhood / others, timed by Telegram

Written Mon Nov 2 14:47:28 UTC 2026 (from `date -u`). At this point only Telegram titles and stamps (2017-10..2024-12)
and the local perp_1d spans have been read. **No aggTrade or other price has been requested or computed.** HOLD
(2025-01-01..2026-10-29): only the per-class count of distinct (class, coin) title pairs, below. No HOLD time, coin
or price is kept or printed. One slip happened before this file: while learning the post format I printed the 20
newest @coin_listing titles (2026-10). They were titles only, with no prices. They are not used in any rule.

## Mechanism (side fixed before data)
A2-D5L (round 65) works because Korean retail buys an Upbit KRW listing and bots carry the move to the Binance perp
within 1-3 s, then the coin keeps drifting into the KRW open. The same retail-demand story is tested on other
venues, using the third-party feed's Telegram stamp T as the public time:
- **Bithumb KRW**: the second Korean retail venue.
- **Coinbase**: the US "Coinbase effect". Two separate events are tested:
  - the first announcement;
  - the retail go-live (app / coinbase.com), which comes later.
- **Robinhood**, and others.

**Long the coin's Binance USDT-M perp, short BTCUSDT perp, equal notional** (A2's side and hedge).

## Data
- **Posts.** @coin_listing pages from the coordinator's round 74 pull (research/data/telegram_hist/raw/coin_listing),
  plus round 73's complete read-only cache of the same channel (research/data/telegram_upbit/raw/coin_listing, 588
  pages, pulled 2026-11-02 ~03:00 UTC).
  - Round 74 pages override round 73 per post id. The event list will be rebuilt once the coordinator's pull is
    complete, and differences will be reported.
  - @newlistingsfeed: pulled by me through the shared fetcher (165 pages, 14:24-14:42 UTC, reached id 1).
  - Every post is cut at T < 2025-01-01 right after parsing (`code/load.py`).
- **Coverage of the non-Upbit / non-Binance venues (pre-2025, found from titles):**
  - @coin_listing:
    - Bithumb notice relays 2020-03..2021-08, and market posts "X/KRW listed on Bithumb" 2018..2020-01.
    - Coinbase blog relays 2020-05..2022-02, Coinbase tweet relays 2022-06..2023-03, and 3 posts in 2024.
    - Huobi "will list" 2020-22, Kraken 2019-20, 1 Robinhood post (2024-11).
    - From 2023-05 to 2024-12 the channel posts almost only Binance and Upbit.
  - @newlistingsfeed: Coinbase from 2024-04, Bithumb from 2024-07, Robinhood from 2024-12.
  - So VAL coverage is patchy: Bithumb VAL = 2024-07..12 only; Coinbase VAL = 2022-06..2023-03 + 2024-04..12.
- **Prices.** data.binance.vision futures/um daily aggTrades (`code/pull.py`, adapted from A2's pull.py):
  - Alt perp: every UTC day touched by [T - 15 min, T + 65 min]. Trades in that window are kept, plus a 1 s series
    for the day.
  - BTCUSDT: local futures-aggTrades npz with a 1 s series (upbit_latency, upbit_census, btc_treasury_8k,
    upbit_bybit_notice; non-HOLD days only), else the day is pulled the same way.
  - Every requested file is dated <= 2024-12-31. The requests log is research/data/tg_cl/requests.log.
- Perp age: round 65 A's `perps.perp_for` (first daily kline <= T - 7 d, alive at T + 1 d; day precision, as
  registered for A2).

## Title regexes per class (code/events.py, `classify`)
- **BH (Bithumb KRW listing).**
  - Matches any of:
    - `Bithumb will list|Bithumb listing/airdrop event` (not "Global"), whose text has
      `상장 예정|추가 예정|신규 상장|원화 마켓|to be listed|new listing`;
    - `^X/KRW listed on Bithumb$`;
    - `listed on Bithumb spot`;
    - `[BITHUMB] $X listed on Bithumb`.
  - Dropped: BTC-market-only notices (`BTC 마켓` without `원화|KRW`).
- **CBA (Coinbase first announcement).**
  - Matches: `Coinbase Pro will list`, `launching on Coinbase Pro`, `Coinbase lists`, `added to the roadmap`,
    `added to Coinbase roadmap`, `Coinbase Roadmap`, `Coinbase will add support for`,
    `listed on Coinbase spot: <date> at <time>`.
  - Not events: Coinbase International futures, Custody, Staking, Pro API pair, BTC auction, maintenance posts.
- **CBL (Coinbase retail go-live).** Matches: `is / are now available on Coinbase`, `now live on https`,
  `trades are live`, `listed on Coinbase( spot)$`, `added to Coinbase spot`.
- **RH**: `Robinhood Listed|listed on Robinhood`.
- **OTH**: `Huobi will list|Kraken listing|KuCoin will list / listing`.
- **Tickers:**
  - from `$X`, `#X` and `(X)` / `((X))` in the first line;
  - else from `(X)` in the text;
  - else the caps list after "will add support for".
  - Market / stable / wrapped tokens are dropped (BTC, KRW, USDT, USDC, DAI, UST, WBTC, ...).
- **Event** = the first post of (class, coin) with no post of the same (class, coin) in the 180 days before, and a
  Binance perp >= 7 d old.
  - Multi-coin posts give one event per coin.
  - Event list: CL/events.csv (with perp); CL/events_all.csv (every first post).

## Event counts (pre-2025, with perp >= 7 d) and HOLD counts (titles only)
| class | IS 2020-21 n (days) | VAL 2022-24 n (days) | per year (2020 / 21 / 22 / 23 / 24) | perp share VAL | HOLD distinct (class, coin) titles | expected HOLD events (x perp share) |
|---|---|---|---|---|---|---|
| BH | 13 (12) | 19 (15) | 3 / 10 / 0 / 0 / 19 | 0.51 | 125 | ~64 |
| CBA | 28 (21) | 23 (21) | 6 / 22 / 14 / 1 / 8 | 0.23 | 66 | ~15 |
| CBL | 24 (15) | 21 (19) | 4 / 20 / 13 / 2 / 6 | 0.21 | 85 | ~18 |
| RH | 0 | 5 (2) | 0 / 0 / 0 / 0 / 5 | - | 22 | (~22, big coins) |
| OTH | 5 (5) | 2 (2) | 1 / 4 / 2 / 0 / 0 | - | - | - |

- HOLD counts are distinct (class, coin) pairs in the 2025-01-01..2026-10-29 titles of both channels. There is no
  perp check, and nothing else from HOLD is read. The expected HOLD events multiply them by the VAL perp share
  (BH: the 2024 share).
- RH (no IS event) and OTH (5 / 2) cannot pass any bar; they are reported descriptively only.

## Rule and grid (6 graded cells)
- **Entry** at T + 5 s: the alt's first aggTrade with time >= T + 5 s; BTC at the 1 s last price of second T + 5 s.
  - BTC is read from the 1 s series because most local BTC days keep trades only around other events. The error is
    < 1 s of BTC movement (~1 bp).
- **Exits X:**
  - X in {T + 5 min, T + 60 min}: the alt's first trade >= X; BTC at the 1 s last price of second X.
  - Venue open "when the post states it": in the pre-2025 events with a perp this appears in < 5 posts. Bithumb and
    Coinbase relays mostly state no time. So it is not a graded cell; the count is reported.
- **Cells:** {BH, CBA, CBL} x {5m, 60m}.
  - Per class, the declared choice is the better IS t of the two exits, checked on VAL unchanged.
  - Each class is its own venue hypothesis. The max-over-6-cells null is reported.
- **Costs:** 20 bp (4 taker fills x 5 bp) + alt slippage (A2's declared measure: half the median 1 s range in the
  60 s after each alt fill, entry and exit) + 1 bp per BTC fill (2 bp) + real funding (A2's `fund`, local files /
  public fapi).
  - net = (alt_x / alt_e - 1) - (BTC_x / BTC_e - 1) + funding - costs.
- **Robustness:**
  - costs x1.5;
  - one step late: entry at T + 10 s;
  - drop edited posts (1 event);
  - drop multi-coin posts.
- **t:** clustered by post day (A2's `clt`).
- **Years:** IS 2020, 2021; VAL 2022, 2023, 2024 (per class, the years that have events).
- **Random benchmark** (A2's):
  - same coin, same day, random entry second;
  - same hold, wholly outside [T - 15 min, T + 65 min + 1 h];
  - gross; 1,000 draw sets of one draw per event; percentile of the event mean.
  - The same draw sets give the max-over-cells net-t null.

## "Already moved" measure (declared; no P&L meaning)
- Ref = the last trade at or before T - 10 min.
- r(t) = ln(alt_t / alt_ref) - ln(BTC_t / BTC_ref).
- Onset = the first alt trade in [T - 10 min, T + 5 min] with r >= +2 %.
- An event "moved before entry" if onset < T + 5 s. Also reported: the share with onset < T, and the median path
  r at T - 60 s, T, T + 5 s, + 60 s, + 5 min, + 60 min, per class and era.

## Power arithmetic (before any price)
- **BH.**
  - HOLD ~64 events: LIVE power >= 3 needs VAL net SR per trade >= 3 / sqrt(64) = 0.375.
  - VAL t >= 1.5 on 15 days needs SR ~0.39-0.42. IS t >= 2.0 (DEMO) on 12 days needs SR ~0.58; 2.5 (LIVE) ~0.72.
- **CBA.**
  - HOLD ~15: LIVE power needs SR >= 0.77, which is implausible.
  - DEMO: IS t >= 2.0 on 21 days needs SR ~0.44 (clustered).
- **CBL.**
  - HOLD ~18: LIVE needs SR >= 0.71.
  - DEMO IS t >= 2.0 on 15 days needs SR ~0.52.
- **Prior.**
  - Round 66 O2: OKX / Bybit notices had no seconds reaction (median +2 bp at +5 s).
  - Round 64 L: Coinbase listings had no K2-type fade.
  - Round 65 H: Bithumb run-up before the open was +5.5 % vs Upbit's +21.5 %.
  - Coinbase relays in @coin_listing came from the blog / RSS and from tweets, so the post may lag the first public
    source. The "already moved" share will show this.
  - Expected: no cell passes. BH is the only class whose HOLD size could carry LIVE power.
