# Stream Q hypotheses: one book of stable clock effects (PRE + IS selection, VAL check)

Written 2026-10-06 01:48 UTC (`date -u`), before any stream-Q number was computed. HOLD (2025-01-01 onwards) is never
loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, and every date range below stops at 2024-12-31.

Only numbers seen before this file: stream M's write-up (STREAM_M.md, which shows IS and VAL for a handful of
families, e.g. that the USDCHF midday legs decay in VAL) and the PRE-only counts of cells.npz by |t_PRE| (3.0: 3,964;
3.5: 1,644; 4.0: 769; 4.29: 500; 5.46: 119). Disclosed: the selection rule below cannot be blind to what STREAM_M.md
printed; to keep it honest it is mechanical, reads only the PRE and IS columns of cells.npz, and every variant is
reported.

## Q0. Mechanism and why a book might escape the per-trade limit
- Mechanism: the clock flows of stream M (home-hours depreciation, fixing-related demand at fixed local times;
  Ranaldo 2009, Breedon & Ranaldo 2013, Krohn, Mueller & Whelan 2024). Each component is a cell whose side was fixed
  by its PRE 2004-15 mean and that was confirmed in IS 2016-21.
- Why a book: LIVE needs power = per-day net Sharpe x sqrt(HOLD days) >= 3, i.e. a per-day Sharpe of ~0.144 at ~250
  days a year. E1 alone is 0.084 (IS). k independent legs, each net > 0 on its own, give ~sqrt(k) x the average leg
  Sharpe. Each leg pays its own cost (unlike round 10 C, which combined sub-cost signals inside one trade).
- Expected failure modes, written now: (1) legs in different symbols at the same clock time share the USD or EUR
  factor, so they are correlated and the sqrt(k) gain shrinks; (2) the legs are chosen on IS net t, so IS is
  in-sample and VAL will shrink (stream M: carried cells kept 72 % of IS size in VAL); (3) most confirmed cells are
  0.3-1 bp, below cost, so few legs pass the net filter.

## Q1. Selection rule (fixed now; PRE + IS columns only)
Source: stream M's cells.npz (K = 270,086 cells: 11 symbols x 4 DST-aware clocks x 28 day types x windows), its
exclusions (JPY pairs: no window overlapping 23:00-02:00 UTC; no window touching 16:45-18:15 New York; Dec 24 -
Jan 1), its prices (PRE Dukascopy bid; IS/VAL panel mid) and its costs (half the actual spread at entry and exit +
0.6 bp commission; PRE: IC 2016-17 spread profile by New York minute + 0.6 bp).

1. **Pool** (PRE): P_B = stream M's set B, the 500 cells with the largest |t_PRE| (|t_PRE| >= 4.29); P_W = every
   cell with |t_PRE| >= 3.5 (1,644 cells). Side = sign of the PRE mean.
2. **Excluded from the pool** (fixed now): non-JPY cells whose window overlaps 23:00-02:00 UTC under either of the
   clock's offsets (stream M's "Tokyo-fix adjacent", C3's mechanism); XAUUSD and AUDUSD cells of day type ALL (round 3
   printed their HOLD hour-of-day means).
3. **IS confirmation**: side t_IS (mid) >= 2.0, IS net mean > 0, and IS net t >= tN with **tN in {1.0, 1.5, 2.0}**.
   IS net t = (side x m_IS - c_IS - 0.6) / (sd_IS / sqrt(n_IS)) from cells.npz.
4. **Greedy order**: eligible cells sorted by IS net t, descending. A cell is added unless
   (a) it overlaps in time an already chosen cell on the same symbol on any IS date on which both trade (UTC
       intervals computed per date from each clock's DST offset and day type; touching ends do not overlap), or
   (b) its IS daily net P&L correlates with an already chosen component's at |rho| > 0.5 (same bet twice).
   No cap on the number of components; no cap on legs a day beyond (a).
5. **Bots**: one bot per symbol; by (a) each bot holds at most 1 position at a time (<= 3 satisfied). Holds are
   <= 4 h and never cross 17:00 New York (stream M's exclusion), so no swap. The maximum number of positions open at
   once across the whole book is reported (relevant if the user wants a single bot).
6. **Weights** (both fixed now, both reported): (W1) equal risk: w_i = sigma_med / sigma_i, sigma_i = the IS sd of
   the leg's gross per-trade return, sigma_med = the median sigma_i of the book; (W2) Sharpe-scaled: W1 x
   clip(s_i / median(s), 0.5, 2), s_i = the leg's IS net per-trade Sharpe. Weights use IS only and never depend on
   capital.
7. **Variants**: 2 pools x 3 tN x 2 weights = **12 books**, all reported. Declared primary: P_B, tN = 1.5, W1.

## Q2. What is computed for each book (IS = in-sample by construction, VAL = out of sample; PRE as information)
- Components: list, per-component per-trade mid / net bp and t in PRE / IS / VAL, VAL/IS ratio.
- Book daily P&L = sum of w_i x net_i over the legs of the day (bp at the median leg's risk), days = UTC weekdays on
  which >= 1 leg traded. Per-day mean, per-day net Sharpe, day-clustered t, years > 0 (IS + VAL, bar >= 6 of 9),
  spread x1.5, both fills +1 minute.
- Correlation matrix of component daily net P&L (zeros on days a leg does not trade; IS and VAL); effective number
  of independent bets = participation ratio (sum lambda)^2 / sum lambda^2 of the eigenvalues of the IS correlation
  matrix.
- Random-entry control at the book level, 200 seeds: every leg keeps its symbol, clock, side, length and trading days,
  its start is redrawn every day uniformly from its own start grid (15 min M1 group, 60 min H1 group) within +-180 min
  of the real start (same session; the real start stays in the draw; excluded windows are redrawn); the book mean is
  recomputed. Second, weaker variant: start anywhere in the day. Bars: beats >= 95 % (LIVE), >= 90 % (DEMO).
- Power on day-clustered units = per-day net Sharpe x sqrt(book days per year x 1.75), on the IS and on the VAL size.
- C3 correlation (daily and monthly, IS + VAL) with the C3 trade list.
- **Ceiling**: if every component kept its IS per-trade net Sharpe and the legs were independent, the book Sharpe is
  sum_i w_i f_i mu_i / sqrt(sum_i w_i^2 f_i sigma_i^2) over days (f_i = fraction of book days leg i trades), and the
  optimal-weight ceiling is sqrt(sum_i f_i s_i^2) per day. The shortfall is split into: correlation (IS ceiling ->
  IS actual), decay (IS actual -> VAL means with IS covariance), the rest (VAL covariance).
- Multiple testing: 12 books; the book-level chance benchmark is the random-entry control; the component-level one is
  stream M's (139 confirmations in set B against a null 95 % of 29).

## Bars (round-13 brief; for a book, t is clustered by UTC day)
LIVE: IS day t >= 2.5 (met trivially in-sample), VAL day t >= 1.5, >= 6 of 9 IS+VAL years net > 0, beats >= 95 % of
the random control, power on the VAL size >= 3, net > 0 at x1.5 and +1 minute. DEMO: IS t >= 2.0, VAL net > 0,
beats >= 90 %. If the primary or any variant meets a bar on IS/VAL: PREREG_DRAFT_Q_<name>.md with the exact list, and
stop; HOLD stays closed.

## Selection done (2026-10-06 01:49 UTC, IS columns only; no book or VAL number computed yet)
- select_book.py read only the PRE and IS columns. After exclusions, 25 P_B cells and 86 P_W cells have side
  t_IS >= 2 and IS net > 0. The books are small: P_B gives E1 + XAUUSD long before UK holidays (tN 1.0 and 1.5) and E1
  alone (tN 2.0); P_W gives 9 / 7 / 3 components. 6 distinct component sets, 12 books with the two weightings.
- Disclosed: the XAUUSD pre-UK-holiday cell is known from STREAM_M.md to decay in VAL; it stays in, as the rule says.
- The W2 weights hit the 2x clip for rare legs with high IS per-trade Sharpe (EURJPY QE-1, USDJPY BD-1 15-min); kept
  as declared.

## Post-hoc reporting additions (2026-10-06 01:51 UTC, after the 12 book results; reporting only, no re-selection)
- No book meets LIVE (best VAL power 2.01). All 12 meet the DEMO numbers formally, but every book contains E1 or its
  4-hour version (EURUSD short 09:00-13:00 London). Added, reporting only: (1) each book without its EURUSD leg
  ("rest of book"), IS and VAL, W1 and W2, to measure what the other legs add; (2) each leg's share of the book's
  daily variance (w_i^2 f_i sigma_i^2) and an effective number of bets by risk share, because the correlation
  participation ratio counts rare legs (3-13 trades a year) as full bets.
