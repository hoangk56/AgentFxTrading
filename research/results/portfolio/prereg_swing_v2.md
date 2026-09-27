# Pre-registration — swing lab v2 holdout (research/scan/swing.py)

Written before the holdout (2025-01-01 .. 2026-09-24) of the candidate below was computed. Nothing about the
candidate may change after its holdout is seen; a failed candidate is reported as failed.

Common to every candidate: `research/scan/swing.py` at the hashes listed at the end — per-symbol bots, cap 3 positions (up to 3
in the same symbol), hold <= 5 calendar days, lots = $100 default risk x a 0.5-2x causal strength multiplier,
real bid/ask from the M1 cache (1x), commission per research/specs + research/scan/specs_ext, swaps from
research/scan/rates.py (historical short rates + markup fitted to IC's 2026 swaps; crypto/energy at IC's 2026
fraction). Eras: IS 2016-2021 (selection), VAL 2022-2024 (validation), HOLD 2025-01..2026-09 (this file).

Pass bar at HOLD (all of): net $ > 0; mean R > 0; both symbols' net $ not both negative. Reported alongside,
not judged: t, per-symbol, long/short split, max drawdown, 1.5x spread stress.

## C1 — Crypto Donchian breakout, H4 (registered 2026-09-27, before its HOLD run)

- Symbols / bots: BTCUSD, ETHUSD, one bot each.
- Bars: H4 (UTC-aligned, stubs merged).
- Entry: on an H4 close above the prior 55-bar high -> buy; below the prior 55-bar low -> sell. Every qualifying
  bar is an entry (the cap of 3 per bot turns a persistent breakout into up to 3 staggered units).
- Exit: first of stop (3 x ATR(20) of H4 from the fill), an H4 close below the prior 20-bar low (longs) / above
  the prior 20-bar high (shorts), or 5 days.
- Lot: risk $100 x clip(breakout distance in ATR / causal median of earlier breakout distances, 0.5, 2).
- Chosen by IS t among 12 Donchian configs (n 20/55, exit 10/20, shorts on/off, D1/H4) — all 12 were positive in
  IS and VAL; 64 time-series-trend configs were run on the same symbols first (76 crypto configs in all).
- IS (2018-2021): n 553, R +0.276, t +4.3, 4/4 years positive. VAL (2022-2024): n 413, R +0.227, t +3.3, 3/3.
- Controls done before HOLD: entries delayed 1/2/6 bars decay gradually (R +0.26/+0.18/+0.12 IS), no cliff;
  random same-side entries with the same exits/stops/cap: real beats 20/20 seeds in IS and VAL.
- Secondary (reported, not the registered candidate): the same rule long-only.

Code hashes at registration (sha256, first 16):
- `research/scan/swing.py` e9d80497d33a9d84
- `research/scan/swing_rules.py` 10fd11c9dfa0f90c
- `research/scan/rates.py` 5a84860812283a21
- `research/scan/specs_ext.py` e63964ed74d204b2
- `research/scan/data.py` 763e848464232614
- `research/specs.py` 9ef05930b3f0baf1

### C1 result at HOLD (run once, 2026-09-27): **FAILED** (mean R <= 0)

HOLD n 302, net **+$2,859**, mean R **-0.025** (t -0.3), 2/2 years net positive, max DD $3,578. BTCUSD R -0.151
(net +$380), ETHUSD R +0.123 (net +$2,479). 1.5x spread: R -0.029. Long-only secondary: R -0.012, net +$2,443.
Net $ is positive only because the strength multiplier put larger lots on the trades that won; the bar asked for
mean R > 0 as well, so C1 fails. Not re-tested with any change.

## R-series — retest of the old lab's positive-but-rejected strategies on 2016-2022 (registered 2026-09-27)

These were designed and judged on 2023-01..2026-09 (research/results/lab/main, v2). The 2016-2022 ticks did not
exist when they were designed, so 2016-2022 is out of sample for every one of them. Run with the unchanged lab
code (`python -m research.lab.run`, catalog params, fixed lots, lab costs), years 2016..2022, real variant, 10
random-entry seeds. Strategies: TOM, K2, VB1, LC1, GF1, MEF, X1, N2-GOTOBI, OD1 and the three positive D1 bank
cells BANK-zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0, BANK-rsiR_D1_P2_lo5_H3_SL1.5_TPNone,
BANK-donchR_D1_N10_H6_SL1.5_TPNone (the last holds 6 D1 bars, over the 5-day limit: reported, cannot be
adopted as is).

Pass bar per strategy (all of), pooled over its symbols, 2016-2022: mean R > 0 with t >= 2.0; at least 5 of the
7 years with net > 0; beats >= 90 % of the random-entry seeds on summed R. A pass makes it a candidate for the
same bar on 2023-2026 in the new engine's rules (constraints: <= 5 days, <= 3 positions, risk-scaled lots).

Addendum (registered before its run): N3-IMOM (market intraday momentum, Gao et al. 2018 / Baltussen et al.
2021), same retest protocol and pass bar, run into research/results/lab/retest_2016_2022_n3.

Protocol change (before any R-series result was read; compute time: 3 of 22 jobs done after ~1 h, the random
control re-simulating every tick 10x): the retest runs with 0 seeds on the 15 real symbols only (no synthetic
crosses); the random-entry control (10 seeds) is run afterwards only for strategies that meet the other criteria.

### R-series result (2016-2022, lab code, 15 real symbols, 0 seeds; seeds run for the survivors)

| strategy | n | mean R | t | years net > 0 | seeds beaten | verdict |
|---|---|---|---|---|---|---|
| N2-GOTOBI | 1002 | +0.078 | +5.7 | 7/7 | 100 % (10 seeds) | **PASS** |
| VB1 | 6572 | +0.023 | +1.3 | 5/7 | - | fail (t) |
| BANK-zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0 | 334 | +0.021 | +0.4 | 5/7 | - | fail (t) |
| TOM | 1316 | -0.006 | -0.7 | 2/7 | - | fail |
| MEF | 415 | -0.040 | -0.7 | 2/7 | - | fail |
| K2 | 7138 | -0.034 | -2.0 | 2/7 | - | fail |
| GF1 | 2944 | -0.036 | -2.0 | 1/7 | - | fail |
| BANK-rsiR_D1_P2_lo5_H3_SL1.5_TPNone | 2293 | -0.035 | -2.1 | 3/7 | - | fail |
| BANK-donchR_D1_N10_H6_SL1.5_TPNone | 2242 | -0.053 | -2.5 | 2/7 | - | fail |
| LC1 | 3591 | -0.060 | -7.9 | 0/7 | - | fail |
| OD1 | 3603 | -0.048 | -11.2 | 1/7 | - | fail |
| N3-IMOM (addendum) | 6978 | -0.041 | -8.1 | 2/7 | - | fail |

N2 ported to research/scan/swing.py (`swing_rules.gotobi`, M5 bars, historical swaps, risk-scaled lots): IS R +0.066
(t 4.3, 6/6 years), VAL +0.054 (t 2.6, 3/3), HOLD +0.038 (t 1.3, 2/2) -- N2's HOLD was already seen by the old lab
(+0.035R), so it is reported, not a new test. Placebo (same hours, non-gotobi weekdays): IS -0.012, VAL +0.002.

## C3 — Gotobi JPY basket (registered 2026-09-27, before its HOLD run)

One bot, USDJPY + EURJPY + GBPJPY, cap 3; `swing_rules.gotobi` unchanged on each (long 18:00 -> 00:55 UTC before
the 09:55 Tokyo fix, short 00:55 -> 02:55 UTC, stop 3 x ATR20(H1)), 1x default lot. Chosen on IS/VAL: EURJPY IS
R +0.037 (t 2.8, 6/6), VAL +0.040 (t 2.1, 3/3); GBPJPY IS +0.027 (t 2.1, 6/6), VAL +0.029 (t 1.7, 3/3); AUDJPY
~0 (excluded). EURJPY and GBPJPY HOLD not seen before this registration.

## C4 — Gotobi USDJPY with day-type lots (registered 2026-09-27, before its HOLD run)

`swing_rules.gotobi` on USDJPY; lot = 2x the default on the 20th and the 25th (and those days moved to the Friday
before), 1x on the 15th, 0.5x on the 5th, 10th and the month's last day. The buckets come from IS mean R by day
type (20th +0.171, 25th +0.128, 15th +0.087, 5th +0.032, 10th -0.001, last -0.005); VAL: 20th +0.160, 25th +0.182,
15th +0.032, 5th -0.105, 10th +0.049, last +0.098. USDJPY's overall HOLD mean R was seen (N2); its split by day
type was not.

Pass bar for C3 and C4 at HOLD: as for C1 (net $ > 0, mean R > 0); C3 additionally: EURJPY and GBPJPY each net > 0.

### C3 / C4 results at HOLD (run once, 2026-09-27)

- **C3 PASSED.** HOLD n 738, net +$3,115, mean R +0.042 (t 2.9), 2/2 years, max DD $851; USDJPY +$940 (R +0.038),
  EURJPY +$1,407 (R +0.057), GBPJPY +$769 (R +0.031). IS R +0.043 (t 5.4, 6/6), VAL +0.041 (t 3.7, 3/3).
  1.5x spread: IS +0.034, VAL +0.031, HOLD +0.019 (t 1.2), all eras net > 0.
- **C4 PASSED the bar, sizing not confirmed.** HOLD n 246, net +$757, mean R +0.038 (t 1.3), 1/2 years net > 0,
  max DD $591. The day-type lots made less than 1x lots at HOLD (+$757 vs +$940), so the day-type sizing is not
  supported out of sample; the rule itself (= N2) is.

## Addendum — code provenance (written 2026-09-27, after every HOLD run above; changes no candidate or verdict)

The hashes above were written at 23:58:46 UTC on 2026-09-26, when C1 was registered. `swing.py` and `swing_rules.py`
were edited again before the first commit (`af3ab38`), so the registered versions were never in git. C3 and C4 were
registered at 00:46:08 UTC without hashes of their own.

**Reconstruction.** The session's edit log was replayed backwards from `af3ab38`, undoing the 11 edits made to
these two files after 23:58:46. The result hashes exactly to the registered `e9d80497d33a9d84` / `10fd11c9dfa0f90c`,
so the list of later edits is complete. Those versions are kept in [prereg_swing_v2_code/](prereg_swing_v2_code/)
(named `<file>@<hash>.py.txt`). `research/tests/test_prereg_code.py` checks their hashes, and checks that the other
four files are unchanged in `af3ab38`.

**Timeline (UTC):**

| time | event | effect on the registered candidates |
|---|---|---|
| 23:58:46 | C1 hashes written | — |
| 23:58:54 | **C1 HOLD run** | ran on the registered code: no edit in between |
| 00:02 – 00:17 | `swing_rules`: new rules `carry`, `session_fx`, `day_long` (+ helpers) | new functions only; `donchian` untouched |
| 00:04:54 | `swing.py`: `if ex is None` → `if ex is None or not ex.any()` | fixes an IndexError on an all-False exit array; any run that finished before gives the same result |
| 00:44:59 | `swing_rules`: `gotobi` and helpers added (used for N2, then C3/C4) | before C3/C4 were registered |
| 00:46:08 | C3 / C4 registered (no hashes) | — |
| 00:46:26 | `gotobi` gets an optional `day_sizes` (default `None`) and `C4_DAY_SIZES`; **C3/C4 HOLD run** in the same call | with `day_sizes=None` (C3), `size` stays `None` and the signals are identical; C4 is exactly what this parameter implements |
| 00:47:52 | `swing_rules`: new rule `fix_window` | new function only; the result is the `af3ab38` file |

So C1 ran on the registered code, and C3 ran on the rule as it was registered. **Process gap:** C3/C4 should have
recorded their own hashes before the run. `swing_rules.py` as it was when they ran hashes to `b6160f125b6255d4`
(kept in the same folder). From now on, run `python -m research.tools.prereg_hashes <files>` and paste its output into
the prereg file before each holdout.

**Move in the 2026-09-27 cleanup.** The code moved to `research/swing/` and the shared helpers moved to the top of
`research/`. Only paths, imports and docstrings changed. C1, C3 and C4 were then re-run with the moved code, and every
number in this file came out identical (C1 HOLD n 302, $+2,859, R -0.025; C3 HOLD n 738, $+3,115, R +0.042; C4
HOLD n 246, $+757; spread-stress and long-only lines too).

| registered file | registered | `af3ab38` | now at | now |
|---|---|---|---|---|
| `research/scan/swing.py` | e9d80497d33a9d84 | 7c5185dd85f7b6ae | `research/swing/swing.py` | 8511bfbae1366fc4 |
| `research/scan/swing_rules.py` | 10fd11c9dfa0f90c | df60101287655d67 | `research/swing/swing_rules.py` | 43059165c2210c17 |
| `research/scan/rates.py` | 5a84860812283a21 | same | `research/swing/rates.py` | 5de71c1ba5069f93 |
| `research/scan/specs_ext.py` | e63964ed74d204b2 | same | `research/specs_ext.py` | e63964ed74d204b2 |
| `research/scan/data.py` | 763e848464232614 | same | `research/m1bars.py` | f7ad6f3f8e79432d |
| `research/specs.py` | 9ef05930b3f0baf1 | same | `research/specs.py` | 5be0d7b3b7bf3d79 |
