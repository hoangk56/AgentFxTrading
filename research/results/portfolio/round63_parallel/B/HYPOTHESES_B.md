# Stream B hypotheses: intraday mean reversion of the Binance perp-spot basis on altcoins

Written 2026-10-31 14:49 UTC (from `date -u`), before any basis, return or event count was computed. Only the
point-in-time universe size (from perp 1d volumes, no returns) was counted before this file.

## Mechanism
The USDT-M perp and the Binance spot pair of the same altcoin are the same asset; the funding mechanism and
spot-perp arbitrageurs pin the log basis b = ln(F / (fac x S)) near a slowly moving level (it tracks expected funding).
Short-lived dislocations happen when one leg takes a burst of one-sided flow (perp liquidation cascades, leveraged
longs piling into the perp, spot listings / unlocks on the spot book) faster than arbitrage capital moves. Arbitrage
capital is limited intraday on alts (margin per venue, spot inventory, borrow limits), so the convergence takes hours.
The trade is a convergence, not a direction: short perp / long spot when the perp is rich (no borrowing needed),
long perp / short spot when cheap (needs margin borrow of the alt). Rounds 58 (multi-week carry, = cash rate since
2025) and 62 (trading through funding stamps) did not trade intraday basis dislocations.

## Data (pull 2019-12-24..2024-12-31 23:59:59 UTC only; HOLD never requested)
- Universe: point-in-time top-60 USDT-M perps by trailing 30-day perp quote volume (perp_1d), listed >= 60 days, with a
  Binance spot pair live that day (spot_first.csv), stablecoins / BTCDOM / PAXG excluded, BTCUSDT and ETHUSDT excluded
  (altcoins only). The universe of day d is taken from day d-1 (no same-day volume). 246 symbols ever in it 2020-24
  (incl. delisted). Code `code/universe.py`, list `universe60.csv`.
- Perp 1h klines (fapi/v1/klines) and spot 1h klines (api/v3/klines) for each symbol from 8 days before its first
  universe day to 2 days after its last (capped at 2024-12-31 23:59:59). 1000X perps map to spot X x factor.
- Funding stamps: research/data/binance/funding/ (213 of 246); the other 33 pulled from fapi/v1/fundingRate into
  research/data/binance_basis/funding/.
- Fed funds (research/data/rates/DFF.csv) for the cash rate on the spot leg.
- Premium index klines: not used for the primary (it is perp vs a multi-venue index, not the tradeable Binance spot
  pair); may be pulled for a subsample as information only.

## Signal and rule (fixed before data)
- Hourly basis b_h = ln(F_close / (fac x S_close)) for bars with the same open time; a bar counts only if both legs
  have >= 20 trades in the hour (stale spot closes otherwise fake a basis).
- Reference m_h = median of b over the previous 168 hours (h-168..h-1), needs >= 120 valid hours.
- Deviation d_h = b_h - m_h. Event (rich side, primary): d_h > k. Event (cheap side, secondary): d_h < -k.
- Entry at the open of bar h+1 on both legs, 1 unit notional per leg. One open trade per coin; signals on a coin while
  it is held are ignored. Any number of coins at once (user lifted position limits).
- Exit: at the first close c >= h+1 with (b_c - m_h) <= d_h / 2 (rich; mirror for cheap; median frozen at entry), the
  trade exits at the open of bar c+1; time stop at the open of bar h+1+H. If either leg's data ends (delisting), exit
  at the last available close of that leg.
- P&L per unit notional (rich): (S_x / S_e - 1) - (F_x / F_e - 1) + funding received on stamps T with E < T <= X
  (short perp receives +rate) - costs. Cheap side: the mirror, minus the borrow cost.
- Grid (12 cells): k in {30, 60, 100} bp x H in {4, 24} h x side {rich (primary), cheap (secondary)}. The cell is
  chosen on IS (highest IS net t among cells with IS net > 0), then checked on VAL unchanged. The max-over-cells null
  is reported (max t over the 12 cells in each random replication).

## Costs
- Taker, 4 legs: spot 0.10 % x 2 + perp 0.05 % x 2 = 30 bp, plus half-spread per leg per side 4 x hs, hs = 3 bp for
  universe rank < 10, 5 bp otherwise (round 58 convention) -> 42-50 bp per round trip. Costs x1.5 check.
- Cheap side: spot borrow 40 %/yr pro rata over the hold (Binance cross-margin alt rates are typically 5-20 %/yr and
  spike in squeezes; availability is NOT modelled, so the cheap side can be DEMO at best unless availability is
  verified by the user).
- Cash rate: Fed funds x hours held / 8760 on the spot notional subtracted (graded on excess over cash, round 58 lesson).
- Maker variant (information only, never graded): perp 0.02 %, spot 0.075 %, no half-spread -> 19 bp.
- One step late: entry at the open of bar h+2 (exit rule unchanged).

## Random benchmark
For every actual trade (coin, hold length L hours): a random entry hour on the same coin, same era, hour valid and coin
in universe, same side rule (rich -> short perp / long spot), held L hours, same costs and funding. 1,000 replications;
"beats random" = share of replications whose mean net is below the actual mean. Max-over-cells: per replication the
max t over the 12 cells.

## Statistics and bars
Net per trade in bp, t clustered by entry UTC day, per-year table (2020..2024), share of years positive. LIVE: IS t >=
2.5, VAL t >= 1.5, >= 2/3 of years positive, beats >= 95 % random, HOLD power at VAL size >= 3, positive at costs x1.5
and one step late. DEMO: IS t >= 2.0, VAL net > 0, beats >= 90 % random.

## Power arithmetic (before data)
- Cost wall: 42-50 bp taker. An exit at the halving captures about d/2 when it triggers, so the gross capture of a
  k-event is ~k/2 plus the overshoot of the first close past entry. k = 30 (capture ~15-25 bp) and k = 60 (~30-45 bp)
  cannot clear the taker wall unless the reversion overshoots; only k = 100 (~50+ bp) can. Expect k 30 / 60 to fail
  taker costs; they are kept as a dose-response check.
- HOLD 2025-01..2026-10 ~1.8 years. Per-trade bar: power = SR_trade x sqrt(n_HOLD) >= 3. If VAL gives E events / yr
  (independent), n_HOLD = 1.8 E: E = 200 -> SR >= 0.158; E = 1,000 -> SR >= 0.071; E = 5,000 -> SR >= 0.032.
- Clustering: basis dislocations bunch on crash / squeeze days across coins. The binding power is the day-level one:
  daily-book (sum of trades by entry day) Sharpe x sqrt(HOLD event-days) >= 3. With ~150 event-days / yr (~270 in HOLD)
  the event-day Sharpe needs >= 0.18 (annual Sharpe ~2.2 if every day is an event day). Both powers are reported;
  the smaller one is graded.
- Which bar each cell can reach: k 30 / 60 neither bar on taker costs (expected net < 0); k 100 rich side LIVE only if
  its per-trade Sharpe after costs is >= ~0.1 at a few hundred events / yr and the effect is not concentrated in a few
  days (2020-03, 2021-05, 2022-05 LUNA / 2022-11 FTX); cheap side DEMO at best (borrow availability).

## Tails reported
Delistings (forced exits at the last bar, counted), max adverse move of the perp leg during the hold (share of trades
with an adverse move > 25 % / 50 %, which would liquidate a 3x / 2x perp margin unless cross-collateralised), results
with 2020-03, 2021-05-19, 2022-05 (LUNA) and 2022-11 (FTX) removed.

## Addendum 1 (written 2026-10-31 14:53 UTC, before any event count, trade or return was computed)
A loader smoke test on the first 10 downloaded coins (distribution of d only) showed 1000PEPEUSDT with a 1st / 99th
percentile deviation of -84 / +118 bp while the others sit within +-12..28 bp: spot PEPEUSDT trades at ~1e-6 with an
8-decimal quote, so one spot tick is ~1 % of the price and the "basis" is tick bounce, not a dislocation (and not
tradeable at the 3-5 bp half-spread assumed). Declared filter, applied to signal and entry bars on both legs: estimate
the tick of each leg per 30-day block as the smallest positive gap between distinct o / h / l / c prices in the block;
an hour is valid only if tick / median price <= 5 bp on both legs (a one-tick spread then fits the cost model).
Nothing else changes.
