# Round 56: short-term cross-section of IC-listable US large caps (no-news reversal, news continuation), 2026-10-30

Brief: [round56_stock_cross_section/BRIEF.md](round56_stock_cross_section/BRIEF.md). Continues the user-approved
single-stock CFD direction (2026-10-30). Research only. Same LIVE / DEMO bars as rounds 25-55. HOLD stayed closed: D's
panel ends 2024-12-31 (`dates < 2025` asserted), 8-K rows dated 2025+ dropped at parse; nothing was downloaded.
HYPOTHESES_R.md was written before any return.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. All 48 cells are net negative in VAL; best net IS t +0.76 (F3 L5 h5 k3:
+28.9 / VAL -86.7). The primary (no-news reversal, 5-day residual, hold 5, k 9 a side, 6 bots) is -1.3 bp per position
IS (t -0.09) / -36.9 VAL (t -2.51), 1 of 8 years positive. Large caps reverse a little at mid (F1 1-day gross +3 to +22
bp), but a close-fill round trip on extreme movers costs ~20-24 bp (spread ~10, commission ~9, financing 1-6); the best
gross IS t 2.39 sits under the max-t null p95 2.97 and falls to +4-5 bp on the other book start days.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| R | 207 D stocks (price >= $10, close spread <= 50 bp); residual return vs beta x SPY (sector-ETF variant) over 1 / 5 days; dollar-neutral top / bottom k = 3 / 6 / 9 at the close bid / ask; F1 no-news reversal (no 8-K 2.02), F2 news continuation, F3 Nagel high-vol reversal (SPY 20-day realized vol); holds 1 / 3 / 5; 48 cells | **none**: primary -1.3 (t -0.09) / -36.9 (t -2.51); x1.5 spread -6.4 / -42.5, +1 day -6.6 / -33.0, ex-2020-03/04 IS -12.4; F2 gross ~0; F3 paid only 2020-21 (2022 -42 to -90 net); news filter adds ~2 bp in the predicted direction; zero-cost HOLD t of the best VAL gross cell ~1.2 | [STREAM_R.md](round56_stock_cross_section/STREAM_R.md), [HYPOTHESES_R.md](round56_stock_cross_section/HYPOTHESES_R.md), R_out/ |

Correlation with C3: nothing survived; for information +0.046 (primary) / +0.007 (best gross cell).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Short-term cross-section of ~200 US large caps: no-news reversal (Chan / DLS / Lehmann; SPY-beta or sector-ETF
  residual, 1 / 5-day signal, 1-5 day hold, k 3-9, Nagel high-vol condition) and 8-K 2.02 news continuation.

## Pitfalls
- Non-overlapping 3-5 day books depend on the start day: report the mean over start days (or overlapping books with HAC
  errors) before quoting a figure.
- Extreme movers pay ~2x the median spread and commission even with a $10 floor.
- Beating 95 % of random books is an easy bar for a dollar-neutral book (the null has zero gross and the same cost):
  pair it with the max-t benchmark on gross returns.
- The daily panel has no dividends (a few bp at most).

## Directions that need the user
| direction | value |
|---|---|
| A venue without per-share commission | best ~+8 IS / -1.5 VAL bp, start-day dependent; DEMO < 1 % |
| Mid / small caps (not at IC / Dukascopy) | LIVE ~1 % |
| Paid intraday news timestamps | LIVE < 1 %, DEMO ~1-2 % |

## State after round 56
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Daily-fill stock rules at IC
need > ~20 bp per position; the remaining stock idea with per-event moves of that size is the earnings gap itself
(round 57: continuation / fade of large earnings gaps entered at 09:45, M1 on those days only).
