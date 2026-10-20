# Round 29, stream O: the direction of the first seconds at the Asian venue clocks round 27 left untested

Written 2026-10-18 01:21 UTC (from `date -u`; finished in the minutes after). [HYPOTHESES_O.md](HYPOTHESES_O.md)
declared every cell at 01:04-01:06 UTC, before any forward return, entry or exit price or spread at a clock was
computed. Its Addendum 1 (01:18 UTC) lists what was added after the numbers (views of declared cells, a recomputation
check, a fix to one information-only split, one unsigned V0 split). Method: round 27 V's
([STREAM_V.md](../round27_levels_opens/STREAM_V.md)), unchanged except for the two declared adaptations (the norm's
clean days also avoid the New York rollover; the venue currencies join each clock's exclusion set). Fill model: round
26's (binding). This is the last round of the session.

HOLD was never loaded:
- the loader asserts every requested day < 2025-01-01 and the file name < "20250101.zticks" before opening it, and
  every tick timestamp < 2025-01-01; the latest clock instant in any event file is 2024-12-31 12:30 UTC;
- the independent check read ticks through research/ticks.py for days < 2025-01-01 only;
- no Dukascopy, panel or C3 file was opened.

## Answer
- **No LIVE and no DEMO candidate. No counted cell meets even the DEMO numbers, so no PREREG_DRAFT_O was written.**
  - 2,808 counted cells (39 sets x 72) at six clocks; TSE-PM's 576 cells were information only.
  - The best IS net t is 2.01, the only cell at >= 2.0: TSE-OPEN XAUUSD V1 w60 k4 h60 (IS +5.18 bp, n 43; VAL -5.29,
    t -1.01, n 30). The per-day sign-flip null puts the max IS net t at p50 2.12 / p95 3.07, so p = 0.63.
  - For the 24 primary cells the best IS net t is 1.33 (SGE-NIGHT ALL V1 k4: +5.33 IS, -2.27 VAL; null p95 1.36,
    p 0.06). 4 of 24 are net > 0 in IS and 1 in both eras (TSE-OPEN ALL V2 k4: +0.28 / +0.97, t 0.2 / 0.9).
  - 56 of 2,808 cells are net > 0 in both eras; none has IS t >= 2. The strongest, CNHK-AM US30 V1 w60 k4 h60
    (follow a large first-minute move at the A-share / HKEX open for 60 min): +17.20 (t 1.76, n 47) IS, +5.33
    (t 0.84, n 11) VAL. 19 events in 2020 average +30 bp; without March-April 2020 IS is +10.7. It fails the DEMO t.
  - The largest per-trade power on the IS size is 1.08 (bar 3).
- **The first seconds carry some direction at mid, mostly a reversal at the 00:00 UTC cluster, well below cost.**
  - The primary cells' max |IS mid t| is 3.06 (ASX-OPEN ALL k2 h15: -1.50 bp, a reversal; VAL -0.45, t -0.81).
    Null p95 2.73, p 0.021. Over all no-stop cells the max is 3.76 (SGE-NIGHT ALL k0 h15: +1.69 bp continuation in
    IS, +0.10 in VAL), null p95 3.89, p 0.084.
  - At ASX-OPEN, TSE-OPEN and ASX+TSE the fade's mid at k 2 is +0.9 to +1.5 bp in IS and +0.4 to +0.8 in VAL (ALL
    sets). The spread paid is 1.4 / 0.6 bp, plus the 0.6 bp commission on FX and gold, so the fade nets -0.3 to -0.9
    in IS and -0.1 to -0.5 in VAL.
  - In AUD / NZD at ASX-OPEN, part of that reversal is the Sydney V's fixed post-10:00 rise. Down-move legs reverse
    (FX k0 V1 mid -1.13, t -3.5 IS; -1.18, t -2.7 VAL) and up-move legs continue (+0.18 / +0.44). That family is
    exhausted (round 12 J failed HOLD).
  - SGE-NIGHT: continuation in IS only (silver k0 +2.65 bp, t 3.63; VAL +0.21). CNHK-AM and CNHK-PM: no direction at
    the primary spec (ALL k2: -0.07 / +0.12 and -0.19 / +0.54 bp).
- **Cost is binding, as in rounds 10-28.** Median |opening move| at w 15 s is 0.4-1.1 bp (silver 2.2-2.6). The median
  entry spread at these clocks is 0.3-0.5 / 0.0-0.3 bp in AUDUSD (IS / VAL), 0.6-1.0 in NZDUSD, 0.7-0.9 / 0.4-0.5 in
  gold, 1.4 / 0.4 in US30, 2.8-2.9 / 1.3-1.4 in USTEC and 3.4 / 3.9 in silver, plus 0.6 bp commission on FX and metals.
- **The clocks themselves are weak in IC's feed.**
  - The 00:00 UTC activity spike is nearly as large on TSE holidays. V0 ratio in the first 15 s: FX x2.4-2.6 on TSE
    holidays vs x2.6 on trading days; US indices x2.1-2.4 vs x3.3. KRX also opens at 00:00 UTC.
  - At 23:00 UTC in the northern winter, the spike in gold and the US indices is IC's / CME's daily reopen (x6.5-12,
    x16-24 on ASX holidays). The rollover rule removes it, so ASX-OPEN under AEDT trades only in October and late
    March.
  - AUD's spike at 01:30 UTC is the Australian release clock (11:30 Sydney): x5.7 under AEST against x1.5 under
    AEDT on SSE / HKEX trading days. The A-share / HKEX open itself barely moves AUD.
  - The SGE night open is faint in IC's metals (gold x2.2 / silver x2.8 against x1.8 / x2.3 on holiday nights).

## How this differs from the fixed-side tests of the same clocks
| earlier test | what it did | here |
|---|---|---|
| round 4 scan, round 6 S4, round 12 J, round 24 B (Sydney V) | AUD / NZD fall into 10:00 Sydney and rise after: fixed sides, limit buys, an off-rollover AUDUSD variant (failed HOLD), Dukascopy 2004-15 | side from the first 15 / 60 s after 10:00 Sydney on large-move days, ticks, also gold and US indices |
| round 15 V1 (minute panel) | TSE, HKEX and ASX cash opens on their home index CFDs (JP225, HK50, AUS200): fade the gap or the last 10 min | non-home instruments, side from the first seconds, ticks, venue-holiday placebos |
| round 10 A (minute panel) | long after the Chinese opens 01:00 / 12:00 / 13:00 UTC for 15-60 min, SGE auctions, Asian fixes | conditional side; the A-share / HKEX, Tokyo and Sydney opens as clocks of their own |
| round 27 V | 01:30 and 05:00 UTC only as shifted controls of its Chinese pools | own clocks, norms, calendars, instruments and placebos |

## Design (exact rules in HYPOTHESES_O.md)
- **Clocks.**
  - ASX-OPEN 10:00 Sydney: 23:00 UTC under AEDT, 00:00 UTC under AEST.
  - TSE-OPEN 09:00 Tokyo (00:00 UTC).
  - ASX+TSE: the AEST days with both venues open, one event.
  - CNHK-AM 09:30 and CNHK-PM 13:00 Beijing / Hong Kong (01:30 / 05:00 UTC), on days SSE or HKEX opens.
  - SGE-NIGHT 20:00 Beijing (12:00 UTC), on SGE night-session days.
  - TSE-PM 12:30 Tokyo (03:30 UTC), information only.
- **Instruments.** ASX / TSE: AUDUSD, NZDUSD, XAUUSD, US30, USTEC. CNHK: AUDUSD, XAUUSD, US30, USTEC. SGE-NIGHT:
  XAUUSD, XAGUSD.
- **Calendars.** The `holidays` package 0.106 (XASX, XJPX, XHKG, XSHG, XKRX), plus:
  - the TSE outage of 2020-10-01, dropped;
  - HKEX half days;
  - SGE night sessions by round 27's rule, with the 2024-02-08 correction from SGE's 2024 schedule. The
    2020-02-03..05-05 window is kept apart (SGE's own notice not found).
- **Rule (round 27's).**
  - Opening move m = mid at T + w over the mid at T - 1 s, w in {15, 60} s.
  - Event: |m| >= k x the median |m| of the previous 60 clean trading days, k in {0, 2, 4}.
  - V1 follows the move, V2 fades it.
  - Entry at the first tick >= T + w + L (buy at the ASK, sell at the BID). L = 250 ms decides; L 0 / 1,000 ms /
    next tick / +1 min are reported.
  - Exit h in {5, 15, 60} min later; optional server-side stop at max(|m|, 2 spreads).
- **Costs and exclusions.**
  - Actual tick spreads, plus 0.6 bp commission on FX and metals.
  - Calendar rows of the instrument's currencies plus the venue's (AUD and JPY at the Sydney / Tokyo clocks, CNY at
    the Chinese ones) within [T - 15 min, T + w + h + 2 min]; central-bank and BOJ windows; vote days.
  - No trade touching 16:55-18:10 New York.
- **Controls.** Venue-shut days, shifted clocks T +- 30 min, random direction (500 seeds), random time (200 seconds
  per event in [T - 150, T - 35] U [T + 35, T + 150] min, side recomputed).
- **Cells.** 39 counted sets x 72 = 2,808; the 24 primary cells are the ALL set of each clock at w 15 s, h 15 min,
  no stop, k 2 / 4, both families. TSE-PM adds 8 x 72 information-only cells.

## V0 clock check (unsigned, IS): activity in the first 15 s against T-60..T-30 s
Ratio of the mean |change of mid| per 5 s in [T, T+15 s) to the same in [T-60 s, T-30 s), trading days / venue-shut
days (n days). Full table: `out/profile_o.txt`.

| clock | instrument: trading day / venue shut |
|---|---|
| ASX-OPEN, AEST (00:00 UTC) | AUD 2.5, NZD 2.4, XAU 3.0, US30 3.7, USTEC 3.5 / no clean placebo (TSE opens at the same instant) |
| ASX-OPEN, AEDT (23:00 UTC; includes the northern-winter days the rollover rule later removes) | AUD 2.9 / 3.3 (24); NZD 3.0 / 12.1; XAU 11.8 / 24.4 (23); US30 7.2 / 16.4 (21); USTEC 6.5 / 18.5 (21) |
| TSE-OPEN (00:00 UTC) | AUD 2.6 / 2.6 (50); NZD 2.6 / 2.4; XAU 3.1 / 2.8; US30 3.3 / 2.4 (48); USTEC 3.3 / 2.1 |
| CNHK-AM (01:30 UTC) | AUD 3.6 / 5.0 (43); XAU 1.5 / 1.8; US30 2.0 / 2.0 (41); USTEC 2.1 / 1.9 |
| CNHK-PM (05:00 UTC) | AUD 1.8 / 1.5 (49); XAU 1.9 / 2.4; US30 2.4 / 1.6 (47); USTEC 2.5 / 1.7 |
| SGE-NIGHT (12:00 UTC) | XAU 2.2 / 1.8 (137) / 2020 window 2.1 (67); XAG 2.8 / 2.3 / 2.6 |
| TSE-PM (03:30 UTC, info) | AUD 1.7 / 1.6 (98); NZD 1.5 / 1.5; XAU 1.4 / 1.1; US30 2.1 / 1.5 (96); USTEC 2.0 / 1.3 |

Reading:
- 00:00 UTC is a clock in IC's feed whether or not Tokyo opens: the TSE-holiday spike is 90-100 % of the trading-day
  one in FX and gold and 64-73 % in the US indices.
- 01:30 UTC in AUD is busier on Chinese holidays than on trading days. Split by Sydney season (an unsigned check
  added after the numbers): on SSE / HKEX trading days the ratio is x5.7 under AEST, when Australian data come out at
  11:30 AEST = 01:30 UTC, and x1.5 under AEDT. So the spike is the Australian release clock, not the A-share open.
  The calendar exclusions remove the release days from the cells.
- At 23:00 UTC in the northern winter the gold and index spikes are IC's / CME's daily reopen (larger on ASX
  holidays), which the rollover rule removes.

## 1. Event counts
Columns: valid OPEN days with an opening move at w = 15 s; events at k = 0 / 2 / 4 after the h = 15 exclusions,
IS / VAL; placebo days with a valid move (all years); SGE's 2020 window. Per-year counts are in HYPOTHESES_O.md.

| clock | instrument | valid OPEN days IS / VAL | k0 IS / VAL | k2 IS / VAL | k4 IS / VAL | HOL days | 2020 SUSP days |
|---|---|---|---|---|---|---|---|
| ASX-OPEN | AUDUSD | 1467 / 736 | 766 / 393 | 167 / 74 | 37 / 14 | 26 | 0 |
| ASX-OPEN | NZDUSD | 1441 / 741 | 742 / 397 | 178 / 72 | 55 / 13 | 25 | 0 |
| ASX-OPEN | XAUUSD | 961 / 482 | 765 / 395 | 178 / 89 | 41 / 25 | 1 | 0 |
| ASX-OPEN | US30 | 882 / 461 | 700 / 377 | 151 / 77 | 49 / 16 | 2 | 0 |
| ASX-OPEN | USTEC | 903 / 478 | 726 / 390 | 176 / 91 | 56 / 24 | 2 | 0 |
| TSE-OPEN | AUDUSD | 1400 / 691 | 1062 / 546 | 266 / 96 | 74 / 22 | 67 | 0 |
| TSE-OPEN | NZDUSD | 1387 / 710 | 1047 / 563 | 255 / 111 | 54 / 18 | 69 | 0 |
| TSE-OPEN | XAUUSD | 1418 / 715 | 1095 / 568 | 235 / 143 | 49 / 34 | 70 | 0 |
| TSE-OPEN | US30 | 1318 / 682 | 1019 / 543 | 222 / 110 | 60 / 16 | 64 | 0 |
| TSE-OPEN | USTEC | 1353 / 701 | 1053 / 557 | 254 / 140 | 71 / 25 | 61 | 0 |
| ASX+TSE | AUDUSD | 695 / 345 | 546 / 274 | 118 / 43 | 32 / 3 | 0 | 0 |
| ASX+TSE | NZDUSD | 679 / 345 | 529 / 272 | 122 / 42 | 34 / 2 | 0 | 0 |
| ASX+TSE | XAUUSD | 705 / 349 | 552 / 276 | 101 / 67 | 16 / 18 | 0 | 0 |
| ASX+TSE | US30 | 666 / 334 | 525 / 264 | 114 / 60 | 29 / 16 | 0 | 0 |
| ASX+TSE | USTEC | 674 / 348 | 538 / 274 | 121 / 80 | 35 / 27 | 0 | 0 |
| CNHK-AM | AUDUSD | 1450 / 718 | 894 / 464 | 191 / 87 | 51 / 17 | 53 | 0 |
| CNHK-AM | XAUUSD | 1458 / 733 | 1100 / 543 | 236 / 138 | 48 / 31 | 59 | 0 |
| CNHK-AM | US30 | 1381 / 686 | 1028 / 511 | 208 / 84 | 56 / 14 | 51 | 0 |
| CNHK-AM | USTEC | 1383 / 734 | 1033 / 544 | 203 / 116 | 60 / 24 | 56 | 0 |
| CNHK-PM | AUDUSD | 1387 / 694 | 1136 / 563 | 263 / 106 | 67 / 12 | 66 | 0 |
| CNHK-PM | XAUUSD | 1414 / 723 | 1160 / 586 | 287 / 126 | 75 / 26 | 66 | 0 |
| CNHK-PM | US30 | 1245 / 674 | 1017 / 550 | 199 / 98 | 57 / 22 | 49 | 0 |
| CNHK-PM | USTEC | 1315 / 715 | 1075 / 583 | 222 / 126 | 71 / 33 | 56 | 0 |
| SGE-NIGHT | XAUUSD | 1321 / 693 | 1048 / 552 | 220 / 113 | 41 / 29 | 205 | 66 |
| SGE-NIGHT | XAGUSD | 1232 / 672 | 978 / 534 | 194 / 121 | 47 / 18 | 182 | 65 |
| TSE-PM | AUDUSD | 1321 / 665 | 1073 / 537 | 260 / 125 | 68 / 22 | 121 | 0 |
| TSE-PM | NZDUSD | 1310 / 682 | 1075 / 554 | 312 / 139 | 122 / 27 | 128 | 0 |
| TSE-PM | XAUUSD | 1367 / 705 | 1113 / 574 | 253 / 114 | 66 / 24 | 132 | 0 |
| TSE-PM | US30 | 1261 / 630 | 1044 / 505 | 203 / 106 | 53 / 24 | 113 | 0 |
| TSE-PM | USTEC | 1312 / 684 | 1078 / 552 | 211 / 131 | 49 / 35 | 121 | 0 |

Median |opening move| (bp, w = 15 s, OPEN days, IS / VAL) and median entry spread at L250 (bp, IS / VAL):

| clock | instrument | median abs m IS / VAL | median spread IS / VAL |
|---|---|---|---|
| ASX-OPEN | AUDUSD | 0.77 / 0.91 | 0.51 / 0.29 |
| ASX-OPEN | NZDUSD | 0.75 / 0.89 | 0.86 / 0.99 |
| ASX-OPEN | XAUUSD | 0.82 / 0.80 | 0.94 / 0.52 |
| ASX-OPEN | US30 | 0.88 / 0.74 | 1.41 / 0.44 |
| ASX-OPEN | USTEC | 0.90 / 1.04 | 2.85 / 1.36 |
| TSE-OPEN | AUDUSD | 0.70 / 0.83 | 0.38 / 0.00 |
| TSE-OPEN | NZDUSD | 0.78 / 0.82 | 0.60 / 0.77 |
| TSE-OPEN | XAUUSD | 0.85 / 0.78 | 0.92 / 0.51 |
| TSE-OPEN | US30 | 0.96 / 0.75 | 1.41 / 0.44 |
| TSE-OPEN | USTEC | 0.94 / 1.03 | 2.91 / 1.36 |
| ASX+TSE | AUDUSD | 0.70 / 0.89 | 0.30 / 0.00 |
| ASX+TSE | NZDUSD | 0.72 / 0.88 | 0.58 / 0.70 |
| ASX+TSE | XAUUSD | 0.91 / 0.78 | 0.92 / 0.52 |
| ASX+TSE | US30 | 0.95 / 0.75 | 1.43 / 0.44 |
| ASX+TSE | USTEC | 1.00 / 1.09 | 2.85 / 1.34 |
| CNHK-AM | AUDUSD | 0.82 / 1.10 | 0.39 / 0.00 |
| CNHK-AM | XAUUSD | 0.74 / 0.88 | 0.88 / 0.49 |
| CNHK-AM | US30 | 0.81 / 0.57 | 1.41 / 0.44 |
| CNHK-AM | USTEC | 0.89 / 0.81 | 2.90 / 1.35 |
| CNHK-PM | AUDUSD | 0.47 / 0.69 | 0.28 / 0.00 |
| CNHK-PM | XAUUSD | 0.49 / 0.56 | 0.85 / 0.47 |
| CNHK-PM | US30 | 0.57 / 0.43 | 1.36 / 0.44 |
| CNHK-PM | USTEC | 0.64 / 0.57 | 2.84 / 1.36 |
| SGE-NIGHT | XAUUSD | 0.98 / 0.95 | 0.70 / 0.38 |
| SGE-NIGHT | XAGUSD | 2.63 / 2.20 | 3.35 / 3.88 |
| TSE-PM | AUDUSD | 0.40 / 0.55 | 0.29 / 0.00 |
| TSE-PM | NZDUSD | 0.38 / 0.49 | 0.57 / 0.58 |
| TSE-PM | XAUUSD | 0.46 / 0.49 | 0.85 / 0.45 |
| TSE-PM | US30 | 0.57 / 0.39 | 1.38 / 0.44 |
| TSE-PM | USTEC | 0.64 / 0.48 | 2.87 / 1.36 |

## 2. Results
### Primary cells (w 15 s, h 15 min, no stop, k 2 / 4); bp per trade, t clustered by UTC day
Columns:
- latencies: net at L0 / **L250, the decision latency** / L1000 / next tick / +1 min;
- years > 0: years with events whose net is > 0;
- power: per-trade (and per-day) net Sharpe x sqrt(1.73 x events per year), at the IS and the VAL size;
- placebo: the same rule on venue-shut days, all years pooled, t clustered by holiday block, with the
  trading-minus-placebo difference t;
- shifted: mean net at T - 30 / T + 30 min;
- RD / RT: the share of random-direction / random-time seeds the cell beats.

| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | years > 0 | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN ALL V1 w15 k2 h15 none | 850 / 403 | -1.50 (-3.06) / -0.45 (-0.81) | -3.34 / **-3.33 (-6.66)** / -3.29 / -3.33 / -2.83 | -1.43 / **-1.39 (-2.49)** / -1.37 / -1.42 / -1.49 | -4.05 / -1.69 | +0.42 | 0/9 | -4.95 / -2.37 | -3.47 / -1.88 | HOL n2 -2.80 (diff t +0.04) | -1.87 / -0.84; -1.07 / -0.76 | 0.00 / 0.15 | 0.00 / 0.10 | fail |
| ASX-OPEN ALL V2 w15 k2 h15 none | 850 / 403 | +1.50 (+3.06) / +0.45 (+0.81) | -0.31 / **-0.32 (-0.66)** / -0.36 / -0.32 / -0.80 | -0.46 / **-0.50 (-0.90)** / -0.52 / -0.47 / -0.38 | -1.05 / -0.80 | +1.54 | 1/9 | -0.48 / -0.85 | -0.36 / -0.68 | HOL n2 -0.06 (diff t -0.72) | -1.72 / -1.25; -2.34 / -1.25 | 1.00 / 0.84 | 1.00 / 0.90 | fail |
| ASX-OPEN ALL V1 w15 k4 h15 none | 238 / 92 | -2.00 (-1.76) / -0.12 (-0.09) | -4.01 / **-3.97 (-3.47)** / -3.90 / -3.93 / -3.38 | -1.16 / **-1.05 (-0.80)** / -1.01 / -1.13 / -1.44 | -4.79 / -1.35 | +0.27 | 0/9 | -2.43 / -0.76 | -1.81 / -0.61 | - | -2.27 / -0.83; -0.22 / +0.05 | 0.01 / 0.43 | 0.01 / 0.38 | fail |
| ASX-OPEN ALL V2 w15 k4 h15 none | 238 / 92 | +2.00 (+1.76) / +0.12 (+0.09) | +0.07 / **+0.04 (+0.03)** / -0.03 / +0.00 / -0.50 | -0.71 / **-0.82 (-0.62)** / -0.85 / -0.73 / -0.45 | -0.78 / -1.11 | -22.06 | 2/9 | +0.02 / -0.59 | +0.02 / -0.47 | - | -1.45 / -1.26; -3.23 / -2.21 | 0.99 / 0.56 | 1.00 / 0.64 | fail |
| TSE-OPEN ALL V1 w15 k2 h15 none | 1232 / 600 | -0.89 (-1.92) / -0.44 (-1.02) | -2.64 / **-2.64 (-5.64)** / -2.64 / -2.68 / -2.26 | -1.42 / **-1.41 (-3.24)** / -1.39 / -1.40 / -1.36 | -3.33 / -1.72 | +0.53 | 0/9 | -4.36 / -3.08 | -2.97 / -2.45 | HOL n66 -0.49 (diff t -1.21) | -1.16 / -0.38; -1.50 / -1.73 | 0.00 / 0.10 | 0.01 / 0.07 | fail |
| TSE-OPEN ALL V2 w15 k2 h15 none | 1232 / 600 | +0.89 (+1.92) / +0.44 (+1.02) | -0.86 / **-0.86 (-1.85)** / -0.85 / -0.82 / -1.22 | -0.52 / **-0.53 (-1.22)** / -0.54 / -0.54 / -0.57 | -1.55 / -0.84 | +0.61 | 2/9 | -1.43 / -1.17 | -1.00 / -0.93 | HOL n66 -2.87 (diff t +1.36) | -2.29 / -1.65; -1.84 / -0.23 | 1.00 / 0.89 | 0.99 / 0.93 | fail |
| TSE-OPEN ALL V1 w15 k4 h15 none | 308 / 115 | -2.17 (-1.67) / -1.92 (-1.79) | -4.03 / **-4.06 (-3.10)** / -4.05 / -4.11 / -2.81 | -2.93 / **-2.87 (-2.65)** / -2.84 / -2.87 / -3.26 | -4.83 / -3.15 | +0.71 | 1/9 | -2.37 / -2.41 | -1.60 / -2.00 | HOL n11 +2.11 (diff t -1.54) | -0.38 / +0.45; -1.23 / -2.44 | 0.01 / 0.01 | 0.01 / 0.00 | fail |
| TSE-OPEN ALL V2 w15 k4 h15 none | 308 / 115 | +2.17 (+1.67) / +1.92 (+1.79) | +0.26 / **+0.28 (+0.22)** / +0.31 / +0.34 / -0.91 | +1.02 / **+0.97 (+0.91)** / +0.94 / +0.97 / +1.35 | -0.49 / +0.68 | +3.44 | 4/9 | +0.17 / +0.83 | +0.12 / +0.69 | HOL n11 -6.70 (diff t +1.69) | -3.11 / -2.57; -2.41 / +0.33 | 0.99 / 0.98 | 0.99 / 0.99 | fail |
| ASX+TSE ALL V1 w15 k2 h15 none | 576 / 292 | -1.30 (-2.03) / -0.83 (-1.17) | -3.05 / **-3.04 (-4.72)** / -3.01 / -3.07 / -2.58 | -1.81 / **-1.75 (-2.44)** / -1.74 / -1.75 / -2.01 | -3.73 / -2.05 | +0.58 | 0/9 | -3.71 / -2.28 | -2.49 / -1.84 | - | -1.23 / -0.86; -1.08 / -1.55 | 0.00 / 0.05 | 0.00 / 0.01 | fail |
| ASX+TSE ALL V2 w15 k2 h15 none | 576 / 292 | +1.30 (+2.03) / +0.83 (+1.17) | -0.42 / **-0.43 (-0.67)** / -0.46 / -0.41 / -0.88 | -0.03 / **-0.09 (-0.13)** / -0.10 / -0.09 / +0.18 | -1.12 / -0.39 | +0.21 | 3/9 | -0.53 / -0.12 | -0.36 / -0.10 | - | -2.25 / -1.08; -2.15 / -0.39 | 1.00 / 0.91 | 1.00 / 0.99 | fail |
| ASX+TSE ALL V1 w15 k4 h15 none | 146 / 66 | -1.22 (-0.72) / -2.36 (-1.23) | -3.10 / **-3.07 (-1.82)** / -3.05 / -3.09 / -2.63 | -3.42 / **-3.31 (-1.71)** / -3.26 / -3.36 / -4.02 | -3.83 / -3.68 | +1.08 | 0/9 | -1.43 / -1.51 | -0.96 / -1.30 | - | -0.87 / -1.38; -1.55 / -0.27 | 0.15 / 0.11 | 0.04 / 0.01 | fail |
| ASX+TSE ALL V2 w15 k4 h15 none | 146 / 66 | +1.22 (+0.72) / +2.36 (+1.23) | -0.59 / **-0.64 (-0.38)** / -0.63 / -0.61 / -1.07 | +1.52 / **+1.41 (+0.74)** / +1.34 / +1.45 / +2.10 | -1.40 / +1.04 | -2.21 | 4/9 | -0.30 / +0.65 | -0.20 / +0.56 | - | -2.63 / -0.51; -1.71 / -1.80 | 0.87 / 0.93 | 0.96 / 0.99 | fail |
| CNHK-AM ALL V1 w15 k2 h15 none | 838 / 425 | -0.07 (-0.10) / +0.12 (+0.22) | -1.90 / **-1.89 (-2.95)** / -1.92 / -1.89 / -1.70 | -0.80 / **-0.80 (-1.50)** / -0.79 / -0.78 / -0.87 | -2.65 / -1.10 | +0.42 | 0/9 | -2.26 / -1.26 | -1.58 / -1.13 | HOL n32 -0.96 (diff t -0.23) | -1.33 / -0.27; -2.22 / -0.35 | 0.48 / 0.60 | 0.30 / 0.70 | fail |
| CNHK-AM ALL V2 w15 k2 h15 none | 838 / 425 | +0.07 (+0.10) / -0.12 (-0.22) | -1.75 / **-1.76 (-2.80)** / -1.74 / -1.78 / -1.94 | -1.03 / **-1.03 (-1.93)** / -1.04 / -1.05 / -0.94 | -2.52 / -1.33 | +0.59 | 0/9 | -2.12 / -1.63 | -1.50 / -1.47 | HOL n32 -2.18 (diff t +0.25) | -2.53 / -1.49; -1.34 / -1.34 | 0.54 / 0.39 | 0.71 / 0.29 | fail |
| CNHK-AM ALL V1 w15 k4 h15 none | 215 / 86 | -0.09 (-0.04) / +1.32 (+0.73) | -2.00 / **-1.96 (-0.99)** / -2.00 / -1.88 / -1.14 | +0.37 / **+0.39 (+0.22)** / +0.36 / +0.40 / +0.03 | -2.76 / +0.10 | -0.20 | 4/9 | -0.79 / +0.21 | -0.53 / +0.16 | HOL n9 +3.05 (diff t -1.38) | -1.26 / +1.15; -3.03 / +0.35 | 0.52 / 0.82 | 0.35 / 0.91 | fail |
| CNHK-AM ALL V2 w15 k4 h15 none | 215 / 86 | +0.09 (+0.04) / -1.32 (-0.73) | -1.76 / **-1.79 (-0.92)** / -1.77 / -1.87 / -2.58 | -2.24 / **-2.25 (-1.24)** / -2.24 / -2.27 / -1.90 | -2.59 / -2.55 | +1.26 | 3/9 | -0.73 / -1.23 | -0.50 / -0.94 | HOL n9 -5.81 (diff t +1.15) | -3.02 / -2.91; -0.92 / -1.98 | 0.53 / 0.17 | 0.63 / 0.10 | fail |
| CNHK-PM ALL V1 w15 k2 h15 none | 971 / 456 | -0.19 (-0.35) / +0.54 (+1.12) | -1.87 / **-1.90 (-3.48)** / -1.91 / -1.90 / -2.02 | -0.35 / **-0.36 (-0.75)** / -0.34 / -0.33 / -0.12 | -2.58 / -0.66 | +0.19 | 2/9 | -2.59 / -0.72 | -1.85 / -0.57 | HOL n31 -0.66 (diff t -0.82) | -2.07 / -0.01; -1.69 / -0.69 | 0.34 / 0.91 | 0.23 / 0.86 | fail |
| CNHK-PM ALL V2 w15 k2 h15 none | 971 / 456 | +0.19 (+0.35) / -0.54 (-1.12) | -1.56 / **-1.52 (-2.87)** / -1.53 / -1.53 / -1.42 | -1.44 / **-1.43 (-2.98)** / -1.46 / -1.46 / -1.67 | -2.21 / -1.73 | +0.94 | 0/9 | -2.12 / -2.86 | -1.54 / -2.25 | HOL n31 -2.13 (diff t +0.67) | -1.21 / -1.74; -1.72 / -1.09 | 0.68 / 0.08 | 0.68 / 0.12 | fail |
| CNHK-PM ALL V1 w15 k4 h15 none | 270 / 93 | -1.94 (-1.21) / +0.23 (+0.17) | -3.68 / **-3.76 (-2.28)** / -3.74 / -3.77 / -3.92 | -0.72 / **-0.73 (-0.54)** / -0.75 / -0.75 / +0.39 | -4.52 / -1.09 | +0.19 | 2/9 | -1.76 / -0.53 | -1.21 / -0.41 | HOL n7 -0.68 (diff t -1.15) | -2.57 / +0.43; -2.30 / -0.53 | 0.04 / 0.58 | 0.01 / 0.56 | fail |
| CNHK-PM ALL V2 w15 k4 h15 none | 270 / 93 | +1.94 (+1.21) / -0.23 (-0.17) | +0.04 / **+0.12 (+0.08)** / +0.09 / +0.14 / +0.26 | -1.21 / **-1.19 (-0.89)** / -1.19 / -1.19 / -2.32 | -0.63 / -1.55 | -9.88 | 3/9 | +0.06 / -0.86 | +0.04 / -0.68 | HOL n7 -2.09 (diff t +0.98) | -0.74 / -2.26; -1.42 / -1.30 | 0.96 / 0.43 | 0.98 / 0.43 | fail |
| SGE-NIGHT ALL V1 w15 k2 h15 none | 414 / 234 | +2.43 (+1.88) / -0.58 (-0.57) | -0.19 / **-0.20 (-0.16)** / -0.21 / -0.22 / -1.32 | -3.44 / **-3.39 (-3.30)** / -3.35 / -3.40 / -3.59 | -1.22 / -4.50 | +16.73 | 2/9 | -0.09 / -2.63 | -0.08 / -2.50 | HOL n64 -2.60 (diff t +0.56) | -1.97 / -1.32; -0.13 / -2.12 | 0.98 / 0.27 | 1.00 / 0.26 | fail |
| SGE-NIGHT ALL V2 w15 k2 h15 none | 414 / 234 | -2.43 (-1.88) / +0.58 (+0.57) | -5.12 / **-5.06 (-3.90)** / -5.09 / -5.06 / -3.95 | -2.18 / **-2.24 (-2.24)** / -2.31 / -2.28 / -1.96 | -6.07 / -3.35 | +0.44 | 0/9 | -2.32 / -1.79 | -2.11 / -1.70 | HOL n64 -2.33 (diff t -0.78) | -3.52 / -3.97; -4.89 / -3.49 | 0.02 / 0.73 | 0.00 / 0.74 | fail |
| SGE-NIGHT ALL V1 w15 k4 h15 none | 88 / 47 | +8.63 (+2.14) / +0.13 (+0.06) | +5.37 / **+5.33 (+1.33)** / +5.12 / +5.25 / +2.20 | -2.34 / **-2.27 (-1.08)** / -2.31 / -2.41 / -2.31 | +3.99 / -3.17 | -0.43 | 6/9 | +0.77 / -0.87 | +0.72 / -0.84 | HOL n13 -7.95 (diff t +1.88) | -0.24 / -5.49; +2.25 / -2.50 | 0.98 / 0.54 | 0.99 / 0.47 | fail |
| SGE-NIGHT ALL V2 w15 k4 h15 none | 88 / 47 | -8.63 (-2.14) / -0.13 (-0.06) | -12.08 / **-11.92 (-2.92)** / -11.84 / -11.93 / -8.49 | -2.51 / **-2.52 (-1.28)** / -2.56 / -2.48 / -2.44 | -13.27 / -3.42 | +0.21 | 1/9 | -1.66 / -1.03 | -1.59 / -0.94 | HOL n13 +2.89 (diff t -1.96) | -6.15 / +0.53; -7.76 / -3.34 | 0.01 / 0.46 | 0.00 / 0.52 | fail |

### Every set at the primary spec (w 15 s, h 15 min, no stop): net at L250, bp (t), IS / VAL
| clock | set | n k2 IS / VAL | V1 k2 | V2 k2 | n k4 IS / VAL | V1 k4 | V2 k4 | V1 mid k2 IS / VAL | spread paid k2 IS / VAL (+0.6 commission for FX, metals) |
|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN | AUDUSD | 167 / 74 | -1.95 (-3.1) / -0.66 (-0.7) | -0.10 (-0.2) / -0.86 (-0.9) | 37 / 14 | -3.17 (-2.5) / +3.92 (+1.9) | +0.74 (+0.6) / -5.44 (-2.7) | -0.93 (-1.5) / +0.10 (+0.1) | +0.43 / +0.16 |
| ASX-OPEN | NZDUSD | 178 / 72 | -2.29 (-3.2) / -2.21 (-2.4) | -0.44 (-0.6) / -0.49 (-0.5) | 55 / 13 | -4.17 (-2.7) / +0.04 (+0.0) | +1.03 (+0.7) / -2.58 (-1.0) | -0.93 (-1.3) / -0.86 (-0.9) | +0.77 / +0.75 |
| ASX-OPEN | XAUUSD | 178 / 89 | -2.82 (-3.9) / -0.63 (-1.0) | -0.90 (-1.2) / -1.58 (-2.4) | 41 / 25 | -1.11 (-0.6) / -0.81 (-0.7) | -2.68 (-1.4) / -1.30 (-1.1) | -0.96 (-1.3) / +0.47 (+0.7) | +1.26 / +0.50 |
| ASX-OPEN | US30 | 151 / 77 | -4.07 (-3.9) / -0.08 (-0.1) | +1.11 (+1.1) / -0.77 (-0.9) | 49 / 16 | -4.99 (-2.0) / -2.06 (-0.7) | +1.69 (+0.7) / +1.21 (+0.4) | -2.59 (-2.5) / +0.34 (+0.4) | +1.48 / +0.43 |
| ASX-OPEN | USTEC | 176 / 91 | -5.54 (-6.4) / -3.19 (-2.4) | -1.06 (-1.2) / +1.07 (+0.8) | 56 / 24 | -5.51 (-2.7) / -4.13 (-1.5) | -0.86 (-0.4) / +2.00 (+0.7) | -2.24 (-2.6) / -2.13 (-1.6) | +3.30 / +1.06 |
| ASX-OPEN | FX | 345 / 146 | -2.13 (-3.5) / -1.42 (-1.8) | -0.28 (-0.5) / -0.68 (-0.8) | 92 / 27 | -3.77 (-3.4) / +2.05 (+1.1) | +0.92 (+0.8) / -4.06 (-2.2) | -0.93 (-1.5) / -0.37 (-0.5) | +0.60 / +0.45 |
| ASX-OPEN | INDICES | 327 / 168 | -4.86 (-5.3) / -1.77 (-1.9) | -0.06 (-0.1) / +0.23 (+0.2) | 105 / 40 | -5.26 (-2.4) / -3.30 (-1.3) | +0.33 (+0.1) / +1.68 (+0.7) | -2.40 (-2.6) / -1.00 (-1.1) | +2.46 / +0.77 |
| ASX-OPEN | ALL | 850 / 403 | -3.33 (-6.7) / -1.39 (-2.5) | -0.32 (-0.7) / -0.50 (-0.9) | 238 / 92 | -3.97 (-3.5) / -1.05 (-0.8) | +0.04 (+0.0) / -0.82 (-0.6) | -1.50 (-3.1) / -0.45 (-0.8) | +1.45 / +0.59 |
| TSE-OPEN | AUDUSD | 266 / 96 | -1.58 (-3.2) / -1.84 (-2.2) | -0.42 (-0.9) / +0.38 (+0.5) | 74 / 22 | -2.97 (-3.1) / -0.78 (-0.4) | +0.82 (+0.9) / -0.77 (-0.4) | -0.58 (-1.2) / -1.11 (-1.3) | +0.40 / +0.13 |
| TSE-OPEN | NZDUSD | 255 / 111 | -1.32 (-2.8) / -2.56 (-3.3) | -1.23 (-2.6) / -0.06 (-0.1) | 54 / 18 | -3.29 (-3.1) / -2.98 (-1.2) | +0.51 (+0.5) / +0.40 (+0.2) | -0.05 (-0.1) / -1.25 (-1.6) | +0.67 / +0.71 |
| TSE-OPEN | XAUUSD | 235 / 143 | -2.31 (-3.9) / -1.59 (-2.6) | -1.15 (-2.0) / -0.67 (-1.1) | 49 / 34 | -1.28 (-0.7) / -4.93 (-2.9) | -3.01 (-1.7) / +2.51 (+1.6) | -0.58 (-1.0) / -0.46 (-0.8) | +1.13 / +0.53 |
| TSE-OPEN | US30 | 222 / 110 | -3.47 (-3.4) / -0.25 (-0.3) | +0.46 (+0.5) / -0.59 (-0.8) | 60 / 16 | -6.08 (-2.0) / -2.47 (-1.4) | +2.78 (+0.9) / +1.69 (+1.0) | -1.96 (-1.9) / +0.17 (+0.2) | +1.50 / +0.42 |
| TSE-OPEN | USTEC | 254 / 140 | -4.66 (-4.9) / -0.93 (-1.0) | -1.84 (-2.0) / -1.33 (-1.5) | 71 / 25 | -5.98 (-2.4) / -2.10 (-1.0) | -0.30 (-0.1) / +0.34 (+0.2) | -1.41 (-1.5) / +0.20 (+0.2) | +3.25 / +1.13 |
| TSE-OPEN | FX | 521 / 207 | -1.45 (-3.5) / -2.22 (-3.3) | -0.81 (-2.0) / +0.14 (+0.2) | 128 / 40 | -3.11 (-3.6) / -1.77 (-1.0) | +0.69 (+0.8) / -0.24 (-0.1) | -0.32 (-0.8) / -1.18 (-1.8) | +0.53 / +0.44 |
| TSE-OPEN | INDICES | 476 / 250 | -4.11 (-4.4) / -0.63 (-0.9) | -0.77 (-0.8) / -1.00 (-1.4) | 131 / 41 | -6.02 (-2.3) / -2.24 (-1.3) | +1.11 (+0.4) / +0.87 (+0.5) | -1.67 (-1.8) / +0.18 (+0.3) | +2.44 / +0.82 |
| TSE-OPEN | ALL | 1232 / 600 | -2.64 (-5.6) / -1.41 (-3.2) | -0.86 (-1.8) / -0.53 (-1.2) | 308 / 115 | -4.06 (-3.1) / -2.87 (-2.6) | +0.28 (+0.2) / +0.97 (+0.9) | -0.89 (-1.9) / -0.44 (-1.0) | +1.38 / +0.62 |
| ASX+TSE | AUDUSD | 118 / 43 | -1.53 (-2.0) / -1.74 (-1.4) | -0.35 (-0.5) / +0.26 (+0.2) | 32 / 3 | -2.50 (-1.4) / +6.92 (+3.1) | +0.59 (+0.3) / -8.40 (-4.0) | -0.59 (-0.8) / -1.00 (-0.8) | +0.34 / +0.14 |
| ASX+TSE | NZDUSD | 122 / 42 | -1.90 (-2.3) / -2.88 (-2.2) | -0.55 (-0.7) / +0.24 (+0.2) | 34 / 2 | -2.77 (-1.5) / -11.61 (-2.8) | +0.31 (+0.2) / +9.01 (+2.0) | -0.68 (-0.8) / -1.56 (-1.2) | +0.62 / +0.72 |
| ASX+TSE | XAUUSD | 101 / 67 | -2.86 (-3.0) / -0.03 (-0.0) | -0.64 (-0.7) / -2.07 (-2.7) | 16 / 18 | +3.10 (+0.9) / -1.24 (-1.0) | -6.88 (-1.8) / -0.82 (-0.6) | -1.11 (-1.2) / +1.02 (+1.3) | +1.15 / +0.45 |
| ASX+TSE | US30 | 114 / 60 | -3.77 (-3.1) / -0.33 (-0.3) | +0.76 (+0.6) / -0.50 (-0.5) | 29 / 16 | -5.73 (-1.8) / -2.18 (-0.8) | +2.46 (+0.8) / +1.34 (+0.5) | -2.26 (-1.9) / +0.08 (+0.1) | +1.51 / +0.41 |
| ASX+TSE | USTEC | 121 / 80 | -5.12 (-4.8) / -3.66 (-2.3) | -1.34 (-1.2) / +1.52 (+1.0) | 35 / 27 | -4.50 (-1.7) / -5.89 (-1.7) | -2.41 (-0.9) / +3.48 (+1.0) | -1.89 (-1.8) / -2.59 (-1.6) | +3.23 / +1.07 |
| ASX+TSE | FX | 240 / 85 | -1.72 (-2.5) / -2.30 (-2.1) | -0.45 (-0.6) / +0.25 (+0.2) | 66 / 5 | -2.64 (-1.6) / -0.49 (-0.1) | +0.45 (+0.3) / -1.44 (-0.3) | -0.63 (-0.9) / -1.28 (-1.2) | +0.48 / +0.43 |
| ASX+TSE | INDICES | 235 / 140 | -4.47 (-4.1) / -2.23 (-1.8) | -0.32 (-0.3) / +0.66 (+0.5) | 64 / 43 | -5.06 (-1.8) / -4.51 (-1.6) | -0.20 (-0.1) / +2.68 (+0.9) | -2.07 (-1.9) / -1.44 (-1.2) | +2.40 / +0.79 |
| ASX+TSE | ALL | 576 / 292 | -3.04 (-4.7) / -1.75 (-2.4) | -0.43 (-0.7) / -0.09 (-0.1) | 146 / 66 | -3.07 (-1.8) / -3.31 (-1.7) | -0.64 (-0.4) / +1.41 (+0.7) | -1.30 (-2.0) / -0.83 (-1.2) | +1.38 / +0.61 |
| CNHK-AM | AUDUSD | 191 / 87 | -0.59 (-0.9) / -0.93 (-1.1) | -1.42 (-2.1) / -0.54 (-0.7) | 51 / 17 | -1.32 (-0.6) / -5.60 (-2.9) | -0.88 (-0.4) / +4.08 (+2.1) | +0.42 (+0.6) / -0.20 (-0.2) | +0.40 / +0.13 |
| CNHK-AM | XAUUSD | 236 / 138 | -2.62 (-3.9) / -1.28 (-1.3) | -0.59 (-0.9) / -0.90 (-0.9) | 48 / 31 | -2.27 (-1.4) / +1.25 (+0.6) | -0.91 (-0.6) / -3.44 (-1.6) | -1.02 (-1.5) / -0.19 (-0.2) | +1.01 / +0.49 |
| CNHK-AM | US30 | 208 / 84 | -1.26 (-1.2) / +0.05 (+0.1) | -1.62 (-1.6) / -0.90 (-1.3) | 56 / 14 | -3.09 (-1.0) / +2.94 (+0.9) | +0.05 (+0.0) / -3.76 (-1.1) | +0.18 (+0.2) / +0.48 (+0.7) | +1.44 / +0.43 |
| CNHK-AM | USTEC | 203 / 116 | -2.90 (-2.5) / -0.74 (-0.7) | -3.57 (-3.2) / -1.65 (-1.6) | 60 / 24 | -1.20 (-0.4) / +2.05 (+0.6) | -4.99 (-1.6) / -4.31 (-1.4) | +0.34 (+0.3) / +0.45 (+0.4) | +3.24 / +1.19 |
| CNHK-AM | INDICES | 411 / 200 | -2.07 (-2.0) / -0.41 (-0.5) | -2.58 (-2.5) / -1.33 (-1.6) | 116 / 38 | -2.11 (-0.7) / +2.38 (+0.8) | -2.55 (-0.9) / -4.11 (-1.3) | +0.26 (+0.2) / +0.46 (+0.6) | +2.33 / +0.87 |
| CNHK-AM | ALL | 838 / 425 | -1.89 (-3.0) / -0.80 (-1.5) | -1.76 (-2.8) / -1.03 (-1.9) | 215 / 86 | -1.96 (-1.0) / +0.39 (+0.2) | -1.79 (-0.9) / -2.25 (-1.2) | -0.07 (-0.1) / +0.12 (+0.2) | +1.52 / +0.60 |
| CNHK-PM | AUDUSD | 263 / 106 | -0.59 (-1.6) / -0.58 (-0.9) | -1.30 (-3.5) / -0.86 (-1.3) | 67 / 12 | -1.41 (-1.5) / -1.24 (-0.5) | -0.51 (-0.5) / -0.21 (-0.1) | +0.35 (+0.9) / +0.14 (+0.2) | +0.34 / +0.12 |
| CNHK-PM | XAUUSD | 287 / 126 | -1.83 (-3.8) / -1.07 (-1.7) | -1.58 (-3.3) / -1.06 (-1.7) | 75 / 26 | -2.23 (-1.6) / -3.35 (-1.9) | -1.41 (-1.1) / +1.17 (+0.7) | -0.13 (-0.3) / -0.01 (-0.0) | +1.10 / +0.46 |
| CNHK-PM | US30 | 199 / 98 | -1.81 (-1.5) / +0.29 (+0.4) | -1.01 (-0.8) / -1.12 (-1.6) | 57 / 22 | -5.94 (-1.7) / +1.55 (+1.1) | +2.79 (+0.8) / -2.45 (-1.7) | -0.40 (-0.3) / +0.70 (+1.0) | +1.41 / +0.42 |
| CNHK-PM | USTEC | 222 / 126 | -3.60 (-3.3) / +0.03 (+0.0) | -2.19 (-2.0) / -2.54 (-2.7) | 71 / 33 | -5.86 (-2.1) / -0.01 (-0.0) | +0.19 (+0.1) / -2.56 (-1.1) | -0.71 (-0.7) / +1.28 (+1.4) | +2.89 / +1.26 |
| CNHK-PM | INDICES | 421 / 224 | -2.76 (-2.5) / +0.14 (+0.2) | -1.63 (-1.5) / -1.92 (-2.5) | 128 / 55 | -5.90 (-1.9) / +0.61 (+0.3) | +1.35 (+0.4) / -2.52 (-1.4) | -0.56 (-0.5) / +1.03 (+1.4) | +2.19 / +0.89 |
| CNHK-PM | ALL | 971 / 456 | -1.90 (-3.5) / -0.36 (-0.7) | -1.52 (-2.9) / -1.43 (-3.0) | 270 / 93 | -3.76 (-2.3) / -0.73 (-0.5) | +0.12 (+0.1) / -1.19 (-0.9) | -0.19 (-0.3) / +0.54 (+1.1) | +1.37 / +0.59 |
| SGE-NIGHT | XAUUSD | 220 / 113 | -1.03 (-1.3) / -0.81 (-1.1) | -1.78 (-2.3) / -1.18 (-1.6) | 41 / 29 | -1.81 (-1.1) / +0.22 (+0.1) | -1.10 (-0.7) / -2.32 (-1.2) | +0.37 (+0.5) / +0.18 (+0.2) | +0.80 / +0.40 |
| SGE-NIGHT | XAGUSD | 194 / 121 | +0.73 (+0.3) / -5.79 (-3.3) | -8.78 (-3.8) / -3.23 (-1.9) | 47 / 18 | +11.57 (+1.7) / -6.28 (-1.5) | -21.36 (-3.1) / -2.84 (-0.7) | +4.75 (+2.1) / -1.28 (-0.7) | +3.42 / +3.91 |
| SGE-NIGHT | ALL | 414 / 234 | -0.20 (-0.2) / -3.39 (-3.3) | -5.06 (-3.9) / -2.24 (-2.2) | 88 / 47 | +5.33 (+1.3) / -2.27 (-1.1) | -11.92 (-2.9) / -2.52 (-1.3) | +2.43 (+1.9) / -0.58 (-0.6) | +2.03 / +2.21 |
| TSE-PM (info) | AUDUSD | 260 / 125 | -0.91 (-3.3) / -0.49 (-1.1) | -1.00 (-3.6) / -0.91 (-2.0) | 68 / 22 | -0.25 (-0.5) / -1.42 (-1.5) | -1.73 (-3.1) / +0.11 (+0.1) | +0.05 (+0.2) / +0.21 (+0.5) | +0.36 / +0.10 |
| TSE-PM (info) | NZDUSD | 312 / 139 | -0.79 (-2.8) / -1.00 (-2.3) | -1.61 (-5.7) / -1.43 (-3.3) | 122 / 27 | -1.21 (-2.7) / -2.40 (-2.2) | -1.20 (-2.7) / -0.31 (-0.3) | +0.41 (+1.5) / +0.22 (+0.5) | +0.60 / +0.61 |
| TSE-PM (info) | XAUUSD | 253 / 114 | -1.37 (-3.8) / -1.19 (-2.2) | -1.95 (-5.4) / -0.93 (-1.7) | 66 / 24 | -0.37 (-0.4) / -1.59 (-1.2) | -3.08 (-3.1) / -0.59 (-0.5) | +0.29 (+0.8) / -0.13 (-0.2) | +1.06 / +0.46 |
| TSE-PM (info) | US30 | 203 / 106 | -1.11 (-2.0) / -0.08 (-0.1) | -1.84 (-3.2) / -0.75 (-1.0) | 53 / 24 | -1.95 (-1.2) / +1.53 (+0.6) | -1.43 (-0.9) / -2.43 (-0.9) | +0.36 (+0.6) / +0.34 (+0.4) | +1.48 / +0.42 |
| TSE-PM (info) | USTEC | 211 / 131 | -2.51 (-4.0) / -1.48 (-1.9) | -3.57 (-5.5) / -0.90 (-1.1) | 49 / 35 | -2.61 (-1.4) / +0.75 (+0.5) | -3.25 (-1.7) / -3.13 (-2.1) | +0.53 (+0.8) / -0.29 (-0.4) | +3.04 / +1.19 |
| TSE-PM (info) | FX | 572 / 264 | -0.84 (-3.7) / -0.76 (-2.0) | -1.33 (-5.7) / -1.18 (-3.1) | 190 / 49 | -0.86 (-2.2) / -1.96 (-2.3) | -1.39 (-3.5) / -0.12 (-0.1) | +0.25 (+1.1) / +0.21 (+0.6) | +0.49 / +0.37 |
| TSE-PM (info) | INDICES | 414 / 237 | -1.82 (-3.4) / -0.85 (-1.2) | -2.72 (-4.9) / -0.83 (-1.2) | 102 / 59 | -2.27 (-1.4) / +1.07 (+0.6) | -2.30 (-1.4) / -2.84 (-1.6) | +0.45 (+0.8) / -0.01 (-0.0) | +2.27 / +0.84 |
| TSE-PM (info) | ALL | 1239 / 615 | -1.28 (-5.3) / -0.87 (-2.3) | -1.92 (-7.7) / -1.00 (-2.7) | 358 / 132 | -1.17 (-2.1) / -0.54 (-0.6) | -1.96 (-3.4) / -1.42 (-1.6) | +0.32 (+1.3) / +0.06 (+0.2) | +1.20 / +0.57 |

### Best cell per clock and set (largest IS net t over its 72 cells)
| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | years > 0 | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN AUDUSD V1 w60 k2 h60 none | 129 / 80 | +2.56 (+2.27) / -1.04 (-0.64) | +1.56 / **+1.57 (+1.40)** / +1.53 / +1.60 / +1.24 | -1.93 / **-1.78 (-1.10)** / -1.89 / -1.77 / -1.22 | +1.38 / -1.85 | -1.13 | 5/9 | +0.75 / -0.84 | +0.75 / -0.84 | - | -0.45 / -2.00; +0.33 / -1.88 | 0.99 / 0.26 | 0.92 / 0.27 | fail |
| ASX-OPEN NZDUSD V2 w60 k4 h60 none | 33 / 15 | +3.89 (+1.40) / +0.44 (+0.17) | +2.60 / **+2.50 (+0.90)** / +2.60 / +2.45 / +1.94 | -0.98 / **-0.98 (-0.39)** / -1.09 / -0.95 / -2.09 | +2.10 / -1.39 | -0.39 | 4/8 | +0.49 / -0.29 | +0.49 / -0.29 | - | -5.03 / -1.52; -4.75 / +1.14 | 0.91 / 0.56 | 0.81 / 0.56 | fail |
| ASX-OPEN XAUUSD V1 w60 k4 h60 S | 38 / 30 | +4.43 (+1.66) / +0.37 (+0.20) | +1.88 / **+1.90 (+0.72)** / +1.84 / +2.11 / +0.65 | -1.14 / **-0.76 (-0.41)** / -1.01 / -0.78 / +0.49 | +0.93 / -1.03 | -0.40 | 4/8 | +0.39 / -0.31 | +0.39 / -0.31 | HOL n1 -5.70 (diff t -) | -4.79 / -1.59; -3.30 / -4.16 | 0.94 / 0.60 | 0.92 / 0.56 | fail |
| ASX-OPEN US30 V2 w15 k2 h15 none | 151 / 77 | +2.59 (+2.48) / -0.34 (-0.42) | +1.16 / **+1.11 (+1.06)** / +1.05 / +1.15 / -0.14 | -0.74 / **-0.77 (-0.94)** / -0.81 / -0.78 / -0.59 | +0.37 / -0.98 | -0.70 | 4/9 | +0.57 / -0.71 | +0.57 / -0.71 | - | -1.67 / -1.25; -2.06 / -0.23 | 1.00 / 0.36 | 0.99 / 0.28 | fail |
| ASX-OPEN USTEC V1 w15 k4 h60 none | 55 / 24 | +4.72 (+1.11) / -9.24 (-1.82) | +1.56 / **+1.55 (+0.37)** / +1.74 / +1.68 / +2.51 | -10.70 / **-10.30 (-2.03)** / -10.04 / -10.32 / -11.49 | -0.03 / -10.83 | -6.63 | 5/9 | +0.20 / -1.54 | +0.20 / -1.54 | - | -13.49 / -6.39; +0.96 / -7.96 | 0.85 / 0.02 | 0.86 / 0.01 | fail |
| ASX-OPEN FX V2 w15 k4 h15 S | 92 / 27 | +2.08 (+2.47) / -1.36 (-1.43) | +0.66 / **+0.69 (+0.82)** / +0.40 / +0.63 / -0.76 | -2.37 / **-2.39 (-2.53)** / -2.40 / -2.34 / -2.27 | +0.30 / -2.61 | -3.45 | 5/9 | +0.50 / -2.04 | +0.44 / -1.79 | - | -1.05 / -1.05; -1.57 / -1.91 | 1.00 / 0.01 | 0.98 / 0.00 | fail |
| ASX-OPEN INDICES V1 w15 k4 h60 none | 103 / 40 | +4.94 (+1.16) / -7.61 (-1.77) | +2.52 / **+2.49 (+0.59)** / +2.64 / +2.57 / +2.85 | -8.70 / **-8.41 (-1.96)** / -8.22 / -8.43 / -8.82 | +1.27 / -8.82 | -3.38 | 3/9 | +0.43 / -1.79 | +0.32 / -1.42 | - | -13.24 / -5.50; +2.22 / -5.78 | 0.95 / 0.02 | 0.94 / 0.01 | fail |
| ASX-OPEN ALL V1 w15 k4 h60 none | 221 / 90 | +2.31 (+0.87) / -4.25 (-1.79) | +0.36 / **+0.37 (+0.14)** / +0.45 / +0.42 / +0.76 | -5.35 / **-5.20 (-2.19)** / -5.09 / -5.18 / -5.76 | -0.44 / -5.50 | -14.07 | 3/9 | +0.11 / -2.03 | +0.08 / -1.62 | - | -4.14 / -2.62; +3.30 / -2.60 | 0.88 / 0.02 | 0.89 / 0.01 | fail |
| TSE-OPEN AUDUSD V1 w60 k4 h60 none | 24 / 20 | +5.60 (+1.64) / -1.49 (-0.66) | +4.47 / **+4.50 (+1.32)** / +4.60 / +4.58 / +5.38 | -2.91 / **-2.28 (-1.01)** / -3.11 / -2.34 / -2.14 | +4.25 / -2.38 | -0.51 | 4/9 | +0.71 / -0.77 | +0.71 / -0.77 | HOL n2 +4.03 (diff t -0.23) | -1.34 / -0.13; +4.69 / -1.04 | 0.95 / 0.27 | 0.97 / 0.33 | fail |
| TSE-OPEN NZDUSD V1 w15 k2 h60 none | 194 / 96 | +1.69 (+1.82) / -1.91 (-1.30) | +0.42 / **+0.44 (+0.47)** / +0.39 / +0.43 / +0.10 | -3.26 / **-3.26 (-2.20)** / -3.17 / -3.09 / -3.16 | +0.11 / -3.63 | -7.41 | 3/9 | +0.25 / -1.67 | +0.25 / -1.67 | HOL n14 -5.21 (diff t +0.91) | -1.22 / -2.59; -0.15 / -2.07 | 0.97 / 0.09 | 0.95 / 0.04 | fail |
| TSE-OPEN XAUUSD V1 w60 k4 h60 none | 43 / 30 | +7.34 (+2.80) / -4.11 (-0.80) | +5.13 / **+5.18 (+2.01)** / +5.15 / +5.47 / +4.15 | -5.34 / **-5.29 (-1.01)** / -5.42 / -5.25 / -5.92 | +4.40 / -5.58 | -1.02 | 6/9 | +1.08 / -0.77 | +1.08 / -0.77 | HOL n2 +4.66 (diff t -0.52) | -2.71 / +5.52; +0.07 / -4.03 | 0.99 / 0.20 | 0.99 / 0.17 | fail |
| TSE-OPEN US30 V2 w15 k4 h15 none | 60 / 16 | +4.43 (+1.50) / +2.08 (+1.20) | +2.73 / **+2.78 (+0.94)** / +2.70 / +2.83 / -0.04 | +1.72 / **+1.69 (+0.99)** / +1.43 / +1.61 / +1.33 | +1.95 / +1.50 | +0.61 | 6/9 | +0.51 / +0.75 | +0.51 / +0.75 | HOL n2 -18.62 (diff t +3.18) | -4.03 / -1.26; -3.27 / +5.56 | 0.93 / 0.88 | 0.94 / 0.95 | fail |
| TSE-OPEN USTEC V1 w60 k4 h60 none | 45 / 22 | +4.78 (+1.52) / -8.00 (-1.17) | +1.65 / **+1.59 (+0.51)** / +1.56 / +1.74 / -1.72 | -8.99 / **-9.04 (-1.32)** / -8.96 / -8.96 / -12.39 | -0.00 / -9.55 | -5.67 | 4/9 | +0.27 / -1.00 | +0.27 / -1.00 | HOL n4 -23.92 (diff t +1.38) | -7.87 / -3.80; -4.14 / -1.63 | 0.91 / 0.15 | 0.84 / 0.10 | fail |
| TSE-OPEN FX V1 w60 k4 h60 none | 55 / 38 | +3.69 (+1.58) / -2.59 (-1.39) | +2.54 / **+2.52 (+1.08)** / +2.65 / +2.59 / +2.92 | -3.97 / **-3.68 (-1.97)** / -4.04 / -3.66 / -3.01 | +2.24 / -3.92 | -1.46 | 4/9 | +0.64 / -1.57 | +0.57 / -1.50 | HOL n3 +0.27 (diff t -0.04) | -0.23 / -1.86; +2.98 / -0.27 | 0.96 / 0.08 | 0.98 / 0.11 | fail |
| TSE-OPEN INDICES V1 w60 k4 h60 none | 92 / 40 | +4.24 (+1.45) / -6.75 (-1.24) | +1.99 / **+1.91 (+0.65)** / +1.85 / +2.00 / -0.51 | -7.45 / **-7.49 (-1.38)** / -7.52 / -7.42 / -9.54 | +0.74 / -7.86 | -3.93 | 4/9 | +0.44 / -1.33 | +0.35 / -1.02 | HOL n6 -15.68 (diff t +2.42) | -5.26 / -3.51; -4.19 / -0.43 | 0.97 / 0.04 | 0.93 / 0.02 | fail |
| TSE-OPEN ALL V1 w60 k4 h60 none | 190 / 108 | +4.78 (+2.75) / -4.55 (-1.75) | +2.86 / **+2.83 (+1.63)** / +2.83 / +2.96 / +1.54 | -5.64 / **-5.54 (-2.12)** / -5.71 / -5.50 / -6.24 | +2.00 / -5.84 | -1.96 | 4/9 | +1.08 / -1.89 | +0.88 / -1.62 | HOL n11 -7.63 (diff t +1.70) | -2.69 / -1.03; -0.81 / -1.81 | 1.00 / 0.03 | 1.00 / 0.01 | fail |
| ASX+TSE AUDUSD V1 w60 k2 h60 none | 93 / 49 | +2.59 (+1.85) / -3.23 (-1.66) | +1.63 / **+1.65 (+1.18)** / +1.69 / +1.69 / +1.79 | -4.20 / **-3.98 (-2.05)** / -4.23 / -3.99 / -3.20 | +1.48 / -4.05 | -2.41 | 5/9 | +0.63 / -1.55 | +0.63 / -1.55 | - | -0.57 / -0.54; +0.39 / -1.51 | 0.96 / 0.05 | 1.00 / 0.03 | fail |
| ASX+TSE NZDUSD V2 w60 k4 h15 none | 28 / 6 | +3.43 (+2.00) / -5.79 (-1.90) | +2.24 / **+2.26 (+1.31)** / +2.45 / +2.63 / +1.36 | -7.26 / **-7.18 (-2.29)** / -7.08 / -7.05 / -6.71 | +1.97 / -7.57 | -3.18 | 3/8 | +0.70 / -1.74 | +0.70 / -1.74 | - | -2.06 / -2.41; -0.43 / -5.60 | 0.98 / 0.03 | 0.99 / 0.00 | fail |
| ASX+TSE XAUUSD V1 w15 k4 h5 S | 16 / 18 | +4.52 (+2.09) / -0.13 (-0.17) | +2.75 / **+2.69 (+1.28)** / +2.47 / +2.56 / +2.04 | -1.20 / **-1.17 (-1.55)** / -1.25 / -1.14 / -1.86 | +2.07 / -1.40 | -0.44 | 2/9 | +0.69 / -1.18 | +0.69 / -1.18 | - | -2.95 / -1.62; -2.14 / -1.81 | 0.97 / 0.39 | 1.00 / 0.56 | fail |
| ASX+TSE US30 V1 w60 k2 h60 none | 120 / 48 | +4.41 (+2.20) / -2.10 (-1.05) | +2.95 / **+2.96 (+1.49)** / +2.90 / +2.96 / +3.07 | -2.45 / **-2.52 (-1.26)** / -2.61 / -2.48 / -2.93 | +2.24 / -2.73 | -0.85 | 4/9 | +0.80 / -0.96 | +0.80 / -0.96 | - | -2.09 / -0.78; -4.99 / -0.21 | 0.98 / 0.16 | 0.99 / 0.12 | fail |
| ASX+TSE USTEC V1 w15 k4 h60 none | 34 / 27 | +8.54 (+2.42) / -11.36 (-1.99) | +5.10 / **+5.11 (+1.43)** / +5.02 / +5.13 / +4.26 | -12.86 / **-12.56 (-2.20)** / -12.30 / -12.55 / -13.87 | +3.40 / -13.15 | -2.46 | 3/8 | +0.77 / -1.67 | +0.77 / -1.67 | - | -4.49 / -6.04; +4.45 / -2.17 | 0.98 / 0.02 | 0.99 / 0.01 | fail |
| ASX+TSE FX V2 w60 k4 h15 S | 47 / 18 | +2.63 (+1.76) / -4.99 (-3.64) | +1.45 / **+1.54 (+1.03)** / +1.80 / +1.83 / +1.00 | -4.63 / **-5.96 (-4.31)** / -4.62 / -5.92 / -4.92 | +1.29 / -6.15 | -3.88 | 4/9 | +0.65 / -3.41 | +0.54 / -2.63 | - | -1.47 / -2.24; -0.33 / -2.17 | 0.97 / 0.01 | 1.00 / 0.00 | fail |
| ASX+TSE INDICES V1 w15 k4 h60 none | 62 / 43 | +6.37 (+1.92) / -9.58 (-2.00) | +3.76 / **+3.75 (+1.13)** / +3.75 / +3.73 / +2.53 | -10.72 / **-10.49 (-2.19)** / -10.29 / -10.49 / -11.07 | +2.45 / -10.94 | -2.79 | 3/8 | +0.78 / -2.03 | +0.60 / -1.66 | - | -3.84 / -5.54; +3.57 / -2.97 | 0.99 / 0.01 | 0.98 / 0.00 | fail |
| ASX+TSE ALL V1 w15 k4 h60 none | 139 / 66 | +4.21 (+1.79) / -7.47 (-2.30) | +2.33 / **+2.34 (+1.00)** / +2.33 / +2.32 / +1.75 | -8.60 / **-8.43 (-2.59)** / -8.35 / -8.46 / -9.36 | +1.57 / -8.81 | -3.60 | 3/9 | +0.75 / -2.35 | +0.53 / -1.94 | - | -0.99 / -4.31; +1.97 / -0.93 | 0.99 / 0.00 | 1.00 / 0.00 | fail |
| CNHK-AM AUDUSD V2 w60 k4 h60 S | 30 / 13 | +8.17 (+1.11) / -0.96 (-0.32) | +7.07 / **+7.02 (+0.96)** / +7.10 / +7.02 / +8.57 | -1.61 / **-1.71 (-0.57)** / -1.63 / -1.70 / -1.61 | +6.74 / -1.78 | -0.24 | 5/9 | +0.52 / -0.43 | +0.52 / -0.43 | - | +0.05 / +0.79; -3.11 / -2.03 | 0.73 / 0.30 | 1.00 / 0.30 | fail |
| CNHK-AM XAUUSD V2 w15 k2 h60 none | 223 / 130 | +3.46 (+3.42) / -0.35 (-0.24) | +1.85 / **+1.84 (+1.83)** / +1.85 / +1.83 / +1.82 | -1.47 / **-1.45 (-1.02)** / -1.39 / -1.44 / -1.55 | +1.33 / -1.71 | -0.79 | 5/9 | +0.98 / -0.77 | +0.98 / -0.77 | HOL n7 -3.00 (diff t +0.68) | -3.08 / -2.32; +0.17 / -1.10 | 1.00 / 0.43 | 1.00 / 0.39 | fail |
| CNHK-AM US30 V1 w60 k4 h60 none | 47 / 11 | +18.83 (+1.92) / +5.79 (+0.92) | +17.25 / **+17.20 (+1.76)** / +16.92 / +17.10 / +17.77 | +5.25 / **+5.33 (+0.84)** / +5.26 / +5.29 / +4.44 | +16.39 / +5.10 | +0.31 | 6/9 | +0.94 / +0.64 | +0.94 / +0.64 | HOL n1 +2.38 (diff t -) | +2.02 / -2.06; -2.70 / -2.90 | 0.97 / 0.83 | 1.00 / 0.76 | fail |
| CNHK-AM USTEC V1 w60 k4 h60 none | 31 / 22 | +13.21 (+1.02) / +6.81 (+1.08) | +10.37 / **+10.34 (+0.81)** / +10.31 / +10.36 / +11.00 | +5.56 / **+5.64 (+0.90)** / +5.60 / +5.67 / +6.34 | +8.90 / +5.06 | +0.55 | 5/8 | +0.43 / +0.68 | +0.43 / +0.68 | HOL n1 +4.50 (diff t -) | -8.88 / -7.97; -5.00 / -4.89 | 0.81 / 0.85 | 0.94 / 0.84 | fail |
| CNHK-AM INDICES V1 w60 k4 h60 none | 78 / 33 | +16.60 (+1.58) / +6.47 (+1.08) | +14.52 / **+14.47 (+1.39)** / +14.29 / +14.42 / +15.08 | +5.45 / **+5.54 (+0.92)** / +5.49 / +5.54 / +5.71 | +13.41 / +5.07 | +0.38 | 7/9 | +1.00 / +0.91 | +0.74 / +0.69 | HOL n2 +3.44 (diff t +1.10) | -3.64 / -5.25; -3.81 / -3.98 | 0.99 / 0.90 | 1.00 / 0.88 | fail |
| CNHK-AM ALL V1 w60 k4 h60 none | 151 / 70 | +6.62 (+1.57) / +7.40 (+2.17) | +4.83 / **+4.80 (+1.15)** / +4.72 / +4.77 / +5.12 | +6.41 / **+6.45 (+1.88)** / +6.56 / +6.53 / +6.24 | +4.04 / +6.14 | +1.34 | 5/9 | +0.57 / +1.70 | +0.61 / +1.39 | HOL n4 -4.80 (diff t +1.28) | -4.26 / -3.12; -4.17 / -2.65 | 0.90 / 0.99 | 0.98 / 0.98 | fail |
| CNHK-PM AUDUSD V1 w60 k4 h60 none | 52 / 19 | +1.79 (+1.09) / -1.20 (-0.45) | +0.79 / **+0.83 (+0.51)** / +0.88 / +0.91 / -0.22 | -1.91 / **-1.92 (-0.71)** / -1.74 / -1.76 / -2.41 | +0.65 / -1.97 | -2.31 | 5/9 | +0.27 / -0.54 | +0.27 / -0.54 | HOL n1 +4.20 (diff t -) | -0.72 / +0.54; +3.89 / -2.39 | 0.88 / 0.26 | 0.87 / 0.34 | fail |
| CNHK-PM XAUUSD V2 w15 k4 h60 none | 75 / 26 | +3.29 (+1.92) / +2.24 (+0.55) | +1.46 / **+1.50 (+0.87)** / +1.39 / +1.49 / +1.25 | +1.18 / **+1.14 (+0.28)** / +1.21 / +1.20 / +1.35 | +0.91 / +0.89 | +0.76 | 6/9 | +0.47 / +0.21 | +0.47 / +0.21 | HOL n5 +3.15 (diff t -0.51) | -1.76 / +0.14; -8.72 / -2.56 | 0.99 / 0.71 | 0.82 / 0.74 | fail |
| CNHK-PM US30 V2 w15 k4 h15 S | 57 / 22 | +4.75 (+1.61) / -0.94 (-0.88) | +2.97 / **+3.12 (+1.07)** / +1.68 / +3.25 / -1.68 | -1.19 / **-1.38 (-1.30)** / -1.40 / -1.58 / -2.67 | +2.30 / -1.61 | -0.44 | 2/7 | +0.57 / -0.99 | +0.57 / -0.99 | - | +4.33 / -0.42; -1.48 / +0.09 | 0.89 / 0.56 | 0.99 / 0.06 | fail |
| CNHK-PM USTEC V1 w60 k4 h60 none | 63 / 34 | +5.50 (+1.54) / -0.82 (-0.18) | +2.35 / **+2.34 (+0.65)** / +2.14 / +2.26 / +0.44 | -1.91 / **-2.02 (-0.43)** / -2.29 / -2.04 / -2.08 | +0.77 / -2.63 | -0.86 | 4/9 | +0.35 / -0.33 | +0.35 / -0.33 | - | +3.39 / -2.85; +1.60 / +1.96 | 0.93 / 0.44 | 0.80 / 0.40 | fail |
| CNHK-PM INDICES V2 w15 k4 h15 S | 128 / 55 | +4.16 (+1.60) / -0.74 (-0.66) | +1.75 / **+1.83 (+0.71)** / +1.27 / +2.01 / -1.99 | -1.70 / **-1.70 (-1.52)** / -1.69 / -1.81 / -3.69 | +0.67 / -2.18 | -0.93 | 2/8 | +0.53 / -1.47 | +0.38 / -1.15 | HOL n1 +6.02 (diff t -) | +2.42 / -1.30; -2.59 / -0.64 | 0.95 / 0.68 | 1.00 / 0.19 | fail |
| CNHK-PM ALL V2 w15 k4 h15 S | 270 / 93 | +2.24 (+1.76) / -0.44 (-0.50) | +0.38 / **+0.40 (+0.33)** / +0.12 / +0.41 / -1.39 | -1.40 / **-1.41 (-1.58)** / -1.38 / -1.43 / -2.29 | -0.36 / -1.78 | -3.51 | 2/9 | +0.24 / -1.70 | +0.18 / -1.23 | HOL n7 -1.55 (diff t +0.86) | -0.46 / -1.27; -2.15 / -1.12 | 0.94 / 0.86 | 1.00 / 0.18 | fail |
| SGE-NIGHT XAUUSD V2 w60 k4 h60 none | 27 / 18 | +7.93 (+1.59) / -7.91 (-1.26) | +6.46 / **+6.44 (+1.30)** / +6.59 / +6.56 / +7.94 | -8.87 / **-8.89 (-1.41)** / -8.97 / -8.77 / -9.65 | +6.00 / -9.08 | -1.38 | 3/9 | +0.70 / -1.07 | +0.70 / -1.07 | HOL n2 +32.87 (diff t -1.04) | -1.73 / -5.50; -4.32 / +10.51 | 0.92 / 0.12 | 0.97 / 0.26 | fail |
| SGE-NIGHT XAGUSD V2 w60 k4 h60 S | 26 / 12 | +41.35 (+2.03) / +6.64 (+0.73) | +35.46 / **+36.32 (+1.80)** / +35.52 / +34.72 / +29.87 | +1.82 / **+2.25 (+0.25)** / +2.49 / +2.45 / -3.24 | +34.11 / +0.36 | +0.06 | 5/9 | +0.96 / +0.19 | +0.96 / +0.19 | HOL n2 -10.81 (diff t +0.91) | -10.03 / -0.74; +4.82 / -7.59 | 0.96 / 0.83 | 1.00 / 0.90 | fail |
| SGE-NIGHT ALL V2 w60 k4 h60 S | 53 / 30 | +23.02 (+2.09) / -0.43 (-0.11) | +19.41 / **+19.79 (+1.81)** / +19.48 / +19.01 / +16.67 | -3.02 / **-2.79 (-0.71)** / -2.71 / -2.72 / -4.26 | +18.48 / -3.68 | -0.14 | 3/9 | +1.03 / -0.56 | +0.97 / -0.54 | HOL n4 +8.95 (diff t +0.11) | -5.87 / -2.24; +0.47 / -4.78 | 0.98 / 0.40 | 1.00 / 0.46 | fail |
| TSE-PM AUDUSD V2 w60 k4 h60 none | 35 / 13 | +0.60 (+0.30) / +4.97 (+1.59) | -0.30 / **-0.30 (-0.15)** / -0.32 / -0.21 / +0.07 | +4.25 / **+4.24 (+1.36)** / +4.16 / +4.24 / +3.22 | -0.45 / +4.17 | -14.20 | 6/9 | -0.08 / +1.04 | -0.08 / +1.04 | HOL n5 -2.48 (diff t +0.80) | +0.62 / -0.59; +0.31 / +2.64 | 0.58 / 0.94 | 0.58 / 0.85 | info only |
| TSE-PM NZDUSD V1 w60 k4 h5 none | 54 / 9 | +1.16 (+1.42) / -1.90 (-1.24) | -0.07 / **-0.06 (-0.07)** / -0.07 / -0.08 / -1.05 | -3.04 / **-3.10 (-2.01)** / -3.11 / -3.16 / -1.75 | -0.36 / -3.39 | +56.14 | 3/9 | -0.04 / -1.53 | -0.04 / -1.53 | HOL n3 -0.43 (diff t -0.04) | -1.16 / -0.32; -1.87 / +0.62 | 0.92 / 0.10 | 0.96 / 0.06 | info only |
| TSE-PM XAUUSD V2 w60 k4 h60 none | 46 / 21 | +1.88 (+0.63) / +0.26 (+0.10) | -0.28 / **-0.24 (-0.08)** / -0.10 / -0.16 / +0.27 | -0.74 / **-0.72 (-0.29)** / -0.70 / -0.83 / -1.50 | -1.01 / -0.90 | +2.95 | 4/9 | -0.04 / -0.22 | -0.04 / -0.22 | HOL n5 -5.66 (diff t +1.56) | -5.53 / -1.12; -2.92 / -4.85 | 0.67 / 0.53 | 0.65 / 0.56 | info only |
| TSE-PM US30 V1 w15 k4 h60 none | 50 / 22 | +2.18 (+0.61) / +1.94 (+0.56) | +0.49 / **+0.51 (+0.15)** / +0.59 / +0.57 / +0.42 | +1.46 / **+1.48 (+0.43)** / +1.49 / +1.43 / +0.22 | -0.32 / +1.25 | +2.89 | 5/8 | +0.08 / +0.32 | +0.08 / +0.32 | HOL n4 -26.77 (diff t +1.01) | -6.07 / +1.87; -7.63 / +2.75 | 0.70 / 0.68 | 0.68 / 0.63 | info only |
| TSE-PM USTEC V2 w15 k4 h60 none | 48 / 33 | +2.94 (+0.71) / -0.54 (-0.17) | -0.11 / **-0.02 (-0.00)** / -0.11 / -0.11 / -0.35 | -1.73 / **-1.75 (-0.55)** / -1.75 / -1.80 / -0.56 | -1.50 / -2.35 | +100.43 | 2/7 | -0.00 / -0.42 | -0.00 / -0.42 | HOL n5 +13.04 (diff t -0.73) | +4.05 / +4.21; -2.76 / +0.75 | 0.76 / 0.47 | 0.68 / 0.47 | info only |
| TSE-PM FX V1 w60 k4 h5 none | 90 / 22 | +0.95 (+1.69) / -2.52 (-1.96) | -0.14 / **-0.12 (-0.22)** / -0.16 / -0.13 / -0.78 | -3.50 / **-3.45 (-2.68)** / -3.41 / -3.45 / -2.41 | -0.36 / -3.62 | +27.70 | 3/9 | -0.13 / -2.56 | -0.12 / -1.82 | HOL n8 -0.74 (diff t -0.05) | -1.34 / -0.89; -2.04 / +0.02 | 0.97 / 0.01 | 0.97 / 0.00 | info only |
| TSE-PM INDICES V2 w60 k4 h60 none | 150 / 56 | +2.02 (+0.67) / +1.26 (+0.34) | -0.47 / **-0.47 (-0.16)** / -0.48 / -0.41 / -0.11 | +0.49 / **+0.47 (+0.13)** / +0.43 / +0.45 / +1.78 | -1.72 / +0.08 | -0.99 | 4/9 | -0.11 / +0.12 | -0.08 / +0.10 | HOL n11 -5.00 (diff t +1.31) | +3.65 / -0.20; +3.07 / -3.83 | 0.80 / 0.66 | 0.75 / 0.69 | info only |
| TSE-PM ALL V2 w60 k4 h60 none | 282 / 99 | +1.34 (+0.74) / +1.74 (+0.77) | -0.67 / **-0.66 (-0.36)** / -0.64 / -0.61 / -0.20 | +0.89 / **+0.88 (+0.39)** / +0.85 / +0.85 / +1.20 | -1.52 / +0.59 | -1.34 | 4/9 | -0.26 / +0.37 | -0.19 / +0.29 | HOL n24 -3.57 (diff t +1.20) | +0.79 / -0.42; +0.85 / -3.40 | 0.85 / 0.84 | 0.79 / 0.81 | info only |

### Cells meeting the DEMO or LIVE numbers
None (counted or information-only).

### All cells with IS net t >= 1.5 (any VAL)
| cell | n IS / VAL | mid IS / VAL (t) | net IS: L0 / **L250 (t)** / L1000 / next / +1 min | net VAL: L0 / **L250 (t)** / L1000 / next / +1 min | x1.5 IS / VAL | VAL/IS | years > 0 | power trade IS / VAL | power day IS / VAL | venue-shut placebo (all years) | shifted -30 IS / VAL; +30 IS / VAL | RD IS / VAL | RT IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TSE-OPEN XAUUSD V1 w60 k4 h60 none | 43 / 30 | +7.34 (+2.80) / -4.11 (-0.80) | +5.13 / **+5.18 (+2.01)** / +5.15 / +5.47 / +4.15 | -5.34 / **-5.29 (-1.01)** / -5.42 / -5.25 / -5.92 | +4.40 / -5.58 | -1.02 | 6/9 | +1.08 / -0.77 | +1.08 / -0.77 | HOL n2 +4.66 (diff t -0.52) | -2.71 / +5.52; +0.07 / -4.03 | 0.99 / 0.20 | 0.99 / 0.17 | fail |
| CNHK-AM XAUUSD V2 w15 k2 h60 none | 223 / 130 | +3.46 (+3.42) / -0.35 (-0.24) | +1.85 / **+1.84 (+1.83)** / +1.85 / +1.83 / +1.82 | -1.47 / **-1.45 (-1.02)** / -1.39 / -1.44 / -1.55 | +1.33 / -1.71 | -0.79 | 5/9 | +0.98 / -0.77 | +0.98 / -0.77 | HOL n7 -3.00 (diff t +0.68) | -3.08 / -2.32; +0.17 / -1.10 | 1.00 / 0.43 | 1.00 / 0.39 | fail |
| SGE-NIGHT ALL V2 w60 k4 h60 S | 53 / 30 | +23.02 (+2.09) / -0.43 (-0.11) | +19.41 / **+19.79 (+1.81)** / +19.48 / +19.01 / +16.67 | -3.02 / **-2.79 (-0.71)** / -2.71 / -2.72 / -4.26 | +18.48 / -3.68 | -0.14 | 3/9 | +1.03 / -0.56 | +0.97 / -0.54 | HOL n4 +8.95 (diff t +0.11) | -5.87 / -2.24; +0.47 / -4.78 | 0.98 / 0.40 | 1.00 / 0.46 | fail |
| SGE-NIGHT XAGUSD V2 w60 k4 h60 S | 26 / 12 | +41.35 (+2.03) / +6.64 (+0.73) | +35.46 / **+36.32 (+1.80)** / +35.52 / +34.72 / +29.87 | +1.82 / **+2.25 (+0.25)** / +2.49 / +2.45 / -3.24 | +34.11 / +0.36 | +0.06 | 5/9 | +0.96 / +0.19 | +0.96 / +0.19 | HOL n2 -10.81 (diff t +0.91) | -10.03 / -0.74; +4.82 / -7.59 | 0.96 / 0.83 | 1.00 / 0.90 | fail |
| CNHK-AM US30 V1 w60 k4 h60 none | 47 / 11 | +18.83 (+1.92) / +5.79 (+0.92) | +17.25 / **+17.20 (+1.76)** / +16.92 / +17.10 / +17.77 | +5.25 / **+5.33 (+0.84)** / +5.26 / +5.29 / +4.44 | +16.39 / +5.10 | +0.31 | 6/9 | +0.94 / +0.64 | +0.94 / +0.64 | HOL n1 +2.38 (diff t -) | +2.02 / -2.06; -2.70 / -2.90 | 0.97 / 0.83 | 1.00 / 0.76 | fail |
| SGE-NIGHT XAGUSD V1 w15 k4 h15 none | 47 / 18 | +16.46 (+2.43) / -1.72 (-0.43) | +11.65 / **+11.57 (+1.72)** / +11.16 / +11.39 / +6.68 | -6.38 / **-6.28 (-1.51)** / -6.24 / -6.52 / -3.57 | +9.42 / -8.26 | -0.54 | 6/9 | +0.92 / -1.15 | +0.92 / -1.15 | HOL n7 -9.10 (diff t +1.64) | +1.19 / -8.21; +4.45 / -4.98 | 0.99 / 0.33 | 1.00 / 0.37 | fail |
| SGE-NIGHT ALL V2 w60 k4 h60 none | 53 / 30 | +22.48 (+1.97) / -4.89 (-0.65) | +18.99 / **+19.31 (+1.70)** / +19.37 / +19.38 / +16.37 | -7.34 / **-7.22 (-0.97)** / -7.30 / -7.39 / -9.86 | +18.02 / -8.08 | -0.37 | 3/9 | +0.96 / -0.89 | +0.91 / -0.71 | HOL n4 +23.96 (diff t -0.86) | -8.72 / -13.80; +0.65 / +5.57 | 0.98 / 0.23 | 1.00 / 0.34 | fail |
| TSE-OPEN ALL V1 w60 k4 h60 none | 190 / 108 | +4.78 (+2.75) / -4.55 (-1.75) | +2.86 / **+2.83 (+1.63)** / +2.83 / +2.96 / +1.54 | -5.64 / **-5.54 (-2.12)** / -5.71 / -5.50 / -6.24 | +2.00 / -5.84 | -1.96 | 4/9 | +1.08 / -1.89 | +0.88 / -1.62 | HOL n11 -7.63 (diff t +1.70) | -2.69 / -1.03; -0.81 / -1.81 | 1.00 / 0.03 | 1.00 / 0.01 | fail |
| TSE-OPEN XAUUSD V1 w60 k4 h60 S | 43 / 30 | +6.04 (+2.44) / -2.34 (-1.26) | +3.87 / **+3.85 (+1.59)** / +3.82 / +4.12 / +2.33 | -5.13 / **-3.56 (-1.90)** / -3.31 / -3.58 / -3.09 | +3.06 / -3.87 | -0.92 | 4/9 | +0.85 / -1.45 | +0.85 / -1.45 | HOL n2 +2.64 (diff t -0.20) | -2.47 / +0.02; +0.48 / -5.40 | 1.00 / 0.07 | 1.00 / 0.01 | fail |
| SGE-NIGHT XAGUSD V2 w60 k4 h60 none | 26 / 12 | +37.59 (+1.76) / -0.36 (-0.03) | +32.00 / **+32.66 (+1.54)** / +32.65 / +32.70 / +25.12 | -5.05 / **-4.71 (-0.37)** / -4.80 / -5.31 / -10.16 | +30.50 / -6.58 | -0.14 | 4/9 | +0.83 / -0.28 | +0.83 / -0.28 | HOL n2 +15.06 (diff t +0.30) | -21.05 / -27.84; +7.22 / +1.45 | 0.95 / 0.47 | 1.00 / 0.47 | fail |

### By year, best cell per clock and family (net bp at the decision latency, n)
| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | years > 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN AUDUSD V1 w60 k2 h60 none | +1.0 (13) | +1.5 (23) | +0.1 (23) | -0.6 (20) | +4.2 (30) | +2.0 (20) | -3.3 (32) | -0.6 (26) | -0.9 (22) | 5/9 |
| ASX-OPEN US30 V2 w15 k2 h15 none | -2.3 (12) | -2.9 (12) | +0.3 (31) | -0.7 (34) | +5.2 (39) | +1.8 (23) | -1.0 (36) | +0.0 (17) | -1.0 (24) | 4/9 |
| TSE-OPEN XAUUSD V1 w60 k4 h60 none | +2.8 (9) | +7.7 (4) | -10.6 (4) | +0.7 (5) | +12.4 (15) | +3.3 (6) | -2.1 (6) | -13.0 (12) | +0.8 (12) | 6/9 |
| TSE-OPEN AUDUSD V2 w60 k4 h15 S | -0.0 (3) | +0.4 (3) | -1.3 (7) | -2.1 (2) | +6.0 (13) | -1.2 (2) | -4.7 (10) | -8.6 (4) | -1.3 (7) | 2/9 |
| ASX+TSE US30 V1 w60 k2 h60 none | -1.0 (7) | +1.3 (13) | -1.7 (26) | +0.6 (28) | +10.7 (25) | +5.1 (21) | -1.6 (23) | -1.3 (10) | -4.8 (15) | 4/9 |
| ASX+TSE NZDUSD V2 w60 k4 h15 none | -0.3 (2) | +0.2 (3) | -1.4 (2) | +5.3 (3) | +4.6 (12) | -0.7 (6) | -10.4 (4) | -0.8 (2) | - | 3/8 |
| CNHK-AM US30 V1 w60 k4 h60 none | +11.3 (2) | -3.6 (6) | +19.7 (11) | +21.0 (2) | +30.1 (19) | -3.3 (7) | +7.1 (7) | -6.5 (1) | +5.1 (3) | 6/9 |
| CNHK-AM XAUUSD V2 w15 k2 h60 none | +1.3 (31) | -2.4 (29) | +4.4 (45) | -1.7 (42) | +4.6 (46) | +3.4 (30) | -3.0 (50) | +3.0 (42) | -4.3 (38) | 5/9 |
| CNHK-PM USTEC V1 w60 k4 h60 none | -6.7 (3) | -6.5 (5) | -2.0 (19) | -14.7 (6) | +15.7 (17) | +4.6 (13) | -9.6 (15) | +1.6 (7) | +5.2 (12) | 4/9 |
| CNHK-PM US30 V2 w15 k4 h15 S | - | - | -2.6 (15) | +1.1 (10) | +8.4 (25) | -0.5 (7) | -1.5 (12) | -0.3 (3) | -1.7 (7) | 2/7 |
| SGE-NIGHT XAGUSD V1 w15 k4 h15 none | +49.8 (3) | +10.4 (7) | -21.1 (2) | +3.2 (8) | +15.2 (22) | +0.9 (5) | +1.6 (4) | -10.6 (11) | -1.0 (3) | 6/9 |
| SGE-NIGHT ALL V2 w60 k4 h60 S | -6.1 (13) | -8.3 (4) | +5.5 (6) | -1.3 (8) | +87.1 (14) | -10.1 (8) | +1.6 (11) | -2.2 (8) | -7.6 (11) | 3/9 |
| TSE-PM US30 V1 w15 k4 h60 none | -5.3 (5) | - | +2.1 (11) | -14.8 (5) | +6.2 (21) | -3.5 (8) | +2.0 (13) | +1.2 (4) | +0.4 (5) | 5/8 |
| TSE-PM US30 V2 w60 k4 h60 none | +0.9 (3) | -0.3 (2) | -2.9 (29) | +12.9 (5) | +2.1 (20) | +0.7 (9) | -1.2 (14) | +1.2 (2) | +0.9 (9) | 6/9 |

### Best cells per clock and family: winsorised, without March-April 2020, spread paid, stop hits
| cell | net IS / VAL | winsorised IS / VAL | IS ex Mar-Apr 2020 | spread paid IS / VAL | stop-hit share IS / VAL |
|---|---|---|---|---|---|
| ASX-OPEN AUDUSD V1 w60 k2 h60 none | +1.57 / -1.78 | +1.40 / -1.77 | +1.25 | +0.39 / +0.14 | - / - |
| ASX-OPEN US30 V2 w15 k2 h15 none | +1.11 / -0.77 | +1.21 / -0.77 | +0.40 | +1.48 / +0.43 | - / - |
| TSE-OPEN XAUUSD V1 w60 k4 h60 none | +5.18 / -5.29 | +5.06 / -0.40 | +5.39 | +1.56 / +0.58 | - / - |
| TSE-OPEN AUDUSD V2 w60 k4 h15 S | +2.12 / -4.29 | +1.98 / -4.26 | -1.89 | +0.58 / +0.16 | 0.30 / 0.57 |
| ASX+TSE US30 V1 w60 k2 h60 none | +2.96 / -2.52 | +2.69 / -2.52 | +1.19 | +1.45 / +0.42 | - / - |
| ASX+TSE NZDUSD V2 w60 k4 h15 none | +2.26 / -7.18 | +2.21 / -6.26 | +1.67 | +0.57 / +0.79 | - / - |
| CNHK-AM US30 V1 w60 k4 h60 none | +17.20 / +5.33 | +15.37 / +5.33 | +10.70 | +1.63 / +0.46 | - / - |
| CNHK-AM XAUUSD V2 w15 k2 h60 none | +1.84 / -1.45 | +1.83 / -1.07 | +1.67 | +1.02 / +0.51 | - / - |
| CNHK-PM USTEC V1 w60 k4 h60 none | +2.34 / -2.02 | +2.44 / -2.01 | +0.75 | +3.15 / +1.21 | - / - |
| CNHK-PM US30 V2 w15 k4 h15 S | +3.12 / -1.38 | +2.95 / -1.38 | -1.09 | +1.63 / +0.45 | 0.61 / 0.73 |
| SGE-NIGHT XAGUSD V1 w15 k4 h15 none | +11.57 / -6.28 | +11.53 / -6.28 | +11.57 | +4.30 / +3.96 | - / - |
| SGE-NIGHT ALL V2 w60 k4 h60 S | +19.79 / -2.79 | +20.25 / -2.79 | +19.79 | +2.63 / +1.77 | 0.51 / 0.77 |
| TSE-PM US30 V1 w15 k4 h60 none | +0.51 / +1.48 | +0.22 / +1.48 | -4.40 | +1.66 / +0.46 | - / - |
| TSE-PM US30 V2 w60 k4 h60 none | +0.49 / -0.24 | +0.11 / -0.24 | -0.06 | +1.65 / +0.45 | - / - |

## 3. Does the opening move predict the next minutes at mid?
### The 20 cells with the largest |IS mid t| (V1 orientation: + continues, - reverses)
| cell | n IS / VAL | mid IS (t) | mid VAL (t) | net V1 IS / VAL | net V2 IS / VAL | spread paid IS / VAL |
|---|---|---|---|---|---|---|
| SGE-NIGHT ALL w15 k0 h15 | 2026 / 1086 | +1.69 (+3.76) | +0.10 (+0.22) | -0.96 / -2.66 | -4.34 / -2.86 | +2.05 / +2.16 |
| SGE-NIGHT XAGUSD w15 k0 h15 | 978 / 534 | +2.65 (+3.63) | +0.21 (+0.27) | -1.39 / -4.39 | -6.68 / -4.80 | +3.43 / +4.00 |
| SGE-NIGHT XAGUSD w15 k0 h5 | 1019 / 551 | +1.70 (+3.45) | -0.05 (-0.10) | -2.35 / -4.62 | -5.75 / -4.51 | +3.45 / +3.96 |
| CNHK-AM XAUUSD w15 k2 h60 | 223 / 130 | -3.46 (-3.42) | +0.35 (+0.24) | -5.07 / -0.76 | +1.84 / -1.45 | +1.02 / +0.51 |
| SGE-NIGHT ALL w15 k0 h5 | 2115 / 1119 | +0.92 (+3.20) | -0.14 (-0.46) | -1.74 / -2.89 | -3.58 / -2.60 | +2.06 / +2.15 |
| ASX-OPEN ALL w15 k2 h15 | 850 / 403 | -1.50 (-3.06) | -0.45 (-0.81) | -3.33 / -1.39 | -0.32 / -0.50 | +1.45 / +0.59 |
| ASX+TSE NZDUSD w60 k0 h5 | 556 / 279 | +0.56 (+2.91) | -0.12 (-0.47) | -0.65 / -1.42 | -1.77 / -1.18 | +0.61 / +0.70 |
| TSE-OPEN XAUUSD w60 k4 h60 | 43 / 30 | +7.34 (+2.80) | -4.11 (-0.80) | +5.18 / -5.29 | -9.49 / +2.93 | +1.56 / +0.58 |
| TSE-OPEN ALL w60 k4 h60 | 190 / 108 | +4.78 (+2.75) | -4.55 (-1.75) | +2.83 / -5.54 | -6.74 / +3.56 | +1.65 / +0.61 |
| TSE-OPEN AUDUSD w15 k4 h5 | 74 / 22 | -1.11 (-2.66) | +1.86 (+1.61) | -2.18 / +1.11 | +0.04 / -2.61 | +0.47 / +0.15 |
| ASX-OPEN INDICES w15 k2 h15 | 327 / 168 | -2.40 (-2.64) | -1.00 (-1.05) | -4.86 / -1.77 | -0.06 / +0.23 | +2.46 / +0.77 |
| TSE-OPEN ALL w60 k2 h60 | 864 / 508 | +1.90 (+2.60) | -1.96 (-2.00) | +0.14 / -2.93 | -3.67 / +1.00 | +1.42 / +0.59 |
| ASX-OPEN USTEC w15 k2 h15 | 176 / 91 | -2.24 (-2.60) | -2.13 (-1.59) | -5.54 / -3.19 | -1.06 / +1.07 | +3.30 / +1.06 |
| SGE-NIGHT XAUUSD w15 k0 h15 | 1048 / 552 | +0.80 (+2.49) | -0.00 (-0.00) | -0.55 / -0.98 | -2.16 / -0.98 | +0.76 / +0.38 |
| TSE-OPEN FX w15 k4 h5 | 128 / 40 | -1.05 (-2.48) | +1.56 (+1.40) | -2.27 / +0.54 | -0.17 / -2.57 | +0.62 / +0.41 |
| ASX-OPEN US30 w15 k2 h15 | 151 / 77 | -2.59 (-2.48) | +0.34 (+0.42) | -4.07 / -0.08 | +1.11 / -0.77 | +1.48 / +0.43 |
| TSE-PM (info) USTEC w60 k0 h60 | 1077 / 556 | -1.17 (-2.47) | -0.18 (-0.36) | -4.58 / -1.39 | -2.24 / -1.02 | +3.41 / +1.21 |
| SGE-NIGHT XAGUSD w15 k4 h15 | 47 / 18 | +16.46 (+2.43) | -1.72 (-0.43) | +11.57 / -6.28 | -21.36 / -2.84 | +4.30 / +3.96 |
| TSE-OPEN ALL w60 k0 h60 | 4266 / 2515 | +0.70 (+2.43) | -0.01 (-0.03) | -1.03 / -0.96 | -2.43 / -0.94 | +1.37 / +0.59 |
| TSE-OPEN NZDUSD w60 k0 h5 | 1087 / 573 | +0.31 (+2.42) | -0.03 (-0.15) | -0.96 / -1.33 | -1.58 / -1.27 | +0.67 / +0.70 |

### Mid direction per clock and set (V1 orientation, w 15 s, h 15 min, no stop): IS (t) / VAL (t)
| clock | set | k0 IS / VAL | k2 IS / VAL | k4 IS / VAL | spread paid k2 IS / VAL |
|---|---|---|---|---|---|
| ASX-OPEN | AUDUSD | -0.44 (-1.8) / -0.42 (-1.2) | -0.93 (-1.5) / +0.10 (+0.1) | -1.95 (-1.6) / +4.68 (+2.3) | 0.43 / 0.16 |
| ASX-OPEN | NZDUSD | -0.32 (-1.2) / -0.11 (-0.3) | -0.93 (-1.3) / -0.86 (-0.9) | -2.60 (-1.7) / +1.31 (+0.5) | 0.77 / 0.75 |
| ASX-OPEN | XAUUSD | -0.25 (-0.9) / +0.53 (+1.8) | -0.96 (-1.3) / +0.47 (+0.7) | +0.78 (+0.4) / +0.25 (+0.2) | 1.26 / 0.50 |
| ASX-OPEN | US30 | -0.05 (-0.1) / +0.29 (+0.9) | -2.59 (-2.5) / +0.34 (+0.4) | -3.34 (-1.3) / -1.63 (-0.6) | 1.48 / 0.43 |
| ASX-OPEN | USTEC | -0.49 (-1.4) / +0.38 (+0.8) | -2.24 (-2.6) / -2.13 (-1.6) | -2.32 (-1.1) / -3.06 (-1.1) | 3.30 / 1.06 |
| ASX-OPEN | FX | -0.38 (-1.7) / -0.26 (-0.8) | -0.93 (-1.5) / -0.37 (-0.5) | -2.34 (-2.1) / +3.06 (+1.6) | 0.60 / 0.45 |
| ASX-OPEN | INDICES | -0.27 (-0.8) / +0.34 (+0.9) | -2.40 (-2.6) / -1.00 (-1.1) | -2.80 (-1.3) / -2.49 (-1.0) | 2.46 / 0.77 |
| ASX-OPEN | ALL | -0.31 (-1.8) / +0.13 (+0.7) | -1.50 (-3.1) / -0.45 (-0.8) | -2.00 (-1.8) / -0.12 (-0.1) | 1.45 / 0.59 |
| TSE-OPEN | AUDUSD | -0.21 (-1.0) / -0.36 (-1.2) | -0.58 (-1.2) / -1.11 (-1.3) | -1.90 (-2.0) / -0.00 (-0.0) | 0.40 / 0.13 |
| TSE-OPEN | NZDUSD | -0.17 (-0.8) / -0.03 (-0.1) | -0.05 (-0.1) / -1.25 (-1.6) | -1.90 (-1.8) / -1.69 (-0.7) | 0.67 / 0.71 |
| TSE-OPEN | XAUUSD | -0.02 (-0.1) / -0.05 (-0.2) | -0.58 (-1.0) / -0.46 (-0.8) | +0.86 (+0.5) / -3.72 (-2.3) | 1.13 / 0.53 |
| TSE-OPEN | US30 | -0.15 (-0.5) / +0.17 (+0.6) | -1.96 (-1.9) / +0.17 (+0.2) | -4.43 (-1.5) / -2.08 (-1.2) | 1.50 / 0.42 |
| TSE-OPEN | USTEC | -0.51 (-1.6) / +0.06 (+0.1) | -1.41 (-1.5) / +0.20 (+0.2) | -2.84 (-1.1) / -1.22 (-0.6) | 3.25 / 1.13 |
| TSE-OPEN | FX | -0.19 (-1.0) / -0.20 (-0.7) | -0.32 (-0.8) / -1.18 (-1.8) | -1.90 (-2.2) / -0.76 (-0.4) | 0.53 / 0.44 |
| TSE-OPEN | INDICES | -0.33 (-1.2) / +0.11 (+0.4) | -1.67 (-1.8) / +0.18 (+0.3) | -3.57 (-1.4) / -1.55 (-0.9) | 2.44 / 0.82 |
| TSE-OPEN | ALL | -0.21 (-1.3) / -0.04 (-0.2) | -0.89 (-1.9) / -0.44 (-1.0) | -2.17 (-1.7) / -1.92 (-1.8) | 1.38 / 0.62 |
| ASX+TSE | AUDUSD | -0.45 (-1.4) / -0.67 (-1.5) | -0.59 (-0.8) / -1.00 (-0.8) | -1.54 (-0.9) / +7.66 (+3.5) | 0.34 / 0.14 |
| ASX+TSE | NZDUSD | -0.42 (-1.3) / -0.19 (-0.4) | -0.68 (-0.8) / -1.56 (-1.2) | -1.54 (-0.8) / -10.31 (-2.4) | 0.62 / 0.72 |
| ASX+TSE | XAUUSD | -0.16 (-0.5) / +0.44 (+1.2) | -1.11 (-1.2) / +1.02 (+1.3) | +4.99 (+1.4) / -0.21 (-0.2) | 1.15 / 0.45 |
| ASX+TSE | US30 | -0.16 (-0.4) / +0.08 (+0.2) | -2.26 (-1.9) / +0.08 (+0.1) | -4.10 (-1.3) / -1.76 (-0.6) | 1.51 / 0.41 |
| ASX+TSE | USTEC | -0.41 (-1.1) / +0.10 (+0.2) | -1.89 (-1.8) / -2.59 (-1.6) | -1.05 (-0.4) / -4.68 (-1.3) | 3.23 / 1.07 |
| ASX+TSE | FX | -0.43 (-1.6) / -0.43 (-1.1) | -0.63 (-0.9) / -1.28 (-1.2) | -1.54 (-0.9) / +0.47 (+0.1) | 0.48 / 0.43 |
| ASX+TSE | INDICES | -0.29 (-0.8) / +0.09 (+0.2) | -2.07 (-1.9) / -1.44 (-1.2) | -2.43 (-0.9) / -3.60 (-1.3) | 2.40 / 0.79 |
| ASX+TSE | ALL | -0.32 (-1.5) / -0.05 (-0.2) | -1.30 (-2.0) / -0.83 (-1.2) | -1.22 (-0.7) / -2.36 (-1.2) | 1.38 / 0.61 |
| CNHK-AM | AUDUSD | -0.18 (-0.7) / -0.00 (-0.0) | +0.42 (+0.6) / -0.20 (-0.2) | -0.22 (-0.1) / -4.84 (-2.5) | 0.40 / 0.13 |
| CNHK-AM | XAUUSD | -0.11 (-0.4) / -0.36 (-0.9) | -1.02 (-1.5) / -0.19 (-0.2) | -0.68 (-0.4) / +2.34 (+1.1) | 1.01 / 0.49 |
| CNHK-AM | US30 | +0.09 (+0.3) / -0.09 (-0.3) | +0.18 (+0.2) / +0.48 (+0.7) | -1.57 (-0.5) / +3.35 (+1.0) | 1.44 / 0.43 |
| CNHK-AM | USTEC | -0.11 (-0.3) / -0.14 (-0.3) | +0.34 (+0.3) / +0.45 (+0.4) | +1.89 (+0.6) / +3.18 (+1.0) | 3.24 / 1.19 |
| CNHK-AM | INDICES | -0.01 (-0.0) / -0.12 (-0.4) | +0.26 (+0.2) / +0.46 (+0.6) | +0.22 (+0.1) / +3.24 (+1.0) | 2.33 / 0.87 |
| CNHK-AM | ALL | -0.08 (-0.4) / -0.16 (-0.6) | -0.07 (-0.1) / +0.12 (+0.2) | -0.09 (-0.0) / +1.32 (+0.7) | 1.52 / 0.60 |
| CNHK-PM | AUDUSD | +0.09 (+0.6) / +0.29 (+1.3) | +0.35 (+0.9) / +0.14 (+0.2) | -0.45 (-0.5) / -0.52 (-0.2) | 0.34 / 0.12 |
| CNHK-PM | XAUUSD | -0.03 (-0.2) / +0.13 (+0.6) | -0.13 (-0.3) / -0.01 (-0.0) | -0.41 (-0.3) / -2.26 (-1.3) | 1.10 / 0.46 |
| CNHK-PM | US30 | -0.21 (-0.7) / +0.07 (+0.4) | -0.40 (-0.3) / +0.70 (+1.0) | -4.37 (-1.2) / +2.00 (+1.4) | 1.41 / 0.42 |
| CNHK-PM | USTEC | -0.35 (-1.2) / +0.22 (+0.8) | -0.71 (-0.7) / +1.28 (+1.4) | -3.02 (-1.1) / +1.27 (+0.6) | 2.89 / 1.26 |
| CNHK-PM | INDICES | -0.28 (-1.0) / +0.15 (+0.7) | -0.56 (-0.5) / +1.03 (+1.4) | -3.62 (-1.2) / +1.57 (+0.9) | 2.19 / 0.89 |
| CNHK-PM | ALL | -0.12 (-0.8) / +0.18 (+1.2) | -0.19 (-0.3) / +0.54 (+1.1) | -1.94 (-1.2) / +0.23 (+0.2) | 1.37 / 0.59 |
| SGE-NIGHT | XAUUSD | +0.80 (+2.5) / -0.00 (-0.0) | +0.37 (+0.5) / +0.18 (+0.2) | -0.36 (-0.2) / +1.27 (+0.7) | 0.80 / 0.40 |
| SGE-NIGHT | XAGUSD | +2.65 (+3.6) / +0.21 (+0.3) | +4.75 (+2.1) / -1.28 (-0.7) | +16.46 (+2.4) / -1.72 (-0.4) | 3.42 / 3.91 |
| SGE-NIGHT | ALL | +1.69 (+3.8) / +0.10 (+0.2) | +2.43 (+1.9) / -0.58 (-0.6) | +8.63 (+2.1) / +0.13 (+0.1) | 2.03 / 2.21 |
| TSE-PM (info) | AUDUSD | +0.08 (+0.5) / +0.38 (+1.7) | +0.05 (+0.2) / +0.21 (+0.5) | +0.74 (+1.4) / -0.76 (-0.8) | 0.36 / 0.10 |
| TSE-PM (info) | NZDUSD | +0.24 (+1.7) / +0.11 (+0.5) | +0.41 (+1.5) / +0.22 (+0.5) | -0.00 (-0.0) / -1.05 (-1.0) | 0.60 / 0.61 |
| TSE-PM (info) | XAUUSD | +0.09 (+0.6) / +0.42 (+1.9) | +0.29 (+0.8) / -0.13 (-0.2) | +1.35 (+1.4) / -0.50 (-0.4) | 1.06 / 0.46 |
| TSE-PM (info) | US30 | +0.05 (+0.3) / +0.20 (+0.8) | +0.36 (+0.6) / +0.34 (+0.4) | -0.26 (-0.2) / +1.98 (+0.8) | 1.48 / 0.42 |
| TSE-PM (info) | USTEC | -0.26 (-0.8) / +0.34 (+1.1) | +0.53 (+0.8) / -0.29 (-0.4) | +0.32 (+0.2) / +1.94 (+1.3) | 3.04 / 1.19 |
| TSE-PM (info) | FX | +0.16 (+1.4) / +0.25 (+1.2) | +0.25 (+1.1) / +0.21 (+0.6) | +0.26 (+0.7) / -0.92 (-1.1) | 0.49 / 0.37 |
| TSE-PM (info) | INDICES | -0.11 (-0.5) / +0.28 (+1.2) | +0.45 (+0.8) / -0.01 (-0.0) | +0.02 (+0.0) / +1.95 (+1.1) | 2.27 / 0.84 |
| TSE-PM (info) | ALL | +0.04 (+0.4) / +0.29 (+2.2) | +0.32 (+1.3) / +0.06 (+0.2) | +0.39 (+0.7) / +0.44 (+0.5) | 1.20 / 0.57 |

Reading:
- **ASX-OPEN, TSE-OPEN, ASX+TSE.** The opening move tends to reverse at k 2-4 in both eras (ALL k 2: -1.50 / -0.45,
  -0.89 / -0.44, -1.30 / -0.83 bp), weaker in VAL. The US index CFDs reverse most (ASX-OPEN INDICES k 2: -2.40 /
  -1.00) and pay 2.5 / 0.8 bp of spread for it.
- **TSE-OPEN, w 60 s, k 4, h 60.** Gold and the pool continue in IS (+7.34 / +4.78 bp, t 2.8) and reverse in VAL
  (-4.11 / -4.55).
- **CNHK-AM / CNHK-PM.** Nothing at w 15 s. The w 60 s k 4 h 60 follow in the US indices is positive in both eras
  (CNHK-AM INDICES mid +16.6 / +6.5 bp), on about 13 events a year for the two indices together.
- **SGE-NIGHT.** Continuation at k 0 in IS (gold +0.80, silver +2.65 bp) is gone in VAL (-0.00, +0.21).

None survives IC's spread at its own minute.

## 4. Families: cells tried, best cell, chance
| clock | family | cells | IS net > 0 | IS and VAL net > 0 | IS net t >= 2 | of which VAL net > 0 | best IS net t | V1 no-stop cells with IS mid t >= 2 / <= -2 | of those, VAL mid same sign t >= 1.5 | DEMO numbers | LIVE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN | V1 | 288 | 10 | 2 | 0 | 0 | +1.40 (AUDUSD w60 k2 h60 none) | 2 / 13 | 0 / 1 | 0 | 0 |
| ASX-OPEN | V2 | 288 | 37 | 6 | 0 | 0 | +1.06 (US30 w15 k2 h15 none) | - / - | - / - | 0 | 0 |
| TSE-OPEN | V1 | 288 | 25 | 0 | 1 | 0 | +2.01 (XAUUSD w60 k4 h60 none) | 9 / 4 | 0 / 0 | 0 | 0 |
| TSE-OPEN | V2 | 288 | 19 | 8 | 0 | 0 | +0.98 (AUDUSD w60 k4 h15 S) | - / - | - / - | 0 | 0 |
| ASX+TSE | V1 | 288 | 31 | 2 | 0 | 0 | +1.49 (US30 w60 k2 h60 none) | 9 / 2 | 0 / 0 | 0 | 0 |
| ASX+TSE | V2 | 288 | 22 | 9 | 0 | 0 | +1.31 (NZDUSD w60 k4 h15 none) | - / - | - / - | 0 | 0 |
| CNHK-AM | V1 | 216 | 12 | 8 | 0 | 0 | +1.76 (US30 w60 k4 h60 none) | 2 / 3 | 0 / 0 | 0 | 0 |
| CNHK-AM | V2 | 216 | 26 | 2 | 0 | 0 | +1.83 (XAUUSD w15 k2 h60 none) | - / - | - / - | 0 | 0 |
| CNHK-PM | V1 | 216 | 14 | 1 | 0 | 0 | +0.65 (USTEC w60 k4 h60 none) | 0 / 0 | 0 / 0 | 0 | 0 |
| CNHK-PM | V2 | 216 | 22 | 7 | 0 | 0 | +1.07 (US30 w15 k4 h15 S) | - / - | - / - | 0 | 0 |
| SGE-NIGHT | V1 | 108 | 20 | 0 | 0 | 0 | +1.72 (XAGUSD w15 k4 h15 none) | 10 / 0 | 0 / 0 | 0 | 0 |
| SGE-NIGHT | V2 | 108 | 23 | 11 | 0 | 0 | +1.81 (ALL w60 k4 h60 S) | - / - | - / - | 0 | 0 |
| TSE-PM (info) | V1 | 288 | 2 | 1 | 0 | 0 | +0.15 (US30 w15 k4 h60 none) | 1 / 1 | 0 / 0 | 0 | 0 |
| TSE-PM (info) | V2 | 288 | 1 | 0 | 0 | 0 | +0.14 (US30 w60 k4 h60 none) | - / - | - / - | 0 | 0 |

| benchmark | all counted cells (K = 2808) | 24 primary cells |
|---|---|---|
| 95 % max \|t\| of K independent normals | 4.29 | 3.07 |
| sign-flip null, max IS net t: p50 / p95 | 2.12 / 3.07 | 0.49 / 1.36 |
| observed max IS net t (share of null draws >= it) | 2.01 (0.630) | 1.33 (0.060) |
| sign-flip null, max \|IS mid t\| (no-stop cells): p50 / p95 | 3.11 / 3.89 | 1.77 / 2.73 |
| observed max \|IS mid t\| (share of null draws >= it) | 3.76 (0.084) | 3.06 (0.021) |

Reading of the chance benchmark:
- **Net.** For K = 2,808 independent normals the 95 % max |t| is 4.29, and 3.07 for the 24 primary cells. The
  per-UTC-day sign-flip null (one flip per day shared by every instrument, clock and cell; 1,000 draws) gives a max
  IS net t of p50 2.12 / p95 3.07; the observed 2.01 has p 0.63. For the primary cells the null is p50 0.49 / p95
  1.36; the observed 1.33 has p 0.06.
- **Mid.** The max |IS mid t| over the no-stop cells is 3.76 against a null p95 of 3.89 (p 0.084). For the primary
  cells it is 3.06 against 2.73 (p 0.021): the reversal at ASX-OPEN, mostly in IS.

## 5. Declared information-only splits
| split | k | V1 IS | V1 VAL | V2 IS | V2 VAL | V1 mid IS / VAL |
|---|---|---|---|---|---|---|
| ASX-OPEN ALL, AEDT (23:00 UTC, ASX alone) | 0 | -2.29 (-5.9) n799 | -0.38 (-1.3) n503 | -1.55 (-4.1) | -1.65 (-5.3) | -0.37 / +0.63 |
| ASX-OPEN ALL, AEST (00:00 UTC) | 0 | -2.03 (-10.0) n2900 | -0.95 (-3.7) n1449 | -1.43 (-7.0) | -0.88 (-3.5) | -0.30 / -0.04 |
| ASX-OPEN ALL, AEDT (23:00 UTC, ASX alone) | 2 | -5.26 (-3.8) n140 | -0.07 (-0.1) n90 | +0.89 (+0.7) | -2.06 (-3.1) | -3.08 / +0.99 |
| ASX-OPEN ALL, AEST (00:00 UTC) | 2 | -2.94 (-5.6) n710 | -1.77 (-2.6) n313 | -0.56 (-1.1) | -0.05 (-0.1) | -1.19 / -0.86 |
| ASX-OPEN ALL, AEDT (23:00 UTC, ASX alone) | 4 | -7.57 (-2.4) n51 | -1.51 (-1.6) n29 | +2.75 (+0.8) | -0.60 (-0.6) | -5.16 / -0.46 |
| ASX-OPEN ALL, AEST (00:00 UTC) | 4 | -2.99 (-2.6) n187 | -0.84 (-0.4) n63 | -0.70 (-0.6) | -0.92 (-0.5) | -1.14 / +0.04 |
| ASX-OPEN ALL, AEDT Monday opens (Sunday 23:00 UTC) | 0 | -3.64 (-3.5) n153 | -0.13 (-0.2) n101 | -0.29 (-0.4) | -2.05 (-2.7) | -1.68 / +0.96 |
| ASX-OPEN ALL, AEDT other days | 0 | -1.97 (-4.8) n646 | -0.45 (-1.3) n402 | -1.85 (-4.3) | -1.55 (-4.5) | -0.06 / +0.55 |
| ASX-OPEN ALL, AEDT Monday opens (Sunday 23:00 UTC) | 2 | -7.21 (-2.9) n34 | +0.19 (+0.1) n28 | +1.40 (+1.0) | -2.42 (-1.7) | -4.30 / +1.31 |
| ASX-OPEN ALL, AEDT other days | 2 | -4.64 (-2.8) n106 | -0.18 (-0.2) n62 | +0.73 (+0.5) | -1.89 (-2.5) | -2.68 / +0.85 |
| TSE-OPEN ALL, AEDT (TSE alone, an hour after ASX) | 0 | -1.90 (-7.9) n2525 | -0.99 (-3.7) n1383 | -1.57 (-6.7) | -0.94 (-3.5) | -0.16 / -0.02 |
| TSE-OPEN ALL, AEST | 0 | -1.99 (-9.5) n2751 | -0.99 (-3.8) n1394 | -1.48 (-7.0) | -0.86 (-3.4) | -0.25 / -0.06 |
| TSE-OPEN ALL, AEDT (TSE alone, an hour after ASX) | 2 | -2.56 (-3.6) n640 | -1.29 (-2.1) n297 | -0.86 (-1.2) | -0.76 (-1.2) | -0.85 / -0.27 |
| TSE-OPEN ALL, AEST | 2 | -2.73 (-4.5) n592 | -1.52 (-2.5) n303 | -0.86 (-1.4) | -0.30 (-0.5) | -0.94 / -0.61 |
| TSE-OPEN ALL, AEDT (TSE alone, an hour after ASX) | 4 | -4.48 (-2.3) n192 | -5.18 (-4.3) n65 | +0.76 (+0.4) | +3.08 (+2.7) | -2.62 / -4.13 |
| TSE-OPEN ALL, AEST | 4 | -3.36 (-2.4) n116 | +0.13 (+0.1) n50 | -0.51 (-0.4) | -1.78 (-1.0) | -1.42 / +0.96 |
| TSE-OPEN ALL placebo (TSE holiday), KRX open | 0 | -2.55 (-3.4) n157 | -0.40 (-0.5) n90 | -1.26 (-1.6) | -1.46 (-1.8) | -0.64 / +0.53 |
| TSE-OPEN ALL placebo (TSE holiday), KRX shut | 0 | -1.07 (-1.2) n30 | +0.58 (+0.3) n20 | -1.93 (-2.2) | -2.58 (-1.3) | +0.43 / +1.58 |
| TSE-OPEN ALL placebo (TSE holiday), KRX open | 2 | -0.66 (-0.3) n46 | -1.12 (-0.7) n17 | -3.32 (-1.6) | -0.76 (-0.5) | +1.33 / -0.18 |
| TSE-OPEN ALL placebo (TSE holiday), KRX shut | 2 | +2.54 (-) n1 | +7.32 (+1.0) n2 | -5.12 (-) | -9.23 (-1.1) | +3.83 / +8.28 |
| CNHK-AM ALL, SSE and HKEX open | 0 | -1.96 (-9.6) n3790 | -1.07 (-3.9) n1899 | -1.80 (-9.0) | -0.65 (-2.4) | -0.08 / -0.21 |
| CNHK-AM ALL, SSE only (HKEX holiday) | 0 | -0.35 (-0.2) n75 | -0.10 (-0.1) n51 | -3.06 (-1.9) | -1.59 (-2.2) | +1.35 / +0.75 |
| CNHK-AM ALL, HKEX only (Chinese holiday) | 0 | -2.51 (-3.8) n190 | -0.52 (-0.5) n112 | -1.41 (-2.0) | -1.19 (-1.2) | -0.55 / +0.33 |
| CNHK-AM ALL, SSE and HKEX open | 2 | -1.78 (-2.6) n786 | -0.85 (-1.5) n389 | -1.89 (-2.9) | -0.98 (-1.7) | +0.06 / +0.07 |
| CNHK-AM ALL, SSE only (HKEX holiday) | 2 | -4.61 (-1.6) n13 | +0.01 (+0.0) n9 | +1.11 (+0.4) | -2.13 (-2.7) | -2.86 / +1.07 |
| CNHK-AM ALL, HKEX only (Chinese holiday) | 2 | -3.23 (-1.7) n39 | -0.35 (-0.2) n27 | +0.01 (+0.0) | -1.32 (-0.6) | -1.62 / +0.49 |
| CNHK-PM ALL, SSE and HKEX open | 0 | -1.89 (-12.0) n4158 | -0.66 (-4.1) n2138 | -1.68 (-10.9) | -1.04 (-6.4) | -0.10 / +0.19 |
| CNHK-PM ALL, SSE only (HKEX holiday) | 0 | -2.12 (-3.8) n74 | -1.05 (-2.1) n50 | -1.85 (-2.6) | -0.64 (-1.2) | -0.14 / -0.20 |
| CNHK-PM ALL, HKEX only (Chinese holiday) | 0 | -2.39 (-3.7) n156 | -0.72 (-1.5) n94 | -1.37 (-2.2) | -0.95 (-1.9) | -0.51 / +0.11 |
| CNHK-PM ALL, SSE and HKEX open | 2 | -1.76 (-3.1) n922 | -0.34 (-0.7) n435 | -1.63 (-2.9) | -1.44 (-2.9) | -0.07 / +0.55 |
| CNHK-PM ALL, SSE only (HKEX holiday) | 2 | -1.61 (-1.0) n10 | -2.13 (-2.0) n9 | -3.85 (-1.3) | +0.46 (+0.4) | +1.12 / -1.29 |
| CNHK-PM ALL, HKEX only (Chinese holiday) | 2 | -5.11 (-4.9) n39 | +0.40 (+0.4) n12 | +1.60 (+1.9) | -2.51 (-2.4) | -3.35 / +1.46 |
| CNHK-AM ALL, first SSE trading day after a Chinese holiday | 0 | -1.10 (-1.1) n90 | -0.82 (-0.8) n66 | -3.26 (-2.8) | -0.89 (-0.9) | +1.08 / +0.03 |
| CNHK-AM ALL, other days | 0 | -1.97 (-10.0) n3965 | -1.02 (-3.9) n1996 | -1.77 (-9.1) | -0.70 (-2.6) | -0.10 / -0.16 |
| CNHK-AM ALL, first SSE trading day after a Chinese holiday | 2 | +2.13 (+1.1) n17 | -0.44 (-0.2) n16 | -6.57 (-3.7) | -1.40 (-0.6) | +4.35 / +0.48 |
| CNHK-AM ALL, other days | 2 | -1.97 (-3.0) n821 | -0.81 (-1.5) n409 | -1.66 (-2.6) | -1.02 (-1.9) | -0.16 / +0.10 |
| SGE-NIGHT ALL on the 2020 SUSP days (SGE status unverified) | 0 | -2.07 (-0.7) n99 | - (-) n0 | -6.51 (-1.9) | - (-) | +2.22 / - |
| SGE-NIGHT ALL on the 2020 SUSP days (SGE status unverified) | 2 | -1.80 (-0.4) n50 | - (-) n0 | -8.78 (-1.7) | - (-) | +3.49 / - |
| SGE-NIGHT ALL, NY summer (12:00 UTC = 08:00 EDT) | 0 | -0.41 (-0.7) n1301 | -2.78 (-4.3) n694 | -4.77 (-8.0) | -2.57 (-4.0) | +2.18 / -0.10 |
| SGE-NIGHT ALL, NY winter (12:00 UTC = 07:00 EST) | 0 | -1.94 (-2.9) n725 | -2.45 (-3.9) n392 | -3.57 (-5.4) | -3.37 (-5.6) | +0.82 / +0.46 |
| SGE-NIGHT ALL, NY summer (12:00 UTC = 08:00 EDT) | 2 | +0.22 (+0.1) n304 | -3.90 (-3.1) n167 | -5.33 (-3.4) | -1.43 (-1.2) | +2.77 / -1.24 |
| SGE-NIGHT ALL, NY winter (12:00 UTC = 07:00 EST) | 2 | -1.36 (-0.7) n110 | -2.12 (-1.2) n67 | -4.30 (-2.0) | -4.27 (-2.5) | +1.47 / +1.07 |
| SGE-NIGHT ALL, NY summer (12:00 UTC = 08:00 EDT) | 4 | +6.52 (+1.4) n71 | -3.19 (-1.3) n29 | -13.08 (-2.8) | -1.73 (-0.7) | +9.80 / -0.73 |
| SGE-NIGHT ALL, NY winter (12:00 UTC = 07:00 EST) | 4 | +0.37 (+0.1) n17 | -0.79 (-0.2) n18 | -7.05 (-1.0) | -3.80 (-1.2) | +3.71 / +1.51 |

### Primary-spec legs by the sign of the opening move
Up-move events: V1 is long, V2 short; down-move events: V1 short, V2 long. A fixed drift after the clock shows as V1 mid of opposite sign on the two legs.

| clock / set | k | up-move V1 mid IS | up-move V1 mid VAL | down-move V1 mid IS | down-move V1 mid VAL |
|---|---|---|---|---|---|
| ASX-OPEN ALL | 0 | -0.04 (-0.2) n1949 | +0.33 (+0.9) n1039 | -0.61 (-2.3) n1750 | -0.09 (-0.3) n913 |
| ASX-OPEN ALL | 2 | -1.67 (-2.1) n456 | -0.02 (-0.0) n230 | -1.31 (-2.2) n394 | -1.01 (-1.2) n173 |
| ASX-OPEN ALL | 4 | -3.12 (-1.8) n133 | +1.43 (+1.0) n48 | -0.59 (-0.5) n105 | -1.81 (-0.8) n44 |
| TSE-OPEN ALL | 0 | -0.22 (-0.8) n2621 | -0.55 (-1.9) n1437 | -0.20 (-0.9) n2655 | +0.50 (+1.6) n1340 |
| TSE-OPEN ALL | 2 | -1.11 (-1.4) n611 | -1.06 (-1.9) n305 | -0.67 (-1.5) n621 | +0.20 (+0.3) n295 |
| TSE-OPEN ALL | 4 | -2.68 (-1.2) n162 | -2.15 (-1.4) n59 | -1.61 (-1.4) n146 | -1.68 (-1.1) n56 |
| ASX+TSE ALL | 0 | -0.19 (-0.5) n1384 | -0.17 (-0.4) n718 | -0.46 (-1.6) n1306 | +0.10 (+0.2) n642 |
| ASX+TSE ALL | 2 | -1.62 (-1.6) n315 | -0.70 (-0.7) n154 | -0.92 (-1.3) n261 | -0.97 (-0.9) n138 |
| ASX+TSE ALL | 4 | -2.06 (-0.8) n86 | -1.92 (-0.6) n27 | -0.01 (-0.0) n60 | -2.67 (-1.1) n39 |
| ASX-OPEN FX | 0 | +0.18 (+0.5) n858 | +0.44 (+1.0) n450 | -1.13 (-3.5) n650 | -1.18 (-2.7) n340 |
| ASX-OPEN FX | 2 | -0.49 (-0.6) n215 | +0.63 (+0.6) n102 | -1.66 (-2.0) n130 | -2.69 (-2.5) n44 |
| ASX-OPEN FX | 4 | -2.84 (-1.7) n54 | +4.27 (+1.8) n19 | -1.63 (-1.3) n38 | +0.17 (+0.1) n8 |
| CNHK-AM ALL | 0 | -0.11 (-0.3) n1999 | +0.28 (+0.7) n1038 | -0.05 (-0.2) n2056 | -0.59 (-1.5) n1024 |
| CNHK-AM ALL | 2 | +0.11 (+0.1) n402 | +0.86 (+1.4) n213 | -0.23 (-0.3) n436 | -0.63 (-0.7) n212 |
| CNHK-AM ALL | 4 | -0.20 (-0.1) n109 | +0.29 (+0.2) n42 | +0.04 (+0.0) n106 | +2.30 (+0.7) n44 |
| CNHK-PM ALL | 0 | -0.28 (-1.4) n2272 | +0.18 (+0.6) n979 | +0.05 (+0.2) n2116 | +0.18 (+0.9) n1303 |
| CNHK-PM ALL | 2 | -0.35 (-0.6) n512 | +1.01 (+1.2) n184 | -0.00 (-0.0) n459 | +0.21 (+0.4) n272 |
| CNHK-PM ALL | 4 | -1.89 (-1.0) n142 | -1.32 (-0.6) n39 | -2.00 (-0.8) n128 | +1.35 (+0.9) n54 |
| SGE-NIGHT ALL | 0 | +1.77 (+2.9) n1104 | +0.93 (+1.4) n562 | +1.60 (+2.3) n922 | -0.79 (-1.1) n524 |
| SGE-NIGHT ALL | 2 | +3.85 (+2.1) n228 | +1.01 (+0.7) n119 | +0.68 (+0.4) n186 | -2.22 (-1.5) n115 |
| SGE-NIGHT ALL | 4 | +14.37 (+2.7) n50 | +2.93 (+1.0) n22 | +1.07 (+0.2) n38 | -2.34 (-0.9) n25 |

Reading:
- **ASX-OPEN by season.** Under AEDT (23:00 UTC, only October and late March survive the rollover rule) k 2 reverses
  in IS (-3.08 bp mid) and continues in VAL (+0.99); under AEST (00:00 UTC) it reverses in both (-1.19 / -0.86).
  Monday opens under AEDT (Sunday 23:00 UTC) show the same pattern (k 2 mid -4.30 / +1.31 against -2.68 / +0.85 on
  the other days).
- **TSE alone (AEDT, an hour after ASX).** k 4 reverses in both eras (V1 mid -2.62 / -4.13 bp); the fade nets +0.76
  (t 0.4) IS and +3.08 (t 2.7) VAL on 192 / 65 events. Post hoc, VAL-driven, IS t far from 2.
- **TSE-holiday placebo by KRX.** With KRX open (157 IS events) both families lose (-2.55 / -1.26 bp at k 0); with KRX
  shut there are too few events to read.
- **CNHK by venue status.** No split carries a sign in both eras. On the first SSE day after a Chinese holiday k 2
  continues in IS (+4.35 bp mid, 17 events) and not in VAL (+0.48, 16).
- **SGE-NIGHT.**
  - The 2020 window (SGE status unverified): k 0 V1 mid +2.22 bp on 99 events, net negative.
  - By New York season: the IS continuation sits in summer (k 0 +2.18 bp, 12:00 UTC = 08:00 EDT) and is -0.10 in VAL.
- **Legs by the move's sign.**
  - FX at ASX-OPEN shows the Sydney V's fixed rise: down-move legs reverse in both eras, up-move legs drift up.
  - SGE-NIGHT k 4 up-moves continue in IS (+14.4 bp, t 2.7) and less in VAL (+2.9, t 1.0); down-moves do not.

## 6. C3 correlation
Not computed: no rule meets the DEMO or LIVE numbers (the brief asks for it only then).
research/results/portfolio/trades_C3_gotobi_jpy_basket.csv exists and was not opened.

## Needs the user
- **IC ticks for the venue index CFDs** (AUS200, JP225, HK50; cTrader backtest downloads on the VPS). They would allow
  the same test on each venue's own index at its own open with tick fills. Round 15 tested those opens at minute
  level with fixed sides only. Prior low: the non-home instruments here show 1-2 bp reversals against 1.4-3 bp
  spreads at these minutes, and the index CFDs' spreads at their cash opens are 2-4 bp (round 15).
- **SGE's 2020 night-session notice**, to classify the 67 excluded days of 2020-02-03..05-05. Negligible value.
- No data purchase or new venue is recommended from this stream.

## Untested ideas
- **The venue index CFDs at minute level** (AUS200 at ASX-OPEN, JP225 at TSE-OPEN, HK50 at CNHK-AM / PM) with this
  rule, from the shared minute panel. It needs no user decision, but it was not in this round's declared set.
- **The KRX open (09:00 KST = 00:00 UTC) as a clock of its own**, with KRX holidays as the placebo. The 00:00 UTC
  spike survives TSE holidays.
- **CNHK-AM follow at w 60 s, k 4, h 60 in the US index CFDs**: net > 0 in both eras (INDICES +14.5 / +5.5 bp, t 1.4 /
  0.9; ALL +4.8 / +6.5, t 1.2 / 1.9). About 13 events a year for the two indices together (US30 ~8), carried in IS
  by 2020. Post hoc; it would need new data, and its expected HOLD t at the VAL size is 0.6-1.7 (US30, the index pair,
  ALL).
- **The TSE-alone reversal at k 4** (V2 net +0.76 IS / +3.08 VAL): post hoc and VAL-driven.
- **A resting limit fade at the 00:00 UTC cluster** (no entry spread). Rounds 12 and 26 found passive fills
  adversely selected. The mid reversal is 1-2 bp at k 2-4 with 0.4-1.1 bp opening moves.
- **SGE-NIGHT's IS-only continuation** could be tied to the SGE premium regime; testing that needs SGE premium data,
  a data decision for the user. Not recommended.

## Scripts and outputs
All under /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r29/O/.
Round 27 V's original code is copied unchanged in `code_v_orig/`.

| script (code/) | what it does |
|---|---|
| cal_o.py | venue calendars from `holidays` 0.106 plus the TSE outage, HKEX half days, SGE night rule -> `cal/venue_calendars_o.json` |
| common_o.py | clocks, day types, exclusions, the HOLD-guarded loader and 3-day window, V's first-crossing search and tick fill simulator (unchanged), `opening_move()` |
| test_sim_o.py | V's synthetic checks plus clocks, day types, `opening_move` == simulator move, the window's HOLD guard (all pass) |
| pass_o.py | per-instrument tick pass; `--counts` = opening moves only -> `out/cnt_<SYM>.npz`; full -> `out/ev_<SYM>.npz`, `out/rt_<SYM>.npz`, `out/prof_<SYM>.npz` |
| count_report_o.py | event counts per clock, instrument and year (no returns) -> `out/counts_o.md` (in HYPOTHESES_O.md) |
| check_events_o.py | independent recomputation of 540 sampled event exits from research/ticks.py -> `out/check_events_o.txt` (0 mismatches) |
| profile_o.py | V0 clock check -> `out/profile_o.txt` |
| analyze_o.py | all cells, controls, sign-flip null, bars -> `out/cells_o.pkl`, `out/cells_o.tsv`, `out/chance_o.txt` |
| report_o.py | tables -> `out/report_o.md` |
| info_o.py | information-only tables and declared splits -> `out/info_o.md` |
| assemble_o.py | builds this file from `code/stream_template_o.md` and the table files |

## Process notes
| UTC | step |
|---|---|
| 00:43-00:57 | briefs, round 27 V's files and code, PROMPT bars read; SGE / HKEX schedule pages and SGE 2020 searches |
| 00:58 | calendars built |
| 00:59-01:03 | O code adapted from V; synthetic tests pass; counts-only pass (opening moves, no returns) and count tables |
| 01:04-01:06 | HYPOTHESES_O.md written (counts appended 01:06) |
| 01:07-01:10 | full tick pass (2 processes, ~3.5 min); counts and full pass define identical events |
| 01:12 | all cells, controls and chance |
| 01:14-01:17 | report, V0, information-only splits, independent recomputation |
| 01:18 | Addendum 1 |
| 01:19-01:21 | one unsigned V0 split added (AUD at 01:30 UTC by Sydney season); this file |

Rules kept:
- At most two heavy processes ran at once. The largest, the analysis, peaked below 1 GB.
- Nothing under research/ was edited. The web requests were schedule lookups (SGE, HKEX, a CLS report of SGE's 2024
  schedule, one news article saved under dl/ and read with `python -I`). They carried no personal data, and no price
  was fetched.
