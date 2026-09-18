# Docker Instance Setup Screen — Design (Phase 2)

**Date:** 2026-09-18
**Status:** Approved (brainstorm), pending implementation plan
**Depends on:** Phase 1 (`CTRADER_HOME` in `.env`, `ctrader_data/` directory)

## Goal

Replace "paste a 40-line `docker run` command" with a screen where the user picks
a cTrader account, ticks symbols per strategy, and clicks once. The screen
generates the exact commands the README documents, saves them as `cbot_configs`
rows, and starts the containers.

## Decisions already made

| Question | Decision |
|---|---|
| Symbol choice | Grid of symbol × strategy limited to the README-tuned presets. No free-form symbols, no parameter editing. |
| Account info | Saved in a new `ctrader_accounts` table and reusable. The cTID password is written to a file, never stored in the DB. |
| On submit | Save config **and** start the container, with a "save only" opt-out. |
| Placement | Inside the existing **Docker Bot Management** view as an inline panel, same style as the current add-bot form. |

## Data model

### New table `ctrader_accounts`

Created in `AccountRegistry._init_schema` (`app/accounts.py`), alongside `accounts`.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `slug` | TEXT UNIQUE | `<account_type>-<slugified label>`, e.g. `demo-main`, `live-ic`. Lowercase, `[a-z0-9-]`, max 24 chars. |
| `ctid_email` | TEXT NOT NULL | |
| `account_number` | TEXT NOT NULL | |
| `account_type` | TEXT CHECK IN ('live','demo') | |
| `label` | TEXT NOT NULL | human label as typed |
| `pwd_file` | TEXT NOT NULL | **in-container** path: `/root/ctrader_data/ctid_<slug>_pwd` |
| `created_at` | TEXT DEFAULT CURRENT_TIMESTAMP | |

The DDL must work on both SQLite and PostgreSQL through the existing
`_adapt_query_for_pg` layer (use `INTEGER PRIMARY KEY AUTOINCREMENT` → adapted to
`SERIAL`, as `cbot_configs` already does).

### Password file

- Host path: `$CTRADER_HOME/ctrader_data/ctid_<slug>_pwd`, written with mode
  `0600`, parent dir created `0700` if missing.
- `CTRADER_HOME` comes from `.env` (Phase 1 writes `/home/forge/ctrader`); default
  `/root` so the existing production box (which mounts `/root:/root`) keeps working.
- The password is accepted in the `POST` body only, written to disk, and dropped.
  It is never logged, never stored, never returned.

### `accounts` table side effect

Creating a cTrader account also calls the existing `AccountRegistry` upsert with
`account_id=<type>-<number>`, `label`, `is_configured=1`, so the dashboard's
account tabs show it immediately.

## Presets — `app/cbot_presets.py` (new)

```python
STRATEGIES = {
    "tms_orb": {"label": "TMS+ORB",     "algo": "AiAgentBot.algo",              "suffix": ""},
    "judas":   {"label": "Judas Sweep", "algo": "AsianRangeJudasSweepBot.algo", "suffix": "-judas"},
    "flowrsi": {"label": "FlowRSI",     "algo": "FlowRsiBot.algo",              "suffix": "-flowrsi"},
}

# (strategy, SYMBOL) -> {"period": "m15", "session": "New York", "params": {...}}
PRESETS = { ... }
```

`params` holds only the **strategy-tuned** flags copied verbatim from the README
block for that symbol (e.g. `OrbStartHour`, `MinDecisiveBreakoutPips`,
`minAsianRangePips`, `FastRsiPeriod`, `RiskPerTradePercent`…). Infrastructure
flags are **not** in presets; the builder emits them.

The matrix, taken from README `docker run` blocks (`--period` flag is the source
of truth where a heading disagrees, e.g. DE40 is `m15`):

| Symbol | TMS+ORB | Judas | FlowRSI |
|---|---|---|---|
| XAUUSD | m15 | m15 | |
| EURUSD | m15 | m15 | m15 |
| GBPUSD | m15 | m15 | |
| USDJPY | m15 | | |
| GBPJPY | m15 | m15 | |
| EURJPY | m15 | m15 | |
| USDCAD | m15 | | |
| AUDUSD | m15 | | |
| AUDJPY | m15 | | |
| US30 | m15 | | |
| USTEC | m5 | | |
| DE40 | m15 | | |
| UK100 | m15 | m15 | |
| BTCUSD | | m15 | |
| ETHUSD | | m15 | |

15 symbols, 22 cells.

### Command builder

```python
def build_run_command(account: dict, strategy: str, symbol: str,
                      project_root: str, ctrader_home: str,
                      image: str = "ghcr.io/spotware/ctrader-console:latest") -> str
```

Output is a single-line command (the existing `docker_manager.start_container`
normalises whitespace and `shlex.split`s it, so no backslash continuations).

- Container name: `cbot-<slug>-<symbol lower><suffix>`, e.g.
  `cbot-live-ic-xauusd-judas`. Because `slug` starts with `live-` for live
  accounts, the existing live/demo detection in `/api/bots` (`"live-" in name`)
  works without changes.
- Fixed prefix: `docker run -d --name <name> --restart unless-stopped --network host -v <project_root>:/workspace -v <ctrader_home>:/root <image> run /workspace/cBot/<algo>`
- Infrastructure flags, every strategy: `--ctid=<email> --pwd-file=<pwd_file> --account=<number> --symbol=<SYMBOL> --period=<period> --full-access --BotId="<name>" --ApiUrl="http://127.0.0.1:8000/trade" --AccountLabel="<label>"`
- Judas only, additionally: `--label="<name>" --DashboardServerUrl="http://127.0.0.1:8000"`
- Then every `params` entry as `--Key=value` (booleans lowercase, strings quoted
  with double quotes as the README does).

Values that go into quotes (`label`, `AccountLabel`) are validated at account
creation to contain no `"` or newline, so the generated string always survives
`shlex.split`.

## API (in `app/dashboard.py`, next to the `/api/bots` routes)

| Method | Path | Request | Response |
|---|---|---|---|
| `GET` | `/api/ctrader-accounts` | | `{"accounts": [{id, slug, ctid_email, account_number, account_type, label, created_at}]}` — no `pwd_file`, no password |
| `POST` | `/api/ctrader-accounts` | `{label, ctid_email, password, account_number, account_type}` | `201 {"success": true, "account": {...}}`; `409` if slug exists; `422` on validation |
| `DELETE` | `/api/ctrader-accounts/{id}` | | `{"success": true}`; deletes row and the password file; `404` if missing. Does **not** touch `cbot_configs` (their commands are self-contained). |
| `GET` | `/api/setup/presets` | | `{"strategies": {...}, "symbols": [...], "cells": [{symbol, strategy, period, session}]}` |
| `POST` | `/api/setup/instances` | `{account_id, selections: [{symbol, strategy}], start: true}` | `{"results": [{symbol, strategy, name, status: "started"\|"saved"\|"exists"\|"error", message}]}` |

`POST /api/setup/instances` per selection:
1. Look up preset; unknown pair → `error`.
2. `build_run_command(...)`.
3. `pm.add_cbot_config(name, description, cmd)`; if it returns `False` (name
   exists) → `exists`, skip start.
4. If `start` → `docker_manager.start_container(name, cmd)`; success → `started`,
   failure → `error` with the docker message (config row is kept so the user can
   retry from the bots table).
5. If not `start` → `saved`.

`description` is `"<Strategy label> <SYMBOL> <period> — <account label>"`.

## UI (`templates/dashboard.html`, Docker view)

New button **Setup Instances** next to **Add Bot**. Toggles `#setup-panel`
(hidden by default; same visual style as `#bot-form-container`). Contents:

1. **Account row** — `<select id="setup-account">` populated from
   `GET /api/ctrader-accounts`, plus a final option "＋ New account…" that reveals
   inputs: Label, cTID email, Password (`type=password`), Account number,
   Live/Demo radio, and a **Save account** button that POSTs and re-selects the
   new account. Delete (🗑) next to the select for the current account, with
   `confirm()`.
2. **Grid** — `<table>` rows = symbols, columns = strategies; a cell has a
   checkbox only when a preset exists, `title` shows `period · session`. Column
   header has a "select all" checkbox.
3. **Footer** — `<label><input type=checkbox id="setup-save-only"> Save only, don't start</label>`
   and **Create instances** (disabled until an account is selected and ≥1 cell is
   ticked).
4. **Results** — after POST, a list under the footer: one line per cell with an
   icon (✅ started / 💾 saved / ⏭ exists / ❌ error + message). Then `loadBots()`
   refreshes the table below.

JavaScript lives in the same inline `<script>` as the rest of the Docker view,
following the existing `fetch` + `renderBots` style. No new CSS file; reuse
`log-input`, `log-btn`, `data-table`, `bot-form-grid`.

## Error handling

- Account creation validates: email contains `@`; account number is digits only;
  label 1–40 chars, no `"`/newline; password non-empty; slug uniqueness.
- If the password file cannot be written (permissions, missing `CTRADER_HOME`),
  the DB row is **not** created and the API returns `500` with the OS error.
- `POST /api/setup/instances` never aborts the batch: each selection reports its
  own status.
- Account endpoints use HTTP status codes for client errors (422 validation,
  409 duplicate slug, 404 not found) with a JSON `{"success": false, "message"}`
  body. `POST /api/setup/instances` always returns 200 and reports per-selection
  outcomes in the body, matching the existing `/api/bots/*` convention.

## Testing (pytest)

- `tests/test_cbot_presets.py` — every `PRESETS` key references a strategy in
  `STRATEGIES`; every cell has a non-empty `period` and `params`; the 22-cell
  matrix above is exactly what's present; `build_run_command` golden strings for
  one TMS+ORB, one Judas, one FlowRSI cell; live vs demo naming; output survives
  `shlex.split` and contains `-d`, `--name`, both `-v` mounts.
- `tests/test_ctrader_accounts.py` — `CTRADER_HOME` monkeypatched to `tmp_path`;
  POST creates row + file (mode `0600`, content == password); GET omits password
  and `pwd_file`; duplicate slug → 409; DELETE removes file; bad input → 422.
- `tests/test_setup_instances.py` — `docker_manager` monkeypatched; `start=true`
  calls `start_container` once per new selection with the built command;
  `start=false` never calls it; pre-existing name → `exists` and no docker call;
  unknown pair → `error`.
- `tests/test_dashboard_ui.py` — add assertions that the Docker view HTML contains
  `id="setup-panel"` and the Setup Instances button.

## Out of scope

- Editing parameters in the UI (presets are fixed; power users still have the
  raw command textarea in Add Bot).
- Editing an account after creation (delete and recreate).
- Migrating the current production containers (`cbot-xauusd`, …) to the new naming.
- Multiple password files per account or per-bot credentials.
