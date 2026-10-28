# Round 33, stream S: gold in segmented markets (SGE premium, T+D delivery direction), SNB sight deposits

Written 2026-10-27 from 19:03 UTC. Hypotheses declared in [HYPOTHESES_S.md](HYPOTHESES_S.md) at 19:14-19:16 UTC
before any return (addendum 20:05 UTC before family T's returns). Bars: research/PROMPT.md (LIVE / DEMO, no RELAXED).
HOLD (2025-01..2026-09) not used: every new series was cut at 2024-12-31 at parse, every IC price load at
ts < 2025-01-01. One HOLD-hygiene disclosure (one 2026 SGE benchmark row printed by an endpoint that ignored its end
date; not used) is in HYPOTHESES_S.md.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.** 13 declared cells; no cell has a positive IS t above 0.53 and the best
cell of each family flips sign between eras. The free SGE data do make "premium SGE" free (PROMPT listed it under paid
data), and the premium shows no next-day or multi-day information about London gold in 2016-24.

The Au(T+D) delivery direction (a daily public flag of onshore physical shortage) fails on the declared side
(IS net t -2.50 / -2.98); the reversed side is not a candidate: it was not declared, it is flat in PRE and VAL, and
most of the IS loss is the 59 % short share against gold's 2016-21 drift (the sign coefficient with an intercept is
t -1.52).

## Sources
| source | span used | notes |
|---|---|---|
| SGE Shanghai Gold Benchmark (POST www.sge.com.cn/graph/DayilyJzj) | 2016-04-19..2024-12-31 | AM and PM, CNY / g; endpoint ignores `end` |
| SGE Au99.99 daily OHLC (POST /graph/Dailyhq, instid=Au99.99) | 2016-12-19..2024-12-31 | identical to the archive on the 6 overlap days |
| SGE historical daily-quote archive (/sjzx/mrhqsj, 3,835 dated articles 2002-10..2023-12) | Au99.99 close 2012-01..2016-12; Au(T+D) direction 2014-09..2023-12 | the direction column starts 2014-09; ~2.3 s per request (server), crawled at >= 1.1 s spacing |
| SGE daily quotes 2024 (/sjzx/quotation_daily_new, inst_ids=Au(T+D)) | 2024 | direction labels 空支付给多 / 多支付给空 |
| SNB weekly sight deposits (data.snb.ch cube snbgwdchfsgw), GI | 2009-01-09..2024-12-27, 834 Fridays | cube PublishingDate = Monday 10:00 Zurich |
| IC USDCNH ticks (research/data/USDCNH/t1) -> M1 closes; Dukascopy USDCNH 2012-15 | 2012-2024 | |
| Unusable: SGE SHAU auction rounds (2024 on), SNB quarterly FX transactions (2020-Q1 on, a quarter late), IBJA (paid API), MCX (403), WGC GoldHub premium (xlsx 403 without login; chart API robots `Disallow: /`) | | |

## Premium timing (no returns)
The sd of the day-to-day change of the premium is minimal where the two legs are simultaneous. Au99.99 close: 07:30 UTC
in 2017-18, 2019-21 and 2022-24 (16.97 / 23.32 / 28.47 bp; 30 min either side +2 to +7 bp), so the close is a 15:30
Beijing print. AM benchmark: flat minimum 02:05-02:20 UTC in all groups (10:15 Beijing auction). PM benchmark: minimum
06:15-06:20 UTC in 2016-18 but 06:45-06:50 in 2019-21 and ~07:00 in 2022-24, so its clock is uncertain: not used.
Premium level (median): +22 bp PRE 2012-15, +44 IS, +66 VAL (close; it includes the CNH-CNY basis).

## Family S: onshore premium deviation from its 20-day mean -> gold / silver (side: premium up = long)
Net per trade in bp (t: day-clustered for 1-day cells, Newey-West lag = hold for overlapping cells).

| cell | PRE 2012-15 net (t) | IS net (t) | VAL net (t) | mid IS / VAL | x1.5 / +1 min IS | shift control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| S1 XAU close prem, 1 d, every day | -5.46 (-1.57), n 799 | -2.33 (-1.06), n 1,426 | +0.26 (+0.08), n 712 | -0.58 / +1.48 | -2.76 / -2.40 | 41 % / 69 % | none |
| S2 XAU close prem, 3 d | +1.04 (+0.14) | -3.17 (-0.60) | -2.15 (-0.28) | -0.88 / -0.51 | -3.61 / -3.16 | 49 % / 54 % | none |
| S3 XAU close prem top tercile (|d| >= 24.8 bp), 5 d, <= 3 open | +24.21 (+1.26), n 214 | -16.98 (-1.06), n 356 | -0.47 (-0.03), n 247 | -13.95 / +1.63 | -17.51 / -17.16 | 10 % / 56 % | none |
| S4 XAU AM-benchmark prem, 02:30 UTC, 1 d | n/a | -3.37 (-1.44), n 1,350 | -1.62 (-0.49), n 712 | -1.52 / -0.38 | -3.85 / -3.46 | 22 % / 43 % | none |
| S5 XAG close prem, 3 d | +8.32 (+0.68) | -20.82 (-1.86) | +11.92 (+0.78) | -15.72 / +17.23 | -22.65 / -20.86 | 9 % / 80 % | none |

- Dose response (mid on d / IS sd): S1 PRE +2.29 bp per sd (t 0.68), IS -3.14 (t -1.43), VAL -0.05; S3 PRE +18.95
  (t 2.52, OLS t on overlapping trades, overstated), IS -13.03 (t -2.56), VAL -5.97; S5 PRE +15.60, IS -27.31 (t -3.48),
  VAL +17.51 (t 1.88); S4 IS -5.43 (t -2.32). The slope changes sign between PRE, IS and VAL in every cell: the
  premium carries no stable information about the next 1-5 days of London gold or silver.
- Momentum control: corr(d, gold's 24 h return to the premium minute) is only -0.10..-0.13 (the same-timestamp rule
  removed the stale-leg effect); adding sign(r24) changes nothing material.
- By year (S1 net): 2012 -6.4, 2013 -11.6, 2014 -5.8, 2015 +0.7, 2016 -10.1, 2017 -4.7, 2018 +2.1, 2019 +2.1,
  2020 -3.7, 2021 +0.3, 2022 +1.8, 2023 -2.1, 2024 +1.1 (5 / 13 years > 0).
- Power: S1's best era Sharpe is ~0 (VAL +0.26 bp on a ~90 bp sd); LIVE needs 13 bp a day.

## Family T: Au(T+D) delivery direction -> gold (side: short pays long = long)
Labels per year (no column before 2014-09): long share 0.41 overall; 空付多 days 2015 89 / 244, 2020 58 / 243,
2022 161 / 242, 2024 75 / 243. Entry 07:45 UTC (fill 07:46) on the SGE day.

| cell | PRE 2014-09..2015 net (t) | IS net (t) | VAL net (t) | mid IS / VAL | x1.5 / +1 min IS | shift control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| T1 1 d | +0.82 (+0.16), n 313 | -5.50 (-2.50), n 1,422 | -3.42 (-1.05), n 711 | -3.85 / -2.37 | -5.93 / -5.53 | 4 % / 37 % | none |
| T2 3 d | -0.94 (-0.11) | -13.16 (-2.98), n 1,421 | +0.17 (+0.03) | -11.18 / +1.36 | -13.60 / -13.13 | 2.5 % / 72.5 % | none |

- With an intercept (removing the drift that a 41 / 59 long / short mix pays in a rising market) the direction's
  coefficient is IS -3.43 bp (t -1.52) / VAL -2.22 (t -0.68) for 1 d, IS -9.62 (t -2.39, OLS on overlapping trades,
  overstated) / VAL +1.94 for 3 d; adding the 24 h gold return changes little. If anything, onshore tightness comes
  after gold has been weak and says nothing reliable about the next days; not a declared side, flat in PRE and VAL.
- By year (T1 net): 2015 -6.7, 2016 -8.4, 2017 -5.7, 2018 -1.0, 2019 +5.1, 2020 -18.9, 2021 -4.1, 2022 -4.1,
  2023 -10.0, 2024 +3.8.

## Family N: SNB weekly sight deposits -> USDCHF, EURCHF proxy (side: GI up = CHF weaker)
Entry Monday 09:30 UTC after the Friday value (next weekday on Swiss holidays), threshold |ΔGI| >= 2,226 CHF mn (4-week
sum: 4,746), the IS medians. PRE excludes trades spanning 2015-01-15 (no trade was affected for N1-N4; N5 / N6 had one).

| cell | PRE 2009-15 net (t) | IS net (t) | VAL net (t) | per-trade Sharpe IS / VAL | power at VAL size (26 / yr) | Tuesday entry IS / VAL | shift control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| N1 USDCHF 1 d | +12.43 (+1.80), n 158 | +1.83 (+0.53), n 153 | -5.62 (-1.27), n 87 | 0.04 / -0.14 | -0.9 | +2.26 / +3.27 | 83 % / 15 % | none |
| N2 USDCHF 4 d | +22.24 (+1.84) | +0.81 (+0.10) | +15.73 (+1.37) | 0.01 / 0.15 | 1.0 | -2.88 / +24.70 | 69 % / 96 % | none |
| N3 EURCHF proxy 1 d | +4.64 (+0.75) | +0.07 (+0.03) | -4.39 (-1.35) | 0.00 / -0.14 | -1.0 | -1.58 / +0.84 | 83 % / 24 % | none |
| N4 EURCHF proxy 4 d | +4.97 (+0.52) | -4.58 (-1.07) | -0.12 (-0.01) | -0.09 / 0.00 | 0.0 | -5.47 / +2.27 | 53 % / 73 % | none |
| N5 USDCHF 4-week sum, 4 d | +23.83 (+1.87) | -2.20 (-0.30) | -6.63 (-0.69) | -0.02 / -0.07 | -0.5 | -6.41 / +1.54 | 53 % / 26 % | none |
| N6 EURCHF proxy 4-week sum, 4 d | +10.99 (+1.12) | -5.91 (-1.31) | -6.45 (-0.93) | -0.11 / -0.09 | -0.6 | -9.65 / -10.86 | 44 % / 47 % | none |

- PRE (the 2009-15 intervention and floor era) has the declared sign in every cell and a dose response in USDCHF
  (+7.47 bp per sd, t 3.92 for 1 d; +9.64, t 2.48 for 4 d) but it is gone from 2016: IS dose +1.93 (t 0.87) / -0.87,
  VAL -0.48 / +4.10. In PRE most of N1 sits on the release Monday itself (Tuesday entry +2.37 vs +12.43), so the
  2009-15 market was still pricing the weekly figure after 10:00 Zurich; from 2016 it was not.
- x1.5 and +1 min move nothing (USDCHF 09:30 UTC spread 0.24-0.31 bp).
- Power: even at PRE size (Sharpe 0.15) 45 HOLD trades give power ~1.0; the weekly cadence cannot reach LIVE.
- The momentum control (week's USDCHF return) was not run: no cell passes IS.

## Multiple testing
13 cells (S1-S5, T1-T2, N1-N6). Best IS net t: +0.53 (N1); the most extreme is T2 at -2.98 (declared side losing); below the chance median (~1.65) of the best of 13
nulls. No cell beats 95 % (90 %) of its circular-shift control in IS.

## Directions that need the user
- Indian premium: free WGC GoldHub account (login) for its daily India / China premium series (India from 2012, China
  from 2003; 5-day smoothed, revised in 2025) or the paid IBJA API. Value: low (~1 % LIVE): the Chinese premium, the
  larger and better-measured segmentation, shows nothing here.
- Nothing else in this stream needs a decision.

## Files
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r33/S/scripts/`):
  `fetch.py` (logged fetches), `crawl_sge_hist.py`, `fetch_td2024.py`, `build_cnh.py`, `legs.py`, `align_bench*.py`,
  `align_close.py`, `px.py` (from round 31 G), `engine.py`, `sge_series.py`, `gold_test.py`, `td_test.py`, `snb_test.py`.
- Outputs: `.../r33/S/out/` (`snb_test.txt`, `gold_S4.txt`, `gold_S1235.txt`, `td_test.txt`, `trades_*.json`);
  cut data `.../r33/S/clean/`; fetch log `.../r33/S/web/requests.log`.
