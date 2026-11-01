"""Round 62 IS / VAL report. Usage: python -I run.py event_syms.txt [end_ms]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import capture as K

END = int(sys.argv[2]) if len(sys.argv) > 2 else 1735689599999
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
EV = {}
rates = {}
for s in syms:
    a = K.stamps(s, END)
    rates[s] = {int(t // K.H * K.H): r for t, r in a}
    EV[s] = K.events(s, END, 0.001)
allev = [e for s in syms for e in EV[s]]
day = lambda e: e["T"] // 86400000
yr = lambda e: int(np.datetime64(int(e["T"]), "ms").astype("datetime64[Y]").astype(int) + 1970)


def era(e):
    for k, (a, b) in K.ERAS.items():
        if a <= e["T"] < b:
            return k


def rep(E, label, f=K.net):
    for er in ("IS", "VAL", "HOLD"):
        X = [e for e in E if era(e) == er]
        if len(X) < 5:
            continue
        r = np.array([f(e) for e in X])
        yy = {}
        for e, v in zip(X, r):
            yy.setdefault(yr(e), []).append(v)
        print("%-26s %-4s n %5d mean %+7.1f bp sd %6.1f SR/tr %+.3f t_cl %+5.2f yrs %s" % (
            label, er, len(r), 1e4 * r.mean(), 1e4 * r.std(ddof=1), r.mean() / r.std(ddof=1),
            K.cluster_t(r, [day(e) for e in X]), {y: round(1e4 * np.mean(v), 1) for y, v in sorted(yy.items())}))


for tier in (0.001, 0.003, 0.005, 0.01):
    E = [e for e in allev if abs(e["fp"]) >= tier]
    rep(E, "net |f_prev|>=%dbp" % round(1e4 * tier))
E = [e for e in allev if abs(e["fp"]) >= 0.003]
rep(E, "  funding part", lambda e: e["fund"])
rep(E, "  price part", lambda e: e["price"])
rep(E, "  pre leg (no funding)", lambda e: e["pre"])
rep(E, "  post leg", lambda e: e["post"])
rep(E, "  costs x1.5", lambda e: K.net(e, 1.5))
rep([e for e in E if not np.isnan(e["wide"])], "  wide (T-2h..T+1h)", lambda e: e["wide"] + e["fund"] - e["cost"])
rep([e for e in E if e["fp"] > 0], "  f>0 (short)")
rep([e for e in E if e["fp"] < 0], "  f<0 (long)")
rep([e for e in E if e["interval"] > 2], "  8h/4h interval")
rep([e for e in E if e["interval"] <= 2], "  1h/2h interval")
rng = np.random.default_rng(0)
for er in ("IS", "VAL"):
    X = [e for e in E if era(e) == er]
    real = np.mean([K.net(e) for e in X])
    draws = []
    for _ in range(300):
        v = [K.random_window(e, rng, rates[e["sym"]]) for e in X]
        v = [x for x in v if x is not None]
        draws.append(np.mean(v))
    draws = np.array(draws)
    print("random %s: real %+.1f bp, random median %+.1f bp, beaten %.1f%%" % (er, 1e4 * real, 1e4 * np.median(draws), 100 * np.mean(draws < real)))
