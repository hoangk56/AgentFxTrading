"""1m fill prices for alt perps from fapi REST (public). need: dict sym -> set of minute timestamps (ms) whose 1m bar
close we need (bar starting at that minute, plus up to 4 later minutes as fallback when a minute has no bar).
Cache: research/data/upbit/binance/alt_1m/<SYM>.csv (t, c) - only bars < 2025-01-01."""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kdata import UP, CUT, M

D = os.path.join(UP, "binance", "alt_1m")
os.makedirs(D, exist_ok=True)


def load(sym):
    p = os.path.join(D, sym + ".csv")
    out = {}
    if os.path.exists(p):
        with open(p) as f:
            for t, c in csv.reader(f):
                out[int(t)] = float(c)
    return out


def fetch(need, limit=99):
    import net
    for sym in sorted(need):
        have = load(sym)
        miss = sorted(t for t in need[sym] if t not in have and t < CUT)
        rows = []
        k = 0
        while k < len(miss):
            st = miss[k]
            js = net.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={st}&limit={limit}")
            got = {int(x[0]): float(x[4]) for x in (js or []) if int(x[0]) < CUT}
            if not got:  # no bars: mark as NaN so we do not retry
                got = {st: float("nan")}
            rows += [(t, c) for t, c in got.items() if t not in have]
            have.update(got)
            end = st + limit * M
            while k < len(miss) and miss[k] < end:
                k += 1
        if rows:
            with open(os.path.join(D, sym + ".csv"), "a", newline="") as f:
                csv.writer(f).writerows(rows)
        print("1m", sym, len(miss), "needed,", len(rows), "bars added", flush=True)


def price_at(cache, t, fallback=4):
    for d in range(fallback + 1):
        v = cache.get(t + d * M)
        if v is not None and np.isfinite(v):
            return v
    return np.nan
