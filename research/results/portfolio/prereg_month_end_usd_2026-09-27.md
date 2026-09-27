# Pre-registration: M1, month-end value-date USD demand (2026-09-27)

Written at 2026-09-27 12:28 UTC, before the holdout (2025-01-01 .. 2026-09-24) of the candidate below was computed.
Nothing about the candidate may change after its holdout is seen, and a failed candidate is reported as failed. The
search that produced it is in [flow_search_2026-09-27.md](flow_search_2026-09-27.md).

## Candidate

- **Hypothesis.** FX spot settles T+2, so the third-to-last weekday of a month is the last day on which a spot trade
  settles inside that month. Companies and funds that need dollars for month-end payments buy them on that day, in
  the European morning. The dollar should rise then and give the move back before the month ends.
- **Symbols / bot.** USDJPY, USDCHF, EURUSD in one bot, cap 3 (one position per symbol).
- **Day.** The third-to-last weekday (Monday-Friday) of the calendar month, by UTC date. Holidays are not modelled.
- **Trade.** Buy USD (buy USDJPY, buy USDCHF, sell EURUSD) on the M5 bar close at 10:00 UTC, filled at the next M1
  open. Exit on the M5 bar close at 13:00 UTC, filled at the next M1 open, or at the stop.
- **Stop / lot.** Stop 3 x ATR20(H1) from the fill; lot = $100 default risk / stop distance (1x, no scaling).
- **Engine and costs.** `research/swing/swing.py` with real M1 bid/ask, commission from research/specs, swaps from
  research/swing/rates.py (the window crosses no rollover, so there is no swap). Code: `swing_rules.month_end_usd`,
  runner `python -m research.swing.month_end_usd [--hold]`.

## How it was found (read before trusting the IS/VAL numbers)

- It came from a scan of 90,168 cells (26 symbols x 17 day types x 1-8 h UTC windows) on IS. VAL was printed for
  the 49 cells with |t_IS| >= 4. The cell "USDJPY, 3rd-to-last weekday, 10-13 UTC" had IS +6.4 bp (t 4.3) and VAL
  +8.7 bp (t 2.1). The value-date story was written after the cell was seen. IS t 4.3 alone does not survive a
  Bonferroni correction over the scan, which would need about 4.9.
- VAL was visible when the cell was picked, so the VAL numbers below are not a blind confirmation. HOLD is the only
  clean test.
- The window (10-13 UTC) and the day come from the scan. The three pairs were chosen on IS: the two strongest
  (USDJPY IS t 3.6, USDCHF t 3.3) and the next (EURUSD t 1.4). GBPUSD, AUDUSD, NZDUSD and USDCAD are about 0 in IS.
- HOLD leakage, disclosed. Earlier the same day, an FOMC event study printed HOLD averages over 14 FOMC days. Three
  of them are M1 days: 2025-01-29, 2025-10-29 and 2026-01-28. The printed pre-FOMC 24 h window contains M1's window.
  That was before M1 was conceived, and it is one average over 14 events (EURUSD pre-FOMC HOLD -17.7 bp, meaning USD
  up), so the leak is small but not zero. No other HOLD number of these three pairs has been computed.

## IS / VAL evidence (engine, $100 risk; `python -m research.swing.month_end_usd`)

| era | trades (days) | mean R | t | day-clustered t | net $ | years > 0 | max DD |
|---|---|---|---|---|---|---|---|
| IS 2016-2021 | 216 (72) | +0.123 | +4.4 | +3.2 | +2,664 | 6/6 | $351 |
| VAL 2022-2024 | 108 (36) | +0.228 | +3.8 | +2.6 | +2,457 | 3/3 | $391 |

- Per pair: USDJPY IS +0.143 / VAL +0.217, USDCHF +0.143 / +0.218, EURUSD +0.084 / +0.247.
- 1.5x spread: IS +0.121, VAL +0.226.
- Random-day control (1 random other weekday per month, same pairs, window, side and stop; 500 seeds): real summed
  R beats 99.2 % of seeds (IS) and 100 % (VAL).
- Placebo, same window on the k-th last weekday, day-clustered t (IS / VAL): k=1 -0.5/+0.6, k=2 +1.9/-0.5,
  **k=3 +3.2/+2.6**, k=4 +1.4/-0.8, k=5 +1.3/-1.9, k=6 -0.2/-1.2, k=7 -1.5/-0.1, k=8 -1.9/+1.4, k=9 +1.1/+0.1,
  k=10 -1.4/+2.5. Other offsets reach |t| 2.5, so the placebo spread is wider than 1: k=3 stands about 2 of its
  standard deviations out in each era, not more.
- Without FOMC days (10 of the 108 days): IS day-clustered t 2.7, VAL 2.6.
- Quarter-end months: IS +0.179 vs +0.095 for other months; VAL +0.030 vs +0.326. The funding story would predict a
  stronger quarter-end, and it is not there in VAL.
- P&L correlation, IS+VAL: with C3 daily -0.023, monthly -0.030; with C1 daily -0.019, monthly -0.054.

## Pass bar at HOLD (all of)

1. Net $ > 0 and mean R > 0.
2. Day-clustered t >= 1.0 (about 21 days; at the IS effect size the expected t is about 1.7).
3. Mean R > 0 with 1.5x spread.
4. Real summed R beats >= 80 % of the random-day control seeds (as above, drawn from HOLD days).

Reported, not judged: per pair, per year, max drawdown, correlation with C3 and C1 over HOLD.

Data limit: the cache ends 2026-09-24 and there is no newer data, so HOLD is 2025-01 .. 2026-09-24. Other strategies
(C1, C3, C4 and the removed lab) used this period as their holdout. M1's own HOLD numbers are computed here once.

## Code hashes at registration (sha256, first 16; `python -m research.tools.prereg_hashes`)

- `research/swing/month_end_usd.py` 3fa2fa3754ebfd1f
- `research/swing/swing.py` 8511bfbae1366fc4
- `research/swing/swing_rules.py` a5378e2095cc59e9
- `research/swing/rates.py` d5ec1cd0fd79819d
- `research/m1bars.py` f7ad6f3f8e79432d
- `research/m1.py` 3970b82bffee304c
- `research/specs.py` 95512c94933790c9
- `research/specs_ext.py` f04098e4f2310007
- `research/indicators.py` 6527b18fbbfe1597

## Result at HOLD (run once, 2026-09-27 12:28 UTC; hashes checked equal to the list above just before): **FAILED**

`python -m research.swing.month_end_usd --hold` (trades in `trades_M1_month_end_usd.csv`, git-ignored):

| era | trades (days) | mean R | t | day-clustered t | net $ | years > 0 | max DD |
|---|---|---|---|---|---|---|---|
| HOLD 2025-01..2026-09 | 60 (20) | +0.044 | +1.0 | **+0.7** | +266 | 1/2 (2025 +$405, 2026 -$139) | $160 |

| criterion | result | |
|---|---|---|
| 1. net $ > 0 and mean R > 0 | +$266, +0.044 | pass |
| 2. day-clustered t >= 1.0 | +0.7 | **fail** |
| 3. mean R > 0 at 1.5x spread | +0.042 | pass |
| 4. beats >= 80 % of random-day seeds | 79.4 % (real summed R +2.7, control -1.7 +/- 5.5) | **fail** |

Per pair: USDJPY R +0.032 (net +$64), USDCHF -0.020 (-$39), EURUSD +0.120 (+$241). HOLD placebo on the other
k-th last weekdays: day-clustered t between -1.2 and +1.1. Correlation over 2016-2026 with C3 daily -0.021 / monthly
-0.019, with C1 daily -0.017 / monthly -0.041.

The sign held but the size did not. HOLD mean R is about a third of IS (+0.123) and a fifth of VAL (+0.228), which
is what a cell picked out of a 90,168-cell scan, with VAL in view, should be expected to do. M1 is not adopted and is
not re-tested with any change.
