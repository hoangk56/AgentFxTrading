"""Trade evaluation on the M1 cache: bid/ask fills, SL/TP/time exits, commission and swap, R per trade.

An order enters at the open of M1 row k (buy at ask ~ bid open + the previous minute's closing spread) and
leaves at the first of: SL, TP (SL first when both fall in one minute; a gap fills at the open), or the
close of row k_end. R = net price move per unit / |entry - SL| at entry."""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

import math
import numpy as np

from research.scan.data import comm_price, spec_for
from research.specs import swap_usd
from research.ticks import day_ms

P2_START, P3_START = day_ms(date(2026, 1, 1)), day_ms(date(2026, 6, 1))
PERIODS = ("P1", "P2", "P3")


def period_of(ms: int) -> str:
    return "P1" if ms < P2_START else ("P2" if ms < P3_START else "P3")


@dataclass
class Order:
    k: int
    side: int
    sl: float
    k_end: int
    tp: Optional[float] = None
    tag: str = ""


@dataclass
class Fill:
    symbol: str
    side: int
    t_in: int
    t_out: int
    entry: float
    exit: float
    risk: float
    r: float
    why: str
    tag: str

    @property
    def period(self) -> str:
        return period_of(self.t_in)


def _first(mask: np.ndarray) -> int:
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else -1


def simulate(m: dict, symbol: str, orders: List[Order], one_at_a_time: bool = True) -> List[Fill]:
    spec = spec_for(symbol)
    comm = comm_price(symbol)
    o, h, l, c, ca, ts = m["o"], m["h"], m["l"], m["c"], m["ca"], m["ts"]
    spr = ca - c
    out: List[Fill] = []
    busy = -1
    for od in sorted(orders, key=lambda x: x.k):
        k = od.k
        if k <= 0 or k >= len(o) or od.k_end < k or (one_at_a_time and k <= busy):
            continue
        s = od.side
        entry = o[k] + spr[k - 1] if s > 0 else o[k]
        risk = (entry - od.sl) * s
        if not risk > 0:
            continue
        w = slice(k, od.k_end + 1)
        if s > 0:
            j_sl = _first(l[w] <= od.sl)
            j_tp = _first(h[w] >= od.tp) if od.tp is not None else -1
        else:
            j_sl = _first(h[w] + spr[w] >= od.sl)
            j_tp = _first(l[w] + spr[w] <= od.tp) if od.tp is not None else -1
        cands = [(j, why) for j, why in ((j_sl, "sl"), (j_tp, "tp")) if j >= 0]
        if cands:
            j, why = min(cands, key=lambda x: (x[0], x[1] != "sl"))
            j += k
            ask_open = o[j] + spr[j]
            if why == "sl":
                px = min(od.sl, o[j]) if s > 0 else max(od.sl, ask_open)
                if j == k:
                    px = od.sl
            else:
                px = max(od.tp, o[j]) if s > 0 else min(od.tp, ask_open)
                if j == k:
                    px = od.tp
        else:
            j, why = od.k_end, "time"
            px = c[j] if s > 0 else ca[j]
        swap = swap_usd(symbol, s, 1.0, int(ts[k]), int(ts[j]) + 60_000) / spec.usd_per_quote
        net = (px - entry) * s - comm + swap
        out.append(Fill(symbol, s, int(ts[k]), int(ts[j]) + 60_000, entry, px, risk, net / risk, why, od.tag))
        busy = j
    return out


def stats(rs) -> tuple:
    n = len(rs)
    if n < 2:
        return n, (float(rs[0]) if n else 0.0), 0.0
    a = np.asarray(rs, float)
    sd = a.std(ddof=1)
    return n, float(a.mean()), float(a.mean() / (sd / math.sqrt(n))) if sd > 0 else 0.0


def table(fills: List[Fill], by_symbol: bool = True, periods=PERIODS) -> str:
    lines = []
    syms = sorted({f.symbol for f in fills})
    rows = ([("ALL", fills)] + ([(s, [f for f in fills if f.symbol == s]) for s in syms] if by_symbol else []))
    for name, fs in rows:
        cells = []
        for P in periods:
            n, mu, t = stats([f.r for f in fs if f.period == P])
            cells.append(f"{P} n{n:4d} {mu:+.3f} t{t:+5.1f}")
        lines.append(f"  {name:7s} " + " | ".join(cells))
    return "\n".join(lines)
