# Round 63 stream O: Binance futures positioning metrics as forced-flow predictors on altcoin perps (hypotheses)

Written 2026-10-31 15:51 UTC (from `date -u`), before any metrics file beyond a 7-file format probe (SOLUSDT, OI
and ratio columns only checked for presence, no returns computed) and before any return of any rule below.
Brief: [../BRIEF.md](../BRIEF.md). HOLD (2025-01-01..) is never requested or loaded: metrics are requested only for
days <= 2024-12-31 and the 1h price panel is cut at ts < 2025-01-01 at load (round 63 C `xs.load`).

## What is new versus round 31 C
Round 31 C used Binance Vision metrics for BTC (2020-09..) and ETH (2021-12..) only, against IC prices: global
account L/S fade at 4 h (real at mid, ~0.07 sd), OI build-up fade (wrong sign), OI flush on BTC (adds nothing to the
price-only cascade). Not repeated here. New: (a) a point-in-time altcoin panel (ETH + 15 alts by volume, rotating
daily, 2022-24), (b) Binance perp execution with a BTC hedge, (c) the top-trader **position** ratio (not the global
account ratio), and (d) the taker buy/sell ratio as an hourly flow signal on alts.

## Eras (new-era split, data start 2021-12)
- DISCOVERY 2022-01-01..2023-06-30 (plays the IS role), VAL 2023-07-01..2024-12-31, both by signal time. No IS
  2020-21 exists for these series. A LIVE claim would need the user to accept this split (as for round 62 P2).
- Bars as in the brief with DISCOVERY in place of IS: LIVE t >= 2.5 DISC, >= 1.5 VAL, >= 2/3 calendar years
  (2022, 2023, 2024) positive, beats >= 95 % of random entries, HOLD power at VAL size >= 3; DEMO t >= 2.0 DISC,
  net > 0 VAL, beats >= 90 % random. Both: net > 0 in DISC and VAL, still > 0 at costs x 1.5 and one step late.

## Universe and data
- Universe on day d: the point-in-time top 40 USDT-M perps by mean daily quote volume over days d-30..d-1, listed
  >= 60 days (`xs.daily_universe` of round 63 C, the perp-only twin of round 58 `carry.universe`), then the 16
  highest-volume coins of it **excluding BTCUSDT** (ETH + 15 alts). K = 16 instead of 40 keeps the pull under ~45
  min and keeps alt costs at the 3 bp half-spread tier.
- Metrics: data.binance.vision `data/futures/um/daily/metrics/<SYM>/<SYM>-metrics-<day>.zip` (5-min stamps:
  sum_open_interest, sum_open_interest_value, count_toptrader_long_short_ratio (top account), sum_toptrader_long_
  short_ratio (top **position**), count_long_short_ratio (global account), sum_taker_long_short_vol_ratio (taker
  buy/sell)). The probe showed the ratio columns empty on some days (SOL 2022-01..03, 2022-09-01): coverage will be
  reported per year; rows with an empty field are missing data for that signal.
- Pull (subsample, declared now):
  - Tier A: every second calendar day from 2022-01-01 (day index even) for the coins in the K = 16 universe that day:
    ~8,800 coin-days. All three families use Tier A.
  - Tier B (OI flush only): the remaining coin-days where the coin is in the universe and has at least one 1h bar
    ending 02:00..24:00 with a perp close-to-close return <= -3 % (price-only condition, part of the signal itself, so
    no selection on outcomes): ~2,000 coin-days. With Tier A this makes the OI-flush event set complete for p >= 3 %.
  - Single process, 2 threads sharing one token bucket: >= 0.25 s between request starts (<= 4 / s), back off on
    418 / 429 / 503, stop on 403. requests.log: time, URL, status, bytes. Files saved under
    research/data/binance_metrics/raw/ (new empty folder), parsed with `python -I`.
- Prices: research/data/binance_1h_full (1h perp klines, `xs.load` panel: P = close at the hour instant, V = VWAP
  of the bar opening at the instant). Known gaps (STREAM_C): 2022-02-26..28 and 2022-04-01..02 for most alts;
  trades whose entry or exit price is missing are dropped (and counted).
- Funding: research/data/binance/funding (+ funding_window), stamps in (entry, exit]. Cash rate: DFF.

## Common trade mechanics
- Signal instant t = a UTC hour. Metrics stamps used are <= t - 5 min (so a stamp is public before t whatever its
  period convention). Hours t = 00:00 and 01:00 are skipped (their window needs the previous day's file).
- Entry: VWAP of the 1h bar opening at t (TWAP-like taker execution over the hour after the signal); exit: VWAP of
  the bar opening at t + H. BTC hedge: beta x BTC on the opposite side, beta = round 63 C `xs.betas` (trailing 720 h
  of hourly returns up to t, shrunk 50 % to 1).
- Return per $1 of alt notional: side x (r_alt - beta r_BTC) - funding paid on both legs (long pays +rate, short
  receives) - costs - cash rate x hold (DFF, on the alt notional; <= 1.5 bp a day).
- Costs per side: taker 5 bp + half-spread 3 bp (alt volume rank < 20 of the top 40) / 5 bp (rank >= 20) / 1 bp (ETH);
  BTC leg 5 + 1 bp, times beta. Round trip ~16 bp alt + ~12 bp x beta BTC, ~28-30 bp total.
- One open position per coin per cell (a signal while that coin's position is open is skipped).
- Checks: costs x 1.5; one step late (entry VWAP of the bar opening at t + 1, exit at t + H + 1).
- t clustered by entry day (sum of demeaned returns per UTC day). Years 2022, 2023, 2024.

## Hypotheses (sides fixed now)

### H1 OI flush -> long reversal (forced long liquidations)
Mechanism: an hour in which open interest falls sharply while price falls is long positions being closed, much of it
forced (liquidation engine, stop-outs). The forced seller pays for immediacy; once the cascade ends liquidity
providers who absorbed it are paid by a partial rebound. Signal at t: dOI = OI(t-5m) / OI(t-65m) - 1 <= -q and the
perp 1h return P(t) / P(t-1h) - 1 <= -p. Side: **long the alt, short beta BTC**. Grid: q in {2 %, 4 %}, p in {3 %,
5 %}, H in {4, 24} h: 8 cells. Information only (not cells): the price-only control (same p, no OI condition), to see
whether OI adds anything (round 31 C found it does not on BTC).

### H2 Crowding fade (top-trader position long/short ratio)
Mechanism: when the top 20 % of accounts by margin hold an unusually long (short) book, the marginal leveraged buyer
(seller) is spent and the position must eventually be unwound, so the next 1-3 days drift against the crowd.
Signal once per Tier-A day d at t = 00:00 of day d+1: X = mean of sum_toptrader_long_short_ratio over the 12 stamps
23:00..23:55 of day d; rank X against the coin's hourly means (same statistic for every hour) over the 30 calendar
days before day d (Tier-A days only; >= 8 such days with data needed). Side: percentile >= 1 - a -> **short** the
alt (long beta BTC); <= a -> **long** the alt. Grid: a in {10 %, 2.5 %}, H in {24, 72} h: 4 cells.

### H3 Taker imbalance (two fixed-side rules, both counted)
Mechanism: an hour of extreme aggressive buying (selling) is a demand shock; either it carries information and
continues (order-flow momentum) or it is temporary price pressure that reverts. Signal at t: Y = mean of
log(sum_taker_long_short_vol_ratio) over the 12 stamps t-60m..t-5m; percentile against the coin's own hourly Y over
the previous 30 calendar days (Tier-A days, >= 8 days with data). Extreme: percentile >= 1 - b or <= b.
- H3C continuation: high -> long, low -> short. H3R reversal: high -> short, low -> long.
- Grid: b in {2 %, 0.5 %}, H in {4, 24} h, 2 sides: 8 cells.

Total: **20 declared cells** (8 + 4 + 8). The selection statistic for the null is the DISCOVERY net t.

## Random benchmark and max-over-cells null
- Per cell, 500 random replications: the same number of trades per coin and era, entry hours drawn uniformly over
  that coin's eligible hours (universe day, Tier-A / Tier-B coverage, 02:00..23:00) in the same era, same hold and
  costs; side: H1 always long; H2 / H3 side recomputed from the signal's sign at the random hour (above / below the
  30-day median). Beats-random % = share of replications whose net mean is below the real one.
- Max-over-cells null: for each replication, the max DISCOVERY net t over the 20 cells; the real max is placed in
  that distribution.

## Power arithmetic (before data)
- HOLD 2025-01..2026-10 is 1.83 years. Any book needs net Sharpe per trade x sqrt(n_HOLD) >= 3; with day-clustered
  events that is an annual net Sharpe of the daily book >= 3 / sqrt(1.83) = 2.2.
- DISCOVERY is 1.5 years, but Tier A covers half the days, so for H2 / H3 DISCOVERY has the information of ~0.75
  year: the DISC LIVE bar t >= 2.5 needs an annual Sharpe ~2.9 on what we see (DEMO t 2.0: ~2.3). H1 has complete
  event coverage (Tier B), so DISC t 2.5 needs annual Sharpe ~2.0.
- H1: ~3,900 coin-days with a >= 3 % hourly drop in 2022-24 (K 20 count, ~3,100 at K 16); if a third also have
  dOI <= -2 %, ~350 trades a year -> ~640 in HOLD: per-trade net Sharpe >= 0.12 (independent) and more, since events
  cluster on market crash days (~100 days a year -> day Sharpe >= 0.22). With a 24 h hedged alt sd ~500 bp this is
  >= ~60-110 bp net per trade, gross >= ~90-140 bp; at 4 h (sd ~250 bp) >= ~30-55 bp net. Only a strong, unknown
  effect reaches LIVE; the p 5 % / q 4 % cells (~100 trades a year) can reach DEMO at most.
- H2: ~16 coins x 2 tails x a -> 3.2 (a 10 %) or 0.8 (a 2.5 %) signals per day on full data: ~1,100 / 300 a year,
  HOLD ~2,100 / 550 -> per-trade Sharpe >= 0.065 / 0.13, i.e. >= ~35 / 65 bp net on a 1-day sd ~500 bp, gross
  >= ~65 / 95 bp a day. Round 31 C's retail crowding on BTC was ~0.07 sd gross: LIVE unlikely; DEMO possible.
- H3: thousands of trades but strongly clustered; equivalent to an annual Sharpe >= 2.2 for the daily book.
  Per trade at 4 h (sd ~250 bp) with ~7,000 HOLD trades: >= ~9 bp net, i.e. gross >= ~40 bp against ~30 bp of
  cost. H3C and H3R are mirror images at the gross level, so at most one side can be positive net, and only if the
  gross |effect| exceeds ~30 bp.
- Expected max of 20 cells under the null: ~2.0 in |t| terms for independent cells (here strongly dependent pairs).

## What is not done
- No IC execution (Binance perps only), no 2025+ data, no change of side after seeing data, no grid beyond the 20 cells
  (anything else is labelled "information").
