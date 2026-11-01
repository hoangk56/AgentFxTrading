# Round 53 brief: Tether (USDT) mint events -> BTC over the next 5-60 minutes

Written 2026-10-30 09:46 UTC (round 52's census left this as the only open mechanism; below its 2 % gate, but cheap,
and it prices the Ethereum-token decision). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds
25-52 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round53_usdt_mints/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r53/<stream>/`).
Network rules: **no web.archive.org**; respect robots.txt (ClaudeBot / anthropic-ai disallowed = off limits, e.g.
apilist.tronscanapi.com, cftc.gov); **a 403 / token wall / bot-wall is a stop, never retry with a browser User-Agent**;
no logins, no API keys; never an email address in a request; any row after 2024-12-31 is cut at parse, before anything
is printed.

**Speed (the user is waiting):** the Tron mints are already on disk
(`.../scratchpad/r52/Z/web/tron/tron_Issue.tsv`, `tron_Redeem.tsv`; read r52 CENSUS_Z.md for how they were pulled).
Optionally add Omni-layer USDT grants 2017-19 if a free, robots-allowed explorer API gives them in under ~20 minutes;
no Ethereum log scans this round. Grade within ~1 hour.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| M | **USDT mints (block timestamp) -> long BTCUSD from block time + 2 min for 5 / 15 / 30 / 60 min (ETHUSD second leg); burns as the declared mirror (short), both declared.** Sides and horizons from Saggu 2022 (FRL 49:103096: +24 to +68 bp over 5-30 min, 2014-21, faded by 60 min; burns no effect). Declared before returns: size filter (e.g. >= $10M and a "treasury refill" exclusion if stated in the paper), clustering of mints within 60 min, entry rule, cost at the actual IC bars, and IC's weekend closure until 2024-04 (weekend mints dropped, say how many). Controls: random entries matched on time of day / weekday and on the prior-60-minute BTC return; a placebo of "BTC rose by the same amount in the prior hour with no mint". Use Binance spot or another 24/7 free M1 source only as a mid-price diagnostic for weekend events, never for net. Count events per year by era first and do the power arithmetic (HOLD ~28 Tron events >= $10M). | round 7 C and round 12 C (daily / weekly stablecoin issuance: excluded), round 31 C (CoinMetrics flows not point-in-time), round 48 N (network fundamentals: none), round 52 Z CENSUS_Z.md (Z1 design and pitfalls). No round traded single mint events at minutes. | Mints are dated to the second on-chain and reflect fresh fiat entering exchanges; the paper's size (24-68 bp) is far above IC's BTC cost in VAL (~3-5 bp). The question is whether it survives the demand-follows-price confound and the post-2021 decay. |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each).
