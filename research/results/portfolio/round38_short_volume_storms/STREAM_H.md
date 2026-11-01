# Round 38, stream H: Atlantic storms and dated physical supply disruptions -> XNG, XTI, XBR

Written 2026-10-29 (after `date -u` 11:25 UTC). Hypotheses: [HYPOTHESES_H.md](HYPOTHESES_H.md), written at 11:11 UTC
before any return. HOLD was kept closed:
- HURDAT2 is the file through 2024;
- no a-deck after 2024 was requested;
- EIA series are cut at 2024-12-31;
- IC M1 is cut at ts < 2025-01-01.

No 2025-26 value was printed.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

The count decides the ceiling before any return:
- **Events per year.** 2.0 storms a year reach the Gulf production box in 1995-2015, and 2.8 in 2016-24.
- **IC-era sample.** First official forecast threats: 19 in IS 2018-21, 4 in VAL 2022-24; about 5 expected in HOLD.
- **LIVE is impossible.** It needs a per-event Sharpe of 1.34.
- **DEMO** needs IS t >= 2 on 19 storm clusters, which takes a per-event Sharpe of ~0.5.

**Storm results (30 declared cells, sides fixed).**
- **Crude long after the first threat.** Right sign in IS but weak: best net t +1.53, XBR 24 h after a forecast
  hurricane. It is strongly negative in VAL (4 storms, -50 to -150 bp) and negative in PRE 1995-2017 on EIA
  settlements (WTI -7 to -63 bp over 1-5 d, Brent spot -55 to -83 bp).
- **Gas.**
  - IS 2018-21: gas *rose* after the first threat (declared short: mid -170 bp, t -3.29 at 24 h).
  - PRE 1995-2009 (production era, declared long): gas *fell* after the first threat (-114 bp at 1 d, t -1.83; -236 bp,
    t -2.64 after a forecast hurricane).
  - So the sign flips between eras against the mechanism in both. The largest |t| (3.29 mid) is inside the sign-flip
    null of the 30 cells (p 0.077).
- **All-clear unwind (H2) and advisory-to-advisory revisions (H3).** Flat; best net t +0.10 in IS.
- **Dated official disruptions outside storms (family D).** 6 events in the IC era; descriptive only.
  - Mixed signs.
  - Abqaiq 2019: entry at the Sunday open came after the gap, and XBR then fell 7.4 % in 72 h.
- **Nuclear outages -> gas (family N).** Not buildable: nrc.gov answered 403, and EIA's outage data needs the keyed
  API.

## Sources
| source | fetched | span used | status |
|---|---|---|---|
| NHC HURDAT2 `hurdat2-1851-2024-040425.txt` | nhc.noaa.gov/data/hurdat/ | 1995-2024 | usable. Newer files (2025 season) were not downloaded. |
| NHC ATCF a-decks `aal<NN><YYYY>.dat.gz` | ftp.nhc.noaa.gov/atcf/archive/<YYYY>/ | 190 storms 1995-2024 (any fix west of 80W, 15-32N) | **usable**: `OFCL` track and intensity per synoptic time. Public issue = DTG + 3 h. No storm lacked OFCL. |
| EIA daily NYMEX futures contract 1 / 2 (RCLC1/2, RNGC1/2), Brent spot RBRTE | eia.gov LeafHandler / `rngc1d.htm` pages (HTML tables) | 1995-2017 for PRE | usable. The futures series stop at 2024-04. Roll handling uses CME expiry rules; a check on large-spread days matched the true roll on 83 % (CL) / 68 % (NG) of expiry days. |
| IC M1 XBR, XTI, XNG, USDCAD, US500 | research/data/m1 | 2018-01..2024-12 | usable. Median spreads: XTI 4.3 bp, XBR 4.0, XNG 31 bp. |
| BSEE shut-in statistics | bsee.gov | - | **unusable**: the newsroom answers 403, and releases are unindexed PDFs (one WebSearch confirmed). |
| NRC Power Reactor Status | nrc.gov | - | **unreachable**: 403 twice. |
| EIA nuclear outages | eia.gov/nuclear/outages | - | data only through the keyed API (needs an account). |

- Requests: 206 in total (191 to ftp.nhc.noaa.gov at >= 1.5 s apart; all others >= 1.2 s apart), logged in
  `web/requests.log`.
- WebSearch: 3 of 25.
- Browser User-Agent; no personal data in any request.

## Events (data only)
- **Production box P:** 25.5-30.0N, 87.0-95.5W.
- **LNG zone:** within 200 km of Sabine Pass, Cameron, Calcasieu Pass, Freeport, Corpus Christi.
- **Triggers:**
  - T1 = the first OFCL advisory with a forecast point (tau 0-72, >= 34 kt) in P;
  - T1H = the same with >= 64 kt;
  - T1L = >= 34 kt in the LNG zone;
  - T2 = the first advisory after T1 with no point in P;
  - H3 = |change| >= 1 in the wind-weighted count of P points between successive advisories.

| era | T1 | T1H | T1L | T2 | H3 |
|---|---|---|---|---|---|
| IS 2018-21 | 19 (2018 3, 2019 4, 2020 8, 2021 4) | 10 | 12 | 16 | 42 |
| VAL 2022-24 | 4 (2022 0, 2023 1, 2024 3) | 3 | 3 | 4 | 9 |
| PRE 1995-2017 (EIA) | 60 | 27 | - | 56 | - |

No event falls in 2020-03/04, so the "without the Covid crash" variant is identical.

## Costs and fills
- **Entry.** The first IC minute >= advisory issue + 1 minute, at its close (bid / ask close). Weekend advisories fill
  at the Sunday open.
- **Exit.** The same clock 24 / 72 / 120 h later, or the first quote after it.
- **Cost.** Half spread at entry + half at exit. Swap per 17:00 New York crossing (Friday x3): energies -2.5 bp, XNG
  -4, US500 -2, USDCAD -0.5. Commission 0.
- **Variants.** Spread x1.5, and both legs +1 minute.
- **Random control.** 1,000 draws of the same n from the advisory clocks (03 / 09 / 15 / 21 UTC) on June-November days
  of the same years. Days within a storm's T1-1 d..T2+1 d window are excluded. Same side and hold.
- **PRE.** Gross; settlement to settlement on EIA daily data, entering at the first settlement after issue.

## Results table (IS / VAL; net bp with t; storms are the units)
| hypothesis | eras | mid IS (t) | cost IS | net IS (t) / VAL (t) | VAL / IS | SR IS, power IS (HOLD n 5) | random IS | PRE (gross, t) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| H1 T1 XBR long 24 h | IS 19 / VAL 4 | +56.5 (1.64) | 9.8 | +46.7 (1.36) / -58.7 (-1.25) | < 0 | 0.31, 0.70 | 0.88 | Brent spot 1 d -55.5 (-1.59) | none |
| H1 T1 XBR long 72 h | | +94.2 (1.27) | 14.4 | +79.7 (1.08) / -148.9 (-5.87) | < 0 | 0.25, 0.55 | 0.92 | 3 d -83.2 (-1.17) | none |
| H1 T1 XTI long 24 / 72 h | | +35.5 / +77.4 (0.93 / 0.90) | 9.7 / 14.5 | +25.8 (0.67) / -53.2; +63.0 (0.73) / -155.2 (-5.15) | < 0 | 0.16 / 0.17, < 0.4 | 0.73 / 0.84 | WTI 1 d -7.5 (-0.30), 3 d -63.3 (-1.40) | none |
| H1 T1H XBR long 24 h (best IS cell) | IS 10 / VAL 3 | +79.7 (1.75) | 9.7 | +70.1 (1.53) / -52.8 (-0.80) | < 0 | 0.48, 1.08 | 0.89 | +8.9 (0.19) | none |
| H1 T1 XNG short 24 h | IS 19 / VAL 4 | -170.3 (-3.29) | 36.7 | -207.0 (-3.98) / -26.4 (-0.16) | - | -0.91 | 0.02 (worse than random) | declared long 1995-2009: -114.3 (-1.83) | none (sign flips by era) |
| H1 T1 XNG short 72 / 120 h | | -75.4 / -149.8 | 46 / 57 | -121 (-1.37) / -175; -206 (-1.41) / -412 (-2.92) | - | < 0 | 0.42 / 0.27 | -80.6 / -25.0 | none |
| H1 T1H XNG short 24 h | IS 10 / VAL 3 | -232.1 (-2.82) | 35.0 | -267.1 (-3.20) / -89.2 | - | < 0 | 0.03 | declared long: -236.3 (-2.64) | none |
| H1 T1L XNG short 24 / 72 / 120 h | IS 12 / VAL 3 | -154 / -275 / -388 | 37-52 | -191 (-2.19) / +208 (3.06); -320 (-1.71); -440 (-2.22) | - | < 0 | 0.05-0.06 | - | none |
| H2 T2 crude short / XNG long 24 / 72 h (6 cells) | IS 16 / VAL 4 | -160..+23 | 8-48 | best +8.6 (0.10); XNG 24 h -195.5 (-2.01) | - | <= 0.03 | - | WTI short 3 d +77.8 (1.55), NG -0.6..-109 | none |
| H3 revisions, 6 h (3 cells) | IS 42 / VAL 9 | -17..+12.5 | 7-30 | best XTI +4.9 (0.31) / +22.8 (0.52) | 4.7 | 0.05 | - | - | none |
| storm book +XBR +XTI -XNG per storm, 24 / 72 / 120 h | IS 19 / VAL 4 | - | - | -44.8 (-1.59) / -46.1; +7.1 (0.12) / -159.6 (-3.45); -85.5 / -200.7 | - | <= 0.03 | - | - | none |
| controls T1: USDCAD short / US500 long | IS 19 / VAL 4 | USDCAD -12..-19; US500 -15..+3 | 4-14 | USDCAD -16.8 (-2.28) at 24 h; US500 ~0 IS, +92..+230 VAL | - | - | - | - | no grade (controls) |

Notes:
- **XNG cells.** For a short-side cell, mid < 0 means gas rose. Gas rose after T1 in every IS year (24 h mean, signed for
  the short: 2018 -64, 2019 -21, 2020 -243, 2021 -255 bp); 2020-21 carry most of it. It also rose in the 24 h *before*
  T1 (-86.7 bp signed, t -0.99). In the PRE production era it fell after T1.
- **Flipped gas side.** Flipping the gas side on these IS numbers would be choosing the side on IS. It would also face
  a PRE with the opposite sign (when the declared mechanism was bullish) and a VAL n of 4 that is negative for the flip
  (mid +31.7 bp for the short at 24 h). It is not a candidate.
- **Crude.** Crude is right-signed only in IS, and 2020 carries it (8 storms, +91 bp mean for XBR at 24 h).
- **Pre-advisory move.** Crude was flat over the 24 h before T1 (XBR +8.4, XTI -4.4 bp). There is no sign of a priced
  threat premium for an unwind to harvest.

## Cells tried and chance benchmark
- **H family.** 30 cells: H1 21 (T1 / T1H x 3 products x 3 holds + T1L x 3), H2 6, H3 3. Plus 6 control cells, not
  graded.
- **Sign-flip null.** Signs flipped by storm, shared across cells, 2,000 draws.
  - Max |IS net t|: observed 3.98, which is the wrong-side XNG short with the cost drag included; null median 2.26,
    95 % 3.50, p 0.022.
  - The same null on mid: observed 3.29, null median 2.18, 95 % 3.54, **p 0.077**.
- **Best right-signed IS cell.** t +1.53, below the null median of 2.2.
- **Family D.** 8 legs; descriptive, not graded. **Family N:** 0 cells (no data).

## Family D: dated official disruptions, IC era (descriptive, net bp)
| event (entry) | leg | 24 h | 72 h | 120 h |
|---|---|---|---|---|
| Abqaiq attack 2019-09-14 (Sun open) | XBR long | -51 | -755 | -564 |
| | XTI long | +75 | -522 | -394 |
| Keystone shut 2019-10-29 (next day 13:00 UTC) | XTI long | -205 | +165 | +231 |
| Colonial shut 2021-05-07 (Sun open; crude side unsigned) | XTI long | -44 | +73 | +12 |
| | XBR long | -58 | +10 | -23 |
| Freeport LNG explosion 2022-06-08 (next day 13:00) | XNG short | -510 | -573 | -328 |
| Freeport outage extended 2022-06-14 (next day 13:00) | XNG short | -459 | +881 | +1003 |
| Keystone shut 2022-12-07 (next day 13:00) | XTI long | -373 | -410 | -150 |

About 1 event a year; DEMO would need a per-event Sharpe > 1. The first tradable minute after the news already holds
the repricing (Abqaiq's Monday gap; Freeport's first day).

## Why this row cannot carry a LIVE rule
- **The independent unit is the storm.** Advisories every 6 h do not multiply n: H3 has 42 IS advisories from 9 storms,
  and its 6 h moves are noise against XNG's 30-60 bp round trip.
- **Count.** A rule needs >= ~100 independent events a year at a per-trade Sharpe ~0.23 for LIVE. Gulf storms give ~3,
  and official non-storm disruptions ~1.
- **Pooling.** Pooling products does not help: crude legs move together, and gas changes sign by era.
- **Swap.** Multi-day holds cost 7-20 bp on crude and 17-30 bp on XNG; this is small next to the 100-400 bp event sd.

## Directions that need the user
| direction | value |
|---|---|
| EIA API key (free registration = an account): daily nuclear outages 2007-24 for a gas-burn rule with ~20-40 days a year | DEMO ~2 %, LIVE < 1 % (market watches NRC data at 10:00 ET; effect ~1 GW = ~0.2 % of US gas demand) |
| BSEE shut-in history (manual collection of release PDFs) | < 1 %: conditioning only, the count stays ~3 storms a year |
| Paid storm-model data (ECMWF / GFS ensemble tracks, issue times) to test whether markets move on model runs before NHC | < 1 %: it would explain the priced-before result, not create a tradable count |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r38/H/scripts/`:
  - `fetch.py`, `pull_adeck.py`: downloads;
  - `hurdat.py`: counts and boxes;
  - `events.py`: triggers;
  - `eia.py`, `pre.py`, `rollcheck.py`: PRE;
  - `ic_events.py`, `grade.py`: IC cells and the random control;
  - `nulls.py`: sign-flip null and pre-advisory diagnostic;
  - `family_d.py`.
- Outputs: `.../r38/H/out/`:
  - `grade.txt`, `pre.txt`, `nulls.txt`, `family_d.txt`;
  - `events.json`: triggers to 2024 only.
