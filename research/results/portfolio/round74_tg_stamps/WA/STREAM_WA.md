# STREAM_WA: Whale Alert Telegram posts (@whale_alert_io) -> Binance USDT-M perp, 5-60 min

Written 2026-11-02 15:53 UTC. Plan: [HYPOTHESES_WA.md](HYPOTHESES_WA.md) (14:25:43 UTC, before any price; one
addendum before the seconds data). HOLD closed: posts >= 2025-01-01 dropped at parse, every price series ends
2024-12-31. No git.

## Answer
**None** (no LIVE, no DEMO, no PREREG_DRAFT). None of the 42 declared cells has IS net > 0 with any useful t: the best IS
net t is +0.66 (BO >= $100M, 60 min, n 23). The random-time chance bar for the max over 42 cells is 2.20 (p95).
38 of 42 IS cells are net negative. The gross reaction to a post is 0 to +4 bp at 5-15 min in the
mechanism's direction. That is real but small (VAL F 5 min gross +1.1 bp, above 99.9 % of same-day random times),
against 12 bp of costs. A seconds entry (first perp aggTrade >= post + 5 s) does not change this: the first minute
after a post moves -1.9 to +1.3 bp on average.

## What is different from rounds 53 / 31 / 48
Round 53 timed USDT mints by the chain block and tested only mints. Rounds 31 / 48 used daily, non-point-in-time
exchange-flow totals. Here each transfer is timed by its Telegram post (what traders saw), and each has a direction
(unknown -> exchange = inflow, exchange -> unknown = outflow) and a posted USD size. The result agrees with round 53:
mints and burns follow price. In the 60 min before the post, the side-signed BTC return is +9.4 bp for IS mints
and +14.3 bp for IS burns, i.e. price rose before mints and fell before burns. After the post, nothing tradable is left.

## Data
- Page sample (declared): IS every 4th page (`before = 56860 - 80 j`), VAL every 2nd page (`before = 85500 - 40 j`).
  That is 1,337 pages plus 19 probes, giving 12,631 IS and 14,332 VAL posts. Pages are in
  research/data/telegram_hist/raw/whale_alert_io/ and the pull log is research/data/whale_alert/pull_tg.out. The pull
  had no 403 / 429 and averaged ~5 s per page under the shared lock.
- Era id boundaries: 2020-01-01 ~ id 6,960; 2022-01-01 ~ 56,870; 2025-01-01 ~ 85,500; the channel is ~104,490 posts.
- Events (code/events.py -> research/data/whale_alert/events.csv). 3 edited posts were dropped. Exchange -> exchange
  and unknown -> unknown transfers are not events.
  IS: BI 556, BO 624, EI 321, EO 575, M 743, B 473. VAL: BI 1,097, BO 1,006, EI 1,303, EO 604, M 389, B 466.
  The >= $100M share is small in IS (BI 21, BO 30) and larger in VAL (BI 237, BO 192, M 183, B 162).
- Prices: perp 1-minute klines for BTCUSDT and ETHUSDT, 2020-01..2024-12, from data.binance.vision monthly zips
  (code/klines.py, 120 files, 0 missing). For the seconds check: perp daily aggTrades on 60 random event days
  (30 per era, plus each next day for exits), covering 347 events (code/secs.py). The zips were deleted after parsing.
  Requests are logged in research/data/whale_alert/requests.log.

## Per rule: IS pick (best IS t over size x horizon) -> VAL unchanged
Net = gross - 12 bp (5 bp taker + 1 bp slip a side). Random % = share of 1,000 same-day random-time draws (same side,
same coin) whose mean net is below the rule's mean net. Power = VAL Sharpe x sqrt(expected HOLD trades), where HOLD
trades are VAL trades / 3 yr x 2 (sampling) x 1.83 yr x 1.09 (post rate).

| rule | IS pick | IS n | IS gross | IS net | IS t | IS rand % | VAL n | VAL gross | VAL net | VAL t | VAL net x1.5 | VAL late | VAL rand % | VAL Sharpe | HOLD n | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BI short | >= 100M 60m | 17 | -26.8 | -38.8 | -1.08 | 8.0 | 204 | +12.9 | +0.9 | 0.17 | -5.1 | -2.0 | 99.8 | 0.011 | 271 | 0.18 |
| BO long | >= 100M 60m | 23 | +20.8 | +8.8 | 0.66 | 83.3 | 142 | +13.8 | +1.8 | 0.29 | -4.2 | +1.2 | 99.7 | 0.023 | 189 | 0.32 |
| EI short | >= 100M 60m | 11 | +7.0 | -5.0 | -0.10 | 58.3 | 56 | -5.3 | -17.3 | -1.92 | -23.3 | -17.3 | 29.4 | < 0 | 74 | 0 |
| EO long | all 60m | 402 | +2.8 | -9.2 | -1.55 | 58.0 | 467 | -0.6 | -12.6 | -3.08 | -18.6 | -12.7 | 52.2 | < 0 | 621 | 0 |
| F pooled | >= 100M 60m | 62 | -13.5 | -25.5 | -1.57 | 10.8 | 405 | +11.1 | -0.9 | -0.21 | -6.9 | -2.5 | 99.9 | < 0 | 539 | 0 |
| M long | >= 100M 5m | 46 | +12.9 | +0.9 | 0.22 | 99.5 | 174 | +2.5 | -9.5 | -7.51 | -15.5 | -9.7 | 94.2 | < 0 | 231 | 0 |
| B short | >= 100M 5m | 4 | +13.2 | +1.2 | 0.05 | 84.2 | 155 | -2.2 | -14.2 | -14.15 | -20.2 | -13.5 | 8.8 | < 0 | 206 | 0 |

Per-year net of the picked cells, in bp (n):
BI 2020 +19.3 (3), 2021 -51.2 (14), 2022 +14.9 (24), 2023 +4.4 (34), 2024 -2.2 (146).
BO 2020 +71.4 (1), 2021 +6.0 (22), 2022 +4.8 (41), 2023 +17.0 (13), 2024 -1.8 (88).
F 2020 +32.3 (4), 2021 -29.4 (58), 2022 -0.1 (79), 2023 +12.6 (60), 2024 -4.1 (266).
All other picks are negative in every VAL year. No pick reaches IS t >= 2.0, so the DEMO bar is not met.

Full 42-cell table: [results/cells.csv](results/cells.csv) (both eras: gross, net, day-clustered t, x1.5, late
+1 bar, sd, Sharpe, random mean / excess / %, pre-60-min drift, years). The largest-n cells are the most
informative. F all 5 min: IS n 1,787, gross +1.4, net -10.6, t -11.6; VAL n 3,414, gross +1.1, net -10.9,
t -27.0.
Max-over-42-cells random t (results/nullmax.txt): IS mean 1.14 / p95 2.20; VAL mean -0.29 / p95 0.90.

## Seconds check (perp aggTrades, 60 random event days, all events, no one-at-a-time filter)
Full table: [results/secs_summary.md](results/secs_summary.md). Side-signed gross bp (day-clustered t):

| era | group | n | missed first minute | post+5 s -> +5 min | late +10 s | 1-min design, same events |
|---|---|---|---|---|---|---|
| IS | F all | 90 | -1.88 (-1.0) | +2.63 (+0.7) | +3.33 | +3.14 |
| VAL | F all | 145 | -0.08 (-0.2) | +1.43 (+0.5) | +0.93 | -2.03 |
| VAL | F >= 100M | 29 | +1.25 (+1.3) | +4.65 (+1.4) | +1.93 | -0.68 |
| IS | M | 53 | -1.48 (-0.8) | -4.37 (-1.5) | -4.45 | +0.48 |

Entering at post + 5 s gains at most ~1-2 bp over the 1-minute design, and the 5-minute gross stays under 5 bp, far
below the 12 bp round trip. No group has a first-minute pop like the Upbit listing one.

## What failed and why
- The posted transfers carry almost no short-horizon information after the post. Most inflows and outflows are
  exchange wallet shuffles and OTC settlements, and the feed is the most-watched on-chain alert, so whatever
  reaction exists is +1 to +4 bp at 5-15 min, under a third of the taker cost.
- The one sizable gross effect is in VAL only: >= $100M BTC flows at 60 min, BI +12.9 and BO +13.8 gross, above
  99.7 % of random times. It is still net ~0 at 12 bp, it is reversed in IS (BI -26.8, F -13.5), and it is
  negative in 2024 (the year with most events). It is not a rule.
- Mints and burns follow price (positive pre-post drift on the trade side), the same as round 53. After the post,
  mints give -0.1 to +2.5 bp gross at 5 min.

## Pitfalls
- t.me ids are dense (20 posts per page). Posting rate varies 5x: 2021 has ~50k posts, 2024 ~10k. A page sample
  by id therefore over-weights 2021 within IS, so it was stratified by era (k = 4 in IS, 2 in VAL).
- The Whale Alert reporting threshold and the USD size mix change over time: the >= $100M share rises sharply in
  2024. Cross-era comparisons of size buckets are confounded by this.
- Labels need care. "Coinbase Institutional" and "Binance Beacon Deposit" count as exchanges; "#Coinbase Custody",
  "#Cumberland" (OTC), "#Xapo" and "#Ceffu" do not. Hack, dormant-address, freeze and escrow posts do not match the
  transfer regex.
- fapi `/fapi/v1/aggTrades` serves only the last 2 days (code -4166). Spot `/api/v3/aggTrades` (also data-api) returns
  [] for 2020 windows. Historical seconds data comes only from data.binance.vision daily aggTrades (4-140 MB per
  day and symbol).

## What a user decision could unlock
Nothing specific. Maker execution would cut the cost from 12 bp to ~2-4 bp, but the effect is not stable across
IS and VAL even gross, so this stays below 1 % for LIVE. A paid point-in-time flow feed (CryptoQuant / Glassnode)
was already rated ~1 % in round 31, and these results do not raise it.

## Files
- HYPOTHESES_WA.md, STREAM_WA.md
- code/: probe.py, peek.py, sample_pull.py, events.py, klines.py, analyze.py, secs.py, secs_analyze.py
- results/: cells.csv, nullmax.txt, analyze.out, secs_summary.md
- research/data/whale_alert/: events.csv, k1m_BTCUSDT.npz, k1m_ETHUSDT.npz, secs.csv, requests.log, pull_tg.out,
  klines.out, secs.out
