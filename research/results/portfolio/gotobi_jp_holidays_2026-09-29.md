# GotobiBot on Japanese holidays (2026-09-29)

**Question.** The swing lab v2 report (`swing_lab_v2_2026-09-27.md`, C3 caveats) left Japanese holidays out of the
gotobi calendar: there is no Tokyo fix on them, and the report expected "~0 effect, so this only adds noise". The
deployed bots therefore trade every gotobi weekday except 2026-12-25. Do the holiday gotobi days cost money?

**Verdict: yes. Skip them.** On the 45 gotobi days of 2016-2026 that fell on a Japanese public holiday or a bank
holiday, the basket lost (mean R -0.066, t -3.4), against +0.056 (t +9.6) on the other 727. The loss sits in the long
leg, bought into a fix that does not happen (R -0.153, 27 % winners). It is negative in every era, and most negative
in the most recent one.

## Data and method

- Trades: the GotobiBot cTrader backtest of `gotobi_cbot_backtest_2026-09-27.md` (IC ticks, 2016-01 .. 2026-09-24,
  USDJPY / EURJPY / GBPJPY, $50 default risk, one bot per pair), i.e. `gotobi_cbot_trades.csv` (git-ignored; on the
  VPS in `~/gotobi-build/`). R = net $ / 50.
- A trade's gotobi day is the date in its leg tag (`GOTOBI-L 2016-01-05`).
- Days with no fix: Japanese public holidays from the python `holidays` package (0.105, `holidays.Japan`), plus
  the bank holidays 31/12, 2/1 and 3/1.
- Everything below is printed by
  `research/.venv/bin/python -m research.tools.gotobi_holidays research/results/portfolio/gotobi_cbot_trades.csv`
  (`holidays` is not in `research/requirements.txt`; install it into the venv first).

## Results ($50 risk per trade)

| trades | days | trades | mean R | t | win | net $ |
|---|---|---|---|---|---|---|
| normal gotobi days | 727 | 4311 | +0.056 | +9.6 | 58 % | +12,045 |
| holiday gotobi days | 45 | 263 | -0.066 | -3.4 | 37 % | -863 |
| normal, long leg | 723 | 2148 | +0.072 | +7.6 | 61 % | +7,760 |
| holiday, long leg | 44 | 131 | -0.153 | -5.7 | 27 % | -1,002 |
| normal, short leg | 724 | 2163 | +0.040 | +5.9 | 56 % | +4,285 |
| holiday, short leg | 44 | 132 | +0.021 | +0.8 | 46 % | +140 |
| public holidays only | 37 | 221 | -0.079 | -4.0 | 37 % | -868 |
| bank holidays only | 8 | 42 | +0.003 | +0.0 | 33 % | +6 |

| era | holiday days | holiday mean R | holiday net $ | normal mean R |
|---|---|---|---|---|
| IS 2016-21 | 25 | -0.019 | -138 | +0.061 |
| VAL 2022-24 | 12 | -0.078 | -275 | +0.042 |
| HOLD 2025-26 | 8 | -0.187 | -449 | +0.063 |

Skipping the holidays does not change the basket's max drawdown ($512 either way): the worst stretch
(2022-12-23 .. 2023-03-10) has no holiday gotobi day in it.

Per day, holiday gotobi days only (net $ of all legs and pairs):

| day | holiday | net $ | | day | holiday | net $ |
|---|---|---|---|---|---|---|
| 2016-04-29 | Showa Day | +37 | | 2021-07-23 | Sports Day | -37 |
| 2016-05-05 | Children's Day | +3 | | 2021-09-20 | Respect for the Aged Day | +89 |
| 2016-10-10 | Physical Education Day | +11 | | 2021-12-31 | Bank holiday | -33 |
| 2016-12-23 | Emperor's Birthday | -61 | | 2022-01-10 | Coming of Age Day | -38 |
| 2017-03-20 | Vernal Equinox Day | -6 | | 2022-04-29 | Showa Day | -40 |
| 2017-05-05 | Children's Day | +64 | | 2022-05-05 | Children's Day | -144 |
| 2017-11-03 | Culture Day | -71 | | 2022-09-23 | Autumnal Equinox Day | +19 |
| 2018-04-30 | Substitute Holiday | -15 | | 2022-10-10 | Sports Day | +29 |
| 2018-05-04 | Greenery Day | +46 | | 2023-05-05 | Children's Day | +10 |
| 2018-11-23 | Labor Thanksgiving Day | +2 | | 2023-11-03 | Culture Day | -24 |
| 2018-12-31 | Bank holiday | -16 | | 2024-02-23 | Emperor's Birthday | -48 |
| 2019-04-30 | National Holiday | -53 | | 2024-03-20 | Vernal Equinox Day | +14 |
| 2019-05-03 | Constitution Day | -40 | | 2024-05-03 | Constitution Day | -14 |
| 2019-07-15 | Marine Day | -143 | | 2024-07-15 | Marine Day | -22 |
| 2019-12-31 | Bank holiday | -9 | | 2024-12-31 | Bank holiday | -15 |
| 2020-01-03 | Bank holiday | +172 | | 2025-01-03 | Bank holiday | -44 |
| 2020-03-20 | Vernal Equinox Day | +84 | | 2025-03-20 | Vernal Equinox Day | -158 |
| 2020-05-05 | Children's Day | -85 | | 2025-05-05 | Children's Day | +39 |
| 2020-07-24 | Sports Day | -98 | | 2025-09-15 | Respect for the Aged Day | -78 |
| 2020-08-10 | Mountain Day | -37 | | 2025-12-31 | Bank holiday | -43 |
| 2020-12-31 | Bank holiday | -6 | | 2026-03-20 | Vernal Equinox Day | -25 |
| 2021-05-05 | Children's Day | +67 | | 2026-05-05 | Children's Day | -25 |
| | | | | 2026-07-20 | Marine Day | -115 |

## Caveats

- One test on 45 days, but a mechanism-driven one (no fix means no settlement flow), not the pick of a search; the
  sign is the same in all three eras.
- Leaving the losing days out of a backtest flatters it only by what they lost: about +$80 a year at $50 risk.
  The case for skipping is that the flow the bot trades is absent on those days, not the size of that number.
- The bank holidays alone are flat (8 days, R +0.003); they are skipped for the same reason as the public ones.
- Not tested: whether a holiday's settlement moves to the business day before it (a day the bot does not trade
  unless it is itself a gotobi day). That needs the research engine, not this trade list.

## What changed

`app/cbot_presets.GOTOBI_SKIP_DATES` lists the holiday gotobi days to the end of 2027 (2026-12-31, 2027-05-05,
2027-09-20, 2027-12-31) plus the cBot's own 2026-12-25 default, and every Gotobi preset cell passes it as
`--SkipDates`. A running bot takes it only when its container is recreated with the new flags
(`PUT /api/bots/{name}`). `python -m research.tools.gotobi_holidays --upcoming 2028-01-01:2028-12-31` prints the
next year's dates (2028-01-10, 2028-03-20, 2028-05-05, 2028-11-03).
