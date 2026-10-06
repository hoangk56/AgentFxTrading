# Round 11, stream H: hypotheses, each written before its numbers

Stream H: a complete intraday calendar scan of IC's commission-free index CFDs, aimed at the LIVE bar, plus a short
pre-written family of mechanism-first index windows. HOLD (2025-01-01..2026-09) stays closed: the panel ends
2024-12-31, the new-symbol M1 files are opened only for dates < 20250101 and bars with ts >= 2025-01-01 are dropped
at load. Scripts and outputs: `scratchpad/r10/H/`.

## Why this could escape the standing limits (2026-10-06 00:28 UTC)
In FX the 0.6 bp commission is the floor (round 10). Index CFDs pay no commission; US30's spread is 0.86 bp IS /
0.3 bp VAL at liquid hours. Round 10's frontier says a daily 15-min rule in US30 needs ~2.6 bp gross at IS costs
(less at VAL costs). Earlier index scans were partial: round 3's hour-of-day scan (7 symbols, UTC hours), round 3's
calendar scan (hour windows starting 18:00 UTC the evening before), round 4's 19 benchmark times, round 7's adaptive
periodicity. A full minute-of-day (15-min grid) x weekday x month-position scan at local exchange time of US30,
USTEC, UK100, HK50, AUS200 and the new bid-only ES35, F40, IT40, STOXX50, US2000 has never been run. If any
fixed-clock flow in an index is >= 2-5 bp per 15-60 min, it would clear the cost line that FX cannot.
Honest prior: rounds 3-4 found index flows of 0.5-3 bp, and the scan is wide, so most cells will be noise; the
rules below are built to say so with numbers.

## H1 full calendar grid (2026-10-06 00:28 UTC, before any return was computed)

Symbols and clocks
- Eligible: US30, USTEC, UK100, HK50, AUS200 (panel mid and actual spreads); ES35, F40, IT40, STOXX50, US2000 (IC M1
  bid bars; mid = bid + published spread / 2; cost = round 7's published average spreads ES35 4.2 pts, IT40 9.0,
  F40 1.79, STOXX50 1.5, US2000 0.34, round trip).
- Information only (round 3 printed their HOLD hour-of-day means; never candidates, not counted in K or in the null):
  US500, DE40, JP225.
- Clocks: local exchange time, DST-aware (America/New_York for US30, USTEC, US500, US2000; Europe/London UK100;
  Europe/Berlin for DE40, STOXX50, F40, ES35, IT40 (same offsets as Madrid/Rome/Paris); Asia/Hong_Kong HK50;
  Australia/Sydney AUS200; Asia/Tokyo JP225) and UTC. HK50 and JP225 have no DST, so their UTC clock duplicates the
  local one and is not counted twice.
- New bid-only symbols: only windows lying entirely inside the cash session (09:00-17:30 CET; US2000 09:30-16:00 ET),
  where a published average spread is a fair cost; elsewhere IC's spreads are wider and unknown.

Cells
- Windows of 15 and 60 minutes starting at every 15-minute boundary of the clock (96 starts a day).
- Day types (date of the window start in that clock): Mon, Tue, Wed, Thu, Fri, all weekdays, first 3 and last 3
  trading days of the month (trading day = weekday with >= 120 M1 bars of that symbol in that clock's date).
- Entry price = mid at the start boundary = close of the last bar in the 5 minutes before it; exit likewise at the
  end boundary; no quote in those 5 minutes -> no observation. A cell is eligible if it has observations on >= 60 %
  of its IS day-type days.
- Return in bp of mid; one observation per day per cell, so the plain t is day-clustered. Spikes: returns clipped at
  +-10 x (1.4826 x MAD) of the cell's own era sample; UK100 2017-04-17 dropped (known IC glitch).
- Cost per observation: half the actual spread at the entry minute + half at the exit minute (panel symbols), or the
  published spread (new symbols). No swap (all windows are intraday and those crossing 21:00/22:00 UTC are flagged;
  a cell whose window crosses the rollover minute pays 2 bp; noted in the output).

Selection on IS 2016-2021 only
- K = number of eligible cells (eligible symbols). Threshold T_K = Bonferroni two-sided 5 %: |t_IS| >= z(1 - 0.025/K).
  Tier 2 (reported, weaker, still family-wise): |t_IS| >= the 95th percentile of the permutation null's max |t|.
- Frontier: side = sign of the IS mean; IS net per-trade Sharpe (side x mean - mean cost) / sd >= S_req =
  3 / sqrt(1.73 x n_IS / 6) (i.e. mean above cost + 0.145 sd for daily cells, + ~0.32 sd for weekday cells,
  + ~0.38 sd for month-position cells). Both T_K and the frontier must hold.
- Null: 1,000 permutations flipping the sign of every return on a UTC date (date of the window start), the same flip
  for all cells and symbols; report the null's max |t_IS| distribution (median, 95th) against the observed max.

After selection, before VAL
- For every selected cell, a mechanism (cash open/close, futures settlement, lunch break, European close, US data at
  08:30 / 10:00 ET, option expiry, futures roll, MOC imbalance at 15:50 ET, ...) is written below, with the UTC time,
  BEFORE VAL is computed for it. No mechanism -> not a candidate even if VAL holds (VAL still computed for the repeat
  count).
- VAL 2022-2024, once: mid and executable net (actual spreads), +1 minute (both ends one minute later), spread x1.5,
  years net > 0 (2016-24), random-slot control (>= 200 seeds: same number of trades on the same days, same side and
  hold, start slot drawn uniformly from the symbol's eligible slots of the same session block (home cash session vs
  outside it) in the same clock), per-trade Sharpe, power per trade and per day (the same here: one trade a day),
  daily and monthly P&L correlation with C3 on IS+VAL.
- Repeat count: of the selected cells, and of the top 100 eligible cells by |t_IS| (a larger, chance-calibrated set),
  how many have the VAL mean on the IS side and how many have VAL t >= 1.5 on the IS side; chance 50 % and 6.7 %.
  Also the correlation of t_IS and t_VAL over all eligible cells, against the same per-day flip null applied to VAL.

## H2 mechanism-first index windows (2026-10-06 00:28 UTC, before any number; separate family)
Each rule has its side fixed here. Fill convention: the signal uses bars up to minute t, entry at the close of
minute t+1. Mid first, then actual spreads, +1 minute, x1.5. IS 2016-21 / VAL 2022-24. Expected counts: daily
~250/yr, monthly ~12-36/yr (DEMO tier only by construction).

- M1 MOC imbalance publication, continuation (US30, USTEC; US500 info). Mechanism: the NYSE/Nasdaq closing-auction
  imbalance is published at a known minute; the futures-based CFD reprices on it and market-on-close liquidity
  takers who see a large imbalance trade with it into 16:00 ET (price pressure that peaks at the cross). Time:
  NYSE 15:45 ET until 2019-01-31, 15:50 ET from 2019-03-01 (SEC approval 2019-01-31 of NYSE Rule 123C change;
  February 2019 dropped as uncertain); Nasdaq NOII 15:50 ET throughout. US30 uses the NYSE time, USTEC Nasdaq's.
  Rule: sign = mid return over the publication minute (close of minute P-1 -> close of minute P); entry at the close
  of minute P+1, exit at 16:00:00 ET (close of 15:59). Side: follow. Variant M1b: 15:50 for both in all years.
  Differs from round 3/4 (post-close reversal; day's move -> last 30 min): conditions on the imbalance minute only.
- M2 10:00 ET US releases, follow-through (US30, USTEC). Releases with a rule-based calendar: ISM manufacturing
  (1st NYSE business day of the month), ISM services (3rd business day), Conference Board consumer confidence (last
  Tuesday of the month), all 10:00 ET. Mechanism: Evans & Lyons-type gradual incorporation of order flow after
  news. Round 3 tested 08:30 releases only; round 7 tested ISM pre-announcement drift. Rule: sign = mid return
  10:00:00 -> 10:02:00 (close of 10:01); entry at the close of 10:02, exit 10:30:00 (M2a) and 11:00:00 (M2b). Side:
  follow. Placebo: the same rule on the other weekdays (non-release days).
- M3 UK100 London closing auction (16:30-16:35 London). (a) Follow sign(08:00 -> 16:15 London return) over
  16:15 -> 16:35 (tracker and gamma-hedging demand into the close in the day's direction, Baltussen, Da, Lammers &
  Martens 2021); (b) fade the 16:00 -> 16:35 move over 16:36 -> 17:30 (temporary auction price pressure reverses).
- M4 HK50 (HKEX lunch 12:00-13:00 HKT, cash close 16:00 with the closing auction 16:00-16:10, HSI futures day
  session to 16:30). (a) Fade the 11:30 -> 12:00 HKT move over 13:00 -> 13:30 (pre-lunch inventory unwinds after the
  break); (b) follow sign(09:30 -> 16:00 HKT return) over 16:00 -> 16:30 (futures-only half hour after the cash close,
  hedging demand in the day's direction, Baltussen et al.).
- M5 AUS200 (ASX pre-close 16:00-16:10, closing single-price auction ~16:10-16:12, SPI futures day session to 16:30).
  (a) Follow sign(10:00 -> 16:00 Sydney return) over 16:00 -> 16:30; (b) fade the 16:00 -> 16:12 move over
  16:13 -> 16:30.
- M6 US monthly option expiry, special opening quotation (3rd Friday; US30, USTEC). AM-settled SPX/NDX options and
  quarterly futures settle on the opening prints; the opening pressure is temporary. Rule: fade the 09:30 -> 09:35 ET
  move over 09:36 -> 10:30 ET on third Fridays (12/yr; DEMO tier only).
Cells: M1 2 symbols x 2 variants, M2 2 x 2, M3 2, M4 2, M5 2, M6 2 = 16 eligible cells (+ placebos, + US500 info).
Chance for the family: the same per-UTC-day sign-flip null over the 16 cells.

## H1 after IS selection, before any VAL number (2026-10-06 00:31 UTC)
IS result (scratchpad/r10/H/grid_is.out): K = 15,913 eligible cells, Bonferroni T_K = 4.66; per-day sign-flip null
max |t_IS| median 3.98, 95th 4.51, 99th 4.79; observed max 4.94. One cell has |t| >= T_K; no cell, at any t, has an
IS net Sharpe at the frontier (best netSR / S_req = 0.53, US30). **Selected set: empty. Tier 2: empty.** So H1 has no
candidate by its pre-written rule; VAL is computed only for the pre-written repeat count (top 100 by |t_IS|) and the
t_IS / t_VAL correlation.
Mechanisms written now, before VAL, for the cells at or near T_K (for the record; none can be a candidate because
each fails the frontier on IS):
- UK100 06:45-07:00 UTC, first 3 trading days of the month (t 4.94; local-clock twin 07:45 London t 4.39; US30
  06:45 UTC First3 t 3.60; DE40 info t 4.01): the 15 minutes before the London/Xetra cash open, long. Mechanism:
  turn-of-the-month equity inflows (Lakonishok & Smidt 1988; Etula, Rinne, Suominen & Vaittinen 2020, month-start
  cash flows of pension and payroll investment) executed at the European open, with futures pre-positioned in the
  pre-open. IS net < 0 (pre-open UK100 spread 4.5 bp vs mean 3.3).
- US30 16:00-16:15 ET (All t 3.85; Last3 t 4.03), long: the futures-only quarter-hour after the NYSE close.
  Mechanism (weak): closing-auction / month-end rebalancing demand spilling into futures after the cross (round 3
  saw continuation after 16:00). Net Sharpe 0.016 (All) / 0.21 (Last3) vs S_req 0.146 / 0.40.
- Other top cells (UK100 20:00-21:00 Fri and 20:45 Wed, HK50 13:15 Mon, USTEC 00:45 Tue, US30 15:45 Wed): no
  mechanism (off-hours or a weekday-only pattern without a weekday-specific flow); the Wednesday 15:45 ET cells would
  need FOMC conditioning, which would be a new post-hoc cell, not tested.

## H3 post hoc diagnostic (2026-10-06 00:34 UTC; written after H1 VAL and H2 numbers, before this number)
H1's VAL showed US30 15:45-16:00 ET on Wednesdays repeating (IS -4.50 bp t -3.64, VAL -3.34 t -2.04; US2000 and
US500 likewise). Question (diagnostic only, cannot become a candidate here: post hoc and below the frontier): is it
carried by FOMC Wednesdays (8 a year, statement 14:00 ET, press conference to ~15:30)? Split: FOMC-decision
Wednesdays (round-10 B calendar) vs other Wednesdays, US30 / USTEC / US2000, mid, IS and VAL.
Result (fomc_wed.out): US30 FOMC Wednesdays 15:45-16:00 ET -8.8 bp (t -3.6, n 45) IS / -9.8 (t -1.5, n 23) VAL;
other Wednesdays -3.5 (t -1.9) / -2.2 (t -1.4); USTEC and US2000 the same shape.
H3b post hoc follow-up (2026-10-06 00:34 UTC, before its numbers): short US30 and USTEC 15:45:00-16:00:00 ET on
scheduled FOMC decision days: executable net (actual spreads), x1.5, +1 minute, years, random control (>= 500 seeds:
the same days, a random 15-min start in 09:30-15:30 ET; and the same slot on random non-FOMC Wednesdays), C3
correlation. Post hoc (found from the H1 grid, then split), so it cannot be pre-registered from this round whatever
the numbers; reported as a lead for new data.
Result (fomc_follow.out, n counts all scheduled FOMC decision days, 47 IS / 24 VAL): US30 short net +6.7 bp
(t 2.72) IS / +9.5 (t 1.48) VAL, 7/9 years > 0, x1.5 and +1 min > 0, beats 100 % / 97 % of random slots on the same
days, 84 % / 100 % of random non-FOMC Wednesdays; C3 daily corr -0.03. Post hoc: no PREREG_DRAFT (see STREAM_H.md).

## Outcome (2026-10-06 00:35 UTC)
H1: no selected cell, no candidate. H2: no cell net > 0 in both eras with IS t >= 2; family max |t| at chance. H3:
post-hoc lead only. No PREREG_DRAFT written. Write-up: scratchpad/r10/H/STREAM_H.md.
