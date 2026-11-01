# Round 52: census of untested mechanisms against 51 rounds, 2026-10-30

Brief: [round52_lit_census/BRIEF.md](round52_lit_census/BRIEF.md). Same LIVE / DEMO bars as rounds 25-51. Phase 1 only
(09:27-09:45 UTC): no price data loaded, HOLD untouched; the only events pulled (Tron USDT mints / burns) were cut at
2024-12-31 at parse.

## Answer
No open item cleared the phase-2 gate (expected LIVE chance >= 2 % with free data), so nothing was graded. The census
swept 2018-24, the one window no earlier census covered in full: 48,633 Crossref titles (30 journals + NBER / Fed
Board) and 797 arXiv q-fin 2024 titles, 426 read by title after a timing-by-asset filter. All but one are tested
families, volatility / jump models without a side, single-country markets or data IC lacks. The exception is Z1, Tether
mint -> long BTC for 5-30 minutes (Saggu 2022, FRL 49:103096: +24 to +68 bp, 2014-21; round 7 C tested daily issuance
only). Z1 fails the gate on events, not size: only Tron mints are free from this Mac (248 in 2019-24; ~28 >= $10M in
HOLD), so HOLD power 3 needs ~20 bp net per event and >= 40 % of the paper's size surviving into 2025-26.

| # | mechanism | status | LIVE / DEMO chance |
|---|---|---|---|
| Z1 | USDT mint -> long BTC 5-30 min (block timestamp + 2 min) | open; Tron only free | ~1-1.5 % / ~5 % (with Ethereum mints ~2.5 % / ~10 %) |
| Z2 | MicroStrategy Monday 8-K purchases -> BTC sell the news | open, ~12 events 2020-21 | < 0.5 % / ~2 % |
| Z3 | USDC mints -> BTC | needs Ethereum logs | < 1 % / ~3 % |
| Z4 | Japanese dividend-reinvestment futures buying (Mar / Sep) -> JP225 | open, 2 a year | 0 / < 1 % |
| Z5 | Leveraged single-stock ETF rebalancing -> USTEC | no IS era (2024+) | < 0.5 % / ~1 % |
| Z6-Z9 | Baker Hughes rig count, OPEC days, rate-lock hedging, USDCNH policy lines | priced / no side / near-tested | < 0.5 % |
| Z10 | Ewald et al. 2025 Brent windows | paywalled | ~1 % / ~3 % |

Detail and the full list: [CENSUS_Z.md](round52_lit_census/CENSUS_Z.md).

## Pitfalls
- export.arxiv.org robots.txt disallows everything (round 23 had used it); use arxiv.org /list pages (15 s delay).
- apilist.tronscanapi.com disallows ClaudeBot / anthropic-ai / Claude-Web by name; api.trongrid.io has no robots file.
- Ethereum public RPCs: publicnode 403 (token), drpc free plan refuses logs, llamarpc 525, cloudflare-eth caps at 800
  blocks (~21k requests for 2017-24, ~6 h: not run).
- Z1 design: mints follow demand (control with random entries matched on the prior-hour BTC return and a "BTC rose,
  no mint" placebo); use block time; cluster mints within 60 min; IC BTC closed at weekends until 2024-04.

## Directions that need the user
| direction | value |
|---|---|
| Single-stock CFDs on MT5 (blackout, insider, buyback, earnings flows) | LIVE ~3-5 %, DEMO ~25 % (unchanged, most valuable) |
| Ethereum archive-RPC token (or ~6 h of Cloudflare queries) for Ethereum USDT / USDC mint times | LIVE ~2.5 %, DEMO ~10 % |
| Ewald et al. 2025 full text; paid Whale Alert / labelled exchange flows | ~1 % / ~3 %; < 1 % / ~2 % |

## State after round 52
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 53 grades Z1 on the free
Tron (and, if free, Omni-layer) mints: below the gate, but cheap, and it prices the Ethereum-token decision.
