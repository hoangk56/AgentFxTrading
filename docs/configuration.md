# Configuration

The server reads its settings from `.env` in the project root (loaded by `app/server.py` with
`load_dotenv(..., override=True)`). Start from [`.env.example`](../.env.example). The strategy presets for the cBots
are **not** covered here: they live in [`app/cbot_presets.py`](../app/cbot_presets.py) and are written out as
commands in [docker-instances.md](docker-instances.md).

## Environment variables

### Server

| Variable | Default | Meaning |
| :--- | :--- | :--- |
| `SERVER_HOST` | `127.0.0.1` | Bind address when started with `python app/server.py` |
| `SERVER_PORT` | `8000` | Port, same condition |
| `SERVER_RELOAD` | `false` | uvicorn auto-reload (`true` / `1` / `yes`) |

The systemd service started by the VPS installer runs `uvicorn app.server:app --host 127.0.0.1 --port 8000`
directly, so these three variables do not apply there.

### Dashboard accounts

No environment variable lists the accounts: you create each one on the dashboard (**Docker Bot Management →
Setup Instances → New account**), which stores the cTrader login in the database and lists the account in the
dashboard's account selector. Do that even for bots you start by hand. A cBot's `--AccountLabel` (`demo`, `live`,
...) decides which dashboard mode its trades belong to.

The server logs every change of an account's balance (`account_balance_log`). The dashboard's **Ledger** view
compares the broker's balance with opening balance + deposits − withdrawals + the bots' closed P&L, lists the
balance changes no closed trade explains, and lets you record each one as a deposit or a withdrawal (or enter one
by hand).

### Database

| Variable | Meaning |
| :--- | :--- |
| `DATABASE_URL` | `postgresql://user:password@host:5432/db` (percent-encode special characters in the password) |

Selection logic (`app/db.py`): a `postgresql://` URL, or simply having `psycopg2` installed, makes the server try
PostgreSQL (with a built-in default URL when `DATABASE_URL` is unset). If the connection fails it logs a warning
and falls back to SQLite `portfolio.db` in the project root. Tests set `AGENTFX_TEST_DB` to redirect the default
database to a throwaway SQLite file.

### cTrader and Docker

| Variable | Default | Meaning |
| :--- | :--- | :--- |
| `CTRADER_HOME` | `/root` | Host directory mounted as `/root` in every cBot container; holds `ctrader_data/` (cTID password files) and `cAlgo/` (build output). The installer sets `/home/forge/ctrader`. |
| `BACKTEST_MAX_PARALLEL` | `3` | Concurrent backtest containers until the value is set on the Backtest page |

## Risk controls

The server takes no part in trading decisions, so it enforces no risk limit. Each bot controls its own risk with
cBot parameters: `RiskPerTradeMoney` (dollars per trade), `MaxSpreadPips` / the spread cap, the max hold time, and
the Crypto Donchian kill switch. A bot paused on the dashboard (Bots tab) takes no new entries until Resume; it keeps
managing its open positions.

## cBot parameters

Each cBot declares its parameters as `[Parameter]` properties at the top of its `cBot/*.cs` file, grouped as they
appear in cTrader. The places to look them up:

- **cTrader Desktop**: the parameter panel when the bot is attached to a chart.
- **Backtest page**: lists every parameter of an installed bot (read with `ctrader-cli metadata`) with its default
  and range.
- **Command line**: any parameter can be passed to `ctrader-console run` as `--<PropertyName>=<value>`.

Tuned strategy values per symbol are presets: change them in `app/cbot_presets.py` (the tests keep
[docker-instances.md](docker-instances.md) in sync). The parameters below are the infrastructure ones that every
instance sets or may need to change regardless of the preset.

| Parameter | Meaning |
| :--- | :--- |
| `BotId` | Unique bot id; the dashboard uses the container name |
| `AccountLabel` | Account tag: routes trades to an account and to the demo or real dashboard |
| `ApiUrl` | Base for the server URLs (default `http://127.0.0.1:8000/trade`): the bot replaces or strips the `/trade` suffix to reach `/api/tick`, `/portfolio/report` and `/api/cbot/commands` |
| `TelemetryUrl` / `ReportUrl` | Override the derived telemetry / report URLs (empty = derive) |
| `CommandPollMs` | Dashboard command poll interval, ms (default 2000, 0 = off) |

Both bots size trades with `RiskPerTradeMoney` in dollars. The presets are sized for a demo balance; see
[docker-instances.md → Adapting a block](docker-instances.md#-adapting-a-block) before going live.
