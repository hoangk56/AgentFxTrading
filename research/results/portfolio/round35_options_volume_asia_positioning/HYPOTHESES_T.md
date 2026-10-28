# Round 35, stream T: hypotheses (declared before any return)

Written 2026-10-28 01:35 UTC (`date -u`). No series below had been joined to any return when this was written. Data
loaded so far: the parsed positioning tables (no prices joined), plus the unconditional (no-signal) 09:30 UTC sd and
cost per symbol for the power arithmetic. Bars: research/PROMPT.md LIVE / DEMO (no RELAXED).

## Sources (probed 2026-10-28 01:25-01:34 UTC; log in scratchpad `web/requests.log`)
- **TAIFEX official** (www.taifex.com.tw; robots.txt answers a 404 page, so no robots rules). The three-institutional-
  investor tables (by contract, calls / puts split) are served **only for the last three years** (form `firstDate`
  2023-10-27; a 2010 and a 2023-06 query return an empty table; the CSV download answers "DateTime error"). Older
  history is sold through TAIFEX's paid "公開資料申購" application. So the official site cannot give IS.
- **FinMind open API** (api.finmindtrade.com, no token, no account; 300 requests / hour without a token; robots.txt
  404) mirrors the same TAIFEX tables from **2018-06-05**: `TaiwanFuturesInstitutionalInvestors` (TX, MTX: long / short
  trading volume and open interest, contracts and NT$, for 自營商 dealers, 投信 investment trusts, 外資 foreign
  institutions) and `TaiwanOptionInstitutionalInvestors` (TXO, calls and puts separately). Checked against TAIFEX's own
  page for 2024-01-02: foreign TX long trades 47,732, long OI 48,357, short OI 65,786: identical.
- **TWSE cash-market three-institution flows** (BFI82U, 三大法人買賣金額統計表), via FinMind
  `TaiwanStockTotalInstitutionalInvestors` from **2004-04-07** (checked against twse.com.tw BFI82U for 2004-04-07:
  foreign buy 15,673,391,640, sell 9,255,777,003: identical). A related source in the row with a PRE era.
- **KRX** (data.krx.co.kr): every statistics menu, including 파생상품 > 투자자별 거래실적, answers "로그인 또는
  회원가입이 필요합니다" / "Please login or sign up to continue". **Login wall: not used** (an account is a user
  decision). finance.naver.com (investor-type futures tables) has robots.txt `Disallow: /`: not used. No other free
  route to Korean investor-type derivatives data was found.
- **CFFEX** member rankings: one request took 60.8 s (IF_1.csv for 2020-01-02; the file splits 期货公司 / 非期货公司).
  ~3,500 days would take ~58 h. **No fast route: not pulled** (as round 34 H).
- **JPX** daily participant volume (取引参加者別取引高, Nikkei 225 futures by broker): the JSON back-number list holds
  only 13 months. No history: not used.

All series are cut at 2024-12-31 at the request (end_date <= 2024-12-31) and again at parsing.

## Publication time and clock (fixed now)
- TAIFEX day session ends 13:45 Taipei (05:45 UTC); the three-institution tables (OI at the day-session close) are
  posted around 15:00 Taipei (07:00 UTC), per TAIFEX practice and the daily press reports. TWSE BFI82U is posted
  after the 13:30 close, around 15:00-16:00 Taipei. Taiwan has no DST.
- **Entry at 09:30 UTC (17:30 Taipei) on the Taiwan trading date D**, fill at the first IC M1 bar at +1 minute (bid /
  ask close), exit at 09:30 UTC (+1 min) of the h-th following weekday (h in {1, 3}). This leaves >= 1.5 h after the
  latest normal posting time. Robustness: spread x1.5 and +1 more minute (fill at +2).
- The signal on D uses only values dated <= D. z-scores are past-only: z(D) = x(D) / sd of x over the previous 250
  trading days (minimum 60), never using D+1.
- Entries at 09:30 UTC never fall inside C3's 23:00-02:00 UTC gotobi window. Holds of 1-3 days on USDJPY do span
  gotobi windows; USDJPY cells are also reported with every trade whose hold contains a gotobi window (5th / 10th /
  ... business-day rule as in C3) removed.

## Eras
- Futures / options families (FinMind TAIFEX, 2018-06-05+): **IS 2018-06..2021 (about 3.3 years after the 60-day
  warm-up)**, VAL 2022-24, no PRE. Shortened IS: LIVE's IS t >= 2.5 and DEMO's t >= 2.0 still apply, no rescaling.
- Cash-flow family (TWSE, 2004-04+): PRE 2004-15 for AUDUSD and USDJPY (Dukascopy, synthetic ask from IC 2016-17
  spread by minute + 0.6 bp), IS 2016-21, VAL 2022-24. Indices have no PRE here.
- HOLD 2025-01..2026-09-24 closed.

## Costs
IC bid / ask at the fill minutes (spread paid both legs); commission 0.6 bp round trip for AUDUSD / USDJPY, 0 for the
index CFDs; swap per 17:00 New York rollover from research/swing/rates.py `swap_frac_at` (FX triple on Wednesday,
indices triple on Friday as in the engine). Unconditional averages at 09:30 UTC, IS (long and short averaged, incl.
swap): HK50 5.9 bp (h1) / 9.4 (h3), JP225 5.4 / 8.9, US500 3.9 / 7.4, USTEC 5.5 / 9.4, AUDUSD 1.6 / 2.8, USDJPY
1.1 / 1.9. HK50 has a 09:30 UTC quote on 91 % of IS weekdays (HK night session from 09:15 UTC; holidays), the others 99 %.

## Power arithmetic (before any return)
Unconditional sd of the 09:30 -> 09:30 UTC move, IS 2016-21: HK50 120 bp (h1) / 199 (h3), JP225 126 / 214, US500
107 / 171, USTEC 132 / 205, AUDUSD 60 / 104, USDJPY 50 / 88.

LIVE: per-trade net Sharpe x sqrt(HOLD trades) >= 3 over 1.73 HOLD years.

| signal | trades / yr | HOLD n | Sharpe needed | net edge needed per trade (bp) |
|---|---|---|---|---|
| daily, k = 0 (every day), h 1 | ~245 | ~425 | 0.146 | HK50 17.5, JP225 18.4, US500 15.5, USTEC 19.3, AUDUSD 8.7, USDJPY 7.4 |
| daily, k = 1 (~32 % of days), h 1 | ~78 | ~135 | 0.258 | HK50 31, JP225 32, US500 27, USTEC 34, AUDUSD 15.5, USDJPY 13 |
| daily, k = 0, h 3 (overlapping: effective n / 3) | | | 0.253 vs h3 sd | HK50 50, JP225 54, US500 43, USTEC 52, AUDUSD 26, USDJPY 22 |

Add the cost above to get the mid edge. For a sign rule the mid edge is about 0.8 x rho x sd, so LIVE at k = 0 h 1
needs a next-day correlation of about **0.17-0.20** between the signal and the target's return (US500: (15.5 + 3.9) /
(0.8 x 107) = 0.23).
DEMO on the shortened futures IS (~810 trades at k 0): IS t 2 needs Sharpe 0.070 (US500 ~7.5 bp net, h1).

Expected size from the literature: Chang, Hsieh & Lai (2009, J. Banking & Finance 33, "Do informed option investors
predict stock returns? Evidence from the Taiwan Stock Exchange") find foreign institutions' net option buying in TXO
predicts the **next-day TAIEX** (the local index, the strongest possible link). Foreign futures OI as a predictor of
TAIEX is studied in NYCU / NTU theses (e.g. "A Study of the Impact of Foreign Capitals' Open Interest on TAIEX",
ir.lib.nycu.edu.tw/handle/11536/71839), mostly as same-day or Granger links. Richards (2005, JFQA, "Big fish in small
ponds") finds foreign flows into Asian markets (Taiwan, Korea) follow lagged global (US) returns and have a mostly
permanent price impact on the local market, i.e. they carry yesterday's global information, not tomorrow's. For
targets outside Taiwan (none of IC's symbols is the TAIEX) the plausible next-day correlation is <= 0.03-0.05, which
gives US500 ~3-4 bp mid per trade, i.e. about the cost. **LIVE needs ~4-6x the plausible size; prior for LIVE ~1 %,
for DEMO ~3-5 %.**

## Families, sides (fixed now from the mechanism / source) and cells
Risk direction: "risk-on" = long HK50, JP225, US500, USTEC, AUDUSD and long USDJPY (yen weakens in risk-on).
Signal side: risk-on when z > k, risk-off when z < -k (k = 0: sign of z every day). k and h chosen on IS per target
and family; VAL checks the IS choice. Targets: HK50, JP225, US500, USTEC, AUDUSD, USDJPY (6).

**F1. Change in foreign institutions' net futures OI, FOLLOW (foreign as informed; practitioner "外資期貨淨空單"
indicator).** n(D) = (TX long OI - TX short OI) + (MTX long OI - MTX short OI) / 4 for 外資 (TX-equivalent contracts);
x(D) = n(D) - n(previous trading day). z as above. A rise in foreign net long (fall in net short) = risk-on.
Cells: 6 targets x k {0, 1} x h {1, 3} = **24**.

**F2. Level of foreign net futures OI at an extreme, FOLLOW (sizable foreign net short = risk-off).** z_level(D) =
(n(D) - mean of n over the previous 250 days) / sd of n over the previous 250 days (min 60). Risk-off when z_level < -1,
risk-on when > +1; k = 1 and h = 3 fixed. Cells: **6**.

**F3. Foreign institutions' net bullish TXO flow, FOLLOW (Chang, Hsieh & Lai 2009).** x(D) = (call long trades -
call short trades) - (put long trades - put short trades) of 外資 on day D, in contracts (buying calls / selling puts
= bullish). z of x itself (a flow, not a change). k = 1 only (the extreme-flow days), h {1, 3}. Cells: 6 x 2 = **12**.

**C1. Foreign net buying of Taiwan stocks (TWSE BFI82U), FOLLOW.** x(D) = foreign buy - foreign sell, NT$ (外資 +
外資自營商 from their 2017-12 split). z as above (min 120 days in PRE / IS). Positive = risk-on. Mechanism: foreign
institutions as informed global investors whose Asian flows persist (Richards 2005 finds persistence; the side is the
informed / persistence side, not the feedback side). Cells: 6 x k {0, 1} x h {1, 3} = **24**; PRE 2004-15 for AUDUSD
and USDJPY only.

**Total declared cells: 66.** Chance benchmark: median of the max |Z| of 66 independent normals ~2.53 (95th pct
~3.2); the cells are strongly correlated across targets (the indices move together), so the effective count is lower;
I report both the independent-normal benchmark and the random controls.

Information only (no cells, no side): same-day correlation of each investor type's change with the TAIEX-session
return of HK50 / JP225 (previous day 09:30 UTC -> D 05:45 UTC), and the next-day correlation of dealers' and
investment trusts' changes, to show who leads and who absorbs. An equally weighted equity basket (HK50, JP225, US500,
USTEC) per family is reported as information (not a cell).

## Tests per cell
Mid and net bp per trade by era (PRE / IS / VAL) and by year; t per trade for h 1 (one trade per day = day-clustered),
Newey-West (lag 3) for overlapping h 3; VAL / IS; spread x1.5 and +1 minute; per-trade Sharpe and power at IS and VAL
size; for every cell with declared-side IS t >= 1.5: 200-seed random-entry control (random trading days of the same
era at the same clock, same count, the cell's side sequence permuted) and a 200-seed circular shift of the signal
series. March-April 2020 excluded as a robustness line. A cell that meets DEMO / LIVE on IS + VAL stops its family and
gets a PREREG_DRAFT. For a survivor: daily P&L correlation with C3 (IS + VAL).
