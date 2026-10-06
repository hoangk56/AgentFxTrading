# Round 17, stream Y: quote-based order-flow imbalance (hypotheses)

Written 2026-10-06 02:41 UTC (`date -u` on the Mac; the round brief's header says 03:05 UTC, so the brief's clock and
this one differ), before any round-17 stream-Y number was computed. Only the tick cache format was inspected (one
2019 day per symbol, to see which fields exist).

## Data fact that shapes the measures
`research/ticks.py`: each .zticks row is (ts ms, bid x1e5, ask x1e5), 0 = that side unchanged. **There are no sizes
(no depth, no traded volume).** So the Cont, Kukanov & Stoikov (2014) OFI is computed in its price-only form (unit
depth at every level): e_n = sign(dBid_n) + sign(dAsk_n). The tick rule is applied to mid changes. Both are signed
counts of quote moves, not volumes; that is a limit of the data, said here before looking.

## Measures (per symbol, from IC ticks, days < 2025-01-01 only; the loader asserts it)
- OFI_k: sum of e_n over the ticks of the last k minutes (k in 1, 5, 15, 30), signal at the minute end t.
- TR_k: sum of sign(dMid_n) over the same ticks (tick rule on mid changes).
- INT_k: number of quote updates (rows) in the window; relative intensity RI = INT_k / mean INT_k at the same UTC hour
  over the previous 20 trading days.
- R_k: own mid log return over the window (control: the question is whether signed flow adds anything beyond the
  return that the window already shows; round 8 and earlier tested price lead-lag and own-return effects).
- z(X) = X / sd(X) with sd from the previous 20 trading days of the same measure (all minutes; look-ahead free).
- Target: mid log return from t + L to t + L + h minutes, h in 1, 5, 15, 30, 60; L in 0 (reference: not
  tradable), +1 s, +5 s, +30 s, +60 s. Mid at a time = last tick at or before it.

Symbols: AUDUSD, NZDUSD, XAUUSD, XAGUSD, US30, USTEC (2016-2024), XTIUSD (2018-2024). Eras: IS 2016-21 (XTI 2018-21),
VAL 2022-24. No PRE (no ticks before 2016). HOLD is never loaded.

## Hypotheses and sides (fixed now, from the literature)

| id | mechanism, source | cells where it is the registered side | side |
|---|---|---|---|
| Y1 | Persistent order flow: order signs are long-memory (Lillo & Farmer 2004; Bouchaud et al. 2004), trades have a permanent impact that is impounded over several trades (Hasbrouck 1991), order imbalance predicts 5-30 min returns on NYSE (Chordia, Roll & Subrahmanyam 2002, 2005) and FX order flow predicts returns (Evans & Lyons 2002, 2005; Rime, Sarno & Sojli 2010) | every (k, h) except Y2's | continuation: long when OFI z > 0 |
| Y2 | Inventory / liquidity-provision reversal at short lags (Ho & Stoll 1981; Hendershott & Menkveld 2014): dealers who absorbed the flow lean their quotes back | k = 1, h = 1 | reversal |
| Y3 | Information events: order flow after news is more informative and its impact more persistent (Love & Payne 2008; Evans & Lyons 2008) | condition HI: 08:30-11:00 New York time (US data, US cash open, EIA Wednesday 10:30) and 08:00-09:00 London, weekdays | continuation, expected stronger than ALL |
| Y4 | Thin liquidity: moves on few, non-informational updates are liquidity-driven and revert (Campbell, Grossman & Wang 1993; Llorente et al. 2002) | condition THIN: 18:05-20:00 New York time (after the daily rollover/reopen, before Tokyo), h <= 15 | reversal |
| Y5 | High activity marks information arrival (Easley & O'Hara 1992; Llorente et al. 2002) | condition HINT: relative intensity RI_k >= 2 | continuation, expected stronger than ALL |

Expectation written now: CKS 2014 find OFI explains the contemporaneous price change and lagged OFI adds little;
round 8 found cross-symbol information priced within the first minute. The likely answer is that the slope at L = 0
is large and at L >= 1 s small, and below cost. The test is whether anything survives at +1 s / +5 s and whether a
large-|z| rule clears the spread.

## Screen (step 1, at mid)
Per symbol x measure (OFI, TR) x k x h x L x condition (ALL, HI, THIN, HINT) x era: OLS slope of the forward return
(bp) on z (bp per 1 sd of z), day-clustered t (UTC day). Also the partial slope of OFI z controlling for z(R_k).
Forward returns winsorised at +-10 robust sd (MAD per symbol and year) in the screen only. Excluded data: XTI
2020-04-15..2020-04-30 (negative-price episode). Cells: 7 symbols x 2 measures x 4 k x 5 h x 5 L x 4 conditions x 2
eras = 11,200 slopes (5,600 per era), of which the tradable ones are L >= 1 s (4,480 per era).
Chance: a permutation null that flips the sign of the forward return per UTC day, the same flip for all symbols,
200 draws, on the IS max |t| over the tradable OFI cells.

## Executable rule (step 2), fixed now
- Signal OFI z_k at minute end t; trade when |z| >= c, side from the table above (continuation unless Y2 / Y4 cell).
- Entry at t + L at the last tick at or before it (long at the ask, short at the bid), L = +1 s primary; +5 s, +30 s,
  +60 s also. Exit at entry + h minutes at the bid (long) / ask (short).
- One position per symbol at a time (signals while in a position are skipped). No entry from 16:30 to 18:10 New York
  time, nor Friday after 16:00 New York; a trade whose exit would be after 17:00 New York is not taken (no swap).
- c = IS quantile of |z| at P95, P99, P99.9 (per symbol, k, condition). k, h, c chosen per symbol and condition on
  IS by the IS net day-clustered t at L = +1 s; VAL is a check only.
- Cost: actual bid/ask at both fills; + 0.6 bp commission round trip for AUDUSD, NZDUSD, XAUUSD, XAGUSD; 0 for US30,
  USTEC, XTI. Stress: spread x1.5 (extra 0.25 x (spread_in + spread_out)) and L = +60 s.
- Report: net bp, day-clustered t, per-trade Sharpe, trades a year, power = Sharpe x sqrt(trades/yr x 1.73) on IS and
  VAL size, by year; VAL / IS ratio; random-entry control and C3 correlation only for a rule that is net > 0 in IS and
  VAL. Rule cells: 7 symbols x 4 conditions x 4 k x 5 h x 3 c = 1,680.

## Post-hoc additions (after the screen and the rule grid were seen)
Added 2026-10-06 02:50 UTC (`date -u`). The only rule net > 0 in IS and VAL with IS net t >= 2 is US30, HI, k = 30,
h = 15, |OFI z| >= IS P99.9, continuation (registered side Y3). Checks run on it as the brief requires (by year,
latency, x1.5, random-entry controls (a) same NY half-hour + weekday on random days and (b) same day at a random time
in the window, side recomputed at the random time, C3 correlation). Post-hoc diagnostics, not registrable:
- PH1: the same rule with z(RET_30) instead of z(OFI_30) (same IS P99.9 cut), and with |RET z| >= cut on the US30
  k30 HI cells, to see whether the signed-flow count adds anything beyond the 30-minute move.
- PH2: the same rule on USTEC (the twin index) as an out-of-symbol check, parameters unchanged.
