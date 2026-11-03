# STREAM_SI: stacked imbalance zones (book setup #4), first test, Binance USDT-M perps

Written 2026-11-03 17:10 UTC. Declarations: HYPOTHESES_SI.md (16:53 UTC, addenda A2-A3 and the IS selection written
before VAL). Code: SI/code/si.py (pipeline), SI/code/analyze.py (tables). Outputs: SI/out/ (IS_tables.txt,
VAL_tables.txt, random_means.txt, logs, trade npz).

## Answer: none (no LIVE, no DEMO)

All 4 declared cells lose money after costs in IS and in VAL. The IS pick (f0_TPV) has pooled net **-1.14 bp / trade,
t -0.56** in IS and **-3.30 bp, t -2.30** in VAL, 0 of 5 years positive, so it fails at the first bar (net > 0). Power
at VAL size is negative (-3.30 / 119 x sqrt(4,443) = **-1.85**). No PREREG_DRAFT.

What the footprint *does* do: stacked-imbalance zones are less bad than random levels with the same retest rules.
In IS, f0_TPV beats 99.5 % of the 200 random draws (-1.1 bp vs random median -5.1 bp); in VAL only 70.5 % (-3.3 vs
-4.1 bp). The gap (~4 bp IS, ~1 bp VAL) shrinks out of sample and is smaller than the round-trip cost (4-7 bp + stop
slippage + funding). Gross per trade before costs is +5.1 bp IS, +3.0 bp VAL on a stop of ~130 / ~90 bp.

## Rule (common execution model of the BRIEF)

Zone = `fp.stacked(fp.imbalances(30m footprint, ratio 3, floor), n=3)`; buying stack -> support (long), selling stack
-> resistance (short). Floor f0 = 0 or fmed = median non-zero bid / ask cell value of the 48 bars before. Usable after
the 2nd 30m bar entirely beyond, 7-day expiry, first 1m test only, limit at the near edge filled only if traded 1 bp
through, stop 0.15 x ATR14 (perp_1d klines), TP = TPV (one row before the nearest prior-48-bar POC beyond 1R, within
3R, else 2R) or 2R, 24 h time stop, maker 2 / taker 5 bp, stop slippage 1 bp (BTC, ETH) / 2 bp (SOL), funding.
k = 3 / 4 / 7 bp rows (BTC / ETH / SOL).

## Pooled (BTC + ETH + SOL), n = 3, declared cells

| cell | era | n | net bp | t | net R | x1.5 bp | late bp | gross bp | random beats | years + |
|---|---|---|---|---|---|---|---|---|---|---|
| **f0_TPV (IS pick)** | IS | 7,160 | -1.14 | -0.56 | -0.020 | -4.28 | -5.79 | +5.07 | 99.5 % | 0 / 2 |
| | VAL | 7,270 | -3.30 | -2.30 | -0.039 | -6.43 | -7.31 | +2.99 | 70.5 % | 0 / 3 |
| f0_2R | IS | 6,028 | -2.87 | -1.06 | -0.019 | -6.26 | -8.08 | +3.84 | 92.0 % | 0 / 2 |
| | VAL | 6,530 | -4.94 | -2.70 | -0.054 | -8.34 | -8.73 | +1.92 | 23.0 % | 0 / 3 |
| fmed_TPV | IS | 1,444 | -10.45 | -2.01 | -0.069 | -13.72 | -17.82 | -4.15 | 51.0 % | 0 / 2 |
| | VAL | 874 | -3.92 | -1.06 | -0.074 | -7.06 | -6.17 | +2.40 | 90.5 % | 0 / 3 |
| fmed_2R | IS | 1,339 | -16.38 | -2.55 | -0.103 | -19.90 | -24.12 | -9.73 | 16.0 % | 0 / 2 |
| | VAL | 861 | -0.58 | -0.13 | -0.036 | -3.94 | -2.79 | +6.19 | 93.0 % | 1 / 3 (2024) |

Max-over-4-cells null (per draw, max pooled t over the 4 cells): IS median -1.32, p95 -0.14, best real -0.56 beats
87.0 %; VAL median -1.13, p95 +0.02, best real -0.13 (fmed_2R) beats 91.5 %. Random pooled mean net per trade (median
of 200 draws): IS f0 -5.1 / -6.0, fmed -9.9 / -10.6; VAL f0 -4.1 / -3.8, fmed -7.4 / -6.6 (TPV / 2R).

Years (f0_TPV): 2020 -1.38 bp (t -0.54), 2021 -0.95 (-0.32), 2022 -2.99 (-1.08), 2023 -2.41 (-1.04), 2024 -4.26
(-2.13). Exit mix ~53 % stop, 46 % TP, < 1 % time. Longs are better than shorts in every cell and era (f0_TPV IS long
+3.0 / short -5.1, VAL -0.9 / -5.7), plausibly the 2020-24 uptrend (net of funding); not a declared cell.

## Per symbol (f0_TPV, base)

| sym | IS n | IS net bp | IS t | VAL n | VAL net bp | VAL t |
|---|---|---|---|---|---|---|
| BTC | 2,582 | +2.17 | 0.89 | 2,854 | -2.66 | -1.68 |
| ETH | 2,771 | -3.95 | -1.30 | 2,623 | -3.48 | -1.61 |
| SOL | 1,807 | -1.56 | -0.31 | 1,793 | -4.05 | -1.09 |

BTC is the only symbol-era with positive net in the selected cell (IS), and it turns negative in VAL. fmed cells are
noisy small samples (SOL VAL fmed +5.5 / +9.9 bp on ~150 trades, t 0.4-0.6). n = 4 (information only): every pooled
cell negative in both eras (best VAL f0_n4_TPV -2.66 bp, t -1.29).

## Holes in the cache (BRIEF update)

Gaps > 30 min between cached 1m bars, 2020-2024: BTC 24 (610 h), ETH 7 (170 h), SOL 7 (170 h). Trades dropped because a
hole lies between zone formation and fill, or fill and exit (f0_TPV / f0_2R / fmed_TPV / fmed_2R): IS BTC 85 / 84 / 5
/ 5, ETH 11 / 12 / 0 / 0, SOL 2 / 2 / 0 / 0; VAL BTC 27 / 27 / 1 / 1, ETH 25 / 25 / 1 / 1, SOL 14 / 13 / 1 / 1.

## Why it fails

- The first retest of a stacked-imbalance zone carries a small gross edge (+3-5 bp per trade on stops of 90-130 bp,
  i.e. ~0.03-0.04 R), below the 4-7 bp round trip; a late (market) entry adds 3 bp of taker fee plus adverse
  selection and is worse everywhere.
- Part of that edge is generic: random levels under the same departure / first-test rules lose about 4-5 bp, the real
  zones 1-3 bp. The footprint-specific part is ~4 bp in IS and ~1 bp in VAL (f0_TPV), so it decays out of sample like
  other crypto microstructure effects (rounds 58-66).
- The floor (fmed) cuts trades by ~80 % without improving the edge in IS; its better VAL rank among random draws is
  on < 900 trades and was not the IS pick.

## Pitfalls met

- The BTC footprint was rebuilt mid-stream (bucket carry into the minute field); all BTC numbers here come from the
  rebuilt file, and prepare() asserts every 30m bar's low / high falls in its bottom / top row.
- Cache holes: a contiguous-day ATR from 1m bars silently drops ~14 days after each hole; ATR now from perp_1d klines.
- The random benchmark matters for reading this setup: "beats random 99.5 %" in IS looks strong while both are
  money-losing, and the margin shrinks in VAL.
- Funding and the HOLD rows of perp_1d / funding CSVs are cut at 2025-01-01 on load; HOLD never opened.
