# Round 4: cheap-instrument flows, a minute-precise benchmark scan and public external data (2026-09-27)

Continuation of [flow_search_2026-09-27.md](flow_search_2026-09-27.md) (round 3, where M1 failed its holdout). Same brief,
constraints and eras: IS 2016-2021, VAL 2022-2024; HOLD 2025-01..2026-09-24 is opened only for a pre-registered
candidate. For this round the user allowed public external data as well as the existing cache (not the VPS). Every
screen printed IS and VAL only.

## Answer

**No new candidate. Nothing reached a pre-registration, so no HOLD was opened.** Seventeen more directions were tested.
Two conclusions:

1. The only effects far above noise in both eras are **fixed-time liquidity V-shapes**. The largest is the Sydney
   open in AUD/NZD (t -13 IS, t -9 VAL). Each leg is 0.7-2 bp, which is IC's round-trip cost at those minutes (spread
   0.45-0.9 bp plus 0.6 bp commission). At executable prices they are zero or negative.
2. The public external sources tested are CFTC positioning, crypto funding rates, Binance order flow, dealer gamma
   and dark-pool flow (SqueezeMetrics), the VIX term structure, Treasury auctions and FRED yields/volatility (42 daily
   features). None gives an effect that holds from IS to VAL at a frequency a 21-month HOLD could confirm.

C3 remains the only algorithm in the repo that has passed out-of-sample years and a pre-registered holdout.

## Existing data (M1 cache)

| hypothesis (source) | where | result (IS / VAL) |
|---|---|---|
| Overnight drift conditional on late-day selling (dealer inventory, Boyarchenko, Larsen & Whelan 2023) | US30, USTEC, UK100: long 18:30 -> 04:00 ET after the 14:00-15:55 ET move | after a < -1 sd late sell-off: US30 +0.4 bp (t 0.0) / -3.6 (t -0.6). Unconditional: US30 +2.0 (t 1.4) / +0.4; USTEC +3.5 (t 2.1) / +1.5 (t 0.8) |
| Flows ending at the European close (11:30 ET) | US30, USTEC, UK100 | follow 09:30-11:30 to 13:00: US30 +0.4 / -1.2, USTEC +0.5 / -1.7 |
| Hedging demand into the US close: day's move -> last 30 min (Baltussen, Da, Lammers & Martens 2021) | US30, USTEC, UK100 | US30 +0.2 / +0.3 bp; USTEC +0.7 (t 0.9) / +1.1 (t 1.0); big days (\|z\| > 2) USTEC +10.0 (t 1.2) / +3.1 |
| **Minute-precise benchmark scan**: 19 benchmark times (Tokyo 09:55, CNY 09:15, ECB 14:15, WM/R 16:00, LBMA, NYMEX 14:30, FX option cuts, cash opens/closes of NY, Xetra, LSE, ASX, HKEX) x 14 day types x 7 windows (15 min - 2 h), vol-normalized | 26 symbols, 48,412 cells | 143 cells with \|t_IS\| >= 4. Beyond chance, and repeated in VAL: **Sydney open (10:00 Sydney, DST-aware)**: NZDUSD 15 min before -1.7 bp (t -13.2) / -1.7 (t -9.3), AUDUSD -1.6 (t -13.1) / -1.3 (t -7.5), then +1.2..+1.7 bp in the 15 min after. The Tokyo fix on all days (USDJPY 30 min before +1.1 bp, t 5.6 / +1.5, t 4.4; excluded: JPY fix). EURUSD 15 min into the ECB fix +0.7 (t 5.5) / +0.8 (t 4.2). USDJPY the hour after the NY close +0.8 (t 5.9) / +1.0 (t 3.8) |
| Sydney-open V at executable prices (sell at bid, buy back at ask, commission) | NZDUSD, AUDUSD, AUDJPY | median spread at 10:00 Sydney: NZD 0.89 bp, AUD 0.45, AUDJPY 0.80 (vs 0.28-0.68 later). Tue-Fri short 30 min before the open: NZD -0.3 bp (t -1.4) / -1.7 (t -6.9), AUD +0.2 / -0.9, AUDJPY -0.7 / -2.3. Long 30 min after: NZD -0.4 / -0.4, AUD +0.2 / 0.0. Mondays: AUD short +0.9 (t 1.6) / +1.5 (t 2.4), n about 50 a year. Real, but smaller than its cost |
| Intraday relative value, 15-min bars: fade a > 2.5 sd 60-min divergence for 1-2 h | US30-USTEC, US500-USTEC, US30-US500, DE40-UK100, XTI-XBR, EURUSD-GBPUSD | none: US30-USTEC -1.5 bp (t -2.5) / -0.1; DE40-UK100 +1.1 (t 1.8) / -0.1; EURUSD-GBPUSD +0.1 / +0.9. The WTI-Brent IS mean is the April 2020 outliers |

## Public external data

| source and hypothesis | where | result (IS / VAL) |
|---|---|---|
| **CFTC COT**, legacy futures-only 2014-2026 (cftc.gov `deacot{year}.zip`): (S1) trade against the weekly change in speculators' net position (liquidity provision, Kang, Rouwenhorst & Tang 2020); (S2) against speculator crowding (net/OI 3-yr z); (S3) hedging pressure (Keynes; de Roon, Nijman & Veld 2000). Next week Mon 01:00 -> Fri 19:00 UTC | 18 CME/COMEX/NYMEX markets mapped to FX, indices, metals, energies, BTC, ETH | in % of a weekly sd: S1 +1.0 (t 0.2) / +5.3 (t 1.3); S2 +4.8 (t 1.7) / +2.9 (t 0.8); S3 -4.7 (t -1.6) / -3.3 (t -0.9). No market consistent in both eras |
| **Crypto perpetual funding**, Binance BTCUSDT/ETHUSDT 2020-2026 (data.binance.vision): contrarian on expensive leverage | BTCUSD, ETHUSD | the contrarian sign is wrong: after top-decile 7-day funding, the next 5 days rise (BTC +180 bp / +190 as a loss for the short), but on overlapping windows. Weekly non-overlapping, with past 7/28-day returns in the regression, funding adds nothing: BTC -111 bp per sd (t -1.0) / -37 (t -0.6), ETH -79 (t -0.5) / +44 (t 0.6). It is crypto momentum, i.e. C1's mechanism |
| **Dealer gamma exposure (GEX)**, SqueezeMetrics DIX.csv 2011-2026: momentum into the close when dealers are short gamma, afternoon reversal when long (Baltussen et al. 2021) | US30, USTEC (US500 for information) | GEX does split volatility (low-GEX days move 92 vs 35 bp open-to-close on US30), but not direction: low-GEX follow into the close USTEC +6.0 (t 1.8) / +6.6 (t 1.6), US30 +2.5 / +1.0; high-GEX afternoon fade -0.6 / -1.5 |
| **Dark-pool index (DIX)**, same file: high DIX -> higher returns | US indices | top quintile, next 4 days (non-overlapping): US30 +41 bp (t 2.3) / -12 (t -0.5), USTEC +59 (t 3.1) / -42 (t -1.0) |
| **Pension month-end rebalancing, stock minus bond return** (Harvey, Mazzoleni & Melone 2025; FRED DGS10, duration 8.5): the specification of the paper, where round 3 used stocks alone | US500, US30, USTEC | last 3 days against the signal: US500 +9.3 bp (t 0.4) / +30.4 (t 0.9); first 2 days of the next month: +15.7 (t 0.9) / +1.5. Round 3's proxy had flipped in VAL, and this one is simply flat |
| **VIX term structure**, FRED VIXCLS / VXVCLS: backwardation = acute fear premium | US indices, ~4-day hold, non-overlapping | VIX/VIX3M > 1: US30 +37 bp (t 0.7, n 49) / +90 (t 1.8, n 13), USTEC +61 (t 1.3) / +112 (t 1.4, n 13). Too few events |
| **Treasury auction cycle** (Lou, Yan & Zhang 2013), TreasuryDirect 2014-2026 (997 coupon auctions) | USDJPY, USDCHF, EURUSD, GBPUSD, XAUUSD, US30, USTEC | intraday concession into the 13:00 ET close and after: USDJPY before short-dated auctions +4.5 bp (t 3.3) / +1.0 (t 0.4); US indices after long-bond auctions US30 +6.8 (t 1.6) / +5.8 (t 1.3). Multi-day (week before / 2 days after): USDJPY before +7.3 (t 1.5) / +22.7 (t 2.9); US30 after large auction weeks +35 (t 2.2, n 44) / +30 (t 1.3, n 39) |
| **Binance order-flow imbalance** (taker-buy share of hourly volume, 30-day z), futures and spot | BTCUSD next 1-4 h | \|z\| > 2, follow for 1 h: +4.1 bp (t 0.8) / +2.1 (t 0.7); for 4 h: +1.1 (t 0.2) / +2.1 (t 0.6) |
| **Crypto weekend reversal** ("CME gap fill"), Binance spot 2018-2024 as the 24/7 proxy for IC (IC closed crypto at weekends until 2024-04) | BTC, ETH | fading the Fri 17:00 -> Sun 17:00 NY move over Mon-Tue: BTC -10 bp (t -0.2) / -86 (t -2.3), i.e. in VAL the weekend move continues; ETH -11 / -69 |
| CBOE put/call ratios (cdn.cboe.com) | - | the free history ends 2019-10: no VAL or HOLD, not usable |
| **Daily external feature scan**: 14 series (VIX, VIX3M, VIX term ratio, OVX, GVZ, 2y/10y/3m yields, 2s10s, real 10y, 5y breakeven, broad dollar, GEX, DIX) x level / 1-day / 5-day change (1-year z), trade sign(z) when \|z\| > 1 | all 26 symbols, next 1 and 3 days (3-day on non-overlapping samples) | 1,867 tests; max \|t_IS\| 3.5 (XAGUSD after a 5y-breakeven change, VAL t 0.2), which is what chance produces; no top cell repeats in VAL. (ICE HY spread dropped: FRED now keeps only 3 years.) |

## What this says, and what would change it

- After four rounds, the picture is consistent. At IC's costs and within the brief's constraints, the 26 symbols over
  2016-2026 carry one robust calendar flow (gotobi, C3). They also carry several real fixed-time liquidity
  V-shapes that are smaller than the round-trip cost at the minutes they occur (Sydney open, Tokyo fix, ECB fix, NY
  close). The public positioning, leverage, options and macro series tested add no short-horizon edge that holds
  across eras.
- The ways forward are decisions, not more screening of the same data:
  1. **Lower execution cost.** The Sydney-open V is about 3 bp gross per day across both legs and 13-sigma
     significant. At roughly half of today's round-trip cost it would be worth a pre-registration.
  2. **More clean data.** IC ticks before 2016 (via cTrader backtests on the VPS, not approved this round), or new
     data after 2026-09-24 as it arrives, would give a holdout nobody has used.
  3. The brief's 5-day and 3-position limits rule out the multi-week trend and carry premia. That was noted in round
     3 and is not proposed here.

## Process

- External data was downloaded to the session scratchpad only (URLs above). Nothing was added to `research/data/`,
  and no code went into the repo because no candidate reached pre-registration.
- HOLD was not computed for anything in this round. The contamination list from round 3 still applies (pre-FOMC
  drift; hour-of-day patterns of XAUUSD, XAGUSD, US500, DE40, JP225, AUDUSD and BTCUSD). The Sydney-open finding
  rests mainly on NZDUSD, which is not on that list.
