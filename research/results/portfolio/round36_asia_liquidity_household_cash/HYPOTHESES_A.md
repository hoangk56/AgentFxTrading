# Round 36, stream A: hypotheses (declared before any return)

Written 2026-10-28 02:05 UTC (`date -u`). No series below had been joined to any return when this was written. Loaded
so far: the HKMA currency-board (CU) transaction list (parsed, no prices joined) and, for the power arithmetic only, the
unconditional (no-signal) 09:30 UTC sd and cost per target. Bars: research/PROMPT.md LIVE / DEMO (no RELAXED).

## Sources (probed 2026-10-28 01:43-02:03 UTC; every fetch in scratchpad `r36/A/web/requests.log`)
- **HKMA open API** (api.hkma.gov.hk, no robots.txt): `daily-figures-interbank-liquidity` answered one 3-row probe
  (fields from 2002-01-02: aggregate balance, CU forex transactions T+1..T+3, HIBOR O/N and 1M). The next request
  (pagesize 1000, `to=2024-12-31`) got **HTTP 405 from the API's WAF** ("request blocked as it may cause potential
  threats"), and every retry since (01:46, 01:50, 01:57 UTC) is still 405. I backed off; a last retry is scheduled.
  If it stays blocked the API is not used (no workaround attempted).
- **HKMA website** (www.hkma.gov.hk): `convertibility.xlsx`, the official list of every currency-board forex
  transaction (trade date, settlement date, HK$ mn, sign = change in the aggregate balance) for **2018-2025**.
  Parsed with sheets <= 2024 only. **Disclosure:** while checking the file structure I printed the header and the
  first three rows of the 2025 sheet (three strong-side transactions in early May 2025 with their sizes). Nothing
  below uses 2025 data; sides were fixed from the mechanism before this, and no family here depends on that sheet.
  Weak-side (HKMA buys HKD, drain) transactions: 2018 27 (14 trade days), 2019 8 (7), 2022 41 (32), 2023 8 (8).
  Strong-side: 2020 only, 85 transactions. None in 2016-17, 2021, 2024.
- **PBoC open-market operations: not available.** www.pbc.gov.cn robots.txt is `User-agent: * Disallow: /` (only
  Baiduspider allowed): not used (one index page was fetched as a probe before reading robots.txt; not parsed).
  chinamoney.com.cn (CFETS) shows the OMO table through a JS endpoint guarded by a robot-check key
  (`/dqs/rest/cm-u-rbt/apply`); the old public endpoint (`/ags/ms/cm-u-bond-publish/TicketHandle`) answers 404. No
  free mirror with daily OMO quantities was found (GitHub, akshare source). **Replacement:** the price of the same
  liquidity, i.e. official interbank fixings mirrored by Eastmoney's data center (datacenter-web.eastmoney.com, no
  robots.txt, `RPT_IMP_INTRESTRATEN`, query cut `REPORT_DATE <= 2024-12-31`): SHIBOR O/N and 1W (from 2006-10),
  HKD HIBOR O/N and 1M, CNH HIBOR O/N and 1W. RRR history: Eastmoney `RPT_ECONOMY_DEPOSIT_RESERVE` (announcement and
  effective dates), query cut at 2024-12-31.
- **BoJ: not used.** Since QQE (2013) the BoJ current-account balance is in the hundreds of trillions of yen; daily
  changes from fiscal flows and operations do not bind (the abundant-reserve case round 32 L found empty in the US),
  and round 31 J did MoF flows / interventions. No mechanical BoJ series is left that is new.

## Clock, publication time, costs (fixed now)
- One clock for all families: **entry 09:30 UTC + 1 minute** (first IC M1 bar close, bid / ask), exit at 09:30 UTC
  (+1 min) h weekdays later, h in {1, 3, 5}. Robustness: spread x1.5; fill one more minute late.
- CU transactions with trade date D (HK date): entry on the **next weekday after D** (D's transactions, also those
  done in the London / New York session, are public by then; settlement and the actual drain happen at D+2, so the
  entry precedes the scheduled drain).
- HIBOR (HKAB / TMA fixing 11:00-11:15 HKT = 03:00-03:15 UTC), CNH HIBOR (TMA, 11:15 HKT) and SHIBOR (11:00 Beijing =
  03:00 UTC): the fixing of date D is used at 09:30 UTC of D (>= 6 h after publication).
- RRR: the effective date is announced 1-3 weeks ahead; entry 09:30 UTC on the effective date (the day the liquidity
  is released).
- Costs: IC bid / ask at both fills; commission 0.6 bp for AUDUSD / USDCNH, 0 for HK50 / US500 / USTEC; swap per
  17:00 New York rollover from `research/swing/rates.py` (`swap_frac_at`). **USDCNH has no swap model in the repo**:
  I use (r_USD - r_CNH) / 360 minus the mean calibrated FX markup of the 8 calibrated pairs, with r_CNH = CNH HIBOR 1W
  (Eastmoney; 2.5 % before its first value). USDCNH cells are also reported **ex swap**; a USDCNH verdict needs both > 0.
- Prices: IC M1 2016-2024 (ts < 2025-01-01 at load). USDCNH: IC M1 rebuilt from IC ticks 2016-01..2024-12 (scratchpad
  `clean/USDCNH_m1.npz`); PRE = Dukascopy USDCNH 2012-15 (bid; ask = bid x IC 2016-17 median spread by minute, + 0.6 bp
  commission). AUDUSD PRE = Dukascopy 2004-15 (same synthetic ask). HK50 / US500 / USTEC: no PRE.
- Eras: PRE <= 2015, IS 2016-21, VAL 2022-24; HOLD closed.

## Power arithmetic (before any return)
Unconditional, 09:30 UTC, IS 2016-21 (scratchpad `out/power.txt`): sd of the h-day mid move and average round-trip
cost incl. swap (long and short averaged).

| target | sd h1 / h3 / h5 (bp) | cost h1 / h3 / h5 (bp) | quoted share of weekdays |
|---|---|---|---|
| HK50 | 120 / 199 / 259 | 5.9 / 9.4 / 12.9 | 0.91 |
| USDCNH | 26.8 / 45.3 / 58.1 | 1.6 / 2.3 / 3.0 | 0.99 |
| AUDUSD | 59.9 / 104 / 137 | 1.6 / 2.8 / 4.1 | 0.99 |
| US500 | 107 / 171 / 217 | 3.9 / 7.4 / 11.0 | 0.99 |
| USTEC | 132 / 205 / 257 | 5.5 / 9.4 / 13.4 | 0.99 |

LIVE: per-trade net Sharpe x sqrt(HOLD trades) >= 3 over 1.73 HOLD years.

| signal | trades / yr | HOLD n | Sharpe needed | net edge needed per trade (bp) | sign-rule rho needed |
|---|---|---|---|---|---|
| daily, k = 0, h 1 | ~245 | ~425 | 0.146 | HK50 17.5, USDCNH 3.9, AUDUSD 8.7 | HK50 0.24, USDCNH 0.26, AUDUSD 0.21 |
| daily, k = 1 (~30 % of days), h 1 | ~75 | ~130 | 0.26 | HK50 31, USDCNH 7.0, AUDUSD 15.6 | ~0.4 |
| daily, k = 0, h 5 (overlapping, n / 5) | | | 0.33 vs h5 sd | HK50 84, USDCNH 19, AUDUSD 45 | ~0.35 |
| events ~20 / yr, h 5 (CNH squeezes) | ~20 | ~35 | 0.51 | USDCNH 30 | |
| CU weak side: 21 IS / 40 VAL trade days in 4 years, 0 in 6 others | ~5 (lumpy) | unknown (peg-dependent) | > 1 | LIVE impossible by count; DEMO at most | |
| RRR effective dates | ~3 | ~5 | 1.3 | LIVE impossible; DEMO needs IS Sharpe >= ~0.55 on ~14 events | |

Expected size from the literature: no study I know finds that HKMA aggregate-balance drains or HIBOR moves predict
the Hang Seng over the next 1-5 days; the HIBOR-equity link in HKMA / HKIMR work is contemporaneous (rates and equity
outflows move together when carry trades unwind). For China, SHIBOR shocks (e.g. the June 2013 cash crunch) hit
A-shares the same day; Funke, Shu, Cheng & Eraslan (2015, J. Int. Money Finance, "Assessing the CNH-CNY pricing
differential") find offshore liquidity / policy events move the CNH-CNY gap, i.e. CNH squeezes strengthen CNH while
they last. A plausible next-day correlation is <= 0.03 for the daily families (LIVE needs ~0.2-0.26: ~8x), and the
event families are too rare for LIVE. **Prior: LIVE ~1 %, DEMO ~3-5 %** (CNH squeezes and CU drains, where the dose
is mechanical, are the only places I expect any sign).

## Families, sides (fixed now from the mechanism) and cells
**A1. HKMA weak-side CU drain -> short HK50.** Event = a trade date D with HKMA HKD purchases (negative transactions);
one trade per D (the day's sum is the dose), entry next weekday. Mechanism: the purchase drains the aggregate balance
at D+2 by a published amount, HIBOR rises, HK equities (banks, property, leveraged buyers) weaken; capital outflow
continues while the peg is at the weak side. Side: short. Cells: HK50 x h {1, 3, 5} = **3 graded**. US500 and USTEC
with the same dates and side as **controls** (information: if they fall as much, the effect is global risk-off, not
the HK drain). IS 2018-19 (21 trades), VAL 2022-23 (40). Extra control (declared now): **local random entries**,
same count, drawn from the weekdays within +-40 weekdays of each event, >= 300 seeds (both 2018 and 2022 were HK bear
years, so an era-wide random control would credit the regime). Information: dose-weighted mean, and the first event of
each episode (gap >= 20 weekdays).

**A2. HKMA strong-side injection -> long HK50 (information only).** 2020 only (85 transactions); no VAL event, so no
bar can be met. Reported for HK50, AUDUSD, USDCNH (long AUDUSD, short USDCNH = Asia inflow / risk-on), h {1, 3, 5}.

**A3. Daily change in 1M HKD HIBOR -> HK50.** x(D) = HIBOR1M(D) - HIBOR1M(previous fixing); z = x / sd of x over the
previous 250 fixings (min 60). Rise = tighter HKD liquidity = short HK50; fall = long. k {0, 1} x h {1, 3, 5} =
**6 graded**; US500 / USTEC as controls (info).

**P1. Daily change in 1W SHIBOR (China onshore liquidity price) -> USDCNH, HK50, AUDUSD.** x(D) = SHIBOR1W(D) -
previous fixing; z as A3. Rise (PBoC lets liquidity tighten) = CNY / CNH stronger -> **short USDCNH**; China
tightening -> **short HK50**, **short AUDUSD**. Fall = the opposite sides. k {0, 1} x h {1, 3, 5} x 3 targets =
**18 graded**. PRE: AUDUSD 2006-10..2015, USDCNH 2012-15.

**P2. CNH liquidity squeeze -> short USDCNH.** Event = CNH HIBOR O/N on D more than 2 sd above its mean of the previous
60 fixings (min 40), i.e. offshore CNH liquidity drained (the PBoC's documented squeezes of CNH shorts). Side: short
USDCNH (CNH strengthens while borrowing CNH to short it is expensive), h {1, 3, 5} = **3 graded**. Consecutive event
days are separate trades (overlap handled by Newey-West). Also reported ex swap (the swap model credits the short with
the spiking CNH HIBOR 1W; IC's real swap may not).

**P3. PBoC RRR effective dates -> long HK50, long USDCNH, long AUDUSD for a cut** (released liquidity: equities and
AUD up, CNY weaker); hikes take the opposite side. h 5 only: **3 graded**. Expected null (announced in advance and
priced at announcement); kept because the release date is the mechanical injection day.

**Total graded cells: 33** (A1 3, A3 6, P1 18, P2 3, P3 3). Chance: max |Z| of 33 independent normals has median
~2.3, p95 ~3.0; I also report a circular-shift null (signal shifted >= 130 weekdays against prices, sides recomputed,
300 draws, shared by all graded cells: max |IS t| p50 / p95).

## Tests per cell
Mid and net bp per trade by era (PRE / IS / VAL) and year; t: h 1 per-trade t (one trade per day = day-clustered);
h 3 / 5 Newey-West with lag h on the trade series; per-trade Sharpe and power at the IS trade rate over 1.73 years;
x1.5 spread, +1 minute; share of positive years; net without 2020-03..04; random control = share of circular shifts
whose IS (VAL) mean net is below the observed (>= 90 % for DEMO, >= 95 % for LIVE); A1 also the local control.
Verdict per research/PROMPT.md: LIVE = IS t >= 2.5, VAL t >= 1.5, >= 2/3 positive years, random >= 95 %, x1.5 and +1 min
> 0, power >= 3; DEMO = IS t >= 2, VAL net > 0, random >= 90 %, x1.5 and +1 min > 0. Parameters k and h are chosen on
IS only; VAL checks the IS choice. Nothing is chosen on VAL. A family that meets a bar gets a PREREG_DRAFT_A_<name>.md.
