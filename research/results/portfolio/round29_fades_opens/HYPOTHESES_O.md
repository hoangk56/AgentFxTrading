# Round 29, stream O: the direction of the first seconds at the Asian venue clocks round 27 left untested. Declared hypotheses

Written 2026-10-18 01:04 UTC (from `date -u`, 01:04:52; the count tables at the end appended at 01:06:20), before
any forward return, entry or exit price, spread or trade at any of the clocks below was computed. Brief:
[BRIEF.md](BRIEF.md) (stream O), round 13's brief (eras, costs, bars, multiple testing), round 26's brief (the
binding tick fill model), round 27's [HYPOTHESES_V.md](../round27_levels_opens/HYPOTHESES_V.md) and
[STREAM_V.md](../round27_levels_opens/STREAM_V.md) (the method reused here, unchanged except where a section below
says "adaptation").

What was looked at before this file:
- round 27 STREAM_V in full, including its shifted-clock readings at 01:30 UTC (CN-DAY plus 30 min) and 05:00 UTC
  (CN-PM minus 30 min) on its six-instrument Chinese pools (silver, platinum, oil, gold, AUD; net only, e.g. k 2 V1:
  -11.37 / -8.98 and -8.66 / -10.14 bp IS / VAL, cost-dominated), and its "Untested ideas" (the 23:00 / 00:00 UTC
  cluster seen in round 26 J's jump counts in AUD, NZD, gold and the US indices; counts only, never returns);
- earlier fixed-side results at these clocks, from the journal and round reports: round 4's AUD / NZD V around
  10:00 Sydney, round 6 S4, round 12 J, round 24 B (the Sydney V); round 15 V1's home-index fades at the TSE, HKEX
  and ASX cash opens (best HK50 gap fade IS t 1.69, VAL net -2.13); round 10 A's fixed-long cells after the Chinese
  opens (01:00 / 12:00 / 13:00 UTC);
- holiday listings from the `holidays` package 0.106 (XASX, XJPX, XHKG, XSHG, XKRX, 2016-2024); SGE's product page
  (night-session hours) and its 2024 holiday schedule (a CLS report of it and SGE's 2024-02-01 notice); an HKEX
  circular for the half-day rule; searches for SGE's 2020 night-session notices (not found);
- a counts-only tick pass (`pass_o.py --counts`): per clock, instrument and day, the size |m| of the opening move
  against its trailing norm, the day type and the exclusions. It calls only `opening_move()`; no entry, exit, spread
  or forward return exists in its output. Its counts are at the end of this file. No sign of any move was tabulated.

## Question
At the Asian venue clocks round 27 did not test (the ASX and TSE opens at 23:00 / 00:00 UTC, the A-share / HKEX
morning and afternoon opens, the SGE night-session start), does the price move of the first seconds, from T - 1 s to
T + w, predict the next 5-60 minutes in AUD, NZD, gold, silver or the US index CFDs, in either direction, after IC's
costs and the tick-level fill model?

## Mechanisms and expected sides
Both families are cells at every clock, as in round 27: **V1 follow** (the venue's participants bring information or
demand that other markets absorb gradually) and **V2 fade** (an opening liquidity gap: thin books make the first
trades overshoot and revert; Amihud & Mendelson 1987, Barclay & Hendershott 2003). Per clock:
- **ASX-OPEN, TSE-OPEN, ASX+TSE: no prior.** None of the instruments is the venue's own asset. The venue's index
  futures trade before the cash open (SPI 200 from 09:50 Sydney, Nikkei 225 at OSE from 08:45 JST), so the cash open
  is not where Australian or Japanese equity risk starts trading. The studies of Tokyo-New York transmission (Hamao,
  Masulis & Ng 1990; Lin, Engle & Ito 1994; from memory, not fetched) concern whole sessions, not the first seconds.
  A fixed post-10:00 Sydney rise in AUD / NZD (round 4's V) is a fixed-side drift, not a prediction from the opening
  move; it is read in the direction split below.
- **CNHK-AM: no prior; information-only lean V1** for AUDUSD and the US indices: the A-share and HKEX continuous
  sessions start, and China-specific equity news reaches the China-linked currency. The call auctions (SSE 09:15-09:25,
  HKEX pre-opening 09:00-09:20) and the CNY fix (09:15) come first, so part of the information is already out.
- **CNHK-PM: no prior** (lunch-break news against a reopening liquidity gap).
- **SGE-NIGHT: no prior; information-only lean V1** for gold and silver (Chinese demand passed to London / COMEX
  prices by arbitrage), as round 27 leaned for the Chinese venue opens. Round 27 found the SHFE night open (21:00
  Beijing) mid-reverting in metals at k 2 (IS -2.06, VAL -3.00 bp, |t| <= 1.5), which argues against the lean.
- The leans are information only: they choose nothing.

## How this differs from the fixed-side tests of the same clocks
| earlier test | what it did | here |
|---|---|---|
| round 4 scan, round 6 S4, round 12 J, round 24 B (Sydney V) | AUD / NZD fall into 10:00 Sydney and rise after: fixed sides (short before, long after), limit buys at the dip, an off-rollover AUDUSD variant (registered, failed HOLD), Dukascopy 2004-15 | side from the first 15 / 60 s after 10:00 Sydney, on days the move is large against its own 60-day norm, filled on ticks; gold and US indices too |
| round 15 V1 (minute panel) | TSE 09:00 JST, HKEX 09:30 HKT and ASX 10:00 Sydney cash opens on the home index CFDs (JP225, HK50, AUS200): fade the overnight gap or the last 10 minutes | non-home instruments; side from the first seconds after the clock; ticks; venue-holiday placebos |
| round 10 A (minute panel) | long after the Chinese opens 01:00 / 12:00 / 13:00 UTC for 15-60 min (12:00 UTC = the SGE night open); SGE auctions; Asian fixes | conditional side; the A-share / HKEX opens and the Tokyo / Sydney opens as clocks of their own |
| round 27 V | 01:30 and 05:00 UTC only as shifted controls of CN-DAY / CN-PM on its Chinese pools | own clocks, norms, calendars, instruments and placebos |

## Data
- IC ticks (research/data/<SYM>/t1/YYYYMMDD.zticks, the research/ticks.py format) through my copy of round 27's
  loader: AUDUSD, NZDUSD, XAUUSD, XAGUSD, US30, USTEC, venue dates 2016-01-04..2024-12-31. **HOLD guard**: the loader
  asserts every requested day < 2025-01-01 and the file name < "20250101.zticks" before opening it, and every tick
  timestamp < 2025-01-01 00:00 UTC; the event list asserts every clock instant + 4 h < 2025-01-01. No file of 2025 or
  later is opened.
- Each UTC day d with events is processed on the ticks of [d - 4 h, d + 1 day + 4 h), from the files of d - 1, d and
  d + 1, loaded once each in day order (the bid / ask carry of the format is kept). Adaptation: round 27's clocks
  needed only d - 1 and d; 10:00 Sydney under AEDT is 23:00 UTC and needs d + 1.
- Timed calendar r25/shared/cal/ff_events_utc.csv (High / Medium rows; untimed rows as whole days), as round 27.
- Venue calendars (code/cal_o.py -> cal/venue_calendars_o.json): the `holidays` package 0.106 (the package round 27
  used): XASX, XJPX, XHKG, XSHG, XKRX. Additions: the TSE full-day halt of 2020-10-01 is dropped (neither OPEN nor
  placebo); HKEX half days (no afternoon session on the weekday eves of Lunar New Year, Christmas and New Year; 17 in
  2016-24); SGE night sessions by round 27's CN_night rule on XSHG (a trading weekday whose next weekday is a trading
  day; SGE: "no night trading session on the previous day before any public holidays"), with one correction from
  SGE's 2024 schedule (2024-02-09 was an SGE trading day without a night session, so 2024-02-08 had one) and round
  27's COVID window 2020-02-03..05-05 kept as SUSP because SGE's own 2020 notice was not found (whether SGE kept its
  night session then is unverified). Other years were not checked against SGE's notices. HKEX typhoon / rainstorm
  cancellations are not in the package; they change a CNHK day type only when SSE is shut the same day (not checked).

## Clocks (T, DST-aware)
| id | T (local) | UTC | venue facts | instruments | OPEN days | placebo days (HOL) |
|---|---|---|---|---|---|---|
| ASX-OPEN | 10:00 Australia/Sydney on ASX date D | 23:00 on D - 1 (AEDT, first Sunday of October to first Sunday of April) / 00:00 on D (AEST) | ASX cash open (alphabetical groups from 10:00:00); SPI futures already trade. In the northern winter 23:00 UTC is 18:00 New York (CME daily reopen, IC's post-rollover hour): those days fall under the rollover rule, so AEDT events exist only in EDT weeks (October, mid-March to early April) | AUDUSD, NZDUSD, XAUUSD, US30, USTEC | XASX trading weekdays | XASX holiday weekdays; under AEST only if TSE is also shut (else TSE opens at the same instant: dropped) |
| TSE-OPEN | 09:00 Asia/Tokyo | 00:00 | TSE opening auction; KRX also opens at 09:00 KST = 00:00 UTC (noted, not modelled) | same 5 | XJPX trading weekdays (2020-10-01 dropped) | XJPX holiday weekdays; under AEST only if ASX is also shut |
| ASX+TSE | 10:00 Sydney = 09:00 Tokyo (AEST only) | 00:00 | the coinciding days, one event; the same days are also in ASX-OPEN and TSE-OPEN | same 5 | AEST weekdays with ASX and TSE both open | both shut (none in 2016-24) |
| CNHK-AM | 09:30 Asia/Shanghai (= Hong Kong) | 01:30 | SSE / SZSE continuous trading start; HKEX morning continuous session start | AUDUSD, XAUUSD, US30, USTEC | SSE or HKEX open | SSE and HKEX both shut |
| CNHK-PM | 13:00 Beijing / Hong Kong | 05:00 | SSE and HKEX afternoon session start | same 4 | SSE open, or HKEX open and not a half day | SSE shut and HKEX shut or on a half day |
| SGE-NIGHT | 20:00 Asia/Shanghai | 12:00 | SGE night session 20:00-02:30 (pre-order matching 19:50-19:59); Friday's session belongs to Monday | XAUUSD, XAGUSD | night-session days, outside the 2020 window | weekdays without a night session (holiday or holiday eve); 2020-02-03..05-05 reported separately (SUSP) |
| TSE-PM (information only) | 12:30 Asia/Tokyo | 03:30 | TSE afternoon session start; also the SSE morning close | same 5 as TSE | XJPX trading weekdays | XJPX holiday weekdays |

Known confounds (written now): 00:00 UTC is also the KRX open, 5 minutes after Japanese releases at 23:50 UTC
(excluded through the JPY rows below) and 55 minutes before the Tokyo fix (C3's clock, inside h 60); 01:30 UTC is 15
minutes after the CNY fix and sits among Chinese and Australian releases (CNY / AUD rows); 05:00 UTC is 30 minutes
before round 27's CN-PM (13:30 Beijing); 12:00 UTC is 30 minutes before US releases in the northern summer (USD rows)
and an hour before round 27's CN-NIGHT; ASX Monday opens under AEDT are Sunday 23:00 UTC, two hours after IC's weekly
open.

## Definitions (round 27 V's, fixed)
- Mid m = (bid + ask) / 2; prevailing quote at t = the last tick with ts <= t.
- **Opening move** at clock T, window w: p0 = prevailing mid at T - 1 s, p1 = prevailing mid at T + w,
  m = (p1 - p0) / p0 x 1e4 bp, d = sign(m). The quote at T - 1 s must be at most 10 min old, else no event; m = 0 gives
  no event. **w in {15, 60} s.**
- **Trailing same-clock norm** N = median |m| over the most recent 60 clean OPEN days strictly before the event,
  same instrument, clock, shift variant and w; >= 20 such days and N > 0 needed for k > 0. Clean = valid m, no
  calendar exclusion in [T - 15 min, T + w + 2 min] and (**adaptation 1**) [T - 15 min, T + w + 2 min] does not touch
  16:55-18:10 New York. It matters only for ASX-OPEN under AEDT in the northern winter, whose opening move is the
  18:00 New York reopen and which the rollover rule never trades; round 27 had no clock near the rollover.
- **Event** at dose k: |m| >= k x N; **k in {0, 2, 4}** (k 0 = every valid day).
- **Sides**: V1 = d, V2 = -d.
- **Entry**: first tick with ts >= T + w + L, buy at its ASK, sell at its BID. **L = 250 ms decides**; L = 0,
  1,000 ms, "next tick" (the tick after the L0 entry tick) and "+1 minute" (L = 60 s) are reported.
- **Exit**: first tick with ts >= entry target + h, long at the BID, short at the ASK. **h in {5, 15, 60} min.**
- **Protective-stop variant** S: server-side stop at s = max(|m|, 2 x the entry tick's spread in bp) from the entry
  mid, triggered by the first later tick up to the exit tick with BID <= level (long) / ASK >= level (short), filled
  there.
- **Costs**: actual tick spreads; commission 0.6 bp round trip for AUDUSD, NZDUSD, XAUUSD, XAGUSD; 0 for US30, USTEC.
  Net = side x (exit fill - entry fill) / entry mid x 1e4 - commission; mid = side x (exit mid - entry mid) / entry
  mid x 1e4; spread paid = mid - net - commission; spread x1.5 = net - 0.5 x spread paid.
- **Calendar exclusions** (per event and h): High / Medium timed rows of the instrument's set in [T - 15 min,
  T + w + h + 2 min]. Sets (round 27): AUDUSD {AUD, NZD, CNY, USD, All}; NZDUSD {NZD, AUD, CNY, USD, All}; XAUUSD,
  XAGUSD {USD, CNY, All}; US30, USTEC {USD, All}. **Adaptation 2**, as round 27 added EUR and GBP at EU-OPEN: every
  instrument adds the venue currencies, AUD and JPY at ASX-OPEN, TSE-OPEN, ASX+TSE and TSE-PM, CNY at CNHK-AM, CNHK-PM
  and SGE-NIGHT. Also round 27's central-bank windows [T_cb - 30 min, T_cb + 120 min] (USD, EUR, GBP, AUD, NZD, CAD,
  CHF), the BOJ window 01:30-07:30 UTC on BOJ days, untimed High / Medium rows of the set as whole UTC days, and
  election / referendum / vote rows (that UTC day and the next).
- **Rollover**: no trade whose window [T - 1 s, T + w + 60 s + h] touches 16:55-18:10 New York.
- **Day, era, year**: the UTC day of the clock instant (t clustered by UTC day; IS 2016-21, VAL 2022-24). The venue
  date is kept for the calendar splits.

## Cells (counted)
| clock | singles | pools | sets |
|---|---|---|---|
| ASX-OPEN | AUDUSD, NZDUSD, XAUUSD, US30, USTEC | FX {AUD, NZD}, INDICES {US30, USTEC}, ALL {5} | 8 |
| TSE-OPEN | same | same | 8 |
| ASX+TSE | same | same | 8 |
| CNHK-AM | AUDUSD, XAUUSD, US30, USTEC | INDICES {US30, USTEC}, ALL {4} | 6 |
| CNHK-PM | same | same | 6 |
| SGE-NIGHT | XAUUSD, XAGUSD | ALL {XAU, XAG} | 3 |
| TSE-PM (information only, not counted) | AUDUSD, NZDUSD, XAUUSD, US30, USTEC | FX, INDICES, ALL | (8) |

Per set: family {V1, V2} x w {15, 60 s} x k {0, 2, 4} x h {5, 15, 60 min} x stop {none, S} = 72 cells. 39 counted sets
= **2,808 counted cells**. TSE-PM's 576 cells are information only: no verdict, not in the chance benchmark. Each
cell is decided at L = 250 ms on OPEN days at the clock itself; latencies, x1.5 and the controls are readings of the
same cell.

**Primary cells (24):** the ALL set of ASX-OPEN, TSE-OPEN, ASX+TSE, CNHK-AM, CNHK-PM and SGE-NIGHT; w 15 s,
h 15 min, no stop, k in {2, 4}, V1 and V2.

## Controls (every cell; round 27's)
- **Venue-shut placebo**: the same rule (thresholds from the same trailing OPEN-day norm) on the placebo days above;
  t clustered by holiday block (consecutive placebo days <= 4 calendar days apart); OPEN minus placebo with its t.
  The ASX placebo days are few (Good Fridays / Easter Mondays in EDT weeks; the AEDT Christmas / New Year days fall
  under the rollover rule) and ASX+TSE has none.
- **Shifted clocks**: the whole rule at T - 30 and T + 30 min on the OPEN days (own norms, sides, exclusions). Known
  confounds: CNHK-AM - 30 = 01:00 UTC is round 27's CN-DAY (SHFE / SGE day open); CNHK-PM + 30 = 05:30 UTC is CN-PM;
  SGE-NIGHT + 30 = 12:30 UTC, US releases in summer (excluded on release days); ASX-OPEN under AEDT - 30 = 22:30 UTC.
- **Random direction** RD: the cell's events with a random side per event, 500 seeds; share of seeds the cell beats.
- **Random time** RT (the bar's random-entry control): per event 200 random whole seconds T' in [T - 150, T - 35] U
  [T + 35, T + 150] min (from 800 candidates), quote at T' - 1 s <= 10 min old, no calendar exclusion in [T' - 15 min,
  T' + 62 min], the rollover rule for h = 60; side from the move T' - 1 s -> T' + w (V1 its sign, V2 minus), no
  magnitude filter; L = 250 ms, same h and stop rule. Share of seeds the cell beats (IS, VAL, all).

## Statistics (round 27's)
- Per cell: n IS / VAL; mid and net bp per event at each latency; t clustered by UTC day; by year; VAL / IS; spread
  paid; stop-hit share; per-trade and per-day Sharpe; power = Sharpe x sqrt(1.73 x events (event days) per year) at
  the IS and the VAL size (IS spans 6 years, VAL 3; a pool's rate is the sum of its instruments').
- Chance: (i) the 95 % max |t| of K independent normals, K = counted cells with >= 10 IS events; (ii) a per-UTC-day
  sign flip of the opening-move direction (one flip per day shared by every instrument, clock and cell, swapping V1
  and V2), 1,000 draws, for the max IS net t over the counted cells and over the 24 primary cells, and the same for
  the max |IS mid t| (no-stop V1 cells).
- Information only (no cell, no bar):
  - ASX-OPEN by Sydney season: AEDT (23:00 UTC, ASX alone) vs AEST (00:00 UTC);
  - TSE-OPEN by Sydney season: AEDT (TSE alone, an hour after ASX) vs AEST;
  - ASX-OPEN Monday opens under AEDT (Sunday 23:00 UTC) vs the other days;
  - the TSE-OPEN placebo split by KRX open / shut;
  - CNHK-AM / PM by venue status: both open, SSE only (HKEX holiday), HKEX only (Chinese holiday); and CNHK-AM on the
    first SSE trading day after a Chinese holiday;
  - SGE-NIGHT on the 2020 SUSP days, and by New York season (12:00 UTC = 07:00 EST / 08:00 EDT);
  - each family's events split by the sign of the opening move (long legs vs short legs), to separate a fixed drift
    such as the Sydney V from a conditional one;
  - ex March-April 2020 and IS-winsorised (1 / 99 %) readings;
  - all of TSE-PM.
- **V0 clock check (no returns)**: per clock and instrument, tick counts and unsigned mean |change of mid| per 5 s
  from T - 60 s to T + 120 s, OPEN vs placebo days (and SUSP for SGE-NIGHT), IS only; ASX-OPEN also by season. A
  check that each clock exists in IC's feed; no cell is added, dropped or changed because of it.

## Bars (round 13's, as round 27 applied them; not lowered)
- **LIVE**: IS day-clustered net t >= 2.5, VAL net t >= 1.5; net > 0 in IS and VAL; >= 2/3 of years with events net
  > 0; > 0 at spread x1.5 and at +1 minute in IS and VAL; beats >= 95 % of RT in IS and VAL; power >= 3 at the VAL
  size.
- **DEMO**: IS net t >= 2.0, net > 0 in VAL, beats >= 90 % of RT (IS), > 0 at spread x1.5 and +1 minute.
- A cell whose IS net t is within the sign-flip null's 95 % max is labelled "within chance"; one whose venue-shut
  placebo or shifted clock does as well, "not venue-specific".
- **PREREG_DRAFT_O_* only for a rule that meets the LIVE or DEMO numbers on IS / VAL and beats the multiple-testing
  null** (IS net t above the null's 95 % max). It would carry the rule, parameters, cell count, expected HOLD events
  and expected HOLD t at the VAL size and at 0.65 of it, and its daily P&L correlation with C3
  (trades_C3_gotobi_jpy_basket.csv, IS + VAL rows). HOLD is not opened.

## Prior (written now)
Opening moves here are probably 0.5-1.5 bp in FX and gold and 1-3 bp in the US index CFDs; none of the instruments
is the venue's own asset except gold and silver at SGE-NIGHT. IC's round trip at these hours is ~0.8-1.2 bp in FX
(0.6 of it commission), ~1.3-1.6 bp in gold, 3-5 bp in silver and 1-3 bp in the index CFDs. A 10-30 % continuation or
reversal of the opening move is 0.1-1 bp. Prior chance of a LIVE pass: ~1 %; of DEMO numbers somewhere: ~20 %, most
likely within chance (round 27: 2 of 3,924 cells, both within chance).

## Event counts (counts-only pass: opening-move sizes, norms, day types, exclusions; no returns)
### Events per year at the primary spec (w 15 s, exclusions of h 15 min): k0 / k2 / k4

k0 = OPEN days with a valid opening move and no exclusion; k2 / k4 also need |m| >= k x the trailing 60-day median. UTC year of the clock instant.

| clock | instrument | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | IS | VAL | placebo days (valid, all years) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN | AUDUSD | 119/16/4 | 113/25/6 | 134/28/3 | 126/26/3 | 139/37/16 | 135/35/5 | 123/38/10 | 138/16/0 | 132/20/4 | 766/167/37 | 393/74/14 | HOL 26 |
| ASX-OPEN | NZDUSD | 114/29/9 | 114/28/6 | 130/36/17 | 120/25/3 | 131/39/14 | 133/21/6 | 122/30/3 | 136/22/3 | 139/20/7 | 742/178/55 | 397/72/13 | HOL 25 |
| ASX-OPEN | XAUUSD | 115/19/6 | 119/22/5 | 130/28/3 | 127/39/8 | 139/33/12 | 135/37/7 | 122/37/6 | 135/25/10 | 138/27/9 | 765/178/41 | 395/89/25 | HOL 1 |
| ASX-OPEN | US30 | 106/12/1 | 81/12/4 | 122/31/9 | 123/34/14 | 134/39/18 | 134/23/3 | 117/36/9 | 129/17/2 | 131/24/5 | 700/151/49 | 377/77/16 | HOL 2 |
| ASX-OPEN | USTEC | 110/21/3 | 91/14/4 | 126/40/13 | 127/27/9 | 134/40/20 | 138/34/7 | 123/33/11 | 133/19/2 | 134/39/11 | 726/176/56 | 390/91/24 | HOL 2 |
| TSE-OPEN | AUDUSD | 162/42/17 | 157/38/11 | 186/41/9 | 176/52/9 | 188/53/21 | 193/40/7 | 172/50/14 | 197/18/2 | 177/28/6 | 1062/266/74 | 546/96/22 | HOL 67 |
| TSE-OPEN | NZDUSD | 157/38/5 | 162/27/5 | 183/44/11 | 170/56/12 | 181/48/11 | 194/42/10 | 174/46/10 | 199/26/4 | 190/39/4 | 1047/255/54 | 563/111/18 | HOL 69 |
| TSE-OPEN | XAUUSD | 162/30/8 | 170/26/4 | 196/37/4 | 178/41/2 | 191/57/24 | 198/44/7 | 175/53/9 | 202/49/12 | 191/41/13 | 1095/235/49 | 568/143/34 | HOL 70 |
| TSE-OPEN | US30 | 146/25/4 | 130/19/6 | 185/52/18 | 175/31/4 | 189/52/21 | 194/43/7 | 173/39/4 | 188/31/3 | 182/40/9 | 1019/222/60 | 543/110/16 | HOL 64 |
| TSE-OPEN | USTEC | 151/28/3 | 142/20/6 | 187/61/19 | 182/34/8 | 192/54/20 | 199/57/15 | 174/45/3 | 201/36/5 | 182/59/17 | 1053/254/71 | 557/140/25 | HOL 61 |
| ASX+TSE | AUDUSD | 78/11/4 | 79/20/6 | 103/13/1 | 94/20/3 | 96/30/15 | 96/24/3 | 81/22/2 | 98/8/0 | 95/13/1 | 546/118/32 | 274/43/3 | HOL 0 |
| ASX+TSE | NZDUSD | 77/23/7 | 77/15/3 | 99/18/3 | 90/19/3 | 91/30/13 | 95/17/5 | 79/17/0 | 93/13/1 | 100/12/1 | 529/122/34 | 272/42/2 | HOL 0 |
| ASX+TSE | XAUUSD | 78/8/1 | 80/13/1 | 106/14/1 | 96/24/2 | 96/23/8 | 96/19/3 | 80/23/6 | 95/19/3 | 101/25/9 | 552/101/16 | 276/67/18 | HOL 0 |
| ASX+TSE | US30 | 77/10/1 | 63/9/3 | 99/27/7 | 96/27/5 | 96/30/13 | 94/11/0 | 79/26/9 | 89/12/2 | 96/22/5 | 525/114/29 | 264/60/16 | HOL 0 |
| ASX+TSE | USTEC | 77/13/2 | 70/8/4 | 102/27/7 | 95/28/12 | 97/29/10 | 97/16/0 | 80/32/17 | 97/14/1 | 97/34/9 | 538/121/35 | 274/80/27 | HOL 0 |
| CNHK-AM | AUDUSD | 148/23/5 | 141/41/6 | 144/34/12 | 128/28/9 | 156/38/17 | 177/27/2 | 159/41/8 | 150/30/7 | 155/16/2 | 894/191/51 | 464/87/17 | HOL 53 |
| CNHK-AM | XAUUSD | 180/34/5 | 175/32/3 | 191/47/8 | 165/44/16 | 189/47/9 | 200/32/7 | 179/51/14 | 179/46/9 | 185/41/8 | 1100/236/48 | 543/138/31 | HOL 59 |
| CNHK-AM | US30 | 167/23/3 | 134/18/3 | 180/50/15 | 166/28/6 | 182/51/19 | 199/38/10 | 174/30/5 | 166/27/3 | 171/27/6 | 1028/208/56 | 511/84/14 | HOL 51 |
| CNHK-AM | USTEC | 160/22/2 | 132/21/4 | 190/53/20 | 165/22/6 | 186/49/17 | 200/36/11 | 183/43/7 | 176/32/7 | 185/41/10 | 1033/203/60 | 544/116/24 | HOL 56 |
| CNHK-PM | AUDUSD | 197/38/7 | 175/44/17 | 185/49/15 | 184/43/4 | 198/46/16 | 197/43/8 | 187/51/9 | 197/29/0 | 179/26/3 | 1136/263/67 | 563/106/12 | HOL 66 |
| CNHK-PM | XAUUSD | 195/30/1 | 183/43/14 | 191/47/13 | 182/51/16 | 205/68/21 | 204/48/10 | 187/39/12 | 197/33/5 | 202/54/9 | 1160/287/75 | 586/126/26 | HOL 66 |
| CNHK-PM | US30 | 163/17/0 | 101/4/0 | 179/49/15 | 172/31/10 | 199/59/25 | 203/39/7 | 182/37/12 | 182/22/3 | 186/39/7 | 1017/199/57 | 550/98/22 | HOL 49 |
| CNHK-PM | USTEC | 158/9/0 | 136/14/1 | 190/56/20 | 183/33/10 | 199/56/24 | 209/54/16 | 191/59/20 | 197/30/4 | 195/37/9 | 1075/222/71 | 583/126/33 | HOL 56 |
| SGE-NIGHT | XAUUSD | 184/38/5 | 172/29/6 | 182/38/5 | 174/53/11 | 144/40/13 | 192/22/1 | 177/40/14 | 192/30/4 | 183/43/11 | 1048/220/41 | 552/113/29 | HOL 205; 2020 SUSP 66 |
| SGE-NIGHT | XAGUSD | 163/24/3 | 157/23/7 | 156/16/2 | 171/53/8 | 140/46/22 | 191/32/5 | 170/40/4 | 186/42/11 | 178/39/3 | 978/194/47 | 534/121/18 | HOL 182; 2020 SUSP 65 |
| TSE-PM | AUDUSD | 191/37/9 | 171/48/16 | 180/42/8 | 161/37/9 | 181/52/15 | 189/44/11 | 183/51/9 | 182/38/4 | 172/36/9 | 1073/260/68 | 537/125/22 | HOL 121 |
| TSE-PM | NZDUSD | 190/45/14 | 176/54/27 | 184/55/23 | 156/46/20 | 185/58/19 | 184/54/19 | 177/50/9 | 195/47/6 | 182/42/12 | 1075/312/122 | 554/139/27 | HOL 128 |
| TSE-PM | XAUUSD | 187/25/6 | 178/44/11 | 182/38/6 | 179/55/13 | 193/52/22 | 194/39/8 | 180/40/11 | 197/44/7 | 197/30/6 | 1113/253/66 | 574/114/24 | HOL 132 |
| TSE-PM | US30 | 177/27/6 | 141/12/0 | 183/47/11 | 168/30/6 | 190/47/22 | 185/40/8 | 170/45/13 | 168/22/5 | 167/39/6 | 1044/203/53 | 505/106/24 | HOL 113 |
| TSE-PM | USTEC | 172/11/0 | 150/18/0 | 189/56/16 | 177/32/6 | 194/48/18 | 196/46/9 | 179/50/17 | 187/32/6 | 186/49/12 | 1078/211/49 | 552/131/35 | HOL 121 |

### Calendar days per year (weekday venue dates; before any quote check)

| clock | day type | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|---|
| ASX-OPEN | OPEN | 253 | 252 | 253 | 253 | 255 | 254 | 251 | 252 | 254 |
| ASX-OPEN | placebo (HOL) | 5 | 4 | 5 | 4 | 4 | 5 | 4 | 4 | 6 |
| TSE-OPEN | OPEN | 245 | 247 | 245 | 241 | 242 | 245 | 244 | 246 | 245 |
| TSE-OPEN | placebo (HOL) | 7 | 7 | 10 | 10 | 10 | 7 | 8 | 8 | 10 |
| ASX+TSE | OPEN | 120 | 120 | 126 | 116 | 117 | 119 | 117 | 120 | 121 |
| CNHK-AM | OPEN | 253 | 252 | 254 | 252 | 255 | 255 | 252 | 252 | 255 |
| CNHK-AM | placebo (HOL) | 7 | 8 | 7 | 9 | 7 | 6 | 8 | 8 | 7 |
| CNHK-PM | OPEN | 253 | 251 | 252 | 251 | 254 | 254 | 251 | 252 | 254 |
| CNHK-PM | placebo (HOL) | 7 | 9 | 9 | 10 | 8 | 7 | 9 | 8 | 8 |
| SGE-NIGHT | OPEN | 237 | 238 | 236 | 237 | 176 | 236 | 235 | 236 | 236 |
| SGE-NIGHT | placebo (HOL) | 23 | 22 | 25 | 24 | 19 | 25 | 25 | 24 | 26 |
| SGE-NIGHT | SUSP | 0 | 0 | 0 | 0 | 67 | 0 | 0 | 0 | 0 |
| TSE-PM | OPEN | 245 | 247 | 245 | 241 | 242 | 245 | 244 | 246 | 245 |
| TSE-PM | placebo (HOL) | 15 | 13 | 16 | 20 | 19 | 16 | 16 | 14 | 17 |

### ASX-OPEN events by season (w 15 s, h 15 exclusions, k0, all instruments summed, IS / VAL)

| season | UTC clock | IS | VAL |
|---|---|---|---|
| AEDT (23:00 UTC) | 23:00 UTC | 799 | 503 |
| AEST (00:00 UTC) | 00:00 UTC | 2900 | 1449 |

### Totals at w 60 s (h 15 exclusions): k0 / k2 / k4, IS | VAL

| clock | instrument | IS | VAL |
|---|---|---|---|
| ASX-OPEN | AUDUSD | 776/153/28 | 400/82/20 |
| ASX-OPEN | NZDUSD | 784/170/40 | 399/94/15 |
| ASX-OPEN | XAUUSD | 774/169/40 | 400/89/31 |
| ASX-OPEN | US30 | 734/184/50 | 392/68/9 |
| ASX-OPEN | USTEC | 743/179/52 | 404/91/20 |
| TSE-OPEN | AUDUSD | 1083/207/30 | 565/111/21 |
| TSE-OPEN | NZDUSD | 1081/208/35 | 572/124/19 |
| TSE-OPEN | XAUUSD | 1107/229/54 | 575/127/36 |
| TSE-OPEN | US30 | 1058/235/64 | 559/106/19 |
| TSE-OPEN | USTEC | 1066/224/61 | 570/103/23 |
| ASX+TSE | AUDUSD | 551/106/19 | 277/50/12 |
| ASX+TSE | NZDUSD | 555/122/28 | 279/58/6 |
| ASX+TSE | XAUUSD | 560/120/22 | 280/66/21 |
| ASX+TSE | US30 | 540/123/32 | 273/48/7 |
| ASX+TSE | USTEC | 543/115/35 | 281/73/22 |
| CNHK-AM | AUDUSD | 915/171/31 | 484/87/13 |
| CNHK-AM | XAUUSD | 1120/223/46 | 555/124/26 |
| CNHK-AM | US30 | 1068/212/48 | 530/102/12 |
| CNHK-AM | USTEC | 1066/202/33 | 552/118/22 |
| CNHK-PM | AUDUSD | 1184/246/52 | 590/108/19 |
| CNHK-PM | XAUUSD | 1197/265/47 | 605/133/24 |
| CNHK-PM | US30 | 1099/217/62 | 557/94/16 |
| CNHK-PM | USTEC | 1136/231/63 | 584/119/34 |
| SGE-NIGHT | XAUUSD | 1065/225/38 | 557/118/23 |
| SGE-NIGHT | XAGUSD | 1030/213/35 | 550/105/16 |
| TSE-PM | AUDUSD | 1146/243/36 | 568/117/13 |
| TSE-PM | NZDUSD | 1146/274/54 | 577/103/9 |
| TSE-PM | XAUUSD | 1162/225/47 | 581/122/22 |
| TSE-PM | US30 | 1089/226/70 | 547/100/25 |
| TSE-PM | USTEC | 1109/253/85 | 574/117/32 |

Placebo days count valid moves before the rollover and calendar exclusions; ASX-OPEN AEDT placebo days in the northern winter
are later removed by the rollover rule. Counts at h 5 / h 60 differ only through the exclusion window.

## Additions after numbers
(anything added below this line after a return was seen is information only, unless it says otherwise)

### Addendum 1, 2026-10-18 01:18 UTC (from `date -u`), written after all 3,384 cells were computed
Seen by now: every declared cell, the controls, the chance benchmark, the V0 check and the declared information-only
splits. No counted cell meets the LIVE or the DEMO numbers, so no PREREG_DRAFT_O is written and no PRE check is run.
Added after the numbers, information only (no cell, no bar, nothing re-chosen):
- a table of every set at the primary spec and a list of all cells with IS net t >= 1.5 (round 27 listed >= 2.0);
  both are views of the declared cells;
- an independent recomputation of 540 sampled event exits from research/ticks.py (0 mismatches);
- a fix to the clustering of the TSE-holiday placebo split (holiday blocks over the selected placebo days, round 27's
  rule; the first run grouped all days into one block).
- an unsigned V0 split of AUDUSD at CNHK-AM by Sydney season (01:19 UTC), to read the 01:30 UTC activity spike
  (Australian releases at 11:30 AEST).
