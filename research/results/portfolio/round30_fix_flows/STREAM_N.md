# Round 30, stream N: H-NOK (Norges Bank's pre-announced daily NOK flow) tested as declared

Started 2026-10-18 09:22 UTC (`date -u`). The cells are those declared in round 25
([HYPOTHESES_A.md](../round25_surprises/HYPOTHESES_A.md), H-NOK, 2026-10-17 19:13 UTC, with the 19:50 UTC cost
amendment). The details the declaration leaves open were fixed in [HYPOTHESES_N.md](HYPOTHESES_N.md) at
09:33 UTC, before any return was computed. This file is written in the declared order: each PRE number is entered
here before the IS / VAL number of the same cell is computed. The order log at the end records the times.

(Sections are filled in as the data arrives; see the summary at the end.)

## Data checks
### IC ticks (research/data/<SYM>/t1, decoded with research.ticks.load_ticks; every ts < 2025-01-01 asserted)
EURNOK, from `snap_ic.py`:
- Every year has every calendar-day file (366 / 365).
- Every weekday has ticks except 1 Jan (and 25 Dec in some years).
- Ticks are bid / ask x1e5 integers: no bid in any year has a fractional part at x1e5.

| year | files | weekdays with ticks | median ticks per weekday | bid range |
|---|---|---|---|---|
| 2016 | 366/366 | 260/261 | 66,685 | 8.90-9.75 |
| 2017 | 365/365 | 260/260 | 50,246 | 8.79-9.99 |
| 2018 | 365/365 | 261/261 | 41,113 | 9.39-10.06 |
| 2019 | 365/365 | 261/261 | 46,783 | 9.55-10.31 |
| 2020 | 366/366 | 261/262 | 71,960 | 9.82-13.12 |
| 2021 | 365/365 | 260/261 | 46,862 | 9.63-10.70 |
| 2022 | 365/365 | 260/260 | 82,842 | 9.43-10.68 |
| 2023 | 365/365 | 260/260 | 72,839 | 10.46-12.07 |
| 2024 | 366/366 | 262/262 | 86,750 | 11.19-12.13 |

IC EURNOK spread at the declared minutes, on Norwegian bank business days (median / mean bp of mid; median in
pips of 0.0001):

| year | n | 09:00 Oslo | 16:00 Oslo | 09:01 | 16:01 | 10:00 | 10:15 |
|---|---|---|---|---|---|---|---|
| 2016 | 253 | 2.75 / 2.97 (25.6) | 2.54 / 2.98 (23.5) | 2.60 / 2.77 | 2.20 / 2.45 | 2.52 / 3.80 | 2.09 / 2.29 |
| 2017 | 251 | 1.26 / 1.35 (11.8) | 1.18 / 1.46 (11.0) | 1.18 / 1.24 | 1.00 / 1.11 | 1.17 / 1.71 | 1.01 / 1.07 |
| 2018 | 249 | 1.34 / 1.53 (12.9) | 1.25 / 1.37 (12.0) | 1.31 / 1.30 | 1.12 / 1.17 | 1.23 / 2.27 | 1.08 / 1.08 |
| 2019 | 249 | 1.04 / 1.13 (10.4) | 1.04 / 1.31 (10.3) | 0.97 / 0.98 | 0.96 / 0.99 | 1.04 / 1.56 | 0.94 / 0.93 |
| 2020 | 252 | 2.61 / 3.30 (28.1) | 2.70 / 3.19 (28.5) | 2.42 / 3.38 | 2.45 / 2.84 | 2.84 / 4.44 | 2.40 / 2.98 |
| 2021 | 252 | 2.70 / 2.72 (27.6) | 2.49 / 2.75 (25.4) | 2.68 / 2.68 | 2.41 / 2.48 | 2.89 / 4.16 | 2.55 / 2.54 |
| 2022 | 253 | 2.99 / 3.11 (30.3) | 2.95 / 3.68 (30.3) | 3.22 / 3.36 | 3.04 / 3.84 | 3.09 / 4.92 | 2.47 / 2.64 |
| 2023 | 251 | 3.18 / 3.35 (37.1) | 3.09 / 5.31 (35.2) | 3.50 / 3.67 | 3.32 / 4.34 | 3.42 / 5.06 | 3.04 / 3.16 |
| 2024 | 250 | 1.83 / 1.92 (21.0) | 2.16 / 4.75 (24.6) | 1.76 / 1.97 | 2.14 / 3.28 | 2.15 / 4.44 | 1.69 / 1.81 |

At 09:00 and 16:00, at most one stale quote (older than 30 min) per year. The round trip at IC is therefore ~1.6-4
bp, not the 2.9-5.6 bp working range of STREAM_A, which came from IC's published averages.

USDNOK (IC, 2016-24):
- Every year has every calendar-day file.
- Weekdays with ticks: 260/261, 260/260, 261/261, 261/261, 261/262, 260/261, 260/260, 260/260, 262/262.
- Median ticks per weekday: 53-118k.
- No bid has a fractional part at x1e5. Bid range 7.63-12.13.

Spread at 09:00 / 16:00 Oslo (median / mean bp; median pips):

| year | 09:00 | 16:00 | 09:01 | 16:01 |
|---|---|---|---|---|
| 2016 | 2.42 / 2.96 (20.5) | 2.62 / 3.29 (22.0) | 2.18 / 2.53 | 1.97 / 2.32 |
| 2017 | 1.72 / 1.80 (14.3) | 1.52 / 2.28 (12.8) | 1.67 / 1.62 | 1.39 / 1.42 |
| 2018 | 1.50 / 1.62 (12.3) | 1.45 / 1.80 (11.7) | 1.46 / 1.47 | 1.41 / 1.40 |
| 2019 | 1.25 / 1.36 (11.0) | 1.30 / 1.49 (11.5) | 1.15 / 1.18 | 1.21 / 1.23 |
| 2020 | 2.67 / 3.34 (24.3) | 2.76 / 3.19 (25.6) | 2.35 / 3.19 | 2.38 / 2.83 |
| 2021 | 2.85 / 2.86 (24.2) | 2.75 / 2.89 (23.6) | 2.94 / 2.94 | 2.68 / 2.76 |
| 2022 | 2.92 / 2.95 (28.1) | 3.00 / 4.09 (28.9) | 2.97 / 3.11 | 3.03 / 3.63 |
| 2023 | 2.08 / 2.08 (21.9) | 2.10 / 3.77 (22.0) | 2.15 / 2.24 | 2.12 / 2.91 |
| 2024 | 1.11 / 1.34 (12.0) | 1.52 / 4.21 (16.6) | 1.12 / 1.31 | 1.50 / 2.48 |

USDNOK PRE cost profile (IC 2016-17 mean, Mon-Fri): 09:00 2.34-2.47 bp, 16:00 2.52-3.41 bp.

Glitch check (amendment 1), deviations > 1 % from the median of T-5..T+5 min at any Oslo minute 06:00-19:01 of
2016-24:
- EURNOK 0 of 1.77 M minute boundaries, USDNOK 1 (2020-03-30 08:14 Oslo), EURSEK 0.
- None at 09:00 / 16:00 / 09:01 / 16:01.

EURSEK (IC, 2016-24):
- Every year has every calendar-day file.
- Weekdays with ticks: 260/261, 260/260, 261/261, 261/261, 261/262, 260/261, 260/260, 260/260, 262/262.
- Median ticks per weekday: 31-73k.
- No bid has a fractional part at x1e5. Bid range 9.11-12.0.

Spread at 09:00 / 16:00 Oslo (median / mean bp; median pips):

| year | 09:00 | 16:00 | 09:01 | 16:01 |
|---|---|---|---|---|
| 2016 | 2.34 / 2.57 (22.1) | 2.10 / 2.49 (20.0) | 2.24 / 2.32 | 1.96 / 2.04 |
| 2017 | 1.33 / 1.41 (12.8) | 1.29 / 1.50 (12.4) | 1.22 / 1.25 | 0.92 / 1.19 |
| 2018 | 1.37 / 1.69 (14.2) | 1.24 / 1.32 (12.8) | 1.32 / 1.32 | 1.15 / 1.16 |
| 2019 | 0.95 / 1.01 (10.0) | 0.98 / 1.19 (10.4) | 0.93 / 0.94 | 0.90 / 0.90 |
| 2020 | 1.89 / 2.51 (19.4) | 1.75 / 2.23 (18.3) | 1.61 / 2.15 | 1.64 / 2.00 |
| 2021 | 1.88 / 2.01 (19.2) | 1.69 / 1.93 (17.2) | 1.78 / 1.84 | 1.64 / 1.70 |
| 2022 | 2.51 / 2.67 (27.4) | 2.17 / 2.93 (23.1) | 2.27 / 2.48 | 2.33 / 3.03 |
| 2023 | 2.82 / 3.00 (32.1) | 2.49 / 4.01 (28.4) | 2.71 / 2.92 | 2.51 / 3.23 |
| 2024 | 1.93 / 2.21 (22.1) | 1.87 / 3.44 (21.1) | 1.87 / 1.95 | 1.87 / 3.01 |

EURSEK PRE cost profile (IC 2016-17 mean, Mon-Fri): 09:00 1.85-2.17 bp, 16:00 1.88-2.33 bp.

PRE cost profile (IC EURNOK 2016-17, 521 weekdays, mean spread by Oslo minute of week):
- 09:00 Mon-Fri: 2.19 2.11 2.22 2.18 2.26 bp.
- 16:00 Mon-Fri: 2.14 2.23 2.20 2.10 2.62 bp.
- Medians are 1.6-2.3 bp.
- Mean at the random-control extremes (06:00 / 07:00 / 08:00 / 12:00 / 18:00 / 19:00 Oslo): 3.43 / 3.30 / 3.39 / 1.63
  / 1.96 / 2.37 bp.

### Dukascopy M1, PRE (research/data/duka/m1_r30/<SYM>_<YYYY>.npz; `snap_duka.py`, `scale_check.py`)
EURNOK (2004-10-25 onwards):
- **Integer scale.** bci / 1e5 at 12:00 Oslo, 14-31 Dec 2015, median 9.528; IC bid, 4-15 Jan 2016, 9.638 (ratio
  1.012). So the scale is 1e5.
- **Coverage is thin before 2007.** Valid quotes on Norwegian bank business days, 09:00 / 16:00 Oslo (fresh = at most
  30 min old; zero-volume minutes are no trading):

  | year | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | weekdays with traded bars | 23 | 24 | 173/260 | 215/261 | 247/262 | 252/261 | 259/261 | 223/260 | 260/261 | 250/261 | 259/261 | 260/261 |
  | stale share at 09:00 (business days) | 0.58 (of 48) | 0.91 | 0.36 | 0.16 | 0.06 | 0.04 | 0.00 | 0.15 | 0.00 | 0.04 | 0.01 | 0.00 |

  - 2004-05 price changes occur on only 21 + 23 days; the other days are flat zero-volume filler bars.
  - 2011 lost ~37 weekdays to HTTP 503 at download (597 of the year's 1,151 day-file requests returned 503; the
    downloader records a day as missing after 5 of them). I did not re-download (brief: never start a download).
- **Asks.** The ask equals the bid on most traded bars of 2007-08 (junk). Where the ask is usable, Dukascopy's median
  spread at 09:00 is 1.7-5.4 bp.
- **Glitches** (amendment 1): 808 Oslo-hours boundaries in 2004-07 deviate by > 1 % from the T-5..T+5 median. All are
  in thin hours except 5 at the declared minutes. None deviates by > 2 %.

## 1. NOK-D on PRE (computed 10:58:50 UTC, before any other return)
OLS of the 09:00 -> 16:00 Oslo return (bp, Dukascopy bid to bid, glitch filter on) on A_d (NOK bn per day) with a
constant. Day set: Norwegian bank business days 2004-10-25..2015-12-31, zero-amount months included, 20-31 Dec at A_d
= 0. 3,016 business days, 2,331 with valid quotes (119 months).

| variant | n | slope, bp per NOK bn/day | t (day) | t (month-clustered) | constant bp (t) |
|---|---|---|---|---|---|
| **primary** | 2,331 | **+3.22** | **+1.40** | +1.73 | +0.37 (+0.34) |
| without 20-31 Dec | 2,275 | +3.13 | +1.35 | +1.67 | +0.48 (+0.43) |
| x = NOK-1 dose, sign(A) clip(\|A\|/1000, 0.5, 2) | 2,331 | +2.85 per dose unit | +1.29 | +1.52 | +0.28 (+0.24) |
| check: Dukascopy (bid + ask) / 2 where the ask is usable | 2,290 | +3.59 | +1.55 | +1.88 | |

- The regressor is mean +0.20, sd 0.44 bn per day. PRE spans +1.54 (Sep 2008) down to -0.70 (2015).
- **Reading:** the slope has the predicted sign, at the impact-model size (~2.3 bp per NOK bn/day, HYPOTHESES_A), but
  is not significant (day t 1.40). It is a mechanism check only, not a tier test.
- By year (mean 09-16 return bp, t; mean A bn/day):

  | year | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | return (t) | +0.13 (0.03) | -0.67 (-0.13) | +2.42 (1.15) | +3.67 (1.62) | +4.63 (1.44) | +2.43 (0.71) | -0.37 (-0.18) | -0.10 (-0.04) | -3.13 (-1.88) | +3.87 (1.38) | +0.17 (0.06) | -2.07 (-0.53) |
  | A | +0.58 | +0.09 | +0.39 | +0.63 | +0.71 | +0.10 | +0.17 | +0.34 | +0.32 | +0.19 | -0.06 | -0.66 |

## 2. NOK-1 on PRE (computed 10:59:18 UTC, before NOK-1 on IS / VAL)
EURNOK, side sign(A_d), 09:00 -> 16:00 Oslo, size clip(|A_d|/1000, 0.5, 2).
- Day set: Norwegian bank business days with |A_d| >= 100, excluding 20-31 Dec. Prices are Dukascopy bid to bid; cost
  is IC's 2016-17 mean spread profile + 0.6 bp.
- 2,025 declared days, 1,603 valid, i.e. 143 a year over 11.2 years (2004-05 almost empty, see the data checks).
  Long on 81 % of days (2004-13); mean size 0.61.

| | mid bp (t) | cost | net bp (t) | spread x1.5 | +1 min net (mid) |
|---|---|---|---|---|---|
| **weighted (declared)** | **+1.29 (+1.85)** | 1.73 | **-0.43 (-0.62)** | -1.11 (-1.60) | -0.45 (+1.09) |
| unweighted (info) | +1.38 (+1.28) | | -1.44 (-1.33) | | |
| check: Dukascopy (bid+ask)/2 | +1.39 (+1.98), n 1,578 | | | | |

- Per-trade net sd 27.9 bp, Sharpe -0.016, power -0.24.
- Years net > 0: 5 / 12.
- Random entries (1,000 seeds, per-day shift -180..+180 min): beaten 61.6 % on net and 71.4 % at mid.
- By year (weighted mid / net bp, t of net, n, side):

  | year | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | mid / net | +0.5 / -1.2 | +3.1 / +0.3 | +1.3 / -0.1 | +4.5 / +2.5 | +3.0 / +0.8 | +2.6 / +1.2 | +1.0 / -0.7 | +0.1 / -1.6 | -1.4 / -2.8 | +1.7 / +0.3 | -6.4 / -7.9 | +1.5 / -0.4 |
  | t net | -0.43 | n/a | -0.11 | +1.18 | +0.32 | +0.39 | -0.30 | -0.74 | -3.05 | +0.19 | -2.02 | -0.15 |
  | n | 19 | 2 | 159 | 181 | 218 | 85 | 87 | 139 | 212 | 199 | 58 | 244 |
  | side | + | + | + | + | + | + | + | + | + | + | - | - |

## 3. NOK-1 on IS / VAL (computed 10:59:38 UTC; IC ticks, ask in / bid out at the last tick at or before each minute, + 0.6 bp)
| era | days declared / valid | per yr | side | mean size | mid bp (t) | cost | net bp (t) | x1.5 | +1 min net (mid) | sd | Sharpe | power | years net > 0 | random: net / mid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRE | 2,025 / 1,603 | 143 | long 81 % | 0.61 | +1.29 (+1.85) | 1.73 | -0.43 (-0.62) | -1.11 | -0.45 (+1.09) | 27.9 | -0.016 | -0.24 | 5/12 | 61.6 % / 71.4 % |
| **IS** | 1,449 / 1,448 | 241 | short | 1.00 | **+5.36 (+3.78)** | 3.03 | **+2.33 (+1.65)** | +1.11 (+0.79) | +1.34 (+4.19) | 53.6 | +0.043 | +0.89 | 3/6 | 100 % / 100 % |
| **VAL** | 693 / 692 | 231 | long 97 % | 1.15 | **+0.07 (+0.03)** | 5.06 | **-4.99 (-2.24)** | -7.18 (-3.21) | -1.44 (+3.49) | 58.6 | -0.085 | -1.70 | 0/3 | 8.9 % / 13.1 % |

- **VAL / IS:** mid 0.01, net -2.15.
- **Decay readings at the VAL size:** power -1.71 at 0.65 x VAL mid and -1.72 at 0.30 x.
- **Unweighted (info):** IS mid +3.43 (t +3.30), net +0.68 (t +0.65); VAL mid -0.10 (t -0.06), net -4.42 (t -2.78).
- **By year** (weighted mid bp (t) / net bp (t)):

  | year | n | side | mid (t) | net (t) |
  |---|---|---|---|---|
  | 2016 | 245 | short | +3.08 (1.45) | +0.01 (0.00) |
  | 2017 | 244 | short | +1.15 (0.75) | -0.52 (-0.34) |
  | 2018 | 245 | short | +1.34 (1.10) | -0.03 (-0.03) |
  | 2019 | 245 | short | +0.63 (0.60) | -0.47 (-0.45) |
  | 2020 | 246 | short | +16.28 (2.37) | +10.34 (1.51) |
  | 2021 | 223 | short | +10.02 (2.57) | +4.81 (1.24) |
  | 2022 | 202 | long 79 % | -1.91 (-0.33) | -8.80 (-1.54) |
  | 2023 | 244 | long | +1.85 (0.46) | -4.79 (-1.19) |
  | 2024 | 246 | long | -0.08 (-0.07) | -2.07 (-1.84) |

- **Random entries:**
  - IS: the declared window beats all 1,000 seeds (random mean net -0.48, p95 +0.76; random mid mean +2.66, p95
    +3.91).
  - VAL: it beats only 8.9 % on net and 13.1 % at mid.
- **Chance benchmark:** NOK-1's IS net |t| 1.65 is below the 95 % max-|t| of 2 cells (2.24) and of 5 cells (2.57).
- **Verdict NOK-1:**
  - **Fails LIVE and DEMO.** IS net t 1.65 is below 2.0 and 2.5; VAL net -4.99 (t -2.24) < 0; 3 / 9 years net > 0;
    VAL random 8.9 %.
  - The IS mid is real (t 3.78), but 80 % of the IS mid P&L is 2020-21. Those were the two years of the largest NOK
    purchases (-1.6 to -2.5 bn a day, size 1.6-2.0), and also of the NOK's recovery from its March 2020 low.
  - In VAL, Norges Bank sold NOK at up to 4.3 bn a day and EURNOK did not rise in Oslo hours (mid +0.07).
- **Cost note.** The 16:00 Oslo exit is 10:00 New York, a US release minute on many days. IC's mean 16:00 spread is
  inflated by release spikes in 2023-24 (5.3 / 4.8 bp mean against 3.1 / 2.2 median). With the larger VAL size this
  makes VAL's cost 5.06 bp.
- **The 09:00 Oslo quote jump** (information, post hoc; `split_minute.py`, `minute_0900.py`, `minute_scan.py`).
  - The +1 minute variant differs from the base mostly through the entry minute. VAL weighted mid is +0.07 at
    09:00 -> 16:00, +2.96 at 09:01 -> 16:00, +0.60 at 09:00 -> 16:01 and +3.49 at 09:01 -> 16:01.
  - Cause: IC's EURNOK quote rises in the minute into 09:00 Oslo and falls back in the next. In VAL, bid +2.33 and
    ask +2.33 bp (t 21) from 08:59 to 09:00, then mid -2.30 (t -18) from 09:00 to 09:01. In IS +0.87 / -0.78 (t 12 /
    -8).
  - It follows the Oslo clock in both DST seasons. It happens at no other full hour 06:00-18:00 (|move| <= 0.5 bp),
    and EURSEK shows at most +0.3 bp at 09:00.
  - So the declared 09:00 entry pays ~2.3 bp more for VAL's long side and gains ~0.8 bp for IS's short side.
  - It does not rescue the cell. With both fills +1 min, net is +1.34 (t 0.97) in IS and -1.44 (t -0.64) in VAL. The
    reversal itself, selling at 09:00 and buying back at 09:01, is +2.3 bp gross against a ~3.4 bp round trip.

## 4. NOK-D on IS, VAL and pooled (computed 11:02:06 UTC)
Same regression as section 1; IS / VAL on IC mids.

| era | n days (months) | slope bp per NOK bn/day | t day | t month | constant bp (t) | A mean / sd | without 20-31 Dec: slope (t) | NOK-1 dose regressor: slope (t) |
|---|---|---|---|---|---|---|---|---|
| PRE 2004-15 | 2,331 (119) | +3.22 | +1.40 | +1.73 | +0.37 (+0.34) | +0.20 / 0.44 | +3.13 (+1.35) | +2.85 (+1.29) |
| IS 2016-21 | 1,505 (72) | +6.00 | +2.80 | +2.76 | +2.21 (+1.15) | -0.96 / 0.56 | +7.33 (+3.31) | +6.46 (+2.73) |
| VAL 2022-24 | 753 (36) | +0.34 | +0.22 | +0.27 | -1.13 (-0.53) | +1.15 / 1.04 | +0.13 (+0.08) | +1.78 (+0.76) |
| IS + VAL | 2,258 (108) | +1.73 | +2.15 | +2.12 | -2.18 (-2.51) | -0.26 / 1.25 | +1.77 (+2.20) | +2.22 (+2.46) |
| **2004-24 (declared span)** | 4,589 (227) | **+2.24** | **+3.09** | **+2.90** | -0.72 (-1.18) | -0.03 / 0.96 | +2.25 (+3.10) | +2.73 (+3.53) |

Mean 09:00 -> 16:00 return by year, IS / VAL (bp, t; mean A):

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| return (t) | -3.92 (-1.64) | -0.94 (-0.50) | -1.28 (-0.74) | -1.37 (-0.81) | -8.17 (-2.01) | -5.67 (-2.41) | -2.23 (-0.78) | +0.10 (+0.03) | -0.05 (-0.02) |
| A | -0.84 | -0.80 | -0.64 | -0.58 | -1.52 | -1.39 | +1.75 | +1.33 | +0.37 |

**Reading.**
- Over the declared 2004-24 span the dose slope is positive and significant: +2.24 bp per NOK bn/day, t 3.09 (month
  t 2.90). That is the square-root impact model's ~2.3 bp, and the mechanism the declaration predicted.
- But it is not stable:
  - PRE +3.22 (t 1.40), IS +6.00 (t 2.80), VAL +0.34 (t 0.22).
  - In 2022-24 Norges Bank sold NOK 0.15-4.3 bn a day and EURNOK did not rise in Oslo hours.
  - The IS slope comes from the NOK-purchase years only. Within IS the largest purchases (2020-21) coincide with the
    NOK's recovery after March 2020, so the IS slope may partly be that trend.
- The VAL / IS ratio of the slope is 0.06: the decaying pattern of every flow anomaly since round 12.

## 5. NOK-A, the 10:00 announcement (information only; computed 11:02:19 UTC)
- Day: the last Norwegian bank business day of each month where A_{m+1} != A_m. Side: sign(A_{m+1} - A_m).

| era | days with a change / valid | 10:00 -> 10:15 mid bp (t) | 10:01 -> 10:15 mid (t) | 10:01 -> 10:15 net (t) | increases: n, mid | decreases: n, mid |
|---|---|---|---|---|---|---|
| PRE | 79 / 60 | +4.43 (+1.86) | +1.48 (+0.91) | -0.98 (-0.60) | 36, +1.24 | 24, +9.22 |
| IS | 27 / 27 | +3.98 (+1.76) | -1.63 (-0.96) | -4.95 (-2.78) | 13, +0.44 | 14, +7.27 |
| VAL | 22 / 22 | +11.37 (+1.68) | +1.94 (+0.37) | -5.07 (-0.90) | 10, +23.17 | 12, +1.55 |

- The announcement moves EURNOK the predicted way in all three eras at mid (+4.0 to +11.4 bp over 15 minutes; the
  three eras together are +5.7 bp over 109 events, event-weighted).
- Most of the move is in the first minute: from 10:01 the mid is +1.5 / -1.6 / +1.9 and net is negative everywhere.
  As round 8 / 10 found for public information, it is priced within a minute. With 12 events a year at most, it
  cannot be a tier cell.
- Caveat: the announcement day is the declared "last business day". Norges Bank's sitemap dates its releases on the
  same days in 2020-24, with one exception (August 2021: slug 2021-08-30, rule 2021-08-31).

## 6. Norwegian-bank-holiday placebo (EURNOK; computed 11:02:19 UTC)
NOK-1's window, side and size on Maundy Thursday, Whit Monday and 17 May (weekday), in months with |A| >= 100.

| set | PRE | IS | VAL | pooled mid (t, n) | business days (same eras) | business minus holiday (Welch t) |
|---|---|---|---|---|---|---|
| declared | +2.31 (+0.43, 19) | -8.51 (-0.90, 17) | +8.99 (+0.40, 9) | -0.44 (-0.07, 45) | +2.64 (n 3,743) | +3.08 (+0.50) |
| extension: Ascension Day, 1 May (info) | -2.61 (-0.80, 10) | -0.99 (-0.07, 10) | +22.73 (+1.28, 5) | +3.11 (+0.46, 25) | +2.64 | -0.47 (-0.07) |

- On holidays, when Norges Bank does not trade, the signed return is ~0 as predicted (-0.44 bp, n 45). But with
  ~2-3 holidays a year and a per-day sd of ~40 bp, the placebo cannot tell a 3 bp effect from none (difference t
  0.50).
- 2005's two placebo days were dropped for stale Dukascopy quotes. 2004's had A = 0, as did the zero months of
  2009-10 and 2014.

## 7. Glitch filter off (information)
The filter changes almost nothing:
- NOK-D PRE: n 2,333 instead of 2,331, slope +3.215 (t 1.40).
- NOK-1 PRE: n 1,605, net -0.43; +1 min -0.53.
- NOK-1 IS / VAL are identical (no IC quote is filtered).

## 8. NOK-2 (USDNOK replica) on PRE (computed 11:39:44 UTC, written 11:39:57 UTC, before NOK-2 on IS / VAL)
(Sections 8-9 were first appended at these times. An editing slip at 11:41 deleted them; they were restored verbatim
at 11:41 UTC.)

Dukascopy USDNOK, 2004-15. Data checks:
- Dense from 2004: 235-260 traded weekdays a year, a stale share at 09:00 of at most 0.11.
- Scale x1e5: late Dec 2015 8.705 against IC early Jan 2016 8.899 (ratio 1.022, the NOK's January 2016 slide).
- Glitch filter: 1 boundary > 1 % in 2004-15, none at the declared minutes.
- Dukascopy's own USDNOK spread is 12.6-16.1 bp in 2004-08 and 2.0-6.6 bp in 2009-15. The declared PRE cost uses
  IC's 2016-17 USDNOK profile instead.

Same days, side and size as NOK-1 (side long USDNOK when A > 0):
- 2,025 declared, 1,979 valid (172 a year); long 85 %, mean size 0.62.
- Weighted: mid +1.41 (t +1.52); cost 1.98; net -0.57 (t -0.62); x1.5 -1.38 (t -1.49); +1 min net -0.10 (mid
  +1.51). Unweighted mid +1.18 (t +0.88), net -2.03.
- Dukascopy (bid+ask)/2 check: mid +1.39 (t +1.48).
- Per-trade net sd 41.2, Sharpe -0.014, power -0.24; years net > 0: 7 / 12.
- Random entries: beaten 14.3 % on net and 31.2 % at mid.
- By year, weighted net bp (t):
  - 2004 -4.6 (-1.99), 2005 +2.0 (0.99), 2006 +0.6 (0.34), 2007 +1.9 (0.83), 2008 +3.1 (0.77), 2009 +2.4 (0.52);
  - 2010 +0.0 (0.01), 2011 -2.0 (-0.37), 2012 -2.3 (-1.42), 2013 +0.3 (0.14), 2014 -10.3 (-2.42), 2015 -4.8
    (-1.47).

### NOK-2 on IS / VAL (computed 11:40:03 UTC; IC ticks)
| era | valid / per yr | mean size | mid (t) | cost | net (t) | x1.5 | +1 min net (mid) | sd | Sharpe | power | years net > 0 | random net / mid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRE | 1,979 / 172 | 0.62 | +1.41 (+1.52) | 1.98 | -0.57 (-0.62) | -1.38 | -0.10 (+1.51) | 41.2 | -0.014 | -0.24 | 7/12 | 14.3 % / 31.2 % |
| IS | 1,448 / 241 | 1.00 | +5.10 (+2.84) | 3.23 | +1.87 (+1.04) | +0.55 | +0.86 (+3.78) | 68.0 | +0.027 | +0.56 | 2/6 | 100 % / 100 % |
| VAL | 692 / 231 | 1.15 | +0.98 (+0.30) | 4.37 | -3.39 (-1.03) | -5.24 | +1.04 (+4.97) | 86.7 | -0.039 | -0.78 | 0/3 | 4.6 % / 8.3 % |

- VAL / IS: mid 0.19, net -1.82. Decay at the VAL size: x0.65 -0.86, x0.30 -0.94.
- By year, weighted net (t): 2016 -2.3 (-0.74), 2017 -1.0 (-0.58), 2018 -1.8 (-1.01), 2019 -1.5 (-1.16), 2020 +13.0
  (+1.52), 2021 +5.1 (+1.01), 2022 -8.3 (-0.94), 2023 -1.5 (-0.27), 2024 -1.3 (-0.82).
- **Verdict NOK-2: fails LIVE and DEMO.** IS net t 1.04; VAL net < 0; 2 / 9 years. It replicates NOK-1's pattern: an
  IS mid made in 2020-21 (+19.0 / +10.5 weighted mid) and ~0 in VAL.

## 9. NOK-P (EURSEK placebo) on PRE (computed 11:40:20 UTC, written 11:40:32 UTC, before NOK-P on IS / VAL)
Dukascopy EURSEK, 2004-10-27 onwards. Data checks:
- 2004 thin (48 traded weekdays); 231-261 traded weekdays a year from 2005.
- Scale x1e5: late Dec 2015 9.261 against IC early Jan 2016 9.258 (ratio 1.000).
- The ask equals the bid on most bars of 2004-10.
- Glitch filter: 1 boundary > 1 %, none at the declared minutes.

NOK-1's days, side sign(A_d) and size, on the Stockholm clock (= Oslo):
- 2,025 declared, 1,898 valid (170 a year); long 84 %, mean size 0.62.
- Weighted: **mid -0.03 (t -0.05)**; cost 1.63; net -1.66 (t -3.31); x1.5 -2.29; +1 min net -0.83 (mid +0.62).
  Unweighted mid +0.01 (t +0.01).
- Dukascopy (bid+ask)/2 check: +0.11 (t +0.23).
- Per-trade net sd 21.8, Sharpe -0.076, power -1.30; years net > 0: 2 / 12.
- Random entries: beaten 11.0 % on net and 16.0 % at mid.
- Placebo reading on PRE: ~0 at mid, as predicted (NOK-1 PRE mid was +1.29, t 1.85).

### NOK-P on IS / VAL (computed 11:40:37 UTC; IC ticks)
| era | valid / per yr | mean size | mid (t) | cost | net (t) | x1.5 | +1 min net (mid) | sd | power | years net > 0 | random net / mid |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PRE | 1,898 / 170 | 0.62 | -0.03 (-0.05) | 1.63 | -1.66 (-3.31) | -2.29 | -0.83 (+0.62) | 21.8 | -1.30 | 2/12 | 11.0 % / 16.0 % |
| IS | 1,448 / 241 | 1.00 | -0.16 (-0.20) | 2.52 | -2.69 (-3.30) | -3.65 | -2.56 (-0.28) | 30.9 | -1.77 | 0/6 | 31.9 % / 26.8 % |
| VAL | 692 / 231 | 1.15 | +0.09 (+0.05) | 4.23 | -4.14 (-2.38) | -5.91 | -3.42 (+0.60) | 45.7 | -1.81 | 0/3 | 45.2 % / 59.1 % |

- **Placebo reading: ~0 at mid in every era, as predicted.** EURSEK on NOK-1's days and sides earns -0.03 / -0.16 /
  +0.09 bp, against NOK-1's +1.29 / +5.36 / +0.07.
- So the IS move of EURNOK on Norges Bank's purchase days (+5.36, t 3.78) is NOK-specific. It is not a general
  EUR-against-Scandinavia or European-hours move.
- EURSEK holiday days (information): pooled -3.96 (t -1.34, n 46) on Norwegian holidays against -0.06 on business
  days.

## Summary (updated 2026-10-18 11:41 UTC; all declared cells done)
| cell | PRE mid (t) / net | IS mid (t) | VAL mid (t) | cost IS / VAL | net IS (t) | net VAL (t) | VAL/IS mid | power IS / VAL size (x0.65, x0.30) | random IS / VAL (net) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| NOK-1 EURNOK (primary) | +1.29 (+1.85) / -0.43 | +5.36 (+3.78) | +0.07 (+0.03) | 3.03 / 5.06 | +2.33 (+1.65) | -4.99 (-2.24) | 0.01 | +0.89 / -1.70 (-1.71, -1.72) | 100 % / 8.9 % | fails LIVE and DEMO |
| NOK-2 USDNOK (replica) | +1.41 (+1.52) / -0.57 | +5.10 (+2.84) | +0.98 (+0.30) | 3.23 / 4.37 | +1.87 (+1.04) | -3.39 (-1.03) | 0.19 | +0.56 / -0.78 (-0.86, -0.94) | 100 % / 4.6 % | fails LIVE and DEMO |
| NOK-P EURSEK (placebo) | -0.03 (-0.05) / -1.66 | -0.16 (-0.20) | +0.09 (+0.05) | 2.52 / 4.23 | -2.69 (-3.30) | -4.14 (-2.38) | - | -1.77 / -1.81 | 31.9 % / 45.2 % | ~0 as predicted |
| NOK-D slope, bp per NOK bn/day | +3.22 (+1.40) | +6.00 (+2.80) | +0.34 (+0.22) | - | - | - | 0.06 | - | - | 2004-24 +2.24 (t 3.09, month t 2.90); decays to ~0 in VAL |
| NOK-A 10:00 -> 10:15 (info) | +4.43 (+1.86) | +3.98 (+1.76) | +11.37 (+1.68) | - | from 10:01: -4.95 | -5.07 | - | - | - | priced within the first minute |
| holiday placebo, EURNOK | +2.31 | -8.51 | +8.99 | - | - | - | - | - | - | pooled -0.44 (t -0.07, n 45); uninformative |

- **H-NOK verdict: no LIVE or DEMO cell; PREREG_DRAFT: none.**
  - The flow left a trace: a NOK-specific IS move, a 2004-24 dose slope at the impact-model size, and an
    announcement reaction.
  - It was absent in VAL, where Norges Bank's NOK sales were the largest on record, and it never cleared IC's cost.
- **Chance benchmark:** 2.24 for 2 trading cells, 2.57 for 5. The best IS net |t| of the trading cells is 1.65
  (NOK-1).

Order log (UTC):
- 09:33 HYPOTHESES_N.md; 09:59 amendment 1.
- 10:58:50 NOK-D PRE (written 10:59:10); 10:59:18 NOK-1 PRE (written 10:59:33); 10:59:38 NOK-1 IS / VAL.
- 11:02 NOK-D IS / VAL / pooled, NOK-A, placebo.
- 11:39:44 NOK-2 PRE (written 11:39:57); 11:40:03 NOK-2 IS / VAL.
- 11:40:20 NOK-P PRE (written 11:40:32); 11:40:37 NOK-P IS / VAL.

Scripts are in the session scratchpad r30/N/: cal_n.py, snap_ic.py, snap_duka.py, nlib.py, cells.py, checks.py,
scale_check.py, glitch_check.py, summarize.py, split_minute.py, minute_0900.py, minute_scan.py, synth_test.py.
Outputs: results.jsonl, out_*.txt, checks_*.txt, web/fetch_log.tsv.
