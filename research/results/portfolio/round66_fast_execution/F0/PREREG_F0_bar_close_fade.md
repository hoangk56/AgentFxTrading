# PREREG F0: fade 5 % idiosyncratic 1-minute wicks, entered at the first trade after the event bar's close (FORWARD test, LIVE candidate)

Registered 2026-11-01 13:48 UTC (from `date -u`) by the coordinator. Draft, tables and caveats:
[PREREG_DRAFT_F0_bar_close_fade.md](PREREG_DRAFT_F0_bar_close_fade.md) (stream F0, 13:47 UTC); hypotheses
[HYPOTHESES_F0.md](HYPOTHESES_F0.md) (12:24 UTC); report [STREAM_F0.md](STREAM_F0.md).

**Test window: FORWARD only, from 2026-10-30 00:00 UTC.** F's HOLD (2025-01-01..2026-10-29) is known for the next-bar
entry (F failed it: +41.8 bp, t 1.17), so this F-family rule is never graded on that period. No forward data has been
read for this rule at registration.

## Rule (frozen, as the draft: cell "E0 H60" in its tradable form)
F's universe and events unchanged (round64_parallel/F/PREREG_F_wick_fade.md "Rule"; universe built as F's HOLD run did,
`F/coord/hold/hold_univ.py`: all perps, EXCL_BASE, non-COIN underlyings dropped). Entry at the price of the first
aggTrade with time >= the close of the event bar (= open time of bar e+1); exit at the close of bar e+61; long after a
crash, short after a spike; funding at real stamps; costs 22 / 30 bp round trip (F's model).

## IS / VAL (stream F0)
IS n 380, +319.5 bp, t 4.90, S 0.249; VAL n 768, +339.2 bp, t 4.56, S 0.207; 5 / 5 years; x1.5, 5h spread, +1 s,
+3 s and $10k taker-VWAP fills all positive (VAL +326 to +344). All LIVE bars on IS / VAL pass. Measured first-second
half-spread median 11 bp (IS) / 7 bp (VAL). The F entry one bar later on the same events: +273 / +271.

## Forward size and timing
- Power 3 at VAL size: 333 events (day-clustered). At F's HOLD pace (94.5 events / month) ~3.5 months.
- Evaluate once, at the first month end with n >= 333 and >= 3 full months of data; hard cap 2027-10-29.
- Expectation warning: F's HOLD kept ~15 % of its VAL size at the next-bar entry; if F0 keeps a similar share the
  forward edge is ~+50-100 bp and 333 events will not detect it (power ~0.6-1.1). A fail then reads "not detectable".

## Forward implementation (declared now; runner written by the coordinator before the first evaluation)
data.binance.vision USDT-M daily 1m klines and daily aggTrades from 2026-10-30, 1d klines for the universe, fapi
fundingRate; missing daily files from fapi REST (logged). Code paths: F's rule.py / hold_univ.py for events, F0's
ev.py / analyze.py entry logic. The runner may only change data folders and date constants; it is hashed before the
evaluation and the hashes are appended here.

## Pass bar (all of; run once) = F's HOLD bars
1. Net mean > 0 and day-clustered t >= 2.0.
2. Net > 0 at costs x1.5, at the 1 s-late entry, and with $10k same-side taker VWAP fills.
3. Each half of the forward window (by event count) net > 0.
Pass = LIVE candidate; the user decides on a bot (the strategy needs a bot reacting at the 1m bar close via websocket).
Fail = dropped; no re-registration of E1, E3, H15 or crash-only on the same forward data.

## Hashes (`python -m research.tools.prereg_hashes`, 13:48 UTC)
- `research/results/portfolio/round66_fast_execution/F0/code/ev.py` d3fbda578aac36fe
- `research/results/portfolio/round66_fast_execution/F0/code/pull.py` 75107157fb6ba0cd
- `research/results/portfolio/round66_fast_execution/F0/code/analyze.py` 934ef60959f3f457
- `research/results/portfolio/round66_fast_execution/F0/code/net.py` 40f1ecae7fd8b010
- `research/results/portfolio/round64_parallel/F/code/events.py` 81e007b5cd04adcb
- `research/results/portfolio/round64_parallel/F/code/report.py` 7e3b78d6ba5476c7
- `research/results/portfolio/round64_parallel/F/coord/hold/hold_univ.py` 84ca87404734aec6
- `research/results/portfolio/round64_parallel/F/coord/hold/rule.py` 3811202d28136b95

## Forward result
(appended at the evaluation date)
