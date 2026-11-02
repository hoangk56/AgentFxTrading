# Round 71 brief: funding-formula asymmetries, CME weekend gap, two forward-only literature rules (coordinator + subagents)

Written 2026-11-01 17:47 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Each stream works
only in `research/results/portfolio/round71_mixed/<STREAM>/` and its own `research/data/<source>/` folder. The user
asked (2026-11-01) to keep researching with 5-10 streams until a LIVE candidate passes a registered holdout.

## Context (read, don't redo)
- research/PROMPT.md (bars, exhausted families, pitfalls), research/JOURNAL.md top entries (rounds 64-70),
  registry.yaml `tried:` (~170 directions). Standing: C3 is the only LIVE algorithm; DEMO that passed HOLD: B, X3, K2,
  Q1, A2-D5L; F0 is forward-registered. Round 70: corporate BTC 8-Ks (M8) fail; stream D2 (Deribit vs Binance funding
  formula) is running; LIT (round70_filings_lit/LIT/STREAM_LIT.md) listed ideas L1-L6.
- **Forward-only rule:** a rule built from a source that uses 2025-26 data (L3, L5) cannot be graded on HOLD; if it
  passes IS / VAL, write PREREG_DRAFT_<name>.md as a FORWARD registration from 2026-10-30 (as round66 F0).

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








## Stream D3: funding-formula asymmetries on other venues
Stream D2 tests Deribit (no interest leg) vs Binance (0.01 %/8h interest leg). Find every other pair of venues /
contract types whose funding formulas differ by rule (interest term, damper / clamp width, interval, cap), from the
venues' own public docs and keyless funding histories 2020-24: OKX, Bybit (linear vs inverse), BitMEX, Kraken Futures,
Hyperliquid (from 2023), Binance COIN-M vs USDT-M. Do not repeat D2's pair or round 59's B1 / B2 (Binance vs Bybit /
Hyperliquid linear, both with the interest leg). For pairs where one leg carries a structural term the other lacks,
test the carry (long the leg that pays less by rule / short the other, daily book, both venues' taker costs, capital
on margin graded on excess over DFF, Newey-West t), IS 2020-21 / VAL 2022-24; declare <= 6 cells before computing.

## Stream CG: CME bitcoin weekend gap
CME BTC / ETH futures close Friday 21:00 UTC (22:00 in winter, check DST) and reopen Sunday 22:00 / 23:00 UTC, while
crypto trades all weekend. Desk lore says the "CME gap" fills: price returns to the Friday close in the following days.
Mechanism to test: CME-based basis and fund flows rebalance at the reopen. Declare before computing (<= 6 cells): the
weekend move m = ln(price at the CME reopen / price at the CME close) on Binance BTCUSDT / ETHUSDT perps (local 1h /
1m data); if |m| >= {2, 4} %, fade it from the first 1m bar after the reopen + 5 min until the Friday price is touched
or 1 / 3 days; costs taker 5 bp a side + spread; funding. Random benchmark: the same rule anchored to other weekdays'
21:00 UTC. ~52 weekends a year: say the per-trade Sharpe needed (3 / sqrt(HOLD n)) first. IS 2020-21 / VAL 2022-24.

## Stream L3F: extreme negative funding, follow the day's direction (forward-only; LIT L3, SSRN 7520320)
Local data only (binance/funding, perp_1h / 1d, ts < 2025-01-01). Declare before computing (<= 6 cells): an event is a
funding stamp <= the trailing-180-day 5th (and 10th) percentile of that coin's funding; side = sign of the UTC-day
return up to the stamp; hold 24 h from the first 1m / 1h bar after the stamp; universe BTC / ETH plus the point-in-time
top-10 perps (round 58 universe()); costs taker + spread + funding. If it passes IS / VAL, forward registration only.

## Stream L5F: quarter-hour opening order imbalance (forward-only; LIT L5, arXiv 2607.09426)
data.binance.vision monthly 1m klines (they carry taker-buy base volume) for BTCUSDT, ETHUSDT and the four largest
other perps by 2020-24 volume, months <= 2024-12, compact npz under research/data/qh_imbalance/. Declare before
computing (<= 6 cells): signal = taker-imbalance z of the first minute of each :00 / :15 / :30 / :45 (vs the same coin's
trailing 30-day distribution of that slot), trade with the sign above |z| >= {2, 3} from the next minute, hold 4 h /
12 h; costs taker 5 bp a side + 1 bp half-spread for BTC / ETH, round 63 C's model for others. Round 63 O found taker
imbalance ~0 before costs on altcoins: say how this differs. If it passes IS / VAL, forward registration only.

## Stream FS: crash-wick fade on Binance SPOT coins without a perp (added 2026-11-01 17:48 UTC)
F (round 64) faded 5 % one-minute wicks on top-40 USDT-M perps and failed HOLD at the next-bar entry; F0 (round 66,
entry at the first trade after the event bar's close) is forward-only because F's HOLD is known. Coins that trade on
Binance SPOT but have no USDT-M perp at the time are a disjoint event set: their HOLD has never been opened. Disclose in
the hypotheses that the same mechanism failed HOLD on perps.
- Universe each UTC day: the top 40 Binance spot <COIN>USDT pairs by trailing-30-day quote volume (spot_1d local, or
  data.binance.vision spot daily / monthly klines), excluding stablecoins / leveraged tokens (UP / DOWN / BULL / BEAR)
  and any coin with a USDT-M perp listed before that day (research/data/binance/perp_1d, all 886 incl. delisted).
- Event: 1m close-to-close return <= -5 % while BTCUSDT's same minute moved <= 0.2 x as much (F's idiosyncratic
  filter), bar e >= 10 trades; long only (no borrow), entry at the first spot aggTrade >= the close of bar e (data.
  binance.vision spot daily aggTrades for event days, windows only) and, as the declared check, at the close of bar
  e+1; exit at the close of bar e+61. Costs: spot taker 10 bp a side + half-spread measured from aggTrades in the entry
  second. One event per coin per 60 bars. Declare <= 6 cells (|r| >= 5 / 8 %, H 15 / 60) before computing.
- Data: data.binance.vision spot monthly 1m klines for the universe months (<= 2024-12), compact npz under
  research/data/spot_wicks/; aggTrades for event days only. IS 2020-21 / VAL 2022-24. Random benchmark as F.

## Stream PX: tokenized gold over the weekend vs the gold market's reopen (added 2026-11-01 17:53 UTC)
PAXG (Paxos Gold, redeemable for LBMA gold) trades on Binance spot all weekend, while spot gold (IC XAUUSD) is closed
from Friday ~21:00 UTC to Sunday ~22:00 / 23:00 UTC. Over the weekend PAXG is moved by crypto flows (and crypto
liquidations) with no gold market to anchor it; when gold reopens, the anchor returns. Mechanism: a wedge with a hard
anchor (redemption at the gold price) and a known closing time. No round tested PAXG / XAUT.
- Data: Binance spot PAXGUSDT (and XAUTUSDT if listed) 1m klines from data.binance.vision (months <= 2024-12), IC
  XAUUSD M1 (research.m1; gold's Friday close and Sunday reopen; note IC's metal cost model issues in PROMPT.md),
  research/data/paxg_weekend/ with requests.log. Check when PAXG listed on Binance (IS may start 2020-09 or later: say
  how many IS weekends exist before building; if too few, do not invent a new split).
- Rule (declare <= 6 cells before computing): weekend deviation w = ln(PAXG at T / (XAUUSD Friday close x the
  Friday-close PAXG/XAU ratio)) at Sunday 21:00 UTC (before gold reopens); if w <= -k (k in {30, 60} bp) buy PAXG
  (spot, no borrow), exit at the first 1m bar after gold's reopen + 30 min / 4 h; the rich side (sell PAXG you hold, or
  a PAXG perp where one existed) reported separately. Costs: spot taker 10 bp a side + half-spread from klines /
  aggTrades on those minutes (PAXG books are thin at weekends: measure them). Also report the path of PAXG vs gold
  from Friday close to Monday 06:00 UTC by w bucket. IS 2020-21 / VAL 2022-24; ts < 2025-01-01.

## Stream IB: scout trades protected by a barrier to entry (no backtest; added 2026-11-01 17:56 UTC)
What survived HOLD in 2025-26: C3 (Japanese corporate settlement flow), B (needs spot borrow most bots lack, HOLD t 14),
K2 / A2-D5L (Upbit-specific Korean retail flow; A2 needs a seconds-level notice bot). Microstructure edges without a
barrier decayed (F, P2, carry = cash). Produce 8-12 hypotheses whose edge is protected by a barrier a retail account
can cross but large bots / market makers avoid or cannot: borrow / short constraints, jurisdiction or KYC-gated venues,
capital lock-up or settlement delay, small capacity, operational rules (deposit / withdrawal suspensions, network
upgrades, redemption windows, fiat rails), mandated flows with public schedules. Each with: mechanism and the barrier,
instrument / venue (any venue; say what account the user would need), free point-in-time data source checked with one
logged request (robots.txt first), events per year, HOLD power at a plausible size, P(LIVE) / P(DEMO), and why it is not
in research/registry.yaml `tried:` (~172 directions) or PROMPT.md's exhausted families. No backtest. Requests logged
in research/data/scout_ib/requests.log; >= 1 s between requests per host; no account / key / e-mail; at most 15
WebSearch. Output STREAM_IB.md (ranked table + sections).

## Stream W7: withdrawal-closed window of new Binance spot listings (added 2026-11-01 18:15 UTC; IB/STREAM_IB.md IB7)
Binance usually opens withdrawals of a newly listed coin ~24 h after spot trading starts; during that window a Binance
spot discount cannot be arbitraged out (coins cannot leave). Long Binance spot (no borrow) / short the reference perp
(Binance perp if live, else the Bybit perp), exit when withdrawals open. Follow IB7's declared grid (<= 8 cells: signal
at listing + 15 / 60 min, k 50 / 100 bp, exit at listing + 24 h + 0 / 30 min), its data plan (data.binance.vision spot
aggTrades for event days, local spot_first.csv / perp_1d, Bybit public archive for the reference perp), withdrawal time
approximated as first kline + 24 h with a sensitivity check, entries at aggTrades only. Report the spot and hedge legs
separately (round 66 N0: big early perp moves continue). IS 2020-21 / VAL 2022-24; ts < 2025-01-01.
