# Round 43 stream M: hypotheses (investor-mood shocks -> local index CFDs and currency)

Written 2026-10-30 05:29 UTC (`date -u`), before any weather / football / pollution series was joined to a price.
Data loaded so far: football results (counted below, no prices), ISD-Lite files being downloaded (not parsed).
HOLD 2025-01-01..2026-09-24 closed: IC M1 cut ts < 1735689600000 at load, weather files requested only for years
<= 2024, football rows with date > 2024-12-31 dropped at parse.

## Sources (declared)
- **Weather (W)**: NOAA ISD-Lite hourly, station-year files, from the NOAA open-data bucket that NCEI's
  `/pub/data/noaa/isd-lite/` page now fronts: `https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/<Y>/<USAF>-<WBAN>-<Y>.gz`
  (no login). NCEI robots.txt disallows `/data*`, so the Global Hourly "access" CSVs (`/data/global-hourly/access/`)
  are NOT used. Field: total sky cover code (ISD-Lite field 10). Stations (main airport, ICAO):
  New York KLGA 725030-14732, London EGLL 037720-99999, Frankfurt EDDF 106370-99999, Paris LFPO 071490-99999,
  Madrid LEMD 082210-99999, Milan LIML 160800-99999, Tokyo RJTT 476710-99999, Hong Kong VHHH 450070-99999,
  Sydney YSSY 947670-99999 (Beijing ZBAA 545110 and Shanghai ZSSS 583670 for the P stream). Years 2004-2024.
- **Football (F)**: martj42/international_results, `https://raw.githubusercontent.com/martj42/international_results/master/results.csv`
  and `shootouts.csv` (dated men's international results; date = venue date; no kick-off time). Cross-check two known
  results before use (Brazil 1-7 Germany 2014-07-08; England 1-2 Iceland 2016-06-27).
- **Pollution (P)**: the US State Department AirNow files (dosairnowdata.org) do not resolve from this Mac (DNS,
  2 tries); UCI's five-city PM2.5 set ends 2015 (no IC index data then). Declared by-product instead: **morning haze
  from airport visibility** in the full ISD files (same bucket, `.../data/<Y>/<station>-<Y>.gz`, mandatory-section
  visibility and dew point) for Beijing ZBAA, Shanghai ZSSS, Hong Kong VHHH, 2010-2024. Haze index = mean over local
  hours 06-08 of -ln(visibility km), using only observations with RH < 90 % (fog / rain excluded; CMA haze
  definition uses RH < 80-90 %); deseasonalised by calendar month with the 2010-2015 climatology.

## Prices, sessions, costs
- IC M1 (bid c, ask ca): US500 (US30, USTEC info), UK100, DE40, JP225, HK50, AUS200; bid-only zbars with IC's
  published fixed spreads (round 7): F40 1.79 pt, ES35 4.2 pt, IT40 9.0 pt; USDCNH zbars 2.93 pip + 0.6 bp.
  FX for currency cells: IC M1 GBPUSD, EURUSD, USDJPY, AUDUSD (+0.6 bp commission); PRE 2004-15 Dukascopy
  (EURUSD, USDJPY m1; GBPUSD, AUDUSD m1c), cost = IC 2016-17 spread by minute of day + 0.6 bp.
- Local cash session, DST-aware (zoneinfo): entry at the open of minute open+1, exit at the close of the bar at
  close-5 min: NY 09:31-15:55 ET; London 08:01-16:25; Frankfurt / Paris / Madrid / Milan 09:01-17:25 CET;
  Tokyo 09:01-14:55 JST (15:00 close through 2024); Hong Kong 09:31-15:55 HKT; Sydney 10:01-15:55 AEST/AEDT.
  Second horizon "first hour": open+1 -> open+60. Two-session hold (F only): open+1 -> next session close-5,
  overnight cost 2 bp a night either side (conservative).
- Cost = half spread at entry + half at exit (M1 ca - c), or the fixed published spread; x1.5 and +1 minute run
  for every graded cell.

## W. Sunshine / cloud cover (Saunders 1993; Hirshleifer & Shumway 2003)
Mechanism: sunshine raises mood and risk appetite of local traders; cloudy mornings lower it. Information-free.
- Signal: mean total sky cover (oktas; ISD codes 0-8 as oktas, 9 obscured -> 8, 10 partial obscured -> missing,
  11-13 scattered -> 4, 14-16 broken -> 6, 17-19 overcast -> 8) over local hour labels open_h-3..open_h-1
  (NY / Europe / Tokyo / HK 06-08, London 05-07, Sydney 07-09; an hour label covers obs within +-30 min, so every
  obs used is >= 30 min before entry). Missing -> no trade. Deviation dev = cover - clim(station, ISO week), clim
  from 2004-2015 (out of sample for IS / VAL; leave-one-year-out inside PRE).
- **Side (fixed): sunny (dev < 0 / low cover) -> LONG the local index; cloudy -> SHORT.**
- Cells: signal S1 sign(dev) every day; S2 terciles (long bottom, short top, thresholds = station's 2004-15
  tercile of dev); S3 quintiles; S4 raw HS categories (long cover <= 2 oktas, short >= 7). x horizon
  {open->close, first hour} = **8 book cells** (equal weight across the 9 cities: US500, UK100, DE40, F40, ES35,
  IT40, JP225, HK50, AUS200). **Primary: S1 open->close book.** 72 single-city cells reported as information.
  Currency info cells (S1, local session, side: sunny -> local currency up): London -> GBPUSD long, Frankfurt+Paris
  mean -> EURUSD long, Tokyo -> USDJPY short, Sydney -> AUDUSD long; IS / VAL and PRE 2004-15 (4 cells).
- Count: ~250 sessions / year / city; S1 ~2,250 city-days a year, ~1,500 book days in IS, ~750 VAL, ~440 HOLD.
- Expected size: HS 2003 NYC perfectly sunny vs cloudy ~16 % a year apart (~6.4 bp a day between extremes); a sign
  rule earns maybe +-1.5-2 bp a day per city around the mean against an open-to-close sd ~80-120 bp: per-trade
  Sharpe ~0.02. With independent weather signs across 9 cities, book day Sharpe ~ 3 x 0.02 = 0.06.
- Power: LIVE needs HOLD power = day Sharpe x sqrt(440) >= 3 -> book day Sharpe >= 0.143 (per-city per-trade
  ~0.048), i.e. ~2.4x the literature size NET of a 1-4 bp round trip; IS t >= 2.5 needs book day Sharpe >= 0.065.
  At literature size before cost IS t ~2.3, HOLD power ~1.3. **LIVE out of reach unless the effect is >2x the
  published one; DEMO possible only at full literature size.** Decay since 2003 is expected (Goetzmann & Zhu 2005
  found no trading by sunny individuals; later replications weak): report by era and year.

## F. Football losses (Edmans, Garcia & Norli 2007)
Mechanism: a national team loss in an important match lowers mood of local investors -> next-day local index down
(EGN: WC losses ~-38 bp, WC elimination ~-49 bp, other continental cups smaller; wins nothing).
- Event: a competitive match (T1: FIFA World Cup, UEFA Euro, Copa America, AFC Asian Cup, Confederations Cup,
  Gold Cup; T2: WC / Euro / Asian Cup qualification, UEFA / CONCACAF Nations League, EAFF Championship; friendlies
  excluded) lost in regular / extra time or on penalties (shootouts.csv). Elimination = the team's last match of
  that tournament edition and a loss.
- Timing without kick-off times: the result is assumed known at venue-date 24:00 local (standard offset of the
  venue country, the westernmost for multi-zone countries) + 2 h, in UTC. Entry = first local cash open after that
  (weekend matches -> Monday). Multiple losses of one country on one session = one trade.
- **Side (fixed): SHORT the loser's index** (England UK100, Germany DE40, France F40, Spain ES35, Italy IT40,
  Japan JP225, Australia AUS200; info: United States US500, Hong Kong HK50).
- Cells: tier {T1+T2, T1 only, eliminations only} x country set {EU5, EU5+JP+AU} x horizon {1 session open->close,
  2 sessions} = **12 cells**. **Primary: T1+T2, EU5, 1 session.** Info: US, HK; currency (short GBPUSD for England,
  short EURUSD for a euro-country loss, long USDJPY for Japan, short AUDUSD for Australia; local session) IS / VAL
  and PRE 2004-15 (2 cells: EU5 FX, all FX).
- Count (computed from the CSV, no prices): EU5 losses T1 3.0 / yr IS, 3.7 VAL; T2 3.7 IS, 5.7 VAL;
  EU5+JP+AU all tiers ~57 IS (9.5 / yr), ~38 VAL (12.7 / yr); PRE 2004-15 EU5 60, +JP/AU 107.
- Power: HOLD (21 months incl. the 2026 World Cup) ~20-25 losses -> LIVE needs per-trade Sharpe >= 0.6-0.67;
  EGN's size (-38 bp / ~100 bp sd) = 0.38 before decay. **LIVE impossible from the count; DEMO needs IS t >= 2,
  i.e. per-trade Sharpe >= 0.26 on 57 IS trades (>= 0.39 on 27 T1 trades).**

## P. Air pollution (morning haze) -> HK50 / USDCNH (Levy & Yagil 2011; Li, Massa, Zhang & Zhang 2021;
Wu, Lu & Wang 2018 on Chinese pollution and returns)
Mechanism: heavy pollution lowers mood / raises risk aversion of local investors -> lower same-day returns.
- Signal: haze index (above) deseasonalised; mainland = mean of Beijing and Shanghai z-scores; HK = VHHH alone.
- **Side (fixed): high haze -> SHORT HK50; low haze -> LONG HK50; USDCNH: high mainland haze -> LONG USDCNH (CNH
  weaker), info only.**
- Cells: source {mainland, HK} x rule {sign, quintiles} x horizon {open->close, first hour} = **8 cells**;
  **primary: mainland quintiles open->close.** +2 USDCNH info cells (mainland quintiles, 01:31-07:55 UTC).
- Count: quintiles ~100 trades / yr -> IS ~600, VAL ~300, HOLD ~170: LIVE needs per-trade Sharpe 0.23 (literature:
  a 1-sd pollution shock ~-5..-10 bp vs HK50 sd ~120 bp -> 0.05-0.08): **LIVE impossible; DEMO needs per-trade
  Sharpe >= 0.082 net on IS.**

## Grading (all families)
Day-clustered t (book = equal-weight mean of the day's trades), by year, IS 2016-21 / VAL 2022-24, PRE where data
exist; with and without 2020-03/04; x1.5 spread; +1 minute on entry and exit. Random control (>= 200 seeds): W / P
recompute the side from a randomly permuted signal (signal days shuffled within station-year) on the same sessions;
F uses random sessions of the same country, month and weekday mix, short. Chance benchmark: best-of-N |t| for
N = 8 (W), 12 (F), 8 (P) book cells (max of N normals p50 / p95 ~1.4 / 2.4 for N 8, ~1.6 / 2.6 for N 12), plus a
day sign-flip permutation for the W book.

## Amendment 1 (2026-10-30 05:37 UTC, before any return was computed)
ISD-Lite's total sky cover (field 10) is missing for most of 2014-24 at Tokyo RJTT (<= 11 days a year), Frankfurt
EDDF (<= 41) and London EGLL (99-133 a year in IS), because those stations send METAR without a total-cover group.
The W signal is therefore built from the **full ISD files** (same bucket, `.../data/<Y>/<station>-<Y>.gz`) for all 9
stations 2004-24: per observation, total cover = GF1 total coverage if present, else the maximum layer coverage of
GA1-GA6 (oktas) or GD1-GD6 (summation 0 clear, 1 FEW = 2 oktas, 2 SCT = 4, 3 BKN = 6, 4 OVC = 8, 5 obscured = 8),
else 0 when the report is CAVOK or its METAR remark says NSC / SKC / CLR / NCD; ISD codes mapped to oktas as above.
Observations are labelled by nearest hour (time + 30 min, floored) in local time; the same pre-open hour labels,
rules, cells, side and grading as declared above. No other change.

## Amendment 2 (2026-10-30 05:58 UTC, before any W return was computed; F and P were graded already)
The full-ISD cover has station level shifts from changes in report mix (per-year mean oktas, data only: HKG
~5.2 in 2004-07 vs ~3.1-3.4 from 2011; LON 5.0 / 4.4 in 2004-05 vs ~3-4 after; MIL / FRA ~1 okta lower after 2017;
TYO drifting up). A 2004-15 weekly climatology alone would then put most IS days of a station on one side (a beta
position, not a mood signal). **W deviation, final:** dev = cover - clim(station, ISO week, 2004-15) minus the
trailing 365-day mean of that deviation (days d-365..d-1, >= 100 days required): known before the open, removes
report-mix shifts within a year. Tercile / quintile thresholds from the 2004-15 distribution of this dev. All
rules, cells, sides and grading unchanged; the un-adjusted version (amendment 1 only) is reported once as a
robustness line, not as an extra cell.

## W2 (added 2026-10-30 05:58 UTC after W / F / P failed; declared before any W2 return): temperature and wind
Related by-products of the same ISD-Lite files (already downloaded, years <= 2024): pre-open temperature (field 5)
and wind speed (field 9), same stations, hour labels, sessions, costs and trailing-adjusted weekly deviation as W.
- T (Cao & Wei 2005, "Stock market returns: a note on temperature anomaly"): **cold (dev < 0 / bottom quintile) ->
  LONG, hot -> SHORT** the local index.
- WIND (Shu & Hung 2009, wind and European index returns): **windy (dev > 0 / top quintile) -> SHORT, calm -> LONG.**
- Cells: {T, WIND} x {sign, quintiles (2004-15 thresholds)} x {open->close, first hour} = 8 book cells
  (equal weight, 9 cities). Primary: T quintiles open->close. Same grading; best-of-8 chance benchmark.
- Expected: published sizes ~1-3 bp a day vs the 2.7 bp round trip of an open->close trade measured in W:
  none expected; LIVE out of reach as for W (book day Sharpe >= 0.143 needed).
