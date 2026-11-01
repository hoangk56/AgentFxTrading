# Round 63, stream P: Polymarket favourite-longshot bias (P1) and settlement-window carry (P2)

Written 2026-10-31 (UTC). Hypotheses with grid, costs and power were declared in [HYPOTHESES_P.md](HYPOTHESES_P.md)
at 16:20 UTC, before any price was pulled. The Kalshi replication (Addendum A) was declared at 16:30 UTC, before any
Kalshi price. HOLD was not opened, and no 2025-26 price or outcome was loaded. Markets with `closedTime >= 2025-01-01`
are dropped at load, and every request ends at or before 2024-12-31 23:59:59.

## Answer first: no LIVE, no DEMO
- **P1 (favourite-longshot, I1): none.** The primary cell (favourite >= 0.90 at T-1 d, hold to resolution) loses
  after costs: IS -0.80 %/$ (t -0.43), VAL -0.59 % (t -0.73). The best cell, >= 0.90 at T-7 d, makes IS +2.32 %
  (t 1.90) and VAL +0.71 % (t 1.02). It dies at costs x2 (VAL -0.09 %) and at the p75 of the measured spread.
- **P2 (settlement window, I2): none.** The best cell is P2a, which buys the leader in [0.90, 0.99) one hour after
  the scheduled end and holds to payout. It makes IS +2.37 % (clustered t 3.26) and VAL +0.61 % (t 1.12), net of
  cash. The clustered t is inflated, though: IS has only 2 losers where a zero net edge would give 5.8. The exact
  binomial test of net > 0 gives IS z 1.87 (below the DEMO 2.0) and VAL z 1.25 (below the LIVE 1.5). The IS
  max-over-15-cells null has p 0.14.
- **The bias is real gross of costs, but it is smaller than the spread.** Under a calibration null (outcome ~
  Bernoulli(mid)), favourites in VAL beat their mid by ~1-1.5c per $. The max-over-cells null gives p 0.006 (best
  cell P2b, z 3.2). The taker half spread measured from 2024 prints is ~0.6-1.0c, so the net edge is ~0-0.7 %
  per trade, with t ~1. This matches the literature's +0.83c at >= 90c.
- **Power:** even at the VAL edge, power over a 21-month forward is ~1.0-1.4 at the 2024 event rate. P1 / P2 cannot
  reach LIVE without a 2-3x larger edge, or a maker-side fill, which cannot be backtested from these data.
- **Kalshi replication (K1, favourite at the real ask): none, strongly negative.** IS -6 % to -18 % and VAL -10 %
  to -35 % per $ across the 4 cells. The declared rule buys a bracket whose ask is >= thr even when the book is
  empty: the mean paid price is 0.93-0.96 while the mean mid is 0.66-0.83. With real quotes, "a price >= 0.9" is
  often just a stale ask.
- No PREREG_DRAFT is written.

## Data (all keyless, logged in research/data/polymarket/requests.log: time, URL, status, bytes)
| source | what | requests |
|---|---|---|
| gamma-api.polymarket.com/markets | closed markets with endDate 2022-11..2024-12, tags (185 pages x 100) | ~190 |
| clob.polymarket.com/prices-history | hourly token-0 series [E-8 d, min(C+1 h, E+4 d)] for 12,491 markets; token 1 for 400 | 12,900 |
| data-api.polymarket.com/trades | taker prints up to entry+6 h, 1,200 sampled VAL entries (only price/size/side/outcome/time kept) | 1,200 |
| api.elections.kalshi.com historical | INXD / HIGHNY event lists (by event ticker) + hourly bid/ask candles for 2,260 bracket markets (Addendum A) | 3,316 (264 x 429, backed off) |

None of the hosts has a robots.txt (all return 404). There were no 403s. The Polymarket hosts returned 29 x 429 (backed off). Kalshi returned 429s at 4 req/s, so the pull
was slowed to 2 req/s with backoff. Documented limits: gamma 300 / 10 s, prices-history 1,000 / 10 s, and data-api
trades 200 / 10 s. I ran at <= 8 / s.
- Universe after filters (CLOB, binary, lifetime volume >= $1k, final 0/1 or 0.5): 12,288 markets, 887 IS
  (2023) and 11,401 VAL (2024). Dropped: 184 with an odd final, 1,360 with no price file (closed > 7 d before E,
  i.e. early resolution, not tradeable by the rule), and 32 with an empty history.
- **The series is the midpoint.** In the 400-market token-1 check, token-0 + token-1 = 1 at 98.6 % of matched hours.
  Last-trade series would not mirror, so this is mid, and spread cost has to be added.
- 2023 is small and ~75 % untagged: 1,181 markets, 791 events. Event counts that qualify per cell are ~100-330 in
  IS and ~700-2,100 in VAL, so IS power is low by construction (see HYPOTHESES).

## Results (net per $ staked, excess over DFF; unit = parent event; t clustered by resolution day)
Base cost: half spread 1c (p < 0.96) / 0.5c (p >= 0.96), plus 5 bp friction, minus DFF for the days held.
Full output: [run_output.txt](run_output.txt), [results_cells.json](results_cells.json).

| cell | IS n | IS mean | IS t_cl | IS exact z | VAL n | VAL mean | VAL t_cl | VAL exact z | x1.5 IS / VAL | late IS / VAL | hold |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **P1-all thr .90 T1d (primary)** | 140 | -0.80 % | -0.43 | -0.50 | 842 | -0.59 % | -0.73 | -0.91 | -1.18 / -0.99 | -1.01 / -0.15 | 3 d |
| P1-all thr .90 T7d | 124 | +2.32 % | +1.90 | +1.24 | 716 | +0.71 % | +1.02 | +1.02 | +1.92 / +0.31 | +2.52 / +0.86 | 9 d |
| P1-all thr .80 T7d | 172 | +1.08 % | +0.58 | | 963 | +0.67 % | +0.69 | | +0.64 / +0.21 | +1.60 / +0.58 | 9 d |
| P1-all thr .80 T1d | 183 | -1.24 % | -0.62 | | 1200 | -0.54 % | -0.59 | | -1.67 / -1.01 | | 3 d |
| P1-Y thr .90 T7d (favourite = "Yes") | 34 | +1.35 % | +0.44 | +0.07 | 160 | +2.22 % | +1.89 | +1.34 | +0.93 / +1.81 | +1.47 / +1.11 | 8 d |
| P1-N thr .90 T7d (sell longshot "Yes") | 97 | +2.73 % | +2.46 | +1.30 | 623 | +0.47 % | +0.62 | +0.58 | +2.34 / +0.07 | +2.93 / +0.92 | 9 d |
| P1-N thr .90 T1d | 102 | +0.13 % | +0.07 | | 739 | -1.14 % | -1.26 | | | | 3 d |
| **P2a L1h (primary)** | 165 | +2.37 % | +3.26 | +1.87 | 1142 | +0.61 % | +1.12 | +1.25 | +1.99 / +0.23 | +2.41 / +0.71 | 2 d |
| P2a L12h | 151 | +1.92 % | +2.25 | +1.37 | 820 | +0.39 % | +0.66 | +0.65 | +1.56 / +0.03 | +2.62 / +0.59 | 2 d |
| **P2b first >= 0.95 (primary)** | 330 | -1.09 % | -0.94 | -1.21 | 2111 | +0.33 % | +1.01 | +1.07 | -1.43 / -0.01 | -0.48 / +0.51 | 5 d |

The other P1 cells (Y / N at thr 0.80, and T1d at 0.90) are all between -2.8 % and +0.8 % with |t| < 1.3. See
run_output.txt.
- **Exact z** ([net_null.py](code/net_null.py), [net_null_output.txt](net_null_output.txt)) simulates outcomes with
  win probability set so that each trade's expected net excess is exactly 0, then reads the one-sided p of the
  observed event mean (20,000 sims). This replaces the clustered t where the sample has very few losers. In the
  bands where no position lost, the clustered t is 40+, which is meaningless. P2a L1h IS: 2 losers vs 5.8 expected
  at net 0.
- **Years** (= eras here): P2a L1h is positive in 2023 and 2024. Quarterly: 2024Q2 -0.68 %, 2024Q4 +0.02 %, and the
  other six quarters positive. For P1 primary, 4 of 8 quarters are positive.
- **Random benchmarks** (2,000 draws): R1 (same markets and timing, random token) and R2 (random same-category
  markets at the same timing, random token). Every positive cell beats >= 98.7 % of both. This is weak evidence: a
  random token is often a longshot, and longshots lose (R1 mean -10 % to -41 %). The informative null is the
  calibration / exact one above.
- **Calibration null** (outcome ~ Bernoulli(mid), same costs; tests gross mispricing, not net > 0):
  - IS: the best cell is P2a L1h (z_edge 2.06), but the null's max-over-15 95th percentile is 2.25 (p 0.14).
  - VAL: P2b z_edge 3.20, P2a L1h 2.59, P1-all 0.90 T7d 2.21; the max-over-cells p is 0.006.
  - So favourites were underpriced against their mid in 2024. The net edge after the spread is what fails.
- **By category** (info only), P2a L1h VAL: crypto +1.38 %, politics +0.86 %, sports -0.09 %, other +0.16 %. For the
  P1 primary, sports in VAL is -3.60 % (t -1.8), consistent with the paper's "no bias in sports".
- **US election week removed** (2024-11-04..10): P2a L1h VAL +0.45 %, and P1 primary -0.70 %.
- **Volume >= $10k** (robustness): P2a L1h IS +1.61 % / VAL +0.35 %, and P1-all 0.90 T7d +2.57 % / +0.03 %.
  The edge is not concentrated in liquid markets.

## Kalshi replication (Addendum A; [kalshi_analyze.py](code/kalshi_analyze.py), [kalshi_output.txt](kalshi_output.txt))
Sample:
- HIGHNY (NYC daily high): 150 random days per year, 900 bracket markets per year.
- INXD (S&P daily close brackets): 30 random 2023 trading days and the 14 random 2024 days that the historical
  endpoint returns. Most 2024 INXD event tickers come back empty.

Method: hourly yes_bid / yes_ask candles. Buy at the ask (YES) or at 1 - bid (NO), plus the taker fee
0.07 p (1 - p), minus DFF.

| cell | 2023 n | 2023 mean | t_cl | 2024 n | 2024 mean | t_cl | paid / mid (2024) |
|---|---|---|---|---|---|---|---|
| T6h thr .90 (primary) | 74 | -17.5 % | -3.84 | 59 | -31.5 % | -5.40 | 0.961 / 0.689 |
| T6h thr .80 | 85 | -14.1 % | -3.31 | 64 | -34.7 % | -6.24 | 0.940 / 0.660 |
| T24h thr .90 | 125 | -6.2 % | -2.35 | 123 | -10.0 % | -3.25 | 0.945 / 0.834 |
| T24h thr .80 | 152 | -9.4 % | -3.74 | 146 | -10.8 % | -3.90 | 0.901 / 0.810 |

- The rule as declared buys wide, stale asks, mostly in HIGHNY.
- A post-hoc filter (not declared, info only: spread <= 4c at entry) leaves n 15-67 per cell, with means between
  -5.1 % and +2.8 % and |t| <= 1.3.
- So Kalshi 2023-24 does not replicate a tradeable favourite edge either. The thin samples cannot confirm or refute
  the +1c gross bias.

## Costs
- **Fees:**
  - 2023-24: 0. `feesEnabled` is false on every market in the table; the AMM `fee` field is for the old FPMM, not
    the CLOB.
  - Today (docs.polymarket.com/trading/fees, read 2026-10-31): the taker fee is `C x rate x p x (1-p)`, with rates
    crypto 0.07, sports / economics / culture / weather / other 0.05, politics / finance / tech / mentions 0.04 and
    geopolitics 0. Makers pay 0 and receive 15-25 % rebates.
  - At p 0.95 and rate 0.04, the fee is 0.19c per share, about 0.2 % per $. That alone would remove a third of
    P2a's VAL net edge for a taker in the forward era.
- **Spread, measured** ([cost_check.py](code/cost_check.py), [cost_check_output.txt](cost_check_output.txt)): the
  first taker buy-equivalent print within 2 h after a sampled 2024 entry, minus the mid:

  | band | median | mean | p75 | assumed |
  |---|---|---|---|---|
  | 0.90-0.95 | +1.0c | +0.4-1.0c | +1.5-2.0c | 1.0c |
  | 0.95-0.97 | +0.65-1.0c | | +1.1-2.0c | 0.5c |
  | 0.97-0.99 | +0.55-0.85c | | +1.0-1.5c | 0.5c |

  The assumed cost above 0.96 was therefore too low by ~0.2-0.4c.
- Re-cost at the measured median ([recost_output.txt](recost_output.txt)): P2a L1h IS +2.32 % / VAL +0.55 %. At
  the measured p75: IS +1.64 % / VAL -0.10 %; P1-all 0.90 T7d VAL +0.01 %; P2b VAL -0.41 %.
- **Fill availability:** only ~50 % of sampled entries had any buy-side print within 2 h. Entries with a print had
  higher model returns (P2a +1.63 %) than entries without one (+0.14 %). The "edge" partly sits in thin books where a
  real order would move the price.
- Friction: 5 bp per trade (USDC on / off-ramp amortised). Polygon gas is paid by Polymarket's relayer.

## Power (LIVE needs >= 3 on the deciding sample)
- Per-event net Sharpe at VAL size: P2a L1h 0.032, P1-all 0.90 T7d 0.034, P2b 0.020, P1 primary negative.
- Over a 21-month forward at the 2024 event rate (1.75 x n_VAL), power = 1.44 / 1.22 / 1.24.
- Polymarket lists many more markets in 2025-26, but power scales only with sqrt(n). Reaching 3 needs ~4.5x the 2024
  independent-event rate at an unchanged edge, and the edge after 2025 taker fees is smaller. The literature (2024-26
  data) reports +0.83c gross at >= 90c, the same order as here. That literature also makes the 2025-26 HOLD non-blind
  (see HYPOTHESES).

## What failed and why
1. **The edge is about the size of the spread.** Polymarket mids are slightly too low for favourites (~1-1.5c per
   $), but a taker pays ~1c. This is the same pattern as the "premia that lose to costs" family (round 9) and
   funding carry (round 58).
2. **Timing:** the bias concentrates at T-7 d (capital locked longer) and right after the scheduled end, not at T-1
   d. At T-1 d the favourite is *not* underpriced (VAL z_edge 0.43). This fits Qiu & Qiu's warning that favourites
   are rich near resolution.
3. **E is a noisy proxy for "outcome public."** Many markets have E = 00:00 UTC of a date whose rule deadline is
   23:59 ET. P2a at E + 1 h is then still ~1 day before the outcome is known: the median hold is 18 h, and the p90 is
   128 h. So P2a mixes true settlement-window carry with P1-like favourite bets. A clean P2 needs the real decision
   time (UMA proposal time, from the subgraph or on-chain), which these keyless endpoints do not give.
4. **IS is tiny.** 2023 has ~100-330 qualifying events per cell with 2-16 losers, so one or two losses swing the
   mean by 1-2 %.

## Pitfalls found (for later rounds)
- The prices-history series is the **mid**, rounded to 0.001-0.01. It is not a fill price.
- prices-history refuses windows longer than ~14 d at `fidelity=60` (400 "interval too long"), and some
  2022 / early-2023 markets return an empty history.
- gamma `limit` is capped at 100 per page (silently). `include_tag=true` is needed for tags, and 2023 is mostly
  untagged.
- Clustered t on bounded, skewed binary returns is anti-conservative when the sample has few losers (t 40+ in
  zero-loss bands). Use an exact / simulated binomial test.
- Lifetime volume is an ex-post filter. `endDate` can be edited after listing, a possible look-ahead in the timing
  anchor that I cannot audit from gamma.
- data-api trades keep ~3 years (2023-11 onward from today) and need `end=`; `start=` with short windows often
  returns nothing. Responses carry wallet / name / profile fields: I kept only price / size / side / outcome / time.
- The Kalshi historical endpoint ignores `series_ticker`, so query by `event_ticker`. Hourly bid / ask candles exist
  for 2023-24.

## What a user decision could unlock
- **Maker-side execution.** The gross edge (~1-1.5c per $ on favourites at T-7 d and right after E) is about the
  size of the spread. A resting bid at or below the mid pays no fee, earns liquidity rewards and maker rebates, and
  may capture it. Fills and adverse selection cannot be backtested without order-book history. A **forward paper log**
  of posted bids from 2026-11 is the only test. It needs a geo-permitted wallet (Vietnam is not on Polymarket's
  blocked / close-only list, but see below). Expected chance of a LIVE-grade result: ~2 %; DEMO ~5 %.
- **Clean P2 timing.** The UMA proposal / settlement timestamps (Polygon logs, or the Goldsky subgraph, both keyless)
  would let P2 enter *after* the proposal, so that the outcome is truly public. That is the only version of I2 that
  is a carry and not a bet. Data work ~1 day; chance LIVE ~2 %.

## Vietnam residency (information, not a reason to skip)
- Polymarket's geoblock list (docs.polymarket.com/api-reference/geoblock, read 2026-10-31) blocks 7 OFAC regions
  outright. It is close-only (frontend and API) in 38 jurisdictions, including the US, UK, France, Germany,
  Singapore, Thailand and Taiwan, and frontend-only close-only in 5 (Japan, South Korea, Netherlands, Ireland, Malta
  sports). **Vietnam is not listed**, so trading is technically possible from a Vietnamese IP with a self-custodied
  USDC wallet.
- Legally, Vietnam bans unlicensed online gambling, and prediction markets have no specific law. The status of using
  unlicensed foreign crypto venues is unclear: secondary sources report fines, and a 2025 pilot licenses domestic
  crypto exchanges. I found no primary text. This is a user / legal decision.
- Kalshi is CFTC-regulated, and access for non-US persons is limited and changing.

## Files
- [HYPOTHESES_P.md](HYPOTHESES_P.md): declarations (16:20 UTC) and Addendum A (Kalshi, 16:30 / 16:40 UTC).
- `code/`:
  - [net.py](code/net.py): rate-limited GET plus the log.
  - [pull_gamma.py](code/pull_gamma.py), [universe.py](code/universe.py), [pull_prices.py](code/pull_prices.py),
    [pull_trades.py](code/pull_trades.py), [pull_kalshi.py](code/pull_kalshi.py): pulls and the universe table.
  - [analyze.py](code/analyze.py): rules, costs, cash, clustering.
  - [run.py](code/run.py): all cells, robustness, random benchmarks, calibration null.
  - [net_null.py](code/net_null.py), [cost_check.py](code/cost_check.py), [recost.py](code/recost.py),
    [kalshi_analyze.py](code/kalshi_analyze.py).
- Outputs: run_output.txt, results_cells.json, trades_primary.json (2023-24 entries of the primary cells only),
  net_null_output.txt, cost_check_output.txt, recost_output.txt, kalshi_output.txt.
- Data (git-ignored): research/data/polymarket/{raw_gamma, raw_prices, prints, kalshi}/, markets.json, requests.log.
