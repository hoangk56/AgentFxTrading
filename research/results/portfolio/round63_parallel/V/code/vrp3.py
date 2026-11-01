"""Stream V, V3 (declared in the 14:41 UTC addendum): short delta-hedged ~25-delta strangle. Reuses vrp.py.
Run: python -I vrp3.py <BTC|ETH>  -> V/out/sims3_<cur>.pkl"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vrp
from vrp import H, DAY, bs

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")


def leg_iv(P, S, K, tau, cp):
    lo, hi = 0.01, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if float(bs(S, K, tau, mid, cp)[0]) > P:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def strangle_quote(m, f0, tenor, late=False):
    w0 = f0 + (9 if late else 8) * H
    t_ref = w0 + H // 2
    tr = m.tr
    a, b = np.searchsorted(tr["ts"], [w0, w0 + H])
    if b - a < 5:
        return None
    sl = slice(a, b)
    ts, ex, kk, cp = tr["ts"][sl], tr["exp"][sl], tr["k"][sl], tr["cp"][sl]
    px, mk, iv, ix = tr["px"][sl], tr["mark"][sl], tr["iv"][sl], tr["idx"][sl]
    S0 = ix[np.argmin(np.abs(ts - t_ref))]
    exps = np.unique(ex[ex > t_ref + DAY])
    if tenor == 7:
        T = f0 + 7 * DAY + 8 * H
        if T not in exps:
            return None
    else:
        days = (exps - (f0 + 8 * H)) / DAY
        ok = (days >= 21) & (days <= 35)
        if not ok.any():
            return None
        T = int(exps[ok][np.argmin(np.abs(days[ok] - 28))])
    tau0 = (T - t_ref) / DAY / 365.0
    me = ex == T
    near = me & (np.abs(np.log(kk / S0)) < 0.25) & np.isfinite(mk) & (mk > 0)
    hs = float(np.median(np.abs(px[near] - mk[near]) / mk[near])) if near.sum() >= 3 else np.nan
    legs = {}
    route = []
    for c, target in ((1, 0.25), (-1, -0.25)):
        mc = me & (cp == c) & np.isfinite(iv) & (iv > 0)
        if not mc.any():
            return None
        Ks = np.unique(kk[mc])
        best, bd = None, 9
        for K in Ks:
            sg = np.median(iv[mc & (kk == K)]) / 100.0
            d = float(bs(S0, K, tau0, sg, c)[1])
            if abs(d - target) < bd:
                bd, best = abs(d - target), (K, sg, d)
        K, sg, d = best
        if abs(d - target) > 0.12:
            return None
        ml = mc & (kk == K) & np.isfinite(mk)
        idxs = np.where(ml)[0]
        q = idxs[np.argmin(np.abs(ts[idxs] - t_ref))]
        _, dl = bs(ix[q], K, (T - ts[q]) / DAY / 365.0, iv[q] / 100.0, c)
        Pl = mk[q] * ix[q] + float(dl) * (S0 - ix[q])
        legs[c] = (K, max(Pl, 1e-6), leg_iv(max(Pl, 1e-6), S0, K, tau0, c), float(d))
        route.append("mark")
    return dict(f0=f0, t_ref=t_ref, T=T, S0=S0, Kc=legs[1][0], Kp=legs[-1][0], Pc=legs[1][1], Pp=legs[-1][1],
                P=legs[1][1] + legs[-1][1], sigc=legs[1][2], sigp=legs[-1][2], dc=legs[1][3], dp=legs[-1][3], hs=hs,
                route=route, dvol=m.dvol_at(w0))


def simulate2(m, q, hedge_h, cost_mult=1.0, lag=0, hs_default=0.05):
    S0, T, Kc, Kp = q["S0"], q["T"], q["Kc"], q["Kp"]
    hs = q["hs"] if np.isfinite(q["hs"]) else hs_default
    h0 = (q["t_ref"] // H + 1) * H
    hours = np.arange(h0, T + 1, H, dtype=np.int64)
    S = np.array([m.px(t) for t in hours])
    dv0 = q["dvol"]
    fee = sum(min(0.0003 * S0, 0.125 * leg) for leg in (q["Pc"], q["Pp"]))
    cash = q["P"] * (1 - hs * cost_mult) - fee * cost_mult
    n = len(hours)
    pos = np.zeros(n)
    scale = np.array([m.dvol_at(t) / dv0 for t in hours])
    cur, traded = 0.0, 0.0
    for i in range(n - 1):
        r = i - lag
        if r >= 0 and r % hedge_h == 0:
            tau = (T - hours[r]) / DAY / 365.0
            dlt = float(bs(S[r], Kc, tau, q["sigc"] * scale[r], 1)[1] + bs(S[r], Kp, tau, q["sigp"] * scale[r], -1)[1])
            traded += abs(dlt - cur) * S[i]
            cash -= 0.0005 * abs(dlt - cur) * S[i] * cost_mult
            cur = dlt
        pos[i] = cur
    cash -= 0.0005 * abs(cur) * S[-1] * cost_mult
    traded += abs(cur) * S[-1]
    hedge = np.concatenate([[0.0], np.cumsum(pos[:-1] * np.diff(S))])
    fund = np.zeros(n)
    fi = np.searchsorted(m.ft, [h0 + 1, T])
    for j in range(fi[0], fi[1]):
        k = int((m.ft[j] - h0) // H)
        if 1 <= k < n:
            fund[k:] += -pos[k - 1] * m.fr[j] * S[k]
    tau = (T - hours[:-1]) / DAY / 365.0
    V = bs(S[:-1], Kc, tau, q["sigc"] * scale[:-1], 1)[0] + bs(S[:-1], Kp, tau, q["sigp"] * scale[:-1], -1)[0]
    ic, ip = max(S[-1] - Kc, 0.0), max(Kp - S[-1], 0.0)
    V = np.append(V, ic + ip)
    dfee = sum(min(0.00015 * S[-1], 0.125 * x) for x in (ic, ip) if x > 0)
    path = cash - V + hedge + fund
    path[-1] -= dfee * cost_mult
    need = 0.15 * S + V - path
    return dict(hours=hours, path=path, final=path[-1], prem=q["P"] * (1 - hs), P=q["P"], intr=ic + ip, hedge=hedge[-1],
                fund=fund[-1], traded=traded, fee=fee, S0=S0, T=T, cap=0.5 * S0, need_max=float(need.max()) / S0,
                mtm_min=float(path.min()) / (0.5 * S0))


def main(cur):
    m = vrp.Mkt(cur)
    weeks = [f for f in vrp.fridays("2021-03-26", "2024-12-31") if f + 8 * H + 7 * DAY <= vrp.CUT]
    res = {"weeks": weeks}
    IS0, VAL1 = vrp.ms(vrp.IS_A), vrp.ms(vrp.VAL_B)
    for tenor in (7, 30):
        for var in ("base", "cost15", "late"):
            sims = []
            for f0 in vrp.fridays("2021-03-26", "2024-12-31"):
                q = strangle_quote(m, f0, tenor, var == "late")
                if q is None or not np.isfinite(q["dvol"]) or q["T"] >= vrp.CUT or not (IS0 <= f0 < VAL1):
                    continue
                s = simulate2(m, q, 24, 1.5 if var == "cost15" else 1.0, 1 if var == "late" else 0)
                s.update(f0=f0, route=q["route"], hs=q["hs"], dvol=q["dvol"], dc=q["dc"], dp=q["dp"],
                         rv30=m.rv30(f0 + 8 * H), sigc=q["sigc"], sigp=q["sigp"])
                days = (s["T"] - q["t_ref"]) / DAY
                s["ex"] = (s["final"] - s["cap"] * m.cash(q["t_ref"]) * days / 360) / s["cap"]
                sims.append(s)
            P, C = vrp.book(m, sims, weeks)
            for s in sims:
                del s["hours"]
                s["path"] = s["path"][::24].astype(np.float32)
            res[(tenor, 24, var)] = dict(sims=sims, P=P.astype(np.float32), C=C.astype(np.float32))
            print(cur, tenor, var, len(sims), flush=True)
    # descriptive: DVOL vs realised vol of the following 30 days, Fridays 08:00
    desc = []
    for f0 in weeks:
        t = f0 + 8 * H
        if t + 30 * DAY >= vrp.CUT or t - 31 * DAY < m.pt[0]:
            continue
        i = m.pos[int(t)]
        r = np.diff(np.log(m.po[i:i + 721]))
        desc.append((f0, m.dvol_at(t), np.sqrt(np.mean(r * r) * 24 * 365), m.rv30(t)))
    res["desc"] = desc
    os.makedirs(OUT, exist_ok=True)
    pickle.dump(res, open(f"{OUT}/sims3_{cur}.pkl", "wb"))


if __name__ == "__main__":
    main(sys.argv[1])
