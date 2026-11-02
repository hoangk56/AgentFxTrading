# Stream U hypotheses: Korean retail rush without a listing (Upbit KRW volume-share shocks)

Written 2026-11-01 10:38 UTC (`date -u`), before any share, return or trade statistic was computed. Read so far: the
round 65 brief, stream K's report / hypotheses / code (kdata, k2, k2_pumpctrl, k2rule), file headers of the local data
(Upbit m240 columns t,o,h,l,c,krw,vol; Binance 1h columns t,o,h,l,c,vol,qvol,n) and stream K's pull status list. Not
read: the HOLD section of K's prereg or anything else under K/coord/hold/ except k2rule.py. HOLD (2025-01-01..) is
never loaded: every series is cut at ts < 2025-01-01 at load; signals need T + 1 h + hold + 5 min < 2025-01-01.

## Mechanism
Same behavioural flow as K2 (Korean retail attention overshoots and fades), but on coins already trading in KRW. When
a coin's Upbit KRW traded value over the last 24 h is a much larger share of its Binance perp quote volume than usual
for that coin, Korean retail is chasing it (KRW buying is mostly retail; Binance perp volume is the global baseline).
Retail chasing pushes the price above value; when the chase ends the coin fades against BTC. Stream K's post-hoc
control showed that shorting a generic alt pump (24 h run-up >= 10 / 20 %) LOSES on the mean (squeeze tails), so the
claim tested is that the Korean share adds what the price pump alone does not.
**Side fixed now: short the alt perp, long BTCUSDT perp, equal USD notional.**

## Data (local, read-only; no new Upbit pull)
- Upbit KRW 240-minute candles of stream K (research/data/upbit/m240/<COIN>.csv, `krw` = KRW traded value, buckets
  start 00/04/.../20 UTC). Universe: K's map (research/data/upbit/raw/map_perp.json) minus BTC (hedge), USDC
  (stablecoin) and BTT (K's name-collision guard).
- Binance perp 1h klines with qvol (USDT quote volume) from the local files kdata.b1h searches (earliest-starting
  file), 1000x perps rescaled for price (qvol is in USDT, no rescale needed).
- Funding: local files as kdata.funding; else public fapi fundingRate (logged).
- Fills: BTCUSDT perp 1m from K's btc_1m.npz (data.binance.vision), alt perp 1m closes from K's alt_1m cache when
  present, else public fapi 1m klines via a copy of k2rule.px in U/code/ (pricing identical) logging to
  research/data/upbit_vol/requests.log, >= 0.3 s between requests, back-off on 418/429/503, 403 = stop.

## Signal (4h bucket b ends at T)
- `KRW24(T)` = sum of the Upbit `krw` of the 6 buckets ending at T (all 6 must exist).
- `Q24(T)` = sum of Binance perp qvol of the 24 1h bars ending at T (>= 22 present).
- Log share `S(T) = ln(KRW24) - ln(Q24)` (KRW / USDT; the FX level cancels in the deviation below to within the 30-day
  FX move, a few %).
- Deviation `D(T) = S(T) - median(S over the 180 buckets ending at T - 24 h)` (the trailing 30 days excluding the
  current 24 h window; need >= 120 valid).
- Liquidity floor: `KRW24 >= 1e9 KRW` (~0.75 M USD).
- Exclusions: buckets within 30 days after a coin's first Upbit KRW candle (when K's status says `history_start`) or
  after its K2 listing time L (k2_events.csv); the trailing-median requirement also drops the first ~30 days of a
  Binance perp.
- Run-up `RU(T)` = (alt / BTC) Binance 1h close at T over the same at T - 24 h, minus 1.
- Event: `D(T) >= ln(k)` [and `RU(T) >= +10 %` in the filtered cells]; one event per coin per 7 days (a new event of
  that coin in that cell needs T >= previous event T + 7 d).

## Trade
Entry at the close of the 1m bar starting at T + 1 h (fallback up to 4 later minutes), both legs; exit at entry + H
(same fallback). Late checks: entry at T + 1 h + 5 min and at T + 2 h.

## Grid (12 cells, declared now)
k in {2, 4, 8} (share >= 2x / 4x / 8x its own trailing-30-day median) x run-up filter {none, RU >= 10 %} x
H in {24, 72} h. The cell is chosen on IS (highest IS t), then checked unchanged on VAL. Max-over-cells null: with 12
highly correlated cells the expected max |t| under the null is ~1.8-2.2; reported with the best cell.

## Costs
As K2: 42 bp round trip (4 taker fills x 5 bp + alt half-spread 10 bp x 2 + BTC 1 bp x 2) plus real funding of both
legs at the stamps in (te + 1 min + 30 s, tx + 1 min + 30 s]. Robustness: costs x1.5, the two late entries.

## Eras and statistics
IS 2020-01-01..2021-12-31 (Upbit data from 2019-12-20 but the 30-day trailing window means signals start ~2020-01-20),
VAL 2022-01-01..2024-12-31. Net bp per trade, t clustered by entry day, years positive (2020..2024), median, sd,
per-trade Sharpe, worst / best, result without the best trade.

## Benchmarks (gross on 1h closes, entry at the close of the 1h bar starting at T + 1 h, as K's random_k2)
1. Random timing: for each event, the same coin at a random 4h boundary in the same calendar quarter (all exclusions
   applied), same hold; 500 draws of the whole set; percentile of the actual mean.
2. Generic-pump control (same-size pumps without the Korean share): for each event, a random draw from the pool of
   (coin, 4h boundary) observations of the same era with `D(T) < ln(1.5)` (no Korean rush) whose run-up RU(T) is among
   the 50 pool observations nearest the event's run-up; same hold; 500 draws; percentile of the actual mean. This is
   the test of "does the Korean share add anything over the price pump".
Bars: DEMO needs >= 90 % on the random benchmark; LIVE >= 95 %. I also require the cell to beat the generic-pump
control at the same level, since that is the stream's question (reported either way).

## Power arithmetic (before computing)
HOLD ~1.83 years. LIVE needs `S x sqrt(n_HOLD) >= 3`, S = VAL net per-trade Sharpe, n_HOLD = VAL events / yr x 1.83.
- 24-72 h alt-vs-BTC sd after a pump: ~800-1500 bp (K2: 1069 / 1666 bp in VAL).
- k = 2: guess 150-400 events / yr in ~90 coins (7-day cooldown caps a coin at 52 / yr) -> n_HOLD ~270-730 -> S >=
  0.11-0.18 -> net >= ~100-250 bp per trade. Day clustering (Korean frenzy days hit many coins together) cuts the
  effective n, so the real bar is higher.
- k = 8 with run-up filter: guess 10-40 / yr -> n_HOLD ~20-75 -> S >= 0.35-0.67 -> net >= ~400-1000 bp: LIVE out of
  reach; DEMO at best.
- So LIVE is plausible only at k = 2-4 and only if the fade is > ~150-250 bp net per trade; prior: the generic-pump
  control loses, and K1 showed the Korean side does the moving, so "none" is the most likely outcome.

## Biases (declared)
- Upbit current-only market list: delisted coins are missing. Coins delisted after a pump-and-dump were the strongest
  fades, so the short is probably understated (conservative).
- Withdrawal suspensions / warning designations on Upbit isolate the KRW market and can create a share spike without
  any Binance flow (K1's IOTA / KAVA / WAVES). These stay in (not identifiable in this data); reported by coin.
- Binance perp volume is not spot volume; perp volume rises with the global pump too, so D measures the Korean share
  beyond the global reaction (intended).
