# Forward-test candidates

Which research candidates run on the VPS, and the stop and promotion rules each one registered **before** its forward
data existed. `app/forward_status.py` applies these rules to the closed trades in `positions`; it holds no threshold
that is not in a PREREG below. Do not change a number here after seeing forward data: a changed bar needs a new
dated PREREG.

PREREG paths are relative to `research/results/portfolio/`.

| Candidate | Bot name ends with | Tier | HOLD (n, net bp, t) | Stop (registered) | Promotion to LIVE (registered) |
|---|---|---|---|---|---|
| F3: E1 on USD-TOP days | `-ecb-f3` (live, 0.01 lot) | RELAXED | 117, +2.00, 2.16 | After 60 trades: pooled HOLD + forward t <= -1.0, or realised mean round-trip cost > 1.5 bp | Pooled day-clustered t >= 2.5, >= 100 trades, net > 0 at spread x1.5 |
| E1: short EURUSD 11:00-13:00 London | `-ecb-e1` (demo, 0.1 lot) | DEMO | 444, +0.64, 0.99 | After 100 trades: pooled t <= -1.0, or realised mean round-trip cost > 1.5 bp | Same as F3 |
| Gold $50 levels (G1-XAU50) | `-levels-gold50` (demo, 0.01 lot) | DEMO | 228, +2.87, 1.43 | After 60 trades: cumulative net < 0. After 120: below expected sum - 1.5 sd (VAL mean +3.62, sd 22.9). After 30: median entry slippage > 1 x s60 | Same as F3 |

Sources: F3 `round24_relaxed/PREREG_R24_relaxed_hold.md` (HOLD) and `PREREG_DRAFT_C_ecb_window_variants.md` (demo terms);
E1 `round13_structural/PREREG_M_eurusd_midday.md`; gold `round27_levels_opens/PREREG_G_gold_round50_cascade.md`.
C3 (Gotobi) is already LIVE and is not tracked here.

## What the module computes

- Trade net bp = price move over entry price on the real fills, minus 0.6 bp commission (the research's cost).
- Pooled t joins the HOLD run (known only by n, mean and sd, the sd implied by its reported t) to the forward trades
  as independent trades. The PREREGs cluster by day; with about one trade a day the two agree closely.
- Verdict: `NO_DATA`, `CONTINUE`, `STOP` (a registered stop fired) or `PROMOTE_CHECK` (every promotion number the
  module can read passes). `PROMOTE_CHECK` is never a promotion.

## What it cannot read (listed as `manual` in each result)

- Spread x1.5 net, and the realised round-trip cost: they need the quotes at each fill.
- Gold entry slippage against the 250 ms tick model: it is in the bot's own log. Run
  `research/.venv/bin/python -m research.tools.gold_demo_check <BotId>_trades.csv`, which also pools the exact HOLD
  trades day by day (its pooled t is the authoritative one for gold).

## Speed

Trades arrive slowly: F3 about 65 a year, gold about 60, E1 about 250. Most candidates need years to reach 100 trades,
so in practice this tracker raises stop signals early and promotion signals late.

## Data-only forward log (no fills)

`round24_relaxed/PREREG_R24_forward.md` appends F3 / E1 on Dukascopy data after 2026-09-24 (HOLD + FWD: F3 +1.86 bp,
t 1.96 to 2026-10-26). It is not a demo (no fills) and does not enter the promotion rule.
