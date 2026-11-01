# Round 60: short new Binance USDT-M perp listings, held weeks (declared before any post-listing return was computed)

Written 2026-10-31 12:38 UTC (from `date -u`). Only the perp 1d klines (pulled in round 58 for volume ranking) exist
locally; no post-listing return, funding or listing count has been computed or looked at.

## Why
Lifting the 5-day hold and IC-only limits (2026-10-31) opens crypto cross-sections held for weeks. No round has looked
at listings. Mechanism: tokens arrive on Binance perps with a small free float, scheduled unlocks (team, investors,
airdrop recipients) and retail attention at a peak; supply then hits a thin market while attention fades. Practitioner
and press evidence ("low float, high FDV", 2024) says new tokens fall for weeks after listing. Risks: short squeezes
(+100-500 % in days), negative funding (crowded shorts pay longs), delistings, regime dependence (2021 alt season).

## Events
- Listing day L0 = the first 1d kline of a USDT-M perpetual in research/data/binance/perp_1d (891 symbols, incl.
  delisted). Exclude re-denominations of a coin that already had a perp (e.g. 1000X after X, LUNA2 after LUNA) and
  stablecoin / index perps (USDC, BTCDOM, DEFI, FOOTBALL, BLUEBIRD). One event per symbol.
- Groups reported: NEW (no Binance spot pair, or spot listed within 30 days of L0) and OLD (spot older than 180 days).

## Trade (fixed)
- Main **N1**: short the new perp at the close of L0 + 1, hold H = 30 days, exit at the close of L0 + 31 (or at the
  last close if data end / delisting). Hedge: long BTCUSDT perp, equal notional (beta-neutral to BTC at 1).
- Costs per side: new perp 0.05 % taker + 0.10 % half-spread; BTC leg 0.05 % + 0.01 %. Funding: actual stamps on both
  legs (short receives positive funding, pays negative). Missing funding history -> pull it (all events need it).
- Reported, not picked: k in {1, 7} entry delay, H in {14, 30, 60}, unhedged. N1 is the only registered candidate.

## Unit, eras, bars
- Unit: episode return (net, on notional). t clustered by entry month (episodes overlap). Eras by entry date: IS
  2020-01..2021-12, VAL 2022-01..2024-12, HOLD 2025-01..2026-09-28 (exit before 2026-10-29). HOLD cut at load.
- Random benchmark: the same entry dates, a random symbol listed >= 365 days earlier and in that day's top-60 by volume,
  same hedge / hold / costs (500 draws): N1 must beat >= 95 % (this separates "new" from "any alt underperforms BTC").
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years positive, > 95 % random, positive at costs x1.5 and with k = 2;
  HOLD power = Sharpe per episode (VAL) x sqrt(expected HOLD episodes) >= 3. Margin-only trade: graded raw and minus
  cash on 1/3 margin.
- Tail report: worst episode, share of episodes with an adverse move > 100 % (squeeze), effect of a 100 % stop.

## Power before building
If ~80 listings / yr and per-episode Sharpe 0.25 -> HOLD (~140 episodes) power 3.0. A -10 % mean with 40 % sd per
episode is Sharpe 0.25; less than that cannot be LIVE on this HOLD.
