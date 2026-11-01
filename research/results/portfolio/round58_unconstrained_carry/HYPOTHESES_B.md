# Round 58, stream B: cross-exchange perp-perp funding spread (declared before any computation)

Written 2026-10-31 11:04 UTC (from `date -u`), before any Bybit series was loaded.

Mechanism: the same leveraged-long demand is not priced identically on every venue; retail-heavy venues pay more.
Long the perp on the venue with the lower trailing funding, short it where it is higher; no spot leg, both legs pay
perp taker fees only. Risks: the two perps' prices diverge (index differences), venue risk on two exchanges.

- Data: Bybit linear USDT perp funding `api.bybit.com/v5/market/funding/history` (public), Bybit 1d klines
  `api.bybit.com/v5/market/kline?category=linear`; Binance from stream A.
- Universe: symbols in stream A's universe that also list on Bybit linear.
- **B1**: each day, signal = trailing-7-day mean (Binance funding - Bybit funding), annualised. Enter |signal| >
  15 %/yr (short the dearer venue), exit when |signal| < 5 %/yr or the sign flips; K = 10; equal notional.
  No grid: one cell, fixed now.
- Costs: 0.055 % Bybit taker + 0.05 % Binance taker + 0.03 % half-spread per leg per side.
- Eras and bars as stream A (IS 2020-01..2021-12 where Bybit data exists, VAL 2022-24, HOLD 2025-01..2026-10 cut).
- Run only if stream A's data pull leaves time; B is secondary.
