# Round 17, stream Z: hypotheses (written before any number)

Written 2026-10-06 02:42 UTC (`date -u`), before any return of this stream was computed. The only thing looked at
before writing is quote coverage at the clock minutes used (coverage.py: share of weekdays 2016-2024 with a bar at
08:00-18:00 CET for STOXX50, F40, ES35, IT40; no prices, no returns). Findings that shaped the rule: ES35 has no
quotes before 09:00 CET; IT40 has a bar in the 09:00 minute on 80 % of days and STOXX50 on 75-83 % at 12:00/13:30, so
the open reference is taken at 09:05 and mids are forward-filled up to 10 minutes (as in rounds 12-13). HOLD
(2025-01-01 onwards) is cut at load (ts < 1735689600000) for the bid-only caches; the shared panel ends 2024-12-31.

## Mechanism and source
Intraday momentum: the return from the previous close (or the open) to midday predicts the return over the rest of
the session, most strongly on high-volatility / big-move days.
- Gao, Han, Li & Zhou (2018, JFE): the first half-hour return (incl. the overnight move) predicts the last half hour
  of the US session; stronger on high-vol days; explained by infrequent rebalancing and late-informed traders.
- Baltussen, Da, Lammers & Martens (2021, JFE): the rest-of-day return predicts the last 30 minutes in 60+ futures
  markets incl. European indices; driven by gamma hedging (short-gamma dealers, LETFs) proportional to the day's move.
- Round 13 P: on DE40 big days, following the day's direction pays at any intraday hour (dose slope t +3.3 IS /
  +4.0 VAL), not only into the close. That observation is why DE40 is information only here.
Side: **follow** (continuation), fixed by the literature and by round 12 L4 / round 13 P; not chosen from data.
Gate: round 12 L4's top decile of the vol-scaled move, causal, fixed before looking.

Why it may escape the limits: a hold of 2-5.5 hours on top-decile days has an sd of tens of bp, so a 3-5 bp round
trip is a small share. Why it may not: round 13 P found the US big-day scale-up was March-April 2020, and US big days
reversed into the close in VAL; round 7 B saw European close momentum only in VAL (STOXX50 +3.7, t 2.4) and below
spread; decay (round 12 lesson) is reported as VAL/IS.

## How this differs from earlier tests
| earlier | what it tested | here |
|---|---|---|
| r4 Baltussen, US30/USTEC/UK100 | day's move -> last 30 min, all days and \|z\| > 2 | European continental indices, longer holds (cut -> close), causal top decile, dose bins |
| r7 B, STOXX50 | momentum into the European close, all days | big-day gate, 3 cuts, 5 indices, open and previous-close references |
| r8 X2c | European morning -> US session (US500 1 h) | European morning -> rest of the European session |
| r11 H1 | 15/60-min clock windows, unconditional mean | data-dependent side, big-day gate |
| r13 P | day's move -> last 10-15 min before the close benchmark | cut -> close (hours), several cuts, the bid-only European indices |

## Rule Z1 (all choices fixed here)
Symbols and clocks (venue local time, DST-aware via zoneinfo; mid = (bid+ask)/2 from the panel, or bid + published
spread / 2 for bid-only symbols; mids forward-filled at most 10 minutes; "price at T" = close of the M1 bar ending at
T):
| group | symbols | open ref O | cuts C | close E | venue days |
|---|---|---|---|---|---|
| EU (counted) | STOXX50, F40, ES35, IT40 | 09:05 CET | 12:00, 13:30, 15:30 CET | 17:30 CET | weekdays minus 1 Jan, Good Friday, Easter Monday, 1 May, 24/25/26/31 Dec |
| EU (counted) | UK100 | 08:05 London | 11:00, 12:30, 14:30 London (same instants as the CET cuts) | 16:30 London | XLON days minus 24/31 Dec |
| info | DE40 | 09:05 CET | as EU | 17:30 CET | as continental EU |
| US comparison (counted) | US30, USTEC | 09:35 ET | 12:00, 13:30, 15:30 ET | 16:00 ET | XNYS days minus early closes (3 Jul, day after Thanksgiving, 24 Dec) |

For symbol X on venue day d:
- close(d) = price at E on day d; sd(d) = std of the previous 60 venue-day log returns ln close(k)/close(k-1)
  (>= 30 valid), day d excluded.
- Two references: **P (previous close)**: z = ln( price(C) / close(d-1) ) / sd(d) (the literature's signal incl. the
  overnight move, and L4's gate variable); **O (open)**: z = ln( price(C) / price(O) ) / sd(d).
- thr(d) = 90th percentile of \|z\| (same symbol, reference and cut) over the previous 250 venue days (>= 60 valid).
  Selected if \|z(d)\| > thr(d). Side = sign(z(d)).
- Trade: enter at the price at C + 1 minute (one-minute lag after the signal); exit at E (horizon "close") or at
  C + 1 + 60 minutes (horizon "60"; dropped where it would pass E, i.e. US 15:30). One trade per symbol per day.
- Mid return in bp, signed. Net = mid - cost. Cost: panel symbols (UK100, DE40, US30, USTEC): half the actual spread
  at the entry minute + half at the exit minute. Bid-only: round 7's published spreads (STOXX50 1.5, F40 1.79, ES35
  4.2, IT40 9.0 index points) / price, one full spread per round trip. No commission (indices); intraday, no swap.
- Stress: spread x1.5; both fills one minute late (enter C+2, exit E+1 or C+62); winsorised mean (2.5/97.5 % per
  era); without 2020-03-01..2020-04-30.

**Primary cell (declared): Z1-EU5 pooled, reference P, cut 13:30 CET, horizon close.** Pooled = mean of the selected
trades of STOXX50, F40, ES35, IT40, UK100 per UTC day, t over days. Everything else is a secondary counted cell.

Cells: EU per symbol 5 x 2 refs x 3 cuts x 2 horizons = 60; EU5 pooled 2 x 3 x 2 = 12; US per symbol 2 x 2 x 5 = 20.
**92 counted cells**; DE40 (12 cells) is information only but sits in the shared null (104 in the null).

## Dose-response (fixed)
All venue days (no gate), per symbol / pool, reference, cut, horizon close, by era: mean signed momentum by \|z\|
bin 0-0.5, 0.5-1, 1-1.5, 1.5-2, 2-3, > 3; OLS slope of signed momentum on min(\|z\|, 4). Prediction: positive slope
and top decile > all-days mean in both eras.

## Statistics, controls and bars
- Mean bp, t clustered by UTC day (single-symbol cells: one trade a day, so per-trade t), by era (IS 2016-21,
  VAL 2022-24; no PRE: no index data before 2016) and by year; VAL/IS ratio of mid and net.
- Power = per-trade net Sharpe x sqrt(1.73 x trades a year), on the IS and VAL sizes (pooled: per-day units); the VAL
  one is the expected HOLD t.
- Random-entry control (look-ahead-free in side): same selected days, same count and hold length; entry T' uniform
  over minutes with [T', T'+hold] inside [O+25 min, E]; side = sign of the move from the same reference to T' - 1;
  actual cost model; 500 seeds. Windows starting before C overlap the move that selected the day, which biases this
  control upward (conservative). **This is the control that counts for the bar.** Also reported (RC-B, strictly
  after the signal): T' uniform in [C+1, E-30] (close horizon, exit at E) or [C+1, E-60] (60-min horizon), side
  recomputed at T'.
- Chance: per-UTC-day sign flip shared by all 104 cells (one sign per UTC day applied to every cell's mid), 1,000
  permutations: max IS mid \|t\|, max IS net t (flipped mid - cost), max VAL net t; plus max of K normals.
- C3 daily and monthly correlation (IS+VAL) for any survivor.
- Bars (round-13 brief): DEMO = IS day-clustered t >= 2.0, VAL net > 0, >= 2/3 of years > 0, x1.5 and +1 min > 0 in
  both eras, beats >= 90 % of the random control; LIVE = IS t >= 2.5, VAL t >= 1.5, beats >= 95 %, power >= 3. A
  secondary cell meeting a bar must also clear the shared null in IS. If met: PREREG_DRAFT_Z_<name>.md, stop the
  family, HOLD stays closed.

## Predictions written down
- The pooled EU top decile follows through (+5..+15 bp over the cut -> close hold) in IS; part of it is
  March-April 2020; VAL smaller (decay) but positive given DE40's VAL dose slope.
- The P reference is stronger than O (the literature's signal includes the overnight move).
- Costs (3-5 bp bid-only, 1-3 bp UK100) are small relative to the sd of a multi-hour hold, so the question is the
  sign and stability, not the cost.
- US30 / USTEC: given round 13 P, big-day continuation in IS (2020) and reversal or nothing in VAL.
- The random control (same days, any hour) will be hard to beat: if the effect is big-day trend at any hour, the cut
  adds nothing and the cell fails the control, as DE40 did in round 13.
