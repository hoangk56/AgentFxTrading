# Stream A3 (round 66) hypotheses: Upbit KRW-listing notice -> Binance SPOT, coins without a Binance perp

Written Sun Nov 1 13:53:40 UTC 2026 (from `date -u`). At this point I have used only: stream A's notice bodies and
event code (read-only), the local spot_first / perp_1d files, data.binance.vision robots.txt (404) and 60 HEAD
existence probes of spot daily aggTrades files (status and size only, logged in research/data/upbit_spot_notice/
requests.log). **No aggTrade, no Upbit candle and no price has been downloaded; no return has been computed.** HOLD
(2025-01-01..) is never requested, loaded or counted: only daily files dated <= 2024-12-31, every N < 2025.

## Mechanism and side (fixed before data)
Same as A2-D5L: an Upbit KRW listing notice sends Korean demand to the coin; arbitrageurs and global retail buy it on
the venues that already list it. When Binance has no perp, the Binance spot pair is that venue. Side: **long Binance
spot <COIN>USDT, short BTCUSDT perp (equal notional)**; also reported unhedged (long spot only).

## Events (code A3/code/events.py; screen in A3/events_screen.txt)
- Notices: stream A's parsing (A/code/events.py `markets`, `start_time`, imported, not edited) of every cached
  KRW-titled notice body with first_listed_at in 2020-01-01..2024-12-31 UTC (79 KRW titles, all bodies cached), plus
  A's declared secondary source (2020 이벤트 notices).
- Keep a coin if: the body puts it on the KRW market; not a stablecoin; **no Binance USDT-M perp trading from >= 7 d
  before N through N + 1 d** (A's `perp_for`, so the set is disjoint from A / A2); **Binance spot <COIN>USDT trading
  >= 7 d before N** (spot_first.csv, and for coins absent from it a HEAD probe of the spot aggTrades file on N - 7 d
  and on N: all absent coins return 404 on both days).
- **Result of the screen: 5 events, all IS, 0 VAL.**

| coin | N (UTC) | notice | Binance spot since | Binance perp |
|---|---|---|---|---|
| HIVE | 2020-07-21 07:10:45 | 1384 | 2020-04-27 | none at N |
| KAVA | 2020-07-23 05:00:31 | 1388 | 2019-10-25 | listed 2020-07-28 (after N) |
| SAND | 2021-01-21 08:00:02 | 1740 | 2020-08-14 | listed 2021-01-25 (after N) |
| STX | 2021-04-05 06:25:09 | 1882 (with AXS, FLOW, DAWN) | 2019-10-25 | none at N (2023-02) |
| NU | 2021-10-15 04:00:01 | 2217 (with SOL, MATIC) | 2021-06-04 | listed 2021-10-21 (after N) |

- 2022-24: every KRW coin had either a Binance perp >= 7 d old (A / A2's events), or no Binance spot (WEMIX, CTC, MNT,
  AKT, UXLINK, CARV, SAFE, DRIFT, MOCA ...), or a Binance spot listed the same day or within 7 d (T, APT, SUI, SEI,
  ZRO, MOVE, ME, VANA). Binance now lists the perp with or before the spot, so the spot-only case has died out.
- **Info-only set (declared now, never used for a verdict):** JST 2020-08-14 (spot 3 d old), T 2022-03-02 (spot 5 d
  old), GAL 2024-07-11 (spot since 2022-05; its perp was live at N but stopped the next day, Galxe migration, so both
  A and this screen drop it). These are the only near-misses with a pre-existing spot pair.
- L = first Upbit KRW 1m candle (api.upbit.com/v1/candles/minutes/1, A's pull_first walk, own cache folder). If the
  market is delisted (404): a sibling coin's L from the same notice (STX -> AXS's L, NU -> SOL's L, as A did for
  MATIC), else stated start + 5 min.

## Rule (frozen from A2-D5L; only the instrument changes; code A3/code/analyze.py)
- Entry: long spot at the price of the first spot aggTrade with time >= N + 5 s; short BTCUSDT perp at the first
  futures/um aggTrade >= N + 5 s.
- Exit: each leg at its first aggTrade with time >= L.
- Costs: spot taker 10 bp a side + perp taker 5 bp a side = 30 bp per hedged trade, plus A2's slippage on each of the
  4 fills (half the median 1 s range, (max - min) / min over 1 s bins with trades, in the 60 s from the fill), plus
  real BTC funding received by the short at stamps in (entry, exit]. Spot cash cost: reported as 5 %/yr x hold
  (negligible over minutes), not deducted from the headline.
- Unhedged: long spot only, 20 bp + 2 slippages.
- Robustness as A2: costs x1.5, one step late (N + 10 s). Random benchmark as A2: same coin, same day, random seconds
  outside [N - 15 min, max(N + 30 min, L + 60 min)], same hold, 1,000 draw sets, percentile of the event gross mean.
- One cell only (no grid), so no max-over-cells null. t clustered by notice day (A2's `clt`).
- Descriptive (as A2): path r(t) = ln(spot / spot_ref) - ln(BTC / BTC_ref), ref = last trade <= N - 60 s, at the A2
  offsets; burst onset (a) = first spot trade in N +- 300 s with r >= +2 %; time to 50 % / 90 % of r(N + 60 s);
  raw spot path too; real spot slippage in the first seconds.

## Data (pulled after this file)
- data.binance.vision `spot/daily/aggTrades/<SYM>/<SYM>-aggTrades-<day>.zip` for the 5 + 3 events, and
  `futures/um/daily/aggTrades/BTCUSDT/...` for the event days not in research/data/upbit_latency/npz (read-only reuse
  for 2021-04-05 and 2021-10-15). Streamed to research/data/upbit_spot_notice/tmp/, parsed with `python -I`, deleted.
  Kept: trades in [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min] plus A2's 1 s day series, npz/.
- Spot aggTrades timestamps: ms (switch to us only in 2025, outside the window; the parser handles both as A2).

## Bars and power arithmetic (before any return)
- **VAL has 0 events, so the rule cannot pass any bar:** LIVE needs VAL t >= 1.5 and DEMO needs VAL net > 0, both
  undefined at n = 0. The verdict is "none" whatever IS shows; IS is reported as description only.
- IS: 5 events on 5 days; t >= 2.5 would need SR ~ 1.1 per trade.
- HOLD pace: no registered spot-only HOLD count exists; the 2020-24 pace is 5 events in 5 years (0 in 2022-24), so
  n_HOLD over 22 months ~ 0-2. Power = SR x sqrt(n_HOLD) >= 3 would need SR >= 2.1 per trade at n 2, i.e. never.
  Even pooled with A2's 92 perp events (same notices, different instrument), the spot set adds ~0-2 trades.
- Prior: A2 found the perp jump half done 1.2 s after N in VAL but 11 s in IS (2020 reactions 5-88 s). The 2020-21 spot
  events may therefore still show a drift after N + 5 s; it does not matter for the verdict.
