# Round 51: LBMA gold / silver auction volume, rounds and imbalance, 2026-10-30

Brief: [round51_gold_auction_volume/BRIEF.md](round51_gold_auction_volume/BRIEF.md). Same LIVE / DEMO bars as rounds
25-50. The probe (09:22-09:25 UTC) stopped inside its 10-minute limit; no series was loaded, no return computed,
nothing from 2025-26 seen.

## Answer
No verdict: per-auction volume / rounds / imbalance for 2015-24 is not free. The only per-auction product (ICE
Benchmark Administration "Gold Auction Historical Transparency Reports", ice.com report 179) needs a registered IBA
account with e-mail verification; LBMA moved historic tables into a members' portal (login) on 2025-11-24; the price
JSON host (prices.lbma.org.uk) is behind a Cloudflare 403 (not retried); ice.com reports 211 / 218 are monthly
aggregates only, which cannot rank single auctions. Had data existed: ~435 auctions per fix in HOLD, so LIVE needs
~1.4 bp net per 15-minute gold trade unconditionally, or ~3 bp on a top-quintile condition.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| L | Availability of LBMA / IBA per-auction volume, rounds, imbalance 2015-24 | **not testable** without an IBA account | [STREAM_L.md](round51_gold_auction_volume/STREAM_L.md) |

## Pitfalls
- prices.lbma.org.uk is behind Cloudflare (403; robots.txt itself 401): off limits.
- ice.com: `/report-center/category/` is disallowed by robots, `/report/<id>` pages are allowed; IBA transparency
  reports are "free" for registered users only.

## Directions that need the user
| direction | value |
|---|---|
| IBA registration (ice.com report 179): per-auction round prices and volumes, probably from 2015 | LIVE < 5 %, DEMO ~5 %; costs only a registration |

## State after round 51
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 52 opens next.
