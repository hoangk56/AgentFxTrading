# Round 52, stream Z: census of untested mechanisms against 51 rounds (phase 1)

Started 2026-10-30 09:27:40 UTC, written 09:43-09:50 UTC (`date -u`). Brief: [BRIEF.md](BRIEF.md) row Z and
round37_forced_flows/BRIEF.md. **No price data was loaded in this stream.** The only data pulled were literature
records and the timestamps / sizes of USDT-TRC20 mint events (TronGrid, cut at 2024-12-31 at parse). HOLD was never
touched.

## Answer
- **No open mechanism reaches the phase-2 gate (expected LIVE chance >= 2 % with free data). Phase 2 was not run, and
  there is no HYPOTHESES_Z.md and no PREREG_DRAFT.**
- **The top open item is Z1: Tether (USDT) mint events -> long BTC for 5-30 minutes** (Saggu 2022, FRL 49:103096).
  It is the only 2018-24 paper in the harvest with an IC symbol, a side, a minute window and an effect several times
  IC's cost: +24 to +68 bp within 5-30 minutes after a mint, 2014-21, fading after 60 minutes.
  - Round 7 C tested Griffin & Shams' daily / weekly stablecoin issuance. Z1 differs: it trades in event time from
    each on-chain mint's block timestamp, at minutes.
  - It fails the gate on the count. Only Tron mints are free from this Mac: 248 events 2019-24, of which >= $10M are
    33 / 57 / 53 / 11 / 16 / 16 per year. That gives ~43 VAL and ~25-30 HOLD events, so LIVE needs a net per-event
    Sharpe >= ~0.57.
  - Ethereum mints, which made up a large share of 2020-21 and 2024 issuance, need an archive RPC. publicnode
    returns 403 with "personal token", drpc's free plan refuses log ranges, and Cloudflare caps each query at 800
    blocks (~21k requests for 2017-24).
  - Expected LIVE chance: ~1-1.5 % on Tron (+ Omni) data, ~2.5 % with the Ethereum mints (needs the user: a free RPC
    token is an account). DEMO chance ~5-10 %.
- **The 2018-24 literature adds nothing else.** It was the one window no earlier census had harvested exhaustively:
  round 25 C covered <= 2017, round 23 N covered 2025-01..2026-10, and rounds 12 K / 19 T searched 2018-26 by topic
  only.
  - Crossref returned 48,633 unique titles from 30 journals + the NBER and Fed Board prefixes, and arXiv 2024 q-fin
    listings 797 more. 426 passed the timing x asset filter, and all were read by title (abstract where Crossref has
    one).
  - Every kept paper is one of: a family rounds 2-51 tested, a volatility or jump model with no side, Chinese /
    emerging single-market work, or data IC lacks. The one exception is Z1.
- **What is left needs the user.** Single-stock CFDs (round 25 A, LIVE ~3-5 %) are still the most valuable decision.
  An Ethereum archive-RPC token for Z1 (~2.5 % LIVE, ~10 % DEMO) is the cheapest new one.

## Sources and robots (fetch log: scratchpad `r52/Z/web/requests.log`, `web/tron/requests.log`, `lit/cr/log.txt`)
| host | robots.txt (ClaudeBot / anthropic-ai / *) | used for | result |
|---|---|---|---|
| api.crossref.org | 404 (no file) | journal and prefix works 2018-01-01..2024-12-31, titles + abstracts, cursor paging, no mailto | 67 requests 09:32-09:41 UTC, all HTTP 200, 48,633 unique titles |
| arxiv.org | `*` allows /list, crawl-delay 15 s | q-fin.TR / ST / PM / GN 2024 listings (4 pages, 16 s apart) | 797 titles, nothing with a side on an IC symbol |
| export.arxiv.org | `*` Disallow: / | not used (round 23 had used the API; robots forbid it now) | - |
| api.openalex.org | `*` Allow | not needed (Crossref sufficed; free budget kept for others) | - |
| api.trongrid.io | 404 (no file) | USDT-TRC20 `Issue` / `Redeem` events 2019-01-01..2024-12-31 | 248 mints, 34 burns |
| apilist.tronscanapi.com | **disallows ClaudeBot, anthropic-ai, Claude-Web** | off limits; not queried | - |
| ethereum-rpc.publicnode.com | 404 | one `eth_getLogs` probe | **403 "archive requests require a personal token": stop**, not retried |
| eth.drpc.org | 404 | 4 probes | HTTP 400, free plan refuses `eth_getLogs` ranges (even < 1,000 blocks); stopped |
| cloudflare-eth.com | 404 | 1 probe | works but max 800 blocks per query (~21k requests for 2017-24): not run |
| eth.llamarpc.com | 200 | 1 probe | HTTP 525; not retried |
| api.omniexplorer.info | no robots file (HTML page) | not queried yet (Omni mints 2015-19 = IS only) | - |
| WebSearch | - | 9 searches (FX / gold flow papers 2024-26, Osler-type cascades, CME gap, LETF single stocks, FX time of day, the Saggu abstract) | only the Saggu abstract was new |

## Harvest counts (2018-01..2024-12)
| stage | count |
|---|---|
| Crossref journals by ISSN | JFutM 747, JBF 1,573, JIMF 1,063, FRL 4,913, IRFA 2,286, JFinMkts 326, JEmpF 556, JIFMIM 868, JFE 1,102, RFS 854, JF 775, JFQA 831, RoF 306, QF 883, Energy Econ 3,682, Resources Policy 3,945, JComM 271, PBFJ 1,398, EFM 407, JPM 783, FAJ 218, JFEc 236, IREF 2,286, NAJEF 1,275, GFJ 525, RIBAF 1,568, RAPS 127, Mgmt Sci 2,699, Econ Letters 3,043, JBEF 614 |
| Crossref prefixes | NBER 9,140; Fed Board 1,334 |
| unique titles | 48,633 (+ 797 arXiv 2024 q-fin) |
| kept by the filter (timing / flow word x asset word in the title, or timing word in the title and asset word in the abstract) | 426 + ~80 arXiv |
| maps to a tested family (fixes, clocks, weekdays, ITSM, LETF, expiries, round numbers, CME / Deribit expiry, Hau-Rey, pre-announcement, overnight, gaps, rebalancing, auctions, roll, news) | ~95 |
| no side (volatility / jump / co-jump models, spillovers, forecasting, ML) | ~210 |
| single-country EM / Chinese / Indian / Gulf markets, single stocks, art, mining, policy | ~115 |
| open with a side on an IC symbol | **1 (Saggu 2022, Z1)**; plus the companion "When Tether says JUMP!" (FRL 2022, 102644, no window in the title) |

The ~6 "mechanism" papers that look new by title but are not: Hau-Rey / Camanho et al. rebalancing (round 4 U1,
round 12 I), "Index options open interest and stock market returns" (OI growth, monthly), "Sunshine vs predatory
trading ... index rebalancing" (round 39 R), "Is there an expiration effect in the bitcoin market?" (round 12 K4 / K5),
"Evidence for round number effects in cryptocurrencies" (round 28 BTC), "Trading time seasonality in commodity
futures" (clock scans, rounds 3 / 13 / 15).

## Census, ranked by expected chance of a LIVE cell
Power = net per-trade Sharpe x sqrt(HOLD trades), HOLD = 21 months (1.73 years); LIVE needs >= 3 (round 37 brief).
The frontier rows used are round 10's table: 1 trade a day needs a per-trade Sharpe of 0.145, 1 a week needs 0.32.
At fewer than ~25 HOLD trades a year LIVE needs > 0.45 and is treated as impossible for flow effects (the best flow
known, C3, runs ~0.1-0.2). Status: **open** = no round tested this construction; **tested** = cite; **untestable** =
why.

| # | mechanism (source) | data, free from this Mac? (robots) | first year | signals / yr (VAL; HOLD est.) | paper size vs IC cost | power at IC cost (what it needs) | status | LIVE / DEMO chance |
|---|---|---|---|---|---|---|---|---|
| **Z1** | **USDT mint -> BTC up 5-30 min, fades by 60 min; burns: no symmetric fall** (Saggu 2022 FRL 49:103096, 2014-21; "Whale Alert" announcement amplifies; Griffin & Shams 2020 JF for the daily version) | Tron mints: TronGrid, free, robots none (pulled: 248 / >= $10M 186). Omni 2015-19: omniexplorer (no robots file; not pulled). Ethereum mints: archive `eth_getLogs` needs a token (publicnode 403) or ~21k Cloudflare calls: **not free in practice**. Tronscan disallows ClaudeBot | Omni 2015; Tron 2019-04; IC BTC 2017-08 | Tron >= $10M: 2019 33, 2020 57, 2021 53, 2022 11, 2023 16, 2024 16 (VAL 43; HOLD ~25-30 Tron-only, ~60-90 all chains) | +24..+68 bp in 5-30 min (+0.8 % at 30 min after a $1bn mint) vs BTC cost ~7-8 bp 2020-21, ~2.6-3.3 bp 2022-24 (rounds 12 K, 37 F) | 30-min sd ~50 bp 2020-21, ~35 bp 2023-24 (sqrt-time estimate from daily vol, not measured). Tron-only HOLD 28: needs Sharpe >= 0.57 = net >= ~20 bp. All chains 80: needs 0.34 = ~12 bp. The paper's size would clear both, but a published crypto effect keeping >= 40 % of its size into 2025-26 is unlikely (round 18: declared rules keep 65-103 %, flows ~30 %) | **open**: round 7 C was daily / weekly issuance (BTC +68.7 bp, t 1.4; weekly slope wrong sign). Event time from block timestamps differs: minutes, one trade per mint. Confound to control: mints follow exchange demand, so a "BTC rose in the prior hour" placebo is needed | **Tron-only ~1-1.5 % / DEMO ~5 %; with Ethereum ~2.5 % / ~10 %** (below the gate on free data) |
| Z2 | Strategy (MicroStrategy) weekly BTC purchases: Monday 8-K after a week of buying -> "sell the news" (practitioner lore 2024-25; considered and not declared in round 24 A) | SEC EDGAR 8-K for CIK 1050446, free (EDGAR allowed, rounds 41-47) | 2020-08 | IS 2020-21 ~12, VAL 2022-24 ~35 (mostly late 2024), HOLD ~70 | no paper; lore claims a Monday dip; the buying itself is spread over the prior week (ATM proceeds), so the 8-K is after the flow | at ~40 bp sd over 4-24 h and ~3 bp cost a LIVE cell needs >= 0.36 Sharpe at 70 HOLD events; IS has ~12 events (DEMO impossible on IS t) | open, era-limited (mostly a 2024-26 mechanism, the round 24 A era-rule case) | < 0.5 % / ~2 % |
| Z3 | Ethereum / Tron USDC mints (Circle) -> BTC, same construction as Z1 | Ethereum archive logs (not free in practice) | 2018-10 | ~30-60 | none published at minutes | as Z1 all-chains, but USDC flows are institutional (less retail FOMO) | open, data-gated | < 1 % / ~3 % |
| Z4 | Japanese dividend-reinvestment futures buying at the March / September record date (index funds buy ~JPY 1 trn of futures at the close of the last day with rights; JA lore 配当再投資の先物買い) | JPX calendar (rule-based), IC JP225 | pre-2016 | 2 | ~+20-40 bp claimed into the close vs ~4-6 bp | 2 / yr: LIVE impossible (needs Sharpe > 1.6) | open (0 hits in results/), count-capped | 0 % / < 1 % |
| Z5 | Leveraged single-stock ETFs (NVDL, TSLL, MSTU...) rebalancing at the close -> USTEC last 15 min (Bessembinder 2025; JPM desk notes) | issuer AUM / leverage (free CSVs for some), but material only from 2024 | 2022-12 | 250 | effect unmeasured; index-level LETF doses (round 34) found USTEC IS t 1.38 / VAL 2.78, then failed HOLD | no IS era (fixed eras), so not gradable under the bars | untestable without a new era rule (round 24 A case) | < 0.5 % / ~1 % |
| Z6 | Baker Hughes rig count, Fridays 13:00 ET -> XTI / XBR (no paper with a side; a public number) | rig-count history free (bakerhughesrigcount.gcs-web.com: not probed) | pre-2016 | 52 | rounds 25-26: public numbers are priced in the first minute; oil cost 3.6-7.9 bp at release minutes | needs Sharpe 0.41 at ~90 HOLD events: not plausible for a priced release | open (0 hits), low prior | < 0.5 % / < 1 % |
| Z7 | OPEC / OPEC+ (JMMC) meeting days -> oil 1-3 days (event literature, e.g. "OPEC news and jumps", Energy Econ 2021) | dates from opec.org press releases | pre-2016 | 6-10 | jump risk, no fixed side | count-capped | open, no side | 0 % / < 1 % |
| Z8 | Corporate IG bond issuance days, rate-lock hedging -> Treasury yields -> USDJPY (practitioner; "Price pressure and price discovery in the term structure", FEDS 2018) | EDGAR 424B2 / 424B5 counts (free; round 41 pulled the index) | pre-2016 | ~250 days | round 41: Treasury supply priced within 15 minutes, post-auction reversal only 2004-15; the corporate leg is smaller | round 41's diagnostic slopes give HOLD power ~0.3-1.2 before cost | open (debt leg not split in round 41), low prior | < 0.5 % / ~1 % |
| Z9 | State-bank USDCNH defence at policy lines (7.00 in 2016-19, 7.30 in 2023-24) -> fade approaches | IC USDCNH (bid only in M1; ticks in data/USDCNH/t1) | 2015 | few defence episodes, many touches | round 30: CNH round trip 1.15 bp; round 28 tested USDCNH major round levels (continuation, none) | ill-defined count; policy lines chosen after the fact | near-tested (round 28 levels, round 30 costs) | < 0.5 % |
| Z10 | Ewald et al. 2025 (Quant. Finance) Brent intraday long / short windows | paywalled; repository copy embargoed to 2027-02 | 2010 | ~250 | "significant alphas after costs" (ICE Brent) vs XBR cost 3.6-7.4 bp | unknown until the windows are known; Brent clock scans (rounds 3 / 11) found nothing | untestable (needs the full text: user) | ~1 % / ~3 % |
| Z11 | Japanese life insurers' semiannual hedge-ratio plans (late Apr / Oct) and GPIF rebalancing | press reports; GPIF dates undisclosed | - | 2 | no side before the trade | impossible | untestable (round 23 P) | 0 % |
| Z12 | Quarter-end window dressing / "leaning for the tape" (Carhart et al. 2002) | NYSE calendar | - | 4 | pre-2016 stock-level | power < 0.5 | untestable at power (round 23 P) | 0 % |
| Z13 | CME FX futures quarterly roll (IMM Monday-Wednesday) -> spot | CME calendar | - | 4 | rolls are swaps: no spot pressure expected | impossible | open, count-capped | 0 % |
| Z14 | DST mismatch weeks (US vs Europe clocks 1-3 weeks apart, March / Oct-Nov) as a liquidity regime | rule-based | - | ~4 weeks | no side; the record treats it as a clock pitfall | - | no side | 0 % |
| Z15 | BTC whale deposits to exchanges (Whale Alert) -> sell pressure | labelled exchange addresses point-in-time are paid (round 31 C: CoinMetrics flows are not point-in-time) | 2018 | hundreds | unmeasured | - | untestable free | < 1 % / ~2 % (paid) |
| - | Single-stock CFDs after earnings blackouts, insider "opportunistic" buys, buyback windows (rounds 25 A, 42, 44, 47) | Dukascopy stock CFDs + EDGAR (free), IC shares only on MT5 | 2017 | 50-500 | 40-90 bp vs ~9 bp | up to 2.6 full size | user decision (platform) | 3-5 % / ~25 % |

Already tested and not re-listed as open (the census checked each candidate against `results/` before ranking):
- FX big figures and minor levels: round 3, round 28 minor rows.
- Major round levels on 22 symbols, USDCNH included: round 28.
- Record and extreme stops: round 37 A.
- Prior-day / Asian-range gold stops: round 31 P1.
- The BTC CME weekend-gap fill: flow search round 4, BTC -10 bp (t -0.2).
- The CME BRR expiry window and the Deribit Friday expiry: round 12 K5 / K4.
- COMEX gold options expiry and first notice day: round 12 L4-G-optex / L4-G-fnd.
- The PBoC fix surprise: round 7.
- Hau-Rey equity -> FX rebalancing: round 4 U1, round 12 I.
- Daily stablecoin issuance: round 7 C.
- Leveraged ETFs, VIX-ETP and index doses: rounds 6 / 12 / 13 / 34.
- Krohn-Mueller-Whelan fixes around the clock and the "W" dollar shape: rounds 3 / 4 / 10 / 13 / 19.
- Volume-conditioned FX reversal (Cespa et al.): round 22 R2.
- FOMC-cycle even weeks: round 22 R1.
- MoF interventions: round 31 J, none in IS.
- Margin hikes, funding stamps and Stock Connect: round 37.
- GLD / ETF primary flows: rounds 31 G and 38.

## Why the gate is not met (power arithmetic for Z1, done before any return)
- **HOLD count.** Tron-only events >= $10M in VAL are 43 over 3 years. HOLD (21 months) at the 2023-24 rate holds ~28
  events.
- **Tron-only threshold.** Power 3 needs a net Sharpe of 3 / sqrt(28) = 0.57 per event. At a ~35 bp 30-minute sd
  that is ~20 bp net, ~23 bp gross at ~3 bp cost.
- **The paper meets it, the record says it won't hold.** The paper's +24..+68 bp would clear it, but every flow
  anomaly in the record lost 35-75 % of its size from IS to VAL, and published crypto effects decayed after 2021
  (round 12 K4 Deribit, round 37 F funding).
- **Probability.** I put P(keeping >= 40 % of the paper's size in 2025-26 and passing IS t >= 2.5 / VAL t >= 1.5) at
  ~1-1.5 %. That is lower than the round 25 A routes (2-5 %), whose effect sizes were also several times cost.
- **With Ethereum mints** (2024 issuance was large on Ethereum) HOLD rises to ~60-90 events, so the bar falls to
  ~0.32-0.39, ~12-14 bp net. That raises the chance to ~2.5 %, but needs data that is not free without an account.
- **IS-era caveat.** IC BTC costs 7-8 bp in 2020-21 (more in 2017-19), and the IS events are mostly 2019-21 on Tron,
  plus 2017-19 Omni if pulled. IS t >= 2.5 is reachable only if the paper's size holds in 2019-21.

## Pitfalls (for whoever runs Z1)
- **Ordering.** A mint is a reaction: Tether mints when exchanges / OTC desks request USDT. The 30 minutes after a
  mint may carry the momentum of the rally that caused it. The control must be random entries with the same
  prior-60-minute BTC return profile, and a placebo "BTC +x % in an hour without a mint".
- **Mint, issue and announcement are different times.**
  - The mint goes to the Tether Treasury, and issuance to exchanges comes later.
  - Whale Alert announces the mint within ~1-2 minutes of the block; its history is paid.
  - Use the block timestamp. Enter at block + 2 minutes (the +1 minute rule on top of 1 minute of detection) at
    the IC ask.
- **Clustering.** Tron and Ethereum mints often come in pairs or minutes apart. Cluster within 60 minutes and keep
  the first.
- **Tiny mints.** 2019 has 83 Tron mints but only 33 of >= $10M; test / dust mints (100, 1,000,000 units) must be
  dropped by a size rule declared before any return.
- **IC BTC gaps.** IC BTCUSD was closed at weekends until 2024-04, so weekend mints have no IC price. Skip them, and
  say how many.
- **Off-limits and blocked hosts.** apilist.tronscanapi.com disallows ClaudeBot. publicnode's archive RPC is behind
  a token (403 = stop). drpc's free plan refuses log queries. Do not use Etherscan (API key = account) or Dune /
  BigQuery (login).

## Directions that need the user (value = chance of a LIVE / DEMO cell)
| direction | what is needed | value |
|---|---|---|
| Single-stock CFDs (MT5) for the blackout / insider / buyback-window flows | accept a non-cTrader platform (round 25 A) | LIVE ~3-5 %, DEMO ~25 %: still the most valuable decision |
| Ethereum archive RPC token (free tier of a provider needs an account) for Z1's Ethereum USDT / USDC mint timestamps 2017-24 | create an account / key, or allow ~21k Cloudflare 800-block queries (~6 h at 1 req/s) | Z1 LIVE ~2.5 %, DEMO ~10 % |
| Allow Z1 on Tron (+ Omni) data only, below the 2 % gate | a lead / user override of the gate; ~30 min of work, events already pulled | LIVE ~1-1.5 %, DEMO ~5 %; would also price the token decision above |
| Ewald et al. 2025 full text (Brent intraday windows) | SSRN / journal access | LIVE ~1 %, DEMO ~3 % |
| Whale Alert or labelled exchange-flow history (paid) | subscription | LIVE < 1 %, DEMO ~2 % |

## Files
- This census: `research/results/portfolio/round52_lit_census/CENSUS_Z.md`.
- Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r52/Z/`:
  - Scripts: `scripts/cr_harvest.py` (Crossref harvest), `scripts/lit_filter.py` (title / abstract filter),
    `scripts/ax_titles.py` (arXiv listing parser), `scripts/tron_mints.py` (TronGrid mint / burn pull, HOLD cut at
    parse).
  - Literature data: `lit/cr/*.jsonl` (32 sources, 48,633 unique titles) with `lit/cr/log.txt`; `lit/filtered.tsv`
    (426 kept records); `lit/ax/*.html` and `lit/ax_titles.txt` (arXiv 2024).
  - Mint data: `web/tron/tron_Issue.tsv` and `tron_Redeem.tsv` (ts ms, USDT amount, tx id; 2019-01..2024-12).
  - Logs: `web/requests.log`, `web/tron/requests.log`, and the `web/robots_*.txt` copies.
