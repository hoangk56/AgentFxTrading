# Stream A: A-share main board, long the session after a first limit-up close (round 63)

Written 2026-10-31 16:55 UTC (from `date -u`). Hypotheses (written before any return):
[HYPOTHESES_A.md](HYPOTHESES_A.md), with an addendum for the data-source change. HOLD stayed closed: no request
asked for a month after 2024-12, and both loaders assert `date < 2025-01-01`.

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)
All 12 tradable cells lose money after costs in IS and in VAL, in both universes (Connect proxy and the full main
board). No cell reaches net t > 0.3 in IS.

What the data show:
- **First sealed limit-ups gap up +216 bp at the next open in IS** (median +151) and +239 bp in VAL. That gap is the
  首板次日溢价.
- A buyer at the open pays for that gap, and the stock then fades.
- X1_S (open to next open), measured as excess over random stocks bought at the same open, is -53 bp IS (t -8.1) and
  -57 bp VAL (t -6.3).
- The fade is exactly the side a Northbound long cannot take.

Touched-only names (high = limit, close below it) are a different case:
- They gap down -111 bp at the next open.
- After that open they beat random stocks by +25 to +35 bp in IS (t 3.6-4.1), but by -4 to +5 bp in VAL (t ~0).
- In absolute net terms they are -17 to +4 bp in IS and -34 to -47 bp in VAL. So they fail VAL and the zero bar.

## Data
- **OHLCVault** (data.ohlcvault.com, monthly all-market shards; source pytdx for OHLCV plus the baostock
  back-adjustment factor).
  - Requests: 112 shards 2015-09..2024-12 plus the symbol list.
  - Size: 148 MB under research/data/ashare/ov/; log at research/data/ashare/requests.log.
  - robots.txt holds only Cloudflare's preamble, with no rules. The CDN is built for programmatic download by an
    MIT-licensed client.
  - Panel: 3,321 main-board stocks, delisted names included, 2,268 sessions.
- **Cross-check against Tencent.** I compared 124 stocks (208,301 bars, 2016-11..2024-12) with the Tencent unadjusted
  klines. OHLC agree to 0.005 CNY on 100.00 % of bars. Tencent has 0 bars that OHLCVault lacks; OHLCVault has 993
  bars that Tencent lacks. Details: [out/validate.txt](out/validate.txt).
- **Tencent web.ifzq.gtimg.cn** (the planned source) put a WAF block page (HTTP 501, waf.tencent.com) in front of the
  pull after 137 requests at ~1 per 1.4 s. I stopped; no retry, no other host, no UA change.
- **Other hosts:** NetEase is dead (502). Sina hq.sinajs.cn answers 403. Sina's kline API cannot take an end date
  (it would load HOLD), so it was not used.
- **Survivorship:** 295 delisted main-board stocks are in the symbol list and have bars up to their delisting.
  - Residual gaps: the symbol list comes from baostock, so codes baostock never knew are missing.
  - Connect eligibility history is not available. The proxy used: trailing 60-day traded value >= the 40th
    percentile of that day's main-board cross-section.
- **ST:** ST status is not in the data, and today's names would be look-ahead. A limit-up is defined as close =
  round(ref x 1.10, 2). ST stocks are capped at +-5 % and so cannot qualify.
- **New listings:** an event needs >= 60 bars and >= 120 days since the IPO.

## Rule and grid (as declared)
Event and entry:
- **Event:** close = limit (S, sealed) or high = limit with close < limit (T, touched only).
- The limit is computed from the ex-rights reference `C_{t-1} x af_{t-1} / af_t`.
- **"First":** no limit-up close in the previous 20 sessions.
- **Entry:** the open of t+1. Events whose next open is a one-price limit-up are skipped: 6.9 % of S events in IS and
  9.1 % in VAL.

Exits:
- X0 = close of t+1. Not tradable under T+1; information only.
- X1 = open of t+2.
- X2 = close of t+2.
- X3 = close of t+3.
- An exit at limit-down rolls to the next open.

Continuation variants:
- CV1a: buy T names at the t close, exit at the t+1 open.
- CV1b: buy T names at the t close, exit at the t+1 close.
- CV2: S events with a t+1 open gap >= +3 %, held to X2.

Book: each date gets one equal-weight basket. The t statistic is computed on the per-date series with Newey-West
lag = the hold in sessions.

## Costs
Median round trip on X2 events: **40.4 bp**. Components:
- Commission 3 + 3 bp.
- Connect fees 0.7 + 0.7 bp.
- Stamp duty 10 bp, or 5 bp from 2023-08-28.
- Half tick per side. The median entry stock is 11.45 CNY, so 4.4 bp per side.
- Opening-auction slippage 10 bp on the buy, 5 bp on the exit.

Stress: costs x1.5.

## Results: Connect proxy (primary), net bp per date basket
| cell | IS events / dates | IS gross | IS net | IS t | VAL events | VAL gross | VAL net | VAL t | net x1.5 IS / VAL | late IS / VAL | yrs + | beats random IS / VAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X1_ALL | 22,234 / 1,458 | -27.2 | -70.4 | -11.33 | 13,469 | -38.2 | -80.5 | -9.06 | -91.9 / -101.6 | -49.2 / -54.3 | 0/9 | 0 % / 0 % |
| X1_S | 14,153 / 1,438 | -53.8 | -96.5 | -12.87 | 8,150 | -58.3 | -100.0 | -9.38 | -117.9 / -120.9 | -52.8 / -69.4 | 0/9 | 0 % / 0 % |
| X1_T | 8,081 / 1,411 | +26.4 | -17.5 | -2.37 | 5,319 | -3.6 | -46.6 | -4.32 | -39.4 / -68.0 | -44.6 / -42.7 | 2/9 | 100 % / 19 % |
| X2_ALL | 22,234 | +4.8 | -38.3 | -4.27 | 13,469 | -19.2 | -61.4 | -4.74 | -59.9 / -82.5 | -25.9 / -37.2 | 0/9 | 0.4 % / 0 % |
| X2_S | 14,153 | -12.5 | -55.2 | -5.50 | 8,150 | -39.1 | -80.8 | -5.69 | -76.6 / -101.7 | -28.0 / -47.2 | 0/9 | 0 % / 0 % |
| X2_T | 8,081 | +40.8 | -3.1 | -0.29 | 5,319 | +5.2 | -37.7 | -2.50 | -25.0 / -59.2 | -23.6 / -31.8 | 3/9 | 100 % / 50 % |
| X3_ALL | 22,234 | -10.9 | -54.0 | -4.33 | 13,452 | -32.9 | -75.2 | -4.04 | -75.6 / -96.3 | -28.9 / -49.7 | 0/9 | 0 % / 0 % |
| X3_S | 14,153 | -41.5 | -84.2 | -5.97 | 8,138 | -65.7 | -107.5 | -5.54 | -105.6 / -128.4 | -34.0 / -56.0 | 0/9 | 0 % / 0 % |
| X3_T | 8,081 | +47.8 | +3.9 | 0.28 | 5,314 | +9.3 | -33.7 | -1.56 | -18.1 / -55.1 | -24.1 / -34.7 | 3/9 | 100 % / 74 % |
| CV1a | 8,097 | -108.6 | -152.5 | -41.6 | 5,430 | -95.1 | -137.9 | -29.7 | -174.5 / -159.3 | -81.0 / -75.9 | 0/9 | 0 % / 0 % |
| CV1b | 8,097 | -49.4 | -93.3 | -12.3 | 5,430 | -71.5 | -114.3 | -10.7 | -115.3 / -135.8 | -66.6 / -67.4 | 0/9 | 0 % / 0 % |
| CV2 | 3,599 / 1,129 | -75.4 | -118.6 | -6.74 | 1,989 | -104.6 | -146.3 | -5.77 | -140.2 / -167.2 | -25.2 / -32.3 | 0/9 | 0 % / 0 % |
| X0_T (not tradable, T+1) | 8,082 | +58.4 | +14.3 | 2.19 | 5,320 | +22.6 | -20.3 | -2.12 | -7.7 / -41.8 | n/a | 5/9 | n/a |

Yearly net, best cells (bp, 2016..2024):

| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| X2_T | +49.5 | -30.9 | -38.0 | -27.8 | +2.2 | +27.9 | -45.7 | -30.1 | -37.2 |
| X3_T | +48.5 | -17.8 | -58.0 | -15.0 | +22.4 | +44.5 | -37.8 | -30.7 | -32.4 |

Other robustness checks:
- N = 60 for X3_T: +16.9 IS (t 1.19), -32.4 VAL.
- Excluding 2020-02..04 for X3_T: IS t 0.13.
- Full main-board universe: everything is worse. Best X3_T: -12.0 IS (t -0.98), -32.0 VAL.

### Random benchmark and nulls
| cell (Connect proxy) | excess over random IS (bp) | t | excess over random VAL (bp) | t |
|---|---|---|---|---|
| X1_T | +24.7 | 4.09 | -3.8 | -0.47 |
| X2_T | +27.9 | 3.56 | -0.3 | -0.03 |
| X3_T | +34.7 | 3.55 | +4.5 | 0.35 |
| X0_T (not tradable) | +45.8 | 8.28 | +16.6 | 2.18 |
| S cells and CV1 / CV2 | -22 to -110 | -2.7 to -27 | -43 to -111 | -4.2 to -21 |

- **Random benchmark:** for each date, draw the same number of random non-limit pool stocks with the same entry, exit
  and costs, 1000 times. The pool earns about -31 to -42 bp net, which is the cost of trading with no gross edge.
- **Max-t null on gross returns** over the 12 cells (300 draws): p95 2.62 IS / 1.80 VAL. The T cells' gross IS t of
  3.5-3.9 clears the IS null, but their gross VAL t is 0.35-0.43.
- **Power at VAL size** for the best cell, X3_T: the net per-date Sharpe in VAL is -0.075, so HOLD power is < 0. Even
  the gross excess (Sharpe ~0.01 per date in VAL) would give HOLD power ~0.3, far from 3.

## Why it fails
1. **The premium sits in the open auction.**
   - Sealed first boards open +2.2 % higher on average (+2.4 % in VAL). The unfilled limit-up queue is the buyer, and
     it clears at the open.
   - From that open, the next close (not tradable) is ~0 gross, and every tradable exit is negative: -54 bp at the
     next open (X1_S), -13 bp at the t+2 close.
   - This matches the "buy-limit / sell-next-day to retail" description of Chen, Gao, He, Jiang & Xiong. The only
     trade that profits from it is a fade, which a long-only Connect account cannot do.
2. **Touched-only boards are failed boards (炸板).**
   - They gap down ~1 %, so buying the close (CV1a) loses -109 bp gross by the next open.
   - The partial reversion after the open was real in 2016-2021 (+25-35 bp excess) and gone in 2022-24, after
     roughly 40 bp of costs.
   - A cell that is positive in 3 of 9 years and negative in every VAL year is not a rule.
3. **Costs.** ~40 bp a round trip (stamp duty plus the auction impact) exceeds any gross drift after the open in VAL.

## Pitfalls
- **T+1:** open-to-close on the day of purchase (X0) is not tradable for a new buyer. Its +14 bp IS (t 2.2) is the only
  "positive" net number in the grid. Do not count it.
- **Ex-dividend days:** compute the limit from the ex-rights reference price. A raw previous close misses limit-ups on
  ex-dates.
- **Tencent fqkline:** returns at most the last 2000 bars of a window, and the WAF blocks a sustained 1 request / s
  pull after ~140 requests. **OHLCVault** monthly shards give the whole market in 112 requests and matched Tencent on
  100 % of 208k bars.
- **One-price limit-up opens** (7-9 % of sealed events) cannot be bought. Excluding them is right, but it removes the
  strongest continuations, so the tradable set is biased toward fades.
- **Max-t null:** computed on net returns, it is meaningless here (every cell is negative). Use gross.

## What a user decision could unlock (small)
| decision | why it could matter | estimate |
|---|---|---|
| Queue a buy at the limit price on day t (打板) | The +216 bp gap goes to whoever was filled at the limit. Fills on a sealed board are adversely selected (you are filled when the seal breaks), so this needs L2 order-queue data (paid) to test. | LIVE < 1 %, DEMO ~2 % |
| A domestic account with ChiNext / STAR (+-20 %), or shorting via margin (融券) | A fade of X1_S (-54 to -58 bp excess) is large, but short supply on hot small caps is near zero and Connect has no short selling. | LIVE ~1 % |
| Intraday bars (exit at the t+1 morning high) | The premium decays during t+1. Needs paid minute data. | < 1 % |

## Files
- Hypotheses: [HYPOTHESES_A.md](HYPOTHESES_A.md).
- Code: [code/](code/).
  - pull_codes.py, pull_klines.py: Tencent pulls, stopped by the WAF.
  - pull_ov.py: the OHLCVault pull.
  - build_panel_ov.py: builds the panel.
  - validate.py: cross-check against Tencent.
  - analyze.py: the declared grid.
  - diag.py: excess over random, gross max-t null, gap premium.
  - build_panel.py: parser for the Tencent files.
- Output: [out/results.txt](out/results.txt), [out/results.json](out/results.json), [out/diag.txt](out/diag.txt),
  [out/validate.txt](out/validate.txt).
- Data (git-ignored): research/data/ashare/ holds ov/ (shards and meta), raw_kline/ (137 Tencent files), raw_quote/
  (code-existence probe), panel_ov.npz and requests.log.
