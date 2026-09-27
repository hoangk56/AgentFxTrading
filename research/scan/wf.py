"""Walk-forward ridge model per symbol (see results/strategy_prereg.md, WF1): monthly refit on the prior 6
months, trade the top decile of |prediction| in the direction of the prediction."""
import argparse
from datetime import datetime, timezone

import numpy as np

from research.indicators import ema, rsi
from research.m1bars import atr, resample
from research.scan.engine import Order, simulate
from research.m1 import PAIRS, load

HZ = 4


def features(b, n_ticks):
    a20 = atr(b, 20)
    a5 = atr(b, 5)
    c = b.c
    F = {}
    for k in (1, 4, 16, 64):
        r = np.full(len(c), np.nan)
        r[k:] = (c[k:] - c[:-k]) / a20[k:]
        F[f"r{k}"] = r
    hh = np.array([np.nan] * 19 + [b.h[i - 19:i + 1].max() for i in range(19, len(c))])
    ll = np.array([np.nan] * 19 + [b.l[i - 19:i + 1].min() for i in range(19, len(c))])
    with np.errstate(invalid="ignore", divide="ignore"):
        F["rangepos"] = (c - ll) / (hh - ll) - 0.5
        F["volratio"] = a5 / a20 - 1
        F["body"] = (c - b.o) / (b.h - b.l)
        F["ema"] = (c - ema(c, 50)) / a20
        F["rsi"] = rsi(c, 14) / 50 - 1
        act = n_ticks / np.convolve(np.r_[np.full(95, n_ticks[:96].mean()), n_ticks], np.ones(96) / 96, "valid") - 1
    F["act"] = act
    F["r1xact"] = F["r1"] * act
    F["shock"] = np.sign(F["r1"]) * (np.abs(F["r1"]) > 2)
    hour = (b.t // 3_600_000) % 24
    F["sinh"], F["cosh"] = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
    X = np.column_stack(list(F.values()))
    y = np.full(len(c), np.nan)
    y[:-HZ] = (c[HZ:] - c[:-HZ]) / a20[:-HZ]
    return X, y, a20, list(F)


def month_index(t):
    d = [datetime.fromtimestamp(x / 1000, timezone.utc) for x in t]
    return np.array([x.year * 12 + x.month - 1 for x in d])


def walk_forward(symbol, tf=15, train_months=6, lam=0.1, q=0.9, SLK=2.0):
    m = load(symbol)
    b = resample(m, tf)
    n_ticks = np.add.reduceat(m["n"], b.first).astype(float)
    X, y, a, names = features(b, n_ticks)
    mon = month_index(b.t)
    pred = np.full(len(y), np.nan)
    thr = np.full(len(y), np.nan)
    coefs = []
    for M in range(mon.min() + train_months, mon.max() + 1):
        tr = (mon >= M - train_months) & (mon < M)
        # labels of the last HZ training bars reach into month M: drop them
        last = np.flatnonzero(tr)
        if last.size:
            tr[last[-HZ:]] = False
        te = mon == M
        ok = tr & np.all(np.isfinite(X), 1) & np.isfinite(y)
        if ok.sum() < 500:
            continue
        mu, sd = X[ok].mean(0), X[ok].std(0) + 1e-12
        Z = (X[ok] - mu) / sd
        yt = np.clip(y[ok], -5, 5)
        w = np.linalg.solve(Z.T @ Z + lam * ok.sum() * np.eye(Z.shape[1]), Z.T @ (yt - yt.mean()))
        coefs.append(w)
        p_tr = Z @ w + yt.mean()
        okte = te & np.all(np.isfinite(X), 1)
        pred[okte] = ((X[okte] - mu) / sd) @ w + yt.mean()
        thr[okte] = np.quantile(np.abs(p_tr), q)
    sig = np.where(np.abs(pred) > thr, np.sign(pred), 0).astype(int)
    orders = []
    for i in np.flatnonzero(sig):
        if i >= len(b) - 1 or not np.isfinite(a[i]):
            continue
        s = int(sig[i]); j = min(i + HZ, len(b) - 1); ref = b.c[i]
        orders.append(Order(int(b.last[i]) + 1, s, ref - s * SLK * a[i], int(b.last[j]), tag=symbol))
    fills = simulate(m, symbol, orders)
    return fills, np.array(coefs), names, (pred, y)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", type=int, default=15)
    ap.add_argument("--symbols", nargs="*", default=PAIRS)
    args = ap.parse_args()
    import csv, sys
    w = csv.writer(sys.stdout)
    for s in args.symbols:
        f, coefs, names, (pred, y) = walk_forward(s, args.tf)
        ok = np.isfinite(pred) & np.isfinite(y)
        ic = np.corrcoef(pred[ok], y[ok])[0, 1] if ok.sum() > 10 else np.nan
        for x in f:
            w.writerow([args.tf, s, x.t_in, x.side, f"{x.r:.5f}", f"{ic:.4f}"])
        sys.stdout.flush()
