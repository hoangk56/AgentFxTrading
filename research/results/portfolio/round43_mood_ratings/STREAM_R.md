# Round 43 stream R: sovereign credit-rating actions -> index CFDs and currencies

Written 2026-10-30 (`date -u` 05:36 UTC when grading finished). Hypotheses, sides, legs, clocks and power arithmetic
were declared in HYPOTHESES_R.md at 05:30 UTC, before any return. Data pull: 34 requests, ~3 minutes. HOLD stayed
closed: every rating row after 2024-12-31 is dropped at parse, and every price series is cut below 2025-01-01 at load.
**Verdict: no LIVE, no DEMO, no PREREG_DRAFT.**

## Sources
- **Used:** countryeconomy.com/ratings/<country>, 22 sovereigns (IT ES FR DE UK JP US AU HK CN MX CA NZ CH NO SE SG PT
  GR IE CY SI). It is a free compiled history of Moody's, S&P and Fitch long-term foreign-currency ratings and outlooks,
  dated to the day. No login is needed. Its terms do not forbid automated access, and robots.txt allows `/ratings/` for
  `User-agent: *`. The site blocks AI indexing and training crawlers by name and explicitly allows user-triggered
  agents. We fetched 24 pages under the `*` rules, at least 2 s apart.
- **Checks against known actions (passed):** S&P UK AAA -> AA on 2016-06-27; Moody's UK Aaa -> Aa1 on 2013-02-22;
  Fitch UK AA+ -> AA on 2016-06-27; Moody's US outlook to negative on 2023-11-10; S&P France AA -> AA- on 2024-05-31;
  Moody's France Aa2 -> Aa3 on 2024-12-14.
- **Check failed:** Fitch US AAA -> AA+ on 2023-08-01 is missing. Fitch coverage ends around 2020 for most countries.
  We therefore built the action families from **Moody's + S&P only**, and used Fitch only for the EU review-calendar
  family B (2014-20, which has no VAL). S&P lists only changes. Moody's lists changes and some periodic reviews.
- **Unusable:**
  - disclosure.spglobal.com: 403, including robots.txt.
  - The SEC 17g-7(b) rating-history pages of Fitch and Moody's: JavaScript apps with no static file links.
  - dt.mef.gov.it: 403.
  - EU sovereign rating calendars of the agencies for 2022-24: on the same blocked or JavaScript sites. No free copy
    was reachable, so non-action review dates exist only for Fitch 2014-20.
- **Disclosure:** the first probe printed the flattened text of the Italy page. That text included 2025-26 rating rows
  (Moody's 2025-05 and 2025-11, S&P 2025-04 and 2026-01), seen before the parse cut was written. No 2025-26 price or
  return was loaded or seen.

## Event list
- 22 countries, Moody's + S&P, from 2004.
- The direction of an event comes from the rating notch first, then from the outlook score. "Under Review" counts in
  the direction implied by the previous outlook.
- Events with the same country and direction within 3 days are merged.
- Counts after merging: PRE 102 NEG / 69 POS; IS 31 / 58; VAL 13 / 33. About 70 % are periphery or EM sovereigns
  without an IC index.
- Downgrades plus negative outlooks run at about 4.5 a year.
- **Entry rule:** an action is assumed known only by D+1 05:00 UTC. Entry is on the first weekday after D, at London
  08:05, NY 09:35 or 06:05 UTC depending on the symbol. Exit is at the same clock k = 1, 2 or 4 weekdays later, capped
  at 120 h.
- **Costs:**
  - IC bid / ask at the minute. The four new euro indices use round 7's published spreads.
  - FX pays the 0.6 bp commission.
  - Swap from rates.py where modelled; placeholders for EM FX.
  - PRE uses Dukascopy bid with IC's 2016-17 spread + 0.6 bp, FX legs only.
- Random control: 200 seeds per leg, drawn from the same era, same weekday, same side and same k.

## Results (net bp per leg, day-clustered t)
| hypothesis | PRE net (t) | mid IS / VAL | net IS (t) | net VAL (t) | per-trade SR IS / VAL | power at IS / VAL size | random pct IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| A1 NEG -> short index k1 | - | +23.3 / -21.2 | +18.6 (0.62) n23 | -23.9 (-0.67) n11 | 0.13 / -0.20 | 0.33 / -0.51 | 0.90 / 0.28 | none |
| A1 k2 | - | +29.2 / -27.0 | +23.3 (0.57) | -29.9 (-0.54) | 0.12 / -0.16 | 0.31 / -0.41 | 0.85 / 0.29 | none |
| A1 k4 | - | +47.4 / -24.9 | +40.2 (0.57) | -28.2 (-0.41) | 0.12 / -0.12 | 0.30 / -0.31 | 0.87 / 0.34 | none |
| A2 NEG -> sell currency k1 | -24.6 (-3.09) n97 | +31.5 / -13.3 | +29.4 (1.68) n25 | -14.6 (-0.79) n12 | 0.34 / -0.23 | 0.89 / -0.60 | 1.00 / 0.12 | none |
| A2 k2 | -23.7 (-1.94) | +6.7 / -23.5 | +4.0 (0.16) | -25.2 (-0.79) | 0.03 / -0.23 | 0.08 / -0.60 | 0.68 / 0.12 | none |
| A2 k4 | -34.5 (-2.02) | +17.0 / -21.1 | +13.2 (0.39) | -23.5 (-0.88) | 0.08 / -0.25 | 0.21 / -0.67 | 0.73 / 0.22 | none |
| A3 POS -> long index k1 | - | +7.9 / -8.9 | +2.8 (0.17) n13 | -14.1 (-1.88) n5 | 0.05 / -0.84 | 0.08 / -1.43 | 0.55 / 0.36 | none |
| A3 k2 | - | -8.0 / +11.0 | -14.4 (-0.38) | +3.6 (0.09) | -0.11 / 0.04 | -0.19 / 0.07 | 0.34 / 0.55 | none |
| A3 k4 | - | +3.2 / -14.8 | -5.9 (-0.09) | -26.8 (-0.36) | -0.03 / -0.16 | -0.05 / -0.27 | 0.47 / 0.39 | none |
| A4 POS -> buy currency k1 | -0.4 (-0.05) n58 | +7.6 / +12.1 | +6.2 (1.20) n58 | +10.7 (1.08) n33 | 0.18 / 0.22 | 0.78 / 0.94 | 0.77 / 0.93 | none |
| A4 k2 | -6.4 (-0.75) | +0.1 / -7.8 | -2.1 (-0.30) | -9.8 (-0.94) | -0.04 / -0.17 | -0.18 / -0.75 | 0.46 / 0.36 | none |
| A4 k4 | +1.2 (0.12) | +2.4 / -11.7 | -2.2 (-0.17) | -16.3 (-1.02) | -0.02 / -0.19 | -0.11 / -0.82 | 0.55 / 0.29 | none |
| A5 periphery -> STOXX50 + EURUSD, signed, k1 | -15.9 (-2.47) n129 | +11.5 / +1.4 | +8.0 (0.98) n110 | -2.1 (-0.18) n64 | 0.09 / -0.03 | 0.57 / -0.16 | 0.77 / 0.51 | none |
| A5 k2 | -15.7 (-1.76) | +13.7 / -27.3 | +9.2 (0.78) | -32.1 (-2.12) | 0.08 / -0.32 | 0.48 / -1.97 | 0.77 / 0.02 | none |
| A5 k4 | -20.3 (-1.69) | +0.1 / -16.4 | -6.8 (-0.30) | -24.6 (-1.28) | -0.04 / -0.20 | -0.22 / -1.24 | 0.42 / 0.17 | none |
| A6 book, all legs signed, k4 (primary) | -21.1 (-2.09) n155 | +7.3 / -16.6 | +0.6 (0.03) n174 | -23.7 (-1.36) n93 | 0.00 / -0.18 | 0.02 / -1.29 | 0.62 / 0.13 | none |
| A6s rating changes only k4 | -27.1 (-1.66) | +47.1 / -7.3 | +40.2 (1.85) n83 | -14.9 (-0.55) n31 | 0.24 / -0.12 | 0.99 / -0.49 | 0.99 / 0.30 | none |
| A6s outlook changes only k4 | -10.6 (-0.85) | -28.9 / -21.2 | -35.5 (-1.19) n91 | -28.1 (-1.30) n62 | -0.15 / -0.20 | -0.92 / -1.22 | 0.03 / 0.11 | none |
| D0 diagnostic: same clock on D -> entry, index (not tradable) | - | -8.5 / -15.7 | (mid only) | | | | | no reaction |
| D0 diagnostic, currency | +11.2 mid (1.56) | +1.0 / +3.2 | (mid only) | | | | | no reaction |
| B1 pre-review drift, Fitch EU calendar, by outlook in force (Mon 08:05 -> Fri 16:25 London) | -55.6 (-1.91) n15 | -35.9 / - | -41.5 (-1.10) n62 | no VAL | -0.17 | -0.73 | 0.06 | none |
| B2 relief after non-action, k1 | +15.6 (0.81) n10 | -27.1 / - | -30.1 (-1.95) n40 | no VAL | -0.34 | -1.15 | 0.01 | none |
| B2 k2 | +10.6 (0.66) | -11.4 / - | -15.2 (-1.11) | no VAL | -0.18 | -0.63 | 0.23 | none |
| B2 k4 | +20.2 (0.80) | -22.7 / - | -28.5 (-1.12) | no VAL | -0.20 | -0.69 | 0.20 | none |

How to read the table:
- **Power** = per-trade SR x sqrt(expected HOLD trades), where HOLD trades = VAL trades / 3 x 1.73.
- **x1.5 spread and +1 minute** change no verdict: x1.5 moves each cell by at most 1.8 bp, +1 minute by at most
  4.3 bp.
- **Results excluding 2020-03/04:** several IS cells move (A1 k4 +40 -> +58, A6 +0.6 -> +8.6, B1 -41.5 -> -4.5), but
  the best IS t without those months is 1.52 (A6s rating-only). VAL contains no 2020.

## Cells and chance
- 25 graded cells: 18 in A1-A5, 3 in A6, 4 in B.
- The best IS net |t| is 1.95 (B2 k1, wrong sign), then 1.85 (A6s rating-only) and 1.68 (A2 k1).
- Max |t| of 25 independent normals: median 2.21, 95th percentile 3.11. Everything is inside chance.
- No cell meets the DEMO bar. DEMO needs IS t >= 2.0 with net > 0 in VAL; every IS-positive cell turns negative in VAL
  except A4 k1, whose IS t is only 1.20.

## Reading
- **Sign flips across eras.** Cells that are positive in IS (A1, A2 k1, A5, A6s rating-only) are negative in both PRE
  (2004-15, mostly euro-crisis periphery) and VAL. The clearest case: "sell the currency after a downgrade" lost
  -24.6 bp (t -3.09) in PRE, made +29.4 (t 1.68) in IS, and lost -14.6 in VAL. The PRE reversal is a post-hoc
  observation and is not registered.
- **No drift after the announcement.** Measured from the same clock before the action to the first tradable clock
  after it (D0), the price does not move in the direction of the action at mid in any era. This fits round 25: dated
  public information is priced before or at release. For developed-market indices a sovereign action is old news.
- **Mechanism failure.** Rating-constrained holders do not leave a 1-5 day footprint in IC's index CFDs or G10 FX.
  Most actions hit periphery or EM sovereigns whose own markets IC does not carry, and the spillover to STOXX50 /
  EURUSD (A5) is not there.
- **Review calendar.** Neither positioning into Fitch EU review dates (B1) nor relief after a non-action (B2) works
  in IS. Both are negative and fall at or below the 6th random percentile.
- **Power ceiling.** Even at the best IS cell's size, power is <= 1.0, against the 3 that LIVE needs. As declared, LIVE
  was out of reach by count alone: about 8 NEG events, or about 30 event dates over all legs, would fall in HOLD.

## Pitfalls
- Release dates in the source are a mix of local, EU and NY dates. Examples: Moody's France 2024-12-14 (Saturday) for
  a Friday-night NY release, and S&P New Zealand 2021-02-21 (Sunday).
- Timing used here: an action counts as known by D+1 05:00 UTC, and Asian legs enter at 06:05 UTC.
- countryeconomy's Fitch tables include many non-calendar rows before 2014. From 2014 the Fitch rows for EU sovereigns
  are 2 Fridays a year per country, which is the calendar.
- Moody's "Under Review" carries no direction in the source; infer it from the previous outlook.

## Directions that need the user
- The agencies' SEC 17g-7(b) XBRL rating histories: a complete Fitch history including affirmations, and every agency's
  EU calendar dates for VAL. These are free in principle but sit behind JavaScript apps or click-through pages
  (S&P 403). Value: LIVE < 1 %, DEMO ~1 %, because the count caps power below 1.5 whatever the source.
- IC CFDs on EM / periphery equity indices or local bonds. The rated assets themselves are where the literature finds
  effects. Value: ~1-2 % DEMO.
- Paid timestamped rating feeds (Bloomberg RATC, agency terminals) would fix the release-time ambiguity. Value: < 1 %.

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r43/R/scripts/`
  - parse.py: source -> events.csv, with the HOLD cut at parse.
  - tables.py: daily clock bid / ask tables, cut at load.
  - grade.py: families A and D0.
  - gradeB.py: family B.
  - fetch.py: polite fetcher.
- Outputs: `.../r43/R/out/` (events.csv, tab_*.npz, grade_A.json, grade_B.json, gradeA.log, gradeB.log).
- Downloads: `.../r43/R/web/`. The request log is web/requests.log.
