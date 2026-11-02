"""Stream G: BTC one-minute shocks and altcoin catch-up trades (../HYPOTHESES_G.md).

Pass 1 (BTC): shocks |r_B| >= X (guard, 60-min de-dup), BTC prices at entry / exit, random minutes (same era, same BTC
trailing-sd decile) with their BTC side and prices. Pass 2 (one symbol at a time): beta over the trailing 7 days, the
alt rows at every shock (eligible alts, lag / lead flags, returns for H in {5, 15, 60}, late, open entry, funding) and
the random-minute returns for the laggard rows. Output out/g_rows.npz. Imports stream F's loaders (not edited).
"""
import os, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F_CODE = os.path.abspath(os.path.join(HERE, "..", "..", "F", "code"))
sys.path.insert(0, F_CODE)
import events as E  # noqa: E402  (stream F, read-only)

xs = E.xs
OUT = os.path.join(HERE, "..", "out")
NM, T0, MIN, DAY, VAL0 = E.NM, E.T0, E.MIN, E.DAY, E.VAL0
HS = (5, 15, 60)
XS = (0.01, 0.02)
NREP = 200
BW, BMIN = 10080, 5000
BETA_MIN = 0.5


def roll_sum(z, w):
    cs = np.concatenate([[0.0], np.cumsum(z)])
    out = np.full(NM, np.nan)
    out[w:] = cs[w:NM] - cs[:NM - w]   # out[t] = sum over t-w..t-1
    return out


def beta_series(ra, rb):
    ok = ~np.isnan(ra) & ~np.isnan(rb)
    x = np.where(ok, rb, 0.0); y = np.where(ok, ra, 0.0)
    n = roll_sum(ok.astype(float), BW)
    sx, sy = roll_sum(x, BW), roll_sum(y, BW)
    sxy, sxx = roll_sum(x * y, BW), roll_sum(x * x, BW)
    with np.errstate(invalid="ignore", divide="ignore"):
        b = (sxy - sx * sy / n) / (sxx - sx * sx / n)
    b[~(n >= BMIN)] = np.nan
    return b


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(64007)
    u = np.load(os.path.join(E.D, "univ.npz"))
    U, RK, usyms = u["U"], u["rank"], list(u["syms"])
    P = xs.load(); FR = P["FR"]; psyms = P["syms"]
    day_of_t = ((T0 + np.arange(NM, dtype=np.int64) * MIN - xs.H0) // DAY)
    dcl = np.clip(day_of_t, 0, U.shape[1] - 1)
    # ---- pass 1: BTC
    cB, oB, nB, qB, _ = E.load_sym("BTCUSDT")
    rB = E.ret1(cB); lastB = E.ffill_idx(cB); sigB = E.trailing_sd(rB)
    cumB = np.concatenate([[0.0], np.cumsum(FR[psyms.index("BTCUSDT")])])
    nxt = np.r_[~np.isnan(cB[1:]), False]
    pool_ok = ~np.isnan(sigB) & ~np.isnan(rB) & (rB != 0) & nxt
    pool_ok[:1] = False; pool_ok[NM - 64:] = False
    SH = []
    for X in XS:
        with np.errstate(invalid="ignore"):
            e = np.where(np.abs(rB) >= X)[0]
        e = e[(e >= BW + 1) & (e + 3 + 60 < NM)]
        rr = rB[e]; no = oB[e + 1]; half = cB[e - 1] * (1 + rr / 2)
        g = (nB[e] >= 10) & (qB[e] > 0) & ~np.isnan(no) & np.where(rr > 0, no >= half, no <= half)
        e = e[g]
        keep = []; last = -10 ** 9
        for t in e:
            if t - last > 60:
                keep.append(t); last = t
        e = np.array(keep, np.int64)
        side = np.sign(rB[e])
        # BTC legs at the shock (entry close e+1 / late e+2 / open e+1)
        bt = {}
        for k, H in enumerate(HS):
            bt[("g", k)] = E.px_at(cB, lastB, e + 1 + H) / cB[e + 1] - 1
            bt[("gl", k)] = E.px_at(cB, lastB, e + 2 + H) / cB[e + 2] - 1
            bt[("go", k)] = E.px_at(cB, lastB, e + 1 + H) / oB[e + 1] - 1
            te = T0 + (e + 2) * MIN
            bt[("f", k)] = E.funding_sum(cumB, te, te + H * MIN)
            bt[("fl", k)] = E.funding_sum(cumB, te + MIN, te + MIN + H * MIN)
        # random minutes
        rnd = np.zeros((len(e), NREP), np.int64)
        for era in (0, 1):
            em = np.zeros(NM, bool)
            if era == 0: em[:VAL0] = True
            else: em[VAL0:] = True
            pool = np.where(pool_ok & em)[0]
            sel = np.where((e < VAL0) == (era == 0))[0]
            if len(sel) == 0:
                continue
            qs = np.quantile(sigB[pool], np.linspace(0, 1, 11)[1:-1])
            pdec = np.searchsorted(qs, sigB[pool])
            edec = np.searchsorted(qs, np.nan_to_num(sigB[e[sel]], nan=0))
            for d in np.unique(edec):
                pp = pool[pdec == d]; ev = sel[edec == d]
                rnd[ev] = pp[rng.integers(0, len(pp), size=(len(ev), NREP))]
        rside = np.sign(rB[rnd])
        rbt = np.zeros((len(e), NREP, 3))
        for k, H in enumerate(HS):
            te = T0 + (rnd + 2) * MIN
            rbt[:, :, k] = E.px_at(cB, lastB, rnd + 1 + H) / cB[rnd + 1] - 1 - 0 * te
        rbf = np.zeros((len(e), NREP, 3))
        for k, H in enumerate(HS):
            te = T0 + (rnd + 2) * MIN
            rbf[:, :, k] = E.funding_sum(cumB, te.ravel(), te.ravel() + H * MIN).reshape(rnd.shape)
        SH.append(dict(e=e, side=side, rb=rB[e], bt=bt, rnd=rnd, rside=rside, rbt=rbt, rbf=rbf,
                       sigB=sigB[e]))
        print("X", X, "shocks", len(e), "IS", int((e < VAL0).sum()), "VAL", int((e >= VAL0).sum()), flush=True)
    del cB, oB, nB, qB, sigB, pool_ok, nxt
    # ---- pass 2: alts
    cols = ["x", "j", "sym", "beta", "ra", "lag", "lead", "rank", "g", "gl", "go", "f", "fl", "m1", "rnd_g", "rnd_f",
            "rnd_beta"]
    rows = {k: [] for k in cols}
    have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(E.D, "npz", "*.npz"))})
    have = [s for s in have if s != "BTCUSDT"]
    for s in have:
        i = usyms.index(s)
        c, o, n, qv, nf = E.load_sym(s)
        r = E.ret1(c); last = E.ffill_idx(c)
        beta = beta_series(r, rB)
        inU = U[i, dcl]; rank = RK[i, dcl]
        cumfr = np.concatenate([[0.0], np.cumsum(FR[psyms.index(s)])]) if s in psyms else np.zeros(FR.shape[1] + 1)
        tot = 0
        for xi, S in enumerate(SH):
            e = S["e"]
            ok = inU[e] & ~np.isnan(c[e - 1]) & ~np.isnan(c[e]) & ~np.isnan(c[e + 1]) & (beta[e] >= BETA_MIN)
            jj = np.where(ok)[0]
            if len(jj) == 0:
                continue
            ee = e[jj]; sd = S["side"][jj]; bb = beta[ee]
            uu = r[ee] - bb * S["rb"][jj]
            lag = (np.sign(uu) == -sd) & (np.abs(uu) > 0.5 * np.abs(bb * S["rb"][jj]))
            lead = np.sign(uu) == sd
            g = np.full((len(jj), 3), np.nan); gl = g.copy(); go = g.copy(); f = g.copy(); fl = g.copy()
            for k, H in enumerate(HS):
                g[:, k] = E.px_at(c, last, ee + 1 + H) / c[ee + 1] - 1
                gl[:, k] = E.px_at(c, last, ee + 2 + H) / c[ee + 2] - 1
                go[:, k] = E.px_at(c, last, ee + 1 + H) / o[ee + 1] - 1
                te = T0 + (ee + 2) * MIN
                f[:, k] = E.funding_sum(cumfr, te, te + H * MIN)
                fl[:, k] = E.funding_sum(cumfr, te + MIN, te + MIN + H * MIN)
            m1 = c[ee + 1] / c[ee] - 1
            # random returns for the laggard rows (same coin, the shock's random minutes)
            rg = np.full((len(jj), NREP, 3), np.nan, np.float32); rf = rg.copy()
            rbeta = np.full((len(jj), NREP), np.nan, np.float32)
            li = np.where(lag)[0]
            if len(li):
                tr = S["rnd"][jj[li]]
                for k, H in enumerate(HS):
                    rg[li, :, k] = E.px_at(c, last, tr + 1 + H) / c[tr + 1] - 1
                    te = T0 + (tr + 2) * MIN
                    rf[li, :, k] = E.funding_sum(cumfr, te.ravel(), te.ravel() + H * MIN).reshape(tr.shape)
                rbeta[li] = beta[tr]
            for k_, v in [("x", np.full(len(jj), xi)), ("j", jj), ("sym", np.full(len(jj), i)), ("beta", bb),
                          ("ra", r[ee]), ("lag", lag), ("lead", lead), ("rank", rank[ee]), ("g", g), ("gl", gl),
                          ("go", go), ("f", f), ("fl", fl), ("m1", m1), ("rnd_g", rg), ("rnd_f", rf),
                          ("rnd_beta", rbeta)]:
                rows[k_].append(v)
            tot += len(jj)
        print(s, nf, tot, flush=True)
        del c, o, n, qv, r, last, beta
    out = {k: np.concatenate(v) for k, v in rows.items()}
    out["syms"] = np.array(usyms)
    for xi, S in enumerate(SH):
        out[f"s{xi}_e"] = S["e"]; out[f"s{xi}_side"] = S["side"]; out[f"s{xi}_rb"] = S["rb"]
        out[f"s{xi}_rnd"] = S["rnd"]; out[f"s{xi}_rside"] = S["rside"]; out[f"s{xi}_rbt"] = S["rbt"]
        out[f"s{xi}_rbf"] = S["rbf"]; out[f"s{xi}_sigB"] = S["sigB"]
        for (nm, k), v in S["bt"].items():
            out[f"s{xi}_b{nm}{k}"] = v
    np.savez(os.path.join(OUT, "g_rows.npz"), **out)
    print("rows", len(out["j"]))


if __name__ == "__main__":
    main()
