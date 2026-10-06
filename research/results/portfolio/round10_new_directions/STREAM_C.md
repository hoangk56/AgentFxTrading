# Round 10, stream C: combining sub-cost FX effects, cost-gated (2026-10-05)

Rules: research/results/portfolio/round10_new_directions/HYPOTHESES_C.md, written before the numbers (17:52 UTC). Two
additions came later, and each was written before its own numbers: the "extend" variant (18:20) and C6 (19:05,
post hoc relative to the pooled results). HOLD was not opened: the panel stops at 2024-12-31. PRE was not run
because nothing survived IS/VAL.

## Answer
**No candidate, so there is no PREREG draft.** None of the hypotheses reaches the IS t bar. The best IS net t over
roughly 156 trading cells is +1.65 (C4a). Chance alone gives about 2.9 for the best of 156, and a sign-flip
permutation gives a family p95 of 2.8-3.0. The combination idea fails for one main reason. The components are
nearly uncorrelated (|corr| <= 0.2, mostly < 0.05), so their edges do add up. But even summed, the edge at mid is
about 0.3-0.7 bp per trade, which is below the 0.6 bp commission alone, before any spread. Only the Sydney open
gets above 1 bp, and it happens at minutes when the spread is wide.

## Component mid screen (pooled 10 pairs, slope in bp of forward mid return per causal z unit; day-clustered t)
| comp | h15 IS | h15 VAL | h60 IS | h60 VAL | h240 IS | h240 VAL |
|---|---|---|---|---|---|---|
| REV (R3) | +0.015 (1.1) | -0.004 (-0.2) | +0.013 (0.2) | -0.038 (-0.5) | -0.198 (-1.2) | +0.021 (0.1) |
| RES (R2 s-score) | +0.020 (4.3) | +0.017 (2.5) | +0.043 (2.4) | +0.049 (1.8) | +0.131 (1.8) | +0.154 (1.4) |
| USDF (L2h-ii) | +0.043 (5.3) | +0.034 (3.2) | +0.052 (3.7) | +0.026 (1.3) | +0.049 (1.6) | +0.071 (1.7) |
| FIXV (ECB + WM/R, KMW) | +0.016 (0.9) | +0.001 (0.0) | -0.005 | +0.089 (1.0) | +0.061 | +0.215 (1.4) |
| HOME (Ranaldo) | +0.003 | +0.009 | +0.008 | +0.022 | +0.020 | +0.017 |
| WED (rollover carry) | +0.008 (0.8) | +0.013 (0.6) | +0.033 (0.8) | +0.083 (1.1) | +0.267 (1.7) | +0.291 (1.2) |
| SYD (Sydney V) | +0.342 (8.4) | +0.273 (4.9) | +0.328 (4.5) | +0.207 (2.2) | +0.208 | +0.589 (2.0) |
| HKS (periodicity) | +0.078 (6.8) | +0.051 (2.6) | +0.012 | **-0.183 (-2.9)** | -0.200 (-1.3) | **-0.682 (-2.7)** |

Median executable cost per round trip: 0.90 bp in IS and 0.82 bp in VAL. A minute with zero spread at both ends still
costs 0.6 bp.

## Results (chosen cell per family = highest IS net t; VAL checked once)
| hypothesis | cell | IS mid (t) / VAL mid (t) | IS net (t) / VAL net (t) | trades/yr IS/VAL | power trade IS/VAL (day) | yrs + | rand. ctrl IS/VAL | x1.5 / +1m net IS, VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| C1 equal-weight z sum, gate k x cost/sigma | h15 k128 | +0.68 (1.2) / +0.13 (0.2) | -0.25 (-0.4) / -0.67 (-1.2) | 162 / 560 | -0.33 / -1.50 (-0.23 / -0.92) | 4/6, 0/3 | 100 % / 78 % | -0.42, -0.77 / -0.24, -0.75 | fail |
| C2 ridge on IS, gate k x cost | h240 k3 | +1.65 (0.5) / +2.04 (0.8) | +0.57 (0.2) / +1.27 (0.5) | 93 / 249 | 0.14 / 0.59 (0.06 / 0.41) | 4/6, 2/3 | 92 % / 96 % | +0.33, +1.19 / +0.62, +1.50 | fail (IS t 0.18) |
| C2 walk-forward inside IS (fit < y, trade y) | h15 k1 / h240 k3 | 2018-21: +0.87 (2.5) / +5.76 (0.9) | -0.15 (-0.4) / +4.64 (0.7) | 816 / 39 | -0.49 / 0.71 | | | | in-sample fit is optimistic at h15 |
| C4a dollar factor at the cheapest USD pair | h240 k128 | +1.63 (2.7) / -0.02 (0.0) | +0.99 (1.65) / -0.66 (-0.7) | 289 / 460 | 0.87 / -0.54 | 3/6, 2/3 | 100 % / 35 % | +0.96, -0.68 / +1.11, -0.61 | fail; best IS t of the stream |
| C4b one bot cap 3, rank C2 forecast/cost | h240 k3 | +1.11 (0.4) / +3.24 (1.6) | +0.07 (0.0) / +2.49 (1.2) | 79 / 215 | 0.02 / 1.11 | 4/6, 2/3 | 80 % / 100 % | -0.14, +2.41 / +0.36, +2.75 | fail (IS) |
| C5 "CT" cost timing per component (cheapest minute in, patient exit) | SYD h15 | +1.01 (2.4) / +0.38 (0.9) | -0.17 (-0.4) / -0.55 (-1.3) | 67 / 132 | -0.24 / -1.07 | 3/6, 0/3 | | -0.46, -0.72 / -0.37, -0.53 | fail |
| C5 reference (no timing), best | HOME h240 | +1.38 (1.8) / +0.38 (0.4) | +0.19 (0.2) / -0.76 (-0.7) | 302 / 309 | 0.13 / -0.55 | 3/6, 1/3 | | | fail |
| C6 C1 on EURUSD + USDJPY only (post hoc) | h60 k128 | +0.87 (2.7) / -0.11 (-0.3) | +0.18 (0.6) / -0.77 (-1.9) | 374 / 847 | 0.29 / -1.46 | 3/6, 0/3 | | | fail |
| C6 C2 on EURUSD + USDJPY only | h60 k1 | +3.71 (0.9) / -1.66 (-0.5) | +2.84 (0.7) / -2.36 (-0.7) | 4 / 25 | 0.37 / -0.53 | | | | fail (too rare) |

The "extend" variant (keep the position when the gate fires again on the same side) changes the C1 and C2 cells by
less than 0.03 bp. Bots: one per pair with 1 position for C1, C2, C5 and C6; one bot with 1 position for C4a; one bot
with cap 3 for C4b. Every hold is 4 h or less and closes by 20:55 UTC, so no swap is paid.

## Cells and chance
| family | cells | best IS net t | chance benchmark |
|---|---|---|---|
| C1 | 24 | -0.43 | max of 24 normals: median 2.19, p95 3.07; day-flip permutation p95 2.85 |
| C2 | 12 (+12 walk-forward diagnostics) | +0.18 | 1.91 / 2.86; permutation p95 2.76 |
| C4a | 24 | +1.65 | 2.19 / 3.07; permutation p95 3.04 |
| C4b | 12 | +0.02 | 1.91 / 2.86 |
| C5 | 48 (24 timed + 24 reference) | +0.24 (reference) / -0.41 (timed) | about 2.5 / 3.4 |
| C6 | 36 | +0.67 | about 2.4 / 3.2 |

## Why it fails
- **Commission is the floor.** In C5, entering only when the observed spread is zero and the tick count is high,
  then exiting patiently, cuts the cost from about 0.9 bp to 0.72-0.80 bp. But the mid edge falls further, and it
  falls at exactly those minutes. RES h15 drops from +0.10 to -0.02, HKS h15 from +0.22 to +0.05, REV and WED to about
  0. The edge sits in minutes that are active and moving, which are also the minutes with wider spreads.
- **Summing does not reach 0.6 bp.** The IS ridge betas at h15, in sd units x 1e3, are REV 1.6, RES 3.7, USDF 10.2,
  FIXV 1.2, HOME 1.2, WED 2.1, SYD 62, HKS 12.8. With sigma_15 at about 4.5 bp, every non-Sydney component at the
  z clip of 3 still forecasts under 0.5 bp. The gate opens only about 600 times a year across 10 pairs, mostly at the
  Sydney open.
- **Break-even commission.** The C2 h15 k1 cell breaks even at a commission of +0.15 bp in IS and -0.09 bp in VAL,
  against 0.6 actual. At h240, VAL alone would break even at +0.95 to +1.87 bp, but the same rules lose money in IS
  even though IS is in-sample.

## Surprises and data notes
- HKS (Heston-Korajczyk-Sadka) changes sign with the horizon. It continues at 15 min (t +6.8 IS / +2.6 VAL) and
  reverses at 60-240 min in VAL (t -2.9 / -2.7). The IS ridge at h240 also put negative weight on REV and HKS. The
  documented periodicity holds only at short horizons.
- FIXV, the Krohn-Mueller-Whelan USD V of +-30 min around the ECB and WM/R fixes, is absent in 2016-24 at this
  construction: t 0.9 / 0.0. Round 3's ECB-only window was t 2.9 / 2.1, and WM/R dilutes it.
- The random-entry control rewards the cost gate itself. The C1 trades beat 100 % of random entries in IS while
  losing -0.25 bp, because the random entries pay typical costs (-0.86) and the gated trades pay less. Beating the
  control is necessary but says little for cost-gated rules.
- In C2 and C4b at h240, VAL is better than IS, with net +1.27 / +2.49 bp and the control beaten 96-100 %. IS is
  only t 0.2, so this is a 2022-24 regime effect, the dominant components being REV and HKS with negative IS
  weights. It cannot be selected from IS.
- The Sydney V at +1 minute loses less than at the base fill (-0.09 vs -0.25 bp in IS), because the spread narrows
  within a minute of 10:00 Sydney. This is post hoc and still negative.
- C3 correlation: not computed, since nothing survived.

## Files (scratchpad r10/C)
prep.py (causal features), common.py (simulator and stats), screen.py / screen.out, c1c2.py / c1c2.out,
ct.py / ct.out (C5), c4.py / c4.out, c6.py / c6.out, final.py / final.out (chosen cells, stress, controls, chance).
