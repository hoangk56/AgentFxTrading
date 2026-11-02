"""Daily-P&L correlation with C3 (IS / VAL only; P&L booked on the exit day), copy of K/code/c3corr.py logic for
L (main set) and pooled K2 + L. Usage: python -I c3corr_l.py"""
import csv, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2
from kdata import DAY, H, ERAS

C3 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv"
c3 = {}
for r in csv.DictReader(open(C3)):
    d = np.datetime64(r["t_out_utc"][:10], "D").astype(np.int64)
    if d * DAY < ERAS["VAL"][1]:
        c3[d] = c3.get(d, 0.0) + float(r["usd_at_100_risk"])
P = pickle.load(open(os.path.join(l2.BD, "l2_trades.pkl"), "rb"))
for name, get in (("L main", lambda h: P["T"]["main7"][0][("e1h", h, 1.0)]),
                  ("pooled K2+L", lambda h: np.vstack([P["KT"][("e1h", h, 1.0)], P["Tn"][("e1h", h, 1.0)]]))):
    for hold in (24, 72):
        a = get(hold)
        k = {}
        for t, net in zip(a[:, 0], a[:, 3]):
            dd = int((t + hold * H) // DAY)
            k[dd] = k.get(dd, 0.0) + net
        for era in ("IS", "VAL"):
            lo, hi = ERAS[era]
            lo = max(lo, 1577836800000)
            days = np.arange(lo // DAY, hi // DAY)
            x = np.array([c3.get(int(x), 0.0) for x in days]); y = np.array([k.get(int(x), 0.0) for x in days])
            print(f"{name} H{hold} {era} days {len(days)} active {(y != 0).sum()} corr {np.corrcoef(x, y)[0, 1]:+.3f}")
