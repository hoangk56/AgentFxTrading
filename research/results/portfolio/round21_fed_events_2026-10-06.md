# Round 21: declared-only — the FOMC-day dollar premium on other scheduled US-policy events (2026-10-06)

Round 20 found the dollar falls on FOMC days in every era (rule A4, Mueller, Tahbaz-Salehi & Vedolin 2017) but at 8
events a year it cannot reach the bars. This round declared the same rule, unchanged, on the other scheduled
US-policy events to raise the count ([round21_fed_events/BRIEF.md](round21_fed_events/BRIEF.md);
[HYPOTHESES_U.md](round21_fed_events/HYPOTHESES_U.md) at 04:31 UTC, first return 04:32;
[STREAM_U.md](round21_fed_events/STREAM_U.md)).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** The premium is specific to the FOMC decision,
as the literature says (Mueller et al. 2017 find none on payroll / CPI / PPI days; Bauer, Lakdawala & Mueller 2022
find that only FOMC announcements resolve short-rate uncertainty).

| cell (8 declared) | n PRE / IS / VAL | net PRE / IS (t) / VAL (t), bp per event | verdict |
|---|---|---|---|
| U1 FOMC minutes | 95 / 39 / 24 | -4.4 / +2.3 (0.32) / -16.6 (-1.19) | fails |
| U2 Chair's semiannual testimony | 24 / 10 / 6 | +8.6 / +7.1 (0.50) / +8.3 (0.27) | fails (IS t) |
| U3 Jackson Hole Chair speech | 7 / 5 / 3 | +5.9 / +33.9 (1.21) / -2.3 | fails |
| U4 Treasury quarterly refunding statement | 35 / 11 / 4 | -8.7 / +10.6 (0.48) / -18.3 | fails |
| **U5 primary: U1-U4 pooled** | 161 / 65 / 37 | -3.0 / +6.9 (1.07) / -11.6 (-0.96) | fails |
| U6: U5 + FOMC | 257 / 102 / 60 | +4.4 / +12.2 (2.10) / +5.0 (0.53) | fails DEMO: the IS t comes from the FOMC days round 20 already measured; random-entry VAL 83 % |
| G1 / G2: long gold over the U5 / U6 windows | | +5.6 / +1.4 / -12.1; +5.6 / +10.4 (1.27) / +9.7 | fail |

- Calendars 2004-24 from official sources (federalreserve.gov testimony / speech / minutes pages and JSON, the
  Treasury's refunding press releases); non-FOMC windows containing an FOMC decision excluded (33 refunding Wednesdays).
- Chance: best IS net t 2.10 (U6) against a max-of-8 95th percentile of 2.72.
- C3 correlation of the cells net > 0 in IS and VAL: about 0 daily, -0.12 to -0.18 monthly.
- Information only: gold also rises on FOMC days (PRE +5.8, IS +24.8 t 1.85, VAL +42.4 t 2.05), the same shape and the
  same 8-a-year limit as the dollar result; testimony is the only other type > 0 in all three eras, at t <= 0.8.
- Caveat for any A4-type rule: it trades only when some currency's rate is above USD's (none in 2018-09..2019-10).

## What this says
The policy-uncertainty premium is a property of the FOMC decision alone; it cannot be multiplied across other Fed
events. The FOMC-day dollar (and gold) effect stays a durable, literature-backed effect of 8 events a year: never LIVE,
below DEMO's IS t. Its options are the user's (round 20).

## Process and disclosures
HOLD not loaded (panel, Dukascopy, calendars, rates all cut before 2025; C3 trades filtered to IS+VAL). The stream's
final message was lost to a session rate limit after it had written its files; the lead read the files directly.
Scripts in the scratchpad (`r21/U`). Nothing in `research/` code was edited.
