"""Shared helpers for the lab tests."""
from dataclasses import replace

import numpy as np
import pytest

from research.lab.feed import Chunk
from research.lab.universe import instrument
from research.ticks import DATA_DIR, Ticks

needs_ticks = pytest.mark.skipif(not (DATA_DIR / "BTCUSD" / "t1").exists(), reason="no tick cache")
needs_m1 = pytest.mark.skipif(not (DATA_DIR / "m1" / "EURUSD.npz").exists(), reason="no M1 cache")


def make_chunk(ts, bid, spread=0.0002, symbol="EURUSD", lo=None, hi=None, variant="real", year=2025, **inst_over):
    t = Ticks(np.asarray(ts, np.int64), np.asarray(bid, float), np.asarray(bid, float) + spread)
    inst = instrument(symbol)
    if inst_over:
        inst = replace(inst, **inst_over)
    return Chunk(symbol, variant, year, t, int(t.ts[0]) if lo is None else lo,
                 int(t.ts[-1]) + 1 if hi is None else hi, inst)


def bar_ticks(t0_ms, minutes, ohlc):
    """Four bid ticks per bar: open, then low/high (high first on a down bar), then the close one minute before
    the bar ends. Returns (ts, bid)."""
    ts, px = [], []
    for k, (o, h, l, c) in enumerate(ohlc):
        base = t0_ms + k * minutes * 60_000
        first, second = (l, h) if c >= o else (h, l)
        ts += [base, base + 60_000, base + 120_000, base + (minutes - 1) * 60_000]
        px += [o, first, second, c]
    return np.array(ts, np.int64), np.array(px, float)
