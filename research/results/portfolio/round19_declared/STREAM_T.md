# Round 19, stream T: a second literature pass, declared rules only (2026-10-06)

Brief: [BRIEF.md](BRIEF.md) row T and round13_structural/BRIEF.md. Every cell was declared in
[HYPOTHESES_T.md](HYPOTHESES_T.md) (03:47 UTC) before any of its returns was computed; two corrections written after
seeing numbers (03:51 UTC) are information only. HOLD (2025-01 onwards) was not loaded: the panel ends 2024-12-31 and
Dukascopy was cut at 2016-01-01 at load.

## Answer

**No candidate at LIVE or DEMO. No PREREG_DRAFT.** 7 families, 63 declared cells (6 families never tested
before, 1 near-tested family re-declared with the paper's own rule and run on PRE). No primary cell has IS net
t >= 2.0 on its declared side. The best |t_IS mid| of any cell (2.19) sits inside every family's chance band.

Closest (information only, fails DEMO): **long/short US500 against Monday's move, Monday close -> Tuesday close**
(Ülkü & Andonov 2016, T3 hold-1 variant): IS mid +17.0 bp (t 2.19), net +14.1 (t 1.83, DEMO needs 2.0); VAL
+6.2 (t 0.68), net +4.6 (t 0.51). VAL/IS 0.37: it is shrinking. It beats 99.8 % of random entries in IS and 76 % in
VAL. Power 0.98 at the IS size and 0.39 at the VAL size.

## Step 1: what was already tested

The rounds 3-11 list (round 12 K) plus rounds 12-18 are in `scratchpad/r19/T/lit/tested_list_r19.md`. In short:
fixes and benchmarks, settlement and LETF flows, closing auctions, pinning, the overnight and European-open drifts,
pre/post central-bank drift, macro follow-through, lead-lag, crypto funding and expiries, intraday momentum (index,
FX, crude, metals), turn of month, calendar days, every 15/60-min index window by weekday (round 11 H), FX/gold
clock x calendar cells with PRE (rounds 13 M, 15 S, 18 B), and income/coupon/redemption dates.

## Step 2: literature search (different from round 12 K)

- **OpenAlex was unusable**: every call returned "Rate limit exceeded ... free daily budget shared by everyone on
  your network's IP ... $0 remaining" (resets at midnight UTC). Its venue filter was replaced by the same filter in
  **Crossref** (ISSN filter): JFE, RFS, JF, JFQA, J. Futures Markets, JIMF, JBF, J. Financial Markets, FRL, plus
  J. Empirical Finance, IRFA, JIFMIM, J. Commodity Markets, Energy Economics, Quantitative Finance, Review of
  Finance, Management Science, J. Financial Econometrics; 2015-2026; 44 queries, 630 papers (`lit/cr1.tsv`).
- **Working papers**: Crossref restricted to the DOI prefixes of the Fed Board (FEDS/IFDP), ECB, Bank of Canada and
  NBER, 15 queries, 371 rows (`lit/cb1.tsv`); BIS papers have no Crossref DOIs and were reached by web search
  (BIS WP 1029, BoJ ETF purchases).
- **arXiv** q-fin.TR / q-fin.ST, 18 queries (`lit/ax1.txt`): almost all ML or market-making; nothing new with a side.
- **Semantic Scholar** search (25 queries): 15 failed on HTTP 429; abstracts of Elsevier papers are withheld there,
  so they came from RePEc/IDEAS pages or web search. Papers read in full for the windows: Hu et al. 2022, Etula et al.
  2020, Dao et al. 2016 (`lit/pdf/`). SSRN was unreachable (no response).

Kept: an intraday or <= 5-day effect on an instrument among IC's 32 symbols, an explicit side and window, evidence
after 2010. Status: **screened here** (declared and tested this round), tested / near-tested earlier, or not testable.

| # | paper | mechanism, side, window | reported size vs IC cost | events/yr | status |
|---|---|---|---|---|---|
| 1 | Hu, Pan, Wang & Zhu 2022 JFE | uncertainty premium before NFP/ISM/GDP: long S&P 500, previous 16:00 ET close -> release - 5 min | +7.5-10.1 bp (2012-18 +7.0, t 2.3) vs US500 2-5 bp incl. swap | 36 | **screened T1** |
| 2 | Etula, Rinne, Suominen & Vaittinen 2020 RFS | month-end cash needs: short T-8..T-4, long T-3..T-1 (settlement deadline) | US 2003-13 reversal ~18 bp/day; 22/25 markets | 12 per index | **screened T2** |
| 3 | Ülkü & Andonov 2016 QF; Pigorsch & Schäfer 2024 FRL | Monday move reverses over the week (Monday afternoon part, US stocks 2007-22) | n/r | 50 | **screened T3** |
| 4 | Chiah & Zhong 2021 JBF | "Tuesday blues": Australian Tuesday returns lower, more after a bad US Monday | n/r | 50 | **screened T4** (index scan r11 H had 60-min windows only) |
| 5 | Caporale & Plastun 2019 FRL; Aharon & Qadan 2019 FRL | bitcoin Monday returns higher (2010-17) | n/r; C&P find no profitable rule | 52 | **screened T5** |
| 6 | Li, Zhu, Wen & Mohd Nor 2022 Energy Econ. | WTI: Monday negative, Wednesday positive (inventory schedule) | n/r; XTI 3-8 bp | 52 + 52 | **screened T6** |
| 7 | Dao, McGroarty & Urquhart 2016 JMFM | FX weekend gap (5 % tails) reverses by Monday's US close | 13-24 bp (majors) vs 1-2 bp | ~5 per pair | near-tested r3; **re-declared T7 with PRE** |
| 8 | Krohn, Mueller & Whelan 2024 JF | USD into / out of the fixes | ~1 bp | 250 | tested r3, r4, r10 E, r13 M (E1) |
| 9 | Melvin & Prins 2015 JFM; Evans 2018 JBF; Ito & Yamada 2018 JIMF; Husselmann & Kasikov 2019 QF; Osler & Turnbull 2026 JBF | WM/R 16:00 fix: hedging flows, pre-fix trend, post-reform behaviour | ~1-7 bp | 12-250 | tested r3, r10 E, r12 I, K1 |
| 10 | Gao et al. 2018 JFE; Baltussen et al. 2021 JFE; Rosa 2022 JFutM | first/overnight half-hour -> last half-hour, follow (thresholded) | n/r, gone out of sample (Rosa) | 250 | tested r4, r13 P, r17 Z |
| 11 | Li, Sakkas & Urquhart 2022 JFinM; Elaut et al. 2018 JFinM | intraday TS momentum incl. FX | n/r | 250 | tested K1 |
| 12 | Bangsgaard & Kokholm 2025 JBF | VIX-ETP end-of-day rebalancing pushes S&P into the close | n/r | 250 | near-tested (r4 LETF/gamma, r13 P, r17 Z big days); intraday VIX not in data |
| 13 | Kurov, Wolfe & Gilbert 2021 FRL (Lucca & Moench 2015) | pre-FOMC drift, gone after 2015 | 0 after 2015 | 8 | tested r3 (contaminated) |
| 14 | Kurov, Sancetta, Strasser & Wolfe 2019 JFQA | pre-release drift in the surprise's direction | needs the surprise | 100+ | tested r7 C (ISM) |
| 15 | Savor & Wilson 2013; Ai & Bansal 2018 | announcement-day premium (NFP day) | +12.7 bp, t 1.0 at IC | 12 | tested r3 |
| 16 | Mourey, Shahrour & Şoiman 2025 FRL | weekend crypto -> Monday stocks | - | 52 | tested r8 X6b |
| 17 | Weiss et al. 2026 FRL; Hoang & Phan 2026 FRL | Deribit Friday expiry reversal | BTC cost 3-27 bp | 52 | tested K4 |
| 18 | Kayacetin 2026 JIFMIM; Han, Han & Tian 2025 FRL | turn of the month (the FRL: disappearing) | - | 12 | tested swing v2 |
| 19 | Khademalomoom & Narayan 2019 JIFMIM | FX hour-of-day effects 2004-14 | n/r | 250 | covered by clock scans r4, r13 M (PRE), r15 S |
| 20 | Casado, Muga & Santamaria 2013 | US holidays and European markets | - | ~9 | near-tested r10 B3 |
| 21 | Mueller, Tahbaz-Salehi & Vedolin 2017 JF | carry earns on FOMC days | - | 8 | power-ruled out r7 C (<= 1.5); not tested |
| 22 | Ko 2026 FRL; BIS WP 1029 | BoJ buys ETFs in the afternoon after a morning TOPIX drop: long JP225 afternoon | n/r | ~30-100 | not tested: programme ended March 2024 (sales from 2026); not deployable |
| 23 | Hartzmark & Solomon 2022 (NBER w30688) | dividend-payment days push the market up | 4x top vs bottom quintile | ~50 | needs a payment calendar (K) |
| 24 | Pirrong 2023 JFutM | TAS positions move the settlement | - | 250 | needs TAS data (K) |
| 25 | Brooks, Katz & Lustig 2018 (NBER w25127) | post-FOMC drift in Treasuries | - | 8 | bonds not at IC; FX/index 1-5 d drift tested r11 F |
| 26 | Yang & Wang 2026 FRL | FOMC hour volatility in BTC/ETH | volatility only | 8 | no side |
| 27 | Baur et al. 2019 FRL; Bouri et al. 2021 IRFA | BTC time-of-day; intraday return curves | "no persistent effects"; model-based | - | no fixed side |
| 28 | Iwatsubo, Watkins & Xu 2018 JCM; Hauptfleisch, Putniņš & Lucey 2016 JFutM | gold/platinum intraday microstructure, price discovery | - | - | no side |
| 29 | Aleti, Bollerslev & Siggaard 2025 MS; Huddleston, Liu & Stentoft 2021 JFEc | ML on constituent / factor returns predicts 5-min market returns | Sharpe ~1 after costs (ETFs) | 250 x many | needs constituent data |
| 30 | Long, Zaremba et al. 2020 FRL | crypto same-weekday cross-section | - | - | needs many coins (IC has 2) |
| 31 | Lee, Liao & Lee 2022 JFutM | industry-ETF overnight sentiment -> index futures | - | 250 | needs ETF data |
| 32 | Kaourma et al. 2025 JIMF; Huang, Ranaldo, Schrimpf & Somogyi 2025 JFE | retail FX order flow on news; dealer constraints | - | - | needs order-flow data / no side |
| 33 | Huang, Tsai, Weng & Yang 2023 JBF | VIX futures intraday momentum | 21.8 %/yr net | 250 | not an IC symbol |
| 34 | Cocoma 2025 JFQA | theory of the pre-announcement drift | - | - | theory (supports #1) |

## Step 3: results (all 63 declared cells; bp per trade; t clustered by UTC day)

Costs = actual spreads at both fills + 0.6 bp for FX + swaps (index long -2 bp a night, energies -2.5). "power" =
per-trade net Sharpe x sqrt(trades/yr x 1.73), at the IS size and at the VAL size. Spread x1.5 and +1 minute for
every cell are in `out/*.out`; the only sign change is T7 USDCHF (b) in VAL (-0.02 -> +2.47 bp with +1 minute), which changes no verdict.

| cell | PRE mid (t) | IS / VAL mid bp (t) | cost IS / VAL | net IS / VAL (t) | VAL/IS | power IS / VAL size | trades/yr |
|---|---|---|---|---|---|---|---|
| T1 US500 a all3 | - | +1.4 (+0.29) / +4.2 (+0.77) | 4.7 / 3.6 | -3.3 (-0.71) / +0.7 (+0.12) | +3.11 | -0.38 / +0.09 | 31 |
| T1 US30 a all3 | - | +1.5 (+0.32) / +0.7 (+0.15) | 3.6 / 2.9 | -2.1 (-0.46) / -2.1 (-0.45) | +0.47 | -0.25 / -0.34 | 31 |
| T1 USTEC a all3 | - | +2.0 (+0.35) / +3.7 (+0.46) | 5.3 / 3.7 | -3.3 (-0.57) / -0.0 (-0.00) | +1.84 | -0.31 / -0.00 | 31 |
| T1 US500 b all3 | - | +1.8 (+0.41) / -3.2 (-0.63) | 2.1 / 1.0 | -0.3 (-0.06) / -4.2 (-0.82) | -1.77 | -0.03 / -0.62 | 32 |
| T1 US30 b all3 | - | +1.4 (+0.31) / -4.0 (-0.85) | 1.2 / 0.3 | +0.1 (+0.03) / -4.4 (-0.93) | -2.88 | +0.02 / -0.70 | 32 |
| T1 USTEC b all3 | - | +0.8 (+0.17) / -4.4 (-0.65) | 3.2 / 1.1 | -2.4 (-0.47) / -5.5 (-0.81) | -5.23 | -0.25 / -0.62 | 33 |
| T1 US500 a NFP+GDP | - | -2.3 (-0.46) / +5.0 (+0.71) | 4.1 / 3.1 | -6.4 (-1.26) / +1.9 (+0.27) | -2.16 | -0.68 / +0.21 | 21 |
| T1 US30 a NFP+GDP | - | -0.9 (-0.18) / +1.8 (+0.30) | 3.0 / 2.3 | -3.9 (-0.78) / -0.5 (-0.09) | -1.95 | -0.42 / -0.07 | 21 |
| T1 USTEC a NFP+GDP | - | -4.2 (-0.64) / +3.4 (+0.34) | 4.9 / 3.2 | -9.1 (-1.39) / +0.2 (+0.02) | -0.83 | -0.75 / +0.02 | 21 |
| T1 US500 b NFP+GDP | - | -1.4 (-0.29) / -1.5 (-0.23) | 2.2 / 1.1 | -3.5 (-0.74) / -2.5 (-0.40) | +1.07 | -0.40 / -0.30 | 22 |
| T1 US30 b NFP+GDP | - | -0.6 (-0.12) / -1.4 (-0.24) | 1.3 / 0.4 | -1.8 (-0.38) / -1.7 (-0.31) | +2.35 | -0.20 / -0.23 | 22 |
| T1 USTEC b NFP+GDP | - | -3.5 (-0.66) / -4.8 (-0.57) | 3.5 / 1.2 | -7.0 (-1.32) / -6.0 (-0.72) | +1.35 | -0.71 / -0.55 | 23 |
| T2 US500 L | - | +8.2 (+0.56) / +62.9 (+2.52) | 7.7 / 5.3 | +0.4 (+0.03) / +57.5 (+2.30) | +7.67 | +0.02 / +1.75 | 11 |
| T2 US500 S | - | -27.2 (-1.10) / +45.6 (+0.96) | 2.0 / 0.8 | -29.1 (-1.18) / +44.8 (+0.95) | -1.68 | -0.63 / +0.72 | 11 |
| T2 DE40 L | - | -8.1 (-0.43) / +35.1 (+1.86) | 6.9 / 6.1 | -14.9 (-0.79) / +28.9 (+1.53) | -4.34 | -0.42 / +1.16 | 12 |
| T2 DE40 S | - | -11.9 (-0.35) / +22.8 (+0.67) | 1.1 / 0.5 | -13.0 (-0.38) / +22.2 (+0.65) | -1.91 | -0.20 / +0.50 | 12 |
| T2 UK100 L | - | +21.8 (+1.11) / +3.7 (+0.24) | 8.0 / 7.2 | +13.8 (+0.70) / -3.5 (-0.23) | +0.17 | +0.38 / -0.17 | 11 |
| T2 UK100 S | - | +13.0 (+0.53) / -10.1 (-0.35) | 2.3 / 1.7 | +10.6 (+0.44) / -11.8 (-0.40) | -0.78 | +0.23 / -0.31 | 11 |
| T2 JP225 L | - | +9.9 (+0.56) / +17.2 (+0.72) | 10.2 / 6.9 | -0.3 (-0.02) / +10.2 (+0.43) | +1.73 | -0.01 / +0.32 | 11 |
| T2 JP225 S | - | -20.5 (-0.67) / -18.2 (-0.47) | 3.2 / 1.8 | -23.7 (-0.77) / -19.9 (-0.51) | +0.89 | -0.41 / -0.39 | 11 |
| T2 HK50 L | - | -5.9 (-0.35) / -9.5 (-0.20) | 8.4 / 7.9 | -14.3 (-0.85) / -17.4 (-0.37) | +1.60 | -0.46 / -0.28 | 11 |
| T2 HK50 S | - | +10.2 (+0.35) / +30.0 (+0.47) | 3.3 / 2.7 | +6.9 (+0.23) / +27.4 (+0.43) | +2.94 | +0.13 / +0.32 | 11 |
| T2 AUS200 L | - | -11.7 (-0.86) / +15.7 (+0.85) | 7.8 / 7.0 | -19.6 (-1.43) / +8.7 (+0.47) | -1.34 | -0.77 / +0.36 | 10 |
| T2 AUS200 S | - | -26.9 (-1.14) / +27.7 (+0.80) | 2.0 / 1.2 | -29.0 (-1.23) / +26.5 (+0.76) | -1.03 | -0.66 / +0.58 | 10 |
| T2 POOLED L | - | +2.5 (+0.22) / +21.4 (+1.31) | 8.1 / 6.7 | -5.6 (-0.50) / +14.6 (+0.89) | +8.51 | -0.43 / +1.02 | 66 |
| T2 POOLED S | - | -10.4 (-0.55) / +16.4 (+0.63) | 2.3 / 1.4 | -12.7 (-0.67) / +15.0 (+0.57) | -1.58 | -0.59 / +0.66 | 67 |
| T3 US500 siga holdfri | - | +7.8 (+0.56) / +15.0 (+0.79) | 5.3 / 3.9 | +2.5 (+0.18) / +11.2 (+0.59) | +1.93 | +0.10 / +0.44 | 40 |
| T3 US500 sigb holdfri | - | +3.3 (+0.23) / -2.6 (-0.14) | 5.5 / 4.6 | -2.2 (-0.16) / -7.2 (-0.38) | -0.81 | -0.08 / -0.29 | 40 |
| T3 US30 siga holdfri | - | +6.3 (+0.43) / -3.4 (-0.21) | 4.5 / 3.7 | +1.8 (+0.12) / -7.1 (-0.43) | -0.54 | +0.07 / -0.33 | 39 |
| T3 US30 sigb holdfri | - | +7.2 (+0.50) / -4.1 (-0.26) | 4.7 / 4.2 | +2.5 (+0.17) / -8.3 (-0.52) | -0.57 | +0.09 / -0.39 | 41 |
| T3 USTEC siga holdfri | - | +4.9 (+0.33) / +32.5 (+1.25) | 5.1 / 3.8 | -0.2 (-0.01) / +28.7 (+1.11) | +6.59 | -0.01 / +0.84 | 41 |
| T3 USTEC sigb holdfri | - | +5.2 (+0.35) / +10.1 (+0.39) | 5.2 / 4.6 | +0.0 (+0.00) / +5.5 (+0.21) | +1.94 | +0.00 / +0.16 | 42 |
| T3 DE40 siga holdfri | - | -17.1 (-1.25) / -13.0 (-0.77) | 4.9 / 4.5 | -22.0 (-1.60) / -17.5 (-1.03) | +0.76 | -0.86 / -0.78 | 49 |
| T3 DE40 sigb holdfri | - | -17.7 (-1.28) / -9.7 (-0.57) | 4.5 / 4.4 | -22.2 (-1.60) / -14.1 (-0.83) | +0.55 | -0.86 / -0.63 | 49 |
| T3 UK100 siga holdfri | - | -2.2 (-0.18) / -15.3 (-1.14) | 6.0 / 5.1 | -8.3 (-0.68) / -20.4 (-1.52) | +6.83 | -0.36 / -1.15 | 46 |
| T3 UK100 sigb holdfri | - | +1.8 (+0.15) / -24.5 (-1.84) | 6.3 / 5.0 | -4.4 (-0.36) / -29.5 (-2.21) | -13.29 | -0.19 / -1.68 | 46 |
| T3 JP225 siga holdfri | - | +17.7 (+1.08) / +12.2 (+0.55) | 6.6 / 5.1 | +11.1 (+0.68) / +7.1 (+0.32) | +0.69 | +0.36 / +0.24 | 42 |
| T3 JP225 sigb holdfri | - | +15.8 (+0.96) / +12.7 (+0.59) | 7.0 / 5.7 | +8.7 (+0.53) / +7.1 (+0.33) | +0.81 | +0.29 / +0.25 | 43 |
| T3 US500 siga hold1 | - | +17.0 (+2.19) / +6.2 (+0.68) | 2.8 / 1.6 | +14.1 (+1.83) / +4.6 (+0.51) | +0.37 | +0.98 / +0.39 | 40 |
| T4 AUS200 Tue cc | - | -10.2 (-1.68) / -2.9 (-0.39) | 2.0 / 1.2 | -12.2 (-2.00) / -4.0 (-0.55) | +0.28 | -1.08 / -0.42 | 45 |
| T4 (c) AUS200 Tue cc, US Mon <= p20: INVALID (look-ahead) | - | +30.4 (+1.33) / +72.1 (+2.26) | 2.2 / 1.3 | +28.2 (+1.23) / +70.9 (+2.22) | +2.37 | +0.66 / +1.69 | 6 |
| T4 AUS200 Tue sess | - | -4.9 (-0.90) / +0.2 (+0.03) | 2.0 / 1.3 | -6.9 (-1.27) / -1.2 (-0.24) | -0.03 | -0.68 / -0.18 | 46 |
| T4 (c') AUS200 Tue session, US Mon <= p20 (post hoc, info) | - | -53.7 (-2.10) / +13.3 (+0.93) | 2.5 / 1.5 | -56.2 (-2.19) / +11.8 (+0.82) | -0.25 | -1.17 / +0.62 | 6 |
| T5 BTCUSD Mon long | - | +18.3 (+0.64) / +13.1 (+0.50) | 13.5 / 3.5 | +4.8 (+0.17) / +9.7 (+0.37) | +0.72 | +0.10 / +0.28 | 45 |
| T5 ETHUSD Mon long (info) | - | -12.5 (-0.36) / +4.1 (+0.14) | 139.5 / 14.2 | -152.0 (-4.26) / -10.1 (-0.34) | -0.33 | -2.50 / -0.26 | 44 |
| T6 XTIUSD mon short | - | +17.6 (+0.57) / +9.1 (+0.52) | 7.2 / 3.3 | +10.4 (+0.34) / +5.8 (+0.33) | +0.52 | +0.23 / +0.25 | 44 |
| T6 XTIUSD wed long | - | +12.8 (+0.51) / -22.0 (-1.05) | 7.9 / 3.4 | +4.9 (+0.20) / -25.4 (-1.22) | -1.72 | +0.13 / -0.92 | 47 |
| T6 XTIUSD mon short fix | - | +15.3 (+0.53) / +5.9 (+0.34) | 7.1 / 3.3 | +8.2 (+0.29) / +2.6 (+0.15) | +0.39 | +0.19 / +0.11 | 47 |
| T6 XTIUSD wed long fix | - | +18.4 (+0.78) / -21.4 (-1.05) | 7.7 / 3.4 | +10.8 (+0.46) / -24.8 (-1.21) | -1.16 | +0.30 / -0.92 | 51 |
| T6 XBRUSD mon short fix | - | +0.1 (+0.01) / +11.4 (+0.68) | 6.3 / 2.7 | -6.2 (-0.38) / +8.7 (+0.52) | +98.29 | -0.25 / +0.40 | 47 |
| T6 XBRUSD wed long fix | - | +14.7 (+0.90) / -24.1 (-0.98) | 6.1 / 2.9 | +8.6 (+0.52) / -27.0 (-1.10) | -1.65 | +0.34 / -0.84 | 48 |
| T7 EURUSD exita | +32.4 (+3.43) | -0.4 (-0.03) / -6.8 (-0.79) | 1.5 / 0.9 | -1.9 (-0.14) / -7.7 (-0.91) | +19.25 | -0.08 / -0.69 | 3 |
| T7 EURUSD exitb | +4.1 (+0.87) | -8.2 (-1.07) / -6.9 (-1.18) | 1.4 / 0.9 | -9.7 (-1.26) / -7.8 (-1.35) | +0.83 | -0.68 / -1.02 | 3 |
| T7 USDJPY exita | +25.9 (+2.45) | +6.8 (+0.47) / -18.3 (-1.55) | 1.5 / 1.5 | +5.3 (+0.37) / -19.8 (-1.68) | -2.68 | +0.22 / -1.28 | 5 |
| T7 USDJPY exitb | +15.3 (+3.00) | -2.7 (-0.23) / -19.5 (-2.34) | 1.4 / 1.4 | -4.1 (-0.35) / -20.8 (-2.49) | +7.09 | -0.20 / -1.89 | 5 |
| T7 GBPUSD exita | +10.1 (+0.83) | -9.3 (-0.72) / -17.8 (-0.80) | 2.2 / 1.2 | -11.5 (-0.90) / -19.0 (-0.86) | +1.92 | -0.53 / -0.65 | 6 |
| T7 GBPUSD exitb | -1.8 (-0.31) | -16.6 (-2.13) / -12.8 (-1.10) | 2.0 / 1.1 | -18.5 (-2.40) / -14.0 (-1.19) | +0.78 | -1.41 / -0.91 | 6 |
| T7 AUDUSD exita | -19.2 (-0.93) | +17.3 (+1.10) / +18.7 (+0.98) | 2.0 / 1.1 | +15.4 (+0.98) / +17.6 (+0.92) | +1.08 | +0.53 / +0.70 | 4 |
| T7 AUDUSD exitb | -11.2 (-1.07) | -0.9 (-0.08) / -3.4 (-0.23) | 1.6 / 1.0 | -2.6 (-0.23) / -4.4 (-0.30) | +3.74 | -0.12 / -0.23 | 4 |
| T7 USDCHF exita | +15.8 (+1.49) | +0.3 (+0.03) / +8.9 (+0.52) | 3.2 / 2.7 | -2.8 (-0.24) / +6.2 (+0.37) | +27.00 | -0.14 / +0.28 | 4 |
| T7 USDCHF exitb | +0.2 (+0.03) | -6.3 (-0.87) / +2.4 (+0.42) | 2.9 / 2.4 | -9.2 (-1.24) / -0.0 (-0.00) | -0.38 | -0.73 / -0.00 | 4 |
| T7 USDCAD exita | -7.7 (-0.67) | +5.5 (+0.39) / -13.0 (-0.64) | 1.8 / 1.5 | +3.7 (+0.26) / -14.5 (-0.72) | -2.37 | +0.14 / -0.55 | 4 |
| T7 USDCAD exitb | +2.6 (+0.51) | +3.4 (+0.45) / -2.1 (-0.22) | 1.6 / 1.4 | +1.8 (+0.23) / -3.5 (-0.36) | -0.62 | +0.12 / -0.27 | 4 |
| T7 NZDUSD exita | -0.7 (-0.05) | +7.1 (+0.54) / -8.7 (-0.28) | 3.0 / 2.2 | +4.1 (+0.32) / -11.0 (-0.36) | -1.23 | +0.19 / -0.27 | 4 |
| T7 NZDUSD exitb | -4.9 (-0.66) | +6.4 (+0.55) / -2.9 (-0.25) | 2.7 / 2.1 | +3.7 (+0.32) / -5.0 (-0.43) | -0.45 | +0.19 / -0.33 | 4 |
| T7 POOLED exita | +8.0 (+1.01) | +3.5 (+0.41) / -5.3 (-0.40) | 2.1 / 1.5 | +1.3 (+0.16) / -6.9 (-0.52) | -1.53 | +0.14 / -0.75 | 26 |
| T7 POOLED exitb | +0.6 (+0.16) | -4.3 (-0.66) / -7.0 (-1.23) | 1.9 / 1.4 | -6.2 (-0.95) / -8.5 (-1.48) | +1.65 | -0.92 / -1.71 | 26 |

### Per family: primary cell, chance benchmark, random-entry control

| family | cells | primary cell: IS / VAL net (t) | best \|t_IS mid\| | sign-flip null median / p95 | random entries beaten IS / VAL (primary) | verdict |
|---|---|---|---|---|---|---|
| T1 pre-announcement (Hu et al.) | 12 | US500 (a): -3.3 (-0.71) / +0.7 (+0.12) | 0.66 | 1.30 / 2.45 | 64 % / 77 % | **fails**: no drift at mid in 2016-24 (IS +1.4, VAL +4.2 bp) |
| T2 dash for cash (Etula et al.) | 14 | US500 L: +0.4 (+0.03) / +57.5 (+2.30) | 1.14 | 1.87 / 2.84 | 61 % / 99.6 % | **fails** IS; VAL alone is 2022-23 |
| T3 Monday reversal (Ülkü & Andonov) | 13 | US500 (a) to Friday: +2.5 (+0.18) / +11.2 (+0.59) | 2.19 | 1.82 / 2.84 | 85 % / 61 % | **fails** (hold-1 variant closest, IS net t 1.83) |
| T4 Tuesday blues (Chiah & Zhong) | 2 valid | AUS200 (a): -12.2 (-2.00) / -4.0 (-0.55) | 1.68 | 0.94 / 2.15 | 3 % / 41 % | **fails**, wrong side in IS |
| T5 BTC Monday (Caporale & Plastun) | 1 | +4.8 (+0.17) / +9.7 (+0.37) | 0.64 | 0.67 / 1.99 | 77 % / 76 % | **fails** |
| T6 crude day of week (Li et al.) | 4 | XTI Mon short: +8.2 (+0.29) / +2.6 (+0.15); Wed long: +10.8 (+0.46) / -24.8 (-1.21) | 0.90 | 1.32 / 2.39 | 70 % / 51 %; 78 % / 15 % | **fails**; IS rests on April 2020 |
| T7 FX weekend overreaction (Dao et al.) | 16 | pooled (a): PRE +6.6 (+0.83), IS +1.3 (+0.16), VAL -6.9 (-0.52) | IS 2.13 (wrong side); PRE 3.43 | IS 1.95 / 3.08; PRE 1.91 / 2.93 | 78 % / 25 % | **fails**: PRE-only (EURUSD, USDJPY), gone since 2016 |

All 63 cells: the expected max |z| of 63 independent normals is ~2.6; nothing exceeds it.

### What the numbers say, family by family
- **T1.** The paper's 7-10 bp overnight drift before NFP/ISM/GDP is absent on IC's US indices in 2016-24 (pooled
  three types +1.4 bp IS, +4.2 VAL; NFP+GDP alone -2.3 / +5.0). Its subperiod stability ended with the paper's sample
  (2018). The paper's window costs 3.6-4.7 bp at IC (16:01 spread plus the rollover swap), so even its 2012-18 size
  (+7.0) would leave ~3 bp net on a ~55 bp sd, power ~0.4.
- **T2.** No dash-for-cash pattern in 2016-21 in any of the six indices (pooled L +2.5 bp, S -10.4 bp on a short,
  i.e. prices rose in the "pressure" days). VAL's +63 bp US500 reversal is 2022 (+133) and 2023 (+54), the bear market.
  Since US settlement moved to T+2 (2017) and T+1 (2024), the deadline effect has had less room.
- **T3.** The weekly reversal of Monday's move is not in index CFDs 2016-24 (US500 +7.8 / +15.0 bp mid, t < 0.8;
  DE40 and UK100 go the other way). Only the one-day version on US500 has an IS mid t above 2, and it fell to a
  third in VAL.
- **T4.** AUS200 rises on Tuesdays in IS (short loses -10 bp, t -1.7). The paper's conditional statement ("lower
  after a bad US Monday") is the overnight transmission of the US move itself: the declared cell (c) could only
  observe it with look-ahead (the US Monday closes inside the trade), and its executable form (c', post hoc) has
  AUS200 *rebounding* in the Tuesday session (-54 bp for the short, t -2.1, IS) and the opposite in VAL (n 13).
- **T5.** BTC Monday is +18 / +13 bp mid on a 400-450 bp daily sd; IC's 2018-21 BTC cost (13.5 bp) takes most of it.
- **T6.** XTI's IS numbers are April 2020 (without it Monday-short IS is -18.8 bp, t -1.1); Wednesday long reverses in
  VAL (-21 bp, 0/3 years). XBRUSD has no quotes at the declared Sunday 19:00 / Tuesday 18:05 ET entries; the
  first-quote fix (written after the first run) is applied to both energies and changes no verdict.
- **T7.** The paper's effect is real in its own era: PRE EURUSD +32 bp (t 3.4, 9/10 years), USDJPY +26 (t 2.5) to the
  US close, beyond the PRE chance band (p95 2.93). After its 2016 publication it is gone: pooled IS +3.5, VAL -5.3 bp;
  EURUSD -0.4 / -6.8. This repeats round 3's "no IS signal" with the paper's own rule.

### Information only (found after looking; not candidates)
- US500 Monday -> Tuesday reversal (T3 hold 1): IS +17.0 bp mid (t 2.19), VAL +6.2 (t 0.68); post-2021 decay.
- US500 month-end "positive reversal" (T2 L) +63 bp in VAL, from 2022-23 only.
- AUS200 Tuesday-session rebound after a bottom-quintile US Monday (c'): IS -54 bp for the declared short; post hoc,
  13 VAL events, sign flips.
- The FX weekend reversal (Dao et al.) is a published effect that decayed after publication: 2004-15 strong, 2016-24
  nothing. It is the clearest case this round of "literature effect, out of sample, gone".

## Untested ideas for the next round
- Mueller, Tahbaz-Salehi & Vedolin (2017): carry on FOMC days, now with PRE (Dukascopy H1 2004-15, 8 events a year,
  FRED short rates in research/data/rates for the carry ranking); DEMO tier at best (power-ruled out at <= 1.5).
- The T3 one-day Monday reversal on 2004-15 index data (Dukascopy offers index CFDs; fetching them is a user decision).
- Dividend-payment price pressure (Hartzmark & Solomon) needs an S&P 500 payment-date calendar (user decision).
- BoJ ETF afternoon purchases (Ko 2026; BIS WP 1029): only a mechanism check on 2016-23; the programme ended in
  March 2024 and the BoJ started selling in 2026, so the reverse flow (selling into strength) is a possible future
  direction once its schedule is public.
- VIX-ETP end-of-day rebalancing (Bangsgaard & Kokholm 2025) conditioned on the day's VIX-futures move needs intraday
  VIX futures (not in the data); with daily VIX only it collapses to round 13 P's big-day close rule.

## Scripts and outputs (scratchpad, not in the repo)
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r19/T/`
- `scripts/cr_search.py` (Crossref venue search), `cr_prefix.py` (working papers), `arxiv_search.py`,
  `s2_search.py`, `s2_abs.py`; queries and results in `lit/` (`q_*.txt`, `cr1.tsv`, `cb1.tsv`, `ax1.txt`,
  `s2_1.txt`, `abs1.txt`, PDFs and text in `lit/pdf/`), tested list `lit/tested_list_r19.md`.
- Calendars: `scripts/parse_gdp.py` -> `lit/cal/us_gdp.json` (BEA release schedules 2016-24 via Wayback);
  `scripts/make_exch_cal.py` -> `lit/cal/exch_holidays.json`; NFP and FOMC from round 12's shared calendars.
- `scripts/tlib.py` (engine on round 12 K's klib: fills at T+1, actual spreads, swaps, day-clustered t, controls,
  sign-flip null), `t1_preann.py`, `t2_dash.py`, `t3_monday.py`, `t456.py` (T4-T6), `t7_fxweekend.py`,
  `summary.py`.
- Outputs: `out/t1.out`, `t2.out`, `t3.out`, `t456.out`, `t7.out` (every cell with x1.5, +1 min, years, controls,
  chance), `out/*.pkl` (trade arrays), `out/summary.md`.
