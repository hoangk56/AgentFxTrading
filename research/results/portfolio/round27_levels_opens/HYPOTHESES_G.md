# Round 27, stream G: gold's round-number cascade with resting orders on IC ticks (declared before numbers)

Brief: [BRIEF.md](BRIEF.md) row G; round13_structural/BRIEF.md (eras, costs, bars, pitfalls); round26_tick_events/
BRIEF.md (the binding tick fill model). **Declaration 1 written 2026-10-17 21:23 UTC (`date -u` 21:23:09), before any
return of any kind was computed in this stream.** HOLD (2025-01-01 onwards) is never loaded: every tick day is
asserted < 2025-01-01 in the loader, the last NY session used ends 2024-12-31 17:00 New York, Dukascopy files are cut
at 2016-01-01, and the C3 file is read for its IS / VAL rows only.

What was looked at before this declaration (no returns, no price differences into returns):
- tick format and density: gold 100-170k ticks a day, median gap ~0.3 s; silver 15-90k; platinum 6k a day, and no
  XPTUSD ticks at all in 2017 (every 2017 file is empty);
- median session spread of gold ($): 2016 0.148, 2017 0.112, 2018 0.086, 2019 0.089, 2020 0.251, 2021 0.115,
  2022 0.098, 2023 0.088, 2024 0.063 (0.64 bp median); silver ~3.8 bp; platinum ~20 bp;
- engine checks: the rolling 24-hour max / min and the 60-minute median spread against brute force (0 mismatches in
  3,000 random minutes); a listing of six 2019 events (arming state, levels, thresholds, trigger ticks; no exits);
- event counts of the bots below, by year (out/count_proto_xau.txt, out/count_proto2.txt). Gold, G1 c = 0.5, $10:
  2016 223, 2017 150, 2018 160, 2019 186, 2020 340, 2021 285, 2022 302, 2023 272, 2024 371 (IS ~226 a year, VAL
  ~315 a year); the $5 grid has the same counts. Sub-cell shares: L a multiple of $50 0.20, of $100 0.10, entries in
  12:00-17:00 UTC 0.40, repeat touches 0.22. Silver $0.50 ~134 a year, $1 ~69 a year; platinum $10 ~264 a year.

## Mechanism and sources (sides from the sources, not from our data)
- Osler 2003 (JF 58, "Currency orders and exchange rate dynamics"): take-profit orders cluster at round numbers, so
  trends tend to reverse when the price first reaches one; stop-loss orders cluster just beyond round numbers, so
  trends accelerate once a round number is crossed. Osler 2005 (JIMF 24, "Stop-loss orders and price cascades"):
  executed stops feed further stops, the cascade is fast (minutes) and its effect lasts hours.
- Aggarwal & Lucey 2007 (RFE 16) and Lucey & O'Connor 2016 (FRL): psychological barriers in gold at prices ending in
  0 / 00; none in silver.
- Round 25 C (STREAM_C.md): a fresh $10 gold level broken at the M1 close continues for 60 minutes at mid in every era
  (PRE +3.50 bp t 4.86, IS +2.77 t 3.31, VAL +2.06 t 2.39), the $5 half level does not, but entering at the close of
  the bar after the break leaves only +1.0-1.1 bp net. Hypothesis of this round: a resting stop just beyond the level
  enters inside the cascade (seconds after the break), earlier than an M1 entry.
- Sides: G1 = continuation in the break direction (Osler's stop-loss cascade); G2 = fade the first touch (Osler's
  take-profit clustering). Both fixed now. G1 is the primary hypothesis; G2 is the declared opposite.
- How this differs from earlier rounds: round 25 C entered on M1 closes 1-2 minutes after the break; round 3 tested FX
  big figures at minute resolution; round 26 S rested stops around scheduled releases (clock events, not price levels);
  round 26 J faded / followed jumps (no level). No round has rested orders at price levels on ticks.

## Common rules (all cells)
- **Instruments and grids.** XAUUSD $10 levels L = 10k (primary); XAUUSD $5 half levels L = 10k + 5 (placebo);
  XAUUSD random-offset grids L = u + 10k, u ~ Uniform[1, 9], 200 draws, numpy default_rng(2027) (placebo and the
  random control); XAGUSD $0.50 and $1.00 grids; XPTUSD $10 grid (secondary / placebo instruments). With S the grid
  step: arm distance D = 0.2 S, protective-stop distance PS = 0.1 S, touch distance TOUCH = 0.05 S (gold: $2, $1,
  $0.50).
- **Data.** IC ticks (research/ticks.py format, decoded with a HOLD-asserting loader), mid = (bid + ask) / 2.
  s = s60 = median of the last-tick spread (ask - bid) of each of the 60 clock minutes before the arming minute.
- **Sessions.** NY trading days. Arming is allowed from 18:10 New York (day d-1) to 15:54 New York (day d) (so every
  position, held at most 60 minutes plus latency, is closed before 16:55 New York), never within +-15 minutes of a
  High-impact USD row of the timed calendar (r25/shared/cal/ff_events_utc.csv, cur USD, impact High, with a time),
  and never within 15 minutes after a tick gap > 60 minutes.
- **Freshness.** An upper level L (above the mid) is fresh if L > the maximum tick mid of the 1,440 clock minutes
  before the arming tick (L was not crossed in 24 hours); a lower level if L < the minimum tick mid.
- **The bot** (one bot per family x grid x offset). While flat (60 minutes after its last trigger or fill, the same
  for every exit variant, so all exits of a bot share one event set; at most one position at a time) and outside the
  exclusions, it keeps at most one resting order, on the nearest grid level within D of the mid: an upper level if
  L - D <= mid < L, a lower level if L < mid <= L + D (D < S / 2, so at most one qualifies). It arms only if L is
  fresh, the bot has not traded L in the previous 1,440 minutes, and the order is not marketable at the arming tick.
  The order price is fixed at arming. The order is cancelled when the mid leaves the band (upper: mid < L - D; lower:
  mid > L + D) or an exclusion starts; it can re-arm later under the same conditions.
- **Fill model (round 26, binding).** Server-side stops trigger when the ASK (buy) / BID (sell) reaches the stop
  price and fill at the ASK / BID of the first tick with timestamp >= trigger + latency. Latencies 0, 250, 1000 ms
  and "one tick later" (the tick after the trigger tick); **250 ms decides**. Limits fill at the limit price only
  when traded through: a sell limit when the BID is strictly above it, a buy limit when the ASK is strictly below it.
  Market exits fill at the BID (long) / ASK (short) of the first tick >= the exit clock + latency; if no tick comes
  within 10 minutes, at the last tick before the exit clock (counted and reported).
- **Exits.** Time exit h in {5, 15, 30, 60} minutes after the trigger (G1) or the fill (G2). Protective-stop variant
  ("ps"): a resting stop at the level's other side, L - PS for a long and L + PS for a short (gold $1 beyond the
  level), active from the entry tick until the exit clock, filled with the same latency; otherwise the time exit.
- **Returns.** net bp = side x (exit price - entry price) / entry mid x 1e4 - 0.6 (commission round trip, metals);
  mid (gross) bp = side x (exit mid - entry mid) / entry mid x 1e4 (mids at the fill ticks). No swap (no position
  crosses 17:00 New York). Variants: spread x1.5 (entry and exit at mid +- 0.75 x the tick's spread; a limit entry
  stays at its price) and "+1 minute" (G1: both fills 60 s late; G2: entry by market order 60 s after the limit
  fill, exit 60 s late).
- **Eras** by trigger / fill time: IS 2016-01-01..2021-12-31, VAL 2022-01-01..2024-12-31 (XPTUSD has no 2017).

## Family G1: the cascade (resting stops beyond fresh levels)
Upper level: buy stop at L + c x s, triggers when ASK >= it. Lower level: sell stop at L - c x s, triggers when
BID <= it. c in {0, 0.5, 1} (c = 0.5: the stop triggers when the mid reaches L at the typical spread; c = 0: half a
spread before; c = 1: half a spread after).

Cells per set: 3 offsets x 4 holds x 2 stop variants = **24**. Primary cell of the family: XAU $10, c = 0.5,
h = 60, no protective stop, L = 250 ms (round 25's hold, now with a resting-stop entry).

| set | definition | cells | status |
|---|---|---|---|
| G1-XAU10 | XAUUSD $10, all events (primary set) | 24 | candidate |
| G1-XAU50 | the G1-XAU10 events whose level is a multiple of $50 (dose) | 24 | candidate |
| G1-XAU100 | the G1-XAU10 events whose level is a multiple of $100 (dose) | 24 | candidate |
| G1-FIRST | G1-XAU10 events on a first touch (see below) | 24 | candidate |
| G1-REPEAT | G1-XAU10 events on a repeat touch | 24 | candidate |
| G1-XAG050 | XAGUSD $0.50 grid | 24 | candidate (secondary; the literature expects no barrier) |
| G1-XAG100 | XAGUSD $1.00 grid | 24 | candidate (secondary) |
| G1-XPT10 | XPTUSD $10 grid | 24 | candidate (secondary) |
| G1-COMEX | G1-XAU10 events triggered 12:00-16:59 UTC | 24 | **information only** (round 25 found this slice after looking) |
| G1-XAU05 | XAUUSD $5 half-level grid, all events | 24 | placebo |
| G1-RAND | 200 random-offset grids, every G1-XAU10 / dose / touch / COMEX cell | 200 x cells | placebo and random control |

First vs repeat touch: for an event on level L, let t_D be the last tick before the trigger at which the mid was
beyond D on the far side (upper: mid < L - D; lower: mid > L + D), or the session start if none. The event is a
**repeat touch** if, in the 1,440 minutes before t_D (minutes before t_D's minute), some minute's maximum tick mid was
>= L - TOUCH (upper; lower: minimum <= L + TOUCH), i.e. the price came within $0.50 of the level and was turned back
at least $2 before this approach; otherwise a **first touch**.

## Family G2: fade the first touch (resting limits just inside fresh levels)
Upper level: sell limit at L - q x s, filled at that price when BID > it. Lower level: buy limit at L + q x s, filled
when ASK < it. q in {0.5, 1, 2} (q = 0.5: filled when the mid reaches L; q = 1, 2: half and one and a half spreads
before). Exits as above from the fill time; ps = a buy stop at L + PS for the short (sell stop at L - PS for the
long). Primary cell of the family: XAU $10, q = 1, h = 60, no protective stop, L = 250 ms (latency applies to the
exit).

Sets: G2-XAU10 (primary), G2-XAU50, G2-XAU100, G2-FIRST, G2-REPEAT, G2-XAG050, G2-XAG100, G2-XPT10 (candidates,
24 cells each); G2-COMEX (information only); G2-XAU05 and G2-RAND (placebos / random control), defined exactly as for
G1 on G2's own events.

## Cell count
- Candidate cells: G1 8 sets x 24 = 192; G2 8 x 24 = 192; **K = 384**. Information only: 48 (the COMEX sets).
  Placebos: 48 ($5) plus the random-offset draws.
- Primary sets (G1-XAU10, G2-XAU10): 48 cells.
- Latency columns (0 / tick / 250 / 1000 ms) and the x1.5 / +1 minute variants are readings of a cell, not cells.

## Statistics and bars
- Per event: mean bp, t clustered by UTC day of the trigger, by era and by year; VAL / IS ratio (net and mid).
- Power: per-trade net Sharpe x sqrt(1.73 x events per year), on the IS rate and on the VAL rate; also per-day
  (daily sums of net) Sharpe x sqrt(1.73 x trade days per year).
- Random control: the same cell on each of the 200 random-offset grids, at L = 250 ms; each draw's IS (VAL) events
  are subsampled without replacement to the real cell's IS (VAL) count when the draw has more (seeded); the share of
  draws whose mean net is below the real cell's mean net, IS and VAL separately. For the silver and platinum sets
  the 200-draw control (u ~ Uniform[0.1 S, 0.9 S]) is computed only if a cell meets the t bars below.
- Placebo: the same cell on the $5 grid (and the random-offset median), reported next to every cell.
- Chance: max |t| of K independent normals (K = candidate cells with >= 10 IS events); and a sign-flip null: 1,000
  draws, one sign per UTC day shared by every candidate cell of a family, applied to the per-event IS mid return; the
  max IS mid t over the family's cells per draw gives p50 / p95. The best observed IS mid and net t are compared.
- **LIVE** (round 13, unchanged; L = 250 ms): IS net day-clustered t >= 2.5; VAL net t >= 1.5; >= 6 of 9 years
  net > 0; net > 0 in IS and VAL at spread x1.5 and at +1 minute; beats >= 95 % of the random control in IS and in
  VAL; power at the VAL rate >= 3.
- **DEMO**: IS net t >= 2.0; VAL net > 0; net > 0 at x1.5 and +1 minute in IS and VAL; beats >= 90 % of the random
  control in IS and in VAL.
- A cell whose $5 placebo is as large flags "barrier not distinguished" in the verdict.
- A family with a LIVE or DEMO cell stops and gets PREREG_DRAFT_G_<name>.md (exact rule, parameters, cell count,
  expected HOLD events and expected HOLD t on the VAL size and at 0.65 of it, the C3 daily correlation on IS + VAL).

## Fill-model checks (reported, not cells)
G1, every set, offset and latency: slippage beyond the stop (fill minus stop price, bp: median, p90); spread-only
triggers (the mid at the trigger tick + s / 2 below the stop price: the ASK reached the stop only because the spread
widened beyond its arming value; mirror for sells) and the share of triggers with a spread > 2 x s; triggers without
the mid reaching L (c = 0); double fills (none possible: one order at a time and no OCO; verified on the event list);
protective stops filled on the entry tick's latency window; effective entry delay after the trigger (ms) per latency;
exits that met a > 10 minute tick gap. G2: share of fills where the price then broke through L by PS within h (the
adverse selection of the fade).

## PRE 2004-2015 (minute level only, labelled; Dukascopy m1c)
- XAUUSD 2004-01-01..2015-12-31 (bid closes; ask closes where present, mostly 2010+); XAGUSD 2008-2015 only (sparse
  before 2008). Path mid = (bid + ask) / 2 where the ask exists, else bid + half the modelled spread. Modelled spread
  and costs: IC's 2016-17 median spread by UTC minute of day and New York DST state (round 25's convention) + 0.6 bp.
- The same bot on minute closes (bar-end time stamps): freshness on closes over 1,440 minutes; arm on the close; the
  trigger is the first later close whose ask-equivalent (mid + s / 2) reaches the stop (G1) or whose bid-equivalent
  passes the limit (G2); the same exclusions (the calendar exists from 2007; 2004-06 have no release exclusion).
- G1 entry, two readings: (a) **stop-fill approximation**: the stop price plus modelled slippage (the IS tick-level
  median slippage beyond the stop at L = 250 ms for the same set and c, bp); (b) **close entry**: the trigger close's
  ask-equivalent. G2 entry: (a) the limit price; (b) the trigger close's bid / ask-equivalent. Exit at the close of
  the minute ending at or after trigger + h, less half the modelled spread; ps on closes.
- (a) is biased upward at minute level (a crossing that reverses inside the minute is not seen). Calibration: the same
  minute-level code on IC's own minute closes 2016-24 against the tick result, cell by cell; PRE is read against that
  calibration, not alone. PRE $5 placebo and 200 random-offset draws at minute level as well.
- PRE is information (supporting or contradicting the sign); it is not one of the bars.

## Not declared (and will not become candidates this round)
Any exit, offset, distance, session or level set not listed above; selections by year or by volatility state; the
COMEX slice as a candidate.

## Addendum (2026-10-17 22:00 UTC, after the results; nothing here is a cell)
- **Bug fix, about 21:28 UTC.** The first analysis showed G2 as positive in 165 of 192 cells. The cause: the fill
  layer booked G2 on the approach side, i.e. a long bought at the sell-limit price below the market. It was fixed
  (trade side = -approach side, protective stop at L - side x PS), two synthetic tests were added, and G2 and every
  random draw were rerun. G1 numbers did not change. The declared rules are unchanged.
- **Information only, chosen after looking:**
  - the random control restricted to offsets u in [3, 7] (the draws near 0 or 10 share the real levels' cascades);
  - a $50-only bot with the tested dollar distances (`info_50only.py`);
  - side and session splits of the $50 cells.
- **The draft.** PREREG_DRAFT_G_gold_round50_cascade.md picks G1-XAU50 c0.5 h30 (no stop) among the 18 DEMO cells:
  the declared dose set, the declared primary offset, and the hold chosen after looking.
