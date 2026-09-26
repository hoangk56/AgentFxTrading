# Pre-registration — strategy refresh v2

Frozen 2026-09-26 02:22 UTC, before any lab output of these strategies existed.

- Spec: `docs/superpowers/specs/2026-09-26-strategy-refresh-design.md` (rules of every variant)
- Plan: `docs/superpowers/plans/2026-09-26-strategy-refresh.md`
- Code at the freeze: git 4fd870f + untracked research/, lab code hash `dbd12076eb09`, catalog hash `0355732ad9d4`
  (`python -c "from research.lab.run import _provenance; print(_provenance())"`)
- Verdict script: `research/lab/verdict.py`

## Variants (14, parameters fixed from the sources, no tuning)

T1-ORB, T2-TMSORB, T3-TMSORB-X, T4-TMS-H4, T5-TMS-H1, J1-ICT, J2-ICT-MO, J3-ICT-2R, J4-ICT-2KZ, J5-SWEEP, N1-FIX,
N2-GOTOBI, N3-IMOM, N4-LBO. Rules as written in `research/lab/catalog.py` and the spec.

## Periods

- Check 2023-01-01 .. 2024-12-31: code check (trade counts, hand-inspected trades); bugs only.
- Holdout 2025-01-01 .. 2026-09-24: run once per variant in `research/results/lab/v2`.

## Pass bar (every condition, per variant pooled over its symbols)

1. Holdout: >= 100 trades, mean net R > 0, t of per-trade net R >= 2.5.
2. Holdout net $ > 0 in 2025 and in 2026 separately.
3. Check period 2023-24: mean net R > 0.
4. Holdout pooled net $ above >= 95 % of the 20 random-entry control seeds.
5. Mirrored prices, holdout net $ > 0 (not applied to N1-FIX, N2-GOTOBI).
6. Holdout net $ > 0 on >= 60 % of the symbols that traded in the holdout (not applied to N2-GOTOBI).

The week-shuffle flag is reported, not part of the bar. A pass = worth a demo forward test, not proof.

## Bug fixes after the freeze

None: the check run (research/results/lab/v2check, 2023-24, 22 jobs, 0 errors) showed no per-day cap breach and 33 hand-inspected trades (T1, T2, T3, T4, T5, J1, J4, J5, N1-N4) matched the rules; one J4 XAUUSD fill + TP within one second on the 2023-06-01 08:15 ET ADP spike is the known limit-fill limitation, not a bug. Parameters unchanged.
