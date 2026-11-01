# Round 59: cross-venue perp-perp funding spread (declared before any Bybit / Hyperliquid series was loaded)

Written 2026-10-31 12:02 UTC (from `date -u`). Stream B1 was first declared 11:04 UTC in
round58_unconstrained_carry/HYPOTHESES_B.md; it is restated here unchanged, plus B2 (Hyperliquid) and the cash grading
that round 58 showed is needed. Only probes so far: one Bybit page (BTC 2020-05) and one Hyperliquid page (BTC from
2023-05-12) to learn the history depth.

## Why
Round 58: spot-perp carry since 2025 earns exactly the cash rate, because funding embeds a fixed interest component
(0.01 % / 8h on Binance, Bybit and Hyperliquid) and the spot leg ties up full capital. A long-perp / short-perp pair
across two venues cancels the interest component and needs only margin on each leg; what remains is the difference
in leveraged-demand premia between venues (retail mix, index construction, clamp rules, hourly vs 8-hourly funding).

## Data (public, no key)
- Bybit linear USDT perps: `/v5/market/funding/history` (200 per page), `/v5/market/kline` interval D.
- Hyperliquid: `POST api.hyperliquid.xyz/info` `fundingHistory` (hourly since mid-2023, 8h before) and
  `candleSnapshot` 1d.
- Binance from round 58 (research/data/binance/).
- Universe: coins that were ever in round 58's Binance top-30 universe and list on the other venue.

## Accounting
Pair = short perp on venue H (higher signal), long perp on venue L, equal coin quantity, constant notional 1 per
pair. Daily P&L = funding received on the short - funding paid on the long + (dF_L - dF_H) / F_prev (the two perps'
price difference). Costs per side per leg: Binance taker 0.05 %, Bybit 0.055 %, Hyperliquid 0.045 %, + 0.03 % half
spread (0.01 % BTC / ETH). Capital = margin = 2 x notional / 3 (3x per leg) for the cash benchmark: graded on net
minus Fed funds x 2/3 x deployed fraction, and on raw net.

## Hypotheses (fixed now; no grid)
- **B1 (Binance vs Bybit)**: signal = trailing-7-day mean (Binance funding - Bybit funding), annualised. Enter when
  |signal| > 15 %/yr (short the dearer venue), exit when |signal| < 5 %/yr or the sign flips; K = 10 pairs, ranked by
  |signal|. Eras: IS 2020-06..2021-12 (Bybit coverage), VAL 2022-24, HOLD 2025-01..2026-10-29 (cut at load).
- **B2 (Binance vs Hyperliquid)**: same rule and thresholds. Hyperliquid starts 2023-05, so it can only be a new-era
  rule: DISCOVERY 2023-06..2024-12, TEST = HOLD 2025-01..2026-10-29 opened once after a prereg. The LIVE bar needs IS
  and VAL eras B2 cannot have; at most RELAXED / DEMO unless the user accepts a new-era LIVE.
- Random benchmark: same episodes and durations, random coins from that day's pair universe, random side, random
  entry days (500 draws).

## Bars
The user's LIVE bar on daily book returns (t_nw lag 10): IS >= 2.5, VAL >= 1.5, >= 2/3 years positive, > 95 % random,
positive at costs x1.5 and one day late; HOLD power at VAL size >= 3; **and excess over cash > 0 with t >= 1.5 in IS
and VAL** (added after round 58, declared here before B's data).

## Power before building
A spread of 5 %/yr net on deployed notional with 2 %/yr vol: daily Sharpe 0.13, x sqrt(669) = 3.4. The cash charge at
3x is ~2.6 %/yr of notional, so the raw spread must be >= ~8 %/yr while deployed for the excess to be material.
