"""Finer split of the notice minute (descriptive): gross alt - BTC on fapi 1m closes between bars starting at
N0-1, N0 (the notice minute), N0+1, N0+5, N0+15 (N0 = floor_minute(N)). Uses run.py's cached k2rule.px."""
import os, sys, pickle
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import run
M = 60000
d = pickle.load(open(os.path.join(run.CACHE, "rows.pkl"), "rb"))["rows"]
ev, _ = run.events(); P = {r["coin"] + r["N_utc"]: r for r in ev}
pts = (-1, 0, 1, 5, 15)
out = {"IS": [], "VAL": []}
for r in d:
    n0 = P[r["coin"] + r["N_utc"]]["N"] // M * M
    a = [run.px(r["perp"], n0 + k * M) for k in pts]; b = [run.px("BTCUSDT", n0 + k * M) for k in pts]
    g = [(a[i + 1] / a[i] - 1) - (b[i + 1] / b[i] - 1) for i in range(len(pts) - 1)]
    out[r["era"]].append(g)
pickle.dump(run._PX, open(run.PXF, "wb"))
lab = ["N0-1 -> N0", "N0 -> N0+1", "N0+1 -> N0+5", "N0+5 -> N0+15"]
lines = []
for era, v in out.items():
    v = np.array(v) * 1e4
    for j, l in enumerate(lab):
        lines.append(f"{era:3s} {l:14s} n {len(v)} mean {np.nanmean(v[:, j]):+7.0f} median {np.nanmedian(v[:, j]):+7.0f} share>0 {np.mean(v[:, j] > 0):.2f}")
txt = "\n".join(lines); print(txt); open(os.path.join(run.A, "split_output.txt"), "w").write(txt + "\n")
