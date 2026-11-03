# Stream CF: aggressive delta (C3) and CVD divergence (C4) at prior-day POC / VAH / VAL

Written 2026-11-03 (UTC). Rules: [HYPOTHESES_CF.md](HYPOTHESES_CF.md) (16:52 UTC, before any return; two
data-hygiene notes after the coordinator's BTC footprint fix and the 1m-hole notice). Code: `CF/code/cf.py`,
`CF/code/report.py`. Full tables: `CF/out/report_BTC_ETH_SOL.txt` (pooled), `CF/out/report_BTC_ETH.txt`.

## Answer: none (no LIVE, no DEMO)
All 8 cells lose money in IS and VAL, pooled and on almost every symbol. The best IS cell (C3 x 0.4, 2R) has
t -0.67, so nothing reaches the IS bar (2.5 LIVE / 2.0 DEMO), and its VAL is -17.3 bp, t -4.32, 1st percentile of
random. Before fees the trades are about flat (-9 to +5 bp per trade): prior-day value-area levels plus a C3 / C4
confirmation give no edge that survives ~9 bp of taker costs. No PREREG_DRAFT.

## Pooled BTC + ETH + SOL, base execution (net bp per trade; t clustered by UTC day; 200 random draws)

| cell | IS n | IS bp | IS R | IS t | VAL n | VAL bp | VAL t | x1.5 VAL t | late VAL t | random pct IS / VAL | years + | power at VAL size |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C3 0.2 TPV | 1,949 | -9.67 | -0.10 | -2.79 | 3,296 | -10.68 | -5.45 | -7.60 | -5.31 | 69 / 26 | 0/5 | -4.7 |
| C3 0.2 2R | 1,801 | -7.22 | -0.10 | -1.58 | 3,059 | -14.86 | -6.04 | -7.85 | -5.53 | 72 / 3 | 0/5 | -5.0 |
| C3 0.4 TPV | 522 | -17.44 | -0.16 | -2.53 | 736 | -10.80 | -3.24 | -4.51 | -2.99 | 18 / 4.5 | 0/5 | -2.6 |
| C3 0.4 2R | 507 | -6.02 | -0.05 | -0.67 | 713 | -17.29 | -4.32 | -5.43 | -3.90 | 38.5 / 1 | 1/5 | -3.3 |
| C4 TPV | 909 | -6.53 | -0.12 | -1.18 | 1,371 | -4.85 | -1.45 | -2.71 | -1.64 | 68 / 85.5 | 1/5 | -1.2 |
| C4 2R | 878 | -9.16 | -0.13 | -1.25 | 1,318 | -3.97 | -0.92 | -1.95 | -1.18 | 39.5 / 97.5 | 1/5 | -0.8 |
| none TPV (limit at level) | 2,706 | -8.50 | -0.07 | -2.67 | 4,352 | -3.77 | -2.15 | -3.71 | -3.69 | 51.5 / 63.5 | 0/5 | -1.8 |
| none 2R (limit at level) | 2,445 | -6.15 | -0.06 | -1.44 | 3,929 | -5.39 | -2.31 | -3.58 | -3.61 | 74 / 58 | 0/5 | -1.9 |
| info: none-mkt TPV | 2,959 | -10.64 | -0.10 | -3.49 | 4,831 | -5.97 | -3.49 | -5.96 | -3.95 | - | 0/5 | -3.0 |
| info: none-mkt 2R | 2,632 | -9.28 | -0.09 | -2.25 | 4,325 | -7.48 | -3.32 | -5.30 | -3.59 | - | 0/5 | -2.7 |

Max-over-8-cells null (IS): the best random cell per draw has median t -0.15, 95th percentile 1.15. The best real cell
(t -0.67) beats 30 % of draws.

Before fees (net + fees, still after slippage and funding), bp per trade, IS / VAL: C3 0.2 TPV -1.1 / -2.0,
C3 0.2 2R +1.8 / -5.8, C3 0.4 TPV -8.7 / -2.1, C3 0.4 2R +2.9 / -8.1, C4 TPV +2.1 / +3.7, C4 2R -0.1 / +5.0,
none TPV -2.9 / +1.8, none-mkt TPV -2.0 / +2.6. Fees average 8.6-9.2 bp (market entries) and 5.6-6.0 bp (limit).
Median stop distance (1R) 74-93 bp.

## Per symbol (base; IS bp / t | VAL bp / t)

| cell | BTC | ETH | SOL |
|---|---|---|---|
| C3 0.2 TPV | -3.8 / -1.00 \| -6.8 / -3.22 | -14.4 / -2.98 \| -11.1 / -4.15 | -11.6 / -1.17 \| -15.2 / -3.28 |
| C3 0.2 2R | -3.0 / -0.59 \| -12.6 / -4.49 | -13.8 / -2.11 \| -12.9 / -3.79 | -3.3 / -0.24 \| -20.2 / -3.43 |
| C3 0.4 TPV | -10.7 / -1.48 \| -6.5 / -1.60 | -17.7 / -2.14 \| -13.1 / -2.63 | -23.2 / -1.34 \| -16.1 / -1.51 |
| C3 0.4 2R | -0.6 / -0.06 \| -13.3 / -2.68 | -1.7 / -0.14 \| -16.9 / -2.72 | -15.9 / -0.74 \| -27.0 / -2.05 |
| C4 TPV | -2.1 / -0.31 \| -6.8 / -1.78 | -18.8 / -2.39 \| +0.8 / 0.17 | +3.3 / 0.26 \| -7.7 / -1.21 |
| C4 2R | +2.1 / 0.23 \| -7.2 / -1.46 | -22.8 / -2.35 \| +5.5 / 0.86 | -4.2 / -0.24 \| -8.9 / -1.06 |
| none TPV | +0.5 / 0.14 \| -3.8 / -1.86 | -15.3 / -3.41 \| -4.8 / -1.95 | -11.2 / -1.37 \| -2.8 / -0.76 |
| none 2R | +1.5 / 0.31 \| -7.2 / -2.58 | -12.0 / -1.92 \| -4.3 / -1.29 | -8.2 / -0.73 \| -4.8 / -0.96 |

Years (pooled mean bp; n in the report file): every cell has 0 or 1 positive year of 5 (C3 0.4 2R +10.5 in 2021,
C4 TPV +5.4 / C4 2R +3.3 in 2021). Bar needs 4 of 5.

## What the numbers say
- **Prior-day value-area levels alone (none):** the first test of yesterday's POC / VAH / VAL is not a reversal point
  on these perps: gross about 0, net -4 to -9 bp per trade, and the real levels sit at the 51-74th percentile of random
  rows of the same day's range. "First retest of any level" and "first retest of a VP level" are the same thing here.
- **C3 (5m delta in the trade direction):** it does not improve on entering at the test (C3 0.2 vs none-mkt, same
  order type: IS -9.7 vs -10.6, VAL -10.7 vs -6.0). The stronger filter (x 0.4) is worse in VAL and at the 1-4.5th
  percentile of random levels in VAL: aggressive buying into a support that has just been hit is, if anything,
  followed by more downside (the "absorption reversed" reading of the book does not show up).
- **C4 (CVD divergence):** the only cell group with gross > 0 in both eras (+2 to +5 bp) and the only one above most
  random draws in VAL (85.5 / 97.5th percentile), but IS t is -1.2 / -1.25 (40-68th percentile), net is negative in
  both eras and in 4 of 5 years, and IS was negative on ETH (-19 to -23 bp, t -2.4). A VAL-only percentile on a
  negative net is not a candidate; reported as information only. It would need ~10 bp more gross per trade (or a
  maker entry) to break even.
- Costs x1.5 and one step late make every cell worse; the late entry barely changes the confirmed cells (they are
  already market orders), which again says there is no fast-decaying edge at the confirmation.

## Data handling and counts
- Footprint: `load_fp(sym, 30)` after the coordinator's BTC fix (no return had been computed on the broken file).
  1m bars from `load_minutes`; 5m bars and CVD built from the 1m aggressive buy / sell qty.
- Holes > 30 min in the 1m cache (coordinator notice): BTC 24 holes / 36,573 min, ETH 7 / 10,174 min, SOL 7 /
  10,594 min. Days without levels (first day, missing profile, or hole on day d-1 or d): BTC 53, ETH 17, SOL 18 (same
  rule for random levels). Trades dropped because their life spans a hole: BTC 3 (C3 0.2 2R) / 2 (none-mkt 2R) in
  base, ETH 0, SOL 0. ATR14 from perp_1d daily klines (2025+ rows skipped unread); funding rows >= 2025-01-01 skipped.
- A first BTC + ETH run used 1m-based ATR and no hole rule; it was superseded by the run above (verdict identical:
  every cell negative in IS).
- Tests: BTC 3,509, ETH 3,524, SOL 2,966 level tests (side from the previous 1m close; levels opening inside the row at
  00:00 skipped). SOL k = 7 bp rows, BTC 3, ETH 4.

## Pitfalls / notes for the next stream
- Market-entry setups at 15-20 % ATR targets on BTC / ETH / SOL pay ~9 bp round trip (5 + 2..5 + slippage), about
  0.1 R; a gross edge of ~0.15 R is the minimum, and nothing here comes close.
- The random benchmark distribution itself is negative (median t -1 to -5): random intraday levels on these perps
  lose after costs, so a percentile alone cannot qualify a rule; the net / t bars do the work.
- C4's VAL percentile vs its IS failure is the pattern of a chance VAL result; do not pick it up without a new era.
- Check: an independent minute-by-minute loop matched the simulator within funding (<= 3 bp) on 80 random ETH trades
  (none 2R and C3 0.2 2R; run before the hole patch, which only adds the drop rule and the kline ATR).
