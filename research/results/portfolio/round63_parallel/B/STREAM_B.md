# Stream B: intraday perp-spot basis mean reversion on Binance altcoins (round 63)

Written 2026-10-31 15:25 UTC. Declared in [HYPOTHESES_B.md](HYPOTHESES_B.md) (14:49 UTC; addendum 1 tick filter
14:53 UTC, both before any event or return was computed). HOLD (2025+) never requested or loaded.

## Answer
- **Rich side (short perp / long spot, no borrowing): none.** Best IS cell k100_H24 +89 bp (t 2.00, n 45), VAL +37 bp
  (t 0.60, n 28), 2023 -100 bp, 9 trades / yr; one step late -31 / -281 bp. k30 / k60 lose the 42-50 bp taker wall.
- **Cheap side (long perp / short spot via margin): k100_H24_cheap is the IS-chosen cell and formally passes the DEMO
  bar, not LIVE** (IS t 2.46 < 2.5). Draft: [PREREG_DRAFT_B_cheap_basis.md](PREREG_DRAFT_B_cheap_basis.md). It is a
  weak DEMO with three serious caveats (below): spot-borrow availability at exactly these moments is unknown, the edge
  sits mostly in the first hour after the observed dislocation (one-hour-late median is negative), and IS is 88 % five
  days (2021-05-19 Binance futures dislocation). I would not run it without the user deciding the borrow question.

## Setup (as declared)
244 coins (point-in-time top-60 perps by trailing 30-day volume, spot pair live, BTC / ETH / stables excluded, 246
symbols incl. delisted; 2 lacked enough data). Basis b = ln(perp close / spot close) per 1h bar (both legs >= 20
trades, relative tick <= 5 bp), deviation d = b - median(previous 168 h). Enter at the next bar open, exit at the open
after the first close where the deviation has halved, else after H hours. Funding explicit (stamps in (E, X]).
Costs: 30 bp fees + 4 x 3-5 bp half-spread; cheap side borrow 40 %/yr; Fed funds on the spot leg. Random: matched
coin / era / hold / side, 1,000 replications. t clustered by entry UTC day.

## All 12 cells (net bp per trade, t)
| cell | IS n | IS net (t) | VAL n | VAL net (t) | x1.5 IS / VAL | late IS / VAL | maker IS / VAL | random % IS / VAL |
|---|---|---|---|---|---|---|---|---|
| k30_H4_rich | 4542 | -25.9 (-20.9) | 330 | -22.6 (-2.86) | -50.6 / -46.0 | -37.1 / 51.0 | 4.5 / 5.3 | 100 / 100 |
| k30_H24_rich | 4093 | -22.7 (-16.2) | 238 | -10.0 (-1.01) | -47.4 / -33.7 | -35.4 / -72.8 | 7.6 / 18.4 | 100 / 100 |
| k60_H4_rich | 371 | 5.7 (0.67) | 101 | -19.2 (-1.03) | -19.0 / -42.3 | -28.1 / 261.5 | 36.2 / 8.0 | 100 / 98 |
| k60_H24_rich | 331 | 14.5 (1.62) | 49 | 13.1 (0.38) | -10.2 / -10.0 | -24.9 / -193.5 | 44.9 / 40.4 | 100 / 94 |
| k100_H4_rich | 65 | 45.8 (1.25) | 54 | 2.3 (0.07) | 21.3 / -20.3 | -39.4 / 529.4 | 75.8 / 28.4 | 100 / 97 |
| k100_H24_rich | 45 | 89.3 (2.00) | 28 | 36.8 (0.60) | 65.0 / 14.1 | -30.7 / -281.3 | 118.9 / 63.2 | 100 / 98 |
| k30_H4_cheap | 6530 | -19.4 (-2.26) | 1686 | -25.7 (-1.01) | -44.2 / -50.0 | -34.8 / -34.4 | 11.0 / 4.0 | 100 / 100 |
| k30_H24_cheap | 5606 | -14.5 (-1.46) | 1378 | 24.3 (3.67) | -39.2 / -0.1 | -32.4 / -8.5 | 16.0 / 54.0 | 100 / 100 |
| k60_H4_cheap | 943 | 78.5 (1.58) | 735 | -12.5 (-0.22) | 54.0 / -36.7 | 19.2 / -30.4 | 108.6 / 16.8 | 100 / 100 |
| k60_H24_cheap | 848 | 93.5 (1.74) | 585 | 101.2 (6.63) | 68.9 / 77.0 | 26.3 / 29.4 | 123.6 / 130.5 | 100 / 100 |
| k100_H4_cheap | 349 | 243.8 (2.22) | 425 | -14.1 (-0.14) | 219.4 / -38.2 | 100.2 / -27.9 | 273.7 / 15.1 | 100 / 100 |
| **k100_H24_cheap** | 303 | **286.5 (2.46)** | 333 | **174.6 (6.41)** | 262.0 / 150.5 | 118.4 / 68.6 | 316.5 / 203.8 | 100 / 100 |

Random matched entries lose ~-46..-60 bp (= cost); the max-over-cells random null is degenerate (p95 of max t: IS -2.95,
VAL 0.71), so "beats random" says only that the signal beats paying costs at random hours. Full table with gross /
funding / cost / ex-crash / Sharpe columns: [out/report_tables.md](out/report_tables.md); raw: out/cells.json,
out/trades_*.npz.

## Chosen cell k100_H24_cheap by year (net bp, n)
2020 +75 (40), 2021 +319 (263), 2022 +265 (111), 2023 +149 (145), 2024 +93 (77): 5 / 5 positive. Median +110 (IS) /
+96 (VAL), win rate 93 % / 91 %. Funding received +22 / +50 bp per trade (long perp on deeply negative funding).
Power at VAL size (111 trades / yr, 48 event-days / yr): per trade SR 0.270 x sqrt(200) = 3.82; per event-day 0.498 x
sqrt(86) = 4.63. Adverse perp move > 25 % in the hold: 32 IS / 10 VAL trades; > 50 %: 0 / 5; forced (delisting) exits 3.

## Robustness (information only; rule unchanged) - out of `code/robust.py`
| variant | IS n / net / median / t | VAL n / net / median / t |
|---|---|---|
| declared | 303 / 286.5 / 110.2 / 2.46 | 333 / 174.6 / 95.6 / 6.41 |
| ex crash windows (2020-03, 2021-05-17..24, 2022-05 LUNA, 2022-11 FTX) | 224 / 144.3 / 74.3 / 3.47 | 280 / 130.9 / 89.9 / 6.84 |
| ex crash and ex TRB / LUNA / FTT / ANC / SRM | 220 / 140.0 / 74.3 / 3.70 | 231 / 112.1 / 72.7 / 5.46 |
| exits after 1 h | 204 / 327.5 / 117.6 / 2.28 | 157 / 137.2 / 75.0 / 3.91 |
| holds > 1 h | 99 / 202.1 / 99.6 / 2.77 | 176 / 208.1 / 113.7 / 5.55 |
| no funding stamp crossed | 208 / 307.1 / 85.1 / 1.85 | 229 / 103.4 / 61.8 / 5.12 |
| **one hour late, declared** | 349 / 118.4 / **-23.1** / 1.22 | 369 / 68.6 / **-10.0** / 3.55 |
| one hour late, ex crash | 242 / **-7.7** / -38.3 / -0.45 | 296 / 35.7 / -16.7 / 3.27 |
| one hour late, ex crash, ex 5 coins | 238 / -7.1 / -37.7 / -0.41 | 238 / 20.1 / -21.5 / 1.89 |

## Why it is not LIVE, and why the DEMO is weak
1. IS t 2.46 < 2.5 (LIVE needs 2.5). The bar is not lowered.
2. **Executability of the short spot leg.** The perp trades > 100 bp below spot exactly when spot cannot be borrowed:
   squeezes (TRB 2023-09/10 with funding -2 %/stamp, UMA, OM 2024-07, REN), the FTX week (FTT, SRM), LUNA. 65 % of VAL
   P&L comes from TRB, LUNA, FTT, SRM, UMA. Binance margin inventory and hourly borrow rates for 2020-24 are not public,
   so availability is unmodelled; 40 %/yr borrow costs only ~1 bp per trade, the real risk is "no borrow" or rates of
   several %/day. The same P&L without borrowing needs a standing hedged inventory (long spot / short perp on each coin,
   unwound while the perp is cheap): capital-heavy, and that standing carry earns about the cash rate (round 58).
3. **The edge is the first hour.** Entry at the open right after the dislocated close carries most of it; one hour
   later the median trade loses in both eras and the IS mean outside crash windows is -7.7 bp. The close-to-close
   basis on a dislocated bar includes stale last trades and spreads far wider than the 3-5 bp half-spread modelled; a
   live bot would trade inside the bar (better) but at the real, wide, book (unknown). Round 62 had the same shape.
4. Concentration: IS top 5 days = 88 % of P&L (2021-05-19: SUSHI perp 7.28 vs spot 13.52, ALPHA, XLM, YFI, ALICE -
   the Binance futures dislocation, likely not fillable). Ex-crash IS t 3.47, but excluding crash windows is post hoc.
5. Data artefacts: LUNA perp settled flat at 0.008 while spot fell (+9,593 bp), ANC (-5,547 bp): they roughly cancel.

## Rich side: why it fails
Perp-rich dislocations on alts are rare at k >= 60 (16-34 / yr in VAL) and the rich side pays funding while it waits
(-30..-94 bp per trade in VAL); k30 captures ~20-55 bp gross against a 47-49 bp wall. Maker fees (19 bp) would make
k30 +5..+18 bp (info only, never graded).

## Pitfalls for later rounds
- Spot tick size on sub-cent coins (PEPE ~1 % tick) fakes basis; filter relative tick (addendum 1).
- Perps that are delisted / settled keep printing a flat price (LUNA 0.008); exits there are not real.
- The one-hour-late check is decisive for dislocation rules on 1h bars; report medians, not only means.

## What a user decision could unlock
- Approve a check of Binance margin borrow history (if any public endpoint exists without a key) or accept a
  "standing inventory" variant: keep long spot / short perp on the top-60 and unwind when the perp is cheap (no
  borrow; capital ~ inventory, graded on excess over cash). DEMO odds ~10-15 %, LIVE < 5 %.
- 1m or aggTrades (data.binance.vision) re-test of k100_H24_cheap entering 1 / 5 / 15 minutes after the hourly
  signal, to see how much survives the first minutes (round 62 shape). Cheap to run on a declared random sample.

## Data pulled
research/data/binance_basis/: perp_1h (246), spot_1h (246), funding (33 symbols not in data/binance/funding), all cut
at 2024-12-31 23:59:59 UTC (0 rows >= 2025 checked), 6,934 requests in requests.log (10 non-200: 4 x 429 back-offs,
timeouts, one 500; all retried), ~28 min. Universe list universe60.csv. Code: code/universe.py, pull.py, basis.py,
run.py, report.py, top_trades.py, robust.py. Correlation with C3 not computed (crypto basis vs JPY fix; expected ~0).
