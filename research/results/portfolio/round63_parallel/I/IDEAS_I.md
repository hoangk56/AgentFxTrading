# Round 63, stream I: next wave of hypotheses (scouting only, nothing backtested)

Written 2026-10-31 16:05 UTC (from `date -u`; work 15:48-16:10 UTC). Stream I did not backtest anything and loaded no
price data from 2025-26. Reachability checks: one request per source, logged in [requests.log](requests.log) with the
UTC time, URL, status and bytes. Bodies went to the scratchpad. Two Kalshi probes returned metadata for 2026 markets
(no prices); both bodies were deleted (see the NOTE lines in the log). Code: `code/probe.py`, `code/lit.py`,
`code/abstracts.py`, and the query lists `code/queries1.tsv` and `code/queries2.tsv`.

## Answer first
- **No idea here is likely to give LIVE.** The best is ~3 %, and the 14 ideas together give maybe 12-18 % of at
  least one LIVE candidate (they are not independent). That is still more than the ~1 % that PROMPT.md gives every
  remaining free direction after round 57.
- **The only way to reach the LIVE power bar (HOLD power >= 3) is a large number of independent events.** C3 gets
  there with ~70 dated forced flows a year per pair. This wave's best route is a new asset class with thousands of
  independent, idiosyncratic events a year: event contracts (Polymarket, Kalshi; I1, I2, I3). After that come
  per-asset dated supply events (token unlock cliffs I4, IPO lockups I5). Exchange-rule events in Asian single
  stocks (I6-I9) are rule-driven and numerous, but they fail on tradability or free data.
- **HOLD hygiene warning for I1-I3.** The 2026 papers I read to find the prediction-market mechanisms (Cardozo &
  Rivero-Wildemauwe; Qiu & Qiu; Bürgi, Deng & Whelan) use mostly 2024-26 data. Their conclusions are therefore
  partly HOLD-era knowledge, so a 2025-26 HOLD is not blind for these ideas. The coordinator should either grade
  them on IS/VAL with a forward log as the deciding test (as for B3/A1 in round 24), or say plainly in the PREREG
  that HOLD was contaminated by the literature.
- **Lesson from today's crypto rounds that applies to I1-I4.** Prediction markets and token unlocks had a large
  inflow of bots and market makers in 2025-26. Strong IS/VAL numbers there are the same pattern that died in
  2025-26 for crypto carry. Grade a capital-heavy rule (I1, I3) on its excess over the cash rate.

## Power arithmetic used below
LIVE needs HOLD power = net Sharpe per trade at VAL size x sqrt(n HOLD trades) >= 3, with HOLD of ~1.8 years.
- For a binary contract bought at price p with true win probability q, the return per $ has mean (q - p) / p and
  sd sqrt(q(1 - q)) / p. Example: p 0.93, q 0.94 gives mean +1.1 % and sd 25.5 %, so a per-trade Sharpe of 0.042,
  and 5,100 independent HOLD events (2,800 a year) are needed.
- Event study with mean m and sd s per event: n = (3 s / m)^2. Example: m -3 % and s 15 % need 225 HOLD events.
- "Independent" means grouped by parent event or day cluster. Brackets of one temperature market, or contracts of
  one election, count once.

## Ranked hypotheses

| # | idea | instrument / venue | events / yr | power at a plausible VAL size | P(LIVE) | P(DEMO) |
|---|---|---|---|---|---|---|
| I1 | favorite-end bias of event contracts held to resolution | Polymarket CLOB (Kalshi as replication) | 1-3k independent events (2023-24) | 2-4 if +1c / $ survives | 3 % | 8 % |
| I2 | settled-but-unpaid lag after the outcome is public (resolution-rule carry) | Polymarket, Kalshi | 1-3k | > 3 if misresolution < 0.3 % | 2.5 % | 6 % |
| I3 | daily temperature contracts vs the NWS settlement rule + free NOAA guidance | Kalshi KXHIGH* (Polymarket weather mostly 2025+) | ~5-7k city-days | > 3 on paper; fees and pre-2025 data decide | 2.5 % | 6 % |
| I4 | short perps into large token cliff unlocks | Binance / Bybit USDT-M perps | 100-300 cliffs | 2-3.5 | 2.5 % | 8 % |
| I5 | short US IPO stocks into the lockup expiry | US single stocks (IB, with borrow) | 150-300 | 1.5-2.6 | 1.5 % | 6 % |
| I6 | A-share price-limit / T+1 rules (day after the first limit-up) | SSE / SZSE main board via Stock Connect (long only) | thousands of stock-days, ~240 dates | 1-3 (date clusters) | 1.5 % | 5 % |
| I7 | VIX ETP calendar-roll component (Todorov's split, roll part only) | CFE VX M1 / M2 calendar spread (IB) | ~250 days | 1-2 | 1.5 % | 4 % |
| I8 | Taiwan "attention / disposition" designation (rule-predictable) | TWSE stocks (needs a local FINI account) | hundreds | 1-2.5 after 0.3 % tax | 1 % | 4 % |
| I9 | Japanese shareholder-perk record dates (優待権利付最終日), hedged | TSE stocks (IB) + TOPIX futures | ~1.5k firm-events on ~20 dates | 0.8-1.5 | 1 % | 4 % |
| I10 | single-stock leveraged ETF close rebalancing (TSLL, NVDL, CONL...) | US single-stock CFDs / stocks at the close | ~250 days x 3-6 names | new era: IS / VAL too short | 1 % | 3 % |
| I11 | TSE margin regulation (日々公表 -> 増担保規制) designations | TSE stocks (IB) | hundreds | unknown (no history found) | 0.5 % | 2 % |
| I12 | EU ETS primary-auction supply calendar | ICE EUA futures (IB) | ~200 auction days | < 1 at daily resolution | 0.5 % | 2 % |
| I13 | broker close-out deadlines before First Notice Day (retail longs) | COMEX GC / SI, NYMEX CL calendar spreads | 6-12 per contract | < 1.5 | 0.5 % | 2 % |
| I14 | month-end PTAX battle, side from B3 positioning by investor type | CME 6L BRL futures | 12 | < 1 (12 / yr) | 0.3 % | 3 % |

The P(LIVE) column includes the chance that the data or the venue turns out to be unusable. Most of the mass in
I1-I4 is lost to "real in 2020-24, crowded out in 2025-26" and to data gaps before 2025.

---

### I1. Favorite-end bias of event contracts, held to resolution (Polymarket; Kalshi replication)
- **Mechanism.** Takers who buy lottery tickets overpay for longshots. The other side (favorites) is underpriced
  because it locks capital until resolution for a small payoff. On Polymarket before 2025 that capital earned no
  interest and had no leverage, and position caps or thin books limited the arbitrage. The bias is one of the most
  durable patterns in betting markets. The timing is set by the venue's resolution rules (the end date is fixed when
  the market is listed). Who trades predictably: retail longshot buyers. Accounts that buy longshots persistently
  make 26.6 % of next-month low-price purchases.
- **Sources.** Cardozo & Rivero-Wildemauwe 2026, "The Favorite-Longshot Bias in Prediction Markets: Evidence from
  Polymarket", doi:10.48550/arxiv.2609.12878. Over 588 M trades, purchases below 10c lose 19.3c per $ and purchases
  at or above 90c earn +0.83c. Grouped by parent event, the longshot side flips sign; the bias holds in crypto and
  politics but not in sports. Bürgi, Deng & Whelan, "Makers and Takers: The Economics of the Kalshi Prediction
  Market", doi:10.2139/ssrn.5502658: clear FLB, and high-price contracts give small positive returns. Zitzewitz 2026,
  "Limits to Arbitrage and Prediction Market Efficiency: the Case of PredictIt", NBER w35845: caps on stakes gave
  larger longshot overpricing. Background: Snowberg & Wolfers 2010, JPE.
- **Why it is not exhausted.** No round has touched event contracts. The closest family is the "premia that lose to
  costs / short vol = beta" conclusion (round 9: VRP is beta). Selling longshots is short-vol-like, but here the risk
  is idiosyncratic and mostly uncorrelated across events, so there is no market beta to strip out. Funding carry
  (round 58) is also close: it is a capital-lock premium. The rule therefore has to beat the cash rate on capital
  deployed.
- **Instrument / venue.** Polymarket CLOB (USDC on Polygon; geo-restricted in some countries, a user decision).
  Kalshi (CFTC-regulated; access for non-US persons is a user decision). Kalshi's taker fee is 0.07 x P x (1 - P)
  per contract, about 0.7c at P 0.9, so the rule there must be maker-side.
- **Data (checked 2026-10-31).**
  - `gamma-api.polymarket.com/markets` returns 200, keyless, with date filters; robots.txt is 404 (no file).
  - `clob.polymarket.com/prices-history` returns 200 for a 2023 market at hourly fidelity; robots.txt 404. Long
    windows give 400 "interval too long", so pull in chunks of about 6 days.
  - polymarket.com/robots.txt timed out (not confirmed).
  - March 2022 holds at least 70 closed markets, only 1 of them on the order book (the pre-CLOB AMM era). March
    2024 holds at least 77, with 104 order-book flags in the truncated page.
  - So reliable CLOB prices start around late 2022. IS = 2023 and VAL = 2024 is about the most one can get, which
    means the new-era rule (round 24) applies.
  - Kalshi API `api.elections.kalshi.com/trade-api/v2` is keyless and returns 200. Requests for pre-2025 settled
    markets returned none, and the historical endpoint ignored `max_close_ts`. Pre-2025 Kalshi coverage is
    unconfirmed.
- **History, events, cost.** History is 2022-11 onward on the CLOB, and the 2024 election year dominates volume. That
  gives ~1-3k independent resolved events a year in 2023-24 and many more in 2025-26. Costs: Polymarket fees were
  ~0 for most markets before 2025, and the half spread is ~0.5-1c at 0.9-0.97. The paper's +0.83c is already at
  transaction prices.
- **Power.** At +1c per $ (Sharpe/trade ~0.04), ~5k independent HOLD events are needed: reachable on 2025-26
  Polymarket volume, but VAL (2024) gives at most ~1-2k, so the VAL t would be only ~1.5-2. At the paper's grouped
  numbers the edge may be half that. Declared first test:
  - buy the leading outcome at T-24 h when 0.90 <= p <= 0.97;
  - one trade per parent event;
  - hold to resolution;
  - grade per $ on excess over the cash rate;
  - IS 2023, VAL 2024.
- **Chance.** LIVE 3 %, DEMO 8 %.

### I2. Settled-but-unpaid lag (resolution-rule carry) on event contracts
- **Mechanism.** After the outcome is public, the winning share often trades below 1 until settlement. On
  Polymarket, settlement goes through the UMA optimistic oracle: a proposal, a 2-hour challenge period, then a vote
  if disputed. On Kalshi, settlement comes from the named source, for example "the morning after" for weather. The
  rule-driven delay plus capital lock and dispute risk leaves a premium for patient capital. The timing is
  predictable from the market's own end time.
- **Sources.**
  - Kalshi help, "Weather markets" (settlement source, delays when the climate report disagrees with METAR or is
    revised lower): https://help.kalshi.com/markets/popular-markets/weather-markets
  - Qiu & Qiu 2026, doi:10.48550/arxiv.2610.13593: in the final 1-12 h of Polymarket weather markets, favorite
    *over*pricing is about an order of magnitude larger than the longshot error. This is a warning that near
    resolution, favorites can be rich, not cheap.
  - The UMA / Polymarket resolution docs are not fetched yet. Read them before declaring the rule.
- **Why it is not exhausted.** No earlier round. It is closest to funding carry (round 58), a cash-like premium, so it
  must be graded on excess over cash. It differs in that the premium compensates a settlement-rule delay plus a tail
  risk of misresolution, not leverage demand.
- **Instrument / data / history.** Same as I1. You also need the time the outcome became public: use the market's
  `endDate` / event time from gamma. If the outcome is decided by a price jump, use the time of the first hourly
  price >= 0.95 and enter one hour later.
- **Events, cost, power.** ~1-3k a year. Per trade, about +0.5-2 % over hours to two days. A misresolution
  probability of ~0.2 % at -100 % gives a per-trade sd of ~4.5 % and a Sharpe of 0.1-0.3, so power > 3 if the
  premium is real. The binding risks: bots took the premium (likely by 2025), and the misresolution tail is
  fat and clustered (a disputed event hits every holder at once).
- **Chance.** LIVE 2.5 %, DEMO 6 %.

### I3. Daily temperature contracts vs the NWS settlement convention and free NOAA guidance (Kalshi)
- **Mechanism.** Settlement is rule-driven and exact: the NWS Daily Climate Report for one named station (NYC =
  Central Park, Chicago = Midway). The day is in local *standard* time, so during DST it runs 01:00-00:59 local
  clock time. The values are integer °F, and preliminary versus final reports can differ. Retail traders anchor on
  phone apps, which the venue says do not settle the contract. A forecaster that applies the exact rules (station,
  LST day, observed highs so far from METAR / 5-minute ASOS, NOAA NBM / MOS guidance) has a dated, mechanical edge
  late in the day.
- **Sources.**
  - Kalshi help pages (the DST window is 01:00 to 00:59; the only source is the NWS CLI):
    https://help.kalshi.com/markets/popular-markets/weather-markets
  - The CFTC filing for the NYC contract: https://www.cftc.gov/filings/orgrules/rules042623980.pdf. Cited from
    search results only, not fetched, because cftc.gov blocks ClaudeBot in robots.txt.
  - Qiu & Qiu 2026, doi:10.48550/arxiv.2610.13593 (time-varying FLB in weather markets).
- **Why it is not exhausted.** Round 31 tested CPC temperature forecasts for natural gas (priced in 24 h earlier)
  and round 43 tested weather mood on equities. Neither traded the weather contract itself, where the payoff is the
  weather.
- **Instrument / data.**
  - Kalshi KXHIGH* / KXLOW* series. Polymarket weather markets are mostly 2025+, so they are HOLD-only.
  - NOAA data are free: the ISD on the public AWS bucket was used in round 43.
  - Kalshi pre-2025 price history is **unconfirmed**: my two requests returned no pre-2025 weather markets. Test
    `/series/{s}/markets/{t}/candlesticks` on a 2023 ticker first.
- **Events, cost, power.** ~20 cities x 365 days, with brackets grouped per city-day. The taker fee at mid prices is
  ~1.75c per $1 contract, so the rule must post maker quotes or buy only near 0.03-0.10. If the documented
  favorite-end error is ~5c at P 0.9, Buy-NO at 0.10 has a Sharpe of ~0.14 per city-day, and n ~ 10k gives power far
  above 3. This depends entirely on IS/VAL data existing and on the edge surviving 2025-26 bots: practitioner
  dashboards for exactly this trade are public (search results, Oct 2026).
- **Chance.** LIVE 2.5 %, DEMO 6 %.

### I4. Short perps into large token cliff unlocks
- **Mechanism.** The supply schedule is a public, dated calendar (vesting cliffs written in token docs and
  contracts). Team and early-investor recipients sell, and team unlocks are the worst. The size is known in advance
  as a share of circulating supply. Keyrock's study of 16k unlock events (Dec 2024) found ~90 % negative, with
  selling starting ~30 days before; unlocks of 5-10 % of supply hit ~2.4x harder.
- **Sources.**
  - Keyrock via secondary coverage: https://cryptoslate.com/90-of-token-unlocks-drive-prices-down-declines-begin-a-month-ahead/
    and https://beincrypto.com/keyrock-research-token-unlocks/. The primary report was not found.
  - Kim 2026, "The 72-Hour Shock? ... 52 Token Unlock Events on Binance", doi:10.2139/ssrn.6632838.
  - Guo 2026, "Token Dilution and the Cross-Section of Cryptocurrency Returns", doi:10.2139/ssrn.6636258.
- **Why it is not exhausted.** Closest are round 60 (shorting new listings: squeeze tails, t 1.1-1.3) and round 61
  (weekly factors). This rule has a dated, sized event per token instead of an age-based or factor rule, and a short
  window (T-10 to T+3) instead of 30 days, which cuts squeeze exposure.
- **Instrument / data.**
  - Binance / Bybit USDT-M perps; klines and funding are already local in research/data/binance and bybit.
  - The unlock calendar is the gap. DefiLlama's emissions-adapters repo is no longer in the public DefiLlama org
    listing (GitHub API, 41 repos, none about emissions). Tokenomist needs a key.
  - Free fallbacks: (a) Coin Metrics community `SplyCur` jumps (round 48 used that API; altcoin coverage is
    limited, and realized jumps are not point-in-time); (b) reconstruct from vesting contracts via an archive RPC
    (a user decision, as in round 52).
- **Events, cost, power.**
  - About 100-300 cliffs >= 1 % of circulating supply a year among Binance perps (2022-24).
  - Costs: taker ~10 bp round trip, plus funding. Funding often turns negative before unlocks because shorts
    crowd in; charge it.
  - At m -3 % and s 15 %, 225 HOLD events are needed, so power is ~2-3.5.
- **Chance.** LIVE 2.5 %, DEMO 8 %. The data source is the first blocker, then the 2025-26 crypto decay.

### I5. Short US IPO stocks into the lockup expiry
- **Mechanism.** Underwriting contracts bar insiders from selling for 180 days (the date is in the prospectus).
  Supply at expiry is known and dated. The effect has survived because borrowing IPO stocks is expensive and scarce,
  which limits arbitrage.
- **Sources.** Field & Hanka 2001, JF, doi:10.1111/0022-1082.00334 (384 citations). Gibbs & Hao 2018, JBF,
  doi:10.1016/j.jbankfin.2017.09.018 (short sellers around expiries). "Market Efficiency and Predictable Supply
  Shocks: Short-Selling Returns Around IPO Lockups" (2026), doi:10.65161/recvzh0gzw5oq55hc.
- **Why it is not exhausted.** Round 41 summed lockups into weekly *index-level* issuance pressure (a hot-market
  indicator). Rounds 54-57 traded large-cap CFDs only, where costs were ~20-24 bp. This idea is per-stock, small and
  mid caps, at an effect of 100-300 bp.
- **Instrument / data.**
  - US stocks via IB with borrow; the borrow fee is the cost to model.
  - Dates come free from EDGAR: 424B4 filing date + the lockup term in S-1 text (EDGAR worked in rounds 41-47).
  - Prices for small IPO names are **not** in Dukascopy's 263 CFDs, and stooq bans bots. Needs a price source (user
    decision).
- **Events, cost, power.** 150-300 IPOs a year (2021 high, 2022-23 low). At m -2 % and s 13 % net of borrow, power
  is ~1.5-2.6.
- **Chance.** LIVE 1.5 %, DEMO 6 %.

### I6. A-share daily price limit + T+1: the day after the first limit-up (long only via Stock Connect)
- **Mechanism.** The exchange rule caps the daily move at +-10 % (main board), and T+1 forbids same-day selling, so
  unmet demand at the limit rolls into the next session. The timing is mechanical (next open). Chen, Gao, He, Jiang
  & Xiong document large investors buying into limit-ups and selling to retail the next day ("destructive"
  behaviour), so the side after the open is predictable (fade). Chinese retail lore (打板, 首板次日溢价) says the
  same.
- **Sources.** Chen, Gao, He & Jiang 2019, J. Econometrics, doi:10.1016/j.jeconom.2018.09.014. "Post-hit dynamics
  of price limit hits in the Chinese stock markets", Physica A 2017, doi:10.1016/j.physa.2016.08.048. ChiNext limit
  relaxation, Econ. Letters 2022, doi:10.1016/j.econlet.2022.110509.
- **Why it is not exhausted.** No round traded A-share single stocks (rounds 37 and 40 used Connect flows and margin
  data at index level). The closest is round 56's stock reversal in the US; this one is driven by an exchange rule
  and a settlement rule.
- **Instrument / data.**
  - Northbound Connect via IB; long only, and ChiNext / STAR are restricted. If the edge is a fade, longs cannot
    take it, so the declared test must use the long-side continuation only.
  - Eastmoney kline: `push2his.eastmoney.com/robots.txt` = `Disallow: /`, so **not allowed**.
  - Sina: robots 404 (no file). Tencent `web.ifzq.gtimg.cn`: no robots file (a JSON error). Usable in principle;
    check the robots of the actual data host first.
- **Events, cost, power.** Thousands of stock-days a year, but on ~240 dates with strong within-date correlation.
  Costs: stamp duty 0.05 % on sells (0.1 % before 2023-08), commission ~3 bp, and a tick of 0.01 CNY (~10 bp on a
  10-CNY stock). Power 1-3.
- **Chance.** LIVE 1.5 %, DEMO 5 %.

### I7. VIX ETP calendar-roll component
- **Mechanism.** Long-vol ETPs (VXX, VIXY, UVXY) must move a fixed slice of exposure from M1 to M2 at each daily
  settlement; inverse ETPs do the opposite. Prospectus rules make the size known in advance. Todorov splits ETP
  demand into leverage, calendar and flow rebalancing, and finds an ETF-related component in VIX futures prices.
- **Sources.** Todorov 2023, RoF, doi:10.1093/rof/rfad038. Avellaneda et al. on ETN roll arbitrage (SSRN 3028910):
  https://math.nyu.edu/inmemoriam/avellaneda/SSRN-id3028910.pdf. Simon & Campasano 2014 (the VIX futures basis).
- **Why it is not exhausted.** Round 34 tested *leverage-rebalancing doses* (ProShares 2006-24), including VIX, and
  round 9 found short vol = beta. This idea isolates the *calendar* roll in an M1/M2 spread, which hedges out the
  level of volatility. Todorov says leverage rebalancing has the largest effect, so the roll alone may be small.
- **Data.** CFE daily files `cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<expiry>.csv`
  returned 200 for 2014 and 2024 expiries, keyless. There is no robots.txt (S3 AccessDenied). ETP shares outstanding:
  ProShares history from round 34 (UVXY, SVXY); VXX is not covered.
- **Events, cost, power.** ~250 days a year, 2009-24. The spread costs ~1-2 ticks (0.05) per leg. Daily spread
  returns are autocorrelated and VIX-shock-heavy, so power is ~1-2.
- **Chance.** LIVE 1.5 %, DEMO 4 %.

### I8. Taiwan attention / disposition stocks (注意股 / 處置股)
- **Mechanism.** TWSE rules flag stocks whose recent returns, turnover or concentration breach published thresholds.
  On a repeat, they move them to "disposition": call auctions every 5-20 minutes, full prepayment and no margin for
  5-10 days (5 days and ~2-minute auctions since 2026-08). Designation can be predicted a day ahead from the
  published criteria. Forced cooling hits day traders and margin longs.
- **Sources.** NCCU thesis on first-time disposition 2020-22:
  https://thesis.lib.nccu.edu.tw/detail/b4a7f7a19a881b2ad6fdddfc4e644144/. The 2026 rule change:
  https://money.udn.com/money/story/5607/9775106. Practitioner write-ups: https://www.esunsec.com.tw/article/post/63.
- **Why it is not exhausted.** Round 35 used TAIFEX / TWSE investor flows at index level, not stock-level exchange
  rules.
- **Data.** `twse.com.tw/robots.txt` allows everything except /epaper/ and /FTSE/. `exchangeReport/STOCK_DAY`
  returned 200, keyless (2330, Jan 2024). The announcement history endpoint is to be confirmed.
- **Cost, tradability.** Sell tax 0.3 % + commission 2 x 0.1425 % = ~58 bp round trip. Foreigners need a FINI
  registration with a local broker (IB does not cover TWSE); a user decision. The 2026-08 rule change is a structural
  break inside HOLD.
- **Chance.** LIVE 1 %, DEMO 4 %.

### I9. Japanese shareholder-perk record dates, TOPIX-hedged
- **Mechanism.** Retail investors must hold on the last cum-date (権利付最終日) to get perks, so they buy before it and
  sell on the ex-date. The arbitrage (優待クロス: buy cash, short via 制度信用) is limited by the JSF borrow-fee auction
  (逆日歩), a rule-set cost. The dates are a public calendar.
- **Sources.** Huang, Rhee, Suzuki & Yasutake 2016, "Shareholder Perks in Japan: Price Movement and Trading Volume
  Around Ex-Benefit Days", doi:10.2139/ssrn.2777549. "The Effects of Shareholder Perks on Equity Pricing in Japan"
  2026, doi:10.2139/ssrn.6066667.
- **Why it is not exhausted.** Round 25's lore covered Tokyo first / last trading days at index level (JA-21); no
  round traded JP single stocks.
- **Data.** No robots-allowed keyless JP daily price source confirmed:
  - kabutan robots 403;
  - kabuoji3 `Disallow: /` for `*`;
  - stock-marketdata.com allows bots (used in round 45), but per-stock price coverage is unverified;
  - the J-Quants free plan needs an account (user decision);
  - the JSF site allows bots (borrow-fee data).
- **Events, power.** ~1.5k firm-events a year on ~20 dates, ~40 % in March. Perks are being abolished since 2022.
  Power 0.8-1.5.
- **Chance.** LIVE 1 %, DEMO 4 %.

### I10. Single-stock leveraged ETF rebalancing into the close
- **Mechanism.** A 2x single-stock ETF must buy AUM x (L^2 - L) x the day's return at the close, a rule in the
  prospectus. Relative to the stock's ADV this can be 10-50x the index LETF ratio, for example for MSTR, TSLA, NVDA
  and COIN.
- **Sources.** "Rebalancing, Frictional Costs, and Returns to Levered Single-stock ETFs" 2026,
  doi:10.2139/ssrn.7383378. Background: Cheng & Madhavan 2009. Todorov 2023 (above).
- **Why it is not exhausted.** Round 34 covered index / commodity LETFs only (USTEC dose IS t 1.38 / VAL 2.78, then
  failed the joint HOLD).
- **Data / history.** Dukascopy M1 for the large names worked in round 55. Daily ETF shares outstanding before 2025
  are thin (issuer files are current-only; N-PORT is monthly with a lag). Funds launched 2022-24 and AUM boomed
  inside HOLD, so IS/VAL is ~2023-24 only (the new-era rule).
- **Chance.** LIVE 1 %, DEMO 3 %.

### I11. TSE margin regulation designations (日々公表銘柄 -> 増担保規制)
- **Mechanism.** TSE / JSF publish designations after the close, using published criteria. Raising the margin
  deposit requirement forces margin longs to add cash or cut, and blocks new margin buying from the next day: a
  dated, side-known forced flow.
- **Sources.** Hardouvelis & Peristiani 1992, QJE, doi:10.2307/2118391 (Japanese margin requirement changes move
  prices). Practitioner pages (no systematic evidence): https://kabukiso.com/advice/kabu00_0032.html and
  https://info.monex.co.jp/news/2026/20260528_03.html.
- **Data.** `jpx.co.jp/robots.txt` disallows nothing. A history of designations is not yet found (JPX may publish
  current lists only), and there is no JP price source (see I9).
- **Chance.** LIVE 0.5 %, DEMO 2 %.

### I12. EU ETS primary-auction supply calendar
- **Mechanism.** EEX auctions EUAs on ~4 days a week at fixed times (09:00-11:00 CET), with volumes published in an
  annual calendar. August volumes are halved; MSR withdrawals and the compliance deadline are dated. Compliance
  buyers are forced by the deadline.
- **Sources.** Umweltbundesamt 2016, "EU-Versteigerungsverfahren Handelsperiode 2013-2020":
  https://www.umweltbundesamt.de/sites/default/files/medien/378/publikationen/climate_change_15_2016_eu-versteigerungsverfahren_handelsperiode_2013-2020_0.pdf.
  Perino et al. on the MSR, doi:10.1080/14693062.2017.1360173. No peer-reviewed intraday auction-effect study was
  found.
- **Why it is not exhausted.** Round 41 covered government bond auctions only; carbon was never mined.
- **Data.** EEX robots allow everything (auction results downloadable). sendeco2.com robots are empty, and its CO2
  price page holds yearly tables 2010+. Intraday EUA data is not free, and at daily resolution the auction slice
  (~3-4 Mt against ~30-50 Mt of futures volume) is lost in ~2 % daily noise.
- **Chance.** LIVE 0.5 %, DEMO 2 %.

### I13. Broker close-out deadlines before First Notice Day
- **Mechanism.** Retail brokers forcibly liquidate long positions in physically delivered futures at known
  times. IB's default is the end of the 2nd business day before FND, with contract-specific times (for example
  ZB / ZN). This is a forced, dated sale by retail longs in the front month.
- **Sources.** IB rules:
  https://www.interactivebrokers.ca/en/trading/marginRequirements/physicalDeliveryLiquidationRules.php and
  https://www.interactivebrokers.co.uk/en/trading/futures-close-out.php. Chinese exchanges impose a similar rule on
  individuals (DCE / ZCE / GFEX close before the delivery month):
  https://cj.sina.com.cn/articles/view/7209955840/1adbf320000101oucc.
- **Why it is not exhausted.** It is closest to round 39's index / ETF rolls (pressure only in the C2-C1 spread). The
  driver differs (retail close-outs), but the observable is the same spread. That is why the chance is low.
- **Data.** No free intraday or daily CME history (DataMine is paid; CME was unreachable in round 37). Chinese data:
  SHFE / DCE daily files exist, but foreigners cannot trade most of those products.
- **Chance.** LIVE 0.5 %, DEMO 2 %.

### I14. Month-end PTAX battle (Brazil), side from B3 positioning by investor type
- **Mechanism.** B3 dollar futures and NDFs settle on the PTAX of the month's last business day. PTAX is the BCB
  average of four 10-minute windows. Holders push the windows toward their side ("disputa pela Ptax"). The side
  could come from B3's daily open interest by participant type (for example, foreign net long dollar futures). The
  structure is like gotobi: a dated fix with a known side.
- **Sources.** Practitioner reports:
  https://www.seudinheiro.com/2018/mercados/comprados-e-vendidos-brigam-pela-formacao-do-cambio-ptax/ and
  https://blocktrends.com.br/ptax-fim-de-mes-disputa-cambial-dolar-junho-2026/. No academic study found
  (Crossref / OpenAlex PTAX queries came back empty).
- **Data.** The BCB PTAX OData API returned 200, keyless (www.bcb.gov.br robots allow everything; olinda's
  robots.txt gave 502). Intraday USDBRL is not free. Whether B3 participant-type files are free is unverified.
- **Power.** 12 events a year, so LIVE is impossible by arithmetic. DEMO at most. The instrument (CME 6L) is thin.
- **Chance.** LIVE 0.3 %, DEMO 3 %.

## Considered and dropped (no IDEAS slot)
- Japanese ETF distribution selling in July (分配金捻出売り, est. ¥0.8-1.2 trn on Jul 8 / 10:
  https://www.matsui.co.jp/fund/column/etf-dividends/) and dividend-reinvestment futures buying on the March /
  September ex-dates. Real and dated, but 1-2 events a year: no power.
- Korean year-end large-shareholder tax selling (대주주 양도세; individuals sold ~KRW 3 trn on 2021-12-28; threshold
  raised to KRW 5 bn in 2023-12: https://economist.co.kr/article/view/ecn202112290009). One event a year, the
  regime changes with the threshold, and KRX data needs a login.
- EM local-bond index rebalancing (JPM GBI-EM weight changes, Pandolfi & Williams 2019, JFE,
  doi:10.1016/j.jfineco.2018.10.008). Month-end FX flows with a known side, but the index weights are proprietary
  (user decision, paid), and the month-end FX family is mostly exhausted.
- Predictable month-end Treasury returns (Hartley & Schwarz, doi:10.2139/ssrn.3440417). 12 a year; round 13 already
  found index extension does not move FX / gold / US30. A Treasury-futures leg is DEMO at most.
- Chinese commodity limit-lock / forced position reduction (强制减仓). Foreigners cannot trade most products, and
  offshore twins already price the move.
- Taiwan CBC close management (尾盤): no free intraday TWD, and TWD is not offered at IB.

## Data reachability summary (2026-10-31, one request each; see requests.log)
| source | robots.txt | probe | verdict |
|---|---|---|---|
| gamma-api.polymarket.com | 404 (none) | 200, date filters work | usable |
| clob.polymarket.com prices-history | 404 (none) | 200 for a 2023 token, hourly; long windows give 400 | usable, chunked; CLOB from ~2022-11 |
| api.elections.kalshi.com | 404 (none); kalshi.com robots 429 | 200, but no pre-2025 weather markets returned | pre-2025 history unconfirmed |
| cdn.cboe.com VX daily files | none (S3 AccessDenied) | 200 for 2014 and 2024 expiries | usable |
| twse.com.tw | allows (except /epaper/, /FTSE/) | STOCK_DAY 200 | usable |
| push2his.eastmoney.com | `Disallow: /` | not requested | not allowed |
| www.eastmoney.com | allows | - | other hosts: check per host |
| money.finance.sina.com.cn / web.ifzq.gtimg.cn | 404 / no file | - | check the data host before use |
| olinda.bcb.gov.br PTAX | 502 on robots (www.bcb.gov.br allows) | 200 | usable |
| jpx.co.jp / jsf.co.jp / stock-marketdata.com | allow | JPX page 200 | usable, but no JP price history found |
| kabuoji3.com | `Disallow: /` for * | - | not allowed |
| kabutan.jp | 403 | - | not allowed |
| finance.naver.com | `Disallow: /` | - | not allowed |
| eex.com / sendeco2.com | allow | sendeco2 page 200 | usable (daily only) |
| DefiLlama emissions-adapters | - | not in the public org (GitHub API) | no free unlock calendar found |
| www.ember-energy.org | Cloudflare challenge | - | not usable |

## Search budget used
- 11 web searches (limit 25): Kalshi rules, JP ETF July selling, Chinese delivery-month rules, Keyrock unlocks,
  Taiwan disposition, IB close-out, Korean year-end tax, PTAX, 増担保規制, EUA auctions, VIX ETP roll.
- 27 Crossref + 27 OpenAlex topic queries (`code/queries1.tsv`, `code/queries2.tsv`; outputs in the scratchpad
  `I/lit1.tsv`, `I/lit2.tsv`) and 12 OpenAlex abstract lookups.
- No arXiv export API, no e-mail or mailto in any request.

## Suggested hand-off order for the coordinator
1. **I1 + I2 together** (one Polymarket loader).
   - Pull gamma markets with an end date of 2022-11-01..2024-12-31, then CLOB hourly histories with endTs <=
     2024-12-31.
   - Declare the T-24 h favorite rule and the post-outcome lag rule with one trade per parent event.
   - Grade on excess over DFF.
   - Before declaring, write the HOLD-contamination note from "Answer first" into HYPOTHESES.
2. **I3**, only after one candlestick request proves Kalshi weather prices exist for 2022-24. Otherwise park it as
   "forward-log only".
3. **I4**, as soon as a point-in-time unlock calendar exists (needs a user decision: a Tokenomist key or an archive
   RPC). Prices and funding are already local.
4. **I7** (free CFE data, quick to test).
5. **I5, I6 and I8-I10** each need a user decision first (data or venue). List them under "needs the user", in that
   order of value.
