"""Money in the lab: quote -> USD at the market's rate of the day, commission and swaps for fixed units.

The FlowRSI simulator used cTrader's 2026 USD-per-quote constants; over 2023-2026 USDJPY moved 130 -> 160, so
the lab converts each deal at the previous UTC day's close of the conversion pair (M1 cache). Swaps keep the
rates fitted on 2026 (research/specs.py), so earlier years' swaps are approximate and reported separately."""
from functools import lru_cache
from typing import Tuple

import numpy as np

from research.lab.universe import CONVERSION, Instrument
from research.scan.m1 import load
from research.specs import rollovers

DAY_MS = 86_400_000


@lru_cache(maxsize=None)
def daily_closes(pair: str) -> Tuple[np.ndarray, np.ndarray]:
    """(UTC day number, mid of the day's last M1 bar)."""
    m = load(pair)
    day = m["ts"] // DAY_MS
    last = np.r_[np.flatnonzero(day[1:] != day[:-1]), len(day) - 1]
    return day[last], (m["c"][last] + m["ca"][last]) / 2.0


def usd_per_quote(ccy: str, ts_ms: int) -> float:
    """USD value of one unit of the quote currency at ts_ms (previous day's close; the first close before the
    cache starts)."""
    if ccy == "USD":
        return 1.0
    pair, direct = CONVERSION[ccy]
    days, px = daily_closes(pair)
    k = max(int(np.searchsorted(days, ts_ms // DAY_MS, side="left")) - 1, 0)
    return float(px[k]) if direct else 1.0 / float(px[k])


def commission(inst: Instrument, units: float) -> float:
    return inst.comm_per_unit * units


def swap(inst: Instrument, side: int, units: float, t_in: int, t_out: int) -> float:
    rate = inst.swap_long if side > 0 else inst.swap_short
    return rate * units * rollovers(t_in, t_out, inst.triple_weekday)
