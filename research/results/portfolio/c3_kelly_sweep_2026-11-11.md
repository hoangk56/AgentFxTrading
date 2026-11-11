# C3 compounding at a fixed fraction per leg, and the Kelly sizes of A2-D5L and B (2026-11-11)

The user's question: how to split a risk-capital fund across the algorithms, accepting high risk. This file holds
the numbers the split in [docs/capital-allocation.md](../../../docs/capital-allocation.md) rests on. Post-hoc sizing
arithmetic on registered trade lists and HOLD summaries; no rule, entry or exit changed, no new return read.

## C3: compounding sweep

Code: `research/tools/c3_kelly_sweep.py`. Input: the registered C3 trade list
[trades_C3_gotobi_jpy_basket.csv](trades_C3_gotobi_jpy_basket.csv) (research engine, 2016-2026, IS + VAL + HOLD).
The six legs of a gotobi day are summed into one day R; equity compounds by (1 + f x day R) once per day, f being the
risk per leg as a fraction of equity. "Half edge" subtracts half the mean leg R from every leg (6 x 0.0212 R per day).

4,590 legs, mean +0.0424 R/leg; 799 gotobi days (72.6 a year), day R mean +0.243, sd 1.525.
Growth-optimal (Kelly) risk per leg = mean / variance of the day R: **0.105** at the full edge, **0.052** at half.

| risk / leg | full edge: CAGR | max DD | half edge: CAGR | max DD | worst day |
|---|---|---|---|---|---|
| 3 % | +57.6 % | 33.6 % | +19.6 % | 44.3 % | −13.7 % |
| 4 % | +77.5 % | 42.9 % | +22.9 % | 56.5 % | −18.2 % |
| 5 % | +96.8 % | 51.4 % | +24.2 % | 66.9 % | −22.8 % |
| 6 % | +114.8 % | 58.9 % | +23.6 % | 75.6 % | −27.3 % |
| 8 % | +144.0 % | 71.5 % | +16.6 % | 87.8 % | −36.4 % |
| 10 % | +159.9 % | 80.9 % | +2.8 % | 95.1 % | −45.5 % |
| 15 % | +123.4 % | 95.8 % | −46.2 % | 100 % | −68.3 % |
| 20 % | +5.8 % | 99.9 % | −85.8 % | 100 % | −91.0 % |

(Worst day shown at the full edge; at half edge it is 0.3-2.6 points worse.)

At half edge growth peaks near 5 % per leg; above it only the drawdown grows. From 10 % a modest loss of edge wipes
the account, as in [gotobi_compound_third_2026-10-09.md](gotobi_compound_third_2026-10-09.md). The 3 % row matches
[c3_sizing_and_trade_management_2026-09-28.md](c3_sizing_and_trade_management_2026-09-28.md) (+60 % / DD 34 %).

Limits: the research engine's fills; no slippage growth with lot size (at the fix, depth costs more as lots grow);
legs of one day compound as one step (no intraday path); 2016-2026 only.

## A2-D5L and B: Kelly from the HOLD summaries

Only n, mean and t are reported, so the per-trade sd is implied: sd = mean x sqrt(n) / t. Kelly notional per trade
(fraction of capital) = mean / sd².

| candidate | HOLD n, mean, t | implied sd / trade | Kelly notional, full edge | half edge |
|---|---|---|---|---|
| A2-D5L ([PREREG](round65_retail_venues/A2/PREREG_A2_D5L.md)) | 91, +780 bp, 3.11 | ~2,390 bp | ~1.36 x capital | ~0.68 x |
| B ([PREREG](round63_parallel/B/PREREG_B_cheap_basis.md)) | 429, +213.5 bp, 14.38 | ~307 bp | ~22 x capital | ~11 x |

B's Kelly is not usable as a size: spot borrow, liquidity and the share of its return that is funding (59 % of
HOLD) bind long before it. Both have no real fills yet.
