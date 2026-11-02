# PREREG DRAFT A2-D5L: long the Binance perp 5 s after an Upbit KRW-listing notice, exit at the KRW open

Drafted Sun Nov 1 12:22:56 UTC 2026 by stream A2 (round 65). HOLD has not been opened. The coordinator opens it once.

## Rule (frozen; code A2/code/analyze.py `trade`, A2/code/events.py)
- **Event:** an Upbit notice whose body puts a coin on the KRW market. Excluded: BTC- or USDT-only notices,
  stablecoins and re-listings. The coin's Binance USDT-M perp must have traded for >= 7 d before N. This is stream A's
  event builder (A/code/events.py), applied to notices with first_listed_at >= 2025-01-01 and <= 2026-10-29.
- **Times:**
  - N = `first_listed_at`, whole seconds, KST -> UTC.
  - L = the first Upbit KRW 1m candle. If that market is delisted: stated start + 5 min; for a shared notice, a sibling
    coin's L.
- **Entry:** long the alt perp and short BTCUSDT perp, equal notional. Each leg fills at the price of its first
  aggTrade with time >= N + 5 s.
- **Exit:** each leg at its first aggTrade with time >= L.
- **Costs:**
  - 20 bp (4 taker fills x 5 bp);
  - plus slippage on each of the 4 fills, = half the median 1 s range ((max - min) / min over 1 s bins with trades) of
    that symbol in the 60 s from the fill time;
  - plus real funding at stamps in (entry, exit]: long alt pays its rate, short BTC receives BTC's.
- **Data and stats:** data.binance.vision futures/um daily aggTrades. t is clustered by notice day.

## Numbers at registration (IS 2020-21 / VAL 2022-24)
| | n (days) | net bp | t | median | SR / trade | years | x1.5 | late (d 10 s) | random |
|---|---|---|---|---|---|---|---|---|---|
| IS | 12 (9) | +1,296 | 3.07 | +1,024 | 1.03 | 2020 +412, 2021 +1,738 | +1,263 | +1,191 | 100 % |
| VAL | 32 (32) | +520 | 1.75 | +182 | 0.31 | 2022 +210, 2023 +386, 2024 +626 | +477 | +454 | 100 % |

**Post-hoc stress on VAL:**
- aggressor-side fills: +516, t 1.73;
- worst price of the 1 s after N + 5 s: +373, t 1.34;
- 10 % trimmed mean: +267;
- minimum leave-one-out t: 1.53.

**Correlation with C3:** 0.01 (24 shared days).

## Power and bar
- At VAL size, the HOLD power is 0.309 x sqrt(92) = **2.97**. The 92 is K2's registered HOLD event count over
  ~22 months. That is just under LIVE's 3, so **the draft is for DEMO.**
- **Pass (DEMO -> keep):** HOLD net > 0 per trade under the frozen rule, t (day-clustered) >= 1.0. Also report the
  aggressor-side fill and the worst-of-second fill.
- **Promotion to LIVE:** HOLD t >= 2.0, net > 0 under the aggressor-side fill, and a forward capture test (below)
  showing notice detection <= 3 s after N on >= 80 % of live notices.
- **Stop:** HOLD net <= 0. In that case drop the family (a seconds-level reaction trade) for good.
- **Report:** n, the number of notice days, the share of events with burst onset > N + 5 s (a sign of the competition
  speed), and the median path at +2 / +5 / +300 s.

## Execution prerequisites (user decisions, outside the backtest)
- **Notice capture.**
  - Keyless: poll api-manager.upbit.com at >= 1.5 s (it returns 429 at 0.3 s); CDN freshness is unknown.
  - Or Upbit's private WebSocket announcement feed, which needs an Upbit API key and account.
- **Trading.** A Binance USDT-M account in Tokyo. Size ~$10-30k per event; the VAL median buyer-taker flow in the first
  second after N + 5 s is $240k.
