# PREREG DRAFT (not registered): short EURUSD on US coupon-auction mornings, 10:05 -> 12:55 ET

Written 2026-10-30 04:50 UTC by round 41 stream A. HOLD was not opened. **Recommendation: do not register.** The cell
meets the DEMO numbers on IS / VAL, but it is at the chance level for the cells tried, its VAL edge is ~0, and the
pre-written PRE era has the opposite sign (details below). The brief requires a draft whenever the numbers are met;
the lead decides.

## Rule (exactly as declared in HYPOTHESES_A.md, family A2, 04:46 UTC)
- Days: every US Treasury nominal / TIPS coupon auction day (fiscaldata `auctions_query`, Note / Bond, FRNs out),
  2Y / 3Y / 5Y / 7Y / 10Y / 20Y / 30Y and TIPS, with at least 20 earlier auction days for the size z (always true
  after 2004).
- Entry: sell EURUSD at the bid at the close of the bar starting 10:05 New York time (fill 10:06).
- Exit: buy at the ask at the close of the bar starting 12:55 ET (11:25 ET on SIFMA early-close days). No stop.
- One trade per auction day, 1 default lot; no swap (intraday). Cost: IC spread at both minutes + 0.6 bp commission.
- Side source: Lou, Yan & Zhang 2013 / Nyborg & Sundaresan 1996 (yields rise into the bid deadline) mapped to "US
  yields up -> USD up". Not chosen on IS.

## Numbers (IS 2016-21, VAL 2022-24; PRE = Dukascopy 2004-15 at the IS 2016-17 cost + 0.6 bp)
| era | n | mid bp (t) | net bp (t, day-clustered) | x1.5 / +1 min | years > 0 | random entries beaten | per-trade Sharpe |
|---|---|---|---|---|---|---|---|
| PRE | 800 | -0.74 (-0.82) | -2.00 (-2.20) | | 1 / 12 | | |
| IS | 501 | +2.80 (3.25) | +2.17 (2.51) | +2.15 / +2.02 | 6 / 6 | 100 % | 0.112 |
| VAL | 276 | +0.95 (0.71) | +0.33 (0.25) | +0.32 / +0.47 | 2 / 3 | 64 % | 0.015 |
Without 2020-03/04: IS +1.77 (t 2.19). VAL / IS = 0.15. Auction-day minus non-auction-day mid: IS +3.18, VAL +1.26 bp.
Daily correlation with the C3 gotobi basket: +0.02.

## Against it
- Chance: A2 has 56 counted cells (max |N| median 2.50, p95 3.32) and the stream 252 (median 2.99): IS t 2.51 is at
  the median of the best-of-56 null.
- PRE (the declared extra check) is negative: net t -2.20, 11 of 12 years < 0.
- VAL is ~0 net and fails the 90 % random control; only IS carries it.
- Its USDJPY twin (same mechanism, same window) fails IS (net t 1.25) though positive in VAL (2.15): the two pairs'
  dollar moves on auction mornings are 2016-24 only.
- Post hoc (information only): not month-end flows (rest-of-month auction days carry IS: mid +3.10, t 3.35) and
  present in every tenor group in IS, none consistently in VAL.

## If the lead still registers it
- Bar: DEMO. Expected HOLD trades: ~92 a year x 1.73 = ~159. Expected HOLD t: 0.19 at the VAL size, 1.41 at the IS
  size; power < 3, so never LIVE on HOLD alone.
- HOLD pass rule: net > 0 (DEMO rule: HOLD net < 0 -> drop).
- Demo: ~92 trades a year at 0.01 lot. Stop rule: after 60 demo trades, stop if the mean net is < 0 with t < -1.0.
- Promotion: HOLD + demo pooled net t >= 2.5.
- Cells tried before this one: 196 (F1-F3) + 56 (A2) = 252.
- Code: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r41/A/scripts/a2.py`
  (with `events.py`, `parse.py`, `lib.py`); hash it with `python -m research.tools.prereg_hashes` at registration.
