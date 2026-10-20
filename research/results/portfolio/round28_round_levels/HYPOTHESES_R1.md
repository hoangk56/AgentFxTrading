# Round 28, stream R1: the round-level cascade on the major round levels of the IC tick symbols (declared before numbers)

**Written 2026-10-17 22:26 UTC (`date -u` 22:26:23), before any return of any kind was computed in this stream.**
Brief: [BRIEF.md](BRIEF.md) (stream R1); the rule generalises round 27 G's G1-XAU50 cell
([../round27_levels_opens/PREREG_DRAFT_G_gold_round50_cascade.md](../round27_levels_opens/PREREG_DRAFT_G_gold_round50_cascade.md));
binding tick fill model of round 26; bars of round 13. Nothing below was tuned on returns.

HOLD (2025-01-01 onwards) is never loaded:
- every tick day requested is asserted < 2025-01-01 and every loaded tick < 2025-01-01 00:00 UTC;
- the last NY session used ends 2024-12-31 17:00 New York;
- Dukascopy data is cut at 2016-01-01;
- the C3 file, if read, is read for its IS / VAL rows only.

What was looked at before this declaration (prices only, no price differences turned into returns):
- tick density, spreads and quote gaps on 3 days a year per symbol (`code/peek.py`);
- the per-minute tick envelopes (`code/build_minutes.py`, the round-27 builder; gold reuses round 27's file);
- the event lists of the declared real-grid bots without any fill or exit (`code/run_events.py SYM count real`), and
  their counts by year and cell (`out/count_summary.txt`, table below);
- the number of major events whose exit clock would pass 16:54 New York (below);
- the lowest oil quote in March-May 2020: XTIUSD 3.45 (2020-04-21), XBRUSD 15.55. IC's oil never went negative.

Facts from those looks:
- **Daily halts.** US30 and USTEC stop 16:15-16:30 New York until 2021 and 17:00-18:00 New York every day. Gold stops
  ~17:00-18:00 New York (61-65 minutes). Oil has many 5-13 minute quote holes in Asian hours. FX has no daily halt.
- **IC data hole.** All symbols have a 30-minute hole at 2023-03-08 00:10 UTC.
- **Median spreads (bp).**
  - US30: ~1.0 in 2018-20, 0.3 in 2022-23, 0.15 in 2024.
  - USTEC: 2-5 in 2016-19, 1.3-1.7 in 2020-22, 0.3-0.8 in 2023-24.
  - XTIUSD / XBRUSD: 4-12 (0.03-0.04 USD). XBR is 1.2 from 2023-11 on.
  - AUDUSD: 0-0.5, plus 0.6 commission. NZDUSD: 0.3-1.0, plus 0.6.
  - Gold: 0.2-1.3, plus 0.6.

## The rule as implemented (identical for every symbol; `code/engine.py`, `code/fills.py`)
- **Data and units.**
  - IC ticks, mid = (bid + ask) / 2.
  - s60 = the median, over the 60 clock minutes before the arming minute, of each minute's last-tick spread
    (minutes without ticks are skipped; carried forward if the hour had none).
  - b = 0.0015 x mid, evaluated at each tick.
- **Grid.** Minor levels L = m x j. Major levels: j a multiple of M / m. Super levels: j a multiple of sup / m. The
  spacings are the BRIEF's:

  | symbol | IS median (BRIEF) | minor m / MAJOR M / super | b at the IS median | M / m | commission (bp round trip) | calendar currencies | class |
  |---|---|---|---|---|---|---|---|
  | XAUUSD | 1,324 | 10 / **50** / 100 | 1.99 | 5 | 0.6 | USD | gold |
  | AUDUSD | 0.7372 | 0.01 / **0.05** / 0.10 | 0.00111 | 5 | 0.6 | AUD, USD | FX |
  | NZDUSD | 0.6894 | 0.01 / **0.05** / 0.10 | 0.00103 | 5 | 0.6 | NZD, USD | FX |
  | US30 | 25,367 | 500 / **1,000** / 5,000 | 38.1 | 2 | 0 | USD | US indices |
  | USTEC | 7,301 | 100 / **500** / 1,000 | 11.0 | 5 | 0 | USD | US indices |
  | XTIUSD | 59.17 | 0.5 / **1** / 5 | 0.089 | 2 | 0 | USD | oil |
  | XBRUSD | 65.23 | 0.5 / **1** / 5 | 0.098 | 2 | 0 | USD | oil |

  2b < m holds at every price these symbols reached in 2016-24, so at most one level is in the band at a time.
- **Sessions and exclusions** (arming-allowed mask; an armed order is cancelled when the mask turns off).
  - Arming is allowed from 18:10 New York (day d-1) to 16:55 New York (day d); 16:55-18:10 New York is excluded.
  - Never within +-15 minutes of a High-impact calendar minute of the symbol's currencies (table above), from
    r25/shared/cal/ff_events_utc.csv (rows with a time).
  - Never within 15 minutes after a quote gap > 60 minutes. The gap is measured on the whole tick stream, including
    the last tick before the session window.
  - No JPY pair is in this stream.
- **Freshness.** An upper level L (above the mid) is fresh if L > the highest tick mid of the 1,440 clock minutes before
  the tick (the previous 1,440 whole minutes plus the earlier ticks of the current minute); a lower level if L < the
  lowest. Clock minutes, as in round 27: after a weekend or holiday close the window holds only the hours since the
  reopen. This is part of the declared rule (round 27's gold numbers were produced this way).
- **The bot** (one per symbol and grid; at most one resting order and one position).
  - When it arms: only while flat, i.e. >= 60 minutes after its last trigger on any level of the symbol, and inside
    the arming mask.
  - Which level: the nearest minor level within b of the mid. An upper level needs L > mid, L - mid <= b and L
    fresh; a lower level needs L < mid, mid - L <= b and L fresh.
  - Further conditions: L has not triggered in the previous 1,440 minutes, and the order is not marketable at the
    arming tick.
  - The order: upper level, a buy stop at L + 0.5 x s60 (triggers when ASK >= it); lower level, a sell stop at
    L - 0.5 x s60 (triggers when BID <= it). The price is fixed at arming.
  - Cancel when the mid leaves the band (upper: L - mid > b; lower: mid - L > b) or the arming mask turns off. At
    the same tick the cancel takes priority over a trigger, as in round 27. The bot can re-arm later.
  - Every trigger, at a minor or a major level, starts the 60-minute busy window and blocks its level for 1,440
    minutes.
  - **A trade is taken only when L is a major level.** Triggers at minor-only levels are measured with the same
    fills as the "minor" dose cell; they are not traded.
- **Fills** (round 26, binding).
  - Entry: a buy fills at the ASK and a sell at the BID of the first tick with timestamp >= trigger + latency.
    Latencies: 0 (the trigger tick), 250 ms, 1,000 ms, and "next tick" (the tick after the trigger tick).
    **250 ms decides.**
  - Exit: a market order at X = min(trigger + h, 16:54 New York of the session), filled at the BID (long) / ASK
    (short) of the first tick >= X + latency ("next tick": one tick after the first tick >= X).
  - If no tick comes within 10 minutes, the exit is at the last tick before X (counted). The exit is never before the
    tick after the entry fill. Positions never cross 17:00 New York, so no swap.
  - Clamped exits (major events whose exit clock passes 16:54 New York) are kept and counted: XAU 3 / 475, AUD 1 / 148,
    NZD 1 / 127, US30 3 / 476, USTEC 7 / 462, XTI 17 / 1,752, XBR 18 / 1,778 at h = 30.
- **Returns.**
  - net bp = side x (exit price - entry price) / entry mid x 1e4 - commission (0.6 bp FX and gold; 0 indices and oil).
  - mid (gross) bp = side x (exit mid - entry mid) / entry mid x 1e4, at the fill ticks.
  - Variant "spread x1.5": entry and exit at mid +- 0.75 x the tick's spread, at the 250 ms fill ticks.
  - Variant "+1 minute": both fills 60 s late (entry at the first tick >= trigger + 60 s, exit at the first tick
    >= X + 60 s).
- **Eras** by trigger time: IS 2016-01-01..2021-12-31 (oil 2018-01-01..2021-12-31: 4 years), VAL
  2022-01-01..2024-12-31. PRE 2004-15 at minute level for XAUUSD only in this stream (below).
- **Side.** The direction of the break (continuation), from the source (Osler 2003 / 2005), not from our data.

## How the gold rule differs from round 27's draft (G1-XAU50 c0.5 h30)
1. **Band.** 0.15 % of the mid instead of a fixed $2. Gold traded $1,050-2,790 in 2016-24, so b = $1.6-4.2: wider in
   2020-24, narrower in 2016.
2. **Arming window.** Until 16:55 New York, with exits clamped at 16:54, instead of 15:54.
3. **Gap rule.** Round 27 treated the first tick of every session window as following a gap, which excluded 18:10-18:25
   New York every day. Here the gap is measured against the real previous tick. For gold the 17:00-18:00 halt still
   excludes 18:00-18:15.
4. **Blocked levels.** When the nearest level is blocked by the 1,440-minute rule, round 27 skipped to the band exit,
   which could miss another level arming in between. Here only that level's candidate ticks are skipped (synthetic
   test 10b).
5. **Repeat.** Defined below by the bot's own earlier trigger, not by round 27's $0.50 touch.
6. **Placebo.** The whole grid is shifted by an offset between minor levels (BRIEF), not by U[1, 9].

Prices-only counts: 475 major events (IS 282, VAL 193), against round 27's 271 / 185.

## Cells
- **Per symbol (7)**, six event sets:
  - **major (primary)**: every trigger at a major level, i.e. the traded book;
  - **super**: major triggers at a super level (dose);
  - **minor**: triggers at minor levels that are not major (dose, not traded);
  - **repeat**: major triggers on a level that triggered in the **same direction** within the previous 5 x 1,440
    clock minutes. The freshness rule forces the price back to the approach side for >= 1,440 minutes in between, so
    the earlier break failed. Triggers whose earlier trigger was in the opposite direction ("flip") are counted, not
    a cell;
  - **down** and **up**: the major set split by side (down = sell after a downward break).

  Each set has three exits, **30 (primary)**, 15 and 60 minutes: 7 x 6 x 3 = **126 cells**. The latencies (0 / 250 /
  1,000 ms / next tick) and the x1.5 and +1-minute variants are readings of a cell, not cells: 504 latency readings.
  **Primary cell per symbol: major, h = 30, 250 ms.**
- **Pools, information for the lead (the lead pools across streams).** Classes (FX = AUD + NZD; US indices = US30 +
  USTEC; oil = XTI + XBR; gold) and the R1 set of all seven, built as in the BRIEF:
  - each trade's net bp is divided by its symbol's IS per-trade sd of the 30-minute net return (major cell, 250 ms,
    IS trades only, ddof 1, fixed for VAL and PRE);
  - t is clustered by UTC day;
  - power = per-trade Sharpe x sqrt(1.73 x trades a year), plus the per-day version.
- **Placebo / random control.** 200 grids per symbol:
  - the whole grid (minor levels and their major / super subsets) is shifted by offset = (k + u) x m, with k uniform
    in {0 .. M/m - 1} and u uniform in [0.3, 0.7];
  - numpy default_rng(2028000 + the symbol's index in the table above: XAU 0, AUD 1, NZD 2, US30 3, USTEC 4, XTI 5,
    XBR 6);
  - each draw is its own bot with the same rule, run at every latency and exit.

  Per cell: the share of the 200 draws whose mean net at 250 ms is below the real mean. Each draw's IS (VAL) trades
  are subsampled without replacement to the real count when the draw has more (seed 99, round 27's method); the
  unsubsampled share is reported too, as the lead's pool.py computes it. The book-level placebo is the lead's: it sums
  the same draw index k across symbols.

## Statistics and bars
- **Per cell**, IS and VAL (and PRE for gold):
  - mean mid and net bp at each latency, t clustered by UTC day of the trigger;
  - x1.5 and +1 minute;
  - years > 0 (net, 250 ms);
  - VAL / IS (net);
  - per-trade net Sharpe and power at the IS and the VAL rate, plus per-day power;
  - placebo share;
  - every reading with and without March-April 2020 (round 13 pitfall).
- **LIVE** (round 13; 250 ms): IS net t >= 2.5; VAL net t >= 1.5; net > 0 in >= 2/3 of years (9 years: 6; oil 7
  years: 5); net > 0 in IS and VAL at x1.5 and at +1 minute; placebo beaten >= 95 % in IS and in VAL; power at the
  VAL rate >= 3.
- **DEMO**: IS net t >= 2.0; VAL net > 0; net > 0 at x1.5 and +1 minute in IS and VAL; placebo beaten >= 90 % in IS
  and in VAL.
- **Chance.** Max |t| of 126 independent normals (p50 / p95), against the best IS net t among the 126 cells.
- **Power arithmetic** (prices-only counts). The per-trade net Sharpe that power 3 needs at the VAL rate is XAU 0.285,
  AUD 0.575, NZD 0.632, US30 0.282, USTEC 0.256, XTI 0.131, XBR 0.132, R1 set 0.079 (836 trades a year). For
  comparison, round 27's gold cell had 0.140 in VAL.

## Event counts (prices only; real grid, `out/count_summary.txt`)
| symbol | all triggers | major | IS / VAL major a year | super | minor | repeat | major down / up | spread-only triggers (major) | median s60 at arming, major (bp): 2016 -> 2024 |
|---|---|---|---|---|---|---|---|---|---|
| XAUUSD | 2,378 | 475 | 47.0 / 64.3 | 244 | 1,903 | 97 | 224 / 251 | 0.131 | 1.21 -> 0.22 |
| AUDUSD | 795 | 148 | 16.8 / 15.7 | 57 | 647 | 25 | 74 / 74 | 0.101 | 0.57 -> 0.00 |
| NZDUSD | 758 | 127 | 14.7 / 13.0 | 93 | 631 | 36 | 66 / 61 | 0.102 | 1.08 -> 0.67 |
| US30 | 969 | 476 | 46.7 / 65.3 | 100 | 493 | 97 | 235 / 241 | 0.126 | 2.11 -> 0.16 |
| USTEC | 2,273 | 462 | 37.2 / 79.7 | 241 | 1,811 | 104 | 232 / 230 | 0.052 | 5.00 -> 0.37 |
| XTIUSD | 3,463 | 1,752 | 210.2 / 303.7 | 348 | 1,711 | 322 | 869 / 883 | 0.108 | 4.55 -> 2.76 |
| XBRUSD | 3,435 | 1,778 | 223.5 / 294.7 | 358 | 1,657 | 338 | 872 / 906 | 0.094 | 4.17 -> 1.25 |
| R1 set | | | 596 / 836 | | | | | | |

Major events by year:

| symbol | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| XAUUSD | 38 | 29 | 37 | 43 | 75 | 60 | 70 | 44 | 79 |
| AUDUSD | 29 | 18 | 8 | 13 | 22 | 11 | 20 | 13 | 14 |
| NZDUSD | 12 | 18 | 7 | 6 | 20 | 25 | 12 | 13 | 14 |
| US30 | 21 | 20 | 54 | 41 | 89 | 55 | 88 | 47 | 61 |
| USTEC | 16 | 10 | 35 | 27 | 74 | 61 | 98 | 65 | 76 |
| XTIUSD | - | - | 202 | 189 | 189 | 261 | 375 | 286 | 250 |
| XBRUSD | - | - | 220 | 209 | 203 | 262 | 367 | 288 | 229 |

Oil is ~70 % of the R1 set's trades. Its round trip (4-12 bp of spread) is the largest cost here. The FX pairs give
15 trades a year each, too few to matter alone.

## Fill-model checks (reported, not cells)
For the major and minor sets at every latency:
- slippage beyond the stop (fill - stop price, bp; median and p90);
- spread-only triggers (mid at the trigger not past L: the ASK / BID reached the stop only because the spread widened
  beyond its arming value) and the share of triggers with a spread > 2 x s60;
- entry delay (ms) per latency; exits that met a > 10-minute quote gap; clamped exits;
- double fills (impossible: one order at a time, no OCO; checked on the event lists);
- an independent per-tick re-simulation (`code/verify_brute.py`) of a few real sessions per symbol that hold major
  events: event lists and 250 ms nets must match exactly.

## Minute-vs-tick fill calibration (XAUUSD, AUDUSD, US30; IC 2016-24)
- **Minute data.** The 1-minute panel r25/shared/panel (mid close, last-tick spread; bar-START labels, so a bar's close
  is at label + 60 s).
- **The minute bot.** The same rule on minute closes:
  - freshness over the closes of the previous 1,440 minutes;
  - band and cancel on the close mid;
  - s60 = the median minute spread of the 60 minutes before arming;
  - the same calendar, 16:55-18:10 New York and gap exclusions;
  - the trigger is the first close whose ask (mid + spread / 2) reaches the buy stop (bid for the sell stop).
- **Minute fill model (the BRIEF's), two readings of "max(stop price, the first available price beyond it)" on
  close-only data**, both at slippage 0 first:
  - **M-stop**: the stop price, or the trigger close's ask / bid when the previous minute bar is missing (a gap: the
    first available price is already beyond the stop);
  - **M-close**: the trigger close's ask / bid (the first observed price beyond the stop).

  For both, the exit is the bid (long) / ask (short) close of the bar h minutes after the trigger bar, i.e. buy at
  ask = bid + the minute's spread. "+1 minute": entry at the next bar's close, exit one bar later. x1.5: spread x1.5
  at the closes; an M-stop entry stays at the stop.
- **Same events.** The minute bot runs on the real grid and on placebo draws 0-39. Its events are matched one to one
  with the tick events of the same grid: same level and side, minute trigger bar within [tick trigger minute - 1, +30];
  the nearest bar wins.
- **Reported.**
  - Match rates both ways.
  - For matched pairs, the per-trade bias (minute net - tick net at 250 ms, h = 30): mean, median and by direction,
    separately for real major, real minor and placebo events. Also the entry-price and exit-price parts.
  - The cell-level comparison (all minute events vs all tick events).
- **Recommended slippage for R2.** The M-stop slippage that zeroes the mean bias on matched placebo events (no
  round-level effect by construction), in bp and in units of the symbol's median absolute 1-minute mid change. R2 can
  then carry it to its symbols. Also how much of the tick result on real major events each reading recovers.
- Written to `r28/R1/minute_calibration.txt` and to STREAM_R1.md as soon as it exists.

## PRE 2004-15 for XAUUSD (minute level, labelled)
- **Data and costs.** Dukascopy m1c XAUUSD (bar-start labels; bid only 2004-09, ask from 2010). The mid is
  (bid + ask) / 2 where the ask exists, else bid + half the modelled spread. The modelled spread and s60 come from
  IC's 2016-17 median spread by UTC minute of day and New York DST (round 27's convention), plus 0.6 bp.
- **The bot.** The same minute bot, with the 2007+ calendar (2004-06 have no release exclusion).
- **Readings.**
  - M-stop with the recommended slippage, which goes into the CSV;
  - M-close;
  - round 27's (a) stop + IS tick median slippage and (b) trigger-close entry, which are the same as M-stop at the
    tick slippage and M-close.

  All exits are at closes. Read against the IC 2016-24 calibration, not alone.
- **Placebo.** The same 200 placebo grids at minute level.

## Per-trade CSV for the lead
- **File.** `r28/R1/trades_R1.csv`. Columns sym, cls, cell, era, year, t_trigger_ms, side, gross_bp, net_L0,
  net_L250, net_L1000, net_x15, net_p1min, sd_is_30min, fill.
- **Rows.** One row per trade and cell, with the 30-minute exit:
  - cells major / super / minor / repeat (super and repeat rows repeat their major trades, so each cell is
    self-contained);
  - placebo_<k> rows (k = 0..199) for the major cell;
  - gold's PRE rows (fill = minute; net_L0 = net_L250 = net_L1000 = the minute model).
- **Columns.** gross_bp is the mid return at the 250 ms fill ticks. sd_is_30min is the symbol's sd defined above.
  cls is FX / USIDX / OIL / GOLD (pool.py's codes).
- **The 15- and 60-minute exits** go to `trades_R1_h15_h60.csv` (same columns plus exit_min).

## Not declared (will not become candidates)
Any other spacing, band, offset, exit, session, side rule, symbol subset, volatility or year selection; the "flip"
triggers.

## Addendum (2026-10-17 22:50 UTC, after the results; nothing here is a cell)
- **Calibration method changed after looking.** The declaration said the recommended slippage would zero the bias on
  *matched* placebo pairs. The first output showed that matching is selection-blind:
  - 11-17 % of tick triggers reverse inside the minute, never produce a close past the stop, and lose 12-15 bp each;
  - the minute bot cannot see them.

  The recommendation is therefore computed at the cell level (each model on its own events, placebo grids). It points
  to the close-entry reading (M-close, slippage 0), not the stop-price reading. Both numbers are reported in
  STREAM_R1.md and r28/R1/minute_calibration.txt.
- **Gold PRE rows in the CSV.** Consequently the CSV uses M-close at slippage 0 for gold's PRE rows, not "M-stop with
  the recommended slippage" as declared. All readings are tabulated in STREAM_R1.md.
- **Information added after looking:**
  - mid-level placebo shares;
  - the R1-without-oil and R1-without-gold pools;
  - the round 27 / round 28 gold event comparison;
  - sessions and Sunday-evening splits.
