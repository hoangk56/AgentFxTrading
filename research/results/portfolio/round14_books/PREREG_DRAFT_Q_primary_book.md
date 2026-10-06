# PREREG DRAFT (stream Q): primary clock book = E1 + XAUUSD long before UK holidays

Draft written 2026-10-06 ~01:55 UTC by stream Q, because the declared primary book meets the DEMO numbers on IS/VAL
(the brief says: write the draft and stop). Not a registration: the lead decides. HOLD was not opened by stream Q.

**Recommendation: do not register this as a new candidate.** E1 carries 96-98 % of the book's risk, and E1 is already
drafted and registered by stream M (round13_structural/PREREG_DRAFT_M_eurusd_midday.md, PREREG_M_eurusd_midday.md).
The only other leg decays: its VAL mean is +0.41 bp (t 0.08) against +4.84 in IS. Opening HOLD for this book would
test E1 again.

## Rule (exact)
Selection rule and variants: HYPOTHESES_Q.md, Q1. This is variant P_B, tN = 1.5, W1 (tN = 1.0 gives the same two legs).
One bot per symbol, at most one position per bot, never two at once across the book (max 1 open in IS).

| leg | symbol, side | clock and window | days | weight (W1) |
|---|---|---|---|---|
| 1 (E1) | EURUSD short | 11:00-13:00 Europe/London | every weekday (London date), except 24 Dec - 1 Jan | 0.99 |
| 2 | XAUUSD long | 11:00-15:00 Asia/Tokyo (02:00-06:00 UTC) | the last weekday before a UK holiday block that is not itself a UK holiday (Tokyo date), except 24 Dec - 1 Jan | 1.01 |

- Fills at the window boundaries: sell at the bid, buy at the ask. No stop in the test. Fixed lot per leg, scaled by
  the weight (equal IS risk per trade); never dependent on capital.
- Sides fixed from PRE 2004-15; legs chosen on IS by the rule; the leg-2 cell was known from STREAM_M.md to decay in VAL
  (disclosed in HYPOTHESES_Q.md before any book number).

## Numbers (book P&L per UTC day, bp at the median leg's risk; t clustered by UTC day)
| era | days | day net bp (t) | day Sharpe | power | x1.5 | +1 min | years > 0 |
|---|---|---|---|---|---|---|---|
| PRE 2004-15 (in-sample for sides) | 3,054 | +1.15 (3.53) | 0.064 | 1.35 | +1.10 | +0.84 | |
| IS 2016-21 (in-sample) | 1,525 | +1.24 (3.53) | 0.090 | 1.90 | +1.21 | +1.15 | 5/6 |
| VAL 2022-24 | 765 | +1.35 (2.47) | 0.089 | 1.89 | +1.33 | +1.01 (1.88) | 3/3 |

- Random-entry control (each leg's start redrawn daily within +-3 h, 200 seeds): beats 100 % (IS), 98 % (VAL).
- C3 correlation (IS + VAL): daily +0.04, monthly +0.04.
- Leg 2 alone: PRE +8.14 (t 3.63, 51 events), IS +4.87 (t 1.79, 26), VAL +0.41 (t 0.08, 16).
- Multiple testing: 12 books tried (2 pools x 3 thresholds x 2 weights); legs drawn from stream M's K = 270,086 cells.
- **Expected HOLD t** (~445 days): 1.89 on the VAL size. HOLD cannot confirm at the LIVE level.

## DEMO plan (only if the lead does not simply run E1)
- Expected demo trades: ~254 a year for leg 1, ~4-5 a year for leg 2.
- Stop rule: stop after 250 demo days if the book's net mean per day <= 0, or at any time if the cumulative day t < -2.
- Promotion rule: HOLD + demo pooled day t >= 2.5.

## Code
`.../scratchpad/r14/Q/`: `qcommon.py`, `select_book.py` (select.out), `legs.py`, `books.py` (books.out), `incr.py`
(incr.out); reuses stream M's `mcommon.py`.
