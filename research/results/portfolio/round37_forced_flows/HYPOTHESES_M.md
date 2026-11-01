# Round 37, stream M: hypotheses (exchange margin and price-limit changes -> forced deleveraging)

Main file written 2026-10-29 09:35 UTC (`date -u` 09:33:22 just before). No return of any event below had been
computed when this was written. Data loaded so far: the SHFE daily contract trade-parameter files (pull running, not
yet parsed) and the SGE notice listing (pull running). No price series has been joined to any event.
Bars: research/PROMPT.md, LIVE / DEMO only. HOLD 2025-01-01..2026-09-24 closed: every series is cut at 2024-12-31 at
load, and no file dated after 2024-12-31 is requested.

## Sources
| id | source | URL | content | span |
|---|---|---|---|---|
| S1 | SHFE daily contract trade parameters | `https://www.shfe.com.cn/data/busiparamdata/future/ContractDailyTradeArgument{YYYYMMDD}.dat` (JSON) | per contract and trading day: speculative / hedge long and short margin ratio, upper / lower daily limit, `UPDATE_DATE` (19:xx-20:xx Beijing the same day) | first file 2013-07-15 (earlier dates 404) .. 2024-12-31 |
| S2 | SGE announcements | `https://www.sge.com.cn/jjsnotice?p=N`, notices `/jjsnotice/{id}` | "关于做好XXXX年春节/国庆节...期间市场风险控制工作的通知", "关于调整...保证金比例和涨跌停板的通知": effective dates and new levels for Au(T+D), Ag(T+D), mAu(T+D) | listing back to the first page that exists; used to 2024-12-31 |
| S3 | CME performance-bond history | cmegroup.com times out (brief). Tried: web.archive.org CDX of `cmegroup.com/clearing/risk-management/historical-margins*` (snapshots 2011-01-10, 2012-08-06 exist; snapshot fetches answered 429 at 09:30-09:32 UTC, backing off). Product-level history is otherwise CME DataMine (paid) or FOIA data (Hedegaard 2011, Abruzzo & Park 2014), not public. | per product initial / maintenance margin changes with effective dates | to be established |

Not a source: the SHFE rankings / warrants of round 34 H (positions), used here only as an optional crowding measure
if time allows (declared below as M-C, not part of the primary family).

## Mechanism and literature
- A margin hike raises the cash a leveraged holder must post at the effective settlement; under-margined holders
  cut. The cut is by the side that holds the leverage. Holders on both sides post margin, so the net price pressure
  comes from the side that is crowded: the one the prior trend built (trend-chasing speculators, round 34 H showed
  SHFE clients chase moves within the day).
- Literature against: Hedegaard (2011/2014, AQR WP "Causes and consequences of margin levels in futures markets",
  CME 2000-11 via FOIA) finds open interest falls after hikes but **no price effect**; volatility rises ~50 % on the
  hike day. Abruzzo & Park (FEDS 2014): CME raises margins quickly after volatility spikes (margins are endogenous to
  volatility). Daskalaki & Skiadopoulos (2016, J. Financial Services Research 49) on 20 commodities: hikes slow price
  changes and cut liquidity. Prior: low.
- Chinese specifics: SHFE / SGE raise margins and widen limits routinely before Spring Festival and National Day
  (and sometimes Labour Day, Dragon Boat, Mid-Autumn), announced 1-2 weeks ahead and restored after the holiday.
  These dates are public and fixed weeks ahead; they also coincide with "holding through a closed Chinese market",
  so a holiday-hike cell must be separated from the Lunar New Year gold drift of round 23 N3a (unconditional long,
  failed). The construction here differs: side = against the crowded side (prior-trend sign), not a fixed long.

## Definitions (fixed before returns)
- **Base margin of a product on day D (S1):** the median `SPEC_LONGMARGINRATIO` over that product's contracts in the
  day-D file **excluding the two nearest-expiry contracts** (their ratio steps up mechanically before delivery,
  which is a per-contract schedule, not an exchange decision). Base limit: the median `UPPER_VALUE` on the same set.
- **Event:** D is a hike day for the product when base margin(D) > base margin(previous file day), a cut when lower.
  A limit change is recorded with it. A change in limit only (margin unchanged) is a separate count, not traded in
  the primary family.
- **Effective clock.** SHFE notices state "自X日收盘结算时起": the new ratio applies from the settlement of day X. The
  file for trading day D is written on the evening of D (`UPDATE_DATE`). Before returns I check on S2 / known notices
  whether the first file showing the new ratio is X or X+1 and record it here as an amendment; call the settlement
  day X = E. SHFE day session 09:00-15:00 Beijing = 01:00-07:00 UTC; the night session of E (21:00 Beijing) belongs
  to trading day E+1.
- **Event classes:** holiday-routine = E within the 7 calendar days before a Chinese exchange closure of >= 3
  consecutive calendar days that include at least one weekday (Spring Festival, National Day, Labour Day, Qingming /
  Dragon Boat / Mid-Autumn when they make a 3-day break with a weekday; dates from the `holidays` package, CN);
  discretionary = every other hike.
- **Crowded side (fixed before returns):** sign of the IC symbol's mid return over the 20 trading days (28 calendar
  days) ending at the entry time t0. Long crowded if > 0. Primary rule trades **against** the crowded side after a
  hike, and **with** it after a cut (released leverage rebuilds the crowded side).
- **Product -> IC symbol:** au -> XAUUSD, ag -> XAGUSD. cu has no IC symbol; it is counted for the power table and
  used in one declared cross-asset cell only (cu -> AUDUSD, M-X below). INE sc (crude) is not in the SHFE file
  (INE is unreachable), so oil has no cell from S1/S2.

## Hypotheses and cells
Costs: XAU / XAG round trip = half spread at entry + exit minute (IC M1 `ca - c`) + 0.6 bp commission; swap for
multi-day holds from research/swing (metals); AUDUSD likewise. Fills at t0 + 1 min (and +2 min for the "+1 minute"
check), spread x1.5 check. t clustered by event date (au and ag on one date are one cluster).

| id | rule | side | entry t0 / exit | cells |
|---|---|---|---|---|
| M1 | SHFE au / ag base-margin hike (all hikes pooled) | against crowded | t0 = 07:00 UTC on E (SHFE day close of the settlement day), exits h1 = +24 h, h3 = +72 h, h5 = +120 h (calendar; if it lands on a weekend, the next open minute) | 2 symbols pooled x 3 h = 3 |
| M1p | same, pressure into the settlement | against crowded | t0 = 01:00 UTC on E (day-session open), exit 07:00 UTC on E | 1 |
| M1a | same, from the announcement: first file in which the hike is announced is not observable in S1, so M1a uses S2's notice date (SGE notice publication day, 15:30 Beijing = 07:30 UTC assumed if no time) for hikes that S1 and S2 share | against crowded | t0 = notice day 08:00 UTC, exit at t0 of M1 (E 07:00 UTC) | 1 |
| M2 | SHFE au / ag base-margin cut | with crowded | t0 = 07:00 UTC on E, h1 / h3 | 2 |
| M3 | split of M1 by class: holiday-routine vs discretionary | against crowded | as M1 h1, h3 | 4 (reported; the pooled M1 is the primary) |
| M4 | SGE Au(T+D) / Ag(T+D) hikes from S2 notices, in years S1 does not cover (PRE: first notice year .. 2013-07) | against crowded | as M1 with E from the notice text | 2 symbols pooled x h1, h3 = 2 |
| M-X | SHFE cu hike -> AUDUSD | against crowded (AUDUSD 20-d trend) | as M1 h1, h3 | 2 |
| M-C | optional, if time: M1 with the crowded side measured by the SHFE client net position (round 34 H's 期货公司 long OI minus short OI, from `pm{date}.dat`) instead of the trend | against client net | as M1 h1 | 1 |

Primary family size: M1 (3) + M1p (1) + M1a (1) + M2 (2) = 7 cells; with M3, M4, M-X, M-C = 16. The best-of-N chance
benchmark uses the family's N (max of N normals, median ~1.3 for N = 7, ~1.8 for N = 16).
CME (S3), if a history can be reached: C1 = CME hike on GC / SI / CL / NG / ES / NQ / YM / RTY / 6E / 6J / BTC ->
XAUUSD / XAGUSD / XTIUSD / XNGUSD / US500 / USTEC / US30 / US2000 / EURUSD / USDJPY / BTCUSD, against crowded, t0 =
the effective date's 22:00 UTC (CME changes are "effective after the close of business"), h1 / h3; C2 cuts with
crowded h1. 3 cells. Added as an amendment with its own time if the data arrive.

## Power arithmetic before any build
Expected counts (from the routine-holiday pattern; replaced by actual counts in an amendment before returns):
au and ag each ~2-4 hikes / year (Spring Festival, National Day, sometimes Labour Day / Mid-Autumn, plus 0-2
discretionary), nearly always on the **same date** for au and ag. So ~3-5 event dates / year, ~6-10 trades / year.

- HOLD (21 months, 1.73 y): ~10-17 trades on ~5-9 dates.
- **LIVE needs** per-trade net Sharpe >= 3 / sqrt(HOLD trades) = 0.73-0.95 (and on date clusters, >= 1.0). Gold's
  1-day sd at IC ~85 bp, so h1 would need a net edge of ~60-80 bp per trade; h5 (sd ~190 bp) ~140-180 bp. No
  margin effect in the literature is near this (Hedegaard: zero). **LIVE is out of reach by count for S1 / S2,
  whatever the effect.** The cell can at most reach DEMO.
- **DEMO needs** IS day-clustered t >= 2: IS 2016-21 ~20-30 dates, so per-date Sharpe >= ~0.4, i.e. ~35 bp on h1
  for gold. VAL > 0 on ~10-15 dates.
- Pooling cu (no IC symbol) adds no tradable count. Pooling across SHFE / SGE adds nothing: same dates.
- CME (S3): ~5-15 changes / year per product, ~11 products, but clustered (equity indices and metals often change
  together): ~60-120 product-events / year on ~30-50 dates. HOLD ~100-200 trades: LIVE needs per-trade Sharpe
  ~0.21-0.30 (per date ~0.35-0.4). Allowed by count, but ~3x anything the literature reports; DEMO possible.
- Crypto / broker leverage-cap dates (fallback): ESMA retail caps (2018-07-30 / 08-01) and similar regulatory dates
  are a few per decade: neither bar is reachable; documented only.

## Amendment 1 (2026-10-29 09:52 UTC, before any return): SGE events, effective-day semantics, CME status
- **SGE holiday-routine hikes (S2) parsed** (`scripts/sge_holiday_events.py`): 138 listing pages, 1,376 notices
  2002-06..2026-10 (titles only were listed for 2025-26; no 2025-26 notice was opened or parsed). Holiday notices
  with a hike and a stated effective settlement day, 2008-09..2024-12: **57 dates** (2011-04-28 is silver only).
  Per era: PRE (2008-09..2013-07-14, before S1 starts) **23 dates**; 2013-07..2015 7; IS 2016-21 **17**; VAL 2022-24
  **10** (2.3 / 2.8 / 3.3 per year). Three holiday notices kept margins unchanged (2012-06 Dragon Boat, 2014-04
  Labour Day, 2024-12 New Year): excluded (too few for a placebo). Notice-to-effective lead: 0-13 days, median ~5.
  Example (2020-01-15 notice): "自2020年1月22日（星期三）收盘清算时起 ... 保证金比例从6%调整为9%", i.e. the new margin
  applies from the settlement of E = 2020-01-22, two trading days before the closure, and is restored at the
  settlement of the first post-holiday day without a limit move.
- **Discretionary SGE notices** (conditional "如果今日收盘时封住跌停板 ..." hikes of 2011-13, silver 2011) are
  conditional on a limit-locked close: whether they took effect is not in the notice. They are **not** used; M4 is
  holiday hikes only.
- **SHFE file semantics.** First reading of S1 (2013-10, 2014-01/02, 2016-02): the hike first appears in the file of
  the trading day after the SGE effective day (2014: SGE E 01-29, SHFE file 01-30; 2016: SGE E 02-04, SHFE file
  02-05), and the post-holiday restores appear in the file of the second post-holiday trading day. So the file for
  day D lists the margin in force during trading day D, set at the settlement of the previous trading day: **E =
  the previous file day (LAG 1)**. To be confirmed on 2020-01 (SGE E 01-22 -> expected SHFE file 01-23) once the pull
  reaches it; if it fails, LAG 0 is used and this is recorded.
- **CME (S3): unusable.** cmegroup.com and ftp.cmegroup.com time out; web.archive.org answered 429 / 503 and then
  "flagged as suspected abusive bot traffic" for this IP (09:30-09:50 UTC): no further archive requests. CME's own
  history is DataMine (licensed); Hedegaard's and Abruzzo & Park's CME data came from FOIA and are not posted; no
  GitHub / Zenodo / figshare copy found (2 searches). The C1 / C2 cells are not run.
- **Power with the actual SGE counts:** holiday hikes give ~3.3 dates / year (6.6 trades with au + ag): HOLD ~6
  dates / 11 trades. LIVE would need a per-trade net Sharpe ~0.9 (per date ~1.2): **LIVE is impossible**; DEMO needs
  IS t >= 2 on 17 dates, i.e. a per-date Sharpe >= ~0.5.

## Amendment 2 (2026-10-29 10:30 UTC, before any IS / VAL / SHFE-PRE return; M4 PRE was run at 09:55, see STREAM_M)
- **S1 pull complete for 2016-01..2024-12** (2,187 files + 161 holiday 404s, 0 errors); 2013-07..2015 still filling.
- **LAG 1 confirmed** on 2020-01: SGE effective settlement 01-22, SHFE file of 01-23 is the first with the hike (au
  6 % -> 8 %, ag 7 % -> 9 %); restore in the file of 02-04 = settlement of the first post-holiday day 02-03.
  E = the previous file day, as amendment 1 said.
- **Actual SHFE counts (au + ag base-margin hikes):** IS 2016-21 **51 trades on 31 dates** (20 holiday-routine
  dates, 11 discretionary, 9 of them silver 2020: one-day hikes after limit-locked closes that revert the next day);
  VAL 2022-24 **14 trades on 9 dates** (4 holiday, 5 discretionary). Cuts: IS 49, VAL 14. cu hikes: IS 24, VAL 8.
  SHFE skipped several 2022-24 holiday hikes that SGE made.
- **Power with these counts:** VAL rate ~4.7 trades / year -> HOLD ~8 trades: LIVE needs a per-trade net Sharpe
  >= 1.06; **LIVE is impossible**. DEMO: IS t >= 2 on 31 date clusters needs per-cluster Sharpe >= ~0.36, i.e. for
  gold h1 (IS sd 84 bp) ~30 bp net per trade, silver h1 (sd 168 bp) ~60 bp.
- **M-C crowding measure, fixed now:** from SHFE `pm{d}.dat` of the last trading day before E (`<p>all` rows, the
  期货公司 row; CJ2 = long OI, CJ3 = short OI): client net = CJ2 - CJ3. M-C (declared): trade against the sign of the
  client net level. M-C2 (added here, before returns): against the sign of the 20-trading-day change of client net.
  h1 only, IS / VAL. Family size becomes 17 cells (M1 3, M1p, M1a, M2 2, M3 4, M4 2, M-X 2, M-C 2).
