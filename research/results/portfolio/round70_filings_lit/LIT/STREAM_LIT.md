# Round 70, stream LIT: 2025-26 literature scout (no backtest)

Written 2026-11-01 17:36 UTC (`date -u` at 17:35:53). The plan is in [HYPOTHESES_LIT.md](HYPOTHESES_LIT.md), written at
17:22 UTC before any request. No price series was loaded and no return was computed. HOLD was never requested. One
third-party file set contains 2025-26 returns; I extracted only its timestamp / venue columns and counted rows by
year, and I did not read or summarise any 2025-26 value (see L1, "HOLD hygiene").

Requests: 120, all logged in research/data/lit_2025_26/requests.log, with bodies under research/data/lit_2025_26/raw/<host>/.
They went to Crossref 40, OpenAlex 40, arXiv 22, Semantic Scholar 12, Zenodo 4 and Deribit 2. WebSearch: 7 of 15.
Code (all run with `python -I`): code/fetch.py, parse.py, filter.py, absparse.py, plus queries.tsv (40 queries declared
17:25 UTC).

## Answer first
- **No idea here is likely to reach LIVE.** The best is ~2 %. The eight live ideas together give maybe 6-9 % of at
  least one LIVE candidate. The 2025-26 crypto literature is large but thin: most of it is 2025-26-only samples (a
  week to a year), AI-assisted SSRN / Zenodo notes, or families this repo already tested (funding extremes, listings,
  ETF flows, unlocks, Polymarket price-level bias, 15-minute reversal).
- **The one material new item is a data unlock, not a mechanism.** An MIT-licensed Zenodo release (Asalio123,
  "binance-listing-study" v1.1.0, doi 10.5281/zenodo.22976615) gives Binance **spot-listing announcement times to the
  second** for 468 events from 2021-01. They were rebuilt from Binance's CMS plus Telegram.
  - Round 63 D failed only because binance.com robots forbid /bapi/. This file supplies those times.
  - It makes the Upbit A2-D5L construction testable for Binance announcements (L1).
  - Pre-2025, the file has 79 events where the coin already traded on Coinbase or Bybit: 23 / 6 / 18 / 9 in
    2021-24. The authors only measured those two venues.
  - **Needs a user decision before use.** The file was built partly from Binance /bapi/ and web.archive.org, two
    sources our network rules forbid us to call directly.
- **Second: a structural funding-formula carry (L2).** Deribit perpetual funding has no interest component (a
  premium-only rule with a ±0.025 % damper). Binance / Bybit / Hyperliquid funding carries a fixed 0.01 %/8h anchor
  (~10.95 %/yr; "The misplaced anchor", SSRN 6751742).
  - The trade: long the Deribit perp and short the Binance perp. It earns the anchor whenever both premiums sit
    inside their dampers, and the capital is margin only.
  - This differs from B1 / B2 (round 59). There, both legs carried the same anchor and the spread was transient.
    Here the anchor sits on one leg only, by rule.
  - The first probe (2020-01-01) shows Deribit's own premium already charging ~0.013-0.014 %/8h. Arbitrage may have
    absorbed the anchor, and only a test can tell.
  - Deribit's hourly funding history is public. I probed it: HTTP 200, hourly interest_8h from 2020.
- **HOLD-contamination flag.** Every source behind L1 and L3-L6 uses 2025-26 data. A rule taken from them can be
  graded on IS / VAL. The PREREG must then say that the literature has seen HOLD, or the rule must be decided on a
  forward log. L2 and L4 depend least on 2025-26 papers: L2 is a contract rule, and L4's main sample is 2023.

## Ranked table
Power = net Sharpe per independent event at a plausible size (half the paper's effect, net of taker costs) x
sqrt(HOLD events, ~1.83 years). LIVE needs >= 3. The P columns include the chance that the data or the venue fails.

| # | mechanism (source) | instrument / venue | free data, status 2026-11-01 | events / yr pre-2025 | HOLD power at plausible size | P(LIVE) | P(DEMO) | forward-only / HOLD-contaminated | duplicate check (`tried:`) |
|---|---|---|---|---|---|---|---|---|---|
| L1 | Binance spot-listing announcement funnels retail. Buy the coin where it already trades, within seconds of the announcement stamp, exit +5 / +60 min (A2-D5L construction) | Coinbase Exchange spot (long), Bybit USDT perp | announcement times: Zenodo MIT file (downloaded, **user OK needed**: built from /bapi/ + web.archive.org). Prices: Coinbase public trades, Bybit public trade archive (allowed) | 23 / 6 / 18 / 9 (2021-24) with a measured second venue; more if OKX / KuCoin / Gate are added | 2.2 at +2 % net, sd 6 %, n ~44; 3.3 at +3 % | 2 % | 7 % | contaminated: the release itself measures this window for 2025-26 (`announcement_premium_coinbase.csv`, `announcement_shock.csv`). Coordinator: grade IS / VAL rows only, never open those files' 2025-26 rows | D (R63) blocked on timestamps; KO / JP / O2 / B2 (R66-69) other venues. **New**: Binance as announcer, third-party stamps |
| L2 | Funding-formula carry: long Deribit perp (premium-only funding) / short Binance perp (0.01 %/8h anchor), held while both premiums sit in their dampers | Deribit BTC / ETH perpetual (inverse; USDC linear from 2022) + Binance USDT-M | Deribit public get_funding_rate_history 200 (hourly from 2020); Binance funding local; Deribit perp candles public | daily book (~730 IS, ~1,100 VAL days) | needs annual Sharpe >= 2.2; B1 / B2 Sharpe collapsed to ~0.5-1 in HOLD | 1.5 % | 5 % | no (contract rules since <= 2019; check Deribit damper history) | B1 / B2 (R59) cross-venue funding spread; A3 (R58) spot-perp carry = cash. **New**: the anchor sits on one leg only, by rule |
| L3 | Extreme negative funding, then follow the day's direction for 24 h (up day: +1.88 %, down day: -1.74 %; SSRN 7520320, 274 events BTC / ETH / SOL 2021-26) | Binance USDT-M perps | local funding + perp_1h (no request needed) | ~50 (3 coins); ~150 day-clusters on the top-40 | 1.7 (3 coins) to 2.2 (top-40), Sharpe ~0.18 | 1 % | 5 % | contaminated (sample to 2026) | R / P1 (R62, minutes after the stamp), F (R37), X2 (R61), 1-day momentum (R2 / R7). **New**: 24 h hold conditioned on the day's sign |
| L4 | Polymarket crypto threshold "Yes" overpriced vs the option-implied digital (gap 5.6-6.3 pp, n 287 hours, arXiv 2606.19517). Sell Yes when it sits above the Deribit / Binance option fair value, largest at low probability and long maturity | Polymarket CLOB (hold to resolution), Deribit options for fair value | Polymarket gamma / CLOB 200 since 2022-11 (R63 I); Deribit option history (R34 D cache 2021-24) | ~50-150 parent dates (2023-24); thousands in 2025-26 | ~2 if a 3 pp net edge survives on 150 parent dates | 1.5 % | 6 % | partly: main sample Sept 2023; 2025-26 crowding by bots likely | P (R63): price-level favourite / longshot. **New**: option fair value as the benchmark. Grade on excess over cash |
| L5 | Quarter-hour opening order imbalance predicts 4-12 h returns (periodic algos; arXiv 2607.09426, six Binance perps) | Binance USDT-M perps | data.binance.vision 1m klines carry taker-buy volume (monthly files <= 2024-12) | ~2-6 independent windows / day | < 2 (taker-imbalance IC ~0 in R63 O) | 0.7 % | 3 % | likely contaminated (sample dates not in abstract) | O (R63) taker ratio; C (R63) intraday cross-section; clock scans (R3 / R11, IC only) |
| L6 | 24/7 equity / commodity perps while the benchmark is closed: a weekend local move maps 0.7-0.9 into the reference at reopen, so fade 10-30 % of the weekend move before reopen (SSRN 7543402) | Hyperliquid HIP-3 / Binance TradFi perps (2025+) | venue APIs public; no pre-2025 history | ~50 weekends + holidays x 7 asset classes (forward only) | n/a (no IS / VAL) | 0.5 % | 3 % | **forward-only** (instruments start 2025) | none (new instrument class) |
| L7 | Binance delisting announcement, short the perp from stamp + seconds (98 events in the same Zenodo file) | Binance / Bybit perp | same Zenodo file (user OK) | 0 (2021), 14 / 5 / 21 (2022-24) | ~1.2 (n ~58 HOLD) | 0.3 % | 2 % | contaminated; no IS era | D, W (R63, R65) |
| L8 | Telegram pump-and-dump fade: first-minute buyers lose 3-11 % within 10 min (SSRN 7607818, 316 verified messages) | Binance spot / perp short | public P&D message datasets (GitHub, 2017-21), Binance aggTrades | hundreds (2018-21), few later | < 1: targets rarely have perps; spot borrow is blocked on the user's account (B lesson) | 0.3 % | 1.5 % | no | M (R53) mint timing; N0 (R66) |

Dropped after reading (no slot):
- **Polymarket 5-minute BTC settlement manipulation** (SSRN 7445139, 7028398). Binance spot reverted after near-strike
  snapshots. The contract started in 2025 and the footprint ended when Polymarket switched to a TWAP on 2026-08-07.
- **Kalshi CFTC perp deadband** (SSRN 7098201, 7205749, 7321823). US-only venue from 2026-06. It is L2's mechanism on a
  venue the user cannot use.
- **Hyperliquid vs CEX funding spread of 7 %/yr** (SSRN 6993978). This is B2, which failed its registered holdout
  (+0.74 %, t 1.27).
- **Spot BTC ETF flows -> next-day BTC** (SSRN 6592830, 7545019, 5452994). Flows exist only from 2024 (R24 A).
- **Token unlocks within 72 h** (SSRN 6632838, 52 events 2023-25). This is U (R63): IS lost.
- **15-minute sign reversal on 183 Binance pairs** (arXiv 2608.21888). The paper itself finds 1.3 bp gross against
  5 bp costs (= C, R63).
- **Extreme BTC funding -> spot returns** (AIJMR 2026). This is F / R / P1.
- **Funding drag** (SSRN 7529458). It is about correction speed, not a side.
- **Tokenised-stock off-hours marks -> MSTR opening gap** (arXiv 2610.21491, xStocks 2025+). Forward-only, and it needs
  single-stock CFDs.
- **Retail option SLIM imbalance cross-section** (SSRN 6781743, +25.8 bp/day 2019-21). It needs paid OPRA trade
  conditions.
- **KOSPI200 futures closing-auction jump** (Korean J. Bus. Admin. 2026). No abstract, no free KRX intraday data.
- **Leveraged-token rebalancing** (FTX BULL / BEAR, Binance BLVT; web only, no paper). The products are gone, so a
  HOLD test is impossible.
- **Crypto index reconstitutions** (CoinDesk 20, Bitwise 10; notices are free). Tracking AUM before 2025 was too small
  and events are ~5-15 a year.
- **Liquidation-cascade microstructure** papers (Oct 10 2025, Bybit / OKX / Hyperliquid). Single events, no side.

## L1. Binance spot-listing announcement -> buy where the coin already trades
- **Mechanism.** Binance is the largest retail venue. A "will list" announcement is public demand news at a known
  second. This is the A2-D5L construction (Upbit KRW, DEMO, HOLD t 3.11), moved to the announcer that round 63 D
  could not time.
- **Data.**
  - The Zenodo release has `announcement_dates.csv`: 468 events with columns symbol, announce_ts_utc, the trading-open
    text, article_code and a confidence grade.
  - Pre-2025 confidence: 2021 has 94 high / 20 medium / 11 low; 2024 has 56 high / 9 low.
  - Rows by year: 125 / 40 / 58 / 65 in 2021-24, then 100 / 80 in 2025-26 (count only).
  - The release's own cross-venue measurement covers only Coinbase (2021: 23, 2022: 6, 2023: 11, 2024: 5) and Bybit
    (2023: 7, 2024: 4).
  - Adding OKX / KuCoin / Gate spot (all public, check robots) would raise IS events. Their seconds-level history
    must be checked first.
  - Copy of the file: research/data/lit_2025_26/zenodo_listing_x/data/ (extracted subset). The zip is under
    raw/zenodo.org/.
- **Rule to declare** (A2-D5L frozen):
  - Entry: first trade >= stamp + {1, 5} s on the second venue.
  - Exit: +5 / +60 min.
  - Costs: Coinbase taker 40-60 bp retail (or 5 bp at Advanced high tier) plus spread from the trades; Bybit taker
    5.5 bp.
- **Power.** At +2-3 % net with sd ~6 %, ~44 HOLD events (2025-26 rows in the file with a measured venue) give 2.2-3.3.
  The 2021 effect was larger (the IS era), and the 2024-26 decay is the risk (The TIE 2026: "listings deliver
  little").
- **HOLD hygiene.** `announcement_premium_coinbase.csv` (79 events) and `announcement_shock.csv` hold the authors'
  measured returns, including 2025-26. I did not read their return columns. The coordinator should filter on
  announce_ts_utc < 2025 at load and keep the 2025-26 rows for one registered HOLD read. The PREREG must state that a
  public release already measured that window.
- **User decision.** The authors' pipeline called Binance /bapi/ (CMS) and web.archive.org, both forbidden to us. Using
  their output is a provenance question for the user, like defillama-datasets.

## L2. Funding-formula carry: Deribit (no interest leg) vs Binance (0.01 %/8h anchor)
- **Mechanism and rules.**
  - Deribit funding = max(0.025 %, P) + min(-0.025 %, P), where P is the premium of mark over index. There is no
    interest component, and the cap is ±0.5 %/8h for BTC (Deribit support pages, via WebSearch).
  - Binance funding = P + clamp(0.01 % - P, ±0.05 %), so it defaults to 0.01 %/8h when P is small.
  - When both premiums are small, short Binance receives ~10.95 %/yr and long Deribit pays ~0, on margin capital.
- **What kills it.** Arbitrage would lift Deribit's premium above +0.025 % until longs pay the same anchor. The
  2020-01-01 probe shows interest_8h of 0.0128-0.0144 %, so Deribit longs were paying that day. Other risks:
  inverse-contract collateral (BTC-margined; hedge or use the BTC_USDC linear perp from 2022), the basis between the
  two perps at exit, and Deribit fees (perp taker 5 bp).
- **Test.**
  - Data: hourly interest_8h for BTC / ETH 2020-24 (~45 requests a year per symbol, 1 s apart), the local Binance
    funding files, and Deribit perp 1h closes for the basis leg.
  - Rule declared before data: always on, or on only when the trailing 7-day Deribit funding is < Binance's minus
    k (k in {0, 2} bp/8h).
  - Grade: excess over DFF on margin used (2-3x per leg), t by Newey-West, IS 2020-21 / VAL 2022-24.
- **Why it might differ from B1 / B2.** Those pairs shared the anchor, so the spread was premium noise that
  arbitrage removed. Here the gap is the anchor itself. If Deribit premiums absorb it, the test will show it within
  a day of work.

## L3. Extreme negative funding, conditioned on the day's sign (SSRN 7520320)
- **Side.** After an extreme negative funding print, go long 24 h if the day is up, short if down. The paper's gap is
  +3.62 pp (bootstrap CI 2.60-4.67), net of funding +3.59, stable across 12 year-by-direction cells.
- **Data.** Local only (binance/funding, perp_1h). The extreme-event definition is not in the abstract. Declare it
  as funding <= the trailing 180-day 5th percentile (and the 10th), and the day as the UTC day up to the stamp.
- **Doubts.** This is 1-day momentum on stress days, a family that failed at IC and that crypto factor X1 only partly
  supports. The sample includes 2025-26. With 3 coins the power is < 2.

## L4. Polymarket threshold contracts vs option-implied digitals (arXiv 2606.19517)
- **Side.** Sell "Yes" (buy "No") when the Polymarket price exceeds the discounted risk-neutral binary implied by a
  listed option at the same strike and expiry. The gap is largest at low probability and long maturity. Hold to
  resolution.
- **Data.** Polymarket gamma markets with titles like "Bitcoin above $X on <date>" (2023-24) and CLOB hourly prices
  (R63 I: usable, chunked). Deribit option quotes are already cached (research/data/deribit, 2021-24) for the fair
  value.
- **Why new.** R63 P graded price-level favourite / longshot bias. This grades the gap to an external fair value,
  using one trade per parent date. It is capital-heavy, so grade the excess over DFF.
- **Risk.** 2025-26 crowding: Polymarket crypto markets drew market makers. It is hard to reach LIVE unless HOLD
  events are numerous, which they are (thousands).

## L5. Quarter-hour order imbalance (arXiv 2607.09426)
- The abstract says the opening order imbalance at quarter-hour marks predicts returns over 4-12 hours, out of
  sample, for six Binance perps.
- It can be tested from monthly 1m klines (taker-buy base volume), cut at 2024-12. Declare the signal as the
  taker-imbalance z of the first minute of each :00 / :15 / :30 / :45, with a 4 h and 12 h hold, on BTC / ETH plus four
  top coins.
- **Prior.** R63 O found taker imbalance ~0 before ~30 bp altcoin costs. On BTC / ETH the costs are 10 bp round trip.
  The paper does not report net returns.

## L6. Weekend equity / commodity perps vs a closed benchmark (SSRN 7543402)
- The local weekend move under-predicts the reopen reference (slope 0.7-0.9), so the perp overshoots by 10-30 %.
- The rule is to fade a declared share of the weekend perp move before the Monday reference returns.
- The instruments exist only from 2025 (Hyperliquid HIP-3, Binance / Bybit TradFi perps), so this is a forward log
  only, at best DEMO. IC has no weekend index price to use as a proxy.

## L7 / L8 (brief)
- **L7.** The same Zenodo file locates 98 Binance delisting announcements: 0 in 2021, 40 in 2022-24, 58 in 2025-26
  (count only). There is no IS era, and W (R65) already found Upbit delisting warnings untradable.
- **L8.** Pump-and-dump fade has a real side (buyers in the first minute lose), but the targets are illiquid spot
  coins without perps. The short leg needs spot borrow, which the user's Binance account cannot get (R63 B status).

## Notes for stream M8 (8-K filings)
- "Selling One to Buy Thirty" (SSRN 6882258) rebuilds Strategy's financing from 8-Ks. Its management break-even
  mNAV is ~1.22, below which Strategy says it may sell BTC. That gives M8 a regime split (premium vs discount) that
  can be declared now.
- Press coverage says Saylor's Sunday "tracker" post precedes the Monday 8-K. The public signal is therefore often
  the post, not the EDGAR acceptance (the round 52 Z2 risk).
- I found no academic event study of the 8-K stamp itself.

## Search log and coverage
- **arXiv.** Yearly listing pages for q-fin.TR / ST / PM / GN 2025 and 2026 (8 pages, 16 s apart) gave 2,147 titles.
  Pitfall: these pages list far fewer entries than the full categories (q-fin.TR June 2025 shows 14), so this is a
  partial view. The round 23 N API harvest (to 2026-10-15) is the fuller one, but it used an IC-symbol filter.
  12 abstract pages were read.
- **Crossref.** 39 queries, filter from-pub-date 2025-01-01, up to 20 rows each.
- **OpenAlex.** 38 queries; the anonymous daily budget was not exhausted. I did not request an API key, because that
  needs an e-mail.
- **Filter.** A mechanism word x venue word filter kept 865 of 3,863 records (529 Crossref / OpenAlex + 336 arXiv),
  all read by title. ~60 abstracts were read.
- **Semantic Scholar.** 12 lookups: 9 returned 404 for SSRN DOIs, and 3 returned records without abstracts.
- **WebSearch (7).** Listing seconds-effects, leveraged-token rebalancing, crypto index rebalancing, MicroStrategy
  8-K reactions, Deribit funding formula, perp-listing announcements, "conditional arbitrage capacity". I found no
  SSRN paper on seconds-level listing effects.
- **Deviations from the plan.** I added www.deribit.com (robots 404 = no file; 1 funding probe) and zenodo.org
  (robots: /records allowed, /api disallowed except files; crawl-delay 10 honoured). The first Zenodo file URL
  returned 404 (concept record), and the version record worked.

## Pitfalls
- Much of the 2026 SSRN crypto literature uses 1-12 weeks of 2025-26 data, and some notes look machine-written
  (pre-registered "nulls", referral-code spam in Crossref). Read sample dates before trusting a sign.
- The Zenodo release bundles minute returns for 2025-26 listings. Any loader must cut at announce_ts_utc < 2025
  before any column other than symbol / venue / timestamp is touched.
- OpenAlex anonymous use now shares a $0.10/day budget per IP. Its notice suggests creating a key with an e-mail,
  which our rules forbid.

## Files
- research/results/portfolio/round70_filings_lit/LIT/HYPOTHESES_LIT.md, STREAM_LIT.md, code/ (fetch.py, parse.py,
  filter.py, absparse.py, queries.tsv, URL lists).
- research/data/lit_2025_26/requests.log, raw/<host>/ (bodies), code_out/ (all.tsv, kept.tsv, title lists),
  zenodo_listing_x/ (extracted metadata CSVs from the Zenodo release).
