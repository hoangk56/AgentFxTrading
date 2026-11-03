# HYPOTHESES_U: is an unfinished auction a magnet? (book setup #5)

Written 2026-11-03 16:52 UTC (from `date -u`), before any revisit rate or return was computed. Only metadata (file
shapes, k) had been read.

## Mechanism (the book's claim)
A 30m swing high whose top footprint row still shows both aggressive sellers (bid > 0) and aggressive buyers (ask > 0)
is an "unfinished auction": the auction did not find the price where one side stops trading, so the market should
come back to finish it. A "finished" high (one side = 0 at the top row) should be less attracting. The book uses this
as a magnet (TP extension, stop placement, no-trade warning). If unfinished turns are not revisited more often than
finished turns at the same distance and volatility, every magnet use is void.

## Data and definitions
- Symbols BTCUSDT (k 3 bp), ETHUSDT (k 4 bp), SOLUSDT (k from `SOL_READY` derived files, from 2020-09). 30m bars
  from `fp.bars(fp.load_minutes(sym), 30)`; 30m footprint from `fp.load_fp(sym, 30)`; `fp.unfinished` for the flags.
  Shared layer imported by path, unchanged.
- **Turn (swing high):** 30m bar i with high_i strictly greater than the highs of bars i-4..i-1 and i+1, i+2 (ties
  are not turns); bars i-4..i+2 must be consecutive (30 minutes apart). Mirror for swing lows (strictly lower lows).
  A bar can be both a swing high and a swing low (two turns).
- **Confirmation:** close of bar i+2 (time t_c = start of bar i+2 + 30 min); price at confirmation = close of i+2.
- **Level row:** the top row L of bar i (swing high) / bottom row of bar i (swing low) from `fp.unfinished`.
  Unfinished = bid > 0 and ask > 0 in that row (`uh` / `ul`); finished otherwise. Level edge (near edge as seen from
  the confirmation price): swing high -> lower edge of row L, `row_price(L, k, "low")`; swing low -> upper edge of
  the bottom row B, `row_price(B, k, "high")`.
- Turns whose confirmation close is already inside or beyond the level row (high: close >= lower edge of L) are
  dropped (the revisit would be trivial). Turns where bars i+1 / i+2 touched the row before confirmation are kept and
  counted (reported).
- **30m ATR14:** mean of the true ranges of the 14 30m bars ending with bar i+2 (known at confirmation), in bp of the
  confirmation close. **Distance** = |level edge / close - 1| in bp, divided by ATR14 -> "distance in ATR".
- **Strata (matching):** symbol x side (high / low) x distance decile x ATR tercile. Decile and tercile edges are
  computed per symbol from its IS turns (both labels pooled) and applied unchanged to VAL.

## 1. Statistic (main answer)
- Revisit_H = 1 if any 30m bar i+3 .. i+2+H trades into the level row (swing high: bar high >= lower edge of L; low:
  bar low <= upper edge of B), H in {12, 48} bars (6 h, 24 h).
- Estimate: matched difference D_H = mean(revisit | unfinished) - sum over strata (n_unf,s / N_unf) x
  mean(revisit | finished, s) (strata with no finished turn are dropped from both). Day-clustered SE from the
  linearised estimator (influence of each turn, summed per UTC day of confirmation). Also a permutation p: shuffle
  labels within strata, 200 draws.
- Reported by era (IS / VAL), year, symbol, side. Information only: revisit "beyond the extreme" (high > high_i).
- **Decision rule for the magnet:** the magnet is real only if D_H > 0 with clustered t >= 2.5 in IS and t >= 1.5
  in VAL pooled over symbols, same sign in each symbol. Otherwise the book's magnet uses (TP extension, stop placement,
  no-trade warning) are declared void. Effect size matters too: a D of +1 point when the base rate is 60 % is not a
  usable magnet; I report the size.

## 2. Trade cells (8 declared: 4 unfinished + 4 finished controls)
- At confirmation, enter **toward** the level: long under a swing high, short above a swing low. Entry = market (taker)
  at the close of bar i+2.
- TP = one row before the level row: swing high -> lower edge of row L-1, `row_price(L-1, k, "low")`; swing low ->
  upper edge of row B+1. Limit (maker), filled only if a 1m bar trades through it (high > TP for a long). If the entry
  price is already at or beyond TP, no trade.
- Stop at the same distance on the other side (entry - (TP - entry) for a long). Stop fill = stop price or the 1m open
  if it gaps beyond, minus 1 bp slippage (BTC, ETH) / 2 bp (SOL), taker fee. In the same minute stop before TP.
- Time stop: the 1m close at t_c + H x 30 min (taker), H in {12, 48}.
- Distance filter, two cells: **D0** = every turn with a TP; **D1** = TP distance in [0.10, 0.30] x daily ATR14 (daily
  true range of UTC days, mean of the 14 days before the entry day; the book's 10-20 % stop band widened to its
  target band).
- Cells = H {12, 48} x filter {D0, D1} x label {unfinished, finished}. The 4 unfinished cells are the candidates; the 4
  finished cells are their controls. One open trade per symbol per cell (turns that confirm while a trade is open are
  skipped).
- Fees: maker 2 bp (TP), taker 5 bp (entry, stop, time stop); funding at each 00 / 08 / 16 UTC stamp held (long pays
  the rate). Stress: fees x 1.5. One step late: market entry at the close of the 1st minute after confirmation (TP and
  stop prices unchanged; no trade if that price is already at / beyond TP).
- Net in bp per trade and in R (R = TP distance). t clustered by UTC day of entry. Pooled over symbols for the verdict,
  each symbol reported.

## Control / random benchmark (this stream's version, declared)
The trade's outcome depends only on the turn and its distance, so a "random level at the same distance" would be the
same trade. The benchmark that answers "is it the unfinished flag or just any swing level" is therefore:
- **Label permutation:** shuffle the unfinished / finished labels within strata (symbol x era x side x distance decile
  x ATR tercile), rebuild the unfinished cell with the one-open-trade rule, 1,000 draws; percentile of the real net t
  (and of the real unfinished - finished difference). Max-over-cells null: per draw the max t over the 4 candidate
  cells, compared with the real max.
- The finished cell (same pipeline) is reported next to each unfinished cell; the difference (unfinished - finished
  net per trade, day-clustered t via a two-sample cluster SE) is the answer, not the raw net.

## Bars (unchanged from BRIEF)
A candidate cell passes only if the unfinished cell itself passes the bars and its difference vs the finished control
is > 0 in IS and VAL:
- LIVE: net > 0 IS and VAL, positive at fees x1.5 and one step late, t >= 2.5 IS / >= 1.5 VAL, >= 2/3 of years
  positive (2020-2024, pooled), permutation percentile >= 95, HOLD power at VAL size >= 3
  (power = mean / sd per trade at VAL x sqrt(VAL trades x 22 / 36)).
- DEMO: t >= 2.0 IS, net > 0 VAL, permutation percentile >= 90.
Parameters are fixed above; nothing is tuned on VAL. If a cell passes: PREREG_DRAFT_<name>.md and stop (no HOLD).

## Power arithmetic (before data)
BTC median IS 30m range ~60 bp (k = 3 bp = range / 20). Typical TP distance ~0.5-1.5 30m ATR = ~30-90 bp; round-trip
cost ~7 bp (TP) to ~11 bp (stop) -> break-even P(TP first) ~ 0.5 + 9 / (2 d) ~ 0.6 at d = 50 bp. sd per trade ~ d.
With one open trade per cell, expect ~1-3 k trades per symbol-year at H 12, fewer at H 48. IS pooled n ~ 5 k:
t 2.5 needs mean / sd >= 0.035 (~1.8 bp net on 50 bp). HOLD power 3 at VAL n ~ 8 k -> HOLD n ~ 4.9 k needs
mean / sd >= 0.043 at VAL size; with the round 58-66 lesson (HOLD t ~ 1/4 of VAL) a cell needs VAL t well above 6 to
have a realistic HOLD pass. The statistic itself has ample power: ~20-30 k turns per symbol, a 2-point difference in
revisit rate is t ~ 3-4 per symbol.

## Pitfalls I check
- The top row of a bar is known only at bar i's close and the turn only at i+2's close: nothing is used earlier.
- Unfinished share depends on k (wider rows -> more two-sided top rows); k is fixed by the shared rule.
- Distance matching is essential: unfinished highs may sit closer to the close (e.g. bars that reverse quickly).
- 2020-03 crash and 2021-05 crash: reported per year.

## Addendum 2026-11-03 16:55 UTC (before any revisit rate or return was read): own 30m footprint flags
While building turns I found that `build_fp.py` stores `fp_key = minute * 100000 + bucket`, and for BTC above
$22,026 the 1 bp bucket (floor(1e4 ln p) >= 100000) overflows into the minute field (BTCUSDT/2021-06.npz: key % 1e5 in
2674..6313, key // 1e5 = minute + 1). The shared `derived/BTCUSDT_tf30.npz` therefore carries wrong rows (row_price
~ $1-40) and a one-minute shift of trades between 30m bars for most of 2021-2024. Reported to the coordinator.
Change (declared): the top / bottom rows and unfinished flags are built in `U/code/build_turns.py::own_unfinished`
from the month files with rows = bucket // k (k from the derived file), decoding BTC keys with key % 1e5 < 50000 as
bucket + 100000 and minute - 1 (every real BTC bucket is >= ~81.6k). ETH / SOL keys are used as stored, and for ETH the
own build is asserted equal to `fp.unfinished(fp.load_fp(...))` exactly (passes). Checks: the top row equals the row of
the 30m 1m-bar high on 100 % of bars for BTC and ETH. Nothing else changes.
Update 2026-11-03 (after the coordinator fixed `fp.split_key` and rebuilt derived/BTCUSDT_tf30.npz, still before any
revisit rate or return was read): `build_turns.py` uses `fp.unfinished(fp.load_fp(sym, 30))` again; the own decode is
kept only as a cross-check and is asserted identical to the shared layer for BTC and ETH (passes).

## Addendum 2026-11-03 17:02 UTC (after the BRIEF note on 1m-cache holes; BTC / ETH revisit rates and trade nets had been
computed once with the minute-built daily ATR and no hole filter; SOL not yet read)
- Daily ATR14 (filter D1) now comes from `research/data/binance/perp_1d/<SYM>.csv` (true range in bp of the previous
  close, mean of the 14 days before the entry day), as the BRIEF now requires.
- A turn is dropped if a hole > 30 min in the 1m cache lies in its life: from the start of bar i-13 (the ATR30
  window) to t_c + 48 bars (the longest window; used for both H). Holes: BTC 24 (609.5 h), ETH 7 (169.6 h), SOL 7
  (169.6 h). Turns dropped: BTC 237, ETH 77, SOL 71. Remaining turns: BTC 17,195, ETH 17,472, SOL 14,556 (SOL k 7 bp).
- The own fp_key decode was removed from the code (it matched the fixed shared layer exactly; BRIEF: never read
  fp_key without `fp.split_key`). No rule, cell or bar changed. The earlier BTC / ETH run is superseded by this one.
