# Round 64 stream F: liquidation-wick fade on Binance USDT-M altcoin perps (1m), result

Written 2026-11-01 09:37 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_F.md](HYPOTHESES_F.md), 08:54 UTC, before any return. Addenda 1 and 2 changed only the
  spot-QC source and the pull order, both before any return was computed.
- Draft: [PREREG_DRAFT_F_wick_fade.md](PREREG_DRAFT_F_wick_fade.md).
- Code: `code/`.
- Outputs:
  - `out/report.txt`: all cells and details; `out/cells.json`;
  - `out/extra.txt`, `out/extra2.txt`: diagnostics;
  - `out/qc_spot.txt`, `out/c3corr.txt`, `out/top_trades.txt`, `out/sample_paths.txt`.

HOLD was never requested or loaded: monthly files <= 2024-12, and every series is cut at ts < 2025-01-01 at load.

## Answer: one LIVE-tier candidate on IS / VAL, T5 idio H60. PREREG_DRAFT written; HOLD left to the coordinator

**The rule.** Fade a >= 5 % one-minute close-to-close move of a top-40 altcoin perp when BTC's same-minute move is
<= 0.2 x as large:
- long after a crash, short after a spike;
- enter at the close of the next minute;
- exit 60 minutes later;
- costs: taker 5 bp a side, plus a half-spread proxy that is 3x normal at entry (22-30 bp round trip).

| era | n | net bp / trade | median | t (day cluster) | S / trade | years + | random beaten | x1.5 t | 2 bars late t |
|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 380 | +273.0 | +274 | 4.05 | 0.224 | 2 / 2 | 100 % | 3.87 | 6.65 |
| VAL 2022-24 | 770 | +270.5 | +177 | 3.76 | 0.163 | 3 / 3 | 100 % | 3.58 | 3.12 |

**Bars.** Every LIVE bar passes:
- IS t >= 2.5 and VAL t >= 1.5;
- 5 / 5 years positive;
- beats >= 95 % of random entries;
- positive at costs x1.5 and two bars late;
- HOLD power at VAL size: per trade 0.163 x sqrt(~470 HOLD trades) = **3.53**;
- the cell was the best IS t of the 18 declared cells. The max-over-cells random null has a 95th percentile of +0.28
  against the real +4.05.

**Caveats:**
- The day-clustered power is 2.93, just under 3: events cluster on crash days.
- The VAL mean includes LUNA (2022-05-11/12). Without the LUNA and FTX months, VAL is +163 bp (t 3.65) and the power
  rises to 5.04.
- The edge is mostly the crash side (IS +581 / VAL +360 bp). Spikes give IS -189 (t -1.14) and VAL +132 (t 1.15).
  The pooled side was declared; a crash-only rule is not registered.

**C3 correlation (daily P&L, weekdays):** IS +0.048, VAL -0.037.

**Other cells:**
- Small vol-scaled events (TZ) lose net in every H: they revert by only 2-60 bp gross, against 22-30 bp of cost.
- The 3 % cells pass IS at H60 but are weak in VAL (power <= 1.93).
- The overshoot scales with the size of the wick and takes ~an hour to come back: H5 < H15 < H60 in every T3 / T5
  cell.

## Set-up (as declared)
- **Universe:** daily point-in-time top 40 USDT-M perps by mean quote volume over days d-30..d-1, listed >= 60 days
  (round 63 C `xs.daily_universe`). 212 symbols, delisted included; 2,759 symbol-months 2020-01..2024-12, all pulled.
- **Event:** r_e = c_e / c_{e-1} - 1. Thresholds:
  - T3: |r| >= 3 %;
  - T5: |r| >= 5 %;
  - TZ: |r| >= max(1 %, 10 x the trailing 1,440-minute sd).
- **idio filter:** |r_BTC,e| <= 0.2 |r|, BTC excluded.
- **Bad-print guard:** >= 10 trades in bar e, and the next bar's open still beyond the halfway point.
- **De-duplication:** one event per coin per 60 minutes.
- **Trade:** entry at the close of e+1, exit at entry + H with H in {5, 15, 60}. Funding is charged on stamps in
  (entry, exit].
- **Costs:** 10 bp of taker fees plus an entry half-spread of 3h and an exit half-spread of h, with h = 1 (BTC / ETH),
  3 (rank < 20) or 5 bp.
- **Random benchmark:** 200 draws per event, from the same coin, the same era and the same trailing-sd decile. The side
  fades the random minute's own return, with the same H and the same cost.

## All 18 cells (net bp per trade; t clustered by entry day)
| cell | IS n | IS net | IS t | VAL n | VAL net | VAL t | 2020 / 21 / 22 / 23 / 24 | x1.5 t I / V | late t I / V | power trade / clust |
|---|---|---|---|---|---|---|---|---|---|---|
| T3 all H5 | 2219 | +9.4 | 0.65 | 3171 | +10.3 | 0.59 | -5 +13 +12 +17 +2 | -0.22 / -0.15 | 1.43 / 0.18 | 1.33 / 0.46 |
| T3 all H15 | 2219 | +7.9 | 0.24 | 3171 | +28.7 | 1.35 | +78 -11 +32 +65 -10 | -0.15 / 0.75 | 0.69 / 1.28 | 2.87 / 1.05 |
| T3 all H60 | 2219 | +111.3 | 3.44 | 3171 | +42.2 | 1.45 | +146 +102 +50 +82 -6 | 3.05 / 1.00 | 3.07 / 1.11 | 1.75 / 1.13 |
| T3 idio H5 | 1530 | +1.8 | 0.09 | 2394 | +8.3 | 0.43 | +21 -3 +23 -11 +11 | -0.59 / -0.24 | 0.47 / 0.58 | 0.85 / 0.34 |
| T3 idio H15 | 1530 | +24.6 | 0.85 | 2394 | +40.4 | 2.73 | +101 +6 +61 +37 +21 | 0.41 / 1.86 | 0.76 / 2.38 | 3.38 / 2.13 |
| T3 idio H60 | 1530 | +123.6 | 3.89 | 2394 | +60.3 | 1.89 | +187 +108 +120 +49 +5 | 3.49 / 1.49 | 4.08 / 1.52 | 1.93 / 1.48 |
| T5 all H5 | 530 | +73.4 | 0.95 | 1017 | +88.7 | 2.03 | +239 +34 +21 +92 +147 | 0.79 / 1.74 | 1.08 / 0.94 | 4.20 / 1.59 |
| T5 all H15 | 530 | +81.8 | 1.00 | 1017 | +141.9 | 3.23 | +345 +18 +47 +201 +184 | 0.84 / 2.94 | 0.86 / 2.97 | 5.38 / 2.53 |
| T5 all H60 | 530 | +251.7 | 2.92 | 1017 | +233.9 | 4.73 | +409 +214 +239 +249 +218 | 2.77 / 4.47 | 3.01 / 3.41 | 3.97 / 3.70 |
| T5 idio H5 | 380 | +43.0 | 0.45 | 770 | +75.1 | 1.52 | +219 +9 +49 -4 +162 | 0.32 / 1.26 | 2.05 / 1.39 | 2.87 / 1.19 |
| T5 idio H15 | 380 | +90.1 | 1.02 | 770 | +155.7 | 3.17 | +374 +35 +100 +120 +236 | 0.87 / 2.91 | 1.37 / 3.01 | 4.85 / 2.48 |
| **T5 idio H60** | 380 | +273.0 | 4.05 | 770 | +270.5 | 3.76 | +460 +236 +397 +164 +236 | 3.87 / 3.58 | 6.65 / 3.12 | 3.53 / 2.93 |
| TZ all H5 | 4798 | -22.5 | -2.33 | 10213 | -18.2 | -2.94 | -34 -14 -14 -11 -35 | -3.60 / -5.01 | -1.60 / -2.24 | < 0 |
| TZ all H15 | 4798 | -13.0 | -1.07 | 10212 | -10.4 | -1.26 | -8 -17 -4 +2 -37 | -2.08 / -2.80 | -0.56 / -0.87 | < 0 |
| TZ all H60 | 4798 | +16.6 | 1.23 | 10210 | -7.2 | -0.86 | +5 +25 -7 +3 -23 | 0.32 / -2.40 | 1.44 / -0.97 | < 0 |
| TZ idio H5 | 2857 | -16.6 | -1.24 | 6300 | -17.5 | -2.12 | -16 -17 -5 -20 -27 | -2.19 / -3.69 | -0.67 / -1.70 | < 0 |
| TZ idio H15 | 2857 | -2.0 | -0.12 | 6299 | -3.2 | -0.47 | +12 -11 +5 -1 -15 | -0.90 / -2.38 | 0.19 / -0.30 | < 0 |
| TZ idio H60 | 2857 | +35.2 | 2.34 | 6297 | -5.3 | -0.62 | +30 +38 +1 -7 -10 | 1.49 / -2.17 | 3.12 / -0.86 | < 0 |

- Random entries are near zero gross, so they average about -cost (-23 to -26 bp). Every cell beats 100 % of them.
  "Beats random" is therefore an easy bar here; the IS / VAL t is what decides.
- Max-over-18 IS t: real 4.05; null median -1.19, p95 +0.28.

## Checks on the chosen cell (out/extra.txt, out/extra2.txt)
**Breadth:**
- Median trade: IS +274 bp, VAL +177 bp.
- Win rate: 65 % / 67 %.
- Coins: 76 coins traded in IS, 138 in VAL; 70 % / 78 % of coins have a positive mean.

**Concentration:**
- Without the top 3 coins: IS +212.8, VAL +190.5.
- Without the top 5 days: IS +177.7 (t 3.74), VAL +126.5 (t 3.41).
- The VAL top days are LUNA 2022-05-11/12 (+80,000 bp summed).
  - Without the LUNA / FTX months: +163.0 (t 3.65, S 0.257).
  - Without the LUNA and FTT coins: +212.2 (t 4.05).

**Crash days:**
- IS without 2020-03-12/13 and March-April 2020: +270.6 (t 3.99).
- IS without 2021-05-19 (a Binance futures outage day, 74 events): +326.5 (t 5.39).

**Liquidity split:**
| | IS | VAL |
|---|---|---|
| rank < 20 | +181 bp | +329 bp |
| rank 20-39 | +384 bp | +200 bp |
| 5-8 % wicks | +251 bp | +111 bp |
| >= 8 % wicks | +354 bp | +684 bp |

**Cost headroom:** break-even round trip ~296 bp in both eras, against 26 bp declared. Slippage would have to be
~10x the proxy to remove the edge.

**Entry timing:** at the open of e+1 (zero latency, information only), IS +317 and VAL +334. That is close to the
one-bar-late entry, so the edge is not a first-seconds bounce.

**Bad prints:**
- Spot QC (out/qc_spot.txt): of 300 random de-duplicated T3 events, 279 also moved >= half as much in the same minute in
  the Binance spot pair. 12 did not, 6 have no spot pair, and 3 straddle a day boundary.
- The failures are perp-only liquidation wicks (2021-05-19 13:4x, FTT 2022-11, TRB 2023-09), not data errors.
- A random sample of 30 event paths (out/sample_paths.txt) shows real volume: the event minute trades $1-80 M, 10-100x
  the trailing median. The recovery is gradual over the hour.

**Worst case:** the worst trade is -5,072 bp and the best is +27,405 bp (LUNA). The largest drawdown of the cumulative
per-trade sum is 18,672 bp over 2020-24 (the sum is 312,071 bp).

## Why it works where round 26 J did not
- Round 26 J faded 6-16 sigma tick jumps on BTC / ETH / FX / metals: +0.6-3.5 bp at mid against 1.6-1.9 bp (IC 23-26 bp
  for crypto). Those jumps are small and liquid.
- Here the wicks are >= 5 % on thin altcoin perps, with a BTC-quiet filter, so they are coin-specific forced flow, not
  market information. The overshoot is ~300 bp gross and comes back over ~60 minutes, i.e. it is 10x the cost.
- The size-scaling matches the liquidation story. 1-3 % vol-scaled moves do not pay; 3 % moves pay only at H60 in
  2020-21; >= 5 % moves pay in every year.

## Power arithmetic (declared vs found)
- Declared: n_VAL ~300 needs S >= 0.22, n_VAL ~1,000 needs S >= 0.12.
- Found: n_VAL = 770 with S 0.163, giving per-trade power 3.53. The day-clustered power is 2.93.
- The event rate is stable: 265 / 223 / 282 per year in 2022-24, so ~470 HOLD trades are expected. At half the rate
  the power would be ~2.5.

## Pitfalls met
- **Hung reads in the pull.** It slowed from ~1.7 to ~0.15 files/s after 4 min. I restarted it with a 40 s timeout and
  6 threads (still >= 0.25 s between request starts). The full pull finished in 35 min:
  - 2,760 x 200 (one file fetched twice across the restart) and 0 x 403 / 418 / 429 / 503;
  - 72 timeouts and 11 URL errors, all retried OK.
- **api.binance.com is closed to bots.** Its robots.txt is "Disallow: /", so the REST API was not used. The spot QC
  used data.binance.vision daily spot files instead (Addendum 1).
- **Module-name clashes.** A diagnostics file named `inspect.py` shadowed the stdlib, and `extra.py` clashed with round
  63 C's `extra.py` on sys.path. They are renamed `top_trades.py` / `f_extra.py`. No result was affected.
- **Candidate prefilter.** `events.py` keeps only |r| >= 3 % or (|r| >= 1 % and >= 10 sigma) before the random draws.
  That is exactly the union of the declared thresholds.
- **C3 correlation on weekdays only.** C3 trades only on weekdays; on weekends both series would be 0 for C3.

## What a user decision could unlock
- **Opening HOLD (coordinator).** It needs the 2025-01..2026-10 monthly 1m files for the point-in-time top 40, ~1,000
  symbol-months, ~15 min of pull. The draft fixes the pass bar:
  - day-clustered t >= 2.0;
  - x1.5 and two-bars-late net > 0;
  - 2025 and 2026 each net > 0.
- **Execution.** The rule needs a bot that streams 1m klines for ~40 perps plus BTC and sends market orders at bar
  close. The Binance USDT-M account needs no borrow. Concurrency matters on crash days: up to dozens of positions in
  the same minute.
- **Crash-only variant.** It would need its own declaration on new data; it is not registrable now.

## Data pulled
- `research/data/binance_1m_wicks/npz/<SYM>_<YYYY-MM>.npz`:
  - 2,759 files, 1.5 GB, 212 symbols, 2020-01..2024-12;
  - fields: minute, o h l c, quote volume, trades; zips deleted after conversion.
- `research/data/binance_1m_wicks/`:
  - `univ.npz` and `pull_list.csv`;
  - `requests.log`: time, URL, status, bytes, including both robots.txt fetches and 297 spot daily files (291 x 200, 6 x 404);
  - `robots.txt` (a 404 body) and `spot_qc/robots_api.txt`.
- Reused: round 63 C panel cache (daily volume, funding).
- Web searches: 0.
