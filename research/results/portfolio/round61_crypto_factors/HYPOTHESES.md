# Round 61: cross-sectional factors on Binance USDT-M perps (declared before any factor return was computed)

Written 2026-10-31 12:52 UTC (from `date -u`). Data already local from rounds 58 / 60 (perp 1d klines, funding of every
symbol ever top-40); no cross-sectional sort has been computed on it.

Why: round 11 found no cross-section on IC's handful of crypto CFDs; the Binance perp universe (40 liquid coins, taker
0.05 %, no financing markup, weekly holds now allowed) is the setting of the crypto factor literature (Liu, Tsyvinski &
Wu 2022 JF "Common risk factors in cryptocurrency": 1-4 week momentum; Schmeling et al. 2023 on carry).

- Universe each Sunday close: top 40 by trailing-30-day perp quote volume, listed >= 60 days, excl. stable / index /
  TradFi perps (round 60 list). Rebalance weekly at the Sunday 00:00 UTC close (Monday open), hold 7 days.
- Portfolio: long top quintile (8), short bottom quintile (8) by signal, equal weight, gross 1 per side (dollar-neutral),
  constant notional within the week. Funding paid / received on each leg (actual stamps). Costs: turnover x (0.05 %
  taker + 0.03 % half-spread; 0.01 % for BTC / ETH).
- **X1 momentum**: signal = past 28-day return (close to close up to the rebalance close); long winners, short losers.
- **X2 funding carry**: signal = - trailing-7-day mean funding; long low-funding, short high-funding coins.
- **X3**: 50 / 50 of X1 and X2 weekly returns.
- Eras by week start: IS 2020-01..2021-12, VAL 2022-24, HOLD 2025-01..2026-10 (cut at load). Unit: weekly return, t
  Newey-West lag 4. LIVE bar as the user's: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years > 0, > 95 % of 500 shuffled-signal
  sorts, > 0 at costs x1.5 and rebalanced one day late; HOLD power = weekly Sharpe (VAL) x sqrt(95) >= 3, i.e. weekly
  Sharpe >= 0.31 (annual ~2.2). Margin-only: also graded minus cash on 1/3 margin of gross 2.
