# Round 33: cross-venue premiums and margin books (crypto, gold), central-bank sight deposits (CHF)

2026-10-27 (UTC). Third round after the user resumed the research with other sources allowed. Brief:
[round33_cross_venue/BRIEF.md](round33_cross_venue/BRIEF.md), written 19:02 UTC before any return. Same bars as rounds
25-32 (LIVE / DEMO, no RELAXED tier). The idea: the same asset priced in a second, segmented market measures local
demand that has to cross over through a known channel. HOLD stayed closed (new series cut at 2024-12-31, IC prices at
ts < 2025-01-01). Disclosed slips, none used: stream K's first `head` printed one 2026-10 ECB EUR/USD/KRW row (file cut
and the full copy deleted); stream S's SGE benchmark endpoint ignored its end date and printed one 2026-10-26 row (raw
file overwritten).

## Answer
- **No LIVE candidate. No DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- Segmented-market premiums are real and persistent (Coinbase vs Binance, Korea, Shanghai), but the one with a stable
  sign (Coinbase rich -> BTC up) is 0.07-0.16 sd per trade with IS t < 2, and the SGE premium has no 1-5 day
  information about London gold. SNB sight deposits moved USDCHF only in the 2009-15 floor era.
- Correction for PROMPT: "premium SGE" was listed under paid data; it is free (SGE publishes the benchmark and daily
  quotes), and it shows nothing.

## Streams
| stream | source | cells | best IS net t (chance) | verdict | file |
|---|---|---|---|---|---|
| K | Coinbase BTC / ETH candles vs Binance (data.binance.vision) from 2017; Upbit KRW vs Binance (ECB KRW reference rate); Bitfinex margin funding | 85 | 1.74 post hoc (chance 2.69) | none | [STREAM_K.md](round33_cross_venue/STREAM_K.md) |
| S | SGE Shanghai Gold Benchmark 2016-24, Au99.99 close 2012-24 (archive crawl), Au(T+D) delivery direction 2014-24; SNB weekly sight deposits 2009-24 | 13 | +0.53 (best of 13 median ~1.65) | none | [STREAM_S.md](round33_cross_venue/STREAM_S.md) |

### K: crypto cross-venue premiums
- Coinbase rich vs Binance / Bitfinex -> BTC up over 1-3 days: positive in IS and VAL and all 8 years, VAL stronger
  (t 2.0-2.7), but IS t 1.4-1.7 (DEMO needs 2.0), per-trade Sharpe 0.07-0.16 against BTC's 300-450 bp daily sd,
  power 0.9-1.7.
- Kimchi premium: the declared contrarian side is wrong (a high premium continues, not reverts).
- Bitfinex margin funding: nothing.

### S: gold in segmented markets, SNB
- Premium timing checked on prices only, before returns: the Au99.99 close is a 15:30 Beijing print (07:30 UTC, the
  minimum of the premium change's sd in every group of years); AM benchmark 02:15 UTC; the PM benchmark's clock drifts
  (06:15 -> ~07:00 UTC), dropped. Median premium +22 bp PRE, +44 IS, +66 VAL.
- S1-S5 (premium deviation from its 20-day mean -> XAU / XAG, 1-5 days): IS net -2.3 to -21 bp, the dose slope flips
  sign between PRE, IS and VAL in every cell (S5: +15.6 per sd PRE, -27.3, t -3.48, IS, +17.5 VAL).
- T1-T2 (Au(T+D) "short pays long" delivery direction = long): IS -5.50 (t -2.50) / -13.16 (t -2.98); the reverse
  side was not declared and is flat in PRE and VAL.
- N1-N6 (SNB sight deposits up = CHF weaker, Monday 09:30 UTC): PRE 2009-15 has the declared sign everywhere and a
  dose response (USDCHF +7.47 bp per sd, t 3.92), mostly on the release Monday itself; gone from 2016 (IS dose t
  0.87). Weekly cadence caps power at ~1.0 even at the PRE size.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Crypto cross-venue premiums (Coinbase, Korea) and Bitfinex margin funding at 1-5 days.
- SGE gold premium (benchmark AM, Au99.99 close) and the Au(T+D) delivery direction for XAU / XAG.
- SNB weekly sight deposits for USDCHF / EURCHF (an effect of the 2009-15 floor era only).

## Directions that need the user
| direction | value (chance of a LIVE candidate) |
|---|---|
| GBTC daily prices before 2024 for the GBTC premium (Stooq blocked by robots and a JS challenge, Yahoo unreachable) | LIVE ~0 % (the trust became an ETF in 2024), information only |
| Point-in-time tick-level cross-venue crypto data (Kaiko / Tardis, paid) | low |
| Indian gold premium (WGC GoldHub login, or the paid IBJA API) | ~1 % |
| Accepting an IS from 2020 for the Coinbase premium | a bar change, not proposed |

## State after round 33
Unchanged: C3 is the only LIVE algorithm; F3 live 0.01 lot, E1 and the gold $50-level rule on demo. Round 34 (SHFE /
INE positioning, ETF / ETP rebalancing dose, Deribit option flows) is open.
