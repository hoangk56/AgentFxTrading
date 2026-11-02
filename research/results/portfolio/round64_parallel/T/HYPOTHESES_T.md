# Stream T hypotheses: USDT-M perp delisting convergence (round 64)

Written Sun Nov 1 09:07:59 UTC 2026 (from `date -u`), before any 1m price, gap or return of a delisting window was
requested or computed. Known before writing: round 63 D's count of perps whose last kline is before 2025 (dates only):
2020 1, 2021 2, 2022 8, 2023 0, 2024 12 (IS 3 / VAL 20), and two news items with lead times (STEPN / NEAR / AVAX BUSD
perps: notice 2023-04-14 ~13:00 UTC, settlement 04-18 09:00, ~92 h; XEM / ORBS / LOOM: notice 2024-11-28 ~23:00 UTC,
settlement 12-09 09:00, ~250 h; both say "no new positions from 30 min before settlement").

## 1. Mechanism
When Binance delists a USDT-M perp, all open positions are closed by automatic settlement at a price tied to the index
(a composite of spot venues) at a time fixed by the announcement; from T - 30 min only reducing orders are allowed.
Holders who cannot or will not keep the position to settlement (or fear ADL / settlement noise) exit early, and market
makers withdraw, so in the final day(s) the perp can trade away from spot. The settlement rule pins the perp to the
index at T: a wedge with a hard anchor at a known time. A trader who holds both legs to T collects the wedge open at
entry minus whatever residual remains at T (the index is not Binance spot alone).

## 2. Events (declared filter, applied to dates only)
- Perps in research/data/binance/perp_1d (886 incl. delisted) whose last 1d kline is in 2020-01-01..2024-12-31
  (loaded with ts < 2025-01-01; a file whose data runs past 2024-12-31 counts as "alive", nothing past the cut is read
  or printed), no `_` (quarterlies) in the name.
- The coin's Binance spot pair (USDT, factor prefixes 1000 / 1000000 / 1M mapped as in carry.spot_name) must have
  1m klines covering [T - 8 d, T] (T = end of the last perp 1m kline), i.e. spot still trading at settlement.
- Excluded: contract roll-overs / ticker changes / redenominations where the perp ended because the symbol was
  replaced (perp relisted under a new name within 30 days, e.g. a 1000-prefix or rename), listed by name in STREAM_T
  with the reason, decided from names and dates before computing returns.
- Delisting time T = close time of the last perp 1m kline (data.binance.vision futures/um daily 1m).

## 3. Entry time vs. announcement look-ahead
The announcement time is not available (Binance /bapi/ banned by robots, HTML behind a JS challenge, round 63 D).
Declared entry: E = T - 24 h (open of the 1m bar starting there). It is valid only if every announcement preceded
T - 24 h. Verification plan: for each event (or event batch, same T), find the announcement date from public news /
GitHub sources (<= 15 WebSearches in total, shared with mechanism lookups); classify each event as "lead verified >=
24 h", "lead verified < 24 h" (event dropped from the graded set, reported) or "unverified" (kept; the bias is stated:
emergency delistings with short leads, e.g. the 2022-05 LUNA and 2022-11 FTX-era cases, are the ones most likely
to have < 24 h lead and are also the most dislocated, so an unverified emergency event could create look-ahead).
Sensitivity (information only): E = T - 6 h and E = T - 48 h.

## 4. Rules (side fixed by the sign of the gap; no borrow)
Gap at entry g = mean over the five 1m closes ending at E of ln(P_perp / (factor x P_spot)) (both legs need >= 1
trade in the minute, else that minute is skipped; >= 3 valid minutes required).
- T1 (rich): g > k: short perp / long spot (equal USD notional), hold to settlement.
- T2 (cheap): g < -k: long perp, short BTCUSDT perp (equal USD notional), hold to settlement. Reported separately; it
  carries the coin's spot move (information: the long-perp / short-spot P&L that would need a borrow, not graded).
- Grid: k in {0, 50, 100} bp x {T1, T2} = 6 cells, entry T - 24 h. Max-over-cells random null reported.
- Exit (declared): perp at the close of its last 1m kline (a trader can close manually up to T; reduce-only after
  T - 30 min), spot / BTC perp at the open of the 1m bar starting at T (or the last available close <= T).
  Alternative exit (information): perp at the settlement proxy = mean of factor x spot 1m closes over [T - 30 min, T].
- Funding of the perp leg (and BTC perp for T2) at real stamps in (E, T] from data.binance.vision fundingRate monthly
  files (or local binance/funding). The spot leg is fully paid: charge nothing extra but report the excess over the
  cash rate (DFF) for the ~1 day of capital (~1 bp).

## 5. Costs
Taker perp 5 bp per side, spot 10 bp per side (2020-24 schedule): 30 bp per round trip for T1; T2 perp 5 x 2 + BTC
perp 5 x 2 = 20 bp. Half-spread proxy 10 bp per leg-side for the delisting coin (illiquid in its final days) and 1 bp
for BTC: T1 30 + 40 = 70 bp, T2 20 + 20 + 2 = 42 bp. Checks: costs x1.5, entry one 1m bar late (E + 1 min), and the
measured jump proxy |open(E) - close(E - 1m)| reported next to the 10 bp assumption.

## 6. Statistics and bars
Net bp per trade, t clustered by settlement day (events delisted in one batch share a day), years positive, random
benchmark: for each event, 1,000 draws of a random entry hour in [T - 7 d, T - 48 h] on the same coin, the gap rule
recomputed at that time (side from data), exit 24 h later at market (perp and spot both at the 1m open), same costs and
funding; p = share of random cell means >= the actual mean. IS 2020-21, VAL 2022-24, cut at 2025-01-01. Bars as in
BRIEF (LIVE / DEMO), not lowered. Also reported: unconditional gap path (median / mean / IQR of g) at T - 72 h ..
T in hourly steps, all events.

## 7. Power arithmetic (before building)
- HOLD 2025-01..2026-10 event count is not looked at. Estimate from VAL / 2024 rates: ~7 / yr (VAL mean) to ~12 / yr
  (2024) -> ~12-22 HOLD events, fewer in a cell with k > 0 (say half). LIVE needs HOLD power = per-trade net Sharpe x
  sqrt(n_HOLD) >= 3: per-trade Sharpe >= 3 / sqrt(22) = 0.64 at best, 3 / sqrt(12) = 0.87, 3 / sqrt(6) = 1.22 for a
  half-size cell. B's mechanical convergence gave 0.5-0.7, so LIVE would need a stronger wedge than B.
- IS: D counts 3 events in 2020-21. t >= 2.0 (DEMO) at n = 3 needs a per-trade Sharpe >= 2.0 / sqrt(3) = 1.15 and
  t clustered with 3 clusters is meaningless. Declared: a cell with fewer than 5 IS trades cannot be graded at IS and
  gets "none (structural: IS sample)" whatever its VAL numbers; VAL is then reported descriptively, and the user
  decision that could unlock it is an event-specific era split (as D proposed). This bar is stated now, not after.
- VAL: n ~ 20 (less per cell). Net > 0 is the DEMO VAL bar; t >= 1.5 LIVE VAL bar needs per-trade Sharpe >= 0.34 at
  n 20.

## 8. Data plan
research/data/binance_delist/ with requests.log (time, URL, status, bytes). robots.txt of data.binance.vision checked
and logged first. Per event: futures/um daily 1m klines of the perp for [T - 8 d, T], spot daily 1m for the same
days, BTCUSDT perp daily 1m for those days (T2), fundingRate monthly files for the months covered. Only files dated
<= 2024-12-31. >= 0.3 s between requests, back off on 418 / 429 / 503, stop on 403. Parse with `python -I`.
