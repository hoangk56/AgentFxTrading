# Round 38: daily short-sale volume and ETF primary flows; Atlantic storms and supply disruptions, 2026-10-29

Brief: [round38_short_volume_storms/BRIEF.md](round38_short_volume_storms/BRIEF.md). Same LIVE / DEMO bars as rounds
25-37. HOLD (2025-01..2026-09) stayed closed in both streams (FINRA requests only for dates <= 2024-12-31, issuer rows of
2025+ dropped at parse, HURDAT2 through 2024, EIA and IC series cut at 2024-12-31; disclosures in STREAM_S.md and
STREAM_H.md).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. FINRA Reg SHO daily short volume 2009-24 (6,388 files) and issuer share
counts for SPY, DIA, IWM, IVV, EWJ were loaded for the first time; 408 declared cells, no family beats its sign-flip
null. Storms reach the Gulf production box ~2-3 times a year, so LIVE was impossible from the count; the declared crude
and gas sides do not hold across eras.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| S | FINRA short-volume ratio (level, z vs 60 days, change) for 11 ETFs and the top-10 index weights; ETF creations / redemptions from SSGA / iShares; creation-delay buying (ETF minus component ratio); country-ETF short spread -> next local session; Rule 201 load via ShortExemptVolume; sides from Diether-Lee-Werner, Boehmer-Jones-Zhang, Evans et al., Brown-Davies-Ringgenberg, fixed before returns; 408 cells, next-day open-to-close to 5 days | **none**: best single cells DIA ratio -> short US30 net IS +9.0 (t 2.13) / VAL -5.0; EWG spread -> DE40 IS t 2.08 / VAL -1.01; books IS t -3.8..-0.1; best book day-Sharpe 0.058 (~0.9 a year) vs ~2.3 needed; family null p 0.33-0.97. Post hoc only: SPY + IVV creations continue (not reverse) in US500, flipped IS t ~1.4 (fails DEMO, side chosen from data) | [STREAM_S.md](round38_short_volume_storms/STREAM_S.md), [HYPOTHESES_S.md](round38_short_volume_storms/HYPOTHESES_S.md) |
| H | NHC HURDAT2 + ATCF a-deck official forecasts (190 storms 1995-2024): first threat to the Gulf production box / LNG zone, all-clear unwind, advisory revisions -> XTI, XBR, XNG (USDCAD, US500 controls); dated non-storm disruptions (Abqaiq, Colonial, Freeport); EIA futures settlements 1995-2017 as PRE; 30 declared cells | **none**: 19 IS / 4 VAL threats, ~5 expected in HOLD (LIVE needs per-event Sharpe 1.34); best right-side cell XBR 24 h after a forecast hurricane net IS +70.1 (t 1.53), VAL -52.8, PRE negative; gas rose after threats in IS (declared short, mid t -3.29) and fell in PRE 1995-2009: sign flips between eras, inside the 30-cell null (p 0.077); non-storm disruptions priced at the first minute | [STREAM_H.md](round38_short_volume_storms/STREAM_H.md), [HYPOTHESES_H.md](round38_short_volume_storms/HYPOTHESES_H.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- FINRA daily short volume on index, country and commodity ETFs and their top components (level, z, change, ETF minus
  basket, short-exempt share) -> US / foreign indices, metals, oil, FX at 1-5 days: short volume is market-maker
  hedging done immediately; Wang-Yan-Zheng's null holds.
- ETF primary flows (SPY, DIA, IWM, IVV, EWJ shares outstanding) as a reversal signal: flows follow price; the
  continuation seen in US500 is round 31 G's "flows chase price" and too weak to register.
- Atlantic storms (official forecast threats, all-clear, advisory revisions) and dated supply disruptions -> crude,
  Brent, US gas: 2-3 events a year, sides flip between eras, outages priced in the first minute.

## Pitfalls
- FINRA before 2018-08: consolidated = FNSQ + FNYX (FNQC / FNRA empty, FORF is OTC); ShortExemptVolume starts in 2011;
  the ratio level shifts at the 2018-08 CNMS switch, so use z vs a trailing window. "META" before 2022-06-09 is an
  unrelated ETF (use FB).
- cdn.finra.org serves ~1 file per 1.1 s; the full 2009-24 pull takes ~2 h.
- SSGA navhist and iShares history sheets contain 2025-26 rows (SSGA oldest-first, iShares newest-first): never `head`
  them, parse with the cut.
- ATCF a-decks (ftp.nhc.noaa.gov/atcf/archive/<year>/) give the official forecast per synoptic time; public issue =
  DTG + 3 h. EIA daily futures series stop at 2024-04. nrc.gov and bsee.gov answer 403.

## Directions that need the user
| direction | value |
|---|---|
| EIA API key (nuclear outages -> US gas) | DEMO ~2 %, LIVE < 1 % |
| BSEE shut-in PDFs (manual collection) | < 1 % |
| Rule 201 / threshold lists (nasdaqtrader bot wall: account or paid feed) | DEMO ~2 %, LIVE < 1 % |
| Paid daily shares outstanding for QQQ / USO / UNG; exchange-side short-volume files | < 1 % each |

## State after round 38
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 39 opens next.
