# Stream U (round 65): Korean retail rush without a listing (Upbit KRW volume-share shocks)

Written 2026-11-01 11:31 UTC. Hypotheses and the 12-cell grid were declared in [HYPOTHESES_U.md](HYPOTHESES_U.md) at
10:38 UTC, before any share or return was computed. HOLD (2025-01-01..) was never requested, loaded or counted: every
series is cut at ts < 2025-01-01, and a signal needs T + 2 h + hold + 10 min < 2025-01-01.

## Answer first: none
- **No cell reaches IS t 2.0**, so none qualifies for DEMO or LIVE. No PREREG_DRAFT is written.
- **The IS-chosen cell is k8-RU-H72** (highest IS t):
  - IS +260 bp/trade, t 1.03, n 12.
  - VAL +115 bp, t 0.46, n 19.
  - Years positive: 3 / 5.
  - Random timing 83 % (IS) and 93 % (VAL). Generic-pump control 83 % / 74 %.
  - Power at VAL size 0.38.
- **IS sign.** 10 of 12 cells are negative in IS. The two broad cells are significantly negative: k2-ALL is -74 bp
  (H24) and -135 bp (H72), both t -2.15.
- **2021 drives the IS losses.** In the alt-season year, shorting coins that Korean retail was chasing lost in every
  one of the 12 cells (2021 net: -58 to -476 bp).
- **VAL behaves differently.** The H72 cells at k = 4 make money in VAL:
  - k4-ALL-H72: +96 bp, t 1.89, n 314.
  - k4-RU-H72: +194 bp, t 1.60, n 97.
  - Both beat 97-100 % of random timings and of same-size generic pumps.
- **The VAL edge is unusable.** IS is negative for the same cells: -43 bp and -148 bp. That is a sign flip across
  eras. The bar picks parameters on IS, so this edge cannot be promoted, and its power at VAL size is only 1.2-1.6
  anyway.
- **Does the Korean share add anything over a price pump?**
  - In VAL, yes. In the H72 cells the Korean-share events beat 97-100 % of matched draws of the same run-up size taken
    when there was no Korean share. The generic pump itself has a negative median.
  - In IS, no. The same comparison gives 62-90 %.
  - So the "Korean attention fades" story holds in 2022-24 only. The listing-specific K2 effect does not generalise to
    existing KRW markets in a way that survives both eras.

## Data
**Upbit.** Stream K's 240-minute candles (research/data/upbit/m240, `krw` column), read-only.
- 96 coins: K's map minus BTC, USDC and BTT.
- No new Upbit request was made.

**Binance local files** (read-only, cut at load).
- Perp 1h close and qvol come from the earliest-starting local file. The column layout differs by folder:
  binance/perp_1h has `t,o,h,l,c,qvol` and the others have `t,o,h,l,c,vol,qvol,n`. Columns are mapped by header.
- Funding comes from local files.
- BTCUSDT perp 1m comes from K's btc_1m.npz.

**New pulls** (research/data/upbit_vol/, requests.log). There were 10,547 requests to fapi.binance.com, every one
returning 200. No 403, 418, 429 or 503.
- robots.txt was logged at 10:41 UTC. It disallows only named search engines.
- 10,540 requests fetched 1m klines (limit 99, weight 1), with >= 0.26 s between requests (shared lock, 4 threads).
  The pull ran 10:42-11:30 UTC, about 48 min.
  - K's alt_1m cache was read first.
  - Cache: research/data/upbit_vol/alt_1m/.
  - Pricing is k2rule's: 1m close at the target minute, with up to 4 later minutes as fallback.
- 7 requests fetched fundingRate for the 6 universe perps with no local funding file: AXL, G, KAIA, ME, POL, SUN.

## Rule (as declared)
**Signal.**
- `S(T) = ln(Upbit KRW value over the 24 h ending at T) - ln(Binance perp quote volume over the same 24 h)`.
- `D(T) = S(T) - median(S)` over the 30 days ending at T - 24 h.
- Floor: KRW24 >= 1e9.

**Exclusions.**
- The first 30 days after a coin's first Upbit candle, and the 30 days after its K2 listing time.
- One event per coin per 7 days.

**Event.** `D >= ln k`, k in {2, 4, 8}, with or without a run-up filter: alt / BTC over 24 h >= +10 %.

**Trade.**
- Short the alt perp / long BTCUSDT perp at the 1m close at T + 1 h.
- Hold 24 or 72 h.
- Cost 42 bp plus real funding.
- Late checks: T + 1 h 5 min and T + 2 h.

**Benchmarks** (gross, on 1h closes, 500 draws).
- (a) Random timing: the same coin, the same quarter, a random 4h boundary.
- (b) Generic-pump control: the 50 pool observations nearest each event's run-up, from the same era, with D < ln 1.5
  (no Korean share).

## Results (net bp/trade, t clustered by day; full output in u_output.txt, u_results.json)
"rand / pump" = percentile of the actual gross mean vs random timing / vs the generic-pump control. Power = VAL
per-trade Sharpe x sqrt(VAL events per year x 1.83).

| cell | IS n | IS net | IS t | IS rand / pump | VAL n | VAL net | VAL t | VAL rand / pump | yrs + | VAL SR | power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| k2-ALL-H24 | 633 | -74 | -2.15 | 50 / 78 | 2037 | -42 | -2.57 | 53 / 78 | 0/5 | -0.074 | - |
| k2-ALL-H72 | 633 | -135 | -2.15 | 42 / 80 | 2036 | -4 | -0.14 | 99 / 99 | 2/5 | -0.005 | - |
| k2-RU-H24 | 255 | -27 | -0.41 | 78 / 82 | 498 | -32 | -0.69 | 92 / 96 | 2/5 | -0.035 | - |
| k2-RU-H72 | 255 | -184 | -1.60 | 49 / 77 | 498 | +16 | +0.23 | 100 / 99 | 2/5 | +0.012 | 0.21 |
| k4-ALL-H24 | 138 | -56 | -0.72 | 49 / 62 | 314 | +26 | +0.79 | 100 / 99 | 2/5 | +0.051 | 0.70 |
| k4-ALL-H72 | 138 | -43 | -0.38 | 84 / 90 | 314 | +96 | +1.89 | 100 / 100 | 4/5 | +0.113 | 1.56 |
| k4-RU-H24 | 63 | -52 | -0.34 | 39 / 50 | 97 | +24 | +0.32 | 94 / 88 | 1/5 | +0.034 | 0.26 |
| k4-RU-H72 | 63 | -148 | -0.68 | 61 / 71 | 97 | +194 | +1.60 | 100 / 97 | 4/5 | +0.157 | 1.21 |
| k8-ALL-H24 | 30 | +32 | +0.18 | 57 / 67 | 64 | -131 | -1.41 | 8 / 13 | 1/5 | -0.190 | - |
| k8-ALL-H72 | 30 | +28 | +0.14 | 35 / 70 | 64 | +77 | +0.74 | 90 / 88 | 2/5 | +0.108 | 0.67 |
| k8-RU-H24 | 12 | -9 | -0.04 | 51 / 52 | 19 | -262 | -1.05 | 8 / 19 | 2/5 | -0.254 | - |
| **k8-RU-H72 (IS pick)** | 12 | **+260** | **+1.03** | 83 / 83 | 19 | **+115** | **+0.46** | 93 / 74 | 3/5 | +0.110 | **0.38** |

**IS pick, details.**
- IS by year: 2020 +827 bp (5 trades), 2021 -145 (7).
- VAL by year: 2022 -510 (2), 2023 +117 (13), 2024 +419 (4).
- Without the best trade: IS +127, VAL +36.
- Costs x1.5: IS +239, VAL +94. Entry 5 min late: IS +238, VAL +109. Entry at T + 2 h: IS +257, VAL +75.
- The edge, if any, rests on a handful of trades.

**k4-ALL-H72 (best VAL, not selectable).**
- By year: 2020 +187, 2021 -182, 2022 +111, 2023 +107, 2024 +60.
- VAL is robust to costs x1.5 (+75) and to late entries (+91, t 1.77 / +77, t 1.47).
- Its IS t is -0.38.

**Max-over-cells null.** Random-timing draws of the 12 IS cells, net of cost, give a maximum IS t with median 1.23
and 95th percentile 2.97.
- The draws are independent per cell, so this is an upper bound for 12 correlated cells.
- The IS pick's t of 1.03 sits below the median of that null.

**Run-up at entry** (alt vs BTC over 24 h, era means).
- ALL cells: +3 to +7 %.
- RU cells: +15 to +19 %.
- K2 listings: +21.5 %.

**C3 correlation.** Not computed: no cell has DEMO numbers. code/c3corr.py is ready.

## Why it fails
1. **2021 regime.** In the 2021 alt bull market, a Korean volume rush was momentum, not exhaustion. Shorting it lost
   (k2-ALL-H72 2021: -166 bp over 419 trades). In 2022-24, with no broad alt bid, the same signal faded. The sign of
   the edge depends on the market regime. Nothing in the declared rule conditions on that, and conditioning now would
   be fitted on VAL.
2. **Wallet suspensions and warnings.** IS events are dominated by coins with long Upbit wallet suspensions or
   isolation episodes: IOTA (Chrysalis), IOST, KAVA, WAVES. That repeats K1's finding. There the KRW share spikes
   with no global flow to fade. IOTA alone gives 14 of 30 k8 IS events.
3. **The listing effect is special.** K2's +1094 / +423 bp comes from a dated, announced event with a +21.5 % pump
   already in at entry. Volume-share shocks on existing markets are weaker and less clean: the k = 8 cells have only
   ~30 IS events over 2 years.

## Biases
- Upbit's current-only market list: coins delisted after a pump-and-dump are missing, which probably understates the
  short. This cannot explain the negative 2021.
- The share uses perp volume, not Binance spot volume. A global pump raises perp volume as well, so D measures the
  Korean share in excess of the global reaction, as intended.

## Pitfalls met
- The local Binance 1h file layouts differ (binance/perp_1h has no `vol` / `n` columns). The first panel build hit an
  index error, and the fix was to map columns by header.
- Six universe perps had no local funding file. They were fetched; no trade is priced with missing funding.

## What a user decision could unlock
- Nothing promotable. The VAL-only k4-H72 pattern (Korean rush fades in non-bull years) could be stated as a new,
  regime-conditioned hypothesis, but it needs a fresh, untouched era to test. IS was used and failed; HOLD stays for
  the coordinator and is too short (power 1.2-1.6 at VAL size) to reach LIVE.

## Files
- HYPOTHESES_U.md, STREAM_U.md, u_output.txt, u_results.json (this folder).
- code/: udata.py (panel, events), fetch.py (1m pull, k2rule pricing), fund.py, u.py (cells + benchmarks), count.py,
  c3corr.py.
- research/data/upbit_vol/: alt_1m/, funding/, requests.log, fetch.out, u_trades.pkl.
