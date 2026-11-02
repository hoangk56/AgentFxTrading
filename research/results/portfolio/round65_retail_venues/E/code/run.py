"""Evaluate the 6 declared cells on IS 2016-21 / VAL 2022-24 (no HOLD data is loaded: letf.CUT)."""
import numpy as np
from letf import panel, prev_ref, bigmask, trade, CELLS, hm

rng = np.random.default_rng(65)
days, yr, B, A = panel()
mid, P = prev_ref(B, A)
IS = (yr >= 2016) & (yr <= 2021)
VAL = (yr >= 2022) & (yr <= 2024)
ex2020 = ~((yr == 2020) & np.isin((days.astype("datetime64[D]").astype("datetime64[M]").astype(int) % 12) + 1, [3, 4]))


def st(x):
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan, np.nan, len(x), np.nan
    m, s = x.mean(), x.std(ddof=1)
    return m, m / s * np.sqrt(len(x)), len(x), m / s


def fmt(x):
    m, t, n, _ = st(x)
    return f"{m:+.2f} ({t:+.2f}) n{n}"


res = {}
starts_m = np.arange(hm("10:00"), hm("11:30") + 1)
starts_a = np.arange(hm("13:15"), hm("15:15") + 1)
for name, (sig, dirn, en, ex, q) in CELLS.items():
    s, e, x = hm(sig), hm(en), hm(ex)
    r = np.log(mid[:, s] / P)
    big = bigmask(r, q)
    side = np.where(big, np.sign(r) * dirn, 0).astype(float)
    side[~np.isfinite(side)] = 0
    net, gm = trade(B, A, side, e, x)
    n15, _ = trade(B, A, side, e, x, 1.5)
    nl, _ = trade(B, A, side, e + 1, x + 1)
    res[name] = dict(net=net, mid=gm, n15=n15, nl=nl, side=side, r=r, big=big)
    print(f"== {name} signal {sig} {'follow' if dirn > 0 else 'fade'} {en}->{ex} q{q}")
    for lab, msk in (("IS", IS), ("VAL", VAL)):
        nyr = len(np.unique(yr[msk]))
        cost = np.nanmean(gm[msk] - net[msk])
        m, t, n, sh = st(net[msk])
        print(f"  {lab}: mid {fmt(gm[msk])} | cost {cost:.2f} | net {fmt(net[msk])} | x1.5 {st(n15[msk])[0]:+.2f}"
              f" | late {st(nl[msk])[0]:+.2f} ({st(nl[msk])[1]:+.2f}) | ex-2020MA {st(net[msk & ex2020])[0]:+.2f}"
              f" ({st(net[msk & ex2020])[1]:+.2f}) | n/yr {n / nyr:.1f} | power {sh * np.sqrt(1.82 * n / nyr):+.2f}")
    ys = []
    for y in range(2016, 2025):
        mm = yr == y
        ys.append((y, st(net[mm])[0], st(net[mm])[2]))
    print("  years:", " ".join(f"{y}:{m:+.1f}/{n}" for y, m, n in ys),
          f"| positive {sum(1 for _, m, _ in ys if m > 0)}/{sum(1 for _, m, _ in ys if np.isfinite(m))}")
    # random benchmark: same signal days, random start minute, side recomputed, same window length
    L = x - e
    allowed = np.r_[starts_m[starts_m + 1 + L <= hm("11:59")], starts_a[starts_a + 1 + L <= hm("15:59")]]
    td = np.flatnonzero(side != 0)
    for lab, msk in (("IS", IS), ("VAL", VAL)):
        dd = td[msk[td]]
        act = np.nanmean(net[dd])
        draws = []
        for _ in range(1000):
            ss = rng.choice(allowed, len(dd))
            rr = np.log(mid[dd, ss] / P[dd])
            sd = np.sign(rr) * dirn
            sd[~np.isfinite(sd)] = 0
            nn, _ = trade(B[dd], A[dd], sd, ss + 1, ss + 1 + L)
            draws.append(np.nanmean(nn))
        draws = np.array(draws)
        print(f"  random {lab}: actual {act:+.2f} random mean {draws.mean():+.2f} beats {np.mean(draws < act) * 100:.1f} %")
    if name in ("C4", "C6"):
        small = np.isfinite(r) & ~big & (np.abs(r) > 0)
        sside = np.where(small, np.sign(r), 0).astype(float)
        sn, sg = trade(B, A, sside, e, x)
        print(f"  non-big days same window (follow): IS net {fmt(sn[IS])} mid {st(sg[IS])[0]:+.2f};"
              f" VAL net {fmt(sn[VAL])} mid {st(sg[VAL])[0]:+.2f}")
        h1, h2 = (yr <= 2020), (yr >= 2021)
        print(f"  split: 2016-20 net {fmt(net[h1 & (IS | VAL)])}; 2021-24 net {fmt(net[h2 & (IS | VAL)])}")

# chance: shared per-day sign flips of the gross mid, cost kept
names = list(CELLS)
obs = max(st(res[k]["net"][IS])[1] for k in names)
mx = []
for _ in range(1000):
    f = rng.choice([-1.0, 1.0], len(days))
    ts = []
    for k in names:
        g, nt = res[k]["mid"][IS], res[k]["net"][IS]
        ts.append(st(f[IS] * g - (g - nt))[1])
    mx.append(np.nanmax(ts))
mx = np.array(mx)
print(f"chance: max IS net t observed {obs:+.2f}; null p50 {np.median(mx):.2f} p95 {np.quantile(mx, 0.95):.2f};"
      f" p {np.mean(mx >= obs):.3f}")

# information: gross mid of the C4 window on all days by |r| decile (follow side), IS then VAL
r = res["C4"]["r"]
alls = np.where(np.isfinite(r), np.sign(r), 0).astype(float)
_, g4 = trade(B, A, alls, hm("16:10"), hm("16:28"))
_, g1 = trade(B, A, np.where(np.isfinite(res["C1"]["r"]), np.sign(res["C1"]["r"]), 0).astype(float), hm("15:45"), hm("15:59"))
for lab, msk in (("IS", IS), ("VAL", VAL)):
    for nm, g, rr in (("C4 window 16:10-16:29", g4, r), ("C1 window 15:45-16:00", g1, res["C1"]["r"])):
        ok = msk & np.isfinite(g) & np.isfinite(rr)
        qs = np.quantile(np.abs(rr[ok]), np.linspace(0, 1, 11))
        b = np.clip(np.searchsorted(qs, np.abs(rr[ok]), side="right") - 1, 0, 9)
        print(f"info {lab} {nm} mid by |r| decile:", " ".join(f"{np.mean(g[ok][b == i]):+.1f}" for i in range(10)),
              f"(n {ok.sum()})")

# keep per-trade rows for any later correlation check
rows = []
for k in names:
    for i in np.flatnonzero(np.isfinite(res[k]["net"]) & (IS | VAL)):
        rows.append((k, str(days[i].astype("datetime64[D]")), res[k]["side"][i], res[k]["net"][i]))
with open("../trades_E.csv", "w") as fh:
    fh.write("cell,date_hkt,side,net_bp\n")
    for k, d, s_, n_ in rows:
        fh.write(f"{k},{d},{int(s_)},{n_:.3f}\n")
