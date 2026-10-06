# Stream B hypotheses: central-bank decisions and home-market holidays, pooled across countries

Written 2026-10-05 17:55 UTC, before any stream-B return, response or event-window number was computed. Before this
file only the brief, the journal, the round 3/4/7/8 tables and the shared panel's meta / spread table were read, and
a literature lookup was done (OpenAlex abstracts). The calendars (decision dates and times, holidays) are being built
from official sites in parallel; they are inputs, not results. Additions made after seeing data will be marked
**post hoc** with their time.

## Common conventions (all families)
- Prices: shared panel mid (bid close + ask close)/2 of minute i, forward-filled with age <= 2 minutes at a window
  start and age 0 at the signal / entry minute (age <= 5 at an exit; else the leg is dropped and counted). ln returns,
  in bp.
- Signal on data up to the close of minute i; fill at the close of minute i+1 (main) and i+2 (latency variant).
- Cost per leg, round trip: half the actual spread at the entry minute + half at the exit minute (panel spr, floored at
  0) + 0.6 bp for FX. Indices 0 commission. Holds across 17:00 New York pay `research/swing/rates.py swap_frac_at` (x3
  on the triple day). Variant: spread x1.5.
- Eras by event time: IS 2016-01..2021-12, VAL 2022-01..2024-12; PRE 2004-2015 (Dukascopy bid, IC 2016-17 spread by
  minute of day + 0.6 bp) where noted. HOLD (2025+) is not loaded anywhere.
- t: clustered by UTC day (all legs of a day summed into one unit, t over days). Spiky quotes: a leg with |mid return|
  > 20 x the symbol's median 60-min |return| is listed and the t is also shown winsorised at 1/99 %.
- Random control (>= 200 seeds): the same rule applied on random non-event weekdays at the same local time of day,
  same symbols, same count per year, same weekday mix (for the momentum rule the side comes from the rule itself, so
  the side mix is reproduced by construction). Reported: share of seeds whose net mean is below the candidate's.
- Power = per-trade net Sharpe x sqrt(expected HOLD trades = trades per year x 1.73); also per-day Sharpe x
  sqrt(HOLD days).
- Multiple testing: cells per family counted; chance benchmark = expected max |t| of K independent normals and a
  sign-flip-per-day permutation null (one flip per UTC day shared by every leg of that day, 1000 draws).

## Why the family as a whole could escape the standing limits
Event moves are 10-100 bp, so the ~1 bp FX / 1-3 bp index cost is not the binding constraint (unlike rounds 3-4
flows). The binding constraint in rounds 3-8 was the count (8-50 events/yr for one event type). Pooling one mechanism
across 7-8 central banks raises it to ~60-90 decisions a year (more legs), and PRE 2004-15 adds a second out-of-sample
era for FX.

A-priori power (per-event Sharpe needed): LIVE needs Sharpe >= 3 / sqrt(N/yr x 1.73). For ~62 decisions/yr that is
0.29 per event (day-clustered); for B1's ~35 events/yr, 0.39 (the size Lucca & Moench report for the Fed, ~0.5);
DEMO needs IS t >= 2, i.e. Sharpe >= 2 / sqrt(IS events): ~0.10 for B2, ~0.14 for B1.

## B1 Pre-announcement drift outside the Fed (falsification test)
- Mechanism / source: Lucca & Moench (2015, JF): equities rise in the 24 h before FOMC announcements (risk premium
  for the resolution of policy uncertainty). Brusa, Savor & Wilson (2020, Review of Finance, "One central bank to rule
  them all"): **no** comparable premium around ECB, BoE, BoJ (and other) meetings, internationally or domestically.
  The literature therefore predicts zero; the test is registered as a falsification of the "every central bank" story.
  Side fixed: long.
- Why it could escape the limits: if a non-Fed drift existed at even half the Fed size (~25 bp per event, Sharpe
  ~0.25), pooling four banks gives ~35 events/yr: DEMO-reachable (IS t ~3.6), LIVE only at Fed size (power 1.9 at
  half size).
- Events: scheduled ECB, BoE, BoJ, RBA decisions (emergency moves excluded). 2016-2024.
- Legs: ECB -> DE40; BoE -> UK100; BoJ -> JP225; RBA -> AUS200 (one leg per event; STOXX50 / F40 bid-only as a
  secondary ECB check only if the primary is positive).
- Windows (decision time T, local clock of the bank; BoJ T := 02:15 UTC of the decision day, before the earliest
  usual release):
  - W24 (primary, the Lucca-Moench construction): entry at T - 24 h (previous trading day, same local clock; if
    that day is a weekend, the previous Friday), exit at T - 15 min. Crosses one rollover: swap paid.
  - WDAY: entry at the home cash open of the decision day (Xetra 09:00 CET, LSE 08:00 UK, Tokyo 09:00 JST =
    00:00 UTC, ASX 10:00 Sydney), exit T - 15 min. No rollover.
- Cells: 2 windows x {pooled, per bank} reported; judged on the pooled W24 cell (K = 2 for the pooled verdict, 10
  with per-bank cells).
- Control: same windows on random non-decision weekdays (same bank clock, same weekday mix).

## B2 Post-decision drift (continuation), pooled across eight central banks
- Mechanism / source: slow digestion of a large, complex policy information event (statement + press conference,
  forward guidance, balance-sheet news) and dealer inventory / hedging after the initial jump (Neuhierl & Weber 2019
  "monetary momentum" for multi-day equity drift after FOMC surprises; Andersen et al. 2003 find quick adjustment to
  data releases, which is why the 08:30 data version failed in rounds 3 and 8 S4). A policy decision is larger and
  harder to parse than a single data print, so the side is continuation (registered).
- Why it could escape the limits: ~62 scheduled decisions/yr across eight banks, two legs (currency + index) where an
  index exists; event moves 10-50 bp, cost ~1 bp FX / 1-3 bp index once the announcement spread has normalised; PRE
  2004-15 (M1 for EURUSD, USDCHF, USDJPY) as a second out-of-sample era. FOMC decisions are included only from the
  announcement onwards (the pre-FOMC window is ineligible).
- Events: scheduled decisions of FOMC, ECB, BoE, BoJ, RBA, BoC, RBNZ, SNB (emergency moves excluded), at the
  official announcement minute T (from the calendar JSON). BoJ (no fixed time): T = the first minute in 02:00-06:30
  UTC of the decision day in which |USDJPY 1-min mid return| >= 6 x its median 1-min |return| over the same window of
  the previous 20 non-BoJ weekdays (a rule a bot can apply in real time; if none, the event is dropped and counted).
- Legs (home instruments, signed so that > 0 = continuation of the first move):
  FOMC: EURUSD, USDJPY, US500; ECB: EURUSD, DE40; BoE: GBPUSD, UK100; BoJ: USDJPY, JP225; RBA: AUDUSD, AUS200;
  BoC: USDCAD; RBNZ: NZDUSD; SNB: USDCHF. (<= 3 positions per event: the bot constraint.)
- Reaction: r0 = ln P(close of T + k - 1) - ln P(close of T - 2) i.e. from the last full minute before the
  announcement to the end of the k-th minute after it, k in {5, 15}. Side d = sign(r0) per leg; legs with r0 = 0
  are skipped. Entry: close of minute T + k (one minute after the signal minute), latency variant T + k + 1.
- Exit H in {60 min after entry, EOD = close of the 20:49 UTC bar (only if entry <= 20:00 UTC; for FOMC entries
  after 20:00 UTC, EOD is not available and the event counts only in H = 60)}.
- Anchor variants: decision minute (primary) and press-conference start (FOMC 14:30 ET, ECB 14:30 / 14:45 CET, when
  the calendar has it) as a secondary anchor.
- Primary cell, fixed now: k = 15, H = EOD, decision anchor, all legs pooled. Grid: 2 k x 2 H x 2 anchors x {all,
  FX only, index only} = 24 cells (K = 24 for the chance benchmark; per-bank splits are descriptive only).
- PRE check (only if the primary passes IS/VAL): ECB -> EURUSD, SNB -> USDCHF, BoJ -> USDJPY, FOMC -> EURUSD /
  USDJPY / USDCHF on Dukascopy M1 2004-2015, same rule.
- Control: the same rule at the same local clock time on random non-event weekdays of the same bank.

## B3 Home-market holiday asymmetry (Ranaldo 2009; Breedon & Ranaldo 2013)
- Mechanism / source: currencies depreciate during their own market's hours because domestic agents are net buyers
  of foreign currency in their hours (Breedon & Ranaldo 2013, JMCB; Ranaldo 2009, JBF). On a home-market holiday the
  domestic agents are absent, so the home-hours depreciation should vanish. Side registered: long the home currency
  vs USD over its home-hours window on its holidays; for US holidays, long USD vs the basket in the US window.
- Why it could escape the limits: pooled across eight home markets the count is ~50-70 currency-holidays a year,
  and PRE 2004-15 doubles the sample. **But the a-priori power is poor and is stated before computing**: the normal-
  day depreciation measured in round 1 v2 was ~1.5 bp (EURUSD, t -2.5 IS), so the holiday trade's expected gross is at
  most ~+1.5 bp against a ~0.7-1.5 bp cost and a 7-9 h window sd of ~30-40 bp: per-event Sharpe <= 0.04, power <=
  0.5, IS t <= 0.8. It is screened as a mechanism check (holiday minus normal-day difference, own t), not expected to
  reach DEMO.
- Home windows (local clock, converted to UTC each date with zoneinfo): EUR Frankfurt 08:00-17:00, GBP London
  08:00-17:00, CHF Zurich 08:00-17:00, JPY Tokyo 09:00-15:00, AUD Sydney 10:00-17:00, NZD Wellington 12:00-17:00 (to
  stay clear of the 17:00 NY rollover), CAD Toronto 08:00-16:00, USD New York 09:00-16:00.
- Holidays (python `holidays` 0.105): DE national + Frankfurt (TARGET-only closures dropped, see exclusions), UK
  England & Wales bank holidays, CH Zurich, JP national + bank holidays 31/12-3/1, AU NSW, NZ national + Wellington,
  CA Ontario (federal + Family Day), US NYSE + federal (Columbus, Veterans). Weekdays only.
- Exclusions (fixed now): 24 Dec - 2 Jan; Good Friday (global thin market); any day that is also a US holiday (for
  non-USD legs; the USD side must be open) or, for USD legs, a UK holiday (London must be open).
- Pairs: EURUSD, GBPUSD, USDCHF, USDJPY, AUDUSD, NZDUSD, USDCAD; US legs = all seven, USD signed.
- Statistics: (a) holiday trade net, pooled, day-clustered; (b) holiday minus normal-day mean of the same signed
  window return, t from the two day-clustered samples. PRE 2004-15: EUR, CHF, JPY on Dukascopy M1, AUD/NZD/CAD/GBP on
  H1 (windows rounded to whole hours).
- Cells: 1 primary (pooled holiday trade) + 8 per-currency descriptive.

## B4 Other pooled scheduled events
- B4a Minutes releases, continuation (same construction and cells as B2's primary, k = 15, H = EOD / 60 min):
  FOMC minutes (14:00 ET; EURUSD, USDJPY, US500) and RBA minutes (11:30 Sydney; AUDUSD, AUS200). Mechanism: as B2,
  a long text released at a fixed time. ~19 events/yr: LIVE impossible (needs Sharpe 0.52); DEMO needs IS Sharpe
  >= 0.19. 4 cells (k 15, H 2, anchor 1, {all}) + FX/index split descriptive.
- Considered and not registered (reason fixed now): Japanese fiscal half-year-end repatriation (2 events/yr: power
  impossible); quarter-end USD funding (round 3 tested USD month/quarter-end, no effect; M1 failed twice);
  daylight-saving mismatch weeks (no literature side, so a side cannot be fixed in advance).

## Addendum 2026-10-05 ~18:25 UTC (method, from the coordinator after stream A; B3 had already been computed)
- Calendar-pooled tests (B3) also report t clustered by holiday block (a run of consecutive days that are weekends or
  holidays in any of the eight calendars = one cluster) and a placebo: the same currency/window trades applied on
  OTHER countries' holidays (own holidays and the US/UK exclusions kept); the effect must beat those placebos. PRE
  2004-15 stays the extra check. B3's verdict is judged on the stricter of the two clusterings.
- CB event families (B1, B2, B4a): unchanged (event days are not blocks); the random same-weekday, same-clock
  non-event control registered above is the placebo.

## B2r, **post hoc** (written 2026-10-05 ~19:05 UTC, after the B2 IS/VAL grid was printed)
- Seen in the B2 grid: the press-conference anchor with k = 5 has the opposite sign to the registered continuation
  in both eras (all legs, H 60: mid -4.5 bp, t -1.6 IS; -9.8, t -1.9 VAL). That is 1 of 24 cells, inside the chance
  band (best |t| 1.99 vs ~2.2 expected max of 24 normals), and it cannot meet DEMO on IS (reversal net t ~1.5 < 2).
- Out-of-sample check only, on data no stream-B number has touched: PRE 2004-2015 Dukascopy M1 bid, IC 2016-17
  spread profile + 0.6 bp. Rule: at the press-conference start P (calendar), r0 = ln P(P+5) - ln P(P); side = -sign(r0);
  entry at P+6 min, exit H = 60 min (primary) and EOD 20:50 UTC. Legs: ECB -> EURUSD; FOMC (press conferences
  2011-2015) -> EURUSD, USDJPY, USDCHF; SNB -> USDCHF. t clustered by UTC day. It is reported as a falsification
  check, not a candidate: whatever PRE shows, the IS bar is not met.
