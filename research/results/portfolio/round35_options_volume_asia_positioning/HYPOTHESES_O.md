# Round 35, stream O: hypotheses (listed-option volume, put/call)

Declared 2026-10-28 01:33 UTC (`date -u` 01:32:09 just before writing), **before any return was computed**. Nothing
below has been joined to a price. HOLD 2025-01-01..2026-09-24 stays closed: every series is requested or cut at
2024-12-31, every IC load at ts < 1735689600000.

## Sources found (probes 01:25-01:31 UTC, logged in scratchpad `r35/O/web/requests.log`)
- **OCC volume query** (`marketdata.theocc.com/volume-query`, no robots.txt: 404). Daily volume by underlying, call /
  put, account type (C customer, F firm, M market maker) and exchange: exactly what the brief wanted, **but the server
  refuses any report date more than 2 years back** ("Report date cannot be prior to 2 years"; monthly `reportType=M`
  the same). Today that means 2024-10-28 onward: ~2 months of pre-HOLD data, the rest is HOLD. **Unusable** for IS /
  VAL. Per-underlying GLD / SLV / USO / FXE / FXY volume, the O/S ratio per ETF and the customer / firm split cannot be
  built from free data here. www.theocc.com sits behind a Cloudflare challenge (not touched further).
- **OCC daily-volume-statistics** (`marketdata.theocc.com/daily-volume-statistics?reportDate=YYYYMM01&format=csv`):
  daily total cleared contracts, split Equity / Index-Others / Futures, no call / put split, no underlying. Available
  from at least 2008-01 (2004-01 "Report is not available"); download 2005-2024 running.
- **CBOE put/call archive** (cdn.cboe.com/resources/options/volume_and_call_put_ratios/*.csv, round 4): total, equity,
  index, ETP, SPX, VIX call / put volumes, 2006-11-01 (SPX 2010-07-06, VIX 2006-02) .. **2019-10-04**.
- **CBOE daily market statistics JSON** (cdn.cboe.com/data/us/options/market_statistics/daily/YYYY-MM-DD_daily_options;
  CDN has no robots.txt, S3 403): same classes (total, index, ETP, equity, VIX, SPX+SPXW, OEX, MSCI) with call / put
  volume **and open interest**, from **2019-10-07** (10-03 / 10-04 are 403). It joins the archive with a 1-day gap.
  This is the replacement the brief asked for: CBOE put/call by class 2006-11..2024-12 continuous.
  - Caveats: the JSON levels look lower than the archive's (total ~3.0-4.1 M vs 4.5-5.0 M on adjacent days): scope may
    differ (one Cboe options exchange vs all). Ratios are less affected than levels; every signal is a z against the
    past 252 days, and a sub-check uses IS 2016-01..2019-09 (archive only).
  - Point in time: Last-Modified of 2024-12 files is D+1 02:27-03:47 UTC (posted ~21:30-23:00 ET on D). Files up to
    2024-08 were all rewritten 2024-08-12/13 (restated; preliminary vs cleared volume differences likely small). The
    archive says post-2012 volumes are preliminary reported volume.
- **ISE ISEE** (opening-long customer calls / puts: the only free-in-principle Pan-Poteshman-type series): no free
  history reachable (nasdaqtrader "Page Not Available", iseoptions.com 404; ISEE Select is a subscription). Unusable.

**What the free data can and cannot show (Pan & Poteshman 2006).** Their informative put/call uses *open-buy* volume by
non-market-makers. CBOE / OCC free totals mix opening and closing, buys and sells, customers and dealers. So the free
P/C cannot test "informed flow"; it can only test the *sentiment / contrarian* reading of the aggregate ratio (Simon &
Wiggins 2001; Billingsley & Chance 1988; Bandopadhyaya & Jones 2008) and pressure stories at the class level.

## Publication time (part of every rule)
Value for US trading day D is used only from **D+1 13:00 UTC** (CBOE JSON posted D+1 ~02:30-04:00 UTC; OCC daily total
assumed posted overnight too, not verifiable: variant O6 also lagged one extra day). **Entry**: IC M1 bar starting 13:00
UTC on the next US trading day after D (both legs mid, half the actual spread each leg). **Exit**: 13:00 UTC h US trading
days later, h in {1, 5}; positions non-overlapping per symbol and cell. Variants: spread x1.5, both fills +1 minute,
signal lagged one more day. Swaps: research.specs / swing.rates as round 32 V (oil -2.5 bp a night). Commission 0.6 bp
on FX and metals. US2000: IC bid zbars + 0.34-pt spread x1.5 (round 32 V).

## Signals (all past-only)
- PCR_X(D) = put volume / call volume of class X on D. z_d = z of ln PCR_X(D) against the 252 previous trading days
  (>= 200 valid). z_ma5 = same on the 5-day mean of ln PCR (D-4..D). z_res = residual of ln PCR_X(D) after a 252-day
  past-only OLS on the prior 1-day and 5-day S&P 500 (CBOE SPX close) returns, then z'd: the round-32 lesson that
  "fear high -> long" is the 1-day reversal; z_res removes the price-implied part.
- Rule: contrarian and symmetric: z > k -> long the risk asset, z < -k -> short (sides below). k in {1.0, 1.5}.
- (k, form) chosen on IS 2016-21 per family x target x h, then VAL 2022-24 reported for that pick only.

## Families, sides (fixed from the literature / mechanism, never from IS), targets, cells
| id | signal | side | targets | h | k | forms | cells |
|---|---|---|---|---|---|---|---|
| O1 | CBOE **equity** P/C (retail-heavy) | contrarian: high P/C (retail fear) -> long; low (complacency) -> short. Simon & Wiggins 2001; Bandopadhyaya & Jones 2008 | US500, USTEC, US30, US2000 | 1, 5 | 1.0, 1.5 | d, ma5, res | 48 |
| O2 | CBOE **SPX+SPXW** P/C (institutional hedging) | contrarian: put hedging demand peaks with fear; dealers short puts are short futures hedges that unwind (Garleanu-Pedersen-Poteshman 2009 demand pressure) -> long on high | US500, USTEC | 1, 5 | 1.0, 1.5 | d, ma5 | 16 |
| O3 | CBOE **ETP** P/C (SPY / QQQ / IWM / GLD...) | contrarian as O1 | US500, US2000 | 1, 5 | 1.0, 1.5 | d, ma5 | 16 |
| O4 | CBOE **VIX** options P/C | low VIX P/C = VIX call (crash-hedge) buying = fear -> long indices; high -> short | US500, USTEC | 1, 5 | 1.0, 1.5 | d | 8 |
| O5 | equity P/C, ma5 form only | fear reverts -> risk-on: z > k: long USDJPY (yen safe haven unwinds), long XTIUSD, long EURUSD (USD safe haven unwinds), **short** XAUUSD (haven unwinds); z < -k: opposite | USDJPY, EURUSD, XAUUSD, XTIUSD | 1, 5 | 1.0, 1.5 | ma5 | 16 |
| O6 | OCC total **equity option volume** (contracts), z of ln vs 252 d (aggregate O/S proxy without S) | Johnson & So 2012 sign: high option activity -> **short** indices (no long leg: one-sided) | US500, USTEC, US2000 | 1, 5 | 1.0, 1.5 | d | 12 |

Total **116 graded cells**. PRE (Dukascopy, P/C from 2007-11 after warm-up): O5 USDJPY / EURUSD 2007-11..2015 and XAU
2009-15; no index PRE exists. Information only (not graded): continuous NW-t regressions of 1 / 5 day returns on each z;
JSON-era open interest P/C (2019-10..2024: no full IS); call-volume-only z.

Untestable rows of the brief, recorded: GLD / SLV / USO call-buying bursts, per-ETF O/S, FXE / FXY option volume,
customer vs firm split (OCC 2-year limit); Pan-Poteshman open-buy (needs ISE / CBOE open-close data, paid).

## Power arithmetic (before any number)
- HOLD 2025-01..2026-09 ~ 435 US trading days. |z| > 1 fires on ~30 % of days, |z| > 1.5 on ~13 %.
- h1, k 1: ~130 HOLD trades -> LIVE needs per-trade net Sharpe >= 3 / sqrt(130) = 0.26. US500 1-day sd ~95-110 bp, so
  ~26 bp net per trade (cost ~2 bp + ~2 bp swap). h5, k 1: ~40-50 non-overlapping trades -> Sharpe >= 0.45, ~100 bp per
  5-day trade on a ~220 bp sd. FX (USDJPY 1-day sd ~50 bp): ~13 bp per 1-day trade.
- Literature size: aggregate P/C contrarian slopes are monthly-scale; at 1 day they correspond to rho ~0.02-0.05, so
  a |z| > 1 trade expects ~3-7 bp at h1 (Sharpe 0.03-0.07, power 0.3-0.8), and ~15-35 bp at h5 (Sharpe 0.07-0.15,
  power 0.5-1.0). **LIVE needs ~4-5x the literature; DEMO (IS t >= 2 over ~480 IS trades at h1) needs Sharpe ~0.09,
  ~2x the literature.** Wang, Keswani & Taylor (2006) found sentiment measures incl. P/C lose their predictive power
  once past returns are controlled: hence the z_res form. Prior expectation: no LIVE; a DEMO only if the effect is
  well above the literature.
- Chance: shared random-date null (same counts, sides, holds, 200 seeds) for the best-of-family IS t; per-cell random
  control >= 200 seeds with the side recomputed at the random date (data-dependent side) and entries after the signal.

## Addendum 1, declared 2026-10-28 02:19 UTC (`date -u`): O7 FINRA daily short-sale volume of the brief's ETFs
Written after O1-O6 numbers were in (all null: best IS t 1.64 vs chance p50 1.89), **before any FINRA file was
downloaded** (only 6 format probes, rows for SPY on 2018-08-01 printed). The OCC per-underlying customer split is out of
reach (2-year limit); FINRA's daily short volume is the free per-ETF positioning series for the same underlyings.
- Source: cdn.finra.org/equity/regsho/daily/ (no robots.txt: S3 403). CNMSshvolYYYYMMDD.txt from 2018-08-01 (=
  FNSQ + FNYX, verified on SPY 2018-08-01); before that FNSQshvol + FNYXshvol summed. Pull 2015-02-01..2024-12-31
  (IS warm-up), only the 9 ETF rows kept. No PRE (2009-15 would double the requests; not pulled).
- Publication: FINRA posts the day's file by ~18:00 ET; used from D+1 13:00 UTC like O1-O6 (same entry / exit /
  costs / variants).
- Signal: SVR = ShortVolume / TotalVolume of the ETF on D; z of SVR vs 252 past days (form d) and of its 5-day mean
  (ma5).
- Side (literature): aggregate short selling predicts lower returns (Rapach, Ringgenberg & Zhou 2016, monthly; Diether,
  Lee & Werner 2009, daily single stocks: short sellers are informed / contrarian and their volume predicts negative
  returns). So **SVR z > k -> short the ETF's underlying, z < -k -> long**. Caveat known before: most ETF short volume is
  market-maker / AP liquidity provision, so the prior is weak.
- Map (ETF -> IC target, side of the target when the ETF is shorted): SPY -> US500, QQQ -> USTEC, IWM -> US2000,
  DIA -> US30, GLD -> XAUUSD, SLV -> XAGUSD, USO -> XTIUSD, FXE -> EURUSD (short), FXY -> USDJPY (FXY is long yen, so
  high FXY short volume -> **long** USDJPY).
- Cells: 9 ETFs x h {1, 5} x k {1.0, 1.5} x form {d, ma5} = **72 graded cells**; (k, form) picked on IS per ETF x h;
  shared random-date null; same bars. Power: same arithmetic as above (LIVE needs Sharpe >= 0.26 per 1-day trade;
  literature at daily index level ~0, so expected power < 0.5).
