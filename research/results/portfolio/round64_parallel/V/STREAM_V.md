# Stream V: venues that could lend coins for B's short-spot leg (round 64, scouting)

Written 2026-11-01 09:07 UTC (from `date -u`). Declared in [HYPOTHESES_V.md](HYPOTHESES_V.md) (08:53 UTC, before any
venue request). Not a backtest: B's rule is untouched and no B P&L is computed. No 2025-26 number is used; the spot
tracking check uses B's 333 VAL 2022-24 entry times only (BX/out/events.csv lag 0), all series cut at ts < 2025-01-01.

## Answer
- **Coins can be borrowed elsewhere today, cheaply, in demo size.** Gate covers 69 / 75 (92 %) of B's current
  universe, Bybit 55 / 75 (73 %), OKX 52 / 75 (69 %), KuCoin 51 / 75 (68 %, rate and cap need a key). Gate or Bybit
  together: 69 / 75. Today's no-VIP borrow rates are 5.5-6.4 %/yr median (far under B's 40 %/yr), and every covered
  coin allows at least 1,000 USDT per account (Gate median cap 120,000 USDT, Bybit 61,000, OKX 55,000).
- **But another venue's spot does not track Binance spot at B's signals, and the gap goes against B.** At B's VAL
  signal hours Binance spot is already rich versus the other venues' spot (median 10-17 bp, mean 24-50 bp), and over
  B's hold Binance spot falls back to them: a short on the other venue's spot gains **38-50 bp less per trade (mean, ex
  crash windows; median 13-25 bp; 68-76 % of events worse)** than the Binance spot short B models. B's convergence is
  partly Binance-spot specific (consistent with BX, where perps moved together and Binance spot did the moving). The
  venues' spot books are also thin: their quote volume around B's signals is 2-17 % of Binance's.
- **Recommendation: fix borrowing on Binance first.** Binance itself lists margin on 73 / 75 of B's current coins
  (`isMarginTradingAllowed`, public), so the user's 0 / 495 is an account-level block (margin account not activated /
  no collateral in it / jurisdiction or sub-account restriction), not missing inventory. A foreign venue is a fallback
  with a known tracking cost (about a quarter of B's VAL mean net of +174.6 bp) and is **not B as registered**: running
  the demo on it would test a different short leg, so it must be labelled as such (the PREREG forbids replacing the
  short-spot leg with another hedge; another venue's spot is arguably that). If the user still wants a fallback, Gate
  (coverage 92 %, caps) or Bybit (73 %, simplest UTA spot margin) are the candidates; the decision is the user's.

## Venue table (B's current universe = 75 coins in universe60_hold.csv whose membership reaches 2026-10, BTC / ETH excluded)
| venue | public data used | current coverage | rate no-VIP, median / p90 (%/yr) | share <= 40 %/yr | cap per account, median (USDT) | cap >= 10k | VAL spot tracking (shortfall vs Binance, ex crash mean / median bp) | caveats |
|---|---|---|---|---|---|---|---|---|
| Gate | unified/currencies, margin/uni/currency_pairs, unified/history_loan_rate | **69 / 75 (92 %)** | 6.4 / 42.5 (latest hour) | 87 % | 120,000 | 100 % | **not checkable** (1h candles only 10,000 points back, ~2025-07) | 28 % of covered coins had an hour > 40 %/yr in the last 100 h; floating hourly rate; unified account |
| Bybit | spot-margin-trade/data (No VIP), spot instruments, tickers | 55 / 75 (73 %) | 5.5 / 14.8 | 96 % | 61,481 | 85 % | +49.9 / +24.9 (n 123, 68 % worse); corr 0.945 | missing TAO, ZEC, XMR, ONE, DASH, NMR...; volume ~2 % of Binance; spot margin is UTA-only |
| OKX | public/interest-rate-loan-quota (basic, Lv1), public/instruments MARGIN, tickers | 52 / 75 (69 %) | 6.0 / 14.9 | 98 % | 55,040 | 88 % | +46.0 / +16.9 (n 136, 76 % worse); corr 0.972 | basic rate is a base rate (daily x 365); missing FET, QNT, WAL, ONE, NMR...; volume ~17 % of Binance |
| KuCoin | margin/config (cross list), isolated/symbols, allTickers | 51 / 75 (68 %) | needs key | - | needs key | - | +38.2 / +12.7 (n 204, 68 % worse); corr 0.975 | lending-market rate endpoint returns empty; borrow rate / cap endpoints need KC-API-KEY; volume ~4 % |
| Bitget | - | not scouted | - | - | - | - | - | api.bitget.com answered robots.txt with 403: host stopped |
| Binance | exchangeInfo `isMarginTradingAllowed` (data-api.binance.vision) | 73 / 75 pairs margin-enabled (97 %) | needs key (/sapi) | - | needs key | - | (is the reference) | user account cannot borrow; api.binance.com robots.txt is `Disallow: /`, so only data-api.binance.vision was used |

Coverage of all 384 names ever in B's universe (2020-26): Gate 76 %, Bybit 49 %, OKX 37 %, KuCoin 31 %, Binance flag
78 %; many are delisted. Coverage today of the coins behind B's 333 VAL entries (event-weighted): Gate 69 %, OKX 45 %,
KuCoin 36 %, Bybit 32 %, Binance flag 71 %. Of VAL's big-P&L squeeze coins, none of OM, REN, SRM is lendable anywhere
today; TRB is on Gate / OKX / KuCoin, not Bybit. Per coin: [out/current_universe_borrow.csv](out/current_universe_borrow.csv).

Rate to B's hold: at the 6 %/yr median a 24 h hold (B's maximum) costs 1.6 bp, so today's rates are not the issue;
availability and rate spikes in squeeze states are (B fires in exactly those). These are calm-day snapshots on
2026-11-01; Bybit / OKX / Gate rates float with utilisation, and no venue publishes 2022-24 borrow history.

## Spot tracking at B's VAL signals (2022-24)
Bars: venue spot 1h (open-time stamped, like Binance) for h-24 h .. exit around each VAL entry; Binance spot from
research/data/binance_basis/spot_1h. gap_h = ln(venue / Binance close) at the signal hour minus its median over the
previous 24 h (removes quote / scale differences). Shortfall = venue spot log return (entry open -> exit open) minus
Binance spot's: + means a venue short earns less than B's modelled Binance short.

| venue | VAL events with bars | hourly return corr | gap_h median / mean (bp) | shortfall mean / median / p10 / p90 (bp) | |shortfall| > 50 bp | venue / Binance quote volume |
|---|---|---|---|---|---|---|
| Bybit | 161 / 333 | 0.945 | -13.9 / -24.1 | +19.3 / +18.7 / -46.6 / +175.0 | 47 % | 0.021 |
| OKX | 146 / 333 | 0.972 | -12.0 / -27.3 | +45.4 / +17.1 / -22.0 / +153.7 | 38 % | 0.17 |
| KuCoin | 239 / 333 | 0.975 | -12.3 / -49.8 | +40.2 / +11.8 / -34.1 / +145.0 | 31 % | 0.039 |
| ex crash windows (2022-05, 2022-11) | Bybit 123 / OKX 136 / KuCoin 204 | | Bybit -16.9 / -43.2, OKX -10.2 / -25.8, KuCoin -12.0 / -42.8 (median / mean) | Bybit +49.9 / +24.9, OKX +46.0 / +16.9, KuCoin +38.2 / +12.7 (mean / median) | | |
corr(gap_h, shortfall): -0.88 Bybit, -0.43 OKX, -0.70 KuCoin: the richer Binance spot is versus the venue at the
signal, the more the venue short falls short. By year (shortfall median): Bybit 2022 +11 / 2023 +105 / 2024 +3,
OKX +7 / +36 / +7, KuCoin +12 / +25 / +2 bp; 2023 (TRB and squeeze coins) is worst, 2024 is small. Coins missing from
the venue APIs are mostly delisted ones (FTT, SRM, ANC, REN, OCEAN...), so the covered set is survivorship-biased
toward listed coins. Full numbers: [out/tracking.json](out/tracking.json), [out/robust_tracking.txt](out/robust_tracking.txt).

## What the user would have to open
- **Binance (preferred):** activate the Cross Margin account, transfer collateral into it, and check whether the
  account / sub-account / jurisdiction allows margin borrowing; then the demo's `maxBorrowable` and inventory checks
  (docs/basis-b-demo.md) will show real numbers. This keeps B exactly as registered.
- **Gate (fallback, widest coverage):** a verified account in unified account mode with borrowing enabled, USDT
  collateral there, plus the Binance account for the perp leg (capital split across two venues, transfers between
  them on a coin-squeeze day are slow).
- **Bybit (fallback):** a verified Unified Trading Account with spot margin switched on (margin is UTA-only), USDT
  collateral there.
- OKX (account mode with borrowing, e.g. spot-and-futures or multi-currency margin) and KuCoin (margin account; rates
  visible only with a key) add little coverage over Gate + Bybit. Region restrictions of each venue apply to the
  user's own jurisdiction and were not checked.
- Free improvement without any account: the paper bot could log, at each signal, Gate's public `loan_status`,
  per-user and platform caps and hourly rate, and Bybit's public No-VIP `borrowable` / `hourlyBorrowRate` /
  `maxBorrowingAmount`, plus each venue's spot price at entry and exit, to measure the tracking cost forward.

## Problems / pitfalls
- I read PREREG_B_cheap_basis.md as instructed; it contains the HOLD result section. None of those numbers is used
  here; the only B number quoted is the registered VAL net (+174.6 bp) for scale.
- Units: Bybit `hourlyBorrowRate` per hour, `maxBorrowingAmount` in coin; OKX basic `rate` read as daily (OKX's own
  borrowing endpoints describe the rate as daily, and USDT 0.0129 %/day = 4.7 %/yr is sensible; the docs page section
  could not be fetched in full); Gate history_loan_rate one point per hour (SDK docs), read as an hourly rate,
  `user_max_borrow_amount` in USDT (SDK docs). Caps are per-account tier limits, not live platform inventory (only Gate
  publishes a platform total).
- Gate 1h candles go back only 10,000 points, so Gate's spot tracking in 2022-24 cannot be checked at 1h.
- Delisted coins return "not supported symbol" on all venues: VAL tracking covers 44-72 % of events.

## Files and data
- Code: [code/fetch.py](code/fetch.py) (polite GET + log), [code/coins.py](code/coins.py) (B's coin lists, VAL
  entries), [code/pull_gate_rates.py](code/pull_gate_rates.py), [code/pull_klines.py](code/pull_klines.py),
  [code/coverage.py](code/coverage.py), [code/table.py](code/table.py), [code/tracking.py](code/tracking.py),
  [code/robust_tracking.py](code/robust_tracking.py). Outputs in [out/](out/): coverage.json,
  current_universe_borrow.csv, tracking.json, robust_tracking.txt, table.txt, pull_*.out.
- Data: research/data/margin_venues/{bybit,okx,gate,kucoin,binance,robots}/, requests.log: 562 requests 08:54-09:04
  UTC (547 x 200, 9 x 400 = key-required KuCoin endpoints and Gate's too-old candles, 4 x 404 robots, 1 x 403 Bitget
  robots, 1 network error retried), no 418 / 429. 2 WebSearch and 8 WebFetch doc reads (Bybit, OKX and Gate API
  docs / SDK docs on GitHub raw; these doc reads went through the WebFetch tool and are not in requests.log).
