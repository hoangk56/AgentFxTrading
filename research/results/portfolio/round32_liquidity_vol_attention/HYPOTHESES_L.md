# Round 32, stream L: hypotheses (US liquidity and fiscal cash flows)

Written 2026-10-27 18:50-19:05 UTC (`date -u` 18:50:50 at the start), **before any return was computed**. At this time
the three sources below were downloaded and parsed (cut at 2024-12-31 at parse); no series had been joined to a price.
Later additions are marked with their own `date -u` time.

## Sources and history depth (loaded, not joined to returns)
| source | what | history used | note |
|---|---|---|---|
| Daily Treasury Statement, api.fiscaldata.treasury.gov `v1/accounting/dts/operating_cash_balance` (query filtered `record_date:lte:2024-12-31`) | TGA closing balance, daily (USD mn) | 2005-10-03..2024-12-31, 4,835 days | Row names change: "Federal Reserve Account" to 2021-09-30, "Treasury General Account (TGA)" 2021-10-01..2022-04-15, "TGA Closing Balance" from 2022-04-18 (value in `open_today_bal`). Before 2008 most Treasury cash sat in Tax and Loan accounts at commercial banks (TGA ~$5 bn), so TGA swings did not move reserves: the reserve-drain mechanism exists from 2008-09 (SFP) and fully from 2012 (TT&L closed). |
| NY Fed reverse-repo results, markets.newyorkfed.org `api/rp/reverserepo/propositions/search.json` (year queries, to 2024-12-31) | total accepted per operation day (USD mn) | 2013-04-02..2024-12-31, 2,825 days | Material only at quarter-ends 2014-20 and from 2021-03 (peak > $2 tn 2022-23). |
| Fed H.4.1, federalreserve.gov DDP full-release zip (SDMX), parsed with a 2024-12-31 cut | Wednesday levels: total assets (RESPPA_N.WW = WALCL), TGA (RESPPLLDT_N.WW), reverse repos "others" (RESPPLLRD_N.WW, = ON RRP), total reverse repos, reserve balances (RESH4R_N.WW) | 2002-12-18..2024-12-25, 1,150 weeks | The zip holds 2025-26 values; they are dropped by the parser before anything is stored. |
| FRED | - | - | still unreachable from this Mac (request hung, stopped); not needed. |

## Publication lags (part of every rule)
- **Mark:** one decision minute per weekday, **15:00 UTC** (11:00 ET summer / 10:00 ET winter: US cash session, London
  open; avoids the 17:00 ET rollover). The signal uses data public before 15:00 UTC; the fill is at the close of the
  15:00 bar (bid / ask), i.e. signal at t, fill at t+1; variant +1 minute = the 15:01 bar. Exit at the 15:00 bar close
  h marks later (h = 1 or 5 weekday marks). A symbol without a bar starting 15:00..15:10 that day skips the trade.
- **DTS** for business day D is published ~16:00 ET on business day D+1 -> first usable mark: **15:00 UTC on business
  day D+2** (US federal business days).
- **RRP** result for day D at ~13:15 ET -> usable at **15:00 UTC on D+1**.
- **H.4.1** (Wednesday level W) published Thursday 16:30 ET -> usable at **15:00 UTC Friday W+2**; if Thursday W+1 is a
  US federal holiday (release moves to Friday) -> **Monday W+5**. The daily liquidity series (L2) uses the latest
  H.4.1 total assets usable at the mark.

## Eras, costs, tests (round 13 / 31 briefs)
- IS 2016-01..2021-12 (design), VAL 2022-01..2024-12 (check), PRE 2009-01..2015-12 where both the mechanism
  (TGA at the Fed) and prices exist: EURUSD, USDJPY (Dukascopy M1, bid; PRE cost = IC 2016-17 spread at the minute +
  0.6 bp) and XAUUSD (Dukascopy m1c). No index PRE.
- Symbols: US500, US30, USTEC, US2000 (IC bid-only zbars, spread = published 0.34 pt), XAUUSD, EURUSD, USDJPY.
- Costs: half the actual spread at entry and exit minute; 0.6 bp commission FX / gold; swap per rollover crossed
  (research.swing.rates.swap_frac_at; US2000 uses US500's; triple roll Wednesday for FX / gold, Friday for indices).
  Variants: spread x1.5, +1 minute.
- t: per trade, clustered by entry day (one-trade-a-day rules are already day clusters); 5-day holds use
  non-overlapping trades (weekly, or every 5th mark), so no overlap correction is needed.
- Random-entry control (>= 200 seeds): same count and hold, entries at a random weekday mark 08:00-19:00 UTC in the
  same era, **side recomputed** from the latest signal public at that random time. Signal null (multiple testing):
  circular shift of the signal series against prices by >= 26 weeks (500 draws), shared by every cell, max |t|.
- C3 correlation (daily P&L, IS + VAL) for any survivor.

## Power arithmetic (before building; round 10 frontier, round 16 STREAM_X)
1-day sd at the frontier: US500 94 bp, US30 95, USTEC 111, XAUUSD 84, EURUSD 43, USDJPY 50 (US2000 ~ 120 assumed).
A sign rule on a signal with correlation rho to the next return has per-trade Sharpe ~ 0.8 rho (E|z| = sqrt(2/pi)).
- **Daily rule (L2), 1-day hold, ~250 trades / yr / symbol:** LIVE needs net per-trade Sharpe >= 3 / sqrt(1.73 x
  250) = 0.144 -> about **+15 bp / trade on US500**, +7 bp on EURUSD, i.e. rho ~ 0.18. DEMO (IS t >= 2 over ~1,500
  IS days) needs Sharpe >= 0.052 -> rho ~ 0.065.
- **Weekly rule (L1), 5-day hold, ~50 trades / yr:** LIVE needs Sharpe >= 3 / sqrt(1.73 x 52) = 0.316 -> **~66 bp +
  ~12 bp cost and swap on US500 (5-day sd ~210 bp)**, ~30 bp on EURUSD, rho ~ 0.4. DEMO needs IS t >= 2 over ~310
  weeks -> Sharpe 0.114, rho ~ 0.14.
- Pooling the four index CFDs does not help (daily correlation ~0.9); a basket with gold and USD adds at most a
  factor ~1.3 in Sharpe if the legs were independent.
- **What the source implies.** The "net liquidity = WALCL - TGA - RRP" thesis (practitioner charts 2021-23; e.g.
  the widely shared "Fed net liquidity vs S&P 500" plots) is a correlation of **levels** in a trending 2020-22 sample,
  which says nothing about 1-5 day changes; the academic evidence is on reserves and money markets (Afonso et al.
  2020 repo spike; Correa, Du & Liao 2020 on the dollar basis), not on index returns at days. My prior for rho at
  1-5 days is <= 0.05: power at that size is ~0.8 (daily) / ~0.7 (weekly). **LIVE needs an effect ~3-4x my prior**;
  DEMO is reachable only if rho is near the top of the plausible range. The stream is a check that the effect is
  absent, unless the data say otherwise.

## Hypotheses (side fixed from the mechanism; "risk side" = long US500 / US30 / USTEC / US2000, long XAUUSD, long
## EURUSD, short USDJPY)
Mechanism common to all: reserves added to the banking system (Fed asset purchases, TGA drawdown, RRP drawdown) are
cash that dealers / funds must place; practitioners claim it flows into risk assets and weakens the dollar. A drain
(TGA rebuild, RRP inflow, QT) does the opposite. USD side: more dollar liquidity -> weaker USD (the practitioner
"liquidity vs DXY" link); for USDJPY this is declared short USDJPY on liquidity added, although a risk-on yen sale
would argue the other way: **declared side short USDJPY, fixed now**.

### L1 Weekly net liquidity (H.4.1)
- NL_W = total assets - TGA - reverse repos "others" (Wednesday levels). x_W = (NL_W - NL_{W-1}) / sd of the 52
  previous weekly changes (causal; first 52 weeks dropped).
- Entry at the first usable mark (Friday 15:00 UTC usually), risk side if x > 0, opposite if x < 0.
- Cells: L1a every week, hold 1 mark and 5 marks (non-overlapping by construction); L1b only |x| > 1, same holds;
  7 symbols + 1 equal-weight basket (mean of the 7 signed legs, one number per event) -> 2 rules x 2 holds x 8 = **32
  cells**. Threshold 1 fixed now (not tuned).
- Information (not cells): the same with each component alone (Δassets, -ΔTGA, -ΔRRP) on the basket; results with
  and without 2020-03..2020-06.

### L2 Daily Treasury / RRP liquidity flow (DTS + RRP)
- y_D = -(ΔTGA_D + ΔRRP_D) in USD mn, the reserve impact of Treasury and RRP for business day D (Fed assets move
  weekly and slowly; they are left out of the daily flow, H.4.1 handles them in L1). Two windows: k = 1 (day D) and
  k = 5 (sum of the 5 business days ending D). z = y / sd of the previous 250 values of the same window (causal).
- Known at the mark on D+2 (DTS lag); RRP before 2013-04 = 0.
- Rule: risk side if z > 0, opposite if z < 0. k = 1 -> hold 1 mark, every mark; k = 5 -> hold 5 marks,
  non-overlapping (every 5th mark from the first IS mark).
- Cells: 2 windows x 8 (7 symbols + basket) = **16 cells**.

### L3 Large Treasury drains / injections (tail of L2)
- As L2, but trade only when |z| > 1.5 (fixed now). This is the realised-dose version of round 13's scheduled
  settlement / tax days: the DTS shows the actual drain whatever caused it (taxes, net issuance, large payments).
- Cells: 2 windows x 8 = **16 cells**.

### L4 Debt-ceiling TGA rebuild (information only: too few events for the bar)
- After a debt-limit suspension / increase that ends extraordinary measures, Treasury rebuilds the TGA by bill
  issuance (the 2023 "liquidity drain" narrative). Events (resolution dates, public law): 2017-09-08, 2018-02-09,
  2019-08-02, 2021-10-14 (temporary +$480 bn), 2021-12-16, 2023-06-03 (PRE: 2013-10-17, 2014-02-15, 2015-11-02).
- Rule: opposite of the risk side (short indices, short gold, short EURUSD, long USDJPY) from the first mark after
  the resolution, hold 5 marks; also the 5 marks starting 10 business days later. 5 IS events, 1 VAL: **no grade**,
  reported as information.

### L5 Reserve-scarcity conditioning of L2 (Round 22 TRIAGE R7; low prior)
- L2 k = 5 basket, split by whether reserve balances (latest H.4.1 usable) are below their trailing 3-year median.
  Hypothesis: the flow matters only when reserves are scarce. Cells: **2** (scarce / ample, basket).

### L6 RRP alone, 2021-03..2024 (information only: IS has 10 months of a non-zero RRP)
- -ΔRRP over 5 days (z as in L2), risk side when RRP falls. Cannot meet the IS bar; reported for the record.

**Total graded cells: 32 + 16 + 16 + 2 = 66.** Chance: max |t| of 66 normals p95 ~ 3.2; the circular-shift null is the
binding benchmark. HOLD stays closed; no PREREG_DRAFT unless a cell meets DEMO / LIVE on IS / VAL.

## Added 2026-10-27 18:57 UTC (`date -u`), after L1-L6 were computed and found null, before any L7 number
The first three sources gave nothing on the registered sides (STREAM_L.md). Keeping going inside the DTS:

### L7 Withheld-tax nowcast (DTS federal tax deposits)
- Source: DTS `v1/accounting/dts/federal_tax_deposits`, "Withheld Income and Employment Taxes", 2005-10-03..
  2023-02-13 (the table stops), spliced with `deposits_withdrawals_operating_cash` "Taxes - Withheld Individual/FICA"
  2023-02-14..2024-12-31 (monthly totals continuous across the splice: Jan-23 288 bn old, Feb-23 264, Mar-23 313 new).
  Withheld taxes are one of the inputs of the NY Fed Weekly Economic Index (Lewis, Mertens & Stock 2020): a real-time
  read of wage income, public each day with the DTS lag.
- Mechanism: an acceleration of withheld taxes is stronger labour income before the monthly data show it; if the
  market under-reacts to this slow, noisy nowcast, US equities and the USD drift up, gold (real rates) down.
- Signal: G_D = sum of withheld deposits over the 28 calendar days ending D / the same over the 28 days ending D - 364,
  minus 1; s_D = G_D - G_{D-20 business days}; z = s / sd of the previous 250 values. Usable at the mark on D+2.
- Side (fixed now): z > 0 -> long US500 / US30 / USTEC / US2000, **short XAUUSD, short EURUSD, long USDJPY**;
  z < 0 the opposite.
- Rules: (a) every mark, hold 1; (b) every 5th mark (non-overlapping), hold 5. 7 symbols + basket -> **16 cells**.
- Prior: round 25 found that leading indicators are priced before the release; a nowcast this slow is unlikely to
  carry a 1-5 day edge. Expected rho <= 0.03, power < 0.5 at that size. Total graded cells now 66 + 16 = 82.
