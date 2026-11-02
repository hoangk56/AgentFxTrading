"""Run the 4 declared cells of ../HYPOTHESES_L3F.md (IS / VAL only, cut at 2025-01-01)."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3f  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rng = np.random.default_rng(71)

P, U, rank = l3f.build_universe()
syms = P["syms"]
nd = U.shape[1]
idx = {s: i for i, s in enumerate(syms)}
ever = set(np.array(syms)[U[:, : int((l3f.CUT - l3f.T0) // l3f.DAY)].any(axis=1)]) | {"BTCUSDT", "ETHUSDT"}
ever = sorted(ever)
print("symbols ever in top 10 (+BTC/ETH):", len(ever))

rows = []   # one per stamp of an ever-top-10 coin
missing = []
for s in ever:
    fd = l3f.load_funding(s)
    o, c, src = l3f.load_1h(s)
    if fd is None or src is None:
        missing.append((s, fd is None, src is None))
        continue
    ft, ff, f8 = fd
    ev5 = l3f.trailing_pct_flags(ft, f8, 5)
    ev10 = l3f.trailing_pct_flags(ft, f8, 10)
    i = idx[s]
    for j, T in enumerate(ft):
        if T < l3f.IS[0] or T >= l3f.VAL[1]:
            continue
        d = int((T - l3f.T0) // l3f.DAY)
        dprev = d - 1
        in12 = s in ("BTCUSDT", "ETHUSDT") or (0 <= dprev < nd and U[i, dprev])
        if not in12:
            continue
        sg = l3f.day_sign(o, c, T)
        if sg == 0:
            continue
        rk = int(rank[i, dprev]) if 0 <= dprev < nd else 9999
        rec = dict(sym=s, T=int(T), sg=sg, f8=float(f8[j]), ev5=bool(ev5[j]), ev10=bool(ev10[j]),
                   u2=s in ("BTCUSDT", "ETHUSDT"), cost=l3f.cost_rt(s, rk))
        ok = True
        for late in (0, 1):
            tr = l3f.trade(o, c, ft, ff, T, 1, late=late)
            if tr is None:
                ok = False
                break
            # unsigned: price R and funding sum F (long pays F): net(side) = side*(R - F) - cost
            rec["R%d" % late] = tr[0]
            rec["F%d" % late] = -tr[1]
            rec["te%d" % late] = tr[2]
            rec["tx%d" % late] = tr[3]
        if ok:
            rows.append(rec)
print("missing data:", missing)
print("pool stamps:", len(rows))

A = {k: np.array([r[k] for r in rows]) for k in rows[0]}
era = np.where(A["T"] < l3f.IS[1], 0, 1)
year = (A["T"].astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970)
eday = A["te0"] // l3f.DAY


def select(mask, late=0):
    """Apply one-position-per-coin to stamps in mask (time order). Returns index array."""
    order = np.where(mask)[0]
    order = order[np.argsort(A["T"][order], kind="stable")]
    busy = {}
    keep = []
    for k in order:
        s = A["sym"][k]
        if busy.get(s, -1) > A["te%d" % late][k] - 1:   # still held at this entry
            continue
        keep.append(k)
        busy[s] = A["tx%d" % late][k]
    return np.array(keep, dtype=int)


def net(k, side=None, late=0, cm=1.0):
    sd = A["sg"][k] if side is None else side
    return sd * (A["R%d" % late][k] - A["F%d" % late][k]) - cm * A["cost"][k]


CELLS = {"C1": ("u2", 5), "C2": ("u2", 10), "C3": ("u12", 5), "C4": ("u12", 10)}


def cell_mask(name):
    u, q = CELLS[name]
    m = A["ev%d" % q].copy()
    if u == "u2":
        m &= A["u2"]
    return m


def summ(k, x):
    out = {}
    for e, nm in ((0, "IS"), (1, "VAL")):
        sel = era[k] == e
        xs = x[sel]
        if len(xs) < 3:
            out[nm] = dict(n=int(len(xs)))
            continue
        out[nm] = dict(n=int(len(xs)), mean_bp=float(xs.mean() * 1e4), sd_bp=float(xs.std(ddof=1) * 1e4),
                       sr=float(xs.mean() / xs.std(ddof=1)), t_cl=float(l3f.cluster_t(xs, eday[k][sel])),
                       days=int(len(np.unique(eday[k][sel]))))
    yrs = {}
    for y in range(2020, 2025):
        sel = year[k] == y
        yrs[str(y)] = (float(x[sel].mean() * 1e4), int(sel.sum())) if sel.any() else (None, 0)
    out["years"] = yrs
    return out


pool_masks = {"u2": A["u2"], "u12": np.ones(len(rows), dtype=bool)}
res = {}
for nm in CELLS:
    k = select(cell_mask(nm))
    x = net(k)
    r = summ(k, x)
    r["x1.5"] = summ(k, net(k, cm=1.5))
    kl = select(cell_mask(nm), late=1)
    r["late"] = summ(kl, net(kl, late=1))
    up = A["sg"][k] > 0
    r["long_upday"] = summ(k[up], x[up])
    r["short_downday"] = summ(k[~up], x[~up])
    r["gross_price"] = summ(k, A["sg"][k] * A["R0"][k])
    r["funding"] = summ(k, -A["sg"][k] * A["F0"][k])
    # daily book NW: book return per entry day = mean of trades entered that day (equal weight), zeros elsewhere
    for e, en in ((0, "IS"), (1, "VAL")):
        sel = era[k] == e
        lo, hi = (l3f.IS if e == 0 else l3f.VAL)
        d0, d1 = lo // l3f.DAY, hi // l3f.DAY
        book = np.zeros(d1 - d0)
        cnt = np.zeros(d1 - d0)
        np.add.at(book, eday[k][sel] - d0, x[sel])
        np.add.at(cnt, eday[k][sel] - d0, 1)
        book = np.where(cnt > 0, book / np.maximum(cnt, 1), 0.0)
        r[en]["t_nw_book"] = float(l3f.nw_t(book)) if en in r and "mean_bp" in r[en] else None
    res[nm] = r

# random benchmarks
ND = 1000
for nm in CELLS:
    k = select(cell_mask(nm))
    u, _ = CELLS[nm]
    for e, en in ((0, "IS"), (1, "VAL")):
        sel = era[k] == e
        n = int(sel.sum())
        if n < 3:
            continue
        real = net(k[sel]).mean()
        pool = np.where(pool_masks[u] & (era == e))[0]
        rnd = np.array([net(rng.choice(pool, n, replace=False)).mean() for _ in range(ND)])
        shf = np.array([net(k[sel], side=rng.choice([-1, 1], n)).mean() for _ in range(ND)])
        res[nm][en]["rand_entry_pct"] = float((rnd < real).mean() * 100)
        res[nm][en]["shuffled_side_pct"] = float((shf < real).mean() * 100)

# max-over-cells null on IS t (random entries, same n per cell)
maxt = []
cellk = {nm: select(cell_mask(nm)) for nm in CELLS}
for _ in range(ND):
    ts = []
    for nm in CELLS:
        k = cellk[nm]
        n = int((era[k] == 0).sum())
        pool = np.where(pool_masks[CELLS[nm][0]] & (era == 0))[0]
        kk = rng.choice(pool, n, replace=False)
        ts.append(l3f.cluster_t(net(kk), eday[kk]))
    maxt.append(np.nanmax(ts))
maxt = np.array(maxt)
best = max(CELLS, key=lambda nm: res[nm]["IS"].get("t_cl", -9))
res["selected_on_IS"] = best
res["maxcell_null_pct"] = float((maxt < res[best]["IS"]["t_cl"]).mean() * 100)
res["maxcell_null_t95"] = float(np.percentile(maxt, 95))
res["pool_n"] = {"IS": int((era == 0).sum()), "VAL": int((era == 1).sum())}

with open(os.path.join(OUT, "results_L3F.json"), "w") as f:
    json.dump(res, f, indent=1)


def line(tag, r):
    s = []
    for en in ("IS", "VAL"):
        z = r.get(en, {})
        if "mean_bp" in z:
            s.append("%s n %d mean %+.1f bp t %.2f sr %.3f" % (en, z["n"], z["mean_bp"], z["t_cl"], z["sr"]))
        else:
            s.append("%s n %d" % (en, z.get("n", 0)))
    print("  %-14s %s" % (tag, " | ".join(s)))


for nm in CELLS:
    r = res[nm]
    print(nm, CELLS[nm])
    for tag in ("net", "x1.5", "late", "long_upday", "short_downday", "gross_price", "funding"):
        line(tag, r if tag == "net" else r[tag])
    print("  years", r["years"])
    for en in ("IS", "VAL"):
        z = r.get(en, {})
        print("  %s rand_entry %.1f%% shuffled %.1f%% t_nw_book %s" % (en, z.get("rand_entry_pct", np.nan),
              z.get("shuffled_side_pct", np.nan), z.get("t_nw_book")))
print("selected", best, "maxcell null pct", res["maxcell_null_pct"], "t95", res["maxcell_null_t95"])
print("pool", res["pool_n"])
