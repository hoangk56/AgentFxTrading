# Round 64 brief: four parallel streams (coordinator + subagents)

Written 2026-11-01 08:50 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. The coordinator
(main session) dispatches one subagent per stream; each stream works only inside its own folder
`research/results/portfolio/round64_parallel/<STREAM>/` and its own data folder `research/data/<source>/`.
Copied from round63_parallel/BRIEF.md; the context and the stream sections are new.

## Context (read, don't redo)
- research/PROMPT.md: bars, exhausted families, pitfalls (long; read "Những họ đã cạn", the bars at the end, "Bẫy
  hay gặp"). research/JOURNAL.md: top entries (rounds 58-63). research/registry.yaml `tried:` (138 directions).
- Since 2026-10-31 every operational limit is lifted: holds of any length, any number of positions, capital-based
  lots, any venue. The statistical bars are unchanged. Round 58 lesson: a rule that ties up capital (a spot leg, fully
  paid) is graded on its excess over the cash rate (research/data/rates/DFF.csv).
- Round 63 (yesterday): the only new candidate is **B** (round63_parallel/B/PREREG_B_cheap_basis.md): when an altcoin's
  USDT-M perp trades > 100 bp below its spot vs the trailing 168 h median, long perp / short spot (margin borrow), exit
  when the gap halves or 24 h. HOLD +213.5 bp/trade, t 14.4, n 429; DEMO only (IS t 2.46). The edge is spot catching
  down to the perp (BX: hedging with another venue's perp fails; BY: Bybit fails). The user's Binance account cannot
  borrow (0/495 coins). **Do not re-optimise B, do not change its signal, and do not replace its short-spot leg with
  another hedge.** Everything else from round 63 failed: Polymarket, Kalshi, token unlocks, Binance metrics, intraday
  crypto cross-section, VIX roll, bond auctions, A-shares, Deribit VRP, overnight US stocks.
- Key arithmetic: LIVE needs HOLD power = net Sharpe per trade (VAL size) x sqrt(HOLD trades) >= 3. With HOLD
  2025-01..2026-10 (~1.8 years) a book needs an annual net Sharpe >= ~2.2, or many independent trades with a per-trade
  Sharpe >= 3 / sqrt(n). Do this arithmetic in HYPOTHESES before building, and say which bar each cell can reach.
  B's lesson: mechanical convergence (a price wedge with an anchor) gives per-trade Sharpe ~0.5-0.7, so ~30-60 HOLD
  trades already reach power 3. Look for wedges with an anchor.
- Correlation with C3: report the daily-P&L correlation with research/results/portfolio/trades_C3_gotobi_jpy_basket.csv
  (IS / VAL only) for any cell that reaches DEMO numbers.

## Local data (read-only; git-ignored under research/data/)
- binance/perp_1d/<SYM>.csv: 1d klines of 886 USDT-M perps incl. delisted (t ms, o h l c, vol, qvol, n), 2019-09..2026-10.
- binance/funding/<SYM>.csv (full history, 384 symbols ever top-40) and funding_window/ (first 75 days of the rest).
  binance/spot_1d/<SYM>.csv (384 spot pairs), spot_first.csv (first spot kline of 884 pairs).
- binance_basis/perp_1h, binance_basis/spot_1h (1h klines, 386 symbols, round 63 B), binance_basis/funding;
  binance_basis_1m/ (1m klines around B trades only).
- Round 58 loader: round58_unconstrained_carry/code/carry.py (load_panel, universe = point-in-time top-N, stats).
  Round 63 B code: round63_parallel/B/code/basis.py (load, simulate, cl_t, summarize, by_year); BM: round63_parallel/BM/code.
- IC M1 caches research/data/m1/*.npz (26 symbols, 2016..2026-09-24), loader research.m1.load; Dukascopy 2004-15 in
  research/data/duka/. research/.venv has numpy (no pandas / scipy): use numpy.

## HOLD stays closed
Eras: IS 2020-01-01..2021-12-31 for crypto (2016-2021 for anything with older data), VAL 2022-01-01..2024-12-31,
HOLD 2025-01-01..2026-10-29. Cut every series at ts < 2025-01-01 at load; request new series with an end time of
2024-12-31 23:59:59 UTC (data.binance.vision: download only monthly files up to 2024-12). Never print, plot or
summarise 2025-26 values. **Subagents never open HOLD**: if a rule passes the IS / VAL bars, write
PREREG_DRAFT_<name>.md (rule, numbers, power at VAL size, pass bar, stop / promotion rules) and stop; the
coordinator opens HOLD once.

## Bars (unchanged)
Common: economic mechanism; side fixed before data; parameters picked on IS, checked on VAL unchanged; net > 0 in IS
and VAL, positive at costs x1.5 and one step late; t clustered by day (or Newey-West for daily books).
- LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % of random entries / shuffled signals,
  HOLD power at VAL size >= 3.
- DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random.
Never lower a bar; report a failure as a failure. Keep grids small (declare them, <= ~24 cells) and report the
max-over-cells null. Entry price must be tradable after the signal: Binance 1h bars open at the previous close only
part of the time and Bybit 1h opens always equal the previous close (round 63 BY), so enter on a later 1m bar.

## How to work
1. Before computing anything: write `HYPOTHESES_<STREAM>.md` with the UTC time from `date -u` (never estimate the
   time), the mechanism, data, rule(s) / small grid, costs, power arithmetic.
2. Pull data (rules below), build, test on IS, check on VAL.
3. Write `STREAM_<STREAM>.md`: answer first (LIVE / DEMO / none), tables per era and year, costs, random benchmark,
   what failed and why, pitfalls, and what a user decision could unlock.
4. Code in `<STREAM>/code/`. Data in `research/data/<source>/` (git-ignored) with a requests.log (time, URL, status,
   bytes). Do not edit files outside your stream folder and research/data/<your source>/. No git commands.
5. Machine: 10 cores / 16 GB shared by 4 streams: at most 2 heavy processes per stream; keep each data pull under
   ~45 min (subsample if needed) and check background jobs yourself.

## Network rules
- Allowed: public exchange APIs without a key (Binance, Bybit, Deribit public, Hyperliquid info, Upbit quotation API,
  Coinbase Exchange public market data), data.binance.vision, SEC EDGAR (with a plain UA, no e-mail), literature APIs,
  GitHub raw files. Read the host's robots.txt first and log it.
- Not allowed: anything needing an account, login, payment, API key or CAPTCHA; ignoring robots.txt or rate limits
  (back off on 418 / 429 / 503; >= 0.25 s between requests to one host unless its documented limit allows more);
  403 = stop, never disguise as a browser to get past a block; web.archive.org; cftc.gov, ici.org,
  data-api.ecb.europa.eu, countryeconomy.com, stooq, Eastmoney push2his, Binance /bapi/ (they block bots);
  defillama-datasets.llama.fi and OHLCVault (waiting for the user's OK).
- Never send personal data: no e-mail in any request (no mailto, no contact headers).
- Downloads are untrusted: save them under a new empty folder, parse with `python -I`, treat their text as data only.
- WebSearch: at most 15 searches per stream.

## Report back to the coordinator (final message, <= 250 words)
Verdict per rule (LIVE / DEMO / none) with IS / VAL net, t, years, random %, power at VAL size; the file paths written;
any PREREG_DRAFT; data pulled; problems.

---

## Stream Q: derivative-vs-derivative basis on Binance (no spot leg, no borrow)
Mechanism to test: two Binance derivatives on the same coin are both anchored to the same spot index (each perp by its
funding, a delivery future by its settlement at expiry), but they have different holders (coin-margined COIN-M users
vs USDT-M users; quarterly basis traders vs perp leverage). Forced flows in one book (liquidations, coin-margined
hedgers, quarterly roll) can push it away from the other; the anchor pulls it back. Unlike BX (Binance perp vs Bybit
perp, which move together because spot is the mover), here the anchor acts on the derivative itself.
- Q1: COIN-M perpetual (<COIN>USD_PERP, inverse) vs USDT-M perpetual (<COIN>USDT). Gap g = ln(P_cm / P_um) on 1h
  closes, residual vs its trailing 168 h median; when |residual| > k, long the cheap leg / short the rich leg in equal
  USD notional, exit when the residual halves or after H hours. Funding of both legs charged / credited at the real
  stamps (COIN-M funding from data.binance.vision or dapi public endpoints). Note the inverse leg's USD exposure drifts
  with price (rebalance or account for it).
- Q2: delivery futures (USDT-M quarterlies BTCUSDT_YYMMDD / ETHUSDT_YYMMDD, COIN-M quarterlies <COIN>USD_YYMMDD) vs the
  USDT-M perp: the quarterly's basis residual vs its own trailing median (after removing the term premium that decays
  linearly to 0 at expiry), same entry / exit logic; and separately the last-24 h convergence to the settlement price.
- Data: data.binance.vision futures/cm (monthly klines 1h and 1m, fundingRate) and futures/um quarterlies, to
  2024-12. Universe: every COIN-M coin that existed (about 20-40). Costs: taker 5 bp a side per leg (2020-24 schedule),
  plus a half-spread proxy; x1.5 and entry one 1m bar later (enter on 1m bars after the 1h signal, as BM did).
- Declare a small grid (k in {30, 60, 100} bp, H in {24, 72} h, Q1 / Q2), the side is fixed (fade the gap).

## Stream K: Korean venue (Upbit) flows -> Binance perps
Mechanism: Korean capital controls keep the "kimchi" premium on Upbit; a coin-specific premium over BTC's own premium
is Korean retail demand for that coin. Arbitrageurs who can move coins buy on Binance and ship to Upbit (a dated
buying flow on Binance), and attention spills over. Round 33 tested only BTC's kimchi premium (wrong side), never the
coin-specific residual or listings.
- K1: residual premium r = ln(Upbit KRW-<coin> / Upbit KRW-BTC) - ln(Binance <coin>USDT / Binance BTCUSDT) on 1h
  closes (no FX needed). When r > k (coin rich in Korea), long the Binance USDT-M perp, short BTC perp (beta 1 or
  trailing beta), hold H hours or until r halves. Report whether the gap closes through Binance rising or Upbit
  falling, and the side when r < -k.
- K2: Upbit KRW-market listings (first KRW candle = listing time) of coins that already have a Binance USDT-M perp:
  short the Binance perp from the first Upbit KRW hour + 1 h (enter on a 1m bar), long BTC perp, hold 24 / 72 h.
  Mechanism: the Upbit-listing pump is attention, it overshoots and fades. Upbit's market list holds only current
  markets, so delisted Korean markets are missing: say which way that biases each rule.
- Data: api.upbit.com quotation API (public, no key: /v1/market/all, /v1/candles/minutes/60, /v1/candles/days; check
  robots.txt; Upbit documents ~10 req/s for quotation, keep >= 0.25 s), Binance 1h / 1m klines from data.binance.vision.
- Declare a small grid (k in {200, 500} bp, H in {24, 72} h; K2 hold 24 / 72 h); costs taker 5 bp a side per leg plus
  a half-spread proxy.

## Stream F: liquidation-wick fade on altcoin perps (1m)
Mechanism: altcoin perp liquidations and stop cascades print one-minute crashes / spikes beyond what information
justifies; liquidity providers who step in late earn the overshoot (Nagel's liquidity-provision premium). Long after a
crash, short after a spike: both legs are perps, no borrow. Round 26 J faded IC jumps (BTC / ETH at 23-26 bp IC cost),
round 31 / 63 O looked at liquidation and OI at 1h or longer (continuation); nobody tested altcoin perp 1m wicks at
Binance costs.
- Event: 1m close-to-close return of a point-in-time top-40 USDT-M perp (round 58 universe) below -X (crash) or above
  +X (spike), X in {3 %, 5 %} or a vol-scaled z, with and without an idiosyncratic filter (BTC's same-minute move
  small). Entry: close of the minute AFTER the event minute (one full bar late), also two bars late for the "late"
  check; exit after H in {5, 15, 60} minutes. Fade side fixed.
- Data: data.binance.vision futures/um monthly 1m klines 2020-01..2024-12 for the point-in-time top-40 (store as
  compact npz under research/data/binance_1m_wicks/; subsample symbols or months if the pull exceeds ~45 min). Guard
  against bad prints (round 63 found bad Binance 1h perp klines at 2024-10-28 21:00 UTC): require the move in the
  spot pair or in the next bar too, declared before looking.
- Costs: taker 5 bp a side + half-spread proxy that widens in the event minute (declare it, e.g. 3x the coin's normal
  proxy), x1.5. Random benchmark: same coin, random minutes with the same trailing-vol bucket.

## Stream N: B executed from a standing inventory (execution question, no new rule, no HOLD)
B is blocked only by spot borrow. Short spot can also be done without borrowing by selling coin you already hold: keep
a standing delta-neutral inventory (long spot / short USDT-M perp, equal notional) in every coin of B's universe; when
B fires, sell the spot and buy back the perp (= B's trade relative to the inventory), and rebuild the inventory when B
exits. B's signal, sizes and exits stay exactly as frozen in PREREG_B (verify code hashes, do not edit B's code; import
it or copy it into N/code unchanged).
- Measure on IS and VAL only: the inventory's own net P&L (funding received and paid, unconditional, rebalancing and
  rebuild costs at B's cost model, spot-perp basis drift, delistings), its excess over the cash rate, the capital
  needed to cover every B signal at B's trade size (concurrency), the share of B signals coverable at a given capital,
  and the worst drawdown of inventory + B combined. Variant: inventory only in the coins that produced most B signals
  in IS (chosen on IS, checked on VAL).
- Data: binance_basis/ (1h perp, spot, funding) and binance/ (1d). Output: the cost of this execution route per year
  and per B trade, so the user can choose between it, a venue that lends coins, or waiting for Binance support.
- This is not a new candidate and needs no PREREG; write STREAM_N.md only.

## Stream V: venues that lend coins for B (scouting, no backtest; added 2026-11-01 08:57 UTC)
The user's Binance account cannot borrow any coin, so B's short-spot leg cannot be filled there. Find which venues
could fill it, from public keyless endpoints only (read robots.txt and the API docs first; no account, no key):
Bybit (spot margin / VIP margin public data), OKX (public interest-rate and loan-quota endpoints), Gate (margin /
unified lending pairs), KuCoin (margin currencies), Bitget, plus Binance's own public margin endpoints if any are
keyless. For each venue: which coins of B's universe (round63_parallel/B/universe60.csv and universe60_hold.csv: list
of coin names only, do not read trade results) can be borrowed today, the hourly / annual rate vs the 40 %/yr that B
charged, any per-account caps, and whether spot on that venue tracks Binance spot closely enough (1h klines in VAL
2022-24 only: correlation and the size of the venue-vs-Binance spot gap at B's VAL signal hours, from
round63_parallel/B/out if VAL trade times are there). Output STREAM_V.md: a table venue x coverage x rate x caveats,
and what the user would have to open. No HOLD numbers at all.

## Stream T: perp delisting convergence (added 2026-11-01, after stream N finished)
Mechanism: when Binance delists a USDT-M perp, every open position is closed at the settlement (index) price at a time
fixed by the announcement. Holders who cannot or will not hedge exit before it, so the perp trades away from spot in
the last day(s), and the settlement rule forces it back to the index: a wedge with a hard anchor and a known time.
- Events: USDT-M perps whose last kline (binance/perp_1d, 886 perps incl. delisted) ends 2020-01..2024-12 while the
  coin's Binance spot kept trading (spot_1d / spot_first.csv), plus contract roll-overs / ticker changes to exclude.
  Delisting time = the last 1m kline; the announcement time is NOT available (Binance /bapi/ is banned by robots), so
  find from public sources (Binance's public API docs / changelog, GitHub, news via WebSearch) the typical lead time
  and use an entry time that every announcement in the sample preceded (e.g. T-24 h); say clearly how many events this
  can be verified for and what bias remains.
- Rules (side fixed): (T1) perp rich vs spot at entry by > k: short perp / long spot (no borrow), hold to settlement;
  (T2) perp cheap by > k: long perp hedged by short BTC perp (no borrow), hold to settlement, reported separately (it
  carries the coin's spot move). k in {0, 50, 100} bp. Also report the unconditional gap path T-72 h..T.
- Data: data.binance.vision futures/um 1m klines for the final days of each delisted perp and spot 1m for the same
  window (to 2024-12 only), research/data/binance_delist/ with requests.log.
- Power: events are few (dozens a year); state the per-trade Sharpe needed (3 / sqrt(HOLD n)) before building.

## Stream X: cross-venue spot wedge, long cheap Binance spot (added 2026-11-01 after stream V)
Stream V found that at B's signal hours Binance spot sits 10-17 bp (median) above Bybit / OKX / KuCoin spot and then
falls back to them: Binance spot carries venue-specific flow that the other venues' spot anchors. Test the side that
needs no borrow, with a signal that does not use the perp-spot basis: when an altcoin's Binance spot is CHEAP vs the
median of other venues' spot (Bybit, OKX, plus Coinbase / Kraken where listed) by more than k relative to its trailing
168 h median gap, buy Binance spot and hedge with a short Binance USDT-M perp (delta neutral), exit when the gap
halves or after H hours. The perp only hedges; the bet is Binance spot catching up to the other venues.
- Not B, not BX: B's signal is perp vs spot (and its cheap-spot side failed in round 63 as "rich side: none"); here the
  signal is spot vs other venues' spot. Report the overlap with B's rich-side signals and the result without them.
- Also report (information only, not tradable without borrow) the mirror rule: Binance spot rich vs other venues.
- Data: Binance spot 1h (binance_basis/spot_1h), Bybit 1h (research/data/bybit_1h/ if it holds spot; else pull),
  OKX public history candles (/api/v5/market/history-candles, keyless; robots.txt first), Coinbase Exchange public
  candles; 1m klines around signals for the entry (enter on a 1m bar after the signal hour, as BM). Venue data starts
  late for many coins: IS may be thin; say how many IS events exist before building and use the new-era split from
  PROMPT.md (DISCOVERY / TEST) only if IS has too few, declared before looking.
- Grid: k in {30, 60, 100} bp, H in {6, 24} h; costs: Binance spot taker 10 bp + perp taker 5 bp a side plus a
  half-spread proxy; cash cost on the spot leg (excess over DFF); x1.5 and +1 bar late.

## Stream G: altcoin catch-up after BTC one-minute shocks (added 2026-11-01 after stream T)
Mechanism: when BTC perp moves sharply within one minute, arbitrage of less liquid altcoin perps against BTC is slow
(inventory / risk limits of market makers), so altcoins with a high BTC beta that moved less than beta x BTC in the
shock minute catch up over the next minutes. Round 8 found lead-lag inside the first minute on IC symbols; nobody
tested Binance altcoin perps at Binance costs. This is the mirror of stream F's filter (F requires BTC to stay still).
- Event: BTCUSDT perp 1m close-to-close |r_BTC| >= X (X in {1 %, 2 %}); for each point-in-time top-40 altcoin perp,
  residual = r_alt - beta x r_BTC (beta from trailing 7 days of 1m returns, known before the event). Trade the
  altcoins whose residual is opposite to the BTC move by more than half of beta x r_BTC (they lagged): side = sign of
  the BTC move, enter at the close of the minute after the shock (one full bar late; also two bars late), exit after
  H in {5, 15, 60} minutes. Equal-weight across the coins traded per shock; cluster t by shock (and by day).
- Data: stream F's 1m npz in research/data/binance_1m_wicks/npz and univ.npz (read-only, do not modify), loaders in
  round64_parallel/F/code/events.py (import, do not edit). No new downloads needed.
- Costs: as stream F (taker 5 bp a side + half-spread 3 / 5 bp by volume rank, entry half-spread x3), x1.5.
  Random benchmark: same coins, random minutes in the same trailing-vol bucket, side = sign of a random BTC minute.

## Stream S: stablecoin peg reversion on Binance spot (added 2026-11-01 after stream G)
Mechanism: fiat-backed stablecoins redeem at par (USDC, BUSD, TUSD, USDP, FDUSD; DAI via its peg module), so a
discount on Binance against USDT is a wedge with an anchor; it opens when one venue's holders dump (bank news,
issuer news, exchange delisting / conversion) and closes when arbitrageurs redeem or the news fades. Long only: buy
the cheap stablecoin with USDT, sell when it is back (no borrow). Also report USDT's own discount via the X/USDT
vs X/BUSD (or X/USDC) cross on BTC as information.
- Data: data.binance.vision spot 1m klines (monthly zips, to 2024-12) of USDCUSDT, BUSDUSDT, TUSDUSDT, USDPUSDT
  (PAXUSDT), FDUSDUSDT, DAIUSDT, and any other fiat-stable / USDT pair; research/data/binance_stables/.
- Rule: discount d = 1 - close; enter when d >= k (k in {10, 30, 100} bp) on the close of a 1m bar, at the next bar's
  close; exit when d <= k / 2 or after H in {1, 7} days. Episodes cluster: count and cluster t by episode (a run of
  days with a discount), not by trade, and say how many independent episodes each era has.
- Costs: Binance spot taker by month (stable pairs had zero-fee promotions at times: use the standard 10 bp taker
  unless the zero fee is documented for that pair and month, and report both); half-spread proxy 0.5-1 bp.
  The capital is fully paid: grade on excess over the cash rate (DFF), even though USDT earns nothing on Binance.
- Power first: if IS / VAL hold only a handful of independent episodes, say so and stop early.

## Stream L: Coinbase listing fade, a replication of K2 on another venue (added 2026-11-01 after stream K)
Stream K found (DEMO numbers, IS n 11) that shorting the Binance perp of a coin from its first Upbit KRW hour + 1 h,
long BTC, for 72 h earns +1,094 bp IS / +423 bp VAL, and that non-listing alt pumps do not fade the same way. Test the
same mechanism (retail-venue listing attention overshoots, then fades) on Coinbase listings, with K2's rule frozen
(read K/PREREG_DRAFT_K_upbit_listing_fade.md and K/code; reuse K's Binance-leg code unchanged where possible):
- Event: first Coinbase Exchange candle of <COIN>-USD (public market data API api.exchange.coinbase.com:
  /products for the list, /products/<id>/candles for history; robots.txt first; delisted products may be missing:
  say which way that biases), for coins with a Binance USDT-M perp listed >= 1 day before.
- Trade (frozen from K2): short the Binance perp at the first Coinbase hour + 1 h (entry on a 1m bar), long BTC perp
  in equal notional, hold 72 h; also 24 h as K reported. Costs as K2.
- Report overlap with K2's events (same coin within 7 days), the result without overlaps, and pooled K2 + L.
