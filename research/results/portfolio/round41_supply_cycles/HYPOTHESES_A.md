# Round 41 stream A hypotheses: sovereign auction supply cycles (US, JGB, Bund)

Declared 2026-10-30 04:38 UTC (`date -u` 04:37:21 just before writing), before any price was joined to an auction.
Brief: [BRIEF.md](BRIEF.md) row A; shared rules from round37_forced_flows/BRIEF.md. Scripts and data:
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r41/A/`.

## Sources (fetched 04:31-04:34 UTC, 8 requests, all logged in web/requests.log)
- US: fiscaldata.treasury.gov `v1/accounting/od/auctions_query`, security_type Note / Bond, auction_date
  2003-06-01..2024-12-31 (the request itself stops at 2024-12-31): 1,776 rows incl. TIPS and FRNs. FRNs dropped (no
  duration). Fields used: auction date, original term, TIPS flag, offering amount, issue / maturity, high yield,
  bid-to-cover, primary-dealer accepted / competitive accepted, competitive closing time (13:00 ET; 11:30 ET on early
  close days; null before 2008 -> 13:00 ET). When-issued yields are not public free, so no US tail.
- Japan: MoF `english/policy/jgbs/auction/past_auction_results/Auction_Results_for_JGBs.xls` (BIFF8, parsed by a
  stdlib reader). Sheets 2Y, 5Y, 10Y, 20Y, 30Y, 40Y, 10Y inflation-indexed, GX5, GX10. Dropped: 15Y floater, 4Y / 6Y /
  3Y discount (pre-2004), bills, liquidity-enhancement auctions (separate file, off-the-run, not fetched). Tail = average
  price - lowest accepted price (40Y is single-price: no tail). Bid-to-cover = competitive bids / accepted.
- Germany: Finanzagentur `emissionshistorie_en.xlsx` ("Auction results since 1999"). Kept Process = "Auc", dropped
  Bubills and secondary-market sales ("OH"). Bund 10/15/30Y, Bobl, Schatz, 7Y, ILB, Green. Tail = weighted average
  price - lowest accepted price; bid-to-cover as published.
- The JGB and Bund files contain 2025-26 rows; they are dropped at parse (`parse.py`, assert max date <= 2024-12-31)
  before anything is printed.
- Prices: IC M1 2016-2024 (cut ts < 1735689600000 at load) for USDJPY, EURUSD, EURJPY, XAUUSD, US500, DE40, JP225;
  PRE 2004-2015: Dukascopy M1 bid for USDJPY, EURUSD, EURJPY (duka/m1) and XAUUSD (duka/m1c); no PRE for indices.

## Event counts (auction days per year, after merging same-day auctions; 2016-24)
US ~79-93, JP ~69-75, DE ~51-65: ~210 auction days a year, ~50 independent weeks per country. PRE: US 42-84
(2004-08 thin: TIPS / 20Y / 7Y absent; 3Y absent 2008-), JP 55-69, DE 22-50.

## Power arithmetic (before any return)
- LYZ 2013 find 10Y yields up ~2-3 bp from day -5 to the auction and down after. With USDJPY's ~3-4 bp per bp of
  10Y yield, a full transfer is ~6-12 bp per 5-day window per auction day. 5-day sd of USDJPY ~120 bp -> per-trade
  Sharpe ~0.05-0.10. US PRE-5 has ~85 trades a year but windows overlap (~1.7 open on average), so the independent unit
  is the day: daily Sharpe ~0.02-0.04 at full transfer.
- LIVE needs HOLD power 3: with ~436 HOLD trading days per pair a daily Sharpe of 0.144 (~8 bp/day on USDJPY), about
  4-8x the literature size. Pooling 10 country-symbol pairs that are partly correlated gains at most ~2x. **LIVE is
  out of reach for F1 / F2 unless the effect is several times LYZ's size**; DEMO (IS t >= 2) needs daily Sharpe ~0.05
  per pair (~3 bp/day USDJPY), the top of the full-transfer range.
- F3 (result surprise, |W| >= 1): ~25 days a year per country, ~75 total. A 3-hour USDJPY window has sd ~25 bp and
  IC costs ~1.5-2 bp with commission. LIVE would need per-trade Sharpe 3/sqrt(130) = 0.26 (~6.5 bp net per trade);
  DEMO needs IS t >= 2 on ~150 IS trades per pair: Sharpe 0.16 (~4 bp net). Rounds 25-26 found releases priced in
  the first minute, so expect less than that. Bar reachable: DEMO at most.

## Mechanism and fixed sides
Dealers absorb scheduled supply with limited risk capacity, so local yields rise into an auction and fall after
(Lou, Yan & Zhang 2013 RFS 26(12); Beetsma, Giuliodori, de Jong & Widijanto 2016 JIMF for euro-area auctions;
Fleming & Rosenberg 2008). A pure supply (term-premium) shock with no growth news maps to: the local currency up,
the local equity index down (discount rate), gold down for US real yields. "High-local-yield side" (+1 = long):
| country | USDJPY | EURUSD | EURJPY | XAUUSD | US500 | JP225 | DE40 |
|---|---|---|---|---|---|---|---|
| US | +1 | -1 | | -1 | -1 | | |
| JP | -1 | | -1 | | | -1 | |
| DE | | +1 | +1 | | | | -1 |
10 country-symbol pairs. Sides are not chosen on IS.

## Clocks
Result times (local): US = competitive closing time (13:00 ET, 11:30 ET early-close days); JP = 12:35 JST (MoF
release; 12:45 assumed in older years, so entries after results use 12:50); DE = 11:30 bid deadline, results ~11:35
(entries after results use 11:50 Berlin). "Pre" exits are 5 minutes before the deadline (US 12:55 ET, JP 12:25 JST,
DE 11:25 Berlin) to avoid the release minute and the pre-release spread. Business days: NYSE (US), Japan holidays +
Dec 31-Jan 3 (JP), TARGET (DE), weekdays only. Fills: signal known at the clock, fill at the close of the bar starting
at the clock (one minute later); buy ask / sell bid; FX and XAU +0.6 bp commission; swap from research/swing/rates.py
(indices / gold included); variants spread x1.5 and +1 minute on both legs.

## Supply size (causal)
DV01 of an auction = offering amount of the previous auction of the same tenor (known weeks ahead) x modified
duration (par bond, remaining maturity, previous high yield; TIPS on real yield). Auction-day DV01 = sum over the
day. Relative size z = auction-day DV01 / median of the country's previous 50 auction days. Unit lot
u = clip(z, 0.5, 2) ("sized"); "top" = z above the 66.7th percentile of the previous 50 auction days, unit 1.

## Families and cells
**F1 concession / reversal (per auction day).**
- PRE5: enter at the pre-exit clock on business day -5, exit at the pre-exit clock on the auction day, high-local-yield side.
- PRE3: same from day -3.
- POST3: enter at the post-entry clock (US 13:15 ET, JP 12:50 JST, DE 11:50 Berlin) on the auction day, exit at the
  same clock on business day +3, low-local-yield side (reversal).
- CYC: PRE5 and POST3 as one book.
- x2 sizes (sized, top) x 10 pairs = 80 symbol cells. Book cap: a new trade is skipped while 3 of the cell are open.
**F2 auction-week clusters.** Week DV01 = sum of auction-day DV01 in a Mon-Fri week; "heavy" = above the 66.7th
percentile of the previous 52 weeks. Named clusters: US refunding weeks (3Y, 10Y and 30Y in one week), JP super-long
weeks (a 30Y or 40Y auction), DE long weeks (a 15Y or 30Y Bund / ILB-30 auction).
- WPRE: enter at the pre-exit clock on the business day before the week's first auction (moved later if needed so the
  hold is <= 120 h), exit at the pre-exit clock on the week's last auction day; high-local-yield side.
- WPOST: enter at the post-entry clock on the week's last auction day, exit +3 business days; low-local-yield side.
- x2 sets (heavy, named) x 10 pairs = 40 cells.
**F3 result surprise, drift after the first 15 minutes.** Per auction: z of bid-to-cover, of the dealer share (US) and of
the tail (JP, DE) vs the previous 6 auctions of the same tenor (>= 4 needed). Weakness W = (z_dealer - z_btc) / 2 (US),
(z_tail - z_btc) / 2 (JP, DE; 40Y: -z_btc). Day W = DV01-weighted mean over the day's auctions. Trade when |W| >= 1:
side = sign(W) x high-local-yield side (weak auction -> higher yields). Entry at the post-entry clock; exits H3 =
entry + 3 h, D1 = same clock next business day. 2 x 10 = 20 cells.

**Pooled cells** (reported with the symbol cells, counted in the benchmark): for every family variant, the country
pool (its pairs, mean per trade, clustered by UTC day) and the ALL pool (10 pairs). Primary (one headline cell):
**F1 CYC sized, ALL pool.**

Cells: 140 symbol cells + 56 pooled (F1 8 x 4 pools, F2 4 x 4, F3 2 x 4) = 196 counted. Chance: max |t| of 196
normals (95th percentile ~3.6); shared sign-flip-per-week null for the primary.

## Grading
- Eras: PRE 2004-15 (FX + XAU only, Dukascopy bid at mid, cost = the cell's IS 2016-17 mean cost + 0.6 bp), IS
  2016-21, VAL 2022-24. HOLD not loaded.
- t clustered by UTC day on the book's daily net (each trade's mid split at UTC midnights; cost on the entry and exit
  days). Per-trade mean net, years positive, VAL / IS ratio, x1.5 and +1 min.
- Random-entry control (>= 200 seeds): each trade moved to a random business day of the same weekday and era (F3:
  a day that is not an auction day of that country), same clock, hold, side and unit; fraction of seeds whose mean
  net is below the observed.
- Power: per-trade Sharpe x sqrt(expected HOLD trades) and daily Sharpe x sqrt(expected HOLD active days); the lower
  is quoted. Results reported with and without 2020-03/04.
- LIVE / DEMO bars from research/PROMPT.md, unchanged. Anything outside these cells is post hoc.

## Prior work, and how this differs
Round 22 R4: 10Y only, USDJPY / EURUSD, sign flipped PRE vs 2016-24 (PRE -26.8 bp, t -2.46; IS +17.9; VAL +29.4).
Here: all tenors, DV01-weighted, JGB and Bund for the first time, reversal leg and surprises. The US 10Y leg's
relative was seen in round 22; disclosed. Round 4 (auctions as features), round 13 (settlement days), round 21
(refunding as a Fed event) are not redone.

## Amendment 1 (2026-10-30 04:38 UTC, before any return was computed)
The user's 5-day hold limit is applied as 120 h (as in round 40 C). Business day -5 to day 0 always spans a weekend
(> 120 h), so: **PRE5 becomes PRE-L** = entry at the earliest business-day pre-exit clock that is <= 120 h before the
exit (3 business days for Mon-Thu auctions, 4 for Friday); **PRE3 becomes PRE2** = 2 business days before. POST3 and
WPOST exits move back to the latest business-day clock <= 120 h after entry when holidays would stretch them. CYC =
PRE-L + POST3. Nothing else changes.

## Amendment 2 (2026-10-30 04:39 UTC, before any return)
Germany: the file labels multi-ISIN auctions (most 15Y / 30Y Bund and ILB-30 supply since 2022) as process "M-A";
they are auctions and are now kept with "Auc". Syndications ("Syn") stay out (not on an auction calendar).

## Amendment 3 (2026-10-30 04:42 UTC, before any return)
Fill mechanics only: an exit clock that falls in a closed CFD minute (e.g. US500's 16:15-16:30 ET break hits F3 H3's
16:15 ET exit) fills at the last bar within 20 minutes before the clock. Entries unchanged.

## Family A2: intraday auction-day concession and same-day reversal (declared 2026-10-30 04:46 UTC)
F1-F3 were graded at ~04:44 UTC: no cell meets DEMO (0 cells with IS t >= 2 and VAL > 0; best IS t +1.80). Per the
brief, the stream moves to a related by-product of the same calendar, declared here before its returns.
- Mechanism: the concession is also built on the auction day itself, in the hours before the bid deadline, as
  dealers short the when-issued / hedge before taking down the issue, and unwinds in the afternoon (Nyborg &
  Sundaresan 1996 JFE on when-issued yields around US auctions; Fleming & Rosenberg 2008 on dealer inventory; LYZ 2013
  Fig. on day 0). Same "high-local-yield side" table as above. It differs from F1 (multi-day), from F3 (conditioned on
  the result) and from round 4's / round 12's clock scans (every day, not auction days against non-auction days).
- Windows (local; fill at the close of the bar starting at the clock): AM = high-local-yield side, PM = low-local-
  yield side (reversal).
  | country | AM | PM |
  |---|---|---|
  | US | 10:05 -> 12:55 ET (11:25 on early-close days) | 13:15 -> 15:55 ET (skip early-close days) |
  | JP | 09:05 -> 12:25 JST | 12:50 -> 14:55 JST |
  | DE | 09:05 -> 11:25 Berlin | 11:50 -> 14:25 Berlin |
- Day sets: "all" auction days (unit 1) and "top" DV01 days (as F1). Cells: 10 pairs x 2 windows x 2 sets = 40 symbol
  cells + 4 pools x 4 = 16 pooled = 56 counted (chance: max |t| of 56 normals, 95th percentile ~3.3). Primary: AM all,
  ALL pool.
- Random control: the same clocks on random business days of the same weekday and era that are not auction days of
  that country, 200 seeds. Also reported (not a cell): the auction-day minus non-auction-day difference.
- Power arithmetic: ~210 auction days a year; a 3-h window has sd ~15-25 bp (FX) and costs ~1.2-1.8 bp (FX incl.
  commission) / ~2-6 bp (indices). LIVE needs per-trade Sharpe 3/sqrt(1.73 x 210) = 0.16 pooled (~3 bp net per FX
  trade): above any literature size mapped to FX. DEMO needs IS t >= 2: pooled Sharpe ~0.056 (~1.1 bp net). Expected
  at full transfer: 0.5-1 bp yield intraday -> ~2-3 bp USDJPY mid, so DEMO is reachable only at the top of that range
  and only on the FX legs.
- Eras: IS, VAL as above; PRE on Dukascopy FX / XAU with the same cost rule. With and without 2020-03/04.
