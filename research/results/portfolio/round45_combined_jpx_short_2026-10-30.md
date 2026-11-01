# Round 45: one declared combined model over the non-price sources of rounds 37-44; JPX daily short selling, 2026-10-30

Brief: [round45_combined_jpx_short/BRIEF.md](round45_combined_jpx_short/BRIEF.md). Same LIVE / DEMO bars as rounds 25-44.
HOLD (2025-01..2026-09) stayed closed in both streams (X: every source row after 2024-12-31 dropped at load with asserts,
no new data; S: ratio rows after 2024-12-31 asserted out at parse, karauri.net requested only up to 2024-12-30, IC cut at
load). Disclosure (S): one WebSearch summary quoted two 2025 JPX short-selling shares (signal values, not prices); not
used, nothing registered.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Pooling the 26 non-price feature families of rounds 37-44 in one declared
ridge gives an out-of-sample forecast-return correlation of about zero and sits inside a date-shuffled null, so the
single-source effects were noise, not small independent edges. The TSE-wide daily short-selling ratio moves with the
same day's return (corr -0.38) and carries nothing for the next session once that is removed; daily changes in large
(>= 0.5 %) short-position reports carry nothing either.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| X | Pooled ridge (lambda 0.1 N) over 26 families / 86 series from 13 sources (FINRA short volume, ETF creations, BTC funding, Connect, GDELT, China margin, auctions, EDGAR issuance, insiders, earnings weight, BoJ rinban, weather, TFF / COT, 52-week range), expanding yearly refits on IS, 12-symbol daily book, \|f\| >= 0.5 RMS, hold 1 day | **none**: net IS walk-forward -0.0336 R (t -2.30), VAL -0.0026 R (t -0.14); mid IS +0.0035 (0.24) / VAL +0.0217 (1.15); shuffled-feature null p 0.37 / 0.11; forecast-return corr -0.003 IS / +0.015 VAL; a third of coefficients flip sign between refits; HOLD power < 1 even at mid | [STREAM_X.md](round45_combined_jpx_short/STREAM_X.md), [HYPOTHESES_X.md](round45_combined_jpx_short/HYPOTHESES_X.md) |
| S | TSE-wide daily short-selling ratio 2017-24 (stock-marketdata.com chart data) and daily large short-position reports (karauri.net, 3,916 pages) -> JP225, USDJPY / HK50 controls: contrarian folk rule (primary) vs informed short, level / residual / change z, >= 45 % rule, overnight into the Tokyo open, report aggregates; 39 declared cells (78 with both sides) + 4 controls | **none**: best R3 residual z k1.5 h1 net IS +9.9 bp (t 0.99) / VAL +21.5 (1.67); best-of-24 mid p 0.70 (R1-R4), 0.77 (R5), 0.65 (K); R4 change z flips sign (IS +41.7 / VAL -138.7); restricted-price family dropped (no free daily source for 2024 or earlier) | [STREAM_S.md](round45_combined_jpx_short/STREAM_S.md), [HYPOTHESES_S.md](round45_combined_jpx_short/HYPOTHESES_S.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Combinations of the round 37-44 daily non-price features (pooled ridge, declared-side vote) at 1 day.
- JPX / TSE daily short-selling ratio (level, residual, change, >= 45 % folk rule, overnight) and daily large
  short-position report changes -> JP225 at 1-3 days.

## Pitfalls
- JPX deletes daily short-selling PDFs older than ~13 months; the restricted / unrestricted daily split is free only for
  the last year (HOLD). Monthly totals only from 2021.
- stock-marketdata.com chart pages hold plotly `bdata` (base64 float64) running to today: decode with the cut.
- karauri.net dates are calculation dates (`（…算出）`); `f=` filters by institution, not pagination; reports are
  disclosed with ~2-day lag (use T+2). nikkei225jp.com disallows `/_data/` in robots.txt.

## Directions that need the user
| direction | value |
|---|---|
| J-Quants API (paid plan) or QUICK / NEEDS: daily restricted-price short split 2008-24 | DEMO ~1-2 %, LIVE < 1 % |
| Unchanged and still the most valuable: IC single-stock CFDs on MT5 (heavyweights after earnings LIVE ~3-5 % / DEMO ~25 %; insider buys LIVE ~2-3 %) | see round 42 / 44 |

## State after round 45
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 46 opens next.
