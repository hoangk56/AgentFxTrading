# Round 45, stream X: one declared combined model over the daily non-price features of rounds 37-44

Written 2026-10-30 06:36 UTC (`date -u`). The declaration is in [HYPOTHESES_X.md](HYPOTHESES_X.md), written at 06:32 UTC.
It came before any return, fit or forecast. Nothing was changed after the numbers; there were no amendments. Bars are
those of research/PROMPT.md, LIVE / DEMO only.

HOLD (2025-01-01..2026-09-24) stayed closed:
- Every source row dated after 2024-12-31 was dropped at load, with asserts. CFTC as-of dates stop at 2024-12-24.
- IC M1 was cut at ts < 1735689600000 and US2000 zbars at < 20250101.
- No 2025+ value was loaded or printed.
- No new data was downloaded. Every file the declaration names was on disk; none had vanished.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

The declared pooled ridge has 26 families: 86 series mapped onto 118 symbol legs. It covers 13 sources from rounds 37-44 and trades a 12-symbol
daily book.

| era | net per trade | mid per trade |
|---|---|---|
| IS walk-forward 2017-21 | -0.034 R (t -2.30) | +0.004 R (t +0.24) |
| VAL 2022-24 (IS fit frozen) | -0.003 R (t -0.14) | +0.022 R (t +1.15) |

It sits inside the shuffled-feature null:
- Net t: IS p 0.37, VAL p 0.11.
- Mid t: IS p 0.41, VAL p 0.11.
- The null's median net t is -2.67 (IS) and -1.43 (VAL): that is the cost of trading on noise.

So the combination behaves exactly like features with their dates scrambled, as the brief said to expect if the
single-source effects are noise. The features are nearly independent (mean |corr| between families 0.015, max 0.31).
Still, the out-of-sample forecast-return correlation is about zero: -0.003 IS walk-forward, +0.015 VAL. The in-sample
2016-21 fit shows mid t 3.14, which is the usual overfit. The ridge's coefficients change sign between yearly refits for
about a third of the families.

## Sources used (all from the round 37-44 scratchpads; detail and timestamp rules in HYPOTHESES_X.md)
FINRA short-volume ratio (11 ETF legs), ETF creations (SPY+IVV, IWM, EWJ), BTC funding (Bybit 2018-11, Binance
2019-09), Connect southbound, GDELT tone (index / FX / world) and producer conflict, Chinese margin financing and
short sales, US / JP / DE auction supply cycle, EDGAR issuance and buybacks, insider net purchases, heavyweight
earnings weight, BoJ offer-to-cover, morning cloud / wind / temperature / haze, CFTC TFF (leveraged funds,
asset-manager changes, disaggregated managed money), legacy non-reportable, and the 52-week range position.

Excluded before any return:
- Sparse event sources: SHFE / SGE margin changes, storms, ratings, football.
- Northbound Connect, which has not been published since 2024-08-19.
- Second forms of the same sources.

## Results
Unit: 1 risk unit per trade (R = net bp / trailing 60-day sd of the symbol's clock-to-clock return). t is
day-clustered. Fills are at the bar close one minute after the clock, at the actual ask and bid. FX and XAU pay 0.6 bp
commission and every trade pays swap.

| hypothesis | eras | mid R (t) | cost R / trade | net IS / VAL R (t) | VAL / IS | per-trade Sharpe; power at HOLD size | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| X: pooled ridge (lambda 0.1 N), 26 families, \|f\| >= 0.5 RMS, hold 1 weekday, 12 symbols | IS WF 2017-21 n 9,641; VAL n 5,849 | IS +0.0035 (0.24); VAL +0.0217 (1.15) | ~0.037 IS, ~0.024 VAL | -0.0336 (-2.30) / -0.0026 (-0.14) | n/a (IS < 0) | IS -0.031, VAL -0.003; daily-book Sharpe IS -0.064, VAL -0.005 -> HOLD power -1.35 (IS size) / -0.11 (VAL size), ~3,370 HOLD trades | 56.8 % / 93.0 % | **none** |
| spread x1.5 | same | same | | -0.0416 (-2.85) / -0.0064 (-0.34) | | | | none |
| both legs +1 min | same | +0.0035 / +0.0217 | | -0.0334 (-2.28) / -0.0031 (-0.17) | | | | none |
| info: threshold 0 (every row) | n 14,880 / 9,227 | +0.0021 (0.19) / +0.0153 (1.03) | | -0.0345 (-3.02) / -0.0092 (-0.62) | | | | not eligible |
| info: in-sample IS fit | n 9,133 / 5,849 | IS +0.0499 (3.14) | | +0.0149 (0.94) / -0.0026 | | | | optimistic, not eligible |
| info: equal-weight declared-side vote, \|f\| >= 1 | n 4,979 / 2,930 | +0.0257 (1.17) / +0.0134 (0.60) | | -0.0104 (-0.47) / -0.0102 (-0.45) | | | | not eligible |

Years (sum of R), ridge: 2017 -122.6, 2018 -129.5, 2019 -113.5, 2020 +72.0, 2021 -30.4 | 2022 +84.5, 2023 -46.4,
2024 -53.5. That is 2 of 8 years positive.

The forecast-return correlation was -0.0031 on all IS rows (-0.0021 on traded rows) and +0.0147 on VAL (+0.0180 on
traded rows). Clearing the cost would need ~0.04-0.05, and LIVE ~0.08-0.1.

Shuffled-feature null (declared). Each draw shifts every family's block circularly by its own random offset and
refits the whole pipeline (500 draws). A second version permutes days i.i.d. (200 draws).

| statistic | observed | circular null p50 / p95 | p (share >= observed) | i.i.d. null p |
|---|---|---|---|---|
| IS walk-forward net t | -2.30 | -2.67 / -0.50 | 0.37 | 0.32 |
| VAL net t | -0.14 | -1.43 / +0.28 | 0.11 | 0.085 |
| IS+VAL net t | -1.90 | -2.97 / -0.65 | 0.16 | 0.135 |
| IS mid t (information) | +0.24 | +0.02 / +2.19 | 0.41 | |
| VAL mid t (information) | +1.15 | -0.07 / +1.63 | 0.11 | |

Per symbol (net R, t), IS / VAL:

| symbol | IS | VAL |
|---|---|---|
| US500 | -0.005 (-0.11) | -0.012 (-0.23) |
| USTEC | -0.007 | -0.006 |
| US2000 | +0.022 (0.56) | -0.025 |
| JP225 | -0.066 (-1.71) | -0.031 |
| HK50 | -0.134 (-3.70) | +0.042 (0.81) |
| DE40 | -0.008 | -0.016 |
| EURUSD | -0.004 | -0.031 |
| USDJPY | -0.065 (-1.81) | +0.046 (0.92) |
| AUDUSD | -0.065 (-1.79) | -0.048 (-1.06) |
| XAUUSD | -0.059 (-1.60) | +0.004 |
| XTIUSD | -0.015 | -0.042 |
| BTCUSD | +0.001 | +0.080 (1.71) |

No symbol is positive in both eras with t > 0.6.

Single-family declared-side correlation with the next-day return, on rows where the family is available, IS 2016-21 /
VAL. This is information only; using it to choose families would be selection by VAL, which is banned.
- Same sign in both eras, +0.02 to +0.07: FUNDING (+0.040 / +0.049, n ~770 each), WX_HAZE (+0.037 / +0.071,
  n 1,390 / 712), EDG_SUPPLY (+0.050 / +0.035), GD_WORLD (+0.023 / +0.025), WX_TEMP (+0.022 / +0.020).
- EARN is on the wrong side in both (-0.027 / -0.037).
- The rest have |r| < 0.03 or flip sign.

Even the stable ones are 0.02-0.05 per row on one to three symbols. That matches the single-source results of rounds
37-44 (those streams saw the same data at the same clocks). It is not a new candidate.

Correlation with C3: not computed, because nothing survived.

## Cells and chance
One eligible model (3 stress lines), plus 3 information-only diagnostics. The chance benchmark is the shuffled-feature
null above. The observed model sits at its 63rd percentile (IS) and 89th percentile (VAL) of net t.

## Why it fails
- Combining uncorrelated features adds their predictive power only if each one keeps a stable sign out of sample.
  - The walk-forward ridge re-estimates 26 coefficients each year from ~2,000-13,000 rows per year.
  - Per-family signals of |r| ~0.02 are inside the estimation noise (1 / sqrt(n) ~0.01-0.03 per family-year).
  - So the fitted weights mostly track noise: AUC_JP -59 -> +26 -> -5, CONNECT_SB +27 -> -4, RNG52 0 -> -24 -> +21
    (x1000).
- The equal-weight declared-side vote avoids that estimation, but half the declared sides are wrong or flip between
  eras: GDELT tone, earnings, margin leverage, BoJ, sunshine.
- Cost: about 0.037 R per trade in 2016-21 (BTC ~13 bp, XTI ~7 bp, HK50 / JP225 ~3 bp). The best case seen at mid,
  VAL +0.022 R, is below it.

## Pitfalls
- In-sample fits of many weak features look good (mid t 3.14 here) and vanish walk-forward (0.24). Grade combined
  models walk-forward only.
- A cost-paying daily book has a null centred well below zero (here net t -2.7 IS). Compare with the null's
  distribution, not with zero.
- GDELT block z for weekday E is public only from E 08:00 UTC, so Asian clocks use E-1. CN margin totals for day D
  are used from the next CN trading day at 01:30 UTC. Weekly CFTC values move to Monday in federal-holiday weeks.

## Directions that need the user
None new. Even at zero cost the VAL mid of +0.022 R per trade gives a daily-book Sharpe of ~0.04: HOLD power ~0.8,
below LIVE at any venue (< 1 %).

## Files (scratchpad r45/X/)
Scripts:
- `scripts/common.py`: clocks, grid, trailing z.
- `scripts/feats.py`: the 13 sources, with public times.
- `scripts/mapfeat.py`: maps the series onto the clocks and builds RNG52.
- `scripts/prices.py`: IC prices, cut.
- `scripts/rets.py`: returns, costs, swaps, sigma.
- `scripts/model.py`: the ridge, the walk-forward, the nulls.
- `scripts/main.py`: grading, controls, diagnostics.

Outputs:
- `out/main.txt`
- `out/null_summary.txt`
- `out/null_circ_1.npy`, `out/null_iid_2.npy`
- `out/featmat.npz`, `out/features_meta.json` (coverage per series and year), `out/rets.npz`, `out/grid.npz`
