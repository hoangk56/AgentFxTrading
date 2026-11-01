"""Stream C: symbols ever in the top 60 (trailing-30-day perp quote volume, aged >= 60 d) 2020-01-01..2024-12-31."""
import csv, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(R, "results/portfolio/round60_new_listings/code"))
import listings as Lm  # noqa
DAY = 86400000; T0 = 1567296000000; END = 1735689600000; IS0 = 1577836800000
nd = (END - T0) // DAY
d1 = os.path.join(R, "data/binance/perp_1d")
syms = sorted(f[:-4] for f in os.listdir(d1) if f.endswith("USDT.csv"))
syms = [s for s in syms if Lm.base_of(s) not in Lm.EXCL_BASE]
QV = np.full((len(syms), nd), np.nan)
for i, s in enumerate(syms):
    rows = list(csv.reader(open(os.path.join(d1, s + ".csv"))))[1:]
    if not rows: continue
    a = np.array(rows, dtype=float)
    a = a[a[:, 0] < END]
    d = ((a[:, 0] - T0) // DAY).astype(int)
    QV[i, d] = a[:, 6]
first = np.array([np.argmax(~np.isnan(r)) if (~np.isnan(r)).any() else nd for r in QV])
d0 = (IS0 - T0) // DAY
t40 = np.zeros(len(syms), int); t60 = np.zeros(len(syms), int)
for d in range(d0, nd):
    tv = np.nanmean(QV[:, d - 30:d], axis=1)
    ok = (~np.isnan(QV[:, d])) & (d - first >= 60) & np.isfinite(tv)
    idx = np.where(ok)[0]; idx = idx[np.argsort(-tv[idx])]
    t40[idx[:40]] += 1; t60[idx[:60]] += 1
e40 = [syms[i] for i in np.where(t40 > 0)[0]]
e60 = [syms[i] for i in np.where(t60 > 0)[0]]
print("ever top40", len(e40), "ever top60", len(e60))
order = sorted(np.where(t60 > 0)[0], key=lambda i: (-int(t40[i] > 0), -t60[i]))
out = [syms[i] for i in order][:212]
with open(os.path.join(R, "data/binance_1h_full/symbols.csv"), "w") as f:
    f.write("sym,days_top40,days_top60,first_day_ms\n")
    for s in out:
        i = syms.index(s); f.write(f"{s},{t40[i]},{t60[i]},{T0 + DAY * first[i]}\n")
print(len(out), "written")
