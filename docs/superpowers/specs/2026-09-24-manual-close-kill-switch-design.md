# Manual Close & Per-Container Kill Switch — Design

**Date:** 2026-09-24
**Status:** Draft, awaiting review

## Problem

The dashboard can show open positions and start/stop containers, but it cannot act on a
position. When a container misbehaves or a black-swan headline hits, the only options today are:

- **Stop** the container (`/api/bots/{name}/stop`). Its positions stay open at the broker with
  their SL/TP but nobody manages them any more (no trailing, no break-even, no giveback lock).
- Close by hand in the cTrader app, position by position, account by account.

The server has no way to tell a cBot to do anything: cBots only push (`/trade`, `/portfolio/report`,
`/api/tick`, `/ws/cbot`).

## Goals

1. Close a single open position from the **Active Positions** table.
2. Per container, in the **Bots** tab:
   - **Pause / Resume** — block new entries; the container keeps running and keeps managing the
     positions it already has. Pause persists until Resume is clicked (survives service and
     container restarts).
   - **Close & Stop** — pause, close every position the container holds, then stop the container.
   - **Stop** — unchanged (positions left at the broker with SL/TP).
3. Delivery to the bot within ~2–3 s, the same way for all three cBots.
4. No meaningful load at 45 containers.

## Non-goals

- Account-wide or per-strategy panic buttons (not requested).
- Closing positions when the bot is hung or disconnected. That needs the cTrader Open API
  (OAuth + protobuf client) and is a possible later fallback; this design only reports the
  failure and tells the user to close in cTrader.
- Partial closes from the dashboard.
- Timed pauses (1h / end of day). Pause is manual-resume only.

## Decisions (from review, 2026-09-24)

| Question | Decision |
|---|---|
| What the container button does | Three levels: Pause/Resume, Close & Stop, Stop |
| Close scope | Per position (plus the container's close-all inside Close & Stop) |
| Pause lifetime | Until Resume, persisted in the DB |
| Button location | Bots tab (container controls); Active Positions table (per-position Close) |
| Server → bot channel | Each bot polls `GET /api/cbot/commands` every 2 s |
| Access log | Filter the poll path out of `uvicorn.access` |

## Architecture

```
Dashboard ──POST /api/positions/{id}/close──────────┐
Dashboard ──POST /api/bots/{name}/pause|resume──────┤
Dashboard ──POST /api/bots/{name}/close-and-stop────┤
                                                    ▼
                      app/bot_commands.py  (in-memory queue + pause cache, bot_controls table)
                                                    ▲
cBot ──GET /api/cbot/commands?bot_id=X (every 2 s)──┘  → {"paused": bool, "commands": [...]}
cBot ──closes its own position(s) on the main thread
cBot ──POST /api/cbot/commands/{id}/result──────────→ command status for the dashboard
cBot ──POST /portfolio/report (existing)────────────→ DB row closed, dashboard broadcast (existing)
```

Pause is enforced twice:

1. **Server:** `PortfolioManager.check_risk()` refuses entries for a paused `bot_id`. Every entry
   in the standard configuration (`UseAiGateMode=true`, Judas `UseDirectAiApi=false`, which the
   presets set) goes through `/trade`, and both `check_risk` call sites there already pass
   `bot_id`.
2. **Bot:** the poll response carries `paused`, and each cBot skips its own entry paths while it is
   set. This covers the configurations that open without asking the server
   (`UseAiGateMode=false`, Judas `UseDirectAiApi=true`, Judas DCA adds).

## Components

### 1. `app/bot_commands.py` and `app/bot_controls.py` (new)

`app/bot_commands.py` owns the in-memory command queue. `app/bot_controls.py` owns the pause
table and the bot-id helpers (`sanitize_bot_id`, moved from `app/server.py` and re-exported there,
and `bot_id_for_config`), in the same shape as `app/risk_limits.py`. No FastAPI imports; routes
live in `app/dashboard.py` next to the existing `/api/bots` routes.

**Command** (dataclass):
`id` (uuid4 hex), `bot_id`, `action` (`close_position` | `close_all`), `position_id`
(cTrader position id, `close_position` only), `status`, `message`, `closed`, `failed`,
`created_at`, `delivered_at`, `finished_at`.

**Status lifecycle:**

```
pending ──(bot polls)──▶ delivered ──(bot reports)──▶ done | failed
   │                         │
   └─ not polled in 15 s ─▶ expired      └─ no report in 30 s ─▶ unconfirmed
```

- `expired` is final: an expired command is **never** delivered. A bot restarting hours later must
  not pick up a stale close.
- Expiry is evaluated lazily (on `take_pending`, `get`, `enqueue`) against an injectable clock, so
  tests need no sleeps. Constants: `PENDING_TTL_S = 15`, `RESULT_TIMEOUT_S = 30`,
  `RETAIN_S = 600` (finished commands kept for status lookups, then purged).
- `take_pending(bot_id)` returns the bot's pending commands and marks them `delivered` — each
  command is handed out once.
- Duplicate clicks: enqueueing `close_position` for a position that already has a pending or
  delivered command returns that command; same for a second `close_all` on one bot.
- A `threading.Lock` guards the dicts: the poll route runs on the event loop, dashboard routes in
  the threadpool.
- The queue lives in the uvicorn process. This relies on the single-worker deployment
  (`uvicorn app.server:app`, no `--workers`). A service restart drops pending commands, which would
  have expired within 15 s anyway.

**Pause state:**

- Table `bot_controls (bot_id TEXT PRIMARY KEY, paused INTEGER NOT NULL DEFAULT 0, paused_at TEXT,
  updated_at TEXT)`, created next to `risk_limits.init_schema` in `PortfolioManager` init, with
  DDL that `_adapt_query_for_pg` accepts. Upsert via `INSERT ... ON CONFLICT(bot_id) DO UPDATE`
  (SQLite ≥ 3.24 and PostgreSQL).
- `set_paused(bot_id, paused)` writes the DB, then the in-memory `set` of paused bot ids.
- The cache is loaded from the table at startup. The poll route reads only the cache;
  `check_risk` reads the table (it already holds a connection; one query per `/trade`).

### 2. Container name → `bot_id`

Pause state and commands are keyed by `bot_id` (what the bot sends). Bots-tab routes receive the
container name and resolve it with the existing `cbot_watchdog.parse_bot_id(run_command)`, falling
back to the container name (preset containers use `--BotId="<container name>"`). The reverse
lookup (for "is this position's container running?") scans `cbot_configs` the same way.

### 3. Routes

**Bot-facing** (cBots call `127.0.0.1:8000` directly; nginx and its Basic auth are not involved):

| Route | Behaviour |
|---|---|
| `GET /api/cbot/commands?bot_id=X` | `async def`, **never touches the DB or Docker**. `200 {"paused": bool, "commands": [{"id", "action", "position_id"}]}` |
| `POST /api/cbot/commands/{id}/result` | Body `{"bot_id", "status": "done"\|"failed", "message", "closed", "failed"}`. `200 {"ok": true}`; `404` unknown id; `409` if `bot_id` does not own the command |

**Dashboard-facing** (behind nginx Basic auth like every other dashboard route):

| Route | Behaviour |
|---|---|
| `POST /api/positions/{id}/close` | `id` = `positions.id`. `404` not found / not open. `409` no `ctrader_id` ("close it in cTrader"). `409` if the bot's container is configured and not running. Else enqueue `close_position` → `200 {"success": true, "command_id", "status"}` |
| `GET /api/bot-commands/{id}` | Command status as above; `404` unknown/purged |
| `POST /api/bots/{name}/pause` / `/resume` | `404` unknown config. `200 {"success": true, "bot_id", "paused"}` |
| `POST /api/bots/{name}/close-and-stop` | See flow below |
| `GET /api/bots` (existing) | Each entry gains `bot_id`, `paused`, `open_positions` (one grouped `COUNT(*)` query for all bots, not one per bot) |

Every manual action is logged at WARNING with a `[MANUAL]` prefix (shows up in the dashboard log
panel through the existing root-logger WebSocket handler).

`/api/dashboard/positions` and the server-rendered positions query add `p.id` and `p.ctrader_id`
so the table can address a row.

### 4. Close & Stop flow

`async def`; Docker calls run via `asyncio.to_thread` so the event loop is never pinned (see
`tests/test_bot_control_api.py` for why).

1. Resolve `bot_id`; `404` if the config is unknown.
2. Container not running → `409` "container is not running; its positions can't be closed from
   here — use cTrader". Nothing changes.
3. `set_paused(bot_id, True)`. The next poll hands out `paused=true` together with the command, so
   the bot cannot re-enter between the close and the stop.
4. Enqueue `close_all`; poll its status every 0.5 s for up to `CLOSE_AND_STOP_WAIT_S = 20`.
5. `done` with `failed == 0` → `docker stop` → `200 {"success": true, "closed": n}`.
6. Anything else (`expired`, `failed`, `unconfirmed`, timeout) → **do not stop**. The container
   keeps running, paused, still managing SL/trailing on whatever is left.
   `200 {"success": false, "stage": "close", "message": "...", "paused": true}` with the bot's
   own error text when it sent one.
7. Stop fails → `{"success": false, "stage": "stop", ...}`; positions are already closed.

`close_all` is sent even when the DB shows no open positions (the DB can lag the broker); a bot
with nothing open answers `done`, `closed: 0`.

### 5. `check_risk` gate

First check in `PortfolioManager.check_risk()`, before the US-index and loss-limit checks:

```python
if bot_id and bot_commands.is_paused_in_db(conn, bot_id):
    return False, "Paused from dashboard"
```

`check_risk` only runs for entries (`not has_open` pre-check and the final `BUY`/`SELL` guard),
so management of open positions is unaffected.

### 6. Access-log filter

A `logging.Filter` on `uvicorn.access` in `app/server.py` drops records whose request path starts
with `/api/cbot/commands` **and** method is `GET`. Result POSTs and every other route are logged
as before. Without it, 45 containers add ~1.9 M access-log lines/day to journald.

### 7. cBots (`AiAgentBot.cs`, `AsianRangeJudasSweepBot.cs`, `FlowRsiBot.cs`)

Same shape in all three:

- Parameter `[Parameter("Command Poll (ms, 0=off)", Group = <bot's API group>, DefaultValue = 2000, MinValue = 0)] public int CommandPollMs`.
- `StartCommandPoll()` in `OnStart`, **RealTime only** (never in backtests); `StopCommandPoll()` in
  `OnStop`. Base URL derived from `ApiUrl` by stripping `/trade`, as `BuildTickStreamUrl` does.
- Background loop (`Task.Run`, `CancellationTokenSource`), its own `HttpClient` with a 5 s timeout,
  one request in flight, `Task.Delay(CommandPollMs)` between polls. Poll errors are printed at most
  once a minute. On error the last known `paused` value is kept.
- `volatile bool _dashboardPaused` set from each response.
- Each command id goes into a `HashSet<string>` of handled ids before execution (a bot never runs a
  command twice). Execution is marshalled with `BeginInvokeOnMainThread`.
- Own positions only:
  - AiAgentBot: `GetBotPositions()` (label `"AI_Agent"` + symbol).
  - Judas: `Positions.FindAll(label, SymbolName)` (label = container name in presets).
  - FlowRSI: `Positions.FindAll(BotId, SymbolName)`.
- `close_position`: the own position with `Id == position_id`; none → report `failed`,
  "position {id} not found among this bot's open positions".
- `close_all`: every own position.
- Closing goes through `CloseWithReason(pos, "Manual close (dashboard)")` so the existing close
  report carries that reason into `positions.close_reason`. AiAgentBot and Judas already have
  `CloseWithReason`; FlowRSI gets the same `_closeReasons` map + helper, and its
  `OnPositionClosed` reads it.
- `CloseWithReason` returns the `TradeResult` (both `ClosePosition(pos)` and AiAgentBot's
  `pos.Close()` return one); existing callers ignore it, so their behaviour is unchanged.
- Result: `done` when every targeted close is `IsSuccessful`, else `failed` with the broker's
  `TradeResult.Error` per position. Posted from a background task, never blocking the main thread.
- Entry guard: every call that opens or adds to a position returns early with one log line while
  `_dashboardPaused` is set:
  - AiAgentBot: the `ExecuteMarketOrder` entry path (~line 2404).
  - Judas: all six — the indicator entries (~784, ~804), the DCA adds (~1917, ~1930), the AI entry
    in `ExecuteDecision` (~4253) and the Anti-FOMO staged entry in `ExecuteStagedMarketOrder`
    (~4451), where a pause also drops the staged order so a later Resume cannot fire a stale signal.
  - FlowRSI: the single `ExecuteMarketOrder` entry (~1742), reached by both the AI and the
    technical path.
  Partial closes, SL/TP modifications and exits are not guarded.

### 8. UI (`templates/dashboard.html`)

**Active Positions table** (Jinja initial render and `updateDashboard()` JS render):

- New last column with a **Close** button (`log-btn`, loss colour). Empty-state `colspan` 10 → 11.
  `handleLiveTick()` finds cells by class (`.td-mono.font-bold` for the symbol, `.td-current-price`,
  `.td-pnl-live`, `.td-sltp`, `.side-chip`), not by index, so an appended column is safe as long
  as the new cell uses none of those classes.
- Disabled with a tooltip when the row has no `ctrader_id`.
- `confirm()`: "Close BUY XAUUSD 0.10L of cbot-xauusd at market? Current P&L −12.30 $" — prefixed
  with **[LIVE]** on live accounts.
- While in flight: button disabled, "Closing…", `GET /api/bot-commands/{id}` every 1 s (max 35 s).
  `done` → nothing more (the existing broadcast removes the row). `failed` / `expired` /
  `unconfirmed` → `alert()` with the message, button re-enabled. `expired` reads: "The bot did not
  pick up the command within 15 s — it may be stuck. Close the position in cTrader."

**Bots tab:**

- Status cell: **PAUSED** badge when `paused`.
- Buttons: **Pause** / **Resume** (amber, shown for any container, since a stopped container
  resumes paused), and for running containers **Close & Stop** (solid red) beside the existing
  Restart / Stop.
- Close & Stop `confirm()`: "Close N open position(s) of cbot-x at market, then stop the
  container?" ([LIVE] prefix on live). Row locked via the existing `lockBotRow` with
  "Closing & stopping…" (up to ~30 s). On `success: false` → `alert()` with the message, which
  says the container is still running and paused.
- `BOT_ACTION_PENDING` gains `pause`, `resume`, `close-and-stop`.

## Error handling summary

| Situation | Result |
|---|---|
| Bot hung / disconnected / old build without polling | Command `expired` after 15 s; UI says close in cTrader. Close & Stop does not stop. |
| Container stopped | Per-position Close → `409`; Close & Stop → `409`. |
| Position already closed (SL hit meanwhile) | Bot reports `failed: position not found`; the row is already gone from the table. |
| Market closed / broker rejects | Bot reports `failed` with `TradeResult.Error` (e.g. `MarketClosed`). |
| Bot got the command but never reported | `unconfirmed` after 30 s; the DB row still reflects reality via `/portfolio/report`. |
| Double click | Same command id returned. |
| Server restart mid-command | Pending commands lost (they would expire anyway); pause state survives (DB). |
| Poll fails | Bot keeps its last `paused` value and retries in 2 s. |

## Performance

Measured on the dev Mac (uvicorn single worker, keep-alive, trivial `async` dict lookup):
0.061 ms CPU/request without access log, 0.076 ms with it. Assuming the VPS is 3–5× slower,
45 containers × 0.5 req/s ≈ 22.5 req/s ≈ 7 ms CPU per second — under 1 % of one core, about a
tenth of what the existing 1 Hz WebSocket tick stream costs at 45 containers (~1.6 ms/message).
The route must stay DB-free: at the ~86 ms that DB-backed `/api/tick` once cost, 22.5 req/s would
saturate the single worker. A test enforces this.

## Testing

pytest (local `venv/bin/pytest -q`; never against port 8000 — on the dev Mac it tunnels to the VPS):

- `tests/test_bot_commands.py` — queue with a fake clock: enqueue/take once, `expired` after 15 s
  and never delivered afterwards, `unconfirmed` after 30 s, result recording, ownership check,
  duplicate-click dedup, purge after 10 min.
- `tests/test_bot_controls.py` — pause blocks `check_risk`, resume, pause survives a restart,
  `is_bot_paused` never reads the DB, `sanitize_bot_id`, `bot_id_for_config`.
- `tests/test_manual_close_api.py` (TestClient, FakeDocker like `test_bot_control_api.py`):
  - poll route returns `paused` + commands and works with the DB and Docker patched to raise;
  - result route: 404 / 409 / 200;
  - `/api/positions/{id}/close`: 404, 409 no `ctrader_id`, 409 container stopped, 200;
  - pause → `check_risk` returns `(False, "Paused from dashboard")`; resume → allowed; persists
    across a fresh `PortfolioManager`;
  - close-and-stop with the wait constants monkeypatched small: bot reports `done` → stop called;
    `expired` / `failed` → stop not called, still paused; container not running → 409;
  - `/api/bots` includes `bot_id`, `paused`, `open_positions`.
- Access-log filter drops the poll GET record and keeps others.
- `tests/test_cbot_command_poll.py` — source checks on the three `.cs` files (project convention):
  parameter present, poll started only in RealTime, handled-id set consulted before execution,
  `CloseWithReason(..., "Manual close (dashboard)")` used, `_dashboardPaused` guard precedes each
  entry `ExecuteMarketOrder`.
- UI: extend `tests/test_dashboard_ui.py` for the Close column and the new Bots-tab buttons.

cBots cannot be compiled locally (no dotnet); compile on the VPS with `ctrader-console` in a temp
directory, then a live check on one **demo** container: Close a position, Pause (see
`Paused from dashboard` on the next `/trade`), Resume, Close & Stop.

## Deployment

Server first (backward compatible: bots without polling simply never call the new routes), then
bots.

1. Pull on the VPS (`/home/forge/AgentFxTrading`), run pytest, `systemctl restart agentfx.service`,
   check `/api/watchdog/status`. Do not use `scripts/deploy_feature.sh`.
2. Build the three `.algo` files (back up the current ones first), restart one demo container per
   strategy, run the live check above.
3. Restart the remaining containers in batches. Open positions survive a restart (bots re-adopt them
   by label).

No commit or push without the user's go-ahead.

## Known limitations

- A hung or disconnected bot cannot receive commands (Open API fallback is future work).
- AiAgentBot identifies its positions by label `"AI_Agent"` + symbol. Two TMS containers on the
  **same account and symbol** would close each other's positions with `close_all`. The preset grid
  never creates that (one TMS bot per symbol per account); hand-written configs could.
- Right after a bot starts, its local pause guard is unknown until the first poll (≤ 2 s). In the
  standard configuration the server-side gate already covers that window.
