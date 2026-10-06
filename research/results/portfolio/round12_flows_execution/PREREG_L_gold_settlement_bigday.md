# Pre-registration L (round 12): gold momentum into the COMEX settlement on top-decile move days

Registered 2026-10-06 01:10 UTC by the round-12 lead, before any HOLD (2025-01-01 onwards) number of this rule was
computed. Built from stream L's draft ([PREREG_DRAFT_L_gold_settlement_bigday.md](PREREG_DRAFT_L_gold_settlement_bigday.md):
mechanism, evidence, multiple testing, known weaknesses). HOLD is opened once with `prereg_code/hold_L.py.txt hold`.

**Bar: DEMO.** LIVE is out of reach: power 1.6 IS / 1.3 VAL at ~25 trades a year (LIVE needs 3).

## Rule
- XAUUSD (IC), NYSE business days (`prereg_code/nyse_holidays.json`), New York clock, DST-aware. Quotes are the
  close of the last M1 bar ending at or before the stated time; mid = (bid + ask) / 2.
- S(d) = mid at 13:30:00 ET. sd(d) = sd of the previous 60 daily log returns ln S(k)/S(k-1) (day d excluded).
- z(d) = ln(mid at 13:14:00 ET on d / S(d-1)) / sd(d).
- thr(d) = 90th percentile of |z| over the previous 250 business days (at least 60), day d excluded.
- If |z(d)| > thr(d): at 13:15:00 ET enter at market in the direction of sign(z(d)); exit at market at 13:30:00 ET.
  Fixed default lot, no stop, one position, no swap. Costs: half the spread at entry + half at exit + 0.6 bp.

## Code
- `research/results/portfolio/round12_flows_execution/prereg_code/hold_L.py.txt` 77e6032226a9aea3
- `research/results/portfolio/round12_flows_execution/prereg_code/nyse_holidays.json` 6edaa8bad4edd48a

The lead's implementation on the IC M1 cache (`prereg_code/check_L_output.txt`): IS 150 trades, net +3.48 bp
(t 3.19, per-trade Sharpe 0.26), 4/6 years > 0; VAL 78 trades, net +2.11 (t 1.70), 3/3 years. Stream L's panel
version: IS +3.31 (t 3.02), VAL identical. Spread x1.5 IS +3.07 / VAL +1.90; entry 1 minute later (13:16, same exit)
+3.20 / +1.99. Random-entry control (stream L, look-ahead-free, side recomputed at the random time): beats 99.4 % IS,
90.6 % VAL. Correlation with C3: daily +0.015, monthly -0.14.

## Verdict rules for HOLD (2025-01-02..2026-09-24, the M1 cache's last day)
- Expected ~43 trades; expected HOLD t 1.3-1.6 if the IS/VAL effect holds, so HOLD cannot confirm it alone.
- **Reject** if HOLD net per trade <= 0 at the registered costs.
- Otherwise **DEMO candidate** (demo account only, fixed small risk, ~25 trades a year, at most one a day):
  - Stop rule: stop if, after 40 demo trades, the pooled HOLD + demo net t < 0; report as an execution failure any
    trade that loses more than 5x the median absolute trade P&L because of a fill problem (spread > 3 bp at 13:15 or
    13:30 ET).
  - Promotion rule to LIVE: HOLD + demo pooled day-clustered net t >= 2.5 at the IC costs actually paid.
- Reported regardless: by year, long/short split, spread x1.5, +1 minute, the trade list.

## HOLD result (run once, 2026-10-06 01:10 UTC; output in `prereg_code/hold_L_output.txt`)
46 trades (32 in 2025, 14 in 2026). Mid +2.54 bp, cost 0.86, **net +1.68 bp per trade** (t 0.37, per-trade Sharpe
0.05); spread x1.5 +1.55, entry 1 minute later +0.55. Both years > 0 (2025 +0.89, 2026 +3.49). Short trades +11.42,
long trades -6.49 (IS/VAL also had the edge mostly on the short side). Win rate 57 %, median trade +3.12.
Descriptive, not registered: three trades decide the mean (2026-01-30 +135, 2025-04-09 -96, 2026-02-03 -71); 2.5 %
winsorised mean +0.23 (t 0.07); the mean without the 3 best and 3 worst +2.10.

**Verdict: DEMO candidate** (registered rule: reject only if net per trade <= 0; it is > 0). Not LIVE: HOLD t 0.37
and power far below 3. HOLD adds almost no evidence either way; the demo has to decide it under the stop and
promotion rules above. Pooled IS + VAL + HOLD (not a registered test): 274 trades, net about +2.8 bp per trade.
No cBot is written and nothing is deployed without the user.
