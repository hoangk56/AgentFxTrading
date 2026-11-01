# Round 56 brief: short-term cross-section of IC-listable US large caps (no-news reversal, news continuation) from the daily panel on disk

Written 2026-10-30 12:10 UTC. Continues the user-approved single-stock CFD direction (2026-10-30). Research only: no
MT5 account, bot or deploy. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds 25-55 (LIVE /
DEMO in research/PROMPT.md; no RELAXED tier); fixed constraints: lot not capital-dependent, hold <= 5 days, <= 3
positions per bot (state the bots needed: a long-short book of k names needs ceil(k/3) bots). Everything in
research/results/portfolio/round54_single_stocks/BRIEF.md applies (network rules, HOLD cut, costs, what to return),
except the stream, the round folder (research/results/portfolio/round56_stock_cross_section/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r56/<stream>/`).

Read first: research/results/portfolio/round54_single_stocks_2026-10-30.md and round55_insider_intraday_2026-10-30.md
(cost lesson: IC's $0.02 / share commission is ~12 bp a round trip, ~20 bp all-in at a close fill; the daily open
candle is not tradeable), round54_single_stocks/DATA_D.md (panel, splits, stocklib, pitfalls), and the round 54
scratchpads (read only): `.../scratchpad/r54/D/out/` (stocks_daily.npz, symbols.csv, splits.csv, stocklib.py) and
`.../r54/E/out/events.csv` (8-K item 2.02 acceptance dates / times for ~204 firms = the news days). Round 2 / 7 / 11
tested momentum / reversal cross-sections on FX and indices only; no round ranked single stocks.

**Speed:** no download is needed. If you want news days beyond 8-K 2.02 (e.g. all 8-K filings from EDGAR submissions
JSON already used by rounds 47 / 54), keep any pull under ~30 minutes (data.sec.gov, generic research UA, no email,
>= 0.15 s). Grade within ~1 hour. Never load a row on or after 2025-01-01.

## Stream
| stream | direction | detail |
|---|---|---|
| R | **Short-term reversal of large-cap moves without news vs continuation of moves with news (Chan 2003; Da, Liu & Schaumburg 2014 "news-adjusted reversal"; Lehmann 1990; Nagel 2012 reversal as liquidity provision, larger when VIX is high).** | Universe: the ~221 stocks of D (ETFs only as hedges / sector benchmarks: map each stock to a sector ETF if one in D fits, else SPY). Signal at the 15:55-ish close of day t (use D's close bid / ask; enter at the same close at the ask / bid, the only tradeable daily fill): residual return over 1 and 5 days (stock minus beta x SPY, or minus its sector ETF, declared), ranked in the cross-section. Declared before returns, sides from the literature: (1) no-news losers long / no-news winners short (news = 8-K 2.02 within [t-k, t] or another declared filter), hold 1, 3, 5 days; (2) news-day movers follow (continuation) as the alternative family; (3) a VIX / market-drawdown conditional variant (Nagel) as a declared variant only. Book: top / bottom k (k = 3, 6, 9; bots = k/3 per side) equal-dollar, market-neutral by construction, or each leg hedged with SPY / US500. Costs: close spreads from D, USD 0.02 / share / side, financing per night (stocklib), x1.5 spread, +1 day delay. Controls: random same-day picks from the universe, ex-2020-03/04, by year, chance benchmark over cells (max-t null from shuffled ranks), PRE (2016-17) if data allows. Turnover and per-trade net must both be shown. Count trades, power first (HOLD 21 months). |

One stream; up to 2 heavy Python processes (under ~3 GB RAM each). If a cell meets DEMO or LIVE numbers, write
PREREG_DRAFT_R_*.md (including the IC MT5 symbol check and the dividend caveat) but do NOT open HOLD.
