# PREREG Q1: COIN-M perp vs USDT-M perp gap reversion on Binance (Q1_k100_H72), DEMO tier

Registered 2026-11-01 10:43 UTC (from `date -u`) by the coordinator, before any 2025-26 value of this rule was read
(the HOLD 1h pull was running into research/data/binance_cm_hold/ and had not been read). Draft and full IS / VAL
tables, caveats, demo plan: [PREREG_DRAFT_Q_cm_um_perp_gap.md](PREREG_DRAFT_Q_cm_um_perp_gap.md) (stream Q, 10:31 UTC).
HOLD 2025-01-01..2026-10-29 is opened once by `coord/hold/hold_run.py run`.

## Rule (frozen, as the draft)
Every COIN-M perpetual with a USDT-M perpetual of the same coin; hourly gap g = ln(COIN-M close / USDT-M close), both
legs >= 20 trades; reference = median of g over the previous 168 h (>= 120 valid). When |g - median| > 100 bp (and both
1h closes equal the last 1m close within 1 bp), long the cheap perp / short the rich one in equal USD notional at the
open of the 1m bar 1 minute after the hourly close; exit when the gap has halved (first hourly close) or after 72 h, at
the open of the 1m bar 1 minute after that hour. Funding of both legs at real stamps; 20 bp taker + 2 x half-spreads.

## IS / VAL (stream Q; reproduced exactly by `coord/hold/check_isval.py`)
IS n 54, +439.8 bp, t 2.20 (22 event-days); VAL n 181, +77.7 bp, t 3.82 (33 event-days); 5 / 5 years; x1.5 and T + 2
min positive. 95-98 % of P&L on 5 crash days; outside them VAL +12.6 bp (t 0.29). Power per event-day 1.47: DEMO only.

## HOLD implementation (declared)
- `hold_pull.py`: every *_PERP in the data.binance.vision COIN-M monthly-klines listing (50 symbols) and <COIN>USDT:
  1h klines 2024-12..2026-09 monthly + 2026-10-01..29 daily (missing daily files from fapi / dapi REST); COIN-M funding
  monthly + dapi for 2026-10. USDT-M funding from research/data/binance/funding (else binance_cm_hold/funding).
- `hold_run.py`: stream Q's unchanged q.py / run.py with T0 = 2024-12-01 (31 days of median warm-up), CUT =
  2026-10-30, data folder binance_cm_hold; trades with entry in 2025-01-01..(2026-10-30 - 74 h); `need` lists 1m
  days, `hold_m1.py` pulls them (daily zip, else REST), `run` prices them.

## HOLD pass bar (DEMO, as the draft)
Net > 0 per trade at T + 1 min, taker costs. Fail if net <= 0. Fewer than 3 event-days = inconclusive. Reported: t (day
cluster), median, T + 2 min, x1.5, top-5 days share, event-days, per year. Pass = DEMO (demo plan / stop / live rules
in the draft; the user decides on any bot).

## Hashes (`python -m research.tools.prereg_hashes`, 10:43 UTC)
- `research/results/portfolio/round64_parallel/Q/code/q.py` 5ed796533eff92fd
- `research/results/portfolio/round64_parallel/Q/code/run.py` f986e7bcb37fc4bc
- `research/results/portfolio/round64_parallel/Q/coord/hold/check_isval.py` 9594a847c99ac8bd
- `research/results/portfolio/round64_parallel/Q/coord/hold/hold_pull.py` ec8002bde24d420c
- `research/results/portfolio/round64_parallel/Q/coord/hold/hold_m1.py` 852faaf6aba953d5
- `research/results/portfolio/round64_parallel/Q/coord/hold/hold_run.py` 410a02a39ddcabe2

## Data amendment before the run (2026-11-01 11:33 UTC, no HOLD value read)
The pull retried HTTP 400 (delisted COIN-M symbols are unknown to the dapi REST fallback) 6 times per missing daily
file and stalled; `hold_pull.py` now treats 400 like 404 (new hash cd3334984a0a07ac) and was restarted (finished
files are skipped; files are written atomically). Rule and run code unchanged.

## HOLD result
(appended after the single run)

1h data pulled 10:43-13:58 UTC (50 COIN-M perps, all USDT-M funding local); 1m days listed and pulled 14:05-14:08 UTC
(37 trades, 82 days, none missing). Run once 2026-11-01 14:08 UTC (`hold_run.py run`, output
`coord/hold/hold_output_2026-11-01.txt`):

| HOLD 2025-01..2026-10 | n | event-days | net bp | t (day) | median | win | x1.5 | T + 2 min | price / funding / cost | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1_k100_H72 | 37 | 7 | **+299.2** | 2.15 | +116.9 | 95 % | +284.3 (2.04) | +333.8 (2.11) | +301.7 / +27.3 / 29.8 | +311.6 (n 35) | +82.9 (n 2) |

- **DEMO bar (net > 0, >= 3 event-days): PASS.** Q1 is a DEMO candidate that passed HOLD.
- As registered, it is a crash-day rule: top-5 days = 101 % of the net; the largest days are 2025-10-10 / 10-11 (the
  October 2025 liquidation cascade), 2025-02-03 / 02-06, 2026-06-30. Per event-day Sharpe 0.41 on 7 days.
- Demo plan / stop / live rules as the draft (stop if cumulative net after 8 demo event-days < 0; live: HOLD + demo
  pooled t >= 2.5 on >= 15 event-days). At ~4 event-days a year, promotion takes years: low priority for a bot.
