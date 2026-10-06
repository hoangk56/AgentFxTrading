# Round 11: multi-day event drift, 1-5 day cross-sections, and a full index intraday scan (2026-10-06)

The user asked to keep searching after round 10
([round10_new_directions_2026-10-06.md](round10_new_directions_2026-10-06.md)) until a LIVE candidate is found. Midway
through this round they asked to stop when it ends. The brief, constraints and bars are round 10's (the
[brief](round10_new_directions/BRIEF.md) and its "Round 11 addendum").

Three streams ran in parallel. Each wrote its hypotheses before the numbers they govern; post-hoc additions are
marked. Hypotheses are in `HYPOTHESES_F/G/H.md`, write-ups in `STREAM_F/G/H.md`, all in
[round10_new_directions/](round10_new_directions/).

| stream | direction | why it might escape the limits |
|---|---|---|
| F | drift over 1-5 days after central-bank decisions and macro surprises ("delayed overshooting", Eichenbaum & Evans 1995) | round 10 found the intraday reaction priced within minutes; at 1-5 days the move per event is tens of bp against ~1-2 bp of FX cost |
| G | cross-sectional momentum / reversal across 8 currencies, 8 indices, 6 commodities at 1-5 days | only intraday relative value (round 8) and multi-week premia (round 7) had been tested; breadth adds trades for power |
| H | every 15- and 60-minute window of the commission-free index CFDs (US30, USTEC, UK100, HK50, AUS200, ES35, F40, IT40, STOXX50, US2000), plus mechanism-first index windows | FX's 0.6 bp commission is a floor (round 10); US30 costs 0.86 bp IS / 0.3 bp VAL, and no full index slot scan had been run |

## Answer

**No candidate at either bar.** Nothing was pre-registered, so HOLD (2025-01..2026-09) stayed closed. C3 remains the
only algorithm that has passed. The search stops here at the user's request.

| tier | candidates |
|---|---|
| LIVE | none |
| DEMO | none (H3 below has DEMO-like numbers, but it was picked from a 15,913-cell scan after looking, so it cannot be registered from IS/VAL) |

## F. Multi-day drift after policy and macro surprises

Rule: the surprise sign is the home currency's move in the first 30 minutes (5 for data releases). Entry is at the
first 20:50 UTC at least 90 minutes after the event, so round 10's intraday windows are excluded. Exit is after 1, 3
or 5 weekdays, capped at 5 x 24 h. Costs are actual spreads plus 0.6 bp FX commission plus swaps. t is clustered by
event date. Calendars:
- 1,877 central-bank events 2004-24 (round 10);
- 15 non-US release types 2016-24;
- US CPI 2004-24 and NFP 2004-15, from BLS archive file names.

| hypothesis (side from the literature) | where | IS mid (t) / VAL / PRE 2004-15 | cost IS / VAL | net IS (t) / VAL (t) | power IS / VAL | verdict |
|---|---|---|---|---|---|---|
| F1 continuation after a decision, 5 days (delayed overshooting) | 8 banks, home currency vs USD | +5.2 (1.11) / +11.8 (1.42) / +6.3 (1.60) | 2.2 / 1.6 | +3.0 (0.64) / +10.2 (1.22) | 0.37 / 0.98 | fails (IS t) |
| F1, 1 day | same | +2.4 (0.84) / +1.4 (0.27) / **+7.4 (3.04)**, 9/12 PRE years | 1.5 / 1.2 | +0.9 / +0.2 | 0.18 / 0.04 | real in 2004-15, gone since 2016 |
| F1, large surprises only / whole-day surprise | same | IS t <= 0.67 | 1.5-2.4 | IS <= +2.2 | <= 0.17 | fails |
| F2 hawkish surprise -> short the home index, 5 days (Neuhierl & Weber 2018) | US500, DE40, UK100, JP225, AUS200 | +3.8 (0.36) / -24.7 (-1.01) | 9.6 / 8.3 | -5.8 / -33.0 | < 0 | fails |
| F2 best cell (whole-day surprise, 1 day) | same | +6.9 (0.98) / +17.8 (1.90) | 5.3 / 3.4 | +1.6 (0.23) / +14.4 (1.53) | 0.12 / 1.06 | fails (IS t) |
| F3 continuation after macro releases, 5 days (Evans & Lyons 2005) | 15 non-US types + US NFP/CPI | -0.3 (-0.10) / -2.2 (-0.53) | 2.2 / 2.1 | -2.4 / -4.4 | < 0 | fails |
| F3 large reactions only | same | IS -5.4..-1.1 / VAL +9..+10.7 (t <= 1.8) | 1.3-2.0 | IS < 0 | < 0 | sign flips |
| F4 FOMC-cycle even weeks, long (Cieslak, Morse & Vissing-Jorgensen 2019) | US500 | even weeks -4.8 / +20.0 | 7-13 | -13.2 / +9.5 | <= 0.44 | fails |

- **Chance.** 35 cells; every family's best IS |t| is at or below its null median (F1 1.11 vs median 1.64, 95th
  percentile 2.75).
- **Power.** LIVE would need a per-leg net Sharpe of 0.26 at ~75 legs a year; F1 shows 0.03 IS / 0.09 VAL.
- **Delayed overshooting faded.** It held at 1 day in 2004-09 (+5..+15 bp net a year), then went to ~0 after 2015,
  as Kim, Moon & Velasco (2017) report. F1's VAL strength comes from FOMC in the 2022-23 hiking cycle (+60 bp per
  leg, t 2.97).
- **The 5 x 24 h cap makes h5 equal to h3** for 1,574 of 1,580 legs, because decisions fall Tuesday to Thursday.
- **Correlation with C3** (cells net > 0 in both eras, none a candidate): -0.01 to 0.01 daily.

## G. Cross-sectional momentum / reversal at 1-5 days

Sides came from the literature: short-term momentum in currencies (Menkhoff et al. 2012; Zaremba, Long &
Karathanasopoulos 2019), indices and commodities. Nagel's reversal was kept as the declared competitor. Holds were
1 day, 3 days, or Monday -> Friday (a 5-trading-day hold breaks the 5-calendar-day limit). Each bot holds at most 2
positions; fills at 20:00 UTC (FX) or 14:00 UTC (indices, commodities).

| hypothesis (IS-chosen cell) | IS mid bp (t by week) / VAL | cost IS / VAL | net IS / VAL | power | verdict |
|---|---|---|---|---|---|
| G1 8 currencies, top-bottom momentum (k 3, Mon -> Fri) | +2.15 (0.27) / -0.17 | 4.7 / 3.3 | -2.56 / -3.45 | -0.18 | fails; PRE net -20.3 (t -2.57) |
| G2m G1 on high-dispersion days (k 1, h 3) | +7.15 (0.90) / +0.72 | 3.4 / 2.8 | +3.74 (0.47) / -2.10 | 0.31 | fails; PRE -10.4 (t -1.70) |
| G2s lot 2x on high-dispersion days, 0.5x otherwise | +4.52 (0.53) / -1.04 | 3.8 / 4.0 | +0.73 / -4.99 | 0.05 | fails |
| G2n Nagel reversal on high days | +2.82 / -2.58 | 4.0 / 3.8 | -1.14 / -6.41 | < 0 | fails |
| G3i 8 indices, vol-adjusted momentum | +7.6 (0.63) / -56.6 (-2.06) | 16.0 / 13.7 | -8.5 / -70.3 | < 0 | fails |
| G3c 6 commodities | -18.6 / +102.9 (1.94) | 36.6 / 54.8 | -55.2 / +48.1 | < 0 | fails |
| G3c2 XAU, XAG, XTI (k 1, h 1) | +13.9 (2.19) / +4.2 | 8.1 / 7.1 | +5.7 / -2.9 | 0.60 | fails; IS is the April 2020 oil crash |
| G5 post hoc: extreme formation-spread days | +12.7 (0.92) / -22.7 (-1.65) | 3.4 / 3.4 | +9.3 / -26.1 | 0.43 | fails |

- **Chance.** 63 declared cells plus 2 post hoc. Every family's best IS |t| (0.58-2.19) is below its permutation
  95th percentile (2.65-2.84).
- **No signal in either direction.** A rank-weighted, dollar-neutral 8-currency book shows |t| <= 1.51 at mid in
  every era (PRE <= 0.42), so the reversal mirror has nothing either.
- **What LIVE would need.** About 8.5 bp net per daily currency trade against ~60 bp sd; the observed mid is <= ~2 bp.
- **PRE.** PRE shows a weekly currency reversal (G1 k 3 mid -15.9 bp, t -2.0) that IS/VAL lack, almost all in
  2004-11.
- **Swaps.** Stream G used round 7 D's fixed markups instead of `rates.py`'s fitted ones, because computing those
  loads M1 files that include 2025-26 prices.

## H. Full intraday scan of the commission-free index CFDs

H1, the grid:
- **Design.** 15- and 60-minute windows at every 15-minute boundary, on the local exchange clock (DST-aware) and on
  UTC. Day types: each weekday, all weekdays, the first and last 3 trading days of the month.
- **Symbols and costs.** US30, USTEC, UK100, HK50, AUS200 with actual spreads; the bid-only new symbols with round 7's
  spreads. US500, DE40 and JP225 (round-3 contamination) were for information only.
- **Size and chance.** K = 15,913 eligible cells; Bonferroni threshold 4.66. Per-day sign-flip null: max |t_IS|
  median 3.98, 95th percentile 4.51. Observed max 4.94: UK100 06:45-07:00 UTC on the first 3 trading days of the
  month, +3.26 bp against a 4.5 bp spread, VAL -0.09.
- **No cell clears the frontier** (IS net Sharpe >= 3 / sqrt(1.73 x trades a year)), at any t. The best reaches 0.53
  of it (US30).
- **Median cost per cell:** US30 1.07 bp, US2000 2.24, UK100 2.97, USTEC 3.45, HK50 4.0, AUS200 5.1, the European
  indices 3.4-4.7.
- **Persistence.** The top 100 IS cells keep their side in VAL 61 % of the time (chance 50 %). The correlation of
  t_IS with t_VAL over all cells is +0.055 (p ~0.04): faint, far from tradeable. Of 268 cells with |t_IS| >= 2.5,
  none clears the frontier in VAL even at US30's 0.3 bp VAL cost.

H2, mechanism-first windows (16 cells, sides fixed beforehand):

| hypothesis | where | IS mid bp (t) / VAL | cost IS / VAL | net IS / VAL | verdict |
|---|---|---|---|---|---|
| follow the market-on-close imbalance publication (NYSE 15:45 until 2019-01, then 15:50) to 16:00 | US30 | +0.29 (0.6) / -0.25 | 0.91 / 0.29 | -0.62 / -0.54 | fails |
| same | USTEC | +1.53 (2.71) / +1.00 (1.54) | 1.67 / 0.65 | -0.14 / +0.35 | at cost |
| follow the 10:00 ET releases (ISM, Conference Board) 30 / 60 min | US30, USTEC | -3.8..+1.4 / -1.5..-8.9 | 0.9-1.7 | < 0 | fails; non-release days look the same |
| UK100 closing auction (follow 16:15-16:35, fade 16:36-17:30) | UK100 | +0.13 / +0.84; +0.27 / -0.33 | 2.4-3.0 | < 0 | fails |
| HK50 lunch fade; close follow | HK50 | -0.17 / +0.43; -1.35 / -0.01 | 2.8-3.3 | < 0 | fails |
| AUS200: fade the 16:00-16:12 move over 16:13-16:30 | AUS200 | +0.82 (2.17) / +0.71 (2.71) | 2.18 / 1.58 | -1.36 / -0.87 | real, below cost |
| fade the 3rd-Friday special opening quotation (12 a year) | US30, USTEC | -7.3 (-2.0) / +13.5 | 0.9-1.7 | < 0 IS | sign flips |

The family's best |t_IS| is 2.71 against a null 95th percentile of 2.92.

H3, a post-hoc lead, not registrable:
- **How it was found.** The Wednesday 15:45-16:00 ET cell came out in the IS top 11 (US30 -4.5 bp, t -3.6) and held
  in VAL (-3.3, t -2.0). Split afterwards by FOMC days, it became the rule **short US30 15:45-16:00 ET on scheduled
  FOMC decision days.**
- **Numbers.** Net +6.7 bp (t 2.72, n 47) IS / +9.5 (t 1.48, n 24) VAL, per-trade Sharpe 0.40 / 0.30, 7/9 years
  positive. Robust to spread x1.5 and +1 minute. Beats 100 % / 97 % of random slots on the same days. C3
  correlation -0.03 daily.
- **Why it is not a candidate.**
  - At ~8 trades a year, HOLD power is ~1.1, so LIVE is impossible.
  - It came out of a 15,913-cell scan and a later split, with no mechanism written beforehand. Round 10's A7 shows
    how such picks fail.
  - Non-FOMC Wednesdays are also negative (-3.5 bp IS, -2.2 VAL), so FOMC explains only part of it.
- **The only clean test** is to register it and judge it on data after 2026-09-24 or on a demo account. Dukascopy
  index data before 2016 exists here only as H1 bars, too coarse for a 15-minute window.

## What this says

- **Moving to 1-5 day horizons removes the cost problem but finds no signal.** Post-decision drift faded after 2015,
  post-release drift is absent, and cross-sectional momentum / reversal has no predictability at mid in any era.
- **Moving to commission-free index CFDs runs into their spreads.** The non-US indices cost 3-5 bp a round trip
  against 1-3 bp effects. US30 is the only cheap one, and its strongest windows do not repeat in VAL.
- **Eleven rounds agree.** On IC's costs and these symbols, what exists outside gotobi is below one round trip, or
  too rare for the holdout, or (at 1-5 days) not there. C3 remains the only algorithm that has passed.
- **What could change this needs the user's decision** (unchanged from round 10): more IC symbols, data after
  2026-09-24 (which would also give H3 a clean test), or a cost structure without the 0.6 bp FX commission.

## Process and disclosures

- **HOLD stayed closed.** The panel ends 2024-12-31; new-symbol bars and M1 loads were cut at 2025-01-01; PRE is
  2004-2015.
- **Network.**
  - Release calendars: BLS archive file names (US CPI, NFP).
  - Literature: OpenAlex and Semantic Scholar.
  - Stream G fetched FRED short rates 2003-2015 into its scratchpad as PRE swap inputs. This is beyond the brief's
    list of network uses, and it fetched no prices.
- **Order of work.** Stream H's first hypothesis entries carried guessed times later than the clock. They were
  corrected from the scratch files' times; the order of entries was always right.
- **Code.** Scratch scripts and outputs stay in the session scratchpad, listed in each STREAM file. Nothing in
  `research/` code was edited.
