"""Round 62: price path in the first 60 s after a stamp from aggTrades (sample of IS / VAL events)."""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, capture as K
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
END = 1735689599999
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
E = [e for s in syms for e in K.events(s, END, 0.003) if 1640995200000 <= e["T"] < END]
rng = np.random.default_rng(7)
idx = rng.choice(len(E), size=min(300, len(E)), replace=False)
od = os.path.join(K.B, "aggtrades_stamps"); os.makedirs(od, exist_ok=True)
log = open(os.path.join(od, "requests.log"), "a", buffering=1)
out = []
for j in idx:
    e = E[j]; T = e["T"]
    url = f"https://fapi.binance.com/fapi/v1/aggTrades?symbol={e['sym']}&startTime={T - 5000}&endTime={T + 60000}&limit=1000"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            d = json.loads(r.read()); log.write(f"{url}\t200\t{len(d)}\n")
    except Exception as ex:
        log.write(f"{url}\tERR {ex}\n"); continue
    time.sleep(0.25)
    if not d: continue
    t = np.array([x["T"] for x in d]) - T; p = np.array([float(x["p"]) for x in d])
    pre = p[t < 0]
    if not len(pre): continue
    ref = pre[-1]
    payer = -e["side"]
    row = {"sym": e["sym"], "T": T, "trades": len(d), "capped": len(d) == 1000}
    for s in (0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 59):
        q = p[t <= s * 1000]
        row[s] = payer * (q[-1] / ref - 1) if len(q) else np.nan
    out.append(row)
json.dump(out, open(os.path.join(od, "sample_val.json"), "w"))
print("events", len(out), "capped at 1000 trades", sum(r["capped"] for r in out))
for s in (0.2, 0.5, 1, 2, 3, 5, 10, 20, 30, 59):
    v = np.array([r[s] for r in out]); print("payer move from last pre-stamp trade to T+%4.1fs: mean %+6.1f bp median %+6.1f" % (s, 1e4 * np.nanmean(v), 1e4 * np.nanmedian(v)))
