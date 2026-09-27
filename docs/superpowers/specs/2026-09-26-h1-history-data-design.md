# Long-history H1 data for the research lab — Design

**Date:** 2026-09-26
**Status:** Approved in chat section by section, awaiting spec review
**Follows:** the 2026-09-26 diagnosis (memory `why-strategies-fail-2026-09`): on 1.8M lab trades the pre-cost
(mid-price) edge is ≈ 0 and costs are 0.02–0.4R per trade; 3.7 years of cTrader ticks are too short to prove a
realistic slow edge. This is step 1 of the follow-up: data only. The portfolio engine, strategies and pass bar
are step 2, with their own spec.

## Goal

Give `research/` 15–20+ years of hourly bid/ask bars for the 26-symbol IC Markets universe, plus a cost and
swap model that follows IC Markets' measured costs and historical interest rates, validated against the IC
ticks we already have for 2025–26.

Nothing here touches the cBots, the VPS, the production database or git history.

## Decisions taken in the brainstorm

| Question | Decision |
|---|---|
| Universe | 26 IC Markets symbols: the 15 lab symbols (no synthetic crosses) + NZDUSD USDCHF US500 JP225 AUS200 HK50 XAGUSD XPTUSD XTIUSD XBRUSD XNGUSD. All 11 new names confirmed on the IC demo account; their ticks 2025-01..2026-09-25 are in `research/data` |
| History source | Dukascopy datafeed (free, bid and ask) |
| Granularity | Monthly **H1** candle files, bid and ask. H1 is the stored base; H4 and D1 are aggregated from it on demand |
| Day boundary | 17:00 New York (DST-aware), as `research/lab/engine.build_d1_ny` does; one FX day = 6 H4 bars |
| Holding constraint (for step 2) | Max about 5 days per position, flat before the weekend, all symbols. Recorded here so the data covers it: H1 is enough |
| Historical swaps | Interest-rate differential per day + broker markup fitted to IC's 2026 swaps |
| Costs | IC Markets' measured spread and commission, never Dukascopy's spread |

## Probe results (2026-09-26)

- `EURUSD/2005/BID_candles_day_1.bi5`, `EURUSD/2005/00/BID_candles_hour_1.bi5`, `USA500IDXUSD/2015/05`,
  `GASCMDUSD/2016/05`, `HKGIDXHKD/2016/05` (ASK), `LIGHTCMDUSD/2012/00`, `BTCUSD/2018/00`: HTTP 200.
- `XPTUSD/2015/05`: 404.
- Latency 1–12 s per file; with a 20 s timeout several requests failed, with 90 s all answered.

## Components (new package `research/hist/`)

| File | Responsibility |
|---|---|
| `symbols.py` | IC symbol → Dukascopy instrument, price scale (points per unit), asset class, quote currency, first year with data. The mapping below is the starting point; the probe task confirms each name and first year |
| `dukascopy.py` | Download and decode monthly H1 candle files (`{INSTR}/{YYYY}/{MM-1:02d}/{BID,ASK}_candles_hour_1.bi5`). Raw files kept under `research/data/dukas/{INSTR}/{YYYY}/{MM}_{SIDE}.bi5`; a per-instrument `manifest.csv` records month, side, status (`ok`, `absent`, `error`), bytes, fetched-at |
| `build.py` | Decoded bid + ask months → one clean H1 array per symbol in `research/data/h1/{SYMBOL}.npz`; plus `bars(symbol, tf)` returning H1, H4 or D1 aligned to 17:00 New York |
| `rates.py` | Daily short-rate series per currency (USD EUR GBP JPY AUD CAD CHF NZD HKD) from FRED, cached as CSV in `research/data/rates/` |
| `costs.py` | Per symbol: spread by New York hour (median of IC ticks 2025–26), round-trip commission, and `swap(symbol, side, units, date)` from the rate model |
| `validate.py` | Dukascopy H1 vs IC H1 (bid, built from ticks) over 2025-01..2026-09 → pass/fail per symbol |
| `report.py` | Writes `research/results/hist/data_report.md` |

Starting instrument map (to confirm in the probe task):

| IC | Dukascopy | IC | Dukascopy |
|---|---|---|---|
| EURUSD GBPUSD USDJPY AUDUSD USDCAD NZDUSD USDCHF EURJPY GBPJPY AUDJPY | same name | US30 | USA30IDXUSD |
| XAUUSD | XAUUSD | USTEC | USATECHIDXUSD |
| XAGUSD | XAGUSD | US500 | USA500IDXUSD |
| XPTUSD | XPTUSD (404) → try alternatives, else drop | DE40 | DEUIDXEUR |
| XTIUSD | LIGHTCMDUSD | UK100 | GBRIDXGBP |
| XBRUSD | BRENTCMDUSD | JP225 | JPNIDXJPY |
| XNGUSD | GASCMDUSD | AUS200 | AUSIDXAUD |
| BTCUSD | BTCUSD | HK50 | HKGIDXHKD |
| ETHUSD | ETHUSD | | |

## Data flow

```
Dukascopy H1 bid/ask ─► data/dukas/ (raw .bi5 + manifest) ─► build.py ─► data/h1/*.npz ─► bars(sym, H1|H4|D1)
FRED short rates ─────► data/rates/*.csv ─► rates.py ─┐
IC ticks 2025-26 (have) ─► costs.py (spread by hour, commission) ◄─┘ swap model
IC ticks 2025-26 + data/h1 ─► validate.py ─► report.py ─► results/hist/data_report.md
```

## Download

- History from each instrument's first available year (not before 2003) to 2026-09-25.
- First year found by probing January of each year, oldest first, both sides.
- 4 concurrent requests, 60 s timeout, up to 5 retries with exponential backoff (2, 4, 8, 16, 32 s) on
  timeouts, 5xx and connection errors. 404 → `absent`, not retried.
- Resumable: files marked `ok` are skipped. The current month and the month before are always refetched.
- Estimated ~12,000 files, ~4–5 hours at 4 workers; runs in the background.

## Decoding and cleaning

- `.bi5` = LZMA-compressed records of 24 bytes, big-endian: int32 seconds from the month start, int32 open,
  close, low, high (price × scale), float32 volume. An empty file = no data.
- Price scale per instrument from `symbols.py`; `build.py` refuses a symbol whose decoded 2025–26 median price
  differs from the IC median by more than 20 % (catches a wrong scale before anything is saved).
- Flat candles with zero volume (Dukascopy's filler for closed hours) are dropped.
- Bid and ask joined on the hour; an hour missing one side keeps NaN for it.
- Output npz: `ts` (int64 ms UTC, hour open), `bo bh bl bc` (bid OHLC), `ao ah al ac` (ask OHLC), `vol`.
- Weekday gaps > 3 days are listed in the report, not filled.

## Aggregation

- H4 buckets start at 17:00, 21:00, 01:00, 05:00, 09:00, 13:00 New York; D1 = 17:00 → 17:00 New York,
  DST-aware per hour. Sunday-evening hours belong to Monday; no Saturday or Friday-stub bars.
- A bar carries bid OHLC, ask close and the number of H1 bars in it.

## Rates and swaps

- Series (to confirm in the rates task): USD `DFF` (daily), EUR `ECBDFR` (daily); GBP JPY AUD CAD CHF NZD HKD
  from the OECD immediate/call-money monthly series on FRED (`IRSTCI01{CC}M156N`), stepped to daily. A
  currency without a series falls back to its central-bank policy rate, flagged in the report.
- FX, per unit per rollover, in quote currency:
  long = price × (r_base − r_quote − m_long) / 360, short = price × (r_quote − r_base − m_short) / 360.
- Indices: long = −price × (r_ccy + m_long) / 360, short = price × (r_ccy − m_short) / 360.
- Metals: as indices with the USD rate.
- Energies (XTI XBR XNG) and crypto (BTC ETH): swap rates of 2026 held constant (their financing follows
  futures curves / exchange funding, not a policy rate), flagged as approximate.
- Markups `m_long`, `m_short` fitted per symbol so the model reproduces IC's 2026 swaps: for the 15 lab symbols
  the fitted `research/specs.SWAPS`; for the 11 new symbols IC's published swap table (recorded in
  `symbols.py` with the date it was read). Triple rollover day as in `research/specs.py`.
- Swaps are converted to USD with the conversion pair's H1 close of that day.

## Costs

- Spread: per symbol, median IC spread for each New York hour of the week (ticks 2025-01..2026-09), applied to
  every year. Earlier years' real spreads were probably wider, so costs before 2015 are optimistic; the report
  says so.
- Commission: FX and metals $30 per million USD notional per side (as `research/lab/universe`); indices,
  energies and crypto none.

## Validation (pass/fail per symbol)

Over 2025-01..2026-09, Dukascopy H1 bid close vs IC H1 bid close built from ticks:

1. Correlation of hourly log returns ≥ 0.98 on the common hours.
2. Timing: that correlation at lag 0 is higher than at ±1 h (catches a timezone or DST error).
3. Coverage: ≥ 95 % of IC's trading hours have a Dukascopy bar.
4. Level offset (median and spread of close_duka − close_ic) reported, not judged: index and energy CFDs of two
   brokers can sit on different bases.

A symbol that fails is left out of step 2 and listed with the reason.

## Error handling

- Network: retries as above; a month still failing after the retries stays `error` in the manifest, the run
  finishes, and the report lists it. Rerunning fetches only non-`ok` months.
- Missing instrument (all 404): symbol marked unavailable, run continues.
- FRED unreachable: rates task fails loudly; swaps are never silently zero.

## Tests (`research/tests/hist/`)

- Decoder on a synthetic `.bi5` fixture built with `lzma` in the test (known records in, same numbers out).
- Month offsets: `{MM-1:02d}` path, last-day-of-month hours, leap years.
- Aggregation: H4/D1 boundaries at 17:00 New York on both sides of the March and November DST switches; no
  weekend bars.
- Cleaning: zero-volume flat candles dropped; one-sided hours keep NaN.
- Swap model reproduces the 2026 IC swaps it was fitted on (within 1 %).
- Downloader: resume skips `ok`, retries on timeout, marks 404 `absent` (HTTP mocked).
- Validation metrics on synthetic series with a known lag/offset.

## Deliverables

1. `research/hist/` package + tests.
2. `research/data/dukas/`, `research/data/h1/`, `research/data/rates/` (local only, git-ignored).
3. `research/results/hist/data_report.md`: per symbol first year, hours, gaps, validation result, level
   offset, spread by session, commission, swap markups and 2026 fit error.

## Out of scope (step 2)

Portfolio engine, strategy rules, position sizing, the pre-registered pass bar, and the ≤ 5-day /
flat-before-weekend rule.
