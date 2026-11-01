# Round 38, stream S: hypotheses (FINRA daily short-sale volume, ETF primary-market flows)

Written 2026-10-29 from 11:15 UTC (`date -u` 11:15:40), **before any return was computed**. At this time the stream had
loaded, not joined to any return: FINRA Reg SHO daily short-volume files being downloaded (2009-08..2024-12 only), the
shares-outstanding histories of SPY, DIA (SSGA navhist), IWM, IVV, EWJ (iShares), all cut at 2024-12-31 at parse, and an
IC price panel (13:00 UTC, NY 09:31, NY 15:55 on NYSE days 2009-08..2024-12, cut at ts < 2025-01-01) used here only for
spreads and the daily sd. Bars: research/PROMPT.md, LIVE / DEMO only (no RELAXED).

Disclosures (HOLD hygiene): one web search for Invesco QQQ shares outstanding returned a Fidelity snippet with a current
QQQ NAV and share count of unknown date (likely 2026). No return; not used. No other 2025-26 value has been seen.

## Literature that fixes the sides (before any return)
- Diether, Lee & Werner 2009 (RFS), Boehmer, Jones & Zhang 2008 (JF): short sellers are informed / contrarian; high
  short volume predicts lower returns (stock level, 2005-07 Reg SHO pilot, horizons of days).
- Wang, Yan & Zheng 2020 (JFE 135, "Shorting flows, public disclosure, and market efficiency"): with FINRA's daily files
  public (2010-15), shorting flows still predict lower returns, but over months; **abnormal short-term flows do not
  predict returns**. This is the prior for 1-5 day horizons: null.
- Rapach, Ringgenberg & Zhou 2016 (JFE): aggregate short interest predicts lower market returns (monthly).
- ETFs: Evans, Moussawi, Pagano & Sedunov ("ETF short interest and failures-to-deliver: naked short-selling or
  operational shorting?"): most ETF short volume is operational shorting by market makers / APs who sell ETF shares
  short to meet buy demand and create later; they find **no relation with the underlying's future return**. The demand
  it reflects is buy pressure on the ETF; Brown, Davies & Ringgenberg 2021 (RF 25(4)) and Ben-David, Franzoni & Moussawi
  2018 (JF) show non-fundamental ETF demand / flows are followed by reversal of the underlying. Both readings give the
  same side: **high short-volume ratio -> short the underlying** (informed shorts, or reversal of buy pressure).
- Practitioner counter-claim: SqueezeMetrics 2017 "Short is long" (DIX): off-exchange short volume of S&P 500
  components is market makers shorting into customer buying and predicts **higher** S&P returns over weeks. Declared as
  its own small family (S2-DIX, long side) because the mechanism differs; counted in the multiple-testing total.
- Flows: BDR 2021, BFM 2018: ETF creations (inflows) -> lower subsequent underlying returns (reversal; their tests are
  monthly, cross-sectional). Side: **inflow z > k -> short, outflow -> long.** Gold / silver flows are excluded (round
  31 G did GLD / IAU / SLV with the continuation side).

## Sources and publication clock
| source | URL | span | public when | used from |
|---|---|---|---|---|
| FINRA Reg SHO daily short volume | https://cdn.finra.org/equity/regsho/daily/{CNMS,FNSQ,FNYX}shvolYYYYMMDD.txt | FNSQ + FNYX 2009-08..2018-07 (TRFs; FNQC / FNRA empty), CNMS 2018-08..2024-12 (= FNSQ + FNYX, verified by round 35 on SPY) | FINRA posts the day's file by ~18:00 ET on D | D+1 13:00 UTC (9:00 ET), i.e. >= 15 h later |
| SSGA NAV history (SPY, DIA) | https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/navhist-us-en-{spy,dia}.xlsx | 2003-12..2024-12 (cut) | the row dated D (NAV, shares outstanding) is posted after the close / next morning; it may carry D-1 creations (T+1 booking) | D+1 13:00 UTC; variant one more day |
| iShares fund download, Historical sheet (IWM 239710, IVV 239726, EWJ 239665) | blackrock.com get-fund-document?portfolioId=... | 1996/2000..2024-12 (cut) | as above | as above |
| Not found free: Invesco QQQ, USCF USO / UNG daily shares outstanding (no history download on the issuer pages) | | | | not used |

Signal: SVR_D = ShortVolume / TotalVolume (FINRA TRF volume only; exchange volume is not in these files).

## Costs and sd (measured on the panel, 13:00 UTC, before any signal)
Median full spread at 13:00 UTC IS / VAL (bp): US500 2.12 / 1.14, USTEC 2.88 / 1.35, US30 0.96 / 0.29, US2000 3.3 / 2.6
(0.34 pt x 1.5 assumed, bid-only data), JP225 3.5 / 2.5, XAUUSD 0.73 / 0.41 (+0.6 commission), XAGUSD 3.4 / 3.8 (+0.6),
XTIUSD 5.6 / 3.5, XNGUSD 11.6 / 46, EURUSD ~0 / ~0 (+0.6), USDJPY ~0.1 (+0.6). Swaps per round 32 V / 35 O convention
(research.specs rollovers, research/swing/rates.py; XTI -2.5 bp a night). 13:00->13:00 daily sd IS / VAL (bp): US500
97 / 113, USTEC 122 / 153, US30 102 / 96, US2000 136 / 153, JP225 131 / 126, XAU 89 / 89, XAG 171 / 181, XTI 420 (Apr
2020) / 235, XNG 319 / 450, EURUSD 45 / 51, USDJPY 52 / 71.

## Power arithmetic (before any test)
HOLD = 2025-01-02..2026-09-24 ~ 437 US trading days (1.73 y). LIVE needs per-trade net Sharpe x sqrt(n_HOLD) >= 3.
| cell type | trades / yr | n HOLD | LIVE per-trade SR | e.g. US500 net edge | DEMO (IS t 2) SR | reachable bar |
|---|---|---|---|---|---|---|
| one target, h 1 day, \|z\| > 1 (~30 % of days) | ~75 | ~130 | 0.26 | ~27 bp | 2 / sqrt(450) = 0.094 (~10 bp) | DEMO only in practice |
| one target, h 5 days non-overlapping, \|z\| > 1 | ~30 | ~50 | 0.42 | ~95 bp | 0.15 | DEMO only |
| one target, open-to-close next day, \|z\| > 1 | ~75 | ~130 | 0.26 (sd ~80 bp -> ~21 bp) | | 0.094 | DEMO only |
| 11-target book, h 1, \|z\| > 1, risk-scaled | ~830 trades, ~240 days | ~415 day-units | per-day book SR 0.147 (annualised 2.3); 0.08 per trade if independent | | per-day 0.067 | LIVE possible only at an annualised net Sharpe >= 2.3 |
| 4-index flow book (S3), h 1 | ~300 | ~520 trades / ~300 days | 0.17 per day-unit | | | LIVE only at annualised ~2.7 |
Literature-implied size at 1-5 days: ~0 (WYZ: abnormal short-term shorting flows do not predict post-2010; Evans et al.:
no relation for ETFs; BDR is monthly and cross-sectional). Expected per-trade SR 0-0.03 -> expected HOLD power < 0.5.
Prior: DEMO ~3 %, LIVE ~1 %. Tested because the data are free, daily, mechanical and never graded (round 35 O7
declared, not run).

## Common rules (all families)
- Signal day D = a FINRA file date (NYSE day). Entry clocks: **H1** D+1 13:00 UTC -> D+2 13:00 UTC; **H5** D+1 13:00 ->
  D+6 13:00 (5 NYSE days); **OC** D+1 NY 09:31 -> D+1 NY 15:55 (no overnight). Fill at the panel minute's mid +/- half
  its actual spread each leg (bar close of that minute; the bar starts after publication by >= 15 h), commission 0.6 bp
  round trip on FX / metals, swap for each rollover crossed. Variants: spread x1.5; +1 minute both legs; one extra day
  of signal lag. Non-overlapping per cell (a new trade only after the previous exits).
- z-scores: value on D against the 60 prior file days (mean, sd; >= 50 valid), never including D.
- Eras: IS 2016-21 (energies 2018-21), VAL 2022-24, PRE 2010-15 where a target exists (Dukascopy EURUSD, USDJPY,
  XAUUSD, XAGUSD bid; cost = IC 2016-17 median spread at the clock + 0.6 bp). HOLD closed.
- Day-clustered t (book cells cluster by entry day); >= 2/3 years net > 0 for LIVE; random-entry control 200 seeds
  (same count, same side mix, same hold, random eligible entry days of the era; and a second control with the side
  recomputed as -sign(z) at the random day, i.e. the unthresholded signal); multiple testing: best |t| vs a shared
  sign-flip-by-day null of all cells of the family (max |t| over the family per draw, 200 draws).
- Parameters (form, k) picked on IS per pair x horizon; VAL checks the pick only. Book cells are fixed (no pick).
- Big-move days: report with and without 2020-03/04.

## Family S1: ETF short-volume ratio -> the ETF's underlying (side: high SVR -> short)
Pairs (ETF -> IC target, target side when SVR is high): SPY -> US500 short, QQQ -> USTEC short, DIA -> US30 short,
IWM -> US2000 short, EWJ -> JP225 short, GLD -> XAUUSD short, SLV -> XAGUSD short, USO -> XTIUSD short, UNG -> XNGUSD
short, FXE -> EURUSD short, FXY -> USDJPY **long** (FXY is long yen).
Forms: **lvl** z(SVR_D); **ma5** z of the 5-day mean of SVR; **chg** z of SVR_D - SVR_{D-1}. Rule: z > k -> high-side
trade, z < -k -> the opposite. k in {1.0, 1.5}. Horizons H1, H5, OC.
Cells: 11 pairs x 3 forms x 2 k x 3 horizons = **198**, plus books (fixed form lvl, k 1.0, risk-scaled by the target's
trailing 60-day sd of 13:00 returns): all 11 pairs, the 4 US index pairs, the 4 commodity pairs; x H1 / H5 / OC = **9**.
S1 total 207.

## Family S2: aggregate short-volume ratio of index heavyweights / the whole tape -> US500, USTEC
- **S2-top10**: sum ShortVolume / sum TotalVolume over the S&P 500 top-10 by market cap at the start of each year
  (lists declared now from public knowledge, approximate; GOOG and GOOGL counted as two lines; FB -> META from
  2022-06-09; BRK/B as in the files):
  2010 XOM MSFT WMT AAPL JNJ PG IBM JPM GE CVX; 2011 XOM AAPL MSFT GE CVX IBM PG JNJ JPM WFC; 2012 XOM AAPL MSFT IBM CVX
  GE WMT PG JNJ GOOG; 2013 AAPL XOM GOOG WMT MSFT GE IBM CVX T JNJ; 2014 AAPL XOM GOOG MSFT GE JNJ CVX WFC BRK/B JPM;
  2015 AAPL XOM MSFT JNJ BRK/B WFC GE PG JPM CVX; 2016 AAPL GOOGL MSFT BRK/B XOM AMZN GE FB JNJ WFC; 2017 AAPL MSFT XOM
  JNJ BRK/B AMZN FB JPM GE GOOGL; 2018 AAPL MSFT AMZN FB BRK/B JNJ JPM XOM GOOGL GOOG; 2019 MSFT AAPL AMZN BRK/B JNJ JPM
  GOOG GOOGL FB XOM; 2020 AAPL MSFT AMZN FB BRK/B JPM GOOG GOOGL JNJ V; 2021 AAPL MSFT AMZN FB TSLA GOOGL GOOG BRK/B JNJ
  JPM; 2022 AAPL MSFT AMZN GOOGL TSLA GOOG NVDA FB/META BRK/B UNH; 2023 AAPL MSFT AMZN BRK/B GOOGL UNH GOOG JNJ XOM JPM;
  2024 AAPL MSFT AMZN NVDA GOOGL META GOOG BRK/B TSLA UNH.
- **S2-all**: sum over every symbol in the day's file (market-wide off-exchange short ratio).
- **S2-DLW** (side short on high): 2 aggregates x 2 targets (US500, USTEC) x forms {lvl, ma5} x k {1.0, 1.5} x {H1, H5,
  OC} = **48**.
- **S2-DIX** (side **long** on high; practitioner): 2 aggregates x 2 targets x form ma5 x k {1.0, 1.5} x H5 = **8**.

## Family S3: ETF primary-market flows (shares outstanding) -> underlying (side: inflow -> short, BDR reversal)
f_D = SO_D / SO_{D-1} - 1 on the issuer row dated D (missing -> no signal). Pairs: SPY + IVV (dollar flow: sum of
dSO x NAV over sum of AUM) -> US500; DIA -> US30; IWM -> US2000; EWJ -> JP225. Forms: **d** z(f_D); **c5** z of the
5-day sum. k {1.0, 1.5}; H1, H5, OC. Cells 4 x 2 x 2 x 3 = **48**, book (4 pairs, d, k 1.0, risk-scaled) x 3 horizons =
**3**. S3 total 51. Used from D+1 13:00 UTC (variant: +1 day).

Total declared: 207 + 56 + 51 = **314 cells**. Anything added later is declared below with its time before its numbers.

## Addendum 1, declared 2026-10-29 11:20 UTC (`date -u`): S3 results in, **no S1 / S2 / S4 return computed yet**
S3 was graded at 11:20 UTC (the FINRA pull is still running): best IS net t +1.82 (DIA -> US30, d, k 1.0, OC), VAL
-0.44; best |mid t| 2.06 vs a 48-cell sign-flip null p50 2.37 (p 0.78); flow book H1 IS t -1.19 / VAL -2.01. None.
The next family is a different mechanical by-product of the same AP / market-maker process and was written before any
FINRA series was joined to a price:

**S4: creation-delay buying (operational shorting is covered by creating later).** When a market maker sells ETF
shares short to meet buy demand (Evans et al.), it covers by creating units within the settlement window (T+1..T+3,
up to T+6 for bona fide market making), i.e. it must buy the basket in the following days. The excess of the ETF's
short-volume ratio over its own components' ratio isolates that operational part from economy-wide shorting. Side
fixed by this mechanism: **high spread -> long the underlying** (the opposite sign of S1, so S1 and S4 together are a
two-sided test of near-identical information; both count in the multiple-testing total, and S4 needs its own DEMO /
LIVE bar on the declared long side).
- Spread_D = SVR(ETF)_D - SVR(aggregate)_D; aggregate = top-10 list (S2) for SPY / QQQ / DIA, the all-tape ratio for
  IWM. Pairs SPY -> US500, QQQ -> USTEC, DIA -> US30, IWM -> US2000. Forms lvl (z of spread vs 60 prior days) and ma5;
  k {1.0, 1.5}; horizons H1, H5, OC. Cells 4 x 2 x 2 x 3 = **48**; book (4 pairs, lvl, k 1.0) x 3 = 3. S4 total 51.
Running total declared: 314 + 51 = 365 cells.

## Addendum 2, declared 2026-10-29 12:46 UTC (`date -u`): S1 / S2 / S4 IS-VAL graded, before any S5 number
Results so far (details in STREAM_S.md): S1 best IS net t +2.13 (DIA -> US30 lvl k1.5 OC, VAL -5.0 bp) vs a 198-cell
null p50 2.85; S1 books IS t -3.6 to -0.1, cost-driven; S2 best IS net t 0.95 (DIX side) vs null p50 2.18; S4
(creation-delay long) best IS t 0.43, book H5 IS t -3.77 (the wrong side: at mid, high ETF SVR is followed by slightly
lower index prices over 5 days, below cost). PRE (2010-15) of S1 waits for the pull.

**S5: operational shorting in US-listed country ETFs, covered in the next local session.** For a US ETF the market
maker can buy the basket in the same session, so any creation-delay pressure is diffuse (S4 null). For a country ETF
traded while its home market is closed, the market maker who sold ETF shares short in US hours can create (buy the
basket) only when the home market reopens; if part of the short is not hedged with futures overnight, the basket
purchase is a forced buy in the next local session. Side fixed by this mechanism: **high country-ETF short-volume
spread -> long the local index for the next local session** (open + 5 min -> close - 5 min, no overnight).
- Spread_D = SVR(ETF)_D - SVR(all tape)_D (FINRA file of US day D, public ~18:00 ET, before every next local open).
- Pairs: EWJ -> JP225 (Tokyo 09:05-14:55 JST), EWH -> HK50 (09:35-15:55 HKT), FXI -> HK50 (same clock), EWA ->
  AUS200 (10:05-15:55 Sydney), EWG -> DE40 (09:05-17:25 Frankfurt), EWU -> UK100 (08:05-16:25 London). Session = the
  first local weekday session starting after D 18:00 ET; a local holiday (no quote within 30 min) = no trade.
- Forms lvl, ma5; k {1.0, 1.5}: 6 x 2 x 2 = **24 cells**, plus a fixed book (6 pairs, lvl, k 1.0, risk-scaled) = 1.
  Costs: actual spread at both minutes; variants x1.5, +1 minute. IS 2016-21, VAL 2022-24 (no PRE: IC indices only).
- Power: daily, ~30 % of days per pair -> ~75 trades / yr / pair, book ~240 day-units / yr; LIVE needs an annualised
  book Sharpe >= ~2.3 net; prior ~1 % LIVE, ~3 % DEMO (the hedge-in-futures argument says the net pressure is ~0).
Running total declared: 365 + 25 = 390 cells.

## Addendum 3, declared 2026-10-29 12:48 UTC (`date -u`): S5 graded (none), before any S6 number
S5 results: best IS net t +2.08 (EWG -> DE40, ma5, k 1.5; random 0.97) but VAL -7.7 bp (t -1.01); best |mid t| 2.26 vs
a 24-cell null p50 2.07 (p 0.33); book IS t -1.02 / VAL -1.36. None.

**S6: Rule 201 short-sale circuit-breaker load (forced restriction on short sellers on D+1).** Rule 201 (effective
2011): when a stock falls >= 10 % from its prior close, short sales may not be executed at or below the national best
bid for the rest of that day and all of the next; orders priced above the bid may then be marked "short exempt"
(Rule 201(c)), as can the 201(d) exceptions. FINRA's ShortExemptVolume (in the files from 2011) summed over the tape and
divided by TotalVolume therefore measures how much short selling runs under the restriction. Mechanism and side: a
high exempt share on D means many names are restricted on D+1 (triggered on D), so aggressive short selling is
removed from them for D+1 -> **long** US2000 (small caps trigger most) and US500 on D+1. One-sided (low share = no
restriction = no trade).
- Signal: E_D = sum ShortExempt / sum Total (all symbols), z vs 60 prior days (lvl). k {1.0, 1.5, 2.0}; horizons H1,
  OC, H5; targets US2000, US500: **18 cells**. Same costs / variants / random control as S1.
- Confound fixed before looking: a high E_D follows down days, and index reversal after down days is a known effect.
  Control (reported next to each cell, not a cell): for each signal day the control draws a non-signal day of the same
  era in the same decile of the target's return over the 24 h before entry (13:00 D -> 13:00 D+1 for H1 / H5, 13:00 D
  -> D+1 open for OC), and takes the same long trade there; 200 draws. The mechanism needs net > 0 AND net above the matched control.
- Count: z > 1.5 ~ 7 % of days (~18 / yr), z > 1 ~ 15 % (~38 / yr): HOLD ~30-65 trades -> LIVE impossible (needs SR
  >= 0.37-0.55); DEMO is the ceiling. Prior DEMO ~3 %.
Running total declared: 390 + 18 = 408 cells.
