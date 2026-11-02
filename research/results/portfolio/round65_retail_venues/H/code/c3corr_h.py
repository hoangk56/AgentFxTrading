"""Daily-P&L correlation of stream H trades with C3 (IS / VAL; P&L booked on the exit day)."""
import csv, os
import numpy as np
DAY, H = 86400000, 3600000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000)}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
C3 = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv"
c3 = {}
for r in csv.DictReader(open(C3)):
    d = int(np.datetime64(r["t_out_utc"][:10], "D").astype(np.int64))
    if d * DAY < ERAS["VAL"][1]:
        c3[d] = c3.get(d, 0.0) + float(r["usd_at_100_risk"])
k = {}
for x in csv.DictReader(open(os.path.join(OUT, "h_trades.csv"))):
    if x.get("te"):
        dd = int((int(x["te"]) + 72 * H) // DAY); k[dd] = k.get(dd, 0.0) + float(x["net"])
for era, (lo, hi) in ERAS.items():
    days = np.arange(lo // DAY, hi // DAY)
    a = np.array([c3.get(int(d), 0.0) for d in days]); b = np.array([k.get(int(d), 0.0) for d in days])
    print(f"H72 {era} days {len(days)} active {(b != 0).sum()} corr {np.corrcoef(a, b)[0, 1]:+.3f}")
