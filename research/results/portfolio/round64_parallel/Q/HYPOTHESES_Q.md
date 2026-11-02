# Stream Q hypotheses: derivative-vs-derivative basis on Binance (round 64)

Written Sun Nov 1 08:54:15 UTC 2026 (from `date -u`), before any price, gap or return was computed. Only the
data.binance.vision bucket listing (symbol names, file names) has been seen. HOLD (2025-01..2026-10) is never
requested: monthly files up to 2024-12 only, every series cut at ts < 2025-01-01 at load.

## Mechanism
Two Binance derivatives on the same coin share one anchor (the Binance spot index): a perp through its funding, a
delivery future through settlement on the index at expiry. Their holders differ: COIN-M (inverse, coin collateral:
miners and coin holders hedging, coin-margined leverage) vs USDT-M (linear, stablecoin collateral: most leverage);
quarterly basis traders vs perp leverage. A forced flow in one book (liquidation cascade in one margin type, hedgers
in the inverse book, quarterly roll) can push one contract away from the other; arbitrage between them needs no
spot and no borrow (both legs are derivatives on one venue, cross-collateral aside), so if a gap exists it should be
pulled back by the anchor. Unlike BX (spot is the mover, all perps move together), here the anchor acts on the
derivative itself. The honest prior: because this arbitrage needs no borrow, desks close it fast, so gaps above
costs may be rare, stale prints, or closed within the first minute (round 62 / B shape). The test is whether a
gap visible at an hourly close is still there and converges after a tradable delay.

## Side (fixed before data): fade the gap
Long the cheap contract, short the rich one, equal USD notional at entry. Never the other way.

## Data
- data.binance.vision futures/cm monthly klines 1h for every <COIN>USD_PERP (49 perps listed, incl. delisted LUNA,
  FTM, MATIC) and every COIN-M quarterly <COIN>USD_YYMMDD that expires <= 2024-12-27 (BTC, ETH from 200925; ADA,
  LINK from 200925; BCH, BNB, DOT, LTC, XRP from 201225; EOS, ETC, FIL, TRX 201225 / 210326 only; SOL 240927 /
  241227). COIN-M funding: futures/cm monthly fundingRate.
- futures/um monthly klines 1h for BTCUSDT_YYMMDD / ETHUSDT_YYMMDD (210326..241227).
- USDT-M perps 1h: research/data/binance_basis/perp_1h (already local); missing coins from futures/um monthly 1h.
  USDT-M funding: research/data/binance/funding, binance_basis/funding, else futures/um monthly fundingRate.
- 1m klines (futures/cm and futures/um daily or monthly zips on data.binance.vision) for the entry / exit days of the
  trades of the declared cells, both legs (pulled after the 1h screen; the 1h screen is used only to know which
  days to pull, grading uses 1m prices).
- Settlement prices: dapi / fapi public `/futures/data/delivery-price` (no key), fallback = mean of the
  quarterly's 1m closes over the last 30 min before expiry (Binance settles on the 30-min average index).

## Rules
Common: hourly closes, a bar is valid when both legs have >= 20 trades in the hour and price > 0. Signal at the close
of hour h (time T = end of hour h). Universe: every coin with a COIN-M contract and a USDT-M perp at the same time.
- **Q1 (COIN-M perp vs USDT-M perp).** g = ln(P_cm_perp / P_um_perp). Residual d = g - median(g over the previous 168
  valid hours, >= 120 needed). If |d| > k: long the cheap leg / short the rich leg. Exit at the first hourly close
  where |g - m_h| <= |d|/2 (same side; reference median frozen at the signal), else after H hours. One trade per coin
  at a time.
- **Q2 (delivery future vs USDT-M perp).** For every quarterly q (COIN-M <COIN>USD_YYMMDD and USDT-M BTC / ETH
  quarterlies) b = ln(F_q / P_um_perp), tau = years to expiry, annualised a = b / tau. Term premium removed with the
  trailing median of a: residual d = b - median(a over the previous 168 valid hours, >= 120) x tau. Enter only
  while tau >= 3 days; exit when the residual (with the frozen median a_ref: b - a_ref x tau) has halved, else after
  H hours, and in any case no later than 2 hours before expiry. One trade per contract at a time (current and next
  quarter can both trade: day-clustered t takes care of the overlap).
- **Q2b (last-24 h convergence).** At the close of the hour ending exactly 24 h before expiry (expiry 08:00 UTC on
  the last Friday of the quarter month), b = ln(F_q / P_um_perp). If |b| > k: short the rich / long the cheap, hold
  to delivery: the quarterly leg is settled at the delivery price, the perp leg is closed at the 1m open at expiry +
  1 min (funding stamp at expiry included). No trailing median (the anchor is 0 at expiry).

## Grid (15 cells, declared; the parameter choice is made on IS only)
- Q1: k in {30, 60, 100} bp x H in {24, 72} h = 6 cells.
- Q2: k in {30, 60, 100} bp x H in {24, 72} h = 6 cells.
- Q2b: k in {10, 20, 30} bp = 3 cells (hold fixed to delivery).
The reported null is the max over all 15 cells of the random-entry t (per era).

## Execution and costs
- Base entry: both legs at the open of the 1m bar starting at T + 1 min (one full minute after the hourly close,
  tradable). Exit: both legs at the open of the 1m bar starting at X + 1 min, X = the hour boundary after the exit
  close. Late check: entry at T + 2 min (one 1m bar later), exit unchanged. Information only: T + 5 min.
- Fees: taker 5 bp per side per leg (entry + exit, 2 legs = 20 bp round trip; the delivery leg of Q2b also pays 5
  bp, conservative). Half-spread per side per leg: USDT-M perp BTC / ETH 0.5 bp, other 2 bp; COIN-M perp BTC / ETH 1
  bp, other 3 bp; USDT-M quarterly 1.5 bp; COIN-M quarterly BTC / ETH 2 bp, other 5 bp. Checked against the median
  |open(T+1m) - close(T)| jump on 1m bars at the signal. Costs x1.5 reported.
- Funding: stamps in (entry, exit] on both perps at their real rates (COIN-M and USDT-M), signed by the side.
  Quarterlies have no funding.
- P&L in USD per unit notional: the inverse leg's USD P&L, with its coin P&L converted at the exit price, equals
  N x (P_exit / P_entry - 1), identical to a linear leg, so equal-notional legs stay hedged. What drifts is the coin
  collateral of the COIN-M leg (long coin); it is assumed hedged by a standing USDT-M short of the same size, which is
  not part of the trade (stated, not charged). No spot leg, no borrow, no cash-rate charge (margin only).

## Statistics and bars
IS 2020-01-01..2021-12-31 (COIN-M perps exist from 2020-08, quarterlies from 2020-07), VAL 2022-01-01..2024-12-31.
t clustered by entry UTC day. Random benchmark: same coin / contract, same era, same hold length, random valid hour,
side recomputed at the random hour as the fade of the sign of the residual there, 1,000 replications; beat % =
share of replications with a lower mean. Bars as in BRIEF (LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive,
>= 95 % random, x1.5 and late > 0, power >= 3; DEMO: IS t >= 2.0, VAL net > 0, >= 90 % random).

## Power arithmetic (before data)
HOLD is ~1.83 years. Power = per-trade net Sharpe (VAL size) x sqrt(n_HOLD), n_HOLD ~ 1.83 x VAL n / 3.
- Power 3 needs n_VAL_per_year >= 9 / (1.83 x SR^2): SR 0.5 -> 20 trades / yr; SR 0.3 -> 55 / yr; SR 0.15 -> 220 / yr.
  With day clustering the relevant count is independent signal days.
- Q1 (~10-30 coin pairs): per-trade SR of a mechanical wedge ~0.3-0.6 (B: 0.27 per trade, 0.5 per day). LIVE is
  reachable if k30 / k60 fire >= ~50 independent days / yr after the delay; k100 is likely too rare.
- Q2: similar arithmetic; the COIN-M alt quarterlies are thin, BTC / ETH quarterlies tight (gaps above 30 bp after
  removing the term premium should be rare except in crash hours).
- Q2b: at most ~4 expiry days / yr (all trades of an expiry share one day cluster): ~12 VAL clusters, ~7 HOLD
  clusters. Power 3 would need a per-expiry-day Sharpe >= 1.1; LIVE is effectively out of reach, DEMO at most.
Expected outcome (prior): gaps above ~30 bp between two Binance derivatives are rare and mostly in crash hours; the
first minute after the close may already remove them. A "none" is the likely answer; the test is cheap.

## Addendum 1 (Sun Nov 1 08:57:25 UTC 2026, from `date -u`; before any price was loaded or computed; only the pull of
1h files is running)
- Settlement price: the `/futures/data/delivery-price` endpoints have no end-time parameter and would return
  2025-26 deliveries (HOLD), so they are not used. Settlement = mean of the quarterly's 1m closes over the last 30
  minutes before expiry (08:00 UTC), from data.binance.vision daily 1m files (<= 2024-12).
- Bad-print guard (round 63 BM pitfall, 2024-10-28 21:00 UTC): a signal counts only if, for both legs, the 1h close
  equals the close of the last 1m bar of that hour within 1 bp. Signals without 1m data for either leg are dropped
  (reported).
- Random benchmark price source: the random entries and the actual trades are compared on the same price source
  (1h opens of the entry / exit hours, as B did), because 1m data is pulled only around actual trades; the rule
  itself is graded on 1m prices (T + 1 min).
- Q2b random benchmark: same contract, entry at a random hour between 72 h and 2 h before expiry, side = fade of the
  sign of b at that hour, hold to delivery, same costs.

## Addendum 2 (Sun Nov 1 09:01:16 UTC 2026, from `date -u`; only trade COUNTS
of the 1h screen on partially downloaded data were seen, no P&L)
The 1h screen gives thousands of trades (Q2 k30-k60: > 1,000 per era on partial data), i.e. ~10-20k (symbol, day)
1m files: over the ~45 min pull budget. Declared sequence, before any P&L is computed:
1. Grade all 15 cells on 1h opens (entry at the open of hour h+1, exit at the open of hour x, as B did); this is
   the screen and the random benchmark's price source.
2. Pull 1m data for (a) every trade of each family's (Q1, Q2, Q2b) best IS cell by 1h-open t and of any cell with
   IS 1h-open net > 0, capped by a random sample of 400 trades per cell and era (seed 64) if larger; (b) a random
   sample of 150 trades per era of every other cell, to measure the 1h-open -> 1m (T+1 min) translation.
3. The verdict uses the 1m (T+1 min) numbers where 1m data exists; a cell whose 1h-open IS net is <= 0 cannot pass
   (the 1m entry one minute after the hour open is not expected to be better; the sample in 2b checks this).
