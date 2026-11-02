# Round 69 brief: listing notices of other retail venues at seconds (coordinator + subagents)

Written 2026-11-01 16:16 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Each stream works
only in `research/results/portfolio/round69_other_notices/<STREAM>/` and its own `research/data/<source>/` folder.

## Context (read, don't redo)
- research/PROMPT.md, research/JOURNAL.md top entries (rounds 64-68), registry.yaml `tried:`.
- Upbit's KRW-listing notice moves the Binance perp within 1-3 s and A2-D5L (long 5 s after the notice, exit at the KRW
  open) passed HOLD as DEMO (t 3.11). Bithumb has no allowed notice history (round 66 B2); OKX / Bybit announcements do
  not move prices (O2); other Upbit notice types rise for 1-3 s and fade (round 68 UC). First-candle studies of other
  retail venues (round 65 I) found no pump at the first candle, but nobody measured the seconds after their notices.
- This round checks Korean (Coinone, Korbit, GOPAX) and Japanese (bitFlyer, Coincheck, bitbank, GMO Coin, BITPoint)
  venues: Step 1 is always whether a public, robots-allowed notice history with second-precision post times exists for
  2020-24; if not, the stream writes that and stops.

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






## Stream KO: Korean venues other than Upbit / Bithumb
## Stream JP: Japanese venues
Both streams, same plan:
- Step 1 (stop if it fails): notice / announcement history 2020-24 with post times to the second, reachable without an
  account or key, robots.txt read first (403 or disallowed = stop that host; never disguise as a browser; >= 1.5 s
  between requests; back off on 429; no e-mail in any request). Log every request (UTC time, URL, status, bytes) in
  research/data/<ko|jp>_notices/requests.log.
- Step 2 (declare before prices): listing notices for coins with a Binance USDT-M perp >= 7 days old (first daily kline
  <= N - 7 d and still trading at N + 1 d); A2-D5L frozen (copy round65_retail_venues/A2/code analyze.py trade / slip
  logic unchanged; costs as A2): long alt perp / short BTC perp at the first trades >= N + 5 s, exit at the venue's
  stated trading start (or N + 60 min if none). Path -60 s .. +300 s first; stamp vs burst check; overlap with Upbit
  notices (same coin within 7 days). data.binance.vision daily aggTrades for event days <= 2024-12-31 only (windows only,
  compact npz under research/data/<ko|jp>_notices/, zips deleted). IS 2020-21 / VAL 2022-24; ts < 2025-01-01.
- Do not read A2's PREREG "HOLD result" or anything under */coord/.
