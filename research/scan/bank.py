"""A broad bank of simple rule families, run on every symbol over 2025-2026 on the M1 engine.

Writes results/bank_stats.csv: one row per (config, symbol, period) with n, sum R, sum R^2, so any grouping of
symbols can be scored later. The pass bar is strict (t >= 2 in each of P1, P2, P3), which is what keeps a
wide scan honest: a no-edge config passes it with probability ~0.023^3."""
import csv
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from research.indicators import prior_max, prior_min, rsi
from research.scan.data import atr, resample
from research.scan.engine import Order, simulate
from research.scan.m1 import PAIRS, load

OUT = Path(__file__).resolve().parents[1] / "results" / "bank_stats.csv"
TFS = {"M15": (15, 0), "H1": (60, 0), "H4": (240, 0), "D1": (1440, 120)}


def _orders(b, a, sig, H, SLK, TPK, tag):
    out = []
    n = len(b)
    for i in np.flatnonzero(sig):
        if i < 25 or i >= n - 1 or not np.isfinite(a[i]) or a[i] <= 0:
            continue
        s = int(sig[i])
        j = min(i + H, n - 1)
        ref = b.c[i]
        out.append(Order(int(b.last[i]) + 1, s, ref - s * SLK * a[i], int(b.last[j]),
                         tp=(ref + s * TPK * a[i]) if TPK else None, tag=tag))
    return out


def configs():
    """(name, tf, signal-builder kwargs, H, SLK, TPK)."""
    cfg = []
    for tf in TFS:
        for L, Z in itertools.product((1, 3, 6, 12), (1.0, 2.0, 3.0)):
            for mode in (1, -1):
                for H, SLK, TPK in ((3, 1.5, None), (12, 2.0, None), (3, 1.0, 1.0), (12, 2.0, 2.0)):
                    cfg.append((f"zmove{'F' if mode > 0 else 'R'}_{tf}_L{L}_Z{Z}_H{H}_SL{SLK}_TP{TPK}", tf,
                                dict(kind="zmove", L=L, Z=Z, mode=mode), H, SLK, TPK))
        for N in (10, 20, 55):
            for mode in (1, -1):
                for H, SLK, TPK in ((6, 1.5, None), (24, 2.5, None), (6, 1.0, 1.5)):
                    cfg.append((f"donch{'F' if mode > 0 else 'R'}_{tf}_N{N}_H{H}_SL{SLK}_TP{TPK}", tf,
                                dict(kind="donch", N=N, mode=mode), H, SLK, TPK))
        for P, lo in ((2, 10.0), (2, 5.0), (14, 30.0), (14, 20.0)):
            for mode in (1, -1):
                for H, SLK, TPK in ((3, 1.5, None), (12, 2.0, None), (6, 1.0, 1.0)):
                    cfg.append((f"rsi{'F' if mode > 0 else 'R'}_{tf}_P{P}_lo{lo:g}_H{H}_SL{SLK}_TP{TPK}", tf,
                                dict(kind="rsi", P=P, lo=lo, mode=mode), H, SLK, TPK))
    return cfg


def signal(b, a, kind, mode, **k):
    n = len(b)
    if kind == "zmove":
        L, Z = k["L"], k["Z"]
        z = np.zeros(n)
        z[L:] = (b.c[L:] - b.c[:-L]) / a[L:]
        raw = np.where(z > Z, 1, np.where(z < -Z, -1, 0))
    elif kind == "donch":
        hh, ll = prior_max(b.h, k["N"]), prior_min(b.l, k["N"])
        with np.errstate(invalid="ignore"):
            up, dn = b.c > hh, b.c < ll
        prev_up, prev_dn = np.r_[False, up[:-1]], np.r_[False, dn[:-1]]
        raw = np.where(up & ~prev_up, 1, np.where(dn & ~prev_dn, -1, 0))
    elif kind == "rsi":
        r = rsi(b.c, k["P"])
        lo = k["lo"]
        # momentum reading: RSI beyond the extreme = strength; mode -1 fades it
        raw = np.where(r > 100 - lo, 1, np.where(r < lo, -1, 0))
    else:
        raise ValueError(kind)
    return (raw * mode).astype(np.int8)


def run_symbol(symbol):
    m = load(symbol)
    bars = {tf: resample(m, *TFS[tf]) for tf in TFS}
    atrs = {tf: atr(bars[tf], 20) for tf in TFS}
    rows = []
    for name, tf, sk, H, SLK, TPK in configs():
        b, a = bars[tf], atrs[tf]
        fills = simulate(m, symbol, _orders(b, a, signal(b, a, **sk), H, SLK, TPK, name))
        for P in ("P1", "P2", "P3"):
            r = np.array([f.r for f in fills if f.period == P])
            rows.append((name, symbol, P, len(r), float(r.sum()), float((r * r).sum())))
    return rows


if __name__ == "__main__":
    pairs = sys.argv[1:] or PAIRS
    OUT.parent.mkdir(exist_ok=True)
    with ProcessPoolExecutor(6) as ex, OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config", "symbol", "period", "n", "sum_r", "sum_r2"])
        for rows in ex.map(run_symbol, pairs):
            w.writerows(rows)
            print(rows[0][1], len(rows), flush=True)
