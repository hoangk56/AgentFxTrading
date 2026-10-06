# Round 20, stream G: European and Hong Kong index expiry settlements

2026-10-06. The settlement rules, the calendar, the sides from the literature and all 64 counted cells were
declared at 04:06 UTC, before any return was computed: [HYPOTHESES_G.md](HYPOTHESES_G.md). Three post-hoc
diagnostics were added at 04:10 UTC, after the counted cells and before their own numbers. They are information
only.

HOLD was never loaded:
- the panel ends 2024-12-31;
- the STOXX50 and F40 bid caches are cut at ts < 1735689600000 at load;
- the day loops stop at 2024-12-31, with an assert.

There is no PRE era, because there is no index minute data before 2016.

## Answer
- **LIVE: none. DEMO: none. No PREREG draft.**
- **The literature's sides mostly do not show up:**
  - No rise into the European settlements. Pooled over the four European indices (EU4), the into-settlement mid is
    +0.8 / -2.7 bp on quarterly (Q) days and -0.7 / +4.9 bp on monthly (M) days.
  - No consistent reversal after them. The fade-the-move rule G2 goes the wrong way on Q days (EU4, 60 min after:
    -2.6 / -9.2 bp, t -0.8 / -2.9).
  - HK50 does not fall on the HSI averaging day in IS (Q -6.5, M +8.1 bp).
- **What does show up is a fall on quarterly expiry Fridays**, the side Stoll & Whaley (1987) report.
  - Four cells meet the DEMO numbers on IS/VAL. All four go short after the settlement on Q days:

    | cell | net IS (t) | net VAL |
    |---|---|---|
    | UK100 to the close | +28.1 (2.32) | +28.0 |
    | STOXX50 to the close | +28.8 (2.16) | +12.1 |
    | EU4 to the close | +22.9 (2.15) | +13.3 |
    | DE40, 60 min | +8.6 (2.09) | +8.0 |

  - **All four fail the random-entry control:**

    | cell | beats random IS | beats random VAL |
    |---|---|---|
    | UK100 to the close | 100 % | 9 % |
    | STOXX50 to the close | 95 % | 31 % |
    | EU4 to the close | 100 % | 16 % |
    | DE40, 60 min | 88 % | 77 % |

  - The reason: in VAL, Q days fell at every hour, so a short at random times on the same days earned as much or
    more (EU4 random mean +18 bp against +13 actual). The timing after the settlement adds nothing in VAL.
  - The family's best IS net t (2.32) is inside chance: the shared sign-flip null gives p95 2.89, p = 0.19.
  - Even taken at face value, the expected HOLD t at the VAL size is 0.6-0.9 (7 quarterly days in HOLD).

## Settlement rules and calendar (from the exchanges)
| index (IC symbol) | rule 2016-24 | minutes used (local) | source |
|---|---|---|---|
| DAX (DE40) | Xetra intraday auction from 13:00 CET; the expiring future stops at 13:00; on Eurex settlement days the DAX-stock auction lasts 5 min instead of 2, random end | 13:00-13:05:30, E = bar ending 13:06 | Eurex DAX Futures / ODAX specifications; Xetra auction schedule |
| FTSE 100 (UK100) | EDSP intraday auction from 10:10:00, lasting 5-5.5 min (extensions to 10:29 at most); kept at 10:10 by LSE notice N14/15 (2015) | E = bar ending 10:16 London | ICE FTSE 100 futures and options note; LSE Market Notice N14/15 |
| EURO STOXX 50 (STOXX50) | average of index values 11:50-12:00 CET | E = 12:00 | Eurex FESX / OESX specifications |
| CAC 40 (F40) | arithmetic mean of index values 15:40-16:00 CET (the brief's guess is right) | E = 16:00 | Euronext FCE specification |
| HSI (HK50) | average of 5-minute quotes on the Last Trading Day (from 5 min after the open to 5 min before the end of the continuous session, plus the close); the Last Trading Day is the business day before the month's last business day | 09:31-16:00 HKT | HKFE Rules, HSI futures and options specifications; HKEX product page |

Calendar (code: `libg.py`, output `expiry_calendar.json`):
- Europe: 108 expiries 2016-24, 36 of them quarterly. Two expiries moved to the Thursday because of Good Friday:
  **2019-04-18 and 2022-04-14**.
- HK: 108 expiries.
- The declared Q-day artefact rule (a 1-minute move above 50 bp at E) dropped one day: **UK100 2020-03-20**
  (-50.7 bp at 10:16 London). That was a real crash-period auction move, not a contract switch. The rule was
  declared, so the day stays out.
- No settlement rule changed during 2016-24.
- The DAX rule moved from the opening price (used to 1998) to the 13:00 auction before 2016. The exact switch date
  was not found, and nothing here depends on it.

## Sides declared from the literature
| source | finding | rule here |
|---|---|---|
| Joensuu 2010 (Aalto MSc; EURO STOXX 50, 2000-09) | returns before expiration higher, after it lower on expiration days | G1: long into, short after |
| Baltussen, Terstegge & Whelan 2024 (WP, "The Derivative Payoff Bias") | US: up into the a.m. settlement, reversal after (+18.5 bp); dealer charm or manipulation in an illiquid pre-settlement window; no effect at the p.m. settlement | G1's mechanism |
| Stoll & Whaley 1987, 1991, 1997 | effects follow the settlement time; reversal afterwards; the market tends to fall on quarterly expiries | G2: fade the into-move |
| brief ("in the direction of the morning move") | no paper found states it | G3: follow the morning move (weakest prior) |
| Chow, Yung & Zhang 2003; Fung & Yung 2009 (HSI average settlement) | negative price effect on the expiry day, no reversal | H1: short the day; H2: the no-reversal control |
| Schlag 1996 (DAX); Alkebäck & Hagelin 2004; Illueca & Lafuente 2006; Xu 2014; Batrinca et al. 2020 | volume and volatility effects; price effects weak under averaging | context |

## Results by family
- Units: bp per trade, t clustered by UTC day.
- EU4 = equal-weight mean of DE40, UK100, STOXX50 and F40 on each expiry day.
- Costs: actual spreads at the minutes for DE40, UK100 and HK50; IC's published spreads for STOXX50 (1.5 pt) and
  F40 (1.79 pt).
- Power = per-trade net Sharpe x sqrt(1.73 x trades a year). The VAL column is the expected HOLD t.
- There is no PRE column, because there is no data before 2016.

| hypothesis (source) | where | IS mid (t) / VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| G1-in: long into the settlement (Joensuu; Baltussen et al.) | EU4 Q | +0.8 (0.25) / -2.7 (-0.76) | 2.6 / 1.9 | -1.9 (-0.62) / -4.6 | <0 | <0 | fails; DE40 Q mid -9.9 (t -1.61), UK100 Q VAL -17.4 (t -2.52) |
| same | EU4 M | -0.7 (-0.31) / +4.9 (2.29) | 2.6 / 1.9 | -3.3 (-1.39) / +3.0 (1.41) | <0 | <0 / 1.07 | fails (IS) |
| G1-out60: short 60 min after (same) | EU4 Q | +7.4 (2.16) / +4.9 (0.95) | 2.6 / 1.9 | +4.8 (1.42) / +3.0 (0.59) | 0.62 | 0.76 / 0.44 | fails the IS t |
| same | DE40 Q | +9.5 (2.27) / +8.3 (0.91) | 0.9 / 0.3 | **+8.6 (2.09) / +8.0 (0.88)**, x1.5 +8.1 / +7.9, +1 min +8.9 / +8.1 | 0.94 | 1.12 / 0.67 | DEMO numbers; **fails the random control (88 % / 77 %)** |
| same | EU4 M | +1.4 (0.69) / +3.9 (1.84) | 2.6 / 1.9 | -1.2 / +1.9 | <0 | <0 | fails; STOXX50 M +3.4 (0.81) / +3.1 beats random 97 / 96 % but IS t 0.8 |
| G1-outC: short after, to the cash close | EU4 Q | +25.5 (2.38) / +15.3 (0.89) | 2.6 / 1.9 | **+22.9 (2.15) / +13.3 (0.77)**, x1.5 +21.6 / +12.4, +1 min +19.5 / +11.2 | 0.58 | 1.15 / 0.59 | DEMO numbers; **fails the random control (100 % / 16 %)** |
| same | UK100 Q | +29.7 (2.45) / +29.3 (1.29) | 1.6 / 1.3 | **+28.1 (2.32) / +28.0 (1.24)**, 7/9 years | 1.00 | 1.25 / 0.94 | DEMO numbers; **fails random (100 % / 9 %)** |
| same | STOXX50 Q | +33.3 (2.49) / +15.6 (0.67) | 4.4 / 3.5 | **+28.8 (2.16) / +12.1 (0.51)** | 0.42 | 1.16 / 0.39 | DEMO numbers; **fails random (95 % / 31 %)**; ex 2020-03-20 IS t 1.85 |
| same | EU4 M | -2.4 (-0.46) / +0.3 | 2.6 / 1.9 | -4.9 / -1.6 | <0 | <0 | fails |
| G2-out60: fade the into-move, 60 min (Stoll & Whaley) | EU4 Q | -2.6 (-0.76) / -9.2 (-2.87) | 2.5 / 1.9 | -5.2 / -11.2 (-3.45) | <0 | <0 | wrong sign: on Q days the move continues |
| same | EU4 M | +2.1 (1.15) / +4.5 (2.26) | 2.6 / 1.9 | -0.5 / +2.6 (1.31) | <0 | <0 / 1.0 | real at mid on M days in VAL only; below cost |
| G2-outC: fade to the close | EU4 Q / M | -4.2 / +3.4; +4.0 (0.96) / +6.6 (1.68) | 2.6 / 1.9 | -6.8 / +1.4; +1.5 (0.35) / +4.8 (1.20) | 3.25 (M) | 0.19 / 0.91 (M) | fails the IS t; DE40 Q +8.2 (0.69) / +21.2 beats random 91 / 98 % but IS t 0.7 |
| G3-in: follow the morning move into the settlement (brief) | EU4 Q / M | +1.6 / +2.8; -0.2 / -1.3 | 2.6 / 1.9 | -1.0 / +0.8; -2.8 / -3.2 | <0 | <0 | fails; best is UK100 Q +5.6 (0.82) / +8.9 |
| H1: short HK50 on the HSI averaging day (Chow et al.) | HK50 Q / M | -6.5 (-0.29) / +76.6 (2.13); +8.1 (0.71) / +27.7 (0.87) | 3.4 / 2.7 | -9.9 / +74.0; +4.9 (0.43) / +25.0 (0.78) | <0 / 5.1 | <0; 0.23 / 0.59 | fails the IS t; VAL is the 2022-24 HK bear market |
| H2: fade the expiry-day move next morning (control: the literature says no reversal) | HK50 Q / M | -9.7 / +53.2 (2.29); +4.8 / -1.6 | 3.4 / 2.7 | -13.1 / +50.5; +1.6 / -4.4 | <0 | <0 | as predicted, no reversal in IS |

Every cell with x1.5, +1 min, the non-expiry-Friday placebo and the random control is in
[the full table](#all-64-counted-cells) below.

### Best cell per family, cells tried, chance
| family | cells | best IS net t (cell) | VAL net of that cell |
|---|---|---|---|
| G1-in | 10 | +0.82 (STOXX50 Q) | -3.7 |
| G1-out60 | 10 | +2.09 (DE40 Q) | +8.0 (fails random) |
| G1-outC | 10 | +2.32 (UK100 Q) | +28.0 (fails random) |
| G2-out60 | 10 | +0.80 (DE40 Q) | -5.9 |
| G2-outC | 10 | +1.01 (F40 M) | -3.3 |
| G3-in | 10 | +1.25 (DE40 Q) | -4.0 |
| H1 / H2 | 4 | +0.43 (H1 M) | +25.0 |

- **Shared null.** The per-UTC-date sign flip is applied to all 64 cells at once, 2,000 draws (`perm_out.txt`).

  | statistic | era | observed | null median | null p95 | p |
  |---|---|---|---|---|---|
  | max \|mid t\| | IS | 2.49 | 2.54 | 3.52 | 0.55 |
  | max net t | IS | 2.32 | 1.85 | 2.89 | 0.19 |
  | max net t | VAL | 2.15 | 2.17 | 3.39 | 0.52 |

  For comparison, the max of 64 independent normals has a one-sided p95 of 3.16.
- **The count of cells with IS net t >= 2.**
  - Observed 4, against a null median of 0 and p95 of 2 (p 0.02).
  - The four are one effect: the same quarterly days, on the same side.
  - In VAL the count is 2 against a null p95 of 3.
- **C3 correlation** for the 15 cells that are net > 0 in both eras (IS+VAL):
  - daily -0.013..+0.073;
  - monthly -0.101..+0.114;
  - G1-outC Q cells: daily -0.012..+0.011.

## What the quarterly-day effect is (post hoc, information only)
The diagnostics are in `posthoc_out.txt` and were declared at 04:10 UTC.
- **P1: a few days carry the sign, and the effect sits in 2020-23.**
  - EU4 to the close, Q days, by year: 2016 +21, 2017 -6, 2018 -14, 2019 +2, 2020 +75, 2021 +60, 2022 +13,
    2023 +38, 2024 -11.
  - The top days are 2020-03-20 (+163), 2021-06-18 (+124), 2021-09-17 (+114) and 2023-03-17 (+106).
  - Without 2020-03-20, EU4's IS net t falls from 2.15 to 1.84, and STOXX50's from 2.16 to 1.85. UK100 had already
    lost that day to the declared rule.
- **P2: the fall happens before the US open, not after it.**
  - Shorting from just after the settlement to the US cash open (EU4, Q days): +15.1 (t 1.94) IS, +21.9 (t 1.81) VAL.
  - From the US open to the European close: +13.1 IS, -5.6 VAL.
  - So it is not the US third-Friday reversal of Baltussen et al. passing into Europe.
  - On M days the European indices rise after the US open (-11.7 bp for the short, t -2.9 IS; -5.5 VAL).
- **P3: the whole session falls on quarterly expiry Fridays.**
  - Shorting the cash session (open+5 to the close), EU4: Q days +26.8 (t 1.45) IS, +33.9 (t 1.60) VAL.
  - On M days: +2.0 / -17.2. On placebo Fridays: -6.1 / -8.9.
  - UK100 Q in VAL is +51.8 (t 2.80).
  - By year it is ~0 in 2016-19 and +30..+105 in 2020-23.
  - This matches Stoll & Whaley's "the market tends to fall" on quarterly expiries. It is a day-level effect, not a
    settlement-auction flow.
  - It would be worth one declared test on data the search has not used (index M1 before 2016, or after
    2026-09-24). From IS/VAL it cannot be registered: it was found after looking, and it is concentrated in four
    years.

## What this says
- The European settlement auctions and averaging windows do not create a tradable price pressure at IC's costs.
  - The intraday averages (STOXX50, F40, HSI) show nothing on the predicted sides. This is what the averaging
    design is meant to do (Kumar & Seppi 1992; Alkebäck & Hagelin 2004).
  - The single-auction settlements (DE40 13:00, UK100 10:10) show no rise into the auction.
- The one effect beyond chance in count is a fall over quarterly expiry Fridays. It sits at the day level, not at
  the settlement minutes.
  - It is ~0 in 2016-19.
  - At 4 days a year, its HOLD t at the VAL size is below 1 for any cell.
  - Even as DEMO, a demo would need decades to reach t 2.
- This adds Europe and Hong Kong to round 10 A5 (Nikkei SQ) and round 11 H2 (US SOQ): expiry settlement windows are
  not a source of candidates on these symbols.

## Directions that need the user
- **Quarterly-expiry-Friday weakness (P3), a test that could be declared.** It needs either European index M1
  before 2016 (a new price fetch, the user's call) or the data after 2026-09-24. It would be too rare for LIVE in
  any case: 4 trades a year.
- **Nothing else.** IC's futures-based CFDs follow the settlement auctions only through the futures; auction prints
  themselves would need exchange data.

## Limitations
- The STOXX50 and F40 costs are IC's published averages, not spreads at 12:00 / 16:00 CET.
- HK typhoon and black-rain closures are not in the calendar.
- The IC CFDs follow the next futures contract on expiry day, so the cash auction is seen only through it.
- The declared artefact rule removed a real UK100 day (2020-03-20). Keeping the day would raise UK100's quarterly
  IS. It would not change any verdict: the random control fails in VAL.

## All 64 counted cells
Columns:
- "random" is the share of 500 random-entry seeds beaten, and was run only for cells net > 0 in both eras.
- "exp - placebo t" is the Welch t of the expiry mid against the same rule on non-expiry Fridays (non-expiry days
  for HK50).
| cell | n IS/VAL | mid IS (t) | mid VAL (t) | cost IS/VAL | net IS (t) | net VAL (t) | x1.5 IS/VAL | +1 min IS/VAL | exp - placebo t IS/VAL | random IS/VAL % | power IS/VAL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DE40 G1-in Q | 24/12 | -9.9 (-1.61) | +2.5 (+0.27) | 0.9/0.3 | -10.8 (-1.76) | +2.2 (+0.23) | -11.2/+2.1 | -8.1/+3.0 | -2.07/+0.30 | -/- | -0.95/+0.18 |
| UK100 G1-in Q | 23/12 | +2.7 (+0.40) | -17.4 (-2.52) | 1.6/1.3 | +1.1 (+0.17) | -18.6 (-2.71) | +0.3/-19.3 | +1.7/-19.3 | +0.29/-2.25 | -/- | +0.09/-2.06 |
| STOXX50 G1-in Q | 24/12 | +10.6 (+1.40) | -0.1 (-0.02) | 4.4/3.5 | +6.2 (+0.82) | -3.7 (-0.44) | +4.0/-5.4 | +2.1/-5.4 | +1.26/-0.27 | -/- | +0.44/-0.33 |
| F40 G1-in Q | 24/12 | -1.3 (-0.19) | +4.1 (+0.41) | 3.4/2.6 | -4.8 (-0.69) | +1.6 (+0.16) | -6.5/+0.3 | -4.7/+3.8 | +0.04/+0.47 | -/- | -0.37/+0.12 |
| EU4 G1-in Q | 24/12 | +0.7 (+0.25) | -2.7 (-0.76) | 2.6/1.9 | -1.9 (-0.62) | -4.6 (-1.30) | -3.2/-5.6 | -2.2/-4.5 | -0.03/-0.70 | -/- | -0.33/-0.99 |
| DE40 G1-out60 Q | 24/12 | +9.5 (+2.27) | +8.3 (+0.91) | 0.9/0.3 | +8.6 (+2.09) | +8.0 (+0.88) | +8.1/+7.9 | +8.9/+8.1 | +2.00/+1.30 | 88/77 | +1.12/+0.67 |
| UK100 G1-out60 Q | 23/12 | +0.9 (+0.18) | +8.1 (+1.12) | 1.5/1.3 | -0.6 (-0.13) | +6.8 (+0.94) | -1.4/+6.2 | -1.0/+5.5 | +0.57/+0.83 | -/- | -0.07/+0.72 |
| STOXX50 G1-out60 Q | 24/12 | +9.5 (+1.70) | +2.9 (+0.36) | 4.4/3.5 | +5.1 (+0.92) | -0.7 (-0.08) | +2.9/-2.4 | +4.0/-1.3 | +1.82/+0.32 | -/- | +0.49/-0.06 |
| F40 G1-out60 Q | 24/12 | +7.8 (+1.82) | +0.5 (+0.04) | 3.4/2.6 | +4.3 (+1.01) | -2.1 (-0.20) | +2.6/-3.4 | +1.8/-3.3 | +0.66/+0.20 | -/- | +0.54/-0.15 |
| EU4 G1-out60 Q | 24/12 | +7.4 (+2.16) | +4.9 (+0.95) | 2.6/1.9 | +4.8 (+1.42) | +3.0 (+0.59) | +3.5/+2.1 | +3.8/+2.3 | +1.96/+1.08 | 93/68 | +0.76/+0.44 |
| DE40 G1-outC Q | 24/12 | +21.7 (+1.91) | +14.5 (+0.69) | 0.9/0.3 | +20.8 (+1.84) | +14.2 (+0.67) | +20.3/+14.0 | +18.8/+11.9 | +1.47/+0.96 | 71/49 | +0.99/+0.51 |
| UK100 G1-outC Q | 23/12 | +29.7 (+2.45) | +29.3 (+1.29) | 1.6/1.3 | +28.1 (+2.32) | +28.0 (+1.24) | +27.3/+27.3 | +23.4/+27.0 | +2.42/+1.41 | 100/9 | +1.25/+0.94 |
| STOXX50 G1-outC Q | 24/12 | +33.3 (+2.49) | +15.6 (+0.67) | 4.4/3.5 | +28.8 (+2.16) | +12.1 (+0.51) | +26.6/+10.3 | +25.8/+8.2 | +2.21/+0.81 | 95/31 | +1.16/+0.39 |
| F40 G1-outC Q | 24/12 | +11.8 (+1.46) | +1.6 (+0.15) | 3.4/2.6 | +8.4 (+1.04) | -0.9 (-0.09) | +6.7/-2.2 | +4.8/-2.4 | +0.79/+0.29 | -/- | +0.56/-0.07 |
| EU4 G1-outC Q | 24/12 | +25.5 (+2.38) | +15.3 (+0.89) | 2.6/1.9 | +22.9 (+2.15) | +13.3 (+0.77) | +21.6/+12.4 | +19.5/+11.2 | +2.05/+1.07 | 100/16 | +1.15/+0.59 |
| DE40 G2-out60 Q | 24/12 | +4.4 (+0.98) | -5.5 (-0.60) | 0.9/0.3 | +3.5 (+0.80) | -5.9 (-0.63) | +3.1/-6.0 | +4.0/-9.8 | +0.70/-0.65 | -/- | +0.43/-0.48 |
| UK100 G2-out60 Q | 23/11 | -3.6 (-0.74) | -6.6 (-0.81) | 1.5/1.3 | -5.1 (-1.06) | -7.8 (-0.97) | -5.9/-8.5 | -5.4/-8.1 | -0.24/-0.86 | -/- | -0.57/-0.73 |
| STOXX50 G2-out60 Q | 22/12 | -3.1 (-0.51) | -6.5 (-0.83) | 4.5/3.5 | -7.6 (-1.24) | -10.1 (-1.28) | -9.8/-11.8 | -7.3/-7.2 | -0.12/-1.03 | -/- | -0.66/-0.97 |
| F40 G2-out60 Q | 23/12 | -4.5 (-0.99) | -17.8 (-1.94) | 3.5/2.6 | -7.9 (-1.76) | -20.4 (-2.21) | -9.7/-21.7 | -6.8/-19.7 | -0.80/-2.18 | -/- | -0.94/-1.68 |
| EU4 G2-out60 Q | 24/12 | -2.6 (-0.76) | -9.2 (-2.87) | 2.5/1.9 | -5.1 (-1.53) | -11.2 (-3.45) | -6.4/-12.1 | -4.7/-11.3 | -0.46/-3.12 | -/- | -0.82/-2.62 |
| DE40 G2-outC Q | 24/12 | +9.1 (+0.76) | +21.5 (+1.04) | 0.9/0.3 | +8.2 (+0.69) | +21.2 (+1.03) | +7.7/+21.0 | +8.8/+19.0 | +0.39/+1.30 | 91/98 | +0.37/+0.78 |
| UK100 G2-outC Q | 23/11 | -13.7 (-1.03) | -2.5 (-0.10) | 1.6/1.3 | -15.4 (-1.15) | -3.8 (-0.14) | -16.2/-4.5 | -15.1/-7.8 | -0.85/+0.02 | -/- | -0.62/-0.11 |
| STOXX50 G2-outC Q | 22/12 | -9.6 (-0.69) | +8.2 (+0.34) | 4.5/3.5 | -14.1 (-1.01) | +4.7 (+0.20) | -16.3/+2.9 | -16.2/+6.0 | -0.43/+0.67 | -/- | -0.54/+0.15 |
| F40 G2-outC Q | 23/12 | +6.6 (+0.78) | -12.7 (-1.27) | 3.5/2.6 | +3.2 (+0.38) | -15.3 (-1.52) | +1.5/-16.5 | +4.4/-12.8 | +0.91/-1.60 | -/- | +0.20/-1.16 |
| EU4 G2-outC Q | 24/12 | -4.2 (-0.50) | +3.4 (+0.28) | 2.6/1.9 | -6.8 (-0.81) | +1.4 (+0.12) | -8.0/+0.4 | -6.7/+0.9 | -0.43/+0.51 | -/- | -0.43/+0.09 |
| DE40 G3-in Q | 23/12 | +8.5 (+1.40) | -3.7 (-0.39) | 0.9/0.3 | +7.6 (+1.25) | -4.0 (-0.43) | +7.2/-4.2 | +6.8/-2.7 | +1.29/-0.67 | -/- | +0.67/-0.32 |
| UK100 G3-in Q | 22/12 | +7.2 (+1.05) | +10.2 (+1.26) | 1.6/1.3 | +5.6 (+0.82) | +8.9 (+1.10) | +4.8/+8.3 | +4.1/+9.1 | +1.10/+0.76 | 92/90 | +0.44/+0.83 |
| STOXX50 G3-in Q | 22/12 | -6.9 (-0.83) | +10.2 (+1.31) | 4.4/3.5 | -11.3 (-1.36) | +6.6 (+0.86) | -13.5/+4.9 | -7.6/+7.4 | -0.94/+0.62 | -/- | -0.73/+0.65 |
| F40 G3-in Q | 24/12 | -2.7 (-0.39) | -5.6 (-0.56) | 3.4/2.6 | -6.1 (-0.88) | -8.2 (-0.81) | -7.9/-9.5 | -8.3/-12.5 | -0.23/-0.72 | -/- | -0.47/-0.62 |
| EU4 G3-in Q | 24/12 | +1.6 (+0.47) | +2.8 (+1.04) | 2.6/1.9 | -1.0 (-0.29) | +0.8 (+0.31) | -2.3/-0.1 | -1.1/+0.3 | +0.45/-0.26 | -/- | -0.15/+0.24 |
| HK50 H1 Q | 18/9 | -6.5 (-0.29) | +76.6 (+2.13) | 3.4/2.7 | -9.9 (-0.44) | +74.0 (+2.07) | -11.6/+72.7 | -13.2/+71.6 | -0.30/+2.09 | -/- | -0.24/+1.57 |
| HK50 H2 Q | 18/9 | -9.7 (-0.79) | +53.1 (+2.29) | 3.4/2.7 | -13.1 (-1.07) | +50.5 (+2.15) | -14.8/+49.1 | -14.3/+48.3 | -0.92/+2.02 | -/- | -0.58/+1.63 |
| DE40 G1-in M | 48/24 | -6.3 (-1.38) | -4.4 (-1.13) | 0.8/0.3 | -7.1 (-1.55) | -4.7 (-1.21) | -7.5/-4.9 | -5.9/-4.3 | -1.97/-0.79 | -/- | -0.83/-0.92 |
| UK100 G1-in M | 48/24 | +1.4 (+0.38) | +9.9 (+2.15) | 1.6/1.3 | -0.2 (-0.06) | +8.6 (+1.87) | -1.0/+8.0 | -0.7/+10.2 | +0.19/+2.06 | -/- | -0.03/+1.42 |
| STOXX50 G1-in M | 48/24 | +3.1 (+0.75) | +7.5 (+1.68) | 4.4/3.5 | -1.3 (-0.33) | +4.0 (+0.89) | -3.5/+2.2 | -1.9/+2.1 | +0.51/+1.04 | -/- | -0.18/+0.67 |
| F40 G1-in M | 48/24 | -1.0 (-0.20) | +6.6 (+0.97) | 3.4/2.5 | -4.5 (-0.87) | +4.1 (+0.60) | -6.2/+2.8 | -5.3/+4.3 | +0.10/+0.98 | -/- | -0.47/+0.46 |
| EU4 G1-in M | 48/24 | -0.7 (-0.31) | +4.9 (+2.29) | 2.6/1.9 | -3.3 (-1.39) | +3.0 (+1.41) | -4.6/+2.0 | -3.4/+3.1 | -0.61/+1.83 | -/- | -0.75/+1.07 |
| DE40 G1-out60 M | 48/24 | -0.2 (-0.04) | -2.4 (-0.77) | 0.8/0.3 | -0.9 (-0.25) | -2.7 (-0.87) | -1.3/-2.9 | +0.2/-2.5 | -0.22/+0.39 | -/- | -0.13/-0.66 |
| UK100 G1-out60 M | 48/24 | +2.7 (+0.90) | +7.8 (+2.32) | 1.6/1.3 | +1.1 (+0.36) | +6.6 (+1.95) | +0.3/+6.0 | +0.4/+5.9 | +1.41/+1.59 | 71/100 | +0.19/+1.48 |
| STOXX50 G1-out60 M | 48/24 | +7.9 (+1.86) | +6.6 (+1.92) | 4.4/3.5 | +3.4 (+0.81) | +3.1 (+0.89) | +1.2/+1.3 | +3.5/+1.8 | +1.97/+1.42 | 97/96 | +0.44/+0.67 |
| F40 G1-out60 M | 48/24 | -4.8 (-1.44) | +3.3 (+0.48) | 3.4/2.5 | -8.2 (-2.48) | +0.8 (+0.12) | -9.9/-0.4 | -9.0/-0.2 | -2.43/+0.66 | -/- | -1.33/+0.09 |
| EU4 G1-out60 M | 48/24 | +1.4 (+0.69) | +3.8 (+1.84) | 2.6/1.9 | -1.2 (-0.56) | +1.9 (+0.93) | -2.4/+1.0 | -1.2/+1.2 | +0.41/+1.89 | -/- | -0.30/+0.71 |
| DE40 G1-outC M | 48/24 | -2.6 (-0.34) | -5.8 (-0.48) | 0.8/0.3 | -3.4 (-0.45) | -6.1 (-0.51) | -3.8/-6.3 | -4.2/-6.3 | -0.70/+0.05 | -/- | -0.24/-0.38 |
| UK100 G1-outC M | 48/24 | +0.1 (+0.02) | +2.7 (+0.25) | 1.7/1.3 | -1.6 (-0.27) | +1.5 (+0.13) | -2.4/+0.8 | -3.0/-0.4 | +0.18/+0.51 | -/- | -0.14/+0.10 |
| STOXX50 G1-outC M | 48/24 | +1.8 (+0.23) | +3.6 (+0.29) | 4.4/3.5 | -2.6 (-0.34) | +0.1 (+0.01) | -4.8/-1.7 | -3.5/-1.8 | -0.04/+0.55 | -/- | -0.18/+0.01 |
| F40 G1-outC M | 48/24 | -8.7 (-2.49) | +0.5 (+0.07) | 3.4/2.5 | -12.1 (-3.46) | -2.0 (-0.27) | -13.9/-3.3 | -13.4/-2.9 | -3.11/+0.26 | -/- | -1.86/-0.20 |
| EU4 G1-outC M | 48/24 | -2.4 (-0.46) | +0.3 (+0.03) | 2.6/1.9 | -4.9 (-0.97) | -1.6 (-0.17) | -6.2/-2.6 | -6.0/-2.8 | -0.77/+0.39 | -/- | -0.52/-0.13 |
| DE40 G2-out60 M | 48/24 | +0.9 (+0.23) | +3.0 (+0.99) | 0.8/0.3 | +0.1 (+0.03) | +2.7 (+0.88) | -0.3/+2.6 | -0.1/+3.6 | -0.06/+0.65 | 73/71 | +0.01/+0.67 |
| UK100 G2-out60 M | 48/24 | -2.1 (-0.70) | +7.4 (+2.18) | 1.6/1.3 | -3.7 (-1.24) | +6.2 (+1.81) | -4.6/+5.6 | -3.4/+4.9 | +0.07/+1.85 | -/- | -0.66/+1.38 |
| STOXX50 G2-out60 M | 48/23 | +6.0 (+1.40) | +5.7 (+1.58) | 4.4/3.5 | +1.6 (+0.37) | +2.2 (+0.60) | -0.6/+0.4 | +2.5/+2.1 | +1.80/+0.74 | 93/76 | +0.20/+0.46 |
| F40 G2-out60 M | 48/23 | +3.4 (+1.02) | +1.7 (+0.26) | 3.4/2.5 | -0.0 (-0.01) | -0.8 (-0.13) | -1.8/-2.1 | +0.9/-0.8 | +1.00/-0.24 | -/- | -0.01/-0.10 |
| EU4 G2-out60 M | 48/24 | +2.0 (+1.15) | +4.5 (+2.26) | 2.6/1.9 | -0.5 (-0.29) | +2.6 (+1.31) | -1.8/+1.6 | -0.0/+2.4 | +1.53/+1.23 | -/- | -0.16/+1.00 |
| DE40 G2-outC M | 48/24 | +0.3 (+0.03) | -0.3 (-0.03) | 0.8/0.3 | -0.5 (-0.07) | -0.6 (-0.05) | -0.9/-0.8 | +0.1/+0.2 | -0.43/+0.45 | -/- | -0.04/-0.04 |
| UK100 G2-outC M | 48/24 | +4.9 (+0.83) | +12.0 (+1.12) | 1.7/1.3 | +3.2 (+0.54) | +10.8 (+1.00) | +2.3/+10.1 | +3.4/+8.5 | +0.96/+1.28 | 66/61 | +0.29/+0.76 |
| STOXX50 G2-outC M | 48/23 | +4.0 (+0.51) | +14.4 (+1.13) | 4.4/3.5 | -0.4 (-0.06) | +10.9 (+0.86) | -2.6/+9.1 | +0.6/+10.8 | +0.80/+1.57 | -/- | -0.03/+0.65 |
| F40 G2-outC M | 48/23 | +7.0 (+1.97) | -0.8 (-0.11) | 3.4/2.5 | +3.6 (+1.01) | -3.3 (-0.47) | +1.9/-4.5 | +4.0/-2.7 | +1.89/-0.65 | -/- | +0.54/-0.35 |
| EU4 G2-outC M | 48/24 | +4.0 (+0.96) | +6.6 (+1.68) | 2.6/1.9 | +1.5 (+0.35) | +4.7 (+1.20) | +0.2/+3.8 | +2.0/+4.5 | +0.95/+1.92 | 83/65 | +0.19/+0.91 |
| DE40 G3-in M | 48/24 | +3.6 (+0.78) | -1.7 (-0.43) | 0.8/0.3 | +2.9 (+0.62) | -2.0 (-0.51) | +2.5/-2.2 | +3.0/-1.6 | +0.67/-0.91 | -/- | +0.33/-0.39 |
| UK100 G3-in M | 48/24 | -1.5 (-0.41) | +5.1 (+1.03) | 1.6/1.3 | -3.1 (-0.85) | +3.8 (+0.78) | -3.9/+3.2 | -3.1/+4.6 | -0.23/+0.25 | -/- | -0.45/+0.59 |
| STOXX50 G3-in M | 48/24 | -5.6 (-1.40) | -1.9 (-0.40) | 4.4/3.5 | -10.1 (-2.50) | -5.4 (-1.15) | -12.3/-7.2 | -7.5/-6.1 | -1.52/-1.32 | -/- | -1.34/-0.87 |
| F40 G3-in M | 48/24 | +2.7 (+0.52) | -6.5 (-0.96) | 3.4/2.5 | -0.8 (-0.15) | -9.1 (-1.33) | -2.5/-10.3 | -1.0/-9.4 | +0.64/-1.12 | -/- | -0.08/-1.01 |
| EU4 G3-in M | 48/24 | -0.2 (-0.09) | -1.3 (-0.49) | 2.6/1.9 | -2.8 (-1.18) | -3.2 (-1.23) | -4.1/-4.1 | -2.1/-3.1 | -0.07/-1.59 | -/- | -0.63/-0.93 |
| HK50 H1 M | 47/24 | +8.1 (+0.71) | +27.7 (+0.87) | 3.2/2.7 | +4.9 (+0.43) | +24.9 (+0.78) | +3.3/+23.6 | +6.6/+20.6 | +0.66/+0.84 | -/- | +0.23/+0.59 |
| HK50 H2 M | 47/24 | +4.8 (+0.62) | -1.6 (-0.12) | 3.2/2.8 | +1.6 (+0.21) | -4.4 (-0.33) | -0.0/-5.8 | +0.3/-1.9 | +0.40/-0.54 | -/- | +0.11/-0.25 |

## Sources
- Eurex, DAX Futures and DAX Options contract specifications: https://www.eurex.com/ex-en/markets/idx/dax/DAX-Futures-139902
- Deutsche Börse, Xetra auction schedule: https://www.cashmarket.deutsche-boerse.com/cash-en/trading/Xetra/continuous-trading-with-auctions/auctionschedule
- Eurex, EURO STOXX 50 Index Futures: https://www.eurex.com/ex-en/markets/idx/stx/euro-stoxx-50-derivatives/products/EURO-STOXX-50-Index-Futures-160088
- Euronext, CAC 40 index future specification: https://live.euronext.com/en/product/index-futures/FCE-DPAR/contract-specification
- ICE, FTSE 100 Index Futures and Options Contracts (EDSP): https://www.ice.com/publicdocs/futures/IFEU_FTSE_100_Index_Futures_Options_Contracts.pdf
- LSE Market Notice N14/15 (15 July 2015): https://docs.londonstockexchange.com/sites/default/files/documents/n1415.pdf
- HKFE Rules, HSI futures and options specifications: https://www.hkex.com.hk/-/media/HKEX-Market/Services/Rules-and-Forms-and-Fees/Rules/HKFE/Rule-Update_Rules-Regulations-and-Procedures-of-the-Futures-Exchange/01-hkferules-hsil.pdf
- Stoll & Whaley 1987, FAJ 43(2): https://rpc.cfainstitute.org/research/financial-analysts-journal/1987/program-trading-and-expiration-day-effects
- Stoll & Whaley 1991, FAJ 47(1), doi 10.2469/faj.v47.n1.58; Stoll & Whaley 1997, AJM 22(2), doi 10.1177/031289629702200202
- Chow, Yung & Zhang 2003, JFM 23, doi 10.1002/fut.10054 (abstract via OpenAlex)
- Fung & Yung 2009, JFM 29, doi 10.1002/fut.20364 (abstract via OpenAlex)
- Alkebäck & Hagelin 2004, AFE 14(6), doi 10.1080/09603100410001673612
- Schlag 1996, EFM 2(1), doi 10.1111/j.1468-036x.1996.tb00029.x (RePEc summary)
- Joensuu 2010, Aalto MSc thesis: https://aaltodoc.aalto.fi/items/c3e236e3-8f48-4c5e-b933-6b60e1f4ffca
- Baltussen, Terstegge & Whelan 2024, "The Derivative Payoff Bias": https://afajof.org/management/viewp.php?n=98196
- Batrinca, Hesse & Treleaven 2020, Empirical Economics, doi 10.1007/s00181-019-01627-2
- Illueca & Lafuente 2006, JFM 26, doi 10.1002/fut.20220; Agarwalla & Pandey 2013, JFM 33, doi 10.1002/fut.21632;
  Xu 2014, JFM 34, doi 10.1002/fut.21620

OpenAlex hit its daily limit midway (HTTP 429), so the searches went through Crossref, Semantic Scholar and the
publishers' pages.

## Scripts and outputs
They are in the scratchpad, under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r20/G/.

| script | what it does | output |
|---|---|---|
| libg.py | loaders (HOLD cut), venue calendars, expiry rules | |
| cal_print.py | the expiry calendar | expiry_calendar.json |
| rows.py | every counted rule on expiry and placebo days | rows_G.pkl |
| analyze.py | the 64 cells and the information rows | analyze_out.txt, cells.pkl |
| perm.py | the shared sign-flip null | perm_out.txt |
| randctl.py | the random-entry control | random_out.txt |
| c3corr.py | correlation with C3 | c3corr_out.txt |
| posthoc.py | P1-P3 | posthoc_out.txt |
| table.py | the cell table above | table_out.md |

Also in that folder:
- lit/: literature query outputs (baltussen_dpb.txt is the paper's text);
- dl/: exchange documents.
