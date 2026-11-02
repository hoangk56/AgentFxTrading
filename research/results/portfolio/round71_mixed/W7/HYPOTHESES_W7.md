# Stream W7 (round 71) hypotheses: withdrawal-closed window of new Binance spot listings

Written Sun Nov 1 18:30:03 UTC 2026 (from `date -u`), before any price file (aggTrades, dumps, klines with prices)
was downloaded and before any return was computed. Only metadata was requested so far (first-day probes of monthly 1d
kline files, used for listing days only; Bybit directory listings; robots.txt), 1,804 lines in
research/data/listing_window/requests.log. HOLD (2025-01-01..) is never requested: every requested day is <= 2024-12-31
and every series is cut at ts < 2025-01-01.

Source: IB7 in round71_mixed/IB/STREAM_IB.md. Disclosed: X (round 64) found that a cross-venue Binance-spot discount
hedged with the Binance perp loses the cost wall, because the whole Binance complex was cheap; N0 (round 66) found
that big early moves of new perps continue. This test differs: it conditions on the spot-vs-perp gap inside the
withdrawal-closed first day of a new coin, and exits on the withdrawal clock.

## Mechanism (side fixed before data)
Binance opens deposits before spot trading and withdrawals usually 24 h after trading starts. During that day a
Binance spot discount to the coin's perp cannot be arbitraged out (buy Binance spot, withdraw, sell elsewhere is shut),
while Launchpool / airdrop supply credited on Binance can only be sold there. When withdrawals open, the route opens
and the discount should close. Side: **long Binance spot (no borrow), short the reference perp**, exit at the
withdrawal clock. The premium side is not traded (it would need borrow, and the inward route caps it anyway).

## Events (code/meta.py -> research/data/listing_window/meta/events_meta.csv; metadata only)
- Universe: Binance spot `<COIN>USDT` pairs whose first 1d kline is 2020-01-01..2024-12-30. Source: spot_first.csv
  (474 pairs of coins that ever had a USDT-M perp), plus the other data.binance.vision USDT symbols of coins with a
  Bybit linear perp (first day from data.binance.vision monthly 1d files).
  - Note: spot_first.csv only holds coins with a Binance perp (ever), so IB7's 77 / 82 / 31 / 41 / 56 is that subset.
    Coins with neither a Binance nor a Bybit perp are irrelevant here (no hedge).
- Dropped: stablecoins / leveraged tokens (2). Renames / swaps of coins already trading (13: EGLD, AAVE, STRAX, XEC,
  BTTC, T, MULTI, LUNC, USTC, BEAMX, G, RENDER, POL). The list was corrected at ~18:29 UTC after I saw the excluded
  names only, before any price: ANT, GTC, ALPACA, WAXP, VIDT, QI, REI, PROM, ID, NEIRO, 1000SATS and others were new
  listings, so they now go through the older-pair filter.
- New-coin filter: drop the pair if any other quote pair of the base (BTC, BNB, BUSD, ETH, TRY, EUR, FDUSD, ...)
  traded on an earlier day. Withdrawals were already open for those coins. Dropped: 27 / 18 / 4 / 13 / 0 (2020..2024).
- New coins: 49 / 69 / 26 / 30 / 56. With a reference perp on or before the listing day (day resolution):

| year | Binance perp on/before day | Bybit perp only | no hedge | hedgeable |
|---|---|---|---|---|
| 2020 | 1 | 0 | 48 | 1 |
| 2021 | 2 | 2 | 65 | 4 |
| 2022 | 3 | 2 | 21 | 5 |
| 2023 | 13 | 3 | 14 | 16 |
| 2024 | 46 | 4 | 6 | 50 |

- **IS (2020-21) has at most 5 hedgeable events, VAL (2022-24) at most 71.** Many Binance perps launch on the spot day
  itself, so the count with a perp live at the signal time will be lower; a Bybit perp is the fallback.
- Expected outcome stated now: with n <= 5 in IS, the LIVE bar (IS t >= 2.5) and even the DEMO bar (IS t >= 2.0) are
  very unlikely to be met even if the effect is real. I will not invent a new split. A failure on IS size is reported
  as a failure.

## Clocks
- Listing clock L0 = the first spot aggTrade of the pair, floored to the minute. Binance announces round times; the
  first print can come seconds later.
- **Withdrawal clock W = L0 + 24 h (approximation; IB7).** Sensitivity (information, not graded):
  1. Exit at W - 4 h and W + 4 h.
  2. Drop ARB (2023-03-23), a known exception per IB's search. OSMO is not in the event list.

## Reference perp and signal
- Reference at signal time S: the Binance USDT-M perp if its first trade is before S - 60 s and it printed in the 300 s
  before S. Otherwise the Bybit linear perp under the same test. Otherwise no trade.
  - Names map with 1000 / 1M prefixes. Price scale f = the power of 10 nearest to spot / perp.
- d = ln(mid_spot(S) / (f x mid_ref(S))), in bp.
  - mid = mean of the last taker-buy and last taker-sell prints, each <= 60 s old, strictly before S. Otherwise the
    last trade, if <= 300 s old.
  - |d| >= 2000 bp is treated as a data error and excluded (count reported).
- Reported for all hedgeable events: the distribution of d at L0 + 15 and L0 + 60 min (both signs), per era.

## Declared cells (8)
S in {L0 + 15 min, L0 + 60 min} x k in {50, 100} bp x exit X in {W + 0, W + 30 min}. Trade if d <= -k. One trade per
event per cell.
- Entry (aggTrades only):
  - Spot: buy at the first taker-buy aggTrade in a second >= S.
  - Perp: sell at the first taker-sell print in a second >= S.
- Exit: spot sell at the first taker-sell print >= W + X; perp cover at the first taker-buy print >= W + X.
- A leg with no print of the needed side within 300 s means the trade is skipped (count reported). Fills at
  taker-side prints already pay the half-spread.
- Legs reported separately: spot leg = Sx / Se - 1, hedge leg = -(Px / Pe - 1); funding; fees.

## Costs
- Fees: spot taker 10 bp a side. Binance USDT-M taker 5 bp a side. Bybit linear taker 7.5 bp a side before 2023-02-17,
  5.5 bp after. Round trip: 30 bp (Binance hedge), 35 / 31 bp (Bybit hedge).
- Half-spread: inside the taker-side fills. It is also measured (information) as (mean taker-buy - mean taker-sell) / 2
  in the 10 s from each fill time, per leg.
- Funding on the short perp: the real stamps in (entry, exit], from local binance/funding, funding_window,
  bybit/funding and bybit_basis/funding. Missing series are pulled from fapi /fapi/v1/fundingRate or Bybit v5
  /v5/market/funding/history with endTime <= 2024-12-31.
- Capital: Fed funds (DFF) x hold time x 1.5 notional (spot plus 50 % perp margin), so the result is excess over cash.
- Checks:
  - Costs x1.5: 1.5 x fees + 0.5 x the measured half-spreads of the 4 fills.
  - One step late: entry 60 s after S, with the signal unchanged.

## Statistics, random benchmark, bars
- Net bp per trade. t clustered by entry UTC day. SR = mean / sd per trade. Years positive.
- Random benchmark: same coin, same reference, a random entry second uniform in [L0 + 15 min, L0 + 23 h]
  (unconditional), with the same exit, fills and costs. 400 draws per event; 1,000 sets with the cell's event count;
  random % = share of sets with a mean below the real mean. Max-over-8-cells null of t from the same draws (IS and
  VAL).
- Parameters are picked on IS (the best IS t among the 8 cells) and checked on VAL unchanged. Bars as in BRIEF.md:
  - LIVE: IS t >= 2.5; VAL t >= 1.5; >= 2/3 of years positive; random >= 95 %; HOLD power at VAL size >= 3.
  - DEMO: IS t >= 2.0; VAL net > 0; random >= 90 %.
  - Both also need net > 0 in IS and VAL, at costs x1.5 and one step late.
- Placebo with the lock open (same rule 7 days later): only if a cell passes the IS bars (otherwise not pulled).

## Power (arithmetic before data)
- HOLD n = VAL n / 3 x 1.83. Power = SR x sqrt(HOLD n).
  - If all 71 VAL events traded: HOLD n ~ 43, so power 3 needs SR >= 0.46.
  - At a VAL cell size of 20: HOLD n ~ 12, so SR >= 0.86 is needed.
  - At 2024's pace (50 a year, ~90 in HOLD), SR 0.32 would do. The brief fixes VAL size, though.
- IS: with n = 5, clustered t >= 2.5 needs SR >= ~1.1 per trade.

## Data plan (no subsample; all 76 day-level candidates)
- Spot: data.binance.vision spot daily aggTrades, listing day + next day (+ day 3 if L0 >= 23:00 UTC).
- Perps: the Binance futures/um daily aggTrades and the public.bybit.com/trading dumps for the same days.
- Storage: compact 1 s series (last, first / last taker-buy and taker-sell price, taker notionals) in
  research/data/listing_window/npz/. Zips / gz are deleted after parsing (`python -I`).
- About 400 files, expected well under 45 min. 2 pull processes at most. >= 0.27 s per host (0.5 s Bybit). Back off
  on 418 / 429 / 503; 403 = stop.
- Note: the S3 listing host's robots.txt answered 403 at 18:18 UTC (root of a bucket host). Under the 403 rule, that
  host is not used; all metadata came from data.binance.vision file probes instead.
