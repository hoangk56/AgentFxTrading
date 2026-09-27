# Backtest Page — Design

**Date:** 2026-09-24
**Status:** Draft, awaiting review

## Problem

There is no way to check a strategy against past prices. Changing a bot parameter means
changing a live container and waiting days to see the effect, and nobody can tell whether a
preset still makes money on recent data.

The cTrader CLI image the bots already run (`ghcr.io/spotware/ctrader-console:latest`) has a
batch `backtest` sub-command that downloads the broker's historical data itself. What is
missing is a way to drive it from the dashboard, keep the results, and compare runs.

## Goals

1. From the dashboard, pick an **installed bot**, change some of its parameters, choose a date
   range, and run a backtest on the VPS.
2. See progress while it runs, then the result: KPIs, equity curve, P&L by hour and weekday,
   the trade list.
3. **Compare 2–4 runs** side by side, including which parameters differ between them.
4. The live bots are unaffected: no writes to the production DB or WebSocket, no cTrader session
   kicks, bounded CPU/RAM.

## Non-goals

- **Judas Sweep and TMS+ORB backtests.** Both enter trades only through the AI (see
  *Spike findings*), so a backtest with the AI off does not show how they trade. A separate spec
  will add a backtest mode to those two cBots. Until then the page lists them as unsupported.
- Replaying AI decisions on history.
- `optimize` (parameter sweeps) and Monte Carlo. The CLI supports both. They can be added
  later on top of this job model.
- Several symbols in one run, scheduled runs, per-user access control (the dashboard is
  behind nginx Basic auth and has no users of its own).

## Decisions (from review, 2026-09-24)

| Question | Decision |
|---|---|
| Main use | Change parameters, re-run, compare |
| Starting parameters | The installed bot's `run_command` (what actually runs live) |
| Scope of v1 | FlowRSI only; Judas / TMS+ORB backtest mode is a follow-up spec |
| Where jobs run | In-process asyncio worker in the FastAPI app (like `cbot_watchdog`), one container per job |
| Concurrency | One job at a time, FIFO queue in the DB |
| Default data mode | `ticks` (real spread); `m1` only with an explicit spread |

## Spike findings (VPS, 2026-09-24)

All runs used FlowRSI EURUSD M15 24/07/2026–23/09/2026 on demo account 10115236 with the live
container's parameters and `UseAiGateMode=false`. The containers used bridge networking.

| | `m1` | `ticks` |
|---|---|---|
| Wall time | ~1.5 min | ~2 min |
| Data cache | 1 MB | 14 MB |
| Container RAM | 80–140 MB | 95–140 MB |
| Trades (W/L) | 69 (41/28) | 66 (38/28) |
| Net profit | −74.68 | **−296.32** |
| Profit factor | 0.94 | 0.77 |

- `m1` mode backtests with **spread 0** (`main.spread.value = 0` in the report), which hides
  three quarters of the loss here. That is why `ticks` is the default and `m1` requires
  `--spread`.
- `--report-json` gives everything the UI needs: `main`, `equity.points`,
  `tradeStatistics`, `history.items` (every closed trade), `parameters`. The per-hour/weekday
  sections only count winning and losing trades, so P&L by hour is computed from
  `history.items`.
- `ctrader-cli metadata <algo>` prints every cBot parameter with group, type (`Boolean`,
  `Integer`, `Double`, `String`, `Enum` with `EnumValues`, `TimeFrame`), default and min/max, in
  ~15 s. The parameter form is generated from it.
- `--end` is inclusive: the 23/09 run stopped at `23/09/2026 23:59`. A one-day range
  (`--start` = `--end`) works.
- Enum and `TimeFrame` parameters are accepted by name (`--SlMode=ATR_Multiplier`,
  `--MacroTimeFrame=Hour4`). A named Docker volume works as `--data-dir`.
- **The cBots still reach for the network while backtesting.** Judas logged
  `HTTP calls ENABLED in mode: SilentBacktesting` and tried the TickStream WebSocket all run. AiAgentBot's
  position reports have no `RunningMode` guard. On `--network host` they would reach
  `127.0.0.1:8000` and write fake trades and ticks into production. On bridge networking they failed
  harmlessly: `agentfx` logged no request from the test containers.
- Backtest logins did not disconnect the live bots on the same account: no cTrader
  reconnects in the live containers during either run.
- Judas with `UseAiGateMode=false` runs its LEGACY entry path and opened **1 trade in two
  months**. That path is not what runs live.
- AiAgentBot places orders only in `ExecuteDecision` (the AI's answer). It has no technical path.

## Architecture

```
Dashboard (view-backtest)
   │  GET  /api/backtests/sources, /sources/{bot}/params
   │  POST /api/backtests            ──► backtest_jobs row (status=queued)
   │  GET  /api/backtests[/{id}]     ◄── rows + webui_data/backtests/<id>.json
   ▼
app/backtest_api.py (APIRouter) ──► backtest_params / backtest_command / backtest_store
                                                  ▲
app/backtest_worker.py (asyncio loop, started in lifespan)
   ├─ picks the oldest queued job when nothing runs
   ├─ docker SDK: containers.run(bt-<id>, bridge, ro mounts, limits)
   ├─ every 3 s: container status + `logs --tail` → phase / progress
   ├─ on exit: get_archive(/tmp/report.json) → backtest_report → store + file
   └─ on startup: reconcile containers labelled agentfx.backtest
```

### Modules

Each module has one job and can be tested on its own. Only the worker and the metadata fetch
touch Docker.

| Module | Responsibility | Depends on |
|---|---|---|
| `app/backtest_command.py` | Pure. Parse a bot's `run_command` into a `BotSource`; map container paths to host paths; build the container spec (args list, mounts, limits) for a job; the locked-parameter table. | `cbot_presets.DEFAULT_IMAGE`, `ctrader_accounts.ctrader_home()` |
| `app/backtest_params.py` | Fetch and cache `metadata` per `.algo` SHA-256; merge metadata defaults with the bot's values; validate overrides. | docker SDK (metadata only), `backtest_command` |
| `app/backtest_report.py` | Pure. cTrader report JSON → `summary` dict and the UI payload (downsampled equity, trades, P&L by hour/weekday). | — |
| `app/backtest_store.py` | `init_schema`, create/list/get/update/delete on `backtest_jobs`; report file read/write/delete. | `app.db` |
| `app/backtest_worker.py` | The queue loop, container lifecycle, progress, timeout, cancel, startup reconcile. | all of the above, docker SDK |
| `app/backtest_api.py` | FastAPI router; request validation; 4xx/5xx mapping. | all of the above |

`server.py` includes the router and starts/stops the worker in `lifespan` next to the watchdog.
`portfolio.py` calls `backtest_store.init_schema(conn)` next to `bot_controls.init_schema`.

## Bot source and parameters

**Eligible bots:** rows of `cbot_configs` whose `run_command` runs `FlowRsiBot.algo`.
`GET /api/backtests/sources` also returns the other bots, with `supported: false` and a reason
("Judas/TMS+ORB enter only through the AI; backtest mode not implemented yet").

**Parsing `run_command`** (`shlex`, after the same whitespace/backslash normalisation
`docker_manager.start_container` does). The parser extracts:

- the algo path `/workspace/cBot/<Algo>.algo` → host `<project_root>/cBot/<Algo>.algo`
- `--ctid`, `--account`, `--symbol`, `--period`
- `--pwd-file=/root/ctrader_data/<file>` → host `<CTRADER_HOME>/ctrader_data/<file>`. The
  resolved path must stay inside `<CTRADER_HOME>/ctrader_data` and exist; otherwise the source
  is unsupported ("password file not found").
- every other `--Key=value` pair that names a cBot parameter, with surrounding quotes stripped

Docker flags (`-d`, `--name`, `--network`, `-v`, `--restart`) and CLI flags (`--full-access`)
are not cBot parameters and are dropped.

**Metadata:** `docker run --rm -v <algo>:/algo/<Algo>.algo:ro <image> metadata /algo/<Algo>.algo`,
parsed as JSON. It is cached in memory and in `webui_data/backtests/metadata/<sha256>.json`,
keyed by the `.algo` file's SHA-256. A rebuilt `.algo` gets fresh metadata on first use. The
`BuildTime` goes into each job (`algo_build_time`).

**Value of each parameter** = the bot's `run_command` value if present, else the metadata default.

**Locked parameters.** The client never sees them as editable, and the server applies them
last, after overrides:

| Parameter(s) | Forced value | Why |
|---|---|---|
| `BotId` | `bt-<id>` | Keeps backtest trades from ever matching a live bot id |
| `AccountLabel` | `backtest` | Same |
| `UseAiGateMode` | `false` | Technical execution; the AI is not called in backtests |
| `ApiUrl`, `AiTelemetryUrl`, `AiReportUrl` | `http://127.0.0.1:9/disabled` | Unreachable on purpose (second line of defence after bridge networking) |
| `CommandPollMs` | `0` | No dashboard command polling |
| `EnableNewsFilter` | `false` | There is no historical news calendar |
| `EnableTelegramAlerts`, `SendChartScreenshot`, `SendAiAdjustAlerts` | `false` | No alerts from backtests |
| `TelegramBotToken`, `TelegramChatId` | empty | Never passed to a backtest container |

The whole metadata groups `AI Agent Integration`, `News Filter` and `Telegram Integration`
are hidden from the form. The table lives in `backtest_command.LOCKED_PARAMS["flowrsi"]`. A
parameter in a hidden group that is not in the table keeps the bot's value and stays hidden.

**Override validation** (422 on the first failure, naming the key):

- the key exists in the metadata and is not locked or hidden
- `Integer`: an int within `MinValue`/`MaxValue` when given
- `Double`: a finite number within `MinValue`/`MaxValue` when given
- `Boolean`: `true`/`false`
- `Enum`: one of the `EnumValues` names, or the enum's int value (looked up and stored as the
  name); it is sent by name (verified: `--SlMode=ATR_Multiplier` shows up as `cmd arg` in the
  CLI's parameter table)
- `TimeFrame`: one of `Minute, Minute5, Minute15, Minute30, Hour, Hour4, Daily`, sent by name
  (verified with `--MacroTimeFrame=Hour4`). The metadata default comes as
  `{"Type": 0, "Size": <minutes>}` and is mapped to the name for display.
- `String`: at most 200 characters, with no newline or NUL

An override equal to the bot's value is dropped, so `overrides` only holds real changes.

## Run configuration

| Field | Rule |
|---|---|
| `bot_name` | An eligible `cbot_configs` name |
| `start`, `end` | Dates (UTC). `start ≤ end` (a single day works), `end ≤ today`, span ≤ 365 days. Passed as `dd/MM/yyyy`; `end` is inclusive |
| `data_mode` | `ticks` (default) or `m1` |
| `spread_pips` | Required, finite and `> 0` when `data_mode = m1`; must be absent for `ticks` |
| `balance` | Finite, 100 – 10 000 000, default 10 000 |
| `note` | Optional, ≤ 200 characters |
| `overrides` | `{key: value}`, validated as above |

Commission is always `--commission-auto` (the symbol's real commission).

## Container

For job `<id>` the worker calls `docker.containers.run` with:

- `image`: `cbot_presets.DEFAULT_IMAGE`
- `name`: `bt-<id>`; `labels`: `{"agentfx.backtest": "<id>"}`
- `network_mode`: `"bridge"`
- `mem_limit`: `"1g"`; `nano_cpus`: `2_000_000_000`; `cpu_shares`: `256`
- `detach`: `True`; `auto_remove`: `False` (the report is read after exit)
- `volumes`:
  - host `.algo` → `/algo/<Algo>.algo`, `ro`
  - host password file → `/secrets/pwd`, `ro`
  - named volume `agentfx-bt-cache` → `/bt-cache`, `rw` (Docker creates it on first use)
- `command` (a list; no shell):

```
backtest /algo/<Algo>.algo
--ctid=<ctid> --pwd-file=/secrets/pwd --account=<account>
--symbol=<symbol> --period=<period>
--start=<dd/MM/yyyy> --end=<dd/MM/yyyy> --data-mode=<ticks|m1> [--spread=<pips>]
--data-dir=/bt-cache --balance=<balance> --commission-auto
--report-json=/tmp/report.json --full-access --exit-on-stop
--<Param>=<value> …            (bot values, then overrides, then locked values)
```

The report stays inside the container and is read with `container.get_archive`. The app,
running as `forge`, then writes it to `webui_data/backtests/<id>.json`. No root-owned files
end up on the host.

## Job lifecycle

```
queued ──► running ──► done
   │          ├──────► failed      (non-zero exit, no report, timeout, lost)
   └──────────┴──────► cancelled
```

The worker loop runs every 3 s. Docker SDK calls go through `asyncio.to_thread`.

1. **Nothing running:** take the oldest `queued` job, build the spec, start the container,
   set `running`, `started_at`, `phase = starting`. If the start fails, set `failed` with the
   Docker error.
2. **Running:**
   - Read the container state, and `logs --tail 20` for the last line matching
     `^Progress \| (.+?) \| ([\d.]+) %`. `Loading …` maps to `phase = loading`, `Backtesting` to
     `phase = backtesting`, and the number to `progress`.
   - Exited with 0: extract `/tmp/report.json`, parse, write the file, store `summary`, set
     `done`, `finished_at`, remove the container.
   - Exited non-zero or no report: set `failed` with the last 50 log lines, remove the container.
   - Running longer than 45 min: stop and remove it, set `failed` with `error = "timeout (45 min)"`.
3. **Cancel:** a `queued` job just becomes `cancelled`. For a `running` job the API marks it
   `cancelled`, and the worker stops and removes the container on its next tick.
4. **Startup reconcile:** for every job still `running`, look for a container labelled
   `agentfx.backtest=<id>`:
   - running → keep polling it
   - exited → collect it as in step 2
   - missing → `failed`, `error = "container lost"`

   Containers labelled `agentfx.backtest` whose job is not running (for example deleted
   rows) are removed.

The worker assumes one app process. `agentfx.service` runs uvicorn without `--workers`. If that
ever changes, the worker needs a DB lock.

## Data model

```sql
CREATE TABLE IF NOT EXISTS backtest_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_name TEXT NOT NULL,
    strategy TEXT NOT NULL,          -- 'flowrsi'
    symbol TEXT NOT NULL,
    period TEXT NOT NULL,
    algo TEXT NOT NULL,              -- 'FlowRsiBot.algo'
    algo_sha TEXT,
    algo_build_time TEXT,
    ctid_email TEXT NOT NULL,        -- login used to download the data (not a secret); `ctid` is a PostgreSQL system column
    account TEXT NOT NULL,
    pwd_file TEXT NOT NULL,          -- container path /root/ctrader_data/<file>; never the password
    start_date TEXT NOT NULL,        -- 'YYYY-MM-DD'
    end_date TEXT NOT NULL,
    data_mode TEXT NOT NULL,         -- 'ticks' | 'm1'
    spread_pips DOUBLE PRECISION,
    balance DOUBLE PRECISION NOT NULL,
    overrides TEXT NOT NULL,         -- JSON {key: {"from": bot value, "to": new value}}, only real changes
    params TEXT NOT NULL,            -- JSON, the bot's --Key=value pairs with overrides applied; locked
                                     -- keys are left out and appended by the worker for the job's id
    note TEXT,
    status TEXT NOT NULL,            -- queued | running | done | failed | cancelled
    phase TEXT,                      -- starting | loading | backtesting | done
    progress DOUBLE PRECISION,
    error TEXT,
    summary TEXT,                    -- JSON, see below
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
)
```

It works on SQLite and PostgreSQL through `app.db`'s adapter (`AUTOINCREMENT` → `SERIAL`).
Rows are created with `INSERT … RETURNING id`, which both support (SQLite ≥ 3.35; the VPS has
3.46). The adapter has no `lastrowid` on PostgreSQL. Numbers are `DOUBLE PRECISION`, not
`REAL`: PostgreSQL's `REAL` is float4, and it turned spread 1.2 into 1.2000000476837158. Ctid, account and
password-file path are stored so a queued job still runs after its bot is deleted. Timestamps are UTC
`YYYY-MM-DD HH:MM:SS`, as in `bot_controls`.

**Report file:** `webui_data/backtests/<id>.json` (~0.8 MB each; `webui_data/` is
git-ignored). It is deleted together with its row. There is no automatic retention.

**`summary`** (from the report):

- `net_profit` = `tradeStatistics.netProfit.all`, `roi_pct` = `main.roi`,
  `starting_capital`, `ending_equity`
- `profit_factor`, `total_trades`, `winning_trades`, `losing_trades`, `win_rate`
- `avg_trade`; `avg_win` and `avg_loss`, computed from `history.items[].net`
- `max_equity_dd_pct` and `max_equity_dd` (from `equity`, rounded to 2 dp like the rest of
  `summary`; the report file keeps full precision), `max_balance_dd_pct`
- `commissions`, `swaps`, `largest_win`, `largest_loss`, `max_consecutive_losses`
- `long_net`, `short_net`, `long_trades`, `short_trades`

## API

All routes live in `app/backtest_api.py`, included by `server.py`.

| Method | Path | Returns / does |
|---|---|---|
| GET | `/api/backtests/sources` | `{sources: [{name, strategy, symbol, period, account_label, supported, reason}], docker_available}` |
| GET | `/api/backtests/sources/{bot}/params` | `{groups: [{name, params: [{key, label, type, default, bot_value, min, max, enum_values}]}], locked: {key: value}, timeframes, algo_build_time}`. 404 unknown bot, 422 unsupported, 502 metadata failure, 503 Docker unavailable |
| POST | `/api/backtests` | Validates, stores a `queued` job, returns `201 {id, status, queue_position}`. 422 on invalid input (including a non-finite `spread_pips` or `balance`), 503 without Docker |
| GET | `/api/backtests` | Jobs, newest first, without the report or `params`: id, bot, symbol, dates, data mode, overrides, note, status, phase, progress, error, summary, timestamps |
| GET | `/api/backtests/{id}` | Job plus `report`: `equity` (≤ 1 000 points, first and last kept), `trades`, `pnl_by_hour[24]`, `pnl_by_weekday[7]` (net and count per bucket, by UTC entry time) |
| GET | `/api/backtests/{id}/report.json` | The raw cTrader report file |
| POST | `/api/backtests/{id}/cancel` | `queued`/`running` → `cancelled`; 409 otherwise |
| DELETE | `/api/backtests/{id}` | Deletes the row and file. 409 while `queued`/`running` (cancel first) |

## UI

A new sidebar item **Backtest** (`view-backtest`, Lucide `flask-conical`). It reuses
`kpi-card`, `panel`, the table styles and Chart.js from the existing dashboard. The page's code
lives in `static/js/backtest.js`, loaded with `defer` rather than added to the dashboard's 3 000-line
inline script. Its `bt*Html` renderers are pure functions, so node tests can render them.

```
┌ New run ──────────────────────────────────────────────────────────┐
│ Bot [cbot-demo-demo-eurusd-all-flowrsi ▾]  From [24/07] To [23/09]│
│ Data [ticks ▾]  Balance [10000]  Note [__________]                │
│ ▸ Nested RSI Engine   ▸ SMC & ICT   ▾ Risk Management (1 changed) │
│     TargetRiskReward  [2.0]  (bot: 1.5) ↺                         │
│ 🔒 Locked for backtests: AI gate off · News off · Telegram off     │
│ ⚠ Technical logic only — the live bot filters entries with the AI │
│                                                 [ Run backtest ]  │
├ Runs ──────────────────────────────────────────── [Compare (2)] ──┤
│ ☑ #12 EURUSD 24/07–23/09  RR 1.5→2.0  ✅ −120$ PF 0.90 DD 4%   ⋯ │
│ ☑ #11 EURUSD 24/07–23/09  (bot)       ✅ −296$ PF 0.77 DD 4%   ⋯ │
│ ☐ #13 GBPJPY …                        ⏳ Backtesting 42% ▓▓░░  ⋯ │
└───────────────────────────────────────────────────────────────────┘
```

1. **New run form**
   - Unsupported bots are disabled, and their reason shows as a tooltip.
   - Parameter groups come from `/params` and are collapsible. A changed field is
     highlighted, shows the bot's value, and has a ↺ reset. Each group header counts its changes.
   - Default range: the last 60 days, ending yesterday. Choosing `m1` reveals a required spread field.
   - The "technical logic only" notice is always visible.
2. **Runs table**
   - Columns: overrides as chips (`TargetRiskReward 1.5→2.0`, or "(bot)" when none), status
     with a progress bar, Net P&L, PF, Win %, Max DD, trades, note.
   - Row actions: **View · Clone · Cancel · Delete**. **Clone** fills the form with that run's
     bot, dates, data mode, balance and overrides.
   - The table polls `GET /api/backtests` every 3 s while any job is queued or running, and stops otherwise.
3. **Run detail** (View)
   - KPI cards: Net P&L, ROI, PF, Win %, trades, max equity DD, avg win / avg loss, commission + swap.
   - Equity chart; P&L by hour and by weekday (bars).
   - Trade table with UTC times, direction, lots, entry/exit, pips, net.
   - The changed parameters, and a link to `report.json`.
   - A failed run shows its `error` / log tail instead.
4. **Compare** (2–4 `done` runs)
   - KPI table with one column per run. The oldest selected run is the baseline, the other
     columns show Δ against it, and the best value per row is bold. Higher is better for net
     profit, ROI, PF, win rate, avg trade and avg win. Lower is better for max DD and trade count
     is neutral. For avg loss and largest loss, the value closest to zero is best; commissions and
     swaps are shown as two separate rows, each scored the same way.
   - Equity curves overlaid as % return from each run's starting balance.
   - A table of **only the parameters whose values differ** between the runs. It is taken from
     each report's `parameters` (the values the run actually used, defaults included), ignoring
     `BotId` and `AccountLabel`.
   - A warning when the runs differ in date range, data mode, symbol or `algo_build_time`.

Every value that comes from a bot, the metadata or the user (note, parameter values, bot names,
error text) is rendered with `textContent` or the dashboard's escape helper, as
`tests/test_dashboard_xss.py` checks for the existing renderers.

## Safety invariants

Each one has a test in `tests/test_backtest_command.py` that fails the build if it breaks:

1. `network_mode` is `"bridge"`. The spec never contains `host`.
2. The only mounts are the `.algo` (ro), the password file (ro) and `agentfx-bt-cache`. The
   project root and `CTRADER_HOME` are never mounted.
3. Locked parameters appear after every override and bot value, with the forced values. An
   override of a locked or hidden key is rejected before the spec is built.
4. The container is named `bt-<id>` and labelled `agentfx.backtest=<id>`. The worker only
   stops or removes containers carrying that label.
5. `mem_limit`, `nano_cpus` and `cpu_shares` are always set.
6. The command is a list, and it contains `--pwd-file=/secrets/pwd`, never a password.

## Error handling

| Case | Behaviour |
|---|---|
| Docker unavailable (e.g. local Mac) | `POST` and `/params` → 503; lists still work; the worker idles |
| `metadata` fails or returns non-JSON | `/params` → 502 with the first lines of output |
| Password file missing or outside `ctrader_data` | Source `supported: false`, reason shown |
| Container fails to start | Job `failed` with the Docker error |
| Non-zero exit / missing report (e.g. wrong password, unknown symbol) | Job `failed` with the last 50 log lines |
| Report JSON unparsable (including valid JSON of an unexpected shape) | Job `failed`; the raw file is kept for inspection |
| Report cannot be written to disk, or any other unexpected error handling a running job | Job `failed` with `report not saved: …` or `worker error: …`; the container is removed and the queue is never blocked |
| > 45 min | Container stopped and removed; `failed: timeout (45 min)` |
| Service restart mid-run | Startup reconcile (see *Job lifecycle*) |
| Bot deleted from `cbot_configs` after the job was queued | The job keeps its stored `params`, so it still runs |

## Testing

- `tests/test_backtest_command.py`
  - Parse fixtures made with `cbot_presets.build_run_command`, plus a hand-written FlowRSI
    command with quotes and backslash continuations.
  - Host path mapping, and rejection of `--pwd-file` paths that escape `ctrader_data`.
  - The six safety invariants.
  - `dd/MM/yyyy` dates; `--spread` present exactly when `m1`.
- `tests/test_backtest_params.py`
  - A trimmed copy of the real FlowRSI `metadata` output as fixture.
  - Merge order; each type's validation, including min/max and enum names.
  - Locked, hidden and unknown keys rejected; no-op overrides dropped.
- `tests/test_backtest_report.py`
  - A trimmed real report as fixture (a few trades, a few hundred equity points).
  - Summary values; `avg_win`/`avg_loss`; P&L by hour and weekday.
  - Downsampling keeps ≤ 1 000 points including the first and last.
- `tests/test_backtest_worker.py`
  - A fake Docker client drives queued→running→done, non-zero exit, missing report, timeout,
    cancel of queued and running jobs, and every startup reconcile case.
  - Only one job runs at a time.
- `tests/test_backtest_api.py`
  - `TestClient` against SQLite (conftest already redirects the DB).
  - Create/list/get/cancel/delete, the 404/409/422/503 paths, unsupported bots.
- `tests/test_dashboard_xss.py` gains cases for the backtest renderers (note, parameter
  values, error text). Like the existing node-driven cases, it skips on the VPS.
- **Acceptance on the VPS after deploy:**
  1. Run `cbot-demo-demo-eurusd-all-flowrsi` for 24/07/2026–23/09/2026, `ticks`, balance 10 000,
     once by hand with the spike's `docker run … backtest` command, then through the page with
     no overrides. Trade count and net profit must match exactly. (The spike numbers,
     66 trades and −296.32, came from the `FlowRsiBot.algo` build that was replaced at 16:34 UTC
     on 2026-09-24. They are not the baseline.)
  2. Clone the run with one override and check that Compare lists exactly that parameter as
     different.
  3. While the run is going, check that no live container logs a cTrader reconnect and that
     `agentfx` logs no request from a `bt-*` bot id.

## Rollout

- App-only change: `systemctl restart agentfx.service` away from M15 bar closes. There is no
  cBot rebuild and no container restart.
- `agentfx-bt-cache` is created on the first run. Ticks take ~7 MB per symbol-month, so a year
  on all 15 symbols is ~1.3 GB. `docker volume rm agentfx-bt-cache` clears it, and the next run
  downloads the data again.
- Remove `/home/forge/backtest_tmp` (left by the spike) once the page works.

## Follow-ups

- **Backtest mode for Judas and TMS+ORB** (own spec). Two parts:
  - A `RunningMode`-aware path that takes the gate's signal in the gate's direction with
    the technical SL/TP.
  - `RunningMode.RealTime` guards on every HTTP/WebSocket call: Judas TickStream, AiAgentBot
    position reports.

  When it lands, `backtest_command` adds the strategy to `LOCKED_PARAMS`, and the sources endpoint
  starts reporting those bots as supported.
- `optimize` and Monte Carlo on top of the same job table.
- FlowRSI note from the spike: with `TargetRiskReward = 1.5` the average winner (+28.86) was smaller
  than the average loser (−44.93) in the `m1` run. The trailing or early-close logic may be
  cutting winners short. Worth a look with this page once it exists.
