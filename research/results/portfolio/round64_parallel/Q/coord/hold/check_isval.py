"""Check: stream Q's functions as hold_run.py uses them (trades_for -> price_1m -> guard -> stats), on the original
2020-24 data and constants, must reproduce Q1_k100_H72: IS n 54 +439.8 bp t 2.20, VAL n 181 +77.7 t 3.82."""
import os, sys
import numpy as np
QC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "code"))
sys.path.insert(0, QC)
import q, run
pairs = q.load()
T = run.trades_for(pairs, ("Q1", 100, 72))
rows = run.price_1m(pairs, ("Q1", 100, 72), T, run.M1())
K = [r for r in rows if r["guard"] and not np.isnan(r["net"])]
for era, (a, b) in q.ERAS.items():
    s = run.stats([r for r in K if a <= r["te"] < b])
    print(era, s["n"], round(s["net_bp"], 1), round(s["t"], 2))
