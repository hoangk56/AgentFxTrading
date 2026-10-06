# Round 19, stream H: hypotheses (the E1 mechanism in other currencies)

Written 2026-10-06 03:18-03:19 UTC (`date -u` 03:18:16 at the start, file time 03:19:01), before any round-19 return
was computed (the E1 code check ran at 03:21, the declared cells at 03:22).
HOLD (2025-01-01 onwards) is never loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, the USDCNH cache
ends 2024-12-31 21:58 UTC, and every day list is capped at 2024-12-31.

## What I had seen before writing this (disclosure)
- Round 13 M (E1 and its family table), round 14 R (TARGET2 check), round 15 S (ECB V moved at end-2015), round 10 A
  (A4) and E (WM/R, ECB, Sydney V, SGE). In particular: M's "same window on every symbol" line (E1's 11:00-13:00
  London window is wrong-signed or ~0 after 2016 on AUD, NZD and CAD), M's families "USDCHF long 10:00-13:15 UTC",
  "NZDUSD long 05:00-07:00 London (gone in VAL)", round 10 E's WMR-pre (USD long into 16:00 London on EURUSD+GBPUSD,
  +0.30 / -0.19 bp) and the Sydney V at 10:00 Sydney.
- Round 7 B's USDCNH output, which prints the IS and VAL mean return by UTC hour (I read it while locating the CNH
  data) and its "long USDCNH 01:30-08:30 UTC" result (+1.17 / +2.03 bp).
- None of this changes a side or a window below: every side is the mechanism's, every window is the fix time plus
  the fixed lengths declared in the next section, chosen before any number of this round.

## Mechanism (E1's, from the literature)
A home currency weakens into its own reference-rate fixing during its home hours and recovers after: home investors
and corporates buy foreign currency at the home fix (asset managers hedging/rebalancing, importers, benchmark
orders), dealers pre-hedge into the fix and the price rebounds once the fix is struck (Ranaldo 2009, "Segmentation
and time-of-day patterns in foreign exchange markets", JBF; Breedon & Ranaldo 2013, "Intraday patterns in FX returns
and order flow", JMCB; Krohn, Mueller & Whelan 2024, "Foreign exchange fixings and returns around the clock", JF; in
this repo E1 and the ECB V, rounds 10-15, and E1's reversal on TARGET2 closing days, round 14 R).

So for every fix: **INTO** = the home currency is sold over the window that ends at the fix; **AFTER** = it is bought
from the fix for a short time.

## The fixes (official sources; times and their history)
| id | fix | local time (clock) | history used | symbol | days (fix published) | source |
|---|---|---|---|---|---|---|
| CADN | Bank of Canada noon rate | 12:00 ET (America/Toronto); window 11:59-12:01 since 2005-11-07, 11:55-12:05 before | published until 2017-04-28 (new rate in parallel from 2017-03-01; noon dropped 2017-05-01) | USDCAD | Canadian (Ontario) business days | bankofcanada.ca 2005/10 "Changes regarding noon foreign exchange rates"; 2016/02 and 2016/12 announcements; 2017/03 "begins publishing new FX rate data" |
| CADD | Bank of Canada daily average rate | truncated mean of 1-minute quotes 08:00-16:00 ET, published by 16:30 ET | 2017-03-01 on (used here from 2017-05-01, when it became the only rate) | USDCAD | Canadian (Ontario) business days | bankofcanada.ca "Background information on foreign exchange rates" |
| AUD | RBA daily rate | 16:00 Sydney (Australia/Sydney) | unchanged over 2004-24 | AUDUSD | NSW business days ("published daily except on public and bank holidays observed in NSW") | rba.gov.au exchange-rates statistics page and RSS notes |
| NZD | RBNZ B1 rate | 11:10 NZ until 2015-04-30 (indicative LSEG mid); **14:00 NZ** from 2015-05-01 (WM/LSEG NZ Dollar Fix 14:00, NZFMA) | as stated | NZDUSD | NZ (Wellington) business days | rbnz.govt.nz B1 series notes ("between 1 April 1991 and 30 April 2015 ... 11:10am mid-rates; from 1 May 2015 ... WM/LSEG 2:00pm fixes from NZFMA") |
| GBP | WM/R 16:00 London (BoE daily spot rates "around 4pm") | 16:00 London; WM/R window 15:59:30-16:00:30 until 2015-02-15, 15:57:30-16:02:30 after | as stated | GBPUSD | England business days (BoE rate not published on bank holidays) | bankofengland.co.uk database notes; FSB FX benchmarks report 2014 / WM implementation 2015-02-15 |
| CHF | SNB daily rates | 11:00 Zurich (based on Bloomberg BFIX today) | assumed unchanged (no dated history found) | USDCHF | Zurich business days | snb.ch statistics pages; SNB data portal update time 11:00 Zurich |
| CNHT | TMA USD/CNY(HK) spot fixing (the CNH fix) | 11:00 Hong Kong (contributions at 11:00, published 11:15) | launched 2011-06-27; transaction-based from 2016-08-01, time unchanged | USDCNH | Hong Kong business days | HKMA/TMA press release 2011-06-23 and specifications; TMA 2016 transition notice |
| CNHC | CFETS onshore CNY 16:30 close (feeds the next day's 09:15 central parity) | 16:30 Beijing | 16:30 stays the official close after the session was extended to 23:30 (2016-01-04) and 03:00 (2023-01-03) | USDCNH | mainland China business days | CFETS 2022-12-30 notice; PBC/SAFE 2015-12-30 Q&A |

Not used: JPY (C3); EUR (the ECB fix is E1 itself; E1 is re-run only as a code check, not counted); CFETS 09:15
central parity (an announcement, not a dealing fix; round 7 H6 tested its surprise); currencies without data here
(SGD, HKD, MXN, ZAR, Scandinavians: new price series need the user). RBA 16:00 and the Sydney 10:00 V are different
times; the Sydney V is already on record (rounds 10-12) and is not re-declared.

## Declared cells (23 counted)
Lengths, fixed for every fix: INTO = the 120 minutes ending at the fix (E1's length); AFTER15 = fix to fix+15;
AFTER60 = fix to fix+60 (the length H1 data can resolve). Exceptions forced by the fix design: CADD's INTO is the
averaging window itself (08:00-16:00 ET, 480 min) and it has no AFTER60 (16:00-17:00 ET runs into the 17:00 NY
rollover); CADN's 15-minute leg exists only where M1 data exist (IS 2016-01..2017-04).

| cell | symbol, side | window (local) | eras |
|---|---|---|---|
| CADN-I | USDCAD long | 10:00-12:00 ET | PRE (H1) 2004-15, IS 2016-01-01..2017-04-28 |
| CADN-A15 | USDCAD short | 12:00-12:15 ET | IS 2016-01..2017-04 |
| CADN-A60 | USDCAD short | 12:00-13:00 ET | PRE (H1), IS 2016-01..2017-04 |
| CADD-I | USDCAD long | 08:00-16:00 ET | IS 2017-05-01..2021, VAL |
| CADD-A15 | USDCAD short | 16:00-16:15 ET | IS 2017-05..2021, VAL |
| AUD-I | AUDUSD short | 14:00-16:00 Sydney | PRE (H1), IS, VAL |
| AUD-A15 | AUDUSD long | 16:00-16:15 Sydney | IS, VAL |
| AUD-A60 | AUDUSD long | 16:00-17:00 Sydney | PRE (H1), IS, VAL |
| NZD-I | NZDUSD short | the 120 min into the fix in force: 09:10-11:10 NZ to 2015-04-30, 12:00-14:00 NZ from 2015-05-01; PRE H1 proxy 09:00-11:00 NZ (ends 10 min early) | PRE (H1), IS, VAL |
| NZD-A15 | NZDUSD long | fix to fix+15 | IS, VAL |
| NZD-A60 | NZDUSD long | fix to fix+60; PRE H1 proxy 11:00-12:00 NZ (contains the 11:10 fix) | PRE (H1), IS, VAL |
| GBP-I | GBPUSD short | 14:00-16:00 London | PRE (H1), IS, VAL |
| GBP-A15 | GBPUSD long | 16:00-16:15 London | IS, VAL |
| GBP-A60 | GBPUSD long | 16:00-17:00 London | PRE (H1), IS, VAL |
| CHF-I | USDCHF long | 09:00-11:00 Zurich | PRE (M1), IS, VAL |
| CHF-A15 | USDCHF short | 11:00-11:15 Zurich | PRE (M1), IS, VAL |
| CHF-A60 | USDCHF short | 11:00-12:00 Zurich | PRE (M1), IS, VAL |
| CNHT-I | USDCNH long | 09:00-11:00 Hong Kong (01:00-03:00 UTC) | IS, VAL |
| CNHT-A15 | USDCNH short | 11:00-11:15 Hong Kong | IS, VAL |
| CNHT-A60 | USDCNH short | 11:00-12:00 Hong Kong | IS, VAL |
| CNHC-I | USDCNH long | 14:30-16:30 Beijing (06:30-08:30 UTC) | IS, VAL |
| CNHC-A15 | USDCNH short | 16:30-16:45 Beijing | IS, VAL |
| CNHC-A60 | USDCNH short | 16:30-17:30 Beijing | IS, VAL |

CADN cannot meet a bar (no VAL); it is a mechanism check, with a declared prediction: **CADN-I on 2017-05..2024 (after
the noon rate stopped) is smaller than on 2004-2017-04**. The same prediction for the NZ 11:10 window after 2015-04 and
the NZ 14:00 window before 2015-05 (information cells, not counted). Variants per hypothesis: 2-3 lengths, counted
above. No other window, side or day set will be computed as a candidate.

## Rules common to every cell
- Days: Monday-Friday by the fix's local date; that country's holidays removed (holidays.json from round 12:
  CA-ON, AU-NSW, NZ-WGN, GB-ENG, CH-ZH; CN and HK from the `holidays` 0.105 package, written to a JSON in my folder);
  24 Dec - 1 Jan removed (as E1).
- Quotes: the price at time m is the close of the last M1 bar labelled m-1 (bar-start labels), at most 10 minutes
  stale, else no trade (as E1); H1 bars: the close at the bar's end. PRE uses the Dukascopy bid; IS/VAL the panel mid;
  USDCNH the IC bid (bid-only).
- Cost: IS/VAL half the actual spread at the entry minute + half at the exit minute + 0.6 bp commission; PRE IC's
  2016-17 mean spread by New York minute of day (stream M's profile) + 0.6 bp; USDCNH round 7's published 2.93 pips
  (spread / price) + 0.6 bp. Windows that cross 17:00 New York (some NZD cells) also pay one night's swap
  (`research/swing/rates.py` swap_frac_at, x3 on Wednesdays) where its rate series cover the date; otherwise say so.
- Stats: mean bp per trade at mid and net, t clustered by day (one trade a day: plain t), by era and year, VAL/IS;
  spread x1.5; both fills +1 minute (M1 data only); per-trade net Sharpe and power = Sharpe x sqrt(1.73 x trades per
  year) on the IS and on the VAL size (the latter = expected HOLD t).
- Random-entry control (look-ahead free; the side is fixed): on the same days, a window of the same length starting at
  a uniformly random minute of the home session (local 07:00 to 19:00 minus the length; whole hours for H1 PRE),
  redrawn if it touches 16:45-18:15 New York, same side, costs at its actual minutes; 200 seeds; share of seeds whose
  net mean is below the cell's (mid also reported).
- Holiday placebo (the TARGET2 check): the same window on that country's weekday holidays (fix not published),
  prediction INTO and AFTER means ~0 (or the reverse), smaller than on business days; t clustered by holiday block
  (dates within 4 days form one block); 2004-24 pooled where data exist, plus by era.
- Chance: 23 counted cells; max of 23 normals (95 % ~2.9); a per-date sign-flip permutation shared by all cells on IS
  mid t (500 draws).
- Bars (round 13 brief): LIVE = IS t >= 2.5, VAL t >= 1.5 (net, day-clustered), >= 2/3 of years net > 0, random
  control >= 95 %, power >= 3, > 0 at x1.5 and +1 minute. DEMO = IS t >= 2.0, VAL net > 0, random >= 90 %. A cell that
  meets either gets the C3 correlation (IS + VAL daily and monthly) and a PREREG_DRAFT_H_<name>.md with the expected
  HOLD t on the VAL size; its family then stops.

## Post hoc additions
- 03:24 UTC, after the numbers: the declared holiday placebo also reported as a difference (business-day mean minus
  holiday mean, block-clustered SE on the holiday side), `h2_placebo_diff.py`. Same days and windows; no new cell.
