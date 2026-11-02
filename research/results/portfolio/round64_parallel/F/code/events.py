"""Stream F: build the candidate wick events and their trade returns (../HYPOTHESES_F.md).

Minute axis: t = minutes since T0 = 2020-01-01 00:00 UTC; c[t] = close of the 1m bar opening at t. Everything is cut at
ts < 2025-01-01 (END). Output out/cand.npz: one row per guarded candidate event with |r| >= 1 % (superset of all cells;
cell membership and de-duplication are applied in report.py), with gross returns for H in {5, 15, 60} entered one or
two bars late, the open-of-next-bar entry (information), funding, cost h, and 200 random-minute draws per event.
"""
import os, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(R, "results/portfolio/round63_parallel/C/code"))
import xs  # noqa: E402

D = os.path.join(R, "data", "binance_1m_wicks")
OUT = os.path.join(HERE, "..", "out")
T0 = 1577836800000            # 2020-01-01
END = 1735689600000           # 2025-01-01 exclusive
MIN = 60000
DAY = 86400000
NM = (END - T0) // MIN
VAL0 = (1640995200000 - T0) // MIN
HS = (5, 15, 60)
NREP = 200
SIG_W, SIG_MIN = 1440, 1000


def load_sym(s):
    files = sorted(glob.glob(os.path.join(D, "npz", f"{s}_*.npz")))
    c = np.full(NM, np.nan); o = np.full(NM, np.nan); n = np.zeros(NM, np.int32); qv = np.zeros(NM)
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
    """sd of r over t-1440..t-1 (needs >= 1000 valid)."""
    ok = ~np.isnan(r)
    x = np.where(ok, r, 0.0)
    def rs(z):
        cs = np.concatenate([[0.0], np.cumsum(z)])
        out = np.full(NM, np.nan)
        out[SIG_W:] = cs[SIG_W:NM] - cs[:NM - SIG_W]
        return out  # out[t] = sum over t-1440..t-1
    cnt, s1, s2 = rs(ok.astype(float)), rs(x), rs(x * x)
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (s2 - s1 * s1 / cnt) / (cnt - 1)
        sd = np.sqrt(np.maximum(var, 0))
    sd[~(cnt >= SIG_MIN)] = np.nan
    return sd


def ffill_idx(c):
    """last valid index <= t."""
    idx = np.where(~np.isnan(c), np.arange(NM), -1)
    np.maximum.accumulate(idx, out=idx)
    return idx


def px_at(c, last, t):
    """close at t with a <= 5 minute forward fill; nan if beyond."""
    t = np.asarray(t)
    good = t < NM
    tt = np.where(good, t, 0)
    j = last[tt]
    p = np.where((j >= 0) & (tt - j <= 5) & good, c[np.maximum(j, 0)], np.nan)
    return p


def funding_sum(cumfr, te_ms, tx_ms):
    """sum of stamps with time in (te, tx]; cumfr[k] = sum FR[:k]."""
    h1 = np.floor((te_ms - xs.H0) / 3600000).astype(np.int64) + 1
    h2 = np.floor((tx_ms - xs.H0) / 3600000).astype(np.int64)
    h1 = np.clip(h1, 0, len(cumfr) - 1); h2 = np.clip(h2 + 1, 0, len(cumfr) - 1)
    return np.where(h2 > h1, cumfr[h2] - cumfr[h1], 0.0)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(64064)
    u = np.load(os.path.join(D, "univ.npz"))
    U, RK, usyms = u["U"], u["rank"], list(u["syms"])
    P = xs.load()
    FR = P["FR"]; psyms = P["syms"]
    day_of_t = ((T0 + np.arange(NM, dtype=np.int64) * MIN - xs.H0) // DAY)
    cb, _, _, _, _ = load_sym("BTCUSDT")
    rb = ret1(cb)
    rows = {k: [] for k in ["sym", "t", "r", "rb", "sig", "rank", "g", "gl", "go", "f", "fl", "rnd", "rnd_t", "dec"]}
    have = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(D, "npz", "*.npz"))})
    if os.environ.get("F_SYMS"):
        have = os.environ["F_SYMS"].split(",")
    for s in have:
        i = usyms.index(s)
        c, o, n, qv, nf = load_sym(s)
        r = ret1(c)
        sig = trailing_sd(r)
        last = ffill_idx(c)
        inU = U[i, np.clip(day_of_t, 0, U.shape[1] - 1)]
        rank = RK[i, np.clip(day_of_t, 0, U.shape[1] - 1)]
        cumfr = np.concatenate([[0.0], np.cumsum(FR[psyms.index(s)])]) if s in psyms else np.zeros(FR.shape[1] + 1)
        # candidates: |r| >= 1 %, in universe, guard
        with np.errstate(invalid="ignore"):
            big = (np.abs(r) >= 0.03) | ((np.abs(r) >= 0.01) & (np.abs(r) >= 10 * sig))
        cand = np.where(big & inU)[0]
        cand = cand[(cand >= 1) & (cand + 2 + 60 < NM)]
        rr = r[cand]
        nxt_o = o[cand + 1]
        half = c[cand - 1] * (1 + rr / 2)
        guard = (n[cand] >= 10) & (qv[cand] > 0) & ~np.isnan(nxt_o) & np.where(rr < 0, nxt_o <= half, nxt_o >= half)
        cand = cand[guard]; rr = r[cand]
        if len(cand) == 0:
            print(s, nf, 0, flush=True); continue
        side = -np.sign(rr)
        pe = c[cand + 1]; pl = c[cand + 2]; po = o[cand + 1]
        g = np.full((len(cand), 3), np.nan); gl = g.copy(); go = g.copy(); f = g.copy(); fl = g.copy()
        for k, H in enumerate(HS):
            x = px_at(c, last, cand + 1 + H); xl = px_at(c, last, cand + 2 + H)
            g[:, k] = side * (x / pe - 1); gl[:, k] = side * (xl / pl - 1); go[:, k] = side * (x / po - 1)
            te = T0 + (cand + 2) * MIN; tel = te + MIN
            f[:, k] = side * funding_sum(cumfr, te, te + H * MIN)
            fl[:, k] = side * funding_sum(cumfr, tel, tel + H * MIN)
        # random benchmark: same coin, same era, same trailing-sigma decile among in-universe minutes
        nxt_ok = np.r_[~np.isnan(c[1:]), False]
        pool_ok = inU & ~np.isnan(sig) & ~np.isnan(r) & (r != 0) & nxt_ok
        pool_ok[:1] = False; pool_ok[NM - 62:] = False
        dec_ev = np.full(len(cand), -1)
        rnd = np.full((len(cand), NREP, 3), np.nan); rnd_t = np.zeros((len(cand), NREP), np.int32)
        for era in (0, 1):
            em = np.zeros(NM, bool)
            if era == 0: em[:VAL0] = True
            else: em[VAL0:] = True
            pool = np.where(pool_ok & em)[0]
            sel_ev = np.where((cand < VAL0) == (era == 0))[0]
            if len(pool) < 100 or len(sel_ev) == 0:
                continue
            qs = np.quantile(sig[pool], np.linspace(0, 1, 11)[1:-1])
            pdec = np.searchsorted(qs, sig[pool])
            sev = sig[cand[sel_ev]]
            edec = np.where(np.isnan(sev), 9, np.searchsorted(qs, np.nan_to_num(sev, nan=0)))
            dec_ev[sel_ev] = edec
            for dcl in np.unique(edec):
                pp = pool[pdec == dcl]
                evs = sel_ev[edec == dcl]
                if len(pp) == 0:
                    continue
                tr = pp[rng.integers(0, len(pp), size=(len(evs), NREP))]
                rnd_t[evs] = tr
                sd_ = -np.sign(r[tr])
                pe_r = c[tr + 1]
                for k, H in enumerate(HS):
                    x = px_at(c, last, tr + 1 + H)
                    te = T0 + (tr + 2) * MIN
                    rnd[evs, :, k] = sd_ * (x / pe_r - 1) - sd_ * funding_sum(cumfr, te, te + H * MIN)
        for k_, v in [("sym", np.full(len(cand), i)), ("t", cand), ("r", rr), ("rb", rb[cand]), ("sig", sig[cand]),
                      ("rank", rank[cand]), ("g", g), ("gl", gl), ("go", go), ("f", f), ("fl", fl),
                      ("rnd", rnd.astype(np.float32)), ("rnd_t", rnd_t), ("dec", dec_ev)]:
            rows[k_].append(v)
        print(s, nf, len(cand), flush=True)
    out = {k: np.concatenate(v) for k, v in rows.items()}
    out["syms"] = np.array(usyms)
    np.savez(os.path.join(OUT, os.environ.get("F_OUT", "cand.npz")), **out)
    print("candidates", len(out["t"]))


if __name__ == "__main__":
    main()
