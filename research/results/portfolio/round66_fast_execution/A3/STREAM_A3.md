# Stream A3 (round 66): Upbit KRW-listing notice -> Binance SPOT (coins without a Binance perp). None

Written Sun Nov 1 13:57:17 UTC 2026 (from `date -u`). The rule, event screen, costs and power were declared at
13:53:40 UTC in [HYPOTHESES_A3.md](HYPOTHESES_A3.md), before any aggTrade or candle was downloaded. HOLD
(2025-01-01..) was never requested, loaded or counted: only daily files dated 2020-07-21..2024-07-11 were pulled, and
every N < 2025.

## Answer first
- **None.** The event set is 5 IS events and **0 VAL events**, so no LIVE or DEMO bar can be tested; this was declared
  before any return. The IS t is below DEMO's 2.0 anyway. No PREREG_DRAFT.
- **Why the set is empty after 2021.** In 2022-24, Binance had one of three things for every KRW coin Upbit listed:
  a perp >= 7 d old (these are A / A2's 32 events), no spot pair at all (WEMIX, CTC, MNT, AKT, UXLINK, CARV, SAFE,
  DRIFT, MOCA, ...), or a spot pair listed the same day or < 7 d before (T, APT, SUI, SEI, ZRO, MOVE, ME, VANA).
  Binance now lists perps together with or before spot, so "Binance spot, no perp" has died out as an Upbit-listing
  case. The pace was 5 events in 2020-21 and 0 in 2022-24, so the expected HOLD count is ~0-2.
- **The spot path is like the perp's, and as fast** (main IS, n 5; spot vs BTC, from N - 60 s). Median: 0 s +3 bp,
  +1 s +734, +2 s +723, +5 s +840, +10 s +1,061, +30 s +1,246, +60 s +1,402, +300 s +2,539. The onset (+2 %) comes a
  median 0.8 s after N, half the +60 s level at 1.8 s, 90 % at 30 s. Across all 8 events (adding JST, T, GAL), the
  onset is 0.7 s and +5 s is +902. HIVE (2020) moved 9 s before its stamp; the other 7 moved 0.3-0.9 s after it.
- **Frozen D5-L on spot** (long spot / short BTCUSDT perp at the first trades >= N + 5 s, exit at the first trades
  >= L; 30 bp + A2 slippage + BTC funding):
  - IS: **+3,243 bp net, t 1.53, n 5 (5 days)**, median +1,504, SR 0.69. Years: 2020 +352, 2021 +5,170.
    Random: 100 %. Costs x1.5: +3,187. One step late (10 s): +3,002.
  - VAL: n 0.
  - Power: undefined at VAL size. Even if the IS SR held, it would be 0.69 x sqrt(1-2) = 0.7-1.0, where LIVE needs 3.
  - Unhedged long: IS +3,268, t 1.55, almost the same (BTC moves little in minutes).
  - NU (+11,554 bp) carries the mean. Without NU: +1,165 bp, t 2.29.
- **Capacity is thin.** The median buyer-taker spot notional in the 1 s after N + 5 s is **$1,666**; over 5 s it is
  $28.8k (NU had $10 in that second). For A2's perp events it was $240k over 1 s. A $10-30k order walking the real
  taker-buy prints takes 3-8 s to fill and costs 0-180 bp (checks.txt).

## Events (A3/events.csv, screen in A3/events_screen.txt)
| coin | set | N (UTC) | L - N | spot since | perp |
|---|---|---|---|---|---|
| HIVE | main IS | 2020-07-21 07:10:45 | 9 min | 2020-04 | 2024-12 |
| KAVA | main IS | 2020-07-23 05:00:31 | 140 min | 2019-10 | 2020-07-28 (after N) |
| SAND | main IS | 2021-01-21 08:00:02 | 5 min | 2020-08 | 2021-01-25 (after N) |
| STX | main IS | 2021-04-05 06:25:09 | 5 min | 2019-10 | 2023-02 |
| NU | main IS | 2021-10-15 04:00:01 | 130 min (SOL's L, KRW-NU 404) | 2021-06 | 2021-10-21 (after N) |
| JST | info IS | 2020-08-14 07:00:33 | 4.5 min | 3 d old | none |
| T | info VAL | 2022-03-02 03:30:02 | 275 min | 5 d old | later |
| GAL | info VAL | 2024-07-11 02:22:28 | 42.5 min (stated + 5, KRW-GAL 404) | 2022-05 | live at N, stopped next day |

- The info set was declared before any data and is never used for a verdict. Pooled, all 8 give +2,259 bp, t 1.67,
  and VAL (T, GAL) gives +45 and +1,142.
- The 79 KRW-titled notice bodies are all in the existing caches. For each coin absent from spot_first.csv, HEAD probes
  of the spot aggTrades file on N - 7 d and on N both returned 404 (30 coins).

## Results (net bp per trade; results.txt, cells.json, trades.csv)
| set | cell | n (days) | gross | slip | fund | cash* | net | t | median | SR | years | rand % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| main IS | **H5-L (frozen)** | 5 (5) | 3354 | 81 | 0.0 | 0.05 | **3243** | **1.53** | 1504 | 0.69 | 2020 +352, 2021 +5170 | 100 |
| | H5-L costs x1.5 | | | | | | 3187 | 1.51 | | | | |
| | H10-L (late) | | 3115 | 83 | | | 3002 | 1.45 | 1503 | 0.65 | | |
| | U5-L unhedged | 5 (5) | 3369 | 81 | | | 3268 | 1.55 | 1560 | 0.69 | 2020 +368, 2021 +5202 | 100 |
| main VAL | all | 0 | | | | | | | | | | |
| info VAL (T, GAL) | H5-L | 2 (2) | 697 | 74 | 0.5 | 0.15 | 593 | 1.08 | 593 | 0.76 | 2022 +45, 2024 +1142 | |
| all 8 pooled | H5-L | 8 (8) | 2371 | 82 | 0.1 | 0.07 | 2259 | 1.67 | 906 | 0.59 | 4/4 years > 0 | 100 |

\* Cash: the cost of the spot leg's cash at 5 %/yr over the hold. It is not deducted and is at most 0.15 bp.

**Per event, H5-L net:** HIVE +415, KAVA +289, SAND +2,451, STX +1,504, NU +11,554 | JST +670, T +45, GAL +1,142.
The entry fills are 5.00-5.14 s after N on spot and 5.01-5.36 s on BTC. The spot slippage at entry (half the median
1 s range) is 22-91 bp, against ~0 at N - 10 min.

**Post-hoc (checks.txt, chooses nothing):**
- With the worst spot price of the 1 s as the entry, the result is +3,180, t 1.50. With a $10k walk it is +3,207,
  t 1.49; with $30k, +3,185, t 1.48.
- Leave-one-out t ranges from 1.27 (drop SAND) to 2.29 (drop NU).

## Bars
| bar | needed | A3 |
|---|---|---|
| IS t | LIVE 2.5 / DEMO 2.0 | 1.53: fail |
| VAL net, t | DEMO > 0; LIVE t >= 1.5 | n 0: untestable, fail |
| years positive | >= 2/3 | IS 2/2; VAL none |
| random | >= 95 % / 90 % | 100 % (IS) |
| x1.5, late | > 0 | +3,187 / +3,002 |
| HOLD power at VAL size | >= 3 | undefined; <= ~1 at the 2020-24 pace |

## What failed and why
- **The sample is structural, not noise.** Spot-only Upbit KRW listings ended after 2021, because Binance's listing
  practice changed. There is no VAL, and the forward pace is ~0-1 a year, so power can never reach 3.
- **IS is 5 bull-market 2020-21 events, and one of them is NU.** NU's spot rose ~+140 % within 5 minutes of the
  notice (raw log return +0.89 at +300 s) and kept rising into the KRW open 130 min later. Most of the drift after N + 5 s is the slow 2020-21 reaction (90 % only at
  ~30 s), which A2 also saw on the perp in IS and which was gone by VAL (half the move inside 1.2 s).
- **Thin spot books.** $1.7k of taker buying in the first second after N + 5 s; a real order would be the flow.

## Pitfalls met
- **Module name clash.** Stream A's `events.py` and A3's `events.py` collide on import. A's module is loaded by path
  under another name (importlib); it is not edited.
- **GAL 2024-07-11.** Its perp was live and >= 7 d old at N, but stopped trading the next day (Galxe migration). A's
  `perp_for` (which needs N + 1 d) misses it, so a "live on N's day" check was added, and GAL went to the info set.
- **spot_first.csv has rows only for perp-listed names.** Coins that never had a perp are absent from it, so their
  spot existence needed HEAD probes.
- **The calm spot baseline 1 s range is 0.** Bins at that time hold one trade, so the A2 slippage model is near zero
  outside the jump.

## What a user decision could unlock
- **Other venues.** The same notices on Bybit / OKX / Bitget spot, where an Upbit-listed coin often trades before it
  reaches Binance (2022-24 coins with no Binance spot: WEMIX, MNT, AKT, UXLINK, CARV, SAFE, DRIFT, MOCA, ...). That is
  outside this brief's data rules (data.binance.vision only), and capacity there is likely thinner still.
- **No effect on A2-D5L.** The spot set would add ~0-1 HOLD trades a year to A2's 92 perp events.

## Files
- **Code (A3/code/):**
  - events.py: the screen.
  - probe.py: HEAD existence probes.
  - pull_L.py: Upbit first KRW candle and fallbacks.
  - pull.py: aggTrades stream / cut / delete.
  - analyze.py: path, cell, random, power.
  - checks.py: post-hoc.
  - net.py
- **A3/:**
  - HYPOTHESES_A3.md, STREAM_A3.md
  - events_raw.csv, events_screen.txt, events.csv
  - results.txt, checks.txt, cells.json, trades.csv
- **Data (research/data/upbit_spot_notice/):**
  - npz/: 14 files, 4.5 MB.
  - up1m/: 9 candle pages.
  - requests.log: 84 lines. 1 robots (404), 60 HEAD, 9 api.upbit.com, 14 aggTrades zips (142 MB, all deleted). No
    403 / 418 / 429.
  - pull.out
  - BTCUSDT 2021-04-05 and 2021-10-15 were reused read-only from research/data/upbit_latency/npz.
