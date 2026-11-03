# HYPOTHESES_SI: stacked imbalance zones (book setup #4, OF4)

Written 2026-11-03 16:53 UTC (from `date -u`), before any return was computed. Stream SI of round 75; common rules in
../BRIEF.md, method in research/methods/order-flow-footprint.md.

## Mechanism

A stacked imbalance is >= 3 adjacent price rows of one 30m bar where aggressive buyers (sellers) traded >= 3x the
opposite aggressive volume on the diagonal row. The book's story: an initiative participant had to lift (hit) through
several prices to get filled; that participant is likely to defend the same prices when price comes back the first time
(resting orders / re-entry at the same level), so the first return to the zone bounces. A buying stack is support (long
on the first test from above), a selling stack is resistance (short on the first test from below). Direction fixed
before data: support -> long, resistance -> short.

## Zone event (declared)

- Footprint: `fp.load_fp(sym, 30)` (k bp rows; BTC k 3, ETH k 4, SOL from its derived file).
- Imbalances: `fp.imbalances(f, ratio=3, floor=F)` (diagonal; opposite cell must be > 0, as in fp.py).
  - F = 0 (cell "f0"), or
  - F = per-bar floor (cell "fmed"): the median of all **non-zero individual bid and ask values** (each side of each
    row counts as one value, as in the book's bid x ask display) over the 48 30m bars **before** the formation bar
    (formation bar excluded; no look-ahead). Bars with fewer than 48 bars of history: no zone. The floor applies to the
    large side (fp.py semantics). fp.py accepts a per-cell floor array; I pass the bar's floor broadcast to its cells.
- Stack: `fp.stacked(f, flag, n=3)`; each run is one zone (a run of 6 is one zone of 6 rows). Several runs in one bar
  are separate zones. n = 4 is computed as information only (not a declared cell, not in the max-over-cells null).
- Zone [lo, hi] = `row_price(low row, 'low')`, `row_price(high row, 'high')`.

## Execution (the BRIEF's common model, unchanged; my reading of the open points)

- Usable at the close of the 2nd 30m bar after the formation bar that lies entirely beyond the zone (support: bar low >
  hi; resistance: bar high < lo); the two bars need not be consecutive. Expiry E = formation close + 336 x 30 min; the
  departure bar must close by E and the test minute must be < E.
- First test: first 1m bar after the usable time whose range reaches the near edge (support low <= hi, resistance high
  >= lo). Fill only if that minute trades >= 1 bp through (support low <= hi(1 - 1e-4), resistance high >= lo(1 + 1e-4)).
  Not filled -> zone gone. Entry price = the near edge (no price improvement assumed if the minute opens through it).
  Touches before the usable time do not consume the zone (BRIEF).
- Stop: 0.15 x ATR14 (ATR14 = mean daily true range of the 14 UTC days before the entry day, days built from the 1m
  bars; trades without 14 prior days are skipped). Stop fill = stop price, or the 1m open if it gaps beyond, minus 1 bp
  (BTC, ETH) / 2 bp (SOL) slippage, taker 5 bp.
- TP cells:
  - TPV: POC rows (`fp.poc`) of the 48 30m bars that closed before the entry minute. Long: candidate POC rows whose
    lower edge > entry + 1R and <= entry + 3R; take the nearest; TP = lower edge of the row below it (one row before the
    POC). Short mirrored (upper edge < entry - 1R and >= entry - 3R; TP = upper edge of the row above). None -> TP 2R.
  - 2R: TP = entry +- 2 x stop distance.
  TP (maker 2 bp) fills only if a later 1m bar trades through it (long: high > TP).
- Fill minute: only the stop can trigger. Later minutes: stop before TP if both are reached. Time stop: close of the
  minute at entry + 1440 min (last minute <= that if missing), taker.
- One open trade per symbol per cell; candidates processed in fill-time order; a zone whose first test happens while a
  trade is open (fill minute <= previous exit minute) is consumed without a trade.
- Fees maker 2 bp (entry, TP), taker 5 bp (stop, time stop); funding from research/data/binance/funding/<SYM>.csv (rows
  with t < 2025-01-01 only) at each stamp with entry minute < stamp minute <= exit minute, sign: long pays a positive
  rate.
- Stress: fees **and** slippage x1.5 (stricter than fees only). One step late: market entry (taker 5 bp) at the close
  of the fill minute, same absolute stop and TP prices, exits checked from the next minute.
- Net bp per trade (simple return x side x 1e4 minus costs plus funding) and net R (net bp / stop distance in bp).
  t clustered by UTC day of entry (CR0: se^2 = sum_c (S_c - n_c mean)^2 / n^2); pooled across symbols, a day with trades
  in two symbols is one cluster.

## Eras and order of work

IS 2020-01-01..2021-12-31 (SOL from 2020-09), VAL 2022-01-01..2024-12-31; HOLD never opened (fp.py cuts at 2025-01-01;
funding rows >= 2025 dropped on load). The IS run reads minute data cut at 2022-01-01 (strict: no VAL minute is seen);
trades are assigned to an era by fill minute. The VAL run uses 2020-2024 data and keeps trades filled in VAL. VAL is run
only after the IS cell is chosen and written below in "IS selection".

## Cells (4 declared) and selection

floor {f0, fmed} x TP {TPV, 2R}. The cell with the highest pooled (BTC + ETH + SOL) IS net t is the candidate; it is
checked on VAL unchanged. n = 4 for the same 4 combos is information only.

## Random benchmark (BRIEF)

For each real zone, a random zone of the same width (rows) formed in the same bar, centred on a row drawn uniformly from
the rows spanned by the 48 bars ending with the formation bar (inclusive: min bottom row .. max top row), excluding
centres inside the real zone's rows (lo = centre - (w - 1) // 2). Its type: support if its upper edge is below the
formation bar's close, resistance if its lower edge is above it, else the real zone's type (a random level has no colour,
so its side is where price sits; real stacks also mostly sit on the side the bar closed away from). Departure, first
test, execution and the one-trade rule unchanged. 200 draws (seeded) per symbol, floor and era. Reported: percentile of
the real pooled net t among the 200 random pooled net t per cell and era, and the max-over-4-cells null (per draw, the
max pooled t over the 4 cells) compared with the best real cell. "Beats >= 95 % (90 %)" is required on IS **and** VAL.

## Bars (unchanged, BRIEF)

Common: net > 0 IS and VAL, positive at stress and one step late, t clustered by day.
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years 2020-2024 positive (pooled), random >= 95 %, HOLD power at VAL size
  >= 3, power = (mean / sd per trade, VAL) x sqrt(VAL trades x 22 / 36).
- DEMO: t >= 2.0 IS, net > 0 VAL, random >= 90 %.
A pass -> PREREG_DRAFT_<name>.md and stop. Failure reported as failure.

## Power arithmetic (before data)

Rough count: one open trade per symbol per cell, stop ~0.15 ATR (BTC ATR ~4 % -> stop ~60 bp, 2R target ~120 bp),
typical hold a few hours, so a few hundred to ~1,500 trades per symbol-year at most; assume ~1,000 / symbol-year ->
VAL ~9,000 pooled, HOLD ~5,500. Power 3 then needs mean/sd >= 3 / sqrt(5,500) ~ 0.04 per trade: with sd ~1.3 R
(~80 bp), mean >= ~3 bp net (~0.05 R). Costs per round trip are 4-7 bp (+1-2 bp slippage on stops), i.e. ~0.1 R, so the
gross edge needed is ~0.15 R per trade. If HOLD t comes in at ~1/4 of the VAL t (lesson of rounds 58-66), VAL t needs
to be ~12 for a HOLD t of 3; I will state this next to the formal power number.

## IS selection (written 2026-11-03 17:06 UTC, after the IS run, before any VAL return)

Pooled IS (BTC + ETH + SOL) net t: f0_TPV -0.56, f0_2R -1.06, fmed_TPV -2.01, fmed_2R -2.55. Candidate = **f0_TPV**
(highest IS t). It already fails the IS bars (net < 0; t < 2.0), so no cell can be LIVE or DEMO; VAL is run once with
everything unchanged for the record and for the random benchmark (does the footprint beat random levels out of
sample?). Random IS: f0_TPV beats 99.5 % of random draws (real -1.1 bp vs random median -5.1 bp per trade), max-over-
cells null 87 %.

## Addenda (before any return was read)

- A1 (2026-11-03 16:57 UTC): the BTC 1m cache has 17 gaps in 2020 (831 missing 30m bars, e.g. 2020-04-13, several whole
  days in 2020-11), contrary to the BRIEF's "no gaps". A strict 14-contiguous-day ATR would drop ~14 days after each
  gap, so ATR14 = mean daily true range of the days present among the 14 UTC days before the entry day, >= 10 present
  (a day after a missing day uses high - low). ETH has one missing bar. Missing bars are simply absent for departure /
  test (the brief's rule counts bars that exist).
- A2: the coordinator's BTC footprint fix (2026-11-03) came in while I was developing; all BTC runs are redone on the
  rebuilt derived/BTCUSDT_tf30.npz, and prepare() asserts each bar's low / high lie in its bottom / top row (+-1).
- A3 (2026-11-03 17:03 UTC, coordinator notice on cache holes; supersedes A1): ATR14 now from
  research/data/binance/perp_1d/<SYM>.csv daily klines (rows >= 2025 dropped on load), mean true range of the 14
  contiguous UTC days before the entry day. Holes = gaps > 30 min between cached 1m bars (BTC 24, ETH 7, SOL: see
  report). A candidate trade is dropped (and does not block the one-trade slot) if a hole starts between its zone's
  formation bar and its fill minute, or between fill and exit. Counts per cell are printed in out/log_*.txt and
  reported in STREAM_SI.md. The BTC / ETH IS random benchmark run before this change is void and redone. Only IS
  numbers (BTC + ETH, no SOL) had been looked at; nothing in the cells or bars changes.
