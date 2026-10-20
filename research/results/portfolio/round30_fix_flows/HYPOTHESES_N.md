# Round 30, stream N: the details H-NOK leaves open, fixed before any return is computed

Written 2026-10-18 09:33 UTC (from `date -u`). The cells are the ones declared in
[round25_surprises/HYPOTHESES_A.md](../round25_surprises/HYPOTHESES_A.md) (H-NOK, 2026-10-17 19:13 UTC, cost amendment
19:50 UTC): NOK-1 (primary), NOK-2 (USDNOK replica), NOK-P (EURSEK placebo), NOK-D (dose regression, mechanism),
NOK-A (announcement, information) and the Norwegian-bank-holiday placebo. Nothing below changes a side, window, day
set, sizing, cost or bar of that declaration; it only fixes what the declaration leaves open.

**State of knowledge when written.** No EURNOK, USDNOK or EURSEK return, price level or spread has been computed or
looked at in this project. I have listed the tick file names per year (EURNOK 2016-21 complete, 2022 partial; USDNOK
2016-19 partial; EURSEK none yet) and the Dukascopy folder (no NOK or SEK npz yet). I have not opened a price file. I
have read the non-price inputs: Norges Bank's monthly table (`r25/A/web/nok/nb_fx_monthly.csv`), its FAQ and press
releases, and today's fetches of the mid-month-change press releases (below).

Every fetch of this stream is logged with its `date -u` time in
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r30/N/web/fetch_log.tsv`.
Downloads are in that `web/` folder and were read as text with `python3 -I`.

## 1. The daily amount A_d (NOK million per day; + = Norges Bank buys foreign exchange = sells NOK = buys EURNOK)
- **Base.** A_d = the month's value in Norges Bank's table (`nb_fx_monthly.csv`, 2000-2026).
- **Mid-month changes.** Norges Bank's table marks five months with "*". The annotations are in the saved table page
  (`data-annotation` attributes), and the dated press releases were fetched today at 09:27-09:29 UTC:
  | month | before | after | source (press release, publication time as printed, Oslo) |
  |---|---|---|---|
  | 2008-10 | +1,400 (1-22 Oct) | +620 from Thu 23 Oct | "Press release 30 September 2008" (10:00): 1,400 per day in October; "Press release 22 October 2008" (15:45): "from NOK 1 400 million to NOK 620 million per day, effective as from 23 October" |
  | 2020-03 | -500 (1-17 Mar) | -1,600 from Wed 18 Mar | 2020-02-28 (10:00): sell FX equivalent to NOK 500 million per day; 2020-03-18 (08:00): "Effective from today, Wednesday, 18 March ... from NOK 500 million to NOK 1 600 million" |
  | 2020-11 | -1,600 (1-20 Nov) | -500 from Mon 23 Nov | 2020-10-30 (10:00): sell FX equivalent to NOK 1600 million per day; 2020-11-23 (09:00): "Effective from Monday, 23 November ... from NOK 1 600 million to NOK 500 million" |
  | 2021-11 | -700 (1-18 Nov) | 0 from Fri 19 Nov | 2021-10-29 (10:00): sell FX equivalent to NOK 700 million per day; 2021-11-18 (12:00): "With effect from Friday, 19 November ... from NOK 700 million to zero for the remainder of the month" |
  | 2003-05 | - | 0 from 2003-05-20 | outside every era; not used |
  - The table shows the first amount for 2008-10 and 2021-11 and the second for 2020-03 and 2020-11. Its annotations
    date the 2008 and 2021 changes one day earlier (10/22/2008, 11/18/2021) than the press releases' effective dates.
    **The press releases' effective dates are used.**
  - On 2020-03-18 (release 08:00) and 2020-11-23 (release 09:00) the new amount is used for the whole day.
- **End of December.** Norges Bank "does not ordinarily carry out foreign exchange transactions ... at the end of
  December" (FAQ). NOK-1/2/P exclude 20-31 Dec as declared. In NOK-D, business days 20-31 Dec enter with A_d = 0;
  robustness: NOK-D without 20-31 Dec.
- The side, the |A| >= 100 filter and the size all use A_d, the amount in effect that day. For example, 2021-11-19..30
  (A_d = 0) are not NOK-1 days.

## 2. Calendar
- **Norwegian bank business day:** Monday-Friday, not a public holiday in `holidays.NO` (python-holidays 0.106,
  category public: 1 Jan, Maundy Thursday, Good Friday, Easter Monday, 1 May, 17 May, Ascension Day, Whit Monday, 25
  and 26 Dec), and not 24 or 31 Dec (bank holidays).
  - No official holiday page could be fetched (lovdata 404 at 09:30:58 UTC).
  - Norges Bank's own announcement dates (from its English sitemap, fetched 09:28:59 UTC) agree with this calendar:
    the January amount is published on 30 Dec in 2020, 2021, 2024 and 2025, when the 31st was a weekday, and the
    April 2024 amount on 27 March, the day before Maundy Thursday.
- **Eras.**
  - PRE runs from each symbol's first Dukascopy day with data to 2015-12-31 (EURNOK from 2004-10-25).
  - IS is 2016-01-01..2021-12-31 and VAL 2022-01-01..2024-12-31.
  - Every load asserts ts < 1735689600000 (2025-01-01). HOLD is never loaded.
- **Completeness.**
  - An IC symbol-year is used only when its t1 folder holds every calendar day of the year (365/366 files).
  - A Dukascopy symbol-year is used only once its npz exists. The downloader writes one only when no day failed;
    days that are missing on the server are listed in the log.

## 3. Clock and minute convention
- Local times are on the Oslo clock (zoneinfo `Europe/Oslo`, DST-aware; Stockholm is the same clock).
- **IC ticks.** The quote "at T" is the last tick with ts <= T (ms), with bid and ask forward-filled by
  `research.ticks.load_ticks`. It is valid if it is at most 30 minutes old; otherwise the day drops out of that cell
  and is counted as dropped.
- **Dukascopy M1 (bar-start labels).** The quote "at T" is the close of the last bar starting at or before T - 60 s
  (the bar labelled T - 1 min, or an earlier one) with bid volume > 0, since a zero-volume minute is no trading. It is
  valid if that bar is at most 30 minutes old.
- **Fills.** NOK-1/2/P/D enter at 09:00:00 and exit at 16:00:00 Oslo. The side is known a month ahead, so no signal
  minute is involved. Stress test: both fills +1 minute (09:01, 16:01) and spread x1.5.
- **NOK-A** (information only).
  - Day: the last Norwegian bank business day of month m. The rule fixes it; it is not taken from the press releases.
    Months where the sitemap shows another date (e.g. "2021-08-30-fx") are listed.
  - Side: sign(A_{m+1} - A_m), where A_{m+1} is the amount for the first day of m+1 and A_m the amount in effect on
    the announcement day. Months where the two are equal make no trade.
  - Window: the declared 10:00 -> 10:15 at mid, which includes the announcement minute. Also an executable variant,
    10:01 -> 10:15, ask in / bid out + 0.6 bp, since the amount is known only after 10:00.

## 4. Returns, costs, size
- Mid return r = s x (mid_out - mid_in) / mid_in x 1e4 bp, with s = sign(A_d) and mid = (bid + ask) / 2.
- **IC executable return.**
  - A long buys at ask_in and sells at bid_out. A short sells at bid_in and buys at ask_out.
  - The executable return is (exit - entry) x s / mid_in x 1e4, and net = executable - 0.6 bp.
  - Cost = mid - net. Spread x1.5: net = mid - 1.5 x (mid - executable) - 0.6.
- **PRE.**
  - The return is computed on Dukascopy BID closes (bid to bid), since early Dukascopy asks are unreliable.
    Dukascopy's (bid + ask) / 2 mid is reported as a check where the ask is valid (aci > 0 and ask >= bid).
  - Cost: half of IC's 2016-17 mean spread (in bp of mid) at the entry minute of week, plus half at the exit minute
    of week, + 0.6 bp. Minute of week means Monday-Friday x 1440 minutes on the Oslo clock; the spread at a minute is
    ask - bid of the last tick at or before it.
  - Spread x1.5 uses 1.5 x that profile; +1 minute uses the profile at 09:01 and 16:01. The median profile is
    reported as information.
- **Size (NOK-1/2/P).** w_d = clip(|A_d| / 1000, 0.5, 2). The P&L per trade is w_d x net_d, in bp of the default lot
  (cost scales with the lot). Unweighted (w = 1) results are information only.
- **Swap.** None: every window ends at or before 16:01 Oslo, before 17:00 New York.

## 5. Statistics and controls
- **t.** There is one trade per day, so the day-clustered t is mean / (sd / sqrt(n)) with ddof 1.
- **Reported** by era and by year: the count of years net > 0, VAL / IS of mid and of net, and trades per year.
- **Power.**
  - Power = per-trade net Sharpe x sqrt(1.73 x trades per year), at the IS size and at the VAL size (the same on day
    clusters).
  - Decay readings: (0.65 x VAL mid - VAL cost) / VAL sd x sqrt(1.73 x VAL trades per year), and the same with 0.30.
- **Random-entry control** (NOK-1, NOK-2, NOK-P; per era).
  - 1,000 seeds. In each seed every trade day independently draws an integer shift u ~ U{-180..+180} min. The window
    becomes [09:00 + u, 16:00 + u] Oslo: same day, same 7 h hold, 06:00-19:00 at the extremes.
  - Side sign(A_d): the rule gives the same side at any time of day. Same weights.
  - Net uses the actual quotes and spreads at the shifted minutes (PRE: the IC 2016-17 profile there) + 0.6 bp. A
    stale quote redraws u, at most 20 times.
  - Statistic: the mean weighted net per trade, and the same at mid. "Beats x %" is the share of seeds whose statistic
    is below the actual one.
  - A cell meets the 95 % (LIVE) or 90 % (DEMO) criterion only if **both** the net and the mid versions do. This
    guards against the pitfall that a window in liquid hours beats random windows on cost alone.
- **NOK-D.**
  - OLS of the 09:00 -> 16:00 mid return (bp) on A_d (NOK bn per day) with a constant. Day set: all Norwegian bank
    business days of the era, zero-amount months included; 20-31 Dec with A_d = 0.
  - Slope t: HC1, which with one observation per day is the day-clustered t.
  - Also reported: the month-clustered t, since A is constant within a month and a common within-month move would
    inflate the day t.
  - Eras: PRE first (declared order), then IS, VAL, IS + VAL and 2004-24.
  - Robustness: without 20-31 Dec; and the slope with A_d replaced by sign(A_d) x clip(|A_d| / 1000, 0.5, 2), the
    NOK-1 dose.
- **Chance benchmark.**
  - The family has 2 trading cells: NOK-1 (counted) and NOK-2 (its replica). The 95 % quantile of the max |t| of 2
    independent normals is 2.24.
  - Counting all 5 declared cells, it is 2.57.
  - NOK-1 is compared with both.
- **Holiday placebo.**
  - Days: Maundy Thursday, Whit Monday and 17 May when a weekday (the declared list), in months with |A_d| >= 100,
    with valid quotes.
  - NOK-1's window, side and weight; mid and net. Each holiday is its own cluster, pooled 2004-24 and by era.
  - Also: business days minus holidays, with a Welch t. Predicted ~0 on holidays.
  - Extension, information only and beyond the declared list: Ascension Day and 1 May when a weekday.
- **Declared order of computation.**
  1. NOK-D on PRE, written into STREAM_N.md.
  2. NOK-1 on PRE, written.
  3. NOK-1 on IS / VAL.
  4. NOK-2 and NOK-P the same way: PRE first, written, then IS / VAL.
  5. NOK-A and the holiday placebo after NOK-1.

## 6. Tiers
- The tiers are the user's bars, unchanged.
- **LIVE:**
  - IS t >= 2.5 and VAL t >= 1.5;
  - >= 2/3 of the IS + VAL years net > 0;
  - beats >= 95 % of random entries;
  - net > 0 at spread x1.5 and at +1 min in IS and VAL;
  - power >= 3 on the VAL size.
- **DEMO:**
  - IS t >= 2.0 with net > 0 in IS and VAL;
  - beats >= 90 % of random entries;
  - net > 0 at x1.5 and +1 min.
- NOK-1 is the counted cell. NOK-2 is reported against the same bars as a replica, and NOK-P and NOK-D as checks.
- If a cell meets a bar, PREREG_DRAFT_N_<name>.md is written and the family stops. HOLD is not opened.

## Amendment 1 (2026-10-18 09:59 UTC, still before any return; the reason is a data-quality check, not a result)
Data checks run since 09:33 (`snap_duka.py`, `glitch_check.py`; they look at quote validity only, not at window
returns) found:
- **Dukascopy EURNOK trades only on a few days in 2004-05.** Price changes occur on 21 of 57 days of 2004 and 23 of
  310 of 2005. The other days are flat zero-volume bars, which section 3 already drops (stale quote). Activity rises
  in 2006 (173 of 260 weekdays traded) and 2007 (215 of 261).
- **Dukascopy has junk quotes in its early years.** In 2004-07, 808 Oslo-hours minute-boundary bids deviate by more
  than 1 % from the median of the quotes at T-5..T+5 min; 5 of them are at the declared minutes. Example: 2007-04-02
  06:00-07:00 Oslo, a repeated 8.27426 while the market is at 8.12-8.19. The Dukascopy ask equals the bid on most
  traded bars of 2007.
- IC EURNOK 2016-24 and USDNOK 2016-21 have no deviation > 1 % at 09:00 / 16:00 / 09:01 / 16:01, and only one
  > 1 % at any Oslo minute 06:00-19:01 (USDNOK 2020-03-30 08:14).

Rule, fixed now:
- **Glitch filter, for every source and every cell:** a quote at minute T is invalid if its price deviates by more
  than 1 % from the median of the valid quotes at T-5..T+5 min. The price is the mid for IC and the bid for
  Dukascopy.
  - An invalid quote drops the day from the cell; in the random control it redraws the shift. Dropped days are
    counted.
  - A 1 % move inside ±5 minutes is a > 10-sigma event for EURNOK. The window looks at most 5 minutes ahead and is
    used only to reject data, never for a side.
- **Information only:** the same cells without the filter.
- **PRE coverage:** a PRE year enters only through its valid days. Valid days per year are reported. No minimum is
  imposed, so 2004-05 contribute only a few days.
