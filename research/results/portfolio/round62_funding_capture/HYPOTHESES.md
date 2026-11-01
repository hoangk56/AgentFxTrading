# Round 62: hold the receiving side through extreme altcoin funding stamps (declared before any price around a stamp was loaded)

Written 2026-10-31 13:03 UTC (from `date -u`). Funding stamps are local (rounds 58 / 60); no intraday price has been
pulled, and no stamp has been joined to a return.

## Why
Round 37 F (BTC / ETH at IC) found that the price drifts toward the receiver into a large-funding stamp (payers close
before paying: short into a positive-funding stamp gained +6 bp in 15 min, both eras) but it exited before the stamp,
so it never collected the funding, and BTC's rates are a few bp. Altcoin perps on Binance pay 10-200 bp per stamp in
squeezes and listings, often at 4h / 1h intervals. The receiving side held through the stamp earns f plus the
payers' pre-stamp exit pressure, minus whatever adverse move the crowding brings. Many events per year, so power is
reachable if the per-trade Sharpe is ~0.08 or more. Different from rounds 58-61: one stamp, hours, not carry.

## Data (to pull, public)
- Binance USDT-M 1h klines (`fapi/v1/klines`, interval 1h) for every symbol with at least one qualifying stamp.
- Funding stamps: research/data/binance/funding (full history, 384 symbols) and funding_window (first 75 days of the
  other listings).

## Rule (fixed)
- Event: a funding stamp T on symbol s whose previous stamp's realised rate f_prev (known since T - interval) has
  |f_prev| >= 30 bp (main tier). Also reported: 10, 50, 100 bp tiers.
- Side: receiver of f_prev (f_prev > 0 -> short, < 0 -> long). Enter at the open of the 1h bar starting T - 1h, exit at
  the close of the 1h bar starting T (T + 1h). P&L per unit notional = side x (exit / entry - 1) - side x f_T
  (side +1 long, -1 short; the realised rate at T is received when it keeps f_prev's sign, paid if it flipped).
- Costs: 0.05 % taker per side + 0.05 % half-spread per side = 0.20 % round trip (BTC / ETH 0.12 %).
- One event per symbol per stamp; events on the same symbol may follow each other (consecutive stamps).

## Unit, eras, bars
- Unit: trade (net); t clustered by UTC day. IS 2020-01..2021-12, VAL 2022-01..2024-12, HOLD 2025-01..2026-10-29 cut at
  load (klines requested to 2024-12-31 23:59 for IS / VAL work; HOLD pulled only after a prereg).
- Random benchmark: same symbol and side, a random 2h window within +-3 days that contains no stamp (500 draws); the
  rule must beat >= 95 %. It isolates the stamp from the coin's general drift (high-funding coins fall, round 61 X2).
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years > 0, > 95 % random, > 0 at costs x1.5 and with entry one hour earlier
  (T - 2h) and exit one hour later; HOLD power = Sharpe per trade (VAL) x sqrt(expected HOLD trades) >= 3.
- Margin-only, two hours: no cash charge.

Addendum 13:05 UTC (`date -u` at 13:05:10; before any return): for symbols whose funding interval is <= 2h every 2h window holds a stamp, so
the random windows there include the funding of the stamps they contain (same side); elsewhere they contain none.
Reported split: pre-stamp leg (entry -> close of the T - 1h bar) and post leg (-> close of the T bar).

## Addendum P1 (13:16 UTC, from `date -u`): post-stamp payer rule, declared after a partial look
A dry run on 83 of 326 symbols (A-C alphabetically, IS / VAL) showed the receiver loses: funding +28 / +49 bp, but the
hour after the stamp moves against the receiver by -105 / -66 bp (t -3.1 / -3.6). That is the "reopen after the stamp"
side round 37 F declared in advance for BTC (flat there). Declared now, before the full panel:
- **P1**: |f_prev| >= 30 bp; side = PAYER (sign of f_prev: long after a positive stamp, short after a negative one);
  enter at the open of the 1h bar starting T (first trade after the stamp, so no funding is paid), exit at its close
  (T + 1h). Costs 0.20 % round trip (0.12 % BTC / ETH). Same eras, clustering, random benchmark (random 1h bars of the
  same symbol +-3 days, payer side, no stamp at their start where interval > 2h) and LIVE bar as above.
- Because 25 % of the IS / VAL symbols were seen, the HOLD expectation uses half the VAL size, and the full-panel
  IS / VAL numbers on the other 243 symbols are reported separately as a quasi-fresh check.
- Robustness required before any prereg: 5m klines around the stamps (entry at T + 5 min, exit T + 60 min) must keep
  the sign; entry latency is the obvious failure mode.

## Addendum P2 (14:31 UTC, from `date -u`): second-level execution, declared after the VAL aggTrades sample
1m klines showed P1's VAL edge sits in the first minute (entry T+1 min: -11.6 bp). A random sample of 197 VAL stamps
(aggTrades, seed 7) showed the payer move builds over ~5-10 s: +4.7 bp median at 1 s, +40 at 10 s. Seen cells: entry
T+0.5 / 1 / 2 / 3 / 5 s x exit 10 / 30 / 59 s (entry T+1 s, exit T+59 s: +25.5 bp net, SR 0.256, t 3.36).
- **P2 (fixed now)**: P1's events and side; entry = last aggTrade price at T + 1.0 s (taker), exit = last aggTrade at
  T + 60 s (taker); costs 0.20 % round trip (0.12 % BTC / ETH). Entry 1 s is "first feasible", exit 60 s is the
  natural one-minute exit, not the best seen cell (10 s was better).
- Checks before any prereg, on samples not yet seen: IS 2020-21 random 200 stamps (seed 11) and a second VAL sample of
  200 stamps excluding the first sample (seed 13). Bar on each: net > 0, t (day-clustered) >= 2.0; entry 2 s also > 0.
- HOLD expectation: half the VAL-sample size (post-hoc execution choice).
