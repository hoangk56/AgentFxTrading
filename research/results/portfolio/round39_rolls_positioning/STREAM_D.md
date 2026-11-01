# Round 39, stream D: retail and broker-client positioning histories

Written 2026-10-29 from 13:25 UTC (`date -u`). Hypotheses with their UTC times: [HYPOTHESES_D.md](HYPOTHESES_D.md)
(part 1 sources 13:27, part 2 COT small traders 13:36, part 3 JPX / NAAIM 13:39), each written before the returns of
its part. HOLD (2025-01-01..2026-09-24) stayed closed: CFTC files are by year and only 2004-2024 were fetched (the
report as of 2024-12-31, released in 2025, was dropped); JPX weekly files were taken only from the 2016-2024 archive
pages (the current-data page lists 2026 file names; their names were seen, no file was opened; the open-interest zip
for 2025+ was not fetched); IC prices cut at ts < 1735689600000 at load. No 2025-26 value was printed.

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- **No free broker-client positioning history reaches 2016-21 with a public timestamp from this machine.** Dukascopy
  SWFX (site times out; widget backend 403; history only through a JForex account), FXCM SSI (one free month,
  2018-01; the rest is paid), Myfxbook (times out), IG / DailyFX (403, current only), FXSSI (history behind a
  sign-in), AAII (members' file, 403), NAAIM (subscription since 2026-08), Hugging Face / Zenodo / GitHub (nothing).
- Fallback 1, the CFTC COT **non-reportable (small trader)** positions, 17 CME / COMEX / NYMEX / CBOT markets mapped
  to IC symbols, 2005-24 (first load of this split; rounds 4 / 9 used non-commercial net): 14 declared book cells and
  204 single-market cells against small traders. Best book D3 k2 h1 (with large speculators when they disagree with
  small traders) net IS +28.8 bp (t 2.06), VAL -15.7 (t -0.70), PRE +0.8: VAL fails, and its mid t 2.56 is inside
  the best-of-14 null (p95 2.69). Small-trader positioning has no timing information at 1-3 days, as Wang (2003)
  found for the 1990s.
- Fallback 2, JPX weekly derivatives trading by investor type (individuals and foreigners in Nikkei 225 futures +
  mini, 2016-24, first load of the derivatives table): 8 declared cells on JP225, best IS net t +0.80 (follow
  foreigners k1.5 h3), VAL -11.0; fading individuals is wrong-signed in VAL (k1 h1 net -38.9, t -1.86).
- LIVE was out of reach for every weekly source from the count (HOLD ~75-80 weeks needs a weekly Sharpe >= 0.35).

## Sources (fetch log: scratchpad `web/requests.log`, 535 requests; 5 WebSearch, 2 WebFetch)
| source | what was fetched | history (used to 2024-12-31) | usable? |
|---|---|---|---|
| Dukascopy SWFX Sentiment Index | www.dukascopy.com: 2 timeouts (WebFetch also failed); freeserv.dukascopy.com `/2.0/` 204, 4 widget paths 403 (the known economic-calendar path too: an embed referrer check, not circumvented) | site shows now / 6 h / 1 day / 1 month only; 30-min history via JForex `IFXSentimentIndex` (account) | no |
| FXCM SSI | github.com/fxcm/MarketData README; `sampledata.fxcorporate.com/sentiment/EURUSD.csv.gz` (one file) | free sample = 2018-01-02..2018-02-01, minute step, 12 series (SSIHist, LongAmountK, orders, NET); directory 403; full history is FXCM premium data (paid); DailyFX archive needs an FXCM login | no (one month) |
| Myfxbook community outlook | www.myfxbook.com timeout | current only (API needs a login) | no |
| IG / DailyFX client sentiment | dailyfx.com 403 | current only | no |
| FXSSI | fxssi.com/tools/current-ratio (page, 200) | ratio history via `/api/ratios` sends a user token; anonymous use ends in a sign-in wall; the auto-mode classifier refused an anonymous history probe as access circumvention, so it was not queried | no (account) |
| Gaitame | timeout | | no |
| Hugging Face, Zenodo | 7 + 4 API searches | no retail positioning dataset | no |
| AAII sentiment survey | `aaii.com/files/surveys/sentiment.xls` 403 | members only | no |
| NAAIM exposure index | naaim.org page (200) | subscription access since 2026-08-01 (page notice) | no |
| **CFTC COT legacy futures-only** | `cftc.gov/files/dea/history/deacot2004..2024.zip` (21 files) | 17 markets 2004-01-06..2024-12-31 (RTY 579 weeks, NZD from 2004-08, BTC from 2018-04-10, Nikkei USD to 2024-12-17) | **yes** |
| **JPX derivatives trading by investor type (weekly)** | `jpx.co.jp/english/markets/statistics-derivatives/sector/00-archives-02..10.html` (2016-2024), 469 weekly CSVs, CSV guide PDF / xls | 2016-01..2024-12; codes 301 = Nikkei 225 Futures (value in kJPY), 313 = Nikkei 225 mini; investor 50 = individuals, 60 = foreigners (brokerage 30 + 50 + 60 + 41 = 70, checked) | **yes** |
| JPX open interest by investor type (Tategyoku) | not fetched | 2020-07..2024-12 zip only (IS would be 18 months) | not used |

## Fallback 1: COT small traders (HYPOTHESES_D part 2)
Rule recap: x = (non-reportable long - short) / OI, Tuesday as-of, public Friday 15:30 ET; trade Friday 15:50 ET at
IC prices, exit Monday 15:50 ET (h1) or Wednesday 15:45 ET (h3); weeks with a US federal holiday and the 2013 / 2018-19
shutdown catch-ups skipped (~42 weeks a year). Sides against small traders (D1 level z vs 156 weeks, D2 weekly change
z vs 52 weeks), with large speculators against small traders (D3 = z(non-commercial) - z(non-reportable)), and an FX
cross-section (D4: short the 2 currencies small traders are most long vs USD, long the 2 most short). Costs: IC spread
at both minutes, 0.6 bp commission on FX and metals, swap; PRE 2005-15 on Dukascopy FX majors and metals with IC
2016-17 spreads + 0.6 bp. Book = equal-weight mean of the legs open that week (bp, so BTC and gas legs dominate).

### Book cells (one return per week; t on weekly returns)
| cell | eras | mid IS (t) / VAL (t) | cost IS (bp) | net IS (t) / VAL (t) / PRE (t) | VAL / IS | Sharpe IS / VAL; power at HOLD n ~75 (IS, VAL size) | x1.5 / +1 min IS t | ex 2020-03/04 IS t | years + | random IS / VAL (a; b) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 k1.0 h1 | PRE, IS, VAL | +8.94 (1.67) / -7.16 (-0.70) | 4.2 | +4.73 (0.89) / -15.20 (-1.48) / +1.40 (0.29) | < 0 | +0.057 / -0.135; 0.50, -1.17 | 0.71 / 0.89 | 0.62 | 4/9 | 0.91; 0.93 / 0.07; 0.12 | none |
| D1 k1.0 h3 | PRE, IS, VAL | +10.36 (1.22) / -0.55 (-0.04) | 5.9 | +4.44 (0.53) / -11.45 (-0.80) / +0.29 (0.03) | < 0 | +0.034 / -0.072; 0.29, -0.62 | 0.41 / 0.56 | 0.19 | 5/9 | 0.93; 0.90 / 0.34; 0.43 | none |
| D1 k1.5 h1 | PRE, IS, VAL | +13.77 (1.05) / +0.38 (0.02) | 4.3 | +9.46 (0.72) / -11.68 (-0.59) / +5.70 (0.74) | < 0 | +0.049 / -0.060; 0.42, -0.52 | 0.65 / 0.72 | 0.21 | 4/9 | 0.93; 0.94 / 0.38; 0.45 | none |
| D1 k1.5 h3 | PRE, IS, VAL | +18.64 (1.01) / +14.78 (0.57) | 5.9 | +12.73 (0.70) / -0.69 (-0.03) / +1.26 (0.10) | < 0 | +0.047 / -0.003; 0.41, -0.02 | 0.64 / 0.71 | 0.27 | 5/9 | 0.95; 0.94 / 0.59; 0.75 | none |
| D2 k1.0 h1 | PRE, IS, VAL | +2.20 (0.33) / +6.02 (0.61) | 4.4 | -2.22 (-0.33) / +0.96 (0.10) / -3.75 (-0.68) | n/a | -0.022 / +0.009 | -0.50 / -0.33 | -0.35 | 7/9 | 0.70; 0.45 / 0.77; 0.60 | none |
| D2 k1.0 h3 | PRE, IS, VAL | +2.79 (0.33) / +5.46 (0.41) | 6.5 | -3.70 (-0.44) / -1.46 (-0.11) / -3.85 (-0.49) | n/a | -0.029 / -0.010 | -0.59 / -0.44 | -0.86 | 5/9 | 0.71; 0.41 / 0.62; 0.60 | none |
| D2 k1.5 h1 | PRE, IS, VAL | -2.51 (-0.22) / +23.27 (1.23) | 4.2 | -6.71 (-0.59) / +17.62 (0.96) / -5.12 (-0.62) | n/a | -0.042 / +0.095 | -0.67 / -0.57 | -0.36 | 4/9 | 0.48; 0.25 / 0.96; 0.94 | none |
| D2 k1.5 h3 | PRE, IS, VAL | +1.86 (0.15) / +27.01 (1.09) | 6.2 | -4.37 (-0.36) / +19.71 (0.81) / -14.02 (-1.13) | n/a | -0.025 / +0.078 | -0.44 / -0.37 | -0.87 | 5/9 | 0.58; 0.54 / 0.92; 0.89 | none |
| D3 k1.0 h1 | PRE, IS, VAL | +12.53 (2.04) / +1.85 (0.17) | 5.8 | +6.71 (1.09) / -7.84 (-0.72) / +0.12 (0.02) | < 0 | +0.071 / -0.065; 0.62, -0.56 | 0.85 / 1.06 | 0.76 | 8/9 | 0.95; 0.89 / 0.33; 0.20 | none |
| D3 k1.0 h3 | PRE, IS, VAL | +16.75 (1.87) / +2.83 (0.20) | 8.5 | +8.23 (0.92) / -10.03 (-0.72) / +2.30 (0.21) | < 0 | +0.059 / -0.065; 0.51, -0.56 | 0.74 / 0.96 | 0.29 | 5/9 | 0.99; 0.91 / 0.18; 0.15 | none |
| **D3 k2.0 h1** | PRE, IS, VAL | +36.02 (2.56) / +1.12 (0.05) | 7.3 | **+28.76 (2.06)** / -15.69 (-0.70) / +0.83 (0.06) | < 0 | +0.148 / -0.068; 1.28, -0.59 | 1.93 / 2.05 | 1.74 | 7/9 | 0.99; 0.99 / 0.34; 0.31 | none (VAL < 0; mid t inside the null) |
| D3 k2.0 h3 | PRE, IS, VAL | +18.58 (0.88) / +10.74 (0.36) | 11.0 | +7.60 (0.36) / -11.05 (-0.37) / -2.18 (-0.10) | < 0 | +0.024 / -0.036; 0.21, -0.31 | 0.26 / 0.38 | 0.57 | 6/9 | 0.90; 0.69 / 0.40; 0.46 | none |
| D4 h1 (FX cross-section) | PRE, IS, VAL | -0.80 (-0.63) / +4.16 (2.70) | 1.3 | -2.07 (-1.64) / +3.18 (2.07) / -2.60 (-1.15) | n/a | -0.106 / +0.187 | -1.81 / -1.66 | -1.67 | 5/9 | 0.30 / 0.83 | none (IS and PRE < 0: VAL-only draw) |
| D4 h3 | PRE, IS, VAL | -0.95 (-0.44) / +2.17 (0.77) | 1.7 | -2.68 (-1.24) / +0.92 (0.32) / -1.47 (-0.39) | n/a | -0.079 / +0.029 | -1.33 / -1.30 | -0.97 | 2/9 | 0.41 / 0.47 | none |

Random control (a) = same sides on random tradable Fridays of the era, per market; (b) = the side recomputed from the
unthresholded signal at the random Friday. IS random beats near 0.9-0.99 mean only that random weekly trades lose
their cost; VAL beats are 0.07-0.4 for every D1 / D3 cell.

- **D3 k2.0 h1 by market (IS net, n):** silver +29.2 (t 2.03, n 49), Nikkei +29.8 (1.76, 48), CHF +10.6 (1.92, 30),
  DJ -50.9 (-2.33, 53); VAL silver -118.8 (n 9), Nikkei -22.9. Without BTC and gas (post hoc, information): IS +10.2
  (t 1.13), VAL -14.8 (-0.75).
- **Single-market cells (204):** IS net t > 2 in 3 cells, < -2 in 1, mean -0.04 (chance: about 5 each side). Best:
  D1 k1.5 h3 BTC +555 bp (t 2.41, n 12; VAL -76), D2 k1.0 h3 BTC +253 (2.18, n 34; VAL -157), D3 k2.0 h1 silver
  +29.2 (2.03; VAL -118.8). None has VAL > 0 with IS t >= 2.
- **Chance benchmark** (weeks sign-flipped jointly across cells, 500 draws, IS mid t): best of 14 book cells median
  1.79, p95 2.69 (observed best mid t 2.56, p ~0.1); best of 204 single cells median 2.87, p95 3.73 (observed best
  mid t 2.53).

## Fallback 2: JPX investor type in Nikkei 225 futures (HYPOTHESES_D part 3)
Rule recap: weekly net (buys - sells) of individuals (J1, faded) and foreigners (J2, followed) in Nikkei 225 Futures +
mini / 10, z vs the past 52 weeks (>= 40, so IS trades start 2016-10); public at ~15:30 JST on the 4th JP business day
of the next week (JPX note); entry 07:00 UTC (16:00 JST) that day on IC JP225, exit +1 / +3 weekdays at 07:00 UTC
(<= 120 h). IC spread both legs, JP225 swap. N1 (NAAIM) was dropped before any data: subscription only.
Same-week corr(individuals, foreigners) = -0.47: individuals take the other side of foreigners, as in cash (round 31).

| cell | eras | mid IS (t) / VAL (t) | net IS (t) / VAL (t) | Sharpe IS | x1.5 / +1 min IS t | ex 2020-03/04 IS t | years + | random IS / VAL (a; b) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| J1 fade individuals k1.0 h1 | IS, VAL | -4.35 (-0.34) / -33.10 (-1.58) | -10.12 (-0.79) n 76 / -38.91 (-1.86) n 41 | -0.090 | -0.95 / -0.91 | -1.62 | 3/9 | 0.43; 0.19 / 0.02; 0.03 | none |
| J1 k1.0 h3 | IS, VAL | +20.21 (0.83) / -19.14 (-0.46) | +10.00 (0.41) / -29.31 (-0.70) | +0.047 | 0.33 / 0.37 | -0.60 | 3/9 | 0.80; 0.77 / 0.21; 0.24 | none |
| J1 k1.5 h1 | IS, VAL | -20.29 (-1.27) / -8.99 (-0.26) | -25.84 (-1.61) n 38 / -15.06 (-0.43) n 20 | -0.261 | -1.72 / -1.77 | -2.15 | 1/8 | 0.16; 0.06 / 0.34; 0.41 | none |
| J1 k1.5 h3 | IS, VAL | +22.86 (0.55) / +11.66 (0.17) | +12.85 (0.31) / +0.85 (0.01) | +0.051 | 0.27 / 0.28 | -0.86 | 2/8 | 0.78; 0.65 / 0.60; 0.62 | none |
| J2 follow foreigners k1.0 h1 | IS, VAL | +0.85 (0.05) / -3.26 (-0.15) | -4.88 (-0.29) n 72 / -8.72 (-0.40) n 42 | -0.034 | -0.40 / -0.31 | -0.82 | 3/9 | 0.52; 0.50 / 0.38; 0.48 | none |
| J2 k1.0 h3 | IS, VAL | +13.88 (0.51) / -31.08 (-0.75) | +3.61 (0.13) / -41.24 (-0.99) | +0.016 | 0.06 / 0.13 | -0.52 | 3/9 | 0.76; 0.48 / 0.18; 0.42 | none |
| J2 k1.5 h1 | IS, VAL | +5.80 (0.18) / +16.42 (0.50) | -0.07 (-0.00) n 30 / +10.99 (0.33) n 24 | -0.000 | -0.06 / 0.00 | -0.79 | 4/8 | 0.59; 0.56 / 0.76; 0.83 | none |
| J2 k1.5 h3 | IS, VAL | +43.44 (1.03) / -1.02 (-0.02) | +33.37 (0.80) / -11.02 (-0.17) | +0.145 | 0.75 / 0.78 | -0.18 | 3/8 | 0.92; 0.86 / 0.53; 0.77 | none |

Best declared IS net t +0.80 (J2 k1.5 h3) against a best-of-8 median of ~1.5; no cell has IS t >= 2. Power at the
HOLD count (~35-75 trades) is <= 1.2 even at the best IS Sharpe. Neither the individuals' futures flow (faded) nor
the foreigners' (followed) predicts JP225 over 1-3 days; the individuals' side was if anything right in VAL (J1 k1 h1
mid -33 bp, t -1.58). This repeats round 31's cash-market result (X1 / X2) on the futures table.

## Exhausted after this stream (for PROMPT "Những họ đã cạn")
- CFTC COT non-reportable (small-trader) positions, level / change / against large speculators / FX cross-section,
  17 markets, 1-3 days after the Friday release (2005-24).
- JPX weekly derivatives trading by investor type (individuals faded, foreigners followed) in Nikkei 225 futures ->
  JP225, 1-3 days (2016-24).
- Free broker retail-sentiment archives: none with 2016-21 history is reachable without an account or payment (list
  above).

## Pitfalls
- www.dukascopy.com and www.myfxbook.com time out from this Mac (also in round 31); freeserv.dukascopy.com widgets
  answer 403 to anonymous requests.
- FXCM's free SSI files are one month (2018-01) only; the minute step makes them look large.
- JPX derivatives investor-type CSVs are coded: product 301 = Nikkei 225 Futures (value in kJPY), 313 = Nikkei 225
  mini (value in JPY); investor 50 = individuals, 60 = foreigners, 70 = brokerage total (= 30 + 50 + 60 + 41). The
  archive selector pages are `00-archives-NN.html` (02 = 2024 .. 10 = 2016; 01 = 2025, not fetched). The server serves
  ~1 file per 3 s.
- CFTC releases move after US federal holidays and were delayed in the 2013 and 2018-19 shutdowns: skip those weeks or
  date each release.

## Directions that need the user
| direction | value (chance of a LIVE candidate) |
|---|---|
| Dukascopy JForex demo account: SWFX sentiment history (30 min, 20+ FX pairs, metals, indices) via `IFXSentimentIndex` | DEMO ~3 %, LIVE ~1 % |
| FXCM premium SSI history (paid; ~32 symbols, minute step since ~2010) | DEMO ~3 %, LIVE ~1 % |
| OANDA order / position book (account; unchanged from round 31) | DEMO ~3-5 %, LIVE ~1 % |
| FXSSI / Myfxbook accounts (multi-broker ratios; history depth unknown, likely 2017+) | ~1 % |
| AAII / NAAIM paid history (weekly, US500 only; LIVE impossible from the count) | DEMO < 1 % |

## Scripts and outputs (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r39/D/`)
- `scripts/fetch.sh` (logged fetches), `scripts/peek_dates.py` (date range without values),
  `scripts/cot_parse.py` -> `out/cot_nonrep.json`, `scripts/build_panel.py` -> `out/panel.npz`,
  `scripts/common.py`, `scripts/run_cells.py` -> `out/cells.json`, `scripts/info_d3.py`, `scripts/jpx_run.py`.
- Downloads under `web/` (s1-s10), log `web/requests.log`.
