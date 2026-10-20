# Round 24, stream B: long history with fetched data (declared before computing)

Written 2026-10-15 12:01-12:02 UTC (`date -u` gave 12:01:15 when writing started and 12:02:12 when it was complete), before any stream-B return was
computed. What had been done before writing: the Dukascopy download started at 11:47 UTC (no return computed from it;
only a one-month test file was opened to check the format and the integer scale), and literature searches for (b) and
(c). HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31 and the fetch stops at 2016-02.

**What I already know of the data (disclosure).** From earlier reports, not from this stream: round 23 N3b (gold
D-2..D+2 around Christmas, IS +81.8 bp, PRE +103 bp) and its post-hoc note (1 January as strong, EURUSD / silver /
platinum rise in the window); round 16 STREAM_X "the dollar's fall over the last 3 days of December (-74 bp IS)". The
windows below are taken from the cited sources, not from those numbers; the PRE era 2004-15 is the part of (b) I have
seen no number for except N3b's gold PRE.

## Data
- New: Dukascopy M1 bid + ask, AUDUSD NZDUSD XAUUSD XAGUSD GBPUSD USDCAD, 2004-01..2015-12, plus 2016-01..02 for a
  calibration overlap with IC (scale, minute alignment, |mid diff|). Stored as research/data/duka/m1c/<SYM>.npz (int64
  ts ms bar start, float32 bid / ask close, uint16 n = 1 if the minute had Dukascopy volume). Only active minutes kept.
- Existing: research/data/duka/m1 (USDJPY EURJPY GBPJPY USDCHF EURUSD 2004-15 M1), research/data/duka/h1 (11 symbols
  H1 incl. AUDUSD NZDUSD GBPUSD USDCAD XAUUSD), the r23 IC panel 2016-2024, r23/shared/cal (NYSE closures 2004-24).
  England, China (SSE) and other holidays from the `holidays` package in r23/shared/venv_extra.
- Ask validity (fixed now): a symbol-year's Dukascopy ask is used if >= 99 % of active minutes have ask > bid and the
  median spread is <= 3x IC's 2016-17 median for that symbol; then PRE price = mid; otherwise PRE price = bid. Both
  the mid / bid choice per year and a bid-only version are reported.

## Conventions (all cells; aligned with stream C)
- Price "at time X" = close of the M1 bar labelled X-1 min (bar-start labels), at most 10 minutes stale, else no trade.
- Eras: PRE 2004-01..2015-12, IS 2016-01..2021-12 (design), VAL 2022-01..2024-12 (check). Sides and parameters are
  the recorded ones (a) or the source's (b, c); nothing is chosen on any era here.
- Costs. IS / VAL: half the actual IC spread at entry + half at exit + 0.6 bp (FX, metals; 0 for indices) + swap.
  PRE: per symbol, the median IC 2016-17 spread at the same New York clock minute of day (weekdays), half at entry +
  half at exit, + 0.6 bp, + swap. Swap: per 17:00 New York rollover crossed, x3 on the Wednesday rollover (FX and
  metals), with research.swing.rates' fitted IC markups and FRED short rates 2003-2024 (fetched to the scratchpad,
  same series as rates.py; coed 2024-12-31). Checks: spread x1.5; both quotes +1 minute.
- Statistics: bp per trade (a basket or a two-leg day = one trade, legs averaged), t clustered by UTC entry day
  (by year for once-a-year rules); per-trade net Sharpe; power = per-trade net Sharpe x sqrt(1.73 x trades a year) on
  the IS and VAL sizes, and on the check-era size for RELAXED (>= 1.5). Years > 0. VAL / IS ratio and PRE / IS ratio.
- Random-entry control (200 seeds): intraday cells, same days and side rule, entry and exit shifted together by a
  random whole number of minutes in [-180, +180] (not 0), a data-dependent side recomputed at the shifted time;
  seasonal cells, same symbols, side and hold length, entry on a random weekday of the same year outside the declared
  window. Percentile of the rule's net mean among seed means.
- Tiers (as in the brief): LIVE, DEMO (the user's bars, IS design / VAL check), RELAXED (design net t >= 1.5, check
  net > 0 with t >= 1.0, x1.5 and +1 min > 0, beats >= 80 % random, check-size power >= 1.5, a mechanism).
- Chance: max |t| of K normals for the K cells below (K = 21 primary + listed variants).

## (a) Effects real at mid (round 16 STREAM_X), PRE 2004-15 test on the new symbols
Sides and rules as recorded; IS / VAL are recomputed with the same code on the IC panel (they must reproduce the
recorded numbers, which checks the code), PRE is the new test.

| id | STREAM_X row / source | rule (side, window, days) | PRE note |
|---|---|---|---|
| A1 | F19 SYDpre (r12 STREAM_J R0) | short AUDUSD and NZDUSD at 09:45:00 Sydney, cover at 10:00:00 Sydney; Sydney Mon-Fri; trade = mean of the two legs | the V is invisible in the H1 PRE scan of round 13, so PRE is fresh |
| A2 | F21 SYDpost (r12 J R0) | long AUDUSD and NZDUSD 10:00:00 -> 10:15:00 Sydney, Sydney Mon-Fri | fresh |
| A3 | F20 J5c (PREREG_J) | short AUDUSD 09:45 -> 10:00 Sydney on Sydney Mon-Fri, 24 Dec - 2 Jan excluded, only days when 10:00 Sydney is at or after 18:30 New York | post hoc on IS/VAL; HOLD failed (net -0.25); PRE is a second out-of-sample read |
| A4 | M5 L4-G-d (PREREG_L) | XAUUSD, NYSE days, S(d) = mid 13:30 ET, sd = sd of previous 60 daily log returns of S, z = ln(mid 13:14 ET / S(d-1)) / sd, thr = 90th pct of \|z\| over previous 250 days (>= 60); if \|z\| > thr enter 13:15 ET in sign(z), exit 13:30 ET | **test = 2009-15** (gold leveraged ETFs UGL/GLL from Dec 2008); **2004-08 = no-LETF placebo** (expect ~0) |
| A5 | M6 L4-G-q | same, 80th percentile | variant of A4, same split |
| A6 | M8 (r15 V) | short XAUUSD 14:59 -> 15:01 London, London business days (England holidays out), 24 Dec - 2 Jan out | the gold PM fixing was at 15:00 London all of 2004-15 |
| A7 | M9 (r15 V) | short XAGUSD 11:59 -> 12:01 London, same days | the silver fixing was at 12:00 London all of 2004-15 (fixing to 14 Aug 2014, LBMA Silver Price after); Abrantes-Metz & Metz (2014) report the pre-2014 fix drops |
| A8 | M10 (r15 V) | short XAUUSD 10:29 -> 10:31 London, same days | AM fixing 10:30 London all of 2004-15 |
| A9 | M11 (r15 V5) | XAUUSD, NYSE days, side = minus sign(mid 08:20 ET - mid 08:10 ET), enter 08:20 ET, exit 08:30 ET | the COMEX gold floor opened 08:20 ET over 2004-15 |
| A10 | M3 (r10 A6) | long XAUUSD 01:00 -> 03:30 UTC on weekdays that are SSE trading days | round 10 checked 02:00-03:00 on PRE H1 already (+1.6 bp t 6.2), so PRE is not fully fresh: reported as a replication |
| A11 | M4 (r10 A2-close) | XAUUSD, SSE trading days, side = minus sign(mid 07:00 UTC - mid 06:30 UTC), enter 07:00, exit 07:30 UTC | fresh at M1 |
| A12 | M1 SGE placebo (r10 A1-flip) | long XAUUSD 02:15 -> 02:23 UTC, SSE trading days | **placebo**: the SGE benchmark auction starts 2016-04-19; a venue effect predicts ~0 in PRE, a clock effect > 0 |
| A13 | F27 W1 (r3) | Wednesdays, 12:00 -> 16:55 New York: long the higher-yielding currency of each pair (FRED short-rate differential on the day; pair skipped if \|diff\| < 0.25 pp) on the 9 pairs with PRE M1: EURUSD USDJPY USDCHF EURJPY GBPJPY AUDUSD NZDUSD GBPUSD USDCAD; trade = mean of legs | round 3 used 10 pairs (AUDJPY has no PRE M1); fresh in PRE |

Not tested in PRE, and why: F1-F15 and F16 (GBPUSD month-end) and M12 had their side or window chosen on PRE 2004-15
(round 13 M / round 14 Q), so a PRE test is circular; F17 needs US500 before 2016; F25 / F26 (multi-currency R3 /
PCA) are not on new symbols only and were at or below cost; M2 (SGE dip) depends on the SGE auction (A12 is its
placebo); M7 is round 6's all-days version of A4 (A4/A5 cover it).

## (b) Turn of the year: gold long and USD short (declared rule, literature window)
Sources for the window and side:
- USD: Seasonax, "Forex Seasonality: The US Dollar Drop at The End of The Year" (dollar index fell from 1 December
  to 1 January in 34 of 50 years, "loses ground particularly quickly in the second half of December. Thereafter, it
  typically appreciates again in January"); FOREX.com / City Index, "The US dollar, seasonality and what that could
  mean for December" (Dec 2024: December the weakest month over 43 years, "a clear bearish bias in the second half of
  December"). Practitioner sources, no peer-reviewed paper found. Mechanism cited: year-end repatriation and the
  unwinding of year-end dollar funding demand.
- Gold: Gulseven (2016, International Journal of Economic Studies; arXiv 2003.11027), "Turn-of-the Year Affect in Gold
  Prices": a seasonal rise from December through February, January the best month; World Gold Council (2023), "Is
  there a January effect for gold?" (January average +1.79 % since 1971, positive ~70 % of years since 2000).
- Window (fixed from the sources, "second half of December"): entry 15:00 UTC on the first weekday on or after
  15 December; exit 15:00 UTC on the last weekday of December that is not 25 December (hold 10-12 weekdays). January
  is declared separately (B3) because the USD source says the dollar recovers in January while the gold sources say
  gold rises.

| id | rule | role |
|---|---|---|
| **B4** | **primary**: basket over the second-half-of-December window, equal notional legs: long EURUSD GBPUSD AUDUSD NZDUSD, short USDJPY USDCAD USDCHF, long XAUUSD (8 legs); trade = mean leg net bp; one trade a year; t clustered by year | the brief's "gold long and USD short over the turn of the year", pooled over symbols |
| B1 | the 7 USD legs only, same window | variant |
| B2 | XAUUSD long only, same window | variant |
| B3 | XAUUSD long, entry 15:00 UTC on the first weekday after 1 January, exit 15:00 UTC 20 weekdays later (January effect, WGC / Gulseven) | variant |

Eras: 2004-2024, reported PRE / IS / VAL and pooled. PRE prices: Dukascopy H1 (existing, close of the hour bar ending
at 15:00 UTC) for the FX legs and XAU; the new M1 where it exists. IS / VAL: IC panel. Swap charged.

## (c) Other literature seasonals with a known side and a hold over 5 days
| id | source | rule | prior |
|---|---|---|---|
| C1 | Baur (2013), "The autumn effect of gold", Research in International Business and Finance 27(1), 1-11: September and November are the only months with significantly positive gold returns, 1980-2010 | long XAUUSD 15:00 UTC on the first weekday of September and of November, exit 20 weekdays later; 2 trades a year; t clustered by trade | low: Potrykus & Augustynowicz (2024, Int. J. Management and Economics 60(3)) report the autumn effect reversed and replaced by a winter effect; 2004-10 overlaps Baur's sample, 2011-24 is out of it (reported separately) |
| C2 | Hirsch, Stock Trader's Almanac ("Santa Claus rally": the last 5 trading days of December and the first 2 of January) | long, **reading** of the window: enter at the NYSE close (15:59 ET quote) of the 6th-last NYSE trading day of December, exit at the NYSE close of the 2nd NYSE trading day of January (7 trading days); US500, US30, USTEC as equal legs (one trade a year) | IC data 2016-24 only (9 trades), so power is tiny; reported for the record |
| C3 | Seasonax (as B1, second half of the sentence: the dollar "typically appreciates again in January") | the 7 USD legs of B1 with the opposite side (USD long), entry 15:00 UTC first weekday after 1 January, exit 20 weekdays later | conflicts with B3 by construction (gold is priced in USD); both declared from their own sources |

Considered and not declared: the yen's March fiscal-year-end strength (bank notes disagree on the side: ANZ and
Nomura found no March yen seasonality), Halloween / sell-in-May (6-month hold), the gold May-July weakness of
Gulseven (no window or size given), turn of the month (< 5 days, exhausted).

## Cell count and chance
Primary cells: A1-A13 (13; A4 counted once with its placebo), B4, B1, B2, B3, C1, C2, C3 = 20, plus A5 (variant) = 21.
Chance: the expected max |t| of 21 independent normals is about 2.2 (p95 about 3.0); a single surviving cell needs to
be read against that. No further cell is added after numbers; anything else is marked post hoc and is information only.

## Additions after numbers (information only, cannot become candidates)
- 2026-10-15 14:07 UTC, after A1-A3 PRE were computed: a venue check. Fetch Dukascopy AUDUSD and NZDUSD M1 for all
  of 2016 and compute A1-A3 on Dukascopy 2016 vs IC 2016 (same days), to see whether the PRE sizes are a Dukascopy
  quote effect rather than a smaller Sydney V. No rule or side changes.
- 2026-10-15 14:19 UTC, data scope (no cell changes): Dukascopy throttled to ~0.3 files/s (11 s per file, many 503s),
  so the remaining fetch was narrowed to what the declared cells use: XAUUSD and XAGUSD Monday-Friday only, GBPUSD and
  USDCAD Wednesdays only (A13; B/C use the existing H1 for them), and no ASK files for 2004-2009 (the brief: early
  ASK is junk), so those years are priced on the bid. AUDUSD / NZDUSD were already complete.
