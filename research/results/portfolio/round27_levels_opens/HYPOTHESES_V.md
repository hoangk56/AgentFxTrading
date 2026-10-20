# Round 27, stream V: the direction of venue-open jumps. Declared hypotheses

Written 2026-10-17 21:23 UTC (from `date -u`, 21:22:58), before any opening move, forward return or spread at any
of the clocks below was computed. Brief: [BRIEF.md](BRIEF.md) (row V), round 13's brief (eras, costs, bars) and round
26's brief (the binding tick fill model).

What was looked at before this file (no price, no return, no opening move in any of it):
- round 26 J's count-based clock flags (`r26/J/out/e10_flags.txt`: jump counts per UTC minute and instrument-season,
  IS only, counts only);
- holiday listings from the `holidays` package 0.106 (XSHG, XLON, XETR, XNZE, XNYS, XCME, IFEU, 2016/2020/2024
  dates only);
- tick rows per day for six symbols on 2019-03-12..14 (decode speed; no price read);
- the CNY rows of the timed calendar (event names, impact, UTC minute; no price).

## Question
At a fixed venue clock T (an exchange open, the CNY fixing, the New York closing-imbalance publication, a
settlement window), does the price move of the first seconds, from T-1 s to T+w, predict the next 5-60 minutes,
in either direction, after IC's costs and a tick-level fill model?

## Mechanisms and sides (both families declared; side comes from the market's own opening move)
- **V1 follow** (trade in the direction of the opening move). The new venue's participants carry information or
  demand that the other markets absorb gradually: Chinese demand at the SHFE / SGE / INE opens passed to London /
  COMEX prices by arbitrage; the CNY central parity as a policy signal; the NYSE / Nasdaq closing imbalance, which
  executes only at 16:00 ET; price discovery at the European cash open. Sources (from memory, not fetched):
  Barclay & Hendershott (2003, RFS) on price discovery around opens; Fung, Leung & Xu (2003) and Liu & An (2011) on
  US-China commodity futures information transmission; the Essex / Nottingham paper on SHFE night trading and price
  discovery in precious metals (repository.essex.ac.uk/27740); Bogousslavsky & Muravyev (2023) on closing-auction
  imbalances and price pressure into the close.
- **V2 fade** (trade against it). An opening liquidity gap: thin books when a venue starts make the first trades
  overshoot, and the overshoot reverts (Amihud & Mendelson 1987; Barclay & Hendershott 2003). The 07:00 New Zealand
  minute is a documented NZD liquidity drought (Darwinex pauses NZD pairs 07:00-07:01 NZ for that reason; FX News
  Group article "Darwinex to introduce NZD daily trading breaks"); settlement-window pressure (trade-at-settlement,
  benchmarked orders) is temporary (the mechanism round 15 V6 declared).
- Literature-leaning side, information only (both families are tested and counted for every clock): follow at
  CN-DAY, CN-PM, CN-NIGHT, CNY-FIX, EU-OPEN, NY-IMB; fade at NZ-07 and SETTLE.

## How this differs from the fixed-side tests of the same venues
| earlier test | what it did | here |
|---|---|---|
| round 10 A1 / A2 / A4 / A5 (minute panel) | A2-flow: long after the Chinese opens 01:00 / 12:00 / 13:00 UTC for 15-60 min (side fixed: China net buyer); A2-cont: side = the move made while the venue was shut (hours before T); A2-close: fade the 30 min before the closes; A1: SGE auction V; A4: Asian FX fixes with fixed USD sides; the CNY 09:15 fix was a round-4 fixed-side cell | side = sign of the move from T-1 s to T+15 s / T+60 s, only on days when that move is large against the same clock's own trailing 60-day median; entry on ticks at T+w+latency at the actual bid / ask |
| round 15 V (minute panel) | 1-10 min windows at 24 benchmarks (cash opens incl. LSE 08:00 / Xetra 09:00 CET, NYSE 09:30, COMEX / NYMEX floor opens, WTI settlement 14:30 ET, LBMA), rules U (long), M (sign of the 10 minutes before entry), G (gap since the previous cash close); 15:50-15:59 ET M+ was information only | the conditioning move is the first 15 / 60 s after the clock (never the 10 minutes before it), with a magnitude filter against the clock's own history; clocks round 15 did not have: CN-DAY, CN-PM, CN-NIGHT, CNY-FIX, NZ-07, NY-IMB as an event, the gold / silver / gas / Brent settlement windows |
| round 24 B (Dukascopy + IC minute panel) | fixed-side rules: China-session gold long 01:00-03:30 UTC (A10), China-close fade of the previous 30 min (A11), COMEX open fade of the previous 10 min (A9), SGE placebo (A12) | as above: conditional side from the clock's own first seconds, tick fills |
| settlement minutes: round 6 (settlement momentum), round 12 L / 13 P / 24 B A4 (side = the day's move, into the settlement), round 15 V6 (WTI, side from the 10 min before / after 14:30) | **already tested as fixed-side / pre-window-conditioned flows** | side from the first w seconds of the settlement window itself |

## Data
- IC ticks via my own copy of the round-26 day loader (`research/ticks.py` format; the previous UTC day is loaded
  for look-backs and carried bid / ask). **Every requested day is asserted < 2025-01-01; HOLD is never loaded.**
  AUDUSD, NZDUSD, XAUUSD, XAGUSD, XPTUSD, US30, USTEC 2016-01-04..2024-12-31; XTIUSD, XBRUSD, XNGUSD
  2018-01-02..2024-12-31 (at the Chinese clocks oil starts 2018-03-26, the INE crude launch).
- Minute panel (r25/shared/panel, bar-start labels) for DE40 and UK100 at the European open (minute level,
  labelled).
- Timed calendar r25/shared/cal/ff_events_utc.csv (High / Medium rows with a time; untimed rows as whole days).
- Venue calendars (built from the `holidays` package, written to JSON in r27/V/cal and copied to r25/shared/cal):
  XSHG for the Chinese venues (SHFE, INE, SGE, CFETS follow the State Council schedule), XLON, XETR, XNZE (NZX,
  national holidays), XNYS (+ hard-coded NYSE 13:00 early closes), XCME, IFEU.

## Clocks (T, DST-aware, sources, history)
| id | T | UTC | source / history | tick instruments | OPEN days | placebo days |
|---|---|---|---|---|---|---|
| CN-DAY | 09:00 Asia/Shanghai | 01:00 | SHFE / INE day session 09:00-10:15, 10:30-11:30, 13:30-15:00; SGE day session 09:00-15:30 (en.sge.com.cn); INE crude from 2018-03-26 | XAUUSD, XAGUSD, XPTUSD, AUDUSD; XTIUSD, XBRUSD from 2018-03-26 | XSHG trading weekdays | XSHG holiday weekdays (HOL) |
| CN-PM | 13:30 Asia/Shanghai | 05:30 | SHFE / INE afternoon reopen after 11:30-13:30 | as CN-DAY | as CN-DAY | as CN-DAY |
| CN-NIGHT | 21:00 Asia/Shanghai | 13:00 | SHFE / INE night session start (gold, silver, crude 21:00-02:30; base metals 21:00-01:00; DCE iron ore night), since 2013-07-05 for gold / silver; no night session on the last trading day before a holiday; suspended 2020-02-03..2020-05-05, resumed the evening of 2020-05-06 (SHFE notice reported by SMM / Yicai) | XAUUSD, XAGUSD, AUDUSD; XTIUSD, XBRUSD from 2018-03-26 | XSHG trading weekdays whose next weekday is a trading day, outside the 2020 suspension | weekdays without a night session because of a holiday or a holiday eve (HOL); the 2020 suspension days are reported separately, not as HOL |
| CNY-FIX | 09:15 Asia/Shanghai | 01:15 | CFETS USD/CNY central parity, published 09:15 Beijing each interbank business day (chinamoney.com.cn) | AUDUSD, NZDUSD, XAUUSD | XSHG trading weekdays | XSHG holiday weekdays (HOL) |
| EU-OPEN | 08:00 Europe/London = 09:00 Europe/Berlin (one instant) | 08:00 GMT / 07:00 BST | LSE continuous trading 08:00 London; Xetra opening auction 09:00 CET | US30, USTEC, XAUUSD, AUDUSD, NZDUSD (cross-checks); DE40, UK100 at minute level | cross-checks: LSE and Xetra both open; DE40: Xetra open; UK100: LSE open | cross-checks: both closed; DE40: Xetra closed; UK100: LSE closed (HOL) |
| NZ-07 | 07:00 Pacific/Auckland on NZ date D' | 19:00 (NZST) / 18:00 (NZDT) on UTC date D'-1 | NZD dealing-day start; documented NZD liquidity gap at 07:00 NZ (Darwinex break, above). NZ Monday 07:00 is Sunday UTC (IC shut): not observable | NZDUSD (primary), AUDUSD | NZ Tue-Fri business days (XNZE) | NZ Tue-Fri holidays (HOL); NZ Saturdays = UTC Fridays (SAT: NZ market shut for the weekend) |
| NY-IMB | USTEC 15:50 ET; US30 15:45 ET before 2019-04-01, 15:50 ET from 2019-04-01; US30-1550 (secondary) 15:50 ET throughout | 19:45-20:50 | Nasdaq order imbalance message from 15:50 ET (SR-NASDAQ-2018-068; early imbalance indicator at 15:50 from 2019, SR-NASDAQ-2019-010 / -064); NYSE Mandatory MOC/LOC Imbalance Publication moved 15:45 -> 15:50 ET on 2019-04-01 (NYSE Trader Update 2018-12-14) | US30, USTEC | NYSE full trading days (XNYS open, not a 13:00 early close) | NYSE holidays and early closes when IC quotes (expected n/a: CME index futures halt by 13:15 ET then) |
| SETTLE | gold 13:29:00 ET, silver 13:24:00 ET, WTI and Henry Hub 14:28:00 ET, Brent 19:28:00 London | | CME settlement windows GC 13:29-13:30, SI 13:24-13:25 ET (CME "Daily Settlement Time Details"), CL / NG 14:28-14:30 ET (CME NG settlement procedure), ICE Brent 19:28-19:30 London (ICE contract spec). Platinum is left out: its window moved (12:59-13:00 ET in a 2009 advisory, 13:03-13:05 now) and the date is unknown | XAUUSD, XAGUSD, XTIUSD, XNGUSD, XBRUSD | XCME trading days that are not US federal holidays or 13:00 early closes; XBR: IFEU trading days except 24 / 31 Dec | XAU, XAG, XTI, XNG: US federal holidays on which CME trades but publishes no settlement (MLK, Presidents, Memorial, Juneteenth from 2022, Labor Day) (HOL); XBR: none |

Days that are neither OPEN nor a placebo (for example one European venue open and the other shut, for the cross-check
instruments) are dropped from both sets.

## Definitions (fixed)
- Prices: mid m = (bid + ask) / 2 of a tick; prevailing quote at time t = the last tick with ts <= t.
- **Opening move** at clock T with window w: p0 = prevailing mid at T - 1 s, p1 = prevailing mid at T + w,
  m = (p1 - p0) / p0 x 1e4 bp, direction d = sign(m). The quote at T - 1 s must be at most 10 min old, else no
  event. m = 0 gives no event. **w in {15, 60} s.**
- **Trailing same-clock norm** N = median |m| over the most recent 60 clean OPEN days strictly before the event day,
  same instrument, clock, shift variant and w (clean = valid m and no calendar exclusion in [T - 15 min, T + w +
  2 min]); needs >= 20 such days and N > 0, else no k > 0 event.
- **Event** at dose k: |m| >= k x N. **k in {0, 2, 4}**; k = 0 means every day with m != 0 (no norm needed).
- **Sides**: V1 side = d, V2 side = -d.
- **Entry**: the first tick with ts >= T + w + L; a buy at its ASK, a sell at its BID. **L = 250 ms decides**;
  execution variants L = 0, 1,000 ms, "next tick" (the tick after the L = 0 entry tick), and the bar's "+1 minute"
  (L = 60 s).
- **Exit**: the first tick with ts >= entry target + h (for "next tick": its own ts + h), long at the BID, short at
  the ASK, whatever the delay. **h in {5, 15, 60} min.**
- **Protective-stop variant** (S): a resting server-side stop placed at entry at distance s = max(|m|, 2 x the entry
  tick's spread in bp) from the entry mid (long: sell stop at m_e (1 - s/1e4), triggered by the first later tick up to
  the exit tick with BID <= level, filled at that BID; short: buy stop, ASK >= level, filled at that ASK). For V1 the
  level sits about where the price was before the clock; for V2 it is a doubling of the opening move.
- **Costs**: actual tick spreads; commission 0.6 bp round trip for AUDUSD, NZDUSD, XAUUSD, XAGUSD, XPTUSD; 0 for US30,
  USTEC, XTIUSD, XBRUSD, XNGUSD, DE40, UK100. Net = side x (exit fill - entry fill) / m_e x 1e4 - commission; mid =
  side x (exit mid - entry mid) / m_e x 1e4; spread paid = mid - net - commission; spread x1.5 = net - 0.5 x spread
  paid.
- **Calendar exclusions** (per event and h): any High / Medium timed row of the instrument's set in [T - 15 min,
  T + w + h + 2 min]. Sets: AUDUSD {AUD, NZD, CNY, USD, All}; NZDUSD {NZD, AUD, CNY, USD, All}; metals {USD, CNY,
  All}; energies {USD, CNY, All} + "Crude Oil Inventories", "Natural Gas Storage", "API Weekly Statistical Bulletin"
  of any impact; US30, USTEC {USD, All}; DE40 {EUR, USD, All}; UK100 {GBP, USD, All}; at EU-OPEN every instrument adds
  EUR and GBP. Also: central-bank windows [T_cb - 30 min, T_cb + 120 min] (the round-26 E2 list, all instruments) and
  the BOJ window 01:30-07:30 UTC on BOJ days; untimed High / Medium rows of the set = whole UTC day; election /
  referendum / vote rows = that UTC day and the next (round-26 E3 / E4); IC artefacts XTI / XBR 2020-04-15..04-30 and
  energies on Good Friday.
- **Rollover**: no trade whose window [T - 1 s, T + w + 60 s + h] touches 16:55-18:10 New York.
- **Minute level (DE40, UK100 at EU-OPEN)**: p0 = panel mid of the bar starting T - 1 min, p1 = mid of the bar
  starting T (so w = 60 s); entry at the close of the bar starting T (L0, optimistic, labelled) and the "+1 minute"
  variant at the close of the bar starting T + 1; exit h minutes after the entry bar's close; cost = half the panel
  spread at the entry minute + half at the exit minute; no stop variant.

## Cells (counted)
Tick sets (instrument or pool) per clock:
| clock | singles | pools | sets |
|---|---|---|---|
| CN-DAY | XAUUSD, XAGUSD, XPTUSD, AUDUSD, XTIUSD, XBRUSD | METALS {XAU, XAG, XPT}, ENERGY {XTI, XBR}, ALL {6} | 9 |
| CN-PM | same | same | 9 |
| CN-NIGHT | XAUUSD, XAGUSD, AUDUSD, XTIUSD, XBRUSD | METALS {XAU, XAG}, ENERGY {XTI, XBR}, ALL {5} | 8 |
| CNY-FIX | AUDUSD, NZDUSD, XAUUSD | FX {AUD, NZD}, ALL {3} | 5 |
| EU-OPEN | US30, USTEC, XAUUSD, AUDUSD, NZDUSD | INDICES {US30, USTEC}, FX {AUD, NZD}, ALL {5} | 8 |
| NZ-07 | NZDUSD, AUDUSD | FX {NZD, AUD} | 3 |
| NY-IMB | US30 (NYSE clock), USTEC, US30-1550 (secondary) | INDICES {US30 (NYSE clock), USTEC} | 4 |
| SETTLE | XAUUSD, XAGUSD, XTIUSD, XNGUSD, XBRUSD | METALS {XAU, XAG}, ENERGY {XTI, XNG, XBR}, ALL {5} | 8 |

Per tick set: family {V1, V2} x w {15, 60 s} x k {0, 2, 4} x h {5, 15, 60 min} x stop {none, S} = 72 cells;
54 sets = **3,888 tick cells**. Minute sets DE40, UK100 at EU-OPEN: family x k x h (w = 60 s, no stop) = 18 each =
**36 minute cells**. **Total 3,924 declared cells.** Every cell is decided at L = 250 ms on OPEN days at the clock
itself; latencies, x1.5 and the controls are readings of the same cell, not cells.

**Primary cells (32):** CN-DAY ALL, CN-PM ALL, CN-NIGHT ALL, CNY-FIX ALL, EU-OPEN ALL, NZ-07 NZDUSD, NY-IMB INDICES,
SETTLE ALL; w = 15 s, h = 15 min, no stop, k in {2, 4}, V1 and V2.

## Controls (every cell)
- **Venue-shut placebo**: the same rule (thresholds from the same trailing OPEN-day norm) at the same clock on the
  placebo days (HOL; NZ-07 also SAT); mean net and mid, t clustered by holiday block (consecutive placebo weekdays
  <= 4 calendar days apart = one block; SAT clustered by day); OPEN minus placebo difference with its t.
- **Shifted clocks**: the whole rule recomputed at T - 30 min and T + 30 min on the OPEN days (own norms, own sides,
  own exclusions). Known confounds, written now: CN-DAY + 30 = 01:30 UTC is the A-share / HKEX open (09:30
  Beijing / HKT), CN-PM - 30 = 05:00 UTC is the A-share / HKEX afternoon reopen.
- **Random direction** RD: the cell's own events with the side drawn at random per event (V1 or V2 outcome), 500
  seeds; share of seeds whose mean net is below the cell's.
- **Random time** RT (the bar's random-entry control): for each event, 200 random whole seconds T' drawn uniformly
  from [T - 150 min, T - 35 min] U [T + 35 min, T + 150 min] of the same day, valid only if the quote at T' - 1 s is
  <= 10 min old, no calendar exclusion in [T' - 15 min, T' + 62 min], the rollover rule holds for h = 60 and T' is not
  in an artefact window; side recomputed from the move T' - 1 s -> T' + w (V1 = its sign, V2 = minus; a draw with a
  zero move is redrawn), no magnitude filter, same L = 250 ms, h, stop rule (s from |m'|). A cell beats seed j if its
  mean net exceeds the mean of its events' j-th draws (IS, VAL, all).

## Statistics
- Per cell: n events IS / VAL; mid and net bp per event at each latency; t clustered by UTC day; by year; VAL/IS
  (net and mid); spread paid; stop-hit share; per-trade and per-day net Sharpe; power = Sharpe x sqrt(1.73 x events
  (event days) per year) on the IS and on the VAL size (events per year of a pool = the sum of its instruments' rates;
  IS spans 6 years, 4 for energies, 3.77 for oil at the Chinese clocks; VAL 3 years).
- Chance benchmark: (i) the 95 % max |t| of K independent normals for K = cells with >= 10 IS events; (ii) a
  per-UTC-day sign-flip null of the opening-move direction (one flip per day shared by every instrument, clock and
  cell, which swaps V1 and V2 outcomes), 1,000 draws, for the max IS net t over all counted cells and over the 32
  primary cells, and the same for the max |IS mid t|.
- Information only (no cell, no bar): CN-NIGHT by New York season (13:00 UTC is 08:00 EST / 09:00 EDT); US30 at
  NY-IMB before / after 2019-04-01; CN-DAY on the first trading day after a Chinese holiday (call-auction opens);
  the 2020 night-session suspension days; ex-March-April-2020 and per-cell winsorised (IS 1 / 99 %) readings.
- **V0 clock check (no returns):** per clock and instrument, tick counts and unsigned mean |change of mid| per 5-s bin
  from T - 60 s to T + 120 s, OPEN vs placebo days, IS only. Reported as a check that each clock exists in IC's
  feed; no cell is added, dropped or changed because of it.

## Bars (round 13's, as round 26 applied them; not lowered)
- **LIVE**: IS day-clustered net t >= 2.5, VAL net t >= 1.5; net > 0 in IS and VAL; >= 2/3 of years with events net
  > 0; > 0 at spread x1.5 and at +1 minute in IS and VAL; beats >= 95 % of RT in IS and VAL; power >= 3 at the VAL
  size (also reported at the IS size).
- **DEMO**: IS net t >= 2.0, net > 0 in VAL, beats >= 90 % of RT (IS), > 0 at spread x1.5 and +1 minute; no power
  requirement.
- A cell whose IS net t lies within the null's 95 % max is labelled "within chance". A cell that meets the numbers but
  whose venue-shut placebo or shifted clocks do as well is labelled "not venue-specific".
- PRE (Dukascopy M1, minute level, labelled) only if a family meets a bar on IS / VAL; its exact proxy and a
  calibration requirement on IC's own M1 are written in an addendum before it runs.
- A rule meeting LIVE or DEMO gets PREREG_DRAFT_V_<name>.md (rule, parameters, cell count, expected HOLD events and
  expected HOLD t on the VAL size and at 0.65 of it, C3 daily correlation on IS + VAL rows) and its family stops.
  HOLD is not opened.

## Prior (written now)
Opening moves at these clocks are probably 1-3 bp in gold, 2-10 bp in silver and oil, < 1 bp in FX. IC's round trip
is ~1.3-1.6 bp in gold, 4-5 in silver, 3-8 in oil, 0.8-1.2 in FX, 0.3-1.8 in the US indices. A 10-30 % continuation
or reversal of the opening move is 0.1-3 bp. Round 26 found jump information priced within the first minute and
single-instrument reversals below cost. Prior chance of a LIVE pass: low (a few %); of DEMO numbers somewhere: ~20 %,
mostly within chance.

## Additions after numbers
(anything added below this line after a number was seen is information only, unless it says otherwise)

### Addendum 1, 2026-10-17 21:40 UTC (from `date -u`), written after all 3,924 cells were computed
Seen by now: every declared cell, the controls, the chance benchmark and the declared information-only splits. Two
cells meet the DEMO numbers, both in the EU-OPEN V2 family (fade a k = 4 opening move over w = 60 s, hold 15 min,
no stop): US30 on ticks and UK100 at minute level. Both are within chance (the max IS net t over all cells, 2.23,
is below the sign-flip null's median 2.31).
- **The declared PRE check cannot run.** Index CFD data before 2016 is not local (research/data/duka holds only FX
  and metals); fetching Dukascopy index M1 2004-15 is a new price fetch, i.e. a user decision. Nothing is fetched.
- The EU-OPEN V2 family stops here: no variant beyond the declared grid is computed.
- Information only (tables built after the numbers, no cell, no bar): the 20 cells with the largest |IS mid t|, a
  mid-direction map per clock and set, the other sets and exits of the two DEMO-number specs (all already inside the
  declared grid), the C3 daily correlation and the HOLD expectations of the two DEMO-number cells.
