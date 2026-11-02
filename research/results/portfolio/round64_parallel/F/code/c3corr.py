"""Stream F: daily P&L correlation of a cell with C3 (IS / VAL rows only). Usage: c3corr.py "T5 idio H15"."""
import csv, os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import report as Rp  # noqa
OUT = os.path.join(HERE, "..", "out")
C3 = os.path.join(HERE, "..", "..", "..", "trades_C3_gotobi_jpy_basket.csv")


def main(cell):
    tn, fn, Hs = cell.split(); k = Rp.HS.index(int(Hs[1:]))
    z = np.load(os.path.join(OUT, "cand.npz")); syms = list(z["syms"])
    sym, t, r, rb, sig, rank, g, f = z["sym"], z["t"].astype(np.int64), z["r"], z["rb"], z["sig"], z["rank"], z["g"], z["f"]
    ib, ie = syms.index("BTCUSDT"), syms.index("ETHUSDT")
    h = np.where((sym == ib) | (sym == ie), 1.0, np.where(rank < 20, 3.0, 5.0)) / 1e4
    a = np.abs(r)
    with np.errstate(invalid="ignore"):
        th = {"T3": a >= 0.03, "T5": a >= 0.05, "TZ": (a >= 0.01) & (a >= 10 * np.nan_to_num(sig, nan=np.inf))}[tn]
        fi = ((sym != ib) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)) if fn == "idio" else np.ones(len(t), bool)
    idx = np.where(th & fi)[0]; idx = idx[Rp.dedup(sym[idx], t[idx])]; idx = idx[np.isfinite(g[idx, k])]
    net = g[idx, k] - f[idx, k] - 10e-4 - 4 * h[idx]
    day = (Rp.T0 + t[idx] * Rp.MIN) // Rp.DAY
    F = {}
    for d, x in zip(day, net): F[d] = F.get(d, 0) + x
    C = {}
    for row in csv.DictReader(open(C3)):
        if row["era"] not in ("IS", "VAL"): continue
        d = int(dt.datetime.strptime(row["t_out_utc"][:10], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() // 86400)
        if d * 86400000 >= 1735689600000: continue
        C[d] = C.get(d, 0) + float(row["r"])
    lo, hi = 18262, (1735689600000 // 86400000)
    days = np.arange(lo, hi)
    days = days[[dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).weekday() < 5 for d in days]]
    x = np.array([F.get(d, 0) for d in days]); y = np.array([C.get(d, 0) for d in days])
    for nm, m in (("IS", days < 18993), ("VAL", days >= 18993)):
        print(cell, nm, "corr", round(float(np.corrcoef(x[m], y[m])[0, 1]), 3), "days", int(m.sum()))


if __name__ == "__main__":
    main(sys.argv[1])
