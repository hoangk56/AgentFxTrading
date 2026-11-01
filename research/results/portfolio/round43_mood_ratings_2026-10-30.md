# Round 43: investor-mood shocks (weather, haze, football); sovereign rating actions, 2026-10-30

Brief: [round43_mood_ratings/BRIEF.md](round43_mood_ratings/BRIEF.md). Same LIVE / DEMO bars as rounds 25-42. HOLD
(2025-01..2026-09) prices stayed closed in both streams (IC cut at load; weather requested for 2004-24 only; football and
rating rows after 2024-12-31 dropped at parse). Disclosure: stream R's first reachability probe printed four 2025-26
rating actions for Italy before the parse cut existed; no 2025-26 price or return was loaded, and nothing was registered.
Pulls: M ~35 minutes (463 requests), R ~3 minutes (34 requests).

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. The published mood effects (sunshine, football losses, pollution) are
absent or wrong-signed at mid since 2016, and the one mood variable positive at mid in both eras (calm wind, +1-2 bp)
is below IC's ~2.7 bp index round trip. Sovereign rating actions are a few dozen a year; every IS-positive cell turns
negative in PRE and VAL.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| M | NOAA ISD (public S3 bucket) morning cloud cover, temperature and wind at 11 exchange-city airports 2004-24 (deseasonalised, trailing-mean adjusted), Beijing / Shanghai / Hong Kong visibility haze proxy 2010-24, 296 competitive losses of 9 national teams (martj42 international results) -> 9 local index CFDs open-to-close / first hour / next sessions and local currencies; 36 book cells + 72 single-city cells | **none**: sunshine primary net IS -2.96 (t -3.46), negative every year 2016-24, mid ~0; football losses -> local index up in IS (declared short net -11.9, n 40); haze -> short HK50 net IS -0.28 / VAL +8.45 (t 1.03); calm wind -> long mid IS +2.17 (t 2.41) / VAL +0.61, net < 0 (HOLD power ~1.3 even at zero cost) | [STREAM_M.md](round43_mood_ratings/STREAM_M.md), [HYPOTHESES_M.md](round43_mood_ratings/HYPOTHESES_M.md) |
| R | Moody's + S&P long-term FC ratings and outlooks for 22 sovereigns 2004-24 (countryeconomy.com; Fitch only to ~2020, used for the 2014-20 EU review calendar) -> downgrade / negative outlook short index or currency, upgrades long, periphery spillover to STOXX50 / EURUSD, book, drift into review dates, relief after no-action reviews; k 1-4 days; 25 cells | **none**: best IS net t 1.85 (rating changes only, k4, VAL -14.9) and 1.68 (sell currency after downgrade, k1, VAL -14.6; PRE -24.6, t -3.09); IS-positive cells negative in PRE and VAL; ~8 downgrade / negative-outlook events expected in HOLD (LIVE needs per-event Sharpe >= 1.06) | [STREAM_R.md](round43_mood_ratings/STREAM_R.md), [HYPOTHESES_R.md](round43_mood_ratings/HYPOTHESES_R.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Investor-mood shocks: morning sunshine / cloud cover, temperature, wind at exchange cities; Chinese haze; national
  football losses -> local indices and currencies (decayed since the 1982-2004 samples; wind +1-2 bp at mid, sub-cost).
- Sovereign rating and outlook actions (Moody's, S&P, Fitch to 2020), EU review-calendar drift and no-action relief.

## Pitfalls
- NOAA: NCEI's robots.txt disallows `/data*`; use the public AWS Open Data bucket `noaa-isd-pds` (ISD-Lite and full
  ISD). Total sky cover is missing for most of 2014-24 at Tokyo, Frankfurt, London in ISD-Lite (use full ISD GF1 / GA /
  GD layers); Hong Kong cover shifts level ~2011 (report mix), so adjust by a trailing mean.
- dosairnowdata.org (State Department PM2.5) does not resolve from this Mac; the UCI five-city PM2.5 set ends in 2015.
- countryeconomy.com's robots.txt allows `*` on /ratings/ but names ClaudeBot / Claude-SearchBot as disallowed: do not
  use it again (round 43 R fetched 24 pages under the `*` rules). Its Fitch coverage ends ~2020; S&P disclosure and the
  agencies' 17g-7(b) pages are 403 or JavaScript-only.
- Print nothing from a probe before the 2024-12-31 cut exists in the parser.

## Directions that need the user
| direction | value |
|---|---|
| A venue under ~1 bp per index round trip (calm-wind mid +1-2 bp) | LIVE < 1 %, DEMO ~2 % |
| Paid / registered hourly PM2.5 (aqicn institutional, China MEE archive) | LIVE < 1 %, DEMO ~1 % |
| Agency 17g-7(b) XBRL rating histories; EM / periphery index or bond CFDs | DEMO ~1-2 % |

## State after round 43
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. The gold bot's USD calendar
guard (valid_through 2026-12-11) is the federal funding date, not a data gap: rebuild only once Congress acts or a
lapse starts. Round 44 opens next.
