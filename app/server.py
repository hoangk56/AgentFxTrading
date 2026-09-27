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

from contextlib import asynccontextmanager

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

app = FastAPI(title="AgentFx Server", lifespan=lifespan)

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


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "false").lower() in ("true", "1", "yes")
    uvicorn.run("app.server:app", host=host, port=port, reload=reload, reload_dirs=["app"] if reload else None)
