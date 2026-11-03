# STREAM_U: is an unfinished auction a magnet? (book setup #5)

Written 2026-11-03 17:04 UTC (from `date -u`). Rules: [HYPOTHESES_U.md](HYPOTHESES_U.md) (16:52 UTC, two addenda).
Code: `U/code/build_turns.py` (turns, flags, per-turn trade outcomes), `U/code/analyze.py` (statistic, cells,
permutation). Full output: [out/results_BTC_ETH_SOL.txt](out/results_BTC_ETH_SOL.txt). BTC, ETH 2020-01..2024-12,
SOL 2020-09..2024-12; HOLD not opened.

## Answer

**No magnet. Verdict for every trade cell: none.**

- Unfinished swing highs / lows are **not revisited more often** than finished ones at the same distance and
  volatility. Pooled matched difference D (unfinished minus finished, in percentage points of the revisit rate):
  IS H12 -0.21 (t -0.27), IS H48 -0.03 (t -0.05), VAL H12 -0.79 (t -1.11), VAL H48 +0.76 (t +1.29). The base rate is
  ~57 % (6 h) and ~78 % (24 h) for both labels. The permutation percentiles of D are 42 / 47 (IS) and 10 / 93 (VAL),
  all inside the null.
- So the book's magnet uses (extend a TP toward an unfinished extreme, don't put a stop in front of one, don't trade
  against one) are **void** on Binance BTC / ETH / SOL perps with this footprint (k = 3 / 4 / 7 bp rows). Other
  setups in this round should not use OF5 as a filter.
- The trade cells (market entry at confirmation toward the level, TP one row before it, symmetric stop) lose
  11-19 bp per trade in every cell, era, year and symbol, and the unfinished cells are no better than their
  finished controls (difference t -1.9..+0.3).

## 1. Statistic: P(price trades back into the level row within H 30m bars after confirmation)

Matched within symbol x side x distance decile (distance from the confirmation close to the level, in 30m ATR14) x
30m ATR tercile; t clustered by UTC day.

| group | H | n unf / fin | P(unf) % | P(fin, matched) % | D pts | t |
|---|---|---|---|---|---|---|
| pooled IS | 12 | 11,270 / 6,706 | 57.3 | 57.6 | -0.21 | -0.27 |
| pooled IS | 48 | 11,270 / 6,706 | 78.0 | 78.1 | -0.03 | -0.05 |
| pooled VAL | 12 | 24,353 / 6,894 | 57.3 | 58.1 | -0.79 | -1.11 |
| pooled VAL | 48 | 24,353 / 6,894 | 78.7 | 77.9 | +0.76 | +1.29 |
| BTC IS / VAL | 48 | | | | -1.75 / -0.24 | -1.67 / -0.23 |
| ETH IS / VAL | 48 | | | | +1.70 / +0.11 | +1.75 / +0.11 |
| SOL IS / VAL | 48 | | | | +0.04 / +2.72 | +0.03 / +2.97 |
| highs IS / VAL | 48 | | | | +0.90 / +1.08 | +0.96 / +1.26 |
| lows IS / VAL | 48 | | | | -1.18 / +0.41 | -1.18 / +0.51 |

By year (H48, D pts): 2020 -0.29, 2021 -0.57, 2022 +0.62, 2023 +2.07 (t 1.91), 2024 +0.07. H12: -0.11, -1.12, -1.40,
+0.05, -0.88. Signs flip between symbols, sides and years; no cell reaches the declared magnet bar (t >= 2.5 IS and
>= 1.5 VAL, same sign in each symbol). The one large number (SOL VAL H48 +2.7 pts, t 3.0) has IS +0.04 and is one of
~20 subgroups. Information rows: revisiting beyond the extreme itself (D -0.3 / -0.6 IS, -1.6 / +0.4 VAL) and
excluding the ~5-6 % of turns that touched the row before confirmation (same picture) change nothing.

Why matching matters: unmatched, unfinished turns look 1-4 points more likely to be revisited in most distance
deciles, because finished turns sit in more volatile periods (mean 30m ATR 118 bp vs 79 bp) and are over-represented
in SOL (finished share 36 % vs 23-26 % in BTC / ETH). Within symbol and ATR tercile the gap disappears.

Note on the definition: at these row sizes 64-77 % of 30m swing extremes are "unfinished" (both sides traded in the
top / bottom row), so "finished" is the minority, thin-extreme case.

## 2. Trade cells (8 declared: H {12, 48} x filter {D0 all, D1 TP in 0.10-0.30 daily ATR} x label)

Pooled three symbols, one open trade per symbol per cell; net bp per trade after fees, slippage, funding.

| cell | era | n | net bp | t | net R | win | fees x1.5 | one step late | unf - fin bp (t) |
|---|---|---|---|---|---|---|---|---|---|
| H12-D0 unf | IS | 8,108 | -14.76 | -8.89 | -0.30 | 0.46 | -19.14 | -15.92 | -2.75 (-0.89) |
| H12-D0 unf | VAL | 16,511 | -12.37 | -13.72 | -0.48 | 0.45 | -16.76 | -12.37 | -1.46 (-0.69) |
| H12-D1 unf | IS | 4,644 | -15.25 | -6.76 | -0.14 | 0.47 | -19.64 | -16.48 | -4.96 (-1.24) |
| H12-D1 unf | VAL | 9,058 | -12.21 | -10.22 | -0.16 | 0.47 | -16.61 | -12.63 | +0.62 (+0.25) |
| H48-D0 unf | IS | 6,781 | -16.58 | -7.89 | -0.30 | 0.46 | -20.89 | -17.96 | -5.97 (-1.31) |
| H48-D0 unf | VAL | 12,975 | -12.60 | -10.55 | -0.45 | 0.47 | -16.90 | -12.54 | -1.76 (-0.63) |
| H48-D1 unf | IS | 4,328 | -18.70 | -7.50 | -0.16 | 0.46 | -23.01 | -20.05 | -8.36 (-1.86) |
| H48-D1 unf | VAL | 8,412 | -11.92 | -8.79 | -0.15 | 0.48 | -16.20 | -12.34 | +0.95 (+0.34) |

Finished controls (IS / VAL net bp): H12-D0 -12.0 / -10.9, H12-D1 -10.3 / -12.8, H48-D0 -10.6 / -10.8,
H48-D1 -10.3 / -12.9. Years positive: 0 / 5 in every unfinished cell (and in every control). Each symbol is negative in
each era in every unfinished cell (t -3.0 .. -13.7).

Permutation benchmark (1,000 draws, labels shuffled within symbol x era x side x distance decile x ATR tercile):
percentile of the real unfinished-cell t IS 8 / 12 / 1 / 3, VAL 45 / 58 / 21 / 64 (cells in the table order);
max-over-4-cells null: IS percentile 5.7, VAL 61. Power at VAL size: -12.1 / -9.0 / -8.8 / -7.6 (negative edge).
Nothing passes LIVE or DEMO; no PREREG_DRAFT.

Mechanism of the loss: a symmetric TP / stop trade toward a level with no edge wins ~46-48 % after the stop slippage
and gap fills, and pays ~7 bp (TP exit) to ~11 bp (stop exit) round trip. The median TP is 60-120 bp, so the fee
drag is ~0.1-0.2 R; the D0 cells also include very short targets where the fee is a large part of R (net R -0.3..-0.5).

## Problems found and fixed
- **BTC footprint key overflow (shared layer, now fixed by the coordinator):** `build_fp.py` stored
  `minute * 100000 + bucket`, and for BTC above $22,026 the bucket carried into the minute field (wrong rows, a one
  minute shift). Found while building BTC turns (row prices ~$1-40). My independent decode was asserted identical to the
  fixed `fp.load_fp` for BTC and ETH, then removed. Every BTC number here uses the fixed layer.
- **1m-cache holes:** turns whose life (bar i-13 to confirmation + 48 bars) spans a hole > 30 min are dropped (BTC 237,
  ETH 77, SOL 71 of ~17 k / 17 k / 15 k); daily ATR from `perp_1d` klines. An earlier BTC / ETH run without these
  two changes gave the same picture (pooled D within +-1.2 pts, all cells negative); it is superseded.

## Pitfalls
- Compare unfinished with finished turns **matched on volatility and symbol**; the raw comparison invents a 1-4 point
  "magnet" that is only the volatility mix.
- The two-sample difference t in the cell table uses independent cluster SEs for the two cells (they share days, so
  it is approximate); the permutation, which keeps the day structure, gives the same answer.
- The unfinished flag depends on the row size k; with the shared k rule (median IS 30m range / 20) most extremes are
  unfinished. A coarser grid was not tested (not declared).
