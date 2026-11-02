"""Stream O2 analysis (declared in O2/HYPOTHESES_O2.md): path around the OKX / Bybit listing stamp N from Binance
aggTrades, burst onset vs N (stamp check), the declared rule O2-D5S (A2-D5L frozen: long alt perp / short BTCUSDT
perp at the first trades >= N + 5 s, exit at the first trades >= X = stated start S or N + 60 min) and diagnostics,
robustness, random benchmark from monthly 1m klines, power. `after`, `at`, `slip`, `fund`, `clt` and `trade` are
copied from round65 A2/code/analyze.py unchanged (trade's exit argument X is the O2 exit)."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net
from pull import load_events, day

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
NPZ = os.path.join(net.D, "npz"); KL = os.path.join(net.D, "kl")
OUTD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
H = 3600000
COST = 0.0020
OFFS = [-300, -60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
CELLS = [("D5-S", 5, "S"), ("D2-S", 2, "S"), ("D10-S", 10, "S"), ("D30-S", 30, "S"), ("D60-S", 60, "S"), ("D5-5m", 5, "5m")]
MAIN = "D5-S"
N_HOLD = 79
_C = {}


def load(sym, days):
    k = (sym, tuple(sorted(days)))
    if k not in _C:
        parts = []
        for d in sorted(days):
            z = np.load(os.path.join(NPZ, f"{sym}_{d}.npz"))
            parts.append({x: z[x] for x in ("t", "p", "q", "m")})
        S = {x: np.concatenate([p[x] for p in parts]) for x in ("t", "p", "q", "m")}
        o = np.argsort(S["t"], kind="stable")
        _C[k] = {x: v[o] for x, v in S.items()}
    return _C[k]


def at(S, T):  # last trade at or before T
    i = np.searchsorted(S["t"], T, "right") - 1
    return S["p"][i] if i >= 0 else np.nan


def after(S, T):  # first trade at or after T
    i = np.searchsorted(S["t"], T, "left")
    return (S["p"][i], int(S["t"][i])) if i < len(S["t"]) else (np.nan, None)


def slip(S, T):  # half the median 1 s range over bins with trades in [T, T + 60 s)
    a, b = np.searchsorted(S["t"], [T, T + 60000])
    t, p = S["t"][a:b], S["p"][a:b]
    if not len(t):
        return np.nan
    bins = (t - T) // 1000
    rs = []
    for k in np.unique(bins):
        q = p[bins == k]; rs.append((q.max() - q.min()) / q.min())
    return 0.5 * float(np.median(rs))


_FU = {}


def fund(sym, a, b):  # sum of real funding rates at stamps in (a, b]
    if sym not in _FU:
        p = os.path.join(R, "binance", "funding", sym + ".csv")
        rows = []
        if os.path.exists(p):
            rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
        _FU[sym] = np.array(rows) if rows else np.zeros((0, 2))
    F = _FU[sym]
    if not len(F) or F[:, 0].min() > a or F[:, 0].max() < b - 9 * H:
        r, s = net.opener(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - 86400000}&endTime={min(b + 86400000, 1735689599999)}&limit=1000")
        body = r.read() if r else b"[]"
        if r:
            net.log(r.url, s, len(body), "GET"); r.close()
        js = json.loads(body)
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js]) if js else np.zeros((0, 2))
        F = F[F[:, 0] < 1735689600000] if len(F) else F
        _FU[sym] = F
    if not len(F):
        return 0.0
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n


def trade(e, d, X, A, B, costmul=1.0):
    N = e["N"]
    ae, te_a = after(A, N + d * 1000); be, te_b = after(B, N + d * 1000)
    ax, tx_a = after(A, X); bx, tx_b = after(B, X)
    if te_a is None or tx_a is None or te_b is None or tx_b is None:
        return None
    sl = slip(A, te_a) + slip(A, tx_a) + slip(B, te_b) + slip(B, tx_b)
    gross = (ax / ae - 1) - (bx / be - 1)
    f = -fund(e["perp"], te_a, tx_a) + fund("BTCUSDT", te_b, tx_b)
    net_ = gross + f - costmul * (COST + sl)
    return dict(gross=gross, fund=f, slip=sl, net=net_, lag_a=(te_a - N) / 1000, hold=(tx_a - te_a) / 1000)


def days_of(e):
    s = set()
    for a, b in [(e["N"] - 600000, e["N"] + 1800000), (e["X"] - 600000, e["X"] + 300000)]:
        s |= {day(a), day(b)}
    return s


def group(e):
    return f"{e['venue']}-{e['src']}"


def main():
    E = load_events()
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        dd = days_of(e)
        try:
            A = load(e["perp"], dd); B = load("BTCUSDT", dd)
        except FileNotFoundError as ex:
            P("missing data", e["coin"], e["N_utc"], ex); continue
        N = e["N"]
        ra, rb = at(A, N - 60000), at(B, N - 60000)
        path = {o: float(np.log(at(A, N + o * 1000) / ra) - np.log(at(B, N + o * 1000) / rb)) for o in OFFS if o != -300}
        r0a, r0b = at(A, N - 360000), at(B, N - 360000)  # pre-stamp drift N - 360 s -> N - 60 s
        path[-300] = float(np.log(ra / r0a) - np.log(rb / r0b)) if np.isfinite(r0a) and np.isfinite(r0b) else np.nan
        a0, a1 = np.searchsorted(A["t"], [N - 300000, N + 300000])
        ta, pa = A["t"][a0:a1], A["p"][a0:a1]
        ib = np.searchsorted(B["t"], ta, "right") - 1
        r = np.log(pa / ra) - np.log(B["p"][np.maximum(ib, 0)] / rb)
        on = {}
        for th in (0.01, 0.02):
            hit = np.where(r >= th)[0]
            on[th] = (ta[hit[0]] - N) / 1000 if len(hit) else None
        s0, s1 = np.searchsorted(A["t"], [N - 600000, N + 300000])
        bins = (A["t"][s0:s1] - (N - 600000)) // 1000
        cnt = np.bincount(bins, minlength=900)[:900]
        base = np.median(cnt[:540]); thr = max(10, 10 * base)
        w = np.where(cnt[300:] >= thr)[0]
        on_b = int(w[0]) - 300 if len(w) else None
        row = dict(e, path=path, on1=on[0.01], on2=on[0.02], on_b=on_b, base=float(base), grp=group(e))
        for c, d, xn in CELLS + [("D10-5m", 10, "5m")]:
            X = N + 300000 if xn == "5m" else e["X"]
            row[c] = trade(e, d, X, A, B)
            row[c + "-x15"] = trade(e, d, X, A, B, 1.5)
        rows.append(row)

    P("# Stream O2 results (bp unless noted). Events", len(rows), "IS", sum(r["era"] == "IS" for r in rows), "VAL", sum(r["era"] == "VAL" for r in rows))
    P("\n## Per event: onset (s vs N; +1 % / +2 % / count burst), path r (bp vs N - 60 s; r(-300) = drift N-360..N-60 s)")
    P("venue coin     era  N(UTC)              src      hold(m)  on1    on2    onB  r(-300) r(-1)  r(0)  r(+2)  r(+5) r(+10) r(+30) r(+60) r(+300)  D5-S net")
    for r in rows:
        f = lambda v: "  --  " if v is None else f"{v:6.1f}"
        p = r["path"]; t5 = r[MAIN]
        P(f"{r['venue']:5s} {r['coin']:8s} {r['era']:4s} {r['N_utc']} {r['src'][:8]:8s} {(r['X']-r['N'])/60000:7.0f} {f(r['on1'])} {f(r['on2'])} {f(r['on_b'])} "
          + " ".join(f"{1e4*p[o]:6.0f}" for o in (-300, -1, 0, 2, 5, 10, 30, 60, 300)) + (f"  {1e4*t5['net']:7.0f}" if t5 else "   --"))
    for era, sel in (("IS", lambda r: r["era"] == "IS"), ("VAL", lambda r: r["era"] == "VAL"),
                     ("VAL OKX", lambda r: r["era"] == "VAL" and r["venue"] == "OKX"), ("VAL Bybit", lambda r: r["era"] == "VAL" and r["venue"] == "Bybit"),
                     ("OKX-bizPTime", lambda r: r["grp"] == "OKX-bizPTime"), ("OKX-pTime", lambda r: r["grp"] == "OKX-pTime"),
                     ("spot", lambda r: r["kind"] == "spot"), ("perp", lambda r: r["kind"] == "perp")):
        S = [r for r in rows if sel(r)]
        if not S:
            continue
        P(f"\n## Path {era} (n {len(S)}): r(t) vs ref N - 60 s, bp: q25 / median / q75 / mean")
        for o in OFFS:
            v = 1e4 * np.array([r["path"][o] for r in S]); v = v[np.isfinite(v)]
            P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f}")
        for k in ("on1", "on2", "on_b"):
            v = np.array([r[k] for r in S if r[k] is not None])
            if len(v):
                P(f"  {k}: n {len(v)}/{len(S)}  median {np.median(v):.1f} s  q25 {np.percentile(v,25):.1f}  q75 {np.percentile(v,75):.1f}  share < 0: {np.mean(v<0):.2f}  share in [0, 5 s]: {np.mean((v>=0)&(v<=5)):.2f}")

    P("\n## Cells (net bp per trade; costs 20 bp + slippage + real funding; t clustered by notice day)")
    P("cell     era  n(days)  gross   slip  fund    net      t   median   SR    x1.5   late   years(net)                       yrs+  power")
    cells = {}
    LATE = {"D5-S": "D10-S", "D2-S": "D5-S", "D10-S": "D30-S", "D30-S": "D60-S", "D60-S": None, "D5-5m": "D10-5m"}
    for c, d, xn in CELLS:
        for era in ("IS", "VAL", "VAL-OKX", "VAL-Bybit"):
            S = [r for r in rows if r[c] is not None and (r["era"] == era or (era == "VAL-OKX" and r["era"] == "VAL" and r["venue"] == "OKX")
                                                        or (era == "VAL-Bybit" and r["era"] == "VAL" and r["venue"] == "Bybit"))]
            if len(S) < 3:
                continue
            net_ = np.array([r[c]["net"] for r in S]); days = [r["day"] for r in S]
            m, t, n = clt(net_, days); sr = net_.mean() / net_.std(ddof=1)
            x15 = np.mean([r[c + "-x15"]["net"] for r in S])
            late = np.mean([r[LATE[c]]["net"] for r in S]) if LATE[c] else np.nan
            yrs = {}
            for r in S:
                yrs.setdefault(r["year"], []).append(r[c]["net"])
            ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
            pw = sr * np.sqrt(N_HOLD) if era == "VAL" else np.nan
            q = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, x15=1e4 * x15, late=1e4 * late,
                     gross=1e4 * np.mean([r[c]["gross"] for r in S]), slip=1e4 * np.mean([r[c]["slip"] for r in S]),
                     fund=1e4 * np.mean([r[c]["fund"] for r in S]), median=1e4 * np.median(net_),
                     years=ys, yrs_pos=f"{sum(np.mean(v)>0 for v in yrs.values())}/{len(yrs)}", power=pw)
            cells[(c, era)] = q
            P(f"{c:8s} {era:9s} {n:3d}({q['days']:2d}) {q['gross']:7.0f} {q['slip']:5.0f} {q['fund']:5.0f} {q['net']:7.0f} {t:6.2f} {q['median']:7.0f} {sr:6.2f} {q['x15']:6.0f} {q['late']:6.0f}  {ys:32s} {q['yrs_pos']:4s} {pw:5.2f}")

    # random benchmark: same coin, same month, 1m klines, hold outside [N - 1 d, N + 1 d]
    rng = np.random.default_rng(66)
    NS = 1000
    P(f"\n## Random benchmark ({NS} draw sets; same coin / month 1m klines, gross; percentile of the event gross mean; max-over-cells t null)")
    KC = {}

    def kl(sym, m):
        if (sym, m) not in KC:
            z = np.load(os.path.join(KL, f"{sym}_{m}.npz")); KC[(sym, m)] = (z["t"], z["o"])
        return KC[(sym, m)]
    rand = {}
    for c, d, xn in CELLS:
        G = np.full((NS, len(rows)), np.nan)
        for j, r in enumerate(rows):
            m = day(r["N"])[:7]
            ta, oa = kl(r["perp"], m); tb, ob = kl("BTCUSDT", m)
            tt, ia, ib = np.intersect1d(ta, tb, return_indices=True)
            oa, ob = oa[ia], ob[ib]
            hold_s = 300 - d if xn == "5m" else (r["X"] - r["N"]) / 1000 - d
            hm = max(1, int(round(hold_s / 60)))
            okk = np.arange(len(tt) - hm)
            okk = okk[(tt[okk + hm] - tt[okk] == hm * 60000) & ((tt[okk + hm] < r["N"] - 86400000) | (tt[okk] > r["N"] + 86400000))]
            u = rng.choice(okk, NS)
            G[:, j] = (oa[u + hm] / oa[u] - 1) - (ob[u + hm] / ob[u] - 1)
        rand[c] = G
    for era in ("IS", "VAL"):
        idx = [j for j, r in enumerate(rows) if r["era"] == era and r[MAIN] is not None]
        days = [rows[j]["day"] for j in idx]
        maxt = np.full(NS, -np.inf)
        for c, G in rand.items():
            jj = [j for j in idx if rows[j][c] is not None]
            ev = np.mean([rows[j][c]["gross"] for j in jj])
            pct = 100 * np.mean(G[:, jj].mean(1) < ev)
            if (c, era) in cells:
                cells[(c, era)]["rand_pct"] = pct
            cost = np.array([COST + rows[j][c]["slip"] for j in jj])
            dj = [rows[j]["day"] for j in jj]
            ts = np.array([clt(G[s, jj] - cost, dj)[1] for s in range(NS)])
            maxt = np.maximum(maxt, ts)
            P(f"  {c:8s} {era:4s} event gross {1e4*ev:7.0f}  random mean {1e4*np.nanmean(G[:, jj]):6.0f}  beats {pct:5.1f} %")
        P(f"  {era}: 95th pct of max-over-{len(rand)}-cells net t under the random null = {np.percentile(maxt, 95):.2f}")
    json.dump({f"{c}|{e}": v for (c, e), v in cells.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as f:
        w = csv.writer(f)
        w.writerow(["venue", "coin", "kind", "era", "day", "N_utc", "src", "xsrc", "hold_min", "on1_s", "on2_s", "onB_s"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{k}" for c, _, _ in CELLS for k in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["venue"], r["coin"], r["kind"], r["era"], r["day"], r["N_utc"], r["src"], r["xsrc"], round((r["X"] - r["N"]) / 60000, 1), r["on1"], r["on2"], r["on_b"]]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [("" if r[c] is None else round(1e4 * r[c][k], 1)) for c, _, _ in CELLS for k in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
