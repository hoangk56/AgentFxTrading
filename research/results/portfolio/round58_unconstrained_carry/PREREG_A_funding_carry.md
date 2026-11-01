# Pre-registration A: delta-neutral perp funding carry on Binance (round 58), 2026-10-31

Written 2026-10-31 11:56 UTC (from `date -u`), before any HOLD (2025-01-01..2026-10-29) return of this mechanism was
computed. Nothing below may change after HOLD is seen; a failed rule is reported as failed. Hypotheses declared at
10:57 UTC in [HYPOTHESES_A.md](HYPOTHESES_A.md); this file only fixes the IS picks and the HOLD bar.

## Context
The user lifted the fixed operational limits on 2026-10-31 ("lần này không có ràng buộc gì cả"): holds > 5 days,
more than 3 positions, a venue other than IC / cTrader. The LIVE statistical bar is unchanged. This mechanism (long
spot + short USDT-M perpetual, collect funding) was never testable before: it needs Binance, multi-month holds and up
to 10 concurrent pairs.

## Rules (fixed)
Common: Binance spot + USDT-M perpetual, daily decisions at the 1d close (00:00 UTC). A position on coin i = long q
spot + short q perp, constant notional C / K (rebalanced; rebalancing cost ignored). Daily P&L per unit notional =
(dS - dF) / S_prev + funding stamps of the UTC day x F_prev / S_prev. Costs per side per coin = 0.10 % spot taker +
0.05 % perp taker + 2 x half-spread (0.01 % BTC / ETH, 0.03 % top-10, 0.05 % others). Signal = trailing-L-day mean of
daily funding sums x 365. Enter when signal > theta_in (ranked by signal, free slots only), exit at the close when
signal < theta_out or when data ends (delisting: exit at the last close). Code: `code/carry.py` `simulate`.

- **A3 (primary)**: BTCUSDT + ETHUSDT only, K = 2, L = 14, theta_in = 10 %/yr, theta_out = 0. Picked on IS as the
  highest net Sharpe of the 18-cell grid (`code/a2_grid.py ... A3`).
- **A2 (secondary)**: universe = top 30 by trailing-30-day perp quote volume among perps listed >= 60 days with a
  spot pair, K = 10, L = 7, theta_in = 10 %/yr, theta_out = 0. Highest net Sharpe of the same grid on IS.

## Evidence before HOLD (net, unit = daily book return, t = Newey-West lag 10)

| Rule | Era | ann. net | vol | t_nw | years > 0 | costs x1.5 | 1 day late | random beaten |
|---|---|---|---|---|---|---|---|---|
| A3 | IS 2020-21 | +26.9 % | 2.3 % | 7.30 | 2/2 | +26.7 % | +26.8 % | 96.5 % |
| A3 | VAL 2022-24 | +6.1 % | 0.6 % | 6.97 | 3/3 (2022 +0.55 %) | +6.0 % | +6.1 % | 99.5 % |
| A2 | IS 2020-21 | +29.3 % | 2.5 % | 6.89 | 2/2 | +28.6 % | +28.9 % | 100 % |
| A2 | VAL 2022-24 | +8.8 % | 1.2 % | 6.63 | 3/3 (2022 +1.32 %) | +7.9 % | +8.1 % | 100 % |

Baseline A1 (always on, BTC): IS +23.5 %/yr, VAL +7.8 %/yr. Correlation with C3 daily R: 0.02-0.05. Worst day: A3
-1.17 % (2020-03-12 basis blow-out), A2 -0.78 %. Drop the top 5 days: t_nw 5.5 / 5.6 (A3), 5.5 / 4.0 (A2).

Expected HOLD power at VAL size: t_nw x sqrt(669 / 1096) = 5.4 (A3), 5.2 (A2) >= 3. VAL is already far below IS
(funding compressed after 2021), so the rule is treated as decaying: at half the VAL size the expected HOLD t is ~2.7.

## Pass bar at HOLD (each rule separately; all of)
1. Net annualised return > 0 and t_nw >= 2.25 (two rules from one family: about a one-sided 1.25 % test each).
2. Net > 0 at costs x1.5 and with the signal lagged one day.
3. Every HOLD calendar year (2025, 2026 to 10-29) net > 0.
4. Beats >= 80 % of 500 random draws (same episodes and durations, random coins from that day's universe, random
   entry days in HOLD).

A rule passing all four is LIVE tier. If A3 passes it is the candidate; A2 passing alone is a candidate with more
tail risk (alt-coin basis, delistings). Reported, not judged: per-episode P&L, worst days, max drawdown.

## Data
- Binance REST, pulled 2026-10-31 10:58-12:10 UTC (`code/pull_binance.py`, request logs in research/data/binance/*/
  requests.log): perp 1d klines for 891 USDT perps (incl. delisted), funding + spot 1d for the 214 symbols that were
  ever top-40 by perp volume (aged >= 60 d) before 2025, plus the 171 symbols that entered that top-40 in 2025-26
  (selected by volume only, before any HOLD return was computed).
- HOLD = 2025-01-01..2026-10-29: clean for this mechanism (no round has used crypto funding returns after 2024; round 37
  F cut at 2024-12-31).

## Run
`cd code && ../../../../.venv/bin/python -I hold_run.py <all_syms.txt>` once, output appended below.

## Execution notes for a bot (not part of the bar)
The short perp must be margined by the spot coin itself (Binance Multi-Assets / Portfolio Margin) or kept at low
leverage with a top-up rule: in IS, BTC and ETH rose 6x and 24x during single episodes. Daily data cannot show
intraday ADL (auto-deleveraging of the profitable short in a crash) or venue failure; both are real risks the bar does
not measure.

## Code hashes at registration (sha256, first 16; `python -m research.tools.prereg_hashes`)
- `research/results/portfolio/round58_unconstrained_carry/code/carry.py` 50a3b95efc5d83ad
- `research/results/portfolio/round58_unconstrained_carry/code/hold_run.py` f9f64a87cc68c990
- `research/results/portfolio/round58_unconstrained_carry/code/pull_binance.py` 910108aeb83e74ce
- `research/results/portfolio/round58_unconstrained_carry/code/all_syms.txt` 6d06b2acc0c7a516

## HOLD result (run once, 2026-10-31 11:59:13-11:59:15 UTC, hashed code; full output in code/hold_output_2026-10-31.txt)

| Rule | HOLD days | ann. net | vol | t_nw | 2025 | 2026 (to 10-29) | costs x1.5 | 1 day late | random beaten | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| A3 | 667 | +1.91 % | 0.28 % | 5.62 | +3.41 % | +0.08 % | +1.77 % | +1.89 % | 100 % | **PASS (all 4)** |
| A2 | 667 | +1.36 % | 1.61 % | 1.73 | +0.58 % | +1.90 % | +0.58 % | -0.21 % | 100 % | FAIL (1, 2) |

A3 episodes: BTC 2025-01-01..05-02 +1.16 %, BTC 2025-07-22..10-21 +1.21 %, ETH 2025-01-08..2026-02-04 +4.61 %; flat
since 2026-02-04 (14-day funding below 0 or 10 %/yr). Mean funding in HOLD: BTC 5.1 %/yr (2025), 3.1 % (2026); ETH
4.9 % / 2.1 %. Always-on A1 BTC: +5.1 % (2025), +2.5 % (2026).

**Verdict: A3 passes the registered LIVE bar. A2 fails.** Size, which the bar does not test: A3 earned +1.9 %/yr on
notional in HOLD (IS +26.9 %, VAL +6.1 %), and the whole carry, always on, earned about the US cash rate (~4 %) in 2025
and less in 2026. Capital in this trade cannot also sit in T-bills, so the excess return over cash in HOLD is about
zero or negative. See the round report for what this means for a live bot.
