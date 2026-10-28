# Round 31, stream C: hypotheses (crypto non-price data -> BTCUSD / ETHUSD at IC, hours to 5 days)

Written 2026-10-27 18:22-18:40 UTC (`date -u` 18:22:18 at the start), **before any return was computed or any
signal was joined to a price**. Loaded so far: IC BTCUSD/ETHUSD M1 coverage, spreads and unconditional return sd per
era (no signal), the CoinMetrics catalog and BTC/ETH daily series to 2024-12-31, samples of Binance Vision metrics
files, Bitfinex probe pages. Data still downloading (Bitfinex positions and liquidations, Binance metrics and
liquidation snapshots) is described from the probe pages only.

## Sources and the bar each one can meet

| series | source (URL) | real start (probed) | point-in-time? | eras it allows | best bar possible |
|---|---|---|---|---|---|
| exchange inflow / outflow / exchange supply, daily (FlowInExNtv, FlowOutExNtv, SplyExNtv), BTC and ETH | community-api.coinmetrics.io/v4/timeseries/asset-metrics (community, no key) | BTC 2011-04-24, ETH 2015-07-30 | **no**: every row carries `status-time` 2026-04 (the whole history was recomputed in April 2026 with today's exchange-address labels; addresses found later are back-filled). A backtest on it uses labels nobody had at the time | PRE 2012-2017-08 (mid only, CoinMetrics PriceUSD 00:00 UTC), IS 2017-09..2021 (IC), VAL 2022-24 | numbers can meet LIVE or DEMO, but a pass is **not registrable** without point-in-time data (paid, or forward-only from today): information / user decision |
| miner flows (FlowMinerOut...), stablecoin exchange balances | CoinMetrics | not in the community catalog (403 / absent) | - | - | user decision (paid) |
| stablecoin supply (SplyCur of USDT, USDC) | CoinMetrics | 2014 / 2018 | yes-ish | - | **excluded**: issuance = round 7 C / round 12 C |
| market open interest, liquidations by exchange | CoinMetrics market-openinterest / market-liquidations | 403 (not community) | - | - | user decision (paid) |
| Bitfinex margin positions, total longs and shorts (pos.size 1m, tBTCUSD, tETHUSD) | api-pub.bitfinex.com/v2/stats1/pos.size:1m:tBTCUSD:{long,short}/hist | 2016-11-06 21:12 UTC, 1-minute | yes (logged live) | IS 2017-09..2021 (IC), VAL 2022-24 | LIVE possible |
| Bitfinex liquidations (all pairs, per position) | api-pub.bitfinex.com/v2/liquidations/hist | 2019-07-28 | yes | IS 2019-08..2021 (2.4 of 6 years), VAL | DEMO at most (truncated IS); LIVE would need the user to accept a short IS |
| Binance USDT-M futures metrics, 5-min: open interest (sum_open_interest, _value), top-trader account and position L/S ratios, global account L/S ratio, taker L/S volume ratio | data.binance.vision/data/futures/um/daily/metrics/{BTCUSDT,ETHUSDT}/ | BTCUSDT 2020-09-01 (5-min rows; the first days have duplicated rows) | yes | IS = 2020-09..2021-12 only (16 months of the 6-year IS), VAL 2022-24 | DEMO route / information: it cannot meet "IS 2016-21" |
| Binance coin-margined liquidation snapshots (BTCUSD_PERP, ETHUSD_PERP) | data.binance.vision/data/futures/cm/daily/liquidationSnapshot/ | 2023-06-25..2024-10-14 (then stops); no USDT-M snapshots at all | yes | VAL only | information only |
| taker buy/sell ratio | Binance metrics | 2020-09 | - | - | **excluded**: taker order flow = round 4 |
| funding | Binance | - | - | - | **excluded**: rounds 4 / 9 |

Round 3 already tested a *price-only* liquidation-cascade fade (\|z\| > 3-5 hourly moves; negative after fills and
2018-20 spreads). The liquidation rules below condition on measured liquidations or open-interest drops instead, so
they are new; the price-only version is the natural control and is reported next to them.

## Prices, costs, timing (all rules)
- Returns: IC M1 (research.m1.load), cut ts < 2025-01-01 at load. BTCUSD from 2017-08-28, ETHUSD from 2017-09-25.
  IC crypto was closed Fri 17:00 -> Sun 17:05 New York until 2024-04; a signal produced while IC is closed is
  **skipped** (not queued). The price at time X = close of the IC bar labelled X-1 min, stale by at most 10 min,
  else no trade. Exit at the last IC quote at or before the exit time (a hold that would end inside the weekend
  closure exits at the last quote before it; never later than 5 days after entry).
- Fill: data known at time t -> entry quote at t + 1 min. Checks: both quotes +1 min; half spreads x1.5.
- Cost: half the actual IC spread at entry + half at exit (buy at ask, sell at bid); no commission on crypto; swap
  per 17:00 New York rollover crossed: **long -5.0 bp, short 0** (x3 on Friday, IC's triple day for crypto).
  Source: research/specs.py SWAPS (BTC long -38.61 USD/unit, short 0; ETH long -1.135, short 0; IC 2026), expressed
  as a fraction of price as round 23 N did (~5 bp a night). I do not compute the fraction from 2025-26 prices (that
  would load HOLD); 5 bp is used for both symbols. Sensitivity: short also -5 bp.
- IC median spreads (pre-2025 data): BTC 2017 30.5 bp, 2018 16.6, 2019 6.8, 2020 3.5, 2021 4.7, 2022 3.1, 2023 3.1,
  2024 2.4; ETH 2017 15.6, 2018 88.6, 2019 253.5, 2020 172.6, 2021 26.3, 2022 17.1, 2023 15.3, 2024 10.1. ETH's IS is
  therefore dominated by cost before 2021; ETH cells are run and counted but expected to fail on IS cost.
- Data lags: CoinMetrics day D (UTC) is complete at ~04:00-05:30 UTC on D+1 (AssetEODCompletionTime 2022-24), so
  daily CoinMetrics rules enter at **08:00 UTC on D+1**. Bitfinex positions: last 1-min value <= clock. Binance
  metrics: rows with create_time <= clock - 5 min. Liquidations: hourly buckets [h, h+1 h), act at h+1 h + 1 min.
- One open trade per rule and symbol (a signal during a trade is ignored), so holds never overlap.
- t clustered by UTC entry day. Random-entry control: 200 seeds, same trade count per era and the same hold, entries
  at random IC-open times on the rule's clock (08:00 UTC weekdays for daily rules, every 4 h for 4-h rules, any IC
  minute for event rules), side = the rule's side function (sign part, no threshold) evaluated at the random time;
  report the percentile of the real mean net.
- Momentum control (rounds 4 and 24 found crypto "signals" that were momentum): for each daily family, an OLS of the
  next-h return on the signal with the past 1, 7 and 28-day returns as regressors, IS and VAL.

## Power arithmetic (done before building; frontier rule: per-trade net Sharpe x sqrt(HOLD trades) >= 3, HOLD 1.73 y)
Unconditional IC mid return sd (08:00 UTC starts, no signal), IS 2018-21 / VAL 2022-24:
BTC 4 h 191 / 95 bp, 1 d 454 / 297, 3 d 697 / 474, 5 d 861 / 652; ETH 4 h 224 / 133, 1 d 547 / 373, 3 d 885 / 614,
5 d 1144 / 829.

| rule shape | trades / yr | HOLD n | Sharpe needed | net edge needed at the VAL sd (BTC) | at the IS sd |
|---|---|---|---|---|---|
| daily, 1-day hold, every weekday | 250 | 430 | 0.145 | 43 bp | 66 bp |
| daily 3-day hold, non-overlapping | 85 | 147 | 0.25 | 118 bp | 174 bp |
| 5-day hold, non-overlapping | 50 | 87 | 0.32 | 209 bp | 276 bp |
| 4-h hold, one a day | 250 | 430 | 0.145 | 14 bp | 28 bp |
| threshold events, ~30 / yr, 1 day | 30 | 52 | 0.42 | 125 bp | 190 bp |
| threshold events, ~30 / yr, 4 h | 30 | 52 | 0.42 | 40 bp | 80 bp |

Expected sizes: the positioning / flow literature for crypto reports daily predictive slopes of a few hundredths of
an sd per sd of signal (e.g. round 4: funding adds -0.03..-0.25 sd per sd after momentum, never significant). At
0.03-0.05 sd per trade none of these shapes reaches power 3; LIVE needs ~0.15 sd per trade every day or ~0.4 sd per
event. The realistic target is therefore the DEMO bar (IS t >= 2.0, VAL net > 0, >= 90 % random), and LIVE only if
an effect is several times larger than anything seen in crypto here. Cost is not the binding constraint at >= 1 day
for BTC after 2019 (2.4-4.7 bp + 5 bp a night long), it is the binding constraint for ETH before 2021 and for every
4-h rule in 2017-19.

## Hypotheses (side fixed by the mechanism, parameters only from the listed grids, chosen on IS)

### Family X: CoinMetrics exchange flows (daily; not point-in-time, see above). 28 cells
- **X1 net deposits = coins about to be sold.** Mechanism: holders move coins to exchanges to sell them and withdraw
  after buying (the CryptoQuant / Glassnode "exchange netflow" reading). f_D = (FlowInExNtv - FlowOutExNtv) / SplyCur
  for UTC day D; z = (f_D - mean) / sd over D-90..D-1. Rule: z > k -> **short**, z < -k -> **long**, enter 08:00 UTC
  D+1, hold h days. Grid k in {1.0, 1.5, 2.0} x h in {1, 3, 5}: 9 cells per symbol, 18.
- **X2 gross inflow spike (whale deposit).** g_D = log FlowInExNtv; z over D-90..D-1; z > 2.0 -> **short**, h in
  {1, 3, 5}: 3 per symbol, 6.
- **X3 exchange-balance trend (accumulation).** s_D = log SplyExNtv_D - log SplyExNtv_{D-30}; side = **-sign(s)**
  (falling exchange balances -> long). Every weekday at 08:00 UTC: (a) 1-day hold, (b) 5-day hold non-overlapping:
  2 per symbol, 4. Momentum-confounded by construction; the OLS control decides.
- PRE check (information): the same rules on CoinMetrics PriceUSD (00:00 UTC daily reference) 2012-01..2017-08, mid,
  entry at the D+1 00:00 reference (one day earlier than 08:00 is not possible on daily data; noted).

### Family B: Bitfinex margin positions (point-in-time, from 2016-11). 24 cells
- **B1 crowded leverage, contrarian.** r = log(total longs / total shorts) on Bitfinex (BTC: tBTCUSD; ETH: tETHUSD),
  z of the value at the clock vs the hourly values of the previous 30 days. Clock 08:00 UTC each day IC is open.
  \|z\| > k -> side **-sign(z)** (crowded side gets squeezed / unwinds). Grid k in {1.0, 1.5, 2.0} x h in {1, 3}
  days: 6 per symbol, 12.
- **B2 squeeze fuel.** a = 24-h change of log(shorts), b = 24-h change of log(longs), each z-scored vs the hourly
  24-h changes of the previous 30 days. z_a > k (shorts piled in) -> **long**; z_b > k (longs piled in) -> **short**;
  both -> no trade. Clock 08:00 UTC, k in {1.5, 2.0} x h in {1, 3} days: 4 per symbol, 8.
- **B3 = B1 at hours.** Clock every 4 h (00, 04, ..., 20 UTC), hold 4 h, k in {1.5, 2.0}: 2 per symbol, 4.

### Family N: Binance USDT-M futures metrics (2020-09+, truncated IS: DEMO route / information). 40 cells
- **N1 retail crowding, contrarian.** x = log count_long_short_ratio (global accounts long / short), z vs the 5-min
  rows of the previous 30 days. \|z\| > k -> side **-sign(z)**. Daily clock 08:00 UTC: k in {1.0, 1.5, 2.0} x h in
  {1, 3} days (6 per symbol); 4-h clock with 4-h hold: k in {1.5, 2.0} (2 per symbol). 16 cells.
- **N2 large accounts vs the crowd.** d = z(log sum_toptrader_long_short_ratio) - z(log count_long_short_ratio)
  (top 20 % of accounts by margin, position-weighted, minus all accounts), both z vs 30 days. \|d\| > k -> side
  **sign(d)** (follow the large accounts against the crowd). Daily clock, k in {1.0, 1.5} x h in {1, 3}: 4 per
  symbol, 8.
- **N3 leverage build-up, contrarian on the side that built it.** o = 24-h change of log sum_open_interest, z vs the
  previous 30 days of 24-h changes (5-min rows); p = 24-h change of log(sum_open_interest_value / sum_open_interest)
  (= mark price). z_o > k -> side **-sign(p)**. Daily clock, k in {1.5, 2.0} x h in {1, 3}: 4 per symbol, 8.
- **N4 open-interest flush (forced closing = liquidations).** Every 5-min row: o1 = 1-h change of log OI, z vs the
  previous 30 days of 1-h changes. z_o1 < -k and the 1-h price change < 0 (longs forced out) -> **long**; z_o1 < -k
  and price change > 0 (shorts forced out) -> **short**. Liquidity-provision reversal. Hold 4 h or 24 h; k in {2, 3}:
  4 per symbol, 8. Control: the same events defined on price alone (the \|1-h move\| at the same percentile, no OI
  condition), i.e. round 3's rule on the same timestamps.

### Family L: measured liquidations. 8 cells + 2 information
- **L1 Bitfinex liquidations, reversal after forced flow.** Hourly USD notional of liquidated long positions (amount
  > 0, sold by the engine) and of short positions (amount < 0), BTC = tBTCUSD + tBTCF0:USTF0, ETH likewise, one row
  per position (is_match = 0). Event: hour with long-liquidation notional above the q-quantile of all IS hours with
  data -> **long**; short-liquidation notional above its q-quantile -> **short** (both: skip). q in {0.99, 0.995} x
  h in {4 h, 24 h}: 4 per symbol, 8. Sign convention to be checked on contemporaneous (not forward) prices: long
  liquidations must coincide with falling prices; if the convention is the other way round, the labels flip, the
  side rule does not.
- **L2 Binance coin-margined liquidation snapshots**, 2023-06-25..2024-10-14 (VAL only): L1's rule with the quantile
  of this sample (look-ahead threshold), h 4 h and 24 h, BTC only: 2 cells, information.

### Count and chance
102 registered cells (X 28, B 24, N 40, L 8) + 2 information cells. Expected max \|t\| of 102 independent normal
cells ~ 2.9 (95 % ~ 3.5); within each family I report the best \|t\| against the max of K normals for that family.
Order of work: B and L first (point-in-time, cover IS), then N, then X.
