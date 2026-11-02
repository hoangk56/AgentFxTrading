# Round 65, stream E: HK leveraged / inverse product rebalancing at the close -> HK50

Written 2026-11-01 11:56 UTC onwards (`date -u`). Hypotheses: [HYPOTHESES_E.md](HYPOTHESES_E.md) (6 cells declared
11:52-11:53 UTC before any return; first return 11:54 UTC). HOLD stayed closed: HK50 loaded at ts < 2025-01-01, no
issuer or HKEX series dated after 2024 was requested. Disclosure: two WebSearch summaries quoted 2025-26 HK L&I
turnover and a current AUM figure for 7500 (fund statistics, not prices; not used).

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- **Data:** no free AUM / units history. csopasset.com (the dominant issuer) answers 403 even to robots.txt, so I
  stopped there. HKEX's ETP pages are current-only, and the Monthly Bulletin JSON covers only the last 12 months (HOLD
  era; the 2024-12 file is 404). So only the sign / size rule was tested, with |r| standing in for the dose.
- **Into the cash close (C1-C3), the effect runs against the mechanism.** Following the day's move from 15:45 / 15:50
  to 16:00 or 16:10 loses in IS (net t -3.1 / -5.2 / -3.0) and is net-negative in VAL. That repeats round 13 P's IS
  reversal.
- **The one mechanism-consistent effect is after the cash close (C4).** It sits in the futures-only window
  16:10-16:29 HKT, before HKFE's 16:30 close, when the L&I products rebalance futures with r already known.
  - On top-decile days, following r gives a gross mid of +8.9 bp (t 2.9) IS and +7.2 bp (t 2.8) VAL.
  - In both eras the mid is ~0-3 bp in deciles 1-9 of |r| and +6.7 / +9.3 bp in the top decile.
- **It fails DEMO.**
  - IS net is +5.69 bp, t 1.90, below the 2.0 bar.
  - Without March-April 2020, IS net is -0.05: the IS edge is 2020 alone. Only 3 of 7 years are positive.
  - The declared random benchmark beats 81 % / 35 % (IS / VAL). That benchmark draws its windows before 16:09, so it
    is biased upward.
  - VAL net is +4.29 (t 1.67). Power at the VAL size is 1.30, far below the 3 needed for LIVE.
  - Round 34's USTEC result looked the same: a real gross flow in VAL, smaller than costs plus 2020 in IS.

## Data
| source | result |
|---|---|
| IC HK50 M1 (research/data/m1/HK50.npz), bid OHLC + ask at the last tick | 2016-01..2024-12. Bars 15:30-16:00 on 97-99 % of days. **16:00-16:29 bars on only 14-19 % of days in 2016-17**, full from 2018: windows after 16:00 effectively have IS = 2018-21. No bars 16:30-17:14 (futures break). Median spread at 15:45-16:28: 4.4 bp (2016), 3.9 (2017), 2.5-2.9 (2018-21), 3.3-3.5 (2022-23), 1.0 (2024) |
| csopasset.com (CSOP: 7200 / 7500 / 7226 / 7552) | robots.txt -> **403**: stopped |
| hkex.com.hk via agentFx (robots 200, allows these paths) | ETP pages current-only; Monthly Bulletin JSON only 2025-09..2026-09 (not requested), 2024-12 is 404; statistics archive lists no per-product files |
| globalxetfs.com.hk | robots 200 (allows everything); its HSI / HSTECH L&I AUM is a small share of CSOP's, so it was not pulled |
| samsungetf.com.hk | robots 301 (not followed) |

Requests: 12 (research/data/hk_lev_etf/requests.log), bodies in research/data/hk_lev_etf/raw/, parsed with
`python -I`. Nothing was left in agentFx /tmp (checked). WebSearch: 3 of 15. Two search hits matter for timing:
- the CSOP filings say the HSI products are futures-based and that "the Index is not a futures index";
- a ChinaAMC HSCEI 2x filing says the daily rebalance is "at or around the close of the trading of the underlying
  futures market".

## Rule and costs (as declared)
- Day move r_m = ln(mid at the close of bar m / the previous day's reference mid). The reference is the 16:09 bar,
  or 15:59 if 16:09 is missing.
- Big day = |r_m| at or above the 90th percentile (80th for C6) of the previous 250 days.
- Entry at the close of the next bar; long at ask, short at bid; exit on the other side.
- Net = the real spread at both ends (IC index CFDs charge no commission). One trade a day, so the t is per day.

## Results (bp per trade; t; n)
| cell | window (HKT) | side | IS mid | IS net (t) n | VAL mid | VAL net (t) n | cost IS/VAL | x1.5 IS/VAL | late IS/VAL | IS ex 2020-03/04 | years > 0 | power IS/VAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 15:45->16:00 | follow | -1.03 | -4.12 (-3.08) 139 | +1.02 | -1.73 (-0.71) 77 | 3.09/2.75 | -5.67/-3.10 | -4.99/-6.02 | -3.59 (-2.63) | 1/9 | -1.69/-0.56 |
| C2 | 15:50->16:00 | follow | -1.81 | -4.92 (-5.20) 140 | +1.87 | -0.91 (-0.50) 77 | 3.11/2.78 | -6.47/-2.30 | -6.38/-5.95 | -4.58 (-5.00) | 1/9 | -2.86/-0.39 |
| C3 | 15:45->16:10 | follow | -4.47 | -7.46 (-3.04) 122 | -0.48 | -3.27 (-0.86) 77 | 2.99/2.79 | -8.95/-4.66 | -5.66/-4.83 | -5.59 (-2.36) | 1/8 | -1.68/-0.67 |
| **C4** | 16:10->16:29 | follow | **+8.93 (t 2.92)** | **+5.69 (+1.90) 86** | **+7.17 (t 2.79)** | **+4.29 (+1.67) 85** | 3.24/2.89 | +4.07/+2.84 | +7.28 (2.55)/+4.18 (1.69) | **-0.05 (-0.03)** | 3/7 | 1.05/**1.30** |
| C5 | 16:29->17:30 | fade | -4.39 | -8.04 (-2.08) 86 | -2.25 | -5.49 (-1.51) 84 | 3.65/3.24 | -9.87/-7.10 | -6.65/-5.45 | -4.86 (-1.73) | 0/7 | -1.14/-1.18 |
| C6 | 16:10->16:29, top quintile | follow | +5.32 (t 3.16) | +2.19 (+1.32) 179 | +3.61 (t 2.23) | +0.74 (+0.46) 164 | 3.13/2.87 | +0.63/-0.70 | +3.20/+0.29 | -0.60 (-0.57) | 3/7 | 0.73/0.35 |

Net per year (n):
| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| C1 | -2.9 (5) | -5.6 (18) | -0.6 (47) | -3.5 (18) | -5.5 (28) | -9.3 (23) | -2.9 (38) | -3.2 (12) | +0.6 (27) |
| C4 | - | - | -2.8 (19) | -2.7 (16) | **+20.4 (30)** | -1.3 (21) | +5.5 (43) | -3.2 (13) | +5.8 (29) |
| C6 | - | - | -1.5 (34) | -2.6 (36) | +9.5 (64) | -1.6 (45) | +2.1 (75) | -2.5 (40) | +1.2 (49) |

C2, C3 and C5 are in code/run_out.txt. The 2016-17 trade counts are low because the threshold needs 120 days of
history, and the windows after 16:00 have few bars in those years.

**Benchmarks.**
| cell | declared random (same days, other minutes) beats IS / VAL | causal shuffled days (bench2, post hoc) beats IS / VAL |
|---|---|---|
| C1 | 0.0 % / 3.4 % | 10.4 % / 71.2 % |
| C2 | 0.0 % / 13.4 % | 0.4 % / 81.5 % |
| C3 | 0.0 % / 0.4 % | 1.4 % / 39.4 % |
| C4 | 81.3 % / 35.0 % | 100 % / 100 % |
| C5 | 100 % / 99.9 % | 2.7 % / 13.9 % |
| C6 | 58.4 % / 5.9 % | 100 % / 97.4 % |

- **What each benchmark measures.**
  - The declared benchmark draws windows earlier in the same big day, with the side taken from the move up to that
    minute. Those windows contain the move that selected the day, so their mean is inflated: for C4, random +3.6 /
    +5.7 against actual +5.7 / +4.3. For C5 the inflation runs the other way (a fade against the selecting trend),
    which is why C5 "beats" it.
  - The causal benchmark draws random era days, keeps the same window, and takes the side from r. C4 and C6 beat it,
    so the 16:10-16:29 follow-through really does concentrate on big days.
  - Non-big days in the same window: IS net -2.11 (t -5.1), mid +0.69; VAL net -2.08, mid +0.66.
- **Chance:** shared per-day sign flips across the 6 cells. Max IS net t is 1.90 (C4) against a null p50 of -0.19 and
  p95 of 1.16 (p 0.004). The null is low because sign-flipped gross minus cost is negative.
- **Dose response** (information; gross mid of the window on all days by |r| decile, follow side):
  - C4 window, IS: +0.5 -0.9 +0.6 -0.4 +0.7 +1.5 +2.7 +0.4 +2.0 **+6.7**
  - C4 window, VAL: -0.7 +1.1 +1.5 -1.5 +0.6 +2.2 +3.5 -1.5 -0.2 **+9.3**
  - C1 window, IS: about 0 in every decile (-0.2 .. +1.1). VAL: -1.6 .. +2.2, no shape.
- **Era split for C4:** 2016-20 net +7.95 (t 2.08, n 65), 2021-24 +3.18 (t 1.49, n 106). The big HSTECH 2x / -2x
  products from 2020-12 did not make it larger.

## Bar check
| bar | C4 (best) |
|---|---|
| DEMO: IS net t >= 2.0 | **1.90: fail** |
| DEMO: VAL net > 0 | +4.29: pass |
| DEMO: >= 90 % random | declared 81 % / 35 %: **fail** (causal 100 %) |
| x1.5 and one step late > 0 | pass (+4.07 / +2.84; +7.28 / +4.18) |
| LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years, power >= 3 | fail (1.90, 1.67, 3/7, 1.30) |

The IS edge is the March-April 2020 crash: IS without those two months is -0.05 bp. That is the same pattern as round
13's index big-day effects and round 34's USTEC. C4 is not a candidate, and nothing was drafted.

## What this says
- **The mechanism has a visible footprint, but at the post-cash-close futures window, not into the auction.**
  - 15:45-16:10 (the window round 13 tested) has no follow-through, or reverses.
  - 16:10-16:29, after the HSI close is fixed and while HKFE futures still trade, top-|r| days follow +7-9 bp gross in
    both eras with a decile step at the top. That timing fits products that track the cash close and rebalance futures
    "at or around the futures close".
  - The 17:15 after-hours session does not give the move back (C5 fade loses); the push looks permanent, not
    transient.
- **Too small for IC's costs before 2024, and too rare for power.**
  - Cost was ~3 bp a round trip in 2016-23 (1.0 in 2024), against ~7 bp gross.
  - ~28 trades a year gives HOLD power 1.3 at the VAL size; LIVE needs 3, so even a doubled effect would not do.
  - The 2024 spread drop (to 1 bp) would leave ~+6 bp net if the gross holds, but that is one year and it is not a
    bar decision.
- **The measured dose could not be built.** CSOP blocks bots (403) and HKEX has no free per-product history. A dose
  rule would need issuer units history from a source the user approves (CSOP site access, or a paid HK ETF database).
  Given C4's IS (only 2020) and its power ceiling, the value is low: LIVE < 1 %, DEMO ~3 %.

## Directions that need the user
1. Forward log of C4 (16:10->16:29 HKT follow on top-decile |r| days; rule fixed in HYPOTHESES_E.md) on IC data after
   2026-09-24. It is information only: it cannot be promoted under the current bars because it failed IS. About 28
   trades a year; at the VAL size the expected t is ~1.3 after 1.8 years.
2. CSOP daily units / AUM (needs CSOP's OK or a paid source) to test the dose version. Value: low.

## Pitfalls met
- The declared random benchmark (other minutes on the same days) is not causal for close-window rules on days
  selected by the day's move (PROMPT pitfall). Use shuffled days, or windows after the signal.
- IC HK50 has few bars after 16:00 in 2016-17, so any post-close HK rule has a 4-year IS.
- Bar labels are minute starts: "price at 16:10" is the close of the bar labelled 16:09.

## Files
- code/coverage.py (minute coverage / spread), code/letf.py (panel, rule, fills), code/run.py -> code/run_out.txt,
  code/bench2.py -> code/bench2_out.txt, code/fetch.sh (logged fetch helper), trades_E.csv (per-trade net, IS / VAL).
- research/data/hk_lev_etf/requests.log, research/data/hk_lev_etf/raw/.
