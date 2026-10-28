# Round 33, stream K: hypotheses (crypto cross-venue premiums and margin funding -> BTCUSD / ETHUSD at IC)

Written 2026-10-27 19:09-19:10 UTC (`date -u` 19:09:11 at the start, file saved before 19:10:10), **before any return was computed or any signal
was joined to a price at IC**. Loaded so far: nothing but the raw downloads below (still running for Coinbase and
Upbit), the ECB reference-rate file cut at 2024-12-31, and round 31 C's IC coverage / spread / sd numbers (no signal).

## What is not mine (round 31 C, HYPOTHESES_C.md 18:22 UTC)
Round 31 C already declared Bitfinex margin **position sizes** (stats1 pos.size long / short: crowding ratio B1,
24-h build-ups B2, 4-h B3), Bitfinex liquidations, Binance futures positioning ratios and CoinMetrics exchange flows,
and it is pulling the pos.size history now. STREAM_C.md does not exist yet. To avoid a duplicate I do **not** test
pos.size in any form. From the Bitfinex margin book I take only the **margin funding rate** (the price of borrowing
USD to go long, BTC / ETH to go short), which C did not declare. It is close in spirit to perp funding (rounds 4 / 9,
failed), so its prior is low; it is a different venue and instrument (peer-to-peer margin lending, not a perp).

## Sources, depth and the bar each can meet
| series | source | depth (to 2024-12-31) | eras | best bar |
|---|---|---|---|---|
| Coinbase Exchange BTC-USD, ETH-USD hourly candles (time = bucket start, close = last trade in the hour) | api.exchange.coinbase.com/products/{p}/candles?granularity=3600 (public, no key) | BTC from 2015-07-20 (2015-01 returns empty), ETH from 2016-05-18 | with Binance: 2017-08-17.. | LIVE possible on a 4.3-year IS (2017-09..2021-12); no PRE (Binance starts 2017-08) |
| Binance spot BTCUSDT, ETHUSDT 1h klines (open time = bucket start, close = last trade) | data.binance.vision/data/spot/monthly/klines/{SYM}/1h/ | 2017-08-17.. | as above | as above |
| Upbit KRW-BTC, KRW-ETH hourly candles (candle_date_time_utc = bucket start, trade_price = last trade) | api.upbit.com/v1/candles/minutes/60 (public quotation API, no key) | first candle ~2017-09-25 (exchange beta), real volume from 2017-10-24 | IS 2017-10..2021-12 (4.2 y) | LIVE possible on the short IS, no PRE |
| USD/KRW | ECB euro reference rates (www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip): USDKRW = KRW / USD columns, both "as of 14:15 CET" (concertation), published ~16:00 CET on TARGET days | 1999.. | - | - (Bank of Korea ECOS needs a key: not used) |
| Bitfinex margin funding rates fUSD, fBTC, fETH, hourly candles of the aggregated 2-30 day book (trade:1h:fXXX:a30:p2:p30, close = last funding trade in the hour, daily rate in decimal) | api-pub.bitfinex.com/v2/candles | fUSD / fBTC from 2016-08-01, fETH to check | IS 2017-09..2021 at IC | LIVE possible |
| Bitfinex tUSTUSD (USDT priced in USD), hourly | api-pub.bitfinex.com/v2/candles | 2018-11-27.. | from 2018-12 | used only for the USDT-adjusted variant (information) |

Unusable / not fetched: GBTC premium (the SMU 2023 working paper https://ink.library.smu.edu.sg/lkcsb_research/7447
names the Grayscale premium the strongest BTC daily predictor) needs GBTC share prices: stooq.com robots.txt disallows
all agents and answers a JavaScript challenge, Yahoo was unreachable in round 9: user decision (data source). Bithumb /
Korbit history (pre-2017 kimchi premium) has no public deep history API: not fetched.

## Timestamp rules (same-timestamp legs, FX time, publication lags)
- **Coinbase premium (CBP).** For hour bucket [h, h+1h): `cbp_h = ln(CB_close_h / BN_close_h)`, both = last trade
  before h+1h on each venue. Known at h+1h. Hours missing on either venue: no value (never forward-filled). Raw
  definition (Coinbase USD vs Binance USDT) is the practitioner's (CryptoQuant "Coinbase Premium Index") and is the
  primary. Information variant from 2018-12: `cbp_adj_h = cbp_h - ln(USTUSD_close_h)` (Bitfinex, same hour).
- **Daily CBP** for UTC day D: mean of the available hourly cbp over D's 24 hours (>= 18 hours present, else none).
  Known at D+1 00:00 UTC.
- **Kimchi premium (KP)**, Korea vs the US venue (no USDT leg): `kp_h = ln(UP_close_h / (CB_close_h x USDKRW))`.
  - **Daily KP (primary)** is measured at the ECB concertation: the hour bucket that ends at 14:00 CET (13:00 UTC in
    CET winter, 12:00 UTC in CEST summer), i.e. both crypto legs are the last trade before that instant, and the FX leg
    is the ECB rate of the same day D "as of 14:15 CET". Mismatch between the crypto and FX legs: 15 minutes, the same
    every day (KRW 15-min sd ~0.05 %, against premiums of 1-50 %). The value is public when the ECB publishes
    (~16:00 CET = 15:00 UTC winter / 14:00 UTC summer), so **daily KP rules enter at 16:00 UTC on D** (>= 1 h after
    publication in both seasons). Days without an ECB rate (TARGET holidays): no value, no trade.
  - **Hourly KP changes** (H6 only): `dkp_h = kp_h - kp_{h-4h}` with the **same** USDKRW (the latest rate published
    before h-4h) on both points, so the change contains no FX staleness beyond the intraday KRW move (sd ~0.2 % over
    4 h; noted as noise, not look-ahead). Known at h+1h.
- **Bitfinex funding.** Daily rate for UTC day D = volume-weighted mean of hourly closes (weight = hourly volume) over
  D, >= 12 hours with trades; known at D+1 00:00 UTC.
- No series is forward-filled across a gap; every z-score uses only values strictly before the signal time.

## Prices, costs, fills (identical to round 31 C, whose engine I copy)
- Returns: IC M1 BTCUSD / ETHUSD (`research.m1.load`), cut ts < 2025-01-01 at load. BTC from 2017-08-28, ETH from
  2017-09-25. IC crypto closed Fri 17:00 -> Sun 17:05 New York until 2024-04: a signal while IC is closed is skipped.
- Signal known at t -> entry at the IC price at t + 1 min (close of the bar labelled t), stale <= 10 min else no
  trade; exit at the last quote at or before the exit time (5 days max).
- Cost: half the actual IC spread at entry + half at exit; no commission; swap long -5.0 bp per 17:00 NY rollover
  (x3 Friday), short 0 (research/specs.py SWAPS: BTC long -38.61 USD/unit, ETH -1.135, short 0, ~5 bp a night as in
  round 23 N / 31 C; the fraction is not computed from 2025-26 prices). Checks: entry and exit +1 min; half spreads x1.5;
  short swap also -5 bp.
- One open trade per cell and symbol (non-overlapping, greedy). t clustered by UTC entry day.
- Random control: 200 seeds, same count per era, same hold, entries at random IC-open times on the rule's clock
  (00:00 UTC weekdays for CBP daily, 16:00 UTC weekdays for KP daily, any IC hour boundary for hourly rules), side =
  the rule's sign function without the threshold, evaluated at the random time. Percentile of the real mean net.
- Momentum control: OLS of the next-h return on the signal z with past 1, 7 and 28-day returns, IS and VAL (premiums
  co-move with price by Makarov & Schoar 2020, so a "premium" effect may be momentum).
- Eras: IS 2017-09 (BTC) / 2017-10 (KP) .. 2021-12; VAL 2022-01..2024-12. HOLD closed. No PRE exists for any of these
  series at IC; a mid-only PRE on Coinbase prices is impossible for CBP / KP because the second leg starts 2017.

## Power arithmetic (before building; LIVE = per-trade net Sharpe x sqrt(HOLD trades) >= 3, HOLD 1.73 y)
Unconditional IC mid sd (round 31 C, 08:00 UTC starts, IS 2018-21 / VAL 2022-24): BTC 4 h 191 / 95 bp, 1 d 454 / 297,
3 d 697 / 474, 5 d 861 / 652; ETH 1 d 547 / 373, 5 d 1144 / 829. IC median spread BTC 2017 30.5 bp -> 2024 2.4; ETH
2018-20 88-254 bp (ETH IS fails on cost by construction; ETH cells are counted, expected to fail).

| rule shape | trades / yr | HOLD n | Sharpe needed | net edge needed, BTC, VAL sd | IS sd |
|---|---|---|---|---|---|
| daily, 1-day hold, every weekday | 250 | 430 | 0.145 | 43 bp | 66 bp |
| daily threshold \|z\| > 1 (~30 % of days), 1 day | 75 | 130 | 0.26 | 78 bp | 120 bp |
| threshold \|z\| > 2 (~5 %), 3 days | ~15 | 26 | 0.59 | 280 bp | 410 bp |
| 5-day hold, non-overlapping | 50 | 87 | 0.32 | 209 bp | 276 bp |
| hourly events ~30 / yr, 4 h | 30 | 52 | 0.42 | 40 bp | 80 bp |

LIVE also needs IS t >= 2.5 on 4.3 years (no rescaling). What the sources imply: Makarov & Schoar 2020 (JFE 135)
show premiums co-move with returns contemporaneously (order flow), not a forecast; Eom 2021 (FRL) reads the kimchi
premium as speculative trading, a 2023 FRL re-examination finds that unstable; a practitioner study (CryptoSlate,
not peer reviewed) finds corr(KP level, forward return) ~ -0.06. At \|corr\| 0.06 a daily rule has Sharpe ~0.06 per
trade, power ~1.2: **the realistic target is DEMO**; LIVE would need an effect ~2.5x anything the sources report.

## Hypotheses (side fixed by mechanism or source; parameter grids fixed here; parameters chosen on IS only)

### Family CB: Coinbase premium = US institutional / fiat demand that continues (follow). 30 cells
- **CB1 daily level, follow.** z = (daily CBP_D - mean) / sd over D-30..D-1 (>= 20 days). z > k -> **long**, z < -k
  -> **short**, enter D+1 00:00 UTC (+1 min fill), hold h days. k in {1.0, 1.5, 2.0} x h in {1, 3, 5}: 9 per symbol
  (BTC: BTC-USD vs BTCUSDT; ETH: ETH-USD vs ETHUSDT), 18.
- **CB2 hourly spike, follow.** z of cbp_h vs the hourly values of the previous 30 days (>= 500). z > k -> **long**,
  z < -k -> **short**, enter at h+1h (+1 min), hold H. k in {2, 3} x H in {4 h, 24 h}: 4 per symbol, 8.
- **CB3 regime, follow.** Every weekday at 00:00 UTC, side = sign(mean daily CBP over D-6..D) (7-day mean): US
  buying -> long, selling -> short. Hold 1 day (every weekday) or 5 days (non-overlapping): 2 per symbol, 4.

### Family KP: Korean premium = retail frenzy (extreme high) or panic (extreme low) that reverts (contrarian). 26 cells
- **KP1 daily extreme, contrarian.** z = (KP_D - mean) / sd over the previous 90 daily values (>= 60). z > k ->
  **short**, z < -k -> **long**, enter 16:00 UTC D, hold h. k in {1.5, 2.0} x h in {1, 3, 5}: 6 per symbol, 12.
- **KP2 frenzy level, contrarian, one-sided.** KP_D above the 90th percentile of the previous 365 daily values (>= 250)
  -> **short**, enter 16:00 UTC D, hold h in {1, 3, 5}: 3 per symbol, 6.
- **KP3 hourly Korean bid surge, contrarian.** z of dkp_h (4-h change) vs the previous 30 days of hourly dkp (>= 500).
  z > k -> **short**, z < -k -> **long**, enter at h+1h, hold H. k in {2, 3} x H in {4 h, 24 h}: 4 per symbol, 8.

### Family FD: Bitfinex margin funding = price of leverage, crowded side gets unwound (contrarian). 16 cells
- **FD1 cost of long leverage.** z of the daily fUSD rate vs the previous 30 days. z > k -> **short** (expensive USD
  margin = crowded longs), z < -k -> **long**. Enter D+1 00:00 UTC. k in {1.5, 2.0} x h in {1, 3}: 4 per symbol
  (BTC, ETH), 8.
- **FD2 cost of short leverage.** z of the daily fBTC (for BTC) / fETH (for ETH) rate vs 30 days. z > k -> **long**
  (expensive coin borrowing = crowded shorts), z < -k -> **short**. Same grid: 4 per symbol, 8. If fETH starts after
  2018 or is too thin (< 12 traded hours a day on most days), ETH FD2 cells are reported as "no data" and still counted.

### Count and chance
72 registered cells (CB 30, KP 26, FD 16). Expected max \|t\| of 72 independent normals ~2.8 (95 % ~3.4); per family
CB 30 -> ~2.5, KP 26 -> ~2.5, FD 16 -> ~2.3. Cells are correlated (shared grids), so these are conservative.
Information only (not counted, no verdict): CB1 on the USDT-adjusted premium (2018-12..), contemporaneous correlation of
daily premium changes with same-day BTC returns (checks the Makarov-Schoar co-movement on our data).
Order of work: build the premium series and check them (coverage, levels by year, outliers), then CB, KP, FD.

## Data notes (added 2026-10-27 19:23 UTC, after building the series, before reading any return)
Full table: scratchpad r33/K/out/describe.txt. No rule or grid changed.
- Coverage to 2024-12-31: Coinbase BTC-USD 82,806 hours from 2015-07-20, ETH-USD 75,397 from 2016-05-18; Binance
  BTCUSDT / ETHUSDT 64,525 hours from 2017-08-17; Upbit KRW-BTC 63,608 / KRW-ETH 63,499 from 2017-09-25 (beta month
  thin); Bitfinex fUSD / fBTC / fETH hourly from 2016-08-01, tUSTUSD from 2018-11-27; ECB 6,658 days. Upbit KRW-USDT
  starts 2024-06 (VAL tail only, unused).
- Raw CBP is nearly identical for BTC and ETH every year (e.g. 2018 mean -35 / -38 bp, p5 -270 / -270): it is mostly
  the USDT / USD basis, not a coin-specific US bid. The CB1 / CB2 / CB3 ETH cells are therefore close copies of the BTC
  signal on a second target. Levels shrink by era: daily p5-p95 2017 -34..+473 bp, 2018 -265..+68, 2020 -15..+20,
  2022-24 about -13..+10 bp.
- The USDT-adjusted CBP (Bitfinex tUSTUSD) is -280 bp in Dec 2018 and -99 bp on average in 2019: Bitfinex's own USD
  traded at a discount then (withdrawal problems), so the adjustment is wrong before ~2020. The information variant is
  read from 2020 only.
- KP (BTC) by year: mean 2018 +3.6 %, 2019 +0.2, 2020 -0.5, 2021 +3.4, 2022 +1.4, 2023 +1.5, 2024 +2.4 %; p95 2017
  +24 %, 2018 +15 %, 2021 +11 %. The 90-value z needs 60 values, so KP1 effectively starts 2018-01; KP2 needs 250
  values, so it starts ~2018-10 (IS = 2018-10..2021, 3.2 years).
- fBTC funding is ~0 % p.a. on most days of 2023-24 (median 0.0, p95 0.0-0.5 %): FD2-BTC has almost no variation in
  VAL; fETH is low but varies. Counted as declared.

## Round 2 of the stream (added 2026-10-27 19:25 UTC, AFTER the 72 cells above were read; new sources / clocks, declared before their numbers)
What I had seen when writing this: CB gross positive in both eras for BTC but no cell at IS net t >= 2.0 (best +1.69);
KP2's declared short lost in VAL (the frenzy side continued); FD nothing. The two cells below are new constructions of
the "US-venue demand continues" mechanism, not refits of a CB grid; grids are fixed here, BTC only (ETH's IS cost
of 130-170 bp a round trip fails any IS by construction). They are second-look hypotheses: by round 18's rule their
expected HOLD retention is ~1/4 of VAL, and the count benchmark includes the 72 earlier cells.
- **K2-CBUS, US-hours Coinbase premium, follow.** The 72 cells average CBP over 24 hours, half of them Asian hours when
  US institutions do not trade. `cbus_D` = mean of hourly cbp for buckets starting 14:00..20:00 UTC on weekday D (US
  cash session, >= 6 of 7 hours). z vs the previous 30 values. z > k -> **long**, z < -k -> **short**; enter at
  23:05 UTC on D (after IC's 17:00 New York rollover hour in both seasons), hold h days. k in {1.0, 1.5} x h in {1, 3}:
  4 cells.
- **K2-BFX, Bitfinex premium over Coinbase, follow.** Both legs in USD, same-hour last trades (Bitfinex
  trade:1h:tBTCUSD close vs Coinbase BTC-USD close), daily mean over UTC day D (>= 18 hours), z vs 30 days; z > k ->
  **long**, z < -k -> **short** (offshore large-trader demand, "Bitfinex leads" practitioner lore); enter D+1 00:00 UTC.
  Caveat known before the numbers: 2017-19 Bitfinex USD traded at a discount (withdrawal problems), which a 30-day z
  only partly removes. k in {1.0, 1.5} x h in {1, 3}: 4 cells.
- Information only (post-hoc, no verdict possible): KP2 with the side reversed (long when KP > its 1-year q90), to say
  whether the reversal would even meet the IS bar.
Count after round 2: 80 cells; expected max |t| of 80 normals ~2.8.

## Round 3 of the stream (added 2026-10-27 19:26 UTC, AFTER round 2 was read; POST-HOC, flagged as such)
Seen before writing: K2-BFX (Bitfinex-over-Coinbase premium, follow) lost in IS (net t -1.2..-2.0) and VAL (-2.9..-3.8,
random 1-6 %); K2-CBUS nothing. Read the other way, K2-BFX says what CB says: when Coinbase trades rich against an
offshore venue, BTC rises afterwards. The rule below combines the two offshore legs under the CB mechanism. Its
leg choice and the sign of the Bitfinex leg were both seen first, so it is post-hoc: any number it gives is
information with an expected HOLD retention of ~1/4 of VAL (round 18), and it is held to the DEMO bar with the full
85-cell count as the chance benchmark.
- **K3-CBX, Coinbase premium against offshore venues, follow.** z1 = CB1's daily z (Coinbase vs Binance USDT, 30
  days), z2 = the daily z of ln(CB / Bitfinex) (= minus K2-BFX's premium, 30 days), Z = (z1 + z2) / 2 where both exist.
  Z > k -> **long**, Z < -k -> **short**, enter D+1 00:00 UTC. k in {1.0, 1.5} x h in {1, 3} days: 4 cells; plus the
  hourly version (mean of the two hourly z's vs 30 days of hourly values, k 2.0, hold 24 h): 1 cell. BTC only.
Count after round 3: 85 cells.
