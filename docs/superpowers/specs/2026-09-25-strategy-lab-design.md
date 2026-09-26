# Strategy Lab — Design

**Date:** 2026-09-25
**Status:** Approved in chat (approach B, tick level), awaiting spec review
**Follows:** `research/results/strategy_search.md` (rounds 1–2 + 2023–24 confirmation) and
`2026-09-25-flowrsi-entry-redesign-design.md` (FlowRSI screening verdict: nothing passed)

## Goal

1. One place that records every strategy we run or have researched — rules, parameters, origin, status and
   findings — and that new research keeps adding to.
2. One tick-level backtest that runs every catalogued strategy on every symbol we have, over all the data we
   have (2023-01 → 2026-09 once the gaps are filled), under the same account rules, and reports $ results.
3. Synthetic data (mirrored prices, reshuffled weeks, synthetic crosses) to stress the results.

## Decisions taken in the brainstorm

| Question | Decision |
|---|---|
| "One position at a time" | Per (strategy × symbol) run: a signal that arrives while that run holds a position is skipped |
| Live cBots | Port to Python: FlowRSI (existing calibrated replica), Judas (its non-AI legacy path), TMS+ORB (rule part, AI assumed to approve every candidate) |
| Data | Fill 2023–2024 for the 10 symbols that only have 2025+ (≈ 20 cTrader cache-fill jobs on the VPS) |
| Lot size | Fixed units per symbol, notional ≈ $10k at the 2025–26 median price, constant for the whole test |
| Engine | **Approach B: tick level for everything** (the user chose accuracy over speed) |
| Limits | None: no loss-count, daily or total loss limit, no guardrails, no equity-based sizing |
| Synthetic data | Stress tests only, never pooled into the real results |

## Account rules (every run)

- Start balance $10,000. P&L in USD. Equity may go below 0: the report records the date it first does
  ("blown") and keeps counting.
- Fixed units per symbol (cTrader units; FX 0.1 lot = 10,000 units):

  | Symbol | Units | Notional at 2025–26 median |
  |---|---|---|
  | EURUSD GBPUSD AUDUSD USDCAD USDJPY EURJPY GBPJPY AUDJPY + synthetic crosses | 10,000 | $6.6k–13k |
  | XAUUSD | 2 | $8.1k |
  | BTCUSD | 0.1 | $8.8k |
  | ETHUSD | 4 | $10.0k |
  | US30 | 0.2 | $9.3k |
  | USTEC | 0.4 | $9.9k |
  | DE40 | 0.4 | $11.0k |
  | UK100 | 0.8 | $10.2k |

  Units stay fixed even where the price was far from the median (BTC 0.1 was $1.7k notional in early 2023).
  R multiples (net / initial stop risk) are reported next to $ so results can be compared across symbols.
- One position per (strategy, symbol). No DCA, no pyramiding, no partial re-entries.
- Strategy logic that is not a risk limit stays: spread filters, session windows, cooldowns that are part of
  the rule (e.g. Judas' once-per-session sweep side).

## Execution model (tick level)

- Ticks: the cTrader cache (`research/data/<SYMBOL>/t1`, bid/ask, forward-filled).
- Bars: bid OHLC built from ticks exactly as cTrader does (`research/bars.py`), UTC-aligned for M1–H4.
  D1 bars close at 17:00 New York (the FX day: no Sunday or Friday stubs) and D1 entries are placed 2 h after
  the close, out of the rollover spread (round-2 finding).
- A signal on bar i fills at the first tick after the bar's close (OnBarClosed): buy at ask, sell at bid.
  Intra-bar (OnTick) strategies fill at the tick that triggers them.
- SL/TP: a buy exits on the first bid ≤ SL or ≥ TP, a sell on the first ask ≥ SL or ≤ TP; the exit fills at
  that tick's price (gaps fill at the gapped price). Time exits fill at the first tick after the bar close.
- Stateful exits (break-even, partial close, trailing, tiered trailing, giveback, session end, indicator
  close) are evaluated tick by tick while the position is open, jumping ahead with vectorised first-hit
  searches until the next level that can change state (as `research/sim.py::_run_flowrsi` does).
- Costs: spread (in the ticks), commission per unit (`research/specs.py`; synthetic crosses 6e-5 × base
  currency in USD, which matches the real pairs), swaps per unit per 17:00 New York rollover (fitted 2026
  rates; 2023–24 swaps are therefore approximate and are reported as a separate column).
- Quote → USD conversion is **time-varying** (daily close of the conversion pair: USDJPY for JPY, USDCAD for
  CAD, EURUSD for DE40, GBPUSD for UK100 and GBP-quoted crosses, AUDUSD for AUD-quoted crosses), replacing
  the constant `usd_per_quote` that only held for 2026.
- Processing is chunked by calendar year: each chunk loads [year − 190 days warm-up (WF1 trains on 6
  months), year end + 45 days tail]; entries are taken only inside the year; a position that crosses the year end is finished on the
  tail, and the next chunk accepts entries only after that exit.

## Universe

- 15 real symbols: AUDJPY AUDUSD BTCUSD DE40 ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 US30 USDCAD USDJPY
  USTEC XAUUSD. Years 2023, 2024, 2025, 2026-01-01..09-24 (after the fill below).
- 7 synthetic crosses built on the fly from the USD legs: EURGBP (EURUSD/GBPUSD), EURAUD, EURCAD, GBPAUD,
  GBPCAD, AUDCAD, CADJPY. bid = base-leg bid ÷ quote-leg ask (or × for the JPY/CAD legs), ask the other way
  round, as-of joined on tick time. The method is checked by rebuilding EURJPY, GBPJPY, AUDJPY from their
  legs and comparing mid and spread with the real ticks; the measured spread ratio real / synthetic is then
  applied to the synthetic half-spread. Results on synthetic crosses are labelled "synthetic".
- Pairs trading / stat-arb needs two legs open at once, which the one-position rule forbids: catalogued as
  "not applicable", not run.

## Data fill

Queue the cTrader backtests that fill the 2023–2024 tick cache for AUDJPY AUDUSD ETHUSD EURJPY EURUSD
GBPJPY GBPUSD UK100 USDCAD USDJPY (2 jobs each, FlowRSI bot, as `research/fill_2023_2024.py` did for the
other five; the reports are not used), then `research/pull_years.sh "2023 2024" …`. Cold-cache runs may
fail once with "aborted by timeout" (the backtest page reruns once); a failed run still fills the cache.
Live bots are unaffected (backtest containers run on bridge networking with 1 GB / 2 CPU limits).

## Synthetic stress tests

Run only as extra columns, never pooled with the real results.

- **Mirror**: p' = K / p per tick with K = (first mid of the symbol's sample)², bid' = K / ask,
  ask' = K / bid; long and short swap rates exchanged. A strategy whose profit is market beta (gold's bull
  run) loses it here. Run for every strategy × symbol.
- **Week shuffle ("đổi năm")**: weeks [Sat 00:00 UTC, next Sat) are permuted across the whole sample with a
  seed; each week's prices are scaled so it opens where the previous one closed, and its timestamps are
  shifted by whole weeks into its new slot (weekday and hour kept; DST drift ≤ 1 h ignored). 20 seeds.
  Run only for strategy × symbol cells whose real net $ over the full period is > 0.
- **Random control**: 20 seeds per cell and year. Each seed replays the real trades' shapes in order (stop
  distance, target distance, holding time as a time cap) at random M15 bar closes with random sides, one
  position at a time. Gives the "cost drag only" baseline for every cell.
- Mirror and shuffle run on the 15 real symbols only (the synthetic crosses are already synthetic).
  Strategies whose signal needs other symbols' real history (X1, FXM1, MEF) run on real data only.

## Strategy catalog

`research/lab/catalog.py` is the single registry. Each entry is a `StrategyInfo`:

- `id`, `name`, `origin` (live cBot, or the research round and date it came from), `family`, `timeframe`
- `rules` (plain-language rule text), `params` (defaults, per-symbol overrides where the live presets have them)
- `status`: `live` / `candidate` / `rejected` / `not_applicable`, with `findings` (dated notes carried over
  from `research/results/*.md` and memory: e.g. "BTC-S1: 2023 +0.000R, pooled 2023–24 t 1.0 — failed")
- `impl`: the implementation (below)

Adding a strategy = add one entry (and its implementation if it is new code). `python -m research.lab.catalog`
renders `research/STRATEGIES.md` from the registry plus the latest lab results.

Two implementation kinds:

- **Vector strategy**: `signals(market) -> Intents` computed from bars (numpy), with a fixed exit policy
  (SL/TP in ATR or price, time exit, optional session-close exit). Used by the research rules.
- **Event strategy**: a small class the engine drives per closed bar (and per tick while a position is open)
  with the position state, for the ported cBots whose entries depend on their own state (Judas' session
  flags and structural invalidation, TMS+ORB's post-TP gate and loss streak).

Initial catalog:

| id | Source | Kind |
|---|---|---|
| FLOWRSI | live FlowRsiBot, live presets, via the calibrated replica (`research/sim.py`, `research/signals.py`) | event (existing) |
| FLOWRSI-E1..E5 | FlowRSI entry-screening candidates | vector + FlowRSI exits |
| JUDAS | live AsianRangeJudasSweepBot, legacy (non-AI) path: Asian range, killzones, sweep, SL/TP, BE, trailing, structural invalidation | event (port) |
| TMSORB | live AiAgentBot rule part: the candidate entries it sends the AI, taken as trades, with its exits (ATR SL/TP bounds, BE, trailing tiers, giveback, session end) | event (port) |
| BTC-S1 | shock-bar follow, M15 | vector |
| XAU-T1 | H4 Donchian 30 breakout | vector |
| TOM | turn-of-month long indices | vector |
| K1 / K1b | FX weekly fade, D1 | vector |
| K2 | index ORB 60 min | vector |
| VB1 | index volatility breakout | vector |
| X1 | cross-sectional FX reversal (per-pair slots) | vector (needs all 8 FX pairs' bars) |
| FXM1 | regime-switch FX weekly | vector |
| LC1 | US last-30-min fade | vector |
| GF1 | US opening-gap fade | vector |
| OD1 | overnight drift 02–03 NY | vector |
| MEF | month-end London fix USD flow | vector |
| BANK-* | the 552-config bank: one entry per kind (zmove, donch = Donchian trend/fade, rsi) × direction (follow, fade) × TF (M15, H1, H4, D1) = 24 entries, each frozen at the config with the best pooled 2025 mean R (n ≥ 30) in `research/results/bank_stats.csv` | vector family |
| WF1 | walk-forward ridge | vector (monthly refit) |
| PAIRS-* | stat-arb | not_applicable |

Rules for the ports that the live bots get from the AI (TMS+ORB's direction choice, Judas' AI gate) are
replaced by "take every candidate the bot would send": for TMS+ORB every bar that passes the server's
deterministic cycle gate (`app/server.py::evaluate_cycle_gate`), in the macro bias direction; open positions are
managed by the cBot's exits plus the AI prompt's rules 1–2 filtered by `validate_tms_close_decision`, and
BiasFlipExit. Risk limits in the bots are switched off to honour the account rules: TMS+ORB's loss-streak gate
and MaxDollarRiskPerTrade / min-lot guards, FlowRSI's MaxRisk guards (fixed units). The ports cannot be calibrated against cTrader here
(the backtest page only supports FlowRSI because the other two enter only through the AI), so their results
carry the label "port, uncalibrated".

## Components

```
research/lab/
  catalog.py        registry + STRATEGIES.md renderer
  universe.py       symbols, fixed units, conversion pairs, synthetic-cross definitions
  feed.py           tick chunks per (symbol, variant, year): real, mirror, shuffle(seed), synthetic cross
  costs.py          commission, swaps, time-varying quote->USD
  cbot.py           live cBot parameters: [Parameter] defaults from cBot/*.cs + presets
  engine.py         one-position tick engine: fills, SL/TP/time exits, trade records, NY-close D1 bars
  strategies/       rules.py (vector rules), flowrsi.py, judas.py, tmsorb.py (the ports carry their own exits)
  check_crosses.py  synthetic-vs-real cross check -> SYNTH_SPREAD_FACTOR
  control.py        random-control generator
  run.py            CLI: strategies × symbols × variants × years, process pool, writes results
  report.py         per-cell / per-year tables, flags, report.md
research/tests/lab/ pytest
research/results/lab/<run_id>/  trades.csv.gz, control.csv, coverage.csv, errors.csv, meta.json,
                                cells.csv, matrix.csv, report.md
research/STRATEGIES.md          generated catalog
```

Parallelism: one job per (symbol, variant); inside it the years run in order (so the one-position state
carries across years) and every strategy runs on the same loaded chunk. Three worker processes by default
(a BTC chunk with warm-up and tail is ≈ 1.8 GB of arrays; the Mac has 16 GB).

## Report

Per (strategy, symbol, year) and full period: trades, net $, gross $ (after spread), commission $, swap $, PF,
win %, mean R, t, max DD $, worst month $, % months positive, blown date; mirror net $, shuffle percentile
of the real net, random-control mean and the real result's percentile against it. Flags per cell:
positive every year / beats random control (≥ 95th pct) / shuffle ≥ 95th pct / mirror > 0. A per-strategy
line sums $ across symbols (a sum, not a one-position portfolio). `STRATEGIES.md` gets each strategy's latest
headline numbers.

## Error handling

- A symbol-year without ticks is reported as "no data", not zero trades.
- An exception in one strategy is written to `errors.csv` with the traceback; the other strategies and
  cells keep running.
- The run records the git state, the catalog hash and the data coverage per symbol in the results folder,
  so a result can be traced back to its inputs.

## Testing

- Engine: buy fills at ask / sell at bid; SL checked on bid for buys and ask for sells; gap fill at the
  gapped tick; time exit; one position at a time (a signal during a position is skipped); fixed units;
  commission and swap; year-boundary carry-over.
- Feed: mirror applied twice returns the original; shuffle keeps the multiset of weekly log returns and
  every tick's weekday/hour; synthetic EURJPY from legs vs real EURJPY within a tolerance.
- Costs: time-varying conversion matches the 2026 report constants (within 8 % on a 2026 date); commission
  and swap per rollover.
- Parity: BTC-S1 in the lab reproduces `research/scan/ticksim.run(..., fixed_units=0.1)` trade for trade;
  FLOWRSI in the lab reproduces `research/sim.run_account` entries with the same parameters.
- Catalog: every entry has the required fields and runs on a 2-week slice of one symbol without error.

## Out of scope

- Changing any cBot, deploying anything, or touching production data.
- Portfolio simulation across strategies/symbols (the user chose per-cell one-position).
- New strategy ideas beyond the catalog (they get added later as entries).

## Expectation

Almost every catalogued strategy already failed an out-of-sample bar in earlier rounds. This test puts them
all on one fixed-lot, tick-level footing over ~3.7 years and 22 symbols; it is not expected to reveal a new
edge, and synthetic data measures robustness, not additional evidence.

## Git

`research/` is untracked on main (the earlier research code is on `origin/feat/flowrsi-entry-screening`);
`docs/` is git-ignored, so this spec is not committed. Nothing is committed or pushed unless the user asks.
