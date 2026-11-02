"""Coordinator HOLD core for PREREG A2-D5L. Uses stream A2's analyze.py (trade, slip, fund, clt, after) and a verbatim
copy of checks.py's fill() / trade() (checks.py runs its analysis at import, so it cannot be imported). Only the data
folders and the request log are redirected; rule logic is unchanged."""
import os, sys
import numpy as np
A2C = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2/code"
sys.path.insert(0, A2C)
import net
import analyze as Z
HD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_hold_a2"
os.makedirs(HD, exist_ok=True)
net.LOG = open(os.path.join(HD, "requests.log"), "a", buffering=1)


def use_npz(path):
    Z.NPZ = path
    Z._C.clear()


def fill(S, T, side, mode):  # verbatim copy of A2/code/checks.py fill()
    t, p, m = S["t"], S["p"], S["m"]
    i = np.searchsorted(t, T, "left")
    if mode == 0:
        return p[i], int(t[i])
    if mode == 1:
        want = 0 if side > 0 else 1
        j = i + np.argmax(m[i:i + 200000] == want)
        return p[j], int(t[j])
    j = np.searchsorted(t, T + 1000, "left")
    q = p[i:max(j, i + 1)]
    return (q.max() if side > 0 else q.min()), int(t[i])


def trade_mode(e, d, X, A, B, mode):  # verbatim copy of A2/code/checks.py trade()
    N = e["N"]; T = N + d * 1000
    ae, tae = fill(A, T, +1, mode); be, tbe = fill(B, T, -1, mode)
    ax, tax = fill(A, X, -1, mode); bx, tbx = fill(B, X, +1, mode)
    sl = Z.slip(A, tae) + Z.slip(A, tax) + Z.slip(B, tbe) + Z.slip(B, tbx)
    g = (ax / ae - 1) - (bx / be - 1)
    f = -Z.fund(e["perp"], tae, tax) + Z.fund("BTCUSDT", tbe, tbx)
    return g + f - Z.COST - sl


def grade(E, label):
    rows = []
    for e in E:
        A = Z.load(e["perp"], e["day"]); B = Z.load("BTCUSDT", e["day"])
        r = Z.trade(e, 5, e["L"], A, B)
        if r is None:
            print("no fill", e["coin"], e["day"]); continue
        r15 = Z.trade(e, 5, e["L"], A, B, costmul=1.5)
        rl = Z.trade(e, 10, e["L"], A, B)
        rows.append(dict(e=e, net=r["net"], x15=r15["net"], late=rl["net"] if rl else np.nan,
                         f1=trade_mode(e, 5, e["L"], A, B, 1), f2=trade_mode(e, 5, e["L"], A, B, 2)))
    day = np.array([x["e"]["day"] for x in rows])
    out = {}
    for k in ("net", "x15", "late", "f1", "f2"):
        v = np.array([x[k] for x in rows]); ok = np.isfinite(v)
        m, t, n = Z.clt(v[ok], day[ok]); out[k] = (m * 1e4, t, n)
    v = np.array([x["net"] for x in rows])
    print(f"{label} D5-L n {out['net'][2]} (days {len(set(day))}) net {out['net'][0]:+.1f} bp t {out['net'][1]:.2f} "
          f"median {np.median(v)*1e4:+.1f} | x1.5 {out['x15'][0]:+.1f} | d10 {out['late'][0]:+.1f} | "
          f"aggressor {out['f1'][0]:+.1f} (t {out['f1'][1]:.2f}) | worst-of-1s {out['f2'][0]:+.1f} (t {out['f2'][1]:.2f})")
    yrs = sorted({x["e"]["year"] for x in rows})
    print("   years:", {y: round(float(np.mean([x["net"] for x in rows if x["e"]["year"] == y])) * 1e4, 1) for y in yrs})
    return out, rows
