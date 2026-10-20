# Round 25, stream B: hypotheses (predictable release surprises)

Written 2026-10-17 19:08 UTC (from `date -u`), before any return (signed or unsigned) was computed for any cell
below. Only the ForexFactory (FF) calendar (no prices), the Cleveland Fed nowcast JSON and the Atlanta Fed GDPNow
workbook (both non-price, fetched 2026-10-17 19:04-19:05 UTC, logged in the scratchpad `B/net/fetch_log.txt`) were
read so far. Bars, eras, costs and pitfalls: round 13's brief and this round's BRIEF.md; nothing is relaxed.

## Literature priors (read before declaring)
- Campbell & Sharpe (2009, JFQA 44(2), doi 10.1017/S0022109009090127): consensus forecasts (MMS, 1990-2006) are
  anchored to the previous release, giving predictable forecast errors; but **bond yields react only to the
  unpredictable residual, not to the anchoring-induced part: markets anticipate the bias.**
- Hess & Orbe (2013, Review of Finance 17(6), doi 10.1093/rof/rfs037): the anchoring test is itself biased; the
  "bias" is a statistical artefact when analysts use more information than the test assumes; bias-adjusting does
  not improve forecasts.
- Gregory & Zhu (2014, Applied Financial Economics, doi 10.1080/09603107.2014.887190): ADP improves VAR forecasts of
  payrolls, but the advantage disappears against the real-time Bloomberg consensus.
- Hess & Niessen (2010, J. Futures Markets 30, doi 10.1002/fut.20450): markets react to the earliest of similar
  indicators; a later similar indicator loses impact (consistent with prices already holding the early news).
- Gurkaynak & Wolfers (2006/07, NBER w11929): survey anomalies largely do not survive in market-based expectations;
  market-based expectations predict price responses slightly better than surveys.
- Andersson, Overby & Sebestyen (2009, German Economic Review): German unemployment numbers were known before release.
- Fed regional surveys (Dallas Fed 2014 note; Richmond Fed EQ 2018) track the ISM: the same-sign link of B2b/B2c.

Prior: B1 and B2 should be null at the release minute (the market prices a better expectation than FF's
consensus). The test is whether FX at IC shows any of the predictable part, net of release-minute spreads.

## Common definitions (all cells)
- **Calendar**: FF CSV rows with Tehran wall date < 2025-01-01 and UTC < 2025-01-01 (HOLD cut at load). UTC = the
  CSV wall time read in the system `Asia/Tehran` zone (the CSV's +04:30 label is wrong in the 2023-24 summers: Iran
  dropped DST in 2023; verified on ADP/ISM/LFS times). Rows at 00:00:00 or 23:59:59 Tehran have no time: date =
  Tehran wall date (equal to the home date for every release before ~16:00 New York). Their time, in order:
  (1) the event type's own non-defective rows: the home-local time of the nearest earlier and later own rows if they
  agree, else of the nearer one; (2) for types with no own times (e.g. USD Retail Sales m/m, CPI m/m), the time of
  the partner type that most often shares its date and currency, on that date; (3) all-day-only types (German
  Prelim CPI m/m) get no time unless one Destatis-practice candidate (13:00 / 14:00 Berlin) shows the activity
  spike in >= 80 % of IS years; otherwise they are signals only (B2), never traded. Home zones: USD New York, CAD
  Toronto, EUR Berlin, GBP London, CHF Zurich, JPY Tokyo, AUD Sydney, NZD Auckland, CNY Shanghai.
- **Time verification (direction-free)**: per event type and era, the median over events of
  n[T+k] / median(n[T-35..T-6]) for k = -90..+90 on the home instrument (IC panel n; Dukascopy n for PRE); verified
  if the maximum is at k = 0 and >= 1.5. Reported per type; failures are fixed or dropped before B0.
- **Values**: numeric with optional %, K, M, B, T suffix (x1e3, 1e6, 1e9, 1e12); multi-part ("x|y", "a-b-c"),
  "<x" and text values dropped. **Anchor Pk = the Actual (first print) of the previous row of the same (currency,
  event)** within 100 days (10 days for weekly series). FF "Previous" is the revised value shown after the release
  (NFP 2007-02-02 shows 206K for December, first printed 167K): it is a look-ahead and is not used.
- **Usual Effect**: "'Actual' greater than 'Forecast' is good for currency" -> good = +1; "less than" -> good = -1;
  anything else -> row excluded. Oriented surprise for the home currency: s = good x sign(A - F).
- **Universe (B0/B1)**: Impact High or Medium; numeric A and F; valid Usual Effect; excluded: central-bank rate
  decisions and votes, bond auctions, speeches, meetings, holidays, referendum-type votes. **Inclusion for trading
  (B1, and as a reported flag for B2 targets): the type's B0 1-minute oriented move on IS 2016-21 has day-clustered
  t >= 3 on its home instrument(s) with >= 20 IS events** (a time / sign / units validation on the realised
  surprise, IS only; VAL stays a clean check; PRE uses the same IS-chosen types).
- **Instruments**: EUR EURUSD; JPY USDJPY; GBP GBPUSD; AUD AUDUSD; NZD NZDUSD; CAD USDCAD; CHF USDCHF; USD the pair
  set EURUSD + USDJPY (two trades per slot, pooled); CNY AUDUSD (proxy, its own cells only); gold XAUUSD (side =
  minus the USD side) and US500 (side = plus the USD side, growth channel; Boyd, Hu & Jagannathan 2005 say the
  equity sign is regime dependent) only in their own cells. Home long = long the pair if home is the base (EUR, GBP,
  AUD, NZD; USD in USDJPY), short the pair if home is the quote (JPY, CAD, CHF; USD in EURUSD).
- **Slot** = (currency, UTC minute T). One trade per slot per instrument per cell.
- **Prices**: IS/VAL from the shared IC panel mid (minute label = bar START, so mid of bar T-1 is the last quote
  before T:00). PRE 2007-15 from Dukascopy bid closes: m1 EURUSD/USDJPY/USDCHF, m1c AUDUSD/NZDUSD (Sun-Fri), XAUUSD
  (Mon-Fri), GBPUSD/USDCAD (Wednesdays only, so only Wednesday GBP/CAD releases have PRE).
- **Entry / exit**: entry at the close of bar T-1 (primary) or T-2; exit h in {5, 15, 30} at the close of bar
  T+h-1 (the quote h minutes after the release). Missing bar: last quote at or before, at most 10 minutes stale,
  else the trade is dropped (same rule at entry and exit, decided without the price direction).
- **Return** (bp of the entry price) = side x (exit - entry) / entry x 1e4.
- **Cost**: half the spread at the entry bar + half at the exit bar (panel spr, in bp of mid) + 0.6 bp round trip
  for FX and gold; US500 no commission. Also spread x1.5, and both fills +1 minute (entry bar T for a T-1 entry,
  i.e. after the release minute, and T-1 for a T-2 entry; exit bar T+h). PRE cost: the median IC 2016-17 cost of
  the same event type at the same relative minutes (fallback: same instrument, all included types) + 0.6 bp.
- **Statistics**: pooled over events and instruments; t clustered by UTC day of T; eras PRE 2007-15, IS 2016-21,
  VAL 2022-24; by year; VAL/IS ratio of net; per-trade net Sharpe; power = Sharpe x sqrt(1.73 x trades per year),
  on the IS and the VAL size, also on day units; random-sign control (1,000 seeds: each trade gets a random side
  with the cell's observed long/short share; same costs; the observed net must beat the share of seeds the bars
  ask); chance benchmark per family and overall: the 95th percentile of the max |t| of K normals, and a sign-flip
  permutation per UTC day shared by all cells (1,000 draws, IS mid t). Survivors: daily P&L correlation with C3
  (trades_C3_gotobi_jpy_basket.csv, IS+VAL).
- **Bars**: LIVE and DEMO exactly as round 13 (net > 0 in IS and VAL at own costs, > 0 at spread x1.5 and +1
  minute, IS t >= 2.5 / VAL >= 1.5, >= 2/3 of years net > 0, >= 95 % of random, power >= 3 for LIVE; IS t >= 2.0,
  VAL net > 0, >= 90 % of random for DEMO). A family meeting a bar stops and gets a PREREG_DRAFT; HOLD stays closed.

## B0 (validation, not a strategy; not counted as a strategy cell)
For every universe type: mean oriented move s x home-long return from bar T-1 to bar T (1 minute) and to bar T+4
(5 minutes), day-clustered t, hit rate, n, by era and year, on its home instrument(s); events with A = F excluded.
Expected strongly positive (t of 3+ for every important type). A type that is flat or negative points to a wrong
time, unit or sign and is investigated before any B1/B2/B3 number is computed for it.

## B1 anchoring (Campbell & Sharpe 2009): 57 cells
Event vote v = good x sign(F - Pk) (the actual is predicted to land on the far side of F from Pk). Slot side for the
home currency = sign(sum of v) over the included events of the slot at the slot's highest impact level present;
0 -> no trade. Threshold variant: an event votes only if |F - Pk| >= 1.0 x the median |A - F| of its own type's
previous 24 releases (>= 12 required; causal).

| cell | pool | votes | threshold | entry | h | count |
|---|---|---|---|---|---|---|
| B1-ALL-H | all currencies except CNY | slots with a High included event, High votes only | none / 1.0x | T-1 / T-2 | 5 / 15 / 30 | 12 |
| B1-ALL-HM | all except CNY | High if present, else Medium | none / 1.0x | T-1 / T-2 | 5 / 15 / 30 | 12 |
| B1-cur (USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF) | one currency | as B1-ALL-HM | none | T-1 | 5 / 15 / 30 | 24 |
| B1-CNY | CNY releases on AUDUSD | as HM | none | T-1 | 5 / 15 / 30 | 3 |
| B1-XAU | USD releases on XAUUSD, side = -USD | as HM | none | T-1 | 5 / 15 / 30 | 3 |
| B1-US500 | USD releases on US500, side = +USD (IS/VAL only) | as HM | none | T-1 | 5 / 15 / 30 | 3 |

Primary (named before numbers): B1-ALL-H, no threshold, T-1, h 15.

## B2 early indicators against a stale consensus: 69 cells
Signal = sign of the sum of the early indicators' oriented surprises s (good x sign(A - F)); side = same sign for
the home currency at the target release; trade at the target slot on the target's instruments.

| pair | early indicator(s) (FF names) | window (relative to the target date D) | target (FF name) | instrument | sign source |
|---|---|---|---|---|---|
| B2a | USD ADP Non-Farm Employment Change | [D-7, D-1] | USD Non-Farm Employment Change | EURUSD + USDJPY | ADP and BLS private payrolls co-move (Cajner et al. 2019); null prior Gregory & Zhu 2014 |
| B2b | USD Empire State Manufacturing Index, Philly Fed Manufacturing Index, Richmond Manufacturing Index, Chicago PMI, Flash Manufacturing PMI | after the previous ISM release, before D | USD ISM Manufacturing PMI | EURUSD + USDJPY | regional surveys track the ISM (Dallas Fed 2014; Richmond Fed 2018) |
| B2c | USD Empire State Manufacturing Index | [D-10, D-1] | USD Philly Fed Manufacturing Index | EURUSD + USDJPY | same |
| B2d | flash -> final, same region and sector: EUR (EZ, German, French) manufacturing and services; GBP manufacturing and services (2019+); USD manufacturing and services | flash in [D-20, D-1] | the matching Final ... PMI | home pair (USD set for USD) | final = flash + late responses of the same panel |
| B2e | EUR German Prelim CPI m/m, Spanish Flash CPI y/y, French Prelim CPI m/m, Italian Prelim CPI m/m | [D-7, D], earlier date, or same date and time < T-1 (German same-date: excluded, time unknown) | EUR CPI Flash Estimate y/y | EURUSD | national CPIs are the HICP's components (Eurostat flash method) |
| B2f | JPY Tokyo Core CPI y/y (latest) | [D-35, D-1] | JPY National Core CPI y/y | USDJPY | Tokyo is a component and the early read of national CPI |
| B2g | USD Unemployment Claims for the survey week (week ending the Saturday on/after the 12th of the reference month = month of D-28; release dated S+4..S+5) | as stated | USD Non-Farm Employment Change | EURUSD + USDJPY | claims and payrolls co-move in the reference week |
| B2g2 | USD Unemployment Claims, all releases | (previous NFP date, D) | USD Non-Farm Employment Change | EURUSD + USDJPY | same |
| B2h | CNY Manufacturing PMI (official) | [D-5, D], earlier date or earlier time | CNY Caixin Manufacturing PMI | AUDUSD (CNY proxy) | both survey China's manufacturing in the same month |
| B2i | EUR German Flash Manufacturing PMI, German Flash Services PMI | [D-10, D-1] | EUR German ifo Business Climate | EURUSD | both are German business surveys of the same month |
| B2j | USD Core CPI m/m (latest) | [D-45, D-1] | USD Core PCE Price Index m/m | EURUSD + USDJPY | core PCE is built from CPI (and PPI) components |

Each pair x entry {T-1, T-2} x h {5, 15, 30} = 6 cells; 11 pairs = 66, plus B2-ALL (all pairs pooled, one trade per
target slot per instrument, side = sign of the sum of the pair signals, T-1, h 5 / 15 / 30) = 3. Primary per pair:
T-1, h 15. B2 targets are traded whether or not they pass the B0 inclusion; the B0 status is reported next to them.

## B3 public nowcasts vs consensus: 18 cells (+ 1 infeasible)
Vintage = the last value published on a date strictly before the release date (the release is at 08:30 ET; the
Cleveland nowcast updates ~10:00 ET; GDPNow's TrackRecord gives the final nowcast "right before" the advance
estimate).

| cell | nowcast (source, vintage status) | target (FF) | vote | instrument |
|---|---|---|---|---|
| B3a | Cleveland Fed CPI and core CPI m/m nowcasts (nowcast_month.json, daily archive since 2013-07; the site does not say whether pre-launch values were backfilled; inputs oil, gasoline, lagged CPI/PCE are rarely revised) | USD CPI m/m and Core CPI m/m (same slot) | per series sign(NC - F) if \|NC - F\| >= 0.05, slot side = sign(sum); good = +1 | EURUSD + USDJPY |
| B3b | Cleveland Fed PCE and core PCE m/m nowcasts | USD Core PCE Price Index m/m (and PCE m/m if in FF, same slot) | same | EURUSD + USDJPY |
| B3c | Atlanta Fed GDPNow, TrackRecord sheet (real-time final nowcasts since 2011q3, live since 2014) | USD Advance GDP q/q | sign(GDPNow - F) if \|diff\| >= 0.1 | EURUSD + USDJPY |
| (B3d) | NY Fed Staff Nowcast | Advance GDP | - | infeasible in this session: the page is a JS app and the vintage file was not located in three probes |

Each x entry {T-1, T-2} x h {5, 15, 30} = 6 cells; 18 in all. Primary: T-1, h 15.

## Cell count and chance
Strategy cells declared: B1 57 + B2 69 + B3 18 = **144** (B0 is validation only). 95th percentile of the max |t| of
K independent normals: 3.57 for 144 (B1 57: 3.32; B2 69: 3.37; B3 18: 2.98). Cells are strongly correlated across
h and entry, so the per-day sign-flip permutation null is the binding benchmark. (Corrected 19:10 UTC, before any
number: the first draft said 3.40 for 144.)

## Prior power arithmetic (before numbers)
LIVE needs per-trade net Sharpe x sqrt(1.73 x trades per year) >= 3: Sharpe 0.11 at 400 trades a year (B1-ALL size,
guess), 0.36 at 40 (one B2 pair on the USD set), 0.66 at 12. B2/B3 pairs can at best reach DEMO; only the pooled
B1 / B2-ALL cells could reach LIVE power, and only if the predictable part is priced at the release minute, which
the literature says it is not.

## Addendum, written 2026-10-17 19:27 UTC (after the cells were computed; records process changes, adds no cell)
- **Time-verification criterion changed before B0 was run** (the v3 verification ran ~19:16 UTC, B0 ~19:19 UTC):
  the declared "maximum over k = -90..+90 at k = 0" failed for well-timed types whose neighbourhood holds a bigger
  scheduled spike (London open one hour before the EZ final PMIs, the Tokyo fix 84 minutes after Japanese CPI,
  08:50 JST data, the month-end 16:00 London fix after the Chicago PMI). It was replaced by "r0 >= 1.5 and
  r0 >= 1.2 x max(r(-3), r(-2), r(-1))" (activity jumps at T and not before), still direction-free. Unverified
  types were not dropped before B0: the declared B0 inclusion (IS t >= 3) is what kept them out of B1; B2 targets
  were traded as declared regardless of B0.
- **Time fixes applied before B0** (direction-free, from the tick / |return| spike): FF hh:29 / hh:59 listings
  snapped +1 minute; rows exactly 60 minutes off their type's modal clock snapped (DST glitches, e.g. USD CPI y/y
  2009-11/12 at 07:30 EST); in PRE years whose spike sits at -2 minutes, Markit PMIs (EUR, GBP) moved 2 minutes
  earlier (subscriber early release, ended 2013), and the MNI Chicago PMI 3 minutes earlier where the spike sits
  at -3. German Prelim CPI m/m stays untimed (14:00 Berlin verified in 3 of 6 IS years < 80 %).
- **Post-hoc diagnostics (information only, not cells)**: predictability of FF's surprise from F - Pk (hit rate,
  Campbell-Sharpe slope), a Campbell-Sharpe pricing regression of the 5-minute move on the realised and the
  anchoring-predicted surprise, hit rates of the B2/B3 signals against the target's realised FF surprise, and
  C3 correlations of the primaries.
