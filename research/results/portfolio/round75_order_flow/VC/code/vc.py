"""Stream VC (round 75): volume clusters in a trend leg / a rejection, first retest. Rules: ../HYPOTHESES_VC.md.

Usage: python -I vc.py <SYM> [n_draws]   -> out/<SYM>_real.npz, out/<SYM>_rand.npz, out/<SYM>_counts.json
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VC = os.path.dirname(HERE)
OUT = os.path.join(VC, "out")
_spec = importlib.util.spec_from_file_location("fp", os.path.join(VC, "..", "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

ROOT = fp.ROOT
HOLD_MS = fp.HOLD_MIN * 60000
IS_END = fp.IS_END_MIN
EXPIRY = 10080
HOLD_T = 1440
SETUPS = ("trend", "rej")
CS = (2, 3)
TPS = ("TPV", "2R")


class Data:
    def __init__(self, sym):
        self.sym = sym
        m = fp.load_minutes(sym)
        self.mn, self.mo, self.mh, self.ml, self.mc = m["min"], m["o"], m["h"], m["l"], m["c"]
        b = fp.bars(m, 30)
        self.bs, self.bo, self.bh, self.bl, self.bc = b["start"], b["o"], b["h"], b["l"], b["c"]
        f = fp.load_fp(sym, 30)
        self.k = f["k"]
        assert np.array_equal(f["bar"][f["ptr"][:-1]], self.bs), "fp bars != minute bars"
        self.ptr, self.row, self.vol = f["ptr"], f["row"], f["bid"] + f["ask"]
        self.rmin = self.row[self.ptr[:-1]]
        self.rmax = self.row[self.ptr[1:] - 1]
        _, self.poc = fp.poc(f)
        del f
        # daily ATR14 from perp_1d klines (rows >= 2025 dropped on read); TR of UTC day, mean of the 14 days before
        kz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "perp_1d", sym + ".csv"), delimiter=",",
                        skiprows=1, usecols=(0, 2, 3, 4))
        kz = kz[kz[:, 0] < HOLD_MS]
        ud = (kz[:, 0] // 86400000).astype(np.int64)
        dh, dl, dc = kz[:, 1], kz[:, 2], kz[:, 3]
        pc = np.r_[dc[0], dc[:-1]]
        tr = np.maximum(dh, pc) - np.minimum(dl, pc)
        tr[0] = dh[0] - dl[0]
        cs = np.r_[0.0, np.cumsum(tr)]
        self.ud, self.cs_tr = ud, cs
        # holes in the 1m cache (> 30 min between trades)
        g = np.flatnonzero(np.diff(self.mn) > 30)
        self.hs, self.he = self.mn[g], self.mn[g + 1]
        # funding (< 2025 only)
        fz = np.loadtxt(os.path.join(ROOT, "research", "data", "binance", "funding", sym + ".csv"), delimiter=",",
                        skiprows=1)
        fz = fz[fz[:, 0] < HOLD_MS]
        self.fs, self.fr = (fz[:, 0] // 1000).astype(np.int64), fz[:, 1]
        self.fcs = np.r_[0.0, np.cumsum(self.fr)]
        self.slip = 2e-4 if sym.startswith("SOL") else 1e-4

    def atr_at(self, minute):
        """Mean TR of the 14 kline days before the UTC day of minute (needs 14 such days)."""
        i = np.searchsorted(self.ud, minute // 1440)  # number of kline days before that day
        if i < 14:
            return np.nan
        return (self.cs_tr[i] - self.cs_tr[i - 14]) / 14.0

    def spans_hole(self, a, b):
        """True if a hole (> 30 min without trades) overlaps [a, b] (epoch minutes)."""
        i = np.searchsorted(self.hs, b, "left")
        return i > 0 and self.he[i - 1] > a

    def rp(self, row, high=False):
        return float(np.exp((row + (1 if high else 0)) * self.k / 1e4))


# ---------------------------------------------------------------- legs
def trend_legs(d):
    bs, bo, bc = d.bs, d.bo, d.bc
    n = len(bs)
    up = (bc > bo).astype(int)
    dn = (bc < bo).astype(int)
    cu, cd = np.r_[0, np.cumsum(up)], np.r_[0, np.cumsum(dn)]
    legs = []
    i0 = 0
    while i0 + 7 < n:
        j = i0 + 7
        if bs[j] - bs[i0] == 210:
            a = d.atr_at(bs[j])
            if a == a:
                disp = bc[j] - bo[i0]
                if abs(disp) >= 0.5 * a:
                    s = 1 if disp > 0 else -1
                    cnt = (cu[j + 1] - cu[i0]) if s > 0 else (cd[j + 1] - cd[i0])
                    if cnt >= 6:
                        legs.append((i0, j, s))
                        i0 = j + 1
                        continue
        i0 += 1
    return legs


def rejection_legs(d):
    bs, bh, bl, bc = d.bs, d.bh, d.bl, d.bc
    n = len(bs)
    legs = []
    last_e = -1
    for e in range(6, n):
        found = []
        a = None
        # bullish: drop then up
        L = e - 3 + int(np.argmin(bl[e - 3:e]))
        if L > last_e and L - 3 >= 0 and bl[e] > bl[L] and bs[e] - bs[L - 3] == 30 * (e - L + 3):
            a = d.atr_at(bs[e])
            if a == a and bh[L - 3:L + 1].max() - bl[L] >= 0.4 * a and bc[e] - bl[L] >= 0.4 * a:
                found.append((L, e, 1))
        # bearish: rally then down
        H = e - 3 + int(np.argmax(bh[e - 3:e]))
        if H > last_e and H - 3 >= 0 and bh[e] < bh[H] and bs[e] - bs[H - 3] == 30 * (e - H + 3):
            if a is None:
                a = d.atr_at(bs[e])
            if a == a and bh[H] - bl[H - 3:H + 1].min() >= 0.4 * a and bh[H] - bc[e] >= 0.4 * a:
                found.append((H, e, -1))
        if found:
            legs.extend(found)
            last_e = e
    return legs


def profile(d, a, b):
    s, e = d.ptr[a], d.ptr[b + 1]
    rows, vol = d.row[s:e], d.vol[s:e]
    r0, r1 = rows.min(), rows.max()
    return r0, np.bincount(rows - r0, weights=vol, minlength=r1 - r0 + 1)


def zones_from_legs(d, legs, c):
    """Zones: (formation bar j, low row, high row, side). Returns zones and counts."""
    out, cnt = [], {"legs": len(legs), "no_cluster": 0, "extreme": 0}
    for a, b, s in legs:
        r0, pr = profile(d, a, b)
        med = np.median(pr)
        im = int(np.argmax(pr))
        if pr[im] < c * med:
            cnt["no_cluster"] += 1
            continue
        thr = c * med
        lo = hi = im
        while lo - 1 >= 0 and pr[lo - 1] >= thr:
            lo -= 1
        while hi + 1 < len(pr) and pr[hi + 1] >= thr:
            hi += 1
        if lo == 0 or hi == len(pr) - 1:
            cnt["extreme"] += 1
            continue
        out.append((b, r0 + lo, r0 + hi, s, a))
    cnt["zones"] = len(out)
    return out, cnt


# ---------------------------------------------------------------- random zones
def random_zones(d, zones, rng):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    if not hasattr(d, "_r48"):
        lo = np.full(len(d.bs), np.iinfo(np.int64).max)
        hi = np.full(len(d.bs), np.iinfo(np.int64).min)
        lo[47:] = sw(d.rmin, 48).min(axis=1)
        hi[47:] = sw(d.rmax, 48).max(axis=1)
        d._r48 = (lo, hi)
    R0, R1 = d._r48
    out = []
    for j, zl, zh, s, a0 in zones:
        if j < 47:
            continue
        a, b = R0[j], R1[j]
        w = zh - zl + 1
        lo_in, hi_in = max(zl, a), min(zh, b)
        excl = max(0, hi_in - lo_in + 1)
        cnt = (b - a + 1) - excl
        if cnt <= 0:
            continue
        u = int(rng.integers(cnt))
        x = a + u
        if excl > 0 and x >= lo_in:
            x += excl
        rl = x - (w - 1) // 2
        out.append((j, rl, rl + w - 1, s, a0))
    return out


# ---------------------------------------------------------------- tests
def first_tests(d, zones, drops=None):
    """Per zone: (minute index of first test, filled?, entry price, side, formation bar). Untested zones dropped, and
    zones whose life (leg start .. test minute + 24 h) overlaps a hole > 30 min are dropped (counted in drops)."""
    res = []
    bs, bh, bl = d.bs, d.bh, d.bl
    for j, zl, zh, s, a0 in zones:
        lo_p, hi_p = d.rp(zl), d.rp(zh, high=True)
        fc = bs[j] + 30
        jend = np.searchsorted(bs, fc + EXPIRY - 30, "right")
        if s > 0:
            beyond = np.flatnonzero(bl[j + 1:jend] > hi_p)
        else:
            beyond = np.flatnonzero(bh[j + 1:jend] < lo_p)
        if len(beyond) < 2:
            continue
        usable = bs[j + 1 + beyond[1]] + 30
        i0 = np.searchsorted(d.mn, usable)
        i1 = np.searchsorted(d.mn, fc + EXPIRY)
        if i1 <= i0:
            continue
        if s > 0:
            hit = np.flatnonzero(d.ml[i0:i1] <= hi_p)
        else:
            hit = np.flatnonzero(d.mh[i0:i1] >= lo_p)
        if len(hit) == 0:
            continue
        i = i0 + hit[0]
        if d.spans_hole(bs[a0], d.mn[i] + HOLD_T):
            if drops is not None:
                drops.append(j)
            continue
        if s > 0:
            ent, filled = hi_p, d.ml[i] <= hi_p * (1 - 1e-4)
        else:
            ent, filled = lo_p, d.mh[i] >= lo_p * (1 + 1e-4)
        res.append((i, bool(filled), ent, s, j))
    res.sort(key=lambda r: (r[0], r[4]))
    return res


# ---------------------------------------------------------------- trades
def tp_price(d, E, D, s, t0, mode):
    if mode == "2R":
        return E + s * 2 * D
    jb = np.searchsorted(d.bs, t0 - 30, "right")
    rows = d.poc[max(0, jb - 48):jb]
    if s > 0:
        tp = np.exp((rows - 1) * d.k / 1e4)
        ok = tp[(tp >= E + D) & (tp <= E + 3 * D)]
        return ok.min() if len(ok) else E + 2 * D
    tp = np.exp((rows + 2) * d.k / 1e4)
    ok = tp[(tp <= E - D) & (tp >= E - 3 * D)]
    return ok.max() if len(ok) else E - 2 * D


def simulate(d, tests, mode, late=False):
    """Returns array rows: entry minute, net bp, fees bp, R bp, exit kind (0 stop, 1 tp, 2 time)."""
    out = []
    busy = -1
    lastmin = d.mn[-1]
    mn, mo, mh, ml, mc = d.mn, d.mo, d.mh, d.ml, d.mc
    for i, filled, ent, s, j in tests:
        if not filled or mn[i] <= busy:
            continue
        t0 = mn[i]
        if t0 + HOLD_T > lastmin:
            continue
        a = d.atr_at(t0)
        if a != a:
            continue
        D = 0.15 * a
        if late:
            E, fee_in, start = mc[i], 5.0, i + 1
        else:
            E, fee_in, start = ent, 2.0, i + 1
        stop = E - s * D
        tp = tp_price(d, E, D, s, t0, mode)
        iend = np.searchsorted(mn, t0 + HOLD_T, "right") - 1
        kind = None
        if not late:
            if (s > 0 and ml[i] <= stop) or (s < 0 and mh[i] >= stop):
                X, kind, xi = stop * (1 - s * d.slip), 0, i
        if kind is None:
            seg_l, seg_h = ml[start:iend + 1], mh[start:iend + 1]
            if s > 0:
                hs, ht = np.flatnonzero(seg_l <= stop), np.flatnonzero(seg_h > tp)
            else:
                hs, ht = np.flatnonzero(seg_h >= stop), np.flatnonzero(seg_l < tp)
            ks = hs[0] if len(hs) else 10 ** 9
            kt = ht[0] if len(ht) else 10 ** 9
            if ks <= kt and ks < 10 ** 9:
                xi = start + ks
                px = min(stop, mo[xi]) if s > 0 else max(stop, mo[xi])
                X, kind = px * (1 - s * d.slip), 0
            elif kt < 10 ** 9:
                xi = start + kt
                X, kind = tp, 1
            else:
                xi = iend
                X, kind = mc[iend], 2
        fee_out = 2.0 if kind == 1 else 5.0
        a0 = np.searchsorted(d.fs, t0 * 60, "right")
        a1 = np.searchsorted(d.fs, mn[xi] * 60, "right")
        fund = s * (d.fcs[a1] - d.fcs[a0]) * 1e4
        gross = s * (X / E - 1) * 1e4
        fees = fee_in + fee_out
        out.append((t0, gross - fees - fund, fees, D / E * 1e4, kind))
        busy = mn[xi]
    return np.array(out, dtype=float).reshape(-1, 5)


def run(sym, n_draws):
    t = time.time()
    d = Data(sym)
    legs = {"trend": trend_legs(d), "rej": rejection_legs(d)}
    print(sym, "legs", {k: len(v) for k, v in legs.items()}, round(time.time() - t, 1), flush=True)
    real, counts = {}, {}
    zsets = {}
    for st in SETUPS:
        for c in CS:
            z, cnt = zones_from_legs(d, legs[st], c)
            zsets[(st, c)] = z
            drops = []
            tests = first_tests(d, z, drops)
            cnt["hole_dropped"] = len(drops)
            cnt["tested"] = len(tests)
            cnt["filled"] = int(sum(r[1] for r in tests))
            counts[f"{st}_c{c}"] = cnt
            for tpm in TPS:
                real[f"{st}_c{c}_{tpm}"] = simulate(d, tests, tpm)
                real[f"{st}_c{c}_{tpm}_late"] = simulate(d, tests, tpm, late=True)
    print(sym, "real done", counts, round(time.time() - t, 1), flush=True)
    np.savez(os.path.join(OUT, f"{sym}_real.npz"), **real)
    with open(os.path.join(OUT, f"{sym}_counts.json"), "w") as fh:
        json.dump(counts, fh, indent=1)
    if n_draws <= 0:
        return
    seed = {"BTCUSDT": 7501, "ETHUSDT": 7502, "SOLUSDT": 7503}[sym]
    rng = np.random.default_rng(seed)
    rand = {}
    for dr in range(n_draws):
        for st in SETUPS:
            for c in CS:
                rz = random_zones(d, zsets[(st, c)], rng)
                tests = first_tests(d, rz)
                for tpm in TPS:
                    tr = simulate(d, tests, tpm)
                    rand.setdefault(f"{st}_c{c}_{tpm}", []).append(np.c_[np.full(len(tr), dr), tr[:, :2]])
        if dr % 20 == 19:
            print(sym, "draw", dr + 1, round(time.time() - t, 1), flush=True)
    np.savez(os.path.join(OUT, f"{sym}_rand.npz"), **{k: np.concatenate(v) for k, v in rand.items()})
    print(sym, "done", round(time.time() - t, 1), flush=True)


if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 200)
