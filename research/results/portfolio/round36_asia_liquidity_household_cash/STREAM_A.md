# Round 36, stream A: Asian central-bank liquidity operations (HKMA, PBoC) -> HK50, USDCNH, AUDUSD

Written 2026-10-28 02:55 UTC (`date -u`). Hypotheses: [HYPOTHESES_A.md](HYPOTHESES_A.md), written at 02:05 UTC, before
any return. Bars: research/PROMPT.md, LIVE / DEMO only (no RELAXED).

HOLD (2025-01..2026-09-24) stayed closed for prices: IC M1 was loaded at ts < 2025-01-01, USDCNH M1 was rebuilt only
from 2016-2024 ticks, every Eastmoney query was cut at `REPORT_DATE <= 2024-12-31`, and the RRR and CU files were cut
in the parser. **One slip, disclosed:** while checking the layout of HKMA's `convertibility.xlsx` I printed the header
and first three rows of its 2025 sheet (three strong-side transactions in early May 2025 with their sizes). No family
uses 2025 data, and the sides had already been fixed from the mechanism.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

- I graded 33 declared cells in five families. None reaches IS net t >= 2.0 on its declared side.
- The best is A3 (HIBOR 1M jumps, k1 h5, HK50): IS net +38.9 bp, t **1.99**; VAL +9.6 bp, t 0.25 (VAL/IS 0.25).
  - It misses the DEMO IS bar by 0.01. That is not rounded up.
  - US500 and USTEC show the same IS pattern on the same days (USTEC +38.2, t 1.89). The signal is US rates or global
    risk, not HK liquidity.
  - It sits inside the family's shift null (max |IS t| p50 2.56).
- The largest |IS t| among graded cells is -2.30, on the wrong side: P1 USDCNH k0 h1, which is mostly cost (mid -0.1 bp).
- **HKMA weak-side drains do not weaken HK50** (A1). Short HK50 after HKMA buys HKD loses in IS (-11.0 bp at h1) and in
  VAL at every hold. Against local random entries it ranks below the median.
- **PBoC liquidity, measured by its price (SHIBOR 1W, CNH HIBOR), says nothing about USDCNH, HK50 or AUDUSD at 1-5
  days** (P1, P2).
  - In PRE 2012-15, a SHIBOR rise or a CNH squeeze is followed by a **weaker** CNH (mid t -2.5 and -2.1), against the
    carry mechanism.
  - In 2016-24 there is no sign at all.
- RRR effective dates (P3) are too rare: 10 IS and 6 VAL events. HK50 VAL +317 bp rests on two stimulus days
  (2022-12-05, 2024-09-27).

## Sources
| source | fetched | span used (cut 2024-12-31) | usable? |
|---|---|---|---|
| HKMA open API `daily-figures-interbank-liquidity` (aggregate balance, CU transactions T+1..T+3, HIBOR) | 1 probe at 200 (3 rows from 2002-01-02); then **HTTP 405 from the API's WAF** on every request at 01:44, 01:46, 01:50, 01:57 and 02:12 UTC | - | **no**: blocked. I backed off for 28 minutes and tried no workaround (no other client, no other IP). The daily aggregate balance is lost; HIBOR comes from Eastmoney instead |
| HKMA website `convertibility.xlsx` (every CU forex transaction since 2018: trade date, settlement date, HK$ mn) | 1 request | 2018-04-12..2023 | **yes**: weak side 84 transactions on 61 trade days (2018-19: 21 days, 2022-23: 40); strong side 85 in 2020 only; none in 2016-17, 2021 or 2024 |
| HKMA page note (publication time) | 1 request | | the CU / liquidity page updates ~19:00 HKT each business day; a CU trigger outside HK hours shows by ~10:00 HKT the next business day (and in real time on Reuters / Bloomberg). The entry (next weekday 09:30 UTC) is after both |
| HKMA Monthly Statistical Bulletin T070102.xls (daily CU transactions by settlement date since 1998) | 1 request | - | not parsed: BIFF .xls and no reader in the venv. It would only add PRE strong-side events (2008-15), and no target here has a 2008-15 index price |
| PBoC OMO announcements (www.pbc.gov.cn) | robots.txt + 1 index page | - | **no**: robots.txt is `User-agent: * Disallow: /` (Baiduspider only). The one page fetched before reading robots.txt was not parsed |
| chinamoney.com.cn OMO table | 6 requests | - | **no**: the old public endpoint answers 404, and the page loads its data through a robot-check key (`/dqs/rest/cm-u-rbt/apply`), which I did not use |
| Eastmoney data center `RPT_IMP_INTRESTRATEN` (mirror of the official fixings) | 52 requests, 500 rows each, ~80 s per response | SHIBOR O/N and 1W 2006-10..2024; HKD HIBOR 1M 1996..2024; CNH HIBOR O/N and 1W 2013-03..2024 | yes |
| Eastmoney `RPT_ECONOMY_DEPOSIT_RESERVE` (RRR announcement and effective dates) | 2 requests (the first, with a date filter, was refused) | 52 changes 2007-2024; 16 in 2016-24 | yes. The file also holds 2025 rows; the parser drops them unprinted |
| GitHub (akshare source, to find the endpoints) | 12 requests | | used only for URLs |

- 89 requests are logged in scratchpad `r36/A/web/requests.log`: no account, no e-mail, browser UA, >= 1.2 s between
  hits to a host.
- Two short overlaps happened against datacenter-web.eastmoney.com while I restarted the downloader: the old process
  was killed mid-request, at most one request each.
- 2 WebSearches.
- **BoJ: not loaded.** The current-account balance has been non-binding since QQE (the abundant-reserve case round 32 L
  found empty), and round 31 J did MoF flows.

## Protocol (as declared)
- **Entry and exit.** 09:30 UTC, filled at the +1 minute bar's bid / ask close. Exit at 09:30 UTC (+1 min) h weekdays
  later, h in {1, 3, 5}.
- **Signal timing.**
  - CU trades: entry on the next weekday after the trade date (settlement is D+2, so the entry comes before the drain).
  - Fixings (HIBOR, SHIBOR, CNH HIBOR; published 03:00-03:15 UTC): entry the same day.
  - RRR: entry on the effective date.
- **Costs.**
  - IC spread at both fills.
  - Commission 0.6 bp for AUDUSD / USDCNH.
  - Swap from `swap_frac_at`.
  - USDCNH swap = (r_USD - CNH HIBOR 1W) / 360 minus the mean calibrated FX markup. Every USDCNH cell is also reported
    ex swap.
- **Prices.**
  - USDCNH: IC M1 rebuilt from IC ticks 2016-24 (median 09:31 UTC spread 1.1 bp in 2016, 0.2-0.5 bp in 2017-21).
  - PRE (USDCNH 2012-15 and AUDUSD 2004-15): Dukascopy bid, with the ask built from IC's 2016-17 spread by minute.
- **Hand check.** The first A1 trade (entry 2018-04-13, HK50 short, h1) from raw M1 gives +199.03 bp before swap. The
  table has 198.43 with a swap of -0.60, which matches.
- **Random control.**
  - Circular shift of each signal against prices (>= 130 weekdays, sides recomputed, 300 draws). Reported as the share
    of draws whose mean net is below the observed.
  - A1 also: local random entries within +-40 weekdays of each event (2018 and 2022 were HK bear years).

## Power (from HYPOTHESES_A.md, before any return)
| target | sd at h1 / h3 / h5 (bp, IS) | cost at h1 / h3 / h5 |
|---|---|---|
| HK50 | 120 / 199 / 259 | 5.9 / 9.4 / 12.9 |
| USDCNH | 26.8 / 45.3 / 58.1 | 1.6 / 2.3 / 3.0 |
| AUDUSD | 60 / 104 / 137 | 1.6 / 2.8 / 4.1 |

- **Daily rules.** LIVE at k0 h1 needs a per-trade Sharpe of 0.146: HK50 17.5 bp net, USDCNH 3.9, AUDUSD 8.7. That is
  a sign-rule correlation of about 0.21-0.26.
- **Prior.** The literature's prior is <= 0.03 (HIBOR and SHIBOR shocks move equities the same day).
- **Event families.** CU drains (21 IS events) and RRR (~3 a year) cannot reach LIVE power by count. DEMO at most.
- **Prior.** LIVE ~1 %, DEMO ~3-5 %.

## Results (declared side; bp per trade; h > 1 t is Newey-West with lag h)
| cell (IS-best of family) | PRE mid / net (t) | IS mid (t) | IS net (t) | VAL net (t) | VAL/IS | yrs+ IS | x1.5 / +1m IS | power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 short HK50 after CU drain, h5 | - | +22.6 (0.71) | +15.9 (0.50) | -29.5 (-0.41) | < 0 | 0.50 | +14.3 / +16.4 | 0.14 / -0.19 | shift 0.24 / 0.13; local 0.44 / 0.19 | none |
| A1 h1 | - | -7.1 (-0.29) | -11.0 (-0.45) | -2.1 (-0.08) | | 0.00 | | < 0 | local 0.33 / 0.42 | none |
| A3 HIBOR 1M jump, HK50 k1 h5 | - | +51.4 (2.63) | **+38.9 (1.99)** | +9.6 (0.25) | 0.25 | 0.83 | +36.9 / +38.9 | 0.61 / 0.11 | 0.99 / 0.69 | none (IS t < 2; global, see controls) |
| A3 k0 h3 | - | +14.0 (2.35) | +4.5 (0.77) | -2.9 (-0.21) | < 0 | 0.67 | +2.6 / +4.4 | 0.27 / -0.12 | 0.99 / 0.67 | none |
| P1 SHIBOR 1W, USDCNH (best IS: k1 h5) | +1.6 / -2.2 (-0.75) | +1.1 (0.37) | -1.4 (-0.45) | +7.1 (1.30) | < 0 | 0.50 | ex swap IS +0.0 | < 0 | 0.62 / 0.86 | none |
| P1 USDCNH k0 h1 | **-1.7 (-2.52)** / -3.7 (-5.46) | -0.1 (-0.19) | -1.7 (-2.30) | -2.8 (-2.19) | | 0.17 | | < 0 | 0.42 / 0.16 | none (PRE wrong side) |
| P1 HK50 (best: k1 h3) | - | +14.1 (1.32) | +4.7 (0.44) | -22.3 (-1.11) | < 0 | 0.50 | | 0.13 / -0.44 | 0.86 / 0.34 | none |
| P1 AUDUSD (best: k0 h1) | +0.4 / -1.3 (-0.64) | +3.3 (2.04) | +1.7 (1.04) | -3.0 (-1.17) | < 0 | 0.50 | +1.5 / +1.7 | 0.56 / -0.89 | 0.98 / 0.26 | none |
| P2 CNH squeeze, short USDCNH (best: h5) | -11.1 / -6.1 (-1.27) | -2.0 (-0.21) | +4.7 (0.45); ex swap -3.3 | -6.6 (-0.53) | < 0 | 0.67 | | 0.17 / -0.29 | 0.42 / 0.43 | none |
| P2 h1 | **-5.0 (-2.14)** / -5.4 | +2.3 (0.72) | +2.6 (0.78); ex swap +1.0 | +1.9 (0.49) | 0.73 | 0.83 | +2.2 / +2.6 | 0.42 / 0.37 | 0.66 / 0.57 | none (PRE wrong side) |
| P3 RRR effective date, long HK50 h5 | - | +81.0 (1.29) | +64.5 (1.03), n 10 | +317, n 6 | | 0.60 | +62.8 / +65.5 | 0.23 / - | 0.77 / - | none (n; VAL = 2 stimulus days) |
| P3 USDCNH h5 | -57 (n 4) | +10.3 (0.84) | +4.5 (0.36) | +51.8, n 6 | | 0.60 | | 0.05 | 0.63 | none |
| P3 AUDUSD h5 | -10.8 / -17.2 (-0.73) | +8.9 (0.22) | +4.1 (0.10) | -28.8, n 6 | | 0.20 | | 0.02 | 0.52 | none |

- Trades:
  - A1: 21 IS, 39-40 VAL.
  - A3 k0: ~1,390 IS, ~710 VAL; k1: ~280 / ~210.
  - P1 k0: ~1,350-1,430 IS, ~700 VAL, 826 PRE (USDCNH) / 2,146 PRE (AUDUSD).
  - P2: 92 IS, 62 VAL, 53 PRE.
- Full tables are in the scratchpad `r36/A/out/` (`A1.txt`, `A3.txt`, `P1_hk_aud.txt`, `P1P2_cnh.txt`, `cnh_noswap.txt`,
  `P3.txt`, `P3_small.txt`; JSON per family).

## Cells and chance
| family | graded cells | best declared-side IS net t | its VAL t | shift-null max \|IS t\| p50 / p95 | observed max \|IS t\| |
|---|---|---|---|---|---|
| A1 CU drain | 3 | 0.50 | -0.41 | 1.22 / 3.08 | 0.50 |
| A3 HIBOR 1M | 6 | 1.99 | 0.25 | 2.56 / 3.98 | 1.99 |
| P1 SHIBOR, HK50 + AUDUSD | 12 | 1.04 | -1.17 | 2.61 / 3.68 | 1.04 |
| P1 USDCNH + P2 | 9 | 0.78 (P2 h1) | 0.49 | 2.73 / 3.81 | 2.30 (wrong side) |
| P3 RRR | 3 | 1.03 | n 6 | 1.77 / 4.21 | 1.03 |

- 33 graded cells in all.
- With 33 independent normals, max |Z| would be p50 2.31 and p95 3.17. Nothing exceeds chance.

## Information (not graded)
- **A1 controls (post hoc).**
  - Short US500 / USTEC on the A1 dates **lose** in both eras. US500 h1 is IS -36.5 (t -3.04) and VAL -48.2 (t -2.62);
    USTEC h1 is -50.1 (-2.91) and -67.8 (-3.07).
  - Against local random entries the observed short ranks at 0.07 / 0.01 (US500) and 0.09 / 0.01 (USTEC).
  - So US indices **rose** in the day after HKMA weak-side purchases. It is not a reversal: the pre-entry day was also
    up on average (US500 +22 IS, +13 VAL).
  - This is the opposite of the declared control side, seen after IS and VAL. It is not registrable. Round 18 says such
    picks keep ~1/4 of their size, and the event depends on the peg sitting at 7.85.
- **A1 dose and episodes.**
  - Dose-weighted HK50 short: IS -6.3 / -26.6 / +15.4 bp at h1 / h3 / h5; VAL -10.9 / -109 / -70. Bigger drains do not
    help.
  - The first event of each episode (3 IS, 5 VAL) is negative at h3 / h5.
- **A2, strong-side injection 2020** (85 transactions, 47-52 trades).
  - Long HK50 h5 -78.6 (t -1.41).
  - Long AUDUSD h5 -40.1 (-1.34).
  - Short USDCNH h5 +11.7 (0.98).
  - No VAL events, so no bar can be met.
- **A3 by year** (k1 h5, IS net):
  - 2016 +24, 2017 +39, 2018 +85, 2019 +2, 2020 -47, 2021 +84;
  - ex 2020-03..04: +47.7.
  - The same rule on USTEC: IS +38.2 (t 1.89), VAL -13.2. On US500: +24.1 (1.40) and -14.3.
  - In this period HIBOR 1M moves follow USD rate expectations through the peg, so this is a rates / global-risk signal
    (the family round 4 / 9 covered with yields), not HK liquidity.
- **P2 swap.** The modelled swap credits the short-USDCNH leg with the spiking CNH HIBOR (IS h5 +4.7 with swap, -3.3
  without). IC's real swap likely would not pay that, which is why the ex-swap line was declared.

## What this says
- In a currency board, the drain is mechanical and its size is published, but it does not move the local equity index
  over the next 1-5 days on the drain side.
  - Weak-side episodes coincide with US-rate-driven outflows. Their price effect shows up in US and HK equities through
    the global channel, not through the aggregate balance.
- The PBoC's liquidity price, onshore (SHIBOR) or offshore (CNH HIBOR squeezes), is either priced by the 09:30 UTC
  entry or points the wrong way: a squeeze strengthens CNH on the day, then CNH gives it back (PRE).
- The quantity series (OMO net injections) could not be loaded legally from a free official source. Given the price
  results, its value is low.

## Directions that need the user
- **HKMA API** (no account needed; blocked by a WAF from this Mac after one large-page request). Retrying later or from
  another network would give the daily aggregate balance and scheduled CU settlements since 2002, plus strong-side PRE
  2008-15 for AUDUSD / USDCNH. Value: < 2 % LIVE, ~2 % DEMO, since A1 with the official transaction list is already
  null.
- **PBoC OMO daily quantities** (Wind / CEIC paid, or permission to use pbc.gov.cn despite robots.txt). Value: ~1 %
  LIVE, ~2 % DEMO, since its price proxies are null.
- **PBoC CNH bill tenders in Hong Kong** (2018-11 onward; scheduled offshore drains with published sizes). Free on
  HKMA press releases but laborious to scrape; ~6-12 a year. DEMO at most, ~2 %.
- Post hoc only: "long US indices the day after HKMA weak-side purchases". Testing it needs a rule registered now and
  fresh data (or the lead's HOLD, where 2025 had weak-side episodes). Value: low (DEMO at best, ~3 %).

## Files
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r36/A/scripts/`):

  | script | what it does |
  |---|---|
  | fetch.py | logged polite fetcher |
  | dl_em.py, dl_rrr.py, dl_hkma.py | downloads (dl_hkma.py unused: the API was blocked) |
  | parse_cu.py, parse_em.py, parse_rrr.py, xlsx.py | `python -I` parsers with the 2024 cut |
  | build_cnh.py | USDCNH M1 from IC ticks < 2025 and Dukascopy 2012-15 |
  | px.py, lib.py, cnhrate.py | 09:30 UTC trade engine, from r35 T plus USDCNH |
  | power.py | |
  | sig.py, cells.py, run_A.py | families, cells, shift null |
  | a1_info.py, a1_pre.py, p3_small.py | information runs |
  | handcheck.py | the one-trade hand check |

- Outputs: `out/`. Downloads and the log: `web/`.
