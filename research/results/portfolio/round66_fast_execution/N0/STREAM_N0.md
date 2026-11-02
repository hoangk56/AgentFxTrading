# Round 66 stream N0: fade the first-minutes move of a new Binance USDT-M perp, result

Written 2026-11-01 14:34 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_N0.md](HYPOTHESES_N0.md), 14:21 UTC, before any download or return. No change after it.
- Code: `code/` (events.py listing list, pull_agg.py launch-day aggTrades streamer, pull_k1m.py monthly 1m klines,
  analyze.py cells / costs / random benchmark). Outputs: `out/report.txt` (every number below), `out/cells.json`,
  `out/trades.csv` (per-event path, move, net).
- No file dated 2025 or later was requested or loaded. HOLD not opened.

## Answer: none. Fading the launch move loses in IS in 7 of 8 cells; no cell passes LIVE or DEMO

The launch overshoot that the brief suspected is not there. In the first hour the median new perp barely moves from
its first trade (IS +1.1 %, VAL -0.6 % at +60 min), and when the first 1 or 5 minutes do move >= 5 %, the move goes on
slightly more often than it reverses, mostly after a drop. The best IS cell (OLD-k1-X10, 4 trades) has t 0.31.

| cell (group-k-X) | era | n (days) | gross | half-spread e / x | net bp | t (day) | median | SR / trade | x1.5 | late +60 s | real $10k | years | random % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NEW-k1-X5 | IS | 16 (15) | -194 | 14 / 9 | **-237** | -1.50 | -110 | -0.37 | -260 | -224 | -233 | 2020 -280, 2021 -109 | 3.8 | |
| | VAL | 33 (27) | -120 | 9 / 4 | **-154** | -1.23 | -290 | -0.20 | -172 | -179 | -132 | -1637 (1), -93, -115 | 0.1 | -0.89 |
| NEW-k1-X10 | IS | 5 (4) | -282 | 29 / 7 | -355 | -0.97 | -221 | -0.44 | | | | -100, -737 | 1.5 | |
| | VAL | 7 (6) | -138 | 12 / 4 | -174 | -0.49 | -290 | -0.19 | | | | 2023 -1605 (1), 2024 +64 | 4.1 | -0.39 |
| NEW-k5-X5 | IS | 15 (14) | -50 | 13 / 9 | -93 | -0.65 | +42 | -0.17 | -115 | -69 | -82 | -172, +127 | 7.2 | |
| | VAL | 39 (30) | +18 | 5 / 4 | -14 | -0.13 | -19 | -0.02 | -29 | +18 | +3 | -309 (1), +90, -56 | 13.4 | -0.10 |
| NEW-k5-X10 | IS | 6 (5) | -201 | 27 / 8 | -255 | -1.10 | -241 | -0.46 | | | | -201, -364 | 5.4 | |
| | VAL | 10 (8) | +76 | 4 / 4 | +45 | 0.19 | +18 | 0.06 | +31 | +81 | +58 | 2023 -635, 2024 +215 | 1.5 | 0.14 |
| OLD-k1-X5 | IS | 19 (19) | -44 | 18 / 8 | -92 | -1.12 | -90 | -0.26 | -116 | -114 | -116 | +148, -267 | 4.1 | |
| | VAL | 19 (19) | +115 | 10 / 3 | +79 | 0.82 | +80 | 0.19 | +62 | +15 | +86 | +74, +18, +168 | 74.5 | 0.64 |
| OLD-k1-X10 | IS | 4 (4) | +89 | 8 / 3 | +53 | **0.31** | +195 | 0.15 | +37 | +2 | +1 | +266, -160 | 53.5 | |
| | VAL | 4 (4) | +209 | 10 / 5 | +170 | 0.68 | +26 | 0.34 | +151 | +251 | +189 | 2023 +314, 2024 +26 | 84.5 | 0.53 |
| OLD-k5-X5 | IS | 22 (22) | -102 | 10 / 8 | -144 | -2.00 | -133 | -0.43 | -164 | -112 | -137 | -74, -202 | 0.1 | |
| | VAL | 20 (20) | +43 | 7 / 3 | +10 | 0.09 | +101 | 0.02 | -6 | +1 | +16 | -97 (1), +19, +9 | 33.4 | 0.07 |
| OLD-k5-X10 | IS | 5 (5) | -49 | 2 / 8 | -85 | -0.73 | -64 | -0.33 | | | | -128, -20 | 4.0 | |
| | VAL | 6 (6) | +178 | 10 / 5 | +139 | 0.73 | +146 | 0.30 | +120 | +165 | +152 | 2023 +274, 2024 +4 | 69.2 | 0.57 |

- Costs: fees 22 bp round trip (alt 2 x 5, BTC 2 x 5 + 2 x 1 bp spread) + the alt half-spread measured at the entry
  and exit second + real funding (cell means -15 .. +2 bp). Every IS cell is negative already gross except
  OLD-k1-X10 (n 4).
- Bars: no cell has IS t >= 2.0 (DEMO) or >= 2.5 (LIVE); 7 / 8 cells have IS net < 0. VAL net > 0 in 4 cells (OLD k1/k5
  and NEW-k5-X10), all t < 1. Random: no IS cell beats 90 %. Power at VAL size (VAL n / 3 yr x 1.83 HOLD years):
  <= 0.64, against 3.
- Max-over-8-cells null (random draws minus each event's own cost): IS real max t 0.31 vs null median 1.95 / p95 4.07;
  VAL 0.82 vs 2.20 / 4.30. The events are below the random benchmark, not above it.
- Pooled (reading only, not graded): ALL-k1-X5 IS n 35 net -158 (t -1.93), VAL n 52 -69 (t -0.79); ALL-k5-X5 IS n 37
  -123 (t -1.86), VAL n 59 -6.

## The first hour of a new perp (median ln(P / P0), P0 = first trade; bp; IS n 127, VAL n 249)

| after T0 | 5 s | 30 s | 1 min | 2 min | 5 min | 10 min | 15 min | 30 min | 60 min | 120 min |
|---|---|---|---|---|---|---|---|---|---|---|
| IS all | 0 | 0 | +8 | +18 | +37 | +41 | +48 | +61 | +109 | +32 |
| IS NEW (39) | +53 | -9 | +93 | +71 | +71 | +28 | +37 | +65 | +113 | +22 |
| IS OLD (88) | 0 | 0 | +4 | +13 | +29 | +43 | +59 | +45 | +77 | +33 |
| VAL all | 0 | -14 | +8 | +15 | -25 | -1 | +3 | -30 | -58 | -65 |
| VAL NEW (138) | -17 | -6 | +8 | +13 | +19 | +1 | -37 | -28 | -92 | -66 |
| VAL OLD (111) | 0 | -25 | -21 | +15 | -35 | -2 | +42 | -30 | -34 | -39 |

- Dispersion is large: IS q25 / q75 at 60 min -202 / +526 bp; mean |move| 3.7 % at 1 min, 5.4 % at 60 min (IS); VAL
  4.3 % / 6.8 %. Median |m1| 2.1 %, |m5| 2.4-2.5 %.
- Share with |m| >= 5 %: NEW 24-41 %, OLD 17-25 %; >= 10 %: 4-15 %. So X10 cells hold 4-10 trades.
- First-second half-spread after T0: median 43 bp IS / 27 bp VAL (mean 156 / 71). By k = 1 or 5 min it is already
  ~5-10 bp median at our entry (cell means 4-29 bp): the book fills within a minute, so cost is not what kills this.
- Launch clock: 07:00 UTC (51), 12:30 (32), 03:30 (30), 12:00 (28) ... ; the first trade comes in the first 5 s of the
  minute in only 29 % of launches (median 330 trades in the first minute).
- Side-signed path after the entry (pooled k1-X5, IS): median -29 / mean -107 bp at the exit; there is no settling
  in seconds either (+1 s 0, +5 s -15, +60 s -7). Fading drops is the worst part: NEW down-moves -602 (IS, 4) /
  -187 bp (VAL, 16).

## Why it failed
- Launch moves on Binance perps are not an overshoot in an empty book: the median path is flat, the spread normalises
  within the first minute, and big early moves carry information (continuation by the hour, worst after drops of NEW
  tokens: airdrop / unlock selling keeps going, consistent with round 60's monthly drift).
- Post-hoc only (not registrable; the side was fixed before data): the opposite (momentum) side earns about the
  negative of the fade gross minus costs: IS ALL-k1-X5 ~ +113 - 46 = +67 bp, but VAL +34 gross - 35 cost -> ~ -1 bp.
  It would not pass VAL either.

## Random benchmark notes
- Pool: same coin, days 2-30 after launch, same-sign 1m-kline k-minute move >= X, fade to u + 60 min, BTC-hedged gross;
  1,000 draw sets. Many pools were small (< 5 moves -> the 10 largest same-sign moves): k1-X5 80 events, k1-X10 19,
  k5-X5 22, k5-X10 20 (of the cell-event slots).
- The random fades earn +22 .. +531 bp gross. Part of that is the 1m close bounce (close = last trade at bid or ask,
  entry and exit both at closes), so the benchmark is biased up against the event (aggTrade entries). This makes the
  random % strict, but the event cells fail on their own (negative IS net) regardless.

## Data and pull
- research/data/perp_launch/agg/<SYM>_<day>.npz: 376 launch-day files (all events, no subsample), rows T0 .. T0 + 2 h
  (next day's file when T0 + 2 h crossed midnight), 109 MB. Zips deflate-decoded on the fly, never written.
- research/data/perp_launch/k1m/<SYM>.npz: monthly futures 1m klines for 376 alts (launch day .. + 31 d, cut < 2025)
  and BTCUSDT 2020-01..2024-12, 246 MB.
- requests.log 1,163 lines: robots.txt 404 (no rules), 1,161 GETs at 200, 0 x 403 / 418 / 429 / 503, no 2025 URL.
  Pull time: aggTrades 3.2 min, klines 10.6 min (both inside the 45 min guideline). Web searches: 0.

## Pitfalls
- BTC hedge priced at the open of the 1m BTC bar containing the fill: launches are on the minute but the first trade
  often comes later in the minute (71 %), so the hedge price can be up to ~60 s stale. BTC 1m noise (~10-20 bp) is
  small next to these alt moves (sd ~ 6 %); it adds noise, not bias.
- "Real $10k" fills leave out events with no aggressor-side trade within 60 s of a fill (nanmean); a few OLD IS
  events in 2020 had none (thin books).
- Cells are tiny (4-39 trades); even a real per-trade Sharpe of 0.3 could not reach power 3 (needs ~0.5 at ~38 HOLD
  trades), as stated in the hypotheses.

## What a user decision could unlock
Nothing in this family on Binance perps: neither the fade nor (post-hoc) the momentum side survives VAL. The only
untested variant with a mechanism is the pre-market / notice side (the listing announcement, hours before T0), which
streams A / A2 cover for Upbit; a Binance-listing-announcement test would need Binance announcement times to the
second (research/data/binance_announcements exists from another round; not checked here, out of scope).
