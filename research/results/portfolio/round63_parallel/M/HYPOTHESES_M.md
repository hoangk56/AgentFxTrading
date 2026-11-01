# Round 63, stream M: known "real at mid" intraday effects re-graded at an exchange / ECN venue cost

Written 2026-10-31 from 15:10 UTC (`date -u` gave 15:10:36 when writing started). Before writing, only published
reports were read (PROMPT.md, round 16 STREAM_X, round 24 STREAM_C / HYPOTHESES_C, the joint prereg) and the arithmetic
in `code/precalc.py` was run on their published IS / VAL numbers (no price file read). No stream-M return has been
computed. HOLD (2025-01-01 onwards) is never loaded: every series is cut at ts < 2025-01-01 at load.

## Question
Rounds 10-24 found hundreds of intraday cells real at mid but below IC's cost (0.6 bp FX / metals commission; index,
metal and oil spreads at the key minutes). The user now allows any venue. Does any effect whose side was declared
before it was measured, and whose HOLD is still closed, pass the IS / VAL LIVE or DEMO bar at a realistic exchange
(CME / Eurex / ICE / ASX / HKEX futures via a low-cost broker) or ECN (about 0.2 bp a side commission) cost?

## 1. Venue cost model (fixed now, before any re-grading)
Round trip in bp of notional = spread paid (half at entry + half at exit) + 2 x commission per side.

### Futures (taker, front contract, retail low-cost broker; all-in commission = broker + exchange + regulatory)
| IC symbol | contract | multiplier | tick | all-in commission per side | tick in bp at IS / VAL typical price | commission rt bp IS / VAL |
|---|---|---|---|---|---|---|
| XAUUSD | COMEX GC | 100 oz | $0.10 | $2.50 | 0.69 / 0.50 ($1,450 / $2,000) | 0.34 / 0.25 |
| XTIUSD | NYMEX CL | 1,000 bbl | $0.01 | $2.50 | 1.82 / 1.25 ($55 / $80) | 0.91 / 0.63 |
| US30 | CBOT YM | $5 | 1 pt | $2.50 | 0.38 / 0.28 | 0.38 / 0.28 |
| US500 | CME ES | $50 | 0.25 pt | $2.50 | 0.83 / 0.57 | 0.33 / 0.23 |
| USTEC | CME NQ | $20 | 0.25 pt | $2.50 | 0.28 / 0.17 | 0.28 / 0.17 |
| UK100 | ICE FTSE 100 (Z) | GBP 10 | 0.5 pt | GBP 2.00 | 0.71 / 0.66 | 0.57 / 0.53 |
| AUS200 | ASX SPI 200 (AP) | AUD 25 | 1 pt | AUD 4.00 | 1.61 / 1.37 | 0.52 / 0.44 |
| HK50 | HKEX HSI | HKD 50 | 1 pt | HKD 40 | 0.38 / 0.53 | 0.62 / 0.84 |
| DE40 | Eurex FDAX | EUR 25 | 1 pt (conservative; 0.5 if the half-point tick applies) | EUR 2.50 | 0.80 / 0.65 | 0.16 / 0.13 |
| BTCUSD | CME BTC | 5 BTC | $5 | $11 (exchange ~$6 + broker ~$5) | 2.5 / 1.43 | 2.2 / 1.26 |

- In the computation the tick and the commission are converted to bp **per trade at that trade's own mid price**
  (not the typical price above). Non-USD contract currencies are converted with fixed era rates (GBP 1.30 / 1.25,
  AUD 0.74 / 0.67, EUR 1.15 / 1.08, HKD 7.8); this only scales the commission.
- **Spread bounds** (as the brief asks), per quote:
  - lower bound = one tick (a one-tick touch market): half a tick paid at each fill;
  - upper bound = max(one tick, IC's quoted spread at that minute) (IC's spread at the effect's minute as the upper
    bound; for XAU, IC's quoted spread excludes its 0.6 bp commission).
- **Futures vs spot differences** (stated, not modelled unless said):
  - CME Globex halts 17:00-18:00 New York every day (FX, metals, energy, equity index, BTC): rules that trade inside
    that hour cannot use futures. ASX SPI day session ends 16:30 Sydney (night session from 17:10); HSI futures open
    09:15 HKT (before the 09:30 cash open); Eurex FDAX trades through the 17:30 CET Xetra close; ICE FTSE futures
    trade through the 16:35 London auction; CME equity futures trade after 16:00 New York until 17:00.
  - Intraday the futures-spot basis is constant to well under 0.1 bp, so minute returns on IC's mid stand in for
    futures returns. Overnight holds (I13 only) subtract carry: futures earn spot minus (r - q) dt, with r = Fed funds
    (research/data/rates/DFF.csv) and q = 1.5 % a year.
  - Rolls: all rules are flat within the day (except I13, 1 night); trade the front / most liquid contract, no roll
    cost. Contract lumpiness ($100-300k notional per contract) and tick discreteness (a 1 bp move is 1-6 ticks) are
    noted, not modelled.
  - IC's index CFDs are priced off futures; IC's FX / gold mid is an LP aggregate. A venue's own quotes at the fix
    minutes may differ (round 12 J: part of the Sydney post-leg was IC's quotes normalising). Not testable without
    the venue's history.
- Scenario check only (not graded): IC's own cost is shown next to each row for comparison. For US30 / US500 in VAL,
  IC (0.31 / 0.49 bp, no commission) is already cheaper than YM / ES (commission alone 0.28 / 0.23 bp plus a tick).

### ECN for FX (IBKR IdealPro-type: 0.2 bp of value per side commission, i.e. 0.4 bp round trip)
- CME FX futures are **not** cheaper than IC for the majors: 6E tick 0.00005 = 0.43-0.46 bp plus ~0.35 bp commission
  = ~0.8 bp round trip at a one-tick touch (IC: 0.6 + ~0.05). So all FX rows are graded at the ECN.
- Upper bound = 0.4 bp + IC's quoted spread at each quote (IC's raw spread is an LP-aggregate touch, the same pool an
  ECN shows). Lower bound = 0.4 bp + a floor touch spread: 0.1 pip for EURUSD / USDJPY / USDCHF / GBPUSD and the six
  USD pairs of N1, 0.3 pip for EURJPY / GBPJPY, 1 pip for USDCNH.
- USDCNH (F23): IC M1 bid bars; IC's published spread 2.93 pips is the upper bound (as in round 24).
- **17:00 New York rows (N1a-c)**: no futures (Globex halt) and the rollover-hour spread widening is market-wide
  (LPs pull quotes), so the floor-touch lower bound is not credible there. A third, measured ECN estimate is added for
  these rows only: Dukascopy SWFX (an ECN) bid / ask at the same New York minutes in 2010-2015 (local
  research/data/duka/m1, mean spread per minute of the New York clock), reported as a cost column; the verdict for N1
  uses max(Dukascopy-measured, IC upper bound) only if the Dukascopy estimate is not lower, else it is reported as
  the "measured ECN" scenario next to the IC upper bound. (This uses 2010-15 spreads, not returns; no 2025-26 file is
  opened: the `*_2026.npz` files in research/data/duka/m1c are never read.)

### Which bound decides
- **Verdict = the upper bound** (IC's quoted spread at the minute, floored at one tick / the floor touch). The rules
  sit at busy or institutional minutes where a venue's touch also thins; IC's quote is the only measured spread at
  those minutes in 2016-24.
- The lower bound is reported as "optimistic"; a rule that passes only there is a venue-data decision (it would need
  that venue's own historical quotes), not a candidate, and gets no PREREG draft.

## 2. The rows: side declared before measurement and HOLD still closed for that rule
Rule definitions are exactly round 24's HYPOTHESES_C.md (copied into `code/rules.py`), same quote convention: the price
at time X = mid (bid close + ask close) / 2 of the last IC M1 bar ending at or before X (bar labelled X - 1 min),
at most 10 minutes stale; calendar windows at clock times; data-driven sides quoted >= 1 minute after the last data
point.

### Graded (computed on IC M1 mid, IS 2016-01..2021-12, VAL 2022-01..2024-12)
| id | rule (round 24 HYPOTHESES_C reading) | sel | venue | flag |
|---|---|---|---|---|
| F2 | EURUSD short 04:00-08:00 NY, weekdays | PRE | ECN | **contaminated**: contains E1's window, whose HOLD was opened 2026-10-06 (mid kept 0.65 of VAL) |
| F4 | EURUSD short 12:45-13:00 LON, weekdays, TARGET2 closing days out | PRE | ECN | **contaminated**: inside E1's window (same HOLD) |
| F7 | USDCHF long 10:00-12:00 UTC (19:00-21:00 Tokyo) | PRE | ECN | |
| F8 | F7 on days with a top-tercile 06:00-10:00 UTC USDCHF rise (250-day causal pct) | decl | ECN | forward-only random control |
| F9 | USDCHF short 08:00-08:30 NY | PRE | ECN | |
| F10 | USDJPY long 11:00-13:00 LON | PRE | ECN | same clock as E1, other symbol (not contaminated) |
| F11 | EURJPY short 11:00-13:00 LON | PRE | ECN | |
| F12 | GBPJPY long 17:30-21:30 LON (rollover-hour days dropped) | PRE | ECN | |
| F13 | GBPJPY long 02:45-06:45 SYD (rollover-hour days dropped) | PRE | ECN | |
| F14 | EURJPY long 16:00-20:00 LON | PRE | ECN | |
| F15 | EURJPY short 05:00-07:00 LON, last weekday of Mar / Jun / Sep | PRE | ECN | count-capped (3 a year) |
| F16 | GBPUSD long 15:00-16:00 LON, last weekday of the month | PRE | ECN | same month-end WM/R family as rule I (HOLD opened, -0.23); decaying |
| F23 | USDCNH long 01:30-08:30 UTC | lit | ECN (CNH) | IC bid bars + published spread |
| F24 | USDJPY long 07:45-08:00 UTC (TWD close) | decl, best of 108 | ECN | best-of-family pick |
| M2 | XAU long 02:15-02:23 UTC on SGE dip mornings (bottom-quintile 07:00 -> 02:00 UTC move) | decl | GC | forward-only random control |
| M4 | XAU fade the 06:30-07:00 UTC move, 07:00-07:30 UTC, XSHG days | decl | GC | |
| M7 | XAU follow the day 13:25-13:30 NY, NYSE days | lit | GC | weakly contaminated: 10 % of its days are rule L's top-decile days (HOLD opened) |
| M11 | XAU fade 08:10-08:20 NY over 08:20-08:30 NY (COMEX open) | decl | GC | |
| M12 | XAU long 02:00-06:00 UTC before England bank-holiday blocks | PRE | GC | count-capped (4 a year) |
| I1 | USTEC follow the 15:50-15:51 move 15:52-16:00 NY (MOC) | decl | NQ | weakly contaminated: E-USTEC (joint prereg, HOLD -2.2 bp) follows the day 15:30-16:00 on top-decile LETF days |
| I3 | US30 fade 15:54-16:04 over 16:04-16:14 NY | decl | YM | |
| I4 | US500 fade 09:31-09:41 over 09:41-09:51 NY | decl | ES | |
| I5 | UK100 fade 16:24-16:34 over 16:34-16:39 LON | decl | Z | |
| I6 | AUS200 fade 16:00-16:12 over 16:13-16:30 SYD | decl | SPI | |
| I8 | HK50 fade the overnight gap 09:30-09:31 HKT | decl | HSI | |
| I10 | DE40 follow the day 17:25-17:35 CET | decl | FDAX | |
| I13 | US500 long 16:00 NY -> 09:30 NY next weekday (night premium; reading fixed now: 16:00 = close of bar 15:59, 09:30 = close of bar 09:29), futures carry subtracted | lit | ES | reading new (round 3 never recorded its times) |
| E1x | XTI follow the day 14:15-14:30 NY (NYMEX settlement), 2018-24 | lit | CL | |
| E2x | XTI fade 14:20-14:30 over 14:30-14:31 NY | decl | CL | |
| C1 | BTC follow the UTC day 23:30-24:00 UTC | lit | CME BTC | IS from IC's first BTC quote |
| N1a | 6 USD pairs, fade the 17:00 NY reopen gap (>= 1 pip), entry bar t_r + 1, exit 18:00 NY | lit | ECN (no futures) | |
| N1b | N1a, entry at 17:05 NY | lit | ECN | |
| N1c | N1a, gap >= 2 pips | lit | ECN | |

### Scored analytically from the record (rule too costly to rebuild, and it cannot pass at any cost >= 0.1 bp)
- F25 (R3 currency-strength reversal, 10 pairs): IS mid +1.70, SE 0.65 -> IS t at zero cost 2.61, at the ECN's
  ~0.6-1.1 bp 0.9-1.7. Fails the LIVE IS gate at any venue cost above 0.08 bp; DEMO IS gate fails above 0.4 bp.
- F27 (W1 carry into the Wednesday rollover): IS mid +0.69, t at zero cost ~1.15. Fails at any cost.

### Excluded (HOLD already opened for the rule or for its mechanism on the same symbol and minutes, or side not declared)
- HOLD opened: F1 (E1), F3, F17 (rule I), F20 (J5c), M5 (rule L gold settlement big days), FOMC-A4, gold $50 levels,
  C3 / Tokyo fix, round-3 M1 (month-end), the joint prereg D-K4 / E-USTEC / A5-HN / U3-BTC, HK50 rebound (round 40),
  round 58-62 crypto rules.
- Same mechanism and minutes as an opened HOLD: M6 (rule L at the 80th pct: contains L's days), I2 (USTEC LETF close,
  top quintile: contains E-USTEC's days), C2 (BTC Friday expiry fade: D-K4 is its high-volume subset).
- The Sydney V (F19, F21, J5c family), as the brief instructs.
- Side not declared before measurement (scan / post): F5, F6, F18, F22, F28, M1 (SGE), M3, M8, M9, M10, I7, I9, I11,
  I12, N3b. (F6, M9 and I7 had positive "LIVE cost" in round 24: they are excluded on selection, not on numbers.)
- Not rebuildable (rule never recorded): F26 (PCA), F29 (Treasury auctions).
- Not M1-testable: round 26's tick-level metals fade (draft, within chance).

## 3. Statistics and bars (unchanged from the brief)
- Per row and era: n, mid bp, net bp at the venue upper bound and lower bound, t clustered by UTC entry day, years
  net > 0 (IS + VAL, 9 years; XTI 7; BTC from its IC start), per-trade sd.
- Checks (IS and VAL, at the upper bound): **costs x1.5** (the whole round trip, spread and commission, x1.5; stricter
  than round 24, which scaled spreads only) and **+1 minute** (both quotes one minute later, same side, costs at the
  later minutes).
- **Random-entry benchmark**, 200 seeds per era: same days, same hold, both times shifted by one random whole number of
  minutes in [-180, +180] (not 0), side recomputed by the rule's own formula at the shifted time, venue cost at the
  shifted minutes; forward-only shifts [+1, +180] for the data-selected rows (F8, M2); for the event-day rows (F15,
  F16, M12) random non-event days of the same era and weekday at the same clock. Draws touching 16:45-18:15 NY are
  dropped except for N1. Score = % of seed means the rule's net mean beats.
- **Power at VAL size** = VAL net t (day-clustered) x sqrt(1.73 / 3) (expected HOLD t if HOLD keeps the VAL size;
  HOLD 2025-01..2026-09-24 = 1.73 years of IC M1). Also at 0.65 of the VAL mid (E1's retention) for information.
- LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years net > 0, random >= 95 % (IS and VAL), x1.5 and +1 min net > 0 (IS
  and VAL), power >= 3. DEMO: IS t >= 2.0, VAL net > 0, random >= 90 %, x1.5 and +1 min net > 0.
- "LIVE cost" per row = the round trip at which IS t >= 2.5, VAL t >= 1.5 and VAL-size power >= 3 all hold (round 24
  formula, on mid).
- Chance: K = 33 graded rows; the expected max |t| of 33 normals (median ~2.3, p95 ~3.1) is reported next to the best
  IS t. These rows were selected as real in earlier rounds, so the IS t is not a fresh search; VAL is the check.

## 4. The one declared book
- Members: the rows meeting at least the DEMO bar at the upper-bound venue cost, excluding the contaminated rows (F2,
  F4, M7, I1), keeping one row per symbol-and-window (none overlap among the graded independent rows).
- **Fallback, declared now** (used only if fewer than 2 rows qualify): the rows with IS net t >= 2.0 and VAL net > 0 at
  the upper bound, regardless of random / x1.5 / +1 min (reported as information; such a book cannot be drafted
  unless it then meets the book bar itself).
- Equal risk: each trade's net / its row's IS per-trade net sd; daily P&L = sum of the day's trades (UTC entry day);
  IS / VAL mean, day-clustered t, years, x1.5, +1 min; IS correlation matrix of the rows' daily P&L; power = daily net
  Sharpe (VAL) x sqrt(1.73 x active days a year). Book bar = the row bars applied to the book's daily series.

## 5. Power arithmetic before building (from published IS / VAL numbers, `code/precalc_out.md`)
Typical-price venue cost; t at the venue = (mid - venue cost) / published SE.

| row | venue rt bp VAL (lo-up) | VAL net at up | VAL t up (lo) | VAL-size power up (lo) | LIVE cost rt bp | reachable bar |
|---|---|---|---|---|---|---|
| F2 | 0.49 | +1.99 | 2.52 | 1.91 | -0.64 | DEMO numbers (contaminated) |
| F4 | 0.49 | +0.65 | 2.61 | 1.98 | +0.16 | DEMO numbers (contaminated); LIVE needs <= 0.16 bp |
| F8 | 0.51-0.68 | +1.16 | 1.34 (1.54) | 1.02 | -1.58 | DEMO at most (IS t ~2.0) |
| F14 | 0.60-0.69 | +0.37 | 0.50 | 0.38 | -1.86 | DEMO at most (IS t 2.3) |
| F15 | 0.60-0.88 | +8.67 | 1.55 | 1.17 | -12.6 | DEMO (count-capped, cost-insensitive) |
| F16 | 0.48-0.58 | +1.29 | 0.31 | 0.23 | -14.7 | DEMO at most (decaying) |
| F23 | 0.54-0.82 | +1.25 | 1.54 (1.88) | 1.17 | -1.15 | none (IS t 0.9-1.5) |
| M2 | 0.75 | +0.69 | 1.63 | 1.24 | -0.23 | DEMO only at the lower bound (IS t 1.4 / 2.6) |
| I3 | 0.56-0.59 | +0.46 | 1.82 | 1.38 | -0.03 | none (IS t < 0: IC's wide 2016-21 spreads set the upper bound) |
| I4 | 0.80 | +0.88 | 1.21 | 0.92 | -1.21 | none |
| N1a / N1b / N1c | 0.52 (floor) - 4.9 (IC) | -2.9 at IC's spread | -27 (+14) | -21 (+10.8) | +0.64 / +0.35 / +0.67 | LIVE only if the 17:00-18:00 NY round trip is <= ~0.6 bp, which no venue offers at the rollover |
| all others | | <= +0.9 | <= 1.0 | <= 0.8 | < 0 | none |

Expected answer, stated before computing: **no row reaches LIVE at a realistic venue cost**. The rows with LIVE-like
gross power need a round trip <= 0.16 bp (the ECB pre-fix slot, contaminated) or a sub-1-bp cost at the 17:00 NY
rollover (N1). A few PRE / declared rows can meet the DEMO numbers (F2 / F4 contaminated; F8, F14, F15, F16 near the
IS gate); their VAL-size power is 0.2-1.2, so even a DEMO pass gives a HOLD that cannot confirm LIVE. The empirical
recompute below decides; this table is not the verdict.

## Amendment 0 (2026-10-31 15:13 UTC from `date -u`, before any stream-M number was computed)
- **Signal latency, one uniform reading**: every data-driven side or selection ends its signal one minute before the
  entry quote (signal on the price at X - 1 min when the record says "p(X)" and the entry is at X), so the window
  traded is the recorded one and the signal is causal with one minute to act. Rows affected: F8 (06:00 -> 09:59 UTC,
  entry 10:00), M4 (p(06:59)), M7 (p(13:24)), M11 (p(08:19)), I3 (p(16:03)), I4 (p(09:40)), I5 (p(16:33)), I8 (p(09:29)
  vs the previous 16:00 close), E1x (p(14:14)), E2x (p(14:29)), C1 (p(23:29)). Rows already with a gap keep theirs (I1,
  I6, I10, M2, N1).
- **N1 random control** = round 23's declared one (random whole-hour boundary H from 18:00 to 15:00 NY in the same
  session, g_H = mid(bar H) - mid(bar H - 2) in pips, |g_H| >= 1 (2 for N1c), fade, entry fill bar H + 1, exit fill bar
  H + 60, venue upper-bound cost), not the +-180 minute shift (which would sit inside the rollover hour).
- N1 fills follow round 23: a "fill at X" is the close of the bar labelled X.
