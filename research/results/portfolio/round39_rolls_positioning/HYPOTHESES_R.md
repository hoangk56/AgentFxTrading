# Round 39 stream R: hypotheses (scheduled futures-roll flows -> XTI, XBR, XNG)

Declared 2026-10-29 13:29 UTC (`date -u`), before any return of any cell below was computed. Data loaded so far:
IC M1 caches (cut at ts < 1735689600000 at load; only date ranges printed) and the EIA daily settlement json that
round 38 H parsed (CL1, CL2, NG1, NG2 to 2024-04-05, Brent spot; only counts and first / last dates printed).

## Prior work and how this differs
- Round 3 O1 (flow_search_2026-09-27.md): short XTI / XBR 12:00-14:29 ET on GSCI roll days (BD 5-9), intraday only;
  mid WTI -21 bp (t -2.0) IS / -12 (t -1.6) VAL, engine R +0.004 (t 0.2). That cell is not repeated. New here: a
  multi-day hold across the whole roll window (cost paid once), the pre-roll and post-roll legs, a check of which
  contract IC's CFD follows, and a PRE era 1995-2017 on exchange settlements.
- Round 6 (settlement / LETF momentum, EIA reports), round 13 (calendar rules), round 17 (gold settlement momentum),
  round 34 E (LETF dose), round 37 F (CME BTC expiry carry): different flows; nothing here reuses them.
- Round 23 P and round 25 C dropped the GSCI roll as "a calendar-spread trade IC cannot hold". That is the crux: the
  question here is whether the outright front contract carries enough of the pressure to be traded alone.

## Mechanism, sources, side and size implied
- S&P GSCI rolls WTI, Brent, Henry Hub gas every month from the nearby to the next contract over the 5th-9th GSCI
  business days, 20 % a day (S&P GSCI methodology; Mou 2011, SSRN 1716841). Bloomberg BCOM rolls on the 6th-10th
  business days in its roll months (BCOM methodology). USO (largest crude ETF) followed the near contract until two
  weeks before expiry and rolled on a single day until 2009-02, over four days after that (Bessembinder, Carrion,
  Tuttle & Venkataraman 2014 draft / 2016 JFE, "Predatory or sunshine trading?", section VII and footnote 32,
  fetched from cftc.gov). USO's 2020-04 restructuring (spreading holdings over several months) is taken from its
  2020 filings as described in the brief, not fetched; no cell depends on the USO schedule after 2020.
- All three sell the contract nearest to expiry (contract 1 in exchange data) and buy contract 2 during roughly
  business days 5-10 of every month. Index investors are long, so the flow is a calendar-spread trade: no net
  outright exposure changes.
- Size from the sources: BCTV measure the calendar spread (contract 2 minus contract 1) widening ahead of / during the
  USO roll by **25 bp per roll** (2006-12) and **38 bp per roll** in 2000-06 (GSCI era, footnote 34), then narrowing by
  **26 bp** after the roll; ~0 in the 1990s before index investing. Over 99 % of the temporary impact of an order
  imbalance in the expiring contract reverses within 10 minutes (resilient market). Mou 2011: front-running Sharpe up
  to 4.39 on the spread, 3.6 %/yr cost to index investors (~30 bp per roll), smaller as arbitrage capital grew.
  Stoll & Whaley 2010: little or no price effect around index roll dates.
- Implied outright size on the front contract: at most the spread move (if all of it sits on contract 1), more likely
  about half: **-10 to -25 bp over the roll window (short contract 1), +10 to +26 bp after it (long contract 1)**.
  These sides are fixed here and are not changed after any number is seen.

## Event count and power arithmetic (done before any return)
- Windows: 12 a year per commodity (GSCI monthly for WTI, Brent, gas; BCOM and pre-2020 USO fall on the same days).
  IC energies start 2018-01: IS 2018-21 = 48 windows per symbol, VAL 2022-24 = 36, HOLD 2025-01..2026-09 ~ 21.
- Outright sd per 5-trading-day window: WTI / Brent daily sd ~2.2-2.5 % -> ~500-560 bp; gas ~3.5-4 % -> ~800-900 bp
  (rough priors from general knowledge of the series, not from these files).
- Per-window Sharpe at the literature size: 25 / 530 ~ **0.05** for crude, 25 / 850 ~ 0.03 for gas (the gas spread
  effect would have to be several times crude's to matter).
- DEMO needs IS t >= 2.0 on 48 windows: per-window Sharpe 0.29, i.e. **~150 bp a window for crude, ~250 bp for gas**,
  6-10 times the whole calendar-spread move the literature reports. Expected IS t at the literature size: 0.05 x
  sqrt(48) = 0.35; P(IS t >= 2) ~ 5 %, the chance level. Pooling XTI + XBR (corr ~0.9) and XNG adds at most ~1.6x
  effective windows: expected t <= 0.45.
- LIVE needs HOLD power 3 on ~21 windows per symbol: per-window Sharpe 0.65 (~350 bp crude). Impossible.
- Daily legs (5 one-day trades per window) do not help: the same exposure, five times the spread cost.
- **Verdict from the arithmetic: DEMO and LIVE are out of reach for every roll cell at any size the literature
  supports; the stream stops after the falsification check below.** The check is kept small because its only
  purpose is to test the prior that the outright effect is <= ~40 bp; a result >= ~150 bp a window in PRE and IS
  would overturn the arithmetic, anything below confirms the stop.

## Business days and contracts
- Business day = weekday that is not an NYSE holiday (`holidays.financial_holidays('NYSE')`); BD k = k-th business
  day of the calendar month; BD0 = last business day of the previous month. For EIA data, business days = days with a
  CL1 (NG1) settlement.
- Contract 1 roll in EIA series: CL expiry = 3 business days before the 25th (or before the last business day
  preceding the 25th if the 25th is not a business day) of the month before delivery; NG expiry = 3 business days
  before the first calendar day of the delivery month. A window containing an expiry is dropped (should not happen
  for the windows below for CL; NG expires near month end).
- **Which contract IC's CFD follows (brief part 2), a price-level check, not a return:** on each EIA day 2018-01..
  2024-04, compare IC XTIUSD mid at the 14:29 ET minute close with CL1 and CL2 settlements; XNGUSD with NG1 / NG2.
  Tag the day "C1" if |IC - CL1| < |IC - CL2| and the gap to CL1 is below a third of |CL2 - CL1|, "C2" in the mirror
  case, else "?". IC's own switch dates = first day of each month on C2. XBRUSD: no Brent futures 1/2 series is
  available, so detect IC's Brent switch from jumps of the XBR - XTI mid gap at 14:29 ET on days when XTI did not
  switch (|jump| > 4 x median absolute daily change); if undetectable, say so and use the XTI rule as a proxy.
- Only windows in which the CFD is on contract 1 ("C1") on every day of the window are traded (the roll sells
  contract 1). If IC already follows contract 2 during BD 5-9, the window is dropped, not flipped.

## Cells (15 declared trade cells + 3 controls)
Entry / exit at the settlement minute: NYMEX 14:30 ET for WTI and gas (IC: mid at the close of the 14:29 ET bar,
fill at the next bar's open price is approximated by the 14:29 close; +1 minute variant = 14:30 bar close), ICE
Brent 19:30 London for XBR (19:29 London bar close). Holds are counted in trading days (5 trading days span 7
calendar days across a weekend; the ≤ 5-day reading is reported as the per-day breakdown).

| id | rule | side | symbols / data | eras |
|---|---|---|---|---|
| R1 | roll window: enter at BD4 settlement, exit at BD9 settlement | short contract 1 | XTI, XBR, XNG (IC); CL1, NG1 (EIA) | PRE 1995-99, 2000-11, 2012-17 (EIA, gross); IS 2018-21, VAL 2022-24 (IC) |
| R2 | after the roll: enter BD9 settlement, exit BD13 settlement | long contract 1 | same | same |
| R3 | pre-roll (front-runners sell contract 1 ahead of the index): enter BD0 settlement, exit BD4 settlement | short contract 1 | same | same |
| C | R1 calendar on controls without a roll-driven outright flow (gold rolls in GSCI only in even months, through COMEX, and GLD is physical; US500 has no monthly roll) | short | XAU, XAG, US500 (IC, 14:30 ET) | IS, VAL |

Mechanism check (not a trade, reported for context): the change of (CL2 - CL1) / CL1 over each window in EIA data,
which BCTV's 25-38 bp predicts.

Cells: 3 rules x 3 IC symbols = 9 IC cells, 3 x 2 = 6 EIA cells (PRE), total 15; controls 3. Chance benchmark: the
expected max |t| of 15 independent normals ~2.0 (crude cells are correlated, so fewer effective tests).

## Costs and fills (IC eras)
Round trip = half spread at entry minute + half at exit minute (actual IC ask - bid at those minutes), energies no
commission, metals 0.6 bp, swap -2.5 bp per night for XTI / XBR, -4 bp for XNG, -2 bp US500, metals from
research/swing/rates.py conventions (approximated at -1 bp a night), counted per calendar night held (whichever side),
spread x1.5 and +1 minute variants. t clustered by window (one trade per window per symbol, so plain t on windows;
the pooled crude book clusters XTI + XBR of the same month). Random-entry control (>= 200 seeds): same side, same
5-day hold, entry on random business days of the same months outside BD 0-13. 2020-03 / 2020-04 reported with and
without (XTI's April 2020 IC quotes are a known glitch).

## Related directions if the first construction fails (declared now, count first)
- R4 annual reweighting (GSCI / BCOM January, BD 6-10): 1 event a year, 4 in IS: DEMO impossible from the count
  (needs per-event Sharpe 1.0); not computed.
- R5 IC's own CFD roll (the day IC switches contract): a broker pricing / adjustment event, not a market flow, and
  IC's adjustment policy is not public in our data; only the switch dates are reported, no trade cell.
- R6 metals GSCI roll (gold even months, silver odd months): the gold calendar spread is a pure financing spread
  arbitraged against spot, implied outright pressure ~0; out of reach by the same arithmetic (gold 5-day sd ~200 bp,
  DEMO would need ~60 bp a window). Not computed.

## Addendum 2026-10-29 13:31 UTC (after the contract-tracking check, before any return)
The tracking check (price levels only, out/track.txt, out/xbrjump.txt) shows IC's XTIUSD is not on a single contract:
x = (IC - CL1) / (CL2 - CL1) at 14:29 ET runs from about -0.4 just after CL1 expiry to about +0.2..+0.5 just before
the next expiry (median -0.26 at BD4, -0.08 at BD9, +0.2 at BD13), i.e. a continuously interpolated / extrapolated
price whose weight sits on contract 1 through BD 0-13. XNGUSD sits on NG1 (median x -0.14..-0.04 at BD 1-13). XBRUSD
shows no switch jump in the XBR - XTI gap on any business day (big jumps spread evenly over BD 1-23), consistent with
the same continuous construction. So the declared per-day "C1" tag (|IC - C1| < |C2 - C1| / 3) is ill-posed for an
interpolated price on days with a small calendar spread (51 % of XTI days were "?").
Change, fixed now: the **primary** sample keeps every window (IC's exposure is dominated by contract 1 in BD 0-13 for
all three symbols); the declared tag filter (windows whose every day is tagged C1) is reported as a secondary variant.
Sides and windows unchanged. The interpolation itself adds a mechanical drift of IC's XTI vs CL1 of about
+0.18 x (CL2 - CL1) over BD4->BD9 (~ +5-10 bp in contango), which works against the short R1 and for the long R2; it is
part of what a CFD holder earns and is not removed.
