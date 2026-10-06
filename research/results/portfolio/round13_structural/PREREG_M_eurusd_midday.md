# Pre-registration M / E1 (round 13): short EURUSD over the European midday

Registered 2026-10-06 01:40 UTC by the round-13 lead (hashes 01:40:15, HOLD run 01:40:28), before any HOLD (2025-01-01 onwards) number of this rule was
computed. Built from stream M's draft ([PREREG_DRAFT_M_eurusd_midday.md](PREREG_DRAFT_M_eurusd_midday.md): mechanism,
selection path, caveats). HOLD is opened once with `prereg_code/hold_M.py.txt hold`.

**Bar: DEMO.** On PRE/IS/VAL it meets every LIVE condition except power: IS t 3.29 (>= 2.5), VAL t 2.46 (>= 1.5),
years 5/6 IS + 3/3 VAL (11/12 PRE), random entries beaten 100 % IS / 99 % VAL, > 0 at spread x1.5 and +1 minute;
power 1.78 at the IS size and 1.88 at the VAL size (needs >= 3). Expected HOLD t ~1.9 at the VAL size.

## Rule
- EURUSD, short, fixed default lot, one position a day, no stop (the 2-hour hold is the risk control; an emergency
  stop is an operations choice, not tested).
- Days: Monday-Friday by the London date, 24 Dec - 1 Jan excluded, holidays not skipped.
- Sell at market at 11:00:00 Europe/London (DST-aware), buy back at market at 13:00:00 London. Quotes: close of the
  last M1 bar ending at or before the time (at most 10 minutes stale, otherwise no trade); cost = half spread in +
  half out + 0.6 bp commission.
- Side fixed from PRE 2004-15 (Dukascopy), window picked on IS among 500 PRE-carried cells; VAL was in view (disclosed).

## Code
- `research/results/portfolio/round13_structural/prereg_code/hold_M.py.txt` e5c605028b7bd70b

The lead's implementation (`prereg_code/check_M_output.txt`) reproduces stream M exactly: IS 1,525 trades, mid
+1.80, cost 0.63, net +1.17 bp (t 3.29); VAL 765, +1.97 / 0.62 / +1.35 (t 2.46); x1.5 +1.15 / +1.34; both fills
+1 minute +1.08 / +1.04. Correlation with C3 (stream M): +0.043 daily, +0.055 monthly.

## Verdict rules for HOLD (2025-01-01..2026-09-24, ~440 trades)
- **Reject** if HOLD net per trade <= 0 at the registered costs.
- Otherwise **DEMO candidate** (demo account only, fixed small risk, ~250 trades a year):
  - Stop rule: after >= 100 demo trades, stop if the pooled HOLD + demo net t <= -1.0, or if the realised mean
    round-trip cost on the demo exceeds 1.5 bp.
  - Promotion rule to LIVE: HOLD + demo pooled day-clustered net t >= 2.5 at the costs actually paid, net > 0 at
    spread x1.5, and at least 100 demo trades.
- Reported regardless: t, per-trade Sharpe, by year, x1.5 and +1 minute; HOLD Sharpe x sqrt(trades).

## HOLD result (run once, 2026-10-06 01:40 UTC; output in `prereg_code/hold_M_output.txt`)
444 trades. Mid +1.28 bp (VAL +1.97, IS +1.80), cost 0.64, **net +0.64 bp per trade** (t 0.99, per-trade Sharpe
0.047, Sharpe x sqrt(444) = 0.99); spread x1.5 +0.62; **both fills one minute late -0.00**; 2025 +1.37, 2026 -0.34.

**Verdict: DEMO candidate** (registered rule: reject only if net per trade <= 0). Weak: the HOLD edge is two thirds
of VAL's, and the +1 minute version is zero, so most of the HOLD edge sat in the entry or exit minute. Pooled
IS + VAL + HOLD (not a registered test): 2,734 trades, net about +1.1 bp. Not LIVE. No cBot, nothing deployed.
