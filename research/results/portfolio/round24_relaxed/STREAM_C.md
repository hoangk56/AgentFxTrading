# Round 24, stream C: RELAXED re-evaluation of the effects that already exist

Written 2026-10-15 12:05-12:15 UTC. Rules declared in [HYPOTHESES_C.md](HYPOTHESES_C.md) (11:53-11:55 UTC) before any
number, plus Amendment 1 at 12:01 UTC (forward-only random control for data-selected rows; an F17 code bug fixed),
both disclosed. HOLD was never loaded (panel ends 2024-12-31; USDCNH cut at load). No new parameter was chosen.

## Answer
- **No LIVE row.** 60 rows recomputed on IS 2016-21 / VAL 2022-24 at IC's executable costs; 3 more (F26 PCA, F29
  Treasury auctions, I13 night premium) cannot be rebuilt because their rule was never recorded and are scored from
  the record (all fail).
- **RELAXED survivors: 7 rows, 2 mechanisms.**
  - The **ECB-fix EURUSD window**: F1 (= registered E1), F2 (04:00-08:00 NY), F3 (E1 on USD-TOP days), F4 (12:45-13:00
    London), F5 (Fridays 12:50-13:00), and F20 (= registered J5c, AUDUSD before 10:00 Sydney, whose HOLD already failed:
    net -0.25).
  - The **FOMC-day dollar short** (round 20 A4): IS net +21.6 (t 1.90), VAL +31.6 (t 2.40), VAL-size power 1.82.
- **DEMO numbers** (user's original bar) are met by F1-F5, F20, M5 (= registered L), and three old post-hoc / rare rows:
  F15 (EURJPY quarter-end, 3 a year), F18 (GBPJPY month-end 10:28 NY, VAL net t 0.77) and F28 (EURUSD after a USTEC
  shock, best of a 5,000-cell grid). None of the last three passes RELAXED (VAL-size power 0.59-1.15).
- **The declared book** (F1, F2, F20, A4; F3/F4/F5 dropped as subsets of F1): IS +0.209 R per active day (t 4.61), VAL
  +0.262 (t 3.89), **VAL-size power 2.96**, correlation with C3 +0.046 daily / +0.089 monthly. It looks close to LIVE,
  but two of its four rows already had their HOLD opened (E1 kept 0.47 of its VAL net, J5c went negative): at those
  measured retentions the book's expected HOLD power is **~0.7**.
- **Cost needed for LIVE**: only F4 (+0.16 bp round trip), F5 (+0.07), F6 (+0.03), M1 (+0.08), F20 (+0.73), F19
  (+1.04, Sydney pre-leg), F21 (+0.74), M9 (+1.54, silver LBMA), I7 (+1.02, ASX open; +1 min < 0) and N1a-c (+0.35-0.68) have a positive cost at
  which the VAL size would reach LIVE; all are below IC's actual cost (0.6 bp commission alone for FX / metals). Every
  other row has no cost at which it reaches LIVE (count- or sd-capped).
- Drafts: [PREREG_DRAFT_C_fomc_dollar_short.md](PREREG_DRAFT_C_fomc_dollar_short.md) and
  [PREREG_DRAFT_C_ecb_window_variants.md](PREREG_DRAFT_C_ecb_window_variants.md) (F2-F5, recommending at most one HOLD
  look, F3). No draft for F1 / F20 / M5 (registered, HOLD already opened) or for the book.

## Method (as declared)
- Panel `r23/shared/panel` (IC M1 mid / spread, bar-start labels). Price at X = close of the last bar ending at or
  before X, <= 10 min stale. Costs: half the actual spread at each quote + 0.6 bp (FX, metals) + swap per 17:00 NY
  rollover. x1.5 = half spreads x 1.5; +1 m = both quotes one minute later. t clustered by UTC entry day.
- Power = per-trade net Sharpe x sqrt(1.73 x trades/yr), on the VAL size (= expected HOLD t at the VAL size).
- Random control, 200 seeds: "time" (same days, both times shifted by a random -180..+180 min, side recomputed,
  rollover-hour draws dropped; forward-only +1..+180 for data-selected rows after Amendment 1) or "day" (event rules:
  random non-event days, same weekday and era).
- LIVE cost = min(IS mid - 2.5 SE, VAL mid - 1.5 SE, VAL mid - 3 sd / sqrt(1.73 n/yr)) on mid + swap.
- Chance: 60 rows, max |t| of 60 normals median 2.52, p95 3.34; best IS net t 4.34 (F18). These rows were all
  selected as real in earlier rounds, so the IS t's are not a fresh search; the VAL columns are the check.

## Full table (net bp per trade; t day-clustered; "rand" = % of random-entry seeds beaten; power VAL (IS); yrs+ = years
net > 0 of IS + VAL; tier = every tier whose numbers are met (RELAXED fails lists the failed RELAXED gates); LIVE cost = round
trip at which LIVE holds on the VAL size, actual IS / VAL cost in brackets)

| id | IS n | IS mid / net bp (t) | VAL n | VAL mid / net bp (t) | x1.5 IS/VAL | +1m IS/VAL | random IS/VAL % | power VAL (IS) | yrs+ | tier | RELAXED fails | LIVE cost rt bp (actual) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 1525 | +1.80 / +1.17 (+3.29) | 765 | +1.97 / +1.35 (+2.46) | +1.15 / +1.34 | +1.08 / +1.04 | 100 / 98 | +1.87 (+1.77) | 8/9 | DEMO+RELAXED | - | -0.20 (0.63 / 0.62) |
| F2 | 1525 | +2.46 / +1.82 (+3.57) | 765 | +2.48 / +1.85 (+2.34) | +1.79 / +1.84 | +1.61 / +1.33 | 100 / 98 | +1.77 (+1.92) | 9/9 | DEMO+RELAXED | - | -0.65 (0.64 / 0.63) |
| F3 | 381 | +3.02 / +2.39 (+3.29) | 207 | +3.63 / +3.01 (+2.60) | +2.38 / +3.00 | +2.29 / +2.66 | 100 / 100 | +1.98 (+1.77) | 9/9 | DEMO+RELAXED | - | -0.94 (0.63 / 0.62) |
| F4 | 1509 | +1.11 / +0.44 (+2.41) | 757 | +1.14 / +0.52 (+2.09) | +0.41 / +0.51 | +0.44 / +0.25 | 100 / 100 | +1.59 (+1.30) | 8/9 | DEMO+RELAXED | - | +0.16 (0.66 / 0.62) |
| F5 | 305 | +1.76 / +1.13 (+3.81) | 153 | +1.95 / +1.31 (+2.74) | +1.11 / +1.28 | +0.96 / +0.70 | 100 / 100 | +2.08 (+2.04) | 8/9 | DEMO+RELAXED | - | +0.07 (0.63 / 0.64) |
| F6 | 1506 | +0.73 / +0.08 (+0.58) | 755 | +0.85 / +0.21 (+1.04) | +0.06 / +0.20 | +0.17 / -0.11 | 100 / 100 | +0.79 (+0.31) | 5/9 | none | is_t,lat,power | +0.03 (0.65 / 0.64) |
| F7 | 1526 | +1.02 / +0.08 (+0.23) | 764 | +1.08 / +0.19 (+0.39) | -0.09 / +0.05 | -0.08 / +0.11 | 99 / 90 | +0.30 (+0.12) | 6/9 | none | is_t,val_t,x15,lat,power,mech | -0.87 (0.94 / 0.89) |
| F8 | 470 | +1.94 / +1.02 (+1.64) | 265 | +1.84 / +0.97 (+1.12) | +0.85 / +0.83 | +0.67 / +0.87 | 100 / 98 | +0.85 (+0.88) | 5/9 | none | power,mech | -1.56 (0.92 / 0.88) |
| F9 | 1525 | +0.69 / -0.62 (-3.12) | 765 | +0.58 / -0.72 (-1.97) | -0.97 / -1.07 | -0.28 / -0.83 | 94 / 72 | -1.49 (-1.68) | 0/9 | none | is_t,val_t,x15,lat,rand,power | -0.87 (1.31 / 1.30) |
| F10 | 1525 | +0.88 / +0.14 (+0.44) | 765 | +0.95 / +0.25 (+0.44) | +0.08 / +0.21 | +0.02 / +0.34 | 96 / 70 | +0.34 (+0.24) | 5/9 | none | is_t,val_t,rand,power | -1.32 (0.73 / 0.69) |
| F11 | 1525 | +0.92 / +0.06 (+0.16) | 765 | +1.01 / +0.12 (+0.18) | -0.06 / -0.03 | +0.10 / -0.32 | 99 / 96 | +0.14 (+0.09) | 5/9 | none | is_t,val_t,x15,lat,power | -1.57 (0.85 / 0.89) |
| F12 | 1418 | +1.65 / +0.41 (+0.82) | 714 | +1.43 / +0.34 (+0.46) | +0.09 / +0.09 | +0.42 / +0.65 | 70 / 49 | +0.35 (+0.44) | 5/9 | none | is_t,val_t,rand,power,mech | -1.48 (1.24 / 1.09) |
| F13 | 1218 | +2.12 / +0.94 (+1.39) | 611 | +1.72 / +0.63 (+0.68) | +0.65 / +0.38 | +1.01 / +0.67 | 80 / 46 | +0.52 (+0.75) | 7/9 | none | is_t,val_t,rand,power,mech | -1.93 (1.18 / 1.09) |
| F14 | 1526 | +1.76 / +0.90 (+1.86) | 765 | +1.06 / +0.17 (+0.23) | +0.77 / +0.03 | +1.00 / +0.08 | 100 / 45 | +0.17 (+1.00) | 5/9 | none | val_t,rand,power,mech | -1.98 (0.86 / 0.89) |
| F15 | 18 | +8.65 / +7.58 (+2.80) | 9 | +9.55 / +8.47 (+1.51) | +7.34 / +8.23 | +8.67 / +9.04 | 100 / 99 | +1.15 (+1.50) | 9/9 | DEMO | power | -12.49 (1.07 / 1.08) |
| F16 | 66 | +9.71 / +8.84 (+2.43) | 33 | +1.87 / +1.09 (+0.26) | +8.70 / +1.00 | +6.90 / +2.33 | 100 / 69 | +0.20 (+1.30) | 7/9 | none | val_t,rand,power | -14.75 (0.87 / 0.78) |
| F17 | 108 | +7.46 / +6.77 (+3.79) | 72 | +2.34 / +1.68 (+0.84) | +6.73 / +1.64 | +6.80 / +1.50 | 100 / 57 | +0.90 (+3.04) | 8/9 | none | val_t,rand,power | -3.26 (0.69 / 0.66) |
| F18 | 66 | +3.51 / +2.48 (+4.34) | 33 | +1.58 / +0.47 (+0.77) | +2.26 / +0.21 | +1.09 / +0.61 | 100 / 99 | +0.59 (+2.33) | 8/9 | DEMO | val_t,power | -0.82 (1.04 / 1.11) |
| F19 | 3042 | +1.65 / -0.11 (-0.86) | 1524 | +1.48 / -0.96 (-5.73) | -0.69 / -1.87 | -0.35 / -1.14 | 100 / 62 | -5.69 (-0.60) | 3/9 | none | is_t,val_t,x15,lat,rand,power | +1.04 (1.76 / 2.43) |
| F20 | 1020 | +1.54 / +0.44 (+2.54) | 510 | +1.53 / +0.76 (+3.77) | +0.19 / +0.68 | +0.34 / +0.41 | 100 / 100 | +2.86 (+1.36) | 8/9 | DEMO+RELAXED | - | +0.73 (1.10 / 0.77) |
| F21 | 3040 | +1.28 / -0.18 (-1.09) | 1524 | +1.44 / -0.29 (-1.25) | -0.62 / -0.86 | -0.34 / -0.48 | 100 / 100 | -1.28 (-0.78) | 4/9 | none | is_t,val_t,x15,lat,power | +0.74 (1.46 / 1.73) |
| F22 | 1519 | +0.77 / -0.30 (-1.90) | 764 | +1.06 / -0.11 (-0.32) | -0.54 / -0.39 | -0.48 / -0.37 | 85 / 74 | -0.24 (-1.02) | 5/9 | none | is_t,val_t,x15,lat,rand,power | -0.28 (1.07 / 1.17) |
| F23 | 1526 | +1.24 / +0.20 (+0.44) | 765 | +2.07 / +1.05 (+1.29) | -0.02 / +0.84 | +0.16 / +1.03 | 97 / 96 | +0.98 (+0.24) | 7/9 | none | is_t,x15,power | -1.15 (1.04 / 1.02) |
| F24 | 1526 | +0.24 / -0.50 (-3.83) | 765 | +0.93 / +0.23 (+0.98) | -0.57 / +0.18 | -0.69 / +0.38 | 98 / 100 | +0.74 (-2.06) | 2/9 | none | is_t,val_t,x15,lat,power | -0.09 (0.74 / 0.70) |
| F25 | 4345 | +1.70 / +0.41 (+0.63) | 2176 | +1.90 / +0.67 (+0.77) | +0.12 / +0.42 | +0.32 / +0.77 | 97 / 81 | +0.58 (+0.35) | 7/9 | none | is_t,val_t,power | -1.67 (1.18 / 1.10) |
| F27 | 306 | +0.69 / -0.35 (-0.58) | 153 | +0.97 / +0.01 (+0.01) | -0.56 / -0.17 | -0.41 / -0.09 | 88 / 71 | +0.01 (-0.31) | 5/9 | none | is_t,val_t,x15,lat,rand,power | -3.34 (1.04 / 0.96) |
| F28 | 677 | +4.81 / +3.98 (+3.04) | 303 | +3.01 / +2.21 (+1.36) | +3.92 / +2.18 | +3.73 / +2.17 | 100 / 98 | +0.98 (+1.70) | 6/9 | DEMO | power | -3.90 (0.71 / 0.66) |
| M1 | 1379 | +0.93 / -0.65 (-5.40) | 720 | +0.72 / -0.33 (-2.03) | -1.15 / -0.55 | -0.69 / -0.61 | 100 / 100 | -1.54 (-2.90) | 0/9 | none | is_t,val_t,x15,lat,power | +0.08 (1.59 / 1.04) |
| M2 | 255 | +1.82 / +0.17 (+0.56) | 149 | +1.44 / +0.39 (+0.92) | -0.35 / +0.17 | +0.41 / -0.09 | 100 / 100 | +0.70 (+0.30) | 6/9 | none | is_t,val_t,x15,lat,power | -0.26 (1.65 / 1.04) |
| M3 | 1448 | +1.98 / +0.33 (+0.47) | 719 | +1.67 / +0.61 (+0.66) | -0.19 / +0.37 | +0.52 / +0.44 | 100 / 95 | +0.50 (+0.25) | 5/9 | none | is_t,val_t,x15,power | -1.96 (1.65 / 1.06) |
| M4 | 1448 | +0.93 / -0.59 (-1.87) | 720 | +0.96 / -0.06 (-0.13) | -1.04 / -0.28 | -0.43 / +0.14 | 100 / 100 | -0.10 (-1.00) | 3/9 | none | is_t,val_t,x15,lat,power | -0.91 (1.52 / 1.03) |
| M5 | 149 | +4.91 / +3.50 (+3.19) | 78 | +3.14 / +2.11 (+1.70) | +3.09 / +1.90 | +1.37 / +1.38 | 100 / 100 | +1.29 (+1.71) | 7/9 | DEMO | power | -1.77 (1.42 / 1.03) |
| M6 | 286 | +2.39 / +0.99 (+1.41) | 161 | +1.89 / +0.89 (+1.14) | +0.59 / +0.69 | -0.62 / +0.20 | 100 / 99 | +0.87 (+0.76) | 5/9 | none | is_t,lat,power | -1.18 (1.40 / 1.01) |
| M7 | 1505 | +0.44 / -1.00 (-6.11) | 753 | +0.38 / -0.61 (-3.14) | -1.42 / -0.81 | -1.61 / -0.90 | 100 / 92 | -2.39 (-3.28) | 1/9 | none | is_t,val_t,x15,lat,power | -0.38 (1.44 / 1.00) |
| M8 | 1492 | +1.09 / -0.36 (-1.69) | 744 | +0.94 / -0.08 (-0.23) | -0.78 / -0.29 | -1.12 / -0.59 | 100 / 100 | -0.17 (-0.90) | 3/9 | none | is_t,val_t,x15,lat,power | -0.46 (1.45 / 1.02) |
| M9 | 1492 | +2.69 / -1.51 (-4.62) | 744 | +2.72 / -1.88 (-6.22) | -3.30 / -3.88 | -3.66 / -3.16 | 100 / 100 | -4.72 (-2.48) | 0/9 | none | is_t,val_t,x15,lat,power | +1.54 (4.19 / 4.60) |
| M10 | 1493 | +0.88 / -0.56 (-5.25) | 744 | +0.24 / -0.75 (-5.94) | -0.98 / -0.95 | -1.10 / -1.21 | 100 / 98 | -4.51 (-2.82) | 1/9 | none | is_t,val_t,x15,lat,power | -0.26 (1.44 / 0.99) |
| M11 | 1480 | +1.03 / -0.71 (-2.30) | 739 | +0.88 / -0.32 (-0.75) | -1.29 / -0.61 | -0.82 / -0.74 | 100 / 96 | -0.57 (-1.24) | 2/9 | none | is_t,val_t,x15,lat,power | -0.79 (1.74 / 1.19) |
| M12 | 26 | +6.73 / +4.84 (+1.79) | 16 | +1.46 / +0.41 (+0.08) | +4.20 / +0.19 | +4.85 / -0.85 | 82 / 37 | +0.06 (+0.96) | 6/9 | none | val_t,lat,rand,power,mech | -19.32 (1.89 / 1.04) |
| I1 | 1463 | +1.53 / -0.15 (-0.26) | 734 | +0.92 / +0.27 (+0.41) | -0.99 / -0.06 | -0.73 / -0.16 | 100 / 99 | +0.31 (-0.14) | 5/9 | none | is_t,val_t,x15,lat,power | -1.67 (1.68 / 0.65) |
| I2 | 287 | +3.18 / +1.50 (+1.03) | 151 | +4.52 / +3.83 (+2.19) | +0.66 / +3.49 | -2.36 / +2.10 | 100 / 100 | +1.66 (+0.55) | 6/9 | none | is_t,lat | -2.39 (1.68 / 0.68) |
| I3 | 1434 | +0.57 / -0.35 (-1.47) | 728 | +1.05 / +0.74 (+2.91) | -0.82 / +0.58 | -0.67 / +0.60 | 92 / 100 | +2.21 (-0.79) | 4/9 | none | is_t,x15,lat | -0.03 (0.93 / 0.31) |
| I4 | 1469 | +0.94 / -0.65 (-1.55) | 734 | +1.68 / +1.20 (+1.64) | -1.44 / +0.95 | -0.63 / +0.55 | 100 / 100 | +1.25 (-0.83) | 5/9 | none | is_t,x15,lat,power | -1.19 (1.59 / 0.49) |
| I5 | 1492 | +1.63 / -1.41 (-5.62) | 740 | +1.15 / -0.89 (-3.02) | -2.92 / -1.90 | -2.37 / -2.06 | 100 / 100 | -2.29 (-3.02) | 0/9 | none | is_t,val_t,x15,lat,power | -0.01 (3.04 / 2.03) |
| I6 | 1485 | +0.75 / -1.36 (-4.14) | 740 | +0.67 / -0.90 (-3.69) | -2.41 / -1.68 | -1.83 / -1.06 | 100 / 84 | -2.80 (-2.22) | 0/9 | none | is_t,val_t,x15,lat,power | -0.29 (2.10 / 1.57) |
| I7 | 1465 | +1.56 / -0.46 (-2.09) | 631 | +2.06 / +0.62 (+2.72) | -1.46 / -0.10 | -2.32 / -2.11 | 100 / 100 | +2.06 (-1.12) | 5/9 | none | is_t,x15,lat | +1.02 (2.02 / 1.44) |
| I8 | 1437 | +2.03 / -1.26 (-3.86) | 722 | +0.29 / -2.52 (-3.38) | -2.90 / -3.93 | -3.10 / -2.82 | 100 / 76 | -2.56 (-2.07) | 2/9 | none | is_t,val_t,x15,lat,rand,power | -2.65 (3.29 / 2.81) |
| I9 | 1514 | +3.09 / -0.10 (-0.17) | 760 | +0.28 / -1.54 (-2.75) | -1.69 / -2.45 | -0.72 / -2.63 | 100 / 94 | -2.09 (-0.09) | 2/9 | none | is_t,val_t,x15,lat,power | -1.93 (3.19 / 1.82) |
| I10 | 1523 | +1.08 / -0.13 (-0.34) | 766 | +1.02 / +0.49 (+1.26) | -0.73 / +0.23 | -0.35 / +0.75 | 100 / 100 | +0.95 (-0.18) | 5/9 | none | is_t,x15,lat,power | -0.54 (1.21 / 0.52) |
| I11 | 47 | +7.59 / +6.71 (+2.72) | 24 | +9.85 / +9.57 (+1.49) | +6.27 / +9.43 | +6.30 / +8.58 | 86 / 100 | +1.13 (+1.46) | 7/9 | none | power | -15.52 (0.88 / 0.28) |
| I12 | 15 | +8.82 / +7.75 (+1.51) | 28 | +5.81 / +5.53 (+1.06) | +7.22 / +5.39 | +8.11 / +7.09 | 50 / 73 | +0.80 (+0.81) | 5/5 | none | rand,power,mech | -14.90 (1.07 / 0.28) |
| E1x | 987 | +5.59 / -1.80 (-0.67) | 744 | +2.03 / -1.30 (-0.99) | -5.49 / -2.97 | -5.32 / -1.83 | 98 / 98 | -0.75 (-0.44) | 2/7 | none | is_t,val_t,x15,lat,power | -3.17 (7.39 / 3.33) |
| E2x | 987 | +1.59 / -5.94 (-9.53) | 744 | +0.65 / -2.65 (-7.75) | -9.71 / -4.30 | -6.48 / -3.79 | 98 / 100 | -5.89 (-6.27) | 0/7 | none | is_t,val_t,x15,lat,power | -0.69 (7.53 / 3.30) |
| C1 | 1127 | +5.72 / -7.80 (-4.59) | 855 | +2.05 / -1.19 (-1.05) | -14.56 / -2.81 | -7.60 / -1.18 | 93 / 82 | -0.80 (-2.88) | 2/8 | none | is_t,val_t,x15,lat,power | -2.41 (13.52 / 3.24) |
| C2 | 225 | +18.92 / +5.71 (+0.70) | 155 | +11.23 / +7.94 (+2.20) | -0.90 / +6.29 | +7.31 / +7.41 | 100 / 100 | +1.67 (+0.44) | 4/8 | none | is_t,x15 | -2.96 (13.22 / 3.29) |
| FOMC_A4 | 37 | +23.00 / +21.62 (+1.90) | 23 | +32.94 / +31.60 (+2.40) | +21.35 / +31.32 | +21.41 / +31.19 | 98 / 100 | +1.82 (+1.02) | 9/9 | RELAXED | - | -19.29 (1.14 / 1.16) |
| N1a | 3791 | +0.96 / -2.24 (-17.51) | 2166 | +2.01 / -3.07 (-29.18) | -3.53 / -5.32 | -2.00 / -2.97 | 0 / 0 | -25.56 (-11.32) | 0/9 | none | is_t,val_t,x15,lat,rand,power | +0.64 (3.19 / 5.09) |
| N1b | 4035 | +0.65 / -2.26 (-18.70) | 2272 | +1.30 / -3.07 (-33.92) | -3.41 / -4.95 | -1.97 / -2.95 | 0 / 0 | -28.17 (-12.24) | 0/9 | none | is_t,val_t,x15,lat,rand,power | +0.35 (2.90 / 4.36) |
| N1c | 2196 | +1.18 / -2.34 (-11.45) | 1503 | +2.50 / -2.92 (-24.83) | -3.81 / -5.32 | -2.06 / -2.82 | 8 / 16 | -21.22 (-7.96) | 0/9 | none | is_t,val_t,x15,lat,rand,power | +0.68 (3.53 / 5.41) |
| N3b | 6 | +85.15 / +81.30 (+3.62) | 3 | +82.66 / +75.39 (+2.20) | +80.81 / +75.16 | +79.99 / +74.79 | 90 / 72 | +1.67 (+1.95) | 9/9 | none | rand | -58.92 (1.57 / 1.05) |


Record-only rows (not rebuildable: the rule was never written down, no code survives):
| id | recorded IS / VAL | verdict |
|---|---|---|
| F26 PCA residual s-score (round 8 R2) | net -1.15 / -1.62 bp (cost 3.4 / 4.1) | none (IS net < 0) |
| F29 USDJPY into short-dated Treasury auctions (round 4) | mid +4.5 (t 3.3) / +1.0 (t 0.4) | none (VAL t < 1 at mid, before cost) |
| I13 US500 night premium (round 3) | net +1.9 / -3.2 after swap | none (VAL net < 0) |

## Did the recompute reproduce the recorded numbers?
- **Exactly or within rounding** (net IS / VAL): F1 (E1), F2, F4, F5, F6, F7, F9-F16, F17 (rule I after the bug fix:
  +6.77 t 3.79 / +1.68 t 0.84), F18, F19-F21 (mid), F20 (J5c), F23, F24, F25 (+0.41 / +0.67 vs +0.32 / +0.65), F28
  (+3.98 t 3.04 / +2.21 t 1.36 vs +3.87 t 2.98 / +2.31 t 1.45), M1-M4, M5 (the lead's L code: +3.50 t 3.19 / +2.11
  t 1.70), M6, M8-M12, I1, I3-I8, I11, E1x, E2x, FOMC A4 (+21.62 t 1.90 / +31.60 t 2.40), N3b (+81.3 / +75.4 vs +81.8 /
  +75.8), N1a-c (net within 0.05 bp; trade counts ~12 % lower because the +1-minute bar is required to exist).
- **Partial**: F3 (63 / 69 trades a year vs ~84; the 250-day history starts in 2016 here, PRE in round 14; VAL net
  +3.01 vs +2.43), F8 (VAL +0.97 vs +0.71), I2 (IS net +1.50 vs +1.94, VAL +3.83 vs +3.11; bar-label ambiguity), I9 / I10
  (mid 0.1-0.3 bp lower), C1 (mid +5.7 / +2.1 vs +7.3 / +2.4: the day set differs), C2 (IS net +5.7 vs +9.0: the BTC IS
  span), F22 (an estimate in STREAM_X; here net -0.30 / -0.11).
- **Not reproduced**: I12 (S4b mirror): the round-8 event subset was never recorded; the declared reading (USD z >= 2)
  gives 2.5 trades a year in IS vs 7-20 recorded and IS net +7.75 (t 1.51) vs +13.0 (t 2.71). F27 (W1 carry into the
  Wednesday rollover): the round-3 row records only the idea; the declared reading gives mid +0.69 / +0.97 vs +2.2 /
  +1.4. Neither would pass RELAXED on the recorded numbers either (I12: power 1.4 and a post-hoc side; F27: "about 1 bp
  net").

## Random-control amendment (forward-only shifts for data-selected rows; symmetric version in brackets)
F3 100 / 99.5 (99 / 100), **F8 100 / 98.5 (0 / 2)**, M2 100 / 100 (100 / 100), M5 100 / 99.5 (100 / 93), M6 100 / 99
(99 / 76), I2 100 / 100 (92 / 92), I12 50 / 73 (52 / 47), F28 100 / 97.5 (100 / 87). No RELAXED verdict changes
(F8, M6, I2, I12, F28 fail RELAXED on other gates); F28 meets the DEMO numbers only under the forward control.

## The declared book of RELAXED survivors
Rows F1, F2, F20, FOMC A4 (F3, F4, F5 inside F1 and dropped, as declared). Equal risk = each trade's net / its row's
IS per-trade sd (R units); one bot per symbol, at most 3 open positions (the cap never bound: 0 trades skipped).
| era | trades | active days/yr | mean R per active day (t) | x1.5 | +1 min | daily Sharpe | power (VAL size) | R per year | by year (sum R) |
|---|---|---|---|---|---|---|---|---|---|
| IS | 4,168 | 288 | +0.209 (4.61) | +0.180 | +0.184 | 0.111 | 2.47 (IS size) | +60 | 2016 81, 2017 65, 2018 49, 2019 77, 2020 35, 2021 54 |
| VAL | 2,075 | 289 | +0.262 (3.89) | +0.252 | +0.181 | 0.132 | **2.96** | +76 | 2022 164, 2023 53, **2024 10** |

- Rows' share of VAL R: F1 +75, F2 +72, F20 +70, A4 +11. Correlation with C3 (IS + VAL): daily +0.046, monthly +0.089.
- Information variants (chosen after seeing the above, not candidates): F1 + F2 + A4: VAL power 2.13; **F1 + F20 + A4:
  3.30** (F2 duplicates F1's EURUSD exposure; F20's HOLD already failed); F1 + A4: 2.09.
- **Expected HOLD.** F1's and F20's HOLD are already known (registered E1 and J5c): E1 kept 0.47 of its VAL net (+0.64 vs
  +1.35), J5c went to -0.25 (-0.33 of VAL). Applying those to F1, F2 (same window as E1) and F20, and 0.65 of the VAL mid
  to A4, the book's HOLD R per year is ~17 against 76 in VAL: **expected HOLD power ~0.7**, and 2024 (+10 R) already
  shows the drop. The book is not drafted: its power comes from the ECB window and the Sydney 10:00 leg, whose HOLD
  readings are in hand and weak.

## Cost needed for LIVE (rows with a positive answer; all others need a negative cost)
| row | LIVE cost, rt bp | IC cost IS / VAL | what it would take |
|---|---|---|---|
| F4 ECB pre-fix 12:45-13:00 | +0.16 | 0.66 / 0.62 | no commission and ~zero spread |
| F5 Friday ECB slot | +0.07 | 0.63 / 0.64 | same |
| F6 ECB rebound | +0.03 | 0.65 / 0.64 | same |
| F20 J5c (HOLD failed) | +0.73 | 1.10 / 0.77 | IC's VAL cost almost; HOLD -0.25 net |
| F21 Sydney post-leg | +0.74 | 1.46 / 1.73 | a venue at ~0.4 bp |
| F19 Sydney pre-leg | +1.04 | 1.76 / 2.43 | a venue at ~0.4 bp (IC's rollover-hour spread kills it) |
| M1 SGE auction | +0.08 | 1.59 / 1.04 | none realistic |
| M9 silver LBMA 12:00 | +1.54 | 4.19 / 4.60 | one COMEX tick (~2 bp) is still too much |
| I7 ASX open drop | +1.02 | 2.02 / 1.44 | not executable (+1 min < 0 every year) |
| N1a / N1b / N1c reopen-gap fade | +0.64 / +0.35 / +0.68 | 3.2-5.4 | a venue without IC's rollover spreads |
The FOMC dollar short needs about -19 bp (count-capped: 8 a year), the ECB 2-hour rows F1-F3 -0.2 to -0.9 bp (sd-capped).

## What this says
- Relaxing the bar to RELAXED does not create a new mechanism: the survivors are the two already-known durable ones,
  the ECB-fix EURUSD window (6 overlapping rows) and the FOMC-day dollar short. Everything else that was "real at mid"
  in rounds 3-23 is still below IC's cost, or fails its VAL check, its random control, or power 1.5.
- The FOMC dollar short is the only RELAXED survivor whose HOLD has not been looked at and whose VAL is larger than IS
  (1.43). Its limit is the count (8 a year) and, in 2025-26, possibly fewer trades because USD's rate was at the top.
- The book reaches VAL-size power 2.96 only because it stacks rows whose HOLD is already known to be weak; at those
  retentions it is ~0.7.

## Surprises
- F8's symmetric random control (0 % / 2 %) is the selection pitfall in pure form: random windows shifted earlier swept
  the morning rise that selected the day.
- F28 (EURUSD after a USTEC 6-sd shock) reproduces at IS net t 3.04 and meets the DEMO numbers under the forward
  control, but VAL is carried by 2022 (+10.9; 2023 -2.2, 2024 -1.0) and it is the best of a 5,000-cell grid.
- I2 (USTEC LETF close, top quintile) has VAL net +3.83 (t 2.19) and VAL-size power 1.66 but fails RELAXED on IS t
  (1.03) and +1 minute in IS (-2.36): the 2020-tail finding of round 13 P again.
- I3 (US30 post-close fade) and I7 (ASX open) are positive in VAL at IC's VAL costs (t 2.91 / 2.72), negative in IS
  only because IC's 2016-21 index spreads were wider: the user's undecided "judge IS at today's cost" question (round
  16 X (e)) would still fail them on x1.5 / +1 minute.

## Files
- Scripts (scratchpad `r24/C/`): `clib.py` (panel, quotes, costs, swap), `eng.py` (trades, era stats, random control,
  tiers, LIVE cost), `rules.py` (rows F1-F24, F27, M, I, E, C), `rules2.py` (FOMC A4, N1, N3b, I12, F28, F25),
  `run_all.py`, `run_all2.py`, `summ.py` (table, survivors), `book.py`, `holdexp.py`.
- Outputs (`r24/C/out/`): `run_all.log`, `run_all2.log`, `run_fwd.log`, `table.md`, `rule_<id>.pkl` (trades),
  `rule_<id>_sym.pkl` (symmetric-control versions), `book_F1_F2_F20_FOMC_A4.out`, `holdexp.out`.
- Calendars added to `r23/shared/cal/`: `fomc_2016_2024.json` (Fed site, fetched 11:49 UTC), `cal_C.json` +
  `make_cal_C.py` (TARGET2, England, Shanghai SE, US federal, NSW holidays, python-holidays 0.106).
