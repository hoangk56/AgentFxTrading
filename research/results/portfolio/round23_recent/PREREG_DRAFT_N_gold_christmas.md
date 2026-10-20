# PREREG DRAFT (stream N, round 23): long gold around Christmas (N3b). DEMO numbers on IS, rare, not recommended alone

Draft written 2026-10-15 11:21 UTC. HOLD (2025-01 onwards) not opened; the lead decides whether to register. Rule
declared in [HYPOTHESES_N.md](HYPOTHESES_N.md) at 11:12 UTC (cell N3b) before any number; diagnostics after 11:18 UTC
are post hoc.

## Rule (exact, as declared)
- Symbol XAUUSD, long, fixed lot (no capital dependence).
- Festival date: 25 December. D-k / D+k = k-th NYSE trading day before / after 25 Dec (NYSE closures from
  `r23/shared/cal/cal_N.json`, python holidays 0.106, financial "NYSE").
- Entry: 16:00 New York on D-2 (fill on the next minute's quote). Exit: 16:00 New York on D+2, **capped at 5 x 24 h**
  (if D+2 16:00 is later than entry + 5 days, exit at 16:00 on the last NYSE trading day within the cap).
- One trade a year. Costs: actual spread at both fills, 0.6 bp commission, swap per rollover (x3 Wednesday).
- Source: Vojtko & Dujava 2025 (SSRN 5384405; Quantpedia 2025-08-05), "Global Holiday Drift": long GLD D-2 -> D+2
  around Christmas, Eid al-Fitr, Diwali and Lunar New Year; Christmas was the source's best festival in its 2005-2025
  sample. **The festival choice was therefore made by the source on years that include all of PRE, IS and VAL.**

## Numbers (net bp per trade; t is a plain t on one trade per year)
| era | n | mid (t) | cost | net (t) | x1.5 | +1 min | per-trade Sharpe | random entries beaten |
|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 (Dukascopy H1 bid, IC 2016-17 spread) | 12 | +106.1 (3.26) | ~1.7 + swap | +103.0 (3.17) | +102.5 | n/a | 0.92 | not run |
| IS 2016-21 | 6 | +85.6 (3.73) | 3.9 | +81.8 (3.61) | +81.3 | +80.5 | 1.48 | 93.2 % |
| VAL 2022-24 | 3 | +83.1 (2.51) | 7.3 | +75.8 (2.20) | +75.6 | +75.2 | 1.27 | 81.6 % |

By year (net): 2016 +85, 2017 +114, 2018 +83, 2019 +163, 2020 +4, 2021 +41, 2022 +110, 2023 +110, 2024 +7 (9/9 > 0);
PRE 9/12 > 0 (2010 -8, 2011 -73, 2015 -10). VAL/IS = 0.93.

## Bars
- DEMO: IS t >= 2.0 (3.61, yes), VAL net > 0 (yes), random entries >= 90 % (IS 93 %, **VAL 82 % on 3 trades: no**).
- LIVE: impossible (1 trade a year; power = Sharpe x sqrt(1.73 x 1) = 1.7-1.9 at the IS/VAL size).
- Multiple testing: one of 10 declared cells this stream. With 6 trades the t has 5 df: P(|t| >= 3.61) = 0.015, so
  ~0.14 for the best of 10 cells: within chance for the stream on IS alone; PRE adds an independent era for us
  (t 3.17 on 12, p 0.009) but not for the source.

## Expected holdout
- HOLD 2025-01..2026-09 contains **one** event (Christmas 2025: D-2 = 23 Dec, D+2 = 29 Dec is beyond the cap, so the
  exit is 26 Dec 16:00 New York). A single trade cannot give a t; the expected HOLD "t" on the VAL size is the per-trade
  Sharpe, ~1.3, and ~0.3 at round 18's retention for picks made with the data in view (0.25).
- Demo: 1 trade a year. Promotion rule "HOLD + demo pooled t >= 2.5" needs about (2.5 / 1.27)^2 ~ 4 trades at the VAL
  size (4+ years) and ~60 at a quarter of it. Stop rule if registered: drop after the first 3 demo trades if their
  summed net is below zero.

## Why it is not recommended on its own (post-hoc diagnostics, information only, `out/n3_diag.out`)
- **Not Christmas-specific; a turn-of-year seasonal.** Same rule around pseudo-dates (net, PRE / IS / VAL): 4 Dec
  -36 / +52 / -98; 11 Dec +7 / -24 / -63; 18 Dec -62 / +19 / +38; **25 Dec +103 / +82 / +76**; **1 Jan +112 / +113
  (t 2.33) / +39**; 8 Jan +51 / -75 / +116; 15 Jan +62 / +49 / -1. The gold rise runs from about 22 Dec into early
  January.
- **Partly the dollar.** Same Christmas window long EURUSD: PRE +36.5 (t 2.16), IS +10.8 (t 0.84), VAL +27.5 (t 4.13);
  XAGUSD IS +189 (t 5.7) / VAL +9; XPTUSD +89 / +87. Gift buying would be gold-specific; a year-end dollar fall moves
  all of them. Gold's extra over EURUSD is still ~+70 bp per event.
- Correlation with C3 (IS + VAL): daily -0.004, monthly +0.28 (C3 has no trade on the N3b exit days; the monthly figure
  is December C3 P&L, 9 points).
- The source picked Christmas after seeing 2005-2025; round 18 found such picks keep about a quarter of their size.

## Recommendation
Do not open HOLD for this rule alone (one event, no power). If the user wants it, run it on the demo account as a
once-a-year measurement next to the existing DEMO candidates, or test the broader turn-of-year gold/dollar window on
data after 2026-09-24 (a user decision; its side would now be post hoc).
