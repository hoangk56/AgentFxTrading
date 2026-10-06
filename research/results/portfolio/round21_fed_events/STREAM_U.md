# Round 21, stream U: the FOMC-day dollar premium (round 20 F, rule A4) on other scheduled US-policy events

2026-10-06. Every rule is in [HYPOTHESES_U.md](HYPOTHESES_U.md), written at 04:31 UTC before any return. The first
return was computed at 04:32 UTC. 8 cells were declared and 8 judged; nothing was added after looking except the
"information only" block. HOLD (2025+) was never loaded: the panel ends 2024-12-31, Dukascopy is cut at 2016-01-01,
the calendars stop at 2024-12-31, FRED rates are cut at 2024-12-31, and C3's trades are filtered to IS + VAL.

**Verdict: no cell meets LIVE or DEMO, so there is no PREREG_DRAFT.** The FOMC premium does not extend to the other
scheduled US-policy events:
- FOMC minutes, the Chair's semiannual testimony, the Jackson Hole speech and the Treasury refunding statement,
  pooled (U5, primary), earn -3.0 bp net in PRE, +6.9 (t 1.07) in IS and -11.6 (t -0.96) in VAL.
- The minutes, the largest group, are negative in PRE and VAL.
- The only cell with a DEMO-size IS t, U6 (the events pooled with FOMC), gets that t from the FOMC days round 20
  already measured. It fails the random-entry control in VAL (83 %). Its VAL t is 0.53, and its best IS t (2.10) is
  within chance for 8 cells.
- Gold over the same windows (G1, G2) fails too.

This matches the literature the cells were declared against:
- Mueller et al. (2017) find no currency premium on payroll, CPI or PPI days.
- Bauer, Lakdawala & Mueller (2022) find that only FOMC announcements resolve short-rate uncertainty.

## Event calendars 2004-2024 (official sources; scratchpad r21/U/build_cal.py -> cal/events_u.json)
| type | event, time (ET) | source | n | kept PRE / IS / VAL |
|---|---|---|---|---|
| MIN | FOMC minutes, 14:00 (2013-04-10 09:00); Thursday after the next meeting until 2004-12, 3 weeks after from 2005-01-04 | federalreserve.gov fomchistorical / fomccalendars pages and json/ne-press.json (via r12 cb_calendar.json) | 168 | 96 / 48 / 24 |
| TES | Chair's semiannual Monetary Policy Report testimony, first day; 08:30-10:00 posting / hearing (2010-07-21 14:00) | federalreserve.gov/json/ne-testimony.json; newsevents/testimony/2004testimony.htm, 2005testimony.htm | 42 | 24 / 12 / 6 |
| JH | Jackson Hole Chair speech, 10:00 ET = 08:00 MT (2020-08-27 09:10, 2023 10:05); none in 2013 or 2015 (no Chair speech) | federalreserve.gov/json/ne-speeches.json, newsevents/speech/2004speech.htm, 2005speech.htm; the kansascityfed.org symposium pages list the speeches but no clock times | 19 | 10 / 6 / 3 |
| QRA | Treasury quarterly refunding statement, Wednesday, 09:00 until 2013-05, 08:30 from 2013-07-31 | home.treasury.gov official-remarks archive (84 press releases); times from the Monday "Marketable Borrowing Estimates" releases and po946 (2002 procedure) | 84 | 35 / 12 / 4 |

Day boundaries:
- Only the minutes come at 14:00 ET. **For every non-FOMC event the window is A4's 16:00-to-16:00 ET day of the
  event date**: 16:00 ET on the previous weekday to 16:00 ET on the event day. All events are between 08:30 and 14:00
  ET and fall Tuesday to Friday.
- FOMC days keep round 20's windows.
- **Non-FOMC events whose window contains an FOMC decision are excluded.** This removed 33 refunding Wednesdays and
  nothing else.

Trade counts:
- The pooled cells make one trade per window.
- A4 makes no trade from 2018-09 to 2019-10, when no currency's rate was above USD's. This removed 12 U5 windows and
  23 U6 windows.

## Mechanism and literature (details in HYPOTHESES_U.md)
| event | literature | status |
|---|---|---|
| MIN | Rosa (2013, FRBNY EPR 19(2)): the minutes raise the volatility of yields, stocks and USD rates, less over time. Jubinski & Tomljanovich (2013, RFE). Boukus & Rosenberg (2006) | market effects only; no directional premium: pure extension |
| TES | Kohn & Sack (2004): Greenspan's testimonies moved Treasury yields. Bauer, Lakdawala & Mueller (2022, EJ) App. D.4: Chair speech days do not resolve short-rate uncertainty | pure extension, contrary evidence |
| JH | no premium literature found; BLM (2022) D.4 as above | pure extension, contrary evidence |
| QRA | Wang & Zhao (SSRN 4764295, 2024/25): Treasuries earn a premium on the day before the **Monday** borrowing-estimate release (fiscal uncertainty) | another asset, event and window: pure extension for FX |
| all | Mueller, Tahbaz-Salehi & Vedolin (2017) Table XIII: no premium on payroll, CPI or PPI days. BLM (2022): short-rate uncertainty falls 1.6 bp on FOMC days, ~0 otherwise | prior against extension |
| gold | none found | pure extension of the dollar leg |

Considered and not declared:
- The Beige Book: its literature is about forecasting content, not uncertainty.
- The FOMC-cycle even weeks (Cieslak, Morse & Vissing-Jorgensen 2019): not an event with a resolution time.
- The Monday borrowing-estimate release.

## Results (bp per event; t clustered by exit date; costs at IC's)
| cell | n PRE / IS / VAL | mid PRE / IS / VAL (t) | cost IS / VAL (swap) | net IS (t) / VAL (t); PRE | x1.5 IS / VAL | +1 min IS / VAL (PRE +1 h) | VAL/IS | yrs > 0 IS, VAL | placebo diff IS / VAL (t) | random IS / VAL | power IS / VAL size | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U1 minutes | 95 / 39 / 24 | -3.4 (-0.54) / +3.7 (0.50) / -15.3 (-1.10) | 1.1 / 1.1 (-0.2) | +2.3 (0.32) / -16.6 (-1.19); PRE -4.4 | +2.1 / -16.8 | +2.4 / -16.6 (-7.3) | <0 | 2/6, 0/3 | +2.1 (0.28) / -14.1 (-1.01) | 59 % / 12 % | 0.19 / -0.91 | fails |
| U2 testimony | 24 / 10 / 6 | +9.7 (0.86) / +8.5 (0.60) / +9.4 (0.30) | 1.2 / 0.9 (-0.2) | +7.1 (0.50) / +8.3 (0.27); PRE +8.6 | +6.8 / +8.1 | +6.2 / +8.4 (+7.5) | 1.17 | 3/5, 2/3 | +8.2 (0.57) / +9.3 (0.30) | 68 % / 66 % | 0.29 / 0.20 | fails (IS t 0.50) |
| U3 Jackson Hole | 7 / 5 / 3 | +7.0 (0.50) / +35.4 (1.26) / -0.4 (0.00) | 1.1 / 1.7 (-0.3) | +33.9 (1.21) / -2.3 (-0.03); PRE +5.9 | +33.6 / -2.8 | +32.7 / -0.1 (+6.4) | <0 | 4/5, 1/3 | +39.9 (1.42) / +5.3 (0.06) | 96 % / 54 % | 0.71 / -0.02 | fails |
| U4 refunding | 35 / 11 / 4 | -7.7 (-0.99) / +11.9 (0.54) / -16.9 (-0.55) | 1.0 / 1.2 (-0.2) | +10.6 (0.48) / -18.3 (-0.59); PRE -8.7 | +10.4 / -18.6 | +9.7 / -18.8 (-12.9) | <0 | 2/4, 1/3 | +10.0 (0.45) / -15.3 (-0.49) | 75 % / 34 % | 0.22 / -0.45 | fails |
| **U5 primary: U1-U4 pooled** | 161 / 65 / 37 | -2.0 (-0.44) / +8.2 (1.29) / -10.3 (-0.85) | 1.1 / 1.1 (-0.2) | +6.9 (1.07) / -11.6 (-0.96); PRE -3.0 | +6.6 / -11.8 | +6.6 / -11.4 (-5.7) | <0 | 3/6, 1/3 | +7.3 (1.13) / -8.9 (-0.73) | 88 % / 17 % | 0.62 / -0.73 | fails |
| U6: U5 + FOMC | 257 / 102 / 60 | +5.4 (1.26) / +13.6 (2.34) / +6.3 (0.67) | 1.1 / 1.1 (-0.2) | **+12.2 (2.10)** / +5.0 (0.53); PRE +4.4 (1.02) | +12.0 / +4.7 | +12.0 / +4.9 (+1.7) | 0.41 | 6/6, 3/3 | +12.3 (2.12) / +7.8 (0.83) | 99 % / **83 %** | 1.23 / 0.40 | fails DEMO (random VAL < 90 %; IS t from the seen FOMC days) |
| G1: gold, U5 windows | 164 / 75 / 36 | +8.1 (0.80) / +3.6 (0.35) / -9.7 (-0.71) | 1.6 / 1.1 (-0.6 / -1.3) | +1.4 (0.14) / -12.1 (-0.89); PRE +5.6 | +0.9 / -12.3 | +1.2 / -11.8 (n/a) | <0 | 3/6, 0/3 | -3.2 (-0.31) / -2.7 (-0.20) | 36 % / 43 % | 0.07 / -0.68 | fails |
| G2: gold, U6 windows | 260 / 122 / 60 | +8.2 (1.04) / +12.6 (1.54) / +12.2 (1.02) | 1.6 / 1.1 (-0.6 / -1.4) | +10.4 (1.27) / +9.7 (0.81); PRE +5.6 | +9.9 / +9.5 | +10.1 / +10.0 (n/a) | 0.93 | 5/6, 2/3 | +5.3 (0.64) / +20.4 (1.69) | 78 % / 98 % | 0.68 / 0.62 | fails (IS t 1.27) |

Notes on the table:
- **Power** = per-event net Sharpe x sqrt(expected HOLD events), with HOLD events = VAL trades / 3 x 1.73 (U5 21,
  U6 35, G2 35). The VAL-size column is the expected HOLD t. Even U6's IS Sharpe (0.21) gives power 1.2 against
  LIVE's 3.
- **Placebo pool:** 4 pm-to-4 pm weekdays with no decision by the 8 banks and no U event, holidays excluded: PRE
  1,891 / IS 984 / VAL 506. The random control used 1,000 seeds, each drawing a placebo day of the same era and
  weekday.
- **Dropped for missing prices:** 4 PRE windows in the A4 cells (Dukascopy gaps: 2007-08-31, 2008-01-02, 2008-08-22,
  2009-08-21) and 4 IS/VAL gold windows (2012-01-03, and 07-05 of 2017, 2018 and 2023: no IC gold quote at 16:00 ET
  on the day after a US holiday).
- **Gold PRE +1 h is n/a:** 17:00 ET falls in IC's gold daily break, so there is no spread profile.

Net by year (bp):
- **U5:**
  - PRE: 2004 +4.7, 2005 -7.9, 2006 +0.3, 2007 +4.2, 2008 -21.0, 2009 +28.0, 2010 -22.4, 2011 +13.3, 2012 +12.1,
    2013 -36.4, 2014 -4.2, 2015 -10.4.
  - IS: 2016 -2.2, 2017 +35.7, 2018 -5.6, 2019 -27.3, 2020 +4.3, 2021 +4.5.
  - VAL: 2022 -6.2, 2023 -30.4, 2024 +1.4.
- **U6:**
  - IS: 2016 +1.0, 2017 +39.6, 2018 +1.4, 2019 +6.9, 2020 +13.0, 2021 +5.2.
  - VAL: 2022 +5.2, 2023 +1.6, 2024 +8.4.
  - PRE: 7/12 years > 0.
- **U1 (minutes), VAL:** 2022 -2.0, 2023 -23.3, 2024 -24.4.

The other per-year rows are in out_info.txt.

## Declared descriptive splits (no verdicts)
**U6 by window type:**

| windows | PRE | IS | VAL |
|---|---|---|---|
| FOMC (= round 20 A4) | +16.6 (1.97), n 96 | +21.6 (1.90), n 37 | +31.6 (2.40), n 23 |
| non-FOMC (= U5) | -3.0, n 161 | +6.9 (1.07), n 65 | -11.6 (-0.96), n 37 |

The pool is the FOMC effect diluted by events that carry nothing. The prior had already said this: with a
zero-premium extension, U6's IS t would be about 1.1. It came out at 2.1 because U5 was +6.9 in IS, and it then
fell to 0.5 in VAL.

**G1 by type, net (bp):**

| type | PRE | IS | VAL |
|---|---|---|---|
| MIN | +8.9 | -2.5 | -12.5 |
| TES | -18.2 | -23.0 | -27.7 |
| JH | +53.8 (n 10) | +67.5 (n 6) | -10.3 (n 3) |
| QRA | -1.0 | -6.9 | +12.6 (n 4) |

## Family summary and chance
| family | cells | best IS net t | chance |
|---|---|---|---|
| A4 on US-policy events + gold | 8 | 2.10 (U6) | max \|t\| of 8 independent normals: median 1.73, 95th pct 2.72. The sign-flip-by-date null over the 8 cells (IS mid) has median 1.73 and 95th pct 5.57; it is inflated by the 5- and 11-event cells, whose sign-flipped t-stats are extreme. U6's own sign-flip p is 0.023 (IS mid t 2.34) |

C3 correlation (IS + VAL, by exit date) for the cells with net > 0 in IS and VAL:

| cell | daily | monthly |
|---|---|---|
| U2 | -0.00 | -0.12 |
| U6 | -0.01 | -0.17 |
| G2 | -0.00 | -0.18 |

## Information only (seen after the cells; not candidates)
- **Gold on FOMC days (G2's FOMC split):** PRE +5.8 (t 0.46), IS +24.8 (1.85), VAL +42.4 (2.05). The same shape as
  round 20's dollar result (strong after 2015, weak in 2004-15). It was not declared as a cell, so it cannot be a
  candidate this round. It also has the same problem as A4: 8 events a year.
- **Jackson Hole:** the dollar falls (U3 IS +33.9) and gold rises (+67.5 IS, +53.8 PRE) in IS and PRE but not in VAL
  (2022's hawkish speech: -143.5 bp). This rests on 19 events in 21 years; it cannot be tested.
- **Testimony:** U2 is the only event type with net > 0 in all three eras (+8.6 / +7.1 / +8.3). But t <= 0.8, with
  40 events in 21 years.
- **Minutes:** the dollar tends to rise on minutes days since 2018 (VAL 0/3 years > 0). That is the opposite of the
  premium; it is not significant.

## Directions that need the user
- None new. The premium is specific to the FOMC decision itself, as the literature says, so the extension does not
  raise the event count. Round 20's options for the FOMC-only rule stand:
  - accept a bar on the 2004-24 pooled evidence;
  - run a slow demo (8 trades a year);
  - add NOK, SEK and other currencies on FOMC days, which needs new price data.
- If the user ever opens a new declared round on the FOMC day, gold on FOMC days (above) could be declared there.
- Caveat for any A4-type rule: A4 trades only when some currency's policy rate is above USD's. With US rates near
  the top of the G10 range, it makes few or no trades (as in 2018-19).

## Scripts and outputs
Scratchpad r21/U/:
- **build_cal.py**: builds cal/events_u.json from dl/, the official pages and JSON downloaded 2026-10-06:
  - federalreserve.gov ne-testimony.json, ne-speeches.json, the 2004/2005 testimony and speech pages;
  - treasury.gov tsy/remarks.html, tsy/pr/* (refunding statements), tsy/fe/* (borrowing estimates);
  - literature PDFs in dl/lit/ (Wang & Zhao; Bauer, Lakdawala & Mueller).
- **ulib.py**: the U windows, the FOMC-overlap exclusion, pooling, the placebo exclusion list, XAUUSD prices and the
  gold trade. It reuses round 20 F's flib.py unchanged.
- **run_u.py**: the 8 cells, placebo, random control and sign-flip null. It writes out_run.json, out_run.txt,
  events.csv and run.log.
- **info_u.py**: per-year tables, the declared splits, C3 correlation and chance. It writes out_info.txt.
