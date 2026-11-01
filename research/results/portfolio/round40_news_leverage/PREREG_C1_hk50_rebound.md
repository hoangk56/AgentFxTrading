# Pre-registration: HK50 rebound after a mainland deleveraging day (round 40 C, post-hoc mirror of C1_k1.5 HK50 h1)

Registered 2026-10-29 17:12 UTC (`date -u`; the user's local date is 2026-10-30), after the user approved one HOLD look
on 2026-10-30. **Written before any 2025+ margin or price data was fetched or loaded.** The local IC HK50 M1 cache was
checked for its last bar time only (2026-09-24 18:53 UTC). No 2025+ price or margin value was read.

## Status: post hoc
- The side (LONG HK50) was chosen **after seeing IS and VAL**. The declared side in [HYPOTHESES_C.md](HYPOTHESES_C.md)
  was the opposite (short, continuation), and it lost: [STREAM_C.md](STREAM_C.md).
- Per research/PROMPT.md "Bài học vòng 18", post-hoc rules kept only 19-31 % of their VAL size in holdout. The
  expected HOLD t is therefore given at 1/4 of the VAL size as well as at the VAL size.

## Rule: one cell, no variants, no parameter choice
- **Data.** SSE + SZSE combined margin totals (Eastmoney `RPTA_RZRQ_LSHJ`): RZYE (financing balance) and ZDF (CSI 300
  daily % change) for CN trading day D.
- **Signal (C1_k1.5, unchanged).** g_D = RZYE_D / RZYE_{D-1} - 1. z60(g_D) is the z of g_D against the 60 CN trading
  days before D (>= 48 valid). Signal when ZDF_D < 0 and z60(g_D) <= -1.5.
- **Side.** LONG HK50.
- **Entry.** Close of the IC HK50 M1 bar starting 01:45 UTC on CN trading day D+1. Buy at the ask close.
- **Exit.** Close of the 01:45 UTC bar on the next CN trading day after D+1 (h1), capped at 5 x 24 h. Sell at the bid
  close.
- **Fills.** A trade is dropped if either bar is missing within 10 minutes.
- **Costs.** Actual IC spread both legs. Swap per 17:00 NY rollover from `swap_frac_at` (index triple on Friday).
- At most 3 open trades (never binds at h1).
- **Statistic.** Mean net bp per trade; t clustered by episode (signal days within 5 CN days of the previous signal
  form one episode).
- **Eras.** IS 2016-21, VAL 2022-24, HOLD 2025-01-01..2026-09-24. A HOLD signal needs its exit bar inside the data:
  margin through 2026-09-24 and HK50 M1 through 2026-09-24 18:53 UTC.

## Frozen code (`prereg_code_c1/`, sha256)
| file | sha256 |
|---|---|
| lib.py (byte-identical to the grading engine) | 1aff086d7f3e00a44318c1f555ac78693fdc1a407aadda64ecc214ab33fd27f3 |
| sig.py (identical) | c41242a2e4740241274ba28ae6967f61ceac8cbe93ea1ec1e7809bcf92114e91 |
| engine.py (identical) | 18fdfdc1c09270ed11bf6ec5160c73b362d77d53ab94ffdbfd6cf6773ca6ed3a |
| run_c1.py (the runner for this cell only) | 4598c1a7b0275e30b0267da3d195f4a770cee5ddbe98f3408f66c9a9ea7364d1 |

- **How it runs.** `research/.venv/bin/python -I .../prereg_code_c1/run_c1.py hold` will be run once, unchanged. It
  reads the existing margin pages (`web/em_lshj/`) plus the new 2025-26 pages (`web/em_hold/`) from the stream C
  scratchpad, and cuts at 2026-09-24.
- **What it computes.** Only this cell: only HK50, only h1, only C1_k1.5 signal days. No random control and no other
  variant is run on 2025+ data.
- **Dry run.** `run_c1.py dry` (margin and prices cut at 2024-12-31) reproduces the graded mirror: mid +41.09 / +46.51
  bp, matching the short cell's -41.1 / -46.5.

## IS / VAL (dry run, before HOLD)
| era | trades / episodes | mid bp | net bp (t) | sd | per-trade Sharpe | win |
|---|---|---|---|---|---|---|
| IS 2016-21 | 53 / 35 | +41.09 | +35.38 (2.14) | 119.4 | 0.296 | 0.66 |
| VAL 2022-24 | 29 / 15 | +46.51 | +41.11 (0.77) | 274.2 | 0.150 | 0.45 |

- VAL's mean is carried by a few large 2022 trades: its sd is 2.3x IS and its win rate is below one half.

## HOLD expectation (fixed now)
- **Expected HOLD trades.** 9.1 a year x 1.73 years = **~16 trades, ~10 episodes** (5.6 a year).
- **Expected HOLD t:**

  | effect size | expected HOLD t |
  |---|---|
  | VAL size (Sharpe 0.150) | 0.150 x sqrt(16) = **0.60** (~0.47 on 10 episodes) |
  | 1/4 of the VAL size (Sharpe 0.037) | **0.15** |
  | IS size (Sharpe 0.296), for information | 1.18 |

- **HOLD power** (per-trade net Sharpe x sqrt(HOLD trades)) is 0.60 at the VAL size and 0.15 at 1/4 of it.
- **LIVE is out of reach by power.** It needs >= 3, which would take a per-trade Sharpe of 0.75 on 16 trades. The best
  possible outcome of this look is the DEMO tier.
- At the VAL size the pass rule below has roughly a 1-in-3 chance even if the effect is real; at 1/4 of the VAL size,
  roughly 1 in 5.

## Pass rule for HOLD (fixed now)
- **HOLD net > 0 and HOLD t (episode-clustered) >= 1.0 on this cell -> DEMO candidate.** A DEMO candidate still needs
  the DEMO pre-registration items (demo trades a year ~9, stop rule, promotion "HOLD + demo pooled t >= 2.5") before
  any demo run.
- **Otherwise: fail, and the rule is dropped for good** (no re-run with other thresholds, horizons or symbols).
- IS + VAL + HOLD pooled numbers are reported for information only. They do not change the verdict.

## HOLD result (appended 2026-10-29 17:18 UTC, `date -u`)
- **Inputs.** Eastmoney `RPTA_RZRQ_LSHJ` 2025-01-02..2026-09-24: 421 CN days in 3 pages of 200 rows, 0 rows outside
  the span, requests logged. IC HK50 M1 from the local cache, which ends 2026-09-24 18:53 UTC. No new IC pull.
- **Run.** The frozen code was run once, unchanged (sha256 prefixes checked before the run: engine 18fdfdc1c09270ed,
  lib 1aff086d7f3e00a4, run_c1 4598c1a7b0275e30, sig c41242a2e4740241). IS / VAL reproduce the dry run exactly.
  Output: scratchpad `r40/C/out/prereg_c1_hold.json`.

| era | trades / episodes | mid bp | net bp (t, episode-clustered) | sd | per-trade Sharpe | win |
|---|---|---|---|---|---|---|
| IS 2016-21 | 53 / 35 | +41.09 | +35.38 (2.14) | 119.4 | 0.296 | 0.66 |
| VAL 2022-24 | 29 / 15 | +46.51 | +41.11 (0.77) | 274.2 | 0.150 | 0.45 |
| **HOLD 2025-01..2026-09-24** | **24 / 17** | +24.95 | **+19.00 (0.74)** | 132.4 | 0.144 | 0.75 |
| IS + VAL + HOLD (information) | 106 / 67 | +38.92 | +33.24 (1.92) | 176.1 | 0.189 | 0.62 |

**Verdict: FAIL.** HOLD net is > 0, but HOLD t is 0.74 < 1.0. Under the pass rule fixed above, the rule is dropped for
good.
- HOLD gave 24 trades against the ~16 expected.
- The HOLD per-trade Sharpe (0.144) is about the VAL size (0.150), above the 1/4-of-VAL expectation, and the t is about
  what the VAL size predicted (0.60 on 16 trades). The sign held in all three eras, but the size is far too small
  for its count.
- The pooled t is 1.92 on 106 trades over 9.7 years. Even at that size, LIVE would need ~250 HOLD trades.
