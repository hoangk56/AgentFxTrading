# Stream R (round 65) hypotheses: Korean waking-hours rhythm on Upbit-heavy altcoins

Written 2026-11-01 11:37 UTC (from `date -u`), before any return (gross or net) was computed. Only data coverage
(which symbols have local 1h / funding files) was checked before this file: all 261 symbols ever in the point-in-time
top 60 of 2020-24 have a local 1h file; 3 (FOOTBALL, NU, TOKEN) have no funding file. HOLD (2025-01-01..) is never
loaded: every series is cut at ts < 2025-01-01 at load, and the last book day is 2024-12-30.

## Mechanism
Korean retail trades on Upbit during Korean waking hours (09:00-24:00 KST = 00:00-15:00 UTC) and is mostly absent
at night (15:00-24:00 UTC = 00:00-09:00 KST). Coins whose global volume is dominated by Upbit get net retail buying
pressure when Korea is awake (attention, chasing); at night, price discovery moves to Binance / global traders who
have no such bias and arbitrage the Korean-day premium back. Prediction: an altcoin's Upbit share of global volume
predicts a positive relative return in the Korean day and a negative one in the Korean night. Coins with a low share
show no such rhythm.

**Side, fixed now:** high-share coins outperform low-share coins 00-15 UTC and underperform 15-24 UTC. The night
books are short high-share; the day books are long high-share.

## Data (local, read-only)
- Upbit 240-minute candles, research/data/upbit/m240/<COIN>.csv (`krw` column = traded KRW value), 139 coins mapped to
  Binance perps by research/data/upbit/raw/map_perp.json (stream K). Buckets start at 00/04/08/12/16/20 UTC.
- Binance USDT-M perps: daily quote volume from binance/perp_1d (all 886 perps incl. delisted) for the universe; 1h
  closes from the earliest-starting local 1h file (binance_1h_full/1h, binance_basis/perp_1h, upbit/binance/perp_1h,
  binance/perp_1h; columns read by header name, since binance/perp_1h has `t,o,h,l,c,qvol` only); funding from local
  funding files (missing file = zero funding, reported).
- KRW -> USD: daily Upbit KRW-BTC close / Binance BTCUSDT perp close at the same 4h boundary (includes the kimchi
  premium; that is fine for a share).

## Definitions (all known before the day)
- Day d = UTC day. Universe(d): top 60 USDT-M perps by mean daily quote volume over days d-30..d-1, listed >= 60 days
  on Binance, excluding BTC (hedge leg), stablecoins (USDC, BUSD, TUSD, USDP, FDUSD) and index perps (DEFI, FOOTBALL,
  BLUEBIRD, BTCDOM).
- Share(i, d) = sum over days d-30..d-1 of Upbit KRW value / KRWUSD(day) divided by the sum of Binance perp quote
  volume over the same days. Measured only if the coin has Upbit candles on >= 20 of those 30 days and its first Upbit
  candle is <= day d-30 (excludes the first month after a KRW listing, which is K2's territory).
- Universe A (main): Universe(d) restricted to coins with a measured share (Upbit-listed coins). Universe B: all of
  Universe(d), share = 0 for coins with no Upbit KRW market on record (ties broken by a fixed per-day random order).
  A day is used only if the universe has >= 9 coins with an entry price.
- Terciles: high = top floor(n/3) by share, low = bottom floor(n/3). Equal weight within a leg, $1 per side.
- Prices: instant h = close of the 1h bar that opened at h-1 (round 63 C convention). The entry is a taker market order
  at that instant, priced at the close plus a half-spread cost (the close is a tradable last-trade price; no use of 1h
  opens). Exit likewise. Coins without a price at entry are dropped that day; missing exit prices are forward filled.

## Books (declared cells: 7)
| cell | universe | window (UTC) | position |
|---|---|---|---|
| A-N-LS | A | 15:00 -> 24:00 | long low tercile / short high tercile |
| A-D-LS | A | 00:00 -> 15:00 | long high tercile / short low tercile |
| A-N-BTC | A | 15:00 -> 24:00 | short high tercile / long BTCUSDT perp |
| A-D-BTC | A | 00:00 -> 15:00 | long high tercile / short BTCUSDT perp |
| A-FLIP | A | both | A-D-LS in the day, A-N-LS at night (positions flip at 00 and 15 UTC) |
| B-N-LS | B | 15:00 -> 24:00 | long low / short high (low = mostly non-Upbit coins) |
| B-D-LS | B | 00:00 -> 15:00 | long high / short low |

No parameter is chosen on IS: the windows are fixed by the Korean clock, the tercile and top-60 by the brief. The IS
pick (for reporting) is the cell with the highest IS t; the max-over-7-cells null is reported.

## First step (declared): the gross hour-by-hour profile, IS only
For every UTC hour h = 0..23 and IS day: gross 1h return (close-to-close, instant h -> h+1) of the universe-A high
tercile minus the low tercile, and high tercile minus BTC; mean in bp, day-clustered t. Also the cumulative profile
from 00 UTC. It is computed after this file and does not change the books above. VAL by hour is reported only as
information after the books are run.

## Costs
- Taker 5 bp per side per leg + half-spread (round 63 C model): BTC / ETH 1 bp, volume rank < 20 3 bp, else 5 bp, on
  |change in weight| (C's `book`). A separate day or night book trades in and out each day: ~4 x (5 + 4) = ~36 bp per
  day per $1 of one side for LS, ~30 bp for the BTC-hedged books; A-FLIP ~72 bp per day.
- Funding on held legs for stamps in (entry, exit] (night: 16:00 and 00:00; day: 08:00).
- Checks: costs x 1.5; one step late (enter and exit 1 h later: 16 -> 01, 01 -> 16).

## Statistics and bars
- Daily book (one return per day per cell): Newey-West t (lag 5) and day t, the smaller is used; years positive
  2020-24 (bar: >= 4 of 5 for 2/3).
- Random benchmark: 500 shuffled-share books (shares permuted among the day's universe, same costs, same days);
  percentile of the real mean net. Max-over-7-cells null: the same shuffle draw for all cells, max IS t.
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 4/5 years positive, >= 95 % random, positive at costs x 1.5 and one step late,
  HOLD power at VAL size >= 3. DEMO: IS t >= 2.0, VAL net > 0, >= 90 % random.

## Power arithmetic (before data)
HOLD = 2025-01-01..2026-10-29 = 667 daily book returns. Power = VAL daily net Sharpe x sqrt(667) >= 3 needs a daily
net Sharpe >= 0.116, i.e. an annual net Sharpe >= 2.2 (x sqrt(365)). IS t >= 2.5 over 731 days needs a daily Sharpe
>= 0.092. If the high-minus-low tercile spread has a ~200-300 bp sd over a 9-15 h window, LIVE needs ~25-35 bp of net
per day on top of ~36 bp of cost: a gross rhythm of ~60-70 bp per window. Prior: the rhythm, if any, is far smaller
(round 63 C's best intraday gross was +7.5 bp per hour of cross-sectional reversal); the likely outcome is a real
gross sign but no net book. A gross rhythm that is real but below cost is reported as such.

## Bias notes (declared)
- Upbit coins delisted or renamed before stream K's pull (e.g. LUNA, MATIC -> POL) have no candles: in universe A they
  are absent; in universe B they count as zero share (misclassified into the low tercile).
- High-share coins are smaller and higher beta than low-share coins; the LS books are not beta-neutral. Post hoc
  (information only): the correlation of each book with BTC's return over the same window.
- C3 correlation (trades_C3_gotobi_jpy_basket.csv) only for a cell with DEMO numbers.
