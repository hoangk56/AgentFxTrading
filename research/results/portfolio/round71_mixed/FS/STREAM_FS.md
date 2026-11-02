# Round 71 stream FS: crash-wick fade on Binance SPOT coins without a USDT-M perp, result

Written 2026-11-01 18:31 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_FS.md](HYPOTHESES_FS.md), 17:52 UTC, before any price or volume was read. Addendum 1 (18:01
  UTC) recorded the symbol list, the universe stats and the pull order before any 1m file was opened.
- Code: `code/` (net, common, exinfo, vol1d, univ, pull1m, events, pull_agg adapted from F0, analyze).
- Outputs: `out/report.txt` (every number below), `out/cells.json`, `out/trades_X*_H*.npz` (small, per trade),
  `out/coverage.txt`, `out/events.log`.

No HOLD data was requested or loaded: monthly files <= 2024-12, daily files <= 2024-12-31, API endTime
2024-12-31 23:59:59.999, and every series is cut at ts < 2025-01-01. F/coord/ and binance_1m_wicks_hold/ were never
opened.

## Answer: none. No cell passes the IS bar (best IS t 0.70); no PREREG_DRAFT

Same mechanism, different coins. F's >= 5 % idiosyncratic one-minute crash fade earned ~+300 bp gross per trade on
top-40 USDT-M perps in IS / VAL (and then failed HOLD). On the top-40 spot coins with **no** perp, the same crash
reverts only +78 / +86 bp gross in IS (H15 / H60). In VAL it reverts +68 bp in 15 minutes and then **keeps falling**:
-67 bp gross at H60. After 42-80 bp of measured cost, nothing is left.

| cell | era | n | net bp | t (day) | S / trade | median | gross | x1.5 (t) | e+1 close entry (t) | years + | random % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X5 H15 | IS | 728 | +18.5 | 0.70 | 0.027 | -15 | +77.7 | -11.1 (-0.42) | -35.7 (-1.45) | 4 / 5 | 100 |
| | VAL | 1025 | +25.9 | 1.05 | 0.038 | -2 | +68.1 | +4.8 (0.19) | -16.6 (-0.67) | | 100 |
| X5 H60 | IS | 728 | +28.5 | 0.49 | 0.030 | -57 | +86.3 | -0.5 (-0.01) | -25.6 (-0.46) | 1 / 5 | 100 |
| | VAL | 1021 | -108.0 | -3.00 | -0.119 | -100 | -66.7 | -128.6 (-3.58) | -150.3 (-4.06) | | 0 |
| X8 H15 | IS | 112 | -62.2 | -0.72 | -0.068 | -37 | +18.0 | -102.2 (-1.18) | -179.0 (-2.33) | 4 / 5 | 79 |
| | VAL | 210 | +132.5 | 2.12 | 0.151 | +96 | +183.5 | +107.0 (1.72) | +59.3 (0.99) | | 100 |
| X8 H60 | IS | 112 | +72.3 | 0.36 | 0.058 | +92 | +146.7 | +35.0 (0.18) | -42.7 (-0.21) | 4 / 5 | 100 |
| | VAL | 209 | +5.0 | 0.05 | 0.004 | -23 | +54.1 | -19.5 (-0.20) | -68.7 (-0.71) | | 100 |

Years (net bp, n):

| cell | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| X5 H15 | +32 (277) | +10 (451) | -1 (440) | +35 (233) | +53 (352) |
| X5 H60 | -7 (277) | +50 (451) | -119 (440) | -70 (232) | -119 (349) |
| X8 H15 | +97 (44) | -165 (68) | +93 (89) | +155 (33) | +164 (88) |
| X8 H60 | +121 (44) | +41 (68) | +43 (89) | +62 (33) | -55 (87) |

**Bars:**
- The IS t needs to be >= 2.0 (DEMO) or >= 2.5 (LIVE). The best IS t of the 4 declared cells is 0.70 (X5 H15).
  Every cell is "none".
- The max-over-4 random null: median -1.62, p95 +0.05 against a real max of +0.70. Random entries only lose their cost
  (-44 to -82 bp), so "beats random" is easy here, as in F. It is the t that decides.
- X8 H15 is the only cell with a VAL t above 2 (+132.5, t 2.12). It lost in IS (-62 bp, t -0.72) and loses one step
  late in IS (t -2.33). It would not have been selected: the IS-best cell is X5 H15. Even if it had been, its HOLD
  power at the VAL rate would be 0.151 x sqrt(161 HOLD trades) = **1.71** (1.92 at the 2024 rate), far below 3.
- Power for the other cells: X5 H15 0.95, X5 H60 < 0, X8 H60 0.05.

## Measured costs (aggTrades, 2,416 tradable candidates)
| | IS | VAL |
|---|---|---|
| first trade after close_e, median / p90 | 0.14 s / 2.4 s | 0.10 s / 0.67 s |
| entry half-spread, median / mean | 14.1 / 25.1 bp | 10.2 / 14.2 bp |
| share of entries measured in the first second (else 10 s, 60 s, then the 50 bp fallback) | 70 % (22 / 6 / 2 %) | 86 % (14 / 1 / 0 %) |
| exit half-spread (H60), median / mean | 7.7 / 13.2 bp | 5.6 / 9.2 bp |
| USD traded in the entry second, median | ~$3,000 | ~$3,600 |
| round-trip cost per trade, mean (X5 / X8) | 58-59 / 75-80 bp | 41-42 / 49-51 bp |

- The fees are 20 bp of the round trip. The rest is spread.
- Only ~$3-5k trades in the entry second. A real fill of more than a few thousand dollars would pay more than the
  model.
- **Entry QC:** the first aggTrade >= close_e equals the spot kline open of e+1 in 99.8 % of events. Unlike perp
  klines (F0: 21.5 % of opens are the previous close), spot 1m opens are the first trade.

## Why the spot-only crash does not revert like the perp wick
- **No perp means no perp liquidation engine.** F's wicks were leverage-forced flow on thin perp books: the overshoot
  was ~300 bp and came back over an hour.
- **A >= 5 % idiosyncratic one-minute drop on a no-perp spot coin is more often a seller with information or intent.**
  That seller may be a team or a holder unlocking, a delisting or monitoring-tag announcement, or an exchange outflow.
- **The evidence is in VAL.** The 15-minute bounce (+68 bp gross) turns into a further fall by 60 minutes (-67 bp
  gross, median trade -100 bp net). 2022-24 are all negative at H60, and the loss holds:
  - without the top 3 coins: -130 bp;
  - without the top 5 days: -157 bp;
  - without the LUNA / FTX months: -129 bp.
- **Size helps only a little.** At >= 8 % the H15 gross is +18 (IS) / +184 (VAL) bp. It is unstable across years
  (2021 -165 net) and rests on ~100-200 events.
- **New listings (< 90 days since the first spot day)** look better in several cells, e.g. X8 VAL n 11, +575 / +1,099
  bp. The counts are tiny and this was not a declared cell: information only.

## Pitfall checks (IS / VAL, from out/report.txt)
- **Breadth:** 147 / 173 coins traded (X5). About half of the coins have a positive mean, and the win rate is 47-50 %.
  The X5 H15 IS mean rests on its top 3 coins (PNT, TLM, FET); without them it is +0.9 bp.
- **Crash days:**
  - IS without 2020-03-12/13 and 2021-05-19: X5 H15 +19.6 (t 0.69), X5 H60 -23.7.
  - VAL without 2022-05 and 2022-11: X5 H15 +19.3, X5 H60 -128.5.
- **Clustering:** 35-41 % of X5 events fall on days with >= 5 events (18-23 % at X8).
- **One step late (close of e+1):** worse in every cell. The small first-minute bounce is the only part that pays.

## Set-up (as declared)
- **Universe:**
  - Each UTC day, the top 40 eligible spot <BASE>USDT pairs by mean quote volume over d-30..d-1. All 30 days must be
    present.
  - Excluded: stablecoins / fiat / gold, leveraged tokens, round 60 EXCL_BASE, and any coin with a USDT-M perp
    (1000x / 1M prefixes and LUNA2 mapped) whose first daily kline is on or before d.
  - 40 pairs every day, 329 distinct symbols; 139 / 175 / 178 / 182 / 130 distinct per year 2020..2024.
  - The 40th pair's 30-day volume was $0.5 M / day (2020), $13 M (2021), $4.9 M (2022), $1.6 M (2023) and
    $2.4 M (2024).
- **Event:**
  - r_e = c_e / c_{e-1} - 1 <= -5 % / -8 % on consecutive bars;
  - |r_BTCUSDT spot| <= 0.2 |r_e|;
  - >= 10 trades and quote volume > 0 in bar e;
  - guard: the first aggTrade after close_e is still beyond half-way;
  - a trade within 60 s of close_e;
  - one event per coin per 60 bars.
  - Counts: 2,426 candidates (IS 979 / VAL 1,447). 2,422 have a trade after close_e, 2,416 within 60 s, and 2,396 pass
    the guard.
  - After de-duplication: X5 has IS 728 / VAL 1,025 events and X8 has IS 112 / VAL 210.
- **Trade:**
  - long at the first aggTrade >= close_e; the declared check enters at the close of e+1;
  - exit at the close of e+16 / e+61 (<= 5 min forward fill);
  - net = gross - 20 bp - the measured entry and exit half-spreads (floored at 0; fallbacks 50 / 25 bp).
- **Random benchmark:** 200 draws per event, from the same coin, the same era and the same trailing-sd decile, at
  in-universe minutes with r < 0. Entry at the next bar's open, the same H and the event's cost.

## Power arithmetic (declared vs found)
- **Declared:** n_H = 150 / 300 / 600 HOLD trades would need S >= 0.245 / 0.173 / 0.122.
- **Found:**
  - X5 cells have ~640 HOLD trades at the VAL rate, but S is 0.04 (H15) or negative (H60).
  - X8 cells have ~160 HOLD trades. X8 H15's VAL S of 0.151 gives power 1.7.
  - No cell is near 3.
- **HOLD rate:** the no-perp universe in HOLD is probably thinner still, because Binance now lists perps within days
  of spot.

## Data pulled (research/data/spot_wicks/, git-ignored)
- `exinfo/exchangeInfo.json` and `spot_usdt_symbols.csv`: 775 USDT pairs, incl. 256 BREAK; old delisted pairs are
  present.
- `vol1d.npz`: daily quote volume and trade count for 464 symbols, 2019-11..2024-12. It came from data-api.binance.vision
  /api/v3/klines; prices were not kept.
- `univ.npz`, `pull_list.csv`, `pull_order.csv`.
- `npz/`: 3,812 spot monthly 1m files (1.8 GB). One pull-list month is 404 (ERDUSDT 2020-09). The pull took 19.5 min
  and zips were never written to disk.
- `agg/`: 1,471 spot daily aggTrades symbol-days (210 MB, window rows only, 1.78 GB streamed in 7.9 min), plus
  `agg_progress.json`.
- `cand.npz`: candidates and random draws.
- `requests.log`: 6,283 lines, 17:51-18:30 UTC.
  - 6,269 x 200.
  - 3 x 404: the data.binance.vision and data-api robots.txt files, and ERDUSDT 2020-09.
  - 1 x 403: s3-ap-northeast-1.amazonaws.com/robots.txt. That host was stopped at once and never used.
  - 8 errors and 2 failures, from two non-ASCII 2025 symbol names that urllib could not encode. They are irrelevant to
    2020-24.
  - No 418 / 429 / 503.
- Web searches: 0.

## Pitfalls met
- **The S3 bucket listing for data.binance.vision is closed** (403 on robots.txt). The symbol list came from the
  data-api exchangeInfo instead. It keeps delisted pairs (BREAK), so survivorship bias is small.
- **No-perp coins in 2020 were very thin.** The 40th pair traded ~$0.5 M / day. In IS, 30 % of entry spreads could
  not be measured in the first second, and 2 % fell back to the declared 50 bp.

## What a user decision could unlock
Nothing registrable. The crash fade does not carry over from perps to no-perp spot coins. The mechanism F relied on
(perp leverage forcing the flow) is absent, and on spot the 60-minute drift after a crash is negative in VAL. Neighbour
cells (X8 H15 VAL-only, new listings < 90 days) would need fresh declarations, and even then have HOLD power < 2 at
these event rates.
