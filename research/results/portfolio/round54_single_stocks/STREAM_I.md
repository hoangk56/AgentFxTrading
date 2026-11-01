# Round 54 stream I: insider purchases on the firm itself (Cohen, Malloy & Pomorski 2012) -> the firm's stock CFD

Written 2026-10-30 10:45 UTC. Hypotheses: [HYPOTHESES_I.md](HYPOTHESES_I.md), declared 10:12 UTC before any price was
loaded. Addendum 1 (10:23, cost model and hedge details, before any return) and Addendum 2 (10:41, close-entry family,
after the open cells and before any close number) are dated in that file. Bars: LIVE / DEMO from research/PROMPT.md.
HOLD (2025-01..2026-09) stayed closed. Filings are cut at 2024-12-31 at parse (asserted, 0 dropped). Prices come from
D's stocklib (cut at load), US500 M1 at ts < 1735689600000. No 2025-26 value was loaded or printed.

## Answer
**No LIVE, no DEMO, no PREREG_DRAFT.** 0 of 48 cells has a positive net IS t >= 2. The best net IS t is 0.42 (CEOCFO h5
H at the close), against a best-of-48 null median of 0.57. LIVE was ruled out by the count before any return was
computed (HOLD n ~40 for OPP).

One real effect sits underneath, and it cannot be traded at IC's costs. On the first session after the filing date,
the firm beats random firms on the same dates, at mid, in both eras:
- all insider buys: +17.6 bp IS / +19.7 bp VAL, open to close, beating 1.00 / 0.99 of random-firm draws;
- CEO / CFO buys: +46.5 / +59.3 bp, beating 1.00 / 1.00.

The effect is on day 1 only: close-to-close from the D+1 close is ~0 or negative. Catching day 1 means buying at the
open, where Dukascopy's opening spread (median 57-103 bp for these events) costs more than the effect. Even at mid the
per-trade Sharpe is ~0.07 (all buys) to ~0.12 (CEO / CFO), so HOLD power is about 1 at zero cost.

## Data
- Form 4 (SEC DERA insider data sets). Round 44's 2014-24 zips were reused read-only. **2013 Q1-Q4 were fetched now**:
  robots.txt plus 4 zips, all HTTP 200, 10:08:17-10:08:23 UTC. robots.txt has `User-agent: *` only and allows
  `/files/`. Generic research UA, no e-mail. Log: `.../r54/I/web/requests.log`.
- The owner-level parse gives 795,299 (accession, owner, P / S) rows for 2013-24. Classification follows CMP 2012: per
  owner, over the 3 prior calendar years, routine = traded in the same calendar month in all 3 years. Opportunistic =
  traded every year but not routine. 2013 makes 2016 classifiable.
- Universe: D's 219 non-ETF stocks, matched on issuer CIK. Daily data starts 2017-01..2018-02, so IS is in effect 2017-21.
- Events (firm-days) for IS 2016-21 / VAL 2022-24: ALL 1,230 / 442; OPP 225 / 68; CEO/CFO (non-routine) 160 / 79;
  CLUSTER (>= 2 non-routine buyers in 7 days) 151 / 59; ROUT placebo 68 / 43. After one position per firm and price
  coverage, ALL h1 has 869 / 440 trades and OPP 165 / 68. 5 trades across D-flagged non-round jumps were dropped.

## Results (net bp per trade, long the firm; H = short IC US500 at the same minute; day-clustered t)
Open cells: entry at the open after filing date D, exit at the open h days later. Close cells: entry at the close of
D+1, exit at the close h days later. Costs follow D's model: the Dukascopy spread of the candle traded, USD 0.02 a
share per side, and (EFFR + 3 %)/360 a night.

| cell | n IS / VAL | mid IS (t) | cost IS | net IS (t) | net VAL (t) | x1.5 IS / VAL | +1 day IS / VAL | ex 2020-03/04 IS | Sharpe IS | random-firm beats IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OPP h5 H open (primary) | 157 / 64 | +25.2 (0.56) | 114 | -88.4 (-2.02) | -114.4 (-2.55) | -132 / -161 | -112 / -177 | -79.5 | -0.16 | 0.66 / 0.44 | none |
| ALL h1 H open | 869 / 440 | +26.9 (2.78) | 98 | -71.4 (-7.47) | -91.0 (-8.74) | -113 / -136 | -93 / -99 | -68.2 | -0.27 | 0.93 / 0.59 | none |
| ALL h3 U open | 775 / 394 | +41.3 (2.28) | 100 | -58.3 (-3.12) | -55.6 (-2.37) | -99 / -100 | -77 / -93 | -46.7 | -0.13 | 0.86 / 0.90 | none |
| CEOCFO h3 U open (best open IS t) | 115 / 73 | +132.2 (1.78) | 120 | +12.1 (0.17) | -28.5 (-0.53) | -37 / -83 | -10 / -92 | -23.9 | 0.02 | 1.00 / 0.75 | none |
| CEOCFO h5 H open | 113 / 71 | +148.8 (1.61) | 137 | +12.0 (0.13) | -112.9 (-2.06) | -42 / -170 | -33 / -180 | -47.6 | 0.01 | 1.00 / 0.46 | none |
| CLUSTER h3 U open | 96 / 59 | +115.9 (1.51) | 121 | -4.9 (-0.07) | -162.3 (-2.68) | -55 / -209 | -41 / -192 | -67.7 | -0.01 | 0.98 / 0.07 | none |
| OPP h5 H close (primary close) | 151 / 64 | -4.3 (-0.09) | 42 | -46.6 (-1.05) | -97.1 (-2.20) | -55 / -103 | -15 / -87 | -71.2 | -0.09 | 0.41 / 0.13 | none |
| CEOCFO h5 H close (best of 48) | 115 / 70 | +75.9 (1.04) | 46 | +30.0 (0.42) | -105.5 (-1.90) | +21 / -113 | -71 / -69 | -2.1 | 0.04 | 0.96 / 0.09 | none |
| ALL h5 U close | 714 / 364 | +6.4 (0.20) | 31 | -24.5 (-0.76) | -54.3 (-2.08) | -30 / -60 | -27 / -41 | +12.8 | -0.04 | 0.62 / 0.03 | none |
| ROUT h1-h5 (placebo, both) | 36-38 / 35-43 | -85 to +11 | 19-81 | -128 to -48 | -36 to +90 | - | - | - | - | - | ~0 / negative, as CMP predict |

The full 48-cell tables with by-year rows are in `out/grade.log` (open) and `out/grade_close.log` (close).
- Cost split, open cells (IS): spread 79-108 bp, commission 11-15 bp, financing 1.5-9 bp. The firms where insiders buy
  are cheaper and wider-spread than the average name: commission alone is 2x D's median.
- By year, the best open cells are negative in 5-7 of 8 years. CEOCFO h3 U open: 2017 +26, 2018 +31, 2019 -64,
  2020 +86, 2021 +7, 2022 +81, 2023 -80, 2024 -172.
- **Diagnostic, optimistic close-spread fills** (post hoc, not graded, Addendum 1): open h1-h5 net ranges from -33 to
  +103 bp, with every IS t <= 1.35. Best: CEOCFO h3 U +93.0 (1.35) IS / +66.9 (1.30) VAL.

### Where the effect is (post hoc, `diag2.log`, `diag3.log`; mid; random firm = same dates, 200 draws)
| family | era | D+1 open -> close mid (t) | beats random | D+1 close -> D+2 open mid | same-day net, Dukascopy open spread (t) | same-day net, close spread (t) | median open spread |
|---|---|---|---|---|---|---|---|
| ALL | IS / VAL | +17.6 (1.92) / +19.7 (1.71) | 1.00 / 0.99 | +6.5 / +4.5 | -40.6 (-4.33) / -44.7 (-3.80) | -6.2 / -5.2 | 61 / 73 bp |
| OPP | IS / VAL | +17.4 (1.10) / +27.5 (1.12) | 1.00 / 0.96 | +13.6 / -23.7 | -40.3 / -34.4 | -9.6 / +4.0 | 57 / 84 |
| CEOCFO | IS / VAL | +46.5 (1.60) / +59.3 (2.16) | 1.00 / 1.00 | -8.7 / -2.9 | -23.8 / -19.3 | +15.3 (0.56) / +29.6 (1.11) | 70 / 103 |
| CLUSTER | IS / VAL | +45.6 (1.24) / +42.8 (1.29) | 1.00 / 0.99 | -31.1 / -3.5 | -19.6 / -28.3 | +16.4 / +14.6 | 60 / 85 |
- Open-to-open h1 at mid also beats random firms in both eras: ALL 1.00 / 0.95, CEOCFO 1.00 / 0.96. CMP's split
  (opportunistic vs routine) shows here as **CEO / CFO and cluster vs all**: the routine placebo is negative.
  Opportunistic buys alone are no stronger than all buys over 225 events.
- Power at mid, zero cost: ALL day 1 ~+19 bp against a per-trade sd of ~270 bp gives Sharpe ~0.07, so HOLD power ~1.1
  (n ~245). CEO / CFO ~+50 bp against ~420 bp gives ~0.12, power ~0.8 (n ~44). **LIVE is out of reach even at zero
  cost; DEMO would need a fill near mid at the open.**

## Cells and chance
- 48 counted cells: 24 open (declared) plus 24 close (Addendum 2), plus 12 ROUT placebo cells that are not counted.
- No cell has a positive net IS t >= 2. 11 open cells and 4 close cells have IS t <= -2 (cost).
- Best-of-24 null, open, 500 random-firm seeds (each cell recomputed): median max t -0.74, p95 0.14. The best open
  cell (t 0.17) is at p 0.05: insider firms beat random firms, who pay the same opening spreads.
- Close: median 0.57, p95 1.52; the best close t of 0.42 has p 0.60.
- Best-of-48 (max of the open and close seeds): median 0.57, p95 1.52. The overall best (0.42) is below the median.

## Bots / positions
With one position per firm, mean open positions are: ALL 0.63 (h1), 1.70 (h3), 2.69 (h5), with a max of 17 and > 3
open on 30 % of days at h5. OPP / CEOCFO / CLUSTER: 0.1-0.5 on average, max 3-7. A book would need ~6 bots of 3
positions for ALL h5, or 2-3 bots for the narrow families, or a concurrency cap. Moot, since nothing survives.

## C3 correlation
No surviving cell. For information, the daily P&L correlation with C3 (trades_C3_gotobi_jpy_basket.csv, present, cut
at 2024) is -0.005 for CEOCFO h3 U open and +0.022 for ALL h1 H open.

## Exhausted after this stream (add to PROMPT "Những họ đã cạn")
- Firm-level SEC Form 4 open-market purchases by officers / directors on Dukascopy's ~220 US large-cap CFDs: all, CMP
  opportunistic, CEO / CFO, cluster, routine placebo. Long the firm 1-5 days from the next open or the D+1 close,
  unhedged or hedged with US500. It is a real day-1 drift: +18 bp (all) to +50 bp (CEO / CFO), firm-specific, in both
  eras. It is below the cost of an opening fill (~60-100 bp Dukascopy spread + 11-15 bp commission). After day 1 there
  is nothing.

## Pitfalls
- Dukascopy stock CFDs quote a very wide first candle: median open spread 65 bp vs 7 bp at the close (D). Any rule that
  must trade the open is graded on that spread. Whether IC MT5's 09:30 spread is narrower is unknown offline.
- Insider-buy firms are lower-priced and wider-spread than the list average. Per-share commission is 11-15 bp per round
  trip (2x the median), so use the event firms' own costs, not D's median.
- The firm-day effect is in the D+1 regular session, not after it. Close-entry rules miss it; overnight close -> open
  adds nothing.
- CMP's routine / opportunistic rule needs 3 prior years of trades. Most large-cap insider buyers are occasional
  directors and stay unclassified (~78 % of ALL events in IS). OPP has only ~37 events a year on this list.
- Dukascopy tickers are old names (FB, PCLN, CTL...): match on CIK, never the Form 4 trading symbol.
- 2020-03/04 holds ~40 % of 2020's events. Ex-covid IS numbers are in the logs; no cell turns positive.

## Directions that need the user / next rounds
| direction | value |
|---|---|
| Intraday entry 5-30 min after the open from Dukascopy stock M1 / ticks (approved feed; 2017-24 for these names), to capture the day-1 drift at a normal spread. No user decision needed, but it is a new pull of ~220 names x M1 | LIVE ~1 % (power ~1 even at mid), DEMO ~5 % (CEO / CFO day 1 only, if the drift is not front-loaded into the first minutes) |
| IC MT5 demo login to measure IC's real 09:30-09:35 spreads on US share CFDs (user account) | settles whether any open-fill stock rule can work; DEMO for this family ~5 % |
| Holds > 5 days (CMP's effect lives at months) | outside the constraints |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/I/scripts/`
  - fetch.py: round 44's SEC fetcher.
  - parse_owner.py: owner-level parse, python -I, HOLD cut.
  - events.py: CMP classification and events.
  - us500_open.py, us500_close.py: the hedge leg.
  - grade.py: 24 cells, variants, random-firm control and null; `AT=close` for the Addendum 2 family.
  - diag.py: concurrency and C3 correlation.
  - diag2.py, diag3.py: post hoc mid, close spread and day-1 decomposition.
- Outputs are in `.../r54/I/out/`: events.csv, grade.log, grade_close.log, diag.log, diag2.log, diag3.log,
  null_maxt*.npy and owner_trades.csv.
