# Stream IB (round 71): hypotheses and plan, before any request

Written 2026-11-01 18:05 UTC (`date -u`: Sun Nov 1 18:05:35 UTC 2026). Scouting only. There is no backtest, I load no
price series, and I never request, print or summarise a 2025-26 value. Every probe asks for a month <= 2024-12 or a
window that ends <= 2024-12-31.

## Question
Which edges are protected by a barrier that a retail account can cross but large bots / market makers avoid or
cannot cross? The survivors so far: C3 (dated corporate flow), B (spot borrow), K2 / A2-D5L (Upbit KRW retail plus a
seconds-level notice bot). The edges that had no barrier decayed (F, P2, carry).

## Already covered (I do not repeat these)
K1 kimchi per coin, X spot venue gap, V / N borrow routes for B, UC Upbit suspensions, S stablecoin depeg buys, J3
funding-interval switch, J5 BtcTurk USDT premium, J7 perp-first spot listing, J9 Coinbase roadmap (no list), J11 Upbit
airdrops, L1 / L7 Binance announcement stamps (Zenodo, user OK), L6 24/7 equity perps, I4 / U unlocks, N0 / N1 new
perps, D Binance notices, H-CNH CFETS close. Vietnamese stocks and VN30F are a separate program
(106.dnse-stock/docs/research, rounds R2-R24), so I do not duplicate it here.

## Candidate hypotheses (side declared now)
| id | mechanism, barrier | side | instrument / account | free point-in-time data to probe (one request each) |
|---|---|---|---|---|
| IB1 | Staking / custody wrappers (BETH before Shapella, WBETH, cbETH, WBTC) trade at a discount when holders need liquidity. The arbitrage needs the capital locked through an unstake queue or a custodian redemption (days to weeks, or impossible before 2023-04). Bots avoid locked capital, and the size is small | long the wrapper / short the ETH (BTC) perp when the discount exceeds the queue cost; exit on reversion or by redeeming | Binance spot + USDT-M perp (the user's account); Coinbase Exchange as replication | data.binance.vision spot monthly klines BETHETH, WBETHETH, WBTCBTC; Coinbase Exchange candles CBETH-ETH |
| IB2 | Fiat-rail closure: only KYC'd institutions can redeem USD stablecoins (USDC, BUSD, USDP, TUSD) at par, over bank wires, and Fedwire is closed at weekends and on US bank holidays. 24/7 rails (SEN / Signet) existed until 2023-03. So weekend sell pressure on USDC vs USDT cannot be arbitraged until Monday | buy USDC vs USDT on Friday-Sunday discounts, sell on Monday after 14:00 UTC | Binance spot USDCUSDT (fee-free stable pairs when promoted) | data.binance.vision USDCUSDT 1m / 1d monthly |
| IB3 | Local-fiat books on Binance (ALT/TRY, also BRL / EUR): Turkish retail funds by TRY rails only, so an ALT/TRY premium over ALT/USDT x USDT/TRY is a Turkish retail flow signal. Unlike K1 (Upbit, KYC-gated), the premium can be sold on the same venue with no transfer (sell ALT/TRY, buy ALT/USDT, or the pure cross trade). Capacity is small, so MMs quote it lazily | sell rich ALT/TRY, buy ALT/USDT + USDT/TRY; flatten when the premium closes | Binance spot (TRY pairs tradable on Binance global; check) | data.binance.vision ALT/TRY monthly klines (e.g. SOLTRY) |
| IB4 | Coinbase listing stamps from status.coinbase.com ("transfers available" / "trading is live" posts, timed to the minute or second). This is the point-in-time list J9 lacked. A2-D5L construction: seconds-level notice bot, long Binance perp / short BTC at notice + 5 s. Barrier: a low-latency notice bot on a feed that market makers watch less than Binance / Upbit | long the Binance perp, short BTC; exit +5 / +60 min | Binance USDT-M perp | status.coinbase.com history (Atlassian Statuspage), robots first |
| IB5 | Binance Launchpool / Launchpad farming windows. Retail locks BNB (or FDUSD) for 7-30 days to farm a new token. BNB demand builds before the snapshot / window start and unwinds after the window ends. Barrier: capital lock-up and Binance-only retail | long BNB perp / short BTC from announcement to window start; short after the end (declared separately) | Binance USDT-M perp BNBUSDT | a free Launchpool calendar (GitHub list or Binance research page); WebSearch first |
| IB6 | Onshore / offshore yuan: capital controls stop arbitrage between CNY (onshore, CFETS) and CNH. When the CNH-CNY spread is stretched, CNH converges to CNY over 1-5 days | trade USDCNH toward the onshore rate | IC USDCNH CFD (existing account) | FRED DEXCHUS (H.10 noon CNY) or SAFE / CFETS onshore close; one request |
| IB7 | Binance new spot listings open withdrawals ~24 h after trading starts. Until then, retail buying on Binance spot cannot be met by coins withdrawn to other venues (it can only be met by deposits), so the Binance spot premium vs other venues closes when withdrawals open | short the Binance-rich side via the Binance perp vs a long perp elsewhere; or simply avoid | Binance + Bybit perps | withdrawal-open times are in Binance announcements (/bapi/ forbidden); spot_first.csv is local; probe whether Bybit / OKX spot candles cover the window |
| IB8 | Binance Margin pair delistings: Binance closes the open margin shorts by force at a pre-announced UTC time (forced buy flow with a known clock). Barrier: only margin users are forced, and the clock is public | long the coin into the forced-close time, exit just after | Binance perp | announcement times (forbidden host); look for a free mirror (GitHub) via WebSearch |
| IB9 | Pre-launch perps (Hyperliquid hyperps from 2024, Bybit / Binance pre-market) converge to the spot listing price. Barrier: no spot to hedge, a funding cap and a mark price from an internal EMA | fade the pre-launch premium into the spot listing | Hyperliquid (non-custodial, no KYC) | Hyperliquid info candleSnapshot for a 2024 hyperp; forward-only if IS / VAL are empty |

## Plan
1. robots.txt of each host, then one data request per source (logged in research/data/scout_ib/requests.log: UTC
   time, method, URL, status, bytes, file). Bodies go under research/data/scout_ib/raw/<host>/. I wait >= 1 s per host,
   send no e-mail or contact header, and stop the host on 403 / disallow. I parse with `research/.venv/bin/python -I`
   (numpy only).
2. Use at most 15 WebSearch (budget: Launchpool list, Binance margin delist force-close rule, TRY pairs on Binance global,
   Circle redemption hours, WBETH listing / redemption delay, hyperps start, Binance withdrawal-open rule, CNH-CNY
   literature, LST discount literature).
3. Power arithmetic: HOLD power = per-event net Sharpe x sqrt(HOLD events, ~1.83 yr). LIVE needs >= 3. For a daily
   book I use the annual Sharpe x sqrt(1.83) >= 3, i.e. Sharpe >= ~2.2. Plausible size = half the mechanism's
   naive size, net of taker costs. P(LIVE) includes the chance that the data / venue fail.
4. STREAM_IB.md: the answer first, then a ranked table (mechanism, barrier, venue / account, data + status,
   events / yr, HOLD power, P(LIVE), P(DEMO), duplicate check), one section per idea, dropped ideas, requests.
