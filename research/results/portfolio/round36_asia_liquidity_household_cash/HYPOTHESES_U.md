# Round 36, stream U hypotheses: US household cash payments (Daily Treasury Statement) -> BTCUSD, ETHUSD, US2000, USTEC, US500

Written 2026-10-28 01:50 UTC (`date -u`), **before any return was computed**. Loaded so far (no prices joined): DTS
withdrawals 2005-10-03..2024-12-31 (query cut `record_date:lte:2024-12-31`) and the IC 19:30 / 19:31 / 15:00 UTC mark
prices (bid / ask, ts < 2025-01-01) with their spreads. Unconditional 1-day sds below are round 10's table
(STREAM_D_outputs.md), not new numbers.

## Data (what the DTS shows, no returns)
Daily EFT withdrawals in USD mn (`deposits_withdrawals_operating_cash`, 24 pages, 238,748 rows). Row names change
and are spliced:
- individual refunds: "IRS Tax Refunds Individual (EFT)" (an "Other Withdrawals" sub-row until 2012-09) ->
  "Taxes - Individual Tax Refunds (EFT)" from 2023-02-14;
- Social Security: "Social Security Benefits (EFT)" -> "SSA - Benefits Payments" from 2021-07-19;
- SSI: "Supple. Security Income Benefits (EFT)" -> "SSA - Supplemental Security Income" from 2021-07-19;
- EIP: "IRS - Economic Impact Payments (EFT)" exists only from 2020-12-24. **EIP round 1 (April-May 2020) is booked
  inside the individual-refund row** (2020-04-15: refunds $150.1 bn);
- advance child tax credit 2021-07-15..2021-12 (monthly on the 15th); unemployment benefits; VA benefits.
- Sizes: SS ~$800-1,300 bn a year, paid on the 3rd (~$22-25 bn) and the 2nd / 3rd / 4th Wednesdays (~$15 bn each in
  2016, ~$27 bn in 2024); SSI ~$4.3 bn on the 1st; individual refunds ~$260-340 bn a year (2020: $489 bn incl. EIP1),
  64-74 % of it paid 15 Feb-30 Apr.
- **Refund calendar.** In season, the IRS pays EFT refunds in a weekly cycle: Friday until 2011 (54 % of in-season
  refunds 2006-15 on Fridays), **Wednesday from 2012** (55 % IS, 49 % VAL on Wednesdays). The largest day of each year
  is the PATH-Act release of held EITC / ACTC refunds (2017-24: 22-27 Feb, $36-61 bn). Both are known in advance (IRS
  refund cycle chart; PATH-Act date announced in January).

## Mechanism and literature (side fixed here: LONG the risky asset when household cash arrives)
- Greenwood, Laarits & Wurgler (2023, RFS 36(10) 4082-4112, "Stock Market Stimulus"): EIP rounds 1 and 2 raised
  retail buying; high-retail-share portfolios (small caps, low price, Robinhood names) +5-7 % abnormal within days;
  value-weighted market ~0; **round 3 nothing**.
- Divakaruni & Zimmerman (Management Science 2024, 70(4); Cleveland Fed WP 21-13): spike in $1,200 BTC buys at EIP1;
  BTC-USD volume +3.8 %, price +0.6 % over the disbursement (WP: +7 bp); the trades were ~0.02 % of EIP dollars.
- Gelman, Kariv, Shapiro & Silverman (AER 2022): refunds are mostly spent (high MPC). Surveys: ~6 % of refund
  recipients say they invest it.
- Social Security goes to retirees with high MPC; not the Robinhood / crypto population.
- Side for every cell: **long** (cash in -> retail buys risky assets). No short cells.

## Publication time (part of the rule)
- DTS for day D is released ~16:00 ET on D+1 (20:00 UTC summer / 21:00 UTC winter). Realised-dose rules enter at the
  **19:30 UTC mark on D+2** (the first 19:30 mark after release in both DST regimes).
- Calendar rules use only the calendar (known years ahead): payment day P, entry at the 19:30 UTC mark of the previous
  IC trading day (P-1), so the hold covers the night the deposits post and P's US session.
- Clock: entry / exit at the 19:30 UTC M1 bar (bid / ask at the first bar at or after 19:30, within 10 min); US cash
  session is open at 19:30 UTC all year. +1 min check: both legs at 19:31.

## Hypotheses (65 graded cells)
Holds h = 1, 3, 5 IC trading days (exit at the 19:30 mark h marks after entry). h = 3 / 5: one trade at a time (a
signal while a trade is open is skipped; re-entry at an exit mark is allowed). Symbols: US500, USTEC, US2000, BTCUSD,
ETHUSD (5).
- **U1a SS Wednesdays** (2nd / 3rd / 4th Wednesday of each month; preceding business day if a federal holiday): long
  from 19:30 on P-1; h 1 / 3 / 5. 15 cells. ~36 entries a year (h 1). Not turn-of-month, so this is the clean SS dose.
- **U1b 1st / 3rd** (SSI + VA + federal retirement on the 1st, legacy SS on the 3rd; preceding business day): h 1 / 3.
  10 cells. ~24 entries a year. Overlaps the turn-of-month already tested (rounds 2-11): graded but flagged.
- **U2 realised refund dose:** R5(D) = individual refunds over DTS days D-4..D; signal if R5(D) > the 80th
  percentile of R5 over the previous 250 DTS days; entry 19:30 on D+2; h 1 / 3 / 5. 15 cells. ~50 signal days a
  year (clustered Feb-Apr).
- **U2s scheduled refund Wednesdays:** every Wednesday 15 Feb-30 Apr (preceding business day if a holiday), entry
  19:30 on P-1; h 1 / 3. 10 cells. ~11 a year. They are a subset of U1a-type days with a double dose (SS + refunds):
  dose-response check = U2s minus off-season SS Wednesdays (information).
- **U3 household cash surprise (all categories):** T5(D) = refunds + SS + SSI + EIP + CTC + unemployment + VA over
  D-4..D; x = ln(T5(D) / T5 one year earlier (5-DTS-day sum ending at the DTS day nearest D-365)); signal if x > its
  80th percentile over the previous 250 DTS days; entry 19:30 on D+2; h 1 / 3 / 5. 15 cells.
- **U4 EIP rounds (information only, 3 events):** first large EIP day of rounds 1-3 (from the DTS), entry at the
  scheduled IRS date (P-1 19:30) and at D+2; h 1 / 3 / 5. Not graded (3 events, 2020-21 only).

**EIP days and 2020-21.** EIP day = DTS day with EIP >= $1 bn, or 2020-04-10..2020-06-30 with refunds >= $5 bn (EIP1
booked as refunds). **The graded version is ex-EIP**: drop any trade whose signal window (D-4..D), or entry-to-exit
window, contains an EIP day or one of the 5 DTS days after it (EIPs are not a recurring flow). The full version is
reported. IS is also reported split 2016-19 / 2020-21.

## Eras, costs, statistics
- IS 2016-2021 (BTC from 2017-08-28, ETH from 2017-09-25: 4.3 years), VAL 2022-2024. PRE: no index data before 2016;
  BTC PRE 2011-04..2017-08 at mid from CoinMetrics PriceUSD (end-of-day reference; entry end of P-1 / D+1 for U2-U3),
  information only.
- Long fill at ask, exit at bid (actual IC spreads; US2000 bid + 0.34 pt). x1.5: 1.5 x the half spreads.
- Financing per rollover crossed (Friday x3): US500 / USTEC `swap_frac_at(sym, +1, ms)`; US2000 uses US500's; BTC and
  ETH -5 bp (round 31 C).
- t over trades (one trade per entry day per symbol, so day-clustered); basket = mean over the available symbols per
  entry day (information).
- Random control: 300 draws of the same number of entries at random IC trading days of the same era, same hold, same
  (long) side; share of draws whose mean net is below the cell's. Bars: LIVE >= 95 %, DEMO >= 90 %.
- Chance: shift every family's signal dates together by a random 20-230 IC trading days (circular in 2016-24), 300
  draws, recompute the 65 IS net t; report p50 / p95 of max |t|.
- Bars unchanged (PROMPT.md): LIVE IS t >= 2.5, VAL t >= 1.5, >= 2/3 years > 0, x1.5 and +1 min > 0, random >= 95 %,
  power at VAL size >= 3. DEMO IS t >= 2.0, VAL net > 0, random >= 90 %.

## Power arithmetic (first)
power = per-trade net Sharpe x sqrt(1.73 x trades a year); LIVE needs 3, DEMO's IS t 2 needs Sharpe x sqrt(IS n) >= 2.
1-day sd (round 10): US500 94 bp, USTEC 110, BTC 450; US2000 ~120, ETH ~600 (assumed). 5-day sd ~ x2.2.

| family | trades / yr | Sharpe for LIVE | LIVE edge US500 / US2000 / BTC (h 1) | Sharpe for DEMO (IS n) | DEMO edge US500 / BTC |
|---|---|---|---|---|---|
| U1a h1 | 36 | 0.38 | 36 / 45 / 170 bp | 0.14 (216; BTC 155: 0.16) | 13 / 72 bp |
| U1b h1 | 24 | 0.47 | 44 / 56 / 210 | 0.17 (144) | 16 / 85 |
| U2 h1 | ~50 | 0.32 | 30 / 39 / 145 | 0.12 (300) | 11 / 60 |
| U2s h1 | 11 | 0.69 | 65 / 83 / 310 | 0.25 (66) | 23 / 120 |
| U3 h1 | ~50 | 0.32 | 30 / 39 / 145 | 0.12 | 11 / 60 |
| h 5, one at a time | ~10-36 | 0.38-0.69 | 80-150 / 100-190 / 380-700 | | |

- Implied size: EIP1 was ~$150 bn in a day with VW-market effect ~0 and BTC +7-60 bp over the whole disbursement. A
  refund Wednesday ($10-40 bn) or an SS Wednesday ($15-28 bn, retirees) is 1/4-1/10 of that dose, to a population that
  mostly spends it. Expected per-trade edge: indices < 2 bp, US2000 maybe ~5-20 bp on the largest refund days, BTC
  < 10 bp. Expected power ~0.0-0.3 for every cell. **A LIVE pass would need an effect 10-30x what the literature
  implies; DEMO 3-10x.** Run anyway as briefed; it closes the family with a dose that no round has loaded.
- ETH: IC spreads 2018-20 are 99-264 bp (median at 19:30), so no ETH cell can pass IS; reported for VAL information.

## Amendment 2026-10-28 01:52 UTC (still before any return)
- Data check (no prices): the DTS books EIP2 on 2021-01-04 ($112 bn) and EIP3 on 2021-03-17 ($242 bn), while deposits
  were already posting on 2020-12-29/30 and 2021-03-12/13 (IRS press releases). The ex-EIP contamination window is
  therefore **5 DTS days before to 5 DTS days after** each EIP day (was: after only). EIP days found: 8 in 2020
  (2020-04-15..05-28, inside the refund row), 12 in 2021.
- The calendar built from the rule (preceding-business-day convention, `holidays.US`) matches 886 of the 890 DTS days
  with SS > $5 bn 2005-24 (the 4 misses are 2005 and one 2009 day).
- Signal counts (data only): U2 fires 45-56 DTS days a year (Feb-May), U3 21-96.

## Amendment 2, 2026-10-28 01:56 UTC (written after the IS / VAL results of the 65 cells; nothing below changes a registered cell)
- Results so far: no cell meets DEMO or LIVE. The best registered-side cell is U3 h3 USTEC (IS net t 1.90, VAL 2.26);
  U3 h3 US500 IS 1.35 / VAL 1.96.
- **PRE check of the registered rules on index closes 2007-2015 (information, mid only).** Source: FRED daily closes
  (NASDAQCOM, NASDAQ100; any free S&P 500 / Russell 2000 close series reachable without an account), requested with
  `coed=2015-12-31`. Same rules, unchanged parameters; daily closes are 16:00 ET, so: calendar rules enter at the close
  of P-1 and exit at the close h trading days later; DTS rules enter at the close of **D+2** (DTS is released ~16:00 ET
  on D+1, the same minute as the close, so D+1's close is not safe). PRE cost reference: IC 2016-17 median spread
  ~2 bp + ~2 bp a night swap. A rule is credible only if PRE mid is positive with t >= ~2 on the cell that led IS /
  VAL; this cannot promote any cell (IS bar unchanged).
- **Not run, by the power arithmetic:** quarterly estimated-tax deadlines (household cash out, ~4 events a year:
  LIVE needs a per-trade Sharpe >= 1.1, DEMO's IS t 2 needs >= 0.41; the pre-2023 DTS lumps individual non-withheld
  EFT payments into "Cash FTDs", so the dose is not measurable; round 13 N already found nothing on tax days);
  federal salary paydays (dose $5-8 bn, below the SS Wednesday dose that is null here).
