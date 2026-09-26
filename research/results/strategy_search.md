# Strategy search on research/data (2026-09-25)

Data: tick cache 2024-12-29..2026-09-24 for 15 symbols (M1 cache in research/data/m1), plus M15 zbars for
Sep-Dec 2024 (BTC/ETH) and Jul-Dec 2024 (XAU, indices) as never-looked-at data. Periods: P1 = 2025,
P2 = Jan-May 2026, P3 = Jun-Sep 2026. Costs: bid/ask, commission, swaps (research/specs.py).
Code: research/scan/ (m1 cache, M1 engine, rule bank, scorer, tick-level sim). Pre-registrations:
strategy_prereg.md.

## Cost vs ATR (spread + commission, median)

| | M15 | H1 | H4 | D1 |
|---|---|---|---|---|
| DE40 / US30 / USTEC | 0.024-0.030 | 0.012 | 0.006 | 0.002 |
| BTC / XAU | 0.05 | 0.023 | 0.011 | 0.004 |
| FX majors, JPY crosses, UK100 | 0.09-0.20 | 0.04-0.09 | 0.02-0.05 | 0.01-0.02 |
| ETH | 0.25 | 0.12 | 0.06 | 0.02 |

## Rejected

- Hour-of-day drift: the only persistent pattern is the 17:00 NY rollover spread widening (bid dips, not tradeable).
- Trend following (Donchian) D1/H4/H1 on all 15: negative in 2025 (-0.10 to -0.27R).
- K1 FX weekly fade (pre-registered, 8 FX pairs D1): 2025 +0.098R (t 2.6, 8/8 pairs) -> 2026 -0.073R (t -1.8,
  1/8 pairs). 72-cell grid: 88 % positive in 2025, 0 % in 2026, corr(IS, OOS) -0.40. Regime flip.
- K2 index ORB 60 min (pre-registered): 2025 +0.130R (t 2.3) -> 2026 +0.005R.
- Noise-area intraday momentum on indices: 2025 t < 1. Intraday segment correlations: mostly April-2025 outliers.
- Crypto multi-bar momentum (L20): negative after costs.
- Rule bank, 552 configs (z-move / Donchian / RSI, follow + fade, M15-D1) x 8 symbol groups: 0 configs with
  t >= 2 in all of P1, P2, P3.

## Best candidate: BTC-S1 (BTC shock-bar momentum)

BTCUSD M15 bid bars. move = (C - C[1]) / ATR20 (SMA of TR). |move| > 2.5 -> follow at the next tick;
SL 2 x ATR, TP 2 x ATR from the fill, time exit after 12 bars (3 h). One position at a time.

| Test | n | mean R | t |
|---|---|---|---|
| Sep-Dec 2024, unseen, bar-level | 60 | +0.218 | +1.8 |
| 2025, M1-level | 211 | +0.135 | +2.1 |
| Jan-May 2026, M1-level | 102 | +0.070 | +0.8 |
| Jun-Sep 2026, M1-level | 76 | +0.134 | +1.2 |
| 2025, tick-level, $2000, live sizing | 203 | +0.100 | +1.4 |
| 2026 YTD, tick-level, $2000 | 178 | +0.093 | +1.2 |

Tick-level $2000: 2025 +$207 (+10.4 %, max DD $103), 2026 YTD +$168 (+8.4 %, max DD $67), 6 entries refused
(min-lot guard), 15/21 months positive; similar across UTC hours, long/short, weekend/weekday.
Random control (same rate/exits, 20 seeds): -0.027R (2025), -0.036R (2026); BTC-S1 beat 20/20 and 19/20 seeds.
Plateau: M15, SL 2/TP 2, every Z >= 2 x every H in 3..24 is positive in all three periods.
Weak points: fails the strict bar (t < 2 in P2, P3); chosen after a broad scan; ETH shows the effect gross
but not net (spread 11.6 bp); ~18 trades/month.

## Second: XAU-T1 (H4 Donchian 30 breakout, SL 1.5 ATR, exit after 12 bars)

Jul-Dec 2024 unseen: n 25, +0.458R (t 1.7). 2025 +0.166, P2 +0.343, P3 +0.287. Mostly the long side (gold
bull market; 2025 shorts -0.50R). Not tradeable at $2000: SL 1.5 x ATR(H4, median $30) at the 1 oz minimum
= $45 risk vs a $15 cap.

## Round 2 (more quant families)

| Candidate | Family | Result |
|---|---|---|
| Pairs, 14 pairs (US30-USTEC, DE40-UK100, EURUSD-GBPUSD, EURJPY-GBPJPY, BTC-ETH ...) | stat-arb, rolling-OLS z | nothing in 2025, not even gross of costs |
| Lead-lag M1/M5 (US -> DE40, DE40 -> UK100, BTC -> USTEC ...) | cross-asset | significant corr (+2..4 %) but 1-2 spreads in size; rules ~0 |
| X1 cross-sectional FX reversal (currency strength, H4, 5 d) | cross-sectional | 2025 +0.74 ATR (t 2.4) -> 2026 -0.09 |
| VB1 index volatility breakout | intraday momentum | P1 +0.10 (t 2.1), P2 +0.08, P3 -0.14 |
| WF1 walk-forward ridge, 14 features, monthly refit | ML | M15 all -0.08R (t -17); low-cost group -0.005R |
| FXM1 regime switch fade/follow on trailing 120 d | meta | May-Dec 2025 +0.11, P2 -0.10 (t -2.3), P3 0.00 |
| LC1 US last-30-min fade of the mid-session move | intraday | +0.040 / +0.019 / +0.025, but Jul-Dec 2024 -0.001 |
| GF1 US opening-gap fade | intraday | 2026 +0.05 (t 0.8) |
| OD1 overnight drift 02-03 NY (Boyarchenko et al.) | literature | 2025 -0.006, 2026 +0.029 (t 2.6): sign flip |
| TOM turn-of-month, long indices intraday | literature | 2025 +0.041 (t 1.7), 2026 +0.088 (t 3.0), other days -0.008; Jul-Dec 2024 +0.002 (23 days) |
| MEF month-end London fix USD flow | literature | 20 events, +0.15R (t 1.0) |
| Trend families by asset | bank re-read | positive only for XAU (H4 Donchian 8/9 cells in all periods) and crypto D1 (ETH, 20-40 trades) |

BTC-S1 latency check (tick level): entry 1 s / 3 s / 10 s / 30 s late -> 2025 +0.092 / +0.066 / +0.092 / +0.042R,
2026 +0.094 / +0.102 / +0.042 / +0.033R. Robust to realistic latency.

Standing after round 2: BTC-S1 is still the only candidate that is positive in every period (incl. unseen
2024) and tradeable at $2000. TOM is weak (flat on 2024) and, like XAU-T1, needs stops that the $2000 min-lot
guard refuses (US30 0.1 lot x 3 % stop = $130).

## Confirmation on 2023-2024 (cache-fill jobs #105-#114, rules unchanged)

| Candidate | 2023 | 2024 | 2025 | 2026 YTD | Verdict |
|---|---|---|---|---|---|
| BTC-S1 (tick, R) | +0.000 (n 222) | +0.107 (t 1.5) | +0.100 | +0.093 | FAIL: pooled 2023-24 t 1.0 |
| XAU-T1 (R) | +0.102 (t 0.5) | +0.087 (t 0.5) | +0.148 | +0.318 | FAIL: t 0.7; shorts -0.09 (gold beta) |
| TOM (R = 3 %) | +0.047, other days +0.021 | -0.014, other days +0.006 | +0.047 | +0.088 | FAIL: 2024 negative |

Fixed-lot $ (BTC 0.1, XAU 0.01, indices 0.1 each): BTC -103 / +1164 / +2154 / +260; XAU +39 / +154 / +283 / +665;
TOM +393 / -179 / +582 / +986. Combined (post hoc): +329 / +1139 / +3019 / +1911, max DD $649, 33/45 months up.
BTC spread was 5.7 bp in 2023 and 4.3 bp in 2024 vs 1.7-2.4 bp in 2025-26.

## Previously proposed next step (done 2026-09-25)

Fill the BTCUSD (and US30/USTEC/DE40/XAUUSD for TOM and XAU-T1) tick cache for 2023-2024 with cTrader backtests on the VPS and run BTC-S1 unchanged on it
(research/scan/ticksim.py, extend the date loop). Only if it holds there: a cBot + demo forward test.
