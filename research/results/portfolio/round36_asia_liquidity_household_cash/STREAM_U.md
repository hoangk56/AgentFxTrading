# Round 36, stream U: US household cash payments (Daily Treasury Statement) -> BTCUSD, ETHUSD, US2000, USTEC, US500

Written 2026-10-28, 01:44-02:12 UTC (`date -u`). Hypotheses with UTC times: [HYPOTHESES_U.md](HYPOTHESES_U.md).
- The 65 graded cells were declared at 01:50 UTC and amended at 01:52 UTC (EIP window), both before any return.
- Amendment 2 (01:56 UTC, after the IS / VAL results) only added a PRE check of the unchanged rules and recorded two
  directions not run on power grounds.
- HOLD (2025-01..2026-09) stayed closed: the DTS query was cut at `record_date:lte:2024-12-31`, IC marks at
  ts < 2025-01-01, Dukascopy requests stop at 2015-12, and no trade exits after 2024-12-31. Nothing from 2025-26 was
  printed or summarised.

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- 65 graded cells (5 families x 2-3 holds x 5 symbols), side fixed long. **None reaches DEMO's IS net t >= 2.0.**
- **Best registered-side cell: U3 h3 USTEC.** U3 is the household-cash surprise: the last 5 DTS days against the same
  window a year earlier. The cell is a 3-day long.
  - IS net +33.3 bp (t 1.90), VAL +55.2 (t 2.26); 8/9 years > 0; x1.5 and +1 min positive.
  - Random control 0.92 / 0.98. Power 1.02 at the IS size, 1.71 at the VAL size.
  - It fails DEMO on IS t. It would fail LIVE on power (< 3) even if HOLD kept the VAL size.
- **Chance.** Over the 52 non-ETH cells, one common circular shift of all signals (500 draws) gives a best long-side
  IS net t of p50 1.94, p95 2.77. The observed 1.90 is exceeded in 55 % of draws: **the best cell is what chance
  gives.**
- **The scheduled (calendar) dose does nothing.** This covers Social Security Wednesdays (~$15-28 bn each), the 1st /
  3rd (SSI, VA, retirement, legacy SS) and the IRS's in-season refund Wednesdays.
  - IS and VAL net t stay within -1.8..+1.4 on every index and on BTC, except U1b h1 BTC in VAL (-2.23, wrong side).
  - Dose response fails: SS Wednesdays inside the refund season carry the largest scheduled household dose of the
    year (SS + refunds), yet they do no better than SS-only Wednesdays.
- **The realised refund dose (U2) points the wrong way for small caps.**
  - US2000: IS -17.8 bp (t -1.41), VAL -14.2 (t -1.16) at 1 day, and negative at every hold in both eras.
  - US500, USTEC and BTC are flat.
- **EIP rounds (2020-21, information, 3 events).**
  - No consistent sign on any index or BTC at any entry: scheduled P-1, start of deposit posting, or DTS D+2.
  - The index moves are the 2020-21 market (-590..+500 bp), not something 3 events can attribute to payments.
  - This fits Greenwood-Laarits-Wurgler: the stimulus effect sat in high-retail-share single stocks, not in the
    value-weighted indices IC trades.
- **Open thread, post hoc and not registrable as is: U3 at 3 days on US500 / USTEC.**
  - It is positive in all three eras at mid. PRE 2012-15 is Dukascopy at 19:00, no cost: +46.8 / +50.2 bp, t 3.34 /
    2.93, against an always-long +16.5 / +22.5.
  - Against the always-long baseline the excess is +17-22 bp in IS (t ~1.2), +36-56 in VAL (t ~2.0-2.3) and +28-30
    in PRE (t 1.6-2.2).
  - The anatomy argues against a household-cash mechanism:
    - surprises built from any single component (calendar-only SS/SSI/VA, refunds only, unemployment only) give the
      same IS mid (+16..+53 bp);
    - 48 % of signals are calendar shifts (the window holds more payment days than last year's);
    - the IS gain sits in turn-of-month trades (+78 / +107), the VAL gain outside them (+50 / +85).
  - It looks like a generic "after a cluster of payment days" timing or noise, not a dose effect.

## Sources
| source | fetched | history used | usable? |
|---|---|---|---|
| DTS `deposits_withdrawals_operating_cash` (api.fiscaldata.treasury.gov), all withdrawals, `record_date:lte:2024-12-31`, 24 pages of 10,000 | 34 requests, ~42 MB | 2005-10-03..2024-12-31, 4,835 days, 238,748 rows | yes; row names spliced (below) |
| DTS deposits, 2 probe days | 2 requests | - | the non-withheld individual tax line is only separate from 2023-02; before that it sits inside "Cash FTDs" (so tax-payment doses are not measurable pre-2023) |
| Dukascopy H1 bid candles, USA500IDXUSD / USATECHIDXUSD, 2012-01..2015-12 (one month per file, one kept-alive connection) | 96 files | 896 / 909 days with a 19:00 bar | yes (PRE, information). USSC2000IDXUSD answers 503 in 2014 (not available) |
| CoinMetrics PriceUSD (round 31 C's local cache) | 0 | BTC 2011-04..2017-08 | PRE at mid, information |
| FRED graph CSV (NASDAQCOM to 2015) | 1 | - | **no**: timeout, as in rounds 9 and 32 |
| stooq.com | robots.txt only | - | **no**: `Disallow: /` for generic agents (not used) |
| Literature | 4 WebSearches | - | Greenwood, Laarits & Wurgler (RFS 2023); Divakaruni & Zimmerman (Mgmt Sci 2024); Gelman et al. (AER 2022); no paper links tax refunds to market-level returns |

- **DTS row splices:**
  - individual refunds: "IRS Tax Refunds Individual (EFT)" (an "Other Withdrawals" sub-row until 2012-09) ->
    "Taxes - Individual Tax Refunds (EFT)" (2023-02-14);
  - SS: "Social Security Benefits (EFT)" -> "SSA - Benefits Payments" (2021-07-19);
  - SSI: "Supple. Security Income Benefits (EFT)" -> "SSA - Supplemental Security Income";
  - EIP: its own row only from 2020-12-24, while **EIP1 is booked in the refund row** (2020-04-15: $150 bn);
  - unemployment: "Unemployment Insurance Benefits" -> "DOL - Unemployment Benefits" (2020-09-21);
  - VA: "Veterans Benefits (EFT)" -> "VA - Benefits" (2020-01-13).
- **Calendar check.** A rule-built SS calendar (preceding business day, `holidays.US`) matches 886 of the 890 DTS days
  with SS > $5 bn. The IRS in-season refund cycle moved from Friday (to 2011) to Wednesday (2012 on).
- **Dates.** The DTS books EIP2 / EIP3 on 2021-01-04 / 2021-03-17, a few days after deposits began posting.
- **Logging.** All 140 requests are logged in `web/requests.log`. No account, no e-mail, browser UA, >= 1.1 s between
  requests to one host, one job per host.

## Method (as declared)
- **Clock.** Entry and exit at the IC M1 bar at 19:30 UTC; the US cash session is open then all year.
  - Calendar rules enter at 19:30 on the trading day before payment day P (known years ahead).
  - DTS rules enter at 19:30 on D+2: DTS for D is out ~16:00 ET on D+1, after 19:30 UTC in both DST regimes.
  - Exit is h = 1 / 3 / 5 marks later. For h > 1, one trade at a time.
- **Families.**
  - U1a: SS 2nd / 3rd / 4th Wednesdays.
  - U1b: the 1st / 3rd.
  - U2: refunds over the last 5 DTS days above their trailing-250-day 80th percentile.
  - U2s: Wednesdays 15 Feb-30 Apr.
  - U3: the log ratio of all household cash over 5 DTS days to the same window a year earlier, above its trailing
    80th percentile.
- **Ex-EIP (graded).** A trade is dropped if its signal or holding window touches an EIP day +- 5 DTS days: 20 EIP
  days, 8 in 2020 and 12 in 2021. The full version is reported as well.
- **Costs.**
  - Fill long at the ask, exit at the bid. IC actual spreads; US2000 is bid + 0.34 pt.
  - Financing per rollover, Friday x3: US500 / USTEC from `swap_frac_at`; US2000 uses US500's; BTC and ETH -5 bp.
  - Hand check: U1a h1 US500, 2018-03-13 -> 03-14, from the raw M1 cache: mid -68.343 bp, net -71.99. The engine
    gives -68.343 / -72.002 (the half spread is taken on mid).
- **Statistics.**
  - t is over trades: one trade per entry day per symbol, so it is day-clustered.
  - Random control: 300 random entry sets of the same size and hold in the same era, long side.
  - Chance: a common circular shift (20-230 marks) of every cell's entries.
- **Eras.** IS 2016-21 (BTC from 2017-08-28, ETH from 2017-09-25), VAL 2022-24. PRE at mid: Dukascopy US500 /
  USTEC 2012-15 at 19:00, and CoinMetrics BTC 2011-04..2017-08 at end of day.

## Power (written before the numbers)
- LIVE needs a per-trade net Sharpe of 0.32-0.69, i.e. +30-65 bp on US500 at 1 day, or +145-310 bp on BTC.
- DEMO's IS t 2 needs 0.12-0.25.
- The literature implies a household-cash effect on value-weighted indices < 2 bp and on BTC < 10 bp per event, i.e.
  power ~0.0-0.3. The results agree.
- ETH cannot pass IS: IC's median spread at 19:30 was 99-264 bp in 2018-20.

## Results (registered side, ex-EIP; bp per trade)
The full 65-row table is in scratchpad `out/U_results.txt`. Shown below: the best cell of each family, each family's
US2000 / BTC row when informative, the U3 cells, and every |t| >= 2.

| cell | mid IS (t) | net IS (t) | net VAL (t) | cost IS / VAL | yrs+ | x1.5 / +1m IS, VAL | IS 2016-19 / 2020-21 net (t) | Sharpe IS / VAL | power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U1a h1 USTEC (best U1a) | +8.7 (1.12) | +5.0 (0.64) | +9.2 (0.67) | 3.8 / 3.5 | 7/9 | +4.1 / +5.5; +8.9 / +8.2 | +8.1 (1.11) / -3.4 | 0.045 / 0.065 | 0.34 / 0.51 | 0.57 / 0.72 | none |
| U1a h5 BTCUSD | +112 (1.19) | +61.6 (0.65) | +84.0 (1.11) | 50 / 39 | 5/8 | +54 / +64; +82 / +85 | +45.9 / +85.8 | 0.056 / 0.107 | 0.41 / 0.84 | 0.46 / 0.74 | none |
| U1a h3 US2000 | -16.7 (-1.05) | -24.7 (-1.55) | -34.1 (-1.30) | 8.0 / 10.0 | 4/9 | | +0.5 / -93.1 (-2.11) | < 0 | < 0 | 0.06 / 0.17 | none (wrong sign) |
| U1b h3 BTCUSD (best U1b) | +195 (1.44) | +157 (1.16) | -103 (-1.19) | 38 / 26 | 4/8 | | +224 / +40 | 0.169 / -0.198 | 0.73 / < 0 | 0.84 / 0.13 | none (sign flips) |
| U1b h1 BTCUSD | +0.2 (0.00) | -20.3 (-0.45) | -65.2 (**-2.23**) | 20 / 10 | 3/8 | | | < 0 | < 0 | 0.36 / 0.05 | none (wrong sign in VAL) |
| U2 h1 US2000 | -12.7 (-1.01) | -17.8 (-1.41) | -14.2 (-1.16) | 5.1 / 5.1 | 2/9 | | +1.5 / -109.5 | < 0 | < 0 | 0.02 / 0.16 | none (wrong sign) |
| U2 h3 BTCUSD (best U2) | +53.5 (0.36) | +13.4 (0.09) | +20.0 (0.23) | 40 / 26 | 4/7 | | +63.7 / -104.1 | 0.013 / 0.031 | 0.06 / 0.17 | 0.45 / 0.50 | none |
| U2s h1 USTEC (best U2s) | +4.5 (0.21) | +0.3 (0.02) | +3.8 (0.17) | 4.2 / 3.3 | 6/9 | | +23.0 (2.32) / -95.0 | 0.002 / 0.029 | 0.01 / 0.13 | 0.43 / 0.57 | none |
| U3 h1 USTEC | +17.9 (2.23) | +12.5 (1.55) | +6.9 (0.59) | 5.5 / 5.7 | 8/9 | +11.6 / +12.2; +6.6 / +7.7 | +9.6 (1.30) / +23.5 | 0.095 / 0.045 | 0.83 / 0.45 | 0.90 / 0.79 | none |
| **U3 h3 USTEC (best overall)** | +44.8 (2.56) | +33.3 (1.90) | +55.2 (**2.26**) | 11.4 / 13.8 | 8/9 | +32.4 / +33.5; +54.9 / +55.6 | +31.0 (2.13) / +43.4 | 0.154 / 0.238 | 1.02 / 1.71 | 0.92 / 0.98 | none (IS t < 2; power < 3) |
| U3 h3 US500 | +30.7 (2.01) | +20.6 (1.35) | +34.9 (1.96) | 10.0 / 12.3 | 9/9 | +19.8 / +20.7; +34.7 / +35.3 | +22.0 (1.90) / +14.3 | 0.109 / 0.207 | 0.72 / 1.49 | 0.91 / 0.99 | none |
| U3 h3 US2000 | +17.0 (0.85) | +6.2 (0.31) | +47.5 (1.81) | 10.8 / 13.7 | 7/9 | | +10.7 / -13.7 | 0.025 / 0.190 | 0.17 / 1.37 | 0.63 / 0.99 | none |
| U3 h3 BTCUSD | +134 (1.47) | +96.4 (1.06) | +159 (**2.27**) | 38 / 26 | 6/8 | | +76.5 / +153.5 | 0.102 / 0.236 | 0.67 / 1.72 | 0.78 / 0.98 | none |
| U3 h5 USTEC | +48.7 (2.05) | +31.2 (1.31) | +15.5 (0.43) | 17.5 / 21.8 | 7/9 | | +38.8 / -3.0 | 0.120 / 0.051 | 0.70 / 0.33 | 0.76 / 0.68 | none |
| ETHUSD, all families | | -82..-360 (to **-4.66**) | -150..+69 | 150-230 / 18-50 | | | | | | | none (IS cost) |

- **Full version (EIP days kept).** No verdict changes. U3 h3 USTEC IS +43.2 (t 2.65) and U3 h1 USTEC +18.3 (t 2.47):
  the EIP windows help U3 in IS, which is why ex-EIP was declared as the graded version.
- **Baskets** (US500, USTEC, US2000, BTC; mean per entry day): U3 h3 IS +24.6 (t 1.04), VAL +99.0 (t 3.33).
  - Every other family basket is within IS t -1.5..+1.1.
  - U1b h3 IS +46.5 (1.11), VAL -63.4 (-1.40).
- **Trade counts, IS / VAL** (indices; BTC about 30 % fewer in IS): U1a h1 199 / 108; U1b h1 120 / 64; U2 h1 248 / 147;
  U2s 52 / 32; U3 h1 266 / 169; U3 h3 152 / 90.

## Per family: cells, best registered-side cell, chance
| family | cells | best IS net t (cell) | its VAL net t |
|---|---|---|---|
| U1a SS Wednesdays | 15 | 0.77 (h5 USTEC) | 0.31 |
| U1b 1st / 3rd | 10 | 1.16 (h3 BTC) | -1.19 |
| U2 realised refund dose | 15 | 0.09 (h3 BTC) | 0.23 |
| U2s refund Wednesdays | 10 | 0.02 (h1 USTEC) | 0.17 |
| U3 household-cash surprise | 15 | 1.90 (h3 USTEC) | 2.26 |

- **All 65 cells.** Max |IS net t| is 4.66 (U2 h1 ETH, wrong side, from cost). The common-shift null over all 65 cells
  gives a max |t| of p50 4.40, p95 5.99; ETH's cost dominates it.
- **52 non-ETH cells, long side.** The null gives p50 1.94, p95 2.77; the observed 1.90 is exceeded in 55 % of draws.
  - For max |t| the null gives p50 2.13, p95 2.93; the observed is 1.90.
- **Nothing differs from chance.**

## Information (not graded)
- **Always-long baseline (ex-EIP, net).**
  - US500: h1 IS +0.8, VAL -0.9; h3 +4.1 / -0.8.
  - USTEC: h3 +11.6 / +1.0.
  - US2000: h3 -3.2 / -10.0.
  - BTC: h3 +41.5 / +21.6.
  - ETH: h1 IS -128.5 (from cost).
- **Dose response on SS Wednesdays (h1 mid, IS / VAL), refund season vs off season.**
  - US500: +2.4 vs +1.1, and +5.1 vs +8.5.
  - USTEC: +6.2 vs +9.3, and +14.6 vs +12.1.
  - US2000: -10.2 vs -0.9, and -0.1 vs +5.0.
  - BTC: -42 vs +6, and +72 vs +42.
  - No dose response.
- **EIP events** (mid bp at h1 / h3 / h5; the full grid is in `out/U_info.txt`).
  - US500, from P-1: EIP1 -203 / +44 / -325; EIP2 -125 / +87 / +201; EIP3 +19 / -107 / -141.
  - US2000, from P-1: -386 / -78 / -368; -173 / +406 / +502; +56 / -135 / -590.
  - BTC, from P-1: -210 / +239 / +7; +922 / +2431 / +4016 (the January 2021 rally); +407 / +577 / -128.
  - Sign and size depend on the event, not on the payment.
- **BTC PRE 2011-04..2017-08 (CoinMetrics, mid, end of day).**
  - Every family is positive, at t up to 3.4.
  - Always long is +74 bp / day (t 4.63), +291 / 3 days.
  - Per day, every family sits within the drift: U3 h1 +88, U2 h1 +101, U1a h1 +44 against +74. Nothing beyond the
    2011-17 bitcoin drift.
- **Index PRE 2012-15 (Dukascopy, 19:00 UTC, bid, no cost).**
  - US500, family vs always long:
    - U1a h1 +10.4 (1.13) vs +5.5;
    - U2 h1 +13.0 (1.57);
    - U2s h1 +34.1 (1.15, n 35);
    - U3 h1 +16.4 (2.14), h3 +46.8 (3.34), h5 +57.3 (2.85);
    - always long h3 +16.5 (1.91).
  - USTEC: U1a h5 +54.5 (2.50) vs +37.5; U3 h3 +50.2 (2.93) vs +22.5 (2.29).
  - Only U3 is clearly above the drift (+28-30 bp at 3 days). At IC 2016-17 costs (~10 bp at h3: spread + 3 nights
    of swap) U3 h3 would net about +37 / +40 bp against +6 / +12 for always long.
- **U3 anatomy (post hoc, h3 mid, IS / VAL).**
  - Surprise built from SS + SSI + VA only:
    - US500 +30.4 (2.18) / +22.3 (1.13);
    - USTEC +38.2 / +38.3.
  - Refunds only: US500 +34.9 (1.95) / +37.0 (1.60); USTEC +52.6 / +48.2.
  - Unemployment only: US500 +16.2 / +19.7; USTEC +32.4 / +30.6.
  - Larger surprises do better (US500 h3 net, above-median x: IS +36.2, VAL +36.7; below: +0.3 / +32.6). But every
    component taken alone, including the purely calendar-driven one, gives a similar IS mid, so the "dose" is not
    specific to the cash that reaches retail investors.
  - Trades touching the turn of month: IS +78 (2.85) / VAL +41 (1.09). Trades outside it: IS +6 (0.34) / VAL +51
    (2.57). The source of the gain changes between eras.

## What this says
- Cash paid by the Treasury straight to households is large, dated and partly scheduled. The data are clean and free
  back to 2005.
- At 1-5 days, it moves none of US500, USTEC, US2000 or BTC on the side the retail-flow story predicts.
  - The calendar part, known in advance, shows nothing.
  - The realised refund dose is flat to negative, and negative for small caps.
  - The literature's effect is in individual high-retail-share stocks during the 2020-21 stimulus rounds. Those
    rounds cannot recur as a tradable schedule, and even there the value-weighted market did not move.
- The one cell family with a positive sign in three eras (U3, 3 days) fails the IS bar. Its best cell is at the
  chance level of the 52 cells, and its anatomy does not support the mechanism.
- This completes the US fiscal-cash picture of round 32 L (TGA, RRP, withheld taxes) and round 13 N (tax and
  settlement days): Treasury cash flows, in or out, do not move IC's US index or crypto CFDs at 1-5 days.

## Directions that need the user
- **None that would change the verdict.**
  - Retail order-flow data (Nasdaq RTAT, broker app flows) is paid. It would measure the channel, not create a
    tradable dose. Value < 2 %.
  - Single-stock CFDs of high-retail-share names (the literature's locus) would need new symbols, and the dose only
    recurs with new stimulus. Value ~1 %.
- **U3 at 3 days on US500 / USTEC** could be written as a forward log with today's parameters unchanged: ~25-30 trades a
  year per symbol.
  - Its VAL-size power is 1.5-1.7, so LIVE is out of reach.
  - DEMO would need the IS bar, which it fails.
  - Value: low (DEMO-type information at best, ~2-3 %). I did not write a PREREG_DRAFT because no bar was met.
- **Not run, on power grounds:** quarterly estimated-tax deadlines (household cash out; ~4 events a year, LIVE
  needs a per-trade Sharpe >= 1.1, and the pre-2023 dose is not separable in the DTS); federal salary paydays (a
  smaller dose than the null SS Wednesdays).

## Files
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r36/U/scripts/`):

  | script | what it does |
  |---|---|
  | fetch.py | polite logged fetcher |
  | pull_dts.py | DTS withdrawals, cut 2024-12-31 |
  | parse_dts.py | `python -I` parser, category splices |
  | ucal.py | payment calendars, DTS signals, EIP windows |
  | marks.py | IC 19:30 / 19:31 / 15:00 marks, ts < 2025 |
  | run_U.py | 65 cells, random control, chance |
  | info_U.py | baseline, dose response, EIP events, BTC PRE, U3 anatomy |
  | info_U3dose.py, info_U3anat.py | post hoc U3 splits |
  | pull_duka_ka.py, info_pre.py | Dukascopy 2012-15 index PRE |

- Outputs (`out/`): `U_results.txt` / `.json`, `U_info.txt`, `U_info_u3dose.txt`, `U_info_u3anat.txt`, `U_pre.txt`.
- Downloads: `web/` (with `requests.log`).
