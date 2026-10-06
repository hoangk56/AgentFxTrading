# Stream Q: one book of stable clock effects (PRE + IS selection, VAL check)

Hypotheses with UTC times: [HYPOTHESES_Q.md](HYPOTHESES_Q.md). Draft: [PREREG_DRAFT_Q_primary_book.md](PREREG_DRAFT_Q_primary_book.md)
(written because the brief requires it; it recommends no new registration). HOLD was never loaded: the panel ends
2024-12-31 and Dukascopy 2015-12-31.

## Answer
- **No book reaches LIVE.** The best VAL power is 2.01 (bar 3). The books that keep their VAL size are the ones that
  are mostly E1 (EURUSD short in the European midday), and those reach E1's own power, 1.9-2.0.
- **The sqrt(k) gain exists in IS and is gone in VAL.** The largest book (9 legs) has IS day Sharpe 0.141, power 2.98,
  in-sample. In VAL it falls to 0.050, power 1.05. Its 8 non-EURUSD legs together make -0.04 bp a day in VAL (t -0.06),
  against +2.64 (t 4.90) in IS.
- **Decay is what limits the book, not correlation.** Cross-symbol correlation costs about 10 % of the Sharpe in IS.
  The rest is lost because 5 of the 9 legs keep less than 20 % of their IS net in VAL. Costs make this worse: a 30-60 %
  fall in mid turns a 0.7-0.9 bp net leg into about 0.
- **The pool of usable legs is thin.** Outside the EURUSD midday family, few PRE-carried, IS-confirmed cells pay their
  cost. Set B (stream M's 500) has 25 such cells, 10 of them with IS net t >= 1; after the per-symbol non-overlap rule only one leg remains besides E1.
  The wider pool (|t_PRE| >= 3.5) gives 3-9 legs.
- All 12 books meet the DEMO numbers formally (IS t >= 2, VAL > 0, beat >= 90 % of random). That is because E1 is in
  every book. The declared primary book gets a draft, which recommends against registering it: it is E1 (96-98 % of
  the risk) plus a leg that decays.

## Selection rule (written before any book number; HYPOTHESES_Q.md Q1)
- Source: stream M's cells.npz (K = 270,086 cells). Only its PRE and IS columns were read.
- Pools: P_B = the top 500 by |t_PRE|; P_W = |t_PRE| >= 3.5 (1,644 cells). Side = sign of the PRE mean.
- Excluded:
  - Tokyo-fix-adjacent non-JPY cells (C3's mechanism): 186 / 512;
  - XAUUSD and AUDUSD "every day" cells (round 3 saw their HOLD hour means): 31 / 55.
- Confirmation: side t_IS (mid) >= 2.0, IS net > 0, IS net t >= tN, tN in {1.0, 1.5, 2.0}.
- Greedy by IS net t. A leg is skipped if it overlaps a chosen leg on the same symbol on any IS date, or if its daily
  P&L correlates with a chosen leg at |rho| > 0.5.
- Bots: one per symbol, one position each. At most 3 positions are open at once across a book, so one bot also fits.
- Weights:
  - W1: equal IS risk per trade;
  - W2: W1 x clip(IS Sharpe / median, 0.5, 2).
- 12 books in all (6 distinct leg sets). Declared primary: P_B, tN 1.5, W1.
- Disclosed: STREAM_M.md had already shown VAL for some families. The rule is mechanical, and every variant is
  reported.

## Legs (per trade; mid and net bp, (t); net = half the actual spread at entry and at exit + 0.6 bp)
| leg (clock, local window, days, side) | trades PRE/IS/VAL | mid PRE | mid IS | mid VAL | net IS | net VAL | VAL/IS net | in books |
|---|---|---|---|---|---|---|---|---|
| EURUSD S, LON 11:00+2h, every day (E1) | 3054/1525/765 | +1.69 (5.2) | +1.80 (5.1) | +1.97 (3.6) | +1.17 (3.3) | +1.35 (2.5) | 1.16 | P_B all |
| EURUSD S, NY 04:00+4h, every day (= 09:00-13:00 London) | 3053/1525/765 | +1.86 (3.7) | +2.46 (4.8) | +2.48 (3.1) | +1.82 (3.6) | +1.85 (2.3) | 1.02 | P_W all |
| EURJPY S, LON 05:00+2h, last weekday of a quarter | 36/18/9 | +10.7 (3.7) | +8.65 (3.1) | +9.55 (1.7) | +7.58 (2.8) | +8.47 (1.5) | 1.12 | P_W all |
| GBPUSD L, LON 15:00+1h, last weekday of the month | 132/66/33 | +8.32 (3.8) | +9.71 (2.7) | +1.87 (0.4) | +8.84 (2.4) | +1.09 (0.3) | 0.12 | P_W all |
| USDCHF L, LON 11:00+2h, every day | 3054/1525/765 | +1.27 (3.7) | +1.61 (4.7) | +0.59 (1.1) | +0.69 (2.0) | -0.28 (-0.5) | -0.41 | P_W t1.0, t1.5 |
| USDJPY S, NY 00:15+15m, last weekday of the month | 132/66/33 | +1.60 (3.7) | +2.11 (3.1) | -0.17 (-0.2) | +1.34 (2.0) | -0.92 (-0.9) | -0.69 | P_W t1.0, t1.5 |
| EURJPY L, LON 16:00+4h, every day | 3051/1526/765 | +2.17 (3.8) | +1.76 (3.6) | +1.06 (1.4) | +0.90 (1.9) | +0.17 (0.2) | 0.19 | P_W t1.0, t1.5 |
| XAUUSD L, TOK 11:00+4h, weekday before a UK holiday | 51/26/16 | +9.82 (4.4) | +6.73 (2.5) | +1.46 (0.3) | +4.84 (1.8) | +0.41 (0.1) | 0.08 | all but P_B t2.0, P_W t2.0 |
| GBPJPY L, SYD 02:45+4h, every day | 2439/1218/611 | +2.27 (3.7) | +2.12 (3.1) | +1.72 (1.9) | +0.94 (1.4) | +0.63 (0.7) | 0.67 | P_W t1.0 |
| AUDJPY L, TOK 19:00+2h, Tuesdays | 611/305/153 | +4.17 (3.8) | +2.28 (2.3) | -0.52 (-0.4) | +1.17 (1.2) | -1.57 (-1.2) | -1.34 | P_W t1.0 |

The two rare legs that hold up, EURJPY at quarter-end and (in mid only) GBPUSD at month-end, trade 3 and 11 times a
year. GBPUSD at month-end is the WM/R month-end flow that round 12 found decaying (VAL/IS 0.12 here).

## Books (bp per UTC day at the median leg's risk; t clustered by UTC day; IS is in-sample by construction)
| book | legs | IS day net (t) | IS Sharpe / power | VAL day net (t) | VAL Sharpe / power | VAL x1.5 | VAL +1 min | years > 0 | random IS / VAL (+-3 h) | C3 d / m | bar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P_B t1.0 = t1.5, W1 (**primary**) | 2 | +1.24 (3.53) | 0.090 / 1.90 | +1.35 (2.47) | 0.089 / 1.89 | +1.33 | +1.01 (1.88) | 8/9 | 100 / 98 % | +0.04 / +0.04 | DEMO numbers; it is E1 |
| P_B t1.0 = t1.5, W2 | 2 | +0.71 (3.79) | 0.097 / 2.05 | +0.68 (2.21) | 0.080 / 1.69 | +0.67 | +0.49 (1.61) | 8/9 | 100 / 97 % | +0.04 / -0.01 | as above |
| P_B t2.0 (E1 alone) | 1 | +1.17 (3.29) | 0.084 / 1.78 | +1.35 (2.46) | 0.089 / 1.88 | +1.34 | +1.04 (1.91) | 8/9 | 100 / 99 % | +0.04 / +0.06 | = stream M's E1 |
| P_W t1.0, W1 | 9 | +4.69 (4.45) | 0.114 / 2.41 | +1.52 (1.00) | 0.036 / 0.77 | +0.99 | +0.69 (0.48) | 8/9 | 100 / 90 % | +0.02 / +0.02 | fails VAL t, power |
| P_W t1.0, W2 | 9 | +4.21 (5.52) | 0.141 / 2.98 | +1.56 (1.38) | 0.050 / 1.05 | +1.24 | +1.00 (0.91) | 8/9 | 100 / 94 % | +0.02 / +0.04 | fails VAL t, power |
| P_W t1.5, W1 | 7 | +3.09 (4.31) | 0.110 / 2.33 | +1.16 (1.14) | 0.041 / 0.87 | +0.89 | +0.80 (0.80) | 8/9 | 100 / 90.5 % | +0.02 / +0.04 | fails VAL t, power |
| P_W t1.5, W2 | 7 | +1.98 (5.13) | 0.131 / 2.77 | +0.73 (1.29) | 0.047 / 0.99 | +0.58 | +0.57 (1.01) | 9/9 | 100 / 93.5 % | +0.02 / +0.02 | fails VAL t, power |
| P_W t2.0, W1 | 3 | +2.22 (4.22) | 0.108 / 2.28 | +2.05 (2.50) | 0.091 / 1.91 | +2.03 | +1.58 (1.93) | 9/9 | 100 / 99.5 % | +0.05 / +0.20 | fails power |
| P_W t2.0, W2 | 3 | +1.47 (4.72) | 0.121 / 2.55 | +1.30 (2.64) | 0.095 / 2.01 | +1.28 | +1.10 (2.19) | 9/9 | 100 / 99.5 % | +0.06 / +0.20 | fails power |

- Book days: IS 1,525-1,526 and VAL 765, so power = day Sharpe x sqrt(254 x 1.75). The power column on the VAL size
  is the expected HOLD t.
- Against random starts anywhere in the day, every book beats 99.5-100 %. The +-3 h control is the binding one.
- PRE book Sharpes (in-sample for sides) are 0.055-0.083 for every book.
- Chance: 12 books, 6 distinct leg sets, all highly correlated through the EURUSD leg. The best VAL power (2.01) is
  below the bar whatever correction is applied.

## Correlation, effective bets, and what the non-EURUSD legs add
| leg set | mean off-diagonal rho IS / VAL (max) | effective bets, eigenvalue participation | effective bets by risk share (W1 / W2) | rest of book without EURUSD, W1: IS day net (t) / VAL day net (t) |
|---|---|---|---|---|
| P_B t1.0 (2 legs) | -0.06 / -0.09 | 1.99 | 1.03 / 1.35 | +4.87 (1.79) / +0.41 (0.08), 26 / 16 days |
| P_W t1.0 (9) | +0.02 / +0.02 (0.48 EURUSD-USDCHF, 0.38-0.43 EURJPY-GBPJPY) | 8.19 | 4.60 / 4.29 | +3.11 (3.67) / -0.09 (-0.07) |
| P_W t1.5 (7) | +0.02 / +0.01 (0.48) | 6.52 | 3.23 / 4.49 | +1.85 (3.61) / -0.11 (-0.15) |
| P_W t2.0 (3) | +0.03 / +0.07 | 2.99 | 1.11 / 1.73 | +9.44 (3.40) / +4.66 (1.12), 66 / 33 days |

- The eigenvalue participation ratio counts a 3-trade-a-year leg as a whole bet. The risk-share count is the honest
  one: a 9-leg book is about 4.5 bets.

## Ceiling: every leg independent at its IS Sharpe, versus reality
| leg set (weights) | ceiling, IS Sharpes, independent: book weights / optimal weights (power) | IS actual | ceiling at VAL Sharpes, independent (book weights) | VAL actual |
|---|---|---|---|---|
| P_W t1.0 (W2) | 0.158 (3.33) / 0.170 (**3.60**) | 0.141 (2.98) | 0.054 (1.14) | 0.050 (1.05) |
| P_W t1.0 (W1) | 0.134 (2.83) / 0.170 (3.60) | 0.114 (2.41) | 0.041 (0.86) | 0.036 (0.77) |
| P_W t1.5 (W2) | 0.147 (3.11) / 0.164 (3.46) | 0.131 (2.77) | 0.048 (1.02) | 0.047 (0.99) |
| P_W t2.0 (W2) | 0.123 (2.59) / 0.132 (2.78) | 0.121 (2.55) | 0.097 (2.04) | 0.095 (2.01) |
| P_B t1.0 (W1) | 0.090 (1.89) / 0.096 (2.02) | 0.090 (1.90) | 0.088 (1.85) | 0.089 (1.89) |

- The 9-leg book would clear LIVE (power 3.3-3.6) if its legs kept their IS Sharpe. Correlation takes about 10 %
  (0.158 -> 0.141). Decay takes the rest (0.158 -> 0.054 at VAL Sharpes, with the legs still independent).
- The decay goes through cost. The every-day legs lose 30-65 % of their mid from IS to VAL: USDCHF 1.61 -> 0.59,
  EURJPY 1.76 -> 1.06, GBPJPY 2.12 -> 1.72. Their cost of 0.9-1.1 bp then takes all of what is left.
- Selection on IS net t picks the cells that were luckiest in IS. That is the IS -> VAL shrinkage stream M measured
  (VAL/IS 0.72 for the mid of carried cells), and it is larger here because the selection is on net.

## What this says
- With stream M's 11 symbols, a book of clock legs cannot do better than E1. The legs that are net > 0 in IS and
  survive VAL are E1 and its 4-hour version (the same flow) and one quarter-end cell trading 3 times a year.
- An optimally weighted book of independent legs needs about 6-8 legs at Sharpe 0.05-0.09 that hold their IS size.
  Over 21 years, no such set exists in this universe at IC's costs. Stream M's "stable and net > 0" list was 12
  cells, all in the EURUSD midday family or GBPJPY, which shows the same thing from the other side.
- Surprising: the legs did not fail through correlation. Off-diagonal rho averages about 0.02; only same-time USD
  legs (EURUSD-USDCHF, 0.3-0.5) and the yen afternoon pair (EURJPY-GBPJPY, 0.4) co-move. A book of genuinely
  independent stable clock legs would add up as theory says, if the legs existed.
- Possible lead, not tested and not selectable now: EURJPY short 05:00-07:00 London on the last weekday of each
  quarter. Mid is +10.7 / +8.7 / +9.6 bp across the three eras, but it has 3 events a year (VAL t 1.5). It is
  DEMO-sized at most, and HOLD would hold about 6 events.

## Directions that need the user
1. More symbols with a long PRE history: Dukascopy M1 2004-15 for GBPUSD, AUDUSD, NZDUSD, USDCAD, AUDJPY, XAUUSD, and
   any other major cross. The book needs about twice as many independent stable legs as this universe offers.
   Fetching a new price series is the user's decision.
2. A commission-free or lower-cost FX venue. The every-day legs that decay in mid still have VAL mids of 0.6-1.7 bp.
   At 0.3-0.5 bp of total cost, USDCHF and EURJPY (VAL mid 0.6-1.1 bp), GBPJPY (1.7) and stream M's USDJPY midday (0.95) would be marginally net > 0, and a 5-6-leg book might
   approach the ceiling above. This needs the user's broker or venue data.

## Scripts and outputs (`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r14/Q/`)
- `qcommon.py`: legs as per-UTC-day events, overlap test, random starts. Reuses stream M's `mcommon.py`.
- `select_book.py`: the selection rule, PRE and IS columns only. Output `select.out`, `selection.json`.
- `legs.py`: every leg's events in PRE / IS / VAL, plus x1.5, +1 minute and 2 x 200 random-start draws. Output
  `legs.out`, `legs.pkl`.
- `books.py`: the 12 books, correlation, effective bets, controls, power, C3 correlation and ceiling. Output
  `books.out`.
- `incr.py`: post-hoc reporting (declared 01:51 UTC), the rest of book without EURUSD and the risk shares. Output
  `incr.out`.
