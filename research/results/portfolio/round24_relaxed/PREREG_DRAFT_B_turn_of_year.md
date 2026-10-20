# PREREG DRAFT B (round 24): gold long + USD short over the second half of December (turn of the year)

Drafted 2026-10-15 14:07 UTC by stream B. **Not registered; HOLD not opened.** The lead decides. **Tier reached: DEMO
numbers on IS / VAL only. RELAXED fails (VAL t 0.04 < 1.0; check-size power 0.03 < 1.5). LIVE fails. Not
recommended** (see "Why not").

## Rule (declared in HYPOTHESES_B.md at 12:01 UTC, before any number; window and sides from the sources)
- Once a year. Entry: market, 15:00:00 UTC on the first weekday on or after 15 December. Exit: market, 15:00:00 UTC on
  the last weekday of December that is not 25 December (10-12 weekdays). No stop. Fixed equal notional per leg.
- Legs (B4, primary): long EURUSD, GBPUSD, AUDUSD, NZDUSD, XAUUSD; short USDJPY, USDCAD, USDCHF (8 legs, at most 3 per
  bot means 3 bots). Variant B2: XAUUSD long only.
- Quotes: close of the last M1 bar ending at or before the time, at most 10 minutes stale (else no trade). Costs: half
  spread in + half out + 0.6 bp per leg + swap per 17:00 NY rollover (x3 Wednesday), FRED rates + IC fitted markups.
- Sources: Seasonax "Forex Seasonality: The US Dollar Drop at The End of The Year" and FOREX.com (Dec 2024) for the
  dollar's second-half-of-December fall; Gulseven (2016, arXiv 2003.11027) and World Gold Council (2023) for gold's
  December-February / January strength. Practitioner sources; no peer-reviewed FX paper was found.

## Evidence (net bp per trade = mean of legs; t over years; scripts in scratchpad r24/B)
| cell | PRE 2004-15 | IS 2016-21 | VAL 2022-24 | IS+VAL | 2004-24 |
|---|---|---|---|---|---|
| B4 basket | +26.8 (t 0.69), 6/12 years > 0, random 72.5 % | **+99.8 (t 4.08)**, 6/6, random 100 % | +3.7 (t 0.04), 2/3, random 59.5 % | +67.8 (t 1.97), random 99.5 % | +44.4 (t 1.69), 14/21 |
| B2 gold only | +34.3 (t 0.47), 5/12 | **+275.8 (t 15.8)**, 6/6 | +38.7 (t 0.35), 2/3, random 53.5 % | +196.8 (t 3.78) | +103.9 (t 2.11) |

Spread x1.5 and +1 minute change nothing (B4 IS +99.6 / +100.2, VAL +3.6 / +1.5). Swap costs B4 -2.9 / -7.5 / -12.5 bp
per trade (PRE / IS / VAL). Correlation with C3 on IS + VAL (trade P&L put on the entry day): daily +0.015, monthly
+0.012 (B2: +0.018 / +0.128).

## Bars
- DEMO (IS t >= 2.0, VAL net > 0, x1.5 / +1 min > 0, random >= 90 %): met on IS t and VAL sign; random 100 % IS,
  99.5 % IS + VAL pooled, 59.5 % on VAL alone (3 trades).
- RELAXED: design net t 4.08 >= 1.5 (met); check-era net > 0 (met) but t 0.04 < 1.0 (fails); check-size power 0.03
  (fails, needs 1.5).
- LIVE: power 2.19 at the IS Sharpe with 1 trade a year, 0.03 at the VAL Sharpe.

## Why not (stream B's view)
- The 12 PRE years, which nobody had seen for this rule, give +26.8 bp at t 0.69 with 6/12 years > 0; 2012-15 all
  lost. The IS strength (6/6 years, gold +276 bp) is a 2016-2023 run, and 2024 lost -168 bp.
- Expected HOLD t: HOLD 2025-01..2026-09 holds one event (December 2025). At the VAL Sharpe 0.024 its expected t is
  0.02; at the 2004-24 Sharpe 0.37 it is 0.37; at the IS Sharpe (1.67) it would be 1.7, which round 18's retention for
  post-hoc-adjacent picks does not support. A once-a-year demo would need ~25-60 years for t 2 at the 2004-24 Sharpe.
- It overlaps round 23's N3b (gold around Christmas) and explains it: the turn-of-year window, not the festival.

## If registered anyway (DEMO)
- Demo trades: 1 basket (8 legs) a year. Stop rule: stop after any 3 consecutive losing years or when the pooled
  HOLD + demo net mean is < 0 after 5 years. Promotion: HOLD + demo pooled t >= 2.5 (not reachable within a decade).
