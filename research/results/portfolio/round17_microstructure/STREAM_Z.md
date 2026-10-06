# Round 17, stream Z: big-day intraday momentum in European index CFDs

2026-10-06. Hypotheses, rule, gate, cuts, cell count and controls were written at 02:42 UTC, before any return was
computed: [HYPOTHESES_Z.md](HYPOTHESES_Z.md). Only quote coverage was looked at beforehand. HOLD was never loaded: the
panel ends 2024-12-31, and the bid-only caches (STOXX50, F40, ES35, IT40) are cut at ts < 2025-01-01 at load. No PRE
era: no index data before 2016.

## Answer
- **LIVE: none. DEMO: none. No PREREG draft.**
- **Primary cell** (declared beforehand: EU5 pooled, previous-close reference, cut 13:30 CET, hold to the 17:30 close,
  top decile): mid +1.39 bp (t 0.3) IS / -1.25 (-0.3) VAL; net -2.10 (-0.5) / -4.18 (-1.0); power -0.24 / -0.76.
- **European family** (72 counted cells: 5 symbols + pool x 2 references x 3 cuts x 2 horizons):
  - no cell reaches IS net t 2.0; the best is UK100 P 13:30 +60 min, +3.13 (t 1.3), with VAL +0.31;
  - the average top-decile mid over the 60 single-symbol cells is +1.1 bp IS / +1.8 VAL, against a 3.7 bp cost. The
    sign follows the literature (61-62 % of cells have mid > 0), but the effect is a third of the cost.
- **US comparison** (20 counted cells, US30/USTEC from the 09:30 ET open): the best is US30 P 13:30 +60 min, net
  +7.30 (t 2.3) IS / +1.09 (t 0.3) VAL. It fails DEMO:
  - only 5/9 years are positive;
  - without March-April 2020 its IS net is +2.18 (t 1.0);
  - its IS net t sits inside the shared null (p 0.16).
  - Every US IS dose slope comes from 2020: US30 t +3.3 becomes 0.0 without it, and turns -0.8 in VAL.
- **DE40 (information)**: the round-13 observation does not carry over to multi-hour holds from a cut. The 13:30 cut
  to the close nets +0.78 (t 0.1) IS / +1.52 (t 0.2) VAL. The dose slope is about 0 at 13:30 with 2020 (+2.1 without
  it) and +0.3 in VAL.
- **Nothing beats chance.**
  - Max IS net t across the 104 cells in the null is +2.26, against a null 95 % of max of 2.65 (p 0.16).
  - Max VAL net t is +1.79, against 2.95 (p 0.60).

## Cells
- **Units.** bp; t is clustered by UTC day. EU5 = the mean of the selected trades of STOXX50, F40, ES35, IT40 and
  UK100 per day.
- **References.** P = from the previous cash close; O = from the cash open (09:05 CET, 08:05 London, 09:35 ET).
- **Cuts and horizons.** Cuts are in CET; UK100 uses the same instants. Horizon "close" exits at 17:30 CET (16:30
  London, 16:00 ET); "60" exits after 60 minutes.
- **Costs.** Panel symbols pay half the actual spread at each fill. The bid-only symbols pay round 7's published
  spreads: STOXX50 1.5, F40 1.79, ES35 4.2 and IT40 9.0 points, i.e. 2.5-4.6 bp round trip.
- **Power** = per-trade (pooled: per-day) net Sharpe x sqrt(1.73 x trades a year). The VAL column is the expected
  HOLD t.
- The full 104-row table, with all-days means, winsorised means, dose bins and every year, is in analyze_out.txt.

### EU5 pooled (counted)
| cell | days/yr IS/VAL | top mid IS (t) | VAL (t) | cost IS/VAL | net IS (t) | net VAL (t) | ex-Mar/Apr-20 net IS (t) | +1 min IS/VAL | x1.5 IS/VAL | power IS/VAL | yrs>0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P 12:00 close | 51 / 59 | +3.85 (0.7) | +4.09 (0.8) | 3.48 / 2.95 | +0.37 (0.1) | +1.14 (0.2) | +1.82 (0.5) | -0.74 / -0.12 | -1.36 / -0.34 | +0.04 / +0.18 | 5/9 |
| P 12:00 60 | 51 / 59 | +1.97 (0.9) | +0.32 (0.2) | 3.45 / 2.95 | -1.48 (-0.7) | -2.63 (-1.3) | -2.61 (-1.5) | -1.43 / -2.15 | -3.21 / -4.10 | -0.38 / -1.00 | 3/9 |
| **P 13:30 close (primary)** | 57 / 62 | +1.39 (0.3) | -1.25 (-0.3) | 3.49 / 2.94 | -2.10 (-0.5) | -4.18 (-1.0) | +0.19 (0.1) | -3.44 / -5.50 | -3.85 / -5.65 | -0.24 / -0.76 | 3/9 |
| P 13:30 60 | 57 / 62 | +1.58 (1.0) | -1.89 (-0.9) | 3.47 / 2.94 | -1.89 (-1.2) | -4.83 (-2.4) | -2.22 (-1.8) | -1.78 / -4.95 | -3.62 / -6.30 | -0.63 / -1.80 | 1/9 |
| P 15:30 close | 55 / 60 | +1.52 (0.5) | +1.23 (0.3) | 3.53 / 2.93 | -2.01 (-0.7) | -1.70 (-0.5) | -1.41 (-0.6) | -2.75 / -3.68 | -3.78 / -3.17 | -0.36 / -0.36 | 4/9 |
| P 15:30 60 | 55 / 60 | +2.99 (1.2) | +2.04 (0.8) | 3.52 / 2.92 | -0.53 (-0.2) | -0.89 (-0.3) | +1.06 (0.6) | +0.08 / -1.94 | -2.29 / -2.35 | -0.11 / -0.25 | 4/9 |
| O 12:00 close | 59 / 60 | -3.41 (-0.8) | +6.94 (1.4) | 3.49 / 2.97 | -6.90 (-1.7) | +3.97 (0.8) | -2.68 (-0.8) | -8.26 / +3.64 | -8.64 / +2.48 | -0.92 / +0.62 | 5/9 |
| O 12:00 60 | 59 / 60 | -1.53 (-0.9) | +0.10 (0.1) | 3.48 / 2.97 | -5.01 (-3.0) | -2.87 (-1.4) | -4.35 (-3.5) | -4.87 / -2.56 | -6.75 / -4.36 | -1.62 / -1.10 | 2/9 |
| O 13:30 close | 60 / 62 | -5.10 (-1.2) | +7.01 (1.7) | 3.49 / 2.87 | -8.58 (-2.0) | +4.15 (1.0) | -1.06 (-0.4) | -9.52 / +4.16 | -10.32 / +2.71 | -1.06 / +0.75 | 3/9 |
| O 13:30 60 | 61 / 62 | -0.91 (-0.7) | +1.91 (0.9) | 3.47 / 2.87 | -4.38 (-3.1) | -0.95 (-0.5) | -2.81 (-2.5) | -4.39 / -0.61 | -6.12 / -2.38 | -1.67 / -0.35 | 3/9 |
| O 15:30 close | 57 / 63 | +0.85 (0.3) | -0.36 (-0.1) | 3.56 / 2.97 | -2.72 (-1.0) | -3.33 (-0.9) | -2.18 (-0.9) | -3.93 / -4.29 | -4.50 / -4.82 | -0.52 / -0.67 | 2/9 |
| O 15:30 60 | 58 / 63 | +1.50 (0.6) | -2.06 (-0.8) | 3.57 / 2.97 | -2.06 (-0.8) | -5.03 (-1.8) | -0.87 (-0.4) | -1.46 / -6.41 | -3.85 / -6.52 | -0.45 / -1.39 | 1/9 |

EU5 P 13:30 close, net by year 2016-24: -12.5, -5.7, +4.6, +5.9, -14.1, +5.5 | -2.2, -4.2, -5.3.

### Per symbol, primary specification (P, 13:30 cut, hold to close), and the best cell of each symbol by IS net t
| symbol | P 13:30 close: top mid IS / VAL | cost | net IS (t) / VAL (t) | VAL/IS net | best cell by IS net t: net IS (t) / VAL (t) |
|---|---|---|---|---|---|
| STOXX50 | -2.15 / -0.29 | 4.4 / 3.5 | -6.56 (-0.7) / -3.76 (-0.5) | | O 15:30 close: +1.29 (0.3) / -1.24 |
| F40 | -1.10 / +2.52 | 3.4 / 2.5 | -4.55 (-0.6) / +0.01 (0.0) | | O 15:30 60: -0.53 (-0.2) / -4.31 |
| ES35 | -0.33 / -3.60 | 4.7 / 4.5 | -4.99 (-0.5) / -8.14 (-1.1) | | O 15:30 close: +4.68 (1.1) / -2.07 |
| IT40 | +4.12 / +2.37 | 4.3 / 3.2 | -0.13 (-0.0) / -0.84 (-0.1) | | O 13:30 close: +7.20 (1.1) / -3.04 |
| UK100 | +3.89 / +4.88 | 1.7 / 1.3 | +2.19 (0.3) / +3.60 (0.7) | 1.64 | P 13:30 60: +3.13 (1.3) / +0.31 |
| info: DE40 | +1.64 / +1.84 | 0.85 / 0.32 | +0.78 (0.1) / +1.52 (0.2) | 1.94 | P 12:00 close: +6.92 (0.9) / -0.88 |
| US30 (09:30 ET open) | +14.93 / -9.15 | 0.96 / 0.30 | +13.97 (1.9) / -9.44 (-1.3) | -0.68 | P 13:30 60: +7.30 (2.3) / +1.09 (0.3) |
| USTEC | +12.41 / +1.24 | 1.62 / 0.59 | +10.79 (1.5) / +0.64 (0.1) | 0.06 | P 13:30 60: +5.14 (1.7) / +3.25 (0.9) |

US30 P 13:30 close, net by year: +11.6, -4.6, +24.6, +0.4, **+52.4 (2020)**, -6.7 | -15.6, -1.3, -11.1. Without
March-April 2020 its IS net is +4.21 (t 0.8).

### Best cells against the bars
| cell | IS net (t) | VAL net (t) | yrs>0 | ex-2020 IS (t) | +1 min IS/VAL | x1.5 IS/VAL | RC-B beats IS/VAL | power IS/VAL | shared null p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| US30 P 13:30 60 | +7.30 (2.3) | +1.09 (0.3) | 5/9 | +2.18 (1.0) | +6.19 / +0.92 | +6.86 / +0.96 | 92 % / 76 % | 1.21 / 0.24 | 0.16 | fails years, 2020, null |
| USTEC P 13:30 60 | +5.14 (1.7) | +3.25 (0.9) | 4/9 | +0.01 (0.0) | +3.09 / +3.10 | +4.35 / +2.97 | 97 % / 64 % | 0.89 / 0.70 | | IS t < 2; all 2020 |
| USTEC P 12:00 close | +7.79 (1.1) | +14.16 (1.8) | 5/9 | -1.05 (-0.2) | +3.44 / +13.50 | +6.98 / +13.87 | 66 % / 98 % | 0.58 / 1.36 | VAL p 0.60 | IS is 2020 (+77.6 bp that year) |
| UK100 P 13:30 close | +2.19 (0.3) | +3.60 (0.7) | 6/9 | +5.10 (1.2) | +0.91 / +1.66 | +1.34 / +2.95 | 87 % / 88 % | 0.17 / 0.51 | | t far below 2 |
| EU5 P 12:00 close | +0.37 (0.1) | +1.14 (0.2) | 5/9 | +1.82 (0.5) | -0.74 / -0.12 | -1.36 / -0.34 | 99 % / 78 % | 0.04 / 0.18 | | ~0 net |

## Dose-response (all days, horizon close, P reference)
- Slopes come from an OLS of signed momentum on min(|z|, 4). Pooled slopes average the symbols per day first,
  because the European indices move together; checks_out.txt has them.

| cell | slope t IS | IS without Mar-Apr 2020 | VAL |
|---|---|---|---|
| EU5 12:00 | +1.7 | +1.8 | +0.6 |
| EU5 13:30 | -0.3 | +2.3 | +0.2 |
| EU5 15:30 | +0.6 | +0.8 | +0.9 |
| UK100 13:30 / 15:30 | -0.5 / +0.1 | +1.1 / +0.2 | +2.2 / +2.4 |
| info: DE40 12:00 / 13:30 / 15:30 | +1.3 / +0.1 / +1.3 | +1.0 / +2.1 / +1.2 | +0.6 / +0.3 / +0.7 |
| US30 12:00 / 13:30 | +3.3 / +2.5 | +0.0 / +0.3 | -0.8 / -1.0 |
| USTEC 12:00 / 13:30 | +2.8 / +3.3 | +0.9 / +1.2 | +0.6 / +0.6 |

- **Europe.** The slope is positive in almost every cell, the literature's sign, but no cell has t >= 2 in both eras.
  March-April 2020 was a reversal regime in Europe at the 13:30 cut: the > 3 sd bin is -31.9 bp IS (n 70). Without it
  the IS slope turns positive.
- **US.** The slope is a 2020 artefact, as in round 13 P.

## Random-entry controls (random_ctrl.py, 500 seeds, same selected days, side recomputed at the random time)
| cell | RC-A (declared): random mean IS / VAL, beats | RC-B (post-signal): random mean IS / VAL, beats |
|---|---|---|
| EU5 P 13:30 close | +20.95 / +17.47, 0 % / 0 % | -2.96 / -3.32, 78 % / 26 % |
| EU5 P 12:00 close | +16.69 / +19.78, 0 % / 0 % | -2.52 / -0.03, 99 % / 78 % |
| UK100 P 13:30 close | +24.15 / +16.04, 0 % / 0 % | -0.70 / +0.98, 87 % / 88 % |
| US30 P 13:30 60 | +10.68 / +7.80, 14 % / 4 % | +3.45 / -0.86, 92 % / 76 % |
| USTEC P 13:30 60 | +10.54 / +12.05, 7 % / 1 % | +0.57 / +1.91, 97 % / 64 % |
| USTEC P 12:00 close | +27.46 / +35.74, 0 % / 0 % | +6.92 / +8.25, 66 % / 98 % |
| IT40 P 12:00 close; info DE40 P 12:00 close | 0 % / 0 % | 97 % / 58 %; 76 % / 45 % |

- **RC-A, the declared control, is not usable for multi-hour holds.** Its random windows mostly start before the cut.
  They therefore contain the morning move that selected the day, and the side is computed from that same move, so
  the control earns +8 to +36 bp by construction.
  - The hypotheses warned of this bias, but its size makes RC-A uninformative here.
  - It does not change any verdict: nothing met the IS/VAL bars before the control.
- **RC-B, entry strictly after the signal, is the informative control.**
  - Entering later on the same days earns the same as entering at the cut, about -3 bp net for EU5 at 13:30.
  - So there is no continuation left after the cut to be timed.
- Future rounds with long holds should use RC-B, or random cuts with the gate recomputed.

## Chance (perm.py: one sign per UTC day, shared by all 104 cells, 1,000 permutations)
| statistic | best observed | null 95 % of max | p |
|---|---|---|---|
| IS mid \|t\| | 2.52, US30 P 13:30 60 | 3.31 | 0.49 |
| IS net t | +2.26, US30 P 13:30 60 | 2.65 | 0.16 |
| VAL net t | +1.79, USTEC P 12:00 close | 2.95 | 0.60 |

Only 1 of the 92 counted cells has IS net t >= 2. Of the 72 European cells, 9 are net > 0 in both eras, all with
\|t\| < 1.3.

## C3 correlation (IS+VAL, information only: no survivor)
| cell | daily | monthly |
|---|---|---|
| US30 P 13:30 60 | +0.008 | +0.085 |
| USTEC P 12:00 close | -0.003 | +0.001 |
| EU5 P 13:30 close | -0.014 | -0.109 |
| UK100 P 13:30 close | -0.029 | -0.130 |

## What this says
- **Big-day intraday momentum in the European indices is the literature's sign but about a third of IC's cost.**
  - Over a 2-5.5 hour hold, the average top-decile mid is +1-2 bp; the bid-only indices cost 2.5-4.6 bp round trip.
  - The longer hold did not make cost a small share. The extra hours added variance, not drift: the top-decile sd is
    tens of bp, and the mean stayed at a few bp.
- **The out-of-sample replication of round 13's DE40 observation fails.**
  - STOXX50, F40, ES35 and IT40 show no big-day continuation from a midday cut, and DE40 itself shows none at this
    horizon.
  - Round 13's DE40 dose slope was a 15-minute effect near the close. It does not scale up to a cut-to-close trade.
- **The US big-day momentum of the literature is March-April 2020 in IS and absent in VAL.** This is round 13 P's
  finding again (US30: IS dose t +3.3 -> 0.0 without 2020; VAL -0.8).
- **Europe in March-April 2020 reversed at the 13:30 cut** (the > 3 sd bin is -32 bp). So the 2020 regime cuts both
  ways: it flattered the US and hurt Europe. Results without it are in every table.
- **Post hoc, not a candidate.** UK100's VAL dose slope is +2.2 / +2.4 at the 13:30 / 15:30 cuts, with an IS slope of
  about 0.
- **Nothing here needs the user.**
  - A pre-2016 M1 history of European index futures would only re-measure a +1-2 bp effect that is below cost at IC.
  - A cheaper venue for STOXX50 / F40 (futures at about 0.5-1 bp round trip) is the only change that would make the
    +1-4 bp top-decile mid worth re-testing. That is the same cost-structure decision as in rounds 15-16.

## Scripts and outputs (scratchpad r17/Z/)
- coverage.py: quote coverage only, run before the hypotheses.
- libz.py: loading (HOLD cut at load), venue days, clocks, statistics.
- build.py -> sess_<SYM>.npz: per-day session matrices of mid and spread, from the open - 5 min to the close + 1 min.
- rows.py -> rows_Z.pkl: z, gate, trades and the +1 minute variant for every cell (with a glitch check of the
  largest moves: all are real March 2020 or CPI days).
- analyze.py -> analyze_out.txt, res_Z.pkl: all 104 cells, dose bins and years.
- perm.py -> perm_out.txt; random_ctrl.py -> random_out.txt; c3corr.py -> c3corr_out.txt; checks.py ->
  checks_out.txt (day-averaged and ex-2020 dose slopes).
