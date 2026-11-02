# Stream L (round 64): Coinbase listing fade, a replication of K2

Written 2026-11-01 10:17 UTC (`date -u`). Hypotheses declared in [HYPOTHESES_L.md](HYPOTHESES_L.md) at 10:01 UTC,
before any Coinbase candle was requested. HOLD (2025-01-01..) was never requested, loaded or counted.

## Answer first
**None. K2 does not replicate on Coinbase listings.**
- Frozen K2 rule (short the Binance alt perp, long BTC perp, at the close of the 1m bar at L + 1 h, hold 72 h, 42 bp
  plus real funding), applied to the first Coinbase `<COIN>-USD` hour L of 67 coins whose Binance perp was >= 7 days
  old:
  - **IS 2020-21: net -621 bp/trade, t -0.81, n 31** (21 entry days). Fails the DEMO bar (IS t >= 2.0).
  - **VAL 2022-24: net +151 bp, t 0.73, n 35.**
  - Years positive 3 / 5 (2020 +597, 2021 -976, 2022 +398, 2023 -388, 2024 +5).
  - Random benchmark (K2's, gross on 1h closes): IS beats **0 %** of other-alt draws and 0.6 % of same-coin draws;
    VAL beats 100 % / 95 %.
  - Power at VAL size: SR 0.120 x sqrt(11.7/yr x 1.83 = 21) = **0.55**.
- **Overlap with K2** (same coin within 7 days): 2 events, GMT 2022-04-28 and PEPE 2024-11-13. Without them: IS
  -621 (t -0.81, n 31), VAL +193 (t 0.88, n 33).
- **Pooled K2 + L** (overlaps counted once, K2's trade kept), H72: **IS -172 bp, t -0.29, n 42; VAL +300 bp, t 1.52,
  n 62**, SR 0.206. Power at VAL size 0.206 x sqrt(20.7/yr x 1.83 = 38) = **1.27**. Pooling makes K2's DEMO case
  weaker, not stronger: the IS sign flips.
- No PREREG_DRAFT. K2's own draft stands on Upbit alone, and this result is evidence that its IS edge is
  venue-specific (or small-sample luck), not a general "retail listing fades" effect.

## Data (all public, no key, no e-mail)
- **Coinbase Exchange** (api.exchange.coinbase.com): `robots.txt` returns **401** (no public file; logged 6 times,
  K's fetcher retries non-404 errors). 1168 requests with status 200, >= 0.26 s apart, no 403 / 418 / 429.
  - `/products`: 845 products, **328 with status `delisted`** (so delisted listings are mostly present), 495 USD.
  - 203 USD products have a base with a Binance USDT-M perp that started before 2025. Daily candles find the first
    trading day (window before the perp start, then forward), one 1h request gives L. All requests end
    <= 2024-12-31 23:59:59 UTC.
  - Robustness pull: daily candles of the other quote products (BTC, USDT, USDC, EUR, GBP, ETH) of each event's base
    for the 300 days before L - 1 d.
- **Binance fapi** (public): 281 requests. They fetched 1m klines around entry / exit / L - 24 h and funding windows
  for RONIN and MOG. Local 1h perp klines and funding files (cut at ts < 2025-01-01) and K's BTCUSDT 1m cache were
  read only. K's 1m alt cache was read only; new bars went to research/data/coinbase/binance/alt_1m.
- Files: research/data/coinbase/{requests.log, raw/products.json, raw/robots.txt, listings.csv, otherquotes.csv,
  exclusions.json, otherquote_flag.json, binance/alt_1m, binance/funding, binance/l2_trades.pkl}.

## Events
- 67 events in the main set (perp >= 7 d, K2's frozen filter): 2020 7, 2021 25, 2022 19, 2023 6, 2024 10.
  Secondary set (perp >= 1 d, the brief's wording) adds TIA, ONDO, STRK: 70 events.
- Not events: 130 of the 203 USD products had traded on Coinbase before the Binance perp existed (or before
  2019-12-20). This includes most of the big 2021 Coinbase listings (the perp came after).
- 10 of the 67 are now delisted on Coinbase (MATIC, STORJ, ENJ, GALA, UNFI, ATA, DAR, MTL, ANT, RONIN). So the
  survivorship bias that K had on Upbit is small here.
- **Declared guards.**
  - Name collision (Binance vs Coinbase price at L + 2 h outside x0.5..x2): dropped only **SHIB**, ratio 0.14. It is
    not a collision: Coinbase's first SHIB-USD hours printed ~7x the global price. Keeping SHIB changes nothing
    (IS H72 -593, t -0.80).
  - Ticker migrations: none among the events.
  - Other quote traded >= 1 d earlier (so the USD pair was not the listing): BAT, MANA, ZEC (USDC / BTC / ETH pairs
    in 2020). Without them: IS H72 -743 (t -0.89, n 28), VAL unchanged.
- Event table with per-event net: [l2_events.csv](l2_events.csv).

## Results (net bp per trade, t clustered by entry day; full output l2_output.txt, l2_results.json)
| cell | era | n | gross | fund | **net** | **t** | median | sd | SR | x1.5 | +5 min | L + 2 h | years |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H72 (K2's choice)** | IS | 31 | -582 | +3 | **-621** | **-0.81** | +399 | 3087 | -0.20 | -642 | -629 | -726 | 2020 +597 (7), 2021 -976 (24) |
| | VAL | 35 | +194 | 0 | **+151** | **0.73** | +357 | 1257 | 0.12 | +130 | +169 | +163 | 2022 +398 (19), 2023 -388 (6), 2024 +5 (10) |
| H24 (declared sibling) | IS | 31 | -123 | -3 | -168 | -0.43 | +354 | 1800 | -0.09 | | | | +274, -297 |
| | VAL | 35 | -134 | -3 | -179 | -0.61 | +201 | 1720 | -0.10 | | | | +189, -1199, -267 |
| H72 perp >= 1 d | VAL | 38 | +217 | +2 | +177 | 0.91 | +395 | 1229 | 0.14 | | | | IS identical |
| H72 without K2 overlap | VAL | 33 | +235 | 0 | +193 | 0.88 | +433 | 1264 | 0.15 | +172 | | | +401, -388, +163 |
| **Pooled K2 + L, H72** | IS | 42 | -128 | -2 | **-172** | **-0.29** | +475 | 2785 | -0.06 | -193 | -203 | -297 | 2020 +581, 2021 -439 |
| | VAL | 62 | +391 | -49 | **+300** | **1.52** | +499 | 1458 | 0.21 | +279 | +297 | +302 | +398, +460, +129 |
| Pooled K2 + L, H24 | IS / VAL | 42 / 62 | | | +52 / +128 | 0.17 / 0.67 | | | | | | | |

The K2 numbers inside the pool are recomputed with K's code and caches and match K2 exactly (IS +1094 t 3.16, VAL +423
t 1.37).

**Random benchmark** (K2's two kinds of draw, 500 each; l2_random.txt). VAL n is 32 here because 3 symbols lack a
local 1h file.

| hold | era | events gross (1h) | % beaten, other alts same hour | median of draws | % beaten, same coin 30-180 d later | median |
|---|---|---|---|---|---|---|
| H72 | IS | -695 | 0.0 | +4 | 0.6 | -39 |
| H72 | VAL | +242 | 100 | -132 | 95.0 | +21 |
| H24 | IS | -291 | 2.6 | -6 | 1.2 | -18 |
| H24 | VAL | -92 | 10.0 | +9 | 12.6 | +6 |

C3 correlation was not computed: no cell reaches DEMO numbers.

## Why it fails
- **Squeeze tails.** The median is positive in every era (+399 IS, +357 VAL at H72; win rate 65-69 %), but the mean is
  wrecked by a few coins that kept running after the Coinbase listing. This is the round 60 new-listing pattern.
  - STORJ 2021-03-25: -11053 bp. ANKR, same day: -7867. GALA 2021-11-16: -8591. BONK 2023-12-14: -3963
    (-8381 at H24). MOG 2024-12-05: -3677.
  - Dropping the 2 worst IS trades turns IS to +22 bp; a 10 % trimmed mean is +102 IS / +307 VAL. That is the median
    story, not a tradable mean, and no stop was declared (none is added after the fact).
- **No pump to fade at the entry.** The alt's run-up vs BTC from L - 24 h to the entry is only +4.3 % IS / +7.0 % VAL,
  against +21.5 % for Upbit KRW listings. Coinbase pre-announces ("inbound transfers" / roadmap), and the attention
  flow is spread out. Upbit's KRW open concentrates Korean retail in one hour. The mechanism K2 relies on (an
  overshoot priced in by L + 1 h) is mostly absent here.
- **2021 alt-season.** Most IS events (24 / 31) are 2021 listings that came into a market-wide alt rally, so the short
  alt leg fights the regime. 2020 and 2022 are positive.

## Bars
- LIVE: fails everything except random in VAL (IS t -0.81 vs 2.5, VAL t 0.73 vs 1.5, 3 / 5 years, IS random 0 %,
  power 0.55).
- DEMO: fails (IS t -0.81 < 2.0, IS random 0 %).
- Pooled K2 + L: also fails both (IS t -0.29). The pool is not a registrable rule: it was not declared as a stand-alone
  candidate, and its IS is negative anyway.

## Pitfalls met
- **Import shadowing (my error).** K's k2.py inserts K/code at the front of sys.path when imported. My fetch then
  loaded K's `net` instead of mine, so the 281 fapi requests were logged in research/data/upbit/requests.log
  (10:13-10:14 UTC) instead of mine. The data files themselves went to my folder. I did not edit K's log. The lines
  are copied, tagged, into research/data/coinbase/requests.log, and l2.py now loads its own net.py by path.
- **A per-event table bug (fixed before the write-up).** Events sharing the same L hour (ANKR / CRV / STORJ) collapsed
  in the first l2_events.csv. The summaries were unaffected (verified identical).
- **Coinbase first-hour prints.** SHIB-USD opened at ~7x the global price. The collision guard should compare a later
  hour; it did not matter here.
- Coinbase `robots.txt` is 401 rather than 404. It was treated as "no robots file", as stream X did.

## What a user decision could unlock
- Nothing for this rule. A Coinbase-listing short would need a stop against squeezes, which round 60 and K both
  declined to add post hoc. Registering one would be a new hypothesis, and it would need fresh data, since 2020-24
  has now been seen.
- K2 (Upbit) remains a DEMO draft on its own. This replication argues for a small notional and a strict stop rule if
  the coordinator opens its HOLD.

Code: round64_parallel/L/code/ (net.py = K's fetcher with my data path; pull_products.py, pull_listings.py,
pull_otherquotes.py, guard.py, l2.py, c3corr_l.py unused). K's files are imported unchanged; their sha256 values match
PREREG_DRAFT_K (k2.py f671e399..., kdata.py da002ebb..., fills.py b058e839..., net.py 49cbd7e4...).
