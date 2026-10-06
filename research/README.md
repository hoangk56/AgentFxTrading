# research/

Offline strategy research on the cTrader backtest tick cache. Nothing here runs in production.

**Where things stand (2026-10-06):** one algorithm has passed out-of-sample years and a pre-registered holdout, and
it is the only one running: C3, the gotobi Tokyo-fix trade on USDJPY/EURJPY/GBPJPY (`cBot/GotobiBot.cs`). It also
passes an older era nobody had used, Dukascopy 2004-2015 (round 7). C1 (crypto Donchian H4) failed its holdout; its
cBot was removed from the repo and the VPS on 2026-10-03 (the research code and reports stay). Rounds 3-22 (flows at
fixes and settlements, premia, liquidity provision, public external data, new symbols and eras, multi-week premia,
interactions between symbols, Asian venue benchmarks, central-bank events, cost-gated signal books, multi-day event
drift, cross-sections, a full index intraday scan, hedge flows at the fixes, other executions of sub-cost flows,
structural calendars, a stability-first scan from 2004, books of stable clock effects, 1-10-minute windows at
benchmark minutes, income conversion flows, quote-based order flow, calendar day-of-month, home-currency fixes, central-bank-day carry, index expiry auctions) found no new LIVE candidate: the effects that exist are
about the size of IC's costs, too rare for the 21-month holdout, or decayed by 2025-26. Two weak DEMO candidates
await a decision: gold into the COMEX settlement on big days (round 12) and short EURUSD 11:00-13:00 London
(round 13).
The day-by-day verdicts, each linked to its result file, are in [JOURNAL.md](JOURNAL.md).
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
| `results/portfolio/round10_new_directions_2026-10-06.md`, `round10_new_directions/` | round 10: new directions on the existing data: Asian benchmarks and Chinese venue sessions with holiday placebos, pooled central-bank decisions and home holidays, a cost-gated FX book of sub-cost signals, option pinning, the overnight drift, size-conditioned fixes, non-US macro releases; no candidate at the LIVE or DEMO bar; the feasibility frontier (gross edge needed per symbol and hold); pitfalls of holiday tests |
| `results/portfolio/round11_multiday_cross_section_index_scan_2026-10-06.md` | round 11: drift 1-5 days after central-bank decisions and macro surprises (delayed overshooting faded after 2015), cross-sectional momentum / reversal at 1-5 days (no signal), a full 15,913-cell intraday scan of the commission-free index CFDs (nothing clears the frontier); write-ups in `round10_new_directions/STREAM_F/G/H.md` |
| `results/portfolio/round12_flows_execution_2026-10-06.md`, `round12_flows_execution/` | round 12: month-end equity-hedge flows at the WM/R fix, other executions of the sub-cost flows (break-even costs, passive fills, the Sydney rollover-hour clash), flow-size conditions, literature 2018-26; three candidates registered (`PREREG_*`, code in `prereg_code/`): two failed HOLD, gold settlement big days is a weak DEMO candidate; `BRIEF.md` is the brief template for parallel streams |
| `results/portfolio/round13_structural_2026-10-06.md`, `round13_structural/` | round 13: effects that should not decay: a stability-first scan with Dukascopy 2004-15 as the discovery era (stable clock effects exist, shrink, mostly below cost), structural calendars (tax, Treasury settlements, index extension: none), the gold big-day rule on oil and index closes (2020-driven); E1 EURUSD midday short registered, weak DEMO candidate |
| `results/portfolio/round14_books_2026-10-06.md`, `round14_books/` | round 14: a book of stable clock legs chosen on 2004-21 (works in theory, fails on decay of the non-EURUSD legs) and mechanism-derived conditions for E1 and other clock effects (scale 1.5x, power unchanged); E1 reverses on TARGET2 closing days; no candidate |
| `results/portfolio/round15_short_windows_2026-10-06.md`, `round15_short_windows/` | round 15: windows of 1-10 minutes at benchmark minutes in FX (PRE discovery), metals, AUD/NZD, indices and oil; real at mid far beyond chance but 0.3-2.7 bp against 1-7 bp costs; the ECB V moved ~16 min at the end of 2015; silver/gold fall into the LBMA auctions (information only); no candidate |
| `results/portfolio/round16_income_flows_2026-10-06.md`, `round16_income_flows/` | round 16: cross-border income conversion flows (dividends, coupons, redemptions: none) and a decision-value table of the ~45 effects real at mid in rounds 3-15 under other cost structures (`STREAM_X.md`): only a venue without the 0.6 bp FX commission lifts any (the Sydney V, the ECB slot) to LIVE-like power, and only if they stop decaying |
| `results/portfolio/round17_microstructure_2026-10-06.md`, `round17_microstructure/` | round 17: order-flow imbalance from IC quotes (real, hundredths of a bp per z) and big-day intraday momentum in European index CFDs (a third of cost; DE40 does not replicate); no candidate |
| `results/portfolio/round18_decay_dom_2026-10-06.md`, `round18_decay_dom/` | round 18: yearly trends and 2025-26 forecasts for 49 effects (how a rule was found predicts its holdout retention, its trend does not; 2024 was a common low year) and calendar day-of-month clocks (noise); no candidate |
| `results/portfolio/round19_declared_2026-10-06.md`, `round19_declared/` | round 19: declared-only cells: E1's fix mechanism in other currencies (only the CNY close, below cost) and a second literature pass (7 families, none); official fix-time histories in `STREAM_H.md` |
| `results/portfolio/round20_declared2_2026-10-06.md`, `round20_declared2/` | round 20: declared-only: FOMC-day currency premium (the dollar falls in every era, but 8 events a year: below DEMO's IS t) and European / HK index expiry settlement auctions (none); exchange settlement rules in `STREAM_G.md` |
| `results/portfolio/round21_fed_events_2026-10-06.md`, `round21_fed_events/` | round 21: the FOMC-day dollar rule on other scheduled US-policy events (minutes, testimony, Jackson Hole, refunding): none; the premium is FOMC-specific |
| `results/portfolio/round22_residual_2026-10-06.md`, `round22_residual/` | round 22: triage of every open idea of rounds 3-21 (`TRIAGE_R.md`) and declared tests of the top four: none; what is left needs a user decision |
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
