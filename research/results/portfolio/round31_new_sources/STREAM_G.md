# Round 31, stream G: commodity and macro public datasets (ETF holdings, NOAA outlooks)

Written 2026-10-27, 18:13-20:55 UTC. The hypotheses were declared in [HYPOTHESES_G.md](HYPOTHESES_G.md) at 18:23-18:40
UTC, before any return was computed. The bars are research/PROMPT.md's (LIVE / DEMO, no RELAXED tier).

HOLD (2025-01..2026-09) was not loaded:
- every fetched series was cut at 2024-12-31 at parse;
- every IC M1 load was cut at ts < 2025-01-01;
- the CPC outlooks were downloaded only through 2024-12-31.

Two small exposures are disclosed in HYPOTHESES_G.md. Neither was used:
- a header peek printed five IAU NAV / shares-outstanding rows from October 2026;
- one literature search returned a news snippet about GLD outflows in 2026.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.** 12 declared cells (7 ETF-flow, 5 weather), all with fixed sides.

**ETF flows.**
- The best IS net t is +1.05 (G1b), below the chance median of ~1.6 for 12 cells.
- No cell reaches IS net t 2.
- Gold's GLD-flow continuation is positive in PRE 2005-15 and IS but negative in VAL 2022-24. Over 2005-24 it is
  +5.9 / +3.6 / -2.9 bp mid on a 90-120 bp daily sd. It decays like every other non-gotobi flow.
- In the joint regression, the flow sign adds nothing beyond the 24 h price move (flow chases price). A day-old
  holdings number does not predict gold.

**NOAA CPC outlooks for XNG.**
- The outlook revisions do carry demand information: corr +0.23 (t 5.3 IS, 5.0 VAL) with XNG's move over the 24 h
  *before* the posting.
- So the market has priced it from the model runs by the time CPC posts, at ~15:00 ET. Nothing is left after the
  posting: best mid t +1.42, every net < 0 except W5 IS.
- IC's XNG round trip (12-25 bp IS, 44-47 bp VAL, plus 4 bp swap a night) would kill a real drift anyway.

**Holdings data versus gotobi.** The holdings data are dated, public and mechanical, like gotobi, but unlike gotobi
they have no execution clock:
- the AP's bullion trade happens when the ETF shares trade, before the holdings number is published;
- the number we can see is the trace of a flow already executed.

## Sources
| source | fetched | span used | status |
|---|---|---|---|
| SPDR Gold Trust historical archive (xlsx) | api.spdrgoldshares.com/api/v1/historical-archive?product=gld&exchange=NYSE&lang=en (the old GLD_US_archive_EN.csv URL now redirects to a bar-list PDF) | 2004-11-18..2024-12-31, 5,248 rows | **usable**: daily total ounces / tonnes, NAV, 4:15 pm premium, volume |
| iShares Gold Trust IAU (SpreadsheetML, "Historical" sheet) | blackrock.com get-fund-document, portfolioId 239561 | 2005-01-21..2024-12-31, 5,018 rows | usable: NAV, shares outstanding (split-adjusted; no ounces) |
| iShares Silver Trust SLV | same, portfolioId 239855 | 2006-04-21..2024-12-31, 4,707 rows | usable |
| NOAA CPC 6-10 / 8-14 day temperature outlook shapefiles | ftp.cpc.ncep.noaa.gov/GIS/us_tempprcpfcst/{610,814}temp_YYYYMMDD.zip | weekdays 2017-10..2024-12 of the trading months: 1,331 + 1,312 files | **usable**: archive daily from 2012-09; the directory listing gives each file's posting time in UTC (19:xx in EDT, 20:xx in EST; 2,596 of 2,643 within those hours). 2022-10-31 returns 403 (both kinds). |
| USCF UNG / USO holdings pages | uscfinvestments.com/ung, /holdings/ung | today only | **unusable**: no free daily history of shares outstanding (only a roll-date CSV) |
| CPC degree-day archive (htdocs/degree_days/weighted, HistDegreeDays) | listing only | - | not used: realised weather is seen in real time; the outlook revision is the only dated surprise (declared) |

Fetch log: scratchpad `web/requests.log`, 2,665 requests, all >= 1.2 s apart, browser User-Agent, no personal data.
One literature WebSearch was used (of 25 allowed).

## Costs used
Costs are executable: buy at the ask, sell at the bid, at the fill minute = the signal minute + 1, from IC M1 (bid
close, ask close).
- **Commission.** 0.6 bp per round trip on metals.
- **Swap.** Per calendar night from research/swing/rates.py (`swap_frac_at`):
  - gold / silver long -0.5..-1.8 bp, short +0.1..+1.35 bp;
  - XNG -4 bp on both sides.
- **Median full spread at the entry minutes:**
  - XAU 13:00 UTC: 0.73 bp IS / 0.40 bp VAL;
  - XAG: 3.4 / 3.8 bp;
  - XNG 14:00 UTC: 11.7 / 44 bp; 19:30-20:55 UTC: 14-25 / 44-47 bp.
- **PRE.**
  - Prices are the Dukascopy XAU / XAG M1 bid.
  - The ask is synthesised from IC's 2016-17 median spread by minute of day, plus the 0.6 bp commission.
  - Swap is approximated at -0.3 bp a night on both sides, because the FRED file starts in 2014.
- **Variants.** Every cell was also run at spread x1.5 and with both fills one minute later.

## Family G: ETF creations / redemptions -> gold, silver
Mechanism (declared): ETF share demand -> AP creation -> bullion bought (the LBMA PM auction is the NAV basis).
Flows persist: the sign of a flow day repeats with probability 0.78 (PRE), 0.73 (IS) and 0.64 (VAL). So a creation
day should predict more buying.
- Side: **continuation**.
- Signal: the GLD ounces change dated T, |F| > 5,000 oz, assumed published by the evening of T.
- Entry: T+1 13:00 UTC.
- t: day-clustered for 1-day holds; Newey-West (lag 3) for the overlapping 3-day holds.

| cell | era | n | mid bp (t) | net bp (t) | x1.5 / +1 min | per-trade SR | years > 0 | shift-null p | random-time p |
|---|---|---|---|---|---|---|---|---|---|
| G1a XAU, 1-day flow, 1-day hold | PRE | 1139 | +5.87 (1.65) | +3.95 (1.11) | +3.50 / +4.08 | +0.033 | 9/12 | 0.02 | 0.52 |
|  | IS | 864 | +3.64 (1.12) | +1.86 (0.57) | +1.36 / +1.72 | +0.019 | 4/6 | 0.11 | 0.43 |
|  | VAL | 501 | -2.92 (-0.73) | -3.87 (-0.97) | -4.07 / -3.76 | -0.043 | 0/3 | 0.62 | 0.28 |
| G1b XAU, 1-day flow, 3-day hold | PRE | 1139 | +4.08 (0.55) | +1.31 (0.18) | +0.86 / +1.48 | +0.006 | 8/12 | 0.19 | - |
|  | IS | 864 | +9.36 (1.38) | +7.15 (1.05) | +6.66 / +7.15 | +0.043 | 4/6 | 0.05 | - |
|  | VAL | 499 | -1.52 (-0.19) | -2.41 (-0.31) | -2.62 / -2.26 | -0.016 | 2/3 | 0.47 | - |
| G2a XAU, 5-day flow sum, 1-day hold | PRE | 2446 | +2.43 (1.00) | +0.52 (0.21) | +0.08 / +0.56 | +0.004 | 5/12 | | |
|  | IS | 1466 | +0.26 (0.11) | -1.53 (-0.66) | -1.98 / -1.56 | -0.017 | 3/6 | | |
|  | VAL | 735 | -0.33 (-0.10) | -1.39 (-0.42) | -1.59 / -1.33 | -0.016 | 2/3 | | |
| G2b XAU, 5-day flow sum, 3-day hold | PRE | 2446 | +1.15 (0.19) | -1.62 (-0.27) | -2.06 / -1.74 | -0.008 | 3/12 | | |
|  | IS | 1466 | -0.88 (-0.15) | -3.22 (-0.55) | -3.67 / -3.15 | -0.021 | 4/6 | | |
|  | VAL | 733 | +0.16 (0.02) | -0.99 (-0.13) | -1.20 / -0.92 | -0.007 | 2/3 | | |
| G3 XAU 14:45 -> 15:10 London on T+1 (into the PM auction) | PRE | 1139 | -1.36 (-1.46) | -2.84 (-3.06) | -3.28 / -2.93 | -0.091 | 3/12 | | |
|  | IS | 864 | +0.20 (0.27) | -1.31 (-1.77) | -1.77 / -1.43 | -0.060 | 0/6 | | |
|  | VAL | 501 | +0.13 (0.14) | -0.87 (-0.91) | -1.07 / +0.05 | -0.041 | 0/3 | | |
| G5 XAU, GLD + IAU dollar flow > $5m, 1-day | PRE | 1409 | +5.06 (1.61) | +3.14 (1.00) | +2.69 / +3.22 | +0.027 | 8/12 | | |
|  | IS | 1165 | +2.33 (0.86) | +0.47 (0.17) | -0.00 / +0.59 | +0.005 | 4/6 | | |
|  | VAL | 622 | -4.78 (-1.33) | -5.74 (-1.59) | -5.95 / -5.59 | -0.064 | 0/3 | | |
| G4 XAG, SLV shares change >= 25k, 1-day | PRE 2008-15 | 638 | -0.17 (-0.02) | -5.01 (-0.51) | -6.90 / -5.24 | -0.020 | 3/8 | 0.46 | 0.49 |
|  | IS | 660 | +11.44 (1.47) | +6.93 (0.89) | +5.13 / +7.19 | +0.035 | 3/6 | 0.03 | 0.66 |
|  | VAL | 520 | +11.80 (1.50) | +7.42 (0.95) | +5.46 / +7.92 | +0.042 | 3/3 | 0.10 | 0.18 |

Power: per-trade net Sharpe x sqrt(expected HOLD trades = 1.73 x VAL trades a year).

| cell | HOLD n | power at IS size | power at VAL size | VAL / IS mid |
|---|---|---|---|---|
| G1a | 289 | 0.33 | -0.73 | -0.80 |
| G1b | 288 | 0.72 (overstated: overlapping) | -0.27 | -0.16 |
| G2a | 424 | -0.35 | -0.32 | n/a |
| G2b | 423 | -0.42 | -0.14 | n/a |
| G3 | 289 | -1.02 | -0.69 | 0.65 |
| G5 | 359 | 0.10 | -1.21 | -2.05 |
| G4 | 300 | 0.60 | 0.72 | 1.03 |

LIVE needs 3. DEMO needs IS net t >= 2: the best is G1b at 1.05.

Declared checks:
- **Dose response (G1a, mid on |F| / sd).**
  - PRE: +6.90 bp per sd (t 1.94).
  - IS: +0.45 (t 0.14).
  - VAL: -3.11 (t -0.78).
  - G4 (silver) has the wrong sign in IS (-7.70, t -0.99).
- **Momentum control.**
  - The flow side agrees with the sign of the 24 h gold move before entry on 56-60 % of days.
  - Joint regression of the 1-day return on both signs, G1a:
    - PRE: flow +4.77 (t 1.32), momentum +6.78 (t 1.87);
    - IS: flow +4.00 (t 1.21), momentum +4.06 (t 1.24);
    - VAL: flow -2.21 (t -0.53), momentum +0.96 (t 0.23).
  - The flow is no better than 1-day momentum, which rounds 2 / 7 / 11 found dead.
- **The clock (G3).** The AP-auction window carries nothing:
  - mid +0.20 / +0.13 bp in IS / VAL;
  - PRE is negative: gold falls into the PM auction (round 15's M8), whatever the flow.
- **Silver (G4).**
  - It has the only same-sign IS and VAL nets (+6.9 / +7.4 bp, t 0.89 / 0.95, shift-null p 0.03 / 0.10).
  - But PRE 2008-15 is -5.0, the IS dose slope is negative, and the random-time control is not beaten (p 0.66 /
    0.18).
  - At a 180-200 bp daily sd, its power is 0.6-0.7. That is noise, not a lead.
- **Publication timing.** Unverified: a creation dated T correlates more with the 4:15 pm premium of T-1 (0.175) than
  of T (0.121) in IS. So the ounces dated T are partly T-1 orders, and the signal is one to two days old at entry.
  - An earlier entry was not declared and was not run.
  - With VAL at -2.9 bp mid and no IS signal, an earlier entry cannot plausibly lift the family to DEMO (it would
    need ~8 bp mid).

## Family W: NOAA CPC outlooks -> XNGUSD
**Index.** The index was declared before any return:
- **Points.** The 25 largest US metros, weighted by population.
- **Value at each point.** The signed excess probability of the highest-probability Above / Below contour that
  contains the point; 0 for Normal or equal chances.
- **Averaging.** The 6-10 and 8-14 outlooks are averaged.
- **Season sign.** Winter (Nov-Mar) -1 and summer (Jun-Aug) +1, by the start of the 6-10 window.

**Signal.** The revision is dX = q x (A_D - A_previous weekday). The interpretation of "X_D - X_D'" uses D's season;
1 boundary day was affected. Trades are taken only above the IS median |dX| = 2.25 (|X| = 6.40 for W5). There are
1,238 signal days.

**Eras.** IS 2018-21 (IC's XNG starts 2018), VAL 2022-24; no PRE.

| cell | era | n | mid bp (t) | net bp (t) | x1.5 / +1 min | SR | years > 0 | shift-null p |
|---|---|---|---|---|---|---|---|---|
| W1 revision, entry posting + 11 min, 1 day | IS | 272 | -8.75 (-0.45) | -36.13 (-1.85) | -46.2 / -35.6 | -0.112 | 0/4 | 0.69 |
|  | VAL | 251 | +24.96 (0.84) | -22.34 (-0.75) | -42.8 / -22.9 | -0.047 | 1/3 | 0.23 |
| W2 same, 3 days | IS | 272 | +6.26 (0.19) | -33.91 (-1.03) | -43.7 / -34.5 | -0.064 | 1/4 | 0.42 |
|  | VAL | 249 | +41.20 (0.74) | -18.09 (-0.33) | -38.7 / -18.9 | -0.023 | 1/3 | 0.25 |
| W3 revision, D+1 14:00 UTC, 1 day | IS | 341 | +14.32 (0.89) | -4.09 (-0.25) | -10.2 / -3.9 | -0.014 | 2/4 | 0.17 |
|  | VAL | 272 | +43.92 (1.42) | -3.43 (-0.11) | -24.0 / -5.3 | -0.007 | 1/3 | 0.05 |
| W4 same, 3 days | IS | 341 | +0.77 (0.03) | -29.78 (-1.18) | -36.0 / -28.6 | -0.060 | 1/4 | 0.52 |
|  | VAL | 270 | +24.30 (0.48) | -34.26 (-0.68) | -54.9 / -35.4 | -0.043 | 1/3 | 0.32 |
| W5 level (not revision), D+1 14:00, 3 days | IS | 342 | +41.83 (1.04) | +10.76 (0.27) | +4.6 / +9.6 | +0.021 | 2/4 | 0.14 |
|  | VAL | 309 | -110.21 (-1.89) | -170.14 (-2.92) | -191.3 / -168.9 | -0.242 | 0/3 | 0.91 |

**Power** (HOLD n ~145-180):
- W1: IS -1.35, VAL -0.57.
- W3: -0.18 / -0.09.
- W5: +0.28 / -3.23.
- The others are below 0.

**Dose response.** The slope on |dX| is never significantly positive. W3 VAL: -54.7 (t -1.78).

**Seasons.** Neither season is consistent across eras:
- W3 winter: IS -10.6, VAL +17.4;
- W3 summer: IS +7.9, VAL -55.3.

**W5's VAL loss** is the 2022-24 gas collapse against a 61 % long book. It is not a reversal signal: the shift-null p
is 0.91.

**Diagnostic (not a cell): the information is priced before CPC posts.**
- The XNG mid return from the previous weekday's posting clock to today's correlates +0.235 with dX in IS (n 476,
  t 5.26) and +0.231 in VAL (n 455, t 5.04).
- The outlook revision summarises the 00z-12z model runs, and gas trades them as they come out.
- After the 15:00 ET posting, the drift is gross +14 / +44 bp at best (W3, t 0.89 / 1.42). That is against a
  45 bp VAL round trip at IC.

## Cells, chance, and what was not run
**Cells and chance.**
- 12 declared cells; no undeclared cell was run.
- Best one-sided IS net t: +1.05 (G1b). For 12 null cells the median is ~1.6 and the 95th percentile ~2.6.
- Best VAL net t: +0.95 (G4).
- The family-level circular-shift nulls agree: nothing beats 95 % in both IS and VAL.

**Not run** (as declared):
- the GLD premium signal;
- commodity-index rolls (round 3 O1);
- CFTC data;
- EIA storage releases;
- the PBoC / US Mint monthly reserves (12 a year: below the DEMO power at gold's sd);
- realised degree days.

**Idea found, not tested: CME margin-change advisories for gold / silver / NG.** These are dated, public and force
leveraged longs to cut, effective the next business day. But they come ~5-15 times a year per product, so at gold's
90 bp daily sd a DEMO needs ~25-40 bp per event. It is worth a declared test only if a later round has spare capacity;
the advisories archive is public on cmegroup.com.

**C3 correlation.** Not computed (no survivor).

## Directions that need the user (one-line value)
- **Daily shares outstanding history for USO / UNG / BOIL / KOLD** (paid data, or EDGAR parsing of filings). This would
  give the futures-ETF creation flow, which, unlike GLD's, is executed in futures at the settlement. Value ~0-1 %
  LIVE: XNG's IC cost (45 bp VAL) and the decayed leveraged-ETF settlement flow (rounds 6 / 13) bound it.
- **XNG on a futures venue** (NG micro ~1 tick ≈ 3-4 bp). The weather information is priced before the CPC posting
  anyway. Value ~0 for this family.
- **Run-by-run weather model data** (GFS free from NOAA NOMADS/NCEI, ECMWF open data only recent). This is the source
  the market actually trades; a drift after each run would need a sub-hour test and a cheap venue. Value ~1 % at IC's
  cost.
- **The GLD publication clock.** It can be logged for free from now on (the site's update time) if a later round wants
  an earlier entry. Value ~0, given VAL is negative at mid.

## Scripts and outputs (scratchpad, not in the repo)
All files are under
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r31/G/`.

**Scripts** (`scripts/`):
- `fetch.sh`: logged fetcher;
- `dl_cpc.sh`: CPC downloader;
- `xlsx_rows.py`, `ssxml.py`: stdlib spreadsheet readers;
- `parse_etf.py`: GLD / IAU / SLV, cut at 2024;
- `describe_etf.py`: flow statistics, no returns;
- `shp.py`, `cpc_index.py`: shapefile reader and population-weighted index;
- `px.py`: quotes, IC + Dukascopy;
- `etf_test.py`, `etf_checks.py`: family G;
- `xng_test.py`: family W.

**Outputs** (`out/`):
- `gld.csv`, `iau.csv`, `slv.csv`, `cpc_index.csv`, `cpc_listing.csv`;
- `trades_G*.csv`, `etf_results.json`, `xng_results.txt`.

**Downloads** (untrusted, all parsed with `python -I`): `web/`.
