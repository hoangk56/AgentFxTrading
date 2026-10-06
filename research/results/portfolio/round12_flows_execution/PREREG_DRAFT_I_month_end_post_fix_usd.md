# PREREG DRAFT (stream I, round 12): month-end post-fix USD reversal after large US equity months

Draft written 2026-10-06 ~01:10 UTC by stream I. **Not registered. HOLD (2025-01-01 onwards) was not opened.** The
lead decides whether to register and run it. Bar targeted: **DEMO** (LIVE fails: VAL t 0.84 < 1.5).

## Mechanism and sources
Foreign holders of US equities hedge the USD exposure and reset the hedge once a month at the WM/R 16:00 London fix
on the last business day, sized by the month's equity return (Melvin & Prins 2015, J. Financial Markets 22: hedge
flow proportional to |equity return|, US flow ~$2.5bn per 1 %; the 15:00-16:00 move reverses 72 % by the next noon on
month-end days). After a month in which US equities rose, hedgers sell USD at the fix; the dealers who took the other
side lay the USD back off after the fix and USD recovers (and the reverse after a falling month). The side was fixed
from the papers before looking (HYPOTHESES_I.md, I2): trade **against** the predicted hedge flow after the fix.

## Rule (exact)
- Day T: the last weekday of the calendar month that is not an England bank holiday and not Dec 25 / Jan 1.
- Signal: r_US = ln(US500 mid at 16:00 New York on the business day before T / US500 mid at 16:00 New York on the last
  business day of the previous month). If a quote is missing, use the last quote before that time (US holidays).
- Gate: trade only if |r_US| >= **2.45 %** (the IS 2016-21 median of |r_US| at month-end, fixed).
- Side: r_US > 0 -> buy USD: sell EURUSD, buy USDJPY, sell GBPUSD. r_US < 0 -> the opposite on the same three pairs.
- Entry: market orders at 16:00:00 London (DST-aware; i.e. right after the fix minute), 1x default lot each.
- Exit: market close at 17:00:00 London the same day. No stop needed for a 1-hour hold (an emergency stop at
  3 x ATR(H1, 20) is acceptable; it was not in the tests).
- One bot, 3 positions max, all opened and closed together. No overnight, no swap.

## Evidence (IS 2016-01..2021-12 / VAL 2022-01..2024-12; executable: actual spread at entry and exit minute + 0.6 bp)
| | IS | VAL |
|---|---|---|
| events (months) / trades | 36 / 108 | 24 / 72 |
| mid per trade, bp | +7.46 | +2.34 |
| cost per trade, bp | 0.69 | 0.66 |
| **net per trade, bp** | **+6.77** | **+1.68** |
| net per event (3 trades), bp; month-clustered t | +20.31, **t 3.79** | +5.03, t 0.84 |
| spread x1.5 / +1 minute / both (per trade) | +6.73 / +6.80 / +6.75 | +1.64 / +1.50 / +1.46 |
| years net > 0 | 6/6 | 2/3 (2023 -22.8 bp) |
| random-entry control (500 seeds, same side and pairs on random ordinary business days, same window) | beats 100 % | beats 86 % (pooled IS+VAL 100 %) |
| per pair net per trade (EURUSD / USDJPY / GBPUSD) | +8.83 / +3.85 / +7.63 | +2.85 / -1.41 / +3.58 |
| gate at the IS 33rd / 67th percentile instead (per trade) | +5.22 (t 3.18) / +6.79 (t 2.88) | -0.37 / +2.73 |
| US-up months / US-down months, per event | +23.7 (t 4.6, n 27) / +10.0 (t 0.7, n 9) | +8.7 (t 1.2, n 14) / -0.1 (n 10) |

- Ordinary-day placebo (same rule, 21-business-day US return, all other days except the first 2 and last 3 business
  days of a month): IS -0.83 bp per trade (t -2.05, the opposite sign), VAL +0.67 (t 1.03). The effect is month-end
  specific in IS.
- Correlation with C3 (IS + VAL): daily -0.05, monthly +0.01.
- Per-trade Sharpe IS 0.544, VAL ~0.13. Power: IS Sharpe x sqrt(HOLD trades ~31) = 3.0 on trades, 2.0 on
  month-clustered events (per-event Sharpe 0.63, ~10 HOLD events). On VAL's Sharpe (per event ~0.17) the expected
  HOLD t is ~0.5: **HOLD alone cannot confirm or reject it**; the demo has to accumulate.

## Multiple testing (disclosed)
72 mid cells (I1 54 + I2 18) were screened, then 27 basket cells (9 cells with IS mid t >= 2 x 3 variants: all,
gated, size-scaled). This cell is the best of the 27 by IS t; the I2 cell and the gate variant were both declared
before any number, but VAL was in view when it was picked (three of the 27 had IS t >= 2 and VAL > 0, all I2 16:00-17:00 or
16:05-17:00). Chance: permutation null flipping sides per month, shared by all 27 basket cells: max |t| 95 % = 3.11,
the chosen gross IS t = 4.17 (p 0.002). Over the 72 mid cells the 95 % max is 3.52; this cell ungated over 7 pairs
was IS t 3.12 there (not beyond chance alone). Threshold sensitivity was checked post hoc (above).

## Known weaknesses
- Decay: VAL per-trade net is a quarter of IS, USDJPY is negative in VAL, 2023 lost. Round 3's F1 (unconditional
  fade of the into-fix move) decayed the same way from 2021; this cell agrees with F1's side on 45 % of trades and is
  positive in IS both when it agrees (+9.4) and when it does not (+4.6), but in VAL only when it agrees (+4.1 / -0.6).
- The paper's own into-fix leg (15:00-16:00 on T, S_rel) is absent in IS (-1.14 bp, t -0.54), so the reversal is of
  a flow that is not visible before 16:00:00 in this data (much of it is in 16:00-16:05, the fix window runs to
  16:02:30; 16:05-17:00 alone keeps IS +4.59 per trade, t 2.83, VAL +0.36).
- A 2026 practitioner replication (Feb 2015-Jul 2026) reports a significant 16:03-17:00 post-fix reversal on S&P
  month-to-date returns; its sample overlaps our HOLD, so the literature has "seen" the HOLD period (our data has not).
- No PRE (2004-15) check: the panel has no equity index before 2016. Duka H1/M1 FX covers the FX side; the missing
  piece is one daily S&P 500 close series 2003-2015 (a user decision, not fetched).

## Registration items for the lead
- Bar: DEMO. Pass on HOLD: net per trade > 0 at actual spreads, with the IS-fixed threshold; report t month-clustered.
- Expected HOLD sample: ~10 events (~31 trades) in 2025-01..2026-09 (half the 12 month-ends a year pass the gate).
- Expected demo: ~6 events (~18 trades) a year.
- Promotion: HOLD + demo pooled month-clustered t >= 2.5.
- Stop rule: stop the demo if, after >= 12 pooled (HOLD + demo) events, the pooled per-event mean is <= 0, or at
  any time the pooled t < -1.5.
