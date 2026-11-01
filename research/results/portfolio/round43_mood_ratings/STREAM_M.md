# Round 43 stream M: investor-mood shocks (cloud cover, temperature, wind, haze, football) -> local index CFDs

Written 2026-10-30 (06:00 UTC). Hypotheses, sides and cells: [HYPOTHESES_M.md](HYPOTHESES_M.md) (05:29 UTC,
amendments 05:37 and 05:58 UTC, W2 05:58 UTC; each written before its returns). Bars: research/PROMPT.md LIVE / DEMO.

## Answer
**No LIVE or DEMO candidate, no PREREG_DRAFT.** 36 declared book cells (W 8, W2 8, F 12, P 8) plus 72 + 72 x 2
single-city and 14 FX / CNH information cells. No declared book cell has IS net t above +0.20: the best IS net
t of each family is W -0.00, W2 -0.60, F +0.20, P -0.07. The
literature's sunshine effect is absent at mid (book IS -0.25 bp, VAL -2.26 bp a day on the declared side); the
football loss effect has the wrong sign (index rises after losses in IS); morning haze does not lower HK50. One
mood variable is positive at mid in both eras: **wind** (calm -> long, windy -> short, Shu & Hung 2009), book mid
IS +2.17 bp (t 2.41) / VAL +0.61 (t 0.50), first hour +1.01 (t 2.46) / +0.80 (t 1.28), but it is smaller than the
2.7 bp round trip of an open->close index trade and its zero-cost HOLD power is ~1.3.

## HOLD and network disclosures
- HOLD closed: IC M1 cut ts < 1735689600000 at load (bid-only zbars: files >= 20250101 skipped, rows cut again);
  weather requested only for years 2004-2024, observations with UTC or local date > 2024-12-31 dropped at parse;
  football rows with date > 2024-12-31 dropped at parse (assert). No 2025-26 value was printed.
- 463 requests (log: scratchpad `web/requests.log`), 8 non-200: 2 robots.txt 404 (raw.githubusercontent,
  S3), 2 missing station-years (EDDF 2004, LFPO 2010) in both lite and full (4), 2 failed DNS lookups for dosairnowdata.org.
  NCEI's robots.txt disallows `/data*`, so the Global Hourly access CSVs named in the brief were not used; the NCEI
  `/pub/data/noaa/isd-lite/` page is an S3 explorer for the public NOAA bucket `noaa-isd-pds`, which was used
  directly (no robots.txt; >= 1.2 s between requests; one process at a time). No web.archive.org. 2 WebSearches.
- Pull time: 05:22-05:57 UTC (~35 min; full ISD ~0.8 MB a file at ~3-40 s each). Files: ISD-Lite 229 (21 MB),
  full ISD 232 (146 MB), football CSVs 3.8 MB.

## Sources
| source | used | span | notes |
|---|---|---|---|
| NOAA ISD-Lite (S3 `isd-lite/data/<Y>/`) 11 airports | temperature, wind (W2); sky cover dropped | 2004-24 | total sky cover missing at RJTT / EDDF / EGLL for most of 2014-24 (METAR without total cover): amendment 1 |
| NOAA full ISD (S3 `data/<Y>/`) 12 airports | sky cover (GF1, else max GA layer, else GD, else CAVOK / NSC = 0); visibility + dew point (haze) | 2004-24 (haze 2010-24) | NY cover vs ISD-Lite corr 0.98; report-mix level shifts (HKG ~5.2 oktas 2004-07 vs ~3.2 from 2011) -> trailing 365-day demeaning (amendment 2) |
| martj42/international_results results.csv + shootouts.csv | competitive men's results | 2004-24 | 296 losses of the 9 teams; checked Brazil 1-7 Germany 2014-07-08, England 1-2 Iceland 2016-06-27 |
| US State Dept AirNow PM2.5 (dosairnowdata.org) | unusable | - | DNS fails from this Mac (2 tries); UCI five-city PM2.5 ends 2015 (no IC index data then); replaced by airport haze (visibility, RH < 90 %) at ZBAA, ZSSS, VHHH; Beijing 2013-01-13 ranks at the top of its month (sanity) |

Prices: IC M1 US500, UK100, DE40, JP225, HK50, AUS200 (bid + ask close), F40 / ES35 / IT40 / USDCNH bid zbars with
round 7's fixed spreads, FX GBPUSD / EURUSD / USDJPY / AUDUSD; PRE 2004-15 Dukascopy FX (cost = IC 2016-17 spread
by UTC minute + 0.6 bp). Sessions DST-aware, entry open+1 min, exit close-5 min (or open+60); local exchange holidays
skipped. Mean round trip of an open->close index trade: 2.7 bp (US500 1.6, UK100 1.7, DE40 0.85, AUS200 2.0,
JP225 3.1, HK50 3.3, F40 3.4, IT40 4.3, ES35 4.7).

## Power arithmetic (before returns; HYPOTHESES_M.md)
- W / W2 daily: ~1,550 IS book days, ~750 VAL, ~440 HOLD. LIVE needs book day Sharpe >= 0.143 (net); the published
  sunshine size implies ~0.06 before cost. LIVE out of reach unless the effect is > 2x the literature net of cost.
- F: ~9.5 losses a year (EU5 + JP + AU), ~20-25 in HOLD -> LIVE needs per-trade Sharpe >= 0.6-0.67; EGN's -38 bp
  is ~0.38: LIVE impossible from the count; DEMO needs >= 0.26 on 57 IS trades.
- P: quintiles ~100 trades a year -> LIVE needs 0.23 per trade vs a literature ~0.05-0.08: LIVE impossible.

## Results (net = after spread at entry and exit; t day-clustered; book = equal-weight mean of the day's trades)
| hypothesis (declared side) | eras | mid bp (t) IS / VAL | cost | net IS (t) / VAL (t) | VAL / IS | day or trade Sharpe IS; power HOLD (VAL size) | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| W S1 sunny -> long, cloudy -> short, 9-city book, open->close (primary) | IS, VAL | -0.25 (-0.29) / -2.26 (-1.97) | 2.72 | -2.96 (-3.46) / -4.27 (-3.71) | n/a | day -0.088; < 0 | 45.0 % / 0.5 % | none |
| W S3 quintiles open->close (best IS book cell) | IS, VAL | +2.65 (+1.99) / -4.67 (-2.30) | 2.70 | -0.01 (-0.00) / -6.62 (-3.26) | n/a | 0.000; < 0 | 97.0 % / 1.5 % | none |
| W S1 first hour | IS, VAL | +0.61 (+1.44) / -0.09 (-0.14) | 2.73 | -2.11 (-4.97) / -2.11 (-3.43) | n/a | -0.126 | - | none |
| W S1 without amendment 2 (robustness) | IS, VAL | +0.13 (+0.15) / -1.56 (-1.39) | 2.72 | -2.58 (-3.03) / -3.57 (-3.18) | n/a | -0.077 | - | none |
| W2 temperature: cold -> long, hot -> short, quintiles o->c (primary) | IS, VAL | +0.17 (+0.11) / +2.03 (+0.89) | 2.71 | -2.55 (-1.66) / -0.01 (-0.00) | n/a | -0.043 | - | none |
| W2 temperature S1 o->c | IS, VAL | +0.24 (+0.26) / -0.43 (-0.34) | 2.72 | -2.47 (-2.63) / -2.43 (-1.94) | n/a | -0.067 | 56.5 % / 35.5 % | none |
| W2 wind: calm -> long, windy -> short, S1 o->c | IS, VAL | **+2.17 (+2.41) / +0.61 (+0.50)** | 2.72 | -0.54 (-0.60) / -1.39 (-1.14) | n/a | mid day 0.061 -> zero-cost HOLD power ~1.3; net < 0 | 100 % / 69.5 % | none (below cost) |
| W2 wind S1 first hour | IS, VAL | +1.01 (+2.46) / +0.80 (+1.28) | 2.73 | -1.71 (-4.17) / -1.21 (-1.93) | n/a | net < 0 | - | none |
| W2 wind quintiles o->c / h1 | IS, VAL | +1.64 (1.20) / -0.71; +1.27 (1.77) / +1.60 (1.51) | 2.7 | -1.05 / -2.70; -1.43 / -0.40 | n/a | < 0 | - | none |
| F short loser's index, T1+T2, EU5, 1 session (primary) | IS, VAL | -9.2 (-0.59) / -0.7 (-0.06) | 2.8 | -11.9 (-0.77) n 40 / -3.4 (-0.28) n 28 | n/a | trade -0.12 | 35.5 % / 40.0 % | none (wrong sign) |
| F best IS cell: T1, EU5+JP+AU, 2 sessions | IS, VAL | +16.0 (+0.29) / +9.2 (+0.55) | 5.0 | +11.0 (+0.20) n 27 / +4.5 (+0.26) n 17 | 0.41 | 0.04; HOLD ~0.2 | - | none |
| F eliminations EU5, 1 session | IS, VAL | -7.9 (-0.23) / -6.7 (-0.59) | 2.8 | -10.7 n 12 / -9.0 n 7 | n/a | < 0 | - | none |
| F currency (short loser's ccy), EU5, local session | PRE, IS, VAL | +6.5 (1.09) / -5.2 (-1.11) / +1.0 (0.12) | 0.6-0.7 | PRE +5.9 (0.98) n 46; IS -5.8 (-1.25); VAL +0.3 | n/a | < 0 in IS | - | none |
| P mainland haze quintiles -> HK50 o->c (primary; high haze short) | IS, VAL | +3.16 (+0.81) / +11.21 (+1.37) | 3.44 | -0.28 (-0.07) n 510 / +8.45 (+1.03) n 225 | n/a | -0.003; VAL 0.069 -> HOLD ~0.9 | 83.5 % / 98.0 % | none |
| P mainland haze sign -> HK50 first hour | IS, VAL | -2.35 (-1.69) / +2.65 (+0.92) | 3.27 | -5.62 (-4.03) / -0.15 | n/a | < 0 | - | none |
| P HK haze quintiles o->c | IS, VAL | -0.01 (-0.00) / +10.78 (+1.23) | 3.36 | -3.38 (-0.74) / +8.07 (+0.92) | n/a | < 0 IS | - | none |
| P mainland haze -> long USDCNH (info) | IS, VAL | -0.43 (-1.02) / -1.91 (-2.55) | ~1.0 | -1.47 (-3.48) / -2.93 (-3.91) | n/a | < 0 (CNH weaker on clean days) | - | none |

By year (W S1 primary, net bp per book day): 2016 -4.2, 2017 -4.6, 2018 -3.4, 2019 -2.1, 2020 -2.1, 2021 -1.4,
2022 -7.4, 2023 -2.9, 2024 -2.5 (all negative; the mid is ~0 or negative in every year). F primary by year (n, net
bp): 2016 7 / -94, 2017 3 / +22, 2018 13 / +17, 2019 4 / -25, 2020 4 / -50, 2021 9 / +21, 2022 16 / -4, 2023 4 / +19,
2024 8 / -13. P primary by year: 2016 +3.6, 2017 -2.5, 2018 -10.2, 2019 -9.9, 2020 +12.7, 2021 +0.8, 2022 +24.2,
2023 -2.3, 2024 +1.4. With / without 2020-03/04 changes no verdict (W S1 ex-2020 IS t -4.18; F has no event then).
Spread x1.5 and +1 minute move every W / P cell by < 1.7 bp and every F cell by < 7 bp; the only sign change is the
F primary in VAL with +1 minute (+2.1 vs -3.4 bp), which does not change a verdict.

Eras and decay: indices have no PRE (IC starts 2016), so decay since publication is read from the FX legs: sunshine
-> local currency (S1) PRE mid +0.65 / +0.85 / -0.45 / +0.66 bp (GBP, EUR, JPY, AUD; |t| <= 0.86), IS and VAL within
+-2.5 bp and sign-unstable; football -> currency PRE EU5 +6.5 bp (t 1.09, 46 losses) then -5.2 (IS) and +1.0 (VAL).
Whatever existed before 2016 is not visible after.

## Cells tried and chance
- W: 8 book cells (+72 single-city). Best IS book net t -0.00 (S3 o->c); day sign-flip best-of-8 null p50 +1.00,
  p95 +2.36 -> p 0.88. Singles: 0 / 72 with IS net t >= 2; 1 / 72 with IS mid t >= 2 (HK S1 first hour, +2.44,
  VAL -2.28) and 1 <= -2: chance.
- W2: 8 declared + 8 shape cells computed by the shared script (S2 terciles, S4 raw thresholds; not declared, not
  graded). Best declared IS net t -0.60 (wind S1 o->c); null p95 +2.29-2.40. Wind single cells, post hoc, information
  only: US500 net IS +1.98 (t 1.02) / VAL +2.61 (0.80), DE40 +2.05 (0.92) / +0.82 (0.26): cheap symbols positive in
  both eras, per-trade Sharpe ~0.025 -> HOLD power ~0.5 per symbol; not registrable (chosen after seeing, power far
  below 3).
- F: 12 cells; best IS t +0.20 vs best-of-12 p50 ~1.6. P: 8 cells; best IS t -0.07 vs best-of-8 p50 ~1.4.

## Why nothing escapes
1. Cost: an open->close index trade costs 2.7 bp on average, while the published mood effects are 1-3 bp a day
   (sunshine, temperature, wind). Only wind reaches +2 bp at mid, and only in IS.
2. The sunshine result is a 1982-97 NYSE / 26-exchange finding; 2016-24 shows none at the exchange-city airports,
   in line with the post-publication null literature (the trading population is no longer the people under the sky:
   index CFD / futures flow is global and algorithmic).
3. Football: national-team losses are followed by higher local index returns in IS (EU5 -9.2 bp at mid on the short
   side); EGN's effect (1973-2004) does not survive in 2016-24 on CFDs, also not for eliminations.
4. Haze: positive at mid on the declared side only in VAL (+11 bp, t 1.37); IS flat; CNH moves the wrong way.

## PREREG_DRAFT
None.

## Directions that need the user
| direction | value |
|---|---|
| Paid / registered hourly PM2.5 (aqicn institutional, China MEE station archive) instead of the visibility proxy | LIVE < 1 %, DEMO ~1 % |
| A venue with index futures / CFDs at < 1 bp round trip (wind effect +1-2 bp at mid) | LIVE < 1 %, DEMO ~2 % |
| Kick-off-timed football data (paid) to trade the first minutes after the final whistle on the night session | < 1 % |

## Files
- Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r43/M/`
  - code/: fetch.py (polite fetcher + log), weather.py (ISD-Lite cover first try, haze), cover_full.py (amendment 1
    cover), tw.py (temperature / wind), px.py (prices, sessions, costs, stats), run_W.py (W and W2; `trail` = amendment
    2), run_F.py, run_P.py, fbcount.py, fbvenues.py, cover_years.py
  - out/: W_trail/ (primary W), W_raw/ (robustness), W2_temp/, W2_wind/ (W_results.txt + run.log each),
    F_results.txt, F_events.csv, F_run.log, P_results.txt, cover.json, haze.json, temp.json, wind.json
  - web/: downloads (isd/, isdfull/, fb/) and requests.log
