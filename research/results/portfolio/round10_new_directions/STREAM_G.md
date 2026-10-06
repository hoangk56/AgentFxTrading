# Round 11, stream G: cross-sectional momentum / reversal at 1-5 days (2026-10-06)

Rules: research/results/portfolio/round10_new_directions/HYPOTHESES_G.md (written 00:30 UTC before any return;
DG at 00:33 and G5/DG2 at 00:34 UTC, both after the G1-G3 numbers, G5 marked post hoc). HOLD closed: shared panel
(2016-2024) only, Dukascopy H1 2004-2015 for PRE, no M1 cache opened. Sides fixed from the literature: momentum in
currencies (Menkhoff et al. 2012; Raza, Marshall & Visaltanachoti 2014; Zaremba, Long & Karathanasopoulos 2019),
indices (Zaremba et al. 2019) and commodities (Kwon, Kang & Yun 2019). Nagel reversal = declared competitor (G2n).

## Result: no candidate, no PREREG_DRAFT

| hypothesis | IS-chosen cell | IS mid bp (t_wk) / VAL | cost IS / VAL | net IS / VAL (t_wk) | power/trade | other | verdict |
|---|---|---|---|---|---|---|---|
| G1 G8 currencies, top-bottom momentum, 20:00 UTC | k3 hW | +2.15 (0.27) / -0.17 (-0.02) | 4.7 / 3.3 | -2.56 (-0.33) / -3.45 (-0.32) | -0.18 | rand 63/50 %; PRE mid -15.9 (t -2.03), net -20.3 (t -2.57) | fails IS, fails PRE |
| G2m same, high dispersion only | k1 h3 | +7.15 (0.90) / +0.72 (0.10) | 3.4 / 2.8 | +3.74 (0.47) / -2.10 (-0.29) | 0.31 | rand 88/52 %; PRE net -10.4 (t -1.70) | fails |
| G2s lot 2x high / 0.5x low | k3 hW | +4.52 (0.53) / -1.04 | 3.8 / 4.0 | +0.73 (0.09) / -4.99 (-0.30) | 0.05 | | fails |
| G2n Nagel reversal, high dispersion | k5 hW | +2.82 (0.11) / -2.58 | 4.0 / 3.8 | -1.14 / -6.41 | <0 | | fails |
| G3i 8 indices, vol-adj momentum, 14:00 UTC | k1 hW | +7.6 (0.63) / -56.6 (-2.06) | 16.0 / 13.7 | -8.5 (-0.71) / -70.3 (-2.56) | <0 | every IS cell net < 0 | fails |
| G3c 6 commodities | k3 hW | -18.6 (-0.34) / +102.9 (1.94) | 36.6 / 54.8 | -55.2 (-1.02) / +48.1 (0.91) | <0 | VAL-only trend (2023-24) | fails |
| G3c2 XAU XAG XTI | k1 h1 | +13.9 (2.19) / +4.2 (0.73) | 8.1 / 7.1 | +5.7 (0.91) / -2.9 (-0.50) | 0.60 | IS = 2020 oil crash only (2018-19, 2021 <= 0); winsorised t 0.81 | fails |
| G5 post hoc: G1 on extreme formation-spread days | k1 h3 | +12.7 (0.92) / -22.7 (-1.65) | 3.4 / 3.4 | +9.3 (0.68) / -26.1 (-1.91) | 0.43 | PRE h1 net +1.5 (t 0.13) | fails |

Stresses of the chosen cells (spread x1.5, +1 min, entry +1 h) change nothing (all in analyse_out.txt).

Chance (per-week sign flips shared by a family's cells, 1,000 permutations; 95th pct of the best |t_IS|): G1 2.65,
G2m 2.74, G2s 2.71, G2n 2.84, G3i 2.66, G3c 2.67, G3c2 2.66; max of 9 normals 2.77. Best IS mid |t| per family:
1.45, 0.90, 0.58, 0.90, 1.96, 1.03, 2.19, all below chance. (Large negative net t such as G3i -4.9 are the cost
itself, not a signal.) Cells: 63 declared + 2 post hoc.

Diagnostics (no position cap, mid only, h 1 day):
- DG rank-weighted dollar-neutral currency slope: k1/3/5 IS -1.36 / +0.48 / -0.28 bp/day (|t| <= 1.51), VAL
  -0.59 / -1.91 / -0.57 (|t| <= 1.38), PRE +0.12 / -0.07 / -0.44 (|t| <= 0.42). Indices: |t| <= 1.24.
- DG2 Lehmann return weights: IS -0.99 / +0.21 / -0.91, VAL -0.37 / -2.07 / -0.75, PRE +0.09 / -0.10 / -0.46
  (all |t| <= 1.30).
So there is no cross-sectional predictability at 1-5 days in either direction in any of three eras; the side choice
does not matter (the reversal mirror is net negative as well).

Feasibility: a daily FX top-bottom book has a per-trade sd of ~60 bp (weekly ~135 bp); LIVE at ~258 trades/yr needs a
net Sharpe of 0.14, i.e. ~8.5 bp net per daily trade, ~43 bp per weekly trade. Observed |mid| <= ~2 bp/day.

C3 correlation (cells net > 0 in both eras, none a candidate): G2m k1 hW 0.00 daily / 0.02 monthly; G3c2 k1 h3
-0.01 / 0.12; G1 k1 hW -0.05 / -0.13.

## Notes for the next round
- The dispersion regime drifts even with a trailing 252-day 67th-percentile cut: high days 18 % IS, 39 % VAL, 31 % PRE.
- XTIUSD's IS daily sd is 374 bp (April 2020); any commodity cross-section in IS is that month. XNG/XPT spreads make
  a 6-commodity book cost 25-55 bp per trade.
- Index long-short pays ~2.6 bp per night in financing markups (two legs) plus 1-3.5 bp spreads at 14:00 UTC for the
  Asian indices: ~9 bp per 1-day and ~16 bp per 3-day trade.
- PRE shows weekly currency reversal (G1 k3 hW momentum mid -15.9 bp, t -2.0, all in 2004-11) that IS/VAL do not.
- Swaps: rates.py's markups need 2026 prices (ref_price over full M1), so fixed markups from round 7 D were used
  (FX 1 %/yr per side; indices r+5.3 % / r-3.9 %; metals 1.0 / 0.5 %; energies -2.5 bp, XNG -4 bp per night).
- Network: FRED short rates 2003-2015 fetched to G/rates_pre/ (cost input for PRE swaps); literature via OpenAlex /
  Semantic Scholar. Raza et al. 2014's abstract was not retrievable; its side is from memory (flagged in the file).

## Files (scratchpad r10/G/)
common.py, engine.py (snapshots, pair tables, stats), g12.py (G1/G2), g3.py (G3), analyse.py (selection, chance,
controls, stresses -> analyse_out.txt), g4_pre.py (PRE + DG PRE -> g4_pre_out.txt), dg.py (DG IS/VAL), g5.py (G5,
DG2), c3corr.py; outputs g12_*.txt, g3_*.txt, *_out.txt.
