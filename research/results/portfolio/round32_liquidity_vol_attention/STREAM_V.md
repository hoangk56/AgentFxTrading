# Round 32, stream V: implied volatility of other assets and option-market shape

Written 2026-10-27 from 18:59 UTC (`date -u`). Hypotheses with their UTC times are in
[HYPOTHESES_V.md](HYPOTHESES_V.md). Batch 1 (180 cells) was declared at 18:51, before any return was computed. Batch
2 (36 cells) was declared at 18:57, after batch 1's numbers were in. HOLD (2025-01..2026-09) stayed closed: every
CBOE series was cut at 2024-12-31 when it was parsed, and every IC or Dukascopy price at ts < 2025-01-01 when it was
loaded. No 2025-26 value was printed or summarised.

## Answer
- **No LIVE or DEMO candidate, and no PREREG_DRAFT.** 216 declared cells across 10 families. The best IS net t is
  **1.57**, so no cell reaches DEMO's IS t >= 2.0.
  - Chance gives more than that. Random-date rules with the same counts, sides and holds have a best-of-180 IS t
    with median 3.20 and 95th percentile 4.20 (the long index legs carry equity drift).
- **No family has a VAL-size power above 1.35. LIVE needs 3.**
  - The best two are SKEW (lagged one day) -> long USTEC for 5 days (power 1.35) and VVIX z > 1 -> long USTEC for 1 day
    (power 1.14).
  - Both are below the arithmetic in HYPOTHESES_V.md, which put the literature's effect sizes at a power of
    ~0.4-0.9.
- **Per-asset variance risk premia do not predict their asset's 1-5 day return with a stable sign.**
  - Gold (GVZ), silver, oil (OVX), Nasdaq (VXN), Dow (VXD) and Russell (RVX) were tested.
  - In IS 2016-21 the continuous index VRP predicts the next 5 days with the **wrong** sign (US30 NW t -3.15, USTEC
    -2.39, US2000 -2.41). In VAL it turns positive (US30 +1.58).
- **Asset-specific implied-vol shocks carry nothing tradeable.** These are the part of the daily IV change that VIX
  does not explain: GVZ, OVX, VXN, VXD, RVX, VXEFA and VXSLV.
  - Gold's declared side (follow a GVZ rise) loses in IS and VAL (-6.6 / -7.1 bp per day) and wins in PRE
    (+4.9 bp). The sign is not stable.
  - VXEFA -> EURUSD flips sign between eras: IS t -2.67, VAL +1.48, PRE -0.56.
- **"Fear priced high -> long US indices" is the 1-day reversal, not a new signal.** These are the VVIX, SKEW,
  VIX9D/VIX and COR1M cells.
  - Positive in VAL, but IS t <= 1.57 with March-April 2020 included.
  - Without March-April 2020, VVIX k1 h1 USTEC reaches IS t 2.73. This is post hoc, and it removes exactly the
    crash in which a "buy when vol-of-vol is high" rule loses.
  - With the prior 1-day and 5-day returns as controls, z(VVIX) adds nothing (USTEC IS t -0.45, ex-2020 +0.30).
    The prior-day return carries the IS effect (coefficient -0.19, t -3.0), and it is ~0 in VAL.
  - Reversal was exhausted in rounds 2, 7 and 11, and round 9 tested buying after VIX > 30.
- **New sources found in the same CDN:** CBOE implied correlation (COR1M/COR3M/COR10D/COR6M/COR1Y, 2006..),
  dispersion DSPX (2014..) and VIXEQ (2014..). The correlation risk premium (Buss, Schoenleber & Vilkov; Pollet &
  Wilson 2010) does not repeat in VAL: IS +48.9 bp (t 1.45), VAL +6.0 (t 0.10) at the best cell.

## Sources (fetch log: scratchpad `r32/V/web/requests.log`, 81 lines: 54 CBOE / robots requests, 15 OpenAlex, 6 Semantic Scholar, rest probes)
| source | history (rows used, <= 2024-12-31) | usable? |
|---|---|---|
| CBOE CDN `cdn.cboe.com/api/global/us_indices/daily_prices/<IDX>_History.csv` (no robots.txt: S3 403; www.cboe.com unreachable) | | |
| GVZ, OVX, VXN, VXD, RVX, VIX3M | 2009-09.. | yes. GVZ / OVX before 2009-09 are not in these files |
| VIX, SKEW, SPX | 1990.. / 1975.. | yes |
| VVIX | 2006-03..; 2006 rows are junk (min 15.7). Unused: IS z windows start 2015 | yes |
| VIX9D | 2011.. | yes |
| VIX6M, VIX1Y | 2008.., 2007.. | downloaded, not used |
| VXTLT | 2004.. (early years likely back-calculated) | yes |
| VXEFA | 2008.. | yes (V7) |
| COR1M, COR3M, COR10D, COR30D, COR90D, COR6M, COR1Y | 2006.. | yes (V5, information) |
| DSPX, VIXEQ | 2014-06.. | information |
| VXSLV, VXGDX, VXFXI | 2011-03..**2022-02** (discontinued) | **no VAL**: information only |
| VIX1D | 2022-05.. | **no IS**: unused |
| VXEEM, VXEWZ, single-stock VXAPL/VXAZN/VXGOG/VXGS/VXIBM | 2011.. | no target in this stream |
| **EVZ** (EUR), EUVIX, JYVIX, BPVIX, VXXLE, TYVIX/VXTYN, SRVIX, VXST, VOLI, SKEW9D, KCJ/ICJ/JCJ | | **403 (not on the CDN)**. No EUR implied vol is free here, so EURUSD had no own-VRP cell |
| Literature | OpenAlex (11 searches + 8 DOI lookups, no mailto) and Semantic Scholar (4 DOIs, 2 searches, both answered 429) | Elsevier abstracts are missing in both. Signs were fixed from the abstracts that came back (Christoffersen & Pan 2018, BTX 2015, Huang et al. 2019) and from the papers' known results (BTZ 2009, An-Ang-Bali-Cakici 2014, Baur 2012, Pollet-Wilson 2010) |

Prices:
- IC M1 mids at 16:30 New York (bid close / ask close of the bar starting 16:30; +1-minute variant at 16:31) for
  XAUUSD, XAGUSD, XTIUSD, XBRUSD, EURUSD, USTEC, US30, US500, and US2000 (bid zbars plus the published 0.34-pt
  spread x1.5).
- Dukascopy PRE: XAU / XAG m1c (2009-15 usable; 2004-09 metals are bid-only) and EURUSD m1 (2004-15).
- PRE cost: IC 2016-17 median spread at the same New York minute (XAU 1.34 bp, XAG 5.6, EURUSD 0.18), plus 0.6 bp
  commission.

## Method (as declared)
- **Timing:**
  - Entry is the 16:30 NY bar on signal day D. CBOE closes are public at 16:15 ET.
  - SKEW is lagged one day.
  - Exit is 16:30 NY on the h-th CBOE trading day after entry, h in {1, 5}.
  - Positions are non-overlapping per symbol.
- **Signals:**
  - z against the 252 prior days.
  - VRP = IV^2 - RV21^2. RV21 is computed from 16:30-NY mids, strictly before D.
  - The IV residual is dIV - beta x dVIX, with beta fitted over the 252 prior days.
  - Thresholds k in {0.5, 1.0, 1.5}, chosen on IS.
- **Costs:** half spread at entry plus half at exit at the actual bar spread. Commission 0.6 bp on EURUSD and metals.
  Swaps per 17:00 NY rollover from `research.swing.rates.swap_frac_at`; oil -2.5 bp a night.
- **Variants:** spread x1.5, both fills +1 minute, all signals lagged one day.
- **Random control:** 200 seeds, same count, same sides and same hold, on random eligible days in the same era.
- **Information:** continuous predictive regressions with Newey-West t.

## Results: best cell per family (IS-picked k), IS 2016-21 / VAL 2022-24
Energies' IS is 2018-21 (IC data) and in practice ~2019-21, after RV and z warm-up. Index IS starts ~2017 for V1
(the RV warm-up on IC data).

| family (cells) | best cell | mid IS / VAL bp | cost bp | net IS (t) / VAL (t) | x1.5 / +1 min / lag 1 day (IS / VAL) | SR per trade IS / VAL | power IS / VAL size | random control IS / VAL | PRE net (t) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 own VRP (42) | RVX -> US2000 long, k0.5 h5 | +49.6 / +21.0 | 16.1 | +33.5 (0.76) / +0.6 (0.01) | +31.9/-0.7; +34.3/+1.1; -6.1/-39.4 | 0.087 / 0.002 | 0.41 / 0.01 | 0.68 / 0.70 | - | none |
| V1 gold (in family) | GVZ -> XAU long, k0.5 h1 | +3.0 / +3.3 | 2.7 | +0.3 (0.05) / +0.5 (0.08) | -0.4/+0.2; +0.2/+0.4; -1.4/+5.6 | | | 0.55 / 0.27 | +3.5 (0.45) | none |
| V2 IV shock (42) | dOVX resid -> short XTI, k0.5 h5 | +138.8 / +6.1 | 25.2 | +113.6 (1.47) / -15.0 (-0.31) | +110/-17; +114/-16; +104/-28 | 0.129 / -0.029 | 0.97 / -0.24 | 0.94 / 0.55 | - | none (ex Mar-Apr 2020 IS +30.1, t 0.65) |
| V3a SKEW lag 1 (18) | -> USTEC long, k1.5 h5 | +56.1 / +77.5 | 17.1 | +39.0 (1.28) / +54.2 (1.78) | +37.6/+53.7; +39.1/+54.4; +15.5/+6.0 | 0.157 / 0.293 | 0.68 / 1.35 | 0.68 / 0.89 | - | none |
| V3b VVIX (18) | -> USTEC long, k1.0 h5 | +78.7 / +66.2 | 17.7 | +61.0 (1.57) / +44.7 (0.71) | +59.3/+44.2; +60.9/+45.1; +38.9/+55.7 | 0.192 / 0.121 | 0.84 / 0.54 | 0.88 / 0.83 | - | none |
| V3b VVIX (h1 cell) | -> USTEC long, k1.0 h1 | +28.0 / +26.4 | 6.2 | +21.8 (1.42) / +21.4 (1.50) | +20.1/+20.9; +22.0/+21.2; +8.7/+14.2 | 0.097 / 0.142 | 0.76 / 1.14 | 0.98 / 0.95 | - | none (reversal; see below) |
| V3c VIX9D/VIX (18) | > 1.00 -> USTEC long, h5 | +47.6 / +73.6 | 18.0 | +29.6 (0.84) / +52.9 (1.03) | +27.9/+52.3; +29.7/+52.7; +16.6/+37.5 | 0.083 / 0.127 | 0.45 / 0.78 | 0.54 / 0.94 | - | none |
| V4a OVX level (18) | -> USTEC long, k0.5 h5 | +40.1 / +31.0 | 18.3 | +21.7 (0.45) / +11.9 (0.20) | | 0.055 / 0.029 | 0.24 / 0.15 | 0.46 / 0.69 | - | none |
| V4b GVZ - VIX (12) | -> XAU long, k0.5 h5 | +19.3 / +25.1 | 5.3 | +14.0 (0.80) / +12.7 (0.61) | +13.4/+12.5; +14.1/+12.5; +16.0/+23.6 | 0.071 / 0.069 | 0.43 / 0.46 | 0.55 / 0.38 | +1.7 (0.07) | none |
| V4c VIX VRP -> EURUSD (6) | k0.5 h5 | +0.7 / -11.1 | 5.4 | -4.7 (-0.40) / -16.2 (-1.26) | | -0.043 / -0.178 | < 0 | 0.40 / 0.34 | +7.1 (0.72) | none |
| V4d VXTLT -> XAU (6) | k0.5 h5 | +19.8 / +34.5 | 6.5 | +13.3 (0.57) / +27.1 (0.76) | | 0.060 / 0.108 | 0.30 / 0.57 | 0.63 / 0.57 | -34.9 (-1.25) | none |
| V5 implied correlation COR1M (18) | -> USTEC long, k0.5 h5 | +66.8 / +24.2 | 17.9 | +48.9 (1.45) / +6.0 (0.10) | +47.3/+5.3; +48.9/+5.8; +48.0/-3.9 | 0.143 / 0.014 | 0.78 / 0.07 | 0.84 / 0.65 | - | none |
| V6a VXN - VXD pair (6) | long USTEC / short US30, k1.5 h1 | +7.8 / -14.7 | 9.2 | -1.4 (-0.17) / -20.2 (-1.17) | | < 0 | < 0 | 0.68 / 0.09 | - | none |
| V6b RVX - VIX pair (6) | long US2000 / short US500, k1.5 h1 | +12.0 / +2.5 | 9.8 | +2.2 (0.23) / -4.7 (-0.48) | | 0.020 / -0.047 | 0.12 / < 0 | 0.97 / 0.66 | - | none |
| V7 dVXEFA resid -> EURUSD (6) | short on z > 1.5, h1 | -2.5 / +0.4 | 1.1 | -3.5 (-0.71) / -0.7 (-0.14) | | < 0 | < 0 | 0.28 / 0.51 | +10.8 (1.80) | none (k1 h5: IS -27.8 t -2.67, VAL +19.1 t +1.48: sign flips) |

Years net > 0 (best cells): V3b USTEC h5 5/6 IS, 2/3 VAL; V3a 4/6, 2/2; V5 5/6, 2/3. At the IS-picked k, 42 of 72
family x target x hold groups have VAL net > 0. That is about what independent noise gives.

### Cells and chance
- **Cells:** 216 graded. Batch 1 has 180: V1 42, V2 42, V3a/b/c 54, V4a 18, V4b 12, V4c 6, V4d 6. Batch 2 has 36:
  V5 18, V6 12, V7 6.
- **Best IS net t:** 1.57 in batch 1 and 1.45 in batch 2.
- **Random-date null over the 180 batch-1 cells:** the best IS t per seed has median 3.20 and 95th percentile 4.20.
  The observed best is below every seed (p 1.00).
- **Information cells (ungraded):** 136 continuous regressions. The largest |NW t| are:
  - V1 index VRP at 5 days in IS: -3.15, -2.41, -2.39. This is the wrong sign, and positive in VAL.
  - V4c VIX VRP -> EURUSD in PRE: +2.61 at 1 day, +1.98 at 5 days. This is the declared side, but the rule cells
    are negative in IS and VAL.
  - Max |t| is about what 136 draws give (~3.1).

### Post-hoc checks (information only, not graded)
- **Without March-April 2020** (the brief's pitfall rule):
  - 10 of 216 cells reach IS t >= 2, and 7 of those have VAL net > 0. The best is VVIX k1 h1 USTEC: IS +29.1 bp
    (t 2.73, n 166), VAL +21.4 (t 1.50). Next are VVIX k1.5 h5 USTEC (t 2.52) and RVX VRP k0.5 h5 US2000 (t 2.50,
    VAL +0.6).
  - The equal-weight VVIX k1 h1 three-index book: IS +13.6 (t 0.85) with 2020, +26.6 (t 2.63) without; VAL +16.0
    (t 1.38).
  - **Not a candidate, for three reasons:**
    - (a) Excluding the crash removes this rule's real risk. A rule that buys when vol-of-vol is high buys into crashes.
    - (b) z(VVIX) adds nothing once the prior 1-day and 5-day returns are controls: USTEC IS t -0.45 (ex-2020
      +0.30), VAL +0.48. The IS effect is the 1-day reversal (r1 coefficient -0.19, t -3.0), which is ~0 in VAL
      (-0.008).
    - (c) Best-of-216 against a chance level of ~3.
- **Oil V2 without March-April 2020:** the best IS cell falls from +113.6 (t 1.47) to +30.1 (t 0.65). The oil IS
  numbers are April-2020 artefacts (round 13's IC glitch list).

## What this says
- Implied vols of gold, oil and the US indices, their premia over realised vol, and the shape of S&P options (SKEW,
  VVIX, VIX9D, implied correlation) do not time the underlying at 1-5 days at a size that clears IC's costs.
- Their literature effects are monthly-to-quarterly. Scaled to 1-5 days they are ~3-30 bp against 30-140 bp
  needed, and the measured effects match that. The per-asset VRP sign even flips between 2016-21 and 2022-24.
- Option prices are public at the close, and the information in them is in the spot price by the next 16:30. This
  is the same lesson as rounds 25-26 (public information is priced before a bot can act), now for option-implied
  information.
- The one recurring positive pattern (buy US indices when fear is priced high) is the known 1-day reversal, plus
  VAL-era equity drift.

## Directions that need the user (with a one-line value)
- **EUR / JPY implied vol history:** CME CVOL (EUVL, JPVL) needs a CME DataMine account; CBOE's EVZ is off the CDN.
  Value low, ~1-2 % LIVE: the FX VRP literature (Della Corte, Ramadorai & Sarno 2016) is cross-sectional and monthly.
- **MOVE / Treasury implied vol** (ICE, paid; Yahoo unreachable): VXTLT here already shows nothing for gold. Value
  ~0-1 %.
- **Options on IC symbols at the strike level** (OI / gamma by strike for GLD / USO / QQQ, paid: ORATS, CBOE
  DataShop): round 4's GEX split vol, not direction. Value ~1-2 %.
- **Deribit DVOL (BTC / ETH implied vol):** public API, but it starts 2021-03, so no IS 2016-21. It would be a
  new-era (DISCOVERY / TEST) rule only, which the current bars don't allow. Value ~1 %.

## Files
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/V/`:
- **scripts/:**
  - fetch_cboe.py (CDN fetcher, logs every request)
  - coverage.py (rows per year, pre-2025 only)
  - build_panel.py (16:30 / 16:31 NY panel)
  - common.py (loaders, signals, costs, swaps, stats)
  - run_cells.py (batch 1 + information regressions + null)
  - run_batch2.py
  - posthoc.py
  - ex2020.py
  - show_oa.py
- **out/:**
  - cells.tsv, cells_b2.tsv (every cell with every variant)
  - info.tsv
  - null.txt, null_t.npy
  - run_cells.log, run_batch2.log, posthoc.log, ex2020.log
  - panel.npz
- **web/:**
  - cboe/*.csv (raw downloads; 2025-26 rows dropped at parse)
  - lit/ (OpenAlex / Semantic Scholar JSON)
  - requests.log

C3 correlation: no surviving rule, so none was computed.
