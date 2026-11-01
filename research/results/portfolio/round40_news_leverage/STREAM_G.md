# Round 40, stream G: global news event and tone flows (GDELT) -> FX, JPY crosses, indices, XAU, XBR, BTC

Written 2026-10-30 (UTC). Declared before any return in [HYPOTHESES_G.md](HYPOTHESES_G.md): 58 cells at 14:08 UTC,
24 more (dyads, protests) at 14:23 UTC on 10-29, and the count and power section at 03:39 UTC on 10-30. HOLD stayed
closed: no GDELT file after 20241231 was requested, rows were checked for DATEADDED == file day (0 dropped), and IC M1
was cut at ts < 1735689600000 at load.

## Answer
**No LIVE or DEMO candidate, no PREREG_DRAFT.** Machine-coded aggregate news tone, Goldstein conflict scores, news
volume, oil-region conflict, bilateral tension and protest counts carry nothing past the entry the day after
publication. The declared continuation of country tone shocks (Tetlock 2007, Garcia 2013, slow diffusion) has the
wrong sign in IS on indices and FX. Its continuous slope is about 0 bp per sd (IS -0.55, t -0.43, on the index book at
1 day), against Tetlock's undecayed ~8 bp per sd. The best positive IS cell is at chance against the best-of-58 null
and is negative in VAL.

## Sources
- **Used:** GDELT 1.0 daily Events export, `http://data.gdeltproject.org/events/YYYYMMDD.export.CSV.zip`, 2013-04-01
  to 2024-12-31: 4,289 files listed, 36.1 GB fetched in ~3,900 GETs. Each file was aggregated on the fly into a
  per-day array (474 MB in total) and then deleted; no raw rows are kept. Two days return 404 on the server
  (2022-11-10, 2023-03-23), and 4 days are missing in 2014.
- **Publication clock** (HEAD sample of ~60 files): every file from 2015-08 to 2024 is stamped D+1 07:00:06-07:01:02
  UTC, so entry is at 08:00 UTC D+1. 2014 files are stamped 07:43-09:20, and the 2013 files were re-uploaded in
  2014-02, so PRE uses a 10:00 UTC clock.
- **Measured and not used:** GDELT 2.0 15-minute Events (95-270 KB each, ~345k files, >= 96 h at 1 request/s). The
  daily GKG is 78 MB a day (~285 GB) and was dropped; the Events `AvgTone` already averages the tone of the documents.
  With daily files, no sub-day timing test is possible.
- **Network:** a single host (data.gdeltproject.org), >= 1.1 s start-to-start across all processes (file lock), plain
  User-Agent, no personal data. No web.archive.org, no searches. Log: scratchpad `web/requests.log`.
- **Incident:** a parser bug (latitude parsed while longitude failed, so the arrays had different lengths) crashed
  both workers from ~19:24 UTC on 10-29 to 02:05 UTC on 10-30. It was fixed with a row-alignment assert. That failure
  always crashed and never misaligned silently, so the days aggregated before it are valid.

## Construction (summary; exact rules in HYPOTHESES_G.md)
Per country (ActionGeo FIPS) or region, by DATEADDED day: article-weighted tone and Goldstein scores, the share of
world articles (attention), the QuadClass-4 share (material conflict), conflict coverage of actor dyads, and the
root-14 (protest) share. Each block is z-scored against the trailing 60 days. Monday pools Fri-Sun.

Trades enter at 08:00 UTC on the weekday after publication. C1 is held 1 weekday; C3 is held 3 weekdays; R enters a
weekday later and holds 3 (reversal). Books are equal-weight over their legs: 6 index legs (US500, JP225, UK100, DE40,
AUS200, HK50), 10 FX legs (7 USD pairs plus EURJPY, GBPJPY, AUDJPY, on relative tone), and GLOBAL (world tone: BTC
the same way, XAU opposite). Costs are IC spreads at both minutes, x1.5 variant, 0.6 bp commission on FX and metals,
and the research swap model. The latency variant uses 08:01 for both legs.

## Results (net bp per trade; t is Newey-West on the book-day series)
| hypothesis | eras | mid IS (t) | net IS (t) | net VAL (t) | VAL / IS | Sharpe / trade IS, VAL | power at VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| G1 tone continuation, IDX, k1, C1 (the core declared cell) | IS, VAL | -1.56 (-0.62) | -6.19 (-2.45) | -4.18 (-1.01) | - | -0.053, -0.017 | < 0 | 0.28 / 0.63 | none (wrong sign) |
| G1 tone continuation, FX, k1, C1 (PRE -1.20, t -0.56) | IS, VAL, PRE | -1.10 (-0.94) | -2.41 (-2.06) | -2.99 (-1.57) | - | -0.048, -0.046 | < 0 | 0.10 / 0.09 | none (wrong sign) |
| G1 Goldstein continuation, FX, k1, C1 | IS, VAL | -2.96 (-2.38) | -4.27 (-3.43) | +0.34 (0.18) | - | -0.079, -0.002 | ~0 | 0.00 / 0.80 | none (wrong sign) |
| G1 tone reversal (R), IDX, k2 | IS, VAL | +15.98 (1.81) | +7.48 (0.85) | +21.76 (1.49) | 2.9 | 0.014, 0.146 | 1.6 | 0.81 / 1.00 | none (IS t < 2; legs split 3 / 3 in IS) |
| G1 world tone, GLOBAL, k2, C1 | IS, VAL | +42.6 (1.84) | +35.1 (1.51) | +66.6 (2.27) | 1.9 | 0.073, 0.221 | 1.5 | 0.82 / 1.00 | none (IS t < 2, random 82 %; VAL is BTC +120 bp on 38 trades) |
| G2 producer conflict -> XAU long, k2.5, C1 (best positive IS cell; PRE -48.8 on 5) | IS, VAL, PRE | +46.3 (2.79) | +44.2 (2.67) | -13.8 (-0.79) | < 0 | 0.535, -0.183 | < 0 | 0.99 / 0.20 | none (VAL < 0; 22 IS trades; inside the null) |
| G2 producer / lane conflict -> XBR long (8 cells) | IS, VAL | -36 to +88 | -152 to +73 (best t 1.43) | -182 to +77 | - | - | <= 0.5 | 0.08-0.78 | none (LIVE impossible from the count; no cell IS t > 1.5) |
| G3a attention reversal, IDX, k1.5, C1 | IS, VAL | +13.97 (2.67) | +9.28 (1.78) | -10.06 (-1.37) | < 0 | 0.085, -0.075 | < 0 | 0.99 / 0.13 | none (VAL < 0; ex-2020 IS +3.7, t 0.90) |
| G3b attention risk premium, IDX, k2.5, C3 | IS, VAL | +24.2 (1.39) | +16.0 (0.92) | +36.2 (0.97) | 2.3 | 0.066, 0.120 | 0.8 | 0.83 / 0.94 | none |
| G4 US-China tension -> short AUD / HK50, k1.5, C1 | IS, VAL | -10.7 (-1.73) | -13.2 (-2.12) | -8.9 (-0.97) | - | -0.168, -0.065 | < 0 | 0.01 / 0.18 | none (wrong sign) |
| G4 Russia-Ukraine -> oil / gold long, DE40 short, k1.5, C3 | IS, VAL | +11.2 (1.01) | +3.9 (0.36) | +22.9 (0.74) | 5.8 | 0.038, 0.075 | 0.7 | 0.83 / 0.94 | none |
| G4 Iran / Korea dyads (8 cells) | IS, VAL | -19 to +46 | best +38.9 (1.25) | all <= 0 | - | - | < 0 | - | none |
| G5 protests -> short the country, IDX / FX (8 cells) | IS, VAL | all < 0 | -16 to -7 (t -1.8 to -0.5) | -33 to +8 | - | - | - | - | none (wrong sign in IS everywhere) |

The full 82-row table (IS / VAL / PRE, x1.5, +1 min, ex-2020, years, random controls) is in the scratchpad
`out/run_cells_isval.txt` and `out/cells.json`.

Robustness:
- Spread x1.5 and +1 minute change no verdict: every cell keeps its IS sign, within 1-3 bp.
- Excluding 2020-03/04 shrinks every positive IS cell. G3a IDX goes from +9.3 to +3.7 (t 0.90); G2 PROD XAU k2.5 has
  no trade there and is unchanged.
- Years positive (2016-24): the best is 8 / 9 for G1 GLOBAL k2 C1 and G3b k1.5 C1. Neither meets the IS t bar.

Control regressions (G1 legs, continuous z with the previous 1-day and 5-day own return as controls, day-clustered).
The slope of the next-day mid return on tone z is:
- IDX: -0.55 bp per sd (t -0.43) in IS, +1.16 (0.52) in VAL;
- FX: -0.93 (-1.45) in IS, -0.76 (-0.69) in VAL;
- Goldstein, FX: -1.96 (-2.51) in IS, -0.04 in VAL.

The controls change nothing because the effect is already ~0. The upper 95 % bound in IS on the index book is about
+2 bp per sd, which rules out Tetlock's ~8 bp per sd after a 08:00 UTC entry.

## Cells tried and the chance benchmark
- 82 declared cells: G1 30, G2 16, G3 12, G4 16, G5 8. No post-hoc cell was run. Leg splits were printed for three
  cells (above) as information only.
- Sign-flip null (by signal day, shared by all cells, 1,000 draws) on IS:
  - G1-G3: best \|t\| 3.43 (a wrong-sign cell), p 0.13; best positive t 2.67, p 0.28 (null median 2.32, p95 3.62).
  - G4-G5: best \|t\| 2.12, p 0.65; best positive 1.25, p 0.91.
  - All 82: best positive t 2.67, p 0.38.
- No family beats its null.

## What this means
- Daily aggregate news tone is not a delayed signal for liquid FX, indices, gold, oil or BTC in 2016-24. Whatever the
  wire carries is priced before the file is public (D+1 07:00 UTC). This matches rounds 25-26 (scheduled and
  unscheduled news priced in minute 1) and round 38 H (disruptions priced at once).
- The two families with the most trades (G1 k1: 400-700 leg trades a year, where LIVE was arithmetically reachable)
  have the wrong sign in IS. The rare families (G2, G4) could at most reach DEMO, and none holds from IS to VAL.

## Correlation with C3
Not computed: nothing survived.

## Directions that need the user
| direction | value |
|---|---|
| GDELT 2.0 15-minute files (sub-day timing; ~96 h of polite requests, or BigQuery with a Google account) | LIVE < 1 %, DEMO ~1 % (daily aggregates show no drift past day 0; intraday would only re-test the minute-1 pricing of rounds 25-26) |
| Commercial news-sentiment feeds (RavenPack, Refinitiv MarketPsych; paid) | LIVE ~1 %, DEMO ~2 % |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r40/G/scripts/`
  (fetch.py, dl.py, agg.py, lm_sample.py, build_panel.py, signals.py, count_power.py, engine.py, run_cells.py).
- Outputs: `.../r40/G/out/` (count_power.txt, run_cells_isval.txt, run_cells_all.txt with PRE, cells.json, lm_sample.tsv); per-day aggregates in
  `.../r40/G/agg/`.

## PRE (2013-07..2015-12, FX and XAU legs only, 10:00 UTC clock)
Complete: 4,287 of 4,289 files (two 404 on the server: 2022-11-10, 2023-03-23). 2013-09-01 and 09-02 have no row
whose DATEADDED is the file day (61k / 130k rows dropped) and count as missing. IS and VAL are identical to the
IS / VAL-only run (diffed). PRE confirms the verdicts; no cell is strong in PRE where it was positive in IS + VAL:
- G1 tone continuation, FX, k1, C1: -1.20 (t -0.56, n 1,354). C3: +1.05 (0.25). R: -5.90 (-1.39).
- G1 Goldstein, FX, k1, C1: +1.42 (0.65).
- G1 GLOBAL (XAU leg only before 2016) k1: C1 +11.0 (1.81), C3 +26.1 (1.97). k2 C1: -2.7 (-0.21, n 41).
- G2 producer conflict -> XAU, k2.5, C1 (the best positive IS cell): -48.8 (-2.33, n 5).
- G3a FX, k1.5: C1 -3.84 (-1.19), C3 -10.6 (-2.03).
- G4 and G5 FX legs: \|t\| <= 1.4 everywhere.

Full table with PRE: scratchpad `out/run_cells_all.txt`.
