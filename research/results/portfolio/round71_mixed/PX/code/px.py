"""Stream PX: PAXG weekend deviation vs gold's reopen. Declared in ../HYPOTHESES_PX.md (6 cells + placebo P).
Run from the repo root: research/.venv/bin/python -m research.results.portfolio.round71_mixed.PX.code.px
(or with PYTHONPATH=repo root). Everything cut at ts < 2025-01-01."""
import glob, os, sys, datetime as dt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, ROOT)
from research.m1 import load  # noqa: E402

D = os.path.join(ROOT, "research", "data", "paxg_weekend", "npz")
END_MIN = 1735689600000 // 60000
MIN0 = 1598486400000 // 60000  # 2020-08-27
FEE = 10.0
rng = np.random.default_rng(71)


def utc(m):
    return dt.datetime.fromtimestamp(int(m) * 60, dt.timezone.utc)


# ---------- PAXG minute grid (forward-filled closes) ----------
ms, cs, ns = [], [], []
for f in sorted(glob.glob(os.path.join(D, "kl_*.npz"))):
    z = np.load(f)
    ms.append(z["m"].astype(np.int64)); cs.append(z["c"]); ns.append(z["n"])
pm = np.concatenate(ms); pc = np.concatenate(cs); pn = np.concatenate(ns)
k = pm < END_MIN; pm, pc, pn = pm[k], pc[k], pn[k]
P0 = pm[0]
grid = np.full(END_MIN - P0, np.nan); grid[pm - P0] = pc
ntr = np.zeros(END_MIN - P0, dtype=np.int64); ntr[pm - P0] = pn
idx = np.where(~np.isnan(grid), np.arange(len(grid)), 0); np.maximum.accumulate(idx, out=idx); grid = grid[idx]


def P(m):  # PAXG close of the bar starting at minute m
    i = int(m) - P0
    return grid[i] if 0 <= i < len(grid) else np.nan


# ---------- gold mid ----------
g = load("XAUUSD")
gm_ = g["ts"] // 60000
k = (gm_ >= MIN0) & (gm_ < END_MIN)
gm = gm_[k]; gmid = (g["c"][k] + g["ca"][k]) / 2
gpos = {int(x): i for i, x in enumerate(gm)}


def G(m):  # gold mid close at the last bar <= m
    i = np.searchsorted(gm, m, side="right") - 1
    return gmid[i]


# ---------- aggTrades half-spread ----------
at, ap, ab = [], [], []
for f in sorted(glob.glob(os.path.join(D, "ag_*.npz"))):
    z = np.load(f); at.append(z["t"]); ap.append(z["p"]); ab.append(z["bm"])
at = np.concatenate(at); ap = np.concatenate(ap); ab = np.concatenate(ab)
o = np.argsort(at, kind="stable"); at, ap, ab = at[o], ap[o], ab[o]
pair = (np.diff(ab) != 0) & (np.diff(at) <= 5000)
pair_t = at[1:][pair]; pair_hs = np.abs(np.diff(ap))[pair] / ap[1:][pair] / 2 * 1e4


def hs_at(m):
    a, b = np.searchsorted(pair_t, [(m - 5) * 60000, (m + 6) * 60000])
    return float(np.median(pair_hs[a:b])) if b - a >= 3 else np.nan


# ---------- DFF ----------
dff = {}
for ln in open(os.path.join(ROOT, "research", "data", "rates", "DFF.csv")).read().splitlines()[1:]:
    d, v = ln.split(",")
    try:
        dff[d] = float(v)
    except ValueError:
        pass


def dff_bp(m0, m1):
    d = utc(m0).date()
    for _ in range(10):
        if d.isoformat() in dff:
            return dff[d.isoformat()] / 100 * (m1 - m0) / 525600 * 1e4
        d -= dt.timedelta(days=1)
    return 0.0


# ---------- events ----------
def build(weekday):
    gaps = np.diff(gm)
    out = []
    if weekday:
        sel = np.flatnonzero((gaps >= 50) & (gaps <= 180))
    else:
        sel = np.flatnonzero(gaps > 30 * 60)
    for i in sel:
        F, R = int(gm[i]), int(gm[i + 1])
        fd = utc(F)
        if weekday:
            if fd.weekday() > 3:
                continue
            T = (F // 60 + 1) * 60
            A = F - 48 * 60
            j = np.searchsorted(gm, A, side="right") - 1
            if j < 0 or F - gm[j] > 48 * 60 + 120 or gm[j] < P0:
                continue
            Am = int(gm[j])
            w = (np.log(P(T - 1) / P(Am)) - np.log(gmid[i] / gmid[j])) * 1e4
        else:
            if F < P0:
                continue
            T = (R // 1440) * 1440 + 21 * 60
            while R - T < 60:
                T -= 1440
            w = np.log(P(T - 1) / P(F)) * 1e4
        if T + 1 >= END_MIN or R + 240 >= END_MIN:
            continue
        qF = P(F) / gmid[i]
        mon6 = (R // 1440) * 1440 + 6 * 60
        while mon6 <= R:
            mon6 += 1440
        e, e1 = P(T), P(T + 1)
        x30, x4 = P(R + 30), P(R + 240)
        r = dict(F=F, R=R, T=T, w=w, gap_h=(R - F) / 60, year=utc(T).year,
                 era="IS" if utc(T).year <= 2021 else "VAL",
                 r30=np.log(x30 / e) * 1e4, r4=np.log(x4 / e) * 1e4,
                 r30L=np.log(x30 / e1) * 1e4, r4L=np.log(x4 / e1) * 1e4,
                 hs_in=hs_at(T), hs_in1=hs_at(T + 1), hs_30=hs_at(R + 30), hs_4=hs_at(R + 240),
                 dff30=dff_bp(T, R + 30), dff4=dff_bp(T, R + 240),
                 ggap=np.log(G(R) / gmid[i]) * 1e4,
                 prem_T=w, prem_R30=np.log(x30 / (G(R + 30) * qF)) * 1e4,
                 prem_R4=np.log(x4 / (G(R + 240) * qF)) * 1e4,
                 prem_M6=np.log(P(mon6) / (G(mon6) * qF)) * 1e4,
                 rM6=np.log(P(mon6) / e) * 1e4, gT_R30=np.log(G(R + 30) / G(R)) * 1e4,
                 ntr_T=int(ntr[T - P0]), wF2T_pax=w)
        out.append(r)
    return out


def tab(ev):
    keys = ev[0].keys()
    return {k: np.array([e[k] for e in ev]) for k in keys}


W = tab(build(False))
Wd = tab(build(True))


def fill_hs(E, ref=None):
    # weekday nights have no aggTrades kept (weekend windows only): use the weekend era median (conservative)
    ref = E if ref is None else ref
    for c in ("hs_in", "hs_in1", "hs_30", "hs_4"):
        for era in ("IS", "VAL"):
            m = (E["era"] == era)
            med = np.nanmedian(ref[c][ref["era"] == era])
            E[c] = np.where(m & np.isnan(E[c]), med, E[c])
    return E


W_raw = {k: v.copy() for k, v in W.items()}
fill_hs(W); fill_hs(Wd, W_raw)
CELLS = [("L30-X30", +1, 30, "30"), ("L30-X4h", +1, 30, "4"), ("L60-X30", +1, 60, "30"),
         ("L60-X4h", +1, 60, "4"), ("S30-X4h", -1, 30, "4"), ("S60-X4h", -1, 60, "4")]


def net(E, side, x, mult=1.0, late=False):
    r = E["r" + x + ("L" if late else "")]
    hin = E["hs_in1"] if late else E["hs_in"]
    cost = (2 * FEE + hin + E["hs_" + x]) * mult
    d = E["dff" + x] if side > 0 else 0.0
    return side * r - cost - d


def sig(E, side, k, w=None):
    w = E["w"] if w is None else w
    return (w <= -k) if side > 0 else (w >= k)


def st(x):
    n = len(x)
    if n < 2:
        return n, (x.mean() if n else np.nan), np.nan, np.nan
    s = x.std(ddof=1)
    return n, x.mean(), x.mean() / (s / np.sqrt(n)), x.mean() / s


def fmt(n, m, t, sr):
    return f"n {n:3d} net {m:+7.2f} t {t:+5.2f} SR {sr:+.2f}"


def report(E, label):
    print(f"\n=== {label} ===")
    for name, side, k, x in CELLS:
        for era in ("IS", "VAL"):
            em = E["era"] == era
            s = sig(E, side, k) & em
            nt = net(E, side, x)[s]
            gross = side * E["r" + x][s]
            n, m, t, sr = st(nt)
            ys = []
            for y in sorted(set(E["year"][em])):
                yy = nt[E["year"][s] == y]
                ys.append(f"{y}:{yy.mean():+.1f}({len(yy)})" if len(yy) else f"{y}:-")
            x15 = net(E, side, x, 1.5)[s].mean() if s.any() else np.nan
            late = net(E, side, x, late=True)[s].mean() if s.any() else np.nan
            # R1 random weekends
            allnet = net(E, side, x)[em]
            if n >= 1:
                draws = np.array([rng.choice(allnet, n, replace=False).mean() for _ in range(2000)])
                r1 = (draws < m).mean() * 100
            else:
                r1 = np.nan
            print(f"{name:8s} {era:3s} {fmt(n, m, t, sr)} gross {gross.mean() if n else np.nan:+7.2f} "
                  f"x1.5 {x15:+7.2f} late {late:+7.2f} R1 {r1:5.1f}% | {' '.join(ys)}")


def maxnull(E, label, cells):
    print(f"\n--- max-over-cells null (permute w within era), {label} ---")
    for era in ("IS", "VAL"):
        em = E["era"] == era
        obs = []
        for name, side, k, x in cells:
            obs.append(st(net(E, side, x)[sig(E, side, k) & em])[2])
        obs = np.nan_to_num(np.array(obs), nan=-9)
        wv = E["w"].copy()
        nulls = []
        for _ in range(2000):
            w2 = wv.copy(); ii = np.flatnonzero(em); w2[ii] = rng.permutation(wv[ii])
            tt = [st(net(E, side, x)[sig(E, side, k, w2) & em])[2] for name, side, k, x in cells]
            nulls.append(np.nanmax(np.nan_to_num(tt, nan=-9)))
        nulls = np.array(nulls)
        print(f"{era}: best observed t {obs.max():+.2f} ({cells[int(obs.argmax())][0]}), "
              f"p(max null >= obs) {(nulls >= obs.max()).mean():.3f}, null 95% {np.quantile(nulls, .95):+.2f}")


if __name__ == "__main__":
    E = W
    print("weekends:", {e: int((E['era'] == e).sum()) for e in ('IS', 'VAL')},
          "irregular (gap>52h):", int((E['gap_h'] > 52).sum()))
    print("weekday-night placebo events:", {e: int((Wd['era'] == e).sum()) for e in ('IS', 'VAL')})
    print("\nweekend deviation w (bp) quantiles 1/5/10/25/50/75/90/95/99, |w|>=30, |w|>=60 shares")
    for era in ("IS", "VAL"):
        w = E["w"][E["era"] == era]
        q = np.quantile(w, [.01, .05, .1, .25, .5, .75, .9, .95, .99])
        print(era, " ".join(f"{v:+.0f}" for v in q), f"| sd {w.std():.0f} | <=-30 {np.mean(w <= -30):.2f} "
              f"<=-60 {np.mean(w <= -60):.2f} >=30 {np.mean(w >= 30):.2f} >=60 {np.mean(w >= 60):.2f}")
        for y in sorted(set(E["year"][E["era"] == era])):
            wy = E["w"][E["year"] == y]
            print(f"   {y}: n {len(wy)} sd {wy.std():.0f} |w| med {np.median(np.abs(wy)):.0f} "
                  f"<=-30 {int((wy <= -30).sum())} <=-60 {int((wy <= -60).sum())} >=30 {int((wy >= 30).sum())} "
                  f">=60 {int((wy >= 60).sum())}")
    print("\nhalf-spread (bp) measured: median / p90 per era at entry T, exit R+30, exit R+4h; share measured")
    raw = tab(build(False))
    for era in ("IS", "VAL"):
        m = raw["era"] == era
        s = []
        for c in ("hs_in", "hs_30", "hs_4"):
            v = raw[c][m]
            s.append(f"{c} {np.nanmedian(v):.2f}/{np.nanquantile(v, .9):.2f} ({np.mean(~np.isnan(v)):.2f})")
        print(era, " | ".join(s), f"| trades in entry minute median {np.median(raw['ntr_T'][m]):.0f}")
    print("\npath by w bucket (means, bp): w | gold reopen gap | PAXG T->R+30, T->R+4h, T->Mon06 | "
          "premium at T, R+30, R+4h, Mon06")
    B = [(-1e9, -60), (-60, -30), (-30, 30), (30, 60), (60, 1e9)]
    for era in ("IS", "VAL"):
        for lo, hi in B:
            m = (E["era"] == era) & (E["w"] > lo) & (E["w"] <= hi) if lo > -1e9 else (E["era"] == era) & (E["w"] <= hi)
            if hi == 1e9:
                m = (E["era"] == era) & (E["w"] >= lo)
            if not m.any():
                continue
            f = lambda c: E[c][m].mean()
            print(f"{era} ({lo:>5.0f},{hi:>5.0f}] n {m.sum():3d} | w {f('w'):+6.1f} | gap {f('ggap'):+6.1f} | "
                  f"{f('r30'):+6.1f} {f('r4'):+6.1f} {f('rM6'):+6.1f} | {f('prem_T'):+6.1f} {f('prem_R30'):+6.1f} "
                  f"{f('prem_R4'):+6.1f} {f('prem_M6'):+6.1f}")
        m = E["era"] == era
        b = np.polyfit(E["w"][m], E["ggap"][m], 1)[0]
        b2 = np.polyfit(E["w"][m], E["r4"][m], 1)[0]
        print(f"{era}: slope gold gap on w {b:+.2f}, slope PAXG T->R+4h on w {b2:+.2f}, corr(w, gap) "
              f"{np.corrcoef(E['w'][m], E['ggap'][m])[0, 1]:+.2f}")
    report(W, "weekend cells (declared)")
    report({k: v[W["gap_h"] <= 52] for k, v in W.items()}, "check: regular weekends only (gap <= 52 h)")
    report(Wd, "placebo P: weekday nights (anchor present), w' = premium change over 48 h")
    maxnull(W, "4 long cells", CELLS[:4])
    maxnull(W, "all 6 cells", CELLS)
    np.savez(os.path.join(ROOT, "research", "data", "paxg_weekend", "events_weekend.npz"), **W)
