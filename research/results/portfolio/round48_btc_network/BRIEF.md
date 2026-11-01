# Round 48 brief: Bitcoin network fundamentals from block data (hashrate, difficulty, fees, miner revenue)

Written 2026-10-30 08:21 UTC (round 47 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-47 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round48_btc_network/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r48/<stream>/`).
Also read the round 37-47 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-7]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com, data-api.ecb.europa.eu); any row
after 2024-12-31 is cut at parse or load, before anything is printed.

**Speed (the user is waiting):** prefer one small chart / CSV endpoint per series (e.g. blockchain.com charts API,
mempool.space, Coin Metrics community: check robots.txt and terms first; no API keys, no accounts); keep the pull under
~1 hour. Background jobs log progress, and every wait also exits when its worker dies. Grade IS + VAL as soon as they
are complete.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| N | **Bitcoin network fundamentals -> BTCUSD (ETHUSD as a second leg, US500 / XAU as controls).** Daily (or per-block, aggregated to the UTC day) hashrate, difficulty adjustments (every 2,016 blocks, exact timestamps from block data), transaction fees / fee share of miner revenue, mempool congestion, miner revenue in USD (hashprice), halvings as dated regime breaks. Use only values computable at the time (block timestamps; state how each series is point-in-time: hashrate estimates are trailing; difficulty is exact). Declared families, sides fixed before returns from mechanism or practitioner rules (state sources): (1) miner capitulation / "hash ribbons" (30-day hashrate MA crossing back above the 60-day MA after a capitulation -> long; practitioner rule, Edwards 2019), and capitulation itself -> short (miners sell reserves); (2) difficulty adjustments: large downward adjustment -> miner margin relief -> less forced selling, long 1-5 days; large upward -> short; (3) hashprice shocks (USD revenue per TH falling to the trailing low) -> miner selling pressure, short 1-3 days; (4) fee / mempool congestion spikes (on-chain demand) -> continuation vs exhaustion, both sides declared, primary by mechanism. Entry at the next IC bar after the value is computable (state the UTC time), hold 1-5 days. Count signal days, do the power arithmetic first: BTC's daily sd is large and IC's cost is a small share of it, but family 1 fires a few times a year. | round 31 C (CoinMetrics exchange flows: not point-in-time; miner flows absent from the community tier), round 4 / 37 (funding), round 33 (Coinbase / kimchi premium), round 34 (Deribit options flow), round 24 A (spot ETF flows), crypto_donchian_weekend_2026-09-27.md. No round used hashrate, difficulty, fees or miner revenue. | Miner sales are a forced, mechanically timed supply (~900 BTC a day before 2024-04, ~450 after) whose pressure rises when hashprice falls below cost; difficulty adjustments are exact, public and dated; block data are immutable, so the series are point-in-time. BTC's ~350 bp daily sd makes IC's cost small at 1-5 days. Expect the folk rules to be rare and noisy: say what is left in the daily families (2)-(4). |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each). If the first construction
fails, move to related public, dated by-products in the row (declare first), as in rounds 37-47.
