# Round 66 stream G0: altcoin catch-up after real-time BTC shocks, entered 1-3 s later (result)

Written 2026-11-01 14:16 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_G0.md](HYPOTHESES_G0.md), 13:24 UTC, before any window was pulled; one amendment at 13:27
  UTC (alt set for small early-2020 universes), before any return.
- Code: `code/shock_days.py` (frame counts), `code/pull.py` (streamed aggTrades, real-time detection, windows),
  `code/analyze.py` (8 cells, random benchmark). Stream F's `events.py` and stream G's `g_events.beta_series` are
  imported, not edited.
- Outputs: `out/report.txt`, `out/cells.json`, `out/shocks_<cell>.npy` (per-shock tau, era, net, trades),
  `out/pull_w0.log`, `out/pull_w1.log`.
- Data: research/data/shock_aggtrades/days/<date>.npz (436 MB, 103 days), requests.log, robots.txt reply.

HOLD was never opened: only files dated 2020-01-01..2024-12-31 were requested, and no window needed 2025.

## Answer: none

No cell reaches DEMO or LIVE. The best IS cell is **U L1 H60** (laggard alone, entry at the first taker print
>= tau + 1 s, exit 60 s later):

| | net / shock | t (day-clustered) | shocks / days / trades | Sharpe per shock | Sharpe per trade |
|---|---|---|---|---|---|
| IS 2020-21 | +2.4 bp | 0.48 | 121 / 51 / 1,272 | 0.048 | 0.070 |
| VAL 2022-24 | +0.7 bp | 0.12 | 76 / 43 / 1,414 | 0.014 | 0.026 |

- It fails the IS t >= 2.0 bar by a wide margin.
- HOLD power at VAL size is 0.014 x sqrt(~340) = **0.26**, against the 3 that LIVE needs.
- The real max IS t over the 8 cells (+0.48) is below the random max-over-8 null p95 (+0.54).
- No PREREG_DRAFT is written.

**Why it fails:**
- **The catch-up is real but about the size of the taker fee.** At the trigger, laggards trail beta x BTC by -75 bp
  (IS) / -87 bp (VAL). From tau + 1 s they recover a mid-to-mid **+17 / +12 bp in the next 60 s**. Filled on taker
  prints (spread included), gross is +14 / +11.5 bp per trade. Taker fees take 10 bp, leaving +4 / +1.5 bp per
  trade and +2.4 / +0.7 bp per shock.
- **Spreads are not the problem.** The measured round-trip spread actually paid (own-side print vs the mid of the
  first bid and ask prints) is only 1-2 bp. The quoted-spread proxy at tau + 1 s is 1.7 / 1.4 bp (median). Top-40
  Binance perps sit on one tick even in a shock. The cost is the fee.
- **It decays fast.** Two extra seconds (L3) cost 2-5 bp. At L10 the VAL mid gain at H60 is +2 bp. Beyond 60 s the
  VAL path turns negative (H900 mid -0.7 bp at L1, -10.5 bp at L10), so longer holds only add noise.
- **The BTC hedge does not help.** It costs beta x 10 bp more. BTC continued after IS shocks and reversed after VAL
  shocks (as in stream G), so hedged cells are IS-negative (B L1 H300 t -2.39) and VAL-flat.

## Set-up (as declared)
**Frame and sample:**
- The frame is the UTC days with a BTCUSDT 1m bar range >= 1 % (387 IS / 337 VAL days).
- The days were put in a fixed random order (seed 66070), alternating eras.
- Two workers pulled for 45 minutes (13:28-14:14 UTC) and finished **103 days (57 IS, 46 VAL)**. 101 of them were
  used; 2 early-2020 days had no alt files.
- Transfer: 2,956 requests, 8.9 GB. Each zip was streamed and inflated in memory, and the connection was closed past
  the day's last needed time.
- Errors: 4 x 404 (FTT, LEND) and 10 timeouts or URL errors. Those coin-days were dropped. There were no 403 / 418 /
  429 / 503 responses.

**Real-time trigger:**
- A trigger fires when a BTCUSDT perp trade is >= 1 % beyond the trailing-60 s extreme. Only one trigger per 60 min.
- This gave **246 triggers**:

  | | 2020 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|
  | triggers | 78 | 86 | 50 | 20 | 12 |
  | with >= 1 laggard | 52 | 69 | 48 | 18 | 10 |

- Most triggers come 30-60 s after the window extreme: they are fast grinds, not one-print jumps.

**Alts and laggards:**
- Alts are the point-in-time top-40 perps of rank 10..39 (ranks 2..39 when the universe has < 30 members), with
  7-day 1m beta >= 0.5. The median is 30 eligible alts per trigger.
- A laggard is an alt whose residual at tau (last trades at tau vs tau_ref) is opposite to the shock and larger
  than 0.5 |beta r_B|.

**Trade:**
- Side = the BTC sign.
- Entry at the first own-side taker print >= tau + L (within 10 s). Exit at the first opposite-side print
  >= tau + L + H (within 60 s).
- Equal weight across a shock's laggards. One observation is one shock, with t clustered by UTC day.

**Costs:**
- Taker 5 bp a side; the hedge leg adds beta x 10 bp.
- The spread is paid through the print prices and measured as above.
- The x1.5 stress adds 0.5 x (fee + measured spread).

**Random benchmark:**
- 200 random times per shock on the same day, >= 60 min from any trigger.
- The same laggard coins are used, with side = the sign of BTC's trailing-60 s move and the same L / H, fills and
  costs.

## All 8 cells (net bp per shock; t clustered by day)
| cell | IS net (t) | VAL net (t) | S shock I / V | S trade I / V | 2020 / 21 / 22 / 23 / 24 | x1.5 I / V | late I / V | rand % I / V | gross / trade I / V | spread rt paid I / V (mean) | power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **U L1 H60** (IS best) | +2.4 (0.48) | +0.7 (0.12) | 0.048 / 0.014 | 0.070 / 0.026 | +11 -4 +7 -9 -13 | -3.6 / -4.8 | +0.4 / -3.5 | 100 / 100 | +14.1 / +11.5 | 1.5 / 0.9 | 0.26 |
| U L1 H300 | -5.5 (-0.61) | +0.9 (0.07) | -0.055 / 0.008 | 0.049 / -0.050 | +6 -14 +5 +3 -22 | -11.4 / -4.7 | -7.7 / -3.0 | 84 / 100 | +15.3 / +4.9 | 1.2 / 0.8 | 0.15 |
| U L1 H900 | -0.2 (-0.02) | -1.2 (-0.08) | -0.001 / -0.009 | 0.073 / -0.109 | +0 -0 +7 -2 -40 | -5.9 / -6.6 | -2.1 / -4.6 | 90 / 96 | +19.8 / -2.8 | 1.1 / 0.7 | < 0 |
| U L3 H60 | +0.4 (0.08) | -3.5 (-0.59) | 0.008 / -0.068 | 0.032 / -0.053 | +8 -5 +2 -14 -12 | -5.8 / -9.1 | -0.4 / -9.6 | 100 / 100 | +11.9 / +7.0 | 1.8 / 1.1 | < 0 |
| U L3 H300 | -7.7 (-0.85) | -3.0 (-0.24) | -0.076 / -0.026 | 0.020 / -0.092 | +3 -16 +0 -2 -21 | -13.7 / -8.6 | -10.9 / -8.3 | 66 / 98 | +12.2 / +0.8 | 1.5 / 0.9 | < 0 |
| U L3 H900 | -2.1 (-0.17) | -4.6 (-0.31) | -0.013 / -0.038 | 0.056 / -0.143 | -2 -2 +3 -6 -40 | -7.9 / -10.1 | -6.6 / -9.9 | 80 / 85 | +17.5 / -6.6 | 1.3 / 0.8 | < 0 |
| B L1 H60 | -6.5 (-1.84) | -2.3 (-0.36) | -0.195 / -0.044 | -0.159 / 0.020 | -4 -9 -2 -16 +19 | -17.3 / -14.4 | -8.6 / -0.3 | 100 / 100 | +12.6 / +23.8 | 1.6 / 1.5 | < 0 |
| B L1 H300 | -13.7 (-2.39) | +1.5 (0.16) | -0.216 / 0.019 | -0.209 / 0.050 | -6 -19 +4 -9 +9 | -24.3 / -10.9 | -15.4 / +3.9 | 98 / 100 | +2.5 / +26.6 | 1.1 / 1.9 | 0.35 |

"late" is L3 for the L1 cells and L10 for the L3 cells.

**Random benchmark:**
- Random entries average -8 to -11 bp unhedged and -19 to -23 bp hedged, which is just the fee.
- "Beats random" is therefore an easy bar, as in streams F and G. The real max IS t (+0.48) still does not beat the
  max-over-8 null (median -1.17, p95 +0.54; 94 % of replications below it).

**Power:**
- 76 VAL triggers with laggards came from 46 sampled VAL days. That implies ~557 in the full VAL frame and ~340 in 22
  HOLD months at the VAL pace.
- That is a large count, but S per shock is <= 0.05 in every VAL cell, so power is <= 0.35.
- LIVE would need S >= 0.16 at that count: about +10 bp net per shock, i.e. roughly double the present gross.

## Where the catch-up happens (laggard rows, unhedged, gross mid-to-mid, bp per trade)
| | residual at tau | L1 H60 | L1 H300 | L1 H900 | L3 H60 | L10 H60 | L10 H900 |
|---|---|---|---|---|---|---|---|
| IS | -74.7 | +17.1 | +20.6 | +27.5 | +15.1 | +14.8 | +18.9 |
| VAL | -87.4 | +12.4 | +5.7 | -0.7 | +8.1 | +2.1 | -10.5 |

Compared with stream G (bar close, entry one bar late, +20 / +12 bp at H5 hedged), entering 1 s after a real-time
trigger roughly doubles the first-minute capture in VAL. It still recovers only ~15-20 % of the lag. Most of the
residual is permanent: a mismeasured 1m beta (Epps effect), or genuinely idiosyncratic moves.

## Pitfalls met
- **Sample.** This is a random 103 of 724 frame days, a 45-minute pull. Triggers on days without a >= 1 % 1m bar
  are not sampled.
- **De-dup across days.** The 60-min de-dup is applied within a day only. A trigger in the first hour of a sampled
  day is not suppressed by one late on the previous (unsampled) day. This affects few shocks.
- **Fill model.** The touch print is taken as fillable at any size, and depth is ignored. A real order of size would
  pay more, which only strengthens the "none".
- **Spread proxy.** The quoted-spread proxy at random minutes (first ask print vs first bid print, both within 0.5 s)
  is 0.4-0.9 bp. It is biased low where prints are sparse. The cost that matters, the spread paid on own-side prints
  at the shocks, is measured directly (1-2 bp round trip).
- **Hedged cells measure BTC's own continuation.** BTC continued in IS and reversed in VAL, so the hedge flips sign
  between eras, as stream G found.

## What a user decision could unlock
Nothing at taker cost. The edge is ~+12-17 bp gross per trade in the first 60 s, and the fee is 10 bp.

**Untested: maker execution.** With maker fees (~2 bp a side, lower with VIP or BNB discounts), the same mid-to-mid
gain would net ~+8-13 bp. But a limit order on a lagging alt during a BTC shock fills mostly when the price moves
against it (adverse selection). aggTrades cannot show whether a resting order would have filled, so this would need
order-book (depth) data or live paper trading.

That is a different execution project. It is not a pass under the present bars.
