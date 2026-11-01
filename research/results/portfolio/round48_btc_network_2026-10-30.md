# Round 48: Bitcoin network fundamentals from block data (hashrate, difficulty, fees, hashprice), 2026-10-30

Brief: [round48_btc_network/BRIEF.md](round48_btc_network/BRIEF.md). Same LIVE / DEMO bars as rounds 25-47.
HOLD (2025-01..2026-09) stayed closed (every series cut at ts < 2025-01-01 at parse, IC at load, before anything was
printed). HYPOTHESES_N.md written 08:28 UTC before any conditional return; addendum (A1 hashrate shock, A2 linear
slopes) 08:31 UTC before its own numbers. 13 requests, ~2 minutes of network.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. None of 37 BTC cells reaches IS net t 2; the best |IS net t| is 1.88 with
the wrong sign, against an expected best-of-37 |t| of 2.40. Hash-ribbon / capitulation rules fire 2-7 times per era
(no power); difficulty adjustments flip sign between eras (IS -50 bp / VAL +72 bp at 1 day) and are predictable days
ahead from block times; hashprice lows behave like the price-only rule; fee / mempool spikes carry nothing. Next-day
linear slopes are |t| <= 1.18 in IS and <= 1.07 in VAL.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| N | Coin Metrics community block series, mempool.space exact retargets, blockchain.com mempool snapshots -> BTCUSD (ETHUSD second leg, US500 / XAU controls): F1 hash ribbons / capitulation, F2 difficulty adjustments, F3 hashprice lows, F4 fee share / mempool congestion, declared BOOK; PRE 2012-17 on Coin Metrics prices; 37 cells | **none**: BOOK net IS -18 bp (t -0.81) / VAL -8 (t -0.46); best positive IS net t 1.54 (mempool follow, VAL -12); F2 rel-all 1 d IS t -1.21 / VAL t 1.88; ETH IS cost 141-215 bp; US500 IS readings are 2018 / 2020 risk-off only | [STREAM_N.md](round48_btc_network/STREAM_N.md), [HYPOTHESES_N.md](round48_btc_network/HYPOTHESES_N.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Bitcoin network fundamentals (hashrate, hash ribbons, capitulation, difficulty adjustments, hashprice, fee share,
  mempool congestion) -> BTC / ETH at 1-5 days.

## Pitfalls
- Coin Metrics community has no difficulty / revenue metrics: hashprice = (IssTotNtv + FeeTotNtv) x PriceUSD / HashRate.
- mempool.space difficulty rows are [ts, height, difficulty, ratio], include a genesis row and run to today; the
  blockchain.com mempool-size file (~11 MB) runs to today: parse with the cut, never `head` it.
- Raw retargets are positive in 72 % of epochs (declare a trend reference); BTC-denominated hashprice sits at a 90-day
  low on 80-100 % of days.
- Fixed-side shorts in a bull IS beat 85-90 % of random shorts while losing money: read the random percentile with net.

## Directions that need the user
| direction | value |
|---|---|
| Paid point-in-time miner flows / reserves (CryptoQuant, Glassnode) | LIVE < 1 %, DEMO ~1 % |
| Pool payout / hashprice index history (Luxor, Foundry; accounts) | < 1 % |

## State after round 48
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 49 opens next.
