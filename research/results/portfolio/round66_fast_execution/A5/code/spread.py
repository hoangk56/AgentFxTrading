"""Stream A5 descriptive (declared in A5/HYPOTHESES_A5.md; info only, no verdict): first-second spread proxies at the
A2-D5L entry second [N + 5 s, N + 6 s) and at calm N - 10 min .. N - 9 min, for ARB (the only perp < 7 d old at N, by
minute precision; already one of A2's events) vs A2's other events; ARB's path at A2's offsets. Reads A2's
research/data/upbit_latency/npz read-only through A2's events loader. No download."""
import os, sys, importlib.util
import numpy as np
A2C = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2/code"
sys.path.insert(0, A2C)
_s = importlib.util.spec_from_file_location("a2_events", os.path.join(A2C, "events.py"))
A2E = importlib.util.module_from_spec(_s); _s.loader.exec_module(A2E)
NPZ = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_latency/npz"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A5/spread.txt"
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
K1M = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/perp_launch/k1m"


def load(sym, day):
    z = np.load(os.path.join(NPZ, f"{sym}_{day}.npz")); return {k: z[k] for k in z.files}


def bins(S, a, b):
    """per 1 s bin in [a, b): (effective spread proxy, range); spread needs both taker sides in the bin."""
    i, j = np.searchsorted(S["t"], [a, b])
    t, p, q, m = S["t"][i:j], S["p"][i:j], S["q"][i:j].astype(float), S["m"][i:j]
    sp, rg, nt = [], [], []
    for k in np.unique((t - a) // 1000):
        w = (t - a) // 1000 == k
        pp, qq, mm = p[w], q[w], m[w]
        rg.append((pp.max() - pp.min()) / pp.min()); nt.append(w.sum())
        bu, se = mm == 0, mm == 1  # m = buyer is maker -> seller is taker
        if bu.any() and se.any():
            vb = (pp[bu] * qq[bu]).sum() / qq[bu].sum(); vs = (pp[se] * qq[se]).sum() / qq[se].sum()
            sp.append((vb - vs) / (0.5 * (vb + vs)))
    return sp, rg, nt


def at(S, T):
    i = np.searchsorted(S["t"], T, "right") - 1
    return S["p"][i] if i >= 0 else np.nan


def age(sym, N):
    p = os.path.join(K1M, sym + ".npz")
    if not os.path.exists(p):
        return np.nan
    z = np.load(p); w = np.where(z["n"] > 0)[0]
    return (N - int(z["ot"][w[0]])) / 86400000 if len(w) else np.nan


def main():
    E = A2E.load_events(); f = open(OUT, "w")
    P = lambda *a: (print(*a), print(*a, file=f))
    P("# A5 descriptive: spread proxies (bp). ent = [N+5, N+6) s; calm = median over 1 s bins in [N-600, N-540) s")
    P("coin      era  day        age_d  ent_spread ent_range ent_trades | calm_spread calm_range")
    R = []
    for e in E:
        A = load(e["perp"], e["day"]); N = e["N"]
        s1, r1, n1 = bins(A, N + 5000, N + 6000)
        s0, r0, _ = bins(A, N - 600000, N - 540000)
        x = dict(coin=e["coin"], era=e["era"], age=age(e["perp"], N),
                 es=1e4 * s1[0] if s1 else np.nan, er=1e4 * r1[0] if r1 else np.nan, en=n1[0] if n1 else 0,
                 cs=1e4 * np.median(s0) if s0 else np.nan, cr=1e4 * np.median(r0) if r0 else np.nan)
        R.append(x)
        P(f"{x['coin']:9s} {x['era']:4s} {e['day']} {x['age']:6.1f} {x['es']:10.1f} {x['er']:9.1f} {x['en']:9d}  | {x['cs']:10.1f} {x['cr']:9.1f}")
    for era in ("IS", "VAL"):
        S = [x for x in R if x["era"] == era and x["coin"] != "ARB"]
        g = lambda k: np.nanmedian([x[k] for x in S])
        P(f"\n{era} excl. ARB (n {len(S)}) medians: entry spread {g('es'):.1f}, entry range {g('er'):.1f}, entry trades {g('en'):.0f}; calm spread {g('cs'):.1f}, calm range {g('cr'):.1f}")
    a = [x for x in R if x["coin"] == "ARB"][0]
    P(f"ARB (perp {a['age']:.2f} d old): entry spread {a['es']:.1f}, entry range {a['er']:.1f}, entry trades {a['en']}; calm spread {a['cs']:.1f}, calm range {a['cr']:.1f}")
    e = [x for x in E if x["coin"] == "ARB"][0]; A = load("ARBUSDT", e["day"]); B = load("BTCUSDT", e["day"]); N = e["N"]
    ra, rb = at(A, N - 60000), at(B, N - 60000)
    P("\nARB path r(t) = ln(alt/alt_ref) - ln(BTC/BTC_ref), ref N - 60 s (bp): " +
      ", ".join(f"{o:+d}s {1e4*(np.log(at(A, N+o*1000)/ra)-np.log(at(B, N+o*1000)/rb)):.0f}" for o in OFFS))
    P(f"ARB L - N = {(e['L']-N)/60000:.1f} min")
    f.close()


if __name__ == "__main__":
    main()
