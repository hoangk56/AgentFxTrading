# Stream A2 (round 65) hypotheses: seconds after the Upbit KRW-listing notice

Written Sun Nov 1 12:04:44 UTC 2026 (from `date -u`). At this point only stream A's event list (A/notice_events_L.csv),
stream W / A's notice JSON (read-only) and five data.binance.vision requests (robots.txt 404, four HEAD size probes)
have been used. **No aggTrade has been downloaded, no price or return computed.** HOLD (2025-01-01..) is never
requested, loaded or counted: only daily files dated 2020-04..2024-12 are requested, and every event has N < 2025.

## Question
Stream A: the alt jumps +1,524 bp (IS) / +1,953 bp (VAL) vs BTC on the Binance perp inside the notice minute, in 100 %
of events. How much is left d seconds after the notice's own timestamp, i.e. could a bot that polls Upbit's notice
API catch it? Side fixed before data: **long the alt USDT-M perp, short BTCUSDT perp, equal notional.**

## Timestamp-precision check (done before any price)
- `first_listed_at` (and `listed_at`) are ISO strings with **whole seconds and a +09:00 offset** in all 80 fetched
  bodies and all 5,953 list rows (no milliseconds). So N is known to +-1 s at best.
- It is the **publish time, not the creation time**: ids are assigned at creation, and 4 of 4,199 pre-2025 notices
  have a later id but an earlier first_listed_at (e.g. id 4293 stamped 2024-06-17 15:00:00 vs id 4294 at 14:39:02 KST),
  i.e. scheduled posts that went live at a round time. 16 % of notices are stamped at second 00-02 (5 % if uniform),
  and many listing notices sit at hh:00:00-hh:00:23 or hh:30:00-08 (scheduled releases). `listed_at` differs from
  `first_listed_at` in 238 rows (later edits); only first_listed_at is used.
- Whether the stamp is the moment the public could see the notice is tested on Binance (below): if the burst starts
  before N, the stamp is late or the news leaks (e.g. Upbit's app push, Telegram bots or the KRW market list showing
  first), and I report it per event.

## Data (pulled after this file)
- data.binance.vision `futures/um/daily/aggTrades/<SYM>/<SYM>-aggTrades-<day>.zip` for each event's alt and BTCUSDT
  on the event day (44 alt files + 41 BTC days). Each zip is streamed to research/data/upbit_latency/tmp/, parsed with
  `python -I`, and deleted. Kept (research/data/upbit_latency/npz/): all trades (time ms, price, qty, buyer-maker) in
  [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min], plus a 1-second last-price / trade-count series of the whole
  day (for the random benchmark). Plain UA `research-script`, >= 0.3 s between requests, back off on 418/429/503,
  403 = stop. Every request logged in research/data/upbit_latency/requests.log.
- Events: stream A's 44 (IS 12 on 9 notice days, VAL 32 on 32 days; SRM dropped as in A). L = first Upbit KRW 1m
  candle; MATIC uses SOL's L (same notice), STG / BONK use stated start + 5 min (A's rule).
- Funding: local research/data/binance/funding/<SYM>.csv, else public fapi fundingRate (logged); long alt pays its
  rate, short BTC receives BTC's, at stamps in (entry, exit].

## Declared definitions (before any price)
- Price at time t = the last aggTrade with transact_time <= t. Relative path r(t) = ln(alt_t / alt_ref) -
  ln(BTC_t / BTC_ref), ref = last trade at or before N - 60 s.
- Path report: median and quartiles of r(t) at t - N in {-60, -30, -10, -5, -2, -1, 0, +1, +2, +3, +5, +10, +20, +30,
  +60, +120, +300} s, per era.
- Burst onset (two definitions, both reported, per event): (a) first alt trade in [N - 300 s, N + 300 s] with
  r(t) >= +2 %; (b) first 1 s bin in the same span with alt trade count >= max(10, 10 x the median per-second count over
  [N - 600 s, N - 60 s]). Onset - N < 0 means the burst leads the stamp.

## Rule and grid (8 cells)
- Entry: alt = price of the first alt aggTrade with time >= N + d s; BTC = first BTC aggTrade with time >= N + d s.
  d in {2, 5, 10, 30} s. Taker fills.
- Exit X in {N + 300 s, L}: first trade with time >= X on each leg (L = the KRW open, not L + 1 h).
- Slippage (declared): per leg and per fill, half the median 1 s range, where the 1 s range is (max - min) / min of
  that symbol's trades in a 1 s bin, over bins with >= 1 trade in the 60 s starting at the fill time. Entry pays it
  (alt bought higher, BTC sold lower); exit pays it again.
- Costs: 20 bp per trade (4 taker fills x 5 bp) + the four slippages + real funding.
  net = (alt_x / alt_e - 1) - (BTC_x / BTC_e - 1) + funding - 20 bp - slippage.
- Cells: D2-5m, D5-5m, D10-5m, D30-5m, D2-L, D5-L, D10-L, D30-L. **D2 is a pure latency race** (a bot needs to read
  the notice and fire within ~1-2 s, against established Upbit-notice bots); a result counts only if d >= 5 carries it.
- Cell choice: best IS t among the d >= 5 cells, checked on VAL unchanged. t clustered by notice day (A's clt).
- Robustness: costs x1.5 (30 bp + 1.5 x slippage); one step late = next d (2 -> 5, 5 -> 10, 10 -> 30, 30 -> 60 s).
- Random benchmark: same coin, same day, entry at random seconds U (from the 1 s series) with the same hold, the whole
  hold outside [N - 15 min, max(N + 30 min, L + 60 min)]; gross r; 1,000 draw sets of one draw per event; percentile
  of the event mean. Max-over-cells: the same draw sets scored on all 8 cells, max t over cells per set.
- Years: IS 2020, 2021; VAL 2022, 2023, 2024.

## Power arithmetic (before any return)
- HOLD pace: K2's registered HOLD count, 92 events over ~22 months (a public fact, not a return). Stream A's notice
  list contains all of K2's events, so n_HOLD ~ 92. **LIVE needs VAL net SR per trade >= 3 / sqrt(92) = 0.31.**
- VAL t >= 1.5 with 32 events on 32 days needs SR >= 0.27.
- IS: 12 events on 9 notice days, t ~ SR x sqrt(9..12). IS t >= 2.5 needs SR ~ 0.75-0.85; DEMO's 2.0 needs ~0.6-0.67.
  Achievable only if the post-d drift is large and consistent; IS notices mostly came at the open (L - N ~ 5 min), so
  the 5-minute and the L exits are nearly the same trade in 7 of 12 IS events.
- Prior: stream A's 1m bars put almost all of the jump inside the notice minute and ~+80 to +120 bp mean in the next
  minute. If the jump completes within 2-5 s, every cell fails after 20 bp + slippage on a fast market.
