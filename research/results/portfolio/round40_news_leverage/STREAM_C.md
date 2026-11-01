# Round 40, stream C: Chinese margin-financing leverage and forced deleveraging -> HK50, USDCNH, AUDUSD, JP225, XAU (US500 control)

Written 2026-10-29 14:30 UTC (`date -u`). Hypotheses: [HYPOTHESES_C.md](HYPOTHESES_C.md), written at 14:23 UTC before any
margin signal was joined to a return. One protocol line (the 5 x 24 h hold cap) was added at 14:24 UTC, also before
any return. Addendum 1 (fallback families F1 / F2) was written at 14:27 UTC, after the first 120 cells, before F1 / F2
were computed. No side was changed after a return was seen. Bars: research/PROMPT.md, LIVE / DEMO only.

HOLD (2025-01..2026-09-24) stayed closed:
- Every Eastmoney request carried `DIM_DATE <= '2024-12-31'`, and the parser drops later rows. None arrived: 0 of the
  3,586 rows were later than the cut.
- IC M1 was loaded at ts < 2025-01-01 (asserted). USDCNH M1 is round 37 N's rebuild from IC ticks 2016-24.
- Nothing from 2025-26 was printed or summarised.

## Answer
**No LIVE candidate.** LIVE was impossible from the count before any return: 8-25 HOLD trades per signal set would
need a per-trade net Sharpe of 0.6-1.06. **One DEMO-number cell, drafted but not recommended:**
[PREREG_DRAFT_C_xau_after_short_sales.md](PREREG_DRAFT_C_xau_after_short_sales.md) (C3 net short-sale surge ->
gold, h1). It is at the chance median for 120 cells, negative in PRE, and its VAL is +8.9 bp (t 0.72).

- **Forced deleveraging does not continue into HK / CNH.**
  - The declared continuation side **loses** on the pre-declared primary cell. C1 HK50 h1: IS net -45.7 bp (t -2.73),
    VAL -49.6 (t -0.93).
  - HK50, JP225 and US500 all rebound on the next Asian session after a mainland down day with a large fall in the
    financing balance.
  - Post hoc: the rebound is specific to those days. HK50 h1 long after C1 days is +35.4 bp in IS, against -5.4 bp
    after equally large CSI 300 down days without deleveraging. That fits the *reversal* half of Bian, He, Shue &
    Zhou (fire-sale declines that subsequently reverse), not the continuation the brief and the stream declared.
  - CNH and AUD drift the declared way at 3-5 days, but under DEMO in IS:
    - USDCNH h3: IS t 0.78, VAL t 2.86;
    - AUDUSD h5: IS t 1.66, VAL t 2.17;
    - AUD's PRE result is mostly 2015: +21.9 bp, but +5.3 bp without 2015.
- **Leverage build-up -> reversal (C2) and securities lending (C3) give nothing on HK50 / CNH.** Their best cells are
  gold cells: C2a XAU h1 (IS t 2.54, VAL -19.0) and C3 XAU h1 (the draft).
- **2015.** IC starts in 2016, so the 2015 crash is in PRE only (USDCNH, AUDUSD, XAUUSD on Dukascopy). It is shown
  with and without 2015. No PRE cell reaches t 2 either way.
- **Fallbacks (F1 distance to the margin-call trigger, F2 deleveraging at high leverage).** Too few events: F1 has
  ~2 episodes a year at 5 %, and its 10 % version has 3 IS events, too few to grade. F2 repeats C1's wrong-side HK50
  rebound (h1 IS -63.3, t -2.05).

## Sources (scratchpad `web/requests.log`, 13 requests, browser UA, no e-mail, >= 1.5 s spacing; 1 WebSearch)
| source | fetched | span used | usable? |
|---|---|---|---|
| Eastmoney `RPTA_RZRQ_LSHJ` (SSE + SZSE combined: financing balance / buy / repay / net buy, short balance in yuan and shares, short sell / repay volume, float cap, CSI 300 close and % change) | 4 pages of 800 rows + 2 pages of 200 (the server caps pages at 800; 3 transfers broke mid-response and were retried after a pause). ~60-80 s per response | 2010-03-31..2024-12-31, 3,586 CN trading days, no gaps | **yes**. Levels match published totals: RZYE 1.17 trn end-2015, 1.85 trn end-2024 |
| robots.txt of datacenter-web / data.eastmoney.com | 2 | | none published (API error / 404) |
| SSE rule text on the publication time | 1 WebSearch | | the article was not returned |

**Publication time.** I declared D's totals public before the next CN open (exchange rule, recalled; not re-read), and
enter at 01:45 UTC on D+1. A 05:00 UTC entry ("late") is reported for every cell and changes no verdict.

**Not used, and why.**
- SSE / SZSE split: this report has the combined total only. A probe would cost ~2 min a page for a correlated
  series.
- Stock-level margin data and CSRC rule-change dates: too few dated events for either bar.
- HKEX short-selling turnover: hkex.com.hk timed out in round 37.

## Protocol
- **Fills.** IC M1: buy at the ask close, sell at the bid close. Spread x1.5, +1 minute on both legs, and the late
  entry are reported.
- **Costs.** FX commission 0.6 bp. Swap per 17:00 NY rollover from `swap_frac_at` (USDCNH: round 37 N's
  approximation).
- **Holds.**
  - S = D+1 01:45 -> 07:59 UTC.
  - h1 / h3 / h5 = 1 / 3 / 5 CN trading days later at 01:45 UTC, capped at 5 x 24 h.
  - At most 3 open trades per cell.
- **t.** Clustered by episode (signal days within 5 CN days form one episode).
- **Random control.** 200 draws of non-signal CN days of the same era and count, with C3's side taken from z's sign on
  the drawn day. The figure is the share of draws with mean net below the observed.
- **PRE 2012-06..2015.** Dukascopy bid-to-bid mid, minus the cell's IC 2016-17 mean cost (n/a where 2016-17 had no
  signal).
- **IS round trips (bp, mean of both sides):**

  | target | S | h1 | h3 | h5 |
  |---|---|---|---|---|
  | HK50 | 3.3 | 5.0 | 8.6 | 12.1 |
  | USDCNH | 1.2 | 1.6 | 2.3 | 3.1 |
  | AUDUSD | 1.0 | 1.6 | 2.9 | 4.1 |
  | JP225 | 3.4 | 4.8 | 8.4 | 11.9 |
  | XAUUSD | 1.0 | 1.3 | 1.9 | 2.5 |
  | US500 | 2.2 | 3.9 | 7.4 | 11.0 |

## Power before the numbers (HYPOTHESES_C)
- **Signal days / episodes, IS / VAL:**

  | set | IS | VAL |
  |---|---|---|
  | C1 k1.5 | 59 / 37 | 33 / 17 |
  | C1 k2 | 27 / 22 | 16 / 13 |
  | C2a | 46 / 21 | 14 / 10 |
  | C2b | 32 / 4 | 18 / 6 |
  | C3 | 92 / 48 | 43 / 25 |

  Expected HOLD trades are 8-25.
- **LIVE.** It needs a per-trade net Sharpe of 0.6-1.06 (HK50 h1: 70-120 bp net), so it was impossible for every set.
- **DEMO.** It needs an IS per-trade Sharpe of ~2 / sqrt(episodes): C1 0.33, C3 0.29, C2b ~1.0 (4 IS episodes).

## Results (declared side; bp per trade)
| hypothesis (cell) | eras | mid IS (t) / VAL (t) | cost IS | net IS (t) | net VAL (t) | VAL / IS | Sharpe IS / VAL; power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| C1 deleveraging -> short HK50, h1 (primary) | IS, VAL | -41.1 (-2.47) / -46.5 (-0.87) | 4.6 | -45.7 (-2.73) | -49.6 (-0.93) | (wrong side in both) | -0.38 / -0.18 | 0.01 / 0.06 | none (wrong side) |
| C1 k1.5 -> long USDCNH, h3 | PRE, IS, VAL | +11.6 (1.31) / +23.6 (2.89) | 4.7 | +6.9 (0.78) | +22.4 (2.86) | 3.2 | | | none (IS t); PRE -6.2 (-1.26) |
| C1 k1.5 -> short AUDUSD, h5 (C1's IS best) | PRE, IS, VAL | +23.2 (1.93) / +38.2 (2.27) | 3.4 | +19.8 (1.66) | +36.3 (2.17) | 1.8 | 0.13 / 0.32; 0.54 / 1.37 | 0.97 / 0.96 | none (IS t < 2; without 2020-03/04 IS t 1.33). PRE +21.9 (1.36), without 2015 +5.3 (0.25) |
| C2a net-buying surge -> short HK50, h1 (primary) | IS, VAL | -12.0 (-0.72) / +18.7 (0.38) | 3.8 | -15.8 (-0.95) | +16.2 (0.33) | < 0 | -0.14 / 0.10 | 0.25 / 0.59 | none |
| C2a -> long XAU, h1 (C2a's IS best) | PRE, IS, VAL | +22.0 (2.79) / -16.7 (-0.97) | 1.9 | +20.1 (2.54) | -19.0 (-1.10) | < 0 | 0.31 / -0.27 | 0.92 / 0.21 | none (VAL < 0) |
| C2b 5-day build-up -> short HK50, h5 (C2b's IS best) | IS, VAL | +45.3 (1.50) / +177.1 (2.72) | 5.1 | +40.2 (1.36) | +176.0 (2.70) | 4.4 | 0.24 / 0.80; 0.58 / 2.20 | 0.88 / 0.99 | none (4 IS / 6 VAL episodes; IS t < 2) |
| C3 short-sale surge / covering -> HK50, h1 (primary) | IS, VAL | -0.2 (-0.02) / -31.9 (-1.19) | 4.9 | -5.1 (-0.39) | -36.4 (-1.37) | < 0 | -0.04 / -0.21 | 0.53 / 0.04 | none |
| **C3 -> XAU, h1** (C3's IS best) | PRE, IS, VAL | +25.1 (2.87) / +9.1 (0.72) | 1.3 | **+23.8 (2.73)** | +8.9 (0.72) | 0.37 | 0.28 / 0.13; 1.41 / 0.62 (HOLD ~25 trades: 0.64) | **1.00** / 0.59 | DEMO numbers met; **draft, not recommended** (chance median, PRE -13.2 (t -1.00), VAL without its top 3 trades -2.7) |
| F1 underwater <= -5 % -> AUDUSD, h1 (F1's IS best) | PRE, IS, VAL | +30.7 (1.05) / +9.8 (0.42) | 1.5 | +29.2 (1.00) | +8.8 (0.38) | 0.30 | 0.32 / 0.15; 0.54 / 0.29 | 0.93 / 0.63 | none (10 IS events) |
| F2 high-leverage deleveraging -> short AUDUSD, h3 (F2's IS best) | IS, VAL | +40.8 (2.00) / +13.6 (0.30) | 2.7 | +38.2 (1.89) | +11.9 (0.26) | 0.31 | 0.18 / 0.09; 0.50 / 0.22 | 0.99 / 0.58 | none |
| F2 -> short HK50, h1 | IS, VAL | -58.9 (-1.92) / -175.8 (-1.24) | 4.4 | -63.3 (-2.05) | -178.1 (-1.26) | | | 0.00 / 0.00 | none (wrong side) |

All cells, IS net t on the declared side (full output in scratchpad `out/grade.txt`, `out/fallback.txt`):

| family | cells | IS net t range | notes |
|---|---|---|---|
| C1 | 48 | -2.90 to +1.66 | HK50 / JP225 / US500 short loses at S and h1 (rebound); CNH / AUD h3-h5 gain in VAL only |
| C2a | 24 | -3.25 to +2.54 | the CNH / AUD S-h1 cells are wrong-side in IS (USDCNH h1 -3.25) and right-side in VAL: the sign flips |
| C2b | 24 | -3.30 to +1.36 | 4 IS episodes (2019-20); VAL's +176 bp on HK50 h5 is the 2023-24 build-ups followed by falls |
| C3 | 24 | -0.94 to +2.73 | only the gold S / h1 cells exceed t 2 |
| F1 | 18 (9 graded) | -1.40 to +1.00 | the 10 % threshold has 3 events per era |
| F2 | 9 | -2.05 to +1.89 | |

- Of the 138 graded cells, 15 have |t| >= 2: 4 on the declared side, 11 against it.
- The spread x1.5, +1 minute and late-entry columns change no verdict.
- Without 2020-03/04, no IS-best cell crosses a bar it did not already cross.

## Multiple testing
- 147 declared cells, 138 graded.
- Max |Z| of N normals:

  | N | median | 95th percentile |
  |---|---|---|
  | 24 | 2.19 | 3.09 |
  | 120 | 2.76 | 3.53 |
  | 147 | ~2.83 | |

- The best declared-side IS t is 2.73 (C3 XAU h1): p ~0.14 within its family of 24 and ~0.6 over all 147.
- The largest |t| (3.30) is a wrong-side cell.
- The 11 wrong-side |t| >= 2 cells are mostly one fact seen through several targets and holds: the next-session
  rebound after deleveraging days.

## Information worth keeping
1. **A free, exact daily SSE + SZSE margin history from 2010-03-31** is reachable through Eastmoney's data-centre API.
   It needs a date filter. Pages hold 800 rows, take 60-80 s each, and sometimes break mid-transfer.
2. **After a mainland down day with a large fall in the financing balance, Asian and US index CFDs rebound in the next
   Asian session** (post hoc).
   - HK50 h1 long +35 bp IS / +41 bp VAL.
   - Matched non-deleveraging down days: -5 / +2 bp.
   - Margin calls on the mainland, if anything, mark the low of the move by the time IC's HK50 can act.
   - A rule built on this would be post hoc. It could only be checked on HOLD, after a fresh pre-registration with the
     user's approval. At ~17 HOLD trades and a Sharpe ~0.3, its HOLD power is ~1.2: DEMO at most.
3. **CNH and AUD weaken over 3-5 days after deleveraging days in VAL (2022-24).** IS is too weak and PRE is flat
   without 2015, so this is not robust.
4. **The Chinese securities-lending series is not stationary.** It is tiny before 2019 (RQYE 3-7 bn yuan), large in
   2020-21 (120 bn), and curbed in 2023-24. Any C3 rule inherits that break.

## Directions that need the user (one-line value estimates)
- **Wind / iFinD maintenance-ratio (维持担保比例) distribution and forced-liquidation (平仓) volumes**, paid. They
  would give the real distance to the trigger instead of F1's cost-basis proxy. Value: low; the aggregate already shows
  rebound, not continuation. LIVE < 1 %, DEMO ~2 %.
- **Pre-registering the post-hoc C1 rebound for a single HOLD look.** Needs the user's decision, because the side was
  chosen after seeing IS / VAL. DEMO at most (HOLD power ~1.2). DEMO ~3 %, LIVE ~0.
- **Account-level Chinese margin data (Bian et al. used broker records)**: not public. ~0.

Correlation with C3 (gotobi): the drafted gold cell is daily +0.11, monthly +0.16. Nothing else survived.

## Files (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r40/C/`)
- **Fetching:** `fetch.py`, the polite fetcher. Raw JSON is in `web/em_lshj/`, the log in `web/requests.log`.
- **Library and signals:**
  - `lib.py`: loads (HOLD cut), fills, costs, swaps, cluster t, and the margin parser with the cut;
  - `sig.py`: series, z scores and the declared signals, with no prices.
- **Engine and grading:**
  - `power_pre.py`: the unconditional sd / cost table, output `out/power_pre.txt`;
  - `engine.py`: per-day trade cache `out/trades.pkl` (IC and PRE);
  - `grade.py`: the 120 declared cells, counts (`grade.py count`), random control; output `out/grade.txt` and
    `out/grade.json`;
  - `fallback.py`: F1 / F2, output `out/fallback.txt` and `out/fallback.json`.
- **Post hoc / information:**
  - `c3xau.py`, `c3xau_corr.py`: the gold-cell breakdown and the C3 correlation;
  - `posthoc_c1.py`: the matched-down-day rebound check.
- All Python ran as `research/.venv/bin/python -I` (the repo root is inserted in lib.py).

## HOLD look (2026-10-29 17:18 UTC; user-approved on 2026-10-30)
- **What was registered.** The post-hoc C1 rebound (long HK50 h1 after C1_k1.5 days), one cell with frozen code, in
  [PREREG_C1_hk50_rebound.md](PREREG_C1_hk50_rebound.md). It was registered at 17:12 UTC, before any 2025+ data was
  fetched or loaded.
- **Pass rule.** HOLD net > 0 and episode-clustered t >= 1.0.
- **Result.**

  | era | trades / episodes | net bp (t) |
  |---|---|---|
  | HOLD 2025-01..2026-09-24 | 24 / 17 | **+19.0 (0.74)** |
  | IS | 53 / 35 | +35.4 (2.14) |
  | VAL | 29 / 15 | +41.1 (0.77) |
  | IS + VAL + HOLD (pooled) | 106 / 67 | +33.2 (1.92) |

- **Verdict: FAIL; dropped for good.** No other cell, horizon, symbol or threshold was run on 2025+ data.
- **Add to the exhausted families:** "Chinese margin financing (deleveraging, build-up, securities lending, distance to
  the trigger) -> HK50 / CNH / AUD / JP225 / XAU 2016-24; the next-session HK50 rebound after deleveraging days held
  its sign in HOLD (+19 bp) but at t 0.74".
