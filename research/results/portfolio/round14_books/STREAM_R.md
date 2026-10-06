# Stream R: conditions that should double the stable clock effects (E1 first)

Hypotheses with UTC times: [HYPOTHESES_R.md](HYPOTHESES_R.md) (written 01:49-01:53 UTC, before any number; post-hoc
additions marked R6). HOLD was never loaded. The panel ends 2024-12-31, Dukascopy ends 2015-12-31, and the date list
stops at 2024-12-31.

## Answer
- **No LIVE rule and no new DEMO rule. No PREREG_DRAFT.**
- No mechanism-derived condition doubles E1 in all three eras.
  - The best is **USD-TOP**: the dollar's overnight move on USDJPY and USDCHF is in the top tercile.
    - E1's mid on those days is 1.09x / 1.72x / 1.55x the all-day mean in PRE / IS / VAL.
    - Net is +2.47 / +2.43 bp (t 3.81 / 2.41) in IS / VAL, at a per-trade Sharpe of 0.170 / 0.150.
    - It trades 84 times a year, so its power is **2.05 / 1.83**, about the same as E1's 1.78 / 1.88.
- **The selectors do not beat chance as a family.**
  - Best IS uplift t: 3.16 against a shared null 95th percentile of 3.31 (p 0.08).
  - Best VAL uplift t: 3.12 against 3.90 (p 0.17).
  - No selector has an uplift t of 2 or more in PRE.
- **Using them as lot sizing does not help either** (post hoc). With the lot at 2x on selector days and 0.5x on the
  others, E1's per-day power is at most 2.14 (IS) / 2.02 (VAL).
- **One mechanism check works.** On TARGET2 closing days, the ECB publishes no reference rate. On those days E1
  reverses: -3.9 bp (block-clustered t -2.7, 35 blocks, 2004-24), against +1.8 on other days. This supports the
  ECB-fix part of E1's mechanism. These days come about 3 times a year, so they can't be traded.

## How this differs from round 10 E and round 12 L
- **Round 10 E** conditioned 15-minute fix legs (ECB, WM/R, SGE, Sydney) on how much a unit of flow moves the price:
  20-day realised-vol terciles and pre-window activity. It found about 1.5x, with the spread rising alongside.
- **Round 12 L** conditioned sub-cost legs on proxies for the flow's size: dip buying, month-end, holidays and
  leveraged-ETF moves.
- **This stream differs in four ways:**
  - The objects are the 2-hour clock effects that were stable across PRE / IS / VAL and already at or above cost
    (E1 is net > 0 in every era). A factor of 1.5-2 would therefore have been enough.
  - The selectors are signed prior moves, not vol or activity: the pair's own morning, yesterday's window, the
    trailing 20-day effect, and the overnight dollar.
  - The calendar conditions ask whether the fix happens at all (TARGET closures), not how big the fix is. They add
    ECB decision days and the weeks when London and New York are 4 hours apart.
  - Every cell is reported in three eras, including PRE 2004-15.

## Design
- **Objects** (side and window from stream M, not re-optimised):
  - O1 = E1: EURUSD short 11:00-13:00 London.
  - O2: EURUSD short 12:45-13:00 London, the ECB pre-fix slot. In PRE the effect sat in 11:45-12:00; this is
    disclosed in the hypotheses.
  - O3: USDJPY long 11:00-13:00 London.
  - O4 = E2: USDCHF long 10:00-12:00 UTC.
  - O5 = G1: GBPJPY long 17:30-21:30 London.
- **Reproduction.** The code reproduces stream M exactly for all five objects. For example, E1 has n 3054 / 1525 /
  765, mid +1.69 / +1.80 / +1.97, and cost 0.67 / 0.63 / 0.62. The first build of the rollover exclusion had a bug,
  which this reproduction check caught and fixed.
- **Selectors.** Each is signed by the object's side, uses data up to 1 minute before entry, and has two levels: HALF
  (> 0) and TOP (above the trailing 250-day 67th percentile).
  - S1 MORN: the pair's own move over the 4 hours before entry.
  - S2 PREV: yesterday's move over the same window.
  - S3 TRAIL: the 20-day trailing mean of the window's return.
  - S4 USD: the overnight dollar on the other USD pairs, from 18:00 NY the previous day to 06:59 London.
  - S5 RISK: US500 from 09:30 to 12:29 NY (O5 only, IS/VAL only).
- **Exclusions:**
  - X1: ECB decision days;
  - X2: the weekday before an ECB decision;
  - X3: home holidays (TARGET2 for O1-O3, Zurich for O4, US for O5);
  - X4: German-only holidays (O1-O3);
  - X5: the weeks when London and New York are 4 hours apart;
  - XC: X1, X3 and X5 together.
  - Each selector was also run inside XC.
- **K = 96 counted cells.** The placebo holidays (JPY / AUD / CAD / NZD holidays that are not EUR, GBP, CHF or US
  holidays), US holidays (seen in round 13) and the 2004-06 six-hour DST weeks are information only.
- **Gate for a survivor:** the uplift (selected minus other days, signed by the prediction) is > 0 in every era with
  data, and net is > 0 in IS and VAL. Survivors then get the full set of checks: by year, x1.5, +1 minute,
  random-entry control and C3 correlation.

## Results: all-days references and the cells that passed the gate
Mid bp (t) on the object's side. "x" = selected mid / all-day mid by era. Net = after half the spread in, half out
and the 0.6 bp commission. Power = per-trade net Sharpe x sqrt(1.73 x trades per year); for a VAL row this is the
expected HOLD t at the VAL size.

| cell | trades/y | PRE mid (t) | IS mid (t) | VAL mid (t) | x PRE / IS / VAL | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 all days (reference) | 254 | +1.69 (5.2) | +1.80 (5.1) | +1.97 (3.6) | 1 | 0.63 / 0.62 | +1.17 (3.29) / +1.35 (2.46) | 1.10 | 1.78 / 1.88 | registered DEMO (r13) |
| O1 **USD-TOP** | 84 | +1.84 (3.3) | +3.10 (4.8) | +3.05 (3.0) | 1.09 / 1.72 / 1.55 | 0.63 / 0.62 | +2.47 (3.81) / +2.43 (2.41) | 0.98 | 2.05 / 1.83 | fails power; PRE uplift t 0.47 |
| O1 USD-TOP&XC | 76 | +1.82 (3.3) | +2.62 (4.3) | +3.36 (3.3) | 1.08 / 1.46 / 1.71 | 0.63 / 0.62 | +1.99 (3.25) / +2.74 (2.67) | 1.28 | 1.74 / 2.03 | fails power |
| O1 USD-HALF | 128 | +1.90 (4.2) | +2.24 (4.5) | +2.30 (2.8) | 1.12 / 1.24 / 1.17 | 0.63 / 0.63 | +1.61 (3.23) / +1.67 (2.06) | 1.03 | 1.74 / 1.56 | fails power |
| O1 MORN-HALF | 128 | +2.06 (4.6) | +2.25 (4.5) | +2.31 (2.9) | 1.22 / 1.25 / 1.17 | 0.63 / 0.62 | +1.62 (3.24) / +1.69 (2.15) | 1.03 | 1.74 / 1.63 | fails power |
| O1 MORN-HALF&XC | 115 | +1.96 (4.4) | +2.04 (4.4) | +2.62 (3.3) | 1.16 / 1.13 / 1.33 | 0.63 / 0.62 | +1.41 (3.04) / +2.00 (2.49) | 1.28 | 1.63 / 1.89 | fails power |
| O1 MORN-TOP&XC | 74 | +1.82 (3.1) | +2.62 (4.4) | +2.32 (2.2) | 1.08 / 1.46 / 1.18 | 0.63 / 0.62 | +1.99 (3.31) / +1.70 (1.63) | 0.89 | 1.78 / 1.24 | fails power |
| O1 X-HOMEHOL (no TARGET closures) | 252 | +1.77 (5.4) | +1.82 (5.1) | +2.03 (3.7) | 1.05 / 1.01 / 1.03 | 0.63 / 0.62 | +1.18 (3.32) / +1.41 (2.55) | 1.12 | 1.78 / 1.93 | = E1 |
| O2 TRAIL-HALF | 188 | +0.65 (3.5) | +1.30 (6.0) | +1.58 (5.8) | 1.25 / 1.19 / 1.41 | 0.66 / 0.63 | +0.64 (2.99) / +0.95 (3.50) | 1.21 | 1.60 / **2.66** | fails power; PRE net < 0; E1 component |
| O2 PREV-HALF | 144 | +0.65 (3.4) | +1.25 (5.2) | +1.27 (4.1) | 1.25 / 1.15 / 1.13 | 0.66 / 0.63 | +0.59 (2.48) / +0.64 (2.08) | 1.01 | 1.33 / 1.58 | fails |
| O2 X-HOMEHOL | 252 | +0.53 (3.7) | +1.11 (6.0) | +1.14 (4.6) | 1.02 / 1.02 / 1.02 | 0.67 / 0.62 | +0.44 (2.41) / +0.52 (2.09) | 1.03 | 1.30 / 1.59 | fails |
| O3 MORN-HALF | 130 | +1.17 (2.9) | +0.94 (2.0) | +1.25 (1.7) | 1.08 / 1.07 / 1.32 | 0.74 / 0.69 | +0.20 (0.43) / +0.56 (0.76) | 1.33 | 0.23 / 0.57 | fails (net t) |
| O4 **MORN-TOP** | 82 | +2.27 (3.9) | +1.97 (3.2) | +1.58 (1.8) | 1.50 / 1.93 / 1.46 | 0.93 / 0.87 | +1.04 (1.67) / +0.71 (0.82) | 0.80 | 0.90 / 0.62 | fails (cost); the only roughly 1.5x-in-every-era selector |
| O4 MORN-TOP&XC | 72 | +2.29 (3.6) | +1.89 (3.0) | +1.72 (2.0) | 1.52 / 1.85 / 1.59 | 0.92 / 0.87 | +0.97 (1.53) / +0.85 (0.97) | 0.91 | 0.82 / 0.73 | fails |
| O5 TRAIL-TOP | 80 | +2.46 (2.5) | +1.73 (2.0) | +1.62 (1.3) | 1.11 / 1.05 / 1.13 | 1.30 / 1.12 | +0.43 (0.49) / +0.50 (0.39) | 0.93 | 0.26 / 0.30 | fails |

Not in the table: O3 X-DEONLY, O4 X-DST4, O4 XC and O5 RISK-TOP passed the gate too, but their net t is below 0.8.
76 of the 96 cells failed the gate. The complete per-cell table, with uplift t by era, is in `r1.out`.

### Checks on the cells that passed the gate (r2.out)
| cell | x1.5 net IS / VAL | +1 min net IS / VAL | years net > 0 (PRE, IS, VAL) | random entries beaten IS / VAL | C3 corr daily / monthly |
|---|---|---|---|---|---|
| O1 USD-TOP | +2.45 / +2.42 | +2.38 / +2.12 | 8/12, 6/6, 3/3 | 100 % / 99.0 % | +0.015 / +0.142 |
| O1 USD-TOP&XC | +1.97 / +2.73 | +1.91 / +2.38 | 10/12, 6/6, 3/3 | 100 % / 99.7 % | +0.019 / +0.110 |
| O1 MORN-HALF | +1.60 / +1.68 | +1.49 / +1.41 | 10/12, 5/6, 3/3 | 100 % / 97.0 % | +0.021 / +0.092 |
| O2 TRAIL-HALF | +0.61 / +0.94 | +0.60 / +0.55 | 5/12, 5/6, 2/3 | 100 % / 100 % | +0.012 / +0.072 |
| O4 MORN-TOP | +0.88 / +0.57 | +0.68 / +0.62 | 8/12, 5/6, 1/3 | 100 % / 91.0 % | +0.063 / +0.134 |
| O5 RISK-TOP | +0.35 / +0.54 | +0.64 / +0.98 | -, 3/6, 3/3 | n/a (signal overlaps the random windows) | +0.025 / +0.162 |

The random-entry control picks a random 15-minute start (London 07:00-16:00, NY 08:00-12:45 for O5) on every day and
recomputes the selector at that start, look-ahead free. It mostly shows that E1's window beats other windows, which
was already known. The test that matters for conditioning is the uplift and its null.

### Uplift by era for the selectors (selected minus other days, mid bp, Welch t), O1 = E1
| selector | PRE | IS | VAL |
|---|---|---|---|
| MORN-HALF / TOP | +0.76 (1.2) / +0.99 (1.4) | +0.91 (1.3) / +0.98 (1.3) | +0.66 (0.6) / -0.20 (-0.2) |
| PREV-HALF / TOP | +0.19 (0.3) / +0.16 (0.2) | -1.21 (-1.7) / -0.12 (-0.2) | -0.31 (-0.3) / -0.05 (0.0) |
| TRAIL-HALF / TOP | -0.04 (-0.1) / -0.13 (-0.2) | +0.22 (0.3) / +0.13 (0.2) | +0.57 (0.5) / +2.07 (1.7) |
| USD-HALF / TOP | +0.43 (0.7) / +0.32 (0.5) | +0.98 (1.4) / +2.01 (2.6) | +0.73 (0.7) / +1.69 (1.4) |

### Shared permutation null over all 96 counted cells (1,000 draws, r1.out)
| statistic | best observed | null max: median / 95 % | p |
|---|---|---|---|
| uplift t IS (flags circularly shifted within era, one shift per draw) | +3.16 (O2 TRAIL-TOP) | 2.40 / 3.31 | 0.081 |
| uplift t VAL | +3.12 (O2 TRAIL-HALF) | 2.41 / 3.90 | 0.168 |
| selected-cell net t IS (per-date sign flips) | +4.66 (O2 TRAIL-TOP&XC) | 1.98 / 3.08 | < 0.001: this is E1's own edge, not the conditioning |

## Calendar conditions: the mechanism checks (r3.out; holiday t clustered by block)
E1 mid bp on these days, against the other weekdays (about +1.7 to +1.8). The 2004-24 column pools all eras.

| days | PRE | IS | VAL | 2004-24 | prediction | reading |
|---|---|---|---|---|---|---|
| TARGET2 closed (no ECB fix: Good Friday, Easter Monday, 1 May) | -6.1 (t -2.8) | +0.2 (0.1) | -3.3 (-1.2) | **-3.9 (t -2.7, 35 blocks)** | ~0 | supports the fix mechanism; ~3 days a year |
| ECB pre-fix slot (O2) on TARGET2-closed days | -0.2 | -0.6 | -0.7 | -0.35 (t -0.6) vs +0.78 | ~0 | consistent |
| German-only holidays (fix published, Germany away) | +8.3 (t 4.8) | +0.1 | +4.0 (1.6) | +5.2 (t 4.0) | smaller | **wrong sign**: larger, as an impact-per-flow story would predict, but zero in IS; ~4 days a year |
| ECB decision days | +3.9 (1.9) | +6.0 (1.5) | +0.5 (0.1) | +4.0 (t 2.4) | unsigned | wrong sign: the euro fell more on decision days through 2021 (dovish ECB); gone in VAL (decision moved to 14:15 CET, outside the window) |
| weekday before ECB | (see r1: uplift -0.3 / -3.6 / -3.9) | | | | smaller | wrong sign, noise |
| London-NY 4 h weeks | uplift +0.6 / -2.1 / +2.3 | | | | smaller | no pattern |
| placebo holidays (JPY / AUD / CAD / NZD only) | +2.9 (t 2.5) | +1.7 | +2.2 | +2.4 (t 3.2) | none | **the placebo is not null**: E1, E2 and G1 are all larger on these days (pooled t 3.2 / 3.1 / 3.2). Thin liquidity elsewhere seems to raise the impact of the same clock flow. Post hoc; ~21 days a year, power < 1 |

## Post-hoc arithmetic (not candidates)
- **Sizing instead of filtering.** E1 every day, with the lot at 2x on selector days and 0.5x otherwise (inside the
  user's 0.5-2x range). The best per-day Sharpe is 0.102 IS / 0.096 VAL (USD-TOP; power 2.14 / 2.02), against a flat
  0.084 / 0.089. In PRE it is lower than flat: 0.051 against 0.057.
- **G1 with S1 flipped**: long GBPJPY in the NY afternoon only after the pair fell in the NY morning.
  - Mid +3.55 / +2.04 / +2.45 (t 4.4 / 2.8 / 2.0); net +2.04 / +0.79 / +1.34.
  - Power 0.96 / 0.58 / 0.83: an afternoon reversal, far from the bar.

## What this says
- E1's conditional structure is weak. Every signed-flow selector moves E1 by a factor of 0.9-1.7, and none does so
  in all three eras. The largest uplifts (USD-TOP 1.7x IS, TRAIL-TOP 1.7x VAL) are IS-only or VAL-only, and they sit
  inside the null of 96 cells.
- The frontier arithmetic holds. Keeping a third of the days at 1.6x leaves the power where it was, because the
  trade count falls by 3x. LIVE needs about 2.1x on a third of the days, or 1.8x on half, in every era.
- USDCHF midday is the one object with a stable ~1.5x selector (its own 4-hour morning move in the top tercile,
  1.50 / 1.93 / 1.46x). USDCHF's ~0.9 bp cost leaves it at net t 1.7 / 0.8.
- Mechanism evidence:
  - The ECB-fix leg disappears when the fix is not published. E1 turns negative on TARGET2 closing days, -3.9 bp,
    t -2.7 over 21 years.
  - Holidays outside Europe and the US enlarge E1, E2 and G1, which fits an impact-per-unit-of-flow story.
  - Neither condition is frequent enough to trade.
- Disclosure for the lead: E1's HOLD has been opened (round 13, +0.64 net, +1 minute -0.00). A HOLD test of any E1
  subset would not be blind to that aggregate.

## Directions that need the user
1. None of these conditions changes the decision on E1 (demo or not). If E1 runs on demo, the TARGET2-closure days
   (about 3 a year) can be skipped on mechanism grounds alone.
2. A daily flow measure for the ECB fix (fix volumes, or euro-area portfolio-flow data from the ECB SDW) would be a
   direct size proxy, where these signed moves are indirect. Fetching it is a data decision for the user.

## Scripts and outputs
Folder `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r14/R/`:
- `mcommon.py`: stream M's module, copied (output folder changed).
- `rbase.py`: the weekday list 2004-24, the objects' returns, costs and +1 minute versions, the selectors and the
  calendars. Output `base.npz`.
- `r1_cells.py`: the 96 counted cells plus the information cells, and the shared permutation null. Outputs `r1.out`,
  `r1_cells.json`, `r1_perm.npz`.
- `r2_survivors.py`: the gate survivors (by year, x1.5, +1 minute, random-entry control, C3). Output `r2.out`.
- `r3_holidays_sizing.py`: the block-clustered holiday cells and the post-hoc sizing and flip. Output `r3.out`.
