# Pre-registration J (round 12): AUDUSD Sydney-open dip outside IC's rollover hour

Registered 2026-10-06 01:21 UTC by the round-12 lead, before any HOLD (2025-01-01 onwards) number of this rule was
computed. Built from stream J's draft ([PREREG_DRAFT_J_sydney_aud_offroll.md](PREREG_DRAFT_J_sydney_aud_offroll.md):
mechanism, the rollover-hour diagnostic, post-hoc disclosure, robustness to the exact second). HOLD is opened once with
`prereg_code/hold_J.py.txt hold`.

**Bar: DEMO.** On IS/VAL it meets every LIVE condition except power: IS t 2.54 (>= 2.5), VAL t 3.77 (>= 1.5), 8/9
years > 0, random entries beaten 100 % in both eras, > 0 at spread x1.5 and +1 minute; but power is 1.36 at the IS
Sharpe and 2.86 at the VAL Sharpe (needs >= 3), so the LIVE bar does not allow its holdout. The day filter is post
hoc (VAL was seen when it was formed); it selects on IC's rollover schedule, a cost known in advance, not on returns.

## Rule
- AUDUSD, short only, fixed default lot, one position, no stop, no swap.
- Day: Sydney date d, Monday-Friday, 24 Dec - 2 Jan excluded, on which 10:00 Australia/Sydney falls at or after
  18:30 America/New_York (in practice the US DST season, about March to early November).
- Sell at market at 09:45:00 Sydney, buy back at market at 10:00:00 Sydney. Quotes: close of the last M1 bar ending
  at or before the time (at most 10 minutes stale, otherwise no trade); cost = half spread in + half out + 0.6 bp.

## Code
- `research/results/portfolio/round12_flows_execution/prereg_code/hold_J.py.txt` 940cb7ab32e1f32e

The lead's implementation on the M1 cache (`prereg_code/check_J_output.txt`) reproduces stream J's tick numbers:
IS 1,020 trades, mid +1.54, cost 1.10, net +0.44 bp (t 2.54); VAL 510, +1.53 / 0.77 / +0.76 (t 3.77); x1.5 +0.19 /
+0.68; +1 minute +0.34 / +0.41. Correlation with C3 (stream J): daily +0.004, monthly -0.08.

## Verdict rules for HOLD (2025-01-01..2026-09-24, ~300 trades expected)
- **Reject** if HOLD net per trade <= 0 at the registered costs.
- Otherwise **DEMO candidate** (demo account only, fixed small risk, ~170 trades a year):
  - Stop rule: after >= 100 demo trades, stop if the pooled HOLD + demo net t <= -1.0 (not <= 0 already) or if the
    realised mean round-trip cost on the demo exceeds 1.5 bp.
  - Promotion rule to LIVE: HOLD + demo pooled day-clustered net t >= 2.5 at the costs actually paid, net > 0 at
    spread x1.5, and at least 100 demo trades (so real fills and spreads at 09:45 / 10:00 Sydney are measured).
- Reported regardless: t, Sharpe, per year, x1.5 and +1 minute; HOLD Sharpe x sqrt(trades) for the record.

## HOLD result (run once, 2026-10-06 01:21 UTC; output in `prereg_code/hold_J_output.txt`)
314 trades. Mid +0.48 bp (a third of IS/VAL's +1.53), cost 0.73, **net -0.25 bp per trade** (t -0.99); spread x1.5
-0.32, +1 minute -0.26; 2025 -0.41, 2026 -0.07.

**Verdict: rejected** (registered rule: net per trade <= 0). The cost filter worked as designed (0.73 bp, as in
VAL); the Sydney dip itself shrank in 2025-26.
