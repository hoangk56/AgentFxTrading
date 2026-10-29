"""HTTP API of the dashboard's Forward view (app/forward_status.py): the registered stop and promotion rules of each
research candidate, applied to its closed trades. Read-only.

The handler is a plain `def`: FastAPI runs it in its threadpool, so the DB work never blocks the event loop that
serves the bots' reports.
"""
import math

from fastapi import APIRouter

from app.forward_status import calendar_guard, forward_status
from app.portfolio import get_portfolio_manager

router = APIRouter()


def _json_safe(value):
    """NaN is not JSON: a pooled t that cannot be computed goes out as null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


@router.get("/api/forward/status")
def api_forward_status():
    return {"candidates": _json_safe(forward_status(get_portfolio_manager().db_path)),
            "gold_calendar": calendar_guard()}
