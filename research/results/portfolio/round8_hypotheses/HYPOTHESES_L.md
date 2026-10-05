# Stream L hypotheses: operational definitions (written 2026-10-05 ~01:00 local, before any return was computed)

The mechanisms and sources are those of STREAM_L.md (written 2026-10-04 17:58 UTC, before any number). This file
fixes the exact rules so that the numbers cannot shape them. Only data availability (bar counts) was looked at before
writing it (`out/l0_avail.txt`). New hypotheses are appended at the bottom, each before its numbers.

## Common conventions (all families)

- Price: panel mid, forward-filled for at most 10 minutes (a longer gap = market closed, sample invalid).
  p = ln(mid). Returns in bp = 1e4 * difference of p.
- Signal minute t: everything known at the close of minute t. Leader move over k minutes: x = p_A[t] - p_A[t-k].
  Entry at the close of minute t+1 (mid[t+1]); exit at the close of minute t+1+h. Target y = p_B[t+1+h] - p_B[t+1]
  (in bp). The minute t -> t+1 is never in the target (removes the non-synchronous-close artefact and gives a bot a
  full minute to act). Latency variant: entry t+2, exit t+2+h.
- Vol scaling: for each symbol, UTC day and k, realised sd of non-overlapping k-minute returns over the day; the
  scale on day d is the RMS over the previous 20 days with data (current day excluded). x_sd = x / scale_k.
  The follower's own past move z = p_B[t] - p_B[t-k], scaled the same way, is the control.
- Sessions (UTC): Asia 23:00-07:00 (belongs to the day that ends at 07:00), Europe 07:00-13:00, US 13:00-20:00. A
  sample needs t >= session start and t+1+h <= last minute of the session, so every trade opens and closes inside
  its session (no swap: nothing crosses 21:00 UTC).
- Statistic: OLS y_bp = a + b x_sd + c z_sd per cell, era and session; b = bp of follower move per 1 sd of leader
  move. t = day-clustered (sandwich with one cluster per session-day), computed from per-day moment sums.
  Secondary: the same with y divided by the follower's trailing h-minute scale (robust to crisis periods).
  Primary ranking statistic: IS t of b (bp version).
- Eras: IS 2016-01..2021-12, VAL 2022-01..2024-12. HOLD (2025+) is not in the panel and is never opened.
- Chance benchmark for scans: (a) max |t| of K independent normals; (b) an empirical null obtained by pairing the
  leader's day d with the follower's day d + delta (random delta of 5..60 days, same session), recomputing the whole
  matrix 20 times, recording max |t| each time.

## L1 systematic matrix

All ordered pairs (A, B), A != B, of the 26 symbols; k in {1, 5, 15, 60}; h in {1, 5, 15, 60}; 3 sessions:
650 x 16 x 3 = 31,200 cells. Report K, the chance max |t| (both benchmarks), the top 30 cells by IS |t| with their
VAL b and t (sign kept?), the follower response in the top IS decile of |x_sd| (mean of sign(b_IS) sign(x) y, bp)
and the follower's median executable cost at those minutes (spread/2 at entry + spread/2 at exit + commission 0.6 bp
for FX and metals). A cell "repeats" if VAL b has the IS sign and VAL t >= 1.5.

## L2 named economic leads (two-sided tests unless a sign is given; k in {1, 5, 15}, h in {1, 5, 15, 60})

Each sub-hypothesis is a family of (leaders x followers x 3 k x 4 h) cells in its own window:
- L2a JP225 -> USDJPY, 00:00-06:00 UTC, expected b > 0.
- L2b US500, USTEC -> AUDJPY, USDJPY, AUDUSD, 13:30-20:00 UTC, expected b > 0 for all three.
- L2c XAUUSD -> AUDUSD, 00:00-20:00 UTC (each of the 3 sessions), expected b > 0.
- L2d XAUUSD -> XAGUSD, XPTUSD, 00:00-20:00 UTC, expected b > 0.
- L2e XTIUSD, XBRUSD -> USDCAD, 07:00-20:00 UTC, h restricted to {1, 5, 15}, expected b < 0.
- L2f DE40 -> EURUSD and UK100 -> GBPUSD, 07:00-09:00 UTC, two-sided.
- L2g BTCUSD -> ETHUSD, all hours except 20:00-23:00 UTC (rollover spreads), h in {1, 5, 15}, expected b > 0.
- L2h USD factor. u_j = USD-signed return of pair j (EURUSD, GBPUSD, AUDUSD, NZDUSD sign -1; USDCAD, USDCHF, USDJPY
  sign +1). F = mean of the 7 u_j. (i) F(k) -> XAUUSD, expected b < 0. (ii) Laggard catch-up: target = future
  u_j over h; regressors -dev_j(k) = -(u_j(k) - F(k)) (sd-scaled) and F(k); expected slope on -dev_j > 0, pooled
  over the 7 pairs (day-clustered) and per pair. Sessions as L1.
- L2i US500 -> AUS200 (00:00-06:00), JP225 (00:00-06:00), HK50 (01:30-08:00), expected b > 0.
- L2j crosses: synthetic EURJPY = EURUSD * USDJPY, GBPJPY = GBPUSD * USDJPY, AUDJPY = AUDUSD * USDJPY.
  (i) deviation d_t = p_cross[t] - p_synth[t] in bp, its distribution vs the cross's spread; (ii) does -d_t predict
  the cross's return from t+1 to t+1+h (h in {1, 5, 15})? (iii) synthetic k-minute return -> cross future return,
  controlling for the cross's own k return. Expected: no tradeable lag.

Multiple testing in L2: the count of cells per sub-hypothesis is reported with the best |t| and the chance max.

## L3 dynamic lead-lag (Huth & Abergel 2014)

For each L2 leader/follower pair (in its L2 window): per day, moments of y (h = 5, gap 1) on x (k = 1). The
trailing estimate on day d = OLS t of the slope pooled over the previous 20 days with data (day d excluded).
Day d is "on" when |t_trail| is at or above the 67th percentile of all previous |t_trail| values of that pair
(expanding window, at least 60 earlier values). On "on" days the predicted sign is sign(t_trail). Test: mean of
sign(t_trail) * b_d on "on" days vs "off" days (b_d = that day's realised slope), and the trading rule below on "on"
days only.

## Trading rule (the best cell of each family, chosen on IS only)

Enter the follower at the close of t+1 when |x_sd| >= theta, direction sign(b_IS) * sign(x); exit at the close of
t+1+h; no stop. theta = the IS percentile of |x_sd| in that window, chosen on IS from {90, 95, 99}. One position per
follower at a time (no new entry before the exit). Cost = spr[entry]/2 + spr[exit]/2 (in bp of mid) + 0.6 bp
commission for FX and metals; none for indices, energies, crypto. Report IS and VAL: n, mean mid, mean cost, mean
net, day-clustered t (net), years net > 0, spread x 1.5, +1 minute latency, random-entry control (same number of
trades and side mix, same hold, random minutes in the same session window and weekday mix, 200 seeds; percentile of
the real net), per-trade Sharpe and power = Sharpe * sqrt(trades per year * 1.75).

## Added 2026-10-05 ~01:15 local, after the L1 matrix (so: data-mined, NOT a pre-written mechanism)

- L1-UK100 (post hoc). The top 30 L1 cells by IS |t| are almost all "index or JPY cross -> UK100 in Asia hours,
  h = 60" (b ~ +5.6 bp per leader sd, IS t 14, VAL t 1.6-3.2). Suspected mechanism: IC's UK100 quote is stale /
  thin during 23:00-07:00 UTC (FTSE futures liquidity), so it catches up with US/EU/JP index moves within the hour.
  Checks (before looking): (a) hour-of-entry profile of the slope and of UK100's bar coverage, tick count and
  spread; (b) per-year slope; (c) the pre-specified trading rule on the best L1 cell (Asia k15 h60 US30 -> UK100)
  and on the best cell by IS top-decile mid minus cost. It cannot be a candidate under the brief (mechanism not
  written before the data) unless it is re-registered; at most it is a lead.
- L1-XNG (post hoc): energy -> XNGUSD in Asia at h = 1 (t 7-8 in both eras). Same stale-quote suspicion; XNG
  costs 28-46 bp round trip. Only the trading rule is checked.
- Diagnostics (out/l1_uk100.txt) showed the UK100 slope is dominated by a few nights (2016-11-09, 2020-03, 2017-04-17
  Easter Monday, 2018-02-06) and that the partial slope (5.6) is much larger than the raw slope (0-2.5 bp/sd by hour),
  i.e. the cell is mostly "UK100's own Asia-hours move relative to US30 reverts" (quote noise inside a 5-7 bp spread).
  Post-hoc variant added before computing it: signal s = b_IS x_sd + c_IS z_sd (the fitted IS partial model), trade
  UK100 when |s| >= IS P90/P95/P99, hold 60 min, Asia window. Also: the best L1 cell by IS top-decile (mid - cost),
  searched over the 883 cells with |t_IS| >= 4 (pre-screened by |b| x 2 / session cost, top 15 evaluated exactly).
- Null check (out/l1_nullcheck.txt): under the day-shift null the largest |t| (6-8) come from UK100 as a leader in
  Asia, where one day carries ~20 % of the cross-product (quote spikes). Day-clustered t is unreliable with such
  leverage. Added (before computing): L1-robust = the same matrix with x_sd and z_sd clipped to [-5, 5] and y clipped
  to +-10 x the follower's trailing h-minute scale; same 20 day-shift null replications. Robust version is a
  sensitivity check of the screen, not a new family.
