"""Telegram alerts (app/alerts.py): ERROR / CRITICAL log lines and a few events (server start / stop, watchdog
restarts) reach a Telegram chat, without blocking the server and without flooding the chat."""
import io
import json
import logging
import threading
import urllib.error
import urllib.parse
from unittest.mock import MagicMock, patch

import pytest

from app import alerts
from app.alerts import AlertHandler, Alerter, setup_alerts, telegram_sender
from app.cbot_watchdog import CbotWatchdog

TOKEN = "123456:ABC-secret-token"


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def _alerter(sent, **kw):
    kw.setdefault("title", "AgentFx @ vps")
    return Alerter(sent.append, **kw)


@pytest.fixture
def no_global_alerter(monkeypatch):
    monkeypatch.setattr(alerts, "_alerter", None)


def test_notify_sends_the_text_under_the_title():
    sent = []
    alerter = _alerter(sent)
    assert alerter.notify("🟢 Server started") is True
    assert alerter.flush(2)
    assert sent == ["AgentFx @ vps\n🟢 Server started"]


def test_a_repeated_key_is_sent_once_per_cooldown_with_the_count_it_held_back():
    sent, clock = [], FakeClock()
    alerter = _alerter(sent, cooldown=900, clock=clock)
    for _ in range(3):
        alerter.notify("DB down", key="db")
    alerter.notify("other", key="other")
    clock.now += 901
    alerter.notify("DB down", key="db")
    assert alerter.flush(2)
    assert sent == ["AgentFx @ vps\nDB down", "AgentFx @ vps\nother",
                    "AgentFx @ vps\nDB down\n(+2 tin tương tự đã gộp từ lần báo trước)"]


def test_notify_without_a_key_always_sends():
    sent = []
    alerter = _alerter(sent)
    alerter.notify("a")
    alerter.notify("a")
    assert alerter.flush(2)
    assert len(sent) == 2


def test_a_long_text_is_cut_to_what_telegram_accepts():
    sent = []
    alerter = _alerter(sent)
    alerter.notify("x" * 10_000)
    assert alerter.flush(2)
    assert len(sent[0]) <= 4000 and sent[0].endswith("…")


def test_a_failed_send_goes_to_stderr_not_to_the_log_and_later_alerts_still_go(capsys, caplog):
    sent = []

    def send(text):
        if not sent:
            sent.append("failed")
            raise RuntimeError("Telegram sendMessage failed: HTTP 400 chat not found")
        sent.append(text)

    alerter = Alerter(send, title="t")
    with caplog.at_level(logging.DEBUG):
        alerter.notify("one")
        alerter.notify("two")
        assert alerter.flush(2)
    assert sent == ["failed", "t\ntwo"]
    assert "chat not found" in capsys.readouterr().err
    assert caplog.records == []            # logging it would feed the alert handler: a loop


def test_a_full_queue_drops_the_alert_instead_of_blocking_the_caller():
    started, release = threading.Event(), threading.Event()

    def send(text):
        started.set()
        release.wait(5)

    alerter = Alerter(send, title="t", max_queue=2)
    alerter.notify("in flight")
    assert started.wait(2)
    assert alerter.notify("queued 1") and alerter.notify("queued 2")
    assert alerter.notify("dropped") is False
    release.set()
    assert alerter.flush(2)


def _logger_with(handler):
    log = logging.getLogger("tests.alerts.handler")
    log.handlers[:] = [handler]
    log.propagate = False
    log.setLevel(logging.DEBUG)
    return log


def test_the_handler_alerts_on_error_and_critical_only():
    sent = []
    log = _logger_with(AlertHandler(_alerter(sent)))
    log.info("fine")
    log.warning("meh")
    log.error("Portfolio report error: boom")
    log.critical("disk full")
    assert log.handlers[0].alerter.flush(2)
    assert sent == ["AgentFx @ vps\n🔴 LỖI · tests.alerts.handler\nLỗi nhận báo cáo lệnh từ bot: boom",
                    "AgentFx @ vps\n🔴 NGHIÊM TRỌNG · tests.alerts.handler\ndisk full"]


def test_the_handler_sends_the_end_of_the_traceback():
    sent = []
    log = _logger_with(AlertHandler(_alerter(sent)))
    try:
        raise ValueError("bad value")
    except ValueError:
        log.error("Unhandled error on POST /portfolio/report", exc_info=True)
    assert log.handlers[0].alerter.flush(2)
    assert "Lỗi chưa được xử lý ở POST /portfolio/report\nTraceback (most recent call last):" in sent[0]
    assert sent[0].endswith("ValueError: bad value")


def test_the_handler_groups_messages_that_differ_only_in_numbers():
    sent, clock = [], FakeClock()
    log = _logger_with(AlertHandler(_alerter(sent, clock=clock)))
    log.error("Failed to restart bot 'cbot-1': HTTP 500")
    log.error("Failed to restart bot 'cbot-2': HTTP 502")
    log.error("Something else")
    assert log.handlers[0].alerter.flush(2)
    assert len(sent) == 2


def test_telegram_sender_posts_to_send_message():
    calls = []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        calls.append((req, timeout))
        return Response(b'{"ok": true}')

    with patch.object(alerts.urllib.request, "urlopen", urlopen):
        telegram_sender(TOKEN, "-100200")("hello")
    req, timeout = calls[0]
    assert req.full_url == f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    assert urllib.parse.parse_qs(req.data.decode()) == {
        "chat_id": ["-100200"], "text": ["hello"], "disable_web_page_preview": ["true"]}
    assert timeout == 10


def test_telegram_sender_reports_telegrams_reason_without_the_token():
    body = json.dumps({"ok": False, "description": "Bad Request: chat not found"}).encode()
    error = urllib.error.HTTPError(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 400, "Bad Request", {},
                                   io.BytesIO(body))
    with patch.object(alerts.urllib.request, "urlopen", side_effect=error):
        with pytest.raises(RuntimeError) as exc:
            telegram_sender(TOKEN, "-100200")("hello")
    assert "HTTP 400" in str(exc.value) and "chat not found" in str(exc.value)
    assert TOKEN not in str(exc.value)


def test_setup_alerts_needs_both_the_token_and_the_chat(no_global_alerter):
    log = logging.getLogger("tests.alerts.setup")
    assert setup_alerts({"TELEGRAM_BOT_TOKEN": TOKEN}, root=log) is None
    assert setup_alerts({"TELEGRAM_CHAT_ID": "1"}, root=log) is None
    assert log.handlers == []


def test_setup_alerts_attaches_the_handler_and_the_module_notify(no_global_alerter):
    log = logging.getLogger("tests.alerts.setup2")
    try:
        alerter = setup_alerts({"TELEGRAM_BOT_TOKEN": TOKEN, "TELEGRAM_CHAT_ID": "1"}, root=log)
        assert alerter is not None and alerts._alerter is alerter
        assert [type(h) for h in log.handlers] == [AlertHandler]
        assert log.handlers[0].level == logging.ERROR
    finally:
        log.handlers.clear()


def test_module_notify_is_a_no_op_until_alerts_are_set_up(no_global_alerter):
    assert alerts.notify("x") is False
    assert alerts.flush(0.1) is True


def _stuck_bot(mock_get_pm, mock_dm):
    mock_dm.is_available = True
    mock_get_pm.return_value = MagicMock(get_cbot_configs=MagicMock(return_value=[{"name": "cbot-usdjpy"}]))
    mock_dm.check_cbot_health.return_value = {"status": "running", "stuck": True, "reason": "Login failed"}
    mock_dm.restart_container.return_value = {"success": True, "message": "restarted"}


@patch("app.cbot_watchdog.docker_manager")
@patch("app.cbot_watchdog.get_portfolio_manager")
def test_the_watchdog_alerts_when_it_restarts_a_bot_but_not_during_the_cooldown(mock_get_pm, mock_dm, monkeypatch):
    sent = []
    monkeypatch.setattr(alerts, "_alerter", _alerter(sent))
    _stuck_bot(mock_get_pm, mock_dm)
    watchdog = CbotWatchdog(cooldown_seconds=100)
    watchdog.check_and_heal()
    watchdog.check_and_heal()             # still logging in after the restart: the cooldown is routine
    assert alerts.flush(2)
    assert sent == ["AgentFx @ vps\n🟠 Watchdog đã khởi động lại cbot-usdjpy: Login failed"]


@patch("app.cbot_watchdog.docker_manager")
@patch("app.cbot_watchdog.get_portfolio_manager")
def test_the_watchdog_alerts_when_it_gives_up_on_a_bot(mock_get_pm, mock_dm, monkeypatch):
    sent = []
    monkeypatch.setattr(alerts, "_alerter", _alerter(sent))
    _stuck_bot(mock_get_pm, mock_dm)
    watchdog = CbotWatchdog(max_restarts_in_window=1)
    watchdog.check_and_heal()
    watchdog.check_and_heal()             # backoff: restarts did not help
    watchdog.check_and_heal()             # same episode: one alert per cooldown
    assert alerts.flush(2)
    assert len(sent) == 2
    assert sent[1].startswith("AgentFx @ vps\n🔴 Watchdog ngừng tự khởi động lại cbot-usdjpy (Login failed): tạm ngừng tự khởi động lại")


def test_the_server_says_when_it_starts_and_when_it_stops(monkeypatch):
    """A "started" with no "stopping" before it is a crash that systemd restarted without a word."""
    import os
    from fastapi.testclient import TestClient
    from app.cbot_watchdog import cbot_watchdog
    from app.server import app

    async def idle():
        return None

    monkeypatch.setattr(cbot_watchdog, "run_loop", idle)
    sent = []
    monkeypatch.setattr(alerts, "_alerter", _alerter(sent))
    with TestClient(app):
        assert alerts.flush(2)
        assert sent == [f"AgentFx @ vps\n🟢 Server đã khởi động (pid {os.getpid()})"]
    assert sent[-1] == "AgentFx @ vps\n⚪ Server đang dừng"
