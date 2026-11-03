"""Round 75 stream TF: trades filter zones, first-retest engine (rules in ../HYPOTHESES_TF.md).

Usage: research/.venv/bin/python -I tf.py SYM [draws]
Writes ../out/<SYM>_trades.npz: per cell (R x TP) the real trades and the trades of each random draw, after the
one-open-trade rule (separately for base / late execution). No statistics here (see stats.py).
"""
import calendar
import importlib.util
import os
import sys
import time
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FP_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "coord", "code", "fp.py"))
spec = importlib.util.spec_from_file_location("fp", FP_PATH)
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)

ROOT = fp.ROOT
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
HOLD_MS = fp.HOLD_MIN * 60000
VAL_LAST_FILL_MIN = (1735689600 - 86400) // 60  # fills must start before 2024-12-31 00:00 UTC
EXPIRY_BARS = 336
STOP_ATR = 0.15
MAKER, TAKER = 2.0, 5.0
RS = (5, 10)
TPS = ("TPV", "2R")
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Data:
    def __init__(self, sym):
        self.sym = sym
        self.slip = 2.0 if sym == "SOLUSDT" else 1.0
        m = fp.load_minutes(sym)
        self.t0 = int(m["min"][0] // 30 * 30)
        n = int(m["min"][-1] - self.t0 + 1)
        n = (n + 29) // 30 * 30
        idx = (m["min"] - self.t0).astype(np.int64)
        self.N = n
        for k in ("o", "h", "l", "c"):
            a = np.full(n + 1440 * 2, np.nan)
            a[idx] = m[k]
            setattr(self, k, a)
        valid = np.zeros(n + 2880, bool)
        valid[idx] = True
        # last valid minute index <= i (for the time stop)
        pos = np.where(valid, np.arange(len(valid)), -1)
        self.lastvalid = np.maximum.accumulate(pos)
        self.H30 = np.nanmax(self.h[:n].reshape(-1, 30), axis=1)
        self.L30 = np.nanmin(self.l[:n].reshape(-1, 30), axis=1)
        self.nb = len(self.H30)
        # holes: runs of > 30 missing minutes (Binance monthly files skip days); flagged per minute index
        gap = np.diff(m["min"])
        hs = np.flatnonzero(gap > 31)  # > 30 missing minutes between two present minutes
        hole = np.zeros(n + 2880, np.int64)
        self.holes = []
        for i in hs:
            s0, s1 = int(m["min"][i] + 1 - self.t0), int(m["min"][i + 1] - self.t0)
            hole[s0:s1] = 1
            self.holes.append((int(m["min"][i] + 1), int(gap[i] - 1)))
        self.hole_cs = np.r_[0, np.cumsum(hole)]
        # minutes present per calendar month (for Q: "R per day" over the days actually present)
        mon = np.array([time.gmtime(int(x) * 60).tm_year * 100 + time.gmtime(int(x) * 60).tm_mon
                        for x in range(int(m["min"][0]) // 1440 * 1440, int(m["min"][-1]) + 1, 1440)])
        dstart = np.arange(int(m["min"][0]) // 1440 * 1440, int(m["min"][-1]) + 1, 1440)
        dm = mon[np.searchsorted(dstart, m["min"], side="right") - 1]
        um, cnt = np.unique(dm, return_counts=True)
        self.present_days = {int(u): c / 1440.0 for u, c in zip(um, cnt)}
        # daily ATR14 from perp_1d klines (UTC days), cut before HOLD on read
        kz = np.genfromtxt(os.path.join(ROOT, "research", "data", "binance", "perp_1d", sym + ".csv"), delimiter=",",
                           skip_header=1)
        kz = kz[kz[:, 0] < HOLD_MS]
        day = (kz[:, 0] // 86400000).astype(np.int64)
        D0 = int(day[0])
        nd = int(day[-1] - D0 + 1)
        H = np.full(nd, np.nan); L = np.full(nd, np.nan); C = np.full(nd, np.nan)
        H[day - D0], L[day - D0], C[day - D0] = kz[:, 2], kz[:, 3], kz[:, 4]
        pc = np.r_[np.nan, C[:-1]]
        tr = np.fmax(H, pc) - np.fmin(L, pc)
        tr[0] = H[0] - L[0]
        cs = np.r_[0.0, np.cumsum(np.nan_to_num(tr))]
        cnt = np.r_[0, np.cumsum(np.isfinite(tr))]
        atr = np.full(nd + 1, np.nan)
        for Dd in range(14, nd + 1):
            if cnt[Dd] - cnt[Dd - 14] == 14:
                atr[Dd] = (cs[Dd] - cs[Dd - 14]) / 14.0
        self.D0, self.atr = D0, atr
        del m
        # footprint k and POC per 30m bar
        f = fp.load_fp(sym, 30)
        self.k = f["k"]
        bs, pr = fp.poc(f)
        self.poc = np.full(self.nb + 100, -1, np.int64)
        bi = (bs - self.t0) // 30
        ok = (bi >= 0) & (bi < self.nb)
        self.poc[bi[ok]] = pr[ok]
        del f
        # rows of the 30m bar extremes (for the random benchmark range)
        k = self.k
        self.rowH = np.floor(np.floor(1e4 * np.log(self.H30)) / k)
        self.rowL = np.floor(np.floor(1e4 * np.log(self.L30)) / k)
        # funding (cut before HOLD on read)
        fz = np.genfromtxt(os.path.join(ROOT, "research", "data", "binance", "funding", sym + ".csv"), delimiter=",",
                           skip_header=1)
        fz = fz[fz[:, 0] < HOLD_MS]
        self.fund_t = fz[:, 0]
        self.fund_cs = np.r_[0.0, np.cumsum(fz[:, 1])]
        # big trades
        self.big = load_big_q(sym, self.present_days)

    def funding(self, f_abs_min, x_abs_min):
        a = np.searchsorted(self.fund_t, f_abs_min * 60000.0, side="right")
        b = np.searchsorted(self.fund_t, x_abs_min * 60000.0, side="right")
        return self.fund_cs[b] - self.fund_cs[a]


def load_big_q(sym, present_days):
    """Big trades per R with the monthly point-in-time Q (N-th largest notional of the previous month, N = R x days,
    floor $100k = the cache's own threshold). Reads the same arrays as fp.load_big, month by month with its HOLD cut,
    so that the ~34M stored BTC trades never sit in memory at once."""
    out = {R: {"ts": [], "p": [], "side": [], "q": {}, "floors": []} for R in RS}
    prev = None
    for path in fp._months(sym):
        mo = os.path.basename(path)[:7]
        z = np.load(path)
        ts, p, q, s = z["big_ts"], z["big_p"], z["big_q"], z["big_side"]
        keep = ts < HOLD_MS
        ts, p, s, notional = ts[keep], p[keep], s[keep], (p * q)[keep]
        y, m = map(int, mo.split("-"))
        if prev is not None and prev[0] == ((y - 1, 12) if m == 1 else (y, m - 1)):
            (py, pm), pn = prev
            for R in RS:
                N = int(round(R * present_days.get(py * 100 + pm, calendar.monthrange(py, pm)[1])))
                if len(pn) >= N:
                    Q = float(pn[N - 1])
                else:
                    Q = 100_000.0
                    out[R]["floors"].append(mo)
                out[R]["q"][mo] = Q
                kk = notional >= Q
                out[R]["ts"].append(ts[kk]); out[R]["p"].append(p[kk]); out[R]["side"].append(s[kk])
        prev = ((y, m), np.sort(notional)[::-1])
    for R in RS:
        for f in ("ts", "p", "side"):
            out[R][f] = np.concatenate(out[R][f])
    return out


def make_zones(D, R):
    B = D.big[R]
    ts, p, side = B["ts"], B["p"], B["side"]
    q, floors = B["q"], B["floors"]
    absmin = ts // 60000
    bar = (absmin - D.t0) // 30
    row = np.floor(np.floor(1e4 * np.log(p)) / D.k).astype(np.int64)
    o = np.lexsort((row, bar))
    bar, row, side = bar[o], row[o], side[o]
    # merge: same bar, rows adjacent (gap <= 1)
    newz = np.r_[True, (bar[1:] != bar[:-1]) | (row[1:] - row[:-1] > 1)]
    zid = np.cumsum(newz) - 1
    first = np.flatnonzero(newz)
    zb = bar[first]
    zlo = np.minimum.reduceat(row, first)
    zhi = np.maximum.reduceat(row, first)
    nbuy = np.add.reduceat((side > 0).astype(np.int64), first)
    nsell = np.add.reduceat((side < 0).astype(np.int64), first)
    del zid
    return {"bar": zb, "lo": zlo, "hi": zhi, "nbuy": nbuy, "nsell": nsell, "q": q, "floors": floors,
            "nbig": int(len(ts))}


def random_zones(D, Z, rng):
    j = Z["bar"]
    w = Z["hi"] - Z["lo"] + 1
    lo48 = np.full(len(j), np.inf)
    hi48 = np.full(len(j), -np.inf)
    for s in range(48):
        jj = j - s
        okj = jj >= 0
        v = np.where(okj, D.rowL[np.clip(jj, 0, None)], np.nan)
        lo48 = np.fmin(lo48, v)
        v = np.where(okj, D.rowH[np.clip(jj, 0, None)], np.nan)
        hi48 = np.fmax(hi48, v)
    rl = np.minimum(lo48, Z["lo"]).astype(np.int64)
    rh = np.maximum(hi48, Z["hi"]).astype(np.int64)
    nel = (rh - rl + 1) - w
    ok = nel > 0
    u = np.floor(rng.random(len(j)) * np.maximum(nel, 1)).astype(np.int64)
    c = rl + u
    c = np.where(c >= Z["lo"], c + w, c)
    lo = c - (w - 1) // 2
    out = {"bar": j[ok], "lo": lo[ok], "hi": (lo + w - 1)[ok], "nbuy": Z["nbuy"][ok], "nsell": Z["nsell"][ok]}
    return out


def tests(D, Z):
    """Departure and first test. Returns per zone: dir (+1 support / -1 resistance / 0 none), test minute index,
    filled flag, entry price."""
    k = D.k
    lo_p = np.exp(Z["lo"] * k / 1e4)
    hi_p = np.exp((Z["hi"] + 1) * k / 1e4)
    j = Z["bar"]
    n = len(j)
    dirn = np.zeros(n, np.int64)
    tmin = np.full(n, -1, np.int64)
    filled = np.zeros(n, bool)
    entry = np.full(n, np.nan)
    departed = np.zeros(n, bool)
    off = np.arange(1, EXPIRY_BARS + 1)
    CH = 4000
    for a in range(0, n, CH):
        sl = slice(a, a + CH)
        jj = j[sl][:, None] + off[None, :]
        inside = jj < D.nb
        jc = np.clip(jj, 0, D.nb - 1)
        Lw = np.where(inside, D.L30[jc], np.nan)
        Hw = np.where(inside, D.H30[jc], np.nan)
        hp, lp = hi_p[sl][:, None], lo_p[sl][:, None]
        up = np.cumsum(Lw > hp, axis=1)
        dn = np.cumsum(Hw < lp, axis=1)
        BIG = 10 ** 6
        iu = np.where((up >= 2).any(1), np.argmax(up >= 2, 1), BIG)
        idn = np.where((dn >= 2).any(1), np.argmax(dn >= 2, 1), BIG)
        dep = np.minimum(iu, idn)
        d = np.where(dep == BIG, 0, np.where(iu < idn, 1, -1))
        # first 30m bar after the departure bar (within expiry) that reaches the near edge
        after = off[None, :] > (dep[:, None] + 1)  # bar offsets strictly after departure bar offset (dep is 0-based)
        touch = np.where(d[:, None] > 0, Lw <= hp, Hw >= lp) & after
        has = touch.any(1) & (d != 0)
        departed[sl] = d != 0
        tb = np.argmax(touch, 1)
        rows = np.flatnonzero(has)
        for r in rows:
            zi = a + r
            bidx = j[zi] + off[tb[r]]
            m0 = bidx * 30
            if d[r] > 0:
                ll = D.l[m0:m0 + 30]
                hit = np.flatnonzero(ll <= hi_p[zi])
                mi = m0 + hit[0]
                fl = D.l[mi] <= hi_p[zi] * (1 - 1e-4)
                e = hi_p[zi]
            else:
                hh = D.h[m0:m0 + 30]
                hit = np.flatnonzero(hh >= lo_p[zi])
                mi = m0 + hit[0]
                fl = D.h[mi] >= lo_p[zi] * (1 + 1e-4)
                e = lo_p[zi]
            dirn[zi], tmin[zi], filled[zi], entry[zi] = d[r], mi, fl, e
    tests.departed = departed
    return dirn, tmin, filled, entry


def execute(D, dirn, tmin, entry, zbar_order):
    """Candidate trades (filled tests) -> both TP cells, base / stress / late. Returns dict of arrays per cell."""
    n = len(tmin)
    absf = D.t0 + tmin
    day = absf // 1440
    atr = D.atr[np.clip(day - D.D0, 0, len(D.atr) - 1)]
    ok = np.isfinite(atr) & (absf < VAL_LAST_FILL_MIN)
    idx = np.flatnonzero(ok)
    dirn, tmin, entry, atr, zbar_order = dirn[idx], tmin[idx], entry[idx], atr[idx], zbar_order[idx]
    n = len(idx)
    dist = STOP_ATR * atr
    stop = entry - dirn * dist
    k = D.k
    # TPV targets
    jf = tmin // 30
    P = np.stack([D.poc[np.clip(jf - s, 0, None)] for s in range(1, 49)], 1).astype(float)
    P[P < 0] = np.nan
    lowedge = np.exp(P * k / 1e4)
    highedge = np.exp((P + 1) * k / 1e4)
    E, Rr = entry[:, None], dist[:, None]
    cand_l = np.where(lowedge > E + Rr, P, np.inf).min(1)
    cand_s = np.where(highedge < E - Rr, P, -np.inf).max(1)
    tp2 = entry + dirn * 2 * dist
    tpv = tp2.copy()
    lg = dirn > 0
    okl = lg & np.isfinite(cand_l)
    okl &= np.exp(np.where(okl, cand_l, 0) * k / 1e4) <= entry + 3 * dist
    tpv[okl] = np.exp((cand_l[okl] - 1) * k / 1e4)
    oks = (~lg) & np.isfinite(cand_s)
    oks &= np.exp((np.where(oks, cand_s, 0) + 1) * k / 1e4) >= entry - 3 * dist
    tpv[oks] = np.exp((cand_s[oks] + 2) * k / 1e4)
    res = {}
    W = 1440
    offs = np.arange(W)
    for tpname, tp in (("TPV", tpv), ("2R", tp2)):
        out = {}
        for mode in ("base", "late"):
            xmin = np.zeros(n, np.int64)
            xpx = np.zeros(n)
            kind = np.zeros(n, np.int64)  # 0 time, 1 stop, 2 tp
            if mode == "base":
                ent = entry.copy()
            else:
                ent = D.c[tmin]
            CH = 3000
            for a in range(0, n, CH):
                sl = slice(a, a + CH)
                mi = tmin[sl][:, None] + offs[None, :]
                lw, hw, ow = D.l[mi], D.h[mi], D.o[mi]
                dd = dirn[sl][:, None]
                st, tt = stop[sl][:, None], tp[sl][:, None]
                sh = np.where(dd > 0, lw <= st, hw >= st)
                th = np.where(dd > 0, hw > tt, lw < tt)
                th[:, 0] = False
                if mode == "late":
                    sh[:, 0] = False
                isS = sh.any(1)
                isT = th.any(1)
                fs = np.where(isS, np.argmax(sh, 1), W)
                ft = np.where(isT, np.argmax(th, 1), W)
                rr = np.arange(fs.shape[0])
                kk = np.where((fs <= ft) & (fs < W), 1, np.where(ft < W, 2, 0))
                xi = np.where(kk == 1, fs, np.where(kk == 2, ft, W - 1))
                # stop fill: stop or gap open (not in the base fill minute), then slippage
                og = ow[rr, np.minimum(xi, W - 1)]
                s1 = stop[sl]
                d1 = dirn[sl]
                gap = np.where(d1 > 0, og < s1, og > s1) & (xi > 0)
                spx = np.where(gap, og, s1) * (1 - d1 * D.slip / 1e4)
                tlast = D.lastvalid[tmin[sl] + W - 1]
                tpx = D.c[tlast]
                px = np.where(kk == 1, spx, np.where(kk == 2, tp[sl], tpx))
                xm = np.where(kk == 0, tlast, tmin[sl] + xi)
                xmin[sl], xpx[sl], kind[sl] = xm, px, kk
            gross = dirn * (xpx / ent - 1) * 1e4
            fund = dirn * D.funding(D.t0 + tmin, D.t0 + xmin) * 1e4
            efee = MAKER if mode == "base" else TAKER
            xfee = np.where(kind == 2, MAKER, TAKER)
            net = gross - efee - xfee - fund
            out[mode] = {"xmin": xmin, "net": net, "fee": efee + xfee, "kind": kind}
        res[tpname] = out
    common = {"tmin": tmin, "dirn": dirn, "rbp": dist / entry * 1e4, "order": zbar_order, "idx": idx}
    return res, common


def one_open(tmin, xmin, order):
    o = np.lexsort((order, tmin))
    keep = np.zeros(len(tmin), bool)
    last = -1
    for i in o:
        if tmin[i] > last:
            keep[i] = True
            last = xmin[i]
    return keep


def run_set(D, Z):
    """Real or random zones -> per TP cell, trades after the one-open rule (base, stress share base set)."""
    dirn, tmin, filled, entry = tests(D, Z)
    sel = np.flatnonzero((dirn != 0) & filled)
    res, com = execute(D, dirn[sel], tmin[sel], entry[sel], Z["bar"][sel])
    # zone life (formation bar start .. exit) must not span a hole > 30 min; checked per execution mode
    zstart = Z["bar"][sel][com["idx"]] * 30
    zsel = sel[com["idx"]]
    out = {}
    for tpname in TPS:
        r = res[tpname]
        for mode in ("base", "late"):
            clean = D.hole_cs[r[mode]["xmin"] + 1] - D.hole_cs[zstart] == 0
            keep = np.zeros(len(clean), bool)
            ci = np.flatnonzero(clean)
            keep[ci] = one_open(com["tmin"][ci], r[mode]["xmin"][ci], com["order"][ci])
            dropped = int((~clean).sum())
            ii = np.flatnonzero(keep)
            rec = {"fmin": D.t0 + com["tmin"][ii], "net": r[mode]["net"][ii], "rbp": com["rbp"][ii],
                   "dirn": com["dirn"][ii], "fee": r[mode]["fee"][ii], "kind": r[mode]["kind"][ii],
                   "nbuy": Z["nbuy"][zsel[ii]], "nsell": Z["nsell"][zsel[ii]]}
            rec["dropped_hole"] = np.array([dropped])
            out[(tpname, mode)] = rec
    info = {"zones": len(Z["bar"]), "departed": int(tests.departed.sum()),
            "tested": int((tmin >= 0).sum()), "filled": int(len(sel)), "candidates": int(len(com["tmin"]))}
    return out, info


def main():
    sym = sys.argv[1]
    draws = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    t0 = time.time()
    D = Data(sym)
    print(f"{sym} loaded {time.time() - t0:.0f}s k={D.k} minutes={D.N}", flush=True)
    store = {}
    meta = [f"holes > 30 min: {len(D.holes)}, {sum(h[1] for h in D.holes) / 60:.0f} h: " +
            ", ".join(f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(s * 60))} +{l / 60:.1f}h" for s, l in D.holes),
            "present days per month: " + " ".join(f"{k}:{v:.2f}" for k, v in sorted(D.present_days.items()))]
    for R in RS:
        Z = make_zones(D, R)
        meta.append(f"R={R} big={Z['nbig']} zones={len(Z['bar'])} floors={Z['floors']}")
        qs = " ".join(f"{m}:{v / 1e3:.0f}k" for m, v in sorted(Z["q"].items()))
        meta.append(f"R={R} Q " + qs)
        real, info = run_set(D, Z)
        meta.append(f"R={R} real {info} dropped_hole " + str({k: int(v["dropped_hole"][0]) for k, v in real.items()}))
        print(meta[0][:200], "\n", meta[-3], "\n", meta[-1], f"{time.time() - t0:.0f}s", flush=True)
        for (tpname, mode), rec in real.items():
            for f, v in rec.items():
                store[f"R{R}_{tpname}_{mode}_real_{f}"] = v
        rng = np.random.default_rng(7500 + R + 1000 * ("BTC", "ETH", "SOL").index(sym[:3]))
        for dr in range(draws):
            RZ = random_zones(D, Z, rng)
            rnd, rinfo = run_set(D, RZ)
            for (tpname, mode), rec in rnd.items():
                for f in ("fmin", "net", "fee", "rbp"):
                    store[f"R{R}_{tpname}_{mode}_d{dr}_{f}"] = rec[f]
            if dr % 20 == 0:
                print(f"R={R} draw {dr} {rinfo} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(OUT, exist_ok=True)
    np.savez_compressed(os.path.join(OUT, f"{sym}_trades.npz"), **store)
    with open(os.path.join(OUT, f"{sym}_meta.txt"), "w") as f:
        f.write("\n".join(meta) + "\n")
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
