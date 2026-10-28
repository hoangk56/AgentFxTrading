# Round 32, stream L: US liquidity and fiscal cash flows (DTS, NY Fed reverse repo, Fed H.4.1)

Written 2026-10-27, 18:43-19:05 UTC (`date -u`). Hypotheses with UTC times: [HYPOTHESES_L.md](HYPOTHESES_L.md). L1-L6
were declared at 18:50 UTC, before any return was computed. L7 was added at 18:57 UTC, after L1-L6 were in and
before any L7 number. HOLD (2025-01..2026-09) stayed closed:
- every new series was cut at 2024-12-31, at the API query where possible and otherwise in the parser;
- IC prices were cut at ts < 2025-01-01 when loaded;
- exits that would land in 2025 were dropped.

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- 82 graded cells: 66 for L1-L5 and 16 for L7. None reaches the DEMO bar's IS net t >= 2.0 on its registered side.
  - The best is L1a h1 US500 (weekly net liquidity, 1-day hold): IS net +9.3 bp (t 1.43), VAL +6.7 (t 0.73), power
    0.77 / 0.55.
  - The largest |IS net t| anywhere is 2.29, on the wrong side (L3 k5 USTEC). The shared circular-shift null gives a
    max of p50 2.98 and p95 3.83, and 97 % of null draws exceed the observed max. L7: max 1.44 against a null p50 of
    2.71.
- **The "net liquidity drives equities" thesis does not hold at 1-5 days.**
  - Weekly changes of WALCL - TGA - RRP give a mid of +7 bp a day on the 7-leg basket (IS t 1.88). That is far below
    the ~+15 bp a day (rho ~0.18) that LIVE needs.
  - At 5 days the sign is not stable: basket IS +8.1, VAL -4.2.
  - Fed asset changes alone point the **wrong** way: the IS basket at 5 days is net -17.5 bp (t -2.12), and VAL
    -29.7 (t -2.23). This is consistent with QE being announced, and priced, before the balance sheet moves.
- **Realised Treasury / RRP cash drains (DTS, daily) carry no IS signal.**
  - The tails (|z| > 1.5) are negative in IS 2016-21 and strongly positive in VAL 2022-24: basket VAL net +27.6 bp,
    t 2.74, 59 events, random control 1.00. IS is -3.9 (t -0.65).
  - This VAL-only pattern is post hoc, not registrable, and has the round-18 signature of a regime (it is also
    positive in 2011-14 and negative in 2009-10 and 2015-21).
- **Scheduled TGA rebuilds after debt-ceiling resolutions** (L4, 9 events 2013-23) go against the "drain" story: the
  indices rose in the week after 5 of the 5 IC-era resolutions with prices.

## Sources
| source | fetched | history used (cut 2024-12-31) | usable? |
|---|---|---|---|
| DTS operating cash balance, `api.fiscaldata.treasury.gov/.../v1/accounting/dts/operating_cash_balance` (query `record_date:lte:2024-12-31`) | 2 pages, 6.9 MB | TGA close 2005-10-03..2024-12-31, 4,835 days | yes. The row name changes in 2021-10 and 2022-04; from 2022-04-18 the amount sits in `open_today_bal` of the "Closing Balance" row. Before 2008 Treasury cash was mostly in commercial-bank TT&L accounts (TGA ~$5 bn), so the reserve channel exists from ~2009: PRE = 2009-15. |
| DTS federal tax deposits (`federal_tax_deposits`), withheld income and employment taxes | 1 request | 2005-10-03..2023-02-13 (the table stops) | yes, spliced with the next row |
| DTS deposits / withdrawals, "Taxes - Withheld Individual/FICA" | 1 request (`record_date` 2021-01-01..2024-12-31) | 2023-02-14..2024-12-31 | yes. Monthly totals are continuous across the splice (Jan-23 288 bn old; Feb-23 264, Mar-23 313 new). |
| NY Fed reverse-repo results, `markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json`, one query per year | 12 requests | 2013-04-02..2024-12-31, 2,825 operation days | yes. Material only at quarter-ends 2014-20 and from 2021-03. |
| Fed H.4.1, federalreserve.gov DDP full-release zip (SDMX XML, 127 MB) | 1 request | Wednesday levels 2002-12-18..2024-12-25 (1,150 weeks) of total assets (RESPPA_N.WW = WALCL), TGA (RESPPLLDT_N.WW), ON RRP "others" (RESPPLLRD_N.WW) and reserve balances (RESH4R_N.WW) | yes. The zip contains 2025-26 values; the parser drops them before storing. Note: the Fed says DDP's "Build your package" is being retired the week of 9 November; the full-release zip may follow. |
| FRED | 1 request | - | **no**: hung, as in round 9 (not needed) |

- All 30 requests are logged in the scratchpad `web/requests.log`: 27 at 200, 2 at 400 (empty pages past the end) and
  1 timeout (FRED).
- No account, no e-mail, browser UA, >= 1.1 s between hits to a host. 0 WebSearches.

## Publication lags and protocol (as declared)
- **Mark:** 15:00 UTC each US business day (the DTS calendar).
- **Fills and exit:** fill at the 15:00 bar close (bid / ask); +1 min variant at the 15:01 bar. Exit at the 15:00 bar
  h marks later.
- **DTS** for day D is used at the mark on D+2. **RRP** results are public at D+1, but are aligned to the DTS day.
- **H.4.1** (Wednesday W) is used at the Friday mark, or at Monday's if Thursday was a holiday. Checks:
  - 2016-11-23 -> 2016-11-28 (Thanksgiving);
  - 2019-12-25 -> 2019-12-27.
  - One quirk: the DTS file has a record for 2020-07-03, an observed federal holiday, so it counts as a mark.
- **Costs:**
  - actual half spreads at entry and exit;
  - 0.6 bp commission for FX / gold;
  - swap per rollover from `swap_frac_at`: triple on Wednesday for FX / gold and on Friday for indices; US2000 uses
    US500's swap;
  - US2000's spread is the published 0.34 pt;
  - PRE: Dukascopy bid plus IC's 2016-17 median spread at 15:00 (EURUSD 0.0, USDJPY 0.18, XAUUSD 0.87 bp) + 0.6 bp.
- **Checks:**
  - one trade recomputed by hand from the raw M1 cache: mid -57.451 bp; net -60.413 = -59.455 spread-adjusted
    - 0.97 swap, equal to the table;
  - every entry is one per mark (or one basket number per event), so t is day-clustered.

## Power (written before the numbers; HYPOTHESES_L.md)
| rule | trades / yr / symbol | LIVE per-trade Sharpe | LIVE edge US500 / EURUSD | rho needed | DEMO (IS t 2) rho |
|---|---|---|---|---|---|
| daily, 1-day hold (L2, L3 k1, L7a) | ~250 | 0.144 | ~15 / ~7 bp | ~0.18 | ~0.065 |
| weekly, 5-day hold (L1 h5, L2 k5, L7b) | ~50 | 0.316 | ~78 / ~30 bp (incl. cost and swap) | ~0.40 | ~0.14 |

- Prior from the sources: the practitioner charts relate **levels** of net liquidity to the S&P 500 in a trending
  2020-22 sample. That says nothing about 1-5 day changes.
- The academic evidence is about money markets: Afonso et al. 2020; Correa, Du & Liao 2020.
- Expected rho <= 0.05, which gives power ~0.8 (daily) and ~0.7 (weekly). LIVE needed 3-4x that before anything was
  run.

## Results (registered side; bp per trade, mid and net with t; PRE = 2009-15, FX and gold only)
Full 66-row table: scratchpad `out/L_results.txt`; L7: `out/L7_results.txt`. Shown below: the best cell of each
family, the basket rows and any row with |t| >= 2 in an era.

| cell | PRE mid / net (t) | IS mid (t) | IS net (t) | VAL net (t) | VAL/IS | yrs+ | x1.5 / +1m IS | power IS / VAL | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| L1a h1 US500 (weekly NL, Fri->Mon) | - | +14.9 (2.28) | +9.3 (1.43) | +6.7 (0.73) | 0.72 | 8/9 | +8.6 / +9.1 | 0.77 / 0.55 | 0.95 / 0.90 | none (IS t < 2) |
| L1a h1 BASKET | +0.6 / -0.6 (-0.22) | +7.0 (1.88) | +3.3 (0.88) | +3.8 (0.60) | 1.15 | 8/9 | +2.8 / +3.2 | 0.47 / 0.45 | 0.86 / 0.83 | none |
| L1a h5 BASKET | +4.6 / +1.8 (0.27) | +8.1 (0.98) | +0.4 (0.05) | -11.1 (-0.82) | < 0 | 4/9 | -0.1 / +0.2 | 0.02 / -0.63 | 0.66 / 0.47 | none |
| L1a h5 USDJPY | -11.9 / -14.6 (-2.04) | +5.7 (0.83) | +3.0 (0.43) | -13.2 (-1.09) | < 0 | 4/9 | | 0.23 / -0.83 | 0.86 / 0.36 | none (PRE wrong side) |
| L1b h1 BASKET (\|x\| > 1) | +6.0 / +4.8 (0.94) | -1.2 (-0.11) | -4.8 (-0.45) | +17.2 (1.19) | < 0 | 5/9 | | -0.24 / 0.90 | 0.29 / 0.94 | none |
| L1b h5 BASKET | -7.5 / -10.2 (-0.85) | -11.5 (-0.55) | -18.5 (-0.88) | -17.6 (-0.67) | | 3/9 | | < 0 | 0.17 / 0.37 | none |
| L2 k1 XAUUSD (best L2 k1) | +1.4 / -0.4 (-0.13) | +4.1 (1.82) | +2.4 (1.08) | +3.8 (1.15) | 1.6 | 6/9 | +2.0 / +2.6 | 0.58 / 0.87 | 0.67 / 0.88 | none |
| L2 k1 BASKET | +0.7 / -0.6 (-0.43) | +0.8 (0.50) | -1.7 (-1.05) | +2.1 (0.75) | < 0 | 3/9 | | -0.56 / 0.57 | 0.65 / 0.74 | none |
| L2 k5 US30 (best L2 k5) | - | +25.5 (1.99) | +15.4 (1.20) | -3.4 (-0.18) | < 0 | 7/9 | +14.9 / +15.3 | 0.64 / -0.14 | 0.68 / 0.78 | none (decays) |
| L2 k5 EURUSD | +7.1 / +4.6 (0.59) | -8.8 (-1.61) | -11.6 (**-2.11**) | -0.9 (-0.10) | | 4/9 | | -1.13 / -0.08 | 0.26 / 0.55 | wrong side in IS |
| L2 k5 BASKET | +0.3 / -2.4 (-0.36) | +5.5 (0.69) | -2.1 (-0.26) | +1.6 (0.11) | | 5/9 | | -0.14 / 0.08 | 0.43 / 0.81 | none |
| L3 k1 BASKET (\|z\| > 1.5) | +5.1 / +3.8 (0.74) | -1.5 (-0.24) | -3.9 (-0.65) | **+27.6 (2.74)** | < 0 | 5/9 | -4.5 / -3.5 | -0.35 / 2.08 | 0.42 / 1.00 | none (VAL only) |
| L3 k1 US2000 | - | -4.3 (-0.35) | -8.3 (-0.67) | +64.5 (2.95) | < 0 | 5/9 | | -0.36 / 2.24 | 0.34 / 1.00 | none (VAL only) |
| L3 k1 XAUUSD | +4.9 / +3.2 (0.35) | -8.1 (-1.08) | -10.0 (-1.34) | +31.7 (2.56) | < 0 | 4/9 | | -0.72 / 1.95 | 0.07 / 1.00 | none (VAL only) |
| L3 k1 EURUSD | +5.1 / +4.1 (0.81) | -7.0 (-1.84) | -7.9 (**-2.08**) | +5.0 (0.70) | | 2/9 | | -1.12 / 0.53 | 0.03 / 0.76 | wrong side in IS |
| L3 k5 USTEC | - | -101.7 (-2.07) | -112.3 (**-2.29**) | +1.5 (0.02) | | 4/9 | | -1.23 / 0.02 | 0.01 / 0.53 | wrong side in IS, n 33 |
| L3 k5 USDJPY | +15.0 / +12.0 (0.61) | +3.6 (0.17) | +1.2 (0.05) | +85.0 (2.58) | | 6/9 | | 0.03 / 1.96 | 0.76 / 0.99 | none (VAL only, n 18) |
| L3 k5 BASKET | -20.8 / -23.5 (-1.29) | -36.1 (-1.33) | -42.9 (-1.57) | +47.2 (1.14) | < 0 | 5/9 | | -0.84 / 0.86 | 0.07 / 0.96 | none |
| L5 scarce reserves, L2 k5 basket | n 7 | +11.0 (1.25) | +3.2 (0.37) | +13.9 (0.71) | 4.3 | 6/8 | +2.6 / +3.0 | 0.21 / 0.54 | 0.51 / 0.93 | none |
| L5 ample reserves | +1.1 / -1.7 (-0.25) | -7.3 (-0.42) | -14.5 (-0.84) | -10.3 (-0.50) | | 1/5 | | < 0 | 0.61 / 0.38 | none |
| L7a h1 BASKET (withheld-tax acceleration) | -1.2 / -2.5 (-1.79) | +2.1 (1.23) | -0.4 (-0.23) | -0.0 (-0.02) | | 6/9 | | -0.12 / -0.01 | 0.77 / 0.60 | none |
| L7a h1 US30 (best L7) | - | +4.0 (1.46) | +1.3 (0.48) | +1.5 (0.43) | 1.2 | 6/9 | +0.9 / +1.3 | 0.26 / 0.33 | 0.73 / 0.64 | none |
| L7b h5 BASKET | +6.3 / +3.5 (0.52) | +1.4 (0.17) | -6.0 (-0.75) | -21.2 (-1.86) | | 2/9 | | -0.40 / -1.42 | 0.48 / 0.24 | none |
| L7b h5 USDJPY | +14.7 / +11.9 (1.63) | -2.3 (-0.33) | -5.0 (-0.71) | +9.5 (0.77) | | 7/9 | | -0.38 / 0.59 | 0.50 / 0.71 | none (PRE mid t 2.01 only) |

Trade counts:
- weekly L1: 314 IS, 156 VAL, 366 PRE entries;
- daily L2 k1: ~1,500 IS, ~750 VAL, ~1,760 PRE;
- L2 k5: ~300 / ~150 / ~350;
- L3 k1 tails: 156 IS, 59 VAL, 205 PRE;
- L3 k5 tails: 33 / 18 / 46;
- L1b: 77 / 33 / 99.

## Per family: cells, best registered-side cell, chance
| family | cells | best IS net t (cell) | its VAL net t |
|---|---|---|---|
| L1a weekly net liquidity, every week | 16 | 1.43 (h1 US500) | 0.73 |
| L1b weekly, \|x\| > 1 | 16 | 0.68 (h1 USDJPY) | -0.56 |
| L2 daily TGA + RRP flow | 16 | 1.20 (k5 US30) | -0.18 |
| L3 tails of L2 | 16 | 0.42 (k1 USTEC) | 1.79 |
| L5 reserve scarcity | 2 | 0.37 (scarce) | 0.71 |
| L7 withheld-tax nowcast | 16 | 0.48 (h1 US30) | 0.43 |

- **Chance benchmark.** For L1-L5, a circular shift of each signal against prices by >= 26 weeks, shared by all 66
  cells, 500 draws. Max |IS net t|: p50 2.98, p95 3.83. The observed 2.29 is exceeded in 97 % of draws.
- For L7 (16 cells, 300 draws): p50 2.71, p95 3.70; observed 1.44.
- With 82 independent normal tests, the p95 of max |t| would be ~3.3.
- **Nothing differs from chance**, and no registered-side cell reaches IS t 2.

## Information (not graded)
- **Side mix and baseline.**
  - L1a goes risk-side 57 % of IS weeks and 48 % of VAL weeks. An always-long US500 at the same Friday -> Monday marks
    makes mid +7.2 IS and +3.4 VAL. L1a h1 US500's +14.9 / +11.1 therefore adds about +7 bp over the baseline, at
    IS mid t 2.28 (2.79 without 2020-Q2).
  - Net, the cell stays at t 1.43 / 1.78 (ex-2020-Q2). It has no PRE (no index data) and is a weekend hold.
  - The edge comes from the TGA component in IS (mid t 2.30) and the RRP component in VAL (mid t 2.04). The
    components do not agree across eras.
- **L1 components** (basket, 5-day hold):
  - Fed assets alone: IS net -17.5 (t -2.12), VAL -29.7 (t -2.23). Rising assets come before falling risk assets.
  - TGA alone: IS -2.0, VAL -21.3.
  - RRP alone: IS -3.6, VAL +15.4. The RRP component is the one the 2022-23 practitioner thesis relied on.
- **Without 2020-03..06:** nothing changes sign.
  - L2 k5 US500 mid rises to +28.2 (t 2.80), net +17.3 (t 1.72) in IS, but VAL is -5.5.
  - It is the "IS-only, decays" pattern.
- **L3 k1 decomposition (post hoc).** By year, the basket net per event is:
  - 2009-10: < 0;
  - 2011-14: > 0 (+5 to +20);
  - 2015-21: <= +2 in every year;
  - 2022 +23.9, 2023 +19.0, 2024 +37.7.
  - In VAL, both RRP-dominated days (+25.7, t 2.01) and TGA-dominated days (+30.3, t 1.83) contribute. The largest
    part is "drain" days, where the rule sells risk: +55 bp, t 2.57, n 18.
  - Quarter turns contribute least (+9.5).
  - It is a 2022-24 regime (the QT / RRP-drain years), not a stable mechanism. It could only be registered as a new
    rule with a VAL-era design, and round 18 says such picks keep ~1/4 of their size.
- **L4, debt-ceiling resolutions** (short risk, 5 marks after the resolution; bp per symbol in the scratchpad file):
  - US500 net over the 5 IC-era events with prices: -107, -317, -114, -191, -40. The indices **rose** after every
    resolution. The +10-business-day window is mixed.
  - The TGA-rebuild "drain" did not show up in index prices within 1-3 weeks.
- **L6, RRP alone, 2021-03..2024:**
  - VAL basket net -14.5 (t -1.02); no symbol positive in VAL;
  - 2021 (43 trades) +6.0.

## What this says
- Fiscal and central-bank cash flows are large, public and partly scheduled, but at 1-5 days they do not move US
  index CFDs, gold, EURUSD or USDJPY on the side the mechanism predicts.
- Fed balance-sheet growth (QE) points the wrong way: it follows market stress.
- The TGA and RRP components change sign between 2016-21 and 2022-24.
- This matches round 13 N (Treasury settlement and tax days, no dose response) with a different construction:
  realised daily drains from the DTS instead of scheduled settlements, and weekly net liquidity instead of event
  dummies.
- The money-market effects documented in the literature (repo spikes, the dollar basis) stay in money markets.

## Directions that need the user
- **None that would change the verdict.**
  - Intraday Treasury cash data (Fedwire / TGA intraday) and repo-rate tick data are not public.
  - Paid futures data (SOFR, T-bill futures) would only refine a channel that shows no 1-5 day effect here. Value
    estimate: < 2 % chance of a LIVE candidate.
- The only open thread is the post-hoc L3 k1 VAL pattern (tails of the realised TGA + RRP drain, 2022-24). Testing it
  cleanly needs data after 2026-09-24 and a rule registered now on the VAL design.
  - It averages ~20 events a year, so even at the VAL size (per-trade Sharpe 0.36) its power over 21 months is
    ~2.1. At a 1/4 retention it is ~0.5.
  - Value: low (DEMO at best, ~3-5 %).

## Files
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/L/scripts/`):

  | script | what it does |
  |---|---|
  | fetch.py | polite logged fetcher |
  | parse_dts.py, parse_rrp.py, parse_h41.py | `python -I` parsers with the 2024-12-31 cut |
  | marks.py | 15:00 / 15:01 / hourly mark prices; IC < 2025, Dukascopy 2009-15 |
  | run_L.py | L1-L5 cells, random control, circular-shift null |
  | info_L.py | the information runs |
  | run_L7.py | L7 |

- Outputs: `out/L_results.txt` / `.json`, `out/L_info.txt`, `out/L7_results.txt`.
- Downloads: `web/` (with `requests.log`).
