"""Registered HOLD run of PREREG_K2 (run once): k2rule on k2_hold_events.csv. DEMO bar: net mean > 0."""
import csv, os, sys, datetime as dt, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k2rule as k
ev = list(csv.DictReader(open(os.path.join(k.D, "k2_hold_events.csv"))))
rows, r15, r2h = [], [], []
for r in ev:
    x = k.trade(r["sym"], int(r["L"]))
    if x is None:
        print("no prices", r["coin"]); continue
    rows.append(x); r15.append(x[1] + x[2] - 1.5 * k.COST)
    y = k.trade(r["sym"], int(r["L"]), off=2 * k.H); r2h.append(y[3] if y else np.nan)
a = np.array(rows); day = (a[:, 0] // k.DAY).astype(int)
m, t, n = k.clt(a[:, 3], day)
yr = np.array([dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).year for x in a[:, 0]])
print(f"HOLD n {n} net {m*1e4:+.0f} bp t {t:.2f} median {np.median(a[:,3])*1e4:+.0f} worst {a[:,3].min()*1e4:+.0f} best {a[:,3].max()*1e4:+.0f} gross {a[:,1].mean()*1e4:+.0f} funding {a[:,2].mean()*1e4:+.0f}")
print(f"  x1.5 net {np.mean(r15)*1e4:+.0f}; L+2h entry net {np.nanmean(r2h)*1e4:+.0f} (n {int(np.isfinite(r2h).sum())})")
for y in np.unique(yr):
    print(f"  {y}: n {(yr==y).sum()} net {a[yr==y,3].mean()*1e4:+.0f}")
print("PASS (DEMO bar: net > 0)" if m > 0 else "FAIL (net <= 0): drop")
np.save(os.path.join(k.D, "k2_hold_trades.npy"), a)
