"""Stream BL analysis (HYPOTHESES_BL.md sections 4-5). Input: research/data/binance_tg_listing/<rule>_events.json with
N (ms), src, sym, X (ms, the open / launch exit; may be null), edited, era, year, day; npz files from pull.py.
Cells: X5, X60, XO (L1) / XP (L2). Long only. Prints per-cell tables, per-year, burst timing, random null.
Usage: python -I analyze.py <rule> [--with-edited]"""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net
D = net.D; NPZ = os.path.join(D, "npz")
FEE = {"bum": 5.0, "bybit": 5.5, "okx": 5.0, "bspot": 10.0}
FUND = {"bum": "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance/funding",
        "bybit": "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/bybit/funding"}
END = net.END_MS
RNG = np.random.default_rng(74)


def day_of(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


class Series:
    """Trades in windows (exact) plus per-second arrays for the loaded days of one (src, sym)."""
    def __init__(self, src, sym, days):
        ts, ps = [], []; self.sec = {}
        for d in sorted(set(days)):
            z = np.load(os.path.join(NPZ, f"{src}_{sym}_{d}.npz"))
            if int(z["missing"]):
                continue
            ts.append(z["t"]); ps.append(z["p"])
            self.sec[d] = (int(z["d0"]), z["hi"], z["lo"], z["fi"], z["la"], z["n"])
        self.d0s = sorted((v[0], k) for k, v in self.sec.items())
        self.t = np.concatenate(ts) if ts else np.zeros(0, np.int64)
        self.p = np.concatenate(ps) if ps else np.zeros(0)
        o = np.argsort(self.t, kind="stable"); self.t, self.p = self.t[o], self.p[o]

    def fill(self, t0, side, maxwait=60000):
        """First trade >= t0 (within maxwait); worst price in its 1 s. side +1 buy (max) / -1 sell (min)."""
        i = np.searchsorted(self.t, t0)
        if i >= len(self.t) or self.t[i] - t0 > maxwait:
            return None
        j = np.searchsorted(self.t, self.t[i] + 1000)
        seg = self.p[i:j]
        return dict(first=self.p[i], worst=seg.max() if side > 0 else seg.min(), tf=int(self.t[i]))

    def last_at(self, t0):
        i = np.searchsorted(self.t, t0, side="right") - 1
        return self.p[i] if i >= 0 and t0 - self.t[i] < 3600000 else np.nan

    def file_of(self, t0):
        for d0, k in self.d0s:
            if d0 <= t0 < d0 + 86400000:
                return k
        return None

    def sec_fill(self, t0, side, maxwait=60):
        """Second-level fill (for the random benchmark and its event twin): first non-empty second >= t0, its high
        (buy) or low (sell)."""
        d = self.file_of(t0)
        if d is None:
            return None
        d0, hi, lo, fi, la, n = self.sec[d]
        s = int((t0 - d0) // 1000)
        for k in range(s, min(s + maxwait, 86400)):
            if n[k] > 0:
                return hi[k] if side > 0 else lo[k]
        return None


_fund = {}


def funding(src, sym, a, b):
    """Sum of funding rates paid by a long between a and b (ms); + = paid (a cost). 0 when no file."""
    if src not in FUND:
        return 0.0, False
    fn = os.path.join(FUND[src], sym + ".csv")
    if not os.path.exists(fn):
        return 0.0, False
    if fn not in _fund:
        x = np.loadtxt(fn, delimiter=",", skiprows=1, ndmin=2); x = x[x[:, 0] < END]; _fund[fn] = x
    x = _fund[fn]
    m = (x[:, 0] > a) & (x[:, 0] <= b)
    return float(x[m, 1].sum()) * 1e4, True


def tclust(v, days):
    v = np.asarray(v, float); n = len(v)
    if n < 2:
        return np.nan
    m = v.mean(); g = {}
    for x, d in zip(v - m, days):
        g[d] = g.get(d, 0.0) + x
    se = math.sqrt(sum(s * s for s in g.values())) / n
    return m / se if se > 0 else np.nan


def run(rule, with_edited=False):
    E = json.load(open(os.path.join(D, f"{rule}_events.json")))
    E = [e for e in E if e["N"] < END and (with_edited or not e["edited"])]
    lastcell = "XO" if rule == "l1" else "XP"
    cells = {"X5": lambda e: e["N"] + 300000, "X60": lambda e: e["N"] + 3600000,
             lastcell: lambda e: e["X"] if e.get("X") and e["N"] + 300000 < e["X"] <= e["N"] + 172800000 else None}
    rows = []
    paths = []
    for e in E:
        days = e["days"]
        S = Series(e["src"], e["sym"], days)
        if len(S.t) == 0:
            continue
        N = e["N"]; fee = FEE[e["src"]]
        ref = S.last_at(N - 60000)
        # burst path
        offs = [-3600, -600, -60, 0, 1, 2, 3, 5, 10, 30, 60, 300, 3600]
        pth = {o: (math.log(S.last_at(N + o * 1000) / ref) * 1e4 if np.isfinite(ref) else np.nan) for o in offs}
        thr = 200 if rule == "l1" else 100
        k0 = np.searchsorted(S.t, N - 600000); k1 = np.searchsorted(S.t, N + 600000)
        onset = None
        if np.isfinite(ref):
            hit = np.where(np.log(S.p[k0:k1] / ref) * 1e4 >= thr)[0]
            if len(hit):
                onset = (S.t[k0 + hit[0]] - N) / 1000
        paths.append(dict(era=e["era"], pth=pth, onset=onset))
        for c, fx in cells.items():
            X = fx(e)
            if X is None:
                continue
            for d_ in (5, 10):
                en = S.fill(N + d_ * 1000, +1); ex = S.fill(X, -1)
                if en is None or ex is None or ex["tf"] <= en["tf"]:
                    continue
                gross = math.log(ex["worst"] / en["worst"]) * 1e4
                gross_ft = math.log(ex["first"] / en["first"]) * 1e4
                gap = gross_ft - gross
                fu, fu_ok = funding(e["src"], e["sym"], en["tf"], ex["tf"])
                net_ = gross - 2 * fee - fu
                x15 = gross_ft - 1.5 * gap - 3 * fee - fu
                se_en = S.sec_fill(N + d_ * 1000, +1); se_ex = S.sec_fill(X, -1)
                sg = math.log(se_ex / se_en) * 1e4 if (se_en and se_ex) else np.nan
                rows.append(dict(cell=c, d=d_, era=e["era"], year=e["year"], day=e["day"], coin=e["coin"],
                                 src=e["src"], gross=gross, gap=gap, fund=fu, fund_ok=fu_ok, net=net_, x15=x15,
                                 sec_gross=sg, H=(X - N), N=N, sym=e["sym"], days=days, fee=fee))
    return E, rows, paths


def random_null(rows, n_sets=1000):
    """Same coin, same UTC day (only days whose file was loaded), uniform second outside [N - 1 h, N + 2 h], same hold
    length H, second-level fills. Returns {cell: array (n_sets,) of random gross means} and per-set per-trade draws."""
    cache = {}
    draws = {}
    for r in rows:
        if r["d"] != 5:
            continue
        key = (r["src"], r["sym"], tuple(r["days"]))
        if key not in cache:
            cache[key] = Series(r["src"], r["sym"], r["days"])
        S = cache[key]
        fN = S.file_of(r["N"])
        if fN is None:
            continue
        d0 = S.sec[fN][0]
        d_end = max(v[0] for v in S.sec.values()) + 86400000
        lo_, hi_ = d0, min(d0 + 86400000, d_end - r["H"] - 60000)
        out = np.full(n_sets, np.nan)
        if hi_ - lo_ > 3 * 3600000:
            for k in range(n_sets):
                for _ in range(20):
                    s = int(RNG.integers(lo_, hi_))
                    if r["N"] - 3600000 <= s <= r["N"] + 7200000:
                        continue
                    a = S.sec_fill(s, +1); b = S.sec_fill(s + r["H"], -1)
                    if a and b:
                        out[k] = math.log(b / a) * 1e4; break
        draws.setdefault(r["cell"], []).append((r, out))
    return draws


def summ(v, days):
    v = np.asarray(v, float)
    if len(v) == 0:
        return dict(n=0)
    sd = v.std(ddof=1) if len(v) > 1 else np.nan
    return dict(n=len(v), nd=len(set(days)), mean=v.mean(), t=tclust(v, days), med=float(np.median(v)),
                sr=v.mean() / sd if sd and sd > 0 else np.nan)


def main():
    rule = sys.argv[1]; we = "--with-edited" in sys.argv
    E, rows, paths = run(rule, we)
    print(f"rule {rule} events {len(E)} (with edited: {we}); rows {len(rows)}")
    out = {}
    draws = random_null(rows)
    for c in (["X5", "X60", "XO"] if rule == "l1" else ["X5", "X60", "XP"]):
        for era in ("IS", "VAL"):
            R = [r for r in rows if r["cell"] == c and r["era"] == era and r["d"] == 5]
            L = [r for r in rows if r["cell"] == c and r["era"] == era and r["d"] == 10]
            if not R:
                print(c, era, "n 0"); continue
            s = summ([r["net"] for r in R], [r["day"] for r in R])
            g = np.mean([r["gross"] for r in R]); gap = np.mean([r["gap"] for r in R]); fu = np.mean([r["fund"] for r in R])
            x15 = np.mean([r["x15"] for r in R]); late = np.mean([r["net"] for r in L]) if L else np.nan
            yrs = {}
            for r in R:
                yrs.setdefault(r["year"], []).append(r["net"])
            ys = " ".join(f"{y} {np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
            # random percentile on second-level gross
            dr = [(r, o) for (r, o) in draws.get(c, []) if r["era"] == era]
            ev_sec = np.nanmean([r["sec_gross"] for r, _ in dr]) if dr else np.nan
            M = np.array([o for _, o in dr]) if dr else np.zeros((0, 1))
            rmeans = np.nanmean(M, axis=0) if len(M) else np.array([np.nan])
            pct = float(np.mean(rmeans < ev_sec) * 100) if np.isfinite(ev_sec) else np.nan
            srcs = {}
            for r in R:
                srcs[r["src"]] = srcs.get(r["src"], 0) + 1
            out[(c, era)] = dict(s, gross=g, gap=gap, fund=fu, x15=x15, late=late, years=ys, rand=pct, srcs=srcs)
            print(f"{c} {era} n {s['n']} ({s['nd']} d) gross {g:+.0f} gap {gap:.0f} fund {fu:+.1f} net {s['mean']:+.0f} "
                  f"t {s['t']:.2f} med {s['med']:+.0f} SR {s['sr']:.2f} x1.5 {x15:+.0f} late {late:+.0f} | {ys} | "
                  f"rand {pct:.1f}% (sec-level event gross {ev_sec:+.0f}) | src {srcs}")
    # max-over-cells null on t (random gross minus each trade's own fee and funding), per era
    for era in ("IS", "VAL"):
        T = []
        for k in range(1000):
            best = -np.inf
            for c, lst in draws.items():
                v, dd = [], []
                for r, o in lst:
                    if r["era"] == era and np.isfinite(o[k]):
                        v.append(o[k] - 2 * r["fee"] - r["fund"]); dd.append(r["day"])
                if len(v) >= 3:
                    best = max(best, tclust(v, dd))
            T.append(best)
        T = np.array(T); T = T[np.isfinite(T)]
        if len(T):
            print(f"max-over-cells null {era}: median t {np.median(T):.2f} p95 {np.percentile(T, 95):.2f}")
    # burst timing
    for era in ("IS", "VAL"):
        P = [p for p in paths if p["era"] == era]
        if not P:
            continue
        med = {o: np.nanmedian([p["pth"][o] for p in P]) for o in P[0]["pth"]}
        on = [p["onset"] for p in P if p["onset"] is not None]
        sh = []
        for p in P:
            a, b = p["pth"][5], p["pth"][60]
            if np.isfinite(a) and np.isfinite(b) and b > 50:
                sh.append(a / b)
        sh5 = []
        for p in P:
            a, b = p["pth"][5], p["pth"][300]
            if np.isfinite(a) and np.isfinite(b) and b > 50:
                sh5.append(a / b)
        print(f"path {era} n {len(P)} median bp vs N-60s: " + " ".join(f"{o:+d}s {v:+.0f}" for o, v in med.items()))
        if on:
            print(f"  onset (>= thr) n {len(on)} of {len(P)}: median {np.median(on):+.1f} s, q10 {np.percentile(on,10):+.1f}, "
                  f"q90 {np.percentile(on,90):+.1f}, share before N {np.mean(np.array(on) < 0):.2f}")
        if sh:
            print(f"  share of +60 s move done by N+5 s: median {np.median(sh):.2f} (n {len(sh)}); of +5 min: "
                  f"{np.median(sh5) if sh5 else float('nan'):.2f} (n {len(sh5)})")
    import csv
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", f"trades_{rule}{'_ed' if we else ''}.csv"), "w") as f:
        w = csv.writer(f); w.writerow(["cell", "d", "era", "year", "day", "coin", "src", "sym", "gross", "gap", "fund", "net", "x15", "H_s"])
        for r in rows:
            w.writerow([r["cell"], r["d"], r["era"], r["year"], r["day"], r["coin"], r["src"], r["sym"], f"{r['gross']:.1f}",
                        f"{r['gap']:.1f}", f"{r['fund']:.2f}", f"{r['net']:.1f}", f"{r['x15']:.1f}", r["H"] // 1000])


if __name__ == "__main__":
    main()
