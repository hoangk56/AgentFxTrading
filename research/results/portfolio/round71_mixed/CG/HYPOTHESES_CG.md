# HYPOTHESES_CG: CME bitcoin weekend gap fade (round 71, stream CG)

Written 2026-11-01 17:50 UTC (from `date -u`: Sun Nov 1 17:50:47 UTC 2026), before any return was computed. No 2025-26
data: every series is cut at ts < 2025-01-01 at load. HOLD stays closed; if a cell passes the IS / VAL bars I write
PREREG_DRAFT_CG_<name>.md and stop.

## Mechanism (side fixed before data)
CME BTC futures (and ETH futures from 2021-02-08) stop trading Friday 16:00 Chicago time and reopen Sunday 17:00 Chicago
time; Binance perps trade through the weekend. Desk lore: the "CME gap" (the CME chart's jump from Friday close to Sunday
open) fills, i.e. price returns to the Friday close in the following days. Economic story to test: during the weekend the
crypto-native book (perps, spot) moves without the CME / ETF-arbitrage basis desks and the regulated-fund flows that hedge
on CME; at the reopen these desks re-enter and rebalance (basis trades re-struck, hedges reset at the Monday CME price),
which would pull price back towards the level at which their hedges were last set. Side: **fade** the weekend move
(short after a weekend rally, long after a weekend drop). Desk lore is public and widely traded, so the prior is weak.

How this differs from what is exhausted (PROMPT "Những họ đã cạn"): round 19 T tested the FX weekend-gap fade (a gap in the
traded asset itself; real 2004-15, gone after publication); round 23 N tested the 17:00 NY rollover gap fade in FX (real at
mid, under the 3-5 bp spread). Here the traded asset has no gap at all; the "gap" is a move of a 24/7 market during a
closure of a *different venue* (CME), and the hold is 1-3 days, so costs (12 bp round trip) are small against the move
(>= 200 bp). Round 37's stops beyond the prior week's extremes found continuation (opposite side) at those levels; the
weekly extreme and the CME Friday close are different anchors, and I report the result whatever its sign.

## Session times (CME Globex, BTC and ETH futures)
- Friday close C = Friday 16:00 America/Chicago = 21:00 UTC under CDT, 22:00 UTC under CST.
- Sunday reopen R = Sunday 17:00 America/Chicago = 22:00 UTC under CDT, 23:00 UTC under CST.
- US DST (CDT) from the second Sunday of March 02:00 local to the first Sunday of November 02:00 local:
  2020-03-08..11-01, 2021-03-14..11-07, 2022-03-13..11-06, 2023-03-12..11-05, 2024-03-10..11-03. On the switch weekends
  C and R take different offsets (March: C 22:00, R 22:00 UTC, 48 h; November: C 21:00, R 23:00 UTC, 50 h). Computed from
  the rule in code, not from a table.
- Holidays: cmegroup.com could not be reached (curl error 7, research/data/cme_gap/requests.log) and one WebSearch did not
  give product-level holiday hours. So weekends whose CME close or reopen is not the regular one are **excluded**
  (declared now, list fixed): Good Friday weekends (2020-04-10, 2021-04-02, 2022-04-15, 2023-04-07, 2024-03-29); the
  Friday after Thanksgiving (early close: 2020-11-27, 2021-11-26, 2022-11-25, 2023-11-24, 2024-11-29); Friday or Monday
  US holidays that move the close / reopen (2020-07-03, 2020-12-25, 2021-01-01, 2021-07-02 weekend (Mon 07-05 observed),
  2021-12-24, 2021-12-31, 2022-12-23 weekend (Mon 12-26), 2022-12-30 weekend (Mon 01-02), 2023-12-22 weekend (Mon 12-25),
  2023-12-29 weekend (Mon 01-01)). Other Monday holidays (MLK, Presidents, Memorial, Labor) keep the Sunday 17:00 CT
  open and are included. About 4-5 weekends / year are dropped.
- ETH: events only from the weekend of 2021-02-12 (first Friday close after the CME Ether futures launch on 2021-02-08).

## Data
- Binance USDT-M perp 1m klines (research/data/binance_1m_wicks/npz/{BTC,ETH}USDT_YYYY-MM.npz, 2020-01..2024-12; o h l c).
- Funding stamps research/data/binance/funding/{BTC,ETH}USDT.csv (cut < 2025-01-01).
- Price at an instant T = close of the 1m bar that opened at T - 1 min (forward fill <= 5 min, else the event is dropped).

## Rule
- m = ln(P(R) / P(C)) on the Binance perp (P(C) is the proxy for the CME Friday close; the CME futures price itself is
  not available, its basis to the perp moves slowly and the lore is quoted on the same chart).
- Event if |m| >= k. Side s = -sign(m).
- Entry: price at R + 6 min (close of the 1m bar opening at R + 5 min, i.e. first 1m bar after reopen + 5 min). If the
  entry price is already at or beyond the Friday price (gap closed before entry), no trade.
- Exit: first 1m bar after entry whose low (for a short) / high (for a long) reaches P(C): fill at P(C) (resting order at
  the target; charged as taker anyway). Otherwise time stop at the close of the bar at entry + H.
- Funding: s x (sum of funding rates of stamps in (entry, exit]) is paid (long pays positive funding).
- Costs: taker 5 bp a side + 1 bp half-spread a side = 12 bp round trip on BTC and ETH; robustness at x1.5 (18 bp).
- One step late: entry one 1m bar later (price at R + 7 min) and target exits filled at the close of the bar *after* the
  touch bar (not at P(C)); time stops one bar later.

## Declared cells (4, pooled BTC + ETH book, one trade per coin per weekend)
| cell | k | H |
|---|---|---|
| G2_1d | 2 % | 24 h |
| G2_3d | 2 % | 72 h |
| G4_1d | 4 % | 24 h |
| G4_3d | 4 % | 72 h |
Primary cell (stated now, for the registration if anything passes): G2_3d (most trades, lets the lore's "following days"
play out). The max-over-4-cells null is reported. BTC-only and ETH-only splits are reported as information, not cells.

## Statistics and bars
- Net bp per trade; t clustered by weekend (BTC and ETH of the same weekend = one cluster). Eras: IS 2020-01-01..2021-12-31,
  VAL 2022-01-01..2024-12-31 (by the Friday close date). Years positive out of 5 (needs >= 4 of 5 for LIVE).
- Bars from BRIEF unchanged: LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years, >= 95 % random, power >= 3; DEMO t >= 2.0 IS,
  net > 0 VAL, >= 90 % random; both need net > 0 in IS and VAL at x1.5 costs and one step late.
- Random benchmark (two forms):
  (a) the brief's: the same rule anchored to the Monday / Tuesday / Wednesday / Thursday 16:00 CT "close" with a pseudo
      reopen 49 h later (same DST conversion), reported per anchor;
  (b) hour-of-week placebo: the same rule (49 h move, same k, same entry delay, target = anchor price, same H, same
      costs and funding) anchored at every UTC hour of the week whose anchor is not within 24 h of the real Friday close
      (about 120 anchors), each run over every week of the era; random % = share of placebo anchors with a lower mean net
      per trade than the real rule in that era. The max-over-4-cells version compares the best real cell with the best of
      4 placebo cells per anchor.

## Power arithmetic (before data)
HOLD 2025-01-01..2026-10-29 = ~95 weekends, ~86 after holiday exclusions. Power = S x sqrt(n_H), S = net mean / sd at VAL
size, n_H = 0.61 n_VAL (HOLD 22 months / VAL 36 months); I also report the weekend-clustered version t_VAL x sqrt(0.61).
Expected rates (guess from BTC weekend vol 2.5-3.5 % over 49 h; ETH higher; BTC-ETH weekend moves correlated ~0.8):
- k = 2 %: ~40 % of weekends per coin -> ~70 HOLD trades in ~40 weekend clusters: LIVE needs a per-cluster Sharpe of
  3 / sqrt(40) = 0.47. With a 3-day per-trade sd of ~500-700 bp that is a mean of ~+250-330 bp per trade, more than the
  typical gap itself: **LIVE is out of reach a priori** unless almost every gap fills; DEMO needs only IS t >= 2.
- k = 4 %: ~12 % of weekends per coin -> ~20 HOLD trades / ~12 clusters: needs S ~ 0.87. Out of reach.
So the realistic best outcome is DEMO; I say this before seeing any return.
