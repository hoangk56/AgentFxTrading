# Pre-registration I (round 12): month-end post-fix USD reversal after large US equity months

Registered 2026-10-06 01:08 UTC by the round-12 lead, before any HOLD (2025-01-01 onwards) number of this rule was
computed. Built from stream I's draft ([PREREG_DRAFT_I_month_end_post_fix_usd.md](PREREG_DRAFT_I_month_end_post_fix_usd.md),
which has the mechanism, the evidence table and the known weaknesses); this file fixes the rule, the code and the
verdict rules. HOLD is opened once, with `prereg_code/hold_I.py.txt` run as `hold`.

**Bar: DEMO.** LIVE is out of reach: VAL month-clustered t is 0.84 (LIVE needs >= 1.5), and HOLD has ~10 events.

## Rule
- Day T: the last weekday of the calendar month that is not an England bank holiday and not 25 Dec / 1 Jan
  (`prereg_code/eng_holidays.json`).
- Signal r_US = ln(US500 mid at 16:00 New York on the weekday before T / US500 mid at 16:00 New York on the previous
  month's T); the mid is the last M1 bar closing at or before that time.
- Gate: trade only if |r_US| >= 0.024471581800513734 (the IS 2016-21 median, fixed).
- Side: r_US > 0 -> buy USD (sell EURUSD, buy USDJPY, sell GBPUSD); r_US < 0 -> sell USD on the same three pairs.
- Entry at 16:00:00 London (DST-aware), exit at 17:00:00 London the same day, market orders, 1x default lot each,
  one bot, 3 positions at most. No overnight, no swap. Costs: half the actual spread at the entry and exit minute
  each + 0.6 bp commission per round trip.

## Code
- `research/results/portfolio/round12_flows_execution/prereg_code/hold_I.py.txt` cb21b81cf55b9677
- `research/results/portfolio/round12_flows_execution/prereg_code/eng_holidays.json` 79960633de8fe5a7
- `research/results/portfolio/round12_flows_execution/prereg_code/check_I_panel.py.txt` c0d182e671d8be95 (the lead's
  independent recomputation on the shared panel; it reproduces stream I exactly)

`hold_I.py check` on the IC M1 caches (2016-2024, cut at load) gives IS 35 events / 105 trades, net +6.73 bp per
trade, month-clustered t 3.66; VAL 24 / 72, +1.68, t 0.84; +1 minute and spread x1.5 IS +6.50 / VAL +1.38. The panel
version has 36 IS events: 2019-07-31 has |r_US| = 2.447 %, equal to the threshold within float32 rounding, and falls
just below it on the float64 M1 cache. No other difference.

## Status against the DEMO bar on IS / VAL
- IS month-clustered t 3.79 (>= 2.0): met. VAL net +1.68 bp per trade (> 0): met. Spread x1.5 and +1 minute: > 0 in
  both eras: met. Years net > 0: 6/6 IS, 2/3 VAL.
- Random-entry control (500 seeds, same side and pairs on random ordinary business days, same window): beats 100 %
  IS, 86 % VAL, 100 % IS + VAL pooled. The bar is read on the pooled sample, as for earlier candidates; VAL alone is
  below 90 %, disclosed here as a weakness.
- Selection: the best of 27 pre-declared basket cells by IS t (permutation null 95th percentile 3.11, observed 4.17,
  p 0.002); VAL was visible when it was picked. Correlation with C3 (IS + VAL): daily -0.05, monthly +0.01.

## Verdict rules for HOLD (2025-01..2026-08: 20 month-ends; 2026-09-30 is after the cache's last day, 2026-09-24)
- Expected: ~10 gated events, ~30 trades. Expected HOLD t on the VAL effect size is ~0.5, so HOLD cannot confirm it.
- **Reject** if the registered net per trade over HOLD is <= 0.
- Otherwise **DEMO candidate**: demo only, fixed small risk, ~6 events (~18 trades) a year.
  - Stop rule: stop the demo if, after >= 12 pooled (HOLD + demo) events, the pooled mean net per event is <= 0, or
    at any time the pooled month-clustered t < -1.5.
  - Promotion rule to LIVE: HOLD + demo pooled month-clustered t >= 2.5 (and per-trade net > 0 at the demo's
    measured spreads and slippage).
- Reported regardless: per event list, +1 minute and spread x1.5 versions, per pair.

## HOLD result (run once, 2026-10-06 ~01:08 UTC; output in `prereg_code/hold_I_output.txt`)
12 of 20 month-ends passed the gate, 36 trades. Mid +0.43 bp per trade, cost 0.66, **net -0.23 bp per trade**
(-0.68 per event, month-clustered t -0.08); spread x1.5 -0.25, +1 minute -0.13; per pair EURUSD +0.17, USDJPY -0.74,
GBPUSD -0.11. Up months (9) and down months (3) both near zero; 2025-06 and 2025-03 lost 60-50 bp per event,
2025-09 and 2026-08 won 44-35.

**Verdict: rejected** (registered rule: net per trade <= 0). No demo. The decay seen from IS (+6.8) to VAL (+1.7)
continued to ~0 in 2025-26, as round 3's unconditional F1 did from 2021.
