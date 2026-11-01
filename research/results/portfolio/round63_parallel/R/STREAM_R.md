# Round 63 stream R: auction-cycle concession in sovereign bond futures, 2026-10-31

Written 2026-10-31 15:56 UTC (from `date -u`). Hypotheses: [HYPOTHESES_R.md](HYPOTHESES_R.md), declared 15:50:54 UTC
before any return was computed. Nothing was amended after that. HOLD stayed closed. Every yield and auction series is
cut at 2024-12-31 at parse, and the cut is asserted again at load. No 2025-26 value was printed or summarised. No
network request was made.

## Answer
**None: no LIVE and no DEMO candidate, so there is no PREREG_DRAFT.**

The concession itself is real at mid. Across 2004-21, Treasury yields rise into scheduled auctions and fall after
them. The full-cycle cell CYC-ALL has a mid IS t of 3.98, against a random-calendar best-of-30 p95 of 2.31 (p < 0.005).
- **The effect has decayed.** In 2004-15 it is about 4-5 yield bp per US cycle (net +3.8, t 5.0). In 2016-21 it is
  about 2.7 bp. Net of one tick plus commission per side, the primary CYC-ALL is +0.88 bp in IS (t 1.73).
- **It fails VAL 2022-24.** The post-auction long lost: POST3-US VAL net -2.30, t -2.04. That is worse than random
  days: only 25 % of random seeds score lower. The pre-auction short worked in VAL but not in IS.
- **No cell reaches HOLD power above 1.5.**

Round 41 never tested the bond yields themselves; it only tested FX, gold and indices. So this is the first direct
test of the concession, and it closes the family for bond futures at daily closes.

## Data (reused, nothing pulled)
| item | source / file | span used |
|---|---|---|
| Auction calendars | round 41 `auctions.json` (fiscaldata, MoF xls, Finanzagentur), copied to `research/data/ust_auctions/auctions.json` | 2004-24 |
| Events used | US nominal coupons (2/3/5/7/10/20/30Y; TIPS and FRNs out), 1,395; JGB 10Y, 264 (all JGB tenors 1,334, information only); Bund 10Y (`Bund|10 Y`), 239 | ALL pool 1,898 |
| Yields | round 46 raw files re-parsed to `research/data/ust_auctions/yields.json`. US par curve (3M-30Y; 30Y missing 2004-05). MoF JGB par curve (1Y-40Y). Bundesbank Svensson 10Y. ECB deposit rate (2014+) from `research/data/rates/ECBDFR.csv` for DE carry | 2003/04-2024 |
Only the Bund 10Y yield is on disk, so Schatz, Bobl and Buxl are untested; see "Decisions".

## Method (as declared)
- **Trade size and units.** One DV01 unit of the matching future per trade. Returns are in **yield bp**. In price
  terms, 1 yield bp is about 6-8 bp of a ZN contract.
- **Carry.** Modelled as `(y_T - y_fin) x days / 365 / MD`, where y_fin is US 3M, JP 1Y or the ECB deposit rate. It
  is under 0.15 bp per trade. Roll-down is ignored.
- **Basis.** The gap between the par yield and the future's CTD is ignored.
- **Fill timing.** Fills are at daily closes. The yield fix comes after the auction in all three countries. The CBOT
  settlement is about 30 minutes before the 15:30 ET CMT quote.
- **Costs.** A flat **0.30 yield bp per side**: one tick plus commission on ZT / ZF / ZN / ZB / UB / FGBL / OSE JGB,
  taking the most expensive contract (table in HYPOTHESES). That is 0.6 bp per round trip and 1.2 bp for CYC, which
  has two legs. The x1.5 check uses 0.45 per side.
- **Eras.** PRE 2004-15, IS 2016-21, VAL 2022-24.
- **t statistic.** Newey-West (lag 10) on the daily equal-DV01 book.
- **Random benchmark.** 1,000 seeds. Each seed moves every event to a random non-auction day of the same country and
  year, with the same tenor and the same rule.
- **Chance null.** The best IS t over the 30 cells, under 200 random calendars, with one draw per event shared by all
  cells.

## Results (net yield bp per trade; t on the daily book)
`x1.5` = costs x1.5, IS / VAL t. `late` = entry and exit one business day later, IS / VAL net. `yrs+` = positive
years 2016-24. `power` = the lower of the per-trade and book power at VAL size.
| cell | PRE net (t) | IS n, mid / net (t) | VAL n, mid / net (t) | random IS / VAL | x1.5 IS / VAL t | late IS / VAL net | yrs+ | power |
|---|---|---|---|---|---|---|---|---|
| **CYC-ALL (primary)** | +2.83 (4.99) | 607, +2.16 / **+0.88 (1.73)** | 330, -0.05 / **-1.21 (-0.97)** | 100 / 23 % | 0.60 / -1.43 | 0.00 / -1.43 | 6/9 | -0.95 |
| CYC-US | +3.77 (4.98) | 454, +2.66 / +1.36 (2.09) | 252, -0.51 / -1.65 (-1.04) | 100 / 17 % | 1.19 / -1.40 | +0.36 / -1.63 | 6/9 | -1.07 |
| CYC-JP10 | +0.75 (1.43) | 72, +1.04 / -0.18 (-0.16) | 35, +0.55 / -0.72 (-0.79) | 99 / 58 % | | | 3/9 | -0.62 |
| CYC-DE10 | -0.41 (-0.25) | 81, +0.36 / -0.87 (-0.84) | 43, +2.16 / +1.00 (0.37) | 68 / 70 % | | | 4/9 | 0.29 |
| POST3-ALL | +1.87 (5.18) | 606, +1.18 / +0.69 (1.87) | 332, -1.47 / -2.14 (-2.25) | 100 / 23 % | 1.09 / -2.56 | +0.15 / -2.32 | 4/9 | -2.60 |
| POST3-US | +2.28 (5.05) | 454, +1.47 / +1.01 (2.18) | 252, -1.62 / -2.30 (-2.04) | 100 / 25 % | 1.55 / -2.30 | +0.36 / -2.36 | 4/9 | -2.24 |
| POST2-US | +1.41 (4.22) | 454, +1.07 / +0.55 (1.59) | 252, -0.94 / -1.59 (-1.93) | 100 / 36 % | | | 3/9 | -1.91 |
| POST1-US | +0.30 (1.48) | 454, +0.69 / +0.12 (0.63) | 252, -0.26 / -0.88 (-2.08) | 100 / 68 % | | | 4/9 | -1.62 |
| PRE5-1-ALL | +0.31 (0.71) | 607, +0.45 / -0.30 (-0.66) | 330, +2.57 / +2.06 (1.92) | 99 / 98 % | -1.30 / 1.64 | +0.45 / +0.75 | 7/9 | 1.50 |
| PRE5-1-US | +0.74 (1.33) | 454, +0.38 / -0.40 (-0.70) | 252, +2.70 / +2.21 (1.76) | 98 / 94 % | | | 7/9 | 1.37 |
| PRE5-0-ALL | +0.97 (1.93) | 607, +1.01 / +0.22 (0.39) | 330, +1.39 / +0.90 (0.76) | 100 / 35 % | | | 6/9 | 0.60 |
| PRE5-1-DE10 | -1.98 (-2.31) | 81, +1.05 / +0.37 (0.43) | 43, +3.72 / +3.21 (1.69) | 97 / 90 % | | | 6/9 | 1.26 |
| SIZE-PRE5-0-US | +3.74 (2.87) | 227, +0.98 / +0.20 (0.26) | 104, -1.96 / -2.12 (-1.21) | 100 / 7 % | | | 4/9 | -1.29 |
| SIZE-POST3-US | +4.58 (4.29) | 227, +1.19 / +0.70 (1.25) | 104, -0.82 / -1.65 (-0.98) | 100 / 30 % | | | 4/9 | -1.09 |
| **WEAK-POST3-US** (dealer share > previous-12 median) | +2.24 (3.34) | 187, +2.04 / **+1.59 (2.11)** | 91, +1.22 / **+0.51 (0.21)** | 100 / 95 % | 1.74 / 0.05 | **+0.97 / -0.12** | 6/9 | 0.16 |
| WEAK-POST3-ALL | +1.66 (3.29) | 252, +1.56 / +1.07 (1.89) | 122, +0.94 / +0.27 (0.13) | 100 / 96 % | 1.39 / -0.09 | +0.53 / -0.31 | 6/9 | 0.10 |
All 30 cells, plus 6 JP all-tenor information cells, are in [out/grade.txt](out/grade.txt). Every JP all-tenor cell
loses net in IS (t -1.1 to -3.2). The JGB mid moves are about 0.3-0.6 bp, smaller than the cost.

**Per year** (sum of the net book in yield bp). US CYC:

| | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US CYC | +106 | +6 | +90 | +17 | +735 | +682 | +380 | +278 | +46 | +153 | +112 | -33 | +54 | +127 | +224 | -155 | +112 | +272 | +35 | -353 | -109 |

- PRE: 11 of 12 years positive. 2008-11 carry most of the total.
- IS: 5 of 6 years positive.
- VAL: 1 of 3 years positive.
- US POST3 is negative in each of 2022, 2023 and 2024 (-235, -193, -164).

Per tenor ([out/posthoc.txt](out/posthoc.txt)): US POST3 is positive in VAL for no tenor. 20Y (-4.3) and 30Y (-3.0)
are the worst.

## Chance and the max-over-cells null
- **Declared null (net IS t, best of 30 cells).** Median 0.15, p95 1.00. It is low because costs push every
  random-calendar cell negative. The best real net IS t, 2.18 for POST3-US, is above it. That only says the auction
  calendar beats random days in IS. The VAL check is what the cells fail.
- **Mid version (post hoc, information only).** Median 1.39, p95 2.31. The real best is CYC-ALL at 3.98 (p < 0.005).
  POST1, POST2, POST3 and CYC on US and ALL all have mid IS t of 3.2-4.0. **The 2016-21 concession is not chance.**
  It is small, though: about 2 yield bp per cycle against about 1.2 bp of cost. And it did not survive into 2022-24.

## What failed and why
- **The cost is not the binding constraint.** At half a tick plus commission (0.165 bp per side), about the
  real cost of crossing a one-tick ZN market, CYC-ALL reaches IS +1.42 bp (t 2.74) and VAL -0.67 bp (t -0.55).
  POST3-US reaches IS +1.28 bp (t 2.74) and VAL -2.03 bp. VAL is the failure at any cost.
- **VAL 2022-24 is a supply-driven bear market** (QT, larger coupon sizes, the 2023 refunding term-premium shock).
  - Yields kept rising after auctions instead of retracing, so the post-auction long lost even against random days.
  - The pre-auction short gained (PRE5-1-ALL VAL +2.06, t 1.92, random 98 %). But it was negative in IS (-0.30) and
    weak in PRE (+0.31).
  - The two halves of the cycle trade places with the rate regime, which is not a stable rule. CYC sums both halves
    and is roughly trend-neutral, yet it is flat at mid in VAL (-0.05).
- **Decay.** The cycle is about 4-5 bp per US cycle in 2004-15 (dominated by 2008-11 supply and volatility), about
  2.7 bp in 2016-21, and about 0 in 2022-24. This is consistent with post-publication arbitrage, given LYZ's sample
  of 1980-2008 and publication in 2013.
- **Near miss, not a pass: WEAK-POST3-US.** It is long for three days after US auctions where primary dealers took
  more than their recent median.
  - It meets the DEMO numbers: IS +1.59 (t 2.11), VAL +0.51 > 0, random 100 / 95 %, x1.5 VAL net +0.21.
  - It **fails the one-step-late check in VAL** (-0.12, t -0.14). Its VAL t is 0.21 and its power at VAL size is
    0.16. Its IS t is one of 30 cells.
  - It is not drafted.
- **Japan and Germany add nothing.** JP10 and DE10 have about 12 auctions a year each, and their mid moves are under
  1 bp. Every JP10 / DE10 cell has IS t < 0.5 net, and none reaches DEMO.

## Pitfalls
- **Old scratchpads.** The round 41 / 46 scratchpad files still existed. Their contents are now copied, HOLD-cut, to
  `research/data/ust_auctions/` (`yields.json`, `auctions.json`). Rerun from there.
- **US calendar gaps.** The US 20Y appears only from 2020 and the 30Y yield is missing in 2004-05, so their PRE cells
  are NaN. US auction counts are only 36-40 a year in 2004-08 (no 7Y until 2009, the 3Y paused in 2007-08), against
  72-85 from 2009.
- **Bund labels.** Bund 10Y auctions are `Bund|10 Y`. Reopenings with 9 or 11 years left are labelled the same.
  Green 10Y bonds are excluded.
- **The declared net null is uninformative.** A net-return random-calendar null sits far below 0 because of costs.
  Compare the mid null as well, or the per-cell random benchmark.

## Decisions for the user / coordinator
| direction | value |
|---|---|
| Pull Bundesbank 2Y / 5Y / 30Y Svensson yields (host not on this round's allowed list) for Schatz / Bobl / Buxl auctions | LIVE < 1 %, DEMO ~2 % (DE10 mid moves < 1 bp) |
| Intraday futures data (paid, or a CME / Eurex vendor) for an auction-day intraday concession (the 2-3 hours before the 13:00 ET deadline) | LIVE ~1 %, DEMO ~3 % |
| When-issued yields (paid) for a US tail-conditioned reversal | LIVE < 1 %, DEMO ~2 % |
| HOLD check of WEAK-POST3-US (would need 2025-26 Treasury par yields, the auction calendar and an exception to the late bar) | not recommended |

## Files
- [HYPOTHESES_R.md](HYPOTHESES_R.md), STREAM_R.md (this file). There is no PREREG_DRAFT.
- Code in `code/`:
  - `parse.py` copies the HOLD-cut inputs to `research/data/ust_auctions/`.
  - `lib.py` holds the loaders, events, rules and Newey-West.
  - `grade.py` grades the 30 cells, runs the random benchmark and the null, and writes `out/grade.json`,
    `out/grade.txt` and `out/run.log`.
  - `posthoc.py` writes `out/posthoc.txt` (per year, per tenor, mid null).
- Data: `research/data/ust_auctions/yields.json`, `research/data/ust_auctions/auctions.json`. No requests were made,
  so there is no `requests.log`.
