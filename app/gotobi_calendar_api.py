"""HTTP API of the dashboard's Calendar view (app/gotobi_calendar.py): one month of gotobi days, Gotobi trades and
ECB window trades.

Handlers are plain `def`: FastAPI runs them in its threadpool, so the DB work never blocks the event loop that
serves the bots' reports.
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import gotobi_calendar as gc
from app.accounts import get_account_registry
from app.dashboard import format_vn_time
from app.db import get_db_connection
from app.portfolio import get_portfolio_manager

router = APIRouter()


def _account_ids(scope: str):
    """Account ids in a dashboard scope (demo / live / one account_id), or None for 'all' (no filter)."""
    if scope == "all":
        return None
    accounts = get_account_registry().list_accounts(include_unconfigured=True)
    if scope in ("demo", "live"):
        return [a["account_id"] for a in accounts if a["account_type"] == scope]
    return [scope]


@router.get("/api/gotobi/calendar")
def api_gotobi_calendar(month: Optional[str] = None, account_id: str = "all"):
    today = gc.today_utc()
    month = month or today.strftime("%Y-%m")
    try:
        first, last = gc.month_bounds(month)
    except ValueError:
        return JSONResponse(status_code=422, content={"success": False, "message": f"Bad month '{month}', want YYYY-MM"})

    # A long is entered the evening before its day, so the month's first day starts with the day before it.
    bots = " OR ".join("bot_id LIKE ?" for _ in gc.BOT_SUFFIXES)
    sql = ("SELECT id, bot_id, account_id, symbol, side, volume, entry_time, exit_time, pnl, status FROM positions "
           f"WHERE ({bots}) AND entry_time >= ? AND entry_time < ?")
    params = ["%" + suffix for suffix in gc.BOT_SUFFIXES]
    params += [(first - timedelta(days=1)).isoformat(), (last + timedelta(days=1)).isoformat()]
    ids = _account_ids(account_id)
    if ids is not None:
        if not ids:
            ids = [""]
        sql += f" AND account_id IN ({', '.join('?' for _ in ids)})"
        params += ids

    conn = get_db_connection(get_portfolio_manager().db_path)
    try:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()
    return gc.month_calendar(month, rows, gc.skip_dates(), today, vn_time=format_vn_time)
