# Round 25, stream C: older literature (<= 2017) and non-English practitioner lore, declared only

Brief: [BRIEF.md](BRIEF.md) row C; round13_structural/BRIEF.md (data, costs, bars, pitfalls); round23_recent/BRIEF.md
(declared-only rule). Every cell below is declared in full, with the `date -u` time, before any of its returns was
computed. Sides come from the sources, never from our data. HOLD (2025-01-01 onwards) is never loaded (the shared panel
ends 2024-12-31; Dukascopy files are cut at 2016-01-01 at load; the `*_2026.npz` files are never opened).

## Order of work (and one disclosed reordering)
1. Literature harvest (log below), started 2026-10-17 19:04 UTC.
2. Families MON and BAR were declared at **2026-10-17 19:33:56 UTC** (section "Declaration 1"), before the census map
   (Step 2) was complete, because their sources were already in hand and nothing in the remaining triage could change
   their definitions. Before this declaration no return of any kind had been computed in this stream; only event
   counts (BAR crossings per year, no prices differenced into returns) and the LBMA tick-count spike (activity, not a
   direction) were looked at.
3. The census map and any further declarations follow, each with its own `date -u` time before its numbers.

## Step 1: search log (raw files and per-query log in the scratchpad `r25/C/lit/`)
| source | queries | time (UTC) | result |
|---|---|---|---|
| OpenAlex, topic search, filter publication_year 1970-2017, top 200 by relevance | 74 (FX 26, metals 9, energy 8, indices 28, crypto 3) | 19:04:43-19:07:57 | 74 x 200 max; API totals per query in `log.tsv` (e.g. F01 1,106; F15 310; M01 301; E01 453; I01 2,104) |
| OpenAlex, title lookups of named classics | 80 | 19:09:41-19:10:32 | 7 answered, then "Insufficient budget ... $0 remaining" (free daily budget of the network's IP; a key needs an account e-mail, not requested) |
| Crossref, query.bibliographic, 1970-2017 journal articles, top 100 | 74 (same topics) | 19:08:10-19:10:59 | 74 x 100 |
| Crossref, title lookups of named classics (top 5) | 73 | 19:10:57-19:13:07 | 73 x 5 |
| arXiv API, abs AND-terms, submitted <= 2017-12-31 | 74 | 19:11:01-19:15:55 | 7 records in total (q-fin starts 2008; little before 2018) |
| Semantic Scholar search | 18 attempted (a slow retry loop, stopped at 19:55) | 19:08:10-19:53:26 | 2 answered (F05, F10; 200 records), 16 HTTP 429 (anonymous pool); log in `log_s2.tsv` |
| SSRN | 1 probe | 19:02 | unreachable (no response), as in rounds 12, 19, 23 |

Unique records after merging (DOI / normalised title): **13,748** (OpenAlex 9,154; Crossref 5,054; arXiv 7); 8,909
with an abstract; 13,674 dated <= 2017. Timing-word x asset-word filter on title + abstract, year <= 2017: **2,965**
records (248 of them auto-dropped as volatility / spread / liquidity / volume titles without a return word). The
remaining 2,717 were read by title (and abstract where kept) in three parallel passes; counts in Step 2.

## Declaration 1 (2026-10-17 19:33:56 UTC)

Common to both families:
- Data: shared panel (bar-start labels): the price at clock time T is the close of the bar labelled T - 1 min; a fill
  at T uses the first quote at or after that bar within 10 minutes, else the trade is void. Signal on data up to T,
  fill at T + 1 minute or later.
- Costs: half the actual spread at the entry minute + half at the exit minute; + 0.6 bp round trip for XAUUSD; 0 for
  index CFDs. Index financing for holds across the 17:00 New York rollover: long pays (r + 5.3 %)/360 per night, short
  receives (r - 3.9 %)/360 per night (round 7 D's fitted markups), r = the index currency's rate from the local FRED
  files (HKD = USD), Friday counts 3 nights. Variants on every cell: spread x1.5; both fills 1 minute late.
- Eras: IS 2016-01-01..2021-12-31 and VAL 2022-01-01..2024-12-31 by entry time; no PRE (no index data before 2016;
  XAUUSD PRE is information only, see BAR).
- Statistics: bp per trade; t clustered by UTC day of entry; by year; VAL/IS; per-trade net Sharpe and power = Sharpe x
  sqrt(1.73 x trades/yr) on the IS and on the VAL size (also on day-summed units for pooled cells); random-entry
  control with >= 200 seeds (500 for MON); chance = max |t| of K normals over the declared cells and a sign-flip null
  per UTC day shared by all cells of a family.
- Bars: LIVE and DEMO exactly as round13_structural/BRIEF.md. Correlation with C3 (IS + VAL, daily and monthly) for any
  cell that meets either bar.

### Family MON: Monday follows a down Friday (individual investors' Monday selling)
Sources and sides (from the sources): Abraham & Ikenberry 1994 (JFQA 29(2)): when Friday's return is negative, Monday's
return is negative ~80 % of the time with mean -0.61 % (US, 1963-91); after a positive Friday, Monday's mean is
+0.11 %; individual investors are more active sellers on Mondays, especially after bad news. Wang, Li & Erickson 1997
(JF 52(5)): the Monday effect occurs mainly in the 4th and 5th weeks of the month. Sun & Tong 2002 (JBFA): negative
Mondays concentrate on days 18-26 and are explained by the previous negative Friday; returns on all days are lower in
the fourth week (days 18-26), "liquidity selling by individual investors".
Not tested before: round 19 T3 tested Monday's own move reversing over the week (Ülkü & Andonov); round 3 the
unconditional weekend and Friday squaring; rounds 2/7/11 unconditional 1-day momentum. The Friday-signed weekend hold and
the days-18-26 window are new constructions.

Definitions: NYSE calendar (rule-based: closures, 13:00 ET early closes). p(D) = US index CFD mid at 16:00:00 New York
on NYSE day D. F = a Friday that is a full NYSE day; P = the NYSE trading day before F; M = the next Monday, a full NYSE
day (weeks where F or M is a closure or early close are skipped). r_F = p(F)/p(P) - 1. Entry 16:01 New York on F, exit
16:00 New York on M (3 nights of financing).

| cell | symbol(s) | rule | expected trades IS / VAL |
|---|---|---|---|
| MON-a (primary) | US500 | short if r_F < 0 | ~130 / ~65 |
| MON-b | US500 | follow sign(r_F) (short after down, long after up Fridays) | ~290 / ~145 |
| MON-c | US30 + USTEC pooled | short if the symbol's own r_F < 0 | ~260 / ~130 |
| MON-d | US500 | MON-a only when M's calendar date is 18..26 | ~28 / ~14 |
| MON-e | US500 | week four: short from 16:01 NY on the last NYSE day before the 18th to 16:00 NY on the 5th NYSE trading day after it, or on the last NYSE trading day <= the 26th if earlier (one trade a month) | ~72 / ~36 |

Random controls (500 seeds, same count, same hold): MON-a/d random weekends short (any r_F); MON-c the same for US30 +
USTEC; MON-b random weekends with random sides, and the cell's own weekends with random sides; MON-e random 5-trading-day
short windows starting on any NYSE day of the month.

### Family BAR: continuation after a round-number barrier breaks (stop-loss clustering beyond round numbers)
Sources and sides: Donaldson & Kim 1993 (JFQA 28(3)): the DJIA is restrained by support/resistance at multiples of
100; "having broken through a 100-level, the DJIA then moves by more than otherwise warranted". Cyree, Domian, Louton &
Yobaccio 1999 (RFE 8): 8 indices, multiples of 100; conditional mean returns significantly higher after an upward
crossing in 5 of 8 (downward: 2 of 8). De Grauwe & Decupere 1992: USD/JPY accelerates away from round numbers once
crossed. Osler 2005 (JIMF 24; 2003 JF 58): stop-loss orders cluster just beyond round numbers, trends are unusually
rapid after rates reach them, significant for hours. Aggarwal & Lucey 2007 (RFE 16) and Lucey & O'Connor 2016 (FRL):
barriers in gold at prices ending in 0 and 00. Counter-evidence: Ley & Varian 1994 (DJIA closes: no predictive use).
Side = the direction of the break (continuation). Not tested before outside FX: round 3 tested FX big figures only
(0.1-0.8 bp, no different from a non-round level); round 10 D tested option-strike pinning at round levels on expiry
days (a different mechanism: attraction at expiry).

- **BAR-i (primary, pooled)**: US30, US500, USTEC, DE40, UK100, JP225, AUS200, HK50 at multiples of 100 index points,
  XAUUSD at multiples of $10. Event at bar i when its mid close is on the other side of a level L than the previous
  quote (gap <= 5 min) and L was not crossed in the previous 1,440 minutes; side = direction of the break; entry at the
  close of bar i + 1, exit 60 minutes later; one open trade per symbol (events during an open trade are skipped).
  Excluded: entry or exit inside 16:55-18:10 New York; events within 15 minutes after a quote gap > 60 minutes.
  Expected ~2,200 trades/yr IS, ~2,950/yr VAL (event counts computed at 19:31 UTC, no returns).
- **BAR-d (primary, pooled)**: the 8 indices at their cash close (US 16:00 New York; DE40 17:30 Frankfurt; UK100 16:30
  London; JP225 15:00 Tokyo, 15:30 from 2024-11-05; AUS200 16:00 Sydney; HK50 16:00 Hong Kong), days with >= 20 ticks
  in the 30 minutes before the close. Event when the close is on the other side of a multiple of 100 than the previous
  close (<= 4 calendar days apart); follow the break from the close + 1 minute to the next close (1 night, 3 over a
  weekend). Expected ~1,160 trades/yr.
- Information only (not cells): per-symbol rows; the same rules at half levels (L + 50 points, L + $5) as a placebo;
  XAUUSD BAR-i on PRE 2004-15 (Dukascopy bid, IC 2016-17 spread profile + 0.6 bp) if time allows.
- Random controls (200 seeds): BAR-i random bars in the same symbol, era and UTC-hour mix, side = sign of the last
  1-minute move (recomputed), same fills and hold; BAR-d random days, side = sign of that day's close-to-close move.

Cells declared in Declaration 1: K = 7 (MON-a..e, BAR-i, BAR-d). Max |t| of 7 normals: median ~1.7, 95th ~2.7.

## Step 2: census map (written 2026-10-17 19:42 UTC, after Declaration 1's numbers; the map's drop reasons are records of earlier rounds and of the sources, not of our returns)

Triage of the 2,717 filtered records (three parallel passes, then my review of every kept row): F (FX queries) 1,030
rows -> 92 kept; I (index queries) 1,023 -> 176 kept; O (metals, energy, crypto, classic lookups) 664 -> 85 kept; 353
kept rows in all (some papers appear in two groups). Dropped at triage: off-topic / outside finance 874; emerging or
non-listed markets 230; volatility / spread / liquidity / volume only 225 (+ 248 auto); method only 248; horizon > 5
days 150; single stocks only 228; news with a surprise-dependent side 99; technical rules 36; no direction 274. Files:
`r25/C/lit/triage/triage_{F,I,O}.tsv` (one line per record with the reason).

The kept rows fall into the families below ("ids" are the record ids in those files; "tested" cites the round that
covered the construction).

| # | family (sources, ids) | mechanism | side / window (source) | IC symbols, events/yr | reported size; source's own OOS note | tested where | decision |
|---|---|---|---|---|---|---|---|
| L1 | home-currency depreciation in home hours: Ranaldo 2009 JBF (C0001), Breedon & Ranaldo 2013 JMCB (C0002) | residents buy FX in their own hours | home currency falls in its local hours | FX majors, 250 | n/r | swing v2; r10 B3, C HOME; r13 M (E1 is its surviving form) | drop: tested |
| L2 | FX weekday effects: McFarland, Pettit & Sung 1982 JF (C0050: USD weak Mon/Wed, strong Thu/Fri), Yamori & Kurihara 2004 (C0047, C0048), C0439 C0458 C0480 C0682 C0686 C0703 C0727/C0745 C2935 | value-date settlement; pre-weekend USD demand | as stated, by weekday | FX, 52 per weekday | n/r; gone after the 1990s (C0047/48), fragile (C0686) | r3 weekday x session (373 cells); r13 M weekday x clock with PRE (270k); W1 r3 / r24 B A13 | drop: exhausted |
| L3 | FX futures intraday, opening and jump reversals: Cornett, Schwarz & Szakmary 1995 JBF (C0005, no abstract), C0136, C0602 (Tue close -> Wed open USD down), C1086, C0567, C1046 | clock; value-date roll; overreaction to jumps | clock / reversal after jumps | FX, 250 | n/r | r3 session hand-off and Asian MR; r13 M; r15 S (CME 14:00/15:00 ET, NY 10:00); r8 S shocks; r17 Y | drop: exhausted |
| L4 | FX benchmark fixes: Melvin & Prins 2015 (C0839/C0858), Evans 2018 and "did the reform fix the London fix" (C0863), Tokyo fix (C0845, C0848/C0867), NOK reference rates (C1498) | hedging / benchmark flows | into / out of the fix | FX, 12-250 | ~1-7 bp | r3 F1, r10 E, r12 I, r15 S; Tokyo = C3 (excluded); NOK not in the 26 (stream A) | drop |
| L5 | round numbers in FX: Osler 2003 JF (C0010/C0991), Osler 2005 JIMF (C0011), De Grauwe & Decupere 1992 (C1014), Mitchell & Izan 2006 (C0051) | stop / take-profit clustering | reverse at, accelerate through round numbers | 10 FX | n/r | r3 (big figures: 0.1-0.8 bp, no different from non-round levels) | drop for FX; mechanism carried to indices / gold (BAR) |
| L6 | round numbers in indices: Donaldson & Kim 1993 JFQA (C0024), Cyree et al. 1999 RFE (C2016), Koedijk & Stork 1994 (C0039), Ley & Varian 1994 (C2015, none), Dorfleitner & Klein 2009 (C0040), C1016 (Germany significant), C2022/C2028 (Benford, none directional), C2029 (new highs at round levels: no momentum after), C2031 (Asia: little predictability), C2804, C2013, C2017, C2034 | stop clustering / reference points | continue after a break of a 100-multiple | 8 indices, ~1,100 (daily) to ~2,900 (intraday) | n/r; mixed | never | **declared: BAR-i, BAR-d** |
| L7 | round numbers in gold: Aggarwal & Lucey 2007 RFE (C0021), Lucey & O'Connor 2016 FRL (C0022; gold yes at 0 / 00, silver no) | same | conditional mean shifts around $10 / $100 levels | XAU, ~250-350 at $10 | n/r | never | **declared inside BAR-i** |
| L8 | round numbers in oil: Dowling, Cummins & Lucey 2016 Energy Econ. 53 (C0180; WP C0052), Cho 2017 (C0175) | same | Brent falls after an upward break of a $10 level, 1-5 days; none in WTI | XBR, ~5-15 | n/r; present only 1990-2006, "dissipated" after (source) | never | drop: source says gone; power < 0.5 at ~10 events/yr |
| L9 | LBMA gold fix leakage and fix autocorrelation: Caminschi & Heaney 2014 JFutM (C0019), Smith 2002 (C2690), Baur 2014 (C2713), Abrantes-Metz & Metz | informed trading in the opening minutes of the fix | follow the first minutes after 15:00 London | XAU, 250 | fix direction predictable > 90 % (phone fix) | r15 V4 (2,460 cells, cites Caminschi & Heaney: below cost); r24 B A6/A8 (PRE) | drop: tested |
| L10 | gold weekday, weekend, overnight: Lucey & Tully 2006 (C0033), Blose & Gondhalekar 2013 (C0068), Blose 2011 (C2749), Blose et al. 2017 (C2714), Ball, Torous & Tschoegl 1982 (C2820), C1112 C2745 C2767 C2822 C2064 | weekend / Monday / night weakness | Fri close -> Mon close low; overnight negative | XAU, XAG | n/r | r3 weekend premium (metals positive at IC: a Friday last-hour quote effect); r3 weekday x session; r13 M (XAU, PRE) | drop: exhausted |
| L11 | lunar cycle: C0432 (metals), C1611 (indices) | mood | new / full moon windows | indices, metals, ~12 | n/r | never | drop: no flow / settlement / premium basis (bar), effect ~1-3 bp a day on a 100 bp sd |
| L12 | gold ETF flows -> gold: C2727 (2012) | creations bought at the fix | continue 1-2 days, reverse days 3-5 | XAU | n/r | r3 (gold ETF creations at the PM price) | drop: tested; daily flow file not in the repo |
| L13 | energy inventory releases: Halova, Kurov & Kucher 2014 (C0036), C0110 (2017), Linn & Zhu, Gay et al., Bjursell et al. | surprise impact; API predicts EIA | side from the surprise | XTI, XBR, XNG, 52 | ITC impact 2x OLS | r6 S2/S3 reactions | not declared: the FF file has EIA crude and gas-storage consensus but no API values; stream B tested consensus anchoring on FX (priced, +0.71 bp gross pooled) but not on energy CFDs; listed as an untested idea |
| L14 | commodity-index roll: Mou 2011 (C0038), Bessembinder et al. 2016, GSCI rebalancing (C0219: none) | index roll front-running | calendar-spread pressure 5th-9th business day | XTI, XBR | Sharpe up to 4.39 (spread) | r3 O1 | drop: tested; a spread trade, not holdable with IC's single CFD |
| L15 | energy weekday / weekend: C0424 C0199 C0203 C0205 C0225 (Friday up) C0365 (TGIF: oil weekend low, gas reverse) C2822 | inventory schedule / weekend | by weekday | XTI, XBR, XNG | n/r | r19 T6 (crude day of week), r3 weekend premium and weekday x session | drop: tested |
| L16 | crypto weekday: Caporale & Plastun (C0184), C2905 C2907 C2908 C2917 | - | Monday high / weekdays positive | BTC, ETH | n/r; fading (C2917) | r19 T5 | drop: tested |
| L17 | index Monday / weekend, unconditional: French 1980 (C0056), Gibbons & Hess, Keim & Stambaugh (C0709), Lakonishok & Levi 1982 (C0710), Rogalski 1984 (C0057, C0547), Smirlock & Starks (C0405), Jaffe & Westerfield 1985 (C0617, C2736), Junkus 1986 (C0074), reverse weekend: Brusa et al. 2000 (C0714), Mehdian & Perry (C1651), C2829 C1583 C1652 C1654 C1803; ~40 more (C1538 C1539 C1614 C1647 C1649 C1653 C1659 C1682 C1684 C1688 C1736 C1743 C1774 C1775 C1789 C1795 C1816 C0718 C0720 C0754 C0423 C0520 C0543 C0631 C0637 C0638 C0665 C1386 C1367 C2208 C2294 ...) | settlement float, individual selling | Monday negative (pre-1987), positive for large caps after | indices, 50 | -0.17 % (French) | r3 weekday x session and weekend; r11 H (every 15/60-min index window by weekday); r19 T3, T4 | drop: exhausted |
| L18 | Monday conditional on Friday and on the week of the month: Abraham & Ikenberry 1994 JFQA (web), Brooks & Kim 1997, Sun & Tong 2002 JBFA, Wang, Li & Erickson 1997 JF (C0027), C1719 (null, Singapore), C1732 (long Mondays of weeks 1-2, 1988-98) | individuals sell on Mondays after bad Fridays | short Monday after a down Friday; weeks 4-5 / days 18-26 | US500, US30, USTEC, ~22-50 | -0.61 % after down Fridays (1963-91) | never | **declared: MON-a..e**; C1732 dropped by power (size n/r; at <= 15 bp the IS t is <= 1.5 after the weekend swap) |
| L19 | daylight-saving weekends: Kamstra, Kramer & Levi 2000 AER (C0025/26), Pinegar 2002 (C2350), C2354 C2355 C2356 C2357 | sleep loss | short DST-change weekends | US500, DE40, UK100, AUS200, 2 each | 200-500 % of a normal weekend | refuted (outliers; 22-country and Australian nulls) | drop: refuted; ~6 events/yr pooled, expected IS t ~1 at the published size; no flow basis |
| L20 | turn of month / payment cycle: Ogden 1990 (C0028), Ariel 1987, Lakonishok & Smidt 1988, C0481 C0510 C0787 C0820 C0822 (FX futures) C0824 C0827 C0829 C1409 C1664 C1912 C1926 C1938 C1944-C1947 C1920 C1927 C1930 C0370 C1788 | payment standardisation at month-end | long last day + first days | indices, FX, 12 | n/r; shifting earlier, weakening | swing v2 TOM; r3 calendar scans; r13 N7 (Etula); r18 B; r19 T2 | drop: tested |
| L21 | earnings-season half-month: Penman 1987 (C0030) | good news early in the reporting month | long the first half of Jan/Apr/Jul/Oct | indices, 4 windows | n/r | r23 P4 (blackout window covers it; IS post hoc +8.2 bp/day t 2.39, VAL +0.4) | drop: near-tested; window > 5 days |
| L22 | pre- / post-holiday: Ariel 1990, Lakonishok & Smidt, Kim & Park 1994, Meneu & Pardo 2004, C1657 C1836-C1841 C1847 C1863 (pan-European) C1878 C1879 (currency futures) C1883 C1886 C0774 (US holidays -> Europe) C0786 C1686 | holiday mood / short covering | long pre-holiday | indices, FX, ~9 | strong to 1987, then diminished (C1657) | swing v2 (pre-holiday); r10 B (holiday blocks with placebo; B3 US holidays); r13 M HOL/PRE/POST | drop: tested |
| L23 | single-date festivals and superstitions: Lunar New Year (C1840 C1844 C1849 C1882), Jewish High Holy Days (C2584), Melbourne Cup (C1784), auspicious days (C0371), Friday 13th (C1687 C1830), administrations (C1618 C0693), Chinese numerology FX days 8/18/24 (C0744) | mood | as stated | 1/yr or calendar days | n/r | r23 N3a (Lunar New Year gold); r18 B (all calendar days, FX/gold) | drop: 1/yr or no economic basis |
| L24 | expiration days: Stoll & Whaley 1987/1991/1997 (C0294), C0340 (Euro Stoxx 50 before 12:00 CET), C1948 (triple-witching last hour, reversal), C1949 C1958 C1965 (HSI), C1950 (DAX), C1953 C1963 C1193 C1194 C1739 C1978 | arbitrage unwinds | into / after settlement | indices, 4-12 | n/r | r20 G (64 cells); r11 H2 SOQ; r3 quarterly; r23 P5 | drop: tested |
| L25 | close / open price pressure and marking: Cushing & Madhavan 2000 (C0032), Hillion & Suominen 2004, Carhart et al. 2002, Ben-David et al. 2013, C2003 C2006 C2237 (HSI end-of-day) C1579 C2102 (opening overreaction) C1487 C1086 | MOC, marking the close | fade after the close / open | indices | n/r | r3 post-close; r11 H2; r12 J; r15 V1/V3; r23 P (Carhart: 4/yr, power < 0.5) | drop: tested |
| L26 | reversals after large opening moves in index futures: Grant, Wolf & Yu 2005 (C0062), Fung, Mok & Lam 2000 (C0061), C2240, C1251 (HK overreaction, weaker after 2004) | overreaction | fade the opening move | US500, HK50, 250 | n/r | r12 K3; r15 V1; r8 X2d | drop: tested |
| L27 | intraday return patterns / U-shapes: Harris 1986, Wood, McInish & Ord 1985, Jain & Joh 1988, Ekman 1992 (C0100), C0151 C1550 C2310 C2298 (FTSE futures) C1646 C2159 C2200 C2270 | clock | Monday morning down; open/close up | indices | n/r | r11 H1 (every 15-min boundary, local and UTC, by weekday); r4 scan; r15 V | drop: exhausted |
| L28 | cross-market open spillovers: C1534 C2040 C2067 (local open vs US-implied open) C2077 C2078 C1105 C1637 C1645 C2206 | non-synchronous trading | follow the US session at the next local open | JP225, DE40, UK100, HK50 | profits vanish after costs (C2040) | r8 (lead-lag, X2a session spillovers rejected); r15 V1 rule G | drop: exhausted |
| L29 | intraday momentum and sentiment: C0576 (market-wide early moves continue), C1146 (online sentiment), Gao et al. | late-day trend following | follow the early move | indices | 2.8 %/month US (C0576) | r8 X2c; r12 K1/K6/K7; r17 Z | drop: tested; sentiment data absent |
| L30 | index changes, dividend reinvestment, fund distributions, pension rebalancing: C1540 C2001 C2293 C2415 C2419 C2440 C2441 C2445 C1604 C1630 C2009 C2366 C2455 (Dutch pensions, quarterly counter-trend) | index-tracker and reinvestment flows | long additions / payers | stock level; payment calendars | n/r | r16 W (dividends, AGMs); r23 P6 (quarter-end pension rebalancing against the QTD move) | drop: stock level or needs a payment calendar (user decision) |
| L31 | announcement premia: C1284 (long equities on NFP and FOMC days), C1246, Savor & Wilson | risk premium for news | long on announcement days | indices, ~20 | 55-100 % of the equity premium | r3 (NFP day), r19 T1 (Hu et al.), r20-r21 (FOMC) | drop: tested |
| L32 | central-bank decisions and interventions: C0559 C1300 (BoE), C0427 (BoC), C1091, Kearns & Manners 2006 | policy news | surprise-dependent / lean against moves | FX | n/r | r10 B, r11 F, r20, r21; interventions too rare | drop |
| L33 | FX macro news: C0571 (AUD consumer-sentiment asymmetry), Andersen et al. 2003, Evans & Lyons 2005/2008, Faust et al. 2007 | surprise impact, order-flow continuation | surprise-dependent | FX | n/r | r10 E2, r11 F3, r15 V7; predictable surprises are stream B's | drop |
| L34 | turn-of-year small caps (C0058, C2544, C2561) | tax-loss selling | small minus large around 31 Dec | US2000 (not in the 26) | gone after 1993 | - | drop |
| L35 | microstructure classics named in the brief: Evans & Lyons 2002, Lyons 1995, Payne 2003, Bjønnes & Rime 2005, Moore & Payne 2011, Cotter & Dowd (C0469/C0517), Ito, Lyons & Melvin 1998, Ito & Hashimoto 2006, Andersen & Bollerslev 1998, Admati & Pfleiderer 1988, Bessembinder 1994, Fischer & Ranaldo 2011, Kaul & Sapp 2006, Menkhoff et al. 2012 | order flow, dealer inventory, activity, spreads | no fixed side without dealer or order-flow data; volatility / volume / spreads; one event (Y2K); monthly momentum | - | - | r17 Y (price-only order flow); r7 D, r11 G (momentum) | drop: no side or data |
| L36 | FX gaps and weekend overreaction: C1228 (Caporale & Plastun 2017, gaps exploitable in FX), C0725 (weekend overreaction, spot FX) | weekend information / liquidity | fade the gap / Friday move | FX, ~5-50 | n/r | r19 T7 (Dao et al.: real in PRE, gone since 2016); r23 N1 (daily reopen gap below cost) | drop: tested |
| L37 | Japanese / Asian weekday (Tuesday) effects: C0009 C0187 C0617 C1686 C1901 | time-zone lag behind the US Monday | Tuesday low | JP225, AUS200 | n/r; Japanese Tuesday effect disappeared (C1686) | r11 H by weekday; r19 T4 | drop: tested |
| L38 | data-snooping caution: Sullivan, Timmermann & White 1998 (C0412), C1918 | - | calendar effects not significant after correcting for the search | - | - | - | supports the declared-only rule |
| L39 | emerging-market calendar studies (230 index rows; FX rows TRY, TWD, NGN, ZAR, INR, CLP) | - | - | not in IC's 26 | - | - | drop (EM FX is stream A's route) |

## After Declaration 1's numbers (information only; written 2026-10-17 19:48 UTC; nothing here is a candidate)
- Declaration 1 results: every MON cell fails; BAR-i pooled is real at mid in IS (+1.20 bp, t 2.72) but below cost
  (net -1.30 / -0.92) and matched by its half-level placebo in IS; BAR-d reverses. Details in STREAM_C.md.
- The declared information row XAUUSD BAR-i on PRE (declared 19:33:56, computed 19:36:25): mid +3.50 bp (t 4.86),
  12/12 years positive at mid; $5 placebo +1.31 (t 1.79). PRE is an unseen era for the gold leg.
- **Post hoc** (chosen after seeing the per-symbol rows): the gold leg by UTC session. The continuation sits in
  12:00-17:00 UTC: net PRE +2.83 (t 2.15), IS +3.10 (t 2.16), VAL +3.23 (t 2.17), placebo ~0, random control 100 %.
  Found after looking, so it cannot become a candidate this round (round 23 rule); it is reported in STREAM_C.md as a
  lead with an exact rule for data that nobody has seen.
- No Declaration 2: the rest of the census (L1-L39) and the lore map add no untested family with a side from the source
  (lore section below).

## Lore map (non-English practitioner sources; helper census 2026-10-17 19:09-19:48 UTC, file `r25/C/lit/lore/lore_map.md`)
71 web searches run (ja 39, zh 14, ko 7, de 11) plus 10 not run (the session's shared search budget ran out) and 19
direct page opens; 80 unique pages, 59 read (2 PDFs converted locally). 59 distinct claims: A (side + codable window +
mechanism) 12, B 27, C (vague) 20; 14 Tokyo-fix / gotobi / JPY 23:00-02:00 UTC claims listed as excluded (C3's).

| lore rows | claim | decision |
|---|---|---|
| JA-01, JA-02, JA-03 | month-end London 16:00 fix: USD bought (JA-01) / yen bought (JA-02); side depends on the month's equity moves | tested: r3 F1, r12 I (conditional on the US month), r14 Q |
| JA-04 | EURJPY short in the hour before the 16:00 fix on Tuesdays (MT4 2015-24; Tuesday picked after looking) | tested: r12 I 15:00-16:00 windows, r15 S WM/R +-30 min by weekday, r13 M |
| JA-05..JA-08 | Diamond ZAi day-of-month candle frequencies (20 years, every day x ~20 pairs) | data-mined; calendar days scanned in r18 B (FX, gold) |
| JA-09, JA-10, JA-11, JA-13, JA-32, JA-35 | Aug 15 redemptions, Golden Week yen surge, late-March repatriation, year-end USD, 掉尾の一振 (Nikkei last 5 days of the year) | 1 event a year (power); r13 N fiscal year-ends, r16 W redemptions, r10 B holidays, r24 B turn of year |
| JA-14, JA-28 | NY 10:00 / Tokyo 15:00 option cuts | no fixed side; r10 D1 pinning, r15 S |
| JA-15 | Monday gap fade | tested: r19 T7, r3 (JPY leg in C3's zone) |
| JA-16 | USDJPY firm in US payroll weeks ("recent tendency", 2014) | no mechanism; 12 a year, IS t >= 2 needs >= ~30 bp a week on a ~120 bp weekly sd; not declared |
| JA-17 | Mrs Watanabe lunch-time yen selling 12:00-13:00 JST (03:00-04:00 UTC) | clock window scanned: r13 M (USDJPY every 15-min start, TOK clock, PRE) |
| JA-18, JA-19, JA-20 | yen weak in Tokyo hours / NLI 4-h blocks / Tokyo vs overseas sessions | home-hours and clock: r10, r13 M (outside 23:00-02:00 UTC) |
| JA-21 | **Nikkei first TSE business day up, last business day down**: 積立 (regular investment plans) and 持株会 (employee share plans) buy on the first day; investors trim to target weights on the last (THE GOLD ONLINE, なのなの, 2024-03-25; Nikkei averages 2001-12 and 2013-23) | **declared: JPN (Declaration 2)**; never tested in this form (swing v2 tested L&S turn of month, long on the last day, pooled indices; r3 calendar windows reached only the Tokyo morning) |
| JA-22, JA-23, JA-31 | Nikkei month-end down (conflicts with JA-21), the 11th up, Monday down | no mechanism / data-mined; weekday scans r11 H |
| JA-24, JA-25, JA-26 | SQ close vs SQ value -> next week; "phantom SQ" (refuted by its own source, 36 events) | r20 G (SQ), 12 a year, no fixed side |
| JA-27 | BoJ ETF afternoon buying after a TOPIX morning drop | programme ended 2024-03 (r22 R9) |
| JA-29, JA-30, JA-33, JA-34 | London arrival, after BoJ meetings, AUD on the PBoC fix, retail gold at night | no side / CB events r10-r21 / r7 B PBoC fix surprise, r4 CNY 09:15 benchmark |
| ZH-01..ZH-05 | BTC weekend crashes, gold session hours, HK closing auction, EIA Wednesdays, HSI settlement | grade C (no side) |
| KO-01..KO-05 | 월말 네고 (month-end exporter USD sales), April dividend repatriation, KOSPI expiry, Seoul open | USDKRW / KOSPI200 not in the 26 (stream A's route); or grade C |
| DE-01 | DAX "down Friday, down Monday" -> Tuesday reversal (no threshold) | reversal family; r19 T3 (DE40 wrong side), r2/r7/r11 |
| DE-02, DE-03 | weekday effects (per-mille), S&P Monday | weekday scans; gone (its own source) |
| DE-04, DE-05, DE-06 | DAX overnight up, follow the first 15-min candle, gap fill | r3 night premium; r12 K / r15 V / r17 Z opens and intraday momentum; r8 X2d |
| DE-07, DE-08, DE-09 | after the big expiry, Hexensabbat, window dressing | r20 G, r23 P5/P6; 4 a year |
| DE-10, DE-11, DE-12 | DAX / S&P turn of month, "Ultimo" strategy (8-9 days) | tested (swing v2, r3, r19 T2); DE-11 > 5 days |
| DE-13, DE-14 | Friday oil intraday (times not visible), holidays | grade C |

## Declaration 2 (2026-10-17 19:53:57 UTC), before any JPN return was computed
Family **JPN** (lore JA-21). Side and window from the source: Nikkei up on the first TSE business day of a month, down
on the last. Note: the source's own evidence (2001-23) overlaps IS/VAL, so IS/VAL are not out of sample for the claim,
only for this repo; the claim conflicts with JA-22 (month-end into month-start down).
- Symbol JP225. TSE business days = weekdays not in `holidays.JapanExchange` (public holidays and 31 Dec - 3 Jan).
  Close clock 15:00 JST (06:00 UTC) until 2024-11-04 and 15:30 JST (06:30 UTC) from 2024-11-05; the close price =
  close of the bar ending at the clock; fills one minute after the signal clock.
- **JPN-a**: long from 1 minute after the close of the last TSE business day of month m-1 to the close of the first
  TSE business day of month m.
- **JPN-b**: short from 1 minute after the close of the second-to-last TSE business day of month m to the close of the
  last TSE business day of month m.
- **JPN-ab (primary)**: JPN-a and JPN-b pooled (24 trades a year).
- Costs: half spread at both fills; financing with the JPY rate (local FRED IRSTCI01JPM156N) and round 7's markups
  (long pays (r + 5.3 %)/360, short receives (r - 3.9 %)/360 per night; Friday = 3 nights). x1.5 spread and +1 minute.
- Eras IS 2016-21 (by entry), VAL 2022-24. Expected trades: 12 + 12 a year (IS ~72 + 72, VAL ~36 + 36).
- Random control (500 seeds, same count and era): JPN-a random TSE days long (close to next close); JPN-b random TSE
  days short; JPN-ab the two pooled.
- Cells added: 3 (total declared in stream C: K = 10; max |t| of 10 normals: median ~1.83, 95th ~2.80).

## After Declaration 2's numbers (run 2026-10-17 19:55:00 UTC; information)
- JPN-ab: IS net +22.48 bp (t 1.96), VAL +0.56 (t 0.04), +1 minute in VAL -1.81: fails (DEMO needs IS net t >= 2.0,
  and VAL is ~0). JPN-a IS +20.5 (t 1.19) / VAL +11.8; JPN-b IS +24.4 (t 1.61) / VAL -10.3. Details in STREAM_C.md.
- Chance over the 10 declared cells: max |t| of 10 normals median 1.83 / 95th 2.81; shared sign-flip null 1.73 / 2.75;
  best declared |t_IS mid| 2.72 (BAR-i).
- Semantic Scholar final tally: 18 attempts 19:08-19:53 UTC, 2 answered (F05, F10), 16 HTTP 429; 200 records, 149 not
  already harvested, 16 past the filter, none kept (off-topic, activity only, or non-listed markets).
- No further declaration: no candidate in this stream; no PREREG_DRAFT.
