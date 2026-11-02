# Round 70, stream LIT: literature scout 2025-26 (plan, written before any request)

Written 2026-11-01 17:22 UTC (`date -u` at 17:22:11). Scouting only: no price series loaded, no backtest, HOLD
(2025-01-01..) never requested. Brief: [../BRIEF.md](../BRIEF.md), section "Stream LIT".

## Question
Which 2025-26 papers / working papers describe a price effect driven by (a) retail flows, (b) exchange
announcements, (c) rule-based flows, or (d) settlement mechanics that is testable with free point-in-time data
before 2025 and tradable by a retail account on any venue (constraints dropped 2026-10-31: Binance / Bybit /
Hyperliquid / Polymarket / IB all count)?

## How this differs from the earlier literature passes
- Round 23 N (2025-01..2026-10-15) harvested 30 journals + NBER / Fed + arXiv q-fin, but filtered on a timing word x
  an **IC symbol** (FX, gold, indices, oil). Crypto venues, prediction markets, single names and perp mechanics were
  out of scope then and are in scope now.
- Round 52 Z covered 2018-24; rounds 12 K / 19 T searched by topic for IC symbols; round 63 I and round 65 J were
  hypothesis scouts (event contracts, unlocks, Upbit, HK), not a 2025-26 literature sweep.
- This pass therefore re-reads 2025-26 (plus anything posted 2026-10-15..11-01) with a **mechanism filter**
  (retail / announcement / rule / settlement) and **no instrument filter**.

## Search plan (all requests logged in research/data/lit_2025_26/requests.log: UTC time, URL, status, bytes)
1. robots.txt of each host first: api.crossref.org, api.openalex.org, api.semanticscholar.org, arxiv.org. No e-mail,
   no mailto, plain UA "research-script/1.0 (python-urllib)", >= 1 s between requests per host (arxiv.org: its
   crawl-delay, 15 s if stated).
2. arXiv listing pages (arxiv.org/list/<cat>/<year>, show=2000) for q-fin.TR, q-fin.ST, q-fin.PM, q-fin.GN,
   2025 and 2026: titles + IDs (~8-12 pages). export.arxiv.org is not used (robots disallow).
3. Crossref keyword queries (~40, `code/queries.tsv`), filter from-pub-date 2025-01-01, 20 rows each, title +
   abstract where present.
4. OpenAlex search, same queries, filter from_publication_date 2025-01-01, if the anonymous quota allows; abstracts
   from abstract_inverted_index.
5. Semantic Scholar graph search for a handful of SSRN-heavy queries (back off on 429; stop after 3 consecutive).
6. arxiv.org/abs pages for the shortlisted arXiv papers (<= ~25, 15 s apart) to read abstracts.
7. WebSearch <= 15 for SSRN-only 2025-26 papers on the strongest families.
8. Filter (`code/filter.py`, `python -I`): mechanism word x (asset / venue word) over titles + abstracts; read the
   kept rows by hand; map each to registry `tried:` and PROMPT "Những họ đã cạn".

## Query families (declared before seeing results)
- Retail: retail order flow / imbalance crypto, Robinhood, Korean retail crypto, meme stock, retail attention
  Google Trends crypto, retail option buying 0DTE, Telegram / pump-and-dump groups, prediction-market retail.
- Exchange announcements: crypto exchange listing / delisting announcement, perpetual futures listing, Binance
  Launchpool / airdrop, Coinbase listing, exchange maintenance, "Monitoring tag", index inclusion crypto.
- Rule-based flows: liquidation cascades, auto-deleveraging (ADL), margin call thresholds, leveraged ETF rebalancing
  (crypto / single-stock), stablecoin mint / redemption rules, token unlock, staking unbonding, ETF creation
  baskets, index reconstitution 2025.
- Settlement mechanics: perpetual funding settlement, futures expiry / settlement price, Deribit / CME settlement,
  oracle price updates, Hyperliquid mark / oracle, prediction-market resolution, T+1 / CNS, options pin.

## Grading rules for each idea (declared)
- Mechanism must be economic and have a fixed side before data.
- Free point-in-time data must exist up to 2024-12-31 for IS 2020-21 (or 2016-21) and VAL 2022-24; if the effect
  only exists from 2025, the idea is **forward-only** and capped at DEMO via forward log.
- HOLD contamination flag: the source uses 2025-26 data -> any rule from it can only be forward-tested honestly
  (or the PREREG says HOLD was seen by the literature).
- Duplicate check: name the `tried:` row if the construction is the same; "new" only if the construction differs
  materially (say where).
- Power at a plausible size: power = (net mean / sd per independent event) x sqrt(HOLD events, ~1.83 y x rate).
  LIVE needs >= 3. Plausible size = the paper's effect shrunk by half (decay seen in rounds 12-69), net of taker
  costs of the venue (Binance perp 5 bp a side + spread; IC CFD spreads; Polymarket 0 fee + spread).
- P(LIVE) / P(DEMO) include the chance that data or venue fails; prior for a fresh literature family after 69
  rounds is ~1 % LIVE.

## Expected outcome (prior, stated now)
Most hits will be crypto microstructure with 2025-26 samples (contaminated) or families already tested (funding,
listings, liquidations, ETF flows). Expect 0-2 ideas above 2 % P(LIVE).
