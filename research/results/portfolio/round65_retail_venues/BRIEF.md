# Round 65 brief: retail-venue attention (coordinator + subagents)

Written 2026-11-01 10:36 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. The coordinator
(main session) dispatches one subagent per stream; each stream works only inside its own folder
`research/results/portfolio/round65_retail_venues/<STREAM>/` and its own data folder `research/data/<source>/`.
Copied from round64_parallel/BRIEF.md; context and streams are new.

## Context (read, don't redo)
- research/PROMPT.md: bars, exhausted families, pitfalls. research/JOURNAL.md top entries. registry.yaml `tried:`.
- No operational limits since 2026-10-31 (any hold, any count, capital-based lots, any venue); bars unchanged.
- Round 64 (today), round64_parallel/: F (fade 5 % idiosyncratic 1m wicks on altcoin perps) passed every LIVE bar on
  IS / VAL (+273 / +271 bp, t 4.05 / 3.76) but FAILED HOLD (+42 bp, t 1.17): the edge decayed to ~15 % of VAL size.
  **K2** (round64_parallel/K/PREREG_K2_upbit_listing_fade.md: short the Binance perp from the first Upbit KRW hour +
  1 h, long BTC, 72 h) passed HOLD as DEMO (+221 bp, t 0.88, n 92; price leg +775, funding -512). L (the same rule on
  Coinbase listings) failed: no pump before entry. K1 (coin-specific kimchi premium) failed: the gap closes on Upbit.
  Q1 (COIN-M vs USDT-M perp gap) is a crash-day rule. N, V, X, T, G, S: none (inventory route for B too costly; other
  venues lend B's coins but their spot misses the move; cross-venue spot wedge loses the cost; delisting perps sit on
  spot; altcoin catch-up after BTC shocks below cost; stablecoin peg only the SVB week).
- Lesson: IS / VAL strength of crypto microstructure edges does not survive 2025-26 unless the mechanism is a
  behavioural flow that keeps coming (K2: Korean retail chasing new KRW listings). This round asks whether that
  mechanism generalises across retail venues, to grow the number of independent HOLD-era events (K2's power ~1).
- Key arithmetic: LIVE needs HOLD power = net Sharpe per trade (VAL size) x sqrt(HOLD trades) >= 3. K2's VAL Sharpe per
  trade is 0.25, so ~150 HOLD events at that size are needed; DEMO needs IS t >= 2.0, VAL net > 0.
- Correlation with C3 (trades_C3_gotobi_jpy_basket.csv) for any cell with DEMO numbers.

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


## Stream H: Bithumb KRW listings, K2's rule frozen (replication on a second Korean venue)
- Event: a coin's first Bithumb KRW candle (public API api.bithumb.com; read robots.txt and the docs; candlestick
  endpoint `/public/candlestick/<COIN>_KRW/<interval>` or the v1 API `/v1/candles/...`; say how far history goes and
  whether delisted markets are visible), for coins whose Binance USDT-M perp was listed >= 7 days before.
- Trade: K2 exactly (read round64_parallel/K/PREREG_K2_upbit_listing_fade.md and K/coord/hold/k2rule.py; import
  k2rule.trade unchanged: it prices both legs from public fapi 1m klines): short alt perp, long BTC perp at L + 1 h,
  hold 72 h, 42 bp + real funding. IS 2020-21, VAL 2022-24 only (L < 2024-12-28).
- Report: overlap with Upbit events (same coin within 7 days: Bithumb-first vs Upbit-first), the result on
  Bithumb-only events, and the pump before entry (+21.5 % on Upbit). No HOLD.

## Stream U: Korean retail rush without a listing (Upbit KRW volume-share shocks)
Mechanism as K2 (Korean retail attention overshoots and fades), but on existing KRW markets: when an altcoin's Upbit
KRW traded value over the last 24 h jumps to a large share of its Binance perp quote volume (vs its own trailing
30-day share), Korean retail is chasing it. Stream K's post-hoc control showed that shorting generic alt pumps loses,
so the test is whether the Korean share adds what a price pump alone does not.
- Data: stream K's Upbit 240-minute candles (research/data/upbit/m240, KRW value column; read-only) and Binance perp
  volume / 1h closes (local files listed in K's kdata.py); no new Upbit pull needed. Cut at ts < 2025-01-01.
- Rule (declare the grid before computing, <= 12 cells): share z or ratio thresholds x {with / without a price run-up
  filter}, short alt perp / long BTC perp at the next 4h boundary + 1 h on a 1m bar (fapi via k2rule.px), hold 24 / 72 h,
  costs as K2. Exclude coins within 30 days of their KRW listing (that is K2). One event per coin per 7 days.
- Random benchmark: same coins at random 4h boundaries; and generic pumps of the same size without the Korean share.

## Stream I: scout retail venues with dated listings (no backtest)
For each retail-heavy spot venue with a public, keyless candle API, check robots.txt and docs, whether history reaches
2020-24, whether a market's first candle (= listing time) is visible, whether delisted markets are visible, and the
number of listings 2020-24 of coins that already had a Binance perp. Candidates: Bithumb (stream H does it; skip),
Coinone, Korbit (Korea), bitFlyer, Coincheck, bitbank (Japan), BtcTurk, Paribu (Turkey), Bitkub (Thailand), Indodax
(Indonesia), WazirX / CoinDCX (India), Bitvavo (EU), Mercado Bitcoin (Brazil), plus anything a search turns up. Rank by
"usable independent events per year", estimate the pre-entry pump size from 3-5 example listings per venue (1h candles
around L only, ts < 2025-01-01), and write which venues a K2-style test could use. One request per endpoint check;
log every request. Output STREAM_I.md (table + ranking).

## Stream W: Upbit investment-warning / delisting notices -> Binance perp (added 2026-11-01 after stream I)
Mechanism: the mirror of K2. When Upbit designates a coin "투자유의 종목" (investment warning) or announces the end of
KRW trading support, Korean retail holders must sell before the deadline, a dated forced flow on one venue that spills
into the global price. Short the Binance USDT-M perp, long BTC perp in equal notional.
- Data: the time of each notice, 2020-24. Try only public sources that allow it: Upbit's notice / announcement API used
  by its own web pages (read robots.txt of the host first; if disallowed or 403, stop), Upbit's market list of
  `market_warning` (current only, not usable for history), news archives via WebSearch for a sample to check times.
  If no point-in-time notice history is reachable, write that and stop (do not scrape disallowed paths).
- Rule (if data exist; declare before computing): enter at notice time + 1 h on a 1m bar (k2rule.px, copied with
  your own log folder), hold 24 / 72 h and to the delisting date, costs as K2 (42 bp + funding). Events: coins with a
  Binance perp at the notice. Report warning designations and delisting notices separately and the overlap with
  Binance's own delistings (round 64 T).

## Stream J: scout the next wave (no backtest; added 2026-11-01 after stream H)
Round 64-65 showed that only persistent behavioural / institutional flows with a dated timing survive into 2025-26
(C3 gotobi: Japanese corporate settlement at the Tokyo fix; K2: Upbit-specific listing chase; Bithumb, Coinbase and
seven other retail venues do not pump). Produce the next wave: 8-12 concrete hypotheses, each testable by one stream
with free point-in-time data 2016-24 (crypto 2020-24) and a venue the user could trade (any venue is allowed now).
- Each hypothesis: who is forced to trade, when (calendar / rule), which side, the instrument, the free data source
  (checked reachable with one logged request, robots.txt first), events per year, HOLD power at a plausible size,
  and why it is not one of the 146 tried directions in research/registry.yaml (`tried:`) or the exhausted families in
  research/PROMPT.md. Gotobi-like settlement flows in other countries / currencies, rule-based fund flows with public
  schedules, exchange rule events, and venue-specific retail behaviour are in scope; generic price patterns are not.
- Rank by P(LIVE) and P(DEMO). Output STREAM_J.md (ranked table + one section per hypothesis). At most 15 WebSearch
  (literature 2023-26 welcome, but note HOLD contamination when a source uses 2025-26 data).

## Stream A: chase the Upbit KRW-listing announcement on Binance perps (added 2026-11-01 after stream W)
Stream W found Upbit's own notice JSON (api-manager.upbit.com/api/v1/announcements, robots.txt without rules; data in
research/data/upbit_notices/, read-only) with the original post time `first_listed_at` from 2017-10. K2 shows the
alt pumps +21.5 % vs BTC between L - 24 h and L + 1 h (L = first KRW candle). The announcement is the start of that
flow: Korean retail buys on Upbit when trading opens, arbitrageurs pre-buy on Binance.
- Events: KRW-market listing notices 2020-24 (parse the notice body for the markets; exclude BTC-market-only and
  re-listings) for coins with a Binance USDT-M perp listed >= 7 days before the notice. Report the lag notice -> L.
- Rule (side fixed long alt perp / short BTC perp, equal notional; declare <= 8 cells before computing): entry at
  notice + {1, 5, 15} min on a 1m bar (copy K's k2rule.py into A/code with the log folder pointed to
  research/data/upbit_announce/), exit at L (first KRW candle open) or L + 1 h; costs 42 bp + funding as K2. The
  1 min cell is a latency race: say so and require the 5 / 15 min cells to carry the result.
- IS has few events (K2 had 11): compute the power first and say which bar is reachable; also report the chained
  book "A then K2" (long into L + 1 h, then K2's short) as information only, since K2 is already registered.

## Stream C: Hong Kong CBBC mandatory-call clusters -> HK50 (added 2026-11-01 after stream J; J/STREAM_J.md J1)
Forced flow: issuers hedge bull / bear CBBCs sold to HK retail in HSI futures; when the index trades through a call
price the CBBC is called (rule-based) and the issuer unwinds its hedge within minutes. A dense band of call levels
just beyond the price means a predictable burst of hedge unwinding in the direction of the break.
- Step 1 (stop if it fails): find a free point-in-time history 2016-24 of CBBC call levels and issue / outstanding
  size (HKEX CBBC daily full lists or launch / MCE notices on hkexnews; robots.txt first; the Mac's DNS maps
  hkex.com.hk to 127.0.0.1, so fetch through `ssh agentFx` with curl and copy the bodies back, logging each request;
  keep it under ~45 min and polite: >= 1 s between requests). If only current lists exist, write that and stop.
- Step 2 (declare before computing): density of outstanding notional per index point beyond the price (from data
  known before the day); when HK50 (local IC M1 cache, research.m1) breaks into a band above a threshold, trade with
  the break from the next minute for 15 / 30 min; cluster t by day; costs at IC HK50 spread (round 28-29 models).
  IS 2016-21, VAL 2022-24. Random benchmark: same-size breaks without a dense band.

## Stream R: Korean waking-hours rhythm on Upbit-heavy altcoins (added 2026-11-01 after stream U)
Mechanism: Korean retail trades during Korean waking hours (09:00-24:00 KST = 00:00-15:00 UTC) and is absent at night.
If its buying pressure lifts the coins it dominates during the day and the global market (other hours, other venues)
pulls them back at night, then coins with a high Upbit share of global volume have an intraday rhythm that coins with a
low share do not. Stream U looked at shocks in that share; nobody tested the daily rhythm (round 63 C's intraday
cross-section did not condition on venue share; rounds 3 / 11 scanned clocks on IC symbols only).
- Data: stream K's Upbit 240-minute candles (research/data/upbit/m240, KRW value; read-only), local Binance perp 1h
  closes and quote volume (files listed in round64_parallel/K/code/kdata.py; read columns by header name, stream U
  found mixed layouts), funding. Cut at ts < 2025-01-01.
- Share = Upbit KRW value (converted with Upbit KRW-BTC / Binance BTCUSDT) / Binance perp quote volume over the
  trailing 30 days, known before the day. Book (declare <= 8 cells before computing): each day, long the low-share
  tercile / short the high-share tercile (or short high-share vs BTC) of the point-in-time top-60 perps over the Korean
  night 15:00-24:00 UTC, and / or the mirror over the Korean day; equal weight; costs taker 5 bp a side per leg + the
  half-spread model of round 63 C; Newey-West t on the daily book. Report the gross rhythm by hour first (IS only),
  then the declared books on IS and VAL; random benchmark: shuffled share ranks.

## Stream M: Upbit non-KRW market additions, K2's rule frozen (added 2026-11-01 after stream C; J/STREAM_J.md J2)
Does the Upbit listing chase also appear when Upbit adds a coin to its BTC or USDT market (no KRW pair yet)? Events
from stream W's notice data (research/data/upbit_notices/, read-only; J counted 32 non-KRW additions in 2020-24),
time = the first BTC- / USDT-market candle (Upbit candles API) or the notice time + the stated opening time; coins with
a Binance USDT-M perp listed >= 7 days before. Trade exactly as K2 (copy k2rule.py with your own log folder
research/data/upbit_nonkrw/): short alt perp / long BTC perp at L + 1 h, 72 h, 42 bp + funding. Report the pump before
entry (K2: +21.5 %), and separately the 9 KRW listings that J found in the notices but not in K's event list (coins
later delisted from Upbit: survivorship check of K2 in IS / VAL only). No HOLD.

## Stream E: Hong Kong leveraged / inverse ETF close rebalancing -> HK50 (added 2026-11-01 after stream R; J4)
Round 34 tested ProShares leveraged-ETF doses on US indices, metals, energy, VIX and JP225 (only gold had an effect at
settlement). Hong Kong was never tested: CSOP / Samsung / Mirae 2x and -2x products on HSI and HSTECH must buy or sell
futures into the 16:00-16:10 closing auction in the direction of the day's move (dose = leverage x (leverage - 1) x
AUM x return). Read round34_china_etf_options_2026-10-28.md and its stream file on ETF doses first.
- Data: issuer AUM / units history (public fund pages or HKEX ETF statistics; robots.txt first; the Mac maps
  hkex.com.hk to 127.0.0.1, so use `ssh agentFx curl` with logging, nothing left on the VPS) for 2016-24; if missing,
  the sign-only rule (the day's move to 15:45 HKT) stays testable. HK50 from the local IC M1 cache (research.m1),
  cut at ts < 2025-01-01. IS 2016-21, VAL 2022-24.
- Rule (declare <= 8 cells before computing): days with |return to 15:45 HKT| in the top decile (or dose >= threshold),
  trade with the day's direction from 15:45 / 15:50 to the close (16:00) or into the auction / after-hours, at IC HK50
  costs (spread at those minutes from the cache); cluster t by day; random benchmark: same-size days, other minutes.

## Stream A2: seconds after the Upbit listing notice (added 2026-11-01 after stream A)
Stream A found the alt rises +1,524 bp (IS) / +1,953 bp (VAL) vs BTC on the Binance perp inside the notice minute,
in 100 % of events, and almost nothing after N + 1 min. The open question is execution, not the effect: how much is
left a few seconds after the notice's own timestamp, i.e. could a bot that polls Upbit's notice API catch it.
- First check the precision of `first_listed_at` (seconds? milliseconds? is it the post time or a scheduled time) on
  stream A's events (A/notice_events*.csv, research/data/upbit_notices/, read-only), and how it compares with the
  first Binance aggTrade burst (if the burst precedes the stamp, the stamp is late or the news leaks: report it).
- Data: data.binance.vision futures/um daily aggTrades for the event days of the alt and BTCUSDT (IS 2020-21 and VAL
  2022-24 only; the zips are large: extract only N - 10 min .. N + 30 min and delete the zip), research/data/upbit_latency/.
- Rule (declare before computing): long alt perp / short BTC perp at the first trade after N + d seconds, d in
  {2, 5, 10, 30}, taker fill at that trade price + a declared slippage (half the median 1 s range), exit at N + 5 min
  and at L (first KRW candle). Costs 20 bp + slippage. Report the price path N - 60 s .. N + 300 s (median, quartiles)
  and the per-event Sharpe, power at VAL size with the 2025-26 event pace from K2's registered HOLD count (92 / 22
  months; that count is a registered public fact, not a HOLD return).
- Also write what a real bot would need (polling rate allowed by api-manager.upbit.com: it returned 429 at 0.3 s;
  websocket / other feeds), as a user decision.
