# Round 71, stream D3: funding-formula asymmetries on other venues

Written 2026-11-01 18:01 UTC (`date -u` at 18:00:51), before any return, funding-difference or price-difference series
was computed. Data seen so far: venue docs and robots (logged in research/data/funding_formulas/requests.log), one
OKX funding file (BTC-USDT-SWAP 2021-09, to learn the columns; first rows read), one page of Bybit inverse funding
(2020-01, format), one OKX daily-candle page (2021-06..09, format), and Kraken chart pages (row counts / first
timestamps only, to find where history starts). No series has been summarised.

## Formula table (2020-24), sources and change dates

| Venue / contract | 8h-equivalent rule | interest leg | damper / clamp | interval, cap | source (raw copies under research/data/funding_formulas/raw/docs/) | change dates |
|---|---|---|---|---|---|---|
| Binance USDT-M | F = P + clamp(0.01 % - P, +-0.05 %) | **0.01 %/8h** | yes (+-0.05 % around the anchor) | 8h for BTC / ETH; symbol caps | secondary descriptions (binance.com support sits behind the /bapi/ family we avoid, as D2); realised stamps local | none known for BTC / ETH 2020-24 (some alts moved to 4h in 2023-24: stamps used as realised) |
| Binance COIN-M | same | 0.01 %/8h | yes | 8h | first local stamps = 0.000100 (binance_cm/cm_funding_dapi) | none known |
| Bybit linear / inverse | F = P + clamp(I - P, +-0.05 %) | 0.01 %/8h (both) | yes | 8h | api.bybit.com probe (BTCUSD inverse stamp 2020-02-01 = 0.0001); www.bybit.com help not reachable (connection error, not a block) | none known |
| BitMEX XBTUSD | F = P + clamp(I - P, +-0.05 %), I = (USD 0.06 % - XBT 0.03 %)/3 | 0.01 %/8h | yes | 8h | BitMEX perpetual guide via WebSearch (page is a JS app); **API returned 403 on 2026-11-01 17:5x: stopped, no BitMEX request after that** | none found |
| Hyperliquid | F = P + clamp(0.01 % - P, +-0.05 %), paid hourly at 1/8 | 0.01 %/8h | yes | 1h, cap 4 %/h | hyperliquid.gitbook.io trading/funding (hl_funding.txt) | venue from 2023 |
| **OKX** (USDT and USD swaps) | **F = clamp(MA(premium - 0), cap, floor)**, premium = (best bid + best ask)/2 / index - 1 | **0 (stated "Interest rate = 0")** | **none** | 8h, per-symbol cap | OKX announcement 2024-01-25 "OKX to optimize funding rate calculation" (okx_optimize.txt) | 2024-03-05 08:00 UTC: MA window changed from "since period start" to "last N hours" (interest still 0). The current page (okx_mechanism.txt) shows 0.01 % interest + +-0.05 % clamp + impact prices: per secondary sources this came ~2025-04 (**unverified**, after VAL) |
| **Kraken Futures** PI_ (inverse), PF_ (linear, 2022+) | hourly rate = TWAP premium / n, premium = impact mid / index - 1 | **none** | **none** ("no dampening") | until 2022-09-29 12:00 UTC: 4h window, n = 8, cap +-0.1 %/h; after: 1h, n = 24, cap +-0.25 %/h | support.mtf.kraken.com art. 7009378818333 (pre-2022 method), support.kraken.com art. 360022835911 (current) | 2022-09-29 (window / n / cap) |
| Deribit | premium with +-0.025 % zero band, no interest | none | zero band | — | D2 (not repeated) | — |

Venues whose rule has **no interest leg** in 2020-24: OKX, Kraken, Deribit (D2). All others carry the same 0.01 %/8h
anchor, so pairs among them (Bybit linear vs inverse, Binance COIN-M vs USDT-M, BitMEX vs any, Hyperliquid vs CEX) have
no structural term (round 59 B1 / B2 type) and are not tested.

## Data limits found (decide what is testable)
- **OKX realised funding**: public monthly files via /api/v5/public/market-data-history (module 3) exist only from
  **2021-09** (2020-01..2021-08 returned no files). OKX daily candles (history-candles, 1Dutc) reach at least 2021-06.
- **Kraken realised funding**: /historical-funding-rates returns only the last 8,760 hours (from 2025-10): nothing
  before 2025. Charts API: trade candles from 2020-02-26, mark / spot (index) candles from somewhere in 2021 (2021-01
  empty, 2022-01 present). So Kraken has no realised 2020-24 funding and no IS: **descriptive only** (reconstructed
  premium = hourly mark / spot - 1, from the earliest available month to 2024-12; not a cell).

## Mechanism and side (fixed before data)
Binance longs pay 0.01 %/8h whenever the premium sits within (-0.04 %, +0.06 %); OKX longs pay only the realised
premium. Long the OKX USDT swap / short the Binance USDT-M perp, equal coin quantity, collects the anchor unless
OKX's premium settles near +0.01 %/8h (arbitrage absorbs it) or the two perps' prices drift apart. Both legs are
USDT-linear: no coin collateral, the hedge is exact in coin units.

**Up-front caveat on HOLD and live use:** OKX's current rule carries the same 0.01 % anchor (from ~2025-04 per
secondary sources). The structural term therefore exists in at most the first ~3 months of HOLD and not today. Any
IS / VAL pass on this pair cannot be traded live; it would only tell whether a no-anchor leg earns the anchor, which
transfers to Kraken (still no interest leg) and Deribit (D2). P(LIVE) for the pair itself ~ 0.

## Cells (6, fixed now)
Assets {BTC, ETH, B10} x rules {ON, F7}:
- B10 = equal weight over BTC ETH SOL XRP DOGE ADA LTC LINK BCH DOT (largest coins listed as USDT perps on both venues
  by 2021; list fixed by size, not by data); a coin enters when both venues have funding + a close.
- **ON**: always on.
- **F7**: on (per coin) when the mean of (Binance funding - OKX funding) over holding days d-8..d-2 is > 0 (all stamps
  known >= 8 h before the mark), off otherwise.

Eras: IS 2021-09-01..2021-12-31 (OKX data start; 122 days), VAL 2022-01-01..2024-12-31. Every series cut at
ts < 2025-01-01 at load; the 2025-01-01 00:00 funding stamp is dropped on both venues (2024-12-31 then has 2 stamps).

## Construction
- Daily mark at 00:00 UTC = close of the 1d candle (Binance perp_1d close, OKX 1Dutc close). Holding day d runs
  from the mark at 00:00 of d to 00:00 of d+1; its funding = stamps in (00:00 d, 00:00 d+1] on each venue.
- Per coin notional N_i (N = 1 for the book). Short q coins Binance, long q coins OKX, q = N_i / Binance close at
  entry; resize both legs when |q x close - N_i| > 20 % N_i (taker on the traded amount, both venues).
- r_d = sum_i q_i [ (F_OKX,d - F_OKX,d-1) - (F_BIN,d - F_BIN,d-1) + f_BIN,d x P - f_OKX,d x P ] / N - costs, with the
  funding paid on notional at the stamp (close of the day used for P; error is second order).
- Capital: leverage L = 2 per venue, equity N/2 at each, C = N. Venue equity re-balanced by a USDT transfer when it
  leaves [0.5, 1.5] x N/2 (cost 1 bp of the amount; assumed instant: optimistic). Days where one leg's intraday
  adverse move (1d high / low vs previous close) exceeds 45 % are reported as liquidation risk.
- Off state (F7): flat on both venues, capital idle at the venue (still charged the cash rate in the excess).

## Costs
Taker 0.05 % per side on each venue + half spread 0.01 % (BTC / ETH) or 0.03 % (other B10 coins). Entry and exit of
the book charged inside each era. Checks: costs x1.5; one day late (signal and entry / exit shifted by one day).

## Grading
- Daily book return, Newey-West t (lag 10, round 58 `stats`).
- Excess over cash: r_d - DFF_d x C / N with C = N (L = 2), plus L = 3 (C = 2/3 N) as sensitivity. DFF from
  research/data/rates/DFF.csv.
- Bars (brief): LIVE t_IS >= 2.5, t_VAL >= 1.5, >= 2/3 of years positive, random >= 95 %, HOLD power >= 3 at VAL
  size; DEMO t_IS >= 2.0, VAL net > 0, random >= 90 %. Added (round 59 / D2 rule): excess over cash > 0 with
  t >= 1.5 in IS and VAL. Net > 0 at costs x1.5 and one day late.
- Random: F7 = circular shifts of each coin's on/off mask (500 draws, same costs); ON has no timing (random side = minus
  the book; stated as weak). Max-over-cells null: joint stationary block bootstrap (mean block 20 d, 1,000 draws) of
  the 6 demeaned cell series in IS, distribution of the max t.
- Decomposition: funding leg (f_BIN - f_OKX), price leg (perp-perp basis change), costs.

## Power
IS 122 days: t >= 2.5 needs annual Sharpe >= 2.5 / sqrt(122/365) = 4.3; t >= 2.0 needs 3.5. VAL 1,096 days: t 1.5
needs Sharpe 0.87. HOLD ~667 days: power >= 3 needs Sharpe >= 2.22 (and the structure vanishes in ~2025-04, see
caveat). A funding gap of ~6 %/yr at ~2 %/yr vol would pass IS / VAL; if OKX premiums absorb the anchor the gap is
~0 and the price leg adds noise. Prior: P(DEMO-level IS / VAL pass) ~ 5 %, P(LIVE) ~ 0 (not tradable now).

## Kraken (descriptive only, no cell)
Hourly mark and spot (index) candles for PI_XBTUSD / PI_ETHUSD from the first available month to 2024-12. Reconstructed
daily funding paid by a long = sum over hours of clamp(TWAP premium / n) with the regime of the date (n = 8 per hour on
4h windows before 2022-09-29 12:00 UTC, n = 24 per hour after), premium approximated by hourly close mark / spot - 1.
Reported: mean reconstructed Kraken funding vs Binance realised funding by year (bp per day), as evidence on whether a
no-anchor premium sits above zero. Not graded.

## Amendment 2026-11-01 18:09 UTC (`date -u` 18:08:44), before any return or funding-gap series was computed
**Data gap found:** OKX's monthly funding files exist for 2021-09 and then from 2022-01-16 (2021-10..2022-01-15
absent, daily "ANY" files also absent; listing checked, no file offered). Realised OKX funding therefore covers 30 IS
days only. Change:
- **IS uses reconstructed OKX funding** for 2020-01..2021-12 (the realised stamps replace it where they exist,
  i.e. 2021-09): under OKX's documented pre-2024-03 rule (interest 0, no damper), the stamp at T = mean over
  (T - 8h, T] of the premium; premium per hour = close of the OKX swap 1H trade candle / close of the OKX index 1H
  candle - 1 (OKX /market/history-candles and /market/history-index-candles, both public; index history from
  2020-01-2x). Calibration of the estimator **on the IS month 2021-09 only** (realised vs reconstructed: mean, corr,
  and lag 0 vs one-period lag, the choice fixed there); the VAL fit (2022-24, realised vs reconstructed) is reported
  as a check and never used to choose.
- If OKX's rule in 2020-21 differed (e.g. had an interest leg), the reconstruction misstates IS funding: the 2021-09
  realised month is the only evidence and is reported.
- VAL keeps realised OKX funding (2022-01-16..2024-12-31; 2022-01-01..15 use the reconstruction too, flagged).
- OKX daily marks for 2020-21 = close of the 23:00 1H trade candle. Cells, costs and bars unchanged.
- B10 coins enter IS when OKX trade + index candles and Binance data exist.
