# STREAM_MN: multiple nodes (book setup #2), round 75

Written 2026-11-03 17:00 UTC; the 3-symbol pool (SOL added once `derived/SOL_READY` existed, SOL k = 7 bp) was
added about 17:05 UTC. Rules: HYPOTHESES_MN.md (16:53 UTC, addendum 16:57 UTC).

## Verdict, BTC + ETH + SOL pooled: none. Every cell loses money in IS and in VAL, on every symbol

| cell | IS n | IS net bp (R) | IS t | VAL n | VAL net bp (R) | VAL t | years + | rand pct IS / VAL / all | VAL power |
|---|---|---|---|---|---|---|---|---|---|
| n2_TPV | 2347 | -8.03 (-0.076) | -2.40 | 5008 | -5.42 (-0.081) | -3.34 | 0/5 | 74.0 / 67.0 / 77.0 | -2.69 |
| n2_2R | 2164 | -9.92 (-0.079) | -2.44 | 4526 | -5.06 (-0.071) | -2.40 | 0/5 | 59.0 / 80.0 / 77.5 | -1.95 |
| n3_TPV | 154 | -20.31 (-0.191) | -1.79 | 544 | -7.09 (-0.086) | -1.58 | 0/5 | 37.0 / 67.5 / 52.5 | -1.25 |
| n3_2R | 153 | -19.57 (-0.198) | -1.33 | 535 | -2.10 (-0.038) | -0.37 | 1/5 | 42.0 / 93.5 / 82.0 | -0.30 |

Of the four cells, n3_2R has the best IS t (-1.33). In the max-over-4-cells random null, that t beats 32.5 % of draws.
SOL alone, IS / VAL net bp (t):
- n2_TPV: -16.5 (t -1.70) / -6.95 (t -2.01)
- n2_2R: -19.1 (t -1.63) / -7.70 (t -1.72)
- n3_TPV: -45.8 (t -1.30) / -11.1 (t -1.12)
- n3_2R: -25.1 (t -0.53) / -0.13 (t -0.01)

SOL zones: n=2 3,988 (3,226 trades kept after the filters), n=3 319 (245). The gap filter dropped 13 zones and 1 trade.
Full tables are in out/stats_ALL_3sym.txt and out/stats_IS_3sym.txt.

The BTC + ETH section below was written before SOL arrived. Its numbers are unchanged.

## BTC + ETH only (first report): none. Every cell loses money in IS and in VAL
No cell reaches the DEMO bar (IS t >= 2.0). The best IS cell, n3_TPV, has t -1.23. The fee-free gross is 0 to +3 bp
per trade against about 6.5 bp of cost, and the stop is 60-90 bp. SOL cannot rescue the pool: it would need IS
t >= 2 on its own while BTC and ETH both sit at t -0.5 to -1.5.

| cell | IS n | IS net bp (R) | IS t | VAL n | VAL net bp (R) | VAL t | years + | rand pct IS / VAL / all | VAL power |
|---|---|---|---|---|---|---|---|---|---|
| n2_TPV | 1773 | -5.29 (-0.072) | -1.73 | 3170 | -4.54 (-0.078) | -3.03 | 1/5 | 76.0 / 87.5 / 92.5 | -2.40 |
| n2_2R | 1630 | -6.92 (-0.070) | -1.78 | 2861 | -3.52 (-0.065) | -1.78 | 0/5 | 62.0 / 97.5 / 93.0 | -1.42 |
| n3_TPV | 119 | -12.83 (-0.178) | -1.23 | 348 | -4.83 (-0.096) | -1.15 | 2/5 | 67.0 / 85.5 / 88.5 | -0.92 |
| n3_2R | 118 | -17.92 (-0.201) | -1.40 | 339 | -3.24 (-0.078) | -0.62 | 1/5 | 44.5 / 89.5 / 81.5 | -0.50 |

The stress test (costs x1.5) and the one-step-late entry are worse in every cell (the IS n2 cells have t -2.2 to
-2.7). Max-over-4-cells null: the IS real best (-1.23) beats 34.5 % of draws. By symbol, every cell is negative in
both eras for both BTC and ETH. Full tables (per symbol, per year, exit mix) are in out/stats_ALL_BTC_ETH.txt.

## What the random benchmark says
The first retest of a random level loses more (the median random t is -2.4 in IS and -4.2 in VAL for n2_TPV; random
net is -6 to -21 bp). The real nodes beat 85-97 % of the random draws in VAL, so the node row is slightly "less bad"
than a random retest, by about 1-3 bp gross. That is a real but tiny difference, a fraction of the 6.5 bp of costs, and
the IS percentiles (44-76 %) do not confirm it.

## Counts and data notes
- Zones on BTC / ETH: n=2: 4,398 / 4,473 zones over 2020-24 (3,240 / 3,480 filled with ATR); n=3: 329 / 336 zones.
  Almost every zone departs, ~93 % get tested, and ~80 % of the tests fill (>= 1 bp through).
- The 1m cache has gaps: BTC misses 23 whole UTC days and ETH 7 (2020-04/05, 2020-11, 2022-08..11), contrary to the
  BRIEF. Handling: ATR comes from the daily klines, and zones or trades spanning a > 30 min hole are dropped
  (BTC 17 zones + 1 trade, ETH 4 + 3).
- An early BTC plumbing run used the void BTC footprint; it was deleted and everything was rerun on the rebuilt
  files (assert: 0 bars with the POC outside [low, high]).
- The vectorised engine matches a brute-force loop on 400 zones per symbol: zero mismatches in fill minute and net
  (code/check.py).

## Files
code/mn.py (engine), code/stats.py, code/check.py; out/{BTC,ETH,SOL}USDT_{real,rand}.npz, out/stats_{IS,ALL}_3sym.txt, out/stats_IS_BTC_ETH.txt,
out/stats_ALL_BTC_ETH.txt, out/run_*.log. No PREREG_DRAFT.
