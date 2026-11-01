# Round 63 stream C: intraday cross-sectional books on Binance USDT-M perps (hypotheses)

Written 2026-10-31 14:29 UTC (from `date -u`), before any 1h data was pulled or any return computed.
Eras: IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31. Every series is cut at ts < 2025-01-01 at load; HOLD
(2025-01-01..2026-10-29) is never opened by this stream.

## Mechanism
1. Short-term cross-sectional reversal (C-REV, primary side: long losers / short winners). Liquidity provision:
   uninformed order-flow pressure (liquidations, retail chasing, index / basket flows) pushes a coin away from the
   basket for hours and is absorbed by market makers who need a premium; the price drifts back (Jegadeesh 1990,
   Lehmann 1990, Nagel 2012 "Evaporating liquidity"). Crypto perps have heavy liquidation cascades, so the premium may be
   larger than in equities.
2. Intraday momentum (C-MOM, declared alternative, opposite side: long winners / short losers). Slow diffusion of
   coin-specific news / listings / unlocks across venues; positive feedback trading.
3. Volume-conditioned (Llorente, Michaely, Saar, Wang 2002; Campbell, Grossman, Wang 1993): moves on LOW abnormal volume
   are liquidity-driven and reverse (C-VLO: reversal among coins with below-median volume surprise); moves on HIGH
   abnormal volume are information-driven and continue (C-VHI: momentum among coins with above-median volume surprise).
   Sides fixed now; the opposite pairings are not tested.
4. Funding-stamp split (reported only, not a rule): rebalances at 00 / 08 / 16 UTC versus the other hours.

## Data
- Universe source: research/data/binance/perp_1d (1d klines, quote volume). Symbol list to pull: every USDT-M perp that
  was in the top 60 by trailing 30-day quote volume (listed >= 60 days, stablecoin / commodity / stock bases excluded as
  in round 60 EXCL_BASE) on any day 2020-01-01..2024-12-31. If that exceeds ~150 symbols, keep those ever in the top 40
  first (the trading universe is the top 40, so every ever-top-40 symbol must be present to avoid survivorship gaps),
  then fill by days in the top 60, cap ~150.
- 1h klines 2019-11..2024-12 from data.binance.vision monthly zips
  (data/futures/um/monthly/klines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip); REST fapi/v1/klines only to fill missing months,
  end time 2024-12-31 23:59:59 UTC. Saved under research/data/binance_1h_full/ with requests.log.
- Funding: research/data/binance/funding (and funding_window); symbols without full funding history get funding from
  fapi/v1/fundingRate with endTime 2024-12-31 23:59:59 UTC, saved under research/data/binance_1h_full/funding/.

## Rules (fixed before data)
- Universe each UTC day d: top N = 40 by trailing-30-day quote volume over days d-30..d-1, perp listed >= 60 days,
  1h bar present. Universe frozen for the whole day.
- Signal at the close of hour t: past J-hour return r_i = C_t / C_{t-J} - 1. Two signal flavours:
  (a) raw (ranking on raw returns = ranking on returns relative to the cross-sectional mean);
  (b) BTC-residual: r_i - beta_i * r_BTC, beta_i from the trailing 30 days (720 h) of hourly returns (OLS, shrunk 50 %
  to 1), computed with data up to t only.
- Book: rank the universe; long bottom q = 8 / short top q = 8 (C-REV) or the reverse (C-MOM); equal weight, $1 per
  side (dollar-neutral, gross 2). Return quoted per $1 of one side: mean(long legs) - mean(short legs).
- Rebalance every H hours on a fixed clock (hours with UTC hour % H == 0), hold H hours (non-overlapping books).
- Grid (small, declared): J in {1, 4, 24} x H in {1, 4, 24} = 9 cells per family x signal flavour.
  Families: C-REV and C-MOM (raw + residual: 9 x 2 each = 36 cells), C-VLO and C-VHI (raw only: 9 each = 18 cells).
  Total 54 cells. Volume surprise for C-VLO / C-VHI: quote volume over the last J hours divided by the coin's mean
  J-hour quote volume over the previous 30 days; split at the cross-sectional median, then q = 4 per side within the
  half (20 coins).
- Parameters (cell) chosen on IS by net day-clustered t; checked on VAL unchanged.
- Execution: primary = trade at the close of the signal hour (the last trade price of hour t); "one step late" = trade at
  the close of hour t+1 with the same signal (mandatory check). Information only: trade at the VWAP of hour t+1
  (qvol / vol), which removes last-trade bounce.

## Costs
- Taker 0.05 % per side + half-spread 0.01 % (BTC, ETH) / 0.03 % (rest of the top 20 by the day's volume rank) /
  0.05 % (others), charged on each leg's traded notional (turnover only: legs kept across rebalances pay nothing; legs
  are re-weighted to equal weight at each rebalance and the weight drift is ignored, a small understatement of cost).
- Funding: each held leg pays (long) / receives (short) the stamp rate if a stamp (00 / 08 / 16 UTC, or the symbol's
  stamp times in the file) falls strictly inside the hold or at its end (Binance charges positions open at the stamp).
  Missing funding -> 0 and the share of missing leg-stamps is reported.
- Costs x 1.5 must stay positive. Maker variant (0.02 % fee, no spread, fills assumed) reported as information only.
- Capital: $1 per side is mostly margin; the round-58 lesson (excess over cash) applies weakly here since a
  dollar-neutral perp book ties up only margin; report excess over DFF on $1 of capital per side as a footnote.

## Statistics and benchmark
- Book returns are summed per UTC day; t = day-clustered (mean / sd x sqrt(n_days) on daily sums), and Newey-West
  (lag 5) on the daily series; the smaller one is used for the bars.
- Random benchmark: at each rebalance the signal is permuted across the universe (shuffled ranks), 200 shuffles, same
  costs; report the percentile of the real net mean. Max-over-cells null: for each shuffle the max net t over all 54
  cells (IS), compared with the best real IS t.
- Years: 2020..2024 per-year net; LIVE needs >= 2/3 positive (>= 4 of 5).

## Power arithmetic (done before data)
HOLD = 2025-01-01..2026-10-29 = ~667 days. LIVE needs net Sharpe per rebalance (VAL size) x sqrt(HOLD rebalances)
>= 3. With n_H = 667 x 24 / H rebalances, the bar per rebalance is:
- H = 1: n = 16,008, Sharpe per rebalance >= 0.0237;
- H = 4: n = 4,002, >= 0.0474;
- H = 24: n = 667, >= 0.116.
All three equal an annualised net Sharpe of ~2.2 (0.0237 x sqrt(8760) = 2.22). More rebalances do not lower the bar by
themselves; they help only because an intraday edge diversified over 16 legs and thousands of hours can have a much
higher Sharpe than a weekly factor. With day clustering the effective count is days (667), so the bar is a daily net
Sharpe >= 0.116.

Cost hurdle per cell (expected before data): a full-turnover rebalance costs ~2 sides x 2 trades x (0.05 + ~0.04) %
= ~0.36 % of one side's notional; turnover per rebalance for J = H is probably 0.6-0.9 of the book. So
- H = 1 needs a gross ~25-30 bp per hour from a 1-hour sort: very unlikely; expected to reach no bar (maker variant only
  as information);
- H = 4 needs ~25 bp per 4 h, i.e. ~1.5 % per day gross: unlikely;
- H = 24, J = 24 needs ~25-30 bp per day gross with a daily gross sd of the 8/8 book of perhaps 2-3 %: the per-day
  Sharpe needed for LIVE (0.116 net) means a gross mean of ~0.55-0.65 % per day. Only DEMO looks reachable a priori, and
  only if the daily reversal premium in crypto is large.
These expectations are stated so a later pass cannot be read as a forecast confirmed.
