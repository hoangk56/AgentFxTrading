# Round 24: relaxed conditions (new data, a new-era split, a RELAXED tier)

2026-10-15. After round 23 the user wrote "cứ research thử xem, có thể nới rộng điều kiện" (go ahead and research, the
conditions may be relaxed). [round24_relaxed/BRIEF.md](round24_relaxed/BRIEF.md) fixed which conditions were relaxed
at 11:44 UTC, before any round-24 number. Three streams ran in parallel; the lead then opened HOLD once for two
RELAXED rules.

## Answer
- **No LIVE candidate.** C3 is still the only LIVE algorithm.
- **F3 passes its registered HOLD look at the RELAXED tier**: short EURUSD 11:00 -> 13:00 London, only on USD-TOP days.
  HOLD 2025-01..2026-09: n 117, net **+2.00 bp per trade (t 2.16)**, still positive at spread x1.5 (+1.98) and with
  both fills 1 minute late (+1.40). It is a RELAXED **demo** candidate only. It weakens: 2025 +4.02 (n 69), 2026 -0.91
  (n 48). Promotion to LIVE needs HOLD + demo pooled day-clustered net t >= 2.5, which at ~65 trades a year takes
  several years.
- **The FOMC-day dollar short (round 20 A4) is rejected at HOLD**: n 10, net -34.63 bp (t -2.36).
- Every 2024+ mechanism (spot BTC/ETH ETF NAV window, new NISA, US T+1, the "10 a.m. BTC dump") fails at DISCOVERY.
- Long Dukascopy history (2004-15) for AUD, NZD, gold and silver kills the Sydney V as a 21-year structure and the
  turn-of-year gold / USD rule; it supports the gold settlement big-day mechanism (round 12 L) but at a small net.

## What was relaxed (BRIEF items 1-4) and what was not
| relaxed | how |
|---|---|
| data | Dukascopy M1 and public flow tables could be fetched (stream B fetched AUDUSD, NZDUSD, XAUUSD, XAGUSD, GBPUSD and USDCAD 2004-15, ~109 MB, in research/data/duka/m1c/; stream A fetched Farside ETF flows) |
| new-era split | for mechanisms that exist only from 2023-24: DISCOVERY = start..2025-06, TEST = 2025-07..2026-09-24, each declared rule looks at TEST once |
| RELAXED tier | design-era net t >= 1.5; check-era net > 0 with t >= 1.0; x1.5 spread and +1 minute > 0; random control >= 80 %; check-era power >= 1.5; an economic mechanism. Demo only; never live without the LIVE bar or the registered promotion rule |
| HOLD | may be opened once per RELAXED candidate after a draft |
| holding | up to 20 trading days for declared seasonal / flow rules (swap charged) |

Not relaxed: sides from the mechanism or the source; every cell declared with a `date -u` time before its numbers;
executable costs; chance benchmarks for the number of cells; no parameter search on a check era.

## Stream A: 2024+ mechanisms on the new-era split ([STREAM_A.md](round24_relaxed/STREAM_A.md))
10 declared cells, 1 run (11:58 UTC). **None reaches any tier; every cell fails at DISCOVERY** (best positive DISCOVERY
net t 0.46; RELAXED needs 1.5).
| cell | DISCOVERY net (t) | TEST net (t) | reading |
|---|---|---|---|
| A1 BTC 15:00-16:00 ET, side = T-1 ETF flow | +1.6 (0.46) | +5.4 (2.07) | TEST sign is BTC momentum (A0b), not flow |
| A1g same, \|flow\| >= $300m | -2.7 | +9.7 (2.05) | same |
| A2 BTC 16:00-16:55 ET, reverse | -1.8 | -2.9 | none |
| A3 ETH, as A1 | -15.0 (-2.69) | -5.3 | IC ETH spread 23-26 bp |
| B1 USDJPY long into the 00:55 UTC fix after NISA order days | -4.7 | +5.0 (1.93) | positive only in TEST |
| B1b on the order day | +1.0 | +2.0 | none |
| B2 USDJPY short after the fix | -3.3 | -0.8 | none |
| B3 EURJPY, as B1 | +1.3 (0.22) | +5.1 (2.35) | positive only in TEST |
| C1 USD basket after US T+1 | -1.24 (-4.49) | -1.23 | no change from pre-T+1 |
| C2 BTC short 10:00-10:30 ET | -3.3 | +0.0 | none |

- Chance: max |t| of 10 normals, p95 2.82; the best TEST t is 2.35.
- Signing the BTC window by the **same day's** ETF flow (an untradable oracle) gives +3.1 bp (t 0.9) in DISCOVERY and
  -2.8 in TEST: creations and redemptions do not move BTC's 15:00-16:00 ET price.
- 25 of the 91 NISA NAV days are C3 gotobi days.

## Stream C: the existing effects under the RELAXED tier ([STREAM_C.md](round24_relaxed/STREAM_C.md))
60 rows recomputed on IS 2016-21 / VAL 2022-24 at IC's executable costs; 3 more scored from the record. No LIVE row.
| RELAXED survivor | IS net (t) | VAL net (t) | VAL-size power | note |
|---|---|---|---|---|
| F1 = E1, EURUSD short 11:00-13:00 London | +1.17 (3.29) | +1.35 (2.46) | 1.87 | registered; HOLD +0.64 (t 0.99) in round 13 |
| F2 EURUSD short 04:00-08:00 NY | +1.82 (3.57) | +1.85 (2.34) | 1.77 | same window as E1 |
| **F3 E1 on USD-TOP days** | +2.39 (3.29) | +3.01 (2.60) | 1.98 | HOLD opened (below) |
| F4 EURUSD short 12:45-13:00 London | +0.44 (2.41) | +0.52 (2.09) | 1.59 | |
| F5 the same, Fridays 12:50-13:00 | +1.13 (3.81) | +1.31 (2.74) | 2.08 | post hoc |
| F20 = J5c, AUDUSD before 10:00 Sydney | +0.44 (2.54) | +0.76 (3.77) | 2.86 | HOLD already failed (-0.25) |
| FOMC A4, short USD vs higher-rate legs on FOMC days | +21.62 (1.90) | +31.60 (2.40) | 1.82 | HOLD opened (below) |

- DEMO numbers without RELAXED: M5 (= registered gold settlement big days L; VAL-size power 1.29), F15 (EURJPY
  quarter-end), F18 (GBPJPY month-end), F28 (EURUSD after a USTEC shock, best of a 5,000-cell grid).
- The declared book F1 + F2 + F20 + A4 has VAL-size power 2.96, but two of its rows already have weak HOLD readings
  (E1 kept 0.47 of its VAL net, J5c went negative); at those retentions its expected HOLD power is ~0.7. Not drafted.
- Cost needed for LIVE: only F4 (+0.16 bp round trip), F5 (+0.07), F6, M1, F19-F21, M9, I7 and N1 have a positive one;
  all are below IC's cost (the 0.6 bp FX / metals commission alone is larger).
- Drafts: [PREREG_DRAFT_C_fomc_dollar_short.md](round24_relaxed/PREREG_DRAFT_C_fomc_dollar_short.md),
  [PREREG_DRAFT_C_ecb_window_variants.md](round24_relaxed/PREREG_DRAFT_C_ecb_window_variants.md) (recommends at most
  one HOLD look in the ECB family, F3).

## Stream B: long history with fetched data ([STREAM_B.md](round24_relaxed/STREAM_B.md))
20 declared cells (12:01 UTC); no 2025-26 price loaded. PRE = 2004-15 on Dukascopy (calibrated to IC on 2016: median
|mid difference| 0.07-0.17 bp for FX and gold, 1-minute return correlation 0.99).
| cell | PRE net (t) | IS net (t) | VAL net (t) | verdict |
|---|---|---|---|---|
| A1 AUD+NZD short 09:45-10:00 Sydney | -0.86 (-7.2) | -0.16 | -1.12 | none |
| A2 AUD+NZD long 10:00-10:15 Sydney | -0.94 (-6.8) | -0.18 | -0.31 | none |
| A3 J5c (AUDUSD, off-rollover days) | -0.61 (-3.8) | +0.44 (2.54) | +0.76 (3.77) | PRE confirms the failed HOLD |
| A4 gold settlement big days (L4-G-d) | 2009-15: +1.35 (0.98); 2004-08 placebo (no gold LETF): mid -0.77 | +3.76 (3.35) | +2.11 (1.70) | mechanism supported; RELAXED misses on power (1.29) |
| A5 same, top quintile | 2009-15: -0.05 | +1.19 | +0.89 | none |
| A6 / A8 gold short into the LBMA PM / AM fix | -0.21 / -0.23 | -0.36 / -0.56 | -0.08 / -0.75 | at cost |
| A7 silver short into the LBMA fix | -3.62 | -1.51 | -1.88 | cost 4.6 bp |
| A9 gold COMEX-open fade | -1.54 | -0.79 | -0.24 | absent in PRE |
| A10 / A11 China-session gold | -0.63 / -0.67 | +0.33 / -0.59 | +0.61 / -0.06 | none |
| A12 SGE placebo (no auction before 2016) | mid +0.22 | -0.67 | -0.33 | the SGE effect is the venue |
| A13 Wednesday carry, 9 pairs | -0.59 | -0.48 | +0.64 | round 3 does not reproduce |
| B4 turn of the year: gold long + USD short, 15 Dec to the last weekday of December (Seasonax, FOREX.com, Gulseven 2016, WGC 2023) | +26.8 (0.69), 6/12 years | **+99.8 (4.08)**, 6/6 | +3.7 (0.04) | DEMO numbers on IS / VAL; RELAXED fails (VAL t, power 0.03) |
| B2 gold only, same window | +34.3 (0.47) | +275.8 (15.8), n 6 | +38.7 (0.35) | RELAXED fails |
| B1 / B3 / C1 / C2 / C3 (USD legs only, gold in January, gold Sep + Nov, Santa Claus rally, January dollar rebound) | - | - | - | none |

- Chance: max |t| of 20 normals, median 2.12, p95 3.03. B2's t 15.8 rests on 6 yearly points and fails in PRE and
  VAL.
- **The Sydney V is not a 21-year structure**: pre-leg mid about -0.3 to +0.8 bp a year in 2004-10, 1-2 bp in 2011-22,
  0.9 bp in 2024. Dukascopy reproduces IC's 2016 V to the decimal, so this is not a quote artefact. The low-cost venue
  route of round 16 assumed a stable V; its value is lower than round 16 estimated.
- **Gold's turn-of-year gain is a 2016-2023 run** (2012-15 all negative, 2024 -168 bp). It explains round 23's N3b
  (gold around Christmas): the window is the turn of the year, not the festival. The draft
  [PREREG_DRAFT_B_turn_of_year.md](round24_relaxed/PREREG_DRAFT_B_turn_of_year.md) is not recommended; HOLD holds one
  event (December 2025), expected HOLD t 0.02-0.37. HOLD was not opened.
- **The gold autumn effect reversed**: +437 bp in 2004-10 (Baur's sample), -218 bp (t -2.8) in 2011-24.
- Dukascopy 503s are not always missing files: a fresh connection often serves the file.

## HOLD looks ([PREREG_R24_relaxed_hold.md](round24_relaxed/PREREG_R24_relaxed_hold.md))
Registered 12:19 UTC with code hashes in [round24_relaxed/prereg_code/](round24_relaxed/prereg_code/); run 12:19:39
UTC. Bar for each rule: reject if HOLD net per trade <= 0.
| rule | HOLD n | mid (t) | net (t) | x1.5 | +1 min | by year (net / n) | verdict |
|---|---|---|---|---|---|---|---|
| FOMC A4 | 10 | -33.64 (-2.29) | **-34.63 (-2.36)** | -34.68 | -35.02 | 2025 -7.34 / 4, 2026 -52.83 / 6 | rejected |
| F3 | 117 | +2.63 (2.85) | **+2.00 (2.16)** | +1.98 | +1.40 | 2025 +4.02 / 69, 2026 -0.91 / 48 | passes; RELAXED demo candidate |

- The pre-registration counted 8 A4 events; the rule traded 10 (the count rounded rates before comparing them with
  USD's). Rule and code did not change.
- F3 kept 0.66 of its VAL net (2.00 / 3.01), close to round 18's 0.65 for declared rules. E1, which F3 filters, had
  HOLD net +0.64 (t 0.99): the USD-TOP filter tripled the HOLD net per trade.
- F3 against C3 (IS + VAL): daily correlation +0.051, monthly +0.101.
- F2, F4 and F5 HOLD stay closed.

## F3: the RELAXED demo candidate (rule and demo rules from the draft; nothing chosen here)
- Rule: short EURUSD at 11:00 London, cover at 13:00 London, Monday-Friday by the local date, 24 Dec-1 Jan out, only
  on days when U = mean of the USDJPY and USDCHF log returns from 18:00 New York on the previous weekday to 07:00
  London is >= the 67th percentile (linear) of U over the previous 250 trading days (>= 60). Quotes = close of the
  last M1 bar ending at or before the time.
- ~65 trades a year; demo account only, fixed small risk; at most one EURUSD position from the ECB family a day.
- Stop rule: after 60 demo trades, stop if HOLD + demo pooled net t <= -1.0, or if the realised mean round-trip cost
  exceeds 1.5 bp.
- Promotion (RELAXED -> LIVE): HOLD + demo pooled day-clustered net t >= 2.5 at the costs paid and net > 0 at spread
  x1.5, with at least 100 demo trades.
- No cBot was written and nothing was deployed.

## Forward data after 2026-09-24 ([PREREG_R24_forward.md](round24_relaxed/PREREG_R24_forward.md))
After this report the user chose to fetch data after 2026-09-24. Registered at 17:02 UTC before any fetch: F3 and E1
unchanged, IC M1 to 2026-09-24 then Dukascopy M1 (median |mid difference| vs IC 0.03-0.06 bp on August-September),
costs at IC's median spread for the minute + 0.6 bp; no gate (too few trades), a rolling log rerun as data accumulates.
| rule | FWD 2026-09-25..10-14 | HOLD + FWD |
|---|---|---|
| F3 | n 2, net -9.18 bp (10-01 -30.9, 10-07 +12.5) | n 119, net +1.81 (t 1.89) |
| E1 | n 14, net -2.95 (t -0.82) | n 458, net +0.53 (t 0.83) |

Two F3 trades carry no information; the slice continues F3's 2026 weakness.

## What this says
- Relaxing the bar does not create a new mechanism. The only survivor after HOLD is a filtered version of the ECB-fix
  window that E1 already trades, and it is fading in 2026.
- The durable-looking FOMC dollar short failed out of sample in 2025-26, when the rate ranking of its legs changed.
- The 2024+ flow mechanisms (crypto ETFs, NISA, T+1) show no price direction in their discovery era.
- The long history removes two hopes of earlier rounds (a stable Sydney V for a cheaper venue; a turn-of-year
  seasonal) and confirms one mechanism (gold settlement big days appear only once gold leveraged ETFs exist).

## Needs the user
- Whether to run F3 (and E1) on the demo account with the stop and promotion rules above. A cBot would be needed.
- Data after 2026-09-24: chosen by the user; first slice read (above). Rerun `fwd_r24.py` with a later date as data
  accumulates (December 2026 for the turn-of-year rule, the Sydney V after 2024 need their own registration).
- The low-cost venue route (round 16): its value is lower now that the Sydney V is known to start only around 2011.

## Files
- [round24_relaxed/](round24_relaxed/): BRIEF.md; HYPOTHESES_A/B/C.md; STREAM_A/B/C.md; PREREG_DRAFT_B_turn_of_year.md,
  PREREG_DRAFT_C_fomc_dollar_short.md, PREREG_DRAFT_C_ecb_window_variants.md; PREREG_R24_relaxed_hold.md and
  prereg_code/ (hashed HOLD code and outputs).
- Fetched data: research/data/duka/m1c/ (git-ignored).
- Scripts: session scratchpad `r24/A`, `r24/B`, `r24/C`, `r24/lead` (not kept).
