# Round 71 stream L5F: quarter-hour opening taker imbalance (result)

Written 2026-11-01 17:54 UTC (from `date -u`). Hypotheses: [HYPOTHESES_L5F.md](HYPOTHESES_L5F.md), written 17:49 UTC
before any kline was downloaded. Code: `code/` (`topvol.py`, `pull.py`, `ranks.py`, `engine.py`, `qc.py`, `run.py`).
Outputs: `out/report.txt` (= `out/run.log`, every table), `out/cells.json`, `out/qc.txt`, `out/ranks.npz`. HOLD was
never requested or loaded: monthly files <= 2024-12 only, rows >= 2025-01-01 dropped at parse, trades exiting at or
after 2025-01-01 dropped.

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)

All 6 declared cells lose money net in both IS and VAL. The best IS net t is -0.01 (M2_12, BTC + ETH, k 2, 12 h),
at the 50th percentile of the max-over-6-cells random null (median -0.00, p95 +1.49). No cell is positive in more than
1 of 5 years. Power at VAL size is negative for every cell.

There is a gross continuation footprint, but only in VAL and it is far below costs. Over all |z| >= 2 marks the
sign-weighted price move in VAL (2022-24) is +3.2 bp at 4 h (t 2.31), +5.2 bp at 8 h (t 3.00) and +4.8 bp at 12 h
(t 2.63), for 6 coins. That matches the paper's sample (2021-01..2024-10) and its ~0.5 bp per boundary average. In IS
(2020-21) the same number is -0.5 bp at 4 h (t -0.22) and -0.1 bp at 12 h, and BTC + ETH are negative at every
horizon. A round trip costs 12 bp (BTC / ETH) to 16-20 bp (alts). The edge is 3-4 x too small, and it is absent in IS.

## Set-up (as declared)
- Coins: BTCUSDT, ETHUSDT + the 4 largest other perps by 2020-24 quote volume (local perp_1d): SOL, XRP, DOGE, BNB.
  The paper uses ADA instead of BNB.
- Signal: I = (2 x taker-buy base - base volume) / base volume of the 1m bar opening at :00 / :15 / :30 / :45. z is
  taken against the same coin's same quarter-hour of day over days d-30..d-1 (>= 25 values). Side = sign(z)
  (continuation, the paper's sign at 4-12 h). Trade if |z| >= k.
- Entry at the close of the bar opening at mark + 1 min (~mark + 2 min). Exit at the close H hours later. One position
  per coin at a time. Costs: 5 bp taker + half-spread 1 bp (BTC, ETH) / 3 bp (point-in-time volume rank < 20) / 5 bp,
  each side. Funding is charged for stamps in (entry, exit].
- t is clustered by entry day. Random: 500 replications, with the same trades per coin and era at random marks and
  the side drawn with the cell's long share.
- Frequency: |z| >= 2 occurs at 4.1-5.0 % of marks and |z| >= 3 at 0.10-0.29 %, so the tails are close to normal.

## Main table (net bp per trade; gross = after funding, before fees and spread)

| cell | IS n | IS net | IS t | IS gross | rand % | VAL n | VAL net | VAL t | VAL gross | rand % | 2020 / 21 / 22 / 23 / 24 net | x1.5 t IS / VAL | late t IS / VAL | power clust / trade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A2_4 (6 coins, k 2, 4 h) | 6808 | -12.5 | -4.19 | +2.1 | 77 | 15319 | -12.2 | -9.31 | +2.6 | 97 | -14 / -12 / -12 / -10 / -14 | -6.6 / -15.0 | -4.1 / -9.0 | -7.3 / -7.9 |
| A2_12 | 3863 | -9.9 | -1.59 | +4.7 | 74 | 8223 | -9.0 | -2.97 | +5.7 | 96 | -3 / -13 / -6 / -9 / -12 | -2.8 / -5.4 | -1.5 / -2.8 | -2.3 / -2.4 |
| A3_4 | 334 | -12.7 | -1.25 | +2.6 | 54 | 1232 | -9.7 | -2.11 | +5.5 | 82 | -41 / -11 / -21 / -4 / -3 | -2.0 / -3.8 | -1.3 / -2.0 | -1.7 / -1.7 |
| A3_12 | 295 | -34.0 | -1.78 | -18.8 | 23 | 1053 | -4.4 | -0.44 | +10.7 | 85 | -58 / -32 / -9 / +1 / -7 | -2.2 / -1.2 | -1.8 / -0.5 | -0.4 / -0.4 |
| M2_4 (BTC + ETH) | 2791 | -11.7 | -3.50 | +0.3 | 58 | 4980 | -8.2 | -4.85 | +3.8 | 98 | -12 / -11 / -7 / -8 / -9 | -5.3 / -8.4 | -3.4 / -4.5 | -3.8 / -4.0 |
| M2_12 | 1601 | -0.1 | -0.01 | +11.9 | 97 | 2737 | -7.5 | -1.97 | +4.5 | 86 | +0.5 / -0.5 / -0.1 / -10 / -12 | -0.8 / -3.6 | +0.2 / -1.9 | -1.5 / -1.5 |

- "late" = entry one more minute later. Entry 15 minutes later gives the same picture (out/report.txt).
- "rand %" = the share of random-entry books whose mean net is below the real one. Random books pay the same costs,
  so a high share on a negative net is not a pass.
- Power = VAL clustered t x sqrt(22/36) and VAL net / sd x sqrt(VAL n x 22/36). The bar is >= 3.
- Max-over-cells null (IS clustered t, 500 reps): the real max is -0.01, the null median -0.00 and the p95 +1.49.

## Information (not cells)
- **Horizon profile** (all |z| >= 2 marks, no position rule, price only, bp, clustered t):

| era / coins | 30 min | 1 h | 4 h | 8 h | 12 h |
|---|---|---|---|---|---|
| IS 6 coins | -1.7 (-2.5) | -1.5 (-1.4) | -0.5 (-0.2) | +1.4 (+0.4) | -0.1 (-0.0) |
| IS BTC + ETH | -1.1 (-1.4) | -1.1 (-1.0) | -1.9 (-0.7) | -2.6 (-0.7) | -4.3 (-0.9) |
| VAL 6 coins | +0.4 (+1.1) | +0.9 (+1.7) | +3.2 (+2.3) | +5.2 (+3.0) | +4.8 (+2.6) |
| VAL BTC + ETH | +0.3 (+0.7) | +1.4 (+2.6) | +3.5 (+3.0) | +4.6 (+2.7) | +3.3 (+1.6) |

  IS shows a short-run reversal at 30 min (t -2.5), which the paper also reports for the first half hour. The 4-12 h
  continuation appears only in 2022-24.
- **Placebo minute** (:07 / :22 / :37 / :52, same cells): VAL gross is +1.0 / +1.0 / +1.6 / -2.8 bp, against +2.6 /
  +5.7 / +3.8 / +4.5 at the marks. So in VAL the quarter-hour mark carries a little more than a random minute. In IS
  the placebo is at least as good as the mark (+4.5 / +11.1 gross vs +2.1 / +4.7).
- **Reversal side**: every cell is negative net in VAL (t -2.6 to -13). In IS only A3_12 is positive, at +3.6 bp
  (t 0.19).
- **Per coin**: no coin is positive net in both eras in any cell, except a thin A3_12 ETH VAL +1.3 bp. XRP at 12 h
  goes the wrong way in both eras (-14 / -8 bp gross). Full list in out/report.txt.
- **Break-even**: the best VAL gross (+5.2 bp at 8 h, all marks) is below even a maker-maker round trip of 4 bp plus
  any queue loss, and IS is ~0. Fee level cannot rescue this.

## How this differs from round 63 O, and what it adds
- Round 63 O tested the hourly taker ratio on 16 alts, beta-hedged, at ~30 bp per round trip, over 2022-24.
- This stream tests the clock-mark opening minute, z-scored by slot, on the six most liquid perps, unhedged, at
  12 bp per round trip for BTC / ETH, with an IS era of 2020-21.
- The result is the same in the end: flow imbalance carries a few bp of continuation at best, and only in 2022-24.
  That is about 1/3 of the cost, and the sign is not stable across eras. It also agrees with round 7 C (quarter-hour
  openings on IC CFDs: no continuation).
- The paper's significance comes from a regression on all 2021-07..2024-10 boundaries, with no costs. Its sample sits
  almost wholly inside our VAL. Our IS (2020-21) is the out-of-sample check, and it fails.

## Pitfalls met / caveats
- 1-minute resolution only: the paper uses the first 10 seconds. A 10-second signal needs aggTrades (about 100 x the
  data). It is not worth pulling, given that the 1-minute version's gross is ~1/3 of cost and absent in IS. A sharper
  signal would have to raise the gross 4 x and also create an IS effect.
- The coin choice uses 2020-24 volume, a mild look-ahead. It is irrelevant to a negative result.
- The archive lacks ~5 days in 2022 for SOL / XRP (round 63 C's known gap; qc.txt). Those marks drop out.
- SOL starts 2020-09, DOGE 2020-07 and BNB 2020-02 (404 for earlier months, as expected), so IS 2020 is thinner for
  alts.
- data.binance.vision robots.txt returns 404 (no rules); it was logged.

## What a user decision could unlock
- Nothing realistic. A market-maker rebate programme would lower costs, but the IS era has no edge to harvest.

## Data pulled
- research/data/qh_imbalance/npz/<SYM>_<YYYY-MM>.npz: 345 symbol-months (m, o, c, v, qv, taker-buy base tb),
  2020-01..2024-12, plus 15 `.404` markers for months before listing. 224 MB. The zips were deleted after parsing
  with `python -I`.
- requests.log: 361 rows (robots 404, 345 x 200, 15 x 404). There was no 403 / 418 / 429 / 503. Pacing was >= 0.25 s
  with 3 threads; the pull took ~2 minutes.
- Web: 2 WebFetch reads of arXiv 2607.09426 (abstract + HTML), and 0 WebSearch.
