# Round 35, stream O: listed-option volume (OCC, CBOE put/call by class) and ETF short volume (FINRA)

Written 2026-10-28 from 02:30 UTC (`date -u`). Hypotheses with their UTC times are in
[HYPOTHESES_O.md](HYPOTHESES_O.md): O1-O6 (116 cells) declared 01:33 UTC before any return; addendum 1 (O7, 72 cells)
declared 02:19 UTC after the O1-O6 numbers and before any FINRA file was downloaded. Bars: research/PROMPT.md (LIVE /
DEMO, no RELAXED). HOLD (2025-01-01..2026-09-24) stayed closed: every download was requested for dates <= 2024-12-31
(the OCC daily files are monthly, the last requested month 2024-12; FINRA and CBOE per day to 2024-12-31), every parser
drops rows >= 2025, every IC / Dukascopy load is cut at ts < 1735689600000. SPX closes were read from round 32 V's
raw CBOE file and cut at parse. No 2025-26 value was printed. Probe disclosure: one OCC probe returned SPY volume by
account type for 2024-11-01 (pre-HOLD; its format is shown below).

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- **The OCC per-underlying data the brief asked for is not usable.** The volume query does give daily call / put
  volume by underlying, account type (customer, firm, market maker) and exchange, but the server refuses any date
  more than 2 years back ("Report date cannot be prior to 2 years", daily and monthly). Today that is 2024-10-28
  onward: ~2 months before HOLD, the rest is HOLD. So GLD / SLV / USO / FXE / FXY volume, the per-ETF O/S ratio and
  the customer / firm split cannot be built for IS / VAL. The OCC's deep history is only the daily market-wide
  total (equity vs index contracts, 2008-01..), which O6 uses.
- **The replacement for the CBOE put/call that ended in 2019 exists and was built:** CBOE's daily market statistics
  JSON on the CDN starts 2019-10-07, one trading day after the old archive's last row (2019-10-04). Put/call by
  class (total, equity, index, ETP, SPX+SPXW, VIX) is now continuous 2006-11..2024-12, plus open interest by class from
  2019-10.
- **Put/call at the class level does not time the US indices, gold, oil, EURUSD or USDJPY at 1-5 days**, in any
  form (daily z, 5-day mean z, or z net of the prior 1- and 5-day S&P return):
  - The best of 116 cells has IS net t 1.64 (O3 ETP P/C -> US2000, 5 days). The shared random-date null gives a best
    of p50 1.89, p95 2.53. Every family is at or below its chance level.
  - VAL repeats nothing: the four IS-best cells (all O3 ETP P/C, contrarian) are -30 to -37 bp per 5-day trade in VAL.
  - The continuous slopes are ~0: equity P/C -> US500 next day +0.3 bp per sd (IS t 0.11), VAL +1.1 (t 0.29). Of 224
    information regressions, none has |t| > 1.5 with the same sign in IS and VAL.
- O7 (FINRA daily short volume of SPY / QQQ / IWM / DIA / GLD / SLV / USO / FXE / FXY, 72 cells) is declared but **not graded**: the pull was still running at hand-off (see below).

## O7 status (FINRA short volume, addendum 1)
**Not graded yet.** The download (scratchpad `r35/O/scripts/dl_finra.py`, PID in `out/dl_finra.pid`) was at 2015-03
at 02:21 UTC; at ~2.2 s per request (2 files a day before 2018-08) the full 2015-02..2024-12 pull needs ~2 h. When
`out/dl_finra.log` says DONE: `python -I scripts/parse_finra.py <O dir>`, then from the repo root
`PYTHONPATH=. research/.venv/bin/python <O dir>/scripts/run_o7.py` (72 declared cells, same machinery, writes
out/cells_o7.tsv, picks_o7.txt, null_o7.txt). Prior from HYPOTHESES (power < 0.5) is that it will be null.

## Sources (fetch log: scratchpad `r35/O/web/requests.log`)
| source | span | usable? |
|---|---|---|
| OCC volume-query (marketdata.theocc.com, no robots.txt) | only the last 2 years | **no** (HOLD only) |
| OCC daily-volume-statistics | 2008-01..2024-12 (2005-07: "not available") | yes: market-wide equity / index contracts |
| www.theocc.com | Cloudflare challenge | not touched |
| CBOE archive put/call CSVs (cdn.cboe.com/resources/...) | 2006-11..2019-10-04 (SPX from 2010-07) | yes |
| CBOE daily statistics JSON (cdn.cboe.com/data/us/options/market_statistics/daily/) | 2019-10-07..2024-12-31, 1,318 days (49 holidays 403) | yes. Posted D+1 ~02:30-04:00 UTC (Last-Modified); files to 2024-08 rewritten 2024-08-12/13. Level check at the splice: total volume continuous (ln 15.30 -> 15.31); equity ln P/C median -0.43 -> -0.56 (~1 sd; 2019-20 retail call boom or scope) |
| ISE ISEE (opening-long customer, Pan-Poteshman-type) | nasdaqtrader "Page Not Available", iseoptions.com 404, ise.com refused | **no**; ISEE Select is a subscription |
| FINRA daily short volume (cdn.finra.org, no robots.txt) | 2015-02..2024-12 being pulled (CNMS = FNSQ + FNYX, verified on SPY) | O7 |

## Method
Entry 13:00 UTC on the next US trading day after D (CBOE file for D posted ~03:00 UTC D+1), exit 13:00 UTC h days later,
h 1 / 5, non-overlapping; half the actual spread each leg, 0.6 bp commission on FX / metals, swaps per round 32 V; variants
x1.5, +1 minute, one extra day of lag; random control 200 seeds (same count, sides, hold); shared random-date null for
best-of-family IS t; IS_A = 2016-01..2019-09 (archive only) as a splice check. PRE only for O5 (Dukascopy bid + IC 2016-17
spread). Rule: contrarian symmetric |z| > k (O4 VIX inverted, O5 XAU inverted, O6 short only).

## Results (IS-picked (k, form) per family x target x h; net bp per trade, t)
| family (cells) | best cell | mid IS / VAL | cost | net IS (t) / VAL (t) | VAL/IS | x1.5 / +1m / lag (IS/VAL) | SR IS / VAL, power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| O1 equity P/C -> indices (48) | USTEC h1 k1.5 ma5 | +13.2 / +10.8 | 5.3 | +7.9 (0.87) / +7.4 (0.50) | 0.94 | +6.1/+6.7; +7.5/+7.4; -2.5/-0.4 | 0.053 / 0.039; 0.52 / 0.38 | 0.96 / 0.81 | none |
| O2 SPX P/C -> US500/USTEC (16) | all IS-best cells < 0 (best US500 h1 -2.5, t -0.35) | | 4-14 | | | | | | none |
| O3 ETP P/C -> US500/US2000 (16) | US2000 h5 k1.5 ma5 | +69.7 / -28.2 | 12.1 | +57.6 (1.64) / -36.5 (-0.72) | -0.63 | +55.9/-37.8; +56.7/-37.5; +45.9/-29.0 | 0.207 / -0.114; 0.99 / -0.55 | 0.97 / 0.36 | none (h1: IS +13.8 t 1.56, VAL +2.8 t 0.21, VAL/IS 0.20) |
| O4 VIX P/C -> indices (8) | US500 h1 k1.5 | +4.7 / -7.5 | 4.1 | +0.7 (0.09) / -10.5 (-1.05) | < 0 | | 0.006 / -0.093 | 0.77 / 0.21 | none |
| O5 equity P/C ma5 -> USDJPY / EURUSD / XAU / XTI (16) | USDJPY h1 k1.5 | +1.3 / -8.0 | 1.1 | +0.2 (0.05) / -9.3 (-1.46) | < 0 | | 0.003 / -0.115 | 0.67 / 0.02 | none; PRE -3.5 (t -0.89). XTI IS -42 / VAL +18, EURUSD IS -2.5 / VAL +6.1: signs flip |
| O6 OCC equity volume -> short indices (12) | all IS-best cells < 0 (US500 h1 -2.7, t -0.26) | | 3-9 | | | | | | none |

Years net > 0 (best cells): O1 USTEC h1 7/9; O3 US2000 h5 4/9. Without March-April 2020 the O3 cells are unchanged (no
trades there at h5; h1 +12.5, t 1.41). Chance: all 116 cells best IS t 1.64 vs null p50 1.89 / p95 2.53; per family
O1 0.87 (p50 1.30), O2 -0.25 (1.12), O3 1.64 (0.96, p 0.14), O4 0.09 (0.56), O5 0.05 (1.43), O6 -0.26 (-0.23).
Information: 224 continuous NW regressions (7 series x 2 forms x 8 targets x 2 h): 4 IS and 6 VAL |t| > 2, none
consistent; JSON-era OI P/C (100 rows, IS part 2020-10..2021 only): IS hits (TOT OI change -> US2000 h5 t +3.67) are
~0 in VAL (t -0.40).

## What this says
The free put/call is the aggregate of opening and closing, buying and selling, customer and dealer volume. Whatever
informed flow it contains (Pan-Poteshman needs open-buy volume) is diluted to nothing at the class level, and the
sentiment reading is the 1-day reversal (rounds 2, 7, 11, 32 V) at best. The only per-underlying, per-account data (OCC)
covers just the last 2 years, i.e. HOLD and forward.

## Directions that need the user
- OCC per-underlying volume by account type from 2024-10-28 on (free, but only HOLD + forward): a forward-only
  log could register a rule on GLD / USO / FXY call bursts, but no IS / VAL exists to choose it. Value ~1 % LIVE.
- Open-close / open-buy option volume (CBOE Open-Close, ISE ISEE Select, Nasdaq; paid): the Pan-Poteshman test.
  Value ~2-3 % LIVE (their effect is cross-sectional single-stock; index / ETF effect weak).
- CBOE DataShop / ORATS per-symbol history (paid) for the per-ETF O/S ratio. Value ~1-2 %.

## Files (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r35/O/`)
scripts/: fetch.py, hdr.py, dl_cboe.py, dl_occ.py, dl_finra.py, parse_sources.py, parse_finra.py, build_panel.py,
common.py, run_cells.py, run_o7.py, info_oi.py, posthoc_ex2020.py. out/: panel.npz, series.npz, cells.tsv, picks.txt,
null.txt, info.tsv, info_oi.tsv, run_cells.log. web/: cboe_old/, cboe_json/, occ_daily/, finra/, probe/, requests.log.
C3 correlation: no survivor, not computed.
