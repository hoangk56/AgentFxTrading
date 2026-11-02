# Stream V hypotheses: venues that lend coins for B's short-spot leg (round 64, scouting)

Written 2026-11-01 08:53 UTC (from `date -u`), before any venue endpoint was requested. Scouting, not a backtest: B's
rule, signal and costs stay frozen (round63_parallel/B/PREREG_B_cheap_basis.md); nothing here grades B. No HOLD
(2025-26) numbers are read or produced; the coin names in universe60_hold.csv are used as a list only.

## Question
B shorts Binance spot (margin borrow) while long the Binance USDT-M perp. The user's Binance account cannot borrow
(0 / 495 coins). Which venue could hold the short-spot leg instead, so that the trade is: long Binance perp (signal on
Binance basis, unchanged) / short spot on venue X? That works only if (1) X lends the coin, (2) at a rate near the
40 %/yr B charged, (3) in a size that covers B's trade notional, and (4) X's spot moves like Binance spot over B's hold
(B's P&L is spot catching down to the perp, BX: another venue's perp does not, so X's spot must catch down too).

## Venues and public, keyless endpoints to try (docs and robots.txt read first)
- Bybit (api.bybit.com): spot-margin VIP data (borrowable coins, hourly rate, max borrow per VIP level), spot
  instruments, spot 1h klines (VAL).
- OKX (www.okx.com): public interest-rate / loan-quota (basic and VIP), MARGIN instruments, lending-rate summary,
  spot history candles (VAL).
- Gate (api.gateio.ws): margin / unified lending currency pairs, lending currencies and rates, spot candlesticks.
- KuCoin (api.kucoin.com): margin config / cross and isolated margin symbols, lending market (project list and
  market interest rate), spot candles.
- Bitget (api.bitget.com): margin currencies, any public interest-rate endpoint, spot candles.
- Binance (api.binance.com): exchangeInfo `isMarginTradingAllowed` (public); /sapi margin endpoints need a key, so
  only listed as "needs key" (not called). /bapi is not allowed.
If an endpoint needs a key or returns 403, it is recorded as unavailable, never worked around.

## Checks (declared before data)
1. Coverage: share of B's coins borrowable on X today, for (a) the current universe = coins in universe60_hold.csv
   whose membership window reaches the last month of the file (the coins the demo bot trades), and (b) all names in
   universe60.csv + universe60_hold.csv. Symbol map: strip the 1000 / 1000000 prefix (1000PEPE -> PEPE), spot name
   from the CSV's spot column.
2. Rate: hourly / annual borrow rate per coin for the lowest (no-VIP) tier, median and share <= 40 %/yr, and the
   rate implied for B's mean hold (~4-5 h: rate x hours / 8760 in bp).
3. Caps: per-account / per-tier max borrow in coin and USD (USD via the venue's own last price), and whether it covers
   B's demo notional (1,000 USDT per leg) and a 10,000 USDT leg.
4. Spot tracking (VAL 2022-24 only, every series cut at ts < 2025-01-01; requests with end time <= 2024-12-31
   23:59:59 UTC): for the 333 VAL entries of B's frozen cell (BX/out/events.csv lag 0, signal hour h, entry e, exit x),
   pull X's spot 1h klines around each event and compare with Binance spot (research/data/binance_basis/spot_1h):
   - correlation of hourly log returns X vs Binance over the event windows (h-24 h .. x);
   - the X-vs-Binance spot gap at the signal close h, as ln(X / Binance) minus its median over h-24..h-1 (removes
     USD / USDT and scale differences), median and p10 / p90 in bp;
   - tracking of the short leg over the hold: (X spot return e -> x) - (Binance spot return e -> x), mean, median,
     p10 / p90 in bp, and the share of B's VAL events where X had a bar at e and x (coverage in 2022-24).
   No B P&L is computed; this says whether a short on X would have captured Binance spot's move.
5. What the user must open per venue (account type, KYC tier, region limits as stated in public docs / help pages).

## Decision rule for the recommendation (declared)
A venue "could fill B" if: current-universe coverage >= 70 %, median no-VIP rate <= 40 %/yr (or <= 100 %/yr with the
cost per B hold < 5 bp), cap >= 1,000 USDT for >= 70 % of covered coins, and VAL hold-tracking median |diff| < 25 bp
with the tracking mean within +/- 25 bp (a bias against B larger than ~1/6 of B's VAL net would matter). These are
scouting thresholds, not research bars; the coordinator / user decides.

## Network and data
Requests logged in research/data/margin_venues/requests.log (UTC time, URL, status, bytes); bodies under
research/data/margin_venues/<venue>/; parsing with `python -I`; >= 0.3 s between requests to one host; back off on
418 / 429 / 503; 403 = stop that host; plain UA without any e-mail; no account, login or key. At most 15 WebSearch.
Power arithmetic: not applicable (no rule is graded; the stream changes no bar).
