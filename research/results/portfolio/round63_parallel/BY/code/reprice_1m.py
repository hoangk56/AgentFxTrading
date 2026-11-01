"""Information only (addendum 1): re-price the graded trades with entry and exit at the close of minute m (1, 5, 15)
of the entry / exit hour on Bybit 1m klines. Funding, costs and carry as in the graded trade."""
import csv, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import by
B = by.B
from basis import cl_t, DAY
R = os.path.join(by.BD, "m1")
spot = {r["perp"]: r["spot"] for r in csv.DictReader(open(os.path.join(by.BD, "cands.csv")))}
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "out", "trades_by.csv"))))
M = 60000


def px(cat, sym, t0, m):
    p = os.path.join(R, f"{cat}_{sym}_{t0}.csv")
    if not os.path.exists(p):
        return None, "nofile"
    a = [x for x in csv.reader(open(p))][1:]
    a = [(int(x[0]), float(x[4]), float(x[5])) for x in a]
    lim = t0 + (m - 1) * M
    c = [x for x in a if x[0] <= lim]
    if not c:
        return None, "nobar"
    return c[-1][1], ("ok" if c[-1][0] == lim else "stale")


out = {}
for m in (1, 5, 15):
    net, tt, era, miss = [], [], [], 0
    for r in rows:
        e = int(np.datetime64(r["entry_utc"], "ms").astype(np.int64)); x = e + int(r["hold_h"]) * 3600000
        s = spot[r["perp"]]
        Fe, _ = px("linear", r["perp"], e, m); Se, _ = px("spot", s, e, m)
        Fx, _ = px("linear", r["perp"], x, m); Sx, _ = px("spot", s, x, m)
        if None in (Fe, Se, Fx, Sx):
            miss += 1; continue
        price = -((Sx / Se - 1) - (Fx / Fe - 1))
        n_ = price + (float(r["fund_bp"]) - float(r["cost_bp"]) - float(r["carry_bp"])) / 1e4
        net.append(n_); tt.append(e)
    net, tt = np.array(net), np.array(tt)
    for nm, (a, b) in B.ERAS.items():
        w = (tt >= a) & (tt < b)
        print(f"m{m} {nm} n {w.sum()} net {net[w].mean()*1e4:.1f} median {np.median(net[w])*1e4:.1f} t {cl_t(net[w], tt[w]//DAY):.2f} missing {miss}")
