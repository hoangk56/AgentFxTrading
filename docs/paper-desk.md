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

## Costs (registered assumptions)
Round-trip bp per symbol, `COST_BP` in `app/paper_desk_runner.py`: EURUSD 1.0, USDJPY 1.0, GBPJPY 1.8, XAUUSD 1.5,
US500 1.5, BTCUSD 8.0. IC commission plus a typical spread, rounded up; not measured medians. They set the bar the calls
must clear and change the result: replace them with measured values in a new dated section, not silently.

## Running it
    python -m app.paper_desk_runner run [--date YYYY-MM-DD] [--dry-run]   # before 07:00 UTC; needs DEEPSEEK_API_KEY
    python -m app.paper_desk_runner score

`DEEPSEEK_API_KEY` is read from the environment (the VPS `.env`) and never written or logged. Nothing is scheduled
yet: a cron entry that runs `run` at about 06:30 UTC on weekdays, and a view on the dashboard, are not built.
