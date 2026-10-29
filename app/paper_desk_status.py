"""Health and results of the paper desk (docs/paper-desk.md) for the dashboard and the Telegram alert.

Coverage is read straight from `paper_calls`: calls per analyst, how many took a side (direction != 0, the only calls
the verdict counts), how many failed, and which weekdays have no calls at all. Scoring needs the Dukascopy exit prices,
which the web process does not fetch: `python -m app.paper_desk_runner score` writes its result to `score.json`
beside the price cache and this module only reads that file, with its time stamp.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from app import paper_desk
from app.db import get_db_connection

RECENT_DAYS = 14
ALERT_AFTER_HOUR_UTC = 5          # the cron runs 03:00-03:40 UTC; by 05:00 a weekday without calls is a miss
ALERT_ERROR_SHARE = 0.25          # ops threshold, not a research one: a quarter of a day's calls failed
CHECK_INTERVAL_SECONDS = 3600


def data_dir() -> Path:
    return Path(os.environ.get("PAPER_DESK_DATA", "data/paper_desk"))


def score_path() -> Path:
    return data_dir() / "score.json"


def save_score(result: dict, now: Optional[dt.datetime] = None) -> None:
    now = now or dt.datetime.now(dt.timezone.utc)
    score_path().parent.mkdir(parents=True, exist_ok=True)
    score_path().write_text(json.dumps({"scored_at": now.isoformat(timespec="seconds"), **result}))


def load_score() -> Optional[dict]:
    try:
        return json.loads(score_path().read_text())
    except (OSError, ValueError):
        return None


def _is_error(rationale: Optional[str]) -> bool:
    return (rationale or "").startswith("ERROR:")


def weekdays(first: dt.date, last: dt.date) -> List[dt.date]:
    out, d = [], first
    while d <= last:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def coverage(db_target=None, now: Optional[dt.datetime] = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    paper_desk.init_schema(db_target)
    conn = get_db_connection(db_target)
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT call_date, symbol, analyst, direction, rationale FROM paper_calls ORDER BY call_date").fetchall()]
    finally:
        conn.close()
    analysts: Dict[str, dict] = {}
    days: Dict[str, dict] = {}
    for r in rows:
        a = analysts.setdefault(r["analyst"], {"analyst": r["analyst"], "calls": 0, "traded": 0, "errors": 0,
                                               "long": 0, "short": 0})
        d = days.setdefault(r["call_date"], {"date": r["call_date"], "calls": 0, "traded": 0, "errors": 0,
                                             "symbols": set()})
        err = _is_error(r["rationale"])
        for t in (a, d):
            t["calls"] += 1
            t["errors"] += err
        d["symbols"].add(r["symbol"])
        if r["direction"] != 0:
            a["traded"] += 1
            d["traded"] += 1
            a["long" if r["direction"] > 0 else "short"] += 1
    for a in analysts.values():
        a["directional_rate"] = a["traded"] / a["calls"] if a["calls"] else None
    today = now.date()
    last_due = today if now.hour >= ALERT_AFTER_HOUR_UTC else today - dt.timedelta(days=1)
    missing: List[str] = []
    if days:
        first = dt.date.fromisoformat(min(days))
        missing = [d.isoformat() for d in weekdays(first, last_due) if d.isoformat() not in days]
    recent = [dict(d, symbols=len(d["symbols"])) for d in sorted(days.values(), key=lambda x: x["date"])][-RECENT_DAYS:]
    return {"analysts": sorted(analysts.values(), key=lambda a: a["analyst"]), "recent_days": recent,
            "days_with_calls": len(days), "days_missing": missing, "symbols": list(paper_desk.SYMBOLS),
            "min_traded_for_verdict": paper_desk.MIN_CALLS_FOR_VERDICT}


def status(db_target=None, now: Optional[dt.datetime] = None) -> dict:
    return {"coverage": coverage(db_target, now), "score": load_score()}


class PaperDeskAlerts:
    """Tells Telegram once per day and problem: a weekday after 05:00 UTC with no calls, or a day where a quarter or
    more of the calls failed. Off until TELEGRAM_* are set (the notifier decides); the notifier de-duplicates by key."""

    def __init__(self, notify):
        self._notify = notify

    def check(self, db_target=None, now: Optional[dt.datetime] = None) -> List[str]:
        now = now or dt.datetime.now(dt.timezone.utc)
        sent: List[str] = []
        cov = coverage(db_target, now)
        today = now.date().isoformat()
        if cov["days_with_calls"] and today in cov["days_missing"]:
            sent.append(f"🟠 Dự đoán AI: chưa có lượt dự đoán nào cho {today} (cron 03:00-03:40 UTC). Xem logs/paper_desk.log.")
            self._notify(sent[-1], key=("paper_desk", today, "missing"))
        for d in cov["recent_days"][-2:]:
            if d["calls"] and d["errors"] / d["calls"] >= ALERT_ERROR_SHARE:
                sent.append(f"🟠 Dự đoán AI {d['date']}: {d['errors']}/{d['calls']} lượt dự đoán bị lỗi (dòng ERROR).")
                self._notify(sent[-1], key=("paper_desk", d["date"], "errors"))
        return sent

    async def run_loop(self, interval: float = CHECK_INTERVAL_SECONDS):
        import asyncio
        import logging
        from app.portfolio import get_portfolio_manager
        while True:
            try:
                await asyncio.to_thread(lambda: self.check(get_portfolio_manager().db_path))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logging.getLogger(__name__).warning(f"[PAPER_DESK] alert check failed: {e}")
            await asyncio.sleep(interval)
