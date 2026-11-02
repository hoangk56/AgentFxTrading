# HYPOTHESES_PX: tokenized gold (PAXG) over the weekend vs gold's reopen

Written 2026-11-01 17:57 UTC (from `date -u`), before any PAXG return was computed. The PAXG 1m / aggTrades pull was
running (prices downloaded, not looked at); only IC gold timestamps and PAXG daily volume were inspected.

## Mechanism
PAXG (Paxos Gold, 1 token = 1 fine troy oz of LBMA gold, redeemable) trades on Binance spot 24/7. Spot gold (IC
XAUUSD, following CME Globex / OTC hours) is shut from Friday ~17:00 New York to Sunday ~18:00 New York. Over the
weekend PAXG is priced by crypto flows (and crypto liquidations, stablecoin flows) with no gold market to anchor it;
creation / redemption at Paxos only happens on business days. When gold reopens the arbitrage anchor returns. If
weekend PAXG moves are partly noise (crypto flow), a cheap PAXG on Sunday evening should drift back up after gold's
reopen. If they are information (PAXG anticipates gold's reopen gap), gold gaps to PAXG and the trade earns nothing.
The test separates the two. Side fixed before data: buy PAXG when it is cheap (long, spot, no borrow). The rich side
(PAXG up vs Friday) can only be traded by selling PAXG one already holds and rebuying (no PAXG perp before 2025-03:
local perp_1d/PAXGUSDT.csv starts 2025-03-27; XAUTUSDT spot starts 2026-03, not usable). It is reported separately.

No earlier round tested PAXG / XAUT (checked registry / JOURNAL per the brief).

## Data
- Binance spot PAXGUSDT 1m klines and aggTrades, data.binance.vision monthly files 2020-08 .. 2024-12
  (research/data/paxg_weekend/npz/; aggTrades kept only for Fri 18:00 .. Mon 08:00 UTC). First PAXGUSDT kline
  2020-08-28 00:00 UTC (spot_first.csv). Everything cut at ts < 2025-01-01.
- IC XAUUSD M1 (research.m1: bid OHLC + ask close); gold mid = (bid close + ask close) / 2.
- Weekend PAXG liquidity is thin: median Sat/Sun daily trades 1.4k (2020), 7.7k (2021), 4.0k (2022), 4.2k (2023),
  8.5k (2024); median weekend daily quote volume $0.2-2.5 M.

## Gold session times at IC (measured from M1 gaps > 30 h, 2020-08-27 .. 2024-12-31)
- Last gold bar Friday 20:56-20:58 UTC (US summer time, EDT) or 21:56-21:58 UTC (winter, EST); reopen Sunday 22:02
  UTC (summer) / 23:02 UTC (winter). Normal gap 49.1 h. US DST-change weekends: 50.1 h (Nov) / 48.1 h (Mar).
- Holidays / irregular (25 of 227): Thanksgiving Friday early close 18:44 UTC; Christmas / New Year Thursday close
  (2020, 2021) or Monday reopen 23:02 UTC (2022-12-26, 2023-01-02, 2023-12-25, 2024-01-01); Good Friday (Thursday close,
  2021-04-01, 2022-04-14, 2023-04-06, 2024-03-28); late IC reopens Mon 00:33 (2023-02-20) and Mon 02:08 (2023-09-04).
- Weekends (gaps spanning a Saturday) with PAXG listed: **IS 71** (2020-08-28 .. 2021-12-31), **VAL 156** (2022-24).
  HOLD (2025-01 .. 2026-10-29) has ~95. 71 IS weekends is small but it is the only split allowed; I do not invent a new
  one.

## Definitions (per weekend)
- F = gold's last M1 bar before the weekend gap (normally Fri 20:56 / 21:56). P_F = PAXG close of the same 1m bar,
  G_F = gold mid close. Ratio q_F = P_F / G_F (absorbs PAXG's standing premium).
- R = gold's first M1 bar after the gap (the reopen minute).
- T = the last 21:00 UTC that is at least 60 min before R (Sunday 21:00 for normal weekends; Monday 21:00 when gold
  reopens Monday 23:02; Sunday 21:00 for the Mon 00:33 / 02:08 reopens).
- w = ln(P_T / (G_F x q_F)) = ln(P_T / P_F), P_T = PAXG close of the bar 20:59 (last trade before T).
- Entry: PAXG close of the bar starting at T (price at T + 1 min), i.e. a minute after the signal. One step late check:
  close of the bar T + 1.
- Exits: PAXG close of the bar starting at R + 30 min (X30) or R + 240 min (X4h).

## Declared cells (6, no others)
| cell | side | k | exit |
|---|---|---|---|
| L30-X30 | buy PAXG if w <= -30 bp | 30 bp | R + 30 min |
| L30-X4h | buy PAXG if w <= -30 bp | 30 bp | R + 4 h |
| L60-X30 | buy PAXG if w <= -60 bp | 60 bp | R + 30 min |
| L60-X4h | buy PAXG if w <= -60 bp | 60 bp | R + 4 h |
| S30-X4h | sell held PAXG if w >= +30 bp, rebuy at exit (rich side, reported separately) | 30 bp | R + 4 h |
| S60-X4h | as above | 60 bp | R + 4 h |
Primary family = the 4 long cells; max-over-cells null reported over them (and over all 6).

## Costs
- Spot taker 10 bp a side (Binance standard, no BNB discount) = 20 bp round trip.
- Plus a measured half-spread on each side: from aggTrades, pairs of consecutive trades with opposite taker side
  within 5 s, half-spread = median |price change| / 2 / price over pairs in a +-5 min window around the fill minute;
  if fewer than 3 such pairs, the era median at that clock (entry / exit) is used. Kline-based check: Roll estimate.
- Costs x 1.5 check: (20 bp + spreads) x 1.5.
- Capital: the spot leg is paid in full for 1.5-6 h; graded on excess over DFF (research/data/rates/DFF.csv), i.e.
  minus DFF x hold time (<= 0.1 bp). Rich side: the held PAXG forgoes nothing (it is the same coin rebought), no DFF.

## Statistics, benchmarks, controls
- One trade per weekend, so t = mean / (sd / sqrt(n)) (clustering by day is the same thing). Years: 2020 (Sep-Dec),
  2021 | 2022, 2023, 2024.
- Random R1 (conditioning): 2,000 draws of the same number of weekends from all weekends of the era, same trade
  (long T -> exit); % of draws whose mean net is below the rule's.
- Random R2 (shuffled signal / max over cells): permute w across the era's weekends 2,000 times, recompute the t of
  the 4 long cells (and of all 6), compare the observed best t to the null of the max.
- Placebo P (anchor present): the same rule on weekday nights Mon-Thu, where gold has the same daily break
  (~20:58 -> 22:02 UTC summer): F' = gold's last bar before the daily break, the same w, T, entry and exits. If the
  weekday version earns the same, the effect is PAXG premium mean reversion, not the weekend wedge.
- Checks: excluding irregular weekends (gap > 52 h); excluding Mar-Apr 2020 (not in sample anyway); entry one bar late;
  costs x 1.5.
- Descriptive: the weekend-deviation size distribution (|w| quantiles per era) and the path of PAXG vs gold from F to
  Monday 06:00 UTC by w bucket (<= -60, -60..-30, -30..+30, +30..+60, >= +60 bp): gold reopen gap ln(G_R/G_F), PAXG
  T -> R+30 / R+4h / Mon 06:00, PAXG premium ln(P / (G x q_F)) at those times.

## Power arithmetic (before computing)
HOLD has ~95 weekends. If a fraction f of weekends triggers, n_HOLD = 95 f and LIVE power >= 3 needs a per-trade net
Sharpe >= 3 / sqrt(95 f): f = 0.5 -> 0.44; f = 0.3 -> 0.56; f = 0.1 -> 0.97. IS t >= 2.5 with 71 f trades needs
Sharpe >= 2.5 / sqrt(71 f): f = 0.3 -> 0.54; f = 0.1 -> 1.0. With 20 bp + spread round trip and a deviation of
30-60 bp, LIVE is a priori out of reach unless most of a large deviation reverts with low noise; DEMO (IS t >= 2.0,
VAL net > 0, >= 90 % random) is the realistic bar.

## Bars (unchanged)
LIVE: net > 0 IS and VAL, positive at costs x1.5 and one bar late, t >= 2.5 IS / >= 1.5 VAL, >= 2/3 years positive,
beats >= 95 % random, HOLD power at VAL size >= 3. DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random. If a cell
passes, PREREG_DRAFT_PX_<name>.md and stop; HOLD stays closed.

## Addendum 2026-11-01 17:58 UTC (before any return was computed): placebo P made precise
On weekday nights T = 21:00 UTC lies before gold's last bar in winter (21:56), so P is defined as: Mon-Thu nights
with a daily break of 50 min .. 3 h; F' = gold's last bar before the break, T' = F' rounded up to the next full hour
(21:00 summer / 22:00 winter), entry = close of the PAXG bar starting at T', exits R' + 30 min / R' + 4 h. Signal =
the PAXG premium change over the same ~48 h span with the anchor present: w' = ln(P_T'/P_A) - ln(G_F'/G_A), A = the
gold bar 48 h before F' (2 trading days). Same k, same costs. This is a control, not a cell.
