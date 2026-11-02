# Round 64 stream G: altcoin catch-up after BTC one-minute shocks, result

Written 2026-11-01 09:48 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_G.md](HYPOTHESES_G.md), 09:45 UTC, before any return.
- Code: `code/g_events.py` (rows), `code/g_report.py` (12 cells), `code/g_diag.py` (where the catch-up happens).
  Stream F's `events.py` / `report.py` are imported, not edited.
- Outputs: `out/report.txt`, `out/cells.json`, `out/diag.txt`, `out/btc_cont.txt`, `out/shock_<cell>.npy`
  (per-shock net: minute, day, era, net, n coins), `out/g_events.log`. The row file `out/g_rows.npz` (137 MB, not
  git-ignored) was deleted after the run; `code/g_events.py` rebuilds it in ~2 min.

HOLD was never loaded: stream F's npz end at 2024-12 and are cut at ts < 2025-01-01 at load. No downloads, no web
searches.

## Answer: none

No cell reaches DEMO. The best IS cell is X2 H15 B (BTC move >= 2 %, BTC-hedged, 15 min):
- IS +52.9 bp per shock, t 1.56;
- VAL +0.6 bp, t 0.02.

It fails the IS t >= 2.0 bar. Every X1 cell is negative in VAL. The real max IS t over the 12 cells (+1.56) does beat
the random max-over-cells null (p95 +0.64), but only because random entries lose their whole cost. No PREREG_DRAFT.

**Why it fails:**
- **Most of the lag is permanent.** At X1 the laggards' residual in the shock minute is about -100 bp (IS) and -129 bp
  (VAL). After that, only +13 / +26 bp comes back inside the next minute, and that minute cannot be traded. From the
  tradable entry (close of e+1) a further +20 bp (IS) / +12 bp (VAL) comes back at H5, hedged and gross.
- **The cost is twice that.** A hedged trade costs 22-30 bp on the alt plus beta x 14 bp on BTC, about 40 bp in all.
- **The unhedged leg adds BTC's own move.** BTC does not keep going after a shock. At X1 it continues by +3 / +14 bp
  (IS, H5 / H15) and reverses by -17 / -20 bp in VAL (t -2.7 / -2.2; `out/btc_cont.txt`). So the unhedged cells,
  which are IS-positive, turn negative in VAL.
- This agrees with round 8: the lead is priced inside the first minute, and a bot one bar late gets a fraction of it.

## Set-up (as declared)
**Shock:**
- BTCUSDT perp, 1m close-to-close |r_B| >= X, with X in {1 %, 2 %}.
- Guard: >= 10 trades in the bar, and the next open still beyond the halfway point.
- One shock per 60 minutes.
- Counts (shocks, not returns): X1 has 601 shocks (IS 395, VAL 206; 2020-24: 184 / 211 / 114 / 49 / 43). X2 has 113
  (IS 77, VAL 36). These are more than the guess in HYPOTHESES.

**Alts:**
- Point-in-time top-40 perps other than BTC (stream F's univ.npz) with beta >= 0.5. Beta is the 7-day 1m OLS slope
  on BTC, using >= 5,000 pairs.
- A laggard has a residual r_alt - beta r_B opposite to the shock and larger than 0.5 |beta r_B|.
- There is a median of 39 eligible alts per shock and 3 laggards. X1 shocks with >= 1 laggard: 261 IS, 154 VAL.

**Trade:**
- Side = sign of the BTC shock.
- Entry at the close of e+1. The late check enters at e+2.
- Exit after H in {5, 15, 60} minutes.
- Leg U is the alt alone. Leg B is the alt minus beta x BTC.
- Equal weight across a shock's laggards. One observation is one shock, with t clustered by UTC day.

**Costs:**
- Taker 5 bp a side.
- Half-spread h = 1 bp (ETH), 3 bp (rank < 20) or 5 bp; 3h at entry and h at exit.
- The BTC hedge adds beta x 14 bp.
- Funding at the real stamps.

**Random benchmark:**
- 200 draws per shock, at random minutes in the same era and the same BTC trailing-sd decile.
- The same coins are used, with the side set by the random minute's BTC sign and the same cost.

## All 12 cells (net bp per shock; t clustered by day)
| cell | IS shocks / trades | IS net | IS t | VAL shocks / trades | VAL net | VAL t | 2020 / 21 / 22 / 23 / 24 | x1.5 t I / V | late net I / V | rand % I / V | power trade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X1 H5 U | 261 / 2742 | +1.6 | 0.18 | 154 / 2076 | -39.2 | -3.20 | +7 -1 -23 -51 -75 | -1.20 / -4.27 | -6.1 / -40.0 | 100 / 0 | < 0 |
| X1 H5 B | 261 / 2742 | -19.6 | -3.35 | 154 / 2076 | -33.0 | -4.29 | -15 -22 -25 -31 -61 | -6.68 / -7.24 | -25.7 / -29.7 | 100 / 100 | < 0 |
| X1 H15 U | 261 / 2742 | +20.2 | 1.34 | 154 / 2076 | -23.5 | -0.94 | +36 +11 -3 -41 -68 | 0.52 / -1.47 | +16.0 / -26.0 | 100 / 64 | < 0 |
| X1 H15 B | 261 / 2742 | -18.6 | -1.68 | 154 / 2076 | -16.3 | -0.72 | -15 -20 +7 -32 -71 | -3.46 / -1.72 | -20.7 / -15.4 | 100 / 100 | < 0 |
| X1 H60 U | 261 / 2742 | +18.6 | 0.78 | 154 / 2076 | -10.4 | -0.38 | +52 +0 -2 -16 -30 | 0.27 / -0.87 | +17.6 / -15.0 | 100 / 93 | < 0 |
| X1 H60 B | 261 / 2742 | -13.0 | -0.70 | 154 / 2076 | -34.2 | -1.54 | -19 -10 -16 -47 -76 | -1.78 / -2.55 | -17.8 / -32.6 | 100 / 92 | < 0 |
| X2 H5 U | 49 / 531 | -30.4 | -0.48 | 28 / 456 | -87.3 | -1.84 | +39 -71 -103 -112 -33 | -0.67 / -2.12 | -41.4 / -85.7 | 18 / 0 | < 0 |
| X2 H5 B | 49 / 531 | -34.3 | -0.98 | 28 / 456 | -27.7 | -1.25 | -6 -51 -51 +27 -35 | -1.55 / -2.21 | -17.5 / -12.7 | 68 / 100 | < 0 |
| X2 H15 U | 49 / 531 | +94.0 | 1.54 | 28 / 456 | -51.6 | -0.82 | +87 +98 -66 -52 -21 | 1.34 / -1.03 | +62.3 / -44.5 | 100 / 2 | < 0 |
| **X2 H15 B** (IS best) | 49 / 531 | +52.9 | 1.56 | 28 / 456 | +0.6 | 0.02 | +28 +68 -6 +45 -31 | 0.97 / -0.64 | +62.5 / +26.6 | 100 / 100 | 0.01 |
| X2 H60 U | 49 / 531 | +13.7 | 0.16 | 28 / 456 | -44.6 | -0.56 | +61 -14 -6 -2 -163 | 0.02 / -0.73 | -3.6 / -27.8 | 92 / 24 | < 0 |
| X2 H60 B | 49 / 531 | +30.8 | 0.67 | 28 / 456 | +3.6 | 0.06 | +79 +3 +44 +77 -150 | 0.23 / -0.32 | +33.3 / +28.1 | 100 / 100 | 0.05 |

**Max-over-12 IS t:**
- Real: +1.56.
- Null: median -0.61, p95 +0.64.
- The real value beats the null, but it is still far below the 2.0 DEMO bar.

**Random entries:**
- They average -cost: -22 to -26 bp unhedged, -36 to -44 bp hedged.
- "Beats random" is an easy bar here, as in stream F.

**Power (declared vs found):**
- To reach LIVE, the per-shock Sharpe S must be >= 3 / sqrt(0.61 n_VAL):
  - X1 (n_VAL 154 with laggards): S >= 0.31 needed. The best X1 cell has VAL S -0.03.
  - X2 (n_VAL 28): S >= 0.73 needed, which is out of reach.
- Found: every VAL S is <= +0.012.

**Checks on X2 H15 B, IS:**
- Without 2020-03-12/13: +55.4 bp (t 1.48).
- Without 2021-05-19: +39.8 bp (t 1.19).
- Without the top 3 shocks: -3.1 bp.
- The IS mean rests on three shocks.

## Where the catch-up happens (out/diag.txt; per-shock means, hedged, gross)
| X1 | residual in e | move in e+1 (not tradable) | H5 after entry | H15 | H60 |
|---|---|---|---|---|---|
| laggards IS | -99.9 | +13.3 (t 2.80) | +19.9 (t 3.42) | +20.9 | +26.7 |
| laggards VAL | -128.9 | +25.5 (t 3.29) | +12.4 (t 1.61) | +29.1 | +11.2 |
| leaders IS | +41.0 | +6.2 | +1.4 | -6.0 | -28.5 |
| leaders VAL | +59.1 | -9.3 | -9.0 | -13.1 | -22.8 |

**The effect is real but small.** Laggards do recover part of the gap: +20 bp at H5 in IS, t 3.4. Leaders give part of
their excess back. Both are well below the cost.

**Laggards minus leaders (information only, not a declared cell):**
- Hedged gross at X1 is +15 / +22 / +44 bp in IS (H5 / H15 / H60), t 1.9-2.4, and +19 / +56 / +45 bp in VAL.
- It needs two alt legs, costing ~44-60 bp round trip, so it is at or below cost.
- It was found after seeing the data, so it could only be a new declaration on new data, and its gross is about the
  size of the cost anyway.

## Pitfalls met
- **The "lag" depends on the beta estimate.** A 1m beta is attenuated (Epps effect), so some "laggards" are
  low-correlation coins whose shock-minute move was just idiosyncratic. That part never catches up. This is why only
  ~20-30 % of the residual comes back.
- **Unhedged cells measure BTC's own continuation.** BTC continued in IS and reversed in VAL. The sign flip of the U
  cells between eras is that, not catch-up.
- **The open-of-e+1 entry is not tradable.** It is zero latency and is reported as information only. Even there, X1 H5
  U is +24.8 bp in IS (t 2.68) and -20.1 in VAL.
- **No overlap issue with stream F.** F's chosen cell requires BTC to be still, and no G cell reached DEMO, so no C3 or
  F correlation was computed.

## What a user decision could unlock
Nothing at 1m bars and Binance taker cost. The recoverable part of the lag is gone inside the first minute, as round 8
found on IC. Sub-second data and execution (Binance websocket book / aggTrades, co-located) would be needed to trade the
shock minute itself. That is a different project, and it competes with professional market makers.
