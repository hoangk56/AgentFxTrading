# Round 63 stream O: Binance futures positioning metrics on altcoin perps (result)

Written 2026-10-31 16:43 UTC (from `date -u`). Hypotheses: [HYPOTHESES_O.md](HYPOTHESES_O.md), written 15:51 UTC
before any metrics beyond a 7-file format probe. Code: `code/` (`univ.py`, `pull.py`, `parse.py`, `coverage.py`,
`engine.py`, `run.py`, `report.py`, `extra.py`). Outputs: `out/report.txt` (all tables), `out/cells.json`,
`out/coverage.txt`, `out/extra.txt`, `out/null_disc_t.npz`, `out/run.log`. HOLD was never requested or loaded:
metrics days <= 2024-12-31, prices cut at ts < 2025-01-01 (round 63 C `xs.load`).

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)

None of the 20 declared cells reaches the DEMO bar (t >= 2.0 in DISCOVERY). The best DISCOVERY net t is +0.87
(H1 q2 p5 H24). The max-over-20-cells null of random entries has median -0.14 and 95th percentile 0.82 for that
statistic, so the best cell sits at the 95th percentile. That null is low only because random hedged entries pay
~30 bp of cost; it is not evidence of an effect, and no cell is close to an absolute bar.
- **H1 OI flush -> long alt, short BTC**: positive gross in 7 of 8 cells in both eras. DISCOVERY net is -39..+73 bp
  (t -1.02..+0.87). VAL is stronger, +18..+92 bp (t +0.78..+1.96), and beats 100 % of random entries. The OI
  condition does add to the price-only drop in VAL (+49..+124 bp gross against +32..+97). But the DISCOVERY era fails,
  2022 is negative at 4 h, and VAL rests on a few coins (TRB, PEPE, REEF, DOGE). It is not a candidate. Best VAL power
  is 2.96 per trade (1.24-2.16 day-clustered), short of 3 even if DISCOVERY had passed.
- **H2 crowding fade (top-trader position L/S)**: flat. DISCOVERY -8..+12 bp (t <= 0.27), VAL -14..+28 bp
  (t <= 0.72). The series only exists from 2023-01 (coverage below), so DISCOVERY is in practice 2023-H1.
- **H3 taker imbalance**: gross is ~0 at 4 h (|gross| <= 7.5 bp). At 24 h DISCOVERY favours continuation (+12..+13
  bp gross), but the sign flips in VAL for b 2 % (-9.7). Every one of the 8 cells is negative net in both eras
  (t -1.5..-12.5). Cost (~30 bp) is 3-30 x the gross.

## Set-up (as declared)
- Universe on day d: point-in-time top 40 USDT-M perps by mean quote volume over days d-30..d-1, listed >= 60 days
  (`xs.daily_universe`, the perp-only twin of round 58 `carry.universe`), then the 16 highest-volume coins excluding
  BTC (ETH + 15 alts). 121 symbols over 2022-24, delisted ones included (LUNA, FTT, SRM...).
- Metrics: Tier A = every second day for the universe coins (8,768 coin-days), Tier B = the other coin-days with
  a >= 3 % hourly drop (1,853), so H1 sees every qualifying event; H2 / H3 see half the days.
- Signal at hour t from stamps <= t - 5 min; entry at the VWAP of the hour after t, exit at the VWAP of the hour
  starting t + H. BTC hedge is beta x BTC (trailing 720 h, shrunk 50 % to 1).
- Costs per side: 5 bp taker plus a half-spread of 3 / 5 / 1 bp (alt rank < 20 / >= 20 / ETH), and 6 bp x beta on
  the BTC leg. That is ~30 bp a round trip. Funding is charged on both legs for stamps in (entry, exit], plus DFF cash
  on the alt notional.
- t is clustered by entry day. Random benchmark: 500 replications with the same trade count per coin and era, at
  uniform random eligible hours. For H2 / H3 the side is recomputed at the random hour from the percentile vs 0.5.
- "gross" in the tables = after funding, before fees, spread and cash.

## Metrics coverage (share of hours with a value on pulled coin-days, `out/coverage.txt`)

| half-year | coin-days | OI | top position L/S | global account L/S | taker buy/sell |
|---|---|---|---|---|---|
| 2022H1 | 1864 | 1.00 | 0.16 | 0.90 | 0.32 |
| 2022H2 | 1737 | 1.00 | 0.09 | 1.00 | 1.00 |
| 2023H1 | 1672 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2023H2..2024H2 | 5339 | 1.00 | 1.00 | 1.00 | 1.00 |

The Binance Vision metrics archive has OI for every day, but the ratio columns are empty for most alts before
2022-07 (taker) and 2023-01 (top-trader position). So H2's DISCOVERY is ~6 months of half-sampled days, and H3's
is 12 months.

## Main table (net per trade in bp; full table with every check in out/report.txt)

| cell | DISC n | DISC net | DISC t | DISC gross | rand % | VAL n | VAL net | VAL t | VAL gross | rand % | 2022 / 2023 / 2024 | x1.5 t D / V | late t D / V | power trade / clust |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 q2 p3 H4 | 936 | -21.7 | -1.02 | +9.1 | 98 | 775 | +18.0 | +1.12 | +48.8 | 100 | -24 / +4 / +9 | -1.74 / +0.17 | -1.05 / -0.32 | 1.62 / 1.24 |
| H1 q2 p3 H24 | 818 | +28.4 | +0.71 | +59.7 | 100 | 659 | +62.3 | +1.46 | +94.2 | 100 | +58 / +33 / +41 | +0.33 / +1.10 | +0.12 / +0.81 | 2.28 / 1.61 |
| H1 q2 p5 H4 | 320 | -13.2 | -0.23 | +18.1 | 96 | 256 | +72.8 | +1.96 | +103.8 | 100 | -22 / +25 / +71 | -0.50 / +1.54 | -0.16 / +1.07 | 2.96 / 2.16 |
| H1 q2 p5 H24 | 306 | +72.9 | +0.87 | +104.5 | 100 | 235 | +71.5 | +0.78 | +103.7 | 100 | +180 / +22 / +33 | +0.68 / +0.62 | +0.50 / +0.42 | 1.45 / 0.87 |
| H1 q4 p3 H4 | 466 | -22.7 | -0.60 | +8.3 | 87 | 343 | +42.5 | +1.70 | +72.9 | 100 | -23 / +3 / +44 | -1.01 / +1.09 | -0.72 / +0.72 | 2.26 / 1.87 |
| H1 q4 p3 H24 | 436 | +31.2 | +0.62 | +62.8 | 100 | 318 | +90.9 | +1.58 | +122.5 | 100 | +78 / +30 / +84 | +0.32 / +1.32 | -0.06 / +0.90 | 2.53 / 1.75 |
| H1 q4 p5 H4 | 216 | -39.0 | -0.49 | -7.5 | 42 | 160 | +79.4 | +1.70 | +110.1 | 100 | -73 / +21 / +77 | -0.69 / +1.38 | -0.53 / +1.15 | 2.23 / 1.88 |
| H1 q4 p5 H24 | 210 | +38.1 | +0.39 | +69.9 | 99 | 151 | +91.5 | +0.94 | +123.5 | 100 | +168 / -3 / +76 | +0.23 / +0.78 | -0.12 / +0.48 | 1.54 / 1.03 |
| H2 a10 H24 | 511 | -8.3 | -0.42 | +22.1 | 90 | 1466 | -13.8 | -0.77 | +17.1 | 43 | +69 / -21 / -8 | -1.16 / -1.59 | -0.66 / -1.48 | -1.72 / -1.20 |
| H2 a10 H72 | 330 | +11.7 | +0.27 | +44.6 | 98 | 921 | -0.4 | -0.01 | +33.4 | 28 | +266 / -32 / +21 | -0.07 / -0.46 | +0.14 / -0.61 | -0.02 / -0.02 |
| H2 a2.5 H24 | 301 | +1.9 | +0.08 | +32.4 | 92 | 825 | +1.6 | +0.07 | +32.5 | 80 | -3 / +1 / +2 | -0.54 / -0.58 | -0.14 / -0.68 | 0.15 / 0.11 |
| H2 a2.5 H72 | 211 | +5.3 | +0.10 | +38.2 | 92 | 586 | +27.8 | +0.72 | +61.6 | 61 | +262 / -43 / +70 | -0.17 / +0.34 | +0.01 / +0.15 | 1.25 / 1.12 |
| H3C b2 H4 | 2719 | -27.9 | -9.95 | +1.8 | 71 | 3592 | -29.4 | -11.92 | +0.6 | 54 | -31 / -26 / -30 | -15.2 / -17.9 | -8.43 / -9.37 | < 0 |
| H3R b2 H4 | 2719 | -31.4 | -11.20 | -1.8 | 24 | 3592 | -30.7 | -12.48 | -0.6 | 47 | -29 / -33 / -31 | -16.4 / -18.6 | -10.9 / -11.3 | < 0 |
| H3C b2 H24 | 1737 | -17.4 | -1.69 | +13.0 | 91 | 2279 | -40.9 | -4.10 | -9.7 | 15 | -25 / -12 / -52 | -3.12 / -5.59 | -1.76 / -4.00 | < 0 |
| H3R b2 H24 | 1737 | -43.4 | -4.20 | -13.0 | 7 | 2279 | -21.5 | -2.16 | +9.7 | 84 | -35 / -50 / -10 | -5.62 / -3.65 | -4.01 / -2.36 | < 0 |
| H3C b0.5 H4 | 975 | -22.2 | -5.75 | +7.5 | 95 | 1320 | -29.2 | -7.40 | +0.9 | 51 | -26 / -22 / -30 | -9.56 / -11.2 | -5.77 / -6.94 | < 0 |
| H3R b0.5 H4 | 975 | -37.2 | -9.64 | -7.5 | 6 | 1320 | -31.1 | -7.87 | -0.9 | 51 | -33 / -37 / -30 | -13.5 / -11.6 | -8.27 / -6.19 | < 0 |
| H3C b0.5 H24 | 779 | -18.3 | -1.46 | +12.2 | 82 | 1054 | -29.7 | -2.08 | +1.6 | 58 | -19 / -13 / -40 | -2.64 / -3.13 | -1.51 / -1.69 | < 0 |
| H3R b0.5 H24 | 779 | -42.7 | -3.41 | -12.2 | 17 | 1054 | -32.9 | -2.31 | -1.6 | 44 | -42 / -49 / -23 | -4.59 / -3.36 | -3.31 / -2.65 | < 0 |

- Year columns are net bp per trade by calendar year. "power trade" = VAL net / sd x sqrt(expected HOLD trades);
  that is VAL n x 22/18, x 2 more for H2 / H3, because live would trade every day. "power clust" = VAL day-clustered
  t x sqrt(same factor).
- Max-over-cells null (DISC net t, 500 replications): real max 0.87, null median -0.14, p95 0.82, real at the 95th
  percentile.

## Information (not cells)

| | DISC n | DISC net | DISC t | DISC gross | VAL n | VAL net | VAL t | VAL gross |
|---|---|---|---|---|---|---|---|---|
| H1 price-only p3 H4 (same covered hours, no OI condition) | 2483 | -31.2 | -1.62 | -0.0 | 2454 | +0.6 | +0.05 | +31.8 |
| H1 price-only p3 H24 | 1636 | -23.5 | -0.65 | +7.8 | 1612 | +9.2 | +0.33 | +41.4 |
| H1 price-only p5 H4 | 622 | -61.8 | -1.16 | -29.7 | 529 | +17.3 | +0.59 | +48.5 |
| H1 price-only p5 H24 | 489 | -35.4 | -0.44 | -3.5 | 431 | +65.1 | +0.93 | +97.4 |
| long alt / short beta BTC at every universe hour, H4 | 191k | -33.9 | -16.8 | -4.2 | 194k | -31.1 | -16.9 | -1.1 |
| same, H24 | 191k | -50.1 | -5.46 | -19.9 | 193k | -38.0 | -4.48 | -6.8 |

H1 by half-year (`out/extra.txt`), net bp (n, t):
- q2 p3 H24: -38 (236, -0.40) | +149 (248, +2.04) | -14 (334, -0.40) | +105 (219, +1.84) | +44 (228, +0.55) |
  +38 (212, +0.46).
- q2 p5 H4: -233 | +108 | -2 | +78 | +89 | +45.
- So the rule only pays in some half-years (2022H2, 2023H2), with no trend.
- DISCOVERY without the LUNA (2022-05) and FTX (2022-11) months: q2 p3 H24 +27.2 bp (t 0.85), q2 p5 H4 +13.2 (t 0.54).
  The crash months are not what sinks DISCOVERY.
- VAL concentration: q2 p3 H4 is 13,950 bp summed, of which 3,061 is left without TRB, BLZ and PEPE. q2 p3 H24 is
  41,067 bp summed, of which 14,720 is left without REEF, XRP and DOGE. VAL depends on a few squeeze-prone coins.

## What failed and why
- **H1** has the right sign in gross terms, and OI does separate forced selling from ordinary drops in VAL (unlike
  BTC in round 31). But the rebound is ~50-120 bp gross on a 250-900 bp sd, i.e. ~0.1 sd per trade. With
  ~150-650 trades a year and event clustering on crash days, that is a DISCOVERY t below 1, and it does not repeat
  across half-years. The 24 h cells beat random hedged longs by ~60-80 bp, but random hedged longs lose 20 bp gross
  in 2022 (alts lagging BTC beyond beta), which flatters "beats random" (100 %).
- **H2**: the top-trader position ratio carries no 1-3 day information on alts; gross matches the random hedged
  baseline.
- **H3**: hourly taker imbalance on alts does not predict 4 h returns at all (|gross| <= 7.5 bp on ~250 bp sd). At
  24 h it changes sign between eras. This is the same as round 4's order-flow result, now on the alt panel.

## Pitfalls met
- **Disclosed rate slip**: a first pull process (2 threads) was meant to be stopped at 15:54 UTC, when I restarted
  with 4 threads. The `pkill` pattern did not match (the macOS binary is `Python`, capital P). Both processes ran
  until 16:18 UTC, so data.binance.vision got ~5-6 requests a second instead of <= 4 for 24 minutes, and 3,053 URLs
  were fetched twice. The server returned 13,659 x 200, 15 x 404 (FTT after its 2022-11 delisting, LUNA 2022-05-13),
  and no 403 / 418 / 429 / 503.
- Ratio columns are blank on many alt-days before 2022-07 (taker) and 2023-01 (top position), with no error. Always
  check coverage per field, not per file.
- Instants 00:00 / 01:00 UTC are skipped for H1 / H3, because their window spans two daily files.
- Tier B's list is built from instants 02:00..23:00 (the hypotheses said 02:00..24:00). That is consistent with the
  skip rule and changes only which files were pulled.
- The H1 random pool uses covered days (Tier A + B), so it over-represents drop days, as declared.

## What a user decision could unlock
- Little. H1 is the only family with a gross effect. Even taking its VAL size at face value, power is <= 2.96 per
  trade and <= 2.16 day-clustered, so it is not LIVE even if the user accepted a VAL-only era. A full K = 40 panel
  would add smaller coins at higher costs. Maker entry (2 bp instead of 5 + 3) would lift H1 VAL net by ~10 bp, but
  DISCOVERY would still be at t < 1.5.
- Cross-exchange aggregated OI / liquidations (Coinglass etc., account) could sharpen the forced-flow flag, but
  round 31 C already showed measured liquidations continue on BTC. Value ~1 %.

## Data pulled
- research/data/binance_metrics/raw/<SYM>/<SYM>-metrics-<day>.zip: 10,612 daily files (130 MB), 121 symbols,
  2022-01-01..2024-12-31. Also pull_list.csv (tier per coin-day), requests.log (13,674 rows: time, URL, status,
  bytes), hourly.npz (parsed hourly OI / ratios), probe/ (7 format-probe files). Parsed with `python -I`.
- Reused: research/data/binance_1h_full (prices, panel_cache.npz), research/data/binance/funding, perp_1d,
  research/data/rates/DFF.csv. No web searches.
