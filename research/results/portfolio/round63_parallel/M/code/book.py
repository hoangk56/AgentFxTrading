"""Round 63 stream M: the one declared book (HYPOTHESES_M section 4). Equal risk = trade net / row IS per-trade sd
(net at the venue upper bound); daily P&L by UTC entry day; IS correlations; power at VAL size.
Usage: python book.py ID ID ..."""
import datetime as dt
import json
import math
import sys

import numpy as np

import eng
import run


def load(i):
    z = np.load(run.OUT / f"{i}_trades.npz", allow_pickle=True)
    return {k: z[k] for k in z.files}


def daily(t, sd, col):
    if col == "x15":
        v = t["gross"] - 1.5 * t["up"]
    elif col == "lat1":
        v = t["gross1"] - t["up1"]
    elif col == "lo":
        v = t["gross"] - t["lo"]
    else:
        v = t["gross"] - t["up"]
    d = eng.day_of(t["ms_in"])
    u, inv = np.unique(d, return_inverse=True)
    return dict(zip(u.tolist(), np.bincount(inv, weights=v / sd).tolist()))


def series(ids, col):
    per = {}
    for i in ids:
        t = load(i)
        m = t["ms_in"] < eng.VAL0
        sd = float(np.nanstd((t["gross"] - t["up"])[m], ddof=1))
        per[i] = daily(t, sd, col)
    days = sorted(set().union(*[set(p) for p in per.values()]))
    mat = np.array([[per[i].get(d, 0.0) for i in ids] for d in days])
    return np.array(days), mat


def era_stats(days, tot):
    out = {}
    for e, m in (("IS", days < eng.VAL0 // 86400000), ("VAL", days >= eng.VAL0 // 86400000)):
        x = tot[m]
        yrs = (6.0 if e == "IS" else 3.0)
        mu = x.mean(); sd = x.std(ddof=1); t = mu / sd * math.sqrt(x.size)
        sh = mu / sd
        y = np.array([dt.datetime.fromtimestamp(int(d) * 86400, eng.UTC).year for d in days[m]])
        by = {int(k): float(x[y == k].sum()) for k in np.unique(y)}
        out[e] = dict(active_days=int(x.size), days_per_year=x.size / yrs, mean_R=float(mu), t=float(t),
                      daily_sharpe=float(sh), power_own=float(sh * math.sqrt(1.73 * x.size / yrs)), R_per_year=float(x.sum() / yrs),
                      by_year=by)
    return out


if __name__ == "__main__":
    ids = sys.argv[1:]
    res = {"members": ids}
    for col in ("up", "x15", "lat1", "lo"):
        days, mat = series(ids, col)
        tot = mat.sum(1)
        res[col] = era_stats(days, tot)
        if col == "up":
            m = days < eng.VAL0 // 86400000
            res["corr_IS"] = np.corrcoef(mat[m].T).round(3).tolist() if len(ids) > 1 else [[1.0]]
    json.dump(res, open(run.OUT / f"book_{'_'.join(ids)}.json", "w"), indent=1)
    for col in ("up", "x15", "lat1", "lo"):
        for e in ("IS", "VAL"):
            s = res[col][e]
            print(f"{col:4s} {e:3s} days {s['active_days']:5d} mean R {s['mean_R']:+.4f} t {s['t']:+.2f} "
                  f"daily Sharpe {s['daily_sharpe']:+.4f} power(own size) {s['power_own']:+.2f} R/yr {s['R_per_year']:+.1f} "
                  f"years {s['by_year']}")
    print("corr IS", res["corr_IS"])
