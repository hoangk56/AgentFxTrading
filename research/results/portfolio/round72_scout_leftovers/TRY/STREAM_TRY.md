# Stream TRY (round 72): BtcTurk USDT/TRY premium -> long USDTRY

Written 2026-11-01 19:35 UTC (`date -u`). The plan, both amendments and the episode counts are in
[HYPOTHESES_TRY.md](HYPOTHESES_TRY.md). Each was written before the step it governs: the plan at 18:47, before any request;
amendment A at 18:57 and B at 19:06, before any premium was built; the episode counts at 19:34, before any return. HOLD was never
requested. Every request ended at or before 2024-12-31 and every series is cut at ts < 2025-01-01.

## Answer first: none (no LIVE, no DEMO)
- **No cell reaches the IS bar.** The best IS cell, picked by IS clustered t, is k 2 % / hold 5 days:
  - IS: +87 bp per trade, t 1.3 clustered by episode, NW 1.5, n 55, 25 episodes. DEMO needs t >= 2.0.
  - VAL: +56 bp, t 2.3 / NW 1.7, n 128, 17 episodes.
  - It beats 86 % of circular-shift random sets, below the 90 % the DEMO bar needs.
  - Max-over-6-cells null: 27 % of shifted IS signal sets give a best t at least this high.
- **The sign is right, but it comes from two lira breaks.** Drop the longest episode and every cell falls to |t| < 1:
  - IS: 2021-11/12 (the crash after the rate cuts).
  - VAL: the managed rate 2022-10..2023-06, which ended in the post-election devaluation.

  Median episode results are near zero or negative in VAL for every hold except k1h20. HOLD power at VAL size is
  0.5-1.05 per episode (LIVE needs 3).
- **Data works.**
  - BtcTurk USDTTRY 1h is keyless from 2018-07-10.
  - Dukascopy USDTRY hourly BID / ASK are complete for 2018-06..2024-12. Tick hours are too slow (see Problems).
  - The CBRT one-week repo step schedule came from tcmb.gov.tr (robots.txt 404).

## Data
| source | what | requests | notes |
|---|---|---|---|
| graph-api.btcturk.com | robots.txt (404 = no rules), USDTTRY 1D (start check), 1h per year 2018-2024 | 9 x 200, 1 x 404 | 56,156 hourly candles. Candle label = hour start: hourly-return corr with Dukascopy is 0.452 at lag 0, 0.019 / 0.060 at -1 / +1 h (code/align_h1.py). Hours without trades are missing in 2018-19, so a 3-hour staleness limit applies |
| datafeed.dukascopy.com | robots.txt (404), 158 monthly hourly-candle files (BID + ASK 2018-06..2024-12), 14 tick hours (2016-01, unused) | 175 x 200, 99 x 503, 35 URLError, 8 x 429, 3 x 504 | Record '>5if' = t, o, c, l, h, vol, price 1e5 (checked: high >= max(o, c) in 100 % of candles) |
| www.tcmb.gov.tr | robots.txt (404), one-week repo page | 1 x 200, 2 x 404 | Steps dated >= 2025 are dropped at parse |

Everything is logged in research/data/usdtry_premium/requests.log (UTC time, URL, status, bytes). Bodies and the day
table (days.npz) are in research/data/usdtry_premium/. No WebSearch was used. No key, account or e-mail was sent anywhere.

## Premium and episodes
p = BtcTurk close of the 05:00-06:00 UTC candle divided by the Dukascopy mid of the 06:00 hourly open, minus 1. That is
09:00 Istanbul (UTC+3, no DST since 2016-09). There are 1,674 valid weekdays.

Premium percentiles by year (%), p10 / p50 / p90 / max:

| year | p10 | p50 | p90 | max |
|---|---|---|---|---|
| 2018 | -2.23 | -0.40 | 1.57 | 4.61 |
| 2019 | -0.72 | 0.45 | 1.57 | 5.64 |
| 2020 | -0.44 | 0.36 | 1.30 | 8.98 |
| 2021 | -0.76 | 0.29 | 1.84 | 6.15 |
| 2022 | -0.06 | 0.85 | 1.98 | 4.28 |
| 2023 | 0.32 | 1.12 | 4.46 | 10.88 |
| 2024 | -0.13 | 0.22 | 1.46 | 4.86 |

The premium also contains the USDT / USD basis, which explains the negative 2018 median.

An episode is a run of signal days; runs with gaps of 5 or fewer trading days are merged:

| k | IS days / episodes | VAL days / episodes |
|---|---|---|
| 1 % | 173 / 31 | 295 / 23 (one episode is 161 days: 2022-10-10..2023-06-12) |
| 2 % | 55 / 25 | 128 / 17 (longest 73 days: 2023-02-09..06-01) |

## Results (bp per trade, after costs)
Prices and costs:
- Entry at the Dukascopy ASK open of the 07:00 candle; exit at the BID open of the 07:00 candle h valid trading days
  later.
- Costs are the spread (as quoted), 0.7 bp commission, and carry. Carry is r_TRY/365 - r_USD/360 + a 2 %/yr markup per
  calendar night, with r_TRY = the CBRT one-week repo and r_USD = EFFR.
- t_cl is clustered by episode (CR1). NW is Newey-West with lag h + 5.
- Random tests: "shift" moves the signal set by a random circular offset within its era, which keeps the episode
  structure; "iid" draws the same number of random days. Each uses 2,000 draws, and the column is the % of draws
  beaten.

| cell | era | n | eps | net | gross | spread | carry | t_cl | t_NW | spread+carry x1.5 | +1 h | +1 day | shift % | iid % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k1h1 | IS | 173 | 31 | -5.9 | +9.7 | 7.6 | 7.3 | -0.65 | -0.29 | -13.3 | -0.8 | +27.3 | 32 | 31 |
| k1h1 | VAL | 295 | 23 | -0.7 | +11.7 | 6.3 | 5.4 | -0.19 | -0.16 | -6.6 | +2.0 | +0.4 | 69 | 84 |
| k1h5 | IS | 173 | 31 | +77.7 | +121.8 | 7.1 | 36.4 | 1.10 | 1.40 | +55.9 | +77.1 | +71.6 | 93 | 98 |
| k1h5 | VAL | 295 | 23 | +29.2 | +64.9 | 6.3 | 28.8 | 1.60 | 1.20 | +11.6 | +31.7 | +33.5 | 75 | 99.6 |
| k1h20 | IS | 173 | 31 | +15.5 | +168.1 | 7.6 | 144.3 | 0.15 | 0.20 | -60.5 | +31.1 | +27.4 | 17 | 4 |
| k1h20 | VAL | 294 | 22 | +201.6 | +322.6 | 6.2 | 114.1 | 2.50 | 1.50 | +141.4 | +204.8 | +206.2 | 89 | 100 |
| k2h1 | IS | 55 | 25 | -65.0 | -46.9 | 9.8 | 7.5 | -1.50 | -1.30 | -73.7 | -59.3 | +4.1 | 1 | 1 |
| k2h1 | VAL | 128 | 17 | +1.9 | +13.1 | 5.9 | 4.6 | 0.49 | 0.43 | -3.3 | +6.1 | +5.2 | 78 | 88 |
| **k2h5** | IS | 55 | 25 | +87.3 | +134.6 | 8.3 | 38.3 | **1.30** | 1.50 | +63.9 | +84.2 | +121.3 | 84 | 87 |
| **k2h5** | VAL | 128 | 17 | +56.2 | +87.3 | 6.3 | 24.1 | 2.30 | 1.70 | +41.0 | +61.9 | +65.7 | 86 | 100 |
| k2h20 | IS | 55 | 25 | +17.3 | +176.0 | 7.2 | 150.8 | 0.18 | 0.21 | -61.7 | +33.4 | +51.4 | 28 | 18 |
| k2h20 | VAL | 128 | 17 | +368.2 | +471.2 | 6.0 | 96.3 | 2.30 | 1.70 | +317.0 | +373.9 | +386.0 | 96 | 100 |

The mean of random iid long entries is itself positive: about +24 bp at 5 days and +113 bp at 20 days in IS, and
+9 / +68 bp in VAL, because the lira trend outran the policy-rate carry. The "iid %" column therefore overstates the
signal. The shift test is the fair one.

Max-over-6-cells null (500 IS shift draws, % of draws whose best cell has IS t >= the cell's own IS t): k1h1 99,
k1h5 46, k1h20 92, k2h1 100, k2h5 27, k2h20 92.

### By year (net bp, n)
| cell | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| k1h5 | -68 (22) | -15 (56) | +43 (40) | +256 (55) | +27 (110) | +53 (141) | -39 (44) |
| k2h5 | +29 (9) | -15 (19) | +56 (8) | +230 (19) | +69 (26) | +75 (84) | -50 (18) |
| k1h20 | -223 | -155 | +185 | +161 | +148 | +370 | -212 |
| k2h20 | -105 | -165 | +215 | +174 | +210 | +553 | -263 |

The other cells are in backtest_out.txt. k2h5 is positive in 3 of 4 IS years and 2 of 3 VAL years. 2024, the first
year of orthodox policy at a 50 % rate, is negative in every multi-day cell.

### Concentration and power (extras_out.txt)
| cell | era | episode mean / median | episodes won | without the longest episode: net (t_cl) | HOLD power per episode / per trade |
|---|---|---|---|---|---|
| k1h5 | IS | +41 / +5 | 52 % | +9 (0.32) | 0.90 / 1.36 |
| k1h5 | VAL | +25 / -2 | 48 % | +6 (0.21) | 0.87 / 2.31 |
| k2h5 | IS | +70 / +45 | 68 % | +25 (0.72) | 1.35 / 0.69 |
| k2h5 | VAL | +21 / -11 | 29 % | +16 (0.44) | 0.52 / 2.66 |
| k1h20 | VAL | +81 / +52 | 59 % | +76 (0.68) | 1.05 / 4.66 |
| k2h20 | VAL | +84 / -20 | 47 % | +46 (0.34) | 0.66 / 4.38 |

Trade-level power counts the overlapping days of one episode as independent, so it is not the relevant number.

## Verdict per cell
| cell | IS t_cl | VAL net / t_cl | tier | why |
|---|---|---|---|---|
| k1h1 | -0.65 | -0.7 / -0.19 | none | no 1-day effect; the spread plus a night of carry eat the +10 bp gross |
| k1h5 | 1.10 | +29.2 / 1.60 | none | IS t < 2.0 |
| k1h20 | 0.15 | +201.6 / 2.50 | none | IS +15 bp, t 0.15; carry is 144 bp per trade |
| k2h1 | -1.50 | +1.9 / 0.49 | none | negative IS |
| k2h5 (IS pick) | 1.30 | +56.2 / 2.30 | none | IS t < 2.0; shift random 84 % IS / 86 % VAL (< 90 %); max-null 27 %; episode power 0.52 |
| k2h20 | 0.18 | +368.2 / 2.30 | none | IS t 0.18; VAL is the 2023 devaluation |

No PREREG_DRAFT was written.

## Why it fails
1. **It works only at regime breaks, and there are about two in seven years.** The premium is high for months while
   the official rate is held (2022-10..2023-06). Being long through that time pays the TRY carry (25-150 bp per trade
   at 5-20 days) and only gains at the break. Many short premium blips (2019, 2024) are USDT-side noise or the
   USDT / USD basis, and the official rate does not follow them.
2. **Carry.** At 20 days the policy-rate carry is 96-151 bp per trade. The real offshore swap was worse in the squeeze
   days (2018-08, 2019-03), which the model does not charge. So even the positive VAL numbers are optimistic.
3. **Under orthodox policy the premium does not lead.** 2024 is negative in every multi-day cell.

## Pitfalls for later rounds
- Dukascopy answers 429 to a User-Agent containing "(python urllib)". A plain "research-scout/1.0" is served. From this
  Mac the host was slow and flaky (503 on ~1/3 of requests, TLS timeouts), and one file from the agentFx VPS also took
  12 s. Budget about 3-5 monthly files a minute. Use hourly monthly files (2 per month), not tick hours (24 per day).
- BtcTurk klines include a candle at or after `to`. Request up to `to` minus 1 h, or cut at load. The label is the
  hour start.
- The CBRT one-week repo page also lists 2025-26 decisions. Cut at parse.
- The random-iid benchmark is gross-positive for long USDTRY (the trend beat policy carry in 2016-24). Use the shift
  benchmark.

## Deviations from the brief
- Entry is the 07:00 hourly open (one hour after the 06:00 reading), not the 06:01 M1 bar (amendment A). The reason is
  that tick hours ran at ~12 s per file. This choice can only make the fill later than the brief's, never earlier. The
  "one step late" column uses the 08:00 open.
- There is no secondary 06:01 tick check, for the same reason. For a 5-20 day hold, one hour should not move the result
  much; the "+1 h" column changes it by less than 7 bp in the k2h5 cell.

## What a user decision could unlock
Nothing worth pursuing. A rule that waits for the break could buy the first day the official rate moves more than X %
while the premium is high (a different hypothesis). With two breaks in seven years it would still have no power.
Correlation with C3 was not computed because there is no candidate.

## Files
- [HYPOTHESES_TRY.md](HYPOTHESES_TRY.md), this file, [backtest_out.txt](backtest_out.txt),
  [extras_out.txt](extras_out.txt).
- Code in code/:
  - net.py: logged GET with spacing and backoff.
  - probe.py, fetch_btcturk.py, fetch_duka.py (ticks, stopped), fetch_duka_hour.py: data pulls.
  - load.py: loaders.
  - rates_try.py: CBRT and EFFR carry.
  - align.py / align_h1.py: candle label check.
  - premium.py: day table and episodes.
  - counts.py: episode counts.
  - backtest.py: the 6 cells and random benchmarks.
  - extras.py: concentration and power.
