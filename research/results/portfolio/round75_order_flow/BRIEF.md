# Round 75 brief: footprint / order-flow setups on Binance perps (coordinator + subagents)

Written 2026-11-03 15:47 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Each stream
works only in `research/results/portfolio/round75_order_flow/<STREAM>/`. Layout and rules copied from
round66_fast_execution/BRIEF.md; the context and streams are new.

## Context (read, don't redo)
- **research/methods/order-flow-footprint.md**: the method this round tests (Trader Dale, *Order Flow Trading
  Setups*, 2021) written as measurable rules. Read all of it first. Its section 9 lists what was already tested.
- research/PROMPT.md (bars, exhausted families, pitfalls), research/JOURNAL.md top entries.
- Earlier order-flow tests asked "does signed flow predict the next N minutes / hours" (round 4: hourly taker share ->
  BTC 1-4 h, t 0.8; round 17: quote OFI on IC, 1/20 of cost; round 63 O H3: hourly taker imbalance on alts, ~0). They
  failed. This round tests something else: **a footprint event creates a price zone, price leaves it, and the first
  return to the zone is traded** (book section 3). Nobody tested that.
- Lesson of rounds 58-66: crypto micro-structure edges that pass IS / VAL often shrink in 2025-26. Expect HOLD t at
  ~1/4 of VAL size when computing power for a decision, and say so.

## Data (read-only, git-ignored)
- `research/data/footprint/<SYM>/<YYYY-MM>.npz`, SYM in BTCUSDT, ETHUSDT, SOLUSDT (USDT-M perps; SOL from 2020-09),
  built from data.binance.vision monthly aggTrades by `coord/code/build_fp.py`: 1 bp log-price footprint per minute
  (aggressive buy / sell qty), 1m bars with aggressive buy / sell qty, and every aggTrade >= $100k notional.
- `research/data/footprint/derived/<SYM>_tf30.npz`, `<SYM>_tf5.npz`: footprints of 30m and 5m bars with k bp rows,
  k = round(median IS 30m range in bp / 20) per symbol (rule declared before any return; `fp.row_k`).
  Values: **BTC k = 3 bp, ETH k = 4 bp, SOL k = 7 bp** (SOL ready 2026-11-03, 52 months checked, 75,009 30m bars). 30m bars: BTC 86,481, ETH 87,359 (2020-2024).
  **SOL is still building**: its derived files are complete only once `research/data/footprint/derived/SOL_READY`
  exists. Develop on BTC / ETH; before any SOL run check that file (wait and recheck if absent); never read SOL
  month files before it exists. No month is missing for BTC / ETH 2020-01..2024-12 (SOL starts 2020-09), but Binance's monthly
  files skip some days: BTC 24 holes > 30 min (610 h, ~1.4 %: e.g. 2020-04-13 +47 h, 2020-11-08 +38 h, 2022-08-27
  +72 h), ETH 7 (170 h). Take ATR14 from perp_1d daily klines, and drop zones / trades whose life spans a hole
  > 30 min (declare the counts). Found by stream MN.
  **Fix 2026-11-03 (found by stream U):** BTC above $22,026 had its fp_key bucket carry into the minute field;
  `fp.split_key` now undoes it and `derived/BTCUSDT_tf30/tf5` were rebuilt (rows 27315..38644, every 30m bar's
  low / high falls in its bottom / top row, ask volume = 1m aggressive buy). Anything computed on BTC footprints
  before this fix is void. Never read `fp_key` yourself without `fp.split_key(key, sym)`.
- **Use `coord/code/fp.py`** (import by path with importlib; do not edit it): `load_minutes`, `load_big`, `bars`,
  `load_fp`, `row_price`, `poc`, `imbalances` (diagonal, book's figure checked in `_selftest`), `stacked`,
  `unfinished`. If you need a different definition, write it in your own code and say why in HYPOTHESES.
- Funding: `research/data/binance/funding/<SYM>.csv` (t ms, rate). Daily klines: `research/data/binance/perp_1d/`.
- research/.venv has numpy only (no pandas / scipy).

## HOLD stays closed
Eras: IS 2020-01-01..2021-12-31 (SOL from its first month), VAL 2022-01-01..2024-12-31, HOLD 2025-01-01..2026-10-31.
The cache holds no 2025-26 data and fp.py cuts at 2025-01-01. Do not download any 2025-26 file. **Subagents never
open HOLD**: if a rule passes the IS / VAL bars, write PREREG_DRAFT_<name>.md (rule, numbers, power at VAL size,
pass bar, stop / promotion rules) and stop; the coordinator opens HOLD once.

## Bars (unchanged)
Common: economic mechanism; side fixed before data; parameters picked on IS, checked on VAL unchanged; net > 0 in IS
and VAL, positive at costs x1.5 and one step late; t clustered by day.
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % of the random benchmark, HOLD power at VAL
  size >= 3 (power = net mean / sd per trade at VAL x sqrt(expected HOLD trades); HOLD trades = VAL pace x 22 / 36).
- DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % of the random benchmark.
Never lower a bar; report a failure as a failure. Declare <= ~24 cells per stream (book parameters first) and report
the max-over-cells null. Pool the three symbols for the verdict, and report each symbol.

## Common execution model (use it unless your stream section says otherwise; any change goes in HYPOTHESES)
- Zone [lo, hi] = price edges of its rows (`row_price`). It becomes usable at the close of the **2nd full 30m bar
  that lies entirely beyond it** after the formation bar (support: bar low > hi; resistance: bar high < lo), and
  expires 7 days (336 bars) after formation.
- **First test only:** the first 1m bar after the usable time whose range reaches the near edge consumes the zone
  (support: low <= hi). Entry = limit at the near edge, filled only if that minute trades >= 1 bp through it (support:
  low <= hi x (1 - 1e-4)); if not, the zone is gone and there is no trade. Direction: support -> long, resistance ->
  short (from where price comes, not from the colour of the cells).
- Stop: 0.15 x ATR14 (daily true range of UTC days, mean of the 14 days before the entry day) from the entry. Stop
  fill = stop price, or the 1m open if it gaps beyond, minus slippage 1 bp (BTC, ETH) / 2 bp (SOL), taker fee.
- Take-profit, two declared cells:
  - TPV (book): the nearest POC of the 48 30m bars before the entry that lies beyond entry + 1R in the trade direction,
    one row before it (limit, maker). None within 3R -> TP = 2R.
  - 2R: fixed at 2 x the stop distance.
  TP fills only if a 1m bar trades through it (high > TP for a long).
- Time stop: exit at the 1m close 24 h after entry (taker). One open trade per symbol per cell; zones that test while
  a trade is open are consumed without a trade.
- Same-minute ambiguity: in the fill minute only the stop can trigger; later, if a minute reaches both stop and TP,
  the stop comes first.
- Fees: maker 2 bp (limit entry, TP), taker 5 bp (stop, time stop, market entries) per side; funding at each 00 / 08
  / 16 UTC stamp held. Stress: fees x1.5. One step late: enter with a market order at the close of the fill minute.
- Report net bp per trade and in R; t clustered by UTC day.
- **Random benchmark (required):** the same pipeline on random levels: for each real zone, a zone of the same width
  formed in the same bar but centred on a row drawn uniformly from that bar's 48-bar range, excluding the real zone's
  rows; departure, first test and execution unchanged; >= 200 draws; report the percentile of the real net t. This
  answers "is it the footprint, or just the first retest of any level?".

## How to work
1. Before computing any return: write `HYPOTHESES_<STREAM>.md` with the UTC time from `date -u` (never estimate the
   time), the mechanism, the exact rules / small grid, costs, power arithmetic.
2. Build, test on IS, check on VAL with parameters unchanged.
3. Write `STREAM_<STREAM>.md`: answer first (LIVE / DEMO / none), tables per era, year and symbol, costs x1.5, one
   step late, random benchmark percentile, what failed and why, pitfalls.
4. Code in `<STREAM>/code/`, outputs in `<STREAM>/out/`. Do not edit files outside your stream folder. No git
   commands. No downloads (everything needed is local); no web searches.
5. Machine: 10 cores / 16 GB shared by 7 streams: one heavy process at a time, keep resident memory under ~2 GB
   (load one symbol at a time), and check your background jobs yourself.

## Report back to the coordinator (final message, <= 250 words)
Verdict per rule (LIVE / DEMO / none) with IS / VAL net, t, years positive, random percentile, power at VAL size;
the file paths written; any PREREG_DRAFT; problems.



## Stream U: is an unfinished auction a magnet? (book setup #5, a statistic first)
- Turn: a 30m bar whose high is the highest of the 4 bars before and the 2 bars after it (swing high; mirror for
  lows). Confirmed at the close of the 2nd bar after. Level = its top row (`unfinished`: bid > 0 and ask > 0 there).
- Statistic (main answer): P(price trades back into the level row within H in {12, 48} bars after confirmation),
  unfinished vs finished turns, matched on distance from the confirmation close to the level (in ATR14 deciles) and
  on 30m ATR. Report by era, year, symbol. If unfinished is not more likely to be revisited, the book's "magnet" uses
  (TP extension, stop placement, no-trade warning) are void: say so plainly.
- Trade cells (<= 8, declared): at confirmation, enter toward an unfinished level (long under an unfinished high),
  TP one row before the level, stop at the same distance on the other side, time stop H; the same on finished turns
  is the control (the difference is the answer, not the raw net).

## Stream SI: stacked imbalance zones (book setup #4)
- `imbalances(ratio=3)` on the 30m footprint, floor in {0, median non-zero cell volume of the 48 bars before};
  `stacked(n=3)`. A buying stack is a support zone, a selling stack a resistance zone.
- Common execution; cells: floor {0, median} x TP {TPV, 2R} (4 cells), plus n = 4 as information only.

## Stream MN: multiple nodes (book setup #2)
- POC (`poc`) of >= n consecutive 30m bars in the same row, n in {2, 3}; zone = that row. The book allows it before a
  trend, in a trend or in a rejection: no context filter (declare). Common execution; cells n x TP (4 cells).

## Stream VC: volume clusters in a trend or a rejection (book setup #1 and Volume Profile setups 2-3)
- Trend leg: 8 consecutive 30m bars with |close_end - open_start| >= 0.5 x ATR14 and >= 6 bars closing in the leg's
  direction. Rejection: a swing of >= 0.4 x ATR14 in <= 4 bars, then a reversal of >= 0.4 x ATR14 in <= 4 bars (the
  leg is the reversal). Profile the leg's rows (sum of its 30m footprints); cluster = the max-volume row and the
  contiguous rows around it with volume >= c x the leg's median row volume, c in {2, 3}. Exclude the leg's first and
  last bar rows if the cluster sits on the extreme row (a turning point, not a cluster); declare.
- Trend: support in an up leg (long), resistance in a down leg; rejection: in the direction of the reversal.
- Common execution; cells: {trend, rejection} x c x TP (8 cells).

## Stream TF: trades filter (book setup #3)
- Big trade: an aggTrade with notional >= Q, where Q is set each calendar month from the previous month so that it
  would have given R big trades per day, R in {5, 10} (point in time; the book: "5-10 signals a day"). Zone = the row
  of the big trade (big trades in the same 30m bar and adjacent rows merge into one zone). Side of the trade does not
  set the direction; the side of the test does.
- Common execution; cells R x TP (4 cells); also report aggressive-buy vs aggressive-sell big trades separately as
  information.

## Stream CF: aggressive delta and CVD divergence at Volume Profile levels (confirmations #3, #4)
- Levels for UTC day d: POC, VAH, VAL of day d - 1 (70 % value area grown from the POC row by row toward the larger
  neighbour, using the 30m footprint rows). A level is tested the first time on day d that price reaches it from one
  side (from above -> support).
- Within 30 minutes after the test, confirmation:
  - C3: a 5m bar with delta in the trade direction and |delta| >= x of its volume, x in {0.2, 0.4};
  - C4: on 1m, price makes a lower low than the lowest low of the 30 minutes before the test while the cumulative delta
    (reset 00:00 UTC) makes a higher low (mirror for resistance); declare the swing rule.
  Entry: market at the close of the confirming bar (taker). Stop / TP / time stop as the common model.
- Controls: the same levels with entry at the test (no confirmation) and random levels. Cells: {C3 x2, C4, none} x
  TP (8 cells).

## Stream AB: big limit orders and absorption at Volume Profile levels (confirmations #1, #2)
- Same levels and tests as stream CF (write your own level code from that definition; do not read CF's files).
- Within 30 minutes after the test, on the 5m footprint rows inside the zone (level row +- 1 row):
  - C1 big limit: support -> a bid cell >= m x the mean non-zero cell volume of the 12 5m bars before the test (a
    passive buyer); resistance -> an ask cell; m in {4, 8};
  - C2 absorption: a cell with both bid and ask >= m x that mean and the 5m bar closes inside or back on the level's
    side;
  - bonus: C1 or C2, then a 5m bar with delta in the trade direction within the next 15 minutes (book: best case).
  Entry: market at the close of the confirming 5m bar. Stop / TP / time stop as the common model.
- Controls: entry at the test without confirmation, and random levels. Cells: {C1, C2, bonus} x m x TP (12 cells).
