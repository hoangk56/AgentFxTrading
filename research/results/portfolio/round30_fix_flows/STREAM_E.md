# Round 30, stream E: H-EMFIX and H-CNH tested as declared

Started 2026-10-18 09:22 UTC. Details fixed before any return are in [HYPOTHESES_E.md](HYPOTHESES_E.md), written
09:37:47-09:38:46 UTC. This file is filled in the declared order. Every PRE number below was written, with its
`date -u` time, before the IS / VAL number of the same cell was computed. The final write-up follows the log.

## Log, in the declared order
### 09:44:50 UTC: MX-1 on PRE, computed at 09:44:44 UTC. No IS / VAL return of any MX cell computed yet.
- **Data:** Dukascopy M1 USDMXN, 2007-03-13 to 2015-12-23.
- **Rule:** long USDMXN from the last bid before 09:00 to the last bid before 12:00 Mexico City, on Mexican banking
  days.
- **Cost:** IC's 2016-17 spread profile by local weekday x minute, + 0.6 bp. It averages 2.10 bp a round trip.

**Result:** 2,111 trades.
- Mid +2.28 bp (t 2.87).
- Net +0.19 bp (t 0.23). sd 36.5 bp.
- Net > 0 in 6 of 9 years.

**By year, mid / net (bp):**

| year | mid | net |
|---|---|---|
| 2007 | +0.7 | -1.4 |
| 2008 | +3.9 | +1.8 |
| 2009 | +3.5 | +1.4 |
| 2010 | +2.3 | +0.2 |
| 2011 | +2.8 | +0.7 |
| 2012 | -1.4 | -3.5 |
| 2013 | +0.8 | -1.3 |
| 2014 | +3.8 | +1.7 |
| 2015 | +3.9 | +1.8 |

**Stress tests:**
- spread x1.5: net -0.56;
- both fills +1 minute: mid +2.34, net +0.52.

**Dukascopy's own quotes (information).** On the 1,490 days with valid asks: mid +2.06 (t 2.44); net -1.44 at
Dukascopy's own spread.

**Random control** (500 seeds, +-180 min). The random windows average mid +1.04, net -0.80. MX-1 beats 97.0 % of seeds
on mid and 93.6 % on net.

### 09:45:51 UTC: PRE of the MX information cells and of CN-1, computed 09:45:35-09:45:36 UTC. Still no IS / VAL return.
Same conventions as above: the IC 2016-17 profile + 0.6 bp as cost, mid = bid to bid. MX-15's control was skipped
by an assertion at 09:45:08 (the grid ended at 15:05 MX); the grid now reaches 15:20 MX, and MX-1 PRE reproduced
unchanged after the rebuild.

**MX-15 (short 12:00 -> 12:15 MX).**
- 2,113 trades: mid -0.15 (t -0.63), cost 1.82, net -1.96 (t -8.55).
- No rebound after the FIX window. Random control: 40.8 % (mid).

**MX-H (FIX-less Mexican bank holidays, long 09:00 -> 12:00).**
- Holidays: mid -3.59 (t -0.80) over 60 days in 58 blocks.
- Banking days: +2.28.
- Difference +5.87 (t 1.29), in the predicted direction but not significant. Holiday net -5.61.

**MX-W (MX-1 split at the WMR minute).** On days with WMR = 10:00 MX:
- part A, 09:00 -> 10:00: mid +1.81 (t 3.40), net -0.18;
- part B, 10:00 -> 12:00: mid +0.60 (t 1.00), net -1.14.

Most of the PRE effect comes before the WMR minute, and part B is not a reversal. On the 41 days of 2007-15 with WMR
= 09:00 MX, MX-1 mid is -4.13 (t -0.81); this is information only.

**MX-C (the 183 PRE days with a 2-hour NY - Mexico City gap).**
- Mexico City clock, 09:00 -> 12:00 MX: mid +3.22 (t 1.09), net +1.12.
- New York clock, 10:00 -> 13:00 NY (08:00 -> 11:00 MX): mid +0.96 (t 0.29), net -0.94.
- MX - NY: +2.26 (t 1.03).
- Reference: MX-1 on the 1-hour-gap days is +2.19 (t 2.66).

**MX-A (short 10:00 -> 11:00 MX, 2015 only).**
- Auction days (2015-03-11..11-20, n 159): mid -0.09 (t -0.06).
- Other 2015 days (n 67): mid -5.10 (t -2.21).
- Difference +5.01 (Welch t 1.88), in the predicted direction.
- Sub-periods: USD 52 m days +1.32 (t 0.85, n 98); USD 200 m days -2.35 (t -0.95, n 61).

**CN-1 PRE (long USDCNH 06:30 -> 08:30 UTC, 2012-06-27..2015-12-23).**
- 806 trades: mid +0.10 (t 0.46), cost 1.60, net -1.50 (t -6.59). sd 6.45.
- Mid by year: 2012 -0.33, 2013 -0.40, 2014 -0.03, 2015 +0.91.
- Random control: 10.6 % (mid), 11.0 % (net).
- There is no CNY-close effect before 2016.

### 09:46:27 UTC: code check. Round 19's CNHC-I reproduced from the IC M1 bid bars (files before 2025 only)
- IS: n 1,428, mid +1.228 (t 4.59). Round 19: +1.22 (t 4.57).
- VAL: n 711, mid +1.689 (t 4.09). Round 19: +1.68 (t 4.08).

The day set and clock conventions match round 19. The small gap comes from `holidays` 0.106 vs 0.105.

### 09:50 UTC: IS 2016-21 computed for MX-1, the MX information cells and CN-1. VAL ticks still arriving
- IC 2022-24 USDMXN and USDCNH files are still being pulled; the full IS / VAL tables are below.
- MX-1's IS number (mid -0.82, t -0.80; net -2.69, t -2.64) was computed at 09:50:18 UTC, after its PRE entry above.

### 10:00:28 UTC: MX cells on IS / VAL. USDMXN IC 2016-24 complete: 366 / 365 files, none on or after 2025
**MX-1** fails, with the wrong sign in both eras.
- IS: mid -0.82 (t -0.80), net -2.69 (t -2.64).
- VAL: mid -2.55 (t -2.01), net -4.28 (t -3.37).
- Net > 0 in 0 of 9 years. Random control: 14.8 % (IS) and 1.0 % (VAL) on net.
- MX-H pooled 2007-24: holiday mid +1.25 (t 0.41, 121 days, 118 blocks) vs banking days +0.40, difference -0.85
  (t -0.28).

Full tables are in the write-up below.

### 10:07:32 UTC: CN-1 on IS / VAL. USDCNH IC 2016-24 complete: 3,288 tick days, none on or after 2025
**CN-1** is real at mid but fails DEMO on IS net t.
- IS: mid +1.23 (t 4.61), cost 1.15, net +0.08 (t 0.30).
- VAL: mid +1.71 (t 4.16), cost 1.06, net +0.65 (t 1.58).
- Random control: 100 % in both eras.

### 10:08 UTC: data integrity
- All three pulls report 3,288 tick days (2016-01-01..2024-12-31).
- Every IC grid used was rebuilt from the final files at 10:08 UTC; all 27 symbol-years are identical.

SG-1 waits for Dukascopy USDSGD 2012-15: its PRE must be written before its IS / VAL.

### 10:32:48 UTC: SG-1 on PRE, computed 10:32:39 UTC. No IS / VAL return of SG-1 computed yet.
- **Data:** Dukascopy M1 USDSGD, 2004-11-17..2015-12-23. Cost: IC's 2016-17 profile + 0.6 bp, 1.30 bp a round trip
  on average.
- **Result:** 2,657 trades. Mid -0.15 (t -0.41). Net -1.46 (t -3.98). sd 18.9. Net > 0 in 2 of 12 years.
- **Stress tests:** spread x1.5 net -1.81; +1 minute mid +0.19, net -1.11.
- **Dukascopy's own quotes (1,394 days):** mid +0.20 (t 0.58).
- **Random control:** 16.6 % (mid), 27.0 % (net).
- **Gotobi days** (n 739): mid +0.20 (t 0.47). **Non-gotobi days** (n 1,918): mid -0.29 (t -0.60).

---

# Write-up (10:34 UTC, after every number above)

## Answer
- **No cell meets the LIVE or DEMO bar, so there is no PREREG_DRAFT.** HOLD was never opened.
- **MX-1, the primary cell (long USDMXN into the Banxico FIX window, 09:00-12:00 Mexico City), fails.**
  - PRE 2007-15 was positive: mid +2.28 bp (t 2.87), better than 97 % of random windows.
  - The sign then reverses: IS mid -0.82 (t -0.80), net -2.69 (t -2.64); VAL mid -2.55 (t -2.01), net -4.28
    (t -3.37). Net is > 0 in 0 of 9 IS + VAL years.
  - None of the mechanism checks supports the FIX as a dealing fix in 2016-24:
    - FIX-less holidays are not smaller than FIX days;
    - after the WMR minute the USD falls rather than rises;
    - MX-15 shows no rebound.
- **CN-1 / H-CNH (long USDCNH 14:30 -> 16:30 Beijing into the CFETS close) is real at mid but below the cost.**
  - Mid +1.23 (t 4.61) IS and +1.71 (t 4.16) VAL; it beats 100 % of random windows.
  - At IC's actual bid/ask the round trip is 1.15 bp in IS and 1.06 bp in VAL, against the <= ~0.69 bp the DEMO bar
    needs. Net is +0.08 (t 0.30) IS and +0.65 (t 1.58) VAL.
  - Power at the VAL size is 1.20 (0.09 at x0.65). It fails DEMO on IS net t, and spread x1.5 is < 0 in IS.
  - This is what round 25 predicted; round 19's assumed 1.04 / 1.02 bp cost was, if anything, slightly optimistic.
- **SG-1 (long USDSGD into the ABS VWAP, 09:00-11:00 SGT) has no effect in any era.**
  - Mid: PRE -0.15 (t -0.41), IS -0.24 (t -0.97), VAL -0.23 (t -0.65).
  - Net: -1.30 (t -5.22) IS, -1.39 (t -3.99) VAL.
  - Gotobi days do not differ from the other days. Its daily correlation with C3 is +0.05.
- **The BOOK (equal-risk MX-1 + SG-1 + CN-1) loses.** Net -0.19 R per day in IS (t -4.40) and in VAL (t -3.07);
  power -2.36 IS, -2.33 VAL. The only real leg, CN-1, is sub-cost, and the other two legs have no edge.
- **Chance.** Best |t_IS mid| over the 4 counted cells is 4.61 (CN-1). That is beyond a shared per-date sign-flip null
  (95 % at 2.45, p < 0.001) and the max of 4 normals (95 % at 2.49). No other counted cell is beyond chance.

## Results table (counted cells, plus MX-15 for information)
Units: bp per trade (BOOK: R per day = units of each leg's IS per-trade net sd); t is day-clustered.
- PRE: Dukascopy bid-to-bid return, cost = IC 2016-17 profile + 0.6 bp.
- IS / VAL: IC ticks, ask in / bid out, + 0.6 bp.
- Random: the share of 500 random-shift seeds whose mean net is below the cell's.
- Power: per-trade net Sharpe x sqrt(1.73 x trades a year). The decay readings are at the VAL size.

| cell | PRE mid (t); net | IS mid (t) | VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS mid | power IS / VAL size | random net IS / VAL | x1.5 IS / VAL | +1 min IS / VAL | years net>0 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MX-1 | +2.28 (2.87); net +0.19 | -0.82 (-0.80) | -2.55 (-2.01) | 1.87 / 1.73 | -2.69 (-2.64) / -4.28 (-3.37) | n/a (both < 0) | -1.42 / -2.56 (x0.65 -2.02, x0.30 -1.49) | 15 / 1 % | -3.33 / -4.84 | -1.94 / -4.15 | 0/9 | fails (wrong sign IS and VAL) |
| SG-1 | -0.15 (-0.41); net -1.46 | -0.24 (-0.97) | -0.23 (-0.65) | 1.06 / 1.17 | -1.30 (-5.22) / -1.39 (-3.99) | n/a | -2.80 / -3.03 (x0.65 -2.86, x0.30 -2.69) | 9 / 23 % | -1.52 / -1.68 | -1.20 / -1.41 | 0/9 | fails (no effect) |
| CN-1 | +0.10 (0.46); net -1.50 | +1.23 (4.61) | +1.71 (4.16) | 1.15 / 1.06 | +0.08 (0.30) / +0.65 (1.58) | 1.39 | 0.16 / 1.20 (x0.65 0.09, x0.30 -1.01) | 100 / 100 % | -0.20 / +0.42 | +0.06 / +0.62 | 7/9 | fails DEMO (IS net t 0.30 < 2.0; x1.5 IS < 0) |
| BOOK | +0.032 (0.82); net -0.185 | +0.070 (1.60) | +0.072 (1.18) | (legs) | -0.191 (-4.40) / -0.187 (-3.07) | 1.04 | -2.36 / -2.33 (x0.65 -2.64, x0.30 -2.96) | 94 / 85 % | -0.256 / -0.251 | -0.164 / -0.188 | 0/9 | fails |
| MX-15 (info) | -0.15 (-0.63); net -1.96 | +0.10 (0.35) | -0.10 (-0.32) | 1.69 / 1.64 | -1.59 (-5.59) / -1.74 (-5.56) | - | -3.00 / -4.22 | 69 / 17 % | -2.14 / -2.25 | -1.46 / -1.62 | 0/9 | no rebound |

**Per-trade net Sharpe:**

| cell | IS | VAL |
|---|---|---|
| MX-1 | -0.069 | -0.124 |
| SG-1 | -0.136 | -0.147 |
| CN-1 | +0.008 | +0.059 |
| BOOK, per day | -0.113 | -0.111 |

**Trades a year:** MX-1 246-247, SG-1 246, CN-1 237-238, BOOK 254 days.

## Counted cells in detail
### MX-1 (USDMXN long, 09:00 -> 12:00 Mexico City, Mexican banking days)
| year | era | n | mid | net |
|---|---|---|---|---|
| 2007 | PRE | 196 | +0.72 | -1.37 |
| 2008 | PRE | 246 | +3.89 | +1.79 |
| 2009 | PRE | 244 | +3.47 | +1.37 |
| 2010 | PRE | 244 | +2.30 | +0.20 |
| 2011 | PRE | 239 | +2.84 | +0.74 |
| 2012 | PRE | 247 | -1.38 | -3.48 |
| 2013 | PRE | 233 | +0.84 | -1.26 |
| 2014 | PRE | 236 | +3.80 | +1.71 |
| 2015 | PRE | 226 | +3.89 | +1.79 |
| 2016 | IS | 247 | +0.10 | -2.33 |
| 2017 | IS | 245 | -0.57 | -2.34 |
| 2018 | IS | 245 | -2.32 | -3.82 |
| 2019 | IS | 246 | -1.31 | -2.59 |
| 2020 | IS | 247 | -1.22 | -3.61 |
| 2021 | IS | 247 | +0.41 | -1.47 |
| 2022 | VAL | 247 | -0.59 | -2.41 |
| 2023 | VAL | 247 | -5.52 | -7.39 |
| 2024 | VAL | 246 | -1.54 | -3.02 |

| era | n | mid (t) | cost mean / median | net (t) | sd | x1.5 net (t) | +1 min mid / net (t) | random mean mid / net | beats random mid / net |
|---|---|---|---|---|---|---|---|---|---|
| PRE | 2,111 | +2.28 (2.87) | 2.10 / 2.07 | +0.19 (0.23) | 36.5 | -0.56 (-0.71) | +2.34 / +0.52 (0.65) | +1.04 / -0.80 | 97.0 / 93.6 % |
| IS | 1,477 | -0.82 (-0.80) | 1.87 / 1.66 | -2.69 (-2.64) | 39.2 | -3.33 (-3.26) | -0.24 / -1.94 (-1.91) | -0.09 / -1.80 | 20.0 / 14.8 % |
| VAL | 740 | -2.55 (-2.01) | 1.73 / 1.56 | -4.28 (-3.37) | 34.5 | -4.84 (-3.81) | -2.58 / -4.15 (-3.30) | -0.41 / -1.98 | 1.4 / 1.0 % |

- Robustness: IS net without Mar-Apr 2020 -2.45 (t -2.48). 1 %-winsorised net: IS -2.29 (t -2.41), VAL -4.23
  (t -3.43).
- Daily correlation with C3: +0.02; monthly -0.04.

### SG-1 (USDSGD long, 09:00 -> 11:00 Singapore, SG business days)
| year | era | n | mid | net | year | era | n | mid | net |
|---|---|---|---|---|---|---|---|---|---|
| 2004 | PRE | 23 | +3.06 | +1.75 | 2015 | PRE | 230 | +2.42 | +1.12 |
| 2005 | PRE | 246 | +0.79 | -0.52 | 2016 | IS | 248 | +1.50 | -0.04 |
| 2006 | PRE | 246 | -1.05 | -2.35 | 2017 | IS | 246 | -1.17 | -2.24 |
| 2007 | PRE | 245 | +0.31 | -0.99 | 2018 | IS | 246 | -0.52 | -1.37 |
| 2008 | PRE | 246 | -0.06 | -1.36 | 2019 | IS | 245 | -0.48 | -1.25 |
| 2009 | PRE | 245 | -3.05 | -4.35 | 2020 | IS | 247 | -0.42 | -1.35 |
| 2010 | PRE | 240 | -1.52 | -2.82 | 2021 | IS | 247 | -0.37 | -1.55 |
| 2011 | PRE | 228 | +0.38 | -0.93 | 2022 | VAL | 246 | -0.68 | -1.92 |
| 2012 | PRE | 228 | -0.86 | -2.17 | 2023 | VAL | 245 | -0.17 | -1.28 |
| 2013 | PRE | 238 | +0.63 | -0.67 | 2024 | VAL | 247 | +0.17 | -0.99 |
| 2014 | PRE | 242 | +0.18 | -1.12 | | | | | |

| era | n | mid (t) | cost mean / median | net (t) | sd | x1.5 net (t) | +1 min mid / net (t) | random mean mid / net | beats random mid / net |
|---|---|---|---|---|---|---|---|---|---|
| PRE | 2,657 | -0.15 (-0.41) | 1.30 / 1.29 | -1.46 (-3.98) | 18.8 | -1.81 (-4.94) | +0.19 / -1.11 (-4.84) | +0.15 / -1.26 | 16.6 / 27.0 % |
| IS | 1,479 | -0.24 (-0.97) | 1.06 / 0.94 | -1.30 (-5.22) | 9.6 | -1.52 (-6.15) | -0.14 / -1.20 (-4.79) | +0.09 / -1.04 | 5.2 / 9.0 % |
| VAL | 738 | -0.23 (-0.65) | 1.17 / 1.16 | -1.39 (-3.99) | 9.5 | -1.68 (-4.81) | -0.20 / -1.41 (-4.09) | +0.04 / -1.21 | 13.4 / 23.4 % |

**Gotobi split** (`gotobi_days`, Singapore date), mid (t) / net:

| era | gotobi | non-gotobi |
|---|---|---|
| PRE | +0.20 (0.47), n 739 / -1.12 | -0.29 (-0.60), n 1,918 / -1.59 |
| IS | -0.09 (-0.16), n 405 / -1.16 | -0.30 (-1.12), n 1,074 / -1.35 |
| VAL | -0.57 (-0.85), n 206 / -1.73 | -0.09 (-0.23), n 532 / -1.26 |

SG-1 does not depend on the gotobi calendar, and it has no edge on either day type.

**Correlation with C3** (IS + VAL only, C3 = 0 on its non-trading days):
- daily +0.052 (2,217 days);
- gotobi days only +0.096 (611);
- days both trade +0.087 (638);
- monthly -0.039 (108 months).

### CN-1 (USDCNH long, 06:30 -> 08:30 UTC = 14:30 -> 16:30 Beijing, CN business days) = H-CNH
| year | era | n | mid | net | year | era | n | mid | net |
|---|---|---|---|---|---|---|---|---|---|
| 2012 | PRE | 123 | -0.33 | -1.93 | 2019 | IS | 238 | +1.03 | +0.16 |
| 2013 | PRE | 218 | -0.40 | -2.00 | 2020 | IS | 237 | +1.53 | +0.54 |
| 2014 | PRE | 227 | -0.03 | -1.63 | 2021 | IS | 237 | +0.53 | -0.47 |
| 2015 | PRE | 238 | +0.91 | -0.69 | 2022 | VAL | 237 | +1.84 | +0.67 |
| 2016 | IS | 239 | +1.09 | -0.84 | 2023 | VAL | 237 | +2.08 | +0.93 |
| 2017 | IS | 239 | +1.52 | +0.25 | 2024 | VAL | 237 | +1.22 | +0.35 |
| 2018 | IS | 238 | +1.69 | +0.86 | | | | | |

| era | n | mid (t) | cost mean / median | net (t) | sd | x1.5 net (t) | +1 min mid / net (t) | random mean mid / net | beats random mid / net |
|---|---|---|---|---|---|---|---|---|---|
| PRE (2012-06..2015) | 806 | +0.10 (0.46) | 1.60 / 1.60 | -1.50 (-6.59) | 6.5 | -2.00 (-8.79) | +0.20 / -1.40 (-6.19) | +0.30 / -1.30 | 10.6 / 11.0 % |
| IS | 1,428 | +1.23 (4.61) | 1.15 / 0.99 | +0.08 (0.30) | 10.1 | -0.20 (-0.73) | +1.21 / +0.06 (0.23) | +0.25 / -0.90 | 100 / 100 % |
| VAL | 711 | +1.71 (4.16) | 1.06 / 1.06 | +0.65 (1.58) | 11.0 | +0.42 (1.02) | +1.69 / +0.62 (1.50) | +0.41 / -0.65 | 100 / 100 % |

- **Distance to the bars:**
  - DEMO needs IS net >= 2.0 x 10.11 / sqrt(1,428) = 0.54 bp, i.e. an IS round trip <= 0.70 bp. That is <= 0.10 bp of
    spread on top of the commission; the measured round trip is 1.15 bp.
  - With IC's spreads and no commission at all, IS net would be +0.68 (t ~2.5); this is arithmetic only.
  - LIVE at the VAL size needs net >= 1.63 bp, i.e. a cost below about 0.09 bp: impossible.
- **Robustness:**
  - IS net without Mar-Apr 2020: -0.04;
  - 1 %-winsorised: IS +0.11 (t 0.44), VAL +0.73 (t 1.93).
- **C3 correlation:** daily -0.004, monthly +0.027.
- **No PRE effect in 2012-15.** Post hoc reading: the effect starts in the era when the previous 16:30 close became an
  input to the next day's central parity (the PBOC's August 2015 reform). That fits the mechanism but was not a
  declared test.

### BOOK (MX-1 + SG-1 + CN-1, each trade x 1 / IS per-trade sd)
**Weights.** IS per-trade net sd: MX-1 39.20 bp, SG-1 9.56 bp, CN-1 10.11 bp.

| era | days (per yr) | legs/day | mid R (t) | net R (t) | sd | x1.5 | +1 min | power | sqrt-sum-sq of leg powers | beats random |
|---|---|---|---|---|---|---|---|---|---|---|
| PRE | 2,778 | 2.01 | +0.032 (0.82) | -0.185 (-4.72) | - | - | - | - | - | - |
| IS | 1,522 (254) | 2.88 | +0.070 (1.60) | -0.191 (-4.40) | 1.70 | -0.256 | -0.164 | -2.36 | 0.16 | 93.8 % |
| VAL | 763 (254) | 2.87 | +0.072 (1.18) | -0.187 (-3.07) | 1.69 | -0.251 | -0.188 | -2.33 | 1.20 | 84.6 % |

- VAL decay: x0.65 -0.212 R (power -2.64); x0.30 -0.238 R (power -2.96).
- Net is < 0 in every IS and VAL year (0/9).

## Information and placebo cells (USDMXN; declared predictions in brackets)
| cell | PRE | IS | VAL | reading |
|---|---|---|---|---|
| MX-15 short 12:00 -> 12:15 [rebound > 0] | -0.15 (t -0.63) | +0.10 (0.35) | -0.10 (-0.32) | no rebound in any era |
| MX-H holidays, long 09-12 [holiday ~0, below FIX days] | holiday -3.59 (t -0.80, 60 days, 58 blocks) vs FIX days +2.28: diff +5.87 (t 1.29) | holiday +6.52 (t 1.27, 40 days) vs -0.82: diff -7.34 (t -1.41) | holiday +5.04 (t 0.75, 21 days) vs -2.55: diff -7.60 (t -1.11) | right direction in PRE only. Pooled 2007-24: holiday +1.25 (t 0.41, 121 days, 118 blocks) vs +0.40, diff -0.85 (t -0.28). IS + VAL: diff -7.41 (t -1.80), opposite to the prediction. The holiday round trip is 2.29 bp |
| MX-W part A 09:00 -> WMR (10:00 MX days) [FIX: > 0; KMW: > 0] | +1.81 (t 3.40) | +0.58 (0.83) | +1.40 (1.21) | the PRE effect sits here |
| MX-W part B WMR -> 12:00 [FIX: > 0; KMW: < 0] | +0.60 (t 1.00) | -1.50 (-1.92) | -3.08 (-2.66) | USD falls after WMR in IS / VAL: KMW's reversal, not the FIX |
| MX-W sign test 2023-24: MX-1, WMR at 09:00 MX (UK summer) vs at 10:00 | - | - | -3.76 (t -1.81, n 299) vs -3.18 (t -1.24, n 194); diff -0.59 (t -0.18) | USD falls over the window on both kinds of day; neither sign is singled out |
| MX-1 on the WMR-09:00 days (info) | -4.13 (t -0.81, n 41) | 2016-22: +1.80 (t 0.21, n 31) | (above) | too few days |
| MX-C 2-hour-gap days: MX clock (09-12 MX) vs NY clock (10-13 NY = 08-11 MX) [MX > NY] | n 183: +3.22 (1.09) vs +0.96 (0.29); diff +2.26 (t 1.03) | n 114: -2.98 (-0.63) vs -2.69 (-0.49); diff -0.28 (t -0.05) | n 347: -3.45 (-1.81) vs +0.12 (0.05); diff -3.58 (t -1.86) | VAL (mostly 2023-24) follows the Mexico City clock, but with the wrong sign |
| MX-1 on the 1-hour-gap days (reference) | +2.19 (t 2.66) | -0.64 (-0.62) | -1.76 (-1.03) | |
| MX-A short 10:00 -> 11:00, 2015 [auction days > other days] | auction days -0.09 (t -0.06, n 159) vs other 2015 days -5.10 (t -2.21, n 67); diff +5.01 (Welch t 1.88) | - | - | USD 52 m days +1.32 (t 0.85, n 98); USD 200 m days -2.35 (t -0.95, n 61): no size response |

## Chance and family count
- **Counted cells:** 4 (MX-1, SG-1, CN-1, BOOK), as declared. Information and placebo cells: MX-15, MX-H, MX-W (with
  its sign test), MX-C and MX-A. PL-1, CZ-1 and HU-1 were not pulled and not tested.
- **IS mid t:** MX-1 -0.80, SG-1 -0.97, CN-1 +4.61, BOOK +1.60.
- **Shared per-date sign-flip null** (1,000 draws, book recomputed): max |t| median 1.33, 95 % 2.45; the observed 4.61
  has p < 0.001. Max of 4 |N(0,1)|: 95 % 2.49.
- Only CN-1's mid effect is beyond chance, and it was already known from round 19.

## Data checks
**IC tick files.** Complete for all 9 years and all 3 symbols: 366 / 365 files a year, 3,288 tick days each,
2016-01-01..2024-12-31, none on or after 2025-01-01. The table gives the days with >= 1,000 ticks / median ticks per
weekday file.

| year | USDMXN | USDSGD | USDCNH |
|---|---|---|---|
| 2016 | 305 / 89,570 | 303 / 52,115 | 261 / 15,502 |
| 2017 | 298 / 64,996 | 293 / 45,083 | 269 / 25,674 |
| 2018 | 288 / 56,023 | 272 / 36,524 | 281 / 38,363 |
| 2019 | 293 / 58,754 | 294 / 35,762 | 300 / 52,558 |
| 2020 | 308 / 58,398 | 298 / 41,116 | 308 / 89,890 |
| 2021 | 301 / 67,164 | 277 / 33,262 | 292 / 89,126 |
| 2022 | 307 / 66,531 | 301 / 53,432 | 287 / 106,105 |
| 2023 | 299 / 69,967 | 305 / 55,564 | 301 / 109,225 |
| 2024 | 305 / 77,408 | 309 / 59,130 | 307 / 98,416 |

**Integer scale.** IC zticks and Dukascopy closes are both x1e5 for all three symbols. The ratio of the last
Dukascopy 2015 bar to IC's first 2016 tick is USDMXN 1.0018, USDSGD 0.9998, USDCNH 1.0016 (a 2-3-day gap, no factor
10). In the IC data, the share of bid integers ending in 0 is 0.26-0.70 for USDMXN (0.65-0.70 in 2016-19: often
4-decimal quotes), about 0.10 for USDSGD and 0.10-0.29 for USDCNH. Every grid quote used was spot-checked against
`research.ticks.load_ticks` on 2019-06-12.

**IC spread at the declared minutes** (median bp, last quote before the minute; means and p90 in `out/datacheck_*.txt`):

| year | MXN 09:00 MX | MXN 12:00 MX | SGD 09:00 SGT | SGD 11:00 SGT | CNH 14:30 BJ | CNH 16:30 BJ |
|---|---|---|---|---|---|---|
| 2016 | 1.63 (30 pips) | 1.33 | 0.95 (1.3) | 0.90 | 1.17 (7.8) | 1.15 |
| 2017 | 1.10 | 0.79 | 0.37 | 0.30 | 0.26 (1.7) | 0.30 |
| 2018 | 0.89 | 0.74 | 0.29 | 0.23 | 0.22 | 0.19 |
| 2019 | 0.64 | 0.57 | 0.15 | 0.15 | 0.22 | 0.25 |
| 2020 | 1.64 | 1.32 | 0.29 | 0.22 | 0.40 | 0.43 |
| 2021 | 1.26 | 1.17 | 0.60 | 0.59 | 0.39 | 0.45 |
| 2022 | 1.11 | 1.02 | 0.65 | 0.59 | 0.50 | 0.55 |
| 2023 | 1.09 | 1.06 | 0.52 | 0.51 | 0.52 | 0.60 |
| 2024 | 0.65 | 0.76 | 0.52 | 0.38 | 0.22 | 0.26 |

**Dukascopy (PRE).**
- **Asks:**
  - USDMXN has bid = ask on 83-88 % of the declared minutes in 2007-09; asks are valid from 2010 (own spread
    1.4-3.4 bp).
  - USDSGD has bid = ask on 78-100 % in 2004-09 and 53-55 % in 2010, then valid (1.3-3.5 bp).
  - USDCNH asks are valid from 2012 (3.3-4.3 bp in 2012-13, 0.55-0.61 in 2014-15).
  - This is why the declared PRE cost uses IC's 2016-17 profile.
- **Coverage of the declared minutes:** 0.92-1.00 a year after each symbol's start (2007-03-13, 2004-11-16,
  2012-06-27).
- **Missing days:** Dukascopy USDMXN lacks 8-20 whole days a year in 2011-15 (absent files, e.g. 2015-09-02..09-10).
  Those days have no trade.

**Grid integrity.** The 27 IC symbol-year grids were rebuilt from the final files after all pulls ended; all are
identical to the ones used.

## What this says
- **The Banxico FIX does not behave like a dealing fix in 2016-24.**
  - The USD does not rise over the averaging window: IS -0.82, VAL -2.55.
  - It falls after the WMR minute, which is the WMR reversal of Krohn, Mueller & Whelan rather than a FIX effect.
  - There is no rebound after 12:00. Days without a FIX show no smaller move: in IS + VAL the holiday mean is +6.0
    against -1.4 on FIX days.
- **The PRE rise (+2.28, t 2.87) has not survived.**
  - It sat almost entirely in 09:00-10:00 MX, the hour before WMR. That hour starts at the 10:00 New York
    data-release minute.
  - It is either a pre-2016 pattern or a chance result in one era. Either way it decayed to a negative number, the
    round-12 pattern at its worst.
- **USDSGD has no drift into the ABS VWAP**, so the "dealing fix" class does not extend to SGD.
- **CNH confirms round 19, and the user's pull settles the cost question.**
  - IC's real spread at 14:30 / 16:30 Beijing is 0.2-0.6 bp (1.2 bp in 2016), which makes the round trip about
    1.1 bp against the 0.7 bp DEMO needs.
  - It would need a venue with a CNH spread of about 0.1 bp at those minutes and IC's commission or less; STREAM_A's
    route 4 is the only way left.
- **No direction from this stream needs a new user decision.** EURNOK / USDNOK / EURSEK are stream N.

## Process and disclosures
- **Order:**
  - HYPOTHESES_E.md was written at 09:37:47-09:38:46 UTC, before any price was loaded.
  - MX-1 PRE was computed at 09:44:44 and written at 09:44:50, before MX-1 IS (09:50:18).
  - The other MX PRE cells and CN-1 PRE were written at 09:45:51, before their IS / VAL.
  - SG-1 PRE was computed at 10:32:39 and written at 10:32:48, before SG-1 IS / VAL (10:32:59).
  - CN-1 IS first ran at 09:50:18 and IS / VAL at 10:07:32, after its PRE (09:45:51) and the CNHC-I code check
    (09:46:27).
- **Deviations and fixes, none of which changes a rule:**
  - MX-15's random control first failed an assertion because the grid ended at 15:05 MX. The grid was extended to
    15:20 MX, and MX-1 PRE reproduced unchanged.
  - The 09:50 IS-only run used Python's salted `hash` for the random-control seed. The seed was then fixed to
    `zlib.crc32` for the final runs. MX-1's IS random shares moved from 20.6 / 15.2 % to 20.0 / 14.8 %.
  - The background builder's "file untouched for 90 s" test was meaningless (the pull keeps the VPS file times).
    It was replaced by the full rebuild comparison above.
- **HOLD:**
  - IC files were selected by name < 20250101, and every timestamp was asserted < 1735689600000.
  - Dukascopy files end in 2015.
  - C3's CSV was read for IS and VAL rows only (3,852 rows, 672 days).
  - The USDCNH m1 folder was read only for files before 20250101.
- **Web:** only non-price official pages, all logged with `date -u` times in `r30/E/web/query_log.tsv`:
  - 2 WebSearch calls (09:27-09:28 UTC);
  - 61 curl calls (09:27:04-09:33:28 UTC): 8 connectivity probes; 9 CNBV PDF-name probes, all 404; 23 DOF searches
    (3 trial, 18 yearly, 2 in-year); 21 decree-note fetches (a first 2015 test, the 19 notes, a 2017 re-fetch of
    a truncated copy).
  - No personal data was sent. The DOF page frame carries an indicator box; no exchange rate from it was read or
    used.
- **Repo:** nothing was written except HYPOTHESES_E.md and this file. No git command was run.

## Files
Scratch folder `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r30/E/`.

**Scripts** (`scripts/`):
- calendars and loaders: `cal_e.py` (CNBV / SG / CN / UK / US calendars, gotobi, WMR and clock-gap day sets ->
  `out/cal_e.json`), `e_lib.py` (loaders, HOLD guard), `build_grids.py`, `waiter.py`, `verify_grids.py`;
- cells: `cells.py` (trade engine, PRE profile, random control), `run_pre.py`, `run_isval.py`, `book.py` (BOOK,
  chance), `c3corr.py`, `mxh_pooled.py`, `cnhc_check.py`;
- reporting and parsing: `datacheck.py`, `summary.py`, `tables.py`, `dof_list.py`, `dof_days.py`.

**Outputs** (`out/`): `pre_*.txt`, `isval_*.txt`, `book.txt`, `c3corr.txt`, `datacheck_*.txt`, `cnhc_check.txt`,
`mxh_pooled.txt`, `summary_table.md`, `tables.md`, per-day series `pre_*.npz` / `isval_*.npz`, and JSON results.

**Web** (`web/`): `query_log.tsv` and `dof/` (the saved DOF searches and decree notes, untrusted, parsed with
`python3 -I`).
