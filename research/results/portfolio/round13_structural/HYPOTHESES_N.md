# Round 13, stream N: structural calendar flows (tax dates, Treasury settlement, bond-index extension, fiscal-year ends, quarter-end funding)

Written 2026-10-06 01:33 UTC, before any price was loaded in this stream. Calendars were built from rules and
official records (no prices): IRS due-date rules, Treasury auction records (fiscaldata.treasury.gov
`auctions_query`, 11,140 auctions 1979-2025, downloaded 01:28 UTC), the `holidays` package, Bloomberg's index
methodology (rebalance on the last business day of the month). Literature: Hartley & Schwarz (2019, SSRN 3440417:
Treasury excess returns are positive only in the last few days of the month; life insurers buy on index rebalancing
dates); Afonso, Cipriani, Copeland et al. (2020, SSRN 3549473: the 16-17 Sep 2019 repo spike on the corporate-tax day
plus a large net coupon settlement); Du, Tepper & Verdelhan (2018, JF, quarter-end CIP spikes after 2015); Aldasoro,
Ehlers & Eren (2022, JIE, global banks' quarter-end dollar funding).

## Common conventions (fixed now)
- Eras: PRE 2004-2015 (Dukascopy bid: M1 for USDJPY EURJPY GBPJPY USDCHF EURUSD; H1 for AUDUSD NZDUSD GBPUSD USDCAD,
  XAUUSD and the rest), IS 2016-2021, VAL 2022-2024 (IC panel, mid). HOLD is never loaded.
- All windows are on the hour in New York time (or Beijing time for N6), so H1 bars serve PRE.
- **USD3** = equal-notional long-USD basket of EURUSD (short), USDJPY (long), GBPUSD (short): a bot of 3 positions.
  The 7-pair USD basket (+ AUDUSD, NZDUSD, USDCAD, USDCHF) is a diagnostic only. Gold = XAUUSD. US equities = US30
  (cheapest IC index; IS/VAL only), US500 diagnostic.
- One number per event: the mean of the legs' returns (bp); t across events (= clustered by event day; events that
  share a day are merged). Costs: half spread at entry + exit minute (panel; PRE: IC 2016-17 median spread at that
  minute of day), 0.6 bp commission FX/metals, swap for every 17:00 ET rollover crossed (`research/swing/rates.py
  swap_frac_at`; indices about -2 bp per night long). Variants: +1 minute both fills (M1 data), spread x1.5.
- Random-entry control: same window on random other business days of the same weekday and the same year (one per
  event), 500 seeds. Placebos as listed per family.
- Effect by era (PRE / IS / VAL), by year, and the ratio VAL / IS for every cell; power = per-trade net Sharpe x
  sqrt(expected HOLD events) on the IS and on the VAL size.
- Pass bars as in the brief; DEMO is the realistic tier (2-12 events a year).

## N1 US tax dates: reserve drain into the Treasury General Account -> USD scarcity
- Mechanism: on corporate estimated-tax due dates, $50-150 bn moves from bank deposits to the TGA in a day, draining
  reserves; repo and fed funds rise (16-17 Sep 2019 is the extreme). Dollar funding demand should lift the dollar,
  weigh on gold (higher USD rates, dollar up) and on US equities (liquidity drain).
- Calendar (rules, IRS Pub. 509 / Form 1120-W, IRC 7503): 15 Apr, 15 Jun, 15 Sep, 15 Dec, moved to the next
  business day for weekends, federal holidays and DC Emancipation Day (April); 2020: Apr and Jun payments deferred to
  15 Jul (Notice 2020-23); calendar-year corporations' annual payment due 15 Mar for tax years through 2015 (15 Mar
  2004-2016 included); the individual April deadline when it is a separate day (17 May 2021). About 5 a year before
  2017, 4 after.
- Why it may escape the limits: the dates are set by law and the drain does not depend on anyone trading it;
  rounds 3-12 never tested tax dates (the 90k calendar scan used business day +-1..5 of the month, not the 15th).
  Decay risk: the size depends on reserve scarcity (high 2018-19 and 2022-24, low 2009-14 and 2020-21), so VAL could
  be as large as IS.
- Rule (side fixed by the mechanism): E = due date.
  - N1a "payment day": E-1 16:00 ET -> E 16:00 ET: long USD3, short XAUUSD, short US30.
  - N1b "pre": E-3 16:00 ET -> E-1 16:00 ET (anticipation in funding markets): same sides.
  - N1c "after": E 16:00 ET -> E+2 16:00 ET: reversal of temporary price pressure: short USD3, long XAU, long US30.
  - N1d dose: N1a on dates whose same-day net coupon settlement (N2's measure) is above the IS median of tax dates.
- Cells: 4 x 3 instruments = 12. Placebo: the 15th (business-day adjusted) of the non-tax months Jan, Feb, May, Jul,
  Aug, Oct, Nov (Jan 15 is an individual estimated-tax date: reported separately); random same-weekday days.

## N2 US Treasury coupon settlement days: dealers must finance new issuance
- Mechanism: on a coupon settlement day, cash for new notes/bonds leaves the banking system (net of maturing
  publicly held coupons); dealers finance their allotment in repo. Large net settlements tighten dollar funding (the
  2019 spike). Same sides as N1: long USD, short gold, short US30 on the settlement day; temporary, so reversal after.
- Calendar: fiscaldata `auctions_query` issue dates of Notes, Bonds, TIPS and FRNs. Net coupon settlement NCS =
  sum of offering amounts (public, excl. SOMA add-ons) - publicly held maturing coupons (2008+: the auction record's
  `est_pub_held_mat_by_type_amt`; 2004-07: sum of original offering amounts of coupons maturing that day). Known
  about a week ahead (announcement), so usable ex ante.
- Why new: round 4 tested auction days (Lou, Yan & Zhang 2013), not settlement days; settlement sizes are fixed by
  Treasury's financing schedule.
- Rule: S = coupon settlement day.
  - N2a "large": NCS in the top third of the coupon settlement days of the previous 24 months (causal).
  - N2b "refunding": the 15 Feb / May / Aug / Nov settlement (next business day if needed).
  - Windows: "day" = S-1 16:00 ET -> S 16:00 ET with long USD3, short XAU, short US30; "after" = S 16:00 ET ->
    S+1 16:00 ET with the opposite sides.
  - N2c dose: OLS slope of the "day" return on NCS z-scored within era (one per instrument).
- Cells: 2 classes x 2 windows x 3 instruments + 3 slopes = 15. Reported splits: mid-month vs month-end
  settlements, with and without N1 tax dates.

## N3 Bond-index month-end extension: Treasuries rally into the last business day's index snapshot
- Mechanism: index-tracking bond investors (Bloomberg US Aggregate / Treasury rebalance on the last business day,
  US bonds priced at 15:00 ET) buy duration at month-end; Hartley & Schwarz (2019) find coupon Treasury excess returns
  positive only in the last few days of the month. Lower US yields -> USDJPY down, gold up.
- Why it may escape: the extension follows the index rule and issuance, not prices; earlier month-end tests were
  London-clock (WM/R fix: F1, M1, round 12 I) and USD-demand sided; this is a New York 15:00 bond snapshot with the
  yield-channel side. Overlap disclosed: round 3's 90k hour-level scan included the last business day at these UTC
  hours without a hit.
- Rule: L = last US business day of the month (weekdays not federal holidays / Good Friday).
  - N3a: L 13:00 -> 15:00 ET: short USDJPY, long XAUUSD.
  - N3b: "last few days": 15:00 ET on the 4th-last business day -> L 15:00 ET (3 days): short USDJPY, long XAU.
  - N3c: L 15:00 -> 16:00 ET, reversal after the snapshot: long USDJPY, short XAU.
  - N3d dose: N3a in refunding months (Feb, May, Aug, Nov), when the extension is largest.
- Cells: 4 x 2 = 8. Placebo: the same clock on the 2nd-to-last and 5th-to-last business days.

## N4 Fiscal-year-end repatriation: home currency bought before the year-end, sold after
- Mechanism: firms and financial institutions with a fiscal year-end repatriate foreign earnings and square foreign
  positions before the books close, and re-invest abroad at the start of the new year (Japanese life insurers'
  April plans). Side: home currency up over the last 5 business days to the year-end, down over the first 5 after.
- Calendar: Japan 31 Mar (full year) and 30 Sep (half year), Australia 30 Jun, New Zealand 31 Mar (tax year and
  most listed companies). Business days from the `holidays` package for each country plus the US.
- Why it may escape: year-ends are statutory; not tested in rounds 3-12. C3 overlap: windows of 5 days contain the
  Tokyo fix and gotobi days; I report a diagnostic that excludes 23:00-02:00 UTC from the JPY return and the
  correlation with C3. UK (5 Apr: personal tax and ISA flows are domestic, no FX leg), Canada (government 31 Mar,
  banks 31 Oct: no documented repatriation) and Switzerland (calendar year = every other year-end flow) are not
  tested.
- Rule: Y = last home business day on or before the year-end date.
  - pre: 16:00 ET on the business day 5 home business days before Y -> 16:00 ET on Y: long home currency
    (short USDJPY; long AUDUSD; long NZDUSD).
  - post: 16:00 ET on Y -> 16:00 ET 5 home business days later: short home currency.
- Cells: (JP-Mar, JP-Sep, AU-Jun, NZ-Mar, pooled) x (pre, post) = 10. Placebos: the same windows at the other three
  quarter-ends of the same currency; other countries' year-ends for the same currency.

## N5 Quarter-end dollar funding (window dressing by non-US banks; G-SIB scores at year-end)
- Mechanism: non-US banks report quarter-end snapshots and cut repo / FX-swap intermediation at quarter-ends; the
  dollar is scarce over the turn (Du, Tepper & Verdelhan 2018), most at year-end (G-SIB surcharge).
- Overlap disclosed: round 3 M1 (3rd-to-last weekday, every month, 10:00-13:00 UTC) found quarter-ends not stronger.
  This is a multi-day, quarter-only rule with non-quarter month-ends as placebo.
- Rule: Q = last US business day of Mar/Jun/Sep/Dec.
  - N5a pre: 16:00 ET on the 4th-last business day -> Q 16:00 ET: long USD3.
  - N5b post: Q 16:00 ET -> 16:00 ET on the 2nd business day of the new quarter: short USD3.
  - N5c, N5d: the same two at year-end only.
- Cells: 4. Placebo: the same windows at the 8 non-quarter month-ends.

## N6 Chinese tax period (onshore liquidity drain before the monthly tax deadline)
- Mechanism: Chinese firms pay VAT and income-tax prepayments by the 15th (quarterly months Jan / Apr / Jul / Oct
  largest, plus the May annual settlement); the drain tightens onshore liquidity (repo rates rise; PBOC injects).
  Tight RMB liquidity -> CNH up (USDCNH down).
- Calendar: deadline = 15th, extended per the Implementing Rules of the Tax Collection Law art. 109 (a deadline on a
  rest day moves to the next working day; 3+ consecutive statutory rest days inside the period extend it by their
  length), Chinese holidays from the `holidays` package. IS/VAL only (USDCNH bid bars from 2016, round 7 spread).
- Rule: short USDCNH from 15:00 Beijing three Chinese business days before the deadline -> 15:00 Beijing on the
  deadline. N6a quarterly months; N6b all months.
- Cells: 2.

## Multiple testing
51 declared cells. Chance benchmark: for 51 independent two-sided tests, the 95th percentile of max |t| is about
3.3; I also run a per-family sign-flip permutation by event. The bar's IS t applies on the registered side only.

## Status at 01:38 UTC (declared cells done; numbers in STREAM_N.md)
No declared cell meets DEMO on its registered side (best registered IS t 2.68, N2a US30 after, VAL < 0).

## N7 (POST HOC, written 2026-10-06 01:38 UTC after seeing the N1 placebo): mid-month payday flow into US equities
- Seen: the N1 placebo "15th of non-tax months, short US30" was -31.5 bp IS (t -2.95) / -52.8 VAL (t -2.79), i.e.
  US30 rises from 16:00 ET on the day before the 15th to 16:00 ET on the 15th; the refunding-day cell (15 Feb/May/
  Aug/Nov) shows the same. Post hoc: the side, the window and the day were all read off the data.
- Mechanism (written after seeing it): semi-monthly payrolls (15th and last day) are followed by defined-
  contribution (401(k)) contributions invested in equity funds within days; payment cycles move equity returns
  around the turn of the month (Etula, Rinne, Suominen & Vaittinen 2020, RFS, "Dash for Cash"). The payroll calendar
  is set by employers and law (semi-monthly pay is mandated in several states), not by prices.
- Rule: D = the 15th, or the next US business day. N7a: long US30 from 16:00 ET on the business day before D to
  16:00 ET on D (one overnight, ~-2 bp swap). US500, USTEC reported alongside. All 12 months (incl. tax months).
- Checks fixed now: shifted placebos (the same window ending on the 8th..22nd, every business-day position);
  random same-weekday/same-year days (500 seeds); split overnight (16:00 -> 09:30 ET) vs cash session (09:30 ->
  16:00 ET); without monthly option expiry (3rd Friday) days; by year; VAL / IS. No PRE (no index data before 2016).
  It counts as one more family (1 cell; 3 symbols reported); with the declared 46-51 cells the chance p95 of max |t|
  is about 3.3 (normal) / 5.0 (sign-flip null on these small cells).
- N7 result (01:39 UTC): fails as declared (all 15ths, US30 IS net -3.0 bp t -0.14, VAL +14.0 t 0.86); the shifted
  placebos (day-of-month 5..28) range IS t -2.6..+1.7, so the 15th is not special; the placebo signal came from
  which months were in the subset (March 2020 sat in neither N1 nor the placebo). Rejected.

## N8 (declared 2026-10-06 01:39 UTC, before its numbers): net Treasury bill settlement (the bill half of N2)
- Mechanism: as N2, for bills. Bills settle on Tuesdays and Thursdays (plus cash-management bills); a large net bill
  settlement (new bills minus maturing publicly held bills, both known from the auction announcements) drains cash
  from banks / money funds on that day (2023 TGA rebuild after the debt ceiling is the extreme). Same sides as N2:
  long USD3, short XAU, short US30 over S-1 16:00 ET -> S 16:00 ET.
- Calendar: fiscaldata `auctions_query` Bills (incl. CMBs): net = sum offering amounts - `est_pub_held_mat_by_type_amt`
  for bills (2008+; 2004-07 from the matured bills' offering amounts).
- Cells: top third of net bill settlement among bill settlement days of the previous 24 months (causal) x 3
  instruments, plus the dose slope (net z within era) x 3 = 6 cells. ~35-50 events a year: the only N family with
  enough events for LIVE power if real.
