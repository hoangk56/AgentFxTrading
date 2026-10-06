# Round 22, stream R: triage of the residual ideas, and declared tests of the best four

Written 2026-10-06 05:31 UTC. Files: [TRIAGE_R.md](TRIAGE_R.md) (collection, drops, survivor table),
[HYPOTHESES_R.md](HYPOTHESES_R.md) (13 counted cells, declared 05:26 UTC before any return). HOLD was never loaded.

## Answer
**No candidate; no PREREG draft.** About 330 open lines from rounds 3-21 reduce to ~190 distinct ideas. ~70 need a user
decision, ~45 were already tested in a later round, ~55 are post hoc, ~20 are below cost with nothing new to try.
**Eleven survive, and none has a full-size power of 3**: the best two are ~1.3-1.5 at full size. Four were declared
and tested. All four fail: the two literature effects that had never been seen do not exist in IC's 2016-24 data, and
the two mechanism sides tested on the unseen 2004-15 era show no effect or the wrong sign.

## Triage summary (detail in TRIAGE_R.md)
| # | idea (source) | side from | events/yr | power full / decay-adj. | tested |
|---|---|---|---|---|---|
| R1 | equity premium in even FOMC-cycle weeks, Cieslak, Morse & Vissing-Jorgensen 2019 (r21 U) | paper | ~125 | ~1.3 / ~0.8 | yes |
| R2 | next-day FX reversal on abnormally low volume, Cespa et al. 2022 (r12 K) | paper | ~580 pair-days | ~1.5 / ~1.0 | yes |
| R3 | high-yielder bought into the Wednesday triple rollover (r3 W1) | mechanism | 52 | ~0.5 / ~0.1 | yes, PRE as the test era, information only |
| R4 | Treasury 10-year auction concession in USD, Lou, Yan & Zhang 2013 (r4) | mechanism | ~10 | ~0.5 / ~0.1 | yes, PRE as the test era, information only |
| R5-R11 | EURJPY quarter-end (all eras seen), W7b coupon dose (PRE opposite), reserve conditioning, VIX settlement / Wang & Zhao (no side), BoJ ETF (programme ended), GBPUSD midday (no mechanism) | | | < 0.5 or n/a | no |

## Results (net bp per trade; t clustered by date, R1 by FOMC-cycle week; costs at the actual minutes)
| cell | PRE 2004-15 | IS 2016-21 | VAL 2022-24 | x1.5 / +1 min (IS, VAL) | random control (IS / VAL) | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| A1 US500 long even-week days (primary) | n/a | mid +4.17 (1.17), net -0.55 (-0.15) | mid +3.67 (0.71), net +0.24 (0.05) | -1.48 / -1.07; -0.03 / -0.11 | 42 % / 62 % | -0.07 / 0.03 | no effect |
| A2 US30 even weeks | n/a | -1.72 (-0.44) | +0.64 (0.14) | similar | - | -0.20 / 0.10 | no |
| A3 USTEC even weeks | n/a | +2.93 (0.74) | +1.17 (0.17) | +2.07 / +1.98; +0.84 / +0.65 | - | 0.31 / 0.12 | no |
| A4 US500 even minus odd (per day) | n/a | -2.43 (-0.40) | +2.28 (0.28) | | | | no (US30 -4.84 / +3.90, USTEC -1.13 / +4.04) |
| A5 US500 odd weeks (placebo) | n/a | +1.88 (0.56) | -2.04 (-0.35) | | | | odd weeks earn as much as even weeks |
| B1 FX reversal, low orthogonal abnormal volume (primary) | mid +2.74 (2.32), net +1.37 (1.17) | mid -0.71 (-0.67), net -1.88 (-1.79) | mid -0.78 (-0.36), net -1.92 (-0.90) | -1.97 / -1.85; -1.99 / -1.94 | PRE 91 %, IS 80 %, VAL 26 % | -1.31 / -1.06 | present in PRE, gone since 2016 |
| B2 same, raw abnormal volume | +0.73 (0.63) | -2.30 (-2.16) | -1.41 (-0.69) | | | -1.62 / -0.80 | no |
| B3 all days (baseline) | -0.10 (-0.13) | -2.44 (-3.30) | -0.99 (-0.74) | | | | daily reversal does not pay its ~1.2 bp |
| B4 high orthogonal volume | -1.74 (-1.49) | -2.75 (-2.10) | -0.23 (-0.12) | | | | |
| B5 low minus high (the paper's interaction) | **+3.12 (2.07)** | +0.87 (0.53) | -1.69 (-0.60) | | | | PRE only |
| C1 high-yielder long 12:00-16:55 NY, Wednesdays | mid +0.75 (0.64), net -0.57 (-0.48) | mid -0.27, net -1.20 (-1.15) | mid +2.28, net +1.35 (0.83) | | PRE 31 %, IS 92 %, VAL 90 % | -0.89 / 0.99 | no |
| C2 same window Mon/Tue/Thu (placebo) | -0.36 (-0.57) | -0.84 (-2.09) | +0.02 (0.04) | | | | |
| C3 Wednesday minus other days | -0.21 (-0.16) | -0.36 (-0.32) | +1.32 (0.77) | | | | no Wednesday flow |
| D1 USDJPY long 3 days into the 10-year auction | **-26.79 (-2.46)**, random 0 % | +17.88 (1.61), random 94 % | +29.39 (1.77), random 61 % | unchanged by x1.5 / +1 min | | 0.86 / 1.34 | sign flips between PRE and 2016-24 |
| D2 USDJPY short after the auction to day +2 | +3.27 (0.40) | -5.51 (-0.66) | +10.51 (0.47) | | 84 / 19 / 84 % | | no |
| D3 EURUSD short into the auction | +2.02 (0.22) | +9.33 (1.25) | -3.07 (-0.25) | | 61 / 88 / 28 % | | no |
| D4 D1 + D3 | -12.38 (-1.58) | +13.61 (1.78) | +13.16 (1.03) | | 1 / 98 / 45 % | 1.09 / 0.95 | no |

Chance benchmark: max of 13 |N(0,1)| has median 1.94 and 95th percentile 2.89. The best counted |t| per era is
PRE 2.46 (D1, wrong sign), IS 2.16 (B2, wrong sign) and VAL 1.77 (D1). Nothing beats chance, and no cell is net
> 0 in both IS and VAL on its declared side with IS t >= 2. C3 correlation is not computed because nothing survived.

## What this says
- **R1 (even FOMC weeks):** in 2016-24 the US index CFDs earn as much in odd weeks as in even weeks (US500 even minus
  odd -2.4 bp/day IS, +2.3 VAL; per-year signs mixed). The pattern CMVJ document for 1994-2016 is not in IC's data
  after 2016 (their working paper appeared on SSRN in 2015).
- **R2 (low-volume reversal):** the paper's interaction is in 2004-15, with Dukascopy volume as the proxy: low minus
  high +3.1 bp, t 2.07; the low-volume reversal is +2.7 bp mid. That era overlaps the paper's own sample. From 2017,
  using IC tick counts, the reversal is gone at mid (-0.7 bp) and negative net. Unconditional daily FX reversal
  costs ~2.4 bp a trade in IS (t -3.3): continuation, not reversal. The volume proxy changes between eras (disclosed).
  A real proxy break cannot be ruled out, but IC tick counts track activity closely enough that a 2-3 bp
  interaction should still show.
- **R3 (Wednesday rollover):** the high-yielder does not rise into the Wednesday 17:00 New York rollover more than
  on other days in any era (difference -0.2 / -0.4 / +1.3 bp). Round 3's "+2.2 / +1.4" used 10 pairs and is not a
  Wednesday flow on these 5.
- **R4 (auction concession):** the dollar rose into 10-year auctions in 2016-24 (IS +17.9, VAL +29.4 bp over ~3 days,
  t ~1.7) but fell in 2004-15 (-26.8, t -2.46, with 2008-09 at -91 and -153). The yield-to-USD mapping is not stable
  (likely the safe-haven yen in the crisis years), so this is not a mechanism side. The VAL number is mostly the
  2022-24 USDJPY carry (random windows earn +24.8 bp, beats 61 %).
- **Across rounds 3-21, no open idea that is not gated by a user decision can reach LIVE power, even at full size.**
  The residual list is exhausted on existing data. The decisions that would change this are unchanged and listed
  below.

## Post-hoc observations (information only, not candidates)
- B1 by pair: no pair is positive in both IS and VAL (NZDUSD IS +2.15, t 0.81, VAL -0.21).
- C1 by pair: JPY crosses (GBPJPY, EURJPY) and USDJPY are positive in VAL on Wednesdays and on the other days alike. This is 2022-24 yen
  carry, not a Wednesday effect.

## Directions that need the user's decision (unchanged from rounds 16-21, reconfirmed by the triage)
- Data after 2026-09-24. This is the only clean holdout, and the only way to test the post-hoc leads (F15 USD on the
  15th, H3 FOMC US30 close, K4 BTC Deribit Fridays, the Friday ECB slot, US30 post-close fade).
- A cost structure without the 0.6 bp FX commission, or a low-cost venue. This is the only route by which the
  stable sub-cost effects (Sydney V, ECB slot, LBMA silver, SGE) reach LIVE power. Caveat: the 2024 dip.
- Dukascopy M1 2004-15 for GBPUSD, AUDUSD, NZDUSD, USDCAD, XAU, XAG and US index CFDs (unlocks PRE for N2a, T3
  US500 Monday reversal, quarterly-expiry Fridays, I12, LBMA silver).
- New IC symbols: EM / Scandinavian pairs with binding fixes (USDMXN Banxico, USDSGD MAS, USDHKD TMA), KOSPI LETF,
  softs, single-stock CFDs.
- Demos of E1 and the gold big-day rule. Paid data: Zheng dividends, Deribit OI, LETF AUM, SPX dividend payment dates.

## Scripts and outputs
In `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r22/R/`:
- `rlib.py`: generic evaluator built on round 13 M's grids and round 19 H's helpers (HOLD asserts). `r0_check.py`
  rebuilds E1 exactly as published, as a code check.
- `r1_fomc_cycle.py` -> `r1_out.txt`, `r1_out.pkl`. One code fix: the NYSE day list now starts 2015-05-01 so that
  every FOMC date is on it (the assert flagged 2015-06/07); the spec is unchanged.
- `r2_fx_volume.py` (rows) and `r2_analyse.py` -> `r2_out.txt`, `r2_rows.pkl`, `r2_res.pkl`.
- `r3_wed_roll.py` -> `r3_out.txt`. `r4_auctions.py` -> `r4_out.txt`. `chance.py` -> `chance_out.txt`.
- Calendars: `nyse_holidays.json` (python `holidays` NYSE), `ten_year_auctions.json` (fiscaldata.treasury.gov
  `auctions_query`, nominal 10-year notes incl. reopenings, 2003-2024, with the competitive close time).
