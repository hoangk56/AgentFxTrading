"""Registered cell PREREG_C1_hk50_rebound: C1_k1.5 signal, LONG HK50, h1, entry 01:45 UTC on CN day D+1.
usage: run_c1.py dry   -> IS / VAL only (margin and prices cut at 2024-12-31)
       run_c1.py hold  -> IS / VAL / HOLD (margin to 2026-09-24, HK50 M1 to the end of 2026-09-24); run once."""
import sys, os, json, glob, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import lib            # frozen copy (same bytes as the grading engine)
import sig
import engine

MODE = sys.argv[1]
assert MODE in ("dry", "hold")
SCR = lib.S
DIRS = [f"{SCR}/web/em_lshj"] + ([f"{SCR}/web/em_hold"] if MODE == "hold" else [])
CUT = dt.date(2024, 12, 31) if MODE == "dry" else dt.date(2026, 9, 24)
lib.CUT = CUT
lib.HOLD_MS = 1735689600000 if MODE == "dry" else 1790294400000  # 2025-01-01 / 2026-09-25 00:00 UTC


def load_margin():
    rows = {}
    for d0 in DIRS:
        for f in sorted(glob.glob(f"{d0}/*.json")):
            for r in json.load(open(f))["result"]["data"]:
                d = dt.date.fromisoformat(r["DIM_DATE"][:10])
                if d > CUT:
                    continue
                rows[d] = r
    return [rows[d] | {"date": d} for d in sorted(rows)]


lib.load_margin = load_margin          # sig.series() reads through lib.load_margin
s = sig.series()
D = s["D"]
zg = sig.tz(s["g"], 60)
SIG = {D[i]: 1 for i in range(len(D)) if s["zdf"][i] < 0 and zg[i] <= -1.5}   # C1_k1.5; side LONG HK50
EP = sig.episodes(SIG, D)
IDX = {d: i for i, d in enumerate(D)}

rows, open_exits = [], []
for d in sorted(SIG):
    i = IDX[d]
    if d.year < 2016:
        continue
    open_exits = [x for x in open_exits if x > i + 1]
    if len(open_exits) >= 3:
        continue
    w = engine.windows(D, i, "h1")
    if w is None:
        continue
    r = lib.trade("HK50", 1, w[0], w[1])
    if r is None:
        continue
    rows.append(dict(d=d, era=lib.era(d), ep=EP[d], mid=r[0], net=r[1]))
    open_exits.append(i + 2)


def st(rr):
    if len(rr) < 3:
        return dict(n=len(rr))
    mid = np.array([r["mid"] for r in rr]); net = np.array([r["net"] for r in rr]); g = np.array([r["ep"] for r in rr])
    return dict(n=len(rr), eps=len(set(g)), mid=round(mid.mean(), 2), net=round(net.mean(), 2),
                t_net=round(lib.cluster_t(net, g), 3), sd=round(net.std(ddof=1), 1),
                sharpe=round(net.mean() / net.std(ddof=1), 4), win=round(float(np.mean(net > 0)), 3))


out = {"mode": MODE, "margin_days": len(D), "margin_last": str(D[-1]),
       "hk50_last_bar_utc": str(dt.datetime.fromtimestamp(lib.load("HK50")["ts"][-1] / 1000, dt.timezone.utc))}
eras = ("IS", "VAL") if MODE == "dry" else ("IS", "VAL", "HOLD")
for e in eras:
    out[e] = st([r for r in rows if r["era"] == e])
if MODE == "hold":
    out["IS+VAL+HOLD"] = st(rows)
    out["HOLD_trades"] = [(str(r["d"]), round(r["net"], 1), r["ep"]) for r in rows if r["era"] == "HOLD"]
print(json.dumps(out, indent=1))
