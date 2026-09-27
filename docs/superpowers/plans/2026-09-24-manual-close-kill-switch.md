# Manual Close & Per-Container Kill Switch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close an open position from the dashboard's Active Positions table, and Pause/Resume or Close & Stop a container from the Bots tab, with each cBot picking up commands by polling the server every 2 s.

**Architecture:** Two small backend modules: `app/bot_controls.py` (the `bot_controls` pause table, bot-id helpers — same shape as `app/risk_limits.py`) and `app/bot_commands.py` (an in-memory command queue with expiry). Routes live in `app/dashboard.py` next to `/api/bots`. `PortfolioManager` gains the pause cache and a `check_risk` gate. Each of the three cBots gets the same poll loop (`GET /api/cbot/commands`), a close executor that only touches its own positions, and a pause guard in front of every entry order. The UI adds a Close column and three Bots-tab buttons in `templates/dashboard.html`.

**Tech Stack:** FastAPI + pydantic v2, SQLite/PostgreSQL through `app/db.py` (`_adapt_query_for_pg`), vanilla JS in the Jinja template, pytest with `fastapi.testclient.TestClient`, cTrader Automate C# (.NET 6, `cAlgo.API`).

**Spec:** `docs/superpowers/specs/2026-09-24-manual-close-kill-switch-design.md`

## Global Constraints

- **Never commit or push unless the user asks.** Several agent sessions share this checkout: when asked, stage only this plan's files (`git add <files>`), never `git add -A` / `git add .`. Each task ends with a checkpoint, not a commit. `docs/` is gitignored: this plan and the spec stay local.
- Work on branch `feat/manual-close-kill-switch` created from `main` (Task 0).
- Local tests: `.venv/bin/pytest -q -p no:cacheprovider` (baseline before this plan: **548 passed**). Never run anything against port 8000 on the Mac (it tunnels to the VPS) and never touch `portfolio.db`; `tests/conftest.py` redirects the DB to a throwaway SQLite file.
- The poll route `GET /api/cbot/commands` is `async def` and must never touch the DB or Docker (45 containers × 0.5 req/s ≈ 22 req/s on a single uvicorn worker).
- Blocking Docker/DB work in a route runs off the event loop: plain `def` handlers (threadpool), or `await asyncio.to_thread(...)` inside `async def` (see `tests/test_bot_control_api.py`).
- Queue timings (module constants in `app/bot_commands.py`, read at call time so tests can monkeypatch them): `PENDING_TTL_S = 15.0`, `RESULT_TIMEOUT_S = 30.0`, `RETAIN_S = 600.0`, `WAIT_POLL_S = 0.5`, `CLOSE_AND_STOP_WAIT_S = 20.0`.
- Command statuses: `pending`, `delivered`, `done`, `failed`, `expired`, `unconfirmed`. Actions: `close_position` (needs the cTrader `position_id`), `close_all`.
- Pause refusal text (exact): `Paused from dashboard`. Manual close reason in cBots (exact): `Manual close (dashboard)`.
- Every manual action is logged at WARNING with the prefix `[MANUAL]`.
- cBot parameter (exact, each bot's own API group): `[Parameter("Command Poll (ms, 0=off)", Group = "<group>", DefaultValue = 2000, MinValue = 0)] public int CommandPollMs { get; set; }`. The poll runs only when `RunningMode == RunningMode.RealTime`.
- No dotnet on the Mac: cBot tasks are verified by source-reading pytest (project convention) and compiled on the VPS in Task 11.

## File Structure

| File | Responsibility |
|---|---|
| `app/bot_controls.py` (new) | `bot_controls` table (pause), `sanitize_bot_id` (moved from `app/server.py`), `bot_id_for_config` |
| `app/bot_commands.py` (new) | `Command`, `CommandQueue`, `command_queue` singleton, `wait_for_final`, timing constants |
| `app/portfolio.py` | pause cache + `set_bot_paused` / `is_bot_paused`, `check_risk` pause gate, `get_open_position`, `open_position_counts` |
| `app/server.py` | re-export `sanitize_bot_id`; `SkipCommandPollAccessLog` filter on `uvicorn.access` |
| `app/dashboard.py` | poll/result/status routes, close-position route, pause/resume, close-and-stop, `/api/bots` fields, positions payload ids |
| `templates/dashboard.html` | Close column in Active Positions; Pause/Resume, Close & Stop, PAUSED badge in the Bots tab |
| `cBot/AiAgentBot.cs`, `cBot/AsianRangeJudasSweepBot.cs`, `cBot/FlowRsiBot.cs` | command poll, close executor, pause guard |
| `tests/test_bot_controls.py`, `tests/test_bot_commands.py`, `tests/test_manual_close_api.py`, `tests/test_cbot_command_poll.py` (new), `tests/test_dashboard_ui.py` | tests |

---

### Task 0: Branch

- [ ] **Step 1: Create the feature branch**

```bash
git switch main
git status --short          # expect: nothing (or only other sessions' files - leave them alone)
git switch -c feat/manual-close-kill-switch
```

- [ ] **Step 2: Baseline**

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: `548 passed`

---

### Task 1: Pause state (`app/bot_controls.py` + `PortfolioManager`)

**Files:**
- Create: `app/bot_controls.py`
- Modify: `app/portfolio.py` (imports; `__init__`; `_init_db` after `risk_limits.init_schema(conn)`; top of `check_risk`; new methods after `update_risk_limits`)
- Modify: `app/server.py:140-146` (replace the `sanitize_bot_id` definition with an import)
- Test: `tests/test_bot_controls.py`

**Interfaces:**
- Produces:
  - `bot_controls.PAUSED_REASON: str = "Paused from dashboard"`
  - `bot_controls.sanitize_bot_id(bot_id: Optional[str]) -> str`
  - `bot_controls.bot_id_for_config(cfg: Dict) -> str`
  - `bot_controls.init_schema(conn) -> None`, `load_paused(conn) -> Set[str]`, `is_paused(conn, bot_id: str) -> bool`, `save_paused(conn, bot_id: str, paused: bool) -> None` (caller commits)
  - `PortfolioManager.set_bot_paused(bot_id: str, paused: bool) -> None`
  - `PortfolioManager.is_bot_paused(bot_id: str) -> bool` (memory only, never the DB)
  - `check_risk(...)` returns `(False, "Paused from dashboard")` for a paused `bot_id`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_bot_controls.py`:

```python
"""Dashboard pause (Bots tab): a paused bot takes no new entries until Resume.

The pause lives in the bot_controls table so it survives service and container restarts.
check_risk refuses entries for a paused bot_id; the 2 s command poll reads an in-memory copy
(PortfolioManager.is_bot_paused) because it must never touch the DB.
"""
import pytest

from app import bot_controls
from app.portfolio import PortfolioManager

ACCOUNT = "acct-pause"


@pytest.fixture
def pm(tmp_path):
    return PortfolioManager(db_path=str(tmp_path / "pause.db"))


def _check(pm, bot_id):
    return pm.check_risk("EURUSD", None, 0.01, account_balance=2000.0, account_id=ACCOUNT,
                         used_margin=0.0, bot_id=bot_id)


def test_a_paused_bot_is_refused_new_entries(pm):
    pm.set_bot_paused("cbot-a", True)
    assert _check(pm, "cbot-a") == (False, "Paused from dashboard")
    assert _check(pm, "cbot-b") == (True, "OK")


def test_resume_allows_entries_again(pm):
    pm.set_bot_paused("cbot-a", True)
    pm.set_bot_paused("cbot-a", False)
    assert _check(pm, "cbot-a") == (True, "OK")
    assert pm.is_bot_paused("cbot-a") is False


def test_pause_survives_a_restart(tmp_path):
    path = str(tmp_path / "pause.db")
    PortfolioManager(db_path=path).set_bot_paused("cbot-a", True)
    reopened = PortfolioManager(db_path=path)
    assert reopened.is_bot_paused("cbot-a") is True
    assert _check(reopened, "cbot-a")[0] is False


def test_is_bot_paused_never_reads_the_db(pm, monkeypatch):
    pm.set_bot_paused("cbot-a", True)

    def boom():
        raise AssertionError("is_bot_paused must answer from memory")

    monkeypatch.setattr(pm, "_get_conn", boom)
    assert pm.is_bot_paused("cbot-a") is True
    assert pm.is_bot_paused("cbot-b") is False


def test_pausing_twice_keeps_one_row(pm):
    pm.set_bot_paused("cbot-a", True)
    pm.set_bot_paused("cbot-a", True)
    conn = pm._get_conn()
    try:
        assert conn.execute("SELECT COUNT(*) FROM bot_controls WHERE bot_id = 'cbot-a'").fetchone()[0] == 1
    finally:
        conn.close()


def test_check_risk_without_a_bot_id_ignores_pauses(pm):
    pm.set_bot_paused("cbot-a", True)
    assert pm.check_risk("EURUSD", None, 0.01, account_balance=2000.0, account_id=ACCOUNT,
                         used_margin=0.0) == (True, "OK")


@pytest.mark.parametrize("raw, clean", [
    ('"cbot-x"', "cbot-x"),
    ("cbot-x --symbol=EURUSD", "cbot-x"),
    ("", "default"),
    (None, "default"),
])
def test_sanitize_bot_id(raw, clean):
    assert bot_controls.sanitize_bot_id(raw) == clean


def test_server_still_exports_sanitize_bot_id():
    from app.server import sanitize_bot_id
    assert sanitize_bot_id is bot_controls.sanitize_bot_id


@pytest.mark.parametrize("cfg, bot_id", [
    ({"name": "cbot-demo-main-xauusd",
      "run_command": 'docker run -d img run x.algo --BotId="cbot-demo-main-xauusd" --x=1'}, "cbot-demo-main-xauusd"),
    ({"name": "cbot-usdjpy", "run_command": "docker run -d img run x.algo --BotId=usdjpy-tokyo --x=1"}, "usdjpy-tokyo"),
    ({"name": "cbot-handmade", "run_command": "docker run -d img"}, "cbot-handmade"),
])
def test_bot_id_for_config(cfg, bot_id):
    assert bot_controls.bot_id_for_config(cfg) == bot_id
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_bot_controls.py -q -p no:cacheprovider`
Expected: collection error `ImportError: cannot import name 'bot_controls' from 'app'`

- [ ] **Step 3: Create `app/bot_controls.py`**

```python
"""Per-bot entry pause set from the dashboard (Bots tab), and bot identity helpers.

A paused bot takes no new entries until Resume is clicked. It keeps running and keeps managing
the positions it already has (trailing, break-even, SL/TP). The pause is stored in the
bot_controls table so it survives service and container restarts, and it is enforced twice:
PortfolioManager.check_risk refuses entries for a paused bot_id (every /trade entry), and the
bots read the flag from GET /api/cbot/commands and skip their own entry paths, which covers the
ones that never ask the server (UseAiGateMode=false, Judas UseDirectAiApi, Judas DCA adds).
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Set

PAUSED_REASON = "Paused from dashboard"


def sanitize_bot_id(bot_id: Optional[str]) -> str:
    """The bot_id a cBot sent, without the quotes or trailing flags the cTrader CLI can leave on it."""
    if not bot_id:
        return "default"
    cleaned = str(bot_id).strip().strip("\"'“”‘’`")
    if " --" in cleaned:
        cleaned = cleaned.split(" --")[0].strip()
    return cleaned.strip("\"'“”‘’`") or "default"


def bot_id_for_config(cfg: Dict) -> str:
    """The bot_id a container reports: its --BotId flag, else the container name (presets use the name)."""
    # Imported here: cbot_watchdog imports app.portfolio, which imports this module.
    from app.cbot_watchdog import parse_bot_id
    return sanitize_bot_id(parse_bot_id(cfg.get("run_command")) or cfg["name"])


def init_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bot_controls (
            bot_id TEXT PRIMARY KEY,
            paused INTEGER NOT NULL DEFAULT 0,
            paused_at TEXT,
            updated_at TEXT
        )
    """)


def load_paused(conn) -> Set[str]:
    return {row[0] for row in conn.execute("SELECT bot_id FROM bot_controls WHERE paused = 1").fetchall()}


def is_paused(conn, bot_id: str) -> bool:
    row = conn.execute("SELECT paused FROM bot_controls WHERE bot_id = ?", (bot_id,)).fetchone()
    return bool(row and row[0])


def save_paused(conn, bot_id: str, paused: bool) -> None:
    """Upsert the bot's pause flag (SQLite >= 3.24 and PostgreSQL). The caller commits."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO bot_controls (bot_id, paused, paused_at, updated_at) VALUES (?, ?, ?, ?)
        ON CONFLICT(bot_id) DO UPDATE SET
            paused = excluded.paused, paused_at = excluded.paused_at, updated_at = excluded.updated_at
    """, (bot_id, 1 if paused else 0, now if paused else None, now))
```

- [ ] **Step 4: Wire it into `app/portfolio.py`**

Imports — replace:

```python
import logging
from datetime import datetime, date, timezone
from typing import Dict, List, Tuple, Optional
```

with:

```python
import logging
import threading
from datetime import datetime, date, timezone
from typing import Dict, List, Set, Tuple, Optional
```

and replace `from app import risk_limits` with:

```python
from app import bot_controls, risk_limits
```

`__init__` — replace:

```python
        self.db_path = Path(db_path) if db_path else None
        self.config = PortfolioConfig()
        self._init_db()
```

with:

```python
        self.db_path = Path(db_path) if db_path else None
        self.config = PortfolioConfig()
        # Bots paused from the dashboard; a copy of the bot_controls table for the 2 s command
        # poll, which must never touch the DB. Written only by set_bot_paused (single worker).
        self._paused_lock = threading.Lock()
        self._paused_bots: Set[str] = set()
        self._init_db()
```

`_init_db` — replace:

```python
            risk_limits.init_schema(conn)
            conn.commit()
```

with:

```python
            risk_limits.init_schema(conn)
            bot_controls.init_schema(conn)
            conn.commit()
            self._paused_bots = bot_controls.load_paused(conn)
```

`check_risk` — replace:

```python
        conn = self._get_conn()
        try:
            # 1. US Index Correlation / Directional Alignment Check
```

with:

```python
        conn = self._get_conn()
        try:
            # 0. Paused from the dashboard (Bots tab): no new entries until Resume.
            if bot_id and bot_controls.is_paused(conn, bot_id):
                return False, bot_controls.PAUSED_REASON

            # 1. US Index Correlation / Directional Alignment Check
```

New methods — insert right after `update_risk_limits` (before `def get_account_ids`):

```python
    # --- Dashboard pause (app/bot_controls.py) ---

    def set_bot_paused(self, bot_id: str, paused: bool) -> None:
        """Pause or resume a bot's new entries: the table first, then the in-memory copy."""
        conn = self._get_conn()
        try:
            bot_controls.save_paused(conn, bot_id, paused)
            conn.commit()
        finally:
            conn.close()
        with self._paused_lock:
            if paused:
                self._paused_bots.add(bot_id)
            else:
                self._paused_bots.discard(bot_id)

    def is_bot_paused(self, bot_id: str) -> bool:
        """Answered from memory: the command poll calls this ~22 times a second."""
        with self._paused_lock:
            return bot_id in self._paused_bots
```

- [ ] **Step 5: Move `sanitize_bot_id` out of `app/server.py`**

Replace the whole definition at `app/server.py:140-146`:

```python
def sanitize_bot_id(bot_id: Optional[str]) -> str:
    if not bot_id:
        return "default"
    cleaned = str(bot_id).strip().strip("\"'“”‘’`")
    if " --" in cleaned:
        cleaned = cleaned.split(" --")[0].strip()
    return cleaned.strip("\"'“”‘’`") or "default"
```

with:

```python
from app.bot_controls import sanitize_bot_id  # shared with the dashboard's bot-facing routes
```

- [ ] **Step 6: Run the tests**

Run: `.venv/bin/pytest tests/test_bot_controls.py -q -p no:cacheprovider`
Expected: all pass.

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: `548 + new` passed, 0 failed.

- [ ] **Step 7: Checkpoint (no commit)**

`git status --short` lists only `app/bot_controls.py`, `app/portfolio.py`, `app/server.py`, `tests/test_bot_controls.py` from this task.

---

### Task 2: Command queue (`app/bot_commands.py`)

**Files:**
- Create: `app/bot_commands.py`
- Test: `tests/test_bot_commands.py`

**Interfaces:**
- Produces:
  - `Command` dataclass: `id, bot_id, action, position_id, created_at, status, message, closed, failed, delivered_at, finished_at`; `for_bot() -> {"id", "action", "position_id"}`; `for_dashboard() -> {"id", "bot_id", "action", "position_id", "status", "message", "closed", "failed"}`
  - `CommandQueue(clock=time.monotonic)` with `enqueue(bot_id, action, position_id=None) -> Command`, `take_pending(bot_id) -> List[Command]`, `record_result(command_id, bot_id, status, message="", closed=0, failed=0) -> Command`, `get(command_id) -> Optional[Command]`. Every returned `Command` is a copy.
  - Exceptions `CommandNotFound(KeyError)`, `CommandNotOwned(PermissionError)`; `ValueError` for a bad action/status.
  - `async wait_for_final(queue, command_id, timeout_s) -> Optional[Command]`
  - Constants `PENDING_TTL_S, RESULT_TIMEOUT_S, RETAIN_S, WAIT_POLL_S, CLOSE_AND_STOP_WAIT_S, ACTIONS, FINAL_STATUSES`
  - Singleton `command_queue = CommandQueue()`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_bot_commands.py`:

```python
"""The dashboard's command queue for cBots (app/bot_commands.py).

Each bot polls every 2 s. A command it has not picked up within 15 s expires and is never
handed out afterwards, so a bot that restarts later cannot act on a stale close.
"""
import asyncio

import pytest

from app import bot_commands
from app.bot_commands import CommandNotFound, CommandNotOwned, CommandQueue


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def queue(clock):
    return CommandQueue(clock=clock)


def test_a_command_is_handed_out_once(queue):
    cmd = queue.enqueue("bot-a", "close_position", 111)
    taken = queue.take_pending("bot-a")
    assert [c.id for c in taken] == [cmd.id]
    assert taken[0].for_bot() == {"id": cmd.id, "action": "close_position", "position_id": 111}
    assert queue.take_pending("bot-a") == []
    assert queue.get(cmd.id).status == "delivered"


def test_commands_go_only_to_their_bot(queue):
    queue.enqueue("bot-a", "close_all")
    assert queue.take_pending("bot-b") == []
    assert len(queue.take_pending("bot-a")) == 1


def test_an_unpolled_command_expires_and_is_never_delivered(queue, clock):
    cmd = queue.enqueue("bot-a", "close_all")
    clock.now += bot_commands.PENDING_TTL_S + 0.1
    assert queue.get(cmd.id).status == "expired"
    assert queue.take_pending("bot-a") == []      # a bot restarting later must not close anything


def test_a_delivered_command_without_a_result_becomes_unconfirmed(queue, clock):
    cmd = queue.enqueue("bot-a", "close_all")
    queue.take_pending("bot-a")
    clock.now += bot_commands.RESULT_TIMEOUT_S + 0.1
    assert queue.get(cmd.id).status == "unconfirmed"


def test_the_bot_reports_the_result(queue):
    cmd = queue.enqueue("bot-a", "close_all")
    queue.take_pending("bot-a")
    queue.record_result(cmd.id, "bot-a", "done", "closed 2", closed=2, failed=0)
    got = queue.get(cmd.id)
    assert (got.status, got.message, got.closed, got.failed) == ("done", "closed 2", 2, 0)
    assert got.for_dashboard()["status"] == "done"


def test_bad_results_are_refused(queue):
    cmd = queue.enqueue("bot-a", "close_all")
    with pytest.raises(CommandNotOwned):
        queue.record_result(cmd.id, "bot-b", "done")
    with pytest.raises(CommandNotFound):
        queue.record_result("nope", "bot-a", "done")
    with pytest.raises(ValueError):
        queue.record_result(cmd.id, "bot-a", "maybe")


def test_a_double_click_returns_the_same_command(queue):
    first = queue.enqueue("bot-a", "close_position", 111)
    assert queue.enqueue("bot-a", "close_position", 111).id == first.id
    assert queue.enqueue("bot-a", "close_position", 222).id != first.id
    queue.take_pending("bot-a")
    assert queue.enqueue("bot-a", "close_position", 111).id == first.id   # delivered, not finished yet


def test_a_finished_command_can_be_sent_again(queue):
    first = queue.enqueue("bot-a", "close_all")
    queue.take_pending("bot-a")
    queue.record_result(first.id, "bot-a", "failed", "MarketClosed")
    assert queue.enqueue("bot-a", "close_all").id != first.id


def test_finished_commands_are_purged_after_ten_minutes(queue, clock):
    old = queue.enqueue("bot-a", "close_all")
    queue.take_pending("bot-a")
    queue.record_result(old.id, "bot-a", "done")
    clock.now += bot_commands.RETAIN_S + 1
    queue.enqueue("bot-b", "close_all")           # enqueue purges
    assert queue.get(old.id) is None


@pytest.mark.parametrize("action, position_id", [("reboot", None), ("close_position", None)])
def test_invalid_commands_are_refused(queue, action, position_id):
    with pytest.raises(ValueError):
        queue.enqueue("bot-a", action, position_id)


def test_returned_commands_are_copies(queue):
    cmd = queue.enqueue("bot-a", "close_all")
    cmd.status = "done"
    assert queue.get(cmd.id).status == "pending"


def test_wait_for_final_returns_once_the_bot_reports(monkeypatch):
    monkeypatch.setattr(bot_commands, "WAIT_POLL_S", 0.01)
    queue = CommandQueue()
    cmd = queue.enqueue("bot-a", "close_all")

    async def scenario():
        async def bot():
            await asyncio.sleep(0.05)
            queue.take_pending("bot-a")
            queue.record_result(cmd.id, "bot-a", "done", closed=1)

        task = asyncio.create_task(bot())
        final = await bot_commands.wait_for_final(queue, cmd.id, timeout_s=2.0)
        await task
        return final

    final = asyncio.run(scenario())
    assert final.status == "done" and final.closed == 1


def test_wait_for_final_gives_up_at_the_timeout(monkeypatch):
    monkeypatch.setattr(bot_commands, "WAIT_POLL_S", 0.01)
    queue = CommandQueue()
    cmd = queue.enqueue("bot-a", "close_all")
    final = asyncio.run(bot_commands.wait_for_final(queue, cmd.id, timeout_s=0.05))
    assert final.status == "pending"
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_bot_commands.py -q -p no:cacheprovider`
Expected: collection error `ImportError: cannot import name 'bot_commands' from 'app'`

- [ ] **Step 3: Create `app/bot_commands.py`**

```python
"""Commands the dashboard sends to a cBot: close one position, or close all of the bot's positions.

The server cannot reach a cBot, so each bot polls GET /api/cbot/commands every 2 s (its
CommandPollMs) and reports back on POST /api/cbot/commands/{id}/result. The queue lives in this
process's memory because the poll route runs ~22 times a second with 45 containers and must never
touch the DB. That relies on the single-worker service (`uvicorn app.server:app`, no --workers).

    pending --(bot polls)--> delivered --(bot reports)--> done | failed
       |                         |
       +- not polled in 15 s --> expired      +- no report in 30 s --> unconfirmed

An expired command is never handed out: a bot that restarts hours later must not act on a stale
close. The bot also skips command ids it has already run.
"""

import asyncio
import threading
import time
import uuid
from dataclasses import dataclass, replace
from typing import Callable, Dict, List, Optional

PENDING_TTL_S = 15.0          # not polled by then -> expired, never delivered
RESULT_TIMEOUT_S = 30.0       # delivered but no report by then -> unconfirmed
RETAIN_S = 600.0              # finished commands stay readable for the dashboard this long
WAIT_POLL_S = 0.5             # wait_for_final's polling interval
CLOSE_AND_STOP_WAIT_S = 20.0  # how long Close & Stop waits for the bot's close_all result

ACTIONS = ("close_position", "close_all")
FINAL_STATUSES = ("done", "failed", "expired", "unconfirmed")


class CommandNotFound(KeyError):
    pass


class CommandNotOwned(PermissionError):
    pass


@dataclass
class Command:
    id: str
    bot_id: str
    action: str
    position_id: Optional[int]
    created_at: float
    status: str = "pending"
    message: str = ""
    closed: int = 0
    failed: int = 0
    delivered_at: Optional[float] = None
    finished_at: Optional[float] = None

    def for_bot(self) -> Dict:
        return {"id": self.id, "action": self.action, "position_id": self.position_id}

    def for_dashboard(self) -> Dict:
        return {"id": self.id, "bot_id": self.bot_id, "action": self.action,
                "position_id": self.position_id, "status": self.status, "message": self.message,
                "closed": self.closed, "failed": self.failed}


class CommandQueue:
    """Thread-safe: the poll route runs on the event loop, dashboard routes in the threadpool."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._commands: Dict[str, Command] = {}

    def enqueue(self, bot_id: str, action: str, position_id: Optional[int] = None) -> Command:
        """Queue a command; the same one still in flight (a double click) is returned instead."""
        if action not in ACTIONS:
            raise ValueError(f"unknown action {action!r}")
        if action == "close_position" and position_id is None:
            raise ValueError("close_position needs a position_id")
        with self._lock:
            now = self._clock()
            self._age_all(now)
            for cmd in self._commands.values():
                if (cmd.bot_id == bot_id and cmd.action == action and cmd.position_id == position_id
                        and cmd.status in ("pending", "delivered")):
                    return replace(cmd)
            cmd = Command(id=uuid.uuid4().hex, bot_id=bot_id, action=action,
                          position_id=position_id, created_at=now)
            self._commands[cmd.id] = cmd
            return replace(cmd)

    def take_pending(self, bot_id: str) -> List[Command]:
        """The bot's pending commands, marked delivered: each is handed out once."""
        with self._lock:
            now = self._clock()
            taken = []
            for cmd in self._commands.values():
                if cmd.bot_id != bot_id:
                    continue
                self._age(cmd, now)
                if cmd.status == "pending":
                    cmd.status = "delivered"
                    cmd.delivered_at = now
                    taken.append(replace(cmd))
            return taken

    def record_result(self, command_id: str, bot_id: str, status: str, message: str = "",
                      closed: int = 0, failed: int = 0) -> Command:
        if status not in ("done", "failed"):
            raise ValueError(f"status must be 'done' or 'failed', not {status!r}")
        with self._lock:
            cmd = self._commands.get(command_id)
            if cmd is None:
                raise CommandNotFound(command_id)
            if cmd.bot_id != bot_id:
                raise CommandNotOwned(command_id)
            cmd.status = status
            cmd.message = message or ""
            cmd.closed = int(closed)
            cmd.failed = int(failed)
            cmd.finished_at = self._clock()
            return replace(cmd)

    def get(self, command_id: str) -> Optional[Command]:
        with self._lock:
            cmd = self._commands.get(command_id)
            if cmd is None:
                return None
            self._age(cmd, self._clock())
            return replace(cmd)

    # Module constants are read at call time so tests can shorten them.
    def _age(self, cmd: Command, now: float) -> None:
        if cmd.status == "pending" and now - cmd.created_at > PENDING_TTL_S:
            cmd.status = "expired"
            cmd.finished_at = now
            cmd.message = f"the bot did not pick up the command within {PENDING_TTL_S:.0f} s"
        elif cmd.status == "delivered" and now - (cmd.delivered_at or now) > RESULT_TIMEOUT_S:
            cmd.status = "unconfirmed"
            cmd.finished_at = now
            cmd.message = "the bot received the command but did not report a result"

    def _age_all(self, now: float) -> None:
        for command_id in list(self._commands):
            cmd = self._commands[command_id]
            self._age(cmd, now)
            if cmd.finished_at is not None and now - cmd.finished_at > RETAIN_S:
                del self._commands[command_id]


async def wait_for_final(queue: CommandQueue, command_id: str, timeout_s: float) -> Optional[Command]:
    """Poll `queue` until the command is final or `timeout_s` has passed; the latest copy either way."""
    deadline = time.monotonic() + timeout_s
    while True:
        cmd = queue.get(command_id)
        if cmd is None or cmd.status in FINAL_STATUSES or time.monotonic() >= deadline:
            return cmd
        await asyncio.sleep(WAIT_POLL_S)


command_queue = CommandQueue()
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/pytest tests/test_bot_commands.py -q -p no:cacheprovider`
Expected: all pass.

- [ ] **Step 5: Checkpoint (no commit)**

New files only: `app/bot_commands.py`, `tests/test_bot_commands.py`.

---

### Task 3: Bot-facing routes, command status, access-log filter

**Files:**
- Modify: `app/dashboard.py` (new section right after `api_restart_bot`, ~line 1152)
- Modify: `app/server.py` (after `logger = logging.getLogger("AgentFxTrading")`, ~line 136)
- Test: `tests/test_manual_close_api.py` (new; extended in Tasks 4 and 5)

**Interfaces:**
- Consumes: `command_queue`, `CommandNotFound`, `CommandNotOwned` (Task 2); `sanitize_bot_id`, `PortfolioManager.is_bot_paused` (Task 1); `_error(status, message)` already in `app/dashboard.py` (defined further down the module, resolved at call time).
- Produces:
  - `GET /api/cbot/commands?bot_id=X` → `{"paused": bool, "commands": [{"id", "action", "position_id"}]}` (handler `api_cbot_poll_commands`, `async def`)
  - `POST /api/cbot/commands/{command_id}/result` body `{"bot_id", "status", "message", "closed", "failed"}` → `{"ok": true}` | 404 | 409 | 422
  - `GET /api/bot-commands/{command_id}` → `Command.for_dashboard()` | 404
  - `app.server.SkipCommandPollAccessLog` attached to `logging.getLogger("uvicorn.access")`
  - Routes use the module-level name `command_queue` in `app/dashboard.py` (tests monkeypatch it).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_manual_close_api.py`:

```python
"""Manual close, Pause/Resume and Close & Stop from the dashboard (spec 2026-09-24).

cBots cannot be reached by the server, so each one polls GET /api/cbot/commands every 2 s and
reports on POST /api/cbot/commands/{id}/result. The poll must stay in memory: with 45 containers
it runs ~22 times a second on a single uvicorn worker.
"""
import inspect
import logging

import pytest
from fastapi.testclient import TestClient

from app.server import app
import app.dashboard as dashboard_module
from app.bot_commands import CommandQueue
from app.portfolio import get_portfolio_manager

client = TestClient(app)
NAME = "cbot-test-manual-xauusd"


@pytest.fixture(autouse=True)
def queue(monkeypatch):
    """A fresh queue per test, so commands left by one test never reach the next."""
    q = CommandQueue()
    monkeypatch.setattr(dashboard_module, "command_queue", q)
    return q


def _poll(bot_id):
    return client.get("/api/cbot/commands", params={"bot_id": bot_id}).json()


# --- bot-facing: poll + result ------------------------------------------------------------------

def test_poll_returns_the_pause_flag_and_pending_commands(queue):
    cmd = queue.enqueue("cbot-test-poll-1", "close_position", 4242)
    assert _poll("cbot-test-poll-1") == {
        "paused": False,
        "commands": [{"id": cmd.id, "action": "close_position", "position_id": 4242}],
    }
    assert _poll("cbot-test-poll-1")["commands"] == []


def test_poll_strips_quotes_the_ctrader_cli_leaves_on_bot_id(queue):
    queue.enqueue("cbot-test-poll-2", "close_all")
    assert len(_poll('"cbot-test-poll-2"')["commands"]) == 1


def test_poll_never_touches_the_db_or_docker(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("the 2 s poll must stay in memory")

    monkeypatch.setattr(get_portfolio_manager(), "_get_conn", boom)
    monkeypatch.setattr(dashboard_module, "get_db", boom)
    monkeypatch.setattr(dashboard_module, "docker_manager", None)
    r = client.get("/api/cbot/commands", params={"bot_id": "cbot-test-poll-3"})
    assert r.status_code == 200
    assert inspect.iscoroutinefunction(dashboard_module.api_cbot_poll_commands)


def test_the_bot_reports_a_result(queue):
    cmd = queue.enqueue("cbot-test-result-1", "close_all")
    queue.take_pending("cbot-test-result-1")
    r = client.post(f"/api/cbot/commands/{cmd.id}/result",
                    json={"bot_id": "cbot-test-result-1", "status": "done", "message": "closed 1",
                          "closed": 1, "failed": 0})
    assert r.status_code == 200 and r.json() == {"ok": True}
    status = client.get(f"/api/bot-commands/{cmd.id}").json()
    assert status["status"] == "done" and status["closed"] == 1


@pytest.mark.parametrize("payload, code", [
    ({"bot_id": "someone-else", "status": "done"}, 409),
    ({"bot_id": "cbot-test-result-2", "status": "maybe"}, 422),
])
def test_bad_results_are_refused(queue, payload, code):
    cmd = queue.enqueue("cbot-test-result-2", "close_all")
    assert client.post(f"/api/cbot/commands/{cmd.id}/result", json=payload).status_code == code


def test_unknown_commands_are_404():
    assert client.post("/api/cbot/commands/nope/result",
                       json={"bot_id": "x", "status": "done"}).status_code == 404
    assert client.get("/api/bot-commands/nope").status_code == 404


# --- access log ---------------------------------------------------------------------------------

def _access_record(method, path):
    return logging.LogRecord("uvicorn.access", logging.INFO, __file__, 1, '%s - "%s %s HTTP/%s" %d',
                             ("127.0.0.1:50000", method, path, "1.1", 200), None)


def test_access_log_drops_only_the_command_poll():
    from app.server import SkipCommandPollAccessLog
    f = SkipCommandPollAccessLog()
    assert f.filter(_access_record("GET", "/api/cbot/commands?bot_id=cbot-x")) is False
    assert f.filter(_access_record("POST", "/api/cbot/commands/abc/result")) is True
    assert f.filter(_access_record("GET", "/api/bots")) is True
    assert any(isinstance(x, SkipCommandPollAccessLog) for x in logging.getLogger("uvicorn.access").filters)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_manual_close_api.py -q -p no:cacheprovider`
Expected: FAIL — `AttributeError: module 'app.dashboard' has no attribute 'command_queue'` (autouse fixture) on every test.

- [ ] **Step 3: Add the routes to `app/dashboard.py`**

Insert right after the `api_restart_bot` function (the one ending `return result` under `@router.post("/api/bots/{name}/restart")`):

```python

# --- Dashboard -> cBot commands: manual close, pause, Close & Stop (spec 2026-09-24) ---
# The server cannot reach a cBot: each bot polls GET /api/cbot/commands every 2 s and reports on
# POST /api/cbot/commands/{id}/result. See app/bot_commands.py and app/bot_controls.py.
from app import bot_commands
from app.bot_commands import command_queue, CommandNotFound, CommandNotOwned
from app.bot_controls import bot_id_for_config, sanitize_bot_id


class CommandResultRequest(BaseModel):
    bot_id: str
    status: str
    message: str = ""
    closed: int = 0
    failed: int = 0


@router.get("/api/cbot/commands")
async def api_cbot_poll_commands(bot_id: str):
    """Polled by every cBot every 2 s: its pause flag and its pending commands.

    `async def` and memory-only on purpose: 45 containers make ~22 calls a second, and a DB read
    here (the old HTTP /api/tick cost ~86 ms a call) would saturate the single uvicorn worker.
    """
    bot_id = sanitize_bot_id(bot_id)
    return {
        "paused": get_portfolio_manager().is_bot_paused(bot_id),
        "commands": [cmd.for_bot() for cmd in command_queue.take_pending(bot_id)],
    }


@router.post("/api/cbot/commands/{command_id}/result")
async def api_cbot_command_result(command_id: str, req: CommandResultRequest):
    """A cBot reports what came of a command it polled."""
    if req.status not in ("done", "failed"):
        return _error(422, "status must be 'done' or 'failed'")
    try:
        cmd = command_queue.record_result(command_id, sanitize_bot_id(req.bot_id), req.status,
                                          req.message, req.closed, req.failed)
    except CommandNotFound:
        return _error(404, "Unknown command")
    except CommandNotOwned:
        return _error(409, "The command belongs to another bot")
    log = logger.warning if cmd.status == "failed" else logger.info
    log(f"[MANUAL] {cmd.bot_id} {cmd.action} {cmd.id[:8]}: {cmd.status} ({cmd.message})")
    return {"ok": True}


@router.get("/api/bot-commands/{command_id}")
async def api_get_bot_command(command_id: str):
    """Status of a command, polled by the dashboard after a Close click."""
    cmd = command_queue.get(command_id)
    if cmd is None:
        return _error(404, "Unknown command")
    return cmd.for_dashboard()
```

- [ ] **Step 4: Add the access-log filter to `app/server.py`**

Insert right after `logger = logging.getLogger("AgentFxTrading")` (the line following `setup_agent_logging(logging.INFO)`):

```python


class SkipCommandPollAccessLog(logging.Filter):
    """Drop uvicorn's access line for the cBots' command poll (GET /api/cbot/commands).

    45 containers poll every 2 s: ~22 lines a second, ~1.9 M a day in journald, none of them
    telling anything. Their result POSTs and every other route are still logged. uvicorn
    configures its loggers before importing the app and dictConfig keeps existing filters.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3 and args[1] == "GET" \
                and str(args[2]).startswith("/api/cbot/commands"):
            return False
        return True


logging.getLogger("uvicorn.access").addFilter(SkipCommandPollAccessLog())
```

- [ ] **Step 5: Run the tests**

Run: `.venv/bin/pytest tests/test_manual_close_api.py -q -p no:cacheprovider`
Expected: all pass.

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 6: Checkpoint (no commit)**

---

### Task 4: Close one position

**Files:**
- Modify: `app/portfolio.py` (new method after `is_bot_paused`)
- Modify: `app/dashboard.py:289-290` (`get_active_positions` SELECT) and the Task 3 section (new route)
- Test: `tests/test_manual_close_api.py` (append)

**Interfaces:**
- Consumes: `command_queue`, `bot_id_for_config`, `_error`, `docker_manager` (module global in `app/dashboard.py`).
- Produces:
  - `PortfolioManager.get_open_position(position_id: int) -> Optional[Dict]` with keys `id, bot_id, symbol, side, volume, account_id, ctrader_id`
  - `_config_for_bot(pm, bot_id) -> Optional[Dict]` in `app/dashboard.py`
  - `POST /api/positions/{position_id}/close` (handler `api_close_position`, plain `def`) → `{"success": true, "command_id", "status"}` | 404 | 409
  - `/api/dashboard/positions` rows (and the server-rendered rows) carry `id` and `ctrader_id`

- [ ] **Step 1: Append the failing tests to `tests/test_manual_close_api.py`**

```python


# --- close one position -------------------------------------------------------------------------

ACCOUNT = "acct-manual"


class FakeDocker:
    def __init__(self):
        self.calls = []
        self.is_available = True
        self.status = "running"
        self.stop_ok = True

    def get_container_status(self, name):
        self.calls.append(("status", name))
        return {"status": self.status, "id": "abc123def456"}

    def stop_container(self, name):
        self.calls.append(("stop", name))
        return {"success": self.stop_ok, "message": "stopped" if self.stop_ok else "docker down"}


@pytest.fixture
def fake_docker(monkeypatch):
    fake = FakeDocker()
    monkeypatch.setattr(dashboard_module, "docker_manager", fake)
    return fake


@pytest.fixture
def bot_config():
    pm = get_portfolio_manager()
    pm.delete_cbot_config(NAME)
    assert pm.add_cbot_config(NAME, "manual close test",
                              f'docker run -d --name {NAME} img run /workspace/cBot/AiAgentBot.algo --BotId="{NAME}"')
    yield NAME
    pm.delete_cbot_config(NAME)
    pm.set_bot_paused(NAME, False)


@pytest.fixture
def cleanup_positions():
    yield
    conn = get_portfolio_manager()._get_conn()
    try:
        conn.execute("DELETE FROM positions WHERE account_id = ?", (ACCOUNT,))
        conn.commit()
    finally:
        conn.close()


def _open_position(ctrader_id=None, bot_id=NAME):
    pm = get_portfolio_manager()
    assert pm.register_position(bot_id=bot_id, symbol="XAUUSD", side="Buy", volume=0.1, entry_price=2000.0,
                                sl_pips=100, tp_pips=200, account_id=ACCOUNT, ctrader_id=ctrader_id)
    conn = pm._get_conn()
    try:
        return conn.execute("SELECT MAX(id) FROM positions WHERE bot_id = ? AND status = 'open'",
                            (bot_id,)).fetchone()[0]
    finally:
        conn.close()


def test_positions_payload_carries_the_row_and_ctrader_ids(cleanup_positions):
    row_id = _open_position(ctrader_id=900001)
    rows = client.get("/api/dashboard/positions", params={"account_id": ACCOUNT}).json()
    row = next(p for p in rows if p["id"] == row_id)
    assert row["ctrader_id"] == 900001


def test_close_queues_a_close_for_that_bot(fake_docker, bot_config, cleanup_positions):
    row_id = _open_position(ctrader_id=900002)
    r = client.post(f"/api/positions/{row_id}/close")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True and body["status"] == "pending"
    assert _poll(NAME)["commands"] == [{"id": body["command_id"], "action": "close_position",
                                        "position_id": 900002}]


def test_close_twice_returns_the_same_command(fake_docker, bot_config, cleanup_positions):
    row_id = _open_position(ctrader_id=900003)
    first = client.post(f"/api/positions/{row_id}/close").json()["command_id"]
    assert client.post(f"/api/positions/{row_id}/close").json()["command_id"] == first


def test_close_unknown_position_is_404(fake_docker):
    assert client.post("/api/positions/99999999/close").status_code == 404


def test_close_without_a_ctrader_id_is_refused(fake_docker, bot_config, cleanup_positions):
    row_id = _open_position(ctrader_id=None)
    r = client.post(f"/api/positions/{row_id}/close")
    assert r.status_code == 409 and "cTrader" in r.json()["message"]


def test_close_is_refused_when_the_container_is_down(fake_docker, bot_config, cleanup_positions):
    fake_docker.status = "exited"
    row_id = _open_position(ctrader_id=900004)
    r = client.post(f"/api/positions/{row_id}/close")
    assert r.status_code == 409 and "exited" in r.json()["message"]
    assert _poll(NAME)["commands"] == []


def test_close_position_handler_runs_off_the_event_loop():
    assert not inspect.iscoroutinefunction(dashboard_module.api_close_position)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_manual_close_api.py -q -p no:cacheprovider`
Expected: the new tests FAIL (`KeyError: 'id'` / 404 from an unknown route / `AttributeError: ... api_close_position`).

- [ ] **Step 3: Add `get_open_position` to `app/portfolio.py`**

Insert right after `is_bot_paused` (Task 1):

```python

    def get_open_position(self, position_id: int) -> Optional[Dict]:
        """One open position by its row id (the dashboard's Close button), or None."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT id, bot_id, symbol, side, volume, account_id, ctrader_id FROM positions "
                "WHERE id = ? AND status = 'open'", (position_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
```

- [ ] **Step 4: Add the row ids to the positions payload**

In `get_active_positions` (`app/dashboard.py`), replace:

```python
            SELECT p.bot_id, p.symbol, UPPER(p.side) as side, p.volume, p.entry_price, p.sl_pips, p.tp_pips, p.entry_time,
```

with:

```python
            SELECT p.id, p.ctrader_id, p.bot_id, p.symbol, UPPER(p.side) as side, p.volume, p.entry_price, p.sl_pips, p.tp_pips, p.entry_time,
```

- [ ] **Step 5: Add the route**

Append to the Task 3 section in `app/dashboard.py` (after `api_get_bot_command`):

```python


def _config_for_bot(pm, bot_id: str) -> Optional[Dict]:
    """The cbot_configs row whose container reports `bot_id`, or None."""
    return next((cfg for cfg in pm.get_cbot_configs() if bot_id_for_config(cfg) == bot_id), None)


@router.post("/api/positions/{position_id}/close")
def api_close_position(position_id: int):
    """Ask the position's bot to close it at market (Close button in Active Positions)."""
    pm = get_portfolio_manager()
    pos = pm.get_open_position(position_id)
    if not pos:
        return _error(404, "Position not found or already closed")
    if pos.get("ctrader_id") is None:
        return _error(409, "This position has no cTrader id recorded; close it in cTrader")
    cfg = _config_for_bot(pm, pos["bot_id"])
    if cfg:
        status = docker_manager.get_container_status(cfg["name"]).get("status")
        if status != "running":
            return _error(409, f"Container {cfg['name']} is {status}; close the position in cTrader")
    cmd = command_queue.enqueue(pos["bot_id"], "close_position", int(pos["ctrader_id"]))
    logger.warning(f"[MANUAL] Close requested from the dashboard: {pos['side']} {pos['symbol']} "
                   f"{pos['volume']}L #{pos['ctrader_id']} of {pos['bot_id']} (command {cmd.id[:8]})")
    return {"success": True, "command_id": cmd.id, "status": cmd.status}
```

- [ ] **Step 6: Run the tests**

Run: `.venv/bin/pytest tests/test_manual_close_api.py -q -p no:cacheprovider`
Expected: all pass.

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 7: Checkpoint (no commit)**

---

### Task 5: Container controls — Pause/Resume, Close & Stop, `/api/bots` fields

**Files:**
- Modify: `app/portfolio.py` (new method after `get_open_position`)
- Modify: `app/dashboard.py` (`api_get_bots`; new routes appended to the Task 3 section)
- Test: `tests/test_manual_close_api.py` (append)

**Interfaces:**
- Consumes: `set_bot_paused`, `is_bot_paused`, `bot_id_for_config` (Task 1); `command_queue`, `bot_commands.wait_for_final`, `bot_commands.CLOSE_AND_STOP_WAIT_S` (Task 2). These routes look the config up by container name (`pm.get_cbot_config(name)`).
- Produces:
  - `PortfolioManager.open_position_counts() -> Dict[str, int]` (bot_id → open rows)
  - `POST /api/bots/{name}/pause` / `/resume` (plain `def`: `api_pause_bot`, `api_resume_bot`) → `{"success", "bot_id", "paused", "message"}` | 404
  - `POST /api/bots/{name}/close-and-stop` (`async def api_close_and_stop_bot`) → success `{"success": true, "closed", "paused": true, "message"}`; failure `{"success": false, "stage": "close"|"stop", "paused": true, "message"}`; 404; 409 when the container is not running
  - `/api/bots` entries gain `bot_id`, `paused`, `open_positions`

- [ ] **Step 1: Append the failing tests to `tests/test_manual_close_api.py`**

First extend the imports at the top of the file — replace:

```python
import inspect
import logging

import pytest
```

with:

```python
import inspect
import logging
import threading
import time

import pytest
```

and replace:

```python
from app.bot_commands import CommandQueue
```

with:

```python
from app import bot_commands
from app.bot_commands import CommandQueue
```

Then append:

```python


# --- container controls -------------------------------------------------------------------------

def _bot(name):
    return next(b for b in client.get("/api/bots").json()["bots"] if b["name"] == name)


def test_pause_and_resume_a_container(fake_docker, bot_config):
    r = client.post(f"/api/bots/{NAME}/pause").json()
    assert r["success"] is True and r["paused"] is True and r["bot_id"] == NAME
    assert _poll(NAME)["paused"] is True
    assert get_portfolio_manager().check_risk("XAUUSD", None, 0.01, account_balance=5000.0,
                                              account_id=ACCOUNT, used_margin=0.0,
                                              bot_id=NAME) == (False, "Paused from dashboard")
    assert client.post(f"/api/bots/{NAME}/resume").json()["paused"] is False
    assert _poll(NAME)["paused"] is False


def test_pause_unknown_bot_is_404(fake_docker):
    assert client.post("/api/bots/cbot-does-not-exist/pause").status_code == 404


def test_pause_and_resume_handlers_run_off_the_event_loop():
    for handler in (dashboard_module.api_pause_bot, dashboard_module.api_resume_bot):
        assert not inspect.iscoroutinefunction(handler), handler.__name__


def test_bots_list_shows_pause_and_open_positions(fake_docker, bot_config, cleanup_positions, monkeypatch):
    from app.cbot_watchdog import cbot_watchdog
    monkeypatch.setattr(cbot_watchdog, "last_health", lambda name: None)
    _open_position(ctrader_id=900010)
    _open_position(ctrader_id=900011)
    client.post(f"/api/bots/{NAME}/pause")
    bot = _bot(NAME)
    assert bot["bot_id"] == NAME and bot["paused"] is True and bot["open_positions"] == 2


class BotThread:
    """Stands in for the cBot: polls the queue and answers every command it is handed."""

    def __init__(self, queue, status="done", closed=2, failed=0):
        self.queue, self.status, self.closed, self.failed = queue, status, closed, failed
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            for cmd in self.queue.take_pending(NAME):
                message = "broker says no" if self.status == "failed" else f"closed {self.closed}"
                self.queue.record_result(cmd.id, NAME, self.status, message, self.closed, self.failed)
            time.sleep(0.02)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(1)


@pytest.fixture
def fast_waits(monkeypatch):
    monkeypatch.setattr(bot_commands, "WAIT_POLL_S", 0.02)
    monkeypatch.setattr(bot_commands, "CLOSE_AND_STOP_WAIT_S", 1.0)


def test_close_and_stop_closes_then_stops(fake_docker, bot_config, fast_waits, queue):
    with BotThread(queue, status="done", closed=2):
        body = client.post(f"/api/bots/{NAME}/close-and-stop").json()
    assert body["success"] is True and body["closed"] == 2, body
    assert ("stop", NAME) in fake_docker.calls
    assert get_portfolio_manager().is_bot_paused(NAME) is True      # stays paused until Resume


def test_close_and_stop_keeps_the_container_when_a_close_fails(fake_docker, bot_config, fast_waits, queue):
    with BotThread(queue, status="failed", closed=1, failed=1):
        body = client.post(f"/api/bots/{NAME}/close-and-stop").json()
    assert body["success"] is False and body["stage"] == "close" and body["paused"] is True
    assert "broker says no" in body["message"]
    assert ("stop", NAME) not in fake_docker.calls


def test_close_and_stop_keeps_the_container_when_the_bot_never_answers(fake_docker, bot_config, fast_waits):
    body = client.post(f"/api/bots/{NAME}/close-and-stop").json()      # nobody polls
    assert body["success"] is False and body["stage"] == "close"
    assert ("stop", NAME) not in fake_docker.calls
    assert get_portfolio_manager().is_bot_paused(NAME) is True


def test_close_and_stop_refuses_a_stopped_container(fake_docker, bot_config, queue):
    fake_docker.status = "exited"
    r = client.post(f"/api/bots/{NAME}/close-and-stop")
    assert r.status_code == 409
    assert get_portfolio_manager().is_bot_paused(NAME) is False
    assert queue.take_pending(NAME) == []


def test_close_and_stop_reports_a_failed_docker_stop(fake_docker, bot_config, fast_waits, queue):
    fake_docker.stop_ok = False
    with BotThread(queue, status="done", closed=1):
        body = client.post(f"/api/bots/{NAME}/close-and-stop").json()
    assert body["success"] is False and body["stage"] == "stop" and "docker down" in body["message"]


def test_close_and_stop_unknown_bot_is_404(fake_docker):
    assert client.post("/api/bots/cbot-does-not-exist/close-and-stop").status_code == 404
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_manual_close_api.py -q -p no:cacheprovider`
Expected: the new tests FAIL (404/405 on the new routes, `KeyError: 'bot_id'` in the list test).

- [ ] **Step 3: Add `open_position_counts` to `app/portfolio.py`**

Insert right after `get_open_position` (Task 4):

```python

    def open_position_counts(self) -> Dict[str, int]:
        """Open positions per bot_id, in one query (the Bots tab lists every container)."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT bot_id, COUNT(*) FROM positions WHERE status = 'open' GROUP BY bot_id").fetchall()
            return {row[0]: int(row[1]) for row in rows}
        finally:
            conn.close()
```

- [ ] **Step 4: Extend `api_get_bots` in `app/dashboard.py`**

Replace:

```python
    pm = get_portfolio_manager()
    configs = pm.get_cbot_configs()
    # enrich with status; health comes from the watchdog's last cycle (one docker inspect per
    # bot here instead of inspect+logs per bot per 10 s poll)
    for cfg in configs:
```

with:

```python
    pm = get_portfolio_manager()
    configs = pm.get_cbot_configs()
    open_counts = pm.open_position_counts()
    # enrich with status; health comes from the watchdog's last cycle (one docker inspect per
    # bot here instead of inspect+logs per bot per 10 s poll)
    for cfg in configs:
        cfg["bot_id"] = bot_id_for_config(cfg)
        cfg["paused"] = pm.is_bot_paused(cfg["bot_id"])
        cfg["open_positions"] = open_counts.get(cfg["bot_id"], 0)
```

(`bot_id_for_config` is imported by the Task 3 section, which sits further down the module; the name resolves when the handler runs.)

- [ ] **Step 5: Add the routes**

Append to the Task 3 section in `app/dashboard.py` (after `api_close_position`):

```python


def _set_paused(name: str, paused: bool):
    pm = get_portfolio_manager()
    cfg = pm.get_cbot_config(name)
    if not cfg:
        return _error(404, "Bot config not found")
    bot_id = bot_id_for_config(cfg)
    pm.set_bot_paused(bot_id, paused)
    verb = "Paused" if paused else "Resumed"
    logger.warning(f"[MANUAL] {verb} new entries for {name} (bot_id {bot_id})")
    return {"success": True, "bot_id": bot_id, "paused": paused, "message": f"{verb} new entries for {name}"}


@router.post("/api/bots/{name}/pause")
def api_pause_bot(name: str):
    """Block the container's new entries; it keeps running and managing its open positions."""
    return _set_paused(name, True)


@router.post("/api/bots/{name}/resume")
def api_resume_bot(name: str):
    return _set_paused(name, False)


@router.post("/api/bots/{name}/close-and-stop")
async def api_close_and_stop_bot(name: str):
    """Pause the bot, have it close every position it holds, then stop its container.

    The container is stopped only once the bot reports every close done: stopping it with
    positions still open would leave them at the broker with nobody managing their stops. On any
    failure it keeps running, paused, and the message says what is left to close in cTrader.
    Docker and DB calls go through asyncio.to_thread so the wait never blocks the event loop.
    """
    pm = get_portfolio_manager()
    cfg = await asyncio.to_thread(pm.get_cbot_config, name)
    if not cfg:
        return _error(404, "Bot config not found")
    status = (await asyncio.to_thread(docker_manager.get_container_status, name)).get("status")
    if status != "running":
        return _error(409, f"Container {name} is {status}; its positions can't be closed from here, use cTrader")

    bot_id = bot_id_for_config(cfg)
    await asyncio.to_thread(pm.set_bot_paused, bot_id, True)
    cmd = command_queue.enqueue(bot_id, "close_all")
    logger.warning(f"[MANUAL] Close & Stop requested for {name}: paused, close_all command {cmd.id[:8]}")

    final = await bot_commands.wait_for_final(command_queue, cmd.id, bot_commands.CLOSE_AND_STOP_WAIT_S)
    if final is None or final.status != "done" or final.failed:
        why = (final.message or final.status) if final else "command lost"
        message = (f"{name} was NOT stopped: its positions could not all be closed ({why}). "
                   f"It keeps running, paused, and still manages its stops. Close what is left in cTrader.")
        logger.warning(f"[MANUAL] {message}")
        return {"success": False, "stage": "close", "paused": True, "message": message}

    stopped = await asyncio.to_thread(docker_manager.stop_container, name)
    if not stopped.get("success"):
        message = (f"Closed {final.closed} position(s) of {name}, but the container did not stop: "
                   f"{stopped.get('message', 'docker error')}")
        logger.warning(f"[MANUAL] {message}")
        return {"success": False, "stage": "stop", "paused": True, "closed": final.closed, "message": message}

    message = (f"Closed {final.closed} position(s) and stopped {name}. "
               f"It stays paused: after Start, click Resume to trade again.")
    logger.warning(f"[MANUAL] {message}")
    return {"success": True, "closed": final.closed, "paused": True, "message": message}
```

- [ ] **Step 6: Run the tests**

Run: `.venv/bin/pytest tests/test_manual_close_api.py tests/test_bot_control_api.py -q -p no:cacheprovider`
Expected: all pass.

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 7: Checkpoint (no commit)**

---

### Task 6: UI — Close button in Active Positions

**Files:**
- Modify: `templates/dashboard.html` (positions `<thead>` ~line 215; Jinja rows ~line 273-276; JS row render in `updateDashboard` ~line 1896-1915; new JS helpers after `updateDashboard`)
- Test: `tests/test_dashboard_ui.py` (append)

**Interfaces:**
- Consumes: `POST /api/positions/{id}/close`, `GET /api/bot-commands/{id}` (Tasks 3-4); row fields `id`, `ctrader_id`, `account_type`, `bot_id`, `symbol`, `side`, `volume`; existing JS `escapeHtml`, `refreshDashboardData`.
- Produces: JS `closingPositions` (Set of row ids as strings), `closeButtonHtml(p)`, `closePosition(btn)`, `waitForBotCommand(id, maxSeconds)`, `commandFailureText(cmd)`; one delegated click listener on `#positions-table`.

- [ ] **Step 1: Append the failing test to `tests/test_dashboard_ui.py`**

```python


def test_active_positions_rows_have_a_close_button():
    html = client.get("/demo/dashboard").text
    assert "action-close-pos" in html
    assert "fetch(`/api/positions/${d.id}/close`" in html
    assert "fetch(`/api/bot-commands/${id}`)" in html
    assert 'colspan="11" class="empty-state">No active positions' in html
    assert 'colspan="10" class="empty-state">No active positions' not in html
    # delegated once on the tbody, so rows re-rendered by updateDashboard() keep working
    assert "document.getElementById('positions-table').addEventListener('click'" in html
    assert "did not pick up the command within 15 s" in html
```

- [ ] **Step 2: Run it to see it fail**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py::test_active_positions_rows_have_a_close_button -q -p no:cacheprovider`
Expected: FAIL on `assert "action-close-pos" in html`.

- [ ] **Step 3: Header cell**

Replace:

```html
                                        <th>Open Time</th>
                                    </tr>
```

with:

```html
                                        <th>Open Time</th>
                                        <th></th>
                                    </tr>
```

- [ ] **Step 4: Jinja row cell and empty state**

Replace:

```html
                                        <td class="td-dim">{{ pos.entry_time }}</td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="10" class="empty-state">No active positions</td></tr>
```

with:

```html
                                        <td class="td-dim">{{ pos.entry_time }}</td>
                                        <td class="td-actions">
                                            <button class="log-btn action-close-pos" data-id="{{ pos.id }}" data-bot="{{ pos.bot_id }}" data-symbol="{{ pos.symbol }}" data-side="{{ pos.side }}" data-volume="{{ pos.volume }}" data-live="{{ '1' if pos.account_type == 'live' else '0' }}"{% if not pos.ctrader_id %} disabled title="No cTrader id recorded for this position - close it in cTrader"{% endif %} style="background:rgba(229,57,53,0.15); color:var(--loss);">Close</button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="11" class="empty-state">No active positions</td></tr>
```

- [ ] **Step 5: JS row cell and empty state in `updateDashboard`**

Replace:

```js
                tb.innerHTML='<tr><td colspan="10" class="empty-state">No active positions</td></tr>';
```

with:

```js
                tb.innerHTML='<tr><td colspan="11" class="empty-state">No active positions</td></tr>';
```

and replace:

```js
                        <td class="td-dim">${p.entry_time}</td>
                    </tr>`;
                }).join('');
```

with:

```js
                        <td class="td-dim">${p.entry_time}</td>
                        <td class="td-actions">${closeButtonHtml(p)}</td>
                    </tr>`;
                }).join('');
```

- [ ] **Step 6: JS helpers**

Insert right after the closing `}` of `function updateDashboard(summary,positions){ ... }`:

```js
        // --- Manual close (Close button in Active Positions) ---
        // The dashboard queues the close; the position's bot picks it up within ~2 s, closes it at
        // market and reports back. The existing broadcast then removes the row.
        const closingPositions = new Set();   // row ids with a close in flight (survives re-renders)
        const COMMAND_FAILURE_TEXT = {
            expired: 'The bot did not pick up the command within 15 s - it may be stuck or running an old build. Close the position in cTrader.',
            unconfirmed: 'The bot received the command but never reported back. Check the position in cTrader.',
        };
        function commandFailureText(cmd) {
            return COMMAND_FAILURE_TEXT[cmd.status] || `Close failed: ${cmd.message || cmd.status}`;
        }
        function closeButtonHtml(p) {
            const closing = closingPositions.has(String(p.id));
            const noId = !p.ctrader_id;
            const title = noId ? ' title="No cTrader id recorded for this position - close it in cTrader"' : '';
            return `<button class="log-btn action-close-pos" data-id="${p.id}" data-bot="${escapeHtml(p.bot_id||'')}" data-symbol="${escapeHtml(p.symbol||'')}" data-side="${escapeHtml(p.side||'')}" data-volume="${p.volume}" data-live="${p.account_type==='live'?'1':'0'}"${(noId||closing)?' disabled':''}${title} style="background:rgba(229,57,53,0.15); color:var(--loss);">${closing?'Closing…':'Close'}</button>`;
        }
        async function waitForBotCommand(id, maxSeconds = 35) {
            for (let i = 0; i < maxSeconds; i++) {
                await new Promise(r => setTimeout(r, 1000));
                const res = await fetch(`/api/bot-commands/${id}`);
                if (!res.ok) continue;
                const cmd = await res.json();
                if (['done', 'failed', 'expired', 'unconfirmed'].includes(cmd.status)) return cmd;
            }
            return { status: 'unconfirmed', message: '' };
        }
        async function closePosition(btn) {
            const d = btn.dataset;
            const tr = btn.closest('tr');
            const pnlCell = tr ? tr.querySelector('.td-pnl-live') : null;
            const pnlText = pnlCell ? pnlCell.textContent.trim() : '';
            const prefix = d.live === '1' ? '[LIVE] ' : '';
            if (!confirm(`${prefix}Close ${d.side} ${d.symbol} ${d.volume}L of ${d.bot} at market?\nCurrent P&L: ${pnlText || 'n/a'}`)) return;
            closingPositions.add(String(d.id));
            btn.disabled = true;
            btn.textContent = 'Closing…';
            try {
                const res = await fetch(`/api/positions/${d.id}/close`, { method: 'POST' });
                const data = await res.json();
                if (!data.success) throw new Error(data.message || 'Close refused');
                const cmd = await waitForBotCommand(data.command_id);
                if (cmd.status !== 'done') throw new Error(commandFailureText(cmd));
                refreshDashboardData();   // the broadcast normally removes the row first
            } catch (err) {
                alert(String((err && err.message) || err));
                btn.disabled = false;
                btn.textContent = 'Close';
            } finally {
                closingPositions.delete(String(d.id));
            }
        }
        document.getElementById('positions-table').addEventListener('click', e => {
            const btn = e.target.closest('.action-close-pos');
            if (btn && !btn.disabled) closePosition(btn);
        });
```

- [ ] **Step 7: Run the tests**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py -q -p no:cacheprovider`
Expected: all pass.

- [ ] **Step 8: Checkpoint (no commit)**

---

### Task 7: UI — Pause/Resume and Close & Stop in the Bots tab

**Files:**
- Modify: `templates/dashboard.html` (`renderBots` ~line 959-1030; `BOT_ACTION_PENDING` ~line 1035; new `closeAndStopBot` after `actionBot`)
- Test: `tests/test_dashboard_ui.py` (append)

**Interfaces:**
- Consumes: `/api/bots` fields `paused`, `open_positions`, `account_type` (Task 5); routes `/api/bots/{name}/pause|resume|close-and-stop`; existing JS `actionBot(name, action, btn)`, `lockBotRow(btn, action)`.
- Produces: JS `closeAndStopBot(btn)`; button classes `action-pause`, `action-resume`, `action-close-stop`.

- [ ] **Step 1: Append the failing test to `tests/test_dashboard_ui.py`**

```python


def test_bots_tab_has_pause_resume_and_close_and_stop():
    html = client.get("/demo/dashboard").text
    for snippet in ("action-pause", "action-resume", "action-close-stop", "Close &amp; Stop",
                    "Pausing…", "Resuming…", "Closing & stopping…", "/close-and-stop", ">PAUSED</span>"):
        assert snippet in html, snippet
```

- [ ] **Step 2: Run it to see it fail**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py::test_bots_tab_has_pause_resume_and_close_and_stop -q -p no:cacheprovider`
Expected: FAIL on `action-pause`.

- [ ] **Step 3: Buttons and badge in `renderBots`**

Replace:

```js
                const modeBadge = (b.account_type === 'live')
                    ? '<span class="badge badge--live"><span class="badge-dot"></span>LIVE</span>'
                    : '<span class="badge badge--demo"><span class="badge-dot"></span>DEMO</span>';
```

with:

```js
                const modeBadge = (b.account_type === 'live')
                    ? '<span class="badge badge--live"><span class="badge-dot"></span>LIVE</span>'
                    : '<span class="badge badge--demo"><span class="badge-dot"></span>DEMO</span>';
                // Pause blocks new entries only; the container keeps managing its open positions.
                const pausedHtml = b.paused
                    ? ' <span class="badge" style="background:rgba(245,158,11,0.15); color:#f59e0b;" title="New entries blocked from the dashboard; open positions are still managed">PAUSED</span>'
                    : '';
                const pauseBtn = b.paused
                    ? `<button class="log-btn action-resume" data-name="${b.name}" style="background:rgba(125,189,30,0.15); color:var(--profit); margin-right:4px;">Resume</button>`
                    : `<button class="log-btn action-pause" data-name="${b.name}" style="background:rgba(255,193,7,0.15); color:#f59e0b; margin-right:4px;">Pause</button>`;
                const closeStopBtn = isRunning
                    ? `<button class="log-btn action-close-stop" data-name="${b.name}" data-open="${b.open_positions || 0}" data-live="${b.account_type === 'live' ? '1' : '0'}" style="background:var(--loss); color:#fff; margin-right:4px;">Close &amp; Stop</button>`
                    : '';
```

Replace:

```js
                    <td>${statusHtml}</td>
```

with:

```js
                    <td>${statusHtml}${pausedHtml}</td>
```

Replace:

```js
                    <td style="text-align:right; white-space:nowrap;">
                        ${isRunning 
```

with:

```js
                    <td style="text-align:right; white-space:nowrap;">
                        ${pauseBtn}${closeStopBtn}${isRunning 
```

(keep the trailing space after `isRunning` exactly as it is in the file).

- [ ] **Step 4: Handlers**

Replace:

```js
            document.querySelectorAll(".action-restart").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "restart", e.currentTarget)));
```

with:

```js
            document.querySelectorAll(".action-restart").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "restart", e.currentTarget)));
            document.querySelectorAll(".action-pause").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "pause", e.currentTarget)));
            document.querySelectorAll(".action-resume").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "resume", e.currentTarget)));
            document.querySelectorAll(".action-close-stop").forEach(btn => btn.addEventListener("click", e => closeAndStopBot(e.currentTarget)));
```

- [ ] **Step 5: Pending labels and `closeAndStopBot`**

Replace:

```js
        const BOT_ACTION_PENDING = { start: "Starting…", stop: "Stopping…", restart: "Restarting…", delete: "Deleting…" };
```

with:

```js
        const BOT_ACTION_PENDING = { start: "Starting…", stop: "Stopping…", restart: "Restarting…", delete: "Deleting…",
                                     pause: "Pausing…", resume: "Resuming…", "close-and-stop": "Closing & stopping…" };
```

Insert right after the closing `}` of `async function actionBot(name, action, btn) { ... }`:

```js
        // Kill switch: pause, close every position the bot holds, then stop the container. The server
        // stops it only when the bot confirms every close; otherwise it keeps running, paused.
        async function closeAndStopBot(btn) {
            const name = btn.dataset.name;
            const n = btn.dataset.open || '0';
            const prefix = btn.dataset.live === '1' ? '[LIVE] ' : '';
            if (!confirm(`${prefix}Close ${n} open position(s) of ${name} at market, then stop the container?\n\nThe bot is paused first. If a position cannot be closed, the container keeps running (paused) so it still manages its stops.`)) return;
            const unlock = lockBotRow(btn, "close-and-stop");
            try {
                const res = await fetch(`/api/bots/${name}/close-and-stop`, { method: "POST" });
                const data = await res.json();
                alert(data.message || (data.success ? "Done" : "Error"));
            } catch(e) { alert("Error: " + e); }
            finally { unlock(); }
        }
```

- [ ] **Step 6: Run the tests**

Run: `.venv/bin/pytest tests/test_dashboard_ui.py -q -p no:cacheprovider`
Expected: all pass (including the existing `test_bot_action_buttons_show_pending_state_and_polls_do_not_overlap`).

- [ ] **Step 7: Checkpoint (no commit)**

The layout of the new column and buttons is checked on the real dashboard in Task 11 Step 5 (port 8000 on the Mac is the VPS tunnel, so there is no local server to look at).

---

### Task 8: AiAgentBot — command poll, close executor, pause guard

**Files:**
- Modify: `cBot/AiAgentBot.cs` (parameter after `TickStreamMs` ~line 40; `OnStart`/`OnStop` ~lines 465-471; `CloseWithReason` ~line 1682; entry order ~line 2404; new section before `private string BuildTickStreamUrl()`)
- Test: `tests/test_cbot_command_poll.py` (new; extended in Tasks 9-10)

**Interfaces:**
- Consumes: server routes from Task 3 (`GET /api/cbot/commands?bot_id=`, `POST /api/cbot/commands/{id}/result` with `{bot_id, status, message, closed, failed}`).
- Produces (same names in all three bots): `CommandPollMs`, `ManualCloseReason`, `DashboardCommand`, `DashboardCommandPoll`, `StartCommandPoll()`, `StopCommandPoll()`, `BuildCommandBaseUrl()`, `CommandPollLoopAsync(HttpClient, string, string, CancellationToken)`, `ExecuteDashboardCommand(string, DashboardCommand)`, `PostCommandResult(...)`, `DashboardPauseBlocks(string)`, `TradeResult CloseWithReason(Position, string)`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cbot_command_poll.py`:

```python
"""cBot side of the dashboard commands (spec 2026-09-24): poll, close, pause guard.

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build itself is
checked on the VPS with ctrader-console.
"""
import re
from pathlib import Path

import pytest

CBOT = Path(__file__).resolve().parent.parent / "cBot"

# bot file -> how its command executor finds its own positions (never another bot's)
OWN_POSITIONS = {
    "AiAgentBot.cs": "var own = GetBotPositions();",
}
BOTS = list(OWN_POSITIONS)


def _src(name):
    return (CBOT / name).read_text(encoding="utf-8")


def _method(src, signature):
    """From `signature` to the next member declared at class-member indentation (8 spaces)."""
    start = src.index(signature)
    rest = src[start + len(signature):]
    nxt = re.search(r"\n {8}(private|protected|public|internal) ", rest)
    return src[start: start + len(signature) + (nxt.start() if nxt else len(rest))]


def _entry_orders(src):
    """Offsets of real ExecuteMarketOrder calls (comment lines skipped)."""
    for m in re.finditer(r"ExecuteMarketOrder\(", src):
        line_start = src.rfind("\n", 0, m.start()) + 1
        if "//" not in src[line_start:m.start()]:
            yield m.start()


@pytest.mark.parametrize("name", BOTS)
def test_command_poll_parameter_defaults_to_two_seconds(name):
    assert re.search(r'\[Parameter\("Command Poll \(ms, 0=off\)", Group = "[^"]+", DefaultValue = 2000, MinValue = 0\)\]'
                     r'\s*public int CommandPollMs \{ get; set; \}', _src(name))


@pytest.mark.parametrize("name", BOTS)
def test_poll_runs_only_live_and_stops_with_the_bot(name):
    src = _src(name)
    start = _method(src, "private void StartCommandPoll()")
    assert "RunningMode != RunningMode.RealTime" in start and "CommandPollMs <= 0" in start
    assert "new HttpClient { Timeout = TimeSpan.FromSeconds(5) }" in start
    assert "StartCommandPoll();" in _method(src, "protected override void OnStart()")
    assert "StopCommandPoll();" in _method(src, "protected override void OnStop()")


@pytest.mark.parametrize("name", BOTS)
def test_poll_and_result_urls(name):
    src = _src(name)
    assert "/api/cbot/commands?bot_id={Uri.EscapeDataString(BotId)}" in src
    assert "/api/cbot/commands/{Uri.EscapeDataString(commandId)}/result" in src


@pytest.mark.parametrize("name", BOTS)
def test_a_command_id_is_recorded_before_it_runs(name):
    loop = _method(_src(name), "private async Task CommandPollLoopAsync(")
    assert loop.index("_handledCommandIds.Add(cmd.id)") < loop.index("BeginInvokeOnMainThread(() => ExecuteDashboardCommand(")
    assert "_dashboardPaused = poll.paused;" in loop


@pytest.mark.parametrize("name", BOTS)
def test_commands_close_only_the_bots_own_positions_with_a_reason(name):
    src = _src(name)
    body = _method(src, "private void ExecuteDashboardCommand(")
    assert OWN_POSITIONS[name] in body
    assert "CloseWithReason(pos, ManualCloseReason)" in body
    assert 'private const string ManualCloseReason = "Manual close (dashboard)";' in src
    assert "private TradeResult CloseWithReason(Position pos, string reason)" in src


@pytest.mark.parametrize("name", BOTS)
def test_pause_log_is_throttled(name):
    helper = _method(_src(name), "private bool DashboardPauseBlocks(string what)")
    assert "if (!_dashboardPaused) return false;" in helper
    assert "TotalSeconds >= 60" in helper


@pytest.mark.parametrize("name", BOTS)
def test_every_entry_order_is_behind_the_pause_guard(name):
    src = _src(name)
    orders = list(_entry_orders(src))
    assert orders
    previous = -1
    for pos in orders:
        guard = src.rfind("if (DashboardPauseBlocks(", 0, pos)
        assert guard > previous, f"{name}: ExecuteMarketOrder at offset {pos} has no pause guard of its own"
        assert pos - guard < 1500, f"{name}: pause guard too far from the order at offset {pos}"
        previous = pos
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py -q -p no:cacheprovider`
Expected: every test FAILS (`ValueError: substring not found` / no regex match).

- [ ] **Step 3: Parameter**

Replace:

```csharp
        [Parameter("Tick Stream (ms, 0=off)", Group = "API", DefaultValue = 1000, MinValue = 0)]
        public int TickStreamMs { get; set; }
```

with:

```csharp
        [Parameter("Tick Stream (ms, 0=off)", Group = "API", DefaultValue = 1000, MinValue = 0)]
        public int TickStreamMs { get; set; }

        // Dashboard commands (Close, Close & Stop, Pause) are polled from /api/cbot/commands.
        // 0 turns them off.
        [Parameter("Command Poll (ms, 0=off)", Group = "API", DefaultValue = 2000, MinValue = 0)]
        public int CommandPollMs { get; set; }
```

- [ ] **Step 4: Start/stop**

Replace:

```csharp
            StartTickStream();
        }
        protected override void OnStop()
        {
            StopTickStream();
        }
```

with:

```csharp
            StartTickStream();
            StartCommandPoll();
        }
        protected override void OnStop()
        {
            StopTickStream();
            StopCommandPoll();
        }
```

- [ ] **Step 5: `CloseWithReason` returns the result**

Replace:

```csharp
        private void CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            pos.Close();
        }
```

with:

```csharp
        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            return pos.Close();
        }
```

- [ ] **Step 6: Pause guard before the entry order**

Replace:

```csharp
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, "AI_Agent", slPips, effectiveTpPips);
```

with:

```csharp
            if (DashboardPauseBlocks($"{tradeType} entry")) return;
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, "AI_Agent", slPips, effectiveTpPips);
```

- [ ] **Step 7: The command section**

Insert right before `        private string BuildTickStreamUrl()`:

```csharp
        // ==========================================
        // DASHBOARD COMMANDS (/api/cbot/commands)
        // ==========================================
        // The dashboard can close this bot's positions (Close, Close & Stop) and pause its new
        // entries (Pause). The server cannot reach a cBot, so the bot asks every CommandPollMs;
        // the reply carries the pause flag and any pending commands. A command not picked up
        // within 15 s expires on the server and is never handed out, so a bot that restarts later
        // cannot act on a stale close. Ids already run are skipped.

        private const string ManualCloseReason = "Manual close (dashboard)";

        private class DashboardCommand
        {
            public string id { get; set; }
            public string action { get; set; }
            public long? position_id { get; set; }
        }

        private class DashboardCommandPoll
        {
            public bool paused { get; set; }
            public List<DashboardCommand> commands { get; set; }
        }

        private CancellationTokenSource _commandPollCts;
        private HttpClient _commandHttp;
        private volatile bool _dashboardPaused;
        private readonly HashSet<string> _handledCommandIds = new HashSet<string>();
        private DateTime _lastCommandPollErrorAt = DateTime.MinValue;
        private DateTime _lastPauseLogAt = DateTime.MinValue;

        private void StartCommandPoll()
        {
            if (RunningMode != RunningMode.RealTime || CommandPollMs <= 0) return;
            var baseUrl = BuildCommandBaseUrl();
            if (baseUrl == null) return;

            _commandHttp = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            _commandPollCts = new CancellationTokenSource();
            var token = _commandPollCts.Token;
            var http = _commandHttp;
            var pollUrl = $"{baseUrl}/api/cbot/commands?bot_id={Uri.EscapeDataString(BotId)}";
            Task.Run(() => CommandPollLoopAsync(http, baseUrl, pollUrl, token), token);
            Print($"[Dashboard] Polling {pollUrl} every {CommandPollMs} ms");
        }

        private void StopCommandPoll()
        {
            try { _commandPollCts?.Cancel(); } catch { }
            _commandPollCts = null;
        }

        private string BuildCommandBaseUrl()
        {
            var baseUrl = ApiUrl;
            if (string.IsNullOrWhiteSpace(baseUrl)) return null;

            baseUrl = baseUrl.Trim().Trim('"', '\'', '“', '”', '‘', '’', '`');
            const string tradePath = "/trade";
            if (baseUrl.EndsWith(tradePath)) baseUrl = baseUrl.Substring(0, baseUrl.Length - tradePath.Length);
            baseUrl = baseUrl.TrimEnd('/');
            return baseUrl.StartsWith("http://") || baseUrl.StartsWith("https://") ? baseUrl : null;
        }

        private async Task CommandPollLoopAsync(HttpClient http, string baseUrl, string pollUrl, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var response = await http.GetAsync(pollUrl, token);
                    response.EnsureSuccessStatusCode();
                    var body = await response.Content.ReadAsStringAsync();
                    var poll = JsonSerializer.Deserialize<DashboardCommandPoll>(body);
                    if (poll != null)
                    {
                        _dashboardPaused = poll.paused;
                        foreach (var cmd in poll.commands ?? new List<DashboardCommand>())
                        {
                            if (cmd == null || string.IsNullOrEmpty(cmd.id)) continue;
                            bool isNew;
                            lock (_handledCommandIds) { isNew = _handledCommandIds.Add(cmd.id); }
                            if (!isNew) continue;
                            var command = cmd;
                            BeginInvokeOnMainThread(() => ExecuteDashboardCommand(baseUrl, command));
                        }
                    }
                }
                catch (OperationCanceledException) when (token.IsCancellationRequested) { break; }
                catch (Exception ex)
                {
                    // Keep the last known pause flag; say so at most once a minute.
                    if ((DateTime.UtcNow - _lastCommandPollErrorAt).TotalSeconds >= 60)
                    {
                        _lastCommandPollErrorAt = DateTime.UtcNow;
                        Print($"[Dashboard] Command poll failed: {ex.GetType().Name}: {ex.Message}");
                    }
                }

                try { await Task.Delay(CommandPollMs, token); } catch { break; }
            }
            try { http.Dispose(); } catch { }
        }

        /// <summary>Runs on the cBot thread. Closes only this bot's own positions.</summary>
        private void ExecuteDashboardCommand(string baseUrl, DashboardCommand cmd)
        {
            var own = GetBotPositions();
            List<Position> targets;
            if (cmd.action == "close_all")
                targets = own.ToList();
            else if (cmd.action == "close_position")
                targets = own.Where(p => p.Id == cmd.position_id).ToList();
            else
            {
                PostCommandResult(baseUrl, cmd.id, "failed", $"unknown action '{cmd.action}'", 0, 0);
                return;
            }

            if (cmd.action == "close_position" && targets.Count == 0)
            {
                Print($"[Dashboard] Close #{cmd.position_id}: not among this bot's open positions");
                PostCommandResult(baseUrl, cmd.id, "failed", $"position {cmd.position_id} not found among this bot's open positions", 0, 0);
                return;
            }

            int closed = 0;
            var errors = new List<string>();
            foreach (var pos in targets)
            {
                var result = CloseWithReason(pos, ManualCloseReason);
                if (result != null && result.IsSuccessful) closed++;
                else errors.Add($"#{pos.Id} {(result != null ? result.Error.ToString() : "no result")}");
            }

            string message = errors.Count == 0 ? $"closed {closed}" : $"closed {closed}, failed: {string.Join(", ", errors)}";
            Print($"[Dashboard] {cmd.action}: {message}");
            PostCommandResult(baseUrl, cmd.id, errors.Count == 0 ? "done" : "failed", message, closed, errors.Count);
        }

        private void PostCommandResult(string baseUrl, string commandId, string status, string message, int closed, int failed)
        {
            var http = _commandHttp;
            if (http == null) return;
            var json = JsonSerializer.Serialize(new { bot_id = BotId, status, message, closed, failed });
            var url = $"{baseUrl}/api/cbot/commands/{Uri.EscapeDataString(commandId)}/result";
            Task.Run(async () =>
            {
                try
                {
                    await http.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                }
                catch (Exception ex)
                {
                    Print($"[Dashboard] Could not report command {commandId}: {ex.Message}");
                }
            });
        }

        /// <summary>True while the dashboard has paused this bot's new entries (logged once a minute).</summary>
        private bool DashboardPauseBlocks(string what)
        {
            if (!_dashboardPaused) return false;
            if ((DateTime.UtcNow - _lastPauseLogAt).TotalSeconds >= 60)
            {
                _lastPauseLogAt = DateTime.UtcNow;
                Print($"[Dashboard] Paused from the dashboard: {what} skipped");
            }
            return true;
        }

```

- [ ] **Step 8: Run the tests**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py tests/test_dashboard_sltp_and_close_reason.py -q -p no:cacheprovider`
Expected: all pass (`pos.Close();` still appears exactly once, inside `CloseWithReason`).

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 9: Checkpoint (no commit)**

The C# is not compiled yet — Task 11 Step 1 does that on the VPS.

---

### Task 9: AsianRangeJudasSweepBot — command poll, close executor, pause guard

**Files:**
- Modify: `cBot/AsianRangeJudasSweepBot.cs` (parameter after `TickStreamMs` ~line 92; `OnStart` ~line 553; `OnStop` ~line 1001; entries ~lines 780, 800, 1916, 1929; `CloseWithReason` ~line 865; `ExecuteDecision` entry ~line 4252; `ExecuteStagedMarketOrder` entry ~line 4450; new section before `private string BuildTickStreamUrl()`)
- Test: `tests/test_cbot_command_poll.py` (extend)

**Interfaces:**
- Consumes/Produces: the same members as Task 8. Judas finds its own positions with `Positions.FindAll(label, SymbolName)` and builds its base URL from `DashboardServerUrl` first (as `BuildTickStreamUrl` does; its `ApiUrl` parameter defaults to a cloud LLM endpoint).

- [ ] **Step 1: Extend the tests**

In `tests/test_cbot_command_poll.py`, replace:

```python
OWN_POSITIONS = {
    "AiAgentBot.cs": "var own = GetBotPositions();",
}
```

with:

```python
OWN_POSITIONS = {
    "AiAgentBot.cs": "var own = GetBotPositions();",
    "AsianRangeJudasSweepBot.cs": "var own = Positions.FindAll(label, SymbolName);",
}
```

and append:

```python


def test_judas_command_base_url_prefers_the_dashboard_server():
    body = _method(_src("AsianRangeJudasSweepBot.cs"), "private string BuildCommandBaseUrl()")
    assert body.index("DashboardServerUrl") < body.index("ApiUrl")


def test_judas_drops_a_staged_order_while_paused():
    body = _method(_src("AsianRangeJudasSweepBot.cs"), "private void ExecuteStagedMarketOrder(TradeType tradeType)")
    assert re.search(r"if \(DashboardPauseBlocks\([^)]*\)\)\s*\{\s*ResetStagedOrder\(\);\s*return;", body)


def test_judas_guards_all_six_entry_orders():
    assert len(list(_entry_orders(_src("AsianRangeJudasSweepBot.cs")))) == 6
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py -q -p no:cacheprovider`
Expected: the Judas cases FAIL; the AiAgentBot cases still pass.

- [ ] **Step 3: Parameter**

Replace:

```csharp
        [Parameter("Tick Stream (ms, 0=off)", Group = "AI Agent Settings", DefaultValue = 1000, MinValue = 0)]
        public int TickStreamMs { get; set; }
```

with:

```csharp
        [Parameter("Tick Stream (ms, 0=off)", Group = "AI Agent Settings", DefaultValue = 1000, MinValue = 0)]
        public int TickStreamMs { get; set; }

        // Dashboard commands (Close, Close & Stop, Pause) are polled from /api/cbot/commands.
        // 0 turns them off.
        [Parameter("Command Poll (ms, 0=off)", Group = "AI Agent Settings", DefaultValue = 2000, MinValue = 0)]
        public int CommandPollMs { get; set; }
```

- [ ] **Step 4: Start/stop**

Replace:

```csharp
            StartTickStream();

            _ = SendStateToAgentAsync();
```

with:

```csharp
            StartTickStream();
            StartCommandPoll();

            _ = SendStateToAgentAsync();
```

Replace:

```csharp
            StopTickStream();
            Print(label + " Stopped.");
```

with:

```csharp
            StopTickStream();
            StopCommandPoll();
            Print(label + " Stopped.");
```

- [ ] **Step 5: `CloseWithReason` returns the result**

Replace:

```csharp
        private void CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            ClosePosition(pos);
        }
```

with:

```csharp
        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            return ClosePosition(pos);
        }
```

- [ ] **Step 6: Guards on the indicator entries**

Replace:

```csharp
                    if (timeDifference.TotalSeconds >= 2 && _isWaiting == false)
                    {
                        CalculateSLTP(TradeType.Buy, Symbol.Bid);
```

with:

```csharp
                    if (timeDifference.TotalSeconds >= 2 && _isWaiting == false)
                    {
                        if (DashboardPauseBlocks("BUY entry")) return;
                        CalculateSLTP(TradeType.Buy, Symbol.Bid);
```

Replace:

```csharp
                    if (timeDifference.TotalSeconds >= 2 && _isWaiting == false)
                    {
                        CalculateSLTP(TradeType.Sell, Symbol.Ask);
```

with:

```csharp
                    if (timeDifference.TotalSeconds >= 2 && _isWaiting == false)
                    {
                        if (DashboardPauseBlocks("SELL entry")) return;
                        CalculateSLTP(TradeType.Sell, Symbol.Ask);
```

- [ ] **Step 7: Guards on the DCA adds**

Replace:

```csharp
                        double vol = dcaVolumeUnit();
                        var res = ExecuteMarketOrder(TradeType.Buy, SymbolName, vol, label, stoploss, takeprofit);
```

with:

```csharp
                        if (DashboardPauseBlocks("DCA BUY add")) return;
                        double vol = dcaVolumeUnit();
                        var res = ExecuteMarketOrder(TradeType.Buy, SymbolName, vol, label, stoploss, takeprofit);
```

Replace:

```csharp
                        double vol = dcaVolumeUnit();
                        var res = ExecuteMarketOrder(TradeType.Sell, SymbolName, vol, label, stoploss, takeprofit);
```

with:

```csharp
                        if (DashboardPauseBlocks("DCA SELL add")) return;
                        double vol = dcaVolumeUnit();
                        var res = ExecuteMarketOrder(TradeType.Sell, SymbolName, vol, label, stoploss, takeprofit);
```

- [ ] **Step 8: Guards on the AI entries**

In `ExecuteDecision` (16-space indentation), replace:

```csharp
                _lastAgentReason = decision.reason;
                var result = ExecuteMarketOrder(tradeType, SymbolName, volume, label, slPips > 0 ? slPips : (double?)null, tpPips > 0 ? tpPips : (double?)null);
```

with:

```csharp
                if (DashboardPauseBlocks($"AI {tradeType} entry")) return;
                _lastAgentReason = decision.reason;
                var result = ExecuteMarketOrder(tradeType, SymbolName, volume, label, slPips > 0 ? slPips : (double?)null, tpPips > 0 ? tpPips : (double?)null);
```

In `ExecuteStagedMarketOrder` (12-space indentation), replace:

```csharp
            _lastAgentReason = decision.reason;
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, label, slPips > 0 ? slPips : (double?)null, tpPips > 0 ? tpPips : (double?)null);
```

with:

```csharp
            // A pause drops the staged order: resuming later must not fire a stale signal.
            if (DashboardPauseBlocks($"staged {tradeType} entry"))
            {
                ResetStagedOrder();
                return;
            }
            _lastAgentReason = decision.reason;
            var result = ExecuteMarketOrder(tradeType, SymbolName, volume, label, slPips > 0 ? slPips : (double?)null, tpPips > 0 ? tpPips : (double?)null);
```

(The two anchors differ only in indentation: match the 16-space one inside `ExecuteDecision` first, then the 12-space one inside `ExecuteStagedMarketOrder`.)

- [ ] **Step 9: The command section**

Insert right before `        private string BuildTickStreamUrl()`:

```csharp
        // ==========================================
        // DASHBOARD COMMANDS (/api/cbot/commands)
        // ==========================================
        // The dashboard can close this bot's positions (Close, Close & Stop) and pause its new
        // entries (Pause). The server cannot reach a cBot, so the bot asks every CommandPollMs;
        // the reply carries the pause flag and any pending commands. A command not picked up
        // within 15 s expires on the server and is never handed out, so a bot that restarts later
        // cannot act on a stale close. Ids already run are skipped.

        private const string ManualCloseReason = "Manual close (dashboard)";

        private class DashboardCommand
        {
            public string id { get; set; }
            public string action { get; set; }
            public long? position_id { get; set; }
        }

        private class DashboardCommandPoll
        {
            public bool paused { get; set; }
            public List<DashboardCommand> commands { get; set; }
        }

        private CancellationTokenSource _commandPollCts;
        private HttpClient _commandHttp;
        private volatile bool _dashboardPaused;
        private readonly HashSet<string> _handledCommandIds = new HashSet<string>();
        private DateTime _lastCommandPollErrorAt = DateTime.MinValue;
        private DateTime _lastPauseLogAt = DateTime.MinValue;

        private void StartCommandPoll()
        {
            if (RunningMode != RunningMode.RealTime || CommandPollMs <= 0) return;
            var baseUrl = BuildCommandBaseUrl();
            if (baseUrl == null) return;

            _commandHttp = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            _commandPollCts = new CancellationTokenSource();
            var token = _commandPollCts.Token;
            var http = _commandHttp;
            var pollUrl = $"{baseUrl}/api/cbot/commands?bot_id={Uri.EscapeDataString(BotId)}";
            Task.Run(() => CommandPollLoopAsync(http, baseUrl, pollUrl, token), token);
            Print($"[Dashboard] Polling {pollUrl} every {CommandPollMs} ms");
        }

        private void StopCommandPoll()
        {
            try { _commandPollCts?.Cancel(); } catch { }
            _commandPollCts = null;
        }

        private string BuildCommandBaseUrl()
        {
            // The dashboard server first, as for the tick stream: this bot's AI endpoint parameter
            // defaults to a cloud LLM, not to our server.
            var baseUrl = !string.IsNullOrWhiteSpace(DashboardServerUrl) ? DashboardServerUrl : ApiUrl;
            if (string.IsNullOrWhiteSpace(baseUrl)) return null;

            baseUrl = baseUrl.Trim().Trim('"', '\'', '“', '”', '‘', '’', '`');
            const string tradePath = "/trade";
            if (baseUrl.EndsWith(tradePath)) baseUrl = baseUrl.Substring(0, baseUrl.Length - tradePath.Length);
            baseUrl = baseUrl.TrimEnd('/');
            return baseUrl.StartsWith("http://") || baseUrl.StartsWith("https://") ? baseUrl : null;
        }

        private async Task CommandPollLoopAsync(HttpClient http, string baseUrl, string pollUrl, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var response = await http.GetAsync(pollUrl, token);
                    response.EnsureSuccessStatusCode();
                    var body = await response.Content.ReadAsStringAsync();
                    var poll = JsonSerializer.Deserialize<DashboardCommandPoll>(body);
                    if (poll != null)
                    {
                        _dashboardPaused = poll.paused;
                        foreach (var cmd in poll.commands ?? new List<DashboardCommand>())
                        {
                            if (cmd == null || string.IsNullOrEmpty(cmd.id)) continue;
                            bool isNew;
                            lock (_handledCommandIds) { isNew = _handledCommandIds.Add(cmd.id); }
                            if (!isNew) continue;
                            var command = cmd;
                            BeginInvokeOnMainThread(() => ExecuteDashboardCommand(baseUrl, command));
                        }
                    }
                }
                catch (OperationCanceledException) when (token.IsCancellationRequested) { break; }
                catch (Exception ex)
                {
                    // Keep the last known pause flag; say so at most once a minute.
                    if ((DateTime.UtcNow - _lastCommandPollErrorAt).TotalSeconds >= 60)
                    {
                        _lastCommandPollErrorAt = DateTime.UtcNow;
                        Print($"[Dashboard] Command poll failed: {ex.GetType().Name}: {ex.Message}");
                    }
                }

                try { await Task.Delay(CommandPollMs, token); } catch { break; }
            }
            try { http.Dispose(); } catch { }
        }

        /// <summary>Runs on the cBot thread. Closes only this bot's own positions (its label).</summary>
        private void ExecuteDashboardCommand(string baseUrl, DashboardCommand cmd)
        {
            var own = Positions.FindAll(label, SymbolName);
            List<Position> targets;
            if (cmd.action == "close_all")
                targets = own.ToList();
            else if (cmd.action == "close_position")
                targets = own.Where(p => p.Id == cmd.position_id).ToList();
            else
            {
                PostCommandResult(baseUrl, cmd.id, "failed", $"unknown action '{cmd.action}'", 0, 0);
                return;
            }

            if (cmd.action == "close_position" && targets.Count == 0)
            {
                Print($"[Dashboard] Close #{cmd.position_id}: not among this bot's open positions");
                PostCommandResult(baseUrl, cmd.id, "failed", $"position {cmd.position_id} not found among this bot's open positions", 0, 0);
                return;
            }

            int closed = 0;
            var errors = new List<string>();
            foreach (var pos in targets)
            {
                var result = CloseWithReason(pos, ManualCloseReason);
                if (result != null && result.IsSuccessful) closed++;
                else errors.Add($"#{pos.Id} {(result != null ? result.Error.ToString() : "no result")}");
            }

            string message = errors.Count == 0 ? $"closed {closed}" : $"closed {closed}, failed: {string.Join(", ", errors)}";
            Print($"[Dashboard] {cmd.action}: {message}");
            PostCommandResult(baseUrl, cmd.id, errors.Count == 0 ? "done" : "failed", message, closed, errors.Count);
        }

        private void PostCommandResult(string baseUrl, string commandId, string status, string message, int closed, int failed)
        {
            var http = _commandHttp;
            if (http == null) return;
            var json = JsonSerializer.Serialize(new { bot_id = BotId, status, message, closed, failed });
            var url = $"{baseUrl}/api/cbot/commands/{Uri.EscapeDataString(commandId)}/result";
            Task.Run(async () =>
            {
                try
                {
                    await http.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                }
                catch (Exception ex)
                {
                    Print($"[Dashboard] Could not report command {commandId}: {ex.Message}");
                }
            });
        }

        /// <summary>True while the dashboard has paused this bot's new entries (logged once a minute).</summary>
        private bool DashboardPauseBlocks(string what)
        {
            if (!_dashboardPaused) return false;
            if ((DateTime.UtcNow - _lastPauseLogAt).TotalSeconds >= 60)
            {
                _lastPauseLogAt = DateTime.UtcNow;
                Print($"[Dashboard] Paused from the dashboard: {what} skipped");
            }
            return true;
        }

```

- [ ] **Step 10: Run the tests**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py tests/test_dashboard_sltp_and_close_reason.py -q -p no:cacheprovider`
Expected: all pass (`ClosePosition(pos);` still appears exactly once, inside `CloseWithReason`).

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 11: Checkpoint (no commit)**

---

### Task 10: FlowRsiBot — command poll, close executor, pause guard, close reason

**Files:**
- Modify: `cBot/FlowRsiBot.cs` (parameter after `AiReportUrl` ~line 241; `OnStart` ~line 527; `OnStop` ~line 668; entry order in `ExecuteTechnicalOrder` ~line 1742; `OnPositionClosed` ~lines 2672-2693; new section before `private void SendLiveTickTelemetry(bool force = false)`)
- Test: `tests/test_cbot_command_poll.py` (extend)

**Interfaces:**
- Consumes/Produces: the same members as Task 8, plus FlowRSI's first `_closeReasons` map and `CloseWithReason`. FlowRSI finds its own positions with `GetBotPositions()` (`Positions.FindAll(BotId, SymbolName)`). The existing raw `ClosePosition(pos)` calls (AI `CLOSE_ALL`, circuit breaker, partial close) are left as they are.

- [ ] **Step 1: Extend the tests**

In `tests/test_cbot_command_poll.py`, replace:

```python
    "AsianRangeJudasSweepBot.cs": "var own = Positions.FindAll(label, SymbolName);",
}
```

with:

```python
    "AsianRangeJudasSweepBot.cs": "var own = Positions.FindAll(label, SymbolName);",
    "FlowRsiBot.cs": "var own = GetBotPositions();",
}
```

and append:

```python


def test_flowrsi_reports_the_manual_close_reason():
    body = _method(_src("FlowRsiBot.cs"), "private void OnPositionClosed(PositionClosedEventArgs args)")
    assert "_closeReasons.TryGetValue(pos.Id, out botReason)" in body
    assert "reason = hasBotReason ? botReason :" in body
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py -q -p no:cacheprovider`
Expected: the FlowRSI cases FAIL; AiAgentBot and Judas still pass.

- [ ] **Step 3: Parameter**

Replace:

```csharp
        [Parameter("Portfolio Report Endpoint", Group = "AI Agent Integration", DefaultValue = "http://127.0.0.1:8000/portfolio/report")]
        public string AiReportUrl { get; set; }
```

with:

```csharp
        [Parameter("Portfolio Report Endpoint", Group = "AI Agent Integration", DefaultValue = "http://127.0.0.1:8000/portfolio/report")]
        public string AiReportUrl { get; set; }

        // Dashboard commands (Close, Close & Stop, Pause) are polled from /api/cbot/commands.
        // 0 turns them off.
        [Parameter("Command Poll (ms, 0=off)", Group = "AI Agent Integration", DefaultValue = 2000, MinValue = 0)]
        public int CommandPollMs { get; set; }
```

- [ ] **Step 4: Start/stop**

Replace:

```csharp
                // 4. Register Position Events for Centralized Telegram & Portfolio Tracking
                Positions.Closed += OnPositionClosed;
```

with:

```csharp
                // 4. Register Position Events for Centralized Telegram & Portfolio Tracking
                Positions.Closed += OnPositionClosed;
                StartCommandPoll();
```

Replace:

```csharp
            _isStopped = true;
            Positions.Closed -= OnPositionClosed;
```

with:

```csharp
            _isStopped = true;
            StopCommandPoll();
            Positions.Closed -= OnPositionClosed;
```

- [ ] **Step 5: Pause guard before the entry order**

Replace:

```csharp
            var result = ExecuteMarketOrder(tradeType, SymbolName, targetUnits, BotId, slPips, tpPips, BotId);
```

with:

```csharp
            if (DashboardPauseBlocks($"{tradeType} entry")) return;
            var result = ExecuteMarketOrder(tradeType, SymbolName, targetUnits, BotId, slPips, tpPips, BotId);
```

- [ ] **Step 6: Report the manual close reason**

In `OnPositionClosed`, replace:

```csharp
                    double pnl = pos.NetProfit;
                    string reason = args.Reason.ToString();
```

with:

```csharp
                    double pnl = pos.NetProfit;
                    string reason = args.Reason.ToString();
                    string botReason;
                    bool hasBotReason = _closeReasons.TryGetValue(pos.Id, out botReason);
                    _closeReasons.Remove(pos.Id);
```

and replace:

```csharp
                    else if (args.Reason == PositionCloseReason.Closed)
                    {
                        reason = pnl >= 0 ? "Closed (Take Profit Early)" : "Closed (Cut Loss Early)";
                    }
```

with:

```csharp
                    else if (args.Reason == PositionCloseReason.Closed)
                    {
                        reason = hasBotReason ? botReason : (pnl >= 0 ? "Closed (Take Profit Early)" : "Closed (Cut Loss Early)");
                    }
```

- [ ] **Step 7: The command section**

Insert right before `        private void SendLiveTickTelemetry(bool force = false)`:

```csharp
        // ==========================================
        // DASHBOARD COMMANDS (/api/cbot/commands)
        // ==========================================
        // The dashboard can close this bot's positions (Close, Close & Stop) and pause its new
        // entries (Pause). The server cannot reach a cBot, so the bot asks every CommandPollMs;
        // the reply carries the pause flag and any pending commands. A command not picked up
        // within 15 s expires on the server and is never handed out, so a bot that restarts later
        // cannot act on a stale close. Ids already run are skipped.

        private const string ManualCloseReason = "Manual close (dashboard)";

        // Why this bot closed a position, for OnPositionClosed: cTrader itself only says "Closed".
        private readonly Dictionary<int, string> _closeReasons = new Dictionary<int, string>();

        private TradeResult CloseWithReason(Position pos, string reason)
        {
            _closeReasons[pos.Id] = reason;
            return ClosePosition(pos);
        }

        private class DashboardCommand
        {
            public string id { get; set; }
            public string action { get; set; }
            public long? position_id { get; set; }
        }

        private class DashboardCommandPoll
        {
            public bool paused { get; set; }
            public List<DashboardCommand> commands { get; set; }
        }

        private CancellationTokenSource _commandPollCts;
        private HttpClient _commandHttp;
        private volatile bool _dashboardPaused;
        private readonly HashSet<string> _handledCommandIds = new HashSet<string>();
        private DateTime _lastCommandPollErrorAt = DateTime.MinValue;
        private DateTime _lastPauseLogAt = DateTime.MinValue;

        private void StartCommandPoll()
        {
            if (RunningMode != RunningMode.RealTime || CommandPollMs <= 0) return;
            var baseUrl = BuildCommandBaseUrl();
            if (baseUrl == null) return;

            _commandHttp = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            _commandPollCts = new CancellationTokenSource();
            var token = _commandPollCts.Token;
            var http = _commandHttp;
            var pollUrl = $"{baseUrl}/api/cbot/commands?bot_id={Uri.EscapeDataString(BotId)}";
            Task.Run(() => CommandPollLoopAsync(http, baseUrl, pollUrl, token), token);
            Print($"[Dashboard] Polling {pollUrl} every {CommandPollMs} ms");
        }

        private void StopCommandPoll()
        {
            try { _commandPollCts?.Cancel(); } catch { }
            _commandPollCts = null;
        }

        private string BuildCommandBaseUrl()
        {
            var baseUrl = ApiUrl;
            if (string.IsNullOrWhiteSpace(baseUrl)) return null;

            baseUrl = baseUrl.Trim().Trim('"', '\'', '“', '”', '‘', '’', '`');
            const string tradePath = "/trade";
            if (baseUrl.EndsWith(tradePath)) baseUrl = baseUrl.Substring(0, baseUrl.Length - tradePath.Length);
            baseUrl = baseUrl.TrimEnd('/');
            return baseUrl.StartsWith("http://") || baseUrl.StartsWith("https://") ? baseUrl : null;
        }

        private async Task CommandPollLoopAsync(HttpClient http, string baseUrl, string pollUrl, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var response = await http.GetAsync(pollUrl, token);
                    response.EnsureSuccessStatusCode();
                    var body = await response.Content.ReadAsStringAsync();
                    var poll = JsonSerializer.Deserialize<DashboardCommandPoll>(body);
                    if (poll != null)
                    {
                        _dashboardPaused = poll.paused;
                        foreach (var cmd in poll.commands ?? new List<DashboardCommand>())
                        {
                            if (cmd == null || string.IsNullOrEmpty(cmd.id)) continue;
                            bool isNew;
                            lock (_handledCommandIds) { isNew = _handledCommandIds.Add(cmd.id); }
                            if (!isNew) continue;
                            var command = cmd;
                            BeginInvokeOnMainThread(() => ExecuteDashboardCommand(baseUrl, command));
                        }
                    }
                }
                catch (OperationCanceledException) when (token.IsCancellationRequested) { break; }
                catch (Exception ex)
                {
                    // Keep the last known pause flag; say so at most once a minute.
                    if ((DateTime.UtcNow - _lastCommandPollErrorAt).TotalSeconds >= 60)
                    {
                        _lastCommandPollErrorAt = DateTime.UtcNow;
                        Print($"[Dashboard] Command poll failed: {ex.GetType().Name}: {ex.Message}");
                    }
                }

                try { await Task.Delay(CommandPollMs, token); } catch { break; }
            }
            try { http.Dispose(); } catch { }
        }

        /// <summary>Runs on the cBot thread. Closes only this bot's own positions.</summary>
        private void ExecuteDashboardCommand(string baseUrl, DashboardCommand cmd)
        {
            var own = GetBotPositions();
            List<Position> targets;
            if (cmd.action == "close_all")
                targets = own.ToList();
            else if (cmd.action == "close_position")
                targets = own.Where(p => p.Id == cmd.position_id).ToList();
            else
            {
                PostCommandResult(baseUrl, cmd.id, "failed", $"unknown action '{cmd.action}'", 0, 0);
                return;
            }

            if (cmd.action == "close_position" && targets.Count == 0)
            {
                Print($"[Dashboard] Close #{cmd.position_id}: not among this bot's open positions");
                PostCommandResult(baseUrl, cmd.id, "failed", $"position {cmd.position_id} not found among this bot's open positions", 0, 0);
                return;
            }

            int closed = 0;
            var errors = new List<string>();
            foreach (var pos in targets)
            {
                var result = CloseWithReason(pos, ManualCloseReason);
                if (result != null && result.IsSuccessful) closed++;
                else errors.Add($"#{pos.Id} {(result != null ? result.Error.ToString() : "no result")}");
            }

            string message = errors.Count == 0 ? $"closed {closed}" : $"closed {closed}, failed: {string.Join(", ", errors)}";
            Print($"[Dashboard] {cmd.action}: {message}");
            PostCommandResult(baseUrl, cmd.id, errors.Count == 0 ? "done" : "failed", message, closed, errors.Count);
        }

        private void PostCommandResult(string baseUrl, string commandId, string status, string message, int closed, int failed)
        {
            var http = _commandHttp;
            if (http == null) return;
            var json = JsonSerializer.Serialize(new { bot_id = BotId, status, message, closed, failed });
            var url = $"{baseUrl}/api/cbot/commands/{Uri.EscapeDataString(commandId)}/result";
            Task.Run(async () =>
            {
                try
                {
                    await http.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                }
                catch (Exception ex)
                {
                    Print($"[Dashboard] Could not report command {commandId}: {ex.Message}");
                }
            });
        }

        /// <summary>True while the dashboard has paused this bot's new entries (logged once a minute).</summary>
        private bool DashboardPauseBlocks(string what)
        {
            if (!_dashboardPaused) return false;
            if ((DateTime.UtcNow - _lastPauseLogAt).TotalSeconds >= 60)
            {
                _lastPauseLogAt = DateTime.UtcNow;
                Print($"[Dashboard] Paused from the dashboard: {what} skipped");
            }
            return true;
        }

```

- [ ] **Step 8: Run the tests**

Run: `.venv/bin/pytest tests/test_cbot_command_poll.py tests/test_flow_rsi_order_units.py tests/test_flowrsi_ai_direction_guard.py tests/test_flowrsi_min_lot_risk_cap.py -q -p no:cacheprovider`
Expected: all pass.

Run: `.venv/bin/pytest -q -p no:cacheprovider`
Expected: 0 failed.

- [ ] **Step 9: Checkpoint (no commit)**

Report to the user: the full diff summary, the test count, and that the three `.cs` files still need the VPS compile check. Wait for "commit" / "push" before any git write.

---

### Task 11: Compile on the VPS, deploy, live check — **only when the user asks**

Run as `forge@204.168.144.232`. App lives at `/home/forge/AgentFxTrading` (not `/root`). Never run `scripts/deploy_feature.sh`. Production Postgres writes from an agent session are blocked — nothing here writes to it directly.

- [ ] **Step 1: Compile check without touching production (before any commit)**

```bash
for B in AiAgentBot AsianRangeJudasSweepBot FlowRsiBot; do
  scp cBot/$B.cs forge@204.168.144.232:/tmp/$B.cs
  ssh forge@204.168.144.232 "
    T=\$(mktemp -d) && mkdir -p \$T/cAlgo/Sources/Robots &&
    cp -r /home/forge/ctrader/cAlgo/Sources/Robots/$B \$T/cAlgo/Sources/Robots/ &&
    cp /tmp/$B.cs \$T/cAlgo/Sources/Robots/$B/$B/$B.cs &&
    docker run --rm -v \$T:/root ghcr.io/spotware/ctrader-console:latest build /root/cAlgo/Sources/Robots/$B/$B/$B.csproj ;
    rm -rf \$T /tmp/$B.cs"
done
```

Expected: `"errors": []` for each of the three bots. Fix any error locally, re-run the tests, re-check.

- [ ] **Step 2: After the user has asked for commit + push and the change is on the branch the VPS deploys**

```bash
cd /home/forge/AgentFxTrading && git pull
T=$(mktemp -d) && .venv/bin/python -m pip install -q --target $T pytest && PYTHONPATH=$T .venv/bin/python -m pytest -q -p no:cacheprovider; rm -rf $T
```

Expected: 0 failed.

- [ ] **Step 3: Restart the service away from an M15 bar close (hh:00/15/30/45)**

```bash
sudo -n systemctl restart agentfx.service
systemctl status agentfx.service --no-pager | head -5
curl -s http://127.0.0.1:8000/api/watchdog/status | head -c 300
curl -s "http://127.0.0.1:8000/api/cbot/commands?bot_id=probe"     # expect {"paused":false,"commands":[]}
```

- [ ] **Step 4: Build the three `.algo` files (mirrors `install.sh build_algo`)**

```bash
TS=$(date +%Y%m%d_%H%M%S) && mkdir -p backups/algo_$TS && cp cBot/*.algo backups/algo_$TS/
for B in AiAgentBot AsianRangeJudasSweepBot FlowRsiBot; do
  cp cBot/$B.cs /home/forge/ctrader/cAlgo/Sources/Robots/$B/$B/$B.cs
  docker run --rm -v /home/forge/AgentFxTrading:/workspace -v /home/forge/ctrader:/root \
    ghcr.io/spotware/ctrader-console:latest build /root/cAlgo/Sources/Robots/$B/$B/$B.csproj
  cp /home/forge/ctrader/cAlgo/Sources/Robots/$B.algo cBot/$B.algo
done
sudo -n chown -R forge:forge cBot /home/forge/ctrader/cAlgo/Sources/Robots
```

- [ ] **Step 5: Live check on one demo container per strategy**

Pick one demo container per strategy (`*-london|-newyork|-tokyo` = AiAgentBot, `*-judas` = Judas, `*-all-flowrsi` = FlowRSI) with no open position, `docker restart` it, then:

- `docker logs --tail 30 <container>` shows `[Dashboard] Polling http://127.0.0.1:8000/api/cbot/commands?bot_id=<name> every 2000 ms` and a clean login.
- Bots tab → **Pause**: PAUSED badge; the next `/trade` from that bot logs `Paused from dashboard`. **Resume** clears it.
- When the container has a demo position open: **Close** in Active Positions → row disappears within ~3 s; history shows `Manual close (dashboard)`.
- **Close & Stop** on a demo container with a position: position closed, container stopped, still PAUSED; Start + Resume brings it back.
- `journalctl -u agentfx --since "5 min ago" | grep -c "/api/cbot/commands?"` → `0`.

- [ ] **Step 6: Restart the remaining containers**

Check open positions first (a close during the ~3 min restart window is lost), then `docker restart` in batches of 5 with ~60 s gaps; after each batch `docker logs --tail 20 <container>` for a clean login and the `[Dashboard] Polling` line.
