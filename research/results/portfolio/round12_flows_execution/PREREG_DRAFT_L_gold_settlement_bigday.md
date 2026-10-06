# PREREG DRAFT (stream L, round 12): gold momentum into the COMEX settlement on top-decile move days

Draft, 2026-10-06. Not registered and HOLD not opened. The lead registers it and runs HOLD. Tier: **DEMO**. It cannot
be LIVE: its power is 1.6 IS / 1.3 VAL, and LIVE needs 3.
Source: research/results/portfolio/round12_flows_execution/STREAM_L.md, family L4, and HYPOTHESES_L.md. Scripts are in
scratchpad r12/L/ (l4_settle.py, l4_checks.py, l4_random.py).

## Mechanism
Flows that trade in the direction of the day's gold move are executed at the COMEX settlement (13:29-13:30 ET VWAP).
Two such flows: leveraged and inverse gold funds, which rebalance in proportion to L(L-1) x AUM x the day's return
(Cheng & Madhavan 2009), and trade-at-settlement / settlement-benchmarked trend and hedging orders. If these flows
are proportional to the day's move, they matter only on days with a very large move. Round 6 (S1) found gold
momentum into the settlement on all days, with slope t +6.8 IS / +2.6 VAL. That was too small to trade, and platinum,
which has no sizeable leveraged ETF, reverses. Stream L tested the dose-response, a top decile of |z|, chosen before
any number was computed.

## Exact rule
- Symbol XAUUSD (IC). Days: NYSE business days. The clock is New York local time, DST-aware.
- S(d) = XAUUSD mid at 13:30:00 ET on business day d (close of the minute bar ending 13:30).
- sd(d) = standard deviation of the previous 60 daily log returns ln S(k)/S(k-1). Day d is excluded.
- z(d) = ln( mid at 13:14:00 ET on d / S(d-1) ) / sd(d).
- thr(d) = 90th percentile of |z| over the previous 250 business days (at least 60), causal.
- If |z(d)| > thr(d): at 13:15:00 ET enter at market in direction sign(z(d)). Exit at market at 13:30:00 ET.
- Default fixed lot. No scaling, no stop or target (15-minute hold). One position at a time, no swap.
- Parameters: q = 0.10 and w = 15 min. q was declared before the numbers. w = 15 is round 6's primary window,
  which round 6 picked from its IS scan of 5-120 min.

## IS / VAL evidence (executable: actual spread half in + half out, plus 0.6 bp commission)
| | IS 2016-21 | VAL 2022-24 |
|---|---|---|
| trades (per year) | 150 (25) | 78 (26) |
| mid bp (day t) | +4.74 (4.31) | +3.14 (2.53) |
| net bp (day t) | **+3.31 (3.02)** | **+2.11 (1.70)** |
| median net, share of trades > 0 | +1.82, 56 % | +0.40, 53 % |
| per-trade net Sharpe; power at 25/yr | 0.247; 1.62 | 0.193; 1.29 |
| spread x1.5 / +1 minute | +2.90 / +1.27 | +1.90 / +1.38 |
| winsorised 2.5/97.5 % | +3.00 (t 3.15) | +2.20 (t 1.89) |
| years net > 0 | 4/6 | 3/3 (7/9 in total) |
| random entry (a): random window end 10:30-16:00 ET, side recomputed, 500 seeds | beats 99.4 % | beats 90.6 % |
| random entry (b): random window after the signal, 13:46-16:45 ET, same side | beats 100 % | beats 100 % |
| time placebo: rank of this window's t among 23 window ends, 10:30-16:00 ET | 1 (next best +2.19) | 2 (16:00 ET window +4.12) |
| C3 correlation, IS+VAL | daily +0.015, monthly -0.14 | |

Per-trade Sharpe at mid is 0.35 / 0.29 on selected days, against 0.07 / 0.03 on all days. The selected days have a
larger sd (13.4 vs 9.6 bp IS), but the mean grows much more than the sd does.

## Multiple testing
- Stream L counted 42 cells (L4 family: 7).
- The best uplift t (selected vs unselected days, IS) was this cell's +4.04. The shared label-permutation null over
  all 42 cells gives a 95th percentile of 2.92 (p 0.002).
- Its IS net t of +3.02 is the best of the 42. The shared per-day sign-flip null gives a 95th percentile of 3.04
  (p 0.056), so it sits at the edge of chance as a pick from 42 cells.
- VAL confirms it on its own: net +2.11, t 1.70, uplift t +2.50.

## Known weaknesses (the lead should weigh these)
1. Silver, the mechanism's twin (AGQ/ZSL), flips in VAL. Its top-decile cell is +11.8 bp (t 4.2) IS and -4.8 (t -2.2)
   VAL. Gold persists, but the leveraged-ETF story alone does not explain why silver flipped.
2. In IS, part of the mean comes from 25 days with |z| > 3 (+14.3 bp). VAL had only 9 such days (-0.1). In both eras
   the 2 < |z| < 3 bin is +5.3 bp (t 3.5 IS / 2.6 VAL).
3. Random control (a) is beaten by only 90.6 % in VAL, just above the DEMO bar.
4. Down days carry most of the edge: net +5.1 IS / +3.4 VAL on short trades, against +1.6 / +0.9 on long trades.
5. No PRE check is possible. Dukascopy XAU is H1 only here, and a 15-minute window needs M1. Downloading Dukascopy
   XAUUSD M1 for 2004-15 would be a new price series, so it is the user's decision.
6. The window is sensitive. q 0.10 with w = 10 gives +2.12 (t 2.08) / +2.50 (t 2.31). With w = 5 it gives +0.15 /
   +0.53, and with w = 30 it gives +3.35 / +0.49.

## Bar, holdout, demo
- Bar: DEMO. IS day-clustered t >= 2.0 (3.02 met), net > 0 in VAL (+2.11 met), beats >= 90 % of random entries (met).
  There is no power requirement.
- Expected HOLD trades (2025-01..2026-09): about 25 x 1.73 = 43. Expected HOLD t is 1.3-1.6 at the VAL or IS
  per-trade Sharpe, so HOLD alone is unlikely to reach 2.5 even if the effect is real.
- Expected demo trades: about 25 a year, at most 1 a day, each held 15 minutes.
- Stop rule (demo): stop if, after 40 demo trades, the pooled HOLD + demo net t is < 0. Also stop if a single trade
  loses more than 5x the median absolute trade P&L because of a fill problem, such as a spread above 3 bp at 13:15 or
  13:30 ET; that is an execution failure, so report it.
- Promotion rule: HOLD + demo pooled day-clustered net t >= 2.5, judged at the IC costs actually paid.
