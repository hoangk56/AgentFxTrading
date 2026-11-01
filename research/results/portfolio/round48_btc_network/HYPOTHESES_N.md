# Round 48, stream N: hypotheses (declared before any conditional return)

Written 2026-10-30 08:28 UTC (`date -u` 08:27:38). Before this file only these were computed: raw downloads, the
2024-12-31 cut at parse, signal-day counts (below), and the unconditional sd of BTC's 1-day IC return at 02:00 UTC (IS
~496 bp, VAL ~308 bp) for the power arithmetic. No return conditioned on any signal has been computed.

## Data and point-in-time rules
All series cut at ts < 2025-01-01 at parse (`scripts/parse.py`), before anything was printed.
- **Coin Metrics community API v4** (`community-api.coinmetrics.io`, no robots.txt (404), no key), BTC daily
  2010-01-01..2024-12-31: HashRate (daily mean hash rate implied by the day's blocks and difficulty), BlkCnt,
  FeeTotNtv, IssTotNtv, IssTotUSD, PriceUSD (00:00 UTC reference rate), TxCnt. Revenue / difficulty-mean metrics are
  not in the community tier. Block-derived values for UTC day D are computable from public blocks at 00:00 UTC D+1
  (immutable data; CoinMetrics only aggregates). **Signal time = D+1 02:00 UTC** (2 h guard for header-timestamp skew
  and late blocks). PriceUSD uses the 00:00 reference of D (known at D+1 00:00).
- **mempool.space** `/api/v1/mining/difficulty-adjustments/all` (robots.txt path serves the app page, i.e. no
  rules): every retarget [header timestamp, height, difficulty, ratio], 421 rows to 2024-12-29. Exact and immutable.
  **Signal time = retarget block header timestamp + 2 h.** `/api/v1/mining/hashrate/all` kept as a cross-check only.
- **blockchain.com charts API** (`api.blockchain.info/charts/...`, robots.txt path serves the API docs page;
  www.blockchain.com robots allows `*` except search pages): mempool-size (bytes, 15-min snapshots from 2016-06-14,
  recorded live, so point-in-time), mempool-count, hash-rate, transaction-fees (cross-checks). Snapshot used for day D =
  last snapshot at or before 00:00 D+1 (must be within 3 h), signal time D+1 02:00.
- **IC M1** BTCUSD (from 2017-08-28), ETHUSD (from 2017-09-25), US500, XAUUSD, cut at load. IC crypto was closed
  Saturday and most of Friday evening / Sunday until 2024-04.

## Execution and costs (rounds 31 / 37 conventions)
- Entry at the first IC bar at or after the signal time (+0; check +1 min on both legs), whatever the gap (weekend
  signals enter at the Sunday / Monday open; gaps > 3 days skipped). Exit at the last IC bar at or before entry + h
  days, h in {1, 3, 5} as declared per cell. Never > 5 days. One open trade per cell (events during a trade skipped).
- Cost: half the actual spread at each leg (mid = bid + half spread); check spread x1.5. Swap: research/specs.SWAPS via
  `swap_frac_at` (BTC long -4.96 bp per 17:00 NY rollover, x3 Friday, short 0; ETH long -4.82 bp). Sensitivity row
  "short also -5 bp".
- Eras: IS 2017-09-01..2021-12-31 (IC starts 2017-08-28), VAL 2022-2024. PRE 2012-01..2017-08 at mid only on CoinMetrics
  PriceUSD: entry at the first 00:00 reference at or after the signal time, exit h days later (no cost).
- Statistics: t clustered by entry day; by year; ex-2020-03/04; random-entry control (300 seeds: same count per era,
  random days at the cell's clock time (02:00 UTC for daily cells, uniform minute for difficulty cells), same hold;
  fixed sides kept, r3-dependent sides recomputed at the random time); chance benchmark = expected max |t| of K
  independent cells (simulated).
- ETHUSD: the primary cells re-run on ETH (graded mainly on VAL: ETH's IS spread 89-254 bp). US500 and XAUUSD:
  primary cells as controls (expect nothing; a risk-off proxy would show up there too). Information, not counted.

## Families, rules, sides (fixed now)
Hashrate below = CoinMetrics HashRate; MAs are trailing simple means over the days up to and including D.

**F1 miner capitulation / hash ribbons** (Edwards 2019, "Hash Ribbons", Capriole; practitioner rule).
- F1a cross long: 30-d MA crosses back above the 60-d MA after >= 10 consecutive days below -> long, h 1 / 3 / 5.
- F1a Edwards buy: after such a capitulation, the first day with 30 > 60 AND price 10-d SMA > 20-d SMA -> long,
  h 1 / 3 / 5.
- F1b capitulation onset: 30-d crosses below the 60-d after >= 10 days above -> short (miners sell reserves),
  h 1 / 3 / 5.
- F1c capitulation state: every day with 30 < 60 -> short, h 1.
**F2 difficulty adjustments** (mechanism: a retarget changes every miner's BTC revenue per hash at a known block).
Change c = ratio - 1 (%), relative change rel = c - median of the previous 13 changes (difficulty trends up).
- F2 rel all: every retarget, rel < 0 -> long (margin relief, less forced selling), rel >= 0 -> short; h 1 / 3 / 5.
- F2 rel big: same, only |rel| >= 5 pp; h 1 / 3 / 5.
- F2 raw drop: c <= -2 % -> long; h 1 / 3 / 5.
**F3 hashprice shocks** (miner USD revenue per hash = (IssTotNtv + FeeTotNtv) x PriceUSD / HashRate, trailing 7-d mean).
- F3 fresh low: 7-d hashprice at its trailing 90-d low and not at such a low in the previous 10 days -> short, h 1 / 3.
- F3 state: every day at the 90-d low -> short, h 1.
- Price-only control (not a cell): the same rules on 7-d mean PriceUSD. Hashprice is mostly price; a hashprice cell
  matters only if it beats this control. A BTC-denominated hashprice was planned and dropped before any return: it is
  at a 90-d low on 80-100 % of days (hashrate growth), so it has no event structure.
**F4 fee / mempool congestion spikes.** z = log value vs the trailing window (excluding D): fee share of miner
revenue FeeTotNtv / (FeeTotNtv + IssTotNtv), 90-d window; mempool bytes at 00:00, 30-d window. Trigger z > 2.
- Primary (mechanism: congestion is coins in transit, mostly exchange deposits that are then sold) -> **short**, h 1 / 3.
- Secondary: exhaustion = fade the prior 3-day IC return (side = -sign of mid change over the 72 h before entry), h 1 / 3;
  continuation = follow it, h 1 / 3 (the mirror of fade: counted, but not independent).
**BOOK** (one cell): each day at 02:00 UTC D+1, s = (-1 if F1c state) + (-1 if F3 state) + (-1 if fee-share z > 2) +
(-1 if mempool z > 2) + (F2 rel-all side if a retarget signal fell in the previous 24 h) + (+1 if an F1a cross fired
in the previous 5 days). Trade sign(s) for 1 day; s = 0 no trade.

Cells: F1 10, F2 9, F3 3, F4 12, BOOK 1 = **35 BTC cells**. ETH / US500 / XAU and price-only rows are information.

## Signal counts (computed before returns; PRE 2012-01..2017-08 | IS 2017-09..2021 | VAL 2022-24)
| signal | PRE | IS | VAL | per year IS / VAL | HOLD trades (VAL rate x 1.73) |
|---|---|---|---|---|---|
| F1a cross long | 6 | 7 | 5 | 1.6 / 1.7 | ~3 |
| F1a Edwards buy | 6 | 6 | 3 | 1.4 / 1.0 | ~2 |
| F1b onset short | 6 | 7 | 6 | 1.6 / 2.0 | ~3 |
| F1c state short | 141 | 290 | 200 | 67 / 67 | ~115 |
| F2 rel all | 160 | 116 | 80 | 27 / 27 | ~46 |
| F2 rel big | 75 | 52 | 18 | 12 / 6 | ~10 |
| F2 raw drop | 11 | 18 | 15 | 4.1 / 5.0 | ~9 |
| F3 USD fresh low | 24 | 19 | 16 | 4.4 / 5.3 | ~9 |
| F3 USD state | 518 | 222 | 132 | 51 / 44 | ~76 |
| price-only fresh / state | 6 / 96 | 10 / 112 | 10 / 88 | | |
| F4 fee share z > 2 | 153 | 81 | 86 | 19 / 29 | ~50 |
| F4 mempool z > 2 | 17 (2016-17) | 61 | 39 | 14 / 13 | ~22 |

## Power arithmetic (before returns)
LIVE needs HOLD power = net Sharpe per trade x sqrt(HOLD trades) >= 3; DEMO needs IS t >= 2 (t ~ Sharpe x sqrt(n IS)).
BTC 1-d sd ~500 bp IS / ~310 VAL; h-day sd ~ x sqrt(h).
| cell | HOLD n | Sharpe/trade for LIVE | net needed (VAL sd) | Sharpe for DEMO IS t 2 | reachable? |
|---|---|---|---|---|---|
| F1a / F1b events | 2-3 | 1.7-2.1 | > 900 bp at 3 d | 0.76-0.82 | LIVE no; DEMO only for a huge effect |
| F1c state, 1 d | 115 | 0.28 | ~87 bp / day | 0.12 (~59 bp at IS sd) | LIVE implausible; DEMO needs ~60 bp/day |
| F2 rel all, 1 d | 46 | 0.44 | ~137 bp | 0.19 | LIVE no; DEMO needs ~93 bp (1 d) |
| F2 rel big / raw drop | 9-10 | 0.95-1.0 | > 300 bp | 0.28-0.47 | LIVE no |
| F3 fresh | 9 | 1.0 | ~310 bp (1 d) | 0.46 | LIVE no |
| F3 state, 1 d | 76 | 0.34 | ~107 bp | 0.13 | LIVE implausible |
| F4 fee share, 1 d | 50 | 0.42 | ~131 bp | 0.22 | LIVE no |
| F4 mempool, 1 d | 22 | 0.64 | ~199 bp | 0.26 | LIVE no |
| BOOK, 1 d | ~200-250 (est.) | ~0.19-0.21 | ~60-65 bp / day | ~0.08 | LIVE only at an implausible ~60 bp/day |

Expectation: no cell can reach LIVE at any plausible size; the event families (F1, F2 big, F3 fresh) cannot reach DEMO
either unless their effect is several hundred bp. Effects of that size in a forced flow of ~900 BTC/day (~0.3-0.5 % of
spot volume) are not expected; the honest prior is "information only".

## Addendum 1 (2026-10-30 08:31 UTC, after the 35 primary cells were graded, before any number below)
The 35 cells are graded (none passes; see STREAM_N.md). Two follow-ups, declared before their numbers:
- **A1 hashrate shock** (sudden miner outages: China ban 2021-05/06, Texas curtailments; the forced-seller mechanism of
  F1 on a faster clock): 7-d mean hashrate >= 10 % below its 30-d mean, first such day in 10 days -> short, h 1 / 3.
  2 cells (total 37). Same execution, costs and controls as above.
- **A2 linear residue of the daily families (information, not cells)**: OLS of the next 1-day BTC IC mid return
  (02:00 D+1 -> 02:00 D+2, every day) on each standardised daily series: log(30-d / 60-d hashrate MA), log(7-d
  hashprice / its 90-d min), fee-share z (90 d), mempool z (30 d), last relative difficulty change (carried forward
  until the next retarget). Slope in bp per sd, IS and VAL, alone and with past 1 / 7 / 28-day returns as controls.
  Answers "what is left in the daily families (2)-(4)"; a slope is not graded against the bars.
