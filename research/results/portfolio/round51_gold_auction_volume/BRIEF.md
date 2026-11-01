# Round 51 brief: LBMA gold / silver auction volume, rounds and imbalance as a dated signal

Written 2026-10-30 09:21 UTC (round 50 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-50 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round51_gold_auction_volume/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r51/<stream>/`).
Also read the round 37-50 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-9]_*_2026-10-30.md, round50_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect
robots.txt (a site that disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com,
data-api.ecb.europa.eu); **a 403 / bot-wall / Access Denied is a stop: never retry with a browser User-Agent or any
other disguise** (round 50 tried once on ici.org and was refused); any row after 2024-12-31 is cut at parse or load,
before anything is printed.

**Speed (the user is waiting):** first find, in under ~10 minutes, whether per-auction volume / number of rounds /
participants are published free for 2015-24 (LBMA / ICE Benchmark Administration pages or JSON). If not, say so and
stop with a short report (no fallback grid is required). Keep any pull under ~1 hour. Background jobs log progress,
and every wait also exits when its worker dies (check by PID).

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| L | **Per-auction LBMA gold (10:30, 15:00 London) and silver (12:00) volume, number of rounds, and the final-round imbalance / price move during the auction -> XAUUSD, XAGUSD.** The auction result (price, volume, rounds) is public at the auction's end: state the publication time. Declared families, sides fixed before returns: (1) large imbalance / many rounds (a big one-sided order filled in the auction) -> continuation in the auction's direction for 15 min to the NY close (information) vs reversal (liquidity), primary by mechanism (state it); (2) unusually high auction volume vs the trailing 60 auctions -> post-auction drift in the price-change direction; (3) the prior-day silver / gold volume as an ex-ante condition for the known pre-auction drop (rounds 10 / 12: silver falls into the 12:00 auction, +2.7 bp t 8-9 at mid, below IC cost): does high expected volume scale the drop >= 3x? Count auctions (~250 a year each) and do the power arithmetic first. | round 10 V / round 12 (auction-minute scans: the silver pre-auction drop is real at mid but below cost), round 6 (settlement flows), round 27-28 (gold $50 levels), round 33 (SGE premium). No round used auction volume, rounds or imbalance. | The auction concentrates large physical / bank orders on a public clock; its size and imbalance are published at once and are not in the price series, and the gold leg's 15-minute-to-close drift needs only a few bp over IC's ~2-3 bp gold cost at the auction minute. |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each).
