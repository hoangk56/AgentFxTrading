# Basis B demo (paper)

Forward test of research rule B `k100_H24_cheap`, the altcoin perp-discount basis reversion. The rule is registered in
`research/results/portfolio/round63_parallel/B/PREREG_B_cheap_basis.md` and passed its HOLD at the DEMO tier. The demo
**sends no order**. Each hour it records one paper trade per signal, together with what a real trade would have met:
the Binance book, and whether the coin could be borrowed for the spot short and at what rate. Spot borrow is the one
risk the research could not measure.

## Code
- `app/basis_b.py`: the rule as pure functions (universe ranking, basis, 168-hour median, event, exit, book walk,
  net). The constants match the research code (`round63_parallel/B/code/universe.py`, `basis.py`).
- `app/basis_b_runner.py`: the Binance REST client and the hourly `tick`. It also has `check`, which probes the
  endpoints, and `status`.
- `app/basis_b_store.py`: the tables `basis_b_universe`, `basis_b_trades` and `basis_b_runs`.
- `app/basis_b_status.py`: the stop and promotion status shown on the Nghiên cứu screen (`docs/research-screen.md`).

## Hourly tick
Cron on the VPS (`/etc/cron.d/agentfx-basis-b`):

    0,5,10 * * * * forge cd /home/forge/AgentFxTrading && /usr/bin/flock -n /tmp/basis_b.lock .venv/bin/python -m app.basis_b_runner tick >> logs/basis_b.log 2>&1

A finished hour is not redone. The :05 and :10 runs only retry an hour that failed. Each tick does the following:

1. Loads the universe for the day of the bar that just closed. If it is missing (first run), builds it. That takes
   about 350 daily-kline requests, a few minutes.
2. For each universe coin, and each coin with an open trade, takes 200 hourly perp and spot klines.
3. Closes the open trades whose exit is now known.
4. Opens a paper trade for every new event, at the open of the current hour.
5. Builds today's universe after 00:00 UTC.

## What each trade records
- **Registered net.** Opens of the entry and exit bars, 30 bp fees, 4 x half-spread, borrow 40 %/yr and cash rate,
  plus funding on stamps in (entry, exit]. This is the research's own arithmetic, comparable with HOLD.
- **Book net.** The 20-level book walked for `BASIS_B_NOTIONAL` USDT per leg (default 1,000): buy perp and sell spot
  at entry, the reverse at exit. Fees are 30 bp. Borrow is the measured hourly rate averaged over the hold, or 40 %/yr
  when it was not measured. An exit recorded late (missed runs) uses the book at the time it is recorded and says so
  in `exit_reason`.
- **Borrow facts.**
  - `isMarginTradingAllowed` of the spot pair (public).
  - `isBorrowable` of the asset (`/sapi/v1/margin/allAssets`, API key).
  - The system's available inventory (`/sapi/v1/margin/available-inventory`, signed).
  - The next hourly rate (`/sapi/v1/margin/next-hourly-interest-rate`, signed), logged again every hour while the
    trade is open.
  - The account's `maxBorrowable` (signed; informational, since it depends on the account's collateral).
- **Fillable.** 0 if the asset or pair is not borrowable on margin. 1 or 0 by whether the inventory covers the
  quantity. The inventory comes back empty for an account without margin assets (seen 2026-11-01); then a positive
  `maxBorrowable` decides instead. Unknown (NULL) when neither gives a number (no secret, or no collateral in the
  cross-margin account).

## Status (registered rules plus the choices this code adds)
- **Stop** after 40 closed signals, if the cumulative net is < 0, or if more than 30 % of the signals with known
  borrow are not fillable. A not-fillable signal counts as 0.
- **PROMOTE_CHECK** once 40 signals have closed, no stop has fired, every signal's borrow is known, and HOLD plus demo
  pooled t >= 2.5. The PREREG gives no minimum count. HOLD alone has t 14, so the promotion is read together with the
  stop. PROMOTE_CHECK is not a promotion: the user decides.
- A demo signal's net is the book net, or the registered net when the book exit is missing.

## Differences from the research code
- The relative tick is `tickSize / last close` from exchangeInfo. Research inferred it from 30 days of prices.
- Listing age uses the perp's `onboardDate`. Research used its first daily kline.
- Only perps and spot pairs that are `TRADING` today can enter the universe.
- Entry is a few seconds after the open (`BASIS_B_START_DELAY`, default 3 s). The registered net still uses the bar's
  open.

## Environment
- `BINANCE_API_KEY` and `BINANCE_API_SECRET` (HMAC). Read permission is enough; never enable trading or withdrawals
  for this demo. Without the secret, trades are recorded with borrow unknown.
- `BASIS_B_NOTIONAL` (default 1000).
- `BASIS_B_CASH_RATE` (default 0.0388, Fed funds 2026-10-01).

Check with `python -m app.basis_b_runner check`. It prints which endpoints work and never prints the key or the
secret.
