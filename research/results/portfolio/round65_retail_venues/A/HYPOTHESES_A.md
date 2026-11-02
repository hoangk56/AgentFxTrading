# Stream A (round 65) hypotheses: chase the Upbit KRW-listing announcement on Binance perps

Written Sun Nov 1 11:32:29 UTC 2026 (from `date -u`). At this point the event list and the actual KRW trading
start L of each event were built (notice bodies and Upbit 1m candles only). **No Binance price, return or funding
has been requested or computed yet.** HOLD (2025-01-01..) is never requested, loaded or counted: every series is cut
at ts < 2025-01-01, and the notice list is filtered to first_listed_at < 2025-01-01 UTC at load.

## Mechanism
Upbit posts a KRW-market listing notice, and the KRW market opens minutes to hours later. Korean retail buys the
coin on Upbit at the open (round 64 K2: the alt gains +21.5 % vs BTC between L - 24 h and L + 1 h). Arbitrageurs
and fast traders pre-buy on global venues as soon as the notice is out, and keep buying while the Upbit KRW price
sits above the global price after the open. So the Binance perp should rise against BTC from the notice into the
first KRW hour. **Side fixed before data: long the alt USDT-M perp, short BTCUSDT perp, equal notional.**

## Data
- Notices: stream W's list pages (research/data/upbit_notices/raw/list_all, read-only), 2020-01-01..2024-12-31
  UTC. 78 KRW-titled 거래 notice bodies fetched from api-manager.upbit.com/api/v1/announcements/<id> into
  research/data/upbit_announce/raw/detail (>= 1.5 s apart; two 429s, backed off and retried; no 403).
- Two 2020 KRW opens (VET 2020-04-07, SRM 2020-10-15) have no 거래 notice in the list, only the "원화마켓 오픈
  이벤트" notice. That notice's first_listed_at is used as N (flag src=event). Declared here, before prices.
- L = the first Upbit KRW 1m candle (api.upbit.com quotation API, robots.txt 404). In every 2022-24 event with a
  stated start time, L = stated start + 5 min (the first 5 minutes are buy-restricted, so the first trade comes when
  buys open). For delisted KRW markets (404): STG and BONK use stated + 5 min; MATIC uses SOL's L (same notice, same
  markets); SRM has no stated time and no candles, so **SRM is dropped** (L unknown).
- Events: coins whose notice body puts them on the KRW market (table / market lines / prose), not stablecoins,
  whose Binance USDT-M perp traded from >= 7 d before N (W/code/perps.py logic, copied unchanged; BEAM -> BEAMXUSDT).
  Re-listings: none found (no KRW candle before N in any event with candles).
- Prices: Binance fapi 1m klines via A/code/k2rule.py (K's coord copy, only the log folder changed to
  research/data/upbit_announce/), funding from local files else fapi fundingRate (same function).

## Events (A/notice_events_L.csv)
| era | events | notice days | lag N -> L (median) | eligible for exit-at-L cells (L - fill >= 5 min) |
|---|---|---|---|---|
| IS 2020-21 | 12: VET, LINK, XTZ, DOT, DOGE, AXS, SOL, MATIC, 1INCH, AAVE, ALGO, NEAR | 9 | ~5 min | 5 (VET, SOL, MATIC, 1INCH, AAVE) on 3 days |
| VAL 2022-24 | 32 (2022: 3, 2023: 9, 2024: 20) | 32 | ~3 h | 32 (STG ~20 min is the shortest) |

In 2020-21 Upbit mostly posted the notice when the market opened (lag 4-5 min), so a notice-chasing entry is
already at or after L in 7 of 12 IS events.

## Rule and grid (6 cells, declared now)
- Entry: both legs at the close of the fapi 1m bar that starts at floor_minute(N) + E, E in {1, 5, 15} min
  (k2rule.px; fallback up to 4 later minutes). The fill is therefore at N + E .. N + E + 1 min.
- Exit X in {L, L + 1 h}:
  - X = L: close of the 1m bar starting at L - 1 min (the price at the KRW open). An event enters an exit-at-L cell
    only if L - entry fill >= 5 min; others are not traded in that cell (counted).
  - X = L + 1 h: close of the 1m bar starting at L + 60 min.
- Cells: A1-L, A5-L, A15-L, A1-L1h, A5-L1h, A15-L1h. **A1 is a latency race** (a bot that reads the notice within
  a minute competes with the fastest arbitrageurs); a result counts only if the A5 and A15 cells carry it.
- Price leg: (alt_x / alt_e - 1) - (BTC_x / BTC_e - 1). Funding: long alt pays its funding, short BTC receives
  BTC's, at the real stamps in (entry + 1 min + 30 s, exit + 1 min + 30 s] (k2rule.funding).
- Costs: 42 bp per trade as K2 (4 taker fills x 5 bp + alt half-spread 10 bp x 2 + BTC half-spread 1 bp x 2).
  Robustness: costs x1.5 (63 bp); one step late = entry E + 5 min.
- Cell choice: by IS t among the 5 / 15 min cells; checked on VAL unchanged. t clustered by notice day (k2rule.clt).
  Max-over-cells: 6 correlated cells; I report the best IS t against that.
- Random benchmark (gross, on fapi 1m, exact same hold per event):
  - (a) same coin, random start minutes in four 25 h windows 30-180 d before N;
  - (b) up to 8 other perps alive at N, over the same entry / exit minutes.
  - Percentile of the event mean against 500 draw-set means (one draw per event per set).
- Descriptive split (no cell): alt vs BTC on Binance from N - 24 h -> N, N -> N + 1 min, entry -> L, L -> L + 1 h.
- Chained book "A then K2" (information only, K2 is registered): long from the A entry to K2's own entry fill
  (L_hour + 61 min, L_hour = floor_hour(L) as K2 defines L), then k2rule.trade (short 72 h). Sum of both nets.

## Power arithmetic (before any return)
- LIVE needs IS t >= 2.5, VAL t >= 1.5, and HOLD power = SR per trade (VAL) x sqrt(n_HOLD) >= 3.
- VAL pace 32 / 3 yr = 10.7 events a year, so n_HOLD ≈ 10.7 x 1.83 ≈ 19.5. **LIVE needs VAL SR per trade >= 3 /
  sqrt(19.5) = 0.68.** At 30 events a year in HOLD (n ≈ 55), SR >= 0.40.
- VAL t >= 1.5 with n = 32 independent days needs SR >= 0.27.
- **IS L + 1 h cells**: n = 12 on 9 days. IS t >= 2.5 needs SR >= ~0.75-0.85; DEMO's t >= 2.0 needs SR >= ~0.6.
- **IS exit-at-L cells**: n = 5 on 3 notice days. A clustered t with 3 clusters has 2 degrees of freedom, and t >= 2.5
  would need SR >= 1.1 per trade. **LIVE and DEMO are not credibly reachable for the exit-at-L cells**: whatever
  they show in IS is reported, but the IS bar is a formality on 3 days. The test that can carry weight is VAL.
- Prior: K2's +21.5 % run-up from L - 24 h to L + 1 h. For 2022-24 the notice sits ~3 h before L, so the part of the
  move after N + 5 min is the question. If arbitrageurs move Binance within the first minute, A5 / A15 will be small.
