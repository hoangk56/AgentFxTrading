# Stream VC (round 75): volume clusters in a trend leg or a rejection, first retest. None

Written Tue Nov 3 17:07:01 UTC 2026 (from `date -u`). Rules declared at 16:52:56 UTC in
[HYPOTHESES_VC.md](HYPOTHESES_VC.md), before any return; two addenda record the coordinator's data fixes (BTC
footprint carry, 1m holes + ATR from perp_1d) and what I had seen before them (only a BTC + ETH IS table of the
superseded run). HOLD was never read: fp.py loaders cut at 2025-01-01, funding and perp_1d rows >= 2025 are dropped
right after reading. SOL was run only after `derived/SOL_READY` existed.

## Answer first
- **Trend clusters (book #1 / VP2): none.** Rule = best IS cell trend_c2_TPV: IS **-1.2 bp, t -0.22** (n 855),
  VAL **-5.2 bp, t -1.58** (n 1,292). Every trend cell is <= 0 in IS and VAL; c = 3 is worse (IS t -2.35 / -2.52).
  The random benchmark beats it (IS 54 %, VAL 11 %).
- **Rejection clusters (book #1R / VP3): none.** Rule = best IS cell rej_c3_TPV: IS **+4.1 bp, t 0.76** (n 987),
  VAL **+1.0 bp, t 0.35** (n 1,371); years 4 / 5 positive (2024 -6.0); random 80 % IS / 90 % VAL; costs x1.5 IS +1.3,
  VAL -1.7 (fails); one step late IS +4.3, VAL +0.3; **power at VAL size 0.24** (LIVE needs 3; HOLD t would be ~1/4 of
  VAL's 0.35). IS t is far below DEMO's 2.0.
- The best IS t over all 8 cells (0.76) is below the median of the random max-over-8-cells null (p50 0.81, p95 2.11).
- **What is real but too small:** rejection clusters beat random levels in VAL (random first retests lose -3 to -4.4
  bp net per trade in VAL; rejection clusters make +1 bp), i.e. about +5 bp gross per trade on a ~90-125 bp stop,
  roughly 0.05 R. That is one fee leg, not a strategy. Trend clusters are no better than random levels.
- No PREREG_DRAFT.

## Event counts (out/<SYM>_counts.json; c = 2 / c = 3)
| sym | k bp | trend legs | trend zones | tested (filled) | rejections | rej zones | tested (filled) | hole drops |
|---|---|---|---|---|---|---|---|---|
| BTC | 3 | 1,028 | 1,021 / 816 | 782 (691) / 620 (541) | 1,577 | 1,553 / 1,207 | 1,182 (1,057) / 915 (815) | 17-25 |
| ETH | 4 | 1,070 | 1,063 / 882 | 853 (778) / 714 (652) | 1,526 | 1,503 / 1,136 | 1,227 (1,106) / 921 (825) | 6-8 |
| SOL | 7 | 1,018 | 1,012 / 830 | 806 (749) / 656 (612) | 1,480 | 1,453 / 1,077 | 1,204 (1,138) / 889 (844) | 3-6 |

Zones lost to "no cluster" (max row < c x median): ~0.5 % at c = 2, ~20-26 % at c = 3. The extreme-row exclusion
removed only 0-2 zones per cell, so the declared reading of that clause does not matter. Trades are fewer than fills
because of one open trade per symbol per cell.

## Results, pooled BTC + ETH + SOL (net bp per trade; out/report_IS.txt, out/report_VAL.txt)
t clustered by UTC entry day. "late" = market entry at the close of the fill minute. rand % = share of 200 random
draws with a lower pooled t. Stop ~ 125 bp IS / ~ 90 bp VAL on average (0.15 x ATR14); time stops < 1 %.

| cell | IS n | IS net | IS t | x1.5 | late | rand % | VAL n | VAL net | VAL t | x1.5 | late | rand % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **trend_c2_TPV (rule)** | 855 | -1.2 | -0.22 | -4.0 | -4.1 | 54 | 1,292 | -5.2 | -1.58 | -8.1 | -9.0 | 11 | -1.27 |
| trend_c2_2R | 850 | -9.6 | -1.44 | -12.6 | -8.7 | 12 | 1,284 | -9.2 | -2.30 | -12.2 | -10.9 | 0.5 | -1.82 |
| trend_c3_TPV | 743 | -13.9 | -2.35 | -16.8 | -14.7 | 2.5 | 1,017 | -6.2 | -1.62 | -9.0 | -6.6 | 13 | -1.30 |
| trend_c3_2R | 743 | -17.2 | -2.52 | -20.2 | -12.7 | 1.5 | 1,013 | -5.6 | -1.25 | -8.6 | -6.3 | 15 | -0.96 |
| rej_c2_TPV | 1,241 | 0.5 | 0.10 | -2.3 | -1.0 | 56 | 1,850 | 1.2 | 0.44 | -1.6 | -2.5 | 97 | 0.32 |
| rej_c2_2R | 1,209 | -5.2 | -0.90 | -8.2 | -6.1 | 37 | 1,809 | -2.3 | -0.68 | -5.3 | -4.2 | 66 | -0.52 |
| **rej_c3_TPV (rule)** | 987 | 4.1 | 0.76 | 1.3 | 4.3 | 80 | 1,371 | 1.0 | 0.35 | -1.7 | 0.3 | 90 | 0.24 |
| rej_c3_2R | 972 | 0.3 | 0.05 | -2.7 | 1.1 | 69 | 1,356 | 1.2 | 0.31 | -1.8 | -2.3 | 85 | 0.22 |

Max-over-8-cells random null: IS p50 0.81, p90 1.89, p95 2.11; VAL p50 0.64, p95 1.72.

### By year (pooled net bp)
| cell | 2020 | 2021 | 2022 | 2023 | 2024 | years > 0 |
|---|---|---|---|---|---|---|
| trend_c2_TPV | +2.9 | -3.4 | -4.3 | -2.7 | -8.2 | 1 / 5 |
| rej_c3_TPV | +5.5 | +3.0 | +4.5 | +3.9 | -6.0 | 4 / 5 |

### By symbol (net bp, t)
| cell | era | BTC | ETH | SOL |
|---|---|---|---|---|
| trend_c2_TPV | IS | -5.2 (-0.76) | -1.4 (-0.19) | +2.8 (0.22) |
| | VAL | -0.5 (-0.13) | -14.0 (-2.88) | -1.7 (-0.24) |
| rej_c3_TPV | IS | +10.5 (1.59) | +2.2 (0.29) | -0.4 (-0.04) |
| | VAL | -3.6 (-0.96) | -1.5 (-0.32) | +7.4 (1.12) |

No symbol carries a cell into both eras: the rejection cell's IS comes from BTC and its VAL from SOL.

### Real vs random levels (out/random_means.txt; mean net bp, random = mean over 200 draws, p5..p95)
| cell | era | real | gross (net + fees) | random |
|---|---|---|---|---|
| trend_c2_TPV | IS | -1.2 | +4.4 | -2.0 (-12.2..6.5) |
| | VAL | -5.2 | +0.5 | -1.6 (-7.0..4.5) |
| rej_c3_TPV | IS | +4.1 | +9.7 | -0.0 (-7.8..9.8) |
| | VAL | +1.0 | +6.6 | -3.6 (-9.7..2.0) |
| rej_c2_TPV | VAL | +1.2 | +6.8 | -4.4 (-9.2..0.7) |

## What failed and why
- The setup is close to a coin flip: TPV's TP hit 43-48 %, stop 52-57 % (near-zero gross implies an average target
  of ~1.1R; target distances were not tabulated). Rejection
  clusters shift that by ~1-2 points of hit rate over random levels, worth ~5 bp gross, against 4-7 bp of fees
  (maker in, taker out on stops) and 1-2 bp slippage. Trend clusters shift nothing.
- The 2R target is worse than TPV in every cell: the second R is rarely reached before the 0.15 x ATR stop.
- c = 3 vs c = 2 does not change the picture (rejection slightly better with c = 3, trend worse).

## Pitfalls / problems
- **BTC footprint carry (found by stream U):** my first BTC run used the pre-fix derived file (rows 0..33,333, ~80 %
  of zones never tested); only counts were printed, outputs deleted, all BTC numbers are from the rebuilt file
  (rows 27,315..38,644).
- **Holes in the 1m cache (found by stream MN):** zones whose leg start .. test + 24 h overlaps a gap > 30 min are
  dropped (BTC 17-25 per cell, ETH 6-8, SOL 3-6). ATR14 from perp_1d klines, rows >= 2025 dropped on read.
- Legs are greedy and non-overlapping; a long trend gives several consecutive 8-bar legs, so clusters of one trend can
  repeat. The random benchmark keeps the same structure, so the percentile is unaffected.
- The "R" column in out/report_*.txt is the mean of net / stop per trade; it can differ in sign from the bp mean
  because stop size varies (large-ATR trades weigh more in bp).

## Files
- [HYPOTHESES_VC.md](HYPOTHESES_VC.md), code: [code/vc.py](code/vc.py) (events, zones, random levels, execution),
  [code/report.py](code/report.py) (pooling, clustered t, random percentile, power), [code/check.py](code/check.py)
  (hand trace of 4 ETH trades).
- out/: `<SYM>_real.npz` (trades per cell: entry minute, net, fees, stop bp, exit kind; `_late` variants),
  `<SYM>_rand.npz` (draw, entry minute, net), `<SYM>_counts.json`, report_IS.txt / report_VAL.txt (+ json),
  random_means.txt, run_all.log.
