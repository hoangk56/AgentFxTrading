# Configuration

The server reads its settings from `.env` in the project root (loaded by `app/server.py` with
`load_dotenv(..., override=True)`). Start from [`.env.example`](../.env.example). The strategy presets for the cBots
are **not** covered here: they live in [`app/cbot_presets.py`](../app/cbot_presets.py) and are written out as
commands in [docker-instances.md](docker-instances.md).

## Environment variables

### LLM provider

`LLM_PROVIDER` picks the client in `app/llm_client.py` (`create_llm_client`). `LLM_MODEL` overrides the model for
whichever provider is selected.

| `LLM_PROVIDER` | Key variable | Other variables | Default model |
| :--- | :--- | :--- | :--- |
| `qwen` (or `dashscope`) | `DASHSCOPE_API_KEY` | `DASHSCOPE_BASE_URL` (default `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`) | `qwen3.7-flash` |
| `openai` | `OPENAI_API_KEY` | `OPENAI_BASE_URL` (default `https://api.openai.com/v1`) | `gpt-4o-mini` |
| `anthropic` (or `claude`) | `ANTHROPIC_API_KEY` | `LLM_MAX_TOKENS` (default `4096`) | `claude-3-5-sonnet-20241022` |
| `gemini` (or `google`) | `GOOGLE_API_KEY` | | `gemini-1.5-flash` |
| `deepseek` | `DEEPSEEK_API_KEY` | `DEEPSEEK_BASE_URL` (default `https://api.deepseek.com/v1`) | `deepseek-v4-flash` |
| `openai_compatible` (or `custom`) | `CUSTOM_API_KEY` | `CUSTOM_BASE_URL` (required) | none: set `LLM_MODEL` |

If `LLM_PROVIDER` is unset the code falls back to `openai`; `.env.example` sets `qwen`.

### LLM timeouts and retries

| Variable | Default | Meaning |
| :--- | :--- | :--- |
| `LLM_TIMEOUT` | `90.0` | Total / read timeout per request, seconds |
| `LLM_CONNECT_TIMEOUT` | `30.0` | Connection timeout, seconds |
| `LLM_MAX_RETRIES` | `3` | Retries on transient connection / timeout errors |
| `LLM_TRADE_TIMEOUT` | `40.0` | Per-attempt timeout for `/trade` calls (a cBot is waiting) |
| `LLM_TRADE_MAX_RETRIES` | `1` | Retries for `/trade` on 408/409/429/5xx and connection errors |
| `LLM_TRADE_DEADLINE` | `55.0` | Hard cap on the whole `/trade` LLM call, retries included |
| `LLM_TRADE_ENABLE_THINKING` | `false` | Qwen thinking mode on `/trade`; much slower, off by default |

### Server

| Variable | Default | Meaning |
| :--- | :--- | :--- |
| `SERVER_HOST` | `127.0.0.1` | Bind address when started with `python app/server.py` |
| `SERVER_PORT` | `8000` | Port, same condition |
| `SERVER_RELOAD` | `false` | uvicorn auto-reload (`true` / `1` / `yes`) |

The systemd service started by the VPS installer runs `uvicorn app.server:app --host 127.0.0.1 --port 8000`
directly, so these three variables do not apply there.

### Dashboard accounts

`DASHBOARD_ACCOUNTS` lists the accounts the dashboard knows about, separated by `;`, each as
`account_id|account_number|type|label` with `type` = `live` or `demo` (parsed in `app/accounts.py`):

```bash
DASHBOARD_ACCOUNTS=demo-10101649|10101649|demo|Demo Account;live-88888888|88888888|live|Live Main
```

A cBot's `--AccountLabel` (`demo`, `live`, `live-main`, ...) decides which account and which dashboard mode its
trades belong to. cTrader logins added on the Setup Instances screen are stored in the database instead.

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

### Portfolio entry checks

`PortfolioManager.check_risk` (`app/portfolio.py`) runs on every entry that goes through `/trade`, in this order:

1. **Paused bot**: a bot paused on the dashboard takes no new entries (it keeps managing open positions).
2. **US index alignment**: US equity indices (US30, USTEC, US500 and aliases) may not be held in opposite directions.
3. **Daily loss limits**: see below.
4. **Margin usage**: refuses entries above `PortfolioConfig.MAX_MARGIN_USAGE_PCT` (50 %), using the margin the
   broker reports when the cBot sends it.

### Daily loss limits

Edited on the dashboard (**Risk Limits**) or through `GET/PUT /api/risk-limits`, stored in the `risk_limits`
table. Each limit is the dollar loss a scope may reach in a UTC day before its new entries are refused; the day's
loss counts closed trades plus what open positions would lose at their stops. Defaults created on first start
(`app/risk_limits.py`):

| Scope | Target | Default |
| :--- | :--- | :--- |
| account | every account | $200 |
| strategy | flowrsi | $100 |
| strategy | tms | $60 |
| strategy | judas | $60 |
| container | every container | $30 |

Gotobi and Crypto Donchian have no default limit: the limits are enforced on `/trade`, which those bots never call.
Their own risk controls are cBot parameters (`RiskPerTradeMoney`, and the Crypto Donchian kill switch).

## cBot parameters

Each cBot declares its parameters as `[Parameter]` properties at the top of its `cBot/*.cs` file (from about 25 to about
100 per bot, grouped as they appear in cTrader). The places to look them up:

- **cTrader Desktop**: the parameter panel when the bot is attached to a chart.
- **Backtest page**: lists every parameter of an installed bot (read with `ctrader-cli metadata`) with a help text
  for each, written in `app/backtest_param_help.py`.
- **Command line**: any parameter can be passed to `ctrader-console run` as `--<PropertyName>=<value>`.

Tuned strategy values per symbol are presets: change them in `app/cbot_presets.py` (the tests keep
[docker-instances.md](docker-instances.md) in sync). The parameters below are the infrastructure ones that every
instance sets or may need to change regardless of the preset.

| Parameter | Bots | Meaning |
| :--- | :--- | :--- |
| `BotId` | all | Unique bot id; the dashboard uses the container name |
| `AccountLabel` | all | Account tag: routes trades to an account and to the demo or real dashboard |
| `ApiUrl` | all | Server `/trade` URL (default `http://127.0.0.1:8000/trade`); other endpoints are derived from it. For Judas it is the direct LLM endpoint, used only when `UseDirectAiApi=true` |
| `DashboardServerUrl` | Judas | Server base URL (default `http://127.0.0.1:8000`) |
| `TelemetryUrl` / `ReportUrl` | Gotobi, Crypto Donchian | Override the derived telemetry / report URLs (empty = derive) |
| `AiTelemetryUrl` / `AiReportUrl` | FlowRSI | Telemetry and report URLs |
| `CommandPollMs` | all | Dashboard command poll interval, ms (default 2000, 0 = off) |
| `TickStreamMs` | TMS+ORB, Judas | Tick stream interval over `/ws/cbot`, ms (default 1000, 0 = off) |
| `UseAiGateMode` | Judas, FlowRSI | Ask the AI to confirm entries (default `true`) |
| `UseDirectAiApi` | Judas | Call the LLM directly with `AiApiKey` / `AiModelName` instead of the server (default `false`) |
| `AiConfidenceThreshold` | Judas, FlowRSI | Minimum AI confidence for an entry (defaults 70 / 65) |
| Telegram group | Judas, FlowRSI | Optional alerts: bot token, chat id |

Risk parameters differ per bot: `RiskPerTradePercent` (TMS+ORB), `riskFactor` (Judas), `RiskPercentage` +
`MaxRiskPerTradeMoney` (FlowRSI), `RiskPerTradeMoney` in dollars (Gotobi, Crypto Donchian). The presets are sized
for a demo balance; see [docker-instances.md → Adapting a block](docker-instances.md#-adapting-a-block) before
going live.
