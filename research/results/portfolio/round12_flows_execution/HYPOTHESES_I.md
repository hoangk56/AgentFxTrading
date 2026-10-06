# Round 12, stream I: hypotheses (month-end equity-hedge rebalancing at the WM/R 16:00 London fix)

Written 2026-10-06 00:56-00:58 UTC, before any number of this stream was computed. Only literature was read before
writing. Data used later: the shared panel (2016-2024), IS 2016-01..2021-12, VAL 2022-01..2024-12. HOLD is never
loaded. There is no PRE check: the panel has no equity index before 2016 and fetching new price series is a user
decision (the paper's own sample, 2004-2012, plays that role).

## Sources read (and what they fix)

- Melvin & Prins (2015), J. Financial Markets 22, 50-72; working paper version (ECB FX workshop, Nov 2013), read in
  full. Mechanism: international equity managers reset their currency hedges once a month, on the last business day,
  at the WM/R 16:00 London fix; hedge size is computed from holdings valued at the close of the day before month-end;
  orders reach the banks "an hour or more before the 4pm fix". If a country's equity market rose over the month
  relative to the others, the hedgers who own it must sell more of its currency forward: **relative equity
  outperformance of country X predicts depreciation of currency X in the hour before the last fix of the month.**
  Spec: currency return 15:00-16:00 London on the last day of the month; equity return = local-currency total market
  index, close of the first day to close of the second-last day of the month (they wrote "first", we read it as the
  previous month-end close, which is what a hedge reset uses); panel regression with both sides cross-sectionally
  demeaned over 10 currencies: slope -0.0142 (p 0.00), R2 0.03, i.e. **1.42 bp of currency move per 1 % relative
  equity return**. 72 % of the 15:00-16:00 move is reversed by noon the next day on month-end days (AR coefficient
  -0.339 all days, -0.387 extra at month-end). NBFI volume at month-end is 1.4-2.4x a normal day; the US flow is
  ~$2.5bn per 1 % US equity move, EUR and JPY ~$0.6bn, GBP/CHF/AUD/CAD $0.06-0.15bn (Table 3). Sample 2004-2012.
- A 2026 practitioner replication (forexdetox substack, "The 4 PM London Fix Anomaly at Month-End", Feb 2015-Jul
  2026, not peer reviewed): S&P 500 month-to-date return to the close before the fixing day; 1 pp higher S&P return
  -> USD weaker by ~2.1-2.2 bp over 15:00-16:00 London (GBP, CHF, AUD, NZD significant), post-fix slope of the
  opposite sign over 16:03-17:00, reversing 41-75 %. This overlaps our HOLD, so it is used only for the side and the
  windows, never as evidence for HOLD.
- Hau & Rey (2006), Camanho, Hau & Rey (2022): rebalancing gives the same sign (foreign outperformance -> sell that
  currency). Evans (2018) and Krohn, Mueller & Whelan (2024): USD tends to rise into fixes unconditionally and fall
  after (a level effect, not tested here: it is round 3 M1/F1).

So the side is fixed: **long the currency whose equity market underperformed, short the one that outperformed, into
the month-end fix**; and for the US-only variant, **US equities up over the month -> sell USD into the fix**.

## How this differs from what was tested
- Round 3 F1 faded the realised 15:00-16:00 move after the month-end fix (no equity signal). Round 3 M1 bought USD
  unconditionally 10:00-13:00 UTC on the 3rd-to-last weekday. Round 3 U1 used the daily US equity move at the next
  daily fix (no month-end concentration). Round 4 traded indices on pension stock-bond rebalancing. Round 10 E1
  conditioned the daily WM/R fix on volatility. None used the month-to-date equity return to sign the month-end fix
  trade, which is the paper's identifying idea.
- Why it may escape the standing limits: the flow's direction and size are predictable from public data a day ahead
  (like gotobi); its size scales with |signal| (the paper's Table 3 makes the hedge flow proportional to |equity
  move|), so on big-move months the expected move (1.4-2.1 bp per 1 %, i.e. 4-10 bp at a 3-5 % relative move) is a
  multiple of the 0.6-1.5 bp FX round-trip cost at 15:00-16:00 London. The weakness is frequency: 12 events a year,
  so DEMO is the realistic bar; LIVE power is reported anyway.

## Common definitions (fixed now)
- Business day: weekday that is not an England bank holiday (GB in holidays.json) and not Dec 25 / Jan 1.
  T = last business day of the month; T-1, T-2 = the business days before it. Quarter-end = Mar, Jun, Sep, Dec.
- Times are London local (DST-aware, Europe/London); 16:00 London is the fix. A window "15:00 -> 16:00" enters at
  the mid at 15:00:00 (close of the 14:59 bar) and exits at 16:00:00 (close of the 15:59 bar). The signal is known
  the evening before, so there is no look-ahead; +1 minute latency shifts both entry and exit by 1 minute.
- Equity return to day D-1 (D = the trading day): log(index mid at its cash close on D-1 / index mid at its cash close
  on the last business day of the previous month). Cash closes (local, DST-aware): US500 16:00 New York; DE40 17:30
  Frankfurt; UK100 16:30 London; JP225 15:00 Tokyo; AUS200 16:00 Sydney. If that minute has no quote, the last quote
  in the 30 minutes before is used; if none, the event is dropped for that pair (counted and reported).
- Country map (Melvin & Prins use country indices): EUR -> DE40, CHF -> DE40 (no Swiss index in the panel; proxy),
  GBP -> UK100, JPY -> JP225, AUD -> AUS200, NZD -> AUS200 (proxy). CAD has no index: CAD is used only in the
  US-only signal.
- Signals (pair X vs USD, all fixed before looking):
  - **S_rel** (the paper's spec, local terms): r_X - r_US. Pairwise this equals the paper's demeaned panel spec.
    Predicted: currency X moves by -k * S_rel against USD.
  - **S_usd** (USD terms): (r_X + FX return of X vs USD over the same dates, taken at the US close) - r_US.
  - **S_us** (US only, the replication's spec): r_US. Predicted: USD moves -k * r_US against every currency.
  - Trade side for a pair: if the predicted move of X vs USD is up, buy XUSD / sell USDX; else the opposite.
- Measured per event x pair: signed mid return in bp (positive = the predicted side won), and the slope of the pair
  return on the signal (bp per 1 %), with the sign convention that the paper's slope is positive.
- Statistic: mean over events of the equal-weight average across pairs that day (clustered by month-end date), t of
  that series. Costs: half the actual spread at the entry minute + half at the exit minute, + 0.6 bp commission.

## Hypotheses

### I1. Into-fix hedge flow, signed by month-to-date equity returns (primary)
- Rule: on day D, from W to 16:00 London, take the side above in each pair.
- Primary cell, declared now: **D = T, W = 15:00, S_rel, all month-ends, 6 pairs (EURUSD, GBPUSD, USDJPY, USDCHF,
  AUDUSD, NZDUSD)**. Expected mid: ~1.4 bp per 1 % of |S_rel| (paper), so +3 to +4 bp per event at a typical 2-3 %.
- Secondary cells: signals {S_rel, S_usd, S_us (7 pairs incl. USDCAD)} x W {15:00, 15:30, 15:45} x D {T, T-1, T-2}
  x subset {all month-ends, quarter-ends} = 54 cells. T-1 is the "day before" check (some managers reset a day
  early); T-2 is the last spot trade settling inside the month (the value-date convention of round 3 M1). For D = T-1
  and T-2 the equity return runs to the close of D-1.
- Horizon: 15-60 minutes, closed by 16:00 London (no swap).

### I2. Post-fix reversal, conditional on the same signal
- Mechanism: the paper's 72 % reversal by noon next day (dealers lay off the fix inventory); the replication's
  16:03-17:00 reversal.
- Rule: on D = T, after the fix, take the side opposite to I1's predicted side.
- Cells: signals {S_rel, S_usd, S_us} x windows {16:00 -> 17:00, 16:05 -> 17:00, 16:00 -> 12:00 London next
  business day} x subset {all, quarter-ends} = 18 cells. The overnight window pays FX swap (research/swing/rates.py)
  in the executable version.
- How it differs from F1: F1 faded the realised 15:00-16:00 move; I2 fades the predicted flow direction whatever the
  realised move was.

### I3. Tradeable basket (only for an I1 or I2 cell with mid t >= 2 in IS on the predicted side)
- One bot, <= 3 positions. S_rel / S_usd: the 3 pairs with the largest |signal| that month (ties: the cheaper pair).
  S_us: EURUSD, USDJPY, GBPUSD (the three cheapest at 15:00-16:00 London by IS median spread, fixed before looking at
  returns).
- Variants (fixed now): (a) all events, 1x lot; (b) gated: trade only when |signal| >= the IS median |signal| of that
  pair; (c) size-scaled: lot = clip(|signal| / IS median |signal|, 0.5, 2).
- Reported: executable net bp per event (lot-weighted), IS / VAL, day-clustered t, years positive, spread x1.5,
  +1 minute, random-entry control (same window on 300 seeds of random non-month-end business days, excluding the
  last 3 and first 2 business days of each month, with the same per-event side vector re-used, so the sign mix is
  preserved), per-trade Sharpe and LIVE power, C3 daily/monthly correlation on IS+VAL.

## Multiple testing (fixed now)
I1 54 cells + I2 18 cells = 72 mid cells; I3 at most 3 variants x a few cells. Chance benchmark: a permutation null
that flips the side of every pair on the same event date together (shared by all cells and pairs), 2,000 draws,
distribution of the max |t_IS| over all 72 cells; and the max-of-K-normals benchmark (K = 72, ~2.9 at 5 %).
The primary cell is judged on its own t (it was declared before looking).

## Additions after the first screen (post hoc, written 2026-10-06 01:00 UTC, before their numbers)
The I1/I2 mid screen (72 cells, +0 and +1 minute) was run at 00:58-00:59 UTC. The paper's primary cell fails IS.
The cells with IS mid t >= 2 are all S_us at T-1 (into the fix) or S_us after the fix on T. Added, all post hoc:
- **P1 (pre-declared above)**: the permutation null over the 72 cells and I3 baskets for every cell with IS mid
  t >= 2 on the predicted side (9 cells: I1 S_us T-1 15:00 all / q, 15:30 all, 15:45 all; I1 S_rel T-1 15:00 q;
  I2 S_us 16:00-17:00 all, 16:05-17:00 all, 16:00-next 12:00 all / q).
- **P2 ordinary-day placebo**: the same windows and side rule on every business day that is not among the last 3 or
  first 2 of its month, with the signal = the equity return over the 21 business days to the close of D-1 (same
  horizon as a month-to-date return at month-end). If the IS effect is as large there, it is not the month-end hedge
  flow (and U1-style daily rebalancing at a monthly horizon would be the thing to test, at ~200 events a year).
- **P3 level vs conditional**: for the S_us cells, the mean pair return (USD side) in US-up months and in US-down
  months separately, to separate an unconditional month-end USD move from the signal-conditional part.

## Additions after the I3 baskets (post hoc, written 2026-10-06 01:01 UTC, before their numbers)
I3 (27 basket cells = 9 cells x 3 variants, run 00:59-01:00 UTC): the only basket with IS t >= 2 and VAL net > 0 at
x1.5 and +1 minute is **I2 S_us 16:00-17:00 London on T, gated (|r_US MTD| >= IS median), USD side = opposite of the
hedge flow (buy USD after the fix when US equities rose over the month, sell when they fell), EURUSD + USDJPY +
GBPUSD**. Before treating it as a candidate, all post hoc:
- **P4** permutation null for the basket family: flip the side of every trade of a month together, recompute the
  gross IS t of all 27 basket cells, distribution of the max (2,000 draws); compare with the chosen cell's gross IS t.
- **P5** ordinary-day placebo (P2's definition) for the I2 16:00-17:00 and 16:05-17:00 windows and for I1 T-1 15:00,
  gated the same way (rolling 21-business-day |r_US| >= its IS median).
- **P6** threshold sensitivity: gate at the IS 33rd and 67th percentile of |r_US| (expect the same sign; a knife-edge
  would be a warning), and the per-year table.
- **P7** overlap with round 3 F1 (fade the realised 15:00-16:00 move after the fix): share of gated events where the
  I2 side equals F1's side, and the I2 result split by agreement.
- **P8** C3 daily and monthly P&L correlation, IS + VAL.
- **P9** random-entry control on IS + VAL pooled (in addition to each era).
Decision rule written now: a PREREG draft is written only if P4 puts the chosen cell beyond the 95th percentile of
the family's max |t|, P5's placebo is not as large (placebo IS t < 2), and P6 keeps the sign at both thresholds.
