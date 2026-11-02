import os
import sys
from pathlib import Path
import uvicorn
import logging
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env
load_dotenv(PROJECT_ROOT / ".env", override=True)

import asyncio

# The log format, the GMT+7 formatter, the daily file handler and the uvicorn access-log filter live
# in app/logging_setup.py. Logging is still configured here, at import time, before the app modules load.
from app.logging_setup import (_LOG_FORMAT, GMT7Formatter, is_running_under_test, setup_agent_logging,
                               SkipCommandPollAccessLog)

setup_agent_logging(logging.INFO)
logger = logging.getLogger("AgentFxTrading")


logging.getLogger("uvicorn.access").addFilter(SkipCommandPollAccessLog())
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.portfolio import init_portfolio
from app.dashboard import router as dashboard_router, manager as ws_manager, WebSocketLogHandler
from app.accounts import init_account_registry
from app.portfolio_api import router as portfolio_router


# Attach WebSocket live log handler to root logger
_ws_handler = WebSocketLogHandler(ws_manager)
_ws_handler.setFormatter(GMT7Formatter(_LOG_FORMAT, datefmt="%H:%M:%S"))
_ws_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(_ws_handler)

# Telegram alerts for ERROR / CRITICAL lines and server / watchdog events (app/alerts.py). Off in tests, and until
# TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set.
from app import alerts
if not is_running_under_test():
    alerts.setup_alerts()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        loop = asyncio.get_running_loop()
        ws_manager.set_event_loop(loop)
    except Exception as e:
        logger.warning(f"Failed to set event loop for ws_manager: {e}")

    alerts.notify(f"🟢 Server đã khởi động (pid {os.getpid()})")

    # Start cBot Watchdog service for automatic relogin and crash recovery
    from app.cbot_watchdog import cbot_watchdog
    watchdog_task = asyncio.create_task(cbot_watchdog.run_loop())

    # Backtest worker. Never under pytest: it removes every container labelled agentfx.backtest whose
    # job is not running in *its* DB, and a test run points at a throwaway SQLite file.
    from app.backtest_worker import backtest_worker
    backtest_task = None
    forward_task = None
    paper_desk_task = None
    if not is_running_under_test():
        backtest_task = asyncio.create_task(backtest_worker.run_loop())
        # Telegram alert when a research candidate turns STOP or PROMOTE_CHECK (app/forward_status.py).
        from app.forward_status import ForwardAlerts
        forward_task = asyncio.create_task(ForwardAlerts(alerts.notify).run_loop())
        # Telegram alert when the paper desk misses a day or its calls fail (app/paper_desk_status.py).
        from app.paper_desk_status import PaperDeskAlerts
        paper_desk_task = asyncio.create_task(PaperDeskAlerts(alerts.notify).run_loop())

    yield

    alerts.notify("⚪ Server đang dừng")
    # Shutdown watchdog cleanly
    cbot_watchdog.stop()
    watchdog_task.cancel()
    try:
        await watchdog_task
    except asyncio.CancelledError:
        pass
    for task in (forward_task, paper_desk_task):
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    if backtest_task:
        backtest_worker.stop()
        backtest_task.cancel()
        try:
            await backtest_task
        except asyncio.CancelledError:
            pass
    await asyncio.to_thread(alerts.flush, 5)   # let the queued alerts out before the process exits

app = FastAPI(title="AgentFx Server", lifespan=lifespan)

# Dashboard login (app/auth.py): every request needs a session, except the cBots' and local scripts' calls to
# 127.0.0.1:8000 that do not come through nginx.
from app.auth import LoginMiddleware, login_enabled, router as auth_router
# Requests that end in an exception or an HTTP error reach the agent log (app/request_errors.py). Added first, so
# it sits inside LoginMiddleware: visitors the login turns away are not logged.
from app.request_errors import RequestErrorLogMiddleware
app.add_middleware(RequestErrorLogMiddleware)
app.add_middleware(LoginMiddleware)
app.include_router(auth_router)
if not login_enabled() and not is_running_under_test():
    logger.warning("DASHBOARD_USERNAME / DASHBOARD_PASSWORD are not set: the dashboard has no login")

# Mount static files
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")

# Mount dashboard router
app.include_router(dashboard_router)
from app.backtest_api import router as backtest_router
app.include_router(backtest_router)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = PROJECT_ROOT / "static" / "favicon.png"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return ""
# Initialize Account Registry (accounts are created on the dashboard's Setup Instances screen)
account_registry = init_account_registry()

# Initialize Portfolio Manager. Code reads it through get_portfolio_manager() at call time, so
# app.portfolio.portfolio_manager is the one place to replace it; this name is kept for importers.
portfolio_manager = init_portfolio()

# Bot telemetry and portfolio reporting routes (app/portfolio_api.py).
app.include_router(portfolio_router)
from app.ledger_api import router as ledger_router
app.include_router(ledger_router)
from app.gotobi_calendar_api import router as gotobi_calendar_router
app.include_router(gotobi_calendar_router)
from app.research_api import router as research_router
app.include_router(research_router)
from app.paper_desk_api import router as paper_desk_router
app.include_router(paper_desk_router)
from app.overview_api import router as overview_router
app.include_router(overview_router)


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "false").lower() in ("true", "1", "yes")
    uvicorn.run("app.server:app", host=host, port=port, reload=reload, reload_dirs=["app"] if reload else None)
