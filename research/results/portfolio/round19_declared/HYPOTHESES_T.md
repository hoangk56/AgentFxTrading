# Round 19, stream T: declared literature rules (written before any return is computed)

Written 2026-10-06 03:47 UTC (`date -u` 03:46:53), after the literature pass and calendar downloads and before any
return of any rule below was computed. Brief: [BRIEF.md](BRIEF.md) (row T, "The rule of this round") and
round13_structural/BRIEF.md. HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31; Dukascopy
H1 (PRE) is 2004-2015. Every cell below is fixed in full (symbol, side, window, day set, cost); no scan, no
parameter search. The side always comes from the paper. Anything found after looking is information only.

Literature sources and the "tested before" check are in STREAM_T.md; the papers' windows were read from their PDFs
where available (Hu et al. 2022 Table 1-2; Etula et al. 2020 Section 1 and Figure 4; Dao et al. 2016 Tables 3-4).

## Common protocol (all families)

- Data: shared M1 panel (mid = (bid+ask)/2 closes, spread at the minute's last tick), 2016-01..2024-12. IS 2016-21
  (energies and BTC: as available, IS from 2018 where the panel starts later), VAL 2022-24. PRE 2004-15 only where
  Dukascopy exists (T7, FX H1, bid; cost = IC 2016-17 median spread at that UTC hour + 0.6 bp).
- Price at T = mid close of the last M1 bar ending at or before T (look back 5 min, else the event is skipped).
  Entry fills at the bar ending at T+1 min (latency variant T+2 min); exit at the bar ending at the exit time.
- Cost per trade = half spread at the entry minute + half at the exit minute (actual panel spreads) + 0.6 bp
  commission for FX and metals (0 for indices, energies, crypto) + swap per 17:00 New York rollover crossed:
  indices long -2 bp per night, short 0; energies -2.5 bp per night either side; the Friday rollover counts 3 nights.
  FX/crypto rules below are timed to cross no rollover. Variants: spread x1.5; both fills +1 minute.
- Statistics: mean bp per trade at mid and net; t clustered by UTC entry day (sum of legs per day); by year and by
  era; VAL / IS ratio of the mid effect; per-trade net Sharpe; power = Sharpe x sqrt(trades per year x 1.73) at the
  IS size and at the VAL size, plus the day-clustered version.
- Random-entry control per family (>= 200 seeds): same count, same side mix (side recomputed by the rule where it is
  data-dependent), same hold, random days of the same session / weekday type outside the event days.
- Family chance benchmark: per-day sign-flip permutation shared by all cells of the family (1,000 draws), median and
  95th percentile of the best |t_IS| at mid; plus the expected max of K normals.
- Bars: LIVE / DEMO exactly as in round13_structural/BRIEF.md. A cell that meets either on IS/VAL stops its family
  and gets a PREREG_DRAFT_T_<name>.md with the expected HOLD t on the VAL size.

## T1. Pre-announcement drift before NFP, ISM and GDP (Hu, Pan, Wang & Zhu 2022, JFE 143(2), "Premium for heightened uncertainty")

- Mechanism (paper): impact uncertainty builds before important scheduled releases and is resolved just before
  them; the equity market earns a premium in the window from the previous close to 5 minutes before the release.
  Paper (E-mini S&P 500, 1994-2018): NFP +10.10 bp (t 3.63), ISM +9.14 (t 2.10), GDP +7.46 (t 2.08); non-FOMC pooled
  2012-2018 +6.98 bp (t 2.27), stable across 1994-2000 / 2001-11 / 2012-18; 36 events a year; FOMC excluded here
  (pre-FOMC drift tested in round 3, contaminated, and gone after 2011 in the paper).
- Events (US, New York time): NFP 08:30 (BLS dates, releases.json US_NFP, 108 events 2016-24); GDP 08:30 advance /
  second / third estimate (BEA release schedules 2016-24 from Wayback snapshots, scratch cal/us_gdp.json, 107
  events; 2024-11-27 was 10:00); ISM manufacturing 10:00 on the first US business day of the month, January on the
  business day on or after 3 January (a rule: the exact ISM history was not retrievable; flagged). Days that are FOMC
  decision days are dropped (paper). If two events fall on one day, one trade ending at the earliest release - 5 min.
- Side: long. Exit: release time - 5 min (08:25 or 09:55 ET).
- Windows (2): (a) paper: entry at 16:00 ET on the previous US business day (fill 16:01), crosses the 17:00
  rollover (swap -2 bp, -6 bp over a weekend); (b) entry 18:00 ET (after IC's post-rollover hour, no swap).
- Event sets (2): all three (primary); NFP + GDP only (exact dates).
- Symbols: US500 (primary, the paper's instrument), US30, USTEC.
- Cells: 3 x 2 x 2 = 12. Primary cell: US500, window (a), all three.
- Control: the same window on random US business days that are not NFP/ISM/GDP/FOMC days, same weekday mix.

## T2. Month-end dash for cash (Etula, Rinne, Suominen & Vaittinen 2020, RFS 33(1), "Dash for Cash")

- Mechanism (paper): institutions that must pay cash on the last day of the month T sell equities by the settlement
  deadline (close of T-4 under T+3 settlement), depressing prices over T-8..T-4 ("price pressure"); prices recover
  over T-3..T-1 ("positive reversal"). US 2003-13: positive-reversal periods +103 % cumulative, pressure periods
  -31 %; 22 of 25 equity markets show the reversal. The deadline moves with the settlement cycle s: D = T-(s+1).
- Settlement cycles: US T+3 to 2017-09-04, T+2 from 2017-09-05 to 2024-05-27, T+1 from 2024-05-28; DE40, UK100
  T+2 throughout; JP225 T+3 to 2019-07-15, T+2 from 2019-07-16; HK50 T+2; AUS200 T+2 (from 2016-03-07, T+3 before).
- Trading days: the home exchange calendar (holidays package: NYSE, XETR-like German exchange days, UK, Japan
  (+ 31 Dec, 2-3 Jan), Hong Kong, Australia), weekdays only. T = last trading day of the month.
- Cash closes: US 16:00 ET, DE40 17:30 Frankfurt, UK100 16:30 London, JP225 15:00 Tokyo (15:30 from 2024-11-05),
  HK50 16:00 Hong Kong, AUS200 16:00 Sydney.
- Legs (2): (L) long from the cash close of D to the cash close of T-1; (S) short from the cash close of D-5 to the
  cash close of D.
- Symbols: US500 (primary), DE40, UK100, JP225, HK50, AUS200. Cells: 6 x 2 = 12; also the 6-index pooled L and S
  books (reported, counted as 2 more cells: 14).
- Control: the same legs anchored on a random trading day of the month instead of D (outside D-5..T), same hold.

## T3. Monday-return reversal (Ülkü & Andonov 2016, Quantitative Finance 16(4); Pigorsch & Schäfer 2024, FRL 65)

- Mechanism (papers): institutional / international trading is thin on Mondays, so Monday's index move is driven
  more by individual investors and reverses over the rest of the week; Pigorsch & Schäfer (US 2007-22): only the
  Monday afternoon part reverses.
- Signal: (a) Monday's index return, cash close of the previous trading day (Friday) to the Monday cash close;
  (b) Monday afternoon: 12:00 local to the Monday cash close. Side = - sign(signal). Monday must be a trading day.
- Trade: entry at the Monday cash close (+1 min), exit at the Friday cash close (4 nights; long pays 8 bp swap);
  (c) only for US500 and signal (a): exit at the Tuesday cash close (1 night).
- Symbols: US500 (primary), US30, USTEC, DE40, UK100, JP225 (cash clocks as T2; afternoon = 12:00 local, JP225
  12:30 Tokyo, after the lunch break). Cells: 6 x 2 + 1 = 13. Primary: US500 (a) to Friday.
- Control: the same rule with a random weekday (Tue-Thu) as the signal day, hold to the close 4 trading days later.

## T4. Tuesday blues in Australia (Chiah & Zhong 2021, JBF 133)

- Mechanism (paper): investor mood, and its contagion from the US Monday through the time-zone gap, makes Australian
  returns on Tuesday significantly lower than on other weekdays, more after a very negative US Monday.
- Side: short AUS200.
- Cells (3): (a) Tuesday close-to-close, Monday 16:00 Sydney -> Tuesday 16:00 Sydney (short, swap 0); (b) Tuesday
  cash session 10:00 -> 16:00 Sydney; (c) = (a) only when the US Monday return of US500 (Friday 16:00 ET -> Monday
  16:00 ET) is at or below the 20th percentile of its trailing 250 trading days (causal).
- Control: the same window on random Mon/Wed/Thu/Fri (Sydney) days, short.

## T5. Bitcoin Monday effect (Caporale & Plastun 2019, FRL 31; Aharon & Qadan 2019, FRL 31)

- Mechanism (papers): bitcoin returns on Mondays are significantly higher than on other days (2010-2017 data);
  weekend attention / flow resumption. Side: long BTCUSD.
- Cell (1): Monday 00:00 UTC (fill 00:01; if IC was closed for the weekend, the first quote after the reopen + 1 min)
  -> Monday 20:50 UTC (before the 21:00/22:00 UTC rollover; no swap). ETHUSD the same, information only.
- Control: the same window on random Tue-Fri, long.

## T6. Crude oil day of the week (Li, Zhu, Wen & Mohd Nor 2022, Energy Economics 106, 105817)

- Mechanism (paper, WTI 2007-2021): abnormal positive return on Wednesdays (inventory-report schedule), abnormal
  negative return on Mondays (sentiment; time-varying).
- Cells (4): (a) short XTIUSD Monday: Sunday 19:00 ET (an hour after the reopen, fill 19:01) -> Monday 14:30 ET
  (NYMEX settlement); (b) long XTIUSD Wednesday: Tuesday 18:05 ET (after the rollover hour) -> Wednesday 14:30 ET;
  (c), (d) the same on XBRUSD. No rollover crossed. IS 2018-21, VAL 2022-24. April 2020 kept (reported with and
  without, per the pitfalls list).
- Control: the same windows on random other weekdays, same side.

## T7. FX weekend overreaction (Dao, McGroarty & Urquhart 2016, J. Multinational Financial Management 37-38)

- Status: near-tested in round 3 ("weekend-gap fade: too few large gaps and no IS signal"); re-declared here with the
  paper's own threshold and horizons, and run on PRE, which round 3 did not have.
- Mechanism (paper, 2002-2014): after a large gap between the Friday close and the Monday (Sydney) open, majors
  reverse over the following day (panel mean -0.13 % after large up gaps, +0.24 % after large down gaps, to the US
  close).
- Pairs: EURUSD, USDJPY, GBPUSD, AUDUSD, USDCHF, USDCAD, NZDUSD.
- Gap = ln mid(Sunday 18:00 NY) - ln mid(Friday 16:55 NY). Large = below the 5th or above the 95th percentile of
  that pair's gaps over the trailing 260 weekends (at least 104), causal. Side = - sign(gap).
- Entry Sunday 18:00 NY (fill 18:01). Exits (2): (a) Monday 16:55 NY (paper's one-day US close; primary), (b)
  Monday 08:00 London (paper's EU open). No rollover crossed.
- PRE: Dukascopy H1 bid closes 2004-15 (Friday = close of the last H1 bar ending at or before 16:55 NY rounded to the
  hour; Sunday = close of the first full H1 bar ending at or after 18:00 NY; exits at the H1 close at or before the
  exit time); cost IC 2016-17 median spread at those UTC hours + 0.6 bp. The 2016-24 IC panel with M1 as above.
- Cells: 7 pairs x 2 exits = 14, plus the 7-pair pooled book for each exit (2): 16.
- Control: random non-Monday weekdays, entry 18:00 NY, same exits, same count, random side with the same mix.

## Count

T1 12, T2 14, T3 13, T4 3, T5 1, T6 4, T7 16: 63 declared cells in 7 families. Primary cells: T1 US500 (a) all;
T2 US500 L; T3 US500 (a); T4 (a); T5; T6 (a) and (b) on XTI; T7 pooled (a).

## Corrections written after T1-T6 numbers were seen (information only; none can become a candidate this round)

Written 2026-10-06 03:51 UTC (`date -u`), after T1-T3 results and the first T4-T6 run.
- T4 (c) is not executable as declared: its window (Monday 16:00 -> Tuesday 16:00 Sydney) starts before the US
  Monday session ends (Tuesday 06:00-08:00 Sydney), so the condition uses information from inside the trade. Its
  number is reported as invalid (look-ahead). The executable form, (c') = the Tuesday cash session 10:00 -> 16:00
  Sydney when the US Monday return is at or below its trailing 20th percentile, is run as information only.
- T6 on XBRUSD: IC's Brent CFD has no quotes at Sunday 19:00 ET (2018-19) or Tuesday 18:05 ET (it reopens later), so
  the declared entries do not fill. Execution fix for both energies: enter at the first quote at or after the
  declared clock (within 120 minutes), fill one minute later. XTI numbers are reported both ways.
