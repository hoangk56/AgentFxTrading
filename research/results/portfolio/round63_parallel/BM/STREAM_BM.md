# Stream BM: B's registered cheap-basis rule re-priced on Binance 1m klines (round 63)

Written Sat Oct 31 17:43:59 UTC 2026 (from `date -u`). Declared in [HYPOTHESES_BM.md](HYPOTHESES_BM.md) (17:34 UTC,
before any 1m kline was requested). This is a robustness check of the registered rule k100_H24_cheap
([B/PREREG_B_cheap_basis.md](../B/PREREG_B_cheap_basis.md)) on IS, VAL and HOLD. HOLD was already opened by the
coordinator (15:50 UTC) and is read here on instruction. No new selection, no parameter change.

## Answer
**Executable at +5 min: YES. HOLD net +222.8 bp per trade, t 13.89 (day-clustered), median +134.2, win 94 %, n 429.**
The fixed rule (net > 0 at +5 in IS, VAL and HOLD, and HOLD t >= 2) passes: IS +180.6 (t 2.44), VAL +163.2 (t 5.75).
Share of the k = 0 net kept at +5: IS 63 %, VAL 93 %, HOLD 104 %. So on Binance this is **not a latency race**: the
gap is still there 5-15 minutes after the hourly close, and a bot that acts after the close keeps almost all of it in
VAL / HOLD. The 2020-21 part decays more (median +110 -> +55 bp by +5). This differs from Bybit (BY), where IS was
negative by +5 min.

What still decides executability is **borrow**, not speed. The gap lasts because closing it needs a spot short. At +5
in HOLD, funding received is +126 bp of the +223 bp net, and the price leg (+149 bp) comes almost entirely from spot
falling toward the perp (spot leg +154, perp leg -5). Those are squeeze states where spot is hard to borrow. Still
unmodelled, as in B.

## Method (as declared)
- Trade list from B's HOLD harness unchanged (`B/code/hold_run.py` -> `basis.load()`, `simulate(coins, 100, 24, -1)`).
  Hashes re-verified 17:34 UTC: basis.py 46a5f647e1fc33f2, universe.py e4a9ae6a1a841feb, pull.py 6234ca2300a998c8
  (= PREREG). Reproduced IS 303 / +286.5 / t 2.46, VAL 336 / +174.6 / t 6.47, HOLD 429 / +213.5 / t 14.38.
  Every trade used, no subsample.
- Both legs enter at the open of the 1m bar starting at T + k min (T = the signal hour's close). The exit is B's: the
  open of the 1m bar at the start of B's exit hour. Funding, costs (30 bp + 4 x 3 / 5 bp half-spread) and carry are B's.
  Check: k = 0 equals B's 1h opens on 100 % of trades (entry and exit), net identical to < 1 bp on 100 %. No trade
  needed the "first bar within 5 min" fallback (0 shifted bars at any k).

## Net per trade by entry delay (bp; t clustered by entry day)
| era | delay | n | net mean | median | t (day) | win |
|---|---|---|---|---|---|---|
| IS 2020-21 | B (1h open) = +0 | 303 | +286.5 | +110.2 | 2.46 | 93 % |
| | +1 min | 303 | +291.1 | +100.1 | 2.19 | 83 % |
| | +2 min | 303 | +247.9 | +80.1 | 2.42 | 80 % |
| | **+5 min** | 303 | **+180.6** | +54.6 | **2.44** | 71 % |
| | +15 min | 303 | +421.8 | +56.4 | 1.98 | 64 % |
| VAL 2022-24 | +0 | 336 | +174.6 | +99.2 | 6.47 | 91 % |
| | +1 min | 336 | +176.3 | +87.7 | 6.23 | 88 % |
| | +2 min | 336 | +170.4 | +82.4 | 6.22 | 86 % |
| | **+5 min** | 336 | **+163.2** | +71.8 | **5.75** | 82 % |
| | +15 min | 336 | +138.0 | +49.7 | 4.88 | 71 % |
| HOLD 2025-01..2026-10 | +0 | 429 | +213.5 | +126.7 | 14.38 | 100 % |
| | +1 min | 429 | +221.1 | +129.7 | 14.49 | 98 % |
| | +2 min | 429 | +222.2 | +130.9 | 14.07 | 97 % |
| | **+5 min** | 429 | **+222.8** | +134.2 | **13.89** | 94 % |
| | +15 min | 429 | +216.5 | +109.8 | 12.86 | 88 % |
IS +15 min mean (+422) is pushed up by tails in the 2021-05 crash window (median +56). The median is the better guide there.

Information only (not declared): delaying **both** entry and exit by k min gives at +5: IS +179.9 (t 2.31), VAL
+148.8 (t 5.20), HOLD +196.1 (t 13.49, median +109.4). At +15: IS +421.9 (t 1.95), VAL +120.9 (t 4.51), HOLD +187.3
(t 12.25).

## Split at +5 min (bp per trade)
| era | perp leg | spot leg | price leg (t) | funding | costs | carry | net | net without funding | x1.5 costs (t) |
|---|---|---|---|---|---|---|---|---|---|
| IS | +526.1 | -317.3 | +208.8 (2.70) | +21.7 | -48.9 | -1.0 | +180.6 | +158.9 | +156.1 (2.11) |
| VAL | +41.7 | +121.1 | +162.8 (6.96) | +50.1 | -48.2 | -1.6 | +163.2 | +113.0 | +139.0 (4.89) |
| HOLD | -5.4 | +154.2 | +148.8 (19.84) | +126.0 | -49.7 | -2.2 | +222.8 | +96.9 | +198.0 (12.34) |
The price leg alone stays positive after costs in every era (net without funding > 0), so the result is not funding
alone. Funding-stamp trades at +5: VAL +357 (n 105) vs +75 (n 231, no stamp); HOLD +286 (n 288) vs +94 (n 141).

## Spread proxy and gap persistence
| era | perp \|open(T) - close(T-1m)\| median / p75 / p90 (bp) | spot same | half the gap closed at k = 0 / 1 / 5 | median deviation ratio to signal at k = 1 / 5 / 15 |
|---|---|---|---|---|
| IS | 3.2 / 16.9 / 53.6 | 4.2 / 19.2 / 51.3 | 3.0 % / 14.9 % / 32.0 % | 0.93 / 0.75 / 0.78 |
| VAL | 0.7 / 2.3 / 5.0 | 1.9 / 5.3 / 13.1 | 8.3 % / 11.6 % / 19.9 % | 0.97 / 0.85 / 0.67 |
| HOLD | 0.9 / 2.9 / 4.5 | 3.4 / 7.2 / 12.4 | 0.0 % / 1.6 % / 6.5 % | 1.01 / 1.00 / 0.94 |
In VAL / HOLD the jump from the last pre-close print to the first post-close print is a few bp, inside or close to the
modelled 3-5 bp half-spread. The gap is not a stale close: in HOLD it is still the full signal deviation at +5 and 94 %
of it at +15. In IS the books were wider (p90 ~50 bp) and a third of trades had already half-converged by +5.

## Per year at +0 / +5 (net bp, t)
2020 +75.4 (5.24) / +66.4 (3.33); 2021 +318.6 (2.52) / +197.9 (2.42); 2022 +264.8 (5.22) / +264.4 (5.10); 2023 +149.1
(9.31) / +129.6 (6.03); 2024 +95.6 (1.86) / +83.5 (1.68, median +17.3); 2025 +138.7 (8.50) / +138.5 (7.79); 2026 +240.3
(12.76) / +253.0 (12.45). At +5, 7 / 7 years are positive. 2024 is the weak year.

Information only: ex B's crash windows at +5: IS n 224 +91.9 (t 4.72), VAL n 283 +115.4 (t 6.01). HOLD has no crash
window (+222.8). Concentration at +5: IS top 5 days 86 % of P&L (2021-05), VAL top 5 coins 65 % (LUNA, TRB, FTT, SRM,
UMA), HOLD top 5 coins 42 % (DEXE, ONE, HOME, ONG, LSK), top 5 days 15 %. Full output:
[out/reprice_report.txt](out/reprice_report.txt), [out/extra_report.txt](out/extra_report.txt).

## Pitfall found: bad Binance fapi 1h klines on 2024-10-28 21:00 UTC
For the hour 21:00-22:00 UTC on 2024-10-28, Binance USDT-M 1h klines have closes (and highs) that do not match the
1m klines for the same hour. Example: 1000BONK 1h close 0.02088 and high 0.020918, while the 1m close at 21:59 is
0.021576. This produced 24 false VAL signals in B (7.1 % of VAL trades), all at the same hour. All of them lose about
the costs (-50 bp, gross ~0), so they lower B's VAL rather than inflate it. Excluding them, VAL +0 is +191.8 (t 8.19)
and +5 is +179.6 (t 6.89). Every other trade in IS, VAL and HOLD has a 1h close equal to the 1m close at T-1 min. For
Binance 1h signals, check them against the 1m close.

## Caveats (the check does not settle these)
- 1m opens are trade prints, not book quotes. Depth at a 1 unit notional per leg is unknown, and the half-spread stays
  as modelled.
- Spot borrow availability and the hourly borrow rate at these moments are unmodelled (40 %/yr assumed). The gap
  lasting minutes to hours is what one expects when arbitrageurs cannot borrow spot. So B's demo plan (log borrowable
  amount, count unfillable signals at 0) remains the real test.
- LIVE is unreachable regardless (tier fixed at DEMO by IS t 2.46 at +0. At +5, IS t is 2.44, also < 2.5).

## For the coordinator
B's demo can be built as "react after the hourly close": signal at the 1h close, send both legs within a few
minutes. A sub-second race is not needed. Size from the +5 numbers (HOLD +223 / median +134 bp, VAL +163 / median +72).
2024 (+84, median +17) shows the edge can thin out.

## Files
- Code: [code/trades.py](code/trades.py) (B's trade list via B's harness), [code/pull1m.py](code/pull1m.py),
  [code/reprice.py](code/reprice.py), [code/extra.py](code/extra.py) (information only).
- Outputs: out/trades_b.csv (1,068 trades), out/reprice_trades.csv, out/reprice_report.txt, out/extra_report.txt.
- Data: research/data/binance_basis_1m/{perp,spot}/<SYM>_<T>.csv, windows [T - 3 min, exit + 20 min], 36 MB.
  requests.log: 2,175 requests (1,068 fapi, 1,107 spot), 17:37-17:43 UTC (~6 min), all HTTP 200, no 418 / 429 / 403.
  Max used weight 415 / 2,400 (fapi) and 392 / 6,000 (spot). No data.binance.vision fallback needed. Two test requests
  for one trade (17:36 UTC, 200) are logged in the scratchpad, not in this log.
