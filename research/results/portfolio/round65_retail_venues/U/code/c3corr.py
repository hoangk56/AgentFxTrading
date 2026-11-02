"""Daily-P&L correlation of U cells with C3 (IS / VAL only; P&L booked on the exit day). Usage: c3corr.py <cell>..."""
import csv, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udata import DAY, H, ERAS, UV
C3 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv"
c3 = {}
for r in csv.DictReader(open(C3)):
    d = int(np.datetime64(r["t_out_utc"][:10], "D").astype(np.int64))
    if d * DAY < ERAS["VAL"][1]:
        c3[d] = c3.get(d, 0.0) + float(r["usd_at_100_risk"])
tr = pickle.load(open(os.path.join(UV, "u_trades.pkl"), "rb"))["trades"]
for cell in sys.argv[1:]:
    hold = int(cell.split("H")[-1])
    k = {}
    for z in tr[cell]:
        p, f, _ = z["r"]["e1h"]
        dd = int((z["T"] + H + hold * H) // DAY)
        k[dd] = k.get(dd, 0.0) + p + f - 0.0042
    for era, (lo, hi) in ERAS.items():
        days = np.arange(lo // DAY, hi // DAY)
        x = np.array([c3.get(int(d), 0.0) for d in days]); y = np.array([k.get(int(d), 0.0) for d in days])
        print(f"{cell} {era} days {len(days)} active {(y != 0).sum()} corr {np.corrcoef(x, y)[0, 1]:+.3f}")
