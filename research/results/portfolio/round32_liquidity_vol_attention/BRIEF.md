# Round 32 brief: US fiscal and central-bank liquidity tables, implied volatility of other assets, public attention

Written 2026-10-27 18:42 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as
rounds 25-31 (the user's LIVE and DEMO bars in research/PROMPT.md; no RELAXED tier).

**Why this round exists.** The user asked on 2026-10-27 to keep researching until a LIVE algorithm is found, using other
sources. Round 31 (round31_new_sources/) opened public non-price data: Japan's flow and positioning tables (stream J)
and practitioner communities (stream P) gave nothing; streams C (crypto on-chain / Binance positioning) and G (gold
ETF holdings, natgas weather) may still be running while you work. This round takes three more public sources no round
has loaded, each reachable from this Mac (probed 2026-10-27 18:40 UTC).

**Everything not changed here follows research/results/portfolio/round31_new_sources/BRIEF.md**: read it first,
including its "Read first" list, Data section (HOLD 2025-01-01..2026-09-24 closed, new series cut at 2024-12-31 at
load), network rules (no accounts / logins / payment, robots.txt, >= 1 s between requests to one host, no e-mail in
any request, downloads under `web/` parsed with `python -I`, every fetch logged), test rules, PREREG_DRAFT rule and
what to return. Also read round31_new_sources/STREAM_J.md and STREAM_P.md (what round 31 already found) and, for
your stream, the earlier rounds named in your row.

## Streams
| stream | direction | why it might escape the limits | already done (don't redo) |
|---|---|---|---|
| L | **US liquidity and fiscal cash flows.** Daily Treasury Statement via api.fiscaldata.treasury.gov (TGA balance, daily tax deposits by type, large withdrawals, debt issuance / redemption cash), NY Fed reverse-repo daily results (markets.newyorkfed.org API), Fed H.4.1 weekly reserves / balance sheet. Practitioner thesis "net liquidity = Fed assets - TGA - RRP drives equities" (2021-23), and the cash-drain mechanism: large known TGA rebuilds / drawdowns (debt-ceiling episodes, tax dates) move reserves, which dealers and funds must fund. Targets US500, US30, USTEC, US2000, XAUUSD, EURUSD, USDJPY; horizons 1-5 days. Signals from data published before the entry (DTS is published ~16:00 ET the next business day: use the publication lag). | The size of the drain is public and often scheduled (tax dates, debt-ceiling resolution, quarter-ends), so the flow's dose is known in advance like gotobi. Not tested as a dose / level signal. | round 13 N settlement-day dummies (Treasury coupon / bill settlement, tax dates: nothing); round 22 TRIAGE R7 reserve-scarcity conditioning (low prior); round 9 FRED macro (42 series) |
| V | **Implied volatility of other assets and option-market shape.** CBOE daily index history (cdn.cboe.com/api/global/us_indices/daily_prices/<IDX>_History.csv, follows a 307): GVZ (gold), OVX (oil), EVZ (EUR), VXN, VXD, RVX, VVIX, SKEW, VIX9D, VIX1D where it exists. Hypotheses: implied-minus-realised gap per asset (the asset's own variance risk premium) predicting its 1-5 day return, the asset vol rising while VIX does not (asset-specific stress), SKEW / VVIX as crash-hedging demand, cross-asset vol spreads. Targets XAUUSD, XAGUSD, XTIUSD, XBRUSD, EURUSD, USTEC, US30, US2000. | Option dealers' hedging and the premium paid for insurance are flows with a public price; VRP timing was tested only on the S&P 500 and only as a beta. Per-asset implied vols are new here. | round 4 VIX term structure, round 9 S&P 500 VRP and VIX > 30 buying (beta, no alpha); round 10 option pinning; GEX / DIX (round 4) |
| A | **Public attention and crowd data.** Wikimedia pageviews REST API (daily per article since 2015-07; e.g. Bitcoin, Ethereum, Gold, Gold as an investment, Crude oil, Natural gas, Yen, Euro, S&P 500, Recession, Inflation, Stock market crash; per-language editions such as ja / zh / de where the language maps to a currency), and any other free crowd series you can reach without an account (GitHub activity of crypto projects, Stack Exchange, Hacker News Algolia API counts of "bitcoin" / "gold" / "recession"). Hypotheses from the attention literature (Da, Engelberg & Gao 2011; Barber & Odean 2008; Kristoufek 2013 for BTC): abnormal attention -> retail buying pressure -> short-term rise then reversal; attention to fear words -> risk-off. Targets BTCUSD, ETHUSD, XAUUSD, US500, USDJPY, EURUSD; horizons 1-5 days. | Retail attention leads retail flows by a day or more, and pageviews are published with a fixed lag; the signal is not a price pattern. Never loaded here (Google Trends is unreachable). | round 23 N / 25 C literature maps list Google Trends FEARS as not testable; round 4 / 9 Binance flows |

## Rules added for this round
- Round 31 streams C and G may still be running: use **at most 1 heavy Python process** per stream until they finish
  (check with `ps aux | grep -c "[r]esearch/.venv/bin/python"`; above 4, wait), each under ~3 GB RAM.
- Write ONLY `HYPOTHESES_<stream>.md`, `STREAM_<stream>.md` and `PREREG_DRAFT_*` in
  research/results/portfolio/round32_liquidity_vol_attention/. Scripts, data and outputs under
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/<stream>/`.
- Publication lags are part of the rule: a signal may use a value only after the time it was public (DTS next
  business day ~16:00 ET; H.4.1 Thursday 16:30 ET; RRP results ~13:15 ET; CBOE index closes 16:15 ET; Wikimedia daily
  counts for UTC day D are complete after D+1 ~01:00 UTC). Write the lag into HYPOTHESES before the first return.
- Do the power arithmetic first (round 16 STREAM_X frontier, round 10 minimum-edge table): state the per-trade edge
  your hypothesis needs for LIVE at its trade count, and what the source literature implies.
- Keep going inside your stream: an unusable or null first source is not the end; move to the next in your row and to
  related free sources you discover.
