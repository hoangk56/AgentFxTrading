# Round 11, stream H: full intraday calendar scan of the commission-free index CFDs (2026-10-06)

Hypotheses with UTC times: research/results/portfolio/round10_new_directions/HYPOTHESES_H.md. HOLD stayed closed
(panel ends 2024-12-31; new-symbol zbars opened only for files < 20250101 and ts cut at 2025-01-01).

## H1 grid (15/60-min windows x every 15-min start x local DST-aware + UTC clock x Mon..Fri/All/First3/Last3)
- Eligible: US30 USTEC UK100 HK50 AUS200 (panel, actual spreads) + ES35 F40 IT40 STOXX50 US2000 (bid-only, round-7
  published spreads, cash session only). Info only: US500 DE40 JP225.
- K = 15,913 eligible cells (+6,706 info). Bonferroni T_K = 4.66. Per-UTC-day sign-flip null (1,000, shared by all
  cells): max |t_IS| median 3.98, 95th 4.51, 99th 4.79. Observed max 4.94 (UK100 06:45-07:00 UTC, first 3 trading
  days of the month). |t| >= 3: 87 cells vs 43 under independence (cells overlap; the null is the reference).
- Frontier (IS net per-trade Sharpe >= 3/sqrt(1.73 n/yr)): **0 cells at any t**; best netSR/S_req 0.53 (US30).
  Median cost per cell: US30 1.07, US2000 2.24, UK100 2.97, F40 3.43, USTEC 3.45, HK50 4.0, IT40 4.34, STOXX50 4.42,
  ES35 4.73, AUS200 5.12 bp. Selected: none. Tier 2: none.
- VAL (only for the pre-written repeat count): top 100 by |t_IS|: 61 % on the IS side (chance 50 %), 13 % with VAL
  t >= 1.5 on the IS side (chance 6.7 %); top 10: 40 % / 10 %. corr(t_IS, t_VAL) over all cells +0.055 vs null
  97.5th +0.062 (p ~ 0.04): a faint persistence, nowhere near tradeable. Of the 268 cells with |t_IS| >= 2.5, none
  has an IS-side VAL net Sharpe at the frontier even at VAL costs (US30 0.3 bp).
- The T_K cell: UK100 pre-open turn-of-month long, IS +3.26 bp (t 4.94) with 4.5 bp pre-open spread (net < 0);
  VAL -0.09 bp. US30 16:00-16:15 ET long: IS +1.15 (t 3.85) / VAL -0.46.

## H2 mechanism-first windows (16 eligible cells, sides fixed beforehand)
| cell | IS mid bp (t) | VAL mid (t) | cost IS/VAL | net IS / VAL | verdict |
|---|---|---|---|---|---|
| M1 MOC imbalance follow, US30 (NYSE 15:45->15:50 in 2019) | +0.29 (0.56) | -0.25 (-0.52) | 0.91/0.29 | -0.62 / -0.54 | fails |
| M1b US30 15:50 all years | +1.07 (2.18) | -0.25 | 0.91/0.29 | +0.16 / -0.54 | fails VAL |
| M1 USTEC (Nasdaq 15:50) | +1.53 (2.71) | +1.00 (1.54) | 1.67/0.65 | -0.14 / +0.35 | real-ish, at cost |
| M2 10:00 ET releases (ISM-M, ISM-S, CB conf), follow 30/60 min | US30 0.00 / -2.52; USTEC +1.41 / -3.81 | -2.9..-8.9 | 0.9-1.7 | all < 0 | fails |
| M3a UK100 follow day into 16:15-16:35 | +0.13 (0.25) | +0.27 | 2.40/1.66 | -2.27 / -1.39 | fails |
| M3b UK100 fade auction 16:36-17:30 | +0.84 (1.59) | -0.33 | 3.01/2.03 | < 0 | fails |
| M4a HK50 fade pre-lunch after 13:00 | -0.17 | -1.35 | 3.27/2.76 | < 0 | fails |
| M4b HK50 follow day 16:00-16:30 | +0.43 | -0.01 | 2.84/3.11 | < 0 | fails |
| M5a AUS200 follow day 16:00-16:30 | +0.58 | +0.08 | 2.18/1.59 | < 0 | fails |
| M5b AUS200 fade 16:00-16:12 over 16:13-16:30 | +0.82 (2.17) | +0.71 (2.71) | 2.18/1.58 | -1.36 / -0.87 | real, below cost |
| M6 3rd-Friday SOQ fade, US30 / USTEC (12/yr) | -7.3 (-2.0) / -1.8 | +13.5 (2.4) / +13.2 | 0.9-1.7 | < 0 IS | fails (sign flips) |
Family max |t_IS| 2.71 vs null median 1.97 / 95th 2.92: chance. M2 placebo (non-release days) is just as negative.

## H3 post hoc lead (not registrable from this round)
Short US30 15:45:00-16:00:00 ET on scheduled FOMC decision days (found because the all-Wednesday 15:45 cell was in
H1's top 11 and repeated in VAL, then split by FOMC): net +6.7 bp (t 2.72, n 47) IS / +9.5 (t 1.48, n 24) VAL,
SR 0.40 / 0.30, 7/9 years > 0, x1.5 +6.3 / +9.4, +1 min +6.3 / +8.5, beats 100 % / 97 % of random slots on the
same days, 84 % / 100 % of random non-FOMC Wednesdays; C3 daily corr -0.03. USTEC same shape (+5.5 / +11.5, t 1.8 /
1.35). Non-FOMC Wednesdays also negative (-3.5 t -1.9 / -2.2 t -1.4), so FOMC is only part of it. ~8 trades a year:
HOLD power ~0.3 x sqrt(14) = 1.1 (LIVE impossible); DEMO-type numbers, but post hoc after a 15,913-cell scan.
15:45 ET was also NYSE's imbalance publication time until 2019. Only clean test: new data after 2026-09-24 or the
demo account, pre-registered first.

## Files
Scripts: h_data.py (loader, HOLD cut), cov.py, grid_build.py, grid_cells.py, grid_is.py, grid_val.py, fam_m.py,
fomc_wed.py, fomc_follow.py; outputs grid_is.out/json, grid_val.out/json, fam_m.out/json, fomc_wed.out,
fomc_follow.out; hol.json (holidays pkg). All in scratchpad/r10/H/.
