"""Information only (rule unchanged): Q1 cell on 1m - concentration, ex crash windows, side, jump proxy at entry,
exits after 1 h, leg split. Usage: python -I info_q1.py <cell>"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import run
from q import M, ERAS
cell = sys.argv[1]
R = [r for r in csv.DictReader(open(os.path.join(run.OUT, f"trades_{cell}.csv")))]
R = [r for r in R if r["guard"] == "1" and r["net"] not in ("", "nan")]
m1 = run.M1()
CR = (("2020-03-01", "2020-03-31"), ("2021-05-17", "2021-05-24"), ("2022-05-07", "2022-05-20"), ("2022-11-06", "2022-11-20"))
for era, (a, b) in ERAS.items():
    K = [r for r in R if a <= int(r["te"]) < b]
    net = np.array([float(r["net"]) for r in K])
    day = [run.day_of(int(r["te"])) for r in K]
    tot = net.sum()
    dd = {}
    for d, v in zip(day, net):
        dd[d] = dd.get(d, 0) + v
    top = sorted(dd.items(), key=lambda x: -x[1])[:5]
    print(f"== {era} n {len(K)} days {len(dd)} net {net.mean()*1e4:.1f} median {np.median(net)*1e4:.1f}")
    print(" top-5 days share", round(sum(v for _, v in top) / tot * 100), "%", [(d, round(v / tot * 100)) for d, v in top])
    ex = np.array([not any(x <= d <= y for x, y in CR) for d in day])
    if ex.sum() > 2:
        print(f" ex crash windows n {ex.sum()} net {net[ex].mean()*1e4:.1f} t {run.cl_t(net[ex], np.array([int(r['te'])//86400000 for r in K])[ex]):.2f} median {np.median(net[ex])*1e4:.1f}")
    side = np.array([float(r["side"]) for r in K])
    for s, lab in ((1, "long COIN-M (cm cheap)"), (-1, "short COIN-M (cm rich)")):
        w = side == s
        if w.sum():
            print(f" {lab}: n {w.sum()} net {net[w].mean()*1e4:.1f}")
    hold = np.array([int(r["x"]) - int(r["e"]) for r in K])
    print(f" exits after 1 h: n {(hold==1).sum()} net {net[hold==1].mean()*1e4:.1f}; longer: n {(hold>1).sum()} net {net[hold>1].mean()*1e4 if (hold>1).sum() else float('nan'):.1f}")
    # jump proxy: |open(T+1m) / close(T) - 1| for each leg (close of the first minute after the hour, then next open)
    jA, jU = [], []
    for r in K:
        te = int(r["te"]); A = r["A"]; U = r["U"]
        for mk, sym, L in (("cm", A, jA), ("um", U, jU)):
            c0 = m1.bar(mk, sym, te, "c", slack=0); o1 = m1.bar(mk, sym, te + M, "o", slack=0)
            if not (np.isnan(c0) or np.isnan(o1)):
                L.append(abs(o1 / c0 - 1) * 1e4)
    for lab, L in (("COIN-M leg", jA), ("USDT-M leg", jU)):
        if L:
            print(f" jump |o(T+1m)/c(T..T+1m)-1| {lab}: median {np.median(L):.1f} p75 {np.percentile(L,75):.1f} p90 {np.percentile(L,90):.1f} bp")
    coins = {}
    for r, v in zip(K, net):
        coins.setdefault(r["coin"], []).append(v)
    print(" top coins by P&L", [(k, len(v), round(np.mean(v)*1e4)) for k, v in sorted(coins.items(), key=lambda x: -sum(x[1]))[:6]])
