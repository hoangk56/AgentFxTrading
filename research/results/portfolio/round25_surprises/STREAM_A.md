# Round 25, stream A: what each pending user decision is worth

Written 2026-10-17 19:38-19:55 UTC (`date -u`). **No price data was fetched or loaded** (no IS, VAL, PRE or HOLD
series; the only repo data touched was a directory listing of research/data/USDCNH). Every number below is either
copied from earlier rounds (cited), taken from a public non-price source (logged with its time in
`r25/A/query_log.tsv` and the four helper logs `r25/A/web/{em1,em2,broker,lit}_log.tsv`), or arithmetic on those
(scripts in the scratch folder, listed at the end). Declared cells for the top routes are in
[HYPOTHESES_A.md](HYPOTHESES_A.md) (H-NOK 19:13, H-STK 19:18 + amendment 19:23, H-CNH 19:27, H-EMFIX 19:47 UTC), all
written before any of their data exists.

## Answer
- **No pending decision produces an expected LIVE candidate.** On the VAL-size arithmetic with the round-16/18 decay
  factors, no route reaches power 3 at x0.65 retention. The best full-size ceilings are:
  - the EM fix book: 3.5, but only if the Mexican and Singapore fixes move prices 1.5x more per unit of risk than
    the ECB and CNY fixes do; 2.0 if they move like them;
  - the single-stock blackout-selling flow: up to 2.6;
  - USDCNH at real spreads: 1.6.
  At x0.65 they fall to 1.4 (0.55), 1.6 and 0.5; at x0.30 to <= 0.6.
- **Ranked by the chance of a LIVE candidate:** (1) single-stock CFDs, employee selling after the earnings blackout
  (~3-5 %); (2) EM fix book led by USDMXN over the Banxico FIX window (~2 %); (3) Norges Bank's pre-announced EURNOK
  flow (~1 %); (4) a cheaper venue (~1 %); (5) USDCNH ticks (0 % LIVE, the cheapest DEMO test); (6) paid data (<= 1 %
  each); (7) FX crosses and (8) softs/grains (~0 %).
- **What the user should decide first:** say yes to the cheap FX data pulls (IC ticks via a cTrader backtest download
  on the VPS for USDCNH, USDMXN, USDSGD, EURNOK, USDNOK, EURSEK, plus Dukascopy M1 2004-15 for the same pairs): no
  money, hours of VPS time, three declared families tested on PRE/IS/VAL. Then decide whether a non-cTrader platform
  is acceptable (IC's share CFDs are MT5-only), because that decides whether the stock route, the only one with a
  published effect several times its cost and breadth, is worth a 1-2 day build on free data (Dukascopy US stock CFDs
  2017-24 + SEC EDGAR).
- **Surprises:**
  - IC's own spread table makes USDMXN cheaper per unit of risk than any other EM pair: 2.07 bp a round trip against
    a ~32 bp sd over the three-hour FIX window, cost/sd 0.064, below USDCNH's 0.08-0.09. So MXN, not the CEE pairs, is
    where a fix mechanism could pay; but the FIX turns out to be an average of three random snapshots over
    09:00-12:00 with no verified dealing convention, which lowers the prior.
  - The NBP, CNB and MNB rates are accounting rates (tax and balance sheets), not dealing fixes, and no study finds
    price pressure into them.
  - Norges Bank publishes the full monthly table of its daily NOK amounts since 2000. The sign flips between our
    eras (IS: it buys NOK every month; VAL: it sells NOK almost every month), a rare clean dose-response design.
  - The stock-level blackout result of Hartzmark & Solomon was dropped from the published AER 2025 version.
  - The US earnings announcement premium has been gone since 2004, so the most cited "breadth" anomaly is not
    available.

## Ranked table
Power = per-trade net Sharpe x sqrt(1.73 x trades a year), on the expected VAL size, then at x0.65 (declared-rule
retention, round 18) and x0.30 (median flow-anomaly retention, round 16 STREAM_X). Costs are round trips at IC.
"t_HOLD" for literature effects = paper t x sqrt(1.73 / sample years).

| # | route | mechanism and evidence | expected effect vs cost (bp) | events/yr | power full / x0.65 / x0.30 | chance of a LIVE candidate | data needed: source, symbols, years, size, time to fetch | first test |
|---|---|---|---|---|---|---|---|---|
| 1 | Single-stock CFDs: short high stock-compensation firms for 3 nights after the earnings blackout lifts (H-STK) | Employees may sell only after the blackout (lifted ~0.8 days after the announcement); Hartzmark & Solomon 2022 NBER WP 30688, Table XI: top 5 % by prior-quarter stock expense -87.5 bp over t+1..t+3 (t -5.77), -116.5 over t0..t+3 (t -5.50), 2002-20, all US firms; t_HOLD 1.74 gross for their whole universe; dropped from the AER 2025 version | 40-90 bp (IC names, unknown share of the paper's) vs ~9 bp (USD 0.02/share/side + spread + 3 nights' financing + USTEC hedge) | 50-150 in IC's universe (to be counted) | 0.6-2.6 / 0.3-1.6 / 0.1-0.6 (power 3 at x0.65 needs >= 530 events a year at 90 bp) | ~3-5 % (DEMO ~25 %) | Dukascopy US stock CFD M1 (~220 names from 2017-01..2018-02, 312 more from 2022; free; ~1 day with the repo's Dukascopy fetcher); SEC EDGAR XBRL share-based compensation + shares outstanding and 8-K item 2.02 timestamps (free bulk files, ~2 GB); IC's MT5 symbol list | STK-1 on IS 2017-21 / VAL 2022-24 with the declared costs, placebo STK-P |
| 2 | EM fix book: USDMXN over the Banxico FIX window (+ USDCNH CFETS close, USDSGD ABS VWAP) (H-EMFIX) | Round 19: dealing fixes move prices (ECB, CFETS, Tokyo), observation fixes don't. The FIX (mean of 3 random platform mids in 09:00-12:00 Mexico City) is the legal rate for USD obligations payable in Mexico and the settlement rate of Banxico's hedges and MXN NDFs/options; dealing "at FIX" not verified; no price-pressure study found | at E1's mid Sharpe (0.13): MXN ~4.2 bp over 3 h vs 2.07; CNH 1.68 vs ~0.9; SGD ~1.3 vs 1.23 | ~245 per leg | book 1.96 (E1-like) to 3.48 (1.5x E1) / 0.55-1.40 / 0 | ~2 % | IC ticks 2016-24 USDMXN, USDSGD (new symbols) and USDCNH via a cTrader backtest download on the VPS + `research/tools/pull_cache.sh` (hours per symbol, ~1-2 GB each); Dukascopy M1 USDMXN 2007-15, USDSGD 2004-15, USDCNH 2012-15 (free, ~1 h each); CNBV bank-holiday calendars | MX-1 on PRE 2007-15 (IC 2016-17 spread convention), then IS/VAL; the Mexican-holiday placebo, the WMR split and the 2-hour-gap clock test |
| 3 | Norges Bank's pre-announced daily EURNOK transactions (H-NOK) | Daily NOK amount announced at 10:00 Oslo on the last business day of the month, executed in EURNOK "spread throughout the day"; signed amounts 2016-24 -2.5 to +4.3 bn NOK/day (~0.5-2.4 % of EURNOK spot); only a 2018 master's thesis estimates an effect (mixed) | square-root impact model 0-3 bp/day vs 2.9-5.6 bp | ~225 | -0.3 (model) to 0.8 (2x model) / ~0 / 0 | ~1 % | Dukascopy M1 EURNOK, USDNOK, EURSEK 2004-15 (free); IC ticks 2016-24 (VPS); Norges Bank's monthly table (already saved, `web/nok/nb_fx_monthly.csv`) | NOK-D dose regression on PRE 2004-15 (sign flip 2013 -> 2015), then NOK-1 on IS/VAL |
| 4 | A cheaper venue for the existing effects | STREAM_X rows at named commissions (Fusion cTrader USD 2.25/side = 0.45 bp round trip, the lowest cTrader found; IBKR 0.20 bp/side) | J5c 1.53 vs 0.57-0.62; ECB slot 1.14 vs 0.42-0.47 | 50-254 | best at x1: J5c 3.35-3.54 (its HOLD already failed); at x0.65 none >= 3 (J5c 1.4-1.6, Friday ECB slot 1.25-1.33); at x0.30 <= 0.2 | ~1 % | the venue's own quotes at the rule minutes: a demo account for 1-3 months (no historical venue quotes are free) | measure Fusion/IBKR spreads at 10:00 Sydney, 12:45-13:00 London, 16:30 Beijing on demo |
| 5 | USDCNH bid/ask ticks for the CFETS 16:30 close (H-CNH) | Round 19 CNHC-I: +1.22 bp (t 4.57) IS, +1.68 (t 4.08) VAL at mid, absent on mainland holidays; only bid M1 exists locally | 1.22 / 1.68 vs 0.8-1.02 | ~237 | 1.2-1.6 / 0.1-0.5 / 0 (LIVE cost at VAL size +0.04 bp: impossible) | 0 % LIVE; DEMO ~15 % (needs <= ~0.6 pip spread at 06:30 and 08:30 UTC) | IC USDCNH ticks 2016-24 (VPS cache via a backtest download; hours; existing symbol) | CNHC-I unchanged at real spreads |
| 6 | Paid data | Deribit OI (Tardis USD 350-3,000/month, Laevitas 50-500) for the K4 BTC Friday fade; CLS hourly flows (price unpublished; USD 1,250/month quoted in 2016; intraday product 10-30 min after the hour from 2017-10); SGE premium (WGC Goldhub, free); LETF AUM (ProShares CSVs, free); S&P 500 dividend payment days (Hartzmark & Solomon AER 2025) | K4 11 bp vs 3.3; SGE dip 1.4 vs 1.0; dividend days +7 bp vs ~2.5 | 25-52 | K4 <= 2.9 / ~1.7 / ~0.5 if half the Fridays carry 2x; SGE <= 2.1 at a venue, < 0 at IC; dividend days t_HOLD 0.58 gross; LETF count-capped (<= 1.9) | <= 1 % each | as listed; none is a price series from IC | none recommended |
| 7 | FX crosses (EURGBP, EURCHF, EURJPY, AUDJPY ...) | The declared flows (ECB fix, Sydney 10:00, Tokyo fix) sit on one USD leg; the cross dilutes them | EURGBP +1.04 / +0.32 vs 0.91; EURCHF +0.78 / +0.89 vs 1.16; EURJPY +0.92 / +1.01 vs 0.88 | 254 | < 0.5 / < 0.3 / 0 | ~0 % | not recommended | - |
| 8 | Softs / grains (IC futures CFDs) | USDA reports move volatility, not direction (WASDE straddles lose 3-7 % on release days); the Goldman-roll front-run decayed (no profit after costs 2004-10); the corn weather premium is one event a year | no directional effect vs 10-25 bp (IC: USD 0 commission, published spreads 0.03-4.6 price units) | 12-30 | ~0 | ~0 % | Dukascopy softs from 2017 (no corn or wheat) | - |
| - | Other EM pairs: PLN, CZK, HUF (accounting fixes), ZAR, TRY, HKD | NBP 11:00, CNB 14:15, MNB 11:00 are tax/accounting rates with no price-pressure evidence; ZAR has no local dealing fix (WMR 16:00 London); TRY managed with large swaps; HKD pegged | cost/sd 0.15-0.54 (vs 0.064 for MXN over its 3-hour FIX window) | 240 | ~0 | ~0 % | not recommended | - |

## 1. EM FX with official or binding fixes
### 1.1 Cost per unit of risk at IC
IC's published average Raw spreads (snippets of icmarkets.com/global and icmarkets.eu spread pages, undated,
retrieved 2026-10-17; pips by inference) converted at assumed 2016-24 price levels, + 0.6 bp commission; the two-hour
sd from an assumed annual vol with the 2-hour share calibrated on the two measured legs (E1 15.1 bp, CNHC 11.1 bp)
(`em_costs.py`, `em_costs_out.md`):

| pair | IC avg spread (pips) | round trip (bp) | assumed vol | 2h sd (bp) | cost/sd | mid Sharpe needed for power 3 alone |
|---|---|---|---|---|---|---|
| EURUSD (E1, measured) | 0.02-0.06 | 0.62 | 7 % | 15.1 | 0.041 | 0.19 (E1 has 0.13) |
| USDCNH (measured sd) | 2.93 | 1.02 | 4.5 % | 11.1 | 0.092 | 0.24 (CNHC has 0.15) |
| **USDMXN** | 28.57 | 2.07 | 12 % | 26.5 (3 h FIX window: 32.5) | **0.078 (0.064)** | 0.23 (0.21 over 3 h) |
| USDSGD | 0.85 | 1.23 | 4.5 % | 9.9 | 0.123 | 0.27 |
| USDCZK | 5.21 | 2.92 | 9 % | 19.8 | 0.147 | 0.29 |
| USDHUF | 9.48 | 3.56 | 11 % | 24.3 | 0.147 | 0.29 |
| USDTRY | 50.61 | 6.93 | 20 % | 44.1 | 0.157 | 0.30 |
| USDSEK | 30.31 | 3.79 | 10 % | 22.0 | 0.172 | 0.32 |
| USDNOK | 36.79 | 4.47 | 11.5 % | 25.4 | 0.176 | 0.32 |
| USDZAR | 79.85 | 5.92 | 15 % | 33.1 | 0.179 | 0.32 |
| USDPLN | 15.79 (EU page 10.46) | 4.65 (3.28) | 10 % | 22.0 | 0.211 | 0.36 |
| EURNOK | 52.89 (EU page 24.40) | 5.64 (2.92) | 8.5 % | 18.7 | 0.301 (0.156) | 0.45 |
| EURSEK | 44.07 (16.53) | 4.76 (2.16) | 6.5 % | 14.3 | 0.332 (0.151) | 0.48 |
| EURPLN | 21.2 (16.38) | 5.42 (4.32) | 5.5 % | 12.1 | 0.447 | 0.59 |
| USDHKD | 0.89 | 0.71 | 0.6 % | 1.3 | 0.54 | 0.69 |

The measured binding-fix legs have a mid Sharpe of 0.12-0.15 per trade (E1 0.12 IS / 0.13 VAL; CNHC 0.12 / 0.15).
At that size only USDMXN and USDCNH net anything (power ~1.1 and 0.8-1.2); every other EM pair needs a fix effect
2-5x the largest measured one just to cover its cost. EURHUF and EURCZK were not found in IC's tables.

### 1.2 The fixes: who must transact at them (helper passes em1 and em2; sources in their logs)
| currency | fix (local time) and history | binding? | price-pressure evidence | flows (BIS April 2022 unless stated) | known-side official flows | Dukascopy from |
|---|---|---|---|---|---|---|
| **MXN** | Banxico FIX: mean of 3 platform mids at random instants in 09:00-09:59, 10:00-10:59, 11:00-12:00 Mexico City (Circular 3/2012 arts 164-173; 1996 rules before, bank polling); published from 12:00, DOF next day; Mexico dropped DST 2022-10-30 | legal conversion rate for USD obligations payable in Mexico (Ley Monetaria art 8); settles Banxico's FX hedges (NDFs, from 2017) and ISDA MXP01-04 NDFs/options; dealing "at FIX" not verified | none found for the window; FSB 2014: WMR 16:00 volume spike >= 10x in MXN | spot 47.8 bn, USDMXN 42.7 bn; dealers in Mexico 16.5 %; 2019: strictly onshore 7 bn of 113 | Banxico USD auctions at published sizes/times 2003-16 (e.g. USD 52-200 m a day without minimum price, 2015-03-11..2015-11-20; minimum-price FIX + 1-2 %); hedge programme USD 20 bn from 2017, maturities settle at FIX | 2007-03-13 |
| SGD | ABS SGD VWAP 10:30-11:00 SGT, published 11:30 (ISDA source SGD3 from 2013-08-06; the earlier method was not found) | ISDA settlement source SGD3; dealing at the fix not verified | none found | spot 56.3 bn, USDSGD 50.0 bn; dealers in Singapore 54.7 % | MAS manages the S$NEER band (not pre-announced) | 2004-11-16 |
| CNY/CNH | CFETS 16:30 Beijing close (round 19) | onshore corporates square before the close; it enters the next day's central parity | round 19: +1.22 / +1.68 bp at mid, absent on mainland holidays | CNY spot 175 bn | - | 2012-06-27 |
| HKD | TMA USD/HKD Spot Rate 11:00 HKT: volume-weighted median of broker trades >= USD 1 m in 10:45-11:15 (from 2016-08-01; submissions before) | dealing fix ("so dealers can hedge when they need to deliver at the fix") | none found | spot 45.0 bn | HKMA convertibility undertaking at 7.75 / 7.85 (e.g. 85 strong-side triggers in 2020, HK$383.5 bn) | 2007-03-13 |
| PLN | NBP Table A, EUR/PLN "for 11:00" Warsaw (dealer poll 10:55-11:00, trimmed mean, until 2022); published 11:45-12:15 | tax and accounting (PIT art 11a, CIT art 15a); GPW USD/PLN futures (USD 1,000) settle on it | none found | spot 15.5 bn, EURPLN 7.9 bn | Ministry of Finance EUR sales, mostly off-market via NBP (2024: EUR 30.2 bn, 84 % at NBP); market leg never pre-announced | 2007-03-13 |
| CZK | CNB fixing reflects trading at 14:15, declared ~14:30 Prague (since 2002) | accounting, tax, customs only | none found | total 29 bn | floor at 27/EUR 2013-11-07..2017-04-06 (EUR 75 bn bought); 2022 FX sales (~EUR 30 bn est.) | 2016-01-03 |
| HUF | MNB official rate 11:00, trimmed mean of 10 banks | VAT (optional); two one-off MNB tenders at the official rate (EUR 7.83 bn 2014-11; CHF 0.9 bn 2015-08) | none found | spot 7.7 bn | energy-importer EUR sales 2022 (off market) | 2007-03-13 |
| ZAR | no local dealing fix found; the WMR 16:00 London fix is the convention | WMR dealing by convention (index trackers) | WMR-wide studies only (G10) | spot 22.3 bn | none found | 2003-08-03 |
| TRY | CBRT indicative rates (from interbank hourly averages; the 15:30 time not verified) | accounting / observation | none found | spot 12.2 bn (2019: 24 bn) | CBRT selling auctions 2013-16, sales to state energy firms, TL-settled forwards 2017-22 | 2007-03-13 |
| NOK | Norges Bank reference rates ~14:15-16:00 CET are indicative; the relevant flow is Norges Bank's own daily EURNOK execution (H-NOK) | Norges Bank must convert the government's petroleum cash flow: a mandated flow, not a fix | KMW 2024: NOK -3.51 %/yr (t -2.2) in 08:00-14:15 CET and -5.08 % (t -3.8) after, 1999-2019 | spot 35.7 bn, EURNOK 17.3 bn | daily amounts announced monthly since 2000 (2016-24: -2.5 to +4.3 bn NOK a day) | 2004-10-25 (EURNOK), 2003-08-04 (USDNOK) |
| SEK | Riksbank reference rates are indicative; the ECB fix matters (KMW: SEK -7.73 %/yr, t -4.9, 08:00-14:15 CET) | - | KMW 2024 | spot 41.0 bn | Riksbank USD 8 bn + EUR 2 bn sales 2023-09-25..2024-01-26, pace varied, weekly figures with a 2-week lag (one programme) | 2004-10-27 (EURSEK) |

**Reading.** Only three currencies have a fix with a plausible dealing role AND a cost per unit of risk near the
measured binding fixes: CNH (measured, at cost), MXN (lowest cost/sd of any EM pair at IC, but no verified dealing
convention) and SGD (settlement source, cost/sd 0.12). The CEE fixes are accounting rates (round 19's "observation"
class); HKD is pegged (cost/sd 0.54); ZAR and TRY have no local dealing fix and cost/sd 0.16-0.18. The book of the
three candidate legs is declared as H-EMFIX; its expected power is 1.96 at full size if each fix moves prices like
E1 per unit of risk, 3.48 if EM fixes move 1.5x as much, 0.55 / 1.40 at x0.65 (`emfix_book.py`).

## 2. FX crosses at IC: what the declared mechanisms add
A cross's move in a window is the sum of its two USD legs, so a declared flow on one leg (E1 = EUR into the ECB fix;
J5c = AUD into 10:00 Sydney; gotobi = JPY at the Tokyo fix, C3's) reaches the cross diluted by the other leg's own
window move. IC's crosses cost 0.9-1.4 bp round trip (published average spreads: EURGBP 0.27, EURCHF 0.61, EURAUD
0.80, EURCAD 0.74, EURNZD 1.32, AUDJPY 0.50, CADJPY 0.48, CHFJPY 0.86, NZDJPY 0.60, AUDNZD 0.77, AUDCAD 0.68 pips)
against 0.6-0.8 bp for EURUSD, AUDUSD and USDJPY. From numbers already in the repo (`cross_arith.py`):

| cross cell | IS mid | VAL mid | IC round trip | net IS / VAL |
|---|---|---|---|---|
| EURGBP short 11-13 London (E1 minus the GBPUSD leg, round 22 R11) | +1.04 | +0.32 | 0.91 | +0.13 / -0.59 |
| EURCHF short 11-13 London (E1 minus the USDCHF long leg, F7) | +0.78 | +0.89 | 1.16 | -0.38 / -0.27 |
| EURJPY short 11-13 London (measured, F11) | +0.92 | +1.01 | 0.88 | +0.04 / +0.13 |
| AUDJPY short 09:45-10:00 Sydney (J5c's AUD leg, JPY leg taken as 0) | +1.54 | +1.53 | 1.23 | +0.31 / +0.30 |

- The ECB-fix flow is partly a USD flow (F3: E1 is 1.5x larger on USD-strength days; Krohn, Mueller & Whelan 2024:
  the dollar rises before every major fix), so EUR crosses keep less of it than EURUSD.
- The Sydney leg on AUD crosses also meets IC's post-rollover spreads in the northern winter (round 12 J).
- JPY crosses at the Tokyo fix would be more of C3 (excluded: the user wants a different mechanism, and they would
  correlate with C3).
- Round 19 found no home-fix effect for CAD, AUD, NZD, GBP or CHF, so CAD/NZD/CHF crosses have no declared mechanism.
- Krohn, Mueller & Whelan (2024, JF 79:541-578; 1999-2019, 08:00-14:15 CET) also have SEK weakening into the ECB fix
  (-7.73 %/yr, t -4.9, i.e. ~3.1 bp a day vs USD): t_HOLD 1.41 gross, but IC's USDSEK round trip is ~3.8 bp, so net
  < 0; EUR and SEK fall together, so EURSEK carries ~nothing.

**Value: none for LIVE (power < 0.5 on every cell, < 0.3 at x0.65); a cross symbol pull is not recommended.**

## 3. Single-stock CFDs
**IC facts** (broker helper pass): IC's spec sheets say "Stock CFDs are available exclusively on MetaTrader 5"
(cdn.ic.com/uploads/FSA/Stocks-Product-Specification-Sheet.pdf, Last-Modified 2026-09-01; IC EU sheet 2022-08-19);
"over 700" (FSA sheet) to ~2,100 (EU sheet, BrokerChooser 2026-05) shares on NASDAQ, NYSE, ASX, Xetra, Euronext,
LSE, SIX, HK...; commission USD 0.02 per share per side in the US (1.3 bp per side at USD 150), 0.10 % per side in
AU/EU/UK, 0.15 % in HK; financing benchmark +/- 3 % a year; dividends credited to longs, debited to shorts; no
statement on history depth (MT5 keeps little M1). **Data without IC:** Dukascopy has 546 US stock CFDs, ~220 of them
with ticks/M1 from 2017-01..2018-02 and 312 only from 2022; German from 2015, French 2016, UK 2015-17, HK 2018, Japan
2018 (dukascopy-node instrument metadata). SEC EDGAR gives share-based compensation, shares outstanding and the
8-K item 2.02 acceptance time of each earnings release for free.

**Structural flows with breadth** (literature helper pass + my reading of Hartzmark & Solomon 2022, Table XI;
t_HOLD = paper t x sqrt(1.73 / years), gross, for the paper's own universe):

| family | side, window | effect (paper) | sample | status after ~2010 | events/yr | t_HOLD gross / verdict |
|---|---|---|---|---|---|---|
| **Blackout selling (HS 2022 WP)** | short top 5 % stock expense, t+1..t+3 | -87.5 bp (t -5.77); t0..t+3 -116.5 (t -5.50) | 2002-20, all US firms | in sample to 2020; not in the AER 2025 version | ~800 all US (top 5 %), 50-150 in IC's list | **1.74**; the only family with effect >> cost |
| Earnings announcement premium | long announcers, week | VW 32.6 bp/week (t 3.5) 1994-2003 | 1974-2016 | **gone after 2004** (VW 8.7 bp, t 0.97; "The Disappearing Earnings Announcement Premium", WP) | ~2,000 | dead in the US; UK/AU alive but mostly small caps; IC charges 0.10 %/side there |
| Dividend month premium (Hartzmark & Solomon 2013) | long predicted payers, run-up before ex-day | 36-53 bp/month (EW) | 1927-2011 | not found; large caps not verified | ~1,600 | the hold is a month (> 5-day limit); a 5-day pre-ex slice nets ~0 at x0.65 |
| End-of-day reversal (BDS 2025 WP) | fade the day, last 30 min | largest quintile 3.41 bp/day (t 10.6) | 1993-2019 | yes (WP) | 252 | 2.68 gross, but two trades a name a day cost >= 3 bp: net < 0 |
| Closing-auction deviation (BM 2023) | fade into next open | large caps 2.7 bp vs half-spread 1.5 | 2010-18 | yes | 252 | below cost |
| S&P 500 additions (Greenwood & Sammon) | long adds | +7.6 % 1990s -> +0.8 % (n.s.) 2010s | 1980-2020 | disappeared | 14-28 | dead |
| Russell reconstitution | long adds | temporary 5.4 % 1996-2001 | to 2018 | no reliable effect after 2008 | 1 day | dead (one cluster a year) |
| Option-expiration week (S&P 100) | long option-active names | ~45 vs ~12 bp other weeks | 1996-2008 | not found | 12 | count-capped |
| Market dividend-payment days (AER 2025) | long US500 on top-quarter payment days | +7.1 bp (t 4.27) | 1926-2018 | published | ~60 | 0.58: dead for LIVE |
| Overnight premium | long close -> open | top 1 % ~2.6 bp a night | 1993-2013 | beta, not alpha | 252 | below financing + spread |

**H-STK power** (`stk_power.py`; hedged 3-day sd ~500 bp and ~9 bp cost are assumptions): power 0.6-2.6 at full
size for 40-90 bp and 50-150 events a year; 0.3-1.6 at x0.65; 0.1-0.6 at x0.30. Power 3 at x0.65 would need >= 530
top-5 % events a year at 90 bp (4,500 at 40 bp), several times what IC's list can hold. **Verdict: the best route
in this stream, but a DEMO-tier expectation; LIVE only if IC's larger names carry the paper's full effect, there
are >= ~150 events a year, and it does not decay.** Cautions: the result is not in the published AER version; the
paper's sample includes small caps; IC trades shares only on MT5 (a new engine) unless another broker offers share
CFDs on cTrader (not verified here).

## 4. Softs and grains at IC
- IC lists eight softs (wheat, corn, soybean, coffee, sugar, cotton, orange juice, cocoa) as futures-based CFDs that
  expire 2 working days before the underlying and are **not rolled** (the client reopens in the next contract);
  USD 0 commission on Raw; published spreads cocoa 4.608, coffee 0.300, corn 0.680, cotton 0.150, OJ 1.120, soybean
  1.350, sugar 0.033, wheat 0.750 (price units; six of eight have min = avg, perhaps placeholders), i.e. roughly
  10-25 bp a round trip at 2016-24 price levels (my conversion); IC Commodity sheet Last-Modified 2026-05-05.
  cTrader availability per symbol not confirmed.
- Dukascopy: cocoa, cotton, OJ from 2017-10, sugar (white, London) 2017-10, soybean 2017-12, coffee 2017-12; no corn
  or wheat. So no PRE era and an IS of 2018-21 at best.
- Literature: report days (WASDE, Crop Progress, Grain Stocks, Acreage) move volatility, not a predictable direction;
  the option evidence is that volatility sellers earn on WASDE days (long straddles lose 3-7 %), which IC's
  instruments cannot trade; the GSCI-roll front-run (Mou 2011, Sharpe up to 4.4 in 2000-10) decayed and needs two
  contract months; the corn weather premium is one trade a year; no study of settlement-time pressure.
- **Value: none.** No directional, frequent, declared effect exists to test; count and cost cap anything seasonal.

## 5. A cheaper venue
Published FX commissions per side (broker helper pass; USD per 100k unless stated): IC cTrader 3.00 (0.30 bp);
Pepperstone cTrader 3.00 (active-trader rebate 1-3 per lot); FP Markets 3.00; BlackBull 3.00; Tickmill 3.00; FxPro
3.50; Eightcap 3.50; TopFX 2.75; Tradeview 2.50 (account type unclear); **Fusion Markets 2.25 (0.225 bp), the lowest
cTrader commission found**; Interactive Brokers 0.20 bp of value up to USD 1 bn a month (USD 2 minimum per order),
0.08 bp only above USD 5 bn; Dukascopy USD 18-35 per million by deposit/volume tier (side basis not confirmed);
LMAX Global 2.5-4.5 per 100k by volume; CME 6E/6A one tick (0.5 pip) + ~USD 1.60 exchange fee per side.

STREAM_X's inputs (VAL mid, sd, trades a year, IC VAL cost) recomputed with these commissions and IC's spreads
kept (`venue_power.py`; it reproduces STREAM_X's (a), (b) and (d) columns exactly). Power at x1 / x0.65 / x0.30:

| row | IC | Fusion-like 0.45 RT | IBKR-like 0.40 RT | no commission | institutional (d) | LIVE cost x1 / x0.65 |
|---|---|---|---|---|---|---|
| F1 E1 | 1.87 / 0.92 / -0.04 | 2.08 / 1.13 / 0.17 | 2.15 / 1.19 / 0.24 | 2.71 / 1.75 / 0.79 | 2.46 / 1.50 / 0.54 | -0.19 / -0.88 |
| F3 E1 on USD-TOP days | 1.82 / 1.02 / 0.22 | 1.93 / 1.13 / 0.33 | 1.97 / 1.17 / 0.37 | 2.27 / 1.47 / 0.67 | 2.13 / 1.33 / 0.54 | -0.96 / -2.02 |
| F4 ECB pre-fix slot | 1.60 / 0.37 / -0.85 | 2.06 / 0.83 / -0.39 | 2.21 / 0.99 / -0.24 | 3.44 / 2.21 / 0.99 | 2.89 / 1.66 / 0.44 | +0.16 / -0.24 |
| F5 Friday ECB slot | 2.10 / 1.01 / -0.09 | 2.34 / 1.25 / 0.15 | 2.42 / 1.33 / 0.23 | 3.06 / 1.97 / 0.87 | 2.81 / 1.71 / 0.62 | +0.08 / -0.60 |
| F19 Sydney pre-leg | -4.86 / -7.51 / -10.15 | -4.09 / -6.74 / -9.39 | -3.83 / -6.48 / -9.13 | -1.79 / -4.44 / -7.09 | 5.52 / 2.87 / 0.22 | +0.89 / +0.38 |
| F20 J5c (HOLD failed) | 2.80 / 0.83 / -1.15 | 3.35 / 1.38 / -0.59 | 3.54 / 1.56 / -0.41 | 5.01 / 3.04 / 1.07 | 4.53 / 2.56 / 0.59 | +0.72 / +0.18 |
| F21 Sydney post-leg | -0.92 / -2.52 / -4.12 | -0.44 / -2.05 / -3.65 | -0.29 / -1.89 / -3.49 | 0.98 / -0.62 / -2.22 | 3.30 / 1.70 / 0.10 | +0.50 / -0.01 |
| CNHC CNY close | 1.20 / 0.13 / -0.94 | 1.48 / 0.40 / -0.67 | 1.57 / 0.50 / -0.58 | 2.30 / 1.23 / 0.15 | 1.97 / 0.90 / -0.18 | +0.04 / -0.55 |
| M5 gold big days | 1.30 / 0.62 / -0.05 | 1.39 / 0.71 / 0.04 | 1.42 / 0.74 / 0.07 | 1.67 / 0.99 / 0.31 | 1.56 / 0.89 / 0.21 | -1.74 / -2.84 |
| I3 US30 post-close fade | 2.26 / 1.14 / 0.02 | same (no commission on indices) | same | same | 2.29 / 1.17 / 0.05 | +0.07 / -0.30 |

- At x1 a retail venue lifts only J5c to 3.35-3.54, and J5c's HOLD has already failed (net -0.25 bp at IC).
- At x0.65 no row reaches 3 at any named venue; only J5c with no commission at all (3.04). At x0.30 nothing exceeds
  1.1 even at zero commission.
- The Sydney legs need a venue whose 10:00 Sydney spread does not carry the 17:00 New York rollover widening; every
  retail cTrader broker has the same rollover, and round 24 B found the V only from ~2011.
- **Value: low.** Moving to Fusion saves 0.15 bp a round trip (~USD 1.5 per lot traded) and changes no verdict; for
  C3 itself it is a small cost saving (~70 lots a month at 1 % risk per round 9), not a research decision.

## 6. Paid data named in earlier rounds
| dataset | provider, price | coverage, lag | what it would test | expected power | value |
|---|---|---|---|---|---|
| Deribit options OI / greeks | Tardis.dev `options_chain`: USD 350 (academic) / 700 / 1,000 / 3,000 a month, minimum order 300, free CSV of the 1st of each month; Laevitas Premium USD 50 a month (1 year CSV), Enterprise 500 (API history, "5+ years") | Deribit from 2019-03-30, tick level | K4 (C2) BTC fade on Deribit-expiry Fridays, conditioned on the paper's own variable (high ATM OI) | STREAM_X: <= 2.9 if half the Fridays carry 2x the edge, ~2.1 at 1.5x; x0.65 ~1.2-1.7; the 2019-21 IS cost still fails the IS gate | low-medium |
| CME OI | DataMine (price not found; site unreachable); Databento USD 199-4,500 a month; CFTC COT free weekly | COT futures from 1986, options from 1995 | option-OI pinning, futures positioning | COT already tested (rounds 4, 9: nothing) | low |
| Leveraged-ETF AUM | ProShares data downloads (free CSV; shares-outstanding field unconfirmed), NEXT FUNDS 1570 (free); Direxion 403 | daily | L4 gold big days and the index LETF close sized by L(L-1) x AUM x r | count-capped: ~1.9 at most (STREAM_X) | low |
| CLS FX volume and flows | CLS Market Data (price unpublished; USD 1,250 a month quoted for Quandl's hourly set in 2016) | spot volume from 2011-10-31, flows from 2012-09-03, hourly-updated flows from 2017-10-27, 5-minute from 2022-07-10; EOD product next business day, intraday 10-30 min after the hour; flows split market makers vs price takers, funds / corporates / non-bank financials vs banks | direct evidence on who trades into E1 / CNY / MXN fixes; a delayed-flow signal | as a signal: information is priced within ~1 minute (round 8), so a 10-30 minute lag is likely useless; as evidence: mechanism checks only | low for LIVE, medium as evidence |
| SGE premium | World Gold Council Goldhub "local gold price premium/discount" (xlsx, free login status not stated) | China daily from 2003, updated weekly | the SGE auction move on high-premium mornings (M1/M2) | STREAM_X: ~2.1 at a 0.6 bp venue, < 0 at IC | low (free, but no LIVE path at IC) |
| S&P 500 dividend payment days | from a dividend calendar (vendor) or EDGAR | daily | the AER 2025 market price pressure | t_HOLD 0.58 gross (1926-2018 t 4.27) | none |
| Single-stock data for H-STK | not needed to be paid: Dukascopy (free) + SEC EDGAR (free); a paid daily US set (e.g. Databento equities, other vendors) only for a PRE era or the all-firm percentile | 2017-24 free | H-STK | as section 3 | (route 1) |

## What I recommend the user decides first and why
1. **First, yes to the free FX pulls** (no money; hours of VPS time; no new account):
   - IC ticks 2016-24 for USDCNH (existing symbol, only bid M1 locally), USDMXN, USDSGD, EURNOK, USDNOK and EURSEK
     (placebo): one cTrader backtest per symbol over 2016-24 on the VPS fills the backtest cache (memory note: ticks
     exist from 2014-16 for FX; a cold cache can time out, a rerun works), then `research/tools/pull_cache.sh <SYM>`;
   - Dukascopy M1 for USDMXN (from 2007-03), USDSGD (2004-11), EURNOK (2004-10), USDNOK (2003-08), EURSEK (2004-10)
     for the PRE era, with the repo's existing fetcher;
   - this tests three declared families at once (H-EMFIX, H-CNH, H-NOK), each with a mechanism check that does not
     depend on the side (Mexican bank holidays without a FIX, the 2-hour New York gap after 2022 and the WMR split
     for MXN; mainland holidays for CNH; Norges Bank's sign flip and dose for NOK). Combined chance of a LIVE
     candidate ~3 %, of a DEMO candidate ~25 %. It is the cheapest decision on the table and the only one that can
     be run this week.
2. **Second, decide whether a non-cTrader engine is acceptable** (IC's share CFDs are MT5-only). If yes, the stock
   route H-STK can be tested on free data (Dukascopy US stock CFDs 2017-24 + SEC EDGAR) in ~1-2 days of building; it
   is the only route where a published effect is 5-10x the cost and the events number in the hundreds, so it has the
   best single chance of a LIVE candidate (~3-5 %), but its expected tier is DEMO, the paper's result is unpublished
   in print, and a live version needs MT5 bots (or another broker) and several bots for the 3-position limit.
3. **Not recommended:** pulling crosses, other EM pairs (PLN, CZK, HUF, ZAR, TRY, HKD), softs; paid data (Deribit OI,
   CLS, CME); switching venue for research reasons. None has a path to power 3 even before decay.

Why this order: the binding constraint since round 10 is cost, not the absence of effects. The FX pulls test the
two places where cost per unit of risk is lowest outside the majors (USDMXN 0.064 over its 3-hour FIX window,
USDCNH 0.08-0.09) and a flow with a
published size (Norges Bank); the stock route escapes cost by breadth and effect size but needs an engine decision
first. Nothing here changes the conclusion of STREAM_X: no data decision alone lifts a known effect to LIVE.

## Needs the user
- **IC tick pulls (VPS)**: USDCNH (existing symbol), USDMXN, USDSGD, EURNOK, USDNOK, EURSEK for 2016-24 (one backtest
  download each; ~1-2 GB per symbol; hours). Optional placebo legs: USDPLN / EURPLN (NBP 11:00 Warsaw), USDCZK (CNB
  14:15 Prague) as "observation fix" controls for H-EMFIX.
- **Dukascopy M1 2004-15** for the same pairs (free; the user already chose Dukascopy for the post-2026-09-24 data).
- **Stock route**: (a) OK to build a stock engine for research (Dukascopy US stock CFDs + SEC EDGAR bulk files,
  ~1-2 days, no money); (b) if it passes, the platform: IC MT5, or a cTrader broker with share CFDs (to verify).
- **Not recommended unless the user wants evidence only**: Tardis/Laevitas Deribit OI (USD 50-350 a month minimum),
  CLS flows (price on request), WGC SGE premium (free) for M1/M2 at a venue.
- **Data after 2026-09-24** (already chosen): the clean forward slice for any of the above that passes IS/VAL.

## Untested ideas
- **Norwegian petroleum-tax instalment dates** (oil companies buy NOK to pay; Norges Bank's 2023-06-02 piece):
  six instalments a year to 2024 (1 Aug, 1 Oct, 1 Dec, 1 Feb, 1 Apr, 1 Jun; ten from 2025; skatteetaten.no), NOK
  strength in the 3 days before each; sizes from Statistics Norway's monthly tax accounts. 6 events a year:
  DEMO at most (power <= ~1.3 even at a 30 bp effect).
- **Banxico's rule-based USD auctions** (2014-12-09..2016-02-17: USD 200 m a day with a minimum price of FIX + 1.5 %,
  USD 52 m then larger no-minimum auctions at 10:00 Mexico City; 2008-13 minimum-price auctions): a gotobi-like daily
  flow with a published side and size, but only in PRE (Dukascopy USDMXN from 2007-03); mechanism evidence only.
- **Banxico FX-hedge maturities** (programme from 2017-03-06, NDFs settled in MXN against the FIX): hedging flows at
  the FIX on maturity days; ~12-24 dates a year; count-capped.
- **IPO lockup expiries** in IC's US list (Field & Hanka 2001, JF: roughly -1 to -3 % around expiry; from memory,
  not fetched this round): 10-40 events a year in IC's large names; DEMO at most.
- **RSU vesting sell-to-cover** (vesting dates cluster on fixed calendar days for many tech firms): dates are not
  public in a machine-readable form.
- **Single-stock leveraged ETFs** (e.g. TSLL, NVDL, launched 2022-23 per my memory, not fetched; rebalance at the
  close): the round-12 L4 mechanism
  at stock level, but almost all of its life is in HOLD (2025-26): needs a new-era rule, which the user has not
  re-allowed.
- **NOKSEK** (IC 7.53 pips; Dukascopy only from 2024-05): Norges Bank trades EURNOK, so NOKSEK would isolate the NOK
  leg from EUR; too little history.
- **WMR 16:00 London into-fix USD rise for EM pairs** (Krohn, Mueller & Whelan 2024 find ~2.5 bp before each major
  fix in G10): at EM cost/sd of 0.15-0.45 it would need several times the G10 size.

## Mechanism notes the next round can use
- Dealing fix vs observation rate, by currency (helper passes): dealing = ECB (in practice, despite the ECB's
  "strongly discouraged"), CFETS 16:30, Tokyo TTM, WMR 16:00 (orders by 15:45 filled at the benchmark), TMA USD/HKD
  (window set so dealers can hedge deliveries at the fix); legal / settlement rate, dealing not verified = Banxico
  FIX (USD obligations payable in Mexico, NDF and option settlement, Banxico's hedges), ABS SGD VWAP (ISDA SGD3);
  observation / accounting = NBP Table A (tax; GPW USD/PLN futures of USD 1,000 settle on it), CNB 14:15
  (accounting, customs), MNB 11:00 (VAT option; two one-off tenders executed at it), CBRT indicative rates, RBA,
  SNB, BoE, Bank of Canada (round 19).
- BIS Triennial April 2022 spot turnover (USD bn a day): MXN 47.8 (USDMXN 42.7), SGD 56.3 (USDSGD 50.0), NOK 35.7
  (EURNOK 17.3, USDNOK 14.9), SEK 41.0, ZAR 22.3, PLN 15.5 (EURPLN 7.9), TRY 12.2, HUF 7.7, HKD 45.0
  (`web/bis/bis2022_table25_2.txt`, annex tables 2.x and 4.2).

## Sources
Every call, with its `date -u` time, is in the logs (my own: `query_log.tsv`, 60+ lines; helper passes:
`web/em1_log.tsv`, `web/em2_log.tsv`, `web/broker_log.tsv`, `web/lit_log.tsv`, ~520 lines). The shared web-search
budget of the session (200 searches) ran out at ~19:17 UTC and OpenAlex's free daily budget for this IP at ~19:11
UTC; after that only direct fetches (curl to central banks, BIS, NBER, Crossref, GitHub, IC's CDN) were used.
- Norges Bank: [FX transactions table 2000-2026](https://www.norges-bank.no/en/topics/statistics/foreign-exchange-transactions-daily/)
  (19:04:47), [FAQ](https://www.norges-bank.no/en/topics/liquidity-and-markets/faq-exchange-transactions/),
  [mechanism page](https://www.norges-bank.no/en/topics/liquidity-and-markets/Foreign-exchange-purchases-for-GPFG/),
  press releases [2019-02-28](https://www.norges-bank.no/en/news-events/news/Press-releases/2019/2019-02-28-press-release/),
  [2023-02-28](https://www.norges-bank.no/en/news-events/news/Press-releases/2023/2023-02-28-fx/),
  [2024-02-29](https://www.norges-bank.no/en/news-events/news/Press-releases/2024/2024-02-29-fx/),
  [2025-02-28](https://www.norges-bank.no/en/news-events/news/Press-releases/2025/2025-02-28-fx/),
  [Langeland 2023-06-02](https://www.norges-bank.no/en/news-events/news/Articles-and-opinion-pieces/2023-05-23-sales-of-nok/);
  Løberg (2018), UiS master's thesis, [hdl 11250/2563496](http://hdl.handle.net/11250/2563496) (abstract via search
  snippet); [Skatteetaten instalment tax](https://www.skatteetaten.no/en/press/nyhetsrommet/instalment-tax-2024/).
- Riksbank: [2023 reserve hedging](https://www.riksbank.se/en-gb/markets/the-gold-and-foreign-currency-reserve/currency-hedging--sales-of-dollars-and-euros/);
  [2021 self-financed reserve](https://www.riksbank.se/en-gb/press-and-published/notices-and-press-releases/press-releases/2021/the-riksbank-begins-transition-to-a-fully-self-financed-foreign-exchange-reserve/).
- BIS Triennial 2022 annex tables: https://www.bis.org/publications/commentary-otc-derivatives/statistics-rpfx22-fx-annex.pdf (19:10:52).
- Hartzmark & Solomon (2022), Predictable Price Pressure, NBER WP 30688, https://www.nber.org/system/files/working_papers/w30688/w30688.pdf
  (19:16:18); published as Market-Wide Predictable Price Pressure, AER 115(9) 3171-3213, doi 10.1257/aer.20231725
  (Crossref, 19:36:18).
- Krohn, Mueller & Whelan (2024), JF 79:541-578, doi 10.1111/jofi.13306; Evans (2018), JBF 87:233-247, doi
  10.1016/j.jbankfin.2017.09.017; Melvin & Prins (2015), JFM 22:50-72; FSB (2014) FX benchmarks final report,
  https://www.fsb.org/wp-content/uploads/r_140930.pdf; ECB reference-rate framework,
  https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf.
- Banxico (helper em1): FIX footnotes https://www.banxico.org.mx/tipcamb/tipCamMIAction.do?idioma=sp; Circular
  3/2012 (copy at https://www.abm.org.mx/legislacion-y-regulacion/juridico/banxico/circulares/2012/Circular_3_2012.pdf);
  Comisión de Cambios announcements (2013-04-08, 2014-12-09, 2016-02-17 PDFs on banxico.org.mx); FpML settlement-rate
  options https://www.fpml.org/coding-scheme/settlement-rate-option; BIS WP 429 (García-Verdú & Zerecero 2013).
- NBP / CNB / MNB (helper em2): NBP Resolution 51/2002 as amended (infor.pl consolidated text); GPW USD/PLN futures
  standard; CNB fixing pages (cnb.cz); MNB "fixing and publication of the official exchange rates" (mnb.hu).
- IC Markets (helper broker): spread tables icmarkets.com/global/en/trading-pricing/spreads and
  icmarkets.eu/en/trading-pricing/spreads-and-swaps (search snippets, undated); spec sheets
  https://cdn.ic.com/uploads/FSA/Stocks-Product-Specification-Sheet.pdf, https://cdn.icmarkets.eu/uploads/EU/Stocks-Specification-Sheet.pdf,
  https://cdn.icmarkets.com/uploads/Commodity+Specification+Sheet.pdf; other brokers' commission pages (fusionmarkets.com,
  pepperstone.com, fxpro.com, interactivebrokers.ie spot-currency commissions, dukascopy.com Tariffs.pdf).
- Dukascopy start dates: dukascopy-node `instrument-meta-data.json` (GitHub, generated 2026-07-13; the 2026-03-09
  commit e6822288de where the newer file has 2000-01-01 placeholders).
- Literature (helper lit): "The Disappearing Earnings Announcement Premium" (WP, iimb.ac.in ARC2020); Frazzini &
  Lamont NBER w13090; Savor & Wilson 2016 JF; Barber, De George, Lehavy & Trueman 2013 JFE; Hartzmark & Solomon 2013
  JFE; Greenwood & Sammon JF (doi 10.1111/jofi.13410); Bogousslavsky & Muravyev 2023 FM; Baltussen, Da & Soebhag
  (end-of-day reversal WP); Ni, Pearson & Poteshman 2005 JFE; Lou, Polk & Skouras 2019 JFE; Mou (2011); Adjemian
  (2012) AJAE; Tardis.dev pricing; CLS Market Data brochure; WGC Goldhub.

## Process and disclosures
- Four read-only helper passes (EM fixes MXN/ZAR/TRY/SGD/HKD; CEE + WMR + ECB; broker costs and Dukascopy dates;
  literature and paid data) ran in parallel from 19:01 UTC under the same rules (no price series, no 2025-26 levels,
  no repo edits, every call logged with its time). Three official pages they fetched embedded exchange-rate tables
  (Banxico's FIX page, a CBRT auction-results PDF, a CNB page with a 2026 rate table): the helpers discarded or
  deleted the tables and recorded no level or return; no price was used anywhere in this stream.
- Spreads come from undated snippets of IC's own spread pages (IC's site does not load from this machine), pip
  conventions and 2016-24 price levels are my assumptions, and every vol and sd for a symbol outside the panel is an
  assumption (labelled). The first test of each route replaces them with measured values.
- Nothing was committed; no git command was run; no repo code was run or edited.

## Files
Scratch folder `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/A/`:
- `query_log.tsv` (my web calls with times), `web/*_log.tsv` (helper passes), `web/nok/nb_fx_monthly.csv`
  (Norges Bank's monthly table, parsed by `parse_nb.py`), `web/bis/` (BIS 2022 annex), `web/stk/w30688.pdf`.
- `venue_power.py` -> `venue_power_out.md` (route 5), `em_costs.py` -> `em_costs_out.md` (route 1 costs),
  `fixleg_power.py` (per-leg needs), `emfix_book.py` -> `emfix_book_out.txt` (H-EMFIX book), `route_table2.py` ->
  `route_table2_out.md` (route powers), `notes_em2.md` / `notes_lit.md` (helper facts used), `stk_power.py` ->
  `stk_power_out.md`, `lit_tscale.py` (t_HOLD of literature effects), `cross_arith.py` -> `cross_arith_out.md`,
  `mx_dst.py` (Mexico City vs New York clock gaps 2004-24).
- Only `research/.venv/bin/python -I` and `python3 -I` were run, on these scripts; no repo code was run or edited,
  no git command was used, no price file was opened.
