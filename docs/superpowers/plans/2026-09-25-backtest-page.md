# Backtest Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A dashboard page that backtests an installed FlowRSI bot with edited parameters in a `ctrader-cli backtest` container on the VPS, keeps every run, and compares 2–4 runs.

**Architecture:** Six small modules under `app/`:
- three pure ones: `backtest_command` (the container spec), `backtest_report` (report parsing), `backtest_params` (metadata and override validation)
- `backtest_store` for the DB table and report files
- `backtest_worker`, an asyncio loop in the FastAPI lifespan that runs one `bt-<id>` container at a time
- `backtest_api` for the routes

The UI is `static/js/backtest.js` plus a `view-backtest` section in `templates/dashboard.html`.

**Tech Stack:** Python 3.14, FastAPI 0.141, docker SDK 7.2, PostgreSQL in production and SQLite in tests (through `app.db`), Chart.js (already loaded), vanilla JS.

**Spec:** `docs/superpowers/specs/2026-09-24-backtest-page-design.md`

## Global Constraints

- **Git:** never commit or push unless the user says so. Finish each task with the changes left in the working tree. Other sessions edit this checkout too, so when the user does ask for a commit, stage only the files this plan touches.
- **Tests:** run the suite with `.venv/bin/python -m pytest -q -p no:cacheprovider`. The baseline on 2026-09-25 is **726 passed**, and it must stay green after every task.
- **Container network:** `network_mode="bridge"` only, **never** `host`. The cBots still call `127.0.0.1:8000` while backtesting.
- **Container identity:** named `bt-<id>` and labelled `agentfx.backtest=<id>`. The worker only removes containers that carry this label.
- **Container resources:** `mem_limit="1g"`, `nano_cpus=2_000_000_000`, `cpu_shares=256`, one job at a time, 45 min timeout.
- **Locked parameters** are forced last:
  - `BotId=bt-<id>`, `AccountLabel=backtest`, `UseAiGateMode=false`
  - `ApiUrl`/`AiTelemetryUrl`/`AiReportUrl=http://127.0.0.1:9/disabled`, `CommandPollMs=0`
  - `EnableNewsFilter=false`, `EnableTelegramAlerts=false`, `SendChartScreenshot=false`, `SendAiAdjustAlerts=false`
  - `TelegramBotToken` and `TelegramChatId` are never passed.
- **Supported strategies:** only `FlowRsiBot.algo` in v1. Judas and TMS+ORB are listed as unsupported with the reason `Judas/TMS+ORB enter only through the AI; backtest mode not implemented yet`.
- Do not touch `cBot/*.cs`. Never run `scripts/deploy_feature.sh`.
- VPS paths are under `/home/forge` (not `/root` as AGENTS.md says).
- Code and comments are in English. Match the repo's comment density: a module docstring that says why, and comments only where the reason is not obvious.

---

## File Structure

| File | Responsibility |
|---|---|
| `app/backtest_command.py` (create) | Pure. Parse `run_command` → `BotSource`; host paths; `describe_source`; locked params; `build_container_spec` |
| `app/backtest_report.py` (create) | Pure. cTrader report JSON → `summarize()` KPIs and `ui_payload()` chart/table data |
| `app/backtest_params.py` (create) | `ctrader-cli metadata` runner and cache, `param_view`, `canonical`, `validate_overrides`, `job_params` |
| `app/backtest_store.py` (create) | `backtest_jobs` schema and CRUD; report files in `webui_data/backtests/` |
| `app/backtest_worker.py` (create) | `BacktestWorker.tick()` (queue, progress, collect, timeout, reconcile) and the async loop |
| `app/backtest_api.py` (create) | `/api/backtests*` routes |
| `app/portfolio.py` (modify) | Call `backtest_store.init_schema(conn)` |
| `app/server.py` (modify) | Include the router; start and stop the worker in `lifespan` (not under pytest) |
| `static/js/backtest.js` (create) | Page logic; pure `bt*Html` renderers |
| `templates/dashboard.html` (modify) | Nav item, `view-backtest` section, script tag, `switchView` hook, CSS version bump |
| `static/css/dashboard.css` (modify) | `bt-*` styles |
| `tests/fixtures/backtest/flowrsi_metadata.json` (create) | Trimmed real `metadata` output of FlowRsiBot |
| `tests/fixtures/backtest/report_small.json` (create) | Small cTrader report with 4 trades |
| `tests/test_backtest_command.py`, `test_backtest_report.py`, `test_backtest_params.py`, `test_backtest_store.py`, `test_backtest_worker.py`, `test_backtest_api.py`, `test_backtest_ui.py` (create) | One test module per unit |

---

### Task 1: Container spec (`app/backtest_command.py`)

**Files:**
- Create: `app/backtest_command.py`
- Test: `tests/test_backtest_command.py`

**Interfaces:**
- Consumes: `app.cbot_presets.DEFAULT_IMAGE`, `app.cbot_presets.build_run_command` (tests only)
- Produces:
  - `SourceError(ValueError)`
  - `@dataclass BotSource(name, algo, strategy, ctid, account, symbol, period, pwd_file, params: Dict[str, str])`
  - `parse_run_command(name: str, run_command: str) -> BotSource`
  - `algo_host_path(algo: str, project_root: Path) -> Path`
  - `pwd_host_path(pwd_file: str, ctrader_home: Path) -> Path`
  - `describe_source(name, run_command, project_root, ctrader_home) -> Dict` (keys `name, strategy, symbol, period, account_label, supported, reason`)
  - `locked_params(strategy: str, job_id: Optional[int]) -> Dict[str, str]`
  - `container_name(job_id: int) -> str`
  - `build_container_spec(job: Dict, project_root: Path, ctrader_home: Path) -> Dict` (kwargs for `client.containers.run(**spec)`)
  - Constants: `LABEL`, `REPORT_PATH`, `CACHE_VOLUME`, `DROPPED_PARAMS`, `HIDDEN_GROUPS`, `SUPPORTED_STRATEGIES`, `UNSUPPORTED_REASON`, `ALGO_DIR`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backtest_command.py`:

```python
"""Backtest container specs: an installed bot's run_command as a backtest source, and the safety rules
of the `docker run … backtest` spec (docs/superpowers/specs/2026-09-24-backtest-page-design.md).

The cBots still call HTTP/WebSocket endpoints while backtesting (Judas' TickStream, AiAgentBot's
position reports), so these tests pin that a backtest container never shares the host network, never
sees more than its three mounts, and always runs with the AI, news and Telegram switched off."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import backtest_command as bc  # noqa: E402
from app.cbot_presets import build_run_command  # noqa: E402

ACCOUNT = {"slug": "demo-demo", "ctid_email": "trader@example.com", "account_number": "10115236",
           "label": "demo", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd"}


def preset(strategy="flowrsi", symbol="EURUSD"):
    return build_run_command(ACCOUNT, strategy, symbol, "/home/forge/AgentFxTrading", "/home/forge/ctrader")


@pytest.fixture
def homes(tmp_path):
    project = tmp_path / "project"
    (project / "cBot").mkdir(parents=True)
    (project / "cBot" / "FlowRsiBot.algo").write_bytes(b"algo")
    ctrader = tmp_path / "ctrader"
    (ctrader / "ctrader_data").mkdir(parents=True)
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").write_text("s3cret-password")
    return project, ctrader


def make_job(**over):
    job = {"id": 7, "strategy": "flowrsi", "algo": "FlowRsiBot.algo", "ctid": "trader@example.com",
           "account": "10115236", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd",
           "symbol": "EURUSD", "period": "m15", "start_date": "2026-07-24", "end_date": "2026-09-23",
           "data_mode": "ticks", "spread_pips": None, "balance": 10000.0,
           "params": {"FastRsiPeriod": "7", "TargetRiskReward": "2.0", "UseAiGateMode": "true",
                      "ApiUrl": "http://127.0.0.1:8000/trade", "BotId": "cbot-demo-demo-eurusd-all-flowrsi",
                      "TelegramBotToken": "123456:telegram-token"}}
    job.update(over)
    return job


def spec_for(homes, **over):
    project, ctrader = homes
    return bc.build_container_spec(make_job(**over), project, ctrader)


# --- parsing ------------------------------------------------------------------------------------

def test_parses_a_preset_flowrsi_command():
    src = bc.parse_run_command("cbot-demo-demo-eurusd-all-flowrsi", preset())
    assert src.algo == "FlowRsiBot.algo" and src.strategy == "flowrsi"
    assert (src.ctid, src.account, src.symbol, src.period) == ("trader@example.com", "10115236", "EURUSD", "m15")
    assert src.pwd_file == "/root/ctrader_data/ctid_demo-demo_pwd"
    assert src.params["BotId"] == "cbot-demo-demo-eurusd-all-flowrsi"      # quotes stripped
    assert src.params["TargetRiskReward"] == "1.5"
    assert src.params["UseAiGateMode"] == "true"
    assert "full-access" not in src.params and "ctid" not in src.params


def test_parses_a_multiline_hand_written_command():
    cmd = ("docker run -d --name cbot-x --network host \\\n  -v /home/forge/AgentFxTrading:/workspace \\\n"
           "  ghcr.io/spotware/ctrader-console:latest run /workspace/cBot/FlowRsiBot.algo \\\n"
           "  --ctid=trader@example.com --pwd-file=/root/ctrader_data/pw --account=1 \\\n"
           "  --symbol=XAUUSD --period=m15 --full-access --TargetRiskReward=2.5 -e")
    src = bc.parse_run_command("cbot-x", cmd)
    assert src.symbol == "XAUUSD" and src.params == {"TargetRiskReward": "2.5"}


@pytest.mark.parametrize("cmd, message", [
    ("docker run -d ghcr.io/spotware/ctrader-console:latest accounts", "run <file>.algo"),
    ("docker run img run /workspace/cBot/FlowRsiBot.algo --pwd-file=/root/ctrader_data/pw --account=1 "
     "--symbol=EURUSD --period=m15", "--ctid"),
    ("docker run img run /root/elsewhere/FlowRsiBot.algo --ctid=a@b.c --pwd-file=/root/ctrader_data/pw "
     "--account=1 --symbol=EURUSD --period=m15", "/workspace/cBot"),
    ('docker run img run /workspace/cBot/FlowRsiBot.algo --ctid="unterminated', "does not parse"),
])
def test_rejects_commands_it_cannot_use(cmd, message):
    with pytest.raises(bc.SourceError, match=re.escape(message)):
        bc.parse_run_command("x", cmd)


# --- host paths ---------------------------------------------------------------------------------

def test_password_file_maps_into_ctrader_home(homes):
    _, ctrader = homes
    host = bc.pwd_host_path("/root/ctrader_data/ctid_demo-demo_pwd", ctrader)
    assert host == (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").resolve()


@pytest.mark.parametrize("pwd_file", [
    "/root/ctrader_data/../.ssh/id_rsa", "/root/other/ctid_pwd", "/root/ctrader_data/", "ctid_pwd",
    "/root/ctrader_data/missing_pwd",
])
def test_password_file_cannot_leave_ctrader_data(homes, pwd_file):
    with pytest.raises(bc.SourceError):
        bc.pwd_host_path(pwd_file, homes[1])


def test_password_file_symlink_out_of_ctrader_data_is_refused(homes, tmp_path):
    _, ctrader = homes
    outside = tmp_path / "outside"
    outside.write_text("x")
    (ctrader / "ctrader_data" / "link_pwd").symlink_to(outside)
    with pytest.raises(bc.SourceError, match="not found"):
        bc.pwd_host_path("/root/ctrader_data/link_pwd", ctrader)


# --- describe_source ----------------------------------------------------------------------------

def test_describe_flowrsi_source_is_supported(homes):
    project, ctrader = homes
    row = bc.describe_source("cbot-demo-demo-eurusd-all-flowrsi", preset(), project, ctrader)
    assert row == {"name": "cbot-demo-demo-eurusd-all-flowrsi", "strategy": "flowrsi", "symbol": "EURUSD",
                   "period": "m15", "account_label": "demo", "supported": True, "reason": ""}


@pytest.mark.parametrize("strategy", ["judas", "tms_orb"])
def test_describe_ai_only_bots_as_unsupported(homes, strategy):
    row = bc.describe_source("x", preset(strategy), *homes)
    assert row["supported"] is False and row["reason"] == bc.UNSUPPORTED_REASON
    assert row["strategy"] == strategy


def test_describe_reports_missing_password_file_and_unbuilt_algo(homes):
    project, ctrader = homes
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").unlink()
    assert bc.describe_source("x", preset(), project, ctrader)["reason"] == "password file not found"
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").write_text("pw")
    (project / "cBot" / "FlowRsiBot.algo").unlink()
    assert bc.describe_source("x", preset(), project, ctrader)["reason"] == "FlowRsiBot.algo is not built"


def test_describe_unparsable_command():
    row = bc.describe_source("x", "echo hello", Path("/nonexistent"), Path("/nonexistent"))
    assert row["supported"] is False and "run <file>.algo" in row["reason"]


# --- safety invariants of build_container_spec (spec: "Safety invariants") ----------------------

def test_invariant_1_bridge_network_only(homes):
    spec = spec_for(homes)
    assert spec["network_mode"] == "bridge"
    assert set(spec) == {"image", "name", "command", "labels", "network_mode", "mem_limit", "nano_cpus",
                         "cpu_shares", "volumes", "detach", "auto_remove"}


def test_invariant_2_only_three_mounts(homes):
    project, ctrader = homes
    assert spec_for(homes)["volumes"] == {
        str(project / "cBot" / "FlowRsiBot.algo"): {"bind": "/algo/FlowRsiBot.algo", "mode": "ro"},
        str((ctrader / "ctrader_data" / "ctid_demo-demo_pwd").resolve()): {"bind": "/secrets/pwd", "mode": "ro"},
        "agentfx-bt-cache": {"bind": "/bt-cache", "mode": "rw"},
    }


def test_invariant_3_locked_params_come_last_and_win(homes):
    command = spec_for(homes)["command"]
    locked = bc.locked_params("flowrsi", 7)
    assert command[-len(locked):] == [f"--{k}={v}" for k, v in locked.items()]
    assert "--UseAiGateMode=true" not in command
    assert "--ApiUrl=http://127.0.0.1:8000/trade" not in command
    assert "--BotId=cbot-demo-demo-eurusd-all-flowrsi" not in command
    assert "--BotId=bt-7" in command and "--AccountLabel=backtest" in command
    assert "--TargetRiskReward=2.0" in command and "--FastRsiPeriod=7" in command


def test_invariant_4_name_and_label(homes):
    spec = spec_for(homes)
    assert spec["name"] == "bt-7" and spec["labels"] == {"agentfx.backtest": "7"}


def test_invariant_5_resource_limits(homes):
    spec = spec_for(homes)
    assert (spec["mem_limit"], spec["nano_cpus"], spec["cpu_shares"]) == ("1g", 2_000_000_000, 256)
    assert spec["detach"] is True and spec["auto_remove"] is False


def test_invariant_6_list_command_without_secrets(homes):
    command = spec_for(homes)["command"]
    assert isinstance(command, list) and all(isinstance(a, str) for a in command)
    assert command[:2] == ["backtest", "/algo/FlowRsiBot.algo"]
    assert "--pwd-file=/secrets/pwd" in command
    joined = " ".join(command)
    assert "s3cret-password" not in joined and "telegram-token" not in joined


def test_dates_balance_and_report_flags(homes):
    command = spec_for(homes)["command"]
    for flag in ("--start=24/07/2026", "--end=23/09/2026", "--data-mode=ticks", "--data-dir=/bt-cache",
                 "--balance=10000", "--commission-auto", "--report-json=/tmp/report.json", "--full-access",
                 "--exit-on-stop", "--symbol=EURUSD", "--period=m15", "--account=10115236"):
        assert flag in command, flag
    assert not any(a.startswith("--spread=") for a in command)


def test_m1_adds_the_spread(homes):
    command = spec_for(homes, data_mode="m1", spread_pips=1.2)["command"]
    assert "--data-mode=m1" in command and "--spread=1.2" in command


@pytest.mark.parametrize("over", [{"strategy": "judas"}, {"data_mode": "tick-csv"}, {"algo": "../evil.algo"}])
def test_refuses_jobs_it_must_not_run(homes, over):
    with pytest.raises(bc.SourceError):
        spec_for(homes, **over)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_command.py -q -p no:cacheprovider`
Expected: collection error `ModuleNotFoundError: No module named 'app.backtest_command'`.

- [ ] **Step 3: Implement `app/backtest_command.py`**

```python
"""
Container specs for the dashboard's Backtest page
(docs/superpowers/specs/2026-09-24-backtest-page-design.md).

Pure functions: parse an installed bot's `docker run … run <algo>` command into a BotSource, and build
the `docker run … backtest` spec for a job. Nothing here talks to Docker or the DB.

The cBots still make HTTP/WebSocket calls while backtesting (Judas' TickStream, AiAgentBot's position
reports). On `--network host` those reach 127.0.0.1:8000 and write fake trades and ticks into
production, so a backtest container only ever gets bridge networking, three mounts, and the locked
parameters below written after everything else. tests/test_backtest_command.py pins each rule.
"""
import re
import shlex
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional

from app.cbot_presets import DEFAULT_IMAGE

CACHE_VOLUME = "agentfx-bt-cache"
CACHE_DIR = "/bt-cache"
PWD_MOUNT = "/secrets/pwd"
ALGO_DIR = "/algo"
REPORT_PATH = "/tmp/report.json"
LABEL = "agentfx.backtest"
MEM_LIMIT = "1g"
NANO_CPUS = 2_000_000_000
CPU_SHARES = 256
DISABLED_URL = "http://127.0.0.1:9/disabled"

STRATEGY_BY_ALGO = {
    "FlowRsiBot.algo": "flowrsi",
    "AsianRangeJudasSweepBot.algo": "judas",
    "AiAgentBot.algo": "tms_orb",
}
SUPPORTED_STRATEGIES = {"flowrsi"}
UNSUPPORTED_REASON = "Judas/TMS+ORB enter only through the AI; backtest mode not implemented yet"
DATA_MODES = ("ticks", "m1")

# cTrader CLI options that sit next to the cBot parameters in a `run` command.
CLI_OPTIONS = {"ctid", "pwd-file", "password", "account", "broker", "symbol", "period", "reconnect-timeout"}

# Written after the bot's values and the user's overrides, so they always win.
LOCKED_PARAMS: Dict[str, Dict[str, str]] = {
    "flowrsi": {
        "UseAiGateMode": "false",
        "ApiUrl": DISABLED_URL,
        "AiTelemetryUrl": DISABLED_URL,
        "AiReportUrl": DISABLED_URL,
        "CommandPollMs": "0",
        "EnableNewsFilter": "false",          # there is no historical news calendar
        "EnableTelegramAlerts": "false",
        "SendChartScreenshot": "false",
        "SendAiAdjustAlerts": "false",
    },
}
# Never passed to a backtest container, whatever the bot's command says.
DROPPED_PARAMS = {"TelegramBotToken", "TelegramChatId"}
# Metadata groups the form does not show; their unlocked parameters keep the bot's value.
HIDDEN_GROUPS = {"AI Agent Integration", "News Filter", "Telegram Integration"}


class SourceError(ValueError):
    """A bot's run_command (or a stored job) cannot be used for a backtest."""


@dataclass
class BotSource:
    name: str
    algo: str                    # "FlowRsiBot.algo"
    strategy: Optional[str]      # "flowrsi" | "judas" | "tms_orb" | None
    ctid: str
    account: str
    symbol: str
    period: str
    pwd_file: str                # container path, as written in run_command
    params: Dict[str, str] = field(default_factory=dict)


def _tokens(run_command: str) -> List[str]:
    # Saved commands are often multi-line with trailing backslashes (see docker_manager.start_container).
    cleaned = run_command.replace("\\\r\n", " ").replace("\\\n", " ").replace("\\\r", " ")
    cleaned = cleaned.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    try:
        return shlex.split(cleaned)
    except ValueError as e:
        raise SourceError(f"run_command does not parse: {e}")


def parse_run_command(name: str, run_command: str) -> BotSource:
    tokens = _tokens(run_command or "")
    start = next((i for i in range(len(tokens) - 1)
                  if tokens[i] == "run" and tokens[i + 1].endswith(".algo")), None)
    if start is None:
        raise SourceError("run_command has no `run <file>.algo`")
    algo_path = PurePosixPath(tokens[start + 1])
    if algo_path.parent != PurePosixPath("/workspace/cBot"):
        raise SourceError("the algo must be /workspace/cBot/<file>.algo")
    options: Dict[str, str] = {}
    params: Dict[str, str] = {}
    for token in tokens[start + 2:]:
        if not token.startswith("--") or "=" not in token:
            continue                                   # --full-access, --exit-on-stop, -e
        key, value = token[2:].split("=", 1)
        if key in CLI_OPTIONS:
            options[key] = value
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            params[key] = value
    missing = [k for k in ("ctid", "pwd-file", "account", "symbol", "period") if not options.get(k)]
    if missing:
        raise SourceError(f"run_command lacks --{', --'.join(missing)}")
    return BotSource(name=name, algo=algo_path.name, strategy=STRATEGY_BY_ALGO.get(algo_path.name),
                     ctid=options["ctid"], account=options["account"], symbol=options["symbol"],
                     period=options["period"], pwd_file=options["pwd-file"], params=params)


def algo_host_path(algo: str, project_root: Path) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_]+\.algo", algo or ""):
        raise SourceError(f"unexpected algo file name: {algo}")
    return Path(project_root) / "cBot" / algo


def pwd_host_path(pwd_file: str, ctrader_home: Path) -> Path:
    """`/root/ctrader_data/<file>` in the bot container -> `<CTRADER_HOME>/ctrader_data/<file>` on the host."""
    container = PurePosixPath(pwd_file or "")
    if container.parent != PurePosixPath("/root/ctrader_data") or container.name in ("", ".", ".."):
        raise SourceError("password file must be /root/ctrader_data/<file>")
    base = (Path(ctrader_home) / "ctrader_data").resolve()
    host = (base / container.name).resolve()
    if host.parent != base or not host.is_file():      # resolve() follows symlinks out of ctrader_data
        raise SourceError("password file not found")
    return host


def describe_source(name: str, run_command: str, project_root: Path, ctrader_home: Path) -> Dict:
    """One row of GET /api/backtests/sources."""
    row = {"name": name, "strategy": None, "symbol": "", "period": "", "account_label": "",
           "supported": False, "reason": ""}
    try:
        src = parse_run_command(name, run_command)
    except SourceError as e:
        row["reason"] = str(e)
        return row
    row.update(strategy=src.strategy, symbol=src.symbol, period=src.period,
               account_label=src.params.get("AccountLabel", ""))
    if src.strategy not in SUPPORTED_STRATEGIES:
        row["reason"] = UNSUPPORTED_REASON
        return row
    try:
        pwd_host_path(src.pwd_file, ctrader_home)
        if not algo_host_path(src.algo, project_root).is_file():
            raise SourceError(f"{src.algo} is not built")
    except SourceError as e:
        row["reason"] = str(e)
        return row
    row["supported"] = True
    return row


def locked_params(strategy: str, job_id: Optional[int]) -> Dict[str, str]:
    bot_id = f"bt-{job_id}" if job_id is not None else "bt-<id>"
    return {"BotId": bot_id, "AccountLabel": "backtest", **LOCKED_PARAMS[strategy]}


def container_name(job_id: int) -> str:
    return f"bt-{int(job_id)}"


def _num(value) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else repr(number)


def _cli_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%d/%m/%Y")      # --end is inclusive


def build_container_spec(job: Dict, project_root: Path, ctrader_home: Path) -> Dict:
    """kwargs for `client.containers.run(**spec)`. `job` is a backtest_jobs row with `params` decoded."""
    strategy = job["strategy"]
    if strategy not in SUPPORTED_STRATEGIES:
        raise SourceError(UNSUPPORTED_REASON)
    if job["data_mode"] not in DATA_MODES:
        raise SourceError(f"unknown data mode {job['data_mode']}")
    host_algo = algo_host_path(job["algo"], project_root)
    host_pwd = pwd_host_path(job["pwd_file"], ctrader_home)
    algo_mount = f"{ALGO_DIR}/{job['algo']}"
    locked = locked_params(strategy, job["id"])

    command = [
        "backtest", algo_mount,
        f"--ctid={job['ctid']}", f"--pwd-file={PWD_MOUNT}", f"--account={job['account']}",
        f"--symbol={job['symbol']}", f"--period={job['period']}",
        f"--start={_cli_date(job['start_date'])}", f"--end={_cli_date(job['end_date'])}",
        f"--data-mode={job['data_mode']}",
    ]
    if job["data_mode"] == "m1":
        command.append(f"--spread={_num(job['spread_pips'])}")
    command += [f"--data-dir={CACHE_DIR}", f"--balance={_num(job['balance'])}", "--commission-auto",
                f"--report-json={REPORT_PATH}", "--full-access", "--exit-on-stop"]
    command += [f"--{k}={v}" for k, v in (job.get("params") or {}).items()
                if k not in locked and k not in DROPPED_PARAMS]
    command += [f"--{k}={v}" for k, v in locked.items()]

    return {
        "image": DEFAULT_IMAGE,
        "name": container_name(job["id"]),
        "command": command,
        "labels": {LABEL: str(job["id"])},
        "network_mode": "bridge",
        "mem_limit": MEM_LIMIT,
        "nano_cpus": NANO_CPUS,
        "cpu_shares": CPU_SHARES,
        "volumes": {
            str(host_algo): {"bind": algo_mount, "mode": "ro"},
            str(host_pwd): {"bind": PWD_MOUNT, "mode": "ro"},
            CACHE_VOLUME: {"bind": CACHE_DIR, "mode": "rw"},
        },
        "detach": True,
        "auto_remove": False,          # the report is read out of the exited container
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_command.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 5: Checkpoint**

Run the full suite: `.venv/bin/python -m pytest -q -p no:cacheprovider`. Expected: 726 plus the new tests pass. Do not commit.

---

### Task 2: Report parsing (`app/backtest_report.py`)

**Files:**
- Create: `app/backtest_report.py`
- Create: `tests/fixtures/backtest/report_small.json`
- Test: `tests/test_backtest_report.py`

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces:
  - `summarize(report: Dict) -> Dict`, with the keys listed in the spec's `summary`
  - `ui_payload(report: Dict) -> Dict` with keys `equity` (`[{t, balance, equity}]`), `trades`, `pnl_by_hour` (24 × `{net, count}`), `pnl_by_weekday` (7 × `{net, count}`, Monday first), `parameters` (`{propertyName: value}`)
  - `downsample(points: List, limit: int = MAX_EQUITY_POINTS) -> List`
  - `MAX_EQUITY_POINTS = 1000`

- [ ] **Step 1: Create the fixture**

Create `tests/fixtures/backtest/report_small.json`. It uses the shape of a real `--report-json` file (FlowRSI EURUSD, 2026-09-24 spike), cut down to 4 trades. The items are deliberately out of order: id 4 comes before id 3.

```json
{
  "main": {"symbol": "EURUSD", "period": "m15", "cBotName": "FlowRsiBot", "depositAsset": "USD",
           "roi": -0.01, "netProfit": -0.98, "startingCapital": 10000, "endingEquity": 9999.02,
           "endingBalance": 9999.02, "testingPeriod": {"formatted": "10d (24/07/2026 - 03/08/2026)"}},
  "equity": {
    "points": [
      {"balance": 10000, "minEquity": 10000, "maxEquity": 10000, "timestamp": 1784851200000},
      {"balance": 10025.02, "minEquity": 10020.5, "maxEquity": 10025.02, "timestamp": 1785148200000},
      {"balance": 10055.02, "minEquity": 10050.0, "maxEquity": 10056.1, "timestamp": 1785254400000},
      {"balance": 10011.02, "minEquity": 9990.4, "maxEquity": 10030.0, "timestamp": 1785290400000},
      {"balance": 9999.02, "minEquity": 9995.1, "maxEquity": 10012.0, "timestamp": 1785718800000}
    ],
    "maxBalanceDrawdownPercent": 0.4376, "maxEquityDrawdownPercent": 0.6533,
    "maxBalanceDrawdownAbsolute": 44.0, "maxEquityDrawdownAbsolute": 65.7, "defaultXAxisMode": "time"
  },
  "tradeStatistics": {
    "netProfit": {"all": -0.98, "long": -14.0, "short": 13.02},
    "profitFactor": {"all": 0.98, "long": 0.68, "short": 2.08},
    "commissions": {"all": -4.2, "long": -2.32, "short": -1.88},
    "swaps": {"all": -0.5, "long": -0.5, "short": 0},
    "totalTrades": {"all": 4, "long": 2, "short": 2},
    "winningTrades": {"all": 2, "long": 1, "short": 1},
    "maxConsecutiveWinningTrades": {"all": 2, "long": 1, "short": 1},
    "largestWinningTrade": {"all": 30.0, "long": 30.0, "short": 25.02},
    "losingTrades": {"all": 2, "long": 1, "short": 1},
    "maxConsecutiveLosingTrades": {"all": 2, "long": 1, "short": 1},
    "largestLosingTrade": {"all": -44.0, "long": -44.0, "short": -12.0},
    "averageTrade": {"all": -0.25, "long": -7.0, "short": 6.51}
  },
  "parameters": [
    {"group": "General", "displayName": "Bot ID", "propertyName": "BotId", "value": "bt-7"},
    {"group": "Risk Management", "displayName": "Target Risk-to-Reward Ratio", "propertyName": "TargetRiskReward", "value": "1.5"},
    {"group": "Risk Management", "displayName": "Stop Loss Mode", "propertyName": "SlMode", "value": "Technical_Swing"}
  ],
  "history": {
    "columns": ["id", "symbol", "direction", "net", "gross", "entryTime", "closeTime", "entryPrice", "closePrice",
                "swaps", "commissions", "volume", "label", "comment", "quantity", "pips"],
    "items": [
      {"id": 2, "symbol": "EURUSD", "direction": "sell", "net": 25.02, "gross": 26.18, "entryTime": 1785139200000,
       "closeTime": 1785148200000, "entryPrice": 1.13901, "closePrice": 1.13747, "swaps": 0, "commissions": -1.16,
       "volume": 17000, "label": "bt-7", "comment": "bt-7", "quantity": 0.17, "pips": 15.4},
      {"id": 4, "symbol": "EURUSD", "direction": "buy", "net": -44.0, "gross": -42.34, "entryTime": 1785246300000,
       "closeTime": 1785290400000, "entryPrice": 1.141, "closePrice": 1.1385, "swaps": -0.5, "commissions": -1.16,
       "volume": 17000, "label": "bt-7", "comment": "bt-7", "quantity": 0.17, "pips": -25.0},
      {"id": 3, "symbol": "EURUSD", "direction": "buy", "net": 30.0, "gross": 31.16, "entryTime": 1785244500000,
       "closeTime": 1785254400000, "entryPrice": 1.14, "closePrice": 1.1418, "swaps": 0, "commissions": -1.16,
       "volume": 17000, "label": "bt-7", "comment": "bt-7", "quantity": 0.17, "pips": 18.0},
      {"id": 5, "symbol": "EURUSD", "direction": "sell", "net": -12.0, "gross": -11.28, "entryTime": 1785533400000,
       "closeTime": 1785718800000, "entryPrice": 1.135, "closePrice": 1.1356, "swaps": 0, "commissions": -0.72,
       "volume": 20000, "label": "bt-7", "comment": "bt-7", "quantity": 0.2, "pips": -6.0}
    ]
  }
}
```

The entry times, in UTC:

| id | Entry time (UTC) | Weekday / hour bucket | Net |
|---|---|---|---|
| 2 | 2026-07-27 08:00 | Mon h8 | +25.02 |
| 3 | 2026-07-28 13:15 | Tue h13 | +30.00 |
| 4 | 2026-07-28 13:45 | Tue h13 | −44.00 |
| 5 | 2026-07-31 21:30 | Fri h21 | −12.00 |

- [ ] **Step 2: Write the failing tests**

Create `tests/test_backtest_report.py`:

```python
"""cTrader backtest report -> Backtest page summary and chart data.

The report's per-hour/weekday sections only count winning and losing trades, so the P&L buckets are
computed from history.items by UTC entry time; avg win/loss come from the same items."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.backtest_report import MAX_EQUITY_POINTS, downsample, summarize, ui_payload  # noqa: E402

REPORT = json.loads((ROOT / "tests" / "fixtures" / "backtest" / "report_small.json").read_text())


def test_summary_reads_statistics_equity_and_history():
    assert summarize(REPORT) == {
        "net_profit": -0.98, "roi_pct": -0.01, "starting_capital": 10000.0, "ending_equity": 9999.02,
        "profit_factor": 0.98, "total_trades": 4, "winning_trades": 2, "losing_trades": 2, "win_rate": 50.0,
        "avg_trade": -0.25, "avg_win": 27.51, "avg_loss": -28.0,
        "max_equity_dd_pct": 0.65, "max_equity_dd": 65.7, "max_balance_dd_pct": 0.44,
        "commissions": -4.2, "swaps": -0.5, "largest_win": 30.0, "largest_loss": -44.0,
        "max_consecutive_losses": 2, "long_net": -14.0, "short_net": 13.02, "long_trades": 2, "short_trades": 2,
    }


def test_summary_of_a_run_without_trades():
    empty = copy.deepcopy(REPORT)
    empty["history"]["items"] = []
    empty["tradeStatistics"] = {k: {"all": None, "long": None, "short": None} for k in REPORT["tradeStatistics"]}
    s = summarize(empty)
    assert (s["total_trades"], s["win_rate"], s["avg_win"], s["avg_loss"], s["profit_factor"]) == (0, 0.0, 0.0, 0.0, 0.0)


def test_pnl_by_hour_and_weekday_use_utc_entry_time():
    payload = ui_payload(REPORT)
    hours = payload["pnl_by_hour"]
    assert len(hours) == 24
    assert hours[8] == {"net": 25.02, "count": 1}
    assert hours[13] == {"net": -14.0, "count": 2}
    assert hours[21] == {"net": -12.0, "count": 1}
    assert sum(b["count"] for b in hours) == 4
    days = payload["pnl_by_weekday"]
    assert len(days) == 7
    assert days[0] == {"net": 25.02, "count": 1}      # Monday
    assert days[1] == {"net": -14.0, "count": 2}      # Tuesday
    assert days[4] == {"net": -12.0, "count": 1}      # Friday
    assert days[5] == {"net": 0.0, "count": 0}


def test_trades_are_sorted_by_entry_and_formatted():
    trades = ui_payload(REPORT)["trades"]
    assert [t["id"] for t in trades] == [2, 3, 4, 5]
    assert trades[0] == {"id": 2, "direction": "sell", "entry_time": "2026-07-27 08:00",
                         "close_time": "2026-07-27 10:30", "entry_price": 1.13901, "close_price": 1.13747,
                         "lots": 0.17, "pips": 15.4, "net": 25.02, "commissions": -1.16, "swaps": 0.0}


def test_equity_points_and_parameters():
    payload = ui_payload(REPORT)
    assert payload["equity"][0] == {"t": 1784851200000, "balance": 10000.0, "equity": 10000.0}
    assert payload["equity"][3] == {"t": 1785290400000, "balance": 10011.02, "equity": 9990.4}
    assert payload["parameters"] == {"BotId": "bt-7", "TargetRiskReward": "1.5", "SlMode": "Technical_Swing"}


def test_downsample_keeps_first_and_last_and_the_limit():
    points = list(range(5000))
    sampled = downsample(points)
    assert len(sampled) <= MAX_EQUITY_POINTS
    assert sampled[0] == 0 and sampled[-1] == 4999
    assert sampled == sorted(sampled)
    assert downsample([1, 2, 3]) == [1, 2, 3]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_report.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'app.backtest_report'`.

- [ ] **Step 4: Implement `app/backtest_report.py`**

```python
"""
cTrader backtest report (`--report-json`) -> the Backtest page's summary and chart data.

The report's per-hour/weekday sections only count winning and losing trades, so P&L by hour and by
weekday is computed here from history.items, bucketed by UTC entry time.
"""
from datetime import datetime, timezone
from typing import Dict, List

MAX_EQUITY_POINTS = 1000


def _r(value, digits: int = 2) -> float:
    return round(float(value or 0), digits)


def _side(stats: Dict, key: str, side: str = "all"):
    value = (stats.get(key) or {}).get(side)
    return value if value is not None else 0


def summarize(report: Dict) -> Dict:
    main, stats, equity = report["main"], report["tradeStatistics"], report["equity"]
    nets = [float(t["net"]) for t in (report.get("history") or {}).get("items", [])]
    wins = [n for n in nets if n > 0]
    losses = [n for n in nets if n < 0]
    total = int(_side(stats, "totalTrades"))
    won = int(_side(stats, "winningTrades"))
    return {
        "net_profit": _r(_side(stats, "netProfit")),
        "roi_pct": _r(main.get("roi")),
        "starting_capital": _r(main.get("startingCapital")),
        "ending_equity": _r(main.get("endingEquity")),
        "profit_factor": _r(_side(stats, "profitFactor")),
        "total_trades": total,
        "winning_trades": won,
        "losing_trades": int(_side(stats, "losingTrades")),
        "win_rate": _r(won * 100.0 / total) if total else 0.0,
        "avg_trade": _r(_side(stats, "averageTrade")),
        "avg_win": _r(sum(wins) / len(wins)) if wins else 0.0,
        "avg_loss": _r(sum(losses) / len(losses)) if losses else 0.0,
        "max_equity_dd_pct": _r(equity.get("maxEquityDrawdownPercent")),
        "max_equity_dd": _r(equity.get("maxEquityDrawdownAbsolute")),
        "max_balance_dd_pct": _r(equity.get("maxBalanceDrawdownPercent")),
        "commissions": _r(_side(stats, "commissions")),
        "swaps": _r(_side(stats, "swaps")),
        "largest_win": _r(_side(stats, "largestWinningTrade")),
        "largest_loss": _r(_side(stats, "largestLosingTrade")),
        "max_consecutive_losses": int(_side(stats, "maxConsecutiveLosingTrades")),
        "long_net": _r(_side(stats, "netProfit", "long")),
        "short_net": _r(_side(stats, "netProfit", "short")),
        "long_trades": int(_side(stats, "totalTrades", "long")),
        "short_trades": int(_side(stats, "totalTrades", "short")),
    }


def downsample(points: List, limit: int = MAX_EQUITY_POINTS) -> List:
    """At most `limit` evenly spaced points, always keeping the first and the last."""
    if len(points) <= limit:
        return list(points)
    step = (len(points) - 1) / (limit - 1)
    return [points[i] for i in sorted({round(i * step) for i in range(limit)})]


def _utc(ms) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def _minute(ms) -> str:
    return _utc(ms).strftime("%Y-%m-%d %H:%M")


def ui_payload(report: Dict) -> Dict:
    items = (report.get("history") or {}).get("items", [])
    by_hour = [{"net": 0.0, "count": 0} for _ in range(24)]
    by_weekday = [{"net": 0.0, "count": 0} for _ in range(7)]
    trades = []
    for t in sorted(items, key=lambda item: item["entryTime"]):
        entry = _utc(t["entryTime"])
        for bucket in (by_hour[entry.hour], by_weekday[entry.weekday()]):
            bucket["net"] += float(t["net"])
            bucket["count"] += 1
        trades.append({
            "id": t.get("id"), "direction": t.get("direction"),
            "entry_time": _minute(t["entryTime"]), "close_time": _minute(t["closeTime"]),
            "entry_price": t.get("entryPrice"), "close_price": t.get("closePrice"),
            "lots": t.get("quantity"), "pips": _r(t.get("pips"), 1), "net": _r(t["net"]),
            "commissions": _r(t.get("commissions")), "swaps": _r(t.get("swaps")),
        })
    for bucket in by_hour + by_weekday:
        bucket["net"] = _r(bucket["net"])
    equity = [{"t": p["timestamp"], "balance": _r(p["balance"]), "equity": _r(p["minEquity"])}
              for p in downsample((report.get("equity") or {}).get("points", []))]
    parameters = {p["propertyName"]: p.get("value") for p in report.get("parameters", [])}
    return {"equity": equity, "trades": trades, "pnl_by_hour": by_hour, "pnl_by_weekday": by_weekday,
            "parameters": parameters}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_report.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 6: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 3: Parameters (`app/backtest_params.py`)

**Files:**
- Create: `app/backtest_params.py`
- Create: `tests/fixtures/backtest/flowrsi_metadata.json`
- Test: `tests/test_backtest_params.py`

**Interfaces:**
- Consumes (Task 1): `BotSource`, `locked_params(strategy, job_id)`, `DROPPED_PARAMS`, `HIDDEN_GROUPS`, `ALGO_DIR`, `parse_run_command` (tests)
- Produces:
  - `DockerUnavailable(RuntimeError)`, `MetadataError(RuntimeError)`, `OverrideError(ValueError)`
  - `TIMEFRAMES: Dict[str, int]`
  - `algo_sha256(path) -> str`
  - `parse_metadata_output(text) -> Dict`
  - `docker_metadata_runner(algo_path) -> str`
  - `MetadataCache(cache_dir: Path, runner=docker_metadata_runner)` with `.get(algo_path) -> Dict`. The returned metadata gains a `"sha256"` key.
  - `canonical(p: Dict, raw) -> str`
  - `param_view(meta, source) -> {"groups": [{"name", "params": [{key, label, type, default, bot_value, min, max, enum_values}]}], "locked": {...}, "timeframes": [...], "algo_build_time": str}`
  - `validate_overrides(meta, source, overrides: Dict) -> Dict[str, {"from": str|None, "to": str}]`
  - `job_params(source, overrides_detail) -> Dict[str, str]`

- [ ] **Step 1: Create the metadata fixture**

Create `tests/fixtures/backtest/flowrsi_metadata.json`. These are 23 of FlowRsiBot's 71 parameters, copied from the real `ctrader-cli metadata` output of 2026-09-24. They cover every type, plus the hidden and locked groups.

```json
{
  "Name": "FlowRsiBot", "Type": "cBot", "AccessRights": "FullAccess", "BuildTime": "2026-09-24T16:34:43.3439105Z",
  "Parameters": [
    {"PropertyName": "BotId", "FriendlyName": "Bot ID", "GroupName": "General", "Type": "String", "DefaultValue": "FlowRSI"},
    {"PropertyName": "AccountLabel", "FriendlyName": "Account Identifier", "GroupName": "General", "Type": "String", "DefaultValue": "FlowRSI-Standard"},
    {"PropertyName": "ShowLogs", "FriendlyName": "Show Detailed Logs", "GroupName": "General", "Type": "Boolean", "DefaultValue": true},
    {"PropertyName": "FastRsiPeriod", "FriendlyName": "Fast RSI Period", "GroupName": "Nested RSI Engine", "Type": "Integer", "DefaultValue": 7, "MinValue": 2, "MaxValue": 50},
    {"PropertyName": "RsiBullishCrossMin", "FriendlyName": "Bullish Cross Min (Oversold Floor)", "GroupName": "Nested RSI Engine", "Type": "Double", "DefaultValue": 25.0, "MinValue": 10.0, "MaxValue": 45.0},
    {"PropertyName": "EnableSmcFilter", "FriendlyName": "Enable SMC Structural Filter", "GroupName": "SMC & ICT Market Structure", "Type": "Boolean", "DefaultValue": true},
    {"PropertyName": "MacroTimeFrame", "FriendlyName": "Macro TimeFrame", "GroupName": "Macro TMS Trend Filter", "Type": "TimeFrame", "DefaultValue": {"Type": 0, "Size": 60}},
    {"PropertyName": "RiskPercentage", "FriendlyName": "Risk per Trade (% Equity)", "GroupName": "Risk Management", "Type": "Double", "DefaultValue": 0.5, "MinValue": 0.01, "MaxValue": 10.0},
    {"PropertyName": "SlMode", "FriendlyName": "Stop Loss Mode", "GroupName": "Risk Management", "Type": "Enum", "DefaultValue": 0, "EnumValues": {"Technical_Swing": 0, "ATR_Multiplier": 1, "Fixed_Pips": 2}},
    {"PropertyName": "TargetRiskReward", "FriendlyName": "Target Risk-to-Reward Ratio", "GroupName": "Risk Management", "Type": "Double", "DefaultValue": 1.5, "MinValue": 1.0},
    {"PropertyName": "UseAiGateMode", "FriendlyName": "Enable AI Gate Mode", "GroupName": "AI Agent Integration", "Type": "Boolean", "DefaultValue": true},
    {"PropertyName": "ApiUrl", "FriendlyName": "Agent API URL", "GroupName": "AI Agent Integration", "Type": "String", "DefaultValue": "http://127.0.0.1:8000/trade"},
    {"PropertyName": "AiTelemetryUrl", "FriendlyName": "Telemetry Endpoint", "GroupName": "AI Agent Integration", "Type": "String", "DefaultValue": "http://127.0.0.1:8000/api/tick"},
    {"PropertyName": "AiReportUrl", "FriendlyName": "Portfolio Report Endpoint", "GroupName": "AI Agent Integration", "Type": "String", "DefaultValue": "http://127.0.0.1:8000/portfolio/report"},
    {"PropertyName": "CommandPollMs", "FriendlyName": "Command Poll (ms, 0=off)", "GroupName": "AI Agent Integration", "Type": "Integer", "DefaultValue": 2000, "MinValue": 0},
    {"PropertyName": "AiConfidenceThreshold", "FriendlyName": "AI Minimum Confidence (%)", "GroupName": "AI Agent Integration", "Type": "Double", "DefaultValue": 65.0, "MinValue": 50.0, "MaxValue": 100.0},
    {"PropertyName": "EnableNewsFilter", "FriendlyName": "Enable News Filter", "GroupName": "News Filter", "Type": "Boolean", "DefaultValue": true},
    {"PropertyName": "MinsBeforeNews", "FriendlyName": "Minutes Before News", "GroupName": "News Filter", "Type": "Integer", "DefaultValue": 30, "MinValue": 5},
    {"PropertyName": "EnableTelegramAlerts", "FriendlyName": "Enable Telegram Alerts", "GroupName": "Telegram Integration", "Type": "Boolean", "DefaultValue": false},
    {"PropertyName": "TelegramBotToken", "FriendlyName": "Telegram Bot Token", "GroupName": "Telegram Integration", "Type": "String"},
    {"PropertyName": "TelegramChatId", "FriendlyName": "Telegram Chat ID", "GroupName": "Telegram Integration", "Type": "String"},
    {"PropertyName": "SendChartScreenshot", "FriendlyName": "Send Chart Screenshot", "GroupName": "Telegram Integration", "Type": "Boolean", "DefaultValue": false},
    {"PropertyName": "SendAiAdjustAlerts", "FriendlyName": "Send AI ADJUST Alerts", "GroupName": "Telegram Integration", "Type": "Boolean", "DefaultValue": true}
  ]
}
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_backtest_params.py`:

```python
"""cBot parameters for the Backtest page: the cached `ctrader-cli metadata` schema, the form view
(bot values over defaults, integration groups hidden), and override validation.

The CLI takes enums and time frames by name (verified 2026-09-24: --SlMode=ATR_Multiplier and
--MacroTimeFrame=Hour4 show up as `cmd arg`), so every value is stored in that canonical text form."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import backtest_params as bp  # noqa: E402
from app.backtest_command import parse_run_command  # noqa: E402
from app.cbot_presets import build_run_command  # noqa: E402

META_TEXT = (ROOT / "tests" / "fixtures" / "backtest" / "flowrsi_metadata.json").read_text()
META = json.loads(META_TEXT)
ACCOUNT = {"slug": "demo-demo", "ctid_email": "trader@example.com", "account_number": "10115236",
           "label": "demo", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd"}


def source(**params):
    src = parse_run_command("cbot-demo-demo-eurusd-all-flowrsi",
                            build_run_command(ACCOUNT, "flowrsi", "EURUSD", "/w", "/r"))
    src.params.update(params)
    return src


# --- metadata output and cache ------------------------------------------------------------------

def test_parse_metadata_output_skips_the_command_echo():
    meta = bp.parse_metadata_output("dotnet metadata /algo/FlowRsiBot.algo\n" + META_TEXT + "\n")
    assert meta["Name"] == "FlowRsiBot" and len(meta["Parameters"]) == 23


@pytest.mark.parametrize("text", ["Error: Algo file is not specified", "{not json}", '{"Name": "x"}'])
def test_parse_metadata_output_rejects_garbage(text):
    with pytest.raises(bp.MetadataError):
        bp.parse_metadata_output(text)


def test_cache_runs_metadata_once_per_algo_build(tmp_path):
    algo = tmp_path / "FlowRsiBot.algo"
    algo.write_bytes(b"build-1")
    calls = []

    def runner(path):
        calls.append(path)
        return META_TEXT

    cache = bp.MetadataCache(tmp_path / "meta", runner)
    first = cache.get(algo)
    assert cache.get(algo) is first and len(calls) == 1
    assert first["sha256"] == bp.algo_sha256(algo)
    assert bp.MetadataCache(tmp_path / "meta", runner).get(algo)["Name"] == "FlowRsiBot"   # disk cache
    assert len(calls) == 1
    algo.write_bytes(b"build-2")                                                          # rebuilt .algo
    cache.get(algo)
    assert len(calls) == 2


# --- form view ----------------------------------------------------------------------------------

def test_param_view_hides_locked_and_integration_groups():
    view = bp.param_view(META, source())
    assert [g["name"] for g in view["groups"]] == [
        "General", "Nested RSI Engine", "SMC & ICT Market Structure", "Macro TMS Trend Filter", "Risk Management"]
    keys = {p["key"] for g in view["groups"] for p in g["params"]}
    assert keys == {"ShowLogs", "FastRsiPeriod", "RsiBullishCrossMin", "EnableSmcFilter", "MacroTimeFrame",
                    "RiskPercentage", "SlMode", "TargetRiskReward"}
    assert view["locked"]["UseAiGateMode"] == "false" and view["locked"]["BotId"] == "bt-<id>"
    assert view["timeframes"] == list(bp.TIMEFRAMES)
    assert view["algo_build_time"] == "2026-09-24T16:34:43.3439105Z"


def test_param_view_shows_bot_values_over_canonical_defaults():
    view = bp.param_view(META, source(TargetRiskReward="2.0"))
    params = {p["key"]: p for g in view["groups"] for p in g["params"]}
    assert (params["TargetRiskReward"]["default"], params["TargetRiskReward"]["bot_value"]) == ("1.5", "2.0")
    assert params["FastRsiPeriod"]["bot_value"] == "7"
    assert params["RsiBullishCrossMin"]["bot_value"] == "25.0"
    assert params["ShowLogs"]["bot_value"] == "true"
    assert params["SlMode"]["bot_value"] == "Technical_Swing"
    assert params["SlMode"]["enum_values"] == ["Technical_Swing", "ATR_Multiplier", "Fixed_Pips"]
    assert params["MacroTimeFrame"]["bot_value"] == "Hour"
    assert (params["FastRsiPeriod"]["min"], params["FastRsiPeriod"]["max"]) == (2, 50)
    assert params["TargetRiskReward"]["label"] == "Target Risk-to-Reward Ratio"


# --- overrides ----------------------------------------------------------------------------------

def test_overrides_are_canonical_and_no_ops_are_dropped():
    changes = bp.validate_overrides(META, source(), {
        "TargetRiskReward": 2, "FastRsiPeriod": "7", "SlMode": "ATR_Multiplier", "EnableSmcFilter": False,
        "MacroTimeFrame": "Hour4", "RsiBullishCrossMin": 25,
    })
    assert changes == {
        "TargetRiskReward": {"from": "1.5", "to": "2.0"},
        "SlMode": {"from": "Technical_Swing", "to": "ATR_Multiplier"},
        "EnableSmcFilter": {"from": "true", "to": "false"},
        "MacroTimeFrame": {"from": "Hour", "to": "Hour4"},
    }


@pytest.mark.parametrize("key, value, message", [
    ("UseAiGateMode", True, "locked"),
    ("ApiUrl", "http://evil", "locked"),
    ("AiConfidenceThreshold", 70, "locked"),
    ("TelegramBotToken", "x", "locked"),
    ("BotId", "x", "locked"),
    ("NoSuchParam", 1, "not a parameter"),
    ("FastRsiPeriod", 1, "minimum"),
    ("FastRsiPeriod", 7.5, "whole number"),
    ("FastRsiPeriod", True, "number"),
    ("RsiBullishCrossMin", 50, "maximum"),
    ("RiskPercentage", "abc", "number"),
    ("RiskPercentage", "inf", "number"),
    ("SlMode", "Nope", "one of"),
    ("MacroTimeFrame", "h1", "one of"),
    ("EnableSmcFilter", "yes", "true or false"),
    ("EnableSmcFilter", 1, "true or false"),
])
def test_invalid_overrides_are_rejected(key, value, message):
    with pytest.raises(bp.OverrideError, match=message) as err:
        bp.validate_overrides(META, source(), {key: value})
    assert str(err.value).startswith(key)


def test_job_params_drop_locked_and_secret_keys_and_apply_overrides():
    src = source(TelegramBotToken="123:abc")
    params = bp.job_params(src, {"TargetRiskReward": {"from": "1.5", "to": "2.0"}})
    assert params["TargetRiskReward"] == "2.0" and params["FastRsiPeriod"] == "7"
    for key in ("UseAiGateMode", "ApiUrl", "BotId", "AccountLabel", "TelegramBotToken"):
        assert key not in params, key
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_params.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'app.backtest_params'`.

- [ ] **Step 4: Implement `app/backtest_params.py`**

```python
"""
cBot parameters for the Backtest page.

`ctrader-cli metadata <algo>` lists every parameter (group, type, default, min/max, enum values) but
takes ~15 s, so the schema is cached per .algo SHA-256 in memory and on disk; a rebuilt .algo gets a
fresh one. The form shows the bot's values over the defaults, and overrides are validated here and
kept in the text form the CLI takes: enums and time frames by name (--SlMode=ATR_Multiplier,
--MacroTimeFrame=Hour4), doubles as Python reprs.
"""
import hashlib
import json
import logging
import math
import threading
from pathlib import Path
from typing import Callable, Dict, Optional

from app.backtest_command import ALGO_DIR, DROPPED_PARAMS, HIDDEN_GROUPS, BotSource, locked_params
from app.cbot_presets import DEFAULT_IMAGE

logger = logging.getLogger(__name__)

TIMEFRAMES = {"Minute": 1, "Minute5": 5, "Minute15": 15, "Minute30": 30, "Hour": 60, "Hour4": 240, "Daily": 1440}
_TF_BY_MINUTES = {minutes: name for name, minutes in TIMEFRAMES.items()}
MAX_STRING = 200


class DockerUnavailable(RuntimeError):
    """No Docker daemon on this host (e.g. a developer Mac)."""


class MetadataError(RuntimeError):
    """`ctrader-cli metadata` failed or printed something that is not the schema."""


class OverrideError(ValueError):
    """A user override the backtest must not take. The message starts with the parameter name."""


def algo_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_metadata_output(text: str) -> Dict:
    # The CLI may echo its own command line before the JSON.
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise MetadataError(f"metadata printed no JSON: {text.strip()[:300]}")
    try:
        meta = json.loads(text[start:end + 1])
    except ValueError as e:
        raise MetadataError(f"metadata JSON does not parse: {e}")
    if not isinstance(meta.get("Parameters"), list):
        raise MetadataError("metadata has no Parameters list")
    return meta


def docker_metadata_runner(algo_path: Path) -> str:
    from app.docker_manager import docker_manager
    if not docker_manager.is_available or docker_manager.client is None:
        raise DockerUnavailable("Docker is not available")
    mount = f"{ALGO_DIR}/{algo_path.name}"
    try:
        out = docker_manager.client.containers.run(
            DEFAULT_IMAGE, ["metadata", mount],
            volumes={str(algo_path): {"bind": mount, "mode": "ro"}},
            network_mode="bridge", remove=True, stdout=True, stderr=True)
    except Exception as e:
        raise MetadataError(f"metadata container failed: {e}")
    return out.decode("utf-8", errors="replace") if isinstance(out, bytes) else str(out)


class MetadataCache:
    def __init__(self, cache_dir: Path, runner: Callable[[Path], str] = docker_metadata_runner):
        self.cache_dir = Path(cache_dir)
        self.runner = runner
        self._mem: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def get(self, algo_path: Path) -> Dict:
        """The metadata of this .algo build, with its "sha256" added."""
        sha = algo_sha256(algo_path)
        with self._lock:
            if sha in self._mem:
                return self._mem[sha]
        file = self.cache_dir / f"{sha}.json"
        meta = None
        if file.is_file():
            try:
                meta = json.loads(file.read_text(encoding="utf-8"))
            except ValueError:
                logger.warning(f"Backtest metadata cache {file} is corrupt; fetching it again")
        if meta is None:
            meta = parse_metadata_output(self.runner(Path(algo_path)))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(meta), encoding="utf-8")
        meta["sha256"] = sha
        with self._lock:
            self._mem[sha] = meta
        return meta


def _hidden(p: Dict, strategy: str) -> bool:
    key = p["PropertyName"]
    return p.get("GroupName") in HIDDEN_GROUPS or key in locked_params(strategy, None) or key in DROPPED_PARAMS


def canonical(p: Dict, raw) -> str:
    """A bot value, a JSON override or a metadata default -> the text the CLI takes."""
    kind, key = p["Type"], p["PropertyName"]
    if kind == "Boolean":
        if raw is True or raw in ("true", "True"):
            return "true"
        if raw is False or raw in ("false", "False"):
            return "false"
        raise OverrideError(f"{key}: expected true or false")
    if kind in ("Integer", "Double"):
        if isinstance(raw, bool):
            raise OverrideError(f"{key}: expected a number")
        try:
            number = float(raw)
        except (TypeError, ValueError):
            raise OverrideError(f"{key}: expected a number")
        if not math.isfinite(number):
            raise OverrideError(f"{key}: expected a finite number")
        if kind == "Integer":
            if not number.is_integer():
                raise OverrideError(f"{key}: expected a whole number")
            number = int(number)
        low, high = p.get("MinValue"), p.get("MaxValue")
        if low is not None and number < low:
            raise OverrideError(f"{key}: below the minimum {low}")
        if high is not None and number > high:
            raise OverrideError(f"{key}: above the maximum {high}")
        return str(number) if kind == "Integer" else repr(number)
    if kind == "Enum":
        values = p.get("EnumValues") or {}
        if isinstance(raw, str) and raw in values:
            return raw
        if isinstance(raw, int) and not isinstance(raw, bool):
            for name, value in values.items():
                if value == raw:
                    return name
        raise OverrideError(f"{key}: expected one of {', '.join(values)}")
    if kind == "TimeFrame":
        if isinstance(raw, dict) and raw.get("Size") in _TF_BY_MINUTES:
            return _TF_BY_MINUTES[raw["Size"]]
        if isinstance(raw, str) and raw in TIMEFRAMES:
            return raw
        raise OverrideError(f"{key}: expected one of {', '.join(TIMEFRAMES)}")
    text = "" if raw is None else str(raw)
    if len(text) > MAX_STRING or any(c in text for c in "\r\n\x00"):
        raise OverrideError(f"{key}: at most {MAX_STRING} characters on one line")
    return text


def _shown(p: Dict, raw) -> Optional[str]:
    """canonical() for display: a value the schema does not accept is shown as written."""
    if raw is None:
        return None
    try:
        return canonical(p, raw)
    except OverrideError:
        return str(raw)


def _current(p: Dict, source: BotSource) -> Optional[str]:
    key = p["PropertyName"]
    return _shown(p, source.params[key]) if key in source.params else _shown(p, p.get("DefaultValue"))


def param_view(meta: Dict, source: BotSource) -> Dict:
    groups, by_name = [], {}
    for p in meta["Parameters"]:
        if _hidden(p, source.strategy):
            continue
        name = p.get("GroupName") or "Other"
        if name not in by_name:
            by_name[name] = {"name": name, "params": []}
            groups.append(by_name[name])
        by_name[name]["params"].append({
            "key": p["PropertyName"], "label": p.get("FriendlyName") or p["PropertyName"], "type": p["Type"],
            "default": _shown(p, p.get("DefaultValue")), "bot_value": _current(p, source),
            "min": p.get("MinValue"), "max": p.get("MaxValue"),
            "enum_values": list((p.get("EnumValues") or {}).keys()) if p["Type"] == "Enum" else None,
        })
    return {"groups": groups, "locked": locked_params(source.strategy, None),
            "timeframes": list(TIMEFRAMES), "algo_build_time": meta.get("BuildTime")}


def validate_overrides(meta: Dict, source: BotSource, overrides: Dict) -> Dict[str, Dict]:
    """{key: raw} from the client -> {key: {"from": bot value, "to": canonical value}}, no-ops dropped."""
    specs = {p["PropertyName"]: p for p in meta["Parameters"]}
    changes = {}
    for key, raw in (overrides or {}).items():
        p = specs.get(key)
        if p is None:
            raise OverrideError(f"{key}: not a parameter of {source.algo}")
        if _hidden(p, source.strategy):
            raise OverrideError(f"{key}: locked for backtests")
        value = canonical(p, raw)
        current = _current(p, source)
        if value != current:
            changes[key] = {"from": current, "to": value}
    return changes


def job_params(source: BotSource, overrides: Dict[str, Dict]) -> Dict[str, str]:
    """What the job stores in `params`: the bot's own values with the overrides applied. Locked keys
    are left out; build_container_spec appends them for the job's id."""
    locked = locked_params(source.strategy, None)
    params = {k: v for k, v in source.params.items() if k not in locked and k not in DROPPED_PARAMS}
    for key, change in overrides.items():
        params[key] = change["to"]
    return params
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_params.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 6: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 4: Job store (`app/backtest_store.py`)

**Files:**
- Create: `app/backtest_store.py`
- Modify: `app/portfolio.py` (the import at line 14, and `_init_db` next to `bot_controls.init_schema(conn)`, about line 184)
- Test: `tests/test_backtest_store.py`

**Interfaces:**
- Consumes: `app.db.get_db_connection`
- Produces:
  - Constants: `REPORT_DIR`, `ACTIVE = ("queued", "running")`, `COLUMNS`, `JSON_COLUMNS`
  - Schema and connection: `init_schema(conn)`, `now_text() -> str`, `connect(db_target=None)` (a context manager that yields the connection, commits and closes)
  - CRUD: `create_job(conn, fields) -> int`, `get_job(conn, job_id) -> Optional[Dict]`, `list_jobs(conn, limit=200) -> List[Dict]`, `next_queued(conn) -> Optional[Dict]`, `jobs_with_status(conn, status) -> List[Dict]`, `update_job(conn, job_id, expect_status=None, **fields) -> bool`, `delete_job(conn, job_id)`, `queue_position(conn, job_id) -> int`
  - Report files: `report_path(job_id, report_dir=None) -> Path`, `write_report(job_id, data: bytes, report_dir=None) -> Path`, `read_report(job_id, report_dir=None) -> Optional[Dict]`, `delete_report(job_id, report_dir=None)`
  - Rows come back as dicts, with `overrides`, `params` and `summary` decoded from JSON.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backtest_store.py`:

```python
"""backtest_jobs rows and report files. Runs against a throwaway SQLite file; production uses the same
SQL through app.db's PostgreSQL adapter (INSERT … RETURNING works on both, SQLite >= 3.35)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import backtest_store as store  # noqa: E402

FIELDS = {
    "bot_name": "cbot-demo-demo-eurusd-all-flowrsi", "strategy": "flowrsi", "symbol": "EURUSD", "period": "m15",
    "algo": "FlowRsiBot.algo", "algo_sha": "abc", "algo_build_time": "2026-09-24T16:34:43Z",
    "ctid": "trader@example.com", "account": "10115236", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd",
    "start_date": "2026-07-24", "end_date": "2026-09-23", "data_mode": "ticks", "spread_pips": None,
    "balance": 10000.0, "overrides": {"TargetRiskReward": {"from": "1.5", "to": "2.0"}},
    "params": {"TargetRiskReward": "2.0"}, "note": "rr 2",
}


@pytest.fixture
def db(tmp_path):
    target = tmp_path / "backtests.db"
    with store.connect(target) as conn:
        store.init_schema(conn)
        store.init_schema(conn)          # idempotent
    return target


def test_create_and_get_round_trip(db):
    with store.connect(db) as conn:
        job_id = store.create_job(conn, FIELDS)
        job = store.get_job(conn, job_id)
    assert job["status"] == "queued" and job["created_at"]
    assert job["overrides"] == FIELDS["overrides"] and job["params"] == FIELDS["params"]
    assert job["summary"] is None and job["balance"] == 10000.0


def test_create_refuses_unknown_columns(db):
    with store.connect(db) as conn, pytest.raises(ValueError):
        store.create_job(conn, {**FIELDS, "evil": 1})


def test_lists_newest_first_and_picks_the_oldest_queued(db):
    with store.connect(db) as conn:
        ids = [store.create_job(conn, FIELDS) for _ in range(3)]
        assert [j["id"] for j in store.list_jobs(conn)] == ids[::-1]
        assert store.next_queued(conn)["id"] == ids[0]
        store.update_job(conn, ids[0], status="running")
        assert store.next_queued(conn)["id"] == ids[1]
        assert [j["id"] for j in store.jobs_with_status(conn, "running")] == [ids[0]]


def test_update_with_expected_status_is_a_guard(db):
    with store.connect(db) as conn:
        job_id = store.create_job(conn, FIELDS)
        assert store.update_job(conn, job_id, expect_status="running", status="done") is False
        assert store.get_job(conn, job_id)["status"] == "queued"
        assert store.update_job(conn, job_id, expect_status="queued", status="running", progress=12.5) is True
        job = store.get_job(conn, job_id)
    assert (job["status"], job["progress"]) == ("running", 12.5)


def test_update_encodes_summary(db):
    with store.connect(db) as conn:
        job_id = store.create_job(conn, FIELDS)
        store.update_job(conn, job_id, status="done", summary={"net_profit": -0.98})
        assert store.get_job(conn, job_id)["summary"] == {"net_profit": -0.98}


def test_queue_position_counts_the_running_job_and_older_queued_ones(db):
    with store.connect(db) as conn:
        first, second, third = (store.create_job(conn, FIELDS) for _ in range(3))
        assert [store.queue_position(conn, i) for i in (first, second, third)] == [1, 2, 3]
        store.update_job(conn, first, status="running")
        assert store.queue_position(conn, second) == 2        # behind the running one
        store.update_job(conn, first, status="done")
        assert store.queue_position(conn, second) == 1


def test_delete_job(db):
    with store.connect(db) as conn:
        job_id = store.create_job(conn, FIELDS)
        store.delete_job(conn, job_id)
        assert store.get_job(conn, job_id) is None


def test_report_files(tmp_path):
    reports = tmp_path / "reports"
    path = store.write_report(5, b'{"main": {}}', reports)
    assert path == reports / "5.json" and store.read_report(5, reports) == {"main": {}}
    store.delete_report(5, reports)
    assert store.read_report(5, reports) is None
    store.delete_report(5, reports)                         # already gone: no error
    (reports / "6.json").write_text("{broken")
    assert store.read_report(6, reports) is None


def test_the_app_database_has_the_table():
    from app.server import app  # noqa: F401  (initialises the portfolio DB, which creates the table)
    with store.connect() as conn:
        conn.execute("SELECT COUNT(*) FROM backtest_jobs").fetchone()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_store.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'app.backtest_store'`.

- [ ] **Step 3: Implement `app/backtest_store.py`**

```python
"""
The Backtest page's jobs (backtest_jobs table) and their cTrader report files.

Report files are ~0.8 MB each, so they live in webui_data/backtests/<id>.json (git-ignored) and only
the KPI summary goes into the row. Rows are dicts with the JSON columns already decoded.
"""
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from app.db import get_db_connection

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "webui_data" / "backtests"
ACTIVE = ("queued", "running")
JSON_COLUMNS = ("overrides", "params", "summary")
COLUMNS = (
    "bot_name", "strategy", "symbol", "period", "algo", "algo_sha", "algo_build_time",
    "ctid", "account", "pwd_file", "start_date", "end_date", "data_mode", "spread_pips", "balance",
    "overrides", "params", "note", "status", "phase", "progress", "error", "summary",
    "created_at", "started_at", "finished_at",
)


def init_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backtest_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name TEXT NOT NULL,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            period TEXT NOT NULL,
            algo TEXT NOT NULL,
            algo_sha TEXT,
            algo_build_time TEXT,
            ctid TEXT NOT NULL,
            account TEXT NOT NULL,
            pwd_file TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            data_mode TEXT NOT NULL,
            spread_pips DOUBLE PRECISION,
            balance DOUBLE PRECISION NOT NULL,
            overrides TEXT NOT NULL,
            params TEXT NOT NULL,
            note TEXT,
            status TEXT NOT NULL,
            phase TEXT,
            progress DOUBLE PRECISION,
            error TEXT,
            summary TEXT,
            created_at TEXT NOT NULL,
            started_at TEXT,
            finished_at TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_backtest_jobs_status ON backtest_jobs(status)")


def now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def connect(db_target=None):
    conn = get_db_connection(db_target)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _check(fields: Dict) -> None:
    unknown = set(fields) - set(COLUMNS)
    if unknown:
        raise ValueError(f"unknown backtest_jobs columns: {sorted(unknown)}")


def _encode(fields: Dict) -> Dict:
    return {k: (json.dumps(v) if k in JSON_COLUMNS and v is not None else v) for k, v in fields.items()}


def _decode(row) -> Optional[Dict]:
    if row is None:
        return None
    job = dict(row)
    for key in JSON_COLUMNS:
        if job.get(key):
            job[key] = json.loads(job[key])
    return job


def create_job(conn, fields: Dict) -> int:
    _check(fields)
    data = _encode({"status": "queued", "created_at": now_text(), **fields})
    columns = list(data)
    cur = conn.execute(
        f"INSERT INTO backtest_jobs ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)}) RETURNING id",
        tuple(data[c] for c in columns))
    return int(cur.fetchone()[0])


def get_job(conn, job_id: int) -> Optional[Dict]:
    return _decode(conn.execute("SELECT * FROM backtest_jobs WHERE id = ?", (int(job_id),)).fetchone())


def list_jobs(conn, limit: int = 200) -> List[Dict]:
    rows = conn.execute("SELECT * FROM backtest_jobs ORDER BY id DESC LIMIT ?", (int(limit),)).fetchall()
    return [_decode(r) for r in rows]


def next_queued(conn) -> Optional[Dict]:
    return _decode(conn.execute(
        "SELECT * FROM backtest_jobs WHERE status = 'queued' ORDER BY id LIMIT 1").fetchone())


def jobs_with_status(conn, status: str) -> List[Dict]:
    rows = conn.execute("SELECT * FROM backtest_jobs WHERE status = ? ORDER BY id", (status,)).fetchall()
    return [_decode(r) for r in rows]


def update_job(conn, job_id: int, expect_status: Optional[str] = None, **fields) -> bool:
    """Set `fields`; with expect_status, only while the row still has that status (the worker and the
    cancel button race on the same rows). Returns whether a row changed."""
    _check(fields)
    data = _encode(fields)
    sql = f"UPDATE backtest_jobs SET {', '.join(f'{c} = ?' for c in data)} WHERE id = ?"
    params = [*data.values(), int(job_id)]
    if expect_status is not None:
        sql += " AND status = ?"
        params.append(expect_status)
    return conn.execute(sql, tuple(params)).rowcount > 0


def delete_job(conn, job_id: int) -> None:
    conn.execute("DELETE FROM backtest_jobs WHERE id = ?", (int(job_id),))


def queue_position(conn, job_id: int) -> int:
    """1 = starts as soon as the worker looks; each running or older queued job adds one."""
    row = conn.execute(
        "SELECT COUNT(*) FROM backtest_jobs WHERE status = 'running' OR (status = 'queued' AND id < ?)",
        (int(job_id),)).fetchone()
    return int(row[0]) + 1


def report_path(job_id: int, report_dir: Optional[Path] = None) -> Path:
    return Path(report_dir or REPORT_DIR) / f"{int(job_id)}.json"


def write_report(job_id: int, data: bytes, report_dir: Optional[Path] = None) -> Path:
    path = report_path(job_id, report_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return path


def read_report(job_id: int, report_dir: Optional[Path] = None) -> Optional[Dict]:
    path = report_path(job_id, report_dir)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def delete_report(job_id: int, report_dir: Optional[Path] = None) -> None:
    report_path(job_id, report_dir).unlink(missing_ok=True)
```

- [ ] **Step 4: Create the table at startup**

In `app/portfolio.py`, change the import at line 14:

```python
from app import bot_controls, risk_limits
```

to:

```python
from app import backtest_store, bot_controls, risk_limits
```

In `_init_db`, change:

```python
            risk_limits.init_schema(conn)
            bot_controls.init_schema(conn)
            conn.commit()
```

to:

```python
            risk_limits.init_schema(conn)
            bot_controls.init_schema(conn)
            backtest_store.init_schema(conn)
            conn.commit()
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_store.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 6: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 5: Worker (`app/backtest_worker.py`)

**Files:**
- Create: `app/backtest_worker.py`
- Test: `tests/test_backtest_worker.py`

**Interfaces:**
- Consumes:
  - Task 1: `build_container_spec`, `LABEL`, `REPORT_PATH`
  - Task 2: `summarize`
  - Task 4: `connect`, `get_job`, `jobs_with_status`, `next_queued`, `update_job`, `write_report`, `now_text`
  - `app.ctrader_accounts.ctrader_home`
- Produces:
  - `parse_progress(logs: str) -> Optional[Tuple[str, float]]`
  - `BacktestWorker(client_provider, db_target=None, report_dir=None, project_root=PROJECT_ROOT, ctrader_home_dir=None, clock=utcnow)` with `.tick()`, `async .run_loop()`, `.stop()`
  - The module singleton `backtest_worker`
  - Constants `POLL_S`, `TIMEOUT_S`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backtest_worker.py`:

```python
"""Backtest worker: one bt-<id> container at a time, progress from the CLI's log, the report collected
from the exited container, timeouts, cancel, and restart reconciliation — all against a fake Docker
client and a throwaway SQLite DB."""
import io
import sys
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import backtest_store as store  # noqa: E402
from app.backtest_worker import TIMEOUT_S, BacktestWorker, parse_progress  # noqa: E402

REPORT = (ROOT / "tests" / "fixtures" / "backtest" / "report_small.json").read_bytes()
# The fake clock sits before any real run date: a job the worker starts gets started_at = the real
# now, so its elapsed time on this clock is negative and only the timeout test (which sets
# started_at itself) can cross TIMEOUT_S.
START = datetime(2026, 1, 1, tzinfo=timezone.utc)
JOB = {
    "bot_name": "cbot-demo-demo-eurusd-all-flowrsi", "strategy": "flowrsi", "symbol": "EURUSD", "period": "m15",
    "algo": "FlowRsiBot.algo", "algo_sha": "abc", "algo_build_time": "2026-09-24T16:34:43Z",
    "ctid": "trader@example.com", "account": "10115236", "pwd_file": "/root/ctrader_data/ctid_demo-demo_pwd",
    "start_date": "2026-07-24", "end_date": "2026-09-23", "data_mode": "ticks", "spread_pips": None,
    "balance": 10000.0, "overrides": {}, "params": {"TargetRiskReward": "1.5"}, "note": None,
}


class FakeContainer:
    def __init__(self, box, name, labels):
        self.box, self.name, self.labels = box, name, labels
        self.status = "running"
        self.attrs = {"State": {"ExitCode": 0}}
        self.report = None
        self.log_bytes = b""

    def logs(self, tail=None):
        return self.log_bytes

    def get_archive(self, path):
        if self.report is None:
            raise RuntimeError(f"Could not find the file {path} in container")
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar:
            info = tarfile.TarInfo("report.json")
            info.size = len(self.report)
            tar.addfile(info, io.BytesIO(self.report))
        return iter([buf.getvalue()]), {"name": "report.json"}

    def finish(self, exit_code=0, report=None):
        self.status = "exited"
        self.attrs["State"]["ExitCode"] = exit_code
        self.report = report

    def remove(self, force=False):
        self.box.removed.append(self.name)
        self.box.items.pop(self.name, None)


class FakeContainers:
    def __init__(self):
        self.items, self.runs, self.removed = {}, [], []
        self.fail_run = None

    def run(self, **spec):
        if self.fail_run:
            raise self.fail_run
        self.runs.append(spec)
        container = FakeContainer(self, spec["name"], spec["labels"])
        self.items[spec["name"]] = container
        return container

    def list(self, all=False, filters=None):
        return [c for c in self.items.values() if filters["label"] in c.labels]

    def orphan(self, job_id):
        container = FakeContainer(self, f"bt-{job_id}", {"agentfx.backtest": str(job_id)})
        self.items[container.name] = container
        return container


class FakeClient:
    def __init__(self):
        self.containers = FakeContainers()


class Clock:
    def __init__(self):
        self.now = START

    def __call__(self):
        return self.now


@pytest.fixture
def env(tmp_path):
    project = tmp_path / "project"
    (project / "cBot").mkdir(parents=True)
    (project / "cBot" / "FlowRsiBot.algo").write_bytes(b"algo")
    ctrader = tmp_path / "ctrader"
    (ctrader / "ctrader_data").mkdir(parents=True)
    (ctrader / "ctrader_data" / "ctid_demo-demo_pwd").write_text("pw")
    db = tmp_path / "bt.db"
    with store.connect(db) as conn:
        store.init_schema(conn)
    client, clock = FakeClient(), Clock()
    worker = BacktestWorker(client_provider=lambda: client, db_target=db, report_dir=tmp_path / "reports",
                            project_root=project, ctrader_home_dir=ctrader, clock=clock)

    class Env:
        pass
    e = Env()
    e.db, e.client, e.clock, e.worker, e.reports, e.ctrader = db, client, clock, worker, tmp_path / "reports", ctrader
    return e


def queue(env, **over):
    with store.connect(env.db) as conn:
        return store.create_job(conn, {**JOB, **over})


def job(env, job_id):
    with store.connect(env.db) as conn:
        return store.get_job(conn, job_id)


def set_fields(env, job_id, **fields):
    with store.connect(env.db) as conn:
        store.update_job(conn, job_id, **fields)


def test_parse_progress_takes_the_last_line():
    logs = ("Progress | Loading EURUSD, m15 | 33.87 % |\nProgress | Backtesting | 18.93 % |\n"
            "23/09/2026 18:00:00.000 | Info | [Order Executed] Buy 0.19 lots\nProgress | Backtesting | 20.50 % |\n")
    assert parse_progress(logs) == ("backtesting", 20.5)
    assert parse_progress("Progress | Loading EURUSD, m15 | 22.58 % |") == ("loading", 22.58)
    assert parse_progress("Logged in.") is None


def test_a_queued_job_starts_in_its_bt_container(env):
    job_id = queue(env)
    env.worker.tick()
    [spec] = env.client.containers.runs
    assert spec["name"] == f"bt-{job_id}" and spec["network_mode"] == "bridge"
    row = job(env, job_id)
    assert (row["status"], row["phase"], row["progress"]) == ("running", "starting", 0.0)
    assert row["started_at"]


def test_only_one_job_runs_at_a_time(env):
    first, second = queue(env), queue(env)
    env.worker.tick()
    env.worker.tick()
    assert len(env.client.containers.runs) == 1
    assert job(env, first)["status"] == "running" and job(env, second)["status"] == "queued"


def test_progress_is_read_from_the_log(env):
    job_id = queue(env)
    env.worker.tick()
    env.client.containers.items[f"bt-{job_id}"].log_bytes = b"Progress | Backtesting | 42.50 % |\n"
    env.worker.tick()
    row = job(env, job_id)
    assert (row["phase"], row["progress"]) == ("backtesting", 42.5)


def test_a_finished_job_is_collected_and_the_next_one_starts(env):
    first, second = queue(env), queue(env)
    env.worker.tick()
    env.client.containers.items[f"bt-{first}"].finish(0, REPORT)
    env.worker.tick()
    row = job(env, first)
    assert row["status"] == "done" and row["progress"] == 100.0 and row["finished_at"]
    assert row["summary"]["net_profit"] == -0.98 and row["summary"]["total_trades"] == 4
    assert store.read_report(first, env.reports)["main"]["symbol"] == "EURUSD"
    assert f"bt-{first}" in env.client.containers.removed
    assert job(env, second)["status"] == "running"


def test_a_non_zero_exit_fails_with_the_log_tail(env):
    job_id = queue(env)
    env.worker.tick()
    container = env.client.containers.items[f"bt-{job_id}"]
    container.log_bytes = b"Establishing connection...\nLogin failed: wrong password\n"
    container.finish(1)
    env.worker.tick()
    row = job(env, job_id)
    assert row["status"] == "failed" and row["error"].startswith("exit code 1")
    assert "Login failed" in row["error"] and f"bt-{job_id}" in env.client.containers.removed


def test_exit_zero_without_a_report_fails(env):
    job_id = queue(env)
    env.worker.tick()
    env.client.containers.items[f"bt-{job_id}"].finish(0, None)
    env.worker.tick()
    assert job(env, job_id)["error"].startswith("no report written")


def test_an_unparsable_report_fails_but_keeps_the_file(env):
    job_id = queue(env)
    env.worker.tick()
    env.client.containers.items[f"bt-{job_id}"].finish(0, b"{not json")
    env.worker.tick()
    assert job(env, job_id)["error"].startswith("report unparsable")
    assert store.report_path(job_id, env.reports).read_bytes() == b"{not json"


def test_a_job_past_the_timeout_is_stopped(env):
    job_id = queue(env)
    env.worker.tick()
    set_fields(env, job_id, started_at=START.strftime("%Y-%m-%d %H:%M:%S"))
    env.clock.now = START + timedelta(seconds=TIMEOUT_S - 60)
    env.worker.tick()
    assert job(env, job_id)["status"] == "running"
    env.clock.now = START + timedelta(seconds=TIMEOUT_S + 60)
    env.worker.tick()
    row = job(env, job_id)
    assert row["status"] == "failed" and row["error"] == "timeout (45 min)"
    assert f"bt-{job_id}" in env.client.containers.removed


def test_a_cancelled_queued_job_never_starts(env):
    job_id = queue(env)
    set_fields(env, job_id, status="cancelled")
    env.worker.tick()
    assert env.client.containers.runs == []


def test_cancelling_a_running_job_removes_its_container(env):
    job_id = queue(env)
    env.worker.tick()
    set_fields(env, job_id, status="cancelled")
    env.worker.tick()
    assert f"bt-{job_id}" in env.client.containers.removed
    assert job(env, job_id)["status"] == "cancelled"


def test_reconcile_marks_a_running_job_without_container_lost(env):
    job_id = queue(env)
    set_fields(env, job_id, status="running", started_at=START.strftime("%Y-%m-%d %H:%M:%S"))
    env.worker.tick()
    row = job(env, job_id)
    assert (row["status"], row["error"]) == ("failed", "container lost")


def test_reconcile_collects_a_job_that_finished_while_the_app_was_down(env):
    job_id = queue(env)
    set_fields(env, job_id, status="running", started_at=START.strftime("%Y-%m-%d %H:%M:%S"))
    env.client.containers.orphan(job_id).finish(0, REPORT)
    env.worker.tick()
    assert job(env, job_id)["status"] == "done"


def test_reconcile_removes_labelled_containers_without_a_running_job(env):
    env.client.containers.orphan(999)
    env.worker.tick()
    assert env.client.containers.removed == ["bt-999"]


def test_a_start_failure_marks_the_job_failed(env):
    job_id = queue(env)
    env.client.containers.fail_run = RuntimeError("image not found")
    env.worker.tick()
    row = job(env, job_id)
    assert row["status"] == "failed" and row["error"] == "start failed: image not found"


def test_a_missing_password_file_fails_at_start(env):
    job_id = queue(env)
    (env.ctrader / "ctrader_data" / "ctid_demo-demo_pwd").unlink()
    env.worker.tick()
    assert job(env, job_id)["error"] == "start failed: password file not found"
    assert env.client.containers.runs == []


def test_without_docker_the_tick_does_nothing(env):
    job_id = queue(env)
    env.worker.client_provider = lambda: None
    env.worker.tick()
    assert job(env, job_id)["status"] == "queued"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_worker.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'app.backtest_worker'`.

- [ ] **Step 3: Implement `app/backtest_worker.py`**

```python
"""
Runs the Backtest page's jobs, one at a time, in `bt-<id>` containers
(docs/superpowers/specs/2026-09-24-backtest-page-design.md).

The asyncio loop only schedules. tick() does the work in a thread, so Docker and DB calls never block
the event loop that serves /trade and /ws/cbot. Containers outlive the app process, so every tick
starts from the containers labelled agentfx.backtest: after a restart it picks a running job back up,
collects one that finished meanwhile, and marks one whose container vanished as lost.
"""
import asyncio
import io
import json
import logging
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from app import backtest_store as store
from app.backtest_command import LABEL, REPORT_PATH, build_container_spec
from app.backtest_report import summarize
from app.ctrader_accounts import ctrader_home

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POLL_S = 3.0
TIMEOUT_S = 45 * 60
LOG_TAIL = 20
ERROR_TAIL = 50
PROGRESS_RE = re.compile(r"^Progress \| (.+?) \| ([\d.]+) %", re.MULTILINE)


def parse_progress(logs: str) -> Optional[Tuple[str, float]]:
    """The CLI prints `Progress | Loading EURUSD, m15 | 33.87 % |`, then `Progress | Backtesting | 20.50 % |`."""
    found = PROGRESS_RE.findall(logs or "")
    if not found:
        return None
    text, pct = found[-1]
    return ("backtesting" if text.startswith("Backtesting") else "loading"), float(pct)


def _docker_client():
    from app.docker_manager import docker_manager
    return docker_manager.client if docker_manager.is_available else None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BacktestWorker:
    def __init__(self, client_provider: Callable = _docker_client, db_target=None,
                 report_dir: Optional[Path] = None, project_root: Path = PROJECT_ROOT,
                 ctrader_home_dir: Optional[Path] = None, clock: Callable[[], datetime] = _utcnow):
        self.client_provider = client_provider
        self.db_target = db_target
        self.report_dir = report_dir
        self.project_root = Path(project_root)
        self.ctrader_home_dir = ctrader_home_dir
        self.clock = clock
        self._running = False

    async def run_loop(self):
        self._running = True
        logger.info("Backtest worker started")
        while self._running:
            try:
                await asyncio.to_thread(self.tick)
            except Exception as e:
                logger.error(f"Backtest worker tick failed: {e}", exc_info=True)
            await asyncio.sleep(POLL_S)

    def stop(self):
        self._running = False

    def tick(self) -> None:
        client = self.client_provider()
        if client is None:
            return
        containers = {}
        for container in client.containers.list(all=True, filters={"label": LABEL}):
            try:
                containers[int(container.labels.get(LABEL, ""))] = container
            except ValueError:
                continue
        with store.connect(self.db_target) as conn:
            # Containers whose job was cancelled, deleted or already finished.
            for job_id, container in list(containers.items()):
                job = store.get_job(conn, job_id)
                if job is None or job["status"] != "running":
                    self._remove(container)
                    containers.pop(job_id)
            for job in store.jobs_with_status(conn, "running"):
                container = containers.get(job["id"])
                if container is None:
                    self._fail(conn, job, "container lost")
                elif container.status in ("exited", "dead"):
                    self._collect(conn, job, container)
                elif self._elapsed(job) > TIMEOUT_S:
                    self._remove(container)
                    self._fail(conn, job, f"timeout ({TIMEOUT_S // 60} min)")
                else:
                    progress = parse_progress(self._logs(container, LOG_TAIL))
                    if progress:
                        store.update_job(conn, job["id"], expect_status="running",
                                         phase=progress[0], progress=progress[1])
            if not store.jobs_with_status(conn, "running"):
                job = store.next_queued(conn)
                if job:
                    self._start(conn, client, job)

    def _start(self, conn, client, job: Dict) -> None:
        try:
            home = self.ctrader_home_dir or Path(ctrader_home())
            client.containers.run(**build_container_spec(job, self.project_root, home))
        except Exception as e:
            self._fail(conn, job, f"start failed: {e}", expect="queued")
            return
        store.update_job(conn, job["id"], expect_status="queued", status="running", phase="starting",
                         progress=0.0, started_at=store.now_text())
        logger.info(f"Backtest #{job['id']} started ({job['symbol']} {job['start_date']}..{job['end_date']})")

    def _collect(self, conn, job: Dict, container) -> None:
        exit_code = (container.attrs.get("State") or {}).get("ExitCode")
        raw = self._read_report(container) if exit_code == 0 else None
        if raw is None:
            reason = "no report written" if exit_code == 0 else f"exit code {exit_code}"
            self._fail(conn, job, f"{reason}\n{self._logs(container, ERROR_TAIL).strip()}".strip())
        else:
            store.write_report(job["id"], raw, self.report_dir)
            try:
                summary = summarize(json.loads(raw))
            except (ValueError, KeyError, TypeError) as e:
                self._fail(conn, job, f"report unparsable: {e}")
            else:
                store.update_job(conn, job["id"], expect_status="running", status="done", phase="done",
                                 progress=100.0, summary=summary, finished_at=store.now_text())
                logger.info(f"Backtest #{job['id']} done: net {summary['net_profit']}, {summary['total_trades']} trades")
        self._remove(container)

    def _fail(self, conn, job: Dict, error: str, expect: str = "running") -> None:
        store.update_job(conn, job["id"], expect_status=expect, status="failed", error=error,
                         finished_at=store.now_text())
        logger.warning(f"Backtest #{job['id']} failed: {error.splitlines()[0]}")

    def _elapsed(self, job: Dict) -> float:
        started = job.get("started_at")
        if not started:
            return 0.0
        at = datetime.strptime(started[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return (self.clock() - at).total_seconds()

    @staticmethod
    def _read_report(container) -> Optional[bytes]:
        try:
            stream, _ = container.get_archive(REPORT_PATH)
            with tarfile.open(fileobj=io.BytesIO(b"".join(stream))) as tar:
                member = next((m for m in tar.getmembers() if m.isfile()), None)
                handle = tar.extractfile(member) if member else None
                return handle.read() if handle else None
        except Exception:
            return None

    @staticmethod
    def _logs(container, tail: int) -> str:
        try:
            return container.logs(tail=tail).decode("utf-8", errors="replace")
        except Exception:
            return ""

    @staticmethod
    def _remove(container) -> None:
        try:
            container.remove(force=True)
        except Exception as e:
            logger.warning(f"Could not remove backtest container {getattr(container, 'name', '?')}: {e}")


backtest_worker = BacktestWorker()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_worker.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 5: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 6: API and server wiring (`app/backtest_api.py`)

**Files:**
- Create: `app/backtest_api.py`
- Modify: `app/server.py` (the `lifespan` function at about lines 175-194, and the router include at about line 202)
- Test: `tests/test_backtest_api.py`

**Interfaces:**
- Consumes:
  - Task 1: `describe_source`, `parse_run_command`, `algo_host_path`
  - Task 2: `ui_payload`
  - Task 3: `MetadataCache`, `param_view`, `validate_overrides`, `job_params`, and the three errors
  - Task 4: store functions
  - Task 5: `backtest_worker`
  - `get_portfolio_manager().get_cbot_configs()` / `.get_cbot_config(name)`
- Produces:
  - `router`
  - Module attributes that tests monkeypatch: `PROJECT_ROOT`, `metadata_cache`, `docker_available()`, `today_utc()`
  - `BacktestCreate`, `validate_run_config(req, today)`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backtest_api.py`:

```python
"""/api/backtests*: sources, the parameter form, job creation with validation, list/detail/report,
cancel and delete. Docker and the metadata container are faked; the DB is the pytest SQLite file."""
import inspect
import json
import sys
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.backtest_api as api  # noqa: E402
import app.server as server  # noqa: E402
from app import backtest_store as store  # noqa: E402
from app.backtest_params import MetadataError  # noqa: E402
from app.cbot_presets import build_run_command, container_name  # noqa: E402
from app.portfolio import get_portfolio_manager  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "backtest"
META = json.loads((FIXTURES / "flowrsi_metadata.json").read_text())
REPORT = (FIXTURES / "report_small.json").read_bytes()
client = TestClient(server.app)
ACCOUNT = {"slug": "bttest", "ctid_email": "trader@example.com", "account_number": "10115236",
           "label": "demo", "pwd_file": "/root/ctrader_data/ctid_bttest_pwd"}
FLOW = container_name("bttest", "flowrsi", "EURUSD")
JUDAS = container_name("bttest", "judas", "EURUSD")


class FakeCache:
    def __init__(self):
        self.error = None

    def get(self, algo_path):
        if self.error:
            raise self.error
        return {**META, "sha256": "f" * 64}


@pytest.fixture
def env(tmp_path, monkeypatch):
    project = tmp_path / "project"
    (project / "cBot").mkdir(parents=True)
    (project / "cBot" / "FlowRsiBot.algo").write_bytes(b"algo")
    ctrader = tmp_path / "ctrader"
    (ctrader / "ctrader_data").mkdir(parents=True)
    (ctrader / "ctrader_data" / "ctid_bttest_pwd").write_text("pw")
    cache = FakeCache()
    monkeypatch.setenv("CTRADER_HOME", str(ctrader))
    monkeypatch.setattr(api, "PROJECT_ROOT", project)
    monkeypatch.setattr(api, "metadata_cache", cache)
    monkeypatch.setattr(api, "docker_available", lambda: True)
    monkeypatch.setattr(api, "today_utc", lambda: date(2026, 9, 25))
    monkeypatch.setattr(store, "REPORT_DIR", tmp_path / "reports")
    pm = get_portfolio_manager()
    for strategy, name in (("flowrsi", FLOW), ("judas", JUDAS)):
        pm.delete_cbot_config(name)
        assert pm.add_cbot_config(name, "", build_run_command(ACCOUNT, strategy, "EURUSD", "/w", "/r"))
    with store.connect() as conn:
        conn.execute("DELETE FROM backtest_jobs")
    yield cache
    for name in (FLOW, JUDAS):
        pm.delete_cbot_config(name)
    with store.connect() as conn:
        conn.execute("DELETE FROM backtest_jobs")


def body(**over):
    data = {"bot_name": FLOW, "start": "2026-07-24", "end": "2026-09-23", "data_mode": "ticks",
            "balance": 10000, "note": "rr 2", "overrides": {"TargetRiskReward": 2.0}}
    data.update(over)
    return data


def create(**over):
    resp = client.post("/api/backtests", json=body(**over))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_sources_list_flowrsi_as_supported_and_judas_as_not(env):
    resp = client.get("/api/backtests/sources")
    assert resp.status_code == 200
    rows = {r["name"]: r for r in resp.json()["sources"]}
    assert rows[FLOW]["supported"] is True and rows[FLOW]["symbol"] == "EURUSD"
    assert rows[JUDAS]["supported"] is False and "AI" in rows[JUDAS]["reason"]


def test_params_view(env):
    resp = client.get(f"/api/backtests/sources/{FLOW}/params")
    assert resp.status_code == 200
    view = resp.json()
    assert view["locked"]["UseAiGateMode"] == "false"
    params = {p["key"]: p for g in view["groups"] for p in g["params"]}
    assert params["TargetRiskReward"]["bot_value"] == "1.5" and "UseAiGateMode" not in params


def test_params_error_codes(env, monkeypatch):
    assert client.get("/api/backtests/sources/cbot-nope/params").status_code == 404
    assert client.get(f"/api/backtests/sources/{JUDAS}/params").status_code == 422
    env.error = MetadataError("metadata printed no JSON")
    assert client.get(f"/api/backtests/sources/{FLOW}/params").status_code == 502
    env.error = None
    monkeypatch.setattr(api, "docker_available", lambda: False)
    assert client.get(f"/api/backtests/sources/{FLOW}/params").status_code == 503


def test_create_stores_a_queued_job(env):
    res = create()
    assert (res["status"], res["queue_position"]) == ("queued", 1)
    with store.connect() as conn:
        job = store.get_job(conn, res["id"])
    assert job["overrides"] == {"TargetRiskReward": {"from": "1.5", "to": "2.0"}}
    assert job["params"]["TargetRiskReward"] == "2.0" and "UseAiGateMode" not in job["params"]
    assert (job["algo"], job["algo_sha"], job["algo_build_time"]) == (
        "FlowRsiBot.algo", "f" * 64, "2026-09-24T16:34:43.3439105Z")
    assert (job["start_date"], job["end_date"], job["note"]) == ("2026-07-24", "2026-09-23", "rr 2")
    assert job["pwd_file"] == "/root/ctrader_data/ctid_bttest_pwd"
    listed = client.get("/api/backtests").json()["jobs"]
    assert listed[0]["id"] == res["id"]
    assert "ctid" not in listed[0] and "pwd_file" not in listed[0]


def test_queue_position_counts_jobs_ahead(env):
    assert [create()["queue_position"] for _ in range(2)] == [1, 2]


@pytest.mark.parametrize("over", [
    {"start": "2026-09-24", "end": "2026-09-23"},
    {"end": "2026-09-26"},
    {"start": "2025-09-25", "end": "2026-09-25"},            # 366 days
    {"data_mode": "m1"},                                      # no spread
    {"data_mode": "m1", "spread_pips": 0},
    {"spread_pips": 1.0},                                     # spread with ticks
    {"data_mode": "csv"},
    {"balance": 50},
    {"note": "two\nlines"},
    {"note": "x" * 201},
    {"overrides": {"UseAiGateMode": True}},
    {"overrides": {"NoSuchParam": 1}},
    {"overrides": {"FastRsiPeriod": 1}},
])
def test_create_rejects_bad_input(env, over):
    assert client.post("/api/backtests", json=body(**over)).status_code == 422


def test_create_accepts_m1_with_spread_and_a_full_year(env):
    create(data_mode="m1", spread_pips=1.2)
    create(start="2025-09-26", end="2026-09-25")              # 365 days


def test_create_refuses_unknown_and_unsupported_bots(env):
    assert client.post("/api/backtests", json=body(bot_name="cbot-nope")).status_code == 404
    assert client.post("/api/backtests", json=body(bot_name=JUDAS, overrides={})).status_code == 422


def test_detail_of_a_done_job_includes_the_report(env):
    job_id = create()["id"]
    with store.connect() as conn:
        store.update_job(conn, job_id, status="done", summary={"net_profit": -0.98})
    store.write_report(job_id, REPORT)
    detail = client.get(f"/api/backtests/{job_id}").json()
    assert detail["summary"] == {"net_profit": -0.98}
    assert len(detail["report"]["trades"]) == 4 and len(detail["report"]["pnl_by_hour"]) == 24
    assert detail["report"]["parameters"]["TargetRiskReward"] == "1.5"
    raw = client.get(f"/api/backtests/{job_id}/report.json")
    assert raw.status_code == 200 and raw.json()["main"]["symbol"] == "EURUSD"


def test_detail_of_a_queued_job_has_no_report(env):
    job_id = create()["id"]
    assert client.get(f"/api/backtests/{job_id}").json()["report"] is None
    assert client.get(f"/api/backtests/{job_id}/report.json").status_code == 404
    assert client.get("/api/backtests/999999").status_code == 404


def test_cancel_and_delete(env):
    job_id = create()["id"]
    assert client.delete(f"/api/backtests/{job_id}").status_code == 409        # still queued
    assert client.post(f"/api/backtests/{job_id}/cancel").json()["status"] == "cancelled"
    assert client.post(f"/api/backtests/{job_id}/cancel").status_code == 409
    store.write_report(job_id, REPORT)
    assert client.delete(f"/api/backtests/{job_id}").status_code == 200
    assert client.get(f"/api/backtests/{job_id}").status_code == 404
    assert not store.report_path(job_id).exists()


def test_worker_is_started_by_the_lifespan_but_not_under_pytest():
    src = inspect.getsource(server.lifespan.__wrapped__)
    assert "backtest_worker.run_loop()" in src
    assert src.index("is_running_under_test()") < src.index("backtest_worker.run_loop()")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_api.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'app.backtest_api'`.

- [ ] **Step 3: Implement `app/backtest_api.py`**

```python
"""
HTTP API of the dashboard's Backtest page (docs/superpowers/specs/2026-09-24-backtest-page-design.md).

Handlers are plain `def`: FastAPI runs them in its threadpool, so the Docker and DB calls never block
the event loop that serves the cBots (see the note above /api/bots in app/dashboard.py).
"""
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Literal, Optional, Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app import backtest_store as store
from app.backtest_command import BotSource, algo_host_path, describe_source, parse_run_command
from app.backtest_params import (DockerUnavailable, MetadataCache, MetadataError, OverrideError, job_params,
                                 param_view, validate_overrides)
from app.backtest_report import ui_payload
from app.ctrader_accounts import ctrader_home
from app.portfolio import get_portfolio_manager

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_SPAN_DAYS = 365
PRIVATE_FIELDS = ("ctid", "pwd_file")
metadata_cache = MetadataCache(store.REPORT_DIR / "metadata")


def docker_available() -> bool:
    from app.docker_manager import docker_manager
    return bool(docker_manager.is_available)


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


class BacktestCreate(BaseModel):
    bot_name: str
    start: date
    end: date
    data_mode: Literal["ticks", "m1"] = "ticks"
    spread_pips: Optional[float] = None
    balance: float = 10000.0
    note: Optional[str] = None
    overrides: Dict[str, Union[bool, int, float, str]] = Field(default_factory=dict)


def validate_run_config(req: BacktestCreate, today: date) -> None:
    if req.start > req.end:
        raise HTTPException(422, "start must be on or before end")
    if req.end > today:
        raise HTTPException(422, "end must not be after today (UTC)")
    if (req.end - req.start).days + 1 > MAX_SPAN_DAYS:
        raise HTTPException(422, f"the range must be at most {MAX_SPAN_DAYS} days")
    if req.data_mode == "m1":
        if req.spread_pips is None or not req.spread_pips > 0:
            raise HTTPException(422, "m1 data needs a spread in pips (> 0): m1 bars carry no spread")
    elif req.spread_pips is not None:
        raise HTTPException(422, "spread_pips is only used with m1 data")
    if not 100 <= req.balance <= 10_000_000:
        raise HTTPException(422, "balance must be between 100 and 10,000,000")
    if req.note is not None and (len(req.note) > 200 or re.search(r"[\x00-\x1f]", req.note)):
        raise HTTPException(422, "note must be at most 200 characters on one line")


def _load_source(bot_name: str) -> BotSource:
    cfg = get_portfolio_manager().get_cbot_config(bot_name)
    if cfg is None:
        raise HTTPException(404, f"unknown bot {bot_name}")
    row = describe_source(cfg["name"], cfg["run_command"], PROJECT_ROOT, Path(ctrader_home()))
    if not row["supported"]:
        raise HTTPException(422, row["reason"])
    return parse_run_command(cfg["name"], cfg["run_command"])


def _metadata(source: BotSource) -> Dict:
    if not docker_available():
        raise HTTPException(503, "Docker is not available on this server")
    try:
        return metadata_cache.get(algo_host_path(source.algo, PROJECT_ROOT))
    except DockerUnavailable as e:
        raise HTTPException(503, str(e))
    except MetadataError as e:
        raise HTTPException(502, str(e))


def _public(job: Dict) -> Dict:
    return {k: v for k, v in job.items() if k not in PRIVATE_FIELDS}


def _job_or_404(conn, job_id: int) -> Dict:
    job = store.get_job(conn, job_id)
    if job is None:
        raise HTTPException(404, f"backtest {job_id} not found")
    return job


@router.get("/api/backtests/sources")
def api_backtest_sources():
    home = Path(ctrader_home())
    rows = [describe_source(c["name"], c["run_command"], PROJECT_ROOT, home)
            for c in get_portfolio_manager().get_cbot_configs()]
    rows.sort(key=lambda r: (not r["supported"], r["name"]))
    return {"sources": rows, "docker_available": docker_available()}


@router.get("/api/backtests/sources/{bot_name}/params")
def api_backtest_source_params(bot_name: str):
    source = _load_source(bot_name)
    return param_view(_metadata(source), source)


@router.post("/api/backtests", status_code=201)
def api_create_backtest(req: BacktestCreate):
    validate_run_config(req, today_utc())
    source = _load_source(req.bot_name)
    meta = _metadata(source)
    try:
        overrides = validate_overrides(meta, source, req.overrides)
    except OverrideError as e:
        raise HTTPException(422, str(e))
    fields = {
        "bot_name": source.name, "strategy": source.strategy, "symbol": source.symbol, "period": source.period,
        "algo": source.algo, "algo_sha": meta.get("sha256"), "algo_build_time": meta.get("BuildTime"),
        "ctid": source.ctid, "account": source.account, "pwd_file": source.pwd_file,
        "start_date": req.start.isoformat(), "end_date": req.end.isoformat(), "data_mode": req.data_mode,
        "spread_pips": req.spread_pips, "balance": req.balance, "overrides": overrides,
        "params": job_params(source, overrides), "note": (req.note or "").strip() or None,
    }
    with store.connect() as conn:
        job_id = store.create_job(conn, fields)
        position = store.queue_position(conn, job_id)
    return {"id": job_id, "status": "queued", "queue_position": position}


@router.get("/api/backtests")
def api_list_backtests():
    with store.connect() as conn:
        jobs = store.list_jobs(conn)
    return {"jobs": [_public(j) for j in jobs], "docker_available": docker_available()}


@router.get("/api/backtests/{job_id}")
def api_get_backtest(job_id: int):
    with store.connect() as conn:
        job = _job_or_404(conn, job_id)
    result = _public(job)
    report = store.read_report(job_id) if job["status"] == "done" else None
    result["report"] = ui_payload(report) if report else None
    return result


@router.get("/api/backtests/{job_id}/report.json")
def api_backtest_report_file(job_id: int):
    with store.connect() as conn:
        _job_or_404(conn, job_id)
    path = store.report_path(job_id)
    if not path.is_file():
        raise HTTPException(404, "no report for this backtest")
    return FileResponse(path, media_type="application/json", filename=f"backtest-{job_id}.json")


@router.post("/api/backtests/{job_id}/cancel")
def api_cancel_backtest(job_id: int):
    with store.connect() as conn:
        job = _job_or_404(conn, job_id)
        if job["status"] not in store.ACTIVE:
            raise HTTPException(409, f"backtest {job_id} is already {job['status']}")
        # A running job's container is stopped by the worker on its next tick.
        if not store.update_job(conn, job_id, expect_status=job["status"], status="cancelled",
                                finished_at=store.now_text()):
            raise HTTPException(409, f"backtest {job_id} changed state; try again")
    return {"id": job_id, "status": "cancelled"}


@router.delete("/api/backtests/{job_id}")
def api_delete_backtest(job_id: int):
    with store.connect() as conn:
        job = _job_or_404(conn, job_id)
        if job["status"] in store.ACTIVE:
            raise HTTPException(409, "cancel the backtest before deleting it")
        store.delete_job(conn, job_id)
    store.delete_report(job_id)
    return {"id": job_id, "deleted": True}
```

- [ ] **Step 4: Wire it into `app/server.py`**

Replace the `lifespan` function (about lines 175-194) with this version. It adds the worker and keeps the watchdog code as it was:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        loop = asyncio.get_running_loop()
        ws_manager.set_event_loop(loop)
    except Exception as e:
        logger.warning(f"Failed to set event loop for ws_manager: {e}")

    # Start cBot Watchdog service for automatic relogin and crash recovery
    from app.cbot_watchdog import cbot_watchdog
    watchdog_task = asyncio.create_task(cbot_watchdog.run_loop())

    # Backtest worker. Never under pytest: it removes every container labelled agentfx.backtest whose
    # job is not running in *its* DB, and a test run points at a throwaway SQLite file.
    from app.backtest_worker import backtest_worker
    backtest_task = None
    if not is_running_under_test():
        backtest_task = asyncio.create_task(backtest_worker.run_loop())

    yield

    # Shutdown watchdog cleanly
    cbot_watchdog.stop()
    watchdog_task.cancel()
    try:
        await watchdog_task
    except asyncio.CancelledError:
        pass
    if backtest_task:
        backtest_worker.stop()
        backtest_task.cancel()
        try:
            await backtest_task
        except asyncio.CancelledError:
            pass
```

After `app.include_router(dashboard_router)`, add:

```python
from app.backtest_api import router as backtest_router
app.include_router(backtest_router)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_api.py -q -p no:cacheprovider`
Expected: all tests pass.

- [ ] **Step 6: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 7: Dashboard page (`static/js/backtest.js`, `templates/dashboard.html`, CSS)

**Files:**
- Create: `static/js/backtest.js`
- Modify: `templates/dashboard.html`. The places to edit are the CSS link and `<head>` scripts at lines 6-9, the nav block at lines 80-83, the start of `view-docker` at about line 519, and `switchView` at about lines 884-896.
- Modify: `static/css/dashboard.css` (append at the end)
- Test: `tests/test_backtest_ui.py`

**Interfaces:**
- Consumes:
  - Task 6's routes
  - `escapeHtml` from the dashboard's inline script. `backtest.js` is loaded with `defer`, so it runs after the inline script.
  - `Chart` (Chart.js from the CDN) and `lucide`
- Produces:
  - Globals: `btOnShow()`, called by `switchView`
  - Pure renderers the tests call: `btSourceOptionsHtml`, `btParamGroupsHtml`, `btLockedHtml`, `btJobRowsHtml`, `btDetailHtml`, `btCompareHtml`, `btParamDiff`, `btCompareWarnings`, `btBestIndex`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backtest_ui.py`:

```python
"""Backtest page: the dashboard wiring and the renderers in static/js/backtest.js.

Strings the renderers draw come from a bot's run_command (names, symbols), the cBot metadata (group
and parameter labels), the user (notes, parameter values) and a container's log (errors). They are all
drawn with innerHTML, so each one must pass through the dashboard's escapeHtml."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.server import app  # noqa: E402

client = TestClient(app)
JS = ROOT / "static" / "js" / "backtest.js"
DASHBOARD = ROOT / "templates" / "dashboard.html"
NODE = shutil.which("node")
HOSTILE = "evil<img src=x onerror=alert(1)>\"'"


def _function(src: str, name: str) -> str:
    """Source of `function name(...) {...}`, matched on braces (same as tests/test_dashboard_xss.py)."""
    start = src.index(f"function {name}(")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


def test_dashboard_has_the_backtest_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-backtest"' in html and 'id="view-backtest"' in html
    assert '<script src="/static/js/backtest.js' in html and " defer></script>" in html
    for element_id in ("bt-form-panel", "bt-bot", "bt-start", "bt-end", "bt-data-mode", "bt-spread-wrap",
                       "bt-spread", "bt-balance", "bt-note", "bt-params", "bt-locked", "bt-run-btn", "bt-form-msg",
                       "bt-compare-btn", "bt-jobs-tbody", "bt-detail-panel", "bt-detail", "bt-compare-panel",
                       "bt-compare", "bt-compare-close"):
        assert f'id="{element_id}"' in html, element_id
    assert "Technical logic only" in html


def test_switch_view_opens_the_backtest_page():
    html = client.get("/demo/dashboard").text
    assert "targetId === 'view-backtest'" in html and "btOnShow();" in html


def test_backtest_js_is_served_and_uses_the_api():
    resp = client.get("/static/js/backtest.js")
    assert resp.status_code == 200 and "function btOnShow" in resp.text
    for route in ("/api/backtests/sources", "/params", "/api/backtests", "/cancel", "/report.json"):
        assert route in resp.text, route


def test_best_value_rules():
    src = JS.read_text(encoding="utf-8")
    assert "['max_equity_dd_pct', 'Max equity DD %', 'min', 'pct']" in src
    assert "['avg_loss', 'Avg loss', 'zero', 'money']" in src


HARNESS = r"""
%(escape)s
%(js)s
const H = %(hostile)s;
const out = {};
out.sources = btSourceOptionsHtml([{name: H, supported: false, reason: H}, {name: H, supported: true, reason: ''}]);
const view = {timeframes: ['Hour', H], groups: [{name: H, params: [
    {key: H, label: H, type: 'String', bot_value: H, default: H},
    {key: 'SlMode', label: H, type: 'Enum', bot_value: H, enum_values: [H, 'ATR_Multiplier']},
    {key: 'FastRsiPeriod', label: 'Fast', type: 'Integer', bot_value: H, min: H, max: 50},
    {key: 'MacroTimeFrame', label: 'TF', type: 'TimeFrame', bot_value: 'Hour'},
    {key: 'ShowLogs', label: 'Logs', type: 'Boolean', bot_value: 'true'}]}]};
const overrides = {FastRsiPeriod: H};
overrides[H] = H;
out.params = btParamGroupsHtml(view, overrides, new Set([H]));
out.locked = btLockedHtml({[H]: H});
const job = {id: 3, bot_name: H, symbol: H, period: H, start_date: H, end_date: H, data_mode: H, note: H,
    status: 'done', overrides: {[H]: {from: H, to: H}}, algo_build_time: H,
    summary: {net_profit: H, profit_factor: 1.2, win_rate: 50, max_equity_dd_pct: 4, total_trades: 10,
              starting_capital: 10000},
    report: {trades: [{entry_time: H, close_time: H, direction: H, lots: H, entry_price: H, close_price: H,
                       pips: H, net: H, commissions: 0, swaps: 0}],
             parameters: {[H]: H, BotId: 'bt-3'}, equity: [], pnl_by_hour: [], pnl_by_weekday: []}};
out.rows = btJobRowsHtml([job, {...job, id: 4, status: 'failed', error: H},
                          {...job, id: 5, status: 'running', phase: H, progress: 42}], new Set([3]));
out.detail = btDetailHtml(job);
out.failed = btDetailHtml({...job, status: 'failed', error: H});
const other = {...job, id: 6, start_date: '2026-01-01',
               report: {...job.report, parameters: {[H]: 'other', BotId: 'bt-6'}}};
out.compare = btCompareHtml([job, other]);
out.diff = btParamDiff([job, other]);
out.warnings = btCompareWarnings([job, other]);
out.best = [btBestIndex([1, 3, 2], 'max'), btBestIndex([1, 3, 2], 'min'), btBestIndex([-5, -1, 2], 'zero'),
            btBestIndex([2, 2], 'max'), btBestIndex([1, 2], null)];
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_backtest_renderers_escape_external_strings():
    dashboard = DASHBOARD.read_text(encoding="utf-8")
    inline = dashboard[dashboard.rindex("<script>") + len("<script>"):dashboard.rindex("</script>")]
    src = HARNESS % {"escape": _function(inline, "escapeHtml"), "js": JS.read_text(encoding="utf-8"),
                     "hostile": json.dumps(HOSTILE)}
    result = subprocess.run([NODE, "-e", src], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    for name in ("sources", "params", "locked", "rows", "detail", "failed", "compare"):
        assert "<img" not in out[name], name
        assert "evil&lt;img" in out[name], name
    assert out["diff"] == [HOSTILE]                               # BotId is ignored
    assert out["warnings"] == ["date ranges differ"]
    assert out["best"] == [1, 0, 1, -1, -1]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_backtest_ui.py -q -p no:cacheprovider`
Expected: FAIL. The dashboard has no `view-backtest`, and `static/js/backtest.js` does not exist.

- [ ] **Step 3: Create `static/js/backtest.js`**

```javascript
/* Backtest page (docs/superpowers/specs/2026-09-24-backtest-page-design.md).
 *
 * Loaded with `defer`, after the dashboard's inline script whose escapeHtml it uses. The bt*Html
 * functions are pure (data in, HTML out) so tests/test_backtest_ui.py can render them in node with
 * hostile strings; everything that touches the DOM, fetch or Chart.js lives below them. */

const BT_POLL_MS = 3000;
const BT_WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
// [summary key, label, which value is best: 'max' | 'min' | 'zero' (closest to 0) | null, format]
const BT_COMPARE_ROWS = [
    ['net_profit', 'Net P&amp;L', 'max', 'money'],
    ['roi_pct', 'ROI %', 'max', 'num'],
    ['profit_factor', 'Profit factor', 'max', 'num'],
    ['win_rate', 'Win rate %', 'max', 'num'],
    ['total_trades', 'Trades', null, 'int'],
    ['avg_trade', 'Avg trade', 'max', 'money'],
    ['avg_win', 'Avg win', 'max', 'money'],
    ['avg_loss', 'Avg loss', 'zero', 'money'],
    ['largest_loss', 'Largest loss', 'zero', 'money'],
    ['max_equity_dd_pct', 'Max equity DD %', 'min', 'pct'],
    ['commissions', 'Commissions', 'zero', 'money'],
    ['swaps', 'Swaps', 'zero', 'money'],
];
const BT_IGNORED_PARAMS = new Set(['BotId', 'AccountLabel']);
const bt = {sources: [], view: null, overrides: {}, pendingOverrides: null, jobs: [], selected: new Set(),
            pollTimer: null, charts: {}, loaded: false};

// ---------- formatting ----------

function btNum(v, digits = 2) {
    const n = Number(v);
    return v !== null && v !== '' && Number.isFinite(n) ? n.toFixed(digits) : '—';
}

function btMoney(v) {
    const n = Number(v);
    if (v === null || v === '' || !Number.isFinite(n)) return '—';
    return `${n < 0 ? '−' : n > 0 ? '+' : ''}$${Math.abs(n).toFixed(2)}`;
}

function btFormat(v, kind) {
    if (kind === 'money') return btMoney(v);
    if (kind === 'int') return btNum(v, 0);
    return btNum(v);
}

function btSignClass(v) {
    const n = Number(v);
    return n > 0 ? 'kpi-value--profit' : n < 0 ? 'kpi-value--loss' : '';
}

function btDateText(iso) {
    const [y, m, d] = String(iso || '').split('-');
    return d ? `${d}/${m}/${y}` : String(iso || '');
}

// ---------- pure renderers ----------

function btSourceOptionsHtml(sources) {
    if (!sources.length) return '<option value="">No installed bots</option>';
    return sources.map(s => {
        const label = s.supported ? s.name : `${s.name} — ${s.reason}`;
        return `<option value="${escapeHtml(s.name)}"${s.supported ? '' : ' disabled'} title="${escapeHtml(s.reason || '')}">${escapeHtml(label)}</option>`;
    }).join('');
}

function btParamInputHtml(p, value, timeframes) {
    const key = escapeHtml(p.key);
    const current = value === null || value === undefined ? '' : String(value);
    const options = list => list.map(o =>
        `<option value="${escapeHtml(o)}"${String(o) === current ? ' selected' : ''}>${escapeHtml(o)}</option>`).join('');
    if (p.type === 'Boolean') return `<select class="log-select bt-param" data-key="${key}">${options(['true', 'false'])}</select>`;
    if (p.type === 'Enum') return `<select class="log-select bt-param" data-key="${key}">${options(p.enum_values || [])}</select>`;
    if (p.type === 'TimeFrame') return `<select class="log-select bt-param" data-key="${key}">${options(timeframes || [])}</select>`;
    if (p.type === 'Integer' || p.type === 'Double') {
        const bounds = (p.min !== null && p.min !== undefined ? ` min="${escapeHtml(p.min)}"` : '')
            + (p.max !== null && p.max !== undefined ? ` max="${escapeHtml(p.max)}"` : '');
        return `<input type="number" class="log-input bt-param" data-key="${key}" step="${p.type === 'Integer' ? '1' : 'any'}"${bounds} value="${escapeHtml(current)}">`;
    }
    return `<input type="text" class="log-input bt-param" data-key="${key}" maxlength="200" value="${escapeHtml(current)}">`;
}

function btParamGroupsHtml(view, overrides, openGroups) {
    const has = key => Object.prototype.hasOwnProperty.call(overrides, key);
    return (view.groups || []).map(g => {
        const changed = g.params.filter(p => has(p.key)).length;
        const rows = g.params.map(p => {
            const isChanged = has(p.key);
            const hint = isChanged
                ? `<span class="bt-param-hint">bot: ${escapeHtml(p.bot_value ?? '—')}</span><button type="button" class="bt-reset" data-key="${escapeHtml(p.key)}" title="Back to the bot's value">↺</button>`
                : '';
            return `<div class="bt-param-row${isChanged ? ' bt-param-row--changed' : ''}" title="${escapeHtml(p.key)}">`
                + `<span class="bt-param-label">${escapeHtml(p.label)}</span>`
                + `${btParamInputHtml(p, isChanged ? overrides[p.key] : p.bot_value, view.timeframes)}${hint}</div>`;
        }).join('');
        const open = changed || (openGroups && openGroups.has(g.name)) ? ' open' : '';
        const count = changed ? ` <span class="bt-changed-count">(${changed} changed)</span>` : '';
        return `<details class="bt-group" data-group="${escapeHtml(g.name)}"${open}><summary>${escapeHtml(g.name)}${count}</summary><div class="bt-param-grid">${rows}</div></details>`;
    }).join('');
}

function btLockedHtml(locked) {
    const items = Object.entries(locked || {}).map(([k, v]) => `${escapeHtml(k)}=${escapeHtml(v)}`).join(' · ');
    return `🔒 Locked for backtests: ${items}`;
}

function btChipsHtml(overrides) {
    const entries = Object.entries(overrides || {});
    if (!entries.length) return '<span class="td-dim">(bot)</span>';
    return entries.map(([k, c]) =>
        `<span class="bt-chip">${escapeHtml(k)} ${escapeHtml((c && c.from) ?? '—')}→${escapeHtml(c && c.to)}</span>`).join(' ');
}

function btStatusHtml(job) {
    if (job.status === 'running') {
        const pct = Math.max(0, Math.min(100, Number(job.progress) || 0));
        return `<span class="bt-status bt-status--running">${escapeHtml(job.phase || 'running')} ${pct.toFixed(0)}%</span>`
            + `<div class="bt-progress"><div style="width:${pct}%"></div></div>`;
    }
    const title = job.status === 'failed' && job.error ? ` title="${escapeHtml(job.error)}"` : '';
    return `<span class="bt-status bt-status--${escapeHtml(job.status)}"${title}>${escapeHtml(job.status)}</span>`;
}

function btJobRowsHtml(jobs, selected) {
    if (!jobs.length) return '<tr><td colspan="13" class="td-dim" style="text-align:center;">No backtests yet</td></tr>';
    return jobs.map(j => {
        const id = Number(j.id);
        const s = j.summary || {};
        const done = j.status === 'done';
        const active = j.status === 'queued' || j.status === 'running';
        const cell = (v, kind) => (done ? btFormat(v, kind) : '—');
        const lastButton = active
            ? `<button class="log-btn bt-act" data-act="cancel" data-id="${id}">Cancel</button>`
            : `<button class="log-btn bt-act" data-act="delete" data-id="${id}">Delete</button>`;
        return `<tr>
            <td><input type="checkbox" class="bt-select" data-id="${id}"${done ? '' : ' disabled'}${selected.has(id) ? ' checked' : ''}></td>
            <td>#${id}</td>
            <td>${escapeHtml(j.symbol)} <span class="td-dim">${escapeHtml(j.period)}</span><div class="td-dim bt-small">${escapeHtml(j.bot_name)}</div></td>
            <td>${escapeHtml(btDateText(j.start_date))} – ${escapeHtml(btDateText(j.end_date))}<div class="td-dim bt-small">${escapeHtml(j.data_mode)}</div></td>
            <td>${btChipsHtml(j.overrides)}</td>
            <td>${btStatusHtml(j)}</td>
            <td class="${done ? btSignClass(s.net_profit) : ''}">${cell(s.net_profit, 'money')}</td>
            <td>${cell(s.profit_factor, 'num')}</td>
            <td>${cell(s.win_rate, 'num')}</td>
            <td>${cell(s.max_equity_dd_pct, 'num')}</td>
            <td>${cell(s.total_trades, 'int')}</td>
            <td class="bt-note">${escapeHtml(j.note || '')}</td>
            <td><div class="bt-actions">
                <button class="log-btn bt-act" data-act="view" data-id="${id}"${done || j.status === 'failed' ? '' : ' disabled'}>View</button>
                <button class="log-btn bt-act" data-act="clone" data-id="${id}">Clone</button>
                ${lastButton}
            </div></td>
        </tr>`;
    }).join('');
}

function btKpiCardsHtml(s) {
    const card = (label, value, cls = '') =>
        `<div class="kpi-card"><div class="kpi-label">${label}</div><div class="kpi-value kpi-value--mono ${cls}">${value}</div></div>`;
    return `<div class="kpi-grid">${[
        card('Net P&amp;L', btMoney(s.net_profit), btSignClass(s.net_profit)),
        card('ROI', `${btNum(s.roi_pct)}%`, btSignClass(s.roi_pct)),
        card('Profit factor', btNum(s.profit_factor)),
        card('Win rate', `${btNum(s.win_rate, 1)}%`),
        card('Trades', btFormat(s.total_trades, 'int')),
        card('Max equity DD', `${btNum(s.max_equity_dd_pct)}%`),
        card('Avg win / loss', `${btMoney(s.avg_win)} / ${btMoney(s.avg_loss)}`),
        card('Commission + swap', btMoney(Number(s.commissions) + Number(s.swaps))),
    ].join('')}</div>`;
}

function btTradeRowsHtml(trades) {
    if (!trades.length) return '<tr><td colspan="9" class="td-dim" style="text-align:center;">No trades</td></tr>';
    return trades.map(t => `<tr>
        <td>${escapeHtml(t.entry_time)}</td><td>${escapeHtml(t.close_time)}</td><td>${escapeHtml(t.direction)}</td>
        <td>${btNum(t.lots)}</td><td>${escapeHtml(t.entry_price)}</td><td>${escapeHtml(t.close_price)}</td>
        <td>${btNum(t.pips, 1)}</td><td class="${btSignClass(t.net)}">${btMoney(t.net)}</td>
        <td>${btMoney(Number(t.commissions) + Number(t.swaps))}</td></tr>`).join('');
}

function btDetailHtml(job) {
    const id = Number(job.id);
    const head = `<div class="bt-detail-head"><strong>#${id} ${escapeHtml(job.symbol)} ${escapeHtml(job.period)}</strong>
        <span class="td-dim">${escapeHtml(btDateText(job.start_date))} – ${escapeHtml(btDateText(job.end_date))} · ${escapeHtml(job.data_mode)} · ${escapeHtml(job.bot_name)}</span>
        <button class="log-btn" data-act="close-detail">Close</button></div>`;
    if (job.status === 'failed') return `${head}<pre class="bt-error">${escapeHtml(job.error || 'failed')}</pre>`;
    if (!job.report) return `${head}<div class="td-dim">No report for this run.</div>`;
    return `${head}${btKpiCardsHtml(job.summary || {})}
        <div class="bt-charts">
            <div class="bt-chart bt-chart--wide"><canvas id="bt-equity-chart"></canvas></div>
            <div class="bt-chart"><canvas id="bt-hour-chart"></canvas></div>
            <div class="bt-chart"><canvas id="bt-weekday-chart"></canvas></div>
        </div>
        <div class="bt-detail-meta">Changed: ${btChipsHtml(job.overrides)} · <a href="/api/backtests/${id}/report.json" target="_blank" rel="noopener">report.json</a></div>
        <div class="table-wrap bt-trades"><table class="data-table">
            <thead><tr><th>Entry (UTC)</th><th>Exit (UTC)</th><th>Side</th><th>Lots</th><th>Entry</th><th>Exit</th><th>Pips</th><th>Net</th><th>Comm + swap</th></tr></thead>
            <tbody>${btTradeRowsHtml(job.report.trades || [])}</tbody>
        </table></div>`;
}

function btReportParams(job) {
    return (job.report && job.report.parameters) || {};
}

function btParamDiff(jobs) {
    const keys = new Set();
    jobs.forEach(j => Object.keys(btReportParams(j)).forEach(k => keys.add(k)));
    return [...keys]
        .filter(k => !BT_IGNORED_PARAMS.has(k))
        .filter(k => new Set(jobs.map(j => String(btReportParams(j)[k]))).size > 1)
        .sort();
}

function btCompareWarnings(jobs) {
    const differs = f => new Set(jobs.map(f)).size > 1;
    const warnings = [];
    if (differs(j => `${j.start_date}|${j.end_date}`)) warnings.push('date ranges differ');
    if (differs(j => j.data_mode)) warnings.push('data modes differ');
    if (differs(j => j.algo_build_time)) warnings.push('the .algo builds differ');
    if (differs(j => j.symbol)) warnings.push('symbols differ');
    return warnings;
}

function btBestIndex(values, best) {
    const nums = values.map(Number);
    if (!best || nums.some(n => !Number.isFinite(n))) return -1;
    const score = best === 'max' ? nums : best === 'min' ? nums.map(n => -n) : nums.map(n => -Math.abs(n));
    const top = Math.max(...score);
    return score.filter(s => s === top).length === 1 ? score.indexOf(top) : -1;
}

function btCompareHtml(jobs) {
    const head = jobs.map(j => `<th>#${Number(j.id)} ${escapeHtml(j.symbol)}<div class="td-dim bt-small">${escapeHtml(j.note || '')}</div></th>`).join('');
    const rows = BT_COMPARE_ROWS.map(([key, label, best, kind]) => {
        const values = jobs.map(j => (j.summary || {})[key]);
        const winner = btBestIndex(values, best);
        const cells = values.map((v, i) => {
            const base = Number(values[0]);
            const delta = i > 0 && Number.isFinite(Number(v)) && Number.isFinite(base)
                ? ` <span class="td-dim bt-small">Δ ${btFormat(Number(v) - base, kind)}</span>` : '';
            return `<td${i === winner ? ' class="bt-best"' : ''}>${btFormat(v, kind)}${delta}</td>`;
        }).join('');
        return `<tr><td>${label}</td>${cells}</tr>`;
    }).join('');
    const diff = btParamDiff(jobs);
    const diffRows = diff.length
        ? diff.map(k => `<tr><td>${escapeHtml(k)}</td>${jobs.map(j => `<td>${escapeHtml(btReportParams(j)[k] ?? '—')}</td>`).join('')}</tr>`).join('')
        : `<tr><td colspan="${jobs.length + 1}" class="td-dim">No parameter differs</td></tr>`;
    const warnings = btCompareWarnings(jobs);
    return `${warnings.length ? `<div class="bt-warning">⚠ Not directly comparable: ${warnings.join(', ')}</div>` : ''}
        <div class="bt-chart bt-chart--wide"><canvas id="bt-compare-chart"></canvas></div>
        <div class="table-wrap"><table class="data-table"><thead><tr><th>Metric</th>${head}</tr></thead><tbody>${rows}</tbody></table></div>
        <h4 class="bt-subtitle">Parameters that differ</h4>
        <div class="table-wrap"><table class="data-table"><thead><tr><th>Parameter</th>${head}</tr></thead><tbody>${diffRows}</tbody></table></div>`;
}

// ---------- DOM, fetch and charts ----------

async function btFetchJson(url, options) {
    const resp = await fetch(url, options);
    let body = null;
    try { body = await resp.json(); } catch (e) { body = null; }
    if (!resp.ok) {
        const detail = body && body.detail;
        const message = Array.isArray(detail)
            ? detail.map(d => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('; ')
            : (detail || `HTTP ${resp.status}`);
        throw new Error(message);
    }
    return body;
}

function btMessage(text, isError) {
    const el = document.getElementById('bt-form-msg');
    el.textContent = text || '';
    el.className = `bt-form-msg${isError ? ' bt-form-msg--error' : ''}`;
}

async function btOnShow() {
    if (!bt.loaded) {
        bt.loaded = true;
        btInitForm();
        await Promise.all([btLoadSources(), btRefreshJobs()]);
        return;
    }
    await btRefreshJobs();
}

function btInitForm() {
    const day = 86400000;
    const end = new Date(Date.now() - day);
    document.getElementById('bt-end').value = end.toISOString().slice(0, 10);
    document.getElementById('bt-start').value = new Date(end.getTime() - 59 * day).toISOString().slice(0, 10);
    document.getElementById('bt-bot').addEventListener('change', () => { bt.overrides = {}; btLoadParams(); });
    document.getElementById('bt-data-mode').addEventListener('change', btToggleSpread);
    document.getElementById('bt-run-btn').addEventListener('click', btSubmit);
    document.getElementById('bt-compare-btn').addEventListener('click', btCompare);
    document.getElementById('bt-compare-close').addEventListener('click', () => btHidePanel('bt-compare-panel'));
    const params = document.getElementById('bt-params');
    params.addEventListener('change', btOnParamChange);
    params.addEventListener('click', e => {
        const reset = e.target.closest('.bt-reset');
        if (!reset) return;
        e.preventDefault();
        delete bt.overrides[reset.dataset.key];
        btRenderParams();
    });
    const tbody = document.getElementById('bt-jobs-tbody');
    tbody.addEventListener('click', btOnJobAction);
    tbody.addEventListener('change', e => {
        if (!e.target.classList.contains('bt-select')) return;
        const id = Number(e.target.dataset.id);
        if (e.target.checked) bt.selected.add(id); else bt.selected.delete(id);
        btUpdateCompareButton();
    });
    document.getElementById('bt-detail').addEventListener('click', e => {
        if (e.target.closest('[data-act="close-detail"]')) btHidePanel('bt-detail-panel');
    });
    btToggleSpread();
}

function btToggleSpread() {
    const m1 = document.getElementById('bt-data-mode').value === 'm1';
    document.getElementById('bt-spread-wrap').style.display = m1 ? '' : 'none';
}

async function btLoadSources() {
    const select = document.getElementById('bt-bot');
    try {
        const data = await btFetchJson('/api/backtests/sources');
        bt.sources = data.sources || [];
        select.innerHTML = btSourceOptionsHtml(bt.sources);
        const first = bt.sources.find(s => s.supported);
        if (first) select.value = first.name;
        if (!data.docker_available) btMessage('Docker is not available on this server: backtests cannot run.', true);
        await btLoadParams();
    } catch (e) {
        btMessage(`Could not load bots: ${e.message}`, true);
    }
}

async function btLoadParams() {
    const bot = document.getElementById('bt-bot').value;
    const container = document.getElementById('bt-params');
    bt.view = null;
    document.getElementById('bt-locked').textContent = '';
    if (!bot) { container.innerHTML = ''; return; }
    container.innerHTML = '<div class="td-dim">Loading parameters… (the first time for a build takes ~15 s)</div>';
    try {
        const view = await btFetchJson(`/api/backtests/sources/${encodeURIComponent(bot)}/params`);
        if (document.getElementById('bt-bot').value !== bot) return;       // switched meanwhile
        bt.view = view;
        if (bt.pendingOverrides) { bt.overrides = bt.pendingOverrides; bt.pendingOverrides = null; }
        document.getElementById('bt-locked').innerHTML = btLockedHtml(view.locked);
        btRenderParams();
    } catch (e) {
        container.innerHTML = `<div class="bt-form-msg--error">${escapeHtml(e.message)}</div>`;
    }
}

function btRenderParams() {
    if (!bt.view) return;
    const container = document.getElementById('bt-params');
    const open = new Set([...container.querySelectorAll('details.bt-group[open]')].map(d => d.dataset.group));
    container.innerHTML = btParamGroupsHtml(bt.view, bt.overrides, open);
}

function btFindParam(key) {
    for (const g of (bt.view && bt.view.groups) || []) {
        const p = g.params.find(x => x.key === key);
        if (p) return p;
    }
    return null;
}

function btOnParamChange(e) {
    const input = e.target.closest('.bt-param');
    const p = input && btFindParam(input.dataset.key);
    if (!p) return;
    const numeric = p.type === 'Integer' || p.type === 'Double';
    const same = numeric ? Number(input.value) === Number(p.bot_value) : input.value === String(p.bot_value);
    if (same) delete bt.overrides[p.key]; else bt.overrides[p.key] = input.value;
    btRenderParams();
}

async function btSubmit() {
    const btn = document.getElementById('bt-run-btn');
    const mode = document.getElementById('bt-data-mode').value;
    const body = {
        bot_name: document.getElementById('bt-bot').value,
        start: document.getElementById('bt-start').value,
        end: document.getElementById('bt-end').value,
        data_mode: mode,
        balance: Number(document.getElementById('bt-balance').value),
        note: document.getElementById('bt-note').value.trim() || null,
        overrides: bt.overrides,
    };
    if (mode === 'm1') body.spread_pips = Number(document.getElementById('bt-spread').value);
    btn.disabled = true;
    btMessage('Queuing…');
    try {
        const res = await btFetchJson('/api/backtests', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
        btMessage(`Backtest #${res.id} queued (position ${res.queue_position}).`);
        await btRefreshJobs();
    } catch (e) {
        btMessage(e.message, true);
    } finally {
        btn.disabled = false;
    }
}

async function btRefreshJobs() {
    clearTimeout(bt.pollTimer);
    try {
        const data = await btFetchJson('/api/backtests');
        bt.jobs = data.jobs || [];
        const doneIds = new Set(bt.jobs.filter(j => j.status === 'done').map(j => Number(j.id)));
        bt.selected = new Set([...bt.selected].filter(id => doneIds.has(id)));
        document.getElementById('bt-jobs-tbody').innerHTML = btJobRowsHtml(bt.jobs, bt.selected);
        btUpdateCompareButton();
    } catch (e) {
        btMessage(`Could not load backtests: ${e.message}`, true);
    }
    // Poll only while something is queued or running and the page is on screen.
    const active = bt.jobs.some(j => j.status === 'queued' || j.status === 'running');
    const visible = document.getElementById('view-backtest').classList.contains('active');
    if (active && visible) bt.pollTimer = setTimeout(btRefreshJobs, BT_POLL_MS);
}

function btUpdateCompareButton() {
    const btn = document.getElementById('bt-compare-btn');
    btn.textContent = `Compare (${bt.selected.size})`;
    btn.disabled = bt.selected.size < 2 || bt.selected.size > 4;
}

function btShowPanel(id) {
    const panel = document.getElementById(id);
    panel.style.display = '';
    panel.scrollIntoView({behavior: 'smooth', block: 'start'});
}

function btHidePanel(id) {
    document.getElementById(id).style.display = 'none';
}

async function btOnJobAction(e) {
    const btn = e.target.closest('.bt-act');
    if (!btn) return;
    const id = Number(btn.dataset.id);
    try {
        if (btn.dataset.act === 'view') {
            await btShowDetail(id);
        } else if (btn.dataset.act === 'clone') {
            await btClone(id);
        } else if (btn.dataset.act === 'cancel') {
            btn.disabled = true;
            await btFetchJson(`/api/backtests/${id}/cancel`, {method: 'POST'});
            await btRefreshJobs();
        } else if (btn.dataset.act === 'delete') {
            if (!confirm(`Delete backtest #${id} and its report?`)) return;
            btn.disabled = true;
            await btFetchJson(`/api/backtests/${id}`, {method: 'DELETE'});
            bt.selected.delete(id);
            await btRefreshJobs();
        }
    } catch (err) {
        btMessage(err.message, true);
        btn.disabled = false;
    }
}

async function btShowDetail(id) {
    const job = await btFetchJson(`/api/backtests/${id}`);
    document.getElementById('bt-detail').innerHTML = btDetailHtml(job);
    btShowPanel('bt-detail-panel');
    if (job.report) btDrawDetailCharts(job.report);
}

async function btClone(id) {
    const job = bt.jobs.find(j => Number(j.id) === id) || await btFetchJson(`/api/backtests/${id}`);
    const select = document.getElementById('bt-bot');
    if (![...select.options].some(o => o.value === job.bot_name && !o.disabled)) {
        btMessage(`${job.bot_name} is no longer installed or supported; cannot clone #${id}.`, true);
        return;
    }
    select.value = job.bot_name;
    document.getElementById('bt-start').value = job.start_date;
    document.getElementById('bt-end').value = job.end_date;
    document.getElementById('bt-data-mode').value = job.data_mode;
    document.getElementById('bt-spread').value = job.spread_pips ?? '';
    document.getElementById('bt-balance').value = job.balance;
    document.getElementById('bt-note').value = `${job.note ? job.note + ' ' : ''}(clone of #${id})`.slice(0, 200);
    btToggleSpread();
    bt.pendingOverrides = Object.fromEntries(Object.entries(job.overrides || {}).map(([k, c]) => [k, c.to]));
    await btLoadParams();
    btMessage(`Form filled from #${id}: change a parameter and run.`);
    document.getElementById('bt-form-panel').scrollIntoView({behavior: 'smooth', block: 'start'});
}

async function btCompare() {
    const ids = [...bt.selected].sort((a, b) => a - b);        // the oldest run is the baseline column
    if (ids.length < 2) return;
    try {
        const jobs = await Promise.all(ids.map(id => btFetchJson(`/api/backtests/${id}`)));
        document.getElementById('bt-compare').innerHTML = btCompareHtml(jobs);
        btShowPanel('bt-compare-panel');
        btDrawCompareChart(jobs);
    } catch (e) {
        btMessage(`Compare failed: ${e.message}`, true);
    }
}

function btDestroyChart(name) {
    if (bt.charts[name]) { bt.charts[name].destroy(); delete bt.charts[name]; }
}

function btDrawDetailCharts(report) {
    if (typeof Chart === 'undefined') return;
    ['equity', 'hour', 'weekday'].forEach(btDestroyChart);
    const eq = report.equity || [];
    bt.charts.equity = new Chart(document.getElementById('bt-equity-chart'), {
        type: 'line',
        data: {
            labels: eq.map(p => new Date(p.t).toISOString().slice(0, 16).replace('T', ' ')),
            datasets: [
                {label: 'Balance', data: eq.map(p => p.balance), borderColor: '#7dbd1e', pointRadius: 0, borderWidth: 1.5},
                {label: 'Equity (low)', data: eq.map(p => p.equity), borderColor: '#4fc3f7', pointRadius: 0, borderWidth: 1},
            ],
        },
        options: {responsive: true, maintainAspectRatio: false, animation: false,
                  interaction: {mode: 'index', intersect: false}, scales: {x: {ticks: {maxTicksLimit: 8}}}},
    });
    const bars = (id, labels, buckets) => new Chart(document.getElementById(id), {
        type: 'bar',
        data: {labels, datasets: [{label: 'Net P&L', data: buckets.map(b => b.net),
                                   backgroundColor: buckets.map(b => (b.net < 0 ? '#e53935' : '#7dbd1e'))}]},
        options: {responsive: true, maintainAspectRatio: false, animation: false,
                  plugins: {tooltip: {callbacks: {afterLabel: c => `${buckets[c.dataIndex].count} trades`}}}},
    });
    bt.charts.hour = bars('bt-hour-chart', [...Array(24).keys()].map(h => `${h}h`), report.pnl_by_hour || []);
    bt.charts.weekday = bars('bt-weekday-chart', BT_WEEKDAYS, report.pnl_by_weekday || []);
}

function btDrawCompareChart(jobs) {
    if (typeof Chart === 'undefined') return;
    btDestroyChart('compare');
    const colors = ['#7dbd1e', '#4fc3f7', '#ffa726', '#ba68c8'];
    bt.charts.compare = new Chart(document.getElementById('bt-compare-chart'), {
        type: 'line',
        data: {datasets: jobs.map((j, i) => {
            const eq = (j.report && j.report.equity) || [];
            const base = Number(j.summary && j.summary.starting_capital) || (eq[0] && eq[0].balance) || 1;
            return {label: `#${j.id}`, data: eq.map(p => ({x: p.t, y: (p.balance / base - 1) * 100})),
                    borderColor: colors[i % colors.length], pointRadius: 0, borderWidth: 1.5};
        })},
        options: {responsive: true, maintainAspectRatio: false, animation: false, parsing: false,
                  scales: {x: {type: 'linear', ticks: {callback: v => new Date(v).toISOString().slice(0, 10)}},
                           y: {ticks: {callback: v => `${v}%`}}}},
    });
}
```

- [ ] **Step 4: Wire the page into `templates/dashboard.html`**

4a. In `<head>`, bump the CSS version and add the script after Chart.js. Replace:

```html
    <link rel="stylesheet" href="/static/css/dashboard.css?v=20260921_setup_installed">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

with:

```html
    <link rel="stylesheet" href="/static/css/dashboard.css?v=20260925_backtest">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="/static/js/backtest.js?v=20260925" defer></script>
```

4b. In the sidebar, add the nav item after Leaderboard. Replace:

```html
            <a href="#" class="nav-item" data-target="view-leaderboard" title="Leaderboard">
                <span class="nav-icon"><i data-lucide="trophy"></i></span>
                <span class="nav-label">Leaderboard</span>
            </a>
```

with:

```html
            <a href="#" class="nav-item" data-target="view-leaderboard" title="Leaderboard">
                <span class="nav-icon"><i data-lucide="trophy"></i></span>
                <span class="nav-label">Leaderboard</span>
            </a>
            <a href="#" class="nav-item" data-target="view-backtest" title="Backtest">
                <span class="nav-icon"><i data-lucide="flask-conical"></i></span>
                <span class="nav-label">Backtest</span>
            </a>
```

4c. Insert the view just before the Docker view. Replace:

```html
            <!-- Docker Bots View -->
            <div id="view-docker" class="view-section">
```

with:

```html
            <!-- Backtest View (static/js/backtest.js) -->
            <div id="view-backtest" class="view-section">
                <section class="panel" id="bt-form-panel">
                    <div class="panel-header">
                        <span class="panel-title"><i data-lucide="flask-conical" class="panel-icon text-blue"></i> New Backtest</span>
                    </div>
                    <div class="panel-body">
                        <div class="bt-form-grid">
                            <label class="bt-field bt-field--wide">Bot <select id="bt-bot" class="log-select"></select></label>
                            <label class="bt-field">From (UTC) <input id="bt-start" type="date" class="log-input"></label>
                            <label class="bt-field">To (UTC) <input id="bt-end" type="date" class="log-input"></label>
                            <label class="bt-field">Data
                                <select id="bt-data-mode" class="log-select">
                                    <option value="ticks" selected>ticks (real spread)</option>
                                    <option value="m1">m1 bars (fixed spread)</option>
                                </select>
                            </label>
                            <label class="bt-field" id="bt-spread-wrap" style="display:none;">Spread (pips) <input id="bt-spread" type="number" step="0.1" min="0.1" class="log-input"></label>
                            <label class="bt-field">Balance <input id="bt-balance" type="number" min="100" step="100" value="10000" class="log-input"></label>
                            <label class="bt-field bt-field--wide">Note <input id="bt-note" type="text" maxlength="200" class="log-input" placeholder="What does this run try?"></label>
                        </div>
                        <div id="bt-params" class="bt-params"></div>
                        <div id="bt-locked" class="bt-locked"></div>
                        <div class="bt-warning">⚠ Technical logic only: backtests run with the AI gate off, while the live bot lets the AI filter its entries.</div>
                        <div class="bt-form-actions">
                            <span id="bt-form-msg" class="bt-form-msg"></span>
                            <button id="bt-run-btn" class="log-btn bt-run-btn"><i data-lucide="play" class="btn-icon"></i> Run backtest</button>
                        </div>
                    </div>
                </section>
                <section class="panel">
                    <div class="panel-header">
                        <span class="panel-title"><i data-lucide="list" class="panel-icon text-blue"></i> Runs</span>
                        <button id="bt-compare-btn" class="log-btn" disabled>Compare (0)</button>
                    </div>
                    <div class="table-wrap">
                        <table class="data-table">
                            <thead><tr><th></th><th>#</th><th>Symbol</th><th>Range</th><th>Changes</th><th>Status</th><th>Net</th><th>PF</th><th>Win %</th><th>Max DD %</th><th>Trades</th><th>Note</th><th></th></tr></thead>
                            <tbody id="bt-jobs-tbody"></tbody>
                        </table>
                    </div>
                </section>
                <section class="panel" id="bt-detail-panel" style="display:none;">
                    <div class="panel-header">
                        <span class="panel-title"><i data-lucide="line-chart" class="panel-icon text-blue"></i> Run Detail</span>
                    </div>
                    <div class="panel-body" id="bt-detail"></div>
                </section>
                <section class="panel" id="bt-compare-panel" style="display:none;">
                    <div class="panel-header">
                        <span class="panel-title"><i data-lucide="columns" class="panel-icon text-blue"></i> Compare</span>
                        <button id="bt-compare-close" class="log-btn">Close</button>
                    </div>
                    <div class="panel-body" id="bt-compare"></div>
                </section>
            </div>

            <!-- Docker Bots View -->
            <div id="view-docker" class="view-section">
```

4d. In `switchView`, replace:

```javascript
                } else if (targetId === 'view-risk') {
                    fetchRiskLimits();
                }
```

with:

```javascript
                } else if (targetId === 'view-risk') {
                    fetchRiskLimits();
                } else if (targetId === 'view-backtest') {
                    btOnShow();
                }
```

- [ ] **Step 5: Add the styles**

Append to the end of `static/css/dashboard.css`:

```css
/* --- Backtest page (static/js/backtest.js) --- */
.bt-form-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px 12px;margin-bottom:12px}
.bt-field{display:flex;flex-direction:column;gap:4px;font-size:0.72rem;color:var(--text-muted)}
.bt-field--wide{grid-column:span 2}
.bt-params{display:flex;flex-direction:column;gap:6px;margin-bottom:10px}
.bt-group{border:1px solid var(--border);border-radius:6px;background:var(--bg-surface)}
.bt-group summary{cursor:pointer;padding:8px 12px;font-size:0.75rem;font-weight:600;color:var(--accent-bright)}
.bt-changed-count{color:#ffa726;font-weight:500}
.bt-param-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:6px 14px;padding:4px 12px 12px}
.bt-param-row{display:flex;align-items:center;gap:6px;font-size:0.72rem;color:var(--text-muted)}
.bt-param-label{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bt-param-row .bt-param{width:120px}
.bt-param-row--changed .bt-param{border-color:#ffa726;color:#ffa726}
.bt-param-hint{font-size:0.65rem;color:var(--text-dim);white-space:nowrap}
.bt-reset{background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:0.8rem;padding:0 2px}
.bt-locked{font-size:0.7rem;color:var(--text-dim);margin-bottom:8px;word-break:break-word}
.bt-warning{font-size:0.72rem;color:#ffa726;background:rgba(255,167,38,0.08);border:1px solid rgba(255,167,38,0.3);border-radius:6px;padding:6px 10px;margin-bottom:10px}
.bt-form-actions{display:flex;align-items:center;justify-content:flex-end;gap:12px;flex-wrap:wrap}
.bt-form-msg{font-size:0.75rem;color:var(--text-muted)}
.bt-form-msg--error{color:var(--loss)}
.bt-run-btn{background:var(--accent-soft);color:var(--accent-bright);border-color:var(--accent)}
.bt-chip{display:inline-block;font-size:0.65rem;padding:1px 6px;margin:1px 0;border-radius:10px;border:1px solid var(--border);background:var(--bg-surface);white-space:nowrap}
.bt-small{font-size:0.65rem}
.bt-note{max-width:180px;overflow:hidden;text-overflow:ellipsis}
.bt-actions{display:flex;gap:4px}
.bt-status{font-size:0.68rem;font-weight:600;text-transform:uppercase}
.bt-status--done{color:var(--profit)}
.bt-status--failed{color:var(--loss);cursor:help}
.bt-status--running{color:#4fc3f7}
.bt-status--queued,.bt-status--cancelled{color:var(--text-dim)}
.bt-progress{height:4px;width:110px;background:var(--bg-surface);border-radius:2px;margin-top:3px;overflow:hidden}
.bt-progress div{height:100%;background:#4fc3f7}
.bt-detail-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.bt-detail-head .log-btn{margin-left:auto}
.bt-charts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.bt-chart{position:relative;height:220px}
.bt-chart--wide{grid-column:1 / -1;height:260px}
.bt-detail-meta{font-size:0.72rem;color:var(--text-muted);margin-bottom:10px}
.bt-detail-meta a{color:var(--accent-bright)}
.bt-trades{max-height:420px;overflow:auto}
.bt-error{white-space:pre-wrap;font-size:0.72rem;color:var(--loss);background:var(--bg-surface);padding:10px;border-radius:6px;max-height:320px;overflow:auto}
.bt-best{font-weight:700;color:var(--accent-bright)}
.bt-subtitle{margin:14px 0 6px;font-size:0.75rem;color:var(--accent-bright)}
@media (max-width:640px){.bt-field--wide{grid-column:auto}.bt-charts{grid-template-columns:1fr}.bt-param-grid{grid-template-columns:1fr}}
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_backtest_ui.py tests/test_dashboard_xss.py tests/test_dashboard_ui.py -q -p no:cacheprovider`
Expected: all pass. The node test only runs where `node` is installed; the Mac has `/opt/homebrew/bin/node`.

- [ ] **Step 7: Checkpoint**

Run the full suite. It must stay green. Do not commit.

---

### Task 8: Verification, handover, then deploy and acceptance when the user approves

**Files:**
- Modify: `docs/superpowers/specs/2026-09-24-backtest-page-design.md`, only if the build differs from the spec

- [ ] **Step 1: Run the full local suite**

Run: `.venv/bin/python -m pytest -q -p no:cacheprovider`
Expected: 726 + the new tests, all passing, and nothing skipped that ran before.

- [ ] **Step 2: Report and stop**

Tell the user:
- which files changed (the 6 new app modules, `portfolio.py`, `server.py`, the template, the CSS, `backtest.js`, 7 test modules and 2 fixtures)
- the test count

Then wait. The steps below need the user's go-ahead: commit and push, then a VPS deploy.

- [ ] **Step 3: Deploy on the VPS (only after the user approves)**

Do it as `forge@204.168.144.232`, one step at a time. Never use `scripts/deploy_feature.sh`.

1. `cd /home/forge/AgentFxTrading && git pull`.
2. Check that `CTRADER_HOME` points at `/home/forge/ctrader`. The sources endpoint needs it to find the password files. Run `grep -c '^CTRADER_HOME=/home/forge/ctrader' .env`; the expected result is `1`.
3. Run the tests the way the memory note "VPS deploy steps" describes. pytest is not in the prod venv, so install it into a temp target, and back up then restore `webui_data/trade_mode.json` and `data/ff_calendar_thisweek.json` around the run. Expected: all pass. The node-based tests are skipped on the VPS.
4. Restart the service away from the M15 closes (hh:00/15/30/45) with `sudo -n systemctl restart agentfx.service`.
5. Check the service: `systemctl status agentfx.service`, `curl -s http://127.0.0.1:8000/api/watchdog/status`, and `sudo -n journalctl -u agentfx --since "-2 min" | grep -i "Backtest worker started"`.

No cBot needs a rebuild or restart.

- [ ] **Step 4: Acceptance on the VPS**

1. **Baseline by hand.** Run the spike's command once for the current `FlowRsiBot.algo` build, then record `TotalTrades` and `NetProfit` from the log. The parameters are the live container's, as `docker inspect cbot-demo-demo-eurusd-all-flowrsi` shows them. The locked values match what the page sends.

   ```bash
   docker run --rm --name bt-manual --memory=1g --cpus=2 --cpu-shares=256 \
     -v /home/forge/AgentFxTrading/cBot/FlowRsiBot.algo:/algo/FlowRsiBot.algo:ro \
     -v /home/forge/ctrader/ctrader_data/ctid_demo-demo_pwd:/secrets/pwd:ro \
     -v agentfx-bt-cache:/bt-cache \
     ghcr.io/spotware/ctrader-console:latest backtest /algo/FlowRsiBot.algo \
     --ctid=hoangvnbkhn@gmail.com --pwd-file=/secrets/pwd --account=10115236 \
     --symbol=EURUSD --period=m15 --start=24/07/2026 --end=23/09/2026 --data-mode=ticks \
     --data-dir=/bt-cache --balance=10000 --commission-auto --report-json=/tmp/report.json \
     --full-access --exit-on-stop \
     --FastRsiPeriod=7 --SlowRsiPeriod=14 --EnableSmcFilter=true --EnableFvgDetection=true \
     --EnablePremiumDiscountFilter=true --RiskPercentage=0.5 --MaxRiskPerTradeMoney=50.0 --TargetRiskReward=1.5 \
     --BotId=bt-manual --AccountLabel=backtest --UseAiGateMode=false \
     --ApiUrl=http://127.0.0.1:9/disabled --AiTelemetryUrl=http://127.0.0.1:9/disabled \
     --AiReportUrl=http://127.0.0.1:9/disabled --CommandPollMs=0 --EnableNewsFilter=false \
     --EnableTelegramAlerts=false --SendChartScreenshot=false --SendAiAdjustAlerts=false \
     2>&1 | grep -E '"(TotalTrades|NetProfit)"'
   ```
2. **The same run through the page.** On `agentfx.hoangbk.com` → Backtest, pick `cbot-demo-demo-eurusd-all-flowrsi`, set 24/07/2026–23/09/2026, `ticks`, balance 10000, and change nothing. Run it. Trades and net profit must match step 1 exactly.
3. **Clone and compare.** Clone that run, change `TargetRiskReward` to `2.0`, and run it. Tick both runs and press Compare. The "Parameters that differ" table must list exactly `TargetRiskReward`.
4. **Live bots unaffected.** While step 2 runs:
   - no live container logs a cTrader reconnect (read LogPath with sudo, as the memory note "docker logs NUL truncation" describes);
   - `sudo -n journalctl -u agentfx | grep -c "bt-"` shows no request from a `bt-*` bot id.
5. **Cancel.** Queue a run, cancel it while it is running, and confirm that `docker ps -a --filter label=agentfx.backtest` is empty within ~5 s.
6. Remove the spike's leftovers: `rm -rf /home/forge/backtest_tmp`.

Report each result to the user.
