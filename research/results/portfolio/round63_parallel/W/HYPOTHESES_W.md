# HYPOTHESES_W: Kalshi daily high-temperature contracts vs the exact settlement rule

Written Sat Oct 31 16:11:31 UTC 2026 (from `date -u`), before any bulk price pull. Stream W of round 63.

## Gate (step 0) result, before this file
- `api.elections.kalshi.com/robots.txt` = 404 (no restrictions on the API host); docs.kalshi.com robots allows all
  but `/_next/` and `/cdn-cgi/`; kalshi.com sits behind a Vercel bot checkpoint (not touched further). The market-data
  endpoints are documented with `security: []` (keyless).
- Pre-2025 history EXISTS through the archive endpoints: `GET /historical/markets?event_ticker=HIGHNY-23JUN15` returned
  the 6 brackets of 2023-06-15 (status finalized, `expiration_value` 77.00), and
  `GET /historical/markets/HIGHNY-23JUN15-B77.5/candlesticks?period_interval=60` returned 27 hourly candles with
  yes_bid / yes_ask OHLC, trade-price OHLC, volume and open interest. Only these two probes saw prices.
- Pre-2025 daily-temperature series (old names, no `KX`): HIGHNY (+ HIGHNY0), HIGHCHI, HIGHAUS, HIGHMIA. No daily-low
  series existed before 2025 (all `KXLOWT*` are new). Any `KXHIGH*` market that closed before 2025 is also used.

## Mechanism
Settlement is the NWS Daily Climate Report (CLI) for one named station, the day in local standard time (LST), integer
°F. Late in the LST day the outcome is mostly fixed by the observed maximum so far (ASOS hourly METAR plus specials,
free in NOAA ISD): a bracket whose upper bound is below the observed max is dead, a ">= X" bracket with X <= observed
max is won. Retail traders anchor on phone apps and on the local clock day (during DST the LST day ends 00:59
local); low-priced brackets attract longshot buyers. Who is on the other side: retail takers; the edge exists only
if the quotes are stale or the takers pay for lottery tickets.

## Data
- Kalshi: `/historical/markets?series_ticker=<S>` for the series above, kept only if `close_time < 2025-01-01` (cut at
  parse, before anything is stored or printed; 2025-26 rows are dropped in memory). Hourly candlesticks per kept
  market from its open to its close. Fields used: candle end time, yes_bid close, yes_ask close, volume.
  Truth = Kalshi `expiration_value` (the CLI value it settled on) and `result`.
- NOAA ISD full (public AWS bucket `noaa-isd-pds`, `data/<Y>/<USAF>-<WBAN>-<Y>.gz`) for the settlement stations
  (taken from `rules_primary`; expected NYC Central Park 725053-94728, Chicago Midway 725340-14819, Austin
  Bergstrom 722540-13904, Miami Intl 722020-12839), 2005-2024. Air temperature (tenths °C) of every report -> °F
  rounded to the integer (ASOS measures in whole °F, so the round trip is exact for METAR T-groups).
- Climatology model fitted on ISD 2005-2021 only (no market overlap): P(final CLI max - M_T = k | city, month
  group, LST hour T, M_T), where M_T = max integer °F observed from 00:00 LST to T (reports stamped <= T - 10 min
  latency), and the final value = the 24-h max (ISD KA1 group of the report closing the LST day; fallback: max of all
  reports that day). Checked against Kalshi `expiration_value` on IS 2022-23 (match rate reported).

## Eras (new-era split, declared honestly)
Kalshi weather starts ~2021-2022, so the brief's IS 2016-21 / VAL 2022-24 cannot be used. IS = earliest..2023-12-31,
VAL = 2024-01-01..2024-12-31, HOLD 2025-01-01.. stays closed. The ISD model uses 2005-2021 (pre-market).

## Rules (side fixed before data; small grid declared here)
Prices: buy YES at yes_ask close of the hourly candle that ends at decision time; buy NO at no_ask = 1 - yes_bid
close. Skip if the quote is missing or yes_bid = 0 / yes_ask = 1 (no quote). Hold to settlement.
Fee (taker): ceil(0.07 x C x P x (1 - P)) dollars rounded up to the cent, C = 10 contracts per order, P = price paid.
Size: 10 contracts; P&L per contract in $; returns per $ at risk = P&L / price paid.

- **(a) Model edge at a fixed LST hour.** At T in {15:00, 17:00} LST, for every bracket compute p_model from the
  ISD-fitted distribution; edge_yes = p - ask - fee/C, edge_no = (1 - p) - (1 - bid) - fee/C. Take the single
  bracket-side with the largest edge per city-day; trade if edge >= theta, theta in {0.05, 0.10}. Grid 2 x 2 = 4 cells.
- **(b) Dead / won brackets under the observed max.** At each hourly candle end from 10:00 to 23:00 LST, a bracket
  is dead if its upper bound < M_T (YES impossible) and won if it is a ">= X" bracket with X <= M_T. Buy NO on a
  dead bracket when yes_bid >= x; buy YES on a won bracket when yes_ask <= 1 - x; x in {0.03, 0.05}. First such hour
  per bracket; P&L summed per city-day. 2 cells.
- **(c) Favourite-longshot.** At the last hourly candle before 00:00 LST of the contract day (T-1 evening), buy NO on
  every bracket with yes mid in [0.03, 0.10] (cell c1; [0.10, 0.20] = c2, information). P&L averaged per city-day.

One step late = next hourly candle's quotes. Costs x1.5 = fee x1.5 plus half the quoted spread again as slippage
(the spread is already paid once at the touch). Maker variant (information only): price at mid, no fee.

## Statistics and bars
- t clustered by calendar date (all cities of one date = one cluster; more conservative than city-day). Also
  reported clustered by city-day.
- Random benchmark: same timing and same side, the bracket replaced by a random bracket of the same event that has a
  valid quote (and, for (b), is not dead/won), 1000 draws; % of draws whose mean net is below the rule's.
- Max-over-cells null: 7 declared cells (4 + 2 + 1); report the best cell's random percentile against the max over
  cells of each draw.
- Bars from BRIEF.md unchanged (LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years positive, beats >= 95 % random, HOLD
  power >= 3; DEMO: t >= 2.0 IS, VAL net > 0, >= 90 % random). Capital: a held contract ties up < 1 day; cash-rate
  excess is negligible (< 0.02 % per trade) and is noted, not subtracted.

## Power arithmetic (before building)
HOLD 2025-01..2026-10 (~1.8 y). The four old cities give ~4 x 665 = 2,660 city-days; Kalshi listed ~20 US cities in
2025-26 (~13,000 city-days) but a rule graded on 4 cities can only be claimed for those 4 unless VAL covers more.
- (b) near-arbitrage: buy NO at 0.95-0.97 on a dead bracket: mean +3 to +5 c minus fee (~0.2-0.3 c at C = 10)
  minus CLI-disagreement losses. If 1 % of such trades lose (CLI revision, station mismatch), per $ mean ~+3 % with
  sd ~10 % -> per-trade Sharpe ~0.3; even 200 HOLD city-days give power ~4. The real limit is how often a dead
  bracket still shows a >= 3 c bid (stale quotes) and the depth behind it (hourly candles give no size).
- (a): per-trade Sharpe for a binary bought at p with true q: (q - p) / sqrt(q(1 - q)). With edge 0.05 at p 0.5:
  0.10 -> needs 900 HOLD trades (1/3 of the 4-city city-days). Edge 0.10: 225 trades.
- (c): buy NO at 0.93 when true q_NO = 0.96: mean +3.2 % per $, sd ~21 % -> Sharpe 0.15 per bracket; ~1.5
  brackets per city-day in band, correlated -> ~0.15-0.2 per city-day -> 2,660 city-days give power 7-10 on paper.
  A 1 c edge (literature size at 90 c) gives Sharpe 0.05 -> power 2.6: below LIVE.
So every cell can reach LIVE power on paper if the IS/VAL edge is >= ~2-3 c per contract after fees; the binding
constraints are quote quality in 2022-24 (wide hourly spreads seen in the probe: bid 0.20 / ask 0.89 at 23:00 UTC)
and the 2025-26 crowding (practitioner bots trade exactly this), which a forward log must decide.

## Venue access (information only)
To be checked: whether a Vietnam resident can open a Kalshi account (CFTC-regulated DCM; non-US access unclear).

## Amendment (Sat Oct 31 16:17 UTC 2026, before any analysis; data logistics only)
- The archive has no series filter (`series_ticker` returns nothing): events are fetched by constructed ticker
  `<SERIES>-YYMONDD`, 1 request per event + 1 per bracket. The keyless API returns 429 above ~4 req/s, so the pull
  is capped at 4 req/s and, to stay within the ~45 min budget, **subsampled to odd ordinal dates** (every other
  day; the ~60 events already fetched on even dates are kept). Coverage: HIGHNY / HIGHCHI 2023-01..2024-11 and
  HIGHAUS / HIGHMIA 2023-03..2024-11 (they start mid-2023), the `KX` successors 2024-10-15..2024-12-30, then
  HIGHNY 2021-07..2022-12 and HIGHCHI 2021-10..2022-12 (1-4 brackets per day then) as time allows.
- ISD truth for calibration: the station's SOD record (`24 HR MAX TEMP (F)`) per LST day, which matched Kalshi's
  `expiration_value` on the probe day (77 F, NYC 2023-06-15).

## Amendment 2 (Sat Oct 31 16:21:45 UTC 2026, ISD only, no Kalshi price looked at)
- SOD vs METAR on 2010-2021: the SOD (CLI-equivalent) max is below the day's max hourly/special METAR (integer F)
  on 0.3-1.5 % of days (rounding / QC), and below METAR max - 1 on 0.02-0.12 %. Rule (b) therefore uses a 1 F
  margin: a bracket is dead only if its upper bound < M_T - 1 (won: ">= X" with X <= M_T - 1). Saved in margin.json.
- The climatology confirms the mechanism's subtlety: at 17:00 LST in summer with the temperature still at its max,
  the final CLI max equals the hourly-METAR max only 17-30 % of the time (the CLI uses continuous ASOS data, usually
  1-2 F above the hourly reports). Rule (a) uses the fitted k distribution, not "max so far".
