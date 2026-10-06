# PREREG draft (stream Y, round 17): US30 continuation after extreme 30-minute quote-flow imbalance in the US morning

Draft written 2026-10-06 02:51 UTC by stream Y. **Not registered; HOLD not opened.** It meets the DEMO numbers on
IS/VAL formally, but it is weak (see "Why the lead may decline"). The lead decides whether to register it.

## Rule (exact; parameters fixed on IS 2016-21)
- Symbol: US30 (IC). Ticks; minute grid; signal at each minute end t.
- OFI_30 = sum over the IC quote rows of the last 30 minutes of sign(dBid) + sign(dAsk) (Cont, Kukanov & Stoikov 2014
  OFI with unit depth; the IC cache has no sizes). z = OFI_30 / sqrt(mean of OFI_30^2 over all eligible minutes of the
  previous 28 calendar days).
- Window (HI, registered as Y3 before the data): weekdays, signal time in 08:30-11:00 New York time or 08:00-09:00
  London time. Every trade so far came from 09:43-10:56 New York, plus 2 from the London hour.
- Trigger: |z| >= 6.795 (the IS 99.9th percentile of |z| in the window). All 30 minutes of the window must have quotes.
- Side: sign(z) (continuation; Hasbrouck 1991, Love & Payne 2008: order flow after news is informative and persists).
- Entry at t + 1 s at the ask (long) / bid (short); exit at entry + 15 minutes at the bid / ask. One position at a time
  (signals inside an open trade are skipped). No swap (exits before 11:16 New York).
- Cost: actual tick bid/ask at both fills; no commission (index CFD).

## Numbers on IS / VAL (HOLD closed)
| | IS 2016-21 | VAL 2022-24 |
|---|---|---|
| trades (days) | 53 (32) | 10 (8) |
| trades a year | 8.8 | 3.3 |
| net bp per trade (day-clustered t) | +8.11 (2.11) | +10.07 (5.77) |
| spread x1.5 | +7.58 (1.97) | +9.93 (5.70) |
| entry +5 s / +30 s / +60 s | +7.49 / +6.19 / +7.29 (t 1.91 / 1.62 / 1.77) | +9.50 / +9.39 / +8.14 |
| per-trade Sharpe | 0.224 | 1.18 (10 trades) |
| power = Sharpe x sqrt(trades/yr x 1.73) | 0.87 | 2.8 |
| random entries (a): same NY half-hour + weekday, random day, side recomputed, 500 seeds | beats 100 % (ctrl -0.88) | beats 95.4 % (ctrl -0.73) |
| random entries (b): same day, random time in the window, side recomputed | beats 85.8 % (ctrl +3.31) | beats 94.4 % (ctrl +1.64) |
| VAL / IS ratio | | 1.24 |

By year (sum of net bp): 2016 +82 (7 trades), 2017 -10 (8), 2018 +95 (15), 2019 +21 (7), 2020 +244 (12), 2021 -2 (4),
2022 +37 (3), 2023 +61 (6), 2024 +3 (1). 7 of 9 years > 0. C3 correlation (IS+VAL): daily +0.05, monthly +0.05.

## Bar and counts
- DEMO bar: IS day-clustered t >= 2.0 (2.11), net > 0 in VAL (+10.07), beats >= 90 % of random entries (control (a):
  100 % / 95.4 %). Positive at spread x1.5 and +1 minute in both eras.
- Cells tried: 1,680 rule cells (7 symbols x 4 conditions x 4 k x 5 h x 3 cuts) x 4 latencies; this one was the IS
  best of the 60 US30 x HI cells. Best IS net t in the whole family: 2.68 (XAUUSD HI, fails VAL). With ~1,600 IS cells,
  max-of-K normals gives about 3.4-3.8, so **the IS t of 2.11 is inside chance for the family.**
- Expected HOLD (2025-01..2026-09, 1.73 years) trades: ~6 at the VAL rate, ~15 at the IS rate. Expected HOLD t on the
  VAL effect size with the pooled IS+VAL per-trade Sharpe (0.25): 0.6 (6 trades) to 1.0 (15 trades); with the VAL
  Sharpe (1.18, 10 trades, not reliable): 2.9.
- Demo: ~3-9 trades a year. Stop rule: stop after 30 demo trades if the pooled mean is <= 0, or at any time if 15
  consecutive trades sum below -150 bp. Promotion rule: HOLD + demo pooled day-clustered t >= 2.5.

## Why the lead may decline
1. Threshold knife edge in IS: at the IS P99 cut the same rule is -0.15 bp (t -0.17, 503 trades) and at P99.5
   -0.01 bp (251); only the 53 most extreme cases are positive in IS. VAL is positive at all three cuts (+1.51 t 1.53,
   +4.38 t 2.73, +10.07 t 5.77).
2. Two days carry IS: without 2018-02-06 IS is +6.43 (t 1.67); without 2020 +4.53 (t 1.44); without the two best days
   +2.42 bp per trade.
3. Post hoc PH1: the same rule on the 30-minute return z instead of OFI z loses in IS (-1.03 bp, t -0.25 at P99.9),
   so whatever there is lives in the signed count of quote moves on days when the US open is one-sided, not in the
   size of the move. PH2: on USTEC (the twin) it is +3.90 (t 1.27, 56 trades) in IS and has 1 VAL trade: no
   confirmation.
4. The trigger fired 10 times in VAL vs 53 in IS: in VAL the IC index quotes move both sides together almost always
   (corr(OFI, TR) 0.997 vs 0.976 in IS), which changes the distribution of OFI; the IS threshold may mean something
   else in HOLD.
5. Mechanism overlap: big-move days after the US open (round 8 S4b mirror; round 17 stream Z's US30/USTEC comparison).
   If stream Z registers a US open big-day rule, this is a second, rarer trigger of the same flow.
