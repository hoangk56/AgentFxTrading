# Round 10, stream E: size-conditioned fixed-time flows (E1) and non-US scheduled macro releases (E2)

Written 2026-10-05 18:05 UTC, before any stream-E number was computed. Read before this file: the brief, the
lead's feasibility frontier (in the task), HYPOTHESES_A/B/C/D, stream A's write-up, the round 3/4/8 tables on fixes
and 08:30 New York data, and the shared panel's meta / spread table. HOLD (2025+) is never loaded: the shared panel
ends 2024-12-31. Additions after seeing data are marked **post hoc** with their UTC time.

## Common conventions (both families)
- Prices: shared panel mid; p(T) = close of the minute bar ENDING at clock time T (panel index T - 1 min),
  forward-filled for up to 10 minutes (stream A's `ev.price`). Returns in bp, signed by the trade side.
- Executable net per round trip = side x mid return - half the actual spread at the entry minute - half the actual
  spread at the exit minute - 0.6 bp commission (FX and gold). Stress: spread x1.5; +1 minute (entry and exit both one
  minute later). All holds close before 20:55 UTC (no swap), except where stated.
- t: clustered by UTC day (all legs of a day summed into one unit). Eras by event date: IS 2016-21, VAL 2022-24.
- Chance benchmark: per-day sign flip shared by all cells of the family (1,000 draws), max |t_IS| over cells;
  also the expected max of K normals.
- For any cell net > 0 in both IS and VAL: random-entry control (>= 200 seeds; same count per year, same side mix,
  same hold, random clock times in the same session window and weekday mix), years positive, per-trade Sharpe and
  power = Sharpe x sqrt(trades/yr x 1.73), per-day power, and the daily/monthly P&L correlation with C3
  (trades_C3_gotobi_jpy_basket.csv, IS+VAL).
- Excluded everywhere: 24 Dec - 2 Jan. The Tokyo 09:55 fix and gotobi days are not used (C3's mechanism).

## E1 Size-conditioned fixed-time flows

### Mechanism and why it could escape the standing limits
A benchmark flow is roughly fixed in money (index funds, corporates and custodians fixing a given notional), so its
price impact in bp scales with the market's illiquidity (Kyle lambda ~ sigma / sqrt(volume)); the spread at a busy
fix minute stays close to normal because dealers compete for fix business. Rounds 3-4 and stream A measured these
fix moves unconditionally: ECB fix +0.7..1.1 bp, SGE gold auction +0.9 bp, Sydney V 1.2-1.7 bp, all below the
~0.7-1.6 bp round trip at those minutes, or barely above it. If impact scales with a causal illiquidity proxy, the
top tercile of days could carry ~1.5-2x the unconditional move while costing about the same, which would lift the
per-event net above zero on ~80 events a year per fix. Sources: Krohn, Mueller & Whelan (2024) for USD up into the
fixes and down after; Evans (2018) / Melvin & Prins (2015) for WM/R; Kyle (1985) and Amihud (2002) for the scaling.
Stream C uses the same fixes unconditionally inside a composite; E1 differs in that it trades each fix alone and only
on days the conditioning variable selects.

### Events, legs and sides (all fixed before computing; sides from the mechanism or from earlier rounds)
| id | event (clock, DST-aware) | symbol(s) | leg | side |
|---|---|---|---|---|
| ECB-pre | ECB reference rate 14:15 Frankfurt; TARGET holidays excluded | EURUSD | p(T-15) -> p(T) | USD long (short EURUSD) |
| ECB-post | same | EURUSD | p(T) -> p(T+15) | USD short (long EURUSD) |
| WMR-pre | WM/R 16:00 London | EURUSD, GBPUSD (2 positions) | p(T-15) -> p(T) | USD long |
| WMR-post | same | EURUSD, GBPUSD | p(T) -> p(T+15) | USD short |
| SGE | SGE AM gold benchmark auction 10:15 Beijing = 02:15 UTC; Chinese trading days only (XSHG, stream A's calendar), since 2016-04-19 | XAUUSD | p(02:15) -> p(02:23) | long (side derived from data by stream A, so it counts only if VAL confirms; Dukascopy XAU is H1 only, so there is no PRE check at minute resolution) |
| NYC | New York 17:00 close, the hour after it | USDJPY | p(17:01 NY) -> p(18:00 NY) | long USDJPY (round 4: +0.8 bp t 5.9 / +1.0 t 3.8). Entry one minute after the rollover minute, so no swap; it does not touch the Tokyo fix |
| SYD-pre | Sydney open 10:00 Sydney, Sydney weekdays | AUDUSD, NZDUSD (2 positions) | p(T-15) -> p(T) | short AUD/NZD (round 4: -1.6/-1.7 bp) |
| SYD-post | same | AUDUSD, NZDUSD | p(T) -> p(T+15) | long AUD/NZD |

### Conditioning variables (two, declared now; no others will be searched)
- **C-RV (multi-day volatility regime)**: RV_d = sum of squared 5-minute mid log returns of the symbol over UTC day d
  (all quoted minutes); RV20 = mean of RV over the 20 weekdays before the event day (today excluded). Tercile cut =
  67th percentile of RV20 over the previous 250 weekdays (at least 60), so the threshold is causal. TOP = RV20 above it.
- **C-PRE (same-day pre-window activity)**: a = RMS of 1-minute mid returns over the 60 minutes ending one minute
  before entry ([entry-61, entry-1]); ratio = a / mean of a at the same clock window over the previous 20 weekdays;
  TOP = ratio above the causal 67th percentile of the ratio over the previous 250 weekdays (at least 60).
- For two-symbol legs each symbol uses its own variable (positions are independent; the day unit sums both).
- Judged cell = TOP tercile. Reported next to it (not as cells to select from): unconditional, BOTTOM tercile, and the
  TOP-minus-BOTTOM mid difference with Welch t as the mechanism check (impact should rise with illiquidity). The
  spread at the entry/exit minutes in TOP vs all days is reported (the mechanism needs it to rise less than the move).
- Cells: 8 legs x 2 variables = 16 judged cells (chance max |t| of 16 normals ~2.6 one-sided, ~2.9 two-sided).
- Bars as in the brief. ~80 events/yr per leg in TOP: LIVE needs per-trade net Sharpe >= 3/sqrt(140) = 0.25 for one
  position per day (0.18 for two-symbol legs if the positions were independent); DEMO needs IS t >= 2.

## E2 Non-US scheduled macro releases, pooled: post-release continuation and the pre-release window

### Mechanism and why it could escape the standing limits
Rounds 3 and 8 (S4) tested only the 08:30 New York releases, where the USD market is the deepest in the world and
adjustment is within a minute (Andersen et al. 2003). Releases of smaller economies move their home currency in
thinner markets, at hours where fewer participants are active (Sydney 11:30 = 00:30/01:30 UTC; London 07:00), so
slow digestion and order-flow continuation after the first reaction are more plausible (Evans & Lyons 2005,
"Do currency markets absorb news quickly?": order flow keeps carrying news for hours; Love & Payne 2008; Dominguez &
Panthaki 2006 on non-US news). Pooling ~10 release types across 7 currencies gives ~100-150 events a year, which is
what the power rule needs (LIVE at ~130/yr requires per-event net Sharpe >= 0.20).

### Releases (local clock, DST-aware), home pair; calendar source
Dates come only from official release calendars or archives (never from price moves). A release type whose dates
cannot be obtained reliably for 2016-2024 is dropped and reported as dropped.
| release | time (local) | pair | source |
|---|---|---|---|
| UK CPI (monthly) | 09:30 London, 07:00 after ONS moved market-sensitive releases (switch date from ONS documentation) | GBPUSD | ONS previous releases |
| UK labour market (monthly) | same | GBPUSD | ONS previous releases |
| Euro-area flash HICP (monthly) | 11:00 CET (Eurostat) | EURUSD | Eurostat euro-indicator calendar / archive |
| German Ifo business climate (monthly) | 10:00 CET | EURUSD | ifo press-release archive |
| German ZEW sentiment (monthly) | 11:00 CET | EURUSD | ZEW release archive |
| Euro-area / German flash PMI | 09:30 / 10:00 CET | EURUSD | S&P Global; likely no public archive -> dropped if so |
| Australia labour force (monthly) | 11:30 Sydney | AUDUSD | ABS past releases |
| Australia CPI (quarterly) | 11:30 Sydney | AUDUSD | ABS past releases |
| Canada LFS (monthly) | 08:30 Toronto | USDCAD | StatCan The Daily |
| Canada CPI (monthly) | 08:30 Toronto | USDCAD | StatCan The Daily |
| NZ CPI, GDP, labour market (quarterly) | 10:45 Wellington | NZDUSD | Stats NZ |
| Japan Tankan (quarterly) | 08:50 Tokyo | USDJPY | BoJ; exit capped at 09:50 JST so no hold reaches the 09:55 fix |
| Swiss CPI (monthly) | FSO release time (08:30 CET; earlier 09:15) | USDCHF | FSO |

### E2-cont rule (side registered: continuation)
- T = release minute; p(T) = last quote before the release. Reaction r0 = ln p(T+5) - ln p(T) (k = 5 fixed).
  Side d = sign(r0) (in the pair's direction); r0 = 0 skipped. Entry at p(T+6) (one minute after the signal minute,
  executable), exit at p(T+6+h), h in {30, 120, 240} minutes, the exit capped at 20:55 UTC (an entry after 20:25 UTC
  is dropped). One position per event; two releases at the same minute for one currency count as one event.
- Subsets: ALL events; LARGE = |z| >= 1 with z = r0 / RMS of r0 over the previous 12 events of the same release type
  (at least 6; causal).
- Cells: 3 h x 2 subsets = 6 pooled cells. Primary cell fixed now: h = 120, ALL. Per-currency and per-release splits
  are descriptive only. Canadian releases often share the minute with US data (LFS with NFP); they are reported
  separately as well, with and without days on which a US release falls at 08:30 ET (if a US calendar is available).
- Control: the same rule at the same local clock time on random non-release weekdays of the same currency.

### E2-pre (report only: no side)
The literature gives no ex-ante side for a pre-release move in FX (Kurov et al. 2019's US pre-announcement drift is
in the direction of the not-yet-known surprise). Reported, not traded: (a) the unsigned mean of r[-60,0] and
r[-15,0] per currency; (b) the same signed by the later reaction sign(r0) (an information-leakage diagnostic that a
bot cannot use); (c) the mean |r[-15,0]| against non-release days (a volatility premium check).

## Clarification of E2's exit cap (2026-10-05 18:06 UTC; after E1's numbers, before any E2 number or release date was read)
The 20:55 UTC cap exists to keep holds off the 17:00 New York rollover. NZ releases (10:45 Wellington = 21:45/22:45
UTC of the previous UTC day) and the Tankan (08:50 Tokyo = 23:50 UTC) come after the rollover, so for them the exit
is capped at 16:55 New York of the next New York day instead (never binding for h <= 240), plus the Tankan's 09:50 JST
cap. All other releases keep the 20:55 UTC cap. No release type is dropped for its clock time.

## E1 outcome (2026-10-05 18:06 UTC)
No candidate: none of the 16 judged TOP-tercile cells is net > 0 in both IS and VAL. Details in the stream E write-up.

## E2 calendars fixed (2026-10-05 19:32 UTC; built from official sources without price data, before any E2 number)
Scratchpad r10/E/cal/releases.json and sources.txt. 16 types, every year complete 2016-2024: UK CPI and labour
market (ONS calendar; 09:30 until March 2020, 07:00 from April 2020, per-event times), AU labour force, AU CPI
quarterly and the monthly CPI indicator from 2022-10 (ABS, 11:30), CA LFS and CPI (StatCan, 08:30 ET), EA flash HICP
(Eurostat, 11:00 CET), Ifo (10:00 CET; dates from archived ifo URLs, medium confidence), ZEW (11:00, 11:05 from
2021), NZ CPI/GDP/HLFS (Stats NZ, 10:45), Tankan (BoJ, 08:50 JST), Swiss CPI (FSO embargo times: 09:15 until 2018,
08:30 from 2019), US NFP (clash flag only). Dropped: euro-area/German flash PMI (no public official archive).
Choices: only the regular "events" are used ("extra_events" such as the 2023-10-17 UK partial release and the
2020-03-19 special Ifo are not). Releases for the same pair at the same minute merge into one event (AU monthly and
quarterly CPI).

## E2 implementation note and outcome (2026-10-05, after the E2 run)
Implementation fix, rule unchanged: NZ releases in the northern winter (21:45 UTC = 16:45 New York) precede the NY
rollover; the first run dropped them by a coding error. They are now held through the rollover and pay swap (x3 on
Wednesdays), as the cost rule in the brief requires. Outcome: no candidate. The primary cell (h 120, ALL) is net -0.88
(t -1.05) IS / -1.56 (t -1.57) VAL; best of 6 cells |t_IS| 1.32 vs per-day sign-flip 95 % 2.61. Write-up: scratchpad
r10/E/STREAM_E.md.
