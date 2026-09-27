# GotobiBot — cTrader build and backtest (2026-09-27)

`cBot/GotobiBot.cs` (research candidate C3, `swing_lab_v2_2026-09-27.md`) built with ctrader-console on the VPS
and backtested with the cTrader engine on IC's own ticks, 2016-01 .. 2026-09, USDJPY / EURJPY / GBPJPY, one bot
per pair. **Every one of the 33 pair-years is net positive, as in the research engine.**

## How it was run

- Build: `ctrader-console create cbot GotobiBot` + `build` in an isolated home (`~/gotobi-build/home` mounted as
  `/root`), not the live `~/ctrader` nor the repo's `cBot/`. 0 errors; the only warnings are 723 x CS1701
  (cAlgo.API's System.Runtime 6.0 vs 10.0 — as for the other bots). Source sha256 `93c1803de684d0e9…`.
- Backtest: the Backtest page's container spec (`app/backtest_command.build_container_spec` for a `gotobi` job):
  bridge network, 1 GB / 2 CPU, the algo and the password file read-only, the `agentfx-bt-cache` tick cache;
  `backtest --data-mode=ticks --balance=10000 --commission-auto`, preset flags `--RiskPerTradeMoney=50.0
  --MaxSpreadPips=3.0` (GBPJPY 4.0), every server URL locked to `http://127.0.0.1:9/disabled`, `--CommandPollMs=0`.
  One run per pair and calendar year (2016 and 2020 end on 30/12), demo account 10115236.
- Scripts and raw reports stay on the VPS in `~/gotobi-build` (`run_bt.sh`, `run_all.sh`, `analyze.py`,
  `combine.py`; `reports/` 2016-2024, `reports_hold/` 2025-2026, `reports_v1/` the first build). Every trade:
  `research/results/portfolio/gotobi_cbot_trades.csv` (git-ignored).

## Results (the 3 bots side by side, $50 default risk per trade)

| year | trades | net $ | R / trade | win % | USDJPY $ | EURJPY $ | GBPJPY $ | of which swaps $ | research engine $ |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 430 | +1,442 | +0.067 | 59 | +724 | +425 | +293 | +102 | +1,517 |
| 2017 | 426 | +1,329 | +0.062 | 61 | +676 | +403 | +250 | +132 | +1,024 |
| 2018 | 427 | +761 | +0.036 | 55 | +490 | +143 | +128 | +151 | +563 |
| 2019 | 431 | +1,291 | +0.060 | 56 | +478 | +437 | +376 | +194 | +858 |
| 2020 | 428 | +840 | +0.039 | 55 | +441 | +273 | +126 | +165 | +514 |
| 2021 | 426 | +1,563 | +0.073 | 60 | +684 | +513 | +367 | +189 | +1,064 |
| 2022 | 426 | +944 | +0.044 | 57 | +499 | +163 | +282 | +105 | +1,128 |
| 2023 | 425 | +356 | +0.017 | 56 | +102 | +184 | +70 | +109 | +447 |
| 2024 | 423 | +941 | +0.044 | 55 | +364 | +348 | +229 | +118 | +1,052 |
| 2025 | 419 | +816 | +0.039 | 55 | +237 | +434 | +145 | +103 | +767 |
| 2026 (to 24 Sep) | 313 | +899 | +0.057 | 56 | +278 | +298 | +322 | +99 | +790 |
| **all** | **4,574** | **+11,182** | **+0.049** | 57 | | | | +1,467 | +9,724 |

Max drawdown of the three bots together: **$512 (10.2 R)**; longest losing run 15 trades; longest hold 6.9 h (the
5-day limit is never approached); at most one position per bot. Net without swaps: +$9,714.

**Why cTrader is above the research engine in 2017-2021:** a cTrader backtest applies the symbol's *current* swap
to every year (USDJPY long +0.81 pips a day), so the long legs, which cross the 21:00 UTC rollover, earn today's
carry in years whose real rates were near zero (2017-2021 swaps +$132..+$194 a year). The research engine used
historical rates (`research/scan/rates.py`) and is the conservative figure. Without swaps the cBot still makes
money in every year.

## Found and fixed by the backtest

The first build (`reports_v1/`) opened a Monday gotobi day's long at **18:00 UTC on Sunday, before the FX week
opens**: the backtest filled 20 trades on Friday's stale quote (10 of them USDJPY 2025), which a live account
would have rejected. `TryOpenLeg` now waits for `Symbol.MarketHours.IsOpened()` — the first quote after the open,
as the research did — and then for the spread, which at the Sunday open is 20-30 pips for a few minutes. After
the fix no trade opens while the market is closed; 2025-26 went from 734 trades / +$1,650 to 732 / +$1,715.
`tests/test_gotobi_bot.py` pins the check.

## Before it trades a real account

1. Merge the branch and pull on the VPS; build the `.algo` with `scripts/install.sh` (or the README's step 4 for
   GotobiBot), then restart `agentfx.service` so the dashboard knows the `gotobi` cells and the Backtest page.
2. Create the three instances from Setup Instances (the "Gotobi Fix" column) on the demo account, with the
   Japanese public holidays in `--SkipDates`, and compare its live fills at 18:00 / 00:55 / 02:55 UTC with this
   backtest for a few weeks.
3. Server-side daily loss limits are enforced on `/trade`, which this bot never calls; its own exposure is one
   position of one default risk per pair.
