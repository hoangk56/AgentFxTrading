# Round 9 brief: what a $100,000 account changes (shared by streams I, O, P)

Written 2026-10-05, before any round-9 number was computed. The user asked (Vietnamese): "research cho tôi chiến
thuật và thuật toán mới với mức vốn $100000" = research new strategies/algorithms for a $100,000 account. Asked to
choose, the user picked three directions (each one stream) and RELAXED the old limits of research/PROMPT.md:
positions may be held weeks to months, a bot/book may hold many positions, and lots may depend on capital
(risk as a share of equity, volatility targeting...). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

| stream | direction | venue |
|---|---|---|
| I | the current IC Markets cTrader account at $100k: what the size and the relaxed limits unlock | IC Markets cTrader (26 symbols in research/data; no share CFDs on cTrader, those are MT5 only) |
| O | index options: harvesting the volatility risk premium (selling puts / spreads / condors) | a listed-options broker (e.g. IBKR: SPX / XSP); NOT cTrader |
| P | a $100k prop-firm account (FTMO-style challenge) | prop firms that offer cTrader |

## Where things stand (read, don't redo)
- research/JOURNAL.md (rounds 1-8, newest first). Eight rounds agree: on IC, intraday flows lose to spread +
  commission, multi-week premia lose to IC's financing markup (FX 0.6-1.7 %/yr per side, metals 1.0/0.5 %, indices
  about r + 5.3 % long, r - 3.9 % short). After 2015 even the gross multi-week premia (TSMOM, carry, FX momentum/value)
  are ~0. Read round7_new_data_2026-10-05.md section D and sizing_round5_2026-09-27.md before proposing anything slow.
- The ONLY algorithm that passed everything is C3, the gotobi Tokyo-fix trade on USDJPY/EURJPY/GBPJPY
  (cBot/GotobiBot.cs): long ~18:00 UTC the evening before a gotobi day -> 00:55 UTC (Tokyo fix), short 00:55 ->
  02:55 UTC, stop 3 x ATR20(H1), mean R ~ +0.04..+0.05 per leg, passes 2004-15, 2016-21, 2022-24 and 2025-26. Its
  cTrader backtest on IC ticks, 2016-01..2026-09, $50 risk per leg: research/results/portfolio/gotobi_cbot_trades.csv
  (4,574 trades; columns symbol,direction,leg,entry_utc,close_utc,entry,close,lots,pips,gross,commissions,swaps,net;
  the gotobi day is the date in `leg`; R = net / 50). Live bots skip Japanese public + bank holidays
  (research/tools/gotobi_holidays.py `no_fix_days`; needs `pip install holidays`, see below); holiday days lose, so
  drop them when you model the live bot. The three pairs' R correlate +0.68..+0.84 (one gotobi event ~ 2.5 legs of
  risk). Round 5 already did C3 compounding at 1-4 % risk on CLOSED-trade equity (1 % -> CAGR +22 %, DD 10 %;
  3 % -> +75 %, DD 28 %); floating DD and execution at size were not done.
- C1 crypto Donchian H4 failed its holdout (forward test only). Nothing else is waiting.

## Eras and the holdout
- For any NEW market series: design (choose rules/parameters) on data up to 2021-12 (options: up to 2015-12 is
  preferred for design, then 2016-21 and 2022-24 as two checks), check 2022-01..2024-12 once per hypothesis family.
  **HOLD = 2025-01-01..2026-09 stays closed**: cut every new series at ts < 2025-01-01 AT LOAD (filter rows right
  after download, before anything prints). Never print, plot or summarise HOLD rows.
- Exception: C3's own trade CSV may be used in full (2016-2026): C3 already passed its holdout and streams I and P
  use it for sizing / rule modelling, not to discover an edge. Say so where you do it.
- Pre-registration (only if something meets its bar): rule, parameters, instruments, bar, number of cells tried,
  code hashes (`research/.venv/bin/python -m research.tools.prereg_hashes <files>` works on any path). Do NOT open
  HOLD; the lead decides.

## Discipline (same as rounds 3-8)
1. Write each hypothesis (mechanism + source + exact rule + horizon + what would count as success) into
   r9/<stream>/HYPOTHESES_<stream>.md BEFORE computing it. Add new ones as you go, always before their numbers.
2. Economic mechanism first (a risk premium, a flow, a constraint), not a chart pattern.
3. Gross first, then executable net with the venue's real costs; report the cost next to the gross.
4. Multiple testing: count the cells you tried per family and compare the best |t| with chance.
5. A slow premium is judged like round 7 D: net > 0 in every era separately, Newey-West (HAC) t of the net mean
   >= 2.5 over the full design+check sample (or say it cannot reach that and why), majority of years > 0, robust to
   cost x1.5, and better than the obvious benchmark at the same risk (e.g. the index at the same beta). Report
   annual Sharpe, CAGR at a stated risk, max drawdown (mark-to-market where you can), worst month, skew.
6. Don't lower a bar. Negative results are results: give the numbers so nobody redoes them.

## Rules for the work
- Write scripts, data and outputs ONLY under your stream folder:
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/34411c43-c386-4eae-97c9-a7e91bcb3a2c/scratchpad/r9/<stream>/
  Do NOT edit any repo file (research/ code, JOURNAL, README, docs, tests, cBot, app). No git commands that change
  state. Do not touch the VPS or the production database. No trading actions of any kind.
- Python: run from the repo root: `cd /Users/hoangbk/00.code_base/105.AgentFxTrading && research/.venv/bin/python ...`.
  research/.venv has numpy only. If you need more (pandas/scipy/holidays), create your OWN venv inside your stream
  folder (`python3 -m venv r9/<stream>/.venv && r9/<stream>/.venv/bin/pip install numpy holidays ...`); don't
  install into research/.venv. Shared Mac (10 cores, 17 GB, 3 streams at once): <= 2 heavy processes, each < 3 GB;
  load research/data/m1/*.npz with mmap_mode="r" and slice.
- IC M1 cache: research/data/m1/<SYMBOL>.npz, keys ts (int64 ms UTC, minute start), o h l c (bid), ca (ask close),
  smin smean (spread stats, price units), n (ticks). 26 symbols, 2016-01..2026-09: cut ts < 1735689600000 on load.
  FRED series cache: research/data/rates/. Swap model: research/swing/rates.py `swap_frac_at(symbol, side, ms)`.
  Dukascopy 2004-15 bid H1 for 11 FX/gold symbols: research/data/duka/h1/.
- Network: allowed for public data (CBOE, FRED, Yahoo chart API with a browser User-Agent, CFTC, prop-firm and broker
  web pages, paper search). Never send the user's email or any credential anywhere; if a service wants contact info
  in a User-Agent, use "AgentFxTrading research" without an email, or skip that service.
- Literature: the paper-lookup / backtest-expert / residual-edge-analyzer / statistical-power skills in
  research/.claude/skills become available after you Read any file under research/ (they are optional aids).
- The harness blocks subagents from writing files named REPORT.md or FINDINGS_*.md: do NOT write your write-up to a
  file. Return it as your final message. CSV/JSON/TXT outputs and HYPOTHESES_<stream>.md are fine.

## What to return (final message, <= ~1,800 words, English)
- One-paragraph answer first (what works / doesn't for this direction at $100k, and the single best thing).
- A table per family: hypothesis (mechanism, source) | data/era | gross | cost | net | t / Sharpe | verdict.
- For anything usable: exact rules, sizing for a $100,000 account at a stated drawdown tolerance, expected annual
  return / max DD with the evidence behind them, and what it would take to run it (platform, broker, code).
- Number of cells tried and the chance benchmark; pre-registration path if any; data or cost-model problems found.
- Paths of your scripts and outputs.
