"""Mechanism check M (descriptive): Binance spot SYM/BTC 1h closes around Upbit W / D notices (KRW market), 2020-24.
Gross short-alt-vs-BTC return = -(P(x)/P(e) - 1), e = close of the 1h bar starting at floor_hour(N) + 1 h."""
import os, sys, csv, io, zipfile, glob, json
import numpy as np
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/spot1h"
W = os.path.join(os.path.dirname(__file__), "..")
H = 3600000; DAY = 86400000; CUT = 1735689600000
_S = {}


def series(sym):
    if sym not in _S:
        rows = []
        for f in sorted(glob.glob(os.path.join(D, sym + "-1h-*.zip"))):
            with zipfile.ZipFile(f) as z:
                for nm in z.namelist():
                    for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                        try:
                            t = int(x[0]); c = float(x[4]); v = float(x[7])
                        except (ValueError, IndexError):
                            continue
                        if t < CUT:
                            rows.append((t, c, v))
        a = np.array(sorted(set(rows))) if rows else np.zeros((0, 3))
        _S[sym] = {int(t): (c, v) for t, c, v in a}
    return _S[sym]


def ret(s, e, h):
    a, b = s.get(e), s.get(e + h * H)
    if not a or not b or a[0] <= 0:
        return np.nan
    return -(b[0] / a[0] - 1)


rows = list(csv.DictReader(open(os.path.join(W, "events_all.csv"))))
keep, last = [], {}
for r in rows:
    if r["cls"] not in ("W", "D") or (r["markets"] and "KRW" not in r["markets"]):
        continue
    k = (r["cls"], r["coin"]); t = int(r["t"])
    if k in last and t - last[k] < 30 * DAY:
        continue
    last[k] = t; keep.append(r)
rng = np.random.default_rng(67)
res = []
for r in keep:
    s = series(r["coin"] + "BTC")
    if not s:
        continue
    N = int(r["t"]); e = N // H * H + H
    if e not in s:
        continue
    pre = s.get(N // H * H - 24 * H)
    run = (s[e][0] / pre[0] - 1) if pre else np.nan
    vol24 = sum(s.get(e - k * H, (0, 0))[1] for k in range(1, 25))
    rr = dict(cls=r["cls"], coin=r["coin"], t=r["t_utc"], era="IS" if N < 1640995200000 else "VAL", run=run, btcvol24=vol24)
    for h in (24, 72):
        rr[f"g{h}"] = ret(s, e, h)
        hrs = N // H * H - rng.integers(7 * 24, 40 * 24, 300) * H
        rr[f"rb{h}"] = [x for x in (ret(s, int(q), h) for q in hrs) if np.isfinite(x)]
    res.append(rr)
out = []
for c in ("W", "D"):
    for era in ("IS", "VAL"):
        for h in (24, 72):
            sub = [x for x in res if x["cls"] == c and x["era"] == era and np.isfinite(x[f"g{h}"]) and len(x[f"rb{h}"])]
            if not sub:
                out.append(f"{c}{h} {era}: n 0"); continue
            g = np.array([x[f"g{h}"] for x in sub]) * 1e4
            draws = np.array([np.mean([rng.choice(x[f"rb{h}"]) for x in sub]) for _ in range(500)]) * 1e4
            day = [x["t"][:10] for x in sub]; _, inv = np.unique(day, return_inverse=True)
            gs = np.bincount(inv, weights=g - g.mean()); G = len(gs)
            se = np.sqrt((gs ** 2).sum() * G / max(G - 1, 1)) / len(g) if G > 1 else np.nan
            yrs = {}
            for x, v in zip(sub, g):
                yrs.setdefault(x["t"][:4], []).append(v)
            runs = np.array([x["run"] for x in sub]) * 100
            out.append(f"{c}{h} {era}: n {len(g)} gross mean {g.mean():+.0f} bp (t clustered by day {g.mean() / se:+.2f}, {G} days) median {np.median(g):+.0f} "
                       f"win {100 * (g > 0).mean():.0f}% | random same coin N-40..-7 d: median of means {np.median(draws):+.0f}, beats {100 * (draws < g.mean()).mean():.0f}% "
                       f"| run-up N-24h->entry median {np.nanmedian(runs):+.1f}% | years {dict((y, (len(v), round(float(np.mean(v))))) for y, v in sorted(yrs.items()))}")
open(os.path.join(W, "mcheck_output.txt"), "w").write("\n".join(out) + "\n\nper event:\n" + "\n".join(
    f'{x["cls"]} {x["coin"]:6s} {x["t"]} {x["era"]} run {100 * x["run"]:+6.1f}% g24 {1e4 * x["g24"]:+6.0f} g72 {1e4 * x["g72"]:+6.0f} btcvol24 {x["btcvol24"]:.2f}' for x in res))
print("\n".join(out)); print(len(res), "events with spot")
