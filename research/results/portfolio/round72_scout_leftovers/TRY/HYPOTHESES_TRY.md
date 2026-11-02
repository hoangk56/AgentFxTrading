# Stream TRY (round 72): hypotheses, written before any return is computed

Written 2026-11-01 18:47 UTC (`date -u`: Sun Nov 1 18:47:36 UTC 2026). At this time no data of this stream has been
requested. The episode counts (section 6) are added after the pull and before any return; that section carries its own
`date -u` stamp. HOLD (>= 2025-01-01) is never requested: every request ends at 2024-12-31 23:59:59 UTC and every
series is cut at ts < 2025-01-01 at load.

## 1. Mechanism (side fixed: long USDTRY)
Turkish savers who are limited or distrustful at banks buy USDT for lira on BtcTurk. When the official / interbank
rate is managed (state-bank selling, 2021-23 "KKM" regime, pre-election holding), the excess demand shows up as a
premium of USDT/TRY over USDTRY. The official rate later gives way (2018-08, 2021-11/12, 2023-06). So a high premium
should lead USDTRY up. The side is long USDTRY only; no short cell.

## 2. Data
- BtcTurk public candles, keyless: `graph-api.btcturk.com/v1/klines/history?symbol=USDTTRY&resolution=60&from&to`
  (1h), plus `resolution=1D` (1d) only to find the listing start. robots.txt first (logged). >= 1 s between requests,
  plain UA, no e-mail. 403 = stop the host; 418 / 429 / 503 = back off.
- Dukascopy USDTRY ticks: `datafeed.dukascopy.com/datafeed/USDTRY/YYYY/MM-1/DD/06h_ticks.bi5` (bid and ask) for every
  weekday 2016-01-01..2024-12-31 (one hour file per day, ~2,350 files, >= 0.5 s apart, back off on 503). The 06h file
  holds the 06:00 mid, the 06:01 entry and the 06:01 exits.
- USD rate: local research/data/rates/DFF.csv (EFFR). TRY rate: the CBRT policy / effective funding rate as a step
  schedule from the CBRT's published decisions (a public CBRT page if robots allows; otherwise the declared schedule
  from the decisions, written into code/rates_try.py before returns are computed).

## 3. Premium and signal
- p_t = (BtcTurk USDTTRY close of the 1h candle 05:00-06:00 UTC) / (Dukascopy USDTRY mid at the first tick >= 06:00:00
  UTC) - 1, i.e. 09:00 Istanbul (Turkey is UTC+3 all year since 2016-09-07; before that EET/EEST, but the brief fixes
  06:00 UTC, so 2016 dates before 09-07 are 08:00 or 09:00 local: harmless for a daily level signal, reported).
- A day is valid if Dukascopy has a tick in 06:00-06:10 and the BtcTurk candle (or the last one within the 3 hours
  before 06:00) has volume > 0. Weekends and days without a Dukascopy quote are skipped.
- Signal day: p_t > k. Episode: a maximal run of signal days with gaps of <= 5 trading days between consecutive signal
  days (declared now).

## 4. Rule and the declared cells (6, no others)
Long USDTRY at the first **ask** tick >= 06:01:00 UTC of the signal day (the next M1 bar after the 06:00 reading);
exit at the first **bid** tick >= 06:01:00 on the h-th later valid trading day. Every signal day is a trade (overlapping
trades in multi-day holds are allowed and handled by the clustering).

| cell | k | hold h (trading days) |
|---|---|---|
| k1h1 | 1 % | 1 |
| k1h5 | 1 % | 5 |
| k1h20 | 1 % | 20 |
| k2h1 | 2 % | 1 |
| k2h5 | 2 % | 5 |
| k2h20 | 2 % | 20 |

Parameters are picked on IS only; VAL is a check of the same cell unchanged. The max-over-6-cells null is reported.

## 5. Costs
- Spread: the Dukascopy ask at entry and bid at exit (the real quoted half-spreads at 06:01).
- Commission: 0.7 bp round trip (IC raw FX).
- Carry per calendar day held (Fri->Mon = 3 nights, by calendar days between entry and exit dates): long USDTRY pays
  r_TRY/365 - r_USD/360 plus a declared broker markup of 2 %/yr (1 %/yr in a sensitivity line). r_TRY is the schedule of
  section 2, r_USD is EFFR on the entry date. Known understatement: offshore TRY overnight swap rates spiked far above
  the policy rate (2018-08, 2019-03 London squeeze); the model does not capture those days (reported as a pitfall).
- Stress: spread x1.5 and carry x1.5; one step late = entry and exits at 06:02 instead of 06:01, and a one-day-late
  variant (enter the next trading day 06:01).

## 6. Episode counts per era (added after the pull, before returns)
IS = data start..2021-12-31, VAL = 2022-01-01..2024-12-31. If IS has < 3 episodes for a k, that k is reported
descriptively only and cannot pass a bar.

Filled 2026-11-01 19:34 UTC (`date -u`), from code/counts.py, before any return was computed. Data: Dukascopy hourly
BID + ASK files 2018-06..2024-12 complete (158 / 158, no ASK fallback needed); 1,678 valid weekdays from 2018-07-10,
1,674 with a premium. BtcTurk candle label = hour start (code/align_h1.py: corr of hourly returns 0.452 at label = start,
0.019 / 0.060 at -1 / +1 h). Median 07:00 Dukascopy spread 2.5-6.0 bp by year.

| k | era | signal days | episodes (gap <= 5 trading days) |
|---|---|---|---|
| 1 % | IS 2018-07..2021 | 173 | 31 |
| 1 % | VAL 2022-24 | 295 | 23 |
| 2 % | IS | 55 | 25 |
| 2 % | VAL | 128 | 17 |

Signal days by year, k 1 %: 2018 22, 2019 56, 2020 40, 2021 55, 2022 110, 2023 141, 2024 44; k 2 %: 9, 19, 8, 19, 26,
84, 18. One k 1 % episode runs 2022-10-10..2023-06-12 (161 days, the pre-election managed rate) and dominates VAL; one
crosses the era line (2021-11-16..2022-02-24; its days are split by era). Both k have >= 3 IS episodes, so all 6 cells
are testable. Power arithmetic at these counts: HOLD would hold ~1.83 x (23 / 3) ~ 14 episodes for k 1 % and ~10 for
k 2 %, so power 3 needs a net Sharpe of ~0.8-0.95 per episode.

## 7. Statistics and bars
- Per cell and era: n trades, n episodes, mean net bp per trade, t clustered by episode (CR1 on episode sums), and
  Newey-West t of the trade series in date order with lag h + 5; years positive (by entry year).
- Random benchmark: (a) circular shift of the signal-day set by a random offset within the era (keeps the episode
  structure), (b) iid random days with the same count; 2,000 draws each, same costs; % of draws whose mean net is below
  the cell's. Max-over-cells: the share of shift draws whose best-of-6 IS t exceeds the chosen cell's IS t.
- USDTRY rose ~3 -> 35 over 2016-24, so random long entries are gross positive; the random benchmark is the test that
  the premium adds anything over the trend minus carry.
- Bars as in the brief (LIVE / DEMO). Pass -> PREREG_DRAFT_TRY_<name>.md and stop; HOLD is not opened here.

## 8. Power arithmetic (before data)
Stream J estimated ~30-60 signal days in a few episodes (2018-08, 2020-11, 2021-12, 2023-06). Power = net Sharpe per
episode x sqrt(HOLD episodes). With ~1-2 episodes a year, HOLD (1.83 years) holds ~2-4 episodes: power >= 3 needs an
episode Sharpe of 1.5-2.1, i.e. nearly every episode a large clean winner. LIVE is therefore close to impossible by
construction; DEMO needs IS t >= 2.0 with clustering on <= ~5 IS episodes, which is also hard. Prior P(LIVE) 0.5 %,
P(DEMO) 2.5 % (J5).

## 9. Amendment A (2026-11-01 18:57 UTC, `date -u`; before any premium, episode or return is computed)
Data facts found while pulling (no prices looked at beyond format checks):
- BtcTurk USDTTRY starts 2018-07-10 10:00 UTC (1D and 1h). IS is therefore 2018-07-10..2021-12-31.
- Dukascopy answered 429 to a User-Agent containing "(python urllib)" and serves the plain UA "research-scout/1.0"
  (not a browser UA). Tick-hour files then took ~10-20 s each with frequent 503 / timeouts: the 2,350-file tick pull
  would take ~8 h, over the 45-min budget. Stopped after 14 files (all January 2016, unused).
- Change of price model (declared now): Dukascopy **hourly candles** (one BID and one ASK file per month, 2018-06..
  2024-12). The 06:00 reading uses the mid of the BID / ASK **open of the 06:00 candle** (first price at or after
  06:00:00). Entry = the ASK open of the **07:00 candle** (the first tradable price one full hour after the reading;
  later than the 06:01 M1 bar of section 4, never earlier). Exit = the BID open of the 07:00 candle h valid trading days
  later. "One step late" = the 08:00 candle open for entry and exits; the one-day-late variant stays. A day is valid if
  the 06:00 and 07:00 candles both have volume > 0. Spread = the BID / ASK open difference at entry and exit.
- If the host allows it inside the budget, 06h tick files for the signal days and their exit days are pulled as a
  secondary check of the 06:01 entry; the cells, k, h and costs are unchanged.
- TRY rate: the CBRT one-week repo step schedule from the CBRT page (tcmb.gov.tr robots.txt 404 = no rules), steps
  >= 2025-01-01 dropped at parse. That page also lists 2025-26 decisions; they were shown in the parse output once and
  are not used.
- The 1D probe response included a 2025-01-01 00:00 boundary candle whose price was printed once in a format check;
  it is dropped at load (ts < 2025-01-01) and is not used.

## 10. Amendment B (2026-11-01 19:06 UTC, `date -u`; still before any premium, episode or return)
The Mac's link to datafeed.dukascopy.com fails TLS often, and the host answers most requests with 503 (~2.5 monthly
files a minute with 3 in flight). A probe from the agentFx VPS took 12 s for one file, so the host is slow, not only the
link. The pull is ordered BID first and stops at 19:45 UTC. Declared fallback: on a day whose month has no ASK file, the
ask = bid x (1 + s), where s is the median relative spread at the 07:00 candle open over the ASK months of the same
calendar year (the previous year if that year has none). The tables say how many trades use the fallback.
