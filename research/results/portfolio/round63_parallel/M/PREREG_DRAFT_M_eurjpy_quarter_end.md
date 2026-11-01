# PREREG DRAFT (round 63, stream M): EURJPY short into the quarter-end, 05:00-07:00 London. Tier DEMO at most

Draft written 2026-10-31 after 15:20 UTC (`date -u` gave 15:20:40 when the IS / VAL results were in). HOLD
(2025-01-01 onwards) has not been opened for this rule by any round. It was never registered: round 14 Q found it,
round 16 X listed it as F15, and round 24 C recomputed it as DEMO at IC's cost but did not draft it, because it failed
RELAXED on power. **The coordinator decides whether to open HOLD; this stream did not.**

## Why this draft exists
This rule meets the DEMO bar at the new venue's cost, which is the brief's condition for a draft. **The venue is not
what makes it pass.** At IC's own cost it is also DEMO (IS net +7.58, t 2.80; VAL +8.47, t 1.51), because the effect
(~9 bp) is ten times its cost (~0.9-1.1 bp). It is capped by count: 3 events a year, and about 5 in HOLD.

## Rule (fixed; the same as round 24 F15 and round 14 Q's leg)
- Symbol EURJPY, side **short**. Days: the last weekday (Monday-Friday, London date) of March, June and September.
  Holidays count; December is excluded (24 Dec-1 Jan).
- Entry at the price at 05:00 Europe/London (close of the M1 bar labelled 04:59 London). Exit at 07:00 London (close
  of bar 06:59). Prices may be at most 10 minutes stale, else no trade. No stop.
- Mechanism: quarter-end yen repatriation and hedge flows by Japanese holders, in Tokyo's afternoon (13:00-16:00
  JST) after the Tokyo fix. The side and window were chosen on 2004-15 (Dukascopy, round 14 Q: PRE n 36, mid +10.7 bp,
  t 3.7) before IS was examined.
- Cost (venue, stream M): ECN at 0.2 bp a side, plus half of IC's quoted spread at each quote, floored at 0.3 pip.
  IC's own cost (half spreads + 0.6 bp) is reported next to it.

## Numbers (IC M1 mid; t clustered by day = by event)
| era | n | mid bp | net at venue up (t) | net at venue lo | net at IC (t) | x1.5 | +1 min | sd | years > 0 |
|---|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 (round 14 Q, Dukascopy) | 36 | +10.7 (t 3.7) | - | - | - | - | - | - | - |
| IS 2016-21 | 18 | +8.65 | +7.76 (2.87) | +8.01 | +7.58 (2.80) | +7.31 | +8.83 | 11.5 | 6/6 |
| VAL 2022-24 | 9 | +9.55 | +8.66 (1.54) | +8.96 | +8.47 (1.51) | +8.21 | +9.23 | 16.8 | 3/3 |

- Random control: same clock on random non-quarter-end weekdays of the same era and weekday, 200 seeds. The rule beats
  100 % (IS) and 98.5 % (VAL).
- Correlation with C3: every F15 day is also a C3 exit day, because month-end is a gotobi day. C3 is flat by ~01:00
  UTC and F15 trades 04:00-06:00 UTC. Same-day correlation on the 27 days is -0.01.

## Power and what HOLD can show
- HOLD events up to the end of the IC cache (2026-09-24): 2025-03-31, 2025-06-30, 2025-09-30, 2026-03-31 and
  2026-06-30, so **n = 5**.
- Per-trade net Sharpe at VAL size is 0.515.
  - Expected HOLD t at the VAL size: 1.15 (power 1.17 on the 1.73-year convention).
  - At 0.65 of the VAL mid: 0.72.
- The probability that HOLD net > 0 is about 0.87 if the VAL size holds, and about 0.45 under no effect. **A HOLD
  look can reject, not confirm.** LIVE is out of reach: power 3 would need ~34 events, about 11 years.

## Bars (fixed now)
- Reject if the HOLD net per trade at the venue upper-bound cost is <= 0. The IC-cost net, x1.5, +1 min and the
  per-event values are reported but do not gate.
- If it is not rejected, it is a DEMO candidate for a small fixed-risk demo: 3 trades a year.
  - Stop rule: after 9 demo trades, stop if the pooled HOLD + demo mean net is <= 0.
  - Promotion to LIVE: only if the pooled HOLD + demo day-clustered net t is >= 2.5. At the VAL size that needs about 24 events, about 8 years.

## Code (sha256, first 16 hex; IS / VAL run; a HOLD run needs a copy of eng.py with T1 moved to 2026-09-25, nothing else)
- `research/results/portfolio/round63_parallel/M/code/eng.py` 061c0f3f1ed6eaee
- `research/results/portfolio/round63_parallel/M/code/rules.py` 3b87eb499b7a4c18 (rule `F15`)
- `research/results/portfolio/round63_parallel/M/code/run.py` 324cb37af5c73d01
- `research/m1.py` 3970b82bffee304c

Reproduce IS / VAL from the repo root: `PYTHONPATH=.:research/results/portfolio/round63_parallel/M/code
research/.venv/bin/python research/results/portfolio/round63_parallel/M/code/run.py F15`.

## Recommendation
Low value. It is a genuine, PRE-declared, stable effect, but with five HOLD events the look decides little, and the
demo would take years. Open HOLD only if the coordinator wants rare DEMO legs logged; do not spend a LIVE-tier
expectation on it.
