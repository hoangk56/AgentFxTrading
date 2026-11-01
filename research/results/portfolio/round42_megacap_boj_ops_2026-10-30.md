# Round 42: index heavyweight earnings; Bank of Japan JGB purchase operations, 2026-10-30

Brief: [round42_megacap_boj_ops/BRIEF.md](round42_megacap_boj_ops/BRIEF.md). Same LIVE / DEMO bars as rounds 25-41. HOLD
(2025-01..2026-09) stayed closed in both streams (EDGAR filings after 2024-12-31 dropped at parse, BoJ rows after
2024-12-31 dropped with an assert, IC cut at load; disclosures in STREAM_E.md and STREAM_J.md). Pulls took ~5 min (E)
and ~18 min (J).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Heavyweight earnings move the index after hours, but nothing continues or
reverses past IC's after-hours spread, and the index announcement premium is absent in VAL. The market does not trade
BoJ operation results (no tick-activity change at the release); amount changes are rare and move EUR, not JPY.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| E | Top 40 US index weights per year (Vanguard 13F year-ends 2015-23), 1,510 8-K item 2.02 releases with EDGAR acceptance times: after-hours continuation (F1a), open-to-close reversal (F1b), announcement premium on news / early-season days (F2), pre-release drift (F3), first minutes after the release (B1) -> US500, USTEC, US30 (DE40 / JP225 controls); 132 cells | **none**: 0 cells IS t >= 2 (best F1a top-10 US500 net IS +39.5, t 1.69, n 25; chance p95 3.05); the 19:00 -> 09:30 IS reversal also shows on DE40 / JP225 and random evenings (a 2016-21 evening-session property); F2 IS +9.9 (t 1.55) / VAL -1.4; B1 +2-5 bp at mid in VAL, below the after-hours spread | [STREAM_E.md](round42_megacap_boj_ops/STREAM_E.md), [HYPOTHESES_E.md](round42_megacap_boj_ops/HYPOTHESES_E.md) |
| J | BoJ monthly operation files 2013-06..2024-12 (4,098 JGB purchase rows: offer-to-cover, cut-off / average spread by bucket), 167 schedule / outline PDFs, fixed-rate (YCC defence) operations -> USDJPY, EURJPY, JP225 (XAU control); entry 14:30 JST after results, 17:30 JST after schedules; PRE 2013-15 on Dukascopy; 96 cells | **none**: best positive IS t 1.65 (F3 YCC defence -> USDJPY, 7 events, VAL +2.2); largest \|t\| 2.90 wrong side and flips in VAL; within-month amount change -> EURJPY positive in three eras (IS +15.4, t 1.40 / VAL +24.9, t 1.81) but only the EUR leg moves; tick activity at ~12:00 JST on operation days 0.90-1.21x other days; daily corr with C3 -0.04..+0.03 | [STREAM_J.md](round42_megacap_boj_ops/STREAM_J.md), [HYPOTHESES_J.md](round42_megacap_boj_ops/HYPOTHESES_J.md) |

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- US index heavyweight earnings at the index level (after-hours continuation / reversal, open-to-close, announcement
  premium, pre-release drift, first minutes after acceptance) on US500 / USTEC / US30.
- BoJ JGB purchase operations (offer-to-cover, cut-off spreads, schedule and within-month amount changes, fixed-rate
  YCC defence) -> USDJPY, EURJPY, JP225.

## Pitfalls
- EDGAR `acceptanceDateTime` in the submissions JSON is true UTC; 8-K 2.02 releases cluster at 06-08 and 16:00-16:15
  ET. iShares IVV historical holdings now return HTML; Vanguard 13F-HR info tables give year-end weights.
- IC index CFDs have no bars at 16:15-16:29 and 16:59-17:59 ET; 16:44 bars are sparse in 2016-17.
- BoJ monthly operation files (`.../fm/ope/m_release/YYYY/opeYYMM.{zip,xlsx}`) start 2013-06 (PDF before); the
  format changes three times. 2016-09..2020-02 schedule amounts sit in attachments outside the PDF text. Historical
  result release times are not online (old www3 pages 404).

## Directions that need the user
| direction | value |
|---|---|
| IC single-stock CFDs (MT5 only): trade the heavyweight itself after its release (round 25 A estimate) | LIVE ~3-5 %, DEMO ~25 % |
| A cheaper after-hours index venue (ES / NQ / YM futures) for the B1 drift | LIVE ~1 %, DEMO ~3 % |
| Paid intraday JGB futures / yen OIS ticks; paid point-in-time earnings calendars and float weights | LIVE < 1 %, DEMO ~1-2 % |

## State after round 42
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 43 opens next.
