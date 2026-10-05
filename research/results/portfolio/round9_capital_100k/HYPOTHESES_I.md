# Stream I hypotheses and planned analyses (written before any stream-I number)

Started 2026-10-05. Account: IC Markets cTrader, $100,000. Rules: BRIEF.md + STREAM_I.md. HOLD (2025-01-01 onward)
is cut at load for every market series. Exception (BRIEF): C3's own trade CSV
(research/results/portfolio/gotobi_cbot_trades.csv) is used in full 2016-2026 for sizing, as the brief allows; its
M1 path reconstruction stops at 2024-12-31 (M1 is cut at load), 2025-26 legs enter with their CSV close only.

## I-A. C3 at $100k: execution and risk at size (descriptive; no edge discovery)

Planned method, fixed before computing:
- A1 notional/lots: per leg, units = lots x 100,000 (CSV), notional USD = units x (base->USD at entry; USDJPY = 1,
  EURJPY/GBPJPY = entry x JPY->USD from the same-minute USDJPY leg or the M1 USDJPY bid). Lots at risk f of $100k
  scale as lots_exact x (f x 100,000 / risk), lots_exact = risk / (stop_pips x pip value per lot) with
  stop = 3 x ATR20(H1, simple, bid H1 bars, last closed bar) rebuilt from M1 for 2016-24 (validated against the CSV
  lots at $50, floor to 0.01 with the bot's min-lot rule). Grid f = 0.25 / 0.5 / 1 / 1.5 / 2 % per leg, fixed fraction
  and compounding. IC limits and margin from IC's web pages (1:30 retail, live account 1:1000).
- A2 spread at C3's minutes: per pair and year 2016-24, ca - c and smean / smin at 18:00 (or the actual entry minute),
  00:55 and 02:55 UTC, vs that day's median minute spread; tick count n at those minutes vs the day's median. Market
  impact: square-root model and a top-of-book depth assumption, stated with its source; R cost of extra slippage
  0.1 / 0.2 / 0.5 pip per side = 2 x slip / stop_pips per leg.
- A3 floating DD: per leg, minute marks from M1 (long marked at bid low within the minute / bid close; short at ask
  = bid + spread at the minute's high; worst point per minute), basket equity at minute resolution, holidays dropped.
  Report closed-only vs mark-to-market max DD and worst day, in R and at each risk.
- A4 block bootstrap: resample gotobi days in blocks of 10 consecutive gotobi days, 5,000 paths, 1 year (~71 days)
  and 3 years (~213 days); each day contributes its closed R per leg and its intraday worst MTM (2016-24 days only for
  the MTM version; 2016-26 closed-only version also shown). Full edge and edge halved (every leg's R shifted by
  -0.5 x mean R). P(max DD >= 10 / 20 / 30 %).
  **Recommendation rule (fixed now):** for a DD tolerance X, recommend the largest risk per leg in the grid
  {0.25, 0.375, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0} % such that P(MTM max DD >= X within 3 years) <= 10 % under the
  HALVED edge, fixed-fraction sizing. Also report the full-edge probabilities.
- A5 IC volume rebates (web) and their value for C3 in R per leg.

## I-B. New mechanisms (each family: design 2004-2015 where data allow, check 2016-21 and 2022-24 once)

Bar (BRIEF point 5, slow premia): net > 0 in every era separately; Newey-West t of the net mean >= 2.5 over the full
design+check sample; majority of years > 0; net > 0 at cost x1.5; better than the obvious benchmark at the same risk.
Costs (IC): spread at the trade minute (IC M1 2016-24; IC 2016-17 median spread profile for 2004-15), commission
0.6 bp round trip (0.3 bp per side) for FX and metals, none for indices/energies; financing per rollover from
research/swing/rates.py swap_frac_at (FX and gold: historical policy rate differential minus IC's fitted markups;
indices r + ~5.3 %/yr long), with my own FRED rate copies back to 2000 so 2004-15 has rates.

### H1 Gold fair value: gold vs US 10y real yield and the dollar (2-12 weeks)
- Mechanism: gold pays nothing, so its opportunity cost is the real yield; the dollar is its numeraire (Erb & Harvey
  2013 "The golden dilemma"; Barsky & Summers 1988). When gold trades far from the level its drivers imply, asset
  allocators' substitution pulls it back over weeks.
- Rule: weekly (Friday 20:00 UTC close). Rolling 156-week OLS of log gold on DFII10 (level, %) and log broad dollar
  (FRED DTWEXBGS, spliced with DTWEXB before 2006). z = last residual / sd(residuals in window). Position =
  -clip(z / 2, -1, 1), sized to 10 %/yr vol (26-week realized vol of weekly returns); held one week, re-set weekly.
  Also the predictive slope of the next 4- and 8-week log return on z (non-overlapping-safe HAC t).
- Success: the slow-premium bar above; also the slope must be negative (reversion) in each era.

### H2 USDJPY fair value vs the US-Japan rate spread (2-12 weeks)
- Mechanism: covered/uncovered interest parity and carry demand: USDJPY co-moves with the US-JP 2y and 10y spread;
  deviations close as carry/real-money flows respond (e.g. Engel & West; the 2013-24 USDJPY-spread co-movement).
- Data: US DGS2 / DGS10 (FRED), Japan 2y / 10y JGB from MoF jgbcme_all.csv. Rule as H1 with regressors the 2y spread
  and the 10y spread (levels). USDJPY from Dukascopy H1 2004-15, IC M1 2016-24.
- Success: as H1.

### H3 Commodity currencies vs terms of trade (2-12 weeks)
- Mechanism: commodity-currency exchange rates follow their export prices (Chen & Rogoff 2003; Cashin, Cespedes &
  Sahay 2004); the exchange rate's deviation from the commodity-implied level closes over weeks. Round 8 R4 tested
  <= 5 days only.
- Rule as H1 on log AUDUSD vs log copper (Yahoo HG=F) + log gold + AU-US short-rate spread; log USDCAD vs log WTI
  (FRED DCOILWTICO) + CA-US rate spread; log NZDUSD vs log copper + log gold (dairy has no daily series) + NZ-US
  spread. Rates: FRED monthly short rates (forward-filled).
- Success: as H1, per pair and as an equal-risk book of the three.
- H1-H3 are one family ("macro fair value"): 5 instruments x 2 forecast horizons (4, 8 weeks) for the slope screen +
  5 tradeable books; cells counted in the write-up.

### H4 Speculator positioning extremes (CFTC COT), 4-12 weeks
- Mechanism: crowded speculative positions unwind (crash risk of crowded carry, Brunnermeier, Nagel & Pedersen 2008);
  hedging pressure (Keynes; de Roon, Nijman & Veld 2000) at longer horizons. Round 4 tested a 1-week hold on 2014-26.
- Data: CFTC legacy futures-only, 2000-2024 (annual deacot files), non-commercial net / open interest; z over 156
  weeks. Markets: JPY, EUR, GBP, AUD, CAD, CHF, NZD futures (-> the IC USD pairs, sign by quote convention), gold,
  silver, WTI crude, S&P 500 (big + e-mini), Nasdaq-100 e-mini, Dow e-mini, Nikkei (if present).
- Rule: contrarian; at each Tuesday report (traded from the following Monday open), z > +1.5 -> short the asset for
  H weeks, z < -1.5 -> long, H in {4, 8, 12}; overlapping positions averaged (1/H of risk per entry cohort).
  Also the continuous version: weekly position = -clip(z/2, -1, 1), vol-targeted. Design 2004-2015 (FX and gold
  from Dukascopy H1; others where daily data exist: Yahoo futures/indices), checks 2016-21 and 2022-24 on IC M1.
- Success: slow-premium bar, net of IC costs and financing; contrarian sign in every era.

### H5 Large-shock regimes in indices: buy after a >= 10 % drawdown or VIX > 30, hold weeks
- Mechanism: crash-risk / liquidity-provision premium: expected returns rise after crashes when intermediaries are
  constrained and risk aversion spikes (Nagel 2012; He & Krishnamurthy 2013; Cochrane's time-varying risk premia).
- Data: S&P 500 (^GSPC), Nasdaq-100 (^NDX), Dow (^DJI), DAX (^GDAXI), FTSE (^FTSE), Nikkei (^N225), ASX 200 (^AXJO),
  Hang Seng (^HSI) daily closes 1990-2024 (Yahoo), VIX 1990-2024 (CBOE). Design 1990-2015, checks 2016-21, 2022-24.
- Rules (fixed): (a) S&P 500 closes >= 10 % below its 252-day high: buy next close, hold 21 / 42 / 63 trading days
  (one position at a time, re-entry allowed after exit if still in drawdown); (b) VIX close > 30: buy S&P 500 next
  close, hold 21 / 42 / 63 days; (c) (a) applied to each index on its own drawdown. Financing: long at
  r_USD (or local) + 5.3 %/yr (IC markup), spread ~1 bp a side.
- Benchmark: the index's unconditional mean daily excess return (buy-and-hold at the same exposure-days), i.e. the
  strategy's excess return per day in the market minus buy-and-hold's; plus Sharpe vs buy-and-hold.
- Success: slow-premium bar AND conditional net excess return per day > unconditional buy-and-hold net per day with
  HAC t >= 2 on the difference.

### H6 Swap-aware carry at IC's actual net swap, positive-swap legs only, vol-targeted book
- Mechanism: the carry (forward premium) risk premium (Lustig & Verdelhan; Burnside et al.), harvested only where
  IC's markup still leaves a positive daily swap, so financing is income, not a cost.
- Rule: month-end rebalance. For the 10 IC FX pairs (+ XAUUSD short), compute each side's net swap per rollover from
  swap_frac_at at the rebalance date (rates known then). Hold every side whose annualized net swap > 0.5 %/yr (a
  minimum so near-zero legs don't churn), each leg at equal vol (60-day realized), book scaled to 8 %/yr vol, at
  most 10 legs. Costs: spread + 0.3 bp a side on each rebalance trade, swap per rollover with the triple Wednesday.
- Data: Dukascopy H1 2004-15 (11 symbols), IC M1 2016-24.
- Success: slow-premium bar; benchmark = round 7 D's equal-weight carry (net Sharpe 0.19) and zero.

### H7 Multi-strategy book
- C3 plus anything from H1-H6 that passes its bar, risk-budgeted (equal risk), with the daily P&L correlation to C3.
  If nothing passes, report the correlation of the best candidates with C3 for information only.

## Amendments (data availability), written before the H1-H5 numbers
- FRED is unreachable from this machine all session (HTTP/2 stream errors / timeouts) and Yahoo answers 429. So:
  DFII10 -> US Treasury's daily real yield curve (10 YR, home.treasury.gov, 2003+; same series FRED republishes);
  DGS2/DGS10 -> Treasury daily nominal curve; broad dollar DTWEXBGS -> a DXY-weighted dollar index built from the
  local FX panel (EUR 57.6, JPY 13.6, GBP 11.9, CAD 9.1, CHF 3.6, SEK left out and weights renormalized); policy
  rates for financing -> BIS WS_CBPOL daily (EUR = ECB main refinancing rate, which overstates the overnight rate by
  ~0.5-0.9 pp in 2009-15; noted). IC financing markups: rates.py's fitted constants (sealed step, constants only, in
  data/markups.json), as round 7 did.
- H3 without copper/WTI history before 2016 (Yahoo): if Yahoo stays blocked, H3 runs on IC data only: AUDUSD vs
  log XAUUSD + log XTIUSD + AU-US policy spread; USDCAD vs log XTIUSD + CA-US spread; NZDUSD vs log XAUUSD + log
  XTIUSD + NZ-US spread; 104-week window (shorter history), design 2016-21 (IC energies start 2017), check 2022-24.
- H5 with SPX only (CBOE SPX_History.csv 1975-2024, price index; dividends added at a flat 2 %/yr, which IC's
  cash-index CFD credits to longs) and VIX (CBOE) if the other index histories stay blocked.
- Weekly bar = the last daily 20:00 UTC close of each week (Friday normally).
- H3 final data (before its numbers): EIA daily WTI spot (RWTCd, 1986-2024; non-positive prints of April 2020
  dropped) + local gold replace Yahoo's copper/WTI; copper is left out (no reachable daily source). Regressions as
  written: log AUDUSD ~ log gold + log WTI + (AU-US policy rate); log NZDUSD ~ log gold + log WTI + (NZ-US);
  log USDCAD ~ log WTI + (CA-US). 156-week window, design 2004-15, checks 2016-21 / 2022-24.
- H1/H2 result seen before H3 is run: the residual slopes have the momentum sign, not reversion. H3 keeps the
  reversion rule as registered; no sign flip will be tested as a candidate on these data.
