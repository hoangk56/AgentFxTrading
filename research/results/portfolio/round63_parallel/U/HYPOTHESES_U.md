# Stream U hypotheses: scheduled token unlocks as a dated supply shock (Binance USDT-M perps, BTC-hedged)

Written 2026-10-31 15:50 UTC (from `date -u`), before any price, funding or return of an event coin was loaded.
Only the unlock schedule (DefiLlama emissions dataset) and the first-kline date of each perp file were read so far.

## Mechanism
A vesting cliff releases a known number of tokens on a known date to holders who received them at a low cost basis
(team, seed / private investors, foundation / ecosystem treasuries). Some of them sell, and market makers / funds
that know the calendar pre-hedge by shorting the perp. Two predictions with a fixed side:
- pre-event drift: the coin underperforms BTC in the days before the unlock (hedgers and front-runners), the
  window most cited by practitioners (Keyrock 2024 "token unlocks" note: most of the decline happens before the date);
- post-event drift: recipients sell for a few days after tokens land.
Side is fixed: **short the coin perp, long BTCUSDT perp at equal notional**. This is the crypto analogue of C3: a
public calendar predicts the side and rough size of a forced flow. Against it: the calendar is public and widely
tracked (TokenUnlocks, DefiLlama), shorting known unlocks is a crowded trade, so funding on the short leg may be
negative (shorts pay) and squeezes are likely when everyone is short into the date.

## Data
- Schedule: DefiLlama emissions, served keyless by `defillama-datasets.llama.fi` (index `emissionsIndex`, per
  protocol `emissions/<slug>` with `documentedData` = schedule from the project's documents). `api.llama.fi/emissions`
  returns HTTP 402 (paid plan), so that endpoint is not used. The per-protocol data are produced by the open-source
  repo DefiLlama/emissions-adapters (adapters written from token-launch documents). Snapshot pulled 2026-10-31; see
  research/data/token_unlocks/requests.log.
- Look-ahead risk: the snapshot is today's schedule. If a project delayed or resized a cliff, the adapter may show the
  realised (revised) date / size, not the one known ex ante. Mitigation: only cliff allocations (one-day releases)
  count; I spot-check large events against launch-document dates I know (APT, ARB, OP, SUI, DYDX, APE, IMX) and report
  the risk. Survivorship: only protocols DefiLlama still tracks are in the index; dropped tokens are missing.
- Prices / funding: research/data/binance/perp_1d (closes cut at ts < 2025-01-01 at load), funding/ and
  funding_window/; missing funding for an event coin is pulled from fapi.binance.com/fapi/v1/fundingRate with
  endTime 2024-12-31 23:59:59 UTC into research/data/token_unlocks/funding/.
- Mapping protocol -> perp by the token symbol in the index; a match is dropped if the perp's first kline is earlier
  than the token's first scheduled event minus 3 days (symbol collision with an older coin).

## Event definition (fixed)
- For each protocol, day d = UTC day of an `unlockEvents` timestamp. Cliff tokens on d = sum of `cliffAllocations`
  amounts on d (all categories except `burned`; farming / staking emissions are linear, so they are not cliffs).
  Events of one coin within 3 days are merged onto the first day.
- Size s = cliff tokens / circulating supply just before d, circulating = sum of `documentedData` unlocked over all
  labels on day d-1 (DefiLlama's own schedule, so numerator and denominator come from one source).
- Exclusions: the token's first event (TGE, circulating ~0); events with d - 30 < first perp kline (perp listed less
  than 30 days before the entry, to keep round 60's listing effect out); for one coin, an event whose entry falls
  before the previous traded event's exit; any event whose exit day is >= 2025-01-01.
- Event set: s >= X, **X in {1 %, 3 %}**.

## Trade (fixed side, small grid)
Daily closes are 00:00 UTC stamps; close index i = end of UTC day i. "t+0" = the last close before the unlock day
(end of d-1), t-k = end of d-1-k, t+k = end of d-1+k.
- Entry **t-7 or t-3**, exit **t+0 or t+3**: 4 windows x 2 sizes = **8 declared cells**.
- Short coin perp, long BTCUSDT perp, equal notional, fixed quantity (no rebalancing, squeezes show at full size).
- Costs per side: coin 0.05 % taker + 0.10 % half-spread = 0.15 %; BTC 0.05 % + 0.01 % = 0.06 %; funding on both legs
  from the stamps (the short receives positive funding, the long BTC pays it). Check at costs x1.5 and one day late
  (entry and exit both shifted +1 day).
- Excess over cash: the book holds margin only; the BTC-hedged pair is self-financing up to margin, so I report the
  return on one unit of short notional; the cash-rate drag is not charged (it is the same for any margin account).

## Statistics
- Per-event net return r; t clustered by ISO week of the unlock day (unlocks cluster on month starts, windows of
  different coins overlap); day-clustered t reported too. Years positive. Max-over-8-cells null: shuffle the sign? No:
  the side is fixed, so the null for the max cell is built from the random benchmark below.
- Random benchmark A (same coin, other dates): for each event, draw a random day of the same coin, inside the same era,
  with the perp live and no cliff >= 0.5 % within +-10 days; same window. Benchmark B (other coins, same date): random
  Binance perp alive >= 60 days on the event date with no cliff >= 0.5 % within +-10 days (coins with no schedule in the
  index count as no-event). 1000 resamples of the mean; report the percentile of the rule's mean for A and B, and the
  max-over-cells null (percentile of the best cell vs the distribution of the best of 8 random cells).
- Squeeze tails: share of events with adverse move (max coin close / entry - 1) > 30 % / 50 %, worst five events.
- Category split (diagnostic only, not a cell): events whose cliff is >= 50 % insiders + privateSale vs the rest.

## Eras
IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31 by unlock day. Most vesting calendars on Binance perps start in
2021-22, so IS is expected to be thin. If IS has fewer than 30 events at X = 1 %, I say so and use a fallback split
DISCOVERY 2021-01-01..2023-06-30 / VAL 2023-07-01..2024-12-31 (parameters picked on DISCOVERY only), noting that a
LIVE claim on that split needs the user's acceptance of a new-era split. HOLD (2025-01-01..) is never loaded.

## Bars (brief, unchanged)
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years positive, beats >= 95 % random, HOLD power at VAL size >= 3.
DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random. Both also need net > 0 at costs x1.5 and one day late.

## Power arithmetic
Filled in below from event counts (schedule only, no prices) before any return is computed.

### Event counts and power (appended 2026-10-31 15:54 UTC, schedule only, still no prices loaded)
117 protocols pulled, mapped to 116 perps (IOTA dropped: perp older than its schedule = symbol collision). Events
after the exclusions (TGE, perp listed >= 30 days before entry), before the per-coin no-overlap rule:

| X | IS 2020-21 | VAL 2022-24 (by year) | DISCOVERY 2021-01..2023-06 | VAL2 2023-07..2024-12 |
|---|---|---|---|---|
| 1 % | 33 events, 10 coins (2020: 7, 2021: 26; 13 are COMP) | 427, 45 coins (69 / 131 / 227) | 145, 24 coins | 308 |
| 3 % | 23, 10 coins | 225, 35 coins (36 / 67 / 122) | 86 | 161 |

Data quality seen in the list (schedule only): for old coins the documented circulating supply misses early supply,
so sizes can be absurd (SOL 2021-01-07 "1321 %", AVAX 2021-01-23 "334 %"). Some sizes > 100 % are real (PYTH
2024-05-19 ~142 %, ARB 2024-03-16 ~77 %). The rule only uses s >= X, so an inflated size matters only near the
threshold; I keep the declared definition unchanged.

Power: VAL runs ~140 events / year at X = 1 % (227 in 2024), ~75 / year at 3 %. HOLD 1.8 years at the 2024 rate
~400 events (1 %) / ~220 (3 %); events cluster by week, so the effective count is lower (say ~half). HOLD power 3
needs net per-event Sharpe >= 3 / sqrt(400) = 0.15 (1 %) or 0.20 (3 %); with effective n halved, 0.21 / 0.29. A
7-10-day coin-minus-BTC return has an sd of roughly 12-15 %, so LIVE needs a net mean of about 2-4 % per event.
The binding bar is IS: 33 events, 10 coins (t >= 2.5 needs per-event SR >= ~0.45 even before clustering), so a LIVE
verdict on the primary split is unlikely unless the effect is large; DEMO (IS t >= 2.0) needs SR >= ~0.35.
IS has >= 30 events at X = 1 %, so the declared primary split IS / VAL stands. I also report the fallback DISCOVERY /
VAL2 split as a sensitivity (declared now, before prices); a verdict on it would need the user's acceptance of a
new-era split.
