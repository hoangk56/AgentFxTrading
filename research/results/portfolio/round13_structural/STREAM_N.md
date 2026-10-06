# Round 13, stream N: structural calendar flows (tax dates, Treasury settlement, bond-index extension, fiscal-year ends, quarter-end funding, Chinese tax period)

Hypotheses, with UTC times written before their numbers: [HYPOTHESES_N.md](HYPOTHESES_N.md). Eras: PRE 2004-15
(Dukascopy H1 bid; FX and XAU only), IS 2016-21, VAL 2022-24 (IC panel, mid). HOLD was never loaded: the panel ends
2024-12-31, every price lookup refuses times >= 2025-01-01, and windows that would end in 2025 were dropped.

## Answer

**No candidate. No cell meets DEMO or LIVE on its registered side, so there is no PREREG_DRAFT.**
- Cells: 51 declared, plus 6 for N8 (bills, declared later but before its numbers) and 1 post hoc (N7).
- Best registered-side IS t: 2.68 (N2a, long US30 the day after a large net coupon settlement). It is +27.9 bp IS
  (6/6 years), then -9.6 bp in VAL: it decayed.
- The largest |t| anywhere is on the wrong side: year-end USD, IS t -4.25 on 6 events. That is below the sign-flip
  null's 95th percentile of 5.00. The null is wide because many cells have only 6-25 events.
- None of the mechanisms shows the gotobi signature: the same sign in PRE, IS and VAL. When PRE has a |t| near 2,
  IS or VAL reverses it.
- The DEMO tier was the realistic target, and these mechanisms do not reach it. All the dated flows are 1-day to
  5-day effects, and their sd (35-100 bp) swamps the events: 4-24 a year, or 35-50 a year for bills.

## Calendars (built without prices)
| calendar | source | events 2004-24 |
|---|---|---|
| US corporate estimated-tax days | IRS rules (Pub. 509 / Form 1120-W: 15 Apr, Jun, Sep, Dec); IRC 7503 next business day incl. DC Emancipation Day; Notice 2020-23 (Apr+Jun 2020 -> 15 Jul); corporate annual due 15 Mar through tax year 2015; IR-2021-59 (17 May 2021) | 97 |
| Treasury coupon settlements, net of maturing coupons | fiscaldata.treasury.gov `v1/accounting/od/auctions_query` (11,140 auctions 1979-2025). Net = public offering amounts - `est_pub_held_mat_by_type_amt` (2008+), or maturing original offerings (2004-07). Check: 16 Sep 2019 net +$54 bn, as Afonso et al. (2020) report | 615 settlement days |
| Treasury bill settlements, net | same API, Bills incl. CMBs | 1,547 |
| Month-ends | last US business day (NYSE + federal holidays); Bloomberg index methodology: rebalance on the last business day of the month | 252 |
| Fiscal year-ends | JP 31 Mar / 30 Sep, AU 30 Jun, NZ 31 Mar; home business days from the `holidays` package (0.105) | 84 |
| Chinese tax deadlines | 15th, extended per the Implementing Rules of the Tax Collection Law art. 109 (CN holidays from `holidays`; make-up working weekends are not modelled, so some deadlines may be a day off) | 108 (2016-24) |

Literature used for the sides:
- Hartley & Schwarz (2019, SSRN 3440417): Treasury excess returns are positive only in the last few days of the
  month; life insurers buy on index rebalancing dates.
- Afonso, Cipriani, Copeland et al. (2020): the mid-September 2019 repo spike, on the tax day plus a large net
  coupon settlement.
- Du, Tepper & Verdelhan (2018) and Aldasoro, Ehlers & Eren (2022): quarter-end dollar funding.
- Etula, Rinne, Suominen & Vaittinen (2020, RFS): payment-cycle flows, used for N7.

## Conventions
- USD3 = long USD vs EUR, JPY and GBP, equal notional (3 positions). One number per event (the legs' mean); t is
  across events.
- Windows run on the hour in New York time. Day-type cells end at 16:00 ET, before the 17:00 ET rollover.
- Costs follow the brief:
  - half the actual spread at entry and at exit;
  - 0.6 bp commission for FX and gold;
  - swap from `swap_frac_at`, counting every rollover;
  - indices: -2 bp per night when long;
  - PRE: IC's 2016-17 median spread at that minute of day.
- Variants: x1.5 spread and +1 minute (IS/VAL).
- Random entries: same weekday and year, non-event days, 500 seeds. The short-side pool uses the short side's own
  swap.
- Power = per-trade net Sharpe x sqrt(events a year x 1.73), on the IS and on the VAL Sharpe.

## Results (registered side; bp per event, mid gross with t; net = after costs)

| cell (mechanism) | where | PRE g (t) | IS g (t) | VAL g (t) | cost IS/VAL | net IS (t) / VAL | VAL/IS | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| N1a tax day, long USD | USD3 | -7.3 (-1.04) | -8.6 (-1.04) | +5.3 (0.28) | 0.9 / 0.3 | -9.5 (-1.14) / +5.0 | -0.61 | -0.61 / 0.20 | fails |
| N1a tax day, short gold | XAU | +1.4 (0.07) | -7.5 (-0.48) | -3.6 (-0.11) | 1.4 / -0.4 | -8.9 / -3.2 | 0.47 | < 0 | fails |
| N1a tax day, short US30 | US30 | - | -15.5 (-1.11) | +9.9 (0.37) | 0.9 / 0.3 | -16.3 / +9.6 | -0.64 | < 0 / 0.28 | fails |
| N1b 2 days before, long USD | USD3 | -12.8 (-1.37) | +7.3 (0.78) | +10.7 (0.35) | 0.8 / -0.1 | +6.6 (0.70) / +10.8 | 1.46 | 0.37 / 0.27 | fails (IS t) |
| N1b 2 days before, short gold | XAU | +45.1 (1.69) | +20.9 (1.02) | +21.2 (0.37) | 0.9 / -2.2 | +20.0 (0.98) / +23.5 | 1.02 | 0.52 / 0.31 | fails (IS t); the only stable sign in 3 eras; gross > 0 in 13 of 21 years |
| N1b, short US30 | US30 | - | -21.7 (-1.05) | +45.0 (0.90) | | -22.5 / +44.7 | -2.08 | | fails |
| N1c 2 days after, short USD | USD3 | +21.3 (2.02) | +2.8 (0.22) | -16.4 (-1.75) | 2.1 / 2.8 | +0.6 / -19.2 | -5.9 | 0.03 / -1.56 | fails; PRE effect gone |
| N1c after, long gold / long US30 | XAU / US30 | +30.9 (1.16) / - | -11.2 / -7.1 | -14.0 / -46.8 | | < 0 | | | fails |
| N1d tax day with big net coupon settlement | USD3 / XAU / US30 | +34.8 (1.84) / +32.7 (1.09) / - | -13.2 (-1.83) / -44.1 (-2.12) / -6.5 | +4.1 / +3.0 / +10.5 | | < 0 IS | | | fails (IS wrong sign) |
| N2a large net coupon settlement day | USD3 / XAU / US30 | +3.3 (0.57) / +13.3 (0.87) / - | -0.8 / -1.5 / +8.0 (0.49) | +9.4 (1.08) / +5.1 / +5.0 | 0.8 / 1.4 / 1.0 | IS -1.6 / -2.9 / +7.1 (t 0.43) | | <= 0.2 | fails |
| N2a day after, reversal | USD3 | -2.0 | -5.4 (-1.34) | -0.6 | 1.5 | -6.9 / -2.1 | | | fails |
| N2a day after, long gold | XAU | +4.2 (0.26) | +7.6 (0.87) | +37.1 (2.23) | 2.2 / 2.7 | +5.4 (0.61) / +34.4 (2.06) | 4.9 | 0.28 / 1.95 | fails (IS t); VAL-only |
| **N2a day after, long US30** | US30 | - | **+27.9 (2.68)**, 6/6 yrs | -9.6 (-0.71) | 3.2 / 2.3 | +24.8 (2.37) / -11.9 | -0.34 | 1.10 / -0.83 | **fails VAL (decayed)**; rnd 96 % IS |
| N2b refunding settlement day (15 Feb/May/Aug/Nov) | USD3 / XAU | +2.6 / +15.7 | +10.0 (1.33) / +0.6 | -3.3 / +1.5 | 0.8 / 1.3 | +9.2 (1.23) / -3.6 | -0.33 | 0.66 / -0.19 | fails |
| N2b refunding day, short US30 | US30 | - | -36.7 (-2.62) | -35.5 (-1.67) | | -37.6 / -35.8 | | | wrong sign (US30 rises; see N7) |
| N2b day after, reversal | USD3 | -11.3 (-2.06) | +11.7 (1.33) | +12.7 (1.30) | 1.6 / 1.9 | +10.1 (1.15) / +10.8 (1.10) | 1.09 | 0.62 / 0.83 | fails (IS t); PRE opposite |
| N2c dose slope (per sd of net settlement) | USD3 / XAU / US30 | +2.5 (0.95) / -0.8 / - | +0.5 (0.17) / -3.6 (-0.61) / +1.6 (0.22) | -0.9 / +1.1 / +7.0 (0.67) | | | | | no dose-response |
| N3a month-end 13-15 ET into the bond snapshot, short USDJPY | USDJPY | +1.2 (0.82) | +0.7 (0.55) | +3.4 (0.95) | 0.7 / 0.7 | +0.0 / +2.6 | 4.5 | 0.00 / 0.56 | fails |
| N3a same, long gold | XAU | +2.2 (0.77) | -1.2 (-0.49) | -6.7 (-1.67) | 1.5 / 1.0 | -2.7 / -7.7 | | | fails |
| N3b last 3 days (Hartley-Schwarz) | USDJPY / XAU | +4.5 (0.51) / +3.5 (0.24) | +0.2 / -7.6 | +4.7 / +8.4 | 2.9-7 | < 0 | | | fails |
| N3c after the snapshot 15-16 ET, reversal | USDJPY | -0.4 (-0.48) | +0.6 (0.60) | +3.8 (1.70) | 0.7 / 0.7 | -0.2 / +3.0 (1.36) | 6.8 | -0.11 / 1.03 | fails (IS) |
| N3c same | XAU | -0.7 (-0.42) | +2.9 (1.54) | +3.4 (1.02) | 1.6 / 1.1 | +1.3 (0.69) / +2.3 | 1.18 | 0.37 / 0.53 | fails (IS t, PRE sign) |
| N3d refunding-month 13-15 ET | USDJPY / XAU | +0.3 / -1.9 | +1.8 (0.83) / +4.5 (1.16) | +11.1 (1.22) / -1.2 | 0.7 / 1.5 | +1.1 / +10.4; +2.9 / -2.2 | | <= 0.9 | fails |
| N4 JP 31 Mar, 5 days before / after | USDJPY | -39.0 / +103.7 (2.54) | -4.1 / -37.1 | -32.8 / +54.6 | 4 / 2-10 | < 0 / < 0 IS | | | fails (6 IS events) |
| N4 JP 30 Sep, before (JPY up) | USDJPY | -12.8 (-0.40) | -64.2 (-3.29) | -74.2 (-1.44) | 4.4 / 11.6 | -68.6 / -85.8 | | | wrong sign: USDJPY rises into the half-year end |
| N4 JP 30 Sep, after | USDJPY | -51.3 (-1.01) | +28.2 (0.92) | +111.5 (1.18) | | +26.9 / +116.8 | | 0.48 / 0.94 | fails (IS t, PRE sign) |
| N4 AU 30 Jun / NZ 31 Mar, before and after | AUDUSD / NZDUSD | -43..+38 | -17..+70, \|t\| <= 1.13 | -23..+19 | 2-5 | | | | fails |
| N4 pooled (4 year-ends a year) | home ccy | pre +2.0 (0.10) / post +5.5 (0.22) | -3.9 / +8.2 (0.35) | -31.2 / +40.6 (1.20) | | | | | fails |
| N5a quarter-end, last 3 days, long USD | USD3 | +0.4 (0.03) | -5.2 (-0.35) | -21.7 (-0.95) | 0.8 / -0.5 | < 0 | | | fails |
| N5b quarter turn, short USD | USD3 | -16.7 (-1.44) | -10.8 (-1.14) | -27.7 (-0.98) | | < 0 | | | fails |
| N5c year-end, last 3 days, long USD | USD3 | -4.3 (-0.28) | **-74.4 (-4.25)** | -41.6 (-1.40) | | -75.3 / -40.9 | | | wrong sign, 6 + 3 events, absent in PRE |
| N5d year turn, short USD | USD3 | -30.3 (-0.91) | -6.1 (-0.45) | n 2 | | | | | fails |
| N6a CN quarterly tax deadline, 3 days before, short USDCNH | USDCNH | - | +12.0 (1.34) | +9.2 (0.76) | 3.3 / 3.3 | +8.7 (0.97) / +6.0 | 0.77 | 0.52 / 0.37 | fails (IS t); 6/9 years > 0 |
| N6b CN every monthly deadline | USDCNH | - | +3.7 (0.76) | +12.0 (0.96) | 3.4 | +0.3 / +8.7 | 3.3 | 0.03 / 0.52 | fails |
| N8a large net bill settlement day (top third, causal) | USD3 / XAU / US30 | -2.8 / -3.6 / - | +0.8 (0.24) / -11.9 (-1.48) / -12.5 (-1.01) | -1.4 / -5.9 / -8.9 | 0.8 / 1.7 / 1.1 | <= 0 | | <= 0 | fails |
| N8b dose slope | USD3 / XAU / US30 | -1.9 / -7.8 / - | -0.2 / -5.4 / -6.9 | -0.7 / +1.9 / -10.4 (-2.25) | | | | | no dose-response on the registered side |
| N7 (post hoc) 15th of every month, long US30 | US30 / US500 / USTEC | - | +0.1 (0.00) / +2.4 / +4.6 | +16.6 (1.03) / +19.7 / +30.0 | 3.1 / 2.6 | -3.0 / +14.0 | | -0.02 / 0.14 per trade | rejected |

Placebos (not counted as cells):
- Non-tax 15ths, USD3: IS +10.5 (t 1.82), VAL -9.8. So the tax days are not different from other 15ths.
- All coupon settlement days: \|t\| <= 1.22.
- Month-end 13-15 ET on the 2nd-last and 5th-last business days: \|t\| <= 1.4, in all three eras.
- The same 5-day windows at the other quarter-ends: AUD +40 bp (t 1.4) PRE and +42 (1.3) IS. That is larger than
  at the AU year-end itself.
- Non-quarter month-ends, USD3: \|t\| <= 1.4.

## Per family: best cell, cells, chance

| family | cells | best registered-side IS t (cell) | its VAL | verdict |
|---|---|---|---|---|
| N1 US tax days | 12 | 1.02 (N1b short gold) | +21 bp, t 0.37 | none |
| N2 coupon settlement | 15 | 2.68 (N2a after, long US30) | -9.6 bp, t -0.71 | none (decayed) |
| N3 month-end bond extension | 8 | 1.54 (N3c gold) | +3.4, t 1.02 | none |
| N4 fiscal year-ends | 10 (+2 pooled) | 0.92 (JP Sep after) | +111, t 1.18 (3 events) | none |
| N5 quarter-end funding | 4 | -0.35 (all wrong sign) | | none |
| N6 Chinese tax period | 2 | 1.34 (quarterly) | +9.2, t 0.76 | none |
| N8 bills | 6 | 0.24 | | none |
| N7 (post hoc) | 1 | 0.00 | | rejected |

- Chance benchmark: 46 cells have IS returns.
- Sign-flip null by event date, shared across cells, 2,000 draws: max \|t_IS\| p50 2.72, p95 5.00. The observed max
  \|t\| is 4.25 (wrong side); 13 % of draws exceed it.
- With 58 normal tests, the p95 of max \|t\| would be about 3.3.
- Nothing stands out from chance.

## Decay and era consistency
No cell keeps the same sign and a similar size across PRE, IS and VAL with t > 1 in any era, except N1b gold
(+45 / +21 / +21 bp, t 1.69 / 1.02 / 0.37). That cell is too weak and too noisy: 4-5 events a year at a 2-day sd of
about 100 bp.

PRE "effects" near t 2 do not carry forward:
- N1c USD3: +21.3 (t 2.02) -> +2.8 -> -16.4.
- N2b reversal: -11.3 (t -2.06) on the registered side -> +11.7 -> +12.7.
- JP March post: +104 (t 2.54) -> -37 -> +55.

The best IS cell (N2a US30) has VAL/IS = -0.34. On the VAL size, the expected HOLD t of every cell is <= 1.

## Surprising, for the record (post hoc, not registrable)
- **The dollar falls in the last 3 days of December**: USD3 -74 bp IS (6/6 years, t -4.25) and -42 VAL, but -4 bp
  in PRE (12 years). That is one event a year, and absent in 2004-15. It is likely a 2016-24 regime (year-end
  dollar-funding pressure was relieved by the Fed's standing facilities and by banks pre-funding), not a rule.
- **USDJPY rises into the Japanese half-year end (30 Sep)**: IS -64 bp on the registered JPY-up side (t -3.3, n 6),
  VAL -74 (n 3), PRE -13 (t -0.4). This is the opposite of repatriation, and not seen before 2016.
- **US30 rose on the 15th of non-tax months** (IS +31 bp, t 2.95; VAL +53, t 2.79). Tested as N7, it is not a 15th
  effect:
  - all 15ths give IS +0.1 bp;
  - the shifted day-of-month placebos 5..28 range IS t -2.6..+1.7;
  - the split came from which months fell in each subset (March 2020 was in neither).
- **Net Treasury settlement size predicts nothing** (dose slopes \|t\| <= 0.95, bills included). The September 2019
  mechanism is real in money markets, but it does not reach FX, gold or US30 at a 1-day horizon.

## Directions that need the user's decision
1. **Dukascopy index CFD history 2004-15** (USA30IDXUSD, USA500IDXUSD: only a few probe files are local). This is a
   new price series. It would give the US30 cells (N1, N2a, N7) a PRE era. N2a "after", the only cell with IS t >
   2.5, needs it before anything else.
2. **Treasury yields or futures intraday** (bond CFDs or futures; IC lists none in the repo). This is needed to test
   the bond-index extension on the instrument itself rather than through USDJPY/gold.
3. **The S&P 500 dividend-payment calendar** (Hartzmark & Solomon 2022) for dividend-reinvestment days. This data is
   not in the repo.
4. Not prices, and allowed but not done here:
   - daily TGA and reserve balances (fiscaldata Daily Treasury Statement);
   - SOFR / GC repo (NY Fed).

   They could condition N1/N2 on reserve scarcity. With every unconditional and dose cell flat, the prior is low.

## Process
- Hypotheses were written before their numbers: N1-N6 at 01:33 UTC; N7 (post hoc, marked) and N8 at 01:38-01:39.
- The random-entry control was fixed once: the short side's pool now uses the short side's own swap. All outputs
  were rerun.
- C3 correlation: not computed, because no cell survived.
- Network:
  - fiscaldata.treasury.gov (auction records);
  - OpenAlex and Semantic Scholar (abstracts; Semantic Scholar was partly rate-limited);
  - the Bloomberg US Aggregate methodology PDF (assets.bbhub.io).

  SSRN was unreachable. No prices were downloaded.

Scripts and outputs (session scratchpad,
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r13/N/`):

| file | what it does |
|---|---|
| `code/cal_build.py` | tax, holiday and Chinese-deadline calendars (scratch `holidays` venv) |
| `code/cal_treasury.py` | net coupon settlements |
| `code/cal_bills.py` | net bill settlements |
| `code/libN.py` | loaders, costs, swap; refuses HOLD |
| `code/screen.py` | 46 cells + placebos |
| `code/analysis2.py` | N2c, N4 pooled, by year, sign-flip null |
| `code/n7_payday.py` | N7 |
| `code/n8_bills.py` | N8 |
| `cal/*.json` | the calendars |
| `out/*_out.txt`, `out/*.pkl` | outputs |
