# PREREG (round 24, lead): one HOLD look each for FOMC_A4 and F3. Tier RELAXED

Registered 2026-10-15 12:19 UTC (`date -u`), before any 2025-26 price was loaded for these rules. Rules exactly as
in [PREREG_DRAFT_C_fomc_dollar_short.md](PREREG_DRAFT_C_fomc_dollar_short.md) and F3 of
[PREREG_DRAFT_C_ecb_window_variants.md](PREREG_DRAFT_C_ecb_window_variants.md); nothing changed or chosen here. The
user allowed relaxed conditions for round 24 ([BRIEF.md](BRIEF.md), item 3: HOLD may be opened once for a RELAXED
candidate after a draft). Only F3 is opened from the ECB-window family, as the draft recommends; F2, F4 and F5 stay
closed (E1's HOLD, opened 2026-10-06, already measures that window).

## What is looked at
- HOLD = 2025-01-01..2026-09-24 (end of the IC M1 cache), panel of 7 USD pairs built from research/data/m1 for
  2024-01-01..2026-09-24 by `build_panel_hold.py` (2024 only feeds F3's causal 250-day selector; no 2024 trade is
  reported).
- FOMC_A4: the 14 scheduled statement days in HOLD (Fed calendar fetched 2026-10-15). Counted from the rate files
  before registration (no prices): 8 have at least one currency above USD (2025-01-29 GBP; 2025-12-10 and the six 2026
  meetings GBP + AUD); the other 6 have no trade. Expected HOLD t: 1.41 at the VAL size (Sharpe 0.50 x sqrt 8),
  0.92 at round 18's 0.65 retention. HOLD can only reject, not confirm.
- F3: ~119 expected trades; expected HOLD t 1.98 at the VAL size, 1.14 at 0.65 retention.

## Bars (fixed now)
- Each rule: **reject if HOLD net per trade <= 0** at the registered costs (half spread at each fill + 0.6 bp per
  leg + swap). Otherwise it stays a RELAXED candidate eligible for a small fixed-risk demo, with the stop and
  promotion rules of its draft (promotion to LIVE only at HOLD + demo pooled day-clustered net t >= 2.5).
- Reported but not gating: x1.5 spread, +1 minute on both fills, per year.

## Check run (IS/VAL on the 2016-24 panel, before HOLD; matches stream C exactly)
See [prereg_code/check_output.txt](prereg_code/check_output.txt): A4 IS n 37 net +21.62 (t 1.90), VAL n 23 +31.60
(t 2.40); F3 IS n 381 +2.39 (t 3.29), VAL n 207 +3.01 (t 2.60).

## Code (sha256, first 16 hex; do not edit before the HOLD run)
- `research/results/portfolio/round24_relaxed/prereg_code/hold_r24.py.txt` a301d4d13bbeeb11
- `research/results/portfolio/round24_relaxed/prereg_code/clib.py.txt` e66aa4f31f7e29c2
- `research/results/portfolio/round24_relaxed/prereg_code/eng.py.txt` beb456eba773d396
- `research/results/portfolio/round24_relaxed/prereg_code/build_panel_hold.py.txt` 0adfdfdee9a30366
- `research/swing/rates.py` d5ec1cd0fd79819d
- `research/swing/swing.py` 8511bfbae1366fc4

Run: `R24_PANEL=<scratchpad>/r24/lead/hold/panel_hold PYTHONPATH=. research/.venv/bin/python hold_r24.py hold`.

## HOLD result
(appended after the run, below this line; nothing above edited)

Run 2026-10-15 12:19:39 UTC with the hashed code (`cmp` against prereg_code/ before the run; output in
[prereg_code/hold_output.txt](prereg_code/hold_output.txt)). A first call at 12:19:33 failed on an import path (it
ran the `.txt` copy; nothing was computed or printed) and was rerun from the identical scratchpad file.

| rule | HOLD n | mid (t) | net (t) | x1.5 | +1 min | by year (net / n) | verdict |
|---|---|---|---|---|---|---|---|
| FOMC_A4 | 10 | -33.64 (-2.29) | **-34.63 (-2.36)** | -34.68 | -35.02 | 2025 -7.34 / 4, 2026 -52.83 / 6 | **rejected** (net <= 0) |
| F3 | 117 | +2.63 (2.85) | **+2.00 (2.16)** | +1.98 | +1.40 | 2025 +4.02 / 69, 2026 -0.91 / 48 | **passes** the registered bar; stays RELAXED |

- Disclosure: the pre-registration counted 8 A4 events; the rule traded 10. The count rounded the rates to two
  decimals before comparing them with USD's, which hid GBP (and AUD in January) above USD's 4.33 % in January-May 2025.
  The rule and code did not change. At 10 events the expected HOLD t was 1.58 at the VAL size; the result is -2.36.
- A4: the dollar rose on HOLD FOMC days against the higher-rate legs, most in 2026 (GBP + AUD legs). Round 20's
  pooled 2004-24 t 3.25 does not carry into 2025-26.
- F3: HOLD keeps 0.66 of the VAL net (2.00 / 3.01), close to round 18's 0.65 for declared rules. HOLD per-trade Sharpe
  0.20; its HOLD t 2.16 is close to the expected HOLD t at the VAL size (1.98), above the 1.14 expected at 0.65
  retention (HOLD is less noisy than VAL: sd 10.0 vs 16.7 bp). The +1 minute check falls to +1.40 and
  2026 is negative (-0.91, n 48): the effect is weakening. E1, which F3 filters, had HOLD net +0.64 (t 0.99), so the
  USD-TOP filter tripled E1's HOLD net per trade.
- Pooled IS + VAL + HOLD (F3): IS +2.39 (n 381), VAL +3.01 (n 207), HOLD +2.00 (n 117). LIVE needs HOLD + demo pooled
  t >= 2.5 (the promotion rule in the draft); F3 is a RELAXED demo candidate only.
