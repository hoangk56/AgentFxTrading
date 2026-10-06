# Stream M: stability-first calendar / clock scan, PRE 2004-15 discovery -> IS 2016-21 -> VAL 2022-24

Hypotheses and their UTC times: [HYPOTHESES_M.md](HYPOTHESES_M.md). Draft: [PREREG_DRAFT_M_eurusd_midday.md](PREREG_DRAFT_M_eurusd_midday.md).
HOLD was never loaded: the panel ends 2024-12-31, Dukascopy 2015-12-31, and dates stop at 2024-12-23.

## Answer
- **One DEMO-tier rule, no LIVE rule.** E1: short EURUSD 11:00-13:00 London, every weekday. Mid +1.69 / +1.80 / +1.97 bp
  (t 5.2 / 5.1 / 3.6) in PRE / IS / VAL, net +1.02 / +1.17 / +1.35 (t 3.2 / 3.3 / 2.5), VAL/IS 1.10. It beats 100 % / 99 %
  of random entries, stays > 0 at spread x1.5 and +1 minute, and has 8 of 9 IS+VAL years net > 0. It fails LIVE on
  power only: 1.78 on the IS size and 1.88 on the VAL size, against a bar of 3.
- E1 is weaker than its headline. Its plateau is narrow, and its PRE mean comes from a 15-minute slot that stopped in
  2016 (caveats below). The family is stopped, as the brief says.
- **Clock effects persist and calendar effects do not.** Of the 139 cells confirmed in IS, 127 are "every weekday"
  cells. Month-end, quarter-end, business-day-of-month and holiday cells hardly survive the PRE -> IS step.
- **Selecting on PRE does not avoid shrinkage.** The 500 cells carried from PRE keep 18 % of their PRE size in IS and
  72 % of their IS size in VAL.

## Design (as declared)
- Cells: 11 symbols x 4 DST-aware clocks (Tokyo, London, New York, Sydney) x 28 day types x windows. Day types:
  every weekday, Mon..Fri, the k-th weekday from month start or end (k = 1..5), quarter-end k = 1..3, and US/UK/JP
  holiday, day before and day after. M1 symbols (USDJPY EURJPY GBPJPY USDCHF EURUSD) use 15-minute starts and
  lengths of 15, 30, 60, 120 and 240 min. H1 symbols (AUDJPY AUDUSD GBPUSD NZDUSD USDCAD XAUUSD) use hourly starts
  and lengths of 1-4 h.
- Exclusions:
  - on JPY pairs, every window that overlaps 23:00-02:00 UTC;
  - every window that touches 16:45-18:15 New York;
  - 24 Dec - 1 Jan;
  - quotes more than 10 minutes stale.
- K = 270,086 cells with at least 30 PRE events (218,237 in the M1 group, 51,849 in the H1 group).
- Prices: PRE uses the Dukascopy bid; IS and VAL use the panel mid.
- Costs:
  - IS and VAL: half the actual spread at entry and at exit, plus 0.6 bp;
  - PRE: IC's 2016-17 mean spread by New York minute of day, plus 0.6 bp. Round 7 used UTC minutes; New York minutes
    keep the rollover hour in place across DST.
- Side: the sign of the PRE mean, fixed before any IS number. IS and VAL are judged on that side only.

## Discovery (PRE) and confirmation (IS, VAL), with chance benchmarks
| step | result | chance benchmark |
|---|---|---|
| PRE, all cells | max \|t_PRE\| 10.98 (EURUSD short 11:45-12:00 London) | sign-flip permutation (one sign per date, shared by all cells), 200 draws: max \|t\| median 4.71, 95 % **5.46**; M1 group 5.36, H1 group 4.98 |
| set A = \|t_PRE\| >= 5.46 | 120 cells (110 M1, 41 H1 by group threshold) | |
| IS confirmation, set A (t_IS >= 2 on the PRE side) | **47 / 120** | IS sign-flip null: median 2, 95 % 9 (p < 0.005) |
| set B = top 500 by \|t_PRE\| (\|t\| >= 4.29) | **139 / 500** confirmed; best side t_IS 5.08 | null count median 10, 95 % 29; null max t_IS 95 % 3.66 |
| VAL, the 139 confirmed | 116 same sign, 47 with t_VAL >= 1.5 | about 9 expected by chance |
| size, set B (mean bp on the PRE side) | PRE 2.01 -> IS 0.35 -> VAL 0.25 (IS/PRE 0.18, VAL/IS 0.72) | |
| net > 0 in IS and VAL | set A 3 %, set B 7 % | |
| "stable" (IS/PRE and VAL/IS >= 0.5) among the confirmed | 40 cells, 12 of them net > 0 in IS and VAL: all are the EURUSD European-midday family, GBPJPY in the US afternoon, or one USDCHF cell | |

Day types of the 139 confirmed cells: ALL 127, FRI 5, MON 2, TUE 2, THU 1, BD-1 1 (Tokyo-fix adjacent), PRE_GBP 1.

## Families of the IS-confirmed cells (best IS cell of each; mid bp on the PRE side, (t))
| family (symbol, side, day, UTC span at standard time) | cells | best cell | PRE / IS / VAL | net IS / VAL | IS/PRE, VAL/IS | note |
|---|---|---|---|---|---|---|
| EURUSD short, every day, 08:15-13:30 | 22 | London 11:00+120 (**E1**) | +1.69 (5.2) / +1.80 (5.1) / +1.97 (3.6) | +1.17 / +1.35 | 1.07, 1.10 | DEMO draft |
| EURUSD long, every day, 01:00-06:00 | 42 | Tokyo 10:15+120 | +1.64 (7.1) / +1.18 (4.6) / +0.52 (1.6) | +0.47 / -0.13 | 0.72, 0.44 | Tokyo-fix adjacent (C3's mechanism), decaying |
| USDCHF long, every day, 10:00-13:15 | 8 | London 12:45+15 | +0.64 (4.4) / +0.68 (4.4) / +0.26 (1.2) | -0.26 / -0.62 | 1.07, 0.38 | below cost, decaying |
| USDCHF long, every day, 00:00-01:45 | 17 | Tokyo 08:00+120 | +1.47 (5.0) / +1.05 (4.2) / +0.09 (0.2) | -0.20 / -1.02 | 0.71, 0.09 | Tokyo fix, gone in VAL |
| USDCHF short, every day, 13:00-13:30 | 1 | New York 08:00+30 | +1.05 (4.5) / +0.69 (3.5) / +0.58 (1.6) | -0.62 / -0.72 | 0.66, 0.84 | ECB-fix rebound, below cost |
| GBPJPY long, every day, 17:30-21:45 | 4 | London 17:30+240 (G1) | +2.21 (4.3) / +1.65 (3.3) / +1.43 (1.9) | +0.41 / +0.34 | 0.74, 0.87 | stable, about 1.2 bp of cost; fails control |
| USDJPY short, every day, 02:00-03:00 | 2 | Tokyo 11:00+30 | +0.69 (4.7) / +0.67 (3.2) / -0.01 (0.0) | -0.10 / -0.74 | 0.97, -0.02 | gone in VAL |
| NZDUSD long, every day, 05:00-07:00 | 2 | London 05:00+120 | +1.58 (4.6) / +1.20 (3.1) / -0.39 (-0.8) | -0.03 / -1.57 | 0.76, -0.33 | gone in VAL |
| EURUSD short, Fridays, 09:15-13:15 | 4 | London 09:15+240 | +4.83 (4.4) / +2.62 (2.4) / +0.32 (0.2) | +1.98 / -0.32 | 0.54, 0.12 | decaying |
| XAUUSD long, weekday before a UK holiday, 02:00-06:00 | 1 | Tokyo 11:00+240 | +9.82 (4.4) / +6.73 (2.5) / +1.46 (0.3) | +4.84 / +0.41 | 0.69, 0.22 | decaying; 4-5 events a year; beats 35 % / 42 % of random |
| 13 more families | 1-7 each | | t_IS 2.1-3.3 | | | 9 are Tokyo-fix adjacent. Only two are net > 0 in IS and VAL: EURUSD long on Tuesdays 02:30-04:30 UTC (+2.11 / +1.08 / +0.92, net +0.37 / +0.26, net t_IS about 0.9, power about 0.5) and USDCHF short 00:45-01:00 UTC on the last weekday of the month (the Tokyo fix on a gotobi day, i.e. C3's mechanism) |

## Candidate evaluations (step 3)
| cell | where | PRE / IS / VAL mid bp (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS | power IS / VAL | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| **E1** short EURUSD 11:00-13:00 London | EURUSD | +1.69 (5.21) / +1.80 (5.08) / +1.97 (3.59) | 0.63 / 0.62 | +1.17 (3.29) / +1.35 (2.46) | 1.10 | 1.78 / 1.88 | 100 % / 99 % | **DEMO** (fails LIVE on power) |
| E1 on the New York clock, 06:00-08:00 | EURUSD | +1.57 (4.87) / +1.64 (4.69) / +2.05 (3.81) | 0.64 / 0.62 | +1.00 (2.87) / +1.43 (2.66) | 1.26 | 1.55 / 2.03 | | same effect (the clocks differ about 3 weeks a year) |
| E1 on a fixed UTC clock, 10:00-12:00 UTC | EURUSD | +1.62 (5.03) / +1.08 (3.15) / +1.82 (3.55) | 0.64 / 0.63 | +0.43 (1.27) / +1.19 (2.33) | 1.69 | 0.68 / 1.78 | | weaker: the effect follows European local time |
| E2 long USDCHF 10:00-12:00 UTC | USDCHF | +1.51 (4.42) / +1.02 (3.04) / +1.08 (2.19) | 0.94 / 0.89 | +0.08 (0.23) / +0.19 (0.39) | 1.06 | 0.12 / 0.30 | 100 % / 90 % | stable but at cost; break-even 1.0-1.1 bp |
| E3 basket, E1 + long USDCHF 11:00-13:00 London (post hoc) | 2 legs a day | day +2.96 (4.65) / +3.41 (5.23) / +2.56 (2.63) | | day +1.85 (2.84) / +1.07 (1.10) | 0.75 | 1.54 / 0.84 (days) | | fails: the USDCHF leg decays (VAL +0.59) |
| G1 long GBPJPY 17:30-21:30 London | GBPJPY | +2.21 (4.33) / +1.65 (3.31) / +1.43 (1.94) | 1.24 / 1.09 | +0.41 (0.82) / +0.34 (0.46) | 0.87 | 0.44 / 0.35 | 94 % / 50.5 % | fails: net t, control. Stable, break-even 1.4-2.2 bp |
| XAU long 02:00-06:00 UTC, weekday before a UK holiday | XAUUSD | +9.82 (4.41) / +6.73 (2.51) / +1.46 (0.28) | 1.89 / 1.04 | +4.84 (1.79) / +0.41 (0.08) | 0.22 | 0.97 / 0.06 | 35 % / 42 % | fails, decaying |

E1 by year, mid bp:
- PRE: 1.8, 2.2, 2.4, -0.3, 1.5, 1.6, 3.4, 2.0, 1.8, 1.0, 0.9, 1.9;
- IS: 3.7, 2.0, 1.5, 2.1, -0.1, 1.6;
- VAL: 3.5, 1.6, 0.8.

PRE sub-periods: 2004-07 +1.52, 2008-11 +2.13, 2012-15 +1.40. Correlation with C3 on IS + VAL: daily +0.043, monthly
+0.055.

### What E1 is made of (reported after the plateau check)
| EURUSD 15-min slot, London time (short side) | PRE | IS | VAL |
|---|---|---|---|
| 11:00-11:15 | +0.19 (1.6) | +0.19 (1.6) | +0.35 (1.9) |
| 11:45-12:00 | **+1.25 (11.0)** | +0.08 (0.7) | -0.03 (-0.2) |
| 12:45-13:00 | +0.52 (3.7) | **+1.09 (5.9)** | **+1.12 (4.5)** |
| 13:00-13:15 (after the window) | **+1.20 (8.9)** | -0.72 (-5.4) | -0.81 (-3.9) |
| 13:15-13:30 (after the window) | -0.93 (-6.0) | +0.02 | -0.02 |
| E1 minus 11:45-12:00 | +0.43 (1.41) | +1.71 (5.12) | +2.00 (3.78) |
| E1 minus 11:45-12:00 and 12:45-13:00 | -0.09 (-0.33) | +0.62 (2.21) | +0.88 (1.89) |

- The 11:45-12:00 slot (12:45-13:00 CET) was positive in every PRE year and is about 0 from 2016. Its PRE yearly
  values are 1.48, 1.41, 1.00, 0.35, 0.93, 1.94, 2.73, 0.82, 1.63, 1.49, 0.67, 0.58; from 2016 they are between
  -0.27 and +0.46.
- The V around the 14:15 CET ECB fix moved 15 minutes earlier at the same boundary:
  - until 2015, EUR fell 13:00-13:15 London and rose 13:15-13:30;
  - from 2016, it falls 12:45-13:00 and rises 13:00-13:15. Rounds 4, 10 and 12 measured this rise.
- So E1's mean is stable across the eras, but its parts are not. A clock-fixed institutional practice changed timing
  once in 21 years and can change again.
- Plateau, IS mid bp:
  - 10:45-12:45: +0.62;
  - 11:15-13:15: +0.88;
  - 11:00-12:00: +0.68;
  - 11:00-15:00: +0.89;
  - 12:00-13:00: +1.11 (PRE +0.05).

### The same window on every symbol, side from PRE: mid PRE / IS / VAL (net IS / VAL)
- USDJPY long: +1.08 / +0.88 / +0.95 (+0.14 / +0.25). Stable, but at cost.
- EURJPY short: +0.58 / +0.92 / +1.01 (+0.06 / +0.12).
- USDCHF long: +1.27 / +1.61 / +0.59 (+0.69 / -0.28).
- GBPUSD short: +0.20 / +0.76 / +1.65.
- AUD, NZD, CAD and XAU pairs: wrong sign or about 0 after 2016.
- The window is a EUR (and partly USD-vs-JPY) effect, not a broad USD move.

## Stable effects below cost (break-even = mid on the PRE side; IS / VAL)
| effect | break-even bp | cost bp |
|---|---|---|
| E2 USDCHF long 10:00-12:00 UTC | 1.02 / 1.08 | 0.94 / 0.89 |
| USDJPY long 11:00-13:00 London | 0.88 / 0.95 | 0.77 / 0.73 |
| G1 GBPJPY long 17:30-21:30 London | 1.65 / 1.43 | 1.24 / 1.09 |
| ECB-fix pre-leg, EURUSD short 12:45-13:00 London | 1.09 / 1.12 | 0.63 / 0.62 (per-trade net Sharpe about 0.06, power about 1.3) |

## What this says
- A 12-year discovery era finds many real clock effects: 47 of 120 family-wise-significant PRE cells confirm in IS,
  against 9 by chance. But they shrink to about a fifth in IS and lose another quarter in VAL. Most are 0.3-1 bp,
  below IC's 0.6 bp commission plus spread.
- The only stable effect above cost is in EURUSD's European midday, and it is about 1.2 bp net, too small to reach
  power 3 with one trade a day. To reach LIVE it would need about 1.6x the per-trade Sharpe, or about 2.5x the trade
  count at the same Sharpe from uncorrelated legs. Neither exists among the 11 symbols here.
- Calendar day types (month-end, quarter-end, business day of the month, holidays) add nothing over 21 years beyond
  what rounds 3-4 found. The gotobi-like structure is in clocks, not in dates, outside gotobi itself.
- Surprise: institutional clock timings do change. The 12:45 CET EUR drop ended and the ECB-fix V moved 15 minutes at
  the 2015/16 boundary. "Structural" does not mean permanent.

## Directions that need the user
1. Whether to run E1 on demo, as a DEMO-tier rule with expected HOLD t 1.9. HOLD cannot confirm it at the LIVE level.
2. Dukascopy M1 2004-2015 for GBPUSD, AUDUSD, NZDUSD, USDCAD, AUDJPY and XAUUSD. They are H1-only here, so their PRE
   discovery ran at hour resolution and could not see 15-minute fix effects (the E1 slots are 15-minute effects).
3. A commission-free EURUSD venue would move E1 from about 1.2 to about 1.8 bp net (power about 2.7). That is still
   short of LIVE.

## Scripts and outputs (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r13/M/`)
- `mcommon.py`: grids, clocks, day types, window matrices, costs.
- `scan1.py`: every cell's stats in PRE, IS and VAL, and the PRE permutation. Writes `cells.npz` and `perm_pre.npz`.
  Only PRE was read for selection.
- `step2.py`: the carried sets, IS confirmation, IS permutation and VAL. Output `step2.out`.
- `step3.py`: candidate evaluations, random-entry controls and C3 correlation. Output `step3.out`.
- `step4.py`: plateau, same window on all symbols, E1 by day type, family table, XAU before UK holidays. Output
  `step4.out`.
- `step4b.py` and `step4c.py`: E1's 15-minute slots and the decomposition. Outputs `step4b.out` and `step4c.out`.
- `step5.py`: shrinkage and stability counts. Output `step5.out`.
- `show_pre.py`: top PRE cells.
