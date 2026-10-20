# Round 25, stream A: hypotheses for routes that need the user's decision (written before any of their data exists)

Started 2026-10-17 18:54:38 UTC (from `date -u`). Stream A fetches NO price data. Every hypothesis below is written
before any price series for its symbols has been fetched or seen in this project; where an existing panel symbol is
involved, that is said explicitly. Times of every web query and fetch are logged in the scratch file
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/A/query_log.tsv`
(and `.../r25/A/web/<helper>_log.tsv` for the four read-only helper passes); a condensed copy is at the end of this file.

Every block carries the `date -u` time at which it was written. Blocks are only appended; later corrections are marked
"amendment" with their own time.

## Common conventions for every declared cell (19:13 UTC)
- Eras: PRE 2004-2015 (Dukascopy, where it has the symbol), IS 2016-2021 (parameters, here none: every parameter is
  fixed below), VAL 2022-2024. HOLD 2025-01-01..2026-09 stays closed; data after 2026-09-24 is the clean forward
  slice. Any download is cut at load to the era being tested.
- Prices: mid = (bid + ask) / 2 at the quote; executable: buy at the ask, sell at the bid, at the actual entry and
  exit minutes (M1 bar-start labels: the price "at 10:00" is the close of the bar labelled 09:59). Fills one minute
  after the signal minute; stress: both fills +1 minute and spread x1.5.
- Costs: IC's actual spread at the minutes + 0.6 bp round-trip commission for FX (USD 3 per 100k per side, IC's
  cTrader page); swap per 17:00 New York rollover when a hold crosses it. For PRE: IC's 2016-17 spread of the same
  symbol by minute of week (local fix clock) + 0.6 bp, because Dukascopy's early asks are unreliable.
- Statistics: day-clustered t; random-entry control with >= 200 seeds (same days, same hold, window start shifted
  by a random -180..+180 min within the same local session, side recomputed from the rule at the random time);
  years net > 0; power = per-trade net Sharpe x sqrt(1.73 x trades per year) and the same on day clusters.
- Decay: report every cell at its VAL size and at 0.65 x VAL mid (declared-rule retention, round 18) and 0.30 x VAL
  mid (median flow-anomaly retention, round 16 STREAM_X).
- Bars: the user's LIVE and DEMO bars of research/PROMPT.md, unchanged. No RELAXED tier.

## H-NOK: Norges Bank's pre-announced daily NOK transactions in EURNOK (19:13 UTC)
**State of knowledge when written.** No EURNOK, USDNOK, EURSEK or NOKSEK price series has ever been loaded in this
project (they are not in research/data); I have seen no intraday or daily return of these pairs. The non-price inputs
were fetched today: Norges Bank's monthly table of announced daily amounts 2000-2026
(https://www.norges-bank.no/en/topics/statistics/foreign-exchange-transactions-daily/, fetched 19:04:47 UTC, saved as
`r25/A/web/nok/nb_fx_monthly.csv`), the press releases of 2019-02-28, 2023-02-28, 2024-02-29 and 2025-02-28, the FAQ
(https://www.norges-bank.no/en/topics/liquidity-and-markets/faq-exchange-transactions/) and the 2023-06-02 opinion
piece by Gaute Langeland. BIS Triennial 2022 (annex tables, fetched 19:10 UTC) for turnover.

**Mechanism (from the sources, not from data).**
- Norges Bank converts the government's petroleum cash flow. "At 10 am on the last business day of the month, Norges
  Bank announces the amount to be converted on each day of the following month." "The Bank purchases or sells NOK
  for EUR, since this is the most liquid currency cross for the Norwegian krone. To minimise the impact of these
  transactions on the market, transactions are spread throughout the day ... with Norwegian and international
  banks." No transactions "at the end of December". (FAQ, published 2025-02-14.)
- Signed amount A_m (NOK million per day; + = Norges Bank buys foreign exchange = sells NOK = buys EURNOK; - = buys
  NOK). Table means: 2004-13 +96..+700 (sells NOK), 2014 ~0, 2015-21 -592..-1,508 (buys NOK), 2022 +1,804, 2023
  +1,367, 2024 +367. Range 2016-24: -2,500 (2020-07) to +4,300 (2022-10). From 2025-03 a second, fixed component
  (NOK purchases to fund the dividend transfer) is netted in; it does not exist in 2016-24 (the 2019, 2023 and 2024
  releases list only the government amount).
- Size: NOK 1 bn a day is about EUR 95 m, i.e. ~0.55 % of EURNOK spot turnover (BIS April 2022: EURNOK spot USD
  17.3 bn a day, USDNOK 14.9 bn, NOK all pairs 35.7 bn); the 2022-10 peak (NOK 4.3 bn) ~2.4 %; NOK non-financial
  customer spot is only USD 2.1 bn a day, so the flow is large relative to the customer flow dealers internalise.
- Why it might escape the round-3..24 limits: it is a flow with a published side AND size every day (gotobi-like),
  whose sign flips between eras (IS: Norges Bank buys NOK every month; VAL: sells NOK almost every month; PRE: sells
  NOK 2004-13). A dose-response across 108 monthly amounts separates it from any constant home-hours effect
  (Ranaldo 2009 predicts NOK weakens in Oslo hours whatever Norges Bank does). Why it might not: the flow is
  announced a month ahead, so dealers can pre-position, and it is executed as a TWAP, the least price-moving way.
  Norges Bank itself: "In the short run, we cannot exclude the possibility that our transactions may have some
  influence on the NOK exchange rate" (2023-06-02). Only a 2018 University of Stavanger master's thesis (Løberg,
  hdl 11250/2563496, abstract via search snippet: mixed, a short-term effect in one model) estimates it.

**Declared cells (no parameter is chosen on data).**
| cell | symbol | side (source) | window (local, DST via tz Europe/Oslo) | day set | sizing | role |
|---|---|---|---|---|---|---|
| NOK-1 | EURNOK | sign(A_m): long EURNOK when A_m > 0, short when A_m < 0 (Norges Bank's own trade direction) | 09:00 -> 16:00 Oslo | Norwegian bank business days of months with \|A_m\| >= 100, excluding 20-31 Dec | lot = default x clip(\|A_m\| / 1000, 0.5, 2) | primary |
| NOK-2 | USDNOK | same sign as NOK-1 (NOK leg) | 09:00 -> 16:00 Oslo | same | same | secondary (same flow through EURUSD arbitrage; not counted as independent) |
| NOK-P | EURSEK | sign(A_m) as NOK-1 | 09:00 -> 16:00 Stockholm (= Oslo) | same days | same | placebo: expected 0 |
| NOK-D | EURNOK | regression of the 09:00-16:00 mid return (bp) on A_m (NOK bn/day) with a constant; slope > 0 predicted | as NOK-1 | all Norwegian business days 2004-24 incl. zero-amount months | n/a | mechanism (information) |
| NOK-A | EURNOK | sign(A_{m+1} - A_m) at the 10:00 Oslo announcement on the last business day, 10:00 -> 10:15 | announcement days | n/a | information only (12 a year, priced within minutes per rounds 8 and 10) |

- Mid-month changes (months marked "*" in Norges Bank's table: 2003-05, 2008-10, 2020-03, 2020-11, 2021-11) take
  the dated amounts from the corresponding press releases (to be fetched before the test; non-price).
- Cell count for the multiple-testing benchmark: 2 trading cells (NOK-1 counted, NOK-2 reported as its replica) +
  3 information cells.
- Holiday placebo: Norwegian bank holidays on which EURNOK still trades (Maundy Thursday, Whit Monday, 17 May
  when a weekday): NOK-1's window on those days, signed by A_m, predicted ~0 (no Norges Bank execution).
- Expected events per year: ~225 (business days minus 20-31 Dec and zero months) in IS and VAL; PRE 2004-13 ~150
  (several zero months).
- Expected size (from a square-root impact model, not from data): impact ~ 0.5 x sigma_day x sqrt(Q / V) = 0.5 x
  ~62 bp x sqrt(0.0055) ~ 2.3 bp per NOK 1 bn a day, less whatever dealers pre-position after the announcement; so
  0-3 bp per trade at mid, against a 09:00-16:00 EURNOK sd of roughly 45 bp (a guess: ~62 bp daily, ~55 % of the
  variance in Oslo hours) and IC's cost (EURNOK spread unknown here, see STREAM_A; 2-4 bp + 0.6 bp is the working
  range). Power at mid with 2.3 bp: 2.3 / 45 x sqrt(1.73 x 225) = 1.0; net of a 3 bp cost: < 0. **LIVE is out of
  reach unless the flow moves EURNOK by >= ~9 bp a day net of cost; DEMO needs IS net t >= 2.0, i.e. ~5 bp net.**
- Data needed: EURNOK, USDNOK, EURSEK M1 bid/ask 2016-24 from IC (cache pull; new symbols) and Dukascopy M1
  2004-15 (free); the dated mid-month press releases; Norwegian bank holidays (python-holidays NO). No price is
  fetched in this round.

## H-STK: employee selling after the earnings blackout window, single-stock CFDs (19:18 UTC)
**State of knowledge when written.** No single-stock price, return, earnings date or compensation figure has ever
been loaded in this project; I have not looked at any. The only input is the paper, read today from the NBER PDF
(https://www.nber.org/system/files/working_papers/w30688/w30688.pdf, fetched 19:16:18 UTC): Hartzmark & Solomon
(2022), "Predictable Price Pressure", NBER WP 30688 (doi 10.3386/w30688; SSRN 4288522), section G and Table XI.

**Mechanism (paper).** Employees paid in stock may trade only in open windows; the blackout is lifted on average
0.8 calendar days after the earnings announcement (Jagolinzer, Larcker & Taylor 2011, quoted in the paper; 78 % of
firms had explicit blackout periods per Bettis, Coles & Lemmon 2000). Diversification motives make employees sell
as soon as the window opens, a predictable, uninformed selling flow whose size scales with stock compensation /
market cap. The side (short) and the window come from the paper, which uses stale (prior-quarter) stock expense to
rule out an information story. Paper numbers (US, 2002-2020, ~300,000 announcements; characteristic-adjusted
returns vs zero-expense firms; SE clustered by date and firm), Table XI Panel A:
| prior-quarter stock expense / market cap | t0..t+3 | t+1..t+3 (controls for the t0 return) | t+4..t+10 |
|---|---|---|---|
| > 0 to 80th pct | -18.4 bp (t -3.69) | -0.2 (-0.05) | -1.1 (-0.27) |
| 80-90th | -33.2 (-2.93) | -10.1 (-1.36) | +23.8 (2.70) |
| 90-95th | -77.4 (-4.83) | -23.6 (-2.04) | +15.2 (1.19) |
| 95-100th | -116.5 (-5.50) | -87.5 (-5.77) | +45.5 (2.06) |

**Why it might escape the limits.** It is the only flow found in this round with breadth (hundreds of events a
year, spread over ~60-80 announcement days), a fixed side, a mechanism tied to corporate policy (insider-trading
blackouts) rather than to a clock that has been scanned, and an effect (tens of bp) far above a share CFD's round-trip
cost (~5-12 bp). Why it might not: the paper's universe is all US firms (small caps carry much of the top 5 %), IC
lists only larger names; it was published in 2022 (VAL 2022-24 is partly post-publication); its whole-sample t of
5.8 over 19 years is only ~1.7 at the 1.73-year holdout size even before costs (t x sqrt(1.73 / 19)).

**Declared cells (nothing chosen on data).**
| cell | rule | role |
|---|---|---|
| STK-1 | short each IC-listed US stock whose lagged stock expense is >= the 95th percentile, from the last quote before the 16:00 ET close of t0 to the last quote before the 16:00 ET close of t+3 (3 nights); hedge: long USTEC CFD of equal notional over the same interval | primary |
| STK-1u | STK-1 without the hedge | report only |
| STK-2 | as STK-1 for the 90th-95th percentile | secondary |
| STK-3 | short >= 95th percentile from the last quote before the close of t0-1 to the close of t+3 (includes the announcement jump) | secondary |
| STK-R | long the >= 95th-percentile names from the close of t+3 to the close of t+10 (reversal, paper +45.5 bp) | information (hold 7 trading days breaks the 5-day limit: report only) |
| STK-P | placebo: the same firms and weekday, 30 trading days before t0 (no window opening), same 3-night hold | expected ~0 |

- Definitions (as the paper): t0 = the first trading day the announcement can affect prices (before the open or in
  session -> that day; after the close -> next trading day), from the announcement timestamp. Lagged stock expense =
  annual share-based compensation reported with the PREVIOUS quarter's results (XBRL tag ShareBasedCompensation,
  trailing four quarters) / market capitalisation at the close of t0-1. Percentiles are computed each calendar
  quarter across ALL US-listed firms announcing that quarter (zero-expense firms included), then only IC-listed
  names are traded.
- Sizing: equal notional per event; a bot holds <= 3 positions, so several bots (one per sector or per letter range).
- Costs: IC share-CFD commission per share and side, the actual spread at both quotes, short financing over 3
  nights by IC's formula, dividend adjustments if an ex-date falls inside the hold; USTEC leg at its spread.
- Eras: IS 2016-2021, VAL 2022-2024; PRE 2004-2015 only if a paid US daily dataset is bought (the paper's own 2002-15
  span overlaps it, so PRE would not be independent of the paper anyway).
- Cell count: 3 trading cells (STK-1, STK-2, STK-3) + 3 report cells.
- Expected events: unknown until the universe is built; working range 50-150 a year in IC's universe in the top 5 %.
- Expected size and power (no data): if IC's names carry 40-90 bp of the paper's -87.5 bp (t+1..t+3) with a 3-day
  hedged sd of ~500 bp and ~8 bp cost, per-trade net Sharpe 0.06-0.16; at 100 events a year power 0.8-2.1 at full
  size, 0.4-1.3 at x0.65, 0.1-0.5 at x0.30. **LIVE needs the top-5 % names in IC's universe to keep >= ~85 bp net with
  >= 150 events a year; the realistic tier is DEMO.**
- Data needed: (1) US share prices 2016-24 at the close (daily close and the last quote before 16:00 ET, ideally
  bid/ask) for IC's CFD list: IC's own history if it goes back (to verify), else a paid vendor; (2) earnings
  announcement dates with before/after-market timing (SEC EDGAR 8-K item 2.02 acceptance timestamps are free); (3)
  quarterly share-based compensation and shares outstanding (SEC EDGAR XBRL company facts, free); (4) IC's share
  CFD commission, financing and symbol list. No price is fetched in this round.

### H-STK amendment 1 (19:23 UTC, still before any stock data; reason: data availability, not results)
New facts from the broker helper pass (web/broker_log.tsv, 19:00-19:17 UTC): IC's own spec sheets say "Stock CFDs are
available exclusively on MetaTrader 5" (cdn.ic.com/uploads/FSA/Stocks-Product-Specification-Sheet.pdf,
Last-Modified 2026-09-01; IC EU sheet 2022-08-19); US commission USD 0.02 per share per side; financing benchmark
+/- 3 % (EU sheet); Dukascopy lists 546 US stock CFDs, ~220 of them with ticks/M1 from 2017-01..2018-02, 312 only
from 2022 (dukascopy-node instrument metadata).
- The all-firm percentile of the original definition needs market caps for every US firm, i.e. prices for
  thousands of stocks; that data is not planned. **Primary definition (replaces the percentile for STK-1/STK-2):
  absolute thresholds on lagged quarterly stock expense / market cap**, from the paper's Figure 6 Panel A (t+1..t+3
  returns about -25 bp at 0.1 %, -80 at 0.2 %, -120 at 0.3 %, -150 at 0.4 % of market cap per quarter):
  STK-1 = lagged quarterly share-based compensation / market cap at the close of t0-1 >= 0.25 % (assumed ~ the
  paper's 95th percentile); STK-2 = 0.15 % to < 0.25 %. "Lagged" = the quarterly figure of the previous quarter's
  report. The percentile version is kept as a secondary cell (STK-1pct) only if all-firm data is ever bought.
- Universe for the first test: US names that Dukascopy has from <= 2018-02 AND IC lists on MT5 (to be intersected
  by symbol list; no price needed for that). IS = 2017-03..2021-12 (shortened by Dukascopy's start), VAL 2022-24.
- Platform: an algorithm would run on MT5 (IC) or at a broker with share CFDs on cTrader (not verified here).
- Costs fixed in advance: IC US share CFD USD 0.02 per share per side; spread = Dukascopy's quoted spread at the two
  quotes as a stand-in for IC's (to be checked on a sample of IC MT5 quotes); short financing 3 nights at
  (benchmark - 3 %) / 360 with benchmark = effective fed funds (research/data/rates); USTEC hedge leg at its panel
  spread plus long financing (benchmark + 3 %) / 360 per night (IC index CFD convention assumed equal).

## H-CNH: round 19's CNY-close cell at IC's real USDCNH spreads (19:27 UTC)
**State of knowledge.** This is not a new effect: round 19 (STREAM_H) declared and measured CNHC-I, long USDCNH
14:30 -> 16:30 Beijing into the CFETS 16:30 close, at mid +1.22 bp (t 4.57) IS and +1.68 (t 4.08) VAL, cost assumed
1.04 / 1.02 bp (round 7's published average 2.93 pips + 0.6 bp) because only bid M1 exists locally
(research/data/USDCNH holds only m1 bid bars from 2015-12-31; listed, not opened, at 19:22 UTC). The decision is only
about cost: IC's USDCNH ticks (bid and ask) 2016-24 from the VPS cTrader cache.
- Rule (unchanged from round 19): long USDCNH from the last quote before 06:30 UTC to the last quote before 08:30 UTC
  (China has no DST); mainland business days (python-holidays CN); 24 Dec - 1 Jan excluded; one trade a day.
- Cost (declared): ask at entry, bid at exit from IC ticks (the last tick at or before the minute), + 0.6 bp.
- Gates: DEMO needs IS net t >= 2.0, i.e. an IS round trip <= ~0.69 bp, i.e. a USDCNH spread <= ~0.09 bp (~0.6 pip)
  at 06:30 and 08:30 UTC. LIVE is impossible at any spread: the VAL-size LIVE cost is +0.04 bp (venue_power_out.md).
- Expected power (VAL size): 1.60 at a 0.8 bp round trip, 1.19 at 1.02; x0.65: 0.53 / 0.12.
- Cell count: 1 (no variants).

### H-STK note 2 (19:36 UTC; no rule change)
The published version, Hartzmark & Solomon (2025), "Market-Wide Predictable Price Pressure", AER 115(9) 3171-3213
(doi 10.1257/aer.20231725; Crossref abstract fetched 19:36:18 UTC), is about the market-level dividend result only;
the stock-expense / blackout result appears in the 2022 NBER working paper and not in the published abstract. It is
therefore not peer-reviewed in print, which lowers my prior for STK-1. Also from the literature pass: the US
earnings announcement premium has disappeared since 2004 (weekly VW 32.6 bp t 3.5 in 1994-2003 -> 8.7 bp t 0.97 in
2005-16; "The Disappearing Earnings Announcement Premium", working paper), so the long side that would fight a
post-announcement short is small in the test eras.

## H-EMFIX: a book of EM legs into their own official fixes, led by USDMXN at the Banxico FIX (19:47 UTC)
**State of knowledge.** No USDMXN, USDSGD, USDPLN, USDCZK or USDHUF price has ever been loaded in this project (none
is in research/data); USDCNH is in the panel as bid-only M1 (round 19 measured it). Non-price inputs are from the
helper passes (web/em1_log.tsv, em2_log.tsv, broker_log.tsv, 19:00-19:41 UTC).

**Mechanism.** Round 19: binding (dealing) fixes move prices into the fix (ECB for EUR, CFETS 16:30 for CNY, Tokyo
TTM for JPY), observation fixes do not (RBA, SNB, BoE, Bank of Canada). The facts on the candidates:
- **Banxico FIX** (Circular 3/2012, arts 164-173, DOF 2012-03-02): each banking day Banxico takes the mid of the best
  T+2 bid and offer on a representative FX platform at a random instant in each of 09:00-09:59, 10:00-10:59 and
  11:00-12:00 Mexico City; FIX = mean of the three (fallback: binding quotes from >= 4 banks in a random 15-minute
  slot of each period); published from 12:00 and in the DOF the next banking day; none on non-banking days. It is
  the legal rate for USD obligations payable in Mexico (Ley Monetaria art 8; Circular 3/2012 art 172: the FIX of
  the previous banking day), the settlement rate of Banxico's FX hedges (NDFs settled in MXN, from 2017-03-06) and
  of offshore MXN NDFs/options (ISDA MXP01-04), and was the reference of Banxico's minimum-price USD auctions
  2008-2016. Whether banks fill client orders "at FIX" was NOT verified, and no study of price pressure in the
  09:00-12:00 window was found: the evidence that it is a dealing fix is weaker than for the ECB or CFETS fixes.
  Mexico abolished DST on 2022-10-30 (DOF 2022-10-28; tzdb): the window is 15:00-18:00 UTC in winter and since
  2022-11, 14:00-17:00 UTC in Mexican summer until 2022.
- **ABS SGD VWAP** (ABS Benchmarks Administration; methodology PDF abs.org.sg): VWAP of interbank USD/SGD spot
  trades >= USD 1 m via six brokers + EBS + Refinitiv in 10:30-11:00 SGT, published 11:30 SGT, Singapore business
  days; ISDA settlement source SGD3 since 2013-08-06; dealing at the fix not verified.
- **CFETS 16:30 Beijing close** for USDCNH: H-CNH above.
- Observation-fix controls (predicted ~0 by the round-19 rule): NBP Table A EUR/PLN "for 11:00" Warsaw (dealer
  poll 10:55-11:00 until 2022); CNB "trading at 2.15 p.m." Prague; MNB 11:00 Budapest trimmed mean. Accounting/tax
  use only (plus USD 1,000 GPW USD/PLN futures settling on NBP), no price-pressure evidence found.
- Side (all legs, from round 19's mechanism, fixed now): the home currency weakens into its own fix: long USD/XXX
  INTO the fix; the 15 minutes after the fix are the rebound (information only).
- Why it might escape the limits: at IC's published spreads USDMXN costs 2.07 bp a round trip against a ~32 bp
  three-hour sd (cost/sd 0.064, better than USDCNH's 0.08-0.09), the lowest cost per unit of risk of any EM pair;
  a book of fix legs on three unrelated clocks (Mexico City, Singapore, Beijing) adds independent power. Why it might
  not: the FIX is not shown to be a dealing fix; the WMR 16:00 London fix sits inside the FIX window (Krohn, Mueller
  & Whelan 2024: the USD rises into every major fix and falls back), a confound the cells below separate.

**Declared cells (nothing chosen on data).**
| cell | symbol | side | window (local clock, tz) | day set | role |
|---|---|---|---|---|---|
| MX-1 | USDMXN | long | last quote before 09:00 -> last quote before 12:00 America/Mexico_City (the FIX averaging window) | Mexican banking days (CNBV calendar of bank holidays, non-price, to fetch), excl. 24 Dec-1 Jan | primary |
| MX-15 | USDMXN | short | 12:00 -> 12:15 Mexico City | as MX-1 | information (rebound) |
| MX-H | USDMXN | long | 09:00 -> 12:00 Mexico City | Mexican bank holidays on which London and New York are open (no FIX) | placebo, predicted ~0; reported as business-day minus holiday difference, clustered by holiday |
| MX-W | USDMXN | MX-1 split at the WMR 16:00 London minute: 09:00 MX -> WMR, WMR -> 12:00 MX | as MX-1 | control: the FIX mechanism predicts USD strength in both parts; KMW predicts strength before WMR and reversal after |
| MX-C | USDMXN | MX-1 vs the same three hours on the New York clock (10:00-13:00 NY) on the days when the NY-Mexico City gap is 2 h instead of 1 h (US DST without Mexican DST: ~28-35 days a year 2007-22; ~238 days a year 2023-24) | those days | clock test: the effect should follow Mexico City |
| MX-A | USDMXN | short | 10:00 -> 11:00 Mexico City on no-minimum-price USD auction days (2015-03-11..2015-11-20, USD 52 m a day, USD 200 m from 2015-07-31) vs other days of 2015 | auction days | PRE information only (Banxico sells USD at a published size and time) |
| SG-1 | USDSGD | long | last quote before 09:00 -> last quote before 11:00 Asia/Singapore (the 120 minutes ending at the end of the VWAP window) | Singapore business days (python-holidays SG), excl. 24 Dec-1 Jan | secondary leg |
| CN-1 | USDCNH | long | 14:30 -> 16:30 Beijing (= H-CNH, round 19 CNHC-I) | mainland business days | leg (effect already measured at mid) |
| BOOK | MX-1 + SG-1 + CN-1 | each trade scaled to 1 / its IS per-trade sd (equal risk), one position per symbol, <= 3 positions per bot | | | book result |
| PL-1 / CZ-1 / HU-1 | USDPLN, USDCZK, USDHUF | long | 09:00 -> 11:00 Warsaw; 12:15 -> 14:15 Prague; 09:00 -> 11:00 Budapest (tz Europe/*) | home business days | optional controls, predicted ~0; only if the user pulls these symbols |

- SG-1's window (01:00-03:00 UTC) overlaps C3's post-Tokyo-fix hours: report SG-1 on gotobi vs non-gotobi days and
  its daily correlation with C3; it must not depend on the gotobi calendar.
- Costs: IC ticks (ask in, bid out) at the declared minutes + 0.6 bp; PRE: IC's 2016-17 spread of the symbol by
  minute of week on the local clock + 0.6 bp. Intraday, no swap.
- Eras: PRE 2007-03-13..2015 for USDMXN (Dukascopy start), 2004-11-16..2015 for USDSGD, 2012-06..2015 for USDCNH
  (Dukascopy; round 19 had no CNH PRE); IS 2016-21; VAL 2022-24.
- Cell count for the chance benchmark: 3 trading cells (MX-1, SG-1, CN-1) + the book; information/placebo cells
  MX-15, MX-H, MX-W, MX-C, MX-A (+ PL-1, CZ-1, HU-1 if pulled) are not counted as trading cells.
- Expected events per year: ~245 per leg (MX-1 ~245, SG-1 ~245, CN-1 ~237).
- Expected size and power (`emfix_book.py`, no data): at E1's mid Sharpe (0.13) MX-1 ~4.2 bp vs 2.07 bp cost
  (power 1.35), SG-1 ~1.3 vs 1.23 (0.12), CN-1 1.68 vs ~0.9 (1.42): book 1.96 at full size, 0.55 at x0.65, 0 at
  x0.30. If EM fixes move 1.5x E1 per unit of risk (s = 0.20): MX-1 2.78, SG-1 1.54, book 3.48; x0.65 1.40.
  **LIVE needs the 1.5x case AND no decay; the realistic outcome is a DEMO-tier MX-1 at best.**
- Data needed: IC ticks 2016-24 for USDMXN, USDSGD, USDCNH (VPS backtest download + pull_cache.sh); Dukascopy M1
  USDMXN 2007-15, USDSGD 2004-15, USDCNH 2012-15 (free); CNBV Mexican bank-holiday calendars 2007-24 and Singapore
  holidays (non-price). No price is fetched in this round.

### Amendments after the helper passes (19:50 UTC; no rule change, no data seen)
- H-NOK costs: IC's published average EURNOK spread is 52.89 pips on the global page and 24.40 on the EU page
  (5.6 / 2.9 bp a round trip with the 0.6 bp commission at ~10.5); USDNOK 36.79 pips (4.5 bp). STREAM_A uses a
  09:00-16:00 EURNOK sd of ~40 bp (assumed 8.5 %/yr vol) instead of the 45 bp guess above; the conclusion (power
  < 0 at the impact-model size, ~0.8 at twice it) is unchanged. Krohn, Mueller & Whelan (2024) report NOK -3.51 %/yr
  (t -2.2) in 08:00-14:15 CET and -5.08 % (t -3.8) after the ECB fix in 1999-2019, a constant European-hours NOK
  weakness that NOK-D's constant absorbs and that NOK-1 meets with opposite signs in IS and VAL.
- H-EMFIX, MX-W: the WMR 16:00 London minute falls at 10:00 Mexico City in most of the year before 2022-11 and at
  09:00 Mexico City (the window's start) during UK summer time from 2023; on those days KMW predicts USD weakness
  over the whole MX-1 window while the FIX mechanism predicts USD strength, so MX-1 on UK-summer days of 2023-24 vs
  the rest is a declared sign test of the two mechanisms.
- H-STK clocks: every STK time is America/New_York (DST-aware); on NYSE early-close days (13:00 ET) the "close" is
  the actual early close; t0 uses the 8-K acceptance time on the same clock (before 09:30 -> that day; 09:30-16:00
  -> that day; after 16:00 -> next trading day).

## Query log (condensed; full logs in the scratch folder) (written 19:50 UTC)
Own calls (`r25/A/query_log.tsv`), in order; connectivity tests merged:

| time UTC | tool | query or URL | outcome |
|---|---|---|---|
| 18:59:19-19:00:02 | curl | connectivity tests (19 hosts) | reachable: api.crossref.org, api.openalex.org, export.arxiv.org, raw.githubusercontent.com, registry.npmjs.org, www.banxico.org.mx, www.bis.org, www.cnb.cz, www.norges-bank.no, www.riksbank.se; not: api.semanticscholar.org, fusionmarkets.com, www.dukascopy.com, www.icmarkets.com, www.myfxbook.com, www.nbp.pl, www.pepperstone.com, www.spotware.com |
| 18:59:30 | WebFetch | https://www.icmarkets.com/global/en/trading-markets/forex | failed (no output) |
| 18:59:40 | WebSearch | IC Markets cTrader forex exotic pairs spreads USDMXN USDZAR USDNOK USDSEK USDPLN commission per side | ok: cTrader commission USD 3 per 100k traded (IC official page via snippet); no exotic spreads |
| 18:59:50 | WebFetch | https://www.icmarkets.com/sc/en/trading-pricing/spreads | failed (no output) |
| 18:59:55 | WebFetch | https://www.myfxbook.com/forex-brokers/ic-markets | failed (no output) |
| 18:59:55 | WebFetch | https://compareforexbrokers.com/reviews/ic-markets-review/spreads-fees | failed (no output) |
| 18:59:58 | WebFetch | https://en.wikipedia.org/wiki/Fixing_(finance) | reached (404): WebFetch works for some hosts |
| 19:04:18 | WebSearch | Norges Bank foreign exchange transactions for the government daily amount NOK per day announced monthly how executed | ok: monthly press releases 2025-26; 'executed in the market as a daily net amount' |
| 19:04:18 | curl | https://www.norges-bank.no/en/news-events/news/Press-releases/2025/2025-02-28-fx/ | saved pr_2025-02-28.html |
| 19:04:33 | curl | https://www.norges-bank.no/en/topics/liquidity-and-markets/Foreign-exchange-purchases-for-GPFG/ | saved topic_fx_gpfg.html |
| 19:04:47 | curl | https://www.norges-bank.no/en/topics/liquidity-and-markets/faq-exchange-transactions/ | saved faq-exchange-transactions.html |
| 19:04:47 | curl | https://www.norges-bank.no/en/topics/statistics/foreign-exchange-transactions-daily/ | saved stats_fx_daily.html |
| 19:05:49 | WebSearch | Norges Bank "purchase NOK" "fund the transfer" profit to the government per day press release 2019 foreign exchange t... | ok: 2019 releases list only government FX sales (no dividend component) |
| 19:05:49 | curl | https://www.norges-bank.no/en/news-events/news/Press-releases/2024/2024-02-29-fx/ | saved pr_2024-02-29-fx.html (   29362 bytes) |
| 19:05:49 | curl | https://www.norges-bank.no/en/news-events/news/Press-releases/2023/2023-02-28-fx/ | saved pr_2023-02-28-fx.html (   32049 bytes) |
| 19:05:49 | curl | https://www.norges-bank.no/en/news-events/news/Press-releases/2019/2019-02-28-press-release/ | saved pr_2019-02-28-press-release.html (   29689 bytes) |
| 19:06:14 | WebSearch | effect of Norges Bank's foreign exchange purchases on the krone exchange rate analysis economic commentary | ok: ING/MNI commentary only; no econometric estimate found |
| 19:06:14 | OpenAlex | Norges Bank foreign exchange purchases krone | 657 hits |
| 19:06:14 | OpenAlex | pre-announced foreign exchange intervention Norway krone | 471 hits |
| 19:06:14 | OpenAlex | petroleum fund foreign exchange transactions exchange rate Norway | 4638 hits |
| 19:06:14 | OpenAlex | sovereign wealth fund currency conversion exchange rate predictable flows | 1266 hits |
| 19:06:34 | curl | https://hdl.handle.net/11250/2563496 | thesis landing (    3055 bytes) |
| 19:06:43 | curl | https://uis.brage.unit.no/server/api/core/handles/11250/2563496 |  bytes |
| 19:06:43 | curl | https://uis.brage.unit.no/uis-oai/request?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:uis.brage.unit.no:11250... |  bytes |
| 19:06:43 | curl | https://api.openalex.org/works/W2899240847 |    11184 bytes |
| 19:07:04 | WebSearch | Does Norges Bank's trading in the foreign exchange market on behalf of the government affect the NOK exchange rate Lø... | ok: 2018 UiS master thesis (Løberg), mixed results; NB article 2023-05-23 sales-of-nok |
| 19:07:04 | curl | https://www.norges-bank.no/en/news-events/news/Articles-and-opinion-pieces/2023-05-23-sales-of-nok/ | saved art_2023-05-23.html (   33347 bytes) |
| 19:08:31 | WebSearch | Riksbank sell foreign currency reserves hedge 2023 USD 8 billion EUR 2 billion evenly per day krona effect | ok: 2023-09-25..2024-01-26 USD 8bn + EUR 2bn, pace adjusted to market conditions (not even), weekly figures with 2-week lag (riksbank.se,... |
| 19:08:31 | WebSearch | Swedish National Debt Office currency exchange purchases ... Riksgälden exchanges SEK billion per | ok: Riksbank agent for SNDO until 2002-07 (daily morning window); Riksbank self-financed reserve purchases ~SEK 5bn/month even pace (2021... |
| 19:10:36 | WebSearch | BIS Triennial Survey 2022 currency distribution ... NOK SEK MXN ZAR PLN share percent | ok: table index only (rpfx22_fx.pdf) |
| 19:10:36 | curl | https://www.bis.org/statistics/rpfx22_fx.pdf | saved rpfx22_fx.pdf (     314 bytes) |
| 19:10:43 | curl | https://www.bis.org/statistics/rpfx22_fx.htm | saved rpfx22_fx.htm (  140760 bytes) |
| 19:10:52 | curl | https://www.bis.org/publications/commentary-otc-derivatives/statistics-rpfx22-fx-annex.pdf | saved rpfx22_annex.pdf ( 1069119 bytes) |
| 19:14:35 | WebSearch | Norway petroleum tax instalments due dates six equal instalments ... oil companies buy NOK | ok: 6 instalments (1 Aug, 1 Oct, 1 Dec, 1 Feb, 1 Apr, 1 Jun) to 2024; 10 instalments from 2025 (skatteetaten.no) |
| 19:15:03 | OpenAlex | Hartzmark Solomon predictable price pressure dividend reinvestment market returns |  hits |
| 19:15:03 | OpenAlex | dividend payment days aggregate market returns reinvestment price pressure |  hits |
| 19:15:15 | Crossref | predictable price pressure dividend reinvestment |     2952 bytes |
| 19:15:24 | OpenAlex | Hartzmark Solomon predictable price pressure ... / dividend payment days ... | FAILED: OpenAlex free daily budget exhausted for this IP (resets 00:00 UTC) |
| 19:15:24 | curl | https://www.nber.org/papers/w30688 |    88533 bytes |
| 19:16:18 | curl | https://www.nber.org/papers/w30688 | ok: abstract (dividend-payment price pressure; blackout selling 117 bp in 4 days) |
| 19:16:18 | Crossref | predictable price pressure dividend reinvestment | ok: Hartzmark & Solomon 2022 NBER w30688 / SSRN 4288522; Li, Yang, Zhang 2026 SSRN 6459800 |
| 19:16:18 | curl | https://www.nber.org/system/files/working_papers/w30688/w30688.pdf |   800140 bytes |
| 19:18:14 | local | read w30688.pdf (pdftotext): Table XI and sections G, market-level dividend result | ok: top-5% lagged stock expense t0..t+3 -116.5 bp (t -5.50), t+1..t+3 -87.5 (t -5.77), 2002-2020, ~300k announcements; market: top-quarte... |
| 19:36:18 | Crossref | https://api.crossref.org/works/10.1257/aer.20231725 |    11826 bytes |

Helper passes (read-only research agents launched at 19:01 UTC; their logs list every call with its time):

| log | calls | first - last (UTC) | by tool |
|---|---|---|---|
| web/em1_log.tsv | 157 | 19:04:07 - 19:42:30 | curl 106, WebSearch 26, WebFetch 17, local 8 |
| web/em2_log.tsv | 93 | 19:04:04 - 19:27:40 | curl 54, WebSearch 33, WebFetch 5, note 1 |
| web/broker_log.tsv | 125 | 19:04:09 - 19:17:40 | WebSearch 84, curl 31, WebFetch 4, Read(PDF) 4, local 1, python3 1 |
| web/lit_log.tsv | 180 | 19:06:01 - 19:32:37 | WebSearch 50, curl 45, WebFetch 41, Crossref 38, OpenAlex 6 |

The session's shared WebSearch budget (200) ran out at ~19:17 UTC and OpenAlex's free daily budget for this IP at
~19:11 UTC; later calls were direct fetches (curl/WebFetch) of official and literature URLs.
