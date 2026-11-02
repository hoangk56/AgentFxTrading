# Stream J (round 65): scout the next wave, plan

Written 2026-11-01 11:16 UTC (from `date -u`: Sun Nov 1 11:16:05 UTC 2026), before any request or count.
Scouting only: no returns are computed, no price series is loaded, HOLD (2025-01-01..) is never requested. Event
counts use only records dated < 2025-01-01; HOLD event rates are extrapolated from 2024, never counted.

## What the next wave must satisfy (from BRIEF, PROMPT, registry, round 64)
- A persistent behavioural or institutional flow with a dated timing (C3 gotobi, K2 Upbit listing chase), not a
  microstructure edge that bots can take (F, P2, carry, funding spreads all decayed in 2025-26).
- Enough independent HOLD events: power = VAL Sharpe per trade x sqrt(n HOLD) >= 3. At K2's 0.25 that is ~150 HOLD
  events (~80 a year); at 0.10 it is 900.
- Free point-in-time data for 2016-24 (crypto 2020-24) and a venue the user can trade.
- Not one of the `tried:` directions or the exhausted families, nor one of round 63 I's 14 ideas unless the
  construction differs materially.

## Candidate list to check (mechanism -> data check planned)
1. Binance spot listing of a coin whose Binance perp is already >= 7 days old (perp-first coins): Binance's own
   retail spot base gets access, K2-style chase. Data: local `binance/spot_first.csv` + `perp_1d` (count events by
   year < 2025; no network). Round 63 D failed for want of announcement times; the first spot kline needs none.
2. Upbit BTC-market and USDT-market listings (not KRW) of coins with a Binance perp, and the K2 event list rebuilt
   from Upbit's own listing notices (adds coins later delisted, which K's /v1/market/all list misses). Data:
   api-manager.upbit.com notices (stream W showed it is allowed; I log my own robots + one list request) and W's
   cached list pages (titles only, < 2025) for counts.
3. Upbit airdrop-support / snapshot notices (holder record dates, the crypto twin of round 63 I9 perks): Korean
   retail buys before the snapshot, sells after. Same notice source.
4. Upbit deposit / withdrawal suspension of a coin (arbitrage door shut) as a dated local squeeze: count only; likely
   un-tradable (the premium closes on Upbit, K1).
5. Binance funding-interval switch (8 h -> 4 h / 1 h when funding hits the cap): a rule event that multiplies the
   crowded side's carrying cost. Data: local funding files (count interval changes by year < 2025).
6. Hong Kong CBBC mandatory-call clusters (retail CBBC, issuer hedge unwind at known call levels) -> HK50. Data:
   HKEX CBBC daily files (robots + one file).
7. Nikkei leveraged / inverse ETF (1570, 1357, 1458, 1459) close rebalancing, dose = AUM x (L^2 - L) x return ->
   JP225 into the Tokyo close. Round 34 used ProShares (US) doses only. Data: issuer daily NAV / assets pages
   (robots + one request).
8. Turkish retail flight into USDT: BtcTurk USDT/TRY premium over USDTRY -> USDTRY next session. Data: BtcTurk graph
   API (robots + one request ending 2024) and Dukascopy USDTRY (robots + one hour file).
9. Coinbase "roadmap" / asset-addition announcements (the US retail pump happens at the announcement, which is why
   stream L found none at the first candle). Data: Coinbase blog / status sources (robots + one request).
10. Leveraged-token rebalancing (Binance BLVT, FTX, Bybit) at the daily rebalance on big-move days -> perps. Data:
    spot klines of BTCUP/BTCDOWN on data.binance.vision (robots + one file), AUM history doubtful.
11. S&P 500 / Nasdaq-100 additions and deletions on the Dukascopy large-cap CFDs (rule-based index fund demand).
    Data: Wikipedia change tables (robots + one API request).
12. Gotobi-like settlement flows in other currencies (KRW month-end nego, TWD, CNH, INR, THB): check whether any has a
    tradable instrument with free intraday history; expected to drop.

## Method
- One request per source, robots.txt first, logged in research/data/scout_j/requests.log (UTC time, URL, status,
  bytes); bodies under research/data/scout_j/<host>/, parsed with `python -I`; >= 0.25 s per host; no e-mail, no key;
  403 = stop. At most 15 WebSearch (budget planned: ~8).
- Code in J/code/ (probe.py for requests, counts.py for local / cached event counts).
- Power arithmetic: per-trade Sharpe guess from the nearest tested analogue (K2 VAL 0.25, F VAL ~0.14, C3), events per
  year from counts; P(LIVE) / P(DEMO) include the chance that data or venue fails.
- Output STREAM_J.md: ranked table first, then one section per hypothesis (forced flow, timing, side, instrument, data,
  why new), dropped ideas, request summary.
