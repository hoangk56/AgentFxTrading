# Round 35, stream T: Asian equity-derivative positioning by investor type -> HK50, JP225, US500, USTEC, AUDUSD, USDJPY

Written 2026-10-28 from 01:38 UTC (`date -u`). Hypotheses: [HYPOTHESES_T.md](HYPOTHESES_T.md), written at 01:35 UTC
before any series was joined to a return. Nothing was added after the returns were seen, and no side was changed.
Bars: research/PROMPT.md, LIVE / DEMO only.

HOLD (2025-01..2026-09-24) stayed closed. Every request had end_date <= 2024-12-31, the parser drops later rows, and
IC prices were loaded at ts < 2025-01-01. Nothing slipped.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

- 66 declared cells in four families. On the declared side, the best IS net t is +1.76 (F3, foreign TXO flow, US500,
  h3). Its VAL is -19 bp (t -1.18).
- No cell reaches IS t 2 on the declared side.
- The largest |t| is -3.56, on the wrong side: C1, foreign buying of Taiwan stocks -> USDJPY, k1 h3. PRE is -0.24
  and VAL +0.08. With the trades that span a gotobi window removed, it is -1.21.
- The positioning tables are real and move with the market on the same day, but they say nothing about the next
  day.
  - Same-window correlation with the Asian session: up to +0.45 for investment trusts' futures change and +0.48 for
    foreign cash buying.
  - Next-day correlation with HK50, JP225 or US500: |rho| <= 0.09 in every series and era.
  - LIVE needs about 0.17-0.23.
- **KRX and CFFEX could not be used.**
  - KRX puts every statistics page behind a login.
  - CFFEX takes 60 s per request, so a full pull would take about 58 h.
  - TAIFEX's own site serves only the last 3 years.
- The TAIFEX tables were loaded from a faithful free mirror (FinMind), but only from 2018-06. The futures and options
  families therefore have a shortened IS of 2018-09..2021 (about 3.3 years). LIVE's t >= 2.5 and DEMO's t >= 2.0
  still apply.

## Sources (fetch log: scratchpad `web/requests.log`, 70 requests; 2 WebSearches)
| source | fetched | history used (cut 2024-12-31) | usable? |
|---|---|---|---|
| TAIFEX three institutional investors, by contract and call / put (taifex.com.tw; no robots rules, robots.txt is a 404 page) | probes only | the form's `firstDate` is 2023-10-27. Queries for 2010 and 2023-06 return an empty table, and the CSV download answers "DateTime error". Older data is sold through TAIFEX's paid application (公開資料申購) | **no** for IS |
| FinMind open API, no token and no account: `TaiwanFuturesInstitutionalInvestors` (TX, MTX), `TaiwanOptionInstitutionalInvestors` (TXO) | 21 yearly requests, 2.5 s apart | 2018-06-05..2024-12-31, 1,605 days. Investor types: foreign institutions (外資), dealers (自營商), investment trusts (投信). Long and short trades and OI | **yes**. Matches TAIFEX's own 2024-01-02 page exactly (foreign TX long trades 47,732, long OI 48,357, short OI 65,786) |
| TWSE cash-market three-institution flows (BFI82U) via FinMind `TaiwanStockTotalInstitutionalInvestors` | 11 requests | 2004-04-07..2024-12-31, 5,111 days. Foreign = 外資 + 外資自營商 after their 2017-12 split | **yes**. Matches twse.com.tw BFI82U for 2004-04-07 exactly |
| KRX data.krx.co.kr, derivatives and stocks by investor type | 5 probes | every menu answers "로그인 또는 회원가입이 필요합니다" or "Please login or sign up to continue". global.krx.co.kr only links back to it | **no** (login wall) |
| finance.naver.com (Korean investor-type tables) | robots.txt | `Disallow: /` | **no** |
| NSE India participant-wise OI (FII / DII / Pro / Client index futures, a related source) | 3 probes | Akamai answers 403 "Access Denied" for every URL, including robots.txt | **no** (blocked from this Mac) |
| CFFEX member rankings, `IF_1.csv` (with a 期货公司 / 非期货公司 split) | 1 request, 60.8 s | about 3,500 days would take about 58 h | **no** (no fast route, as in round 34 H) |
| JPX daily participant volume, Nikkei 225 futures by broker | JSON back-number list | 13 months online only | **no** |
| FinMind `TaiwanFuturesOpenInterestLargeTraders` | 1 request | 400: "Your level is free" (sponsor tier) | **no** |

**Timing.** OI is at the TAIFEX day-session close, 13:45 Taipei (05:45 UTC). The tables are posted around 15:00
Taipei, and BFI82U after the 13:30 cash close. Entry is 09:30 UTC (17:30 Taipei) on Taiwan date D, filled at +1
minute; exit is at 09:30 UTC h weekdays later. No entry falls inside C3's 23:00-02:00 UTC window. USDJPY is also
reported with every trade whose hold contains a gotobi window removed. The gotobi dates come from C3's trade file,
which starts in 2016, so PRE has no exclusion.

## Power before the numbers
- LIVE at k0 h1 needs a per-trade net edge of: US500 15.5 bp, JP225 18.4, HK50 17.5, USTEC 19.3, AUDUSD 8.7,
  USDJPY 7.4. At k1 it needs about 1.8x those. That is a next-day correlation of about 0.17-0.23.
- The literature points to about 0.03-0.05 outside Taiwan:
  - Chang, Hsieh & Lai (2009) is about the TAIEX itself, which IC does not list.
  - Richards (2005) finds that foreign flows follow yesterday's global returns.
- Prior: LIVE about 1 %, DEMO about 3-5 %.
- The measured next-day |rho| <= 0.09 is below even DEMO's requirement on the shortened IS (Sharpe 0.07 at k0).

## Results
- **Units:** bp per trade.
- **Cost (09:30 UTC, IS, including swap):** HK50 5.9 / 9.4 at h1 / h3; JP225 5.4 / 8.9; US500 3.9 / 7.4; USTEC
  5.5 / 9.4; AUDUSD 1.6 / 2.8; USDJPY 1.1 / 1.9.
- **t:** per trade at h1, Newey-West (lag 3) at h3.
- **pow:** per-trade net Sharpe x sqrt(1.73 x trades per year / h).
- **Robustness:** spread x1.5 and +1 minute change no verdict (every line is in `out/cells.txt`).

### IS-best cell of each family (declared side)
| hypothesis | cell (chosen on IS) | eras | mid IS (t) / VAL (t) | net IS (t) | net VAL (t) | net PRE (t) | VAL / IS | Sharpe IS / VAL; pow IS / VAL | random control (beats, IS / VAL) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 change in foreign net TX-equivalent futures OI, follow | AUDUSD k1 h1 | IS 2018-09..21, VAL | +7.89 (1.64) / -4.52 (-0.99) | +6.37 (1.32) | -5.89 (-1.29) | n/a | < 0 | 0.092 / -0.084; 0.87 / -0.98 | n/r (IS t < 1.5) | none |
| F1 | USTEC k1 h1 | same | +16.25 (1.38) / -8.33 (-0.82) | +11.92 (1.01) | -11.55 (-1.14) | n/a | < 0 | 0.070 / -0.075; 0.66 / -0.87 | n/r | none |
| F2 extreme foreign net futures level, follow, k1 h3 fixed | HK50 | same | +31.64 (1.87) / -8.65 (-0.43) | +23.18 (1.37) | -15.59 (-0.78) | n/a | < 0 | 0.107 / -0.053; 0.76 / -0.49 | n/r | none |
| F3 foreign net bullish TXO flow (Chang et al. 2009), follow, k1 | US500 h3 | same | +30.87 (2.28) / -12.63 (-0.79) | **+23.80 (1.76)** | -19.03 (-1.18) | n/a | < 0 | 0.105 / -0.099; 0.57 / -0.54 | 0.99 / 0.155; circular shift 0.99 / 0.185 | none (VAL < 0) |
| F3 | USTEC h3 | same | +32.62 (2.09) / -21.90 (-0.98) | +24.33 (1.56) | -29.42 (-1.32) | n/a | < 0 | 0.096 / -0.112; 0.52 / -0.62 | 0.975 / 0.14; shift 0.99 / 0.14 | none |
| F3 | USDJPY h3 | same | +10.59 (1.71) / +2.99 (0.28) | +8.75 (1.41) | +1.33 (0.12) | n/a | 0.15 | 0.103 / 0.011; 0.56 / 0.06 | n/r | none. Without gotobi-spanning trades: IS -0.99 (t -0.10, n 36) |
| C1 foreign net buying of Taiwan stocks (BFI82U), follow | AUDUSD k1 h3 | PRE 2004-15, IS, VAL | +11.70 (1.54) / +6.92 (0.92) | +9.04 (1.19) | +4.27 (0.57) | -0.50 (-0.09) | 0.47 | 0.076 / 0.043; 0.49 / 0.27 | n/r | none (IS t 1.19; ex-2020 IS +5.4) |
| C1 | HK50 k1 h3 | IS, VAL | +15.56 (1.17) / +38.35 (1.77) | +6.44 (0.48) | +30.54 (1.41) | n/a | 4.7 | 0.029 / 0.109; 0.18 / 0.67 | n/r | none |
| C1 (wrong side, information) | USDJPY k1 h3 | PRE, IS, VAL | -19.06 (-3.23) / +2.76 (0.30) | **-21.05 (-3.56)** | +0.72 (0.08) | -1.17 (-0.24) | sign flip | | | none. Without gotobi-spanning trades: IS -11.63 (t -1.21, n 79). IS only, and the reversed side would be post hoc |

"n/r" means not run. Per the declared rule, only cells with declared-side IS t >= 1.5 got the 200-seed random-entry
and circular-shift controls.

### All cells (IS net t, declared side; full lines in `out/cells.txt`)
- **F1 (24 cells): -2.59 to +1.32.**
  - Every k0 cell on an index is negative in both IS and VAL. The basket at k0 h3 is -2.33 / -2.06 net, but its mid
    is only -1.07 / -0.98: that is cost plus a small reversal.
  - Reversing the side would give the basket about +3-4 bp mid against about 5 bp cost, so it is not tradable either
    way.
- **F2 (6 cells): -0.17 to +1.37.** VAL is <= 0.06 except AUDUSD (+0.23) and USDJPY (+0.39).
- **F3 (12 cells): -1.92 to +1.76.**
  - Every h1 cell is <= 0.
  - The h3 index cells are positive in IS and all negative in VAL (-0.54 to -1.35).
- **C1 (24 cells): -3.56 to +1.19.**
  - Index k0 cells are -2.47 to -0.47.
  - FX PRE is -2.64 to -0.09.
- **Equal-weight index basket (information):**

  | family / cell | net IS (t) | net VAL (t) |
  |---|---|---|
  | F1 k1 h1 | +3.11 (0.31) | -9.06 (-1.10) |
  | F3 k1 h3 | +13.08 (0.95) | -24.10 (-1.27) |
  | C1 k1 h1 | -5.35 (-0.84) | +6.34 (0.77) |

- **Excluding March-April 2020** lowers most IS-best cells (F3 US500 h3: +23.8 -> +15.0; F2 HK50: +23.2 -> +9.8).

## Multiple testing
- 66 cells. Over 66 independent normals, the median of the max |Z| is 2.56 and the 95th percentile 3.36. The
  cells are correlated across targets, so the effective count is lower.
- The best declared-side IS t (+1.76) is well below the median.
- The largest |t| (3.56, wrong side) is near the 95th percentile but vanishes in PRE and VAL. Without gotobi-spanning
  trades it is -1.21.
- No family is beyond chance.

## Information worth keeping
1. **Same-window correlation** of each z-scored series with the Asian session's return (previous weekday 09:30 UTC ->
   D 05:45 UTC):

   | series | target | IS | VAL |
   |---|---|---|---|
   | investment trusts' futures change | HK50 / JP225 / US500 | +0.45 / +0.45 / +0.46 | +0.26 / +0.35 / +0.37 |
   | foreign cash buying | all three | +0.40-0.48 | +0.35-0.47 |
   | dealers' net TXO flow | all three | +0.31-0.36 | |
   | foreign futures change | all three | 0.01-0.13 | 0.14-0.24 |

   Local institutions and foreign cash flows trade with the day's move. The foreign futures position follows it only
   weakly.
2. **Next-day correlation** (09:30 -> 09:30 UTC): |rho| <= 0.09 for every investor type, family, target and era. The
   largest are about +0.086, for dealers' and foreign cash buying -> JP225 in VAL only (IS +0.02).
3. The F1 change has a lag-1 autocorrelation of -0.22. Big expiry and roll days reverse the next day, which is noise
   for a position-change signal. F2's level persists (lag-1 autocorrelation 0.96), so its k1 h3 trades come in long
   streaks of the same side and its IS t is inflated relative to the independent count.
4. A free, exact mirror of TAIFEX's three-institution tables exists from 2018-06, and TWSE's cash flows from 2004-04
   (FinMind, no token). They can be reused for any later Taiwan question.

## Directions that need the user (one-line value estimates)
- **TAIFEX history 2008-2018** (TAIFEX paid application, or a FinMind sponsor tier, which also unlocks large-trader
  OI). It would give F1 / F3 a full IS and a PRE era. Value: low. The only IS hint (F3 h3) reversed in VAL, and the
  next-day |rho| is <= 0.05. LIVE about 1 %, DEMO about 2-3 %.
- **KRX account** (foreigners' KOSPI200 futures and USD/KRW futures by investor type, since the 1990s-2000s). Value:
  low-moderate. Korean foreign futures flow is the best-known case in the literature. On Taiwan's evidence, though,
  the next-day link to other markets is below 0.1. LIVE about 1 %, DEMO about 3 %.
- **NSE India participant OI** (FII index futures long / short, from about 2012) is blocked by Akamai from this Mac. It
  would need another network or a vendor copy. LIVE about 1 %.
- **CFFEX rankings** need a 58-hour polite crawl, or a vendor with an account. Value: about 0 after round 34 H's null
  on SHFE and this round's null on TAIFEX. LIVE below 1 %.

Correlation with C3 was not computed, because no rule survived.

## Files
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r35/T/`:
- **Fetch:**
  - `scripts/fetch.py`: logged single fetch, 1.2 s minimum per host.
  - `scripts/dl_finmind.py`: sequential, 2.5 s apart, end dates <= 2024-12-31.
  - Raw files are in `web/`, and the log is `web/requests.log`.
- **Parse:** `scripts/parse_finmind.py`, run with `python -I`, writes `clean/tw.json`.
- **Engine:**
  - `scripts/px.py` and `scripts/lib.py`, from round 34 H. Changes: a 09:30 UTC clock, index symbols and USDJPY PRE
    from duka/m1.
  - `scripts/sig.py`: signals with past-only z-scores.
- **Runs:**
  - `scripts/power.py`: unconditional sd and cost.
  - `scripts/cells.py`: 66 cells, plus the USDJPY ex-gotobi lines.
  - `scripts/rand_info.py`: random controls, basket and correlations.
- **Outputs:** `out/cells.txt`, `out/cells_F1_F2_F3_C1.json`, `out/rand_info.txt`, `out/rand.json`.
