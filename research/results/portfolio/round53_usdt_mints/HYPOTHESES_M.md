# Round 53, stream M: hypotheses (USDT mints / burns -> BTCUSD, ETHUSD at minutes)

Written 2026-10-30 09:49-09:55 UTC (`date -u` 09:49:29 at the start), **before any return was computed**. Brief:
[BRIEF.md](BRIEF.md); general rules round37_forced_flows/BRIEF.md; Z1 design round52_lit_census/CENSUS_Z.md.
What had been computed when this was written: event counts per year, IC bar coverage at the entry minute and the IC
spread at the entry bar (costs, not returns). No price change of any kind has been computed or printed.

## Mechanism and source
Tether mints USDT when exchanges / OTC desks bring fiat; fresh USDT reaching exchanges is buying power for crypto.
Saggu 2022 (Finance Research Letters 49:103096, "The intraday bitcoin response to tether minting and burning events:
asymmetry, investor sentiment, and 'whale alerts' on Twitter"): BTC +24 to +68 bp within 5-30 minutes of a mint,
2014-21, faded by 60 minutes; burns no significant effect. Side (long after mints) and horizons from the paper. I do
not know a "treasury refill" exclusion rule from the paper's text (no full text here), so **none is applied**; the
on-chain data cannot tell an "authorized but not issued" inventory mint from an exchange-driven one anyway. The size
tier >= $100M is declared as a secondary cell (large mints are the "whale alert" events).

## Data (pulled before this file; HOLD cut at parse)
- Tron USDT-TRC20 `Issue` / `Redeem` events (TronGrid, pulled in round 52 Z), 2019-04..2024-12.
- Omni USDT (property 31) `Grant` / `Revoke` transactions: api.omniexplorer.info `/v1/properties/gethistory/31`,
  10 POST pages 2026-10-30 09:47-09:48 UTC, all HTTP 200 (api host serves no robots.txt, an HTML docs page instead;
  www.omniexplorer.info robots: `*` Allow / except /search). Cut blocktime < 2025-01-01 at parse. 92 grants total in
  the listing (2014-19), 5 revokes.
- No Ethereum mints (no log scans this round).
- IC M1 BTCUSD (2017-08-28..), ETHUSD (2017-09-25..), cut ts < 1735689600000 at load.

## Event filter (declared)
- Mint = Tron `Issue` or Omni `Grant` with amount >= 10,000,000 USDT (drops test / dust mints). Burn = Tron `Redeem`
  or Omni `Revoke` >= 10M.
- Clustering: events sorted across both chains; a qualifying event within 60 minutes of the previous qualifying event
  of the same kind joins its cluster (chained). Trade only the first event of each cluster, at its block timestamp.
- Secondary size tier: cluster first event >= 100,000,000 USDT (mint only).
- Entry: the close of the first IC M1 bar whose start is >= ceil_minute(block time) + 1 minute (so the fill is at
  >= block + 2 minutes, the detection minute plus the +1 minute rule), long at the ask (short at the bid for burns).
  If that bar starts more than 10 minutes after the block, IC is closed: the event is dropped and counted.
- Exit: the close of the last bar starting <= entry bar start + h, h in {5, 15, 30, 60} minutes, at the bid (long);
  dropped if that bar starts earlier than entry + h - 5 minutes.
- One trade per cluster per cell; holds never overlap within a cell (clusters are >= 60 min apart, holds <= 60 min).

## Counts before returns (IC-covered clusters, mint >= $10M)
| year | clusters | before IC BTC start | IC-covered | dropped: no IC bar (weekend) | IC full spread at entry, median bp |
|---|---|---|---|---|---|
| 2017 | 50 | 18 | 25 | 7 | 28.5 |
| 2018 | 12 | 0 | 10 | 2 | 41.2 |
| 2019 | 29 | 0 | 21 | 8 | 7.4 |
| 2020 | 57 | 0 | 43 | 14 | 4.2 |
| 2021 | 51 | 0 | 38 | 13 | 7.1 |
| 2022 | 11 | 0 | 11 | 0 | 4.1 |
| 2023 | 16 | 0 | 14 | 2 | 3.1 |
| 2024 | 16 | 0 | 16 | 0 | 2.8 |

IS (2017-08..2021) 137 trades, VAL (2022-24) 41. Weekend drops: 46 of 224 post-IC-start clusters (all on weekend
closures; none from weekday gaps). Mint >= $100M: IS 81, VAL 41. Burns >= $10M: IS 21, VAL 8.

## Cells (declared: 20)
- Primary family: mint >= $10M -> long, {BTCUSD, ETHUSD} x h {5, 15, 30, 60} = 8 cells. **Headline cell: BTCUSD 30
  min** (the paper's window end before the fade).
- Size tier: mint >= $100M -> long, {BTCUSD, ETHUSD} x 4 h = 8 cells.
- Mirror: burn >= $10M -> short, BTCUSD x 4 h = 4 cells (paper: no effect; expectation 0 before cost).
- Total 20 cells; the chance benchmark is over all 20.

## Costs and statistics
- Net = (exit bid - entry ask) / entry mid for longs (mirror for shorts), i.e. the actual IC spread at both bars;
  swap if the hold crosses the 17:00 New York rollover: BTC long -38.61 USD / unit / rollover, ETH long -1.135
  (research/specs.py SWAPS, triple Wednesday), shorts 0. Mid = (bid + ask) / 2.
- Robustness: spread x1.5 (both legs), +1 minute (entry and exit one bar later), ex-2020-03/04, by year.
- Eras: IS = first IC-covered event (2017-08-28) .. 2021-12-31; also IS-core 2019-21 (Tron era, IC cost < 10 bp)
  reported separately because 2017-18 IC spreads are 28-41 bp. VAL 2022-01-01..2024-12-31.
- t: clustered by UTC entry day (day sums), per-trade Sharpe = mean / sd.
- Control A (random entries, 300 seeds): for each event, a random minute within +-90 days, same weekday, same UTC
  hour, IC open, no mint / burn within +-6 h, and prior-60-minute BTC mid return among the 30 nearest candidates to
  the event's own prior-60 return. Same entry / exit / cost code. Report the cell's percentile among seed means.
- Control B (no-mint placebo): for each event, the 30 minutes (anywhere in the same era, IC open, no mint / burn
  within +-6 h) whose prior-60-minute BTC return is nearest the event's; placebo mean forward net per event. Event
  minus placebo = the excess the mint adds over "BTC rose that much in the prior hour".
- Chance benchmark: for each Control A seed compute all 20 cells' IS t on the random entries; the 95th percentile
  of the max over cells is the best-of-20 bar.
- Bars (PROMPT.md): LIVE = IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, beats >= 95 % random, HOLD power >= 3.
  DEMO = IS t >= 2.0, VAL net > 0, beats >= 90 % random. Both net, robust to x1.5 and +1 min.

## Power arithmetic (before returns)
- HOLD (2025-01..2026-09-24, 1.73 y) at the 2023-24 Tron rate (15 / y, weekends now open on IC): ~26-28 mints >= $10M.
  LIVE power 3 needs VAL net Sharpe >= 3 / sqrt(27) = **0.58 per trade**. At a 30-min BTC sd of ~35-50 bp that is
  ~20-29 bp net per trade, ~24-32 bp gross at ~3-4 bp cost. Only the paper's full size would reach it.
- IS t >= 2.5 with 137 trades needs Sharpe >= 0.21 (~10 bp net at ~50 bp sd); IS-core 2019-21 (102) needs 0.25.
- VAL t >= 1.5 with 41 trades needs Sharpe >= 0.23.
- DEMO is reachable at a third of the paper's size if it survives cost in IS.
- Expected (round 52 Z): LIVE ~1-1.5 %, DEMO ~5 %.

## Not done (declared)
- Binance / 24/7 mid diagnostic for weekend events: skipped for time (would only be a mid diagnostic, never net).
- Ethereum mints: not pulled (rule of the round); their value is priced in STREAM_M.md from the Tron result.
