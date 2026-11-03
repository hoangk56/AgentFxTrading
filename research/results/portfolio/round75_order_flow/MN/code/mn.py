"""Round 75 stream MN: multiple nodes (POC of >= n consecutive 30m bars in one row), first-retest trades.

Usage: python -I mn.py run <SYM> [draws]   -> out/<SYM>_real.npz, out/<SYM>_rand.npz
Rules: ../HYPOTHESES_MN.md. One symbol per process (memory ~1 GB).
"""
import importlib.util
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STREAM = os.path.dirname(HERE)
OUT = os.path.join(STREAM, "out")
_spec = importlib.util.spec_from_file_location("fp", os.path.join(STREAM, "..", "coord", "code", "fp.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)
REPO = fp.ROOT
HOLD_MIN = fp.HOLD_MIN
IS_END_MIN = fp.IS_END_MIN

NS = (2, 3)
TPS = ("TPV", "2R")
EXPIRY_BARS = 336
STOP_ATR = 0.15
MAKER, TAKER = 2.0, 5.0
SLIP = {"BTCUSDT": 1.0, "ETHUSDT": 1.0, "SOLUSDT": 2.0}
LMIN, LBAR = 11, 10  # binary-lifting levels: 2047 minutes, 1023 bars


# ---------- sparse tables + first-hit search ----------
def build_st(a, levels, fn, pad):
    n = len(a)
    p = n + 2 ** levels
    t0 = np.full(p, pad, dtype=np.float64)
    t0[:n] = a
    st = [t0]
    for j in range(1, levels):
        h = 2 ** (j - 1)
        prev = st[-1]
        nxt = prev.copy()
        nxt[: p - h] = fn(prev[: p - h], prev[h:])
        st.append(nxt)
    return st


def first_hit(st, start, thr, nohit):
    """Smallest idx >= start whose value is a hit; nohit(block_value, thr) is True when no element of the block hits.
    Padding values are hits, so the result is <= len(a). Caller must verify the hit (range 2^levels - 1)."""
    pos = start.astype(np.int64).copy()
    for j in range(len(st) - 1, -1, -1):
        v = st[j][pos]
        pos += nohit(v, thr) * (2 ** j)
    return pos


def gt(v, t):
    return v > t


def ge(v, t):
    return v >= t


def lt(v, t):
    return v < t


def le(v, t):
    return v <= t


# ---------- data ----------
class Sym:
    def __init__(self, sym):
        t0 = time.time()
        self.sym = sym
        m = fp.load_minutes(sym)
        self.mmin = m["min"]
        self.o, self.h, self.l, self.c = m["o"], m["h"], m["l"], m["c"]
        b = fp.bars(m, 30)
        del m
        self.bstart, self.bh, self.bl = b["start"], b["h"], b["l"]
        self.bfirst = np.searchsorted(self.mmin, self.bstart)  # first minute index of each bar
        f = fp.load_fp(sym, 30)
        self.k = f["k"]
        pb, pr = fp.poc(f)
        del f
        idx = np.searchsorted(self.bstart, pb)
        ok = (idx < len(self.bstart)) & (self.bstart[np.minimum(idx, len(self.bstart) - 1)] == pb)
        self.poc = np.full(len(self.bstart), -1, dtype=np.int64)
        self.poc[idx[ok]] = pr[ok]
        self.poc_mismatch = int((~ok).sum()) + int((self.poc < 0).sum())
        # POC row must lie inside the bar's [low, high] rows (guards against a broken footprint)
        okp = self.poc >= 0
        rl, rh = self.row_of(self.bl), self.row_of(self.bh)
        badp = okp & ((self.poc < rl) | (self.poc > rh))
        assert badp.sum() <= 0.001 * okp.sum(), f"POC outside bar range in {badp.sum()} bars"
        self.poc_outside = int(badp.sum())
        # daily ATR14 from the daily klines (complete; cut at HOLD)
        z = np.genfromtxt(os.path.join(REPO, "research", "data", "binance", "perp_1d", sym + ".csv"),
                          delimiter=",", skip_header=1)
        z = z[z[:, 0] < HOLD_MIN * 60000]
        ud = (z[:, 0] // 86400000).astype(np.int64)
        dh, dl, dc = z[:, 2], z[:, 3], z[:, 4]
        pc = np.r_[np.nan, dc[:-1]]
        prev_ok = np.r_[False, np.diff(ud) == 1]
        tr = np.where(prev_ok, np.maximum(dh, pc) - np.minimum(dl, pc), dh - dl)
        d0 = ud[0]
        trd = np.full(ud[-1] - d0 + 1, np.nan)
        trd[ud - d0] = tr
        cs = np.r_[0.0, np.cumsum(np.nan_to_num(trd))]
        cn = np.r_[0, np.cumsum(~np.isnan(trd))]
        nd = len(trd)
        atr = np.full(nd + 1, np.nan)
        j = np.arange(14, nd + 1)
        full = (cn[j] - cn[j - 14]) == 14
        atr[j[full]] = (cs[j] - cs[j - 14])[full] / 14.0
        self.d0, self.atr = d0, atr
        # 1m data gaps > 30 minutes: gcum[j] = number of gaps between minute 0 and minute j
        gap = np.r_[False, np.diff(self.mmin) > 30]
        self.gcum = np.cumsum(gap)
        # funding (cut at HOLD)
        z = np.genfromtxt(os.path.join(REPO, "research", "data", "binance", "funding", sym + ".csv"),
                          delimiter=",", skip_header=1)
        z = z[z[:, 0] < HOLD_MIN * 60000]
        self.fmin = (z[:, 0] // 60000).astype(np.int64)
        self.fcum = np.r_[0.0, np.cumsum(z[:, 1])]
        # search tables
        self.st_ml = build_st(self.l, LMIN, np.minimum, -np.inf)  # minute: low <= x
        self.st_mh = build_st(self.h, LMIN, np.maximum, np.inf)  # minute: high >= / > x
        self.st_bl = build_st(self.bl, LBAR, np.minimum, -np.inf)  # bar: low <= x
        self.st_bh = build_st(self.bh, LBAR, np.maximum, np.inf)  # bar: high >= x
        self.st_blmax = build_st(self.bl, LBAR, np.maximum, np.inf)  # bar: low > x
        self.st_bhmin = build_st(self.bh, LBAR, np.minimum, -np.inf)  # bar: high < x
        # 48-bar rolling range rows for the random benchmark
        nb = len(self.bstart)
        lo48 = np.full(nb, np.nan)
        hi48 = np.full(nb, np.nan)
        from numpy.lib.stride_tricks import sliding_window_view as swv
        lo48[47:] = swv(self.bl, 48).min(axis=1)
        hi48[47:] = swv(self.bh, 48).max(axis=1)
        self.lo48, self.hi48 = lo48, hi48
        print(f"[{sym}] loaded {len(self.mmin):,} minutes, {nb:,} bars, k={self.k}, poc mismatch "
              f"{self.poc_mismatch}, poc outside bar {self.poc_outside}, {time.time() - t0:.0f}s", flush=True)

    def row_lo(self, r):
        return np.exp(r * self.k / 1e4)

    def row_of(self, p):
        return np.floor(1e4 * np.log(p)).astype(np.int64) // self.k


# ---------- zones ----------
def nodes(s, n):
    """Formation bar index and row of every multiple-node zone with run length n (one zone per run)."""
    p = s.poc
    same = (p[1:] == p[:-1]) & (p[1:] >= 0) & (np.diff(s.bstart) == 30)
    # run length ending at bar i
    rl = np.ones(len(p), dtype=np.int64)
    brk = np.r_[True, ~same]
    grp = np.cumsum(brk) - 1
    gstart = np.flatnonzero(brk)
    rl = np.arange(len(p)) - gstart[grp] + 1
    fb = np.flatnonzero((rl == n) & (p >= 0))
    return fb, p[fb]


def _verify(arr, idx, cond):
    n = len(arr)
    ok = idx < n
    safe = np.minimum(idx, n - 1)
    return ok & cond(arr[safe])


def zone_trades(s, fb, row, tag=None):
    """Departure, first test and fill. Returns dict of potential entries (only filled zones)."""
    nb = len(s.bstart)
    if tag is None:
        tag = np.zeros(len(fb), dtype=np.int64)
    lo = s.row_lo(row)
    hi = s.row_lo(row + 1)
    expiry = s.bstart[fb] + 30 + EXPIRY_BARS * 30
    BIG = np.int64(1 << 40)
    # support departure: bars with low > hi
    s1 = first_hit(s.st_blmax, fb + 1, hi, le)
    ok1 = _verify(s.bl, s1, lambda v: v > hi)
    s2 = first_hit(s.st_blmax, np.minimum(s1 + 1, nb), hi, le)
    ok2 = ok1 & _verify(s.bl, s2, lambda v: v > hi)
    sup = np.where(ok2, s2, BIG)
    # resistance departure: bars with high < lo
    r1 = first_hit(s.st_bhmin, fb + 1, lo, ge)
    ok1 = _verify(s.bh, r1, lambda v: v < lo)
    r2 = first_hit(s.st_bhmin, np.minimum(r1 + 1, nb), lo, ge)
    ok2 = ok1 & _verify(s.bh, r2, lambda v: v < lo)
    res = np.where(ok2, r2, BIG)
    u = np.minimum(sup, res)
    is_sup = sup < res
    valid = u < BIG
    us = np.minimum(u, nb - 1)
    valid &= (s.bstart[us] + 30) <= expiry
    idx = np.flatnonzero(valid)
    u, is_sup, lo, hi, expiry, fb_v, row_v = u[idx], is_sup[idx], lo[idx], hi[idx], expiry[idx], fb[idx], row[idx]
    tag_v = tag[idx]
    d = np.where(is_sup, 1, -1)
    edge = np.where(is_sup, hi, lo)
    # first test bar after u
    tb = np.where(is_sup, first_hit(s.st_bl, u + 1, edge, gt), first_hit(s.st_bh, u + 1, edge, lt))
    okt = np.where(is_sup, _verify(s.bl, tb, lambda v: v <= edge), _verify(s.bh, tb, lambda v: v >= edge))
    tbs = np.minimum(tb, nb - 1)
    okt &= s.bstart[tbs] < expiry
    m0 = s.bfirst[tbs]
    tm = np.where(is_sup, first_hit(s.st_ml, m0, edge, gt), first_hit(s.st_mh, m0, edge, lt))
    nm = len(s.mmin)
    tms = np.minimum(tm, nm - 1)
    okt &= tm < nm
    okt &= np.where(is_sup, s.l[tms] <= edge, s.h[tms] >= edge)
    okt &= s.mmin[tms] < expiry
    # fill: trades >= 1 bp through
    zgap = okt & (s.gcum[tms] != s.gcum[np.minimum(s.bfirst[np.minimum(fb_v, nb - 1)], nm - 1)])
    okt &= ~zgap
    fill = okt & np.where(is_sup, s.l[tms] <= edge * (1 - 1e-4), s.h[tms] >= edge * (1 + 1e-4))
    j = np.flatnonzero(fill)
    i = tms[j]
    out = {"fb": fb_v[j], "row": row_v[j], "d": d[j], "E": edge[j], "i": i, "tag": tag_v[j]}
    # ATR of the entry day
    day = s.mmin[i] // 1440 - s.d0
    atr = s.atr[np.clip(day, 0, len(s.atr) - 1)]
    okatr = ~np.isnan(atr) & (day >= 0) & (day < len(s.atr))
    tend = np.searchsorted(s.mmin, s.mmin[i] + 1440, side="right") - 1
    okgap = s.gcum[tend] == s.gcum[i]
    nogap = int((okatr & ~okgap).sum())
    okatr &= okgap
    for kk in out:
        out[kk] = out[kk][okatr]
    out["S"] = STOP_ATR * atr[okatr]
    stats = {"zones": len(fb), "departed": len(idx), "tested": int(okt.sum()), "filled": int(fill.sum()),
             "gap_zone_dropped": int(zgap.sum()), "gap_trade_dropped": nogap, "kept": int(okatr.sum())}
    return out, stats


def simulate(s, z, tpmode):
    """Outcome of each potential entry. Returns dict with exit index, net (base, stress, late) in bp, R bp, type."""
    i, d, E, S = z["i"], z["d"], z["E"], z["S"]
    nm = len(s.mmin)
    stop = E - d * S
    # TP
    if tpmode == "2R":
        tp = E + d * 2 * S
    else:
        tp = E + d * 2 * S  # default when no node qualifies
        bE = np.searchsorted(s.bstart, s.mmin[i], side="right") - 1
        okb = bE >= 48
        rows = s.poc[np.maximum(bE, 48)[:, None] - 48 + np.arange(48)[None, :]]  # (N, 48)
        cand = np.where(d[:, None] > 0, s.row_lo(rows - 1), s.row_lo(rows + 2))
        dist = d[:, None] * (cand - E[:, None])
        good = (rows >= 0) & (dist >= S[:, None]) & (dist <= 3 * S[:, None]) & okb[:, None]
        dist = np.where(good, dist, np.inf)
        jbest = np.argmin(dist, axis=1)
        has = np.isfinite(dist[np.arange(len(i)), jbest])
        tp = np.where(has, cand[np.arange(len(i)), jbest], tp)
    end = np.searchsorted(s.mmin, s.mmin[i] + 1440, side="right") - 1
    st1 = np.minimum(i + 1, nm)
    # first stop minute after i, first TP minute after i
    js = np.where(d > 0, first_hit(s.st_ml, st1, stop, gt), first_hit(s.st_mh, st1, stop, lt))
    jt = np.where(d > 0, first_hit(s.st_mh, st1, tp, le), first_hit(s.st_ml, st1, tp, ge))
    js_s, jt_s = np.minimum(js, nm - 1), np.minimum(jt, nm - 1)
    oks = (js <= end) & np.where(d > 0, s.l[js_s] <= stop, s.h[js_s] >= stop)
    okt = (jt <= end) & np.where(d > 0, s.h[jt_s] > tp, s.l[jt_s] < tp)
    js = np.where(oks, js, nm + 10)
    jt = np.where(okt, jt, nm + 10)
    stop_in_fill = np.where(d > 0, s.l[i] <= stop, s.h[i] >= stop)
    R = S / E * 1e4

    def path(from_fill_check):
        typ = np.full(len(i), 2)  # 0 stop, 1 tp, 2 time
        ex = end.copy()
        px = s.c[end].copy()
        hit_s = js <= jt
        sel = (js <= end) & hit_s
        typ[sel] = 0
        ex[sel] = js[sel]
        o = s.o[js_s]
        px[sel] = np.where(d[sel] > 0, np.minimum(stop[sel], o[sel]), np.maximum(stop[sel], o[sel]))
        sel2 = (jt <= end) & ~hit_s
        typ[sel2] = 1
        ex[sel2] = jt[sel2]
        px[sel2] = tp[sel2]
        if from_fill_check is not None:
            f = from_fill_check
            typ[f] = 0
            ex[f] = i[f]
            px[f] = stop[f]
        return typ, ex, px

    def funding(ex):
        a = np.searchsorted(s.fmin, s.mmin[i], side="right")  # stamps > fill minute
        b = np.searchsorted(s.fmin, s.mmin[ex], side="right")  # stamps <= exit minute
        return (s.fcum[b] - s.fcum[a]) * 1e4

    slip = SLIP[s.sym]
    # base
    typ, ex, px = path(stop_in_fill)
    gross = d * (px - E) / E * 1e4
    fees = MAKER + np.where(typ == 1, MAKER, TAKER)
    sl = np.where(typ == 0, slip, 0.0)
    fund = d * funding(ex)
    net = gross - fees - sl - fund
    stress = gross - 1.5 * (fees + sl) - fund
    # one step late: market entry at the fill minute close
    El = s.c[i]
    beyond = np.where(d > 0, (El <= stop) | (El >= tp), (El >= stop) | (El <= tp))
    ltyp, lex, lpx = path(None)
    nxt = np.minimum(i + 1, nm - 1)
    ltyp = np.where(beyond, 0, ltyp)
    lex = np.where(beyond, nxt, lex)
    lpx = np.where(beyond, s.o[nxt], lpx)
    lgross = d * (lpx - El) / El * 1e4
    lfees = TAKER + np.where(ltyp == 1, MAKER, TAKER)
    lsl = np.where(ltyp == 0, slip, 0.0)
    lnet = lgross - lfees - lsl - d * funding(lex)
    return {"ex": ex, "typ": typ, "gross": gross, "net": net, "stress": stress, "late": lnet, "R": R,
            "fund": fund, "tp": tp, "ltyp": ltyp, "lex": lex}


def one_at_a_time(i, ex, fb, grp=None):
    """Greedy filter: take a trade only if it fills after the previous taken trade's exit (per group)."""
    if grp is None:
        grp = np.zeros(len(i), dtype=np.int64)
    order = np.lexsort((fb, i, grp))
    take = np.zeros(len(i), dtype=bool)
    gi, ii, ee = grp[order].tolist(), i[order].tolist(), ex[order].tolist()
    last_g, last_e = None, -1
    for pos in range(len(order)):
        g = gi[pos]
        if g != last_g:
            last_g, last_e = g, -1
        if ii[pos] > last_e:
            take[order[pos]] = True
            last_e = ee[pos]
    return take


def run(sym, draws=200):
    s = Sym(sym)
    real = {}
    zstats = {}
    rng = np.random.default_rng(75_000 + fp.SYMS.index(sym))
    rand_parts = []
    for n in NS:
        fb, row = nodes(s, n)
        z, st = zone_trades(s, fb, row)
        zstats[n] = st
        print(f"[{sym}] n={n} {st}", flush=True)
        for tpm in TPS:
            r = simulate(s, z, tpm)
            take = one_at_a_time(z["i"], r["ex"], z["fb"])
            c = f"n{n}_{tpm}"
            real[c] = {**{k: v[take] for k, v in z.items()}, **{k: v[take] for k, v in r.items()},
                       "min": s.mmin[z["i"][take]], "n_potential": len(take)}
        # random benchmark, batched by draws
        okr = ~np.isnan(s.lo48[fb])
        fbr, rowr = fb[okr], row[okr]
        rlo = s.row_of(s.lo48[fbr])
        rhi = s.row_of(s.hi48[fbr])
        width = rhi - rlo  # number of choices excluding the real row
        good = width >= 1
        fbr, rowr, rlo, width = fbr[good], rowr[good], rlo[good], width[good]
        B = 25
        for d0 in range(0, draws, B):
            nd = min(B, draws - d0)
            x = rlo[None, :] + (rng.random((nd, len(fbr))) * width[None, :]).astype(np.int64)
            x = np.where(x >= rowr[None, :], x + 1, x)
            dr = np.repeat(np.arange(d0, d0 + nd), len(fbr))
            zfb = np.tile(fbr, nd)
            zr, _ = zone_trades(s, zfb, x.ravel(), dr)
            zr_draw = zr["tag"]
            for tpm in TPS:
                r = simulate(s, zr, tpm)
                take = one_at_a_time(zr["i"], r["ex"], zr["fb"], zr_draw)
                rand_parts.append({"draw": zr_draw[take].astype(np.int16),
                                   "cell": np.full(int(take.sum()), NS.index(n) * 2 + TPS.index(tpm), np.int8),
                                   "min": s.mmin[zr["i"][take]], "net": r["net"][take].astype(np.float32),
                                   "R": r["R"][take].astype(np.float32)})
            print(f"[{sym}] n={n} random draws {d0 + nd}/{draws}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    flat = {}
    for c, dct in real.items():
        for kk, v in dct.items():
            flat[f"{c}__{kk}"] = v
    for n, st in zstats.items():
        for kk, v in st.items():
            flat[f"zstats_n{n}__{kk}"] = v
    np.savez(os.path.join(OUT, f"{sym}_real.npz"), k=s.k, poc_mismatch=s.poc_mismatch, poc_outside=s.poc_outside, **flat)
    if not rand_parts:
        print(f"[{sym}] saved (no random draws)", flush=True)
        return
    rp = {kk: np.concatenate([p[kk] for p in rand_parts]) for kk in rand_parts[0]}
    np.savez(os.path.join(OUT, f"{sym}_rand.npz"), **rp)
    print(f"[{sym}] saved", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 200)
