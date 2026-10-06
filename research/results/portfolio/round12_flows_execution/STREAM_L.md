# Round 12, stream L: flow-size conditions on the sub-cost flows

2026-10-06. Hypotheses were written at 00:59 UTC, before any number:
[HYPOTHESES_L.md](HYPOTHESES_L.md); the addendum covers the checks run on the one surviving cell. HOLD was never
loaded. The panel ends 2024-12-31, and the USDCNH cache is cut at 2025-01-01 at load.

## Answer
- **LIVE: none.**
- **DEMO: one cell meets the DEMO numbers on IS/VAL: L4-G-d, gold momentum into the COMEX 13:30 ET settlement on
  top-decile move days.** Results, net of executable cost:
  - net +3.31 bp (t 3.02) IS and +2.11 bp (t 1.70) VAL, at 25 trades a year;
  - 7 of 9 years net > 0, and still > 0 at spread x1.5 and at +1 minute;
  - beats 99.4 % (IS) and 90.6 % (VAL) of look-ahead-free random entries.
  - Its power is 1.6 / 1.3, so it cannot be LIVE.
  - Draft: [PREREG_DRAFT_L_gold_settlement_bigday.md](PREREG_DRAFT_L_gold_settlement_bigday.md). The L4 family is
    stopped there. It comes with real caveats:
    - silver, the mechanism's twin, flips sign in VAL;
    - as the best of 42 cells, its IS net t sits at the edge of chance (p 0.056).
- Everywhere else, no mechanism-derived flow-size proxy reached the target of about 3x the unconditional move in
  both eras:
  - the SGE dip-buying proxy doubles the SGE auction move (uplift t 3.5 IS / 1.8 VAL), but 2x is not enough;
  - the Sydney V scales at most 1.2-1.7x;
  - the ECB fix reverses at month-end, against the prediction;
  - the index closing-window cells repeat in one era only.

## How this differs from round 10 E and from stream J
Round 10 E conditioned on how much a unit of flow moves the price: 20-day realised vol and the activity in the 60
minutes before entry. It got about 1.5x. This stream conditions on how much flow there is that day, using proxies
taken from each mechanism:
- calendar dates when the flow's owners must trade (holidays in the home venue, month- and quarter-end, index
  rebalances, option expiry, first notice);
- the prior move that the owners respond to (Chinese dip buying, the size of the New York move before Sydney,
  leveraged-ETF rebalancing proportional to the day's return, hedge top-ups after month-to-date moves).

For the Sydney cells, the overlap with E's C-RV top tercile is printed. It is near the base rate (20 % IS / 37 % VAL)
for every variable except NYabs and MExUSdown (31-33 % IS, 45-51 % VAL). Execution is fixed at the earlier rounds'
market in/out minutes, so nothing here overlaps J.

## Reproduction of the earlier unconditional numbers (mid; all match)
| effect | here IS / VAL | earlier |
|---|---|---|
| SGE long XAU 02:15-02:23 UTC | +0.91 (t 7.7) / +0.70 (4.3) | +0.91 (7.7) / +0.70 (4.3), round 10 E |
| Sydney pre leg, short AUD+NZD [T-15, T] | +1.65 (13.1) / +1.48 (10.0) | identical, round 10 E |
| Sydney post leg | +1.28 (7.6) / +1.44 (6.0) | identical |
| ECB, long EURUSD 14:00-14:15 CET | +0.73 (5.3) / +0.85 (4.1) | USD side -0.73 / -0.85, round 10 E |
| gold settlement momentum, w 15, \|z\| > 1 (round 6 timing) | +2.37 (3.8) / +0.94 (1.5) | +2.31 (3.6) / +1.00 (1.5), round 6 S1 |
| silver, same | +5.39 (3.2) / -4.21 (-3.1) | IS +2.43 on all days; VAL flips |
| AUS200 close fade | +0.82 (2.2) / +0.70 (2.7) | +0.82 (2.17) / +0.71 (2.71), round 11 H2 |
| USTEC MOC follow | +1.54 (2.7) / +0.99 (1.5) | +1.53 (2.71) / +1.00 (1.54) |
| USDCNH 01:30-08:30 UTC | +1.17 (2.6) / +2.03 (2.5) | identical, round 7 B |

For the conditional cells, the gold/silver settlement signal is made executable: z is measured to 13:14 ET and the
entry is at 13:15. Round 6 used the same minute for both.

## All 42 counted cells (mid bp with day-clustered t; "x uncond" = selected mid / all-day mid)
Net = mid - half the actual spread at entry - half at exit - 0.6 bp commission for FX and metals (0 for indices).
Power = per-trade net Sharpe x sqrt(1.73 x trades a year). One trade a day per symbol. Two-symbol legs (Sydney) have
day-clustered t.

| cell | pred | IS n/yr | IS mid (t) | x uncond | VAL mid (t) | x uncond | uplift t IS / VAL | net IS (t) | net VAL (t) | power IS / VAL |
|---|---|---|---|---|---|---|---|---|---|---|
| **L1 all days** | | 225 | +0.91 (7.7) | 1 | +0.70 (4.3) | 1 | | -0.67 (-5.5) | -0.34 (-2.1) | -3.0 / -1.6 |
| L1-DIP-q | + | 42 | +1.84 (6.0) | 2.0 | +1.36 (3.2) | 1.9 | +3.5 / +1.8 | +0.19 (0.6) | +0.32 (0.8) | +0.3 / +0.6 |
| L1-DIP-d | + | 20 | +2.36 (4.8) | 2.6 | +1.25 (1.9) | 1.8 | +3.2 / +0.9 | +0.73 (1.5) | +0.20 (0.3) | +0.8 / +0.2 |
| L1-CNH-q | + | 43 | +0.82 (2.4) | 0.9 | +0.86 (2.1) | 1.2 | -0.4 / +0.5 | -0.80 (-2.2) | -0.21 (-0.5) | -1.2 / -0.4 |
| L1-PREHOL | + | 11 | +0.36 (0.8) | 0.4 | +0.24 (0.4) | 0.3 | -1.3 / -0.7 | -1.27 (-2.7) | -0.75 (-1.1) | -1.4 / -0.8 |
| L1-POSTHOL | + | 4 | -0.02 (-0.0) | -0.0 | +0.78 (1.8) | 1.1 | -1.1 / +0.2 | -1.58 (-1.8) | -0.24 (-0.6) | -1.0 / -0.4 |
| L1-MON | + | 44 | +0.76 (2.8) | 0.8 | +0.57 (1.5) | 0.8 | -0.6 / -0.4 | -0.84 (-3.0) | -0.49 (-1.3) | -1.6 / -1.0 |
| **L2pre all days** | | 507 | +1.65 (13.1) | 1 | +1.48 (10.0) | 1 | | -0.11 (-0.9) | -0.96 (-5.7) | -0.6 / -5.7 |
| L2pre-MON | + | 101 | +1.93 (6.6) | 1.2 | +2.45 (6.1) | 1.7 | +1.1 / +2.8 | -0.12 (-0.4) | -0.65 (-1.4) | -0.3 / -1.4 |
| L2pre-POSTHOL | + | 22 | +0.92 (1.5) | 0.6 | +0.93 (1.8) | 0.6 | -1.2 / -1.1 | -1.06 (-1.7) | -1.76 (-2.4) | -1.2 / -2.2 |
| L2pre-ME | + | 44 | +0.27 (0.7) | 0.2 | +2.11 (4.8) | 1.4 | -3.9 / +1.5 | -1.38 (-3.8) | +0.06 (0.1) | -2.6 / +0.1 |
| L2pre-MExUSdown | + | 10 | -0.23 (-0.3) | -0.1 | +2.19 (2.3) | 1.5 | -2.3 / +0.7 | -1.72 (-2.1) | +0.35 (0.4) | -1.5 / +0.4 |
| L2pre-NYabs | + | 93 | +2.15 (6.0) | 1.3 | +1.83 (4.3) | 1.2 | +1.3 / +1.0 | +0.25 (0.7) | -0.83 (-2.0) | +0.5 / -2.0 |
| L2pre-NYdown | + | 96 | +2.02 (6.5) | 1.2 | +1.47 (4.2) | 1.0 | +1.0 / -0.0 | +0.25 (0.8) | -0.97 (-2.5) | +0.6 / -2.5 |
| L2pre-RBA | - | 22 | +1.08 (2.2) | 0.7 | +1.80 (2.6) | 1.2 | -1.1 / +0.5 | -0.54 (-1.1) | -0.50 (-0.6) | -0.7 / -0.6 |
| **L2post all days** | | 507 | +1.28 (7.6) | 1 | +1.44 (6.0) | 1 | | -0.18 (-1.1) | -0.29 (-1.2) | -0.8 / -1.3 |
| L2post-MON | + | 101 | +1.59 (3.8) | 1.2 | +2.36 (3.8) | 1.6 | +0.9 / +1.7 | -0.01 (-0.0) | +0.29 (0.5) | -0.0 / +0.5 |
| L2post-POSTHOL | + | 22 | +1.72 (2.2) | 1.3 | +2.10 (2.3) | 1.5 | +0.6 / +0.7 | +0.16 (0.2) | +0.29 (0.3) | +0.2 / +0.3 |
| L2post-ME | + | 44 | +0.74 (1.4) | 0.6 | +1.00 (1.1) | 0.7 | -1.1 / -0.5 | -0.68 (-1.3) | -0.48 (-0.5) | -0.9 / -0.6 |
| L2post-MExUSdown | + | 10 | +0.50 (0.4) | 0.4 | +0.10 (0.1) | 0.1 | -0.6 / -0.7 | -0.87 (-0.7) | -1.24 (-0.7) | -0.5 / -0.7 |
| L2post-NYabs | + | 93 | +1.42 (2.9) | 1.1 | +2.04 (3.1) | 1.4 | +0.4 / +1.1 | -0.12 (-0.2) | +0.18 (0.3) | -0.2 / +0.3 |
| L2post-NYdown | + | 96 | +0.12 (0.3) | 0.1 | +1.16 (2.1) | 0.8 | -3.0 / -0.6 | -1.36 (-3.1) | -0.56 (-1.0) | -2.2 / -1.0 |
| L2post-RBA | - | 22 | +2.20 (2.9) | 1.7 | +2.74 (2.3) | 1.9 | +1.2 / +1.1 | +0.79 (1.0) | +1.09 (0.9) | +0.7 / +0.9 |
| **L3 all days** | | 251 | +0.73 (5.3) | 1 | +0.85 (4.1) | 1 | | +0.08 (0.6) | +0.21 (1.0) | +0.3 / +0.8 |
| L3-ME | + | 22 | -0.80 (-1.6) | -1.1 | +0.06 (0.1) | 0.1 | -3.3 / -1.1 | -1.46 (-3.0) | -0.58 (-0.8) | -1.6 / -0.6 |
| L3-QE | + | 6 | -1.19 (-1.1) | -1.6 | -0.95 (-0.5) | -1.1 | -1.7 / -1.0 | -1.88 (-1.6) | -1.59 (-0.9) | -0.9 / -0.7 |
| L3-MExEURdown | + | 12 | -0.44 (-0.7) | -0.6 | -0.39 (-0.4) | -0.5 | -1.9 / -1.3 | -1.09 (-1.7) | -1.04 (-1.0) | -0.9 / -0.8 |
| L3-MExUSup | + | 15 | -0.43 (-0.7) | -0.6 | +0.26 (0.3) | 0.3 | -2.1 / -0.6 | -1.09 (-1.9) | -0.36 (-0.4) | -1.0 / -0.3 |
| **L4G all days** | | 247 | +0.68 (2.7) | 1 | +0.27 (0.9) | 1 | | -0.76 (-3.0) | -0.73 (-2.3) | -1.6 / -1.8 |
| L4-G-q | + | 48 | +2.34 (3.3) | 3.4 | +1.89 (2.4) | 7.1 | +2.8 / +2.4 | +0.94 (1.3) | +0.89 (1.1) | +0.7 / +0.9 |
| L4-G-d | + | 25 | +4.74 (4.3) | 7.0 | +3.14 (2.5) | 11.8 | +4.0 / +2.5 | +3.31 (3.0) | +2.11 (1.7) | +1.6 / +1.3 |
| L4-G-agree | + | 30 | +3.39 (3.4) | 5.0 | +2.78 (2.7) | 10.4 | +3.0 / +2.7 | +1.98 (2.0) | +1.77 (1.7) | +1.1 / +1.3 |
| L4-G-optex | - | 12 | -0.35 (-0.4) | -0.5 | +3.06 (1.8) | 11.5 | -1.1 / +1.7 | -1.86 (-1.9) | +2.08 (1.2) | -1.0 / +0.9 |
| L4-G-fnd | + | 17 | +2.51 (2.9) | 3.7 | +1.36 (1.0) | 5.1 | +2.2 / +0.8 | +1.03 (1.2) | +0.37 (0.3) | +0.6 / +0.2 |
| **L4S all days** | | 245 | +2.58 (4.8) | 1 | -1.52 (-2.5) | 1 | | -1.48 (-2.7) | -5.83 (-9.8) | -1.5 / -7.4 |
| L4-S-q | + | 48 | +7.14 (3.8) | 2.8 | -4.15 (-2.6) | 2.7 | +2.8 / -1.9 | +3.30 (1.8) | -8.44 (-5.2) | +0.9 / -4.0 |
| L4-S-d | + | 22 | +11.78 (4.2) | 4.6 | -4.82 (-2.2) | 3.2 | +3.5 / -1.6 | +8.08 (2.9) | -9.19 (-4.2) | +1.6 / -3.2 |
| **L5 all days** | | 218 | +0.82 (2.2) | 1 | +0.70 (2.7) | 1 | | -1.35 (-3.6) | -0.88 (-3.4) | -1.9 / -2.6 |
| L5-REBAL | + | 7 | +5.91 (2.6) | 7.2 | +0.41 (0.2) | 0.6 | +2.2 / -0.2 | +3.54 (1.6) | -1.10 (-0.6) | +0.8 / -0.5 |
| L5-ME | + | 10 | +2.18 (1.0) | 2.7 | +0.45 (0.4) | 0.6 | +0.7 / -0.2 | -0.05 (-0.0) | -1.18 (-1.0) | -0.0 / -0.7 |
| L5-MOVE | + | 41 | +0.71 (0.5) | 0.9 | +1.07 (1.7) | 1.5 | -0.0 / +0.7 | -1.99 (-1.5) | -0.60 (-0.9) | -0.8 / -0.7 |
| L5-DAY | + | 38 | +0.18 (0.1) | 0.2 | +2.17 (2.4) | 3.1 | -0.6 / +1.9 | -2.54 (-1.9) | +0.52 (0.6) | -1.0 / +0.4 |
| **L6 all days** | | 246 | +1.54 (2.7) | 1 | +0.99 (1.5) | 1 | | -0.14 (-0.2) | +0.34 (0.5) | -0.1 / +0.4 |
| L6-PUB | + | 50 | +3.25 (1.4) | 2.1 | +2.48 (1.3) | 2.5 | +0.9 / +0.9 | +1.56 (0.7) | +1.80 (1.0) | +0.4 / +0.7 |
| L6-OPEX | + | 12 | -0.29 (-0.2) | -0.2 | +3.08 (1.4) | 3.1 | -1.1 / +0.9 | -1.98 (-1.3) | +2.42 (1.1) | -0.7 / +0.8 |
| L6-ME | + | 11 | +2.14 (0.6) | 1.4 | +11.46 (2.5) | 11.5 | +0.2 / +2.3 | +0.47 (0.1) | +10.81 (2.3) | +0.1 / +1.8 |
| L6-DAY | + | 47 | +2.83 (1.9) | 1.8 | +1.44 (0.8) | 1.5 | +1.2 / +0.3 | +1.16 (0.8) | +0.76 (0.4) | +0.4 / +0.3 |
| **L6L all days** | | 247 | +0.98 (2.3) | 1 | +1.86 (2.9) | 1 | | -0.69 (-1.6) | +1.20 (1.9) | -0.9 / +1.4 |
| L6-LETF | + | 48 | +3.62 (2.5) | 3.7 | +3.79 (2.2) | 2.0 | +2.2 / +1.3 | +1.94 (1.3) | +3.11 (1.8) | +0.7 / +1.4 |
| **L7 all days** | | 259 | +1.17 (2.6) | 1 | +2.03 (2.5) | 1 | | +0.13 (0.3) | +1.02 (1.3) | +0.2 / +1.0 |
| L7-PREHOL | + | 12 | +2.65 (1.4) | 2.3 | +3.31 (0.8) | 1.6 | +0.8 / +0.3 | +1.61 (0.9) | +2.29 (0.6) | +0.5 / +0.4 |
| L7-DIV | + | 66 | +2.78 (3.1) | 2.4 | +2.98 (2.2) | 1.5 | +2.1 / +0.8 | +1.74 (1.9) | +1.97 (1.5) | +1.0 / +1.1 |

## Chance (shared across all 42 cells, 1,000 permutations; perm.py)
| statistic | best observed | null 95 % of max | p |
|---|---|---|---|
| uplift t IS (selected minus other days, signed by the predicted direction; flags shuffled across days within era) | +4.04 (L4-G-d) | 2.92 | 0.002 |
| uplift t VAL | +2.84 (L2pre-MON) | 3.12 | 0.12 |
| selected-cell net t IS (per-UTC-day sign flip) | +3.02 (L4-G-d) | 3.04 | 0.056 |
| selected-cell \|mid t\| IS (sign flip) | 6.65 (L2pre-MON; the base Sydney effect, not the conditioning) | 3.25 | |

IS uplifts beyond chance: L4-G-d +4.0, L4-S-d +3.5 (VAL flips), L1-DIP-q +3.5, L1-DIP-d +3.2, L4-G-agree +3.0. Of
those, only the gold cells keep a VAL uplift of t >= 2.4.

## Per family
- **L1 SGE auction (6 cells).**
  - Dip buying is real. When gold fell while the Chinese day session was shut (bottom quintile), the auction move
    doubles: +1.84 / +1.36 bp.
  - The dose slope is -0.36 bp per sd of the overnight move (t -3.1 IS / -1.8 VAL).
  - Net is only +0.19 / +0.32 (power 0.3 / 0.6). The decile reaches 2.6x IS but only 1.8x VAL.
  - Calendar proxies fail or go the wrong way: pre-holiday 0.4x, post-holiday ~0, Mondays 0.8x. So does USDCNH
    (0.9-1.2x).
  - Best cell: L1-DIP-q. Below cost.
- **L2 Sydney V (14 cells).**
  - The largest uplift is Mondays in VAL (pre leg 1.7x, t 2.8), against 1.2x in IS. On Mondays the spread is wider:
    1.44 vs 1.16 IS, 2.51 vs 1.83 VAL.
  - Month-end is 0.2x IS and 1.4x VAL.
  - Post-holiday, NY move size and NY direction give 0.6-1.3x.
  - RBA days (predicted smaller): pre leg 0.7x / 1.2x, post leg 1.7x / 1.9x. The side is wrong.
  - No cell is net > 0 in both eras with t > 1.
- **L3 ECB fix (4 cells).**
  - The opposite of the prediction. On the last 2 TARGET days of the month, EURUSD falls into the 14:15 CET fix:
    -0.80 bp IS (uplift t -3.3) and +0.06 VAL. This fits month-end USD demand at fixes (Krohn, Mueller & Whelan),
    on top of the everyday EUR rise.
  - Month-to-date splits are all negative.
  - No flipped cell was tested: that would be post hoc.
- **L4 settlement momentum (7 cells): DEMO numbers, see below.**
  - The dose-response is steep for gold and absent below |z| ~ 2. By |z| bin, IS / VAL mid bp:
    - 0-0.5: -0.2 / -0.5
    - 0.5-1: +0.8 / +0.7
    - 1-1.5: -0.1 / -0.4
    - 1.5-2: +1.5 / +1.0
    - 2-3: **+5.3 (t 3.5) / +5.3 (t 2.6)**
    - > 3: +14.3 / -0.1 (n 25 / 9)
  - COMEX option expiry was predicted smaller. It is smaller in IS and larger in VAL.
  - First-notice windows are 3.7x IS and 5.1x VAL, but net t is only 1.2 / 0.3.
  - Silver: top decile +11.8 (t 4.2) IS, then **-4.8 (t -2.2) VAL**. The flip on all days, which round 6 already
    saw, is sharper on the big days.
- **L5 AUS200 close fade (4 cells).**
  - Index-rebalance days: +5.9 bp IS (7x, t 2.6), +0.4 VAL (n 7-8 a year).
  - Large-day: 0.2x IS, 3.1x VAL.
  - Nothing holds in both eras.
- **L6 USTEC MOC (5 cells).**
  - Month-end VAL +11.5 bp (t 2.5), IS +2.1 (t 0.6).
  - Option-expiry Fridays -0.3 IS / +3.1 VAL.
  - L6-LETF (follow the day's direction 15:52-16:00 on top-quintile days): 3.7x / 2.0x, net +1.94 (t 1.3) / +3.11
    (t 1.8). It fails the IS t bar. The +1 minute variant is -1.92 IS.
- **L7 USDCNH (2 cells).** Dividend season (June-August) is 2.4x / 1.5x, net +1.74 (t 1.93) / +1.97 (t 1.48). That is
  just under DEMO's IS t of 2.0, and it is a seasonal split of a t-2.6 effect, consistent with summer depreciation
  episodes (2016, 2018, 2019, 2023). Not a candidate.

## L4-G-d: full checks (l4_checks.py, l4_random.py)
| check | IS | VAL |
|---|---|---|
| n (per year) | 150 (25) | 78 (26) |
| mid / net bp (t) | +4.74 (4.31) / **+3.31 (3.02)** | +3.14 (2.53) / **+2.11 (1.70)** |
| median net; share > 0 | +1.82; 56 % | +0.40; 53 % |
| per-trade Sharpe at mid: selected vs all days; sd bp | 0.35 vs 0.07; 13.4 vs 9.6 | 0.29 vs 0.03; 11.0 vs 8.6 |
| per-trade net Sharpe; power (trade = day) | 0.247; 1.62 | 0.193; 1.29 |
| spread x1.5; +1 minute | +2.90; +1.27 (t 1.12) | +1.90; +1.38 (t 1.08) |
| winsorised 2.5/97.5 % | +3.00 (t 3.15) | +2.20 (t 1.89) |
| spread on selected days vs all | 0.82 vs 0.84 | 0.43 vs 0.39 |
| years net > 0 | 2016 +5.0, 2017 -0.1, 2018 +4.2, 2019 +5.9, 2020 +7.2, 2021 -2.0 | 2022 +0.8, 2023 +1.0, 2024 +5.2 |
| long / short trades, net | +1.55 / +5.13 | +0.89 / +3.39 |
| 30 min after the settlement, same side | -1.27 (t -0.97) | +1.91 (t 1.51) |
| time placebo: 22 other window ends, 10:30-16:00 ET (side and decile recomputed) | rank 1 of 23 (next +2.19; 13:30-13:45 reverses -3.09, t -3.4) | rank 2 of 23 (15:45-16:00 ET +3.00, t 4.12) |
| random entry (a): window end 10:30-16:00, side recomputed, 500 seeds | beats 99.4 % (null mean +0.02) | beats 90.6 % (null mean +0.39, 95 % +2.57) |
| random entry (b): window after the signal, same side | beats 100 % | beats 100 % |
| XPTUSD control, same rule at 13:05 ET | -7.6 (t -1.9) | -1.5 (t -0.5) |
| C3 correlation, IS+VAL | daily +0.015, monthly -0.14 | |

Sensitivity is descriptive, not cells. The net t, IS / VAL, by top-|z| share q and window w (min):

| q | w 5 | w 10 | w 15 | w 30 |
|---|---|---|---|---|
| 0.05 | 0.9 / 1.4 | 2.5 / 2.5 | 3.5 / 1.5 | 3.2 / 1.2 |
| 0.10 | 0.2 / 0.8 | 2.1 / 2.3 | 3.0 / 1.7 | 2.2 / 0.3 |
| 0.15 | -0.8 / 0.2 | 1.4 / 1.9 | 2.4 / 1.1 | 1.2 / -0.2 |
| 0.20 | -1.4 / -0.3 | 0.6 / 1.4 | 1.3 / 1.1 | 0.4 / 0.6 |

The edge sits in the 15-5 minutes before the settlement and in the most extreme days.

**Pitfall found here:** the first random-entry control drew windows from 08:30 ET with the trade's own side, which is
set at 13:14. Windows before the signal then contain the move that defines the side, and they gave a null mean of
+1.67 bp in VAL ("beats 61.8 %"). Random controls for conditional-side rules must recompute the side at the random
time or sample after the signal, the same lesson as round 10's time placebo.

## Surprises and data notes
- **Sydney V cost depends on the season.** In the Australian summer, 10:00 Sydney is 23:00 UTC, within about an hour
  of the NY rollover. The pre leg then costs 2.4 bp IS and 3.9 bp VAL, against 1.2 / 1.0 in the Australian winter
  (00:00 UTC).
  - The winter pre leg nets +0.18 (t 1.1) / +0.49 (t 2.2), although its mid move is smaller (+1.36 vs +1.96 IS).
  - This is descriptive and post hoc, but stream J should know it: the whole loss is the summer spread.
- **ECB fix at month-end** goes the opposite way from the daily EUR rise (above).
- **Gold after the settlement on big days**: it reverses in IS (-3.1 bp, t -3.4, at 13:30-13:45), a price-pressure
  signature, but not in VAL (+0.6).
- **Silver's VAL flip** (momentum turns into reversal on the biggest days) is the main reason to doubt that the gold
  cell is a leveraged-ETF effect rather than a 2016-21 artefact. Gold's VAL holds on its own.

## Directions that need the user
1. **Dukascopy XAUUSD M1 2004-2015** (free, same feed as research/data/duka). This would give a PRE check of L4-G-d,
   which has 25 events a year, about 300 in PRE. Only XAU H1 is local, and a 15-minute window cannot be tested on H1.
   This is the cleanest next test of the draft, and it is a new price series.
2. **Leveraged gold/silver fund AUM and daily creations** (ProShares UGL/GLL/AGQ/ZSL holdings files, public). They
   would size the rebalancing flow directly (L(L-1) x AUM x r), instead of using |z|, and might explain silver's flip.
3. **SGE daily premium / withdrawal data** (SGE website): a direct Chinese-demand measure for the SGE auction. It
   could beat the 2x dip proxy.

## Scripts and outputs (scratchpad r12/L/)
lib.py, runner.py (cell statistics); l1_sge.py -> l1_out.txt; l2_syd.py -> l2_out.txt; l3_ecb.py -> l3_out.txt;
l4_settle.py -> l4_out.txt; l56_index.py -> l56_out.txt; l7_cnh.py -> l7_out.txt; perm.py -> perm_out.txt;
l4_checks.py -> l4_checks_out.txt; l4_random.py -> l4_random_out.txt; table.py -> table_out.md; cal_L.json (ASX, NYSE
holidays from `holidays` 0.105); calendars_A.json (round 10 A's XSHG calendar).
