"""Logging for the agent server: GMT+7 timestamps, one log file per GMT+7 day, test-run isolation.

Split out of app/server.py, which still calls setup_agent_logging() at import time and re-exports
every name here.
"""
import datetime
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_LOG_FORMAT = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s"

class GMT7Formatter(logging.Formatter):
    """Formatter that outputs timestamps in GMT+7 (Asia/Bangkok / Asia/Ho_Chi_Minh)."""
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone(datetime.timedelta(hours=7))).timetuple()

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = datetime.datetime(*ct[:6]).strftime(datefmt)
        else:
            s = datetime.datetime(*ct[:6]).strftime("%Y-%m-%d %H:%M:%S")
        return s
class DailyDateFileHandler(logging.Handler):
    """
    Daily log file handler that writes directly to logs/agent_YYYY-MM-DD.log based on GMT+7 date.
    Rolls over cleanly at 00:00 GMT+7 without filename mangling.
    """
    def __init__(self, logs_dir: Path, backup_count: int = 14, encoding: str = "utf-8"):
        super().__init__()
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.backup_count = backup_count
        self.encoding = encoding
        self._current_date = None
        self._file = None
        self._lock = threading.Lock()

    def _get_current_date(self) -> str:
        now_gmt7 = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)
        return now_gmt7.strftime("%Y-%m-%d")

    def _cleanup_old_logs(self):
        try:
            log_files = sorted(self.logs_dir.glob("agent_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            for f in log_files[self.backup_count:]:
                f.unlink(missing_ok=True)
        except Exception:
            pass

    def emit(self, record):
        try:
            msg = self.format(record)
            date_str = self._get_current_date()
            with self._lock:
                if self._file is None or self._current_date != date_str:
                    if self._file is not None:
                        try:
                            self._file.close()
                        except Exception:
                            pass
                    self._current_date = date_str
                    log_path = self.logs_dir / f"agent_{date_str}.log"
                    self._file = open(log_path, "a", encoding=self.encoding)
                    self._cleanup_old_logs()
                self._file.write(msg + "\n")
                self._file.flush()
        except Exception:
            self.handleError(record)

    def close(self):
        with self._lock:
            if self._file is not None:
                try:
                    self._file.close()
                except Exception:
                    pass
                self._file = None
        super().close()

def is_running_under_test() -> bool:
    return (
        "pytest" in sys.modules
        or "PYTEST_CURRENT_TEST" in os.environ
        or any("pytest" in str(arg).lower() for arg in sys.argv)
        or os.environ.get("ENV") == "test"
        or os.environ.get("TESTING") == "1"
    )

def setup_agent_logging(level=logging.INFO, log_filename: Optional[str] = None):
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    under_test = is_running_under_test()
    if under_test or log_filename:
        # Isolate pytest / test runner logs to logs/test.log instead of polluting live daily logs
        target_log = logs_dir / (log_filename or "test.log")
        file_handler = logging.FileHandler(target_log, mode="a", encoding="utf-8")
    else:
        # Daily rotating file handler (14 days backup, GMT+7 date-aligned) for production live trading
        file_handler = DailyDateFileHandler(logs_dir, backup_count=14, encoding="utf-8")

    file_handler.setFormatter(GMT7Formatter(_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    file_handler.setLevel(level)
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(GMT7Formatter(_LOG_FORMAT, datefmt="%H:%M:%S"))
    console_handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    return file_handler, console_handler


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
