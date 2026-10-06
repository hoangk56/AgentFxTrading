# Round 20, stream F: carry on central-bank decision days (declared before any return)

Written 2026-10-06 04:03 UTC (`date -u` gave 04:02:58), before any stream-F return, mean or t was computed. Only
data layouts were inspected (panel meta, Dukascopy H1 field names, calendar fields, rate-file date ranges). HOLD
(2025-01-01 onwards) is never loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, rates used for ranks and
swaps are cut at 2024-12-31, C3 trades are filtered to IS + VAL.

## Source: Mueller, Tahbaz-Salehi & Vedolin (2017), JF 72(3) 1213-1252, doi 10.1111/jofi.12499

Full text: published version at kellogg.northwestern.edu/faculty/alirezat/FXAnnouncements.pdf (also SRC DP 54, LSE).
What the paper does, exactly:
- Data 1994-2013, Olsen 5-min mid quotes; 9 currencies vs USD: AUD CAD CHF EUR GBP JPY NOK NZD SEK. 160 scheduled
  FOMC days (10 unscheduled excluded), 4,512 other days.
- Day = **4 pm ET to 4 pm ET**; announcement day = the 4 pm-4 pm day containing the ~2:15 pm ET statement.
- Excess return = log spot change + interest differential accrued linearly (one-month forward discount); almost all of
  the announcement-day return is the spot change ("s" in Table I).
- Portfolios: at the end of each month, sort the 9 currencies on the forward discount (= interest differential vs
  USD) into 3 equal-weight portfolios of 3; pf1 lowest, pf3 highest rates; **dol** = long all 9 vs USD.
- Reported sizes (Table II, 160 FOMC days): pf1 +5.19 bp (t 1.06), pf2 +12.66, **pf3 +14.47 bp (t 2.49, annualised
  Sharpe 0.556 = 0.197 per event)**, dol +10.77 (t 2.27); non-announcement days pf3 +1.73, dol +0.47. Difference
  pf3 +12.74 (t 2.45), dol +10.30 (t 2.55). The split (Table IV): pf3 +9.48 bp from 4 pm to 2:15 pm, +3.24 after.
- S1/S2 (Table VII): long all at 4 pm the day before; after the statement keep it on easing, reverse on tightening
  (needs the Nakamura-Steinsson futures-based policy indicator); S2 = only currencies with a positive differential vs
  USD: +22.5 bp (t 4.17).
- Other banks (Section III.D, 1998-2013): rebase to the announcing currency, sort the others on the differential vs
  it. **BoJ: pf3 +17.59 bp (t 2.76), "jpy" (long all vs JPY) +14.70 (t 2.60) on 232 days. RBA, BoE, RBNZ, SNB: "no
  significant effects"** (BoC, Norges, Riksbank, ECB not tested for history reasons).
- Mechanism: financiers who are short the low-rate (funding) currency face uncertainty about its rate; on the
  decision day they need a premium, which accrues to the high-rate side and grows with the differential
  (Propositions 1-2).

Prior from the paper alone (power arithmetic, before data): if pf3's per-event Sharpe were the paper's 0.197, IS (48
FOMC days) would give an expected t of 1.36 and VAL (24 days) 0.97; HOLD (~14 days) 0.73. LIVE is out of reach for
the FOMC family whatever the data say (power <= 0.8); DEMO needs IS t >= 2.0, i.e. a per-event Sharpe ~1.5x the
paper's. The pooled secondary has ~62 events a year (power reachable only if the per-event Sharpe is >= 0.29). The
paper's sample ends 2013 and was public from 2014-15; PRE 2004-13 overlaps the paper's own sample (a replication of
our construction, not an out-of-sample check); 2014-24 is post-sample. Related literature (Kurov, Wolfe & Gilbert
2021, the pre-FOMC equity drift disappeared after 2015) is a reason to expect a smaller effect after publication.

## Data
- IS 2016-21 and VAL 2022-24: round-12 panel (mid = (bid close + ask close)/2 at the minute, spr = ask - bid at the
  minute's last tick). Pairs: EURUSD GBPUSD AUDUSD NZDUSD USDJPY USDCAD USDCHF (the 7 currencies IC quotes vs USD;
  NOK and SEK are not in the data, so the universe is 8 currencies incl. USD).
- PRE 2004-15: Dukascopy H1 bid (bar-start labels) for the same 7 pairs; price at 16:00 ET = close of the H1 bar
  starting at 15:00 ET (bid; the early ask is not used).
- Rates for ranking:
  - 2016-24: research/data/rates/ (FRED; they cover 2014-01..2026 only): USD DFF (daily effective fed funds), EUR
    ECBDFR (daily deposit rate), GBP IUDSOIA (daily SONIA), JPY / AUD / CAD IRSTCI01*M156N (monthly call/overnight
    rates), CHF IR3TIB01CHM156N and NZD IR3TIB01NZM156N (monthly 3-month interbank).
  - PRE 2004-15: the local files do not cover it, so BIS central-bank policy rates (WS_CBPOL, daily, US XM GB JP AU
    CA CH NZ), downloaded 2026-10-06 from stats.bis.org for 2003-01..2016-01 (rates, not prices) to
    scratchpad r20/F/rates_pre/. CHF before the 2019 SNB policy rate = BIS's representative rate (3M LIBOR target
    midpoint).
  - Causal rank: for a trade whose entry falls in month M, each currency's rate = the last daily value dated before
    the first day of M, or for monthly series the observation dated M-1 (that month's average, complete when M
    starts). Ties broken by the currency order USD EUR GBP JPY AUD NZD CAD CHF.
- Calendar: r12/shared/cal/cb_calendar.json, kind = decision, scheduled = true only (unscheduled moves excluded as in
  the paper). Decision time t_d = `utc`; BoJ without a time uses the end of its window (06:30 UTC); RBA 2004-Jan
  2008 non-change meetings without an announcement (time null) are excluded.

## Window, fills, costs (all cells)
- Exit X = the first 16:00 New York time at or after t_d + 60 min on a Monday-Friday; entry E = the last 16:00 New
  York time at or before t_d - 60 min on a Monday-Friday. For FOMC (14:00/14:15 ET) this is exactly the paper's 4
  pm-to-4 pm day; for every other bank it is the 4 pm-4 pm day containing the decision (a 48-h window only when t_d is
  within an hour of 16:00 ET: some pre-2019 RBNZ days; a weekend window when the decision is on a Monday in Asia).
- Fill prices: the panel mid at the minute labelled 16:00 ET for E and X (calendar-only signal, known days ahead). In
  PRE: H1 close at 16:00 ET. Latency variant: both fills +1 minute (IS/VAL), +1 hour (PRE).
- Basket in the paper's units: a leg "long j vs k" has return log(j/k) change, computed through USD pairs; basket =
  equal-weight average of its legs (pf3 = mean of 3 legs). Execution is the netted set of USD pairs (weights summed
  per pair; a USD "leg" is not traded). Cost per basket = sum over pairs of |w| x (half spread at E + half spread at X
  + 0.6 bp commission), x1.5 variant on the spread part; IS/VAL spreads = actual panel spread at the fill minutes
  (missing minute: the nearest earlier quote within 5 min, else the event is dropped and counted); PRE spreads = the
  IC 2016-17 median spread of that pair at the same minute of the day (UTC) + 0.6 bp.
- Swap: every 17:00 New York rollover between E and X, Wednesday x3, weekends none. Per pair:
  research/swing/rates.py swap_frac_at(symbol, side, ms) in IS/VAL; in PRE (FRED files start 2014) the same formula
  with BIS rates: (r_base - r_quote)/360 - the rates.py fitted markup for that side. Swap enters net only.
- mid = spot (log) change only; net = mid - spread - commission + swap. Carry accrual (the differential / 360 per
  rollover) is reported for reference.
- t: mean / clustered s.e. by the UTC date of X (several banks on one day form one cluster).

## Cells (7 in all; no others will be judged)

Family A, FOMC (primary), scheduled FOMC statements, X = 16:00 ET on the statement day:
| cell | rule | why |
|---|---|---|
| **A1 (primary)** | **pf3: long the 3 highest-rate of the 7 currencies vs USD, equal weight** | paper's headline sorted portfolio (pf3 +14.47 bp) |
| A2 | dol: long all 7 vs USD | paper's dol (+10.77 bp) |
| A3 | HML: pf3 - pf1 (long top 3, short bottom 3; dollar-neutral) | the "carry" form of Prop. 2; paper implies +7.0 bp (12.72 - 5.69) |
| A4 | POS: long the currencies with r_j > r_USD, equal weight; no trade if none | paper's S2 without the tightening switch (the policy indicator needs fed-funds futures, which we do not have, and is known only after the statement) |
With 7 currencies, pf3 and pf1 have 3 each and pf2 has 1 (paper: 9 in 3 x 3).

Family B, pooled central banks (secondary): rationale. The paper's mechanism is not US-specific: uncertainty about
the announcing currency's short rate, borne by intermediaries in carry positions against it; Prop. 2 says the premium
rises with the differential. The paper tests 5 other banks and finds it only for the BoJ (a funding currency), so the
prior for pooling is weak; pooling gives ~8x the events and is the brief's question. The generalised rule: on bank
X's day, long the 3 currencies with the highest r_j - r_X (among the 7 other currencies, USD included) vs X, equal
weight (the paper's rebased pf3).
| cell | rule | why |
|---|---|---|
| **B1 (secondary primary)** | pf3_X on the 7 non-US banks' decision days (ECB, BoE, BoJ, BoC, RBA, RBNZ, SNB), pooled | the brief's 8-bank extension without FOMC |
| B2 | B1 + A1 pooled (all 8 banks) | the 8-bank pool |
| B3 | BoJ days only: long all 7 vs JPY ("jpy") | the paper's one non-US positive result (+14.70 bp) |

Days with two decisions: each bank's event is its own basket (B1/B2), clustered by date.

## Checks reported for every cell (no selection among them)
- Mid and net by era (PRE, IS, VAL) and by year; VAL/IS ratio; per-event net Sharpe; power = Sharpe x sqrt(expected
  HOLD events: FOMC 8/yr x 1.73 = 13.8; B1 ~54/yr x 1.73; B2 ~62/yr x 1.73; BoJ 8/yr x 1.73) on the IS and on the VAL
  size; expected HOLD t on the VAL size.
- Spread x1.5; both fills +1 minute (PRE +1 hour).
- Placebo: the same rule on non-decision days, i.e. 4 pm-4 pm windows (X Monday-Friday) with no decision of any of the
  8 banks in [E, X], X and E not on 24 Dec-1 Jan, not on a US federal or UK bank holiday; ranks recomputed at each
  day; weighted to the events' weekday-of-X mix (and the same announcing currency X for B cells). Reported: placebo
  mean and the event-minus-placebo difference with its t (the paper's test).
- Random-entry control: 1,000 seeds; each draws, for every event, a random placebo day in the same era with the same
  weekday of X (and the same X currency), computes the rule's net there; percentile of the event mean among seeds.
- Descriptive only (not cells): A1 split into E -> t_d - 5 min and t_d - 5 min -> X (the paper's pre/post).
- C3 correlation (daily and monthly P&L by exit date, IS + VAL) for any cell with net > 0 in IS and VAL.
- Multiple testing: 7 cells; the expected max |t| of 7 independent normals is ~2.0 (they are highly correlated, so
  less in practice); a sign-flip-by-date null over the 7 cells is also reported.

## Bars (unchanged)
LIVE: IS t >= 2.5, VAL >= 1.5, >= 2/3 years net > 0, random >= 95 %, power >= 3. DEMO: IS t >= 2.0, VAL net > 0,
random >= 90 %. Net > 0 also at x1.5 and +1 min. If a cell meets either on IS/VAL: PREREG_DRAFT_F_<name>.md, stop
the family, do not open HOLD.

## Amendment 1 (04:04 UTC from `date -u`, before any number)
PRE spread profile: "the IC 2016-17 median spread at the same minute of the day" is taken by **New York** minute of
the day, not UTC. By UTC minute, 21:00 UTC mixes 16:00 EST (normal) with 17:00 EDT (the rollover minute, wide) and
the median would charge a rollover spread on ordinary 16:00 ET fills. The profile is the 2016-17 median of spr / mid
for each pair over Monday-Friday minutes, keyed by NY hh:mm. The holiday filter for placebo days uses the US and GBP
lists of r12/shared/cal/holidays.json.

## Amendment 2 (04:06 UTC from `date -u`, before any return; found while checking rank inputs)
BIS has no JPY policy rate outside 2006-03-09..2013-04-03 (no rate target under the BoJ's quantitative easing of
2001-06 and QQE from April 2013). PRE fills JPY with 0.00 % before 2006-03-09 (uncollateralised call rate ~0.001 %)
and 0.05 % after 2013-04-03 (the last BIS value; the call rate stayed at 0-0.1 % under QQE). Used for ranks and PRE
swaps. Checks so far (no returns): scheduled events per bank and era as expected (FOMC PRE 96 / IS 47 / VAL 24; the
March 2020 meeting is unscheduled in the calendar), 37 RBA null-time days dropped as declared, 19 RBNZ windows are 48
h, 6 Monday-Asia windows span a weekend; placebo pool PRE 1,997 / IS 1,049 / VAL 529 days.
