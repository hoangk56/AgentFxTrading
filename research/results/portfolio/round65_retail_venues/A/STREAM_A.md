# Stream A (round 65): chase the Upbit KRW-listing notice on Binance perps. No LIVE or DEMO rule

Written Sun Nov 1 12:00 UTC 2026 (from `date -u`). Hypotheses and the 6-cell grid were declared at 11:32:29 UTC in
[HYPOTHESES_A.md](HYPOTHESES_A.md). By then the event list and L were built, and no Binance price had been requested.
HOLD (2025-01-01..) was never requested, loaded or counted. Notices were filtered to first_listed_at < 2025-01-01 UTC,
and every fapi request asserted t < 2025-01-01.

## Answer first
**None, for all 6 cells.** The reason is a timing fact: the pump is already in the price within the notice minute.

**Where the move happens** (split_output.txt; gross alt vs BTC on Binance perps; the bar closes are at N0 - 1 and
N0, where N0 = the notice minute):

| window | IS n 12: mean / median | IS share > 0 | VAL n 32: mean / median | VAL share > 0 |
|---|---|---|---|---|
| N - 24 h -> N | +277 / +198 | | +254 / +86 | |
| notice minute (close N0 - 1 -> close N0) | **+1524 / +789** | **100 %** | **+1953 / +1378** | **100 %** |
| N0 -> N0 + 1 | +124 / +80 | 67 % | +116 / +8 | 50 % |
| N0 + 1 -> N0 + 5 | +175 / +62 | 58 % | -133 / -70 | 34 % |
| N0 + 5 -> N0 + 15 | -129 / -3 | 50 % | +57 / +43 | 56 % |
| N + 1 min -> L | +309 / +92 | | -21 / -2 | |
| L -> L + 1 h | -140 / +27 | | -88 / -154 | |

- Upbit's notice moves the Binance perp +15-20 % against BTC within seconds, in every event. That is most of K2's
  +21.5 % run-up from L - 24 h to L + 1 h.
- From a fill 1-2 minutes later, the drift into the KRW open is about zero in VAL. The first KRW hour is negative,
  which is where K2's short begins.
- **The A1 cell is a latency race, and even it is too slow.** Its fill (the close of the bar starting at N0 + 1)
  comes after the jump. The edge, if any, belongs to bots that react in seconds. 1m bars cannot test that.
- **Best IS t among the 5 / 15 min cells:** A15-L with t 1.51 (n 5 on 3 notice days). That is below DEMO's 2.0, and
  with 6 correlated cells it is well inside the max-over-cells null.
  - In VAL the same cell makes +24 bp, t 0.29.
  - The best VAL cell, A5-L, makes +84 bp, t 0.73, SR 0.13. Its power at VAL size is 0.57; LIVE needs 3.
- **No PREREG_DRAFT.** C3 correlation was not computed, since no cell has DEMO numbers.

## Data (research/data/upbit_announce/, requests.log 2175 lines; no account, key or e-mail; UA `research-script`)
**Notice list.** Stream W's 298 list pages, read-only.
- The 3,438 notices dated 2019-10..2024-12 give 161 titles that look like listings (A/listing_titles.json).

**Notice bodies.** 78 KRW-titled 거래 notices, plus 2 이벤트 notices.
- Fetched from api-manager.upbit.com/api/v1/announcements/<id> at 1.5 s per request: 81 × 200 and 2 × 429. After
  each 429 the fetcher backed off and retried. No 403.
- robots.txt was re-read and logged: one comment line, no rules.

**First KRW trade L.** api.upbit.com/v1/candles/minutes/1, the public quotation API (robots.txt 404; 57 × 200, 5 × 404
for delisted markets).
- **The open is always stated time + 5 minutes.** In all 27 events with a stated start, the first 1m KRW candle is
  exactly the stated start + 5 min: buys are blocked for the first 5 minutes.
- **Delisted markets:**
  - STG and BONK: L = stated + 5 min.
  - MATIC: SOL's L (same notice, same markets).
  - SRM: dropped, since L is unknown.

**Binance.** 2014 fapi requests through A/code/k2rule.py. This is K's coord copy; a diff shows only the log folder
changed. It priced 1m fills and funding windows, plus 1500-minute 1m windows for the random draws. There were 16
timeouts or resets, all retried.

## Events (A/notice_events_L.csv)
**Selection.** A coin counts if its notice body puts it on the KRW market, it is not a stablecoin (USDT and USDC are
excluded), and its USDT-M perp traded from at least 7 d before N.
- **Excluded:** BTC- or USDT-only coins (MASK 2021, AUDIO, YGG, IMX 2022, GAL 2023, ACS, ALT, POKT, BIGTIME 2024-04,
  OMNI) and coins with no perp yet (SAND, STX, FLOW, NU, WEMIX, APT, SUI, SEI, MNT, AKT, ZRO, TAIKO and others).
- **Re-listings:** none found. No event had a KRW candle before N.

| era | n | notice days | lag N -> L | notes |
|---|---|---|---|---|
| IS 2020-21 | 12 | 9 | median 5 min (4-210) | Posted at the open (lag 4-5 min): LINK, XTZ, DOT, DOGE, AXS, ALGO, NEAR. Hours ahead: SOL, MATIC, 1INCH (2 h), AAVE (3.5 h). VET (40 min) comes from the 이벤트 notice. |
| VAL 2022-24 | 32 | 32 | median 157 min (20-425) | 2022-23: ~5-7 h ahead. 2024: often 20-75 min. |

**Compared with K2's 40 events.** This list adds MATIC (renamed POL, so it is missing from Upbit's current market list),
STG, BEAM and BONK, and it contains all 40 of K2's events (44 in total).

## Results (net bp per trade; 42 bp + real funding; t clustered by notice day; results.txt, cells.json, trades.csv)
**Columns:**
- **late:** entry 5 minutes later.
- **rS:** percentile of the gross mean vs the same coin at random minutes 30-180 d before N, same hold, on fapi 1m.
- **rO:** the same percentile vs other alive perps over the same minutes.
- **SR:** net Sharpe per trade.

| cell | era | n (days) | hold (median) | price | fund | **net** | **t** | median | SR | x1.5 | late | rS / rO % | years + | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1-L | IS | 5 (3) | 128 m | +737 | +4 | +700 | 1.29 | +330 | 0.80 | +679 | +403 | 100 / 100 | 1/2 | |
| | VAL | 32 (32) | 156 m | -21 | +17 | -46 | -0.35 | -37 | -0.06 | -67 | +44 | 6 / 100 | 1/3 | -0.27 |
| A5-L | IS | 5 (3) | 124 m | +479 | +4 | +442 | 1.41 | +148 | 0.53 | +421 | +473 | 100 / 100 | 1/2 | |
| | VAL | 32 (32) | 152 m | +109 | +17 | **+84** | **0.73** | -29 | 0.13 | +63 | +60 | 98 / 100 | 2/3 | 0.57 |
| A15-L | IS | 5 (3) | 114 m | +434 | +4 | **+397** | **1.51** | +102 | 0.43 | +376 | +232 | 100 / 100 | 1/2 | |
| | VAL | 32 (32) | 142 m | +50 | +17 | +24 | 0.29 | +2 | 0.05 | +3 | +9 | 78 / 100 | 1/3 | 0.22 |
| A1-L1h | IS | 12 (9) | 64 m | +170 | +3 | +131 | 0.26 | +120 | 0.08 | +110 | +6 | 100 / 100 | 1/2 | |
| | VAL | 32 (32) | 216 m | -139 | +42 | -139 | -1.07 | -175 | -0.19 | -160 | -44 | 0 / 0 | 1/3 | -0.83 |
| A5-L1h | IS | 12 (9) | 60 m | +11 | +3 | -28 | -0.06 | +39 | -0.02 | -49 | +72 | 96 / 100 | 1/2 | |
| | VAL | 32 (32) | 212 m | -7 | +42 | -7 | -0.05 | -227 | -0.01 | -28 | -30 | 27 / 97 | 1/3 | -0.04 |
| A15-L1h | IS | 12 (9) | 50 m | +96 | +3 | +56 | 0.18 | +5 | 0.06 | +35 | -9 | 100 / 100 | 1/2 | |
| | VAL | 32 (32) | 202 m | -55 | +42 | -55 | -0.40 | -204 | -0.07 | -76 | -70 | 4 / 15 | 1/3 | -0.32 |

**IS exit-at-L cells.** These cells hold only 5 trades, from 3 days: VET 2020-04-07, SOL / MATIC 2021-10-15 and
1INCH / AAVE 2021-10-27. AAVE alone gives about +1900 bp. They show bull-market 2021 batch days, not a rule.

**VAL exit-at-L cells.** The medians are about 0, and the means rest on AGLD 2024-11 (+2878 in A5-L). Without AGLD,
A5-L makes about -6 bp.

**Random benchmark.** The high rS / rO percentiles in IS mostly measure the rest of the post-jump drift. In VAL they
are mixed (rS 6-98 %). No cell beats random in both eras together with positive net t.

**Years.** Every cell has at least one losing year, and none reaches 2/3 of years positive in both eras.

## Power
- **What LIVE needs.** n_HOLD ≈ 10.7 events/yr × 1.83 yr ≈ 19.5, so LIVE needs a VAL SR per trade of at least 0.68.
  The best VAL SR is 0.13 (A5-L), which gives power 0.57.
- **IS exit-at-L cells (n 5 on 3 days).** These could never carry an IS bar, as declared before the run.
- **IS L + 1 h cells (n 12 on 9 days).** IS t >= 2 would need SR ≥ 0.6. The observed SR is -0.02 to 0.08.

## Chained book "A then K2" (information only; K2 is already registered)
Long from N + E to K2's own entry fill (L_hour + 61 min), then K2's short for 72 h. Same 12 / 32 events.

| E | era | A leg | K2 leg | chain net | chain t | chain SR |
|---|---|---|---|---|---|---|
| 1 | IS | +215 (t 0.42) | +961 (t 2.63) | +1176 | 1.57 | 0.53 |
| 5 | IS | +48 (t 0.11) | +961 | +1008 | 1.54 | 0.53 |
| 15 | IS | +140 (t 0.46) | +961 | +1101 | 1.93 | 0.70 |
| 1 | VAL | -51 (t -0.36) | +488 (t 1.68) | +437 | 1.34 | 0.24 |
| 5 | VAL | +79 (t 0.60) | +488 | +567 | 1.81 | 0.32 |
| 15 | VAL | +27 (t 0.20) | +488 | +515 | 1.72 | 0.30 |

- **The A leg adds noise, not edge.** Chain t is at most K2's own t in IS (1.5-1.9 vs 2.63).
- **The K2 leg replicates on this notice-built list.** It makes IS +961 bp, t 2.63, and VAL +488 bp, t 1.68 (n 32,
  incl. MATIC, STG, BEAM, BONK). That is close to K's +1094 / +423. Information only; K2's registration is untouched.

## What failed and why
- **The latency race is lost at 1-minute resolution.** The whole notice reaction (+15-20 % vs BTC, 100 % of events)
  happens before the close of the notice minute. It cannot be tested with 1m klines.
- **After the jump, alt vs BTC is a random walk with fat tails into the KRW open.** VAL N + 1 min -> L is -21 bp mean,
  -2 bp median.
- **Then it fades.** L -> L + 1 h is -154 bp median in VAL: K2's territory.
- **2020-21 has almost no lead time.** Upbit posted most IS notices when the market opened, so IS has only 5
  events with a pre-open window.

## Pitfalls met
- **Notice titles get edited.** Postponement suffixes ("거래지원 개시 시점 연기 안내") are appended later, and the body
  shows both the old and the new times. The actual first 1m KRW candle settles L; it is always stated + 5 min.
- **Bodies come in three layouts:** prose (2020-21), market lines (2021-24), an HTML table (2024-04+). The title's
  market list is per notice, not per coin: "(KRW, BTC, USDT 마켓)" covered a BTC-only BIGTIME in 2024-04.
- **Body text needs cleaning.** Non-breaking spaces (\xa0) in 2020 bodies broke the regex, and a guard against price
  lines dropped tickers that start with a digit (1INCH). Both were fixed before any price request.
- **Missing notices.** Two 2020 KRW opens (VET, SRM) have only an event notice in the list. VET is kept, flagged
  src=event; SRM is dropped.
- **Delisted KRW markets return 404 on the candle API** (SRM, MATIC, STG, BONK), so the fallbacks above were needed.
- **The 1.5 s gap still drew two 429s** on api-manager; the back-off handled them.

## What a user decision could unlock
- **A seconds-level test.** This needs Binance aggTrades around each notice (data.binance.vision daily aggTrades files
  for the perp, <= 2024-12), and a notice-capture latency budget. It would measure how much of the jump a bot that
  polls api-manager.upbit.com every ~1 s could catch.
  - This is an HFT race against established Upbit-notice bots.
  - The seconds of `first_listed_at` may also lag the push notification.
  - **Low P(LIVE).** n is unchanged (power ceiling as above), the per-event SR would have to be ≥ 0.68 after a
    seconds-level fill and slippage on a +15 % candle, and the competition is fierce.
- **No change to K2.** The notice-built event list gives the coordinator a survivorship-free K2 event source for
  HOLD: delisted and renamed coins such as MATIC are visible in the notices.

## Files
- **Code (A/code/):**
  - scan.py: listing titles.
  - fetch.py: polite fetcher, a W copy.
  - pull_detail.py: bodies.
  - events.py: per-coin KRW markets, stated start, perp filter.
  - perps.py: a W copy.
  - pull_first.py: first KRW 1m candle.
  - k2rule.py: a K copy; only the log folder changed.
  - run.py: cells, random draws, descriptive split, chain.
  - summarize.py
  - split.py: notice-minute split.
- **Outputs (A/):**
  - HYPOTHESES_A.md
  - listing_titles.json, notice_events.csv, notice_events_L.csv
  - run_log.txt, results.txt, cells.json, trades.csv, split_output.txt
- **Data (research/data/upbit_announce/):**
  - raw/detail (78 bodies), raw/detail_event (2), raw/up1m (candle pages)
  - cache/ (px.pkl, win.pkl 18 MB, rows.pkl)
  - requests.log
