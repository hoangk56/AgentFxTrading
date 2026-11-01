"""Round 62 P1 (payer side in the hour after an extreme stamp), IS / VAL. Usage: python -I run_p1.py syms seen.txt"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, capture as K
END = 1735689599999
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
seen = {l.strip() for l in open(sys.argv[2]) if l.strip()}
allev = [e for s in syms for e in K.events(s, END, 0.001)]
day = lambda e: e["T"] // 86400000
yr = lambda e: int(np.datetime64(int(e["T"]), "ms").astype("datetime64[Y]").astype(int) + 1970)
era = lambda e: next((k for k, (a, b) in K.ERAS.items() if a <= e["T"] < b), None)
def rep(E, label, f=lambda e: e["p1"]):
    for er in ("IS", "VAL"):
        X = [e for e in E if era(e) == er]
        if len(X) < 5: continue
        r = np.array([f(e) for e in X]); yy = {}
        for e, v in zip(X, r): yy.setdefault(yr(e), []).append(v)
        print("%-30s %-3s n %5d mean %+7.1f bp sd %6.1f SR/tr %+.3f t_cl %+5.2f yrs %s" % (label, er, len(r), 1e4 * r.mean(), 1e4 * r.std(ddof=1),
              r.mean() / r.std(ddof=1), K.cluster_t(r, [day(e) for e in X]), {y: round(1e4 * np.mean(v), 1) for y, v in sorted(yy.items())}))
E = [e for e in allev if abs(e["fp"]) >= 0.003]
rep(E, "P1 all")
rep([e for e in E if e["sym"] not in seen], "P1 unseen symbols")
rep([e for e in E if e["sym"] in seen], "P1 seen symbols")
rep(E, "P1 costs x1.5", lambda e: e["p1"] - 0.5 * e["cost"])
for tier in (0.001, 0.005, 0.01):
    rep([e for e in allev if abs(e["fp"]) >= tier], "P1 tier %dbp" % round(1e4 * tier))
rep([e for e in E if e["fp"] > 0], "P1 f>0 (long after)")
rep([e for e in E if e["fp"] < 0], "P1 f<0 (short after)")
rep([e for e in E if e["interval"] <= 2], "P1 1h/2h interval")
# drop the 5 best trades per era
for er in ("IS", "VAL"):
    r = np.sort([e["p1"] for e in E if era(e) == er])
    print("drop top 10 trades %s: mean %+.1f bp" % (er, 1e4 * r[:-10].mean()))
rng = np.random.default_rng(1)
for er in ("IS", "VAL"):
    X = [e for e in E if era(e) == er]; real = np.mean([e["p1"] for e in X]); d = []
    for _ in range(300):
        v = [K.random_p1(e, rng) for e in X]; d.append(np.mean([x for x in v if x is not None]))
    d = np.array(d); print("random %s: real %+.1f, random median %+.1f, beaten %.1f%%" % (er, 1e4 * real, 1e4 * np.median(d), 100 * np.mean(d < real)))
syms_n = {}
for e in E: syms_n.setdefault(era(e), set()).add(e["sym"])
print({k: len(v) for k, v in syms_n.items()}, "symbols with events")
