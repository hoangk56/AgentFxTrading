"""Margin series -> declared signals (no prices here)."""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r40/C")
import numpy as np
import lib


def series():
    R = lib.load_margin()
    D = [r["date"] for r in R]
    f = lambda k: np.array([np.nan if r[k] is None else float(r[k]) for r in R])
    rzye, zdf, rqjmg, rqyl, ltsz, rqye = f("RZYE"), f("ZDF"), f("RQJMG"), f("RQYL"), f("LTSZ"), f("RQYE")
    g = np.r_[np.nan, rzye[1:] / rzye[:-1] - 1]          # daily change of the financing balance
    nq = np.r_[np.nan, rqjmg[1:] / rqyl[:-1]]             # net short selling (shares) / prior short shares
    g5 = np.full(len(g), np.nan)
    g5[5:] = rzye[5:] / rzye[:-5] - 1                      # 5-day financing growth
    return dict(D=D, g=g, zdf=zdf, nq=nq, g5=g5, rzye=rzye, rqye=rqye, ltsz=ltsz)


def tz(x, w, minobs=None):
    """z of x[t] vs x[t-w..t-1] (trailing, excluding t)."""
    minobs = minobs or int(0.8 * w)
    z = np.full(len(x), np.nan)
    for t in range(w, len(x)):
        y = x[t - w:t]
        y = y[np.isfinite(y)]
        if len(y) >= minobs and np.isfinite(x[t]) and y.std(ddof=1) > 0:
            z[t] = (x[t] - y.mean()) / y.std(ddof=1)
    return z


# declared cells (HYPOTHESES_C.md): name -> function(series) -> {date: side_of_risk}; side_of_risk -1 = risk-off
def signals():
    s = series()
    D = s["D"]
    zg = tz(s["g"], 60)
    zg5 = tz(s["g5"], 250)
    zn = tz(s["nq"], 60)
    out = {}
    for k in (1.5, 2.0):
        out[f"C1_k{k}"] = {D[i]: -1 for i in range(len(D)) if s["zdf"][i] < 0 and zg[i] <= -k}
    out["C2a_k2"] = {D[i]: -1 for i in range(len(D)) if zg[i] >= 2.0}
    out["C2b_k2"] = {D[i]: -1 for i in range(len(D)) if zg5[i] >= 2.0}
    out["C3_k2"] = {D[i]: (-1 if zn[i] > 0 else 1) for i in range(len(D)) if np.isfinite(zn[i]) and abs(zn[i]) >= 2.0}
    return out, D, dict(zg=zg, zg5=zg5, zn=zn)


def episodes(dates, D, gap=5):
    """episode id per signal date: a new episode when > gap CN days after the previous signal."""
    idx = {d: i for i, d in enumerate(D)}
    ep, last, e = {}, None, -1
    for d in sorted(dates):
        i = idx[d]
        if last is None or i - last > gap:
            e += 1
        ep[d] = e
        last = i
    return ep
