import os
import logging
import shutil
import tempfile
from pathlib import Path
import pytest

# Ensure TESTING environment variable is set
os.environ["TESTING"] = "1"

# Never let a pytest run write into the production database: app.db redirects the default
# DB target (None / portfolio.db) to this throwaway SQLite file when AGENTFX_TEST_DB is set.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="agentfx-tests-")
os.environ["AGENTFX_TEST_DB"] = str(Path(_TEST_DB_DIR) / "test_portfolio.db")

# The repo root (for `app` and `tests._paths`) is on sys.path via `pythonpath = .` in the root
# pytest.ini. This conftest applies to every directory under tests/.

@pytest.fixture(scope="session", autouse=True)
def isolate_test_logging():
    """
    Redirect all logging during pytest runs to logs/test.log
    so that daily live trading agent logs (logs/agent_YYYY-MM-DD.log)
    remain completely clean and free of test traffic.
    """
    from app.server import setup_agent_logging
    setup_agent_logging(level=logging.INFO, log_filename="test.log")
    yield


@pytest.fixture(scope="session", autouse=True)
def isolate_test_database():
    """Drop the throwaway test database once the pytest session ends."""
    yield
    shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def dashboard_login_off(monkeypatch):
    """app.server loads .env with override=True, and the VPS .env sets the dashboard login: turn it off, so the
    tests call the API as before. tests/app/test_auth.py turns it back on."""
    monkeypatch.delenv("DASHBOARD_USERNAME", raising=False)
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
