"""research/plain.yaml: the research screen's plain-language layer (docs/research-screen.md).

Keyed by the registry's algorithm id, it carries a plain name, what / why sentences, each research period's numbers
and the dated journey. It sits beside research/registry.yaml instead of inside it so the research sessions' registry
keeps its own shape; an algorithm without an entry keeps the registry's text on screen. Read-only and forgiving like
the registry loader: a missing file is simply no plain data, a broken one or a bad field becomes a warning, never an
exception.
"""
import datetime
import logging
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)

PLAIN_PATH = Path(__file__).resolve().parent.parent / "research" / "plain.yaml"
UNITS = ("R", "bp", "pct_week", "pct_year")
KINDS = ("find", "demo", "live", "change", "wait", "out")
PERIODS = ("is", "val", "hold")


def _text(value) -> Optional[str]:
    if value is None:
        return None
    return str(value).strip() or None


def _number(value) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None                               # .nan / .inf would also break the JSON response
    return float(value)


def _count(value) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _date(value) -> Optional[str]:
    if isinstance(value, datetime.date):
        return value.isoformat()[:10]
    try:
        return datetime.date.fromisoformat(str(value).strip()).isoformat()
    except ValueError:
        return None


def _period(key: str, raw, warn) -> dict:
    raw = raw if isinstance(raw, dict) else {}
    out = {"years": _text(raw.get("years")), "n": _count(raw.get("n")), "mean": _number(raw.get("mean")),
           "t": _number(raw.get("t"))}
    for field in ("n", "mean", "t"):
        if raw.get(field) is not None and out[field] is None:
            warn(f"kỳ {key}: {field} \"{raw.get(field)}\" không phải số hợp lệ")
    return out


def _clean(entry: dict, warn) -> dict:
    unit = _text(entry.get("unit"))
    if unit is not None and unit not in UNITS:
        warn(f"đơn vị \"{unit}\" không rõ")
        unit = None
    periods = {}
    raw_periods = entry.get("periods") if isinstance(entry.get("periods"), dict) else {}
    for key, raw in raw_periods.items():
        if key not in PERIODS:
            warn(f"kỳ \"{key}\" không rõ")
            continue
        periods[key] = _period(key, raw, warn)
    history = []
    raw_history = entry.get("history")
    if raw_history is not None and not isinstance(raw_history, list):
        warn("history phải là danh sách")
        raw_history = []
    for raw in raw_history or []:
        if not isinstance(raw, dict):
            warn("một mốc hành trình sai dạng")
            continue
        date, kind = _date(raw.get("date")), _text(raw.get("kind"))
        if date is None:
            warn(f"mốc ngày \"{raw.get('date')}\" không đọc được")
            continue
        if kind not in KINDS:
            warn(f"loại mốc \"{kind}\" không rõ")
            continue
        history.append({"date": date, "kind": kind, "text": _text(raw.get("text"))})
    history.sort(key=lambda h: h["date"])          # stable: same-day events keep the file's order
    return {"name": _text(entry.get("name")), "what": _text(entry.get("what")), "why": _text(entry.get("why")),
            "unit": unit, "periods": periods, "history": history, "note": _text(entry.get("note"))}


def load_plain(path: Path = None, known_ids: Iterable[str] = ()) -> Tuple[Dict[str, dict], List[str]]:
    """({id: cleaned entry}, warnings). With `known_ids`, an id the registry does not have is dropped with a warning."""
    path = Path(path or PLAIN_PATH)
    known = set(known_ids)
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return {}, []
    except Exception as e:                        # ImportError, OSError, UnicodeDecodeError, YAMLError
        logger.warning(f"[RESEARCH] cannot read {path}: {e}")
        return {}, [f"Không đọc được bản dễ hiểu ({path.name}): {type(e).__name__}."]
    if data is None:
        return {}, []
    if not isinstance(data, dict):
        return {}, [f"Bản dễ hiểu ({path.name}) sai dạng: cần các khoá là id thuật toán."]
    plain: Dict[str, dict] = {}
    warnings: List[str] = []
    for key, entry in data.items():
        algo_id = str(key).strip()
        if known and algo_id not in known:
            warnings.append(f"Bản dễ hiểu: {algo_id} không có trong sổ nghiên cứu.")
            continue
        if not isinstance(entry, dict):
            warnings.append(f"Bản dễ hiểu: {algo_id} sai dạng.")
            continue
        try:
            plain[algo_id] = _clean(entry, lambda msg, i=algo_id: warnings.append(f"Bản dễ hiểu {i}: {msg}."))
        except Exception as e:                    # a shape no rule above foresaw: skip the entry, keep the page
            warnings.append(f"Bản dễ hiểu: bỏ qua {algo_id} ({type(e).__name__}).")
    return plain, warnings
