# Round 75 stream TF: trades filter (book setup #3). Verdict: none

**Answer: no LIVE, no DEMO, no candidate.** No cell gets near the IS bar. The best pooled IS cell (R5 x 2R) makes
+0.70 bp / trade (t +0.23). In VAL all four cells lose 3.6-3.8 bp / trade (t -2.0 to -3.4, 0 / 3 years positive) and
land at the 30-54th percentile of the random-level benchmark. Before fees the retest of a big-trade price makes about
+2 bp in VAL, and the retest of a random price of the same width makes the same; fees and slippage come to ~5.5 bp.
The book's "trades filter" level is just another level here: no better than any first retest. No PREREG_DRAFT.

Rules: HYPOTHESES_TF.md (written 16:52 UTC, before any return; addenda for the coordinator's BTC footprint fix and the
1m holes, both before any return was read). IS was read and the selection written (out/IS_SELECTION.md) before VAL
was computed. Code: TF/code/tf.py (engine), stats.py (tables), check.py (slow re-implementation of departure / test
/ 2R execution, 0 mismatches on 40 zones each for BTC and ETH).

## Setup in one paragraph
Big trade = aggTrade >= Q, Q per month = the N-th largest notional of the previous month, N = R x days present in it
(R 5 or 10). Zone = the 30m footprint rows of the big trades (same bar, adjacent rows merged). Common execution model
of the BRIEF: 2 full 30m bars beyond, first test only, limit at the near edge filled only 1 bp through, stop 0.15 x
ATR14 (perp_1d), TP = TPV (POC of the prior 48 bars beyond 1R, one row before it, else 2R) or 2R, 24 h time stop, one
open trade per symbol per cell, maker 2 / taker 5 bp, slippage 1 bp (BTC, ETH) / 2 bp (SOL), funding. Pooled BTC + ETH +
SOL, t clustered by UTC day. Random benchmark: 200 draws of same-width zones in the same bar on a random row of the
48-bar range.

## IS 2020-21 (pooled)

| cell | n | net bp | net R | sd R | t | fees x1.5 t (net) | late t (net) | years + | random pct |
|---|---|---|---|---|---|---|---|---|---|
| R5 TPV | 5,832 | +0.45 | -0.006 | 1.15 | +0.22 | -1.15 (-2.34) | -2.00 (-5.00) | 1/2 | 88.5 |
| R5 2R | 4,878 | +0.70 | +0.007 | 1.45 | +0.23 | -0.75 (-2.27) | -1.58 (-5.29) | 1/2 | 96.5 |
| R10 TPV | 8,056 | -1.66 | -0.017 | 1.14 | -0.96 | -2.56 (-4.44) | -3.41 (-7.20) | 0/2 | 39.0 |
| R10 2R | 6,425 | -1.27 | -0.012 | 1.45 | -0.51 | -1.70 (-4.25) | -2.57 (-7.34) | 1/2 | 77.0 |

Max-over-4-cells null: best real t +0.23 beats 76.5 % of the draws' max (95th percentile of the null max +0.93).
In IS the random levels lose more (median random t -0.85 to -1.20), hence the high percentile of R5 2R; but the cell
itself is ~0, far below the DEMO IS bar of t 2.0.

## VAL 2022-24 (pooled, cells unchanged)

| cell | n | net bp | net R | t | fees x1.5 t | late t | years + | random pct | power at VAL size |
|---|---|---|---|---|---|---|---|---|---|
| R5 TPV | 8,669 | -3.81 | -0.052 | -2.80 | -4.82 | -6.07 | 0/3 | 35.5 | -2.38 |
| R5 2R | 7,453 | -3.57 | -0.057 | -1.98 | -3.62 | -4.37 | 0/3 | 53.5 | -1.64 |
| R10 TPV | 13,112 | -3.69 | -0.058 | -3.37 | -5.90 | -7.82 | 0/3 | 30.5 | -2.87 |
| R10 2R | 10,666 | -3.79 | -0.068 | -2.48 | -4.42 | -5.67 | 0/3 | 40.0 | -2.11 |

Max-over-4-cells null in VAL: best real t -1.98 beats 31 % of draws. Power is negative because net is negative; at
1/4 of VAL size (the round 58-66 shrink) it would be -0.4 to -0.7.

## Per symbol (n / net bp / t)

| cell | BTC IS | ETH IS | SOL IS | BTC VAL | ETH VAL | SOL VAL |
|---|---|---|---|---|---|---|
| R5 TPV | 2104 / +2.05 / +0.86 | 2546 / -2.38 / -0.87 | 1182 / +3.67 / +0.55 | 2657 / -4.12 / -2.84 | 2777 / -3.68 / -2.07 | 3235 / -3.66 / -1.26 |
| R5 2R | 1785 / +2.83 / +0.83 | 2114 / -0.77 / -0.20 | 979 / -0.01 / -0.00 | 2313 / -5.06 / -2.75 | 2420 / -2.83 / -1.13 | 2720 / -2.98 / -0.77 |
| R10 TPV | 3022 / +0.03 / +0.02 | 3564 / -4.02 / -1.73 | 1470 / +0.60 / +0.11 | 4155 / -3.46 / -3.05 | 4234 / -4.30 / -2.97 | 4723 / -3.34 / -1.40 |
| R10 2R | 2416 / +3.29 / +1.12 | 2818 / -6.38 / -1.94 | 1191 / +1.55 / +0.19 | 3425 / -5.66 / -3.59 | 3449 / -1.74 / -0.83 | 3792 / -3.98 / -1.23 |

Per year (pooled, net bp / t): R5 2R 2020 +3.8 / +1.16, 2021 -1.3 / -0.29, 2022 -5.4 / -1.17, 2023 -2.7 / -1.08,
2024 -3.1 / -1.22. All years for all cells: out/stats_IS.md, out/stats_VAL.md.

## Before fees: footprint vs random (out/gross.md)

| cell | IS real | IS random | VAL real | VAL random |
|---|---|---|---|---|
| R5 TPV | +6.0 | +3.9 | +1.8 | +2.1 |
| R5 2R | +6.6 | +2.6 | +2.4 | +2.1 |
| R10 TPV | +3.9 | +4.1 | +1.9 | +2.1 |
| R10 2R | +4.7 | +3.3 | +2.2 | +2.4 |

bp per trade after funding, before fees and slippage. The first retest of any level makes a small positive gross
(~+2 bp in VAL on a ~90 bp stop, ~0.02 R); the big-trade level adds nothing in VAL. Stop distance averages ~118 bp in
IS, ~90 bp in VAL; 52-65 % of trades stop out, 34-48 % hit TP, ~1 % time out.

## Information: side of the big trades x test direction
IS showed one large subgroup: zones made only of aggressive-buy big trades, tested from above (long), R5 TPV +12.3 bp
(t +2.71), R5 2R +13.9 (t +2.26). It is one of 24 information subgroups and was not declared as a cell; VAL does not
hold it: R5 TPV -2.1 (t -0.78), R5 2R -3.0 (t -0.83), R10 TPV +0.7 (t +0.33). Nothing else in VAL is positive with
any size; aggressive-sell zones tested from below (short) are the worst (R10 TPV -7.2 bp, t -3.36). Not a lead.

## Data notes and counts
- Q floor ($100k = the cache threshold): BTC, ETH never. SOL: R5 2020-10..2021-04, R10 2020-10..2021-05 used $100k,
  so in those IS months SOL had more than R big trades per day (R5: 14,552 SOL big trades over the whole sample vs
  ~11-14k for BTC / ETH). First cached month (BTC / ETH 2020-01, SOL 2020-09) has no Q, no zones.
- Holes > 30 min in the 1m cache: BTC 24 (610 h), ETH 7 (170 h), SOL 7 (170 h, the same days as ETH). Trades dropped because
  zone life + trade spanned a hole: BTC 116-118 (R5) / 203-207 (R10), ETH 16 / 32, SOL 16 / 26.
- Zones per symbol: BTC 10,468 (R5) / 19,876 (R10), ETH 12,500 / 23,288, SOL 12,152 / 20,716. Every zone departs
  within 7 days (2 bars beyond on one side); ~89-91 % get a first test, ~86-92 % of tests fill 1 bp through, and the
  one-open-trade rule then keeps ~2.3-4 trades per day per symbol.
- The coordinator's BTC footprint fix (bucket carry) only touched TPV's POC rows here; all returns were computed after
  the rebuild, and every BTC / ETH 30m POC row lies inside its bar's range.

## What failed and why
The book's claim is that the price of an unusually large single aggressive order becomes a level that holds on the
first retest. On Binance USDT-M perps 2020-24, measured with the common execution model, it does not: the level's
first retest earns ~+2 bp before fees in VAL, the same as a random level of the same width in the same 48-bar range,
and less than the ~5.5 bp of fees and slippage. The one IS hint (buy-side support) did not hold in VAL. Sharper
thresholds (R5 vs R10) do not help. Late entry (market at the fill-minute close) costs another 1-4 bp.

## Pitfalls
- `fp.load_big` holds all stored trades (~34M for BTC, > 1 GB); TF reads the same arrays month by month and keeps only
  trades >= Q (same HOLD cut).
- The random benchmark's first retest is itself negative after fees (VAL median random t -2 to -3), so a high random
  percentile alone (IS R5 2R: 96.5) does not mean a tradable edge; the absolute bars decide.
- Do not run `pkill` on a shared machine: other streams run Python too (the classifier blocked one such call here; no
  process was killed).
