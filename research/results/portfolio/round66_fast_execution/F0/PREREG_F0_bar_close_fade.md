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

## Forward runner (written 2026-11-02)
- File: `research/results/portfolio/round66_fast_execution/F0/coord/forward/fwd_f0.py` (`python -I fwd_f0.py pull |
  progress | check | eval`). Data: `research/data/f0_forward/` (request logs `requests.log` for data.binance.vision
  1m klines, `requests_net.log` for aggTrades and fapi; REST fills in `fills.csv`).
- Hashes (`python -m research.tools.prereg_hashes`, 2026-11-02 06:40 UTC):
  - `research/results/portfolio/round66_fast_execution/F0/coord/forward/fwd_f0.py` 4d603298cde843d0
  - `research/results/portfolio/round64_parallel/F/coord/hold/hold_pull.py` f5f8c60987059ed1 (executed, not in the
    list above; pinned too)
- Reuse, no logic copied into the runner: `rule.trades` (events + F's costs) and `rule.load_sym / px_at / fund /
  funding_hours`; F0 `pull.jobs_for / fetch` + `net.open_url` (aggTrades windows, streaming, pacing); F0 `analyze.
  first_at / vwap_at / spread_w / clt` (entry, $10k fills, spread, day-clustered t). `hold_univ.py` and `hold_pull.py`
  run at import, so the runner executes their hashed source with literal replacements only: perp_1d / output / exinfo
  folders -> `data/f0_forward`, `END` / `END_MIN` -> the data end, pull-list start 2025-01-01 -> 2026-10-30
  (`research/tests/test_f0_forward.py` checks that only string folder and integer date literals change). Module
  folders redirected: `net.DATA`, `net.LOG`, `pull.NPZ`, `rule.FUND_DIRS`.
- Beyond folders / dates (plumbing, not rule logic): (1) `events_only`, a return-free copy of the selection lines of
  `rule.trades` (same guard, de-duplication and exit-availability drop, no price ratio of the trade), used only by
  `progress` and the eval date gate so the event count can be read blind; `eval` itself grades `rule.trades` and refuses
  if the two event sets differ. (2) Fetchers for fapi exchangeInfo (fresh each pull, for F's non-COIN filter), 1d klines
  (perp_1d rows < 2026-10-30 from `research/data/binance/perp_1d`, later complete days from fapi), fundingRate, and fapi
  REST fills for daily files data.binance.vision still lacks 2 days later (1m klines; aggTrades windows). (3) 1m files
  per (coin, day) for universe coins plus the day before / after (HOLD pulled whole months; the event set is the same
  as long as bars e-1..e+62 are present). (4) A manifest that re-streams an aggTrades day file when a later event needs
  a window the file lacks. (5) URL-quoting of non-ASCII symbols (e.g. 币安人生USDT). (6) With T0 = 2026-10-30 00:00 the
  first minute cannot be an event (no previous bar), as HOLD's last 62 minutes were not.
- `check` (graded periods only): `events_only` = the registered HOLD run's 2,080 trades (sym, minute) exactly; = F0's
  1,150 IS / VAL events exactly (`--full`); forward universe = HOLD universe on all 667 HOLD days; first-aggTrade entry
  prices at 0 / 1 s = F0's sample rows on 60 events.
- `eval` refuses (exit non-zero) unless: every hashed file matches, this runner's hash is in this file, this section's
  "Forward result" is empty, and today is past the first month end with >= 3 full calendar months and n >= 333 with data
  complete through it (earliest 2027-01-31), or the cap (2027-10-29). It appends its output below once.
- First `progress` (2026-11-02 06:40 UTC; data complete through 2026-10-31, the 2026-11-01 1m files were not yet on
  data.binance.vision): 13 events, 2 event days, 0 full months; pace ~198 / month -> n >= 333 projected 2026-12-21,
  so the projected evaluation is the 2027-01-31 month end. Two days only: the pace is not informative yet.

## Forward result
(appended at the evaluation date)
