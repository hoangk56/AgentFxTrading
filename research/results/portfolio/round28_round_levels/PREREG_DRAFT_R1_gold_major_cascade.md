# Draft pre-registration: gold's major-round-level cascade under the round-28 rule (stream R1)

Draft written 2026-10-17 22:47 UTC (`date -u`) by stream R1. **HOLD (2025-01-01..2026-09) has not been opened.** The
lead decides whether to register this and open HOLD. Tier: **DEMO numbers on IS / VAL**. Not LIVE: power at the VAL
size is 1.28 against 3.

**This is a variant of round 27's draft, not a second candidate.**
- Round 27's draft is [../round27_levels_opens/PREREG_DRAFT_G_gold_round50_cascade.md](../round27_levels_opens/PREREG_DRAFT_G_gold_round50_cascade.md).
- The two rules share 444 of their 475 / 456 events. Register at most one of them.
- Rule and cells were declared in [HYPOTHESES_R1.md](HYPOTHESES_R1.md) at 22:26 UTC; results are in [STREAM_R1.md](STREAM_R1.md).

## How it differs from round 27's draft
| | round 27 draft (G1-XAU50 c0.5 h30) | this draft (round-28 rule, XAUUSD major, h30) |
|---|---|---|
| arming band | $2 | 0.15 % of the mid ($1.6-4.2 over 2016-24) |
| arming window | 18:10 NY .. 15:54 NY | 18:10 NY .. 16:55 NY; exits clamped at 16:54 NY |
| gap rule | every session start treated as a gap (18:10-18:25 NY excluded) | real quote gaps > 60 min only |
| blocked level | skip to the band exit | skip only that level's candidate ticks |
| IS / VAL net (t), 250 ms | +5.99 (2.66) / +3.27 (1.81) | **+4.97 (2.28) / +2.80 (1.59)** |
| events IS / VAL | 271 / 185 | 282 / 193 |

- The 444 shared events give +6.05 IS and +3.24 VAL, the same as round 27.
- The 31 events only this rule takes lose -7.73 IS (n 22) and -6.13 VAL (n 9):
  - 8 trigger at 15:54-16:55 New York;
  - 10 at 18:10-18:25 New York;
  - 13 come from the wider band.
- The 12 events only round 27 takes gain.

So the round-28 generalisation costs gold about 1 bp a trade. Whether that is chance or the thin hours around the
New York close and reopen is not known.

## Rule (exactly as tested)
- **Instrument and data.** XAUUSD at IC Markets (cTrader), tick quotes. mid = (bid + ask) / 2.
- **Levels.** Minor levels every $10. A trade is taken only when the level is a multiple of $50.
- **Arming window.** From 18:10 New York (day d-1) to 16:55 New York (day d). Never within +-15 minutes of a
  High-impact USD calendar minute, and never within 15 minutes after a quote gap > 60 minutes.
- **Arming.** Only while flat, i.e. >= 60 minutes after the last trigger on any level. The bot arms on the nearest $10
  level within b = 0.0015 x mid of the mid:
  - an upper level if it is above the highest tick mid of the previous 1,440 clock minutes;
  - a lower level if it is below the lowest;
  - in both cases only if that level has not triggered in the previous 1,440 minutes and the order is not marketable
    when placed.
- **Order.** Upper level: a buy stop at L + 0.5 x s60 (triggers when ASK >= it). Lower level: a sell stop at
  L - 0.5 x s60 (BID <= it).
  - s60 = the median, over the 60 clock minutes before the arming minute, of each minute's last-tick spread.
  - The order is cancelled when the mid leaves the band or an exclusion starts.
- **Trigger.**
  - Every trigger starts the 60-minute busy window and blocks its level for 1,440 minutes.
  - Only triggers at multiples of $50 are traded.
- **Exit.** A market order 30 minutes after the trigger, or at 16:54 New York if that is earlier. No protective stop.
  No position crosses 17:00 New York, so no swap. One position at a time; fixed lot.
- **Side.** The direction of the break (Osler 2003 / 2005), not from our data.

## Numbers on IS (2016-21) and VAL (2022-24)
Latency 250 ms; fills at the ASK / BID of the first tick at or after trigger + 250 ms; commission 0.6 bp. bp per trade,
t clustered by UTC day.

| reading | IS | VAL |
|---|---|---|
| trades (per year) | 282 (47.0) | 193 (64.3) |
| mid, bp (t) | +6.75 (3.09) | +3.83 (2.17) |
| net L0 / next tick / 250 / 1000 ms | +5.22 / +5.02 / **+4.97 (t 2.28)** / +4.59 | +2.94 / +2.81 / **+2.80 (t 1.59)** / +2.77 |
| net at spread x1.5 | +4.38 | +2.59 |
| net, both fills +1 minute | +5.10 | +2.45 |
| per-trade net Sharpe; power at its own rate | 0.144; 1.30 | 0.121; **1.28** |
| per-day power | 1.22 | 1.21 |
| placebo: 200 grids shifted between minor levels, share beaten (draw median) | 1.000 (-3.15) | 1.000 (-1.74) |
| without March-April 2020 | +5.10 (t 2.29) | - |
| median trade; winsorised at the IS 1 / 99 % | -1.25; +4.02 | -0.80; +2.80 |

Net by year:

| 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| +4.67 | +3.83 | +5.49 | -1.13 | +6.67 | +7.66 | +1.89 | +4.52 | +2.66 |

- 8 of 9 years are positive. VAL / IS = 0.56.
- The top 5 trades make 890 of the IS total of 1,403 bp: a right tail, as in round 27.
- **PRE 2004-15** (Dukascopy, minute level; entry at the trigger close; the calibration says this reading is unbiased
  under the null within +-0.4 bp and understates the IS tick result by ~2 bp):
  - net +3.90 (t 2.50), mid +5.49;
  - 2004-09 +3.88 (t 1.34), 2010-15 +3.92 (t 2.29);
  - 8 of 12 years positive; 200 minute-level placebo grids beaten 100 %.
- **Doses and sides.** Super ($100) levels: IS +5.67 (t 2.83), VAL +2.11. Down breaks: IS +10.73 (t 2.51), VAL +3.41
  (t 1.51). Up breaks: +0.26 / +2.19.
  - The side split was declared in this round, but it repeats round 27's post-hoc observation on the same data, so it
    is not new evidence.
- **Repeat touches** (the same level broken in the same direction within 5 days): about 0 (+0.21 / +0.02). The
  continuation is in first breaks.

## Cell count, selection, chance
- Stream R1 declared 126 cells (7 symbols x 6 sets x 3 exits). 8 meet the DEMO numbers, all in gold: major h15, h30,
  h60; super h15, h30; down h15, h30, h60. None is LIVE.
- No symbol other than gold meets either bar. The R1 set fails: IS -0.052 sd a trade (t -2.52), VAL +0.005 (t 0.29).
- Max |t| of 126 independent normals: p50 2.77, p95 3.53. This cell's IS net t is 2.28.
- **The hold is not a fresh choice for gold.** The 30-minute hold was picked in round 27 after looking at gold. Treat
  the expected HOLD retention as below the 0.65 of fully declared rules.

## Expected HOLD (21 months)
- About 111 trades (64.3 a year x 1.73).
- Expected HOLD t:
  - 1.28 at the VAL effect size;
  - 0.83 at 0.65 of it;
  - 0.32 at 0.25 of it (post-hoc retention).
- If registered as DEMO: open HOLD once; **net < 0 in HOLD = reject.**

## DEMO terms (if run on the demo account)
Same as round 27's draft:
- about 60 trades a year;
- stop if cumulative net < 0 after 60 demo trades, or below -1.5 sd of the expected sum after 120;
- promotion rule: HOLD + demo pooled net t >= 2.5, about 430 trades at the VAL Sharpe (0.121), i.e. ~7 years.

## Correlation with C3
IS + VAL rows only:

| hold | daily | on its 453 trade days | monthly |
|---|---|---|---|
| 30 minutes | -0.005 | -0.023 | -0.143 |
| 15 minutes | +0.006 | | -0.000 |

## Recommendation
- Register at most one gold rule.
- The round-28 version is the one consistent with the pooled book; round 27's version has the better numbers and was
  written first.
- Both have an expected HOLD t of about 0.8-1.5, so HOLD can only reject. The value of either is a demo log, not the
  holdout.
