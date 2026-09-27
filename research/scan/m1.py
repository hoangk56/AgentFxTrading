"""Compact M1 cache from the tick cache: bid OHLC, ask at the bar's last tick, tick count, per symbol.

research/data/m1/<SYMBOL>.npz holds int64 minute start (ms UTC) and float64 o/h/l/c (bid), ca (ask close)
and spread stats; bars built this way aggregate exactly to the bid M15 bars the simulator uses."""
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from research.ticks import DATA_DIR, load_ticks

OUT = DATA_DIR / "m1"
START, END = date(2016, 1, 1), date(2026, 9, 24)
PAIRS = ["AUDJPY", "AUDUSD", "BTCUSD", "DE40", "ETHUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD",
         "UK100", "US30", "USDCAD", "USDJPY", "USTEC", "XAUUSD",
         "NZDUSD", "USDCHF", "US500", "JP225", "AUS200", "HK50",
         "XAGUSD", "XPTUSD", "XTIUSD", "XBRUSD", "XNGUSD"]


def _month_chunks():
    d = START
    while d <= END:
        nxt = (d.replace(day=1) + timedelta(days=32)).replace(day=1)
        yield d, min(nxt - timedelta(days=1), END)
        d = nxt


def build(symbol: str) -> str:
    parts = []
    for a, b in _month_chunks():
        t = load_ticks(symbol, a, b)
        if len(t) == 0:
            continue
        m = t.ts // 60_000
        s = np.flatnonzero(np.r_[True, m[1:] != m[:-1]])
        e = np.r_[s[1:], len(t)]
        spr = t.ask - t.bid
        parts.append(np.column_stack([
            (m[s] * 60_000).astype(np.float64),
            t.bid[s], np.maximum.reduceat(t.bid, s), np.minimum.reduceat(t.bid, s), t.bid[e - 1],
            t.ask[e - 1], np.minimum.reduceat(spr, s), np.add.reduceat(spr, s) / (e - s), (e - s).astype(np.float64),
        ]))
    x = np.concatenate(parts)
    OUT.mkdir(exist_ok=True)
    np.savez(OUT / f"{symbol}.npz", ts=x[:, 0].astype(np.int64), o=x[:, 1], h=x[:, 2], l=x[:, 3], c=x[:, 4],
             ca=x[:, 5], smin=x[:, 6], smean=x[:, 7], n=x[:, 8].astype(np.int64))
    return f"{symbol}: {len(x)} minutes"


def load(symbol: str) -> dict:
    z = np.load(OUT / f"{symbol}.npz")
    return {k: z[k] for k in z.files}


if __name__ == "__main__":
    pairs = sys.argv[1:] or PAIRS
    with ProcessPoolExecutor(5) as ex:
        for msg in ex.map(build, pairs):
            print(msg, flush=True)
