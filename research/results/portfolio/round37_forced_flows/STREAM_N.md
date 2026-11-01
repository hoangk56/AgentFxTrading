# Round 37, stream N: Stock Connect quota flows between mainland China and Hong Kong -> HK50, USDCNH, AUDUSD, JP225, US500

Written 2026-10-29 09:49 UTC (`date -u`). Hypotheses: [HYPOTHESES_N.md](HYPOTHESES_N.md), written at 09:37 UTC before
any flow series was joined to a return; addendum at 09:46 UTC (N6 date check, N5 count, a post-hoc note) before the
fallback N7 was computed. No side was changed after a return was seen. Bars: research/PROMPT.md, LIVE / DEMO only.

HOLD (2025-01..2026-09-24) stayed closed: every Eastmoney query carried `TRADE_DATE <= '2024-12-31'`, the parser drops
later rows, IC M1 was loaded at ts < 2025-01-01 (asserted), and USDCNH M1 was rebuilt only from 2016-2024 ticks.
Nothing slipped.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

- 36 counted cells in six families (N1 8, N2 18, N4 5, N6 3, N7 2; N5 had too few events to grade). No cell
  reaches IS net t 2.0 on its declared side with a positive VAL.
- **Stock Connect flows co-move, they do not predict** (round 35's lesson again). Northbound z vs the same HK window:
  corr +0.47 IS / +0.49 VAL (HK50), +0.30-0.34 (JP225, US500), -0.23 / -0.31 (USDCNH). Next window: |corr| <= 0.06
  for every series, target and era. LIVE needs ~0.15-0.25.
- **Connect-closed days do not weaken HK50.** The declared short over southbound-closed blocks (E1) loses in IS
  (-37.7 bp, t -0.71) and badly in VAL (-248 bp, t -3.03; 10 of 13 blocks up). The reopening day (E3b, declared long)
  is weak instead (IS -32.3, t -1.79). The reversed sides are post hoc and still fail IS (E1 reversed t 0.71, E3b
  reversed t 1.79), so they are not candidates.
- The best declared-side IS net t is +1.72 (N2 northbound -> short USDCNH, k1 h3; VAL -0.29 bp), and that series
  cannot be traded at all: northbound net buy has not been published since 2024-08-16. The tradable runner-up, N7 Q1
  (long HK50 into quarter-end), has IS +43.1 bp (t 1.67), random control 0.85 and ~4 events a year.
- Chance: the max |Z| of 36 normals has a median of 2.35 and a 95th percentile of 3.20. The best declared-side cell
  (1.72) is below the median. The largest |IS t| (-5.59, N1c) is pure cost: a 30-minute HK50 hold with a mid of
  +0.5 bp against a 3.3 bp round trip.

## Sources (scratchpad `web/requests.log`, 18 requests, browser UA, no e-mail, >= 1.5 s between requests; 1 WebSearch)
| source | fetched | span used | usable? |
|---|---|---|---|
| Eastmoney `RPT_MUTUAL_DEAL_HISTORY`, MUTUAL_TYPE 001-006 (Shanghai / Shenzhen / total, northbound / southbound): net buy, buy, sell, turnover, quota used and left | 16 pages of 1,000 rows (60-80 s per response) + 1 probe | 2014-11-17..2024-12-31 (Shenzhen from 2016-12-05). **Northbound NET_DEAL_AMT is null from 2024-08-19** (85 VAL days) | yes |
| Eastmoney `push2his ... kamt.kline` | 1 request | - | timed out at 60 s; not retried, because the data-center report has the same fields |
| HKEX (hkex.com.hk) | not tried | - | timed out in the lead's probe; the Connect calendar was rebuilt from the flow data (see below) |
| MSCI / FTSE / S&P China A inclusion steps | 1 WebSearch (the MSCI 2018-19 step plan) | 8 implementation closes 2018-2020 | yes, after a flow check that moved three 2019 dates by one day (below) |

**Calendar from the data.** A HK trading day (HK50 day-session bars) without a southbound record is a southbound-closed
day. That gives 160 days in 41 blocks from 2016 to 2024 (28 IS, 13 VAL), with blocks 1-7 HK days long.
- Until 2022, Connect also shut on the 1-2 days before each mainland holiday (settlement), while A-shares traded.
  From 2023, it shuts only on the mainland holidays themselves.
- Northbound-closed days with the mainland open number 99. They are the HK holidays, the days before them, and a few
  typhoon / rainstorm days. Only blocks containing a pre-announced XHKG holiday enter E4.

**Publication time and the 2024-08 stop.** Both daily totals are taken as public by 09:30 UTC. Northbound is final at
the 15:00 Beijing close; southbound after the 16:10 HKT auction. Every daily trade fills at the close of the 09:31 UTC
bar (09:32 in the +1-minute variant).
- Northbound net buy stopped being published on 2024-08-19. Its VAL era is therefore 2022-01..2024-08-16, and any
  northbound rule is information only: there is no forward signal.
- Southbound net buy is still published, so N1 / N4 / N7 could run forward.

## Protocol
- **Fills.** IC M1: buy at the ask close, sell at the bid close of the fill bar. Spread x1.5 and +1 minute on both
  legs are reported for every cell; neither changes a verdict.
- **Half days.** On Lunar New Year eve and 24 / 31 Dec the HK close is 12:00 HKT, so fills there are at 03:54 / 03:56
  UTC.
- **Costs.** Commission 0.6 bp for FX. Swap per 17:00 NY rollover: indices and AUDUSD from `swap_frac_at`; USDCNH from
  (r_USD - 2.5 %)/360 minus the mean calibrated FX markup (the CNH rate is approximated).
- **IS round trips (bp):**

  | target | windows | cost |
  |---|---|---|
  | HK50 | day session / h1 / h3 | 3.3 / 5.5 / 9.1 |
  | USDCNH | h1 / h3 | 1.5 / 2.1 |
  | AUDUSD | h1 / h3 | 1.5 / 2.8 |
  | JP225 | h1 | 5.4 |
  | US500 | h1 | 3.9 |

- **t statistics.** Daily cells: one trade per signal day, with Newey-West lag 3 for h3. Event cells: t over events
  (one trade per block).
- **Random controls.** Daily cells: a circular shift of the z series against the dates (300 draws, shift >= 130 days,
  side recomputed). Per round 35's convention this ran only for cells with IS t >= 1.5. Event cells: each event moved by
  a random offset within +-40 HK days, outside event windows (300 draws).
- **Power.** Per-trade net Sharpe x sqrt(1.73 x trades a year / h).

## Results (declared side; bp per trade)
| hypothesis (cell) | eras | mid IS (t) / VAL (t) | net IS (t) | net VAL (t) | VAL / IS | Sharpe IS / VAL; power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| N1 southbound z -> HK50, best IS (h1 k1) | IS, VAL | +5.3 (0.87) / +13.3 (1.09) | -0.28 (-0.05) | +8.49 (0.70) | < 0 | -0.002 / 0.046; -0.03 / 0.53 | n/r | none |
| N1 HK50 next day session k0 | IS, VAL | +0.8 (0.32) / -0.1 (-0.02) | -2.52 (-1.08) | -2.88 (-0.63) | | -0.03 / -0.02 | n/r | none |
| N1c southbound z(D-1) -> HK50 last 30 min, k0 | IS, VAL | +0.5 (1.03) / -0.6 (-0.66) | -2.75 (-5.59) | -3.27 (-3.88) | | -0.15 | n/r | none (cost) |
| N2 northbound z -> short USDCNH, k1 h3 (best IS) | IS, VAL to 2024-08 | +6.7 (2.47) / +1.8 (0.37) | **+4.69 (1.72)** | -0.29 (-0.06) | < 0 | 0.103 / -0.005; 0.62 / -0.03 | 1.000 / 0.65 | none (VAL; signal discontinued) |
| N2 -> AUDUSD k1 h1 | same | +6.6 (1.92) / -2.0 (-0.38) | +5.10 (1.48) | -3.19 (-0.62) | < 0 | 0.076 / -0.046; 0.80 / -0.47 | n/r | none |
| N2 -> HK50 / JP225 / US500 (14 cells) | same | | -1.07 to -10.1 (t -1.87 to -0.10) | | | | | none |
| E1 short HK50 over a southbound-closed block (L close -> last closed day) | IS, VAL | -28.9 (-0.55) / -245 (-2.99) | -37.7 (-0.71) | -248 (-3.03) | < 0 | -0.14 / -0.84 | 0.26 / 0.00 | none (wrong side) |
| E2 short HK50 on the last open day's session | IS, VAL | -3.2 (-0.23) / +37.8 (1.84) | -6.5 (-0.47) | +35.3 (1.71) | < 0 | -0.09 / 0.48 | 0.43 / 0.87 | none |
| E3a long HK50, last closed close -> reopening close | IS, VAL | -16.5 (-0.59) / -115 (-1.41) | -23.8 (-0.86) | -123 (-1.52) | | -0.16 / -0.42 | 0.24 / 0.01 | none |
| E3b long HK50 reopening-day session | IS, VAL | -28.9 (-1.60) / -80.0 (-1.09) | -32.3 (-1.79) | -82.6 (-1.13) | | -0.34 / -0.33 | 0.04 / 0.00 | none (wrong side) |
| E4 long USDCNH over northbound-closed blocks (42) | IS, VAL | +3.2 (0.46) / +5.2 (0.38) | -0.7 (-0.09) | +4.2 (0.32) | | -0.02 / 0.08 | 0.67 / 0.54 | none |
| N6 C1 short USDCNH D-3 -> D (8 inclusion closes) | IS | -14.4 (-0.59) | -15.6 (-0.64) | - | | | | none (info; no forward events) |
| N6 C2 long USDCNH D -> D+3, as declared / flow-confirmed dates | IS | +17.5 (2.45) / +11.4 (1.32) | +14.7 (2.03) / +8.7 (0.99) | - | | n 8 | | none (info; n 8, no forward events) |
| N6 C3 short HK50 D-3 -> D | IS | +10.2 (0.12) | +4.5 (0.05); flow-confirmed -65.5 (-0.87) | - | | | | none |
| N7 Q1 long HK50 over the last 4 HK days of a quarter | IS, VAL | +56.8 (2.20) / +170 (1.45) | +43.1 (1.67) | +153 (1.31) | 3.5 | 0.34 / 0.40; HOLD ~7 events: 0.89 / 1.06 | 0.85 / 0.96 | none (IS t < 2, random < 0.90) |
| N7 Q2 short HK50 over the first 2 HK days of a quarter | IS, VAL | +3.1 (0.08) / -134 (-1.53) | -4.0 (-0.10) | -136 (-1.55) | | -0.02 / -0.47 | 0.48 / 0.02 | none |

Notes:
- "n/r" = not run (IS t < 1.5). Without 2020-03/04, no IS-best cell crosses a bar (columns in `out/*.txt`).
- E1-E3 trade counts are 28 IS / 12-13 VAL, against ~8 a year for HOLD. Even at E2's VAL size the event power would
  be 0.48 x sqrt(8), about 1.4: these families could only ever have been DEMO.
- **Placebos for E1 / E2** (one-day NYSE-closed and TSE-closed HK days) are flat: IS t -0.29 to +0.76.
- **E1 by period:** 2016-22 -70.9 bp (t -1.43), 2023-24 -223 bp (t -1.97). The 2024-10-02 Golden Week block alone
  is -934 bp (HK's stimulus rally while the mainland was shut).
- **E3b by period:** 2016-22 -38.9 (t -2.29), 2023-24 -81.2 (t -0.74). HK rises while the mainland is shut and gives
  some back when it reopens. That is a mainland-catch-up / reopening story, not a missing-buyer story.
- **N5 quota pressure:** only 6 IS days (2016-07, Shanghai southbound) and 0 VAL days have < 10 % of the daily quota
  left. Since the 2018-05 quadrupling the quota has never bound. Not graded.
- **N6 dates:** the declared 2019 MSCI closes (05-27, 08-26, 11-25) show net selling or small flows. The flow peaks
  one day later (05-28 +5.6, 08-27 +11.3, 11-26 +21.4 bn RMB, the 3rd largest IS day), so MSCI implemented as of 28
  May / 27 Aug / 26 Nov 2019. Both versions are reported. With the confirmed dates every N6 cell is |t| < 1.
- **N7 flow check:** the mean southbound z over the last 4 HK days of a quarter is +0.24 in IS (others +0.11), but
  only +0.02 in VAL. Q1's VAL return rests on 11 quarters, against a VAL flow that shows no window dressing.

## Multiple testing
- 36 counted cells. Max |Z| of 36 normals: median 2.35, 95th percentile 3.20.
- Best declared-side IS net t: +1.72 (N2 USDCNH, untradable). Best tradable: +1.67 (Q1). Both are below the median.
- Every |t| > 3 is a cost-dominated short hold (N1c) or a wrong-side VAL result (E1).

## Information worth keeping
1. **A free, exact daily Connect history** (6 legs, net buy / turnover / quota) is reachable through Eastmoney's
   data-center API with a date filter. Responses are slow (60-80 s each). The Connect calendar, including the pre-2023
   pre-holiday shutdowns, can be rebuilt from it without HKEX.
2. **Same-window correlations.**
   - Northbound z: +0.47 / +0.49 (HK50, IS / VAL), +0.30-0.34 (JP225, US500, IS).
   - Southbound z vs USDCNH: +0.06 IS, but +0.45 in VAL. In 2022-24 mainland investors bought HK stocks on the days
     the CNH weakened.
   - None of these carries over to the next window.
3. The daily quota no longer binds. "Quota exhaustion" is not an event after 2018.
4. HK50 tends to rise while the mainland is closed and fall back on reopening. This is post hoc, not significant in
   IS, and moves with China-policy headlines, not with a measurable flow.

## Directions that need the user (one-line value estimates)
- **HKEX intraday Connect flow history** (minute-level northbound / southbound, published live until 2024-05; history
  only from vendors such as Wind / iFinD, paid). It would allow an intraday HK-afternoon test (southbound through
  11:30 HKT -> 13:00-16:00 HKT HK50). Value: low. The daily co-move does not carry to the next window, and IC's
  3.3 bp HK50 round trip needs ~12 bp of edge per day session. LIVE ~1 %, DEMO ~3 %.
- **Northbound replacement** (HKEX quarterly northbound holdings, or broker-level CCASS holdings, daily, free on
  hkex.com.hk, which times out from this Mac). It would need another network or a mirror. Value: low. Holdings
  changes are the same flow, and the flow does not predict. LIVE < 1 %.
- **Pre-Spring-Festival CNH seasonal** (exporters convert USD to pay bonuses): one event a year, so it could never
  reach DEMO power. Not worth a decision.

Correlation with C3 was not computed, because no rule survived.

## Files (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r37/N/`)
- `fetch.py`, `dl_em.py`: polite fetcher and the Eastmoney download; raw JSON in `web/em/`, log in
  `web/requests.log`.
- `build_cnh.py`: USDCNH M1 from IC ticks 2016-24 (`USDCNH_m1.npz`).
- `lib.py`: fills, costs, swaps, t.
- `cells.py`: per-date trade cache, grading, shift null.
- `power_pre.py`: the unconditional sd / cost table.
- `daily.py`: N1 / N2 / N3, output `out/daily.txt`.
- `events.py`: N4 / N5 / N6, output `out/events_v3.txt` (v1 / v2 before the half-day fix) and
  `out/inclusion_corrected.txt`.
- `quarter.py`: N7, output `out/quarter_v3.txt`.
