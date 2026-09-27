"""HTTP API of the dashboard's Ledger view (app/ledger.py): per-account ledger, and deposits / withdrawals.

Handlers are plain `def`: FastAPI runs them in its threadpool, so the DB work never blocks the event loop that
serves the bots' reports.
"""
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import ledger
from app.accounts import get_account_registry
from app.dashboard import format_vn_time
from app.db import get_db_connection
from app.portfolio import get_portfolio_manager

router = APIRouter()


class MovementRequest(BaseModel):
    account_id: str
    amount: Optional[float] = None
    occurred_at: Optional[str] = None
    note: Optional[str] = None
    balance_log_id: Optional[int] = None


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "message": message})


def _accounts(scope: str):
    """Accounts in a dashboard scope: demo / live / all, or one account_id."""
    accounts = get_account_registry().list_accounts(include_unconfigured=True)
    if scope in ("demo", "live"):
        return [a for a in accounts if a["account_type"] == scope]
    if scope == "all":
        return accounts
    return [a for a in accounts if a["account_id"] == scope]


def _with_vn_times(entry: dict) -> dict:
    entry["broker_balance_at_vn"] = format_vn_time(entry["broker_balance_at"])
    for m in entry["movements"]:
        m["occurred_at_vn"] = format_vn_time(m["occurred_at"])
    for u in entry["unexplained"]:
        u["recorded_at_vn"] = format_vn_time(u["recorded_at"])
    return entry


def _conn():
    return get_db_connection(get_portfolio_manager().db_path)


@router.get("/api/ledger")
def api_ledger(account_id: str = "all"):
    conn = _conn()
    try:
        return {"accounts": [_with_vn_times(e) for e in ledger.ledgers(conn, _accounts(account_id))],
                "tolerance": ledger.TOLERANCE}
    finally:
        conn.close()


@router.post("/api/ledger/movements", status_code=201)
def api_add_movement(req: MovementRequest):
    if not _accounts(req.account_id) or req.account_id in ("demo", "live", "all"):
        return _error(404, f"Unknown account {req.account_id}")
    conn = _conn()
    try:
        movement_id = ledger.add_movement(conn, req.account_id, req.amount, req.occurred_at, req.note,
                                          req.balance_log_id)
    except ledger.LedgerError as e:
        return _error(422, str(e))
    finally:
        conn.close()
    return {"success": True, "id": movement_id}


@router.delete("/api/ledger/movements/{movement_id}")
def api_delete_movement(movement_id: int):
    conn = _conn()
    try:
        if not ledger.delete_movement(conn, movement_id):
            return _error(404, "No such movement")
    finally:
        conn.close()
    return {"success": True}
