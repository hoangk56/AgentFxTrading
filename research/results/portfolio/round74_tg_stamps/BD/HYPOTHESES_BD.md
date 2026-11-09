# Stream BD hypotheses: Binance delisting announcements timed by @binance_announcements

Written Mon Nov 2 14:23:27 UTC 2026 (from `date -u`), before any price was requested or looked at. No Telegram
title has been read yet either (the coordinator's pull of `binance_announcements` is still running). The regexes
below may get one amendment after reading pre-2025 **titles only** (to fix format misses), stamped with `date -u`
and still before any price.

## Mechanism (side fixed: SHORT the delisted coin)

A "Binance Will Delist X" notice removes the coin's largest spot venue in ~1-2 weeks. Holders sell before the
deposit / trading stop, market makers pull quotes, retail panics. The sell pressure should be strongest in the
first minutes after the notice (retail sees the post) and may continue over 24 h. Side: short. Never long.

## What is different from earlier rounds

- round64 T: convergence of a delisted **perp** to spot at T - 24 h before the perp's settlement (dates only, no
  notice times). BD trades the **notice time** (second stamps from Telegram), entry at post + 5 s, exits within 24 h:
  the reaction, not the settlement wedge. T's "forward paper log at the notice" idea is exactly what this tests on
  history.
- research/data/binance_delist/ holds 1m windows around perp settlement days, not around notices; not reused for
  returns (wrong window), only its event list as a cross-check of perp delistings.
- round63 D / 66 N0: listing notices and new-perp launches (long side, different mechanism).

## Data

- Events: @binance_announcements via the shared fetcher pages (coordinator's pull), parsed with
  `coord/parse.py` under `python -I`. Every post with time >= 2025-01-01 00:00:00 UTC is dropped right after parsing,
  before classification. 2025-26 posts enter only as a **count** of class-S/F/MT titles (no text printed, no prices).
- Edited posts (`edited` True): primary = dropped; sensitivity = kept. Report both.
- Prices: data.binance.vision futures/um daily aggTrades (alt + BTCUSDT) for the notice day and the next day;
  Bybit linear perp ticks from public.bybit.com/trading when no Binance perp exists; Binance spot daily aggTrades
  (information only, see below). Every request has end <= 2024-12-31 23:59:59 UTC; a notice on 2024-12-31 whose 24 h
  exit falls in 2025 gets the 24 h cell dropped (not extended).
- Funding: fapi fundingRate (Binance) / Bybit public funding history, only for stamps <= 2024-12-31.
- Optional cross-venue cells (separate, not in the Binance grid): @OKXAnnouncements, @Bybit_Announcements delisting
  posts, pulled with the shared pageback.py.

## Title classes (explicit regexes, case-insensitive, on the first line of the post text = title)

- Exclusion first (class X, not traded): `(?i)\b(swap|migration|rebrand|redenomination|token\s+split|rename)\b`.
- **F (perp delisting):** `(?i)(futures|perpetual|USDⓈ?-?M|USDS-M|COIN-M).*\b(delist|will\s+delist|close\s+and\s+delist|
  settle\s+and\s+delist)` or `(?i)\bdelist\b.*\bperpetual\b`.
- **M (margin only):** `(?i)\bmargin\b.*\bdelist` (not traded: no reason the coin itself sells; counted only).
- **P (pair removal only):** `(?i)(remov\w*|delist\w*).*\btrading\s+pairs?\b` with no "Will Delist <TICKER>" form, or
  pair notation `[A-Z0-9]+/[A-Z0-9]+` only (coin stays listed: not traded, counted only).
- Other non-spot products excluded: `(?i)(leveraged\s+tokens?|BLVT|options|earn|savings|loans?|convert|isolated)`.
- **S (spot delisting of the coin):** `(?i)\b(will\s+delist|to\s+delist|delisting\s+of|will\s+be\s+delisted|
  delists?)\b` not matched by F / M / P / X / other above.
- **MT (monitoring tag):** `(?i)monitoring\s+tag` (exists from 2023 only: VAL-only by construction, at most a
  new-era / forward note; it cannot be a LIVE or DEMO cell since it has no IS).
- Coins: tickers parsed from the title after "Delist" (split on `,`, `&`, `and`), `[A-Z0-9]{2,12}`; if the title has
  none, from the body's "(TICKER)" groups. One trade per coin; t clustered by notice day.

## Instrument per coin

Binance USDT-M perp `<COIN>USDT` (or `1000<COIN>USDT`) if its daily aggTrades file exists for the notice day; else
Bybit linear `<COIN>USDT` if public.bybit.com/trading has that day; else no trade (counted as "no perp"). Class F
always trades the perp being delisted (Binance).

## Rule and grid (6 graded cells)

- Entry: SHORT at the worst price of the 1 s after the first trade at or after post time N + 5 s (A2's F2 fill).
- Exit: buy back at the worst price of the 1 s after the first trade at or after N + {5 min, 60 min, 24 h}.
- Classes {S, F} x exits {5m, 60m, 24h} = 6 cells; IS / VAL. MT x 3 exits = VAL-only info cells.
- Unhedged primary. Sensitivity (not a cell): BTCUSDT-perp hedged (long BTC, equal notional, its own costs).
- One step late: N + 10 s entry. Costs x 1.5.
- Costs: Binance taker 5 bp a side; Bybit taker 5.5 bp a side (VIP0 retail derivatives); both + worst-of-1 s fill.
  Funding counted for the 24 h exit (short receives positive funding).
- Eras: IS 2020-01-01..2021-12-31 (no USDT-M perps before 2019-09, so 2018-19 cannot add perp trades; declared
  IS stays 2020-21). VAL 2022-01-01..2024-12-31. HOLD closed.
- Info only (not graded): Binance spot path of class-S coins 2018-2024 (the spot itself; long-only venue, so not
  tradeable short) to measure the reaction and the burst timing over a larger sample.

## Burst timing

Per event: r(t) = ln p(N + t) - ln p(N - 60 s) at t in {-600, -60, -10, -5, 0, 2, 5, 10, 30, 60, 300, 3600} s.
Share of the move before N + 5 s = r(5 s) / r(300 s) (median over events with r(300 s) < 0), plus onset time
(first trade with r <= -2 %).

## Random benchmarks

(a) same coins, same notice day, random seconds outside [N - 15 min, N + exit + 15 min], same hold, same cost model
(1,000 draw sets) -> percentile of the event mean; max-over-6-cells t null (95th pct).
(b) same coins at random other Binance announcement post times (non-delisting posts) within +-30 days, same hold.

## Bars

As BRIEF (unchanged). A cell needs n >= 5 IS trades to be graded. Pass -> PREREG_DRAFT_BD_<name>.md and stop.

## Power arithmetic

Filled in below from the title counts, before any price (amendment stamped with `date -u`).

## Amendment 1 (Mon Nov 2 14:56:42 UTC 2026, `date -u`; titles only, still before any event price)

Read pre-2025 titles only (2025-26: class counts only). Format fixes, no change to the rule or the grid:
- Ticker extraction is case-insensitive on "Delist" (titles say "Will Delist BTS, PERL, ..."); MT coins are the
  tickers after "Include" up to "and Remove" / "on"; F coins are all ticker-like words of the title.
- F regex also matches `delist ... futures` ("Binance Will Delist FTT Margin Pairs, USDⓈ-M Futures Contracts ...").
- Non-spot products also excluded: `staking`, `p2p`, `flexible loan` ("Binance Staking to Delist ..." is not a spot
  delisting).
- Stablecoins / fiat tokens never traded (no sell-off mechanism): BUSD, TUSD, USDC, USDP, PAX, USDS, IDRT, BIDR, BKRW,
  EUR, GBP, AUD, NGN, RUB, TRY, UAH, BRL, ZAR, DAI, FDUSD, AEUR, EURI, BVND, VAI, UST, USTC, SUSD.
- "Notice of Removal of Trading Pairs" (2019-21, pair-only) is class "-" / P: not traded.
- Random (b) uses non-delisting post times inside the loaded two days (same coin), not +-30 days: that would need
  ~60 more tick days per coin.

## Power arithmetic (counts from titles; 2025-26 as counts only)

Class-S posts / coins (edited posts dropped): 2018 2 / 5, 2019 2 / 6, 2020 8 / 9, 2021 7 / 15, 2022 7 / 25,
2023 6 / 16, 2024 8 / 25. Class F posts: 2021 1 (DOTECO index, edited), 2022 4 (LUNA x2, ANC, FTT), 2023 1 (BUSD,
stable: no coin). MT posts: 2023 2, 2024 4. HOLD 2025-26: S 21 posts, MT 22, M 10 (counts only).

- IS 2020-21: 24 S coins, but these are mostly 2017-era small caps (ARN, FUEL, LUN, INS, MCO, POE, TNT, AE, HC,
  BCPT, CMT, TNB, VIBE, OST, RCN, WPR, SNGLS, VIA, COVER, PPT, SWRV, DLT, GVT, SKY, POA, APPC, EVX, RDN); a Binance
  USDT-M or Bybit perp is unlikely for almost all. **Expected IS trades with a perp: 0-3, below the n >= 5 gate.**
  F in IS: 0 usable (DOTECO is an index contract). So **no cell can reach the LIVE / DEMO IS bar by construction**;
  this is known before prices. The run still measures VAL (2022-24, ~66 S coins, perp share to be counted) and the
  spot path 2018-24 as information and a new-era / forward note.
- HOLD size if VAL's perp share is p: ~21 posts x ~3 coins x p (e.g. p 0.5 -> ~30 trades). Power 3 then needs a
  net Sharpe per trade >= 3 / sqrt(30) ~ 0.55.
