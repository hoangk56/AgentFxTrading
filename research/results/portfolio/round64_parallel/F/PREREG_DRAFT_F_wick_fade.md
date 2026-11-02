# PREREG DRAFT F: fade 5 % idiosyncratic 1-minute wicks on Binance USDT-M altcoin perps, hold 60 min (LIVE tier on IS / VAL)

Draft written 2026-11-01 09:36 UTC (from `date -u`) by stream F (round 64). HOLD (2025-01-01..2026-10-29) is **not
opened**. The coordinator opens it once. Hypotheses: [HYPOTHESES_F.md](HYPOTHESES_F.md), 08:54 UTC, before any return.
Report: [STREAM_F.md](STREAM_F.md).

Tier: **LIVE on the IS / VAL bars**. Every LIVE bar passes. Per-trade HOLD power at VAL size is 3.53, but the
day-clustered version is 2.93 (caveats below).

## Rule (frozen: cell "T5 idio H60" of the 18 declared cells, chosen as the best IS t)
- **Universe**, recomputed each UTC day d: the top 40 Binance USDT-M perps by mean daily quote volume over days
  d-30..d-1, listed >= 60 days (round 63 C `xs.daily_universe`). Delisted coins are included in the history.
- **Event** at 1m bar e (bar opening at minute e, UTC):
  - r = close_e / close_{e-1} - 1, on consecutive bars;
  - |r| >= 5 %;
  - the coin is in the universe on e's UTC day and is not BTCUSDT;
  - |r_BTCUSDT,e| <= 0.2 x |r| (BTC perp's same-minute close-to-close return).
- **Bad-print guard:**
  - bar e has >= 10 trades and quote volume > 0;
  - bar e+1 exists and its open is still on the shocked side of the halfway point: crash, open_{e+1} <= close_{e-1} x
    (1 + r/2); spike, open_{e+1} >= close_{e-1} x (1 + r/2).
- **De-duplication:** after an accepted event, the same coin's events in bars e+1..e+60 are ignored.
- **Trade:**
  - side: long the perp after a crash (r < 0), short it after a spike (r > 0);
  - enter at the close of bar e+1 (one full bar late);
  - exit at the close of bar e+1+60. If that bar is missing, use the last close within 5 minutes before it; else drop
    the trade.
- **P&L per unit notional** = side x (exit / entry - 1) - side x funding on stamps in (entry, exit] - costs.
- **Costs:**
  - taker 5 bp a side;
  - half-spread h = 3 bp (volume rank < 20 that day) or 5 bp (rank 20-39);
  - entry half-spread 3h, exit half-spread h, so a round trip is 22 / 30 bp.
- **Code:** `code/univ.py`, `code/pull.py`, `code/events.py`, `code/report.py`, plus round 63 C `code/xs.py`. Hashes:
  - `research/results/portfolio/round64_parallel/F/code/univ.py` 9b56f6a4ecbd2a83
  - `research/results/portfolio/round64_parallel/F/code/pull.py` fb61cae7c3b980d9
  - `research/results/portfolio/round64_parallel/F/code/events.py` 81e007b5cd04adcb
  - `research/results/portfolio/round64_parallel/F/code/report.py` 7e3b78d6ba5476c7
  - `research/results/portfolio/round63_parallel/C/code/xs.py` a53fe02181166152

## IS / VAL numbers (declared cell, taker costs, t clustered by entry UTC day)
| era | n | net bp | median | t | S / trade | x1.5 t | 2 bars late t | random beaten | crash / spike net |
|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 380 | +273.0 | +274 | 4.05 | 0.224 | 3.87 | 6.65 | 100 % | +581 / -189 |
| VAL 2022-24 | 770 | +270.5 | +177 | 3.76 | 0.163 | 3.58 | 3.12 | 100 % | +360 / +132 |

- **Years 2020-24:** +460 / +236 / +397 / +164 / +236 bp (5 / 5 positive). Break-even round trip ~296 bp (declared
  26 bp).
- **Max-over-18-cells null:** real IS t 4.05; the random-entry null has median -1.19 and 95th percentile +0.28.
- **Robustness:**
  - IS without 2021-05-19 (Binance futures outage day): +326.5 bp, t 5.39.
  - VAL without the LUNA (2022-05) and FTX (2022-11) months: +163.0 bp, t 3.65.
  - Without the top 3 coins: IS +212.8, VAL +190.5.
  - Without the top 5 days: IS +177.7 (t 3.74), VAL +126.5 (t 3.41).
- **Spot QC:** 279 of 291 sampled 3 % perp events with a spot bar also moved >= half as much in spot. The 12 failures
  are perp-only liquidation wicks (2021-05-19, FTT 2022-11), not bad prints.
- **Daily-P&L correlation with C3:** IS +0.048, VAL -0.037 (weekdays).

## Power at VAL size
- VAL has 257 trades a year, so HOLD (~22 months) is expected to hold ~470 trades.
- Per trade: 0.163 x sqrt(470) = **3.53**.
- Day-clustered: VAL t 3.76 x sqrt(0.61) = 2.93.
- Without LUNA / FTX the per-trade power is 5.04: the fat right tail inflates the sd more than the mean.
- Risk to power: the event rate depends on altcoin volatility. VAL ran 265 / 223 / 282 events in 2022 / 2023 / 2024.
  If HOLD has half that rate, the per-trade power falls to ~2.5.

## HOLD pass bar (all of; run once on 2025-01-01..2026-10-29)
1. Net mean > 0 and day-clustered t >= 2.0.
2. Net > 0 at costs x1.5 and with the entry two bars late (close of e+2, exit 60 bars later).
3. 2025 and 2026 (to 10-29) each net > 0.
4. Report, but do not use as a gate:
   - median;
   - crash / spike split;
   - share of P&L from the top 5 coins and top 5 days;
   - n versus the expected ~470.

HOLD needs monthly 1m klines for 2025-01..2026-10 for the point-in-time top 40 (and BTCUSDT), pulled by `code/pull.py`
with the month cap lifted. Everything else stays unchanged.

## If HOLD passes: demo, then live
- **Execution:**
  - stream 1m klines for the universe plus BTCUSDT (websocket);
  - at the close of bar e+1, send a market order for a fixed small notional;
  - exit with a market order 60 minutes later;
  - no stop (none was tested; the worst VAL trade was about -5,000 bp, so size for it).
- **Log for each trade:**
  - the model entry and exit prices against the real fills, and the book spread at entry;
  - concurrent positions: crash days such as 2021-05-19 fire dozens of coins at once.
- **Stop rule:** stop if the cumulative net after 60 demo trades is < 0, or if the median slippage against the model
  entry is > 100 bp.
- **Live rule:** HOLD + demo pooled, day-clustered t >= 2.5 at real fills.

## Not registered (information only; never choose these after the fact)
- The crash side alone is much stronger (IS +581, VAL +360) than spikes (IS -189, VAL +132). Splitting the sides was
  not declared, so the pooled rule stands.
- The neighbour cells also pass:
  - T5 all H60: IS t 2.92, VAL 4.73;
  - T3 idio H60: IS t 3.89, VAL 1.89, power 1.93;
  - the H15 versions fail IS (t ~1.0).
