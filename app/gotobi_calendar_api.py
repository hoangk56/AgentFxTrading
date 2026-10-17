"""HTTP API of the dashboard's Calendar view (app/gotobi_calendar.py): one month of gotobi days, Gotobi trades and
ECB window trades.

Handlers are plain `def`: FastAPI runs them in its threadpool, so the DB work never blocks the event loop that
serves the bots' reports.
"""
from datetime import date, timedelta
from typing import Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import gotobi_calendar as gc
from app.accounts import get_account_registry
from app.cbot_presets import installed_cells
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


def _ecb_bots(ids) -> Dict[str, date]:
    """ECB rule -> the day its first bot config in the scope was created, for the installed EcbWindowBot cells (the
    dashboard's account ids are matched to the cTrader accounts by number and type)."""
    registry = get_account_registry()
    configs = {c["name"]: c for c in get_portfolio_manager().get_cbot_configs()}
    ctrader = registry.list_ctrader_accounts()
    by_id = {a["id"]: a for a in ctrader}
    out: Dict[str, date] = {}
    for cell in installed_cells(ctrader, set(configs)):
        rule = gc.ECB_RULE_BY_STRATEGY.get(cell["strategy"])
        if rule is None:
            continue
        acc = by_id[cell["account_id"]]
        if ids is not None and registry.resolve_account_id(acc["account_number"], acc["account_type"]) not in ids:
            continue
        try:
            since = date.fromisoformat(str(configs[cell["name"]].get("created_at") or "")[:10])
        except ValueError:
            since = gc.today_utc()
        out[rule] = min(out.get(rule, since), since)
    return out


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
    return gc.month_calendar(month, rows, gc.skip_dates(), today, vn_time=format_vn_time, ecb_bots=_ecb_bots(ids))
