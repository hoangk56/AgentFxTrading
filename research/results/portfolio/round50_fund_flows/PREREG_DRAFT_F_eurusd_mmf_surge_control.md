# PREREG DRAFT (round 50, stream F): EURUSD long after a big H.6 retail money-fund surge (control cell)

Written 2026-10-30 09:20 UTC. **Status: not recommended. Do not open HOLD unless the lead overrides.** This cell was
declared in [HYPOTHESES_F.md](HYPOTHESES_F.md) as a control ("never a candidate"); it is drafted only because it meets
the DEMO numbers on IS / VAL and the brief asks for a draft whenever a cell does. HOLD was not opened.

## Rule (exactly as graded)
- Signal: Fed H.6 retail money funds `MMFGB_N.WM` (weekly NSA). Weekly residual r = dlog minus the mean dlog of the same
  calendar week in the 3 previous years. At each H.6 release (official dates, `releases/h6/releaseDates.json`),
  z = sum of r over the weeks first published by that release / (sd of r over the previous 156 weeks x sqrt(weeks)).
  Monthly era (all of HOLD): new weeks = week end <= last day of the previous month.
- Trade: z >= +1 long EURUSD, z <= -1 short; entry 13:05 ET on the release day (monthly era, 13:00 ET release; weekly
  era was next trading day 09:35 ET), exit next US trading day at the same clock (h1). Skip if entry or exit is a US
  federal / NYSE holiday. IC bid / ask, 0.6 bp commission, swap.
- Code: scratchpad `r50/F/scripts/run.py` (sha256 7e8b1610338e38e4f620cc86fccf2a14fe1cb1a46f32fc8b592c0122b5f80089),
  `parse_h6.py` (049b8bd319002ddabf1585317ce8a4771f56e4cd413662f1d56e63adc9263fb1); hashes via
  `python -m research.tools.prereg_hashes` still to be taken by the lead.

## Evidence
| era | net bp (t, n) | mid t | x1.5 / +1 min t | random (a; b) |
|---|---|---|---|---|
| PRE 2004-15 (weekly) | -3.1 (-0.67, 189) | | | |
| IS 2016-21 | +14.8 (2.35, 49); ex 2020-03/04 t 2.00; 5 / 6 IS years > 0 (7 / 8 with VAL) | 2.51 | 2.35 / 2.40 | 0.995; 0.995 |
| VAL 2022-24 (monthly) | +20.1 (1.78, 19), all in 2022-23 | 1.90 | 1.78 / 1.83 | 1.00; 0.96 |

## Why it is not recommended
- Declared as a control before any number, side "USD safe-haven reversal"; promoting it changes the role after the
  numbers.
- Cells tried: 8 candidates + 12 controls + 8 diagnostics. Best-of-12 control null for |IS mid t|: p95 2.84; this cell
  (2.51) is inside chance. PRE (2004-15, 189 trades) is negative.
- IS is the weekly era (10-day-old data, 1 new week); VAL and HOLD are monthly (4-5 weeks, up to 55 days old): a
  different signal.

## If the lead opens it anyway
- Bar: DEMO. Expected HOLD trades: 21 monthly releases x (19 / 36 in VAL, 0 / 12 in 2024) = ~0-11; HOLD t at the VAL
  per-trade Sharpe 0.408: ~1.35 at 11 trades. Pass: HOLD net > 0.
- Demo: ~3-6 trades a year, fixed small risk. Stop rule: cumulative net < -2 R after 10 demo trades. Promotion rule:
  HOLD + demo pooled t >= 2.5 (years at this rate).
