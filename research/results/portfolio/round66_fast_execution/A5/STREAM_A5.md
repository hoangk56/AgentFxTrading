# Stream A5 (round 66): Upbit KRW-listing notice -> Binance perp listed 1-7 days before N. None (0 events)

Written Sun Nov  1 14:50:10 UTC 2026 (from `date -u`). The rule, screen, costs and power were
declared in [HYPOTHESES_A5.md](HYPOTHESES_A5.md) before any price was loaded. HOLD (2025-01-01..) was never requested,
loaded or counted; no network request was made at all.

## Answer first
- **None.** Under the declared screen (stream A's parser, perp first trade in [N - 7 d, N - 1 d], still trading at
  N + 1 d, no perp >= 7 d by A's check) there are **0 IS and 0 VAL events** among the 83 KRW coin-notices of 2020-24.
  No bar can be tested. No PREREG_DRAFT. Power at the 2022-24 pace = 0 (0 events in 3 years -> ~0 in HOLD).
- **The premise is reversed.** Upbit does not list hot tokens days after Binance's perp. It lists them first, and
  Binance's perp follows hours later. Of the 2020-24 coin-notices with a Binance perp opening within 7 d of N:
  - 0 opened 1-7 d before N, 0 opened < 1 d before N;
  - 13 opened AFTER N: IS KAVA +5.1 d, SAND +4.0, NU +6.0; VAL VANA +0.22 d, ME +0.32, ZRO +0.35, MOVE +0.37,
    MOCA +0.40, DRIFT +0.42, SUI +0.62, APT +1.03, SAFE +1.25, SEI +2.7 (median +0.4 d in VAL).
  The remaining 46 had a perp >= 7 d old (A / A2's set) and 24 had no Binance perp near N.
- **The one "young" case is already in A2.** With minute precision, ARB's perp was 6.42 d old at N (first trade
  2023-03-23 15:01, N 2023-03-30 01:00:00). A's day-precision `perp_for` counted it as >= 7 d, so it is one of
  A2-D5L's 32 VAL events, not a disjoint A5 event. Its D5-L in A2: gross -4 bp, net -42 bp.
- **Young books are not wider here (one case).** At the D5-L entry second [N + 5, N + 6) s, ARB's effective-spread
  proxy (buyer-taker VWAP - seller-taker VWAP, over mid) was 6 bp and its 1 s range 37 bp, against VAL medians for A2's
  31 older perps of 21 bp and 212 bp. Calm (N - 10 min) both were ~0.8 bp. ARB was a top-tier launch with deep books,
  and its Upbit jump was small: path vs BTC since N - 60 s: 0 s -11 bp, +1 s +278, +2 s +409, +3 s +426, +5 s +370,
  +10 s +344, +30 s +179, +60 s +144, +300 s +210 (A2's VAL median at +5 s is +1,289). n = 1, info only.

## Events (A5/events_screen.txt, one line per coin-notice)
| outcome | IS 2020-21 | VAL 2022-24 |
|---|---|---|
| perp >= 7 d old by A's day check (A / A2 set; incl. GAL, SRM, VET-event) | 13 | 33 |
| **perp first trade in [N - 7 d, N - 1 d] (A5)** | **0** | **0** |
| perp first trade in (N - 1 d, N] | 0 | 0 |
| perp opened after N, within 7 d | 3 | 10 |
| no Binance perp near N | 17 | 7 (WEMIX, CTC, MNT, CARV none; T, AKT, UXLINK later) |

- All 83 launch times came from stream N0's k1m cache (first 1m kline with trades); none needed the day-precision
  fallback.
- **Completeness check of the notice set.** All 5,953 cached list rows were scanned for KRW / 원화 listing-type titles
  without a cached body: 28 found: 23 2020 "원화마켓 오픈 / 상장 기념 이벤트" notices (posted after the open, so
  not a notice time), 2 KRW-deposit site notices, 1 2022 MVL airdrop event and 2 2024 ENS / GAL deposit events (whose
  trade notices are cached). None adds an event.

## Results
| set | n | net bp | t | years | random % | power |
|---|---|---|---|---|---|---|
| IS (A5-D5L frozen) | 0 | - | - | - | - | - |
| VAL | 0 | - | - | - | - | 0 |
| info: ARB (already in A2) | 1 | -42 | - | 2023 | - | - |

Bars: IS t >= 2.0 / 2.5, VAL net > 0 / t >= 1.5, power >= 3: all untestable at n 0, so failed.

## Spread (A5/spread.txt; descriptive, from A2's npz read-only)
| group | entry-second spread proxy | entry-second 1 s range | trades in that second | calm spread | calm range |
|---|---|---|---|---|---|
| A2 IS, 12 perps (44-520 d old) | 8 bp | 50 bp | 280 | 0.8 | 0.7 |
| A2 VAL, 31 perps (50-1,495 d old) | 21 bp | 212 bp | 511 | 0.8 | 0.6 |
| ARB (6.4 d old) | 6 bp | 37 bp | 210 | 0.8 | 0.8 |

The proxy is noisy (it can be negative when the price falls within the second). The range is what A2's slippage model
uses: in the jump seconds the cost is set by the move, not by the book's age.

## What failed and why
- **Wrong premise, structural.** Binance's 2022-24 practice for hot new tokens is to open the perp a few hours after
  Upbit's KRW notice (pre-market or same-day launch), so "perp 1-7 d old at the Upbit notice" never occurs. In 2020-21
  the late Binance perps came 4-6 d after the notice. The event set is empty at both ends of the age window.
- **The day-precision perp check in A / A2 lets 6-7-day-old perps in.** It only affects ARB (6.42 d) in 2020-24. It is
  harmless for A2-D5L (the rule is about the notice, not the perp's age), but the registered rule's text says ">= 7 d";
  the coordinator may want to note that the code uses calendar days (first active day <= N - 7 d).

## What a user decision could unlock
- **The reversed case: Upbit notice first, Binance perp launch hours later** (10 VAL events, ~3 a year). The pump
  happens on other venues (Bybit / OKX perps or spot, Upbit itself) and Binance's perp opens into it. That is a
  launch-overshoot question (stream N0's rule, with the Upbit notice as a conditioning flag), or A4's Bybit route
  while Binance has no perp. It is a new rule and needs its own brief.

## Pitfalls met
- Stream A's events.py collides with A5's events.py on import: loaded by path under another name (as A3).
- Negative ages in the screen mean the perp opened after N; the screen's "< 1 d old" label covers those 7 cases.

## Files
- Code (A5/code/): events.py (screen), spread.py (descriptive spread and ARB path).
- A5/: HYPOTHESES_A5.md, STREAM_A5.md, events_screen.txt, spread.txt.
- Data (research/data/upbit_young_perp/): requests.log only (one line: no request made). No npz, no zips.
- Read-only inputs: research/data/perp_launch/k1m (N0, launch times only), research/data/upbit_latency/npz (A2),
  stream A's notice caches and parser, A2's trades.csv (ARB's D5-L row).
