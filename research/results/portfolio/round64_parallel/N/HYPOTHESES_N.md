# Stream N hypotheses: rule B executed from a standing inventory (round 64)

Written Sun Nov 1 08:54:35 UTC 2026 (from `date -u`), before any inventory P&L, funding sum or coverage number was
computed. Execution study, not a new rule: no PREREG, no HOLD. Eras IS 2020-01-01..2021-12-31, VAL 2022-01-01..
2024-12-31; every series cut at ts < 2025-01-01 at load (B's `basis._read`, CUT = 1735689600000). B's hold_* scripts are
not run.

## B unchanged
Code hashes checked 08:53 UTC (sha256, first 16) = PREREG_B: basis.py 46a5f647e1fc33f2, universe.py e4a9ae6a1a841feb,
pull.py 6234ca2300a998c8. N imports `basis.load()` and `simulate(coins, 100, 24, -1)` from round63_parallel/B/code
without edits (sys.path), and must reproduce IS 303 / +286.5 bp / t 2.46 and VAL 333 / +174.6 bp / t 6.41 before
anything else is reported.

## Mechanism (why the route could work)
B needs a spot short exactly when spot is hard to borrow. Selling coin already held is the same trade without a lender:
hold long spot / short USDT-M perp (equal notional, delta-neutral) in every coin B can fire on; when B fires, sell Q of
the spot and buy back Q of the perp (the position in that coin goes flat = B's long perp / short spot relative to the
inventory); when B exits, buy the spot back and re-short the perp (= rebuild). B's 4 legs are exactly the unwind and the
rebuild, so B's own cost model already pays the rebuild. What the route adds is the inventory itself: capital fully
paid on the spot leg plus perp margin, its funding (received when positive, paid when negative), spot-perp basis drift,
hedge resets as prices move, universe churn (build / unwind), delistings, and liquidation risk on the short perp. The
round 58 lesson says such a book must be graded on excess over the cash rate (DFF). Prior: always-on alt carry earned
well above cash in 2020-21 and roughly cash in 2022-24; the inventory needs ~60-75 coins x ~1.9 Q of capital, while B
adds ~111 trades/yr x ~1.75 % Q ~ 1.9 Q/yr (~1.5 %/yr on that capital). So the route is viable only if the inventory's
excess over cash is above about -1.5 %/yr; the question is purely numerical.

## Inventory model (declared; one primary configuration P)
- Unit: Q = B's trade notional (1 unit per leg). Everything is reported in Q and in % of capital.
- Held set: a coin (B's 244 loaded coins) is held while it is in B's point-in-time universe (`inU`, previous day's
  top-60); build at the open of its first `inU` hour; unwind after 48 consecutive hours outside `inU` (hysteresis
  against churn), or when its data ends / the perp stops trading.
- Target notional N* = 1.25 Q per leg (spot units u = N*/S, perp short u' = N*/F at the reset). Hourly check at each
  open: if the spot notional leaves [1.0 Q, 1.5 Q], reset both legs to N* (trade only the differences). Resets happen
  before a B entry at the same open, so every held coin can always deliver Q.
- Perp margin m = 0.5 x N* in USDT on the futures wallet (cross between coins not assumed). Liquidation proxy: if the
  perp 1h high exceeds the last reset price x (1 + m) / (1 + 0.05) (5 % maintenance), count a liquidation: charge 5 %
  of notional plus the unhedged spot move from the liquidation level to the next open, then rebuild at that open.
- Capital per held coin C = N* x (1 + m) = 1.875 Q. Cash benchmark: DFF on the capital of held coins, hour by hour
  (rate x 1/8760). Excess over cash = inventory net - cash.
- Costs per inventory trade (B's cost model per leg per side): spot 10 bp + hs, perp 5 bp + hs, hs = 3 bp if rank < 10
  else 5 bp (previous-day rank; out of universe = 5 bp). Build / unwind / reset / rebuild after liquidation pay this.
  Costs x1.5 reported.
- Funding: the short perp receives fund_j x u' x F_open(j) at each stamp (B's stamp mapping: stamp at hour boundary j,
  credited stepping from open j-1 to open j); negative funding is paid.
- MTM on hourly opens (B's entry / exit prices), missing opens forward-filled; if a leg has no open for 24 h, unwind at
  the last valid opens.
- Settled-perp guard (declared before looking, because B saw LUNA's perp print flat at 0.008 while spot fell): if the
  perp 1h bar has high == low for >= 6 consecutive hours while spot's close moves > 1 % over those hours, the perp is
  treated as settled: unwind the inventory at the open of the first such hour. Results reported with the guard
  (primary) and without it (info).

## B overlay (combined book)
- B's frozen trade list (k100_H24_cheap). In this route a B trade's P&L = B's price + funding - B's costs (30 bp + 4 hs);
  B's 40 %/yr borrow and its cash charge on the spot leg are dropped (no borrow; cash is charged once at book level on
  the capital). B's frozen net (with borrow and cash) is also shown.
- A B trade is covered if its coin is held at entry open e. Combined P&L = inventory P&L (all units, also during B
  windows) + covered B trades (exact additivity: during a B trade Q of the inventory is flat, which equals inventory
  + B's long-perp / short-spot leg).
- Combined daily equity (UTC days) -> max drawdown in Q and in % of capital, per era and 2020-24.

## Measures (all IS and VAL, per year 2020-24)
1. Inventory: price leg (basis drift = spot return - perp return), funding received / paid, costs by type (build,
   reset, unwind, liquidation), net, cash charge, excess over cash, in Q/yr and %/yr of mean capital; held coins
   (mean / max), capital (mean / max), resets / yr, liquidations, delisting / settled-perp events.
2. Concurrency of B: max, p99, p95, mean simultaneous open B trades (the capital a borrow route would need, in Q units of
   margin); in the inventory route capital scales with held coins, not with concurrency (say so).
3. Coverage per capital level: share of B trades and of B net P&L covered when the inventory is restricted to
   (a) the IS-chosen top-M coins by IS B-signal count, M in {10, 20} (chosen on IS, checked unchanged on VAL);
   (b) point-in-time volume rank < M, M in {10, 20, 30, 40, 60} (no look-ahead; held while previous-day rank < M,
   same 48 h hysteresis); each with its own inventory cost and capital.
4. Route cost: cost per year = cash on capital - inventory net (= minus excess); per covered B trade = that / covered B
   trades per year; compared with B's net per trade. Combined excess over cash per year and its daily Newey-West t
   (lag 10, info only, no bar).
5. Sensitivity (info): m in {0.25, 1.0} (capital vs liquidations), costs x1.5, band [0.9, 1.75] Q (fewer resets).
   Portfolio-margin note: if spot could collateralise the perp, capital ~ N* x 1.1.

## Grid / statistics
No selection except (a) M chosen on IS by signal count; everything else is declared above. No bar is graded here; the
answer is a cost and a decision for the user. Correlation with C3 is not needed (no DEMO cell).

## Expectations (written before computing)
- IS: alt funding ran 20-40 %/yr on many coins, cash ~0.2 %: inventory excess strongly positive; the route pays.
- VAL: funding lower and often negative in 2022 (bear) and in squeeze coins; cash 2-5 %. Expect excess around -2 to
  +3 %/yr, i.e. the route's cost in VAL of roughly 0-3 Q/yr against B's ~1.9 Q/yr; the verdict is likely "viable only
  if the inventory carry itself is accepted as a position", i.e. the inventory decides, not B.
- Coverage: B's VAL P&L is concentrated (TRB, LUNA, FTT, SRM, UMA = 65 %); IS-chosen top-M likely covers < 40 % of VAL
  P&L, since the squeeze coins change from year to year.
- Risks the model does not capture: intraday ADL on the short perp, venue failure, depth at reset times in crashes.
