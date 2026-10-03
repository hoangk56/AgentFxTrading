
import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from app import cbot_watchdog as wd
from app.cbot_watchdog import CbotWatchdog
from app.docker_manager import DockerManager

def test_check_cbot_health_stuck_log():
    dm = DockerManager()
    dm.is_available = True
    dm.get_container_status = MagicMock(return_value={"status": "running", "id": "12345"})

    stuck_log = """
Login to 6094347...
Connection Error: Unknown
Login failed. Retrying in 4 seconds...
Login to 6094347...
Connection Error: Unknown
All login retry attempts failed, moving to reconnection state.
08/09/2026 01:00:02.969 | The connection has been lost. Reconnecting...
08/09/2026 01:00:02.969 | Establishing connection using senior1206@gmail.com...
08/09/2026 01:00:03.055 | The connection has been restored.
"""
    dm.get_container_logs = MagicMock(return_value=stuck_log)
    health = dm.check_cbot_health("cbot-usdjpy")
    assert health["healthy"] is False
    assert health["stuck"] is True
    assert "All login retry attempts failed" in health["reason"]

def test_check_cbot_health_healthy_log():
    dm = DockerManager()
    dm.is_available = True
    dm.get_container_status = MagicMock(return_value={"status": "running", "id": "12345"})

    healthy_log = """
08/09/2026 01:44:21.919 | Establishing connection using senior1206@gmail.com...
08/09/2026 01:44:35.140 | The connection has been established.
Login to 6094347...
Logged in.
Starting cBot...
Info | CBot instance [GotobiBot, USDJPY, m15] started.
"""
    dm.get_container_logs = MagicMock(return_value=healthy_log)
    health = dm.check_cbot_health("cbot-usdjpy")
    assert health["healthy"] is True
    assert health["stuck"] is False

def test_check_cbot_health_reconnect_loop_is_stuck():
    # CLI 5.10 prints no "Login failed" when the cTID is rejected (e.g. "Password was not
    # set for this cTID"): it just alternates lost/establishing ~3x per second forever.
    dm = DockerManager()
    dm.is_available = True
    dm.get_container_status = MagicMock(return_value={"status": "running", "id": "12345"})

    loop_log = "| ShowLogs             | True                      | default value        |\n"
    loop_log += "---------------------------------------------------------------------------\n"
    for i in range(10):
        loop_log += f"21/09/2026 08:38:1{i}.522 | Establishing connection using someone@example.com...\n"
        loop_log += f"21/09/2026 08:38:1{i}.288 | The connection has been lost. Reconnecting...\n"
    dm.get_container_logs = MagicMock(return_value=loop_log)
    health = dm.check_cbot_health("cbot-demo-xauusd")
    assert health["healthy"] is False
    assert health["stuck"] is True
    assert "reconnect" in health["reason"].lower()

def test_check_cbot_health_transient_reconnect_then_restored_is_healthy():
    dm = DockerManager()
    dm.is_available = True
    dm.get_container_status = MagicMock(return_value={"status": "running", "id": "12345"})

    blip_log = """
21/09/2026 10:11:44.306 | Info | CBot instance [GotobiBot, USDJPY, m15] started.
21/09/2026 12:00:01.000 | The connection has been lost. Reconnecting...
21/09/2026 12:00:01.001 | Establishing connection using someone@example.com...
21/09/2026 12:00:01.300 | The connection has been lost. Reconnecting...
21/09/2026 12:00:01.301 | Establishing connection using someone@example.com...
21/09/2026 12:00:01.600 | The connection has been lost. Reconnecting...
21/09/2026 12:00:01.601 | Establishing connection using someone@example.com...
21/09/2026 12:00:01.900 | The connection has been lost. Reconnecting...
21/09/2026 12:00:01.901 | Establishing connection using someone@example.com...
21/09/2026 12:00:02.200 | The connection has been lost. Reconnecting...
21/09/2026 12:00:02.201 | Establishing connection using someone@example.com...
21/09/2026 12:00:02.500 | The connection has been restored.
"""
    dm.get_container_logs = MagicMock(return_value=blip_log)
    health = dm.check_cbot_health("cbot-demo-xauusd")
    assert health["healthy"] is True
    assert health["stuck"] is False

def test_check_cbot_health_not_running():
    dm = DockerManager()
    dm.is_available = True
    dm.get_container_status = MagicMock(return_value={"status": "exited", "id": "12345"})
    health = dm.check_cbot_health("cbot-usdjpy")
    assert health["healthy"] is False
    assert health["stuck"] is False

@patch("app.cbot_watchdog.docker_manager")
@patch("app.cbot_watchdog.get_portfolio_manager")
def test_check_and_heal_caches_health_for_the_dashboard(mock_get_pm, mock_dm):
    mock_dm.is_available = True
    mock_pm = MagicMock()
    mock_pm.get_cbot_configs.return_value = [{"name": "cbot-a"}, {"name": "cbot-b"}]
    mock_get_pm.return_value = mock_pm
    healthy = {"status": "running", "healthy": True, "stuck": False, "reason": "Healthy and running"}
    exited = {"status": "exited", "healthy": False, "stuck": False, "reason": "Container is exited"}
    mock_dm.check_cbot_health.side_effect = lambda name: healthy if name == "cbot-a" else exited

    watchdog = CbotWatchdog()
    assert watchdog.last_health("cbot-a") is None          # nothing before the first cycle
    watchdog.check_and_heal()
    assert watchdog.last_health("cbot-a") == healthy
    assert watchdog.last_health("cbot-b") == exited

    # A bot whose config was deleted drops out on the next cycle.
    mock_pm.get_cbot_configs.return_value = [{"name": "cbot-a"}]
    watchdog.check_and_heal()
    assert watchdog.last_health("cbot-b") is None

def test_watchdog_cooldown_and_backoff():
    watchdog = CbotWatchdog(
        cooldown_seconds=10,
        max_restarts_in_window=3,
        window_seconds=60,
        backoff_cooldown_seconds=30
    )

    can_restart, _ = watchdog._can_restart("test-bot")
    assert can_restart is True

    # 1st restart
    watchdog._record_restart("test-bot", "reason 1", True, "ok")
    can_restart, msg = watchdog._can_restart("test-bot")
    assert can_restart is False
    assert "Cooldown active" in msg

    # Simulate cooldown passing
    watchdog._restart_history["test-bot"][-1] -= 15
    can_restart, _ = watchdog._can_restart("test-bot")
    assert can_restart is True

    # 2nd and 3rd restarts
    watchdog._record_restart("test-bot", "reason 2", True, "ok")
    watchdog._restart_history["test-bot"][-1] -= 15
    watchdog._record_restart("test-bot", "reason 3", True, "ok")

    # Now max_restarts reached (3 in window) -> backoff triggers
    can_restart, msg = watchdog._can_restart("test-bot")
    assert can_restart is False
    assert "Backoff active" in msg

@patch("app.cbot_watchdog.docker_manager")
@patch("app.cbot_watchdog.get_portfolio_manager")
def test_watchdog_check_and_heal(mock_get_pm, mock_dm):
    mock_dm.is_available = True
    mock_pm = MagicMock()
    mock_pm.get_cbot_configs.return_value = [{"name": "cbot-usdjpy"}]
    mock_get_pm.return_value = mock_pm

    # Case 1: Bot is stuck -> triggers restart
    mock_dm.check_cbot_health.return_value = {
        "status": "running",
        "stuck": True,
        "reason": "All login retry attempts failed"
    }
    mock_dm.restart_container.return_value = {"success": True, "message": "restarted"}

    watchdog = CbotWatchdog(cooldown_seconds=100)
    actions = watchdog.check_and_heal()

    assert len(actions) == 1
    assert actions[0]["name"] == "cbot-usdjpy"
    assert actions[0]["success"] is True
    mock_dm.restart_container.assert_called_once_with("cbot-usdjpy", timeout=15)

    # Case 2: Immediate next check -> blocked by cooldown
    actions2 = watchdog.check_and_heal()
    assert len(actions2) == 0


# ---------------------------------------------------------------------------
# Bar heartbeat carried on the tick stream: each tick frame carries the last bar the bot handled; a bot
# whose ticks keep flowing while that stops advancing has a stalled bar pipeline.
# ---------------------------------------------------------------------------

GOTOBI_BOT = "cbot-demo-main-usdjpy-fix-gotobi"
GOTOBI_RUN_COMMAND = (
    f"docker run -d --name {GOTOBI_BOT} --network host "
    f"run /workspace/cBot/GotobiBot.algo --BotId=\"{GOTOBI_BOT}\" --RiskPerTradeMoney=50.0"
)
NOW = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _clean_tick_telemetry():
    wd.reset_tick_telemetry()
    yield
    wd.reset_tick_telemetry()


def _stream(bot_id, last_bar, start, end, step=timedelta(minutes=2)):
    t = start
    while t <= end:
        bar = last_bar(t) if callable(last_bar) else last_bar
        wd.record_bot_tick(bot_id, bar, now=t.timestamp())
        t += step


def test_bar_stall_flags_a_bot_whose_ticks_flow_but_bars_stop():
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", NOW - timedelta(minutes=60), NOW)
    reason = CbotWatchdog(stale_feed_seconds=2400)._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW)
    assert reason is not None
    assert "60 min" in reason and "2026-09-24T08:45:00" in reason


def test_bar_stall_ignores_healthy_bot_whose_bars_advance():
    quarter = lambda t: t.replace(minute=t.minute // 15 * 15, second=0).strftime("%Y-%m-%dT%H:%M:%S")
    _stream(GOTOBI_BOT, quarter, NOW - timedelta(minutes=90), NOW)
    assert CbotWatchdog(stale_feed_seconds=2400)._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW) is None


def test_bar_stall_ignores_a_closed_market():
    """No ticks means no market (weekend): silence is expected."""
    _stream(GOTOBI_BOT, "2026-09-24T08:00:00", NOW - timedelta(minutes=90), NOW - timedelta(minutes=10))
    assert CbotWatchdog(stale_feed_seconds=2400)._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW) is None


def test_bar_stall_gives_the_first_bar_after_a_reopen_its_full_allowance():
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", NOW - timedelta(minutes=70), NOW - timedelta(minutes=60))
    # market shut for 40 min, ticks resume 20 min ago with no bar closed yet
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", NOW - timedelta(minutes=20), NOW)
    assert CbotWatchdog(stale_feed_seconds=2400)._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW) is None


def test_bar_stall_ignores_bots_without_bar_telemetry():
    """A build that sends ticks without last_bar: nothing to judge by."""
    _stream(GOTOBI_BOT, None, NOW - timedelta(minutes=60), NOW)
    assert CbotWatchdog(stale_feed_seconds=2400)._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW) is None


def test_bar_stall_heals_once_per_stalled_bar():
    watchdog = CbotWatchdog(stale_feed_seconds=2400)
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", NOW - timedelta(minutes=60), NOW)
    assert watchdog._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, NOW) is not None
    # restarted bot still warming up on the same bar -> latched, no restart loop
    later = NOW + timedelta(minutes=10)
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", NOW, later)
    assert watchdog._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, later) is None
    # it recovers, then stalls again on a new bar -> eligible again
    _stream(GOTOBI_BOT, "2026-09-24T10:00:00", later, later + timedelta(minutes=50))
    assert watchdog._bar_stall_reason(GOTOBI_BOT, GOTOBI_RUN_COMMAND, later + timedelta(minutes=50)) is not None


@patch("app.cbot_watchdog.docker_manager")
@patch("app.cbot_watchdog.get_portfolio_manager")
def test_watchdog_heals_a_bot_with_stalled_bars(mock_get_pm, mock_dm):
    mock_dm.is_available = True
    mock_dm.check_cbot_health.return_value = {
        "status": "running", "stuck": False, "healthy": True, "reason": "Healthy and running"
    }
    mock_dm.restart_container.return_value = {"success": True, "message": "restarted"}
    mock_pm = MagicMock()
    mock_pm.get_cbot_configs.return_value = [{"name": GOTOBI_BOT, "run_command": GOTOBI_RUN_COMMAND}]
    mock_get_pm.return_value = mock_pm

    now = datetime.now(timezone.utc)
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", now - timedelta(minutes=60), now)
    actions = CbotWatchdog(stale_feed_seconds=2400).check_and_heal()

    assert [a["name"] for a in actions] == [GOTOBI_BOT]
    assert "no bar handled" in actions[0]["reason"]
    mock_dm.restart_container.assert_called_once_with(GOTOBI_BOT, timeout=15)


def test_status_exposes_the_bar_heartbeat():
    now = datetime.now(timezone.utc)
    _stream(GOTOBI_BOT, "2026-09-24T08:45:00", now - timedelta(minutes=4), now)
    status = CbotWatchdog().get_status()
    assert "feed_telemetry" not in status
    beat = status["bar_telemetry"][GOTOBI_BOT]
    assert beat["last_bar"] == "2026-09-24T08:45:00"
    assert 200 <= beat["bar_age"] <= 300
    assert beat["tick_age"] < 60


# ---------------------------------------------------------------------------
# The allowance follows the bot's chart: a bot on H1 (as the removed Crypto Donchian was) gets a bar once an hour,
# and the M15 allowance (40 min) would call it stalled between minutes 40 and 60 of every hour.
# ---------------------------------------------------------------------------

H1_BOT = "cbot-demo-main-usdjpy-h1-gotobi"
H1_RUN_COMMAND = (
    f"docker run -d --name {H1_BOT} --network host run /workspace/cBot/GotobiBot.algo "
    f"--symbol=USDJPY --period=h1 --full-access --BotId=\"{H1_BOT}\" --RiskPerTradeMoney=100.0"
)


@pytest.mark.parametrize("command, seconds", [
    (H1_RUN_COMMAND, 3600),
    ("run x.algo --period=m15 --BotId=a", 900),
    ('run x.algo --period="m5" --BotId=a', 300),
    ("run x.algo --period=h4 --BotId=a", 14400),
    ("run x.algo --period=d1 --BotId=a", 86400),
    ("run x.algo --BotId=a", 900),              # no --period: the M15 default
    ("run x.algo --period=t100 --BotId=a", 900),  # tick charts have no bar clock
    (None, 900),
])
def test_parse_bar_seconds(command, seconds):
    assert wd.parse_bar_seconds(command) == seconds


def test_bar_allowance_keeps_the_m15_value_and_gives_slower_charts_one_bar_plus_the_same_slack():
    watchdog = CbotWatchdog(stale_feed_seconds=2400)
    assert watchdog.bar_allowance_seconds(GOTOBI_RUN_COMMAND) == 2400            # m15 by default
    assert watchdog.bar_allowance_seconds("run x.algo --period=m5") == 2400      # faster charts keep the floor
    assert watchdog.bar_allowance_seconds(H1_RUN_COMMAND) == 3600 + 1500   # one H1 bar + 25 min


def test_h1_bot_whose_bars_advance_hourly_is_never_called_stalled():
    hourly = lambda t: t.replace(minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%S")
    watchdog = CbotWatchdog(stale_feed_seconds=2400)
    start = NOW - timedelta(hours=3)
    t = start
    while t <= NOW:
        wd.record_bot_tick(H1_BOT, hourly(t), now=t.timestamp())
        assert watchdog._bar_stall_reason(H1_BOT, H1_RUN_COMMAND, t) is None, t
        t += timedelta(minutes=5)


def test_h1_bot_is_restarted_once_it_misses_a_whole_bar():
    watchdog = CbotWatchdog(stale_feed_seconds=2400)
    _stream(H1_BOT, "2026-09-24T08:00:00", NOW - timedelta(minutes=80), NOW)
    assert watchdog._bar_stall_reason(H1_BOT, H1_RUN_COMMAND, NOW) is None       # 80 min < 85
    later = NOW + timedelta(minutes=10)
    _stream(H1_BOT, "2026-09-24T08:00:00", NOW, later)
    reason = watchdog._bar_stall_reason(H1_BOT, H1_RUN_COMMAND, later)
    assert reason is not None and "90 min" in reason and "bar cycle is H1" in reason


def test_status_exposes_each_bots_allowance():
    now = datetime.now(timezone.utc)
    _stream(H1_BOT, "2026-09-24T08:00:00", now - timedelta(minutes=4), now)
    watchdog = CbotWatchdog(stale_feed_seconds=2400)
    watchdog._bar_stall_reason(H1_BOT, H1_RUN_COMMAND)
    assert watchdog.get_status()["bar_telemetry"][H1_BOT]["allowance"] == 5100
