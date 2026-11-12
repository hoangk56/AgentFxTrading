"""The "Theo kỳ" block of the research screen: last week / month / year of an algorithm's forward trades against the
period right before it (docs/research-screen.md, "Periods"; mirrors 106.dnse-stock's watch periods).

Pure functions: the trackers hand over their closed trades as (exit day, value) pairs in their own unit, and these
cut them into calendar-day windows. Only forward trades exist here (no job replays a locked rule over history), so a
day before the run started is "not run yet", never an in-sample number.
"""
from __future__ import annotations

import calendar
import datetime as dt
import math
import statistics
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Dated = Tuple[dt.date, float]
PERIODS = ("week", "month", "year")


def minus_months(day: dt.date, months: int) -> dt.date:
    """Calendar month subtraction; a day the target month lacks becomes that month's last day (31/03 - 1 = 28/02)."""
    y, m = divmod(day.year * 12 + day.month - 1 - months, 12)
    return dt.date(y, m + 1, min(day.day, calendar.monthrange(y, m + 1)[1]))


def _start(kind: str, end: dt.date) -> dt.date:
    if kind == "week":
        return end - dt.timedelta(days=6)
    return minus_months(end, 1 if kind == "month" else 12) + dt.timedelta(days=1)


def windows(end: dt.date) -> Dict[str, Tuple[Tuple[dt.date, dt.date], Tuple[dt.date, dt.date]]]:
    """{kind: ((from, to), (prev_from, prev_to))}, both ends included. The previous window ends the day before the
    current one starts and spans the same rule (7 days, 1 month, 12 months) back from there."""
    out = {}
    for kind in PERIODS:
        start = _start(kind, end)
        prev_end = start - dt.timedelta(days=1)
        out[kind] = ((start, end), (_start(kind, prev_end), prev_end))
    return out


def _t(values: Sequence[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    sd = statistics.stdev(values)
    return round(statistics.fmean(values) / (sd / math.sqrt(len(values))), 2) if sd > 0 else None


def cell(trades: Iterable[Dated], start: dt.date, end: dt.date, since: Optional[dt.date]) -> dict:
    """One window: `days` calendar days, `covered` of them on or after the run's first day (`since`), and the trades
    that closed inside it. Numbers are null without a trade; t needs two."""
    values = [v for d, v in trades if start <= d <= end]
    days = (end - start).days + 1
    first = max(start, since) if since else start
    covered = max(0, (end - first).days + 1)
    n = len(values)
    return {"from": start.isoformat(), "to": end.isoformat(), "days": days, "covered": covered, "n": n,
            "mean": round(statistics.fmean(values), 4) if n else None, "t": _t(values),
            "total": round(sum(values), 4) if n else None}


def periods(trades: Sequence[Dated], end: dt.date, since: Optional[dt.date], unit: str) -> dict:
    """{unit, end, since, week|month|year: {current, previous}} over the trades, oldest or newest first."""
    trades = list(trades)
    out = {"unit": unit, "end": end.isoformat(), "since": since.isoformat() if since else None}
    for kind, (cur, prev) in windows(end).items():
        out[kind] = {"current": cell(trades, *cur, since), "previous": cell(trades, *prev, since)}
    return out


def to_day(value) -> Optional[dt.date]:
    """A date from a date, an ISO date / datetime string ("2026-11-03 07:00:00", "...Z", "...+00:00") or None."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def dated(pairs: Iterable[Tuple[object, Optional[float]]]) -> List[Dated]:
    """(day, value) pairs with a readable day and a finite value; the rest are dropped."""
    out = []
    for when, value in pairs:
        day = to_day(when)
        if day is None or value is None:
            continue
        try:
            v = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(v):
            out.append((day, v))
    return out
