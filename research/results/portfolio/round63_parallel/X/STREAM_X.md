# Round 63 stream X: VIX-futures ETP roll and leveraged-ETP dose (result)

Written 2026-10-31 16:20 UTC (from `date -u`). Rules, grid, costs and power were declared in
[HYPOTHESES_X.md](HYPOTHESES_X.md) at 16:11 UTC, before any return was computed. HOLD (2025+) was never loaded: every
row with Trade Date >= 2025-01-01 is dropped in `code/vxdata.py` at parse. Full output: [run_output.txt](run_output.txt).

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)
- **A1, the roll-window calendar (short M1 / long M2), is term-structure beta, not a roll flow.** The 1:1 version has
  IS +0.44 pt per window (t 2.03), VAL +0.24 (t 1.27), but it loses in all three PRE years. Against US500 its alpha is
  +0.07 pt (t 0.50) in IS, with R² 0.65. Windows aligned to the ETP roll calendar do no better than random-start
  windows (53 % / 59 %), and 2.03 is below the max-over-8-cells null p95 of 2.27. The beta-neutral version (h 1.29)
  has IS t 1.45 and VAL -0.08.
- **A2, the overnight reversal of the roll impact, is real but below cost.** Long M1 / short M2 from settle t to the
  next open earns IS +0.037 pt per day gross (NW t 7.1) and VAL +0.014 (t 3.5). The drift sits in M1, the contract
  the ETPs sell (see the diagnostic below). The cost is 0.108 pt per round trip, 3-8x the gross. Net t is -13.5 IS and
  -24.6 VAL, and the result is still negative with a TAS entry.
- **B, fading the leveraged-ETP dose, fails.** The settle-to-open fade loses in IS (t -2.1 / -2.8). The
  settle-to-settle fade has IS t 1.28 / 1.52, below DEMO's 2.0. VAL top decile has only 17 days, because the dose per
  unit of OI fell after UVXY / SVXY were cut to 1.5x / -0.5x in 2018.

## Data
| source | span | notes |
|---|---|---|
| Cboe CFE `cdn.cboe.com/.../historical_data/VX/VX_<expiry>.csv`, keyless | 146 monthly contracts, Jan 2013 .. Feb 2025; rows used 2013-01-02 .. 2024-12-17 | columns: Open High Low Close Settle Change Volume EFP OI; no intraday data. Settle = 0 before 2013-05-17, where Close is used instead (PRE only). Expiry = file-name date, which matches the last trade date for 2013-05 .. 2024 |
| ProShares UVXY / SVXY / VIXY AUM (round 34 E raw), cut at < 2025-01-01 into research/data/cboe_vx/proshares/ | 2011-2024 | VXX, TVIX and XIV are missing: the roll dose is understated, and the LETF dose is understated before 2018 |
| IC US500 M1 cache, 16:14 ET | 2016-2024 | beta check for A1 |

Fetch log: research/data/cboe_vx/requests.log (151 requests: 146 x 200, 5 x 403). cdn.cboe.com is S3, so a missing
key answers 403 AccessDenied, and its robots.txt does the same (no file exists). Each 403 was a holiday-shifted
expiry candidate. The next candidate date returned 200 every time: they were not blocks. Spacing was >= 1 s.

## Costs (as declared)
Tick 0.05 = $50; bid-ask one tick per leg; $2 per contract per side. A calendar round trip costs 0.108 pt ($108), an
outright 0.054 pt. A1b scales the M2 leg by h. Futures margin is small, so P&L is shown in points per spread (x $1000),
not as excess over cash.

## Results per era (net of costs; t: windows plain, daily cells Newey-West)
| cell | PRE net / t | IS n | IS net / t | IS yrs + | VAL n | VAL net / t | VAL yrs + | random IS / VAL | x1.5 IS / VAL | late IS / VAL | HOLD power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1a 1:1 window | -0.335 / -1.58 | 72 | **+0.442 / 2.03** | 5/6 | 35 | +0.236 / 1.27 | 2/3 | 53 % / 59 % | +0.388 / +0.182 | +0.406 / +0.261 | 0.98 |
| A1b h 1.29 window | -0.444 / -2.79 | 72 | +0.209 / 1.45 | 4/6 | 35 | -0.076 / -0.65 | 2/3 | 52 % / 57 % | +0.147 / -0.138 | +0.150 / -0.090 | -0.51 |
| A2a all days, settle->open | -0.111 / -29 | 1440 | -0.071 / -13.5 | 1/6 | 708 | -0.094 / -24.6 | 0/3 | (gross) 100 / 99.9 % | neg | neg | -19 |
| A2b top-tercile roll dose | -0.099 / -18 | 480 | -0.054 / -7.3 | 1/6 | 234 | -0.096 / -14.3 | 0/2 | 98.5 % / 39.7 % | neg | neg | -10 |
| B1a fade, top-decile dose, ->open | -0.019 / -0.97 | 143 | -0.056 / -2.11 | 0/6 | 17 | +0.146 / 1.40 | 2/2 | 33 % / 99.8 % | -0.083 / +0.119 | +0.200 / +0.747 | 0.90 |
| B1b fade, top quintile, ->open | -0.033 / -3.61 | 286 | -0.064 / -2.76 | 0/6 | 55 | +0.013 / 0.35 | 2/3 | 15 % / 96 % | -0.091 / -0.014 | +0.145 / +0.021 | 0.20 |
| B2a fade, top decile, ->settle | +0.051 / 0.56 | 143 | +0.159 / 1.28 | 4/6 | 17 | +0.629 / 1.29 | 2/2 | 95 % / 99.5 % | +0.132 / +0.602 | +0.388 / +0.554 | 0.96 |
| B2b fade, top quintile, ->settle | +0.036 / 0.59 | 286 | +0.130 / 1.52 | 4/6 | 55 | -0.053 / -0.26 | 2/3 | 96.5 % / 49 % | +0.103 / -0.080 | +0.153 / +0.148 | -0.15 |

Max-over-8-cells null of IS t (each cell's declared benchmark, 300 draws): p50 1.13, p95 2.27. Best observed: A1a
2.03.

Yearly net, A1a (points per spread, x $1000): 2013 -5.1, 2014 -3.4, 2015 -3.9 | 2016 +8.9, 2017 +0.8, 2018 -9.4,
2019 +13.0, 2020 +9.8, 2021 +8.8 | 2022 +4.6, 2023 +7.3, 2024 -3.6. Worst IS window -8.46 pt (Feb 2018).

### A1 checks
- US500 regression on window log-returns: A1a IS alpha +0.067 pt (t 0.50), beta +30.6 pt per 100 % (t 11.5), R² 0.65.
  VAL alpha +0.066 (t 0.44). This is the short-front-vol carry that round 9 already graded as beta. The beta-neutral
  A1b IS alpha is +0.28 (t 1.93), and VAL -0.10 (t -0.86).
- The random-start benchmark is nearly degenerate for an always-on spread: shifted windows hold the same daily
  position. The rule's alignment to the roll calendar adds nothing (52-59 %).
- The mechanism's own split (windows with an above-IS-median ProShares share of OI) goes the predicted way. A1a: IS
  +0.62 vs +0.27, VAL +0.51 vs -0.05. A1b: IS +0.58 vs -0.16, VAL +0.15 vs -0.32. This was reported, not a pass
  condition. ETP AUM rises after vol spikes, so the split is confounded with the vol regime. With ~6 windows a year it
  could not reach power 3 (it would need a per-window Sharpe of ~0.9).
- Post-hoc control (labelled): the same carry one step out, short M2 / long M3 (M3 is not traded by short-term ETPs).
  1:1 version: IS +0.17 (t 0.78), VAL +0.15 (t 1.51). Beta-neutral: IS +0.01, VAL -0.11.

### A2 diagnostic (post hoc, [diag_a2_output.txt](diag_a2_output.txt))
Gross settle -> next open, per contract: IS M1 +0.038 (t 4.2), M2 +0.001, M3 -0.005; VAL M1 +0.010 (t 1.4), M2 -0.004,
M3 +0.005. PRE (XIV era, smaller net ETP position) M1-M2 -0.003. By year, the M1-M2 gross: 2016 +0.012, 2017 +0.002,
2018 +0.007, 2019 +0.042, 2020 +0.113, 2021 +0.048, 2022 +0.016, 2023 +0.016, 2024 +0.008. The roll's temporary
impact on M1 at the settlement is measurable, as the mechanism predicts. It is 0.01-0.05 pt in normal years against a
0.05 pt half-spread per leg, so only a zero-spread liquidity provider (a CFE market maker on the TAS book) could earn
it.

## What failed and why
- The roll flow is real (A2 gross) but tiny. The ETP roll per day is ~0.8 % of M1+M2 OI (ProShares alone; VXX adds
  more). Its impact is a fraction of one tick and reverts within hours. Over a full window the inventory effect can't
  be told apart from the term-structure premium, which carries an S&P beta.
- The LETF dose is small next to VX OI: |dose| p90 is 1.7 % of M1+M2 dollar OI in IS and 0.9 % in VAL. A fade of
  the day's move on high-dose days is no better than fading any day in IS.
- The power cap shows even before the results. A1 has 12 windows a year, so it would need an annual Sharpe of ~2.25.
  A2 / B lose to costs.

## Pitfalls hit
- cdn.cboe.com answers 403 for a missing key (S3). The first fetch stopped on the Mar 2014 expiry, which moved to
  Tuesday 03-18 because Good Friday fell on the April SPX expiry. The fetch was resumed with date shifts.
- Files before 2013-05-17 have Settle = 0, so Close is used (PRE only).
- The Tuesday-to-Wednesday day (the pair changes) is excluded from A1 / A2 / B, and A2 / B never enter on the day
  before an M1 expiry.

## What a user decision could unlock
- Intraday VX data (Cboe DataShop, paid) would give the last-15-minute push of the LETF dose and the exact settlement
  window. Round 34's dose sizes suggest it is small.
- VXX / iPath shares outstanding (Barclays, no free history found) would give the full roll dose. It would not
  change A1's beta problem.
- A zero-spread market-making setup on the CFE TAS book is the only venue where A2's +0.01-0.04 pt overnight drift
  could pay. That is not a retail route.

## Files
- code/fetch_vx.py (download), code/cut_proshares.py (AUM cut at 2025), code/vxdata.py (loader, HOLD cut),
  code/run.py (8 cells), code/diag_a2.py (post-hoc per-contract diagnostic).
- run_output.txt, diag_a2_output.txt. Data: research/data/cboe_vx/{raw/, proshares/, requests.log}.
