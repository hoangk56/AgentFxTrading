# Stream S: FX very short windows (1-10 minutes) at benchmark minutes, PRE 2004-15 discovery -> IS 2016-21 -> VAL 2022-24

Hypotheses with UTC times, written before their numbers (post hoc additions marked): [HYPOTHESES_S.md](HYPOTHESES_S.md).
Drafts: [PREREG_DRAFT_S_eurusd_friday_ecb_prefix.md](PREREG_DRAFT_S_eurusd_friday_ecb_prefix.md),
[PREREG_DRAFT_S_gbpjpy_monthend_1028.md](PREREG_DRAFT_S_gbpjpy_monthend_1028.md) (both post hoc; stream S
recommends registering neither). HOLD was never loaded: Dukascopy ends 2015-12-31 (2017-12-31 for the 2016-17
alignment files), the panel ends 2024-12-31, IC ticks were read for four 2016-24 days only, C3's list was read with
2025+ rows skipped.

## Answer
- **No LIVE candidate. The declared path finds nothing beyond chance.** Of the 409 cells above the PRE family-wise
  bar, 25 confirm in IS. The sign-flip null gives a 95th percentile of 30. Set B (top 300) confirms 20, against 27. No
  confirmed cell is net > 0 in both IS and VAL.
- **The PRE-strong benchmark effects moved or vanished after 2015.**
  - The largest PRE cells are the old ECB V, at 13:10-13:15 London (14:10-14:15 CET), up to t 15.9. On the New York
    clock the same move shows up at 08:10-08:15.
  - From 2016 these cells have the opposite sign in IS, because the V moved to 12:55-13:02 London.
  - On the PRE side, the cells with |t_PRE| >= 4 average PRE +0.75 / IS -0.07 / VAL +0.09 bp (ECB), and
    +0.75 / -0.13 / +0.10 (NY 08:30).
- **Even in hindsight, no every-weekday 1-10-minute window at any benchmark minute clears the LIVE line.**
  - The largest |IS mid| of any every-day cell is 0.88 bp for EURUSD (ECB slot) and 0.45 bp for USDJPY.
  - The line is cost + 0.144 sd = 0.8-1.2 bp.
  - Most cells pay 0.63-1.1 bp of cost to capture 0.1-0.5 bp of mid.
- **Two post hoc leads meet the DEMO numbers.** Both were chosen on IS from a loose pool (|t_PRE| >= 2), with VAL in
  view:
  1. **EURUSD short 12:50-13:00 London on Fridays.** It sits in the ECB pre-fix slot, inside E1. Net +1.13 (t 3.81)
     IS and +1.31 (t 2.74) VAL; power 2.04 / 2.08; PRE net -0.08.
  2. **GBPJPY long 10:28-10:31 New York on the last weekday of the month.** Net +2.48 (t 4.34) IS and +0.47 (t 0.77)
     VAL. It is decaying (VAL/IS 0.45), has no known mechanism, and its plateau is one cell wide.
- **Recommendation:** register neither as a HOLD test.
  - The Friday cell is a subset of E1, whose HOLD is already open.
  - The GBPJPY cell's expected HOLD t is about 0.6.

## S0. Minute labels (verified before scanning)
| check | result |
|---|---|
| IC panel vs IC ticks (AUDUSD, 4 days 2016-24) | panel close of label L = last tick in [L, L+1) on 1,303-1,316 / 1,303-1,316 minutes (100 %); [L-1, L) matches 3-7 %. **Bar-START labels** |
| Dukascopy 2016-17 vs IC (USDJPY, EURJPY, GBPJPY), 1-min return correlation | lag 0: 0.991-0.994; lags +-1: -0.01..-0.02. Same labels |
| US 08:30 ET release on first Fridays, mean \|1-min return\| by bar label | peak in bar 08:30 in both: EURUSD PRE 20.6 bp (08:29 6.2, 08:31 8.5), IS 14.6; USDJPY PRE 28.5, IS 15.4 |
| ECB V, EURUSD by London minute | PRE: drop in bars 13:13-13:14 (-0.34, -0.56 bp, t -10, -12), rebound 13:15-13:16; IS / VAL: drop in bar 12:57 (-0.43, t -10.2 / -0.26), rebound in bar 13:02 (+0.24 / +0.39, t 6-7) |
| the same V in both sources on the same days (EURJPY 2016-17, 5-min sums) | Dukascopy 12:55-13:00 -0.68 (t -3.7), IC -0.68 (t -3.7) |

The ECB V moved about 16 minutes earlier at the 2015/16 boundary in the market, not in the data, which confirms round
13 M. Grids as declared: price at boundary m = close of the bar labelled m-1, in both sources.

## Design (as declared at 02:04 UTC)
- **Symbols:** EURUSD and USDCHF (all hours); USDJPY, EURJPY and GBPJPY with 23:00-02:00 UTC removed.
- **Anchors:**
  - ECB 14:15 CET (= 13:15 London all year);
  - WM/R 16:00 London;
  - 10:00 New York (option cut and data minute);
  - 15:00 Tokyo;
  - London 08:00 (= Frankfurt 09:00 CET, counted once);
  - 08:30 ET;
  - CME 14:00 and 15:00 ET.
- **Windows:** lengths 1, 2, 3, 5 and 10 minutes, starting at every minute within +-30 minutes of an anchor.
- **Day types:** every weekday, Monday..Friday, and month-end (the last weekday).
- **Cell count:** K = 85,225. Every window touching 16:45-18:15 New York, and 24 Dec - 1 Jan, are excluded.
- **Prices:** PRE uses the Dukascopy bid; IS and VAL use the panel mid.
- **Costs:**
  - IS and VAL: half the actual spread at the entry and exit minutes, plus 0.6 bp;
  - PRE: IC's 2016-17 spread profile by New York minute, plus 0.6 bp.
- **Side:** the sign of the PRE mean.
- **Control:** EURUSD, every 1/2/3/5-minute window of the day (London clock, every weekday); 5,633 cells.
- **Latency:** no FX ticks exist for these symbols, so the +10 s and +30 s fills could not be run. Only +1 minute was
  run.

## Discovery and confirmation, with chance benchmarks
| step | benchmark cells | control (EURUSD all windows) |
|---|---|---|
| PRE max \|t\| | 15.94 (EURUSD short 13:13+2 London) | 13.32 (EURUSD short 11:55+5 London) |
| sign-flip null of the max (one sign per date, shared, 200 draws) | median 4.34, **95 % 5.02** | median 3.77, 95 % 4.35 |
| cells above the 95 % bar | set A 409 (ECB 185, NY 08:30 139, Tokyo 15:00 42, London 08:00 24, CME 13, NY 10:00 5, WM/R 1) | 361 |
| IS confirmations (side t >= 2) vs IS sign-flip null | A: **25** (null median 8, **95 % 30**); B (top 300): **20** (null 95 % 27) | **58** (null median 8, 95 % 15) |
| best side t_IS vs null of the max | 8.92 vs 3.61 | 8.92 vs 3.56 |
| VAL, confirmed cells | A: 14/25 same sign, 7 with t_VAL >= 1.5 | 33/58 same sign, 11 with t_VAL >= 1.5 |
| net > 0 in IS and VAL among the confirmed | **0** | **0** |
| mean mid on the PRE side, carried set (PRE / IS / VAL) | A: +0.70 / **-0.12** / +0.05 | +0.24 / +0.02 / +0.00 |

Are the benchmark minutes special? In PRE they are not:
- In the control, cells beyond the null are 5.8 % within +-30 minutes of a benchmark and 6.8 % elsewhere (median
  |t| 1.23 vs 1.43).
- The control's strongest PRE cells are the 11:52-12:00 London slot that round 13 found (gone from 2016) and
  0.1-0.3 bp Asian-session minutes.
- Those Asian minutes confirm in IS beyond chance, but they are a third of their cost.

### Best PRE cell per anchor (PRE selection; mid bp on the PRE side (t); net = mid - actual cost)
| anchor | cell | PRE | IS | VAL | cost IS / VAL | net IS / VAL | power IS / VAL |
|---|---|---|---|---|---|---|---|
| ECB | EURUSD short 13:13-13:15 London | +0.90 (15.9) | -0.19 (-3.5) | -0.12 (-1.6) | 0.65 / 0.64 | -0.84 / -0.76 | <0 |
| NY 08:30 | EURUSD short 08:13-08:15 NY (the ECB V on the NY clock) | +0.84 (14.9) | -0.23 (-4.1) | -0.12 (-1.6) | 0.65 / 0.64 | -0.88 / -0.76 | <0 |
| Tokyo 15:00 | EURUSD short 14:33-14:34 JST | +0.25 (9.5) | -0.02 (-1.2) | +0.01 (0.2) | 0.69 / 0.64 | -0.71 / -0.63 | <0 |
| London 08:00 | EURUSD short 07:59-08:04 London | +0.70 (6.9) | -0.18 (-1.6) | -0.61 (-3.7) | 0.64 / 0.62 | -0.82 / -1.24 | <0 |
| CME 15:00 | EURUSD short 14:59-15:02 NY | +0.36 (6.8) | +0.27 (4.7) | +0.02 (0.3) | 0.68 / 0.62 | -0.41 / -0.60 | <0 (VAL/IS 0.09) |
| CME 14:00 | EURUSD short 13:34-13:35 NY | +0.19 (6.3) | -0.04 (-1.3) | +0.01 (0.3) | 0.64 / 0.62 | -0.68 / -0.61 | <0 |
| NY 10:00 | USDCHF short 09:59-10:00 NY | +0.40 (6.2) | -0.13 (-2.6) | +0.12 (1.6) | 1.04 / 1.01 | -1.17 / -0.90 | <0 |
| WM/R | USDCHF short 15:43-15:44 London | +0.24 (5.2) | -0.05 (-1.1) | +0.06 (0.7) | 0.90 / 0.89 | -0.95 / -0.83 | <0 |
| WM/R month-end | EURUSD short 15:45-15:55 London | +2.39 (3.9) | +1.61 (1.4) | -0.84 (-0.5) | 0.63 / 0.69 | +0.98 / -1.52 | 0.46 / <0 |

Shrinkage of cells with |t_PRE| >= 4 by anchor. Mean mid on the PRE side, PRE / IS / VAL, then the share with
t_IS >= 2 and with t_IS <= -2:

| anchor | PRE / IS / VAL mid | t_IS >= 2 | t_IS <= -2 |
|---|---|---|---|
| ECB | +0.75 / -0.07 / +0.09 | 10 % | 26 % |
| NY 08:30 | +0.75 / -0.13 / +0.10 | 1 % | 28 % |
| London 08:00 | +0.48 / -0.02 / -0.20 | 15 % | 26 % |
| Tokyo 15:00 | +0.28 / +0.01 / -0.00 | 9 % | 3 % |
| CME 15:00 | +0.32 / +0.07 / +0.12 | 12 % | 0 % |
| others (WM/R, NY 10:00, CME 14:00) | 10-21 cells each, IS within +-0.2 | | |

### Hindsight bound against the LIVE line (every weekday, the best |IS mid| per anchor, chosen on IS)
| EURUSD anchor | best cell | \|IS mid\| | cost | needed (cost + 0.144 sd) | max \|IS mid\| any cell |
|---|---|---|---|---|---|
| ECB | 12:57+2 London | 0.54 | 0.63 | 0.97 | 0.88 |
| London 08:00 | 07:54+5 | 0.66 | 0.64 | 1.17 | 0.78 |
| WM/R | 15:54+1 | 0.30 | 0.63 | 0.90 | 0.76 |
| NY 08:30 | 08:02+5 | 0.51 | 0.63 | 1.09 | 0.59 |
| NY 10:00 / CME 14:00 / CME 15:00 / Tokyo 15:00 | | 0.15-0.30 | 0.63-0.68 | 0.81-0.95 | 0.27-0.33 |

- USDJPY: the best cell at any anchor has |IS mid| <= 0.45, against a cost of 0.72-0.76.
- Share of all cells with net > 0 in IS and VAL on the PRE side:
  - 1 minute: 0.01 %;
  - 3 minutes: 0.17 %;
  - 10 minutes: 0.55 %.
- Median cost is 0.86 bp at every length.

## Post hoc leads (marked; the side is from PRE, the window and day type from IS)
- Loose pool: the 9,111 cells with |t_PRE| >= 2.
- IS sign-flip null of the max side t over the pool: median 3.70, 95 % 4.27.

| lead | where | PRE / IS / VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS | x1.5 IS / VAL | +1 min IS / VAL | random IS / VAL | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ECB pre-fix slot, Fridays | EURUSD short 12:50-13:00 London | +0.58 (2.5) / +1.76 (5.95) / +1.95 (4.10) | 0.63 / 0.64 | **+1.13 (3.81) / +1.31 (2.74)** | 1.11 | +1.11 / +1.28 | +0.96 / +0.70 | 100 % / 100 % | 2.04 / 2.08 | DEMO numbers, LIVE except power; post hoc; E1 subset; PRE net -0.08; draft |
| same, IS-best 5 min | 12:55-13:00 Fridays | +0.71 (4.6) / +1.58 (7.18) / +1.29 (3.65) | 0.63 / 0.64 | +0.95 (4.31) / +0.65 (1.85) | 0.82 | +0.93 / +0.63 | +0.50 / **-0.51** | 100 % / 100 % | 2.31 / 1.40 | fails +1 min in VAL |
| same, every weekday | 12:50-13:00 | +0.31 (3.0) / +0.82 (5.7) / +0.87 (4.4) | 0.63 / 0.62 | +0.19 (1.32) / +0.24 (1.24) | 1.05 | | +0.25 / -0.00 | | 0.71 / 0.94 | below the bar |
| month-end, 15:28 London | GBPJPY long 10:28-10:31 NY | +1.32 (2.9) / +3.51 (6.17) / +1.58 (2.60) | 1.04 / 1.11 | **+2.48 (4.34) / +0.47 (0.77)** | **0.45** | +2.26 / +0.21 | +1.09 / +0.61 | 100 % / 100 % | 2.33 / 0.59 | DEMO numbers; decaying, one-cell plateau, no mechanism; draft, not recommended |

- **The Friday effect:**
  - Friday minus Mon-Thu in the 12:50-13:00 slot: PRE +0.34 (t 1.32), IS +1.18 (t 3.48), VAL +1.36 (t 2.60).
  - Friday also enlarges the post-fix rebound (long 13:00-13:15): IS +1.16, VAL +1.71, against +0.05..+1.05 on the
    other days.
  - Information only: the Friday two-leg V nets +1.65 (t 3.60) IS and +2.38 (t 3.78) VAL, with power 1.93 / 2.87.
    PRE is -2.33, because the PRE V sat at 13:13. The post-leg side contradicts PRE.
- **Overlap with E1 and the ECB slot:**
  - every Friday cell lies inside E1 (11:00-13:00 London) and inside the ECB pre-fix slot (12:45-13:00);
  - the GBPJPY cell overlaps neither.
- **C3 correlation (IS+VAL):** Friday cell +0.023 daily / -0.058 monthly; GBPJPY +0.002 / +0.030.

## What this says
- **Short windows do not beat the cost floor at FX benchmark minutes.** The flows are concentrated: the ECB V is two
  minutes of -0.3..-0.6 bp per minute. But the concentrated part is 0.3-0.9 bp, and IC's 0.6 bp commission alone takes
  most of it. At 1-3 minutes the required mid is 0.8-1.0 bp, and no every-day cell has it, even chosen in hindsight.
- **PRE discovery at minute resolution selects market microstructure that changed.** The strongest PRE minute
  effects are the pre-2016 ECB timing, and they have the opposite sign afterwards. Selecting on 12 years of PRE did
  worse than chance here (25 vs a null 95th percentile of 30). In round 13, at 15-240 minutes, it did better than
  chance.
- **Benchmark minutes are not special in PRE.** The control scan finds as many beyond-chance cells away from them,
  and more IS confirmations (58). Those are tiny (0.1-0.3 bp).
- **The only tradable short-window structure is the ECB pre-fix slot on Fridays.** It is E1's tail on one day a week,
  and is about 2/3 of the LIVE power.

## Surprises
1. The ECB V moved about 16 minutes earlier at the 2015/16 boundary (PRE drop at 14:13-14:15 CET, IS/VAL drop at
   13:57-13:58 CET, rebound 14:02 CET). Dukascopy and IC agree on 2016-17, so this is the market, not the data.
2. Friday carries about twice the ECB-fix V in 2016-24 in both legs; PRE shows only a weak Friday tilt.
3. The NY 08:30 anchor's top PRE cells (08:10-08:15 NY) are the ECB V seen through the New York clock, not a
   data-release effect.

## Directions that need the user's decision
1. **EURUSD ticks 2016-2024** (IC). The brief's +10 s / +30 s latency test cannot be run without them. A 10-minute
   Friday window loses 0.2-0.6 bp at +1 minute.
2. **A commission-free EURUSD venue.** At cost about 0.1 bp, the every-day ECB slot cells (IS mid 0.5-0.9) would net
   about 0.4-0.8. This is the only way short windows reach LIVE in this data.
3. **Whether the lead registers the Friday ECB draft.** It is not blind (E1's HOLD is open). Stream S recommends a
   forward demo instead of a HOLD test, if anything.
4. **Data after 2026-09-24** as the only clean holdout (unchanged).

## Scripts and outputs
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r15/S/`:
- `align.py` -> `align.out`: label checks (ticks, Dukascopy vs IC, NFP, ECB V).
- `scommon.py`: anchors, cells, window matrices, costs. It builds on round 13 M's `mcommon.py` (grids, clocks, day
  types).
- `scan.py` -> `scan.out`, `cells.npz`, `perm_pre.npz`, `ctrl.npz`, `perm_ctrl.npz`: all cells, the PRE null, the
  control.
- `step2.py` -> `step2.out`: sets A and B, IS confirmation and null, VAL, the control family.
- `step3.py` -> `step3.out`: per-anchor tables, the post hoc loose carry, the hindsight bound, month-end WM/R,
  shrinkage.
- `step4.py` -> `step4.out`: the lead evaluations, random entries, C3, weekday split, placebos, the pool null.
- `step5.py` -> `step5.out`, `step6.py` -> `step6.out`, `step6b.out`: robustness, plateau, the two-leg information
  line, the IS-only ranking by length.
