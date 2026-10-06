# Round 22: triage of every residual idea from rounds 3-21, and declared tests of the best (2026-10-06)

One stream ([round22_residual/BRIEF.md](round22_residual/BRIEF.md)) read every report and STREAM file of rounds 3-21,
listed every idea left open, triaged them ([TRIAGE_R.md](round22_residual/TRIAGE_R.md)), and declared and tested the top
ones ([HYPOTHESES_R.md](round22_residual/HYPOTHESES_R.md) at 05:26 UTC, [STREAM_R.md](round22_residual/STREAM_R.md)).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened. The residual idea list that needs no user decision
is exhausted:** no open idea can reach LIVE power on the existing data even at its full reported size.

## Triage
~330 open lines, ~190 distinct ideas. Dropped: ~70 need a user decision (later data, cheaper venue, new symbols, paid
data, demos, a bar change); ~45 already tested in a later round; ~55 post hoc (evidence only from the data that
suggested them: the 15th-of-month USD, the Friday ECB slot, FOMC US30 close, J5c, gold on FOMC days, the US30 open-OFI
draft...); ~20 below cost with no new execution, or method notes. 11 survivors, none reaching power 3 at full size;
the top four were tested.

## Results (13 declared cells)
| idea (source) | best cell, net bp (t) PRE / IS / VAL | verdict |
|---|---|---|
| R1 equity premium in even FOMC-cycle weeks (Cieslak, Morse & Vissing-Jorgensen 2019) | US500 long even-week days: n/a / -0.55 (-0.15) / +0.24 (0.05); odd weeks earn as much | none |
| R2 next-day FX reversal on abnormally low volume (Cespa et al. 2022, RFS) | +1.37 (1.17) / -1.88 (-1.79) / -1.92 (-0.90); the low-minus-high interaction +3.12 (t 2.07) in PRE only | gone since 2016 (PRE overlaps the paper's sample) |
| R3 high-yielder into the Wednesday triple rollover (round 3 W1 lead) | -0.57 / -1.20 / +1.35; Wednesday minus other days ~0 | no Wednesday flow |
| R4 10-year auction concession in USDJPY (Lou, Yan & Zhang 2013) | -26.8 (-2.46) / +17.9 (1.61) / +29.4 (1.77) | sign flips between eras |

Chance: max of 13 |N(0,1)| 95th percentile 2.89; best |t| 2.46 (PRE, wrong sign). The pipeline reproduces E1 exactly.

## Process and disclosures
HOLD not loaded (panel, Dukascopy, event lists asserted before 2025). R2's volume proxy changes between eras
(Dukascopy volume before 2016, IC tick counts after; disclosed). R3/R4 were declared as information only for IS/VAL
because their relatives were seen in rounds 3-4; their test era is PRE. Scripts in the scratchpad (`r22/R`).
Nothing in `research/` code was edited.
