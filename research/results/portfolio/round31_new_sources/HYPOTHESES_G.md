# Round 31, stream G: hypotheses (commodity and macro public datasets)

Written 2026-10-27 18:23-18:40 UTC (`date -u` 18:23:10 at the start), **before any return was computed**. At this
time the stream had loaded: the ETF holdings series (GLD tonnes, IAU and SLV shares outstanding, all cut at
2024-12-31 at parse), the CPC outlook file listing, one CPC shapefile, and IC spreads at the candidate minutes (cost
only). No price series has been joined to any signal.

Disclosures (HOLD hygiene):
- While finding the IAU sheet header, a `head` of the raw iShares file printed 5 rows of IAU NAV per share and shares
  outstanding dated 2026-10-20..26 (the file is newest-first). No gold price and no return; nothing here uses them;
  every parsed series is cut at 2024-12-31.
- A web search for literature (one query) returned a news snippet about 2026 GLD outflows and gold's 2026 YTD move.
  Not used for any choice below; the sides were fixed by the mechanism before that search.

## Sources (fetched, see the scratchpad `web/requests.log`)
| source | URL | span | content |
|---|---|---|---|
| SPDR Gold Trust (GLD) historical archive | https://api.spdrgoldshares.com/api/v1/historical-archive?product=gld&exchange=NYSE&lang=en (xlsx, linked from spdrgoldshares.com/usa/historical-data/) | 2004-11-18..2024-12-31 (cut) | daily total ounces / tonnes, NAV, 4:15 pm premium, volume |
| iShares Gold Trust (IAU) | blackrock.com get-fund-document, portfolioId 239561 (SpreadsheetML) | 2005-01-21..2024-12-31 | NAV per share, shares outstanding |
| iShares Silver Trust (SLV) | same, portfolioId 239855 | 2006-04-21..2024-12-31 | NAV per share, shares outstanding |
| NOAA CPC 6-10 / 8-14 day temperature outlooks | https://ftp.cpc.ncep.noaa.gov/GIS/us_tempprcpfcst/610temp_YYYYMMDD.zip, 814temp_... | daily from 2012-09; downloading weekdays 2017-10..2024-12 of the trading months | shapefile polygons (Cat Above / Below / Normal, Prob %); the directory listing gives each file's posting time (UTC): 19:xx UTC in EDT, 20:xx in EST, i.e. ~15:00-15:30 ET |

Flow facts already seen (no returns): GLD |change| > 5,000 oz on 41 % (PRE), 57 % (IS), 67 % (VAL) of days; the sign
of non-zero flow days repeats the next day with probability 0.78 / 0.73 / 0.64 and after 5 days 0.68 / 0.63 / 0.57
(flows persist, decaying over eras). Correlation of the change dated T with the 4:15 pm premium of T-1 is higher than
with T in IS (0.175 vs 0.121), so the ounces dated T partly reflect orders of T-1. IAU and SLV shares outstanding do
not change on 65 % / 59 % of days.

## Costs per round trip (IC, measured at the entry / exit minutes, median full spread in bp)
- XAUUSD 13:00 UTC: 0.73 IS / 0.40 VAL (+0.6 commission); 14:45 / 15:10 UTC 0.70 / 0.35. Swap per night (rates.py):
  long -0.5..-1.8 bp, short +0.1..+1.35 bp.
- XAGUSD 13:00 UTC: 3.4 IS / 3.8 VAL (+0.6).
- XNGUSD: 14:00 UTC 11.7 IS (2018-21) / 44 VAL; 19:30-20:55 UTC 14-25 IS / 44-47 VAL; swap -4 bp per night on both sides.
- PRE (Dukascopy 2004-15, gold bid only before 2010): IC 2016-17 spread by minute of day + 0.6 bp.
- Executable: actual bid / ask at the fill minute (buy at the ask, sell at the bid), fill one minute after the
  signal minute; also +1 more minute and spread x1.5.

## Power arithmetic (before any test)
Daily sd assumed from typical vol (not measured on the series): gold ~90 bp / day, silver ~170, XNG ~400; a 25-minute
gold window ~12 bp. HOLD 1.73 years. LIVE needs per-trade net Sharpe >= 3 / sqrt(n_HOLD); DEMO needs IS t >= 2.

| cell type | trades / yr | n HOLD | LIVE net edge needed | DEMO net edge needed (IS) | cost | implied mid for DEMO |
|---|---|---|---|---|---|---|
| gold 1-day hold on GLD flow days | ~145 IS / ~165 VAL | ~285 | 0.178 sd = **16 bp** | 2.0 / sqrt(870) = 0.068 sd = 6.1 bp | ~1.3 + ~0.5 swap | ~8 bp (0.09 sd per day) |
| gold 25-min window into the LBMA PM auction | same | ~285 | 2.1 bp | 0.8 bp | ~1.3 IS / 1.0 VAL | ~2.1 bp |
| silver 1-day on SLV flow days | ~100 | ~175 | 0.23 sd = 38 bp | 2.0 / sqrt(600) = 0.082 sd = 14 bp | ~4.4 + swap | ~19 bp |
| XNG 1-day on outlook days (8 months / yr, top half) | ~85 | ~145 | 0.25 sd = 100 bp | IS 2018-21 only: 2.0 / sqrt(340) = 0.11 sd = 43 bp | 12-25 IS / 45 VAL + 4 swap | ~65 bp IS, ~95 VAL |

Reading: for gold a LIVE cell needs a daily predictability of ~0.2 sd from a public, day-old holdings number; the
literature of ETF flows shows flows chasing returns, not predicting them. Prior: gold DEMO ~5 %, LIVE ~1 %; XNG
anything ~1-2 % (the outlooks are a human blend of model runs the market trades four times a day, and IC's XNG cost
in VAL is ~50 bp). Tested anyway because the mechanisms are new here and the data are free.

## Family G: ETF creations / redemptions (mechanism: flow persistence + price pressure)
Mechanism: GLD / IAU / SLV shares are created when ETF buying pushes the shares to a premium; the authorised
participant buys bullion (London spot, LBMA PM auction is the NAV basis) or hedges in COMEX futures. Daily flows
persist (sign repeats ~0.7 the next day), so a creation day predicts more ETF buying, hence more bullion buying, on
the next days. Side fixed by this mechanism: **continuation** (long after net creation, short after net redemption).
The opposite side (reversal of the price pressure) is not tested as a cell; its t would be minus these.

Signal day T = a GLD archive business day; publication assumed by the evening of T (NAV and holdings are posted after
the US close; assumption, to verify before any live use). Flow F_T = total ounces T - total ounces at the previous
row; an event needs |F_T| > 5,000 oz (half a basket; excludes the small fee sales of ~2,000 oz). Entry = the first
weekday after T with a quote at the entry minute.

| cell | symbol | signal | entry (UTC unless stated) | exit | side |
|---|---|---|---|---|---|
| G1a | XAUUSD | sign F_T | T+1 13:00 (fill 13:01) | 1 trading day later 13:00 (fill 13:01) | continuation |
| G1b | XAUUSD | sign F_T | T+1 13:00 | 3 trading days later 13:00 (<= 3 open positions) | continuation |
| G2a | XAUUSD | sign of 5-day sum F_{T-4..T}, |sum| > 5,000 oz | T+1 13:00 | 1 day | continuation |
| G2b | XAUUSD | same | T+1 13:00 | 3 days | continuation |
| G3 | XAUUSD | sign F_T | T+1 14:45 London (fill +1 min) | T+1 15:10 London (after the PM auction) | continuation (AP bullion buying into the NAV auction) |
| G4 | XAGUSD | sign of SLV shares change dated T (|change| >= 25,000 shares, half a basket) | T+1 13:00 | 1 day | continuation |
| G5 | XAUUSD | sign of GLD + IAU dollar flow (F_T x GLD NAV per oz + IAU share change x IAU NAV), |flow| > $5m | T+1 13:00 | 1 day | continuation |

7 cells. Eras: PRE 2005-2015 on Dukascopy XAUUSD M1 bid (G1a, G1b, G2a, G2b, G3, G5) and XAGUSD (G4: 2008-15 only,
Dukascopy silver before 2008 is sparse); IS 2016-21; VAL 2022-24.

Checks per cell (not extra cells): dose response (slope of the return on F_T / its IS sd); a **momentum control**:
the same rule with side = sign of the gold return over the 24 h ending at the entry (13:00 T -> 13:00 T+1), and the
joint regression of the trade return on both signs, because ETF flows chase returns and round 2/7/11 found 1-day
momentum dead; by year; random-entry control: 200+ circular shifts of the signal series against the returns
(>= 20 business days), side recomputed from the shifted signal, same entry clock and hold; and a time control of
random entry minutes 07:00-20:00 UTC on the same days with the side recomputed from the flow known at that time.
t: day-clustered for 1-day cells; Newey-West with lag = hold for overlapping 3-day cells.

## Family W: NOAA CPC 6-10 / 8-14 day temperature outlooks and natural gas (XNGUSD)
Mechanism: gas demand is driven by heating (Nov-Mar) and cooling / power burn (Jun-Aug); the CPC outlooks are a
dated, public demand forecast posted ~15:00-15:30 ET. Escape argument (weak): if the market under-reacts to the
human consensus outlook, or the outlook revision carries information beyond the model runs already traded, the
next 1-3 days drift in the direction of the demand revision. Side fixed by the mechanism: colder in winter / hotter
in summer = **long** gas.

Index (fixed before any return): 25 largest US metropolitan areas (2020 census populations, weights in millions):
New York 20.1 (40.71 N, 74.01 W), Los Angeles 13.2 (34.05, -118.24), Chicago 9.6 (41.88, -87.63), Dallas 7.6
(32.78, -96.80), Houston 7.1 (29.76, -95.37), Washington 6.4 (38.91, -77.04), Philadelphia 6.2 (39.95, -75.17),
Miami 6.1 (25.76, -80.19), Atlanta 6.1 (33.75, -84.39), Boston 4.9 (42.36, -71.06), Phoenix 4.8 (33.45, -112.07),
San Francisco 4.7 (37.77, -122.42), Riverside 4.6 (33.95, -117.40), Detroit 4.4 (42.33, -83.05), Seattle 4.0
(47.61, -122.33), Minneapolis 3.7 (44.98, -93.27), San Diego 3.3 (32.72, -117.16), Tampa 3.2 (27.95, -82.46),
Denver 3.0 (39.74, -104.99), Baltimore 2.8 (39.29, -76.61), St. Louis 2.8 (38.63, -90.20), Orlando 2.7
(28.54, -81.38), Charlotte 2.7 (35.23, -80.84), San Antonio 2.6 (29.42, -98.49), Portland 2.5 (45.52, -122.68).
At each point the outlook value s = +(P - 33.3) if inside an "Above" polygon of highest probability P, -(P - 33.3) if
"Below", 0 if "Normal" or no polygon (equal chances). A_D = population-weighted mean of s, averaged over the 6-10
and 8-14 outlooks issued on day D (one of them alone if the other is missing). Season sign q = -1 if the 6-10 window
starts in Nov-Mar, +1 in Jun-Aug, else no trade. Demand index X_D = q x A_D (positive = bullish gas). Revision
dX_D = X_D - X_{D'} with D' the previous weekday issue. Signal days: weekdays with both D and D' files.
Threshold for trading: |dX| (or |X| for W5) above its IS (2018-21) median, from the signal series alone.

| cell | signal | entry | exit | side |
|---|---|---|---|---|
| W1 | sign dX_D, top half of |dX| | D at the file's posting time + 10 min (fill +1 min) | same clock 1 trading day later | long if dX > 0 |
| W2 | same | same | 3 trading days later | same |
| W3 | same | D+1 14:00 UTC (cheaper spread) | 1 day later 14:00 | same |
| W4 | same | D+1 14:00 UTC | 3 days later 14:00 | same |
| W5 | sign X_D (level, not revision), top half of |X| | D+1 14:00 UTC | 3 days later 14:00 | long if X > 0 |

5 cells. Eras: IS 2018-21 (IC XNG starts 2018), VAL 2022-24; no PRE (no XNG price before 2018 here). The weekend
outlooks are skipped; Monday's revision is against Friday. Checks: by year, by season, dose response on |dX|,
circular-shift null (200+), spread x1.5, +1 minute.

## Multiple testing
12 declared cells (7 G, 5 W), sides fixed. Chance benchmark: the best one-sided t of 12 independent nulls has median
~1.6 and 95th percentile ~2.6; reported next to the best cell, plus the circular-shift null per cell.

## Not declared (and why)
- GLD 4:15 pm premium as a signal: the AP arbitrage it triggers happens the same evening, before the publication
  time can be relied on; no clock to trade at.
- Commodity-index roll in energies: tested in round 3 (O1); IC's energy CFDs are continuous.
- CFTC (TFF / disaggregated): rounds 4 and 9.
- EIA storage / crude reports: rounds 6, 25, 26.
- PBoC / US Mint monthly gold data: 12 events a year, no execution clock, power far below DEMO (needs ~20 bp per
  event at gold's daily sd with 72 IS events).
- Realised degree days: realised weather is observed in real time and priced; the outlook revision is the only dated
  surprise.
- Oil ETF (USO / UNG) shares outstanding: no free daily history found yet; probed in the stream report if time allows.
