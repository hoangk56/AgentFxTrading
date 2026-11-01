# Round 63, stream M: the known "real at mid" intraday effects at an exchange / ECN venue cost

Written 2026-10-31 from 15:20 UTC (`date -u` 15:20:40 when the results were in). The cost model, the list of rows
and the bars were declared in [HYPOTHESES_M.md](HYPOTHESES_M.md) from 15:10 UTC; Amendment 0 (signal latency, N1
control, both written 15:13 UTC) came before any number. HOLD was never loaded: every series is cut at ts < 2025-01-01
when it is loaded, and the Dukascopy `*_2026.npz` files were not opened.

## Answer
- **No LIVE row and no LIVE book at any realistic venue cost.** The highest power at VAL size among the 33 graded
  rows is 1.96 (F4, the ECB pre-fix slot, and it sits inside E1's window, whose HOLD has been opened). The best clean
  rows reach 1.1-1.3 (F15, F23, F24, M2).
- **DEMO bar met at the venue's upper-bound cost:**
  - **F15**, EURJPY short 05:00-07:00 London on the last weekday of March, June and September. IS net +7.76 bp
    (t 2.87, n 18), VAL +8.66 (t 1.54, n 9), 9/9 years, random 100/98 %, x1.5 and +1 min > 0. Power at VAL size
    is 1.17.
    - It also passed at IC's cost (round 24: DEMO), so the venue is not what makes it pass.
    - Draft: [PREREG_DRAFT_M_eurjpy_quarter_end.md](PREREG_DRAFT_M_eurjpy_quarter_end.md). HOLD holds about 5
      events, so the look can only reject it.
  - **F8**, USDCHF long 10:00-12:00 UTC after a top-tercile morning rise, **meets the DEMO numbers only at the
    venue**: IS t 2.02 (IC 1.72), VAL +0.95 (t 1.10), random 100/98 %.
    - It has no recorded economic mechanism (round 24: "mech: no", a clock cell found by a scan of 2004-15), so it
      fails the common bar. No draft.
    - It is also decaying: mid 1.97 -> 1.64, with 2023 and 2024 negative. Power at VAL size is 0.84.
  - F2 and F4 (EURUSD, the ECB-fix window) meet the DEMO numbers, but both are contaminated: E1's HOLD (2026-10-06)
    has already measured those minutes. Excluded from drafting and from the book, as declared.
- **The venue barely moves the frontier.**
  - At the ECN (0.2 bp a side), FX rows save 0.12-0.2 bp per round trip, against effects of 1-2 bp with a 2-4 h
    sd of 13-24 bp.
  - CME FX futures are dearer than IC: a 6E tick is about 0.45 bp, plus ~0.35 bp of commission.
  - COMEX GC saves ~0.25 bp in VAL, but its tick was 0.6-0.8 bp in 2016-21, when gold traded at $1,100-1,800.
  - YM and ES cost more than IC's VAL-era CFD spread: the commission alone is 0.23-0.28 bp, plus a tick.
- **The one row the venue question could flip is N1**, the 17:00 NY reopen-gap fade (VAL mid t 20 at a floor touch).
  It fails at every measured cost.
  - CME is halted 17:00-18:00 ET, so N1 has no futures route.
  - Dukascopy's ECN quotes at the same minutes in 2010-15 cost 2.4 bp a round trip (EURUSD 1.25, USDCHF 3.6). That
    is about half of IC's cost, and still more than the 1.1 / 2.1 bp IS / VAL mid.
    - Net at that measured cost: IS -1.39 bp (t -12.2), VAL -0.30 (t -3.7).
  - Its break-even round trip of 0.7-1.3 bp (IS) is below what any venue quotes at the rollover.
- **The declared book** is F8 + F15 (the rows meeting the DEMO numbers, not contaminated).
  - IS +0.116 R per active day (t 2.48), VAL +0.096 (t 1.48).
  - x1.5 IS / VAL t 1.87 / 1.06; +1 min t 1.96 / 1.41.
  - IS correlation 0.06. **Power at VAL size 1.12**: not LIVE.
  - It meets the DEMO numbers only through F15's 3 events a year, and F8 brings no mechanism. Not drafted.

## 1. Venue cost model (as declared; realised per trade at that trade's own price)
| instrument | venue | spread lower / upper bound | commission rt | realised rt cost VAL, upper (lower) | IC VAL |
|---|---|---|---|---|---|
| EURUSD, USDJPY | ECN (IBKR IdealPro type) | 0.1 pip / IC's quoted spread | 0.40 bp | 0.50-0.53 (0.47-0.49) | 0.62-0.70 |
| USDCHF, GBPUSD | ECN | 0.1 pip / IC | 0.40 | 0.61-1.12 (0.48-0.51) | 0.78-1.30 |
| EURJPY, GBPJPY | ECN | 0.3 pip / IC | 0.40 | 0.73-0.90 (0.57-0.60) | 0.89-1.09 |
| USDCNH | ECN | 1 pip / IC's published 2.93 pips | 0.40 | 0.82 (0.54) | 1.02 |
| six USD pairs at 17:00-18:00 NY (N1) | ECN (no futures: Globex halt) | 0.1 pip / IC; **measured: Dukascopy SWFX 2010-15** | 0.40 | 4.2-5.4 (0.49); Dukascopy 2.4 | 4.3-5.6 |
| XAU | COMEX GC, $2.50 a side | 1 tick ($0.10) / max(tick, IC) | 0.25-0.35 | 0.77-0.95 (0.75) | 1.00-1.19 |
| USTEC | CME NQ | 1 tick / max(tick, IC) | 0.17-0.28 | 0.82 (0.34) | 0.65 |
| US30 | CBOT YM | same | 0.28-0.38 | 0.60 (0.57) | 0.31 |
| US500 | CME ES | same | 0.23-0.33 | 0.81-1.08 (0.78) | 0.49-0.82 |
| UK100 | ICE Z | same | 0.53-0.57 | 2.68 (1.30) | 2.03 |
| AUS200 | ASX SPI 200 | same | 0.44-0.52 | 2.06 (1.65) | 1.57 |
| HK50 | HKEX HSI | same | 0.62-0.84 | 2.92 (0.64) | 2.81 |
| DE40 | Eurex FDAX (1-point tick) | same | 0.13-0.16 | 0.83 (0.77) | 0.52 |
| XTI | NYMEX CL | same | 0.63-0.91 | 3.92 (1.84) | 3.30 |
| BTC | CME BTC, $11 a side | same | 1.3-2.2 | 4.42 (2.65) | 3.17 |

- The upper bound uses IC's spread at the minute (verdict). For index, oil and BTC rows that bound is often worse
  than IC's own cost, because IC charges no commission. The lower bound (one tick) is the optimistic case. A row that
  passes only at the lower bound is a venue-data decision, not a candidate.
- Measured ECN spread at the rollover (Dukascopy SWFX, median 2010-15, bp):
  - 17:01 NY: EURUSD 0.99, GBPUSD 2.01, USDJPY 2.14, USDCHF 4.16, USDCAD 3.14, AUDUSD 2.95;
  - 18:00 NY: 0.70, 1.32, 1.11, 2.32, 1.78, 1.67;
  - 12:00 NY, for reference: 0.42-1.40.
  - IC's spread at 17:01 is 2.6-7.8 bp. An ECN's spread at the rollover is about half of IC's, not the normal-hours
    level ([out/n1_duka_spreads.json](out/n1_duka_spreads.json), [out/n1_ic_spreads.json](out/n1_ic_spreads.json)).

## 2. Results (IC M1 mid, IS 2016-21, VAL 2022-24; net in bp per trade at the venue upper bound; t clustered by day)
"(c)" = contaminated (an opened HOLD covers the same symbol and minutes). Power = VAL net t x sqrt(1.73 / 3), the
expected HOLD t if HOLD keeps the VAL size. The value in brackets assumes HOLD keeps 0.65 of the VAL mid (E1's
retention). "LIVE cost" = the round trip at which the VAL size would give IS t 2.5, VAL t 1.5 and power 3. The
tier at "lo" checks the numbers only. The full table, with IS / VAL lower-bound nets, IC nets and per-year values, is
in [out/summary.md](out/summary.md).

| row | venue | rt cost VAL: venue up (lo) / IC | IS mid | IS net up (t) | VAL mid | VAL net up (t) | x1.5 / +1m (IS, VAL) | random IS/VAL % | yrs+ | power VAL size (at 0.65) | LIVE cost | tier at up / at lo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 (c) | ECN | 0.50 (0.49) / 0.63 | +2.46 | +1.95 (+3.85) | +2.48 | +1.98 (+2.50) | ++, ++ | 100/96 | 9/9 | +1.90 (+1.06) | -0.65 | DEMO / DEMO-numbers |
| F4 (c) | ECN | 0.50 (0.49) / 0.62 | +1.11 | +0.58 (+3.15) | +1.14 | +0.64 (+2.58) | ++, ++ | 100/100 | 8/9 | +1.96 (+0.74) | +0.16 | DEMO / DEMO-numbers |
| F7 | ECN | 0.71 (0.51) / 0.89 | +1.02 | +0.26 (+0.78) | +1.08 | +0.37 (+0.76) | -+, ++ | 98/90 | 6/9 | +0.57 (-0.01) | -0.87 | none / none |
| F8 | ECN | 0.69 (0.51) / 0.87 | +1.97 | +1.23 (+2.02) | +1.64 | +0.95 (+1.10) | ++, ++ | 100/98 | 6/9 | +0.84 (+0.33) | -1.77 | DEMO numbers (no mechanism) / DEMO-numbers |
| F9 | ECN | 1.12 (0.51) / 1.30 | +0.69 | -0.43 (-2.18) | +0.58 | -0.54 (-1.47) | --, -- | 93/65 | 1/9 | -1.12 (-1.53) | -0.87 | none / none |
| F10 | ECN | 0.52 (0.47) / 0.69 | +0.88 | +0.31 (+0.96) | +0.95 | +0.42 (+0.74) | ++, ++ | 98/74 | 6/9 | +0.56 (+0.12) | -1.32 | none / none |
| F11 | ECN | 0.73 (0.60) / 0.89 | +0.92 | +0.20 (+0.50) | +1.01 | +0.28 (+0.43) | -+, -- | 96/94 | 6/9 | +0.33 (-0.08) | -1.57 | none / none |
| F12 | ECN | 0.90 (0.57) / 1.09 | +1.65 | +0.60 (+1.21) | +1.43 | +0.53 (+0.72) | ++, ++ | 70/50 | 5/9 | +0.55 (+0.03) | -1.48 | none / DEMO-numbers |
| F13 | ECN | 0.90 (0.57) / 1.09 | +2.12 | +1.13 (+1.67) | +1.72 | +0.82 (+0.89) | ++, ++ | 76/48 | 7/9 | +0.67 (+0.18) | -1.93 | none / DEMO-numbers |
| F14 | ECN | 0.73 (0.60) / 0.89 | +1.76 | +1.03 (+2.12) | +1.06 | +0.33 (+0.43) | ++, -+ | 100/58 | 6/9 | +0.33 (-0.04) | -1.98 | none / DEMO-numbers |
| **F15** | ECN | 0.89 (0.60) / 1.08 | +8.65 | +7.76 (+2.87) | +9.55 | +8.66 (+1.54) | ++, ++ | 100/98 | 9/9 | +1.17 (+0.72) | -12.61 | **DEMO** / DEMO-numbers |
| F16 | ECN | 0.61 (0.48) / 0.78 | +9.71 | +9.02 (+2.48) | +1.87 | +1.26 (+0.30) | ++, ++ | 100/71 | 7/9 | +0.23 (+0.11) | -14.74 | none / DEMO-numbers |
| F23 | ECN | 0.82 (0.54) / 1.02 | +1.24 | +0.40 (+0.88) | +2.07 | +1.25 (+1.53) | -+, ++ | 98/96 | 7/9 | +1.17 (+0.49) | -1.15 | none / none |
| F24 | ECN | 0.53 (0.47) / 0.70 | +0.24 | -0.33 (-2.54) | +0.93 | +0.40 (+1.72) | --, ++ | 96/100 | 3/9 | +1.31 (+0.25) | -0.09 | none / none |
| M2 | GC | 0.80 (0.75) / 1.04 | +1.82 | +0.37 (+1.21) | +1.44 | +0.63 (+1.48) | -+, ++ | 100/100 | 6/9 | +1.12 (+0.23) | -0.26 | none / DEMO-numbers |
| M4 | GC | 0.79 (0.75) / 1.03 | +1.23 | -0.11 (-0.34) | +0.86 | +0.07 (+0.14) | --, -+ | 100/100 | 3/9 | +0.11 (-0.37) | -1.02 | none / none |
| M7 (c) | GC | 0.77 (0.75) / 1.00 | +0.45 | -0.83 (-5.10) | +0.37 | -0.41 (-2.09) | --, -- | 100/95 | 1/9 | -1.58 (-2.08) | -0.40 | none / none |
| M11 | GC | 0.95 (0.75) / 1.19 | +0.81 | -0.76 (-2.44) | +0.80 | -0.15 (-0.36) | --, -- | 98/96 | 4/9 | -0.28 (-0.78) | -0.87 | none / none |
| M12 | GC | 0.80 (0.75) / 1.06 | +6.33 | +4.64 (+1.59) | +1.86 | +1.06 (+0.18) | ++, +- | 80/40 | 6/9 | +0.13 (+0.05) | -21.98 | none / none |
| I1 (c) | NQ | 0.82 (0.34) / 0.65 | +1.55 | -0.48 (-0.84) | +0.92 | +0.10 (+0.16) | --, -- | 100/96 | 4/9 | +0.12 (-0.26) | -1.68 | none / none |
| I3 | YM | 0.60 (0.57) / 0.31 | +0.39 | -0.94 (-3.89) | +0.93 | +0.33 (+1.31) | --, ++ | 84/99 | 2/9 | +0.99 (+0.02) | -0.21 | none / none |
| I4 | ES | 0.81 (0.78) / 0.49 | +1.07 | -0.88 (-2.06) | +1.76 | +0.95 (+1.28) | --, ++ | 100/100 | 2/9 | +0.97 (+0.34) | -1.16 | none / none |
| I5 | Z | 2.68 (1.30) / 2.03 | +0.99 | -2.80 (-11.02) | +1.03 | -1.65 (-5.55) | --, -- | 83/100 | 0/9 | -4.22 (-5.14) | -0.14 | none / none |
| I6 | SPI | 2.06 (1.65) / 1.57 | +0.86 | -1.76 (-4.64) | +0.73 | -1.33 (-5.03) | --, -- | 100/87 | 0/9 | -3.82 (-4.55) | -0.32 | none / none |
| I8 | HSI | 2.92 (0.64) / 2.81 | +2.21 | -1.15 (-3.38) | +0.14 | -2.78 (-3.54) | --, -- | 100/56 | 1/9 | -2.69 (-2.74) | -2.96 | none / none |
| I10 | FDAX | 0.83 (0.77) / 0.52 | +1.10 | -0.32 (-0.83) | +1.03 | +0.20 (+0.50) | --, -+ | 100/100 | 3/9 | +0.38 (-0.30) | -0.55 | none / none |
| I13 | ES | 1.08 (0.78) / 0.82 | +4.73 | +2.29 (+1.41) | -0.57 | -1.66 (-0.69) | ++, -- | 39/40 | 6/9 | -0.53 (-0.46) | -10.02 | none / none |
| E1x | CL | 3.94 (1.84) / 3.33 | +5.92 | -2.45 (-0.88) | +2.08 | -1.86 (-1.38) | --, -- | 99/98 | 1/7 | -1.05 (-1.46) | -3.23 | none / none |
| E2x | CL | 3.92 (1.84) / 3.30 | +1.42 | -7.10 (-10.72) | +0.55 | -3.37 (-9.65) | --, -- | 96/98 | 0/7 | -7.33 (-7.74) | -0.83 | none / none |
| C1 | CME BTC | 4.42 (2.65) / 3.17 | +7.22 | -12.22 (-5.76) | +2.22 | -2.20 (-1.67) | --, -- | 98/83 | 1/8 | -1.27 (-1.72) | -2.98 | none / none |
| N1a | ECN | 5.06 (0.49) / 5.25 | +1.07 | -1.99 (-17.01) | +2.14 | -2.92 (-30.36) | --, -- | 0/0 | 0/9 | -23.06 (-28.98) | +0.77 | none / LIVE numbers (floor touch only) |
| N1b | ECN | 4.15 (0.49) / 4.34 | +0.71 | -2.04 (-17.91) | +1.31 | -2.84 (-32.61) | --, -- | 0/0 | 0/9 | -24.76 (-28.76) | +0.42 | none / none |
| N1c | ECN | 5.41 (0.49) / 5.61 | +1.29 | -2.10 (-10.88) | +2.65 | -2.76 (-26.44) | --, -- | 0/0 | 0/9 | -20.08 (-26.81) | +0.81 | none / LIVE numbers (floor touch only) |

- Chance: K = 33. The best IS t at the upper bound is 3.85 (F2, contaminated), against a max |t| of 33 normals with
  median 2.32 and p95 3.18. F15's IS t of 2.87 is below that p95. Its side and window were fixed on 2004-15 (round 14
  Q, PRE mid +10.7, t 3.7), so IS is out of sample for it.
- **N1 at the measured ECN cost** (Dukascopy median spread at the fill's NY minute + 0.4 bp,
  [out/n1_duka_cost.txt](out/n1_duka_cost.txt)):

  | rule | IS net (t) | VAL net (t) |
  |---|---|---|
  | N1a | -1.39 (-12.2) | -0.30 (-3.7) |
  | N1b | -1.71 (-15.4) | -1.10 (-14.4) |
  | N1c | -1.21 (-6.5) | +0.17 (+1.8) |

  The IS era fails in every pair; EURUSD is the best one, at -0.53 / +0.48.
- Signal-latency reading (information only, [out_r24read/summary.md](out_r24read/summary.md)): with round 24's
  zero-latency signals the affected rows (F8, M4, M7, M11, I3, I4, I5, I8, E1x, E2x, C1) keep the same tier.
  - Some mids are larger: I5 +1.65 vs +0.99, I3 VAL +1.05 vs +0.93.
  - F8: IS t 2.08, VAL +1.03.

## 3. The declared book ([out/book_F8_F15.json](out/book_F8_F15.json))
| era | active days | mean R per active day (t) | x1.5 (t) | +1 min (t) | daily Sharpe | power (this era's size) | R per year | by year |
|---|---|---|---|---|---|---|---|---|
| IS | 484 | +0.116 (2.48) | +0.087 (1.87) | +0.093 (1.96) | 0.113 | 1.33 | +9.4 | 2016 +21.4, 2017 +6.2, 2018 +21.0, 2019 -2.8, 2020 +3.8, 2021 +6.5 |
| VAL | 271 | +0.096 (1.48) | +0.069 (1.06) | +0.092 (1.41) | 0.090 | **1.12** | +8.7 | 2022 +28.3, 2023 -5.4, 2024 +3.2 |

- IS correlation F8-F15 is 0.06. The book was not given a random control of its own; each member beats 98-100 % of
  its own. 2022 holds 2/3 of VAL.
- Fallback book, information only (rows with IS t >= 2.0 and VAL net > 0: F8, F14, F15, F16):
  - IS t 3.47, VAL t 1.12, power at VAL size 0.85;
  - VAL x1.5 t 0.50; 2024 -8.2 R; IS correlations -0.03..+0.07.
  - Decay is the binding fact: IS +26.5 R a year, VAL +13.6.

## 4. Decay and HOLD power, honestly
- **IS > VAL** in mid for F8 (1.97 -> 1.64), F12, F13, F14 (1.76 -> 1.06), F16 (9.71 -> 1.87), M2, M12 (6.33 -> 1.86),
  I1, I8 (2.21 -> 0.14), E1x (5.92 -> 2.08), C1 (7.22 -> 2.22) and I13 (4.73 -> -0.57).
- **VAL >= IS** for F2, F4, F7, F10, F11, F15, F23, F24, I3, I4 and N1. In the index rows (I3, I4) the IS net is
  negative at any cost: their IS mid (0.39 / 1.07) is below even a futures tick plus commission.
- **HOLD power at VAL size** for every clean row is <= 1.31. At E1's measured retention of 0.65 it is <= 0.72.
  - Only F4 (contaminated) has a positive LIVE cost: +0.16 bp. That is an institutional prime-broker FX venue with
    ~zero spread at 12:45-13:00 London, and it would also need no decay; at E1's retention F4's power is 0.74.
  - N1 has a positive LIVE cost on mid (+0.4-0.8 bp), but the measured rollover cost is 2.4 bp or more.
- As before, the binding constraint is the per-trade Sharpe, not the venue.
  - FX clock effects have a per-trade Sharpe of 0.02-0.1 even at zero cost: sd 13-24 bp against 1-2 bp.
  - The large rare effects (F15, F16, M12) are capped by count.

## 5. What failed and why
- The ECN saves too little. FX rows go from IC's 0.62-1.30 to 0.50-1.12 bp: F7, F10, F11, F12, F13 and F14 stay
  below IS t 2.5 / VAL t 1.5.
- Gold at GC is still about 0.8 bp in VAL and 1.0-1.6 bp in IS. M4, M7 and M11 sit at mid 0.4-1.2 bp; M2 has IS
  t 1.21 at the upper bound and 2.60 only at a one-tick touch.
- Index and oil futures do not beat IC in VAL. YM, ES and FDAX are dearer than IC's CFD in 2022-24 because of the
  commission. UK100, AUS200, HK50 and CL are slightly cheaper than IC but still 2-4 bp, against mids of 0.7-2 bp.
- BTC on CME costs 2.7-4.4 bp against C1's +2.2 bp VAL mid.
- I13 (the night premium, a new reading) is IS +2.29 (t 1.41) and VAL -1.66, and fails random (39 / 40 %).
- N1 lives inside the rollover hour, whose spread widening is market-wide (measured on an ECN as well).

## 6. Pitfalls met
- **Futures are not automatically cheaper.** The commission is fixed per contract and the tick is fixed in price,
  so small-notional contracts (YM $5 a point) and the cheaper prices of 2016-21 (gold at $1,200: a GC tick of 0.8 bp)
  cost more than IC's CFD spreads. CME FX futures (6E: 0.45 bp a tick) cost more than IC's EURUSD.
- **The upper bound for indices in IS** uses IC's wide 2016-21 CFD spreads (US30 0.93 bp, US500 1.59). It is
  pessimistic for a futures venue. At the lower bound (one tick) the index rows still fail the IS gate (I3 IS t -1.76,
  I4 -0.43, I10 +0.24).
- **Contamination.** F2, F4, M7 and I1 share minutes with opened HOLDs (E1; rule L; E-USTEC). The most valuable venue
  row (F4) is one of them.
- **Signal latency.** Round 24's readings put the entry at the signal's own last price. Here every signal ends one
  minute before entry (Amendment 0). The verdicts do not change.
- **Mechanism.** F8 meets the DEMO numbers only at the venue, but it is a clock cell with no named flow.

## 7. What a user decision could unlock
- **Nothing at LIVE in this family.** No venue cost makes a clean, declared, HOLD-closed effect reach power 3 at its
  VAL size.
- An institutional FX venue at about 0.1-0.2 bp all-in (prime broker), plus a fresh HOLD (data after 2026-09-24),
  would make the ECB pre-fix slot (F4) LIVE-like at its VAL size. E1's HOLD reading, however, implies about 0.7.
- A venue with its own 2016-24 quotes at 17:00-18:00 NY (an ECN's tick history) would settle N1 directly. Dukascopy's
  2010-15 spreads say it fails.
- F15 is the only HOLD-closed DEMO row. Its HOLD has about 5 events, so a HOLD look can only reject it (draft
  written; the coordinator decides).
- Correlation of F15 with C3: all 27 F15 days are also C3 exit days (the month-end is a gotobi day). C3 exits by
  ~01:00 UTC and F15 trades 04:00-06:00 UTC. Same-day correlation on those days is -0.01.

## Files
- [HYPOTHESES_M.md](HYPOTHESES_M.md): cost model, the list, bars, book, power arithmetic, Amendment 0.
- Code ([code/](code/)):
  - `precalc.py`: the pre-registration arithmetic from published numbers, output `precalc_out.md`;
  - `eng.py`: panel, quotes, venue costs, statistics;
  - `rules.py`: the 30 single-symbol rules;
  - `run.py`: grading and random control;
  - `n1.py`: N1, plus the Dukascopy and IC spread tables;
  - `n1_duka_cost.py`;
  - `book.py`;
  - `summarize.py`.
  - Run: `PYTHONPATH=.:research/results/portfolio/round63_parallel/M/code research/.venv/bin/python
    research/results/portfolio/round63_parallel/M/code/run.py` from the repo root (`M_R24READ=1` for the latency
    information run).
- Outputs ([out/](out/)):
  - `<id>.json` and `<id>_trades.npz` per row;
  - `summary.md`;
  - `run_all.log` and `n1.log`;
  - `n1_duka_spreads.json`, `n1_ic_spreads.json` and `n1_duka_cost.txt`;
  - `book_*.json` / `.txt`.
  - [out_r24read/](out_r24read/): the latency information run.
- Draft: [PREREG_DRAFT_M_eurjpy_quarter_end.md](PREREG_DRAFT_M_eurjpy_quarter_end.md).
- No data was pulled. Inputs were IC M1 (`research/data/m1`), IC USDCNH bars, Dukascopy M1 2010-15 and `DFF.csv`.
