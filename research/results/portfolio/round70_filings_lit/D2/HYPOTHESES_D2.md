# Round 70, stream D2: funding-formula carry, long Deribit perp / short Binance perp

Written 2026-11-01 17:44 UTC (from `date -u`), before any return or price-difference series was computed. Data seen so
far: Deribit robots / support pages, one month of BTC-PERPETUAL hourly funding (2020-01, to learn the field meanings),
one 1h chart page (2020) to learn the page size. The full Deribit pull (funding + 1h trade OHLC to 2024-12-31
23:59:59 UTC) is running; nothing from it has been summarised.

## Mechanism
Binance USDT-M funding has an interest leg; Deribit perpetual funding has none. In calm markets a Binance long pays
~0.01 %/8h (10.95 %/yr) while a Deribit long pays ~0 when its mark sits within +-0.025 % of the index. Long Deribit /
short Binance in equal USD delta collects the Binance anchor unless (a) Deribit's premium rises until its longs pay the
same (arbitrage), or (b) the two perps' prices drift apart. Round 59's B1 / B2 paired venues that both carry the anchor
(it cancels); here it sits on one leg only, by contract rule.

## Funding formulas (sources and change dates)
- **Deribit** (support.deribit.com "Funding Specifications", art. 31424939178397, page dated 2026-10-21, and "Inverse
  Perpetual", art. 31424954847133; bodies in research/data/deribit_funding/raw/docs/):
  Premium = (Mark - Deribit Index) / Index; Funding (8h-rate) = min(cap, max(-cap, max(0.025 %, P) + min(-0.025 %, P))),
  cap +-0.5 % BTC, +-1 % ETH, +-5 % USDC / USDT linear. Accrues continuously (per ms), no fee on funding, realised into
  cash at the 08:00 UTC settlement. No interest component. **Change dates: not found.** No dated changelog surfaced
  (2 WebSearches); one older Deribit Insights article describes a +-0.05 % zero band. Web.archive.org is not allowed.
  Consequence: the test uses Deribit's realised hourly funding (`interest_1h`), not a formula, so the damper history
  only matters for the mechanism; I will report the share of hours with exactly zero funding by year as a descriptive
  check of the damper in force.
- **API semantics checked on 2020-01:** `interest_1h` = realised funding fraction over the hour ending at `timestamp`;
  `interest_8h` = trailing sum of the last 8 `interest_1h` (corr 0.9999, ratio 0.999). Daily funding = sum of
  `interest_1h` stamped in the day. (`get_funding_rate_value` for 2020-01-03 gave 1.059e-4 vs 1.105e-4 for my sum: window
  convention differs by ~1 h; I will check 3 more days and use whichever convention matches.)
- **Binance USDT-M** (Binance FAQ "Introduction to Binance Futures Funding Rates", via secondary descriptions; no
  primary page fetched because www.binance.com support pages sit behind the /bapi/ host family we avoid):
  F = P_avg + clamp(0.01 % - P_avg, -0.05 %, +0.05 %) per 8h; P_avg time-weighted premium index; interest 0.01 %/8h for
  USDT-M contracts, unchanged 2019-24 as far as known; 8h stamps 00 / 08 / 16 UTC for BTCUSDT / ETHUSDT 2020-24. The test
  uses realised stamps in research/data/binance/funding/ (local). Descriptive check: share of stamps at exactly 0.0001
  by year.

## Construction (declared)
Notional N = 1 per asset. Daily marks at 00:00 UTC = close of the 23:00 1h bar on both venues (last trade before
midnight; Deribit index from `index_price` at the 00:00 funding row). The F7 signal uses funding known by 23:00 UTC
(Deribit hours through 23:00, Binance stamps through 16:00); trades happen at the 00:00 marks, >= 59 min later.
*Amended 17:46 UTC before any return was computed:* the first draft marked at 01:00, which would need the
2025-01-01 00:00-01:00 bar for the last VAL day (HOLD data). Binance's 00:00 stamp belongs to the day it closes;
the 2025-01-01 00:00 stamp is dropped (cut), so 2024-12-31 has two stamps.
- **Binance leg:** short q_B coins of the USDT perp, USDT collateral U_B; P&L -q_B dF_B + funding received at each stamp
  (rate x q_B x 1h close at the stamp hour).
- **Deribit leg (inverse, coin-margined):** collateral M coins, long V USD of the inverse perp (BTC-PERPETUAL /
  ETH-PERPETUAL). Account USD delta = M x S + V, so to keep the pair USD-neutral V = N - M S (the coin collateral itself
  is long). Coin P&L per day V (1/F_D,prev - 1/F_D) - sum_h interest_1h x V / index_h, realised into M daily (Deribit
  settles daily). This is the implementable version: part of the Deribit delta is spot coins (paying no funding), so
  the book is "perp-perp on N - m" plus "spot-perp on m". The decomposition reports both parts.
- **Leverage / capital:** target equity per venue m = N / L. **Primary L = 2** (capital C = N): at 3x the 2020-03-12
  -40 % day would have liquidated the Deribit long (equity N/3) unless topped up intraday. L = 3 reported as a
  sensitivity of the cash grading only. Liquidation check: days where the intraday adverse move (1h highs / lows from the
  last mark) exceeds the leg's equity minus 1 % maintenance; reported, not simulated.
- **Rebalancing:** at a daily mark, (a) if |Deribit delta - Binance delta| > 5 % of N or either delta is outside
  [0.8, 1.2] N, trade both back to N; (b) if either venue's equity leaves [0.6, 1.6] x m, move capital so both equal m
  (BTC <-> USDT conversion at 0.10 % of the amount moved, transfer assumed instant at the mark: optimistic).
- **When the rule is off:** Binance flat (USDT); Deribit holds "synthetic USD": V = -M S (short inverse equal to the
  collateral), paying / receiving Deribit funding on it. Capital stays at the venues.

## Costs
Binance taker 0.05 % per side + 0.01 % half spread; Deribit taker 0.075 % per side (the older 2020-21 schedule, kept for
all years: conservative, current schedule 0.05 %) + 0.01 % half spread; spot conversion 0.10 % on capital transfers and
on the initial coin collateral. Entry and exit of the whole book charged inside each era. Checks: costs x1.5, one day
late.

## Cells (6, fixed now)
Assets {BTC, ETH, BTC+ETH 50 / 50 of N} x rules {
- **ON**: always on;
- **F7**: on when the trailing 7-day mean of (Binance daily funding - Deribit daily funding) > 0, evaluated at 00:00 UTC
  daily (exit when <= 0) }.

Eras: IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31 (all series cut at ts < 2025-01-01 at load). USDC linear
perps (2022+) are descriptive only (funding level vs inverse), not a cell.

## Grading
- Daily book return r_d = change in total equity / N. Newey-West t (lag 10, round 58 `stats`).
- Cash: excess_d = r_d - DFF_d x C / N, C = 2 m (capital at both venues every day; primary), plus a deployed-days-only
  variant for F7. DFF from research/data/rates/DFF.csv. Report also excess at L = 3 (C = 2/3 N).
- Bars (brief): LIVE t_IS >= 2.5, t_VAL >= 1.5, >= 2/3 years positive, random >= 95 %, HOLD power >= 3; **and excess over
  cash > 0 with t >= 1.5 in IS and VAL** (round 59 rule). DEMO: t_IS >= 2.0, VAL net > 0, random >= 90 %.
- Random benchmark: F7: circular shifts of the on/off mask by random offsets (500 draws) with the same costs; ON: there
  is no timing to randomise (random side = minus the book: beaten iff mean > 0), stated as weak. Max-over-cells null:
  joint stationary block bootstrap (mean block 20 days, 1,000 draws) of the 6 demeaned cell series, distribution of the
  max IS t.
- Decomposition: funding leg (Binance funding received - Deribit funding paid), price leg (perp / index moves of both
  legs and the collateral), costs; plus the "pure" funding gap f_B - f_D on the full N (as if collateral were USD).

## Power
IS ~731 days, VAL ~1,096, HOLD ~667. HOLD power >= 3 at VAL size needs annual Sharpe >= 3 / sqrt(667/365) = 2.22; IS
t 2.5 needs Sharpe 1.77; VAL t 1.5 needs 0.86. A funding gap of 6 %/yr with 2 %/yr vol (Sharpe 3) would pass; a gap
that Deribit's premium absorbs (Deribit longs paying the same ~11 %/yr) gives ~0 with price-leg noise. Excess over cash
at L = 2 needs net > DFF (VAL mean ~3.9 %/yr): net >= ~6 %/yr with t >= 1.5. Prior (LIT): P(LIVE) 1.5 %, P(DEMO) 5 %.
