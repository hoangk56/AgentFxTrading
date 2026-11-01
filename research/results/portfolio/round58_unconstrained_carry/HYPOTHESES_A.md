# Round 58, stream A: delta-neutral perpetual funding carry (declared before any computation)

Written 2026-10-31 10:57 UTC (from `date -u`), before any funding / price series of this round was loaded.

## Why this round exists
On 2026-10-31 the user asked again to research until there is a LIVE bot, "lần này không có ràng buộc gì cả" (no
constraints this time). Read as: the fixed operational limits of research/PROMPT.md (hold <= 5 days, <= 3 positions per
bot, capital-independent lot) and the IC / cTrader-only venue no longer apply. The statistical LIVE bar is kept: it is
what "a LIVE bot" means.

The frontier after 57 rounds: every real effect is a few bp, below IC's spread + commission, and multi-week premia lose
to IC's overnight financing markup (rounds 9, 11). One family was never testable under the old limits: the
**perp-spot funding carry** on crypto exchanges (long spot, short the USDT-margined perpetual, collect funding,
hold weeks / months). Round 37 F used funding only as a minutes-ahead *directional* signal for BTCUSD at IC; no round
held a hedged spot-perp pair. It needs (a) a venue other than IC, (b) holds far beyond 5 days, (c) many concurrent
positions. All three are now allowed.

Economic basis: leveraged-long demand in crypto (retail, basis-insensitive) keeps perpetuals above spot; the funding
transfer pays whoever supplies the short side. Literature: He, Manela, Ross & von Wachter (2022) "Fundamentals of
perpetual futures" (spot-perp arbitrage Sharpe ~1.8 taker / higher maker, 2020-22); Schmeling, Schrimpf & Todorov
(2023, BIS WP 1087) "Crypto carry" (carry large, time-varying, crash-prone); the Ethena USDe product (2024-) runs this
exact trade at scale. Risk: basis blow-outs, negative-funding regimes, exchange / ADL risk, liquidation of the short
leg in a squeeze if margin is thin.

## Data (to pull, public, no key)
- Binance USDT-M perpetual funding: `fapi.binance.com/fapi/v1/fundingRate` (from 2019-09-10) and data.binance.vision
  monthly zips (from 2020-01, includes delisted symbols).
- Daily (1d) klines, perpetual (`data/futures/um/monthly/klines/<S>/1d`) and spot (`data/spot/monthly/klines/<S>/1d`),
  data.binance.vision, including delisted symbols (survivorship).
- Bybit linear funding history `api.bybit.com/v5/market/funding/history` for stream B only.

## Eras (declared)
- IS = 2020-01-01..2021-12-31 (funding data start; 2 years, not 6: a data limit, stated in the report).
- VAL = 2022-01-01..2024-12-31.
- HOLD = 2025-01-01..2026-10-30. Never looked at for this mechanism. Cut at load (ts < 2025-01-01) for IS / VAL work;
  HOLD is opened once, after a PREREG with hashes.

## Accounting (declared)
- Book capital C fixed. A position on coin i = long q spot + short q perp, entered at the 1d close (00:00 UTC) of the
  signal day, q = (C / K) / spot close. Daily P&L = q x (dS - dF) + sum over the day's stamps of rate x q x F_close.
  (Funding mark price approximated by the perp close of the stamp's day; the error is second order.)
- Costs per entry and per exit, per coin: spot taker 0.10 % + perp taker 0.05 % + half-spread on each leg
  (0.01 % BTC / ETH, 0.03 % top-10 others, 0.05 % rest) = 0.17-0.25 % per side. VIP0, no BNB discount, no maker.
- Unit for t / power: the book's daily return (calendar days, crypto trades 7 days). Also reported per episode.
- Liquidation check: for each episode, the max perp rise from entry; report how many would breach a 2x / 3x short-leg
  margin without a top-up (spot leg gains cover it but a bot must move collateral).

## Hypotheses
- **A1 (unconditional premium, BTC and ETH)**: hold the pair continuously, entry once at the era start, exit at the era
  end. Side fixed: short perp / long spot. Expect net > 0 in every era. A premium, not a selection rule: no random
  benchmark; it is reported as the baseline the rules must beat.
- **A2 (conditional carry, the candidate)**: universe each day = Binance USDT-M perps with a spot pair, listed >= 60
  days, top N = 30 by trailing-30-day perp quote volume. Signal = trailing-L-day mean funding, annualised. Enter when
  signal > theta_in, exit when signal < theta_out; at most K = 10 coins, ranked by signal; each coin C / K.
  Grid (18 cells, fixed now): L in {3, 7, 14} days x theta_in in {10, 20, 30} % / yr x theta_out in {0, theta_in / 2}.
  Pick one cell on IS (net Sharpe of daily book returns, ties to the lower turnover), check it on VAL unchanged.
- **A3 (BTC + ETH only, conditional)**: A2's rule restricted to BTC and ETH, same grid; the lower-tail-risk version.
- Random benchmark for A2 / A3: the same number of concurrent positions and the same episode durations, but coins drawn
  at random from that day's universe and entry days shifted at random within the era (500 draws); LIVE needs A2 > 95 %
  of draws on IS and VAL.
- Stress: costs x1.5; entry one day late (signal on day t, enter at day t + 1 close); drop the top 5 funding days.

## Bars (the user's, unchanged; unit = daily book return)
- LIVE: net t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, > 95 % of random draws, positive at costs x1.5 and one
  day late; open HOLD only if expected HOLD power = daily net Sharpe (VAL size) x sqrt(HOLD days ~ 669) >= 3.
- Power arithmetic before building: a book at 6 %/yr net with 2 %/yr vol has daily Sharpe 0.16; x sqrt(669) = 4.1.
  At 3 %/yr net and 3 %/yr vol: 0.052 x 25.9 = 1.35 (fails). So the rule needs VAL net/vol >= ~2.2 annualised.
- Correlation with C3 daily P&L reported for any survivor.

## Known pitfalls to check
- Survivorship: use data.binance.vision (keeps delisted symbols); LUNA (2022-05), FTT (2022-11) must be in VAL.
- Funding interval changes (8h -> 4h / 1h for some coins since 2023): sum actual stamps, do not assume 3 per day.
- Spot and perp 1d closes are the same second; illiquid coins' last trades can be stale: note the basis noise.
- Funding caps / floors and the 0.01 % default (interest component): BTC's 0.01 % / 8h = 10.95 %/yr is the baseline.
