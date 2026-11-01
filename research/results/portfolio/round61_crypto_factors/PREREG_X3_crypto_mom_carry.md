# Pre-registration X3: weekly crypto momentum + funding-carry long-short on Binance perps (round 61), 2026-10-31

Written 2026-10-31 12:57 UTC (from `date -u`), before any HOLD (2025-01-01..2026-10-29) factor return was computed.
Declared at 12:52 UTC in [HYPOTHESES.md](HYPOTHESES.md); nothing changed since.

## Rule (fixed)
Each Sunday 1d candle close (Monday 00:00 UTC): universe = top 40 Binance USDT-M perps by trailing-30-day quote
volume, listed >= 60 days, excl. stable / index / TradFi perps. X1 = long top 8 / short bottom 8 by past-28-day return;
X2 = long the 8 lowest / short the 8 highest trailing-7-day mean funding. X3 = 50 / 50 of X1 and X2 weekly returns.
Equal weight, gross 1 per side, held 7 days, funding on every leg, costs turnover x (0.05 % + 0.03 % half-spread;
0.01 % BTC / ETH). Code `code/factors.py` `book`.

## Evidence before HOLD (weekly, t Newey-West lag 4)
| Era | weeks | mean / wk | SR / wk | t_nw | years | x1.5 | late | random beaten | corr C3 |
|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 89 | +2.39 % | 0.343 | 4.32 | 2/2 | +2.32 % | +1.81 % | 100 % | -0.02 |
| VAL 2022-24 | 156 | +0.83 % | 0.136 | 1.51 | 3/3 (2022 +8.0) | +0.75 % | +0.69 % | 100 % | -0.03 |

X1 alone IS t 2.37 / VAL 1.28; X2 alone 3.41 / 1.29 (both fail the LIVE t bar; X3 was declared as the combination).

## Tier
Passes every LIVE item on IS / VAL except HOLD power: 0.136 x sqrt(95) = 1.33 < 3. So **DEMO** at most; the HOLD look
below can only confirm or kill the DEMO candidate (bar: X3 net > 0), not make it LIVE.

## DEMO terms (if HOLD passes)
- Demo: 52 rebalances / yr, small fixed gross (e.g. $100 per leg), Binance demo / testnet or paper log.
- Stop: cut if the cumulative demo return after 26 weeks is below -20 % of gross per side (~1.2 sd under VAL's mean).
- Promotion to LIVE: HOLD + demo weeks pooled, t_nw >= 2.5 (at VAL size this takes ~5 years of weekly data; realistic
  only if the effect is larger than VAL's).

## Run
`cd code && ../../../../.venv/bin/python -I hold_run.py perp_all.txt` once; output appended below.

## Code hashes at registration (sha256, first 16; `python -m research.tools.prereg_hashes`)
- `research/results/portfolio/round61_crypto_factors/code/factors.py` 67e4a1efa622ee31
- `research/results/portfolio/round61_crypto_factors/code/hold_run.py` 4b9c5157a2c7af95
- `research/results/portfolio/round61_crypto_factors/code/perp_all.txt` ec0a130920ba4b14
- `research/results/portfolio/round60_new_listings/code/listings.py` 1d728118b613023a
- `research/results/portfolio/round58_unconstrained_carry/code/carry.py` 50a3b95efc5d83ad

## HOLD result (run once, 2026-10-31 12:57:34-13:00:28 UTC, hashed code; output in code/hold_output_2026-10-31.txt)
- 94 weeks (2025-01-05..2026-10-18): X3 +1.141 %/wk, sd 12.0 %, SR/wk 0.095, t_nw 1.16; costs x1.5 +1.066; late
  +1.400; beats 95.8 % of 500 shuffled sorts; 2025 +65.8 %, 2026 +41.4 % (sums of weekly returns, gross 1 per side).
- Reported: X1 momentum +3.287 %/wk (t_nw 2.47), X2 funding carry -1.005 %/wk (t -0.72).
- Worst week -30.0 %, max drawdown -57.0 % (sum of weekly returns).

**Verdict: passes the DEMO bar (net > 0). DEMO candidate, not LIVE** (HOLD t 1.16; pooled promotion t >= 2.5 needs
years of demo weeks). The HOLD edge came from momentum; carry lost. Size any demo for a -30 % week.
