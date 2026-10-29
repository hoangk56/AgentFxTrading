# Paper desk

An experiment, not a strategy: do LLM agents "analysing the day" beat naive rules after costs? It touches no money and
no bot. Code: `app/paper_desk.py`. The terms below are fixed before the first call; change them only with a new dated
section, never after seeing results.

## Registered terms (2026-10-28)
- **Symbols:** EURUSD, USDJPY, GBPJPY, XAUUSD, US500, BTCUSD.
- **Call:** one analyst, one symbol, one day: direction -1 / 0 / +1 (0 = no trade), confidence, short rationale, the
  features it was shown, the model id.
- **Timing:** entry at 07:00 UTC of the call date, exit at 07:00 UTC of the next weekday. A call is written before
  07:00 UTC of its date or refused. The table is insert only; a repeat for the same (day, symbol, analyst) is refused.
- **Inputs:** numbers computed in Python (returns, ATR, volatility, distance to recent highs/lows, the USD high-impact
  release calendar of `cBot/seeds/usd_high_calendar.csv`). No free-text news: it invites hallucinated facts and
  cannot be audited. The model never does arithmetic.
- **Only forward data.** The models' knowledge ends before this experiment; scoring past days would be contaminated.
- **Net:** direction x move in bp, minus the round-trip cost in bp per symbol (from the research's spread and
  commission figures, passed to `score`).
- **Baselines on the same cells:** always long, and previous-day momentum (sign of entry minus the previous day's entry).
- **Verdict per analyst:** `TOO_FEW` below 600 traded calls; `PASS` needs day-clustered net t >= 2.5 and a mean above
  both baselines; otherwise `FAIL`. Even PASS only licenses a demo test of a frozen rule, never agent-chosen trades.

## Power
Six symbols for about 100 weekdays give about 600 calls per analyst, which can only separate a large edge (a hit rate
near 55 % with costs below the move). A smaller edge will read TOO_FEW or FAIL. That is the honest limit of the
experiment.

## Models and analysts
DeepSeek `deepseek-chat` (no reasoning model: the analysts read computed numbers), temperature 0, through an
OpenAI-compatible API (`PAPER_DESK_BASE_URL`, `PAPER_DESK_MODEL`). Three analysts per symbol and day (`trend`,
`meanrev`, `risk`) and a `chief` who sees their answers; the analyst name carries the model (`trend@deepseek-chat`),
so a second model can run beside it. A call that fails or answers something invalid is recorded as direction 0 with the
reason, never left out.

## Data
Dukascopy bid M1 files (`app/dukascopy.py`), aggregated to hours and cached per finished day under `PAPER_DESK_DATA`
(default `data/paper_desk`). Features use only bars closed before 07:00 UTC; entry and exit prices are the open of the
07:00 UTC bar. A day with no price at 07:00 (within two hours) is not scored.
Dukascopy's free feed publishes a day's file only after the day is over (today's file answered 503 or empty at
14:00 UTC on 2026-10-28), so features use complete UTC days only, up to 00:00 UTC of the call date; the entry is 7 hours
later. `asof_utc` and `hours_until_entry` are in the features and in the stored record. The run time therefore does not
matter as long as it is before 07:00 UTC: cron may run at 03:00, 03:20 and 03:40 UTC (10:00-10:40 Vietnam). A newest bar
older than 3 hours before 00:00 UTC withholds the call (a weekend gap does: no call on such a day).

## Costs
2026-10-28 (superseded): assumed round-trip bp EURUSD 1.0, USDJPY 1.0, GBPJPY 1.8, XAUUSD 1.5, US500 1.5, BTCUSD 8.0.

2026-10-29 (in force from the 2026-10-30 call date; calls of 10-29 and earlier were made with the assumed figures in
the prompt, but every call is scored with the measured costs, which the prompt only quotes): measured by
`research/tools/paper_desk_costs.py`, result in `research/results/portfolio/paper_desk_costs_2026-10-29.md`. Each symbol
has a (long, short) pair: spread at the 07:00 UTC minute + commission + the overnight swap of the side, with swap credits
not counted. `COST_BP` in `app/paper_desk_runner.py` holds them; the prompt shows the analyst the mean of the pair. US500
has no calibrated swap fit, so its swap is assumed 0 (a disclosed gap). They set the bar the calls must clear and change
the result: change them only with a new dated section, not silently.

## Running it
    python -m app.paper_desk_runner run [--date YYYY-MM-DD] [--dry-run]   # before 07:00 UTC; needs DEEPSEEK_API_KEY
    python -m app.paper_desk_runner score     # fetches exit prices, prints the table and writes score.json

`DEEPSEEK_API_KEY` is read from the environment (the VPS `.env`) and never written or logged. Nothing is scheduled
by the code: the VPS cron (`/etc/cron.d/agentfx-paper-desk`) runs `run` at 03:00, 03:20 and 03:40 UTC on weekdays and
`score` at 04:30 UTC.

## Dashboard and alerts
The Paper desk view (`#paper-desk`, `/api/paper-desk/status`) shows, from the call log, calls per analyst, how many took
a side (the share of calls that are not 0), how many failed, the last 14 days and the weekdays with no call at all; and
from `score.json` the last score with its time. Telegram (once `TELEGRAM_*` are set) hears of a weekday still without
calls at 05:00 UTC, and of a day where a quarter or more of the calls failed (an ops threshold, not a research one).
The share of calls that take a side decides how long the 600-call bar takes: watch it, do not tune the prompts to raise it
(prompts are fixed by this document).
