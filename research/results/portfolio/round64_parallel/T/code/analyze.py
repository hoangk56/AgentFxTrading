"""Stream T step 3: delisting convergence rules T1 / T2 as declared in ../HYPOTHESES_T.md.
Usage: python -I analyze.py <events_kept.csv> <data-root> <out-dir>
Every series is cut at ts < 2025-01-01 at load."""
import csv, io, json, os, sys, time, zipfile
import numpy as np

CUT = 1735689600000
M, H, DAY = 60000, 3600000, 86400000
ev_file, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(64)
COST = {"T1": 0.0070, "T2": 0.0042}
KS = (0.0, 0.0050, 0.0100)
NREP = 1000

# announcement lead classification (STREAM_T section "Announcement lead"); decided from news before returns
LEAD = {
    "MBLUSDT": "verified", "SNTUSDT": "verified", "STPTUSDT": "verified", "RADUSDT": "verified",
    "UNFIUSDT": "verified", "KEYUSDT": "verified", "RENUSDT": "verified", "LOOMUSDT": "verified",
    "ORBSUSDT": "verified", "XEMUSDT": "verified", "ANTUSDT": "verified", "DGBUSDT": "verified",
    "CTKUSDT": "verified", "CVXUSDT": "verified",
    "LUNAUSDT": "short", "FTTUSDT": "short",
}
EMERGENCY = {"LUNAUSDT", "ANCUSDT", "FTTUSDT", "SRMUSDT", "RAYUSDT"}


def read_zip_rows(path):
    with zipfile.ZipFile(path) as z:
        for nm in z.namelist():
            for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                if x and x[0].isdigit():
                    yield x


def load_k(folder):
    """1m klines -> dict t -> (o, h, l, c, n); ts < CUT only."""
    d = {}
    if not os.path.isdir(folder):
        return d
    for f in sorted(os.listdir(folder)):
        if not f.endswith(".zip"):
            continue
        for x in read_zip_rows(os.path.join(folder, f)):
            t = int(x[0])
            if t > 10 ** 14:
                t //= 1000
            if t >= CUT:
                continue
            d[t] = (float(x[1]), float(x[2]), float(x[3]), float(x[4]), int(float(x[8])))
    return d


def load_f(folder):
    out = []
    if not os.path.isdir(folder):
        return np.zeros((0, 2))
    for f in sorted(os.listdir(folder)):
        if f.endswith(".zip"):
            for x in read_zip_rows(os.path.join(folder, f)):
                t = int(x[0])
                if t < CUT:
                    out.append((t, float(x[2])))
    return np.array(sorted(out)) if out else np.zeros((0, 2))


def fsum(F, a, b):
    if not len(F):
        return 0.0
    m = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[m, 1].sum())


def open_at(K, t, back=False):
    """Open of the first traded bar starting in [t, t + 5 min]; with back=True the last close <= t as fallback."""
    for k in range(6):
        b = K.get(t + k * M)
        if b and b[4] > 0:
            return b[0]
    if back:
        for k in range(1, 61):
            b = K.get(t - k * M)
            if b and b[4] > 0:
                return b[3]
    return None


def gap_at(P, S, fac, t, nmin=5):
    """Mean of ln(perp close / (fac x spot close)) over the nmin 1m bars ending at t (bars starting t-nmin..t-1)."""
    g = []
    for k in range(1, nmin + 1):
        a, b = P.get(t - k * M), S.get(t - k * M)
        if a and b and a[4] > 0 and b[4] > 0:
            g.append(np.log(a[3] / (fac * b[3])))
    return float(np.mean(g)) if len(g) >= 3 else None


def trade(side, P, S, B, FP, FB, E, X, perp_exit):
    """Net-of-funding gross return (fraction) of a T1 / T2 trade entered at E (1m opens), exited at X."""
    pe = open_at(P, E)
    if pe is None:
        return None
    if side == "T1":
        se = open_at(S, E)
        sx = open_at(S, X, back=True)
        if se is None or sx is None or perp_exit is None:
            return None
        rp = -(perp_exit / pe - 1.0)
        rs = sx / se - 1.0
        fund = fsum(FP, E, X)            # short perp receives positive funding
        return dict(price=rp + rs, perp_leg=rp, other=rs, fund=fund, pe=pe, se=se)
    be = open_at(B, E)
    bx = open_at(B, X, back=True)
    if be is None or bx is None or perp_exit is None:
        return None
    rp = perp_exit / pe - 1.0
    rb = -(bx / be - 1.0)
    fund = -fsum(FP, E, X) + fsum(FB, E, X)
    se = open_at(S, E); sx = open_at(S, X, back=True)
    hedged_spot = (rp - (sx / se - 1.0)) if (se and sx) else np.nan   # info: long perp / short spot (needs borrow)
    return dict(price=rp + rb, perp_leg=rp, other=rb, fund=fund, pe=pe, se=se, spot_hedged=hedged_spot)


def cl_t(x, cl):
    x = np.asarray(x, float); cl = np.asarray(cl)
    n = len(x)
    if n < 3:
        return np.nan
    u = np.unique(cl)
    if len(u) < 2:
        return np.nan
    m = x.mean()
    s = sum(((x[cl == c] - m).sum()) ** 2 for c in u)
    g = len(u)
    se = np.sqrt(s * g / (g - 1)) / n
    return m / se if se > 0 else np.nan


events = list(csv.DictReader(open(ev_file)))
BTC = load_k(os.path.join(root, "perp", "BTCUSDT"))
FB = load_f(os.path.join(root, "funding", "BTCUSDT"))
recs, paths, rand_pool, diag = [], {}, [], []
for r in events:
    p, s, fac = r["perp"], r["spot"], float(r["fac"])
    P = load_k(os.path.join(root, "perp", p))
    S = load_k(os.path.join(root, "spot", s))
    FP = load_f(os.path.join(root, "funding", p))
    act = sorted(t for t, b in P.items() if b[4] > 0)
    if not act:
        diag.append((p, "no perp 1m data")); continue
    T = act[-1] + M
    ts_act = sorted(t for t, b in S.items() if b[4] > 0)
    spot_ok = bool(ts_act) and ts_act[-1] >= T - 10 * M
    last = P[act[-1]]
    # settlement proxy: mean of fac x spot closes over [T - 30 min, T)
    sc = [fac * S[t][3] for t in range(T - 30 * M, T, M) if t in S and S[t][4] > 0]
    settle_proxy = float(np.mean(sc)) if sc else None
    path = {}
    for h in range(72, -1, -1):
        g = gap_at(P, S, fac, T - h * H)
        path[h] = g
    paths[p] = path
    yr = time.gmtime(T / 1000).tm_year
    day = T // DAY
    diag.append((p, time.strftime('%Y-%m-%d %H:%M', time.gmtime(T / 1000)), "spot_ok" if spot_ok else "SPOT MISSING AT T",
                 "last perp close %.6g, perp-vs-settle-proxy %s bp" % (last[3], ("%.1f" % (1e4 * np.log(last[3] / settle_proxy))) if settle_proxy else "na"),
                 "first perp bar %s" % time.strftime('%Y-%m-%d %H:%M', time.gmtime(act[0] / 1000)), "spot bars %d" % len(ts_act)))
    if not spot_ok:
        continue
    for lead_h in (24, 6, 48):
        for late in (0, 1):
            E = T - lead_h * H + late * M
            g = gap_at(P, S, fac, T - lead_h * H)
            if g is None:
                continue
            jp = jp_s = np.nan
            b0, b1 = P.get(E), P.get(E - M)
            if b0 and b1 and b0[4] > 0 and b1[4] > 0:
                jp = abs(np.log(b0[0] / b1[3]))
            c0, c1 = S.get(E), S.get(E - M)
            if c0 and c1 and c0[4] > 0 and c1[4] > 0:
                jp_s = abs(np.log(c0[0] / c1[3]))
            for side in ("T1", "T2"):
                for ex_name, px in (("last", last[3]), ("settle", settle_proxy)):
                    tr = trade(side, P, S, BTC, FP, FB, E, T, px)
                    if tr is None:
                        continue
                    tr.update(perp=p, side=side, lead=lead_h, late=late, exit=ex_name, gap=g, T=T, day=int(day), year=yr,
                              lead_class=LEAD.get(p, "unverified"), emergency=p in EMERGENCY, jump_perp=jp, jump_spot=jp_s)
                    recs.append(tr)
    # random benchmark pool: entries in [T - 7 d, T - 48 h] on a 1-minute grid (sampled), hold 24 h at market
    lo, hi = T - 7 * DAY, T - 48 * H
    cand = rng.integers(lo // M, hi // M, size=600) * M
    for R in cand:
        g = gap_at(P, S, fac, int(R))
        if g is None:
            continue
        X = int(R) + 24 * H
        px = open_at(P, X, back=True)
        for side in ("T1", "T2"):
            tr = trade(side, P, S, BTC, FP, FB, int(R), X, px)
            if tr is not None:
                rand_pool.append(dict(perp=p, side=side, gap=g, net0=tr["price"] + tr["fund"], year=yr))

with open(os.path.join(out, "diag.txt"), "w") as f:
    for d in diag:
        f.write(" | ".join(map(str, d)) + "\n")
with open(os.path.join(out, "trades.json"), "w") as f:
    json.dump(recs, f, default=float)
with open(os.path.join(out, "paths.json"), "w") as f:
    json.dump(paths, f)
with open(os.path.join(out, "random_pool.json"), "w") as f:
    json.dump(rand_pool, f)
print("events", len(events), "trades", len(recs), "random pool", len(rand_pool))
