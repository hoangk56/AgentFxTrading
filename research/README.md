# research/

Offline strategy research on the cTrader backtest tick cache. Nothing here runs in production.

**Where things stand (2026-09-26):** no strategy tested so far has an edge that survives multiple testing
and out-of-sample years. The full list, with rules, origin and findings per strategy, is
[STRATEGIES.md](STRATEGIES.md). Read it before proposing a strategy, so nothing gets tested twice.

## Layout

| path | what |
|---|---|
| `STRATEGIES.md` | the catalog, rendered from `lab/catalog.py` + lab results. Edit the catalog, not this file |
| `lab/` | the strategy lab: every catalogued strategy x 22 symbols, tick level, fixed lots, 2023-01..2026-09 |
| `lab/strategies/` | lab strategy code: `rules.py` (researched rules), `flowrsi.py`, `judas.py`, `tmsorb.py` (live bots) |
| `scan/` | round 1-2 strategy search on the M1 cache: 552-config bank, pairs, walk-forward ridge, tick sim, 2023-24 confirmation |
| `*.py` (top level) | FlowRSI replica (`signals`, `sim`, `specs`, `calibrate`), entry screening (`screen`), tick/bar decoding (`ticks`, `bars`) |
| `pull_cache.sh`, `pull_years.sh` | copy the tick/M15 cache from the VPS into `data/` |
| `fill_*.py` | queue the VPS backtests that make cTrader download missing years of ticks |
| `tests/` | `research/.venv/bin/python -m pytest research/tests` (tests needing `data/` skip without it) |

Design docs: `docs/superpowers/specs/2026-09-25-strategy-lab-design.md` (lab rules and flags),
`2026-09-25-flowrsi-entry-redesign-design.md`, `2026-09-25-flowrsi-pair-optimization-design.md`, and the plans
of the same dates in `docs/superpowers/plans/`.

## Results

Git keeps the reports and summary tables; the bulky outputs stay on the local disk only (git-ignored).

| file | in git | what |
|---|---|---|
| `results/lab/main/report.md` | yes | lab baseline: 62 strategies x 22 symbols, 1198 cells, per-year $, stress flags |
| `results/lab/main/cells.csv`, `matrix.csv` | yes | one row per (strategy, symbol); strategy x symbol net $ |
| `results/lab/main/meta.json`, `coverage.csv`, `errors.csv` | yes | run arguments + code hashes, tick coverage, errors (none) |
| `results/lab/main/trades.csv.gz`, `control.csv`, `parts/` | no (880 MB) | every trade, random-entry control, per-job raw files |
| `results/strategy_search.md`, `strategy_prereg.md` | yes | rounds 1-2 of the open search and the pre-registered 2023-24 confirmation |
| `results/screen_report.md`, `screen_refusals.csv` | yes | FlowRSI entry screening (E1a..E5b x X1/X2) |
| `results/bank_stats.csv`, `wf_trades.csv` | yes | 552-config bank stats (rescore with `scan/score.py`), walk-forward ridge trades |
| `results/screen_trades.csv` | no (100 MB) | entry-screening trades |
| `data/` | no (9.6 GB) | tick + M15 cache per symbol, `data/m1/*.npz`, backtest reports; re-pull with `pull_cache.sh` |

`results/lab/main` is write-protected (`chmod -R a-w`) so a new run can't overwrite the baseline by accident;
`chmod -R u+w research/results/lab/main` if it really has to be regenerated.

## Trying a new strategy

1. Write `fn(ctx, **params)` in `lab/strategies/` (usually `rules.py`). Build `Intent(at_ms, side, sl_dist=...,
   tp_dist=..., exit_ms=...)` from `ctx.bars(minutes)` or the ticks `ctx.t` and hand them to `run_intents(ctx, ...)`;
   the engine fills at the first tick, one position at a time, with the account's costs. Only look at data before
   `at_ms`. `vol_breakout` and `shock_follow` in `rules.py` are short examples.
2. Add a `StrategyInfo` to `CATALOG` in `lab/catalog.py`: id, status `candidate`, origin, family, rules in words,
   the function, params, symbols. `tests/lab/test_lab_catalog.py` runs every entry on a short slice.
3. Write down the pass bar before looking at results (as in `results/strategy_prereg.md`).
4. Run it into a **new** run dir (the default is a timestamped dir under `results/lab/`). Rerunning a job
   rewrites its part file for every strategy, so never run a subset of strategies into an existing dir:

   ```bash
   research/.venv/bin/python -m research.lab.run --strategies NEW_ID --run-dir research/results/lab/new1
   research/.venv/bin/python -m research.lab.run --strategies NEW_ID --shuffle 20 --into research/results/lab/new1
   research/.venv/bin/python -m research.lab.report research/results/lab/new1
   research/.venv/bin/python -m research.lab.catalog research/results/lab/main research/results/lab/new1
   ```

   The catalog takes several run dirs; a strategy in a later dir replaces its result from an earlier one, so
   STRATEGIES.md keeps the baseline and adds the new rows.
5. Record the verdict in the entry's `findings` and set its status.

Reading the flags (report.md): E = positive every year, C = beats >= 95 % of 20 random-entry seeds,
S = beats >= 95 % of 20 week-shuffles, M = mirrored prices net > 0. With ~1200 cells, ~26 cells reach t >= 2 and
~13 pass E by chance alone, so one flagged cell is not an edge; it needs a pre-registered bar on unseen data.

## Setup

```bash
python3 -m venv research/.venv
research/.venv/bin/python -m pip install -r research/requirements.txt
research/pull_cache.sh                                 # all 15 real symbols; or: research/pull_cache.sh BTCUSD XAUUSD
research/.venv/bin/python -m research.scan.m1          # build data/m1/*.npz from the ticks
```

Account rules of the lab: $10k, fixed units (FX 10k incl. synthetic crosses, XAU 2, BTC 0.1, ETH 4, US30 0.2,
USTEC 0.4, DE40 0.4, UK100 0.8), no loss limits, one position per strategy x symbol. The 7 synthetic crosses
(EURGBP EURAUD GBPAUD EURCAD GBPCAD AUDCAD CADJPY) are built from USD legs.
