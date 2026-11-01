# Stream BY: B's frozen cheap-basis rule replicated on Bybit spot vs Bybit linear perp (round 63)

Written 2026-10-31 17:32 UTC (from `date -u`). Declared in [HYPOTHESES_BY.md](HYPOTHESES_BY.md) (16:46 UTC, before any
Bybit price was requested; addendum 1 at 17:27 UTC, information only). Bybit HOLD (2025+) never requested or loaded:
every request ends at 2024-12-31 23:59:59.999 UTC, every series is cut at ts < 2025-01-01 (0 rows >= 2025 on disk).

## Answer: none (fails the common "positive one step late" bar in IS)
- As frozen (enter at the open of h+1), Bybit looks strong: IS +73.8 bp (t 3.75, n 75), VAL +106.3 bp (t 9.47, n 385),
  4 / 4 years, x1.5 positive, beats 100 % random, power 11.0 (trade) / 6.0 (event-day).
- **But on Bybit 1h klines the open of every bar equals the previous close (100.0 % of universe hours, both legs;
  Binance 32-37 %).** The frozen entry is therefore exactly the signal-bar closing prints that define the dislocation:
  not executable, an upper bound.
- **One hour late (open of h+2 = close of h+1, the first executable hourly price): IS -15.4 bp (t -1.46, median -24.0),
  VAL +15.0 bp (t 1.53, median -27.1).** The bar needs net > 0 one step late in IS and VAL, so it fails both DEMO and
  LIVE. Late by year: 2021 -15.4, 2022 -1.5, 2023 +1.4, 2024 +86.0 bp (medians -22..-33 bp in every year).
- 1m re-pricing (information only, addendum 1): entry / exit at the close of minute 1 / 5 / 15 after the hourly print:
  IS +20.6 (t 1.15) / -24.6 (t -3.95) / -33.3 (t -3.20); VAL +51.8 (t 4.95) / +26.7 (t 2.80) / +18.0 (t 1.99) bp. The
  Bybit edge is mostly gone within 1-5 minutes in IS; in VAL a smaller, decaying part survives.
- No PREREG_DRAFT (a common bar fails). A Bybit HOLD is not worth opening for this rule.

## Coverage (Bybit spot klines start mid-2021: SOL spot 2021-10-21, XRP 2021-07-20; no 2020 data)
| year | coins in universe with data | mean members / day | universe coin-hours | valid deviation share |
|---|---|---|---|---|
| 2020 | 0 | 0.0 | 0 | - |
| 2021 | 35 | 5.1 | 43,848 | 78.8 % |
| 2022 | 104 | 58.5 | 511,992 | 34.2 % |
| 2023 | 124 | 60.0 | 525,456 | 60.3 % |
| 2024 | 153 | 60.0 | 526,296 | 91.1 % |
IS = 2021 H2 only (75 trades, 36 days, 15 coins; top 5 coins 84 % of P&L: AVAX, DOGE, FTM, XLM, DOT). It clears my
"too thin" threshold (30 trades / 10 days) but is a weak IS. Survivorship: Bybit's kline API serves closed perps
(458 / 461 candidates) but not delisted spot pairs (199 of 460 candidate spot pairs return "Not supported symbols"),
so the universe only holds coins whose Bybit spot pair still trades (or is still served, e.g. FTT). The low 2022 valid
share comes from the declared turnover / two-price / 5 bp tick filters (not decomposed).

## Graded cell k100_H24_cheap on Bybit (taker: 31 bp fees + 4 x 3-5 bp half-spread, borrow 40 %/yr, Fed funds)
| era | n | days | net bp | median | t (day) | win | x1.5 (t) | 1 h late n / net / median / t | random beaten (mean) | ex-crash n / net / t |
|---|---|---|---|---|---|---|---|---|---|---|
| IS 2021 | 75 | 36 | +73.8 | +43.5 | 3.75 | 89 % | +50.8 (2.56) | 80 / **-15.4** / -24.0 / -1.46 | 100 % (-49.6) | 75 / +73.8 / 3.75 |
| VAL 2022-24 | 385 | 196 | +106.3 | +65.2 | 9.47 | 99 % | +81.7 (7.24) | 429 / +15.0 / -27.1 / 1.53 | 100 % (-51.3) | 313 / +91.3 / 12.81 |
Years (n, net, median, t): 2021 (75, +73.8, +43.5, 3.75), 2022 (234, +97.3, +61.2, 5.80), 2023 (88, +98.3, +66.0, 8.67),
2024 (63, +150.9, +88.5, 6.77). Random benchmark: matched coin / era / hold / side, 1,000 reps (B's `random_null`);
it only says the signal beats paying costs at random hours. One frozen cell, so no max-over-cells null.

Decomposition per trade (bp): IS price +122.5, funding -0.3, costs -45.9, carry -2.6; VAL price +140.0, funding
+16.7, costs -49.1, carry -1.3. Legs: VAL short-spot leg +93.0, long-perp leg +46.9 (spot falls to the perp, as BX
found on Binance); IS short-spot +2.8, long-perp +119.7. Unlike Binance HOLD (59 % funding), Bybit's VAL edge is the
price leg, i.e. exactly the part the open = previous-close artefact inflates. Mean hold 5.7 h IS / 2.6 h VAL; 258 of
460 trades exit after 1 h (VAL 1 h exits +110 bp, longer holds +100 bp). Concentration VAL: top 5 days 24 %, top 5
coins 42 % (FTT 2022-11 alone 7,472 bp-sum, WOO, UXLINK, AXS, NEAR); 62 coins traded. Adverse perp move > 25 %: 1.3 %
IS / 0.8 % VAL; 1 forced exit (FTT).

Power at VAL size (if it had passed): per trade SR 0.722 x sqrt(1.8 x 385 / 3) = 10.97; per event-day 0.553 x
sqrt(1.8 x 196 / 3) = 6.00. These are computed on the non-executable entry and mean nothing for a live book.

## Correlation with B's Binance trades (IS / VAL only; B/out/trades_k100_H24_cheap.npz, names via code/b_names.py)
| era | BY / B trades | days both trade | corr daily P&L: both-days / union / calendar | trades matched (same coin, entry +-2 h) | matched corr | matched BY / B net | unmatched BY n / net / t |
|---|---|---|---|---|---|---|---|
| IS | 75 / 303 | 5 | 0.72 / 0.11 / 0.14 | 4 | 0.86 | +280 / +165 | 71 / +62.1 / 3.48 |
| VAL | 385 / 333 | 41 | 0.41 / 0.30 / 0.36 | 42 | 0.57 | +242 / +256 | 343 / +89.7 / 12.87 |
Only 11 % of Bybit VAL trades coincide with a Binance trade: the Bybit signals are mostly Bybit's own spot-book prints
(below the HYPOTHESES guess of 0.5-0.7 on shared days; calendar correlation 0.36 is close to the ~0.3 guessed).

## Borrow proxy (Bybit spot instruments-info `marginTrading`, snapshot 2026-10-31, not point-in-time)
VAL trades: 282 on coins with margin today (`utaOnly`, +83.9 bp), 40 on coins without margin (`none`, +279.8 bp), 63
on spot pairs not listed today (+96.5 bp). IS: 56 margin (+83.8), 19 not listed today (+44.2). So ~27 % of VAL trades
(and the best ones) are on coins that cannot be shorted on Bybit margin today; historical availability is unknown.

## What failed and why
1. The frozen entry is not executable on Bybit (open = previous close), and the first executable hourly price (one hour
   late) loses in IS (-15 bp) and is flat in 2022-23; medians are negative in every year.
2. Minute data shows a fast decay: 1 minute after the print IS t 1.15, after 5 minutes IS is negative (t -3.95).
3. IS is 2021 H2 only (no Bybit spot data before), 15 coins, 84 % in 5 coins.

## Pitfalls for later rounds
- **Bybit kline open = previous close** (both spot and linear, 100 %): "enter at the next open" on Bybit 1h (and 1m)
  data is entry at the signal close. Use the close of the next bar, or 1m / trade data, for any Bybit entry.
- Bybit kline API does not serve delisted spot pairs (survivorship); closed perps are served; status=Closed
  instruments-info lists 1,050 closed linear contracts with launch / delivery times.
- Bybit returned retCode 10016 (server error) on 10 of 9,446 requests: retry it, or the paged series is silently
  truncated (fixed in code/pull.py after 7 series were truncated; those were re-pulled).
- For B: on Binance the open is the first trade of the next hour (only 32-37 % equal the previous close), so B's entry
  is not affected by this artefact, but BY's 1m result supports B's own caveat that the edge is in the first minutes.

## What a user decision could unlock
- Nothing on Bybit for this rule. For B's Binance DEMO, the decisive check is the same 1m re-pricing (entry 1 / 5 / 15
  minutes after the hourly print) on Binance 1m klines (data.binance.vision) for B's IS / VAL trades: if IS dies by
  minute 5 as on Bybit, B's demo should be sized as a latency race, not a convergence trade.

## Data pulled (research/data/bybit_basis/, git-ignored; requests.log 9,446 requests, 16:47-17:32 UTC, ~41 min)
instruments-info (linear trading 923, linear closed 1,050, spot 520), daily klines for 461 candidate perps (458 served)
and their spot pairs (261 served), 1h klines for 195 universe coins (both legs, 1 spot missing: GAS), funding for 71
perps not in research/data/bybit/funding, 1m windows (16 min at entry and exit hour) for the 460 graded trades.
Non-zero retCodes: 193 x 10001 (unsupported / delisted symbol), 4 x 10006 (rate limit, backed off), 10 x 10016
(retried). No 403 / 418 / 429. Candidate HPOS10IUSDT daily failed (launched 2024-10-21, under the 60-day age rule
for almost all of 2024; not retried).
Code: code/pull.py, cands.py, by.py (universe + loader, imports B's frozen basis.py and patches only the fee in
trade_net), run_by.py, b_names.py, info.py, pull_1m.py, reprice_1m.py. Outputs: out/by_results.json, trades_by.csv /
.npz, run_by.log, info.log, reprice_1m.log, b_trades_named.csv.
