# Round 27: gold's round-number cascade with resting stops, and the direction of venue-open jumps

2026-10-17 (UTC). Same task and bars as rounds 25-26. [round27_levels_opens/BRIEF.md](round27_levels_opens/BRIEF.md)
fixed the two streams at 21:04 UTC, before any round-27 number; tick fill model from round 26. HOLD was never loaded.

## Answer
- **No LIVE candidate.** C3 is still the only LIVE algorithm.
- **New DEMO-tier candidate: gold continues after it breaks a fresh $50 level** (G1-XAU50: resting stop at the level
  + half a spread, exit after 30 minutes). IS 2016-21 net **+5.99 bp per trade (t 2.66)**, VAL 2022-24 **+3.27 (t
  1.81)**, **9 of 9 years positive**, PRE 2004-15 at minute level +5.35 (t 3.12), random level grids beaten 96 % / 99.5
  %, $5 half levels negative, positive at spread x1.5 and with both fills a minute late, C3 daily correlation -0.008.
  It meets every LIVE bar except power: ~45-62 trades a year give VAL-size power 1.45 against 3. The 30-minute hold
  was picked after looking (the declared 60-minute hold missed the VAL random control by 0.01). **HOLD not opened**
  (see "Next").
- **The effect is a dose response in level size**, monotone in IS, VAL and PRE: ordinary $10 levels (80 % of breaks)
  carry ~0, $50 levels +7-8 bp mid in IS and +3-5 in VAL, $100 levels +8-9 in IS. Shifting the grid by $3-7 removes
  it. The resting stop does not find a fast cascade at $10 levels (+0.35 bp in the first 5 minutes).
- **V: the opening move at venue clocks carries information at mid beyond chance, nothing after cost.** Two cells
  (fade the European cash open in US30 / UK100) meet the DEMO numbers but are within chance and carried by March-April
  2020: drafted, not registered.

## G. Gold's round-number cascade on ticks ([STREAM_G.md](round27_levels_opens/STREAM_G.md))
384 cells declared at 21:23 UTC ([HYPOTHESES_G.md](round27_levels_opens/HYPOTHESES_G.md)): G1 resting stops beyond
fresh $10 levels (offsets 0 / 0.5 / 1 spread, exits 5-60 min, with / without a protective stop, dose $10 / $50 / $100,
first vs repeat touch), G2 the first-touch fade, silver and platinum as secondary instruments, $5 and 200 random-offset
placebos, a minute-level PRE replica on Dukascopy 2004-15. A G2 side bug found while reading the first results was
fixed and G2 rerun (two synthetic tests added); an independent per-tick re-simulation of 8 sessions matched exactly.

| cell | mid IS / VAL (t) | net IS / VAL (t), 250 ms | PRE (minute) | power IS / VAL | $5 placebo IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| G1 all $10 levels, c 0.5, 60 min (declared primary) | +2.44 (2.87) / +1.54 (1.83) | +0.66 (0.76) / +0.49 (0.58) | +1.66 (2.12) | 0.42 / 0.43 | -3.29 / -2.29 | 1.00 / 1.00 | fails |
| **G1 $50 levels, c 0.5, 30 min (draft)** | +7.72 (3.41) / +4.29 (2.37) | **+5.99 (2.66) / +3.27 (1.81)** | +5.35 (3.12) | 1.52 / **1.45** | -4.86 / -0.85 | 0.96 / 0.995 | DEMO numbers; LIVE but for power |
| G1 $50, c 1, 15 min | +7.21 / +3.47 | +5.34 (3.32) / +2.43 (1.70) | +4.85 (3.32) | 1.81 / 1.34 | -3.87 / -1.54 | 0.96 / 1.00 | DEMO numbers |
| G1 $100 levels, c 1, 15 min | +8.73 (5.56) / +3.48 | +6.93 (4.49) / +2.45 (1.08) | - | 2.41 / 0.82 | -5.09 / -2.08 | 0.97 / 0.65 | fails VAL |
| G1 repeat touches, c 1, 30 min | +5.53 / +2.23 | +3.89 (2.43) / +1.21 | - | 1.32 / 0.79 | - | 1.00 / 0.96 | DEMO numbers |
| G2 first-touch fade, $10, 60 min | -2.41 / -1.49 | -5.08 (-5.90) / -3.20 | -4.62 | < 0 | - | 0.00 / 0.04 | fails (mirror of G1) |
| silver $0.50 / $1, platinum $10 | ~-2 to 0 | -5 to -32 | < 0 | < 0 | - | - | fail (no barrier in silver; platinum costs 20-35 bp) |

- 18 G1 cells meet the DEMO numbers (13 at $50 levels, 5 on repeat touches); all are net > 0 at spread x1.5 and +1
  minute. Chance: the best IS mid t 5.56 is beyond every one of 1,000 per-day sign-flip draws (p95 3.11); the ten best
  IS net t are all $50 / $100 cells.
- G1-XAU50 by year (net bp): 2016 +4.84, 2017 +4.86, 2018 +6.17, 2019 +0.19, 2020 +8.26, 2021 +8.45, 2022 +2.28,
  2023 +5.24, 2024 +3.04. Without March-April 2020 IS +6.09 (t 2.66). The payoff is a right tail (median trade ~0;
  trimmed at 1 / 99 %: +4.36 / +3.27). Downward breaks carried IS (+11.85 vs +1.33 up; not declared), VAL more even
  (+3.71 / +2.81). Draft: [PREREG_DRAFT_G_gold_round50_cascade.md](round27_levels_opens/PREREG_DRAFT_G_gold_round50_cascade.md)
  (expected ~107 HOLD trades; expected HOLD t 1.45 at the VAL size, 0.94 at 0.65 of it).
- Fill facts (gold, 250 ms): slippage beyond the stop median +0.3 bp (p90 2.5-3); spread-only triggers 13-18 %; a
  "250 ms" bot fills ~415 ms after the trigger; 0 vs 1,000 ms changes the median by 0.08 bp. Execution is not the
  constraint; the event count is.

## V. Direction of venue-open jumps ([STREAM_V.md](round27_levels_opens/STREAM_V.md))
3,924 cells declared at 21:23 UTC ([HYPOTHESES_V.md](round27_levels_opens/HYPOTHESES_V.md)): 8 clocks (SHFE/SGE day
open, afternoon reopen, night session, CNY fix, European cash opens, 07:00 New Zealand, the 15:50 NY imbalance,
settlement minutes) x tick sets x follow / fade, w 15 / 60 s, exits 5-60 min, holiday and shifted-clock placebos.

| cell | n IS / VAL | net IS / VAL (t) | power IS / VAL | shifted -30 / +30 (IS) | verdict |
|---|---|---|---|---|---|
| EU-open US30 fade, w60 k4, 15 min | 59 / 14 | +9.26 (2.23) / +4.65 (0.85) | 1.20 / 0.65 | +0.24 / -4.03 | DEMO numbers, within chance |
| EU-open UK100 fade (minute level) | 42 / 14 | +13.15 (2.12) / +17.07 (2.40) | 1.14 / 1.82 | -1.71 / +6.10 | DEMO numbers, within chance |
| CN afternoon gold follow, w15 k4, 60 min | 66 / 27 | +5.48 (1.76) / +3.63 (1.15) | 0.94 / 0.87 | -5.55 / -0.62 | fails (IS t) |
| NY imbalance US30 follow, stop | 244 / 111 | +3.56 (2.13) / -2.87 (-2.69) | 1.15 / < 0 | - | fails (reverses in VAL) |
| 07:00 NZ follow (primary) | 235 / 78 | -2.80 / -1.47 | < 0 | - | fails; IS-only reversal at mid |
| settlement windows, metals fade | 2,419 / 1,225 | -1.99 / -1.87 (mid +0.78, t 2.9 / 2.2) | < 0 | - | real at mid, below cost |

- Chance: K = 3,924; best IS net t 2.23 is below the sign-flip null's median for the maximum (2.31, p 0.57); the max
  |IS mid t| 4.41 is beyond chance (p 0.009): direction carries information at mid (mostly the 07:00 NZ reversal and
  the metals settlement reversal) but none survives cost. The two EU-open cells: 9-12 opens of March-April 2020 plus
  2018-02-06 carry 67-77 % of each IS sum; USTEC with the same spec is -7.99 bp in VAL. Draft
  [PREREG_DRAFT_V_euopen_index_fade.md](round27_levels_opens/PREREG_DRAFT_V_euopen_index_fade.md), not registered.
- Facts: the 07:00 New Zealand spike survives NZ holidays and vanishes on Saturdays (a liquidity-provider day roll, not
  a venue); the 13:00 UTC move is New York's, not Shanghai's (it continued during the 2020 SHFE night-session
  suspension); IC has no quotes at 15:50 ET or at the settlement minutes on NYSE / CME holidays.

## What this says
- Gold's round levels behave like the order clusters Osler described, but only at the levels most traders watch ($50
  and $100), and the effect is a slow 15-60-minute continuation with a right tail, not a seconds-long cascade.
- One instrument gives ~60 such breaks a year: power 1.45. A LIVE algorithm on this mechanism needs the same effect at
  the major round levels of several other instruments (independent events), which is round 28's test.
- Venue clocks are the familiar story: direction at mid, cost after.

## Next (round 28)
The gold rule's HOLD stays closed for now: round 28 tests the same mechanism, with a salience rule declared before any
number, on the major round levels of the other IC symbols (FX majors and crosses, US / European / Asian indices, BTC,
oil). If a pooled book meets LIVE on IS / VAL with power >= 3, it is registered and HOLD is opened once for the whole
book; if not, the gold-only rule is registered as a DEMO candidate and its HOLD is opened once.

## Needs the user
- A cBot and a demo account slot for the gold $50 rule if it ends as a DEMO candidate (~60 trades a year; a demo alone
  needs ~5 years to reach pooled t 2.5).
- Dukascopy gold ticks 2004-15 for a tick-level PRE (low priority: the minute-level PRE already agrees).
- From stream V (low prior): Dukascopy index M1 2004-15 for a PRE of the EU-open fade; IC ticks for UK100 / DE40.

## Files
- [round27_levels_opens/](round27_levels_opens/): BRIEF.md, HYPOTHESES_G.md (with the bug-fix addendum),
  HYPOTHESES_V.md, STREAM_G.md, STREAM_V.md, PREREG_DRAFT_G_gold_round50_cascade.md,
  PREREG_DRAFT_V_euopen_index_fade.md.
- Scripts: session scratchpad `r27/G`, `r27/V` (not kept); reusable venue calendars in `r25/shared/cal/`.
