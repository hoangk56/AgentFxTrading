"""Stream R: hourly gross profile (IS) then the 7 declared books on IS / VAL (../HYPOTHESES_R.md).
Usage: r.py profile  -> IS hour-by-hour gross profile only
       r.py books    -> declared books, checks, shuffled-share benchmark, max-over-cells null
       r.py valprof  -> VAL hour-by-hour profile (information, after the books)"""
import json, os, sys
import numpy as np
import rdata as r

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "..")
D = r.load()
S = r.shares(D)
P, FR, U, rk, syms = D["P"], D["FR"], D["U"], D["rk"], D["syms"]
n = len(syms); ND = r.ND
iB = syms.index("BTCUSDT")
CF = np.cumsum(FR, axis=1)


def ffill(x):
    m = x.shape[1]
    idx = np.where(~np.isnan(x), np.arange(m)[None, :], 0)
    np.maximum.accumulate(idx, axis=1, out=idx)
    return x[np.arange(x.shape[0])[:, None], idx]


Pf = ffill(P)
days = np.arange(ND)
tday = r.H0 + days * r.DAY
LAST = int((r.CUT - r.H0) // r.DAY) - 1       # 2024-12-31 is excluded: last book day 2024-12-30
use_day = (tday >= r.IS[0]) & (days < LAST)
h00 = days * 24; h15 = days * 24 + 15; h24 = days * 24 + 24
priced = ~np.isnan(P[:, np.minimum(h00, r.NH)]) & ~np.isnan(P[:, np.minimum(h15, r.NH)])   # [n, ND]
EA = (U & np.isfinite(S) & priced).T         # [ND, n] eligible universe A
EB = (U & priced).T                           # universe B
SB = np.where(np.isfinite(S), S, 0.0)
JIT = np.random.default_rng(65).random((ND, n)) * 1e-9    # fixed tie-break for zero shares in B
XA = np.where(EA, S.T, np.nan)
XB = np.where(EB, SB.T + JIT, np.nan)
okA = use_day & (EA.sum(1) >= 9)
okB = use_day & (EB.sum(1) >= 9)
big = np.array([s in ("BTCUSDT", "ETHUSDT") for s in syms])
HS = np.where(rk.T < 20, 0.0003, 0.0005)
HS = np.where(big[None, :], 0.0001, HS)       # [ND, n]
HS[:, iB] = 0.0001


def terc(X):
    """[ND, n] -> +1 high tercile, -1 low tercile, 0 else (k = floor(nv / 3))."""
    valid = ~np.isnan(X)
    nv = valid.sum(1)
    k = nv // 3
    order = np.argsort(np.where(valid, X, np.inf), axis=1)
    rank = np.empty_like(order)
    np.put_along_axis(rank, order, np.arange(X.shape[1])[None, :].repeat(X.shape[0], 0), axis=1)
    hi = valid & (rank >= (nv - k)[:, None])
    lo = valid & (rank < k[:, None])
    return hi.astype(float) - lo.astype(float), k


def window(e, x):
    """Per-day [ND, n] simple return entry instant e -> exit x (exit ffilled) and funding over (e, x]."""
    e = np.minimum(e, r.NH); x = np.minimum(x, r.NH)
    ret = (Pf[:, x] / P[:, e] - 1).T
    ret = np.where(np.isfinite(ret), ret, 0.0)
    fu = (CF[:, x] - CF[:, e]).T
    return ret, fu


def leg_weights(T, k, kind, sign):
    """kind LS: +high/k - low/k ; BTC: high/k vs BTC -1. sign = +1 (long high) or -1 (short high)."""
    kk = np.where(k > 0, k, 1)[:, None]
    if kind == "LS":
        W = T / kk
    else:
        W = np.where(T > 0, 1.0, 0.0) / kk
        W[:, iB] = -1.0
    return sign * W


CELLS = {  # name: universe, window, kind, sign of the high-share leg
    "A-N-LS": ("A", "N", "LS", -1), "A-D-LS": ("A", "D", "LS", +1), "A-N-BTC": ("A", "N", "BTC", -1),
    "A-D-BTC": ("A", "D", "BTC", +1), "A-FLIP": ("A", "F", "LS", +1), "B-N-LS": ("B", "N", "LS", -1),
    "B-D-LS": ("B", "D", "LS", +1)}


def prep(lag=0):
    RD, FD = window(h00 + lag, h15 + lag)
    RN, FN = window(h15 + lag, h24 + lag)
    return dict(RD=RD, FD=FD, RN=RN, FN=FN)


def run_cell(name, TA, kA, TB, kB, M, cost_mult=1.0):
    uni, win, kind, sg = CELLS[name]
    T, k, ok = (TA, kA, okA) if uni == "A" else (TB, kB, okB)
    W = leg_weights(T, k, kind, sg)
    W[~ok] = 0.0
    c = cost_mult * (0.0005 + HS)
    if win in ("D", "N"):
        R_, F_ = (M["RD"], M["FD"]) if win == "D" else (M["RN"], M["FN"])
        gross = (W * R_).sum(1)
        fund = -(W * F_).sum(1)
        cost = 2 * (np.abs(W) * c).sum(1)
        btc = R_[:, iB]
    else:      # FLIP: day W, night -W; trades at 00 (from previous night) and 15
        Wn = -W
        prevn = np.vstack([np.zeros((1, n)), Wn[:-1]])
        gross = (W * M["RD"]).sum(1) + (Wn * M["RN"]).sum(1)
        fund = -(W * M["FD"]).sum(1) - (Wn * M["FN"]).sum(1)
        cost = (np.abs(W - prevn) * c).sum(1) + (np.abs(Wn - W) * c).sum(1)
        # closing the last night position (next day not traded) is charged on that day
        nxt = np.concatenate([ok[1:], [False]])
        cost += np.where(ok & ~nxt, (np.abs(Wn) * c).sum(1), 0.0)
        btc = M["RD"][:, iB] + M["RN"][:, iB]
    net = gross + fund - cost
    return dict(net=net, gross=gross, fund=fund, cost=cost, ok=ok, btc=btc)


def tst(x):
    nn = len(x)
    if nn < 10:
        return dict(n=nn, mean=np.nan, t=np.nan, sr=np.nan)
    mu, sd = x.mean(), x.std(ddof=1)
    t_day = mu / sd * np.sqrt(nn) if sd > 0 else 0.0
    xc = x - mu; v = (xc * xc).mean()
    for L in range(1, 6):
        v += 2 * (1 - L / 6) * (xc[L:] * xc[:-L]).mean()
    t_nw = mu / np.sqrt(v / nn) if v > 0 else 0.0
    return dict(n=nn, mean=mu, t=min(t_day, t_nw), t_day=t_day, t_nw=t_nw, sr=mu / sd if sd > 0 else 0.0)


def era(era_):
    a, b = era_
    return (tday >= a) & (tday < b)


def year_of_day():
    return tday.astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970


def profile(eraname):
    TA, kA = terc(XA)
    m = era(r.IS if eraname == "IS" else r.VAL) & okA
    rows = []
    hi_w = np.where(TA > 0, 1.0, 0.0) / np.maximum(kA, 1)[:, None]
    lo_w = np.where(TA < 0, 1.0, 0.0) / np.maximum(kA, 1)[:, None]
    cum = 0.0; cumB = 0.0
    out = []
    for h in range(24):
        e = np.minimum(days * 24 + h, r.NH); x = np.minimum(e + 1, r.NH)
        ret = (P[:, x] / P[:, e] - 1).T
        okr = np.isfinite(ret)
        # leg means over coins with both prices
        hw = np.where(okr, hi_w, 0); lw = np.where(okr, lo_w, 0)
        rr = np.where(okr, ret, 0)
        hm = (hw * rr).sum(1) / np.where(hw.sum(1) > 0, hw.sum(1), np.nan)
        lm = (lw * rr).sum(1) / np.where(lw.sum(1) > 0, lw.sum(1), np.nan)
        bm = ret[:, iB]
        d1 = hm - lm; d2 = hm - bm
        g = m & np.isfinite(d1) & np.isfinite(d2)
        s1 = tst(d1[g]); s2 = tst(d2[g])
        cum += s1["mean"]; cumB += s2["mean"]
        out.append(dict(h=h, n=int(g.sum()), hl_bp=1e4 * s1["mean"], hl_t=s1["t_day"], hb_bp=1e4 * s2["mean"],
                        hb_t=s2["t_day"], cum_hl=1e4 * cum, cum_hb=1e4 * cumB))
    return out


def print_profile(prof, title, f):
    print(title, file=f)
    print(" UTC  KST   n    high-low bp  t     cum   | high-BTC bp  t     cum", file=f)
    for p in prof:
        print(f" {p['h']:02d}   {(p['h'] + 9) % 24:02d}  {p['n']:4d}  {p['hl_bp']:+7.2f}  {p['hl_t']:+5.2f}  {p['cum_hl']:+7.1f} |"
              f"  {p['hb_bp']:+7.2f}  {p['hb_t']:+5.2f}  {p['cum_hb']:+7.1f}", file=f)
    d = sum(p["hl_bp"] for p in prof[:15]); nt = sum(p["hl_bp"] for p in prof[15:])
    db = sum(p["hb_bp"] for p in prof[:15]); nb = sum(p["hb_bp"] for p in prof[15:])
    print(f" sum 00-15 UTC (Korean day): high-low {d:+.1f} bp, high-BTC {db:+.1f} bp; 15-24 (night): high-low {nt:+.1f}, "
          f"high-BTC {nb:+.1f}", file=f)


def summarize(res, yrs):
    out = {}
    for en, ee in (("IS", r.IS), ("VAL", r.VAL)):
        m = era(ee) & res["ok"]
        s = tst(res["net"][m])
        out[en] = dict(n=s["n"], net_bp=1e4 * s["mean"], t=s["t"], t_nw=s.get("t_nw"), t_day=s.get("t_day"),
                       sr_day=s["sr"], sr_ann=s["sr"] * np.sqrt(365), gross_bp=1e4 * res["gross"][m].mean(),
                       cost_bp=1e4 * res["cost"][m].mean(), fund_bp=1e4 * res["fund"][m].mean(),
                       corr_btc=float(np.corrcoef(res["gross"][m], res["btc"][m])[0, 1]))
    out["years"] = {int(y): 1e4 * float(res["net"][(yrs == y) & res["ok"]].mean()) for y in range(2020, 2025)}
    out["years_pos"] = int(sum(v > 0 for v in out["years"].values()))
    out["power"] = out["VAL"]["sr_day"] * np.sqrt(667)
    return out


def books():
    f = open(os.path.join(OUTD, "r_books.txt"), "w")
    yrs = year_of_day()
    TA, kA = terc(XA); TB, kB = terc(XB)
    M0 = prep(0); M1 = prep(1)
    print("Declared books, net per day per $1 of one side (bp), t = min(NW lag 5, plain day t)", file=f)
    print(f"IS days A {int((era(r.IS) & okA).sum())} B {int((era(r.IS) & okB).sum())}; VAL days A {int((era(r.VAL) & okA).sum())} "
          f"B {int((era(r.VAL) & okB).sum())}; mean tercile size A IS {kA[era(r.IS) & okA].mean():.1f} VAL {kA[era(r.VAL) & okA].mean():.1f}, "
          f"B IS {kB[era(r.IS) & okB].mean():.1f} VAL {kB[era(r.VAL) & okB].mean():.1f}", file=f)
    res = {}
    for c in CELLS:
        base = run_cell(c, TA, kA, TB, kB, M0)
        s = summarize(base, yrs)
        s["x1.5"] = summarize(run_cell(c, TA, kA, TB, kB, M0, 1.5), yrs)
        s["late"] = summarize(run_cell(c, TA, kA, TB, kB, M1), yrs)
        res[c] = s
    # shuffled-share benchmark: 500 draws, same uniform matrix ranks A and B (same draw for all cells)
    rng = np.random.default_rng(6501)
    ND_ = 500
    rand_mean = {c: {"IS": [], "VAL": []} for c in CELLS}
    rand_t = {c: [] for c in CELLS}
    mIS = era(r.IS); mV = era(r.VAL)
    for k in range(ND_):
        Z = rng.random((ND, n))
        TzA, kzA = terc(np.where(EA, Z, np.nan)); TzB, kzB = terc(np.where(EB, Z, np.nan))
        for c in CELLS:
            z = run_cell(c, TzA, kzA, TzB, kzB, M0)
            a = z["net"][mIS & z["ok"]]; b = z["net"][mV & z["ok"]]
            rand_mean[c]["IS"].append(a.mean()); rand_mean[c]["VAL"].append(b.mean())
            rand_t[c].append(tst(a)["t"])
    maxt = np.max(np.array([rand_t[c] for c in CELLS]), axis=0)
    for c in CELLS:
        for en in ("IS", "VAL"):
            arr = np.array(rand_mean[c][en])
            res[c][en]["rand_pct"] = 100.0 * float((arr < res[c][en]["net_bp"] / 1e4).mean())
    hdr = ("cell", "IS n", "IS net", "IS t", "IS gross", "cost", "fund", "rand%", "VAL n", "VAL net", "VAL t", "VAL gross",
           "rand%", "yrs+", "VAL SRann", "power", "corrBTC IS/VAL")
    print(" | ".join(hdr), file=f)
    for c, s in res.items():
        I, V = s["IS"], s["VAL"]
        print(f"{c} | {I['n']} | {I['net_bp']:+.1f} | {I['t']:+.2f} | {I['gross_bp']:+.1f} | {I['cost_bp']:.1f} | {I['fund_bp']:+.1f} | "
              f"{I['rand_pct']:.0f} | {V['n']} | {V['net_bp']:+.1f} | {V['t']:+.2f} | {V['gross_bp']:+.1f} | {V['rand_pct']:.0f} | "
              f"{s['years_pos']}/5 | {V['sr_ann']:+.2f} | {s['power']:+.2f} | {I['corr_btc']:+.2f}/{V['corr_btc']:+.2f}", file=f)
    print("\nYears (net bp/day):", file=f)
    for c, s in res.items():
        print(c, " ".join(f"{y}:{v:+.1f}" for y, v in s["years"].items()), file=f)
    print("\nChecks (net bp/day, t): costs x1.5 | one step late (+1 h)", file=f)
    for c, s in res.items():
        a, b = s["x1.5"], s["late"]
        print(f"{c}: x1.5 IS {a['IS']['net_bp']:+.1f} ({a['IS']['t']:+.2f}) VAL {a['VAL']['net_bp']:+.1f} ({a['VAL']['t']:+.2f}) | "
              f"late IS {b['IS']['net_bp']:+.1f} ({b['IS']['t']:+.2f}) VAL {b['VAL']['net_bp']:+.1f} ({b['VAL']['t']:+.2f})", file=f)
    print(f"\nMax-over-7-cells shuffled null of IS t ({ND_} draws): median {np.median(maxt):+.2f}, 95th {np.percentile(maxt, 95):+.2f}; "
          f"rand IS net mean (all cells) {1e4 * np.mean([np.mean(rand_mean[c]['IS']) for c in CELLS]):+.1f} bp", file=f)
    best = max(res, key=lambda c: res[c]["IS"]["t"])
    print(f"IS pick (highest IS t): {best}, IS t {res[best]['IS']['t']:+.2f}, pct of max-null "
          f"{100 * (maxt < res[best]['IS']['t']).mean():.0f}", file=f)
    f.close()
    json.dump(dict(res=res, maxnull=dict(median=float(np.median(maxt)), p95=float(np.percentile(maxt, 95))), pick=best),
              open(os.path.join(OUTD, "r_results.json"), "w"), indent=1, default=float)
    print(open(os.path.join(OUTD, "r_books.txt")).read())


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "profile":
        with open(os.path.join(OUTD, "r_profile_IS.txt"), "w") as f:
            print_profile(profile("IS"), "IS 2020-04..2021-12 gross 1h returns by UTC hour, universe A terciles by trailing "
                          "30-day Upbit share (bp per hour, day t)", f)
        print(open(os.path.join(OUTD, "r_profile_IS.txt")).read())
    elif what == "valprof":
        with open(os.path.join(OUTD, "r_profile_VAL.txt"), "w") as f:
            print_profile(profile("VAL"), "VAL 2022-24 (information only, after the books) gross 1h returns by UTC hour", f)
        print(open(os.path.join(OUTD, "r_profile_VAL.txt")).read())
    else:
        books()
