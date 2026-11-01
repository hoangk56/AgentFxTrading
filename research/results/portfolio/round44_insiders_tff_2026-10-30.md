# Round 44: aggregate corporate insider trading; CFTC Traders in Financial Futures positioning, 2026-10-30

Brief: [round44_insiders_tff/BRIEF.md](round44_insiders_tff/BRIEF.md). Same LIVE / DEMO bars as rounds 25-43. HOLD
(2025-01..2026-09) stayed closed in both streams (SEC quarters after 2024 Q4 refused by the fetcher, filings after
2024-12-31 asserted absent; TFF rows as-of <= 2024-12-24 because the 12-31 report is released in 2025; IC cut at load).
Both pulls were fast (I ~1 minute, T ~10 minutes in total).

## Answer
No LIVE candidate; one DEMO-number cell, not registered. Aggregate insider trading lives at months and is unstable
between eras; at <= 5 days it is 1-3 bp a day per sd against a ~4.5 bp index round trip. TFF positioning (leveraged
funds, asset managers, dealers) carries nothing at 1-3 days after the Friday release.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| I | SEC DERA insider transactions data sets 2014 Q1..2024 Q4 (606k Form 4 P / S filings, officers and directors, value capped $10 M): aggregate net purchases (count / value, daily / weekly), surges after falls, large / small split by Vanguard 13F ranks, CEO / CFO buys, cluster buying -> long US500 / USTEC / US30 / US2000 1-5 days from 09:31 ET after the filing day; 104 cells + 8 by-products | **none**: 0 of 64 aggregate cells IS t >= 2; F3 large-cap value weekly k1.5 -> US500 h1 met the DEMO numbers (net IS +25.3, t 2.23 / VAL +2.5) at chance (best-of-104 p 0.68), IS t 1.88 without 2020-03/04, VAL < 0 without its top 3 trades, and the series is really missing sales in blackout weeks: draft not registered; slope at 20-60 days +45-116 bp per sd in IS but negative in VAL | [STREAM_I.md](round44_insiders_tff/STREAM_I.md), [HYPOTHESES_I.md](round44_insiders_tff/HYPOTHESES_I.md), [PREREG_DRAFT_I_large_insider_value_us500.md](round44_insiders_tff/PREREG_DRAFT_I_large_insider_value_us500.md) |
| T | CFTC TFF futures-only 2010-07..2024-12 (Hugging Face mirror, matched exactly to CFTC legacy files on disk) on 13 legs (7 FX, ES / NQ / DJ / RTY / NKY, VIX): leveraged-fund crowding reversal, against leveraged-fund changes, with asset-manager changes, dealer extremes, asset managers vs leveraged funds; vol-scaled book, Friday 15:50 ET -> Monday / Wednesday; disaggregated managed-money controls on gold / silver / WTI / gas; 30 + 12 + 208 cells | **none**: best TFF book IS net t +0.76 (equal-weight bp book +1.04), best-of-24 mid p 0.34; asset-manager continuation wrong sign (XS h3 IS t -3.00); commodity control "fade managed-money weekly change" positive in IS and VAL (IS t 0.66-1.35, leans on 2020, PRE negative in 3 / 4) | [STREAM_T.md](round44_insiders_tff/STREAM_T.md), [HYPOTHESES_T.md](round44_insiders_tff/HYPOTHESES_T.md) |

Correlation with C3: insider draft cell -0.008 daily; others not computed.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Aggregate corporate insider trading (count / value, surges after falls, size splits, CEO / CFO, cluster buys) ->
  US indices at 1-5 days.
- CFTC TFF positioning (leveraged funds, asset managers, dealers; levels, changes, cross-sections) at 1-3 days;
  disaggregated managed-money level and swap-dealer controls.

## Pitfalls
- **www.cftc.gov's robots.txt disallows ClaudeBot / anthropic-ai / Claude-Web (read 2026-10-30).** Round 39 D fetched
  CFTC annual COT files from cftc.gov before this was checked; those files stay on disk for checks only and cftc.gov is
  off limits from now on. publicreporting.cftc.gov answers 403. The Hugging Face mirror `XOOMAR/cftc-commitments-of-traders`
  (robots allows `*`) matches the CFTC files exactly; it lacks TFF 2006-09, spreading columns and NYMEX WTI before 2022.
- SEC insider data sets: path `files/structureddata/data/insider-transactions-data-sets/<YYYY>q<Q>_form345.zip`;
  FILING_DATE is DD-MON-YYYY, no acceptance times (use the 22:00 ET filing deadline); the 2014-24 pull takes ~1 minute.
  Large-cap "net purchase" series are sale-volume series that follow the blackout calendar: compare with
  calendar-matched random entries.

## Directions that need the user
| direction | value |
|---|---|
| IC single-stock CFDs (MT5): trade the firm after its own opportunistic insider buys (Cohen, Malloy & Pomorski) | LIVE ~2-3 %, DEMO ~10 % |
| A declared commodity family "fade the managed-money weekly change" on XAU, XAG, XPT, XTI, XBR, XNG (IS already seen on 4 legs) | DEMO ~2 %, LIVE ~0 % |
| pyarrow in a scratch venv for parquet COT mirrors (point-in-time release times, TFF from 2006) | DEMO < 1 % |

## State after round 44
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 45 opens next.
