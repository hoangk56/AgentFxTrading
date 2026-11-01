# Round 63, stream P: hypotheses (declared before any price was pulled)

Written 2026-10-31 16:20 UTC (from `date -u`). Stream P = I1 + I2 of `../I/IDEAS_I.md`.

What I had seen before writing this file: Polymarket's fee page, the geoblock page, one gamma market record (field
names), and the gamma **metadata** of every closed market with `endDate` 2022-11-01..2024-12-31 (pulled 16:08-16:17
UTC, 185 pages, `research/data/polymarket/raw_gamma/`). The metadata holds the final outcome (`outcomePrices`), but I
only printed counts (market / event counts by year, volume bucket and tag category, and the `closedTime - endDate` lag
distribution). No price history was requested and no outcome was tabulated. No 2025-26 data: markets with
`closedTime >= 2025-01-01` are dropped at load.

## HOLD contamination (say it first)
The papers behind I1 / I2 (Cardozo & Rivero-Wildemauwe 2026; Bürgi, Deng & Whelan; Qiu & Qiu 2026) use mostly
2024-26 Polymarket / Kalshi data. A 2025-26 HOLD is therefore **not blind** for this family. Any PREREG_DRAFT from this
stream proposes a **forward log on markets listed after 2026-10-31** as the deciding test, not HOLD.

## Universe (fixed)
- Polymarket CLOB markets (`enableOrderBook` true), exactly 2 tokens (binary), lifetime `volumeNum` >= 1,000 USDC
  (robustness, not selection: >= 10,000). Lifetime volume is known only ex post: a mild survivorship filter, stated.
- E = scheduled end (`endDate`, fixed at listing; it can be edited later, a pitfall). C = `closedTime` (resolution).
- Era by C: IS = 2023, VAL = 2024. 2022-11/12 (17 events) reported as PRE info only. Counts at the 1k filter:
  IS 1,181 markets / 791 events, VAL 12,657 markets / 5,161 events (`events[0].id` = parent event).
- Payout = final `outcomePrices` (1 / 0; 0.5 / 0.5 split counted as 0.5). Markets with other finals are dropped and
  counted.
- Category from gamma tags: sports > crypto > politics > other > untagged (2023 is ~75 % untagged). Primary = all
  categories pooled; per-category tables are reported, never used to select.

## Prices
- CLOB `prices-history`, token 0 (first outcome), hourly (`fidelity=60`), windows ending at
  min(C, E + 4 d, 2024-12-31 23:59:59). Token 1 price = 1 - p0 (assumption; check on a subsample by pulling token 1).
- Price at time t = the last point with timestamp <= t and >= t - 6 h; else no trade. Entry needs t < C - 1 h.
- I do not know yet whether the series is the midpoint or the last trade; I will say what the data suggests.

## Rules
### P1: favourite-longshot bias, hold to resolution
- Entry t = E - T, T in {7 d, 1 d}. Favourite = token with price p in [thr, 0.98], thr in {0.80, 0.90}.
- Sides as separate declared rules (a partition in a binary market):
  - P1-all: buy the favourite, whichever token it is (primary).
  - P1-Y: the favourite is token 0 (the named / "Yes" outcome).
  - P1-N: the favourite is token 1 ("No"), i.e. **selling the longshot "Yes"** (the mirror rule).
- Grid 2 thr x 2 T x 3 sides = 12 cells. **Declared primary cell: P1-all, thr 0.90, T 1 d** (the scout's).
  Max-over-cells null reported.
### P2: settlement window (outcome already public), hold to payout
- P2a: entry t = E + L, L in {1 h, 12 h}, market still open (C > t + 1 h); buy the leading token if p in
  [0.90, 0.99). Primary cell: L 1 h.
- P2b: first hour tau in [E - 7 d, min(C, E + 4 d)) where a token prints >= 0.95; enter at tau + 1 h if that token is
  in [0.95, 0.99). (Scout's "decided by a price jump" variant.)
- 3 cells. Graded on **excess over the cash rate**: DFF (research/data/rates/DFF.csv) x days from entry to C / 360.

## Returns and costs
- Per $ staked: r = payout / (p + h) - 1 - f, then minus cash for the days held (P1 and P2 both).
- h (half spread paid, from mid / last): 1.0c for p < 0.96, 0.5c for p >= 0.96 (tick 0.01 / 0.001). Stress x1.5 and
  x2. If trade prints suggest larger spreads near resolution I will say so and re-cost.
- Fee: 0 (2023-24 CLOB markets: `feesEnabled` false for every market in the table; the AMM `fee` field is not the
  CLOB). Today's schedule (taker 0.03-0.07 x p(1-p) per share, geopolitics 0, makers 0) is reported as the forward
  cost: at p 0.9, rate 0.04 gives 0.36c / share = 0.40 % per $.
- Friction f: 0.05 % per trade (USDC on / off ramp ~$0.5 amortised on a $1,000 ticket; Polygon gas is paid by the
  relayer).
- One step late: P1 entry at E - T + 1 h; P2a at E + L + 1 h; P2b at tau + 2 h.

## Statistics
- Unit = parent event: each (event, cell) return is the equal-weight mean of its qualifying markets. t is clustered by
  the resolution day (UTC date of the event's latest C). Years = 2023, 2024 (plus quarters as info).
- Random benchmarks (2,000 draws each): R1 same markets and timing, random token (coin flip); R2 same timing on random
  eligible markets of the same category and era, random token, same number of events. Report the % of draws the rule
  beats. Also the analytic null (excess = 0).
- Costs x1.5, one step late, by category, by price band, without the 2024 US election event cluster.

## Power arithmetic (before building)
LIVE needs per-trade (per-event) net Sharpe at VAL size x sqrt(n forward events) >= 3, and t >= 2.5 IS.
- P1, p ~ 0.9: sd per $ ~ 0.30 (0.23 at p 0.95). Expect ~50 % of events to qualify: IS ~400 events, VAL ~2,500.
  t_IS ~ (e / 0.30) x sqrt(400) = 67 e. **IS t >= 2.5 needs a net edge e >= 3.8c per $; DEMO (t >= 2) e >= 3.0c.**
  The literature's +0.83c gross would give IS t ~ 0.6 and VAL t ~ 1.4. So P1 reaches the bars only if 2023 was much
  more biased than 2024-26. Forward: 2025-26 Polymarket lists roughly 10x the 2024 count; at ~15k independent
  events / 21 months, forward power at e = 0.83c is 0.028 x sqrt(15,000) ~ 3.4 (marginal).
- P2: if the outcome is public, q ~ 0.995+; at p 0.97 the return is ~ +3 % with sd set by reversals / misresolution
  (~ 7 % sd at 0.5 % reversal at -100 %): Sharpe ~ 0.4 per event, so ~60 events suffice for t 3. IS has maybe
  ~200-300 qualifying events. **P2 can reach every bar on paper; the risk is that the quoted mid hides an ask at 0.99+
  (then cost eats it) and that reversals cluster.**
- Prior: P1 LIVE ~3 %, DEMO ~8 %; P2 LIVE ~2.5 %, DEMO ~6 % (scout's).

## Vietnam residency (information)
Polymarket's geoblock page (docs.polymarket.com/api-reference/geoblock, read 2026-10-31) does not list Vietnam among
blocked or close-only countries. Vietnamese law bans unlicensed online gambling, and the legal status of prediction
markets and unlicensed crypto venues is unclear. That is a user decision, not a reason to skip.

## Addendum A (2026-10-31 16:30 UTC, `date -u`): Kalshi replication of P1, declared before any Kalshi price
Probes (3 requests, 16:2x UTC): `api.elections.kalshi.com/trade-api/v2/historical/markets?event_ticker=INXD-23DEC29`
returns the 2023 bracket markets with results, and `/historical/markets/{ticker}/candlesticks?period_interval=60`
returns hourly **yes_bid / yes_ask** candles for 2023. So Kalshi gives real quotes (no mid assumption).
- Series: INXD (S&P 500 daily close brackets) and HIGHNY (NYC daily high temperature brackets). Events with close
  time in 2023 (IS) / 2024 (VAL); markets with close >= 2025-01-01 are dropped at load, never printed.
- Sample: up to 150 events per series per era, seeded (random.Random(63)), to keep the pull < 30 min.
- K1: at entry t = close_time - T, T in {6 h, 24 h}, for every bracket take the last hourly candle ending <= t
  (yes_bid close, yes_ask close). Buy YES at yes_ask if yes_ask in [thr, 0.98], else buy NO at 1 - yes_bid if that is
  in [thr, 0.98]; thr in {0.80, 0.90}. Event return = mean over its qualifying brackets. 4 cells; primary
  thr 0.90, T 6 h.
- Costs: the ask is paid (spread included), plus the taker fee 0.07 x p x (1 - p) per contract (stress x1.5), minus
  DFF for the hold. Same statistics as P1 (clustered t by close day, calibration null at the paid price).
- Change at 16:40 UTC, before any Kalshi price was read: INXD events have ~30-40 brackets each, so the INXD sample is
  cut to 30 events per era (first 30 of the same seeded day order); HIGHNY stays at 150. Kalshi returned 429 at
  4 req/s, so the pull runs at 2 req/s, one thread.
