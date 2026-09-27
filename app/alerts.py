"""Telegram alerts: ERROR / CRITICAL log lines and a few events (server start / stop, watchdog restarts).

Off unless TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are both set (app/server.py calls setup_alerts() outside tests).
Messages go out from one background thread, so a slow or unreachable Telegram never blocks a request; a repeated
alert is sent once per cooldown with the number of repeats it held back. A failed send is printed to stderr
(journald), never logged: the log line would come straight back here.
"""
import json
import logging
import os
import queue
import re
import socket
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable, Hashable, Mapping, Optional

from app.logging_setup import Throttle

TELEGRAM_API = "https://api.telegram.org"
MAX_TEXT = 4000            # Telegram refuses messages over 4096 characters
TRACEBACK_LINES = 12
DEFAULT_COOLDOWN = 900     # the same alert at most once every 15 minutes

Sender = Callable[[str], None]


def telegram_sender(token: str, chat_id: str, timeout: float = 10.0) -> Sender:
    """A function that posts one message to the chat; raises RuntimeError (without the token) when it fails."""
    url = f"{TELEGRAM_API}/bot{token}/sendMessage"

    def send(text: str) -> None:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text,
                                       "disable_web_page_preview": "true"}).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=timeout) as res:
                res.read()
        except urllib.error.HTTPError as e:
            try:
                reason = json.loads(e.read().decode("utf-8", "replace")).get("description") or e.reason
            except Exception:
                reason = e.reason
            raise RuntimeError(f"Telegram sendMessage failed: HTTP {e.code} {reason}".replace(token, "***")) from None
        except Exception as e:
            raise RuntimeError(f"Telegram sendMessage failed: {type(e).__name__}: {e}".replace(token, "***")) from None

    return send


class Alerter:
    """Queues alerts for one background sender thread, dropping them when the queue is full."""

    def __init__(self, send: Sender, title: Optional[str] = None, cooldown: float = DEFAULT_COOLDOWN,
                 clock: Callable[[], float] = time.monotonic, max_queue: int = 100):
        self.send = send
        self.title = title or f"AgentFx @ {socket.gethostname()}"
        self._throttle = Throttle(cooldown, clock=clock)
        self._queue: "queue.Queue[str]" = queue.Queue(maxsize=max_queue)
        self._worker: Optional[threading.Thread] = None
        self._worker_lock = threading.Lock()

    def notify(self, text: str, key: Optional[Hashable] = None) -> bool:
        """Queue `text`; with a key, once per cooldown. False when held back or dropped."""
        if key is not None:
            held = self._throttle.hit(key)
            if held is None:
                return False
            if held:
                text = f"{text}\n(+{held} similar held back since the last alert)"
        message = f"{self.title}\n{text}"
        if len(message) > MAX_TEXT:
            message = message[:MAX_TEXT - 1] + "…"
        self._start_worker()
        try:
            self._queue.put_nowait(message)
        except queue.Full:
            print("[alerts] queue full, alert dropped", file=sys.stderr)
            return False
        return True

    def flush(self, timeout: float = 5.0) -> bool:
        """Wait until every queued alert has been sent (or has failed); False on timeout."""
        deadline = time.monotonic() + timeout
        with self._queue.all_tasks_done:
            while self._queue.unfinished_tasks:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._queue.all_tasks_done.wait(remaining)
        return True

    def _start_worker(self) -> None:
        with self._worker_lock:
            if self._worker is None:
                self._worker = threading.Thread(target=self._run, name="telegram-alerts", daemon=True)
                self._worker.start()

    def _run(self) -> None:
        while True:
            message = self._queue.get()
            try:
                self.send(message)
            except Exception as e:
                print(f"[alerts] {e}", file=sys.stderr)
            finally:
                self._queue.task_done()


class AlertHandler(logging.Handler):
    """Sends ERROR and CRITICAL records; lines that differ only in their numbers count as one alert."""

    def __init__(self, alerter: Alerter):
        super().__init__(level=logging.ERROR)
        self.alerter = alerter

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
            text = f"🔴 {record.levelname} · {record.name}\n{message}"
            if record.exc_info:
                lines = "".join(traceback.format_exception(*record.exc_info)).rstrip().splitlines()
                if len(lines) > TRACEBACK_LINES:
                    lines = [lines[0], "  …"] + lines[-TRACEBACK_LINES:]
                text += "\n" + "\n".join(lines)
            key = (record.name, re.sub(r"\d+", "#", message)[:200])
            self.alerter.notify(text, key=key)
        except Exception:
            self.handleError(record)


_alerter: Optional[Alerter] = None


def setup_alerts(env: Mapping[str, str] = os.environ, root: Optional[logging.Logger] = None) -> Optional[Alerter]:
    """Turn the alerts on when the Telegram bot token and chat id are both set."""
    global _alerter
    token, chat_id = (env.get("TELEGRAM_BOT_TOKEN") or "").strip(), (env.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        return None
    _alerter = Alerter(telegram_sender(token, chat_id))
    (root or logging.getLogger()).addHandler(AlertHandler(_alerter))
    return _alerter


def notify(text: str, key: Optional[Hashable] = None) -> bool:
    """Send an event (not a log line) to Telegram; a no-op while alerts are off."""
    return _alerter.notify(text, key=key) if _alerter is not None else False


def flush(timeout: float = 5.0) -> bool:
    return _alerter.flush(timeout) if _alerter is not None else True
