# Round 37, stream A: hypotheses (record-level stops with the gold $50 construction)

Declared 2026-10-29 09:31 UTC (`date -u`), before any return was computed and before any event count. Event counts
(prices only, no returns) are appended below with their own time, still before any return. HOLD 2025-01-01..2026-09
stays closed: every IC series is cut at ts < 1735689600000 at load; tick days are asserted < 2025-01-01.

## Mechanism and sources
- Stop-loss and breakout buy-stop orders cluster just beyond the most visible price levels and, when hit, are
  executed at market in the direction of the break, so the price continues (Osler 2003, JF,
  https://doi.org/10.1111/1540-6261.00588; Osler 2005, JIMF, https://doi.org/10.1016/j.jimonfin.2004.12.002). Round 27
  found this in gold at fresh $50 / $100 levels only (DEMO, HOLD power 1.40); round 28 found it nowhere else at round
  numbers.
- A record (all-time high, 52-week high / low) is a more visible level than a round number: it is printed by every
  data vendor and screener, it is the anchor of the 52-week-high literature, and volume jumps when the price crosses
  it (Huddart, Lang & Yetman 2009, Management Science, https://doi.org/10.1287/mnsc.1080.0920: volume is strikingly
  higher when the price crosses the 52-week high or low; George & Hwang 2004, JF,
  https://doi.org/10.1111/j.1540-6261.2004.00695.x; Li & Yu 2012, JFE, https://doi.org/10.1016/j.jfineco.2011.04.003:
  nearness to the Dow's 52-week high and historical high predicts index returns). The crowd of shorts with stops
  above the record, of breakout funds with buy-stops there, and (for lows) of longs with stops below the 52-week low,
  is the same kind of order cluster as gold's.
- What differs from earlier rounds: an intraday resting stop at the record + half spread with a 15-60 minute exit
  (rounds 2 / 7 / 11 tested daily Donchian / 52-week momentum on daily closes held for days; C1 was a Donchian H4
  bot; round 31 P1 tested gold stops beyond prior-day / week / Asian extremes; rounds 27 / 28 round numbers).
- Side: the direction of the break (continuation), from the mechanism. Never chosen on data.

## Data, eras, seeds
- IC M1 (`research/data/m1/<SYM>.npz`, bid OHLC + ask close): US500, USTEC, US30, DE40, UK100, JP225, AUS200, HK50,
  XAUUSD, XAGUSD, BTCUSD (from 2017-08-28). US2000: IC M1 bid zbars (`research/data/US2000/m1`), ask = bid + 0.34
  index points x the US500 hourly spread factor (round 29 F's declared model; factor = US500 IS median minute spread by
  UTC hour / its median in 14:30-21:00 UTC).
- IC ticks (days < 2025-01-01) for USTEC, US30, XAUUSD, XAGUSD: the tick fill model below decides for these four;
  minute model for the other eight (round 28's calibration: entry at the trigger bar's close, unbiased under the null
  within +-0.4 bp, a lower bound when the move is fast).
- FX family (F): IC M1 EURUSD, USDJPY, GBPUSD, AUDUSD, NZDUSD, USDCAD, USDCHF, EURJPY, GBPJPY, AUDJPY.
- PRE 2004-15 (Dukascopy): XAUUSD, XAGUSD (`duka/m1c`, close-only minutes; silver before 2008 is thin and is
  reported but not trusted), FX USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD (`duka/m1`), AUDUSD, NZDUSD (`duka/m1c`).
  Bid only (early asks are junk): ask = bid + the IC 2016-17 median spread (bp of mid) by UTC minute of day; + 0.6 bp
  commission. Records on PRE from minute closes. PRE events start 2005-01-01 (one year of seed).
- Eras: IS 2016-01..2021-12, VAL 2022-01..2024-12, PRE 2004-15. 52-week records need 365 days of history:
  - indices and BTC (IC data from 2016-01 / 2017-08): 52-week events from 2017-01-01 / 2018-08-28, so their IS is
    2017-21 (5 years) / 2018-08..2021;
  - XAU, XAG and FX: the 2015 seed year comes from Dukascopy (H1 for FX and XAU highs / lows, m1c for XAG), so IS
    starts 2016-01-01. The venue basis (Dukascopy vs IC) is a few pips / cents and is accepted, stated here.
- All-time high (ATH) seed = max(declared pre-2016 public intraday all-time high, running IC max). Declared seeds
  (cash index / spot, from public history, approximate; the IC CFD basis is a few tenths of a percent at most):
  US500 2,134.72 (2015-05-20), US30 18,351.36 (2015-05-19), USTEC 4,816.35 (Nasdaq-100, 2000-03-24), US2000 1,296.0
  (2015-06-23), DE40 12,390.75 (2015-04-10), UK100 7,122.74 (2015-04-27), JP225 38,957.44 (1989-12-29), AUS200
  6,851.5 (2007-11-01), HK50 31,958.41 (2007-10-30), XAUUSD max(873.0 (1980-01-21), Dukascopy 2004-15 max), XAGUSD
  max(50.35 (1980-01-18), Dukascopy max), BTCUSD 4,480 (2017-08-17). ATH events start 2016-01-15 (BTC 2017-09-05). No
  all-time lows (not meaningful for these series).
- Calendar exclusion: High-impact USD minutes from `research/results/portfolio/gold_level_cbot/ff_usd_high_2015_2023.csv`
  (ForexFactory, 2015-12..2023) and `round27_levels_opens/prereg_code/usd_high_2024_2026.csv` (rows < 2025 only). No
  calendar for other currencies and none for PRE (round 25's ForexFactory file is gone with its scratchpad): stated
  limitation, applied the same way to real and placebo levels.

## The rule (family A, primary construction; mirrors round 27 G1-XAU50)
- NY session day d = 17:00 New York (d-1) .. 17:00 New York (d). Daily mid high H_d / low L_d from minute mid highs /
  lows (bid high / low + half the bar's closing spread).
- Levels known at the start of session d (only data of sessions < d):
  - H52(d) = max H over sessions in [d - 365 calendar days, d - 1]; L52(d) = min L over the same window;
  - ATH(d) = max(seed, max H over all IC sessions < d).
- Fresh (K): the level was set (touched) >= K sessions before d, i.e. max H over the last K sessions < H52(d) (for
  lows: min L over the last K sessions > L52(d)). K = 5 primary, K = 20 secondary. When ATH(d) = H52(d) the two are
  one level (one event, flagged both).
- Order: upper level R: buy stop at R + 0.5 x s60(t); lower level R: sell stop at R - 0.5 x s60(t); s60(t) = median
  closing spread of the 60 minutes before minute t (updated each minute; a bot can modify a resting stop each minute).
- Armed minutes: 18:10 NY (d-1) .. 15:54 NY (d); not within +-15 min of a High-impact USD minute; not within 15 min
  after a quote gap > 60 min; not while the symbol has an open trade (one position per symbol); FX JPY pairs never in
  23:00-02:00 UTC (C3's Tokyo-fix window +- 1 h).
- Trigger: the first minute of session d in which the stop is reached (minute model: bid high + bar spread >= buy
  stop, bid low <= sell stop; tick model: the first tick with ASK >= buy stop / BID <= sell stop). If that first
  reach falls in a non-armed minute (incl. a gap open beyond the level), the level is consumed for the day: no trade
  (the record is no longer a record afterwards, so it can never be fresh again). One trigger per level per day.
- Exit: market h = 30 minutes after the trigger (15 and 60 secondary), capped at 16:54 NY. No protective stop. No
  position crosses 17:00 NY, so no swap.
- Fills:
  - tick model (USTEC, US30, XAU, XAG): entry at the ASK (buy) / BID (sell) of the first tick at or after trigger +
    250 ms; exit at the BID / ASK of the first tick at or after trigger + h + 250 ms. Readings at 0 ms (the trigger
    tick) and 1000 ms.
  - minute model (all others, and the placebo grids of every symbol): entry at the trigger bar's close ask / bid,
    exit at the close bid / ask of the bar starting h minutes after the trigger bar.
  - spread x1.5: entry and exit each a further 0.25 x their spread worse. +1 minute: both fills 1 minute later.
  - commission 0.6 bp round trip for metals and FX, 0 for indices and BTC. PRE: modelled spread + 0.6 bp.
- Units: bp of the entry mid; t clustered by UTC day. Pooled books at equal risk: each trade's net / the symbol's IS
  sd of unconditional 30-minute mid returns in the armed minutes (sd units); raw bp also shown.

## Cells (all declared now)
- A (12 symbols): record type {H52, L52, ATH} x K {5, 20} x h {15, 30, 60} per symbol = 216 readings; book cells
  {ALL (union of the three), H52, L52, ATH} x K x h = 24. **Primary: book ALL, K = 5, h = 30.** Candidate cells for
  the bars: the 24 book cells and the 12 per-symbol ALL K5 h30 cells (36); the rest are readings.
- F (10 IC FX symbols, IS / VAL; PRE on 7 Dukascopy pairs): {H52, L52} x K x h per symbol = 120 readings; book
  {ALL, H52, L52} x K x h = 18 candidate cells. Primary: F book ALL K5 h30, with PRE 2005-15 as the third era.
- Gold PRE: A's XAU cells on Dukascopy 2005-15 (minute model).
- Declared dose predictions (information, not gates): K = 20 >= K = 5 (older records gather more stops); ATH >= H52;
  low breaks >= high breaks (long liquidation, as in gold $50 and round 28's side split).
- Fallback family B (declared now; run in full if A and F fail): salient calendar-period extremes, never tested with
  this construction. Levels known at the start of the period:
  - PM: the previous calendar month's high / low; PQ: the previous calendar quarter's; PY: the previous calendar
    year's; EV: the high / low of the most recent NFP, CPI or FOMC-statement session (NY session containing a
    ForexFactory / official "Non-Farm Employment Change", "CPI m/m" or "FOMC Statement" / "Federal Funds Rate" minute),
    armed for the 5 sessions after it.
  - Fresh: the level has not been reached since its period ended (first break in the new period); same order, fills,
    exits and exclusions as A. Up breaks buy, down breaks sell.
  - Cells: {PM, PQ, PY, EV, ALL} x h {15, 30, 60} as books over the 12 A symbols (15 candidate cells) + per-symbol
    ALL h30 readings (12); FX: {PM, PQ, PY, ALL} x h on the 10 FX symbols (12 cells), PRE on the 7 Dukascopy pairs.
  - P1 (round 31) already did prior-day / prior-week / Asian-range extremes in gold, and its P1-X replication did
    prior-day on XAG / US30 / USTEC / AUD / NZD: those are not repeated.

## Controls and bars
- Placebo levels (the random control, 200 draws): each real level R is replaced by R x (1 + u x w), w = the symbol's
  IS median daily range in %, u ~ U([-1, -0.25] U [0.25, 1]) per symbol-day, with the same freshness rule against the
  last K sessions, the same armed minutes and the minute model; the draw's mean (subsampled to the real count) is
  compared to the real minute-model mean. This separates "a record" from "a fresh K-session extreme at any level"
  (which is P1 / Donchian-like momentum). Also 200 random-time draws per cell: random armed minutes on the event's
  own day, side = sign of the 60-minute mid return before the random minute (data-dependent side recomputed).
- Multiple testing: sign-flip null (one sign per UTC day shared across cells) on the IS mid t of the candidate cells;
  max |t| of K independent normals.
- Overlap with P1 / Donchian: share of record-trigger days that are (a) P1-PD days (the prior NY-day high / low broken
  that day), (b) daily Donchian-20 / -55 close-breakout days, and the converse shares; the record result on the days
  that are not Donchian-20 signal days.
- Gold overlap with round 27: gold record events within $5 of a $50 multiple are flagged and the gold cell is shown
  without them.
- Bars (research/PROMPT.md, unchanged): LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years net > 0, beats >= 95 % of
  random, net > 0 at x1.5 and +1 minute, HOLD power = per-trade net Sharpe x sqrt(1.73 x trades a year) >= 3. DEMO:
  IS t >= 2.0, VAL net > 0, beats >= 90 % of random, x1.5 and +1 minute > 0. Results reported with and without
  March-April 2020.

## Power arithmetic (before any count)
LIVE needs per-trade net Sharpe >= 3 / sqrt(1.73 x N) at N trades a year: N = 50: 0.322; 100: 0.228; 200: 0.161;
400: 0.114. Gold $50 had 0.14-0.17 on IS / VAL, so a record rule with gold's per-trade quality needs >= ~200 trades a
year for LIVE. With a 30-minute sd of ~15-25 bp at index / metal breaks, 100 a year needs ~4-6 bp net per trade.

## Event counts (prices only; appended 2026-10-29 09:42 UTC, before any return was computed)
Trades (first armed reach, after the busy rule) per year; scripts `count.py` / `run.py` with COUNT=1, outputs
`out/count_*.txt` in the stream scratchpad.

| set | IS (per year) | VAL (per year) | note |
|---|---|---|---|
| A, K = 5, 12 symbols (H52 + ATH + L52 union) | 267 (44.5; 2016 = 24 as 52-week indices start 2017) | 133 (44) | K = 20 subset about half; L52 about 1/6 |
| A, K = 1 (added now, see below) | 564 (94) | 264 (88) | |
| F, K = 5, 10 IC FX | 183 (30.5) | 108 (36) | |
| PRE metals K = 5 (Dukascopy XAU + XAG 2005-15) | ~7 a year | | gold ATH events 2008-11 |
| PRE FX K = 5 (7 Dukascopy pairs 2005-15) | ~23 a year | | |
| B, 12 A symbols (PM + PQ + PY + EV) | ~520 a year (EV ~33, PM ~8, PQ ~2.5, PY ~0.6 per symbol-year) | same rate | |
| BF, 10 FX | ~400 a year | same rate | |

What the counts allow (LIVE needs per-trade net Sharpe >= 3 / sqrt(1.73 N)):
- A at K = 5: N ~ 45 a year -> needs 0.34 per trade: out of reach for any effect seen in 36 rounds (gold $50: 0.14-0.17).
  **A can reach DEMO at most.** With F pooled (~80 a year) LIVE needs 0.26: still out of reach in practice.
- A at K = 1: N ~ 90 -> 0.24. LIVE only if records are far stronger than gold's $50 levels.
- B: N ~ 520 -> 0.10 (B book), PM alone ~100 -> 0.23, EV alone ~400 -> 0.11. **B is the only family whose count
  allows LIVE at a plausible per-trade Sharpe** (~0.1, below gold $50's).
- Added after the counts, before any return: cell A1 (K = 1: the record was set >= 1 session before the trigger
  session), same rule otherwise, as a secondary book cell (h 15 / 30 / 60); it counts towards the cells tried.

## Family C (declared 2026-10-29 09:51 UTC, after A / A20 / A1 / F / B / BF / PRE returns were seen; before any C return)
A and B fail at the book level (STREAM_A.md). C extends the salient-level search to two levels no round has run with
this construction on these symbols; both are declared before their returns, same order / fill / exit / exclusion
rules as A, same placebo-level and random-time controls, same bars:
- PW: the previous calendar week's (NY sessions Mon-Fri) high / low, fresh = not reached since that week ended. Round
  31 P1-PW ran it on gold only (net -1.56 / -0.06); here on the other 11 A symbols and the 10 FX (gold reported, not a
  candidate). ~40 a year per symbol, so a book of 21 symbols has the count for LIVE at a per-trade Sharpe ~0.07.
- MA200: the 200-session simple moving average of session closes (known at the session start), traded when price
  crosses it intraday after closing on the other side for >= 5 consecutive sessions (side = direction of the cross).
  Mechanism: the most-watched trend level of index and commodity desks (CTA / trend-following rules and media).
- Cells: {PW, MA200, ALL} x h {15, 30, 60} books for the 12 A symbols (9) and for the 10 FX (9); per-symbol ALL h30
  readings. Primary: A-symbol book ALL h30.
