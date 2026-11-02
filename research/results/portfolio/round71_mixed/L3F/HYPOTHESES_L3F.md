# Round 71, stream L3F: extreme negative funding, follow the day's direction for 24 h (forward-only)

Written 2026-11-01 17:49 UTC (`date -u` at 17:49:29), before any return was computed. Source: LIT L3 (SSRN 7520320,
274 events BTC / ETH / SOL 2021-26). The paper's sample includes 2025-26, so this rule is **forward-only**: HOLD is
never graded; a pass on IS / VAL gives a FORWARD registration from 2026-10-30.

## Mechanism
An extreme negative funding print marks a crowded short side. On a day that is already rising, shorts are being
squeezed and forced covering can continue for a day (follow up). On a day that is falling, the negative funding
confirms a deleveraging cascade of longs into shorts that keeps going (follow down). Funding is the stress filter;
the day's sign picks the side. Prior doubt: 1-day momentum failed at IC in rounds 2 / 7; X1 (weekly momentum) is
only partly supported; round 62 found the post-stamp move for large stamps is in the first seconds, not over 24 h.

## Data (local only, cut at ts < 2025-01-01 at load; nothing after is read into memory)
- Funding: research/data/binance/funding/<SYM>.csv (t, rate).
- 1h perp klines: research/data/binance_1h_full/1h/<SYM>.csv (ends 2024-12-31); if a symbol is missing there,
  research/data/binance_basis/perp_1h/<SYM>.csv cut at t < 2025-01-01.
- Universe: round 58 `carry.universe(P, N=10)` on `load_panel` (perp_1d / spot_1d / funding, hold=False):
  point-in-time top 10 by trailing 30-day perp quote volume, listed >= 60 days, spot + perp valid. Universe U12 =
  BTCUSDT + ETHUSDT + that day's top 10 (day of the stamp, previous UTC day's ranking to avoid same-day volume).
  Universe U2 = BTCUSDT + ETHUSDT only.

## Event definition
- Stamp time T = funding timestamp rounded to the hour. Rate normalised to an 8h equivalent:
  f8 = f x 8 / dt, dt = hours since the coin's previous stamp, rounded and clipped to [1, 8] (Binance moved some alts
  to 4h / 1h intervals; BTC / ETH stay 8h).
- Event: f8 < 0 **and** f8 <= the q-th percentile of the coin's f8 over stamps in [T - 180 d, T) (current stamp
  excluded), q in {5, 10}; needs >= 90 days of prior stamps (first stamp <= T - 90 d) and >= 100 stamps in the window.
  The f8 < 0 condition stops degenerate events when the 5th percentile sits at the 0.01 % floor (2021 BTC).

## Side rule (fixed before data)
- Day return r_d = ln(P_T / P_D0), P_T = close of the 1h bar ending at T, P_D0 = open of the first 1h bar of the UTC
  day that contains T - 1 ms. So a 00:00 stamp uses the full previous UTC day; 08:00 uses 00:00-08:00; 16:00 uses
  00:00-16:00. Side = sign(r_d): long if up, short if down; r_d == 0 skipped.

## Trade
- Entry: close of the 1h bar [T, T+1h) (price at T+1h, one hour after the signal is known: tradable, and it skips
  round 62's first-minute post-stamp move). Exit: close of the bar [T+24h, T+25h) (24 h hold).
- One position per coin at a time: an event while that coin is held is skipped. Trades must exit before
  2025-01-01; era by entry time (IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31; 2019 stamps are history only).
- Return per trade (unit notional) = side x (P_exit / P_entry - 1) - side x sum of funding stamps f in
  (entry, exit] (long pays f, short receives f) - costs.
- Costs: taker 5 bp a side + half-spread a side (round 58 `half_spread`: BTC / ETH 1 bp, other rank < 10 3 bp,
  else 5 bp) = 12 bp round trip for BTC / ETH, 16 bp for top-10 alts. Checks: costs x1.5; one step late (entry and
  exit one bar later: close of [T+1h, T+2h) to close of [T+25h, T+26h)).

## Declared cells (4)
| cell | universe | q |
|---|---|---|
| C1 | U2 (BTC / ETH) | 5 |
| C2 | U2 | 10 |
| C3 | U12 (BTC / ETH + top 10) | 5 |
| C4 | U12 | 10 |
Hold fixed at 24 h (the paper's horizon), no other knobs. The cell is picked on IS (highest IS t), checked on VAL
unchanged. Max-over-cells null reported.

## Statistics and bars (BRIEF, unchanged)
- Net bp / trade, t clustered by entry UTC day; robustness: Newey-West (lag 5) t on the equal-weight daily book
  (each trade's return spread over its days not needed: book return booked on the entry day, NW absorbs overlap).
- Years: 2020-2024 each, >= 2/3 positive (4 of 5 overall; reported per era too).
- Random benchmark (a) random entries: same number of trades per era, drawn from all stamps of coins in the same
  universe and era (no funding condition), same side rule, same costs and hold; 1,000 draws; percentile of the cell's
  net mean. (b) shuffled side: real events, random side. LIVE needs >= 95 % on (a) and (b); DEMO >= 90 %.
  Max-over-cells: the selected cell's IS t vs the distribution of max-over-4-cells t of random-entry draws.
- LIVE: t >= 2.5 IS, >= 1.5 VAL, net > 0 both, >= 2/3 years positive, costs x1.5 and one step late positive,
  random >= 95 %, power >= 3. DEMO: t >= 2.0 IS, net > 0 VAL, random >= 90 %.

## Power arithmetic (before data)
Power = per-trade Sharpe (net, VAL) x sqrt(n over the window). HOLD-equivalent window 1.83 years. Prior event rate
(LIT): ~50 / yr for 3 coins, ~150 day-clusters / yr on a top-40; for U12 guess ~80-120 trades / yr, U2 ~25-40.
- U12 at 100 / yr: n = 183, needed SR >= 3 / sqrt(183) = 0.22. Paper: follow-day gap 3.6 pp (+1.8 % per trade) on
  a 24 h sd ~5-6 % on stress days -> SR ~0.3 gross; at half size net of 16 bp -> (0.9 - 0.16) / 5.5 = 0.13,
  power ~1.8.
- U2 at 30 / yr: n = 55, needed SR >= 0.40: out of reach unless the full paper effect holds.
- Expectation: P(LIVE) ~1 %, P(DEMO) ~5 % (LIT). Forward registration, if any: window from 2026-10-30, length
  = (3 / SR_VAL)^2 / events per year.
