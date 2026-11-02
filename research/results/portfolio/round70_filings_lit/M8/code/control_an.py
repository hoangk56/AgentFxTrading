"""Post-hoc control analysis (addendum A1): same cells at the same UTC clock time 7 / 14 days earlier."""
import csv, os, sys
import numpy as np
sys.argv = [sys.argv[0]]
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round70_filings_lit/M8"
CELLS = [(5, 5), (5, 60), (30, 5), (30, 60)]
ev = {e["acc"]: e for e in csv.DictReader(open(os.path.join(D, "events.csv")))}
C = list(csv.DictReader(open(os.path.join(D, "controls.csv"))))
cache = {}


def load(day):
    if day not in cache:
        z = np.load(os.path.join(D, "npz", f"BTCUSDT_{day}.npz")); cache[day] = {k: z[k] for k in z.files}
    return cache[day]


def gross(T, d, H):
    day = str(np.datetime64(T, "ms"))[:10]; z = load(day); t, p = z["t"], z["p"]
    i = np.searchsorted(t, T + d * 1000); j = np.searchsorted(t, t[i] + H * 60000)
    return (p[j] / p[i] - 1) * 1e4


def cl_t(x, g):
    x = np.asarray(x, float); mu = x.mean(); G = np.unique(g)
    s = np.array([(x[np.asarray(g) == k] - mu).sum() for k in G]); n = len(x)
    return mu / np.sqrt((s ** 2).sum() / n ** 2 * len(G) / (len(G) - 1))


L = ["# Post-hoc control (addendum A1): same UTC clock time 7 / 14 days earlier, gross bp (long)"]
for d, H in CELLS:
    for era, ok in (("IS", lambda y: y <= 2021), ("VAL", lambda y: y >= 2022)):
        cc = [c for c in C if ok(int(c["day"][:4]))]
        g = [gross(int(c["T_ms"]), d, H) for c in cc]
        ee = [e for e in ev.values() if e["cls"] == "FRESH" and ok(int(e["acc_utc"][:4]))]
        ge = [gross(int(e["T_ms"]), d, H) for e in ee]
        L.append(f"D{d}-{H}m {era}: event gross {np.mean(ge):.1f} (n {len(ge)}, t {cl_t(ge, [e['acc_utc'][:10] for e in ee]):.2f}) | "
                 f"control gross {np.mean(g):.1f} (n {len(g)}, t {cl_t(g, [c['day'] for c in cc]):.2f}, med {np.median(g):.1f})")
# path of controls in VAL MSTR vs events
OFFS = [0, 60, 120, 300, 600, 1800, 3600]
for lab, ok in (("IS", lambda y: y <= 2021), ("VAL", lambda y: y >= 2022), ("2024 MSTR", None)):
    if ok is None:
        cc = [c for c in C if c["day"][:4] == "2024" and c["tk"] == "MSTR"]
    else:
        cc = [c for c in C if ok(int(c["day"][:4]))]
    A = []
    for c in cc:
        T = int(c["T_ms"]); z = load(str(np.datetime64(T, "ms"))[:10]); t, p = z["t"], z["p"]
        r = p[np.searchsorted(t, T, side="right") - 1]
        A.append([(p[np.searchsorted(t, T + o * 1000, side="right") - 1] / r - 1) * 1e4 for o in OFFS])
    A = np.array(A)
    L.append(f"control path {lab} n {len(A)} vs T, offsets {OFFS}: mean {np.round(A.mean(0),1).tolist()} median {np.round(np.median(A,0),1).tolist()}")
open(os.path.join(OUT, "control.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
