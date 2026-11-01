# Round 46: balanced-fund rebalancing and risk-parity de-leveraging with the bond leg, 2026-10-30

Brief: [round46_rebalancing_bond_leg/BRIEF.md](round46_rebalancing_bond_leg/BRIEF.md). Same LIVE / DEMO bars as rounds 25-45.
HOLD (2025-01..2026-09) stayed closed (Treasury requests stop at 2024, MoF / Bundesbank rows cut at parse, IC cut at
load, only row counts printed). HYPOTHESES_P.md finished 07:54:22 UTC, first grading 07:57:41; one dated addendum
(07:59, no cell changed).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Building the Harvey-Mazzoleni-Melone (NBER w33554, 2025) 60/40 threshold
signal with the 10-year Treasury leg does not rescue round 23 P2: the bond leg changes the signal (corr 0.83 with the
equity-only proxy) but adds +0.4 / -0.4 bp to the stock-minus-bond return. The paper's slope is in our data
(IS equity slope -20 bp per sd, t -2.57; paper -15.9; the equity leg carries 95 % IS / 72 % VAL of it), but it comes
from turmoil days only: a sign rule earns nothing, and a signal-sized position is IS +3.7 bp (t 0.74), -4.3 without
2020-03/04. LIVE was out from the count (needs ~16-17 bp net a day; the paper's full size is ~13 bp mid).

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| P | F1 60/40 threshold / month-end / paper-regression rebalancing pressure (US500 + UST 10y) -> US500, USTEC, US30; F2 2-asset risk-parity leverage cuts (20 / 60 days) 1-3 days; F3 same for JP225 + JGB 10y and DE40 + Bund 10y, US signal into the next Asian / European session; USDJPY / EURUSD controls; 17 declared cells | **none**: primary F1-thr-all-full net IS -2.1 bp (t -0.68) / VAL +6.1 (t 1.35, all 2022); best IS net t +0.27; best IS mid \|t\| 1.19 vs family null median 1.48; 3-5 positive years of 9 (2020, 2022); F2 repeats round 23 P1 (56-68 % same trigger days); F3 negative in IS and VAL | [STREAM_P.md](round46_rebalancing_bond_leg/STREAM_P.md), [HYPOTHESES_P.md](round46_rebalancing_bond_leg/HYPOTHESES_P.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Balanced-fund (60/40) threshold / calendar rebalancing pressure with the bond leg, US / Japan / Germany, at 1 day;
  2-asset risk-parity leverage cuts at 1-3 days.

## Pitfalls
- IC is closed at 20:00 NY on Fridays: entries timed after the Treasury curve (18:00 ET) lose ~20 % of days.
- MoF `jgbcme_all.csv` is Shift-JIS with a title row; Bundesbank daily series run every calendar day with "." gaps up
  to today; Treasury yearly CSVs are newest-first and 2004-05 lack the 30-year column.
- data-api.ecb.europa.eu disallows ClaudeBot / Claude-Web / anthropic-ai in robots.txt: off limits. cdn.cboe.com
  robots.txt answers 403 (not used).
- A significant linear slope can give zero P&L for a sign rule when a few turmoil days carry it: report the placeable
  trade, with and without 2020-03/04.

## Directions that need the user
| direction | value |
|---|---|
| A bond futures / CFD venue for the stock-minus-bond spread | LIVE < 1 %, DEMO ~1 % |
| Paid ES1 / TY1 history 1997-2015 for a PRE check | LIVE < 1 %, DEMO ~2 % |

## State after round 46
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 47 opens next.
