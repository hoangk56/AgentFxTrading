# Stream A5 (round 66) hypotheses: Upbit KRW-listing notice -> Binance perp listed 1-7 days before N

Written Sun Nov  1 14:47:55 UTC 2026 (from `date -u`). At this point I have used only: stream A's notice bodies and
parser (read-only), the local perp_1d / relisted_candidates files, and the first 1m kline time of each perp from stream
N0's cache research/data/perp_launch/k1m (read-only, used only for the launch time, not for prices). **No aggTrade, no
Upbit candle and no price has been downloaded; no return has been computed. No network request has been made.**
HOLD (2025-01-01..) is never requested, loaded or counted: every N < 2025.

## Mechanism and side (fixed by the brief, before data)
As A2-D5L: an Upbit KRW listing notice sends Korean demand to the coin; bots and global retail buy it on the venues
that already list it. The premise of A5: Upbit often lists hot new tokens a few days after Binance, so their Binance
perp is 1-7 d old at N. Side: **long the alt USDT-M perp, short BTCUSDT perp, equal notional.**

## Events (code A5/code/events.py; full screen in A5/events_screen.txt)
- Notices: stream A's `markets` / `start_time` (A/code/events.py loaded by path, not edited) on every cached KRW
  notice body with first_listed_at in 2020-01-01..2024-12-31 UTC (research/data/upbit_announce/raw/detail,
  research/data/upbit_notices/raw/detail), plus A's declared secondary source (detail_event, 2020). 83 KRW coin-notices.
- Keep a coin if: KRW market; not a stablecoin; **no** perp that A's `perp_for` counts as >= 7 d old (incl. A3's
  "live on N's day" variant), so the set is disjoint from A / A2; a Binance USDT-M perp (`<C>USDT` or `1000<C>USDT`,
  incl. relisted lives) whose **first trade is in [N - 7 d, N - 1 d]** (first 1m kline with trades, k1m cache; day
  precision from perp_1d if absent: never needed, all 83 resolved from k1m); and it still trades at N + 1 d.
- **Result of the screen: 0 events (IS 0, VAL 0).**

| outcome | IS 2020-21 | VAL 2022-24 |
|---|---|---|
| perp >= 7 d old by A's day-precision check (A / A2's set) | 13 | 33 |
| perp first trade in [N - 7 d, N - 1 d] (A5) | 0 | 0 |
| perp first trade in (N - 1 d, N] | 0 | 0 |
| **perp launched AFTER N** (within 7 d) | 3: KAVA +5.1 d, SAND +4.0 d, NU +6.0 d | **10**: VANA +0.22 d, ME +0.32, ZRO +0.35, MOVE +0.37, MOCA +0.40, DRIFT +0.42, SUI +0.62, APT +1.03, SAFE +1.25, SEI +2.7 |
| no Binance perp near N (none ever, or launched > 7 d after N) | 17 | 7: WEMIX, CTC, MNT, CARV (none); T, AKT, UXLINK (later) |

(The last two rows are the screen's 30 "no perp in N - 8 d .. N" lines plus its 7 "< 1 d old" lines, whose negative
ages mean the perp opened after N. IS 13 + 0 + 0 + 3 + 17 = 33, VAL 33 + 0 + 0 + 10 + 7 = 50 coin-notices. Corrected at
~14:50 UTC, before any price was loaded: this row's VAL count and the ARB launch time below.)
- **The premise is reversed in the data.** Since 2022 Binance launches the perp of a hot token hours *after* Upbit's
  notice (median ~0.4 d), not days before. No 2020-24 KRW notice hit a Binance perp aged 1-7 d.
- **One overlap with A2, info only.** With minute precision, ARB's perp (first trade 2023-03-23 15:01 UTC, 6.42 d before
  N = 2023-03-30 01:00:00) is younger than 7 d, but A's day-precision `perp_for` counted it
  as >= 7 d, so it is one of A2's 32 VAL events. It is not a disjoint A5 event. GAL (2024-07-11) is the A3 case
  (perp stops the next day) and stays out.

## Rule (frozen from A2-D5L, copy of A2/code/analyze.py `trade` / `slip`; would be applied unchanged)
- Entry: each leg at its first aggTrade >= N + 5 s; exit: each leg at its first aggTrade >= L (first Upbit KRW 1m
  candle as stream A, fallbacks as A / A3).
- Costs: 20 bp (4 taker fills x 5 bp) + A2's slippage on each fill (half the median 1 s range over 60 s from the fill)
  + real funding (young perps: research/data/binance/funding_window). Robustness: costs x1.5, one step late (N + 10 s).
  Random: A2's same-coin same-day draws. t clustered by notice day. One cell, no grid.
- **With 0 IS and 0 VAL events, no bar can be tested and the verdict is "none"**, declared now, before any price.

## Descriptive, info only (declared now; never a verdict)
- ARB 2023-03-30 (the only young perp, already in A2): path r(t) at A2's offsets and the first-second spread, read
  from A2's research/data/upbit_latency/npz (read-only; no download).
- **First-second spread** (declared definition): in the 1 s bin [N + 5 s, N + 6 s), effective spread proxy =
  (VWAP of buyer-taker prints - VWAP of seller-taker prints) / mid, and A2's 1 s range (max - min) / min; compared
  with the same two numbers at N - 10 min .. N - 9 min (calm) and with the median over A2's other 43 events
  (old perps), to answer "are young books wide?" on the one case available.

## Power (2022-24 pace, before any return)
- 2022-24 pace of disjoint A5 events: 0 in 3 years, so the expected HOLD count over 22 months is ~0 (at most ~1 if
  the minute-precision ARB-type case is counted, and that one is already in A2's registered rule).
- Power = SR x sqrt(n_HOLD) = 0 for any SR. LIVE (>= 3) and even a forward test are out of reach.

## Data plan
- No aggTrade download is needed (0 events). research/data/upbit_young_perp/requests.log records that no request
  was made. If the coordinator wants the reversed case (Upbit notice before the Binance perp launch), that is a
  different rule (the perp opens after the pump starts elsewhere): stream N0's launch data or A4's Bybit route.
