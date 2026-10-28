# Round 34, stream E: hypotheses (leveraged / inverse ETP rebalancing with the measured dollar dose)

Written 2026-10-27 20:36-20:50 UTC (`date -u` at start: Tue Oct 27 20:36:04 UTC 2026), **before any return of this
stream was computed**. Data loaded so far, not joined to any return: ProShares daily NAV / shares outstanding / AUM
for 31 funds (cut at 2024-12-31 at parse) and CFTC legacy COT open interest 2008-2024 (9 markets).

## HOLD hygiene disclosure
- While probing the ProShares file format (the first request, 20:30 UTC), `head -c 600` printed the header and the
  first five rows of TQQQ's file, which are dated 2026-10-20..2026-10-26 (TQQQ NAV, shares outstanding, AUM). These are
  fund values inside / after HOLD, not IC prices; they were not saved anywhere else and are not used. All later parsing
  drops rows dated after 2024-12-31 before anything is printed (scripts/parse_ps.py). No IC price after 2024-12-31 has
  been loaded.

## Sources (all public, no account)
- ProShares historical NAV files `https://accounts.profunds.com/etfdata/ByFund/<TICKER>-historical_nav.csv` (the
  "download" link of proshares.com product pages; accounts.profunds.com has no robots.txt (404); proshares.com's
  robots.txt disallows /api/, /funds/, /product-data/ etc., none of which was requested). Columns: Date, NAV, Prior NAV,
  NAV change %, Shares Outstanding (000), AUM. 31 funds, 2006-2011 inception to 2024-12-31 after the cut.
- CFTC legacy futures-only COT annual files `https://www.cftc.gov/files/dea/history/deacot<YYYY>.zip`, 2008-2024: open
  interest (contracts) for E-mini + big S&P 500, Nasdaq-100 mini + big, DJIA x$5 + x$10, Russell 2000 (CME E-mini and
  ICE mini), VIX futures, COMEX gold, COMEX silver, NYMEX WTI, NYMEX natural gas.
- CBOE VIX daily history (VIX.csv as downloaded by round 32 V into its scratchpad; copied, cut at 2024-12-31) for the
  VIX-futures beta.
- Not reachable / not used: Direxion (403 per the brief's probe: TNA/TZA, SPXL/SPXS, TECL, SOXL are therefore missing,
  which understates the Russell and S&P doses), Credit Suisse ETNs (UGAZ/DGAZ, TVIX, XIV: delisted, no free daily
  shares archive found yet; a coverage gap for natgas before 2020 and VIX before 2018), USCF USO / UNG / BNO (1x funds:
  L(L-1) = 0, they carry no leverage-rebalancing dose; their monthly roll is a different family).

## Mechanism and literature (sides fixed here)
A fund with daily leverage L must trade, at its rebalance time, AUM x L(L-1) x r of the underlying, where r is the
underlying's return since the last rebalance (Cheng & Madhavan 2009). L(L-1) > 0 for every L except 0 and 1, so long
and inverse funds both trade **in the direction of the day's move**. Shum, Hejazi, Haryanto & Rodier 2016 and Barbon,
Beckmeyer, Buraschi & Moerke 2021 (with short-gamma hedgers) find price pressure into the close in the day's direction
and a reversal afterwards; Ivanov & Lenkey 2018 argue creations/redemptions offset much of the rebalancing (the null).
Sides: **follow** the dose into the benchmark (H1, H2, H4); **fade** it after the benchmark into the next morning (H3).

## Publication lag (rule; written before any return)
- ProShares posts the row dated D after D's NAV strike. Observed at 2026-10-27 20:30 UTC (16:30 ET): the file's last
  row was 10/26 and 10/27 was absent. **Rule: on trading day d the signal uses only the fund row with the latest date
  < d** (normally d-1, posted the previous evening). The posting time of a new row will be re-checked later this session
  (presence of the date only, no values printed). If d-1's row turns out to appear only during d, the robustness run
  uses the row dated <= d-2.
- Shares outstanding may lag creations by a day (T+1 booking). Check (before returns, outcome cannot change the rule):
  corr of the daily change in shares with the fund's same-day vs previous-day NAV return for the 3x funds. Either way
  the rule only uses rows dated < d, so a lag adds noise, not look-ahead.
- COT: the report as of Tuesday T is released Friday T+3 at 15:30 ET. **Rule: on day d use the latest report with
  T + 3 < d** (calendar days), i.e. released before d.

## Definitions
- Fund maps and L (prospectus; verified by NAV-change ratios against the -1x sibling / each other before any return):
  USTEC: TQQQ 3, SQQQ -3, QLD 2, QID -2, PSQ -1 | US500: UPRO 3, SPXU -3, SSO 2, SDS -2, SH -1 | US30: UDOW 3,
  SDOW -3, DDM 2, DXD -2, DOG -1 | US2000: URTY 3, SRTY -3, UWM 2, TWM -2, RWM -1 | XAUUSD: UGL 2, GLL -2 | XAGUSD:
  AGQ 2, ZSL -2 | XTIUSD (XBRUSD information only): UCO 2, SCO -2 | XNGUSD: BOIL 2, KOLD -2 | VIX: UVXY 2 then 1.5 from
  2018-02-28, SVXY -1 then -0.5 from 2018-02-28 (VIXY, VIXM 1x: no dose). If the ratio check shows another leverage
  change, the detected date is used and disclosed.
- Gamma Γ(d) = Σ_f AUM_f(row < d) x L_f(L_f - 1) (dollars).
- Benchmark B (New York clock, DST-aware): US500 / USTEC / US30 / US2000 16:00; XAU 13:30 (COMEX settlement); XAG 13:25;
  XTI and XNG 14:30 (NYMEX settlement); XBR 14:30 information only.
- Days: NYSE trading days (holidays package), early-close days dropped; energies 2020-04-14..2020-04-30 dropped.
- Prices: IC M1 mid = (bid close + ask close)/2, close of the bar ending at the clock, forward-filled <= 10 minutes;
  US2000 bid-only bars: mid = bid + 0.17 points, cost 0.34 points round trip (round 7 published spread). IC loads cut at
  ts < 1735689600000. PRE (XAU, XAG only): Dukascopy m1c 2009-2015, cost = IC 2016-17 median spread by New York minute +
  0.6 bp.
- r(d) = ln( mid at B-w-1 on d / mid at B on the previous trading day ). Dose D(d) = Γ(d) x r(d).
- Liquidity: dollar open interest DOI(d) = COT units (contracts x multiplier, summed over the listed contracts) x the IC
  mid at B on d-1 (VIX: x the VIX index close of d-1). **Scaled dose S(d) = D(d) / DOI(d).**
- Trade: signal at the close of bar ending B-w-1, entry at close of bar ending B-w, exit at close of bar ending B.
  Net = mid - half actual spread at entry - half at exit (- 0.6 bp for XAU / XAG). One trade per target per day.
- Stress (all cells): spread x1.5; both fills +1 minute (enter B-w+1, exit B+1, same signal); ex-2020.

## Hypotheses and counted cells (52)
- **H1-roll (16 cells: 8 targets x w in {15, 30})**: trade (follow sign S) when |S(d)| > the 90th percentile of |S| over
  the previous 250 trading days (>= 120 valid). Same shape as round 13 P1, but ranked by AUM x L(L-1) / OI x r, so a day
  with the same |z| ranks higher when the funds are big relative to the futures market.
- **H1-abs (16 cells)**: trade when |S(d)| > the expanding 90th percentile of the NAV-based daily dose S_nav over all
  days from fund-data start to d-1, where S_nav(k) = Γ(k)/DOI(k) x r_nav(k), r_nav = - NAV change of the -1x fund
  (PSQ, SH, DOG, RWM) for indices and NAV change of the 2x fund / 2 (UGL, AGQ, UCO, BOIL) for commodities. This keeps
  the absolute level of the dose (AUM growth) instead of a rolling rank; the history starts 2009-2011, so the threshold
  is set before IS begins.
- **H2-size (8 cells, w 15, all days)**: follow sign S every day with size clip(|S| / median_250(|S|), 0.5, 2); report
  net per unit of size. The only route with ~250 trades a year per target.
- **H3-rev (8 cells)**: on H1-roll (w 15) days, **fade** sign S from the close of the bar ending B+1 to 10:00 New York
  on the next trading day. Swap: research.swing.rates.swap_frac_at for indices and metals, -2.5 bp per night for XTI,
  -4 bp for XNG (both sides).
- **H4-VIX (2 cells, w 15 and 30)**: VIX-ETP vega rebalancing. Γ_V(d) from UVXY + SVXY; the VIX-futures move is proxied
  by β60(d) x r_US500(d), β60 = OLS slope of daily VIX-index log changes on US500 16:00 log returns over the previous 60
  days; S_V = Γ_V x β60 x r / (VX units x VIX_{d-1}). Top decile of |S_V| (rolling 250): US500 **follow sign r_US500**
  into 16:00 (ETPs buy VX futures as the market falls; the hedge of that flow sells equities).
- **H5 pooled (2 cells)**: H1-roll w 15 averaged per day across the 4 indices (P-IDX) and across all 8 targets (P-ALL).
- Information only (not counted): XBR with the UCO/SCO dose; the dose-response OLS slope of signed window return on
  |S|; H1 at the PRE era for XAU / XAG (counted as evidence, not as a cell); the dose size in % of DOI per 1 % move;
  Ivanov-Lenkey offset (corr of the next day's dollar creations x L with the dose).

## Eras and bars
IS 2016-2021 (energies 2018-21), VAL 2022-2024, PRE 2009-2015 for XAU / XAG. Bars unchanged from research/PROMPT.md:
LIVE: IS day-clustered net t >= 2.5, VAL >= 1.5, >= 2/3 years > 0, >= 95 % of random entries, power >= 3, + x1.5 and +1
min > 0. DEMO: IS t >= 2.0, VAL > 0, >= 90 % random. Random control: >= 200 seeds, same count per era, random trading
days and a random signal minute (indices 10:30 ET..B-w-1; commodities 09:00 ET..B-w-1), side recomputed from the
previous benchmark to the random signal minute, same window and costs. Chance: per-UTC-day sign-flip permutation
(1,000 draws) shared by the counted cells, distribution of the max IS net t.

## Power arithmetic (before any return)
- Top-decile cells: ~25 trades a year per target -> ~43 HOLD trades -> LIVE needs per-trade net Sharpe >= 3/sqrt(43)
  = 0.46. The best earlier big-day cell (gold L4-G-d) had 0.29 IS / 0.19 VAL; round 13's index top deciles were ~0 ex
  2020. Pooling 8 targets (indices move together: ~4 independent groups) gives ~100 day-clusters a year -> 173 HOLD ->
  Sharpe per day >= 0.23: every group would need gold-sized IS effects without decay.
- H2 all days: 250 a year -> 432 HOLD -> Sharpe 0.144. US500 15-min sd ~12.4 bp (round 10 frontier) -> net >= 1.8 bp
  a day, mid >= ~3.6 bp after ~1.8 bp cost; round 12 L6 measured +1.5 / +1.0 bp at mid on all days for USTEC.
- H3: 1-day sd 60-110 bp -> at 25 a year it needs >= ~30 bp per trade.
- Dose size (back of envelope from median 2016-24 AUM): Nasdaq funds ~$63bn of Γ -> ~$0.6bn per 1 % move, ~1 % of NQ
  dollar OI; gold UGL+GLL ~$0.45bn of Γ -> ~$5m per 1 % (~0.005 % of COMEX OI); silver ~$0.8bn Γ; crude ~$2.4bn; natgas
  ~$0.26bn. Outside equities the measured ProShares dose is tiny relative to the futures market, so a large effect in
  metals / energies would not be this mechanism.
- Prior: LIVE probability ~2-3 % (count cap + 2020 tail + decay); the dose is the only untested ingredient.

## Addendum 1 (2026-10-27 20:41 UTC, after the 52 declared cells were computed; post hoc, information only)
- Mechanism checks run before any return (scripts/mech_check.py): every L above is confirmed by NAV-change ratios
  in every year (TQQQ/PSQ -3.00 ... UVXY/VIXY 2.00 then 1.50 from 2018, SVXY/VIXY -1.00 then -0.50); no other leverage
  change. AUM = NAV x shares in every row. Shares-outstanding changes correlate more with the **same** day's fund
  return than with the previous day's (TQQQ -0.29 vs -0.19, SQQQ -0.34 vs -0.19, UCO -0.47 vs -0.28, BOIL -0.47 vs
  -0.18): the row dated D already includes D's creations / redemptions, so the row dated d-1 used on day d is the
  exposure the fund carries into d. The rule (row < d) is unchanged.
- Post-hoc check P1 (not counted): does the measured dose add anything to the day's move? Within the days whose
  vol-scaled move |z| (round 13 P1 definition: r / sd of the previous 60 daily benchmark returns) is in its rolling top
  decile, split by Γ/DOI above vs below its rolling 250-day median; and OLS of the signed window mid on |z| and
  |z| x (Γ/DOI / its rolling median). Indices, gold, silver, oil, w 15 and 30.
- Extension X1 (declared before any of its data is loaded): Nikkei 225 leveraged / inverse ETFs (NEXT FUNDS 1570 2x,
  1357 -2x; others if the same source has them), if their daily NAV and units are downloadable without an account.
  Target JP225 at the OSE day-session close (15:15 Tokyo; 15:45 from 2024-11-05) and the TSE close (15:00; 15:30 from
  2024-11-05), w 15, H1-roll rule with S = Γ x r / (Γ's rolling 250-day median) if no free Nikkei futures OI source is
  found (stated if so); follow sign r. 2 counted cells (+ the same split check as P1).
