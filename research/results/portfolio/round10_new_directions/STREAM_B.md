# Stream B (round 10): central-bank decisions and home-market holidays, pooled across countries

Rules: research/results/portfolio/round10_new_directions/HYPOTHESES_B.md (written 2026-10-05 17:55 UTC before any
number; addendum ~18:25 UTC on holiday-block clustering; B2r marked post hoc ~19:05 UTC). HOLD (2025+) never loaded.
Costs: actual half-spreads at entry and exit (panel), +0.6 bp FX; index swap on W24 (rates.swap_frac_at, Friday x3).
t clustered by UTC day (B3 also by holiday block). Power = per-trade net Sharpe x sqrt(trades/yr x 1.73).

**Verdict: no family reaches DEMO or LIVE; no PREREG_DRAFT.** LIVE power (>= 3) is not reachable for any of these
mechanisms on this evidence: it would need a per-event net Sharpe of 0.29 (B2, ~66 decisions/yr) to 0.39 (B1, ~35/yr);
the best observed pooled per-trade Sharpe is 0.06 (B3 IS), and every pooled cell is <= 0.04 in the other era.

## Calendar (inputs)
- calendar/cb_calendar.json: 1,877 events 2004-2024, eight banks + FOMC/RBA minutes, UTC times DST-correct, sources
  per event (calendar/sources.txt). Verified rule changes: FOMC 14:15 ET to Jan 2013 (12:30 on 2011-12 press days), 14:00
  from Mar 2013; ECB 13:45 -> 14:15 CET from 21 Jul 2022; BoC 09:00 -> 10:00 ET from Jan 2013; RBNZ 09:00 -> 14:00 NZ
  from 13 Feb 2019; RBA same-day 14:30 from Feb 2008. 48 unscheduled moves flagged and excluded.
- calendar/holidays.json: python holidays 0.105 (DE-HE, GB-ENG, CH-ZH, JP + bank days, AU-NSW, NZ-WGN, CA-ON, US
  federal + NYSE).
- Scheduled decisions 2016-24 per year: FOMC 8, ECB 8, BoE 8 (11 in 2016), BoJ 8, RBA 11 (8 in 2024), BoC 8, RBNZ 7,
  SNB 4: ~62-66 a year.

## Results (IS 2016-21 / VAL 2022-24; mid and net in bp per leg)

| hypothesis | where | n/yr | IS mid (t) | VAL mid (t) | cost | net IS (t) / VAL (t) | power IS / VAL | random | verdict |
|---|---|---|---|---|---|---|---|---|---|
| B1 W24 pre-decision drift, long (Lucca-Moench construction; Brusa-Savor-Wilson 2020 predict 0) | ECB->DE40, BoE->UK100, BoJ->JP225, RBA->AUS200 | 35 | +2.1 (0.29) | -5.8 (-0.59) | 3.2 incl. swap | -1.2 (-0.17) / -9.0 (-0.91) | -0.09 / -0.73 | 70 % / 18 % | falsified, as the literature says |
| B1 WDAY home open -> T-15 | same | 35 | +4.0 (1.07) | -1.0 (-0.17) | 1.3-2.0 | +2.0 (0.53) / -2.3 (-0.41) | 0.28 / -0.31 | 98.5 % / 42 % | fails (IS t < 2, VAL < 0) |
| B2 primary: post-decision continuation, k 15, EOD | 8 banks, FX + index (<= 3 legs) | ~100 legs, 52 days | +2.1 (0.64) | +1.1 (0.24) | 1.6 / 1.1 | +0.4 (0.14) / +0.0 (0.00) | 0.07 / 0.00 | 82 % / 54 % | fails; continuation absent |
| B2 latency +1 / spread x1.5 | same | | | | | +0.2 / -0.0; -0.2 / -0.4 | ~0 | | fails |
| B4a minutes continuation, k 15, EOD | FOMC minutes -> EURUSD/USDJPY/US500; RBA minutes -> AUDUSD/AUS200 | ~39 legs | -4.9 (-1.33) | +5.8 (1.48) | 1.4 / 0.8 | -6.2 (-1.70) / +4.9 (1.27) | -1.0 / 1.1 | 0.5 % / 63 % | fails; signs flip |
| B4a minutes, H 60 | same | | -0.2 (-0.09) | -0.7 (-0.32) | 1.2 / 0.8 | -1.4 / -1.5 | -0.5 / -0.6 | | fails |
| B3 home-holiday: long home ccy in its home hours on its holidays (Breedon-Ranaldo) | 7 USD pairs, 8 calendars | 88-99 legs, ~35 day clusters | +2.6 (1.72; block 1.79) | -1.8 (-0.71) | 1.2 / 1.0 | +1.4 (0.91; block 0.95) / -2.8 (-1.12) | 0.75 / -1.4 | 46 % (IS+VAL) | fails |
| B3 holiday minus normal day (mechanism check) | same | | +2.7 (t 1.8) | -1.6 (t -0.6) | | PRE +3.9 (t 2.4) | | | real in PRE/IS, gone in VAL |
| B2r **post hoc**: fade the first 5 min of a press conference, H 60 | IS/VAL: FOMC, ECB, BoE, RBNZ, SNB, RBA-2024 legs; PRE: ECB->EURUSD, FOMC 2011-15, SNB | ~45 legs | reversal +4.5 (1.55) | +9.8 (1.89) | 0.9 / 0.7 | +3.5 (~1.2) / +9.1 (~1.8) | ~0.7 / ~1.4 | | same sign in 3 eras (PRE +3.9, t 1.3, net +3.1, t 1.05, 8/12 yrs) but IS t < 2: below DEMO |

Per-bank B2 primary (descriptive, not judged): BoJ IS +12.7 (t 1.3, winsorised 2.3) / VAL +14.8 (t 0.8); RBNZ +14.3 /
-23.8; SNB -2.3 / +20.8; FOMC -1.3 / -3.5; ECB +1.9 / +6.0; BoE -0.9 / +3.2; RBA +1.5 / -1.4; BoC -0.3 / -3.7.
Per-bank B1 W24: ECB +11.1 / -3.1; BoE -10.1 / -9.0; BoJ +6.1 / -15.3; RBA +2.1 / +2.5. B1 WDAY BoJ +6.7 (t 1.2) /
+14.4 (t 1.9): one of 8 per-bank cells, 8 events/yr, power <= 1.3.
Per-currency B3 holiday trade: GBP IS +17.3 (t 2.3, 18 events) / VAL -16.3 (t -1.9); JPY +2.8 (1.1) / +9.6 (2.2), PRE
+4.8 (2.3) but JPY normal days VAL -3.4 (t -2.5); USD legs +1.5 / -1.2.

## Multiple testing
- B1: 10 cells (2 windows x pooled + 4 banks). Best |t| 1.99 (ECB WDAY VAL, negative); IS best 1.16. Expected max of
  10 |normals| ~1.9.
- B2: 24 registered cells. Best |t| IS 1.99, VAL 1.89; expected max of 24 |normals| 2.24; sign-flip-per-day null
  median 2.0, 95th pct 2.98. Nothing above chance. Per-bank splits (8) descriptive.
- B3: 1 primary + 8 per-currency. Best per-currency |t| 2.34 (GBP IS, flips in VAL); expected max of 9 ~1.9.
  Placebo (all currencies' windows on OTHER countries' holidays): own holidays beat 7/7 placebo calendars in PRE, 6/7 in
  IS, 3/7 in VAL. Block clustering changed little (IS 211 day clusters -> 188 blocks, t 0.91 -> 0.95).
- B4a: 2 cells. B2r: 1 post-hoc cell + 1 PRE check (2 horizons; EOD +0.2, t 0.04).

## Surprises, data and method notes
- Pre-ECB/BoE/BoJ/RBA drift is absent (consistent with Brusa, Savor & Wilson 2020); combined with round 3's FOMC
  result, there is no pooled "every central bank" premium to harvest.
- Continuation after the decision is absent at 15 min -> 1 h / EOD; if anything, the first 5 minutes of the press
  conference reverse (three eras, same sign, never significant). The 08:30-data result of rounds 3/8 extends to CB
  decisions: the jump is priced within minutes.
- The home-hours depreciation itself (normal days) is weak in 2016-24 except EUR (IS -2.1, t -2.2); JPY's home-hours
  sign flips by era. The holiday asymmetry is visible in PRE (diff +3.9, t 2.4) and IS (+2.7, t 1.8) but not VAL,
  and its size (~3 bp) is the cost (~1.1 bp) plus noise: even if real, power <= 0.75.
- BoJ real-time detection rule (6 x median 1-min |ret| in 02:00-06:30 UTC) fires early on many days (24 of 69 before
  02:15 UTC, several exactly 02:00), so some BoJ "reactions" are noise and the threshold was too loose. It affects the
  descriptive BoJ splits only; the pooled verdicts do not depend on it (BoJ is 77 of 603 IS legs). B1's BoJ exit at
  02:00 UTC may also sit after an early release on a few days.
- The calendar was rewritten by the builder after the first runs; all B1/B2 outputs were rerun on the final file
  (2016-24 identical; changes were pre-2016 only).
- Not done: B2 PRE (only registered if the primary passed); STOXX50/F40 secondary for B1 (only if primary positive);
  C3 correlation (no survivor).

## Files (scratchpad r10/B)
blib.py, build_holidays.py, b3_holidays.py, b3_blocks.py, b1_pre.py, b2_post.py, b2_control.py, b2r_pre.py;
outputs out_b1.json, out_b2.json (+ out_b2.log), out_b2_control_*.json, out_b3.json, out_b3_blocks.json,
out_b2r_pre.json, boj_detected_times.json; calendar/ (cb_calendar.json, holidays.json, sources.txt, work/ parsers).
