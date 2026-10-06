# Round 12, stream I: month-end equity-hedge rebalancing at the WM/R 16:00 London fix

2026-10-06. Hypotheses with UTC times: HYPOTHESES_I.md. IS 2016-01..2021-12, VAL 2022-01..2024-12, shared panel
only; HOLD never loaded. No PRE era (no equity index before 2016 in the data).

## Answer
- **The paper's own effect (into the fix, signed by relative equity returns) is not there in 2016-21**: the primary
  cell, declared before looking, is IS -1.14 bp (t -0.54) / VAL +3.43 (t 1.23). Fails.
- **The post-fix reversal of the predicted hedge flow is real in IS and month-end specific, weaker in VAL.** Gated
  on large US months (|S&P month-to-date| >= 2.45 %), USD bought (sold) 16:00-17:00 London on the last business day
  after a rising (falling) US month, EURUSD + USDJPY + GBPUSD: net +6.77 bp per trade, month-clustered t 3.79, 6/6
  years (IS); +1.68 bp, t 0.84, 2/3 years (VAL). It survives spread x1.5 and +1 minute in both eras, beats 100 % of
  random entries in IS (86 % in VAL), the ordinary-day placebo has the opposite sign, and it is the best of 27 basket
  cells beyond a permutation null (p 0.002).
- It meets the DEMO numbers on IS/VAL with one caveat (VAL random-entry 86 % < 90 % if the control is applied to VAL
  alone; 100 % IS and pooled). Draft: **PREREG_DRAFT_I_month_end_post_fix_usd.md**. LIVE fails (VAL t 0.84 < 1.5;
  power 3.0 on trades but 2.0 on month-clustered events, and ~0.5 on VAL's Sharpe).

## Literature (side, window, magnitude)
- Melvin & Prins (2015, JFM 22; 2013 working paper read in full): hedges reset on the last business day at the WM/R
  fix, sized on the close of the day before; currency return 15:00-16:00 London regressed on the country's
  month-to-date (to the second-last day) local equity return, demeaned across 10 countries: -1.42 bp per 1 %
  (p 0.00, 2004-12); 72 % reverses by noon next day on month-end days. Side: a country's equity outperformance ->
  its currency falls into the fix.
- A 2026 practitioner replication (Feb 2015-Jul 2026): S&P month-to-date +1 % -> USD -2.1 bp over 15:00-16:00
  London; opposite post-fix slope over 16:03-17:00 (41-75 % reversal). Overlaps HOLD; used only for sides/windows.
- Hau & Rey (2006), Camanho, Hau & Rey (2022): same sign via rebalancing.

## I1: into the fix (54 cells), mid bp per event (equal weight across pairs), month-clustered t
Signals: S_rel = local index MTD minus US500 MTD (paper; DE40 for EUR/CHF, UK100, JP225, AUS200 for AUD/NZD, 6
pairs); S_usd = same in USD terms; S_us = US500 MTD alone (7 pairs incl. USDCAD). Side fixed from the paper.
| cell | IS mid (t) | cost | IS net | VAL mid (t) | VAL net |
|---|---|---|---|---|---|
| **primary: S_rel, T, 15:00-16:00, all** | -1.14 (-0.54) | 0.88 | -2.02 | +3.43 (1.23) | +2.62 |
| S_rel, T, 15:00, quarter-ends | -2.47 (-1.03) | 0.88 | -3.36 | +6.88 (2.20) | +6.03 |
| S_usd, T, 15:00, all | -0.84 (-0.43) | 0.88 | -1.71 | +1.40 (0.54) | +0.58 |
| S_us, T, 15:00, all | +0.96 (0.46) | 0.88 | +0.09 | +5.18 (1.74) | +4.37 |
| S_us, T-1, 15:00, all (best IS) | +5.03 (3.80) | 0.92 | +4.11 | +1.25 (0.63) | +0.44; **+1 min: -0.86** |
| S_us, T-1, 15:30, all | +2.75 (3.04) | 0.84 | +1.91 | +0.07 (0.05) | -0.69 |
| S_rel, T-1, 15:00, quarter-ends | +4.39 (2.63) | 0.89 | +3.50 | -2.59 (-1.16) | -3.38 |
| S_rel, T-2, 15:00, all | +2.07 (1.49) | 0.96 | +1.11 | +4.54 (1.64) | +3.69 |
| S_rel, T-2, 15:30, all | +0.90 (0.89) | 0.84 | +0.06 | +4.28 (2.49) | +3.54 |
| S_us, T-2, 15:30, all | -2.09 (-1.74) | 0.84 | -2.93 | +5.60 (2.74) | +4.86 |

Pattern: on T the paper's sign shows up only in VAL (2022-24), on T-1 only in IS, on T-2 mostly in VAL. Nothing in
I1 is positive in both eras at IS t >= 2. The best IS cell (S_us T-1 15:00) loses its VAL sign at +1 minute and as a
3-pair basket (IS t 1.33, VAL -0.10 bp per event).

## I2: after the fix on T (18 cells), side = against the predicted hedge flow
| cell | IS mid (t) | IS net | VAL mid (t) | VAL net |
|---|---|---|---|---|
| S_rel 16:00-17:00 all | +1.44 (1.12) | +0.62 | +2.16 (1.50) | +1.41 |
| S_us 16:00-17:00 all | +4.65 (3.12) | +3.83 | +0.75 (0.39) | +0.00 |
| S_us 16:05-17:00 all | +2.93 (2.33) | +2.08 | +0.16 (0.09) | -0.62 |
| S_us 16:00-next 12:00 all | +12.98 (3.32) | +12.14 (before swap) | -3.96 (-0.46) | -4.70 |
| S_us 16:00-next 12:00 quarter-ends | +17.92 (3.00) | +17.08 | +0.69 (0.05) | -0.06 |

Level vs conditional (S_us 16:00-17:00, USD side, 7 pairs): IS US-up months +5.41 bp (t 4.11, n 56), US-down -1.83
(n 15); VAL +1.12 / -0.17. It is conditional, not an unconditional month-end USD move.

## Multiple testing
- 72 mid cells: best IS |t| 3.80 (S_us T-1 15:00); permutation null (sides flipped per month, shared by all cells):
  max |t| median 2.53, 95 % 3.52, p 0.018. Nine cells had IS t >= 2 on the predicted side (about 1.6 expected by chance if the cells were independent; they are
  correlated); two of them had VAL net > 0 (S_us T-1 15:00 and S_us I2 16:00-17:00, both ~0 in VAL).
- 27 basket cells (I3: the 9 cells x {all, gated at IS median |signal|, size 0.5-2x}): best gross IS t 4.17 (the
  candidate); null 95 % 3.11, p 0.002.

## I3 baskets (<= 3 positions; S_us: EURUSD, USDJPY, GBPUSD = cheapest at 15-17 London; executable)
| basket | IS net/trade | IS t (x1.5, +1m) | yrs | VAL net/trade | VAL per event, x1.5, +1m | random IS / VAL |
|---|---|---|---|---|---|---|
| **I2 S_us 16:00-17:00 gated** | **+6.77** | **3.79** (3.77, 4.09) | 6/6 | **+1.68** | +5.03, +4.93, +4.49 (t 0.84) | 1.00 / 0.83-0.86 |
| I2 S_us 16:00-17:00 size-scaled | +4.85 | 2.54 (2.51, 2.87) | 6/6 | +0.99 | +2.96, +2.83, +2.18 | 1.00 / 0.76 |
| I2 S_us 16:00-17:00 all | +1.86 | 1.08 | 5/6 | -0.50 | -1.51 | |
| I2 S_us 16:05-17:00 gated | +4.59 | 2.83 (2.80, 2.69) | 6/6 | +0.36 | +1.09, +0.96, +2.09 | 1.00 / 0.73 |
| I2 S_us 16:00-next 12:00 gated (with swap) | +16.88 | 3.01 | 6/6 | -2.03 | -6.08 | 1.00 / 0.35 |
| I2 S_us 16:00-next 12:00 size | +16.29 | 3.03 | 6/6 | -5.83 | -17.49 | 1.00 / 0.27 |
| I1 S_us T-1 15:00 all | +1.81 | 1.33 | 3/6 | -0.03 | -0.10, +1m -4.74 | |
| I1 S_rel T-1 15:00 quarter-ends | +3.01 | 1.61 | 5/6 | -2.18 | -6.55 | |
Other 15 baskets: IS t < 1.1 or VAL < 0 (scratch analyse_I.txt).

## The candidate: checks (all post hoc, pre-written in HYPOTHESES_I.md P4-P9 with a decision rule)
| check | result |
|---|---|
| mid / cost / net per trade | IS +7.46 / 0.69 / +6.77; VAL +2.34 / 0.66 / +1.68 |
| per pair net IS (VAL) | EURUSD +8.83 (+2.85), USDJPY +3.85 (-1.41), GBPUSD +7.63 (+3.58) |
| years | 2016-21 all > 0 (+15..+36 bp per event); 2022 +6.2, 2023 -3.3, 2024 +11.6 |
| threshold 33rd / 50th / 67th pct of IS \|r_US\| | IS t 3.18 / 3.79 / 2.88; VAL per trade -0.37 / +1.68 / +2.73 (rises with \|signal\|) |
| US-up / US-down months per event | IS +23.7 (t 4.6, n 27) / +10.0 (t 0.7, n 9); VAL +8.7 (t 1.2, n 14) / -0.1 (n 10) |
| ordinary-day placebo (21-bd US return, gated) | IS -0.83 bp/trade (t -2.05), VAL +0.67 (t 1.03): month-end specific |
| random entries (500 seeds) | beats IS 100 %, VAL 86 %, pooled 100 % |
| overlap with round 3 F1 (fade the realised 15-16 move) | same side on 45 % (IS) / 49 % (VAL) of trades; IS +9.4 agree / +4.6 disagree; VAL +4.1 / -0.6 |
| C3 correlation IS+VAL | daily -0.05, monthly +0.01 |
| Sharpe and power | per trade IS 0.544 (18 trades/yr) -> 3.0 on ~31 HOLD trades; per event 0.63 (6/yr) -> 2.0; VAL Sharpe ~0.13/trade, ~0.17/event -> HOLD t ~0.5 |

Verdict: DEMO numbers met on IS/VAL (IS t 3.79 >= 2, VAL net > 0 at x1.5 and +1 minute, random 100 % IS); LIVE not
met. The family is stopped; pre-registration draft written, HOLD not opened.

## Surprises and data notes
- The flow the paper identifies (into the fix) is not visible before 16:00:00 in 2016-21; the reversal after it is.
  Much of the reversal sits in 16:00-16:05 (inside the post-2015 5-minute fix window, 15:57:30-16:02:30), which a
  bot can only take with a market order right after 16:00:00; +1 minute keeps it (IS +6.80, VAL +1.50 per trade).
- The S_us signal (US alone) beats the paper's relative signal everywhere: consistent with the paper's Table 3 (the
  US flow is 4x EUR/JPY and 20-40x the others).
- Effects decay between IS and VAL by ~4x, like round 3 F1; USDJPY flips in VAL.
- Month-end calendar: last England business day (Good Friday and the August bank holiday move T). Jan 2016 is dropped
  (no Dec 2015 close in the panel): 71 IS months, 36 VAL.

## Directions that need the user
- **PRE check 2004-2015** for the candidate: needs one daily S&P 500 close series 2003-2015 (not in the repo; a new
  price series). The FX side is already there (Duka H1 bars end exactly at 16:00 and 17:00 London for EURUSD,
  USDJPY, GBPUSD). This would add ~70 gated events and settle the decay question before the demo.
- Fix-window tick data (IC ticks exist only for AUD/NZD and metals) for EURUSD/GBPUSD/USDJPY at 15:55-16:10 London
  on month-ends would show how much of the move is inside 16:00:00-16:02:30 and whether a 16:00 market order fills
  at the panel's spread.

## Scripts and outputs (scratchpad .../r12/I/)
common_I.py (calendar, signals, windows, costs), screen_I.py (I1/I2 72-cell mid screen; screen_I_shift0/1.txt,
.json), analyse_I.py (permutation null, P3, I3 baskets, random control; analyse_I.txt), analyse2_I.py (P4-P9;
analyse2_I.txt), gross_chosen.py (mid/cost split, per pair), lit/mp2013.pdf (Melvin & Prins working paper).
