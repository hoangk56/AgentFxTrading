# Round 28, stream R1: the gold round-level cascade on the major round levels of the IC tick symbols

Written 2026-10-17 22:50 UTC (from `date -u`). Rule, spacings, cells and prices-only event counts were declared in
[HYPOTHESES_R1.md](HYPOTHESES_R1.md) at 22:26 UTC, before any return was computed.

HOLD was never loaded:
- the tick loader asserts every day < 2025-01-01 and every tick < 2025-01-01 00:00 UTC;
- the last NY session used ends 2024-12-31 17:00 New York;
- Dukascopy data is cut at 2016-01-01;
- the C3 file was read for its IS / VAL rows only.

The calibration section below was published first (22:45 UTC) for stream R2.

## Answer
- **The generalisation fails on the tick symbols.** Gold is the only symbol where breaking a fresh major round level
  is followed by continuation beyond the placebo grids.
  - The R1 set, all seven symbols at equal risk, major levels, 30 minutes, 250 ms: **IS -0.052 sd a trade
    (t -2.52), VAL +0.005 (t 0.29)**, power -1.66 / +0.26. Not LIVE, not DEMO.
  - Without gold: IS -0.075 (t -3.50), VAL -0.001.
  - Without oil: IS +0.001, VAL +0.034 (t 1.11).
- **At mid, outside gold, the major levels are not distinguishable from shifted grids in IS.** The R1 set without gold
  beats 60 % of the 200 placebo books at mid in IS and 96 % in VAL.
  - Outside gold the pooled mid is small and positive in five of the six class-eras (+0.01 to +0.04 sd, about +0.3
    to +2.8 bp).
  - The placebo grids show about the same: the pooled ex-gold placebo median is +0.018 sd IS and +0.020 VAL against
    the real +0.022 / +0.043. That is momentum after a fresh 24-hour extreme at any level, not a round-number barrier.
  - Oil's round trip (4-12 bp of spread) and the indices' 1-5 bp before 2021 turn it negative.
- **Gold under the round-28 rule: DEMO numbers, as in round 27, slightly weaker.**
  - IS +4.97 bp (t 2.28), VAL +2.80 (t 1.59), 8 / 9 years positive, x1.5 +4.38 / +2.59, +1 minute +5.10 / +2.45.
  - 200 placebo grids beaten 100 % in IS and VAL. Power 1.30 / 1.28.
  - PRE 2004-15 (minute level, close entry) +3.90 (t 2.50), with 8 / 12 years positive.
  - Round 27's draft had +5.99 / +3.27. The difference is 31 extra events (wider band at high prices, arming until
    16:55 NY, 18:10-18:25 NY), which lose -7.7 / -6.1 bp.
  - Draft: [PREREG_DRAFT_R1_gold_major_cascade.md](PREREG_DRAFT_R1_gold_major_cascade.md), a variant of round 27's
    draft. Register at most one of the two.
- **No other symbol meets either bar in any of its 18 cells.** 8 of the 126 cells meet DEMO numbers, all in gold:
  major h15 / h30 / h60, super h15 / h30, down h15 / h30 / h60.
- **Minute-vs-tick calibration** (for R2): enter at the trigger bar's close with no added slippage. The stop-price
  reading is biased up by +1.7 to +3.5 bp per trade. See the calibration section.
- **Per-trade CSV for the lead:** `r28/R1/trades_R1.csv`, 1,150,396 rows: real cells, 200 placebo draws, gold PRE.
  The 15- and 60-minute exits are in `trades_R1_h15_h60.csv`.

## Per symbol: primary cell (major levels, exit 30 min, latency 250 ms decides)
bp per trade; t clustered by UTC day; power = per-trade net Sharpe x sqrt(1.73 x trades a year) at the era's own rate
(oil IS = 2018-21, 4 years). Placebo = share of 200 shifted grids (subsampled to the real count) whose mean net is
below the real mean.

| symbol | n IS / VAL | mid IS / VAL (t) | IS net L0 / tick / **250** (t) / 1000 | VAL net L0 / tick / **250** (t) / 1000 | x1.5 IS / VAL; +1 min IS / VAL | years > 0 | VAL/IS | Sharpe IS / VAL | power IS / VAL (per day) | placebo IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| XAUUSD | 282 / 193 | +6.75 (3.09) / +3.83 (2.17) | +5.22 / +5.02 / **+4.97 (2.28)** / +4.59 | +2.94 / +2.81 / **+2.80 (1.59)** / +2.77 | +4.38 / +2.59; +5.10 / +2.45 | 8/9 | 0.56 | 0.144 / 0.121 | 1.30 / 1.28 (1.22 / 1.21) | 1.000 / 1.000 | **DEMO** |
| AUDUSD | 101 / 47 | -0.64 / +1.46 | -1.54 / -1.73 / **-1.78 (-1.38)** / -1.99 | +0.96 / +0.83 / **+0.76 (0.35)** / +0.69 | -2.04 / +0.71; -5.29 / -0.10 | 4/9 | - | -0.137 / 0.052 | -0.74 / 0.27 | 0.355 / 0.755 | fail |
| NZDUSD | 88 / 39 | -0.05 / -1.11 | -1.30 / -1.49 / **-1.46 (-0.88)** / -1.47 | -2.28 / -2.39 / **-2.32 (-1.44)** / -2.44 | -1.87 / -2.63; -2.24 / -1.43 | 3/9 | - | -0.094 / -0.231 | -0.47 / -1.10 | 0.770 / 0.410 | fail |
| US30 | 280 / 196 | +0.41 / +0.93 | -0.68 / -0.77 / **-0.79 (-0.39)** / -0.83 | +0.64 / +0.61 / **+0.63 (0.41)** / +0.66 | -1.39 / +0.48; -0.39 / +0.43 | 5/9 | - | -0.023 / 0.029 | -0.21 / 0.31 | 0.420 / 0.645 | fail |
| USTEC | 223 / 239 | +0.17 / +2.13 (1.01) | -1.68 / -1.79 / **-1.88 (-0.73)** / -1.90 | +1.29 / +1.25 / **+1.24 (0.59)** / +1.26 | -2.90 / +0.80; -2.14 / +1.07 | 4/9 | - | -0.049 / 0.038 | -0.39 / 0.45 | 0.315 / 0.990 | fail |
| XTIUSD | 841 / 911 | +4.44 (1.94) / +1.00 | -2.77 / -2.82 / **-3.26 (-1.50)** / -3.31 | -2.49 / -2.47 / **-2.56 (-1.69)** / -2.52 | -7.11 / -4.34; -3.58 / -2.50 | 1/7 | - | -0.049 / -0.053 | -0.94 / -1.21 | 0.875 / 0.310 | fail |
| XBRUSD | 894 / 884 | -0.07 / +4.46 (2.56) | -6.46 / -6.56 / **-6.93 (-3.30)** / -7.01 | +1.86 / +1.71 / **+1.70 (0.98)** / +1.64 | -10.35 / +0.32; -7.85 / +1.13 | 2/7 | - | -0.112 / 0.034 | -2.20 / 0.77 | 0.045 / 1.000 | fail |

Without March-April 2020, IS net (mid):

| XAU | AUD | NZD | US30 | USTEC | XTI | XBR |
|---|---|---|---|---|---|---|
| +5.10 (+6.70) | -2.82 (-1.71) | -1.51 (-0.11) | +0.35 (+1.45) | -1.29 (+0.70) | -5.49 (+1.20) | -6.17 (-0.11) |

XTI's IS mid of +4.44 comes from March-April 2020.

Mid at the major levels against the placebo grids' mid (share beaten, IS / VAL): XAU 1.00 / 1.00, AUD 0.43 / 0.78,
NZD 0.84 / 0.41, US30 0.40 / 0.64, USTEC 0.33 / 1.00, XTI 0.87 / 0.34, XBR 0.05 / 1.00. The placebo grids' own mid
is positive for indices and oil in IS: US30 +1.00, USTEC +1.30, XTI +1.14, XBR +1.87 bp.

## Classes and the R1 set (equal risk: net / the symbol's IS sd of the 30-minute net; `out/pools_*.txt`)
Units: sd units a trade (raw bp in brackets for single classes). Power at the era rate, with oil's IS rate counted on
its 4 years.

| pool (major, h30, 250 ms) | n IS / VAL (a year) | mid IS / VAL | net IS (t) | net VAL (t) | x1.5 IS / VAL | +1 min IS / VAL | years > 0 IS / VAL | power IS / VAL (per day) | placebo books beaten IS / VAL |
|---|---|---|---|---|---|---|---|---|---|
| gold | 282 / 193 (47 / 64) | +0.196 / +0.111 | +0.144 (2.28) | +0.081 (1.59) | +0.127 / +0.075 | +0.148 / +0.071 | 5/6, 3/3 | 1.30 / 1.28 (1.22 / 1.21) | 1.000 / 1.000 |
| FX (AUD, NZD) | 189 / 86 (32 / 29) | -0.028 / +0.029 | -0.117 (-1.66) | -0.036 (-0.35) | -0.141 / -0.047 | -0.286 / -0.046 | 2/6, 2/3 | -0.87 / -0.27 | 0.575 / 0.670 |
| US indices (US30, USTEC) | 503 / 435 (84 / 145) | +0.009 / +0.043 | -0.035 (-0.77) | +0.026 (0.70) | -0.056 / +0.018 | -0.031 / +0.021 | 1/6, 3/3 | -0.42 / 0.55 | 0.345 / 0.965 |
| oil (XTI, XBR) | 1,735 / 1,795 (434 / 598) | +0.032 / +0.043 | -0.082 (-3.21) | -0.006 (-0.28) | -0.138 / -0.031 | -0.092 / -0.010 | 0/4, 2/3 | -2.23 / -0.25 | 0.660 / 0.795 |
| **R1 set** | 2,709 / 2,509 (596 / 836) | +0.040 / +0.048 | **-0.052 (-2.52)** | **+0.005 (0.29)** | -0.096 / -0.015 | -0.069 / +0.000 | 0/6, 2/3 | -1.66 / 0.26 (-1.36 / 0.22) | 0.945 / 0.990 |
| R1 without gold | 2,427 / 2,316 | +0.022 / +0.043 | -0.075 (-3.50) | -0.001 (-0.06) | -0.121 / -0.022 | -0.094 / -0.006 | 0/6, 2/3 | -2.30 / -0.05 | 0.625 / 0.945 |
| R1 without oil | 974 / 714 | +0.056 / +0.060 | +0.001 (0.03) | +0.034 (1.11) | -0.020 / +0.026 | -0.029 / +0.027 | 3/6, 2/3 | 0.02 / 0.89 | 0.990 / 1.000 |

- The lead's pool.py run on this CSV alone gives the same means and t (`out/lead_pool_R1only.txt`).
- It counts oil's IS rate over 6 years (289 instead of 434 a year), so its oil and book powers are slightly lower.
- Other exits and sets of the R1 set (IS / VAL, sd units, t):
  - h15: -0.058 (-3.58) / -0.017 (-1.40);
  - h60: -0.043 (-1.42) / -0.014 (-0.60);
  - super h30: -0.039 / +0.027;
  - down h30: -0.006 / +0.017;
  - minor h30: -0.058 (-4.07) / -0.027 (-2.18).
- At the book's VAL rate (836 a year), LIVE power needs a per-trade Sharpe of 0.079. The book has +0.007.

## Dose and side (mid h30 bp (t) IS | VAL; net 250 ms h30 for the sides; `out/robust.txt`)
| symbol | minor-only levels | major, not super | super | down breaks, net | up breaks, net | repeat, net |
|---|---|---|---|---|---|---|
| XAUUSD | +0.63 \| +1.33 (1.86) | +5.95 (1.54) \| +4.44 (1.93) | +7.42 (3.72) \| +3.14 (1.29) | **+10.73 (2.51) \| +3.41 (1.51)** | +0.26 \| +2.19 | +0.21 \| +0.02 |
| AUDUSD | -0.68 \| -0.54 | +0.79 \| +0.36 | -2.75 \| +3.58 | -1.59 \| -0.84 | -1.96 \| +2.57 | -3.61 \| -2.44 |
| NZDUSD | +0.02 \| -1.20 | -0.60 \| +2.87 | +0.15 \| -2.67 | -1.60 \| -0.60 | -1.28 \| -3.66 | +3.62 \| -3.01 |
| US30 | -0.36 \| -1.50 | +0.23 \| +1.12 | +0.98 \| -0.04 | -0.49 \| +0.71 | -1.07 \| +0.56 | +3.60 \| -3.21 |
| USTEC | +0.38 \| +1.19 | +3.96 \| +1.17 | -3.21 \| +3.02 | +0.51 \| +1.36 | -4.08 \| +1.11 | -6.75 \| +5.96 |
| XTIUSD | +3.87 \| +1.87 | +4.10 (1.53) \| +0.87 | +5.77 \| +1.52 | +2.10 \| -2.90 | -8.59 (-3.39) \| -2.23 | -4.81 \| -4.62 |
| XBRUSD | +3.31 (2.12) \| -0.04 | -0.38 \| +3.63 (1.92) | +1.02 \| +8.21 (1.73) | -6.97 \| +3.78 | -6.88 \| -0.33 | -7.56 \| +5.29 |

- **Dose.** Only gold rises with the dose in both eras by more than noise (minor ~+1, major +4-6, super +3-7 bp mid).
  - AUD and US30 major-level mids sit 0.6-2.6 bp above their minor-level mids in both eras, but every one of those
    mids has |t| < 1.
  - NZD, USTEC and oil reverse between eras.
- **Side** (the declared mechanism: long holders' stops below round levels, so down breaks are stronger in gold,
  indices and BTC).
  - Gold matches in both eras: down +10.73 / +3.41 against up +0.26 / +2.19.
  - The indices lean the same way weakly. US30 down is better than up in both eras; USTEC in IS only.
  - XTI down breaks have a large IS mid (+10.22, t 2.71) that is gone in VAL (+0.71).
  - Pooled, the down set is about 0 (IS -0.006, VAL +0.017 sd units).
- **Repeat breaks** (the same level broken in the same direction within 5 days): no consistent sign anywhere. In gold
  the effect is in first breaks (IS +6.13, t 2.34; VAL +3.58, t 1.73). Round 27's touch-based "repeat" result does not
  carry over to the trigger-based definition.
- **Gold sessions (information).** NY 12-17 UTC IS +8.24, VAL +2.13; London IS +1.24, VAL +7.04. Not stable, as in
  round 27.
- **Sunday-evening NY triggers (information).** The 1,440-minute window holds only the hours since the reopen. These
  triggers are not systematically different: gold IS +8.96, VAL -1.84 (n 52).

## Gold: round 28 vs round 27 (`out/robust.txt`)
- The 444 events both rules take: IS +6.05, VAL +3.24.
- The 31 only round 28 takes: IS -7.73 (n 22), VAL -6.13 (n 9).
  - 8 trigger at 15:54-16:55 New York, 10 at 18:10-18:25 New York, 13 from the band / gap / blocked-level changes.
- The 12 only round 27 takes: IS +4.51 (n 11), VAL +8.07 (n 1).
- The round-28 rule (the one consistent across the book) therefore lowers gold from +5.99 / +3.27 to +4.97 / +2.80.

## PRE 2004-15 for XAUUSD (Dukascopy m1c, minute level, labelled; `out/pre_tables.txt`)
Minute model: entry at the trigger close (M-close, slippage 0; the calibrated reading, which goes into the CSV); IC
2016-17 spread profile + 0.6 bp. Placebo: the same 200 grids at minute level.

| cell | n (a year) | PRE net (t) | 2004-09 / 2010-15 | years > 0 | x1.5 ; +1 min | placebo beaten | IC 2016-24 minute model IS / VAL vs tick |
|---|---|---|---|---|---|---|---|
| major h15 | 469 (39) | +3.09 (2.62) | +2.62 / +3.41 (2.69) | 8/12 | +2.60 ; +2.55 | 1.000 | +2.19 / +1.74 vs +4.19 / +1.86 |
| **major h30** | 469 (39) | **+3.90 (2.50)** | +3.88 (1.34) / +3.92 (2.29) | 8/12 | +3.41 ; +3.19 | 1.000 | +2.91 / +3.02 vs +4.97 / +2.80 |
| major h60 | 469 (39) | +5.22 (2.75) | +6.91 / +4.04 | 7/12 | +4.72 ; +4.42 | 1.000 | +3.76 / +2.54 vs +4.72 / +2.96 |
| super h30 | 247 (21) | +4.73 (2.11) | +2.29 / +6.29 | 10/12 | +4.24 ; +3.85 | 1.000 | +3.16 / +2.26 vs +5.67 / +2.11 |
| minor h30 | 1,944 (162) | +0.29 (0.43) | +1.76 / -0.65 | 7/12 | -0.20 ; +0.16 | 1.000 | -0.98 / +0.31 vs -1.18 / +0.28 |
| down h30 | 237 (20) | +5.72 (2.35) | +6.57 / +5.15 | 8/12 | +5.23 ; +5.12 | 1.000 | +6.81 / +0.97 vs +10.73 / +3.41 |
| up h30 | 232 (19) | +2.05 (1.05) | +1.25 / +2.62 | 7/12 | +1.55 ; +1.21 | 1.000 | - |
| repeat h30 | 81 (7) | -0.67 (-0.23) | -3.39 / +1.51 | 5/12 | -1.17 ; +0.54 | 0.595 | +0.45 / +1.36 vs +0.21 / +0.02 |

- The stop-price readings give +9.3 (M-stop) and +8.96 (round 27's (a)) for major h30. They are biased up, as the
  calibration shows; M-stop + the 3.45 bp cell-calibrated slippage gives +5.85 (t 3.71).
- **Read against the calibration** (the close entry understates gold's IS tick result by ~2 bp and matches VAL), the
  $50-level continuation is present in 2004-15 at about the 2016-24 size, in both halves.

## Fill-model checks (`out/fillcheck.txt`; major set)
| symbol | slippage median / p90, bp: L0 \| tick \| 250 \| 1000 \| +60 s | spread-only triggers | trigger spread > 2 x s60 | delay median ms tick / 250 / 1000 | exit gaps > 10 min (h30) |
|---|---|---|---|---|---|
| XAUUSD | +0.29/1.83 \| +0.33/2.48 \| +0.33/2.65 \| +0.21/3.66 \| +0.01/8.62 | 0.131 | 0.044 | 241 / 410 / 1164 | 0 |
| AUDUSD | +0.14/0.74 \| +0.29/1.41 \| +0.29/1.64 \| +0.32/2.41 \| +0.54/6.82 | 0.101 | 0.068 | 232 / 454 / 1256 | 0 |
| NZDUSD | +0.21/0.88 \| +0.29/1.42 \| +0.29/1.44 \| +0.33/1.72 \| +0.11/5.71 | 0.102 | 0.031 | 245 / 428 / 1329 | 0 |
| US30 | +0.23/1.01 \| +0.30/1.45 \| +0.30/1.46 \| +0.28/2.03 \| +0.15/7.00 | 0.126 | 0.013 | 300 / 402 / 1199 | 0.008 |
| USTEC | +0.27/1.34 \| +0.34/1.83 \| +0.34/1.93 \| +0.44/2.18 \| +0.64/7.13 | 0.052 | 0.011 | 299 / 394 / 1194 | 0.004 |
| XTIUSD | +0.82/4.61 \| +1.19/6.43 \| +1.19/6.73 \| +0.96/7.49 \| +0.88/17.3 | 0.108 | 0.031 | 399 / 505 / 1418 | 0.002 |
| XBRUSD | +0.77/4.55 \| +0.96/5.82 \| +0.96/5.86 \| +1.03/6.61 \| +1.23/17.2 | 0.094 | 0.031 | 401 / 588 / 1500 | 0.001 |

- **Latency** is again not the constraint: L0 and L1000 differ by 0.1-0.6 bp. Cost is: oil's slippage alone is about
  1 bp at the median.
- **No entry gaps.**
- **Clamped exits** (16:54 New York) at h30: 3-18 per symbol.
- **Double fills** are impossible: one order at a time, no OCO.
  - The minimum gap between triggers is 60.0 minutes.
  - Only 0-11 triggers per symbol fall within 61 minutes of the previous one, where a +1-minute 60-minute exit could
    overlap.
- **Independent per-tick re-simulation** (`code/verify_brute.py`): 25 real sessions holding major events, 3-4 per
  symbol, with their own 24-h freshness, band, arming, cancel, trigger, busy, 1,440-minute and repeat logic, and their
  own fills. 0 event-list mismatches, repeat flags identical, max |net difference| 1.3e-6 bp.
- **Synthetic tests:** 16 groups (`code/test_engine.py`), round 27's kept and extended. They cover band edges,
  major / super flags, the 16:54 cap, repeat windows, blocked-level skipping, placebo offsets, the exclusion mask and
  the gap rule.

## Minute-vs-tick fill calibration (for stream R2; XAUUSD, AUDUSD, US30, IC 2016-24)
Full text: `r28/R1/minute_calibration.txt`.

**Recommendation for R2: enter at the trigger bar's close ask (buy) / bid (sell) with no added slippage ("M-close",
slippage 0).** That is the BRIEF's "max(stop price, first available price beyond it)" read literally on close-only
data. Do not enter at the stop price.

How it was tested:
- The same rule runs on the 1-minute panel (closes, bar-start labels) and on ticks.
- Grids: the real grid and placebo draws 0-39, which have no round-level effect by construction.
- Exit h = 30; tick latency 250 ms.

| symbol | M-close bias IS / VAL / all (bp) | M-stop bias IS / VAL / all (bp) | tick triggers the minute bot never sees | their tick net (bp) |
|---|---|---|---|---|
| XAUUSD | +0.76 / -0.09 / +0.41 | +3.99 / +2.69 / +3.45 | 17 % | -13.9 |
| AUDUSD | -0.11 / -0.11 / -0.10 | +1.83 / +1.53 / +1.73 | 11 % | -12.5 |
| US30 | -0.35 / +0.16 / -0.14 | +2.86 / +2.57 / +2.74 | 13 % | -14.5 |

Bias = minute mean net minus tick mean net on the placebo grids, each model on its own events. The draw-bootstrap sd
of the bias is 0.05-0.08 bp.

- **M-stop is biased up by selection, not by slippage.**
  - Crossings that reverse inside the minute never produce a close past the stop. Those triggers lose 12-15 bp at
    tick level, and the minute bot never trades them.
  - On the remaining events, an entry at the stop price also credits the first close's overshoot past the stop
    (+1.8 to +3.0 bp).
  - On matched trades alone, the M-stop bias is only +0.3 to +1.0 bp, mostly the tick slippage (+0.4 to +1.0 bp).
    A slippage calibrated on matched trades would therefore leave +1.4 to +2.5 bp of upward bias.
  - The slippage that removes the cell-level bias is 0.9-1.5 x the rms 1-minute move (XAU 3.45, AUD 1.73,
    US30 2.74 bp). That is not stable across symbols.
- **M-close is unbiased within +-0.4 bp under the null** (mean of the three symbols +0.06 bp).
  - By direction (down / up), the bias ranges from -0.76 to +1.12 bp.
  - The "+1 minute" variant agrees with ticks to 0.1 bp. x1.5 agrees to 0.45 bp.
- **What M-close misses: continuation inside the trigger minute.** On gold's real major levels (the one cell with an
  effect) ticks give +4.97 IS / +2.80 VAL, and M-close +2.91 / +3.03. R2's minute numbers are a lower bound when the
  move is fast.
- **Round 27's PRE code had a one-bar look-ahead in event selection.** `pre_minute.py` set T0M = t0 - 60000, so the
  24-hour freshness max at bar i included the close of bar i + 1. This drops "arm on bar i, break on bar i + 1"
  events. It does not bias returns after a close entry, which uses data only up to the entry close. It is fixed here.

## Chance and cells
- 126 cells (7 symbols x 6 sets x 3 exits; latencies are readings of a cell). Verdicts: **DEMO 8 (all gold), LIVE 0,
  fail 118**.
- Max |t| of 126 independent normals: p50 2.77, p95 3.53.
  - The best IS net t is +4.00 (XAU super h15, VAL t 0.86).
  - Gold's eight DEMO cells share most of their events; they are one finding.
- Of the six non-gold symbols' 108 cells:
  - best IS net t is +1.32 (US30 repeat h30; VAL -3.21 bp, t -1.08);
  - best VAL net t is +1.88 (USTEC repeat h30; IS t -1.47);
  - only 3 cells have net > 0 in both IS and VAL (US30 down h60, USTEC down h30 / h60), with IS t <= 0.27.

## C3 correlation (IS + VAL rows)
| cell | daily | monthly |
|---|---|---|
| gold major h30 | -0.005 | -0.143 |
| gold major h15 | +0.006 | -0.000 |
| R1 set (major h30, sd units) | -0.010 | -0.036 |

## Needs the user
- **Which gold rule to register, if any:** round 27's draft or this round's variant, not both. Either way expected
  HOLD t is 0.8-1.5, so HOLD can only reject. The draft is
  [PREREG_DRAFT_R1_gold_major_cascade.md](PREREG_DRAFT_R1_gold_major_cascade.md).
- **A demo or forward log** of the gold rule on data after 2026-09-24 (a cBot with server-side stops at L + 0.5 s60
  and a 30-minute timed exit). At ~60 trades a year it is the only way to add evidence without HOLD.
- Nothing in R1 makes a cheaper venue worth asking for:
  - oil's mid at major levels is not distinguishable from shifted grids;
  - the indices and FX have no mid effect.

## Untested ideas (not declared, so not candidates)
- **Down breaks of gold's $50 / $100 levels only.** A declared cell this round: DEMO, IS +10.73 (t 2.51), VAL +3.41
  (t 1.51), power 1.15 at ~32 a year. But it repeats round 27's post-hoc observation on the same data, so it is not
  new evidence. Only new data can test it.
- **Gold-like barriers on other gold venues** (COMEX GC quotes, Shanghai Au99.99), where the round numbers differ from
  spot by the basis. That would separate a spot-quote cluster from a futures one.
- **XTI down breaks.** IS mid +10.2 (t 2.71) is gone in VAL (+0.7) and comes largely from March-April 2020. Not worth
  pursuing.

## Scripts and outputs
Scripts are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/R1/code/`
(round 27's originals in `code/r27_orig/`) and outputs in `.../r28/R1/out/`. Run them from the repo root with
`PYTHONPATH=. research/.venv/bin/python <script>`.

| script | what it does |
|---|---|
| gcommon.py | HOLD-asserting tick loader, symbol table (spacings, commission, calendar currencies), calendar, clustered t, power |
| build_minutes.py | per-minute tick envelopes, 24-h max / min, s60 -> `out/min_<SYM>.npz` (gold reuses round 27's file) |
| engine.py | sessions, exclusion mask (16:55-18:10 NY, calendar, real gaps), the declared bot, placebo offsets |
| fills.py | fills at 0 / next tick / 250 / 1,000 ms / +60 s, timed exits with the 16:54 NY cap, x1.5 |
| test_engine.py | synthetic-tick tests |
| verify_brute.py | independent per-tick re-simulation of real sessions -> `out/verify_brute.txt` |
| peek.py, count_summary.py | pre-declaration looks (prices only) -> `out/count_summary.txt` |
| run_events.py | real grid and 200 placebo grids per symbol, every latency and exit -> `out/ev_<SYM>_full_{real,placebo_0_200}.npz` |
| analyze.py | the 126 cells, placebo shares, verdicts -> `out/cells.txt`, `out/cells.pkl` |
| pool_r1.py | class / R1-set pools in sd units, pooled placebo -> `out/pools_<cell>_h<h>.txt` |
| robust.py | dose / side / repeat / year / session splits; round 27 comparison -> `out/robust.txt` |
| fillcheck.py | fill checks -> `out/fillcheck.txt` |
| minute_bot.py, minute_nets.py | minute-level replica (IC panel 2016-24; Dukascopy PRE 2004-15), both minute fill readings |
| calib.py | minute-vs-tick calibration -> `out/calib_<SYM>.txt`, `r28/R1/minute_calibration.txt` |
| pre_analyze.py | gold PRE tables -> `out/pre_tables.txt` |
| c3corr.py | C3 daily / monthly correlation -> `out/c3corr.txt` |
| write_csv.py | `r28/R1/trades_R1.csv`, `trades_R1_h15_h60.csv` (sd_is_30min in `out/sd_is_30min.txt`) |
