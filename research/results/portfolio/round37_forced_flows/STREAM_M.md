# Round 37, stream M: exchange margin and price-limit changes as forced deleveraging (SHFE, SGE; CME unreachable)

Written 2026-10-29 from 10:40 UTC. Hypotheses: [HYPOTHESES_M.md](HYPOTHESES_M.md) (main file 09:35 UTC, amendment 1
09:52, amendment 2 10:30, each before the returns of the cells it covers; M4's PRE returns were computed at ~09:55,
after amendment 1). Bars: research/PROMPT.md, LIVE / DEMO only.

HOLD (2025-01..2026-09-24) stayed closed: no SHFE / SGE file or notice dated after 2024-12-31 was requested or
parsed, and IC prices were cut at ts < 2025-01-01 at load. Two disclosures: (1) the SGE listing pages show notice
titles of 2025-26 (holiday risk-control notices); only titles were seen, no 2025-26 notice was opened. (2) A WebSearch
summary (looking for SHFE's 2020 notice text) quoted SHFE's 2026 pre-holiday margin level for gold / silver. Margin
levels only, no prices; not used.

## Answer
**No LIVE or DEMO candidate; no PREREG_DRAFT.**

- **LIVE is impossible for this mechanism on the reachable sources, whatever the effect:** SHFE au / ag base-margin
  hikes run at ~4.7 trades a year in VAL (8.5 in IS, inflated by silver's 2020 limit days), on ~3 dates a year. HOLD
  would hold ~8 trades, so LIVE needs a per-trade net Sharpe >= ~1.06. SGE's holiday hikes give the same dates.
- **No cell reaches the DEMO bar** (IS t >= 2): 17 declared cells; the best IS net t on the declared side is +1.31
  (M-C2: fade the side SHFE clients added over 20 days, h1, VAL +21.6 bp, t 0.53), then +1.21 (M3 holiday-routine
  hikes, h3, VAL -2.6 bp); the best-of-17 chance median is 1.74 (max |t| 2.05). The largest |t| is on the wrong
  side: M3 discretionary hikes h3, IS -246 bp (t -1.51).
- **What the data say about the mechanism:**
  - Holiday-routine hikes (announced ~5 days ahead, two trading days before a closure): no price effect in any era
    on the declared side (fade the 20-day trend): IS h1 -8.1 bp (t -0.40), VAL +2.7 (t 0.04), PRE (SGE 2008-13) h1
    +7.3 (t 0.30). The pressure window into the effective settlement (M1p) is negative in all three eras (-10 to
    -12 bp, |t| <= 1.3). This matches Hedegaard (2011/2014): open interest falls, prices do not move.
  - Discretionary hikes are mostly the exchange's automatic response to a limit-locked close (silver 2020: one-day
    hikes that revert the next day). After them the move **continued**: fading the 20-day trend lost -169 bp at h1 in
    IS (t -1.26; worse than 100 % of random entries). This is the big-move-day momentum the earlier rounds already
    know, and it is too rare (13 IS, 7 VAL trades) to make a rule from it, post hoc.
  - Post-holiday restores (M2, with the crowded side): IS -19 bp (t -0.69), VAL +39 (t 1.81): sign flips.
- **CME performance-bond history is not reachable** without paid data (details in Sources). That was the only
  source where the count (~60-120 product-events a year) would allow LIVE at all.

## Sources and spans
| source | fetched | span used | notes |
|---|---|---|---|
| SHFE daily contract trade parameters `https://www.shfe.com.cn/data/busiparamdata/future/ContractDailyTradeArgument{YYYYMMDD}.dat` (JSON: per contract spec / hedge long / short margin ratio, upper / lower limit, `UPDATE_DATE`) | 3,121 requests, 2013-06..2024-12 weekdays; 2,821 files (2,733 non-empty trading days) + 199 404s; earliest file 2013-07-15 (earlier dates 404); 2 files (2013-10-16/17) not JSON | 2013-07-15..2024-12-31; base margin = median spec-long ratio excluding the 2 nearest expiries | new to the repo (0 hits before). Covers 18 products (au ag cu al zn pb ni sn rb hc ru bu fu wr ...); INE (sc) is not in it |
| SGE announcements `https://www.sge.com.cn/jjsnotice?p=N` + notice pages | 138 listing pages (1,376 notices 2002-06..2026-10), 173 margin / risk notices opened (all <= 2024-12-31) | holiday hikes 2008-09..2024-12: 57 dates with stated effective settlement day and notice day | conditional limit-lock notices (2011-13) not used: whether they took effect is not in the text |
| SHFE member rankings `…/dailydata/pm{YYYYMMDD}.dat` (round 34's source) | 79 file days 2016-24 (the day before each hike and 20 trading days earlier; 17 timeouts, all retried OK) | 2016-01..2024-12 | 2016 files have no `<p>all` row: summed per contract |
| Unusable: CME performance bonds | cmegroup.com (brief: timeout), ftp.cmegroup.com (URLError, 1 try); web.archive.org CDX worked once (snapshots of `historical-margins.html` 2011-01-10, 2012-08-06), then every fetch got 429 / 503 and "flagged as suspected abusive bot traffic" for this IP: stopped after 6 requests | none | CME's history is DataMine (licensed); Hedegaard and Abruzzo & Park used FOIA data, not posted; no GitHub / Zenodo / figshare / Mendeley / openICPSR copy (2 searches) |
| Unusable: SHFE notice list API (`POST /api/search/`, docchannel 2384) | 2 tries, URLError | none | the margin dates come from S1 itself, so the notices were only needed for the announcement clock; SGE's notice dates were used for M1a |
| Related triggers checked for count only | ESMA CFD caps (2018-08-01) and national renewals, FCA 2019-08-01, ASIC 2021-03-29, JFSA 25x (2011-08-01); Binance / FTX / Bybit max-leverage cuts (2021-07-19 / 25); JSCC Nikkei 225 extraordinary SPAN reviews (big-move-day triggered, a few a year) | none | a handful of dates each in a decade: neither bar is reachable; JSCC's are big-move days (tested in many rounds) |

Request log: scratchpad `r37/M/web/requests.log` (3,538 lines: SHFE 3,224 incl. 99 ranking-file requests and 2 POSTs, SGE 307, archive 6, CME FTP 1).

**Effective clock.** SGE notices say "自 E 日收盘清算时起 ... 保证金比例从 x% 调整为 y%": the new ratio applies from
the settlement of E. The SHFE file of day D lists the ratio in force during trading day D, set at the settlement of
the previous day (checked on 2014-01, 2016-02 and 2020-01 against SGE's dates; amendment 2). So E = the file day
before the first file with the new ratio. t0 = 07:00 UTC on E (SHFE day close 15:00 Beijing) for M1 / M2 / M3 /
M-X / M-C; 07:30 UTC (SGE close) for M4; M1p 01:00-07:00 UTC on E; M1a from the SGE notice day 08:00 UTC to E 07:00.

## Power before the numbers (amendments 1-2)
- SHFE au + ag hikes: IS 51 trades on 31 dates, VAL 14 on 9; SGE holiday hikes IS 17 dates, VAL 10, PRE 23.
- HOLD ~8 trades at the VAL rate: LIVE needs per-trade net Sharpe >= ~1.06. Out of reach by count.
- DEMO: IS t >= 2 on ~31 clusters needs ~30 bp net per gold trade at h1 (IS sd 84 bp) or ~60 bp for silver (sd 168).

## Results
Net and mid in bp per trade; t clustered by event date (au and ag on one date = one cluster). Cost = half spread at
entry and exit minute + 0.6 bp commission + swap; PRE adds 0.6 bp and uses IC 2016-17 spreads by minute on
Dukascopy prices. "pow" = per-trade net Sharpe x sqrt(1.73 x trades per year) on that era's size. "rand" = share of
300 random-entry seeds (same symbols, clock and hold, random weekday in the era, side recomputed from the 20-day
trend at the random time) whose mean net is below the cell's. Full lines incl. spread x1.5, +1 minute and ex-2020-03/04
in `r37/M/out/run1.log`.

| hypothesis (side) | cell | eras | mid IS (t) / VAL (t) | cost IS / VAL | net PRE (t) | net IS (t) | net VAL (t) | VAL / IS | shp, pow IS / VAL | rand IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 all au / ag hikes, fade 20-d trend | h1 | PRE IS VAL | -44.8 (-1.12) / +35.4 (0.89) | 4.0 / 3.0 | +61.0 (0.83) | -49.1 (-1.23) | +32.6 (0.81) | < 0 | -0.21, -0.79 / +0.26, 0.74 | 0.01 / 0.82 | none |
| M1 | h3 | | -32.4 (-0.62) / +54.5 (0.80) | 6.3 / 5.4 | +15.4 (0.16) | -39.6 (-0.76) | +50.1 (0.73) | < 0 | -0.12, -0.47 / +0.24, 0.69 | 0.10 / 0.75 | none |
| M1 | h5 | | -15.3 (-0.24) / +53.7 (0.65) | 5.3 / 4.1 | +2.2 (0.02) | -21.8 (-0.35) | +51.3 (0.61) | < 0 | -0.06, -0.21 / +0.20, 0.56 | 0.28 / 0.71 | none |
| M1p pressure into the settlement | 01-07 UTC on E | | -6.2 (-0.38) / -8.8 (-0.26) | 3.8 / 3.2 | -12.5 (-1.28) | -10.0 (-0.62) | -11.9 (-0.36) | | -0.09 / -0.11 | 0.18 / 0.20 | none |
| M1a from the SGE notice | notice 08:00 -> E 07:00 | | +38.6 (0.97) / -9.4 (-0.11) | 3.1 / 2.8 | +5.6 (0.10) | +34.8 (0.88) | -15.1 (-0.17) | < 0 | +0.21, 0.58 / -0.07 | 0.71 / 0.42 | none |
| M2 cuts (restores), with the trend | h1 | | -14.8 (-0.53) / +45.8 (2.14) | 4.2 / 5.7 | +13.0 (0.56) | -19.2 (-0.69) | +39.1 (1.81) | < 0 | -0.10 / +0.55, 1.57 | 0.19 / 0.88 | none |
| M2 | h3 | | -9.6 (-0.22) / +7.5 (0.12) | 6.5 / 6.1 | +45.1 (0.82) | -17.1 (-0.40) | -0.8 (-0.01) | | -0.06 / -0.00 | 0.35 / 0.63 | none |
| M3 holiday-routine hikes | h1 | | -4.5 (-0.22) / +7.2 (0.11) | 3.2 / 2.9 | -3.9 (-0.17) | -8.1 (-0.40) | +2.7 (0.04) | < 0 | -0.08 / +0.02 | 0.40 / 0.55 | none |
| M3 holiday-routine | h3 | | +37.3 (1.43) / +6.6 (0.06) | 5.2 / 6.7 | -59.0 (-1.00) | **+31.1 (1.21)** | -2.6 (-0.02) | < 0 | +0.22, 0.73 / -0.01 | 0.83 / 0.48 | none |
| M3 discretionary hikes | h1 | | -162.6 (-1.20) / +63.6 (1.18) | 6.2 / 3.0 | n 1 | -169.0 (-1.26) | +62.5 (1.18) | < 0 | -0.39 / +0.48, 0.96 | 0.00 / 0.87 | none (wrong side in IS) |
| M3 discretionary | h3 | | -236.0 (-1.45) / +102.3 (1.25) | 9.7 / 4.0 | n 1 | -246.3 (-1.51) | +102.9 (1.26) | < 0 | -0.44 / +0.54, 1.09 | 0.00 / 0.89 | none (wrong side in IS) |
| M4 SGE holiday hikes, PRE only | h1 | PRE | | | +7.3 (0.30), mid +11.2 | | | | +0.05 | 0.77 | none |
| M4 | h3 | PRE | | | -21.4 (-0.50), mid -16.9 | | | | -0.08 | 0.53 | none |
| M-X SHFE cu hikes -> AUDUSD | h1 | | -4.4 (-0.20) / -16.2 (-1.11) | 1.1 / 1.0 | +32.3 (1.04) | -6.3 (-0.29) | -18.5 (-1.27) | | -0.06 / -0.45 | 0.36 / 0.20 | none |
| M-X | h3 | | -9.8 (-0.29) / -18.7 (-0.99) | 4.2 / 4.7 | +53.4 (1.61) | -15.7 (-0.47) | -25.6 (-1.39) | | -0.10 / -0.49 | 0.29 / 0.27 | none |
| M-C hikes, against SHFE client net OI level (always short: clients are net long every time) | h1 | IS VAL | +3.8 (0.09) / +72.7 (2.25) | 4.0 / 3.0 | | -0.0 (-0.00) | +71.9 (2.25) | n/a | -0.00 / +0.69, 1.95 | 0.67 / 0.99 | none (IS 0) |
| M-C2 hikes, against the 20-day change of client net OI | h1 | IS VAL | +54.6 (1.42) / +26.4 (0.66) | 4.0 / 3.0 | | **+50.3 (1.31)** | +21.6 (0.53) | 0.43 | +0.21, 0.79 / +0.17, 0.48 | 1.00* / 0.76* | none (IS t < 2) |

\* M-C / M-C2 random control keeps each event's side (the side comes from positioning, not price) and draws random
weekdays; it is more lenient than the trend-recomputed control of the other rows. M-C's VAL +71.9 is just "short gold /
silver after a 2022-24 hike" (14 trades, 9 dates); its IS is zero.

Era sizes: PRE for M1-M3 / M-X = SHFE 2013-07..2015 on Dukascopy (14 au / ag trades on 8 dates); M4 = SGE
2008-09..2013-07 (45 trades on 23 dates). Excluding 2020-03/04 changes no verdict (M1 h1 IS -32.1, M3 discretionary
h1 IS -113.4).

Breakdowns (out/trades_*.csv):
- M1 h1 IS by year: 2016 -21 (6), 2017 +64 (4), 2018 -34 (4), 2019 +12 (10), 2020 -111 (19), 2021 -62 (8); by symbol
  XAG -63.5 (29), XAU -30.1 (22). VAL: 2022 +192 (3), 2023 -86 (3), 2024 +17 (8).
- M3 discretionary IS: 11 of 13 trades are 2020 (silver one-day limit hikes in March and July-August 2020, gold
  2020-03-16 and 2020-08-12); VAL 7 trades (2022-03-09 gold, 2024 silver / gold).
- M1a IS by year is positive in 5 of 6 years (+32 XAU, +37 XAG per trade) but t 0.88, and VAL is -15.

## Cells and chance
17 declared cells (M1 3, M1p 1, M1a 1, M2 2, M3 4, M4 2, M-X 2, M-C 2); CME's C1 / C2 not run (no data). Best IS t
on the declared side +1.31 (M-C2), then +1.21 (M3 holiday h3), vs the best-of-17 null median 1.74 (p95 2.74); best |t| 1.51 vs median
2.05. The family is at or below chance.

## Why it fails, and what would change it
- The routine hikes are known a week or more ahead and are small (gold 6 % -> 8-9 %); SGE / SHFE speculators can
  post the cash; the global gold price is set in London / COMEX, where the Chinese holders are a small share. The
  forced cut, if any, is absorbed without a measurable move (Hedegaard's null).
- The discretionary hikes are endogenous to a limit move: they mark big-move days, after which the move tends to
  continue; that is momentum, not a margin effect, and too rare to register.
- A test with power needs CME product-level margin history (DataMine, licensed; or a FOIA request). Value estimate:
  low. Even at ~100 product-events a year, LIVE needs a per-trade Sharpe ~0.25, ~3x more than any margin effect in
  the literature (Hedegaard: none on prices); P(LIVE) ~1 %, P(DEMO) ~3 %.

## Files
- Scripts (scratchpad `r37/M/scripts/`): `fetch.py` (logged GET), `pull_shfe_tp.py`, `parse_shfe_tp.py`,
  `events.py` (LAG 1), `pull_sge_notices.py`, `parse_sge.py`, `sge_holiday_events.py`, `engine.py` (prices cut at
  2025-01-01), `run_cells.py`, `pull_pm.py`, `run_mc.py`, `shfe_search.py` (unused, API unreachable).
- Outputs (`r37/M/out/`): `shfe_base.csv`, `events_shfe.csv`, `sge_holiday_hikes.csv`, `run1.log`, `cells.txt`,
  `cells_mc.txt`, `trades_<cell>_<era>.csv`.
