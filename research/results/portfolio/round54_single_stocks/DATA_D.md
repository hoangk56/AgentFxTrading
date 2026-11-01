# Round 54 stream D: data and cost model (2026-10-30)

No hypothesis was tested here. Files live in the scratchpad (git-ignored):
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/D/`
(`out/` holds stocks_daily.npz, symbols.csv, splits.csv, stocklib.py, READY and the request logs; `code/` holds
meta.py, fetch.py, splits_sec.py, build.py, summary.py and smoke.py; `cache/` holds the raw .bi5 files).

## Sources and robots
- **Instrument list:** the dukascopy-node 1.51.1 npm bundle via unpkg.com. unpkg's robots.txt has an explicit
  `User-agent: ClaudeBot / Allow: /`. github.com disallows ClaudeBot, so it was not used. The bundle lists 615 US
  `*ususd` CFDs. By first daily candle: 1 from 2016, 192 from 2017, 70 from 2018, 13 from 2020, 313 from 2022, 26 from
  2023-24. The 263 names that start before 2019 were pulled.
- **Prices:** `datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{BID|ASK}_candles_day_1.bi5`, with SYM = key in upper
  case (e.g. AAPLUSUSD). robots.txt answers 404, so nothing is disallowed. This is the browser User-Agent exception
  the user approved. 4,070 year files over 2016-2024, no 2025/2026 request, ~20 min at 10 threads plus a 6-min retry.
  503 is often transient: 47 files that got four 503s in a row all came back on the retry. Every file exists. LZMA
  '>5if' records, offsets in whole days from 1 Jan UTC, **price scale 1e3**. Checked: AAPL 2018-01-02 bid o/c
  170.138 / 172.198, KO 45.54, MSFT 2024-12-31 421.12. Zero-volume flat days are dropped.
- **SEC:** a local copy of `company_tickers.json` (from round 42). Split facts came from
  `data.sec.gov/api/xbrl/companyconcept/CIK…/us-gaap/StockholdersEquityNoteStockSplitConversionRatio1.json` (225
  CIKs, 39 with facts, 0.2 s spacing, generic research UA, no email). data.sec.gov robots.txt answers 404. The
  www.sec.gov robots.txt returned the rate-threshold page to the generic UA, so www.sec.gov was not used.
- **IC:** `cdn.ic.com/uploads/FSA/Stocks-Product-Specification-Sheet.pdf` fetched with the generic UA (HTTP 200).
  cdn.ic.com/robots.txt is an S3 AccessDenied, not a bot wall. www.ic.com and www.icmarkets.com did not answer
  (timeout), so they were not retried.
- **Rates:** local `research/data/rates/DFF.csv` (FRED EFFR).

## Coverage (`stocks_daily.npz`)
263 names: 221 stocks and 42 ETF/ETN funds (`is_etf`), including SPY (from 2017-02-16), QQQ, IWM and DIA (hedge
legs on the same clock). The grid has 2,063 trading days from 2016-09-26 to 2024-12-31, cut at parse. Names per day:
1 in 2016, median 101 in 2017, all 263 from 2018 on. **So IS (2016-21) is in practice 2017-21, and 2018-21 for the
full list.** 676 name-days are missing inside the names' spans, out of 485,954. All 221 stocks have a CIK. 11 were
mapped by hand because the current SEC file has the new tickers or lacks the name: FB→1326801, PCLN→1075531,
HCN→766704, CTL (Lumen)→18926, GPS→39911, K→55067, AVB, BK, EA, IPG, FOXA = 21st Century Fox 1308161 (to 2019).
**Tickers are Dukascopy's old names.** APA maps to the 2021 holding CIK 1841666 (Apache 6769 before 2021).

## Splits
Dukascopy CFD prices are **not split-adjusted**: AAPL drops 4:1 on 2020-08-31 in the raw data. The detector flags
any overnight move (previous close to open) above 40 %. It counts as a split when one of these holds:
- an SEC split fact matches within 8 % and was filed within 500 days;
- the ratio is >= 2 and within 2 % of a round ratio (5 % for funds);
- it is on a manual list, which holds one entry: PCAR 3:2 on 2023-02-08.

3:2-like moves happen in crashes (APA, DVN, EOG and OXY on 2020-03-09; LUMN on 2024-08-06), so a 1.5 ratio alone is
not enough. Result:
- **31 splits / reverse splits**, adjusted through `adj`, 24 of them SEC-corroborated: AAPL, TSLA x2, NVDA x2, AMZN,
  GOOG(L), AVGO, CMG, WMT, LRCX, GE 1:8, VXX 1:4 x4, USO 1:8, XOP 1:4, and others.
- **21 other jumps**, left unadjusted and flagged per trade (`jump`): spin-offs EQT 2018-11-13 and EXC 2022-02-02,
  NFLX and SNAP earnings, PCG, BIIB, ITUB 2018-11-28 (possibly a bonus issue), and the VXX spike of 2024-08-05.

Spin-offs are not adjusted, so a hold across one shows a fake loss. Exclude `jump` trades.

## IC MT5 cost model (stocklib defaults)
IC FSA sheet (Last-Modified 2026-09-01): US shares (.US/.NAS/.NYSE, also -24 versions) cost **USD 0.02 per share per
side**, lot = 1 share, min 0.1, **max 1000 shares per order / volume limit 1000**, tick 0.01, leverage 1:5-1:20,
spread variable. Dividend adjustments are credited to longs and debited from shorts. The sheet has **no symbol list**
(it says ">700 stocks" on NASDAQ / NYSE / ASX), so the IC overlap with these 263 names **cannot be verified offline**.
Assume the large US caps are listed, and check the MT5 symbol list before any PREREG.
- Fills: long buys at the ask and sells at the bid (short mirrored). `spread_mult` widens the half-spread around mid
  (1.5 for the stress test).
- **Spread proxy:** the Dukascopy bid/ask of the traded candle. Per-name median close spread is 7.3 bp round trip
  (p10 4.9, p90 11.2). By year, the median close spread was 2.8 bp in 2017, 9.9 in 2022 and 7.1 in 2024. **The open
  spread is the first quote of the session, median 65 bp** (p10 23, p90 116). That is probably far wider than IC a
  minute after the open. `open_spread="close"` charges the closing spread at every fill as the optimistic bound.
  Report both for open entries.
- Commission: 0.02 / raw price per side, with the share count scaled across splits. That is 2.2 bp per side at the
  median price ($90) and >= 20 bp per side under $10 (ABEV $3 ≈ 67 bp).
- Financing per calendar night held (Fri→Mon = 3): long pays (EFFR + 3 %)/360, short pays (3 % − EFFR)/360, which is
  a credit when EFFR > 3 % (2023-24). EFFR is the value on the entry date.
- Check of the cost model: random 3-day longs, open to close, average gross +20 bp, spread 36 bp, commission 8 bp,
  financing 6 bp, net −30 bp.

## stocklib API
In `out/stocklib.py`, numpy only. Add that directory to `sys.path`.
- Loading and lookup: `S = sl.load()`, `S.idx(ticker|sym|cik)`, `S.day(date)`, `S.px(field, adjusted=True)`,
  `S.mid(at)`, `S.spread_bp(at)`, `S.valid()`, `S.is_etf`, `S.info[col]`, `S.max_notional(i, d)`.
- Trades: `S.trade(sym_i, entry_d, side, exit_d, entry_at, exit_at, spread_mult, hedge="SPY"|"QQQ", beta,
  open_spread)`. It returns net / gross / spread / commission / financing in bp, plus nights, `ok` and `jump`.
- Statistics: `sl.clustered_t(x, cluster)` (cluster = entry day), `sl.by_year`, `sl.period` (IS ≤ 2021, VAL),
  `sl.ex_covid`, and `sl.random_control` (same dates and side, random non-ETF firms with quotes on both days).

## Pitfalls
1. **Dividends are missing.** Prices drop on ex-dates and IC pays or charges the dividend. Short holds across an
   ex-date look better than they are, and long holds look worse, by roughly the quarterly yield (0.2-1 %). About
   8 % of 5-day holds cross an ex-date. Report the side bias, or drop event windows that contain an ex-date if a
   stream has ex-dates.
2. **Opening spreads:** see above. The day candle's open is the first quote of the regular session (AAPL
   2018-01-02 bid open 170.14 vs the official 170.16), not a mid-auction price.
3. **Survivorship:** the list is today's Dukascopy list of names that existed before 2019. Delisted firms are missing,
   and the names are large caps chosen in 2017-18.
4. **Hedge leg:** use SPY or QQQ from the same file rather than US500, so both legs fill at the same time.
5. `ok` needs quotes only on the entry and exit days. A missing day inside the hold is not caught (676 such
   name-days in total). A random-entry control with `pool=None` draws stocks only.
6. Intraday (H1 / M1) probes for stocks got 503 after the bulk pull, so they were not pursued. Session hours were not
   checked beyond the daily candle.
