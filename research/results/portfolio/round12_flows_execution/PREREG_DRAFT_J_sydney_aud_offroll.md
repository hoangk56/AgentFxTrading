# PREREG DRAFT (stream J, round 12): AUDUSD Sydney-open dip, traded only outside IC's rollover hour

Status: draft for the lead. Written 2026-10-06 after IS/VAL only; HOLD (2025-01-01 onwards) was never loaded. Tier
reached on IS/VAL: **DEMO** (LIVE fails on power). **Post hoc disclosure (read first):** the day filter was written
after a diagnostic (D1 in HYPOTHESES_J.md) that split the Sydney V by New York clock time in both IS and VAL, so VAL
is not a clean check of the filter. The filter selects days on cost, which is known in advance from IC's rollover
schedule, not on returns: the mid edge on the kept AUD days (+1.54 IS / +1.53 VAL bp) equals the edge on all AUD days
(+1.57 / +1.28). IS alone picks the same filter (rollover-hour days IS net -0.90, t -4.7) and the same symbol (AUD
+0.44 vs NZD +0.12 IS). The only clean tests are HOLD and forward/demo trading.

## Mechanism
Round 4 and round 10 E found AUD and NZD falling in the 15 minutes before 10:00 Sydney and recovering after (mid t
8-13 in IS and VAL). D1 shows the dip is tied to the Sydney clock (it is there when 10:00 Sydney is 19:00 or 20:00 New
York, and absent at 18:00 NY in the northern summer, when that is 08:00 Sydney). Its cost is not: in the northern
winter (Sydney on AEDT, New York on EST) 10:00 Sydney is 18:00 NY, the last minute of the wide-spread hour after IC's
17:00 NY rollover, and the round trip there costs 2.8 bp IS / 5.2 bp VAL instead of 1.2 / 1.0. Skipping those days and
using the cheaper of the two pairs (AUDUSD, the J5 "cheapest symbol" idea) leaves the mid edge and removes most of the
spread. The 0.6 bp commission remains.

## Rule (exact)
- Symbol: AUDUSD only. Side: short (fixed since round 4). Lot: fixed default lot (no capital dependence; no scaling).
- Day: every weekday (Sydney date d, Mon-Fri; 24 Dec - 2 Jan excluded) on which 10:00 Australia/Sydney falls at or
  after 18:30 America/New_York, i.e. from the US DST start (2nd Sunday of March) to the US DST end (1st Sunday of
  November). No Australian holiday filter (as tested).
- Entry: sell at market at 09:45:00 Sydney. Exit: buy at market at 10:00:00 Sydney (send the order so it fills at or
  before 10:00:00; exits 5-10 s late cost ~0.2 bp, see robustness). One position, no stop, no target.
- One bot, one position at a time; hold 15 minutes; no swap (no rollover crossed).

## Numbers (IS 2016-21 / VAL 2022-24; costs: actual tick spread at fill + 0.6 bp commission; t day-clustered)
| measure | IS | VAL |
|---|---|---|
| trades (days) | 1,020 (170 a year) | 510 |
| mid edge per trade | +1.54 bp (t 8.9) | +1.53 (t 7.5) |
| cost per trade | 1.10 | 0.77 |
| net per trade | **+0.44 (t 2.54)** | **+0.76 (t 3.77)** |
| spread x1.5 | +0.19 (t 1.09) | +0.68 (t 3.35) |
| +60 s on both orders | +0.34 (t 2.04) | +0.41 (t 1.83) |
| +60 s and x1.5 | +0.10 | +0.33 |
| winsorised 1/99 % | +0.38 (t 2.58) | +0.78 (t 3.90) |
| per-trade net Sharpe | 0.079 | 0.167 |
| power = Sharpe x sqrt(HOLD trades ~294) | 1.36 | 2.86 |
| day-bootstrap P(mean <= 0) | 0.004 | 0.000 |
| random-entry control (500 seeds: same days, short 15 min at random starts 18:30-21:45 NY outside the open) | beats 100 % (random mean -1.00) | beats 100 % (-0.68) |
| years net > 0 | 2016 -0.39, 2017 +0.11, 2018 +0.26, 2019 +0.87, 2020 +1.32, 2021 +0.46 | 2022 +1.75, 2023 +0.48, 2024 +0.06 (8/9 years > 0) |
| time placebos (same rule at -60/-30/+30/+60 min) | net -2.01 / -1.05 / -0.99 / -0.57 | -1.76 / -0.85 / -0.90 / +0.23 |
| C3 correlation (IS+VAL) | daily +0.004, monthly -0.08 | |

Robustness to the exact second (ticks, 5 entry x 7 exit offsets, -60..+60 s): all 35 combinations net > 0 in both
eras; exits at or before 10:00:00 give IS t 2.3-3.1 and VAL t 2.9-3.7, exits 5-60 s after give IS t 1.2-2.2.

## Bars
- LIVE: IS t 2.54 >= 2.5, VAL 3.77 >= 1.5, years 8/9, control 100 %, stress > 0: met; **power 1.36 (IS size) to 2.86
  (VAL size) < 3: not met.** LIVE is not reachable in the 21-month HOLD unless the VAL-size edge holds.
- DEMO: IS t >= 2.0, VAL net > 0, control >= 90 %, x1.5 and +1 min > 0: met.
- Cells and chance: stream J declared 70 cells, plus J1b (4) and the post hoc J5c path (2 legs x 2 executions x 3
  symbol sets = 12, after D1's 10 descriptive groups). For K = 12-22, the 95th percentile of max |t| of K normals is
  2.85-3.05; IS t 2.54 alone is inside that range, the pooled IS+VAL t is 4.09 (1,530 days). This is a lead whose
  edge (the Sydney dip) is beyond chance since round 4; what is new and post hoc is only the cost filter.

## Expected counts
- HOLD (2025-01-01..2026-09): eligible weekdays 2025-03-10..2025-10-31 (~168) and 2026-03-09..end of HOLD (~140):
  ~300 trades. Expected HOLD t = Sharpe x sqrt(300): 1.4 at the IS size, 2.9 at the VAL size.
- Demo: ~170 trades a year (weekdays from early March to early November).

## Decision rules (proposed)
- HOLD test (lead): one pass, the rule above at IC's actual HOLD spreads; report net, day-clustered t, cost per trade,
  and the same at x1.5 and +60 s.
- Promotion: HOLD + demo pooled day-clustered t >= 2.5 (net of realised costs), with net > 0 at x1.5.
- Stop (demo): stop after >= 100 demo trades if the pooled net t <= -1.0, or if the realised mean round-trip cost
  exceeds 1.5 bp (the mid edge; above it the rule cannot be net positive).
- Not to be changed after registration: the symbol, the side, 09:45:00 / 10:00:00 Sydney, the NY-clock day filter,
  the fixed lot.
