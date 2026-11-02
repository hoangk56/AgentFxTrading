# Stream K hypotheses: Upbit (Korea) flows -> Binance USDT-M perps

Written 2026-11-01 08:57 UTC (`date -u`), before any premium, return or trade statistic was computed. At this time
only metadata had been read: Upbit's current market list (299 KRW markets), the first daily kline of each local
Binance perp file (to find which Upbit coins had a perp before 2025), and two probe candles from 2019 to check
Upbit's timestamp format. HOLD (2025-01-01..) is never requested or loaded: Upbit requests end at
`to=2025-01-01T00:00:00Z` (exclusive), every series is cut at ts < 2025-01-01 at load.

## Data
- Upbit quotation API (public, no key). `api.upbit.com/robots.txt` = 404 (no robots file) at 08:53:07 UTC, logged.
  Requests >= 0.26 s apart (shared lock, 3 threads because each request takes ~0.7 s), back-off on 418/429/503,
  403 = stop. Log: research/data/upbit/requests.log.
- Universe: the 139 coins with a current Upbit KRW market and a Binance USDT-M perp whose first kline is before 2025
  (map in research/data/upbit/raw/map_perp.json; PEPE / SHIB / XEC map to the 1000x perps, scale removed).
  BTC is the hedge, USDC is excluded (stablecoin), so 137 alts.
- **Deviation from the brief, declared now:** the brief asks for 1h closes. A 60-minute pull measured 1.2 req/s
  (0.7 s latency) and needs ~14.5k requests (~3.3 h, over the ~45 min budget). K1 therefore uses **Upbit 240-minute
  candles** (aligned to 00/04/08/12/16/20 UTC) and Binance 1h closes sampled at the same 4h boundaries. K2 uses
  60-minute Upbit candles only around each listing (one request per listing) to find the first KRW hour.
- Binance: perp 1h klines from local files (binance_basis/perp_1h, binance/perp_1h, binance_1h_full) or fapi REST
  for missing symbols (saved to research/data/upbit/binance/); funding from local funding files or fapi
  /fapi/v1/fundingRate; 1m klines for entry / exit prices from fapi REST (alts) and data.binance.vision monthly 1m
  zips (BTCUSDT perp), all ending 2024-12.

## Eras
IS 2020-01-01..2021-12-31 (K2 also uses 2019-12 events if any), VAL 2022-01-01..2024-12-31. HOLD closed.

## K1: coin-specific Korean premium
Mechanism: Korean capital controls stop KRW arbitrage, but a coin can still be shipped from Binance to Upbit. A coin
rich in Korea relative to BTC's own kimchi premium is Korean retail demand for that coin. Arbitrageurs who can move
coins buy on Binance (a dated buying flow), and the attention spills to global venues. Prior: the gap mostly closes
through the Upbit price falling (Makarov-Schoar: the global market is larger), and many large gaps are wallet
suspensions where nobody can arbitrage, so a small Binance-side drift is the realistic best case.

Definitions (4h bucket b, start t, end T = t + 4h; all four candles must exist in b):
- `r(b) = ln(U_coin / U_BTC) - ln(B_coin / B_BTC) - ln(scale)`, U = Upbit KRW close (last trade in the bucket),
  B = Binance perp close of the 1h bar ending at T. No FX needed.
- Liquidity / staleness filter: Upbit coin KRW value in the bucket >= 40 M KRW (about 10 M KRW per hour), else the
  bucket is not a signal or exit-check point.
- Name-collision guard (e.g. Upbit TON = Tokamak, old vs new BTT): drop a coin entirely if the median of |r| over all
  its pre-2025 buckets is > 20 %.
- Two signals: **RAW** `s = r`; **DEV** `s = r - m`, m = median of r over the previous 42 buckets (168 h, need >= 30).
- Long cells (declared side): when `s > k`, long the alt perp, short BTCUSDT perp, equal USD notional (beta 1).
  Exit at the first later bucket end where s has halved (RAW: `r <= r_entry / 2`; DEV: `r - m_entry <= s_entry / 2`,
  anchor frozen at entry), or at entry + H. One open trade per coin; trades in different coins may overlap.
- Short cells (the side when `r < -k`, declared now as the mirror flow: coin cheap in Korea -> coins shipped from Upbit
  and sold on Binance): `s < -k`, short alt perp / long BTC perp, same exit logic mirrored.
- Grid: k in {200, 500} bp x H in {24, 72} h x signal {RAW, DEV} x side {long, short} = 16 cells.
- Entry / exit prices: the close of the 1m bar that starts at the bucket end T (signal and exit checks use bucket
  closes; the trade is filled 1 minute later on both legs). "One step late": the close of the 1m bar starting at
  T + 5 min, and a pure 1h version (fill at the close of the next 1h bar, T + 1 h).
- Decomposition per trade: change in r = (Upbit leg change) - (Binance leg change); report the share of the closed
  gap that came from the Binance leg (the only part we earn).
- Robustness only (not new cells): trailing beta (60 days of 4h returns) instead of beta 1; excluding March 2020 and
  May 2021.

## K2: Upbit KRW listings of coins that already have a Binance perp
Mechanism: an Upbit KRW listing creates a Korean retail attention pump that spills onto Binance; it overshoots and
fades once Korean demand is met. Side fixed: short the Binance alt perp, long BTCUSDT perp, equal notional.
- Event: L = start of the first Upbit KRW 60-minute candle of a coin whose Binance perp's first daily kline is >= 7
  days before L. Coins whose KRW history starts before our pull floor (2019-12-20 or perp start - 8 d) are not
  events. One event per coin.
- Entry at the close of the 1m bar starting at L + 1 h (the end of the first KRW hour); late checks L + 1 h + 5 min
  and L + 2 h. Exit at entry + 24 h or + 72 h (1m bar close). Grid: 2 cells (hold 24 / 72 h).
- Report the pre-entry run-up (Binance alt vs BTC from L - 24 h to entry): announcements precede the KRW open.

## Costs (per trade, both legs perps)
Taker 5 bp per side per leg (4 fills = 20 bp) + half-spread proxy per fill: alt 5 bp (K2: 10 bp, listing hour), BTC
1 bp -> K1 32 bp, K2 42 bp round trip. Funding of both legs charged / credited at the real stamps between entry and
exit. Robustness: costs x1.5, late fills. Perps need margin only, so no cash-rate excess is charged (no fully paid
spot leg); noted in the report.

## Statistics
Net bp per trade (equal weight), t clustered by entry day (sum per day). Years positive (2020..2024). Random
benchmark: K1, for each trade, a random entry time of the same coin in the same calendar quarter, same side and the
same holding length (time exit), 500 draws of the whole trade set; percentile of the actual mean. K2: (a) other
universe alts at the same entry time (same hedge, same hold), (b) the same coin at random times 30-180 days after
listing; 500 draws. Max-over-cells null: K1 16 cells, K2 2 cells -> report the expected max |t| of 16 correlated
cells (~2.0-2.4 under the null) alongside the best cell. Parameters chosen on IS only, VAL unchanged; C3 daily-P&L
correlation for any cell reaching DEMO numbers.

## Power arithmetic (before building)
HOLD is ~1.83 years. LIVE needs `S x sqrt(n_HOLD) >= 3`, S = net per-trade Sharpe at VAL size, n_HOLD = VAL rate x
1.83 / 3.
- K1: a 24-72 h alt-vs-BTC hold has sd ~500-900 bp. If VAL yields ~300 trades/yr (n_HOLD ~550), LIVE needs S >= 0.13,
  i.e. net >= ~65-115 bp per trade; at ~50 trades/yr (n_HOLD ~90) S >= 0.32, net >= ~160-290 bp. Day clustering (Korean
  frenzy days hit many coins at once) cuts the effective n, so the bar is higher than this. Given the prior that the
  gap closes on the Upbit side, DEMO is the realistic best; LIVE only if the Binance leg carries > 1/3 of a 500 bp gap.
- K2: Upbit listed perhaps 15-30 such coins a year 2020-24 (n_HOLD ~30-50 if the pace held). The 24-72 h alt-vs-BTC
  sd after a listing pump is ~1000-2000 bp and round 60 showed squeeze tails, so LIVE needs S >= 0.42-0.55 (net >=
  ~500-1000 bp per trade): out of reach in practice. K2 can at most reach DEMO.

## Biases from Upbit's current-only market list (declared)
Coins delisted from Upbit before 2026-11 are missing (their candles cannot be found from /v1/market/all), and so are
renamed markets' old codes (e.g. MATIC -> POL). Selection on survival to 2026 is a look-ahead filter:
- K1 long: surviving coins are the Korean "winners"; dropped coins (warning-designated, delisted) had Korean dumps
  (r < 0) and Binance underperformance. Bias: flatters the long side and the short (r < -k) side loses its strongest
  episodes (delisting dumps). Treat a long-side pass as optimistic.
- K2 short: listings later delisted from Upbit (often coins that faded) are missing; the survivors faded less. Bias:
  against the short (conservative).
