# Capital allocation

How a risk-capital fund (100 % = the whole fund, money the user accepts losing) is split across the algorithms. It is
a target in percentages, independent of what runs on the VPS today; the bots' sizes are set elsewhere
([docker-instances.md](docker-instances.md), `app/cbot_presets.py`). Written 2026-11-11 at the user's request.

> **Evidence.** Sizes come from
> [c3_kelly_sweep_2026-11-11.md](../research/results/portfolio/c3_kelly_sweep_2026-11-11.md); each algorithm's tier and
> HOLD numbers from [research/JOURNAL.md](../research/JOURNAL.md) and [forward-candidates.md](forward-candidates.md).
> Only C3 has live fills. A2-D5L has none: 25 % of the fund sits on its holdout result alone.

## The split

Sizes are fractions of the **whole fund**, not of the algorithm's slice.

| Algorithm | Tier (HOLD) | Share of fund | Size per trade | Role |
|---|---|---|---|---|
| C3 Gotobi | LIVE (+0.042 R/leg, t 2.9) | **35 %** | risk **4 %** per leg | the engine: strongest evidence |
| A2-D5L | DEMO (+780 bp, t 3.11, n 91) | **25 %** | notional **25 %** | large edge per trade, uncorrelated with C3 |
| B | DEMO (+213.5 bp, t 14.38, n 429) | **0 %** (was 20 %) | notional **10 %**, at most 3 open, once fillable | not fillable: its coins have no spot to borrow (below) |
| Q1 | DEMO (+299 bp, t 2.15, n 37 on 7 days) | **5 %** | notional **10 %** | crash days only |
| F3 | RELAXED (+2.00 bp, t 2.16, n 117) | **3 %** | notional **3x** | small steady edge; collects trades for its promotion rule |
| Gold $50 levels | DEMO (+2.87 bp, t 1.43, n 228) | **2 %** | notional **2x** | as F3 |
| Small bets: X3 / K2 / F0 | DEMO / DEMO / forward | **5 %** (2 / 2 / 1) | registered rule, small size | weak evidence, asymmetric payoff |
| Reserve | | **25 %** | | B's 20 % until B can borrow; funds a candidate that gets promoted |

E1 (t 0.99) gets nothing.

**Why these sizes.**
- **C3, 4 % per leg.** Kelly is 10.5 % per leg at the measured edge and 5.2 % at half of it. At half edge growth peaks
  near 5 %, but going from 4 % to 5 % there adds only +1.3 points of CAGR for 10 more points of drawdown, and live
  costs (the fix-time short's latency, depth at larger lots) put the real edge between the measured one and half of it.
  The three JPY legs move together, so one direction of a day carries about 3 x 4 % = 12 %. Expect at the measured edge
  CAGR ~+78 %, max DD ~43 %; at half edge ~+23 % / ~57 %; worst day about −18 % of the fund. Go to 5 % only once
  a few hundred real legs show an edge near the measured one.
- **A2-D5L, 25 % notional.** About 0.18 Kelly at the HOLD edge, 0.37 at half; one implied sd (~24 %) is ~6 % of the fund.
- **B, 0 % for now.** On 2026-11-11 every one of its 15 paper signals (LSK, BMT, GTC, INIT) had zero Binance margin
  inventory, and `maxBorrowable` answered `-3045` for all four, while the same account could borrow XRP, BNB and BTC
  ([basis_b_borrow_check_2026-11-11.md](../research/results/portfolio/basis_b_borrow_check_2026-11-11.md)). The
  discount B trades likely exists because nobody can short the spot, so more collateral does not help. If its demo
  ever shows fillable signals, it gets 20 % back from the reserve at 10 % notional, at most 3 open.
- **F3, gold, Q1.** Small risk per trade (one sd ≈ 0.1-0.3 % of the fund); they run to reach their promotion counts.

## Rules

1. **Never above Kelly.** C3 at most 10 % per leg; A2-D5L at most 70 % notional (full Kelly at half edge).
2. **Drawdown brake.** Fund down 40 % from its peak: halve every size. Down 60 %: quarter them. Back at the old peak:
   full size again.
3. **Crypto cap.** A2-D5L, Q1, X3 and K2 (and B, if it returns) all lose together when coins crash: their open notional together stays
   at or under 60 % of the fund.
4. **Phase in.** A2-D5L (and B, if it returns) trades at a quarter of their size for their first 10 real trades.
5. **Re-size monthly** from the fund's current equity, so gains compound and losses shrink the sizes.
6. **Promote and stop by the registered rules** ([forward-candidates.md](forward-candidates.md) and each PREREG):
   a small bet that passes its promotion rule takes 10-15 % from the reserve; one that hits its stop goes to 0 and is
   not refilled.
