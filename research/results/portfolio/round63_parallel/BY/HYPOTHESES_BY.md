# Stream BY hypotheses: independent-venue replication of B's cheap-basis rule on Bybit spot vs Bybit linear perp

Written 2026-10-31 16:46 UTC (from `date -u`), before any Bybit 1h or daily price kline was requested by this stream.
Nothing Bybit-specific has been computed yet (the existing research/data/bybit/ funding and perp 1d files were not
opened for returns or basis).

## What is frozen, what is new
- **The rule is frozen from stream B** (PREREG_B_cheap_basis.md, cell k100_H24_cheap, code B/code/basis.py
  `simulate(coins, 100, 24, -1)`). No parameter is chosen here: k = 100 bp, 168 h trailing median (>= 120 valid hours),
  exit at the open after the first close where the deviation has halved (median frozen at entry), else at the open of
  h+25; entry at the open of h+1; one open trade per coin; long perp / short spot (margin borrow), 1 unit each leg.
  The BY code imports B's `simulate`, `reltick`, `cl_t`, `summarize`, `by_year` unchanged and only supplies Bybit
  coins and the Bybit cost function.
- **Bybit HOLD (2025-01-01..2026-10-29) has not been seen** by anyone: never requested (every request ends at
  2024-12-31 23:59:59.999 UTC) and every series is cut at ts < 2025-01-01 at load.
- Binance's HOLD for the same rule has been seen (+213.5 bp, t 14.4). The Bybit HOLD covers the same calendar days and
  largely the same coins and squeeze events, so it is **not an independent sample of the time dimension**. Expected
  correlation of daily P&L (sum by entry day) with B's Binance trades: about 0.5-0.7 on days where both trade (the
  big days are market-wide alt squeezes / crashes that hit spot books on both venues: TRB 2023, LUNA, FTX week),
  lower (~0.3) over all days because each venue also has its own stale-spot / thin-book events. Bybit trades will
  be partly the same (coin, hour) events. A Bybit HOLD pass would therefore be expected with high probability given
  Binance's pass (my guess ~75 %), and would mostly test the venue-specific part (fees, Bybit spot book, Bybit
  funding), not the time stability. This is stated so the coordinator can weigh a Bybit HOLD accordingly.

## Mechanism (unchanged from B, plus what BX found)
Perps lead, the alt spot book lags during one-sided perp flow (liquidations, squeezes); the basis converges mostly by
spot catching down to the perps (BX: the Bybit perp is as cheap as the Binance perp at B's signals, corr of hold
returns 0.998). If this is a general "perps lead thin spot" effect it should replicate on Bybit's own spot book vs its
own perp. If it is a Binance spot-book artefact (stale Binance closes, Binance-specific flow), it should not.

## Data (Bybit public v5 API, no key; requests end 2024-12-31 23:59:59.999 UTC)
- /v5/market/instruments-info (category=linear and spot): symbol lists, spot `marginTrading` field (today's snapshot,
  used as the borrow proxy only; not point-in-time). Also status=Closed for linear if the API serves it (delisted
  perps; survivorship is reported).
- /v5/market/kline interval=D, category=linear for every candidate USDT perp (point-in-time turnover ranking) and
  category=spot for the matching spot pair (spot-live dates).
- /v5/market/kline interval=60, both categories, for each coin ever in the universe, from 8 days before its first
  universe day to 2 days after its last (as B). Bybit 1h klines have no trade count.
- Funding: research/data/bybit/funding/ (252 symbols) and /v5/market/funding/history for missing ones.
- Fed funds research/data/rates/DFF.csv. Saved under research/data/bybit_basis/ with requests.log.
- Pull budget <= 45 min; spacing >= 0.15 s between requests (Bybit documents 600 requests / 5 s per IP for public
  market endpoints, so this is far inside it), back off on 418 / 429 / 503 / retCode 10006, stop on 403. If the
  estimated request count exceeds the budget, subsample coins by a fixed seed (declared then, before any basis is
  computed) and report it.

## Universe (Bybit analogue of B's)
Point-in-time top-60 Bybit USDT linear perps by trailing 30-day perp turnover (previous day's universe, as B), listed
>= 60 days, with the Bybit spot pair (X/USDT, 1000X / X1000 / 1000000X perps mapped to spot X with the factor) live
that day (spot daily kline exists on or before the day), BTC / ETH / stablecoins / BTCDOM-type / PAXG / XAUT excluded.
Half-spread rank = Bybit turnover rank.

## Validity filter (substitution, declared now)
B required >= 20 trades per leg per hour. Bybit klines carry no trade count, so a bar is valid when both legs have
turnover >= 2,000 USDT in the hour and high > low (at least two prices traded); plus B's relative-tick filter
unchanged (tick / median close <= 5 bp per 30-day block, both legs) and positive closes. This is the only rule
substitution; it is fixed before data.

## Costs (Bybit, taker)
Spot taker 0.10 % x 2 + linear taker 0.055 % x 2 = 31 bp, plus 4 x half-spread (3 bp for rank < 10, else 5 bp) ->
43-51 bp per round trip; borrow 40 %/yr pro rata on the short spot leg; Fed funds on the spot notional; Bybit funding
stamps in (entry, exit] charged / received on the long perp. Costs x1.5 and one hour late (entry at h+2) checks.

## Grading (B's bars; one frozen cell, so no max-over-cells null)
IS 2020-21 (expected thin: Bybit alt USDT perps mostly listed from 2021-09, Bybit spot alt pairs from 2021; if IS has
< 30 trades or < 10 event-days it is reported as too thin to grade, i.e. the DEMO / LIVE IS bar is not met), VAL
2022-24. Net bp per trade, median, t clustered by entry UTC day, per year, share of years positive, x1.5, one hour
late, matched random benchmark (same coin, era, hold, side; 1,000 reps), power at VAL size, decomposition into
price-leg / funding / costs / carry, coverage per year (coin-hours valid, universe members with spot), correlation
of daily P&L with B's Binance trades on overlapping days (and trade-level overlap: same coin, entry within 2 h).
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, beats >= 95 % random, power >= 3, positive at x1.5 and late.
- DEMO: IS t >= 2.0, VAL net > 0, beats >= 90 % random, positive at x1.5 and late.
If it passes, PREREG_DRAFT_BY_cheap_basis.md with a HOLD pass bar of net > 0 and t (day cluster) >= 2.0 on the Bybit
HOLD; the HOLD is not opened here.

## Power arithmetic (before data)
HOLD ~1.8 yr. B's VAL per-trade Sharpe 0.270. If Bybit's VAL gives n_VAL trades over 3 years at per-trade Sharpe s,
power = s x sqrt(1.8 x n_VAL / 3). With s = 0.27: n_VAL >= 206 (~70 / yr) gives power >= 3; with s = 0.15 it needs
n_VAL >= 667. Day clustering binds: B had ~48 event-days / yr; power per event-day is reported too and the smaller
is graded. Which bar is reachable: IS will likely be too thin for LIVE (IS t >= 2.5 needs a few hundred IS trades at
B's Sharpe, Bybit IS is ~2021-Q4 only), so **LIVE is very unlikely to be reachable and DEMO only if IS has enough
trades**. A VAL pass alone is a venue replication (information for B's DEMO), not a new tier.

## Addendum 1 (written 2026-10-31 17:27 UTC, after the graded run; information only, the grade is not changed)
The graded run showed that on Bybit 1h klines the open of every bar equals the previous bar's close (100 % of
universe hours, both legs; on Binance only ~32-37 %, the open there is the first trade of the hour). So B's frozen
"enter at the open of h+1" is, on Bybit, an entry at exactly the signal-bar closing prints that define the
dislocation: not executable, an upper bound. The graded one-hour-late check (open of h+2 = close of h+1) is the first
executable price in the hourly data. To measure what survives a realistic reaction time, an information-only check
(never graded, cannot rescue the verdict): for every graded IS / VAL trade, pull Bybit 1m klines of both legs around
entry and exit and re-price the same trades (same entry hour, same exit hour from the hourly rule) with entry and exit
at the close of minute m of the hour, m = 1, 5, 15 (i.e. ~1 / 5 / 15 minutes after the hourly print), same costs.
