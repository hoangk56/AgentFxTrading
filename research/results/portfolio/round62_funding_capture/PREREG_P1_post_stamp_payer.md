# Pre-registration P1: trade the payer side in the hour after an extreme Binance funding stamp (round 62)

Written before any HOLD (2025-01-01..2026-10-29) price around a stamp was pulled; the time is stamped in the "Run"
section from `date -u`. Rule declared 13:16 UTC in [HYPOTHESES.md](HYPOTHESES.md) (addendum P1). Nothing below may
change after HOLD is seen.

## Rule (fixed)
- Universe: Binance USDT-M perps. Funding history: full for every symbol that was ever top-40 by volume
  (research/data/binance/funding), first 75 days for all other listings (funding_window). Same definition in HOLD.
- Event: stamp T on symbol s with |f_prev| >= 30 bp, f_prev = the realised rate of the previous stamp of s.
- Side: payer of f_prev (long after a positive stamp, short after a negative one). Enter at the open of the 1h bar
  starting T (first trade after the stamp, no funding paid), exit at the close of that bar (T + 1h, before any next
  stamp). Costs 0.20 % round trip (0.12 % BTC / ETH). Code: `code/capture.py` (`events`, key `p1`).

## Evidence before HOLD (net per trade, t clustered by UTC day)
See the round report for the full table. P1 IS 2020-21: n 2,096, +85.4 bp, SR/trade 0.265, t 2.76; VAL 2022-24:
n 1,985, +49.7 bp, SR 0.120, t 5.05. Symbols not seen when P1 was declared (243 of 326): IS t 2.84, VAL t 4.47.
Every year positive; costs x1.5 IS t 2.43 / VAL 4.03; beats 100 % of random same-symbol hours in both eras; dose
monotone in |f_prev|; both sides positive; correlation with C3 daily 0.02.

## Power
VAL rate ~660 trades / yr -> ~1,200 HOLD trades. At VAL size: 0.120 x sqrt(1,200) = 4.2 >= 3. At half VAL size (the
caution for the 25 % seen before declaring): 2.1.

## Pass bar at HOLD (all of)
1. Net mean > 0 and t (day-clustered) >= 2.0.
2. Net > 0 at costs x1.5, and with entry at T + 5 min on 1m klines (exit T + 60 min).
3. Both HOLD years (2025, 2026 to 10-29) net > 0.
4. Beats >= 80 % of 500 random same-symbol payer-side hours (+-3 days, as in IS / VAL).
Passing all four = LIVE tier.

## Run
Pull HOLD 1h and 1m klines (`code/pull_1h.py`, `code/pull_1m.py` with start 2025-01-01, end 2026-10-29 23:59:59),
then `code/hold_run.py` once; output appended below.
