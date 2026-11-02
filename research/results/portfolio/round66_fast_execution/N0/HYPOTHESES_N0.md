# Round 66 stream N0: fade the first-minutes overshoot of a new Binance USDT-M perp (declared before any return)

Written 2026-11-01 14:21 UTC (from `date -u`). Nothing has been downloaded yet; no launch-day price, path or return has
been computed or looked at. Only the listing list (round 60 code, 1d kline first-row dates) and the spot first-kline
dates have been read: 376 launches, IS 127 (NEW 39 / OLD 88), VAL 249 (NEW 138 / OLD 111); by year 2020 73, 2021 54,
2022 22, 2023 98, 2024 129.

## Mechanism
A perp opens at a scheduled time with an empty order book. Retail market orders (launch FOMO, or the dump of
airdrop / spot holders who can now short or hedge) hit a book that market makers are still building, so the first
trades print far from where the price settles once inventory and arbitrage against spot (where it exists) arrive.
A fade of a large first-k-minute move should earn the settling. Risk: the move is information (a real repricing that
keeps going), or a squeeze (round 60's lesson: new listings carry fat squeeze tails; here the hold is 1 h, so the tail
is bounded but still large).

## Events (fixed)
- Listing list = round 60 (`round60_new_listings/code/listings.py events()`: first 1d kline per base asset, no
  re-denominations, no stable / index / TradFi perps), launch day 2020-01-01..2024-12-31 (`N0/code/events.py`).
- Launch time T0 = time of the first aggTrade in the launch day's data.binance.vision daily aggTrades file (UTC); P0 =
  its price. If the day file is missing (404) the event is dropped (reported). If the first trade of the file is in its
  first second (00:00:00) and the 1d kline of the previous day exists, the event is flagged and dropped (not a launch).
- Groups (separate cells): NEW = no Binance spot pair or spot first kline <= 30 days before the launch day; OLD = spot
  listed > 30 days before (spot-existing coin). Eras by launch day: IS 2020-21, VAL 2022-24. Nothing on or after
  2025-01-01 is requested or loaded.

## Rule and the 8 declared cells
- Move m = ln(P(T0 + k min) / P0), P(t) = last aggTrade at or before t.
- If |m| >= X: fade it. Side s = -sign(m) (short after a rise, long after a drop). Enter at the first aggTrade >=
  T0 + k min + 2 s (price of that trade); BTC hedge with equal notional on the opposite side (s = -1 alt -> long BTC).
  Exit at the first aggTrade >= T0 + 60 min; BTC leg priced from BTCUSDT perp 1m klines: open of the minute that
  contains the entry / exit time (launches are scheduled on the minute, so this is ~2 s stale; it only adds hedge noise).
- **Cells: group {NEW, OLD} x k {1, 5} min x X {5 %, 10 %} = 8 cells.** The pooled (NEW + OLD) rows are reported for
  reading only, not graded. One event per listing per cell. Selection: the cell with the best IS t among those that
  pass the IS bars is the candidate; VAL checks it unchanged.

## Costs (measured, not modelled)
Per trade = alt taker 5 bp x 2 + BTC taker 5 bp x 2 + BTC half-spread 1 bp x 2 + alt half-spread measured at entry
and at exit + real funding.
- Alt half-spread in a window W = (VWAP of buyer-taker trades - VWAP of seller-taker trades) / their mean / 2, floored
  at 0; W = [t, t + 1 s) from the fill time; if either side has no trade there, widen to 5 s, then 30 s; if still
  one-sided, use A2's slip (half the median 1 s high-low range over the next 60 s). Expected from F0 (seasoned
  altcoins in a wick second): ~7-11 bp median, 25+ bp in thin books; new books are likely wider.
- Funding: the alt's and BTC's real stamps in (entry, exit] from research/data/binance/funding*, side-signed.
- Robustness (reported, not graded): costs x1.5; one step late = entry at the first trade >= T0 + k min + 62 s;
  real fills = taker-side VWAP of our first $10k of aggressor-side volume at entry and at exit (fees 10 + 10 bp, BTC
  spread 2 bp); entry delay 0 s / 10 s (path only).

## Random benchmark
Same coin, days 2..30 after the launch day (alt + BTC perp 1m klines from data.binance.vision monthly files, cut at
2024-12-31 23:59): random start minutes u with a 1m move ln(close[u+k-1] / open[u]) of the same sign and |move| >= X;
fade from close[u+k-1] to close[u+59], BTC-hedged, gross. If a coin has fewer than 5 such minutes, its 10 largest
same-sign k-minute moves are the pool (count reported). 1,000 draw sets (one draw per event); the event gross mean
must beat >= 95 % (LIVE) / 90 % (DEMO) of random set means. Also the max-over-8-cells null: 95th percentile of the
max net t over cells when each event's return is replaced by a random draw minus the event's own cost.

## Bars (unchanged)
Net > 0 in IS and VAL, positive at costs x1.5 and one step late, t clustered by launch day.
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive (IS 2020, 2021; VAL 2022, 2023, 2024), beats >= 95 % random,
HOLD power at VAL size >= 3. DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random. A passing cell -> PREREG_DRAFT_N0_<name>.md
and stop (HOLD stays closed).

## Power arithmetic (before data)
VAL pace 249 listings / 3 yr = 83 / yr; HOLD 2025-01..2026-10-29 = 1.83 yr -> ~152 listings expected at the VAL pace
(the 2025-26 count is not looked at). A group holds ~45-55 % of listings, so a cell with qualifying share f has ~76 f
HOLD trades: f = 0.5 -> ~38 trades, power 3 needs net Sharpe per trade >= 0.49; f = 0.25 -> ~19 trades, >= 0.69.
On IS the NEW cells have <= 39 events (f = 0.5 -> ~20): t 2.5 needs Sharpe per trade ~0.56. So LIVE needs a very
strong per-trade effect (e.g. +3 % mean with 6 % sd); a weaker real effect can at most be DEMO, and a NEW-group IS
cell is likely too small to reach t 2.0 unless the effect is large. Stated now so a small-n failure is not read as a
pass-in-waiting.

## Data and pull plan (no subsample unless the clock forces it)
- data.binance.vision futures/um daily aggTrades, launch day (+ next day if T0 + 2 h crosses midnight), all 376
  events, streamed (deflate-decoded on the fly, nothing written as zip), rows kept T0 .. T0 + 2 h ->
  research/data/perp_launch/agg/<SYM>_<day>.npz. Order: seeded random interleave of IS / VAL; if the ~45 min budget
  ends first, the pulled events are a random subsample (declared here) and the rest are reported missing.
- futures/um monthly 1m klines for each alt (months covering launch day .. day 30) and BTCUSDT (2020-01..2024-12),
  -> research/data/perp_launch/k1m/. requests.log: UTC time, URL, status, bytes; >= 0.3 s between requests to the
  host, back off on 418 / 429 / 503, 403 = stop. robots.txt checked and logged first.
