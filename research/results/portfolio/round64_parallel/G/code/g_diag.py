"""Stream G diagnostics (information only, no new cells): where the catch-up happens. For laggards, the shock-minute
residual, the hedged move inside e+1 (not tradable: it is the bar we wait for), and the hedged gross after entry;
laggards minus leaders (gross, hedged). Per-shock means, IS / VAL. Writes out/diag.txt."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g_report as G  # noqa: E402

BP = 1e4


def main():
    z = dict(np.load(os.path.join(G.OUT, "g_rows.npz")))
    L = []
    for xi, xn in enumerate(G.XN):
        e = z[f"s{xi}_e"]; ns = len(e); era = (e >= G.VAL0).astype(int)
        day = (G.T0 + e * G.MIN) // G.DAY
        isx = z["x"] == xi
        j = z["j"]; sd = z[f"s{xi}_side"][np.where(isx, j, 0)]
        b = z["beta"]; rb = z[f"s{xi}_rb"][np.where(isx, j, 0)]
        u = sd * (z["ra"] - b * rb)                       # signed residual at e (negative = lagged)
        # BTC move inside e+1 approximated by c[e+1] / o[e+1] (o[e+1] ~ c[e]); from stored legs
        bm1 = (1 + z[f"s{xi}_bgo0"]) / (1 + z[f"s{xi}_bg0"]) - 1
        hm1 = sd * (z["m1"] - b * bm1[np.where(isx, j, 0)])
        for grp, gm in (("laggards", isx & z["lag"]), ("leaders", isx & z["lead"]), ("all", isx)):
            for en in (0, 1):
                parts = []
                for lab, w in [("resid_e", u), ("hedged_e+1", hm1)] + [
                        (f"hedged_H{H}", sd * (z["g"][:, k] - b * z[f"s{xi}_bg{k}"][np.where(isx, j, 0)]))
                        for k, H in enumerate(G.HS)]:
                    sel = np.where(gm & np.isfinite(w))[0]
                    sm, _ = G.shock_mean(w[sel], j[sel], ns)
                    m = (era == en) & np.isfinite(sm)
                    x = G.clt(sm[m], day[m])
                    parts.append(f"{lab} {x[0] * BP:+.1f} (t {x[1]:+.2f})")
                L.append(f"{xn} {grp:8s} {'IS ' if en == 0 else 'VAL'} | " + " | ".join(parts))
        # laggards minus leaders, hedged gross per shock (both legs exist)
        for k, H in enumerate(G.HS):
            w = sd * (z["g"][:, k] - b * z[f"s{xi}_bg{k}"][np.where(isx, j, 0)])
            a = np.where(isx & z["lag"] & np.isfinite(w))[0]; c = np.where(isx & z["lead"] & np.isfinite(w))[0]
            ma, _ = G.shock_mean(w[a], j[a], ns); mc, _ = G.shock_mean(w[c], j[c], ns)
            d = ma - mc
            for en in (0, 1):
                m = (era == en) & np.isfinite(d)
                x = G.clt(d[m], day[m])
                L.append(f"{xn} lag-minus-lead hedged gross H{H} {'IS ' if en == 0 else 'VAL'}: {x[0] * BP:+.1f} bp "
                         f"(t {x[1]:+.2f}, n {x[3]})")
    open(os.path.join(G.OUT, "diag.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
