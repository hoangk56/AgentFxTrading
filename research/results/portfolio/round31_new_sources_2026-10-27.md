# Round 31: public non-price sources no round had used (Japan flow tables, practitioner communities, crypto on-chain and positioning, ETF holdings and weather)

2026-10-27 (UTC). On 2026-10-27 the user resumed the research ("research đến khi nào tìm được thuật toán live thì thôi")
and allowed searching other sources ("cho phép bạn tìm kiếm research các nguồn khác nhau"). Brief:
[round31_new_sources/BRIEF.md](round31_new_sources/BRIEF.md), written 18:12 UTC before any return. Same bars as rounds
25-30 (LIVE / DEMO, no RELAXED tier). HOLD 2025-01..2026-09 stayed closed in all four streams: new series cut at
2024-12-31 at parse, IC prices at ts < 2025-01-01. Disclosed slips, none used: stream G printed 5 IAU NAV rows of
October 2026 in a header peek and saw one 2026 GLD news snippet; stream C ran two download jobs against
data.binance.vision at once (~2 requests a second, against the 1 / s rule; no 429).

## Answer
- **No LIVE candidate. No DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- The idea behind the round: C3 works because a public, dated fact predicts the side and size of a real flow, so look
  for the same in public non-price data. The four streams found real information in several sources (TFX open interest
  shows Japanese retail's side; CPC outlooks carry natgas demand news; Binance retail crowding is real at mid), but in
  every case either the market prices it before it is public, or it predicts magnitude and not direction, or it is
  0.03-0.1 sd per trade, a third or less of what LIVE needs.

## Streams
| stream | source | cells | best IS net t (chance) | verdict | file |
|---|---|---|---|---|---|
| J | TFX Click 365 daily OI / volume 2005-24, MoF weekly securities flows, JPX investor-type and margin balances, MoF intervention record | 70 (4 post hoc) | +1.14 declared (post hoc T4 2.09, VAL -1.91) | none | [STREAM_J.md](round31_new_sources/STREAM_J.md) |
| P | Census of ~1,550 practitioner entries (Quantpedia, QuantConnect, GitHub, mql5, GogoJungle, TradingView, Chinese repos); 2 untested mechanisms declared | 6 | all negative on the declared side | none | [STREAM_P.md](round31_new_sources/STREAM_P.md) |
| C | CoinMetrics exchange flows (not point-in-time), Bitfinex margin longs / shorts 2016-24, Binance Vision futures metrics (BTC from 2020-09, ETH 2021-12), Binance liquidation snapshots (2023-24) | 80 + 4 info | 2.64 (X1, expected max 2.30 for 28, p95 3.12; all 80: chance 2.7) | none | [STREAM_C.md](round31_new_sources/STREAM_C.md) |
| G | SPDR GLD ounces 2004-24, iShares IAU / SLV shares, NOAA CPC 6-10 / 8-14 day temperature outlooks 2017-24 | 12 | +1.05 (best of 12 median ~1.6) | none | [STREAM_G.md](round31_new_sources/STREAM_G.md) |

### J: Japan's public flow and positioning tables
- Weekly MoF flows, JPX margin and investor-type tables do not predict USDJPY, the JPY basket or JP225 over 1-5 days
  even at ~10 bp (LIVE needs ~35 bp a week on USDJPY). Best declared IS net t +1.14 (M1 outward flows), VAL -1.30.
- TFX open interest shows Japanese retail acting as contrarians on the same day (|corr| up to 0.63) and volume
  predicts tomorrow's absolute move (t 2-7), but not its direction (|corr| <= 0.07 in every pair and era). Post hoc
  T4 (fade the inferred retail flow): IS +5.92 bp (t 2.09), VAL -1.91, PRE -5.34.
- Interventions: none in IS 2016-21, information only.

### P: practitioner and community strategies
- About 520 entries are indicator / chart rules with no economic basis; nearly all the rest map to families rounds
  2-30 exhausted. Japan's 朝スキャ is round 23's reopen-gap fade.
- P1, gold stops beyond prior-day / week / Asian-range extremes (the design of 2026's best-selling mql5 gold EAs): net
  -1.6 to -3.2 bp in IS; the prior-day break continued in 2004-15 (mid +2.78, t 4.38) and not since 2016: a decayed
  practitioner breakout. The same engine finds round 27's $50 cascade, so it can see one where it exists.
- P2, Friday position squaring: wrong sign (IS -4.67, t -1.77; VAL -2.90; PRE -2.45).

### C: crypto non-price data
- X1 net exchange deposits |z| > 2, fade, 1 day: IS +132 bp (t 2.64), VAL +11 (t 0.33), PRE +20; decays, random 80 %
  in VAL, and the data are restated with 2026 address labels (not point-in-time), so optimistic.
- Bitfinex long / short contrarian: IS +27-59 (t <= 0.82), power <= 0.9.
- Binance retail long / short at 4 hours: real at mid in both eras and both coins (gross t ~2.1-2.5) but ~0.07 sd per
  trade, a third of LIVE; BTC IS starts 2020-09, ETH has no IS.
- Open-interest build-ups continue (fade side VAL -142, t -2.13); liquidation spikes continue rather than reverse (L2,
  VAL only); the open-interest flush adds nothing to round 3's price-only cascade rule.

### G: ETF holdings and weather
- GLD flows chase gold's price and add nothing beyond 1-day momentum (flow coefficient = momentum coefficient in PRE
  and IS, both ~0 in VAL). G1a XAU 1 d: IS +1.86 (t 0.57), VAL -3.87. SLV: IS +6.93 (t 0.89), VAL +7.42 (t 0.95), but
  the IS dose slope is negative and PRE 2008-15 -5.01. The authorised participant buys bullion when ETF shares trade,
  before holdings are published: no execution clock, unlike gotobi.
- CPC outlook revisions correlate +0.23 (t 5.3 IS, 5.0 VAL) with XNG's move over the 24 hours **before** the ~15:00 ET
  posting: priced. After the posting nothing survives IC's XNG cost (12-25 bp IS, 44-47 bp VAL, + 4 bp a night).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Japan's public weekly flow / margin / investor-type tables and TFX Click 365 OI (direction not predictable).
- Practitioner / community strategy census 2026 (Quantpedia free, QuantConnect, GitHub, mql5, GogoJungle, TradingView).
- Crypto exchange flows (CoinMetrics community), Bitfinex margin positions, Binance futures positioning ratios and
  open interest, Binance liquidation snapshots.
- Gold / silver ETF holdings (GLD, IAU, SLV) and NOAA CPC temperature outlooks for natgas.

## Directions that need the user
| direction | value (chance of a LIVE candidate) |
|---|---|
| OANDA order / position book (account): where retail stops and limits sit, would test round 27's cascade mechanism directly | DEMO ~3-5 %, LIVE ~1 % |
| OANDA Japan / Gaitame / FFAJ daily retail net positions with the long / short split (accounts) | LIVE ~1-2 % |
| Point-in-time crypto exchange flows (CryptoQuant, Glassnode, Coin Metrics Pro; paid) | ~1 % |
| Exchange-aggregated crypto OI / long-short / liquidations from 2019 (Coinglass, Coinalyze, Kaiko; account, usually paid) | ~2 % |
| A long unattended free pull of Bitfinex liquidations (3-4 h) and ETH positions (~2 h) | < 1 % |
| Daily shares outstanding for USO / UNG / BOIL / KOLD (paid, or parse EDGAR) | ~0-1 % (round 34 E got ProShares BOIL / KOLD free: nothing) |
| Run-by-run weather model data (GFS free) on a sub-hour test with a cheap natgas venue | ~1 % |
| Retail sentiment ratios (IG, Myfxbook, DailyFX SSI), mql5 Signals histories, TradingView popularity | ~0-1 % |

Untested idea that does not need the user (noted by G): CME margin-change advisories for gold, silver and natgas, ~5-15
events a year per product, so DEMO at most.

## State after round 31
C3 is the only LIVE algorithm. F3 runs live at 0.01 lot and E1 on demo (EcbWindowBot); the gold $50-level rule runs on
demo (1 demo trade, +10.24 bp vs model +10.46; HOLD + demo t 1.45, promotion not reached). F3 / E1 forward log slice 3
(to 2026-10-26): F3 HOLD + FWD n 120, +1.86 bp (t 1.96); E1 HOLD + FWD +0.55 (t 0.87). Rounds 32-34 follow.
