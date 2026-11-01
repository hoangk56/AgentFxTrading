# Round 54 brief: single-stock CFDs (IC MT5) — data, cost model and three firm-level flows

Written 2026-10-30 10:05 UTC. **The user approved this direction on 2026-10-30 ("làm CFD cổ phiếu riêng lẻ của IC trên
MT5 đi").** This round is research only: no MT5 account, bot or deploy. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-53 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Fixed constraints still hold: lot size
does not depend on capital, each position is held at most 5 days, one bot holds at most 3 positions at once (a book
may use several bots, e.g. one per stock or per strategy: state how many the rule needs). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies (Read first, HOLD closed at 2024-12-31 at load,
Network rules, What to return), except the streams, the round folder (research/results/portfolio/round54_single_stocks/)
and the scratchpad (`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/<stream>/`).

Read first: research/results/portfolio/round25_surprises/STREAM_A.md section 3 (IC stock facts, Dukascopy coverage,
H-STK power), round42_megacap_boj_ops/STREAM_E.md, round44_insiders_tff/STREAM_I.md, round47_buyback_capacity/STREAM_B.md
(EDGAR files on disk and their pitfalls), and the Pitfalls of rounds 37-53.

Network: **no web.archive.org**; read robots.txt first and skip hosts that disallow ClaudeBot / anthropic-ai /
Claude-Web; **a 403 / bot-wall / token wall is a stop — never retry with a browser User-Agent or any disguise**, with
one established exception: the Dukascopy datafeed (datafeed.dukascopy.com), whose downloads the user approved on
2026-10-18 and which earlier rounds fetched with the browser User-Agent recorded in memory / round7_pre_code/duka.py.txt
(check its robots.txt first; if it names ClaudeBot, stop and report). SEC: generic research User-Agent, never an email,
>= 0.15 s spacing. **Never request a 2025 or 2026 Dukascopy file**; cut every series at 2024-12-31 at parse / load,
before anything is printed.

**Speed (the user is waiting):** stream D's pull must stay under ~1 hour (daily candles: one file per symbol-year
side). Streams E, I and B start at once: write HYPOTHESES_<x>.md and build their EDGAR-side signals from files on disk
while D pulls, then wait for D's `READY` file (exit the wait after 90 minutes or if D's `FAILED` file appears).

## Streams
| stream | direction | detail |
|---|---|---|
| D | **Data and cost model (others depend on it).** | (1) The Dukascopy US stock CFD list with first-data dates (instrument metadata, e.g. the dukascopy-node instrument list on GitHub / npm, robots permitting). (2) Daily BID and ASK candles 2016-01..2024-12 for every US stock CFD with data before 2019 (~220), `datafeed/{SYM}/{YYYY}/BID_candles_day_1.bi5` (verify path and scale on 2 names first; a missing file answers 503). Save open / high / low / close bid and ask per day as `.../r54/D/out/stocks_daily.npz` plus `symbols.csv` (Dukascopy symbol, ticker, CIK via SEC `company_tickers.json`, first date, rows). Check splits (Dukascopy CFDs may not be adjusted: detect jumps against the SEC split facts or a > 40 % overnight move with a round ratio, and flag them). (3) The IC MT5 cost model: from IC's public spec sheets (round 25 A: USD 0.02 per share per side, financing benchmark +/- 3 % a year, dividends adjusted), plus the Dukascopy spread at the open / close as the spread proxy; state which IC names overlap (IC's sheet lists, if the PDF is reachable). (4) A shared helper `stocklib.py` (entry / exit at the open or close bid / ask, commission, financing per night, day-clustered t, random-entry control, by-year table). Write `READY` with a one-paragraph summary when done, or `FAILED` with the reason. No hypothesis testing in D. |
| E | **Earnings: employee selling after the blackout (Hartzmark & Solomon 2022, NBER WP 30688) and post-earnings drift of large caps.** | Firms in D's list; 8-K item 2.02 acceptance times (round 47's `ea_8k202.csv` for the top-200, extend via submissions JSON if needed); XBRL `ShareBasedCompensation` (prior quarter, as filed). Declared before returns: (1) H-STK: short the top quintile / decile of stock compensation over market cap from the first open after the release (blackout lifts ~0.8 days after) for t+1..t+3, hedged with US500 or USTEC (declared), the paper's size -87.5 bp (t -5.77) for the top 5 %; (2) PEAD at 1-5 days: follow the earnings-day open-to-close reaction (Chordia et al.: large-cap drift weak; declare the side from the literature and the alternative). Count events, do the power arithmetic first. |
| I | **Opportunistic insider purchases on the firm itself (Cohen, Malloy & Pomorski 2012).** | Round 44 I's Form 4 data sets (2014-24 on disk: `.../scratchpad/r44/I/`), firms in D's list. Classify routine vs opportunistic insiders per the paper (an insider who traded in the same month in each of the prior 3 years is routine), declared before returns. Long the firm from the open after the filing date (22:00 ET deadline rule from round 44) for 1-5 days, hedged and unhedged (declared); also cluster buys (>= 2 insiders in 5 days) and CEO / CFO open-market buys as declared variants. Count events, power first. |
| B | **Firm-level buyback windows (the round 47 construction applied to each stock).** | Round 47's `universe.csv`, `facts.csv`, `ea_8k202.csv` (`.../scratchpad/r47/B/out/`), firms in D's list. Declared: long the firm's largest buybacks (run-rate / market cap top quintile) for 1-5 days from window reopening (2 trading days after the release) against the market, and the mirror (blackout start) as alternative; the round 47 week-of-quarter confound must be removed by comparing firms on the same day (cross-section at the same date). Count events, power first. |

Each of E, I, B may use up to 2 heavy Python processes (under ~3 GB RAM each); D up to 3 for the pull.
Report per stream: net IS (2016-21, from first data) / VAL (2022-24), spread x1.5, +1 day delay variant where it
applies, ex-2020-03/04, by year, random-entry control (same dates, random firms from D's list), chance benchmark over
cells, power at HOLD size, the number of bots / concurrent positions the rule needs, and correlation with C3's daily
returns for any surviving cell (`research/results/portfolio/trades_C3_gotobi_jpy_basket.csv`, git-ignored; if missing,
say so). If a cell meets DEMO or LIVE numbers write PREREG_DRAFT_<x>_*.md, but do NOT open HOLD.
