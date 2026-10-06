# Round 12, stream J: other executions of the real-but-sub-cost effects

Written 2026-10-06 00:58 UTC, before any stream-J number was computed. Read before writing: BRIEF.md (round 12),
round10_new_directions/STREAM_A, STREAM_C, STREAM_E (+ HYPOTHESES_E, their scripts e1.py / ev.py), round 6 S1 and S4,
round 11 H2 (+ HYPOTHESES_H M1/M5), flow_search_2026-09-27 (crypto intraday momentum), round 7 B (USDCNH), round 8 R3.
HOLD (2025-01-01 onwards) is never loaded: the panel ends 2024-12-31 and every tick load stops at 2024-12-31.
Additions after seeing data are marked **post hoc** with their UTC time.

## What this stream changes, and what it does not
The effect (clock window, symbol, side, conditioning) is kept exactly as the earlier round defined it; only the
execution changes: which minute / tick the order goes in and out at, market vs resting limit orders, how many flows
one position spans, lot size, and which IC symbol carries it. Each effect is first reproduced at mid with its original
rule (R0), and the match with the published IS mid number is reported.

Why this could escape the standing limits: the standing diagnosis is that these flows are real at mid (t 4-13) and
die on IC's cost (spread at busy minutes + 0.6 bp FX/metals commission). The earlier tests mostly paid the spread at
the exact clock minute with market orders. If the spread at those minutes is a transient spike, or if the flow itself
pushes price through a resting order, or if several same-sign flows can share one round trip, the cost per unit of
edge falls without touching the edge. The hard floor that no execution removes is the 0.6 bp commission per round
trip on FX and metals; for each effect I report the break-even cost and how far the best execution gets from it.

## Effects carried (sides fixed by the earlier rounds, never re-chosen)
| id | effect, original rule | side | published IS / VAL mid | data for execution tests |
|---|---|---|---|---|
| SGE | XAUUSD long p(02:15) -> p(02:23) UTC, Chinese trading days (XSHG) from 2016-04-19 (round 10 A/E) | long | +0.93 (t 7.9) / +0.72 (t 4.5) | panel + IC ticks |
| SYDpre | AUDUSD, NZDUSD short p(09:45) -> p(10:00) Sydney, Sydney weekdays (round 4, round 10 E) | short AUD, NZD | +1.65 (t 13.1) / +1.48 (t 10.0), C-RV top +2.52 / +2.12 | panel + ticks |
| SYDpost | same, long p(10:00) -> p(10:15) Sydney | long | +1.28 / +1.44 | panel + ticks |
| ECB | EURUSD long p(14:00) -> p(14:15) Frankfurt, TARGET days (round 10 E, flipped side) | long EUR | +0.73 (t 5.3) / +0.85 (t 4.1) (USD side -0.73 / -0.85) | panel only (no EURUSD ticks) |
| SETT | XAUUSD, follow sign(r_day) over 13:15 -> 13:30 ET, r_day = prev 13:30 ET -> 13:15 ET; big days |r_day| > sd of past 60 settlement-to-settlement returns; US weekdays, federal holidays out (round 6 S1) | follow | big days +2.31 (t 3.6) / +1.00 (t 1.5); all days +0.58 / +0.29 | panel + ticks |
| MOC | USTEC follow sign(mid 15:49 -> 15:50 ET) from close 15:51 to 16:00 ET (round 11 H2 M1, Nasdaq NOII time) | follow | +1.53 (t 2.71) / +1.00 (t 1.54) | panel + ticks |
| ASX | AUS200 fade the 16:00 -> 16:12 Sydney move over 16:13 -> 16:30 (round 11 H2 M5b) | fade | +0.82 (t 2.17) / +0.71 (t 2.71) | panel only |
| BTC | BTCUSD follow sign(day return 00:00 -> 23:30 UTC) over 23:30 -> 24:00 UTC (round 3, Wen et al. 2022) | follow | +8.8 (t 4.1) / +2.6 (t 1.9) | panel only |

Not carried, with reason (written now): FX residual / currency-strength reversal (round 8 R3, round 10 C) — round 10
stream C already ran cost timing (C5, "cheapest minute in, patient exit") on RES/REV/HKS and the per-component lot
by forecast (C1/C2 gates); a continuous 10-pair signal has no single flow minute for ideas 1-3 to act on. USDCNH
(round 7 B) — bid-only M1 with a published average spread, so no execution choice can be measured. Dollar catch-up /
adaptive periodicity: same as the FX residual (round 10 C).

## Common conventions
- Eras by event date: IS 2016-21, VAL 2022-24. Excluded: 24 Dec - 2 Jan (as round 10 E).
- Panel prices: p(T) = mid close of the bar ending at T (ffill <= 10 min), spread at that bar's last tick; the same
  helpers as round 10 E (`common.py`).
- Tick prices: research/ticks.py load_ticks, one UTC day (or two) at a time, days <= 2024-12-31 only. Quote at time
  t = the last tick with ts <= t. Market buy pays the ask, market sell gets the bid.
- Latency: a clock-scheduled order (no data condition) fills at the quote prevailing at the scheduled time. An
  order conditioned on observed data (spread gate, signal) fills at the quote 1 s after the condition was observed
  on ticks, or at the close of the next minute bar on M1 data. Stress: +60 s on every order of the rule, and spread
  x1.5 (half-spreads paid scaled by 1.5; limit fills unchanged but the market legs scaled).
- Limit fills (conservative, as the brief says): a buy limit at L fills only when the ask trades strictly below L
  (ask < L), at price L; a sell limit when the bid trades strictly above L, at L. Touch fills (ask <= L) are
  reported only as a sensitivity. No fill = no trade (for entry limits) or a market order at the timeout (exit
  limits). Unfilled days are counted and kept in the random-entry control.
- Adverse selection of a limit: mid move from order placement to a fixed horizon after the order window, on filled
  vs unfilled days (Welch t).
- Commission 0.6 bp round trip for FX and metals, 0 for indices and crypto. Every hold closes before 20:55 UTC (no
  swap) except J3e, which pays gold's long swap (research/swing/rates.py if it works without 2025 prices; else a
  fixed 1.5 bp per night long, stated).
- Statistics: per-trade mean, day-clustered t (sum of legs per UTC day), per-trade net Sharpe, power = Sharpe x
  sqrt(trades a year x 1.73), per-day power = per-day Sharpe x sqrt(days a year x 1.73), years net > 0. For any cell
  net > 0 in both IS and VAL: spread x1.5, +60 s, a random-entry control (>= 200 seeds, same count/side/hold, random
  start in the same session block on the same weekdays, same execution rule), and the C3 correlation (IS+VAL).
- Break-even round-trip cost per effect = its mid edge per trade (net 0); LIVE cost = mid edge - 3 x sd /
  sqrt(HOLD trades) (the cost at which power = 3). Both reported in bp next to the best execution's cost.
- Chance benchmark: max |t_IS| over the family's cells against max of K normals and a per-day sign-flip permutation
  shared by all cells of the family (1,000 draws).

## R0 reproduction (before anything else)
Each effect's IS and VAL mid with the original rule, printed next to the published number; a mismatch > 0.15 bp or
> 15 % is investigated before going on. The tick version of each tick effect (mid from bid/ask ticks at the same
clock times) is also printed, to show the tick data matches the panel.

## J1 Entry / exit minute chosen for the spread, causally
Mechanism: the cost at the flow's clock minutes is partly a transient spread spike (Sydney 10:00, gold 02:15, USTEC
15:50-16:00, BTC at the day roll); a few minutes away the spread is normal, and if the flow's move is not yet under
way (entry) or has finished and does not revert (exit), the edge survives the shift. Round 10 C5 tried the "cheapest
minute" idea only at a 15-min horizon in a pooled FX composite; here it is per effect, at tick level, with windows
chosen from the effect's documented path.
- Rule: entry window [a1, a2] ending at the original entry time (the order goes in at the first tick in the window
  with spread <= theta_in, filled 1 s later; if none, at market at a2); exit window [b1, b2] starting at the original
  exit time (first tick with spread <= theta_out after b1, fill 1 s later; if none, market at b2).
  theta = r x the median spread of the same clock window over the previous 20 event days (causal), r in {0.75, 1.0}.
- Windows (from the documented paths, written now):
  - SGE: entry [02:05, 02:15] (the pre-leg is flat: A1 pre [-30,0] +0.21), exit [02:23, 02:38] (no reversion
    within the hour).
  - SYDpre: entry [09:35, 09:45] Sydney; exit [10:00, 10:03] (the dip is gone 5-10 min after 10:00, so the exit
    window is short). SYDpost: entry [10:00, 10:02], exit [10:15, 10:25].
  - SETT: entry [13:12, 13:15] ET (the signal r_day is computed at the entry tick), exit [13:30, 13:40].
  - MOC: entry [15:51, 15:53] ET, exit [16:00, 16:05].
  - ECB (M1): entry minute in [13:50, 14:00] Frankfurt with spread <= theta, exit minute in [14:15, 14:25].
  - ASX (M1): entry [16:13, 16:16], exit [16:30, 16:35]. BTC (M1): entry [23:25, 23:30], exit [23:59, 00:05 next day].
- Also reported (not tradable, a bound): the oracle cheapest tick in each window, and the always-at-a2 / b1 market
  version (= R0 at executable prices).
- Cells: 8 effects (SYD counts two legs x 2 symbols as one effect each for pre/post -> 9 effect-legs) x 2 r = 18.

## J2 Passive limit orders filled by the known uninformed flow
Mechanism: when the flow's direction and timing are known, the price move it causes can fill a resting order: the
pre-fix leg of a V pushes price into a resting limit that closes the pre-leg position (and, if wanted, opens the
reversal), and a resting take-profit at the expected end of a one-way move earns the spread instead of paying it.
How it differs from round 6 S4: S4 rested a buy limit for the post-dip long (entry) at Sydney and exited at market
10 min later; it never closed the pre-leg short passively, never used a passive exit on a one-way flow (SGE, SETT,
MOC), and had no adverse-selection split.
- J2a SYDpre passive cover: short at market at 09:45 Sydney (bid); buy limit at L = entry bid - x bp (x in {0.5, 1,
  2}), live until 10:00 + tau (tau in {0, 3 min}); unfilled -> market buy (ask) at the timeout. 6 cells x 2 symbols.
- J2b SGE passive exit: long at market at 02:15 (ask); sell limit at L = entry ask + y bp (y in {0.5, 1, 2}), live
  until T_out in {02:23, 02:45}; unfilled -> market sell (bid) at T_out. 6 cells.
- J2c SGE passive entry: buy limit at the bid prevailing at 02:13 (x = 0) or bid - 0.5 bp, live 02:13-02:16; if
  filled, exit at market at 02:23. No fill = no trade. 2 cells. Expected to suffer adverse selection (the flow is
  upward, so a buy limit fills on the days it is absent); measured to say so.
- J2d SETT passive exit: entry at market 13:15 ET on big days; take-profit limit at entry + y (y in {1, 2, 4} bp) in
  the trade's direction, live to 13:30 / 13:40 ET; unfilled -> market. 6 cells.
- J2e MOC passive exit: entry at market at 15:51 ET; take-profit limit at y in {1, 2, 4} bp, live to 16:00 / 16:05;
  unfilled -> market. 6 cells.
- For every J2 cell: fill rate, net per trade (filled + market fallbacks), adverse selection (mid move from order
  time to T_out + 15 min, filled vs unfilled), and the touch-fill sensitivity.
- Cells: 12 + 6 + 2 + 6 + 6 = 32.

## J3 One position through several same-sign flows; netting opposite flows
Mechanism: the round-trip cost is paid once per position. If two flows of the same sign follow each other in one
symbol, holding through both pays one round trip for two edges; the price is the extra variance of the time between
them.
- J3a Gold Asian session: long XAU 01:00 -> 02:23 UTC (Chinese open drift + SGE AM auction) and 02:15 -> 06:23
  (AM + PM SGE auctions), Chinese trading days. Round 10 A6 (01:00-03:30, post hoc window) is the reference; J3a
  differs only in ending the hold at an auction's end. 2 cells.
- J3b EUR: long EURUSD 14:00 Frankfurt -> 15:45 London (the ECB fix, then hold until the WM/R window opens). The only
  later same-day EUR flow documented, WM/R pre, is USD long (opposite sign) and not significant in VAL (round 10 E:
  +0.30 / -0.19), so there is no second same-sign flow; this cell measures the cost of the extra variance. 1 cell.
- J3c Gold settlement -> next Asian morning: on SETT big-day-up days, hold the long from 13:15 ET to 02:23 UTC next
  day (through the settlement flow, the overnight, the Chinese open and the SGE auction; crosses one rollover and
  pays swap). Long side only (the Asian flows are long). 1 cell.
- J3d Netting opposite flows (Sydney V: short 09:45-10:00, long 10:00-10:15): a stop-and-reverse at 10:00 trades 2
  lots at 10:00, the same 4 lot-sides as two round trips, so it saves nothing at market. It is reported as the
  combined V P&L (pre + post at one fill at 10:00) for completeness. 1 cell x 2 symbols.
- Cells: 2 + 1 + 1 + 2 = 6.

## J4 Lot 0.5-2x by the conditional forecast
Mechanism: the constraints allow lot 0.5-2x by signal strength. Where a causal state variable scales the flow (round
10 E: SYD-pre +1.0 bp in the C-RV top tercile, SGE +0.65 bp on C-PRE active mornings; S1: big days carry the
settlement momentum), sizing up on those days raises $ per trade and $ Sharpe if the forecast ranks net edge. Caveat
written now: these variables were found in round 10 / round 6 on IS and VAL, so J4 is not out-of-sample for VAL.
- Lot = 2 in the causal top tercile, 1 in the middle, 0.5 in the bottom tercile (round 10 E's causal terciles:
  C-RV for SYDpre and SYDpost, C-PRE for SGE); SETT: lot 0.5 if |r_day| <= 0.5 sd, 1 if 0.5-1 sd, 2 if > 1 sd (all
  days traded); BTC: same by |day return| / its 60-day sd; MOC: by |signal minute return| / its 60-day RMS.
- Executions: the base (market at the clock minutes) and the best J1/J2 execution for that effect.
- Report: $ per trade at lot 1 = 1 unit, $ Sharpe, power, and the same at flat lot. 6 effects x 2 executions = 12 cells.

## J5 The cheapest correlated IC symbol / venue time
- J5a SYD: AUDUSD vs NZDUSD each alone, and AUDJPY (same Sydney open, AUD side). 1 extra cell (AUDJPY), per-symbol
  splits of SYD reported.
- J5b MOC: the USTEC signal (15:49 -> 15:50 ET) traded in US30 (VAL spread 0.3 bp vs USTEC 0.65), and US30's own
  NYSE-time signal for reference (round 11). 1 cell.
- J5c SETT: XAU only; there is no cheaper gold proxy at IC (XAG costs ~4 bp). Not run.
- SGE / ECB / ASX / BTC: no cheaper IC proxy carrying the same flow (EURUSD is the cheapest EUR pair; gold has no
  commission-free CFD at IC; AUS200 is the only Australian index; ETH costs more than BTC). Not run.
- Cells: 2.

## Bars
As the brief: LIVE needs IS day-clustered t >= 2.5, VAL >= 1.5, >= 2/3 years net > 0, random control >= 95 %, power
>= 3; DEMO IS t >= 2.0, VAL net > 0, control >= 90 %. Stress at spread x1.5 and +60 s must stay > 0. If any cell meets
DEMO or LIVE on IS/VAL, that family stops and PREREG_DRAFT_J_<name>.md is written; HOLD is not opened.
Total declared cells: J1 18 + J2 32 + J3 6 + J4 12 + J5 2 = 70.

## Clarifications after R0, before any J1-J5 number (2026-10-06 01:01 UTC)
- R0 matched the published IS mid for SGE (+0.91 vs +0.93), SYDpre (+1.65), SYDpost (+1.28), ECB (+0.73), ASX
  (+0.86 vs +0.82) and MOC (+1.55 vs +1.53, once round 11's bar-START labels are used: signal = mid over the bar
  15:50:00-15:50:59 ET, entry 15:52:00, exit 16:00:00). SETT big days give +2.05 (t 3.1) vs +2.31 (t 3.6) in IS and
  +0.97 vs +1.00 in VAL; BTC +7.3 (t 3.4) vs +8.8 (t 4.1) IS, +2.4 vs +2.6 VAL. The residual gaps are calendar /
  sample-start conventions I could not recover; both effects are carried as reproduced here.
- MOC windows therefore move one minute with the convention: J1 entry [15:52, 15:54] ET, J2e entry at market at
  15:52:00; exits unchanged ([16:00, 16:05]; limits live to 16:00 / 16:05).
- SETT's J1 gate: the side and the big-day flag are recomputed from the tick mid at the gate time (as written).

## J1b (added 2026-10-06 01:10 UTC, after the J1-J5 results, before any J1b number; post hoc in motivation)
Motivation: J1's causal spread gate saves 0.1-0.7 bp of spread but loses mid, because the flows' moves sit in the
same seconds as the spread spikes. The remaining "minute / second chosen for the spread" variant is a fixed clock
schedule chosen on IS at second resolution: the entry and exit seconds that maximise the IS mean of (exit price -
entry price) at the executable side, i.e. the best trade-off between mid kept and spread paid, then checked once in
VAL. It is a clock rule (no data condition), so no latency beyond the +60 s stress.
- Grid: prevailing quote every 5 s. Separable choice: entry second = argmin over the entry window of the IS mean
  executable entry price (relative to the mid 35 min before T, signed by the side); exit second = argmax of the IS
  mean executable exit price. Windows: SYDpre entry [T-30 min, T-5 min], exit [T-3 min, T+5 min] (T = 10:00 Sydney);
  SYDpost entry [T-1 min, T+3 min], exit [T+5 min, T+30 min]; SGE entry [02:00, 02:16], exit [02:16, 02:45] UTC;
  MOC entry [15:52, 15:55], exit [15:58, 16:10] ET (side from the signal, which needs the 15:51:00 close).
- Pooled AUD+NZD choice is primary; per-symbol choices reported as descriptive. 4 cells (SYDpre, SYDpost, SGE, MOC).
  The IS number is an in-sample optimum over ~300 x ~100 grid points (biased up); VAL is the test.

## D1 diagnostic: is the Sydney V tied to 10:00 Sydney or to the end of IC's rollover hour? (added 2026-10-06 01:12 UTC, post hoc, before its numbers)
Seen in the spread profile (control_out.txt): AUD/NZD mean spreads are wide (and skewed) for the whole half hour
before 10:00 Sydney and fall at 10:01. In the northern winter (AEDT + EST) 10:00 Sydney = 23:00 UTC = 18:00 New York,
exactly the end of the hour after IC's 17:00 NY rollover, when spreads normalise; in the northern summer it is 20:00
NY, and in the DST-mismatch weeks 19:00 NY. If the V (mid falls into T, recovers after) is a flow of the Sydney open,
it is the same size whatever T is on the New York clock; if it is a quote artefact of the end of the wide-spread
rollover hour, it sits at 18:00 NY and is absent at 10:00 Sydney when that is 19:00/20:00 NY, and a placebo V
appears at 18:00 NY in the northern summer (08:00 Sydney). Report only (no trading rule): SYDpre / SYDpost mid and
spreads split by the NY-clock time of 10:00 Sydney; the same windows at 18:00 NY on days when that is not 10:00
Sydney. Sides as registered (short into, long after).

## J5c the Sydney V outside IC's rollover hour (added 2026-10-06 01:13 UTC; POST HOC: D1's split by NY clock, IS and VAL, was seen first)
D1 result that motivates it: the pre-10:00 dip is a Sydney-open effect (present when 10:00 Sydney = 19:00 or 20:00 NY,
absent in the 18:00-NY placebo in the northern summer), but its cost is 2.4-5x higher in the northern winter, when
10:00 Sydney = 18:00 NY and the window sits in IC's post-rollover wide-spread hour (17:00-18:00 NY). "Never trade in
the rollover hour" is an execution rule a desk would write before looking (it is the cheapest-venue-time idea of J5),
but here it was written after seeing the split in both eras, so VAL is not a clean check for it.
- Rule: SYDpre (short AUDUSD and NZDUSD from T-15 to T, T = 10:00 Sydney, Sydney weekdays) only on days when T is at
  or after 18:30 New York (i.e. 19:00 or 20:00 NY; the [T-15, T] window is outside 17:00-18:15 NY). Executions:
  clock market (base), and the J1 r0.75 gate. SYDpost with the same filter is reported for completeness.
- Per-symbol (AUD, NZD) numbers reported; the pooled pair is the cell. 2 cells (SYDpre, SYDpost) x base.
- Full bar battery if net > 0 in both eras: x1.5, +60 s, years, random-entry control (200 seeds: short both
  symbols for 15 min at a random start in the same NY-clock block 18:30-22:00 NY on the same days, excluding the
  Sydney-open window), day-clustered power, C3 correlation. No clean out-of-sample era exists (Dukascopy AUD/NZD are
  H1 only), so any pass is a lead for HOLD / forward testing with this disclosure, not a VAL-confirmed rule.

## Outcome (2026-10-06 01:19 UTC)
J1, J1b, J2, J3, J4, J5a/b: no cell net > 0 in both eras with IS t >= 2 (details in STREAM_J.md). J5c (post hoc): the
AUDUSD cell meets the DEMO bar on IS/VAL (LIVE fails on power); J5 is stopped and PREREG_DRAFT_J_sydney_aud_offroll.md
is written with the post hoc disclosure. HOLD was not opened.
