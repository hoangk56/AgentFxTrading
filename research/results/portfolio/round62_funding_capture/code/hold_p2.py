"""Round 62 P2 registered new-era HOLD look (PREREG_P2_post_stamp_1s.md).
Usage: python -I hold_p2.py event_syms.txt <empty zip scratch dir> <part k> <n parts>   (download + per-event rows)
       python -I hold_p2.py event_syms.txt score                                       (verdict)
Events: stamps T in 2025-01-01..2026-10-29 with |f_prev| >= 30 bp (funding files as in IS / VAL); random sample of
600 (numpy seed 101) in a fixed order; payer side; entry = last aggTrade at T+1 s, exit = last aggTrade at T+60 s."""
import csv, io, json, os, sys, urllib.request, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, capture as K
A, B_ = 1735689600000, 1793318400000
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
OD = os.path.join(K.B, "aggtrades_stamps_hold"); os.makedirs(OD, exist_ok=True)
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
allsyms = sorted(set(syms) | {f[:-4] for d in ("funding", "funding_window") for f in os.listdir(os.path.join(K.B, d)) if f.endswith(".csv")})
EV = []
for s in allsyms:
    a = K.stamps(s, B_ - 1)
    for j in range(1, len(a)):
        T = int(a[j, 0] // 1000 * 1000)
        if A <= a[j, 0] < B_ and abs(a[j - 1, 1]) >= 0.003:
            EV.append((s, int(a[j, 0]), float(a[j - 1, 1])))
EV.sort()
idx = np.random.default_rng(101).choice(len(EV), size=min(600, len(EV)), replace=False)
SAMPLE = [EV[i] for i in idx]

def one(e, tmp):
    s, Tm, fp = e
    T = Tm // 3600000 * 3600000
    days = [str(np.datetime64(T, "ms"))[:10]]
    if T % 86400000 == 0:
        days.insert(0, str(np.datetime64(T - 86400000, "ms"))[:10])
    t_all, p_all = [], []
    for dd in days:
        url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{s}/{s}-aggTrades-{dd}.zip"
        zp = os.path.join(tmp, "x.zip")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r, open(zp, "wb") as f:
                f.write(r.read())
        except Exception as ex:
            return dict(sym=s, T=T, err=str(ex))
        with zipfile.ZipFile(zp) as z, z.open(z.namelist()[0]) as f:
            for line in io.TextIOWrapper(f):
                p = line.split(",")
                if p[0][:1].isdigit():
                    t = int(p[5])
                    if T - 5000 <= t <= T + 60000:
                        t_all.append(t - T); p_all.append(float(p[1]))
        os.remove(zp)
    t = np.array(t_all); p = np.array(p_all)
    if not len(t) or not (t < 0).any():
        return dict(sym=s, T=T, err="no trades")
    o = np.argsort(t, kind="stable"); t, p = t[o], p[o]
    payer = 1.0 if fp > 0 else -1.0
    px = lambda sec: p[t <= sec * 1000][-1]
    cost = 0.0012 if s in ("BTCUSDT", "ETHUSDT") else 0.0020
    return dict(sym=s, T=T, fp=fp, cost=cost, r1=payer * (px(60) / px(1) - 1), r2=payer * (px(60) / px(2) - 1))

if sys.argv[2] == "score":
    R = []
    for f in os.listdir(OD):
        if f.startswith("part_") and f.endswith(".json"):
            R += json.load(open(os.path.join(OD, f)))
    ok = [r for r in R if "err" not in r]
    print("sample %d, scored %d, errors %d" % (len(SAMPLE), len(ok), len(R) - len(ok)))
    v = np.array([r["r1"] - r["cost"] for r in ok]); v2 = np.array([r["r2"] - r["cost"] for r in ok]); v15 = np.array([r["r1"] - 1.5 * r["cost"] for r in ok])
    day = np.array([r["T"] // 86400000 for r in ok]); yr = np.array([str(np.datetime64(r["T"], "ms"))[:4] for r in ok])
    t = K.cluster_t(v, day)
    print("P2 HOLD net %+.1f bp, median %+.1f, sd %.1f, SR %.3f, t_cl %.2f, win %.0f%%" % (1e4 * v.mean(), 1e4 * np.median(v), 1e4 * v.std(ddof=1), v.mean() / v.std(ddof=1), t, 100 * np.mean(v > 0)))
    py = {y: 1e4 * v[yr == y].mean() for y in np.unique(yr)}
    print("per year", {y: round(x, 1) for y, x in py.items()}, "| entry T+2s %+.1f bp | costs x1.5 %+.1f bp" % (1e4 * v2.mean(), 1e4 * v15.mean()))
    fpp = np.array([r["fp"] for r in ok]); print("f>0 n %d %+.1f bp; f<0 n %d %+.1f bp" % ((fpp > 0).sum(), 1e4 * v[fpp > 0].mean() if (fpp > 0).any() else 0, (fpp < 0).sum(), 1e4 * v[fpp < 0].mean()))
    print("worst 5", np.round(1e4 * np.sort(v)[:5]))
    bars = {"1 net > 0 and t_cl >= 2.5": v.mean() > 0 and t >= 2.5, "2 entry T+2s > 0 and costs x1.5 > 0": v2.mean() > 0 and v15.mean() > 0,
            "3 2025 and 2026 > 0": all(x > 0 for x in py.values()), "4 >= 500 events scored": len(ok) >= 500}
    for k, b in bars.items(): print("  ", "PASS" if b else "FAIL", k)
    print("VERDICT:", "PASS (new-era LIVE)" if all(bars.values()) else "FAIL")
else:
    tmp, k, n = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    os.makedirs(tmp, exist_ok=True)
    out = [one(e, tmp) for i, e in enumerate(SAMPLE) if i % n == k]
    json.dump(out, open(os.path.join(OD, f"part_{k}.json"), "w"))
    print("part", k, "done", len(out))
