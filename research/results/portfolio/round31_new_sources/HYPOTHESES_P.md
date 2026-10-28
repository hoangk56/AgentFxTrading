# Round 31, stream P: practitioner and community strategies, declared hypotheses

Declaration written 2026-10-27 18:27-18:28 UTC (`date -u` at start: 18:26:48 UTC; file saved 18:28:01 UTC; the first
return, P2's, was computed at 18:29:05 UTC), **before any return of any cell below was computed**. At this point no price file has been opened by this stream. Brief:
[BRIEF.md](BRIEF.md) row P; round13_structural/BRIEF.md for costs, fills, controls and bars. HOLD (2025-01-01 onward)
is cut at load in every script (`ts < 1735689600000`, tick days `< 2025-01-01`).

## Step 1: census (done 18:13-18:26 UTC; the full table is in STREAM_P.md)
Sources fetched (log: scratchpad `r31/P/web/requests.log`): Quantpedia free screener (82 free strategies) and its
1,176 blog-post slugs; QuantConnect Strategy Library (84 strategies, via GitHub QuantConnect/Tutorials); GitHub
(topic and keyword searches; EA31337-strategies 70 indicator strategies; freqtrade-strategies 66 files;
je-suis-tm/quant-trading 17 strategies; smart-money-concepts (ICT/SMC); GeneralTradingSarl/mql4_experts, 1,125 MQL4
EAs from the Russian-born mql5 code base; vnpy CTA strategies; Chinese keyword searches); the mql5.com Market
(70 top MT5 EAs listed, 20 product pages read); GogoJungle (Japan's EA market, genre counts); 2 web searches for
TradingView's most used public scripts (its robots.txt disallows /scripts/*, so no script page was fetched) and the
QuantConnect forum. Almost every entry is a chart pattern, a published factor premium already mapped (rounds 2-25), or
a genre already tested (ORB / London breakout / ICT Judas sweep in the September lab; early-morning scalpers = round
23 N1 reopen-gap fade; CME gap fill = round 4; WTI/Brent and gold/silver spreads = round 8; Monday dip = round 25 MON;
grid / martingale = round 5; news straddles = round 26).

**What is left with an economic basis and no earlier test:**
1. The dominant commercial gold-EA design on the mql5 Market in 2026 (Lizard, Dynamic Liquidity Intelligence, Range
   Breakout EA, Gold Reaper, Ghost Scalper, Ultimate Breakout System, Prop Firm Gold EA): **resting buy-stop /
   sell-stop orders just beyond visible extremes (prior-day, swing, Asian-session high / low) in gold, following the
   break.** The economic basis is stop-loss clustering beyond widely watched extremes and the cascade when they fill
   (Osler 2005; the same mechanism round 27 found for fresh $50 levels in gold). Rounds 27-28 tested round-number
   levels only; the September lab tested ORB / London breakout with stops at the range's other side held to the
   session end (2023-26 only), not the short cascade at prior-day / prior-week extremes.
2. FX practitioner lore (Kathy Lien-style "Friday position squaring"; prop-firm rules that force flat books before the
   weekend): **leveraged traders square trend-aligned positions on Friday afternoon, so the week's move partly
   reverses into the Friday close.** No round conditioned a Friday-afternoon trade on the week-to-date move (round 25
   MON looked at Monday after Friday; rounds 2/7/11 at unconditional 1-5-day reversal).

## Power arithmetic before building (frontier: round 10 STREAM_D_outputs, round 16 STREAM_X)
- Gold 30-minute trades after a break: sd about 30-35 bp per trade (round 27 VAL: net +3.27 bp at per-trade Sharpe
  0.093 -> sd ~35). Cost: 0.6 bp commission + half spreads + stop slippage, ~1.0-1.7 bp in IS, ~0.8-1.2 in VAL.
- **P1-PD** (~1 break a day, ~200-250 trades a year): LIVE power 3 needs per-trade Sharpe >= 3 / sqrt(1.73 x 225) =
  0.15, i.e. **net >= ~5 bp (mid >= ~6 bp)**, as large as round 27's $50 levels. DEMO (IS t >= 2 over 6 years at
  ~1,300 trades) needs net >= ~1.9 bp. A priori: P(LIVE) ~3-5 %, P(DEMO numbers) ~10-15 %.
- **P1-PW** (~1-1.5 breaks a week, ~60 a year): LIVE needs Sharpe 0.29 (net ~10 bp): out of reach; DEMO needs net
  >= ~3.5 bp.
- **P1-AR** (~1 a day): as P1-PD; near-tested (lab London breakout, negative), prior lower.
- **P1-X** (the P1-PD rule on silver, US30, USTEC, AUDUSD, NZDUSD; round 28 found no round-level cascade outside gold):
  replication only; prior near 0.
- **P2** (Friday squaring): 11 symbols, top tercile -> ~190 trades a year on ~40 Fridays; the unit is the Friday
  (symbols share the USD leg). 7-hour sd ~25-35 bp FX, ~45 gold, ~55 indices. LIVE needs a per-Friday net Sharpe
  >= 3 / sqrt(1.73 x 40) = 0.36; DEMO needs IS t >= 2 over ~240 Fridays, a per-Friday Sharpe >= 0.13. At typical
  cross-symbol correlation this means **>= ~4-6 bp net per trade for DEMO and ~12-15 bp for LIVE**. A priori:
  P(LIVE) ~2 %, P(DEMO numbers) ~10 %.

## Common rules (all cells)
- Eras: IS 2016-01..2021-12 (thresholds chosen here only), VAL 2022-01..2024-12, PRE 2004-15 (Dukascopy) where stated.
- Sides are fixed below from the sources; nothing is chosen on IS except the P2 tercile threshold (a quantile of
  |WTD|, not a side).
- t clustered by UTC day of entry (P2: by Friday). Per-trade Sharpe and power = Sharpe x sqrt(1.73 x trades/yr) at
  the IS and VAL sizes. Spread x1.5 and +1 minute (both fills) for every cell. Years net > 0.
- Chance: K = 6 primary cells (P1-PD, P1-PW, P1-AR, P1-X, P2-top, P2-all); max |t| of 6 normals, median ~1.6 /
  95th ~2.6, plus each family's own placebo.
- C3 correlation (daily, monthly; IS + VAL) for any cell with IS net t >= 2.

## P1: gold stop cascades beyond prior-day / prior-week / Asian-range extremes (follow the break)
Source: mql5 Market gold EAs listed above (product pages 172541 Lizard, 169976 Dynamic Liquidity Intelligence, 122237
Range Breakout EA, 111357 Gold Reaper, 189922 Ghost Scalper, 153540 Prop Firm Gold EA); Osler (2005) for stop
clustering; round 27 for the construction. Side: **follow** (buy stop above the high, sell stop below the low), as the
sources trade it.

Rule (one bot per cell; IC XAUUSD ticks, mid = (bid+ask)/2):
- NY session d = [18:00 NY of d-1, 17:00 NY of d), weekdays only. A session needs >= 300 minutes with ticks or it is
  skipped (and cannot provide a level).
- Levels:
  - **PD**: H / L = max / min tick mid of session d-1 (the previous valid session).
  - **PW**: H / L = max / min tick mid of the previous NY week's sessions (Mon-Fri); live for every session of the
    current week; one trade per level per week.
  - **AR**: H / L = max / min tick mid between 00:00 and 06:59:59 UTC inside session d; armable from 07:00 UTC.
- Freshness: a level is eligible only while the session's (PW: the week's) running max mid is below H (running min
  above L). Once the mid has reached the level it is dead for that session (week), traded or not.
- Arming window: 18:10 NY (d-1) .. 15:54 NY (d) (AR: 07:00 UTC .. 15:54 NY). Excluded (order cancelled, re-armed
  after): +-15 min around 08:30, 10:00 and 14:00 NY on every weekday (a calendar-free stand-in for round 27's
  High-impact USD exclusion, whose ForexFactory file no longer exists), and 15 min after a tick gap > 60 min.
- Order: buy stop at H + 0.5 x s60, sell stop at L - 0.5 x s60; s60 = median of the M1 last-tick spreads (ask close
  - bid close) of the 60 minutes before the arming minute, fixed at arming. Armable only if not marketable at that
  tick. Trigger: first tick with ask >= buy stop (bid <= sell stop) while armed. One trade per level per session
  (PW: per week). Both sides may trade in one session. No protective stop.
- Fill: entry at the ask (buy) / bid (sell) of the first tick >= trigger + 250 ms; exit at market (bid for a long,
  ask for a short) at the first tick >= trigger + 30 min (round 27's registered hold; not re-chosen). Exit ticks more
  than 10 min after the target time are flagged and reported.
- Net bp = side x (exit - entry) / mid_trigger x 1e4 - 0.6 (commission). Mid bp = side x (mid_exit - mid_trigger) /
  mid_trigger x 1e4. Variants: latency 0; +1 minute (both fills 60 s late); spread x1.5 (half spreads at entry and
  exit x1.5).
- **P1-X**: the P1-PD rule unchanged on XAGUSD, US30, USTEC, AUDUSD, NZDUSD (IC ticks); commission 0.6 bp for
  XAG / FX, 0 for indices; pooled per trade in bp, plus per symbol.
- Placebo (the declared random control, 200 seeds): the same engine with each session's two levels replaced by
  random levels: close of session d-1 +- U(0.25, 1.0) x (H - L of session d-1), freshness and side rule unchanged
  (P1-PW: the week's close +- the same fraction of the week's range; P1-AR: the 06:59 UTC mid +- the fraction of the
  Asian range). Report the share of seeds whose net mean the real cell beats.
- Overlap with round 27: P1-PD / P1-PW trades whose level is within $5 of a multiple of $50 are counted and the cell is
  also reported without them (information).
- PRE (P1-PD only): Dukascopy XAUUSD m1c 2004-15 with a minute fill model: trigger minute = first minute whose bid
  high + spread estimate >= the buy stop (bid low <= the sell stop); entry at the stop price (or the minute's open if
  it gapped through); exit at the M1 close 30 minutes later; cost = IC 2016-17 spread profile by minute of day + 0.6
  bp. The minute model is first compared with the tick engine on IS gold and that gap is reported.

## P2: Friday position squaring (against the week-to-date move)
Source: FX practitioner lore of Friday profit-taking / position squaring before the weekend (e.g. Kathy Lien, "Day
Trading and Swing Trading the Currency Market"; DailyFX / BabyPips "Friday reversal" articles) and prop-firm weekend
rules (no weekend holding on standard accounts). Side: **against** the week-to-date move.

Rule:
- Symbols: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, XAUUSD, US500, US30, USTEC (IC M1).
- WTD = ln mid(close of the M1 bar labelled 12:59 UTC Friday) - ln mid(close of the first M1 bar at or after Monday
  00:00 UTC of the same week). Mid = (bid close + ask close) / 2.
- Entry at the close of the bar labelled 13:00 UTC (one minute after the signal), side = -sign(WTD): buy at ask close,
  sell at bid close. Exit at the close of the bar labelled 19:59 UTC (before the US cash close in summer and IC's
  rollover). No swap.
- **P2-top (primary)**: only when |WTD| >= that symbol's 66.7th percentile of |WTD| over IS Fridays (fixed on IS,
  applied unchanged to VAL and PRE). **P2-all**: every Friday.
- Cost: half the actual spread at entry + exit (bar's ask close - bid close) + 0.6 bp for FX and gold; 0 for indices.
- Pooled equal weight per trade in bp; t clustered by Friday; per symbol and per class (FX / gold / indices) reported.
- Random control (200 seeds): each trade replaced by the same symbol on a random Monday-Thursday of the same week, same
  13:00 -> 19:59 UTC clock, side recomputed as -sign(return from Monday 00:00 UTC to that day 12:59 UTC) with the same
  threshold rule (P2-top: same symbol threshold).
- PRE 2004-15: Dukascopy M1 bid for EURUSD, USDJPY, USDCHF (m1), AUDUSD, NZDUSD, XAUUSD (m1c); cost = IC 2016-17 median
  spread of the symbol at 13:00 and 19:59 UTC + 0.6 bp. Threshold = the IS one.
- Information (not a cell): a Thursday version (same clock) as a same-construction placebo; Fridays before US
  3-day weekends.

## Stopping rule
A family meeting LIVE or DEMO numbers on IS / VAL stops and gets a PREREG_DRAFT_P_<name>.md; HOLD is not opened.
Post-hoc rows, if any, are marked as such and added below with their time before their numbers.

## Post-declaration additions (information only; none is a cell or changes a verdict)
- 2026-10-27 ~18:36 UTC, after the P1 gold numbers: an engine check, "R50" = the nearest $50 multiples beyond the
  previous session's extremes run through the same P1 engine, to confirm the engine finds round 27's known gold $50
  cascade (it is an approximation of round 27's G1-XAU50, not a new rule).
- Splits printed by the report scripts after the numbers (by break side, per symbol of P1-X, per class of P2, ex
  March-April 2020, ex levels within $5 of a $50 multiple, Wednesday / Thursday placebos) are information only.
