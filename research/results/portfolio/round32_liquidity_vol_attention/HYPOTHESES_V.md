# Round 32, stream V: hypotheses (implied volatility of other assets, option-market shape)

Written 2026-10-27 18:51 UTC (`date -u`), **before any return was computed**. At this time the CBOE files are
downloaded and their row counts per year are known (no value was printed or summarised). No IC, Dukascopy or CBOE
series has been joined to a return. HOLD 2025-01-01..2026-09-24 stays closed: every CBOE series is cut at
2024-12-31 when it is parsed, and every price at ts < 2025-01-01 when it is loaded.

## What is already done (not redone here)
- Round 4: VIX / VIX3M term structure (backwardation, US indices, ~4-day hold: too few events) and a daily feature
  scan in which OVX and GVZ entered as level / 1-day / 5-day change z, trade sign(z) when |z| > 1, all 26 symbols,
  1 and 3 days (1,867 tests, nothing). V2 below is a different construction (the part of the asset's IV change that
  VIX does not explain, with a side from the spot-vol sign), V1 a different quantity (implied minus realised).
  V4a (OVX level -> US indices) overlaps round 4's scan; it is kept because the side and horizon now come from a
  paper (Christoffersen & Pan 2018), and it is marked as an overlap.
- Round 9: the S&P 500 variance risk premium (VIX vs realised), put-writing and its timing overlays, S&P 500 after
  VIX > 30. Not redone: no rule here trades SPX options or uses VIX level alone. V4c uses the S&P VRP only as a
  predictor of EURUSD (a different target).

## Sources (fetched 2026-10-27 18:45-18:48 UTC; log in scratchpad `r32/V/web/requests.log`)
`https://cdn.cboe.com/api/global/us_indices/daily_prices/<IDX>_History.csv` (no robots.txt on the CDN: S3 answers
403; www.cboe.com is unreachable from this Mac, as in round 9).

| index | what | history (rows <= 2024) | usable for |
|---|---|---|---|
| GVZ | 30-day implied vol of GLD options | 2009-09-18.. | XAU, XAG: PRE 2010-09..2015 (after a 252-day warm-up), IS, VAL |
| OVX | 30-day implied vol of USO options | 2009-09-18.. | XTI, XBR (IC energies from 2018: IS 2018-21) |
| VXN / VXD / RVX | Nasdaq-100 / DJIA / Russell 2000 implied vol | 2009.. | USTEC / US30 / US2000 (no index PRE) |
| VIX, VIX9D (2011..), VIX3M, VIX6M, VIX1Y | S&P 500 implied vol term structure | 1990 / 2011 / 2009 | V2 (the VIX change), V3c, V4 |
| VVIX | implied vol of VIX | 2006-03..; early rows look unclean (checked at load) | V3b |
| SKEW | CBOE S&P 500 risk-neutral skew index | 1990.. | V3a |
| VXTLT | implied vol of TLT (20y+ Treasury ETF) | 2004.. | V4d |
| SPX | S&P 500 close | 1975.. | realised vol for the VIX VRP (V4c) |
| VXSLV, VXGDX, VXFXI | silver ETF, gold miners, China ETF vol | 2011-03..2022-02 (discontinued) | **no VAL**: information only |
| VIX1D | 1-day S&P implied vol | 2022-05.. | **no IS**: not usable |
| VXEEM, VXEWZ, VXEFA, VIXEQ, single-stock VX* | EM / Brazil / EAFE / equity-name vols | 2008-2014.. | no target in this stream's list; not used |
| **EVZ** (EUR vol), EUVIX, JYVIX, BPVIX, VXXLE, TYVIX / VXTYN, SRVIX | | **403 (not on the CDN)** | **not usable**: no EUR implied vol free here, so no EURUSD own-VRP cell |

## Publication lag and clocks (fixed before any return)
- CBOE closes for date D are public at 16:15 New York time on D (VIX-family closes are the 16:15 ET values; GLD/USO
  options close 16:00-16:15). **Entry: the M1 bar starting 16:30 New York on D** (bid close / ask close of that bar).
  +1 minute variant: the bar starting 16:31.
- **SKEW is used with a one-day lag** (signal of D, entry 16:30 NY on the next trading day): it is not certain that
  its daily value was public by 16:15 in every year. Every cell that passes is also re-run with all signals lagged one
  day.
- Exit: the bar starting 16:30 NY on the h-th CBOE trading date after the entry date (h = 1 or 5). If IC has no bar at
  16:30, take the last bar in 16:00-16:30 NY; if none, the trade is dropped (entry or exit day).
- Trading days = dates present in the CBOE file of the signal. Non-overlapping per symbol: no new entry while a
  position on that symbol is open (respects one bot <= 3 positions; one symbol per bot).

## Definitions
- Mid = (bid close + ask close) / 2 at the bar. RV21_D = 100 x sqrt(252 / 21 x sum of the last 21 squared log
  returns of the 16:30-NY mids up to D) (vol points). For the VIX VRP (V4c), RV21 from CBOE SPX closes.
- VRP_D = IV_D^2 - RV21_D^2. Pairing: GVZ <-> XAUUSD (also for XAGUSD), OVX <-> XTIUSD (also XBRUSD), VXN <-> USTEC,
  VXD <-> US30, RVX <-> US2000, VIX <-> SPX.
- z of any signal x: (x_D - mean(x over the 252 trading days before D)) / sd(same window). Past-only.
- IV residual (V2): e_D = dIV_D - beta_D x dVIX_D, d = 1-day change, beta_D = OLS slope of dIV on dVIX over the 252
  days before D; z of e as above.
- Thresholds k in {0.5, 1.0, 1.5} (for V3c the ratio VIX9D / VIX > {1.00, 1.05, 1.10}): chosen on IS only.

## Costs, fills, statistics (round 13's brief, unchanged)
- Long buys at the ask, sells at the bid: cost = half the actual spread at entry + half at exit (ca - c of the bar).
  Commission 0.6 bp round trip for EURUSD, XAU, XAG; 0 for indices and energies. US2000 (bid-only bars): IC's
  published spread 0.34 pt x 1.5 (after the cash close).
- Swaps per 17:00 NY rollover: FX / metals / US30 / USTEC via `research.swing.rates.swap_frac_at` (US2000 uses
  US30's model), triple day from `research.specs`; XTI / XBR -2.5 bp per night on either side.
- PRE (Dukascopy XAU / XAG m1c, EURUSD m1): IC 2016-17 median spread at the same New York minute + 0.6 bp.
- Variants: spread x1.5; both fills +1 minute; all signals lagged one day.
- t: per trade (trades on one symbol do not overlap); pooled books cluster by entry date. Per year net.
- Random-entry control: >= 200 seeds, same count per era, same side, same hold, entry dates drawn from the symbol's
  eligible days in the same era, same costs; report the share of seeds the rule beats.
- Information screen (not graded): predictive regression of the h-day forward mid return (in sd units) on the
  continuous z, Newey-West t with h-1 lags, IS / VAL / PRE, for every signal x target pair.

## Power arithmetic (before building)
Frontier (round 10 STREAM_D d0): 1-day sd XAU 84 bp, XAG 152, XBR 239, XTI 345 (2020-inflated; ~230 ex-2020),
EURUSD 42.6, US30 94.6, USTEC 110.5, US2000 ~130 (est.). 5-day sd ~ x sqrt(5).
LIVE needs power = per-trade net Sharpe x sqrt(HOLD trades) >= 3, i.e. an annualised Sharpe >= 3 / sqrt(1.73) =
2.3 for any single always-or-often-in rule, whatever the horizon. A z > 1 trigger fires on ~16 % of days (~40 a
year); non-overlapping 5-day holds give ~20-25 trades a year.

| rule shape | trades / yr | HOLD trades | per-trade Sharpe needed | net needed per trade |
|---|---|---|---|---|
| z > 1, 1-day hold | ~40 | ~69 | 0.36 | XAU 30 bp, XAG 55, US30 34, USTEC 40, US2000 47, EURUSD 15, XTI ~83 |
| z > 1, 5-day hold | ~22 | ~38 | 0.49 | XAU 92 bp, US30 104, USTEC 121, US2000 142, EURUSD 47, XTI ~250 |
| z > 0.5, 5-day hold | ~35 | ~60 | 0.39 | XAU 73 bp, US30 82, USTEC 96 |

What the literature implies: Bollerslev, Tauchen & Zhou (2009) / Bollerslev, Todorov & Xu (2015, JFE, "Tail risk
premia and return predictability"): a 1-sd move in the S&P VRP shifts the expected market return by roughly
0.4-0.8 % a month (monthly R^2 ~1-2 %, quarterly ~7 %), i.e. ~2-4 bp a day or ~10-20 bp per 5 days per sd. At the
mean z of a z > 1 bucket (~1.5): 1-day ~3-6 bp, 5-day ~15-30 bp, against 30-40 / 90-120 bp needed: **expected power
~0.4-0.9, LIVE prior < 2 %**. DEMO needs IS t >= 2: expected IS t at those sizes ~0.7 (1 day, n ~240) to ~1.2
(5 days, n ~130): **DEMO prior ~10 %**. Christoffersen & Pan (2018, JBF, "Oil volatility risk and expected stock
returns"): after 2004-05, oil volatility is "a strong predictor of returns ... of the overall stock market" (monthly
horizon); assume the same magnitude. An, Ang, Bali & Cakici (2014, JF): single-stock IV increases predict returns
over the next month (~1 %/month quintile spread); for liquid macro assets expect far less. No paper found reports a
1-5 day effect of the size needed. Searches: OpenAlex (8 queries) and Semantic Scholar (4 DOIs), logged.

## Hypotheses (side fixed from the mechanism / source; cells counted)

### V1 Own-asset variance risk premium -> the asset's return (risk-premium side: long when the premium is high)
Mechanism: a high IV - RV gap is a high price of insurance; holders of the underlying are paid for bearing that risk
(BTZ 2009, BTX 2015 for the S&P; Prokopczuk, Symeonidis & Wese Simen 2017 show commodity VRPs exist; for gold the
insured risk is upside, so a high premium is also hedging demand ahead of a rally: same side).
Rule: long when z(VRP) > k, hold h. Targets XAUUSD (GVZ), XAGUSD (GVZ), XTIUSD, XBRUSD (OVX), USTEC (VXN), US30
(VXD), US2000 (RVX). Cells 7 x 3 k x 2 h = **42**. Short leg (z < -k) reported as information only.

### V2 Asset-specific implied-vol shock (the part of dIV that VIX does not explain)
Mechanism: option demand that leads the spot (An, Ang, Bali & Cakici 2014: IV increases predict the underlying's
return in the direction of the asset's usual spot-vol sign). Gold's spot-vol relation is positive (Baur 2012,
"asymmetric volatility in the gold market"): a GVZ rise beyond VIX = call demand -> **long** gold / silver. Oil and
equity indices have a negative spot-vol relation: an OVX / VXN / VXD / RVX rise beyond VIX = put demand -> **short**.
Rule: trade when |z(e)| > k with side = s x sign(z), s = +1 metals, -1 oil and indices; hold h.
Targets as V1. Cells 7 x 3 x 2 = **42**.

### V3 Option-market shape for US indices (crash-hedging demand; risk-premium side: long when fear is priced high)
- V3a SKEW (lagged one day) z > k -> long (BTX 2015: the left-tail premium carries the predictability).
- V3b VVIX z > k -> long (vol-of-vol risk is priced with a negative price of risk, Huang, Schlag, Shaliastovich &
  Thimme 2019 JFQA; the spot side by the same premium argument; low prior).
- V3c VIX9D / VIX > c, c in {1.00, 1.05, 1.10} -> long (acute short-dated fear; a short-end analogue of round 4's
  VIX / VIX3M > 1, marked as a near-duplicate mechanism).
Targets USTEC, US30, US2000. Cells 3 x 3 x 3 x 2 = **54**.

### V4 Cross-asset vol spreads
- V4a OVX level z > k -> long USTEC, US30, US2000 (Christoffersen & Pan 2018; funding-constraint channel). Overlaps
  round 4's scan (see above). 3 x 3 x 2 = **18**.
- V4b (GVZ - VIX) z > k -> long XAUUSD, XAGUSD (gold-specific fear while equities are calm = safe-haven demand
  building). 2 x 3 x 2 = **12**.
- V4c VIX VRP (VIX^2 - RV21(SPX)^2) z > k -> long EURUSD (a high global VRP pays the holder of the non-haven against
  the dollar; Aloosh 2012/2016 "Global variance risk premium and forex return predictability" reports predictability,
  side not verified from the text: low prior). 1 x 3 x 2 = **6**. PRE 2005-15 on Dukascopy EURUSD.
- V4d VXTLT z > k -> long XAUUSD (rate-uncertainty hedging demand for gold; low prior). 1 x 3 x 2 = **6**.

**Total declared rule cells: 180.** Chance benchmark: the best of 180 one-sided t's (correlated cells) is ~2.5-2.8
under the null; a permutation null (sign-flip by date blocks, shared by all cells) is reported.

### Information only (not graded)
VXSLV -> XAGUSD V1 / V2 on IS only (series ends 2022-02); continuous predictive regressions for every pair.

## Batch 2 (written 2026-10-27 18:57 UTC, after batch 1's 180 cells were computed; batch 1's best IS net t was
1.57, none met DEMO). These are new signals, not re-cuts of batch 1; sides fixed here from the source.

New source found in the same CDN: **CBOE implied correlation indices** COR1M (30-day), COR3M, COR10D, COR6M, COR1Y
(2006-01..), and DSPX (S&P 500 dispersion, 2014-06..), VIXEQ (average constituent implied vol, 2014-06..). KCJ / ICJ /
JCJ (the old implied-correlation tickers) answer 403. VXEFA (MSCI EAFE ETF implied vol, 2008..) was already on disk.

### V5 Implied correlation (the correlation risk premium) -> long US indices when high
Mechanism: index options price diversification breaking down; a high implied correlation is a high price of
correlation insurance and is paid to holders of the index (Driessen, Maenhout & Vilkov 2009 JF; Buss, Schoenleber &
Vilkov, "Expected stock returns and the correlation risk premium" SSRN 3114063 / "Implied correlation and expected
returns"; Pollet & Wilson 2010 JFE: average correlation predicts the market with a positive sign).
Rule: long when z(COR1M) > k, k in {0.5, 1.0, 1.5}, h in {1, 5}; targets USTEC, US30, US2000. **18 cells.**
Information: COR3M and DSPX (z) with the same rule, not graded.

### V6 Relative implied vol across US indices -> index pair (risk-premium side: the index whose risk is priced
higher relative to the other earns more)
- V6a z(VXN - VXD) > k -> long USTEC, short US30 (equal notional, h days).
- V6b z(RVX - VIX) > k -> long US2000, short US500.
Both legs at their own spreads, swaps, commissions; net reported in bp of one leg's notional. **2 x 3 x 2 = 12 cells.**

### V7 Europe-specific equity option demand -> EURUSD
Mechanism as V2 (option demand leads the spot): the part of the daily VXEFA change that VIX does not explain is
non-US (mostly European) put demand -> **short** EURUSD when z > k, long when z < -k (side = -sign(z)); k in {0.5,
1.0, 1.5}, h in {1, 5}. PRE 2009-15 on Dukascopy EURUSD. **6 cells.**

### Information only
VXSLV (silver ETF vol, 2011-03..2022-02, no VAL): V1 / V2 on XAGUSD in IS. Batch 2 total graded cells: **36**
(grand total 216).
