# research/

Offline strategy research on the cTrader backtest tick cache. Nothing here runs in production.

**Where things stand (2026-10-05):** one algorithm has passed out-of-sample years and a pre-registered holdout, and
it is the only one running: C3, the gotobi Tokyo-fix trade on USDJPY/EURJPY/GBPJPY (`cBot/GotobiBot.cs`). It also
passes an older era nobody had used, Dukascopy 2004-2015 (round 7). C1 (crypto Donchian H4) failed its holdout; its
cBot was removed from the repo and the VPS on 2026-10-03 (the research code and reports stay). Rounds 3-8 (flows at
fixes and settlements, premia, liquidity provision, public external data, new symbols and eras, multi-week premia,
interactions between symbols) found no new candidate: the effects that exist are about the size of IC's costs, or too
rare for the 21-month holdout. The day-by-day verdicts, each linked to its result file, are in [JOURNAL.md](JOURNAL.md).
Read it and [results/portfolio/swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md)
("What was tried") before you propose a strategy, so that nothing gets tested twice. The older strategy lab
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
| `results/portfolio/crypto_donchian_*.md` | CryptoDonchianBot cTrader backtest (the cBot was removed on 2026-10-03), C1 vs the weekend closure, C1's MaxPositions (keep 3) |
| `results/portfolio/flow_search_2026-09-27.md`, `prereg_month_end_usd_2026-09-27.md` | round 3: ~40 flow / premium / liquidity hypotheses and scans; M1 registered and failed |
| `results/portfolio/flow_search_round4_2026-09-27.md` | round 4: benchmark-time scan and public external data (COT, funding, GEX/DIX, VIX, auctions); no candidate |
| `results/portfolio/sizing_round5_2026-09-27.md` | round 5: capital-based lots with a 60 % drawdown limit; equity premium and martingale rejected, C3 compounding and stress |
| `results/portfolio/round6_commodity_flows_2026-10-04.md` | round 6: settlement flows in energies/metals, EIA/API reports, passive execution at the Sydney open, index liquidity provision; no candidate; holdout power table; metals commission overstated before 2025 |
| `results/portfolio/round7_new_data_2026-10-05.md`, `round7_pre_code/` | round 7: Dukascopy 2004-2015 as a new era (C3 passes it, M1 fails again; data in `data/duka/`), seven new IC symbols, a 2010-2026 literature screen, multi-week premia with relaxed limits (killed by IC's financing markup); no new algorithm |
| `results/portfolio/round8_inter_symbol_2026-10-05.md`, `round8_hypotheses/` | round 8: how the symbols affect each other (intraday lead-lag, shock spillover, relative value / pairs / PCA residuals / currency strength, cross-session and regime spillovers, literature map); effects are real but priced within a minute or below IC's cost; no candidate; pitfalls of minute-level cross-asset screens |
| `results/portfolio/round9_capital_100k_2026-10-05.md`, `round9_capital_100k/` | round 9: a $100k account. C3 at size on IC (risk per leg by DD tolerance), six new IC families with relaxed limits (none passes), S&P 500 option selling (real premium, no alpha over beta since 2015), C3 at a $100k prop firm (rules survey, pass probability, EV per fee, the account guard it needs) |
| `results/portfolio/c3_sizing_and_trade_management_2026-09-28.md` | C3 compounding vs fixed $ risk, one pair vs the basket; averaging down, pyramiding and holding losing legs rejected |
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
