"""Tables from the simulator's JSON. Usage: orb_re2_report.py tick.json m1.json"""
import json
import sys
from collections import defaultdict

import numpy as np


def stats(tr):
    if not tr:
        return dict(n=0, wr=0, avg=0, t=0, pf=0, tot=0, dd=0)
    r = np.array([x["r"] for x in tr])
    g, l = r[r > 0].sum(), -r[r < 0].sum()
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.r_[0, eq])[1:] - eq).max()
    t = r.mean() / r.std(ddof=1) * np.sqrt(len(r)) if len(r) > 1 and r.std() > 0 else 0
    return dict(n=len(r), wr=(r > 0).mean() * 100, avg=r.mean(), t=t, pf=g / l if l else np.inf, tot=r.sum(), dd=dd)


def row(name, s):
    return (f"| {name} | {s['n']} | {s['wr']:.1f} | {s['avg']:+.3f} | {s['t']:+.2f} | {s['pf']:.2f} | "
            f"{s['tot']:+.1f} | {s['dd']:.1f} |")


HEAD = "| variant | n | win % | avg R | t | PF | total R | max DD R |\n|---|---|---|---|---|---|---|---|"


def by_year(tr):
    y = defaultdict(list)
    for x in tr:
        y[x["date"][:4]].append(x["r"])
    return {k: (len(v), sum(v)) for k, v in sorted(y.items())}


def rolling(tr_all, sessions_dates, win=23):
    """All consecutive 23-session windows, trades mapped onto session dates."""
    r_by_d = {x["date"]: x["r"] for x in tr_all}
    v = np.array([r_by_d.get(d, 0.0) for d in sessions_dates])
    out_tot, out_pf, out_n = [], [], []
    for i in range(len(v) - win + 1):
        w = v[i:i + win]
        g, l = w[w > 0].sum(), -w[w < 0].sum()
        out_tot.append(w.sum())
        out_n.append((w != 0).sum())
        out_pf.append(g / l if l > 0 else (np.inf if g > 0 else 0))
    return np.array(out_tot), np.array(out_pf), np.array(out_n)


def main():
    data = {}
    for p in sys.argv[1:]:
        data.update(json.loads(open(p).read()))
    for key, blob in data.items():
        tr = blob["trades"]
        print(f"\n## {key}  (sessions in base: {blob['sessions']['base']})\n\n{HEAD}")
        for nm, t in tr.items():
            print(row(nm, stats(t)))
        base = tr["base"]
        print("\nbase by year (n, total R):", {k: f"{n}/{v:+.1f}" for k, (n, v) in by_year(base).items()})
        ex = defaultdict(int)
        for x in base:
            ex[x["why"]] += 1
        print("base exits:", dict(ex))
        if base:
            sl = np.array([x["sl"] for x in base])
            m = np.array([x["mins_after_or"] for x in base])
            o = np.array([x["overshoot"] for x in base])
            rr = np.array([x["r"] for x in base])
            spread = np.array([x["spread"] for x in base])
            print(f"entry mins after OR: median {np.median(m):.1f}, share at first minute of the live window "
                  f"{(m <= m.min() + 1).mean() * 100:.0f}% | overshoot in R: median {np.median(o):.3f} p90 "
                  f"{np.percentile(o, 90):.3f} | last 60 trades SL {sl[-60:].mean():.2f} px, spread/SL "
                  f"{(spread / sl).mean() * 100:.2f}%")
            for lo, hi in ((0, .1), (.1, .25), (.25, .5), (.5, 9)):
                k = (o >= lo) & (o < hi)
                if k.sum():
                    print(f"  overshoot {lo}-{hi}R: n {k.sum()} avg R {rr[k].mean():+.3f}")
            for side in (1, -1):
                k = np.array([x["side"] == side for x in base])
                if k.sum():
                    print(f"  side {side:+d}: n {k.sum()} avg R {rr[k].mean():+.3f}")
            for since, lab in (("2023", "2023+"), ("2025", "2025+")):
                print(" ", lab, row("base", stats([x for x in base if x["date"] >= since])))
            d = sorted({x["date"] for x in base})
            # session calendar: every weekday in span is good enough for a window measure
            import datetime as dt
            a, b = dt.date.fromisoformat(d[0]), dt.date.fromisoformat(d[-1])
            cal = [(a + dt.timedelta(days=i)).isoformat() for i in range((b - a).days + 1)
                   if (a + dt.timedelta(days=i)).weekday() < 5]
            tot, pf, n = rolling(base, cal)
            print(f"rolling 23 sessions: trades median {np.median(n):.0f}; total R p5 {np.percentile(tot, 5):+.1f} "
                  f"median {np.median(tot):+.1f} p95 {np.percentile(tot, 95):+.1f}; share windows PF>=3.73 "
                  f"{(pf >= 3.73).mean() * 100:.1f}%; share total>0 {(tot > 0).mean() * 100:.1f}%")
    # M1 vs tick agreement
    for s in ("XAUUSD", "US30", "USTEC"):
        a, b = data.get(f"{s}|tick"), data.get(f"{s}|m1")
        if a and b:
            ta = {x["date"]: x for x in a["trades"]["base"]}
            tb = {x["date"]: x for x in b["trades"]["base"]}
            both = set(ta) & set(tb)
            same = sum(ta[d]["side"] == tb[d]["side"] for d in both)
            diff = np.array([ta[d]["r"] - tb[d]["r"] for d in both])
            print(f"\n{s} tick vs m1: tick n {len(ta)}, m1 n {len(tb)}, common {len(both)}, same side {same}, "
                  f"mean |dR| {np.abs(diff).mean():.3f}, avg R tick {stats(a['trades']['base'])['avg']:+.3f} "
                  f"m1 {stats(b['trades']['base'])['avg']:+.3f}")


main()
