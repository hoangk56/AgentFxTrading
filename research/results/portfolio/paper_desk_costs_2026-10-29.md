# Paper desk measured costs (2026-10-29)

Source: `research/tools/paper_desk_costs.py` on `research/data/m1` (IC Markets, weekdays 2026-01-01 to 2026-09-24, minutes 06:55-07:05 UTC) and `research/specs.py`. Basis points of notional, round trip (entry 07:00 UTC, exit 07:00 UTC next weekday). `cost_long` / `cost_short` are what a call in that direction pays: spread + commission + overnight swap (credits not counted).

| symbol | days | spread bp | commission bp | mean rollovers | swap long bp | swap short bp | cost long bp | cost short bp | swap fitted |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 190 | 0.06 | 0.58 | 1.40 | +0.95 | +0.00 | 1.58 | 0.64 | yes |
| USDJPY | 190 | 0.07 | 0.60 | 1.40 | +0.00 | +1.45 | 0.67 | 2.12 | yes |
| GBPJPY | 190 | 0.32 | 0.59 | 1.40 | +0.00 | +1.32 | 0.92 | 2.24 | yes |
| XAUUSD | 189 | 0.20 | 0.57 | 1.40 | +1.78 | +0.00 | 2.55 | 0.77 | yes |
| US500 | 190 | 0.68 | 0.00 | 1.40 | +0.00 | +0.00 | 0.68 | 0.68 | NO (0 assumed) |
| BTCUSD | 191 | 1.69 | 0.00 | 1.40 | +7.60 | +0.00 | 9.29 | 1.69 | yes |

Caveats: spread is the mean tick spread in the minute, not the spread at an exact fill; the swap rates are the constant 2026 fit of `specs.SWAPS` (see its docstring); commission is the fitted `comm_per_unit` (metals commission is known to be overstated, see JOURNAL). The desk scores on Dukascopy bids, so the measured spread is the whole cost of crossing it.

`COST_BP` in `app/paper_desk_runner.py` holds these `(cost_long, cost_short)` pairs:

```
"EURUSD": (1.58, 0.64),
"USDJPY": (0.67, 2.12),
"GBPJPY": (0.92, 2.24),
"XAUUSD": (2.55, 0.77),
"US500": (0.68, 0.68),
"BTCUSD": (9.29, 1.69),
```
