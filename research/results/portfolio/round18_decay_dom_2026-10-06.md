# Round 18: which effects do not decay, and calendar day-of-month clocks (2026-10-06)

Two streams from one brief ([round18_decay_dom/BRIEF.md](round18_decay_dom/BRIEF.md)); hypotheses with `date -u`
times before their numbers (`HYPOTHESES_A/B.md`), write-ups `STREAM_A/B.md`, in [round18_decay_dom/](round18_decay_dom/).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** The round's main result is about method: **how
a rule was found predicts its holdout retention; its 2016-24 trend does not.**

## A. Decay forensics (49 series: the ~45 effects of round 16's STREAM_X table, C3 in bp and in R)
- Rebuilds match their sources (E1 +1.80 / +1.97 bp, gold big days +4.74 / +3.14, SGE +0.91 / +0.70, rule I +6.73 net).
- Trend classes over 2016-24: 22 flat, 5 decaying, 22 unclear in bp (29 / 5 by per-trade Sharpe). Nine yearly means
  cannot separate slow decay from noise: the tests only flag effects that had already collapsed from IS to VAL
  (GBPUSD month-end WM/R, rule I, JP225 after the Tokyo close, ...).
- **Trend did not predict the registered rules' HOLD retention** (Spearman +0.26 on the bp trend, -0.20 on the
  Sharpe trend; every published HOLD falls inside its wide 90 % interval). **How the rule was found did** (descriptive,
  n = 6; a perfect 3-vs-3 split has chance ~1 in 20):

| rule | found how | HOLD / VAL retention |
|---|---|---|
| C3 gotobi basket | declared from the mechanism, PRE-confirmed | 1.03 (bp) |
| L4-G-d gold settlement big days | gate declared before numbers, mechanism from round 6 | 0.81 |
| E1 EURUSD 11-13 London | side fixed in PRE 2004-15 | 0.65 |
| J5c AUDUSD Sydney off-rollover | cost filter chosen post hoc with VAL in view | 0.31 |
| I month-end post-fix USD | best of 27 baskets with VAL in view | 0.24 |
| M1 month-end USD (round 3) | from a 90k-cell scan | 0.19 (R) |

- **2024 was a common low year** (post hoc): 35 of 49 series were below their 2016-23 mean (mean z -0.88; the series
  overlap). The Sydney V legs show it most (z -3.1 to -3.6, the lowest year since 2016, before HOLD); J5c's HOLD
  (+0.48 bp) continues its 2024 level (+0.68). At the 2024 level, round 16's low-cost venue route falls to power 2.36
  (Sydney pre-leg), 1.41 (J5c), below 0 (post-leg). Not hit in 2024: C3 (R), gold big days, M1.
- **C3 is the only effect flat on every reading** (2004-24 trend -0.07 bp/yr, t -1.3; in R ~0).
- No effect reaches power 3 at IC's costs on its forecast size except two already ruled out (the AUS200 10:10 drop,
  not executable; J5c, rejected in HOLD). Next best at IC: USTEC leveraged-ETF close, US30 post-close fade, USDJPY
  16-17 New York, C3: power 1.4-2.4.
- **Demo arithmetic:** the forecasts favour the gold big-day demo slightly (flat Sharpe trend, HOLD +2.54 bp mid,
  per-trade net Sharpe ~0.13), but at IC's costs a demo alone needs 8.5-10 years to reach t 2; E1 needs 5-24 years.
  Neither demo can confirm within two years.

## B. Calendar day-of-month x clock windows (631,915 cells, PRE discovery)
- Day types: calendar day 1-31, the n-th last calendar day, and "day d or the previous business day" (payment
  convention), on round 13 M's symbols, windows and clocks. C3 exclusions on JPY pairs (gotobi dates, Tokyo-fix hours);
  non-JPY cells mostly on gotobi dates or next to the Tokyo fix were information only.
- **None.** PRE max |t| 5.73 vs a null 95th percentile of 5.55 (that cell is -0.15 bp in IS). Top-500: 19 IS
  confirmations vs a null median of 11 / 95th percentile 22; of the eligible ones, 4 / 319 confirm and none holds in
  VAL. Calendar-day cells are no more stable than business-day cells; both are noise (PRE-IS t correlation 0.06-0.08
  against 0.36 for every-day clock cells).
- Information only: the USD strengthened in the European morning on the 15th across USD pairs (6-pair basket net IS
  +3.73, t 1.89 / VAL +7.69, t 2.08; PRE +2.74), not on other gotobi days; post hoc, within the family's chance range,
  mechanism unknown (payroll, coupon, tax or CPI week), expected HOLD t ~1.6. Not a candidate.

## What this says
- **The holdout losses of rounds 3-13 are mostly the winner's curse of post-hoc picks, not time decay.** Rules
  declared from a mechanism, from the literature or from 2004-15 kept 65-103 % of their size; picks made with VAL in
  view kept 19-31 %. A future pre-registration should expect about a quarter of the VAL size for a post-hoc pick.
- **Calendar dates add nothing beyond business-day types**; the stable structure in FX is the every-day clock.
- **Venue route weaker than it looked:** the Sydney V was at its lowest in 2024.

## Directions that need the user's decision
- Demo of the gold big-day rule or E1: affordable as a measurement of real spreads, but neither can confirm within two
  years at IC's costs.
- A US release calendar for 2004-24 (CPI dates) to separate a CPI-week effect from the 15th (low priority).
- Unchanged from rounds 15-16: Dukascopy M1 2004-15 for more symbols; a cheaper venue (now with the 2024 caveat);
  data after 2026-09-24.

## Process and disclosures
- HOLD was not loaded by the streams; published HOLD numbers were used as numbers only. Stream A floored each yearly
  standard error at half the pooled sd / sqrt(n) (disclosed in STREAM_A, not in its hypotheses file) and added two
  timestamped post-hoc readings (volatility-free Sharpe trend, the 2024 dip).
- Scripts and outputs in the scratchpad (`r18/A`, `r18/B`). Nothing in `research/` code was edited.
