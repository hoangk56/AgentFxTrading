# Round 27, stream V: the direction of venue-open jumps (follow or fade the first seconds after a venue clock)

Written 2026-10-17 21:42 UTC (from `date -u`; finished in the minutes after). [HYPOTHESES_V.md](HYPOTHESES_V.md)
declared all 3,924 cells at 21:23 UTC, before any opening move, forward return or spread at a clock was computed.
Its Addendum 1 (21:40 UTC) was written after all cells: the declared PRE check cannot run, and four information-only
tables were added. Fill model: round 26's (binding).

HOLD was never loaded:
- the loader asserts every requested day and every tick timestamp < 2025-01-01;
- the minute panel ends 2024-12-31;
- the C3 file was read for its IS / VAL rows only;
- no Dukascopy file was opened.

## Answer
- **No LIVE candidate. Two cells meet the DEMO numbers, both within chance. They are drafted, with the
  recommendation not to open HOLD:** [PREREG_DRAFT_V_euopen_index_fade.md](PREREG_DRAFT_V_euopen_index_fade.md).
  - Both fade a first-minute move of >= 4 x its trailing 60-day median at the European cash open (08:00 London) in
    an index CFD and hold 15 min.
    - US30 on ticks: IS +9.26 bp net (t 2.23, n 59), VAL +4.65 (t 0.85, n 14).
    - UK100 at minute level: IS +13.15 (t 2.12, n 42), VAL +17.07 (t 2.40, n 14).
  - Against them:
    - the best IS net t of all 3,924 cells (2.23) is below the sign-flip null's **median** for the max (2.31);
      57 % of null draws beat it;
    - 67-77 % of each IS sum comes from 9-12 opens in March-April 2020. Without them, IS is +2.69 / +5.49;
    - the USTEC sibling is -7.99 bp in VAL;
    - HOLD would hold ~8 events per variant. The expected HOLD t is 0.65 / 1.82 at the VAL size.
- **The opening move does carry direction, beyond chance at mid, but not in a tradable way.**
  - The max |IS mid t| over the no-stop cells is 4.41, against a sign-flip null p95 of 3.99 (p 0.009). For the 32
    primary cells it is 3.18 against 2.86 (p 0.016).
  - The strongest is 07:00 New Zealand: NZDUSD reverses its first 15 s in IS (k 2, h 5: -1.26 bp mid, t -4.41) and
    not in VAL (+0.46, t 0.92).
  - The only effect present in both eras: the first 15-60 s of the gold and silver settlement windows (13:29 / 13:24
    ET) reverse, by 0.5-1.4 bp in IS (t 2.8-3.5) and 0.4-0.9 bp in VAL (t 1.1-2.75), at k 0 (every day). The metals
    round trip at that minute is ~2.7 bp (2.1 bp spread + 0.6 bp commission), so the fade nets -1.4 to -2.3 bp.
  - The most consistent "follow" reading: gold after a large move at the 13:30 Beijing afternoon reopen (k 4).
    - Mid: +3.75 bp (t 2.25) IS and +3.38 (t 1.83) VAL at h 15; +7.31 / +4.74 at h 60.
    - Net at h 60: +5.48 (t 1.76) IS, +3.63 (t 1.15) VAL. That fails the DEMO t.
- **Cost is the binding constraint, as in rounds 10-26.** The clocks with the largest opening moves are the most
  expensive minutes at IC.
  - Mean round-trip spread paid at k 2 (w 15 s, h 15 min):
    - silver 3.3-4.7 bp;
    - oil 6.5-9.5 bp in IS, 2.6-3.6 in VAL;
    - platinum 26-32 bp at the Chinese clocks;
    - natural gas 13.6 / 44 bp (IS / VAL) at its settlement.
  - FX and gold opening moves are 0.4-2 bp (median |m| at w 15 s).
  - 23 of the 32 primary cells lose more than 1 bp a trade in IS. 6 are net > 0 in IS, and 1 in both eras.
- **Venue-shut placebos.**
  - Chinese holidays remove most of the activity spike: the V0 check shows silver x8.9 at 09:00 Beijing on trading
    days against x2.1 on holidays. In the primary cells, the trading-day-minus-holiday differences stay within |t| 2
    at the Chinese clocks. The exception is CNY-FIX k 4 (|t| 2.3, 7 holiday events). Both sides lose on both day
    types.
  - There are no US-holiday placebos: IC quotes nothing at 15:50 ET or at the settlement minutes on NYSE / CME
    holidays.
  - The 07:00 NZ spike survives NZ holidays (x6.0, n 27) but vanishes on NZ Saturdays (x1.5). It is a dealing-day
    clock, not an NZ venue.

## How this differs from the fixed-side tests of the same venues
| earlier test | what it did | here |
|---|---|---|
| round 10 A (minute panel) | A2-flow: long after the Chinese opens (01:00 / 12:00 / 13:00 UTC) for 15-60 min; A2-cont: side = the move while the venue was shut; A2-close: fade the 30 min before the closes; A4: Asian FX fixes with fixed USD sides; the CNY 09:15 fix was a round-4 fixed-side cell | side = the sign of the move from T-1 s to T+15 / 60 s, on days when it is large against the clock's own 60-day median, filled on ticks at T+w+latency |
| round 15 V (minute panel) | 1-10 min windows at 24 benchmarks with U / M (sign of the 10 minutes before entry) / G (gap) rules, sides predicted from mechanisms; cash opens, COMEX / NYMEX floor opens, WTI settlement end 14:30 ET; 15:50-15:59 ET M+ as information | conditioning on the first seconds after the clock, never the 10 minutes before; clocks round 15 did not have: CN-DAY, CN-PM, CN-NIGHT, CNY-FIX, NZ-07, the NY imbalance as an event (with NYSE's 15:45 -> 15:50 move on 2019-04-01), gold / silver / gas / Brent settlement windows |
| round 24 B (Dukascopy + IC) | fixed sides: China-session gold long, China-close fade, COMEX open fade, SGE placebo | as above |
| settlement minutes (rounds 6, 12 L, 13 P, 15 V6, 24 B) | sides from the day's move or the 10 minutes around the window | side from the first w seconds of the settlement window |

## Design (exact rules in HYPOTHESES_V.md)
- **Clocks.** CN-DAY 09:00 Beijing (01:00 UTC); CN-PM 13:30 Beijing (05:30); CN-NIGHT 21:00 Beijing (13:00;
  night-session days only); CNY-FIX 09:15 Beijing (01:15); EU-OPEN 08:00 London = 09:00 Frankfurt; NZ-07 07:00
  Auckland; NY-IMB 15:50 ET (USTEC; US30 at 15:45 ET before 2019-04-01, 15:50 after, plus US30 at 15:50 throughout as
  a secondary set); SETTLE gold 13:29, silver 13:24, WTI and gas 14:28 ET, Brent 19:28 London.
- **Opening move.** m = prevailing mid at T + w over the one at T - 1 s, w in {15, 60} s.
- **Event.** |m| >= k x the median |m| of the previous 60 clean trading days at that clock, k in {0, 2, 4} (k 0 = every
  day).
- **Sides and fills.** V1 follows, V2 fades. Entry at the first tick >= T + w + L, buying at the ASK and selling at
  the BID; L = 250 ms decides, with L 0 / 1,000 ms / next tick and +1 minute reported. Exit h in {5, 15, 60} min
  later. Optional server-side stop at max(|m|, 2 spreads) from the entry mid.
- **Costs.** Actual tick spreads, plus 0.6 bp commission for FX and metals.
- **Exclusions.** Calendar rows within [T - 15 min, T + w + h + 2 min], central-bank windows, untimed and vote days,
  IC artefacts, the 16:55-18:10 NY rollover.
- **Controls.**
  - Venue-shut days (Chinese, LSE + Xetra, NZ holidays, NZ Saturdays; US holidays turned out n/a).
  - Shifted clocks T +- 30 min, with the rule recomputed there.
  - Random direction (500 seeds).
  - Random time (200 seconds per event in [T - 150, T - 35] U [T + 35, T + 150] min, side recomputed).
- **Cells.** 54 tick sets x 72 + 2 minute sets (DE40, UK100) x 18 = 3,924. The 32 primary cells are w 15 s, h 15 min,
  no stop, k 2 / 4, both families, on the clock's pooled set (NZDUSD for NZ-07, the index pair for NY-IMB).

## V0 clock check (unsigned, IS): activity in the first 15 s against T-60..T-30 s
Ratio of the mean |change of mid| per 5 s in [T, T+15 s) to the same in [T-60 s, T-30 s), on trading days and on
venue-shut days (n days). Full table: `out/profile_v.txt`.

| clock | instrument: trading day / venue shut |
|---|---|
| CN-DAY | XAG 8.9 / 2.1 (103); XBR 6.8 / 1.8; XPT 5.4 / 2.4; XAU 5.3 / 1.9; XTI 4.8 / 2.6; AUD 2.1 / 1.9 |
| CN-PM | XAG 6.6 / 1.4; XAU 3.8 / 1.4; XPT 3.4 / 1.1; XBR 3.4 / 1.8; XTI 2.6 / 1.5; AUD 1.6 / 1.1 |
| CN-NIGHT | XTI 3.6 / 3.2; XBR 3.3 / 3.0; XAG 3.2 / 1.8; XAU 2.3 / 1.7; AUD 1.7 / 1.7 |
| CNY-FIX | AUD 1.8 / 1.4; NZD 1.7 / 1.4; XAU 1.3 / 1.3 |
| EU-OPEN | US30 4.3 / 3.5 (13); USTEC 4.2 / 4.1 (13); AUD 2.3 / 2.8; NZD 2.3 / 3.5; XAU 2.3 / 3.0 (base activity on holidays is 3-5x lower) |
| NZ-07 | NZD 3.9 / 6.0 (NZ holidays, 27) / 1.5 (NZ Saturdays, 311); AUD 1.6 / 1.9 / 1.5 |
| NY-IMB | USTEC 2.7, US30 2.4 / no IC quotes on NYSE holidays |
| SETTLE | XNG 2.5, XAG 2.4, XAU 2.0, XTI 1.7, XBR 1.6 / no IC quotes on the US holidays |

The Chinese day and afternoon opens are clean venue events; CN-NIGHT oil is not (13:00 UTC is also 08:00 / 09:00
New York); the CNY fix barely moves IC's quotes.

## 1. Event counts
Columns: valid trading (OPEN) days with an opening move at w = 15 s (DE40 / UK100: w = 60 s, minute level);
events at k = 0 / 2 / 4 after the h = 15 exclusions, IS / VAL; placebo days with a valid move, all years pooled.

| clock | instrument | valid OPEN days IS / VAL | k0 IS / VAL | k2 IS / VAL | k4 IS / VAL | HOL days | SAT days | 2020 suspension days |
|---|---|---|---|---|---|---|---|---|
| CN-DAY | AUDUSD | 1396 / 687 | 1142 / 560 | 234 / 122 | 50 / 10 | 146 | 0 | 0 |
| CN-DAY | XAUUSD | 1430 / 706 | 1205 / 576 | 280 / 126 | 66 / 22 | 148 | 0 | 0 |
| CN-DAY | XAGUSD | 1358 / 699 | 1141 / 573 | 243 / 116 | 68 / 34 | 138 | 0 | 0 |
| CN-DAY | XPTUSD | 938 / 702 | 791 / 574 | 175 / 133 | 41 / 34 | 113 | 0 | 0 |
| CN-DAY | XTIUSD | 805 / 656 | 670 / 539 | 165 / 109 | 53 / 23 | 91 | 0 | 0 |
| CN-DAY | XBRUSD | 535 / 300 | 453 / 243 | 110 / 51 | 22 / 19 | 50 | 0 | 0 |
| CN-PM | AUDUSD | 1319 / 679 | 1085 / 556 | 282 / 106 | 57 / 20 | 132 | 0 | 0 |
| CN-PM | XAUUSD | 1401 / 710 | 1149 / 579 | 246 / 130 | 66 / 27 | 146 | 0 | 0 |
| CN-PM | XAGUSD | 1235 / 696 | 1012 / 567 | 220 / 130 | 44 / 30 | 116 | 0 | 0 |
| CN-PM | XPTUSD | 874 / 696 | 715 / 565 | 192 / 138 | 63 / 31 | 107 | 0 | 0 |
| CN-PM | XTIUSD | 662 / 629 | 530 / 515 | 118 / 104 | 29 / 27 | 76 | 0 | 0 |
| CN-PM | XBRUSD | 682 / 633 | 546 / 516 | 143 / 102 | 41 / 28 | 75 | 0 | 0 |
| CN-NIGHT | AUDUSD | 1291 / 670 | 999 / 506 | 232 / 110 | 44 / 16 | 203 | 0 | 63 |
| CN-NIGHT | XAUUSD | 1341 / 694 | 1044 / 526 | 208 / 114 | 38 / 28 | 205 | 0 | 64 |
| CN-NIGHT | XAGUSD | 1284 / 685 | 996 / 517 | 209 / 99 | 39 / 20 | 188 | 0 | 63 |
| CN-NIGHT | XTIUSD | 786 / 675 | 623 / 506 | 125 / 96 | 30 / 25 | 149 | 0 | 62 |
| CN-NIGHT | XBRUSD | 776 / 674 | 618 / 510 | 128 / 98 | 26 / 25 | 150 | 0 | 61 |
| CNY-FIX | AUDUSD | 1379 / 684 | 855 / 445 | 212 / 105 | 35 / 24 | 142 | 0 | 0 |
| CNY-FIX | NZDUSD | 1355 / 696 | 832 / 451 | 212 / 97 | 42 / 24 | 138 | 0 | 0 |
| CNY-FIX | XAUUSD | 1397 / 703 | 1075 / 525 | 238 / 113 | 43 / 20 | 149 | 0 | 0 |
| EU-OPEN | AUDUSD | 1444 / 724 | 982 / 543 | 211 / 101 | 49 / 14 | 21 | 0 | 0 |
| EU-OPEN | NZDUSD | 1454 / 734 | 988 / 551 | 199 / 92 | 42 / 8 | 23 | 0 | 0 |
| EU-OPEN | XAUUSD | 1472 / 744 | 1009 / 558 | 220 / 103 | 46 / 15 | 15 | 0 | 0 |
| EU-OPEN | US30 | 1436 / 734 | 992 / 554 | 209 / 104 | 60 / 22 | 14 | 0 | 0 |
| EU-OPEN | USTEC | 1452 / 740 | 1002 / 556 | 219 / 105 | 66 / 23 | 15 | 0 | 0 |
| EU-OPEN | DE40 | 1496 / 754 | 1029 / 573 | 185 / 90 | 32 / 6 | 5 | 0 | 0 |
| EU-OPEN | UK100 | 1502 / 741 | 1037 / 560 | 200 / 108 | 42 / 14 | 6 | 0 | 0 |
| NZ-07 | AUDUSD | 1165 / 550 | 967 / 437 | 268 / 71 | 63 / 9 | 29 | 436 | 0 |
| NZ-07 | NZDUSD | 1170 / 458 | 969 / 360 | 235 / 78 | 61 / 16 | 30 | 418 | 0 |
| NY-IMB | US30 | 1416 / 738 | 1183 / 615 | 248 / 111 | 66 / 14 | 0 | 0 | 0 |
| NY-IMB | USTEC | 1460 / 741 | 1221 / 619 | 225 / 126 | 58 / 22 | 0 | 0 | 0 |
| SETTLE | XAUUSD | 1471 / 740 | 1216 / 615 | 274 / 129 | 54 / 21 | 12 | 0 | 0 |
| SETTLE | XAGUSD | 1395 / 716 | 1149 / 598 | 227 / 119 | 49 / 20 | 9 | 0 | 0 |
| SETTLE | XTIUSD | 968 / 723 | 799 / 612 | 173 / 99 | 35 / 3 | 9 | 0 | 0 |
| SETTLE | XBRUSD | 944 / 710 | 787 / 597 | 154 / 107 | 31 / 12 | 0 | 0 | 0 |
| SETTLE | XNGUSD | 761 / 717 | 638 / 603 | 138 / 128 | 29 / 20 | 11 | 0 | 0 |
| NY-IMB-1550 | US30 | 1433 / 738 | 1197 / 615 | 224 / 111 | 63 / 14 | 0 | 0 | 0 |

Median |opening move| (bp, w = 15 s, OPEN days, IS / VAL) and median entry spread at L250 (bp, IS / VAL); DE40 and UK100: w = 60 s and the bar-close spread:

| clock | instrument | median abs m IS / VAL | median spread IS / VAL |
|---|---|---|---|
| CN-DAY | AUDUSD | 0.78 / 0.91 | 0.30 / 0.00 |
| CN-DAY | XAUUSD | 1.82 / 1.46 | 0.89 / 0.51 |
| CN-DAY | XAGUSD | 4.14 / 4.59 | 4.21 / 4.79 |
| CN-DAY | XPTUSD | 2.94 / 2.45 | 22.41 / 27.84 |
| CN-DAY | XTIUSD | 4.86 / 5.34 | 6.40 / 3.61 |
| CN-DAY | XBRUSD | 4.79 / 7.55 | 5.58 / 2.92 |
| CN-PM | AUDUSD | 0.44 / 0.73 | 0.28 / 0.00 |
| CN-PM | XAUUSD | 0.84 / 1.17 | 0.85 / 0.50 |
| CN-PM | XAGUSD | 2.60 / 3.50 | 4.09 / 4.26 |
| CN-PM | XPTUSD | 1.51 / 2.03 | 22.00 / 26.97 |
| CN-PM | XTIUSD | 2.73 / 3.28 | 6.61 / 3.66 |
| CN-PM | XBRUSD | 2.62 / 3.27 | 5.82 / 2.75 |
| CN-NIGHT | AUDUSD | 0.76 / 0.93 | 0.27 / 0.00 |
| CN-NIGHT | XAUUSD | 1.84 / 1.95 | 0.73 / 0.42 |
| CN-NIGHT | XAGUSD | 4.08 / 5.89 | 3.34 / 3.88 |
| CN-NIGHT | XTIUSD | 6.64 / 6.93 | 6.23 / 3.59 |
| CN-NIGHT | XBRUSD | 6.15 / 6.37 | 5.60 / 2.77 |
| CNY-FIX | AUDUSD | 0.62 / 0.86 | 0.39 / 0.00 |
| CNY-FIX | NZDUSD | 0.59 / 0.76 | 0.60 / 0.70 |
| CNY-FIX | XAUUSD | 0.72 / 0.88 | 0.87 / 0.50 |
| EU-OPEN | AUDUSD | 0.99 / 1.05 | 0.27 / 0.00 |
| EU-OPEN | NZDUSD | 1.00 / 1.05 | 0.47 / 0.64 |
| EU-OPEN | XAUUSD | 1.29 / 1.34 | 0.72 / 0.47 |
| EU-OPEN | US30 | 1.44 / 1.33 | 1.11 / 0.29 |
| EU-OPEN | USTEC | 1.56 / 1.74 | 2.97 / 1.36 |
| EU-OPEN | DE40 | 5.84 / 6.98 | 0.81 / 0.32 |
| EU-OPEN | UK100 | 6.54 / 6.68 | 1.59 / 1.28 |
| NZ-07 | AUDUSD | 0.52 / 0.72 | 0.29 / 0.00 |
| NZ-07 | NZDUSD | 0.65 / 0.66 | 0.70 / 0.96 |
| NY-IMB | US30 | 2.03 / 2.70 | 0.87 / 0.29 |
| NY-IMB | USTEC | 3.31 / 3.98 | 1.60 / 0.68 |
| SETTLE | XAUUSD | 1.35 / 1.34 | 0.71 / 0.41 |
| SETTLE | XAGUSD | 3.29 / 2.54 | 3.19 / 3.60 |
| SETTLE | XTIUSD | 7.66 / 8.27 | 6.36 / 3.50 |
| SETTLE | XBRUSD | 7.20 / 7.22 | 5.84 / 2.76 |
| SETTLE | XNGUSD | 9.04 / 14.92 | 12.90 / 42.78 |
| NY-IMB-1550 | US30 | 2.03 / 2.70 | 0.87 / 0.29 |

Notes:
- XPTUSD has no IC ticks from mid-2016 to mid-2018, so its IS sample is short.
- XBRUSD at 01:00 UTC is mostly a summer sample: in winter ICE Brent itself opens at 01:00 London, so there is no
  quote before the clock (valid share 0.13 in winter months against 0.74 in summer).

## 2. Results
### Primary cells (w 15 s, h 15 min, no stop, k 2 / 4); bp per trade, t clustered by UTC day
Columns:
- latencies: net at L0 / **L250, the decision latency** / L1000 / next tick / +1 min;
- power: per-trade (and per-day) net Sharpe x sqrt(1.73 x events per year), at the IS and the VAL size;
- placebo: the same rule on venue-shut days, all years pooled, t clustered by holiday block, with the
  trading-minus-placebo difference t;
- shifted: mean net at T - 30 / T + 30 min;
- RD / RT: the share of random-direction / random-time seeds the cell beats.

| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CN-DAY ALL V1 w15 k2 h15 none | 1207 / 657 | +0.55 (+0.61) / +2.92 (+2.23) | -6.79 / **-6.77 (-6.88)** / -6.78 / -6.70 / -7.34 | -5.76 / **-5.77 (-4.25)** / -5.70 / -5.68 / -5.79 | -10.20 / -9.89 | +0.85 | -4.77 / -3.80 | -3.59 / -3.20 | HOL n64 -2.83 (diff t -0.95) | -8.74 / -9.83; -11.37 / -8.98 | 0.77 / 1.00 | 0.83 / 1.00 | fail |
| CN-DAY ALL V2 w15 k2 h15 none | 1207 / 657 | -0.55 (-0.61) / -2.92 (-2.23) | -7.88 / **-7.87 (-8.46)** / -7.81 / -7.87 / -7.14 | -11.66 / **-11.61 (-8.15)** / -11.53 / -11.59 / -11.11 | -11.30 / -15.73 | +1.48 | -5.90 / -7.89 | -4.42 / -5.90 | HOL n64 -12.64 (diff t +0.53) | -8.54 / -10.16; -6.44 / -8.11 | 0.22 / 0.00 | 0.17 / 0.00 | fail |
| CN-DAY ALL V1 w15 k4 h15 none | 300 / 142 | +0.98 (+0.42) / +7.37 (+2.09) | -6.90 / **-6.90 (-2.82)** / -6.84 / -6.72 / -8.50 | -3.50 / **-3.54 (-0.90)** / -3.72 / -3.60 / -2.42 | -10.61 / -8.78 | +0.51 | -1.88 / -0.85 | -1.51 / -0.69 | HOL n7 +40.30 (diff t -1.05) | -10.46 / -9.73; -16.89 / -7.19 | 0.65 / 0.99 | 0.68 / 1.00 | fail |
| CN-DAY ALL V2 w15 k4 h15 none | 300 / 142 | -0.98 (-0.42) / -7.37 (-2.09) | -8.98 / **-8.85 (-3.66)** / -8.80 / -8.86 / -7.11 | -18.44 / **-18.28 (-5.05)** / -18.08 / -18.22 / -18.96 | -12.56 / -23.53 | +2.07 | -2.55 / -4.54 | -1.92 / -3.66 | HOL n7 -49.18 (diff t +0.73) | -8.94 / -12.18; -11.48 / -14.70 | 0.32 / 0.00 | 0.28 / 0.00 | fail |
| CN-PM ALL V1 w15 k2 h15 none | 1201 / 710 | +0.74 (+0.90) / -0.26 (-0.30) | -6.87 / **-6.85 (-7.83)** / -6.90 / -6.80 / -7.02 | -8.60 / **-8.59 (-8.84)** / -8.62 / -8.58 / -9.32 | -10.41 / -12.55 | +1.25 | -5.76 / -7.83 | -4.15 / -6.40 | HOL n38 -3.35 (diff t -0.56) | -8.66 / -10.14; -7.31 / -7.94 | 0.89 / 0.39 | 0.86 / 0.24 | fail |
| CN-PM ALL V2 w15 k2 h15 none | 1201 / 710 | -0.74 (-0.90) / +0.26 (+0.30) | -8.31 / **-8.33 (-9.27)** / -8.28 / -8.22 / -8.13 | -8.06 / **-8.07 (-8.37)** / -8.05 / -8.09 / -7.39 | -11.89 / -12.02 | +0.97 | -6.94 / -7.58 | -4.70 / -6.19 | HOL n38 -16.91 (diff t +1.07) | -7.18 / -9.45; -8.25 / -8.42 | 0.11 / 0.69 | 0.02 / 0.47 | fail |
| CN-PM ALL V1 w15 k4 h15 none | 300 / 163 | +1.95 (+0.79) / -1.63 (-0.85) | -8.23 / **-8.22 (-3.04)** / -8.30 / -8.26 / -8.72 | -9.85 / **-9.80 (-4.29)** / -9.91 / -9.89 / -10.41 | -13.07 / -13.69 | +1.19 | -2.36 / -3.90 | -1.68 / -3.19 | HOL n9 -12.72 (diff t +0.13) | -11.30 / -15.13; -9.11 / -7.19 | 0.89 / 0.14 | 0.84 / 0.12 | fail |
| CN-PM ALL V2 w15 k4 h15 none | 300 / 163 | -1.95 (-0.79) / +1.63 (+0.85) | -12.11 / **-12.12 (-4.72)** / -12.03 / -11.93 / -11.55 | -6.49 / **-6.55 (-3.24)** / -6.48 / -6.45 / -5.94 | -16.98 / -10.44 | +0.54 | -3.46 / -2.68 | -2.37 / -2.46 | HOL n9 -5.65 (diff t -0.15) | -9.33 / -14.11; -10.84 / -10.33 | 0.14 / 0.87 | 0.06 / 0.77 | fail |
| CN-NIGHT ALL V1 w15 k2 h15 none | 902 / 517 | +0.62 (+0.45) / -0.88 (-0.37) | -2.80 / **-2.77 (-2.06)** / -2.77 / -2.73 / -2.48 | -3.30 / **-3.30 (-1.38)** / -3.21 / -3.26 / -4.79 | -4.25 / -4.32 | +1.19 | -1.55 / -1.44 | -1.11 / -1.05 | HOL n99 -6.03 (diff t +0.52) | -3.27 / -2.46; -1.64 / -2.50 | 0.76 / 0.31 | 0.75 / 0.14 | fail |
| CN-NIGHT ALL V2 w15 k2 h15 none | 902 / 517 | -0.62 (-0.45) / +0.88 (+0.37) | -4.00 / **-4.01 (-2.89)** / -4.04 / -4.08 / -4.32 | -1.54 / **-1.55 (-0.65)** / -1.61 / -1.52 / +0.04 | -5.49 / -2.57 | +0.39 | -2.19 / -0.68 | -1.54 / -0.49 | HOL n99 -0.07 (diff t -0.49) | -2.73 / -2.35; -4.89 / -2.14 | 0.29 / 0.73 | 0.24 / 0.86 | fail |
| CN-NIGHT ALL V1 w15 k4 h15 none | 177 / 114 | +8.80 (+2.00) / +1.98 (+0.28) | +4.33 / **+4.41 (+1.02)** / +4.59 / +4.48 / +4.03 | -0.71 / **-0.63 (-0.09)** / -0.50 / -0.33 / -5.69 | +2.43 / -1.77 | -0.14 | +0.73 / -0.09 | +0.55 / -0.07 | HOL n14 -23.41 (diff t +1.55) | -5.09 / -4.79; -3.31 / -0.37 | 0.99 / 0.66 | 1.00 / 0.65 | fail |
| CN-NIGHT ALL V2 w15 k4 h15 none | 177 / 114 | -8.80 (-2.00) / -1.98 (-0.28) | -13.23 / **-13.18 (-2.90)** / -13.39 / -13.20 / -13.04 | -4.60 / **-4.60 (-0.64)** / -4.72 / -4.75 / +0.48 | -15.16 / -5.74 | +0.35 | -2.07 / -0.65 | -1.51 / -0.48 | HOL n14 +19.86 (diff t -1.89) | -1.06 / -0.27; -4.59 / -4.63 | 0.00 / 0.37 | 0.00 / 0.35 | fail |
| CNY-FIX ALL V1 w15 k2 h15 none | 662 / 315 | +0.78 (+1.75) / +0.08 (+0.12) | -0.58 / **-0.57 (-1.27)** / -0.56 / -0.58 / -0.57 | -0.95 / **-0.97 (-1.41)** / -1.02 / -0.95 / -1.36 | -0.94 / -1.20 | +1.71 | -0.78 / -1.33 | -0.68 / -1.07 | HOL n42 -3.10 (diff t +1.63) | -1.73 / -0.35; -0.90 / -1.83 | 0.98 / 0.60 | 0.98 / 0.51 | fail |
| CNY-FIX ALL V2 w15 k2 h15 none | 662 / 315 | -0.78 (-1.75) / -0.08 (-0.12) | -2.12 / **-2.14 (-4.75)** / -2.15 / -2.13 / -2.10 | -1.16 / **-1.14 (-1.66)** / -1.10 / -1.18 / -0.74 | -2.51 / -1.37 | +0.53 | -2.92 / -1.56 | -2.55 / -1.25 | HOL n42 +0.55 (diff t -1.54) | -0.90 / -1.72; -1.87 / -0.23 | 0.02 / 0.45 | 0.01 / 0.39 | fail |
| CNY-FIX ALL V1 w15 k4 h15 none | 120 / 68 | +1.86 (+1.24) / -0.46 (-0.29) | +0.38 / **+0.48 (+0.32)** / +0.46 / +0.43 / +0.32 | -1.50 / **-1.55 (-0.98)** / -1.78 / -1.56 / -2.52 | +0.09 / -1.79 | -3.25 | +0.18 / -0.98 | +0.17 / -0.74 | HOL n7 -5.56 (diff t +2.32) | -1.50 / +0.04; +1.14 / -2.23 | 0.91 / 0.38 | 0.95 / 0.36 | fail |
| CNY-FIX ALL V2 w15 k4 h15 none | 120 / 68 | -1.86 (-1.24) / +0.46 (+0.29) | -3.16 / **-3.24 (-2.17)** / -3.23 / -3.16 / -3.02 | -0.65 / **-0.62 (-0.40)** / -0.39 / -0.63 / +0.40 | -3.63 / -0.87 | +0.19 | -1.26 / -0.40 | -1.17 / -0.30 | HOL n7 +3.46 (diff t -2.32) | -1.14 / -2.13; -4.34 / +0.06 | 0.10 / 0.67 | 0.04 / 0.62 | fail |
| EU-OPEN ALL V1 w15 k2 h15 none | 1058 / 505 | -0.98 (-1.47) / +0.72 (+1.13) | -2.51 / **-2.49 (-3.66)** / -2.47 / -2.49 / -2.34 | -0.14 / **-0.15 (-0.24)** / -0.17 / -0.16 / -0.23 | -3.06 / -0.41 | +0.06 | -2.94 / -0.22 | -1.95 / -0.18 | HOL n5 -13.34 (diff t +4.18) | -2.09 / -0.50; -1.28 / -1.02 | 0.01 / 0.89 | 0.00 / 0.96 | fail |
| EU-OPEN ALL V2 w15 k2 h15 none | 1058 / 505 | +0.98 (+1.47) / -0.72 (-1.13) | -0.50 / **-0.52 (-0.79)** / -0.53 / -0.52 / -0.65 | -1.61 / **-1.59 (-2.49)** / -1.59 / -1.60 / -1.52 | -1.09 / -1.85 | +3.06 | -0.63 / -2.24 | -0.42 / -1.87 | HOL n5 +7.74 (diff t -2.28) | -0.95 / -1.34; -1.71 / -0.73 | 0.98 / 0.10 | 1.00 / 0.04 | fail |
| EU-OPEN ALL V1 w15 k4 h15 none | 263 / 82 | -2.68 (-1.34) / +3.59 (+2.03) | -4.35 / **-4.33 (-2.12)** / -4.28 / -4.33 / -4.19 | +2.78 / **+2.75 (+1.56)** / +2.82 / +2.82 / +3.37 | -4.99 / +2.46 | -0.63 | -1.69 / +1.28 | -1.11 / +1.16 | - | -3.64 / -1.52; -0.79 / -0.06 | 0.01 / 0.98 | 0.00 / 0.97 | fail |
| EU-OPEN ALL V2 w15 k4 h15 none | 263 / 82 | +2.68 (+1.34) / -3.59 (-2.03) | +1.06 / **+1.03 (+0.52)** / +1.01 / +1.03 / +0.93 | -4.48 / **-4.44 (-2.51)** / -4.51 / -4.51 / -5.04 | +0.36 / -4.72 | -4.30 | +0.41 / -2.04 | +0.28 / -1.82 | - | +0.16 / -0.33; -2.40 / -1.52 | 0.97 / 0.01 | 1.00 / 0.03 | fail |
| NZ-07 NZDUSD V1 w15 k2 h15 none | 235 / 78 | -1.23 (-3.14) / -0.03 (-0.04) | -2.80 / **-2.80 (-6.71)** / -2.67 / -2.78 / -1.57 | -1.46 / **-1.47 (-2.17)** / -1.42 / -1.44 / -0.58 | -3.28 / -1.89 | +0.53 | -3.60 / -1.65 | -3.60 / -1.65 | HOL n10 -5.23 (diff t +1.65); SAT n76 -0.27 (diff t -2.98) | -0.75 / -0.87; -1.31 / +0.61 | 0.00 / 0.47 | 0.00 / 0.30 | fail |
| NZ-07 NZDUSD V2 w15 k2 h15 none | 235 / 78 | +1.23 (+3.14) / +0.03 (+0.04) | -0.35 / **-0.33 (-0.86)** / -0.40 / -0.38 / -1.05 | -1.42 / **-1.42 (-2.04)** / -1.52 / -1.41 / -1.77 | -0.81 / -1.84 | +4.28 | -0.46 / -1.55 | -0.46 / -1.55 | HOL n10 +2.66 (diff t -1.88); SAT n76 -2.26 (diff t +2.25) | -1.65 / -1.47; -1.16 / -3.03 | 1.00 / 0.52 | 0.97 / 0.34 | fail |
| NZ-07 NZDUSD V1 w15 k4 h15 none | 61 / 16 | -2.95 (-3.18) / -0.48 (-0.25) | -5.09 / **-5.09 (-4.90)** / -4.86 / -5.16 / -1.99 | -1.94 / **-1.98 (-1.00)** / -2.03 / -1.96 / -1.53 | -5.86 / -2.43 | +0.39 | -2.63 / -0.76 | -2.63 / -0.76 | HOL n4 -6.01 (diff t +0.44); SAT n16 +1.98 (diff t -2.98) | -0.70 / +1.29; -1.13 / +5.33 | 0.00 / 0.43 | 0.00 / 0.29 | fail |
| NZ-07 NZDUSD V2 w15 k4 h15 none | 61 / 16 | +2.95 (+3.18) / +0.48 (+0.25) | +0.75 / **+0.82 (+0.91)** / +0.69 / +0.85 / -1.06 | -1.07 / **-1.02 (-0.55)** / -1.36 / -1.00 / -0.99 | +0.05 / -1.47 | -1.24 | +0.49 / -0.42 | +0.49 / -0.42 | HOL n4 +3.27 (diff t -0.76); SAT n16 -4.82 (diff t +2.38) | -1.63 / -3.81; -1.36 / -8.04 | 1.00 / 0.60 | 0.96 / 0.56 | fail |
| NY-IMB INDICES V1 w15 k2 h15 none | 463 / 237 | +2.36 (+1.00) / -0.34 (-0.16) | +0.85 / **+0.85 (+0.36)** / +0.80 / +0.86 / -0.36 | -0.93 / **-0.95 (-0.45)** / -1.11 / -0.89 / -1.64 | +0.09 / -1.25 | -1.12 | +0.26 / -0.40 | +0.19 / -0.34 | - | -1.37 / +0.63; -1.91 / -1.33 | 0.91 / 0.41 | 0.99 / 0.37 | fail |
| NY-IMB INDICES V2 w15 k2 h15 none | 463 / 237 | -2.36 (-1.00) / +0.34 (+0.16) | -3.86 / **-3.87 (-1.63)** / -3.82 / -3.89 / -2.61 | -0.29 / **-0.27 (-0.13)** / -0.11 / -0.33 / +0.43 | -4.62 / -0.58 | +0.07 | -1.17 / -0.12 | -0.87 / -0.10 | - | -1.20 / -1.54; -1.05 / -0.32 | 0.08 / 0.61 | 0.01 / 0.56 | fail |
| NY-IMB INDICES V1 w15 k4 h15 none | 123 / 36 | +10.18 (+1.40) / +5.65 (+1.23) | +8.22 / **+8.30 (+1.14)** / +8.22 / +8.34 / +3.88 | +5.01 / **+5.09 (+1.10)** / +4.75 / +5.11 / +7.35 | +7.36 / +4.81 | +0.61 | +0.80 / +0.89 | +0.61 / +0.85 | - | +0.47 / +6.84; -3.47 / -2.38 | 0.97 / 0.91 | 1.00 / 0.96 | fail |
| NY-IMB INDICES V2 w15 k4 h15 none | 123 / 36 | -10.18 (-1.40) / -5.65 (-1.23) | -11.95 / **-12.05 (-1.66)** / -11.98 / -12.09 / -7.57 | -6.12 / **-6.21 (-1.35)** / -5.86 / -6.23 / -8.46 | -12.99 / -6.49 | +0.52 | -1.16 / -1.09 | -0.88 / -1.04 | - | -3.30 / -7.70; -0.83 / +0.74 | 0.02 / 0.10 | 0.00 / 0.04 | fail |
| SETTLE ALL V1 w15 k2 h15 none | 966 / 582 | -0.49 (-0.37) / +1.41 (+1.02) | -6.76 / **-6.81 (-5.03)** / -6.75 / -6.80 / -7.80 | -10.52 / **-10.54 (-6.87)** / -10.49 / -10.41 / -11.20 | -9.81 / -16.39 | +1.55 | -3.48 / -5.49 | -2.65 / -5.18 | - | -7.26 / -9.92; -6.55 / -10.35 | 0.33 / 0.86 | 0.34 / 0.87 | fail |
| SETTLE ALL V2 w15 k2 h15 none | 966 / 582 | +0.49 (+0.37) / -1.41 (-1.02) | -5.86 / **-5.82 (-4.42)** / -5.88 / -5.81 / -4.63 | -13.35 / **-13.36 (-8.44)** / -13.36 / -13.38 / -12.28 | -8.82 / -19.21 | +2.30 | -3.01 / -6.72 | -2.37 / -6.49 | - | -3.87 / -11.34; -3.85 / -9.76 | 0.65 / 0.09 | 0.72 / 0.19 | fail |
| SETTLE ALL V1 w15 k4 h15 none | 198 / 76 | -0.41 (-0.08) / +1.60 (+0.37) | -8.90 / **-9.31 (-1.88)** / -9.28 / -9.12 / -13.58 | -12.35 / **-12.20 (-2.53)** / -12.18 / -12.28 / -15.31 | -13.60 / -18.93 | +1.31 | -1.29 / -1.93 | -0.99 / -1.93 | - | -7.69 / -12.59; -5.59 / -14.40 | 0.46 / 0.64 | 0.44 / 0.71 | fail |
| SETTLE ALL V2 w15 k4 h15 none | 198 / 76 | +0.41 (+0.08) / -1.60 (-0.37) | -8.82 / **-8.48 (-1.71)** / -8.51 / -8.56 / -3.70 | -15.13 / **-15.40 (-3.03)** / -15.55 / -15.24 / -11.72 | -12.77 / -22.14 | +1.82 | -1.19 / -2.29 | -0.93 / -2.29 | - | -4.81 / -8.81; -6.18 / -9.12 | 0.55 / 0.39 | 0.51 / 0.33 | fail |

### Best cell per clock and family (largest IS net t)
| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CN-DAY AUDUSD V1 w15 k4 h60 none | 29 / 6 | +15.65 (+1.64) / +0.30 (+0.04) | +14.71 / **+14.59 (+1.55)** / +14.63 / +14.57 / +14.75 | -0.43 / **-0.43 (-0.05)** / -0.46 / -0.55 / -0.23 | +14.35 / -0.50 | -0.03 | +0.83 / -0.04 | +0.83 / -0.04 | HOL n5 -2.07 (diff t +1.46) | +3.17 / -0.98; -4.17 / -2.43 | 1.00 / 0.48 | 1.00 / 0.47 | fail |
| CN-DAY AUDUSD V2 w60 k2 h60 none | 165 / 84 | +3.66 (+1.76) / +1.01 (+0.56) | +2.68 / **+2.68 (+1.30)** / +2.65 / +2.69 / +2.50 | +0.27 / **+0.28 (+0.16)** / +0.31 / +0.30 / +0.20 | +2.48 / +0.22 | +0.10 | +0.70 / +0.12 | +0.70 / +0.12 | HOL n18 -4.43 (diff t +1.91) | -2.99 / +0.45; +0.42 / +0.45 | 0.98 / 0.70 | 1.00 / 0.82 | fail |
| CN-PM XAUUSD V1 w15 k4 h60 none | 66 / 27 | +7.31 (+2.36) / +4.74 (+1.50) | +5.49 / **+5.48 (+1.76)** / +5.50 / +5.48 / +4.98 | +3.51 / **+3.63 (+1.15)** / +3.76 / +3.71 / +2.29 | +4.86 / +3.38 | +0.66 | +0.94 / +0.87 | +0.94 / +0.87 | - | -5.55 / -1.50; -0.62 / -4.03 | 0.99 / 0.92 | 0.99 / 0.88 | fail |
| CN-PM XTIUSD V2 w15 k4 h60 S | 28 / 27 | +19.66 (+1.97) / -1.20 (-0.27) | +8.68 / **+8.48 (+0.86)** / +8.33 / +9.73 / +6.90 | -4.30 / **-4.56 (-1.02)** / -4.29 / -4.46 / -7.23 | +2.89 / -6.24 | -0.54 | +0.59 / -0.78 | +0.59 / -0.78 | HOL n3 +42.70 (diff t -0.74) | -14.73 / -3.11; -27.30 / -8.78 | 0.80 / 0.62 | 0.91 / 0.54 | fail |
| CN-NIGHT AUDUSD V1 w15 k4 h60 none | 28 / 11 | +7.63 (+2.35) / -0.84 (-0.05) | +6.69 / **+6.78 (+2.09)** / +6.90 / +6.87 / +7.53 | -1.53 / **-1.53 (-0.10)** / -1.66 / -1.52 / +2.31 | +6.65 / -1.58 | -0.23 | +1.12 / -0.07 | +1.12 / -0.07 | HOL n8 -3.23 (diff t +1.28) | -1.03 / +1.46; -0.50 / -3.93 | 0.98 / 0.46 | 1.00 / 0.43 | fail |
| CN-NIGHT XAGUSD V2 w15 k2 h60 none | 129 / 55 | +8.66 (+1.71) / +18.92 (+1.99) | +4.90 / **+4.75 (+0.94)** / +4.90 / +5.02 / +2.20 | +14.40 / **+14.42 (+1.52)** / +14.76 / +14.50 / +13.74 | +3.10 / +12.47 | +3.04 | +0.50 / +1.15 | +0.50 / +1.15 | HOL n5 -34.28 (diff t +1.44) | -8.25 / -8.33; -8.80 / -15.00 | 0.96 / 0.97 | 0.99 / 0.99 | fail |
| CNY-FIX ALL V1 w15 k4 h15 S | 120 / 68 | +2.20 (+1.71) / -0.51 (-0.49) | +0.76 / **+0.80 (+0.62)** / +0.36 / -0.00 / -0.17 | -1.56 / **-1.61 (-1.55)** / -1.77 / -1.39 / -1.44 | +0.41 / -1.87 | -2.01 | +0.37 / -1.41 | +0.33 / -1.16 | HOL n7 -3.15 (diff t +3.25) | -1.56 / -0.23; -0.67 / -1.80 | 0.93 / 0.35 | 1.00 / 0.09 | fail |
| CNY-FIX AUDUSD V2 w15 k4 h60 none | 30 / 22 | +9.59 (+1.41) / +1.47 (+0.41) | +8.58 / **+8.43 (+1.26)** / +8.51 / +8.48 / +7.99 | +0.73 / **+0.73 (+0.20)** / +0.86 / +0.70 / +1.32 | +8.16 / +0.66 | +0.09 | +0.68 / +0.16 | +0.68 / +0.16 | HOL n2 +6.00 (diff t -0.17) | +2.71 / -0.05; -3.12 / +8.09 | 0.92 / 0.67 | 0.99 / 0.68 | fail |
| EU-OPEN NZDUSD V1 w60 k4 h60 none | 20 / 10 | +6.49 (+1.43) / -2.07 (-0.32) | +5.26 / **+5.22 (+1.16)** / +5.01 / +5.27 / +6.17 | -3.20 / **-3.34 (-0.52)** / -3.34 / -3.11 / -1.23 | +4.88 / -3.68 | -0.64 | +0.62 / -0.39 | +0.62 / -0.39 | - | -3.15 / -2.10; +1.23 / -1.10 | 0.92 / 0.36 | 0.90 / 0.38 | fail |
| EU-OPEN US30 V2 w60 k4 h15 none | 59 / 14 | +10.42 (+2.50) / +4.97 (+0.91) | +9.25 / **+9.26 (+2.23)** / +9.41 / +9.34 / +7.49 | +4.41 / **+4.65 (+0.85)** / +4.49 / +4.51 / +1.61 | +8.67 / +4.48 | +0.50 | +1.20 / +0.65 | +1.20 / +0.65 | - | +0.24 / -2.57; -4.03 / -2.93 | 1.00 / 0.81 | 1.00 / 0.92 | DEMO numbers, within chance |
| EU-OPEN DE40(min) V1 w60 k2 h5 none | 190 / 96 | +0.32 (+0.19) / -0.05 (-0.03) | -0.62 / **-0.62 (-0.37)** / - / - / -2.09 | -0.47 / **-0.47 (-0.24)** / - / - / -1.21 | -1.10 / -0.68 | +0.75 | -0.20 / -0.19 | -0.20 / -0.19 | - | -1.50 / -0.55; -0.83 / -1.16 | 0.55 / 0.50 | 1.00 / 0.70 | fail |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | 42 / 14 | +15.36 (+2.46) / +18.37 (+2.58) | +13.15 / **+13.15 (+2.12)** / - / - / +12.85 | +17.07 / **+17.07 (+2.40)** / - / - / +23.44 | +12.05 / +16.42 | +1.30 | +1.14 / +1.82 | +1.14 / +1.82 | - | -1.71 / -9.59; +6.10 / -6.44 | 0.99 / 0.99 | 1.00 / 1.00 | DEMO numbers, within chance |
| NZ-07 AUDUSD V1 w60 k4 h5 S | 36 / 14 | +1.55 (+1.10) / +2.82 (+2.02) | +0.40 / **+0.55 (+0.39)** / +0.52 / +0.31 / +0.63 | +2.14 / **+2.12 (+1.51)** / +1.93 / +2.10 / +2.15 | +0.34 / +2.08 | +3.89 | +0.21 / +1.15 | +0.21 / +1.15 | HOL n4 -1.17 (diff t +1.01); SAT n24 -2.14 (diff t +2.47) | -1.14 / -0.16; -1.24 / -0.76 | 0.80 / 1.00 | 0.93 / 1.00 | fail |
| NZ-07 NZDUSD V2 w15 k4 h60 none | 59 / 15 | +4.50 (+2.32) / +0.95 (+0.24) | +2.31 / **+2.40 (+1.25)** / +2.35 / +2.45 / +0.56 | -0.68 / **-0.65 (-0.17)** / -1.10 / -0.65 / -0.93 | +1.65 / -1.15 | -0.27 | +0.67 / -0.13 | +0.67 / -0.13 | HOL n2 -5.73 (diff t +0.98); SAT n15 -4.81 (diff t +1.29) | -3.04 / -3.85; -1.56 / -3.61 | 0.99 / 0.56 | 0.96 / 0.56 | fail |
| NY-IMB US30 V1 w15 k2 h15 S | 244 / 111 | +4.61 (+2.76) / -2.60 (-2.44) | +3.64 / **+3.56 (+2.13)** / +4.13 / +3.59 / +0.29 | -2.72 / **-2.87 (-2.69)** / -2.73 / -2.83 / -2.20 | +3.04 / -3.01 | -0.81 | +1.15 / -2.04 | +1.15 / -2.04 | - | -0.30 / +1.22; -2.24 / -1.19 | 1.00 / 0.02 | 1.00 / 0.00 | fail |
| NY-IMB USTEC V2 w60 k4 h5 S | 57 / 18 | +6.02 (+1.25) / -4.99 (-1.30) | +4.30 / **+4.19 (+0.87)** / +3.61 / +4.08 / -2.43 | -5.56 / **-5.53 (-1.44)** / -4.28 / -5.39 / -8.49 | +3.27 / -5.80 | -1.32 | +0.47 / -1.10 | +0.47 / -1.10 | - | +0.32 / -4.41; -4.15 / +0.03 | 0.90 / 0.14 | 0.98 / 0.00 | fail |
| SETTLE XNGUSD V1 w15 k4 h60 none | 28 / 19 | +29.94 (+1.68) / +25.46 (+1.09) | +13.77 / **+14.20 (+0.80)** / +13.71 / +13.93 / -2.46 | -18.99 / **-18.58 (-0.80)** / -18.94 / -19.15 / -32.57 | +6.33 / -40.60 | -1.31 | +0.53 / -0.60 | +0.53 / -0.60 | - | -56.55 / -16.26; -27.41 / -32.62 | 0.95 / 0.85 | 0.89 / 0.88 | fail |
| SETTLE XBRUSD V2 w60 k4 h60 S | 32 / 17 | +23.03 (+2.47) / +2.39 (+0.32) | +13.58 / **+13.19 (+1.45)** / +13.28 / +13.27 / +13.67 | +0.34 / **+0.03 (+0.00)** / -1.48 / -0.99 / +1.09 | +8.27 / -1.14 | +0.00 | +0.95 / +0.00 | +0.95 / +0.00 | - | +0.31 / -8.85; -9.32 / +9.17 | 0.97 / 0.63 | 0.99 / 0.75 | fail |

### Cells meeting the DEMO numbers
| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EU-OPEN US30 V2 w60 k4 h15 none | 59 / 14 | +10.42 (+2.50) / +4.97 (+0.91) | +9.25 / **+9.26 (+2.23)** / +9.41 / +9.34 / +7.49 | +4.41 / **+4.65 (+0.85)** / +4.49 / +4.51 / +1.61 | +8.67 / +4.48 | +0.50 | +1.20 / +0.65 | +1.20 / +0.65 | - | +0.24 / -2.57; -4.03 / -2.93 | 1.00 / 0.81 | 1.00 / 0.92 | DEMO numbers, within chance |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | 42 / 14 | +15.36 (+2.46) / +18.37 (+2.58) | +13.15 / **+13.15 (+2.12)** / - / - / +12.85 | +17.07 / **+17.07 (+2.40)** / - / - / +23.44 | +12.05 / +16.42 | +1.30 | +1.14 / +1.82 | +1.14 / +1.82 | - | -1.71 / -9.59; +6.10 / -6.44 | 0.99 / 0.99 | 1.00 / 1.00 | DEMO numbers, within chance |

### All cells with IS net t >= 2.0
| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EU-OPEN US30 V2 w60 k4 h15 none | 59 / 14 | +10.42 (+2.50) / +4.97 (+0.91) | +9.25 / **+9.26 (+2.23)** / +9.41 / +9.34 / +7.49 | +4.41 / **+4.65 (+0.85)** / +4.49 / +4.51 / +1.61 | +8.67 / +4.48 | +0.50 | +1.20 / +0.65 | +1.20 / +0.65 | - | +0.24 / -2.57; -4.03 / -2.93 | 1.00 / 0.81 | 1.00 / 0.92 | DEMO numbers, within chance |
| EU-OPEN US30 V2 w60 k4 h60 none | 48 / 13 | +16.71 (+2.33) / -6.64 (-0.76) | +15.50 / **+15.52 (+2.18)** / +15.92 / +15.60 / +14.65 | -7.12 / **-6.96 (-0.79)** / -7.12 / -7.05 / -9.81 | +14.93 / -7.12 | -0.45 | +1.17 / -0.60 | +1.17 / -0.60 | - | +5.79 / -3.56; +6.60 / -2.80 | 0.99 / 0.26 | 0.99 / 0.15 | fail |
| NY-IMB US30 V1 w15 k2 h15 S | 244 / 111 | +4.61 (+2.76) / -2.60 (-2.44) | +3.64 / **+3.56 (+2.13)** / +4.13 / +3.59 / +0.29 | -2.72 / **-2.87 (-2.69)** / -2.73 / -2.83 / -2.20 | +3.04 / -3.01 | -0.81 | +1.15 / -2.04 | +1.15 / -2.04 | - | -0.30 / +1.22; -2.24 / -1.19 | 1.00 / 0.02 | 1.00 / 0.00 | fail |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | 42 / 14 | +15.36 (+2.46) / +18.37 (+2.58) | +13.15 / **+13.15 (+2.12)** / - / - / +12.85 | +17.07 / **+17.07 (+2.40)** / - / - / +23.44 | +12.05 / +16.42 | +1.30 | +1.14 / +1.82 | +1.14 / +1.82 | - | -1.71 / -9.59; +6.10 / -6.44 | 0.99 / 0.99 | 1.00 / 1.00 | DEMO numbers, within chance |
| CN-NIGHT AUDUSD V1 w15 k4 h60 none | 28 / 11 | +7.63 (+2.35) / -0.84 (-0.05) | +6.69 / **+6.78 (+2.09)** / +6.90 / +6.87 / +7.53 | -1.53 / **-1.53 (-0.10)** / -1.66 / -1.52 / +2.31 | +6.65 / -1.58 | -0.23 | +1.12 / -0.07 | +1.12 / -0.07 | HOL n8 -3.23 (diff t +1.28) | -1.03 / +1.46; -0.50 / -3.93 | 0.98 / 0.46 | 1.00 / 0.43 | fail |
| EU-OPEN US30 V2 w60 k4 h5 none | 60 / 17 | +6.06 (+2.55) / -2.15 (-0.81) | +4.79 / **+4.87 (+2.07)** / +5.04 / +4.83 / +5.44 | -2.51 / **-2.47 (-0.93)** / -2.68 / -2.63 / -1.54 | +4.28 / -2.63 | -0.51 | +1.11 / -0.71 | +1.11 / -0.71 | - | -0.52 / +0.42; -3.11 / -1.69 | 0.99 / 0.17 | 1.00 / 0.16 | fail |
| NY-IMB US30 V1 w15 k2 h60 S | 231 / 111 | +5.61 (+2.57) / -2.94 (-2.34) | +4.68 / **+4.48 (+2.06)** / +5.37 / +4.54 / +0.66 | -2.98 / **-3.21 (-2.55)** / -2.91 / -3.20 / -2.25 | +3.92 / -3.35 | -0.72 | +1.10 / -1.94 | +1.10 / -1.94 | - | -1.81 / +2.13; - / - | 0.99 / 0.02 | 1.00 / 0.00 | fail |
| NY-IMB INDICES V1 w15 k4 h15 S | 123 / 36 | +12.50 (+2.39) / +0.03 (+0.01) | +10.74 / **+10.72 (+2.05)** / +11.31 / +10.44 / +2.26 | -2.98 / **-0.46 (-0.10)** / -2.90 / -0.54 / +4.61 | +9.83 / -0.70 | -0.04 | +1.44 / -0.08 | +1.09 / -0.08 | - | +0.11 / +6.86; -4.38 / -1.66 | 0.99 / 0.54 | 1.00 / 0.54 | fail |

### By year, best cells (net bp at the decision latency, n)
| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | years > 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| CN-DAY AUDUSD V1 w15 k4 h60 none | - | +5.3 (5) | +2.1 (11) | +33.0 (1) | +31.9 (10) | +11.2 (2) | -2.1 (4) | +3.0 (2) | - | 6/7 |
| CN-DAY AUDUSD V2 w60 k2 h60 none | +1.1 (25) | +2.7 (28) | +0.4 (33) | +2.9 (21) | +8.4 (27) | +1.2 (31) | +1.4 (35) | +0.4 (26) | -1.6 (23) | 8/9 |
| CN-PM XAUUSD V1 w15 k4 h60 none | +9.6 (14) | +5.4 (6) | -6.8 (9) | +7.4 (18) | +16.3 (12) | -10.3 (7) | +8.7 (8) | +0.4 (8) | +2.3 (11) | 7/9 |
| CN-PM XTIUSD V2 w15 k4 h60 S | - | - | +16.7 (4) | +11.1 (5) | +9.3 (11) | +1.7 (8) | -7.7 (8) | -3.7 (8) | -2.9 (11) | 4/7 |
| CN-NIGHT AUDUSD V1 w15 k4 h60 none | - | -3.0 (5) | +7.2 (5) | +2.5 (6) | +18.1 (6) | +7.5 (6) | +63.0 (2) | -16.0 (5) | -15.8 (4) | 5/8 |
| CN-NIGHT XAGUSD V2 w15 k2 h60 none | -4.7 (13) | -4.3 (16) | +14.0 (24) | -0.1 (32) | +5.1 (23) | +13.8 (21) | +9.9 (20) | +20.9 (17) | +13.3 (18) | 6/9 |
| CNY-FIX ALL V1 w15 k4 h15 S | -1.7 (17) | +4.3 (15) | -1.8 (15) | +2.5 (29) | -0.7 (29) | +2.4 (15) | -2.7 (34) | +0.2 (16) | -1.2 (18) | 4/9 |
| CNY-FIX AUDUSD V2 w15 k4 h60 none | +1.2 (3) | +18.9 (5) | -4.3 (4) | -14.0 (6) | +28.9 (9) | -1.5 (3) | +2.9 (10) | -6.4 (8) | +9.5 (4) | 5/9 |
| EU-OPEN NZDUSD V1 w60 k4 h60 none | +9.5 (3) | -20.7 (2) | +2.6 (2) | +10.6 (2) | +9.6 (7) | +6.0 (4) | -10.2 (5) | - | +3.5 (5) | 6/8 |
| EU-OPEN US30 V2 w60 k4 h15 none | -3.8 (1) | +0.5 (2) | +4.5 (21) | -4.0 (7) | +27.4 (17) | +1.5 (11) | -6.6 (8) | +36.2 (1) | +16.4 (5) | 6/9 |
| EU-OPEN DE40(min) V1 w60 k2 h5 none | +1.0 (16) | +0.8 (26) | -3.2 (43) | +1.7 (36) | -7.3 (36) | +5.6 (33) | -4.0 (31) | +4.4 (33) | -2.1 (32) | 5/9 |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | +18.1 (4) | +18.4 (1) | +11.9 (11) | -1.0 (8) | +20.5 (16) | +5.6 (2) | +20.0 (5) | +36.1 (3) | +5.2 (6) | 8/9 |
| NZ-07 AUDUSD V1 w60 k4 h5 S | +0.9 (4) | -4.7 (1) | -2.8 (2) | -3.5 (3) | +2.6 (19) | -1.6 (7) | -0.8 (7) | +6.9 (4) | +2.5 (3) | 4/9 |
| NZ-07 NZDUSD V2 w15 k4 h60 none | -6.2 (3) | -4.3 (3) | +5.2 (6) | -2.2 (10) | +10.4 (12) | +1.6 (25) | +12.5 (3) | -9.2 (4) | -1.3 (8) | 4/9 |
| NY-IMB US30 V1 w15 k2 h15 S | -0.7 (21) | -0.3 (30) | +7.1 (66) | -3.7 (34) | +9.8 (49) | +1.6 (44) | -6.9 (41) | -3.6 (25) | +1.2 (45) | 4/9 |
| NY-IMB USTEC V2 w60 k4 h5 S | +0.9 (3) | -6.5 (3) | -6.1 (7) | +0.1 (6) | +11.4 (28) | -2.0 (10) | -10.9 (6) | +10.9 (2) | -5.6 (10) | 4/9 |
| SETTLE XNGUSD V1 w15 k4 h60 none | - | - | -20.6 (10) | +16.6 (3) | +57.3 (9) | +6.3 (6) | -28.7 (5) | -31.4 (7) | +1.5 (7) | 4/7 |
| SETTLE XBRUSD V2 w60 k4 h60 S | - | - | +17.3 (10) | -3.4 (3) | +21.8 (14) | -9.2 (5) | -14.4 (6) | +29.6 (2) | +3.1 (9) | 4/7 |

### Best cells: winsorised, without March-April 2020, spread paid, stop hits
| cell | net IS / VAL | winsorised IS / VAL | IS ex Mar-Apr 2020 | spread paid IS / VAL | stop-hit share IS / VAL |
|---|---|---|---|---|---|
| CN-DAY AUDUSD V1 w15 k4 h60 none | +14.59 / -0.43 | +12.27 / +0.06 | +4.20 | +0.47 / +0.13 | - / - |
| CN-DAY AUDUSD V2 w60 k2 h60 none | +2.68 / +0.28 | +1.31 / +0.62 | +1.06 | +0.38 / +0.13 | - / - |
| CN-PM XAUUSD V1 w15 k4 h60 none | +5.48 / +3.63 | +5.17 / +3.63 | +4.92 | +1.23 / +0.51 | - / - |
| CN-PM XTIUSD V2 w15 k4 h60 S | +8.48 / -4.56 | +8.14 / -4.56 | +9.42 | +11.18 / +3.36 | 0.50 / 0.70 |
| CN-NIGHT AUDUSD V1 w15 k4 h60 none | +6.78 / -1.53 | +6.77 / -1.37 | +6.78 | +0.25 / +0.10 | - / - |
| CN-NIGHT XAGUSD V2 w15 k2 h60 none | +4.75 / +14.42 | +4.58 / +15.61 | +4.75 | +3.31 / +3.90 | - / - |
| CNY-FIX ALL V1 w15 k4 h15 S | +0.80 / -1.61 | +0.74 / -1.61 | +1.44 | +0.80 / +0.50 | 0.69 / 0.69 |
| CNY-FIX AUDUSD V2 w15 k4 h60 none | +8.43 / +0.73 | +7.53 / +0.73 | +2.74 | +0.55 / +0.14 | - / - |
| EU-OPEN NZDUSD V1 w60 k4 h60 none | +5.22 / -3.34 | +5.05 / -2.60 | +3.25 | +0.67 / +0.67 | - / - |
| EU-OPEN US30 V2 w60 k4 h15 none | +9.26 / +4.65 | +9.04 / +5.15 | +2.69 | +1.17 / +0.32 | - / - |
| EU-OPEN DE40(min) V1 w60 k2 h5 none | -0.62 / -0.47 | -0.30 / -0.53 | +1.09 | +0.94 / +0.42 | - / - |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | +13.15 / +17.07 | +12.96 / +17.07 | +5.49 | +2.20 / +1.30 | - / - |
| NZ-07 AUDUSD V1 w60 k4 h5 S | +0.55 / +2.12 | +0.20 / +2.12 | -1.69 | +0.41 / +0.09 | 0.31 / 0.14 |
| NZ-07 NZDUSD V2 w15 k4 h60 none | +2.40 / -0.65 | +2.15 / -0.45 | +0.96 | +1.50 / +1.00 | - / - |
| NY-IMB US30 V1 w15 k2 h15 S | +3.56 / -2.87 | +3.69 / -2.87 | +2.93 | +1.04 / +0.27 | 0.61 / 0.64 |
| NY-IMB USTEC V2 w60 k4 h5 S | +4.19 / -5.53 | +3.75 / -5.53 | -3.77 | +1.83 / +0.54 | 0.26 / 0.28 |
| SETTLE XNGUSD V1 w15 k4 h60 none | +14.20 / -18.58 | +13.95 / -14.19 | +2.15 | +15.74 / +44.04 | - / - |
| SETTLE XBRUSD V2 w60 k4 h60 S | +13.19 / +0.03 | +12.92 / +0.03 | +13.01 | +9.84 / +2.35 | 0.16 / 0.29 |

## 3. Does the opening move predict the next minutes at mid?
### The 20 cells with the largest |IS mid t| (V1 orientation: + continues, - reverses)
| cell | n IS / VAL | mid IS (t) | mid VAL (t) | net V1 IS / VAL | net V2 IS / VAL | spread paid IS / VAL |
|---|---|---|---|---|---|---|
| NZ-07 NZDUSD w15 k2 h5 | 236 / 78 | -1.26 (-4.41) | +0.46 (+0.92) | -2.84 / -0.97 | -0.31 / -1.89 | +0.97 / +0.83 |
| NZ-07 NZDUSD w15 k0 h5 | 973 / 361 | -0.50 (-4.39) | -0.07 (-0.32) | -1.90 / -1.40 | -0.89 / -1.26 | +0.80 / +0.73 |
| NZ-07 NZDUSD w15 k4 h5 | 61 / 16 | -2.60 (-4.31) | +0.24 (+0.16) | -4.78 / -1.26 | +0.42 / -1.74 | +1.58 / +0.90 |
| SETTLE METALS w15 k0 h15 | 2365 / 1213 | -0.95 (-3.50) | -0.40 (-1.12) | -3.69 / -3.04 | -1.79 / -2.24 | +2.14 / +2.04 |
| NZ-07 FX w15 k4 h5 | 124 / 25 | -1.48 (-3.24) | +0.99 (+0.87) | -3.08 / -0.22 | -0.13 / -2.20 | +1.01 / +0.61 |
| NZ-07 FX w15 k2 h5 | 505 / 149 | -0.76 (-3.18) | +0.51 (+1.17) | -2.01 / -0.58 | -0.49 / -1.59 | +0.65 / +0.48 |
| NZ-07 NZDUSD w15 k4 h15 | 61 / 16 | -2.95 (-3.18) | -0.48 (-0.25) | -5.09 / -1.98 | +0.82 / -1.02 | +1.53 / +0.90 |
| NZ-07 NZDUSD w15 k2 h15 | 235 / 78 | -1.23 (-3.14) | -0.03 (-0.04) | -2.80 / -1.47 | -0.33 / -1.42 | +0.96 / +0.85 |
| NZ-07 FX w15 k4 h15 | 124 / 25 | -2.18 (-3.04) | +0.68 (+0.47) | -3.77 / -0.53 | +0.59 / -1.90 | +0.99 / +0.62 |
| EU-OPEN ALL w60 k2 h5 | 1066 / 570 | -1.05 (-3.00) | +0.64 (+1.44) | -2.63 / -0.25 | -0.52 / -1.54 | +1.22 / +0.54 |
| SETTLE METALS w60 k0 h5 | 2430 / 1229 | -0.48 (-2.99) | -0.59 (-2.75) | -3.25 / -3.24 | -2.29 / -2.07 | +2.17 / +2.05 |
| EU-OPEN ALL w60 k4 h5 | 226 / 88 | -3.54 (-2.91) | +1.57 (+1.18) | -5.43 / +0.68 | +1.64 / -2.47 | +1.63 / +0.58 |
| SETTLE METALS w60 k0 h15 | 2419 / 1225 | -0.78 (-2.91) | -0.78 (-2.20) | -3.55 / -3.43 | -1.99 / -1.87 | +2.17 / +2.05 |
| NZ-07 FX w15 k2 h15 | 503 / 149 | -0.96 (-2.90) | +0.29 (+0.48) | -2.21 / -0.80 | -0.29 / -1.38 | +0.65 / +0.49 |
| SETTLE METALS w60 k0 h60 | 2269 / 1169 | -1.40 (-2.84) | -0.88 (-1.47) | -4.19 / -3.52 | -1.39 / -1.77 | +2.19 / +2.05 |
| SETTLE XNGUSD w60 k0 h5 | 668 / 615 | -3.11 (-2.81) | -2.18 (-1.53) | -15.86 / -43.73 | -9.64 / -39.36 | +12.75 / +41.55 |
| NY-IMB US30 w15 k0 h60 | 1094 / 612 | +2.36 (+2.72) | -0.74 (-1.00) | +1.20 / -1.03 | -3.52 / +0.45 | +1.16 / +0.29 |
| CN-DAY XTIUSD w15 k0 h60 | 548 / 463 | -5.48 (-2.69) | +0.42 (+0.20) | -12.65 / -3.03 | -1.69 / -3.86 | +7.17 / +3.45 |
| SETTLE METALS w60 k2 h15 | 484 / 242 | -2.15 (-2.69) | -0.53 (-0.62) | -4.96 / -3.22 | -0.66 / -2.16 | +2.21 / +2.09 |
| SETTLE XAGUSD w15 k0 h15 | 1149 / 598 | -1.31 (-2.66) | -0.24 (-0.37) | -5.43 / -4.57 | -2.82 / -4.10 | +3.52 / +3.73 |

### Mid direction per clock and set (V1 orientation, w 15 s, h 15 min, no stop): IS (t) / VAL (t)
| clock | set | k0 IS / VAL | k2 IS / VAL | k4 IS / VAL | round trip paid k2 IS / VAL |
|---|---|---|---|---|---|
| CN-DAY | XAUUSD | +0.43 (+1.2) / +0.64 (+1.4) | +1.60 (+1.9) / +0.89 (+0.7) | +1.17 (+0.6) / +6.43 (+1.8) | 1.28 / 0.54 |
| CN-DAY | XAGUSD | +1.35 (+1.6) / +1.38 (+1.3) | +2.99 (+1.4) / +2.19 (+0.7) | -3.13 (-0.6) / +4.72 (+0.6) | 4.65 / 4.75 |
| CN-DAY | XPTUSD | +0.63 (+0.8) / -0.61 (-0.9) | -2.07 (-1.1) / +0.00 (+0.0) | -5.95 (-1.1) / +3.75 (+1.3) | 26.44 / 32.10 |
| CN-DAY | AUDUSD | -0.07 (-0.3) / +0.22 (+0.7) | +0.30 (+0.6) / +0.61 (+0.9) | +1.41 (+1.1) / -0.18 (-0.1) | 0.40 / 0.13 |
| CN-DAY | XTIUSD | -0.87 (-0.8) / +0.77 (+0.6) | -1.70 (-0.6) / +8.41 (+2.6) | +4.04 (+0.7) / +11.36 (+1.4) | 8.21 / 3.43 |
| CN-DAY | XBRUSD | -0.08 (-0.1) / +2.57 (+1.2) | +0.55 (+0.2) / +11.01 (+2.1) | +17.62 (+1.9) / +18.84 (+2.0) | 6.46 / 2.60 |
| CN-DAY | METALS | +0.81 (+1.7) / +0.47 (+0.8) | +1.17 (+1.0) / +0.98 (+0.6) | -2.17 (-0.7) / +4.77 (+1.2) | 8.76 / 13.03 |
| CN-DAY | ENERGY | -0.55 (-0.6) / +1.33 (+1.0) | -0.80 (-0.3) / +9.24 (+2.7) | +8.03 (+1.3) / +14.74 (+1.8) | 7.51 / 3.17 |
| CN-DAY | ALL | +0.34 (+0.9) / +0.64 (+1.3) | +0.55 (+0.6) / +2.92 (+2.2) | +0.98 (+0.4) / +7.37 (+2.1) | 6.86 / 8.23 |
| CN-PM | XAUUSD | +0.29 (+1.2) / +0.46 (+1.5) | +1.40 (+2.2) / -0.14 (-0.2) | +3.75 (+2.2) / +3.38 (+1.8) | 1.03 / 0.49 |
| CN-PM | XAGUSD | +0.69 (+1.1) / +0.79 (+1.0) | +0.91 (+0.6) / -1.44 (-0.7) | +0.29 (+0.1) / +2.37 (+0.6) | 3.90 / 4.29 |
| CN-PM | XPTUSD | -0.43 (-0.7) / -0.41 (-0.7) | -0.37 (-0.3) / -1.04 (-0.8) | +0.05 (+0.0) / -2.88 (-1.0) | 27.29 / 31.49 |
| CN-PM | AUDUSD | -0.24 (-1.6) / -0.21 (-0.9) | -0.78 (-2.6) / +0.10 (+0.2) | -0.98 (-1.1) / -1.37 (-0.9) | 0.37 / 0.10 |
| CN-PM | XTIUSD | +1.73 (+1.8) / +0.03 (+0.0) | +1.92 (+0.6) / +0.71 (+0.3) | +2.61 (+0.2) / -5.86 (-1.2) | 8.81 / 3.49 |
| CN-PM | XBRUSD | +1.46 (+1.7) / +0.56 (+0.7) | +2.82 (+1.2) / +0.76 (+0.4) | +7.38 (+1.1) / -5.45 (-1.0) | 7.38 / 2.66 |
| CN-PM | METALS | +0.25 (+0.7) / +0.28 (+0.6) | +0.72 (+0.8) / -0.88 (-0.8) | +1.52 (+0.7) / +0.83 (+0.4) | 9.65 / 12.48 |
| CN-PM | ENERGY | +1.59 (+1.8) / +0.29 (+0.4) | +2.41 (+0.9) / +0.74 (+0.4) | +5.40 (+0.7) / -5.65 (-1.1) | 8.03 / 3.08 |
| CN-PM | ALL | +0.43 (+1.4) / +0.20 (+0.5) | +0.74 (+0.9) / -0.26 (-0.3) | +1.95 (+0.8) / -1.63 (-0.9) | 7.12 / 7.91 |
| CN-NIGHT | XAUUSD | -0.19 (-0.4) / -0.92 (-1.7) | +0.13 (+0.1) / -0.07 (-0.0) | -1.40 (-0.5) / -6.05 (-2.8) | 0.80 / 0.39 |
| CN-NIGHT | XAGUSD | -1.08 (-1.1) / -0.81 (-0.6) | -4.25 (-1.8) / -6.38 (-1.8) | +5.51 (+0.8) / -5.04 (-0.5) | 3.34 / 3.96 |
| CN-NIGHT | AUDUSD | -0.11 (-0.5) / +0.79 (+2.0) | -0.86 (-1.8) / -0.08 (-0.1) | -0.00 (-0.0) / +4.34 (+0.8) | 0.29 / 0.09 |
| CN-NIGHT | XTIUSD | +3.79 (+2.4) / +0.49 (+0.2) | +7.62 (+1.6) / +2.11 (+0.3) | +31.54 (+2.2) / +5.03 (+0.3) | 7.17 / 3.61 |
| CN-NIGHT | XBRUSD | +1.99 (+1.6) / -0.10 (-0.1) | +5.19 (+1.4) / -0.09 (-0.0) | +17.26 (+1.3) / +12.05 (+0.8) | 6.57 / 2.72 |
| CN-NIGHT | METALS | -0.62 (-1.0) / -0.86 (-1.1) | -2.06 (-1.4) / -3.00 (-1.5) | +2.10 (+0.6) / -5.63 (-1.3) | 2.08 / 2.05 |
| CN-NIGHT | ENERGY | +2.89 (+2.1) / +0.20 (+0.1) | +6.39 (+1.6) / +1.00 (+0.2) | +24.91 (+1.9) / +8.54 (+0.6) | 6.87 / 3.16 |
| CN-NIGHT | ALL | +0.52 (+1.0) / -0.12 (-0.1) | +0.62 (+0.5) / -0.88 (-0.4) | +8.80 (+2.0) / +1.98 (+0.3) | 2.96 / 2.05 |
| CNY-FIX | AUDUSD | -0.12 (-0.4) / -0.46 (-1.4) | +0.28 (+0.5) / +0.03 (+0.0) | +0.68 (+0.3) / -0.09 (-0.0) | 0.41 / 0.13 |
| CNY-FIX | NZDUSD | +0.51 (+2.1) / -0.61 (-1.9) | +0.83 (+1.5) / -0.25 (-0.3) | +1.15 (+0.7) / -1.08 (-0.7) | 0.66 / 0.72 |
| CNY-FIX | XAUUSD | +0.21 (+0.8) / -0.15 (-0.4) | +1.20 (+1.5) / +0.42 (+0.4) | +3.51 (+1.2) / -0.16 (-0.1) | 1.13 / 0.54 |
| CNY-FIX | FX | +0.19 (+0.8) / -0.54 (-1.8) | +0.55 (+1.1) / -0.10 (-0.1) | +0.94 (+0.6) / -0.59 (-0.4) | 0.54 / 0.41 |
| CNY-FIX | ALL | +0.20 (+1.1) / -0.39 (-1.6) | +0.78 (+1.8) / +0.08 (+0.1) | +1.86 (+1.2) / -0.46 (-0.3) | 0.75 / 0.46 |
| EU-OPEN | US30 | -0.68 (-1.6) / -0.06 (-0.1) | -3.55 (-2.4) / -0.53 (-0.4) | -6.63 (-1.5) / +0.99 (+0.3) | 1.05 / 0.31 |
| EU-OPEN | USTEC | -0.10 (-0.2) / +0.93 (+1.5) | -0.98 (-0.8) / +3.08 (+1.8) | -3.13 (-1.0) / +8.75 (+2.2) | 2.96 / 1.17 |
| EU-OPEN | XAUUSD | +0.00 (+0.0) / +0.05 (+0.1) | -0.59 (-0.8) / +0.09 (+0.1) | +0.58 (+0.3) / +0.04 (+0.0) | 0.85 / 0.42 |
| EU-OPEN | AUDUSD | +0.21 (+0.8) / -0.17 (-0.4) | -0.03 (-0.1) / +0.67 (+0.7) | -1.89 (-1.1) / +5.01 (+2.6) | 0.27 / 0.09 |
| EU-OPEN | NZDUSD | -0.13 (-0.5) / +0.65 (+1.6) | +0.26 (+0.4) / +0.21 (+0.2) | -0.82 (-0.4) / +0.12 (+0.0) | 0.51 / 0.61 |
| EU-OPEN | INDICES | -0.39 (-1.0) / +0.44 (+1.0) | -2.23 (-1.8) / +1.28 (+1.1) | -4.79 (-1.4) / +4.95 (+1.6) | 2.03 / 0.74 |
| EU-OPEN | FX | +0.04 (+0.2) / +0.24 (+0.6) | +0.11 (+0.2) / +0.45 (+0.6) | -1.40 (-0.9) / +3.23 (+1.4) | 0.39 / 0.34 |
| EU-OPEN | ALL | -0.14 (-0.6) / +0.28 (+1.1) | -0.98 (-1.5) / +0.72 (+1.1) | -2.68 (-1.3) / +3.59 (+2.0) | 1.15 / 0.52 |
| NZ-07 | NZDUSD | -0.41 (-2.4) / -0.13 (-0.4) | -1.23 (-3.1) / -0.03 (-0.0) | -2.95 (-3.2) / -0.48 (-0.3) | 0.96 / 0.85 |
| NZ-07 | AUDUSD | -0.08 (-0.5) / +0.57 (+2.0) | -0.72 (-1.9) / +0.64 (+0.8) | -1.43 (-1.8) / +2.75 (+1.3) | 0.38 / 0.11 |
| NZ-07 | FX | -0.25 (-1.8) / +0.25 (+1.1) | -0.96 (-2.9) / +0.29 (+0.5) | -2.18 (-3.0) / +0.68 (+0.5) | 0.65 / 0.49 |
| NY-IMB | US30 | +1.52 (+2.4) / -0.77 (-1.2) | +2.93 (+1.3) / -1.68 (-1.0) | +11.63 (+1.7) / -5.68 (-1.3) | 1.01 / 0.29 |
| NY-IMB | USTEC | +0.81 (+1.1) / +0.79 (+0.7) | +1.72 (+0.6) / +0.85 (+0.3) | +8.56 (+0.9) / +12.86 (+2.1) | 2.07 / 0.89 |
| NY-IMB | INDICES | +1.16 (+2.0) / +0.01 (+0.0) | +2.36 (+1.0) / -0.34 (-0.2) | +10.18 (+1.4) / +5.65 (+1.2) | 1.51 / 0.61 |
| NY-IMB | US30-1550 | +1.15 (+1.9) / -0.77 (-1.2) | +1.71 (+0.7) / -1.68 (-1.0) | +7.44 (+1.1) / -5.68 (-1.3) | 1.01 / 0.29 |
| SETTLE | XAUUSD | -0.62 (-2.5) / -0.56 (-1.6) | -0.95 (-1.6) / -0.42 (-0.5) | +1.15 (+0.7) / -5.75 (-1.5) | 0.93 / 0.39 |
| SETTLE | XAGUSD | -1.31 (-2.7) / -0.24 (-0.4) | -2.42 (-1.6) / +2.94 (+2.0) | -4.92 (-0.9) / +1.67 (+0.4) | 3.93 / 3.73 |
| SETTLE | XTIUSD | +0.91 (+0.7) / +0.15 (+0.2) | -0.65 (-0.1) / -1.58 (-0.6) | -8.92 (-0.5) / +1.99 (+0.8) | 9.46 / 3.42 |
| SETTLE | XNGUSD | -0.03 (-0.0) / -3.07 (-1.5) | +5.29 (+1.3) / +4.42 (+0.9) | +19.56 (+1.7) / +13.24 (+0.9) | 13.56 / 44.23 |
| SETTLE | XBRUSD | +0.83 (+0.9) / +0.22 (+0.3) | -1.85 (-0.8) / +1.08 (+0.5) | -5.10 (-0.7) / -5.12 (-0.8) | 7.41 / 2.92 |
| SETTLE | METALS | -0.95 (-3.5) / -0.40 (-1.1) | -1.61 (-2.1) / +1.19 (+1.4) | -1.74 (-0.6) / -2.13 (-0.8) | 2.29 / 2.00 |
| SETTLE | ENERGY | +0.61 (+0.7) / -0.90 (-1.0) | +0.72 (+0.3) / +1.57 (+0.7) | +1.02 (+0.1) / +5.98 (+0.7) | 10.00 / 18.90 |
| SETTLE | ALL | -0.20 (-0.5) / -0.70 (-1.3) | -0.49 (-0.4) / +1.41 (+1.0) | -0.41 (-0.1) / +1.60 (+0.4) | 6.00 / 11.70 |
| EU-OPEN | DE40(min) | +0.39 (+0.5) / -0.61 (-0.6) | -0.79 (-0.3) / +0.20 (+0.1) | -18.89 (-2.0) / -9.39 (-0.7) | 0.96 / 0.38 |
| EU-OPEN | UK100(min) | -0.71 (-1.0) / +0.08 (+0.1) | -4.44 (-2.4) / -1.77 (-0.8) | -15.36 (-2.5) / -18.37 (-2.6) | 1.78 / 1.30 |

Reading:
- **Chinese day open.** Continuation at k 4 is mostly a VAL reading (ALL +7.37 bp, t 2.09; IS +0.98).
- **Chinese afternoon reopen.** Gold continues in both eras at k 4 only; at k 2 VAL is -0.14.
- **NZ-07.** Reversal in IS only.
- **SETTLE metals.** Reversal in both eras.
- **NY-IMB.** US30 continues in IS and reverses in VAL. USTEC continues at k 4 in both eras (+8.56 / +12.86 bp,
  t 0.9 / 2.1).

None survives IC's spread at its own minute.

## 4. Families: cells tried, best cell, chance
| clock | family | cells | IS net > 0 | IS and VAL net > 0 | IS net t >= 2 | of which VAL net > 0 | best IS net t | V1 no-stop cells with IS mid t >= 2 / <= -2 | of those, VAL mid same sign t >= 1.5 | DEMO numbers | LIVE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CN-DAY | V1 | 324 | 19 | 15 | 0 | 0 | +1.55 (AUDUSD w15 k4 h60 none) | 10 / 5 | 4 / 0 | 0 | 0 |
| CN-DAY | V2 | 324 | 16 | 6 | 0 | 0 | +1.30 (AUDUSD w60 k2 h60 none) | - / - | - / - | 0 | 0 |
| CN-PM | V1 | 324 | 16 | 9 | 0 | 0 | +1.76 (XAUUSD w15 k4 h60 none) | 14 / 1 | 4 / 0 | 0 | 0 |
| CN-PM | V2 | 324 | 5 | 1 | 0 | 0 | +0.86 (XTIUSD w15 k4 h60 S) | - / - | - / - | 0 | 0 |
| CN-NIGHT | V1 | 288 | 53 | 45 | 1 | 0 | +2.09 (AUDUSD w15 k4 h60 none) | 10 / 1 | 0 / 0 | 0 | 0 |
| CN-NIGHT | V2 | 288 | 14 | 8 | 0 | 0 | +0.94 (XAGUSD w15 k2 h60 none) | - / - | - / - | 0 | 0 |
| CNY-FIX | V1 | 180 | 17 | 1 | 0 | 0 | +0.62 (ALL w15 k4 h15 S) | 1 / 0 | 0 / 0 | 0 | 0 |
| CNY-FIX | V2 | 180 | 10 | 9 | 0 | 0 | +1.26 (AUDUSD w15 k4 h60 none) | - / - | - / - | 0 | 0 |
| EU-OPEN | V1 | 288 | 12 | 5 | 0 | 0 | +1.16 (NZDUSD w60 k4 h60 none) | 0 / 15 | 0 / 0 | 0 | 0 |
| EU-OPEN | V2 | 288 | 53 | 5 | 3 | 1 | +2.23 (US30 w60 k4 h15 none) | - / - | - / - | 1 | 0 |
| EU-OPEN(min) | V1 | 18 | 0 | 0 | 0 | 0 | -0.37 (DE40(min) w60 k2 h5 none) | 0 / 3 | 0 / 1 | 0 | 0 |
| EU-OPEN(min) | V2 | 18 | 10 | 6 | 1 | 1 | +2.12 (UK100(min) w60 k4 h15 none) | - / - | - / - | 1 | 0 |
| NZ-07 | V1 | 108 | 2 | 2 | 0 | 0 | +0.39 (AUDUSD w60 k4 h5 S) | 0 / 15 | 0 / 0 | 0 | 0 |
| NZ-07 | V2 | 108 | 14 | 3 | 0 | 0 | +1.25 (NZDUSD w15 k4 h60 none) | - / - | - / - | 0 | 0 |
| NY-IMB | V1 | 144 | 78 | 25 | 3 | 0 | +2.13 (US30 w15 k2 h15 S) | 8 / 0 | 0 / 0 | 0 | 0 |
| NY-IMB | V2 | 144 | 6 | 0 | 0 | 0 | +0.87 (USTEC w60 k4 h5 S) | - / - | - / - | 0 | 0 |
| SETTLE | V1 | 288 | 6 | 0 | 0 | 0 | +0.80 (XNGUSD w15 k4 h60 none) | 0 / 21 | 0 / 7 | 0 | 0 |
| SETTLE | V2 | 288 | 21 | 6 | 0 | 0 | +1.45 (XBRUSD w60 k4 h60 S) | - / - | - / - | 0 | 0 |

| benchmark | all counted cells (K = 3924) | 32 primary cells |
|---|---|---|
| 95 % max \|t\| of K independent normals | 4.36 | 3.16 |
| sign-flip null, max IS net t: p50 / p95 | 2.31 / 3.06 | 0.81 / 1.83 |
| observed max IS net t (share of null draws >= it) | 2.23 (0.569) | 1.14 (0.271) |
| sign-flip null, max \|IS mid t\| (no-stop cells): p50 / p95 | 3.26 / 3.99 | 1.98 / 2.86 |
| observed max \|IS mid t\| (share of null draws >= it) | 4.41 (0.009) | 3.18 (0.016) |

Reading of the chance benchmark:
- **Net.** K = 3,924 cells, all with >= 10 IS events. For K independent normals the 95 % max |t| is 4.36, and 3.16
  for the 32 primary cells.
- The per-day sign-flip null (one flip per UTC day shared by every instrument, clock and cell; 1,000 draws) gives a
  max IS net t of p50 2.31 / p95 3.06. The observed 2.23 has p 0.57.
- For the 32 primary cells the null is p50 0.81 / p95 1.83. The observed 1.14 has p 0.27.
- **Mid.** The max |IS mid t| over the no-stop cells has a null p95 of 3.99. The observed 4.41 has p 0.009 (NZ-07,
  IS only). For the primary cells the null p95 is 2.86 against 3.18 observed (p 0.016).

## 5. Declared information-only splits
| split | k | V1 IS | V1 VAL | V2 IS | V2 VAL | V1 mid IS / VAL |
|---|---|---|---|---|---|---|
| CN-NIGHT ALL, NY summer (13:00 UTC = 09:00 EDT) | 2 | -3.99 (-2.4) n680 | -2.06 (-0.7) n368 | -3.40 (-1.9) | -2.87 (-0.9) | -0.30 / +0.40 |
| CN-NIGHT ALL, NY winter (13:00 UTC = 08:00 EST) | 2 | +0.96 (+0.6) n222 | -6.35 (-2.0) n149 | -5.89 (-3.4) | +1.72 (+0.6) | +3.42 / -4.04 |
| CN-NIGHT oil only, NY summer | 2 | -1.57 (-0.3) n208 | +1.14 (+0.2) n136 | -12.51 (-2.6) | -7.47 (-1.0) | +5.47 / +4.30 |
| CN-NIGHT oil only, NY winter | 2 | +4.57 (+0.7) n45 | -9.89 (-1.3) n58 | -16.74 (-2.5) | +3.60 (+0.5) | +10.66 / -6.74 |
| CN-NIGHT ALL, NY summer (13:00 UTC = 09:00 EDT) | 4 | +3.60 (+0.7) n140 | +2.60 (+0.3) n80 | -13.76 (-2.4) | -7.93 (-0.8) | +8.68 / +5.26 |
| CN-NIGHT ALL, NY winter (13:00 UTC = 08:00 EST) | 4 | +7.51 (+2.3) n37 | -8.23 (-1.1) n34 | -10.95 (-3.0) | +3.23 (+0.4) | +9.23 / -5.73 |
| CN-NIGHT oil only, NY summer | 4 | +14.65 (+1.0) n52 | +12.92 (+0.5) n31 | -33.56 (-2.3) | -19.51 (-0.8) | +24.10 / +16.22 |
| CN-NIGHT oil only, NY winter | 4 | +29.49 (+1.6) n4 | -7.19 (-0.5) n19 | -41.31 (-2.3) | +0.78 (+0.1) | +35.40 / -3.99 |
| CN-NIGHT ALL on the 2020 suspension days | 0 | +0.16 (+0.0) n213 | - (-) n0 | -15.43 (-3.3) | - (-) | +7.80 / - |
| CN-NIGHT ALL on the 2020 suspension days | 2 | +10.14 (+1.1) n78 | - (-) n0 | -31.75 (-3.4) | - (-) | +20.94 / - |
| NY-IMB US30 (NYSE clock: 15:45 ET) before 2019-04-01 | 2 | +2.87 (+1.2) n122 | - (-) n0 | -4.87 (-2.0) | - (-) | +3.87 / - |
| NY-IMB US30 (15:50 ET) from 2019-04-01 | 2 | +0.97 (+0.2) n122 | -1.97 (-1.1) n111 | -3.01 (-0.8) | +1.39 (+0.8) | +1.99 / -1.68 |
| NY-IMB-1550 US30 (15:50 ET) before 2019-04-01 | 2 | +0.89 (+0.3) n97 | - (-) n0 | -2.90 (-1.1) | - (-) | +1.90 / - |
| NY-IMB US30 (NYSE clock: 15:45 ET) before 2019-04-01 | 4 | +7.11 (+1.0) n29 | - (-) n0 | -9.34 (-1.3) | - (-) | +8.23 / - |
| NY-IMB US30 (15:50 ET) from 2019-04-01 | 4 | +12.84 (+1.2) n36 | -6.01 (-1.4) n14 | -15.89 (-1.5) | +5.35 (+1.2) | +14.36 / -5.68 |
| NY-IMB-1550 US30 (15:50 ET) before 2019-04-01 | 4 | -3.89 (-0.5) n25 | - (-) n0 | +1.54 (+0.2) | - (-) | -2.71 / - |
| CN-DAY ALL, first trading day after a Chinese holiday | 0 | -3.99 (-1.2) n174 | -2.01 (-0.5) n101 | -11.89 (-3.5) | -14.95 (-4.2) | +3.95 / +6.47 |
| CN-DAY ALL, other trading days | 0 | -7.05 (-17.9) n5228 | -7.95 (-15.4) n2964 | -7.50 (-19.4) | -8.84 (-16.7) | +0.22 / +0.44 |
| CN-DAY ALL, first trading day after a Chinese holiday | 2 | -4.12 (-0.7) n80 | +4.21 (+0.7) n52 | -11.07 (-2.0) | -17.77 (-3.1) | +3.48 / +10.99 |
| CN-DAY ALL, other trading days | 2 | -6.96 (-7.1) n1127 | -6.63 (-4.9) n605 | -7.64 (-8.3) | -11.08 (-7.6) | +0.34 / +2.23 |

Reading:
- **CN-NIGHT by New York season.** The pooled set has no season consistent across eras: in winter the k 2 mid is
  +3.42 IS / -4.04 VAL, in summer -0.30 / +0.40.
  - Oil continues in New York summer in both eras: k 2 mid +5.47 / +4.30, k 4 +24.1 / +16.2 bp. 13:00 UTC is then
    09:00 EDT, the old NYMEX floor open, so this is not clearly the Shanghai night session.
  - Its k 4 net is +14.7 / +12.9 bp, but t is only 1.0 / 0.5.
- **The 2020 night-session suspension** (venue shut, February-May 2020). The 13:00 UTC move continued at mid: +7.8 bp
  at k 0, +20.9 at k 2. That is the US pre-market of the COVID crash, not the Shanghai session.
- **The first Chinese trading day after a holiday** (call-auction opens) continues at mid in both eras: +3.5 to
  +11 bp at k 0-2. That is about 7 days a year, and the six-instrument pool's cost swamps it. Gold alone was not
  declared.
- **US30 before 2019-04-01.** The NYSE's own clock (15:45 ET) shows more continuation than 15:50 ET: k 2 mid +3.87 vs
  +1.90, V1 net +2.87 (t 1.2) vs +0.89. That fits the NYSE imbalance publication being the event. From 2019-04-01
  (15:50 ET) it is +0.97 IS and -1.97 VAL. None of this is significant.

## 6. The DEMO-number cells: siblings, C3, HOLD
| set | n IS / VAL | mid IS (t) / VAL (t) | net IS (t) / VAL (t) | +1 min IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|
| US30 | 59 / 14 | +10.42 (+2.50) / +4.97 (+0.91) | +9.26 (+2.23) / +4.65 (+0.85) | +7.49 / +1.61 | 1.00 / 0.92 | DEMO numbers, within chance |
| USTEC | 64 / 22 | +4.13 (+1.24) / -6.92 (-1.39) | +1.06 (+0.32) / -7.99 (-1.58) | +0.27 / -5.78 | 0.95 / 0.03 | fail |
| XAUUSD | 42 / 13 | +1.00 (+0.47) / +0.49 (+0.22) | -1.06 (-0.50) / -0.54 (-0.24) | -1.74 / +4.54 | 0.71 / 0.56 | fail |
| AUDUSD | 31 / 14 | +0.07 (+0.03) / -1.46 (-0.44) | -0.91 (-0.41) / -2.15 (-0.64) | -0.49 / -1.83 | 0.51 / 0.30 | fail |
| NZDUSD | 23 / 10 | -3.99 (-1.30) / +2.89 (+0.90) | -5.23 (-1.66) / +1.63 (+0.51) | -5.04 / +0.30 | 0.03 / 0.82 | fail |
| INDICES | 123 / 36 | +7.15 (+1.98) / -2.30 (-0.55) | +4.99 (+1.40) / -3.08 (-0.73) | +3.74 / -2.90 | 1.00 / 0.17 | fail |
| FX | 54 / 24 | -1.66 (-0.76) / +0.35 (+0.12) | -2.75 (-1.23) / -0.58 (-0.19) | -2.43 / -0.94 | 0.09 / 0.61 | fail |
| ALL | 219 / 73 | +3.79 (+1.91) / -0.93 (-0.43) | +1.92 (+0.98) / -1.80 (-0.82) | +1.17 / -0.93 | 1.00 / 0.24 | fail |
| DE40(min) | 32 / 6 | +18.89 (+1.98) / +9.39 (+0.67) | +17.39 (+1.85) / +8.92 (+0.64) | +19.26 / +11.08 | 1.00 / 0.82 | fail |
| UK100(min) | 42 / 14 | +15.36 (+2.46) / +18.37 (+2.58) | +13.15 (+2.12) / +17.07 (+2.40) | +12.85 / +23.44 | 1.00 / 1.00 | DEMO numbers, within chance |

The same family (V2, w 60 s, no stop) at every k and h, index sets:

| cell | n IS / VAL | net IS (t) / VAL (t) |
|---|---|---|
| US30 w60 k0 h5 | 1035 / 583 | -0.97 (-4.01) / -0.41 (-1.51) |
| US30 w60 k0 h15 | 984 / 555 | -1.06 (-2.46) / -0.47 (-1.05) |
| US30 w60 k0 h60 | 843 / 506 | -0.32 (-0.42) / -0.54 (-0.65) |
| US30 w60 k2 h5 | 206 / 106 | +0.21 (+0.26) / +0.01 (+0.01) |
| US30 w60 k2 h15 | 200 / 99 | +2.29 (+1.50) / -0.19 (-0.12) |
| US30 w60 k2 h60 | 173 / 93 | +4.20 (+1.66) / -1.85 (-0.66) |
| US30 w60 k4 h5 | 60 / 17 | +4.87 (+2.07) / -2.47 (-0.93) |
| US30 w60 k4 h15 | 59 / 14 | +9.26 (+2.23) / +4.65 (+0.85) |
| US30 w60 k4 h60 | 48 / 13 | +15.52 (+2.18) / -6.96 (-0.79) |
| USTEC w60 k0 h5 | 1055 / 590 | -3.00 (-11.50) / -1.47 (-3.97) |
| USTEC w60 k0 h15 | 1003 / 562 | -3.22 (-7.60) / -1.98 (-3.29) |
| USTEC w60 k0 h60 | 856 / 513 | -2.50 (-3.09) / -2.05 (-1.85) |
| USTEC w60 k2 h5 | 235 / 125 | -1.21 (-1.56) / -2.01 (-2.18) |
| USTEC w60 k2 h15 | 228 / 116 | -1.64 (-1.39) / -2.89 (-1.62) |
| USTEC w60 k2 h60 | 198 / 109 | +0.70 (+0.31) / -4.83 (-1.54) |
| USTEC w60 k4 h5 | 65 / 25 | +1.45 (+0.69) / -3.14 (-1.40) |
| USTEC w60 k4 h15 | 64 / 22 | +1.06 (+0.32) / -7.99 (-1.58) |
| USTEC w60 k4 h60 | 56 / 20 | +1.49 (+0.22) / -11.46 (-1.20) |
| INDICES w60 k0 h5 | 2090 / 1173 | -1.99 (-8.61) / -0.94 (-3.15) |
| INDICES w60 k0 h15 | 1987 / 1117 | -2.15 (-5.42) / -1.23 (-2.53) |
| INDICES w60 k0 h60 | 1699 / 1019 | -1.41 (-1.94) / -1.30 (-1.44) |
| INDICES w60 k2 h5 | 441 / 231 | -0.55 (-0.74) / -1.08 (-1.34) |
| INDICES w60 k2 h15 | 428 / 215 | +0.20 (+0.16) / -1.65 (-1.06) |
| INDICES w60 k2 h60 | 371 / 202 | +2.33 (+1.06) / -3.46 (-1.26) |
| INDICES w60 k4 h5 | 125 / 42 | +3.09 (+1.44) / -2.87 (-1.42) |
| INDICES w60 k4 h15 | 123 / 36 | +4.99 (+1.40) / -3.08 (-0.73) |
| INDICES w60 k4 h60 | 104 / 33 | +7.97 (+1.25) / -9.69 (-1.19) |
| DE40(min) w60 k0 h5 | 1084 / 598 | -0.99 (-1.92) / +0.27 (+0.41) |
| DE40(min) w60 k0 h15 | 1029 / 573 | -1.22 (-1.54) / +0.23 (+0.23) |
| DE40(min) w60 k0 h60 | 877 / 521 | -0.70 (-0.50) / -0.14 (-0.08) |
| DE40(min) w60 k2 h5 | 190 / 96 | -1.27 (-0.77) / -0.37 (-0.19) |
| DE40(min) w60 k2 h15 | 185 / 90 | -0.17 (-0.07) / -0.58 (-0.21) |
| DE40(min) w60 k2 h60 | 163 / 83 | +0.27 (+0.06) / -3.15 (-0.61) |
| DE40(min) w60 k4 h5 | 33 / 7 | +7.64 (+1.09) / +10.99 (+1.29) |
| DE40(min) w60 k4 h15 | 32 / 6 | +17.39 (+1.85) / +8.92 (+0.64) |
| DE40(min) w60 k4 h60 | 25 / 6 | +28.35 (+1.49) / +7.97 (+0.23) |
| UK100(min) w60 k0 h5 | 1092 / 587 | -1.46 (-3.29) / -0.98 (-1.71) |
| UK100(min) w60 k0 h15 | 1037 / 560 | -0.99 (-1.37) / -1.36 (-1.63) |
| UK100(min) w60 k0 h60 | 888 / 513 | -1.06 (-0.86) / -2.10 (-1.51) |
| UK100(min) w60 k2 h5 | 208 / 112 | +0.33 (+0.28) / -0.57 (-0.37) |
| UK100(min) w60 k2 h15 | 200 / 108 | +2.66 (+1.46) / +0.47 (+0.22) |
| UK100(min) w60 k2 h60 | 166 / 100 | +3.12 (+0.83) / -2.32 (-0.59) |
| UK100(min) w60 k4 h5 | 44 / 15 | +5.59 (+1.47) / -0.57 (-0.08) |
| UK100(min) w60 k4 h15 | 42 / 14 | +13.15 (+2.12) / +17.07 (+2.40) |
| UK100(min) w60 k4 h60 | 32 / 13 | +27.29 (+1.79) / +16.69 (+2.25) |

| cell | C3 corr all weekdays / trade days (n days) | VAL rate / yr | expected HOLD events (1.73 y) | VAL per-trade Sharpe | expected HOLD t at the VAL size / at 0.65 of it |
|---|---|---|---|---|---|
| EU-OPEN US30 V2 w60 k4 h15 none | +0.009 / +0.006 (73) | 4.7 | 8.1 | +0.227 | +0.65 / +0.42 |
| EU-OPEN UK100(min) V2 w60 k4 h15 none | +0.005 / -0.039 (56) | 4.7 | 8.1 | +0.641 | +1.82 / +1.18 |

- **Concentration.** Most of the IS sum comes from crash opens.
  - US30: 12 of 59 IS events in March-April 2020 carry 77 % of the IS sum. 6 February 2018 adds another +111 bp.
    The IS median is +1.01 bp.
  - UK100: 9 of 42 events carry 67 % of the sum. The IS median is +6.31 and the VAL median +12.71.
  - DE40, same spec: 10 of 32 events carry 79 %.
- **Venue-shut placebo: n/a.** The few LSE + Xetra holidays have no k 4 event.
- **Shifted clocks.** For US30, 07:30 gives +0.24 / -2.57 and 08:30 gives -4.03 / -2.93. For UK100, 07:30 gives
  -1.71 / -9.59 and 08:30 gives +6.10 / -6.44 (IS / VAL).
- **PRE.** Not possible: there is no local index data before 2016.
- **Verdict.** DEMO numbers, within chance, crash-driven. Drafted; not recommended for HOLD.

## Needs the user
- **Dukascopy index M1 2004-15** (UK100, DE40, US30) for a PRE check of the EU-open fade. Only worth it if the user
  wants that DEMO-number family pursued. Prior low: it is within chance and crash-driven.
- **IC ticks for UK100 / DE40** (cTrader backtest downloads on the VPS), to test the UK100 cell with tick fills
  instead of bar closes.
- **Data after 2026-09-24** for a forward demo log of the EU-open fade, ~10 events a year for both variants. Not
  recommended.
- **A cheaper metals venue** would be needed before the settlement-window reversal matters: 0.4-1.4 bp against a
  ~2.7 bp round trip (2.1 bp spread + 0.6 bp commission).

## Untested ideas
- **The 23:00 / 00:00 UTC cluster** in round 26's counts. It is the ASX 10:00 Sydney / TSE 09:00 JST open, seen in
  AUD, NZD, gold and the US indices. It was not declared here. The Sydney V is an exhausted fixed-side family for
  AUD / NZD; a side from the first seconds was not tested.
- **The A-share / HKEX opens** (01:30 UTC; afternoon 05:00 UTC) as clocks of their own for AUD and the US indices.
  Here they appeared only as the shifted-clock controls of CN-DAY and CN-PM.
- **The SGE night session start** (20:00 Beijing, 12:00 UTC) for metals. Round 10 tested only a fixed side.
- **Gold-only after a Chinese holiday** (the call-auction day open). The pooled reading continues at mid, but the
  pool is dominated by expensive instruments. This is post hoc and would need declaring on new data.
- **A resting limit order instead of a market fade** in the settlement windows (no entry spread). Rounds 12 and 26
  found passive limits adversely selected.
- **What drives 07:00 New Zealand.** Its spike survives NZ holidays and vanishes on NZ Saturdays, so it looks like a
  liquidity-provider day roll rather than a venue. Neither side pays.

## Scripts and outputs
All under /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r27/V/.

| script (code/) | what it does |
|---|---|
| cal_v.py | venue calendars from `holidays` 0.106 -> `cal/venue_calendars_v.json` (copy: r25/shared/cal/venue_calendars_2015_2024.json) |
| common_v.py | clocks, day types, calendar exclusions, the HOLD-guarded loader, the sparse-table first-crossing search, the tick fill simulator |
| test_sim_v.py | synthetic checks of the fill simulator and the first-crossing search |
| pass_v.py | per-instrument tick pass -> `out/ev_<SYM>.npz` (events at T and T +- 30 min), `out/rt_<SYM>.npz` (random-time control per cell), `out/prof_<SYM>.npz` (V0) |
| minute_v.py | DE40 / UK100 minute-level cells from the panel -> `out/ev_DE40.npz`, `out/ev_UK100.npz` (+ rt files) |
| profile_v.py | V0 clock check -> `out/profile_v.txt` |
| analyze_v.py | all cells, controls, sign-flip null, bars -> `out/cells_v.pkl`, `out/cells_v.tsv`, `out/chance_v.txt` |
| report_v.py | tables -> `out/report_v.md` |
| info_v.py | information-only tables, C3 correlation, HOLD expectations -> `out/info_v.md` |
| assemble_v.py | builds this file from `code/stream_template_v.md` and the two table files |

## Process notes
| UTC | step |
|---|---|
| 21:05-21:22 | briefs and earlier reports read; clock schedules sourced (NYSE trader update, Nasdaq filings, CFETS, CME / ICE settlement pages, SHFE notices); calendars listed |
| 21:23 | HYPOTHESES_V.md written |
| 21:25-21:29 | calendars built (21:26); synthetic simulator tests; a 41-day debug pass (counts and NaN shares only) |
| 21:29-21:34 | full tick pass (2 processes); minute-level pass (21:33) |
| 21:34-21:37 | V0 check (21:34), all cells and chance (done 21:37) |
| 21:37-21:39 | report and information-only tables |
| 21:40 | Addendum 1 |
| 21:42 | draft and this file |

Rules kept:
- At most two heavy processes ran at once. The largest, the analysis, holds ~0.5 GB of event arrays.
- Nothing under research/ was edited; ticks were read through my own copy of the round-26 loader.
- The web requests were schedule lookups (exchange, CFETS, CME / ICE pages). They carried no personal data, and no
  price was fetched.
- The DEMO-number cells were recomputed independently from the raw event rows and from the panel; the numbers match
  exactly.
