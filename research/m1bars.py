"""Bars of any timeframe from the M1 cache, with the spread and the round-trip commission in price units."""
from dataclasses import dataclass

import numpy as np

from research.m1 import load
from research.specs_ext import EXT_SPECS
from research.specs import SPECS

MIN = 60_000


def spec_for(symbol: str):
    return SPECS.get(symbol) or EXT_SPECS[symbol]


@dataclass
class TF:
    t: np.ndarray      # bar open, ms UTC
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray      # bid close
    ca: np.ndarray     # ask at the close tick
    first: np.ndarray  # index of the bar's first M1 row
    last: np.ndarray   # index of the bar's last M1 row

    def __len__(self):
        return len(self.t)


def resample(m: dict, minutes: int, offset_min: int = 0) -> TF:
    """UTC-aligned buckets of `minutes` (offset shifts the bucket edges, e.g. D1 at 22:00 UTC = offset 120)."""
    span = minutes * MIN
    b = (m["ts"] + offset_min * MIN) // span
    s = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    e = np.r_[s[1:], len(b)] - 1
    return TF(b[s] * span - offset_min * MIN, m["o"][s], np.maximum.reduceat(m["h"], s),
              np.minimum.reduceat(m["l"], s), m["c"][e], m["ca"][e], s, e)


def comm_price(symbol: str) -> float:
    """Round-trip commission per unit, expressed in quote price units."""
    sp = spec_for(symbol)
    return sp.comm_per_unit / sp.usd_per_quote


def atr(b: TF, n: int = 14) -> np.ndarray:
    prev = np.r_[b.c[0], b.c[:-1]]
    tr = np.maximum(b.h - b.l, np.maximum(np.abs(b.h - prev), np.abs(b.l - prev)))
    out = np.full(len(tr), np.nan)
    cs = np.cumsum(np.r_[0.0, tr])
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out
