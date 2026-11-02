# Stream N: rule B executed from a standing inventory (round 64, execution study)

Written Sun Nov 1 09:03:01 UTC 2026 (from `date -u`). Declared in [HYPOTHESES_N.md](HYPOTHESES_N.md) (08:54 UTC, before
any inventory number was computed). IS 2020-21 and VAL 2022-24 only; every series cut at ts < 2025-01-01 by B's own
loader (asserted); B's hold_* scripts not run, no 2025-26 value looked at. No network, no git.

## Answer
**Not viable. In 2022-24 the inventory route costs about 6 Q per year more than leaving the capital in cash, where Q is B's trade
size. B's trades earn about 1.6 Q per year back.** Here is the declared configuration P: 59 coins held, 110.7 Q of capital, 0.5 x notional
as perp margin. In VAL the inventory's own net is -3.31 Q/yr against 4.38 Q/yr of cash, so its excess over cash is
**-7.69 Q/yr (-6.9 %/yr of capital, Newey-West t -4.30)**. The covered B trades add +1.59 Q/yr. The combined book's
excess over cash is **-6.10 Q/yr (-5.5 %/yr, t -3.96)**. Put another way, the route costs **~700 bp of Q per covered B
trade**, while a B trade earns ~+144 bp in this route. Every variant loses in VAL: cheapest m = 1.0 at -3.4 %/yr, and a
portfolio-margin proxy at -2.0 Q/yr. Every capital level loses too (-7.5 to -8.5 %/yr). 2020-21 looks good (+17.8 %/yr
excess), but only because the inventory was itself a profitable alt funding carry in 2021: funding was 39 %/yr of
notional and cash 0.1 %. That is the carry premium round 58 found has gone to cash since 2024-25. It is not B.

**What the user must decide:** the inventory route only makes sense if the user wants to own an always-on alt carry
book in its own right. In 2022-24 that book earned below cash. B stays cheap only with a lender of the coin on
**Binance spot**: margin borrow enabled on the account, or a Binance loan product. With a lender, B's capital is only
the margin on its concurrent trades (usually 1-2, at most 33-48 in crash hours). Otherwise the choice is to wait for
Binance borrow support. Taking coin from another venue does not help: the edge is Binance spot catching down to the
Binance perp (B, BX, BY).

## B unchanged
Hashes checked 08:53 UTC: basis.py 46a5f647e1fc33f2, universe.py e4a9ae6a1a841feb, pull.py 6234ca2300a998c8
(= PREREG_B). N imports `basis.load()` / `simulate(coins, 100, 24, -1)` from round63_parallel/B/code without edits.
Both runs reproduce B: IS 303 / +286.5 bp / t 2.46, VAL 333 / +174.6 / t 6.41 (asserted in `code/run.py`).
In this route a B trade's P&L is price + funding - B's costs. B's 40 %/yr borrow is dropped, and cash is charged once
on the book's capital.

## Model (as declared; Q = B's trade notional)
- Long spot / short USDT-M perp at N* = 1.25 Q per leg in every coin of B's universe while it is in the point-in-time
  top-60, with 48 h hysteresis. A coin is unwound when it leaves the universe, when its data ends, or when its perp
  stops trading (settled-perp guard).
- Hourly reset to N* when spot notional leaves [1.0, 1.5] Q. Perp margin is m x N*; capital per held coin is N*(1+m).
- Liquidation proxy: the 1h perp high reaches the reset price x (1+m)/1.05. The charge is 5 % of notional plus the
  spot leg unhedged until the next open.
- Costs are B's cost model per leg (spot 10 bp, perp 5 bp, plus a 3/5 bp half-spread). Funding is taken at the real
  stamps. Cash is DFF on capital, charged hourly.
- Combined book = inventory (all units) + covered B trades. This sum is exact: while a B trade is open, Q of the coin's
  inventory sits flat.

## Main table (Q per year; capital and DD in Q)
| config | era | capital (coins) | price leg | funding | build+reset+unwind | liq | inv net | cash | inv excess | B route | B trades / P&L covered | combined excess (% cap) | t_nw | combined max DD (% cap) | route cost per B trade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **P** (m 0.5) | IS | 77.7 (41.5) | -3.18 | +16.86 | 2.06 | 2.05 | +9.58 | 0.06 | +9.51 | +4.35 | 100 % / 100 % | +13.87 (+17.8 %) | +3.77 | 1.8 (2.4 %) | -628 bp (gain) |
| **P** | VAL | 110.7 (59.0) | +0.79 | +0.27 | 2.70 | 1.67 | **-3.31** | 4.38 | **-7.69** | +1.59 | 99 % / 81 %* | **-6.10 (-5.5 %)** | -3.96 | 13.3 (12.0 %) | **+697 bp** |
| costs x1.5 | VAL | 110.7 | +0.79 | +0.27 | 4.05 | 1.69 | -4.68 | 4.38 | -9.06 | +1.59 | | -7.47 (-6.8 %) | -4.88 | 15.0 | +821 bp |
| m 1.0 | IS | 103.7 | -2.19 | +16.85 | 2.08 | 0.12 | +12.46 | 0.09 | +12.38 | +4.35 | | +16.73 (+16.1 %) | +4.47 | 1.0 | -818 bp |
| m 1.0 | VAL | 147.5 | +2.14 | +0.24 | 2.72 | 0.37 | -0.71 | 5.84 | -6.54 | +1.59 | | -4.96 (-3.4 %) | -2.87 | 9.0 (6.1 %) | +593 bp |
| no guard | VAL | 110.7 | +0.60 | +0.26 | 2.71 | 1.68 | -3.53 | 4.38 | -7.91 | +1.96 | 100 % / 100 % | -5.95 (-5.4 %) | -3.79 | 13.0 | +712 bp |
| m 0.25 | VAL | 92.2 | | | | 77.75 | -82.31 | 3.65 | -85.96 | | | -91.5 % | | | infeasible |
| band [0.9, 1.75] | VAL | 110.7 | | | | 17.43 | -18.28 | 4.38 | -22.66 | | | -19.0 % | | | infeasible |
| info: rehedge at liq | VAL | 110.7 | +0.10 | +0.24 | 2.73 | 1.64 | -4.03 | 4.38 | -8.40 | +1.59 | | -6.82 (-6.2 %) | -4.91 | 14.8 | +762 bp |
| info: m 1.0 + rehedge | VAL | 147.5 | +0.05 | +0.24 | 2.73 | 0.36 | -2.81 | 5.84 | -8.64 | +1.59 | | -7.05 (-4.8 %) | -5.76 | 11.7 | +783 bp |
| info: 14-day hysteresis | VAL | 119.9 (63.9) | +0.61 | +0.66 | 2.39 | 1.74 | -2.86 | 4.73 | -7.59 | +1.59 | | -6.00 (-5.0 %) | -3.78 | 12.5 | +688 bp |
| portfolio-margin proxy (m 1.0, capital N* x 1.1, liq removed) | VAL | 81.1 | | | | 0 | -0.34 | 3.21 | -3.55 | +1.59 | | -1.96 (-2.4 %) | | | +322 bp |

\* Two of B's 333 VAL trades fire on a perp that had already stopped trading. They are LUNA 2022-05-12 16:00 (+9,593 bp,
the artefact B already flagged) and FTT 2022-11-14 05:00 (+1,457 bp: the FTT perp printed 0 trades from 05:00, while
spot kept trading). No route can fill them. Excluding them, B's fillable VAL net is ~+142 bp per trade, and P covers
100 % of the fillable trades and P&L. The m 0.25 and band 1.75 rows break down because their reset band is looser than
their margin: the short is liquidated before the reset fires (3,000+ liquidations). They are not real choices.

Full table, all 15 configurations: [out/report.txt](out/report.txt).

## Per year (configuration P, Q/yr)
| year | capital | coins | price leg | funding (%/yr of notional) | costs | inv net | cash | inv excess | B route (n) | combined excess (% cap) | DD combined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020 | 44.7 | 23.8 | -0.13 | +4.85 (+16.3 %) | 0.68 | +4.03 | 0.04 | +3.99 | +0.31 (40) | +4.30 (+9.6 %) | 0.4 |
| 2021 | 110.9 | 59.2 | -6.23 | +28.92 (+39.1 %) | 7.54 | +15.14 | 0.09 | +15.06 | +8.41 (263) | +23.47 (+21.2 %) | 1.8 |
| 2022 | 110.6 | 59.0 | +4.46 | -5.51 (-7.5 %) | 6.00 | -7.05 | 1.86 | -8.91 | +1.85 (109) | -7.06 (-6.4 %) | 6.6 |
| 2023 | 111.1 | 59.3 | -1.38 | -2.00 (-2.7 %) | 3.67 | -7.05 | 5.59 | -12.64 | +2.19 (145) | -10.45 (-9.4 %) | 7.1 |
| 2024 | 110.3 | 58.8 | -0.70 | +8.31 (+11.3 %) | 3.47 | +4.14 | 5.67 | -1.54 | +0.72 (77) | -0.82 (-0.7 %) | 0.8 |
The combined excess is positive in 2 of 5 years (2020, 2021). Only 2024 had funding above cash, and the costs ate it.

## Why it loses (VAL, P)
- **Funding is ~0 on B's universe.** The top-60 by volume is full of squeeze coins with deeply negative funding. The
  worst inventory coins are TRB -2.68 Q (funding -1.79), BLZ -1.57, FTT -1.35, AXS -1.19 and WAVES -0.91. This is
  adverse selection: the coins where B fires are the coins where a standing short-perp inventory pays funding.
- **The inventory is short B in B's own windows.** Outside B windows, price plus funding earns +2.67 Q/yr against 3.87
  Q/yr of costs. Inside B windows the inventory loses -1.61 Q/yr ([out/split_P.txt](out/split_P.txt)). So B's +2.12
  Q/yr gross mostly cancels a loss the inventory would otherwise take; it adds little on top.
- **Costs are 4.4 Q/yr.** Universe churn costs 1.6 Q/yr (~255 builds and ~275 unwinds a year). Resets cost 1.1 Q/yr (~1,600
  a year). Liquidations at m 0.5 cost 1.7 Q/yr (18 a year, all in squeezes and crashes).
- **Cash is 4.38 Q/yr** (4 % on 110 Q).
- Liquidations are a lottery. The unhedged hour after a liquidation gave windfalls in UNFI 2022-06-07 (+3.5 Q) and
  LUNA 2022-05-11 (+3.2 Q), and losses elsewhere. The rehedge variant removes the lottery and lands 0.7 Q/yr worse.

## Capital, concurrency, coverage
- **Capital per unit of B trade size: ~111 Q (m 0.5), ~148 Q (m 1.0), ~81 Q with portfolio margin.** A $1,000 B trade
  therefore needs ~$110-150k of capital in the inventory route. Capital scales with the number of coins held (59), not
  with B's concurrency, because each coin needs its own spot.
- **B's concurrency** (what a borrow route needs in margin): mean 0.04 open trades, p99 1, p99.9 2, max 33 (VAL) / 48
  (IS, 2021-05-19). B has a trade open in 3.2 % of VAL hours.
- **Coverage per capital level, VAL** (inventory only in coins with previous-day volume rank < M; no look-ahead):

| M | capital Q | B trades covered | B P&L covered | combined excess %/yr of capital |
|---|---|---|---|---|
| 10 | 15.6 | 22 % | 27 % | -7.6 % |
| 20 | 34.8 | 39 % | 43 % | -8.5 % |
| 30 | 54.0 | 54 % | 51 % | -7.6 % |
| 40 | 72.9 | 64 % | 56 % | -7.5 % |
| 60 (P) | 110.7 | 99 % (100 % fillable) | 81 % (100 % fillable) | -5.5 % |
In IS the same levels give +13.1 to +15.8 %/yr, all from 2021 funding.
- **IS-chosen subset** (top-M coins by IS B-signal count, chosen on IS, checked on VAL unchanged). Top 10 (DOGE, RUNE,
  EGLD, SOL, AXS, AVAX, IOTA, OMG, ONT, SUSHI) covers 30 % of IS trades but **1 % of VAL trades and 0 % of VAL B P&L**.
  Top 20 covers 48 % IS and 4 % VAL trades (2 % of the P&L). VAL combined excess: -8.2 % and -6.8 %/yr. **Fails**: the
  squeeze coins change from year to year (VAL is TRB, LUNA, FTT, SRM, UMA).
- **Combined drawdown**: VAL max DD 13.3 Q (12 % of capital), counted on the excess over cash 19.9 Q. IS 1.8 Q. Worst
  day -1.69 Q (2022).

## Pitfalls
- The perp margin and the reset band must be consistent. If the band lets price rise further than the margin can
  absorb, the short is liquidated over and over (m 0.25 and band 1.75 lose 20-90 %/yr). Hourly bars understate how
  fast a live bot must react.
- Dead perps: in 9 coins (LEND, LUNA, FTT, SRM, COCOS, TOMO, RNDR, MATIC, UNFI) the 1h perp kline keeps printing a flat
  price with 0 trades after delisting or migration. B's LUNA and FTT VAL trades enter on such bars. Check the trade
  count (column n) before trusting a fill.
- A standing hedge is the mirror image of any convergence rule on it. Report the inventory's P&L inside and outside
  the rule's windows, or the rule looks additive when it is not.

## Files
- Code: [code/inventory.py](code/inventory.py) (inventory simulator, settled-perp guard, NW t), [code/run.py](code/run.py)
  (configs, B overlay, coverage, concurrency, drawdowns), [code/report.py](code/report.py) (tables),
  [code/split.py](code/split.py) (inside / outside B windows), [code/diag.py](code/diag.py) (liquidation list,
  uncovered trades).
- Output: out/results_*.json (per config / era / year, per coin), out/report.txt, out/split_P.txt, out/diag_P.txt
  (all 100 liquidations in P), out/daily_P.npz (daily inventory, B and cash series), out/run_a.log, out/run_b.log.
- Data: none pulled. Read research/data/binance_basis/{perp_1h,spot_1h,funding}, research/data/binance/{perp_1d,funding,
  spot_first.csv}, research/data/rates/DFF.csv, all through B's loader with the 2025 cut.
