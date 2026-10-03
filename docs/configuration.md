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

### Dashboard login

| Variable | Meaning |
| :--- | :--- |
| `DASHBOARD_USERNAME` | Login name of the dashboard |
| `DASHBOARD_PASSWORD` | Its password |

With both set (`app/auth.py`), every page, API call and WebSocket needs the session cookie the `/login` page sets
(HttpOnly, SameSite=Lax, Secure over HTTPS, 30 days). Changing either variable and restarting the service logs every
browser out. Five failed logins from one IP lock it out for 15 minutes. With either one unset there is no login, and
the server logs a warning at start.

The cBots and local scripts are not asked: a request that reaches `127.0.0.1:8000` directly passes. A request
proxied by nginx carries `X-Real-IP` / `X-Forwarded-For`, and one with either header needs the login, so the nginx
site must keep setting them (`proxy_set_header X-Real-IP $remote_addr;` and
`proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` in every proxied `location`). The cookie is signed
with a random secret the server creates in `webui_data/session_secret`.

### Telegram alerts

| Variable | Meaning |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token of the Telegram bot that sends the alerts (from @BotFather) |
| `TELEGRAM_CHAT_ID` | Chat that receives them: your user id, or a group id (`-100…`) |

With both set, `app/alerts.py` sends to the chat:

- every `ERROR` / `CRITICAL` line of the agent log, with the end of its traceback. That includes a request that ends
  in an unhandled exception or a 5xx answer, which `app/request_errors.py` logs;
- `🟢 Server started` and `⚪ Server stopping`. A "started" with no "stopping" before it is a crash that systemd
  restarted on its own;
- `🟠 Watchdog restarted …`, one message per watchdog cycle, and `🔴 Watchdog gave up on …` when a bot is in
  backoff (several restarts did not help).

The same alert (lines that differ only in their numbers count as one) is sent at most once every 15 minutes; the next
one says how many it held back. A failed send is printed to journald (`sudo journalctl -u agentfx`), not to the
agent log. Tests never send.

To set it up: create a bot with @BotFather, send it any message (or add it to a group), read the chat id from
`https://api.telegram.org/bot<token>/getUpdates` (`"chat":{"id":…}`), put both values in `.env` and restart the
service; the `🟢 Server started` message confirms it works.

The server cannot report its own death, or the VPS going down: check it from outside with an uptime monitor (e.g.
UptimeRobot) on `https://<your domain>/login`, the one page that answers `200` without a login.

### Dashboard accounts

No environment variable lists the accounts: you create each one on the dashboard (**Docker Bot Management →
Setup Instances → New account**), which stores the cTrader login in the database and lists the account in the
dashboard's account selector. Do that even for bots you start by hand. A cBot's `--AccountLabel` (`demo`, `live`,
...) decides which dashboard mode its trades belong to.

The server logs every change of an account's balance (`account_balance_log`). The dashboard's **Ledger** view
starts from 0: it compares the broker's balance with deposits − withdrawals + the bots' closed P&L, lists the
balance changes no closed trade explains, and lets you record each one as a deposit or a withdrawal (or enter one
by hand). The first balance the server logged is listed as a change from 0, less the P&L of the closes booked before
it: the money that was in the account before the log started.

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
cBot parameters: `RiskPerTradeMoney` (dollars per trade), `MaxSpreadPips` / the spread cap and the max hold time. A
bot paused on the dashboard (Bots tab) takes no new entries until Resume; it keeps managing its open positions.

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
