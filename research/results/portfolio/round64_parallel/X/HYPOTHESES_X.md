# Stream X hypotheses: cross-venue spot wedge, long cheap Binance spot (round 64)

Written 2026-11-01 09:12 UTC (from `date -u`), before any new venue price was requested and before any signal or
return was computed. HOLD (2025+) is never requested or loaded: every request ends at 2024-12-31 23:59:59 UTC and
every series is cut at ts < 2025-01-01 at load.

## Mechanism
Binance spot carries venue-specific order flow (it is the largest alt spot book, the leg every Binance basis / funding
/ liquidation trade hits). Stream V found at B's signal hours that Binance spot sat 10-17 bp (median) above Bybit /
OKX / KuCoin spot and then fell back toward them: the other venues' spot acted as an anchor (cross-venue arbitrage by
market makers who hold inventory on several venues; they need no borrow to close a gap, only inventory and
transfers). The no-borrow side of this wedge: when Binance spot is CHEAP versus the other venues (a Binance-specific
selling flow), buy Binance spot, hedge with a short Binance USDT-M perp (delta neutral), and earn Binance spot catching
up. The perp only hedges the coin's market move.
Not B / BX: B's signal is the perp-spot basis; here the signal is Binance spot vs other venues' spot. The trade
(long spot / short perp) is the same direction as B's rich side, so the overlap with B's rich-side signal is reported
and the result without it.

## Side (fixed before data)
- Graded rule: Binance spot cheap (D < -k) -> long Binance spot, short Binance USDT-M perp, equal USD notional.
- Mirror (information only, needs borrow, never graded): Binance spot rich (D > +k) -> short spot, long perp.

## Data
- Binance spot 1h: research/data/binance_basis/spot_1h (B's 246-symbol universe), perp 1h: binance_basis/perp_1h,
  funding: data/binance/funding or binance_basis/funding (B's loader `B/code/basis.py`, imported read-only).
- Other venues' spot 1h, base coin vs USDT (USD for Coinbase):
  - Bybit spot: reuse research/data/bybit_basis/spot_1h (round 63 BY) where it covers; pull the missing spans from
    api.bybit.com /v5/market/kline (category=spot).
  - OKX: www.okx.com /api/v5/market/history-candles (bar=1H, 100 bars per request).
  - KuCoin: api.kucoin.com /api/v1/market/candles (type=1hour, 1500 per request) (used by stream V).
  - Coinbase Exchange: api.exchange.coinbase.com /products/<BASE>-USD/candles (granularity 3600, 300 per request);
    converted to USDT with Coinbase USDT-USD 1h close where it exists, else 1. Kraken is skipped (its public OHLC
    endpoint serves only the last 720 bars, so no 2020-24 history).
  - Coin list per venue from each venue's current public instrument list (venues do not serve delisted pairs:
    survivorship, see bias note). Pull span per coin: from its first universe day - 8 days to its last universe day
    (B/universe60.csv), end <= 2024-12-31 23:59:59 UTC. If OKX at 100 bars / request exceeds ~45 min, restrict OKX to
    the universe-membership windows only.
- Binance 1m klines (spot from data-api.binance.vision /api/v3/klines, perp from fapi.binance.com /fapi/v1/klines) for
  [signal close - 3 min, exit + 20 min] of every trade in the k60 / k100 cells, and of a seed-0 random subsample of up to
  1,500 trades per era for each k30 cell if it has more.
- Data folder research/data/xvenue_spot/ with requests.log (UTC time, URL, status, bytes). robots.txt of every host
  read and logged first; 403 = stop that host; back off on 418 / 429 / 503; >= 0.25 s between requests to one host.

## Data cleaning (fixed, not fitted on strategy returns)
- Per coin x venue: scale = median(venue close / Binance spot close) over the overlap rounded to a power of 10
  (1000SHIB-type names); a venue x coin x calendar-year is dropped if its hourly log-return correlation with Binance
  spot is < 0.5 (ticker reused for another coin, e.g. LUNA after 2022-05) or it has < 500 valid hours.
- A venue bar is valid only if its volume > 0 and |ln(scaled venue close / Binance close)| < 10 %.
- Binance spot bar: B's validity filters (>= 20 trades in the hour, relative tick <= 5 bp, close > 0).

## Signal
For venue v and hour h: r_v(h) = ln(P_v(h) x scale_v / S(h)) (close-to-close, both stamped by open time, hour h's
close). m_v(h) = median of r_v over the previous 168 h (>= 120 valid hours, else venue v unusable at h).
d_v(h) = r_v(h) - m_v(h); D(h) = median over usable venues of d_v(h); require >= 2 usable venues (fixed). Positive D
means the other venues sit above Binance more than usual, i.e. Binance is cheap. Sign used below and in code:
G(h) = -D(h) (the Binance-vs-others deviation); cheap signal G(h) < -k, mirror G(h) > +k. Universe: B's point-in-time top-60 USDT-M perps with a spot
pair (previous day's membership), BTC / ETH excluded (as B).
- Entry: signal at the close of hour h (time T = start of h+1). Both legs enter at the open of the Binance 1m bar
  starting at T + 1 min (primary). One coin holds at most one position.
- Exit: the first hour close c in [e, e + H) where G recomputed with the entry-hour references m_v(h) (median over
  venues valid at c, >= 1) satisfies G(c) >= G(h) / 2 (gap halved); exit at the 1m open at (c + 1 h) + 1 min. Else exit
  after H hours at the 1m open H hours + 1 min after T. Fallbacks: B's (next bar with both opens within 24 h; delisting
  = last valid bar, flagged forced).
- Grid (6 cells, declared): k in {30, 60, 100} bp x H in {6, 24} h. IS-chosen cell = highest IS day-clustered t at
  the primary entry among cells with IS net > 0. All 6 cells reported, plus the max-over-6-cells random null.

## Costs (per unit notional, round trip)
Binance spot taker 10 bp a side + USDT-M perp taker 5 bp a side = 30 bp; half-spread proxy 4 legs x (3 bp if the coin's
previous-day universe rank < 10 else 5 bp) = 12-20 bp (B's `hs_of`); total 42-50 bp. Funding on the short perp at the
real stamps in (entry, exit] (received when positive). Cash cost on the fully paid spot leg: Fed funds (DFF) x hours /
8760 (graded on the excess over cash). Robustness: costs x1.5; entry one 1m bar later (T + 2 min); information: T + 5,
T + 15 min, the 1h-open entry (open of h+1) and one hour late (open of h+2).

## Bars and tests
Common bars of the brief (IS > 0 and VAL > 0 net, positive at x1.5 and one bar late, t clustered by entry UTC day,
>= 2/3 years positive for LIVE). Random benchmark: B's matched random entries (same coin, same era, same hold length,
same side, 1,000 reps) priced at 1h opens, compared with the signal's own 1h-open pricing (like with like); max-over-6-
cells null of t. Overlap with B: share of X trades whose coin had B's rich-side deviation (perp-spot basis minus its
168 h median) > k at the signal hour or the hour before / after; results with those trades removed. Also: gap closure
split (Binance spot leg vs the venue median's move over the hold) and the perp-hedge leg; ex crash windows (2020-03,
2021-05-17..24, 2022-05, 2022-11) as information. C3 daily-P&L correlation for any cell reaching DEMO numbers.

## IS thinness rule (declared now; applied from signal counts only, before any return is computed)
Bybit spot starts mid-2021 and the other venues lack many 2020 alts. After the pull I count signals only (no returns) in
IS for the k60_H24 cell. If it has < 30 trades or < 10 distinct entry days, the split becomes DISCOVERY 2020-01-01..
2022-12-31 (parameters chosen there) and TEST 2023-01-01..2024-12-31 (checked unchanged); the count and the split are
written into an addendum here before computing returns.

## Power arithmetic (HOLD 2025-01..2026-10 ~ 1.83 years)
Power = per-trade net Sharpe (at VAL size) x sqrt(1.83 x VAL trades per year) >= 3 for LIVE. Needed per-trade Sharpe:
20 trades / yr -> 0.50; 50 / yr -> 0.31; 100 / yr -> 0.22; 300 / yr -> 0.13. Expected shape: V's 10-17 bp median
anchoring is below the 42-50 bp wall, so only k >= 60 can clear costs; if the gap reverts by ~half of k = 60-100 bp the
gross is 30-50 bp, near the wall: k30 cells are expected to fail on costs, k100 cells are the realistic ones, and they
need either >= ~50 trades / yr at SR >= 0.31 or ~100 / yr at SR >= 0.22. A B-like mechanical convergence (SR 0.5-0.7)
would reach power 3 with 20-40 trades / yr. Prior odds: DEMO ~10 %, LIVE ~3 % (thin venues produce stale prints, so many
"Binance cheap" readings will be the other venues being stale, which carry no P&L for a Binance-only trade).

## Bias notes
- Survivorship: venue APIs serve only currently listed pairs, so anchors exist only for coins still listed on those
  venues; trades are on Binance, so P&L is real, but the coin set leans toward survivors (biases toward fewer delisting
  crashes; the hedge with the perp neutralises most of the coin move).
- Venue closes are last trades in the hour: stale prints on thin venues bias D toward noise; the >= 2 venue median and
  the 1m entry after the signal are the guard.

## Addendum 1 (2026-11-01 10:03 UTC, from `date -u`; signal counts only, no return computed yet)
Pull finished 10:01 UTC (25,168 x 200; 36 x 429 from OKX backed off and retried; 0 rows >= 2025). Usable-venue
coverage of universe coin-hours with >= 2 venues: 2020 49.5 %, 2021 56.7 %, 2022 48.6 %, 2023 51.9 %, 2024 70.4 %;
181 / 244 coins have at least one usable venue (out/count.txt). IS signal count for k60_H24 cheap: 746 trades on 246
days (>= 30 trades and >= 10 days), so the **main split IS 2020-21 / VAL 2022-24 is used**; the alternative split is
not used. Operational change: OKX was pulled by 3 parallel workers (each >= 0.3 s between its requests, ~4-5 req/s
combined, under OKX's documented 20 requests / 2 s for history-candles) to keep the pull under ~45 min.
