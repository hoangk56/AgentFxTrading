# Round 26, stream S: scheduled releases on IC ticks (news straddle, overshoot fade)

Written 2026-10-17 20:33 UTC (`date -u`). All 630 cells were declared in [HYPOTHESES_S.md](HYPOTHESES_S.md) at
20:15 UTC, before any return was computed. Addendum 1 (post hoc, information only: orders armed at T) was written
at 20:28 UTC, before it was computed. HOLD stayed closed:
- every tick day loaded is < 2025-01-01 (asserted in the loader);
- placebo days and random windows reaching 2025 were dropped;
- the PRE check opened only the Dukascopy `m1c` AUDUSD / NZDUSD / XAUUSD files (asserted < 2016), never `*_2026`;
- the C3 trade list was filtered to its IS / VAL rows at load.

## Answer
**No LIVE or DEMO cell. No PREREG_DRAFT.** All 627 cells with trades fail at the primary latency (L = 250 ms).

- **S1, OCO stop straddle: the move after the trigger is real but too small.** Gross is +0.2 to +1.0 bp per trade
  (USD pool S1-m1-h5: IS +0.97, t 2.20; VAL +0.57). IC's release round trip costs more:
  - 1.1-3.0 bp in IS on FX, gold and the US indices (0.3-3.0 in VAL, where US30 fell to 0.3 and USTEC to 0.95);
  - 3.6-7.9 bp on oil;
  - 25-57 bp on natural gas.

  Best IS net t +0.59 (US30 S1-m1-h5-ns): IS +0.45 bp, VAL +2.28 (t 1.31), positive in 4 of 9 years, and 5 trades
  make 841 of its 924 bp.
- **S1's side is mostly set before the number.** With orders resting from T-2, 52-96 % of USD-release triggers at
  m <= 0.5 come between T-2 and T, from pre-release drift and widening (73-96 % without gold, whose m = 0.5 share is
  0.52; the addendum's "73-96 %" left gold out). Even at m = 1, 20-52 % of USD-release triggers come before T.
  - A widening alone (spread-only trigger) is rare: 0 % on FX, metals, indices and oil, 1-4 % on XNG.
  - Widening helps 8-49 % of triggers (spread-assisted).
- **S2a, resting limit fade: adversely selected.** IS gross is negative in 143 of 168 cells and IS net is negative in
  all 168. On the USD pool the event fills do worse than almost every random-time seed (random beat 0.00-0.01): at a
  release a limit fills when the price runs through it, and the price keeps going.
- **S2b, market fade at T+1 min: the first minute continues in IS.** On the USD pool, gross is -1.2 to -2.8 bp at
  h 3-5 (t -1.7 to -3.1). Best IS net t +1.18 (Brent, 9 trades). The PRE minute check (2007-15) shows a weak
  reversal instead on AUDUSD / NZDUSD at h 15. The sign changed between eras, and it is below cost in IS / VAL.
- **Placebo days, same orders and clock but no release, lose about as much as release days.** USD pool S1-m1-h5:
  -1.03 bp per trade on events, -0.73 on placebo days. Among the best cells, only US30 S1 beats its placebo on a
  real sample (+1.93 bp, t 2.10), and that cell fails its own bars. Gold S2b's +39.6 bp gap rests on 4 placebo
  trades.
- **Chance.** K = 627. The max |t| of K normals has p95 3.93; the sign-flip null per event day has p50 3.04 and p95
  3.99. Best declared-side IS net t: +0.59 (S1), < 0 (S2a), +1.18 (S2b). The largest |IS gross t|, 4.01 (Brent S1
  m0.25 h15 ps), has the wrong sign and sits at the null's 95.6th percentile.

## Fill-model checks (S1, orders to T+2 min, all events of each primary set)
The table uses m = 0.5. "Pre-release" means the trigger came before T. "Spread-assisted" means the mid at the
trigger tick had moved less than k in the trigger direction (the widening did the rest). "Spread-only" means the mid
had not moved in that direction at all. "Double" counts both OCO legs filled before the cancel took effect.

| set.instrument | triggered | pre-release | spread-assisted | spread-only | double L250 / L1000 | slippage beyond stop, median L0 / L250 / L1000 (p90 L250), bp | spread at T-2 / at trigger, median bp |
|---|---|---|---|---|---|---|---|
| USD.AUDUSD | 0.99 | 0.73 | 0.40 | 0.00 | 0.012 / 0.024 | 0.21 / 0.31 / 0.35 (5.7) | 0.15 / 0.58 |
| USD.NZDUSD | 0.99 | 0.79 | 0.49 | 0.00 | 0.008 / 0.027 | 0.26 / 0.32 / 0.35 (3.7) | 0.57 / 1.16 |
| USD.XAUUSD | 0.99 | 0.52 | 0.26 | 0.00 | 0.005 / 0.020 | 0.44 / 0.66 / 0.72 (12.6) | 0.62 / 1.08 |
| USD.US30 | 0.99 | 0.75 | 0.10 | 0.00 | 0.004 / 0.013 | 0.20 / 0.27 / 0.30 (2.2) | 0.73 / 0.81 |
| USD.USTEC | 0.99 | 0.79 | 0.08 | 0.00 | 0.007 / 0.008 | 0.25 / 0.34 / 0.42 (2.4) | 1.64 / 1.72 |
| AUD.AUDUSD | 0.96 | 0.34 | 0.37 | 0.00 | 0.004 / 0.011 | 0.62 / 1.19 / 1.45 (13.6) | 0.32 / 1.36 |
| NZD.NZDUSD | 0.86 | 0.17 | 0.40 | 0.00 | 0 / 0 | 1.92 / 2.97 / 3.53 (24.3) | 0.99 / 2.35 |
| EIA.XTIUSD | 0.98 | 0.30 | 0.14 | 0.00 | 0.014 / 0.014 | 2.80 / 3.78 / 5.04 (29.5) | 4.34 / 5.89 |
| EIA.XBRUSD | 0.97 | 0.26 | 0.19 | 0.00 | 0.020 / 0.023 | 2.37 / 4.04 / 4.89 (22.3) | 3.99 / 6.00 |
| GAS.XNGUSD | 1.00 | 0.50 | 0.32 | 0.01 | 0.039 / 0.052 | 4.86 / 5.74 / 6.22 (63.4) | 17.3 / 38.8 |

- **Pre-release share** at m = 0.25 and m = 1.0:

  | sets | m = 0.25 | m = 1.0 |
  |---|---|---|
  | USD instruments | 0.85-0.96 | 0.20-0.52 |
  | AUD | 0.69 | 0.09 |
  | oil | 0.71-0.72 | 0.05-0.08 |
  | gas | 0.85 | 0.09 |

  At m = 0.25 almost every event fills (0.97-1.00); at m = 1.0, 0.71-0.93 do.
- **Spread-only triggers** are 0.00 on every set and k except XNG: 0.04 at m = 0.25 and 0.01 at m = 0.5. At T-2 the
  spread is small next to k. The widening near T assists, it does not trigger alone.
- **Double fills** are at most 2.7 % of triggered events on FX, metals, indices and oil (L = 1000 ms), and 4-8 % on
  XNG at m = 0.25.
- **Slippage beyond the stop by event type** (m = 0.5, median bp at L0 / L250 / L1000). The large releases slip
  most:

  | release | instrument | L0 / L250 / L1000 |
  |---|---|---|
  | NFP | AUDUSD | 1.57 / 2.77 / 4.24 |
  | NFP | NZDUSD | 1.14 / 2.35 / 2.90 |
  | NFP | XAUUSD | 3.65 / 7.42 / 10.20 |
  | NFP | US30 | 1.02 / 1.35 / 1.82 |
  | NFP | USTEC | 1.01 / 1.38 / 1.56 |
  | core CPI | XAUUSD | 0.85 / 1.81 / 1.77 |
  | AUD CPI | AUDUSD | 3.35 / 7.13 / 10.38 |
  | AUD jobs | AUDUSD | 1.13 / 2.52 / 2.86 |
  | EIA crude | XTIUSD | 2.80 / 3.78 / 5.04 |
  | EIA crude | XBRUSD | 2.37 / 4.04 / 4.89 |
  | gas storage | XNGUSD | 4.86 / 5.74 / 6.22 |

  The minor USD releases (CB confidence, durable goods, PMIs, UoM) slip 0.05-0.4 bp. Full table:
  `out/fillcheck.txt`.
- **Release round trip** (gross minus net per S1 trade, family mean IS / VAL, bp):

  | set | IS / VAL |
  |---|---|
  | USD.AUDUSD | 1.71 / 1.53 |
  | USD.NZDUSD | 2.37 / 2.98 |
  | USD.XAUUSD | 2.29 / 1.56 |
  | USD.US30 | 1.09 / 0.32 |
  | USD.USTEC | 2.96 / 0.95 |
  | AUD | 2.34 / 1.91 |
  | EIA pool | 7.62 / 3.60 |
  | XNG | 25.3 / 56.7 |

## Results table: best cell per set and family
The best cell is picked by IS net t at L = 250 ms; the full 630-cell table is in `out/cells_table.txt`.
- "mid" is the gross mid-to-mid return per trade (bp, day-clustered t).
- Net is shown at L 0 / one tick / 250 / 1000 ms.
- "x1.5" is the net at spread x1.5 (L = 250).
- Power = per-trade (or per-day) net Sharpe x sqrt(1.73 x trades (days) per year), at the IS and VAL size.
- Random beat = the share of 500 random-time seeds (30 candidate minutes per slot, +-4 h) whose per-trade mean net
  is below the event's, IS / VAL / all.
- Placebo = the share of 200 placebo-day seeds beaten, and the mean net per placebo trade.

| set | best cell | IS / VAL trades | IS mid 250 | IS net L0 / tick / 250 / 1000 | VAL mid 250 | VAL net L0 / tick / 250 / 1000 | x1.5 IS / VAL | VAL/IS | power IS / VAL trade | power IS / VAL day | random beat IS / VAL / all | placebo beat / mean | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| USD.AUDUSD | S1-m1-h5-ns | 471 / 313 | +0.84 (+1.47) | -0.51 (-0.86) / -0.79 (-1.37) / -0.84 (-1.46) / -0.92 (-1.58) | -0.66 (-0.44) | -1.52 (-0.95) / -1.85 (-1.19) / -2.17 (-1.43) / -2.26 (-1.58) | -1.38 / -2.63 | +2.59 | -0.78 / -1.09 | -0.78 / -1.09 | 0.89 / 0.00 / 0.14 | 0.00 / -0.63 | fail |
| USD.AUDUSD | S2a-m2-h15 | 249 / 277 | -0.27 (-0.30) | -2.29 (-2.44) / -2.33 (-2.47) / -2.32 (-2.47) / -2.31 (-2.45) | -1.03 (-0.60) | -5.91 (-3.32) / -6.00 (-3.37) / -5.93 (-3.32) / -6.03 (-3.38) | -2.43 / -5.96 | +2.56 | -1.33 / -2.47 | -1.32 / -2.51 | 0.20 / 0.00 / 0.00 | 0.10 / -3.34 | fail |
| USD.AUDUSD | S2b-c3-h15 | 43 / 147 | +2.16 (+0.79) | +1.03 (+0.38) / +1.02 (+0.37) / +1.10 (+0.40) / +1.11 (+0.41) | -0.10 (-0.07) | -1.13 (-0.73) / -1.03 (-0.67) / -1.04 (-0.68) / -0.66 (-0.44) | +0.86 / -1.21 | -0.95 | +0.21 / -0.52 | +0.22 / -0.52 | 0.61 / 0.40 / 0.49 | 0.54 / -1.17 | fail |
| USD.NZDUSD | S1-m0.25-h15-ns | 547 / 322 | +0.68 (+0.89) | -0.71 (-0.94) / -0.82 (-1.08) / -0.97 (-1.28) / -0.94 (-1.26) | -1.19 (-0.60) | -2.68 (-1.33) / -2.66 (-1.34) / -2.90 (-1.45) / -2.98 (-1.51) | -1.49 / -3.45 | +2.99 | -0.70 / -1.13 | -0.69 / -1.10 | 0.84 / 0.00 / 0.03 | 0.01 / -0.93 | fail |
| USD.NZDUSD | S2a-m2-h15 | 228 / 271 | -1.36 (-1.32) | -4.04 (-3.77) / -4.05 (-3.76) / -4.04 (-3.76) / -4.06 (-3.74) | -0.39 (-0.23) | -6.36 (-3.40) / -6.49 (-3.48) / -6.35 (-3.39) / -6.49 (-3.47) | -4.24 / -6.52 | +1.57 | -1.99 / -2.54 | -1.99 / -2.58 | 0.06 / 0.00 / 0.00 | 0.00 / -2.55 | fail |
| USD.NZDUSD | S2b-c3-h15 | 49 / 139 | +2.27 (+0.95) | +0.64 (+0.27) / +0.73 (+0.30) / +0.70 (+0.30) / +0.88 (+0.38) | -2.24 (-1.21) | -4.01 (-2.14) / -3.79 (-2.03) / -3.87 (-2.07) / -3.40 (-1.84) | +0.22 / -4.39 | -5.51 | +0.15 / -1.57 | +0.16 / -1.57 | 0.54 / 0.16 / 0.31 | 0.99 / -9.57 | fail |
| USD.XAUUSD | S1-m0.5-h15-ps | 540 / 320 | +1.61 (+1.85) | +0.01 (+0.01) / -0.67 (-0.76) / -0.79 (-0.90) / -1.21 (-1.38) | -1.51 (-1.17) | -1.78 (-1.35) / -2.85 (-2.12) / -3.18 (-2.43) / -4.01 (-3.09) | -1.69 / -3.71 | +4.01 | -0.49 / -1.90 | -0.48 / -1.84 | 0.96 / 0.00 / 0.35 | 0.09 / -1.18 | fail |
| USD.XAUUSD | S2a-m2-h15 | 229 / 215 | +0.37 (+0.20) | -4.05 (-2.20) / -4.09 (-2.23) / -4.10 (-2.23) / -4.18 (-2.26) | +0.71 (+0.31) | -4.63 (-1.96) / -4.79 (-2.02) / -4.78 (-2.02) / -4.89 (-2.07) | -4.33 / -4.89 | +1.17 | -1.21 / -1.56 | -1.19 / -1.53 | 0.34 / 0.31 / 0.29 | 0.04 / -2.05 | fail |
| USD.XAUUSD | S2b-c3-h15 | 40 / 70 | +1.27 (+0.32) | -0.52 (-0.13) / -0.55 (-0.14) / -0.39 (-0.10) / -0.28 (-0.07) | -4.31 (-1.35) | -5.56 (-1.73) / -5.42 (-1.70) / -5.41 (-1.69) / -4.46 (-1.43) | -0.92 / -5.67 | +13.80 | -0.05 / -1.35 | -0.05 / -1.30 | 0.35 / 0.34 / 0.26 | 1.00 / -47.85 | fail |
| USD.US30 | S1-m1-h5-ns | 459 / 314 | +1.55 (+2.03) | +0.72 (+0.94) / +0.48 (+0.63) / +0.45 (+0.59) / +0.33 (+0.43) | +2.60 (+1.49) | +2.19 (+1.23) / +2.38 (+1.36) / +2.28 (+1.31) / +2.31 (+1.33) | -0.10 / +2.13 | +5.05 | +0.31 / +0.99 | +0.32 / +0.99 | 0.99 / 1.00 / 1.00 | 1.00 / -0.68 | fail |
| USD.US30 | S2a-m0.5-h15 | 489 / 321 | +0.18 (+0.19) | -1.80 (-1.82) / -1.81 (-1.81) / -1.80 (-1.81) / -1.84 (-1.84) | -1.63 (-0.77) | -2.90 (-1.35) / -3.08 (-1.44) / -2.92 (-1.36) / -3.24 (-1.51) | -2.06 / -2.99 | +1.62 | -0.97 / -1.03 | -0.97 / -1.03 | 0.33 / 0.00 / 0.02 | 0.03 / -1.27 | fail |
| USD.US30 | S2b-c2-h15 | 134 / 168 | -2.48 (-1.23) | -3.54 (-1.74) / -3.74 (-1.84) / -3.64 (-1.80) / -3.78 (-1.84) | -0.82 (-0.46) | -1.16 (-0.64) / -1.14 (-0.63) / -1.11 (-0.62) / -0.73 (-0.41) | -4.23 / -1.26 | +0.31 | -0.96 / -0.47 | -0.97 / -0.47 | 0.29 / 0.36 / 0.32 | 0.06 / +0.77 | fail |
| USD.USTEC | S1-m1-h5-ns | 474 / 321 | +1.42 (+1.58) | -1.20 (-1.32) / -1.43 (-1.58) / -1.46 (-1.62) / -1.56 (-1.72) | +1.28 (+0.44) | +0.17 (+0.06) / +0.63 (+0.22) / +0.32 (+0.11) / +0.52 (+0.18) | -2.90 / -0.17 | -0.22 | -0.87 / +0.08 | -0.87 / +0.08 | 0.94 / 0.92 / 0.98 | 0.51 / -0.74 | fail |
| USD.USTEC | S2a-m2-h15 | 232 / 289 | -2.15 (-1.03) | -5.59 (-2.64) / -5.74 (-2.70) / -5.71 (-2.69) / -5.79 (-2.72) | +1.30 (+0.34) | -2.71 (-0.73) / -4.67 (-1.35) / -3.10 (-0.84) / -3.58 (-0.97) | -6.32 / -3.34 | +0.54 | -1.47 / -0.64 | -1.45 / -0.63 | 0.17 / 0.19 / 0.11 | 0.55 / -4.52 | fail |
| USD.USTEC | S2b-c2-h15 | 126 / 189 | -4.31 (-1.88) | -7.15 (-3.10) / -7.13 (-3.08) / -7.24 (-3.14) / -7.24 (-3.13) | -1.10 (-0.50) | -2.14 (-0.97) / -2.14 (-0.97) / -2.14 (-0.97) / -1.86 (-0.85) | -8.70 / -2.66 | +0.30 | -1.69 / -0.74 | -1.68 / -0.74 | 0.23 / 0.43 / 0.23 | 0.00 / +1.93 | fail |
| USD.pool | S1-m1-h5-ns | 2350 / 1570 | +0.97 (+2.20) | -0.68 (-1.52) / -1.01 (-2.27) / -1.11 (-2.52) / -1.30 (-2.92) | +0.57 (+0.58) | -0.60 (-0.57) / -0.74 (-0.75) / -0.91 (-0.93) / -0.97 (-1.00) | -1.98 / -1.47 | +0.82 | -1.70 / -0.82 | -1.35 / -0.70 | 0.97 / 0.38 / 0.90 | 0.01 / -0.64 | fail |
| USD.pool | S2a-m2-h15 | 1206 / 1325 | -1.11 (-1.20) | -3.98 (-4.14) / -4.05 (-4.21) / -4.02 (-4.19) / -4.08 (-4.22) | +1.07 (+0.74) | -3.53 (-2.38) / -4.04 (-2.69) / -3.66 (-2.45) / -3.84 (-2.54) | -4.30 / -3.78 | +0.91 | -3.15 / -2.39 | -2.20 / -1.85 | 0.07 / 0.00 / 0.01 | 0.05 / -2.92 | fail |
| USD.pool | S2b-c3-h15 | 281 / 625 | -2.57 (-1.27) | -4.27 (-2.09) / -4.34 (-2.13) / -4.31 (-2.12) / -4.28 (-2.09) | -2.29 (-1.39) | -3.41 (-2.05) / -3.28 (-1.99) / -3.31 (-2.00) / -2.80 (-1.72) | -5.04 / -3.64 | +0.77 | -1.56 / -2.60 | -1.12 / -1.50 | 0.33 / 0.39 / 0.34 | 0.00 / +0.54 | fail |
| AUD.AUDUSD | S1-m1-h5-ps | 171 / 37 | +2.40 (+2.25) | +0.67 (+0.57) / -0.71 (-0.65) / -0.48 (-0.44) / -0.49 (-0.46) | +0.50 (+0.21) | -0.05 (-0.02) / -1.57 (-0.65) / -1.77 (-0.74) / -2.17 (-0.97) | -1.62 / -2.61 | +3.67 | -0.24 / -0.56 | -0.24 / -0.56 | 0.73 / 0.15 / 0.69 | 0.33 / +0.08 | fail |
| AUD.AUDUSD | S2a-m2-h15 | 90 / 13 | -2.25 (-1.15) | -5.83 (-2.87) / -5.84 (-2.88) / -5.86 (-2.89) / -5.79 (-2.85) | +1.14 (+0.37) | -1.02 (-0.33) / -1.16 (-0.37) / -1.02 (-0.33) / -0.92 (-0.30) | -5.97 / -1.08 | +0.17 | -1.55 / -0.25 | -1.55 / -0.25 | 0.31 / - / 0.29 | 0.12 / +0.27 | fail |
| AUD.AUDUSD | S2b-c3-h3 | 21 / 2 | -1.72 (-1.27) | -3.06 (-2.22) / -2.93 (-2.20) / -2.85 (-2.13) / -2.95 (-2.21) | +3.99 (-) | +3.19 (-) / +3.11 (-) / +3.35 (-) / +2.95 (-) | -3.12 / +3.33 | -1.17 | -1.14 / +7.47 | -1.14 / +7.47 | - / - / - | 0.00 / +0.10 | too few |
| NZD.NZDUSD | S1-m1-h1-ns | 15 / 7 | +9.82 (+1.02) | +8.25 (+0.81) / +5.03 (+0.52) / +5.51 (+0.57) / -0.11 (-0.01) | -0.56 (-0.06) | -4.49 (-0.56) / -2.36 (-0.25) / -3.41 (-0.36) / -2.18 (-0.24) | +3.65 / -4.53 | -0.62 | +0.31 / -0.28 | +0.31 / -0.28 | - / - / - | - / - | fail |
| NZD.NZDUSD | S2a-m2-h3 | 8 / 3 | -1.26 (-0.08) | -10.05 (-0.59) / -10.02 (-0.59) / -10.14 (-0.59) / -9.78 (-0.57) | +0.69 (+0.31) | -0.39 (-0.25) / -1.23 (-0.54) / -1.29 (-0.53) / -1.29 (-0.55) | -10.47 / -1.56 | +0.13 | -0.32 / -0.40 | -0.32 / -0.40 | - / - / - | - / - | fail |
| NZD.NZDUSD | S2b-c2-h5 | 5 / 0 | +8.53 (+1.14) | +6.00 (+0.77) / +5.99 (+0.80) / +5.99 (+0.80) / +5.65 (+0.75) | - | - / - / - / - | +5.02 / - | - | +0.43 / - | +0.43 / - | - / - / - | - / - | too few |
| EIA.XTIUSD | S1-m0.25-h5-ns | 204 / 153 | -2.87 (-0.72) | -8.68 (-2.19) / -9.74 (-2.47) / -10.07 (-2.54) / -10.66 (-2.71) | -5.52 (-1.69) | -8.61 (-2.61) / -9.21 (-2.81) / -9.08 (-2.78) / -9.60 (-2.94) | -13.67 / -10.86 | +0.90 | -1.67 / -2.11 | -1.67 / -2.11 | 0.04 / 0.00 / 0.00 | 0.00 / -6.29 | fail |
| EIA.XTIUSD | S2a-m2-h15 | 61 / 32 | -1.27 (-0.17) | -12.28 (-1.62) / -12.42 (-1.63) / -12.33 (-1.63) / -12.54 (-1.64) | +38.73 (+3.74) | +32.25 (+3.13) / +32.55 (+3.14) / +32.56 (+3.16) / +32.96 (+3.15) | -14.21 / +31.68 | -2.64 | -1.07 / +2.40 | -1.07 / +2.40 | 0.38 / 0.72 / 0.48 | 0.00 / +22.85 | fail |
| EIA.XTIUSD | S2b-c3-h15 | 13 / 1 | +27.95 (+1.36) | +19.36 (+0.96) / +18.25 (+0.92) / +18.97 (+0.96) / +19.86 (+1.03) | +126.07 (-) | +124.94 (-) / +124.94 (-) / +122.66 (-) / +114.71 (-) | +14.48 / +120.96 | +6.47 | +0.63 / - | +0.63 / - | 0.51 / - / 0.60 | - / - | too few |
| EIA.XBRUSD | S1-m1-h3-ns | 160 / 102 | +2.19 (+0.76) | -3.23 (-1.08) / -4.72 (-1.64) / -5.17 (-1.79) / -5.80 (-2.02) | -0.53 (-0.21) | -4.13 (-1.75) / -3.90 (-1.62) / -3.87 (-1.58) / -3.62 (-1.47) | -8.84 / -5.54 | +0.75 | -1.17 / -1.20 | -1.17 / -1.20 | 0.70 / 0.45 / 0.68 | 0.61 / -5.26 | fail |
| EIA.XBRUSD | S2a-m2-h15 | 52 / 27 | +1.34 (+0.20) | -6.95 (-1.03) / -7.12 (-1.05) / -7.19 (-1.07) / -7.07 (-1.05) | +24.52 (+2.67) | +19.61 (+2.18) / +19.54 (+2.16) / +19.47 (+2.16) / +19.68 (+2.18) | -8.87 / +18.75 | -2.71 | -0.71 / +1.64 | -0.71 / +1.64 | 0.29 / 0.70 / 0.32 | 0.00 / +10.74 | fail |
| EIA.XBRUSD | S2b-c3-h15 | 9 / 1 | +29.31 (+1.60) | +21.81 (+1.28) / +19.99 (+1.17) / +20.45 (+1.18) / +19.77 (+1.18) | +110.45 (-) | +107.30 (-) / +105.19 (-) / +107.30 (-) / +100.98 (-) | +16.01 / +105.72 | +5.25 | +0.77 / - | +0.77 / - | 0.60 / - / 0.29 | - / - | too few |
| EIA.pool | S1-m1-h3-ns | 325 / 214 | -0.64 (-0.19) | -7.05 (-2.09) / -8.09 (-2.46) / -8.43 (-2.56) / -9.56 (-2.90) | -2.24 (-0.89) | -5.44 (-2.18) / -5.55 (-2.22) / -5.86 (-2.35) / -5.47 (-2.18) | -12.33 / -7.67 | +0.69 | -2.18 / -2.39 | -1.68 / -1.79 | 0.65 / 0.29 / 0.49 | 0.69 / -8.02 | fail |
| EIA.pool | S2a-m2-h15 | 113 / 59 | -0.07 (-0.01) | -9.83 (-1.46) / -9.98 (-1.47) / -9.96 (-1.48) / -10.02 (-1.47) | +32.22 (+3.44) | +26.47 (+2.86) / +26.60 (+2.86) / +26.57 (+2.87) / +26.88 (+2.88) | -11.76 / +25.76 | -2.67 | -1.29 / +2.91 | -0.97 / +2.23 | 0.30 / 0.75 / 0.43 | 0.00 / +16.41 | fail |
| EIA.pool | S2b-c3-h15 | 22 / 2 | +28.50 (+1.50) | +20.36 (+1.12) / +18.96 (+1.05) / +19.57 (+1.08) / +19.83 (+1.13) | +118.26 (-) | +116.12 (-) / +115.06 (-) / +114.98 (-) / +107.85 (-) | +15.11 / +113.34 | +5.87 | +0.96 / +11.36 | +0.70 / - | 0.55 / - / 0.44 | - / - | too few |
| GAS.XNGUSD | S1-m0.25-h15-ns | 208 / 155 | +7.04 (+0.95) | -13.50 (-1.77) / -13.54 (-1.77) / -13.75 (-1.80) / -13.70 (-1.79) | -22.35 (-1.57) | -68.49 (-4.83) / -68.08 (-4.79) / -67.54 (-4.77) / -68.85 (-4.84) | -24.14 / -90.14 | +4.91 | -1.19 / -3.62 | -1.19 / -3.62 | 0.67 / 0.00 / 0.03 | 0.05 / -33.02 | fail |
| GAS.XNGUSD | S2a-m2-h15 | 64 / 71 | -13.11 (-1.15) | -34.81 (-2.94) / -35.12 (-2.97) / -34.70 (-2.93) / -35.49 (-2.99) | +3.93 (+0.18) | -53.47 (-2.52) / -52.85 (-2.49) / -53.01 (-2.50) / -53.38 (-2.50) | -37.73 / -63.21 | +1.53 | -1.93 / -1.90 | -1.93 / -1.90 | 0.35 / 0.47 / 0.42 | 0.00 / +19.13 | fail |
| GAS.XNGUSD | S2b-c3-h3 | 14 / 28 | +5.09 (+0.62) | -7.49 (-0.89) / -7.40 (-0.86) / -7.58 (-0.89) / -8.67 (-1.04) | +18.58 (+1.62) | -26.18 (-2.21) / -28.79 (-2.45) / -26.85 (-2.26) / -27.47 (-2.28) | -13.91 / -49.57 | +3.54 | -0.59 / -1.71 | -0.59 / -1.71 | - / - / - | - / - | fail |
| USDHM.pool | S1-m1-h5-ns | 3549 / 2093 | +0.74 (+2.27) | -0.82 (-2.45) / -1.06 (-3.23) / -1.13 (-3.46) / -1.27 (-3.87) | +0.38 (+0.49) | -0.71 (-0.88) / -0.83 (-1.07) / -0.96 (-1.26) / -1.03 (-1.36) | -1.89 / -1.45 | +0.85 | -2.36 / -1.12 | -1.85 / -0.95 | 0.99 / 0.26 / 0.90 | 0.00 / -0.56 | fail |
| USDHM.pool | S2a-m2-h15 | 1856 / 1742 | -0.67 (-1.01) | -3.10 (-4.52) / -3.16 (-4.61) / -3.14 (-4.59) / -3.19 (-4.63) | +0.57 (+0.50) | -3.36 (-2.88) / -3.78 (-3.19) / -3.48 (-2.96) / -3.61 (-3.04) | -3.40 / -3.61 | +1.11 | -3.34 / -2.89 | -2.42 / -2.24 | 0.04 / 0.00 / 0.00 | 0.01 / -2.31 | fail |
| USDHM.pool | S2b-c3-h15 | 378 / 755 | -2.21 (-1.32) | -3.86 (-2.29) / -4.00 (-2.37) / -3.90 (-2.32) / -3.88 (-2.30) | -2.35 (-1.66) | -3.43 (-2.40) / -3.34 (-2.35) / -3.35 (-2.36) / -2.92 (-2.08) | -4.62 / -3.68 | +0.86 | -1.69 / -3.02 | -1.23 / -1.77 | 0.25 / 0.18 / 0.16 | 0.00 / +0.40 | fail |
| AUDHM.AUDUSD | S1-m1-h5-ps | 198 / 48 | +2.25 (+2.38) | +0.67 (+0.65) / -0.51 (-0.54) / -0.40 (-0.42) / -0.48 (-0.52) | -0.15 (-0.08) | -0.41 (-0.22) / -1.73 (-0.90) / -2.06 (-1.07) / -2.15 (-1.20) | -1.43 / -2.71 | +5.12 | -0.22 / -0.81 | -0.22 / -0.81 | 0.75 / 0.28 / 0.65 | 0.62 / -0.95 | fail |
| AUDHM.AUDUSD | S2a-m2-h15 | 98 / 15 | -2.42 (-1.33) | -5.78 (-3.09) / -5.78 (-3.10) / -5.79 (-3.11) / -5.73 (-3.08) | +1.08 (+0.41) | -0.88 (-0.33) / -0.98 (-0.36) / -0.89 (-0.33) / -0.80 (-0.31) | -5.91 / -0.94 | +0.15 | -1.67 / -0.25 | -1.67 / -0.25 | 0.28 / - / 0.32 | 0.00 / +3.85 | fail |
| AUDHM.AUDUSD | S2b-c3-h3 | 21 / 2 | -1.15 (-0.80) | -2.53 (-1.73) / -2.39 (-1.68) / -2.29 (-1.60) / -2.28 (-1.54) | +3.99 (-) | +3.19 (-) / +3.11 (-) / +3.35 (-) / +2.95 (-) | -2.55 / +3.33 | -1.46 | -0.86 / +7.47 | -0.86 / +7.47 | - / - / - | - / - | too few |

Event minus placebo-day per-trade net, all events of these cells (`out/placebo_diff.txt`):

| set | cell | event minus placebo, bp (t) |
|---|---|---|
| USD.pool | S1-m1-h5-ns | -0.30 (-0.57) |
| USD.US30 | S1-m1-h5-ns | +1.93 (+2.10) |
| USD.USTEC | S1-m1-h5-ns | +0.06 |
| USD.pool | S2a-m2-h15 | -1.41 (-1.22) |
| USD.pool | S2b-c3-h15 | -2.91 (-1.05) |
| EIA.pool | S1-m1-h3-ns | +0.75 (+0.23) |
| GAS | S1-m0.25-h15-ns | -4.08 (-0.51) |

Placebo days fill 0.47-0.91 of the time at the event's k for USD S1, against 0.84-1.00 on events.

## Families: best cell, cells tried, chance

| family | cells (with >= 5 IS trades) | IS gross > 0 | IS net > 0 | IS and VAL net > 0 | best IS net t (cell) | largest \|IS gross t\| | verdicts |
|---|---|---|---|---|---|---|---|
| S1 | 336 (336) | 208 | 14 | 11 | +0.59 (USD.US30 S1-m1-h5-ns) | -4.01 (EIA.XBRUSD S1-m0.25-h15-ps) | 336 fail |
| S2a | 168 (168) | 25 | 0 | 0 | < 0 everywhere (best -0.59, NZD S2a-m2-h3, n 8) | -3.63 (USD.US30 S2a-m1-h3) | 167 fail, 1 too few |
| S2b | 126 (123) | 42 | 20 | 9 | +1.18 (EIA.XBRUSD S2b-c3-h15, n 9 / 1) | -3.08 (USD.pool S2b-c1-h3) | 105 fail, 21 too few |

- The S2b stress rows (entry at T+120 s) are robustness readings, not counted; they change no verdict.
- Chance benchmark: max |t| of 627 normals, p50 3.26 / p95 3.93. The sign-flip permutation (1,000 draws, one flip per
  event day shared by all cells, IS gross t) gives p50 3.04 / p95 3.99. The observed max |IS gross t| is 4.01, of
  the wrong sign, with 4.4 % of null draws above it. No declared-side cell comes near the null median.

### Best cell per family: by year, robustness, C3
Net bp per trade at L = 250, by year (n):
- **S1, USD.US30 S1-m1-h5-ns**: 2016 -0.36 (99), 2017 -2.34 (58), 2018 -1.98 (86), 2019 +2.63 (81), 2020 +2.23
  (73), 2021 +2.79 (62), 2022 +12.44 (91), 2023 -3.43 (112), 2024 -0.28 (111): 4 of 9 years > 0.
  - All trades: mean +1.20, median -0.76, trimmed at the IS 1 / 99 % quantiles +0.58.
  - The top 5 trades make +841 bp of the +924 total.
  - Without March-April 2020: +1.27 (t 1.50).
  - C3 daily correlation +0.009.
- **S2a, NZD.NZDUSD S2a-m2-h3** (least negative): n 11, mean -7.73. C3 corr -0.016.
- **S2b, EIA.XBRUSD S2b-c3-h15**: 2018 +22.1 (2), 2019 +21.9 (4), 2020 +17.4 (3), 2022 +107.3 (1). n 10, median
  +9.0. C3 corr -0.003.

### Per event type (information; `out/report.txt`)
- **S1-m1-h5-ns on the USD pool.** Two IS readings are positive:

  | dominant type | IS net (t) | VAL net (t) |
  |---|---|---|
  | core CPI | +1.70 (0.99) | +4.73 (0.87) |
  | CPI y/y slot | +9.49 (3.45), n 22 | none in VAL |

  The others are negative in IS or in VAL:

  | dominant type | IS net (t) | VAL net (t) |
  |---|---|---|
  | NFP | -1.59 | +2.18 |
  | ISM manufacturing | +0.25 | -4.92 |
  | retail sales | -2.87 (-2.77) | -5.43 (-3.31) |
  | ADP | -2.65 | -2.60 |

  Picking types after looking is post hoc. The CPI cell has about 12 events a year.
- **S2a-m1-h5.** The fade loses most on the largest releases:

  | release | IS net (t) | VAL net (t) |
  |---|---|---|
  | NFP | -7.84 (-3.24) | -15.83 (-2.97) |
  | core CPI | -11.69 (-3.82) | -19.29 (-2.71) |

  Adverse selection grows with the size of the news.
- **S2b on oil (EIA).** It loses in IS and gains in VAL: S2b-c2-h5 IS -7.41 (t -1.14, n 58), VAL +24.49 (t 3.09,
  n 26); S2a-m1-h5 IS -10.19, VAL +0.12. This is a 2022-24 oil overshoot, not a design-era rule.

## PRE (2007-2015, minute level, Dukascopy bid closes, S2b gross only, information)
`out/pre_check.txt`:

| set | cell | PRE gross bp (t), n | IS gross on ticks (t) |
|---|---|---|---|
| USD.AUDUSD | S2b-c1-h15 | +2.14 (3.00), n 543 | +1.16 (1.45), net +0.08 (0.10) |
| USD.NZDUSD | S2b-c1-h15 | +1.85 (2.62), n 646 | +0.27 (0.32), net -1.19 (-1.44) |
| USD.XAUUSD | S2b-c1 | -0.68 / -1.20 / -0.80 at h 3 / 5 / 15 | |
| AUD.AUDUSD | S2b-c1 to c3 | -0.3 to -3.8 | |
| NZD.NZDUSD | S2b-c1 | n 15 only | |

The USD-release reversal over 15 minutes in AUD/NZD was there in 2007-15 at about 2 bp. It is half that or less on
2016-24 ticks and below IC's cost. At the 3-5 minute horizon the fade gains slightly in PRE on AUDUSD / NZDUSD
(+0.1 to +1.3 bp; gold -0.6 to -2.7), but in IS the first minute continues (-1.2 to -2.8 bp on the USD pool).

## Post hoc (Addendum 1, information only): orders armed at T
Levels come from the T-2 quote; the orders are active only from T. The results are in `out/armed_table.txt`.

| set | cell | IS mid (t) | IS net (t) | VAL mid (t) | VAL net (t) |
|---|---|---|---|---|---|
| USD.pool | S1-m1-h3 | +1.35 (3.07) | -0.91 (-2.06) | -0.09 | -1.71 |
| USD.pool | S1-m0.5-h3 | +1.20 (3.55) | -1.20 | -0.55 | -2.25 |
| USD.US30 | S1-m1-h3 | +2.33 (3.64) | +1.22 (1.90) | -0.16 | -0.53 |

- Arming at T lifts the IS gross on the USD pool to +1.2-1.45 bp (t 3.0-3.6). VAL loses it.
- 21 of 431 armed cells are net > 0 in both eras: 17 on NZD (about 23 IS / 12 VAL events, t <= 0.72) and 4 US30
  protective-stop cells with t < 0.7.
- Nothing near DEMO. Not registrable: chosen after looking.

## What this says
- A straddle needs no forecast, and the release move does keep going a little after the trigger: S1 gross is > 0 in
  208 of 336 cells, mostly +0.2 to +1.6 bp on the USD and AUD sets. That is the order-flow continuation of Evans &
  Lyons. But it is smaller than what IC charges in the release minute: half the widened spread at entry and exit,
  plus slippage beyond the stop (median 1-7 bp on NFP / CPI / AUD CPI), plus 0.6 bp commission on FX and metals.
  The cost floor is the release minute itself, as round 25 found for the predictable surprise.
- The T-2 placement that round 25's spread map recommends makes the straddle mostly a pre-release coin toss. Arming
  at T restores the IS gross but not VAL.
- The overshoot side is worse. Limits at the far levels are picked off by real moves: the fill rate rises with the
  size of the news and the loss rises with it.
- The market fade after a large first minute loses at mid in IS, because the first minute continues.
- Every family is uncorrelated with C3 (|corr| < 0.02), but there is nothing to add to it.

## Needs the user
- **VPS tick pull for EURUSD / USDJPY / GBPUSD / USDCAD** (cTrader backtest downloads, 2016-24). It would add:
  - USD releases on the two most liquid USD pairs (91-108 High slots a year each);
  - EUR releases: 16-22 High slots a year (German flash PMI, ZEW, ifo, French flash services);
  - GBP releases: 51 a year IS, 18 a year VAL (CPI, retail, earnings, PMIs, manufacturing);
  - CAD releases: 37-39 a year (jobs, CPI, retail, GDP, manufacturing sales);
  - nothing for JPY or CHF (no B0 type).

  Expected value is low. The S1 gross on five USD instruments is <= 1 bp against a 1-3 bp release round trip, and
  the 0.6 bp commission stays on EURUSD / USDJPY. I would put LIVE at ~1 % and DEMO at ~5 %, the highest for CAD jobs
  / CPI (round 25 B0: 9-18 bp release moves).
- **Index IS costs at today's levels** (an open decision, a change of bar). At VAL-era costs (~0.3 bp), US30
  S1-m1-h5-ns would net about +1.2 bp in IS (t ~1.6). That is still below DEMO's 2.0, with 4 of 9 years > 0 and 5
  trades carrying it. It does not create a candidate.
- **Dukascopy ticks 2004-15** (a tick-level PRE). Low value after the IS / VAL failure.

## Untested ideas
- A declared "armed at T" straddle, or orders sent at T-5 s at the T-2 levels, on data the post-hoc check has not
  seen. Candidates are the VPS pairs above or data after 2026-09-24. Low prior: the VAL gross was 0.
- A causal rolling norm (trailing 24 events of the type) instead of the fixed IS median. VAL moves were larger, so
  the fixed k (m = 1) filled 97-100 % of VAL events against 84-87 % in IS.
- Exits other than the clock: a take-profit at 1-2 norms, or a trailing stop. Only one protective stop (1 norm) was
  declared.
- CNY releases on AUDUSD (16 High slots a year IS, 11 VAL; out by declaration).
- The VAL-only oil overshoot reversal on EIA days (S2b c2 h5 +24.5 bp net, t 3.1, n 26), which needs a new era to
  test.
- Medium releases alone. They were tested only pooled with High (USDHM / AUDHM: no difference in sign).

## Scripts and outputs
Scripts are in
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r26/S/code/`
and outputs in `.../r26/S/out/`. Run them from the repo root with
`PYTHONPATH=.:<code dir> research/.venv/bin/python <script>`.

| script | what it does |
|---|---|
| common.py | calendar, sets, HOLD-guarded tick access, statistics |
| cal_explore.py, cal_explore2.py, tick_format.py, xng_cov.py | pre-declaration data checks, no returns |
| build_events.py | slots, placebo days, random candidate minutes -> `out/events.json` |
| norms.py | IS release-minute norms -> `out/norms.json` / `norms.txt` |
| sim.py | tick fill simulator: S1 / S2a / S2b, four latencies, OCO cancel latency, protective stop |
| test_sim.py | synthetic-tick tests |
| verify_real.py, verify_ps.py | brute-force loop re-implementations on real events: 2,376 + 2,520 cell checks, 0 mismatches |
| run_sym.py | per-instrument run of events, placebo days and random times -> `out/res_<SYM>.npz`, `map_<SYM>.json` |
| analyze.py | per-cell statistics, controls, chance, verdicts -> `out/cells_table.txt`, `cells.json`, `chance.txt` |
| fillcheck.py | fill-model checks -> `out/fillcheck.txt` |
| report.py, placebo_diff.py, summary.py | tables for this file -> `out/report.txt`, `placebo_diff.txt` |
| pre_check.py | PRE minute-level S2b -> `out/pre_check.txt` |
| posthoc_armed.py | Addendum 1 -> `out/armed_table.txt` |
| vps_pull_value.py | slot counts for the VPS-pull note -> `out/vps_pull_value.txt` |
