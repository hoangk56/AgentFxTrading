# Round 11, stream F: multi-day drift after monetary-policy and macro surprises (1-5 days)

2026-10-06. The rules are in research/results/portfolio/round10_new_directions/HYPOTHESES_F.md. They were written
at 00:30 UTC, before any stream-F number; nothing was added post hoc. HOLD (2025+) was never loaded: the panel ends
2024-12-31, the Dukascopy files end 2015-12-31, and flib asserts both. Entry is at the first 20:50 UTC at least 90
min after the event, so round 10's intraday windows (B2, E2) are excluded. Exits are 1/3/5 weekdays later at 20:50,
capped at 5 x 24 h. Costs are the actual panel spreads at the entry and exit minutes, plus 0.6 bp on FX, plus swap
per rollover (swap_frac_at x rollovers, FX triple on Wednesday, indices on Friday). t is clustered by event date
(ISO-week clustering is also given in the outputs and changes nothing).

**Verdict: no family reaches DEMO or LIVE. There is no PREREG_DRAFT.** LIVE power is out of reach. F1 would need a
per-leg net Sharpe of 0.26 at ~75 legs a year; it shows 0.03 (IS) / 0.09 (VAL), and pooled over 2004-24 it shows
0.04-0.06 (power 0.5-0.6). DEMO is also out of reach: it needs an IS t of 2.0, and the best IS net t of any judged
cell is 0.64.

## Results (bp per leg)

| hypothesis (source, side) | where | n/yr | IS mid (t) / VAL mid (t) / PRE mid (t) | cost IS/VAL | net IS (t) / VAL (t) | x1.5 / +60 min IS, VAL | power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **F1 primary**: S30, all events, h5 (Eichenbaum-Evans delayed overshooting; continuation) | 8 CBs, home ccy vs USD (FOMC: EURUSD+USDJPY) | ~69 legs | +5.2 (1.11) / +11.8 (1.42) / +6.3 (1.60) | 2.2 / 1.6 | +3.0 (0.64) / +10.2 (1.22); PRE +4.1 (1.04) | +2.8, +10.0 / +1.5, +8.8 | 0.37 / 0.98 | 95 % / 96 % | fails (IS t) |
| F1, S30, h1 | same | ~69 | +2.4 (0.84) / +1.4 (0.27) / **+7.4 (3.04), 9/12 yrs** | 1.5 / 1.2 | +0.9 (0.32) / +0.2 (0.04); PRE +5.9 (2.41) | ~0 | 0.18 / 0.04 | 83 % / 87 % | real in 2004-15, gone since 2016 |
| F1, LARGE (\|S30\| >= 1.5x trailing median), h1-5 | same | ~22 | +0.4..+4.5 (<= 0.67) / -6.8..+10.6 / -1.3..+0.6 | 1.5-2.4 | <= +2.2 (0.32) IS | | <= 0.17 IS | 52-61 % IS | fails; the size filter removes the effect |
| F1, SDAY (whole decision-day move), h1-5 | same | ~69 | -0.0..+3.3 (<= 0.56) / -5.8..+7.4 / +0.6..+9.3 | 1.5-2.4 | -0.5..+0.9 IS | | <= 0.11 IS | 58-85 % | fails |
| F2 primary: S30, h5; hawkish -> short index (Neuhierl & Weber 2018) | FOMC->US500, ECB->DE40, BoE->UK100, BoJ->JP225, RBA->AUS200 | ~40 | +3.8 (0.36) / -24.7 (-1.01) | 9.6 / 8.3 | -5.8 (-0.55) / -33.0 (-1.34) | | -0.29 / -1.16 | 73 % / 1 % | fails |
| F2, FOMC only (descriptive) | US500 | 8 | +51.9 (1.83) / -22.9 (-0.37) | | +43.6 / -29.7 | | | | flips |
| F2 best cell: SDAY, h1 | same | ~41 | +6.9 (0.98) / +17.8 (1.90) | 5.3 / 3.4 | +1.6 (0.23) / +14.4 (1.53) | -0.4, +13.5 / -5.6, +16.2 | 0.12 / 1.06 | 95 % / 98 % | fails (IS t) |
| F3 primary: all releases, h5 (Evans & Lyons 2005; continuation of the first 5 min) | 15 non-US types + US NFP/CPI, home pair / EURUSD+USDJPY | ~175 | -0.3 (-0.10) / -2.2 (-0.53) | 2.2 / 2.1 | -2.4 (-0.87) / -4.4 (-1.04) | | <0 | 29 % / 8 % | fails |
| F3 LARGE (\|r0\| >= RMS of the last 12), h1-5 | same | ~45 (IS ~40, VAL ~67) | -5.4..-1.1 (h1 t -1.52) / +9.0..+10.7 (t 1.5-1.8) | 1.3-2.0 | IS < 0 / VAL +7.8..+8.8 (t 1.2-1.5) | | IS < 0 | 10-27 % / 63-83 % | sign flips IS -> VAL |
| F3 US only, h1 (2004-24 BLS dates) | EURUSD, USDJPY | 24 events | +0.2 / +12.7 (2.08) / PRE -3.5 (-1.25) | 1.3 | -1.1 / +11.5 (1.87); PRE -4.7 (-1.69) | | | | VAL-only (2022-24 CPI era) |
| F4 FOMC-cycle even weeks, long (Cieslak, Morse & Vissing-Jorgensen 2019) | US500 (US30 as robustness) | 8 per window | W0post -25.8 (-0.90) / -1.8; W2 +24.5 (1.17) / -3.4; W4 +4.0 / +35.9 (1.09); pooled W2+W4+W6 -4.8 / +20.0 | 7-13 incl. long swap | pooled -13.2 (-0.71) / +9.5 (0.37) | | <= 0.44 | pooled 13 % / 63 % | fails (the cycle has not repeated since 2016) |

LARGE needs prior history: 4 events for F1, 12 for F3. F2 and F4 have no PRE because there is no index data before
2016.

## Per family: best cell, cells tried, chance

| family | cells | best IS \|t_mid\| (cell) | sign-flip-per-date null: median / 95th pct of max \|t\| | max of K normals |
|---|---|---|---|---|
| F1 | 12 | 1.11 (S30 h5 ALL) | 1.64 / 2.75 | 1.96 |
| F2 | 12 | 0.98 | 1.70 / 2.75 | 1.96 |
| F3 | 6 | 1.52 (h1 LARGE, negative) | 1.33 / 2.50 | 1.65 |
| F4 | 5 | 1.47 (W6, n 5, negative) | 1.47 / 2.45 | ~1.6 |

Every family's best IS t is at or below the median of its null.

## What is real but too small, and other notes
- **Delayed overshooting at 1 day existed, then faded.** F1 S30 h1 is +7.4 bp at mid (t 3.04) in 2004-15, positive
  in 9/12 years, net +5.9 (t 2.41), and it survives x1.5 and +60 min. In 2016-24 it is +2.4 / +1.4 (t 0.84 / 0.27).
  Pooled over 2004-24: net +3.9 bp, t 2.14, per-leg Sharpe 0.056, power 0.64. The yearly net is +5..+15 bp in
  2004-09 and about 0 after 2015. This matches Kim, Moon & Velasco (2017): delayed overshooting is an old-regime
  phenomenon. It is not a candidate: IS fails, and the pooling was done after looking (descriptive only).
- **F1 at 3-5 days is positive in all three eras, but tiny next to its noise.** Mid is +6.3 / +5.2 / +11.8 bp (PRE /
  IS / VAL) against an sd of 90-117 bp. It beats 95-96 % of the random-day controls, because on random days the same
  rule loses about 4-5 bp net. Per-leg Sharpe is 0.03-0.09. In VAL, FOMC carries it: +60 bp per leg (t 2.97, 24
  events, the 2022-23 hiking cycle).
- **h5 = h3 in practice.** The <= 5 x 24 h cap makes the h5 exit equal to the h3 exit for 1,574 of 1,580 F1 legs:
  decisions fall on Tue-Thu, so 5 weekdays always span a weekend. "5 days" here means 3 trading days.
- **Index holds are expensive.** F2 / F4 costs are 7-13 bp per 3-5 day leg, mostly the long-index swap (~2 bp a
  night, Friday x3) and the 20:50 UTC UK100 / AUS200 spreads. FX legs cost 1.2-2.4 bp, so cost is not binding for F1
  or F3: the effect is.
- **The F3 LARGE sign flips** from IS (-5.4 bp at h1, t -1.5, 0/5 years positive) to VAL (+9.0, t 1.8). This is the
  same regime split stream E saw. US CPI in VAL goes against continuation (-20 bp, t -1.8); NFP is weakly positive
  in both eras (+11 / +5 bp, t 1.3 / 0.4).
- Positions: one bot per bank (F1/F2: at most 2 legs open per bot) or per pair (F3: the cap of 3 never bound).
  Across all bots, at most 6 positions are open at once in F1 and 8 in F3.
- C3 correlation, for the record, on the cells with net > 0 in IS and VAL (none is a candidate), IS+VAL by exit
  date: F1 S30 h5 daily -0.01 / monthly 0.11; F1 S30 h1 0.01 / 0.03; F2 SDAY h1 0.01 / 0.02.
- Data: BoJ decisions without a published time use a 02:00-06:30 UTC window, so their surprise is noisy (median
  \|S30\| 48 bp in VAL). The PRE H1 symbols (GBP, AUD, NZD, CAD) use a 30-90 min window. RBNZ's 20:00-21:00 UTC
  slot before 2019 sits at the rollover.
- The US CPI 2004-24 and NFP 2004-15 release dates come from BLS archive file names (cal/us_releases.json). The
  January 2004 NFP release is not in the BLS list.

## Files (scratchpad r10/F)
- flib.py (prices, clock, costs, stats)
- f12.py: F1/F2, giving out_f12.json and f12_legs.pkl; its control mode gives out_f12_control.json
- f12_split.py, f1_pooled.py: descriptive splits
- f3.py: gives out_f3.json and f3_legs.pkl; its control mode gives out_f3_control.json
- f4.py: gives out_f4.json, including its own control
- control_pct.py: gives out_control_pct.json
- c3corr.py
- cal/: build_us.py, us_releases.json, nyse_holidays.json
- logs: out_*.log
