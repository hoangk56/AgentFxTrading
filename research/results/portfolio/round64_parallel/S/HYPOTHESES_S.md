# Stream S hypotheses: stablecoin peg reversion on Binance spot

Written 2026-11-01 09:52 UTC (from `date -u`), before any stablecoin data was downloaded or any return computed.
Fee facts below come from 3 WebSearches done before this file (no price data seen).

## Mechanism
Fiat-backed stablecoins (USDC, BUSD, TUSD, USDP / PAX, FDUSD, USDS) redeem at par with their issuer; DAI is held
near par by its Peg Stability Module (USDC 1:1). A discount of X/USDT on Binance is a wedge with an anchor: it opens
when one group of holders dumps X (issuer / bank news, a chain or venue problem, delisting or conversion on Binance)
faster than redeemers / arbitrageurs can absorb it, and it closes when redemption or the news passes. Side fixed:
**long X, paid in USDT, only when X is cheap** (no borrow). The mirror (X rich = USDT cheap) is information only.

Caveat fixed in advance: X/USDT < 1 can be USDT rich, not X cheap. The trade is still the same wedge (two par
anchors) and is graded as such; the BTC cross (BTCUSDT vs BTCBUSD / BTCUSDC, 1h) is reported to say which leg moved.

## Data (to request)
data.binance.vision spot monthly 1m klines 2018-01..2024-12 for USDCUSDT, BUSDUSDT, TUSDUSDT, PAXUSDT, USDPUSDT,
FDUSDUSDT, DAIUSDT, USDSUSDT, USDSBUSDT (any month that 404s = not listed). Excluded by declaration: UST / USTC
(algorithmic, no par redemption), PAXG (gold), EUR / AEUR / EURI (not USD). BTC cross: 1h monthly klines of
BTCUSDT, BTCBUSD, BTCUSDC (information only). Load with ts < 2025-01-01. Requests logged in
research/data/binance_stables/requests.log.

## Eras
IS = first available month .. 2021-12-31 (brief: "2016-2021 for anything with older data"; stable pairs start
2018-19), VAL = 2022-01-01..2024-12-31. HOLD never opened.

## Rule (per pair, one position per pair at a time)
- d_t = 1 - close_t of X/USDT 1m bar t.
- Signal: d_t >= k at a bar close (no position open). Entry: buy at the close of bar t+1 (late check: t+2). If that
  bar has zero trades, use the next bar with trades (bad-print / stale guard).
- Exit: first bar s > entry with d_s <= k/2: sell at the close of s+1 (late: s+2); else time stop: sell at the close of
  the bar at entry + H. Same zero-trade rule. A new trade can only start after the exit bar.
- Grid (6 cells): k in {10, 30, 100} bp x H in {1, 7} days. Pairs pooled, equal notional per trade.
- Trade return r = P_exit / P_entry - 1 - costs; excess = r - DFF(entry day) x hold_days / 365.

## Costs
- Primary: Binance standard spot taker 10 bp per side (no BNB discount, no VIP) + half-spread proxy 0.5 bp per side
  (USDC, BUSD, FDUSD, the deep pairs) or 1.0 bp (TUSD, PAX / USDP, DAI, USDS). Round trip ~21-22 bp.
- Secondary (reported, not the verdict basis unless documented): zero taker fee on USD stablecoin / stablecoin spot
  pairs from 2023-07-01 (Binance announcement "zero trading fee promotion ... all existing and new USD stablecoin spot
  and margin pairs, incl. BUSD/USDT, TUSD/USDT, USDC/USDT, USDP/USDT", from 2023-06-30; FDUSD/USDT zero taker from
  2023-07-26). Before 2023-07-01 the standard 10 bp is charged even where maker promotions existed.
- Stress: costs x1.5 and the one-bar-late entry / exit.
- Arithmetic before data: with ~21 bp round trip, k = 10 can gain at most ~10 bp if it reverts fully to par, so it is
  net negative by construction at standard fees and only testable on the zero-fee variant; k = 30 needs a near full
  reversion; k = 100 is the cell with room for costs.

## Statistics
- Episode = union of trades in any pair whose [entry, exit] intervals, each padded by 24 h, overlap (one SVB weekend
  in USDC and DAI is one episode). t of the mean trade return clustered by episode (CR1 sandwich, G / (G-1)). Report
  trades, episodes, years positive.
- Random benchmark: for each real trade, a random entry minute uniform in the same pair and era, long, held the same
  number of bars, same costs; 2000 draws; % of draws whose mean is below the rule's mean. Also a tougher "same
  discount" benchmark (random minute in the same pair / era with d in the same bucket as at entry, same hold): timing
  inside a discount. Max-over-cells null: per draw take the max over the 6 cells of the random mean minus the cell's
  own random mean, compare with the best cell.
- C3 correlation: daily P&L correlation with trades_C3_gotobi_jpy_basket.csv (IS / VAL) for any DEMO-level cell.

## Power arithmetic (before data)
HOLD 2025-01..2026-10 = 1.83 years. If VAL (3 years) holds E independent episodes, HOLD expects ~0.61 E. LIVE needs
per-episode Sharpe (VAL size) x sqrt(0.61 E) >= 3:
- E = 5 -> per-episode Sharpe >= 1.72 (unreachable for lumpy depeg trades); E = 15 -> 0.99; E = 30 -> 0.70; E = 60
  -> 0.50.
Prior on episodes: deep discounts (k = 100) on Binance are a handful of named events (USDC / DAI March 2020?, SVB
March 2023, TUSD 2023-24, BUSD wind-down 2023), i.e. E ~ 2-6 in VAL and fewer in IS: k = 100 can reach DEMO at best
and probably cannot clear t >= 2 by episode. k = 10-30 may give dozens of shallow episodes, but at standard fees they
cannot net positive (above); only the zero-fee variant (VAL 2023-07+ only, none in IS) could produce many episodes,
and it has no IS to pick parameters on. Expectation: no LIVE; DEMO only if k = 100 has >= ~8 positive IS episodes.
Stop early if IS / VAL hold only a handful of independent episodes per cell.

## Addendum 2026-11-01 10:14 UTC (after a first run on 5 of 9 pairs; nothing in the rule or grid changed)
The first run showed that the k = 100 IS gross (+49 bp at bar closes) falls to +26 bp if one buys at the entry bar's
high and sells at the exit bar's low: on thin 2018-20 pairs (PAX, TUSD, USDC 2-12 bp median 1m ranges) part of the
close-to-close reversion can be bid / ask bounce that the declared 0.5-1 bp half-spread does not cover. Added a fill
check, not a new rule: buy at the entry bar's taker-buy average price (taker_buy_quote / taker_buy_base), sell at the
exit bar's taker-sell average price ((quote - taker_buy_quote) / (volume - taker_buy_base)), next bar with such
trades within 10 bars, fees only (the spread is inside the price). The verdict requires the cell to pass the bars
under BOTH the declared close fill and this taker fill; the worst fill (high / low) is reported as a bound.
