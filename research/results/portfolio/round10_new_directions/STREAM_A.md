# Round 10, stream A: Asian benchmark and venue-session flows, with venue-holiday placebos

2026-10-05. Hypotheses (written before computing, post hoc parts marked):
research/results/portfolio/round10_new_directions/HYPOTHESES_A.md. HOLD (2025+) was never loaded: the shared panel
ends 2024-12-31, and PRE is Dukascopy H1 2004-2015.

**Verdict: no candidate. No PREREG draft.** 0 of 223 declared cells is net > 0 in both IS and VAL. The one sharp
venue-linked flow (XAU rises during the SGE morning benchmark auction) is real, but its sign is the opposite of the
ex-ante side and it is 0.3-0.65 bp below cost. The one post hoc rule that met DEMO numbers on IS/VAL (short gold in
Asian hours on Chinese holidays) failed its pre-written PRE 2004-2015 check, losing at t -3.3.

## Method
- Panel mid/spr per minute, p(T) = close of the bar ending at T, forward-filled for up to 10 min. Each event is one
  trade per day per symbol, so t is per UTC day.
- Day types: OPEN = venue trading day, HOL = venue-holiday weekday on which IC quotes. Calendars from `holidays`
  0.105 financial calendars (XSHG for SGE/SHFE/INE, XKRX, XTAI, XSES, XJPX, XHKG, XNYS, XLON) and country calendars
  (India, Indonesia, UK-England, China for PRE). Chinese night sessions are HOL on the eve of a holiday and during
  the SHFE suspension (2020-02-03..05-05).
- Executable: half spread at entry + half at exit (panel spread at those minutes) + 0.6 bp for FX/metals. Also
  spread x1.5 and +1 minute.
- Time placebos at T +-10/30/60, recomputing conditional sides at the shifted time. Chance benchmark: per-day sign
  flip shared by all cells, 1,000 permutations.

Cost at the event minutes (median spread IS/VAL, bp): XAU 0.84/0.44 at 02:15 (round trip incl. commission, mean:
1.6/1.05). XAG 4.1/4.4. XTI 5.2/3.5. XBR 4.6/2.7. NZD 0.57/0.51. AUD 0.29/0.00. USDJPY 0.10/0.07.

## Results

| hypothesis (source) | where | IS mid bp (t) / VAL mid (t) | HOL mid, diff t | cost IS/VAL | net IS / VAL (t) | power | verdict |
|---|---|---|---|---|---|---|---|
| A1 SGE gold benchmark V: long into, short after (SGE 2016 notice) | XAU 02:15, post [0,30] short | -1.02 (-3.8) / -0.97 (-2.8) | +1.74, -4.2 | 1.6/1.05 | -2.6 / -2.0 | <0 | wrong sign: fails |
| same, pre leg [-30,0] long | XAU 02:15 | +0.21 (0.7) / -0.08 (-0.2) | -0.80, 1.4 | | <0 | <0 | fails |
| A1 flipped (post hoc diagnostic): long through the auction | XAU 02:15-02:23 | +0.93 (7.9) / +0.72 (4.5); 9/9 years > 0 | -0.47, 3.75 | 1.59/1.04 | -0.65 (-5.4) / -0.33 (-2.0) | -2.5 | real, 0.3-0.65 bp below cost |
| A1 PM auction / silver | XAU 06:15, XAG both | \|mid\| <= 1.9, \|t\| <= 2.9 (wrong sign) | | XAG ~4.7 | <0 | <0 | fails |
| A2-flow long after Chinese opens (China net buyer) | best XAU 01:00 [0,60] | +1.19 (2.2) / +0.45 (0.6) | -1.76, 2.5 | 1.65/1.07 | -0.46 / -0.61 | <0 | fails |
| A2-cont continuation of closure move at opens | best \|t\| XAG 12:00 [0,15] | -2.93 (-4.6) / +0.53 (0.8) | | 4.1/4.5 | <0 | <0 | reversal, not continuation; doesn't repeat in VAL |
| A2-close fade the last 30 min before Chinese closes | XAU 07:00 [0,30] | +1.21 (3.85) / +0.86 (1.8) | +0.41, 0.7 | 1.52/1.03 | -0.31 / -0.17 | -0.4 | not venue-driven (holiday same), below cost |
| A3 Platts MOC: long in SG window; fade after SG / London windows (Platts methodology) | XBR, XTI | in-window long VAL -3.8 (-2.8); fades \|t\| <= 1.5 | | 2.6-7.4 | all < 0 | <0 | fails |
| A4 Asian FX fixes/closes (TAIFX, JISDOR, KRW, INR, CNY: USD weak into; TWD close: CBC USD buying) | AUD, NZD, USDJPY | all \|mid\| <= 1.1 bp; ex-ante best TWD 08:00 USDJPY [-15,0] +0.28 (2.1) / +0.95 (3.95) | diff t 1.9 | 0.7 | -0.46 / +0.25 | <0 | fails |
| A5a JP225 SQ: fade the first 15 min | JP225 00:15-01:15 | +5.5 (1.1) / -5.3 (-0.75), n 70/36 | | 3.0/1.8 | +2.5 / -7.1 | ~0 | fails |
| A6 (post hoc window) long gold in the Chinese session | XAU 01:00-03:30 | +2.02 (2.8) / +1.70 (1.85) | -5.69, 5.6 | 1.65/1.06 | +0.37 (0.5) / +0.64 (0.7) | 0.35 | fails (net t ~0.5); XAG all < 0 |
| A7 (post hoc) short gold in Asian hours on Chinese holidays | XAU 01:00-04:30, CN-holiday weekdays (~17/yr) | +7.8 (4.3) / +7.3 (3.3) | OPEN -1.48, diff t 5.9 | 1.66/1.05 | **+6.1 (3.3) / +6.2 (2.8)**, 9/9 yrs, x1.5 +5.6/+6.0, +1 min +6.1/+5.6, random control 100 % | 1.9 | **fails its PRE check**: 2004-15 net -6.2 (t -3.3, n 206) |

## Best cell per family, cells tried, chance

| family | cells | best \|t_IS\| (cell, signed) | perm-null 95 % of max \|t\| | p |
|---|---|---|---|---|
| all declared | 223 | 6.24 (A1 XAU 02:15 [0,15] short, -6.24) | 3.61 | <0.001 |
| A1 | 24 | 6.24 (wrong sign) | 2.93 | <0.001 |
| A2-flow | 30 | 2.24 (XAU 01:00 [0,60]) | 2.99 | 0.38 |
| A2-cont | 30 | 4.61 (XAG 12:00 [0,15], wrong sign) | 2.98 | <0.001 |
| A2-close | 20 | 3.85 (XAU 07:00 [0,30]) | 2.94 | 0.003 |
| A3 | 10 | 1.51 | 2.69 | 0.63 |
| A4 | 108 | 3.86 (INR window USDJPY [-15,0], wrong sign) | 3.40 | 0.014 |
| A5a | 1 | 1.06 | 2.14 | 0.30 |
| post hoc: A1-flip 4, A6 18, A7 4 | 26 | A7 XAU +4.26 mid | | |

Several effects are beyond chance, but none of them is both on the ex-ante side and above cost. The ex-ante-side cells
with mid t_IS >= 2 and VAL > 0 are A1 [-60,0], A2-flow XAU 01:00 [0,60], A2-close XAU 07:00 (two windows) and A4
TWD/USDJPY [-15,0]. All of them are net < 0 in IS or VAL.

## Details worth keeping

1. **The SGE AM auction moves gold, the "wrong" way.** XAUUSD rises in the bars ending 02:16-02:23 UTC, the minutes
   of the Shanghai Gold Benchmark auction at 10:15 Beijing. The rise is +0.93 bp (t 7.9) IS and +0.72 (t 4.5) VAL,
   positive in all 9 years, absent on Chinese holidays (-0.47, diff t 3.75), and it does not revert in the next hour.
   It looks like auction demand passed through to London, not the pre-hedge-then-revert V of gotobi. The four months
   before the benchmark launched (2016-01-04..04-18, n 68) give +0.81 (t 1.4), too few to tell whether the benchmark
   created it or only coincides with it (the SHFE also breaks at 10:15). At executable prices it is below cost:
   -0.65 bp IS and -0.33 bp VAL, because the 0.6 bp commission alone takes most of the gross. Its gross per-trade
   Sharpe is ~0.2, and at most ~0.06 even with zero spread, so it cannot reach power 3. The PM auction (06:15) shows
   +0.3..0.45 bp. Silver rises at 02:15 too (VAL +1.3, t 2.9) against a ~4.7 bp round trip.
2. **Holiday-subset means scatter widely, which is how A7 fooled IS and VAL.** The same short on weekdays that are
   holidays only in Japan, Hong Kong, Korea or the US (not China) loses 5-12 bp per trade (t -2.1..-2.8). In PRE the
   Chinese-holiday short loses 6.2 bp (t -3.3); gold rose in Asian hours on all day types in the 2004-15 bull
   market. Day-clustered t on ~150 holiday days that come in multi-day blocks overstates significance. **Future
   holiday-placebo tests should cluster by holiday block, or use a placebo distribution built from other venues'
   holidays, not a per-day t.**
3. In PRE, gold's Asian morning drift is not specific to China: 02:00-03:00 UTC is +1.6 bp (t 6.2) on Chinese
   trading days and +1.7 on Chinese holidays. In 2016-24 the gap between trading days and holidays is large instead.
   That is consistent with a regime effect, or with item 2's noise.
4. Pitfalls: oil on Singapore/UK holidays (often Good Friday) shows -14..-24 bp means (n 38-51), which are IC quote
   artefacts when ICE/NYMEX are shut, so oil holiday placebos need Good Friday removed. AUDUSD's VAL median spread at
   the minute close is 0.0, so commission is the whole cost there. Before I fixed it, the time placebos of
   conditional-side cells reused the unshifted side, and the shifted window overlapping the signal window gave
   spurious |t| up to 34. Placebos must recompute the side at each shift.
5. A7's correlation with C3 (IS+VAL), for the record: daily -0.03, monthly -0.08. It is moot after the PRE failure.

## Files (scratchpad r10/A/)
- calendars.py, calendars.json, cn_pre.json: venue calendars
- ev.py: panel helpers; screen.py: all 223 declared cells → screen_cells.tsv (+ screen_g.npy, screen_O.npy)
- perm.py → perm_out.txt: chance benchmarks
- profile.py, minute_prof.py: 15-min and 1-min profiles (OPEN vs HOL)
- a6a7.py → a6a7_out.txt: A1-flip, A6, A7 on IS/VAL; a7_confirm.py → a7_confirm_out.txt: PRE check, venue
  placebos, random control, C3 correlation
