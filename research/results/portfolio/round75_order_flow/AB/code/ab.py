"""Round 75 stream AB: big limit (C1) and absorption (C2) confirmations at yesterday's Volume Profile levels.

Rules: ../HYPOTHESES_AB.md. Usage (research venv, -I):
    ab.py run SYM [NDRAWS]   -> ../out/<SYM>_real.npz (trades of every cell / variant) + <SYM>_rand.npz (draw day sums)
    ab.py selftest
"""
import importlib.util
import os
import sys
import time

import warnings

import numpy as np

warnings.simplefilter("ignore", RuntimeWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
OUT = os.path.join(HERE, "..", "out")
_spec = importlib.util.spec_from_file_location(
    "fp", os.path.join(ROOT, "research", "results", "portfolio", "round75_order_flow", "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

SLIP = {"BTCUSDT": 1e-4, "ETHUSDT": 1e-4, "SOLUSDT": 2e-4}
MAKER, TAKER = 2.0, 5.0
DAY0 = 18262  # 2020-01-01 in epoch days
NDAYS_ALL = 1827  # 2020-01-01 .. 2024-12-31
RK = 1 << 20  # row key multiplier
WIN = 6  # B0..B5
BON = 3  # bonus: delta bar within the next 3 bars
MS = (4, 8)
CONFS = ("C1", "C2", "BON")
CELLS = [(c, m, tp) for c in CONFS for m in MS for tp in ("TPV", "2R")]  # 12 verdict cells
CTRLS = [("N0", 0, "TPV"), ("N0", 0, "2R"), ("N0m", 0, "TPV"), ("N0m", 0, "2R")]
ALL = CELLS + CTRLS


def cname(c):
    return f"{c[0]}" + (f"_m{c[1]}" if c[1] else "") + f"_{c[2]}"


# ----------------------------------------------------------------------------------------------- data preparation
def ffill_idx(valid):
    i = np.where(valid, np.arange(len(valid)), 0)
    return np.maximum.accumulate(i)


def prepare(sym):
    t_start = time.time()
    m = fp.load_minutes(sym)
    t0 = int(m["min"][0] // 1440 * 1440)
    T = fp.HOLD_MIN - t0
    nd = T // 1440
    ix = (m["min"] - t0).astype(np.int64)
    O, H, L, C = (np.full(T, np.nan) for _ in range(4))
    O[ix], H[ix], L[ix], C[ix] = m["o"], m["h"], m["l"], m["c"]
    del m
    valid = ~np.isnan(C)
    Cf = C[ffill_idx(valid)]
    prevC = np.r_[np.nan, Cf[:-1]]
    # holes: runs of > 30 missing minutes (Binance monthly files skip days)
    miss = np.r_[0, (~valid).astype(np.int64)]
    hcum_all = np.cumsum(miss)  # hcum_all[i] = missing minutes before minute i
    run_start = np.flatnonzero(np.diff(np.r_[1, valid.astype(np.int8)]) == -1)
    run_end = np.flatnonzero(np.diff(np.r_[valid.astype(np.int8), 1]) == 1)
    big = (run_end - run_start + 1) > 30
    hole = np.zeros(T, bool)
    hole_day = np.zeros(nd, bool)
    for a, b in zip(run_start[big], run_end[big]):
        hole[a:b + 1] = True
        hole_day[a // 1440:b // 1440 + 1] = True
    hcum = np.r_[0, np.cumsum(hole)]
    nholes, hole_h = int(big.sum()), float(hole.sum() / 60)
    # daily ATR14 from perp_1d daily klines (rows >= 2025-01-01 cut on load), mean TR of the 14 days before the day
    kz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "perp_1d", f"{sym}.csv"), delimiter=",",
                    skiprows=1)
    kz = kz[kz[:, 0] < fp.HOLD_MIN * 60000.0]
    kd = (kz[:, 0] // 86400000).astype(np.int64) - t0 // 1440
    Hd, Ld, Cd = (np.full(nd, np.nan) for _ in range(3))
    okk = (kd >= 0) & (kd < nd)
    Hd[kd[okk]], Ld[kd[okk]], Cd[kd[okk]] = kz[okk, 2], kz[okk, 3], kz[okk, 4]
    Cp = np.full(nd, np.nan)
    pre = kd < 0
    Cp[0] = kz[pre, 4][-1] if pre.any() else np.nan
    Cp[1:] = Cd[:-1]
    TR = np.nanmax(np.c_[Hd - Ld, np.abs(Hd - Cp), np.abs(Ld - Cp)], axis=1)
    atr = np.full(nd, np.nan)
    TRx = np.r_[np.full(14, np.nan), TR]
    if pre.any():  # the 14 days before the first cache day, from the klines
        kp = kz[pre]
        trp = np.maximum(kp[1:, 2] - kp[1:, 3], np.maximum(np.abs(kp[1:, 2] - kp[:-1, 4]), np.abs(kp[1:, 3] - kp[:-1, 4])))
        trp = trp[-14:]
        TRx[14 - len(trp):14] = trp
    for d in range(nd):
        w = TRx[d:d + 14]
        if np.isfinite(w).sum() >= 10:
            atr[d] = np.nanmean(w)
    # funding (long pays rate at each stamp held)
    fz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "funding", f"{sym}.csv"), delimiter=",",
                    skiprows=1)
    fmin = fz[:, 0] / 60000.0
    keep = fmin < fp.HOLD_MIN
    fmin, frate = fmin[keep], fz[keep, 1]
    fcum = np.r_[0.0, np.cumsum(frate)]
    # 30m footprint: day profiles and per-bar POC
    f30 = fp.load_fp(sym, 30)
    k = f30["k"]
    day = (f30["bar"] - t0) // 1440
    key = day * RK + f30["row"]
    uk, inv = np.unique(key, return_inverse=True)
    vol = np.bincount(inv, weights=f30["bid"] + f30["ask"])
    uday, urow = uk // RK, uk % RK
    nbar_day = np.bincount(np.unique((f30["bar"] - t0) // 30) // 48, minlength=nd)
    prof = np.full((nd, 5), -1, np.int64)  # POC, VAH, VAL, rmin, rmax of that day
    starts = np.r_[np.flatnonzero(np.r_[True, np.diff(uday) != 0]), len(uday)]
    for a, b in zip(starts[:-1], starts[1:]):
        d = uday[a]
        if nbar_day[d] < 40 or hole_day[d]:
            continue
        rows, v = urow[a:b], vol[a:b]
        rmin, rmax = rows[0], rows[-1]
        dense = np.zeros(rmax - rmin + 1)
        dense[rows - rmin] = v
        p, lo, hi = value_area(dense)
        prof[d] = (rmin + p, rmin + hi, rmin + lo, rmin, rmax)
    b30, p30 = fp.poc(f30)
    pocd = np.full(T // 30, -1, np.int64)
    pocd[(b30 - t0) // 30] = p30
    del f30, key, uk, inv, vol, uday, urow, day
    # 5m footprint
    f5 = fp.load_fp(sym, 5)
    assert f5["k"] == k
    key5 = f5["bar"] * RK + f5["row"]
    assert np.all(np.diff(key5) > 0)
    s = f5["ptr"][:-1]
    bi5 = (f5["bar"][s] - t0) // 5
    n5 = T // 5
    S5, C5, D5 = np.zeros(n5), np.zeros(n5), np.zeros(n5)
    P5 = np.zeros(n5, bool)
    S5[bi5] = np.add.reduceat(f5["bid"] + f5["ask"], s)
    C5[bi5] = np.add.reduceat((f5["bid"] > 0).astype(float) + (f5["ask"] > 0), s)
    D5[bi5] = np.add.reduceat(f5["ask"] - f5["bid"], s)
    P5[bi5] = True
    cS, cC, cP = (np.r_[0.0, np.cumsum(x)] for x in (S5, C5, P5.astype(float)))
    D = dict(sym=sym, t0=t0, T=T, nd=nd, k=k, O=O, H=H, L=L, Cf=Cf, prevC=prevC, atr=atr, fmin=fmin, fcum=fcum,
             prof=prof, pocd=pocd, key5=key5, bid5=f5["bid"], ask5=f5["ask"], D5=D5, P5=P5, cS=cS, cC=cC, cP=cP,
             slip=SLIP[sym], hole_day=hole_day, hcum=hcum, nholes=nholes, hole_h=hole_h)
    print(f"{sym} prepared in {time.time() - t_start:.0f}s: days {nd}, levels {np.sum(prof[:, 0] >= 0)}, holes {nholes} ({hole_h:.0f} h, {hole_day.sum()} days)", flush=True)
    return D


def value_area(dense, frac=0.7):
    """POC (lowest row on a tie) and the 70 % value area grown row by row toward the larger neighbour (tie: up)."""
    p = int(np.argmax(dense))
    tot, acc, lo, hi = dense.sum(), dense[p], p, p
    while acc < frac * tot:
        up = dense[hi + 1] if hi + 1 < len(dense) else -1.0
        dn = dense[lo - 1] if lo > 0 else -1.0
        if up >= dn:
            hi += 1
            acc += up
        else:
            lo -= 1
            acc += dn
    return p, lo, hi


def rp(row, k, edge="low"):
    return fp.row_price(row, k, edge)


# --------------------------------------------------------------------------------------------------------- tests
def find_tests(D, LR):
    """LR: (nd, nlev) level rows for day d (-1 = none). Returns arrays of tests: day, lev, row, minute idx, side."""
    nd, k = D["nd"], D["k"]
    Hm, Lm, Pm = (D[x].reshape(nd, 1440) for x in ("H", "L", "prevC"))
    out = []
    ok_day = np.isfinite(D["atr"])
    for j in range(LR.shape[1]):
        r = LR[:, j]
        good = (r >= 0) & ok_day
        dd = np.flatnonzero(good)
        lo = rp(r[dd], k)[:, None]
        hi = rp(r[dd], k, "high")[:, None]
        P, Hh, Ll = Pm[dd], Hm[dd], Lm[dd]
        sup = (P > hi) & (Ll <= hi)
        res = (P < lo) & (Hh >= lo)
        anyt = sup | res
        first = np.argmax(anyt, axis=1)
        has = anyt[np.arange(len(dd)), first]
        side = np.where(sup[np.arange(len(dd)), first], 1, -1)
        dd, first, side = dd[has], first[has], side[has]
        out.append(np.c_[dd, np.full(len(dd), j), r[dd], dd * 1440 + first, side])
    t = np.concatenate(out).astype(np.int64)
    return t[np.argsort(t[:, 3], kind="stable")]


def lookup5(D, b, row):
    """bid, ask of 5m dense bar index b at row (0 if absent)."""
    q = (D["t0"] + b * 5) * RK + row
    i = np.searchsorted(D["key5"], q)
    i = np.minimum(i, len(D["key5"]) - 1)
    f = D["key5"][i] == q
    return np.where(f, D["bid5"][i], 0.0), np.where(f, D["ask5"][i], 0.0)


def confirm(D, tests):
    """Per test and confirmation cell: entry minute idx (close of the confirming 5m bar) or -1."""
    k, n5 = D["k"], len(D["P5"])
    row, tm, side = tests[:, 2], tests[:, 3], tests[:, 4]
    B0 = tm // 5
    a = np.maximum(B0 - 12, 0)
    ref = (D["cS"][B0] - D["cS"][a]) / np.maximum(D["cC"][B0] - D["cC"][a], 1)
    ok = (D["cP"][B0] - D["cP"][a] >= 6) & (D["cC"][B0] - D["cC"][a] > 0)
    nb = WIN + BON
    bmax = np.zeros((len(tests), nb))
    amax = np.zeros_like(bmax)
    both = np.zeros_like(bmax)
    pres = np.zeros((len(tests), nb), bool)
    dsg = np.zeros((len(tests), nb), bool)
    cin = np.zeros((len(tests), nb), bool)
    lo_z, hi_z = rp(row - 1, k), rp(row + 1, k, "high")
    for j in range(nb):
        b = np.minimum(B0 + j, n5 - 1)
        for dr in (-1, 0, 1):
            bv, av = lookup5(D, b, row + dr)
            bmax[:, j] = np.maximum(bmax[:, j], bv)
            amax[:, j] = np.maximum(amax[:, j], av)
            both[:, j] = np.maximum(both[:, j], np.minimum(bv, av))
        pres[:, j] = D["P5"][b] & (B0 + j < n5)
        dsg[:, j] = np.sign(D["D5"][b]) == side
        cl = D["Cf"][b * 5 + 4]
        cin[:, j] = np.where(side > 0, cl >= lo_z, cl <= hi_z)
    res = {}
    for m in MS:
        thr = (m * ref)[:, None]
        pas = np.where((side > 0)[:, None], bmax, amax)
        c1 = (pas >= thr) & pres & ok[:, None]
        c2 = (both >= thr) & cin & pres & ok[:, None]
        c1[:, WIN:] = False
        c2[:, WIN:] = False
        c12 = c1 | c2
        bon = np.zeros_like(c1)
        for j in range(1, nb):
            prior = c12[:, max(0, j - BON):min(j, WIN)].any(axis=1)
            bon[:, j] = prior & dsg[:, j] & pres[:, j]
        for name, mat in (("C1", c1), ("C2", c2), ("BON", bon)):
            hit = mat.any(axis=1)
            j = np.argmax(mat, axis=1)
            res[(name, m)] = np.where(hit, (B0 + j) * 5 + 4, -1)
    res[("N0m", 0)] = np.where(D["P5"][np.minimum(B0, n5 - 1)], B0 * 5 + 4, -1)
    return res


# ---------------------------------------------------------------------------------------------------- simulation
def tp_price(D, ent_t, P, SD, side, mode):
    if mode == "2R":
        return P + side * 2 * SD
    k = D["k"]
    nb = np.floor(ent_t / 30).astype(np.int64)  # bars with index < nb are complete at ent_t (minutes from t0)
    idx = nb[:, None] - 48 + np.arange(48)[None, :]
    rows = np.where(idx >= 0, D["pocd"][np.maximum(idx, 0)], -1)
    valid = rows >= 0
    lo_e, hi_e = rp(rows, k), rp(rows, k, "high")
    up = valid & (lo_e > (P + SD)[:, None])
    dn = valid & (hi_e < (P - SD)[:, None])
    tl = np.where(up, rp(rows - 1, k), np.inf).min(axis=1)
    ts = np.where(dn, rp(rows + 1, k, "high"), -np.inf).max(axis=1)
    tp = np.where(side > 0, tl, ts)
    far = np.where(side > 0, tp > P + 3 * SD, tp < P - 3 * SD) | ~np.isfinite(tp)
    return np.where(far, P + side * 2 * SD, tp)


def simulate(D, e, side, P, SD, TP, limit=False, chunk=1500):
    """e: minute idx of entry (market: entry at close of e, path from e+1; limit: fill inside e, only the stop can
    trigger in e). Returns gross bp, exit kind (0 stop, 1 tp, 2 time), exit time (minutes from t0), funding bp."""
    T, O, H, L, Cf, slip = D["T"], D["O"], D["H"], D["L"], D["Cf"], D["slip"]
    n = len(e)
    X = np.zeros(n)
    kind = np.zeros(n, np.int64)
    xt = np.zeros(n)
    stop = P - side * SD
    for a in range(0, n, chunk):
        sl = slice(a, a + chunk)
        ee, ss, st, tp = e[sl], side[sl], stop[sl], TP[sl]
        idx = ee[:, None] + 1 + np.arange(1440)[None, :]
        inb = idx < T
        idc = np.minimum(idx, T - 1)
        Hw, Lw, Ow = H[idc], L[idc], O[idc]
        Hw[~inb], Lw[~inb] = np.nan, np.nan
        lg = (ss > 0)[:, None]
        hs = np.where(lg, Lw <= st[:, None], Hw >= st[:, None])
        ht = np.where(lg, Hw > tp[:, None], Lw < tp[:, None])
        iS = np.where(hs.any(1), np.argmax(hs, 1), 1440)
        iT = np.where(ht.any(1), np.argmax(ht, 1), 1440)
        r = np.arange(len(ee))
        if limit:
            s0 = np.where(ss > 0, L[ee] <= st, H[ee] >= st)
            iS = np.where(s0, -1, iS)
        stopx = (iS <= iT) & (iS < 1440)
        tpx = ~stopx & (iT < 1440)
        oS = Ow[r, np.clip(iS, 0, 1439)]
        fillS = np.where(ss > 0, np.fmin(st, oS), np.fmax(st, oS))
        fillS = np.where(iS < 0, st, fillS)
        fillS = fillS * (1 - ss * slip)
        last = np.minimum(ee + 1440, T - 1)
        xs = np.where(stopx, fillS, np.where(tpx, tp, Cf[last]))
        X[sl] = xs
        kind[sl] = np.where(stopx, 0, np.where(tpx, 1, 2))
        xt[sl] = np.where(stopx, ee + 1 + iS + 0.5, np.where(tpx, ee + 1 + iT + 0.5, last + 1))
    et = e + (0.5 if limit else 1.0)
    fs = np.searchsorted(D["fmin"], D["t0"] + et, side="right")
    fe = np.searchsorted(D["fmin"], D["t0"] + xt, side="right")
    fund = -side * (D["fcum"][fe] - D["fcum"][fs]) * 1e4
    gross = side * (X / P - 1) * 1e4
    return gross, kind, xt, fund


def one_open(et, xt):
    """Sequential filter: keep a trade only if it starts after the previous kept trade's exit (inputs time sorted)."""
    keep = np.zeros(len(et), bool)
    busy = -1.0
    for i in range(len(et)):
        if et[i] > busy:
            keep[i] = True
            busy = xt[i]
    return keep


def run_cells(D, tests, late=False, entry_slip=False, cells=ALL):
    """All cells for one set of tests. Returns dict cell -> dict of per-trade arrays (after the one-open filter)."""
    conf = confirm(D, tests)
    k, slip = D["k"], D["slip"]
    side_all, row_all, tm_all, day_all = tests[:, 4], tests[:, 2], tests[:, 3], tests[:, 0]
    out = {}
    for c in cells:
        name, m, tpm = c
        limit = name == "N0"
        if limit:
            hi, lo = rp(row_all, k, "high"), rp(row_all, k)
            P = np.where(side_all > 0, hi, lo)
            thr = np.where(side_all > 0, D["L"][tm_all] <= hi * (1 - 1e-4), D["H"][tm_all] >= lo * (1 + 1e-4))
            sel = np.flatnonzero(thr)
            e = tm_all[sel]
            P = P[sel]
        else:
            ent = conf[(name, m)]
            sel = np.flatnonzero(ent >= 0)
            e = ent[sel]
            P = D["Cf"][e]
        side = side_all[sel]
        dd0 = np.minimum(e // 1440, D["nd"] - 1)
        SD = 0.15 * D["atr"][dd0]
        fin = np.isfinite(SD) & np.isfinite(P)
        sel, e, P, side, SD = sel[fin], e[fin], P[fin], side[fin], SD[fin]
        ent_t = e + (0.5 if limit else 1.0)
        TP = tp_price(D, ent_t, P, SD, side, tpm)
        if late:  # market at the close of the next minute (limit: close of the fill minute), same stop / TP prices
            e2 = e if limit else e + 1
            e2 = np.minimum(e2, D["T"] - 2)
            P2 = D["Cf"][e2]
            TP = TP + (P2 - P)  # same stop / TP distances from the late fill
            e, P = e2, P2
            limit_sim, fee_in = False, TAKER
        else:
            limit_sim, fee_in = limit, (MAKER if limit else TAKER)
        o = np.argsort(e, kind="stable")
        sel, e, side, P, SD, TP = sel[o], e[o], side[o], P[o], SD[o], TP[o]
        gross, kind, xt, fund = simulate(D, e, side, P, SD, TP, limit=limit_sim)
        hc = D["hcum"]
        span = hc[np.minimum(np.ceil(xt).astype(np.int64) + 1, len(hc) - 1)] - hc[np.maximum(e - 60, 0)] > 0
        nspan = int(span.sum())
        keep = ~span
        ks = np.flatnonzero(keep)
        keep[ks] = one_open((e + (0.5 if limit_sim else 1.0))[ks], xt[ks])
        fee_out = np.where(kind == 1, MAKER, TAKER)
        extra = 0.0
        if entry_slip:
            extra = slip * 1e4 * ((fee_in == TAKER) + (kind == 2))
        R = SD / P * 1e4
        out[c] = dict(e=e[keep], side=side[keep], gross=gross[keep], fund=fund[keep],
                      fee=(fee_in + fee_out)[keep] + (extra[keep] if entry_slip else 0.0), kind=kind[keep],
                      R=R[keep], lev=tests[sel[keep], 1], tday=day_all[sel[keep]], xt=xt[keep], nspan=np.array([nspan]))
    return out, conf


def day_sums(D, res, mult=1.0):
    """Per cell: (2, NDAYS_ALL, 2) sums of net and counts by absolute day, split IS / VAL in the last axis? No:
    returns array (ncell, NDAYS_ALL, 2) = (sum net, count) by entry day from 2020-01-01."""
    arr = np.zeros((len(ALL), NDAYS_ALL, 2), np.float32)
    off = D["t0"] // 1440 - DAY0
    for i, c in enumerate(ALL):
        r = res[c]
        net = r["gross"] + r["fund"] - mult * r["fee"]
        d = r["e"] // 1440 + off
        arr[i, :, 0] = np.bincount(d, weights=net, minlength=NDAYS_ALL)[:NDAYS_ALL]
        arr[i, :, 1] = np.bincount(d, minlength=NDAYS_ALL)[:NDAYS_ALL]
    return arr


def random_levels(D, rng):
    prof = D["prof"]
    nd = D["nd"]
    LR = np.full((nd, 3), -1, np.int64)
    for j in range(3):
        L = np.r_[-1, prof[:-1, j]]
        rmin, rmax = np.r_[-1, prof[:-1, 3]], np.r_[-1, prof[:-1, 4]]
        ok = L >= 0
        exlo = np.maximum(L - 1, rmin)
        exhi = np.minimum(L + 1, rmax)
        nex = exhi - exlo + 1
        n = rmax - rmin + 1 - nex
        ok &= n > 0
        u = np.floor(rng.random(nd) * np.maximum(n, 1)).astype(np.int64)
        cand = rmin + u
        cand = np.where(cand >= exlo, cand + nex, cand)
        LR[:, j] = np.where(ok, cand, -1)
    LR[D["hole_day"]] = -1
    return LR


def real_levels(D):
    prof = D["prof"]
    LR = np.full((D["nd"], 3), -1, np.int64)
    LR[1:] = prof[:-1, :3]
    LR[D["hole_day"]] = -1  # day d itself has a hole (day d - 1 holes already give no profile)
    return LR


def run(sym, ndraws=200):
    os.makedirs(OUT, exist_ok=True)
    D = prepare(sym)
    t = time.time()
    tests = find_tests(D, real_levels(D))
    variants = {}
    base, conf = run_cells(D, tests)
    variants["base"] = base
    variants["late"], _ = run_cells(D, tests, late=True)
    variants["eslip"], _ = run_cells(D, tests, entry_slip=True)
    off = D["t0"] // 1440 - DAY0
    save = {"tests": tests, "off": off, "conf_n": np.array([np.sum(conf[(c, m)] >= 0) for c in CONFS for m in MS])}
    for v, res in variants.items():
        for c in ALL:
            for f, arr in res[c].items():
                save[f"{v}|{cname(c)}|{f}"] = arr
    np.savez_compressed(os.path.join(OUT, f"{sym}_real.npz"), **save)
    print(f"{sym} real done {time.time() - t:.0f}s, tests {len(tests)}", flush=True)
    rng = np.random.default_rng(7500 + fp.SYMS.index(sym))
    sums = np.zeros((ndraws, len(ALL), NDAYS_ALL, 2), np.float32)
    ntests = np.zeros(ndraws, np.int64)
    for i in range(ndraws):
        tr = find_tests(D, random_levels(D, rng))
        res, _ = run_cells(D, tr)
        sums[i] = day_sums(D, res)
        ntests[i] = len(tr)
        if i % 20 == 0:
            print(f"{sym} draw {i} {time.time() - t:.0f}s tests {len(tr)}", flush=True)
    np.savez_compressed(os.path.join(OUT, f"{sym}_rand.npz"), sums=sums, ntests=ntests,
                        real=day_sums(D, base), cells=np.array([cname(c) for c in ALL]))
    print(f"{sym} all done {time.time() - t:.0f}s", flush=True)


# ------------------------------------------------------------------------------------------------------ selftest
def selftest():
    # value area on a toy profile: rows 0..6 volumes, POC row 3
    # 31 total: POC row 3 (10) -> +8 row 2 (18) -> +3 row 4 (21) < 21.7 -> +6 row 5 (27)
    assert value_area(np.array([1, 2, 8, 10, 3, 6, 1], float)) == (3, 2, 5)
    assert value_area(np.array([5, 5, 1], float)) == (0, 0, 1)  # tie on POC -> lowest row, tie on growth -> up
    # one_open
    keep = one_open(np.array([1.0, 2.0, 5.0, 6.0]), np.array([4.0, 3.0, 5.5, 9.0]))
    assert list(keep) == [True, False, True, True], keep
    print("ab selftest ok")


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        selftest()
    elif sys.argv[1] == "run":
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 200)
