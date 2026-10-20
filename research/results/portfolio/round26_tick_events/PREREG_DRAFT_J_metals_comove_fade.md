# PREREG DRAFT J: fade large co-moving precious-metals jumps in the Asian session (round 26, stream J)

Written 2026-10-17 20:52 UTC by stream J. **Draft only: not registered, HOLD (2025-01..2026-09) not opened, no code
hashed.** The brief asks for a draft whenever a declared cell meets the LIVE or DEMO numbers on IS / VAL. This one
meets the DEMO numbers, but it is within chance for its family and goes against the mechanism the hypotheses
declared. **Recommendation: do not open HOLD for it** (see "Why not to register"). The lead decides.

## Rule (exact; cell `J2 W10 k16 h15 none CO METALS Asia` of [HYPOTHESES_J.md](HYPOTHESES_J.md), definition D2)
- Instruments: XAUUSD, XAGUSD, XPTUSD (IC, cTrader). Each is detected and traded on its own ticks.
- Local sigma (bp): bipower variation of the 60 one-minute log-mid returns of the complete minutes before the current
  minute (minute price = last mid at or before the minute end), sigma^2 = (pi/2) x mean(\|r_j\| \|r_j-1\|). It needs
  >= 45 valid products; a return is invalid if it straddles a quote gap >= 10 min.
- Threshold theta = max(16 x sigma, 2 x the median of the last 60 minute-end spreads), in bp of mid.
- Jump: at a tick, the mid is >= theta above the minimum (or below the maximum) of the prevailing mids over the last
  10 s. Direction d = +1 for up, -1 for down. Detection time t_d = that tick. One event per instrument per 15 min.
- Co-move filter (CO, causal): at t_d, at least one of the other instruments among AUDUSD, NZDUSD, XAUUSD, XAGUSD,
  XPTUSD moved in the same direction by >= 2 of its own sigma over [t_d - 60 s, t_d]. That instrument also needs a
  valid sigma and a tick in the last 10 min.
- Session: Asia only, i.e. from 18:10 New York to 07:00 London (DST-aware).
- No detection inside these windows:
  - USD and "All" High / Medium calendar rows, +-30 min;
  - the central-bank decision windows (T - 30 to T + 120 min; BOJ days 01:30-07:30 UTC);
  - untimed USD / All rows (whole day);
  - High-impact votes (the day and the next);
  - rollover 16:35-18:10 NY;
  - the metals clocks: 08:15-08:30 and 13:25-13:40 NY; 09:40-09:55, 10:25-10:40, 11:55-12:10, 13:55-14:10 and
    14:55-15:10 London;
  - 30 min after a quote gap >= 10 min;
  - E10, [m - 2, m + 5) around these UTC minutes m, by New York season:
    - XAUUSD, NY winter: 00:01, 00:09, 01:00, 01:01, 05:30, 05:31, 05:32, 07:00, 08:00, 13:00, 18:02;
    - XAUUSD, NY summer: 00:00, 01:00, 01:01, 05:30, 06:00, 23:00;
    - XAGUSD, NY winter: 00:30, 01:00, 01:01, 01:02, 05:30, 05:31, 05:32, 08:00, 13:00, 18:24;
    - XAGUSD, NY summer: 00:00, 01:00, 01:01, 01:02, 05:30, 05:31, 12:00, 17:24;
    - XPTUSD, NY winter: 11:28, 18:03;
    - XPTUSD, NY summer: 01:15.
- Trade: a market order against the jump (sell after an up jump, buy after a down jump). It fills at the first tick
  with ts >= t_d + 250 ms (buy at the ask, sell at the bid). Exit at market at the first tick >= t_d + 250 ms +
  15 min. No stop (the tested stop at theta fails: IS +5.01 bp, t 0.75). Fixed lot. At most 3 positions at once (one
  per metal).
- Costs: the actual bid / ask of the ticks, plus 0.6 bp round-trip commission.

## Numbers (IC ticks, IS 2016-21, VAL 2022-24; scratchpad r26/J/out/cells_D2.npy, cell 2413)
| | IS | VAL |
|---|---|---|
| events (days) | 46 (39) | 7 (7) |
| mid bp (t) | +17.87 (3.70) | +30.50 (3.61) |
| net bp at L 250 ms (day-clustered t) | **+12.15 (2.60)** | **+18.49 (2.17)** |
| net at L 0 / 1,000 ms / next tick (t) | +15.05 (2.66) / +14.05 (2.72) / +12.29 (2.65) | +17.13 (2.44) / +13.40 (1.13) / +18.05 (2.11) |
| net at +1 minute (L 60 s) | +16.61 (t 1.17) | +5.88 (t 0.96) |
| net at spread x1.5 | +9.59 | +12.79 |
| spread paid (bp) | 5.12 | 11.40 |
| winsorised at the IS 1 / 99 % (t) | +10.46 (3.37) | +18.50 (2.17) |
| IS without March-April 2020 (t) | +11.75 (2.47) | - |
| per-trade net Sharpe; power = Sharpe x sqrt(1.73 x events / yr) | 0.383; 1.40 | 0.821; 1.65 |
| random-time control RT (200 seeds; RT mean net) | beats 100 % (-4.76 bp) | 100 % (-8.58 bp) |
| random-direction control RD | 100 % | 98 % |

- By year, net bp: 2016 +9.0, 2017 +7.5, 2018 +2.1, 2019 +5.0, 2020 +26.6, 2021 +61.8, 2022 -9.7, 2023 +23.5,
  2024 +39.1 (8/9 > 0).
- Events by year: 19, 18, 2, 2, 2, 3, 2, 3, 2. 37 of the 53 events are in 2016-17.
- By metal (IS): XAUUSD +9.80 bp (t 4.91, n 25; VAL +14.08, n 4), XAGUSD +17.77 (t 1.53, n 18; VAL n 2), XPTUSD
  -1.96 (n 3).
- Same effect in the neighbouring declared cells. All sessions: IS +9.98 (t 2.37, n 116), VAL +13.80 (t 2.18, n 11).
  W30 instead of W10: IS +9.05 (t 2.35), VAL +16.98 (t 2.21, n 11). Without E10 (definition D1): IS +12.38 (t 2.95),
  VAL +14.97 (t 2.52, n 11).
- It is absent at W60 (IS -1.16 bp) and at k6 (IS -1.92 bp, t -2.39). Only the largest and fastest jumps qualify.

## Cell count and chance
- Counted: 7,776 cells on D2 plus the same 7,776 on D1 (15,552). 108 of them are primary; this cell is not one of
  them (the primary J2 cells are SINGLE).
- D2: the family's best IS net t is this cell's 2.60. The per-day sign-flip permutation null of the max over 7,392
  cells has p95 2.88, and 13.8 % of its draws exceed 2.60. **The result is within chance.**
- D1: the max is 2.95 against a null p95 of 2.91 (4.3 % of draws exceed it).

## Expected HOLD (not opened)
- The event rate since 2018 is 2.3 a year in Asia (VAL 7 in 3 years). HOLD (1.73 years) would hold **about 4
  events** (about 6 for the all-session variant).
- Expected HOLD t:
  - at the VAL size: 0.821 x sqrt(4.0) = **1.6**;
  - at 0.65 of VAL: **1.1**;
  - at round 18's 1/4 retention for a pick made with VAL in view: **0.4**.
- Four trades cannot tell any of these apart.

## DEMO-tier additions (if the user wanted it on demo anyway)
- Expected demo trades: about 2-3 a year (Asia), 3-4 with all sessions.
- Stop rule (fixed now): stop the demo after 8 demo trades if the mean net per trade is <= 0 bp.
- Promotion rule: HOLD + demo pooled day-clustered t >= 2.5 with >= 30 trades. At this rate that is about a decade.

## C3 correlation (IS + VAL)
Daily net P&L vs C3's daily P&L: **+0.014** over all weekdays, +0.10 over its 44 trade days.

## Why not to register
1. **Within chance**: 13.8 % of the permutation draws beat it (D2).
2. **Wrong side for the declared mechanism.** The hypotheses declared co-moving jumps as information, so they should
   continue (J1). Here they revert. The likely story, gold and silver sharing one thin Asian liquidity pool (COMEX
   Globex and Shanghai) so that one liquidity event moves both, is a reinterpretation made after the fact.
3. **The events disappear after 2017** (37 of 53 in 2016-17). Something changed in the market or in IC's metals
   feed.
4. **No PRE check is possible.** Dukascopy has only M1 closes for metals. The declared minute proxy reproduces the
   tick result on IC's own M1 with only 8-10 IS events and 0-1 VAL events, so it is not meaningful. As information,
   the proxy gives PRE 2008-15 gold -3.0 bp net (n 30) and silver +8.5 bp (n 35).
5. **The holdout cannot decide it** (about 4 events, expected t 0.4-1.6).
6. **Tail risk and wide fills.** The stop variant fails, so the trade carries the full tail: one silver event
   (2021-02-18) is +207 bp. The VAL spread paid averages 11.4 bp.
