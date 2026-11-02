"""Daily P&L correlation of a Q cell (1m net, guard passed, by exit day) with C3 (r by exit day), IS / VAL only.
Usage: python -I corr_c3.py <cell>"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
C3 = os.path.join(HERE, "..", "..", "..", "trades_C3_gotobi_jpy_basket.csv")
cell = sys.argv[1]
ERAS = {"IS": ("2020-01-01", "2021-12-31"), "VAL": ("2022-01-01", "2024-12-31")}
c3 = {}
for r in csv.DictReader(open(C3)):
    if r["era"] not in ("IS", "VAL"):
        continue
    d = r["t_out_utc"][:10]
    c3[d] = c3.get(d, 0.0) + float(r["r"])
qd = {}
for r in csv.DictReader(open(os.path.join(OUT, f"trades_{cell}.csv"))):
    if r["guard"] != "1" or r["net"] in ("", "nan"):
        continue
    v = float(r["net"])
    if np.isnan(v):
        continue
    d = str(np.datetime64(int(float(r["tx"])), "ms"))[:10]
    qd[d] = qd.get(d, 0.0) + v
for era, (a, b) in ERAS.items():
    days = np.arange(np.datetime64(a), np.datetime64(b) + 1)
    days = [str(d) for d in days]                     # all calendar days (crypto trades every day, C3 = 0 on weekends)
    x = np.array([qd.get(d, 0.0) for d in days]); y = np.array([c3.get(d, 0.0) for d in days])
    both = np.array([d in qd for d in days])
    print(era, "days", len(days), "Q days", int(both.sum()), "corr", round(float(np.corrcoef(x, y)[0, 1]), 3))
