# Round 38, stream H: hypotheses (Atlantic storms and dated physical supply disruptions -> XNG, XTI, XBR)

Main file written 2026-10-29 11:11 UTC (`date -u` 11:10:53 just before). No return of any event below had been
computed when this was written. Data loaded so far: HURDAT2 (file `hurdat2-1851-2024-040425.txt`, parsed only through
2024-12-31), the ATCF a-deck archive (pull running, not parsed), EIA daily NYMEX futures contract 1 / 2 for WTI and
Henry Hub and Brent spot (downloaded, not parsed). No price series has been joined to any event.
Bars: research/PROMPT.md, LIVE / DEMO only. HOLD 2025-01-01..2026-09-24 closed: every series is cut at 2024-12-31 at
load; the 2025 HURDAT2 files are not downloaded and no a-deck after 2024 is requested.

## Sources
| id | source | URL | content | span |
|---|---|---|---|---|
| S1 | NHC HURDAT2 best track | `https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2024-040425.txt` | 6-hourly position, status, wind per storm | 1995-2024 used |
| S2 | NHC ATCF a-decks (official forecasts) | `https://ftp.nhc.noaa.gov/atcf/archive/<YYYY>/aal<NN><YYYY>.dat.gz` | `OFCL` forecast track and intensity at tau 0-72 (to 120 h from 2003) for each synoptic time | 190 storms 1995-2024 with any fix west of 80W between 15N and 32N |
| S3 | EIA daily NYMEX futures, contract 1 and 2 (WTI RCLC1 / RCLC2, Henry Hub RNGC1 / RNGC2), Brent spot RBRTE | `https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RCLC1&f=D`, `.../ng/hist/rngc1d.htm` etc. | daily settlement | PRE era 1995-2017 |
| S4 | IC M1 cache XTIUSD, XBRUSD, XNGUSD, USDCAD, US500 | research/data/m1 | bid OHLC + ask close | 2018-01..2024-12 (IS 2018-21, VAL 2022-24) |
| S5 | BSEE Gulf shut-in statistics (per-storm daily press releases) | bsee.gov newsroom, to be probed | % of GoM oil / gas production shut in, release date | conditioning only, if reachable |

## Event counts before any return (S1, data only) and the power arithmetic
Production box P (declared): 25.5-30.0N, 87.0-95.5W (federal OCS shelf and deepwater, Mississippi Canyon / Green Canyon
/ Garden Banks / Keathley Canyon). LNG zone L: within 200 km of Sabine Pass, Cameron, Calcasieu Pass, Freeport,
Corpus Christi. Storms whose best track is at TS / HU strength inside P:

| era | years | storms in P per year | total |
|---|---|---|---|
| PRE (EIA daily, gross) | 1995-2017 | 2.0 (1995-2015), 2.8 (2016-24) | ~47 |
| IS (IC) | 2018-21 | 1 / 4 / 8 / 3 | 16 |
| VAL (IC) | 2022-24 | 0 / 1 / 3 | 4 |
| HOLD expected | 2025-01..2026-09 | ~2.8 a year x ~1.7 seasons | ~5 |

- **LIVE is out of reach.** HOLD would hold ~5 storm events per product. Power 3 needs a per-event net Sharpe of
  3 / sqrt(5) = 1.34. Even pooling three products per storm, the storm is the independent unit.
- **DEMO is the ceiling, and only for a very large effect.** IS t >= 2.0 on 16 storm clusters needs a per-event Sharpe of
  ~0.5. With XNG's ~3.5 % daily sd and ~6-8 % over 3-5 days, that is a mean of ~3-4 % per storm net of cost. With
  XTI / XBR (~2.2 % daily), ~1.1 % a day or ~2.5 % over 3-5 days. VAL has 4 events. "Net > 0" there is a coin flip
  unless the effect is that large.
- So the storm family is built only because the bar it can reach (DEMO) is still informative. Grading: DEMO needs IS
  t >= 2.0, VAL net > 0, >= 90 % of random entries, plus a PRE check with the same sign. If IS t < 2 on all cells,
  I stop the family and do not tune it.

## Family H1: first official forecast threat to Gulf production
- **Mechanism.** When the NHC official forecast first puts a storm into the production area, operators evacuate
  platforms and shut in production over the next 1-3 days. In 2018-24, GoM was ~15 % of US crude, ~2 % of US gas.
  Gulf-coast LNG export terminals and power demand also go off line (2016+ LNG export era: ~10-15 % of US gas demand
  by 2023). Practitioner view (Aegis Hedging, "Why hurricanes now pose a bearish risk to gas prices"; NGI coverage of
  Laura 2020): bearish gas in the export era. The older view (Ivan 2004, Katrina / Rita 2005) is bullish gas and crude
  through lost production.
- **Literature against.** Price reaction is to forecasts, and shut-ins are expected to be temporary (Gustav 2008: crude fell
  through the storm). Round 31 G found NOAA CPC weather outlooks priced in the 24 h before posting, because model runs
  (GFS / ECMWF 00 / 12 UTC) precede the NHC advisory. Prior: low.
- **Trigger (T1).** The first `OFCL` record of a storm in which any forecast point with tau in {0, 12, 24, 36, 48, 72}
  and forecast wind >= 34 kt lies in P. Public issue time = synoptic DTG + 3 h (advisories at 03 / 09 / 15 / 21 UTC).
  One event per storm.
- **Variant T1H.** Same, with forecast wind >= 64 kt (hurricane forecast in P). First such advisory per storm.
- **Variant T1L (XNG only).** First OFCL point >= 34 kt within 200 km of an LNG terminal (zone L).
- **Sides (fixed now).**
  - XBRUSD long, XTIUSD long (lost Gulf crude supply).
  - XNGUSD short in the IC era 2018-24 (LNG export outage + coastal power demand loss > ~2 % of supply lost).
  - PRE side for gas: long in 1995-2009, when GoM gas was 10-20 % of US supply and there were no exports. 2010-17 is
    reported unsigned, as a transitional period.
  - Controls, no expected effect, reported raw: USDCAD (expected sign, if any, short, since CAD follows oil) and US500
    (expected 0).
- **Entry and exit.** Entry at the first IC minute >= issue time + 1 minute, with a second variant +2 minutes; weekend
  advisories enter at the Sunday open + 1 minute. Exit at the same clock 1, 3 and 5 days later (24 / 72 / 120 h). If the
  exit time is in a closed market, the exit is the first quote after it. Cost: half the spread at entry plus half at
  exit (IC M1 `ca - c`). Swap per night crossed at 21:00 UTC: energies -2.5 bp, XNG -4 bp, both sides. Commission 0.
  Variants: spread x1.5, and both legs +1 minute.
- **PRE (S3).** Entry at the first NYMEX settlement after issue time (settlement 14:30 ET = 18:30 / 19:30 UTC; the
  settlement of day D counts if issue < 18:30 UTC in EDT). Exit at the settlement 1 / 3 / 5 trading days later. Same
  contract across a roll: when contract 1 expires inside the hold, the return uses contract 2 at entry. Gross, no cost.
  Brent uses spot (no futures in S3).
- **Statistic.** Mean net bp per event and t across events (one event per storm per product, so storms are the clusters).
  Plus a pooled "storm book" per storm: mean of +XBR, +XTI, -XNG legs.
- **Random control.** >= 500 seeds. Each draws the same number of entry times from the advisory clocks (03 / 09 / 15 /
  21 UTC) on random days in the same months (June-November) of the same IC years, excluding days with an active P
  threat. Same products, sides and holds. Report the share of seeds with a lower mean net.
- **Cells.** T1 / T1H x {XBR, XTI, XNG} x {1, 3, 5 d} = 18, plus T1L x XNG x 3 = 3, so 21 graded cells, plus the
  6 control cells (not graded). Chance benchmark: max |t| of 21 correlated cells. Normal max-of-21 is ~2.4; I also
  report a sign-flip null by storm.

## Family H2: all-clear (risk premium unwinds)
- **Mechanism.** A threat premium built ahead of a storm unwinds once the forecast no longer threatens P. Shut-ins are
  restored within days, "sell the news".
- **Trigger (T2).** After a storm's T1, the first OFCL record in which no forecast point (tau 0-72) is in P with
  wind >= 34 kt and the tau-0 position is outside P. One event per storm that had a T1.
- **Sides.** XBR / XTI short; XNG long (LNG export and demand return) in 2018-24; PRE gas short in 1995-2009.
- **Entry / exit / costs.** As H1, holds 1 and 3 days. Cells: 3 products x 2 = 6. Chance benchmark: max of 6.

## Family H3: forecast revisions between successive advisories (expected to fail like round 31 G)
- **Signal.** For an active storm with any P threat in the last 4 advisories: threat index A = number of OFCL points
  (tau 0-72, >= 34 kt) inside P, weighted by wind / 64. dA = A(advisory k) - A(k-1).
- **Trade.** Trade when |dA| >= 1. Side: sign(dA) long for XBR / XTI, short for XNG. Hold until the next advisory
  (6 h), enter at issue + 1 minute.
- **Statistic.** t clustered by storm-day.
- **Cells.** 3 products x 1 hold = 3.
- **Diagnostic (not a cell, as in round 31 G).** The correlation of dA with the move over the 6 h *before* issue, to
  show whether the forecast is priced before NHC posts.

## Family D: dated unscheduled supply disruptions from official sources (count first)
- **Event list.** Declared from official notices only, not from prices: EIA Today in Energy / Natural Gas Weekly Update /
  This Week in Petroleum articles and operator / regulator notices.
  - Freeport LNG explosion 2022-06-08 (operator statement that day, extension 2022-06-14): XNG short.
  - Colonial Pipeline shutdown 2021-05-07, announced the evening of Fri 05-07: products, no crude side; reported
    descriptively only.
  - Abqaiq / Khurais attack 2019-09-14 (Sat): XBR / XTI long from the Sunday open.
  - Forties Pipeline System shutdown 2017-12-11 (Ineos): XBR long. Pre-IC: PRE only.
  - Keystone pipeline shutdowns 2017-11-16, 2019-10-29, 2022-12-07 (TC Energy notices): XTI long (Cushing supply loss).
  - Sabine Pass / Cameron / Freeport hurricane or freeze outages are already inside H1 / Uri; the Texas freeze of
    2021-02 is weather, not counted.
- **Count.** ~1 event a year in the IC era. DEMO needs IS t >= 2 on ~4 events, which takes a per-event Sharpe > 1.
  The family cannot reach DEMO on count alone. It is reported as a descriptive table (gross and net per event, 1 / 3 /
  5 d), not graded. It is added before any of its returns is computed.
- **S5 BSEE shut-in releases (conditioning).** If S5 is reachable and dated, H1 is split by the eventual peak oil
  shut-in share (>= 50 % vs < 50 %), known only ex post. So it is a mechanism check (larger realised shut-in -> larger
  crude move), not a tradable cell.

## Amendments
- **2026-10-29 11:25 UTC, after the H1-H3 and D numbers. Documentation only; no rule changed.**
  - *Family D entry clocks.* These were fixed in `family_d.py` before it ran, but were not written here first.
    Entry is the first session after the public date: 13:00 UTC on the next day, or the Sunday open for a weekend
    event. Holds are 24 / 72 / 120 h, with the declared sides.
  - *Trigger timing.* In 2018-24 the trigger issue times came from the a-deck `OFCL` DTG + 3 h (special advisories are
    not separated).
  - *S5 (BSEE).* BSEE's newsroom answered 403. Its shut-in releases are scattered PDFs with no index, so S5 is unusable
    and was not used.
- **2026-10-29 11:25 UTC, family N declared (fallback in the row: dated power-sector supply loss -> gas).**
  - *Rule.* Daily change in US nuclear output, in reactor-equivalents, from the NRC Power Reactor Status Report. Trade
    days with a drop of >= 1.5 reactor-equivalents. XNG long (gas-fired replacement burn), entry D+1 13:00 UTC, hold
    1 / 3 d. Count is ~20-40 days a year, so DEMO at best.
  - *Sources: unreachable before any data.* nrc.gov answered 403 twice (directory and the 365-day text file). EIA's
    nuclear-outage page loads its data through the keyed API. Family N is therefore not built, and no number exists
    for it.
