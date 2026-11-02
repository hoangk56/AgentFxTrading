# Round 64 stream G: altcoin catch-up after BTC one-minute shocks, hypotheses

Written 2026-11-01 09:45 UTC (from `date -u`), before any return was computed. Nothing has been loaded except the
array shapes of one npz file and univ.npz (no prices printed). HOLD is never requested: stream F's npz hold only
ts < 2025-01-01 and every series is cut at ts < 2025-01-01 at load (F's `events.load_sym`).

## Mechanism and side (fixed now)
When the BTCUSDT perp moves sharply inside one minute, market makers in thinner altcoin perps hedge against BTC with a
delay (inventory and risk limits, quote refresh, stale books), so a high-beta altcoin that moved less than beta x BTC
in the shock minute should keep moving in BTC's direction over the next minutes (price discovery led by BTC; Brauneis
& Mestel / Makarov-Schoar style lead-lag on crypto). Round 8 found that on IC symbols the lead is priced inside the
first minute; this tests Binance altcoin perps at Binance costs, where books are thinner.
**Side: sign of the BTC shock-minute return** (long the laggards after an up-shock, short them after a down-shock).
This is the mirror of stream F, whose idio filter requires BTC to stay still.

## Data
- Stream F's 1m npz (research/data/binance_1m_wicks/npz, 212 symbols, 2020-01..2024-12) and univ.npz (point-in-time
  top 40 USDT-M perps by trailing 30-day quote volume, listed >= 60 days, plus daily volume rank), read-only, loaded
  with F/code/events.py (`load_sym`, `ret1`, `trailing_sd`, `ffill_idx`, `px_at`, `funding_sum`; imported, not edited).
- Funding: round 63 C panel cache via `xs.load()` (as F), stamps in (entry, exit].
- No downloads.

## Events
- Shock minute e: r_B = c_B[e] / c_B[e-1] - 1 of BTCUSDT, |r_B| >= X, X in {1 %, 2 %}.
- BTC bad-print guard (as F): bar e has >= 10 trades and quote volume > 0, bar e+1 exists and its open is still beyond
  the half-way point of the shock (up: o_B[e+1] >= c_B[e-1] (1 + r_B / 2); down: <=).
- De-duplication: a shock is dropped if another kept shock (same X) lies in e-60..e-1 (one shock per hour, same set
  for every H).
- Alt set at shock e: every symbol other than BTCUSDT that is in the top 40 on the UTC day of e, has a close at e-1, e
  and e+1, and has beta_i >= 0.5.
- beta_i: OLS slope of r_alt on r_B over minutes e-10080..e-1 (7 days, both returns valid, >= 5,000 pairs).
- Residual u_i = r_alt,e - beta_i r_B. **Laggard** if sign(u_i) = -sign(r_B) and |u_i| > 0.5 |beta_i r_B|, i.e. the
  alt moved less than half of beta x BTC in BTC's direction (it may have moved the other way).

## Trade
- Entry at the close of e+1 (one full bar late); "late" check at the close of e+2. Exit at entry + H, H in {5, 15, 60}
  min (missing exit minute: last close within 5 min, else the coin is dropped from that shock).
- Leg (fixed, 2 variants): **U** unhedged: side x (c_x / c_entry - 1) on the alt; **B** BTC-hedged: side x
  [(alt return) - beta_i x (BTC return over the same entry / exit)], i.e. the pure catch-up.
- Per shock: equal weight across its laggards; **one observation = one shock** (mean over its laggards). t clustered
  by UTC day of the shock (shocks on the same day are one cluster); shock-level t also reported.
- Grid: 2 X x 3 H x 2 legs = **12 cells**, side fixed. Cell chosen on IS (best day-clustered net t), checked on VAL
  unchanged; all 12 reported. Information only (not cells): all alts (no lag filter) and the "leaders" (alts that
  over-moved, u_i same sign as r_B), the alt's move inside e+1 (not tradable), and the open-of-e+1 entry.

## Costs (declared, as stream F)
- Taker 5 bp a side; half-spread h = 1 bp (ETH), 3 bp (volume rank < 20 that day), 5 bp (rank 20-39); entry
  half-spread 3h (minute after a shock), exit h. Alt round trip 10 + 4h = 14 / 22 / 30 bp.
- BTC hedge leg (variant B): beta_i x (10 + 4 x 1) = beta_i x 14 bp, plus its funding.
- Robustness: costs x1.5, two bars late.

## Statistics and bars
- Eras: IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31; years 2020..2024 (LIVE needs >= 4 of 5 positive).
- Random benchmark (200 replications per shock): a random minute m in the same era whose BTC trailing 1,440-minute sd
  is in the same decile (deciles of BTC sd per era) as the shock minute; the same coins as traded at the shock (betas
  at m for leg B); side = sign of r_B at m; entry close m+1, the same H, the same cost. Random % = share of
  replications whose mean net (over shocks) is below the real mean. Max-over-12-cells null: per replication the max
  IS t across the 12 random cells vs the real max IS t.
- Pitfalls: IS without 2020-03-12..13 and without March-April 2020; IS without 2021-05-19 (Binance futures outage:
  stale alt prints may look like lag but be unfillable); VAL without the LUNA (2022-05) and FTX (2022-11) months;
  concentration (top 3 shocks removed).
- Bars as in BRIEF: LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years, >= 95 % random, HOLD power at VAL size >= 3, positive
  at x1.5 and late; DEMO t >= 2.0 IS, net > 0 VAL, >= 90 % random. A pass writes PREREG_DRAFT_G_<name>.md and stops.
- Daily-P&L correlation with C3 (weekdays, IS / VAL) and with stream F's chosen cell (T5 idio H60, rebuilt from
  F/out/cand.npz read-only) for any cell at DEMO numbers.

## Power arithmetic (before data)
- Guess of shock counts after de-dup (BTC 1m sd ~0.05-0.15 %): X = 1 %: IS ~200-400, VAL ~60-120 (2022-24 BTC was
  calmer); X = 2 %: IS ~20-50, VAL ~5-20. HOLD (22 months, BTC calm in 2025-26) likely <= 0.61 x VAL rate.
- The unit is the shock (laggards in one minute share the market move). Power = S x sqrt(n_H), n_H ~ 0.61 n_VAL:
  - X1: n_VAL ~90 -> n_H ~55 -> S >= 0.40 per shock. A 15-min basket of ~10 laggards has sd ~50-100 bp, so this needs
    ~+20-40 bp net per shock after 22-30 bp of cost: only a large residual lag can do it. LIVE possible only if so.
  - X2: n_VAL ~10 -> n_H ~6 -> S >= 1.2: **LIVE unreachable**, DEMO at best.
- Prior: round 8 says the lead is gone after one minute; with entry at the close of e+1 the alts have had a full
  minute to catch up, so the residual drift is likely small vs 22-30 bp. Expected result: none, unless thin alts lag
  for several minutes on big shocks.
