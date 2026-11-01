# Round 63 stream C: intraday cross-sectional books on Binance USDT-M perps (result)

Written 2026-10-31 15:23 UTC (from `date -u`). Hypotheses: [HYPOTHESES_C.md](HYPOTHESES_C.md) (14:29 UTC, before any
1h data). Code: `code/` (`select_syms.py`, `pull_1h.py`, `fill_rest.py`, `xs.py`, `run.py`, `null.py`, `report.py`,
`extra.py`, `qc.py`). Outputs: `out/report.txt` (all tables), `out/cells.json`, `out/extra.txt`, `out/qc.txt`,
`out/null_*.npz`. HOLD was never loaded (every series cut at ts < 2025-01-01).

## Answer: none (no LIVE, no DEMO)

All 54 declared cells lose money net of taker costs in IS and in VAL, except one cell that is flat in IS
(REV raw J=1 / H=24: +2.4 bp per day, t 0.19) and negative in VAL (-13.1 bp, t -1.36). The best real IS t (0.19) sits
at the 81st percentile of the max-over-54-cells shuffled null (null max median -0.29, 95th 0.67). No PREREG draft.

The 1-hour cross-sectional reversal does exist at the gross level, but it is small and has shrunk to nothing: gross
+10.0 bp per hour in 2021, +2.1 in 2022-23, -0.04 in 2024, against ~23 bp of cost per rebalance. The break-even cost
per side per trade fell from 3.2 bp (2021) to 0.7 bp (2022-23) to 0 (2024), below even the 2 bp maker fee.

## Set-up (as declared)
- Universe: daily top 40 by trailing-30-day perp quote volume (days d-30..d-1), listed >= 60 days; 212 symbols ever in
  the top 40 in 2020-2024 (all pulled, so no survivorship gap; delisted ones included).
- Signal at instant t: past J-hour return (raw = relative to the cross-sectional mean, or BTC-beta residual).
  REV long 8 losers / short 8 winners, MOM the reverse; VLO = REV among the 20 coins with below-median volume surprise
  (q = 4), VHI = MOM among the above-median half. Equal weight, $1 per side; return quoted per $1 of one side.
- Grid J, H in {1, 4, 24} h; non-overlapping holds on a fixed UTC clock. 54 cells.
- Costs: taker 5 bp per side + half-spread 1 bp (BTC, ETH) / 3 bp (volume rank < 20) / 5 bp, on turnover; funding
  on held legs for stamps in (entry, exit]. Day-clustered and Newey-West (lag 5) t on daily sums, the smaller is used.
- Random benchmark: 200 shuffled-rank books per cell (same eligible coins, same costs).

## Main table (net, per rebalance; full table with all checks in out/report.txt)

| cell (fam sig J H) | IS net bp | IS t | IS gross bp | cost bp | turnover | VAL net bp | VAL t | VAL gross bp | maker IS / VAL t |
|---|---|---|---|---|---|---|---|---|---|
| REV raw 1 1 | -15.7 | -23.5 | +7.5 | 23.1 | 0.66 | -26.0 | -67.2 | +1.4 | +2.86 / -12.0 |
| REV raw 1 4 | -9.6 | -4.5 | +13.0 | 22.6 | 0.64 | -25.8 | -16.5 | +1.7 | +3.09 / -2.95 |
| REV raw 1 24 | +2.4 | 0.19 | +26.2 | 22.9 | 0.65 | -13.1 | -1.36 | +16.8 | +1.64 / +0.84 |
| REV raw 4 1 | -7.6 | -11.9 | +4.5 | 12.1 | 0.34 | -13.7 | -35.9 | +0.7 | +2.26 / -6.43 |
| REV raw 4 4 | -19.0 | -8.2 | +4.0 | 22.9 | 0.65 | -26.5 | -16.8 | +0.9 | -0.55 / -3.30 |
| REV raw 4 24 | -12.8 | -0.91 | +10.8 | 23.0 | 0.65 | -18.4 | -1.93 | +10.1 | +0.35 / +0.29 |
| REV raw 24 1 | -4.4 | -7.2 | +1.0 | 5.4 | 0.15 | -6.2 | -15.6 | -0.0 | -0.37 / -3.53 |
| REV raw 24 4 | -10.1 | -4.9 | -0.1 | 9.9 | 0.28 | -14.5 | -8.4 | -2.9 | -1.21 / -3.21 |
| REV raw 24 24 | -34.0 | -2.6 | -10.8 | 22.7 | 0.65 | -22.7 | -2.35 | +5.1 | -1.27 / -0.16 |
| MOM raw 24 24 (best MOM) | -11.5 | -0.88 | +10.8 | 22.7 | 0.65 | -31.8 | -3.29 | -5.1 | +0.42 / -1.10 |
| VLO raw 1 24 (best VLO) | -1.8 | -0.15 | +24.4 | 25.5 | 0.72 | -15.3 | -1.56 | +14.5 | +1.35 / +0.78 |
| VLO raw 24 24 | -38.1 | -3.09 | -12.2 | 25.3 | 0.72 | -8.8 | -0.91 | +21.0 | -1.51 / +1.46 |
| VHI raw 24 4 (best VHI) | -6.5 | -2.08 | +3.9 | 10.6 | 0.30 | -7.5 | -2.82 | +4.7 | +0.49 / +0.84 |

BTC-residual signals are within noise of the raw ones (e.g. REV resid 1 1 IS gross +7.6 bp, VAL +1.3 bp). Momentum is
the mirror image of reversal at the gross level, so it loses gross and costs: every MOM cell is negative in IS and VAL.
Volume conditioning does not separate the two (Llorente et al. pattern absent): low-volume reversal (VLO 1 1, IS gross
+6.5 bp) is no stronger than unconditional reversal (+7.5 bp), and high-volume moves also reverse (VHI 1 1 gross
-8.0 bp for the momentum side = reversal).

Years (net, REV raw 1 24, the only cell positive in IS): 2020 +6 %, 2021 +11 %, 2022 -12 %, 2023 -61 %, 2024 -71 %
(sum of daily returns per $1 per side): 2/5 years positive.

## Checks
- One step late (trade at the close of the next hour): REV raw 1 24 IS t -1.42, VAL -2.31; every cell negative.
- Next-hour VWAP execution (removes last-trade bounce): REV raw 1 1 IS t -30.3 (vs -23.5 at the close), so part of the
  close-to-close 1h gross is bid-ask bounce.
- Costs x 1.5: every cell negative.
- Funding-stamp split (H = 1, 4): rebalancing at 00 / 08 / 16 UTC is not better for REV (REV raw 1 1 stamp -11.8 /
  -24.7 bp vs other hours -16.3 / -26.2 bp IS / VAL); for momentum the stamp instants lose less (MOM raw 24 1: -1.8
  vs -7.0 bp IS) but stay negative in both eras.
- Shuffled ranks: many REV cells beat 100 % of shuffles on net mean, but only because a shuffled book has full
  turnover and zero gross; beating a random book that loses even more is not a pass when the real net is negative.
- Liquidity slice (out/extra.txt, gross, REV raw 1 1, q = 4): volume rank 0-19 IS +9.6 bp (t 10.7), VAL +1.2 bp;
  rank 20-39 IS +5.2 bp, VAL +1.6 bp. The decay is not just a top-coin effect.
- Break-even cost per side per trade (gross / (4 x turnover)): REV raw 1 1: 2.3 / 3.2 / 0.7 / 0.7 / 0.0 bp for
  2020-2024; REV raw 1 24: 9.7 / 10.3 / 8.6 / 4.7 / 2.9 bp. Taker plus half-spread is 6-10 bp per side.

## Power arithmetic (declared before data)
LIVE needs net Sharpe per rebalance x sqrt(667 x 24 / H) >= 3, i.e. an annual net Sharpe >= ~2.2 whatever H is.
The best VAL cell (REV raw 1 24 at taker cost) has power -1.06. Even the maker variant of that cell (VAL t 0.84 over
3 years) would give a power of ~0.7 on HOLD. The frequency argument in the brief does not hold here: the per-rebalance
gross edge shrinks faster than the number of rebalances grows, and turnover costs scale with the number of rebalances.

## Pitfalls met
- data.binance.vision has no monthly USDT-M futures klines before 2020-01: 2019-11/12 (needed only for beta warm-up and
  the first IS universe) were filled from fapi/v1/klines for BTC, ETH, BCH.
- The monthly archive lacks 1h bars for most altcoins (not BTC) on 2022-02-26..28 and 2022-04-01..02, plus ~1 day
  per coin elsewhere (out/qc.txt); those hours drop out of the universe (signal or entry price missing). Not refilled
  from REST: 5 of 1,096 VAL days, and no VAL cell is within reach of a bar. A few extreme hours are real (LUNA 2022-05, UNFI pump):
  kept.
- The (entry, exit] funding convention charges a stamp that coincides with the exit instant; for H = 24 at 00 UTC this
  gives 3 stamps per hold either way, so it barely matters.
- A 9-coin, q = 2 smoke test (to check the code mechanics during the pull) touched IS / VAL returns of the largest coins
  before the full run; the grid had been fixed at 14:29 UTC and was not changed.

## What a user decision could unlock
- Nothing realistic at taker cost. The 1h reversal break-even fee is below 1 bp per side since 2022 and ~0 in 2024, so
  even VIP-level maker fees with assumed fills do not rescue it. Only an exchange market-maker programme with rebates
  and real queue priority (a different business: quoting, not a directional cross-sectional book) could harvest it,
  and the 2024 gross is already ~0.
- The 24h-hold version (REV 1 24) has a break-even of 3-10 bp per side; with maker fills at 2 bp it stays positive in
  VAL (t 0.84) but far below any bar, and it decays every year.

## Data pulled
- research/data/binance_1h_full/1h/<SYM>.csv: 1h klines 2019-11..2024-12-31 for 212 symbols (7,524 monthly zips from
  data.binance.vision, 5 x 404 for the pre-2020 months, 2 timeouts retried OK; 5 REST calls to fapi/v1/klines).
  symbols.csv (selection), requests.log, missing_months.csv, filled_months.csv, panel_cache.npz (numpy cache).
- Funding: existing research/data/binance/funding covered all 212 symbols; nothing new pulled.
- 1 web search (literature context: recent preprints report hourly crypto reversal as small, microstructure-driven and
  fragile after costs, consistent with this result).
