# Stream JP (round 69) hypotheses: seconds after Japanese venues' listing notices

Written Sun Nov 1 17:11:57 UTC 2026 (from `date -u`). At this point only notice pages (titles, post stamps, a few
bodies for stated start times) and the local perp_1d first-kline dates have been read. **No aggTrade has been
downloaded and no price, path or return has been computed.** HOLD (2025-01-01..) is never requested, loaded or counted:
every event has N, L < 2025-01-01, notice rows dated >= 2025 were dropped unprinted at parse, and every kline series is
cut at ts < 2025-01-01 at load.

## Step 1: sources (details in STREAM_JP.md; requests in research/data/jp_notices/requests.log)
| venue | robots.txt | notice history 2020-24 with post times | used |
|---|---|---|---|
| bitbank (row note added 17:17 UTC after the run: 42 % of 2020-24 stamps end in :00, so some are minute-level) | bitbank.cc: only /account/ disallowed | **yes**: bitbank.cc/blog (お知らせ / maintenance / campaign tags, 109 pages, server-rendered) carries `publishedAt` with seconds (ms for posts after the 2024-08 CMS move). 587 rows 2019-12..2024 | yes |
| Coincheck | coincheck.com disallows /api (not used); corporate.coincheck.com allows /news and /press (disallows /2017-2021/, /archive, /en) | **yes, partly**: corporate press / news pages carry CMS `publishedAt` to the second (970 news + 273 press rows read, one page each). Press stamps of 2020 to mid-2021 sit at 01:00:00 UTC (10:00 JST) in 96 % (2020) / 67 % (2021) of rows: a fixed release time or a date-only placeholder; flagged `P10` | yes |
| GMO Coin | coin.z.com allows /jp/news | **no**: the WordPress news site's sitemap starts 2026-02; the older お知らせ list is not served | no |
| bitFlyer | bitflyer.com / www.bitflyer.com: 6 timeouts (no TCP answer from this network); api.bitflyer.com robots 404 | not reachable | no |
| BITPoint | www.bitpoint.co.jp robots.txt **403** | stop (rule) | no |

## Mechanism and side (fixed before data)
A Japanese venue announces it will list a coin. Japanese retail cannot buy it abroad easily, but global traders and
bots that read the notice may front-run expected local demand on the Binance perp, as with Upbit (A2). Side: **long the
alt USDT-M perp, short BTCUSDT perp, equal notional.** Prior: weak. Stream I's examples showed no pump around JP listing
days (bitbank median -6 %), JP listings come years after the perp (median perp age here ~600 d), and the coins are
large caps (ADA, DOT, SOL, BNB, AVAX, LINK).

## Events (frozen; code/events.py prints the screen)
One event per (venue, coin). **N = post stamp of the venue's first public notice that it will list a new coin** (not
pair or order-book additions of coins it already lists, not token migrations RENDER / POL). **L = the venue's stated
trading start:** the stamp of its own later "trading has started" notice (bitbank: `取扱いを開始しました`; Coincheck:
`本日より…取扱いを開始`, CHZ / LINK: the start-day news). For same-day Coincheck notices whose body gives no later clock
time ("本日午後", or "正午" already passed at N), L = N + 60 min (brief's fallback). Screen: Binance USDT-M perp first
daily kline <= N - 7 d and trading at N + 1 d (local perp_1d; SHIB -> 1000SHIBUSDT).

- **IS (2020-21), 9 events on 9 days:** bitbank XLM, QTUM, BAT, OMG, LINK; Coincheck BAT, IOST, ENJ (all P10, L days
  later), OMG (P10, same day, L = N + 60 min).
- **VAL (2022-24), 34 events on 24 days:** bitbank MKR, ENJ, MATIC (first notice = "近日取扱い開始予定"), DOT, DOGE,
  ADA, AVAX, AXS, SAND, APE, GALA, CHZ, MANA, GRT, RNDR, BNB, ARB, OP, KLAY, IMX, MASK, SOL, CYBER; Coincheck SAND,
  IMX, APE, AXS, AVAX, SHIB (same day, L = N + 60 min), DOT, CHZ, LINK, MKR, MATIC (L days later).
- Excluded by the screen: no perp (XYM, BOBA, FLR, OAS, DAI, PLT, FNCT, WBTC, BRIL, BC), perp < 7 d (bitbank ASTR,
  Coincheck QTUM).
- Hold N -> L: bitbank 50-314 h (median ~120 h); Coincheck 1 h (7 events) or 95-357 h.
- **Upbit overlap** (coin in any Upbit listing title, stream A's listing_titles.json, within 7 days of N): **none**.
- Stamp classes: `s` (seconds, irregular or scheduled round times) for bitbank and Coincheck 2022-24; `P10` for the 5
  Coincheck IS events. All results are also reported without P10.

## Rule (A2-D5L frozen, the only rule; no grid)
- Price at t = last aggTrade with time <= t. Entry: first alt and first BTC aggTrade with time >= N + 5 s. Exit: first
  trade >= L on each leg. Taker fills. A2's `trade`, `slip`, `fund`, `clt` code copied unchanged.
- Costs (as A2): 20 bp (4 taker fills x 5 bp) + declared slippage (per fill, half the median 1 s range of that symbol's
  trades in the 60 s from the fill) + real funding over (entry, exit] (local funding files, else public fapi
  fundingRate with endTime < 2025).
- t clustered by notice day. Robustness: costs x1.5; one step late = d 10 s (D10-L).
- Descriptive only (declared now, never selectable): D2-5m, D5-5m, D30-5m (exit N + 5 min).
- Random benchmark (declared change from A2, because holds last days): same coin, 1,000 draw sets of one random 1h-open
  entry per event within N +- 180 d, the whole hold outside [N - 7 d, L + 7 d] and before 2025-01-01, hold =
  round((L - N) / 1 h) hours, gross alt-vs-BTC return from local 1h perp opens (binance_basis/perp_1h, cut < 2025).
  Percentile of the event gross mean; and the 95th percentile of the random net t (event costs subtracted).
- Years: IS 2020, 2021; VAL 2022, 2023, 2024.

## Path and stamp check (before the rule)
- r(t) = ln(alt_t / alt_ref) - ln(BTC_t / BTC_ref), ref = last trade at or before N - 60 s; median and quartiles at
  t - N in {-60, -30, -10, -5, -2, -1, 0, +1, +2, +3, +5, +10, +20, +30, +60, +120, +300} s per era.
- Onsets as A2: (a) first alt trade in N +- 300 s with r >= +2 % (and, added for small JP moves, r >= +0.5 %); (b) first
  1 s bin with trade count >= max(10, 10 x the pre-N median per second). Onset < 0 = the move leads the stamp. Also the
  alt trade count in [N, N + 60 s) over the pre-N per-minute mean.
- If there is no burst after N, the stamp cannot be confirmed from the tape; that is reported as "unverified", and P10
  stamps in particular stay unverified.

## Power arithmetic (before any return)
- HOLD pace at the VAL rate: 34 events / 3 years x 1.83 years ~ **21 events**. **LIVE needs VAL net SR per trade >=
  3 / sqrt(21) = 0.65.** VAL t >= 1.5 over 24 day clusters needs SR ~ 0.3.
- IS: 9 events on 9 days. DEMO's t >= 2.0 needs SR ~ 0.67; LIVE's 2.5 needs ~ 0.83.
- Holds of 3-15 days carry alt-vs-BTC noise of roughly 6-12 % per trade, so SR 0.65 needs a mean of ~+4-8 % per trade.
  Only a large, consistent post-notice drift could reach it. Expected verdict: none.
