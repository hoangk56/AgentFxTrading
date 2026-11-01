# Stream A hypotheses: China A-shares, the session after a first limit-up close (long only)

Written 2026-10-31 16:24:46 UTC (from `date -u`), before any return was computed. The only data seen so far are probe
bars of 3 stocks, used to check the API format (dates, OHLCV columns, the 2000-bar cap). Brief:
[../BRIEF.md](../BRIEF.md), idea I6 in [../I/IDEAS_I.md](../I/IDEAS_I.md). HOLD (2025-01-01 onward) stays closed:
every request ends 2024-12-31 and the loader asserts `date < 2025-01-01`.

## Mechanism
- SSE / SZSE main-board stocks cannot close more than 10 % above the previous close. Under T+1 a buyer cannot sell
  on the day of purchase.
- When a stock closes sealed at the limit (close = limit price), buy orders are left unfilled in the queue. That
  demand rolls into the next session's opening auction. The literature and practitioner lore (首板次日溢价) describe
  a next-open premium followed by an intraday fade. Chen, Gao, He, Jiang & Xiong describe large investors who buy
  into limit hits and sell to retail the next day.
- Access for the user is Northbound Stock Connect: long only, main-board names. A fade cannot be traded. The tests
  are therefore LONG-only. The question is whether, after paying the open price (which already contains the gap),
  there is any further drift.
- Prior: the premium is mostly in the open gap, which a buyer at the open does not earn. The expected open-to-later
  return is ~0 or negative (the fade). P(LIVE) ~1.5 %, P(DEMO) ~5 % (from IDEAS_I).

## Data
- Tencent `web.ifzq.gtimg.cn/appstock/app/fqkline/get` (unadjusted daily OHLCV: date, open, close, high, low,
  volume in lots). Robots check 2026-10-31: web.ifzq.gtimg.cn/robots.txt returns a JSON error ("No dispatch info"),
  qt.gtimg.cn/robots.txt returns "bad request". Neither host serves a robots file, and I found no terms forbidding
  automated access. Eastmoney is not used. Pull rules: one request at a time, >= 1.05 s apart, stop on 403 or a
  captcha, log every request to research/data/ashare/requests.log.
- The API returns at most 2000 bars, the last 2000 in the requested window. With one request per stock and an end of
  2024-12-31, a long-listed stock starts around 2016-10-13. To keep the cross-section uniform, **IS is
  2017-01-01..2021-12-31** (a declared deviation from 2016-2021: Jan-Sep 2016 is dropped to halve the number of
  requests). **VAL is 2022-01-01..2024-12-31.**
- Universe:
  - Code space: main board only, i.e. SSE 600xxx / 601xxx / 603xxx / 605xxx and SZSE 000xxx / 001xxx / 002xxx /
    003xxx (002 = the former SME board, merged into the main board in 2021).
  - Excluded: ChiNext 300/301, STAR 688/689 and B shares.
  - Which codes exist comes from the batch quote `qt.gtimg.cn/q=...`. It also returns delisted codes (for example
    凯迪退 000939 and 退市锐电 601558), so delisted names enter the pull.
  - Survivorship is therefore mostly handled. Remaining gaps: codes that were reused, and delisted codes the quote
    server no longer knows.
  - The quote fields are 2026 values. They are used only for "does this code exist": not the name, not the market
    cap, not the price.
  - If the full pull exceeds ~45 min, a seeded random order is used and the pull stops at the time limit. That gives
    a random subsample, and its size will be stated.
- ST:
  - Tencent has no history of ST status, and today's names are look-ahead.
  - An ST stock's limit is +-5 %, so it cannot close at the 10 % limit price. Defining a limit-up as close = round(prev
    close x 1.10, 2) therefore excludes ST stocks automatically.
  - Residual risk: days where ST status changes, when the limit switches.
- Connect proxy: the Connect eligibility history is not available (it needs SSE 180/380 and SZSE index membership
  plus a market-cap floor). As a declared proxy, an event is in the "Connect proxy" universe if the stock's trailing
  60-day mean traded value (volume x 100 x close) is at or above the 40th percentile of that day's main-board
  cross-section (the top 60 %). Results are reported for both the Connect proxy (primary) and all main-board names.

## Event definition (fixed)
- Limit price on day t: `Lu_t = round_half_up(C_{t-1} x 1.10, 2)`. Limit-down: `Ld_t = round_half_up(C_{t-1} x 0.90, 2)`.
  A 0.005 tolerance is applied to equality tests.
- Limit-up close (sealed, S): `C_t = Lu_t`. Touched only (T): `H_t = Lu_t` and `C_t < Lu_t`.
- The stock needs >= 60 earlier bars in the data, so new listings, the 44 % first day and the post-2023 no-limit first
  5 days are dropped.
- Ex-dividend days use the raw previous close (higher than the exchange reference), so a few limit-ups on ex-dates are
  missed. This loses events; it does not bias their returns.
- "First": no limit-up close in the previous N = 20 trading days of that stock. N = 60 is a robustness check on the
  chosen cell only. Not a grid axis.
- Entry: the open of t+1. The event is skipped if `O_{t+1} >= Lu_{t+1} - 0.005` (one-price limit open, cannot be
  bought) or if the stock does not trade on t+1.
- Exit price: if the exit price equals limit-down (cannot sell), the exit moves to the next session's open; this
  repeats up to 10 times.

## Grid (declared; 12 cells)
Exits after entry at `O_{t+1}`:
- X0: `C_{t+1}`. Information only: under T+1 a new buyer cannot sell on the purchase day, so X0 is not tradable and
  cannot be a candidate.
- X1: `O_{t+2}`.
- X2: `C_{t+2}`.
- X3: `C_{t+3}`.

Conditions:
- ALL (S or T).
- S: sealed.
- T: touched, not sealed.

The tradable cells are 3 exits x 3 conditions = 9.

Continuation variants (long, declared):
- CV1: buy at `C_t` on T events. A touched-but-unsealed stock has sellers at the close, so the closing auction fills.
  Exit at `O_{t+1}` (CV1a) or `C_{t+1}` (CV1b). This is the only way a long captures the "next-open premium" itself.
- CV2: S events whose `O_{t+1} / C_t - 1 >= +3 %` (strong open, aimed at a second board). Buy at `O_{t+1}`, exit at
  `C_{t+2}`.

Total: 9 + 3 = 12 candidate cells. The max-over-cells null is computed over the same 12 cells on the random
benchmark.

## Book, statistics, benchmark
- Each date (entry date) gets one equal-weight basket of that date's events. The unit is the per-date mean net
  return. The t statistic is computed on the per-date series (date clustering). For holds that overlap (X2, X3, CV2)
  it is Newey-West with lag = the hold in sessions.
- Years: 2017-2024 per calendar year of the entry date. The bar is >= 2/3 of years positive.
- Random benchmark: for each event date, draw the same number of stocks from the eligible universe. Eligible means
  the same main-board / Connect-proxy filter, no limit-up or limit-down close on t, tradable at `O_{t+1}`. Use the
  same entry and exit and the same costs. Draw 1000 times and report the percentile of the rule's net mean.
- Max-t null: for each random draw, take the max t over the 12 cells. The best real cell is compared with the 95th
  percentile of that max.
- Robustness: costs x1.5; one step late (enter at `O_{t+2}` with the same hold length; CV1 late = buy at `O_{t+1}`);
  excluding 2020-02..04; N = 60.

## Costs (per round trip, bp of notional)
| item | assumption |
|---|---|
| commission | 3 bp per side |
| Connect fees (handling 0.487 bp, management 0.2 bp, transfer ~0.1 bp) | 0.7 bp per side |
| stamp duty, sell side only | 10 bp before 2023-08-28, 5 bp from 2023-08-28 (by exit date) |
| tick / spread | half tick per side = 0.005 / price x 1e4 bp (10 CNY: 5 bp; 5 CNY: 10 bp; 20 CNY: 2.5 bp), on the event's entry price |
| auction slippage | 10 bp on the opening-auction buy (hot names), 5 bp on the exit |

Example: 10 CNY before 2023-08 gives 3 + 0.7 + 5 + 10 (entry) + 3 + 0.7 + 5 + 5 + 10 (exit) = 42.4 bp. Stressed x1.5:
~64 bp. Cash-rate drag on 1-3 day holds is ~1-2 bp and is ignored (said here, not hidden).

## Power arithmetic (dates are the sample)
- ~243 trading dates a year. IS 2017-2021 has ~1,215 dates and VAL ~727. HOLD 2025-01..2026-10 has ~430.
- With first-limit-up events on nearly every date in a ~1,500+ stock universe, the per-date net Sharpe s_d needed is:

| bar | requirement on s_d |
|---|---|
| IS t >= 2.5 | s_d >= 2.5 / sqrt(1215) = 0.072 |
| VAL t >= 1.5 | s_d >= 0.056 |
| HOLD power >= 3 | s_d >= 3 / sqrt(430) = 0.145, about an annual Sharpe of 2.25 |
| DEMO, IS t >= 2.0 | s_d >= 0.057 |

- The per-date sd of a basket of next-day returns of hot stocks is probably ~2-3 %. LIVE then needs a net mean of
  >= ~0.3-0.45 % per date, i.e. a gross >= ~0.7-0.9 % over the open after ~40 bp of costs. That is large for a
  post-gap drift. Only the S / CV2 continuation cells can plausibly reach it.
- DEMO needs ~0.15 % net in IS.
- Which bar each cell can reach:
  - X1-X3 ALL / T: DEMO at most (expected fade, near or below zero).
  - S cells and CV2: LIVE possible only if the sealed-board continuation is real after the open.
  - CV1 (close buy on touched): DEMO / LIVE possible if the touched names carry an overnight premium. Prior small,
    because unsealed boards are the weak ones.

## Addendum 2026-10-31 16:49:56 UTC (from `date -u`): data source changed, still before any return was computed
- **Tencent blocked the pull.** At 16:37 UTC, after 137 kline requests (~1 request / 1.4 s), web.ifzq.gtimg.cn began
  answering HTTP 501 with a Tencent WAF redirect page (waf.tencent.com/501page). I treated that as a block or
  captcha and stopped; I did not retry, change host or change the UA. The 137 files are kept only to cross-check the
  new source.
- Other sources checked:
  - NetEase quotes.money.163.com: 502, the service is gone.
  - Sina hq.sinajs.cn: 403 on robots.txt.
  - Sina's kline API cannot take an end date, so it would load 2025-26 (HOLD). Not used.
- **New source: OHLCVault** (data.ohlcvault.com).
  - Public CDN with monthly all-market shards, built for programmatic download by its MIT-licensed open-source client
    (github.com/helpquant/ohlcvault, SPEC.md v1).
  - robots.txt holds only Cloudflare's content-signal preamble: no User-agent or Disallow lines and no signals set.
  - Prices are unadjusted (pytdx) and carry baostock's cumulative back-adjustment factor `af` and the traded amount.
  - The symbol list (meta/symbols/cn.json) has board, IPO date and status, and includes 295 delisted main-board
    stocks.
  - It is a third-party compilation, so it is cross-checked against the 137 Tencent stocks before use.
  - 112 requests: months 2015-09..2024-12. The 2015 months are lookback only.
- Changes to the declared design. Each one follows from the better data and none from returns:
  1. **IS is back to 2016-01-01..2021-12-31** as in the brief. The cross-section is the full main board, not a
     subsample.
  2. The limit reference is the ex-rights previous close `C_{t-1} x af_{t-1} / af_t` (the exchange's 前收盘 on
     ex-dates), rounded half up to 0.01. Returns are af-adjusted (dividends included).
  3. New-listing guard: >= 60 bars since the first bar in the panel, and the IPO date (meta) >= 120 calendar days
     before t.
  4. Universe: board = "main" in meta (includes the former SME 002 board), code prefixes as declared, type stock.
     The name field is not used: it is today's name, so it would be look-ahead for ST status.
  5. Traded value: the shard's amount `a` replaces volume x close.
- Grid, costs, statistics, bars and the benchmark are unchanged.
