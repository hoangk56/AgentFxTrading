# Docker Instance Setup Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A "Setup Instances" panel in the dashboard's Docker view where the user picks (or creates) a cTrader account, ticks symbol × strategy cells from the README-tuned presets, and clicks once to save the generated `docker run` commands as `cbot_configs` rows and start the containers.

**Architecture:** Three small backend units — `app/cbot_presets.py` (pure data + command builder, no I/O), `app/ctrader_accounts.py` (validation, slug, password file on disk, orchestration over the registry), and new methods on `AccountRegistry` (`ctrader_accounts` table CRUD) — wired by five routes in `app/dashboard.py` next to the existing `/api/bots` routes. The UI is one hidden panel plus a JS block in `templates/dashboard.html`, reusing the existing classes. The cTID password is accepted in a POST body, written to `$CTRADER_HOME/ctrader_data/ctid_<slug>_pwd` (0600), and never stored, logged or returned.

**Tech Stack:** FastAPI + pydantic v2 (existing), SQLite/PostgreSQL through `app/db.py`'s `_adapt_query_for_pg`, vanilla JS in the Jinja template, pytest with `fastapi.testclient.TestClient` (test DB isolated via `AGENTFX_TEST_DB`, see `tests/conftest.py`).

**Spec:** `docs/superpowers/specs/2026-09-18-docker-instance-setup-design.md`

## Global Constraints

- Table `ctrader_accounts` is created in `AccountRegistry._init_schema` (`app/accounts.py`); DDL uses `INTEGER PRIMARY KEY AUTOINCREMENT` (adapted to `SERIAL PRIMARY KEY` for PostgreSQL by `_adapt_query_for_pg`). Columns exactly: `id, slug, ctid_email, account_number, account_type, label, pwd_file, created_at`.
- Slug: `<account_type>-<slugified label>`, lowercase `[a-z0-9-]`, max **24** chars (e.g. `demo-main`, `live-ic`). `pwd_file` column stores the **in-container** path `/root/ctrader_data/ctid_<slug>_pwd`.
- Password file host path: `$CTRADER_HOME/ctrader_data/ctid_<slug>_pwd`, mode `0600`, parent created `0700` if missing. `CTRADER_HOME` read from the environment (`.env` is loaded by `app/server.py` with `override=True`), default `/root`. Content is exactly the password (no trailing newline).
- The password is never logged, never stored in the DB, never returned by any endpoint. `GET /api/ctrader-accounts` returns neither `pwd_file` nor the password.
- Creating an account also upserts `accounts` with `account_id=<type>-<number>`, `label`, `is_configured=1`.
- Presets: exactly the 22 cells of the spec matrix (15 symbols); `params` holds only the strategy-tuned flags copied verbatim from the README `docker run` block for that symbol; the builder emits infrastructure flags. `--period` in the README block is the source of truth (USTEC `m5`, DE40 `m15`).
- Container name: `cbot-<slug>-<symbol lower><suffix>` (suffixes `""`, `-judas`, `-flowrsi`). Commands are a single line (no backslash continuations) and must survive `shlex.split`.
- Account endpoints: `422` validation, `409` duplicate slug, `404` not found, `500` password file write failure — body `{"success": false, "message": "..."}`. `POST /api/setup/instances` reports per-selection status (`started` | `saved` | `exists` | `error`) with HTTP 200; the only non-200 is `404` when `account_id` does not exist (request-level, not per-selection — a deliberate, documented deviation from the spec's "always 200").
- Account validation: email contains `@` (and no whitespace/`"`); account number digits only; label 1–40 chars, no `"` / newline, at least one letter or digit; password non-empty; **demo** labels whose slug would contain `live` are rejected (the `/api/bots` live-detection matches `-live`/`live-` in container names).
- UI lives in `templates/dashboard.html` inside `#view-docker`, same visual style as `#bot-form-container`; reuse `log-input`, `log-select`, `log-btn`, `data-table`, `bot-form-grid`, `td-dim`. No new CSS file. The existing refresh function is `fetchBots()` (the spec calls it `loadBots()`).
- Local test command: `.venv/bin/pytest -q` (baseline before this plan: **138 passed**). Never touch `portfolio.db` or port 8000 locally — port 8000 on this Mac is an SSH tunnel to the user's VPS.
- Commit messages end with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

## File Structure

| File | Responsibility |
|---|---|
| `app/cbot_presets.py` (new) | `STRATEGIES`, `SYMBOLS`, `PRESETS` (22 cells), `container_name`, `describe_cell`, `build_run_command`, `presets_payload`. Pure; no DB, no env. |
| `app/accounts.py` (modify) | `ctrader_accounts` DDL in `_init_schema`; `upsert_configured_account` (extracted from `seed_from_env`); `list_ctrader_accounts`, `get_ctrader_account`, `get_ctrader_account_by_slug`, `insert_ctrader_account`, `delete_ctrader_account`. |
| `app/ctrader_accounts.py` (new) | `slugify`, `validate_account_input`, `ctrader_home`, `password_file_paths`, `write_password_file`, `public_view`, `create_ctrader_account`, `delete_ctrader_account`, `list_ctrader_accounts`; exceptions `AccountValidationError`, `DuplicateSlugError`. |
| `app/dashboard.py` (modify) | Routes: `GET/POST /api/ctrader-accounts`, `DELETE /api/ctrader-accounts/{id}`, `GET /api/setup/presets`, `POST /api/setup/instances`. |
| `templates/dashboard.html` (modify) | "Setup Instances" button, `#setup-panel`, JS block. |
| `README.md` (modify) | One tip pointing at the new screen. |
| `tests/test_cbot_presets.py` (new) | Matrix, golden commands, naming, `shlex` survival. |
| `tests/test_ctrader_accounts.py` (new) | Registry CRUD (tmp SQLite) + account API (row, file, mode, 409/422/404/500). |
| `tests/test_setup_instances.py` (new) | Presets endpoint + instance creation with `docker_manager` monkeypatched. |
| `tests/test_dashboard_ui.py` (modify) | Panel/button present inside the Docker view. |

---

### Task 1: Presets module and command builder

**Files:**
- Create: `app/cbot_presets.py`
- Test: `tests/test_cbot_presets.py`

**Interfaces:**
- Consumes: nothing (pure module).
- Produces:
  - `STRATEGIES: Dict[str, Dict[str, str]]` keyed `tms_orb|judas|flowrsi` with `label`, `algo`, `suffix`.
  - `SYMBOLS: List[str]` (15, grid row order).
  - `PRESETS: Dict[Tuple[str, str], Dict]` keyed `(strategy, SYMBOL)` → `{"period": str, "session": str, "params": dict}`.
  - `container_name(slug: str, strategy: str, symbol: str) -> str`
  - `describe_cell(strategy: str, symbol: str, account_label: str) -> str` → `"<Strategy label> <SYMBOL> <period> — <account label>"`
  - `build_run_command(account: dict, strategy: str, symbol: str, project_root: str, ctrader_home: str, image: str = DEFAULT_IMAGE) -> str` — `account` needs keys `slug, ctid_email, account_number, label, pwd_file`.
  - `presets_payload() -> dict` → `{"strategies", "symbols", "cells": [{symbol, strategy, period, session}]}`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cbot_presets.py`:

```python
import shlex
import sys
from pathlib import Path

import pytest

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.cbot_presets import (
    DEFAULT_IMAGE, PRESETS, STRATEGIES, SYMBOLS,
    build_run_command, container_name, describe_cell, presets_payload,
)

ROOT = "/home/forge/AgentFxTrading"
HOME = "/home/forge/ctrader"
DEMO = {"id": 1, "slug": "demo-main", "ctid_email": "me@example.com", "account_number": "10101649",
        "account_type": "demo", "label": "Demo Main", "pwd_file": "/root/ctrader_data/ctid_demo-main_pwd"}
LIVE = {"id": 2, "slug": "live-ic", "ctid_email": "me@example.com", "account_number": "6094347",
        "account_type": "live", "label": "IC", "pwd_file": "/root/ctrader_data/ctid_live-ic_pwd"}

# The spec matrix: 15 symbols, 22 cells.
EXPECTED_MATRIX = {
    "XAUUSD": {"tms_orb", "judas"},
    "EURUSD": {"tms_orb", "judas", "flowrsi"},
    "GBPUSD": {"tms_orb", "judas"},
    "USDJPY": {"tms_orb"},
    "GBPJPY": {"tms_orb", "judas"},
    "EURJPY": {"tms_orb", "judas"},
    "USDCAD": {"tms_orb"},
    "AUDUSD": {"tms_orb"},
    "AUDJPY": {"tms_orb"},
    "US30": {"tms_orb"},
    "USTEC": {"tms_orb"},
    "DE40": {"tms_orb"},
    "UK100": {"tms_orb", "judas"},
    "BTCUSD": {"judas"},
    "ETHUSD": {"judas"},
}


def test_matrix_is_exactly_the_readme_cells():
    assert len(PRESETS) == 22
    actual = {}
    for strategy, symbol in PRESETS:
        actual.setdefault(symbol, set()).add(strategy)
    assert actual == EXPECTED_MATRIX
    assert len(SYMBOLS) == 15
    assert set(SYMBOLS) == set(EXPECTED_MATRIX)


def test_every_cell_is_well_formed():
    assert set(STRATEGIES) == {"tms_orb", "judas", "flowrsi"}
    for (strategy, symbol), cell in PRESETS.items():
        assert strategy in STRATEGIES
        assert symbol == symbol.upper()
        assert cell["period"] in ("m5", "m15"), (strategy, symbol)
        assert cell["session"], (strategy, symbol)
        assert cell["params"], (strategy, symbol)
    # --period in the README block is the source of truth
    assert PRESETS[("tms_orb", "USTEC")]["period"] == "m5"
    assert PRESETS[("tms_orb", "DE40")]["period"] == "m15"


def test_tms_orb_golden_command():
    cmd = build_run_command(DEMO, "tms_orb", "EURUSD", ROOT, HOME)
    assert cmd == (
        "docker run -d --name cbot-demo-main-eurusd --restart unless-stopped --network host "
        f"-v {ROOT}:/workspace -v {HOME}:/root {DEFAULT_IMAGE} run /workspace/cBot/AiAgentBot.algo "
        "--ctid=me@example.com --pwd-file=/root/ctrader_data/ctid_demo-main_pwd --account=10101649 "
        "--symbol=EURUSD --period=m15 --full-access "
        '--BotId="cbot-demo-main-eurusd" --ApiUrl="http://127.0.0.1:8000/trade" --AccountLabel="Demo Main" '
        '--TmsTimeFrame="Hour" --EmaPeriod=5 --SessionName="london" --OrbStartHour=8 --SessionEndHour=17 '
        '--SessionDstRule="Europe" --MinDecisiveBreakoutPips=3.0 --MinOrWidthPips=6.0 --OrbBufferPips=1.0 '
        "--BreakevenTriggerAtr=1.2 --BreakevenOffsetAtr=0.1 --TrailTriggerAtr=2.0 --TrailDistanceAtr=1.0 "
        "--PartialCloseRatio=0.5 --MinSlAtr=0.8 --MaxSlAtr=3.0 --MinTpAtr=1.0 --MaxTpAtr=6.0 --MaxGivebackAtr=1.0 "
        "--EnablePostTpGate=true --PostTpPullbackAtr=0.5 --BounceTradeEnabled=true --BounceDistanceThreshold=5 "
        "--RiskPerTradePercent=0.2 --TrendTpDisabled=true"
    )


def test_judas_golden_command():
    cmd = build_run_command(LIVE, "judas", "GBPUSD", ROOT, HOME)
    assert cmd == (
        "docker run -d --name cbot-live-ic-gbpusd-judas --restart unless-stopped --network host "
        f"-v {ROOT}:/workspace -v {HOME}:/root {DEFAULT_IMAGE} run /workspace/cBot/AsianRangeJudasSweepBot.algo "
        "--ctid=me@example.com --pwd-file=/root/ctrader_data/ctid_live-ic_pwd --account=6094347 "
        "--symbol=GBPUSD --period=m15 --full-access "
        '--BotId="cbot-live-ic-gbpusd-judas" --ApiUrl="http://127.0.0.1:8000/trade" --AccountLabel="IC" '
        '--label="cbot-live-ic-gbpusd-judas" --DashboardServerUrl="http://127.0.0.1:8000" '
        "--UseDirectAiApi=false --UseAiGateMode=true --minAsianRangePips=15.0 --maxAsianRangePips=45.0 "
        "--sweepBufferPips=3.5 --AiSlMinFloorPips=15.0 --breakEvenTrigger=20.0 --stoplossPip=15.0 "
        "--takeprofitPip=35.0 --enableBreakEvenPrice=true"
    )


def test_flowrsi_golden_command():
    cmd = build_run_command(DEMO, "flowrsi", "EURUSD", ROOT, HOME)
    assert cmd == (
        "docker run -d --name cbot-demo-main-eurusd-flowrsi --restart unless-stopped --network host "
        f"-v {ROOT}:/workspace -v {HOME}:/root {DEFAULT_IMAGE} run /workspace/cBot/FlowRsiBot.algo "
        "--ctid=me@example.com --pwd-file=/root/ctrader_data/ctid_demo-main_pwd --account=10101649 "
        "--symbol=EURUSD --period=m15 --full-access "
        '--BotId="cbot-demo-main-eurusd-flowrsi" --ApiUrl="http://127.0.0.1:8000/trade" --AccountLabel="Demo Main" '
        "--FastRsiPeriod=7 --SlowRsiPeriod=14 --EnableSmcFilter=true --EnableFvgDetection=true "
        "--EnablePremiumDiscountFilter=true --RiskPercentage=0.2 --MaxRiskPerTradeMoney=50.0 "
        "--TargetRiskReward=1.5 --UseAiGateMode=true"
    )


def test_readme_quirks_are_kept_verbatim():
    xau = build_run_command(DEMO, "tms_orb", "XAUUSD", ROOT, HOME)
    assert "--SessionName" not in xau and "--TmsTimeFrame" not in xau      # README XAUUSD block has neither
    assert "--OrbStartHour=13 --SessionEndHour=21 --SessionDstRule=\"US\"" in xau
    assert "--MinDecisiveBreakoutPips=200.0 --MinOrWidthPips=400.0 --OrbBufferPips=50.0" in xau
    us30 = build_run_command(DEMO, "tms_orb", "US30", ROOT, HOME)
    assert '--SessionName="newyork_index" --OrbStartHour=14 --OrbStartMinute=30 --SessionEndHour=21' in us30
    uk = build_run_command(DEMO, "tms_orb", "UK100", ROOT, HOME)
    assert "--BreakevenTriggerAtr=0.8 --BreakevenOffsetAtr=0.1 --TrailTriggerAtr=1.2 --TrailDistanceAtr=0.7" in uk
    assert "--MinSlAtr=1.5 --MaxSlAtr=4.5 --MinTpAtr=2.0 --MaxTpAtr=8.0 --MaxGivebackAtr=0.6" in uk
    assert "--BounceDistanceThreshold=1.5 " in uk
    btc = build_run_command(DEMO, "judas", "BTCUSD", ROOT, HOME)
    assert btc.endswith("--takeprofitPip=60000.0 --enableBreakEvenPrice=true --riskFactor=0.2")
    assert "--maxAsianRangePips=400000.0" in btc
    xau_judas = build_run_command(DEMO, "judas", "XAUUSD", ROOT, HOME)
    assert "--riskFactor" not in xau_judas


def test_live_vs_demo_naming():
    assert container_name("demo-main", "tms_orb", "XAUUSD") == "cbot-demo-main-xauusd"
    assert container_name("live-ic", "judas", "XAUUSD") == "cbot-live-ic-xauusd-judas"
    assert container_name("live-ic", "flowrsi", "EURUSD") == "cbot-live-ic-eurusd-flowrsi"
    # /api/bots detects live bots by "live-" in the name; demo names must not contain it
    assert "live-" in container_name("live-ic", "tms_orb", "US30")
    assert "live" not in container_name("demo-main", "tms_orb", "US30")


def test_every_command_survives_shlex_and_has_docker_essentials():
    for (strategy, symbol) in PRESETS:
        cmd = build_run_command(LIVE, strategy, symbol, ROOT, HOME)
        assert "\n" not in cmd and "\\" not in cmd
        parts = shlex.split(cmd)
        assert parts[:3] == ["docker", "run", "-d"]
        assert "--name" in parts and parts[parts.index("--name") + 1] == container_name("live-ic", strategy, symbol)
        assert parts.count("-v") == 2
        assert f"{ROOT}:/workspace" in parts and f"{HOME}:/root" in parts
        assert f"--symbol={symbol}" in parts
        assert f"--period={PRESETS[(strategy, symbol)]['period']}" in parts
        assert f"--BotId={container_name('live-ic', strategy, symbol)}" in parts   # quotes stripped by shlex
        assert "--AccountLabel=IC" in parts
        assert ("--DashboardServerUrl=http://127.0.0.1:8000" in parts) == (strategy == "judas")
        assert f"/workspace/cBot/{STRATEGIES[strategy]['algo']}" in parts


def test_custom_image_and_describe_cell():
    cmd = build_run_command(DEMO, "tms_orb", "USTEC", ROOT, HOME, image="ghcr.io/spotware/ctrader-console:1.2")
    assert " ghcr.io/spotware/ctrader-console:1.2 run " in cmd
    assert describe_cell("tms_orb", "USTEC", "Demo Main") == "TMS+ORB USTEC m5 — Demo Main"
    assert describe_cell("judas", "XAUUSD", "IC") == "Judas Sweep XAUUSD m15 — IC"
    assert describe_cell("flowrsi", "EURUSD", "IC") == "FlowRSI EURUSD m15 — IC"


def test_presets_payload_shape():
    payload = presets_payload()
    assert payload["strategies"] == STRATEGIES
    assert payload["symbols"] == SYMBOLS
    assert len(payload["cells"]) == 22
    cell = next(c for c in payload["cells"] if c["symbol"] == "USTEC" and c["strategy"] == "tms_orb")
    assert cell == {"symbol": "USTEC", "strategy": "tms_orb", "period": "m5", "session": "New York"}
    for c in payload["cells"]:
        assert set(c) == {"symbol", "strategy", "period", "session"}
        assert "params" not in c
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_cbot_presets.py -q`
Expected: collection error — `ModuleNotFoundError: No module named 'app.cbot_presets'`.

- [ ] **Step 3: Write the module**

Create `app/cbot_presets.py`:

```python
"""
Strategy × symbol presets for the dashboard's "Setup Instances" screen.

Every cell mirrors one `docker run` block in README.md (section 4, "Run
Multi-Instance Docker Containers"). `params` holds only the strategy-tuned
flags copied verbatim from that block. Infrastructure flags (credentials,
symbol, period, BotId, ApiUrl, AccountLabel, Judas' label/DashboardServerUrl)
are emitted by `build_run_command`, so a preset never knows which account
runs it.
"""
from typing import Dict, List, Tuple

DEFAULT_IMAGE = "ghcr.io/spotware/ctrader-console:latest"
API_URL = "http://127.0.0.1:8000/trade"
DASHBOARD_URL = "http://127.0.0.1:8000"

STRATEGIES: Dict[str, Dict[str, str]] = {
    "tms_orb": {"label": "TMS+ORB",     "algo": "AiAgentBot.algo",              "suffix": ""},
    "judas":   {"label": "Judas Sweep", "algo": "AsianRangeJudasSweepBot.algo", "suffix": "-judas"},
    "flowrsi": {"label": "FlowRSI",     "algo": "FlowRsiBot.algo",              "suffix": "-flowrsi"},
}

# Row order of the setup grid (the spec's matrix order).
SYMBOLS: List[str] = [
    "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "GBPJPY", "EURJPY", "USDCAD", "AUDUSD",
    "AUDJPY", "US30", "USTEC", "DE40", "UK100", "BTCUSD", "ETHUSD",
]

# --- TMS+ORB building blocks (the README blocks share these verbatim) ---
_TMS_HEAD = {"TmsTimeFrame": "Hour", "EmaPeriod": 5}
_LONDON = {**_TMS_HEAD, "SessionName": "london", "OrbStartHour": 8, "SessionEndHour": 17, "SessionDstRule": "Europe"}
_LONDON_INDEX = {**_TMS_HEAD, "SessionName": "london", "OrbStartHour": 8, "SessionEndHour": 16, "SessionDstRule": "Europe"}
_TOKYO = {**_TMS_HEAD, "SessionName": "tokyo", "OrbStartHour": 0, "SessionEndHour": 9, "SessionDstRule": "None"}
_NEWYORK = {**_TMS_HEAD, "SessionName": "newyork", "OrbStartHour": 13, "SessionEndHour": 21, "SessionDstRule": "US"}
_NEWYORK_INDEX = {**_TMS_HEAD, "SessionName": "newyork_index", "OrbStartHour": 14, "OrbStartMinute": 30,
                  "SessionEndHour": 21, "SessionDstRule": "US"}
# The README XAUUSD block predates the TmsTimeFrame/EmaPeriod/SessionName flags; kept verbatim.
_XAU_SESSION = {"OrbStartHour": 13, "SessionEndHour": 21, "SessionDstRule": "US"}

_TMS_ATR = {
    "BreakevenTriggerAtr": 1.2, "BreakevenOffsetAtr": 0.1, "TrailTriggerAtr": 2.0, "TrailDistanceAtr": 1.0,
    "PartialCloseRatio": 0.5, "MinSlAtr": 0.8, "MaxSlAtr": 3.0, "MinTpAtr": 1.0, "MaxTpAtr": 6.0,
    "MaxGivebackAtr": 1.0,
}
_UK100_ATR = {
    "BreakevenTriggerAtr": 0.8, "BreakevenOffsetAtr": 0.1, "TrailTriggerAtr": 1.2, "TrailDistanceAtr": 0.7,
    "PartialCloseRatio": 0.5, "MinSlAtr": 1.5, "MaxSlAtr": 4.5, "MinTpAtr": 2.0, "MaxTpAtr": 8.0,
    "MaxGivebackAtr": 0.6,
}


def _tms(session: dict, breakout: float, or_width: float, buffer: float, bounce, atr: dict = _TMS_ATR) -> dict:
    return {
        **session,
        "MinDecisiveBreakoutPips": breakout, "MinOrWidthPips": or_width, "OrbBufferPips": buffer,
        **atr,
        "EnablePostTpGate": True, "PostTpPullbackAtr": 0.5,
        "BounceTradeEnabled": True, "BounceDistanceThreshold": bounce,
        "RiskPerTradePercent": 0.2, "TrendTpDisabled": True,
    }


def _judas(min_range: float, max_range: float, sweep_buffer: float, ai_sl_floor: float,
           be_trigger: float, sl: float, tp: float, risk_factor=None) -> dict:
    params = {
        "UseDirectAiApi": False, "UseAiGateMode": True,
        "minAsianRangePips": min_range, "maxAsianRangePips": max_range, "sweepBufferPips": sweep_buffer,
        "AiSlMinFloorPips": ai_sl_floor, "breakEvenTrigger": be_trigger,
        "stoplossPip": sl, "takeprofitPip": tp, "enableBreakEvenPrice": True,
    }
    if risk_factor is not None:
        params["riskFactor"] = risk_factor
    return params


def _cell(period: str, session: str, params: dict) -> dict:
    return {"period": period, "session": session, "params": params}


_JUDAS_SESSION = "London + NY killzones"

# (strategy, SYMBOL) -> {"period", "session", "params"}; 15 symbols, 22 cells.
PRESETS: Dict[Tuple[str, str], Dict] = {
    # TMS+ORB (AiAgentBot)
    ("tms_orb", "XAUUSD"): _cell("m15", "New York", _tms(_XAU_SESSION, 200.0, 400.0, 50.0, 10)),
    ("tms_orb", "EURUSD"): _cell("m15", "London",   _tms(_LONDON, 3.0, 6.0, 1.0, 5)),
    ("tms_orb", "GBPUSD"): _cell("m15", "London",   _tms(_LONDON, 4.5, 10.0, 1.5, 10)),
    ("tms_orb", "USDJPY"): _cell("m15", "Tokyo",    _tms(_TOKYO, 4.0, 8.0, 1.5, 3)),
    ("tms_orb", "GBPJPY"): _cell("m15", "London",   _tms(_LONDON, 6.0, 15.0, 2.0, 5)),
    ("tms_orb", "EURJPY"): _cell("m15", "London",   _tms(_LONDON, 5.0, 12.0, 1.5, 5)),
    ("tms_orb", "USDCAD"): _cell("m15", "New York", _tms(_NEWYORK, 4.0, 10.0, 1.5, 4)),
    ("tms_orb", "AUDUSD"): _cell("m15", "Tokyo",    _tms(_TOKYO, 3.0, 8.0, 1.0, 3)),
    ("tms_orb", "AUDJPY"): _cell("m15", "Tokyo",    _tms(_TOKYO, 4.0, 10.0, 1.5, 4)),
    ("tms_orb", "US30"):   _cell("m15", "New York", _tms(_NEWYORK_INDEX, 30.0, 80.0, 15.0, 30)),
    ("tms_orb", "USTEC"):  _cell("m5",  "New York", _tms(_NEWYORK_INDEX, 25.0, 70.0, 12.0, 25)),
    ("tms_orb", "DE40"):   _cell("m15", "London",   _tms(_LONDON_INDEX, 20.0, 60.0, 10.0, 25)),
    ("tms_orb", "UK100"):  _cell("m15", "London",   _tms(_LONDON_INDEX, 25.0, 120.0, 15.0, 1.5, atr=_UK100_ATR)),
    # Asian Range Judas Sweep (AsianRangeJudasSweepBot)
    ("judas", "XAUUSD"): _cell("m15", _JUDAS_SESSION, _judas(200.0, 8000.0, 30.0, 200.0, 250.0, 200.0, 450.0)),
    ("judas", "EURUSD"): _cell("m15", _JUDAS_SESSION, _judas(15.0, 45.0, 3.5, 15.0, 20.0, 15.0, 35.0)),
    ("judas", "GBPUSD"): _cell("m15", _JUDAS_SESSION, _judas(15.0, 45.0, 3.5, 15.0, 20.0, 15.0, 35.0)),
    ("judas", "GBPJPY"): _cell("m15", _JUDAS_SESSION, _judas(25.0, 70.0, 5.0, 25.0, 30.0, 25.0, 50.0)),
    ("judas", "EURJPY"): _cell("m15", _JUDAS_SESSION, _judas(25.0, 70.0, 5.0, 25.0, 30.0, 25.0, 50.0)),
    ("judas", "UK100"):  _cell("m15", _JUDAS_SESSION, _judas(120.0, 800.0, 30.0, 150.0, 200.0, 150.0, 350.0, risk_factor=0.2)),
    ("judas", "BTCUSD"): _cell("m15", _JUDAS_SESSION, _judas(10000.0, 400000.0, 1500.0, 20000.0, 25000.0, 25000.0, 60000.0, risk_factor=0.2)),
    ("judas", "ETHUSD"): _cell("m15", _JUDAS_SESSION, _judas(800.0, 35000.0, 150.0, 1500.0, 2000.0, 2000.0, 5000.0, risk_factor=0.2)),
    # FlowRSI (FlowRsiBot)
    ("flowrsi", "EURUSD"): _cell("m15", "All sessions", {
        "FastRsiPeriod": 7, "SlowRsiPeriod": 14, "EnableSmcFilter": True, "EnableFvgDetection": True,
        "EnablePremiumDiscountFilter": True, "RiskPercentage": 0.2, "MaxRiskPerTradeMoney": 50.0,
        "TargetRiskReward": 1.5, "UseAiGateMode": True,
    }),
}


def _fmt(value) -> str:
    """Render a param value the way the README writes it: true/false, bare numbers, "quoted strings"."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    return f'"{value}"'


def container_name(slug: str, strategy: str, symbol: str) -> str:
    return f"cbot-{slug}-{symbol.lower()}{STRATEGIES[strategy]['suffix']}"


def describe_cell(strategy: str, symbol: str, account_label: str) -> str:
    return f"{STRATEGIES[strategy]['label']} {symbol} {PRESETS[(strategy, symbol)]['period']} — {account_label}"


def build_run_command(account: dict, strategy: str, symbol: str, project_root: str, ctrader_home: str,
                      image: str = DEFAULT_IMAGE) -> str:
    """Single-line `docker run` for one preset cell. `account` needs slug, ctid_email, account_number, label, pwd_file."""
    preset = PRESETS[(strategy, symbol)]
    name = container_name(account["slug"], strategy, symbol)
    parts = [
        "docker", "run", "-d", "--name", name, "--restart", "unless-stopped", "--network", "host",
        "-v", f"{project_root}:/workspace", "-v", f"{ctrader_home}:/root",
        image, "run", f"/workspace/cBot/{STRATEGIES[strategy]['algo']}",
        f"--ctid={account['ctid_email']}", f"--pwd-file={account['pwd_file']}", f"--account={account['account_number']}",
        f"--symbol={symbol}", f"--period={preset['period']}", "--full-access",
        f'--BotId="{name}"', f'--ApiUrl="{API_URL}"', f'--AccountLabel="{account["label"]}"',
    ]
    if strategy == "judas":
        parts += [f'--label="{name}"', f'--DashboardServerUrl="{DASHBOARD_URL}"']
    parts += [f"--{key}={_fmt(value)}" for key, value in preset["params"].items()]
    return " ".join(parts)


def presets_payload() -> dict:
    """What GET /api/setup/presets returns: the grid, without params."""
    return {
        "strategies": STRATEGIES,
        "symbols": SYMBOLS,
        "cells": [
            {"symbol": symbol, "strategy": strategy, "period": cell["period"], "session": cell["session"]}
            for (strategy, symbol), cell in PRESETS.items()
        ],
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_cbot_presets.py -q`
Expected: `10 passed`. If a golden string differs, compare against the README block (`README.md` lines ~324–1212) — the README is the source of truth, not the test.

- [ ] **Step 5: Run the whole suite and commit**

Run: `.venv/bin/pytest -q` → Expected: `148 passed`.

```bash
git add app/cbot_presets.py tests/test_cbot_presets.py
git commit -m "feat(setup): add README-derived cBot presets and docker run command builder

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: `ctrader_accounts` table and registry CRUD

**Files:**
- Modify: `app/accounts.py` (`_init_schema` at ~line 55, `seed_from_env` at ~line 72, new methods after `get_account_type`)
- Test: `tests/test_ctrader_accounts.py` (registry-level tests; Task 3 appends API tests to the same file)

**Interfaces:**
- Consumes: `app.db.get_db_connection` (existing).
- Produces (all on `AccountRegistry`):
  - `upsert_configured_account(self, account_id: str, account_number: str, account_type: str, label: str) -> None` — insert-or-update into `accounts` with `is_configured=1` (the SQL `seed_from_env` already runs, extracted).
  - `list_ctrader_accounts(self) -> List[Dict]` — all columns, live first then label.
  - `get_ctrader_account(self, account_id: int) -> Optional[Dict]`
  - `get_ctrader_account_by_slug(self, slug: str) -> Optional[Dict]`
  - `insert_ctrader_account(self, slug, ctid_email, account_number, account_type, label, pwd_file) -> Dict` — returns the inserted row (all columns). Raises the DB's IntegrityError on a duplicate slug.
  - `delete_ctrader_account(self, account_id: int) -> bool`
  - Row dicts have keys `id, slug, ctid_email, account_number, account_type, label, pwd_file, created_at`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ctrader_accounts.py`:

```python
import sqlite3
import sys
from pathlib import Path

import pytest

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.accounts import AccountRegistry

CTRADER_COLUMNS = {"id", "slug", "ctid_email", "account_number", "account_type", "label", "pwd_file", "created_at"}


@pytest.fixture
def registry(tmp_path):
    return AccountRegistry(str(tmp_path / "accounts_test.db"))


def _insert(reg, slug="demo-main", account_type="demo", label="Demo Main", number="10101649"):
    return reg.insert_ctrader_account(slug, "me@example.com", number, account_type, label,
                                      f"/root/ctrader_data/ctid_{slug}_pwd")


def test_ctrader_accounts_crud(registry):
    assert registry.list_ctrader_accounts() == []
    row = _insert(registry)
    assert set(row) == CTRADER_COLUMNS
    assert row["id"] >= 1
    assert row["slug"] == "demo-main"
    assert row["pwd_file"] == "/root/ctrader_data/ctid_demo-main_pwd"
    assert row["created_at"]

    assert registry.get_ctrader_account(row["id"])["label"] == "Demo Main"
    assert registry.get_ctrader_account(row["id"] + 1000) is None
    assert registry.get_ctrader_account_by_slug("demo-main")["id"] == row["id"]
    assert registry.get_ctrader_account_by_slug("nope") is None
    assert [a["slug"] for a in registry.list_ctrader_accounts()] == ["demo-main"]

    assert registry.delete_ctrader_account(row["id"]) is True
    assert registry.delete_ctrader_account(row["id"]) is False
    assert registry.get_ctrader_account(row["id"]) is None
    assert registry.list_ctrader_accounts() == []


def test_slug_is_unique(registry):
    _insert(registry)
    with pytest.raises(sqlite3.IntegrityError):
        _insert(registry, number="999")


def test_account_type_is_checked(registry):
    with pytest.raises(sqlite3.IntegrityError):
        _insert(registry, slug="x-main", account_type="paper")


def test_list_orders_live_first_then_label(registry):
    _insert(registry, slug="demo-zulu", account_type="demo", label="Zulu")
    _insert(registry, slug="demo-alpha", account_type="demo", label="Alpha")
    _insert(registry, slug="live-ic", account_type="live", label="IC", number="6094347")
    assert [a["slug"] for a in registry.list_ctrader_accounts()] == ["live-ic", "demo-alpha", "demo-zulu"]


def test_upsert_configured_account_marks_dashboard_account(registry):
    registry.upsert_configured_account("live-6094347", "6094347", "live", "IC")
    accounts = registry.list_accounts()          # configured only
    assert len(accounts) == 1
    assert accounts[0]["account_id"] == "live-6094347"
    assert accounts[0]["label"] == "IC"
    assert accounts[0]["is_configured"] == 1
    # Re-upsert relabels instead of duplicating (unique on number+type)
    registry.upsert_configured_account("live-6094347", "6094347", "live", "IC Main")
    accounts = registry.list_accounts()
    assert len(accounts) == 1 and accounts[0]["label"] == "IC Main"


def test_seed_from_env_still_uses_the_upsert(registry, monkeypatch):
    monkeypatch.setenv("DASHBOARD_ACCOUNTS", "demo-1|7654321|demo|Demo Test;live-main|1234567|live|Live Main")
    registry.seed_from_env()
    ids = sorted(a["account_id"] for a in registry.list_accounts())
    assert ids == ["demo-1", "live-main"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_ctrader_accounts.py -q`
Expected: 6 failures — `AttributeError: 'AccountRegistry' object has no attribute 'insert_ctrader_account'` / `upsert_configured_account`.

- [ ] **Step 3: Add the DDL, extract the upsert, add CRUD methods**

In `app/accounts.py`, inside `_init_schema` after the `CREATE UNIQUE INDEX ... idx_accounts_number_type` statement and before `conn.commit()`, add:

```python
            # cTrader login accounts used by the dashboard's "Setup Instances" screen.
            # pwd_file is the in-container path; the password itself lives only on disk.
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ctrader_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                ctid_email TEXT NOT NULL,
                account_number TEXT NOT NULL,
                account_type TEXT NOT NULL CHECK(account_type IN ('live','demo')),
                label TEXT NOT NULL,
                pwd_file TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
```

Replace the body of `seed_from_env` so it delegates:

```python
    def seed_from_env(self):
        for acc in parse_dashboard_accounts_env():
            self.upsert_configured_account(acc["account_id"], acc["account_number"], acc["account_type"], acc["label"])

    def upsert_configured_account(self, account_id: str, account_number: str, account_type: str, label: str) -> None:
        """Insert or relabel a dashboard account and mark it configured (unique on number+type)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO accounts (account_id, account_number, account_type, label, is_configured)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(account_number, account_type) DO UPDATE SET
                account_id = excluded.account_id,
                label = excluded.label,
                is_configured = 1
            """, (account_id, account_number, account_type, label))
            conn.commit()
```

After `get_account_type`, add:

```python
    # --- cTrader accounts (Setup Instances screen) ---

    _CTRADER_COLUMNS = "id, slug, ctid_email, account_number, account_type, label, pwd_file, created_at"

    def list_ctrader_accounts(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
            SELECT {self._CTRADER_COLUMNS} FROM ctrader_accounts
            ORDER BY CASE WHEN account_type = 'live' THEN 0 ELSE 1 END, label ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_ctrader_account(self, account_id: int) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {self._CTRADER_COLUMNS} FROM ctrader_accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_ctrader_account_by_slug(self, slug: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {self._CTRADER_COLUMNS} FROM ctrader_accounts WHERE slug = ?", (slug,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert_ctrader_account(self, slug: str, ctid_email: str, account_number: str, account_type: str,
                               label: str, pwd_file: str) -> Dict:
        """Insert and return the new row. Raises the driver's IntegrityError on a duplicate slug."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO ctrader_accounts (slug, ctid_email, account_number, account_type, label, pwd_file)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (slug, ctid_email, account_number, account_type, label, pwd_file))
            conn.commit()
        # Re-read by slug: lastrowid is not available through the PostgreSQL wrapper.
        return self.get_ctrader_account_by_slug(slug)

    def delete_ctrader_account(self, account_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ctrader_accounts WHERE id = ?", (account_id,))
            conn.commit()
            return cursor.rowcount > 0
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_ctrader_accounts.py -q`
Expected: `6 passed`.

- [ ] **Step 5: Run the whole suite and commit**

Run: `.venv/bin/pytest -q` → Expected: `154 passed` (the server's registry now also creates the table in the test DB; nothing else changes).

```bash
git add app/accounts.py tests/test_ctrader_accounts.py
git commit -m "feat(accounts): add ctrader_accounts table and registry CRUD; extract configured-account upsert

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Account service (validation, slug, password file) and `/api/ctrader-accounts` routes

**Files:**
- Create: `app/ctrader_accounts.py`
- Modify: `app/dashboard.py` (insert after `api_restart_bot`, before `api_watchdog_status`, ~line 997)
- Test: `tests/test_ctrader_accounts.py` (append API tests)

**Interfaces:**
- Consumes: Task 2's registry methods; `get_account_registry()` from `app.accounts`.
- Produces (`app/ctrader_accounts.py`):
  - `class AccountValidationError(ValueError)` → 422; `class DuplicateSlugError(ValueError)` → 409.
  - `ctrader_home() -> str` — `os.environ.get("CTRADER_HOME")` or `/root`.
  - `slugify(account_type: str, label: str) -> str`
  - `validate_account_input(label, ctid_email, password, account_number, account_type) -> None` (raises `AccountValidationError`).
  - `password_file_paths(slug: str) -> Tuple[Path, str]` — `(host path, in-container path)`.
  - `write_password_file(path: Path, password: str) -> None`
  - `public_view(row: Dict) -> Dict` — drops `pwd_file`.
  - `create_ctrader_account(registry, *, label, ctid_email, password, account_number, account_type) -> Dict` (public view).
  - `delete_ctrader_account(registry, account_id: int) -> bool`
  - `list_ctrader_accounts(registry) -> List[Dict]` (public views).
- Produces (routes): `GET /api/ctrader-accounts` → `{"accounts": [...]}`; `POST /api/ctrader-accounts` → `201 {"success": true, "account": {...}}`; `DELETE /api/ctrader-accounts/{account_id}` → `{"success": true}`. Also the helper `_error(status: int, message: str) -> JSONResponse` in `app/dashboard.py`, reused by Task 4.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_ctrader_accounts.py`:

```python
# ---------------------------------------------------------------------------
# Service + API
# ---------------------------------------------------------------------------
import stat

from fastapi.testclient import TestClient

from app.server import app
from app.accounts import get_account_registry
from app.ctrader_accounts import slugify

client = TestClient(app)


@pytest.fixture
def ctrader_home(tmp_path, monkeypatch):
    """Point CTRADER_HOME at a temp dir and start each test with an empty ctrader_accounts table."""
    monkeypatch.setenv("CTRADER_HOME", str(tmp_path))
    reg = get_account_registry()
    with reg._get_connection() as conn:
        conn.execute("DELETE FROM ctrader_accounts")
        conn.commit()
    return tmp_path


def _payload(**overrides):
    base = {"label": "Demo Main", "ctid_email": "me@example.com", "password": "s3cret!",
            "account_number": "10101649", "account_type": "demo"}
    base.update(overrides)
    return base


def test_slugify():
    assert slugify("demo", "Main") == "demo-main"
    assert slugify("live", "IC Markets #2") == "live-ic-markets-2"
    assert slugify("live", "  Spaces  ") == "live-spaces"
    long = slugify("demo", "a very long account label indeed")
    assert len(long) <= 24 and not long.endswith("-") and long.startswith("demo-")


def test_create_account_writes_row_file_and_dashboard_tab(ctrader_home):
    res = client.post("/api/ctrader-accounts", json=_payload())
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["success"] is True
    acc = body["account"]
    assert acc["slug"] == "demo-main"
    assert acc["label"] == "Demo Main" and acc["account_type"] == "demo" and acc["account_number"] == "10101649"
    assert "password" not in acc and "pwd_file" not in acc
    assert "s3cret!" not in res.text

    pwd = ctrader_home / "ctrader_data" / "ctid_demo-main_pwd"
    assert pwd.read_text() == "s3cret!"
    assert stat.S_IMODE(pwd.stat().st_mode) == 0o600
    assert stat.S_IMODE(pwd.parent.stat().st_mode) == 0o700

    row = get_account_registry().get_ctrader_account(acc["id"])
    assert row["pwd_file"] == "/root/ctrader_data/ctid_demo-main_pwd"     # in-container path

    tabs = get_account_registry().list_accounts()
    assert any(t["account_id"] == "demo-10101649" and t["label"] == "Demo Main" and t["is_configured"] == 1 for t in tabs)


def test_list_omits_secrets(ctrader_home):
    client.post("/api/ctrader-accounts", json=_payload())
    client.post("/api/ctrader-accounts", json=_payload(label="IC", account_type="live", account_number="6094347"))
    res = client.get("/api/ctrader-accounts")
    assert res.status_code == 200
    accounts = res.json()["accounts"]
    assert [a["slug"] for a in accounts] == ["live-ic", "demo-main"]
    for a in accounts:
        assert set(a) == {"id", "slug", "ctid_email", "account_number", "account_type", "label", "created_at"}
    assert "s3cret" not in res.text


def test_duplicate_slug_is_409_and_writes_no_second_file(ctrader_home):
    assert client.post("/api/ctrader-accounts", json=_payload()).status_code == 201
    res = client.post("/api/ctrader-accounts", json=_payload(account_number="222", password="other"))
    assert res.status_code == 409
    assert res.json() == {"success": False, "message": res.json()["message"]}
    assert "demo-main" in res.json()["message"]
    assert (ctrader_home / "ctrader_data" / "ctid_demo-main_pwd").read_text() == "s3cret!"   # untouched
    assert len(client.get("/api/ctrader-accounts").json()["accounts"]) == 1


def test_delete_removes_row_and_file(ctrader_home):
    acc = client.post("/api/ctrader-accounts", json=_payload()).json()["account"]
    pwd = ctrader_home / "ctrader_data" / "ctid_demo-main_pwd"
    assert pwd.exists()
    res = client.delete(f"/api/ctrader-accounts/{acc['id']}")
    assert res.status_code == 200 and res.json() == {"success": True}
    assert not pwd.exists()
    assert client.get("/api/ctrader-accounts").json()["accounts"] == []
    res = client.delete(f"/api/ctrader-accounts/{acc['id']}")
    assert res.status_code == 404 and res.json()["success"] is False


@pytest.mark.parametrize("bad, fragment", [
    ({"ctid_email": "not-an-email"}, "email"),
    ({"ctid_email": "a b@example.com"}, "email"),
    ({"account_number": "12ab"}, "digits"),
    ({"account_number": ""}, "digits"),
    ({"label": ""}, "label"),
    ({"label": "x" * 41}, "label"),
    ({"label": 'Has "quote"'}, "quotes"),
    ({"label": "line\nbreak"}, "quotes"),
    ({"label": "!!!"}, "letter or digit"),
    ({"label": "Not Live", "account_type": "demo"}, "live"),
    ({"password": ""}, "password"),
    ({"account_type": "paper"}, "account_type"),
])
def test_validation_returns_422_and_writes_nothing(ctrader_home, bad, fragment):
    res = client.post("/api/ctrader-accounts", json=_payload(**bad))
    assert res.status_code == 422, res.text
    assert res.json()["success"] is False
    assert fragment in res.json()["message"]
    assert not (ctrader_home / "ctrader_data").exists()
    assert client.get("/api/ctrader-accounts").json()["accounts"] == []


def test_live_label_may_contain_live(ctrader_home):
    res = client.post("/api/ctrader-accounts", json=_payload(label="Live IC", account_type="live", account_number="6094347"))
    assert res.status_code == 201 and res.json()["account"]["slug"] == "live-live-ic"


def test_unwritable_ctrader_home_is_500_and_no_row(ctrader_home, monkeypatch):
    blocker = ctrader_home / "blocker"
    blocker.write_text("not a directory")
    monkeypatch.setenv("CTRADER_HOME", str(blocker))
    res = client.post("/api/ctrader-accounts", json=_payload())
    assert res.status_code == 500
    assert res.json()["success"] is False and "password file" in res.json()["message"]
    assert client.get("/api/ctrader-accounts").json()["accounts"] == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_ctrader_accounts.py -q`
Expected: `ModuleNotFoundError: No module named 'app.ctrader_accounts'` at collection.

- [ ] **Step 3: Write the service module**

Create `app/ctrader_accounts.py`:

```python
"""
cTrader account service behind /api/ctrader-accounts (the dashboard's
"Setup Instances" screen): input validation, slug derivation, the cTID
password file under $CTRADER_HOME/ctrader_data, and the ctrader_accounts row.

The password only ever passes through create_ctrader_account on its way to
disk; it is never logged, stored, or returned.
"""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from app.accounts import AccountRegistry

logger = logging.getLogger(__name__)

SLUG_MAX_LEN = 24
LABEL_MAX_LEN = 40
CONTAINER_CREDENTIALS_DIR = "/root/ctrader_data"   # every container mounts CTRADER_HOME as /root


class AccountValidationError(ValueError):
    """Bad client input -> HTTP 422."""


class DuplicateSlugError(ValueError):
    """An account with the same slug already exists -> HTTP 409."""


def ctrader_home() -> str:
    """Host directory mounted as /root in every cBot container (Phase 1 writes it to .env)."""
    return os.environ.get("CTRADER_HOME", "").strip() or "/root"


def slugify(account_type: str, label: str) -> str:
    """`<type>-<label>` in [a-z0-9-], max 24 chars: ('live', 'IC Markets #2') -> 'live-ic-markets-2'."""
    body = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"{account_type}-{body}"[:SLUG_MAX_LEN].rstrip("-")


def validate_account_input(label: str, ctid_email: str, password: str, account_number: str, account_type: str) -> None:
    if account_type not in ("live", "demo"):
        raise AccountValidationError("account_type must be 'live' or 'demo'")
    if not 1 <= len(label) <= LABEL_MAX_LEN:
        raise AccountValidationError(f"label must be 1-{LABEL_MAX_LEN} characters")
    if '"' in label or "\n" in label or "\r" in label:
        raise AccountValidationError("label must not contain quotes or newlines")
    if not re.search(r"[a-z0-9]", label.lower()):
        raise AccountValidationError("label must contain at least one letter or digit")
    if account_type == "demo" and "live" in slugify(account_type, label):
        raise AccountValidationError("a demo account label must not contain 'live' (the dashboard uses it to detect live bots)")
    if "@" not in ctid_email or re.search(r'[\s"]', ctid_email):
        raise AccountValidationError("ctid_email must be an email address")
    if not account_number.isdigit():
        raise AccountValidationError("account_number must contain digits only")
    if not password:
        raise AccountValidationError("password must not be empty")


def password_file_paths(slug: str) -> Tuple[Path, str]:
    """(host path, in-container path) of the cTID password file for `slug`."""
    filename = f"ctid_{slug}_pwd"
    return Path(ctrader_home()) / "ctrader_data" / filename, f"{CONTAINER_CREDENTIALS_DIR}/{filename}"


def write_password_file(path: Path, password: str) -> None:
    """Write `password` to `path` with mode 0600; the parent is created 0700 when missing."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(password)
    os.chmod(path, 0o600)   # O_CREAT's mode is umask-masked and ignored for a pre-existing file


def public_view(row: Dict) -> Dict:
    return {k: row[k] for k in ("id", "slug", "ctid_email", "account_number", "account_type", "label", "created_at")}


def list_ctrader_accounts(registry: AccountRegistry) -> List[Dict]:
    return [public_view(row) for row in registry.list_ctrader_accounts()]


def create_ctrader_account(registry: AccountRegistry, *, label: str, ctid_email: str, password: str,
                           account_number: str, account_type: str) -> Dict:
    """Validate, write the password file, insert the row, mark the dashboard account configured.

    Raises AccountValidationError (422), DuplicateSlugError (409) or OSError (500, no row written).
    """
    label = label.strip()
    ctid_email = ctid_email.strip()
    account_number = account_number.strip()
    account_type = account_type.strip().lower()
    validate_account_input(label, ctid_email, password, account_number, account_type)

    slug = slugify(account_type, label)
    if registry.get_ctrader_account_by_slug(slug):
        raise DuplicateSlugError(f"an account with slug '{slug}' already exists")

    host_path, container_path = password_file_paths(slug)
    write_password_file(host_path, password)
    try:
        row = registry.insert_ctrader_account(slug, ctid_email, account_number, account_type, label, container_path)
    except Exception:
        host_path.unlink(missing_ok=True)
        raise
    registry.upsert_configured_account(f"{account_type}-{account_number}", account_number, account_type, label)
    logger.info(f"cTrader account created: {slug} ({account_type} {account_number})")
    return public_view(row)


def delete_ctrader_account(registry: AccountRegistry, account_id: int) -> bool:
    """Delete the row and its password file. cbot_configs are left alone (their commands are self-contained)."""
    row = registry.get_ctrader_account(account_id)
    if not row:
        return False
    registry.delete_ctrader_account(account_id)
    host_path, _ = password_file_paths(row["slug"])
    try:
        host_path.unlink(missing_ok=True)
    except OSError as e:
        logger.warning(f"Could not remove password file {host_path}: {e}")
    logger.info(f"cTrader account deleted: {row['slug']}")
    return True
```

- [ ] **Step 4: Add the routes**

In `app/dashboard.py`, after `api_restart_bot` (the `@router.post("/api/bots/{name}/restart")` handler) and before `@router.get("/api/watchdog/status")`, insert:

```python
# --- cTrader accounts & preset-based instance setup (Setup Instances screen) ---
from fastapi.responses import JSONResponse
from app import ctrader_accounts as ctrader_accounts_service


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "message": message})


class CtraderAccountRequest(BaseModel):
    label: str = ""
    ctid_email: str = ""
    password: str = ""
    account_number: str = ""
    account_type: str = "demo"


@router.get("/api/ctrader-accounts")
async def api_list_ctrader_accounts():
    return {"accounts": ctrader_accounts_service.list_ctrader_accounts(get_account_registry())}


@router.post("/api/ctrader-accounts", status_code=201)
async def api_create_ctrader_account(req: CtraderAccountRequest):
    try:
        account = ctrader_accounts_service.create_ctrader_account(
            get_account_registry(), label=req.label, ctid_email=req.ctid_email, password=req.password,
            account_number=req.account_number, account_type=req.account_type,
        )
    except ctrader_accounts_service.AccountValidationError as e:
        return _error(422, str(e))
    except ctrader_accounts_service.DuplicateSlugError as e:
        return _error(409, str(e))
    except OSError as e:
        return _error(500, f"Could not write password file: {e}")
    return {"success": True, "account": account}


@router.delete("/api/ctrader-accounts/{account_id}")
async def api_delete_ctrader_account(account_id: int):
    if not ctrader_accounts_service.delete_ctrader_account(get_account_registry(), account_id):
        return _error(404, "Account not found")
    return {"success": True}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_ctrader_accounts.py -q`
Expected: `25 passed` (6 registry + 8 API functions, one of them parametrized ×12 → 19).

- [ ] **Step 6: Run the whole suite and commit**

Run: `.venv/bin/pytest -q` → Expected: `173 passed`.

```bash
git add app/ctrader_accounts.py app/dashboard.py tests/test_ctrader_accounts.py
git commit -m "feat(setup): cTrader account service and /api/ctrader-accounts routes with on-disk password files

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: `/api/setup/presets` and `/api/setup/instances`

**Files:**
- Modify: `app/dashboard.py` (append after Task 3's routes)
- Test: `tests/test_setup_instances.py`

**Interfaces:**
- Consumes: `PRESETS`, `build_run_command`, `container_name`, `describe_cell`, `presets_payload` (Task 1); `get_ctrader_account` (Task 2); `ctrader_accounts_service.ctrader_home()` and `_error` (Task 3); `get_portfolio_manager().get_cbot_config/add_cbot_config` and `docker_manager.start_container` (existing).
- Produces: `GET /api/setup/presets` → `presets_payload()`; `POST /api/setup/instances` body `{"account_id": int, "selections": [{"symbol", "strategy"}], "start": bool = true}` → `{"results": [{symbol, strategy, name, status, message}]}`; `404` `{"success": false, "message"}` for an unknown `account_id`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_setup_instances.py`:

```python
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.server import app
import app.dashboard as dashboard_module
from app.accounts import get_account_registry
from app.portfolio import get_portfolio_manager
from app.cbot_presets import build_run_command

client = TestClient(app)


class FakeDocker:
    def __init__(self, success=True):
        self.calls = []
        self.success = success
        self.is_available = True

    def start_container(self, name, command):
        self.calls.append((name, command))
        return {"success": self.success, "message": "ok" if self.success else "boom"}


@pytest.fixture
def fake_docker(monkeypatch):
    fake = FakeDocker()
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    return fake


@pytest.fixture
def account(tmp_path, monkeypatch):
    """A fresh demo account 'Setup' (slug demo-setup) with CTRADER_HOME in tmp_path; cleans its bot configs."""
    monkeypatch.setenv("CTRADER_HOME", str(tmp_path))
    reg = get_account_registry()
    with reg._get_connection() as conn:
        conn.execute("DELETE FROM ctrader_accounts")
        conn.execute("DELETE FROM cbot_configs WHERE name LIKE 'cbot-demo-setup-%'")
        conn.commit()
    res = client.post("/api/ctrader-accounts", json={
        "label": "Setup", "ctid_email": "me@example.com", "password": "pw",
        "account_number": "10101649", "account_type": "demo"})
    assert res.status_code == 201, res.text
    acc = res.json()["account"]
    yield acc
    with reg._get_connection() as conn:
        conn.execute("DELETE FROM cbot_configs WHERE name LIKE 'cbot-demo-setup-%'")
        conn.commit()


def _post(account_id, selections, start=True):
    return client.post("/api/setup/instances", json={"account_id": account_id, "selections": selections, "start": start})


def test_presets_endpoint_shape():
    res = client.get("/api/setup/presets")
    assert res.status_code == 200
    data = res.json()
    assert set(data["strategies"]) == {"tms_orb", "judas", "flowrsi"}
    assert data["strategies"]["judas"]["label"] == "Judas Sweep"
    assert len(data["symbols"]) == 15
    assert len(data["cells"]) == 22
    assert all(set(c) == {"symbol", "strategy", "period", "session"} for c in data["cells"])


def test_start_saves_config_and_starts_each_new_selection(account, fake_docker, tmp_path):
    res = _post(account["id"], [{"symbol": "XAUUSD", "strategy": "tms_orb"}, {"symbol": "GBPUSD", "strategy": "judas"}])
    assert res.status_code == 200, res.text
    results = res.json()["results"]
    assert [r["status"] for r in results] == ["started", "started"]
    assert [r["name"] for r in results] == ["cbot-demo-setup-xauusd", "cbot-demo-setup-gbpusd-judas"]
    assert results[0]["message"] == "ok"

    row = get_account_registry().get_ctrader_account(account["id"])
    expected = build_run_command(row, "tms_orb", "XAUUSD", str(dashboard_module.PROJECT_ROOT), str(tmp_path))
    assert fake_docker.calls[0] == ("cbot-demo-setup-xauusd", expected)
    assert len(fake_docker.calls) == 2

    pm = get_portfolio_manager()
    cfg = pm.get_cbot_config("cbot-demo-setup-xauusd")
    assert cfg["run_command"] == expected
    assert cfg["description"] == "TMS+ORB XAUUSD m15 — Setup"
    assert f"-v {tmp_path}:/root" in expected                       # CTRADER_HOME from env
    assert "--pwd-file=/root/ctrader_data/ctid_demo-setup_pwd" in expected
    assert pm.get_cbot_config("cbot-demo-setup-gbpusd-judas")["description"] == "Judas Sweep GBPUSD m15 — Setup"


def test_save_only_never_calls_docker(account, fake_docker):
    res = _post(account["id"], [{"symbol": "EURUSD", "strategy": "flowrsi"}], start=False)
    results = res.json()["results"]
    assert results == [{"symbol": "EURUSD", "strategy": "flowrsi", "name": "cbot-demo-setup-eurusd-flowrsi",
                        "status": "saved", "message": "Config saved"}]
    assert fake_docker.calls == []
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-eurusd-flowrsi") is not None


def test_existing_name_is_reported_and_not_started(account, fake_docker):
    first = _post(account["id"], [{"symbol": "US30", "strategy": "tms_orb"}]).json()["results"]
    assert first[0]["status"] == "started"
    second = _post(account["id"], [{"symbol": "US30", "strategy": "tms_orb"}]).json()["results"]
    assert second[0]["status"] == "exists"
    assert second[0]["name"] == "cbot-demo-setup-us30"
    assert len(fake_docker.calls) == 1


def test_unknown_pair_is_error_and_batch_continues(account, fake_docker):
    res = _post(account["id"], [
        {"symbol": "BTCUSD", "strategy": "tms_orb"},       # no such preset
        {"symbol": "eurusd", "strategy": "flowrsi"},        # symbol case-normalised
        {"symbol": "XAUUSD", "strategy": "nope"},
    ])
    results = res.json()["results"]
    assert results[0]["status"] == "error" and "preset" in results[0]["message"] and results[0]["name"] == ""
    assert results[1]["status"] == "started" and results[1]["symbol"] == "EURUSD"
    assert results[2]["status"] == "error"
    assert len(fake_docker.calls) == 1


def test_docker_failure_keeps_config_for_retry(account, monkeypatch):
    fake = FakeDocker(success=False)
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    res = _post(account["id"], [{"symbol": "DE40", "strategy": "tms_orb"}])
    result = res.json()["results"][0]
    assert result["status"] == "error" and result["message"] == "boom"
    assert get_portfolio_manager().get_cbot_config("cbot-demo-setup-de40") is not None


def test_unknown_account_is_404(fake_docker):
    res = _post(999999, [{"symbol": "XAUUSD", "strategy": "tms_orb"}])
    assert res.status_code == 404
    assert res.json()["success"] is False
    assert fake_docker.calls == []


def test_empty_selection_is_ok(account, fake_docker):
    res = _post(account["id"], [])
    assert res.status_code == 200 and res.json() == {"results": []}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_setup_instances.py -q`
Expected: `test_presets_endpoint_shape` fails with `assert 404 == 200`; the others fail on `res.json()["results"]` (404 body has no `results`).

- [ ] **Step 3: Add the routes**

In `app/dashboard.py`, directly after `api_delete_ctrader_account` (Task 3), add:

```python
from app.cbot_presets import PRESETS, build_run_command, container_name, describe_cell, presets_payload


class InstanceSelection(BaseModel):
    symbol: str
    strategy: str


class SetupInstancesRequest(BaseModel):
    account_id: int
    selections: List[InstanceSelection]
    start: bool = True


@router.get("/api/setup/presets")
async def api_setup_presets():
    return presets_payload()


@router.post("/api/setup/instances")
async def api_setup_instances(req: SetupInstancesRequest):
    """Save (and optionally start) one cbot_configs row per selected preset cell. Never aborts the batch."""
    account = get_account_registry().get_ctrader_account(req.account_id)
    if not account:
        return _error(404, "Account not found")
    pm = get_portfolio_manager()
    ctrader_home = ctrader_accounts_service.ctrader_home()
    results = []
    for sel in req.selections:
        symbol, strategy = sel.symbol.strip().upper(), sel.strategy.strip()
        entry = {"symbol": symbol, "strategy": strategy, "name": "", "status": "error", "message": ""}
        results.append(entry)
        if (strategy, symbol) not in PRESETS:
            entry["message"] = f"No preset for {strategy} × {symbol}"
            continue
        name = container_name(account["slug"], strategy, symbol)
        entry["name"] = name
        cmd = build_run_command(account, strategy, symbol, str(PROJECT_ROOT), ctrader_home)
        # get_cbot_config first: add_cbot_config only recognises sqlite3.IntegrityError, not psycopg2's
        if pm.get_cbot_config(name) or not pm.add_cbot_config(name, describe_cell(strategy, symbol, account["label"]), cmd):
            entry.update(status="exists", message="Bot config already exists")
            continue
        if not req.start:
            entry.update(status="saved", message="Config saved")
            continue
        result = docker_manager.start_container(name, cmd)
        if result.get("success"):
            entry.update(status="started", message=result.get("message", "Container started"))
        else:
            entry["message"] = result.get("message", "Docker error")   # config row kept so the user can retry
    return {"results": results}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_setup_instances.py -q`
Expected: `8 passed`.

- [ ] **Step 5: Run the whole suite and commit**

Run: `.venv/bin/pytest -q` → Expected: `181 passed`.

```bash
git add app/dashboard.py tests/test_setup_instances.py
git commit -m "feat(setup): presets endpoint and batch instance creation from preset cells

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Setup Instances panel in the Docker view, README tip

**Files:**
- Modify: `templates/dashboard.html` (panel header ~line 521–525, insert panel after `#bot-form-container` ~line 549, JS after `submitBotForm` ~line 945 and inside the `DOMContentLoaded` handler ~line 948–966)
- Modify: `README.md` (section "### 4. Setup & Run cBot", before "4. **Run Multi-Instance Docker Containers**")
- Test: `tests/test_dashboard_ui.py` (append)

**Interfaces:**
- Consumes: the five routes from Tasks 3–4; existing `fetchBots()`.
- Produces: DOM ids `setup-instances-btn`, `setup-panel`, `setup-account`, `setup-account-delete`, `setup-new-account`, `setup-acc-label`, `setup-acc-email`, `setup-acc-password`, `setup-acc-number`, radio `setup-acc-type`, `setup-account-save`, `setup-account-msg`, `setup-grid`, `setup-grid-head`, `setup-grid-body`, `setup-save-only`, `setup-create-btn`, `setup-cancel-btn`, `setup-results`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_dashboard_ui.py`:

```python
def test_setup_instances_panel_is_in_docker_view():
    html = client.get("/demo/dashboard").text
    docker_idx = html.find('id="view-docker"')
    logs_idx = html.find('id="view-logs"')
    panel_idx = html.find('id="setup-panel"')
    button_idx = html.find('id="setup-instances-btn"')
    assert docker_idx != -1 and panel_idx != -1 and button_idx != -1
    assert docker_idx < button_idx < panel_idx < logs_idx        # inside the Docker view, next to Add Bot
    assert "Setup Instances" in html
    for element_id in ("setup-account", "setup-new-account", "setup-acc-password", "setup-grid",
                       "setup-save-only", "setup-create-btn", "setup-results"):
        assert f'id="{element_id}"' in html, element_id
    assert 'id="setup-acc-password" type="password"' in html
    for endpoint in ("/api/setup/presets", "/api/setup/instances", "/api/ctrader-accounts"):
        assert endpoint in html, endpoint
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py::test_setup_instances_panel_is_in_docker_view -q`
Expected: FAIL — `assert docker_idx != -1 and panel_idx != -1 ...` (panel_idx is -1).

- [ ] **Step 3: Add the button and the panel markup**

In `templates/dashboard.html`, replace the Docker panel header's Add Bot button:

```html
                        <button id="add-bot-btn" class="log-btn" style="margin-left:auto;"><i data-lucide="plus" class="btn-icon"></i> Add Bot</button>
```

with two buttons:

```html
                        <button id="setup-instances-btn" class="log-btn" style="margin-left:auto;"><i data-lucide="layout-grid" class="btn-icon"></i> Setup Instances</button>
                        <button id="add-bot-btn" class="log-btn"><i data-lucide="plus" class="btn-icon"></i> Add Bot</button>
```

Then, directly after the closing `</div>` of `#bot-form-container` (the line before `<div class="table-wrap">` that wraps `#bots-table`), insert:

```html
                    <div id="setup-panel" style="display:none; margin-bottom: 16px; padding: 16px; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 6px;">
                        <h4 style="margin-top:0; margin-bottom:12px; color:var(--accent-bright);">Setup Instances from Presets</h4>
                        <div class="bot-form-grid">
                            <div>
                                <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:4px;">cTrader Account</label>
                                <div style="display:flex; gap:6px; align-items:center;">
                                    <select id="setup-account" class="log-select" style="flex:1;"></select>
                                    <button id="setup-account-delete" class="log-btn" title="Delete selected account" style="display:none;">🗑</button>
                                </div>
                            </div>
                        </div>
                        <div id="setup-new-account" style="display:none; margin-top:12px;">
                            <div class="bot-form-grid">
                                <div>
                                    <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:4px;">Label (1–40 chars)</label>
                                    <input type="text" id="setup-acc-label" class="log-input" style="width:100%" placeholder="Demo Main" maxlength="40">
                                </div>
                                <div>
                                    <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:4px;">cTID email</label>
                                    <input type="text" id="setup-acc-email" class="log-input" style="width:100%" placeholder="you@example.com" autocomplete="off">
                                </div>
                                <div>
                                    <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:4px;">cTID password (written to a 0600 file, never stored)</label>
                                    <input id="setup-acc-password" type="password" class="log-input" style="width:100%" autocomplete="new-password">
                                </div>
                                <div>
                                    <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:4px;">Account number</label>
                                    <input type="text" id="setup-acc-number" class="log-input" style="width:100%" placeholder="10101649" inputmode="numeric">
                                </div>
                            </div>
                            <div style="margin-top:10px; display:flex; gap:14px; align-items:center; flex-wrap:wrap;">
                                <label style="font-size:0.75rem;"><input type="radio" name="setup-acc-type" value="demo" checked> Demo</label>
                                <label style="font-size:0.75rem;"><input type="radio" name="setup-acc-type" value="live"> Live</label>
                                <button id="setup-account-save" class="log-btn" style="background:var(--profit-soft); color:var(--profit); border-color:var(--profit);"><i data-lucide="save" class="btn-icon"></i> Save account</button>
                                <span id="setup-account-msg" class="td-dim"></span>
                            </div>
                        </div>
                        <div class="table-wrap" style="margin-top:14px;">
                            <table class="data-table" id="setup-grid">
                                <thead><tr id="setup-grid-head"><th>Symbol</th></tr></thead>
                                <tbody id="setup-grid-body"><tr><td class="td-dim">Loading presets...</td></tr></tbody>
                            </table>
                        </div>
                        <div style="margin-top: 14px; display:flex; gap: 12px; align-items:center; flex-wrap:wrap;">
                            <label style="font-size:0.75rem;"><input type="checkbox" id="setup-save-only"> Save only, don't start</label>
                            <button id="setup-create-btn" class="log-btn" disabled style="background:var(--accent-soft); color:var(--accent-bright); border-color:var(--accent);"><i data-lucide="rocket" class="btn-icon"></i> Create instances</button>
                            <button id="setup-cancel-btn" class="log-btn">Close</button>
                        </div>
                        <ul id="setup-results" style="list-style:none; padding:0; margin:12px 0 0; font-size:0.78rem; line-height:1.7;"></ul>
                    </div>
```

- [ ] **Step 4: Add the JavaScript**

In the same file, directly after the `submitBotForm` function (before `document.addEventListener("DOMContentLoaded", () => {` of the Docker section), insert:

```javascript
        // --- Setup Instances (README presets) ---
        const SETUP_NEW_ACCOUNT = "__new__";
        let setupPresets = null;      // {strategies, symbols, cells} from /api/setup/presets
        let setupAccounts = [];       // from /api/ctrader-accounts
        const setupEl = (id) => document.getElementById(id);
        const setupEscape = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

        async function fetchSetupPresets() {
            if (setupPresets) return setupPresets;
            const res = await fetch("/api/setup/presets");
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            setupPresets = await res.json();
            return setupPresets;
        }

        async function fetchCtraderAccounts(selectId = null) {
            try {
                const res = await fetch("/api/ctrader-accounts");
                setupAccounts = (await res.json()).accounts || [];
            } catch (e) { console.error("Error fetching cTrader accounts", e); setupAccounts = []; }
            const sel = setupEl("setup-account");
            let html = `<option value="">— select account —</option>`;
            setupAccounts.forEach(a => {
                html += `<option value="${a.id}">${a.account_type.toUpperCase()} · ${setupEscape(a.label)} (${setupEscape(a.account_number)})</option>`;
            });
            html += `<option value="${SETUP_NEW_ACCOUNT}">＋ New account…</option>`;
            sel.innerHTML = html;
            sel.value = selectId !== null ? String(selectId) : (setupAccounts.length ? "" : SETUP_NEW_ACCOUNT);
            onSetupAccountChange();
        }

        function onSetupAccountChange() {
            const v = setupEl("setup-account").value;
            setupEl("setup-new-account").style.display = v === SETUP_NEW_ACCOUNT ? "block" : "none";
            setupEl("setup-account-delete").style.display = (v && v !== SETUP_NEW_ACCOUNT) ? "inline-flex" : "none";
            updateSetupCreateState();
        }

        function renderSetupGrid(p) {
            const strategies = Object.keys(p.strategies);
            const cellMap = {};
            p.cells.forEach(c => { cellMap[`${c.symbol}|${c.strategy}`] = c; });
            setupEl("setup-grid-head").innerHTML = `<th>Symbol</th>` + strategies.map(s =>
                `<th style="text-align:center"><label style="cursor:pointer; white-space:nowrap;"><input type="checkbox" class="setup-col-all" data-strategy="${s}" title="Select all ${setupEscape(p.strategies[s].label)}"> ${setupEscape(p.strategies[s].label)}</label></th>`
            ).join("");
            setupEl("setup-grid-body").innerHTML = p.symbols.map(sym => {
                const tds = strategies.map(s => {
                    const c = cellMap[`${sym}|${s}`];
                    if (!c) return `<td style="text-align:center" class="td-dim">–</td>`;
                    return `<td style="text-align:center"><input type="checkbox" class="setup-cell" data-symbol="${sym}" data-strategy="${s}" title="${c.period} · ${setupEscape(c.session)}"></td>`;
                }).join("");
                return `<tr><td><strong>${sym}</strong></td>${tds}</tr>`;
            }).join("");
            document.querySelectorAll("#setup-grid .setup-cell").forEach(cb => cb.addEventListener("change", updateSetupCreateState));
            document.querySelectorAll("#setup-grid .setup-col-all").forEach(cb => cb.addEventListener("change", () => {
                document.querySelectorAll(`#setup-grid .setup-cell[data-strategy="${cb.dataset.strategy}"]`).forEach(c => { c.checked = cb.checked; });
                updateSetupCreateState();
            }));
        }

        function selectedSetupCells() {
            return Array.from(document.querySelectorAll("#setup-grid .setup-cell:checked"))
                .map(cb => ({ symbol: cb.dataset.symbol, strategy: cb.dataset.strategy }));
        }

        function updateSetupCreateState() {
            const v = setupEl("setup-account").value;
            setupEl("setup-create-btn").disabled = !(v && v !== SETUP_NEW_ACCOUNT && selectedSetupCells().length > 0);
        }

        async function openSetupPanel() {
            setupEl("bot-form-container").style.display = "none";
            setupEl("setup-panel").style.display = "block";
            setupEl("setup-results").innerHTML = "";
            try {
                renderSetupGrid(await fetchSetupPresets());
            } catch (e) {
                setupEl("setup-grid-body").innerHTML = `<tr><td class="td-dim" style="color:var(--loss)">Failed to load presets: ${setupEscape(e)}</td></tr>`;
            }
            await fetchCtraderAccounts();
        }

        async function saveCtraderAccount() {
            const msg = setupEl("setup-account-msg");
            const body = {
                label: setupEl("setup-acc-label").value.trim(),
                ctid_email: setupEl("setup-acc-email").value.trim(),
                password: setupEl("setup-acc-password").value,
                account_number: setupEl("setup-acc-number").value.trim(),
                account_type: document.querySelector('input[name="setup-acc-type"]:checked').value,
            };
            msg.textContent = "Saving…";
            try {
                const res = await fetch("/api/ctrader-accounts", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
                });
                const data = await res.json();
                if (!res.ok || !data.success) { msg.textContent = data.message || `Error ${res.status}`; return; }
                msg.textContent = "";
                setupEl("setup-acc-password").value = "";
                await fetchCtraderAccounts(data.account.id);
            } catch (e) { msg.textContent = "Error: " + e; }
        }

        async function deleteCtraderAccount() {
            const id = setupEl("setup-account").value;
            const acc = setupAccounts.find(a => String(a.id) === id);
            if (!acc) return;
            if (!confirm(`Delete account "${acc.label}" (${acc.account_number})?\nExisting bot configs keep working; the stored password file is removed.`)) return;
            try {
                const res = await fetch(`/api/ctrader-accounts/${id}`, { method: "DELETE" });
                const data = await res.json();
                if (!data.success) alert(data.message || "Error");
                await fetchCtraderAccounts();
            } catch (e) { alert("Error: " + e); }
        }

        async function createSetupInstances() {
            const btn = setupEl("setup-create-btn");
            const list = setupEl("setup-results");
            const payload = {
                account_id: Number(setupEl("setup-account").value),
                selections: selectedSetupCells(),
                start: !setupEl("setup-save-only").checked,
            };
            btn.disabled = true;
            list.innerHTML = `<li class="td-dim">Creating ${payload.selections.length} instance(s)…</li>`;
            try {
                const res = await fetch("/api/setup/instances", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) { list.innerHTML = `<li style="color:var(--loss)">❌ ${setupEscape(data.message || `HTTP ${res.status}`)}</li>`; return; }
                const icons = { started: "✅", saved: "💾", exists: "⏭", error: "❌" };
                list.innerHTML = (data.results || []).map(r =>
                    `<li>${icons[r.status] || "•"} <strong>${setupEscape(r.name || r.symbol)}</strong> <span class="td-dim">${setupEscape(r.symbol)} · ${setupEscape(r.strategy)}</span> — ${setupEscape(r.message || r.status)}</li>`
                ).join("");
                document.querySelectorAll("#setup-grid input[type=checkbox]:checked").forEach(cb => { cb.checked = false; });
                fetchBots();
            } catch (e) {
                list.innerHTML = `<li style="color:var(--loss)">Error: ${setupEscape(e)}</li>`;
            } finally {
                updateSetupCreateState();
            }
        }
```

Inside the Docker section's `document.addEventListener("DOMContentLoaded", () => { ... })`, add `setupEl("setup-panel").style.display = "none";` as the first line of the existing `add-bot-btn` click handler, and add these listeners before the handler's closing `});`:

```javascript
            setupEl("setup-instances-btn").addEventListener("click", openSetupPanel);
            setupEl("setup-cancel-btn").addEventListener("click", () => { setupEl("setup-panel").style.display = "none"; });
            setupEl("setup-account").addEventListener("change", onSetupAccountChange);
            setupEl("setup-account-save").addEventListener("click", saveCtraderAccount);
            setupEl("setup-account-delete").addEventListener("click", deleteCtraderAccount);
            setupEl("setup-create-btn").addEventListener("click", createSetupInstances);
```

- [ ] **Step 5: README tip**

In `README.md`, in "### 4. Setup & Run cBot" → "#### Option B", immediately before the line `4. **Run Multi-Instance Docker Containers**:`, insert:

```markdown
   > 💡 **Prefer clicking?** Open the dashboard → **Docker Bot Management** → **Setup Instances**. Pick (or create) a cTrader account, tick the symbol × strategy cells you want, and click **Create instances**. The screen generates exactly the commands listed below from the README presets, saves them as bot configs and starts the containers. The cTID password is written to `$CTRADER_HOME/ctrader_data/ctid_<account>_pwd` (mode 0600) and never stored in the database.

```

- [ ] **Step 6: Run the UI test and the whole suite**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py -q` → Expected: `5 passed`.
Run: `.venv/bin/pytest -q` → Expected: `182 passed`.

- [ ] **Step 7: Commit**

```bash
git add templates/dashboard.html README.md tests/test_dashboard_ui.py
git commit -m "feat(ui): Setup Instances panel — pick a cTrader account, tick preset cells, create containers

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Browser smoke test against a throwaway local server

No Docker on the dev machine, so container starts report `Docker not available` — the point of this task is the panel's rendering and the account/config flow end-to-end through the real server. Port 8000 is an SSH tunnel to the user's VPS: **use 8765**, a scratch DB and a scratch `CTRADER_HOME`.

**Files:** none committed (`.claude/launch.json` may be created for `preview_start` and must not be committed).

- [ ] **Step 1: Start the server on 8765 with an isolated DB and CTRADER_HOME**

Create `.claude/launch.json` (do not `git add` it):

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "agentfx-smoke",
      "runtimeExecutable": "bash",
      "runtimeArgs": ["-c", "export AGENTFX_TEST_DB=/tmp/agentfx-smoke/portfolio.db CTRADER_HOME=/tmp/agentfx-smoke/ctrader TESTING=1; mkdir -p /tmp/agentfx-smoke; exec .venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8765"],
      "port": 8765
    }
  ]
}
```

Start it with the browser tool's `preview_start` (`name: agentfx-smoke`) and open `http://127.0.0.1:8765/demo/dashboard`.

- [ ] **Step 2: Walk the flow**

1. Click the Docker icon in the top bar → click **Setup Instances**. Expected: the panel shows, the grid has 15 rows × 3 strategy columns with checkboxes only on the 22 preset cells, the account select shows "＋ New account…" and the new-account inputs are visible (no accounts yet).
2. Fill Label `Smoke Demo`, email `smoke@example.com`, password `pw-smoke`, number `10101649`, Demo → **Save account**. Expected: select now shows `DEMO · Smoke Demo (10101649)` selected, 🗑 visible, inputs hidden; `/tmp/agentfx-smoke/ctrader/ctrader_data/ctid_demo-smoke-demo_pwd` exists with mode 0600 and content `pw-smoke` (check from Bash).
3. Tick XAUUSD/TMS+ORB and EURUSD/FlowRSI, tick **Save only**, click **Create instances**. Expected: two 💾 lines, and the bots table below lists `cbot-demo-smoke-demo-xauusd` and `cbot-demo-smoke-demo-eurusd-flowrsi` as DEMO with the generated command.
4. Untick **Save only**, tick GBPUSD/Judas, click **Create instances**. Expected: one ❌ line with `Docker not available` (no Docker locally), and the config still appears in the table.
5. Re-tick XAUUSD/TMS+ORB and create again. Expected: ⏭ `Bot config already exists`.
6. Click 🗑 → confirm. Expected: account gone from the select, password file removed; bot configs remain in the table.
7. Read the browser console: no JS errors.

- [ ] **Step 3: Stop the server and clean up**

Stop the preview server; `rm -rf /tmp/agentfx-smoke`; make sure `git status` shows no stray files (`.claude/launch.json` may stay untracked — do not commit it). Fix anything found with a `fix(setup): ...` commit, re-running `.venv/bin/pytest -q` first.

---

## Self-review notes

- **Spec coverage:** data model (T2), password file rules (T3), `accounts` side effect (T3 via `upsert_configured_account`), presets + matrix + builder (T1), all five endpoints (T3, T4), per-selection statuses and description string (T4), UI panel with account row / grid / footer / results (T5), error handling codes (T3, T4), all four test files (T1–T5). Out-of-scope items untouched.
- **Deviations from the spec, on purpose:** (1) `POST /api/setup/instances` returns `404` for an unknown `account_id` rather than 200; (2) demo labels containing "live" are rejected so `/api/bots`' name-based live detection cannot misclassify; (3) the refresh function is `fetchBots()`, the spec's `loadBots()` does not exist; (4) `get_cbot_config` is consulted before `add_cbot_config` because the latter only catches `sqlite3.IntegrityError` (PostgreSQL would raise `psycopg2.IntegrityError`).
- **Type consistency:** `container_name(slug, strategy, symbol)`, `build_run_command(account, strategy, symbol, project_root, ctrader_home, image)`, `describe_cell(strategy, symbol, account_label)` used identically in T1 tests, T4 routes and T4 tests. Registry methods named the same in T2 tests, T3 service and T4 route. `_error` defined in T3, reused in T4. Status vocabulary `started|saved|exists|error` in T4 and the T5 icon map.
