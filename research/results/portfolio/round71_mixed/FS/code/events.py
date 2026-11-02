"""Round 71 FS: candidate crash events and random draws from the spot 1m npz (../HYPOTHESES_FS.md).

Minute axis t = minutes since 2020-01-01 00:00 UTC; c[t] = close of the 1m bar opening at t; cut at ts < 2025-01-01.
Candidate (superset of the 4 cells, before the aggTrade guard and de-duplication): r_e = c_e / c_{e-1} - 1 <= -5 %
(consecutive bars), in the universe on e's day, bar e >= 10 trades and qv > 0, |r_BTC spot,e| <= 0.2 |r_e|.
Stored per candidate: kline o_{e+1}, c_{e+1}, exit closes at bars e+16 / e+61 (<= 5 min ffill), trailing sd, rank,
and 200 random-minute gross returns per H (same coin, era, universe, r < 0, sd decile; entry o_{t+1}, exit c_{t+1+H}).
Output out/cand.npz (small).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

NM, MIN, T0 = C.NM, C.MIN, C.T0
HS = (15, 60)
NREP = 200
SIG_W, SIG_MIN = 1440, 1000


def load_sym(s):
    import glob
    c = np.full(NM, np.nan); o = np.full(NM, np.nan); n = np.zeros(NM, np.int32); qv = np.zeros(NM)
    files = sorted(glob.glob(os.path.join(C.DATA, "npz", f"{s}_*.npz")))
    for f in files:
        z = np.load(f)
        t = z["m"].astype(np.int64) - T0 // MIN
        k = (t >= 0) & (t < NM)
        t = t[k]
        c[t] = z["c"][k]; o[t] = z["o"][k]; n[t] = z["n"][k]; qv[t] = z["qv"][k]
    return c, o, n, qv, len(files)


def ret1(c):
    r = np.full(NM, np.nan)
    r[1:] = c[1:] / c[:-1] - 1
    return r


def trailing_sd(r):
    ok = ~np.isnan(r)
    x = np.where(ok, r, 0.0)

    def rs(z):
        cs = np.concatenate([[0.0], np.cumsum(z)])
        out = np.full(NM, np.nan)
        out[SIG_W:] = cs[SIG_W:NM] - cs[:NM - SIG_W]
        return out
    cnt, s1, s2 = rs(ok.astype(float)), rs(x), rs(x * x)
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (s2 - s1 * s1 / cnt) / (cnt - 1)
        sd = np.sqrt(np.maximum(var, 0))
    sd[~(cnt >= SIG_MIN)] = np.nan
    return sd


def ffill_idx(c):
    idx = np.where(~np.isnan(c), np.arange(NM), -1)
    np.maximum.accumulate(idx, out=idx)
    return idx


def px_at(c, last, t):
    t = np.asarray(t)
    good = t < NM
    tt = np.where(good, t, 0)
    j = last[tt]
    return np.where((j >= 0) & (tt - j <= 5) & good, c[np.maximum(j, 0)], np.nan)


def main():
    os.makedirs(C.OUT, exist_ok=True)
    rng = np.random.default_rng(71071)
    u = np.load(os.path.join(C.DATA, "univ.npz"))
    U, RK, usyms = u["U"], u["rank"], list(u["syms"])
    day_of_t = np.arange(NM, dtype=np.int64) // 1440
    cb = load_sym("BTCUSDT")[0]
    rb = ret1(cb)
    keys = ["sym", "t", "r", "rb", "sig", "rank", "cprev", "o1", "c1", "x15", "x60", "rnd", "rnd_t", "nbar", "qvbar"]
    rows = {k: [] for k in keys}
    act = [i for i in range(len(usyms)) if U[i].any()]
    stats = []
    for i in act:
        s = usyms[i]
        c, o, n, qv, nf = load_sym(s)
        inU = U[i, day_of_t]
        rank = RK[i, day_of_t]
        cov = np.isfinite(c[inU]).mean() if inU.any() else np.nan
        r = ret1(c)
        sig = trailing_sd(r)
        last = ffill_idx(c)
        with np.errstate(invalid="ignore"):
            big = (r <= -0.05) & inU
        cand = np.where(big)[0]
        cand = cand[(cand >= 1) & (cand + 2 + 60 < NM)]
        with np.errstate(invalid="ignore"):
            keep = (n[cand] >= 10) & (qv[cand] > 0) & np.isfinite(rb[cand]) & (np.abs(rb[cand]) <= 0.2 * np.abs(r[cand]))
        ncrash_all = len(cand)
        cand = cand[keep]
        stats.append((s, nf, int(inU.sum()), cov, ncrash_all, len(cand)))
        if len(cand) == 0:
            continue
        x15 = px_at(c, last, cand + 1 + 15); x60 = px_at(c, last, cand + 1 + 60)
        # random pool: same coin, in universe, r < 0, sd known, next bar exists
        nxt_ok = np.r_[~np.isnan(o[1:]), False]
        with np.errstate(invalid="ignore"):
            pool_ok = inU & ~np.isnan(sig) & (r < 0) & nxt_ok
        pool_ok[:1] = False; pool_ok[NM - 62:] = False
        rnd = np.full((len(cand), NREP, 2), np.nan, np.float32); rnd_t = np.zeros((len(cand), NREP), np.int32)
        for era in (0, 1):
            em = np.zeros(NM, bool)
            if era == 0:
                em[:C.VAL0] = True
            else:
                em[C.VAL0:] = True
            pool = np.where(pool_ok & em)[0]
            sel = np.where((cand < C.VAL0) == (era == 0))[0]
            if len(sel) == 0 or len(pool) < 100:
                continue
            qs = np.quantile(sig[pool], np.linspace(0, 1, 11)[1:-1])
            pdec = np.searchsorted(qs, sig[pool])
            sev = sig[cand[sel]]
            edec = np.where(np.isnan(sev), 9, np.searchsorted(qs, np.nan_to_num(sev, nan=0)))
            for dcl in np.unique(edec):
                pp = pool[pdec == dcl]
                evs = sel[edec == dcl]
                if len(pp) == 0:
                    continue
                tr = pp[rng.integers(0, len(pp), size=(len(evs), NREP))]
                rnd_t[evs] = tr
                pe = o[tr + 1]
                for k, H in enumerate(HS):
                    rnd[evs, :, k] = px_at(c, last, tr + 1 + H) / pe - 1
        for k_, v in [("sym", np.full(len(cand), i)), ("t", cand), ("r", r[cand]), ("rb", rb[cand]),
                      ("sig", sig[cand]), ("rank", rank[cand]), ("cprev", c[cand - 1]), ("o1", o[cand + 1]),
                      ("c1", c[cand + 1]), ("x15", x15), ("x60", x60), ("rnd", rnd), ("rnd_t", rnd_t),
                      ("nbar", n[cand]), ("qvbar", qv[cand])]:
            rows[k_].append(v)
        print(s, nf, len(cand), flush=True)
    out = {k: np.concatenate(v) for k, v in rows.items()}
    out["syms"] = np.array(usyms)
    np.savez(os.path.join(C.DATA, "cand.npz"), **out)
    with open(os.path.join(C.OUT, "coverage.txt"), "w") as f:
        f.write("sym files universe_minutes share_of_universe_minutes_with_a_bar crashes_5pct_in_univ idio_guarded\n")
        for st in stats:
            f.write(" ".join(str(x) for x in st) + "\n")
    print("candidates", len(out["t"]), "IS", int((out["t"] < C.VAL0).sum()), "VAL", int((out["t"] >= C.VAL0).sum()))


if __name__ == "__main__":
    main()
