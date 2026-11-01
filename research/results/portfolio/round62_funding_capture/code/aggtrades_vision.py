"""Round 62: first-60s price path after VAL stamps from data.binance.vision daily aggTrades (random sample).
Zips go to an empty scratch folder (argv 2) and are deleted after the window is extracted."""
import csv, io, json, os, sys, time, urllib.request, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, capture as K
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
END = 1735689599999
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
tmp = sys.argv[2]; os.makedirs(tmp, exist_ok=True)
n_sample = int(sys.argv[3]) if len(sys.argv) > 3 else 200
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
era_a, era_b = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (1640995200000, END)
tag = sys.argv[7] if len(sys.argv) > 7 else "val"
exclude_seed = int(sys.argv[8]) if len(sys.argv) > 8 else None
E = [e for s in syms for e in K.events(s, END, 0.003) if era_a <= e["T"] < era_b]
excl = set()
if exclude_seed is not None:
    excl = set(np.random.default_rng(exclude_seed).choice(len(E), size=min(200, len(E)), replace=False).tolist())
rng = np.random.default_rng(seed)
pool = np.array([i for i in range(len(E)) if i not in excl])
idx = rng.choice(pool, size=min(n_sample, len(pool)), replace=False)
od = os.path.join(K.B, "aggtrades_stamps"); os.makedirs(od, exist_ok=True)
log = open(os.path.join(od, "vision_requests.log"), "a", buffering=1)
res = []
for j in idx:
    e = E[j]; T = e["T"]
    day = str(np.datetime64(int(T), "ms"))[:10]
    days = [day]
    if T % 86400000 == 0:  # stamp at 00:00: the pre-stamp trades are in the previous day's file
        days = [str(np.datetime64(int(T - 86400000), "ms"))[:10], day]
    t_all, p_all = [], []
    for dd in days:
        url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{e['sym']}/{e['sym']}-aggTrades-{dd}.zip"
        zp = os.path.join(tmp, "x.zip")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(zp, "wb") as f:
                f.write(r.read())
            log.write(f"{url}\t200\t{os.path.getsize(zp)}\n")
        except Exception as ex:
            log.write(f"{url}\tERR {ex}\n"); continue
        with zipfile.ZipFile(zp) as z:
            name = z.namelist()[0]
            with z.open(name) as f:
                for line in io.TextIOWrapper(f):
                    parts = line.split(",")
                    if not parts[0][:1].isdigit():
                        continue
                    t = int(parts[5])
                    if T - 5000 <= t <= T + 60000:
                        t_all.append(t - T); p_all.append(float(parts[1]))
        os.remove(zp)
    if not t_all:
        continue
    t = np.array(t_all); p = np.array(p_all); o = np.argsort(t, kind="stable"); t, p = t[o], p[o]
    pre = p[t < 0]
    if not len(pre):
        continue
    payer = -e["side"]; ref = pre[-1]
    row = {"sym": e["sym"], "T": int(T), "n": int(len(t))}
    for s in (0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 30, 59, 60):
        q = p[t <= s * 1000]
        row[str(s)] = float(payer * (q[-1] / ref - 1))
    first = p[t >= 0]
    row["first_trade"] = float(payer * (first[0] / ref - 1)) if len(first) else None
    res.append(row)
json.dump(res, open(os.path.join(od, f"sample_{tag}_vision.json"), "w"))
print("events", len(res))
for s in ("first_trade", "0.1", "0.25", "0.5", "1", "2", "3", "5", "10", "30", "59", "60"):
    v = np.array([r[s] for r in res if r[s] is not None], float)
    print("payer move vs last pre-stamp trade at %-11s: mean %+6.1f bp, median %+6.1f" % (s, 1e4 * v.mean(), 1e4 * np.median(v)))
