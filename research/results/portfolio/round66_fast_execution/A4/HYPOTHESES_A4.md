# Stream A4 (round 66) hypotheses: Upbit KRW-listing notice -> Bybit USDT perp, coins without a Binance perp

Written Sun Nov 1 14:39:48 UTC 2026 (from `date -u`). At this point I have used only: stream A's notice bodies and
event code (read-only), the local Binance perp_1d spans (A's perps.py), the local Bybit instruments-info snapshots
(research/data/bybit_basis/, read-only), three robots.txt requests (public.bybit.com, api.bybit.com,
bybit-exchange.github.io: all 404 = no rules), 38 public.bybit.com directory listings (file names only) and 5 HEAD size
probes, all logged in research/data/upbit_bybit_notice/requests.log. **No trade, no candle and no price has been
downloaded; no return has been computed.** HOLD (2025-01-01..) is never requested, loaded or counted: only dump files
dated <= 2024-12-16 and funding with endTime <= 2024-12-31 23:59:59 UTC are requested; every N < 2025.

## Mechanism and side (fixed before data)
Same as A2-D5L: an Upbit KRW-listing notice sends Korean demand to the coin; arbitrageurs and global retail buy it on
the venues that already list it. When Binance futures has no perp, Bybit's USDT perpetual is the leveraged venue.
Side: **long the Bybit alt USDT perp, short Bybit BTCUSDT perp, equal notional.**

## Events (A4/code/events.py, probe.py; screen in A4/events_screen.txt, A4/probe.txt)
- Notices: stream A's parsing (`markets`, `start_time`, A/code/events.py loaded by path, not edited) of the cached
  KRW-titled bodies with first_listed_at in 2020-01-01..2024-12-31 UTC, plus A's 2020 이벤트 notices (as A3).
- Keep a coin if: KRW market in the body; not a stablecoin; **no Binance USDT-M perp >= 7 d old at N** (A's `perp_for`
  plus A3's "live on N's day" variant: disjoint from A / A2); **a Bybit USDT linear perp with launchTime <= N - 7 d,
  not delivered before N + 1 d** (instruments-info, trading + closed lists). Because launchTime is the latest launch,
  every screened coin's dump directory listing was checked: the first dump file is on launchTime's day or 1-7 days
  later for all 37 coins that have one, and no coin has an earlier Bybit life.
- **Screen result: 7 events, all VAL, 0 IS.** In 2020-21 Bybit had no USDT perp for any of the KRW coins without a
  Binance perp (the first ones, SAND / FLOW / STX, came in 2021-11).

| coin | N (UTC) | notice | Bybit perp since | stated start (UTC) |
|---|---|---|---|---|
| CTC | 2023-12-12 08:00:20 | 3920 | 2022-05-17 | 2023-12-12 09:00 |
| MNT | 2024-03-27 05:13:24 | 4133 (with POKT) | 2023-10-02 | 2024-03-27 10:00 |
| UXLINK | 2024-09-03 10:04:34 | 4477 | 2024-07-19 | 2024-09-03 13:00 |
| SAFE | 2024-10-24 06:32:30 | 4581 | 2024-04-29 | 2024-10-24 09:00 |
| DRIFT | 2024-11-08 05:44:59 | 4625 | 2024-05-21 | 2024-11-08 09:00 |
| ME | 2024-12-10 09:24:15 | 4713 | 2024-11-25 (pre-market perp; dumps from 11-26) | 2024-12-11 01:30 |
| MOCA | 2024-12-16 01:56:48 | 4723 | 2024-07-12 | 2024-12-16 05:00 |

- ME's Bybit perp was a pre-market perpetual until the token's TGE (around N). It stays in the main set as screened;
  "main without ME" is reported as a declared sensitivity line, not a selection.
- L = first Upbit KRW 1m candle (api.upbit.com/v1/candles/minutes/1, A3's walk from pull_L.py, own cache
  research/data/upbit_bybit_notice/up1m/; A's cache has none of these coins). If the market is delisted (404): stated
  start + 5 min (A's rule).

## Rule (frozen from A2-D5L; only the venue changes; code A4/code/analyze.py, trade / slip copied from A2)
- Entry: long alt at the price of the first Bybit alt trade with time >= N + 5 s; short BTCUSDT at the first Bybit
  BTCUSDT trade >= N + 5 s. Exit: each leg at its first trade with time >= L.
- Costs: **Bybit non-VIP derivatives taker 5.5 bp a side** (Bybit's fee table and its guide as of 2023-02-17 list VIP 0
  perpetual taker 0.055 %, maker 0.02 %; all 7 events are 2023-12..2024-12) = 22 bp per hedged trade, plus A2's
  slippage on each of the 4 fills (half the median 1 s range, (max - min) / min over 1 s bins with trades, in the 60 s
  from the fill), plus real Bybit funding at stamps in (entry, exit]: long alt pays its rate, short BTC receives
  BTC's (local research/data/bybit/funding, bybit_basis/funding; ME from the public v5 /market/funding/history,
  endTime <= 2024-12-31).
- Robustness as A2: costs x1.5, one step late (N + 10 s). Random benchmark as A2: same coin, same day, random seconds
  outside [N - 15 min, max(N + 30 min, L + 60 min)], same hold, 1,000 draw sets, percentile of the event gross mean.
- One cell only (no grid), so no max-over-cells null. t clustered by notice day (A2's `clt`). Also reported (info):
  unhedged long, and the alt's taker-buy notional in the 1 s / 5 s after N + 5 s (capacity, from the side field).
- Descriptive (as A2): path r(t) = ln(alt / alt_ref) - ln(BTC / BTC_ref), ref = last trade <= N - 60 s, at A2's
  offsets -60..+300 s; onset (a) = first alt trade in N +- 300 s with r >= +2 %; time to 50 % / 90 % of r(N + 60 s).

## Data (pulled after this file)
- public.bybit.com/trading/<SYM>/<SYM><YYYY-MM-DD>.csv.gz for the 7 alts and BTCUSDT on the 7 event days (14 files,
  ~0.8 GB by HEAD), >= 0.5 s between requests, streamed to research/data/upbit_bybit_notice/tmp/, parsed with
  `python -I`, deleted. The timestamp unit and the side field are checked on the first file before use. Kept (npz/):
  trades in [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min] (L is on the same UTC day for all but ME, whose
  stated start is the next day: ME's L-day file is pulled too), plus a 1 s last-price / count series of the N day.

## Bars and power arithmetic (before any return)
- **IS has 0 events, so the rule cannot pass any bar:** LIVE needs IS t >= 2.5 and DEMO IS t >= 2.0, both undefined at
  n = 0 (parameters cannot be "picked on IS"). **The verdict is "none" whatever VAL shows**; VAL is reported as
  description only, as A3 did for its IS-only set.
- VAL: 7 events on 7 days (2023: 1, 2024: 6; 2022: 0). t >= 1.5 would need SR ~ 0.57.
- HOLD pace (2022-24, as the brief asks): 7 events / 3 years = 2.3 / yr -> n_HOLD ~ 4.3 over the 22 HOLD months.
  Power = SR x sqrt(4.3) >= 3 needs **SR >= 1.45 per trade**. (At the 2024 pace alone, 6 / yr -> ~11, SR >= 0.90.)
  A2-D5L's VAL SR was 0.31, so power here would be ~0.6 (2022-24 pace) to ~1.0 (2024 pace).
- Prior: A2 found the Binance perp jump half done 1.2 s after N in VAL. Bybit-only coins are smaller and Bybit is the
  main leveraged venue for them, so the jump may be as fast, and the residual after 5 s may be like A2's (+520 bp mean,
  +182 median, fat right tail).
