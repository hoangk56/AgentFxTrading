# Round 64: parallel streams under a coordinator (Q, K, F, N, V, T, X, G, S, L), 2026-11-01

Shared brief: [round64_parallel/BRIEF.md](round64_parallel/BRIEF.md) (08:50 UTC; streams V, T, X, G, S, L appended
as slots freed). Coordinator queue: [round64_parallel/QUEUE.md](round64_parallel/QUEUE.md). Subagents never opened
HOLD; the coordinator re-implemented each candidate, reproduced its IS / VAL numbers exactly, registered it with code
hashes and opened HOLD once.

## Answer first
- **No LIVE candidate.** F passed every LIVE bar on IS / VAL and failed HOLD (t 1.17).
- **New DEMO that passed HOLD: K2** (short the Binance perp after an Upbit KRW listing, long BTC, 72 h): HOLD n 92,
  +221 bp/trade, t 0.88 ([PREREG_K2](round64_parallel/K/PREREG_K2_upbit_listing_fade.md)).
- DEMO drafts not yet opened: Q1 (COIN-M vs USDT-M perp gap, crash-day rule; HOLD needs a 2025-26 COIN-M pull, kept
  for the coordinator), S peg100 (stablecoin discount; not opened: VAL is one week, ~2 HOLD episodes, loses to cash).

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| Q | Binance derivative vs derivative: Q1 COIN-M perp vs USDT-M perp gap, Q2 quarterly vs perp, Q2b last-24 h delivery convergence (no borrow) | Q1 k100_H72 **DEMO numbers** (IS +440 bp t 2.20 n 54, VAL +78 t 3.82 n 181, 5/5 years) but 95-98 % of P&L on 5 crash days, outside them VAL t 0.29; power per event-day 1.47. Q2 / Q2b none | [STREAM_Q.md](round64_parallel/Q/STREAM_Q.md), [PREREG_DRAFT_Q](round64_parallel/Q/PREREG_DRAFT_Q_cm_um_perp_gap.md) |
| K | Upbit: K1 coin-specific kimchi premium -> Binance perp; K2 short Binance perp after an Upbit KRW listing | K1 none (gap closes by Upbit falling, sign flips); **K2 DEMO, HOLD passed** (see below) | [STREAM_K.md](round64_parallel/K/STREAM_K.md) |
| F | Fade 1m liquidation wicks on top-40 altcoin perps (>= 5 %, BTC still), next-bar entry, 60 min | **all LIVE bars on IS / VAL, FAILED HOLD** (see below) | [STREAM_F.md](round64_parallel/F/STREAM_F.md), [PREREG_F](round64_parallel/F/PREREG_F_wick_fade.md) |
| N | Run B from a standing long-spot / short-perp inventory (no borrow) | **not viable**: VAL inventory -6.9 %/yr vs cash, combined -5.5 %/yr (t -3.96); ~$110-150k capital per $1k B trade | [STREAM_N.md](round64_parallel/N/STREAM_N.md) |
| V | Venues that lend B's coins (scouting) | Gate 92 %, Bybit 73 %, OKX 69 % of B's coins at ~6 %/yr, but their spot misses the Binance-specific drop (+40-50 bp shortfall, ~1/4 of B's VAL net); Binance allows margin on 73/75 coins, so the user's 0/495 is an account-level block | [STREAM_V.md](round64_parallel/V/STREAM_V.md) |
| T | Perp delisting convergence to settlement | none: IS 1 event; VAL perp sits on spot at T-24 h (median +5.8 bp); short-rich side -141 bp t -2.15 | [STREAM_T.md](round64_parallel/T/STREAM_T.md) |
| X | Long Binance spot when cheap vs other venues' spot, perp-hedged | none: every cell loses the 42-50 bp cost (k100_H24 IS -59.5 t -5.76, VAL -76.3); the perp is as cheap as spot at these signals | [STREAM_X.md](round64_parallel/X/STREAM_X.md) |
| G | Altcoin catch-up after BTC 1m shocks | none: best IS t 1.56, VAL ~0; the lag that returns is mostly inside the untradable next minute | [STREAM_G.md](round64_parallel/G/STREAM_G.md) |
| S | Stablecoin peg reversion (buy the discounted stablecoin) | peg100 **DEMO numbers** (IS +22 bp t 6.97 by episode, VAL +65 t 1.34) but VAL = SVB week (without it -8.4), 4 VAL episodes, power 0.71, standing book below cash: draft, HOLD not opened | [STREAM_S.md](round64_parallel/S/STREAM_S.md) |
| L | K2's frozen rule on Coinbase listings | none: IS -621 t -0.81, VAL +151 t 0.73; no pump before entry (+4-7 % vs +21.5 % on Upbit); pooled with K2 flips K2's IS sign | [STREAM_L.md](round64_parallel/L/STREAM_L.md) |

## F: fade idiosyncratic 1-minute wicks (registered, HOLD failed)
Rule: top-40 USDT-M altcoin perp moves >= 5 % close-to-close in one minute while BTC moves <= 0.2 x as much; long after
a crash / short after a spike at the close of the next minute; exit 60 minutes later; 22-30 bp costs.
- IS +273.0 bp (t 4.05, n 380), VAL +270.5 (t 3.76, n 770), 5/5 years, x1.5 / 2 bars late / mean-OHLC fills positive,
  per-trade power 3.53 (day-clustered 2.93). Coordinator stress: paying both full one-minute ranges kills it (VAL +0.6).
- HOLD (2025-01..2026-10-29, universe rebuilt from all 886 perps minus stablecoin / index / TradFi underlyings; 16 TradFi
  stock perps of 2025-26 dropped by fapi underlyingType before any price was read; 2026-10-28 filled from fapi REST
  because data.binance.vision had no file): **n 2,080, +41.8 bp, t 1.17**; x1.5 +28.8, late +63.2, 2025 +93.9, 2026
  +27.5. Gate t >= 2.0 failed. Top-5 coins = 102 % of net. **Dropped.**
- Lesson: the reversal of liquidation wicks is now mostly taken inside the first minute; an IS / VAL edge of +270 bp
  kept ~15 %. The event count rose 4.4 x because 2026's top 40 is full of new thin coins.

## K2: Upbit KRW-listing fade (registered, HOLD passed as DEMO)
- IS n 11 +1,094 bp (t 3.16), VAL n 29 +423 (t 1.37); random 100 %; generic pumps without a listing lose (t -2.3 to
  -3.0); C3 correlation ~-0.03.
- HOLD: 92 listings (Upbit listed many coins with existing Binance perps in 2025-26): **+221 bp, t 0.88**, median +656,
  gross +775, funding -512 (crowded shorts after listing pumps), x1.5 +200, L + 2 h +160; 2025 -110 (n 45), 2026 +539
  (n 47); worst -9,959 bp.
- Tier **DEMO (HOLD passed)**. Promotion: HOLD + demo pooled t >= 2.5 with n >= 40, rule unchanged. Stop rule: after 10
  demo trades cumulative net < -2,500 bp, or pooled mean < 0 after 20 pooled trades. A demo needs a bot polling Upbit's
  market list and shorting Binance perps: **user decision**. Funding is now the dominant cost; nothing was re-optimised.

## Q1 HOLD (opened later the same day by the coordinator)
Registered as [PREREG_Q1](round64_parallel/Q/PREREG_Q1_cm_um_perp_gap.md) at 10:43 UTC, run once at 14:08 UTC: n 37 on
7 event-days, **+299.2 bp, t 2.15**, x1.5 +284, T + 2 min +334; top-5 days 101 % of net (2025-10-10 / 11). **DEMO,
HOLD passed**, crash-day rule (~4 event-days a year).

## What a user decision could unlock (added to the standing list)
- K2 demo / paper bot (Upbit market list poll + Binance perp short + BTC long; ~50 events a year at 2025-26 pace).
- B: fix borrowing on the Binance account (margin is allowed on 73/75 of B's coins, so the block is account-level);
  Gate / Bybit / OKX lend the coins but would be a different test (their spot misses part of the move).
- Q1 / S drafts: Q1's HOLD needs a 2025-26 COIN-M pull (coordinator can do it; low value: crash days only).

## Pitfalls found this round
- data.binance.vision had no 2026-10-28 daily 1m file for any symbol on 2026-11-01: fill from fapi REST and log it.
- Binance lists TradFi stock / ETF / commodity perps since 2025 (INTC, MU, SAMSUNG, SOXL...): a "top-N altcoin perp"
  universe must drop them by fapi exchangeInfo underlyingType (fapi robots.txt only blocks named search bots).
- api.binance.com robots.txt is "Disallow: /"; use data.binance.vision or fapi.
- Large `.npz` outputs under results/ were not git-ignored: `.gitignore` now ignores `research/results/**/*.npz` / `*.npy`.
- Importing another stream's fetch module can write into that stream's requests.log (L wrote to K's log once).

## Standing after round 64
C3 is the only LIVE algorithm. DEMO that passed HOLD: B (round 63, blocked by borrow), X3 (round 61), K2 (new).
Round 65 ([round65_retail_venues/BRIEF.md](round65_retail_venues/BRIEF.md)) tests whether K2's mechanism generalises
across retail venues (Bithumb listings, Upbit volume-share shocks, a scout of other retail venues).
