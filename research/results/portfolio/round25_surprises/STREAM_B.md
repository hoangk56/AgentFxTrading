# Round 25, stream B: predictable release surprises (published consensus)

Written 2026-10-17 19:30 UTC. Hypotheses, all 144 cells, were declared in [HYPOTHESES_B.md](HYPOTHESES_B.md) at
19:08 UTC, before any return was computed. Its addendum (19:27 UTC) records the process changes and the post-hoc
diagnostics. HOLD stayed closed:
- the panel ends 2024-12-31 and Dukascopy 2015-12-31 (asserted in code);
- FF rows dated 2025 or later were cut at load;
- the Dukascopy `*_2026` files were never opened.

## Answer

**No LIVE or DEMO candidate.** No PREREG_DRAFT was written.
- **FF's consensus is predictable.** It is anchored to the previous print: the sign of F - Pk calls the sign of the
  surprise 54-57 % of the time. National flash CPIs call the euro-area flash HICP surprise against FF 76-92 % of the
  time.
- **The FX market has already priced that part before the release.** At the release minute, the predicted part
  moves nothing net of IC's spread.
- **Released numbers still move prices strongly.** The realised surprise sign gets 5-40 bp in the release minute
  (B0, t 4-9). But the part an outsider can predict from public data earns little:
  - the pooled cells make at most about 1 bp gross (B1 primary +0.71 bp IS, t 1.39; B2-ALL -0.22);
  - the only small cell positive in IS, B3a (Cleveland Fed CPI nowcast, +6.4 bp, t 2.00), reverses in VAL
    (-15.8 bp).

  The release-minute round trip costs 0.8-1.9 bp.

## Calendar and B0 validation

### FF data quality and fixes
The calendar is shared at
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/shared/cal/ff_events_utc.csv`,
with a `ff_events_utc_README.txt` next to it.

- **Lost times.** 17,543 High-impact rows in 2007-2024; 32.7 % had lost their time (00:00 Tehran). After the fixes,
  only 349 all-day rows stay untimed.
- **Time recovery.** Untimed rows take their time in this order:
  1. the type's nearest own rows;
  2. a same-slot partner type (e.g. CPI m/m takes Core CPI m/m's time, Retail Sales takes Core Retail Sales');
  3. the official time (USD Trade Balance, 08:30 New York).
- **Offset labels.** UTC was recomputed from the wall time in the system `Asia/Tehran` zone. **The CSV's +04:30
  labels are wrong in the 2023-24 summers** (Iran dropped DST). Read as labelled, ADP shows 07:15 ET, ISM 09:00 ET
  and the Canadian LFS 07:30 ET in those months.
- **Snaps.**
  - FF lists Richmond and Philly at hh:59 / hh:29: snapped +1 minute.
  - 507 own rows sat exactly 60 minutes off their type's clock (e.g. USD CPI y/y at 07:30 EST in 2009): snapped
    back.
- **Verification (direction-free).** The tick-count spike at T, or the |return| spike for Dukascopy, whose tick
  count is always 1, verified 217 of 287 type-era cells in IS/VAL and 376 of 500 overall. The ones that fail are
  mostly releases the market ignores: EZ / German / French final PMIs, Chicago PMI, EIA crude on EURUSD.
- **Early releases visible in PRE.**
  - Markit PMIs (EUR, GBP) spike 2 minutes before the official time in 2007-2013: the subscriber early release,
    gone after 2013. 21 type-years were moved 2 minutes earlier.
  - The MNI Chicago PMI spikes 3 minutes early (09:42 ET) in 5 PRE years: moved.
- **German Prelim CPI m/m** is all-day in FF. 14:00 Berlin shows the spike in only 3 of 6 IS years, so it is used as
  a B2 signal only, never traded.
- **Units.** Values parse cleanly as number + %, K, M, B, T.
- **FF "Previous" is a look-ahead.** It differs from the previous release's first print in 44 % of rows, because FF
  shows the value revised at the release (e.g. NFP 2007-02-02 shows 206K for December, first printed 167K). B1
  therefore anchors on the previous first print (Pk), which is known before the release.

### B0: realised surprise sign vs the release-minute move
The table gives the 1-minute oriented move, bar T-1 close to bar T close, on the home pair(s), in bp (day-clustered
t, n).

| type | PRE 2007-15 | IS 2016-21 | VAL 2022-24 | in B1 |
|---|---|---|---|---|
| USD Non-Farm Employment Change | 20.85 (8.35) n214 | 12.55 (5.85) n142 | 20.57 (4.04) n72 | yes |
| USD CPI m/m | 2.77 (3.26) n144 | 8.96 (5.09) n92 | 39.83 (6.35) n46 | yes |
| USD Core CPI m/m | 4.49 (3.76) n120 | 10.25 (6.96) n96 | 35.48 (4.97) n46 | yes |
| USD Retail Sales m/m | 8.23 (8.50) n192 | 6.64 (5.19) n134 | 9.30 (3.88) n72 | yes |
| USD ISM Manufacturing PMI | 6.12 (8.21) n212 | 5.67 (6.67) n142 | 7.33 (4.87) n72 | yes |
| USD ISM Services PMI | 4.84 (9.10) n212 | 5.03 (6.20) n142 | 12.63 (5.84) n72 | yes |
| USD ADP Non-Farm Employment Change | 6.23 (7.95) n216 | 4.31 (7.32) n142 | 7.92 (8.35) n66 | yes |
| USD PPI m/m | 3.36 (4.59) n194 | 3.61 (3.77) n106 | 12.62 (5.80) n62 | yes |
| USD Unemployment Claims | 3.09 (9.11) n862 | 0.86 (2.52) n432 | 5.62 (5.18) n300 | no |
| USD Advance GDP q/q | 8.94 (5.45) n70 | 4.74 (2.54) n46 | 4.43 (1.19) n24 | no |
| USD Philly Fed Manufacturing Index | 3.56 (6.06) n216 | 1.35 (2.80) n142 | 1.25 (0.61) n72 | no |
| USD Core PCE Price Index m/m | 0.12 (0.08) n102 | 1.57 (1.85) n60 | 8.03 (3.21) n26 | no |
| USD Unemployment Rate (NFP slot) | -0.10 (-0.03) n160 | -2.09 (-0.65) n104 | 18.42 (3.30) n62 | no |
| EUR German Flash Manufacturing PMI | 4.27 (6.40) n93 | 4.76 (5.46) n72 | 5.37 (2.68) n34 | yes |
| EUR German ifo Business Climate | 6.56 (8.84) n107 | 2.46 (5.90) n70 | 2.89 (5.09) n33 | yes |
| EUR CPI Flash Estimate y/y | 1.76 (2.36) n70 | 0.91 (1.50) n46 | 0.61 (0.88) n28 | no |
| GBP CPI y/y | - | 8.63 (6.20) n55 | 13.21 (6.07) n31 | yes |
| GBP Retail Sales m/m | - | 6.68 (5.49) n66 | 5.94 (7.26) n36 | yes |
| AUD Employment Change | 26.31 (9.31) n107 | 9.37 (3.89) n71 | 16.48 (7.39) n36 | yes |
| AUD CPI q/q | 17.90 (3.03) n32 | 22.49 (4.19) n21 | 21.84 (3.68) n11 | yes |
| NZD CPI q/q | 28.62 (8.61) n31 | 37.79 (4.78) n21 | 15.00 (3.20) n10 | yes |
| CAD Employment Change | - | 18.02 (7.20) n72 | 9.19 (2.87) n36 | yes |
| CAD CPI m/m | 1.59 (0.83) n11 | 15.26 (5.28) n51 | 10.90 (5.73) n28 | yes |
| CNY Caixin Manufacturing PMI (AUDUSD) | 7.29 (5.12) n29 | 4.26 (7.03) n65 | 3.66 (6.19) n32 | yes |
| JPY Tokyo Core CPI y/y | 0.82 (1.83) n66 | 0.30 (1.72) n55 | 3.31 (4.80) n27 | no |
| JPY National Core CPI y/y | 0.82 (1.67) n53 | 0.02 (0.07) n32 | 1.38 (1.70) n18 | no |
| CHF CPI m/m | 4.69 (5.52) n87 | - (Low impact in IS) | 15.27 (6.23) n22 | no |

What the table says:
- B0 is strongly positive wherever the market cares. That validates times, signs and units. Hit rates are 0.7-0.97
  for the large releases.
- 56 types meet the declared B1 inclusion (IS t >= 3).
- No JPY or CHF type qualifies, so B1-JPY and B1-CHF have no trades. CHF CPI is FF "Low impact" in 2016-21, so it
  falls outside the universe.
- Full table: `B/out/b0_table.txt`.

## Results

Notes for the table:
- "mid" is the gross return in bp (day-clustered t); PRE uses Dukascopy bid closes.
- The cost is IC's actual half spread at the entry bar + half at the exit bar + 0.6 bp.
- Power = per-trade net Sharpe x sqrt(1.73 x trades per year).
- The random control is the share of 1,000 random-sign draws that the observed net beats.
- All rows enter at T-1 and exit at h 15 unless stated.

| hypothesis | where (IS / VAL trades) | PRE / IS / VAL mid bp (t) | cost IS / VAL | net IS / VAL (t) | VAL/IS | power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| B1 anchoring, all currencies, High slots (primary) | 8 pairs (1,792 / 877) | -0.06 (-0.12) / +0.71 (1.39) / +0.40 (0.35) | 1.72 / 1.32 | -1.01 (-1.98) / -0.92 (-0.79) | n/a (both < 0) | -1.20 / -0.76 | 0.93 / 0.62 | fail |
| same, entry T-2 | same | +0.15 (0.32) / +0.68 (1.33) / +0.32 (0.28) | 0.88 / 0.84 | -0.20 (-0.39) / -0.53 (-0.46) | n/a | -0.23 / -0.44 | 0.92 / 0.61 | fail |
| same, High+Medium slots | (2,613 / 1,242) | -0.11 (-0.27) / +0.38 (1.03) / +0.41 (0.48) | 1.47 / 1.17 | -1.09 (-2.97) / -0.76 (-0.88) | n/a | -1.80 / -0.85 | 0.85 / 0.70 | fail |
| same, High, \|F-Pk\| >= 1x typical surprise | (1,004 / 382) | +1.02 (1.29) / +0.27 (0.38) / +1.91 (1.04) | 1.91 / 1.61 | -1.64 (-2.27) / +0.30 (0.16) | n/a | -1.34 / 0.15 | 0.67 / 0.80 | fail |
| B1 USD pool, h5 (best B1 IS gross t) | EURUSD + USDJPY (1,484 / 804) | +0.34 (0.81) / +0.82 (1.89) / +1.11 (1.01) | 1.17 / 1.10 | -0.35 (-0.80) / 0.00 (0.00) | n/a | -0.61 / 0.00 | 0.97 / 0.88 | fail |
| B1 EUR pool, h5 (largest \|t\|, wrong sign) | EURUSD (250 / 127) | -0.93 (-1.85) / -1.02 (-2.23) / +0.16 (0.15) | 0.76 / 0.72 | -1.77 (-3.88) / -0.56 (-0.52) | n/a | -2.05 / -0.41 | 0.01 / 0.60 | fail |
| B1 NZD pool, h30 (best B1 IS net t) | NZDUSD (38 / 19) | +11.57 (1.76) / +9.54 (1.24) / -12.97 (-1.77) | 5.05 / 7.03 | +4.49 (0.60) / -20.01 (-2.88) | -4.46 | 0.32 / -2.19 | 0.88 / 0.03 | fail |
| B1 gold on USD releases (side -USD) | XAUUSD (739 / 401) | +0.08 (0.09) / +1.33 (1.42) / +1.18 (0.72) | 1.95 / 1.36 | -0.62 (-0.66) / -0.18 (-0.11) | n/a | -0.36 / -0.09 | 0.92 / 0.78 | fail |
| B1 US500 on USD releases (side +USD) | US500 (739 / 401) | - / +1.12 (1.59) / +1.22 (0.57) | 1.91 / 0.77 | -0.79 (-1.12) / +0.45 (0.21) | n/a | -0.62 / 0.16 | 0.95 / 0.65 | fail |
| B1 GBP / AUD / CAD / CNY pools | home pair | IS mid -0.85..+0.05 | 1.2-2.3 | IS net -1.4..-3.1 | - | < 0 | 0.31-0.56 | fail |
| B2a ADP -> NFP | USD set (142 / 66) | -6.12 (-1.51) / +1.10 (0.40) / -5.67 (-0.72) | 2.35 / 1.89 | -1.25 (-0.45) / -7.57 (-0.96) | n/a | -0.33 / -0.99 | 0.72 / 0.28 | fail |
| B2b Fed regional surveys + Chicago + flash PMI -> ISM | USD set (142 / 68) | -0.59 (-0.35) / +1.08 (0.70) / -7.27 (-2.54) | 0.99 / 1.02 | +0.09 (0.06) / -8.30 (-2.92) | -94 | 0.04 / -2.81 | 0.79 / 0.01 | fail |
| B2c Empire -> Philly | USD set (124 / 62) | -0.43 (-0.39) / -0.95 (-0.66) / -3.53 (-1.24) | 0.90 / 0.99 | -1.85 (-1.29) / -4.52 (-1.59) | n/a | -0.84 / -1.59 | 0.27 / 0.13 | fail |
| B2d flash -> final PMIs (EUR, GBP, USD) | home pairs (722 / 424) | +0.24 (0.69) / +0.16 (0.60) / +0.22 (0.56) | 0.80 / 0.80 | -0.63 (-2.32) / -0.59 (-1.52) | n/a | -1.46 / -1.35 | 0.76 / 0.77 | fail |
| B2e national flash CPIs -> EA flash HICP | EURUSD (61 / 33) | -1.84 (-1.62) / +1.07 (1.11) / -1.73 (-1.68) | 0.73 / 0.66 | +0.34 (0.35) / -2.38 (-2.33) | -7.1 | 0.19 / -1.77 | 0.84 / 0.05 | fail |
| B2f Tokyo CPI -> national CPI | USDJPY (56 / 26) | -0.80 (-0.48) / +0.21 (0.47) / -3.44 (-3.07) | 0.93 / 0.87 | -0.72 (-1.64) / -4.31 (-3.83) | n/a | -0.88 / -2.91 | 0.66 / 0.00 | fail |
| B2g survey-week claims -> NFP | USD set (136 / 68) | -3.70 (-0.90) / -0.71 (-0.25) / +3.29 (0.42) | 2.29 / 1.71 | -2.99 (-1.04) / +1.57 (0.20) | n/a | -0.76 / 0.21 | 0.42 / 0.40 | fail |
| B2g2 all claims since last NFP -> NFP | USD set (104 / 56) | +1.81 (0.38) / -5.73 (-1.87) / -13.27 (-1.92) | 2.34 / 1.87 | -8.08 (-2.65) / -15.14 (-2.17) | n/a | -1.92 / -2.24 | 0.02 / 0.01 | fail (wrong sign) |
| B2h CN official PMI -> Caixin PMI | AUDUSD (64 / 29) | -2.20 (-1.72) / -1.73 (-1.40) / +0.78 (0.44) | 1.22 / 0.72 | -2.94 (-2.40) / +0.07 (0.04) | n/a | -1.29 / 0.03 | 0.11 / 0.68 | fail |
| B2i German flash PMIs -> ifo | EURUSD (33 / 19) | -2.22 (-0.81) / -0.61 (-0.65) / -1.66 (-0.95) | 0.69 / 0.66 | -1.30 (-1.38) / -2.32 (-1.33) | n/a | -0.74 / -1.01 | 0.15 / 0.21 | fail |
| B2j core CPI -> core PCE | USD set (94 / 46) | -0.24 (-0.19) / +0.10 (0.12) / -0.45 (-0.17) | 0.87 / 1.23 | -0.77 (-0.93) / -1.68 (-0.62) | n/a | -0.60 / -0.62 | 0.54 / 0.43 | fail |
| B2-ALL pooled | (1,424 / 769) | -0.81 (-1.31) / -0.22 (-0.60) / -1.51 (-2.07) | 0.98 / 0.93 | -1.21 (-3.25) / -2.44 (-3.33) | n/a | -2.22 / -3.22 | 0.28 / 0.02 | fail |
| B3a Cleveland Fed CPI + core nowcast vs FF | USD set (78 / 54) | -5.18 (-0.90) / +6.41 (2.00) / -15.80 (-1.29) | 1.57 / 1.88 | +4.84 (1.50) / -17.67 (-1.45) | -3.65 | 1.09 / -1.50 | 0.91 / 0.13 | fail |
| B3b Cleveland Fed core PCE nowcast vs FF | USD set (36 / 38) | -2.04 (-0.46) / -0.70 (-0.62) / +1.87 (0.58) | 0.89 / 1.00 | -1.58 (-1.40) / +0.87 (0.27) | n/a | -0.86 / 0.28 | 0.29 / 0.74 | fail |
| B3c Atlanta Fed GDPNow vs FF (advance GDP) | USD set (36 / 22) | +3.19 (0.65) / -2.67 (-0.95) / +4.50 (0.70) | 1.57 / 1.19 | -4.24 (-1.54) / +3.31 (0.51) | n/a | -1.07 / 0.53 | 0.20 / 0.78 | fail |
| B3d NY Fed Staff Nowcast | - | - | - | - | - | - | - | infeasible (vintage file not located) |

- **Full grid.** All 144 cells (every h and entry, x1.5 spread, +1 minute, years) are in `B/out/cells_table.txt`
  and `B/out/cells_summary.json`. 138 cells have trades. The bar check gives fail for 138 and no data for 6
  (B1-JPY and B1-CHF).
- **By year, B1 primary net.** IS: +0.1, -1.1, -1.6, -0.8, -1.7, -1.6. VAL: -2.6, -0.7, +0.1. PRE is negative in
  9 of 9 years.
- **B3a's IS** comes from 2017 (+26.5 bp). Its VAL years are -21.5, -13.0 and -18.5.

### Best cell per family, cells tried, chance

| family | cells (with trades) | best IS net t | best IS gross t | max \|IS gross t\| vs permutation null (p50 / p95) | max-\|t\| of K normals, 95 % |
|---|---|---|---|---|---|
| B1 | 57 (51) | B1-NZD h30 +0.60 | B1-USD h5 +1.89 | 2.23 (EUR, wrong sign) vs 2.05 / 3.03 | 3.32 |
| B2 | 69 (69) | B2b T-2 h5 +0.69 | B2b T-1 h5 +1.30 | 2.13 (B2i, wrong sign) vs 2.23 / 3.01 | 3.37 |
| B3 | 18 (18) | B3a T-2 h15 +1.69 | B3a T-1 h15 +2.00 | 2.00 vs 1.69 / 2.54 | 2.98 |
| all | 144 (138) | - | - | 2.23 vs 2.46 / 3.21 (74 % of null draws exceed it) | 3.57 |

The null shares one sign flip per UTC day across all cells and uses 2,000 draws. The whole family sits at the noise
median.

## Why: the predictable part exists but is priced

These diagnostics were added after the cells and are information only.
- **FF's consensus is anchored.**
  - The sign of F - Pk matches the sign of A - F 56.9 % (PRE), 53.9 % (IS) and 54.3 % (VAL) of the time.
  - The Campbell-Sharpe slope of (A - F) on (F - Pk), in units of the type's typical surprise, is 0.11 (t 6.5),
    0.08 (t 2.4) and 0.08 (t 3.5).
  - The bias replicates on FF data, weaker after 2016.
- **FX sees through it, as bond yields did in Campbell & Sharpe 2009.** We regress the 5-minute home move on the
  realised surprise s = (A - F)/typ and the anchoring predictor x = (F - Pk)/typ:

  | era | b_s (bp per typical surprise) | b_x | b_x if the market prices the bias (-lambda b_s) |
  |---|---|---|---|
  | PRE | 4.05 (t 17.6) | -0.58 (t -3.1) | -0.32 |
  | IS | 3.63 (t 16.8) | -0.41 (t -2.7) | -0.29 |
  | VAL | 6.72 (t 8.6) | +0.02 (se 0.44) | -0.54 |

  A naive market (one that takes F as its expectation) would give b_x = 0. In PRE and IS the market reacts only to
  the part of the surprise the anchoring does not predict. VAL has no power to tell the two apart.
- **B2's stale consensus is real in FF but not in prices.** The early signal calls the target's FF surprise as
  follows:

  | pair | PRE | IS | VAL |
  |---|---|---|---|
  | B2e (national flash CPIs -> EA flash HICP) | 92.5 % | 76 % | 77 % |
  | B2i (German flash PMIs -> ifo) | 60 % | 63 % | 74 % |
  | B2b (regional surveys -> ISM) | 64 % | 59 % | 41 % |
  | others | about 50 % | about 50 % | about 50 % |

  Yet the EA flash moves EURUSD +1.1 bp (t 1.1) in IS and -1.7 bp (t -1.7) in VAL in the predicted direction. Its
  own B0 slope is the weakest of the EUR releases (IS t 1.50). The market prices the national releases when they
  come out, which is Hess & Niessen's (2010) early-news effect. FF's consensus is simply not the market's
  expectation.
- **IC's spread at the release minute.** For High slots the round trip costs 1.7 bp when entering at T-1 but 0.9 bp
  at T-2, because IC widens in the last minute. Any future release rule should enter at least 2 minutes before.
- **C3 daily correlation (IS+VAL, information).** B1 primary +0.012, B1-USD -0.008, B2-ALL +0.025, B3a +0.003.

## Needs the user
- **HOLD consensus data.** None was needed this round. A future consensus-based rule would need consensus values for
  2025-01..2026-09; the FF file ends 2025-04-07 and 2025 rows are HOLD. Possible sources:
  - ForexFactory's own weekly calendar pages (same definitions; a scrape; check their terms);
  - the Investing.com or FXStreet calendars (actual / forecast / previous);
  - the Trading Economics API (paid).
- **Paid survey data.** Bloomberg ECO or Reuters polls with individual forecasts, timestamps and dispersion would let
  a test separate FF's stale consensus from the market's expectation and time consensus updates.
- **Market-based expectations.** CPI fixings or inflation swaps, fed funds futures. Given the pricing test above,
  the prior value is low.

## Untested ideas
- **NY Fed Staff Nowcast vintages.** The data file sits behind a JS app, not found in 3 probes; a browser could find
  it. GDP has 4 releases a year, so at most DEMO.
- **German Länder CPIs -> German CPI.** The values are public (Destatis GENESIS). The test also needs Destatis'
  historical release times, because FF lists the German flash as all-day. The prior is low: the market prices the
  Länder in the morning.
- **Revision-sign rules.** FF "Previous" minus the first print gives each release's revision of the prior month,
  present in 44 % of rows. No revision-based predictor was declared.
- **FF forecast updates during the week.** The dataset keeps only the final forecast, so the time at which the
  consensus goes stale cannot be measured.
- **The B2g2 contrarian pattern** (USD falls at NFP after a month of USD-good claims): IS net t -2.65, VAL -2.17. It
  is post hoc, opposite to the declared side and positive in PRE (+1.81, t 0.38). Not registrable.

## Scripts and outputs
All are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/B/`.

Scripts in `code/`:

| script | what it does |
|---|---|
| ff_explore.py, ff_values.py, ff_offsetcheck.py, ff_timecheck.py | calendar exploration, csv module, no prices |
| cal_build.py, cal_final.py | build the timed calendar and write the shared copy |
| universe.py | universe rule |
| verify_times.py | direction-free time check |
| prices.py, lib_b.py | price access (HOLD asserted out), costs, statistics |
| b0.py | B0 validation |
| cells.py | all 144 cells |
| chance.py | permutation null and bar check |
| diag.py, diag2.py | post-hoc diagnostics |
| c3corr.py | C3 correlation |
| clev_parse.py, xlsx_sheet.py | nowcast parsers |
| oa_show.py | literature reader |

Outputs in `out/`:
- b0_table.txt, b0_included.json
- verify_times_v3.txt, time_shifts_v3.csv
- cells_table.txt, cells_summary.json, cells_trades.npz, specs.json
- chance.txt, diag.txt, diag2.txt, c3corr.txt
- clev_month.csv, gdpnow_trackrecord.csv

Network fetches are in `net/fetch_log.txt`, all at 2026-10-17 18:59-19:05 UTC:
- OpenAlex literature queries;
- the Cleveland Fed nowcast page and `nowcast_month.json`;
- the Atlanta Fed GDPNow page and `GDPTrackingModelDataAndForecasts.xlsx`;
- the NY Fed nowcast page and 3 probes.

No price data was fetched.

**Disclosure.** While inspecting the GDPNow TrackRecord sheet, its first rows were printed once. They include 2025-26
quarters: GDPNow and BEA advance estimates, macro numbers, no prices. Those rows were cut at load in the cells.
