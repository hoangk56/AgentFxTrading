# Stream O2 (round 66) hypotheses: OKX / Bybit listing announcements -> Binance perp within seconds

Written Sun Nov 1 14:26:52 UTC 2026 (from `date -u`). Up to this point only announcement metadata and OKX article pages
have been fetched (research/data/okx_bybit_notice/requests.log). **No aggTrade or kline has been downloaded and no
price or return has been computed.** HOLD (2025-01-01..) is never requested: every event has N < 2025-01-01, and the
2025-26 rows that the list APIs return on their first pages were only paged through (events.py cuts at 2025-01-01;
they are not counted or summarised anywhere).

## Step 1: history availability (done; the stop condition does not trigger for OKX)
- **Robots / docs (logged).** www.okx.com/robots.txt: `Allow: /api/*?`, `/help/<slug>` not disallowed. api.bybit.com and
  bybit-exchange.github.io robots.txt: 404. www.bybit.com: unreachable from this machine (URLError);
  announcements.bybit.com robots.txt: 301 (to www.bybit.com), so no Bybit article page is fetched. Docs read: OKX
  docs-v5 "Get announcements" (public, 5 requests / 2 s per IP, 20 rows / page; `pTime` = "actual time the
  announcement was first published", ms; `businessPTime` = "time displayed on the page"); Bybit v5 "Get Announcement"
  (`dateTimestamp` = "timestamp that author fills", `publishTime` = "published timestamp"). Requests at >= 0.6 s per host,
  plain UA `research-script`, no key, no e-mail. No 403 / 418 / 429.
- **OKX** (164 pages of all types, 3,266 rows; 53 pages of `announcements-new-listings`):
  - Rows posted before the March 2023 help-centre migration have `pTime` = the migration time (2023-03-03 or
    2023-03-21) and `businessPTime` with whole, non-round seconds (e.g. 2021-03-18 02:50:59): the old CMS post time.
    From ~2023-03-22 on, `businessPTime` is rounded to the minute (display time) and `pTime` carries ms.
  - Listing posts 2020-01..2023-03 sit in three types (`new-listings` to 2021-08, `others` 2021-09.., perpetual
    listings in `trading-updates` 2020-21). 2022 is thin (few spot listings of coins already on a Binance perp).
- **Bybit** (`new_crypto`, 92 pages, 1,826 rows): history starts 2022-06-01. `dateTimestamp` has seconds, but 50 %
  of the rows sit at second 00 (author-filled, often a scheduled time). `publishTime` exists only from 2024-03-11 and is
  spread from -18 h to +165 d around `dateTimestamp` (republish / edit time), so it is not used as N. **Bybit has no
  IS history**; its events fall in VAL only (2023-24) and cannot carry IS.

## Event definition (events.py, starts.py; frozen)
- A post that announces a new spot pair or a new perpetual on OKX or Bybit for coin X, 2020-01-01 <= N < 2025-01-01.
  Excluded by title: delistings, tick-size / tier / funding / price-limit adjustments, margin / earn / staking / loans
  only, dual investment, copy trading, leveraged tokens, launchpad / launchpool / votes, convert, TradFi / equity,
  pre-market, futures expiries, promotions / terms / airdrops, deposit / withdrawal / mainnet notices, delays.
- X = the tickers in the title (for OKX "List Perpetual for A/B" only the coins after "Perpetual for"; for a Bybit
  "X/USDT -- prize pool of Y" title only X). X must map to a Binance USDT-M perp (X or 1000X + USDT) that traded >= 7 d
  before N and through N + 1 d (perps.py, copied from round 65 A unchanged). BTC, ETH and stablecoins excluded.
- Same coin within the previous 24 h (any venue): later event dropped (overlapping windows; 4 rows).
- **Stamp N.** OKX: `pTime` when |pTime - businessPTime| <= 10 min; else `businessPTime` if pTime is a migration
  artefact (pTime - businessPTime > 1 d) and businessPTime has non-zero seconds; else dropped (ambiguous). Bybit:
  `dateTimestamp`.
- **Stated start S** (starts.py): OKX: the earliest trading / listing / enable time stated in the article body in
  (N, N + 24 h] (the clause naming the coin preferred; deposit / withdrawal times ignored). Bybit: a time stated in the
  title. **Exit X = S if found, else N + 60 min.**
- Counts (after dedupe): **128 events**. IS (OKX only) 60 on 41 notice days (2020: 34, 2021: 26). VAL 68 on 54 days
  (OKX 2022: 4, 2023: 11, 2024: 31; Bybit 2023: 10, 2024: 12). Stamps: OKX businessPTime 70, OKX pTime 40,
  Bybit dateTimestamp 22. Exits: S from the body / title for ~70, N + 60 min for the rest. Hold up to 20 h.

## Stamp check (computed after this file, from Binance aggTrades; reported per venue and stamp source)
- r(t) = ln(alt_t / alt_ref) - ln(BTC_t / BTC_ref), price = last aggTrade at or before t, ref = N - 60 s (as A2).
- Path: median / quartiles / mean of r(t) at t - N in {-300, -60, -30, -10, -5, -2, -1, 0, +1, +2, +3, +5, +10, +20,
  +30, +60, +120, +300} s, per era and per stamp source. The -300 s point uses the ref N - 360 s (pre-stamp drift).
- Burst onset (a): first alt trade in [N - 300 s, N + 300 s] with r >= +1 % (A2 used +2 %; listings of coins that
  already trade on Binance are expected to move less; +2 % also reported). (b) A2's 1 s trade-count burst
  (>= max(10, 10 x median count over [N - 600, N - 60 s])). Onset < 0 = the burst leads the stamp.
- If the median path shows no move within +-60 s of N in an era / stamp source, the stamp cannot be confirmed for it
  and that is reported (the rule is still evaluated as declared, the stamp check does not select events).

## Rule (A2-D5L frozen; analyze.py `trade` copied unchanged except the exit time)
- **O2-D5S: long the alt USDT-M perp, short BTCUSDT perp, equal notional, each leg at its first aggTrade >= N + 5 s;
  exit each leg at its first aggTrade >= X** (X = S or N + 60 min).
- Costs as A2: 20 bp (4 taker fills x 5 bp) + slippage on each fill = half the median 1 s range over 1 s bins with
  trades in the 60 s from the fill + real funding at stamps in (entry, exit] (local funding files, else public
  fapi fundingRate, logged). x1.5 stress: 30 bp + 1.5 x slippage. One step late: entry at N + 10 s.
- Diagnostics (reported, not selectable; they enter the max-over-cells null): D2-S, D10-S, D30-S, D5-5m (exit N + 5 min),
  D60-S. Venue split (OKX / Bybit) and kind split (spot / perp) are descriptive only.
- t clustered by notice day (A2's clt). Years: IS 2020, 2021; VAL 2022, 2023, 2024.

## Random benchmark (declared)
- Same coin, same calendar month, data.binance.vision monthly 1m klines (USD-M futures, alt and BTCUSDT): entry at a
  random minute open, hold = the event's hold rounded to whole minutes (>= 1), gross r (alt - BTC); the whole hold
  outside [N - 1 d, N + 1 d]. 1,000 draw sets of one draw per event; percentile of the event gross mean. Max-over-cells:
  the same draws scored with each cell's hold and cost, max day-clustered t per set, 95th percentile reported.
  (A2 drew random seconds from the event day; holds here reach 20 h, so the day file is too short.)

## Data (pulled after this file)
- data.binance.vision `futures/um/daily/aggTrades/<SYM>/<SYM>-aggTrades-<day>.zip`: each event's alt and BTCUSDT on
  the UTC days that hold N - 10 min .. N + 30 min and X - 10 min .. X + 5 min (133 alt files, 97 BTC days, all
  <= 2024-12-31). Each zip streamed to research/data/okx_bybit_notice/tmp/, parsed with `python -I`, deleted; kept
  (npz/): trades in the windows only. Two processes (alt, BTC) in parallel.
- `futures/um/monthly/klines/<SYM>/1m/<SYM>-1m-<YYYY-MM>.zip` for the event months (random benchmark only), kept as
  compact npz (open time, open), zips deleted.
- Every request logged in research/data/okx_bybit_notice/requests.log; >= 0.3 s per request to data.binance.vision,
  back off on 418 / 429 / 503, 403 = stop.

## Power arithmetic (before any return)
- HOLD pace: the 2025-26 event count is not looked at. The pace is taken from 2024, the only year with both venues'
  modern stamps: 43 events in 2024 -> **n_HOLD ~ 43 x 22 / 12 ~ 79**. LIVE needs VAL SR per trade >= 3 / sqrt(79) = 0.34.
- VAL t >= 1.5 with 68 events on 54 days needs SR ~ 0.2 (less if multi-coin days are correlated).
- IS t >= 2.5 with 60 events on 41 days needs SR ~ 0.39 (more with same-post correlation); DEMO's 2.0 needs ~0.31.
- Prior: the coin already trades on Binance and usually on other major venues; an OKX / Bybit listing adds a venue,
  not access for a new retail pool as Upbit KRW does. 2020-21 OKX perpetual listings are mostly large caps (ADA, LINK,
  XLM, ATOM). Expect a small jump (tens of bp) if any; after 20 bp + slippage the rule likely fails. Positive is
  possible for mid-cap spot listings in 2020-21 (OKX was a top-3 spot venue then).
