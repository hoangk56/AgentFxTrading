# Round 63 stream S: overnight vs intraday returns of US large caps, executed in the auctions

Hypotheses: [HYPOTHESES_S.md](HYPOTHESES_S.md) (written 2026-10-31 14:32 UTC, before any return). Code: `code/`
(`build_panel.py`, `onlib.py`, `run.py`, `nulls.py`, `us500_check.py`, `checks*.py`). Outputs: `out_cells.json`
(every cell x era x cost, years), `out_nulls.json`, `out_books.npz` (daily gross books). HOLD stayed closed: the
source ends 2024-03-11 and the loader asserts `dates < 2025-01-01`; two probe files of other datasets that ran into
2025-26 were deleted after reading only their schema / min-max date / first 3 rows of 2010 (logged in requests.log).
Finished 2026-10-31 14:46 UTC.

## Answer
**None: no LIVE or DEMO candidate, no PREREG_DRAFT.** All 8 cells are net negative in IS and VAL at the declared
auction cost (2.5 bp per side per name). The literature effects exist in the top-200 S&P 500 names but are
2-6 bp per day gross since 2016, below the 10 bp a dollar-neutral overnight-only (or intraday-only) book pays every
day:
- Overnight persistence (Lou-Polk-Skouras clientele effect; X1c, 252-day mean overnight return, long top / short
  bottom 20, close -> open): gross +13.7 bp / day PRE (t 15.4), **+5.6 IS (t 3.31), +5.8 VAL (t 1.60)**; net -4.6
  (t -2.69) / -4.4 (t -1.23). The same names lose -6.0 / -6.6 bp on the next intraday leg (the tug of war is real), so
  close-to-close it is ~0. Break-even cost 1.4 bp per side; **even at zero cost its annual Sharpe is 1.2 IS / 1.1 VAL,
  HOLD power at VAL size 1.45 < 3**, so LIVE is out of reach at any cost.
- Aggregate overnight drift (B1, EW basket of the 200 names, SPY proxy): gross +6.0 bp / night IS (t 2.80), **-0.3
  VAL**; net of 5 bp cost and the cash rate +0.6 IS (t 0.29), -6.7 VAL (t -2.60).
- Momentum overnight (X2), momentum intraday reversal (X3), intraday reversal of the previous overnight (X4a/b): gross
  0-8 bp, net -2.5 to -13.6 in every era, never net > 0 in IS.

## Data
- stooq.com is out: its robots.txt is `User-agent: * / Disallow: /` (only Googlebot / Bingbot). Nothing was requested
  beyond robots.txt.
- Used: Hugging Face `jwigginton/timeseries-daily-sp500` (Yahoo-style daily O/H/L/C split-adjusted, adj_close,
  volume; 503 S&P 500 members as of 2024-03-11; 1980..2024-03-11) and `jwigginton/index-constituents-sp500`
  (date_added). huggingface.co robots.txt `Allow: /`. Files in research/data/stooq/ (raw_jwig/, raw_jwig_const/,
  panel_sp500.npz, requests.log). Parquet read with duckdb from another local venv (`106.dnse-stock/.venv`, `-I`),
  analysis in research/.venv (numpy).
- Universe: each day the top 200 by 63-day median dollar volume (through t-1) of names already in the S&P 500
  (date_added <= t), price >= USD 5. Median 200 names every era.
- Dividends from the adj-factor (d_t = 1 - f_{t-1}/f_t, rounding noise < 1e-5 set to 0): ~3 ex-dates per name-year,
  credited to the overnight leg.
- Open quality: the EW basket overnight return vs the IC US500 CFD mid 15:59 -> 09:30 New York (1,908 nights
  2016-24) correlates **0.972** (means 5.6 vs 3.7 bp: EW vs cap weight). Yahoo opens before 2008 often equal the
  previous close (12-15 % of name-days 2003-06 vs 2-3 % later): those name-days are dropped before 2008.
- Eras: PRE 2004-2015 (declared extra), IS 2016-2021, **VAL 2022-01-03..2024-03-11 (548 sessions, the source ends
  there)**.

## Cells (bp per day, book = USD 1 long + USD 1 short; net at 10 bp cost + 0.5 %/yr borrow; t Newey-West lag 5)

| cell | leg | PRE gross (t) | IS gross (t) | IS net (t) | VAL gross (t) | VAL net (t) | IS x1.5 / x2 / late | VAL x1.5 / x2 / late |
|---|---|---|---|---|---|---|---|---|
| X1a on-mean 21 d, long high | close->open | +8.29 (9.57) | +0.87 (0.42) | -9.33 (-4.44) | -1.48 (-0.46) | -11.68 (-3.60) | -14.3 / -19.3 / -9.3 | -16.7 / -21.7 / -12.6 |
| X1b on-mean 63 d | close->open | +11.08 (12.14) | +2.87 (1.56) | -7.34 (-4.00) | +0.55 (0.18) | -9.65 (-3.20) | -12.3 / -17.3 / -7.0 | -14.7 / -19.7 / -10.8 |
| X1c on-mean 252 d | close->open | +13.74 (15.36) | +5.63 (3.31) | -4.57 (-2.69) | +5.76 (1.60) | -4.44 (-1.23) | -9.6 / -14.6 / -4.8 | -9.4 / -14.4 / -3.6 |
| X2 12-1 momentum, long winners | close->open | +2.48 (2.07) | +0.11 (0.04) | -10.09 (-3.58) | +7.67 (1.74) | -2.53 (-0.58) | -15.1 / -20.1 / -10.2 | -7.5 / -12.5 / -1.4 |
| X3 12-1 momentum, short winners | open->close | +2.10 (0.89) | +4.79 (1.41) | -5.21 (-1.54) | +4.92 (0.73) | -5.08 (-0.75) | -10.2 / -15.2 / -5.4 | -10.1 / -15.1 / -4.9 |
| X4a prev. overnight, short high | open->close | +5.50 (2.71) | +2.98 (0.97) | -7.02 (-2.29) | +3.17 (0.50) | -6.83 (-1.07) | -12.0 / -17.0 / -8.6 | -11.8 / -16.8 / -10.7 |
| X4b prev. 21 d on-mean, short high | open->close | +9.33 (7.15) | +5.90 (2.31) | -4.10 (-1.60) | -3.64 (-0.87) | -13.64 (-3.27) | -9.1 / -14.1 / -4.4 | -18.6 / -23.6 / -12.9 |

PRE net (10 bp): X1c +3.54 (t 3.96), X1b +0.88, every other cell < 0.

B1 (EW basket long close -> open, 5 bp cost, minus Fed funds x nights / 360):

| era | gross (t, ann. SR) | gross - cash | net (t) | net x1.5 / x2 | intraday leg gross (t) |
|---|---|---|---|---|---|
| PRE | +2.89 (2.71, 0.65) | +2.86 | -2.14 (-2.01) | -4.64 / -7.14 | +2.45 (1.38) |
| IS | +6.02 (2.80, 1.12) | +5.63 | +0.63 (0.29) | -1.87 / -4.37 | +1.37 (0.73) |
| VAL | -0.31 (-0.12, -0.07) | -1.74 | -6.74 (-2.60) | -9.24 / -11.74 | +3.37 (0.91) |

The "overnight drift" is weak in this sample: the intraday leg is also positive in PRE and VAL, and VAL's whole
return came intraday.

## Years (net bp / day)

| year | X1c | X1b | X2 | X4b | B1 net |
|---|---|---|---|---|---|
| 2016 | -5.89 | -8.90 | -8.25 | -4.65 | -4.53 |
| 2017 | -0.82 | -4.08 | -2.66 | -5.44 | +0.94 |
| 2018 | -5.08 | -9.70 | -3.66 | -10.66 | -1.35 |
| 2019 | -8.22 | -13.22 | -11.07 | -12.08 | +1.06 |
| 2020 | -5.63 | -3.10 | -27.88 | +5.83 | +3.80 |
| 2021 | -1.74 | -5.02 | -6.91 | +2.31 | +3.84 |
| 2022 | -0.67 | -8.46 | +1.81 | -16.18 | -8.99 |
| 2023 | -8.96 | -14.49 | -9.19 | -14.12 | -5.00 |
| 2024 (to 03-11) | -0.58 | +9.72 | +9.71 | +2.16 | -4.01 |

X1c is net positive in 9 of 12 PRE years and 0 of 9 IS / VAL years. Gross X1c by era fell from +13.7 to +5.6 bp
after 2015 (decay around the publication of the overnight / intraday literature; PRE opens are also noisier and
PRE survivorship heavier, so the PRE level is an upper bound).

## Random benchmark and max-over-cells null
Random books: 20 random long / 20 random short names from the same day's universe, same leg and cost, 1,000 draws
per cell (random net ~-10.0 to -10.3 bp in every era). Max-over-cells null: |IS gross t| of 7 independent random
books, max over cells, 200 draws: p50 1.65, p90 2.41, **p95 2.71**.

| cell | beat random (net) PRE / IS / VAL % | IS gross t | p of max-null |
|---|---|---|---|
| X1a | 100 / 86.6 / 16.2 | 0.42 | 1.00 |
| X1b | 100 / 99.9 / 64.9 | 1.56 | 0.58 |
| X1c | 100 / 100 / 99.9 | 3.31 | **0.015** |
| X2 | 100 / 55.3 / 100 | 0.04 | 1.00 |
| X3 | 99.7 / 100 / 99.0 | 1.41 | 0.68 |
| X4a | 100 / 99.7 / 93.8 | 0.97 | 0.95 |
| X4b | 100 / 100 / 2.7 | 2.31 | 0.14 |

As round 56 noted, beating random books is easy for a dollar-neutral book (the null pays the same cost on zero
gross). Only X1c's gross effect survives the max-over-cells null (p 0.015) and stays in VAL (beats 99.9 % of random
books), so the overnight-persistence effect is genuine; it is the cost, and the low Sharpe, that fail.

## Power and break-even (HOLD ~460 sessions; LIVE needs net annual Sharpe >= 2.22)

| cell | power at VAL size, net | at zero cost | break-even cost per side IS / VAL (bp) |
|---|---|---|---|
| X1a | -3.10 | -0.39 | 0.22 / < 0 |
| X1b | -2.78 | 0.16 | 0.72 / 0.14 |
| X1c | -1.12 | 1.45 | 1.41 / 1.44 |
| X2 | -0.53 | 1.59 | 0.03 / 1.92 |
| X3 | -0.68 | 0.66 | 1.20 / 1.23 |
| X4a | -1.11 | 0.52 | 0.75 / 0.79 |
| X4b | -2.79 | -0.75 | 1.47 / < 0 |
| B1 (excess over cash) | -2.14 | -0.55 | 2.82 / < 0 |

No cell reaches power 3 even with free execution: the best zero-cost annual Sharpe in VAL is ~1.2.

## What failed and why
- The effects are real at mid but small in the 200 most liquid names: an overnight-only or intraday-only book turns
  over 100 % twice a day, so a dollar-neutral book pays 4 auction fills per name-pair per day (10 bp at 2.5 bp per
  side). The best spread (X1c) is 5.6 bp.
- Combining the overnight leg with the opposite intraday leg (tug of war, ~+11.6 bp / day gross for X1c in IS) doubles
  the traded notional at every auction (20 bp / day): worse, not tested as a cell (not declared).
- The overnight drift of the US market (B1) did not exist in VAL 2022-24 in these names (-0.3 bp / night).

## Pitfalls
- stooq.com disallows every bot except Google / Bing in robots.txt (2026-10-31): do not use it.
- Hugging Face stock datasets often contain 2025-26 rows (younginpiniti / vessel888 / AYUSHKHAIRE end 2026): filter at
  parse or pick a file that ends before 2025. jwigginton ends 2024-03-11, so VAL here is 2.2 years and 2024-03..12 is
  not covered.
- Survivorship: the 503 names are 2024 survivors. date_added removes pre-inclusion run-ups, but delisted / removed
  firms are missing (worst in PRE). The bias mostly lifts long-only levels (B1), less the dollar-neutral spreads.
- Yahoo opens before 2008 are often the previous close (fills); Yahoo's open is the consolidated open, not necessarily
  the official auction print (US500 cross-check corr 0.97 at the basket level; name-level error unknown).
- Dividends must be added to the overnight leg (ex-dates fall between close and open); without them high-yield names
  look like persistent overnight losers and an X1 sort becomes a dividend sort.
- No SPY / QQQ / IWM in the free files: the basket proxy stands in for SPY's auction-to-auction drift.

## What a user decision could unlock
| direction | value |
|---|---|
| Paid CRSP / official auction prints with delisted names, incl. mid / small caps (where LPS effects are 3-10x larger) | LIVE ~1-2 % (auction impact in small caps is far above 2.5 bp), DEMO ~3 % |
| A venue with near-zero auction cost (< 1 bp per side, e.g. a market maker's own book) | X1c becomes net +1-2 bp / day but power at zero cost is 1.45: DEMO ~3 %, never LIVE |
| Futures overnight (ES / NQ) at ~0.3 bp per side | B1 VAL gross < 0: < 1 % |
