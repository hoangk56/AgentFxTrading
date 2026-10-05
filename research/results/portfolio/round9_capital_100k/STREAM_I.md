# Stream I: the IC Markets cTrader account at $100,000 (relaxed limits)

Read BRIEF.md first. Question: on the existing IC cTrader account (26 symbols, the bots' infrastructure), what does
$100k plus relaxed limits (hold weeks-months, many positions, capital-based lots) unlock that eight rounds have not
tested, and how should the one proven edge (C3) be run at that size?

## I-A. C3 at $100k: execution and risk at size (do this first; it is the practical answer)
Round 5 sized C3 on closed-trade equity only. At $100k with risk 0.25-2 % per leg, a leg's notional is far larger
than today's ($50 risk -> median ~$36k notional per leg; derive the ratio from the CSV: lots x 100,000 units).
1. Notional and lots per leg at 0.25 / 0.5 / 1 / 1.5 / 2 % risk per leg (fixed fraction of the starting $100k, and
   compounding). IC limits: max volume per order on cTrader for FX (find it; IC docs say 200 lots? verify), margin at
   1:30 vs 1:500 (the live account is 1:1000).
2. Execution cost at size: from research/data/m1 (cut HOLD), the spread (smean / smin, ca - c) at the exact entry and
   exit minutes C3 uses (~18:00 UTC entry, 00:55 UTC exit/entry, 02:55 UTC exit) for USDJPY/EURJPY/GBPJPY by year,
   vs the day's median. Whether the 00:55 minute is unusually wide or thin (tick count n). A simple market-impact
   assumption for 5-50 lots on IC's ECN at that minute (say what it is based on; e.g. top-of-book ~1-5M per level).
   How much of C3's +0.04-0.05 R edge survives an extra 0.1 / 0.2 / 0.5 pip of slippage per side at each size.
3. Floating (mark-to-market) drawdown: rebuild each CSV leg's intrabar path from the M1 bid/ask between its entry
   and close (2016-2024 only from M1; for 2025-26 legs use the CSV close only and say so), so the max DD and the worst
   day include open losses. Drop JP-holiday gotobi days (the live bot skips them).
4. Block bootstrap (blocks of ~10 gotobi days, >= 4000 paths) of the basket at each risk level: P(max DD >= 10 / 20 /
   30 %) in 1 and 3 years, with the full edge and with the edge halved (shift R by -0.5 x mean). Recommend a risk per
   leg for DD tolerances 10 / 20 / 30 %.
5. IC commission at volume: IC's Active Trader / volume rebate terms if any (web), and what they are worth for C3.

## I-B. New mechanisms the relaxation unlocks on IC's 26 symbols
Already done, don't redo: published multi-week premia at their published parameters (round 7 D: TSMOM, carry,
FX momentum/value, index momentum, commodity momentum/reversal), the vol-managed equity premium and a martingale
(round 5), FOMC cycle, pre-FOMC, night premium, turn of month, intraday flows of every kind.
Candidates you may test (write each into HYPOTHESES_I.md first; add your own if they have a mechanism and are
genuinely different from the list above):
- Macro fair value at 2-12 week horizons: gold vs US real yield (FRED DFII10) and the dollar; AUD/NZD/CAD vs
  their commodity terms of trade; USDJPY vs the US-JP 2y/10y spread. Trade the residual's mean reversion.
- Positioning extremes: CFTC COT (legacy / TFF) speculator net position z-score at multi-week horizons.
- Large-shock regimes in indices: buy after a >= 10 % drawdown or VIX > 30 and hold weeks (crash-premium /
  liquidity provision), with IC's long index financing (r + ~5.3 %/yr) charged.
- Swap-aware carry at IC's ACTUAL net swap (positive-swap legs only), vol-targeted, as a book.
- A multi-strategy book: C3 plus whatever survives, risk-budgeted; correlation with C3 daily P&L.
Costs: spread at the trade minute, 0.6 bp commission FX/metals, financing via research/swing/rates.py
`swap_frac_at` for FX and the round-7 markups for indices/metals (state the numbers you use).
Bar: BRIEF.md point 5 (slow premia) or the round-8 bar for anything with many trades.

Return per BRIEF.md "What to return". In the one-paragraph answer, say plainly whether IC at $100k gives anything
beyond scaling C3.
