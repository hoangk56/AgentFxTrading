# Round 37: forced and rule-driven flows (exchange margins, funding stamps, record-level stops, Stock Connect), 2026-10-29

Brief: [round37_forced_flows/BRIEF.md](round37_forced_flows/BRIEF.md). Same LIVE / DEMO bars as rounds 25-36. HOLD
(2025-01..2026-09) stayed closed in every stream (series cut at 2024-12-31 at load; disclosures in STREAM_M.md).

## Answer
No LIVE or DEMO candidate. Four forced-flow families with public, dated triggers were loaded for the first time (SHFE
daily trade parameters 2013-24, SGE notices 2008-24, Binance / Bybit funding 2018-24, Eastmoney Stock Connect 2014-24,
record levels on 22 IC symbols). Two show real effects at mid (BTC falls into a large-funding stamp by about the funding
paid; prices continue after fresh salient extremes, previous-week mid t 4.02), both below IC's cost and short of power
even at zero cost. Margin hikes and Connect flows show nothing beyond co-movement.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| M | SHFE gold / silver base-margin and limit changes (2,733 daily parameter files 2013-24), SGE pre-holiday hikes 2008-24 (57 events), SHFE client net OI, copper hikes -> AUDUSD; 17 cells. CME history unreachable (cmegroup.com times out; web.archive.org flagged this IP after 6 requests) | **none**: ~4.7 hikes / year in VAL caps HOLD at ~8 trades (LIVE impossible); best declared IS t +1.31 vs a best-of-17 null median 1.74; holiday hikes have no price effect in any era (Hedegaard's null); discretionary hikes = limit-locked big-day momentum | [STREAM_M.md](round37_forced_flows/STREAM_M.md) |
| F | Perpetual-funding stamps (00/08/16 UTC) conditioned on the predicted rate (Binance funding 2019-09+, premium index, Bybit inverse 2018-11+); short into the stamp / long after; BTCUSD at IC, ETH as information; CME expiry hot-carry months; 36 + 36 + 2 cells | **none**: PP-A5 w15 PRE mid +8.9 (t 1.91) IS / +15.3 (2.68) VAL, but IS cost 7.7 bp -> net +1.16 (t 0.27); IS mid t < 2 even at zero cost; large-funding stamps nearly vanish 2022-24 (HOLD n ~20-65); no rebound after the stamp; best IS mid t 2.37 at null p 0.27 | [STREAM_F.md](round37_forced_flows/STREAM_F.md) |
| A | Stop orders through fresh records (all-time, 52-week high / low) on 12 IC symbols and 10 FX pairs, the gold $50 construction with the 250 ms tick model; calendar-period extremes (prior month / quarter / year, release-day range); previous week, 200-day average; PRE gold / silver / FX; 159 cells | **none at book level**: continuation after a fresh extreme is real at mid (C previous week mid t 4.02, null p 0.001) but +1-7 bp against a 1-4 bp round trip, and power at zero cost <= 2.3; best book A1 52-week high 60 min IS net t 1.97 / VAL 1.27; 52-week lows reverse; FX records ~0. BTC K5 meets DEMO numbers on 9 IS trades (draft written, **not registered**: VAL positive only through one +955 bp trade, HOLD power 0.57) | [STREAM_A.md](round37_forced_flows/STREAM_A.md), [PREREG_DRAFT_A_btc_record_stop.md](round37_forced_flows/PREREG_DRAFT_A_btc_record_stop.md) |
| N | Stock Connect northbound / southbound daily net buy and quota 2014-24 -> HK50, USDCNH, AUDUSD, JP225, US500; Connect-closed blocks, reopening days, MSCI / FTSE inclusion closes, quarter-end window; 36 cells | **none**: same-window co-move (northbound vs HK50 +0.47) but next window \|corr\| <= 0.06; best declared IS t +1.72 (northbound -> USDCNH, VAL negative; northbound net flow unpublished since 2024-08-19); HK50 rose in 10 / 13 VAL Connect-closed blocks (wrong side); quota never binds since 2018 | [STREAM_N.md](round37_forced_flows/STREAM_N.md) |

Correlation with C3: not computed for M / F / N (nothing survived); stream A's cells ~0 (daily -0.015 to +0.028).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Exchange margin / price-limit changes at SHFE / SGE (holiday routine and discretionary hikes, post-holiday cuts,
  SHFE client OI) for gold, silver, copper -> AUD; leverage-cap dates (ESMA, FCA, ASIC, JFSA, crypto 2021) are too few.
- Perpetual-funding stamps conditioned on the predicted rate (BTC, ETH, 2018-24): real at mid, below IC's 2020-21 cost,
  and the large-funding regime disappeared after 2021.
- Stops beyond records and salient extremes (all-time / 52-week, prior week / month / quarter / year, release-day
  ranges, 200-day average) on indices, metals, BTC and FX: continuation at mid below cost; gold records add nothing to
  the $50 rule.
- Stock Connect flows and calendar (daily flows, closed blocks, inclusion steps, quarter-end).

## Pitfalls
- web.archive.org rate-limits hard and then flags the IP as abusive (round 37 M); don't use it as a bulk source.
- SHFE `ContractDailyTradeArgument{YYYYMMDD}.dat` is a clean daily margin / limit history from 2013-07; the effective
  day of a change is the day before the first file showing it.
- Eastmoney `RPT_MUTUAL_DEAL_HISTORY` answers in 60-80 s per page; northbound net buy is null from 2024-08-19.
- data.binance.vision funding zips start 2020-01; `fapi.binance.com/fapi/v1/fundingRate` goes back to 2019-09-10.
  OKX's funding API keeps ~3 months only. BitMEX shows a wind-down page (ceased trading 2026-09-23 per its host).

## Directions that need the user
| direction | value |
|---|---|
| CME product-level margin history (DataMine licence or FOIA) | LIVE ~1 %, DEMO ~3 % |
| OANDA order / position book (account) | unchanged from round 31: DEMO ~3-5 %, LIVE ~1 % |
| Paid intraday Stock Connect flow (Wind / iFinD) | LIVE ~1 %, DEMO ~3 % |
| Paid BitMEX funding 2016-19 (Tardis / Kaiko); grading BTC IS at today's cost | < 1 % each |

## Forward logs (same day)
- F3 / E1 slice 4 (FWD 2026-09-25..10-28): F3 FWD n 5, net -5.03 bp; HOLD + FWD n 122, +1.71 (t 1.82), down from 1.96.
  E1 HOLD + FWD +0.51 (t 0.82). [PREREG_R24_forward.md](round24_relaxed/PREREG_R24_forward.md).

## State after round 37
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 38 opens next.
