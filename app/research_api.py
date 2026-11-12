"""HTTP API of the dashboard's Research view (static/js/research.js): every researched algorithm from
`research/registry.yaml`, each joined to its forward tracker, plus the rounds that were tried and failed. Read-only.

The registry is written by the research sessions; this module only reads it. A missing or broken file never breaks
the page: the answer is an empty registry and a `warning` the page shows. Trackers:

- `ecb_f3`, `ecb_e1`, `gold_levels`: the registered stop and promotion rules applied to the bots' closed trades
  (app/forward_status.py), with the rule numbers of each candidate.
- `basis_b`: the paper / demo bot's `status()` from app/basis_b_status.py, imported lazily so a missing module or one
  that raises only empties that tracker.
- `a2_live`: the A2-D5L executor's `status()` from app/a2_live_status.py (its trades.csv / state.json), same way.

Each tracker also hands over its closed trades as (exit time, value) under `dated`; the payload turns them into the
algorithm's `periods` (last week / month / year against the period before, app/research_periods.py) and drops them.

The handler is a plain `def`: FastAPI runs it in its threadpool, so the DB work never blocks the event loop that serves
the bots' reports. Docs: docs/research-screen.md.
"""
from __future__ import annotations

import datetime
import importlib
import logging
import math
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import APIRouter

from app.forward_status import CANDIDATES, calendar_guard, forward_status
from app.portfolio import get_portfolio_manager
from app.research_plain import PLAIN_PATH, load_plain
from app.live_r import live_r_summary, live_r_trades
from app import research_periods

def _json_safe(value):
    """NaN is not JSON: a pooled t that cannot be computed goes out as null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


router = APIRouter()
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "research" / "registry.yaml"
TIERS = ("live", "demo", "cho-kiem", "da-loai")
RULE_TRACKERS = tuple(CANDIDATES)          # ecb_f3, ecb_e1, gold_levels
BASIS_TRACKERS = ("basis_b", "a2_live")
NO_DATA = "chưa có dữ liệu"


def _text(value) -> Optional[str]:
    if value is None:
        return None
    return str(value).strip() or None


def _clean_algorithm(raw: dict) -> dict:
    research = raw.get("research") if isinstance(raw.get("research"), dict) else {}
    return {
        "id": str(raw["id"]).strip(),
        "name": _text(raw.get("name")) or str(raw["id"]),
        "description": _text(raw.get("description")),
        "market": _text(raw.get("market")),
        "round": _text(raw.get("round")),
        "tier": (_text(raw.get("tier")) or "").lower(),
        "tier_reason": _text(raw.get("tier_reason")),
        "research": {k: _text(research.get(k)) for k in ("is", "val", "hold") if _text(research.get(k))},
        "forward": _text(raw.get("forward")),
        "bot": _text(raw.get("bot")),
        "prereg": _text(raw.get("prereg")),
        "report": _text(raw.get("report")),
    }


def _clean_tried(raw: dict) -> dict:
    return {k: _text(raw.get(k)) for k in ("round", "name", "reason", "report")}


def load_registry(path: Path = None) -> Tuple[List[dict], List[dict], List[str]]:
    """(algorithms, tried, warnings). A missing, unreadable or malformed file gives two empty lists and a warning;
    a single bad row is skipped with a warning of its own."""
    path = Path(path or REGISTRY_PATH)
    try:
        import yaml
    except ImportError:
        return [], [], ["Thiếu thư viện PyYAML trên server: không đọc được sổ nghiên cứu."]
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return [], [], [f"Chưa có sổ nghiên cứu ({_rel(path)})."]
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        logger.warning(f"[RESEARCH] cannot read {path}: {e}")
        return [], [], [f"Không đọc được sổ nghiên cứu ({_rel(path)}): {type(e).__name__}."]
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return [], [], [f"Sổ nghiên cứu ({_rel(path)}) sai dạng: cần các khoá algorithms và tried."]

    warnings: List[str] = []
    algorithms: List[dict] = []
    seen = set()
    for i, raw in enumerate(data.get("algorithms") or []):
        if not isinstance(raw, dict) or not _text(raw.get("id")):
            warnings.append(f"Bỏ qua dòng algorithms #{i + 1}: thiếu id.")
            continue
        entry = _clean_algorithm(raw)
        if entry["id"] in seen:
            warnings.append(f"Bỏ qua {entry['id']}: id trùng.")
            continue
        seen.add(entry["id"])
        if entry["tier"] not in TIERS:
            warnings.append(f"{entry['id']}: bậc \"{entry['tier']}\" không rõ, xếp vào Chờ kiểm.")
        algorithms.append(entry)
    tried = [_clean_tried(r) for r in (data.get("tried") or []) if isinstance(r, dict)]
    return algorithms, tried, warnings


def _rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _rules(key: str) -> dict:
    """The registered numbers of a rules candidate, for the page to put in words (app/forward_status.py)."""
    c = CANDIDATES[key]
    return {
        "stop_t_after": c.min_trades_stop_t if c.min_trades_stop_t < 10 ** 9 else None,
        "stop_t": c.stop_t,
        "stop_cum_after": c.stop_cum_after,
        "floor_after": c.floor_after,
        "promote_after": c.min_trades_promote,
        "promote_t": c.promote_t,
        "hold": {"n": c.hold_n, "mean_bp": c.hold_mean},
    }


def _rule_trackers(keys: List[str]) -> dict:
    if not keys:
        return {}
    try:
        rows = forward_status(get_portfolio_manager().db_path, keys)
    except Exception as e:                      # a DB failure must not take the registry down with it
        logger.warning(f"[RESEARCH] forward status failed: {e}")
        return {k: {"key": k, "kind": "rules", "available": False, "message": NO_DATA} for k in keys}
    return {r["key"]: {"key": r["key"], "kind": "rules", "available": True, "message": None,
                       "data": _json_safe(r), "rules": _rules(r["key"])} for r in rows}


def basis_b_tracker() -> dict:
    """The basis B bot's status() (app/basis_b_status.py), or an empty tracker when it is missing or fails."""
    return _module_tracker("basis_b", "app.basis_b_status")


def a2_live_tracker() -> dict:
    """The A2-D5L executor's status() (app/a2_live_status.py), or an empty tracker when it is missing or fails."""
    return _module_tracker("a2_live", "app.a2_live_status")


def _module_tracker(key: str, module: str) -> dict:
    out = {"key": key, "kind": key, "available": False, "message": NO_DATA}
    try:
        status = importlib.import_module(module).status()
    except Exception as e:
        logger.info(f"[RESEARCH] {key} status unavailable: {type(e).__name__}: {e}")
        return out
    if not isinstance(status, dict):
        return out
    return {**out, "available": bool(status.get("available")),
            "message": None if status.get("available") else NO_DATA, "data": _json_safe(status)}


def _live_r_db():
    return get_portfolio_manager().db_path


def live_r_tracker(entry: dict) -> Optional[dict]:
    """Real-money R for a live algorithm sized by risk with no forward tracker of its own (Gotobi C3), or None when the
    entry does not qualify. Its live date is the first `live` event of its plain journey."""
    plain = entry.get("plain") or {}
    if plain.get("unit") != "R" or entry["tier"] != "live" or entry["forward"] or not entry["bot"]:
        return None
    since = next((h["date"] for h in plain.get("history") or [] if h["kind"] == "live"), None)
    out = {"key": "live_r", "kind": "live_r", "available": False, "message": NO_DATA}
    try:
        trades, skipped = live_r_trades(entry["bot"], since, _live_r_db())
    except Exception as e:                      # a DB failure empties this tracker only
        logger.warning(f"[RESEARCH] live R failed for {entry['id']}: {e}")
        return out
    data = {**live_r_summary(trades, skipped), "since": since, "dated": trades}
    return {**out, "available": True, "message": None, "data": _json_safe(data)}


TRACKER_UNIT = {"rules": "bp", "basis_b": "bp", "a2_live": "bp", "live_r": "R"}


def _today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


def run_since(entry: dict) -> Optional[datetime.date]:
    """First day of the forward run: the plain journey's first `live` event for a live algorithm, its first `demo`
    event otherwise (the same date the bar chart prints under its last bar)."""
    kind = "live" if entry["tier"] == "live" else "demo"
    for h in (entry.get("plain") or {}).get("history") or []:
        if h.get("kind") == kind:
            return research_periods.to_day(h.get("date"))
    return None


def algorithm_periods(entry: dict, today: datetime.date) -> Tuple[Optional[dict], Optional[str]]:
    """(periods, note) of an algorithm from its tracker's dated trades; periods is None with a note in words when there
    is nothing to cut (no trade yet, tracker unreadable), and None with no note when there is no tracker at all."""
    tr = entry.get("tracker")
    if not tr or tr.get("kind") not in TRACKER_UNIT:
        return None, None
    if not tr.get("available") or not isinstance(tr.get("data"), dict):
        return None, "Chưa đọc được lệnh của bộ theo dõi."
    try:
        trades = research_periods.dated(tr["data"].get("dated") or [])
        if not trades:
            return None, "Chưa có lệnh nào đóng."
        since = run_since(entry) or min(d for d, _ in trades)
        return research_periods.periods(trades, today, since, TRACKER_UNIT[tr["kind"]]), None
    except Exception as e:                      # one bad tracker never takes the page down
        logger.warning(f"[RESEARCH] periods failed for {entry['id']}: {e}")
        return None, f"Không tính được số theo kỳ: {type(e).__name__}."


def research_payload(path: Path = None, plain_path: Path = None) -> dict:
    algorithms, tried, warnings = load_registry(path)
    plain, plain_warnings = load_plain(plain_path or PLAIN_PATH, known_ids=[a["id"] for a in algorithms])
    warnings = warnings + plain_warnings
    for a in algorithms:
        a["plain"] = plain.get(a["id"])
    wanted = {a["forward"] for a in algorithms if a["forward"]}
    trackers = _rule_trackers([k for k in RULE_TRACKERS if k in wanted])
    if "basis_b" in wanted:
        trackers["basis_b"] = basis_b_tracker()
    if "a2_live" in wanted:
        trackers["a2_live"] = a2_live_tracker()
    for a in algorithms:
        key = a["forward"]
        if key and key not in trackers:
            trackers[key] = {"key": key, "kind": "unknown", "available": False,
                             "message": f"Không có bộ theo dõi tên \"{key}\"."}
        a["tracker"] = trackers.get(key) if key else live_r_tracker(a)
    today = _today()
    for a in algorithms:
        a["periods"], a["periods_note"] = algorithm_periods(a, today)
    for a in algorithms:                        # the raw trades stay on the server
        if a["tracker"] and isinstance(a["tracker"].get("data"), dict):
            a["tracker"]["data"].pop("dated", None)
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "registry": _rel(Path(path or REGISTRY_PATH)),
        "warning": " ".join(warnings) or None,
        "algorithms": algorithms,
        "tried": tried,
        "gold_calendar": calendar_guard() if "gold_levels" in wanted else None,
    }


@router.get("/api/research")
def api_research():
    return research_payload()
