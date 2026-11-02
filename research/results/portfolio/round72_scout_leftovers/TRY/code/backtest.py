"""Stream TRY backtest of the 6 declared cells (HYPOTHESES_TRY.md). numpy only. Every number is in bp per trade.
Usage: python -I backtest.py [days.npz]  -> prints tables (copied into STREAM_TRY.md)."""
import datetime as dt
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402
import premium  # noqa: E402
import rates_try as R  # noqa: E402

COMM = 0.7  # bp round trip
CELLS = [(k, h) for k in (0.01, 0.02) for h in (1, 5, 20)]
IS_END = dt.date(2022, 1, 1).toordinal()
D = dict(np.load(os.path.join(load.ROOT, "days.npz")))
D.pop("med_spread", None)
DAY = D["day"]
N = len(DAY)
DATES = [dt.date.fromordinal(int(x)) for x in DAY]
CARRY = {}


def carry_bp(i, j, markup):
    key = (i, j, markup)
    if key not in CARRY:
        CARRY[key] = R.carry_cost(DATES[i], DATES[j], markup) * 1e4
    return CARRY[key]


def trades(sig_idx, h, late="none", sm=1.0, cm=1.0, markup=0.02):
    """Rows (entry index, net, gross_mid, spread, carry) for entries at sig_idx."""
    out = []
    for i in sig_idx:
        e = i + 1 if late == "day" else i
        j = e + h
        if j >= N:
            continue
        if late == "min":
            ea, eb, xa, xb = D["ask2"][e], D["bid2"][e], D["ask2"][j], D["bid2"][j]
        else:
            ea, eb, xa, xb = D["ask1"][e], D["bid1"][e], D["ask1"][j], D["bid1"][j]
        if not np.isfinite([ea, eb, xa, xb]).all():
            continue
        m0, m1 = (ea + eb) / 2, (xa + xb) / 2
        gross = (m1 / m0 - 1) * 1e4
        spread = ((ea - eb) / 2 / m0 + (xa - xb) / 2 / m1) * 1e4
        car = carry_bp(e, j, markup)
        net = gross - sm * spread - COMM - cm * car
        fb = int(D["ask_fallback"][e] or D["ask_fallback"][j]) if "ask_fallback" in D else 0
        out.append((i, net, gross, spread, car, fb))
    return np.array(out).reshape(-1, 6)


def cl_t(x, g):
    """t of the mean clustered by group g (CR1)."""
    if len(x) < 2:
        return np.nan
    u = np.unique(g)
    G = len(u)
    if G < 2:
        return np.nan
    m = x.mean()
    s = np.array([(x[g == k] - m).sum() for k in u])
    se = np.sqrt((s ** 2).sum() * G / (G - 1)) / len(x)
    return m / se if se > 0 else np.nan


def nw_t(x, lag):
    n = len(x)
    if n < 3:
        return np.nan
    e = x - x.mean()
    v = (e @ e) / n
    for L in range(1, min(lag, n - 1) + 1):
        v += 2 * (1 - L / (lag + 1)) * (e[L:] @ e[:-L]) / n
    return x.mean() / np.sqrt(v / n) if v > 0 else np.nan


def era_mask(idx, era):
    d = DAY[idx]
    if era == "IS":
        return d < IS_END
    return d >= IS_END


def stats(T, ep, h):
    if len(T) == 0:
        return dict(n=0, eps=0, net=np.nan, t_cl=np.nan, t_nw=np.nan, gross=np.nan, spread=np.nan, carry=np.nan)
    g = ep[T[:, 0].astype(int)]
    return dict(n=len(T), eps=len(np.unique(g)), fb=int(T[:, 5].sum()), net=T[:, 1].mean(), t_cl=cl_t(T[:, 1], g), t_nw=nw_t(T[:, 1], h + 5),
                gross=T[:, 2].mean(), spread=T[:, 3].mean(), carry=T[:, 4].mean())


def signal(k):
    p = D["p"]
    return np.isfinite(p) & (p > k)


def run():
    rng = np.random.default_rng(72)
    pfin = np.isfinite(D["p"])
    eras = {e: np.flatnonzero(pfin & era_mask(np.arange(N), e)) for e in ("IS", "VAL")}
    res = {}
    for k, h in CELLS:
        sig = signal(k)
        ep = premium.episodes(sig)
        for era, pool in eras.items():
            idx = pool[sig[pool]]
            T = trades(idx, h)
            s = stats(T, ep, h)
            s["x1.5"] = trades(idx, h, sm=1.5, cm=1.5)[:, 1].mean() if len(idx) else np.nan
            s["+1min"] = trades(idx, h, late="min")[:, 1].mean() if len(idx) else np.nan
            s["+1day"] = trades(idx, h, late="day")[:, 1].mean() if len(idx) else np.nan
            s["mk1"] = trades(idx, h, markup=0.01)[:, 1].mean() if len(idx) else np.nan
            s["nocarry"] = (T[:, 1] + T[:, 4]).mean() if len(T) else np.nan
            yrs = {}
            for row in T:
                yrs.setdefault(DATES[int(row[0])].year, []).append(row[1])
            s["years"] = {y: (len(v), float(np.mean(v))) for y, v in sorted(yrs.items())}
            if len(T):
                # episode-level series for power
                g = ep[T[:, 0].astype(int)]
                em = np.array([T[g == u, 1].mean() for u in np.unique(g)])
                s["ep_sharpe"] = em.mean() / em.std(ddof=1) if len(em) > 1 else np.nan
                s["tr_sharpe"] = T[:, 1].mean() / T[:, 1].std(ddof=1) if len(T) > 1 else np.nan
                # random benchmarks
                n_era = len(pool)
                sh, iid = [], []
                cand = pool[pool + h < N]
                for _ in range(2000):
                    off = int(rng.integers(h + 1, n_era - h - 1))
                    pos = np.searchsorted(pool, idx)
                    ridx = pool[(pos + off) % n_era]
                    Tr = trades(ridx, h)
                    sh.append(Tr[:, 1].mean() if len(Tr) else np.nan)
                    ri = rng.choice(cand, size=min(len(idx), len(cand)), replace=False)
                    Ti = trades(ri, h)
                    iid.append(Ti[:, 1].mean())
                sh, iid = np.array(sh), np.array(iid)
                s["rand_shift"] = float(np.nanmean(sh < s["net"]) * 100)
                s["rand_iid"] = float(np.mean(iid < s["net"]) * 100)
                s["rand_iid_mean"] = float(np.mean(iid))
            res[(k, h, era)] = s
    return res


def maxcell_null(res, draws=500):
    """Share of circular-shift draws (same offset for all cells, within IS) whose best IS clustered t beats each cell's."""
    rng = np.random.default_rng(7272)
    pool = np.flatnonzero(np.isfinite(D["p"]) & era_mask(np.arange(N), "IS"))
    n_era = len(pool)
    best = []
    for _ in range(draws):
        off = int(rng.integers(21, n_era - 21))
        bt = -np.inf
        for k, h in CELLS:
            sig = signal(k)
            idx = pool[sig[pool]]
            if not len(idx):
                continue
            pos = np.searchsorted(pool, idx)
            shifted = np.zeros(N, bool)
            shifted[pool[(pos + off) % n_era]] = True
            ep = premium.episodes(shifted)
            T = trades(np.flatnonzero(shifted), h)
            if len(T) > 1:
                t = cl_t(T[:, 1], ep[T[:, 0].astype(int)])
                if np.isfinite(t):
                    bt = max(bt, t)
        best.append(bt)
    best = np.array(best)
    return {(k, h): float(np.mean(best >= res[(k, h, "IS")]["t_cl"]) * 100) for k, h in CELLS}


if __name__ == "__main__":
    res = run()
    hdr = "cell era n eps fallback net gross spread carry t_cl t_nw x1.5 +1min +1day mk1 nocarry rand_shift% rand_iid% iid_mean ep_SR tr_SR"
    print(hdr)
    for (k, h, era), s in res.items():
        f = lambda key: s.get(key, np.nan)
        print(f"k{int(k*100)}h{h} {era} {s['n']} {s['eps']} {s.get('fb', 0)} " + " ".join(
            f"{f(x):.1f}" if isinstance(f(x), float) and abs(f(x)) >= 1 else f"{f(x):.2f}" for x in (
                "net", "gross", "spread", "carry", "t_cl", "t_nw", "x1.5", "+1min", "+1day", "mk1", "nocarry",
                "rand_shift", "rand_iid", "rand_iid_mean", "ep_sharpe", "tr_sharpe")))
    print("\nyears (n, net bp)")
    for (k, h, era), s in res.items():
        print(f"k{int(k*100)}h{h} {era}", {y: (n, round(v, 1)) for y, (n, v) in s["years"].items()})
    if "--maxnull" in sys.argv:
        print("\nmax-over-6-cells null, % of IS shift draws with best t >= cell's IS t:", maxcell_null(res))
