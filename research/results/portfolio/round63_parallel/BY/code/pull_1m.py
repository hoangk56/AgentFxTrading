"""Information-only pull (addendum 1): Bybit 1m klines of both legs for [entry hour, entry hour + 16 min) and
[exit hour, exit hour + 16 min) of each graded trade (../out/trades_by.csv). End capped at 2024-12-31 23:59:59.999.
Usage: python -I pull_1m.py <trades_by.csv> <root> <part> <nparts>"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pull as P
src, root, part, nparts = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(os.path.join(root, "m1"), exist_ok=True)
P.LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
spot = {r["perp"]: (r["spot"]) for r in csv.DictReader(open(os.path.join(root, "cands.csv")))}
M = 60000
rows = list(csv.DictReader(open(src)))
for i, r in enumerate(rows):
    if i % nparts != part:
        continue
    import numpy as np
    e = int(np.datetime64(r["entry_utc"], "ms").astype(np.int64))
    x = e + int(r["hold_h"]) * 3600000
    for t0 in (e, x):
        for cat, sym in (("linear", r["perp"]), ("spot", spot[r["perp"]])):
            p = os.path.join(root, "m1", f"{cat}_{sym}_{t0}.csv")
            if os.path.exists(p) or t0 > P.CAP:
                continue
            j = P.get(f"/v5/market/kline?category={cat}&symbol={sym}&interval=1&start={t0}&end={min(t0 + 15 * M, P.CAP)}&limit=20")
            L = j["result"]["list"] if j and j.get("retCode") == 0 else []
            with open(p, "w") as f:
                f.write("t,o,h,l,c,vol,turnover\n")
                for k in sorted(L, key=lambda z: int(z[0])):
                    if int(k[0]) <= P.CAP:
                        f.write(",".join(k[:7]) + "\n")
    print(i, flush=True)
