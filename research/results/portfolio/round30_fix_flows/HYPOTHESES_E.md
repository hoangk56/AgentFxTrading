# Round 30, stream E: details of H-EMFIX and H-CNH fixed before any return

Written 2026-10-18 09:37:47-09:38:46 UTC (`date -u` 09:37:47 at the start, file time 09:38:46), before any USDMXN,
USDSGD or USDCNH price was loaded in this round. The declared cells are those of
[round25_surprises/HYPOTHESES_A.md](../round25_surprises/HYPOTHESES_A.md) (H-CNH 19:27, H-EMFIX 19:47 and the
amendments of 19:50 UTC, 2026-10-17). Nothing here changes a side, a window, a day set, the sizing, the costs, the
controls or the eras. This file fixes only what the declaration leaves open. Blocks are only appended; a later change
is marked "amendment" with its own `date -u` time.

## What I had seen before writing this
- From earlier rounds: round 19's CNHC-I numbers (mid +1.22 bp, t 4.57 IS; +1.68, t 4.08 VAL; net +0.19 / +0.66 at
  an assumed 1.04 / 1.02 bp cost); round 7's hourly USDCNH profile (as disclosed in round 19); round 25 STREAM_A's
  expected sizes, powers and published IC spreads.
- In this session:
  - directory listings and file counts of research/data/{USDMXN,USDSGD,USDCNH}/t1 and research/data/duka/m1_r30/;
  - the tail of requests.log (file paths only);
  - the CNBV decrees on dof.gob.mx (non-price). The DOF page frame has an "indicadores" box: its parsed text
    showed only a 2026 UDIS value, an inflation unit; no exchange rate was read or used.
- No price of USDMXN or USDSGD has been opened. No USDCNH price has been opened in this round.

## 1. Calendars (non-price; fetched 2026-10-18 09:27-09:33 UTC, logged in `r30/E/web/query_log.tsv`)
**Mexican banking days.** Mon-Fri minus the CNBV closing days. The source is each year's "Disposiciones de carácter
general que señalan los días del año N en que las entidades financieras sujetas a la supervisión de la CNBV deberán
cerrar sus puertas y suspender operaciones", DOF note codes:

| year | DOF code | year | DOF code | year | DOF code |
|---|---|---|---|---|---|
| 2007 | 4938942 | 2013 | 5282546 | 2019 | 5546178 |
| 2008 | 5010425 | 2014 | 5326551 | 2020 | 5582495 |
| 2009 | 5075842 | 2015 | 5377596 | 2021 | 5607227 |
| 2010 | 5124899, + amendment 5159251 of 2010-09-13 adding 17 Sep 2010 | 2016 | 5420967 | 2022 | 5639317 |
| 2011 | 5170638 | 2017 | 5466056 | 2023 | 5672531 |
| 2012 | 5225255 | 2018 | 5508103 | 2024 | 5711052 |

- Every year's list:
  - 1 Jan;
  - the first Monday of February and the third Monday of March;
  - Holy Thursday and Good Friday;
  - 1 May and 16 Sep;
  - 2 Nov and the third Monday of November;
  - 12 Dec and 25 Dec.
- Plus 17 Sep 2010, 1 Jul and 1 Dec 2012, 1 Jul and 1 Dec 2018 (weekends), and 1 Oct 2024.
- I transcribed the lists into `r30/E/scripts/cal_e.py`. On weekdays they agree day for day with the `holidays`
  package's XMEX (BMV) calendar.
- Result: 246-247 banking days a year, before the 24 Dec - 1 Jan exclusion is applied to every cell.

**Singapore and China.** Mon-Fri minus `holidays` 0.106 `country_holidays("SG")` and `country_holidays("CN")`. CN
includes the substituted days off. Weekend make-up working days are not trading days. The 24 Dec - 1 Jan exclusion
applies.

**London and New York for MX-H.**
- London open: not an England bank holiday (`country_holidays("GB", subdiv="ENG")`).
- New York open: not a US federal holiday (`country_holidays("US")`), the Federal Reserve / FX-settlement calendar.

**MX-H day set (126 days).** Weekday CNBV closing days, outside 24 Dec - 1 Jan, with London and New York open:
- 2007: 02-05 03-19 04-05 05-01 11-02 11-19 12-12
- 2008: 02-04 03-17 03-20 05-01 09-16 11-17 12-12
- 2009: 02-02 03-16 04-09 05-01 09-16 11-02 11-16
- 2010: 02-01 03-15 04-01 09-16 09-17 11-02 11-15
- 2011: 02-07 03-21 04-21 09-16 11-02 11-21 12-12
- 2012: 02-06 03-19 04-05 05-01 11-02 11-19 12-12
- 2013: 02-04 03-18 03-28 05-01 09-16 11-18 12-12
- 2014: 02-03 03-17 04-17 05-01 09-16 11-17 12-12
- 2015: 02-02 03-16 04-02 05-01 09-16 11-02 11-16
- 2016: 02-01 03-21 03-24 09-16 11-02 11-21 12-12
- 2017: 02-06 03-20 04-13 11-02 11-20 12-12
- 2018: 02-05 03-19 03-29 05-01 11-02 11-19 12-12
- 2019: 02-04 03-18 04-18 05-01 09-16 11-18 12-12
- 2020: 02-03 03-16 04-09 05-01 09-16 11-02 11-16
- 2021: 02-01 03-15 04-01 09-16 11-02 11-15
- 2022: 02-07 03-21 04-14 09-16 11-02 11-21 12-12
- 2023: 02-06 03-20 04-06 11-02 11-20 12-12
- 2024: 02-05 03-18 03-28 05-01 09-16 10-01 11-18 12-12

Dropped because London or New York was closed: every Good Friday, plus 2017-05-01 and 2023-05-01 (UK May Day).
Holiday blocks: dates within 4 days of each other form one block (as round 19), e.g. 2010-09-16/17.

**Gotobi days (for the SG-1 split).** `research.swing.swing_rules.gotobi_days`: the 5th, 10th, 15th, 20th and 25th
and the last day of the month, a weekend day moved to the Friday before, with no Japanese holiday adjustment. The
calendar date is the Singapore (= Tokyo) date; the window 01:00-03:00 UTC lies on it.

## 2. Clocks and minutes
- **Time zones** from the tz database (zoneinfo): America/Mexico_City (DST abolished on 2022-10-30), Asia/Singapore,
  Asia/Shanghai (CN-1 is 06:30-08:30 UTC all year), Europe/London, America/New_York. The trade date is the local date.
- **Price at a declared minute T** (IC ticks):
  - the last tick with timestamp < T (ms), i.e. "the last quote before T" = the close of the M1 bar labelled
    T - 1 minute. A tick stamped exactly T belongs to the next bar.
  - If that tick is more than 10 minutes older than T, the quote is missing. A trade needs valid quotes at both of
    its minutes, else there is no trade that day.
  - (The brief's "at or before" differs only for ticks stamped exactly at T.)
- **Dukascopy M1 (PRE):** the price at T is the bid close of the last bar that starts at or before T - 1 minute and
  has bid volume > 0, at most 10 minutes stale. A zero-volume bar is no trading.
- **Stress "+1 minute":** both minutes become T + 1 (the last quote before T + 1).
- **MX-W's WMR minute:** 16:00 Europe/London on the trade date, converted to Mexico City. It is 10:00 MX on most days
  of 2007-2022 (09:00 on 3-5 days a year), and 09:00 MX on 147-152 banking days a year in 2023-24.
- **MX-C's day set:** MX-1 days on which the New York minus Mexico City UTC-offset gap, at 12:00 local, is 2 hours.
  That is 16-24 banking days a year in 2007-22 and 164-165 in 2023-24.

## 3. Returns and costs
**IS / VAL, IC ticks.** bp of the entry mid.
- Long: mid = (mid_exit - mid_entry) / mid_entry x 1e4, and net = (bid_exit - ask_entry) / mid_entry x 1e4 - 0.6.
- Short: mid = (mid_entry - mid_exit) / mid_entry x 1e4, and net = (bid_entry - ask_exit) / mid_entry x 1e4 - 0.6.
- Cost = mid - net.
- Spread x1.5: net = mid - 1.5 x (cost - 0.6) - 0.6.
- No swap: no declared window crosses 17:00 New York.

**PRE, Dukascopy M1.**
- The return is bid close to bid close, used as the mid proxy because the early asks are unreliable.
- Cost = half of the IC 2016-17 spread profile at the entry minute + half at the exit minute + 0.6 bp. The profile is
  the mean IC spread in bp ((ask - bid) / mid at the last quote before the minute), by local weekday x local minute.
  It uses the symbol's 2016-17 days of the cell's own day set:
  - Mexican banking days for USDMXN, SG business days for USDSGD, CN business days for USDCNH;
  - always excluding 24 Dec - 1 Jan;
  - built for every local minute that the cells and the random draws use.
- Information only: Dukascopy's own bid/ask spread at the minutes, and a mid-based PRE return, on bars whose ask is
  valid (aci > 0 and ask > bid).

**PRE starts.** USDMXN 2007-03-13 (Dukascopy start), USDSGD 2004-11-16, USDCNH at its first Dukascopy day of 2012
(declared 2012-06). PRE ends 2015-12-31.

## 4. Cells: what is computed and how they are compared
| cell | rule (as declared) | statistic |
|---|---|---|
| MX-1 | USDMXN long, 09:00 -> 12:00 MX, MX banking days | mid / net, by era and year |
| MX-15 | short 12:00 -> 12:15 MX, MX-1 days | mid / net (information) |
| MX-H | long 09:00 -> 12:00 MX on the 126 MX-H days | holiday mean; business-day (MX-1) mean minus holiday mean. Holiday side clustered by block, business side by day: t = diff / sqrt(se_b^2 + se_h^2). By era, and pooled 2007-24 |
| MX-W | MX-1 split at the WMR minute | on WMR = 10:00 MX days: part A 09:00 -> WMR and part B WMR -> 12:00 MX (mid, long), by era |
| MX-W sign test (amendment 19:50) | the same split | MX-1 on 2023-24 days with WMR at 09:00 MX (UK summer) vs 2023-24 days with WMR at 10:00 MX: both means, difference, Welch t. Information: MX-1 on the 3-5 WMR-09:00 days a year of 2007-22 |
| MX-C | MX-C days | MX clock = 09:00 -> 12:00 MX (MX-1 itself) vs NY clock = 10:00 -> 13:00 New York (= 08:00 -> 11:00 MX on those days). Both means, paired difference MX - NY with t over days, by era; MX-1 on the 1-hour-gap days as reference |
| MX-A | short 10:00 -> 11:00 MX | auction days (MX banking days 2015-03-11..2015-11-20) vs the other 2015 banking days. Means, difference, Welch t; sub-periods to 2015-07-30 (USD 52 m) and from 2015-07-31 (USD 200 m) as information; PRE only |
| SG-1 | USDSGD long, 09:00 -> 11:00 SGT, SG business days | mid / net by era and year; split by gotobi and non-gotobi days; correlation with C3 |
| CN-1 | USDCNH long, 06:30 -> 08:30 UTC, CN business days | mid / net by era and year |
| BOOK | MX-1 + SG-1 + CN-1 | see below |

**Correlation with C3.**
- C3's daily P&L is the sum of `usd_at_100_risk` by the UTC date of `t_out_utc`, over rows with `era` IS or VAL and
  `t_in_utc` < 2025. HOLD rows are skipped at read.
- SG-1's daily net is placed on its UTC date, which is its Singapore date. C3 counts as 0 on days it does not trade.
- Pearson correlation over the IS + VAL SG-1 days; also on gotobi days only, and on monthly sums.

**Code check before CN-1 (not a result).**
- Reproduce round 19's CNHC-I mid (+1.22, t 4.57 IS; +1.68, t 4.08 VAL) from the IC M1 bid bars round 19 used:
  research/data/USDCNH/m1, files named < 20250101 only.
- Then compute CN-1 at the IC ticks' bid/ask.

**BOOK.**
- Weights: each leg's trade is multiplied by w = 1 / sd_IS, where sd_IS is the sd of that leg's per-trade net in IS
  2016-21 at base costs. The same w is used in every era and every stress.
- A book day is a UTC date. Its P&L is the sum of w x net over the legs that traded that date, in units of IS sd ("R").
- The windows (01-03, 06:30-08:30, 14/15-17/18 UTC) never overlap: one position per symbol, at most 3 a day.
- Reported:
  - mean, t over book days, Sharpe per book day;
  - power = Sharpe x sqrt(1.73 x book days a year);
  - also sqrt(sum of max(leg power, 0)^2), as `emfix_book.py` computes it;
  - mid and net, PRE where legs exist, stresses, random control.
- Decay (book and legs): each trade's net is lowered by (1 - k) x the leg's VAL mean mid, for k = 0.65 and 0.30.

## 5. Random-entry control
- **Seeds:** 500 (at least 200), for MX-1, SG-1, CN-1, the BOOK and, for information, MX-15.
- **Draws:** per trade day and seed, the window start is shifted by an integer number of minutes drawn uniformly from
  [-180, +180], independently by day. The window keeps its length and side. The side is fixed by the rule, so
  "recomputing it" changes nothing.
- **Session:** the shifted windows lie in 06:00-15:00 MX, 06:00-14:00 SGT and 11:30-19:30 Beijing, within the local
  day. A draw is redrawn, up to 20 times, if its window meets 16:45-18:15 New York (entry < 18:15 and exit > 16:45 NY)
  or if a quote is stale. After 20 failures the day is dropped for that seed.
- **Costs** at the shifted minutes: IC bid/ask in IS / VAL; in PRE the 2016-17 profile at the shifted local minutes.
- **Statistic:** the share of seeds whose mean net (and mean mid) is below the cell's, by era.
- **Book:** seed s combines the legs' seed-s draws with the book weights.

## 6. Statistics and bars
- **t:** one trade per day and leg, so t = mean / (sd / sqrt(n)) is day-clustered. The book is clustered by UTC date.
- **Years:** calendar years of the local trade date; "years net > 0" counts the 9 years of IS + VAL. PRE years are
  reported separately.
- **Power:**
  - per-trade net Sharpe x sqrt(1.73 x trades a year of the era), at the IS size (IS mean / IS sd, IS trades / 6)
    and at the VAL size (VAL mean / VAL sd, VAL trades / 3);
  - decay: (k x VAL mid - VAL mean cost) / VAL sd x sqrt(1.73 x VAL trades / 3), for k = 0.65 and 0.30;
  - VAL / IS = VAL mid / IS mid (net ratio also shown).
- **Chance (4 counted cells: MX-1, SG-1, CN-1, BOOK):**
  - the max of 4 |N(0,1)| has its 95th percentile at 2.49;
  - a shared per-date sign-flip null (1,000 draws): one random sign per UTC date, applied to every leg's IS mid that
    date, with the book recomputed; statistic = the max |t_IS mid| over the 4 cells.
- **LIVE** (all of): IS net t >= 2.5; VAL net t >= 1.5; >= 6 of the 9 IS + VAL years net > 0; random control >= 95 %
  in IS and in VAL; net > 0 at spread x1.5 and at +1 minute in IS and in VAL; power at the VAL size >= 3.
- **DEMO** (all of): IS net t >= 2.0; VAL net > 0; random control >= 90 % in IS and in VAL; net > 0 at x1.5 and at
  +1 minute in IS and in VAL.
- The bars are never lowered.
- If a counted cell meets either bar, I write PREREG_DRAFT_E_<name>.md and stop that family (no further variants).
  All declared cells are still reported. HOLD is never opened.

## 7. Order and HOLD guard
**Order.**
1. Data checks (no returns): files per year, ticks per day, integer scale, spreads at the declared minutes.
2. PRE: MX-1 first, then MX-15, MX-H, MX-W, MX-C, MX-A, SG-1 and CN-1. Each PRE number goes into STREAM_E.md, with
   its time, before the IS / VAL number of the same cell is computed.
3. The CNHC-I code check, then CN-1 IS / VAL.
4. MX cells IS / VAL, SG-1 IS / VAL, then the BOOK, random controls, stresses and chance.

A symbol-year is used only when complete: IC 365 / 366 files; Dukascopy once its npz exists.

**HOLD guard.**
- IC files are selected by name < 20250101.
- Every loaded timestamp is asserted < 1735689600000. Dukascopy files end in 2015.
- C3 rows with era HOLD are skipped at read.
- HOLD is not on this Mac and is never fetched.
