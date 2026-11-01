# Round 47: dollar-weighted corporate buyback capacity from filed repurchases and true earnings dates, 2026-10-30

Brief: [round47_buyback_capacity/BRIEF.md](round47_buyback_capacity/BRIEF.md). Same LIVE / DEMO bars as rounds 25-46.
HOLD (2025-01..2026-09) stayed closed (3,860 XBRL facts filed after 2024-12-31 dropped at parse, latest kept 2024-12-20;
latest 8-K kept 2024-12-19; IC cut at load). HYPOTHESES_B.md: main grid 08:07:49 UTC, addendum A1 08:16:38 (before
returns), A2 08:17:37 (by-products, before their own numbers).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Built from the top-200 US issuers' XBRL repurchase run-rates and 8,700
8-K item 2.02 release times, the dollar-weighted open-window share is 94 % explained by the week of the quarter, so it
is round 23 P4's calendar proxy measured better, with the same answer: high-capacity days are no better than low ones
(US500 10:00-15:30 +0.8 vs +1.7 bp). Earnings-season days (weeks 2-7 of the quarter) are positive in both eras and in
the low-buyback US2000 control too, so that is a market-wide season effect, not a buyback bid; splitting the season by
capacity adds +0.7 to +5.8 bp in IS (t < 0.9) and the capacity slope flips sign from IS to VAL. LIVE was out from the
count (~145 HOLD trades need ~20 bp net).

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| B | Open-window buyback capacity (W14 / W0 conventions) -> US500 / USTEC / US30, US2000 control: F1 high capacity 10:00-15:30 or close-to-close 1-5 d, F2 reopening surges 1-3 d, F3 within-season split by capacity; by-products B1 (capacity vs trailing year), B2 (top-10 buyers open in season); 60 cells | **none**: best IS net t 1.47 (F3 USTEC c2c, VAL t 0.62) vs chance p95 2.37; best by-product B2 US500 IS t 1.66 (p95 2.03); calendar-matched random 56-86 %; primary F1 US500 net IS -0.7 (t -0.25) / VAL +1.3 | [STREAM_B.md](round47_buyback_capacity/STREAM_B.md), [HYPOTHESES_B.md](round47_buyback_capacity/HYPOTHESES_B.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Corporate buyback windows at the index level, measured firm by firm (XBRL repurchase dollars x true 8-K 2.02 dates):
  level, reopening surges, within-season split, 1-5 days.

## Pitfalls
- An 8-K item 2.02 is not always the earnings release (pre-announcements, e.g. AAPL 2019-01-02): require the release
  >= 10 days after the period end.
- XBRL cash-flow facts are year-to-date (TTM = FY + YTD - prior YTD); tags vary by firm and year (JPM 2011-17 used
  another tag); company-concept JSON includes 2025-26 restatements of old periods: drop by `filed` date.
- Vanguard 13F names are abbreviated; "BANCORP" normalises to empty in naive matching. A script named `signal.py`
  shadows the standard library.

## Directions that need the user
| direction | value |
|---|---|
| IC single-stock CFDs (MT5): trade the big buyers themselves, open window vs blackout | LIVE ~2-3 %, DEMO ~10 % |
| Paid sell-side buyback execution flows | LIVE < 1 %, DEMO ~2 % |

## State after round 47
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 48 opens next.
