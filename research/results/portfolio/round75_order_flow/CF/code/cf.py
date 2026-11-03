"""Round 75 stream CF: C3 (5m aggressive delta) and C4 (1m CVD divergence) at prior-day POC / VAH / VAL.
Rules: CF/HYPOTHESES_CF.md (written before any return). One symbol per process:
    research/.venv/bin/python -I cf.py <SYM> [n_draws]
Writes CF/out/<SYM>_real.npz (every trade of every cell, base and one-step-late) and CF/out/<SYM>_rand.npz
(per-day net sums / counts of every random draw and cell)."""
import importlib.util
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.dirname(HERE)
OUT = os.path.join(CF, "out")
_spec = importlib.util.spec_from_file_location("fp", os.path.join(CF, "..", "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

DAY0 = 18262  # 2020-01-01 in epoch days
NDAYS = 1827  # 2020-01-01 .. 2024-12-31
HOLD_MS = 1735689600000
SLIP = {"BTCUSDT": 1e-4, "ETHUSDT": 1e-4, "SOLUSDT": 2e-4}
MAKER, TAKER = 2.0, 5.0
STOP_ATR = 0.15
CONF = ("C3_0.2", "C3_0.4", "C4", "none")
TPS = ("TPV", "2R")
CELLS = [(c, t) for c in CONF for t in TPS]
INFO = [("nonemkt", "TPV"), ("nonemkt", "2R")]


def load_funding(sym):
    t, r = [], []
    with open(os.path.join(fp.ROOT, "research", "data", "binance", "funding", f"{sym}.csv")) as fh:
        next(fh)
        for line in fh:
            a, b = line.strip().split(",")
            ti = int(a)
            if ti >= HOLD_MS:  # HOLD rows are skipped unread
                continue
            t.append(ti)
            r.append(float(b))
    t, r = np.array(t, np.int64), np.array(r)
    o = np.argsort(t)
    return t[o], np.r_[0.0, np.cumsum(r[o])]


def load_daily_atr(sym, d0, D):
    """ATR14 per dense day index from perp_1d daily klines (rows with t >= 2025-01-01 are skipped unread)."""
    days, hh, ll, cc = [], [], [], []
    with open(os.path.join(fp.ROOT, "research", "data", "binance", "perp_1d", f"{sym}.csv")) as fh:
        next(fh)
        for line in fh:
            a = line.split(",", 1)[0]
            if int(a) >= HOLD_MS:
                continue
            x = line.strip().split(",")
            days.append(int(a) // 86400000)
            hh.append(float(x[2]))
            ll.append(float(x[3]))
            cc.append(float(x[4]))
    days, hh, ll, cc = map(np.array, (days, hh, ll, cc))
    o = np.argsort(days)
    days, hh, ll, cc = days[o], hh[o], ll[o], cc[o]
    cp = np.r_[np.nan, cc[:-1]]
    tr = np.where(np.isfinite(cp), np.maximum(hh, cp) - np.minimum(ll, cp), hh - ll)
    contiguous = np.r_[False, np.diff(days) == 1]
    tr = np.where(contiguous | (np.arange(len(tr)) == 0), tr, np.nan)
    atr = np.full(D, np.nan)
    pos = {int(d): i for i, d in enumerate(days)}
    for di in range(D):
        i = pos.get(d0 + di)
        if i is None or i < 14:
            continue
        w = tr[i - 14:i]
        if np.all(np.isfinite(w)) and days[i] - days[i - 14] == 14:
            atr[di] = w.mean()
    return atr


def prep(sym):
    m = fp.load_minutes(sym)
    mn = m["min"]
    d0 = int(mn[0] // 1440)
    M0 = d0 * 1440
    D = int(mn[-1] // 1440 + 1 - d0)
    N = D * 1440
    idx = mn - M0
    have = np.zeros(N, bool)
    have[idx] = True
    pos = np.where(have, np.arange(N), 0)
    pos = np.maximum.accumulate(pos)  # last minute with a trade
    c = np.zeros(N)
    c[idx] = m["c"]
    c = c[pos]
    prevc = np.r_[c[0], c[:-1]]
    o = prevc.copy()
    h = c.copy()
    lo = c.copy()
    o[idx], h[idx], lo[idx] = m["o"], m["h"], m["l"]
    vb = np.zeros(N)
    vs = np.zeros(N)
    vb[idx], vs[idx] = m["vb"], m["vs"]
    del m
    atr = load_daily_atr(sym, d0, D)
    # holes: runs of > 30 missing minutes (Binance monthly files skip days); also the dense tail past the last trade
    hole = np.zeros(N, bool)
    gaps = np.flatnonzero(np.diff(idx) > 31)
    for g in gaps:
        hole[idx[g] + 1:idx[g + 1]] = True
    if N - 1 - idx[-1] > 30:
        hole[idx[-1] + 1:] = True
    if idx[0] > 30:
        hole[:idx[0]] = True
    hole_day = hole.reshape(D, 1440).any(1)
    hole_cs = np.r_[0, np.cumsum(hole)]
    n_holes = int(len(gaps))

    f = fp.load_fp(sym, 30)
    k = f["k"]
    pb, pr = fp.poc(f)
    day = f["bar"] // 1440 - d0
    vol = f["bid"] + f["ask"]
    key = day * 10_000_000 + f["row"]
    uk, inv = np.unique(key, return_inverse=True)
    uv = np.bincount(inv, weights=vol)
    ud, ur = uk // 10_000_000, uk % 10_000_000
    del f, key, inv, vol, day
    # levels for day d come from the profile of day d - 1
    lev = np.full((D, 3), -1, np.int64)  # POC, VAH, VAL rows
    rng_lo = np.full(D, -1, np.int64)
    rng_hi = np.full(D, -1, np.int64)
    starts = np.r_[np.flatnonzero(np.r_[True, np.diff(ud) != 0]), len(ud)]
    for s, e in zip(starts[:-1], starts[1:]):
        dd = int(ud[s])
        if dd + 1 >= D or dd < 0:
            continue
        r, v = ur[s:e], uv[s:e]
        rmin = int(r.min())
        n = int(r.max()) - rmin + 1
        vv = np.zeros(n)
        vv[r - rmin] = v
        p = int(np.argmax(vv))
        target, up, dn, cum = 0.7 * vv.sum(), p, p, vv[p]
        while cum < target:
            a = vv[up + 1] if up + 1 < n else -1.0
            b = vv[dn - 1] if dn - 1 >= 0 else -1.0
            if a >= b:
                up += 1
                cum += a
            else:
                dn -= 1
                cum += b
        if hole_day[dd] or hole_day[dd + 1]:
            continue  # day d-1 or d has a hole > 30 min: no levels for day d
        lev[dd + 1] = (rmin + p, rmin + up, rmin + dn)
        rng_lo[dd + 1], rng_hi[dd + 1] = rmin, rmin + n - 1
    ft, fcs = load_funding(sym)
    d5 = (vb - vs).reshape(-1, 5).sum(1)
    v5 = (vb + vs).reshape(-1, 5).sum(1)
    delta = vb - vs
    cvd = np.r_[0.0, np.cumsum(delta)]  # cvd[i + 1] = sum of delta[0..i]
    # fractal-2 swings (known at the close of j + 2)
    swl = np.zeros(N, bool)
    swh = np.zeros(N, bool)
    swl[2:-2] = ((lo[2:-2] < lo[1:-3]) & (lo[2:-2] < lo[:-4]) & (lo[2:-2] <= lo[3:-1]) & (lo[2:-2] <= lo[4:]))
    swh[2:-2] = ((h[2:-2] > h[1:-3]) & (h[2:-2] > h[:-4]) & (h[2:-2] >= h[3:-1]) & (h[2:-2] >= h[4:]))
    return dict(sym=sym, d0=d0, M0=M0, D=D, N=N, o=o, h=h, l=lo, c=c, prevc=prevc, atr=atr, k=k,
                pb=(pb - M0).astype(np.int64), pr=pr.astype(np.int64), lev=lev, rng_lo=rng_lo, rng_hi=rng_hi,
                ft=ft, fcs=fcs, hole_cs=hole_cs, n_holes=n_holes, hole_min=int(hole.sum()), d5=d5, v5=v5, cvd=cvd, swl=swl, swh=swh, slip=SLIP[sym])


def find_tests(P, rows):
    """rows: (D, L) level rows for each day (-1 = none). Returns tests sorted by minute: t, side, lo, hi."""
    D, k = P["D"], P["k"]
    lo = fp.row_price(rows, k, "low")
    hi = fp.row_price(rows, k, "high")
    ok = rows >= 0
    Lx = np.minimum(P["l"], P["prevc"]).reshape(D, 1440)
    Hx = np.maximum(P["h"], P["prevc"]).reshape(D, 1440)
    touch = (Lx[:, None, :] <= hi[:, :, None]) & (Hx[:, None, :] >= lo[:, :, None])
    anyt = touch.any(2) & ok
    first = touch.argmax(2)
    dd, jj = np.nonzero(anyt)
    t = dd * 1440 + first[dd, jj]
    lo_, hi_ = lo[dd, jj], hi[dd, jj]
    pc = P["prevc"][t]
    side = np.where(pc > hi_, 1, np.where(pc < lo_, -1, 0))
    keep = side != 0
    o = np.argsort(t[keep], kind="stable")
    return t[keep][o], side[keep][o], lo_[keep][o], hi_[keep][o]


def entries(P, tests, conf, late=False):
    """Entry minute e, kind (0 market at close of e, 1 limit filled during e), price, side."""
    t, side, lo, hi = tests
    N, slip, c = P["N"], P["slip"], P["c"]
    if conf == "none":
        px = np.where(side > 0, hi, lo)
        fill = np.where(side > 0, P["l"][t] <= hi * (1 - 1e-4), P["h"][t] >= lo * (1 + 1e-4))
        t, side, px = t[fill], side[fill], px[fill]
        if late:
            return t, np.zeros(len(t), int), c[t] * (1 + side * slip), side
        return t, np.ones(len(t), int), px, side
    if conf == "nonemkt":
        e = t + (1 if late else 0)
    elif conf.startswith("C3"):
        x = float(conf.split("_")[1])
        b0 = t // 5
        nb = (t + 29) // 5 - b0 + 1  # 6 or 7 bars
        bb = b0[:, None] + np.arange(7)[None, :]
        valid = (np.arange(7)[None, :] < nb[:, None]) & (bb < len(P["d5"]))
        bb = np.minimum(bb, len(P["d5"]) - 1)
        d5, v5 = P["d5"][bb], P["v5"][bb]
        okb = valid & (side[:, None] * d5 > 0) & (np.abs(d5) >= x * v5) & (v5 > 0)
        has = okb.any(1)
        e = (bb[np.arange(len(t)), okb.argmax(1)] * 5 + 4)
        t, side, e = t[has], side[has], e[has]
        if late:
            e = e + 1
    elif conf == "C4":
        good = t >= 30
        t, side = t[good], side[good]
        pre = t[:, None] + np.arange(-30, 0)[None, :]
        post = np.minimum(t[:, None] + np.arange(30)[None, :], N - 1)
        lw, hw = P["l"], P["h"]
        lmin_i = pre[np.arange(len(t)), np.where(side[:, None] > 0, lw[pre], -hw[pre]).argmin(1)]
        ref = np.where(side > 0, lw[lmin_i], hw[lmin_i])
        cv_ref = P["cvd"][lmin_i + 1]
        cv_j = P["cvd"][post + 1]
        long_ok = P["swl"][post] & (lw[post] < ref[:, None]) & (cv_j > cv_ref[:, None])
        short_ok = P["swh"][post] & (hw[post] > ref[:, None]) & (cv_j < cv_ref[:, None])
        okj = np.where(side[:, None] > 0, long_ok, short_ok)
        has = okj.any(1)
        e = post[np.arange(len(t)), okj.argmax(1)] + 2
        t, side, e = t[has], side[has], e[has]
        if late:
            e = e + 1
    else:
        raise ValueError(conf)
    keep = e < N - 1
    e, side = e[keep], side[keep]
    return e, np.zeros(len(e), int), c[e] * (1 + side * slip), side


def tpv(P, T, px, sd, side):
    pb, pr, k = P["pb"], P["pr"], P["k"]
    j = np.searchsorted(pb + 30, T, "right")
    cand = pr[max(0, j - 48):j]
    if side > 0:
        near = fp.row_price(cand, k, "low")
        ok = (near > px + sd) & (near <= px + 3 * sd)
        if ok.any():
            r = cand[ok][np.argmin(near[ok])]
            return float(fp.row_price(r - 1, k, "low"))
        return px + 2 * sd
    near = fp.row_price(cand, k, "high")
    ok = (near < px - sd) & (near >= px - 3 * sd)
    if ok.any():
        r = cand[ok][np.argmax(near[ok])]
        return float(fp.row_price(r + 1, k, "high"))
    return px - 2 * sd


DROPPED = {}


def run(P, ent, tp_mode, tag=None):
    """Sequential trades, one open per symbol. Returns array rows: e, day, side, net, fees, rbp, exit kind."""
    e_all, kind_all, px_all, side_all = ent
    o_, h_, l_, c_ = P["o"], P["h"], P["l"], P["c"]
    N, M0, slip, atr = P["N"], P["M0"], P["slip"], P["atr"]
    ft, fcs = P["ft"], P["fcs"]
    order = np.argsort(e_all, kind="stable")
    out = []
    prev_exit = -1
    for i in order:
        e, kind, px, side = int(e_all[i]), int(kind_all[i]), float(px_all[i]), int(side_all[i])
        if e <= prev_exit:
            continue
        a_tr = atr[e // 1440]
        if not np.isfinite(a_tr):
            continue
        sd = STOP_ATR * a_tr
        stop = px - side * sd
        T = e + 1 if kind == 0 else e
        tp = px + side * 2 * sd if tp_mode == "2R" else tpv(P, T, px, sd, side)
        fee_in = MAKER if kind == 1 else TAKER
        xp = None
        if kind == 1 and ((side > 0 and l_[e] <= stop) or (side < 0 and h_[e] >= stop)):
            xp, xi, xk = stop * (1 - side * slip), e, 0
        if xp is None:
            a = e + 1
            b = min(e + (1439 if kind == 1 else 1440), N - 1)
            if a > b:
                continue
            if side > 0:
                sm = l_[a:b + 1] <= stop
                tm = h_[a:b + 1] > tp
            else:
                sm = h_[a:b + 1] >= stop
                tm = l_[a:b + 1] < tp
            ks = int(sm.argmax()) if sm.any() else 10 ** 9
            kt = int(tm.argmax()) if tm.any() else 10 ** 9
            if ks < 10 ** 9 and ks <= kt:
                op = o_[a + ks]
                fillp = min(op, stop) if side > 0 else max(op, stop)
                xp, xi, xk = fillp * (1 - side * slip), a + ks, 0
            elif kt < 10 ** 9:
                xp, xi, xk = tp, a + kt, 1
            else:
                xp, xi, xk = c_[b] * (1 - side * slip), b, 2
        hc = P["hole_cs"]
        if hc[xi + 1] - hc[max(e - 31, 0)] > 0:  # trade life (or its 30 min confirmation window) spans a hole
            if tag:
                DROPPED[tag] = DROPPED.get(tag, 0) + 1
            continue
        fee_out = MAKER if xk == 1 else TAKER
        t_in = (M0 + e + (1 if kind == 0 else 0)) * 60000 + (0 if kind == 0 else 30000)
        t_out = (M0 + xi + 1) * 60000 if xk == 2 else (M0 + xi) * 60000 + 30000
        fund = fcs[np.searchsorted(ft, t_out, "right")] - fcs[np.searchsorted(ft, t_in, "right")]
        net = side * (xp / px - 1) * 1e4 - fee_in - fee_out - side * fund * 1e4
        out.append((e, P["d0"] + e // 1440 - DAY0, side, net, fee_in + fee_out, sd / px * 1e4, xk))
        prev_exit = xi
    if not out:
        return np.zeros((0, 7))
    return np.array(out, float)


def real(P):
    rows = P["lev"]
    tests = find_tests(P, rows)
    res = {}
    for conf, tpm in CELLS + INFO:
        for late in (False, True):
            ent = entries(P, tests, conf, late)
            tag = f"{conf}|{tpm}|{'late' if late else 'base'}"
            res[tag] = run(P, ent, tpm, tag)
    res["_ntests"] = np.array([len(tests[0])])
    res["_dropped"] = np.array([f"{k}={v}" for k, v in DROPPED.items()])
    res["_holes"] = np.array([P["n_holes"], P["hole_min"], int((P["lev"][:, 0] < 0).sum())])
    return res


def random_draws(P, n_draws, seed):
    rng = np.random.default_rng(seed)
    D = P["D"]
    lev, rlo, rhi = P["lev"], P["rng_lo"], P["rng_hi"]
    valid = (lev[:, 0] >= 0) & (rhi - rlo + 1 > 3)  # lev is -1 on hole days, so random levels skip them too
    sums = np.zeros((n_draws, len(CELLS), NDAYS))
    cnts = np.zeros((n_draws, len(CELLS), NDAYS))
    off = P["d0"] - DAY0
    for g in range(n_draws):
        rows = np.full((D, 3), -1, np.int64)
        r = rng.integers(rlo[:, None], rhi[:, None] + 1, size=(D, 3))
        for _ in range(100):
            bad = valid[:, None] & ((r[:, :, None] == lev[:, None, :]).any(2))
            if not bad.any():
                break
            r2 = rng.integers(rlo[:, None], rhi[:, None] + 1, size=(D, 3))
            r = np.where(bad, r2, r)
        rows[valid] = r[valid]
        tests = find_tests(P, rows)
        ents = {conf: entries(P, tests, conf) for conf in CONF}
        for ci, (conf, tpm) in enumerate(CELLS):
            tr = run(P, ents[conf], tpm)
            if len(tr):
                d = tr[:, 1].astype(int)
                np.add.at(sums[g, ci], d, tr[:, 3])
                np.add.at(cnts[g, ci], d, 1)
        if g % 20 == 0:
            print(f"  draw {g} {time.strftime('%H:%M:%S')}", flush=True)
    return sums, cnts


def main():
    sym = sys.argv[1]
    nd = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    mode = sys.argv[3] if len(sys.argv) > 3 else "all"
    t0 = time.time()
    P = prep(sym)
    print(f"{sym} prep {time.time() - t0:.0f}s D={P['D']} k={P['k']}", flush=True)
    if mode in ("all", "real"):
        res = real(P)
        np.savez(os.path.join(OUT, f"{sym}_real.npz"), **res)
        print(f"{sym} real done {time.time() - t0:.0f}s tests={res['_ntests'][0]} holes(n, min, days w/o levels)="
              f"{list(res['_holes'])} dropped={list(res['_dropped'])}", flush=True)
    if mode in ("all", "rand"):
        sums, cnts = random_draws(P, nd, seed={"BTCUSDT": 751, "ETHUSDT": 752, "SOLUSDT": 753}[sym])
        np.savez(os.path.join(OUT, f"{sym}_rand.npz"), sums=sums, cnts=cnts,
                 cells=np.array([f"{a}|{b}" for a, b in CELLS]))
        print(f"{sym} rand done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
