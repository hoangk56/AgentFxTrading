"""Round 60 IS / VAL report (HOLD cut). Usage: python -I run.py <perp symbols file> [hold]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import listings as Lm  # noqa: E402

C = Lm.C
hold = len(sys.argv) > 2 and sys.argv[2] == "hold"
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
ser = {s: Lm.load_series(s, hold) for s in syms}
nd = len(ser["BTCUSDT"][0])
Fb, _, fb = ser["BTCUSDT"]
names = list(ser)
QV = np.array([ser[s][1] for s in names])
FIRST = {}
for s in names:
    w = np.where(~np.isnan(ser[s][0]))[0]
    FIRST[s] = int(w[0]) if len(w) else nd
tv = C.trailing_mean(QV, 30)
tv = np.where(np.isnan(tv), -1, tv)
first_arr = np.array([FIRST[s] for s in names])
sf = Lm.spot_first()
EV = Lm.events(syms)
days = C.T0 + C.DAY * np.arange(nd, dtype=np.int64)
months = days.astype("datetime64[ms]").astype("datetime64[M]").astype(int)
yrs = C.years(days)


def era_of(e):
    t = days[e] if e < nd else None
    for k, (a, b) in Lm.ERAS.items():
        if t is not None and a <= t < b:
            return k
    return None


def group(s, L0):
    sp, _ = C.spot_name(s)
    t = sf.get(sp)
    if t is None:
        return "NEW"
    dd = (C.T0 + L0 * C.DAY - t) / C.DAY
    if dd <= 30:
        return "NEW"
    return "OLD" if dd >= 180 else "MID"


def run(k=1, H=30, hedge=True, cm=1.0, side=-1):
    out = []
    for s, L0 in EV:
        if s == "BTCUSDT":
            continue
        e = L0 + k
        if e >= nd - 1:
            continue
        era = era_of(e)
        if era is None or (era == "HOLD" and not hold):
            continue
        Fa, _, fa = ser[s]
        res = Lm.episode(Fa, fa, Fb, fb, e, H, side=side, cost_a=0.0015 * cm, cost_b=0.0006 * cm, hedge=hedge)
        if res is None or (res[2] - e) < min(H, 3):
            continue
        out.append(dict(sym=s, e=e, era=era, r=res[0], adv=res[1], x=res[2], g=group(s, L0)))
    return out


def summarize(eps, label):
    for era in ("IS", "VAL", "HOLD"):
        E = [x for x in eps if x["era"] == era]
        if not E:
            continue
        r = np.array([x["r"] for x in E])
        t = Lm.cluster_t(r, [months[x["e"]] for x in E])
        yy = {int(y): round(100 * np.mean([x["r"] for x in E if yrs[x["e"]] == y]), 1) for y in np.unique([yrs[x["e"]] for x in E])}
        print("%-22s %-4s n %3d mean %+6.2f%% med %+6.2f%% sd %5.1f%% SR/ep %+.3f t_cl %+5.2f yrs %s" % (
            label, era, len(r), 100 * r.mean(), 100 * np.median(r), 100 * r.std(ddof=1), r.mean() / r.std(ddof=1), t, yy))


def random_pct(eps, n_draw=500, k=1, H=30):
    rng = np.random.default_rng(0)
    res = {}
    for era in ("IS", "VAL", "HOLD"):
        E = [x for x in eps if x["era"] == era]
        if not E:
            continue
        real = np.mean([x["r"] for x in E])
        pools = {}
        for x in E:
            e = x["e"]
            ok = (first_arr <= e - 365) & (tv[:, e] > 0)
            idx = np.where(ok)[0]
            idx = idx[np.argsort(-tv[idx, e])][:60]
            pools[e] = [names[i] for i in idx if names[i] != "BTCUSDT"]
        draws = []
        for _ in range(n_draw):
            rr = []
            for x in E:
                pool = pools[x["e"]]
                if not pool:
                    continue
                s = pool[int(rng.integers(len(pool)))]
                Fa, _, fa = ser[s]
                o = Lm.episode(Fa, fa, Fb, fb, x["e"], H)
                if o is not None:
                    rr.append(o[0])
            draws.append(np.mean(rr))
        draws = np.array(draws)
        res[era] = (100 * np.mean(draws < real), 100 * np.median(draws))
    return res


if __name__ == "__main__":
    base = run()
    summarize(base, "N1 k1 H30 hedged")
    summarize(run(cm=1.5), "N1 costs x1.5")
    summarize(run(k=2), "N1 k=2")
    summarize(run(hedge=False), "unhedged")
    for k, H in ((7, 30), (1, 14), (1, 60)):
        summarize(run(k=k, H=H), "k%d H%d" % (k, H))
    for g in ("NEW", "MID", "OLD"):
        summarize([x for x in base if x["g"] == g], "group " + g)
    for era in ("IS", "VAL", "HOLD"):
        E = [x for x in base if x["era"] == era]
        if not E:
            continue
        adv = np.array([x["adv"] for x in E]); r = np.array([x["r"] for x in E])
        w = sorted(E, key=lambda x: x["r"])[:3]
        print(era, "adverse >100%%: %d of %d; worst eps %s; with -100%% cap mean %+.2f%%" % (
            (adv > 1).sum(), len(E), [(x["sym"], round(100 * x["r"])) for x in w], 100 * np.maximum(r, -1.0).mean()))
    print("random benchmark (pct beaten, median random mean %):", random_pct(base))
