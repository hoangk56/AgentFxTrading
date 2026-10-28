# Round 31, stream J: Japan's public flow and positioning tables

Written 2026-10-27, 18:35 UTC onwards (`date -u`). Hypotheses with their UTC times: [HYPOTHESES_J.md](HYPOTHESES_J.md),
declared before any return was computed. One post-hoc rule (T4) was added after the T, M, G and I cells were in. It is
marked in both files. HOLD (2025-01..2026-09) stayed closed. Every new series was cut at 2024-12-31 when it was parsed,
and IC prices at ts < 2025-01-01 when they were loaded.

## Answer
- **No LIVE or DEMO candidate.** No PREREG_DRAFT was written.
- Five Japanese tables were joined to returns for the first time here: TFX Click 365 daily open interest and volume
  (2005-2024), MoF weekly portfolio flows (2005-2024), JPX weekly trading by investor type (2016-2024), JPX weekly
  margin balances (2002-2024) and the MoF intervention record. 70 cells in total (66 declared, 4 post hoc).
- **Best declared IS net t by family:**
  - M1 (outward flows to USDJPY): +1.14, VAL -1.30.
  - T2 (big-move days, absorption arm): +0.47.
  - G1 (margin longs, faded): +0.33.
  - X1 / X2 (investor type): +0.19 / +0.15.
  - Each is at or below what chance gives for its family's cell count.
- **No sign of a weekly flow or positioning effect in Japan's tables at 1-5 days.** The weekly flow, margin and
  investor-type tables do not predict the next 1-5 days of USDJPY, the JPY basket or JP225 at even ~10 bp. LIVE would
  need ~35 bp a week on USDJPY and ~89 on JP225.
- **TFX open interest carries real information, but not about direction:**
  - The same-day link between OI and price is strong (|corr| up to 0.63). This shows Japanese retail traders acting as
    contrarians, and shows which side they are net on.
  - Volume predicts tomorrow's absolute move (t 2-7).
  - The next day's direction is not predictable (|corr| <= 0.07 in every pair and era).
  - The post-hoc T4 rule (fade the inferred retail flow) reached IS net +5.92 bp (t 2.09). VAL was -1.91 and PRE
    -5.34, so it fails.
- **Interventions:** IS 2016-21 has none, so no rule can be graded. This was information only.

## Sources (fetch log: scratchpad `web/requests.log`, 882 requests, 1 WebSearch)
| source | fetched | history (used to 2024-12-31) | usable? |
|---|---|---|---|
| TFX Click 365 daily open interest / volume / settlement price, 7 pairs: USDJPY, EURJPY, GBPJPY, AUDJPY, EURUSD, GBPUSD, AUDUSD | the yearly "summary data" CSV (`/historical/fx/result?...submit_type=csv`), 20 requests. The per-day files under `/kawase/document/` also work (the index page returns 403) but take ~3 s each | JPY pairs 2005-07-01 to now; USD pairs 2008-10-27 to now | **yes**, but there is **one OI number per pair**: long and short are not split |
| Click 365 weekly customer buy / sell positions (`weekly_sellbuy.xls`, Tuesdays) | site + Wayback CDX | only the latest 4 weeks online. Wayback has 19 snapshots 2013-2022 and answered 429 | **no** (no history) |
| Click Kabu 365 Nikkei 225 CFD open interest | yearly summary CSV | 2010-11 to 2021-03-12 (old contract). The yearly reset contracts N21-N25 return 404 | **no** for the bars (no VAL); not tested |
| MoF weekly International Transactions in Securities | `week.csv` | weeks ending 2005-01-08 .. 2024-12-28 (1,043). Net = acquisition - disposition, computed from the columns. This is the **latest revision, not the first print** | yes |
| JPX weekly trading by investor type (TSE 1st section; Prime from 2022-04), value basis | 469 weekly PDFs (archives 2016-2024), parsed with pdftotext | 2016-01 .. 2024-12 (468 weeks; 1 unparsed, 2022-04 week 1). **No PRE online** | yes |
| JPX weekly outstanding margin transactions (customers' long / short balances), a related source found in the row | `20260925_mtsk.pdf` (history table) | 2002-08-02 .. 2024-12-27 (1,141 weeks). Osaka merged into Tokyo in 2013-07 | yes |
| JPX daily short-selling ratio | index page | only the last ~12 months | **no** |
| MoF FX intervention record | `foreign_exchange_intervention_operations.csv` | yen interventions by year: 2004 47 days, 2010 1, 2011 7, 2022 3, 2024 4 (HOLD, not used); **none in IS** | information only |
| FFAJ retail OTC net positions | not fetched | USD/JPY monthly, others quarterly | no power at 1-5 days |
| Literature | BoJ Review 2023-E-7 (PDF); RBA Bulletin March 2009 (PDF 403; abstract via search) | | side sources |

Timing assumptions (declared):

| source | data | entry used |
|---|---|---|
| TFX | day D ends 20:55 UTC; the report is posted before noon JST the next day | D+1 at 04:00 UTC |
| MoF | released Thursday 08:50 JST | Thursday 03:00 UTC (the next JP business day if Thursday is a holiday) |
| JPX investor type | 4th business day after the week, 15:00 JST | that day at 07:00 UTC |
| JPX margin | 2nd business day, 16:00 JST | that day at 08:00 UTC |

None of these entries falls inside C3's 23:00-02:00 UTC window.

## Power before the numbers (from HYPOTHESES_J)
- **Weekly signal:**
  - LIVE needs ~35 bp per trade on USDJPY or the JPY basket, and ~89 bp on JP225 at a 5-day hold.
  - That is a next-week correlation of ~0.32.
  - DEMO needs ~12.7 bp (USDJPY) or ~32 bp (JP225).
- **Daily signal:** LIVE needs ~7-10 bp per 1-day trade (correlation ~0.14). DEMO needs ~2.6-3.5 bp.
- **Literature-sized effects** (correlation 0.05-0.10 weekly, 0.02-0.04 daily) give LIVE power of only 0.4-0.8.
- **Prior: LIVE is out of reach unless the effect were 3-4x the literature's size.** The numbers below are well below
  even the literature's size.

## Results
Mid and net are in bp per trade (per basket for baskets; per entry day for multi-pair T rules). t for h = 1 is per
entry. For overlapping daily h = 3 trades, t is clustered by ISO week. "pow" = per-trade net Sharpe x sqrt(1.73 x
trades a year), divided by h for overlapping daily rules. Costs are actual IC spreads, plus 0.6 bp FX commission, plus
swap from `swap_frac_at` (FX triple on Wednesday, JP225 on Friday). PRE uses the IC 2016-17 median spread by minute +
0.6 bp, plus commission.

### Selected (IS-best) cell of each family
| hypothesis (cell chosen on IS) | eras | mid IS (t) / VAL (t) | cost (approx., incl. swap) | net IS (t) / VAL (t) / PRE (t) | VAL / IS | per-trade Sharpe IS / VAL; power (IS, VAL size) | random control (beats) | verdict |
|---|---|---|---|---|---|---|---|---|
| M1 outward flow -> yen weaker, USDJPY, k0, h3 | PRE 2005-15, IS, VAL | +7.15 (1.45) / -9.94 (-1.12) | ~1.6 | +5.61 (1.14) / -11.56 (-1.30) / -2.07 (-0.46) | < 0 | +0.065 / -0.104; 0.61, -0.99 | IS 0.90, VAL 0.145 | none |
| M2 foreign equity buying -> JP225 up, k0, h5 | IS, VAL | +16.42 (1.28) / +28.83 (1.74) | ~9 | +7.11 (0.56) / +20.74 (1.25) | 2.9 | +0.032 / +0.100; 0.30, 0.95 | n/r | none (IS t; the mid is mostly JP225's 2016-24 up-drift on the long-heavy weeks) |
| M3 foreign JGB buying -> yen stronger, basket, k1, h3 | PRE, IS, VAL | +1.98 (0.16) / +7.86 (0.47) | ~1.7 | +0.25 (0.02) / +6.32 (0.38) / -7.98 (-0.71) | | 0.002 / 0.059; 0.01, 0.29 | n/r | none |
| T1 fade retail OI adds in EURJPY / GBPJPY / AUDJPY, k1, h3 | PRE 2005-15, IS, VAL | +2.43 (0.66) / -9.38 (-1.58) | ~1.9 | +0.54 (0.15) / -11.24 (-1.89) / -5.76 (-1.37) | < 0 | 0.006 / -0.101; 0.04, -0.75 | n/r | none |
| T2 big-move day x OI change (absorption arm: continue), 7 pairs, h3 | PRE, IS, VAL | +5.17 (0.84) / +4.38 (0.55) | ~2.3 | +2.88 (0.47) / +2.87 (0.36) / -1.65 (-0.22) | 1.0 | 0.027 / 0.026; 0.16, 0.15 | n/r | none |
| T3 crowded OI level -> short crosses, h1 | PRE, IS, VAL | -0.30 (-0.13) / -1.61 (-0.24) | ~1.4 | -1.68 (-0.75) / -3.50 (-0.52) / -2.54 (-1.06) | | < 0 | n/r | none |
| T4 POST HOC: fade the retail flow inferred from the trailing OI-return correlation, 7 pairs, k1, h3 | PRE, IS, VAL | +7.98 (2.82) / -0.15 (-0.03) | ~2.1 | **+5.92 (2.09)** / -1.91 (-0.41) / -5.34 (-1.71) | < 0 | +0.068 / -0.019; 0.67, -0.19 | IS 1.000, VAL 0.59 (per leg) | none (VAL < 0, PRE < 0, post hoc) |
| G1 fade a rise in margin longs, JP225, k1, h5 | IS, VAL | +16.90 (0.64) / +21.96 (0.65) | ~8 | +8.73 (0.33) / +15.08 (0.44) | 1.7 | 0.036 / 0.067; 0.18, 0.34 | n/r | none |
| G2 fade a high margin buy / sell ratio, JP225, k1, h1 | IS, VAL | +4.02 (0.44) / -12.81 (-0.78) | ~5 | -0.82 (-0.09) / -16.24 (-0.98) | | < 0 | n/r | none |
| X1 foreigners' net buying -> JP225 continues, k1, h5 | IS, VAL | +15.09 (0.63) / -5.19 (-0.14) | ~10 | +4.54 (0.19) / -14.86 (-0.40) | < 0 | 0.019 / -0.058; 0.10, -0.30 | n/r | none |
| X2 fade individuals' net buying, JP225, k1, h3 | IS, VAL | +13.98 (0.56) / -8.01 (-0.24) | ~10 | +3.70 (0.15) / -17.62 (-0.53) | < 0 | 0.016 / -0.075; 0.08, -0.40 | n/r | none |
| X3 foreigners' buying -> yen stronger, USDJPY, h5 | IS, VAL | +0.41 (0.09) / +3.93 (0.42) | ~1.6 | -1.17 (-0.27) / +2.22 (0.24) | | < 0 | n/r | none |
| I1 continue after an intervention, USDJPY, h5 (information) | PRE 2004 / 2010-11, VAL 2022 | 2004 +33.2, 2010-11 -36.7, 2022 +5.9 | ~3 | 2004 +30.2 (t 1.15, 47 days in 12 weeks) / 2010-11 -39.7 (-1.24, 8 days) / 2022 -0.1 (3 days) | | | n/a | information only (no IS event) |

"n/r" = not run. A random control only matters for a cell that is near a bar. For the two cells with IS t > 1, it
was run with 200 seeds: random days of the same weekday and clock in the same era, with the side sequence permuted. For
T4 the control is per leg, per pair.

### All cells (IS net t; full numbers in scratchpad `out/*_cells.json`)
- **M (24 cells):**
  - M1 basket: -0.32 to +1.06. M1 USDJPY: +0.03 to +1.14. M2 JP225: -0.77 to +0.73. M3 basket: -0.75 to +0.02.
  - **VAL**: M1 basket k1 h1 is the only notable cell, net +20.08 (t 2.48), but its IS is +2.35 (t 0.26) and its PRE
    is +3.29 (t 0.50). It was not chosen on IS, so it is a VAL-only draw.
  - h5 = h3 for Thursday entries because of the 5 x 24 h cap.
- **T (12 declared):**
  - T1: -1.29 to +0.15.
  - T2:
    - both arms h1 -1.99 (the declared side is wrong in all three eras: mid PRE -5.71, IS -2.94, VAL -4.12);
    - the liquidation arm -1.06 to -0.69;
    - the absorption arm -0.57 to +0.47.
  - T3: -0.75 to -0.31.
- **T2 with the side reversed (information, after looking).** Rule: a big move continues when OI fell, and reverts when
  OI rose.
  - h1 net: IS +1.61 (t 0.73), VAL +2.59 (0.71), PRE +3.83 (1.08).
  - It is consistent in sign across the three eras but nowhere near DEMO (IS t 2).
- **T4 post hoc (4 cells):** k0 h1 +0.39, k0 h3 -0.02, k1 h1 +0.93, k1 h3 +2.09. Every VAL is <= 0 and every PRE is < 0.
- **G (12 cells):** -1.02 to +0.33.
- **X (14 cells):** -1.11 to +0.19.
- **I (9 information cells):** see the table above.

## Multiple testing
The median of max |Z| over K independent cells is:

| cells (K) | median of max \|Z\| |
|---|---|
| 12 | 1.91 |
| 14 | 1.96 |
| 16 | 2.03 |
| 24 | 2.19 |
| 70 | 2.58 |

The observed best IS |t| by family:

| family | best IS \|t\| | side | against chance |
|---|---|---|---|
| T (declared) | 1.99 | wrong side | about the median of 12 |
| T + T4 | 2.09 | | about the median of 16 |
| M | 1.14 | | below the median of 24 |
| G | 1.02 | | below |
| X | 1.11 | | below |

No family is beyond chance, and over all 70 cells the best |t| (2.09) is below the null median of 2.58.

## Information worth keeping
1. **TFX OI reveals the side of retail traders without a long / short split.**
   - The same-day corr(r_D, dOI_D) is large and its sign changes over time:
     - AUDJPY: IS -0.59, VAL -0.33 (net long, buying dips);
     - USDJPY: PRE -0.36, IS +0.11, VAL +0.63 (net short, selling the 2022-24 yen fall);
     - EURJPY: PRE -0.13, IS +0.41.
   - This matches the BoJ Review's account of retail traders as contrarians who changed net side in USD/JPY in 2022.
   - It is a cheap daily proxy for the FFAJ's monthly net-position table. It does not predict the next day.
2. **Click 365 volume predicts the next day's |return| beyond today's |return| in every pair and era**: +1 to +9 bp per
   z, t 0.6-7.0. Volatility information, not direction, so not tradable at IC without options.
3. **MoF weekly flows: the published (revised) weekly numbers do not predict the yen over the next 1-5 days.**
   - This holds for outward flows, foreign equity flows and foreign bond flows, in PRE, IS and VAL.
   - Any effect is priced before or at the Thursday release, or the flow is not persistent enough week to week.
   - The values are the latest revision, which would favour finding an effect, and none was found.
4. **Foreign-investor persistence and fading individuals (Kamesaka et al. 2003) are absent in 2016-24 JP225 at 1-5
   days.** So is the margin-overhang lore (信用倍率, margin-long changes).

## Directions that need the user (with a one-line value estimate)
- **Click 365 weekly customer buy / sell history** (`weekly_sellbuy.xls` keeps 4 weeks).
  - Only TFX itself, by request, or a paid vendor could supply it. The Internet Archive holds 19 snapshots.
  - Value: low. It is weekly (DEMO needs ~12.7 bp a week). The inferred side in point 1 already gives the net side,
    and its flow does not predict.
  - LIVE probability ~1 %.
- **FFAJ / broker-level daily retail net positions** (OANDA Japan, Gaitame order books need accounts; gaitame.com is
  unreachable here).
  - Value: low-moderate as research. A daily net side with the split might reach correlation 0.05, still below LIVE's
  0.14.
  - LIVE ~1-2 %.
- **First-print (unrevised) MoF weekly numbers.** These would remove a revision look-ahead. They could only lower the
  results above, so they are not worth fetching.
- **JPX investor-type weekly data before 2016** (offline / paid; JPX's site starts 2016). It would give a PRE era for
  X1 / X2. Value: ~0, because IS / VAL already show nothing.

## Scripts and outputs
Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r31/J/`

- **Fetching:**
  - `scripts/fetch.sh`, the logged fetcher (1.2 s sleep);
  - `scripts/dl_jpx.sh`;
  - `scripts/dl_tfx.sh`, the per-day TFX route, abandoned for the yearly summary.
- **Parsers** (run with `python -I`; they cut at 2024-12-31): `scripts/parse_tfx.py`, `parse_mof.py`, `parse_jpx.py`,
  `parse_margin.py`, `parse_feio.py`.
- **Engine:**
  - `scripts/jlib.py`: quotes, fills, costs, swap and t;
  - `scripts/wk.py`: weekly evaluation and the random control;
  - `scripts/tsig.py`: TFX signals.
- **Runs:**
  - `scripts/run_M.py`, `run_G.py`, `run_X.py`, `run_I.py`;
  - `run_T13.py`: the final T1-T3, after an AUDJPY H1 PRE quote fix; `run_T.py` was the first pass;
  - `run_T4.py`;
  - `run_T2rev.py`;
  - `run_rand.py`.
- **Outputs:** `out/*_cells.json`, `out/rand_M.txt`, `out/rand_T4.txt`, and the parsed series `out/*.npz`. The raw
  downloads are in `web/`.

Correlation with C3: not computed, because no rule survived.
