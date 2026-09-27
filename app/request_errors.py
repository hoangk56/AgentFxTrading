"""Logs the HTTP requests that end badly: an unhandled exception (ERROR, with its traceback), a 5xx answer (ERROR)
or a 4xx answer (WARNING), each with the start of the response body.

uvicorn logs these only to its own loggers, which reach journald but not the agent log, the dashboard or the
Telegram alerts. Added inside LoginMiddleware (app/server.py), so visitors turned away by the login are not logged.
The same method, path and status is logged at most once a minute.
"""
import logging
from typing import Optional

from app.logging_setup import Throttle, log_throttled

logger = logging.getLogger("AgentFxTrading.Requests")

MAX_BODY = 300


class RequestErrorLogMiddleware:
    """Pure ASGI, so a streamed or file response passes through untouched; only an error body is kept."""

    def __init__(self, app, throttle: Optional[Throttle] = None):
        self.app = app
        self.throttle = throttle or Throttle(60)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        status = 0
        body = bytearray()

        async def send_and_watch(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            elif message["type"] == "http.response.body" and status >= 400 and len(body) <= MAX_BODY:
                body.extend(message.get("body", b"")[:MAX_BODY + 1 - len(body)])
            await send(message)

        route = f"{scope.get('method', '')} {scope.get('path', '')}"
        try:
            await self.app(scope, receive, send_and_watch)
        except Exception:
            log_throttled(logger, logging.ERROR, (route, "exception"), f"Unhandled error on {route}",
                          exc_info=True, throttle=self.throttle)
            raise

        if status >= 400:
            text = body.decode("utf-8", "replace")
            if len(text) > MAX_BODY:
                text = text[:MAX_BODY] + "…"
            level = logging.ERROR if status >= 500 else logging.WARNING
            log_throttled(logger, level, (route, status), f"HTTP {status} on {route}: {text}", throttle=self.throttle)
