# Stream H (round 19): does the home currency weaken into its own fix, as EUR does into the ECB fix (E1)?

Hypotheses with UTC times: [HYPOTHESES_H.md](HYPOTHESES_H.md). It was written at 03:18-03:19 UTC, before any number.
The E1 code check ran at 03:21 and the declared cells at 03:22. There was one post-hoc addition at 03:24: the
declared holiday placebo, restated as a difference.

HOLD was never loaded:
- the panel ends 2024-12-31;
- Dukascopy ends 2015-12-31;
- the USDCNH cache ends 2024-12-31;
- day lists stop at 2024-12-31;
- C3's trade list was read only for its IS and VAL rows.

## Answer
- **No LIVE rule and no DEMO rule. No PREREG_DRAFT.**
- **E1's mechanism does not carry over to CAD, AUD, NZD, GBP or CHF.** For these five, the 120 minutes into the home
  fix show no weakening of the home currency in any era:
  - IS mid is between -0.88 and -0.07 bp;
  - CHF moves the wrong way (IS -0.85, t -2.03);
  - the Bank of Canada noon rate is wrong-signed in PRE (-0.85, t -1.67).
- **The one exception is the CNY onshore close.** Long USDCNH 14:30-16:30 Beijing, into the CFETS 16:30 close that
  feeds the next day's central parity:
  - mid +1.22 bp (t 4.57) in IS and +1.68 (t 4.08) in VAL, VAL/IS 1.38;
  - it beats 100 % of random windows;
  - it vanishes on mainland holidays (-0.27 against +1.38 on business days, difference t 2.10). This mechanism check
    passes, like E1's TARGET2 check.
- **But CNY-close is at cost.** Net is +0.19 (t 0.69) in IS and +0.66 (t 1.61) in VAL, against the DEMO bar of IS t 2.0.
  Power is 0.37 on the IS size and 1.23 on the VAL size, so the expected HOLD t is about 1.2.
- **CNY-close is not fully blind.** Its window lies inside round 7's "CNH home hours" (01:30-08:30 UTC). I had seen
  round 7's hourly USDCNH profile before declaring it (disclosed in the hypotheses).
- **Family chance.** Over the 23 counted cells, the best |t_IS mid| is 4.57 (CNY-close), against a shared sign-flip
  null 95th percentile of 3.14 (max of 23 normals: 3.07). Only that one cell is beyond chance.

## Fixes and their times (official sources)
| fix | time used | history | symbol |
|---|---|---|---|
| Bank of Canada noon rate | 12:00 ET. Window 11:59-12:01 from 2005-11-07, 11:55-12:05 before | last published 2017-04-28 | USDCAD |
| Bank of Canada daily rate | trimmed mean of 1-minute quotes 08:00-16:00 ET, published by 16:30 ET | from 2017-03-01 (sole rate from 2017-05-01) | USDCAD |
| RBA | 16:00 Sydney | no change found; not published on NSW holidays | AUDUSD |
| RBNZ B1 | 11:10 NZ (1991-04 to 2015-04-30), then the WM/LSEG NZFMA 14:00 NZ fix | 2015-05-01 switch | NZDUSD |
| WM/R 16:00 London (BoE "around 4pm") | 16:00 London | WM window 1 minute until 2015-02-15, then 5 minutes | GBPUSD |
| SNB | 11:00 Zurich (BFIX-based today) | no dated history found | USDCHF |
| TMA USD/CNY(HK) fixing (the CNH fix) | 11:00 Hong Kong | from 2011-06-27; transaction-based from 2016-08-01, time unchanged | USDCNH |
| CFETS CNY close | 16:30 Beijing | remains the official close after the session was extended (23:30 from 2016-01-04, 03:00 from 2023-01-03) | USDCNH |

## Design (as declared)
- **Windows** (side from the mechanism):
  - INTO = the 120 minutes ending at the fix, short the home currency;
  - AFTER15 and AFTER60 = from the fix, long the home currency.
  - The CAD daily rate's INTO is the averaging window itself (08:00-16:00 ET), and it has no AFTER60.
  - NZD uses the fix in force on each date. In PRE, H1 data force an hour-aligned proxy (09:00-11:00 and
    11:00-12:00 NZ).
- **Days:** home business days. Holidays come from holidays.json (CA-ON, AU-NSW, NZ-WGN, GB-ENG, CH-ZH) and from the
  `holidays` package (CN, HK); 24 Dec - 1 Jan is excluded.
- **Costs:**
  - IS and VAL: half the actual panel spread at the entry and exit minutes, plus 0.6 bp;
  - PRE: IC's 2016-17 spread by New York minute, plus 0.6 bp;
  - USDCNH: round 7's published 2.93 pips plus 0.6 bp. It has bid-only data, so the cost at the actual minutes is
    not observable.
  - NZD windows that cross 17:00 New York also pay the swap.
- **Code check:** the pipeline reproduces E1 exactly (PRE 3054 / +1.69 / 0.67; IS 1525 / +1.80 / net +1.17, t 3.29;
  VAL 765 / +1.97 / +1.35, t 2.46).

## Results: 23 counted cells
Mid and net are in bp per trade on the declared side, with t in brackets.
- "rand": the share of 200 random same-length windows in the home session 07:00-19:00 (rollover excluded) that the
  cell's net beats, IS / VAL.
- "hol t": the declared placebo, business-day minus holiday mean, pooled over every era with data (> 0 = supports
  the fix).

| cell | PRE mid | IS mid | VAL mid | cost IS / VAL | net IS / VAL | VAL/IS | power IS / VAL | rand IS / VAL | hol t | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| CADN-I long USDCAD 10-12 ET (to 2017-04) | -0.85 (-1.67) | -0.20 (-0.13) | - | 1.26 / - | -1.46 / - | - | <0 | 44 % / - | -2.00 | wrong sign |
| CADN-A15 short 12:00-12:15 ET | - | +0.40 (1.20) | - | 1.03 / - | -0.63 / - | - | <0 | 86 % / - | +0.93 | below cost |
| CADN-A60 short 12-13 ET | -0.47 (-1.88) | +0.67 (1.05) | - | 1.02 / - | -0.36 / - | - | <0 | 73 % / - | -0.23 | fails |
| CADD-I long 08-16 ET (2017-05 on) | - | -0.88 (-0.89) | -0.03 (-0.02) | 0.82 / 0.74 | -1.70 / -0.76 | - | <0 | 15 % / 44 % | -0.24 | none |
| CADD-A15 short 16:00-16:15 ET | - | +0.04 (0.40) | -0.10 (-1.09) | 0.86 / 0.75 | -0.82 / -0.86 | - | <0 | 49 % / 33 % | -0.72 | none |
| AUD-I short AUDUSD 14-16 Sydney | -0.05 (-0.12) | -0.37 (-0.92) | +0.58 (0.86) | 0.94 / 0.69 | -1.31 / -0.11 | - | <0 | 33 % / 86 % | +0.20 | none |
| AUD-A15 long 16:00-16:15 | - | -0.00 | -0.63 (-2.48) | 0.93 / 0.69 | -0.93 / -1.32 | - | <0 | 56 % / 1 % | -0.74 | wrong sign in VAL |
| AUD-A60 long 16-17 | +0.22 (0.70) | -0.23 (-0.77) | -0.78 (-1.62) | 0.94 / 0.68 | -1.17 / -1.46 | - | <0 | 24 % / 7 % | -1.33 | none |
| NZD-I short NZDUSD 120 min into the fix | +1.13 (1.92) | -0.24 (-0.48) | -1.12 (-1.67) | 1.62 / 2.08 | -1.86 / -3.20 | - | <0 | 6 % / 0 % | +0.94 | PRE only; cost 1.6-2.9 |
| NZD-A15 long | - | +0.20 (0.69) | +0.25 (0.53) | 1.29 / 1.23 | -1.09 / -0.97 | 1.26 | <0 | 86 % / 85 % | -0.53 | below cost |
| NZD-A60 long | -0.95 (-3.15) proxy | +0.60 (1.28) | +1.62 (2.58) | 1.28 / 1.21 | -0.69 / +0.41 (0.65) | 2.72 | <0 / 0.50 | 99 % / 100 % | +0.41 | fails (IS net < 0; +1 min VAL -0.03) |
| GBP-I short GBPUSD 14-16 London | +0.63 (1.36) | -0.07 (-0.11) | -0.27 (-0.28) | 0.82 / 0.71 | -0.89 / -0.98 | - | <0 | 40 % / 29 % | +1.00 | none |
| GBP-A15 long 16:00-16:15 | - | +0.07 (0.34) | +0.64 (2.20) | 0.80 / 0.71 | -0.73 / -0.06 | 8.6 | <0 | 73 % / 99 % | +1.32 | below cost |
| GBP-A60 long 16-17 | +0.63 (2.37) | -0.03 (-0.07) | +0.80 (1.44) | 0.80 / 0.70 | -0.83 / +0.10 | - | <0 / 0.14 | 66 % / 94 % | +1.33 | fails |
| CHF-I long USDCHF 09-11 Zurich | -0.26 (-0.36) | -0.85 (-2.03) | -0.11 (-0.14) | 0.96 / 0.90 | -1.81 / -1.01 | - | <0 | 2 % / 40 % | +1.08 | wrong sign |
| CHF-A15 short 11:00-11:15 | +0.10 (0.56) | -0.09 (-0.71) | -0.03 (-0.15) | 0.94 / 0.88 | -1.04 / -0.91 | - | <0 | 26 % / 50 % | -1.70 | none |
| CHF-A60 short 11-12 | -0.41 (-1.52) | -0.10 (-0.39) | -0.55 (-1.36) | 0.94 / 0.87 | -1.04 / -1.42 | - | <0 | 33 % / 14 % | -1.15 | none |
| CNHT-I long USDCNH 09-11 Hong Kong | - | +0.13 (0.39) | +1.40 (2.52) | 1.04 / 1.02 | -0.91 / +0.38 (0.69) | 11 | <0 / 0.53 | 34 % / 100 % | +0.01 | IS ~0; no placebo effect |
| CNHT-A15 short 11:00-11:15 | - | +0.12 (1.53) | +0.20 (1.48) | 1.04 / 1.02 | -0.92 / -0.82 | 1.66 | <0 | 97 % / 99 % | +0.61 | real-ish, 1/5 of cost |
| CNHT-A60 short 11-12 | - | +0.21 (1.43) | +0.31 (1.15) | 1.04 / 1.02 | -0.83 / -0.71 | 1.47 | <0 | 99 % / 98 % | +0.09 | below cost |
| **CNHC-I long USDCNH 14:30-16:30 Beijing** | - | **+1.22 (4.57)** | **+1.68 (4.08)** | 1.04 / 1.02 | **+0.19 (0.69) / +0.66 (1.61)** | 1.38 | **0.37 / 1.23** | 100 % / 100 % | **+2.10** | real, mechanism check passes; fails DEMO (net t) |
| CNHC-A15 short 16:30-16:45 | - | +0.21 (2.42) | +0.22 (1.41) | 1.04 / 1.02 | -0.82 / -0.79 | 1.05 | <0 | 100 % / 97 % | +2.18 | real, 1/5 of cost |
| CNHC-A60 short 16:30-17:30 | - | +0.21 (1.31) | +0.17 (0.60) | 1.04 / 1.02 | -0.83 / -0.85 | 0.80 | <0 | 98 % / 96 % | +1.45 | below cost |

### CNHC-I in detail (the only cell net > 0 in IS and VAL)
- **Years, mid / net:**
  - IS: 2016 +1.1 / +0.1, 2017 +1.6 / +0.6, 2018 +1.7 / +0.6, 2019 +1.0 / -0.0, 2020 +1.5 / +0.5, 2021 +0.5 / -0.6.
    Net is > 0 in 4 of 6 years.
  - VAL: 2022 +1.8 / +0.8, 2023 +2.0 / +1.0, 2024 +1.2 / +0.2. Net is > 0 in 3 of 3 years.
- **Stress tests:**
  - spread x1.5: net -0.03 IS / +0.45 VAL;
  - both fills one minute late: +0.17 / +0.64.
- **Random-entry control:** the cell beats 100 % / 100 % of random windows. The random means are -0.79 / -0.55 net
  and +0.25 / +0.47 mid. USDCNH drifts up through the Asian day, and this window is about 1 bp above that drift.
- **Holiday placebo:**
  - mainland holidays: -0.27 bp (152 days, 53 blocks), against +1.38 on business days, difference t 2.10;
  - by era: IS +0.84 (t 1.02), VAL -2.29 (t -1.58).
  - The holidays are mainly Golden Week and Spring Festival, when CNH trades but the onshore market is closed.
- **C3 correlation (IS + VAL):** daily -0.002, monthly +0.065.
- **Distance from the bars:**
  - DEMO needs IS net t >= 2.0. With an IS per-trade sd of about 10.1 bp, that means net >= 0.53, so a round trip of
    at most about 0.69 bp, against the 1.04 assumed here.
  - LIVE at the VAL size (sd about 11 bp, about 410 HOLD trades) needs about 1.6 bp net, which is impossible at any
    cost.

### Mechanism predictions (information cells)
| prediction | result |
|---|---|
| CAD noon window smaller after the noon rate stopped (2017-05 on) | there was nothing to lose: -0.20 (to 2017-04) and then -0.19 IS / -0.80 VAL (t -1.14); AFTER60 +0.67 then +0.04 / -0.05 |
| CAD daily-rate window ~0 before the daily rate existed | PRE -0.12, IS 2016-17 -0.54; after the rate existed it was also ~0 or negative |
| NZ 11:10 window smaller after 2015-04 | -0.39 IS / -0.15 VAL, at a cost of 3.5-5.4 bp (the window sits on the New York rollover) |
| NZ 14:00 window smaller before 2015-05 | **opposite**: PRE 12:00-14:00 NZ +1.04 (t 2.22) before it was the fix; -0.24 IS / -1.12 VAL after |
| holiday placebo (fix not published → smaller) | supports only CNY-close (t 2.10) and its 15-minute rebound (2.18); CAD noon goes the other way (t -2.00); the rest are \|t\| <= 1.7 |

## Chance and family count
| item | value |
|---|---|
| cells counted | 23 (8 INTO, 15 AFTER), plus 6 information cells and the E1 check |
| best \|t_IS mid\| | 4.57 (CNHC-I); next 2.42 (CNHC-A15), -2.03 (CHF-I, wrong side) |
| shared per-date sign-flip null of the max \|t\| (500 draws) | median 2.14, 95 % 3.14, p < 0.002 |
| max of 23 \|normals\| | median 2.17, 95 % 3.07 |
| cells positive at mid in IS | 12 / 23 (chance 11.5) |
| INTO cells with the predicted sign, IS / VAL | 2 / 8 and 3 / 7 (CNH twice in both; AUD in VAL) |

## What this says
- **E1 is a euro-area mechanism, not a general rule.** The ECB fix is a point-in-time reference that euro-area funds
  and corporates actually trade at. The other central-bank rates here are indicative publications:
  - RBA 16:00, SNB 11:00 and BoE 4pm are observations of the market, not dealing fixes. None of them moves its
    currency into the publication time.
  - The Bank of Canada noon rate was used contractually, but USDCAD did not rise into it over 2004-2017. The
    Canadian flow seems to trade at WM/R 16:00 London instead.
- **The renminbi is the exception, where the official fix has teeth.** The 16:30 CFETS close enters the next day's
  central-parity formula, and onshore corporates square positions before it.
  - CNH weakens into it by about 1.2-1.7 bp in both eras, and not on mainland holidays.
  - But it is at IC's ~1 bp CNH cost. Round 7 had found this inside its broader "CNH home hours" window, so this is a
    sharper and mechanism-checked version of round 7's result, not a new effect.
- **"Declared from a mechanism" also gives honest negatives.** Of the 8 INTO cells, only the one with a real dealing
  fix behind it worked.

## Directions that need the user
1. **USDCNH ask or tick data from IC for 2016-24.** Only bid M1 exists here, so the CNY-close cost is round 7's
   published average (2.93 pips). If IC's actual CNH spread at 06:30-08:30 UTC (CNH's liquid hours) is well under 2.93
   pips, CNHC-I's IS net t could approach the DEMO line. That needs a round trip of about 0.69 bp or less, which is
   below the 0.6 bp commission plus about 0.6 pip of spread, so it is unlikely at IC. It cannot reach LIVE at any
   cost.
2. **Other fix currencies are not in the data:** USDSGD (MAS), USDHKD (TMA 11:00), USDMXN (Banxico FIX 12:00 Mexico
   City), USDZAR, and the Scandinavians. They would need new price series from IC. They are the natural next places
   for the CNY-close mechanism, where official fixes are used for dealing.

## Sources
- Bank of Canada:
  - [noon-rate window change, 2005-11-07](https://www.bankofcanada.ca/2005/10/changes-regarding-noon-foreign-exchange-rates/)
  - [future changes, 2016-02](https://www.bankofcanada.ca/2016/02/bank-canada-announces-future-changes-published-foreign-exchange-rate-data/)
  - [details, 2016-12](https://www.bankofcanada.ca/2016/12/bank-canada-announces-details-forthcoming-changes/)
  - [new data, 2017-03](https://www.bankofcanada.ca/2017/03/bank-canada-begins-publishing-new-foreign-exchange/)
  - [methodology (08:00-16:00 ET trimmed mean, by 16:30 ET)](https://www.bankofcanada.ca/rates/exchange/background-information-on-foreign-exchange-rates/)
- RBA: [exchange-rate statistics (4pm; not published on NSW holidays)](https://www.rba.gov.au/statistics/frequency/exchange-rates.html) and its [RSS notes](https://www.rba.gov.au/rss/rss-cb-exchange-rates.xml).
- RBNZ: [B1 series notes](https://www.rbnz.govt.nz/statistics/series/exchange-and-interest-rates/exchange-rates-and-the-trade-weighted-index)
  ("1 April 1991 - 30 April 2015 11:10am mid-rates; from 1 May 2015 WM/LSEG 2:00pm fixes from NZFMA"). The page is
  Cloudflare-protected, so it was read through search snippets. Also the [NZFMA 2pm fix](https://www.rbnz.govt.nz/hub/statistics/discontinued/nzfma-nzd-usd-2pm-fix).
- Bank of England: [daily spot rates notes (around 4pm)](https://www.bankofengland.co.uk/boeapps/database/Rates.asp). WM/R
  window change of 2015-02-15 per the FSB Foreign Exchange Benchmarks final report (2014).
- SNB: [current interest and exchange rates (BFIX-based)](https://www.snb.ch/en/the-snb/mandates-goals/statistics/statistics-pub/current_interest_exchange_rates),
  with an 11:00 Zurich update time. No dated history was found, so the time is assumed constant.
- HKMA / TMA:
  - [launch of the USD/CNY(HK) fixing, 2011-06-23](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2011/06/20110623-3/) and [specifications annex](https://www.hkma.gov.hk/media/eng/doc/key-information/press-release/2011/20110623e3a1.pdf)
  - [transaction-based from 2016-08-01](https://www.tma.org.hk/information/news-press-releases/transiting-tma-usdhkd-and-usdcnyhk-spot-rates-to-transactionbased-regime-282)
- CFETS / PBC:
  - [trading-hours extension notice 2022-12-30](https://www.chinamoney.com.cn/english/rarfmrrudrgl/20221230/2526819.html)
  - [PBC/SAFE Q&A 2015-12-30 (16:30 stays the close)](https://www.safe.gov.cn/en/2015/1230/1179.html)
- Literature: Ranaldo (2009, JBF); Breedon & Ranaldo (2013, JMCB); Krohn, Mueller & Whelan (2024, JF).

## Scripts and outputs
Folder `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r19/H/`:
- `make_hol.py`: CN and HK holidays from the `holidays` package (scratch venv). Output `hol_cn_hk.json`.
- `hcommon.py`: the declared cells, local-clock windows, grids (stream M's Dukascopy and panel grids, and the
  USDCNH bid cache), costs, swap and stats.
- `h0_check.py`: the E1 reproduction.
- `h1_cells.py`: all cells by era and year, x1.5, +1 minute, the random-entry control, the holiday placebo, the
  sign-flip null and the C3 correlation. Outputs `h1.out` and `h1_results.pkl`.
- `h2_placebo_diff.py`: the holiday placebo as a business-day minus holiday difference. Output `h2.out`.
