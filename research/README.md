# research/

Offline strategy research on the cTrader backtest tick cache. Nothing here runs in production.

**Where things stand (2026-09-27):** one algorithm has passed out-of-sample years and a pre-registered holdout:
C3, the gotobi Tokyo-fix trade on USDJPY/EURJPY/GBPJPY (`cBot/GotobiBot.cs`). C1 (crypto Donchian H4,
`cBot/CryptoDonchianBot.cs`) failed its holdout and runs only as a forward test. The day-by-day verdicts, each linked
to its result file, are in [JOURNAL.md](JOURNAL.md). Read it and
[results/portfolio/swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md) ("What was tried")
before you propose a strategy, so that nothing gets tested twice. A third round (flows at fixes and settlement dates,
premia, liquidity provision; [results/portfolio/flow_search_2026-09-27.md](results/portfolio/flow_search_2026-09-27.md))
found nothing new: its one registered candidate, M1 (month-end USD), failed its holdout. The older strategy lab
(TMS+ORB, Judas Sweep, FlowRSI and the 62-strategy baseline) was removed on 2026-09-27; see the last entry of the
journal.

## Layout

| path | what |
|---|---|
| `JOURNAL.md` | the verdicts, one entry per day, newest first, each linked to its result file |
| `PROMPT.md` | prompt mẫu để giao một đợt research thuật toán mới (ràng buộc, pass bar, những gì phải đọc trước) |
| `ticks.py`, `bars.py`, `m1.py`, `m1bars.py` | shared data layer: decode the tick cache (`ticks`, plus `_first_hit`, the tick-level SL/TP search), cTrader-style bid bars from ticks (`bars`), build/load the M1 cache `data/m1/*.npz` (`m1`), bars of any timeframe from M1 plus costs in price units (`m1bars`) |
| `specs.py`, `specs_ext.py`, `indicators.py` | shared cost and indicator layer: contract specs, commission and swaps for the 15 calibrated symbols (`specs`) and the 11 approximated ones (`specs_ext`); cTrader-equivalent indicators |
| `swing/` | **swing lab v2, the engine to reuse**: `swing.py` (per-bot cap 3 with stacking, signal exits, <= 5 days, risk-scaled lots), `swing_rules.py` (the rules, incl. `gotobi` = C3 and `donchian` = C1), `rates.py` (swaps from historical FRED rates), `retest_verdict.py` (verdict of the 2016-2022 R-series retest), `weekend_test.py` (C1 vs the weekend closure), `cap_test.py` (C1 with other per-bot caps, i.e. MaxPositions), `month_end_usd.py` (round-3 candidate M1, failed its holdout), `account.py` (compounding with capital-based risk per trade). Results: `results/portfolio/swing_lab_v2_2026-09-27.md`, `prereg_swing_v2.md` |
| `tools/` | `prereg_hashes.py` (code hashes to paste into a pre-registration); `pull_cache.sh`, `pull_years.sh` (copy the tick/M15 cache from the VPS into `data/`) |
| `tests/` | `research/.venv/bin/python -m pytest research/tests` (tests needing `data/` skip without it); `tests/swing/` mirrors the package, shared-layer tests at the top |

Imports go one way, with no cycles: the shared top-level modules import only each other, and `swing/` uses only
the shared layer. Run modules from the repo root as `research/.venv/bin/python -m research.<package>.<module>`, e.g.
`python -m research.swing.retest_verdict RUN_DIR`, `python -m research.m1`.

## Results

Git keeps the reports and summary tables in `results/portfolio/`; bulky outputs stay on the local disk only
(git-ignored), as does `data/` (tick + M15 cache per symbol and `data/m1/*.npz`; re-pull with `tools/pull_cache.sh`).

| file | what |
|---|---|
| `results/portfolio/swing_lab_v2_2026-09-27.md`, `prereg_swing_v2.md`, `prereg_swing_v2_code/` | swing lab v2: pre-registration, verdicts of C1/C3/C4 and the R-series, and the registered sources |
| `results/portfolio/gotobi_*.md` | GotobiBot cTrader backtests |
| `results/portfolio/crypto_donchian_*.md` | CryptoDonchianBot cTrader backtest, C1 vs the weekend closure, C1's MaxPositions (keep 3) |
| `results/portfolio/flow_search_2026-09-27.md`, `prereg_month_end_usd_2026-09-27.md` | round 3: ~40 flow / premium / liquidity hypotheses and scans; M1 registered and failed |
| `results/portfolio/flow_search_round4_2026-09-27.md` | round 4: benchmark-time scan and public external data (COT, funding, GEX/DIX, VIX, auctions); no candidate |
| `results/portfolio/sizing_round5_2026-09-27.md` | round 5: capital-based lots with a 60 % drawdown limit; equity premium and martingale rejected, C3 compounding and stress |
| `results/portfolio/swing_lab_2026-09-27.md`, `full_run_2026-09-27.md`, `baseline_report.md`, `sweep_*.csv` | swing lab v1 (superseded by v2; its code was removed with the lab) |

## Trying a new strategy

1. Write it as a rule in `swing/swing_rules.py` returning `swing.Signals` for one symbol's bars (decided on the
   bar close), with a stop so the lot can be sized off it.
2. Write down the pass bar before looking at results (as in `results/portfolio/prereg_swing_v2.md`), together with
   the code hashes from `research/.venv/bin/python -m research.tools.prereg_hashes <files the run uses>`; don't edit
   those files until the holdout has run.
3. Choose parameters on 2016-2021, check on 2022-2024, and look at the holdout once.
4. Write the report into `results/portfolio/` and add a row to [JOURNAL.md](JOURNAL.md).

## Setup

```bash
python3 -m venv research/.venv
research/.venv/bin/python -m pip install -r research/requirements.txt
research/tools/pull_cache.sh                           # all symbols; or: research/tools/pull_cache.sh BTCUSD USDJPY
research/.venv/bin/python -m research.m1               # build data/m1/*.npz from the ticks
```
