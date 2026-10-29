"""HTTP API of the dashboard's Paper desk view (app/paper_desk_status.py). Read-only; a plain `def` so FastAPI runs the
DB work in its threadpool."""
import math

from fastapi import APIRouter

from app import paper_desk_status
from app.portfolio import get_portfolio_manager

router = APIRouter()


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


@router.get("/api/paper-desk/status")
def api_paper_desk_status():
    db = get_portfolio_manager().db_path
    return _json_safe(paper_desk_status.status(db))
