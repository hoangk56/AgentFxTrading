# Round 66 stream G0: altcoin catch-up after BTC shocks, entered within seconds (hypotheses)

Written 2026-11-01 13:24 UTC (from `date -u`), before any aggTrades window was pulled and before any return was
computed. So far: robots.txt of data.binance.vision (404, logged), 6 HEAD requests and 2 test downloads for file sizes
and bandwidth (logged; zips deleted, no prices read), and BTC 1m bar ranges from stream F's npz (shock *days* only,
`code/shock_days.py`; no returns). HOLD is never requested: no file dated after 2024-12-31 is downloaded, and any
window that would need 2025-01-01 is dropped.

## Mechanism and side (fixed now, as stream G)
When BTCUSDT perp moves sharply, market makers in thinner altcoin perps re-quote with a delay, so an alt that has
moved less than beta x BTC should move toward beta x BTC. Stream G (round 64) found the returning lag mostly inside
the minute after a 1m shock bar (+13 / +26 bp hedged in e+1, IS / VAL, untradable at bar resolution) and +20 / +12 bp
more by H5, below a ~40 bp cost. G0 asks whether a bot that detects the shock from the trade stream and enters a few
seconds later captures enough of it. **Side: sign of the BTC move** (long laggards after an up-shock, short after a
down-shock).

## Data and subsample (declared before pulling)
- Source: data.binance.vision `futures/um/daily/aggTrades/<SYM>/<SYM>-aggTrades-<date>.zip`, dates 2020-01-01..
  2024-12-31 only. Columns used: price, quantity, transact_time, is_buyer_maker.
- Streamed download: each zip is read as a stream, inflated on the fly and the connection is closed once trades pass
  the day's last needed time (so only the part of the file up to the last window is transferred); zips never touch
  disk except as that stream; nothing but the extracted windows is kept. Requests >= 0.25 s apart per process, back
  off (60 s, then 300 s) on 418 / 429 / 503, stop everything on 403; every request logged (UTC, URL, status, bytes)
  in research/data/shock_aggtrades/requests.log. Parsed with `python -I`.
- **Sample frame:** UTC days with at least one BTCUSDT 1m bar whose high / low - 1 >= 1 % (such a bar guarantees a
  real-time trigger that day): 387 IS days (2020-21), 337 VAL days (2022-24).
- **Subsample (bandwidth ~2-4 MB/s, shared):** the frame days are put in one random order (numpy seed 66070),
  alternating IS / VAL, at most 60 IS + 60 VAL days, and the pull stops after 45 minutes of wall time; the days done
  by then are the sample (truncation of a fixed random order, so the sample stays random). Triggers on days outside
  the frame (2-bar moves only) are not sampled; the frame slightly favours volatile days.
- **Alt set downloaded:** the point-in-time top-40 USDT-M perps of that UTC day (stream F's univ.npz, read-only) with
  daily volume rank 10..39 (30 coins; fewer in 2020). The 9 most liquid alts (ETH, XRP, ...) are left out: they are
  the largest files and the mechanism (slow re-quoting) is about thin books. This is a declared restriction, not a
  result.
- beta_i: OLS slope of 1m alt returns on BTC over the 7 days before the trigger minute (stream G's `beta_series`,
  >= 5,000 pairs) from stream F's 1m npz (read-only, cut at ts < 2025-01-01). Alts need beta >= 0.5.

## Real-time shock detection (BTCUSDT perp aggTrades)
- At every BTC trade i at time t_i: up-trigger if p_i / min(p_j : t_i - 60 s <= t_j <= t_i) - 1 >= X; down-trigger
  if p_i / max(...) - 1 <= -X. **X = 1 %** (G's X2 = 2 % had 28 VAL shocks: LIVE unreachable, so it is not a cell).
- The detection time tau is the first trade that crosses; tau_ref = time of the window extreme (the low for an up
  trigger); r_B = p(tau) / p(tau_ref) - 1. After a trigger no new trigger for 60 minutes (one shock per hour).
- Only trades inside candidate pairs of 1m bars (2-bar high / low range >= X, a superset of every 60-s move) are
  scanned, so no trigger is missed on a sampled day.
- No look-ahead guard: everything used is known at tau.

## Laggards (known at tau)
- Alt move a_i = last alt trade price at or before tau / last alt trade price at or before tau_ref - 1 (the alt must
  have traded within 30 s before tau_ref). Residual u_i = a_i - beta_i r_B.
- **Laggard** (as G): sign(u_i) = -side and |u_i| > 0.5 |beta_i r_B|.

## Trade (8 declared cells)
- Entry at the first aggTrade on the taker's side (long: buyer-aggressor, is_buyer_maker = false; short: seller-
  aggressor) with time >= tau + L; the coin is dropped if no such trade within 10 s. That print is the price a small
  taker pays (the touch); depth is ignored (small size).
- Exit at the first opposite-side aggressor trade (long sells: is_buyer_maker = true) with time >= tau + L + H (within
  60 s, else dropped).
- **U** unhedged: side x (P_exit / P_entry - 1). **B** hedged: U minus beta_i x side x the BTC return over the same
  times, BTC filled the same way (taker prints on its own side).
- Cells: U x L {1 s, 3 s} x H {60 s, 300 s, 900 s} = 6, plus B x L 1 s x H {60 s, 300 s} = 2. **8 cells.** The cell
  is chosen on IS by day-clustered net t and checked on VAL unchanged; all 8 reported.
- Per shock: equal weight across its laggards; **one observation = one shock**; t clustered by UTC day.
- "One step late": L = 3 s for the L = 1 s cells, L = 10 s for the L = 3 s cells.

## Costs (measured, not the static model)
- Taker 5 bp a side (10 bp round trip), BTC hedge leg beta x 10 bp more.
- Spread: paid implicitly by filling on own-side prints. It is also measured: at tau + L the first buyer- and first
  seller-aggressor prints (each within 10 s) give a mid and a quoted-spread proxy; the spread cost of a leg =
  side x (P_fill / mid - 1). Reported per cell (mean / median, entry and exit, IS / VAL, random minutes vs shocks).
- Stress x1.5: net - 0.5 x (10 bp + measured round-trip spread cost) (the cell's median spread cost where a mid is
  missing).

## Random benchmark and nulls
- For every shock, 200 random times on the same UTC day (inside the streamed range, >= 60 minutes from any trigger),
  the **same coins** as the shock's laggards (their betas at that minute for B), side = sign of BTC's trailing-60 s
  move at that time (matched sign rule), the same L / H, fills and costs. Random % = share of the 200 replications
  whose mean net over shocks is below the real mean. Max-over-8-cells null: per replication the max IS t over the
  8 random cells vs the real max IS t.
- Pitfalls checked on the chosen cell: IS without 2020-03-12/13 and without 2021-05-19; VAL without 2022-05 and
  2022-11; without the top 3 shocks; by year.

## Bars (BRIEF, unchanged)
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % random, positive at x1.5 and one step late,
  HOLD power at VAL size >= 3. DEMO: t >= 2.0 IS, net > 0 VAL, >= 90 % random. A pass writes
  PREREG_DRAFT_G0_<name>.md and stops; HOLD is never opened here.

## Power arithmetic (before data)
- HOLD pace: G's 1m X1 shocks were 206 in VAL (36 months; 49 / 43 in 2023 / 2024); a 60-s trigger fires somewhat
  more often than a 1-bar close-to-close move. Guess for HOLD (22 months, calm BTC): ~70-120 shocks, ~60-100 with a
  laggard among ranks 10-39.
- Power = S x sqrt(n_HOLD) >= 3 needs per-shock net Sharpe S >= 0.30-0.39. With a per-shock sd of ~40-80 bp
  (one to a few thin alts, 1-15 min), that is +15-30 bp net per shock, i.e. +30-50 bp gross over ~10 bp taker plus
  an expected 5-20 bp round-trip spread in the first seconds after a shock.
- Sample: ~40-60 sampled days per era give ~50-90 shocks per era; IS t >= 2.5 on ~50 day-clusters needs S ~0.35+.
- Prior: G's laggards recovered ~+13-26 bp in the whole next minute plus ~+20 bp by H5 from the bar close; entering
  1-3 s after the trigger catches part of the e+1 recovery and some of the move still inside the shock minute, but
  thin-book spreads right after a shock are wide. Expected: H = 60 s / 300 s U gross of +20-40 bp, net near zero;
  LIVE unlikely, DEMO possible only if the in-minute catch-up is large.

## Amendment 2026-11-01 13:27 UTC (before any return; only the BTC trigger list of one test day was seen)
The first test day (2020-03-21) showed the point-in-time universe has only 10 members on early-2020 days, so "ranks
10..39" is empty there. Rule changed: alts of ranks 10..39 when the day's universe has >= 30 members; otherwise all
alts except ETH (ranks 2..39). The test day's file was deleted and is re-pulled in the sample.
