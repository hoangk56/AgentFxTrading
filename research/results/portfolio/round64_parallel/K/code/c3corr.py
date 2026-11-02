"""Daily-P&L correlation of K2 cells with C3 (IS / VAL only; P&L booked on the exit day, zero on other days)."""
import csv, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kdata import DAY, H, ERAS

C3 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv"
c3 = {}
for r in csv.DictReader(open(C3)):
    d = np.datetime64(r["t_out_utc"][:10], "D").astype(np.int64)
    if d * DAY < ERAS["VAL"][1]:
        c3[d] = c3.get(d, 0.0) + float(r["usd_at_100_risk"])
d = pickle.load(open(os.path.join(os.path.dirname(__file__), "..", "k2_trades.pkl"), "rb"))
for hold in (24, 72):
    a = d["T"][("e1h", hold, 1.0)]
    k = {}
    for t, net in zip(a[:, 0], a[:, 3]):
        dd = int((t + hold * H) // DAY)
        k[dd] = k.get(dd, 0.0) + net
    for era in ("IS", "VAL"):
        lo, hi = ERAS[era]
        lo = max(lo, 1577836800000)
        days = np.arange(lo // DAY, hi // DAY)
        x = np.array([c3.get(int(x), 0.0) for x in days]); y = np.array([k.get(int(x), 0.0) for x in days])
        print(f"H{hold} {era} days {len(days)} K2 active days {(y != 0).sum()} corr {np.corrcoef(x, y)[0, 1]:+.3f}")
