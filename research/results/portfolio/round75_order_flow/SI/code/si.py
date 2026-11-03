"""Stream SI (round 75): stacked imbalance zones, first test, common execution model of BRIEF.md.

Usage:
    python -I si.py <SYM> <ERA> [--draws N] [--real-only]
ERA = IS (minute data cut at 2022-01-01) or VAL (2020-2024 data, trades filled in 2022-2024 kept).
Writes SI/out/<SYM>_<ERA>_real.npz and SI/out/<SYM>_<ERA>_rand.npz.
"""
import importlib.util
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SI = os.path.dirname(HERE)
OUT = os.path.join(SI, "out")
_spec = importlib.util.spec_from_file_location("fp", os.path.join(SI, "..", "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

ROOT = fp.ROOT
VAL_START_MIN = fp.IS_END_MIN
EXPIRY_BARS = 336
MAKER, TAKER = 2.0, 5.0
SLIP = {"BTCUSDT": 1.0, "ETHUSDT": 1.0, "SOLUSDT": 2.0}
CELLS = [("f0", "TPV"), ("f0", "2R"), ("fmed", "TPV"), ("fmed", "2R")]


class Prep:
    pass


def prepare(sym, cut_min):
    P = Prep()
    P.sym = sym
    m = fp.load_minutes(sym)
    keep = m["min"] < cut_min
    m = {k: v[keep] for k, v in m.items()}
    P.mmin, P.o, P.h, P.l, P.c = m["min"], m["o"], m["h"], m["l"], m["c"]
    b = fp.bars(m, 30)
    P.bstart, P.bh, P.bl, P.bc = b["start"], b["h"], b["l"], b["c"]
    f = fp.load_fp(sym, 30)
    kf = f["bar"] < cut_min
    f = {n: f[n][kf] for n in ("bar", "row", "bid", "ask")} | {"k": f["k"], "tf": f["tf"]}
    f["ptr"] = np.r_[np.flatnonzero(np.r_[True, np.diff(f["bar"]) != 0]), len(f["bar"])]
    P.f = f
    P.k = f["k"]
    fb = f["bar"][f["ptr"][:-1]]
    assert np.array_equal(fb, P.bstart), "footprint bars != minute bars"
    # POC per bar, bottom / top row per bar
    _, P.poc_row = fp.poc(f)
    s, e = f["ptr"][:-1], f["ptr"][1:] - 1
    P.brow_lo, P.brow_hi = f["row"][s], f["row"][e]
    # sanity (BTC key fix 2026-11-03): each bar's low / high lies in its bottom / top row
    lo_ok = np.abs(fp.bucket(P.bl) // P.k - P.brow_lo) <= 1
    hi_ok = np.abs(fp.bucket(P.bh) // P.k - P.brow_hi) <= 1
    assert lo_ok.mean() > 0.999 and hi_ok.mean() > 0.999, (lo_ok.mean(), hi_ok.mean())
    # daily ATR14 from perp_1d daily klines (BRIEF update; rows >= 2025 dropped on load); 14 contiguous days
    kz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "perp_1d", f"{sym}.csv"), delimiter=",",
                    skiprows=1, usecols=(0, 2, 3, 4))
    kz = kz[kz[:, 0] < fp.HOLD_MIN * 60000.0]
    day = (kz[:, 0] // 86400000).astype(np.int64)
    dh, dl, dc = kz[:, 1], kz[:, 2], kz[:, 3]
    pc = np.r_[np.nan, dc[:-1]]
    contiguous = np.r_[False, np.diff(day) == 1]
    tr = np.where(contiguous, np.maximum(dh, pc) - np.minimum(dl, pc), dh - dl)
    P.day0 = int(day[0])
    nd = max(int(day[-1]), int(P.mmin[-1] // 1440)) - P.day0 + 2
    trd = np.full(nd, np.nan)
    trd[day - P.day0] = tr
    atr = np.full(nd, np.nan)
    for i in range(14, nd):
        w = trd[i - 14:i]
        if not np.isnan(w).any():
            atr[i] = w.mean()
    # holes in the 1m cache (> 30 min without a minute): zones / trades whose life spans one are dropped
    gap = np.flatnonzero(np.diff(P.mmin) > 30)
    P.hole_start = P.mmin[gap]
    P.hole_len = P.mmin[gap + 1] - P.mmin[gap]
    P.atr = atr
    # funding (HOLD rows dropped on load)
    fz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "funding", f"{sym}.csv"), delimiter=",",
                    skiprows=1)
    fz = fz[fz[:, 0] < fp.HOLD_MIN * 60000.0]
    o = np.argsort(fz[:, 0])
    P.fund_min = (fz[o, 0] // 60000).astype(np.int64)
    P.fund_cum = np.r_[0.0, np.cumsum(fz[o, 1])]
    P.slip = SLIP[sym] / 1e4
    return P


def bar_floor(P):
    """Median of non-zero individual bid and ask values over the 48 bars before each bar (nan if < 48 bars)."""
    f = P.f
    ptr = f["ptr"]
    nb = len(ptr) - 1
    out = np.full(nb, np.nan)
    bid, ask = f["bid"], f["ask"]
    for b in range(48, nb):
        a0, a1 = ptr[b - 48], ptr[b]
        v = np.concatenate([bid[a0:a1], ask[a0:a1]])
        v = v[v > 0]
        if len(v):
            out[b] = np.median(v)
    return out


def make_zones(P, floor_mode, n=3, floors=None):
    f = P.f
    nb = len(f["ptr"]) - 1
    seg = np.repeat(np.arange(nb), np.diff(f["ptr"]))
    if floor_mode == "f0":
        fl = 0.0
        valid_bar = np.ones(nb, bool)
    else:
        valid_bar = ~np.isnan(floors)
        fl = np.where(valid_bar, floors, np.inf)[seg]
    buy, sell = fp.imbalances(f, ratio=3.0, floor=fl)
    zs = []
    for flag, side in ((buy, 1), (sell, -1)):
        st = fp.stacked(f, flag, n=n)
        if not st:
            continue
        a = np.array(st, dtype=np.int64)
        zs.append(np.c_[a, np.full(len(a), side)])
    z = np.concatenate(zs)
    zb = np.searchsorted(P.bstart, z[:, 0])
    keep = valid_bar[zb]
    z, zb = z[keep], zb[keep]
    o = np.lexsort((z[:, 1], zb))
    return {"zb": zb[o], "lo_row": z[o, 1], "hi_row": z[o, 2], "side": z[o, 3]}


def random_zones(P, Z, rng):
    """Same width, same bar, centre uniform in the 48-bar row range (inclusive of the formation bar), excluding the
    real zone's rows; side from the formation close."""
    zb = Z["zb"]
    w = Z["hi_row"] - Z["lo_row"] + 1
    nb = len(P.bstart)
    lo48 = np.empty(nb, np.int64)
    hi48 = np.empty(nb, np.int64)
    from numpy.lib.stride_tricks import sliding_window_view as swv
    pad_lo = np.r_[np.full(47, P.brow_lo[0]), P.brow_lo]
    pad_hi = np.r_[np.full(47, P.brow_hi[0]), P.brow_hi]
    lo48[:] = swv(pad_lo, 48).min(axis=1)
    hi48[:] = swv(pad_hi, 48).max(axis=1)
    rmin, rmax = lo48[zb], hi48[zb]
    exc_lo = np.maximum(Z["lo_row"], rmin)
    exc_hi = np.minimum(Z["hi_row"], rmax)
    nexc = np.maximum(exc_hi - exc_lo + 1, 0)
    navail = (rmax - rmin + 1) - nexc
    ok = navail > 0
    u = np.floor(rng.random(len(zb)) * np.maximum(navail, 1)).astype(np.int64)
    centre = rmin + u
    centre = np.where((nexc > 0) & (centre >= exc_lo), centre + nexc, centre)
    lo_row = centre - (w - 1) // 2
    hi_row = lo_row + w - 1
    lo_p = fp.row_price(lo_row, P.k, "low")
    hi_p = fp.row_price(hi_row, P.k, "high")
    cl = P.bc[zb]
    side = np.where(hi_p < cl, 1, np.where(lo_p > cl, -1, Z["side"]))
    return {"zb": zb[ok], "lo_row": lo_row[ok], "hi_row": hi_row[ok], "side": side[ok]}


def test_zones(P, Z):
    """Per zone: fill minute position (-1 if no usable first test or not filled) and entry price."""
    zb, side = Z["zb"], Z["side"]
    lo = fp.row_price(Z["lo_row"], P.k, "low")
    hi = fp.row_price(Z["hi_row"], P.k, "high")
    nz, nb = len(zb), len(P.bstart)
    E = P.bstart[zb] + 30 + EXPIRY_BARS * 30
    usable = np.full(nz, -1)
    cnt = np.zeros(nz, np.int64)
    act = np.arange(nz)
    j = 1
    while len(act):
        idx = zb[act] + j
        inb = idx < nb
        idxc = np.minimum(idx, nb - 1)
        intime = inb & (P.bstart[idxc] + 30 <= E[act])
        s = side[act]
        beyond = intime & np.where(s > 0, P.bl[idxc] > hi[act], P.bh[idxc] < lo[act])
        cnt[act] += beyond
        done2 = cnt[act] >= 2
        usable[act[done2]] = idxc[done2]
        act = act[~done2 & intime]
        j += 1
    # first test bar after the usable bar
    testbar = np.full(nz, -1)
    act = np.flatnonzero(usable >= 0)
    j = 1
    while len(act):
        idx = usable[act] + j
        inb = idx < nb
        idxc = np.minimum(idx, nb - 1)
        intime = inb & (P.bstart[idxc] < E[act])
        s = side[act]
        touch = intime & np.where(s > 0, P.bl[idxc] <= hi[act], P.bh[idxc] >= lo[act])
        testbar[act[touch]] = idxc[touch]
        act = act[~touch & intime]
        j += 1
    # first minute in the test bar that reaches the near edge
    fillpos = np.full(nz, -1)
    entry = np.where(side > 0, hi, lo)
    t = np.flatnonzero(testbar >= 0)
    if len(t):
        p0 = np.searchsorted(P.mmin, P.bstart[testbar[t]])
        bend = P.bstart[testbar[t]] + 30
        first = np.full(len(t), -1)
        nm = len(P.mmin)
        for off in range(30):
            pos = np.minimum(p0 + off, nm - 1)
            inbar = (p0 + off < nm) & (P.mmin[pos] < bend) & (first < 0)
            s = side[t]
            touch = inbar & np.where(s > 0, P.l[pos] <= hi[t], P.h[pos] >= lo[t])
            first[touch] = pos[touch]
        assert (first >= 0).all()
        s = side[t]
        filled = np.where(s > 0, P.l[first] <= hi[t] * (1 - 1e-4), P.h[first] >= lo[t] * (1 + 1e-4))
        fillpos[t[filled]] = first[filled]
        testpos = np.full(nz, -1)
        testpos[t] = first
    else:
        testpos = np.full(nz, -1)
    return {"fillpos": fillpos, "testpos": testpos, "entry": entry, "side": side, "zb": zb}


def _tp(P, p0, side, entry, R, mode):
    if mode == "2R":
        return entry + side * 2 * R
    be = np.searchsorted(P.bstart + 30, P.mmin[p0], "right")  # bars closed by the entry minute's start
    rows = P.poc_row[max(0, be - 48):be]
    k = P.k
    if side > 0:
        low = np.exp(rows * k / 1e4)
        c = rows[(low > entry + R) & (low <= entry + 3 * R)]
        if len(c):
            return float(np.exp((c.min() - 1) * k / 1e4))
    else:
        high = np.exp((rows + 1) * k / 1e4)
        c = rows[(high < entry - R) & (high >= entry - 3 * R)]
        if len(c):
            return float(np.exp((c.max() + 2) * k / 1e4))
    return entry + side * 2 * R


def sim_trade(P, p0, side, entry, R, tp, late):
    m = P.mmin
    pend = np.searchsorted(m, m[p0] + 1440, "right") - 1
    stop = entry - side * R
    if late:
        e = P.c[p0]
        fee_in = TAKER
    else:
        e = entry
        fee_in = MAKER
        if (side > 0 and P.l[p0] <= stop) or (side < 0 and P.h[p0] >= stop):
            return e, stop, "S", p0, fee_in
    a = p0 + 1
    if pend < a:
        return e, P.c[p0], "T", p0, fee_in
    if side > 0:
        hs = P.l[a:pend + 1] <= stop
        ht = P.h[a:pend + 1] > tp
    else:
        hs = P.h[a:pend + 1] >= stop
        ht = P.l[a:pend + 1] < tp
    iS = int(np.argmax(hs)) if hs.any() else 10 ** 9
    iT = int(np.argmax(ht)) if ht.any() else 10 ** 9
    if iS <= iT and iS < 10 ** 9:
        p = a + iS
        op = P.o[p]
        px = op if (side > 0 and op <= stop) or (side < 0 and op >= stop) else stop
        return e, px, "S", p, fee_in
    if iT < 10 ** 9:
        return e, tp, "P", a + iT, fee_in
    return e, P.c[pend], "T", pend, fee_in


def _hole(P, a, b):
    """True if a cache hole starts in [a, b) (a, b are existing minutes, so this is any overlap)."""
    i = np.searchsorted(P.hole_start, a)
    return i < len(P.hole_start) and P.hole_start[i] < b


def run_cell(P, T, tp_mode, late, era_lo, era_hi):
    """Greedy one-open-trade schedule over filled first tests. Returns dict of trade arrays."""
    fpos = T["fillpos"]
    cand = np.flatnonzero(fpos >= 0)
    fm = P.mmin[fpos[cand]]
    cand = cand[(fm >= era_lo) & (fm < era_hi)]
    cand = cand[np.argsort(fpos[cand], kind="stable")]
    rec = []
    drops = {"zone": 0, "trade": 0}
    last_exit = -1
    for z in cand:
        p0 = fpos[z]
        mn = P.mmin[p0]
        if mn <= last_exit:
            continue
        F = P.bstart[T["zb"][z]]
        if _hole(P, F, mn):
            drops["zone"] += 1
            continue
        di = mn // 1440 - P.day0
        a = P.atr[di] if 0 <= di < len(P.atr) else np.nan
        if np.isnan(a):
            continue
        side = int(T["side"][z])
        entry = float(T["entry"][z])
        R = 0.15 * a
        tp = _tp(P, p0, side, entry, R, tp_mode)
        e, px, kind, pex, fee_in = sim_trade(P, p0, side, entry, R, tp, late)
        exit_min = P.mmin[pex]
        if _hole(P, mn, exit_min):
            drops["trade"] += 1
            continue
        last_exit = exit_min
        gross = side * (px / e - 1) * 1e4
        slip = P.slip * 1e4 if kind == "S" else 0.0
        fee = fee_in + (MAKER if kind == "P" else TAKER)
        i0 = np.searchsorted(P.fund_min, mn, "right")
        i1 = np.searchsorted(P.fund_min, exit_min, "right")
        fund = -side * (P.fund_cum[i1] - P.fund_cum[i0]) * 1e4
        rbp = R / entry * 1e4
        rec.append((z, mn, exit_min, side, gross, slip, fee, fund, rbp, "SPT".index(kind)))
    if not rec:
        return None
    a = np.array(rec, dtype=float)
    out = {"zone": a[:, 0].astype(np.int64), "fill_min": a[:, 1].astype(np.int64),
           "exit_min": a[:, 2].astype(np.int64), "side": a[:, 3].astype(np.int8), "gross": a[:, 4],
           "slip": a[:, 5], "fee": a[:, 6], "fund": a[:, 7], "rbp": a[:, 8], "kind": a[:, 9].astype(np.int8)}
    out["net"] = out["gross"] - out["slip"] - out["fee"] + out["fund"]
    out["drops"] = np.array([drops["zone"], drops["trade"]])
    return out


def era_bounds(era):
    if era == "IS":
        return 0, VAL_START_MIN, VAL_START_MIN
    return VAL_START_MIN, fp.HOLD_MIN, fp.HOLD_MIN


def main():
    sym, era = sys.argv[1], sys.argv[2]
    draws = 200
    if "--draws" in sys.argv:
        draws = int(sys.argv[sys.argv.index("--draws") + 1])
    real_only = "--real-only" in sys.argv
    era_lo, era_hi, cut = era_bounds(era)
    t0 = time.time()
    P = prepare(sym, cut)
    floors = bar_floor(P)
    print(f"{sym} {era}: prep {time.time() - t0:.0f}s, bars {len(P.bstart)}, k {P.k}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    real = {}
    zsets = {}
    for fm in ("f0", "fmed"):
        for n in (3, 4):
            Z = make_zones(P, fm, n=n, floors=floors)
            if n == 3:
                zsets[fm] = Z
            T = test_zones(P, Z)
            nz = int(((P.bstart[Z["zb"]] >= era_lo) & (P.bstart[Z["zb"]] < era_hi)).sum())
            print(f"  {fm} n{n}: zones in era {nz}, tested {int((T['testpos'] >= 0).sum())}, "
                  f"filled {int((T['fillpos'] >= 0).sum())}", flush=True)
            for tpm in ("TPV", "2R"):
                for late in (False, True):
                    r = run_cell(P, T, tpm, late, era_lo, era_hi)
                    tag = f"{fm}_n{n}_{tpm}_{'late' if late else 'base'}"
                    if r is not None:
                        if not late:
                            print(f"    {tag}: trades {len(r['net'])}, dropped for holes zone {r['drops'][0]} "
                                  f"trade {r['drops'][1]}", flush=True)
                        for kk, vv in r.items():
                            real[f"{tag}__{kk}"] = vv
    np.savez(os.path.join(OUT, f"{sym}_{era}_real.npz"), **real)
    print(f"  real done {time.time() - t0:.0f}s", flush=True)
    if real_only:
        return
    seed = {"BTCUSDT": 1, "ETHUSDT": 2, "SOLUSDT": 3}[sym] * 1000 + (0 if era == "IS" else 500)
    rng = np.random.default_rng(seed)
    days, nets, dr, cl = [], [], [], []
    for d in range(draws):
        for ci, (fm, tpm) in enumerate(CELLS):
            if tpm == "TPV":
                RZ = random_zones(P, zsets[fm], rng)
                RT = test_zones(P, RZ)
            r = run_cell(P, RT, tpm, False, era_lo, era_hi)
            if r is None:
                continue
            days.append(r["fill_min"] // 1440)
            nets.append(r["net"])
            dr.append(np.full(len(r["net"]), d, np.int16))
            cl.append(np.full(len(r["net"]), ci, np.int8))
        if d % 10 == 9:
            print(f"  draw {d + 1}/{draws} {time.time() - t0:.0f}s", flush=True)
            np.savez(os.path.join(OUT, f"{sym}_{era}_rand.npz"), day=np.concatenate(days),
                     net=np.concatenate(nets).astype(np.float32), draw=np.concatenate(dr), cell=np.concatenate(cl),
                     ndraws=d + 1)
    print(f"  random done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
