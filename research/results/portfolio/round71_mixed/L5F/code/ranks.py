"""Point-in-time rank of each L5F alt by trailing-30-day (d-30..d-1) perp quote volume among all perps in
binance/perp_1d (cut < 2025-01-01). Output L5F/out/ranks.npz: day0 (days since epoch of 2020-01-01), rank[sym]."""
import os, glob, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
D0 = 1577836800000 // 86400000; D1 = 1735689600000 // 86400000
ND = D1 - D0 + 31
mat = []; names = []
for f in sorted(glob.glob(os.path.join(R, "data", "binance", "perp_1d", "*.csv"))):
    s = os.path.basename(f)[:-4]
    try:
        a = np.loadtxt(f, delimiter=",", skiprows=1, usecols=(0, 6), ndmin=2)
    except Exception:
        continue
    if a.size == 0: continue
    d = (a[:, 0] // 86400000).astype(int) - (D0 - 31)
    k = (d >= 0) & (d < ND) & (a[:, 0] < 1735689600000)
    row = np.zeros(ND); row[d[k]] = a[k, 1]
    mat.append(row); names.append(s)
M = np.array(mat)  # syms x days (day 0 = 2019-12-01)
cs = np.cumsum(np.concatenate([np.zeros((M.shape[0], 1)), M], 1), 1)
# trailing sum over days d-30..d-1 for day index d (in the shifted frame)
tr = cs[:, 31:ND + 1 - 0][:, :D1 - D0] - cs[:, 1:D1 - D0 + 1]
ranks = {}
for s in ["SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "BTCUSDT", "ETHUSDT"]:
    i = names.index(s)
    ranks[s] = (tr > tr[i][None, :]).sum(0)
np.savez(os.path.join(OUT, "ranks.npz"), **ranks)
for s, r in ranks.items():
    print(s, "share of days rank<20:", round(float((r < 20).mean()), 3), "first-year min/max", r[:366].min(), r[:366].max())
