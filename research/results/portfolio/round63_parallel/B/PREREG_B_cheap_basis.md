# PRE-REGISTRATION B (frozen by the coordinator 2026-10-31 15:25 UTC, from `date -u`): DEMO-tier HOLD look

Frozen copy of PREREG_DRAFT_B_cheap_basis.md below; the rule, cell and bar may not change. HOLD = 2025-01-01..2026-10-29, opened once. The HOLD script must import code/basis.py and code/universe.py unchanged (hashes below) and only override the cut / era constants at runtime.

Draft written 2026-10-31 15:25 UTC by stream B (round 63). HOLD (2025-01-01..2026-10-29) NOT opened; the coordinator
opens it once. Tier: **DEMO** (IS t 2.46 < 2.5 rules out LIVE). Strong caveats in [STREAM_B.md](STREAM_B.md).

## Rule (frozen; code `code/basis.py` simulate(coins, 100, 24, -1), loader `load()`)
- Universe: point-in-time top-60 Binance USDT-M perps by trailing 30-day perp quote volume (previous day), listed >= 60
  days, Binance spot pair live, BTC / ETH / stablecoins / BTCDOM / PAXG excluded.
- Hourly basis b = ln(perp close / (factor x spot close)); valid bar: >= 20 trades on both legs, relative tick <= 5 bp
  both legs (30-day block estimate). Reference m = median of b over the previous 168 h (>= 120 valid).
- Event: b - m < -100 bp at the close of hour h. Enter at the open of h+1: long perp, short spot (margin borrow),
  1 unit notional each. One open trade per coin.
- Exit at the open after the first close c >= h+1 with b_c - m_h >= (b_h - m_h) / 2, else at the open of h+25.
- P&L: -(spot return) + (perp return) - funding on stamps in (entry, exit] - 30 bp fees - 4 x half-spread (3 bp rank <
  10, else 5 bp) - borrow 40 %/yr pro rata - Fed funds on the spot notional.

## IS / VAL numbers (declared cell, taker costs)
| era | n | net bp | median | t (day cluster) | x1.5 | 1 h late | random beaten |
|---|---|---|---|---|---|---|---|
| IS 2020-21 | 303 | +286.5 | +110.2 | 2.46 | +262.0 | +118.4 (median -23.1) | 100 % |
| VAL 2022-24 | 333 | +174.6 | +95.6 | 6.41 | +150.5 | +68.6 (median -10.0) | 100 % |
Years 2020-24: +75 / +319 / +265 / +149 / +93 bp (5 / 5).

## Power at VAL size
111 trades / yr, 48 event-days / yr. HOLD ~1.8 yr: per trade 0.270 x sqrt(200) = 3.82; per event-day 0.498 x sqrt(86)
= 4.63. Graded power = 3.82 (but the tier is DEMO because of IS t).

## HOLD pass bar (DEMO)
HOLD net > 0 per trade at taker costs with t (day cluster) reported; also report median, one-hour-late, x1.5, and the
share of P&L from the top 5 coins / days. Fail if net <= 0. Run once, HOLD cut 2025-01-01..2026-10-29.

## Demo plan (if HOLD passes and the user approves margin shorting)
- Expected ~100 trades / yr; small fixed notional per trade; log the real borrowable amount and hourly borrow rate at
  each signal (trades without borrow are recorded as "not fillable", counted against the rule), the fill prices and the
  book spread at entry.
- Stop rule: stop if cumulative net after 40 demo signals (fillable or not) < 0, or if > 30 % of signals are not
  fillable for lack of borrow.
- Live rule: HOLD + demo pooled t >= 2.5 on fillable trades, with not-fillable signals counted at 0.

## Code hashes at registration (sha256, first 16)
- `research/results/portfolio/round63_parallel/B/code/basis.py` 46a5f647e1fc33f2
- `research/results/portfolio/round63_parallel/B/code/universe.py` e4a9ae6a1a841feb
- `research/results/portfolio/round63_parallel/B/code/pull.py` 6234ca2300a998c8

HOLD run started Sat Oct 31 15:50:51 UTC 2026

## HOLD result
Written Sat Oct 31 15:52:02 UTC 2026 (from `date -u`). Run once by `code/hold_run.py run` (frozen basis.py / universe.py / pull.py, hashes
re-verified 15:27 UTC: 46a5f647e1fc33f2 / e4a9ae6a1a841feb / 6234ca2300a998c8; only universe.END, basis.CUT ->
2026-10-30 00:00 UTC and basis.ERAS['HOLD'] overridden). Full output: [code/hold_output_2026-10-31.txt](code/hold_output_2026-10-31.txt).
Universe: point-in-time top-60 through HOLD (`code/hold_universe.py`, `universe60_hold.csv`; pre-2025 universe
identical to the registered one): 291 alts, 290 loaded (LITUSDT: Binance spot pair delisted, 0 spot rows).
Reproduction with the extended data: IS 303 / +286.5 / t 2.46 (identical), VAL 336 / +174.6 / t 6.47 (3 late-2024 trades
previously cut at the 2024 data end now complete).

| cell k100_H24_cheap, taker | n | event-days | coins | net bp | median | t (day) | x1.5 | 1 h late (n / net / median / t) |
|---|---|---|---|---|---|---|---|---|
| HOLD 2025-01-01..2026-10-29 | 429 | 206 | 60 | **+213.5** | +126.7 | **14.38** | +188.7 (t 12.71) | 533 / +114.7 / +24.3 / 8.27 |

- Per year: 2025 n 113, +138.7 bp (median +99.5, t 8.50); 2026 n 316, +240.3 bp (median +133.3, t 12.76).
- Components per trade: price convergence +139.5, funding received +126.0, costs -49.7, carry (cash + 40 %/yr borrow)
  -2.2 bp; mean hold 4.4 h; 0 forced exits; adverse perp move > 25 % in 2.8 % of trades, > 50 % in 0.2 %.
- Concentration: top 5 coins 40 % of P&L (DEXE, HOME, ONE, ONG, SENT); top 5 days 15 % (2026-07-21, 08-26, 06-07,
  06-11, 07-22); top 10 |net| trades 16 %; 1 %-trimmed mean +200.3 bp.
- Worst trades: -13 bp (VANRY 2026-07-27), -2 (AVNT), +2, +2, +6 ...; only 2 of 429 trades lose. Best: DEXE 2026-07-22
  +2,146 bp of which funding +2,194 (perp fell 4.21 -> 2.49 in the hold).
- Data: 1h perp + spot for 291 symbols and funding for 76 pulled 15:28-15:48 UTC (2,979 requests, 1 transient
  disconnect retried, no 418 / 429 / 403). HOLD universe coin-hours with a valid deviation 59.3 % (VAL 67.1 %, IS
  93.9 %): the declared 5 bp relative-tick filter removes 40.0 % (VAL 32.1 %), missing bars 1.1 %. DFF.csv ends
  2026-10-01, so the cash charge is 0 for 2026-10-02..29 (< 0.4 bp per trade).

**Verdict: PASS of the registered DEMO bar (HOLD net +213.5 bp > 0 at taker costs, t 14.4).** Not LIVE (tier fixed at
DEMO by IS t 2.46). Caveats the bar does not test: 59 % of HOLD net is funding received while long a perp in deeply
negative funding, i.e. the squeeze states where shorting spot needs margin borrow that is likely scarce or very
expensive (borrow availability unmodelled, 40 %/yr assumed); the edge is front-loaded (one hour late keeps +115 bp
mean but the median falls to +24 bp); a 99.5 % win rate at taker costs on close-to-close 1h prints says the entry-bar
open prices may not be fillable at the modelled 3-5 bp half-spread. The demo plan above (borrow logging, not-fillable
signals counted at 0, stop rules) is what tests these.
