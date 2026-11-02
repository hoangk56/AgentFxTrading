"""Daily aggTrades for the HOLD events (A2/code/pull.py fetch() / parse(), redirected to research/data/upbit_hold_a2):
for each (symbol, day of N) keep trades in the event windows [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min],
pulling every UTC day those windows touch. npz fields t, p, q, m as stream A2 (analyze.py / checks.py read only these).
Run with python -I."""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # redirects net.LOG
import pull as P  # A2/code/pull.py (on sys.path via core)
HD = core.HD
OUT = os.path.join(HD, "npz"); TMP = os.path.join(HD, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
P.TMP, P.OUT = TMP, OUT
DAYMS = 86400000

E = list(csv.DictReader(open(os.path.join(HD, "hold_events.csv"))))
jobs = {}
for e in E:
    N, L = int(e["N"]), int(e["L"])
    win = [(N - 600000, N + 1800000), (L - 600000, L + 300000)]
    for sym in (e["perp"], "BTCUSDT"):
        jobs.setdefault((sym, e["day"]), []).extend(win)
for k, ((sym, dayN), win) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))):
    out = os.path.join(OUT, f"{sym}_{dayN}.npz")
    if os.path.exists(out):
        continue
    days = sorted({str(np.datetime64(int(t), "ms"))[:10] for a, b in win for t in (a, b)})
    parts = []
    for d in days:
        zp, s = P.fetch(sym, d)
        if zp is None:
            print("MISS", sym, d, s, flush=True); continue
        a = P.parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        a[:, 2] = t
        parts.append(a)
    if not parts:
        continue
    a = np.concatenate(parts)
    o = np.argsort(a[:, 2], kind="stable"); a = a[o]; t = a[:, 2].astype(np.int64)
    keep = np.zeros(len(t), bool)
    for x, y in win:
        keep |= (t >= x) & (t <= y)
    np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8))
    print(f"{k+1}/{len(jobs)} {sym} {dayN} days {len(days)} kept {keep.sum()}", flush=True)
print("done")
