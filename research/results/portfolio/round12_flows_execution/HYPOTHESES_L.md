# Round 12, stream L: conditions that scale the real-but-sub-cost flows (selection, not execution)

Written 2026-10-06 00:59 UTC, before any round-12 number of this stream was computed (the unconditional numbers below
are the earlier rounds' published ones). HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31,
the USDCNH M1 cache is cut at 2025-01-01 at load.

## Why this could escape the standing limits, and how it differs from round 10 E
The effects below are real at mid (t 2-13 in both eras) but 1.5-3x too small for IC's round trip. A flow is a
quantity of orders; its price impact on a given day is (size of that day's flow) x (impact per unit). Round 10 E
conditioned only on the *impact per unit* side (20-day realised vol C-RV, 60-min pre-window activity C-PRE) and got
~1.5x, with spreads rising too. This stream conditions on the *size of the flow itself*, using day-level proxies taken
from each mechanism: calendar dates when the flow's owners must trade more (month/quarter-end, holidays in the flow's
home venue, index rebalances, option expiries), and the prior price move that the owners respond to (dip buying,
leveraged-ETF rebalancing proportional to the day's return, hedge rebalancing proportional to month-to-date moves).
None of these variables was used by E (E used RV20 and pre-window RMS only), by round 6 S1 (big days = |z| > 1 only),
by round 11 H2 (unconditional) or round 7 B (unconditional). Stream J works on how to execute; here execution is
fixed at the earlier rounds' rule (market in/out at the stated minutes), so the two streams do not overlap.

A cell can only matter if its selected days carry about 3x the unconditional mid move with a spread that does not
grow as much; so the judged quantity is the per-trade net Sharpe and the power at the selected frequency, and the
ratio (selected mid) / (unconditional mid) is reported next to it, with the spread on selected vs all days.

## Common method (fixed now)
- Prices: panel mid, p(T) = close of the bar ending at T, forward-filled up to 10 min. USDCNH: IC M1 bid + half
  the published 2.93-pip spread. Cost: half the actual spread at entry + half at exit (panel) + 0.6 bp commission for
  FX and metals, 0 for indices; USDCNH: published spread + 0.6. Variants: spread x1.5, both fills +1 minute.
- Signals use data up to minute t, fills at t+1 or later (the base rules below already respect this, except where
  noted and changed).
- Every conditioning variable is causal (known before entry). Quantile levels use thresholds from the previous 250
  event days of the same family (at least 60), never the full sample.
- Each cell = (effect, variable, level). Statistics per cell and era (IS 2016-21, VAL 2022-24): n, trades/yr, mid bp
  and day-clustered t, ratio to the unconditional mid, mean cost (and selected vs all-day spread), net bp and t,
  per-trade net Sharpe, power = Sharpe x sqrt(1.73 x trades/yr), day-clustered power; the uplift
  (selected minus unselected mid, Welch t) as the mechanism check.
- Chance, two nulls, both shared across the cells of a family and across all families:
  (1) per-UTC-day sign flip (as the brief), on the selected net/mid; (2) label permutation: shuffle the vector of all
  conditioning variables across event days within era (keeps their correlations), recompute every cell's uplift t;
  compare the observed best uplift t with the 95th percentile of the max. 1,000 permutations each.
- Screen order: mid uplift and ratio first; then net. A cell goes to the full checks (x1.5, +1 min, years net > 0,
  random-entry control >= 200 seeds, C3 correlation) only if net > 0 in both IS and VAL with IS net t >= 2.0.
- Pass bars as the brief. LIVE or DEMO -> PREREG_DRAFT_L_<name>.md and stop that family.

## L1 SGE gold morning auction (long XAUUSD 02:15 -> 02:23 UTC, Chinese trading days from 2016-04-19)
Source: round 10 A1-flip / E (+0.93 t 7.9 IS / +0.72 t 4.5 VAL; cost 1.6 / 1.05). Mechanism: Chinese physical buyers
(jewellers, banks importing for them) bid in the auction; the excess passes through to London. Their demand is
price-sensitive (buy dips) and seasonal (stock before holidays). Base trade reproduced first.
| cell | variable (causal) | level | predicted |
|---|---|---|---|
| L1-DIP-q | XAU mid log return 07:00 UTC previous Chinese trading day -> 02:00 UTC today (the hours the Chinese day session was shut) | bottom quintile | larger rise |
| L1-DIP-d | same | bottom decile | larger rise |
| L1-CNH-q | USDCNH change over the same window | top quintile (CNH weaker) | larger rise (CNY-hedge demand; onshore price up) |
| L1-PREHOL | last 3 XSHG trading days before a closure of >= 2 consecutive XSHG weekday holidays | in set | larger rise (holiday stocking) |
| L1-POSTHOL | first XSHG trading day after such a closure | in set | larger rise (pent-up orders) |
| L1-MON | Monday (after a weekend) | Monday | larger rise (pent-up orders) |
| L1-DIPxPRE | L1-DIP-q and L1-PREHOL or L1-POSTHOL | both | larger (descriptive only, not counted; may be empty) |
Counted cells: 6.

## L2 Sydney-open V in AUDUSD + NZDUSD (two positions per day)
Source: round 4, round 10 E (pre leg short [T-15, T], T = 10:00 Sydney: +1.65 t 13.1 / +1.48 t 10.0; post leg long
[T, T+15]: +1.28 t 7.6 / +1.44 t 6.0; cost ~2.0-2.3). Mechanism: AUD/NZD selling by local participants (importers,
offshore holders unwinding at the local open) concentrated before 10:00 Sydney in a thin market, then reverting. Flow
size proxies:
| cell | variable | level | predicted |
|---|---|---|---|
| L2-MON | Monday (weekend backlog) | Monday | larger V |
| L2-POSTHOL | first Sydney weekday after a weekday that was an NYSE or ASX holiday (backlog) | in set | larger V |
| L2-ME | last 2 Sydney business days of the month (Australian fund rebalancing) | in set | larger V |
| L2-MExUSdown | L2-ME and US500 month-to-date return (to the previous NY close) < 0 (super funds over-hedged after a fall in foreign assets buy back USD, i.e. sell AUD) | both | larger V |
| L2-NYabs | abs(AUDUSD return over the previous New York session 13:00 -> 21:00 UTC) | top quintile | larger V (repositioning at the local open) |
| L2-NYdown | signed AUDUSD return over the previous NY session | bottom quintile (AUD fell) | larger V (Australian holders sell after a loss) |
| L2-RBA | RBA decision day (14:30 Sydney, cb_calendar.json) | in set | SMALLER V (locals wait for the decision); traded rule would be "not RBA" |
Each cell is judged on the pre leg and the post leg separately: 14 cells. Descriptive only (mechanism, not counted):
AU winter (10:00 Sydney = 00:00 UTC = 09:00 Tokyo) vs AU summer (23:00 UTC); Japanese holidays.
Overlap with E's C-RV TOP tercile is reported for every L2 cell.

## L3 EURUSD into the ECB 14:15 CET fix (long EURUSD 14:00 -> 14:15 CET, TARGET days)
Source: round 10 E (USD side -0.73 t -5.3 / -0.85 t -4.1; cost 0.65-0.8, mostly commission). Side: long EURUSD (the
data-derived side E found; it counts only because both eras agree). Mechanism: euro-area corporates and fund
administrators convert USD to EUR at the ECB reference rate; hedge rebalancing is concentrated at month-end, and its
direction follows month-to-date moves (euro investors with hedged USD assets sell more USD after USD assets rose).
| cell | variable | level | predicted |
|---|---|---|---|
| L3-ME | last 2 TARGET business days of the month | in set | larger EUR rise |
| L3-QE | last 2 TARGET business days of Mar/Jun/Sep/Dec | in set | larger EUR rise |
| L3-MExEURdown | L3-ME and EURUSD month-to-date (to 13:59 CET) < 0 | both | larger EUR rise (hedge top-up) |
| L3-MExUSup | L3-ME and US500 month-to-date (to the previous NY close) > 0 | both | larger EUR rise |
Counted cells: 4 (DEMO tier by frequency: <= 24 a year).

## L4 Gold / silver momentum into the COMEX settlement (leveraged-ETF rebalancing)
Source: round 6 S1 (gold w15 slope t 6.8 / 2.6; big days |z| > 1: +2.31 / +1.00 bp vs 1.30 / 0.96). Rule (made
executable): r_day = ln p(T-16) / p(previous settlement T on the previous US business day), T = 13:30 ET gold, 13:25
ET silver; z = r_day / sd of the past 60 daily settlement returns; trade sign(r_day) from p(T-15) to p(T). Round 6's
exact (non-lagged) version is reproduced first. Mechanism: rebalancing ~ L(L-1) x AUM x r_day, so dose-response in
|z|; more aggregate metal-ETF flow when gold and silver move together.
| cell | variable | level | predicted |
|---|---|---|---|
| L4-G-q | gold \|z\| | top quintile (causal) | larger momentum |
| L4-G-d | gold \|z\| | top decile | larger |
| L4-G-agree | gold \|z\| top quintile and silver's r_day the same sign with silver \|z\| > 1 | both | larger |
| L4-G-optex | COMEX gold options expiry day (4th last business day of the month; earlier if Friday-before-holiday is ignored) | in set | SMALLER (pinning) |
| L4-G-fnd | 3 business days up to the first notice day of Feb/Apr/Jun/Aug/Oct/Dec gold (last business day of the prior month) | in set | larger (roll-period open-interest concentration; low prior) |
| L4-S-q | silver \|z\| | top quintile | larger |
| L4-S-d | silver \|z\| | top decile | larger |
Counted cells: 7.

## L5 AUS200 closing auction fade (fade the 16:00 -> 16:12 Sydney move over 16:13 -> 16:30)
Source: round 11 H2 M5b (+0.82 t 2.17 / +0.71 t 2.71; cost 2.18 / 1.58). Mechanism: closing-auction order imbalance
pushes the futures-based CFD into the ASX closing single-price auction (16:10-16:12) and relaxes afterwards. Size
proxies:
| cell | variable | level | predicted |
|---|---|---|---|
| L5-REBAL | index rebalance days: S&P/ASX quarterly (third Friday of Mar/Jun/Sep/Dec) and MSCI (last business day of Feb/May/Aug/Nov) | in set | larger fade |
| L5-ME | last ASX business day of the month | in set | larger fade |
| L5-MOVE | abs(16:00 -> 16:12 move) | top quintile (causal) | larger fade (dose) |
| L5-DAY | abs(10:00 -> 16:00 move) | top quintile | larger fade (more close rebalancing) |
Counted cells: 4.

## L6 USTEC market-on-close imbalance follow (Nasdaq NOII 15:50 ET; follow the publication-minute move to 16:00)
Source: round 11 H2 M1 (+1.53 t 2.71 / +1.00 t 1.54; cost 1.67 / 0.65). Rule as H2: sign of p(15:50) -> p(15:51),
entry p(15:52), exit p(16:00) ET, NYSE trading days without early closes. Size proxies:
| cell | variable | level | predicted |
|---|---|---|---|
| L6-PUB | abs(publication-minute move) | top quintile | larger follow (bigger imbalance) |
| L6-OPEX | third Friday of each month (option expiry; quarterly Nasdaq-100 / S&P rebalances on Mar/Jun/Sep/Dec) | in set | larger follow |
| L6-ME | last NYSE business day of the month | in set | larger follow |
| L6-DAY | abs(USTEC 09:30 -> 15:49 return) | top quintile | larger follow (leveraged-ETF MOC orders) |
| L6-LETF | side = sign(09:30 -> 15:49 return) instead of the publication sign, entry 15:52, exit 16:00, on days in the top quintile of abs(day return) | top quintile | > 0 (leveraged-ETF rebalancing, Cheng & Madhavan; round 3 tested day move -> last 30 min unconditionally) |
Counted cells: 5.

## L7 USDCNH home-hours depreciation (long USDCNH 01:30 -> 08:30 UTC)
Source: round 7 B H7 (+1.17 t 2.6 / +2.03 t 2.5; cost ~1.0). Mechanism (Breedon & Ranaldo 2013): residents buy
foreign currency in home hours.
| cell | variable | level | predicted |
|---|---|---|---|
| L7-PREHOL | last 3 XSHG trading days before a closure of >= 2 weekday holidays (outbound travel / import payments) | in set | larger rise |
| L7-DIV | June-August (H-share and red-chip dividend payment season: corporates buy HKD/USD) | in set | larger rise |
Counted cells: 2.

## Other effects with |t| >= 4 at mid in both IS and VAL (checked in the write-ups)
None beyond L1-L4 (round 4's USDJPY 16:00-17:00 ET is t 5.9 / 3.8; HKS periodicity 6.8 / 2.6; USDF 5.3 / 3.2; silver
post-settlement reversal IS only). Not added.

## Totals
Counted cells: L1 6 + L2 14 + L3 4 + L4 7 + L5 4 + L6 5 + L7 2 = 42. Max of 42 normals: 95 % about 3.2.

## Addendum 2026-10-06 01:07 UTC (after the screen; checks, not new cells)
- L4-G-d (gold, top decile) was the only cell net > 0 in both eras with IS net t >= 2.0, so it went to the full checks
  declared above (x1.5, +1 min, years, random-entry, C3), plus a time placebo (window end shifted by -180..+150 min
  in 15-min steps, z, side and decile recomputed at every shift), an XPTUSD control, and a descriptive q x w
  sensitivity grid (not cells; w = 15 came from round 6's IS scan).
- Correction made after seeing its output: the first random-entry control drew windows from 08:30 ET onward with
  the trade's own side, which was fixed at 13:14 ET. Windows before 13:14 then overlap the move that set the side
  (look-ahead) and inflate the control. Replaced by two look-ahead-free controls, both reported: (a) random window end
  in [10:30, 16:00] ET, side recomputed from the previous settlement up to that window; (b) random window after the
  signal (13:46-16:45 ET) with the trade's side. The flawed control is reported too.
