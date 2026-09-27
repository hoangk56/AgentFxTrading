# Research journal

The verdicts, one entry per day, newest first. Each row says what was tested, the verdict, and which file has the
detail. The numbers are copied from those files, and the file wins if the two ever differ.

When you write a new result file, add a row to that day's entry (or start a new entry) and link the file. Don't
repeat its tables here.

## 2026-09-27: swing lab on 26 symbols, 2016-2026. C3 Gotobi JPY basket passes its holdout

Constraints for every test this day: a lot never depends on account capital (default $ risk x 0.5-2x), a position is
held 5 days at most, and a bot holds 3 positions at most. Eras: IS 2016-21, VAL 2022-24, HOLD 2025-01..2026-09.

| tested | verdict | detail |
|---|---|---|
| Swing lab v1: one portfolio-wide bot, cap 3, SL/TP exits only, 9 families, ~95 configs (`scan/portfolio.py`, removed; see the note at the end) | no strategy cleared the pre-registered bar. Superseded by v2 | [swing_lab_2026-09-27.md](results/portfolio/swing_lab_2026-09-27.md), [full_run_2026-09-27.md](results/portfolio/full_run_2026-09-27.md) |
| R-series: the old lab's positive-but-rejected strategies (TOM, K2, VB1, LC1, GF1, MEF, OD1, N2-GOTOBI, three D1 bank cells, plus N3-IMOM as an addendum), rerun with unchanged code on 2016-2022, which is out of sample for all of them | only N2-GOTOBI passed: n 1002, +0.078R, t +5.7, 7/7 years, beat 10/10 random seeds. Every other strategy failed | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) (R-series) |
| C1 Crypto Donchian H4 (BTCUSD, ETHUSD), pre-registered | **failed** at HOLD: mean R -0.025. Net was +$2,859 only because the lot multiplier sized up the winners. IS +0.276, VAL +0.227 | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md), [swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md) |
| C3 Gotobi JPY basket (USDJPY + EURJPY + GBPJPY, one bot), pre-registered | **passed**: HOLD n 738, R +0.042, t 2.9, all three pairs net > 0. IS +0.043 (t 5.4), VAL +0.041 (t 3.7) | same |
| C4 Gotobi USDJPY with day-type lots, pre-registered | passed the bar, but the sizing is not confirmed: the day-type lots made less than 1x lots at HOLD (+$757 vs +$940) | same |
| Other v2 hypotheses on IS/VAL: the Connors RSI(2) family, turn of the month, time-series momentum, Donchian outside crypto, pairs, FX carry, home-hours depreciation, fixing windows | none worked | [swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md) ("What was tried") |
| `cBot/GotobiBot.cs` (C3) built and backtested with cTrader on IC ticks, 2016-2026 | 33/33 pair-years net positive, 4,574 trades, R +0.049, basket max DD $512 (10.2 R). Also fixed an entry on a stale Monday quote | [gotobi_cbot_backtest_2026-09-27.md](results/portfolio/gotobi_cbot_backtest_2026-09-27.md) |
| `cBot/CryptoDonchianBot.cs` (C1), cTrader backtest 2018-2026 | matches the research engine trade for trade. HOLD R is -0.027 (research: -0.025), so C1 stays a forward test only | [crypto_donchian_cbot_2026-09-27.md](results/portfolio/crypto_donchian_cbot_2026-09-27.md) |
| C1 vs the weekend closure: IC crypto was closed at weekends until 2024-04, so IS/VAL ran on a 5-day market and HOLD on a 24/7 one. C1 rerun on 2024-05..2026-09 with the old closure cut out | **not supported**: pooled mean R +0.042 -> +0.053 (+0.011; bar was +0.10), +0.000..+0.011 at the other bar phases, BTCUSD and ETHUSD in opposite directions. The 24/7 switch does not explain the weak HOLD | [crypto_donchian_weekend_2026-09-27.md](results/portfolio/crypto_donchian_weekend_2026-09-27.md) |
| GotobiBot, VPS Backtest page jobs #366-#374 (3 pairs x $50/$100/$200 risk, 2025-10..2026-09) | all 9 jobs profitable (+0.068R per trade at $50). This is not new evidence, since the period falls inside HOLD. Found two simulation bugs around market closures: a stale Sunday quote, and the 25/12 gotobi | [gotobi_backtest_366-374_2026-09-27.md](results/portfolio/gotobi_backtest_366-374_2026-09-27.md) (Vietnamese) |
| Code provenance of the swing v2 holdouts: the registered code hashes did not match git | the registered sources were rebuilt from the edit log and hash exactly as registered. C1 ran on the registered code, and C3 on its rule as registered. C3/C4 had not recorded their own hashes (a process gap, now `tools/prereg_hashes.py`). A re-run after the folder move gives identical numbers. Verdicts unchanged | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) (addendum), [prereg_swing_v2_code/](results/portfolio/prereg_swing_v2_code/) |

Standing at the end of the day: C3 is the only algorithm that survived both out-of-sample years and a pre-registered
holdout. It is now a cBot, and the next step is the demo account. C1 runs as a forward test only.

## Before 2026-09-27: the strategy lab (removed)

On 2026-09-26 and 2026-09-25 the strategy lab (`lab/`, `scan/`, `flowrsi/`) tested the TMS+ORB, Judas Sweep and
FlowRSI bots, their canonical rebuilds, an open search on the M1 cache and a 62-strategy baseline over 22 symbols.
None of it passed a pre-registered bar. The one lead was N2-GOTOBI (USDJPY), which met five of the six conditions of
the 2026-09-26 refresh and became C3 above. On 2026-09-27 the three bots and the lab were removed from the repo with
their result files; they remain in git history before that removal, and the R-series verdict of
[prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) keeps the numbers it relies on.
