# Hypotheses R2 (round 67): rotation out of Upbit-heavy coins after an Upbit KRW-listing notice

Written Sun Nov 1 14:54:41 UTC 2026 (from `date -u`). No return, price path or P&L of any kind has been computed
when this file is written. HOLD (2025-01-01..) is never requested, loaded or counted: every series is cut at
ts < 2025-01-01 at load, and every fapi request asserts endTime < 2025-01-01 00:00 UTC.

## Mechanism (side fixed now)
Korean retail funds a new Upbit KRW listing by selling what it already holds on Upbit. Upbit-heavy alts are the
coins Korean retail holds disproportionately, so the selling pressure should show up as a relative fall of those alts
on Binance perps between the notice N and the KRW open L (cash is raised before buys open), and possibly for a while
after L (late rotation, money chasing the listed coin's first hours). **Side: short the Upbit-heavy basket.**
Prior: weak. Korean flows are a small share of global volume for most coins, the rotation is spread over many
holdings, and stream R found an hour-of-day rhythm in the same high-share coins (they fall in the Korean day); the
random benchmark below is therefore matched on time of day and weekday.

## Events
- round65_retail_venues/A/notice_events_L.csv (read-only), one trade per notice id (a notice with two coins is one
  basket trade). SRM (notice 1536) is dropped (L unknown), as in stream A.
- Notice time N = `N` (ms, first_listed_at). L per notice = earliest KRW open among the notice's coins: L1m when
  present; STG and BONK: stated + 5 min; MATIC shares notice 2217 with SOL (SOL's L). 2217 -> SOL's L, 2239 -> 1INCH's
  L (the earlier of 1INCH / AAVE).
- Expected count: IS 2020-21 9 notices (9 days), VAL 2022-24 32 notices.

## Basket (point in time, no future data)
- Day d = UTC day of N. Universe(d) = stream R's top-60 USDT-M perps by mean daily quote volume over d-30..d-1
  (listed >= 60 d; stream R's panel research/data/korea_hours/panel.npz and R/code/rdata.py, read-only).
- Upbit share(i, d) = sum over d-30..d-1 of Upbit KRW value (in USD) / sum of Binance perp quote volume (stream R's
  `shares`, the same 30-day share logic as stream U's udata.py but daily). Universe A = Universe(d) with a measured
  share.
- High tercile = top floor(n/3) of universe A by share, low tercile = bottom floor(n/3). The notice's listed coin(s)
  and BTC are excluded. Equal weight, $1 per side.

## Rule and declared cells (6)
- Entry: close of the first 1m bar that opens at or after N + 60 s (bar t_e = ceil((N + 60 s) / 1 min)); price =
  its close (time t_e + 1 min). Exit price = 1m close at time X (close of the bar that opens at X - 1 min), with up to
  5 minutes of forward fill (stale beyond that = coin dropped from that trade, weights renormalised).
- Cells = hedge {BTC, LOW} x exit {L, L1H = L + 1 h, L6H = L + 6 h}:
  - **BTC-L, BTC-L1H, BTC-L6H** (primary, as the brief): short the high tercile, long BTCUSDT perp.
  - **LOW-L, LOW-L1H, LOW-L6H**: short the high tercile, long the low-share tercile (isolates the Korean-share
    component from alt beta).
- No parameter is fitted: there is nothing to pick on IS besides which of the 6 cells is best; the IS pick is the
  cell with the highest IS t, checked on VAL unchanged. The max-over-6-cells null is reported.
- Trades with exit time <= entry time are dropped (possible only for exit L when L - N < 2 min; none expected).

## Costs
- Taker 5 bp per side per leg + half-spread (round 63 C model as stream R): BTC 1 bp, volume rank < 20 3 bp, else
  5 bp, by universe rank on day d. Round trip on both legs ~ 2 x (5 + ~4.5) + 2 x (5 + 1) ~ 31 bp for BTC cells,
  ~38 bp for LOW cells.
- Real funding from stream R's hourly funding grid (stamps in (entry, exit]); short leg receives, long leg pays.
- Checks: costs x 1.5; one step late = entry and exit both one 1m bar later. Information: entry 5 min late.

## Statistics and benchmark
- Net bp per notice; t clustered by notice day (each notice is its own day here; 2217 / 2239 are separate days).
- Years 2020..2024: share of years with net > 0.
- Random benchmark ("same basket at random hours"): per notice, 20 random draws with the same basket coins, weights,
  hedge, entry minute-of-day, entry -> exit offsets; the draw day is a uniformly random KST weekday within +-60 days of
  N, at least 2 days from every notice in the list, same era, and the window ends before 2025-01-01. Pricing as the
  real trade on 1m. Percentile of the real gross mean among 2000 random means (one draw per notice resampled).
  Max-over-6-cells null: the IS t of each cell on each random book, max over cells, 95th percentile. If the pull for
  20 draws would exceed ~45 min, the draws are cut to 12 per notice (decided on request count, before any return).
- Data: research/data/binance_1m_wicks/npz (top-40 months, read-only); fapi /fapi/v1/klines 1m for every other
  (symbol, window), cached in research/data/upbit_rotation/, logged in research/data/upbit_rotation/requests.log.

## Bars (from the brief, unchanged)
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, >= 95 % random, positive at costs x 1.5 and one step
  late, HOLD power at VAL size >= 3. DEMO: IS t >= 2.0, VAL net > 0, >= 90 % random.

## Power arithmetic
- HOLD n: VAL rate 32 / 3 yr = 10.7 / yr x 1.83 yr ~ 19.5 notices (2024 alone had ~20, which would give ~37).
- LIVE needs VAL per-notice net SR >= 3 / sqrt(19.5) = 0.68 (0.49 at the 2024 rate).
- IS: 9 notices on 9 days; t >= 2.0 needs an IS per-notice SR of about 0.7.
- If basket-vs-BTC has a ~100-200 bp sd over 1-7 h, the VAL net mean must be ~70-140 bp on top of ~31 bp cost. In IS
  the exit-at-L cells hold 2-40 min for 7 of 9 notices, so they cannot carry the IS bar unless the move is large.
  Expected outcome: none. A gross sign is reported even if net fails.
