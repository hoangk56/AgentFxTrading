# Round 45, stream X: hypotheses (one declared combined model over the daily non-price features of rounds 37-44)

Written 2026-10-30 06:32 UTC (`date -u`), **before any return, fit or forecast was computed in this stream**. What
existed when this file was written: the per-source series rebuilt from the round 37-44 scratchpads and mapped onto
each symbol's decision clock (scripts `feats.py`, `mapfeat.py`; outputs `out/series.pkl`, `out/featmat.npz`,
`out/features_meta.json` with coverage by year), and the list of entry days with a bar at the clock (`out/grid.npz`).
No price change between two clocks, no volatility and no feature-return join had been computed. Scratchpad:
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r45/X/`.

HOLD (2025-01-01..2026-09-24) stays closed: every source row dated after 2024-12-31 is dropped at load (asserts in
`feats.py`; CFTC as-of <= 2024-12-24 because the 12-31 report is released in 2025); IC M1 ts < 1735689600000 and
US2000 zbars < 20250101 at load (`prices.py`, asserted). Nothing from 2025+ is loaded, so nothing can be printed.

Disclosure about prior knowledge: I read the round 37-44 reports, which graded each source alone on IS and VAL. To keep
that knowledge out of the model, (a) every daily or weekly source in those scratchpads that is still publishable forward
is included, whatever its earlier result; (b) each source enters in its simplest aggregate form (the stream's level /
z form on the stream's own mapping), never in the form of its best earlier cell; (c) the sides are the streams'
declared sides (literature / mechanism), and the ridge may flip a sign only through the IS fit. No feature, form,
symbol, penalty or threshold below is chosen by IS or VAL numbers.

## Book and clocks
12 symbols, one bot each, one position at a time, held one weekday (<= 4 calendar days, <= 3 positions per bot holds):
| symbols | decision clock (entry) | exit |
|---|---|---|
| US500, USTEC, US2000 | 10:00 New York (DST-aware) | same clock, next weekday with a bar |
| DE40 | 10:00 Frankfurt | same |
| JP225 | 10:00 Tokyo (01:00 UTC) | same |
| HK50 | 10:30 Hong Kong (02:30 UTC) | same |
| EURUSD, USDJPY, AUDUSD, XAUUSD, XTIUSD, BTCUSD | 12:00 UTC | same |
Grid: weekdays 2016-01-04..2024-12-31; a day is eligible when the bar starting at the clock exists (<= 10 min late) and
an exit day exists within 4 calendar days. XTIUSD starts 2018, BTCUSD 2017-08 (IC cache).

## Features (26 families; one coefficient per family shared by its legs; x = side x clip(z, -3, 3), 0 when missing)
A value is used at a decision clock T only if its public time is <= T - 1 min and it is not older than the stale cap
(daily 4 calendar days, weekly 10 days; weather 12 h; funding / BoJ 1 day). z = trailing z on the source's own
observation sequence (current value excluded) unless stated.

| # | family | source (scratchpad) | series and z | public time used | legs: symbol (declared side) | side source |
|---|---|---|---|---|---|---|
| 1 | FINRA_SVR | r38/S `out/finra.npz` (FINRA Reg SHO daily, FNSQ+FNYX to 2018-07, CNMS after) | ETF short-volume ratio, z vs prior 60 files (>= 50) | D 18:30 ET (FINRA ~18:00 ET) | SPY->US500, QQQ->USTEC, IWM->US2000, EWJ->JP225, EWG->DE40, EWH->HK50, EWA->AUDUSD, GLD->XAU, USO->XTI, FXE->EURUSD (all -1); FXY->USDJPY (+1) | DLW informed shorting (round 38 S1) |
| 2 | ETF_FLOW | r38/S `out/so_*.npz` (SSGA / iShares shares outstanding) | daily creation rate (SPY+IVV dollar flow; IWM; EWJ share change), z vs prior 60 rows | D+1 13:00 UTC (round 38 rule) | US500, US2000, JP225 (-1) | BDR reversal (round 38 S3) |
| 3 | FUNDING | r37/F `web/binance_funding_BTCUSDT.json` (from 2019-09-10), Bybit inverse BTCUSD before | mean of the last 3 funding stamps, z vs prior 270 stamps (>= 180) | at the stamp (00/08/16 UTC) | BTCUSD (-1) | payers close / crowded longs (round 37 F) |
| 4 | CONNECT_SB | r37/N `web/em/mdh_002/004` (Eastmoney southbound SH+SZ net buy) | z vs prior 60 days (>= 40) | D 09:30 UTC (round 37 N rule) | HK50 (+1) | follow the mainland buyer |
| 5 | GD_TONE_IDX | r40/G `out/signals.npz` (GDELT 1.0 daily, blocks per weekday) | z_TONE_<geo>_60 (stream's block z) | weekday E 08:00 UTC (files D+1 07:00-07:30) | US tone->US500, USTEC, US2000; JA->JP225; CH+HK->HK50; GM->DE40 (+1) | Tetlock continuation (round 40 G1) |
| 6 | GD_TONE_FX | same | z_RELTONE_<pair>_60 (base minus quote tone) | same | EURUSD, USDJPY, AUDUSD (+1) | same |
| 7 | GD_WORLD | same | z_TONE_WORLD_60 | same | BTCUSD (+1), XAUUSD (-1) | round 40 G (world tone) |
| 8 | GD_CONF | same | z_CONF_PROD_60 (quad-4 share in producer countries) | same | XTIUSD (+1), XAUUSD (+1) | round 40 G2 producer conflict |
| 9 | CNM_LEV | r40/C `web/em_lshj` (SSE+SZSE RZYE) | 1-day financing-balance growth, z vs prior 60 days | next CN trading day 01:30 UTC | HK50, AUDUSD, JP225 (+1), XAUUSD (-1) | deleveraging continuation (round 40 C1, risk map) |
| 10 | CNM_SHORT | same (RQJMG / RQYL) | net short sales per share short, z60 | same | HK50, AUDUSD, JP225 (-1), XAUUSD (+1) | informed short sellers (round 40 C3) |
| 11-13 | AUC_US, AUC_JP, AUC_DE | r41/A `out/auctions.json` | log1p(DV01 resulting in (T, T+5 d] / median) - log1p(DV01 resulting in (T-3 d, T] / median); DV01 = previous same-tenor amount x duration; median of the previous 50 auction days; z250 over the symbol's decision days | result times US 13:00 ET, JP 12:35 JST, DE 11:35 Berlin; amounts known from the previous auction, dates scheduled | US: USDJPY +1, EURUSD -1, XAU -1, US500 / USTEC / US2000 -1; JP: USDJPY -1, JP225 -1; DE: EURUSD +1, DE40 -1 | LYZ concession before, reversal after (round 41 F1 CYC) |
| 14 | EDG_SUPPLY | r41/B `out/z_ALLEQ.npy` (EDGAR IPO+shelf+secondary counts) | stream's trailing z (weekday-adjusted) | D 22:00 ET (Reg S-T acceptance limit) | US500, USTEC, US2000 (-1) | supply pressure (round 41 B) |
| 15 | EDG_BUYBACK | r41/B `out/z_BUY.npy` (SC TO-I) | same | same | same (+1) | same |
| 16 | INSIDER | r44/I `out/series.npz` z_ALL_cnt_W | weekly net purchase ratio (all officers / directors, counts), stream's z250 | filing day 22:00 ET | US500, USTEC, US2000 (+1) | insiders informed (round 44 I) |
| 17 | EARN | r42/E `out/ea_8k202.csv` + `company_list.csv` | sum of 13F weights (previous year-end list) of top-40 8-K 2.02 releases accepted since the symbol's previous decision clock; z250 over decision days | EDGAR acceptance time (UTC) | US500, USTEC, US2000 (+1) | announcement premium (round 42 E F2) |
| 18 | BOJ_OTC | r42/J `out/ops.json` | per op offer-to-cover, z vs previous 20 ops of the bucket (>= 10); day mean; fixed-rate ops excluded | op day 05:30 UTC (14:30 JST, round 42 J rule); stale 1 day | USDJPY (-1), JP225 (-1) | eager dealers -> JPY up (round 42 J F1) |
| 19 | WX_SUN | r43/M `out/cover.json` (NOAA ISD morning 06-08 local) | cover minus 2004-15 ISO-week climatology, z250 | local 09:00 same day | NY->US500, USTEC, US2000; FRA->DE40; TYO->JP225; HKG->HK50 (cloudy -> short: -1 on cover) | Saunders / Hirshleifer-Shumway |
| 20 | WX_WIND | r43/M `out/wind.json` | same construction | same | same legs (-1 on wind) | Shu & Hung |
| 21 | WX_TEMP | r43/M `out/temp.json` | same construction | same | same legs (-1 on temperature) | Cao & Wei |
| 22 | WX_HAZE | r43/M `out/haze.json` | mean of Beijing + Shanghai haze, minus 2010-15 monthly climatology, z250 | 09:00 HKT | HK50 (-1) | round 43 P |
| 23 | TFF_LEV | r44/T `out/tff.json` (HF mirror of CFTC TFF; GOLD / WTI disaggregated managed money) | leveraged-fund net / OI, z vs prior 52 reports (>= 40) | Friday 15:30 ET after the Tuesday as-of; week with a US federal holiday -> Monday 15:30 ET; shutdown as-of 2013-10-01..11-19 and 2018-12-25..2019-03-05 dropped | EUR->EURUSD, JPY->USDJPY, AUD->AUDUSD, ES->US500, NQ->USTEC, RTY->US2000, NKY->JP225, GOLD->XAU, WTI->XTI; side -1 x contract sign (JPY sign -1) | crowding reversal (round 44 T) |
| 24 | TFF_AMCHG | same (financial legs) | weekly change of asset-manager net / OI, z52 | same | EUR, JPY, AUD, ES, NQ, RTY, NKY legs; side +1 x sign | with asset managers (round 44 T) |
| 25 | COT_NR | r39/D `out/cot_nonrep.json` (CFTC legacy, non-reportable) | small-trader net / OI, z52 | same rule | the 9 legs of TFF_LEV + BTC->BTCUSD; side -1 x sign | small traders wrong (round 39 D) |
| 26 | RNG52 | IC prices (decision-clock mids) | position in the range of the previous 250 decision mids plus the current pre-clock mid, minus 0.5; z250 | the bar before the clock | all 12 symbols (+1) | record-level continuation (round 37 A) |

Excluded before any return, by a rule fixed here (not by results):
- Event sources with fewer than ~20 events a year on the book's symbols, which a daily linear model cannot weigh:
  SHFE / SGE margin changes (round 37 M, ~5 a year), Atlantic storms (round 38 H, ~2-3), sovereign ratings (round 43 R),
  football losses (round 43 M F). Fresh record breaks (round 37 A) enter as the continuous RNG52 instead.
- Northbound Stock Connect net buy (round 37 N): not published since 2024-08-19, so a model using it cannot run forward.
- Other forms of the same sources (FINRA all-tape / heavyweight / creation-delay / Rule 201 forms, GDELT attention /
  dyads / protests, other insider universes, F3 auction result surprises (priced within 15 min), heavyweight
  after-hours reactions (prices, intraday)): one form per source, as stated above.
- Nothing vanished: every file named above is on disk (no new download in this stream).

## Model (fixed in full)
- Rows: (symbol s, eligible weekday d) with sigma available. Target y = clip(r / sigma, -4, 4), r = mid log return
  (bp) from the entry fill to the exit fill (the closes of the bars starting at the two clocks), sigma = sd of the
  symbol's previous 60 clock-to-clock mid returns that ended at or before the decision (>= 40).
- Pooled ridge, no intercept, 26 coefficients: beta = (X'X + lambda I)^-1 X'y with **lambda = 0.1 x N_fit** (rows in
  the fit).
- Forecast f = x . beta (sigma units). **Trade sign(f) when |f| >= tau_s, tau_s = 0.5 x RMS of the fitted values of
  symbol s in the fit window**; hold to the next clock. Size: one risk unit, P&L in R = net bp / sigma (the lot is
  scaled by 1 / sigma; bp per trade also reported).
- **IS walk-forward**: for each year y = 2017..2021, fit on rows with entry >= 2016-01-01 and exit < y-01-01, predict
  year y (2016 rows are fit-only). **VAL 2022-2024**: one fit on all 2016-2021 rows (beta and tau frozen), no refit.
- Costs (the rounds' IC model): buy at the ask close / sell at the bid close of the bar starting at each clock; FX
  (EURUSD, USDJPY, AUDUSD) and XAUUSD +0.6 bp commission round trip; US2000 bid + 0.34 pt fixed spread; swap =
  `swap_frac_at(sym, side, entry)` x `rollovers(entry, exit, triple)` (triple from research/specs.py SWAPS, else
  Wednesday for FX / metals and Friday for indices, energies, BTC; US2000 uses US500's swap). Stresses: spread x1.5;
  both legs 1 minute later.

## Evaluation (all declared now)
- Net mean R per trade; t on the daily book (sum of R of the trades entered that weekday, day-clustered); years
  positive; per-trade Sharpe; mid (pre-cost) numbers alongside; per-symbol and per-family lines as information.
- **Shuffled-feature null**: 500 draws; in each draw every family's whole feature block (12 symbols x weekday grid, with
  its availability) is circularly shifted along the weekday axis by its own uniform offset in [250, n - 250] (keeps each
  feature's autocorrelation and cross-symbol structure, breaks its alignment with returns and with the other families);
  the full pipeline (5 walk-forward fits + the VAL fit + thresholds) is rerun. p = share of draws with net t >= the
  observed one, for IS walk-forward, VAL, and IS+VAL. Secondary: 200 draws with an i.i.d. permutation of weekdays per
  family. If the individual effects are noise, the observed t sits inside this null; that will be said.
- **Random-entry control**: 500 seeds per era; per symbol the same number of trades on random eligible days of the era,
  long with the model's long share on that symbol; share of seeds whose mean net R per trade is below the model's.
- **Power at HOLD size**: daily-book net Sharpe x sqrt(450 HOLD weekdays) and per-trade Sharpe x sqrt(VAL trades a
  year x 1.73).
- Daily correlation with C3 (`research/results/portfolio/trades_C3_gotobi_jpy_basket.csv`) if anything survives.
- Information only, not eligible: (i) the in-sample fit 2016-21 (optimistic); (ii) an equal-weight declared-side vote
  f_vote = sum_k x_k / sqrt(number of available families), trade sign when |f_vote| >= 1.0, same holds and costs, IS and
  VAL; (iii) the threshold-0 version of the ridge (trade every row).

## Power arithmetic (before any return)
- LIVE needs HOLD power >= 3: with ~450 HOLD weekdays the daily book needs a net Sharpe >= 0.141 per day (~2.2 a year).
  DEMO needs IS walk-forward t >= 2 over 2017-21 (~1,300 days): daily Sharpe >= 0.055.
- Cost per trade in R is small: ~1-2 bp against a 1-day sd of ~45 bp (FX) to ~100 bp (indices), ~5 bp against
  ~200 bp (XTI), ~10 bp against ~350 bp (BTC): 0.01-0.03 R. So a per-trade gross edge of ~0.04 R with ~6 trades a day
  of correlation ~0.2 would give a daily Sharpe of ~0.07-0.08 (DEMO numbers possible, LIVE not); LIVE needs ~0.07 R per
  trade net, i.e. a forecast-return correlation of ~0.08-0.1 on the traded rows. Rounds 37-44 measured ~0.01-0.05 per
  source at mid, much of it unstable between eras: the prior expectation is the null.

## Bars
DEMO: IS walk-forward net t >= 2.0, VAL net > 0, random control >= 90 %, positive at x1.5 spread and +1 minute in IS
and VAL. LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 of the 8 years positive, random >= 95 %, HOLD power >= 3. Declared in
addition for this stream: a PREREG_DRAFT is written only if the shuffled-feature null p <= 0.05 on IS walk-forward as
well. Nothing is changed after numbers; amendments only for mechanical bugs, timestamped, before the affected returns.
