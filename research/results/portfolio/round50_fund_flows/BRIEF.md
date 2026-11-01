# Round 50 brief: aggregate mutual-fund / ETF flows and money-market fund assets (ICI weekly)

Written 2026-10-30 09:05 UTC (round 49 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-49 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round50_fund_flows/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r50/<stream>/`).
Also read the round 37-49 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-9]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com, data-api.ecb.europa.eu); any row
after 2024-12-31 is cut at parse or load, before anything is printed.

**Speed (the user is waiting):** ICI publishes small weekly / monthly spreadsheets; keep the pull under ~1 hour.
Background jobs log progress, and every wait also exits when its worker dies. If ICI's history is not reachable
without an account or before 2016, say so at once and move to the by-products below. Grade IS + VAL as soon as they
are complete.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| F | **ICI weekly estimated long-term mutual-fund flows (domestic / world equity, taxable / municipal bond, hybrid), weekly ETF net issuance, and weekly money-market fund assets (retail / institutional) -> US500, US2000, USTEC, XAU, EURUSD, USDJPY.** Release times: state them from ICI (flows Wednesday afternoon ET for the week to the prior Wednesday; MMF assets Thursday afternoon ET). Declared families, sides fixed from the literature before returns: (1) Ben-Rephael, Kandel & Wohl 2012 (JFE): net exchanges from bond to equity funds -> temporary price pressure then reversal: high equity-minus-bond flow z -> short US500 / US2000 1-5 days after release (primary), with the continuation side declared as alternative; (2) Coval & Stafford-style fire sales at the aggregate: extreme equity-fund outflows -> long after release (liquidity provision); (3) money-market asset surges (risk-off cash hoarding) -> long equities 1-5 days (cash on the sidelines) vs flight-to-safety continuation, primary by mechanism; (4) world-equity flows -> USD (repatriation): outflows from world equity funds -> USD up vs EUR / JPY. Weekly: count releases, say from the count that LIVE is impossible unless the per-trade Sharpe is very large, state what DEMO needs, and pool families into one declared book if needed for power. | round 44 T (TFF positioning), round 39 D (COT small traders, JPX investor types), round 38 S (ETF creations / FINRA), round 45 X (pooled weekly / daily non-price features), round 13 (structural money-market channels). No round used ICI fund flows or MMF assets. | Fund flows are the retail / institutional demand the managers must execute, reported with a short lag on a public clock; the literature finds price pressure that reverses within weeks, inside the 5-day limit at the short end. Weekly, so DEMO at most: expect it to be small and say so. |

By-products if ICI is unreachable (declare first): Federal Reserve H.8 / Z.1 are too slow (say so); the weekly Fed H.6
money stock (M2 components incl. retail MMF) as a substitute for (3).

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each).
