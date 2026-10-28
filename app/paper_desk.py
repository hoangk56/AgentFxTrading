"""Paper desk: a log of LLM-agent calls that cannot be edited after the fact, and the scoring that judges them.

The experiment (docs/paper-desk.md) asks whether agents "analysing the day" beat a naive rule after costs. It touches
no money and no bot. A call is one analyst's view for one symbol and one day: direction (-1, 0, +1), confidence, a
short rationale, and the features the analyst was shown. It is written before the entry time of its day and is insert
only: there is no update or delete in this module, and a second call for the same (day, symbol, analyst) is refused.

Scoring takes the realised prices from the caller (entry, exit, and the previous day's entry for the momentum
baseline), so this module needs no data feed. Net bp = direction x move in bp, minus the round-trip cost in bp the
caller passes per symbol.
"""
from __future__ import annotations

import datetime
import json
import math
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from app.db import get_db_connection

SYMBOLS = ("EURUSD", "USDJPY", "GBPJPY", "XAUUSD", "US500", "BTCUSD")
ENTRY_HOUR_UTC = 7
MIN_CALLS_FOR_VERDICT = 600
PASS_T = 2.5


class CallRefused(Exception):
    pass


def init_schema(db_target=None) -> None:
    conn = get_db_connection(db_target)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                analyst TEXT NOT NULL,
                direction INTEGER NOT NULL,
                confidence REAL,
                rationale TEXT,
                features_json TEXT,
                model TEXT,
                created_at TEXT NOT NULL,
                UNIQUE (call_date, symbol, analyst)
            )""")
        conn.commit()
    finally:
        conn.close()


def entry_time(call_date: str) -> datetime.datetime:
    d = datetime.date.fromisoformat(call_date)
    return datetime.datetime(d.year, d.month, d.day, ENTRY_HOUR_UTC, tzinfo=datetime.timezone.utc)


def record_call(call_date: str, symbol: str, analyst: str, direction: int, confidence: Optional[float] = None,
                rationale: str = "", features: Optional[dict] = None, model: str = "",
                now: Optional[datetime.datetime] = None, db_target=None) -> None:
    """Insert one call. Refused after the day's entry time, for an unknown symbol, a bad direction, or a repeat."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if symbol not in SYMBOLS:
        raise CallRefused(f"unknown symbol {symbol}")
    if direction not in (-1, 0, 1):
        raise CallRefused(f"direction must be -1, 0 or 1, got {direction}")
    if now >= entry_time(call_date):
        raise CallRefused(f"{call_date} {symbol} {analyst}: recorded at {now.isoformat()}, after the "
                          f"{ENTRY_HOUR_UTC:02d}:00 UTC entry")
    conn = get_db_connection(db_target)
    try:
        try:
            conn.execute(
                "INSERT INTO paper_calls (call_date, symbol, analyst, direction, confidence, rationale, features_json,"
                " model, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (call_date, symbol, analyst, direction, confidence, rationale,
                 json.dumps(features, sort_keys=True) if features is not None else None, model, now.isoformat()))
            conn.commit()
        except Exception as e:
            if "UNIQUE" in str(e).upper() or "unique" in str(e):
                raise CallRefused(f"{call_date} {symbol} {analyst} already recorded") from None
            raise
    finally:
        conn.close()


def load_calls(db_target=None) -> List[dict]:
    conn = get_db_connection(db_target)
    try:
        return [dict(r) for r in conn.execute(
            "SELECT call_date, symbol, analyst, direction, confidence FROM paper_calls ORDER BY call_date, id"
        ).fetchall()]
    finally:
        conn.close()


def recorded_symbols(call_date: str, db_target=None) -> set:
    """Symbols that already have at least one call for the day, so a rerun does not ask (and pay for) them again."""
    conn = get_db_connection(db_target)
    try:
        return {r["symbol"] for r in conn.execute(
            "SELECT DISTINCT symbol FROM paper_calls WHERE call_date = ?", (call_date,)).fetchall()}
    finally:
        conn.close()


def clustered_t(values: Sequence[float], groups: Sequence[str]) -> float:
    """t of the mean with standard errors clustered by group (the calls of one day move together)."""
    n = len(values)
    if n < 3:
        return float("nan")
    m = sum(values) / n
    sums: Dict[str, float] = {}
    for v, g in zip(values, groups):
        sums[g] = sums.get(g, 0.0) + (v - m)
    G = len(sums)
    if G < 2:
        return float("nan")
    se = math.sqrt(sum(s * s for s in sums.values()) * G / (G - 1)) / n
    return m / se if se > 0 else float("nan")


# prices: (call_date, symbol) -> (prev_entry, entry, exit)
Prices = Mapping[Tuple[str, str], Tuple[float, float, float]]


def net_bp(direction: int, entry: float, exit_: float, cost_bp: float) -> float:
    return direction * (exit_ / entry - 1.0) * 1e4 - (cost_bp if direction else 0.0)


def _summary(rows: List[Tuple[str, float, int]]) -> dict:
    """rows: (day, net_bp, direction). Calls with direction 0 are no trade and not counted."""
    traded = [r for r in rows if r[2] != 0]
    n = len(traded)
    if not n:
        return {"n": 0, "mean": None, "hit": None, "t": float("nan")}
    nets = [r[1] for r in traded]
    return {"n": n, "mean": sum(nets) / n, "hit": sum(1 for x in nets if x > 0) / n,
            "t": clustered_t(nets, [r[0] for r in traded])}


def score(calls: Iterable[dict], prices: Prices, cost_bp: Mapping[str, float]) -> dict:
    """Per analyst, plus the always-long and previous-day-momentum baselines on the same (day, symbol) cells.
    Calls without prices yet (the exit has not happened) are skipped."""
    by_analyst: Dict[str, List[Tuple[str, float, int]]] = {}
    long_rows: List[Tuple[str, float, int]] = []
    mom_rows: List[Tuple[str, float, int]] = []
    seen = set()
    for c in calls:
        key = (c["call_date"], c["symbol"])
        p = prices.get(key)
        if p is None:
            continue
        prev, entry, exit_ = p
        cost = cost_bp[c["symbol"]]
        by_analyst.setdefault(c["analyst"], []).append(
            (c["call_date"], net_bp(c["direction"], entry, exit_, cost), c["direction"]))
        if key not in seen:
            seen.add(key)
            long_rows.append((key[0], net_bp(1, entry, exit_, cost), 1))
            mom = 1 if entry > prev else -1 if entry < prev else 0
            mom_rows.append((key[0], net_bp(mom, entry, exit_, cost), mom))
    out = {"analysts": {a: _summary(r) for a, r in by_analyst.items()},
           "baselines": {"always_long": _summary(long_rows), "prev_day_momentum": _summary(mom_rows)}}
    for name, s in list(out["analysts"].items()) + [("always_long", out["baselines"]["always_long"]),
                                                    ("prev_day_momentum", out["baselines"]["prev_day_momentum"])]:
        base_means = [b["mean"] for b in out["baselines"].values() if b["mean"] is not None]
        s["beats_baselines"] = (s["mean"] is not None and bool(base_means) and s["mean"] > max(base_means)
                                if name not in out["baselines"] else None)
        s["verdict"] = verdict(s, name in out["baselines"])
    return out


def verdict(s: dict, is_baseline: bool) -> str:
    """PASS needs the registered number of traded calls, net t >= 2.5 and a mean above both baselines."""
    if is_baseline:
        return "BASELINE"
    if s["n"] < MIN_CALLS_FOR_VERDICT:
        return "TOO_FEW"
    if s["t"] >= PASS_T and s["beats_baselines"]:
        return "PASS"
    return "FAIL"
