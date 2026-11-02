"""Registered HOLD run of PREREG A2-D5L (run once): core.grade on the HOLD events (D5-L: long alt perp / short BTC perp
at the first aggTrades >= N + 5 s, exit at the first trades >= L, 20 bp + declared slippage + funding).
Pass (DEMO): net > 0 and day-clustered t >= 1.0. Also: aggressor-side and worst-of-1 s fills, x1.5, d 10 s, years,
share of events whose +2 % burst starts after N + 5 s, median path at +2 / +5 / +300 s."""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
Z = core.Z
E = []
for r in csv.DictReader(open(os.path.join(core.HD, "hold_events.csv"))):
    r["N"], r["L"] = int(r["N"]), int(r["L"]); E.append(r)
core.use_npz(os.path.join(core.HD, "npz"))
E = [e for e in E if os.path.exists(os.path.join(core.HD, "npz", f"{e['perp']}_{e['day']}.npz"))
     and os.path.exists(os.path.join(core.HD, "npz", f"BTCUSDT_{e['day']}.npz"))]
out, rows = core.grade(E, "HOLD")
late, path = [], {2: [], 5: [], 300: []}
for x in rows:
    e = x["e"]; A = Z.load(e["perp"], e["day"]); B = Z.load("BTCUSDT", e["day"]); N = e["N"]
    ra, rb = Z.at(A, N - 60000), Z.at(B, N - 60000)
    for o in path:
        path[o].append(float(np.log(Z.at(A, N + o * 1000) / ra) - np.log(Z.at(B, N + o * 1000) / rb)))
    a0, a1 = np.searchsorted(A["t"], [N - 300000, N + 300000])
    ta, pa = A["t"][a0:a1], A["p"][a0:a1]
    r = np.log(pa / ra) - np.log(B["p"][np.searchsorted(B["t"], ta, "right") - 1] / rb)
    hit = np.where(r >= 0.02)[0]
    late.append(bool(len(hit) and ta[hit[0]] > N + 5000))
print(f"   events {len(rows)}; burst onset after N + 5 s: {np.mean(late):.2f}; median path (bp) "
      + ", ".join(f"+{o}s {np.median(v)*1e4:+.0f}" for o, v in path.items()))
m, t, n = out["net"]
print("PASS (DEMO bar: net > 0 and t >= 1.0)" if (m > 0 and t >= 1.0) else "FAIL: drop the seconds-level reaction family")
