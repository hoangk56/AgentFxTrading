# PREREG DRAFT B: Binance altcoin perp-discount basis reversion (k100_H24_cheap), DEMO tier only

Draft written 2026-10-31 15:25 UTC by stream B (round 63). HOLD (2025-01-01..2026-10-29) NOT opened; the coordinator
opens it once. Tier: **DEMO** (IS t 2.46 < 2.5 rules out LIVE). Strong caveats in [STREAM_B.md](STREAM_B.md).

## Rule (frozen; code `code/basis.py` simulate(coins, 100, 24, -1), loader `load()`)
- Universe: point-in-time top-60 Binance USDT-M perps by trailing 30-day perp quote volume (previous day), listed >= 60
  days, Binance spot pair live, BTC / ETH / stablecoins / BTCDOM / PAXG excluded.
- Hourly basis b = ln(perp close / (factor x spot close)); valid bar: >= 20 trades on both legs, relative tick <= 5 bp
  both legs (30-day block estimate). Reference m = median of b over the previous 168 h (>= 120 valid).
- Event: b - m < -100 bp at the close of hour h. Enter at the open of h+1: long perp, short spot (margin borrow),
  1 unit notional each. One open trade per coin.
- Exit at the open after the first close c >= h+1 with b_c - m_h >= (b_h - m_h) / 2, else at the open of h+25.
- P&L: -(spot return) + (perp return) - funding on stamps in (entry, exit] - 30 bp fees - 4 x half-spread (3 bp rank <
  10, else 5 bp) - borrow 40 %/yr pro rata - Fed funds on the spot notional.

## IS / VAL numbers (declared cell, taker costs)
| era | n | net bp | median | t (day cluster) | x1.5 | 1 h late | random beaten |
|---|---|---|---|---|---|---|---|
| IS 2020-21 | 303 | +286.5 | +110.2 | 2.46 | +262.0 | +118.4 (median -23.1) | 100 % |
| VAL 2022-24 | 333 | +174.6 | +95.6 | 6.41 | +150.5 | +68.6 (median -10.0) | 100 % |
Years 2020-24: +75 / +319 / +265 / +149 / +93 bp (5 / 5).

## Power at VAL size
111 trades / yr, 48 event-days / yr. HOLD ~1.8 yr: per trade 0.270 x sqrt(200) = 3.82; per event-day 0.498 x sqrt(86)
= 4.63. Graded power = 3.82 (but the tier is DEMO because of IS t).

## HOLD pass bar (DEMO)
HOLD net > 0 per trade at taker costs with t (day cluster) reported; also report median, one-hour-late, x1.5, and the
share of P&L from the top 5 coins / days. Fail if net <= 0. Run once, HOLD cut 2025-01-01..2026-10-29.

## Demo plan (if HOLD passes and the user approves margin shorting)
- Expected ~100 trades / yr; small fixed notional per trade; log the real borrowable amount and hourly borrow rate at
  each signal (trades without borrow are recorded as "not fillable", counted against the rule), the fill prices and the
  book spread at entry.
- Stop rule: stop if cumulative net after 40 demo signals (fillable or not) < 0, or if > 30 % of signals are not
  fillable for lack of borrow.
- Live rule: HOLD + demo pooled t >= 2.5 on fillable trades, with not-fillable signals counted at 0.
