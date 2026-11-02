# Round 70 brief: corporate BTC-purchase filings at seconds; literature scout 2025-26 (coordinator + subagents)

Written 2026-11-01 17:20 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Each stream works
only in `research/results/portfolio/round70_filings_lit/<STREAM>/` and its own `research/data/<source>/` folder.

## Context (read, don't redo)
- research/PROMPT.md, research/JOURNAL.md top entries (rounds 64-69), registry.yaml `tried:` (167 directions).
- Rounds 64-69: the only public announcement with a seconds-level edge on Binance is Upbit's KRW-listing notice
  (A2-D5L, DEMO, HOLD t 3.11); every other venue's notices, Upbit's other notice types, OKX / Bybit, Japanese venues
  fail or have no data. Microstructure edges found at minute resolution decayed in 2025-26 (F failed HOLD).

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







## Stream M8: corporate BTC-purchase 8-K filings -> BTC perp within seconds
- Mechanism: a listed company's 8-K (or 8-K item 7.01 / 8.01) disclosing a completed BTC purchase is public demand
  information released at a known second (EDGAR acceptance time). If the market reads it as continuing demand, the
  BTC perp may drift after the stamp.
- Data: SEC EDGAR full-text search is not needed: use EDGAR submissions JSON per CIK (MicroStrategy / Strategy CIK
  1050446, plus any other company with repeated BTC-purchase 8-Ks you can identify from EDGAR itself, e.g. Tesla 2021,
  Semler, MARA), plain UA without e-mail (as rounds 41 / 47), >= 0.25 s; acceptance times to the second (check that
  the filing index page gives acceptance datetime; EDGAR times are Eastern). Binance BTCUSDT perp aggTrades from
  data.binance.vision daily files for event days <= 2024-12-31 (windows only). Distinguish filings that came before
  the company's own tweet / press release from those after (check timestamps of press releases on EDGAR exhibits).
- Rule (declare before prices): long BTC perp at the first trade >= acceptance + {5, 30} s, exit +5 / +60 min; costs
  taker 5 bp a side + spread from aggTrades. Report events per year, path -60 s .. +60 min, IS 2020-21 / VAL 2022-24.

## Stream LIT: literature scout 2025-26 (no backtest)
- Find 2025-26 papers / working papers (arXiv q-fin, SSRN abstracts via search, NBER, journals' online-first) on
  price effects driven by retail flows, exchange announcements, rule-based flows or settlement mechanics that are
  testable with free point-in-time data and tradable by a retail account on any venue. For each: mechanism, data, the
  sample period (flag HOLD contamination: a paper using 2025-26 data means any rule from it can only be forward-
  tested), whether it duplicates one of the 167 tried directions, and power at a plausible size.
- Output STREAM_LIT.md: ranked table (P(LIVE), P(DEMO), forward-only flag) + short sections. Read research/registry.yaml
  `tried:` and the "Những họ đã cạn" list in PROMPT.md first. At most 15 WebSearch; literature APIs allowed (no e-mail;
  export.arxiv.org disallows bots, use arxiv.org/abs pages or the API host allowed by robots).

## Stream D2: funding-formula carry, long Deribit perp / short Binance perp (added 2026-11-01 after LIT; LIT idea L2)
Binance USDT-M funding = premium + clamp(0.01 %/8h interest - premium, +-0.05 %), so in calm markets longs pay a
fixed ~11 %/yr; Deribit's perpetual funding has no interest leg (read Deribit's docs; check the exact formula and
its changes 2020-24). Long the Deribit perp / short the Binance perp in equal notional collects Binance's interest
leg if the two perps' prices do not drift apart. Round 59 tested Binance vs Bybit / Hyperliquid where both legs carry
the interest term (it cancels); this construction differs in that one leg has none. See LIT/STREAM_LIT.md section L2.
- Data: Deribit public API (keyless: funding rate history, perpetual 1h / 1d chart data for BTC-PERPETUAL, ETH-PERPETUAL
  and the USDC linear perps if any existed 2020-24; robots / docs first; >= 0.5 s), Binance funding and 1h klines
  local (research/data/binance/, binance_basis/). Note Deribit's inverse perps are coin-margined: account for the
  USD exposure of the inverse leg. Cut at ts < 2025-01-01.
- Rule (declare <= 6 cells before computing): always-on, or on when the trailing 7-day funding difference > 0; daily
  book; costs taker both venues at entry / exit and on rebalances; margin on both venues (report capital used and the
  excess over the cash rate on it, DFF); Newey-West t; IS 2020-21 / VAL 2022-24.
