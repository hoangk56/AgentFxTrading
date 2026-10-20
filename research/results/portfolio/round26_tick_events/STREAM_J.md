# Round 26, stream J: unscheduled jumps on IC ticks (continuation or reversal, net of IC's costs)

Written 2026-10-17 20:55 UTC (from `date -u`). [HYPOTHESES_J.md](HYPOTHESES_J.md) declared all 7,776 cells at
20:17 UTC, before any forward return was computed. It has three addenda:
- Addendum 1 (20:33 UTC): written after event counts only, before any cell return. It adds the clock filter E10,
  makes D2 the primary definition and adds two robustness requirements that only raise the bar.
- Addendum 2 (20:43 UTC): written after the results. It defines the PRE check.
- Addendum 3 (20:58 UTC): information-only additions (the causal panel check, the stop-flag redefinition).

HOLD was never loaded:
- every tick day is asserted < 2025-01-01;
- the panel ends 2024-12-31;
- Dukascopy data is cut at 2015-12-31;
- the HOLD rows of the C3 file were skipped.

## Answer
- **No LIVE candidate. One effect meets the DEMO numbers and is within chance.** It fades the largest co-moving
  precious-metals jumps in the Asian session: 16 x the local 1-minute sigma within 10-30 s, a gold or silver move
  confirmed by another USD-quoted instrument, held 15 min.
  - D2, IS: +12.15 bp net (day-clustered t 2.60, n 46).
  - D2, VAL: +18.49 (t 2.17, n 7).
  - It passes x1.5 spread, +1 minute, the random-time control (100 %), winsorising, and IS without March-April
    2020.
  - Against it:
    - 13.8 % of the per-day sign-flip null draws beat its t over the family's 7,392 cells;
    - it takes the side opposite to the declared mechanism (co-moving jumps should continue);
    - 37 of its 53 events are in 2016-17, and it gets about 2 events a year since 2018;
    - HOLD would hold about 4 events.
  - Draft: [PREREG_DRAFT_J_metals_comove_fade.md](PREREG_DRAFT_J_metals_comove_fade.md), with the recommendation
    not to open HOLD.
- **J1 (continuation) fails everywhere.**
  - In the LIQUID set (AUDUSD, NZDUSD, XAUUSD, US30, USTEC), co-moving jumps revert at mid instead of continuing
    (W10 k16 h15: -7.09 bp IS, -8.70 VAL).
  - Net, 1 of 54 primary cells is >= 0 in IS (+0.04 bp) and none in VAL.
  - The best J1 cell (index co-moving jumps, 15 min) is +5.78 bp (t 2.08) in IS and -4.46 (t -1.76) in VAL.
- **J2 (reversal) is real at mid but below IC's cost.**
  - Single-instrument jumps revert in every class and both eras: +0.6 to +3.5 bp at mid in the LIQUID set (t up to
    8.6 in IS and up to 3.8 in VAL), against a round trip of about 1.6-1.9 bp.
  - 0 of 54 primary cells are net > 0 in IS.
  - Even at zero latency, which no bot achieves, the best primary cells reach only +0.2 to +0.8 bp in IS.
- **Mechanism split.** In the large-sample sets (k6, k10), single-instrument jumps revert more than co-moving ones
  in all four classes, as the liquidity story predicts. But co-moving FX and metal jumps also revert, and co-moving
  index jumps continued only in IS.
  - An information-only panel label (a broad USD move, or US500 for indices, from the minute before the jump to the
    minute after it) separates the two cleanly: with it the jump continues (+0.9 to +2.6 bp, t 3.2-10, IS and VAL),
    without it the jump reverts (-1.1 to -3.1 bp, t -7.5 to -14).
  - Once that label is known (entry at +60 s), the continuation is about 0 for USD-quoted jumps and +0.5 to
    +0.8 bp at mid for index jumps (net -0.9 to +0.1 bp). The information in
    an unscheduled jump is priced within its first minute: round 8's result, now at tick level.
- **Surprise: many "unscheduled" jumps sit on fixed clocks.** 13-30 % per instrument (XPT 6 %) of the jumps that
  passed the declared exclusions were at venue clock minutes:
  - 01:00 / 05:30 UTC: the Shanghai metals and oil day open and afternoon reopen (silver at 01:00 UTC is 189x the
    average minute);
  - 13:00 UTC: the 21:00 Beijing night session;
  - the European cash open for US30 / USTEC;
  - 07:00 New Zealand for NZDUSD;
  - the 15:50 NY MOC imbalance;
  - the 13:24 NY silver settlement minute;
  - 01:15 UTC (the CNY fixing).
  A count-based filter (E10, Addendum 1) removed them before any return was computed. Without it (definition D1) the
  same metals cell is IS t 2.95 / VAL t 2.52, just past the null's 95 % (4.3 % of draws beat it).

## How this differs from the earlier shock tests
| earlier test | what it did | here |
|---|---|---|
| round 3 (flow_search_2026-09-27, "Liquidity provision") | Asian-hours M5 fades of 2-3 ATR from SMA20 held for hours; BTC/ETH cascades of \|z\| 3-5 over 1-6 h held 2-8 h; tick-count reversal over days | detection over <= 10 / 30 / 60 s on ms ticks, holds of 1-15 min, 10 non-crypto instruments, fills at the actual bid / ask after 0 / 250 / 1,000 ms or the next tick |
| round 6 S5 | US30 / USTEC 5-minute bars 09:35-15:50 ET, shocks of 2-4 sd of the clock slot, entry at the next 5-min bar, releases kept in | all sessions, releases / central-bank windows / rollover / venue clocks removed, both sides, a cross-instrument mechanism label |
| round 17 Y | unconditional regressions of 1-60 min returns on signed quote flow; 1-minute inventory reversal (~0.05 bp) | an event study of rare jumps only (6-16 sigma), split by co-movement |
| round 8 S | a source's 5/15-min shock predicting other symbols from the next minute | the jumping instrument itself at ms latency; co-movement used as a label of information |

## Definitions (exact rules in HYPOTHESES_J.md)
- **Jump.** The mid moves >= theta within <= W s (range: the current mid against the minimum or maximum of the
  prevailing mids over the window).
  - theta = max(k x sigma, 2 x the trailing 60-min median spread).
  - sigma = the bipower 1-minute sd of the previous 60 minutes (Lee & Mykland 2008).
  - W in {10, 30, 60} s and k in {6, 10, 16}: 9 event sets.
  - One event per instrument per 15 min.
- **Exclusions:**
  - E1: +-30 min around High / Medium rows of the instrument's currencies, plus USD and All;
  - E2: central-bank windows;
  - E3, E4: untimed rows and votes (whole days);
  - E5: energy reports;
  - E6: rollover 16:35-18:10 NY;
  - E7: declared venue clocks;
  - E8: 30 min after quote gaps;
  - E9: IC artefacts;
  - E10 (D2 only): the count-flagged clock minutes.
- **Labels.**
  - CO: a same-group partner moved >= 2 of its own sigma the same way over [t_d - 60 s, t_d]. Groups: USD-quoted
    FX and metals; US30-USTEC; XTI-XBR.
  - SINGLE: no other tick instrument moved >= 2 sigma.
  - OTHER: everything else.
- **Fills.** Buy at the ask, sell at the bid of the first tick >= t_d + L, with L = 250 ms for decisions (also 0,
  1,000 ms and the next tick; +60 s for the bar's "+1 minute"). Exit at t_d + L + h, h in {1, 5, 15} min.
  Optional resting stop at theta from the entry mid. Commission 0.6 bp round trip for FX and metals, 0 for indices
  and energies.
- **Controls.** RT: 200 random times per event in the same instrument, UTC day and session, with the side
  recomputed from the trailing-W move. RD: random side at the actual events.
- **Bars.** Round 13's LIVE / DEMO bars, plus winsorised and ex-March-April-2020 checks.
- **Cells.** 2 sides x 9 sets x 3 h x 2 stop x 3 mechanism (ALL / CO / SINGLE) x 6 instrument sets (LIQUID, ALL10,
  FX, METALS, INDICES, ENERGY) x 4 sessions (ALL / Asia / Europe / US) = 7,776 per definition. The 108 primary cells
  are J1-CO and J2-SINGLE on LIQUID over all sessions.

## 1. Jump counts and exclusions (D2)
### Events per year by instrument and set (IS / VAL); IS = 2016-21 (energies 2018-21), VAL = 2022-24
| instrument | W10 k6 | W10 k10 | W10 k16 | W30 k6 | W30 k10 | W30 k16 | W60 k6 | W60 k10 | W60 k16 |
|---|---|---|---|---|---|---|---|---|---|
| AUDUSD | 133 / 56 | 23 / 11 | 5 / 3 | 326 / 143 | 51 / 28 | 12 / 6 | 650 / 344 | 83 / 46 | 17 / 9 |
| NZDUSD | 156 / 66 | 28 / 14 | 9 / 3 | 370 / 170 | 59 / 28 | 14 / 6 | 739 / 391 | 91 / 43 | 19 / 9 |
| XAUUSD | 261 / 105 | 54 / 13 | 12 / 2 | 507 / 241 | 94 / 33 | 20 / 5 | 898 / 521 | 149 / 62 | 27 / 8 |
| XAGUSD | 164 / 62 | 35 / 6 | 8 / 1 | 413 / 183 | 71 / 20 | 14 / 2 | 797 / 432 | 122 / 46 | 24 / 3 |
| XPTUSD | 18 / 5 | 6 / 1 | 2 / 1 | 43 / 15 | 12 / 4 | 3 / 1 | 90 / 42 | 22 / 13 | 5 / 3 |
| US30 | 124 / 109 | 26 / 21 | 5 / 3 | 290 / 241 | 57 / 42 | 12 / 8 | 596 / 502 | 95 / 69 | 18 / 15 |
| USTEC | 116 / 115 | 26 / 22 | 5 / 2 | 258 / 272 | 51 / 48 | 9 / 8 | 518 / 583 | 84 / 78 | 15 / 13 |
| XTIUSD | 201 / 162 | 52 / 28 | 14 / 6 | 427 / 348 | 91 / 50 | 20 / 9 | 815 / 729 | 148 / 85 | 31 / 13 |
| XBRUSD | 120 / 107 | 20 / 13 | 4 / 2 | 285 / 253 | 45 / 30 | 8 / 5 | 576 / 527 | 76 / 51 | 11 / 9 |
| XNGUSD | 193 / 51 | 115 / 22 | 69 / 8 | 309 / 108 | 144 / 38 | 76 / 13 | 486 / 202 | 179 / 67 | 87 / 18 |

### Session split, set W30 k10: events per year IS / VAL
| instrument | Asia | Europe | US |
|---|---|---|---|
| AUDUSD | 21 / 10 | 10 / 9 | 20 / 9 |
| NZDUSD | 31 / 11 | 9 / 7 | 19 / 11 |
| XAUUSD | 37 / 18 | 36 / 9 | 22 / 6 |
| XAGUSD | 29 / 11 | 24 / 4 | 17 / 5 |
| XPTUSD | 4 / 2 | 4 / 1 | 4 / 1 |
| US30 | 22 / 17 | 19 / 16 | 16 / 9 |
| USTEC | 24 / 29 | 17 / 8 | 10 / 11 |
| XTIUSD | 42 / 31 | 31 / 8 | 18 / 11 |
| XBRUSD | 18 / 14 | 15 / 6 | 12 / 10 |
| XNGUSD | 60 / 12 | 60 / 19 | 24 / 7 |

### Raw detections (same rule, no exclusion, own dead time) and the share each exclusion removes, all sets pooled
| instrument | raw | calendar E1-E5 | E1 timed rows | E2 CB windows | E3+E4 untimed / votes | E5 energy | E6 rollover | E7 clocks | E8 reopen | E9 artefacts | any |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDUSD | 32781 | 0.42 | 0.34 | 0.07 | 0.11 | 0.00 | 0.26 | 0.01 | 0.00 | 0.00 | 0.71 |
| NZDUSD | 35825 | 0.39 | 0.30 | 0.06 | 0.11 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.70 |
| XAUUSD | 30360 | 0.33 | 0.21 | 0.06 | 0.12 | 0.00 | 0.02 | 0.13 | 0.00 | 0.00 | 0.51 |
| XAGUSD | 28113 | 0.30 | 0.18 | 0.06 | 0.12 | 0.00 | 0.02 | 0.12 | 0.00 | 0.00 | 0.59 |
| XPTUSD | 3482 | 0.47 | 0.35 | 0.08 | 0.14 | 0.00 | 0.02 | 0.18 | 0.00 | 0.00 | 0.59 |
| US30 | 25398 | 0.35 | 0.23 | 0.06 | 0.12 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.60 |
| USTEC | 23547 | 0.36 | 0.24 | 0.06 | 0.13 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.59 |
| XTIUSD | 25685 | 0.29 | 0.09 | 0.04 | 0.12 | 0.10 | 0.02 | 0.03 | 0.00 | 0.01 | 0.57 |
| XBRUSD | 18696 | 0.32 | 0.11 | 0.04 | 0.12 | 0.12 | 0.03 | 0.04 | 0.00 | 0.01 | 0.61 |
| XNGUSD | 14154 | 0.31 | 0.11 | 0.04 | 0.12 | 0.12 | 0.01 | 0.03 | 0.01 | 0.00 | 0.43 |
| ALL | 238041 | 0.35 | 0.22 | 0.06 | 0.12 | 0.03 | 0.09 | 0.09 | 0.00 | 0.00 | 0.60 |

Shares overlap (a detection can sit in several windows); "any" includes E10.

set W10 k16: raw 3074, calendar share 0.57, any exclusion 0.76
set W60 k6: raw 96124, calendar share 0.29, any exclusion 0.54

### Mechanism labels (share of allowed events), by class, all sets pooled
| class | n | CO | SINGLE | OTHER | spike (next tick takes back >= 50 %) | median spread at detection / trailing median |
|---|---|---|---|---|---|---|
| FX | 20848 | 0.70 | 0.24 | 0.06 | 0.004 | 1.00 |
| METALS | 28713 | 0.78 | 0.16 | 0.07 | 0.004 | 1.00 |
| INDICES | 20291 | 0.86 | 0.07 | 0.07 | 0.002 | 1.09 |
| ENERGY | 27266 | 0.60 | 0.24 | 0.16 | 0.049 | 1.21 |

### Spread paid (bp, half at entry + half at exit, h = 5 min) by latency and class, IS / VAL; trailing median spread for reference
| class | median spread (trailing) | L0 | L250 | L1000 | next | L60s |
|---|---|---|---|---|---|---|
| FX | 0.66 / 0.53 | 0.67 / 0.80 | 0.69 / 0.80 | 0.69 / 0.82 | 0.69 / 0.81 | 0.69 / 0.78 |
| METALS | 3.02 / 2.78 | 3.47 / 3.16 | 3.35 / 3.16 | 3.34 / 3.21 | 3.34 / 3.16 | 3.23 / 3.04 |
| INDICES | 1.62 / 0.74 | 1.79 / 0.76 | 1.77 / 0.76 | 1.76 / 0.76 | 1.77 / 0.76 | 1.72 / 0.75 |
| ENERGY | 10.39 / 8.50 | 23.07 / 9.63 | 18.92 / 9.49 | 18.73 / 9.49 | 18.75 / 9.52 | 16.65 / 9.17 |

E10 (count-based clock filter) share of all raw detections: AUDUSD 0.18, NZDUSD 0.18, XAUUSD 0.13, XAGUSD 0.24, XPTUSD 0.03, US30 0.16, USTEC 0.12, XTIUSD 0.29, XBRUSD 0.28, XNGUSD 0.11; all 0.19. The calendar (E1-E5) removes 35 % of raw detections (57 % of the largest, W10 k16), all exclusions together 60 % (76 % of W10 k16): the biggest jumps are mostly scheduled.

## 2. Results (D2, decision latency L 250 ms; mid and net in bp per event, day-clustered t; RT = share of 200 random-time seeds beaten; the t of the other latencies is in out/cells_D2.npy)

### Primary cells, D2, no stop (the stop variant is worse than no stop in 48 of 54 primary pairs in IS and 50 in VAL, 2,504 of 3,696 pairs overall; full grid in out/cells_D2.npy)

**J1 on CO, LIQUID set, all sessions**

| cell | n IS / VAL | mid IS / VAL (t) | net L0 | **net L250 IS (t) / VAL (t)** | net L1000 | net next tick | net +1 min | net x1.5 | VAL/IS | power IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W10 k6 h1 | 3313 / 1007 | -0.68 (-4.14) / -0.75 (-2.06) | -2.03 / -1.70 | **-2.27 (-13.68) / -1.75 (-4.75)** | -2.23 / -1.57 | -2.22 / -1.75 | -1.26 / -0.86 | -2.87 / -2.10 | nan | -8.99 / -5.56 | +0.00 / +0.00 | fail |
| W10 k6 h5 | 3313 / 1007 | -0.21 (-0.87) / -0.88 (-2.23) | -1.57 / -1.82 | **-1.79 (-7.30) / -1.86 (-4.67)** | -1.75 / -1.70 | -1.76 / -1.87 | -0.96 / -0.93 | -2.39 / -2.21 | nan | -4.97 / -4.74 | +0.00 / +0.00 | fail |
| W10 k6 h15 | 3313 / 1007 | +0.26 (+0.74) / -0.35 (-0.70) | -1.08 / -1.27 | **-1.32 (-3.80) / -1.32 (-2.65)** | -1.28 / -1.19 | -1.28 / -1.33 | -0.61 / -0.46 | -1.91 / -1.67 | nan | -2.67 / -2.62 | +0.82 / +0.07 | fail |
| W10 k10 h1 | 751 / 176 | -1.39 (-3.02) / -2.67 (-2.14) | -2.83 / -3.91 | **-3.15 (-6.72) / -3.95 (-3.12)** | -2.89 / -3.36 | -3.06 / -3.97 | -1.69 / -1.24 | -3.84 / -4.46 | nan | -4.26 / -3.15 | +0.00 / +0.00 | fail |
| W10 k10 h5 | 751 / 176 | -1.34 (-2.20) / -2.84 (-2.55) | -2.75 / -4.14 | **-3.08 (-4.99) / -4.09 (-3.60)** | -2.88 / -3.50 | -2.99 / -4.14 | -1.45 / -0.98 | -3.76 / -4.59 | nan | -3.31 / -3.34 | +0.00 / +0.00 | fail |
| W10 k10 h15 | 751 / 176 | -1.17 (-1.57) / -3.07 (-2.57) | -2.57 / -4.30 | **-2.90 (-3.84) / -4.31 (-3.55)** | -2.72 / -3.69 | -2.82 / -4.33 | -1.58 / -1.54 | -3.58 / -4.80 | nan | -2.43 / -3.19 | +0.00 / +0.00 | fail |
| W10 k16 h1 | 165 / 28 | -4.33 (-3.18) / -6.53 (-2.72) | -5.34 / -8.45 | **-6.47 (-4.38) / -8.28 (-3.34)** | -7.16 / -8.24 | -6.13 / -8.75 | -2.77 / -1.55 | -7.34 / -8.99 | nan | -2.67 / -2.80 | +0.00 / +0.00 | fail |
| W10 k16 h5 | 165 / 28 | -5.49 (-2.81) / -7.50 (-2.77) | -6.42 / -9.14 | **-7.61 (-3.70) / -9.09 (-3.30)** | -8.24 / -8.95 | -7.27 / -9.66 | -3.00 / -1.56 | -8.47 / -9.72 | nan | -2.41 / -2.71 | +0.00 / +0.00 | fail |
| W10 k16 h15 | 165 / 28 | -7.09 (-2.29) / -8.70 (-3.83) | -8.00 / -10.34 | **-9.19 (-2.86) / -10.28 (-4.52)** | -9.85 / -10.08 | -8.86 / -10.82 | -4.51 / -3.13 | -10.04 / -10.91 | nan | -2.07 / -3.46 | +0.00 / +0.00 | fail |
| W30 k6 h1 | 7884 / 2538 | -0.32 (-3.55) / -0.52 (-2.79) | -1.65 / -1.42 | **-1.83 (-19.75) / -1.49 (-7.96)** | -1.81 / -1.42 | -1.80 / -1.49 | -1.34 / -0.98 | -2.40 / -1.83 | nan | -13.57 / -8.89 | +0.00 / +0.00 | fail |
| W30 k6 h5 | 7884 / 2538 | -0.14 (-1.08) / -0.53 (-2.38) | -1.46 / -1.43 | **-1.64 (-12.54) / -1.49 (-6.58)** | -1.62 / -1.41 | -1.62 / -1.49 | -1.27 / -0.89 | -2.20 / -1.82 | nan | -8.38 / -6.36 | +0.00 / +0.00 | fail |
| W30 k6 h15 | 7884 / 2538 | +0.09 (+0.48) / -0.33 (-1.03) | -1.23 / -1.21 | **-1.41 (-7.77) / -1.28 (-4.05)** | -1.39 / -1.24 | -1.39 / -1.29 | -1.02 / -0.63 | -1.97 / -1.61 | nan | -5.16 / -3.98 | +0.47 / +0.01 | fail |
| W30 k10 h1 | 1573 / 430 | -0.67 (-2.43) / -1.63 (-2.13) | -2.13 / -2.66 | **-2.32 (-8.24) / -2.71 (-3.53)** | -2.27 / -2.56 | -2.28 / -2.70 | -1.54 / -1.10 | -2.95 / -3.12 | nan | -5.25 / -4.14 | +0.00 / +0.00 | fail |
| W30 k10 h5 | 1573 / 430 | -0.31 (-0.74) / -2.12 (-2.61) | -1.76 / -3.17 | **-1.94 (-4.60) / -3.18 (-3.90)** | -1.91 / -3.02 | -1.91 / -3.16 | -1.03 / -1.27 | -2.57 / -3.57 | nan | -3.14 / -4.10 | +0.00 / +0.00 | fail |
| W30 k10 h15 | 1573 / 430 | +0.35 (+0.59) / -1.41 (-1.36) | -1.09 / -2.46 | **-1.27 (-2.15) / -2.47 (-2.37)** | -1.23 / -2.32 | -1.24 / -2.44 | -0.59 / -0.66 | -1.89 / -2.85 | nan | -1.52 / -2.57 | +0.80 / +0.00 | fail |
| W30 k16 h1 | 328 / 71 | -1.27 (-1.63) / -3.45 (-1.61) | -2.60 / -4.60 | **-3.08 (-3.91) / -4.80 (-2.21)** | -3.10 / -4.77 | -2.89 / -4.97 | -2.12 / -2.83 | -3.79 / -5.33 | nan | -2.27 / -2.11 | +0.00 / +0.00 | fail |
| W30 k16 h5 | 328 / 71 | -1.63 (-1.41) / -6.00 (-2.70) | -2.90 / -7.13 | **-3.41 (-2.90) / -7.28 (-3.27)** | -3.47 / -7.16 | -3.23 / -7.53 | -1.72 / -2.59 | -4.10 / -7.77 | nan | -1.91 / -2.99 | +0.00 / +0.00 | fail |
| W30 k16 h15 | 328 / 71 | -2.04 (-1.37) / -6.26 (-2.66) | -3.29 / -7.39 | **-3.80 (-2.50) / -7.55 (-3.21)** | -3.88 / -7.42 | -3.61 / -7.72 | -2.56 / -3.75 | -4.49 / -8.04 | nan | -1.73 / -2.85 | +0.00 / +0.00 | fail |
| W60 k6 h1 | 16070 / 5847 | -0.12 (-2.38) / -0.28 (-3.03) | -1.45 / -1.15 | **-1.59 (-29.88) / -1.22 (-12.81)** | -1.58 / -1.20 | -1.57 / -1.22 | -1.42 / -0.89 | -2.13 / -1.53 | nan | -20.20 / -13.46 | +0.00 / +0.00 | fail |
| W60 k6 h5 | 16070 / 5847 | -0.00 (-0.06) / -0.30 (-2.31) | -1.33 / -1.15 | **-1.47 (-17.64) / -1.22 (-9.44)** | -1.46 / -1.19 | -1.45 / -1.22 | -1.30 / -0.97 | -2.00 / -1.52 | nan | -11.62 / -8.80 | +0.08 / +0.00 | fail |
| W60 k6 h15 | 16070 / 5847 | +0.14 (+1.19) / -0.07 (-0.35) | -1.18 / -0.92 | **-1.32 (-11.24) / -0.99 (-5.11)** | -1.31 / -0.97 | -1.31 / -0.98 | -1.17 / -0.64 | -1.86 / -1.29 | nan | -7.21 / -4.98 | +0.91 / +0.08 | fail |
| W60 k10 h1 | 2570 / 735 | -0.36 (-1.70) / -1.04 (-2.13) | -1.78 / -2.00 | **-1.97 (-9.21) / -2.07 (-4.20)** | -1.88 / -2.04 | -1.92 / -2.06 | -1.46 / -0.91 | -2.59 / -2.44 | nan | -6.18 / -4.91 | +0.00 / +0.00 | fail |
| W60 k10 h5 | 2570 / 735 | -0.09 (-0.29) / -1.32 (-2.32) | -1.49 / -2.27 | **-1.69 (-5.34) / -2.33 (-4.08)** | -1.62 / -2.25 | -1.65 / -2.32 | -1.22 / -1.24 | -2.30 / -2.69 | nan | -3.67 / -4.29 | +0.01 / +0.00 | fail |
| W60 k10 h15 | 2570 / 735 | +0.44 (+1.00) / -1.15 (-1.61) | -0.95 / -2.10 | **-1.15 (-2.62) / -2.16 (-3.03)** | -1.08 / -2.09 | -1.12 / -2.14 | -0.81 / -0.89 | -1.76 / -2.52 | nan | -1.72 / -3.21 | +0.94 / +0.00 | fail |
| W60 k16 h1 | 489 / 132 | -0.47 (-0.72) / -2.97 (-2.27) | -1.72 / -4.07 | **-2.18 (-3.27) / -4.11 (-3.12)** | -2.19 / -4.00 | -2.00 / -4.23 | -1.46 / -3.20 | -2.85 / -4.54 | nan | -2.14 / -3.31 | +0.00 / +0.00 | fail |
| W60 k16 h5 | 489 / 132 | +0.38 (+0.35) / -5.68 (-2.96) | -0.88 / -6.80 | **-1.33 (-1.20) / -6.78 (-3.54)** | -1.36 / -6.58 | -1.17 / -6.92 | -0.47 / -3.29 | -2.00 / -7.19 | nan | -0.88 / -4.12 | +0.66 / +0.00 | fail |
| W60 k16 h15 | 489 / 132 | +1.72 (+1.21) / -3.92 (-2.06) | +0.50 / -5.10 | **+0.04 (+0.02) / -5.02 (-2.65)** | +0.00 / -4.78 | +0.20 / -5.14 | +0.49 / -1.93 | -0.62 / -5.42 | -140.77 | +0.02 / -2.75 | +1.00 / +0.00 | fail |

**J2 on SINGLE, LIQUID set, all sessions**

| cell | n IS / VAL | mid IS / VAL (t) | net L0 | **net L250 IS (t) / VAL (t)** | net L1000 | net next tick | net +1 min | net x1.5 | VAL/IS | power IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W10 k6 h1 | 999 / 225 | +0.94 (+5.88) / +1.17 (+2.11) | -1.03 / -0.78 | **-0.98 (-5.76) / -0.95 (-1.35)** | -1.03 / -0.90 | -1.01 / -1.02 | -1.89 / -1.78 | -1.67 / -1.79 | nan | -3.44 / -1.15 | +1.00 / +0.99 | fail |
| W10 k6 h5 | 999 / 225 | +0.83 (+3.92) / +1.42 (+2.22) | -1.11 / -0.34 | **-1.06 (-4.83) / -0.50 (-0.75)** | -1.11 / -0.49 | -1.08 / -0.56 | -1.82 / -2.05 | -1.73 / -1.24 | nan | -2.91 / -0.58 | +1.00 / +1.00 | fail |
| W10 k6 h15 | 999 / 225 | +0.92 (+3.62) / +1.16 (+1.75) | -1.03 / -0.61 | **-0.98 (-3.79) / -0.78 (-1.15)** | -1.03 / -0.69 | -1.01 / -0.85 | -1.83 / -1.99 | -1.65 / -1.54 | nan | -2.12 / -0.86 | +1.00 / +0.97 | fail |
| W10 k10 h1 | 140 / 51 | +2.43 (+4.96) / +3.47 (+1.61) | -0.15 / +1.02 | **-0.37 (-0.65) / +0.44 (+0.18)** | -0.52 / +0.26 | -0.38 / +0.25 | -2.84 / -2.62 | -1.49 / -0.85 | nan | -0.36 / +0.15 | +1.00 / +1.00 | fail |
| W10 k10 h5 | 140 / 51 | +1.90 (+3.86) / +4.51 (+2.16) | -0.61 / +2.38 | **-0.84 (-1.57) / +2.12 (+0.91)** | -0.96 / +1.91 | -0.84 / +1.60 | -3.21 / -2.53 | -1.94 / +1.15 | nan | -0.88 / +0.85 | +1.00 / +1.00 | fail |
| W10 k10 h15 | 140 / 51 | +1.80 (+2.83) / +4.92 (+3.06) | -0.69 / +2.27 | **-0.93 (-1.37) / +2.02 (+1.07)** | -1.05 / +1.81 | -0.91 / +1.58 | -3.05 / -1.57 | -2.02 / +0.80 | nan | -0.79 / +1.02 | +0.99 / +1.00 | fail |
| W10 k16 h1 | 46 / 13 | +3.49 (+2.53) / +3.08 (+1.61) | +0.77 / -3.04 | **-0.12 (-0.08) / -1.62 (-0.85)** | +0.04 / -3.24 | -0.04 / -2.15 | -2.53 / -3.21 | -1.64 / -3.74 | nan | -0.04 / -0.61 | +1.00 / +0.75 | fail |
| W10 k16 h5 | 46 / 13 | +3.04 (+2.31) / +8.87 (+1.51) | +0.37 / +3.90 | **-0.46 (-0.33) / +5.39 (+0.91)** | -0.24 / +2.47 | -0.40 / +4.87 | -3.45 / -0.40 | -1.94 / +3.88 | nan | -0.18 / +0.91 | +1.00 / +1.00 | fail |
| W10 k16 h15 | 46 / 13 | +2.81 (+1.96) / +11.58 (+1.33) | +0.19 / +6.11 | **-0.63 (-0.43) / +7.50 (+0.85)** | -0.41 / +5.69 | -0.55 / +6.99 | -3.58 / +3.82 | -2.07 / +5.70 | nan | -0.23 / +0.75 | +0.98 / +1.00 | fail |
| W30 k6 h1 | 1877 / 414 | +0.66 (+6.74) / +0.73 (+2.10) | -1.09 / -0.74 | **-1.06 (-10.23) / -0.88 (-2.12)** | -1.10 / -0.82 | -1.07 / -0.93 | -1.57 / -1.20 | -1.66 / -1.47 | nan | -5.83 / -1.87 | +1.00 / +1.00 | fail |
| W30 k6 h5 | 1877 / 414 | +0.91 (+6.38) / +1.56 (+3.81) | -0.85 / +0.18 | **-0.81 (-6.01) / +0.04 (+0.09)** | -0.85 / +0.09 | -0.82 / +0.01 | -1.39 / -0.76 | -1.41 / -0.50 | nan | -3.17 / +0.08 | +1.00 / +1.00 | fail |
| W30 k6 h15 | 1877 / 414 | +1.06 (+5.87) / +1.20 (+2.59) | -0.68 / -0.17 | **-0.65 (-3.69) / -0.34 (-0.68)** | -0.69 / -0.22 | -0.66 / -0.39 | -1.23 / -1.04 | -1.25 / -0.90 | nan | -1.91 / -0.57 | +1.00 / +1.00 | fail |
| W30 k10 h1 | 223 / 73 | +1.74 (+4.39) / +2.57 (+1.73) | -0.60 / +0.24 | **-0.76 (-1.75) / -0.47 (-0.27)** | -0.87 / -0.43 | -0.75 / -0.53 | -2.46 / -2.34 | -1.75 / -1.76 | nan | -0.92 / -0.23 | +1.00 / +1.00 | fail |
| W30 k10 h5 | 223 / 73 | +1.50 (+3.26) / +3.45 (+2.29) | -0.74 / +1.38 | **-0.90 (-1.89) / +0.92 (+0.55)** | -0.92 / +0.92 | -0.88 / +0.59 | -2.53 / -2.53 | -1.84 / -0.12 | nan | -0.99 / +0.48 | +1.00 / +1.00 | fail |
| W30 k10 h15 | 223 / 73 | +1.01 (+1.69) / +3.06 (+2.41) | -1.22 / +0.63 | **-1.38 (-2.17) / +0.20 (+0.15)** | -1.42 / +0.19 | -1.35 / -0.07 | -3.05 / -2.21 | -2.32 / -1.00 | nan | -1.18 / +0.12 | +0.88 / +1.00 | fail |
| W30 k16 h1 | 56 / 19 | +3.41 (+3.10) / +1.98 (+0.71) | +0.71 / -3.28 | **-0.25 (-0.19) / -2.22 (-0.78)** | -0.22 / -3.00 | -0.17 / -2.45 | -3.12 / -1.28 | -1.81 / -4.12 | nan | -0.11 / -0.60 | +1.00 / +0.38 | fail |
| W30 k16 h5 | 56 / 19 | +3.19 (+3.18) / +6.13 (+1.76) | +0.42 / +1.78 | **-0.37 (-0.33) / +2.72 (+0.72)** | -0.22 / +1.18 | -0.30 / +2.46 | -3.07 / -1.45 | -1.87 / +1.22 | nan | -0.18 / +0.79 | +1.00 / +1.00 | fail |
| W30 k16 h15 | 56 / 19 | +2.12 (+1.71) / +5.90 (+2.05) | -0.64 / +1.14 | **-1.42 (-1.11) / +2.11 (+0.64)** | -1.30 / +1.43 | -1.33 / +2.01 | -4.57 / -0.53 | -2.92 / +0.42 | nan | -0.61 / +0.64 | +0.85 / +1.00 | fail |
| W60 k6 h1 | 3070 / 731 | +0.61 (+8.63) / +0.33 (+1.99) | -1.07 / -0.97 | **-1.01 (-14.02) / -1.04 (-5.29)** | -1.06 / -1.00 | -1.01 / -1.08 | -1.51 / -1.09 | -1.56 / -1.52 | nan | -7.81 / -4.49 | +1.00 / +0.81 | fail |
| W60 k6 h5 | 3070 / 731 | +0.76 (+6.89) / +0.85 (+3.32) | -0.91 / -0.41 | **-0.85 (-8.17) / -0.48 (-1.69)** | -0.90 / -0.45 | -0.85 / -0.50 | -1.44 / -0.84 | -1.40 / -0.94 | nan | -4.29 / -1.36 | +1.00 / +1.00 | fail |
| W60 k6 h15 | 3070 / 731 | +0.91 (+6.37) / +0.81 (+2.24) | -0.75 / -0.45 | **-0.69 (-4.96) / -0.51 (-1.32)** | -0.75 / -0.47 | -0.69 / -0.54 | -1.26 / -0.84 | -1.24 / -0.96 | nan | -2.61 / -1.06 | +1.00 / +0.99 | fail |
| W60 k10 h1 | 321 / 103 | +1.44 (+4.50) / +2.35 (+2.21) | -0.72 / -0.20 | **-0.83 (-2.35) / -0.46 (-0.34)** | -0.94 / -0.64 | -0.82 / -0.51 | -2.14 / -2.29 | -1.70 / -1.63 | nan | -1.28 / -0.29 | +1.00 / +1.00 | fail |
| W60 k10 h5 | 321 / 103 | +1.22 (+2.92) / +2.96 (+2.61) | -0.87 / +0.69 | **-0.99 (-2.19) / +0.65 (+0.53)** | -1.06 / +0.42 | -0.97 / +0.39 | -2.20 / -2.25 | -1.83 / -0.29 | nan | -1.23 / +0.42 | +1.00 / +1.00 | fail |
| W60 k10 h15 | 321 / 103 | +1.64 (+3.30) / +2.71 (+2.74) | -0.43 / +0.20 | **-0.55 (-1.02) / +0.19 (+0.19)** | -0.62 / -0.04 | -0.53 / -0.03 | -1.92 / -2.09 | -1.38 / -0.84 | nan | -0.58 / +0.14 | +1.00 / +1.00 | fail |
| W60 k16 h1 | 73 / 23 | +2.85 (+3.02) / +1.80 (+0.72) | +0.19 / -2.43 | **-0.57 (-0.54) / -1.86 (-0.77)** | -0.69 / -2.29 | -0.50 / -2.01 | -3.04 / -1.51 | -2.02 / -3.49 | nan | -0.31 / -0.58 | +1.00 / +0.47 | fail |
| W60 k16 h5 | 73 / 23 | +3.10 (+3.82) / +4.22 (+1.36) | +0.41 / +0.73 | **-0.22 (-0.25) / +1.22 (+0.37)** | -0.20 / +0.12 | -0.16 / +1.00 | -2.64 / -1.81 | -1.61 / -0.08 | nan | -0.14 / +0.39 | +1.00 / +1.00 | fail |
| W60 k16 h15 | 73 / 23 | +1.93 (+1.88) / +4.42 (+1.67) | -0.74 / +0.63 | **-1.38 (-1.30) / +1.11 (+0.38)** | -1.37 / +0.72 | -1.29 / +1.02 | -3.86 / -1.15 | -2.76 / -0.36 | nan | -0.71 / +0.39 | +0.85 / +1.00 | fail |

### The cells that meet the DEMO numbers (D2 primary definition; D1 versions below), and other notable cells

| cell | n IS / VAL | mid IS / VAL (t) | net L0 | **net L250 IS (t) / VAL (t)** | net L1000 | net next tick | net +1 min | net x1.5 | VAL/IS | power IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D2 J2 10 16 15 none CO METALS Asia | 46 / 7 | +17.87 (+3.70) / +30.50 (+3.61) | +15.05 / +17.13 | **+12.15 (+2.60) / +18.49 (+2.17)** | +14.05 / +13.40 | +12.29 / +18.05 | +16.61 / +5.88 | +9.59 / +12.79 | +1.52 | +1.40 / +1.65 | +1.00 / +1.00 | DEMO numbers, within chance |
| D2 J2 10 16 15 none CO METALS ALL | 116 / 11 | +14.74 (+3.25) / +23.97 (+3.85) | +9.20 / +14.87 | **+9.98 (+2.37) / +13.80 (+2.18)** | +11.49 / +13.03 | +9.04 / +15.55 | +5.82 / +1.81 | +7.91 / +9.01 | +1.38 | +1.33 / +1.65 | +1.00 / +1.00 | DEMO numbers, within chance |
| D2 J2 30 16 15 none CO METALS Asia | 73 / 11 | +14.56 (+3.66) / +25.48 (+3.28) | +8.23 / +13.61 | **+9.05 (+2.35) / +16.98 (+2.21)** | +9.54 / +13.48 | +9.32 / +16.79 | +10.37 / +3.63 | +6.59 / +13.03 | +1.88 | +1.28 / +1.68 | +1.00 / +1.00 | DEMO numbers, within chance |
| D2 J2 10 16 15 stop CO METALS Asia | 46 / 7 | +17.87 (+3.70) / +30.50 (+3.61) | +5.20 / +0.16 | **+5.01 (+0.75) / +1.54 (+0.07)** | +6.26 / +13.40 | +4.23 / +1.10 | +14.44 / +5.88 | +2.45 / -4.16 | +0.31 | +0.40 / +0.05 | +1.00 / +0.96 | fail |
| D2 J2 60 16 15 none CO METALS Asia | 110 / 19 | +4.58 (+1.18) / +9.41 (+2.46) | +0.10 / +2.41 | **-1.16 (-0.30) / +2.12 (+0.50)** | -0.73 / +0.31 | -0.89 / +2.14 | +1.63 / -2.98 | -3.74 / -1.23 | nan | -0.16 / +0.42 | +0.98 / +0.98 | fail |
| D2 J2 10 16 15 none CO LIQUID Asia | 74 / 16 | +11.25 (+1.76) / +7.78 (+2.61) | +7.72 / +6.27 | **+8.98 (+1.46) / +6.35 (+2.09)** | +9.69 / +5.39 | +8.52 / +6.78 | +2.55 / -0.02 | +8.05 / +5.80 | +0.71 | +1.10 / +1.67 | +1.00 / +1.00 | fail |
| D2 J1 60 16 15 stop CO INDICES ALL | 184 / 69 | +7.32 (+2.57) / -2.85 (-1.13) | +6.13 / -4.19 | **+5.78 (+2.08) / -4.46 (-1.76)** | +5.62 / -4.29 | +5.83 / -4.44 | +3.38 / -2.10 | +4.84 / -4.85 | -0.77 | +1.46 / -1.65 | +1.00 / +0.01 | fail |
| D2 J1 30 10 15 none CO INDICES ALL | 600 / 225 | +3.06 (+2.67) / -0.46 (-0.34) | +1.40 / -1.28 | **+1.21 (+1.06) / -1.28 (-0.94)** | +1.15 / -1.13 | +1.23 / -1.28 | +0.51 / +0.45 | +0.29 / -1.69 | -1.06 | +0.73 / -0.89 | +1.00 / +0.19 | fail |
| D2 J2 10 16 15 none SINGLE ENERGY ALL | 195 / 19 | +20.23 (+6.33) / +19.24 (+1.30) | -38.45 / -26.48 | **-39.89 (-7.74) / -22.45 (-1.55)** | -40.20 / -22.91 | -38.67 / -21.38 | -39.71 / -34.90 | -69.94 / -43.30 | nan | -5.67 / -1.18 | +0.00 / +0.88 | fail |
| D2 J2 60 16 15 none SINGLE ENERGY ALL | 242 / 40 | +17.20 (+6.30) / +21.10 (+2.77) | -34.67 / -19.68 | **-36.14 (-8.28) / -18.93 (-2.37)** | -35.84 / -18.25 | -34.96 / -18.30 | -35.07 / -23.33 | -62.81 / -38.95 | nan | -6.08 / -1.84 | +0.00 / +0.99 | fail |
| D2 J2 60 6 1 none SINGLE FX ALL | 1857 / 301 | +0.53 (+6.30) / +0.38 (+2.18) | -1.05 / -1.50 | **-0.97 (-12.78) / -1.64 (-6.74)** | -1.02 / -1.61 | -0.97 / -1.73 | -1.51 / -1.84 | -1.41 / -2.36 | nan | -7.04 / -5.78 | +1.00 / +0.17 | fail |
| D2 J2 10 10 15 none SINGLE METALS ALL | 80 / 5 | +24.31 (+2.19) / +12.18 (+1.48) | +14.78 / -12.13 | **+13.47 (+1.31) / -6.47 (-0.47)** | +13.85 / -6.94 | +13.99 / -6.56 | +3.50 / -10.13 | +8.36 / -15.49 | -0.48 | +0.71 / -0.36 | +1.00 / +0.71 | fail |
| D1 J2 10 16 15 none CO METALS Asia | 61 / 11 | +17.57 (+4.05) / +24.09 (+3.87) | +14.74 / +13.55 | **+12.38 (+2.95) / +14.97 (+2.52)** | +13.38 / +12.32 | +12.69 / +14.51 | +14.34 / +4.56 | +10.09 / +10.71 | +1.21 | +1.61 / +1.91 | +1.00 / +1.00 | DEMO |
| D1 J2 10 16 15 none CO METALS ALL | 136 / 16 | +14.42 (+3.54) / +24.12 (+4.34) | +9.08 / +15.94 | **+9.76 (+2.55) / +15.72 (+2.79)** | +11.37 / +14.85 | +9.08 / +16.79 | +5.33 / +5.17 | +7.73 / +11.82 | +1.61 | +1.44 / +2.12 | +1.00 / +1.00 | DEMO numbers, within chance |
| D1 J2 30 16 15 none CO METALS Asia | 115 / 27 | +12.04 (+3.91) / +13.79 (+2.86) | +6.62 / +6.02 | **+7.22 (+2.41) / +8.02 (+1.72)** | +7.07 / +6.71 | +7.41 / +7.78 | +6.65 / -1.43 | +5.11 / +5.43 | +1.11 | +1.31 / +1.20 | +1.00 / +1.00 | fail |

### By year, net bp at L250 (D2)

| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | years > 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| J2 10 16 15 none CO METALS Asia | +9.0 | +7.5 | +2.1 | +5.0 | +26.6 | +61.8 | -9.7 | +23.5 | +39.1 | 8/9 |
| J2 10 16 15 none CO METALS ALL | +10.0 | +2.7 | +17.6 | +7.2 | +28.4 | +16.0 | +2.0 | +10.5 | +31.1 | 9/9 |
| J2 30 16 15 none CO METALS Asia | +6.2 | +7.2 | -8.3 | +4.3 | +12.4 | +53.8 | +6.7 | +23.5 | +22.4 | 8/9 |
| J1 60 16 15 stop CO INDICES ALL | -3.4 | -2.1 | +11.5 | +4.9 | +14.2 | +2.2 | -0.9 | -3.4 | -8.4 | 4/9 |
| J2 60 6 1 none SINGLE LIQUID ALL | -1.2 | -1.0 | -0.8 | -1.1 | -0.8 | -0.9 | -0.8 | -1.4 | -0.9 | 0/9 |
| J2 10 16 1 none SINGLE LIQUID ALL | +2.9 | +2.0 | +3.2 | -1.8 | -4.7 | -1.8 | +1.6 | -3.3 | +0.1 | 5/9 |


## 3. Co-move vs single-instrument split (D2, J1-oriented mid at L 250: positive = continuation, negative = reversal; bp (t) n)

| class | set | h | CO IS | CO VAL | SINGLE IS | SINGLE VAL | OTHER IS | OTHER VAL |
|---|---|---|---|---|---|---|---|---|
| FX | W10 k16 | 1 | -7.98 (-1.8) n41 | -1.02 (-0.3) n8 | -3.04 (-2.0) n39 | -2.17 (-1.1) n10 | -1.70 (-0.7) n4 | nan |
| FX | W10 k16 | 15 | -16.35 (-1.5) n41 | -6.68 (-3.1) n8 | -3.03 (-2.0) n39 | -3.43 (-1.2) n10 | -3.55 (-1.3) n4 | nan |
| FX | W30 k10 | 1 | -0.41 (-1.2) n478 | -0.19 (-0.2) n116 | -1.38 (-2.8) n154 | -2.05 (-2.9) n49 | -1.67 (-1.2) n30 | -3.86 (-1.0) n4 |
| FX | W30 k10 | 15 | -0.02 (-0.0) n478 | -1.78 (-1.3) n116 | -1.02 (-1.4) n154 | -3.62 (-3.2) n49 | -4.92 (-3.2) n30 | -6.52 (-1.9) n4 |
| FX | W60 k6 | 1 | -0.23 (-3.5) n5927 | -0.16 (-1.2) n1808 | -0.53 (-6.3) n1857 | -0.38 (-2.2) n301 | +0.06 (+0.3) n545 | +0.14 (+0.5) n95 |
| FX | W60 k6 | 15 | -0.14 (-1.1) n5927 | -0.45 (-1.8) n1808 | -0.80 (-5.3) n1857 | -1.18 (-3.8) n301 | -0.17 (-0.5) n545 | -0.89 (-1.3) n95 |
| METALS | W10 k16 | 1 | -4.23 (-0.7) n116 | -14.22 (-4.5) n11 | -74.62 (-1.1) n10 | -4.22 (-1.3) n2 | -4.32 (-0.6) n7 | nan |
| METALS | W10 k16 | 15 | -14.74 (-3.3) n116 | -23.97 (-3.8) n11 | -72.39 (-1.2) n10 | -2.67 (-0.3) n2 | -8.28 (-1.1) n7 | nan |
| METALS | W30 k10 | 1 | -1.93 (-1.7) n870 | -2.36 (-2.2) n146 | -7.23 (-1.3) n129 | -1.84 (-1.2) n14 | +4.07 (+0.5) n63 | -7.85 (-2.1) n8 |
| METALS | W30 k10 | 15 | -2.55 (-1.9) n870 | -3.00 (-1.9) n146 | -17.43 (-2.7) n129 | -6.06 (-1.7) n14 | -2.32 (-0.9) n63 | -13.70 (-1.9) n8 |
| METALS | W60 k6 | 1 | -0.19 (-1.1) n8360 | -0.58 (-3.2) n2357 | -1.49 (-3.3) n1687 | -0.95 (-2.5) n414 | -1.26 (-3.5) n658 | -0.51 (-0.8) n212 |
| METALS | W60 k6 | 15 | -0.77 (-2.8) n8360 | -0.71 (-1.8) n2357 | -2.59 (-4.3) n1687 | -2.42 (-2.9) n414 | -2.05 (-2.8) n658 | -2.03 (-1.5) n212 |
| INDICES | W10 k16 | 1 | -0.36 (-0.2) n54 | -6.12 (-1.7) n13 | +0.60 (+0.3) n3 | -6.13 (-1.3) n3 | -1.91 (-1.7) n4 | nan |
| INDICES | W10 k16 | 15 | -0.80 (-0.2) n54 | -6.48 (-1.9) n13 | -1.04 (-0.3) n3 | -38.74 (-1.3) n3 | -6.79 (-2.5) n4 | nan |
| INDICES | W30 k10 | 1 | +0.58 (+1.3) n600 | -1.74 (-1.8) n225 | -2.43 (-1.9) n28 | -4.45 (-0.8) n18 | -2.26 (-1.8) n23 | -4.42 (-1.6) n26 |
| INDICES | W30 k10 | 15 | +3.06 (+2.7) n600 | -0.46 (-0.3) n225 | -1.75 (-0.9) n28 | -2.00 (-0.5) n18 | -5.47 (-2.5) n23 | -8.06 (-1.6) n26 |
| INDICES | W60 k6 | 1 | +0.15 (+1.5) n5812 | -0.26 (-2.0) n2786 | -0.48 (-2.5) n473 | +0.15 (+0.4) n225 | -0.40 (-1.6) n395 | -0.30 (-0.6) n245 |
| INDICES | W60 k6 | 15 | +0.95 (+3.8) n5812 | +0.36 (+1.2) n2786 | -0.65 (-1.3) n473 | +0.34 (+0.4) n225 | -0.53 (-0.8) n395 | +0.25 (+0.3) n245 |
| ENERGY | W10 k16 | 1 | -16.22 (-3.3) n54 | -3.10 (-0.5) n21 | -12.19 (-5.5) n195 | -14.59 (-1.6) n19 | -12.54 (-5.6) n99 | +8.58 (+0.5) n8 |
| ENERGY | W10 k16 | 15 | -10.81 (-1.1) n54 | +12.08 (+1.6) n21 | -20.23 (-6.3) n195 | -19.24 (-1.3) n19 | -22.80 (-6.5) n99 | -3.33 (-0.1) n8 |
| ENERGY | W30 k10 | 1 | -3.54 (-2.7) n456 | +0.34 (+0.1) n194 | -7.87 (-6.2) n427 | -0.93 (-0.2) n94 | -9.77 (-6.8) n239 | -2.28 (-0.3) n66 |
| ENERGY | W30 k10 | 15 | +0.70 (+0.2) n456 | +8.13 (+1.6) n194 | -12.24 (-5.8) n427 | -14.43 (-1.9) n94 | -14.27 (-5.2) n239 | -0.29 (-0.0) n66 |
| ENERGY | W60 k6 | 1 | -0.26 (-1.2) n4934 | -0.11 (-0.4) n3320 | -3.69 (-6.5) n1550 | +0.48 (+0.3) n582 | -3.15 (-5.2) n1018 | +0.30 (+0.2) n470 |
| ENERGY | W60 k6 | 15 | +0.65 (+1.0) n4934 | +0.29 (+0.4) n3320 | -3.68 (-2.9) n1550 | +1.46 (+0.5) n582 | -3.25 (-2.1) n1018 | -5.02 (-1.3) n470 |

Single-instrument jumps revert in every class and both eras; in the large-sample sets (k6, k10) they revert more than co-moving ones in all four classes (at k16 the samples are small and FX / metal co-moving jumps revert as much or more). Co-moving FX and metal jumps revert too; co-moving index jumps continue in IS (W60 k6 h15 +0.95, t 3.8; W30 k10 h15 +3.06, t 2.7) and not in VAL (+0.36 / -0.46). Co-moving energy jumps are flat or mixed in IS and positive but not significant in VAL. Energy single-instrument reversals are large at mid (-4 to -20 bp, t -3 to -6.5 in IS) but IC charges ~40-60 bp in those moments (XNG-dominated).

Label shares (all sets): CO 0.70 FX, 0.78 metals, 0.86 indices, 0.60 energies; SINGLE 0.24 / 0.16 / 0.07 / 0.24. The causal CO label is mostly mechanical same-group co-movement (AUD with NZD, gold with silver, US30 with USTEC, WTI with Brent), which is why it does not separate information from liquidity well.

### Information only: a panel label (EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD for USD-quoted jumps; US500 for index jumps), close of the minute before the detection minute to the close of the minute after it (looks up to ~2 min ahead)

| group | set | h | panel co-move IS | panel co-move VAL | no panel co-move IS | no panel co-move VAL |
|---|---|---|---|---|---|---|
| G_USD (>= 2 of 5 USD pairs) | W10 k16 | 1 | 3.63 (0.42) n78 | -7.43 (-1.65) n11 | -14.41 (-2.77) n139 | -5.40 (-2.58) n21 |
| G_USD (>= 2 of 5 USD pairs) | W10 k16 | 15 | -10.70 (-1.73) n78 | -13.15 (-2.25) n11 | -17.69 (-3.04) n139 | -10.34 (-2.56) n21 |
| G_USD (>= 2 of 5 USD pairs) | W30 k10 | 1 | 2.57 (2.02) n692 | -0.29 (-0.25) n158 | -4.44 (-4.51) n1032 | -2.93 (-3.79) n179 |
| G_USD (>= 2 of 5 USD pairs) | W30 k10 | 15 | -0.02 (-0.01) n692 | -1.41 (-0.95) n158 | -4.76 (-5.48) n1032 | -4.59 (-3.80) n179 |
| G_USD (>= 2 of 5 USD pairs) | W60 k6 | 1 | 1.09 (7.61) n6272 | 0.88 (4.90) n1962 | -1.10 (-10.89) n12762 | -1.23 (-9.92) n3225 |
| G_USD (>= 2 of 5 USD pairs) | W60 k6 | 15 | 1.37 (4.52) n6272 | 1.24 (3.25) n1962 | -1.81 (-12.17) n12762 | -2.11 (-7.50) n3225 |
| G_IDX (US500) | W10 k16 | 1 | -1.18 (-0.47) n36 | 0.56 (0.14) n8 | 0.68 (0.70) n25 | -10.19 (-3.03) n9 |
| G_IDX (US500) | W10 k16 | 15 | -3.84 (-0.97) n36 | -14.38 (-1.19) n8 | 2.59 (0.62) n25 | -11.33 (-3.04) n9 |
| G_IDX (US500) | W30 k10 | 1 | 1.85 (3.03) n415 | 0.12 (0.13) n197 | -2.29 (-5.32) n236 | -8.46 (-3.91) n72 |
| G_IDX (US500) | W30 k10 | 15 | 4.77 (3.01) n415 | 1.57 (1.09) n197 | -1.36 (-1.49) n236 | -9.14 (-3.33) n72 |
| G_IDX (US500) | W60 k6 | 1 | 1.25 (10.13) n3924 | 0.87 (5.95) n2213 | -1.61 (-14.28) n2756 | -2.57 (-12.75) n1043 |
| G_IDX (US500) | W60 k6 | 15 | 2.59 (7.50) n3924 | 1.92 (5.41) n2213 | -1.89 (-8.05) n2756 | -2.99 (-7.76) n1043 |

At W60 k6 (most events): with a panel co-move the jump continues (+0.9 to +2.6 bp, t 3.2-10, IS and VAL), without one it reverts (-1.1 to -3.1, t -7.5 to -14). The window overlaps the outcome, so this is the mechanism, not a rule.

### Information only, causal: the label from the detection minute's own close, entry at L 60 s (after the label is known), J1

| group | set | h | label | IS mid (t) n \| IS net (t) | VAL mid (t) n \| VAL net (t) |
|---|---|---|---|---|---|
| G_USD | W10 k16 | 1 | panel co-move | -9.40 (-1.31) n66 \| -12.83 (-1.60) | 0.58 (0.45) n10 \| -1.21 (-0.78) |
| G_USD | W10 k16 | 1 | no panel co-move | -2.44 (-1.06) n151 \| -8.02 (-2.90) | -0.88 (-0.68) n22 \| -9.80 (-2.38) |
| G_USD | W10 k16 | 15 | panel co-move | -15.58 (-1.43) n66 \| -18.63 (-1.63) | -5.27 (-1.49) n10 \| -7.36 (-1.76) |
| G_USD | W10 k16 | 15 | no panel co-move | -3.20 (-1.80) n151 \| -8.55 (-4.04) | -4.51 (-1.72) n22 \| -14.51 (-2.64) |
| G_USD | W30 k10 | 1 | panel co-move | -1.36 (-1.50) n641 \| -3.78 (-3.83) | 0.03 (0.04) n150 \| -1.87 (-2.08) |
| G_USD | W30 k10 | 1 | no panel co-move | -0.81 (-1.55) n1083 \| -4.74 (-7.88) | -0.13 (-0.31) n187 \| -4.45 (-4.91) |
| G_USD | W30 k10 | 15 | panel co-move | -1.84 (-1.18) n641 \| -4.18 (-2.60) | -0.83 (-0.63) n150 \| -2.70 (-1.99) |
| G_USD | W30 k10 | 15 | no panel co-move | -0.99 (-1.15) n1083 \| -4.87 (-5.21) | -1.75 (-1.66) n187 \| -5.80 (-4.46) |
| G_USD | W60 k6 | 1 | panel co-move | 0.02 (0.16) n5229 \| -2.02 (-19.34) | 0.07 (0.42) n1802 \| -1.89 (-9.36) |
| G_USD | W60 k6 | 1 | no panel co-move | -0.20 (-3.13) n13805 \| -3.02 (-34.84) | -0.12 (-1.19) n3385 \| -2.91 (-23.09) |
| G_USD | W60 k6 | 15 | panel co-move | 0.04 (0.16) n5229 \| -1.99 (-7.47) | -0.07 (-0.20) n1802 \| -1.99 (-5.42) |
| G_USD | W60 k6 | 15 | no panel co-move | -0.51 (-3.49) n13805 \| -3.31 (-20.79) | -0.47 (-1.66) n3385 \| -3.22 (-11.11) |
| G_IDX | W10 k16 | 1 | panel co-move | -1.14 (-0.68) n34 \| -2.80 (-1.68) | -3.32 (-1.14) n9 \| -3.97 (-1.33) |
| G_IDX | W10 k16 | 1 | no panel co-move | 1.71 (1.19) n27 \| -1.20 (-0.79) | -2.42 (-1.78) n8 \| -3.11 (-2.44) |
| G_IDX | W10 k16 | 15 | panel co-move | -4.25 (-1.44) n34 \| -5.90 (-2.00) | -15.13 (-1.44) n9 \| -15.78 (-1.50) |
| G_IDX | W10 k16 | 15 | no panel co-move | 2.48 (0.67) n27 \| -0.42 (-0.11) | -0.62 (-0.22) n8 \| -1.30 (-0.47) |
| G_IDX | W30 k10 | 1 | panel co-move | 0.26 (0.57) n429 \| -1.49 (-3.22) | -0.55 (-0.94) n211 \| -1.35 (-2.28) |
| G_IDX | W30 k10 | 1 | no panel co-move | 0.56 (1.75) n222 \| -1.36 (-4.24) | 0.10 (0.17) n58 \| -0.52 (-0.92) |
| G_IDX | W30 k10 | 15 | panel co-move | 2.49 (1.99) n429 \| 0.75 (0.60) | 0.63 (0.48) n211 \| -0.16 (-0.12) |
| G_IDX | W30 k10 | 15 | no panel co-move | 1.17 (1.39) n222 \| -0.75 (-0.89) | 2.04 (1.34) n58 \| 1.43 (0.93) |
| G_IDX | W60 k6 | 1 | panel co-move | 0.04 (0.39) n4217 \| -1.64 (-17.70) | 0.06 (0.57) n2373 \| -0.70 (-6.50) |
| G_IDX | W60 k6 | 1 | no panel co-move | 0.17 (2.28) n2460 \| -1.52 (-19.95) | -0.02 (-0.16) n883 \| -0.73 (-5.48) |
| G_IDX | W60 k6 | 15 | panel co-move | 0.80 (2.95) n4217 \| -0.87 (-3.23) | 0.84 (2.64) n2373 \| 0.08 (0.25) |
| G_IDX | W60 k6 | 15 | no panel co-move | 0.43 (1.75) n2460 \| -1.26 (-5.18) | 0.02 (0.06) n883 \| -0.69 (-1.85) |

Once the confirmation is known, USD-quoted jumps continue by ~0 bp (W60 k6 co-move +0.02 / +0.04 IS at 1 / 15 min) and index jumps by +0.5 to +0.8 bp at 5-15 min, all net negative or ~0: the information in a co-moving jump is priced within its first minute (round 8's result at tick level).

## 4. Best cell per family, cells tried, chance

| definition | family | cells (>= 10 IS events) | IS net > 0 | IS and VAL net > 0 | IS net t >= 2 | best cell (IS net t) | DEMO-number cells | LIVE |
|---|---|---|---|---|---|---|---|---|
| D2 | J1 | 3696 | 168 | 16 | 1 | W60 k16 h15 stop CO INDICES ALL (2.08; VAL -1.76) | 0 | 0 |
| D2 | J2 | 3696 | 507 | 246 | 16 | W10 k16 h15 none CO METALS Asia (2.60; VAL 2.17) | 3 | 0 |
| D1 | J1 | 3720 | 224 | 16 | 3 | W60 k16 h15 stop CO INDICES ALL (2.16; VAL -2.04) | 0 | 0 |
| D1 | J2 | 3720 | 388 | 162 | 16 | W10 k16 h15 none CO METALS Asia (2.95; VAL 2.52) | 6 | 0 |

D2: K = 7392 cells with >= 10 IS events; max-\|t\| of K independent normals (95 %) 4.50; per-day sign-flip permutation null of the max IS net t (1,000 draws): p50 2.03, p95 2.88; observed max 2.60 (13.8 % of draws exceed it). Primary 108 cells: K-normal 95 % 3.49, null p95 1.13, observed max 0.02.

D1: K = 7440 cells with >= 10 IS events; max-\|t\| of K independent normals (95 %) 4.50; per-day sign-flip permutation null of the max IS net t (1,000 draws): p50 2.06, p95 2.91; observed max 2.95 (4.3 % of draws exceed it). Primary 108 cells: K-normal 95 % 3.49, null p95 1.00, observed max 0.49.

Per-day units (daily sums of net): in the primary cells, the best per-day power is +0.01 in IS for J1 and -0.04 for J2. In VAL it is -1.76 for J1 and +0.97 for J2. The metals cells give per-day Sharpe 0.42 / 0.82 (IS / VAL) and per-day power 1.42 / 1.65 (Asia, W10). RD (random side at the same events) is beaten 100 % / 98 % (Asia, W10), 100 % / 100 % (all sessions) and 100 % / 99 % (W30).

## 5. Latency, spreads and stops
- **Effective entry delay** (median ms after detection, all events): L 250 ms -> 401-575 ms; L 1,000 ms -> 1.2-1.5 s;
  next tick -> 240-401 ms. IC's ticks arrive every ~0.4-0.7 s, so a "250 ms" bot usually fills on the second or third
  quote after the jump.
- **Latency hardly matters at 1-15 min.** Differences against L 250 in the primary cells, IS:
  - J2 (fade), zero latency (entering on the jump's own tick, which no bot can do): +0.6 to +1.0 bp for k16, +0.1 to
    +0.2 for k10, -0.03 to -0.06 for k6.
  - J2, L 1,000 ms and the next tick: within -0.15..+0.22 bp.
  - J2, "+1 minute": costs 0.5-3.2 bp, because the reversal is front-loaded.
  - J1 (follow): zero latency is 0.1-1.2 bp better, and "+1 minute" is 0.2-4.7 bp better. The follow trades lose
    most in the first minute, which is the reversal.
- **Spreads in jumps.** On IC's feed the spread at the detection tick is the trailing median in FX and metals (ratio
  1.00), 1.09x in indices and 1.21x in energies. Spread paid per round trip at h 5, L 250 (IS / VAL), against the
  trailing median:
  - FX: 0.69 / 0.80 bp vs 0.66 / 0.53;
  - metals (pooled, XAG / XPT dominate): 3.35 / 3.16 vs 3.02 / 2.78;
  - indices: 1.77 / 0.76 vs 1.62 / 0.74;
  - energies: 18.9 / 9.5 vs 10.4 / 8.5. Energy spreads roughly double after jumps in 2018-21, with XNG the worst.
- **Stops.**
  - A resting stop at theta from the entry mid is hit in 6-12 % of trades by 1 min, 18-25 % by 5 min and 33-40 % by
    15 min.
  - A stop fill counts as spread-only when the stop side would not have reached the level had the spread stayed at
    its entry width. Spread-only fills are 17-27 % of stop fills in FX and metals, 6-7 % in indices and 9-15 % in
    energies.
  - The stop is worse than no stop in 48 of 54 primary pairs in IS (50 in VAL) and in 2,504 of 3,696 pairs overall.
    It also turns the metals DEMO-number cell from +12.15 bp to +5.01 (t 0.75).
- **Quote spikes are rare.** In 0.2-0.5 % of events the next tick takes back >= 50 % of the move (energies 4.9 %),
  so the reversal is not a single-tick glitch effect.

## 6. PRE (Dukascopy, labelled minute-level check; Addendum 2)
Dukascopy has only M1 closes for metals, so the 10-30 s rule is proxied by a 1-minute close-to-close move of >= 16
sigma, confirmed by the other metal in the same minute, Asia, faded for 15 min. IC 2016-17 spreads by minute of day
plus 0.6 bp.
- Calibration on IC's own M1 (2016-24): XAUUSD 8 IS events (mid +22.1 bp, t 1.96) and **0 VAL events**; XAGUSD 10
  IS events, 1 VAL event.
- A 1-minute close-to-close 16-sigma move is far rarer than a 16-sigma range within 10 s. By the declared criterion
  the proxy cannot reproduce the tick result in VAL, so **the PRE check is not meaningful for this rule.**
- As information, PRE 2008-15: XAUUSD n 30, net -3.01 bp (t -0.94); XAGUSD n 35, net +8.53 (t 1.04).

## 7. C3 correlation
For the metals DEMO-number cell, the daily net P&L correlation with C3's daily P&L (IS + VAL) is +0.014 over all
weekdays and +0.10 over its 44 trade days. The all-session variant gives -0.002 / +0.012. No other cell survived.

## Needs the user
- **Major-pair ticks** (EURUSD, USDJPY, GBPUSD, USDCAD; cTrader backtest downloads on the VPS). The information /
  liquidity split exists, but here it needs a non-causal minute label. With ticks of the majors, a causal tick-level
  USD-wide co-move label could be tested. The prior is low: entering when the minute label is known leaves ~0 bp, and
  the useful part is in the first seconds, against an FX round trip of ~1.3 bp.
- **Dukascopy ticks 2008-15 for XAUUSD / XAGUSD**, only if the user wants the metals DEMO-number effect pursued (a
  tick-level PRE). The prior is low: the event rate collapsed after 2017.
- **Data after 2026-09-24** for a forward log of the metals fade (DEMO at most, ~2-3 events a year; not recommended).

## Untested ideas
- **Jumps at venue clocks (the E10 events) as their own family.** The Shanghai metals / oil opens (01:00, 05:30,
  13:00 UTC), the CNY fixing (01:15), the European cash open in US indices, 07:00 New Zealand and the 15:50 NY MOC
  produce 20-190x the average jump rate. These are scheduled flows, so a side would need declaring from the
  opening-auction / price-discovery literature. Their returns were never computed (excluded before any number).
- A causal tick-level USD-wide co-move label (needs the majors' ticks, above).
- Passive limit orders resting beyond the jump instead of market fades: no entry spread. Round 12 found passive fills
  adversely selected; stream S tests limits at releases.
- Longer holds (1-4 h) after the largest metals jumps (the reversal keeps growing to 15 min). Post hoc, so it would
  need declaring on new data.
- A spread-state split (spread blown out at detection or not) as a liquidity marker. On IC's feed the detection
  spread is the median in FX and metals, so it would separate little.

## Scripts and outputs
All under /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r26/J/.

Scripts in `code/`:
| script | what it does |
|---|---|
| common_j.py | instruments, sets, the day loader with the HOLD assert, timezone and session helpers |
| excl_j.py | exclusions E1-E7, E9 -> `out/excl.npz` |
| e10_j.py | Addendum 1 clock flags -> `out/excl_D2.npz`, `out/e10_flags.txt` |
| pass_j.py | per-day tick pass: detection, labels, trades at every latency, stops, RT control per atom |
| analyze_j.py | all cells, controls, permutation null -> `out/cells_D1.npy`, `out/cells_D2.npy`, `out/chance_*.npy` |
| report_j.py | counts, exclusion shares, labels, spreads, mechanism split -> `out/report_tables_D1.txt`, `out/report_tables_D2.txt` |
| panel_label_j.py, panel_causal_j.py | information-only panel labels -> `out/panel_label_D2.txt`, `out/panel_causal.txt` |
| pre_check_j.py | Addendum 2 -> `out/pre_check.txt` |
| sanity_j.py | -> `out/sanity.txt` |
| stream_tables_j.py | -> `out/stream_tables.md` |
| peek.py, proto_detect.py, proto_counts.py | data-structure and count prototypes run before the hypotheses (no returns) |

Event files in `out/`:
- D1: `events_A.npz`, `events_B.npz`, with matching `atoms_*.npz` and `raw_*.npz`;
- D2: `events_D2A.npz`, `events_D2B.npz`, with matching atoms and raw files;
- the first D2 run before the stop-flag fix: `out/v1/`.

## Process notes
Order of work (all UTC):

| time | step |
|---|---|
| 20:05 | start |
| 20:10-20:16 | data peek and count prototypes; no forward return |
| 20:17 | HYPOTHESES_J.md written |
| 20:26-20:31 | D1 pass |
| 20:31 | sanity listing: counts by minute, NaN shares, the 25 largest single-event moves |
| 20:33 | Addendum 1 written, before any cell statistic |
| 20:34-20:38 | D2 pass |
| 20:39 | cell analyses D2 and D1 |
| 20:43 | Addendum 2 (PRE) written |
| 20:44 | PRE run |
| 20:45-20:50 | panel labels; the stop-flag fix and the D2 rerun |
| 20:52 | PREREG draft written |

Corrections and limits:
- The stop "spread-triggered" flag was first defined as "the mid had not reached the level". That flags almost every
  stop fill (the mid sits half a spread inside the stop side), so it was redefined against the entry spread. D2 was
  rerun; events and returns are identical (checked), only that flag changed.
- The x1.5 check of the stop variants uses the time-exit spread as a stand-in for the stop-exit spread.
- The RT control matches each event's own label, instrument, day and session. Its side is recomputed at the random
  time.
- A cell's mean can be carried by a few large events (one silver event of +207 bp; XPT and XNG quote glitches of
  5-7 %). The winsorised requirement guards against that; the day-clustered t ignores it.

Rules kept:
- No web request was made: the literature is cited from memory (HYPOTHESES_J.md).
- No file under research/ was edited. The tick decoder was reused through my own loader with the HOLD assert.
- At most two heavy processes ran at a time.
