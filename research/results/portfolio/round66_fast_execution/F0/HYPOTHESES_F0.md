# Round 66 stream F0: wick fade entered at the event bar's close (or 1 / 3 s later), hypotheses

Written 2026-11-01 12:24 UTC (from `date -u`), before any F0 return was computed. At this time I had read the brief,
F's HYPOTHESES / STREAM / PREREG rule section (not its HOLD result), events.py, report.py and round 62's aggTrades
notes; built the event list (no returns) and sent 1 robots.txt GET (404) and 4 HEAD probes for file sizes.
Already public before this file (from STREAM_F.md): F's open-of-e+1 entry ("go", information) on T5 idio H60 gave IS
+317 / VAL +334 bp net. That is the E0-H60 cell below at F's cost, so E0-H60 is not a fresh test on IS / VAL; the
fresh parts are the 1 s / 3 s entries, the H15 rows at go and the measured spread / slippage.

**HOLD rule:** F's HOLD (2025-01..2026-10-29) is known for the next-bar entry, so nothing here is graded on it. No
2025-26 file is requested or loaded (daily aggTrades only for 2020-2024 event days; everything cut at < 2025-01-01).
A passing cell is registered as a FORWARD test from 2026-10-30 00:00 UTC.

## Mechanism and side (fixed: F's)
Liquidation / stop cascades on thin altcoin perps overshoot; liquidity providers who step in after the cascade earn
the overshoot. Rounds 64-65 suggest the reversal is now taken earlier (F's HOLD at the e+1-close entry was +42 bp,
t 1.17). Question: does a bot that fires at the bar close (or within 1-3 s) still earn it after the real first-seconds
spread? Side: fade the event minute (long after a crash, short after a spike), both sides pooled as F.

## Events (F's registered set, unchanged)
F's PREREG rule "T5 idio": |c_e / c_{e-1} - 1| >= 5 %, top-40 universe that UTC day, not BTC, |r_BTC,e| <= 0.2 |r|,
guard (>= 10 trades, qv > 0, open of e+1 beyond the half-way point), one event per coin per 60 min. Taken from
F/out/cand.npz with F's report.py selection: IS 2020-21 n 380, VAL 2022-24 n 770 (1,150 events, 960 symbol-days).

Note on the guard: it uses o_{e+1}, i.e. the first trade after close_e. An entry at close_e + 1 s / 3 s knows it; an
entry "at the open of e+1" uses the same trade as its fill and as its filter. A live bot can apply it as "the first
trade after the close is still beyond half-way" before sending. Kept as F's.

## Cells (6, declared)
Entry (3) x exit (2):
- **E0**: open of bar e+1 (kline open = first trade at >= close_e; F's `go`). All 1,150 events.
- **E1**: price of the first aggTrade with time >= close_e + 1 s. aggTrades sample only.
- **E3**: price of the first aggTrade with time >= close_e + 3 s. aggTrades sample only.
- Exit: **F's exit**, the close of bar e+1+H, **H in {15, 60}** (same exit as F's registered rule, so only the entry
  moves; holding is H+1 minutes minus latency). Missing exit minute: last close within 5 min (F's px_at), else drop.
- P&L = side x (exit / entry - 1) - side x funding on stamps in (close_e, exit] - costs.
  (F's `f` covers (close_{e+1}, exit]; I add the stamps in (close_e, close_e + 1 min] from the same funding panel.)
- The parameter choice on IS is the best day-clustered IS t among the 6 cells; checked on VAL unchanged. All 6 shown.
  E0 is also reported on the sample events alone, so E0 / E1 / E3 can be compared on the same events.

## Costs (declared)
- Taker 5 bp a side. Half-spread h as F: 1 bp (ETH), 3 bp (volume rank < 20 that day), 5 bp (rank 20-39).
- **Declared cost:** entry half-spread 3h, exit h: round trip 10 + 4h = 22 / 30 bp.
- **Stress:** entry half-spread 5h: 10 + 6h = 28 / 40 bp. Also declared cost x1.5.
- **Measured (real-fill) check, sample only:** entry at the first aggTrade on the taker side we would take (buyer-taker,
  `is_buyer_maker` = false, for a long; seller-taker for a short) at >= close_e + L (L = 0 / 1 / 3 s); exit at the first
  closing-side taker trade at >= the exit time; fees 10 bp only (spread is in the prices). Second version: VWAP of the
  same-side taker trades until $10,000 of notional is filled (window cap 10 s; if not filled, VWAP of what traded)
  at both legs. A passing cell must also be net > 0 in IS and VAL on the $10k real-fill version (reported per era).
- **Spread measurement (sample):** per event and window, (VWAP buyer-taker - VWAP seller-taker) / their mean, when both
  sides traded, for windows [0, 1), [1, 3), [3, 10), [10, 60) s after close_e and [0, 10) s after the exit time; median
  and mean across events, half = /2, compared with the 3h model (9 / 15 bp). Slippage: side x (same-side taker first
  price / any-side first price - 1) at L = 0 / 1 / 3 s, and the aggTrade first price vs the kline o_{e+1} (QC: should
  be equal).

## Bars (BRIEF, unchanged)
LIVE: IS day-clustered t >= 2.5, VAL t >= 1.5, >= 2/3 of years 2020-24 positive, beats >= 95 % of random entries,
net > 0 in IS and VAL at costs x1.5 and one step late, forward power at VAL size >= 3 (registered as months needed).
DEMO: IS t >= 2.0, VAL net > 0, >= 90 % random. "One step late": E0 -> E1, E1 -> E3, E3 -> E10 (first trade >= close_e
+ 10 s, a check, not a cell). Random benchmark: F's 200 random-minute draws per event (same coin, era, sigma decile;
side fades the random minute; F's entry), charged the cell's cost; share of draws whose mean net is below the cell's.
F noted this is a weak test (random draws only lose the cost). Max-over-6-cells IS-t null from the same draws.

## Sample design (aggTrades)
- Two fixed random permutations (numpy default_rng seed 6606): one of the 380 IS events, one of the 770 VAL events.
  Pull order: alternate IS, VAL, IS, VAL ... until IS is exhausted, then VAL only. Stop at 45 min of pull or when all
  are done. Every pulled event is used (stopping depends only on the clock; no return is computed during the pull).
  Minimum target >= 200 IS + >= 200 VAL; events sharing a symbol-day share one download.
- Per symbol-day, one daily futures/um aggTrades zip is streamed (deflate decoded on the fly) and the connection is
  closed after the last needed timestamp; rows in [close_e - 2 min, close_e + 65 min] of each event on that day are
  kept (the next day's file is streamed only up to its cutoff when the window crosses midnight). Compact npz per
  symbol-day in research/data/wick_aggtrades/npz/: time ms, price, qty, is_buyer_maker. No zip is kept.
- data.binance.vision robots.txt: 404 (logged). >= 0.3 s between request starts, 3 threads, back-off on 418 / 429 / 503,
  stop on 403, plain non-browser User-Agent, no personal data.

## Power arithmetic (before data)
- Sample t: if E1 / E3 keep F's per-trade S (IS 0.224, VAL 0.163) and clustering costs ~25 % of t as in F, a sample of
  n_IS events gives t ~ 0.75 x 0.224 x sqrt(n_IS): n_IS 200 -> 2.4, 300 -> 2.9, 380 -> 3.3. So the IS bar 2.5 needs most
  of the IS events; a pull limited to ~200 IS events can at best reach DEMO for E1 / E3 unless the 1-3 s entry is
  better than E0. VAL: 0.75 x 0.163 x sqrt(300) = 2.1 >= 1.5.
- Forward power: the forward pace is taken from F's registered HOLD event count (2,080 events in 22 months, ~94.5 /
  month; a count, not a return). n_fwd needed = (3 / S_VAL)^2; months = n_fwd / 94.5. E.g. S 0.163 -> 339 trades ->
  3.6 months; S 0.10 -> 900 -> 9.5 months; S 0.05 -> 3,600 -> 38 months. Day-clustered: n_fwd = n_VAL x (3 / t_VAL)^2
  at the VAL clustering (reported too; the larger of the two is the registered size).

## Addendum 1 (2026-11-01 13:25 UTC, before any F0 return)
The first pull stalled: 22 files in the first 2 min (12:25-12:27 UTC), then one connection trickled for 56 min (the
socket timeout never fired; stream G0 saw a stalled download at the same time). Restarted with a 20 s socket timeout,
read1() chunks, a 150 s wall deadline per file, failed files re-queued (<= 3 tries) and a hard stop. Same order and
seed; the 22 files already saved are reused. Restart budget 35 min of clock (the stalled hour counts against the
~45 min guideline; reported). Nothing else changes.
