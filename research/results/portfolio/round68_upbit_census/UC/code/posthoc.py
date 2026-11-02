"""POST-HOC, descriptive only (labelled so in STREAM_UC.md): the long-alt / short-BTC version of the frozen trade on
every coin-named category (DWSUSP flipped), from trades.csv. Not a rule: the side was chosen after seeing the paths."""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import clt
UC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R = list(csv.DictReader(open(os.path.join(UC, "trades.csv"))))
out = open(os.path.join(UC, "posthoc.txt"), "w")
P = lambda *a: (print(*a), print(*a, file=out))
P("POST-HOC long alt / short BTC, D5 entry, net bp (20 bp + slip + funding), t clustered by day")
groups = {c: [c] for c in sorted(set(r["cat"] for r in R))}
groups["POOL (all coin-named, excl. LISTING)"] = list(set(r["cat"] for r in R))
groups["POOL excl. WARN"] = [c for c in set(r["cat"] for r in R) if c != "WARN"]
for g, cs in groups.items():
    for xn in ("5m", "60m"):
        for era in ("IS", "VAL"):
            S = [r for r in R if r["cat"] in cs and r["era"] == era and r[f"D5-{xn}_net"] != ""]
            if len(S) < 3:
                continue
            sg = np.array([-1.0 if r["side"] == "-1" else 1.0 for r in S])
            gross = sg * np.array([float(r[f"D5-{xn}_gross"]) for r in S]); fund = sg * np.array([float(r[f"D5-{xn}_fund"]) for r in S])
            slip = np.array([float(r[f"D5-{xn}_slip"]) for r in S])
            net = gross + fund - 20 - slip
            m, t, n = clt(net, [r["day"] for r in S])
            yrs = {}
            for r, v in zip(S, net):
                yrs.setdefault(r["day"][:4], []).append(v)
            ys = " ".join(f"{y}:{np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
            P(f"{g[:36]:36s} {xn:3s} {era:3s} n {n:3d} days {len(set(r['day'] for r in S)):3d} gross {gross.mean():6.1f} net {m:6.1f} t {t:5.2f} median {np.median(net):6.1f} SR {net.mean()/net.std(ddof=1):5.2f}  {ys}")
