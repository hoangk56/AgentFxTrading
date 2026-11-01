# Round 39: scheduled futures-roll flows; retail and broker-client positioning, 2026-10-29

Brief: [round39_rolls_positioning/BRIEF.md](round39_rolls_positioning/BRIEF.md). Same LIVE / DEMO bars as rounds 25-38.
HOLD (2025-01..2026-09) stayed closed in both streams (IC cut at load, EIA graded through 2017 only, CFTC files 2004-24
without the report released in 2025, JPX 2016-24 archive pages only; disclosures in STREAM_R.md and STREAM_D.md).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Roll pressure is real but lives in the calendar spread, which IC does not
offer; IC's XTI / XBR are interpolated between the front two contracts with no roll day. No free broker-client
sentiment history is reachable without an account; the public substitutes (CFTC small-trader positions, JPX investor
types) are weekly, so LIVE was impossible from the count, and no cell holds from IS to VAL.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| R | GSCI / BCOM / pre-2020 USO roll window (business days 5-9): short over the window, long after, short before -> XTI, XBR, XNG on IC 2018-24, CL1 / NG1 settlements 1995-2017 as PRE; XAU / XAG / US500 controls; 15 declared cells | **none** (DEMO ruled out by the count before returns: 12 windows a year, literature size 25-38 bp in the C2-C1 spread vs a 5-day sd ~500 bp, expected IS t ~0.35): best IC cell XBR R1 net IS +45.9 (t 0.44) / VAL -106.7; XTI R1 IS is all 2020-03/04. C2-C1 widens +17.7 bp (t 2.11) in the window and narrows after, shrinking 30.7 -> 10.8 bp from 1995-99 to 2012-17; contract 1 outright does not carry it | [STREAM_R.md](round39_rolls_positioning/STREAM_R.md), [HYPOTHESES_R.md](round39_rolls_positioning/HYPOTHESES_R.md) |
| D | Probe of free broker sentiment archives (Dukascopy SWFX, FXCM SSI, Myfxbook, Gaitame, IG / DailyFX, FXSSI, AAII, NAAIM): none reachable with 2016-21 history; then CFTC COT non-reportable (small-trader) positions 2004-24 on 17 markets (level, change, against large specs, FX cross-section; Friday 15:50 ET -> Monday / Wednesday) and JPX weekly investor-type flows in Nikkei futures 2016-24; 14 book + 204 single COT cells, 8 JPX cells | **none**: best D3 (with large specs against small traders, k2 h1 book) net IS +28.8 (t 2.06) / VAL -15.7, mid t 2.56 inside the best-of-14 null (p95 2.69); individuals' Nikkei flow wrong sign; weekly sources need weekly Sharpe >= 0.35 for LIVE | [STREAM_D.md](round39_rolls_positioning/STREAM_D.md), [HYPOTHESES_D.md](round39_rolls_positioning/HYPOTHESES_D.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Commodity-index and commodity-ETF roll calendars (GSCI, BCOM, USO / UNG) on outright energy CFDs; January
  reweighting (1 a year); metals rolls (financing only); IC's own CFD roll (none: XTI / XBR interpolated, XNG = NG1).
- CFTC COT small-trader (non-reportable) positions as a contrarian signal at 1-3 days, alone, against large
  speculators, or as an FX cross-section; JPX weekly investor-type flows (individuals, foreigners) into JP225.
- Free broker-client sentiment archives: none reachable without an account or payment from this Mac.

## Pitfalls
- IC XTIUSD vs CL settlements: x = (IC - CL1) / (CL2 - CL1) drifts from ~-0.4 after expiry to +0.2 at business day 13,
  so IC's crude is a blend, not a front-month series with a switch day.
- JPX weekly CSVs: product 301 = Nikkei 225 futures (kJPY), 313 = mini; investor 50 = individuals, 60 = foreigners;
  archive pages `00-archives-02` (2024) to `-10` (2016); ~1 file per 3 s.
- CFTC COT: the report as of 2024-12-31 is released in 2025, so drop it under the HOLD cut.
- Added 2026-10-30 (round 44 T): www.cftc.gov's robots.txt disallows ClaudeBot; the annual files used here were fetched
  before that was checked. Do not fetch from cftc.gov again; the Hugging Face mirror matches the files exactly.
- www.dukascopy.com, Myfxbook and Gaitame time out from this Mac; Dukascopy freeserv widget paths return 403 (embed check).

## Directions that need the user
| direction | value |
|---|---|
| Dukascopy JForex demo account (SWFX sentiment history, 30 min, FX / metals / indices) | DEMO ~3 %, LIVE ~1 % |
| FXCM premium SSI history (paid, ~32 symbols) | DEMO ~3 %, LIVE ~1 % |
| OANDA order / position book (account; unchanged since round 31) | DEMO ~3-5 %, LIVE ~1 % |
| A venue with dated single-contract energy futures / CFDs (trade C2-C1 across the roll) | DEMO ~1-2 %, LIVE < 1 % |
| FXSSI / Myfxbook accounts; AAII / NAAIM paid history | ~1 % or less |

## State after round 39
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 40 opens next.
