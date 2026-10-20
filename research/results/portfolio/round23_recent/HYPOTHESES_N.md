# Round 23, stream N: newest literature (2025-01 to 2026-10), hypotheses declared before any number

Written 2026-10-15 11:12 UTC (`date -u`; two wording fixes to N2/N5 exit bars at 11:14-11:15 UTC, same rules, still before
any number), before any return of any cell below was computed. Brief: [BRIEF.md](BRIEF.md)
row N and round13_structural/BRIEF.md. HOLD (2025-01-01 onwards) is never loaded. The only data looked at so far are
literature metadata and two holiday calendars (no prices).

## Step 1: search (log; details and raw files in scratchpad `r23/N/lit/`)

| route | what | count | files |
|---|---|---|---|
| Crossref, every record by ISSN, pub date 2025-01-01..2026-10-15 | JF, JFE, RFS, JFQA, RoF, JFutM, JIMF, JBF, J. Empirical Finance, FRL, J. Financial Markets, IRFA, JIFMIM, J. Commodity Markets, Energy Economics, Quantitative Finance, J. Financial Econometrics, FAJ, Pacific-Basin FJ, Global FJ, NAJEF, Resources Policy, Management Science, JPM, Economics Letters, IREF, EJF, J. Financial Research, Financial Review, Financial Management | 15,786 records (totals reconciled per journal) | `lit/cr/*.jsonl`, `lit/cr/log.txt` |
| Crossref, every record by DOI prefix, same dates | NBER (10.3386) 2,575; Fed Board FEDS/IFDP/notes (10.17016) 415; ECB (10.2866) 0 and Bank of Canada (10.34989) 0 (no 2025-26 records under these prefixes) | 2,990 | same |
| arXiv API, full listing by category x half-year, 2025-01-01..2026-10-15 | q-fin.TR, ST, PM, GN, RM, CP, MF, econ.GN (API totals reconciled, all < 2,000 per slice) | 6,939 | `lit/ax/*.json`, `lit/ax/log.txt` |
| Crossref keyword queries restricted to SSRN (10.2139), same dates | 36 queries (`lit/ssrn/queries.txt`), 60 rows each; SSRN's own site unreachable (no response), as in rounds 12 and 19 | 997 rows, 193 kept by the title filter | `lit/ssrn/hits.tsv`, `log.txt` |
| title/abstract filter (timing word x asset word) over all harvested records | `scripts/lit_filter.py` | 462 kept of 23,880 unique; read by hand | `lit/filtered.tsv` |
| abstracts | OpenAlex by DOI (Elsevier abstracts mostly withheld), Crossref SSRN records, NBER pages | ~45 | `lit/oa/abs.txt`, `lit/ssrn/abs_selected.txt` |
| web search (WebSearch / WebFetch) | 22 queries: FX time-of-day 2025, gold Shanghai/London 2026, overnight index 2025 NBER, BIS FX intraday 2025, JFE 2025 intraday flows, Tokyo fix 2025-26, 0DTE reversal, BTC ETF intraday, crude settlement 2025, FX month-end 2025, Harvey et al. rebalancing, FRL BTC intraday 2025, Fed WP auction FX, Ewald et al. full text, Valenti, BIS WP list, ECB WP 2025, BoJ WP 2025, gold fix 2025-26, pre-holiday 2025, Quantpedia gold holidays, Tolusic, CME BTC gap, Nikkei night session, natgas EIA; pages fetched: Quantpedia (BTC overnight, BTC pre-holiday, gold cultural holidays), NBER w35896 / w33423 / w33477, BIS papers page | - | listed in STREAM_N |

## Step 2: candidate map (every paper with an intraday-5-day effect on FX, metals, energy, indices or crypto)

"In K/T/TRIAGE" = mapped or tested in round12 STREAM_K, round19 STREAM_T, round22 TRIAGE_R. "Exhausted" = a family in
PROMPT.md. Sizes are as reported by the source (n/r = not reported in what was readable).

| # | source | mechanism, side, window | symbols | events/yr | reported size | OOS in source | status |
|---|---|---|---|---|---|---|---|
| 1 | Tolusic 2026, SSRN 7135159 / 7356684, "The First Hour: How FX Absorbs Its Daily Gap" | daily reopen auction: the first hourly bar after the daily break opens 4.8 pips from the prior close on average; **fade reopen gaps >= 1 pip, hold 1 hour**; edge monotone in gap size; holding to the daily close halves it; micro-gaps at other hours lose | six USD pairs | ~250 per pair | net profit factor 2.63 (>= 1 pip), 0 losing years 2019-26; pre-2019 "marginal" | partial (2019-26 strong, 2014-18 marginal) | **declared N1** |
| 2 | Valenti 2026, SSRN 6074846, "Intraday Price Asymmetry and Next-Day Intraday Returns in the S&P 500" | range asymmetry of the session around its open; **negative asymmetry -> stronger next-day open-to-close, positive -> weaker** (contrarian) | SPY | ~250 | "economically meaningful", short side in stress | n/r | **declared N2** (formula reconstructed from the abstract; flagged) |
| 3 | Vojtko & Dujava 2025, SSRN 5384405 (Quantpedia, 2025-08-05), "Cultural Calendars and the Gold Drift" | gift / wealth buying of gold around Christmas, Eid al-Fitr, Diwali, Lunar New Year: **long gold from close D-2 to close D+2** ("Global Holiday Drift") | GLD | 4 | Sharpe 0.71 (combined), Christmas best; no costs | none (2005-2025 in sample) | **declared N3** |
| 4 | Quantpedia 2025-09-08, "Surprisingly Profitable Pre-Holiday Drift Signal for Bitcoin" | pre-holiday drift (Ariel 1990) carried to BTC: **long close D-1 -> close D+1 around US holidays**; a 5/10/20-day-high filter is the "augmented" version | BITO / BTC futures 2018-25 | ~10 | Sharpe "over 0.6" (filtered) | none | **declared N4** (base rule only; the N-day-high filter is a breakout filter, excluded family) |
| 5 | Perreten 2026, SSRN 7600620, "When Does Overnight Price Discovery Occur?" | S&P 500 stocks: "dark" returns (after-market + night) positive, **pre-market negative and partially reversing the dark return**, more when pre-market liquidity is low | S&P 500 stocks (index-level implication) | ~250 | n/r | n/r | **declared N5** (index transfer of a stock-level result; flagged) |
| 6 | Ewald, Haugom, Ouyang, Smith-Meyer & Størdal 2025, Quant. Finance, doi 10.1080/14697688.2025.2535479 | Brent intraday seasonality, long/short at "particular times" with significant CAPM alphas after costs, 2010-21 | ICE Brent | 250 | significant alphas | n/r | **not declarable**: the times and sides are only in the full text (paywalled; SSRN 5037563 unreachable; Glasgow copy embargoed to 2027-02) -> needs the user (obtain the paper) |
| 7 | Zarattini, Aziz & Barbon 2024-25 (SPY noise-area intraday momentum); Paz 2026 SSRN 7290621 OOS | intraday breakout of a time-of-day noise band, follow | SPY | 250 | Sharpe 1.33 2007-24; **OOS May 2024-Mar 2026 Sharpe 0.39** (Paz) | failed (Paz) | dropped: breakout / intraday-momentum family (PROMPT: no Donchian/breakout; ITSM rounds 4, 12 K1/K3, 13 P, 17 Z) |
| 8 | Quantpedia 2025, SSRN 5021138, "How To Profitably Trade Bitcoin's Overnight Sessions?" | long BTC at the 16:00 ET close when at a 10-day high, overnight only | BTC | ~50-100 | 35 % OOS, no costs | split arbitrary | dropped: 10-day-high breakout on crypto = C1 family (PROMPT ban) |
| 9 | Harvey, Mazzoleni & Melone 2025 (NBER w33554); Ratnaike 2026 SSRN 7566720 (UK/Germany) | pension rebalancing sells equities after outperformance | US, DE40, UK100 | 12 | -16/-17 bp next day per sd | n/r | tested rounds 3-4 (stock-bond and MTD versions); stream P declares S2/S3 this round |
| 10 | Mourey, Shahrour & Şoiman 2025 FRL 108661; Song 2026 SSRN 7579278 | weekend/overnight BTC losses -> US equities down at the open | US indices | 52-250 | Song: 87-98 % of the response is in the opening gap, intraday not predictable | Song: none intraday | in T (#16) / tested r8 X6b; Song removes the executable part |
| 11 | Schmidt & Kraft 2026 FRL 110932 / SSRN 7384239 | BTC volume moved to the New York benchmark window after spot ETFs | BTC | 250 | volume only | - | in K (#26); 2024+ only -> needs the user |
| 12 | Mazur & Polyzos 2025 SSRN 5452994; Oefele 2025 EcLett; Yuan 2026 FRL; Fabus 2026; Lim 2026 (x2); Espel 2025; Lee & Lee 2026; Kim 2026 | spot BTC ETF flows and BTC intraday structure | BTC | 250 | flows follow price; most price change outside ETF hours | - | 2024+ (HOLD era) and flow data -> needs the user (stream P S10 maps the same) |
| 13 | Weiss et al. 2026 FRL; Hoang & Phan 2026 FRL "Bitcoin option expiration, gamma exposure, and intraday price reversals" | Deribit Friday expiry reversal | BTC | 52 | - | - | in K (#5), tested K4 |
| 14 | Shen, Li & Luo 2026 FRL 110300 | BTC option positions -> futures returns | BTC | - | n/a (no abstract) | - | needs Deribit OI history -> needs the user (as K) |
| 15 | Aalipour, Mehdian & Rezvanian 2026 SSRN 6776934 (FRL 2026) | crypto day-of-week effects are a few intraday intervals, asset-specific | BTC, ETH | - | n/r | - | not declarable: no side/hour in the abstract, full text unreachable |
| 16 | Algieri et al. 2025 NAJEF | crypto calendar anomalies "in some periods" | 8 coins | - | n/r | - | not declarable (no stated side); BTC Monday tested T5 |
| 17 | Elms 2026 SSRN 6564078 | SPX expiry: pinning gone, high ATM-OI days 16 % wider ranges | US500 | 250 | range only | - | no side; needs OI data |
| 18 | Kurth, Eisler, Rej & Bouchaud 2026 arXiv 2501.16772 | trends and reversion minutes to decades | futures | - | - | - | in K (#21) |
| 19 | Zhao 2026 SSRN 7229918 / arXiv 2608.03703 "Preying on Leveraged ETFs"; Pagano et al. 2025 SSRN 5371016 | LETF close rebalancing (Korea; stress days) | KOSPI; US | 250 | - | - | in K (#13); US big-day close tested r6, r13 P, r17 Z |
| 20 | Fleming, Liu & Nguyen 2026 (NY Fed SR 1188, SSRN 6447502); "The treasury auction risk premium" 2025 JBF | pre-auction yield rise, reversal after | Treasuries | ~250 | - | - | in K (#19); USD side tested TRIAGE R4 |
| 21 | Ko 2026 FRL; "Market anticipation and intraday trading: BOJ ETF purchases" 2025 FRL | BoJ afternoon ETF buying | JP225 | - | - | - | in T (#22) / TRIAGE R9 (programme ended 2024) |
| 22 | Ma, Bouri, Xu & Zhou 2025 GFJ | Chinese gold/silver night-session effect | SHFE | 250 | - | - | in K (#25) |
| 23 | Yang & Wang 2026 FRL 110073 | FOMC hour in crypto | BTC/ETH | 8 | volatility only | - | in T (#26) |
| 24 | He 2026 SSRN 7388124 | W-shaped dollar around fixes (Krohn et al. replication) | G9 | 250 | - | - | in T (#8), tested r3/r4/r10 E/r13 M |
| 25 | Seeck 2026 SSRN 7008318; Ladia 2026 SSRN 7124578 | FX ITSM; Dow opening-range reversal | - | - | - | - | in K (#3, #4) |
| 26 | Sizova, Syrstad & Sævareid 2025 SSRN 5143899 | currency-hedge rebalancing moves FX | NOK etc. | 12 | - | - | near-tested (round 12 month-end hedge at WM/R); NOK not at IC |
| 27 | Aldunate, Da, Larraín & Sialm 2025 JFE | Chilean pension fund flows and CLP | CLP | - | - | - | symbol not at IC |
| 28 | Andonov, Jansen & Rauh 2026 NBER w35896 | pension funds sell equities to meet negative cash flows | US equities | - | no timing | - | no timing / side on the index |
| 29 | Bartram, Grinblatt & Xu 2025 NBER w33423 | central-bank restrictiveness predicts currency returns | G10 | 12 | monthly | yes | horizon >= 1 month; needs money-supply data -> out of scope |
| 30 | Guo 2025 RFS "Earnings Extrapolation and Predictable Stock Market Returns"; Breckenfelder et al. 2026 SSRN 7370496 | monthly market predictability | US | 12 | - | - | horizon 1 month (and premia over weeks lose to financing, r9) |
| 31 | Zhang, Feng & Wei 2025 Quant. Finance | realized skewness of oil predicts FX | 9 currencies | - | n/r | - | not declarable: no side/horizon in the abstract |
| 32 | Guyot & Montgomery 2026 SSRN 6832400; Yang 2026 SSRN 7380619 | Japanese intervention days, intraday dynamics and reversal | USDJPY | < 2 | - | - | too rare (no power); unscheduled |
| 33 | Fanta 2025 IES WP 23/2025 | ECB communication outside meetings moves EURUSD within minutes | EURUSD | - | - | - | side depends on tone (no ex-ante side) |
| 34 | "Signal in the noise: Trump tweets and the currency market" 2025 JIMF; "When presidents make the news, do crude oil markets listen?" 2025 EnEc | tweet / news content | FX, oil | - | - | - | needs text data and a content classifier |
| 35 | arXiv 2511.06177 "Push-response anomalies in high-frequency S&P 500" | large negative pushes followed by positive responses at long tick lags | SPY | - | - | - | no fixed window (event time in ticks) |
| 36 | Yue, Li & Wu 2025 IRFA (INE crude weekdays); "Weekend information gaps" 2026 JFutM | weekday effects in Chinese crude; Monday decoupling | SC, oil | 52 | n/r | - | SC not at IC; WTI weekdays tested T6 |
| 37 | Ewald et al. (above) / Rotondi 2025 EnEc (natgas seasonality) | seasonal convenience yield (model) | gas | - | - | - | no intraday-5-day window |
| 38 | Morgan Stanley (Perzov) 2026 via FIA; Blose et al. 2018 | gold returns earned outside COMEX pit hours | XAU | 250 | +61 % vs -7 % (1 year) | - | practitioner; unconditional clock window = exhausted (r3, r13 M) |
| 39 | Hartzmark & Solomon (NBER w30688) | dividend-payment days | US | 50 | - | - | in K (#15); needs data |
| 40 | Wilkens 2026 SSRN 7066558 (European 0DTE); Hoang 2025 SSRN 5689945 (BTC options time of day); "Dealer-inventory frictions in SPX options: LETF rebalancing" 2026 FRL | option-market costs / pricing | options | - | - | - | no underlying side |

## Step 3: common definitions (all cells)

- Data: shared panel `r23/shared/panel` (mid = (bid close + ask close)/2 of the minute, spr = ask - bid at the minute's
  last tick; **label = bar start**, so the mid of bar t is the price at about t + 1 min). PRE: Dukascopy H1 XAUUSD
  2004-2015 only (N3). Nothing else from PRE: N1 depends on a venue's daily break (Dukascopy quotes through 17:00 New
  York and has no reopen auction), N2/N4/N5 have no index or crypto data before 2016.
- Clock: "time X" in a rule = the mid of the bar labelled X - 1 min (price at X). A **fill at X** = the mid and spread
  of the bar labelled X (the minute after X), i.e. signal on data up to X, fill one minute later. **+1 minute check**:
  every fill one bar later. **Spread x1.5 check**: half-spreads multiplied by 1.5. Missing bar at a fill: first bar
  with a quote within the next 30 minutes, else the trade is dropped (reported).
- Costs (bp of mid, per trade): half spread at entry + half spread at exit (actual panel spreads) + 0.6 bp commission
  for FX and metals (0 for indices and crypto) + swap for every 17:00 New York rollover crossed:
  `research.swing.rates.swap_frac_at(symbol, side, entry_ms)`, x3 on the symbol's triple day
  (`research.swing.swing.swap_frac(symbol)[2]`). PRE (N3 only): IC 2016-17 median XAU spread at that minute of day
  (New York clock) + 0.6 bp + the same swap model.
- Eras: PRE 2004-2015 (N3), IS 2016-2021, VAL 2022-2024. Era of a trade = its entry date.
- Statistics: mean bp per trade at mid and net; t clustered by UTC entry day (N3/N4: one trade per event, so plain t);
  per-year net; VAL/IS ratio; per-trade net Sharpe; **power = per-trade net Sharpe x sqrt(1.73 x trades/yr)** at the
  IS size and at the VAL size; spread x1.5 and +1 minute net. Outliers: also report net with trades clipped at the
  IS 0.5 / 99.5 % quantiles (information).
- Random-entry control (>= 200 seeds), per family below; report the percentile of the cell's net mean.
- Chance: per family, expected max |t| of K independent normals (K = cells) and, across the round, K = 10 primary +
  variant cells; for N1 also a sign-flip-per-day null shared by the six pairs (200 draws).
- Bars: LIVE / DEMO as in round 13's brief. Post-hoc findings are information only.
- Correlation with C3 (daily and monthly net, IS + VAL) for any cell that meets DEMO numbers.

## Step 4: declared cells (10 cells in 5 families)

### N1. FX daily-reopen gap fade (Tolusic 2026). 3 cells
- Symbols: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD (my reading of "six USD pairs"; NZDUSD not included). Pip
  = 0.0001, 0.01 for USDJPY. Results pooled over the six pairs (one cell per variant; per-pair rows are information).
- Days: every New York trading session start, Sunday-Thursday 17:00 New York (DST-aware via New York local time).
- Prior close P0 = mid at 17:00 NY (bar labelled 16:59 NY; if missing, the last bar with a quote in 16:30-16:59 NY).
  Reopen R = mid of the **first bar with a quote at or after 17:00 NY** (label t_r, within 17:00-17:30 NY; else no
  trade). Gap g = (R - P0) / pip. Event if |g| >= 1 pip. Side = -sign(g) (fade).
- **N1a (primary)**: entry fill at the bar t_r + 1 min (signal known at the close of bar t_r); exit fill at 18:00 NY
  (bar labelled 18:00 NY; one hour after the reopen, the paper's "single hour").
- **N1b**: same events and side; entry fill at 17:05 NY (bar labelled 17:05), exit at 18:00 NY. Declared because
  IC's spread is widest in the first minutes after the 17:00 NY rollover (round 12-13 pitfall); the paper's own
  costs are per-pair constant spreads.
- **N1c**: same as N1a but only |g| >= 2 pips (the paper's dose step).
- No swap (the trade is opened after the rollover). Information only: |g| >= 5 pips; exit at the next 17:00 NY
  ("holding to the daily close", which the paper says halves the edge); per-pair rows; by year.
- Random control: same pairs and days, a random hour boundary H in 18:00 NY .. 15:00 NY of the same session (uniform
  over whole hours), g_H = mid(bar H) - mid(bar H-2) in pips, event if |g_H| >= 1, side = -sign(g_H), entry H+1 min,
  exit H+60 min; the rule's own N1a cost model; 200 seeds. (The paper's own control: micro-gaps at other hours lose.)

### N2. Contrarian next-day session after intraday asymmetry (Valenti 2026). 2 cells
- Symbol: US500. Day d = NYSE trading day with a full session (early-close days 13:00 ET: session ends 13:00).
- O_d = mid at 09:30 ET (bar 09:29 ET); H_d, L_d = max / min of bar mids 09:30-15:59 ET (to 12:59 on early-close days).
  A_d = ((H_d - O_d) - (O_d - L_d)) / (H_d - L_d) in [-1, 1] (reconstructed from the abstract: "range-based measure from
  daily open, high and low ... relative to the opening level"; flagged as my reading).
- Trade on the next NYSE trading day d+1: entry fill at 09:30 ET (bar labelled 09:30), exit fill at 16:00 ET (bar
  labelled 16:00 ET, the general fill convention; on early-close days 13:00 ET). No rollover crossed.
- **N2a (primary)**: long if A_d < 0, short if A_d > 0 (A_d = 0: no trade).
- **N2b**: long only, when A_d < 0 (the abstract's main statement; short side "concentrated in stress").
- Random control: same number of trades on random NYSE days of the same era, same side mix (N2a) or all long (N2b),
  same 09:30-16:00 ET hold; 200 seeds.

### N3. Gold cultural-holiday drift (Vojtko & Dujava 2025). 2 cells
- Symbol: XAUUSD (IC panel 2016-24; PRE: Dukascopy H1 bid 2004-15). Festivals (`r23/shared/cal/cal_N.json`, python
  holidays 0.106): Christmas 25 Dec; Lunar New Year (CN Spring Festival day 1); Diwali (IN); Eid al-Fitr day 1 (ID).
- Trading days = NYSE trading days (the source used GLD on the American calendar). D-k = k-th NYSE trading day before
  the festival date; D+k = k-th NYSE trading day after it (the festival date is D0 if it is a trading day, else there is
  no D0).
- Entry: long at 16:00 ET of D-2 (fill bar labelled 16:00 ET; PRE: the open of the H1 bar starting 16:00 ET, i.e. the
  close of the 15:00 bar, bid + IC 2016-17 half spread). Exit: 16:00 ET of D+2. **5-day cap** (user's constraint): if
  D+2 16:00 ET is more than 5 x 24 h after entry, exit at 16:00 ET of the last NYSE trading day within 5 x 24 h.
  Overlapping windows of two festivals in one year are merged into one position (source: "Global Holiday Drift").
- Swap: XAU long per rollover, x3 on its triple day; commission 0.6 bp.
- **N3a (primary)**: all four festivals ("Global Holiday Drift"), ~4 trades/yr.
- **N3b**: Christmas only (the source's best festival in its own 2005-25 sample; so N3b is in the source's sample).
- Note: the source's sample 2005-2025 covers PRE, IS and VAL; this is a replication on another venue, not OOS.
- Random control: the same number of trades per year, long, entry at 16:00 ET of random NYSE days in the same years,
  same hold length distribution (D-2 -> D+2 trading days, same cap); 500 seeds.

### N4. Bitcoin around US market holidays (Quantpedia 2025, base pre-holiday drift). 1 cell
- Symbol: BTCUSD. Holidays: recurring NYSE holidays (`nyse_recurring`: New Year, MLK, Presidents, Good Friday,
  Memorial, Juneteenth from 2022, Independence, Labor, Thanksgiving, Christmas; special closures excluded).
- **N4a**: long at 16:00 ET of D-1 (last NYSE trading day before the holiday; fill bar labelled 16:00 ET), exit at
  16:00 ET of D+1 (first NYSE trading day after). Holds 2-4 days (<= 5). Swap: BTC long per rollover (IC 2026 fraction,
  x3 on its triple day). No commission.
- Information only: the same window with the source's 5-day-high filter is NOT run (breakout filter, excluded family).
- Random control: same count per year, long, random NYSE-day 16:00 ET entries with the same hold-length mix; 500 seeds.

### N5. US pre-market reversal of the "dark" return (Perreten 2026). 2 cells
- Symbol: US500. Day d = NYSE trading day. Dark return D_d = mid(04:00 ET of d) / mid(16:00 ET of the previous NYSE
  trading day) - 1. Pre-market window: entry fill 04:00 ET (bar labelled 04:00 ET), exit fill 09:30 ET (bar labelled
  09:30 ET, the general fill convention). No rollover crossed (IC's US500 break is
  17:00-18:00 ET).
- **N5a (primary)**: side = -sign(D_d) (pre-market partially reverses the dark return).
- **N5b**: short every day (pre-market returns negative on average).
- Index transfer of a stock-level result: the paper's returns are S&P 500 constituents' pre-market trades; the CFD
  follows E-mini futures, which trade through the night. Flagged; the side is still the paper's.
- Random control: same days, a random start time T (whole or half hour, 18:00-11:30 ET, outside 16:00-18:00 ET), hold
  5.5 h, N5a side = -sign(return over the 12 h before T), N5b short; 200 seeds.

### Cell count and chance
10 cells (N1 3, N2 2, N3 2, N4 1, N5 2). Expected max |t| of 10 independent normals ~2.0 (95th percentile ~2.8); per
family: K = 3 -> ~1.3 / 95 % ~2.4; K = 2 -> ~1.1 / ~2.2; K = 1 -> 0.8 / 1.96.

### Expected power before computing (a-priori, from the sources' sizes vs IC cost)
- N1: ~1,500 trades/yr pooled; cost at 17:00-18:00 NY is the issue (IC spreads at the rollover 1-5+ pips). If the net
  survived at, say, 0.5 bp with a 1-hour sd ~8 bp, per-trade Sharpe 0.06 x sqrt(1.73 x 1500) = 3.2 (LIVE-like); if not,
  nothing.
- N2: ~250/yr, session sd ~80 bp, cost ~1 bp; needs >= ~11 bp per trade for power 3; the source reports no size.
- N3: 4/yr: no LIVE power possible; DEMO at most (IS t >= 2 on ~24 events needs Sharpe ~0.4 per event).
- N4: ~10/yr: DEMO at most.
- N5: ~250/yr, 5.5 h sd ~40 bp, cost ~1-2 bp: needs ~5 bp per trade for power 3.

## Post-hoc additions (information only; cannot make a candidate)

Written 2026-10-15 11:18 UTC (`date -u`), after the N1-N5 results were seen. N3b (Christmas-only gold) came out with IS net
+81.8 bp (t 3.61, n 6), VAL +75.8 (t 2.20, n 3), PRE +103 (t 3.17, n 12); N3a (all four festivals) did not. Before
any draft, three diagnostics, declared here before running them:
- **H1 time placebo**: the N3b rule (long XAU 16:00 ET D-2 -> D+2, 5-day cap) around pseudo-festival dates 25 Nov,
  4 Dec, 11 Dec, 18 Dec, 1 Jan, 8 Jan, 15 Jan (each year), PRE / IS / VAL. If neighbouring weeks show the same drift,
  the effect is a December / turn-of-year seasonal, not a Christmas (gift-buying) one.
- **H2 dollar check**: the same Christmas window long EURUSD, long XAGUSD, long XPTUSD (IS/VAL; PRE EURUSD from
  Dukascopy H1 bid). Gold-specific demand predicts gold > silver/platinum and no EURUSD move; year-end dollar weakness
  predicts all of them up.
- **H3 C3 correlation** (daily and monthly net, IS + VAL) for N3b.
- N1 random-hour control and sign-flip null as declared (run after the main numbers; N1's net is far below zero).
