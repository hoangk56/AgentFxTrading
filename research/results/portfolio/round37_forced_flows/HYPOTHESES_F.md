# Round 37, stream F: hypotheses (perpetual-funding settlement pressure, conditioned on the rate paid)

Written 2026-10-29 09:32 UTC (`date -u`). No funding signal had been joined to any return when this file was written.
What had been computed before this file (signal-only, or unconditional price statistics used as power inputs):
- the funding distribution by year;
- the agreement between venues and between the predicted and the realised rate;
- the IC BTC / ETH unconditional window sd and round-trip cost at the stamp clocks.

Scripts: scratchpad `r37/F/scripts/` (`pull_funding.py`, `signal_stats.py`, `power_inputs.py`). Fetch log:
`r37/F/web/requests.log`. HOLD 2025-01-01..2026-09-24 stays closed: every series was requested with endTime
2024-12-31 23:59:59 UTC, and IC M1 is cut at ts < 1735689600000 at load.

## Sources (fetched 2026-10-29 09:25-09:30 UTC)

| series | span loaded | note |
|---|---|---|
| Binance USDT-M BTCUSDT funding, `fapi.binance.com/fapi/v1/fundingRate` (public, no key) | 2019-09-10 08:00 .. 2024-12-31 16:00, 5,819 stamps, all at 00/08/16 UTC, no gaps | The data.binance.vision monthly zips start only at 2020-01 (2019-09..12 are 404), so the REST endpoint was used for the whole span |
| Binance ETHUSDT funding (same endpoint) | 2019-11-27 .. 2024-12-31, 5,585 stamps | |
| Binance BTCUSDT premium index, hourly klines (`/fapi/v1/premiumIndexKlines`) | 2019-12-24 .. 2024-12-31, 44,036 hours | For the predicted rate |
| Bybit inverse BTCUSD funding (`api.bybit.com/v5/market/funding/history`) | 2018-11-15 .. 2024-12-31, 6,714 stamps (00/08/16) | Extends the signal 10 months before Binance |
| Bybit linear BTCUSDT funding | 2020-03-26 .. 2024-12-31, 5,227 stamps | |
| OKX `/api/v5/public/funding-rate-history` | last ~3 months only | An `after=2021-01-01` request and an `after=2025-01-01` request both return empty. Unusable for history |
| BitMEX (04/12/20 UTC stamps, 2016+) | - | API 403. `public.bitmex.com` serves a wind-down page ("BitMEX ceased trading on 23 September 2026"). Unusable |

## Signal facts that shape the design (signal only, no returns)

- Binance's rate sits at the 1 bp floor most of the time. When the premium is within ±5 bp of the 1 bp interest
  term, the clamp pins the rate there: 32-65 % of stamps by year.
- Large rates are an IS-era phenomenon. Weekday stamps with \|f\| >= 3 bp: 2019 5 %, 2020 19 %, 2021 30 %, 2022
  0.5 %, 2023 1.4 %, 2024 7.3 %. With \|f\| >= 5 bp: 2.1 / 9.9 / 19.2 / 0.3 / 0.3 / 2.5 %. Bybit inverse looks the
  same; it also has 2019 at 26 % (\|f\| >= 3 bp).
- The predicted rate (Binance's formula on the hourly premium closes up to T-1h) correlates 0.83 with the realised
  rate; the last published rate correlates 0.79. For Binance and Bybit inverse at the same stamp the correlation is
  0.57.
- Counts with \|P_pred\| >= 3 bp, all days (IC trades crypto on weekdays only until 2024-04): 2020 215, 2021 351,
  2022 7, 2023 26, 2024 82. With >= 5 bp: 121, 216, 4, 7, 30.

## Unconditional power inputs (IC mid, all stamps, no signal)

| era | window | BTC sd pre / post (bp) | BTC RT cost median (mean) | ETH RT cost median |
|---|---|---|---|---|
| IS 2019-09..2021 | 15 min | 44 / 54 | 4.95 (6.1) | 103 |
| IS | 30 | 60 / 69 | 4.9 (6.2) | 103 |
| IS | 60 | 99 / 97 | 5.4 (6.5) | 104 |
| VAL 2022-24 | 15 | 26 / 32 | 2.9 (3.4) | 12.7 |
| VAL | 30 | 41 / 46 | 2.9 (3.4) | 12.8 |
| VAL | 60 | 63 / 61 | 2.9 (3.5) | 12.9 |

## How this differs from what earlier rounds ran (cells dropped)

- **Round 3** (flow_search_2026-09-27.md, "Crypto perpetual-funding times"): unconditional mean returns at the
  00/08/16 UTC clock (and BitMEX 04/12/20), <= 3 bp, no sign kept.
  - Because f > 0 at 76-93 % of stamps, an "all stamps, side = -sign(f)" cell is nearly that unconditional short
    into the stamp. **Dropped.**
  - The all-stamps dose slope below is reported for the mechanism only, not as a cell.
- **Rounds 4 / 9**: funding level (7-day mean, top decile, regressed with momentum) as a predictor of 1-5 day returns.
  That construction was multi-day and contrarian; mine is a minutes-long window around the stamp itself. No cell is
  shared.
- **Round 12 K4**: on Fridays, fade the 07:00-08:00 move after 08:00, with Mon-Thu as the control. The side comes
  from the prior price move, and the clock is the Deribit expiry. Mine takes the side from the funding rate at every
  stamp, with no price input. Round 12 K5 (CME BRR window, unconditional) is the one F2 conditions below.
- **Round 31 C** (Binance OI, long/short ratios, liquidations, 4 h - 5 d) and **round 33 K** (Bitfinex margin
  funding, daily): no stamp clock, and not the perp funding. No overlap.

## Mechanism and side (fixed here, from the brief's mechanism, not from data)

Funding is paid by whoever holds the perp at the stamp T (00/08/16 UTC on Binance, Bybit and OKX). When the rate is
large, the paying side has an incentive to close just before T and reopen just after. With f > 0, longs pay: they sell
before T (pressure down into T) and buy back after T (pressure up). With f < 0 it is the reverse. Arbitrage keeps IC's
spot CFD tied to the perp.
- **PRE leg**: side = -sign(f̂), held [T-w, T).
- **POST leg**: side = +sign(f̂), held [T, T+w].
- **V**: both legs on the same stamp, two round trips.

A competing flow could point the other way: carry traders opening long-spot / short-perp just before T to receive
the funding would lift spot. The side is not chosen on data. Only the brief's side is graded; an opposite-sign
result is reported as information and cannot be registered.

**Size bound (what makes LIVE out of reach before any number).** The payer avoids paying f by selling and rebuying,
so the price concession they accept per round trip cannot exceed f minus their fees. Otherwise staying in is cheaper,
and someone else would provide the liquidity at a profit. The expected move into T is therefore at most of the
order of f: 3-10 bp in the large-rate tiers, about 1 bp at the floor.

## Family F1: funding-settlement pressure (36 cells)

- **Predictors**, both known before every window opens:
  - **PP** = predicted rate: Binance's formula F = P + clamp(1 bp - P, ±5 bp), where P is the linearly weighted
    mean of the hourly premium-index closes of hours T-8h..T-1h (the 7 hours fully closed by T-60 min). It is used
    for all windows. Premium klines start 2019-12-24; before that PP is missing.
  - **PL** = last published rate (stamp T-8h).
- **Tiers**: A3 = \|f̂\| >= 3 bp, A5 = \|f̂\| >= 5 bp. The thresholds come from the mechanism:
  - 3 bp is three times the floor;
  - 5 bp is above Binance's maker round trip of ~4 bp (VIP 0, 2 x 0.02 %), where closing and reopening starts to pay.
- **Windows** w = 15, 30, 60 min. **Legs**: PRE, POST, V.
- Cells: 2 predictors x 2 tiers x 3 windows x 3 legs = **36 cells**. Symbol: BTCUSD at IC.
- **Fills** (IC M1, bar label = bar start, price = (bid close + ask close) / 2):
  - PRE enters at the close of bar T-w (the price at T-w+1 min) and exits at the close of bar T-1 (the last quote
    before T).
  - POST enters at the close of bar T (T+1 min) and exits at the close of bar T+w.
  - A missing entry or exit bar drops the trade (weekends until 2024-04).
- **Cost**: half the actual spread at the entry bar plus half at the exit bar; no commission (crypto). No swap, since
  no window crosses 17:00 New York.
- **Checks**: spread x1.5; +1 min on both legs (PRE then exits at T+1, after the stamp, which tests whether the edge
  needs exact timing).
- **Statistics**: t clustered by UTC day; by year; with and without 2020-03/04.
- **Random-entry control**: 200 seeds. For each real trade, a random start minute within its stamp's ±8 h, at least
  90 min from any stamp, same w. The side and f̂ are recomputed at the random time for the next stamp, from premium
  hours fully closed by then (PL if fewer than 2 hours).
- **Time placebo**: the same rule with the stamp shifted by ±2 h and ±4 h, the side recomputed.
- **Multiple testing**: best \|IS net t\| over the 36 cells against a day-block sign-flip null (200 draws, max over
  the 36 cells).
- **Mechanism check** (information): the OLS slope over all stamps of the PRE return on PP, in bp of return per bp of
  funding. The mechanism needs a negative slope, of magnitude at most about 1.
- **Eras**:
  - IS = 2019-09-10..2021-12-31 (Binance series start; PP from 2019-12-24). This is a shortened IS of 2.3 years.
  - VAL = 2022-2024.
  - IS-early 2018-11-15..2019-09-09 uses Bybit inverse PL, as information (out-of-sample before IS).
- **ETH** (information only, at IC's real cost): the same 36 cells on ETHUSD with ETHUSDT funding. IS RT cost is
  ~103 bp against a 3-10 bp mechanism bound, so no ETH cell can pass.

### Power arithmetic (done before any return)

HOLD trade counts are taken at the VAL-era rate per year x 1.75 years, with all days counted (IC trades crypto at
weekends since 2024-04): PP-A3 115 VAL stamps -> ~67 HOLD; PP-A5 41 -> ~24.

| cell type | IS trades (weekday) | HOLD trades expected | Sharpe needed for LIVE (3/sqrt(n)) | net needed at VAL w30 sd 43 bp | Sharpe the mechanism bound allows (f ~5 bp, cost 3) | bar reachable |
|---|---|---|---|---|---|---|
| A3, one leg | ~400 | ~67 | 0.37 | ~16 bp | <= ~0.1 | DEMO at most |
| A5, one leg | ~240 | ~24 | 0.61 | ~26 bp | <= ~0.15 | DEMO at most |
| all stamps, dose-sized (dropped, = round 3) | ~1,800 | ~1,900 | 0.069 | ~3 bp | ~1 bp gross at the floor, below cost | none |

- **DEMO**: needs IS net t >= 2, i.e. on ~400 IS trades a per-trade Sharpe >= 0.10. At the IS w30 sd of ~60 bp that
  is net >= 6 bp, or mid >= 11 bp. That is about the whole funding paid at the A3 tier, so DEMO is possible only if
  the pressure approaches the funding size.
- **LIVE**: no cell can reach HOLD power 3. Large rates are rare in 2022-24 (and with them the trade count), and the
  edge is bounded by f.

## Family F2 (declared now, run after F1): CME BTC monthly expiry, the BRR window, conditioned on the carry

- **Mechanism**: CME BTC futures settle on the last Friday of the month to the CF BRR (15:00-16:00 London).
  Cash-and-carry holders (long spot, short CME) who do not roll sell spot over the window. The flow scales with how
  much basis trade exists, and that grows with the carry.
  - Proxy for the carry, known before the window: the mean of the perp funding over the 21 stamps before 08:00 UTC of
    the expiry day (Binance; Bybit inverse before 2019-09-10). CME basis data are unreachable (cmegroup.com timeout).
- **Rule** (round 12 K5's legs, now conditioned):
  - A: short BTCUSD 15:00 -> 16:00 London;
  - B: long 16:00 -> 17:00 London;
  - only when the 7-day mean funding >= 2 bp per 8 h (about 22 % a year, double the floor's carry).
  - Control (information): the months below the threshold.
  - Cells: A, B = **2**.
- **Eras and power**: IS 2018-01..2021-12 (CME from 2017-12; signal from 2018-11). Expected count ~15-20 IS events and
  only a few in VAL. DEMO needs IS t >= 2 on ~18 events, i.e. Sharpe ~0.47. LIVE is impossible (~8 HOLD events at
  most).

## Families considered and dropped on count or data before any return
- **Binance / Deribit quarterly delivery** (08:00 UTC, last Friday of the quarter; settlement = 30-min index TWAP),
  conditioned on the quarterly basis: 4 events a year, so ~8 in IS 2020-21 and ~7 in HOLD. It cannot reach DEMO's IS
  t (Sharpe ~0.7 needed), and its clock is round 12 K4's Friday 08:00 (with K4's quarterly split, n 15 / 12).
  **Dropped.**
- **Funding interval / cap changes**: BTCUSDT on Binance kept 8 h and its cap throughout 2019-24. Interval changes
  (to 4 h / 1 h) hit only altcoins, which are not at IC. **Dropped** (no BTC event).
- **Index-price constituent changes** (Binance / Bybit index weights): no public history found. **Not testable.**

## Log after the numbers (2026-10-29 09:37 UTC)

F1 and F2 were run between 09:33 and 09:37 UTC exactly as declared above.

Added after the first F1 numbers, as information only (no cell, nothing registrable):
- the minute profile of the PRE move;
- the split by funding sign and by stamp hour;
- the +2 h placebo with the last-published side (PP has fewer than 2 premium hours there);
- break-even cost and power at today's cost.

No new family was declared after the numbers.
