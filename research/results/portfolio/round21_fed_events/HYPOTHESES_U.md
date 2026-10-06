# Round 21, stream U: the FOMC-day dollar premium (round 20 F, rule A4) on other scheduled US-policy events

Written 2026-10-06 04:31 UTC (`date -u` gave 04:30:47), before any stream-U return, mean or t was computed. Only
the event calendars (dates, times, counts per era) and data layouts were inspected. HOLD (2025-01-01 onwards) is
never loaded: the panel ends 2024-12-31, Dukascopy is cut at 2016-01-01, events are cut at 2024-12-31, FRED rates are
cut at 2024-12-31 (flib), C3 trades are filtered to IS + VAL.

## The rule carried over unchanged (round 20 F, A4)
Long, equal weight, every currency j of EUR GBP JPY AUD NZD CAD CHF whose rate r_j > r_USD, against USD, from E = 16:00
New York to X = 16:00 New York; no trade if no currency qualifies (so no trade 2018-09..2019-10 and in some single
months, as in round 20). Ranks causal (rates as of the end of the previous month: BIS policy rates before 2016, local
FRED files from 2016; JPY fill as round 20 F Amendment 2). Execution, prices, costs, swaps, latency, statistics and
code: round 20 F's flib.py, unchanged (HYPOTHESES_F.md incl. Amendments 1-2). Source of the rule: Mueller,
Tahbaz-Salehi & Vedolin (2017), JF 72(3) 1213-1252 (S2 without the tightening switch); its mechanism: a premium for
bearing uncertainty about the US short rate, paid until that uncertainty is resolved.

## Windows (the 16:00 ET day boundaries)
- FOMC decisions (scheduled, as round 20): flib.window, i.e. the paper's 4 pm-4 pm day containing the 14:00/14:15
  ET statement.
- Every other event: **none is at 14:00 ET except the minutes, so for all non-FOMC events the window is declared by
  date: E = 16:00 ET on the previous weekday, X = 16:00 ET on the event date** (A4's 16:00-to-16:00 ET window of the
  event day). All event times are 08:30-14:00 ET (none at or after 15:00 ET), so every event lies inside its window
  with >= 2 h to X. Weekend: a Monday event has E = Friday 16:00 (none in the calendars: events fall Tue-Fri).
- **Exclusion:** a non-FOMC event whose window [E, X] contains any FOMC decision (scheduled or unscheduled) is dropped
  from the non-FOMC cells (U1-U5, G1). This drops 33 refunding Wednesdays and nothing else. In the pooled cells one
  trade is made per window (two events on one window = one trade; only 2019-07-10, minutes + testimony).

## Event calendars 2004-2024 (built 04:27-04:29 UTC; scratchpad r21/U/build_cal.py -> cal/events_u.json)
| type | event and time (ET) | official source | n 2004-24 | PRE / IS / VAL kept |
|---|---|---|---|---|
| MIN | FOMC minutes release, 14:00 (2013-04-10 at 09:00, early release); pre-2005 minutes came on the Thursday after the next meeting, from 2005-01-04 three weeks after the meeting | federalreserve.gov fomchistorical{yyyy}.htm and fomccalendars.htm (release dates), json/ne-press.json (times), via r12/shared/cal/cb_calendar.json | 168 | 96 / 48 / 24 |
| TES | Chair's semiannual Monetary Policy Report testimony, **first day only** (the prepared statement and the Q&A first meet the market; the second chamber gets identical remarks the next day or later); hearing / posting times 08:30-10:00 (2010-07-21: 14:00); 2004-08 times not given (morning hearings) | federalreserve.gov/json/ne-testimony.json (2006-24, "submitted identical remarks ... on <date>" gives the other day), newsevents/testimony/2004testimony.htm and 2005testimony.htm (Greenspan) | 42 | 24 / 12 / 6 |
| JH | Kansas City Fed Jackson Hole symposium, Chair's speech; 10:00 ET (08:00 MT) 2009-24 except 2020-08-27 09:10 ET (virtual, Thursday) and 2023 10:05 ET; 2004-08 times not given (Friday morning programme). No Chair speech in 2013; 2015 was Vice Chair Fischer (Saturday) - both years have no event | federalreserve.gov/json/ne-speeches.json, newsevents/speech/2004speech.htm, 2005speech.htm. The KC Fed symposium pages (kansascityfed.org, checked 2012 and 2021) list the speech but no clock time | 19 | 10 / 6 / 3 |
| QRA | Treasury quarterly refunding statement (the Wednesday "Quarterly Refunding Statement"), 09:00 ET until 2013-05-01, 08:30 ET from 2013-07-31 | home.treasury.gov official-remarks-on-quarterly-refunding archive (one press release per quarter, its date); times from the Monday "Marketable Borrowing Estimates" releases ("... at 9:00 a.m. on Wednesday" 2007-13, "8:30 a.m." from 2013-07), 2002 procedure release po946 (09:00) | 84 | 35 / 12 / 4 (33 dropped: FOMC day) |
| FOMC | scheduled decisions (round 20 F A4) | r12 cb_calendar.json | 167 | 96 / 47 / 24 |

Pooled non-FOMC windows: PRE 165 / IS 77 / VAL 37; pooled with FOMC: 261 / 124 / 61 (about 20 a year, not the
brief's hoped-for 25-30, because the refunding Wednesday often is an FOMC day and JH / testimony are rare).

## Mechanism and literature, per event type (searched 04:20-04:27 UTC; OpenAlex and Semantic Scholar were rate-limited, Crossref partly; web search, publisher / author PDFs)
General: the announcement premium under generalized risk sensitivity (Ai & Bansal 2018, Econometrica 86(4)) and
the scheduled-announcement equity premium (Savor & Wilson 2013, JFQA 48(2)) predict a premium on any scheduled event
that resolves macro uncertainty. Two findings work against extending A4 beyond FOMC:
(1) Mueller et al. (2017) Table XIII: **no** currency premium on payroll, CPI or PPI days ("monetary policy
announcements by the Federal Reserve have a unique impact on currency returns"); (2) Bauer, Lakdawala & Mueller
(2022, EJ, "Market-based monetary policy uncertainty"): short-rate uncertainty falls by 1.6 bp on scheduled FOMC days
and ~0 on other days; the employment report resolves half as much; **speeches by FOMC members, including the Chair's
speech days 1994-2017, have no systematic effect on short-rate uncertainty** (their online Appendix D.4).
- **MIN.** The minutes reveal the balance of views and the expected path, i.e. news about future policy. Literature
  on market effects, not on a premium: Rosa (2013, FRBNY Economic Policy Review 19(2)), minutes raise the volatility
  of yields, stocks and USD exchange rates (about ISM-sized; smaller than statements or payrolls), with a declining
  impact; Jubinski & Tomljanovich (2013, Review of Financial Economics, doi 10.1016/j.rfe.2013.01.002), intraday
  equity effects; Boukus & Rosenberg (2006, SSRN 922312), information content. Oct 2007 - Jan 2011 the SEP came with
  the minutes. **No paper documents a directional premium on minutes days: pure extension of the premium.**
- **TES.** The Chair's prepared statement and Q&A on the outlook and policy path. Kohn & Sack (2004, "Central bank
  talk: does it matter and why?", Bank of Canada conference volume): Greenspan's testimonies moved Treasury yields
  significantly (volatility). No premium literature; BLM (2022) D.4 is direct evidence against (Chair speech days do
  not resolve short-rate uncertainty). **Pure extension, with contrary evidence.**
- **JH.** The Chair's annual speech is used to signal framework or policy shifts (e.g. 2010 QE2, 2020 average
  inflation targeting, 2022). No premium literature found; BLM (2022) D.4 as above. **Pure extension, with contrary
  evidence.**
- **QRA.** Wang & Zhao ("Pre-Refunding Announcement Gains in U.S. Treasurys", SSRN 4764295, 2024, rev. July 2025):
  10-30-year Treasuries earn a premium on the day **before** the Monday 15:00 ET "Marketable Borrowing Estimates"
  release (fiscal-uncertainty resolution, stronger right after an FOMC meeting and near the debt ceiling). Their asset
  (Treasuries), event (Monday release) and window (the pre-event day) all differ from this cell; the paper gives no
  sign for the dollar. The Wednesday statement is what the brief and treasury.gov call the quarterly refunding
  announcement; it is declared as is. **Pure extension of the FX premium** (the mechanism, uncertainty resolution, is
  documented for the Treasury market only).
- Considered, not declared: the Beige Book (its literature is about forecasting content - Balke & Petersen 2002 JMCB,
  Armesto et al. 2009 JMCB - not uncertainty or a premium); the FOMC-cycle even weeks (Cieslak, Morse &
  Vissing-Jorgensen 2019 JF 74(5)) - not a scheduled event with a resolution time; the Monday financing-estimate
  release itself (Wang & Zhao's event: its premium is on the day before, in bonds; a second refunding cell would add a
  cell without an FX mechanism); press conferences and SEP (part of the FOMC event).
- **Gold.** If these days carry a dollar-short premium, gold quoted in USD should rise over the same window; the gold
  leg tests the dollar leg in a second asset. No gold-specific literature on Fed-event premia found in this pass:
  pure extension.

Prior (arithmetic before data): round 20's FOMC A4 per-event Sharpe is ~0.26 (2004-24 pooled; seen). If every
non-FOMC event carried the same premium, U5 (IS ~65 trades after no-trade months) would have an expected IS t of
~2.1 and U6 ~2.8. If they carry nothing, U5's expected t is 0 and pooling dilutes FOMC: U6's IS t would be ~1.1 (A4
alone 1.90). Literature (Mueller et al. Table XIII; BLM 2022) points to the second case. **U6 contains round 20's 47
IS / 24 VAL FOMC trades, whose numbers are already known; only the non-FOMC events are new information.** HOLD power
for LIVE needs per-event Sharpe >= 3 / sqrt(~35) = 0.51 for U6 (~20 events a year x 1.73), out of reach for
anything round 20 saw; DEMO (IS t >= 2.0) is the reachable bar.

## Cells (8 in all; no others will be judged)
| cell | events (windows) | rule |
|---|---|---|
| U1 | MIN | A4 |
| U2 | TES | A4 |
| U3 | JH | A4 |
| U4 | QRA (non-FOMC Wednesdays) | A4 |
| **U5 (primary)** | MIN + TES + JH + QRA pooled, one trade per window | A4 |
| U6 (secondary) | U5 + scheduled FOMC decisions (round 20 windows), one trade per window | A4 |
| G1 | U5's windows | long XAUUSD |
| G2 | U6's windows | long XAUUSD |
Descriptive only (no verdict): G1 split by event type; per-type numbers inside U6; the A4 split pre / post event
time is not computed (non-FOMC event times before 2009 are partly unknown).

## Costs, prices, statistics (all cells)
- A4 baskets: flib.trade unchanged (actual panel half-spreads at both fills on netted USD-pair weights; PRE: IC
  2016-17 median spread by NY minute; 0.6 bp commission per unit; swap per 17:00 NY rollover crossed, Wednesday x3,
  PRE with BIS rates and the rates.py markups).
- Gold: panel XAUUSD mid at 16:00 ET (IS/VAL), Dukascopy H1 XAUUSD bid close of the bar starting 15:00 ET (PRE); spread
  = half the actual spread at both fills (PRE: IC 2016-17 median XAUUSD spread by NY minute, as Amendment 1 of round
  20); commission 0.6 bp; swap per rollover = rates.swap_frac_at("XAUUSD", long) in IS/VAL, PRE = -r_USD(BIS)/360 -
  the rates.py long markup.
- mid = log price change; net = mid - spread - commission + swap; x1.5 on the spread; latency: both fills +1 minute
  (IS/VAL), +1 hour (PRE). Missing quote within 5 min (panel) or the exact H1 bar (PRE): event dropped and counted.
- t: mean / s.e. clustered by the NY date of X (one trade per date in the pooled cells).
- Placebo: the same rule on weekdays whose 16:00-16:00 window holds no decision of the 8 banks (round 20 list) and no
  U event, not on 24 Dec - 1 Jan, not on US or UK holidays; ranks recomputed per day; weighted to the cell's
  weekday-of-X mix; event minus placebo difference with its t (the paper's test).
- Random-entry control: 1,000 seeds; each draws, per event, a random placebo day of the same era and weekday of X;
  percentile of the event mean net among seeds.
- Mid and net by era (PRE, IS, VAL) and by year; VAL/IS ratio; per-event net Sharpe; power = Sharpe x
  sqrt(expected HOLD events = VAL events / 3 x 1.73) on the IS and on the VAL size; expected HOLD t on the VAL size.
- C3 daily and monthly P&L correlation (by exit date, IS + VAL) for any cell with net > 0 in IS and VAL.
- Chance: 8 cells; the expected max |t| of 8 independent normals is ~1.4 (95th pct ~2.7); a sign-flip-by-date null
  over the 8 cells (IS mid) is also reported.

## Bars (unchanged)
LIVE: IS t >= 2.5, VAL >= 1.5, >= 2/3 years net > 0, random >= 95 %, power >= 3. DEMO: IS t >= 2.0, VAL net > 0,
random >= 90 %. Net > 0 also at x1.5 and +1 min. If a cell meets either on IS/VAL: PREREG_DRAFT_U_<name>.md with the
expected HOLD t on the VAL size; HOLD is not opened.
