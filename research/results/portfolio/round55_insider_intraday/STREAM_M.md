# Round 55 stream M: insider-purchase day-1 drift, intraday entry after the opening auction

Written 2026-10-30 12:00 UTC. Hypotheses: [HYPOTHESES_M.md](HYPOTHESES_M.md), declared at 10:48 UTC, before any M1
file was requested. The design came after round 54's look at the D+1 open-to-close return in IS and VAL; see the
honesty note in that file. Bars: LIVE / DEMO from research/PROMPT.md. HOLD (2025-01..2026-09) stayed closed: no 2025 /
2026 file was requested (latest D+2 date 2024-12-30, asserted in jobs.py and parse.py), and every series is cut at
ts < 2025-01-01 at parse.

## Answer
**No LIVE, no DEMO, no PREREG_DRAFT.** 0 of 48 cells has net IS t >= 2. The best net IS t is +0.36 (CEOCFO 09:35 E2 H),
which sits at p 0.34 against the random-firm best-of-48 null (median 0.12, p95 1.07). The primary cell, **ALL 09:45 E1 H**,
loses -14.0 bp a trade in IS (t -1.97) and -21.4 in VAL (t -2.54), and is negative in 8 of 8 years.

Why:
- **Most of the all-buys drift is still there after 09:45 in IS, but much less in VAL.** At mid, unhedged, 09:45 -> 15:55,
  ALL keeps +19.8 bp in IS (95 % of the day's move) but only +6.4 in VAL (39 %).
- **The rest does not cover the cost of a round trip.** The Dukascopy spread at 09:45 is ~11 bp (vs 70 at the first
  quote) and IC's commission is ~12 bp, so a round trip costs ~24 bp.
- **CEO / CFO buys do not survive either.** Round 54's CEO / CFO IS day-1 figure (+46.5 bp) rests largely on one trade:
  RRC at $1.6 on 2020-03-12, +2,853 bp. On the trades with every intraday bar present it is +15 bp, all of it before
  09:35. CEO / CFO VAL keeps +20 bp after 09:45, below cost.

The count already ruled LIVE out before any return (zero-cost HOLD power 0.2-0.35 under the 1/4 rule).

## Data and sources
- **Events:** round 54 I's `events.csv`, read only: CMP classification, and filing date D public by 22:00 ET.
  D+1 is the first trading day after D in D's daily grid. There are 1,336 valid ALL firm-days over 859 distinct D+1
  dates: IS 2017-21 896, VAL 2022-24 440. ROUT is a subset of ALL.
- **Dukascopy M1 bid / ask:** `datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{MM0}/{DD}/{BID|ASK}_candles_min_1.bi5`,
  using the approved browser-UA exception.
  - robots.txt answered 404 (nothing disallowed), checked at 10:50 UTC.
  - Pull: 15,372 files (7,686 firm-days), 10:54:35-11:51 UTC at 12 threads, ~4.4 files/s. 116+ transient 503s and
    17 files failed after 12 tries; all 17 came back on one retry at 11:53. Every firm-day is present.
  - What was pulled: event firms on D+1 and D+2, plus a random pool of 3 non-ETF names per D+1 date (seed 55, never
    an event firm that day) on D+1 and D+2.
  - Log: `.../r55/M/cache/requests.log`.
- **Format check, on 2 known non-event days, before the bulk pull:**
  - Price scale is 1e3. Bar time is the start of the minute. The regular session is 09:30-15:59 ET (390 bars; 14:30
    UTC in winter).
  - The first bar's bid open and last bar's bid close equal D's daily raw candle exactly: AAPL 2018-01-02 170.138 /
    172.198; MSFT 2024-12-31 425.547 / 421.116.
  - M1 prices are raw (not split-adjusted). Only 235 traded minutes fall outside 09:30-16:00 ET over all 7,686 days.
- **Hedge:** IC US500 M1 from the local `research/data/m1/US500.npz` (bid open + mean spread), at the same minutes,
  cut at load. SPY was not pulled (pull budget).
- **Costs:** Dukascopy bid / ask of the traded bar (long buys at the ask open, sells at the bid open); IC USD 0.02 a
  share a side on the raw price; E2 financing (EFFR + 3 %) / 360 a night; hedge -0.5 bp a night.

## Results (net bp per trade, long the firm; H = short IC US500 at the same minutes; day-clustered t)
E1 = exit 15:55 ET on D+1 (primary); E2 = exit 15:55 ET on D+2 (declared variant). Entries are at the ask of the first
traded bar at or after the offset. The random column is the share of 1,000 random-pool seeds the cell beats, IS / VAL.

| cell | n IS / VAL | mid IS (t) | cost IS | net IS (t) | net VAL (t) | x1.5 IS / VAL | +1 min IS / VAL | ex 2020-03/04 IS | Sharpe IS | random IS / VAL | yrs > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **ALL 09:45 E1 H (primary)** | 863 / 431 | +11.8 (1.64) | 23.9 | **-14.0 (-1.97)** | **-21.4 (-2.54)** | -21.0 / -28.2 | -13.4 / -15.9 | -13.0 | -0.063 | 1.00 / 0.54 | 0/8 |
| ALL 09:35 E1 U | 874 / 427 | +19.1 (1.91) | 26.2 | -7.1 (-0.73) | -18.3 (-1.68) | -14.2 / -26.9 | -6.4 / -11.8 | -8.5 | -0.028 | 1.00 / 0.64 | 1/8 |
| ALL 09:45 E1 U | 870 / 433 | +19.6 (1.67) | 23.9 | -4.3 (-0.38) | -17.2 (-1.71) | -10.4 / -23.8 | -5.3 / -11.9 | -13.9 | -0.017 | 1.00 / 0.55 | 2/8 |
| ALL 10:00 E1 U | 878 / 432 | +19.5 (1.46) | 23.7 | -4.1 (-0.32) | -14.7 (-1.62) | -10.0 / -20.8 | -5.3 / -10.8 | -13.2 | -0.016 | 1.00 / 0.73 | 2/8 |
| ALL 10:00 E1 H | 871 / 430 | +14.6 (1.98) | 23.7 | -11.0 (-1.53) | -17.5 (-2.38) | -17.8 / -23.8 | -9.3 / -13.1 | -12.1 | -0.051 | 1.00 / 0.71 | 1/8 |
| OPP 10:00 E1 H (best E1 IS t) | 166 / 68 | +28.2 (2.51) | 27.1 | -0.8 (-0.07) | -18.5 (-1.38) | -8.1 / -25.8 | -0.2 / -19.1 | -12.2 | -0.005 | 1.00 / 0.08 | 3/8 |
| OPP 09:45 E1 H | 163 / 67 | +23.7 (2.17) | 27.0 | -5.2 (-0.47) | -18.2 (-1.11) | -12.5 / -25.6 | -5.5 / -13.0 | -9.8 | -0.035 | 1.00 / 0.11 | 3/8 |
| CEOCFO 09:35 E1 H | 126 / 78 | +25.9 (1.27) | 31.3 | -7.3 (-0.39) | -11.7 (-0.59) | -16.5 / -21.8 | -28.9 / -8.8 | -5.8 | -0.035 | 0.98 / 0.93 | 2/8 |
| CEOCFO 09:45 E1 H | 127 / 78 | -12.8 (-0.65) | 26.9 | -41.5 (-2.07) | -22.4 (-1.21) | -49.3 / -30.0 | -35.3 / -20.3 | -20.3 | -0.182 | 0.05 / 0.65 | 1/8 |
| CLUSTER 10:00 E1 U | 102 / 58 | +21.3 (0.59) | 25.8 | -4.5 (-0.13) | +5.8 (0.23) | -10.9 / -0.4 | +9.1 / +3.8 | -28.2 | -0.014 | 0.59 / 0.99 | 5/8 |
| CLUSTER 09:45 E1 H | 101 / 57 | -2.8 (-0.12) | 26.9 | -31.7 (-1.32) | -9.7 (-0.44) | -39.6 / -16.3 | -26.9 / -2.6 | -25.2 | -0.125 | 0.51 / 0.90 | 2/8 |
| **CEOCFO 09:35 E2 H (best of 48)** | 119 / 72 | +57.0 (0.96) | 33.8 | +20.4 (0.36) | +10.2 (0.34) | +10.8 / +1.3 | -23.4 / +10.1 | -15.5 | +0.033 | 1.00 / 1.00 | 5/8 |
| ALL 09:45 E2 H | 802 / 407 | -4.8 (-0.43) | 24.8 | -32.2 (-2.83) | -13.4 (-0.98) | -38.9 / -19.8 | -31.3 / -12.2 | -16.9 | -0.117 | 0.30 / 0.99 | 2/8 |
| CLUSTER 09:45 E2 H | 98 / 55 | -30.4 (-1.12) | 28.8 | -61.9 (-2.24) | -72.1 (-2.12) | -69.8 / -78.5 | -61.6 / -65.7 | -45.6 | -0.172 | 0.30 / 0.49 | 0/8 |
| ROUT E1 / E2 (placebo, 12 cells) | 37-39 / 39-42 | -86 to +19 | 18-22 | -107 to -1 | +17 to +103 | - | - | - | - | 0.23-0.86 / 1.00 | - |

All 60 rows, with by-year values, are in `out/grade.log`.
- **By year, primary cell:** 2017 -6, 2018 -21, 2019 -18, 2020 -7, 2021 -10, 2022 -26, 2023 -31, 2024 -1.
- **By year, best of 48:** 2017 -35, 2018 +10, 2019 -43, 2020 +122, 2021 +39, 2022 +63, 2023 -40, 2024 +27. Its per-trade
  sd is 612 bp, driven by a few 2020 penny-price trades, and the +1 minute variant flips its IS to -23.4.
- **Cost split, ALL E1** (spread / commission, bp): 09:35 14.2 / 12.0 IS and 17.3 / 11.7 VAL; 09:45 12.1 / 11.8 and
  13.2 / 11.5; 10:00 11.8 / 11.8 and 12.3 / 11.0. The US500 hedge adds ~1 bp. Moving the entry from 09:35 to 10:00
  saves only ~2-5 bp of spread; commission is a fixed ~12 bp.
- **Routine placebo:** negative in IS (-1 to -107) and positive in VAL (+17 to +103, n ~40). It is noise at this size,
  with VAL sd 240-310 bp, and the VAL sign is the opposite of CMP's prediction.
- 26-35 events per offset have no tradeable entry or exit bar: half days, and the 2020-03 circuit-breaker halts.

## How much of round 54's day-1 drift is left (mid bp, unhedged, D+1, trades with every bar present)
| family | era | n | daily open -> close (r54 def.) | 09:30 -> 15:55 | 09:30 -> 09:35 | 09:35 -> 15:55 | 09:45 -> 15:55 | 10:00 -> 15:55 | share left at 09:35 / 09:45 / 10:00 |
|---|---|---|---|---|---|---|---|---|---|
| ALL | IS | 863 | +20.9 (2.05) | +20.9 | +2.8 | +18.4 (1.82) | +19.8 (1.68) | +23.8 (1.81) | 0.88 / 0.95 / 1.14 |
| ALL | VAL | 422 | +16.4 (1.40) | +15.4 | +5.7 | +9.6 (0.89) | +6.4 (0.64) | +7.0 (0.75) | 0.59 / 0.39 / 0.42 |
| OPP | IS | 162 | +23.3 | +22.5 | -1.9 | +24.4 | +24.7 | +28.3 | 1.05 / 1.06 / 1.22 |
| OPP | VAL | 67 | +21.0 | +17.8 | +12.4 | +5.7 | +3.6 | -1.8 | 0.27 / 0.17 / -0.09 |
| CEOCFO | IS | 126 | +15.4 (0.66) | +16.2 | +19.0 (2.01) | -2.4 | +0.4 | +9.2 | -0.15 / 0.03 / 0.60 |
| CEOCFO | VAL | 77 | +56.2 (2.04) | +54.5 | +22.6 (1.91) | +31.9 | +20.0 | +14.1 | 0.57 / 0.36 / 0.25 |
| CLUSTER | IS | 98 | +11.6 | +8.1 | +5.6 | +2.7 | +15.7 | +29.9 | 0.23 / 1.34 / 2.57 |
| CLUSTER | VAL | 56 | +39.5 | +39.6 | +9.7 | +30.1 | +22.9 | +28.8 | 0.76 / 0.58 / 0.73 |
| random pool | IS / VAL | 2,577 per era set | - | -15.8 / +1.0 | - | -14.9 / +3.0 | +0.0 / +1.2 | -7.1 / +0.4 | - |

- The CEO / CFO IS day-1 move is +15 bp on these 126 trades, not round 54's +46.5. One trade explains the gap: RRC on
  2020-03-12 (+2,853 bp, at $1.6; the circuit-breaker halt left no 09:45 / 10:00 bar, so it drops out here).
- Where any CEO / CFO drift exists, it is front-loaded in the first 5 minutes (+19 IS / +23 VAL, at the 70 bp
  first-quote spread).
- The random pool's IS intraday mean (-15.8) is pulled down by a few 2020 crash days, each repeated across that date's
  events. The pool is small (3 per date), so "beats random 1.00" in IS partly reflects this. The verdict does not
  depend on it.

## Spread profile 09:30-10:30 (median bid / ask spread in bp at the bar open, bars with volume)
| group | year (n firm-days) | 09:30 | 09:31 | 09:32 | 09:33 | 09:35 | 09:40 | 09:45 | 09:50 | 10:00 | 10:15 | 10:30 | 15:55 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| event | 2017 (58) | 23.3 | 7.7 | 7.9 | 7.0 | 5.4 | 5.9 | 4.6 | 4.5 | 4.7 | 4.1 | 3.9 | 3.3 |
| event | 2018 (200) | 48.7 | 20.2 | 16.9 | 16.4 | 13.3 | 11.1 | 10.8 | 9.4 | 9.4 | 7.9 | 8.3 | 5.1 |
| event | 2019 (268) | 65.9 | 18.8 | 17.9 | 17.3 | 14.8 | 12.1 | 12.2 | 11.0 | 11.1 | 8.9 | 8.9 | 7.3 |
| event | 2020 (234) | 91.0 | 26.5 | 24.7 | 19.8 | 17.2 | 13.4 | 13.1 | 10.5 | 13.1 | 10.1 | 9.7 | 6.2 |
| event | 2021 (135) | 65.8 | 20.8 | 18.3 | 18.0 | 14.3 | 9.9 | 9.1 | 7.8 | 8.5 | 6.7 | 6.7 | 4.6 |
| event | 2022 (157) | 73.7 | 24.5 | 21.9 | 23.0 | 21.3 | 15.6 | 14.7 | 12.2 | 12.4 | 9.9 | 9.7 | 5.8 |
| event | 2023 (169) | 89.5 | 24.2 | 21.9 | 16.6 | 14.2 | 11.4 | 9.3 | 8.3 | 10.2 | 7.5 | 8.3 | 4.7 |
| event | 2024 (114) | 66.8 | 32.7 | 28.6 | 25.9 | 23.7 | 17.1 | 11.6 | 11.6 | 12.1 | 10.4 | 8.9 | 5.1 |
| event | all (1,335) | 70.0 | 21.2 | 18.4 | 17.6 | 15.1 | 11.7 | 11.0 | 9.6 | 10.2 | 8.1 | 8.3 | 5.4 |
| random | 2017 (174) | 25.9 | 11.2 | 8.2 | 8.8 | 6.9 | 4.9 | 5.1 | 4.3 | 3.9 | 3.5 | 3.9 | 2.0 |
| random | 2018 (600) | 44.0 | 19.2 | 16.0 | 14.5 | 12.3 | 10.7 | 10.1 | 9.0 | 8.9 | 7.9 | 7.6 | 4.7 |
| random | 2019 (779) | 52.5 | 20.7 | 16.5 | 13.8 | 12.5 | 10.2 | 9.4 | 8.1 | 8.2 | 7.1 | 6.7 | 4.5 |
| random | 2020 (705) | 68.4 | 27.0 | 22.7 | 20.8 | 19.6 | 15.1 | 13.8 | 12.3 | 13.1 | 10.5 | 9.1 | 6.4 |
| random | 2021 (405) | 56.6 | 20.4 | 18.3 | 16.8 | 14.9 | 12.0 | 11.1 | 8.1 | 9.2 | 7.2 | 7.2 | 4.1 |
| random | 2022 (469) | 71.0 | 28.5 | 23.8 | 22.0 | 20.6 | 17.4 | 15.0 | 12.4 | 12.2 | 10.5 | 9.3 | 5.4 |
| random | 2023 (507) | 81.2 | 28.2 | 24.4 | 22.3 | 18.1 | 12.7 | 11.0 | 10.2 | 10.2 | 7.8 | 7.0 | 4.4 |
| random | 2024 (342) | 47.3 | 25.1 | 23.7 | 21.0 | 18.9 | 13.3 | 11.4 | 9.3 | 9.7 | 7.4 | 6.8 | 4.2 |
| random | all (3,981) | 56.8 | 22.1 | 18.7 | 16.8 | 15.0 | 11.8 | 10.8 | 9.2 | 9.4 | 7.8 | 7.4 | 4.6 |

- The opening auction's first quote (70 bp) is a 1-minute artefact: 21 bp at 09:31, 15 at 09:35, 11 at 09:45, and
  8 at 10:15-10:30. It is still about 2x the 15:55 spread (5 bp).
- Event firms and random firms have the same profile, so insider-buy days are not wider after 09:31.
- 2017 is much tighter (2-5 bp) than 2018-24. That is Dukascopy's quoting regime, not IC.

## Cells, chance, power
- 48 counted cells (4 families x 3 offsets x 2 exits x 2 hedges), plus 12 ROUT placebo cells.
- 0 cells have net IS t >= 2. The best IS t is +0.36; the best-of-48 random-pool null has median 0.12 and p95 1.07,
  so P = 0.34.
- **Power at HOLD size** (VAL n / 3 x 1.73; `out/grade.log` power block):

| rule | HOLD n | at VAL net size | at VAL net / 4 | at VAL mid / 4, zero cost |
|---|---|---|---|---|
| primary | 249 | -1.97 | -0.49 | +0.09 |
| best of 48 | 42 | +0.26 | +0.06 | +0.27 |
| largest zero-cost value in any cell (CEOCFO 09:35 E2 U) | - | - | - | 0.38 |

  - LIVE needs power >= 3. DEMO needs IS t >= 2. Neither is close.
  - Even at zero cost, HOLD power stays below 0.4 under the 1/4 rule.
- **Bots / positions:**
  - E1 (flat each day): ALL averages 1.56 positions on event days, max 9, more than 3 on 4.0 % of event days.
    OPP / CEOCFO / CLUSTER average 1.1, max 3-4.
  - E2: ALL 2.09, max 15, more than 3 on 14 % of days. Narrow families 1.2, max 4-5.
  - So ALL needs ~3 bots of 3 positions or a concurrency cap, and the narrow families 1-2 bots. Moot.
- **C3 daily correlation** (information only; nothing survived): primary -0.050 (1,197 days), best cell -0.028 (720
  days).

## Exhausted after this stream (add to PROMPT "Những họ đã cạn")
- Insider purchases (ALL / OPP / CEO-CFO / CLUSTER, CMP families) on Dukascopy's ~220 US large-cap CFDs, as an
  intraday long on D+1:
  - entries 09:35 / 09:45 / 10:00 ET at the ask, exit 15:55 the same day or the next day;
  - unhedged or US500-hedged, at IC cost (Dukascopy spread ~11-15 bp at entry, plus USD 0.02 / share ≈ 12 bp a round
    trip).
- Result: the all-buys drift after 09:45 is +20 bp IS and +6 bp VAL at mid, so every cell is net negative. The CEO / CFO
  "day-1 +50 bp" was one penny-price outlier (IS) plus a 5-minute opening move (VAL). With round 54 this closes the
  family at any entry time with holds of 0-5 days.

## Pitfalls
- **Outliers drive the narrow families.** RRC at $1.6 on 2020-03-12 (+2,853 bp) made round 54's CEO / CFO IS day-1
  +46.5 bp; without it, +15. Low-priced names also pay 100+ bp commission a side at IC. Check a cell's top trade before
  quoting a family mean.
- **Halts:** the market-wide circuit breakers near the open in March 2020 leave ~15-30 minutes without bars (seen on
  RRC 2020-03-12: no volume 09:36-10:05 ET).
  The "first bar at or after the offset within 5 minutes" rule drops those events (26-35 per offset).
- **The pool is small:** a random pool of 3 firms per date makes the random-firm share coarse. A few crash days,
  repeated across a date's events, pulled the pool's IS intraday mean to -15.8 bp. Use the same-date cross-section,
  and more names, if the control decides a verdict.
- **Diagnostics can overwrite the log:** a diagnostic that exec'd the top of grade.py truncated `grade.log` once. It
  now takes `GLOG`, and the final log was regenerated.
- Dukascopy M1 for stocks pulled at ~4.4 files/s on 12 kept-alive connections with sporadic 503 bursts. All 17 hard
  failures came back on one retry: 503 is not "missing" for these stock files.
- The +1 minute variant moves the narrow-family cells by 20-40 bp: the per-trade sd is 200-700 bp and n ~100.

## Directions that need the user
| direction | value |
|---|---|
| IC MT5 demo login to log real 09:31-10:00 spreads on US share CFDs | low now: even at zero spread the commission (~12 bp) alone exceeds the VAL drift left after 09:45 (+6 bp ALL); DEMO < 2 % |
| A venue without per-share commission (spread-only US share CFDs) | ALL 09:45 E1 at spread-only cost: IS ~+8 / VAL ~-6 bp; DEMO ~2 %, LIVE < 1 % |
| Holds > 5 days (CMP's horizon) | outside the fixed constraints |

## Files
- Round folder: `research/results/portfolio/round55_insider_intraday/HYPOTHESES_M.md`, this file.
- Scripts are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r55/M/scripts/`:
  - duka.py: round 7 fetcher, cache moved.
  - count.py, jobs.py: event counts, job list and random pool.
  - parse.py: python -I, HOLD cut.
  - grade.py: 48 + 12 cells, variants, control, null, decomposition, spread profile, concurrency, power, C3.
  - chk_pool.py, chk_r54.py: data checks (outliers, the r54 reconciliation).
- Outputs are in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r55/M/out/`:
  grade.log, m1_days.npz, jobs.txt, pool.csv, null_maxt.npy, res.pkl, fetch.log, fetch_retry.log.
- Raw .bi5 cache and request log: `.../r55/M/cache/`.
