# Round 75 stream AB: big limit orders (C1) and absorption (C2) at yesterday's Volume Profile levels

Written 2026-11-03 17:09 UTC. Rules: [HYPOTHESES_AB.md](HYPOTHESES_AB.md) (written 16:52 UTC, before any return;
notes on the BTC rebuild and the day holes added before any return was read). Code: `code/ab.py` (levels, tests,
confirmations, execution, 200 random draws), `code/report.py` (pooled tables). Full tables: `out/report_ALL.txt`
(IS-only first read: `out/report_IS.txt`).

## Answer: none. No cell is LIVE or DEMO

Not one of the 12 cells has a positive IS t above 0.44 (bar: 2.0 for DEMO, 2.5 for LIVE). Pooled over BTC + ETH +
SOL, 9 / 12 cells lose money in IS, 12 / 12 in VAL. Gross (before fees) is about 0 bp per trade against ~8.5-9 bp of
costs. The confirmations add nothing over entering at the test, and real VP levels do no better than random levels
from the same day's range. No PREREG_DRAFT.

| cell (pooled) | IS n | IS net bp | IS R | IS t | VAL n | VAL net bp | VAL t | yrs + | rnd % IS / VAL | power VAL |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 m4 TPV | 1,072 | -10.1 | -0.10 | -2.38 | 2,004 | -9.8 | -4.26 | 0/5 | 60 / 17 | -3.6 |
| C1 m4 2R | 1,022 | -12.7 | -0.10 | -2.22 | 1,911 | -10.0 | -3.29 | 0/5 | 36 / 35 | -2.7 |
| C1 m8 TPV | 136 | -6.3 | -0.05 | -0.48 | 239 | -2.9 | -0.43 | 1/5 | 81 / 82 | -0.4 |
| C1 m8 2R | 132 | +2.9 | +0.07 | 0.18 | 234 | -6.3 | -0.70 | 3/5 | 87 / 73 | -0.6 |
| C2 m4 TPV | 218 | -4.6 | -0.11 | -0.52 | 637 | -12.1 | -3.22 | 1/5 | 71 / 9 | -2.6 |
| C2 m4 2R | 216 | -5.3 | -0.07 | -0.45 | 630 | -11.0 | -2.21 | 0/5 | 56 / 30 | -1.8 |
| C2 m8 TPV | 10 | -68.4 | -0.54 | -1.63 | 44 | -23.3 | -1.35 | 1/5 | 5 / 35 | -1.1 |
| C2 m8 2R | 10 | -51.2 | -0.55 | -0.94 | 43 | -29.1 | -1.41 | 0/5 | 19 / 30 | -1.1 |
| bonus m4 TPV | 957 | -11.8 | -0.11 | -2.84 | 1,889 | -8.7 | -3.64 | 0/5 | 42 / 47 | -3.0 |
| bonus m4 2R | 913 | -14.8 | -0.12 | -2.49 | 1,801 | -10.1 | -3.24 | 0/5 | 30 / 29 | -2.7 |
| bonus m8 TPV | 116 | -8.3 | +0.01 | -0.70 | 208 | -3.5 | -0.47 | 1/5 | 60 / 77 | -0.4 |
| bonus m8 2R | 114 | +6.9 | +0.18 | 0.44 | 204 | -5.8 | -0.59 | 3/5 | 90 / 75 | -0.5 |
| control N0 TPV (limit at test) | 2,750 | -8.8 | -0.08 | -2.78 | 4,438 | -3.9 | -2.29 | 0/5 | 48 / 61 | -1.9 |
| control N0 2R | 2,481 | -7.1 | -0.07 | -1.68 | 4,006 | -5.5 | -2.41 | 0/5 | 61 / 57 | -1.9 |
| info N0m TPV (market at B0 close) | 3,209 | -12.0 | -0.12 | -4.18 | 5,284 | -5.6 | -3.40 | 0/5 | 34 / 90 | -3.0 |
| info N0m 2R | 2,877 | -9.7 | -0.10 | -2.45 | 4,766 | -8.6 | -4.04 | 0/5 | 57 / 64 | -3.4 |

t clustered by UTC entry day; rnd % = percentile of the real pooled t among 200 random-level draws; power = VAL net
mean / sd x sqrt(n_VAL x 22 / 36) (all negative, so the HOLD-at-1/4 caveat is moot). Fees x1.5 and one step late make
every cell worse or leave it below zero (`out/report_ALL.txt`); the best IS cell (bonus m8 2R, +6.9 bp, t 0.44) is t
0.16 at fees x1.5, then -5.8 bp in VAL.

**Max-over-cells null:** real max IS t 0.44 vs random max-t median 0.59 (95th 2.25): beats 42 % of draws. VAL: real
max -0.43 vs median -0.23 (95th 1.09): 41.5 %. The real levels are indistinguishable from random levels.

## Per symbol (net bp / t)

| cell | IS BTC | IS ETH | IS SOL | VAL BTC | VAL ETH | VAL SOL |
|---|---|---|---|---|---|---|
| C1 m4 TPV | -8.0 / -1.75 | -12.0 / -1.87 | -10.7 / -0.69 | -6.8 / -2.58 | -12.4 / -3.93 | -10.1 / -1.88 |
| C1 m8 2R | -25.2 / -1.54 | +27.9 / 1.27 | -47.0 / -0.63 | -11.4 / -1.14 | -3.9 / -0.32 | -1.8 / -0.07 |
| C2 m4 TPV | +1.0 / 0.09 | -10.6 / -0.95 | -4.7 / -0.12 | -11.7 / -2.49 | -15.2 / -3.03 | -8.6 / -0.93 |
| bonus m4 TPV | -6.5 / -1.35 | -14.3 / -2.29 | -18.5 / -1.13 | -7.3 / -2.54 | -6.2 / -1.91 | -13.5 / -2.47 |
| bonus m8 2R | -10.1 / -0.55 | +31.1 / 1.50 | -83.7 / -0.94 | -3.8 / -0.35 | +7.5 / 0.56 | -26.4 / -1.04 |
| N0 TPV | 0.0 / 0.00 | -15.6 / -3.47 | -11.3 / -1.38 | -3.7 / -1.87 | -5.0 / -2.06 | -3.1 / -0.86 |

The only positive IS numbers are ETH at m = 8 (n 65-80, t <= 1.5); BTC and SOL are negative there, and VAL ETH is
t 0.56 at best. All 16 rows per symbol are in `out/report_ALL.txt`.

## Where the money goes

| | gross IS | gross VAL | fees + funding |
|---|---|---|---|
| C1 m4 TPV | -1.5 | -1.2 | ~8.6 |
| C2 m4 TPV | +4.1 | -3.5 | ~8.6 |
| bonus m4 TPV | -3.2 | -0.2 | ~8.6 |
| bonus m8 2R | +15.9 (n 114) | +3.2 | ~8.9 |
| N0 TPV (maker entry) | -3.1 | +1.6 | ~5.6 |

Gross is within a few bp of zero for every cell with n > 200, so the stop / TP geometry (R ~ 85-100 bp, about half
stopped, half at TP) is a coin flip and the costs set the sign. The confirmation cells pay ~3 bp more than N0 (taker
entry) and gain nothing for it: at m = 4, C1 / bonus gross is no better than N0 or N0m gross, by era or level type.

## Counts and data
- Tests (first touch of yesterday's POC / VAH / VAL on day d): BTC 3,604, ETH 3,609, SOL 3,006 (about 66 % of levels
  are tested). Confirmations m = 4 / 8: C1 1,236 / 140 (BTC), 1,287 / 174 (ETH), 809 / 76 (SOL); C2 314 / 23,
  339 / 19, 226 / 14; bonus 1,135 / 122, 1,176 / 148, 746 / 67. C2 at m = 8 is too rare to test (10 IS trades).
- Holes > 30 min in the 1m cache: BTC 24 (610 h, 28 UTC days), ETH 7 (170 h, 9 days), SOL 8 (177 h, 10 days). Days
  touching a hole and the day after get no levels; no remaining trade spans a hole (0 dropped).
- ATR14 from perp_1d klines (2025+ rows cut on load). BTC footprint used only after the coordinator's rebuild.
- Peak memory ~0.9-1.1 GB per symbol run, ~70-135 s each with 200 draws.

## What failed and why
- Mechanism not visible: heavy passive cells (C1) and two-sided heavy cells (C2) at yesterday's VP levels do not
  predict the next hours' direction; the bonus (C1 / C2 then same-direction 5m delta) does not either. This matches
  rounds 4, 17 and 63: signed and passive flow on Binance perps carries ~nothing at cost-relevant size.
- The VP levels themselves carry nothing: random rows of yesterday's range give the same t (percentiles 17-90 %).
- Shorts are worse than longs in IS for C1 m4 (-15.4 vs -6.0 bp); no level type (POC / VAH / VAL) is positive in VAL.

## Pitfalls / choices worth knowing
- Reference for C1 / C2 = mean of all non-zero side values (bid and ask each a cell) over the 12 5m bars before the
  test bar, all rows. A test bar always carries more volume than average, so m = 4 fires on ~35 % of tests: m = 4 is a
  loose filter, m = 8 a rare one; neither helps.
- The test minute's 5m bar (B0) counts in the window; confirmations are read only at bar closes (no look-ahead).
- One step late keeps the stop / TP distances from the late fill; late numbers are close to on-time (no fill-time edge
  to lose).
- Market entries pay no slippage in the base model (common model); the +1 / 2 bp entry-slip variant is 1-3 bp worse.
- Trades still open at 2024-12-31 are cut at the last 2024 minute (no 2025 data read).
