# Draft pre-registration: gold after a surge or collapse in Chinese net short sales (round 40 C, cell C3_k2 XAUUSD h1). NOT RECOMMENDED

Draft written 2026-10-29 14:28 UTC (`date -u`) by stream C. **HOLD (2025-01..2026-09) has not been opened.** The rule
was declared in [HYPOTHESES_C.md](HYPOTHESES_C.md) at 14:23 UTC, before any return. It is one of 147 graded-or-declared
cells (24 in family C3). Details: [STREAM_C.md](STREAM_C.md).

It meets the DEMO numbers on IS / VAL (IS net t 2.73 >= 2.0, VAL net > 0, random entries beaten 1.00 in IS, positive
at spread x1.5 and +1 minute). **Stream C recommends not registering it.**
- The IS t (2.73) sits at the median of the best |t| among 120 normals (2.76); the family-of-24 chance p is ~0.14.
- Gold was a declared weak-prior target, and the mechanism linking A-share short sales to gold is thin.
- PRE 2012-15 is negative (net -13.2 bp, t -1.00; without 2015 -14.8, t -0.86).
- VAL is +8.9 bp (t 0.72), VAL random control 0.59, and VAL turns negative without its 3 best trades (-2.7 bp).
- HOLD power at the VAL size is ~0.64 (25 expected HOLD trades), and the lending market was suspended or curbed in
  2023-10 / 2024, so the signal's source changed before HOLD.

The draft exists because the process asks for one whenever a declared cell meets a bar.

## Rule (exactly as tested)
- **Data.** SSE + SZSE combined margin totals, Eastmoney `RPTA_RZRQ_LSHJ`: `RQJMG` (net short sales in shares, sell
  minus repay) and `RQYL` (short balance in shares) for CN trading day D.
- **Signal.** n_D = RQJMG_D / RQYL_{D-1}; z_D = (n_D - mean) / sd over the 60 CN trading days before D (>= 48 valid).
  Trade when |z_D| >= 2.
- **Side.** z_D > 0 (net short selling surge, risk-off) -> **long XAUUSD**; z_D < 0 (heavy covering, risk-on) -> **short
  XAUUSD**. From the declared mechanism (informed short sellers, continuation; gold as haven), not from IS.
- **Entry.** Close of the 01:45 UTC M1 bar on D+1 (the next CN trading day; the exchanges publish D's totals before
  D+1's open). Buy at ask, sell at bid.
- **Exit.** 01:45 UTC on the next CN trading day after D+1 (h1), capped at 5 x 24 h. No stop.
- At most 3 open trades (never binds at h1).
- Costs: IC spread at the minute, swap from `swap_frac_at` per 17:00 NY rollover (Wednesday triple), no commission.

## Numbers
| reading | IS 2016-21 | VAL 2022-24 | PRE 2012-15 (Dukascopy bid, IC 2016-17 cost) |
|---|---|---|---|
| trades / episodes | 89 / 48 | 41 / 25 | 65 / 42 |
| long share | 0.49 | 0.39 | |
| mid, bp (t, episode-clustered) | +25.1 (2.87) | +9.1 (0.72) | -11.8 (-0.89) |
| net, bp (t) | **+23.8 (2.73)** | **+8.9 (0.72)** | -13.2 (-1.00); without 2015 -14.8 (-0.86) |
| spread x1.5 / +1 min / entry 05:00 UTC | +23.4 / +25.0 / +16.3 | +8.6 / +8.4 / +11.3 | |
| without 2020-03/04 | +22.8 (2.62) | | |
| years > 0 | 6/6 | 2/3 (2024 -6.7) | 1/4 |
| per-trade Sharpe; power at the era rate | 0.279; 1.41 | 0.127; 0.62 | |
| random entries beaten (200 draws, side from z's sign on the drawn day) | 1.00 | 0.59 | |
| without the 3 best trades | +14.0 | -2.7 | |

By arm (net bp, t): risk-off long IS +38.6 (2.64), VAL +14.7 (1.23); risk-on short IS +9.4 (1.08), VAL +5.1 (0.28).
The S variant (D+1 01:45 -> 07:59 UTC) is IS +9.6 (t 2.24), VAL +0.4. h3 loses in its risk-on arm (IS -20.4).
Correlation with C3's gotobi basket: daily +0.11, monthly +0.16.

## HOLD expectation, demo, stop and promotion rules (if the lead registers it anyway)
- Expected HOLD trades: ~25 (14.4 a year x 1.73). HOLD t at the VAL size: 0.127 x sqrt(25) = **0.64**; at the IS size
  1.4. Pass rule: HOLD net > 0 (DEMO bar). Net < 0 in HOLD -> drop.
- Demo: ~14 trades a year at a small fixed risk.
- Stop rule (fixed now): after 20 demo trades, stop if the cumulative demo net is below 0.
- Promotion rule: HOLD + demo pooled t >= 2.5. At the VAL size that would take ~25 years of demo.
- Cells tried: 120 declared (C1 48, C2a 24, C2b 24, C3 24) + 27 fallback (F1 18, F2 9).
- Script hashes (sha256, first 16 hex; scratchpad `r40/C/`): lib.py 1aff086d7f3e00a4, sig.py c41242a2e4740241,
  engine.py 18fdfdc1c09270ed, grade.py 212df8ce54b9a992. `research.tools.prereg_hashes` not run (scripts live in the
  scratchpad, not the repo).
