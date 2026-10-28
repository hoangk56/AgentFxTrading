# Round 35: listed-option volume (OCC / CBOE put-call), Asian equity-derivative positioning (TAIFEX, TWSE)

2026-10-28 (UTC). Fifth round after the user resumed the research with other sources allowed. Brief:
[round35_options_volume_asia_positioning/BRIEF.md](round35_options_volume_asia_positioning/BRIEF.md), written 01:24 UTC
before any return. Same bars as rounds 25-34 (LIVE / DEMO, no RELAXED tier). HOLD stayed closed (requests and parsers cut
at 2024-12-31, IC prices at ts < 2025-01-01). Disclosed: stream O's OCC format probe printed SPY volume by account type
for 2024-11-01 (before HOLD).

## Answer
- **No LIVE candidate. No DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- Free option-volume data mixes opening and closing, buying and selling, customer and dealer volume, so any informed
  flow is diluted to nothing at the class level; Taiwan's institutional positioning moves with the market on the same
  day and does not predict the next one.

## Streams
| stream | source | cells | best IS net t (chance) | verdict | file |
|---|---|---|---|---|---|
| O | CBOE put/call archive 2006-11..2019-10 spliced with the CBOE daily statistics JSON 2019-10..2024 (by class, OI from 2019-10); OCC market-wide daily volume 2008-24. The OCC per-underlying / per-account query refuses dates more than 2 years back (from 2024-10-28 only) | 116 graded + 324 information regressions; O7 (FINRA ETF short-volume ratio, 72 cells) declared, **not graded**: the lead stopped its 2-hour download to close the round (declared prior power < 0.5; FINRA short volume is also DIX's source, round 4) | 1.64 (null p50 1.89, p95 2.53) | none | [STREAM_O.md](round35_options_volume_asia_positioning/STREAM_O.md) |
| T | TAIFEX three-institution futures / TXO positions via the FinMind open API (2018-06..2024; verified against TAIFEX's own page; the official site serves only the last 3 years), TWSE cash flows by institution 2004-24 | 66 | 1.76 (median max of 66 ~2.56) | none | [STREAM_T.md](round35_options_volume_asia_positioning/STREAM_T.md) |

### O: put/call and option volume
- Equity P/C contrarian -> USTEC 1 d: IS +7.9 bp (t 0.87), VAL +7.4 (t 0.50). SPX P/C: every IS pick < 0.
- ETP P/C -> US2000 5 d: IS +57.6 (t 1.64), VAL -36.5. VIX P/C -> US500, equity P/C -> FX / gold / oil, OCC volume ->
  short indices: nothing; XTI and EURUSD signs flip between eras.
- Information regressions (224): none with |t| > 1.5 and the same sign in IS and VAL; equity P/C -> next-day US500
  +0.3 bp per sd. OI P/C (2019-10..) IS hits do not repeat in VAL.

### T: Taiwan positioning
- Foreign net futures OI change, follow -> AUDUSD / USTEC: IS t 1.32 / 1.01, VAL negative.
- Foreign net bullish TXO flow (Chang, Hsieh & Lai 2009) -> US500 3 d: IS +23.8 (t 1.76), VAL -19.0; random 0.99 IS,
  0.155 VAL.
- Foreign buying of Taiwan stocks -> AUDUSD: IS t 1.19, VAL t 0.57, PRE -0.09.
- Same-day co-movement is strong (investment trusts' futures change +0.45, foreign cash buying +0.40-0.48), next-day
  |rho| <= 0.09 everywhere (LIVE needs 0.17-0.23).
- KRX statistics are behind a login; NSE India 403 (Akamai); CFFEX ~60 s per request; JPX participant volume 13 months.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- CBOE put/call ratios by class 2006-24 (now continuous via the daily statistics JSON), OCC market-wide option volume, as
  1-5 day signals for indices, FX, gold, oil.
- TAIFEX institutional futures / option positioning (2018-24) and TWSE institutional cash flows (2004-24) for HK50, JP225,
  US indices, AUDUSD, USDJPY.

## Directions that need the user
| direction | value (chance of a LIVE candidate) |
|---|---|
| Paid open-close / open-buy option data (CBOE Open-Close, ISEE Select): the real Pan-Poteshman test | ~2-3 % |
| Paid per-symbol option history (CBOE DataShop, ORATS) for a per-ETF O/S ratio | ~1-2 % |
| OCC per-underlying volume by account (free, only from 2024-10-28): forward-only log of a rule declared now | ~1 % |
| TAIFEX history 2008-18 (paid application or a FinMind sponsor tier) | LIVE ~1 %, DEMO ~2-3 % |
| KRX account (foreigners' KOSPI200 and USD/KRW futures) | LIVE ~1 %, DEMO ~3 % |
| NSE India FII participant OI (blocked here) | ~1 % |
| Finishing O7 (FINRA ETF short volume; scripts ready in the round 35 O scratchpad) | < 1 % |

## State after round 35
Unchanged: C3 is the only LIVE algorithm; F3 live 0.01 lot, E1 and the gold $50-level rule on demo. Round 36 ran in
parallel.
