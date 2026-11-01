# Round 63, stream V: crypto volatility risk premium (short delta-hedged Deribit straddles / strangles)

Written 2026-10-31 (work 14:30-14:50 UTC from `date -u`). Hypotheses: [HYPOTHESES_V.md](HYPOTHESES_V.md) (V1 / V2
declared 14:30; V3 added at 14:41 after the BTC V1 / V2 results, with the selection disclosed). HOLD was never loaded.
Every series is cut at ts < 2025-01-01 and every request ended <= 2024-12-31 23:59:59 UTC.

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)
None of the 28 cells passes the DEMO bar. The best IS t is +1.50 (BTC 7d, 4-hourly hedge, V2 tau 10), and that cell
loses in VAL (t -0.68). The best VAL t is +1.14 (BTC 30d, V2 tau 10), but its IS t is only 0.68-1.04. Both maxima are
inside the max-over-28-cells null (IS p50 1.29, VAL p50 1.24). Power at VAL size is <= 0.90 against the 3 that LIVE
needs (that requires an annual Sharpe of ~2.2; the best VAL annual Sharpe here is 0.80).

Why it fails: the premium exists in DVOL but not in the options a weekly ATM / 25-delta seller actually sells.
- **DVOL is above realised vol.** On IS Fridays BTC DVOL averaged 83.7 against 73.0 realised over the next 30 days;
  in VAL it was 56.5 against 47.0. DVOL was above the next-30-day realised vol on 74-78 % of Fridays.
- **The traded ATM options are not.** At the Friday 08:30 UTC entry, the implied vol of the traded ATM straddle is
  only 0.85 x DVOL (7d) or 0.90 x DVOL (30d), about the realised vol that followed. The 25-delta legs sit at
  0.87-0.94 x DVOL. DVOL is a variance-swap index over the whole strike strip, so its gap over realised vol sits in
  the far wings (the tail insurance).
- **Costs take what is left.** After delta hedging, a BTC 7d straddle sold at mid earns ~+0.75 % of capital C
  (C = 0.5 x underlying notional) per week before costs. The costs per week are: 0.31 % half spread, 0.12 % option
  fees and 0.22 % perp taker (0.43 % with the 4-hour hedge), plus ~0.09 % hedge funding (the perp hedge is mostly
  long in 2021-22, when longs paid funding). Net is ~0 before the cash rate, and negative after it.
- **ETH is worse.** ETH's ATM premium after the hedge is negative in IS: payoff 14.86 % against a premium of
  14.37 % of C.

## Pricing (data quality first)
| | BTC 7d | BTC 30d | ETH 7d | ETH 30d |
|---|---|---|---|---|
| Fridays priced (IS + VAL) | 196 | 191 | 196 | 190 |
| both legs from Deribit marks of trades in 08:00-09:00 | 194 | 119 | 183 | 111 |
| rest: BS at the same-expiry ATM trade iv | 2 | 72 | 13 | 79 |
| median half spread (\|trade - mark\| / mark), % of premium | 2.11 | 0.79 | 1.96 | 0.80 |
| entry straddle iv / DVOL (median) | 0.854 | 0.895 | 0.863 | 0.899 |
| BS at raw DVOL overprices the straddle by | 17.1 % | 11.7 % | 15.9 % | 11.3 % |
| BS at DVOL x IS ratio vs trade price: median error / median \|err\| / p90 \|err\| | -2.5 / 4.8 / 14.4 % | +9.9 / 10.4 / 18.5 % | -3.0 / 6.1 / 13.9 % | +11.9 / 12.0 / 21.7 % |

- **Pitfall.** Pricing the straddle with Black-Scholes at DVOL, the fallback the brief allowed, would invent a VRP of
  ~2 % of C per week. On BTC 7d that is 17 % of the 12.1 % premium. Only trade marks are used for grading.
- **The mark-to-market of open 30d legs is accurate.** It uses the entry iv x DVOL(t) / DVOL(entry). Checked
  against 1,108 later Deribit marks of the same instruments, its error is median -0.03 % of spot, median |err| 0.14 %,
  p90 0.45 % ([out/check_mtm.txt](out/check_mtm.txt)).
- **Realised vol does not depend on the sampling interval.** It is the same from 1 h, 4 h and 24 h returns: BTC IS
  75.4 / 75.5 / 74.7, VAL 49.3 / 48.5 / 50.3.

## Results: weekly excess over the Fed funds rate on C, % per week
Headline cells (all 28 are in [out/report.txt](out/report.txt) and [out/cells.json](out/cells.json)). t is Newey-West
with 4 lags. SR is annualised (x sqrt 52). "rnd" is the % of random draws the rule beats:
- V1 and V3: random entry hour, with BS @ DVOL x ratio pricing on both sides.
- V2: random subsets of weeks of the same size.

| cell | IS mean | IS t | IS SR | VAL mean | VAL t | VAL SR | x1.5 IS / VAL | late IS / VAL | years 21 / 22 / 23 / 24 (sum %) | rnd IS / VAL | power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC 7d H1d V1 | -0.106 | -0.13 | -0.11 | -0.061 | -0.17 | -0.10 | -0.45 / -0.40 | -0.38 / +0.15 | +27.6 / -2.1 / -33.1 / -7.2 | 46 / 37 | -0.13 |
| BTC 7d H4h V1 | +0.033 | +0.05 | +0.06 | -0.154 | -0.60 | -0.32 | -0.43 / -0.60 | +0.29 / +0.23 | +24.4 / +5.4 / -23.6 / -24.0 | 26 / 25 | -0.43 |
| BTC 30d H1d V1 | -0.181 | -0.37 | -0.30 | +0.229 | +0.82 | +0.52 | -0.31 / +0.12 | -0.30 / +0.16 | +13.4 / +10.3 / -19.2 / +13.3 | 1 / 95 | 0.70 |
| BTC 30d H4h V1 | -0.030 | -0.07 | -0.07 | +0.152 | +0.64 | +0.39 | -0.21 / -0.01 | +0.21 / +0.27 | +17.8 / +13.2 / -15.2 / +2.1 | 3 / 3 | 0.52 |
| ETH 7d H1d V1 | -1.116 | -1.01 | -0.99 | +0.068 | +0.16 | +0.09 | -1.50 / -0.26 | -1.66 / +0.28 | -22.4 / -19.7 / -27.3 / +4.6 | 60 / 58 | 0.12 |
| ETH 7d H4h V1 | -0.659 | -0.97 | -1.05 | -0.013 | -0.03 | -0.02 | -1.16 / -0.45 | -0.49 / +0.25 | -20.4 / +18.1 / -42.8 / -0.1 | 61 / 58 | -0.03 |
| ETH 30d H1d V1 | -0.329 | -0.44 | -0.43 | -0.076 | -0.24 | -0.13 | -0.48 / -0.18 | -0.68 / -0.18 | +10.8 / -4.1 / -14.6 / -23.6 | 23 / 88 | -0.18 |
| ETH 30d H4h V1 | -0.693 | -0.75 | -0.79 | +0.011 | +0.04 | +0.02 | -0.91 / -0.15 | -0.29 / -0.03 | -25.6 / +13.9 / -20.5 / -12.1 | 3 / 2 | 0.03 |
| BTC 7d H1d V2 tau 10 | +0.874 | +0.97 | +0.95 | -0.337 | -0.65 | -0.47 | +0.52 / -0.67 | +0.91 / +0.13 | +23.8 / +3.9 / -30.9 / +15.3 | 89 / 27 | -0.41 |
| BTC 7d H4h V2 tau 10 | +0.948 | **+1.50** | +2.03 | -0.287 | -0.68 | -0.50 | +0.48 / -0.72 | +0.88 / -0.09 | +29.9 / -0.7 / -15.7 / +3.8 | 97 / 35 | -0.43 |
| BTC 30d H1d V2 tau 10 | +0.335 | +0.68 | +0.63 | +0.428 | +1.11 | +0.77 | +0.21 / +0.31 | +0.49 / +0.47 | +8.4 / +32.5 / -16.0 / +23.0 | 99 / 27 | 0.82 |
| BTC 30d H4h V2 tau 10 | +0.470 | +1.04 | +1.35 | +0.378 | **+1.14** | +0.80 | +0.29 / +0.21 | +0.59 / +0.40 | +17.5 / +29.0 / -9.7 / +12.7 | 100 / 26 | 0.84 |
| ETH 30d H1d V2 tau 10 | +0.616 | +0.79 | +0.79 | +0.238 | +0.47 | +0.37 | +0.44 / +0.13 | +0.22 / +0.26 | +29.3 / +35.8 / -5.8 / -16.4 | 91 / 69 | 0.36 |
| BTC 30d H1d V2 tau 0 | -0.088 | -0.15 | -0.14 | +0.313 | +1.08 | +0.68 | -0.22 / +0.20 | -0.07 / +0.24 | +10.8 / +19.2 / -19.0 / +22.4 | 96 / 79 | 0.90 |
| BTC 7d H1d V3 (25d strangle) | +0.029 | +0.06 | +0.05 | +0.023 | +0.08 | +0.05 | -0.20 / -0.20 | -0.03 / +0.08 | +25.1 / +0.7 / -34.2 / +13.3 | n/c | 0.06 |
| BTC 30d H1d V3 | +0.259 | +0.70 | +0.57 | +0.173 | +0.79 | +0.49 | +0.17 / +0.10 | +0.07 / +0.10 | +25.4 / +19.8 / -12.6 / +7.0 | n/c | 0.67 |
| ETH 7d H1d V3 | -0.904 | -1.02 | -1.03 | -0.453 | -1.54 | -0.78 | -1.17 / -0.72 | -1.19 / -0.21 | -7.1 / -48.8 / -33.9 / -28.9 | n/c | -1.05 |
| ETH 30d H1d V3 | -0.117 | -0.19 | -0.19 | -0.056 | -0.22 | -0.12 | -0.22 / -0.14 | -0.33 / -0.06 | +17.4 / -8.6 / -9.1 / -14.8 | n/c | -0.16 |

- **Sample sizes.** IS has 66 weeks and VAL 130 for V1 / V3. V2 tau 10 trades 32-45 IS / 37-80 VAL weeks. 2021
  covers March to December. Rows not shown: the other V2 cells, all with IS t < 0.3, and ETH 7d V2, all negative.
- **No 2023 is positive.** 2023 is negative in every cell: low realised vol, but also the lowest implied premium,
  with costs unchanged.
- **Random benchmark.** It is not computed for V3, because no V3 cell came near the IS bar.
- **The max-over-cells null** is a joint 4-week block bootstrap of the recentred weekly series over all 28 cells:
  - IS: best observed NW t 1.50, null p50 1.29, p95 4.95. The p95 is inflated by the short, gappy V2 series.
  - VAL: best observed 1.14, null p50 1.24, p95 3.05.

### Gross decomposition per trade (V1, H1d, % of C)
| | premium (after half spread) | payoff | hedge P&L | funding | option fees | perp taker | net (before cash) |
|---|---|---|---|---|---|---|---|
| BTC 7d | 12.07 | -11.55 | -0.08 | -0.09 | 0.12 | 0.22 | -0.01 |
| BTC 30d | 22.97 | -23.11 | +1.53 | -0.41 | 0.12 | 0.35 | +0.48 (4 weeks) |
| ETH 7d | 14.37 | -14.86 | +0.71 | -0.12 | 0.12 | 0.22 | -0.27 |
| ETH 30d | 27.05 | -29.25 | +2.92 | -0.54 | 0.12 | 0.36 | -0.34 (4 weeks) |

## Tail, capital and margin (V1)
- **Named stress weeks** (week starting Friday, % of C):

  | cell | 2021-05-14 | 2022-05-06 (LUNA) | 2022-06-10 (3AC) | 2022-11-04 (FTX) |
  |---|---|---|---|---|
  | BTC 7d H1d | -6.0 | -3.4 | -7.7 | -10.3 |
  | BTC 7d H4h | -7.8 | -2.0 | -3.5 | -19.5 |
  | BTC 30d H1d | -5.6 | -4.3 | -11.3 | -14.5 |
  | ETH 7d H1d | -3.5 | -3.1 | -12.5 | -11.1 |
  | ETH 30d H4h | -41.5 | -5.8 | -7.4 | -25.1 |

- **The worst weeks are not only the named crises.** BTC 7d H1d: 2021-05-07 -21.5 %, 2021-12-03 -18.3 %,
  2023-01-13 -17.5 %. ETH 7d H1d: 2021-04-16 -42.5 %, 2024-05-17 -21.4 % (ETH ETF surprise). Squeezes up hurt
  as much as crashes.
- **Max drawdown** of cumulative weekly excess:
  - BTC 7d: 68 % of C (H1d), 50 % (H4h).
  - BTC 30d: 27-31 %.
  - ETH 7d: 106 % / 74 %.
  - ETH 30d: 51-79 %.
- **Margin.** Capital needed to stay above Deribit maintenance (~0.075 x S per short leg plus the mark), as a
  multiple of S0:
  - BTC 7d: median 0.25, max 0.55; 1 / 196 trades needed more than C = 0.5 S0.
  - BTC 30d: median 0.32, max 0.73; 24 / 191 needed more than C.
  - ETH 30d: max 1.36-1.38; 40-42 / 190 needed more than C. The worst intra-trade MTM was -94 % of C, so at
    C = 0.5 x S the account is liquidated.

  For the 30d book, C must be ~1-1.5 x S to survive. That halves or thirds the % returns above, which are already
  ~0.

## Costs and checks
- **Costs:**
  - Option fee: min(0.03 % of underlying, 12.5 % of price) per leg.
  - Delivery fee: 0.015 % on the leg that expires in the money.
  - Half spread: estimated from trades.
  - Perp taker: 0.05 %.
  - Binance funding on the hedge.
  - Graded series: excess over DFF on C.
- **x1.5 costs and one step late** (entry priced 09:00-10:00 and every hedge one hour late): no cell turns into a
  pass.

## What failed and why
1. **V1.** The ATM straddle sold every Friday carries ~0.75 % of C of gross premium at mid per week (BTC),
   against ~0.74 % of costs and funding. ETH's premium is negative in IS. The DVOL-RV gap is real (~10 points) but is not priced
   into ATM / 25-delta options.
2. **V2.** Conditioning on DVOL - RV30 > 10 points selects weeks where DVOL is high relative to past realised vol. It
   lifts BTC IS (and BTC 30d VAL), but the 7d effect flips sign in VAL, and no cell clears IS t 2.0.
3. **V3.** 25-delta strangles have the same ~0.9 x DVOL iv, higher relative spread (3.3 % of premium for 7d) and the
   same squeeze tails.

## Pitfalls
- **BS at DVOL is not a price.** DVOL exceeds the ATM iv by 11-17 %. Any backtest that prices at DVOL (or at the
  VIX-style index) manufactures the premium.
- **Hedging with the perp costs funding.** In 2021 the short-straddle hedge was mostly long perp and paid
  0.1-0.5 % of C per trade in funding.
- **The 30d cells overlap.** Up to 4 positions are open at once, so the weekly book is marked to market (scaled
  iv, validated). Positions that expire after 2024-12-31 are dropped, so the last VAL weeks of the 30d book are
  thinner.
- **Settlement proxy.** Settlement uses the Binance perp at 08:00 in place of Deribit's 07:30-08:00 index TWAP.
  Strikes and premium are referenced to the Deribit index. The basis error is symmetric for a straddle.
- **V3 is post hoc.** It was chosen after seeing V1 and is counted in the null.

## What a user decision could unlock
- **Selling the far wings** (10-delta, or a variance-swap replication across the strip) is where the DVOL - RV gap
  sits. It is tail insurance by construction, with:
  - higher relative costs: the fee cap and tick size bind on cheap options;
  - margin that explodes in crashes.

  Free data supports the test, but it would need a decision to accept liquidation-scale tails. Prior for LIVE:
  ~3 %.
- **Maker execution** (quoting the options instead of crossing half the spread) would remove ~0.3 % of C per week:
  about the size of the BTC 30d V2 VAL edge. It needs a live market-making setup, which cannot be backtested from
  trades. Prior ~5 % for a DEMO.
- **Portfolio margin** would cut C to ~0.15-0.25 x S and lift the % returns. It does not change t or Sharpe.

## Files
- Code ([code/](code/)):
  - [fetch.py](code/fetch.py): polite GET and request log;
  - [pull_small.py](code/pull_small.py): DVOL and Binance 1h pull;
  - [pull_eth_fri.py](code/pull_eth_fri.py): ETH option trades in the Friday windows;
  - [extract_btc_fri.py](code/extract_btc_fri.py): BTC windows from round 34's trades;
  - [vrp.py](code/vrp.py): engine;
  - [quotes.py](code/quotes.py): entry quotes;
  - [run.py](code/run.py): V1 / V2 simulation and random pools;
  - [vrp3.py](code/vrp3.py): V3 and the descriptive variance premium;
  - [report.py](code/report.py): grading;
  - [check_mtm.py](code/check_mtm.py): mark-to-market check.
- Outputs ([out/](out/)): report.txt, cells.json, check_mtm.txt, sims_*.pkl, sims3_*.pkl, run logs.
- Data (research/data/deribit/, git-ignored):
  - dvol_BTC_1h.csv, dvol_ETH_1h.csv (2021-03-24..2024-12-31);
  - binance_1h/{BTC,ETH}USDT.csv (2021-2024);
  - ETH_fri/ (ETH option trades, Friday 07:30-10:00 windows 2021-03..2024-12: 457 k trades);
  - BTC_fri/, BTC_daily/ (extracted from round 34's 16.5 M BTC trades, which are still in its scratchpad);
  - quotes_*.pkl;
  - requests.log: 317 requests, all HTTP 200 (history.deribit.com 200, www.deribit.com 69, fapi.binance.com 48),
    14:31-14:45 UTC, plain UA, no personal data.
