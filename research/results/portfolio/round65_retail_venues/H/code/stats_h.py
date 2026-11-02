"""Stats for stream H trades: per era / year / overlap class; t clustered by entry day (k2rule.clt).
Usage: python -I stats_h.py > ../h_output.txt"""
import csv, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from k2rule import clt
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DAY = 86400000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000)}
T = [x for x in csv.DictReader(open(os.path.join(OUT, "h_trades.csv"))) if x.get("te")]
te = np.array([int(x["te"]) for x in T]); yr = np.array([int(time.gmtime(t / 1000).tm_year) for t in te])
cls = np.array([x["cls"] for x in T])
col = lambda k: np.array([float(x[k]) if x[k] != "" else np.nan for x in T])
NET = col("net")


def line(name, w, k="net"):
    v = col(k)[w]; ok = np.isfinite(v); v = v[ok]; d = (te[w][ok] // DAY)
    if len(v) < 2:
        return f"{name}: n {len(v)}"
    m, t, n = clt(v, d)
    by = {int(y): (int((yr[w][ok] == y).sum()), round(float(v[yr[w][ok] == y].mean() * 1e4))) for y in np.unique(yr[w][ok])}
    return (f"{name}: n {n} mean {m*1e4:+.0f} t {t:.2f} median {np.median(v)*1e4:+.0f} sd {v.std(ddof=1)*1e4:.0f} "
            f"SR {m/v.std(ddof=1):.3f} win {(v>0).mean():.2f} worst {v.min()*1e4:+.0f} best {v.max()*1e4:+.0f} years {by}")


print("trades with fills:", len(T))
groups = {"all": np.ones(len(T), bool), "joint": np.char.startswith(cls.astype(str), "joint"),
          "bithumb_only": np.char.startswith(cls.astype(str), "bithumb_only")}
for c in sorted(set(cls)):
    groups[c] = cls == c
for era, (lo, hi) in ERAS.items():
    ew = (te >= lo) & (te < hi)
    print(f"\n=== {era} ===")
    for g, gw in groups.items():
        w = ew & gw
        if w.sum() == 0:
            continue
        print(line(f"[{g}] H72 net", w))
        if g in ("all", "joint", "bithumb_only"):
            for k in ("price", "fund", "net_x15", "net_late5", "net_late2h", "net_h24", "runup"):
                v = col(k)[w]
                print(f"   {k}: mean {np.nanmean(v)*1e4:+.0f} median {np.nanmedian(v)*1e4:+.0f}" + ("" if k in ("price", "fund", "runup") else "   | " + line(k, w, k)))
            v = NET[w]; o = np.argsort(v)
            print("   drop best:", f"{np.delete(v, o[-1]).mean()*1e4:+.0f}", " worst 3:", [(T[i]["coin"], round(NET[i]*1e4)) for i in np.where(w)[0][np.argsort(NET[w])[:3]]],
                  " best 3:", [(T[i]["coin"], round(NET[i]*1e4)) for i in np.where(w)[0][np.argsort(NET[w])[-3:]]])
