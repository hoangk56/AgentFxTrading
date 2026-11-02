"""Stream P helpers: USDCNH IC ticks around 01:15 UTC, one day at a time, HOLD guard."""
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path("/Users/hoangbk/00.code_base/105.AgentFxTrading")
sys.path.insert(0, str(ROOT))
from research.ticks import decode_day, _ffill  # noqa: E402

T1 = ROOT / "research/data/USDCNH/t1"
FIX_CSV = ROOT / "research/data/cny_fix/usdcny_fix.csv"
HOLD = date(2025, 1, 1)
OUT = ROOT / "research/results/portfolio/round67_fix_seconds/P/out"
CACHE = ROOT / "research/data/cny_fix/cache"  # large arrays live here, not in results/


def day_ms(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


def load_window(d: date, t0_s: int, t1_s: int):
    """Ticks of UTC day d with t0_s <= seconds-of-day < t1_s: (ts ms, bid, ask). Side ffill uses the whole day."""
    assert d < HOLD, "HOLD guard"
    p = T1 / f"{d:%Y%m%d}.zticks"
    if not p.exists():
        return None
    rows = decode_day(p)
    if rows.size == 0:
        return None
    bid, ask = _ffill(rows[:, 1]), _ffill(rows[:, 2])
    ts = rows[:, 0]
    keep = (bid != 0) & (ask != 0)
    ts, bid, ask = ts[keep], bid[keep] / 1e5, ask[keep] / 1e5
    assert ts.size == 0 or ts.max() < day_ms(HOLD)
    base = day_ms(d)
    m = (ts >= base + t0_s * 1000) & (ts < base + t1_s * 1000)
    # keep the last tick before the window too, as the quote in force at t0
    i0 = np.searchsorted(ts, base + t0_s * 1000) - 1
    idx = np.flatnonzero(m)
    if i0 >= 0:
        idx = np.concatenate([[i0], idx])
    return ts[idx] - base, bid[idx], ask[idx]


def load_fix():
    import csv
    out = {}
    with FIX_CSV.open() as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["date"])
            if d < HOLD:
                out[d] = float(r["fix"])
    return out


def quote_before(ts, bid, ask, t_ms):
    """Last quote with ts < t_ms."""
    i = np.searchsorted(ts, t_ms) - 1
    if i < 0:
        return None
    return int(ts[i]), bid[i], ask[i]


def quote_at_or_after(ts, bid, ask, t_ms):
    """First tick with ts >= t_ms (a market order sent at t_ms fills at the next quote update)."""
    i = np.searchsorted(ts, t_ms)
    if i >= ts.size:
        return None
    return int(ts[i]), bid[i], ask[i]
