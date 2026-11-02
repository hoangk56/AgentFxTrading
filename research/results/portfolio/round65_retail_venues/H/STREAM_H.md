# Stream H (round 65): Bithumb KRW listings, K2's rule frozen

Written 2026-11-01 11:06 UTC (`date -u`). Hypotheses were declared in [HYPOTHESES_H.md](HYPOTHESES_H.md) at 10:40 UTC,
before any event date or return was computed. HOLD (2025-01-01..) was never requested, loaded or counted, and there
is no PREREG draft.

## Answer first: none (fails DEMO and LIVE)
- **H72 (the frozen K2 rule), all 99 events:**
  - IS 2020-21: **+432 bp/trade, t 1.92** (n 24). That is below the DEMO bar of IS t >= 2.0.
  - VAL 2022-24: **-75 bp, t -0.31** (n 75). The VAL bar needs net > 0.
  - Years: 2020 +175, 2021 +538, 2022 +119, 2023 -459, 2024 +264 (4 / 5 positive).
  - Random benchmark: IS 99.2 % against other alts and 92.8 % against the same coin. VAL only 5.6 % / 18.8 %.
  - Power at VAL size: SR -0.036 x sqrt(~46 HOLD events) ≈ **-0.24**.
- **Bithumb-only events** (96 of 99; the independent test): IS +489 bp, t 2.15 (n 23); VAL -115 bp, t -0.47
  (n 73). This split is not the declared rule, and its VAL is negative anyway.
- **Overlap with Upbit is almost nil.** Only 3 events have Upbit's first KRW candle within +-7 days:
  - DOT 2020-10: Upbit first by 2 days, -869 bp.
  - GMT 2022-05: Bithumb first by 1 day, +1226 bp.
  - PYTH 2024-02: the same hour, +1537 bp.
  Bithumb and Upbit list the same coins months apart, so these events would be independent of K2. They just do not
  earn.
- **The pump before entry is small.** The alt gains **+5.5 % (IS) / +5.9 % (VAL)** against BTC from L - 24 h to the
  entry. On Upbit it gained +21.5 %. A Bithumb listing draws far less of a rush. The pump size does not sort trades
  either: the VAL correlation of run-up with net is +0.10.
- **Why VAL fails.** The median VAL trade is +246 bp (64 % win), but two squeezes sink the mean:
  - CYBER 2023-08: -13,391 bp. The perp was only 8 days old.
  - BIGTIME 2023-11: -9,072 bp.
  Without the two worst trades VAL is +230 bp, t 2.14. That number is post-hoc, and the rule has no stop by design.
  2023 is negative as a year (34 trades, -459 bp).
- **C3 daily-P&L correlation:** IS -0.037, VAL +0.007 (h_c3corr.txt). It does not matter, since no cell has DEMO
  numbers.

## Data (public, no key, no e-mail; research/data/bithumb/requests.log)
**Bithumb (api.bithumb.com).**
- robots.txt returned 404, a JSON "No static resource" (no file). Logged 10:38:25 and saved under raw/.
- 1452 requests, >= 0.3 s apart in one process at a time:
  - 1421 returned 200 and 1 returned 404 (robots).
  - 30 were local UnicodeEncodeErrors on 5 Chinese-character tickers in the probe; nothing was sent for them.
  - No 403, 418 or 429.
- The v1 API (`/v1/market/all`, `/v1/candles/months|days|minutes/60`) mirrors Upbit's.
  - `to` is read as **KST**, and a `Z` suffix is rejected with a 400.
  - Every series request used `to=2025-01-01T08:59:59` (= 2024-12-31 23:59:59 UTC) or earlier. Rows were cut at
    ts < 2025-01-01.
- **How far history goes.** The full history is visible: BTC month candles start 2013-12, and BTC day candles were
  pulled from 2019-06.
- **Delisted markets are invisible.** All 515 Binance-perp coins absent from the current list returned "Code not
  found" (probe_delisted.csv; LUNA among them). The bias is the same as Upbit's: delisted, faded listings are
  missing, which probably works against the short.
- **Legacy endpoint.** `/public/candlestick/<C>_KRW/24h` returns only the latest ~200 candles and takes no end time.
  It was called once in the first probe and then never used.
- **Mistake.** One probe request (`/v1/candles/days?market=KRW-SOL&count=2`) went out without `to`. It returned
  2026-10 values, which were printed once and used nowhere.

**Universe and event dates.**
- 489 KRW markets now listed. 369 of them map to a Binance USDT-M perp (also checked under the 1000 / 1000000 / 1M
  prefixes).
- Results of the first-candle search:
  - 199 coins have a first candle before 2025.
  - 156 have no candle before 2025.
  - 13 start in the last KST hours of 2024-12-31, so their first day falls in 2025 and they are skipped.
- Filters: perp >= 7 days old at L, L in 2020-01-01..2024-12-27, and BTC / USDC excluded as in k2.events().
  That leaves 102 events.
- The declared collision guard dropped 3: BTT (ratio 0.001), RAY (22.7) and STRAX (0.095).
  **99 events remain: IS 24, VAL 75.** They are listed in h_events.csv.
- The declared rename guard flagged nothing.
- **Post-hoc check (it chose nothing): is L a real trading start?** In burst.csv, the first-day KRW value is >= 2x the
  median of days 2-8 for 87 of 99 events. The rest (CYBER, BONK, DOGE, BIGTIME and others) are listings into an
  ongoing mania. There is no sign of truncated history.

**Binance (fapi.binance.com).**
- 2052 requests, all returning 200. They fetched the 1m klines for k2rule.trade / px and fundingRate where no local
  file existed.
- The random benchmark used local 1h files cut at ts < 2025-01-01. They cover 62 of the 75 VAL events.

## Rule (frozen; H/code/k2rule.py)
- **Code.** This is a copy of round64_parallel/K/coord/hold/k2rule.py. Only the log folder `D` and the docstring
  changed (shown by `diff`). `trade()`, `px()`, `funding()` and `COST = 0.0042` are byte-identical.
- **Event.** L is the start of the coin's first Bithumb KRW 60-minute candle.
- **Trade.** Short the alt perp and long BTCUSDT perp at the 1m close at L + 1 h. Exit after 72 h. Cost 42 bp, plus
  real funding.

## Results (net bp / trade, t clustered by entry day; h_output.txt)
| cell | era | n | gross | fund | **net** | **t** | median | SR | x1.5 | +5 min | L + 2 h | H24 (t) | run-up |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H72 all** | IS | 24 | +471 | +4 | **+432** | **1.92** | +657 | 0.41 | +411 | +416 | +227 | +497 (4.85) | +5.5 % |
| | VAL | 75 | -8 | -25 | **-75** | **-0.31** | +246 | -0.04 | -96 | -82 | -97 | -89 (-0.54) | +5.9 % |
| Bithumb-only | IS | 23 | +527 | +4 | +489 | 2.15 | +662 | 0.46 | +468 | +473 | +272 | +510 (4.81) | +6.0 % |
| | VAL | 73 | -47 | -26 | -115 | -0.47 | +215 | -0.05 | -136 | -123 | -145 | -98 (-0.58) | +5.9 % |
| Joint (+-7 d of Upbit) | IS / VAL | 1 / 2 | | | -869 / +1382 | | | | | | | | |

**Per year (H72 all):**

| year | n | net |
|---|---|---|
| 2020 | 7 | +175 |
| 2021 | 17 | +538 |
| 2022 | 6 | +119 |
| 2023 | 34 | -459 |
| 2024 | 35 | +264 |

**By Upbit status, inside Bithumb-only (descriptive; these sub-splits were declared as overlap reporting, not as
rules):**

| Upbit status | IS | VAL |
|---|---|---|
| Upbit listed earlier (Bithumb catching up) | +219, n 7 | +435, t 3.33, n 19 |
| Upbit listed later | +610, n 5 | -1040, n 10 |
| Upbit never | +606, n 11 | -142, n 44 |

The "Upbit earlier" VAL cell is chosen on VAL and its IS t is 0.45. It is not a candidate.

**Random benchmark (gross on 1h closes, fill at L + 2 h, 500 draws; h_random.txt):**

| hold | era | event mean | other alts, same hour: pct (median) | same coin 30-180 d later: pct (median) |
|---|---|---|---|---|
| H72 | IS | +280 | 99.2 % (-175) | 92.8 % (-21) |
| H72 | VAL | -89 | 5.6 % (+34) | 18.8 % (+18) |
| H24 | IS | +452 | 100 % | 100 % |
| H24 | VAL | -116 | 3.0 % | 4.2 % |

## Bars
- **LIVE: fails.**
  - IS t 1.92 < 2.5.
  - VAL t -0.31 < 1.5.
  - Random 5.6 % in VAL.
  - Power ≈ -0.24.
- **DEMO: fails.**
  - IS t 1.92 < 2.0.
  - VAL net -75 < 0.
  - VAL random < 90 %.
- **The sibling cells change nothing.**
  - H24 has IS t 4.85, but its VAL is -89 bp.
  - It was declared for reference only, and it fails VAL too.

## What failed and why
- **Bithumb listings carry a much smaller Korean rush.**
  - The run-up is about a quarter of Upbit's (+6 % vs +21.5 %).
  - Bithumb lists ~25 perp coins a year in 2023-24, against Upbit's ~10 (K2 VAL). Many are coins Upbit already lists,
    or small coins listed into an ongoing global pump.
- **The fade exists in 2020-21 and in the median, but the short tail dominates VAL.** Shorting a newly listed
  small-cap perp (CYBER: the perp was 8 days old) meets round 60's squeeze tail. K2's universe had fewer such cases.
- **The mechanism does not generalise across Korean venues on this evidence.** The edge looks specific to Upbit
  listings, where the pump before entry is large. One reading: the K2 effect scales with the size of the pump. That
  is a new hypothesis, not tested here.

## Pitfalls
- **`to` is in KST on Bithumb's v1 API.** A UTC string silently shifts the window by 9 h. The cut was enforced at
  load as well.
- **Coin codes reused across renames carry the old history.** For example, `A` (Vaulta, ex-EOS) starts in 2017. The
  perp-age filter removes these cases.
- **Chinese-character tickers in `/v1/market/all`** need URL encoding. They are irrelevant to the universe.

## What a user decision could unlock
- Nothing for this rule.
- A test of whether K2's edge scales with the pre-entry pump would need a declared rule and pooled venues (Upbit +
  Bithumb + stream I's venues), with the pump threshold fixed on IS. The Bithumb IS has only 24 events.

Files: HYPOTHESES_H.md, STREAM_H.md, h_events.csv, h_trades.csv, h_output.txt, h_random.txt, h_c3corr.txt; code in
H/code/ (k2rule.py, bnet.py, pull_events.py, events_h.py, run_h.py, stats_h.py, random_h.py, burst.py, c3corr_h.py).
Data: research/data/bithumb/ (first_candles.csv, btc_days.csv, probe_delisted.csv, burst.csv, raw/, requests.log).
