# Round 20, stream F: carry on central-bank decision days (Mueller, Tahbaz-Salehi & Vedolin 2017)

2026-10-06. Every rule is in [HYPOTHESES_F.md](HYPOTHESES_F.md). It was written at 04:03 UTC, before any return,
with two amendments (04:04 and 04:06 UTC), also before any return. The first number came at 04:07 UTC. Seven cells
were declared and seven were judged. Nothing was added post hoc except the information block marked as such. HOLD
(2025+) was never loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, FRED rates are cut at 2024-12-31, and
C3's trades are filtered to IS + VAL.

**Verdict: no cell meets LIVE or DEMO, so there is no PREREG_DRAFT.** The paper's FOMC effect does repeat. Long
foreign currencies against the US dollar from 16:00 ET on the day before the statement to 16:00 ET on the statement
day earns +14 to +32 bp net per event in PRE, IS and VAL, with no decay (VAL/IS 1.5). The problem is size against
noise: a per-event Sharpe of 0.2-0.5 at 8 events a year gives an IS net t of 1.51 (primary A1) to 1.90 (A4), below
DEMO's 2.0, and HOLD power of 0.8-1.8 against LIVE's 3. The "carry" part, long high-rate against short low-rate
currencies (A3), is absent after 2015. The pooled 8-bank extension and the BoJ cell fail in IS.

## The paper (read in full; JF 72(3) 1213-1252, doi 10.1111/jofi.12499)
- Sample 1994-2013, Olsen 5-minute mid quotes. Nine currencies against USD: AUD CAD CHF EUR GBP JPY NOK NZD SEK.
  There are 160 scheduled FOMC days; unscheduled meetings are excluded.
- Day: 4 pm ET to 4 pm ET. Portfolios are re-sorted at each month end on the forward discount (= the rate
  differential) into 3 x 3. Returns are equal-weight log excess returns against USD.
- Results on FOMC days:
  - pf1 (lowest rates): +5.19 bp (t 1.06).
  - **pf3 (highest rates): +14.47 bp (t 2.49), per-event Sharpe 0.197.**
  - dol (long all nine against USD): +10.77 bp (t 2.27).
  - Difference from other days: pf3 +12.74 (t 2.45), dol +10.30 (t 2.55).
  - Of pf3's excess, 9.5 bp comes before the statement and 3.2 bp after (Table IV).
- S2 keeps only currencies with a positive differential and reverses the position after a tightening (which needs a
  fed-funds-futures shock measure): +22.5 bp (t 4.17).
- Other central banks (1998-2013), with returns rebased to the announcing currency:
  - BoJ: pf3 +17.6 bp; long all currencies against JPY +14.7 bp (t 2.6).
  - RBA, BoE, RBNZ, SNB: no significant effect.
- Mechanism: the announcing country's rate is uncertain, intermediaries are short the low-rate currency, and they
  are paid a premium that grows with the rate differential.
- Sources: kellogg.northwestern.edu/faculty/alirezat/FXAnnouncements.pdf (the published version); Crossref record
  10.1111/jofi.12499. OpenAlex was rate-limited today, so Crossref and Semantic Scholar were used.

## Setup (details in HYPOTHESES_F.md)
- Universe: the 8 currencies IC quotes, through 7 USD pairs. NOK and SEK are not available.
- Price data:
  - PRE 2004-15: Dukascopy H1 bid.
  - IS 2016-21 and VAL 2022-24: the panel mid at the 16:00 ET minute.
- Window: from the last 16:00 ET at least 1 h before the decision to the first 16:00 ET at least 1 h after it. For
  FOMC this is exactly the paper's day.
- Ranks are causal: rates as of the end of the previous month.
  - 2016-24: the local FRED files, which cover 2014-2026 only: USD DFF, EUR ECBDFR, GBP SONIA, JPY / AUD / CAD
    monthly call rates, CHF / NZD 3-month interbank rates.
  - PRE: BIS daily policy rates (WS_CBPOL, fetched from stats.bis.org for 2003-01..2016-01; rates only, no prices).
    BIS has no JPY rate under QE, so JPY is filled with 0 % before 2006-03 and 0.05 % after 2013-04 (Amendment 2).
- Costs:
  - Spread: the actual half-spreads at both fill minutes, on netted USD-pair weights. PRE uses IC's 2016-17 median
    by New York minute (Amendment 1).
  - Commission: 0.6 bp per unit traded.
  - Swap: rates.py swap_frac_at per rollover crossed, Wednesday x3. PRE uses BIS rates with the rates.py markups.
- Units: everything is in the paper's units, bp per event per unit of the long side; A3 is pf3 - pf1.

## Results (bp per event; t clustered by exit date)

| cell (paper construct) | where | n PRE / IS / VAL | mid PRE / IS / VAL (t) | cost IS / VAL (+swap) | net IS (t) / VAL (t) | x1.5 IS / VAL | +1 min IS / VAL (PRE +1 h) | VAL/IS | yrs > 0 IS, VAL | placebo diff IS / VAL (t) | random IS / VAL | power IS / VAL size | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A1 primary**: pf3, long top-3-rate currencies vs USD, FOMC days | 7 USD pairs | 96 / 47 / 24 | +18.3 (1.92) / +15.9 (1.67) / +22.8 (1.77) | 1.1 / 1.0 (-0.3) | +14.4 (1.51) / +21.6 (1.67); PRE +17.3 (1.82) | +14.2 / +21.4 | +14.2 / +21.4 (PRE +15.5) | 1.49 | 5/6, 3/3 | +14.9 (1.57) / +25.9 (2.01) | 97.7 % / 99.2 % | 0.82 / 1.27 | fails DEMO (IS t 1.51 < 2.0) |
| A2: dol, long all 7 vs USD | same | 96 / 47 / 24 | +14.7 (1.90) / +13.2 (1.77) / +27.3 (2.32) | 1.0 / 0.9 (-0.5/-0.7) | +11.7 (1.57) / +25.8 (2.19) | +11.5 / +25.6 | +11.3 / +25.8 (PRE +11.3) | 2.20 | 4/6, 3/3 | +13.1 (1.76) / +32.3 (2.74) | 98.3 % / 100 % | 0.85 / 1.66 | fails DEMO (IS t 1.57) |
| A3: HML = pf3 - pf1 (the literal "carry") | same | 96 / 47 / 24 | +9.3 (1.61) / +6.2 (1.06) / -5.7 (-0.76) | 1.9 / 1.8 | +4.1 (0.69) / -7.2 (-0.97) | +3.7 / -7.5 | +4.3 / -7.5 | <0 | 3/6, 1/3 | +3.5 (0.60) / -10.0 (-1.34) | 72 % / 8 % | 0.37 / -0.74 | fails |
| A4: POS, long only currencies with r > r_USD (S2 without the switch) | same | 96 / 37 / 23 (10 + 1 days without a trade) | +17.7 (2.09) / +23.0 (2.02) / +32.9 (2.50) | 1.1 / 1.2 | +21.6 (1.90) / +31.6 (2.40); PRE +16.6 (1.97) | +21.4 / +31.3 | +21.4 / +31.2 (PRE +14.1) | 1.46 | 6/6, 3/3 | +19.8 (1.74) / +33.8 (2.55) | 98.9 % / 99.4 % | 1.14 / 1.82 | fails DEMO (IS t 1.90) |
| **B1 secondary**: pf3_X, top-3 r_j - r_X vs X, 7 non-US banks pooled | USD pairs, netted | 782 / 325 / 159 | +3.7 (1.34) / -2.2 (-0.61) / +15.3 (2.44) | 1.8 / 1.5 (-0.6/-0.2) | -4.7 (-1.27) / +13.7 (2.17); PRE +1.1 (0.39) | -5.0 / +13.5 | -4.6 / +13.8 (PRE -4.3) | <0 | 2/6, 2/3 | +0.4 (0.11) / +17.7 (2.81) | 55 % / 100 % | -0.69 / 1.71 | fails (IS < 0) |
| B2: B1 + FOMC (8 banks pooled) | same | 878 / 372 / 183 | +5.3 (1.97) / +0.0 (0.01) / +16.3 (2.86) | 1.7 / 1.4 | -2.2 (-0.65) / +14.7 (2.58) | -2.6 / +14.5 | -2.2 / +14.8 (PRE -2.1) | <0 | 3/6, 3/3 | +2.2 (0.65) / +18.8 (3.29) | 81 % / 100 % | -0.35 / 2.01 | fails (IS < 0) |
| B3: BoJ days, long all 7 vs JPY | same | 165 / 47 / 24 | +4.8 (0.73) / -16.0 (-1.56) / +33.6 (1.23) | 1.6 / 1.5 | -18.4 (-1.79) / +32.4 (1.18) | -18.6 / +32.2 | -18.4 / +32.5 | <0 | 1/6, 2/3 | -15.5 (-1.51) / +37.6 (1.37) | 1.5 % / 100 % | -0.97 / 0.90 | fails (IS < 0) |

Notes:
- Power = per-event net Sharpe x sqrt(expected HOLD events): FOMC 13.8; B1 92; B2 106. FOMC events are one per day,
  so day-clustered power is the same. The expected HOLD t on the VAL size is that column's VAL figure: A1 1.27, A2
  1.66, A4 1.82, B2 2.01.
- Placebo pool: 4 pm-to-4 pm days with no decision by any of the 8 banks, holidays excluded: PRE 1,997 / IS 1,049 /
  VAL 529 days. On these days the same rules earn -3 to +4 bp at mid, i.e. no unconditional drift.
- Random control: 1,000 seeds, each drawing a placebo day from the same era and weekday (and the same X for the B
  cells).
- 7 B1 / B2 events (6 for B3) of 2007-09 were dropped for missing Dukascopy H1 bars (6 BoJ, 1 RBNZ).

Net by year (bp):
- A1: 2016 +5.5, 2017 +37.2, 2018 -2.7, 2019 +9.3, 2020 +33.8, 2021 +5.8, 2022 +27.8, 2023 +25.5, 2024 +11.3.
  - PRE: 7/12 years > 0. 2008 +114 and 2009 +63; 2014 -45 and 2013 -23.
- A4: 6/6 IS years and 3/3 VAL years > 0. 2014 -39 is its worst year.

A1 split (descriptive, as in the paper's Table IV), from 16:00 ET to 5 min before the statement and from there to
16:00 ET:

| era | pre-statement | post-statement |
|---|---|---|
| IS | +11.6 bp (t 1.98) | +4.3 bp (t 0.55) |
| VAL | +17.2 bp (t 2.27) | +5.7 bp (t 0.50) |

The shape matches the paper: most of the return comes before the statement.

## Family summary and chance
| family | cells | best IS net t (cell) | chance |
|---|---|---|---|
| A FOMC | 4 | 1.90 (A4; mid t 2.02) | max of 4 normals ~1.6. Sign-flip-by-date null over all 7 cells (IS mid): median max \|t\| 1.47, 95th pct 2.56 |
| B pooled | 3 | -1.27 (B1); best positive VAL only | same null |

No IS t exceeds the 95th percentile of the null. A1, A2 and A4 all have net > 0 in PRE, IS and VAL, at x1.5 and at
+1 min, and they beat 97-100 % of random days in every era. What fails is the IS t, because there are only 47 events.

C3 correlation (IS + VAL, by exit date), for the cells with net > 0 in IS and VAL:

| cell | daily | monthly |
|---|---|---|
| A1 | -0.03 | -0.06 |
| A2 | -0.04 | -0.12 |
| A4 | -0.03 | -0.11 |

## Information only (computed after seeing the cells; not candidates)
- **Eras pooled, 2004-24:**
  - A1: +17.1 bp net, t 2.70, n 167.
  - A2: +14.8, t 2.84.
  - A4: +20.0, t 3.25, n 156. Winsorised at 5/95 %: +17.2, t 3.38. Dropping the top 3 events: +14.3.
- **Outside the paper's sample (2014-24):**
  - A1: +9.5 bp, t 1.29.
  - A2: +11.4, t 1.79.
  - A4: +16.9, t 2.13, n 76.
  - PRE 2004-13 overlaps the paper's own sample, so it replicates the construction; it is not an independent test.
- **Medians.** A1's median in IS / VAL is +17 / +31 bp, and 60 % / 75 % of events are > 0. The effect is therefore
  not three outliers, unlike PRE, where 2008 dominates (median +2).
- **What the number of events implies.** At A4's pooled per-event Sharpe (~0.26), a demo would need about
  (2 / 0.26)^2 ≈ 60 FOMC days, about 7.5 years, to reach t 2. HOLD (~14 days) would give an expected t of ~1.0-1.8.
  Even a true effect of this size cannot pass the LIVE bar on the FOMC alone.
- **What drives the result.** It is the dollar leg (A2 and A4 against USD), not the carry spread: A3 is ~0 or
  negative since 2015. Adding the other 7 banks dilutes it (B1 IS < 0); the 2023-24 VAL strength of B1 / B2 is a
  2-year episode (2016-21 had 1/6 positive years for BoJ). This agrees with the paper's own null for the RBA, BoE,
  RBNZ and SNB, and contradicts its BoJ result after 2015.

## Directions that need the user
- A FOMC-only dollar-short rule (A2 / A4 form) is a real, non-decaying effect: it is positive in 3 eras, at about
  15-30 bp against about 1 bp of cost. But at 8 events a year it cannot reach the DEMO t in IS, nor the LIVE power in
  any holdout. The only ways to use it:
  1. Accept a bar based on the pooled 2004-24 evidence, with the paper as prior. That is a change to the user's
     rules, not a candidate under them.
  2. Run it as a tiny always-on demo (8 trades a year) knowing it would take 7+ years to confirm.
  3. Add more currencies on FOMC days (NOK, SEK, MXN, ZAR... at IC). Under the paper's Prop. 2 the per-event Sharpe
     of dol rises with breadth, but that needs new price data, which is the user's decision.

## Scripts and outputs
Scratchpad r20/F/:
- flib.py: rates, prices, windows, baskets, costs, statistics.
- run.py: the 7 cells, placebo, random control, A1 split, sign-flip null. It writes out_run.json, out_run.txt,
  events.csv and run.log.
- info.py: per-year tables, C3 correlation and the post-hoc information. It writes out_info.txt.
- paper/: the downloaded PDF and its text.
- rates_pre/bis_cbpol_daily_2003_2016.csv: the BIS rates.
- The calendar is r12/shared/cal/cb_calendar.json.
