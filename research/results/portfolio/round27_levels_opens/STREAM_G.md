# Round 27, stream G: gold's round-number cascade with resting orders on IC ticks

Written 2026-10-17 21:58 UTC (from `date -u`). Every cell was declared in [HYPOTHESES_G.md](HYPOTHESES_G.md) at
21:23 UTC, before any return was computed: 384 candidate cells, 48 information-only COMEX cells, the $5 placebo and
200 random-offset grids. HOLD was never loaded:
- every tick day is asserted < 2025-01-01, and the last NY session used ends 2024-12-31 17:00 New York;
- Dukascopy data is cut at 2016-01-01;
- the C3 file was read for its IS / VAL rows only.

Two process notes:
- A bug was found and fixed while the first results were being read: G2 (the fade) booked its trades on the
  approach side, which made the fade a long bought at a sell-limit price below the market. G1 was unaffected. The fix
  is in `fills.py` (trade side = -approach side for G2; protective stop at L - side x PS). G2 and every random draw
  were rerun, and two synthetic tests now cover it.
- Two readings were added after the results and are information only: a bot that arms only on $50 levels
  (`info_50only.py`), and the random control restricted to offsets $3-7 from the real levels.

## Answer
- **G1, resting stops beyond fresh $10 levels (primary set): fails.**
  - The resting stop reproduces round 25's M1 continuation over 60 minutes: mid +2.44 bp (t 2.87) IS, +1.54
    (t 1.83) VAL at c = 0.5. It does not enlarge it: there is no fast cascade at ordinary $10 levels.
  - In the first 5 minutes after the trigger the mid moves +0.35 bp (IS) and -0.08 bp (VAL).
  - Net is +0.66 (t 0.76) IS and +0.49 (t 0.58) VAL. The best primary cell has IS net t 1.03.
- **The declared dose split holds the effect.**
  - Plain $10 levels (not multiples of $50, 80 % of events) do not continue: mid about 0 at 5-15 min, about +1 bp
    at 30-60 min.
  - Levels at multiples of $50 continue by +7 to +8 bp in IS and +3 to +5 bp in VAL, mostly within 15-30 minutes.
- **18 G1 cells meet DEMO, none LIVE** (13 at $50 levels, 5 on repeat touches). Each is net > 0 at x1.5 spread and
  +1 minute and beats >= 90 % of 200 random-offset grids in IS and VAL. Power at the VAL size is <= 1.51, against
  the 3 that LIVE needs.
  - The best-supported cell is G1-XAU50 c0.5 h30 (no stop): IS net +5.99 bp (t 2.66), VAL +3.27 (t 1.81), 9/9 years
    positive, random control 0.96 / 0.995. It meets every LIVE bar except power (1.45).
  - Against chance: the family's best IS mid t is 5.56, and no draw of the per-day sign-flip null reaches it (p95
    3.11). Over 384 independent normals the p95 is 3.80.
  - PRE 2004-15 (Dukascopy, minute level, unbiased close entry): +5.35 bp (t 3.12), positive in 2004-09 and 2010-15.
  - Shifting the grid by $3-7 removes the effect: the real cell beats 100 % of those draws in IS, VAL and PRE.
- **Draft: [PREREG_DRAFT_G_gold_round50_cascade.md](PREREG_DRAFT_G_gold_round50_cascade.md).** Expected HOLD t is
  1.45 at the VAL size, 0.94 at 0.65 of it, and 0.36 at round 18's post-hoc retention; about 107 HOLD events. Not
  recommended as a reason to open HOLD on its own. The G1 family is stopped here.
- **G2, fading the first touch with resting limits: fails everywhere.**
  - In gold it is G1's mirror image: mid -2.4 bp, net -5 bp at 60 minutes. With the protective stop: mid about 0,
    net -2.5 to -3.
  - In silver the fade is positive at mid (+1 to +9 bp: no barrier continuation in silver, as Lucey & O'Connor
    2016 find), but silver's round trip is 5-9 bp. Best G2 IS net t is +0.16.
- **Silver and platinum G1: fail.** Silver mid -0.4 to -3 bp. Platinum costs 20-35 bp a round trip.
- **COMEX hours 12:00-16:59 UTC (information).** Net +2.46 bp (t 1.69) IS, +2.01 (t 1.25) VAL at c0.5 h60.
  Round 25's post-hoc lead survives on ticks at the same size; the stop entry does not make it larger.

## Fill-model checks (G1; out/fillcheck.txt)
Column definitions:
- **Slippage**: stop fill minus stop price, bp (> 0 = worse), median / p90.
- **Spread-only**: the trigger needed a spread wider than its arming value s60; the mid alone was not past the stop.
- **Wide**: the trigger tick's spread is > 2 x s60.
- **No-break**: the mid at the trigger had not passed L.
- **Delay**: median ms from the trigger to the entry fill.
- **Stop < 1 s**: the protective stop triggered within 1 s of the entry.
- **Double fills**: none are possible, since one order is armed at a time and there is no OCO. Verified: 0
  overlapping events in every bot.

| set, offset | n | slippage median / p90: L0 \| tick \| 250 \| 1000 \| +60 s | spread-only | wide | no-break | delay tick / 250 / 1000 ms | stop < 1 s | exit gaps > 10 min |
|---|---|---|---|---|---|---|---|---|
| XAU $10 c0 | 2314 | +0.24/+2.04 \| +0.27/+2.51 \| +0.26/+2.66 \| +0.22/+2.83 \| -0.30/+6.65 | 0.176 | 0.069 | 0.563 | 244 / 420 / 1163 | 0.016 | 0.0013 |
| XAU $10 c0.5 | 2289 | +0.30/+2.04 \| +0.30/+2.52 \| +0.30/+2.68 \| +0.20/+3.02 \| -0.30/+6.76 | 0.133 | 0.067 | 0.133 | 238 / 415 / 1159 | 0.012 | 0.0013 |
| XAU $10 c1 | 2229 | +0.30/+2.05 \| +0.28/+2.50 \| +0.26/+2.64 \| +0.20/+3.02 \| -0.31/+6.89 | 0.157 | 0.067 | 0.017 | 237 / 415 / 1152 | 0.009 | 0.0013 |
| XAU $50 c0.5 | 456 | +0.28/+1.73 \| +0.35/+2.41 \| +0.34/+2.57 \| +0.20/+3.53 \| +0.08/+8.35 | 0.127 | 0.037 | 0.127 | 240 / 410 / 1164 | 0.007 | 0 |
| XAG $0.50 c0.5 | 1202 | +0.65/+3.24 \| +0.63/+4.33 \| +0.63/+4.58 \| +0.61/+5.64 \| -0.25/+15.7 | 0.161 | 0.037 | 0.161 | 273 / 472 / 1248 | 0.002 | 0.0017 |
| XAG $1 c0.5 | 617 | +0.67/+3.70 \| +0.71/+4.93 \| +0.65/+5.07 \| +0.58/+6.10 \| -0.17/+15.7 | 0.159 | 0.050 | 0.159 | 265 / 468 / 1230 | 0 | 0.0016 |
| XPT $10 c0.5 | 2113 | +0.95/+5.73 \| +1.04/+6.48 \| +1.04/+6.34 \| +0.99/+6.75 \| +0.26/+12.6 | 0.312 | 0.024 | 0.312 | 386 / 608 / 1566 | 0.344 | 0.0038 |

- **Gold.** A server-side stop just beyond a fresh $10 level slips +0.3 bp at the median and 2.5-3 bp at p90,
  about the same at 0 / 250 / 1000 ms. 13-18 % of triggers need a widened spread (round 26 J: 17-27 %).
- **Latency.**
  - A "250 ms" bot fills on the second or third quote after the trigger (median 415 ms).
  - Latency does not matter at 5-60 minute holds: across the gold G1 cells L0 vs L1000 differ by a median of
    0.08 bp, p90 0.21, at most 0.34.
  - "+1 minute" is usually better than L250 for G1, because the continuation builds over minutes.
- **Platinum.** Its spread (~$2) is wider than the $1 protective-stop distance. The ps variant stops 34-52 % of
  trades within 1 s, so platinum's ps cells are unworkable by construction (declared, reported as is).
- **G2 fills (out/fillcheck.txt).** After a gold limit fill at a fresh level, the price runs $1 through the level
  within 15 minutes in 55-64 % of fills (71-78 % within 60). That is about a random walk's hitting probability over
  15 minutes ($1 against a ~$2 15-minute sd). The fade buys the cascade's first touch; for a sell limit that means
  being run over.
  - Price improvement on a limit that is jumped through is not modelled; the fill stays at the limit price, which is
    conservative for G2.

## Results table
Units and controls:
- bp per trade, t clustered by UTC day. Latency 250 ms decides.
- PRE = Dukascopy 2004-15 at minute level: (b) entry at the trigger close (unbiased); (a) stop-fill approximation
  (biased up, see the PRE section).
- Power = per-trade net Sharpe x sqrt(1.73 x events per year), at the IS and the VAL rate.
- Random control = share of the 200 random-offset grids (subsampled to the real count) whose mean net is below the
  cell's.

Full table of all 432 cells: `out/cells_rand.txt`; the primary set at every offset and hold: `out/stream_tables.md`.

### G1: the declared primary parameters (c 0.5, h 60, no stop) and the best cell of each set

| cell | n IS / VAL | mid IS / VAL (t) | IS net L0 / tick / 250 (t) / 1000 | VAL net L0 / tick / 250 (t) / 1000 | x1.5 IS / VAL ; +1 min IS / VAL | years > 0 | PRE minute level (b) (t); (a) | VAL/IS | power IS / VAL | $5 placebo IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1-XAU10 c0.5 h60 ns (primary) | 1344 / 945 | +2.44 (2.87) / +1.54 (1.83) | +0.78 / +0.70 / **+0.66 (0.76)** / +0.83 | +0.48 / +0.47 / **+0.49 (0.58)** / +0.49 | +0.07 / +0.26 ; +1.57 / +0.86 | 6/9 | +1.66 (2.12); +5.99 | 0.74 | 0.42 / 0.43 | -3.29 / -2.29 | 1.00 / 1.00 | fail |
| G1-XAU10 c1 h30 ns (best) | 1301 / 928 | +2.46 (3.47) / +1.94 (2.86) | +0.79 / +0.76 / **+0.74 (1.03)** / +0.91 | +0.90 / +0.86 / **+0.88 (1.30)** / +0.86 | +0.18 / +0.65 ; +1.73 / +1.24 | 8/9 | +1.18 (1.81); +5.65 | 1.19 | 0.57 / 1.03 | -3.20 / -2.36 | 1.00 / 1.00 | fail |
| G1-XAU50 c0.5 h60 ns | 271 / 185 | +7.38 (3.15) / +4.71 (2.12) | +5.79 / +5.68 / **+5.65 (2.41)** / +5.53 | +3.77 / +3.68 / **+3.68 (1.66)** / +3.78 | +5.09 / +3.46 ; +6.17 / +3.63 | 9/9 | +7.52 (3.40); +12.07 | 0.65 | 1.36 / 1.31 | -4.59 / -1.53 | 0.94 / **0.89** | fail (random VAL) |
| **G1-XAU50 c0.5 h30 ns (draft)** | 271 / 185 | +7.72 (3.41) / +4.29 (2.37) | +6.10 / +6.05 / **+5.99 (2.66)** / +5.85 | +3.39 / +3.25 / **+3.27 (1.81)** / +3.25 | +5.42 / +3.05 ; +6.19 / +2.87 | 9/9 | +5.35 (3.12); +9.90 | 0.55 | 1.52 / 1.45 | -4.86 / -0.85 | 0.96 / 0.995 | **DEMO** (LIVE except power) |
| G1-XAU50 c1 h15 ns (best IS t) | 262 / 183 | +7.21 (4.24) / +3.47 (2.42) | +5.30 / +5.32 / **+5.34 (3.32)** / +5.08 | +2.44 / +2.42 / **+2.43 (1.70)** / +2.42 | +4.70 / +2.22 ; +5.69 / +2.02 | 9/9 | +4.85 (3.32); +9.62 | 0.46 | 1.81 / 1.34 | -3.87 / -1.54 | 0.96 / 1.00 | DEMO |
| G1-XAU100 c0.5 h60 ns | 150 / 85 | +8.78 (3.54) / +0.91 (0.31) | +6.93 / +6.99 / **+7.01 (2.81)** / +6.96 | -0.16 / -0.13 / **-0.13 (-0.05)** / -0.03 | +6.43 / -0.35 ; +7.02 / -0.31 | 7/9 | - | -0.02 | 1.51 / -0.03 | -4.37 / -2.80 | 0.87 / 0.43 | fail |
| G1-XAU100 c1 h15 ns (best) | 143 / 85 | +8.73 (5.56) / +3.48 (1.53) | +6.96 / +6.92 / **+6.93 (4.49)** / +6.78 | +2.32 / +2.46 / **+2.45 (1.08)** / +2.46 | +6.33 / +2.24 ; +6.68 / +1.45 | 9/9 | - | 0.35 | 2.41 / 0.82 | -5.09 / -2.08 | 0.97 / 0.65 | fail (random VAL) |
| G1-FIRST c0.5 h60 ns | 1054 / 717 | +1.88 (1.89) / +1.22 (1.22) | +0.17 / +0.10 / **+0.06 (0.06)** / +0.24 | +0.14 / +0.15 / **+0.16 (0.16)** / +0.19 | -0.56 / -0.07 ; +1.21 / +0.61 | 5/9 | - | 2.84 | 0.03 / 0.12 | -3.26 / -2.28 | 1.00 / 0.89 | fail |
| G1-REPEAT c0.5 h60 ns | 290 / 228 | +4.47 (3.00) / +2.53 (1.67) | +2.98 / +2.87 / **+2.84 (1.90)** / +2.96 | +1.54 / +1.49 / **+1.51 (1.00)** / +1.42 | +2.32 / +1.30 ; +2.90 / +1.64 | 7/9 | - | 0.53 | 1.03 / 0.78 | -3.41 / -2.33 | 1.00 / 0.95 | fail |
| G1-REPEAT c1 h30 ns (best) | 283 / 228 | +5.53 (3.44) / +2.23 (1.92) | +3.96 / +4.01 / **+3.89 (2.43)** / +3.94 | +1.26 / +1.19 / **+1.21 (1.04)** / +1.09 | +3.38 / +0.99 ; +3.71 / +1.30 | 8/9 | - | 0.31 | 1.32 / 0.79 | -1.62 / -1.37 | 1.00 / 0.96 | DEMO |
| G1-XAG050 c0.5 h60 ns | 671 / 531 | -1.94 (-0.57) / -1.96 (-0.74) | -6.41 / -6.47 / **-6.60 (-1.92)** / -6.73 | -6.84 / -6.83 / **-6.70 (-2.52)** / -6.72 | -8.63 / -8.77 ; -4.13 / -6.48 | 1/9 | -0.88 (-0.38); +9.09 | - | -1.06 / -1.94 | - | - | fail |
| G1-XAG100 c1 h60 ns (best) | 342 / 257 | -0.43 (-0.08) / -2.73 (-0.73) | -4.88 / -5.23 / **-5.35 (-1.02)** / -5.68 | -7.57 / -7.43 / **-7.49 (-2.00)** / -7.61 | -7.50 / -9.57 ; -1.18 / -6.88 | 2/9 | +0.71 (0.21); +12.66 | - | -0.51 / -1.58 | - | - | fail |
| G1-XPT10 c1 h15 ns (best) | 797 / 600 | -0.76 (-0.28) / -2.32 (-1.97) | -23.5 / -23.7 / **-23.6 (-8.26)** / -23.5 | -32.7 / -32.3 / **-32.2 (-21.6)** / -32.1 | -34.8 / -46.8 ; -23.3 / -30.4 | 0/8 | - | - | -5.25 / -17.5 | - | - | fail |
| G1-COMEX c0.5 h60 ns (information) | 549 / 373 | +4.11 (2.83) / +3.01 (1.88) | +2.52 / +2.49 / **+2.46 (1.69)** / +2.63 | +1.99 / +1.96 / **+2.01 (1.25)** / +2.10 | +1.93 / +1.80 ; +3.55 / +2.27 | 8/9 | +2.21 (1.47); +7.60 | 0.82 | 0.88 / 0.93 | -0.80 / -1.99 | 1.00 / 0.96 | info |
| G1-XAU05 c0.5 h60 ns ($5 placebo) | 1376 / 957 | -1.57 (-1.64) / -1.23 (-1.47) | -3.30 / -3.32 / **-3.29 (-3.43)** / -3.18 | -2.22 / -2.27 / **-2.29 (-2.74)** / -2.25 | -3.86 / -2.52 ; -1.65 / -1.71 | 0/9 | -1.31 (-1.73); +2.84 | - | - | - | - | placebo |

The 18 DEMO cells (out/stream_tables.md):
- XAU50, no stop: c0 h15; c0.5 h15, h30; c1 h15, h30, h60.
- XAU50, with the protective stop: c0 h30; c0.5 h15, h30, h60; c1 h15, h30, h60.
- REPEAT, no stop: c0 h30, h60; c0.5 h30; c1 h30, h60.

Across them: IS net +2.65 to +6.34 bp (t 2.05-3.32), VAL +0.53 to +4.08 (t 0.47-1.88), VAL-size power 0.35-1.51.

### G2: the declared primary parameters (q 1, h 60, no stop) and the best cell of each set

| cell | n IS / VAL | mid IS / VAL (t) | IS net 250 (t) | VAL net 250 (t) | x1.5 ; +1 min | PRE (b) (t) | power IS / VAL | $5 placebo | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| G2-XAU10 q1 h60 ns (primary) | 1359 / 953 | -2.41 (-2.81) / -1.49 (-1.78) | -5.08 (-5.90) | -3.20 (-3.82) | -5.34 / -3.30 ; -4.55 / -2.77 | -4.62 (-5.92) | -3.24 / -2.90 | -1.18 / -0.54 | 0.00 / 0.04 | fail |
| G2-XAU10 q1 h15 ps (with the protective stop) | 1359 / 953 | +0.02 (0.07) / ... | -2.78 (-9.23) | -1.80 (-6.48) | - | - | - | - | - | fail |
| G2-XAU50 q1 h60 ns | 275 / 187 | -8.22 (-3.53) / -4.04 (-1.83) | -10.79 (-4.59) | -5.75 (-2.61) | -11.03 / -5.85 ; -9.86 / -4.89 | -10.53 (-4.81) | -2.60 / -2.07 | +0.27 / -0.90 | 0.03 / 0.26 | fail |
| G2-XAU100 q1 h60 ns | 151 / 86 | -9.78 (-4.01) / -1.03 (-0.35) | -12.47 (-5.08) | -2.68 (-0.93) | - | - | -2.73 / -0.71 | -0.41 / +0.16 | 0.12 / 0.60 | fail |
| G2-FIRST q1 h60 ns | 1099 / 730 | -1.70 (-1.71) / -1.18 (-1.18) | -4.40 (-4.40) | -2.94 (-2.94) | - | - | -2.42 / -2.23 | - | 0.00 / 0.14 | fail |
| G2-REPEAT q1 h60 ns | 260 / 223 | -5.39 (-3.54) / -2.49 (-1.67) | -7.96 (-5.19) | -4.05 (-2.72) | - | - | -2.80 / -2.11 | - | 0.00 / 0.11 | fail |
| G2-XAG050 q0.5 h30 ns (best) | 678 / 529 | +3.57 (1.25) / +2.60 (1.34) | -4.08 (-1.59) | -3.32 (-1.71) | -5.04 / -4.35 ; -2.72 / -2.12 | -4.99 (-2.97) | -0.92 / -1.35 | - | - | fail |
| G2-XAG100 q2 h30 ns (best of family) | 371 / 280 | +9.06 (2.04) / +2.07 (0.80) | +0.59 (0.16) | -3.72 (-1.45) | -0.40 / -4.73 ; -0.40 / -1.70 | -7.60 (-3.25) | 0.09 / -1.13 | - | - | fail |
| G2-XPT10 q1 h60 ns | 1109 / 872 | +2.64 (1.37) / +3.65 (2.40) | -21.50 (-11.3) | -24.08 (-15.1) | - | - | -6.93 / -11.5 | - | - | fail |
| G2-COMEX q1 h60 ns (information) | 557 / 378 | -4.07 (-2.82) / -2.81 (-1.76) | -6.56 (-4.47) | -4.58 (-2.86) | - | -4.91 (-3.28) | - | -3.38 / -0.76 | 0.00 / 0.06 | info |
| G2-XAU05 q1 h60 ns ($5 placebo) | 1389 / 965 | +1.37 (1.41) / +1.23 (1.47) | -1.18 (-1.25) | -0.54 (-0.64) | - | -1.89 (-2.52) | - | - | - | placebo |

## Dose and session splits (G1, L 250, out/robust.txt)
Mid path after the trigger (bp, t), c = 0.5, by roundness of the level:

| levels | IS h5 / h15 / h30 / h60 | VAL h5 / h15 / h30 / h60 |
|---|---|---|
| plain $10 (not $50), ~80 % of events | -0.31 / -0.19 / +1.05 (1.7) / +1.19 (1.4) | -0.39 / +0.50 / +1.22 (1.8) / +0.77 |
| $50 not $100 | +1.53 / +5.31 (1.7) / +7.18 (1.8) / +5.64 | +0.86 / +3.07 (1.9) / +4.77 (2.0) / +7.95 (2.6) |
| $100 | +4.14 (3.2) / +8.41 (5.3) / +8.15 (4.0) / +8.78 (3.5) | +1.59 / +3.40 (1.5) / +3.74 (1.5) / +0.91 |

- **Dose.** Net at c0.5 h15 for plain $10 / $50-not-$100 / $100: IS -1.99 / +3.38 / +6.61, VAL -0.57 / +2.02 /
  +2.36. Monotone in both eras. At $100 levels the move is fast: half of it within 5 minutes and nearly all within
  15 in IS, a cascade shape. At $50 it builds over 30-60 minutes. Most of round 25's $10 result came from the $50
  and $100 levels (plain $10 levels: +1.2 / +0.8 bp at 60 min, t <= 1.4).
- **Side (information, not declared).** For $50 levels at c0.5 h30, downward breaks carry IS: +11.85 bp (t 2.63)
  against +1.33 for upward breaks. VAL is more even: +3.71 vs +2.81. The asymmetry fits long-gold stop clusters
  below round numbers (long liquidation).
- **Sessions ($50 levels, c0.5 h30).**

  | session (UTC) | IS | VAL |
  |---|---|---|
  | Asia 23-07 | +4.59 | +1.15 |
  | London 07-12 | +1.39 | +6.68 |
  | NY 12-17 | +8.40 (t 2.51) | +2.13 |
  | late 17-23 | +8.56 | +5.62 |

  No session is stable across the eras. The full-day rule is the one to keep.
- **First vs repeat touch.** At all $10 levels:
  - first touches are flat (net +0.06, 0.16);
  - repeat touches, where the price was turned back from within $0.50 of the level before this approach, continue
    (net +2.84 t 1.90 IS / +1.51 VAL at c0.5 h60; 5 DEMO cells).

  Osler's take-profit story predicts the reversal on the first touch. The data say the first touch is merely flat,
  and the break after a rejection carries the move.
- **Robustness of the draft cell** (XAU50 c0.5 h30):
  - median trade about 0;
  - trimmed at the IS 1 / 99 % quantiles: +4.36 IS / +3.27 VAL;
  - top 5 trades: 890 of 2,227 bp;
  - without March-April 2020: IS +6.09 (t 2.66);
  - a post-hoc $50-only bot (no busy windows from plain $10 triggers): IS +6.19 (t 2.64), VAL +3.08 (t 1.76), the
    same.

## Best cell per family, cells tried, chance (out/chance.txt)
| family | candidate cells | IS mid > 0 | IS net > 0 | IS and VAL net > 0 | DEMO / LIVE | best IS net t (cell) | largest \|IS mid t\| | sign-flip null max IS mid t p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| G1 | 192 | 133 | 74 | 64 | 18 / 0 | +4.49 (XAU100 c1 h15 ns; VAL t 1.08, random VAL 0.65: fail) | +5.56 (same) | 2.07 / 3.11 (no draw >= 5.56) |
| G2 | 192 | 54 | 1 | 0 | 0 / 0 | +0.16 (XAG100 q2 h30 ns) | -5.54 (XAU100 q1 h15: G1's mirror) | 2.21 / 3.09 (declared-side best +2.47 sits at the null's 69th percentile) |

- **Max |t| of K independent normals:**

  | K | cells | p50 | p95 |
  |---|---|---|---|
  | 192 | one family | 2.91 | 3.63 |
  | 384 | both families | 3.12 | 3.80 |
  | 24 | a primary set | - | 3.06 |

- **Primary sets.** G1 best IS net t +1.03 (mid +3.50); G2 best IS net t -5.74.
- **The G1 dose cells are beyond chance in IS, not only within the family.** All ten of the best IS net t are $50 /
  $100 cells, and the dose response was declared before the numbers. VAL is about half the IS size (VAL / IS 0.3-0.7)
  and VAL t stays below 2 everywhere. That is the round-13 warning sign of a weakening effect, so the expected HOLD t
  is computed on the VAL size.

## PRE 2004-15 (minute level, labelled; out/pre_tables.txt)
Inputs: Dukascopy m1c gold closes. The ask exists from 2010; for 2004-09 the mid is bid + IC's modelled half spread.
Costs: IC's 2016-17 spread profile + 0.6 bp. The same bot runs on minute closes. (b) enters at the trigger close and
is unbiased; (a) enters at the stop price + IS median slippage.

| cell | PRE (b) net (t) | PRE mid (b) | 2004-09 (b) / 2010-15 (b) | PRE (a) | IC minute (b) IS / VAL | IC tick IS / VAL | PRE random offsets beaten, (b) |
|---|---|---|---|---|---|---|---|
| XAU $10 c0.5 h30 | +1.31 (2.04) | +2.90 (4.49) | +2.30 / +0.51 | +5.64 | +0.28 / +0.13 | +0.63 / +0.76 | 1.00 |
| XAU $50 c0.5 h15 | +4.96 (3.46) | +6.55 (4.57) | +6.92 / +3.29 | +9.51 | +1.59 / +1.29 | +5.17 / +2.18 | 1.00 |
| XAU $50 c0.5 h30 | +5.35 (3.12) | +6.94 (4.05) | +7.15 (2.30) / +3.82 (2.18) | +9.90 | +1.51 / +3.07 | +5.99 / +3.27 | 1.00 |
| XAU $50 c0.5 h60 | +7.52 (3.40) | +9.11 (4.12) | +10.12 / +5.30 | +12.07 | +1.35 / +2.93 | +5.65 / +3.68 | 1.00 |
| XAU $5 placebo, $50 subset, c0.5 h30 | -0.51 (-0.36) | +1.08 | -0.61 / -0.42 | +3.33 | -3.09 / -1.33 | -4.86 / -0.85 | - |
| G2 XAU $10 q1 h60 | -4.62 (-5.92) | -3.03 | -6.16 / -3.36 | -9.10 | -3.42 / -3.23 | -5.08 / -3.20 | - |
| XAG $0.50 G1 c0.5 h30 (2008-15) | -4.86 (-2.90) | -0.10 | -12.30 (2008-09) / -2.60 | +5.10 | -5.08 / -6.37 | -7.93 / -6.78 | - |

- **Calibration on IC 2016-24.**
  - The close-entry replica (b) understates the tick result at $50 levels in IS: +1.5 against +6.0, because most of
    the gain sits inside the trigger minute. It is close in VAL (+3.1 vs +3.3).
  - The stop-fill approximation (a) overstates at plain levels (all $10 c0.5 h30: IC (a) +3.02 vs tick +0.63) and
    is close at $50 levels (+4.00 IS / +5.73 VAL vs +5.99 / +3.27).
  - So PRE (b) is a lower bound for the stop entry, and PRE (a) an upper one.
- **Read that way, the $50-level continuation is present in 2004-15.**
  - It is larger than in 2016-24, with t > 2 in both halves and 8-9 of 12 years positive.
  - It beats every one of 200 random-offset grids at minute level.
  - The $5 placebo is flat.
- **Silver** shows no G1 continuation in PRE either.

## C3 correlation (IS + VAL rows)
The draft cell's daily net P&L correlation with C3 is -0.008 (monthly -0.141). The h15 version: +0.001 / -0.006. The
all-$10 primary: +0.016 / -0.160.

## Needs the user
- **Whether to register the draft and open HOLD.** The draft is
  [PREREG_DRAFT_G_gold_round50_cascade.md](PREREG_DRAFT_G_gold_round50_cascade.md): DEMO tier, about 107 HOLD events.
  - The expected HOLD t is 1.45 at the VAL size and 0.94 at 0.65 of it, so HOLD can only reject (net < 0), not
    confirm.
  - I recommend not opening HOLD for it alone.
- **A demo or forward log of the $50 rule on data after 2026-09-24.**
  - It needs a cBot with server-side stops at L + 0.5 x s60 on fresh $50 levels and a 30-minute timed exit.
  - About 60 trades a year. Promotion needs HOLD + demo pooled t >= 2.5, about 320 trades or ~5 years at the VAL
    Sharpe.
  - A Dukascopy gold M1 fetch would give the minute-level reading sooner.
- **Dukascopy XAUUSD ticks 2004-15** (a fetch, the user's decision). They would replace the bracketed (a) / (b)
  minute readings with a tick-level PRE for the dose cells. This is the cheapest way to tighten the evidence: the
  minute-level PRE already says the effect is larger there.
- **A cheaper gold venue.** It would not change the verdict: the $50 cells are already net-positive at IC's cost.
  The limit is the event count (~60 a year), not cost. LIVE power needs a per-trade Sharpe of ~0.29 at this rate;
  VAL gives 0.14.

## Untested ideas (not declared, so not candidates)
- **Downward breaks of $50 / $100 levels only.** The asymmetry is large in IS (+11.9 vs +1.3 bp). Picked after
  looking; it would need new data.
- **Intermediate doses ($25 multiples).** Also round numbers on other gold instruments (COMEX GC futures quotes)
  against IC spot, to see whether the cluster sits at the futures or the spot round number.
- **An exit at the next round level** (take-profit at L +- $10 for $50 breaks), or a trailing exit. Only clock exits
  and one protective stop were declared, and the stop helps in no gold cell.
- **Combinations.** The repeat-touch condition on $50 levels (n too small: 61 / 45). A book of the $50 continuation
  with the silver round-number fade (silver G2 mid +1 to +9 bp) on a venue with tight silver spreads.
- **The same resting-stop entry at index round levels.** Round 25 found index 100-point levels to be plain crossing
  momentum (half levels as strong), so the prior is low.

## Scripts and outputs
Scripts are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r27/G/code/`
and outputs in `.../r27/G/out/`. Run them from the repo root with
`PYTHONPATH=. research/.venv/bin/python <script>`.

| script | what it does |
|---|---|
| gcommon.py | HOLD-asserting tick loader, NY clock, calendar (High USD), clustered t, power, max-normal benchmark |
| build_minutes.py | pass 1: per-minute tick envelopes, 24-h rolling max / min, s60 -> `out/min_<SYM>.npz` |
| engine.py | sessions, exclusion masks, the declared bot (arming, cancel, trigger, busy, 1,440-min level rule) |
| fills.py | fills at 0 / tick / 250 / 1000 ms / +60 s, timed exits, protective stops, x1.5, PRE modes |
| test_engine.py | synthetic-tick tests (G1, G2, cancel / re-arm, busy, fills, stops, exclusions) |
| verify_brute.py | independent per-tick re-simulation on 8 real sessions: 0 event mismatches, max net difference 9e-7 bp |
| peek.py, count_proto.py, count_proto2.py, sanity_pre.py | pre-declaration checks (no returns) -> `out/count_proto*.txt` |
| run_real.py | all bots on the real / $5 / silver / platinum grids -> `out/ev_<grid>_<fam>_<c>.npz` |
| run_rand.py | 200 random-offset grids at 250 ms -> `out/rand_0_100.npz`, `out/rand_100_200.npz` |
| analyze.py | every cell, latencies, variants, power, placebo, random control, verdicts -> `out/cells_rand.txt`, `out/cells_rand.pkl` |
| digest.py, stream_tables.py | per-set digests and the tables above -> `out/digest_rand.txt`, `out/stream_tables.md` |
| robust.py | dose / side / session / touch splits, years, trimming -> `out/robust.txt` |
| chance.py | K-normal and per-day sign-flip benchmarks -> `out/chance.txt` |
| fillcheck.py | fill-model checks -> `out/fillcheck.txt` |
| pre_minute.py, pre_analyze.py | PRE minute-level replica, IC calibration, PRE random offsets -> `out/pre_*.npz`, `out/pre_tables.txt` |
| c3corr.py | C3 daily / monthly correlation (IS + VAL rows) |
| info_50only.py | post-hoc information: the $50-only bot -> `out/info_50only.txt` |
