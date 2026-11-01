# Stream BX hypotheses: borrow-free hedge of stream B's cheap-basis signal with the Bybit linear perp

Written 2026-10-31 15:58 UTC (from `date -u`), before any Bybit 1h kline was requested and before any BX return was
computed. Inputs read before this file: stream B's reports (STREAM_B.md, PREREG_B_cheap_basis.md incl. its HOLD result)
and code; the names of the 252 symbols in research/data/bybit/funding/ (file names only).

## Contamination statement (read first)
Stream B's HOLD (2025-01-01..2026-10-29) has already been opened and seen: 429 trades, +213.5 bp, t 14.4, of which
price convergence +139.5 and funding received +126.0 bp. BX uses the same frozen signal, so a BX HOLD would trade the
same signal hours / days. A BX HOLD is therefore not an independent test of the signal. What it would still add is a
test of the substitution only: whether (a) the Bybit perp tracks spot rather than the Binance perp over the hold
(i.e. the dislocation is Binance-specific) and (b) the Bybit funding paid by the short does not eat the Binance funding
received. Those two Bybit quantities were not looked at in B's HOLD, so they are unseen, but they are correlated with
what B saw (the squeeze states). BX never opens HOLD; the coordinator decides whether that partial test is worth it.

## Mechanism
B's signal: on a Binance altcoin, the USDT-M perp trades > 100 bp below Binance spot relative to the 168 h median of
the basis. If the dislocation is a Binance-perp event (liquidation cascade / forced selling on the Binance perp book,
which is the largest alt perp venue), the Bybit linear perp of the same coin is held near spot by Bybit's own
arbitrageurs and index, so long Binance perp / short Bybit perp captures the same convergence without a spot borrow.
If instead the dislocation is market-wide across perps (all venues' perps cheap vs spot, e.g. a cross-venue short
squeeze in reverse / heavy hedging demand), the Bybit perp is cheap too and the perp-perp spread captures little; the
declared variant tests that directly by requiring Bybit to be richer at the signal. Funding: B's long perp received
the deeply negative Binance funding; a short Bybit perp pays Bybit's funding if it is negative too, so the funding leg
nets to (Bybit rate - Binance rate) per stamp. If both venues' rates are equally negative, the funding leg is ~0 and the
rule lives on price convergence alone.

## Data (pull 2020-01..2024-12-31 23:59:59 UTC only; 2025+ never requested or loaded)
- Trades: rerun B's frozen `simulate(coins, 100, 24, -1)` (B/code/basis.py, unchanged, imported read-only) for IS and
  VAL; B's IS / VAL trade list (n 303 / 333) is the event list. Lag-1 trades for the one-hour-late check likewise.
- Bybit linear 1h klines `api.bybit.com/v5/market/kline?category=linear&interval=60` for each traded coin over merged
  windows [entry - 48 h, exit + 48 h] (and the lag-1 windows), end capped at 2024-12-31 23:59:59.999 UTC. Symbol map:
  Binance perp name; for 1000X perps try 1000XUSDT then X1000USDT then XUSDT (scale detected from the median price
  ratio rounded to a power of 10, a level check, not a return). Saved to research/data/bybit_1h/<SYM>.csv with a
  requests.log. Public, no key, >= 0.25 s between requests, back off on 429 / 403 = stop.
- Bybit funding: research/data/bybit/funding/<SYM>.csv; symbols missing there are pulled from
  `/v5/market/funding/history` into research/data/bybit_1h/funding/ over the same windows. All series cut at
  ts < 2025-01-01 at load.
- Binance perp opens, Binance funding, universe rank: B's loader (research/data/binance_basis, binance/funding).
- Coverage reported: share of B's IS / VAL trades whose coin has Bybit 1h bars at both entry and exit open hours
  (bar with volume > 0 at the entry hour). Uncovered trades are dropped (reported), not filled.

## Rule (fixed; no new grid)
- Signal, entry hour e, exit hour x: exactly B's k100_H24_cheap (same universe, basis, k = 100 bp, halving exit with
  the median frozen at entry, H = 24 h, one trade per coin). The exit rule stays on the Binance perp-spot basis.
- Position: long Binance perp, short Bybit linear perp, 1 unit notional each, entry at the open of bar e on both
  venues, exit at the open of bar x. If the Bybit bar at x is missing, exit Bybit at the next bar with an open within
  24 h (else the trade is dropped as uncovered).
- P&L per unit: (F_x / F_e - 1) - (Y_x / Y_e - 1) - sum Binance rates on stamps in (e, x] + sum Bybit rates on stamps
  in (e, x] - costs - carry. (Long Binance receives -rate; short Bybit receives +rate, i.e. pays it when negative.)
- Decomposition: price convergence = the two price returns; funding = Binance leg and Bybit leg separately.
- Primary rule P: all covered B trades. Declared variant V50: additionally require ln(Y_c,h / F_c,h) >= 50 bp at the
  signal close h (Bybit perp at least 50 bp richer than the Binance perp at the signal; scale-adjusted). Selection
  between the two follows B's rule (higher IS t among cells with IS net > 0); max-over-2 null reported.

## Costs
- Taker fees: Binance perp 0.05 % x 2 + Bybit linear 0.055 % x 2 = 21 bp.
- Half-spreads: Binance leg as in B (3 bp if universe rank < 10, else 5 bp, per side); Bybit leg 5 bp per side flat
  (Bybit alt books are thinner than Binance's; no rank available there) -> 4 x hs total = 32-40 bp all-in at 21 bp
  fees, i.e. 37-41 bp vs B's 42-50 bp.
- No borrow. Carry: cash rate (DFF) x hours / 8760 on 1 unit (margin capital tied up, round 58 lesson). Costs x1.5 and
  one hour late (B's lag-1 trades) checked.

## Random benchmark
B's matched random entries adapted: for every BX trade, a random entry hour on the same coin, same era, hold length
L, coin in universe and Bybit bar present, same long-Binance / short-Bybit P&L incl. funding and costs; 1,000
replications; share of replications with mean below the actual mean.

## Statistics and bars (unchanged)
Net per trade (bp), t clustered by entry UTC day, per year 2020-24, x1.5, one hour late, random %, power at VAL size.
LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, beats >= 95 % random, HOLD power >= 3, positive at x1.5 and
late. DEMO: IS t >= 2.0, VAL net > 0, beats >= 90 % random.

## Power arithmetic (before data)
- B at VAL: 111 trades / yr, per-trade SR 0.270, 48 event-days / yr. Bybit coverage c is unknown; Bybit listed few
  alt USDT perps before 2021, so IS coverage may be low (a sizable IS sample is not guaranteed; IS t >= 2 needs n
  large enough: with B's IS per-trade SR ~0.14 (t 2.46 on 303 trades, day-clustered), IS t 2.0 needs ~200 covered IS
  trades at the same SR, unless the perp-perp hedge cuts variance).
- HOLD trades ~ 1.8 yr x c x 111 (B's HOLD actually had 429, higher activity). Per-trade power = SR_BX x sqrt(n_HOLD):
  c = 0.7 -> n ~ 140 (or ~300 at B's HOLD rate) -> SR_BX >= 0.25 (0.17) needed for power 3.
- Expected funding leg ~0 if Bybit rates are equally negative; B's VAL funding was +50 of +175 bp, so BX VAL net may
  be ~ +125 bp minus any convergence lost on the Bybit leg, plus ~9 bp lower costs.
- Which bar is reachable: DEMO if IS covered sample is large enough and the Bybit perp is not dislocated with Binance;
  LIVE needs IS t >= 2.5 on a covered subset of a signal whose full IS t was 2.46, so LIVE is only reachable if the
  hedge removes a lot of variance (likely, since the perp-perp spread has no spot-specific noise and the funding legs
  partly cancel), not by sample size.
