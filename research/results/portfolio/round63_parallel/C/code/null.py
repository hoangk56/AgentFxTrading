"""Round 63 stream C: shuffled-rank null for the 54 cells (same eligible set, same costs, base execution).
Per cell and shuffle: IS t (min of day-clustered and NW), IS / VAL net mean per rebalance. Writes ../out/null_<i>.npz.
Usage: null.py <worker> <n_workers> [n_shuffles]"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import xs  # noqa: E402


def fast_t(net, dayidx, nday):
    s = np.bincount(dayidx, weights=net, minlength=nday)
    mu, sd = s.mean(), s.std(ddof=1)
    t_day = mu / sd * np.sqrt(len(s)) if sd > 0 else 0.0
    xc = s - mu
    v = (xc * xc).mean()
    for L in range(1, 6):
        v += 2 * (1 - L / 6) * (xc[L:] * xc[:-L]).mean()
    t_nw = mu / np.sqrt(v / len(s)) if v > 0 else 0.0
    return min(t_day, t_nw)


def main():
    w, nw = int(sys.argv[1]), int(sys.argv[2])
    nsh = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    cx = xs.Ctx(xs.load())
    cl = run.cells()
    t0 = time.time()
    for ci in range(w, len(cl), nw):
        fam, kind, J, H = cl[ci]
        fn = os.path.join(run.OUT, f"null_{ci:02d}.npz")
        if os.path.exists(fn):
            continue
        ts, S = xs.precompute(cx, J, H, kind, fam)
        q = run.q_of(fam)
        M = xs.mats(cx, ts, H)
        valid = ~np.isnan(S)
        K, n = S.shape
        tms = M["tms"]
        mIS = xs.era_mask(tms, xs.IS)
        mVA = xs.era_mask(tms, xs.VAL)
        d = (tms // xs.DAY).astype(np.int64)
        dIS = d[mIS] - d[mIS].min()
        dVA = d[mVA] - d[mVA].min()
        rng = np.random.default_rng(1000 + ci)
        out = np.zeros((nsh, 4))
        for s in range(nsh):
            W = xs.weights(np.where(valid, 0.0, np.nan), q, rng=rng)
            b = xs.book(M, W)
            r = b["net"]
            out[s] = (fast_t(r[mIS], dIS, dIS.max() + 1), r[mIS].mean(), r[mVA].mean(),
                      fast_t(r[mVA], dVA, dVA.max() + 1))
        np.savez(fn, out=out, cell=np.array("|".join(map(str, cl[ci]))))
        print(ci, cl[ci], f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
