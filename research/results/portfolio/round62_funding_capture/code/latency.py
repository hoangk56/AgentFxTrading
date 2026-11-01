"""Round 62 P1 latency check on 1m klines: entry at the open of minute T+m, exit at the close of minute T+59."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, capture as K
END = int(sys.argv[2]) if len(sys.argv) > 2 else 1735689599999
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
rows = []
for s in syms:
    p = os.path.join(K.B, "perp_1m_stamps", f"{s}_{END}.csv")
    if not os.path.exists(p):
        continue
    m = {}
    for r in list(csv.reader(open(p)))[1:]:
        T, t = int(float(r[0])), int(float(r[1]))
        m.setdefault(T, {})[(t - T) // 60000] = (float(r[2]), float(r[3]))
    for e in K.events(s, END, 0.003):
        bars = m.get(e["T"])
        if not bars or 59 not in bars:
            continue
        payer = -e["side"]
        rec = dict(T=e["T"], fp=e["fp"], p1h=e["p1"])
        for mm in (0, 1, 2, 5, 10):
            if mm in bars:
                rec[mm] = payer * (bars[59][1] / bars[mm][0] - 1) - e["cost"]
        rec["first_min"] = payer * (bars[0][1] / bars[0][0] - 1) if 0 in bars else np.nan
        rows.append(rec)
for er, (a, b) in K.ERAS.items():
    X = [r for r in rows if a <= r["T"] < b]
    if not X:
        continue
    print(er, "n", len(X), "1h-bar P1 %+.1f bp" % (1e4 * np.mean([r["p1h"] for r in X])))
    for mm in (0, 1, 2, 5, 10):
        v = np.array([r[mm] for r in X if mm in r])
        t = K.cluster_t(v, [r["T"] // 86400000 for r in X if mm in r])
        print("   entry T+%2d min: %+.1f bp (t_cl %.2f, n %d)" % (mm, 1e4 * v.mean(), t, len(v)))
    print("   first minute payer move %+.1f bp" % (1e4 * np.nanmean([r["first_min"] for r in X])))
