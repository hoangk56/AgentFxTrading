# Round 10: new directions after nine rounds (2026-10-06)

The user asked (Vietnamese) for more research into trading algorithms on the data already in `research/data/`, until
a candidate reaches the "live" bar. A negative round was not to be a stopping point; the search was to widen into
directions that explain why they could escape the limits found in rounds 3-9. The constraints: lots independent of
capital (0.5-2x around a default allowed), each position held <= 5 days, at most 3 positions per bot. Everything else
was free. The algorithm also had to be new: not gotobi or the Tokyo fix, and with low correlation to C3's daily P&L.

Five streams ran in parallel from one brief ([round10_new_directions/BRIEF.md](round10_new_directions/BRIEF.md)).
Each wrote its hypotheses, with UTC times, before the numbers they govern (`HYPOTHESES_*.md`); post-hoc additions
are marked there. The write-ups are in `STREAM_*.md`, all in [round10_new_directions/](round10_new_directions/).

| stream | direction | why it might escape the standing limits |
|---|---|---|
| A | Asian benchmarks and Chinese venue sessions (Shanghai Gold Exchange auctions, SHFE/INE opens and closes, Platts oil windows, Asian FX fixings, Nikkei SQ), with venue-holiday placebos | C3's signature is a price-insensitive flow at one known minute that disappears when the venue is shut; round 4's 19-benchmark scan had no Asian commodity or EM benchmark |
| B | central-bank decisions (8 banks, 1,877 events 2004-24) and home-market holidays, pooled across countries | events move 10-100 bp, far above cost; pooling raises the count from 8-50 to ~60-150 a year |
| C | one FX book combining the effects that are real at mid but below cost, trading only when the summed forecast clears that minute's cost | cost is paid once per trade while independent signals add; EURUSD's spread is often 0 at the minute close |
| D (lead) | feasibility frontier; sub-minute lead-lag on ticks; FX and index option pinning; the European-open "overnight drift" | round 8 measured lead-lag at M1 only; pinning and the drift were never tested as conditional / own-window rules |
| E | known fixing flows only on volatile / thin days; drift after non-US macro releases (16 types, ~130 a year) | a fixed-money flow's impact should scale with illiquidity while the fix-minute spread stays normal; only the 08:30 New York releases had been tested |

## Answer

**No candidate at either bar. Nothing was pre-registered, so HOLD (2025-01..2026-09) was not opened.**

| tier | candidates |
|---|---|
| LIVE | none |
| DEMO | none (stream A's A7 met the DEMO numbers on IS/VAL but failed its pre-written 2004-15 check, see below) |

About 620 declared cells across the streams (A 223 + 26 post hoc, B ~40, C ~156, D ~150, E 22). In every family the
best IS |t| was either at or below chance, or on the wrong side of the side fixed in advance, or below cost.

What is new and real, but too small to trade at IC's costs:
- **The Shanghai Gold Exchange morning auction moves gold.** XAUUSD rises +0.93 bp (t 7.9) IS / +0.72 (t 4.5) VAL
  in the auction minutes (02:15-02:23 UTC). It is positive in 9/9 years and absent on Chinese holidays (difference
  t 3.75), and it does not revert within an hour. The round-trip cost at that minute is 1.05-1.6 bp. The registered
  side, a gotobi-like pre-hedge V, was wrong.
- **The fix flows scale with volatility, but not enough.** The Sydney-open dip is +1.0 bp larger in the top tercile of
  realised vol (t 3.0 / 3.8), and the SGE auction +0.65 bp larger on active mornings. That is about 1.5x, and at
  Sydney the spread grows with it.
- **EURUSD rises into the ECB 14:15 CET fix**, opposite to the registered side (Krohn, Mueller & Whelan's USD-into-fix
  pattern): -0.73 bp (t -5.3 / -4.1) on the USD side. Flipped after the fact it nets +0.08 / +0.21 bp, exactly at
  cost.

## The feasibility frontier

Stream D measured, from IS 2016-21 mid returns at liquid hours, the gross edge per trade a rule needs for the LIVE
power bar. That bar is a per-trade net Sharpe of >= 0.145 at one trade a day (~430 HOLD trades) or >= 0.32 at one
a week (~90). The edge needed is cost + Sharpe x sd of the hold:

| symbol | cost, bp | 15 min: sd / need daily / need weekly | 1 h | 1 day |
|---|---|---|---|---|
| EURUSD | 0.60 | 5.4 / 1.4 / 2.3 | 10.7 / 2.1 / 4.0 | 42.6 / 6.8 / 14.2 |
| USDJPY | 0.69 | 5.2 / 1.4 / 2.3 | 10.5 / 2.2 / 4.0 | 50.1 / 8.0 / 16.7 |
| GBPUSD, AUDUSD, USDCAD, USDCHF | 0.83-0.90 | 5.4-6.9 / 1.6-1.8 / 2.6-3.0 | 2.5-2.8 / 4.3-5.3 | 7.0-9.7 / 14.5-20.3 |
| US30 | 0.86 (VAL 0.3) | 11.9 / 2.6 / 4.7 | 23.8 / 4.3 / 8.5 | 94.6 / 14.6 / 31.1 |
| DE40, US500, USTEC | 0.85-1.97 | 12.4-14.6 / 2.8-4.1 / 5.2-6.6 | 4.8-6.2 / 9.5-11.2 | 15.5-18.0 / 32-38 |
| XAUUSD | 1.31 | 9.8 / 2.7 / 4.5 | 19.7 / 4.2 / 7.6 | 84.0 / 13.5 / 28.2 |
| XAGUSD, XTI, XBR | 3.9-5.3 | 19-38 / 6.6-10.8 / 10-17 | 9.3-16.4 / 16-30 | 26-55 / 52-116 |

Full table: [STREAM_D_outputs.md](round10_new_directions/STREAM_D_outputs.md). The real intraday flows found in
rounds 3-10 are ECB fix ~1 bp, SGE auction ~0.9 bp, gold/silver settlement momentum 0.3-2.4 bp, and the Sydney V
~1.5-2.5 bp, at a minute when the spread is ~2 bp. Each sits below the line for its symbol. Gotobi is the only flow
above it. The table assumes independent trades. C3 itself has a per-leg power of 2.9, but clustered by gotobi day
its t is 3.5 IS / 2.3 VAL / 1.9 HOLD (C3's trade list was regenerated from the engine and matches the registered
numbers). So the per-trade bar is the easier of the two readings.

## A. Asian benchmarks and venue sessions

Costs at those minutes: XAU at 02:15 UTC 1.6 IS / 1.05 VAL; XAG ~4.7; XTI/XBR 2.6-7.4; FX ~0.6-0.9 bp. HOL = the same
clock on Chinese-holiday days.

| hypothesis (registered side) | where | IS mid bp (t) / VAL | HOL, diff t | net IS / VAL | verdict |
|---|---|---|---|---|---|
| A1 SGE benchmark V: long into the 10:15 Beijing auction, short after | XAU 02:15 UTC | -1.02 (-3.8) / -0.97 (-2.8) | +1.74, -4.2 | -2.6 / -2.0 | wrong sign |
| A1 flipped (diagnostic): long through the auction | XAU 02:15-02:23 | +0.93 (7.9) / +0.72 (4.5), 9/9 yrs | -0.47, 3.75 | -0.65 (t -5.4) / -0.33 (t -2.0) | real, below cost |
| A1 PM auction 14:15 Beijing; silver | XAU, XAG | \|t\| <= 2.9, wrong sign | | < 0 | fails |
| A2 long after the Chinese opens (01:00 / 12:00 / 13:00 UTC) | best XAU 01:00, 60 min | +1.19 (2.2) / +0.45 (0.6) | -1.76, 2.5 | -0.46 / -0.61 | fails |
| A2 continue the move made while the venue was shut | best XAG 12:00, 15 min | -2.93 (-4.6) / +0.53 | | < 0 | prices reverse; not repeated in VAL |
| A2 fade the 30 min before the Chinese closes | XAU 07:00 | +1.21 (3.85) / +0.86 (1.8) | +0.41, 0.7 | -0.31 / -0.17 | not venue-linked, below cost |
| A3 Platts MOC windows (Singapore 08:00, London 16:00) | XBR, XTI | in-window long VAL -3.8 (t -2.8); fades \|t\| <= 1.5 | | < 0 | fails |
| A4 Asian FX fixings: TAIFX / JISDOR 03:00, KRW / INR 06:30, TWD close 08:00, CNY 16:30 Beijing | AUDUSD, NZDUSD, USDJPY | all \|mid\| <= 1.1; best on the registered side TWD close USDJPY +0.28 (2.1) / +0.95 (3.95) | diff t 1.9 | -0.46 / +0.25 | fails |
| A5 Nikkei SQ (monthly settlement at the open), fade the first 15 min | JP225 | +5.5 (1.1) / -5.3, n 70 / 36 | | +2.5 / -7.1 | fails |
| A6 post hoc: long gold in the Chinese session | XAU 01:00-03:30 | +2.02 (2.8) / +1.70 (1.85) | -5.69, 5.6 | +0.37 (t 0.5) / +0.64 (t 0.7) | fails, power 0.35 |
| A7 post hoc: short gold 01:00-04:30 UTC on Chinese holidays (~17 a year) | XAU | +7.8 (4.3) / +7.3 (3.3) | | +6.1 (t 3.3) / +6.2 (t 2.8) | **met DEMO numbers; failed its pre-written PRE check** |

A7 in detail: 9/9 years positive; spread x1.5 +5.6 / +6.0; +1 minute +6.1 / +5.6; beats 100 % of random entries;
correlation with C3 -0.03 daily, -0.08 monthly. Its PRE criteria were written before PRE was read. Dukascopy XAU H1
2004-2015: net **-6.2 bp (t -3.3, n 206)**. The same short also "worked" on Japan-, Hong Kong-, Korea- and US-only
holidays (t -2.1..-2.8). So A7 is a blocked-day artefact of a gold market that drifted in Asian hours, not a Chinese
venue effect. It is rejected. This is the round's main methodological lesson (see Pitfalls).

Chance (per-day sign flip shared by all 223 cells, 1,000 permutations): 95th percentile of the best |t_IS| 3.61.
Observed best 6.24 (A1, wrong sign). Per family: A1 6.24 vs 2.93, A2-cont 4.61 vs 2.98 (wrong sign), A2-close 3.85
vs 2.94, A4 3.86 vs 3.40 (wrong sign), the rest below chance. Sources for the event times are in STREAM_A.md.

## B. Central-bank decisions and home-market holidays

Calendar: 1,877 events 2004-2024 from official sites, a source on each. Rule changes: FOMC 14:15 to 14:00 ET in 2013;
ECB 13:45 to 14:15 CET from 2022-07-21; BoC 09:00 to 10:00 ET in 2013; RBNZ 09:00 to 14:00 NZ in 2019; 48 unscheduled
moves excluded. ~62-66 scheduled decisions a year.

| hypothesis | where | n/yr | IS mid (t) / VAL mid (t) | cost | net IS / VAL (t) | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|
| B1 pre-decision drift, 24 h before to T-15, long (Lucca & Moench; Brusa, Savor & Wilson 2020 predict none outside the Fed) | ECB->DE40, BoE->UK100, BoJ->JP225, RBA->AUS200 | 35 | +2.1 (0.29) / -5.8 (-0.59) | 3.2 incl. swap | -1.2 / -9.0 (-0.91) | -0.09 / -0.73 | falsified, as the literature says |
| B1 home cash open to T-15 | same | 35 | +4.0 (1.07) / -1.0 (-0.17) | 1.3-2.0 | +2.0 / -2.3 | 0.28 / -0.31 | fails |
| B2 post-decision continuation (follow the first 15 min, exit 20:50 UTC) | 8 banks, currency + index | ~100 legs | +2.1 (0.64) / +1.1 (0.24) | 1.6 / 1.1 | +0.4 / +0.0 | 0.07 / 0.00 | fails; +1 min and x1.5 ~0 |
| B4a minutes releases, same rule (FOMC, RBA) | EURUSD, USDJPY, US500; AUDUSD, AUS200 | ~39 legs | -4.9 (-1.33) / +5.8 (1.48) | 1.4 / 0.8 | -6.2 / +4.9 | -1.0 / 1.1 | sign flips |
| B3 home holiday: long the home currency in its home hours on its own holidays (Breedon & Ranaldo home-hours depreciation) | 7 USD pairs, 8 calendars | ~90 legs, ~35 blocks | +2.6 (1.72; by block 1.79) / -1.8 (-0.71) | 1.2 / 1.0 | +1.4 (0.95 by block) / -2.8 | 0.75 / -1.4 | fails; holiday minus normal day PRE +3.9 (t 2.4), IS +2.7 (1.8), VAL -1.6 |
| B2r post hoc: fade the first 5 min of a press conference, exit after 60 min | FOMC, ECB, BoE, RBNZ, SNB | ~45 legs | +4.5 (1.55) / +9.8 (1.89) | 0.9 / 0.7 | ~+3.5 / ~+9.1 | ~0.7 / ~1.4 | same sign in PRE (+3.9, t 1.3), but IS t < 2 and post hoc: below DEMO, cannot be registered |

For the LIVE bar these mechanisms would need a per-event net Sharpe of 0.29 (B2) to 0.39 (B1). The best pooled cell
reached 0.06. Chance: B2 best |t| 1.99 against a per-day null median of 2.0 (95th percentile 2.98). Detail, including
per-bank splits and a note that BoJ release times detected from the data are loose, in STREAM_B.md. The calendar
(`scratchpad/r10/B/calendar/`) is reusable.

## C. A cost-gated FX book of sub-cost effects

10 FX pairs, a decision every 15 min (00:00-20:45 UTC plus the Sydney open), fill at t+1 with the actual spreads at
entry and exit plus 0.6 bp, all trades closed by 20:55 UTC. Eight causal components with signs fixed from earlier
rounds:
- residual / currency-strength reversal;
- a lagging USD pair catching up with the dollar factor;
- the ECB and WM/R fixing V;
- home-hours depreciation;
- carry into the Wednesday rollover;
- the Sydney-open V;
- adaptive same-slot periodicity.

Nothing uses the Tokyo fix.

| hypothesis | chosen on IS | IS mid / VAL mid, bp (t) | net IS / VAL, bp (t) | trades/yr | power IS / VAL | verdict |
|---|---|---|---|---|---|---|
| C1 equal-weight z-sum, trade when \|sum\| > k x cost / sd | h 15, k 128 | +0.68 (1.2) / +0.13 (0.2) | -0.25 / -0.67 | 162 / 560 | -0.33 / -1.50 | fails |
| C2 ridge composite fit on IS | h 240, k 3 | +1.65 (0.5) / +2.04 (0.8) | +0.57 (0.18) / +1.27 (0.5) | 93 / 249 | 0.14 / 0.59 | fails (IS t) |
| C4a dollar factor traded in the cheapest USD pair | h 240 | +1.63 (2.7) / -0.02 | +0.99 (1.65) / -0.66 | 289 / 460 | 0.87 / -0.54 | fails (best IS t of the stream) |
| C4b one bot, cap 3, pairs ranked by forecast / cost | h 240, k 3 | +1.11 (0.4) / +3.24 (1.6) | +0.07 / +2.49 (1.2) | 79 / 215 | 0.02 / 1.11 | fails (IS) |
| C5 each component alone at the cheapest minutes (zero spread, high tick count) | Sydney h 15 | +1.01 (2.4) / +0.38 (0.9) | -0.17 / -0.55 | 67 / 132 | < 0 | fails |
| C6 post hoc: C1/C2 in EURUSD + USDJPY only | C1 h 60 | +0.87 (2.7) / -0.11 | +0.18 (0.6) / -0.77 (-1.9) | 374 / 847 | 0.29 / -1.46 | fails |

Why it fails:
- **Commission is the floor.** The components that are real at mid (residual reversal +0.020 bp per z unit at 15 min,
  t 4.3 / 2.5; dollar catch-up +0.043, t 5.3 / 3.2; periodicity +0.078, t 6.8 / 2.6; Sydney +0.342, t 8.4 / 4.9)
  forecast under 0.5 bp together outside the Sydney open, even at a z of 3. The commission alone is 0.6 bp.
- **The edge is in the busy minutes.** Trading only at zero-spread, high-activity minutes cuts the cost to
  0.72-0.80 bp, but the mid edge disappears at those minutes (residual reversal +0.10 -> -0.02 bp).
- **Break-even commission.** The C2 15-minute cell would break even at a commission of 0.15 bp (IS), against 0.6.
- **A cost gate beats random entries by construction.** For cost-gated rules, beating the random-entry control means
  little: C1 beats 100 % of random seeds in IS while losing money.
- **Chance.** About 156 trading cells; the best IS t in every family is below the per-day null's median best.

## D. Lead's screens

| hypothesis (registered side) | where | result | verdict |
|---|---|---|---|
| sub-minute lead-lag, 1-second grid, delay 1-5 s, leader moves \|z\| >= 4-8 (2019, IS) | USTEC -> AUDUSD; USTEC -> US30 | AUDUSD +0.1..+0.4 bp (t 2-3) against 0.37 bp spread + 0.6 bp commission; US30 +0.1..+0.4 against 1.2 bp spread | below cost, rejected |
| D1 FX option pinning: toward the nearest 50-pip level 09:01-09:59 New York when within 5-25 pips at 09:00; away after the 10:00 cut | 6 USD pairs, ~1,800-9,300 IS events | pre-cut mid -0.45..+0.13 bp (\|t\| <= 1.4) IS, -0.31..+0.57 VAL; post-cut \|t\| <= 1.0; the same rule at 07:00 and 12:00 New York looks the same; net -0.6..-1.4 bp | no pinning |
| D2 index pinning into the 16:00 ET close on expiry days (Fridays; every day from 2022-05) | US500 (25-point levels), USTEC (100), US30 as a no-option control | US500 IS -9.3..+0.0 bp (t >= -1.3), VAL -1.6..+0.6; USTEC IS -5.3..-2.0, VAL +1.2..+1.7 (t <= 0.9); US30 the same | no pinning |
| D3 "overnight drift" at the European open, long 02:00-03:00 ET (Boyarchenko, Larsen & Whelan 2023), unconditional and after a late-day sell-off | US30, USTEC (US500 and DE40 for information only) | US30 +0.51 bp (t 1.2) IS, -0.36 VAL; USTEC +0.81 (1.7) / +0.12; cost at 02:00 ET 1.2-3.5 IS, 0.3-1.2 VAL; only 2020 clearly positive | gone after 2019, rejected |

## E. Size-conditioned fixing flows; non-US macro releases

Conditioning (fixed in advance): the top tercile of the causal 20-day realised vol, or of pre-window activity. The
Tokyo fix was excluded.

| hypothesis | where | IS mid bp (t) / VAL | cost | net IS / VAL | verdict |
|---|---|---|---|---|---|
| E1 USD long into the ECB 14:15 CET fix, volatile days | EURUSD | -0.68 (-1.9) / -0.87 (-2.0) | 0.65 | -1.33 / -1.50 | wrong sign (EUR rises into the fix) |
| E1 USD short after the ECB fix | EURUSD | +0.19 / +0.24 | 0.8 | -0.71 / -0.49 | fails |
| E1 WM/R 16:00 London, into / after | EURUSD, GBPUSD | best +0.23 / +1.43 (2.9) | 0.7 | -0.49 / +0.77 | flips between eras |
| E1 SGE auction, active mornings (side from stream A's data) | XAU 02:15-02:23 | +1.31 (4.9) / +1.02 (3.3) | 1.35 | -0.21 / -0.04 | real, just below cost |
| E1 USDJPY long 17:01-18:00 New York | USDJPY | -0.41 / -0.93 | ~1.9 | -2.1 / -3.1 | fails* |
| E1 Sydney dip, short AUD/NZD 09:45-10:00 Sydney, volatile days | AUDUSD, NZDUSD | +2.52 (5.9) / +2.12 (7.2) | 2.0-2.3 | +0.69 (1.7) / -0.62 (-1.9) | fails VAL |
| E1 Sydney rebound, long 10:00-10:15 | same | +0.88 / +2.40 (5.1) | 1.7 | -0.67 / +0.52 | fails |
| E2 follow the first 5-min reaction to non-US releases for 120 min (Evans & Lyons 2005), primary | 7 home pairs, 1,167 events | +0.04 (0.05) / -0.69 (-0.7) | ~0.9 | -0.88 / -1.56 | fails |
| E2 same, 30 min, large reactions only | same | +1.21 (1.3) / +2.09 (2.4) | ~0.9 | +0.31 (t 0.33) / +1.15 (1.31) | fails (IS t 0.33; +1 min IS -0.12); C3 corr 0.01 daily |

\* Round 4's "+0.8 bp in the hour after the NY close" was the 16:00 cash close, not the 17:00 FX close. This row tests
the 17:00 close, which is wide-spread and negative.

Release calendars: 16 types 2016-24, ~130 events a year, official sources only, built without looking at prices. The
UK, Swiss and ZEW release-time changes are applied per event. Flash PMIs were dropped (no official archive). E2 best
|t_IS| 1.32 against a null 95th percentile of 2.61. Per-type splits flip between eras. USDCAD's large-reaction cells
(+3.3 / +3.8 net, t ~1.4) partly repeat the US 08:30 effect.

## What this says

- **The binding constraint is now quantified.** For one trade a day, a rule needs about 1.4 bp gross per 15 minutes
  in EURUSD/USDJPY, 2.6 in US30, 2.7 in gold. Every real flow found in ten rounds sits below that, except gotobi.
  In FX the floor is the 0.6 bp commission, not the spread: zero-spread minutes do not rescue an effect, because
  the effects live in the busy minutes.
- **Venue-linked flows exist where no one had looked** (the SGE auction), and they behave like flows: absent when
  the venue is shut, larger on active days. But they are a fraction of a basis point after cost.
- **Rare scheduled events have no pooled premium.** Neither pre-decision drift nor post-decision continuation shows
  up across eight central banks, nor follow-through after non-US data. Information is priced within minutes, as it
  was for the 08:30 New York releases. The one consistent sign (fading the first minutes of a press conference) was
  found after looking and is below the DEMO t.
- **Combining sub-cost signals does not clear the floor.** They are nearly uncorrelated, but their summed forecast
  outside the Sydney open stays under the commission.
- **Standing: unchanged.** C3 remains the only algorithm that has passed. Ten rounds now agree: on IC's cost structure
  and these 26 + 6 symbols, the effects that exist outside gotobi are smaller than one round trip, or too rare for
  the holdout.

What could still change this. None of it is screening of the same data, and each needs the user's decision:
1. **More instruments in the same broker.** IC's cTrader lists many symbols the repo has never pulled: about 60 FX
   pairs (crosses such as EURGBP / EURCHF / AUDNZD, Scandinavian and EM pairs with their own fixes), more indices,
   soft commodities. Pulling them needs throwaway backtest containers on the VPS (the classifier denied that in
   round 7). Dukascopy's free feed, reachable from this Mac, has most of them for a first screen, but they would
   then need IC's own costs.
2. **New holdout data.** Every day after 2026-09-24 is unseen. Dukascopy serves it now; IC's cache needs a pull. It
   adds ~250 days a year. Only a strong effect could use it soon; for the demo-tier ideas, the demo account itself
   is the holdout.
3. **A cost structure without the 0.6 bp floor.** For example an account type without per-lot commission, or index
   CFDs, which cost 0.3 bp in US30 since 2022. The sub-cost FX components of stream C would break even at about
   0.15 bp commission.

## Pitfalls (for the next round)

- **Holiday tests must cluster by holiday block, and use other countries' holidays as the placebo.** Holidays come in
  multi-day blocks, so clustering by day overstates t. A7 passed IS/VAL (t 3.3 / 2.8, 100 % of random entries) and
  failed 2004-15 at t -3.3. The same trade worked on unrelated countries' holidays.
- **Rerun a conditional side at every shift of a time placebo.** If the side is conditional, it must be recomputed
  at each shifted time. Reusing the unshifted side made the window overlap the signal and gave spurious |t| up to 34.
- **A cost gate beats random entries by construction.** For cost-gated rules, the random-entry control rewards the
  gate itself, not the forecast.
- **Causal vol terciles drift with the regime.** In 2022 volatility left its trailing range: 36 % of VAL days fell in
  the top tercile, against 22 % of IS days.
- **Check the clock time a "close" refers to.** Round 4's NY-close line meant 16:00 ET, not 17:00.
- **Oil quotes on Good Friday are IC artefacts.** On Singapore/UK holidays (often Good Friday) IC's oil quotes show
  -14 to -24 bp means while ICE/NYMEX are shut.

## Process and disclosures

- **HOLD stayed closed.** The shared panel ends 2024-12-31, M1/tick loads were cut at 2025-01-01, PRE is 2004-2015.
  No stream printed a 2025-26 return. C3's own trade list (2016-2026) was regenerated from the unchanged engine
  (`trades_C3_gotobi_jpy_basket.csv`, git-ignored, identical to the registered numbers) and used only for
  correlations on IS+VAL.
- **Network.** Event calendars came from official sites. These were the SGE, Platts methodology, FBIL, the central
  banks, and the statistics agencies ONS, Destatis, ABS, StatCan and Eurostat. Holidays came from the `holidays`
  package in a scratch venv. Literature came from scholarly APIs. No prices were downloaded.
- **Code.** The screens are scratch scripts, as in rounds 3-9. Kept in the round folder:
  - the brief and the five hypothesis files;
  - the four stream write-ups;
  - the lead's scripts and outputs (`D_*.py.txt`, `STREAM_D_outputs.md`).

  The streams' scripts, calendars and outputs stay in the session scratchpad. They are listed in each STREAM file.
  Nothing in `research/` code was edited. No pre-registration was written, so `prereg_hashes` was not needed.
- **Correlation with C3** was computed for the two cells that were net > 0 in both eras:
  - A7: -0.03 daily, -0.08 monthly;
  - E2 large-reaction cell: 0.01 daily, -0.02 monthly.

  Neither is a candidate.
