# Round 26: information events at the tick level (stop entries at scheduled releases, unscheduled jumps)

2026-10-17 (UTC). Same task and bars as round 25 (original LIVE and DEMO bars, no RELAXED tier).
[round26_tick_events/BRIEF.md](round26_tick_events/BRIEF.md) fixed the two streams and a binding fill model at
20:04 UTC, before any round-26 number. HOLD was never loaded (asserted in both streams' tick loaders).

## Answer
- **No LIVE candidate, no DEMO candidate registered, HOLD not opened.** C3 is still the only LIVE algorithm.
- **S: a news straddle does not pay at IC.** After a resting stop triggers inside the release minute the price does
  keep going a little (gross > 0 in 208 of 336 straddle cells, +0.2 to +1.6 bp), but IC's release-minute round trip
  is 1.1-3.0 bp on FX, gold and US indices, 3.6-7.9 bp on oil and 25-57 bp on natural gas. Resting limits that try
  to catch the overshoot are picked off, worst on the biggest releases. 630 declared cells, none net > 0 in IS at the
  primary 250 ms latency except US30 straddles (+0.45 bp, t 0.59).
- **J: unscheduled jumps.** Following a jump fails everywhere. Fading a single-instrument jump is real at mid in every
  class and both eras (+0.6 to +3.5 bp, IS t up to 8.6), but below IC's 1.6-1.9 bp round trip. One corner (fading
  co-moving precious-metal jumps in the Asian session) meets the DEMO numbers but is within chance for 7,392 cells,
  goes against the declared side, and has ~2 events a year since 2018: drafted as required, **not registered**.
- Both streams re-find round 8's result at tick level: information is priced within the first minute, and what
  reverts (liquidity moves) reverts by less than the spread.

## S. Scheduled releases on ticks ([STREAM_S.md](round26_tick_events/STREAM_S.md))
Declared at 20:15 UTC in [HYPOTHESES_S.md](round26_tick_events/HYPOTHESES_S.md): S1 OCO stop straddle placed at T-2
min (k from the event type's IS median release move or fixed bp; exit T+1/3/5/15 min; with / without a protective
stop), S2a resting limits at the opposite levels, S2b a market fade at T+1 min. Sets: USD releases on AUDUSD, NZDUSD,
XAUUSD, US30, USTEC; AUD and NZD releases; EIA crude on XTI/XBR; gas storage on XNG. Fill simulator checked against
synthetic ticks and brute-force loops (4,896 cell checks, 0 mismatches).

| cell (best per family / set) | IS mid (t) | IS net L 0 / 250 / 1000 ms | VAL net 250 (t) | power IS / VAL | random / placebo | verdict |
|---|---|---|---|---|---|---|
| S1 straddle, USD pool, k 1x, 5 min | +0.97 (2.20) | -0.68 / -1.11 (-2.52) / -1.30 | -0.91 | < 0 | 0.90 / 0.01 | fails |
| S1, US30 (best S1) | +1.55 (2.03) | +0.72 / +0.45 (0.59) / +0.33 | +2.28 (1.31) | 0.31 / 0.99 | 1.00 / 1.00 | fails IS t; 5 trades make 841 of 924 bp, 4 of 9 years > 0 |
| S1, AUD releases on AUDUSD | +2.40 (2.25) | +0.67 / -0.48 / -0.49 | -1.77 | < 0 | 0.69 / 0.33 | fails |
| S1, EIA crude (XTI, XBR) | -0.64 | -7.05 / -8.43 / -9.56 | -5.86 | < 0 | - | fails |
| S2a resting limit fade, USD pool | -1.11 | -3.98 / -4.02 (-4.19) / -4.08 | -3.66 (-2.45) | < 0 | 0.01 / 0.05 | fails (picked off) |
| S2a, EIA pool | -0.07 | -9.83 / -9.96 / -10.0 | +26.6 (2.87) | IS < 0 | - | fails (VAL-only regime) |
| S2b market fade at T+1 min, USD pool | -2.57 | -4.27 / -4.31 (-2.12) / -4.28 | -3.31 | < 0 | 0.34 / 0.00 | fails (the first minute continues in IS) |

- Chance: 627 cells with >= 5 IS trades; max |t| of 627 normals p95 3.93; per-event-day sign-flip null p50 3.04,
  p95 3.99. Best declared-side IS net t: S1 +0.59, S2b +1.18 (9 trades).
- **Fill facts at IC**: with orders resting from T-2, 52-96 % of USD-release stop triggers at k <= 0.5x come before the
  number (20-52 % at 1x), so the straddle is largely a bet on pre-release drift; spread spikes alone almost never
  trigger a stop (0 % in FX, metals, indices, oil; 1-4 % gas); median slippage beyond the stop at L 0 / 250 / 1000 ms:
  NFP on AUDUSD 1.6 / 2.8 / 4.2 bp, on gold 3.7 / 7.4 / 10.2, on US30 1.0 / 1.4 / 1.8; AUD CPI on AUDUSD 3.4 / 7.1 /
  10.4; EIA on XTI 2.8 / 3.8 / 5.0.
- **Placebo days lose about as much as release days** (USD pool -1.03 vs -0.73 bp); only US30's straddle beats its
  placebo (+1.93, t 2.10), and it fails its own bars.
- Post hoc (information only, logged before it ran): stops armed only from T lift the USD-pool IS gross to +1.2-1.45
  bp (t 3.0-3.6); VAL gives it back (-0.1 to -0.9); net stays negative.
- Gas storage is not tradeable at IC: the spread is 17 bp at T-2 and 24-48 bp at the trigger.

## J. Unscheduled jumps on ticks ([STREAM_J.md](round26_tick_events/STREAM_J.md))
Declared at 20:17 UTC in [HYPOTHESES_J.md](round26_tick_events/HYPOTHESES_J.md): a jump = mid move >= k x local
1-minute sd within W s (W 10/30/60, k 6/10/16) on the 10 tick instruments, outside +-30 min of High/Medium calendar
rows and the rollover; J1 follow, J2 fade; entry 250 ms after detection (0 ms, 1 s, next tick, +60 s reported);
108 primary cells (J1 on co-moving jumps, J2 on single-instrument jumps, liquid set). Before any return, an addendum
(20:33 UTC, counts only) added a filter for fixed clock minutes the calendar misses (Shanghai day open and afternoon
reopen at 01:00 / 05:30 UTC, 21:00 Beijing, European cash opens, 07:00 New Zealand, 15:50 NY imbalance, settlement
minutes: 13-30 % of the "unscheduled" jumps), definition D2 used for verdicts, D1 reported alongside.

| cell | n IS / VAL | mid IS / VAL | net IS (t) / VAL (t), 250 ms | power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|
| J1 follow, co-move, liquid, W60 k6, 1 min | 16,070 / 5,847 | -0.12 / -0.28 | -1.59 (-29.9) / -1.22 (-12.8) | < 0 | 0 / 0 % | fails |
| best primary J1 (W60 k16, 15 min) | 489 / 132 | +1.72 / -3.92 | +0.04 / -5.02 | 0.02 / < 0 | 100 / 0 % | fails |
| J1 index co-move, W60 k16, 15 min, stop | 184 / 69 | +7.32 / -2.85 | +5.78 (2.08) / -4.46 | 1.46 / < 0 | 100 / 1 % | fails (IS only) |
| J2 fade, single, liquid, W60 k6, 1 min | 3,070 / 731 | +0.61 (8.6) / +0.33 (2.0) | -1.01 (-14.0) / -1.04 (-5.3) | < 0 | 100 / 81 % | real at mid, below cost |
| J2 fade, single, energies, W60 k16, 15 min | 242 / 40 | +17.2 (6.3) / +21.1 (2.8) | -36.1 / -18.9 | < 0 | 0 / 99 % | fails (40-55 bp spread paid) |
| J2 fade, **metals co-move, Asia, W10 k16, 15 min** | 46 / 7 | +17.87 (3.7) / +30.50 (3.6) | **+12.15 (2.60) / +18.49 (2.17)** | 1.40 / 1.65 | 100 / 100 % | DEMO numbers, within chance; draft only |

- Chance: D2 7,392 cells with >= 10 IS events, best IS net t 2.60, sign-flip null p95 2.88 (13.8 % of draws beat it);
  D1 best 2.95 against p95 2.91.
- The metals corner: x1.5 spread +9.59 / +12.79, winsorised +10.46 (t 3.37), without March-April 2020 +11.75; C3 daily
  correlation +0.014; but 37 of 53 events are in 2016-17, a protective stop kills it (+5.0, t 0.75), and a PRE check
  needs Dukascopy metals ticks. [PREREG_DRAFT_J_metals_comove_fade.md](round26_tick_events/PREREG_DRAFT_J_metals_comove_fade.md):
  expected HOLD events ~4, expected HOLD t 1.6 at the VAL size, 1.1 at 0.65, 0.4 at the 1/4 retention of picks made
  with VAL in view. **Not registered; HOLD stays closed for it.**
- Mechanism split: single-instrument jumps revert more than co-moving ones in all four classes (the liquidity story).
  A look-ahead label (a broad USD move in the panel, or US500 for indices) separates them cleanly (with it: continue
  +0.9 to +2.6 bp; without it: revert -1.1 to -3.1 bp), but once the label is known (+60 s) about 0 bp is left.
- Latency barely matters at 1-15 min (IC ticks arrive every 0.4-0.7 s); following trades do better entering a minute
  late, which skips the early reversal. Resting stops make 48 of 54 primary pairs worse; 17-27 % of stop fills in FX
  and metals come from spread widening alone (outside releases).

## What this says
- Execution cannot rescue the information channel at IC: the post-trigger continuation at releases (<= ~1.6 bp) and
  the liquidity reversal outside them (<= ~3.5 bp in the liquid set) are both real and both smaller than IC's round
  trip at those moments. The fastest a retail cTrader bot can be (250 ms) is not the binding constraint; the spread is.
- Together with round 25, the "public information" family is closed: before the release (priced), at the release
  (straddle below cost), after it (no drift, rounds 3 and 10-11), and outside releases (jumps priced within a minute).

## Needs the user
- Unchanged from round 25 (see [round25_surprises/STREAM_A.md](round25_surprises/STREAM_A.md)): IC tick pulls via the
  VPS plus Dukascopy 2004-15 for USDCNH, USDMXN, USDSGD, EURNOK, USDNOK, EURSEK; a non-cTrader platform for share CFDs.
- Low prior, named by the streams: VPS ticks for EURUSD, USDJPY, GBPUSD, USDCAD (more release slots for the straddle,
  ~1 % LIVE / 5 % DEMO by stream S's estimate; a causal tick-level USD co-move label for J); Dukascopy metals ticks
  2008-15 for a PRE check of the metals fade; a forward log of the metals fade (not recommended).

## Untested ideas (logged)
- Venue-open jumps that J's clock filter removed (Shanghai 01:00 / 05:30 UTC opens, CNY fix, European cash opens) as
  their own family; their returns were never computed.
- A straddle armed at T, declared, on data not yet seen; rolling (not fixed-IS) trigger norms; take-profit / trailing
  exits; CNY releases on AUDUSD; the VAL-only oil-overshoot reversal on EIA days (needs a new era).

## Files
- [round26_tick_events/](round26_tick_events/): BRIEF.md, HYPOTHESES_S.md, HYPOTHESES_J.md, STREAM_S.md, STREAM_J.md,
  PREREG_DRAFT_J_metals_comove_fade.md.
- Scripts: session scratchpad `r26/S`, `r26/J` (not kept).
