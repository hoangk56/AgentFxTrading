# Round 34, stream H: hypotheses (declared before any return)

Written 2026-10-27 20:36 UTC (`date -u`), before any IC price was joined to any SHFE / INE series. Data loaded so far:
probe files only (structure, publication-time fields). Bars: research/PROMPT.md LIVE / DEMO (no RELAXED).

## Sources (probed 2026-10-27 20:30 UTC; no robots.txt on either host: both answer 404)
- SHFE member rankings, one JSON per trading day:
  `https://www.shfe.com.cn/data/tradedata/future/dailydata/pm{YYYYMMDD}.dat`. Per contract, ranks 1-20 for volume
  (CJ1), long OI (CJ2) and short OI (CJ3) with member name / id and day change; rank 999 = top-20 sum. From some date
  in 2016 (2015-12-30 lacks it, 2016-12-30 has it) each product also has two rows `<product>all` RANK -1 = futures
  companies (期货公司, i.e. brokers' clients) and RANK 0 = non-futures-company members (非期货公司: banks, miners,
  refiners, trading houses). Long and short of the two rows add to the same total, so this is a **complete daily
  split of the market's OI**, a Chinese daily "COT". Gold from 2008-01, silver from 2012-05.
- INE: the ranking file exists but **crude oil (sc) is never in it** (2018-04-02 empty, 2020-01-02 and 2022-01-04 only
  nr, 2024-12-31 ec / lu / nr). INE does not publish crude member rankings: no oil positioning family is possible.
- SHFE daily warrant report (仓单日报) `{YYYYMMDD}dailystock.dat` (gold, silver, copper...), weekly stock report
  `{YYYYMMDD}weeklystock.dat` (Fridays; warehouse stocks incl. copper; INE crude in `o_cursorine`); INE daily warrant
  report `https://www.ine.cn/data/tradedata/future/dailydata/{YYYYMMDD}dailystock.dat` (crude from 2018-03).
- Downloads are cut at 2024-12-31 at the request level (no file dated after 2024-12-31 is requested).

## Publication time and entry clock (fixed now)
- SHFE trading day D = night session from 21:00 Beijing of the previous business day (gold / silver night trading
  from 2013-07) + day session 09:00-15:00 Beijing. The ranking / warrant files for D are published after the day
  session and **include the preceding night session**; OI is at the 15:00 Beijing (07:00 UTC) close.
- Observed `update_date` fields: 2015-12-30 20:59:30, 2016-12-30 20:59:30, 2020-01-02 20:00:30 and 2024-12-31
  15:46:32 Beijing (files before 2015 carry no time; the HTTP Last-Modified is a 2024 site migration, useless).
- **Entry at 13:00 UTC on Beijing date D** (= 21:00 Beijing, after every observed update time), fill at +1 minute.
  Rule fixed now: if the parsed `update_date` distribution of 2016-24 shows any file updated after 20:59 Beijing on
  day D, the entry moves to the first whole UTC hour after that file's time for that day (and the day is dropped if it
  is after 20:00 UTC). Files without a time (2008-15) use the same 13:00 UTC clock (disclosed assumption).
- Exits at 13:00 UTC of the h-th following weekday on which the IC symbol trades, h in {1, 3}. h = 5 is not used: a
  Friday entry would be held 7 days (> the 5-day cap); h = 3 from Friday ends Wednesday (5 x 24 h).
- Weekly copper stocks (Friday report): entry Friday 13:00 UTC.

## Eras
PRE 2004-15 where both series exist (gold rankings 2008-01..2015, silver 2012-05..2015; IC XAU / XAG / AUDUSD from
Dukascopy m1c with ask = bid x (1 + IC 2016-17 spread profile) + 0.6 bp commission), IS 2016-21 (choose k, h), VAL
2022-24. Family B (the FCM / non-FCM split) starts in 2016: its IS is shortened (~5-6 years); LIVE's IS t >= 2.5 still
applies. Crude warrants start 2018-03: IS 2018-03..2021 (3.8 y), DEMO at most realistic. HOLD 2025-26 closed.

## Costs and fills
IC M1 bid / ask at the fill minute (spread paid both legs), commission 0.6 bp round trip for XAU / XAG / AUDUSD, 0 for
XTI / XBR; swap: XAU / XAG / AUDUSD from research/swing/rates.py `swap_frac_at`; XTI / XBR -2.5 bp per rollover on
either side (round 31 brief convention, conservative for shorts). Always also spread x1.5 and +1 minute (fill at +2).

## Power arithmetic (round 10 frontier: 1-day sd XAU 84 bp, XAG 152, XTI 345 incl. 2020, XBR 239, AUDUSD 60)
LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3, HOLD = 1.73 years.
| signal | trades / yr | HOLD n | Sharpe needed | per-trade edge needed |
|---|---|---|---|---|
| daily, k = 0 (every day), h 1 | ~245 | ~425 | 0.146 | XAU 12.2 bp, XAG 22, XTI 50 (sd ex-2020 ~230 -> 34), XBR 35 |
| daily, k = 1 (~32 % of days), h 1 | ~78 | ~135 | 0.258 | XAU 22 bp, XAG 39, XTI 60-89, XBR 62 |
| daily, h 3 (overlapping; effective n / 3, sd x sqrt 3) | | | | XAU ~65 bp per trade at k 1, ~37 at k 0 |
| weekly copper -> AUDUSD, k 1, h 1 | ~16 | ~28 | 0.57 | ~34 bp (sd 60) |
Expected size from the literature: positioning tables predict 1-5 day futures returns with |rho| of at most ~0.03-0.05
(Kang, Rouwenhorst & Tang 2020 weekly US COT liquidity premium; Wang 2001-type informed-trader studies; round 31 J:
|corr| <= 0.07 for Japanese retail OI). At rho 0.05, XAU k 0 h 1 gives ~4 bp per trade, Sharpe 0.05, power ~1.0.
**LIVE needs ~3x the literature's size**; DEMO (IS t >= 2) needs rho ~0.07 at k 0 over 6 IS years. Prior: low; round
33 S already found the Chinese gold premium carries no next-day information about London gold.

## Families, sides (fixed now from the mechanism / source) and cells
All z-scores are past-only: z(D) = x(D) / sd of x over the previous 250 trading days (minimum 120), never using D+1.
Signal side: long when z > k, short when z < -k (k = 0 means sign of z every day), unless the family says otherwise.

**A. Top-20 members' net (informed-member momentum; side FOLLOW).** Source: the Chinese practitioner "spider web"
(蜘蛛网) timing rule (Guotai Junan quant research, ~2013, CFFEX top-20 member positions: follow the top-20 members'
net long change as informed traders, against the rest of the market; cited from memory, not fetched) and the
"informed institutional traders" literature (Taiwan futures, Lai & Wang 2015 extreme dealer OI). Per product p in
{au, ag}: L = sum over contracts of the 20 largest long OI (CJ2 ranks 1-20), S = same for short (CJ3);
s(D) = (L - S) / (L + S); x = s(D) - s(prev trading day). au -> XAUUSD, ag -> XAGUSD.
Cells: 2 symbols x k {0, 1} x h {1, 3} = **8**. k and h chosen on IS per symbol.

**B. Non-futures-company members (commercials) vs brokers' clients (side: FOLLOW the commercials' net trading = fade
the clients).** Source: Kang, Rouwenhorst & Tang (JF 2020, "A Tale of Two Premiums"): short-term position changes are
driven by speculators' liquidity demand and commercials earn a liquidity premium by taking the other side, so
returns after commercials' net buying are positive. n(D) = (L0 - S0) / (L0 + L-1) from the `<p>all` rows
(RANK 0 = non-FCM, RANK -1 = FCM); x = n(D) - n(prev). au -> XAUUSD, ag -> XAGUSD. From the split's first date (2016).
Cells: 2 x k {0, 1} x h {1, 3} = **8**.

**C. Named large brokers (side FOLLOW).** Practitioner lore (席位分析): 永安期货 (Yongan) and 中信期货 (CITIC Futures) as
"smart" seats. m(D) = (sum of the member's long OI over contracts where it is in the long top 20 - same for short) /
((L + S) / 2), only on days when the member is listed on both sides in the product's largest-OI contract; x = m(D) -
m(prev valid day). k = 1, h = 1 fixed (no IS choice). Cells: 2 members x 2 metals = **4**.

**W. Warehouse warrants / stocks (side: a draw = physical demand = LONG; a build = SHORT).** Mechanism: cancelled
warrants are metal taken out of exchange warehouses for use / export (the SHFE-London arbitrage moves metal), a rise is
supply delivered against futures. x = log(W(D) / W(D-5 trading days)) of the total registered warrants; long when
z < -1, short when z > +1 (k = 1 fixed).
- W1 silver warrants (daily, total WRTWGHTS) -> XAGUSD, h {1, 3}: 2 cells.
- W2 gold warrants (daily) -> XAUUSD, h {1, 3}: 2 cells (gold warrants are small; low prior).
- W3 INE crude warrants (daily, 2018-03+) -> XBRUSD and XTIUSD, h {1, 3}: 4 cells.
- W4 SHFE copper total warehouse stock (weekly, Friday) -> AUDUSD (declared copper proxy: Australia's export
  basket; IC has no copper symbol), x = weekly log change, h {1, 3}: 2 cells.
Total W: **10**.

**Total declared cells: 30.** Chance benchmark: median of the max |Z| of 30 independent normals ~2.30 (95th pct ~3.0);
also a permutation / circular-shift null shared by all cells.

## Tests per cell
Mid and net bp per trade by era (PRE / IS / VAL) and by year; t per trade for h 1 (one trade per day = day-clustered),
Newey-West (lag 3) for overlapping h 3; VAL / IS; spread x1.5 and +1 minute; per-trade Sharpe and power at IS and VAL
size; random-entry control (>= 200 seeds: random trading days of the same era and weekday mix at the same clock, same
count, the cell's side sequence permuted) and a circular-shift control of the signal; March-April 2020 excluded as a
robustness line. A cell that meets DEMO / LIVE on IS + VAL stops its family and gets a PREREG_DRAFT. For a survivor:
daily / monthly P&L correlation with C3 (IS + VAL).

## Disclosures (HOLD hygiene)
- One WebSearch (Chinese, "会员持仓排名 前20名 净多头...") returned auto-generated 10jqka (同花顺) daily notes dated
  2026 whose summary quoted rolling 2-year correlations between SHFE silver / gold top-20 net positions and price
  (silver -0.21 in 2026-02 and -0.70 in 2026-09; gold +0.34 in 2026-08). These are 2025-26 descriptive numbers (price
  level vs net position, not returns). They were not used for any side or parameter: the sides above come from the
  mechanism / sources named.

## Amendment 1 (2026-10-27 20:39 UTC, before any return; data definitions only, no side or cell change)
- The FCM / non-FCM split also exists **per contract** before 2016 (seen in 2013-01-04 and 2015-12-30 files; absent in
  2010-01-04); from 2016 only the product rows `<p>all` carry it. Family B uses the product row when present and
  otherwise the sum of the per-contract RANK -1 / 0 rows, from the first date the split exists. B therefore may have
  a PRE era (2013?-15); the exact start is reported in STREAM_H.md.
- Member names change: family C maps Yongan = {永安期货, 浙江永安 (pre-rename)}, CITIC = {中信期货, 中信新际 (CITIC
  Newedge, merged into CITIC Futures)}.
- In family B the denominator is total OI = L0 + L-1 (long side of both rows; equals the short total).

## Amendment 2 (2026-10-27 23:14 UTC; families A, B, C on gold / silver already computed, W not yet)
- New cells, declared before their returns: **A-cu and B-cu**, the same definitions and sides as A (follow the top-20
  net change) and B (follow the non-FCM members' net change) on SHFE copper (cu rankings 2008+, split from
  2013-06-25), target **AUDUSD** (the declared copper proxy, as W4), k {0, 1} x h {1, 3}: **8 cells**. Total cells now
  38 (chance median of the max |Z| of 38 ~2.38).
- Information only (no rule): the same-window correlation of the position changes with the metal's return over the
  SHFE trading day (previous weekday 13:00 UTC -> D 07:00 UTC).
- CFFEX rankings (IF / IH / IC index futures, the spider-web rule's own market, as a proxy for HK50) answer at
  ~60 s per request over http (https hangs): ~3,500 days would take ~2.5 days of polite crawling. Not fetched;
  no CFFEX cell is declared.

## Amendment 3 (2026-10-28 01:21 UTC; before any W return)
- The weekly stock files sit under `/weeklydata/`, not `/dailydata/`: the bulk pull requested the wrong path (889 x
  404), so W4 as declared (weekly copper warehouse stock) is **not run**. Replacement, declared now with the same side
  and clock: **W4' daily copper warrants** (SHFE daily warrant report, total row 总计), x = 5-day log change,
  draw (z < -1) -> long AUDUSD, h {1, 3}: 2 cells (count unchanged).
- The daily warrant pull was stopped at the lead's request: W1, W2 and W4' cover 2014-05-19..2024-03-27
  (SHFE returns 404 for the daily warrant file before 2014-05-19 on this path), so PRE is only 2014-05..2015 and VAL is
  2022-01..2024-03. Total per product: the 总计 row when present, otherwise the sum of the warehouse rows (gold has a
  single row).
