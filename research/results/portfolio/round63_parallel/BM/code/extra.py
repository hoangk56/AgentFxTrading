"""Information only (not pre-declared): +5 min re-priced trades ex B's crash windows, top-5-day / top-5-coin share,
and the gap-persistence profile (deviation from m_h at minutes 0..15). Reads BM/out/reprice_trades.csv."""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "B", "code")))
from basis import cl_t, DAY  # noqa: E402
from run import CRASH  # noqa: E402  (B's crash windows)

R = list(csv.DictReader(open(os.path.join(HERE, "..", "out", "reprice_trades.csv"))))


def col(R, k):
    return np.array([float(r[k]) if r.get(k, "") != "" else np.nan for r in R])


for era in ("IS", "VAL", "HOLD"):
    E = [r for r in R if r["era"] == era]
    t = col(E, "T"); day = t // DAY
    cr = np.zeros(len(E), bool)
    for a, b in CRASH:
        cr |= (t >= np.datetime64(a, "ms").astype(np.int64)) & (t < np.datetime64(b, "ms").astype(np.int64))
    line = [f"{era}:"]
    for k in (0, 5, 15):
        x = col(E, f"net{k}")
        w = ~cr
        line.append(f"+{k} ex-crash n {w.sum()} net {x[w].mean()*1e4:.1f} median {np.median(x[w])*1e4:.1f} "
                    f"t {cl_t(x[w], day[w]):.2f};")
    print(" ".join(line))
    x5 = col(E, "net5")
    u, inv = np.unique(day, return_inverse=True); s = np.bincount(inv, weights=x5)
    names = np.array([r["perp"] for r in E]); uc, ic = np.unique(names, return_inverse=True)
    sc = np.bincount(ic, weights=x5)
    print(f"   +5 top-5 days share {np.sort(s)[-5:].sum() / x5.sum():.2f}, top-5 coins share "
          f"{np.sort(sc)[-5:].sum() / x5.sum():.2f} ({', '.join(uc[np.argsort(-sc)[:5]])})")
    # basis deviation at the entry minute relative to the signal deviation
    for k in (0, 1, 2, 5, 15):
        dev = np.log(col(E, f"Fe{k}") / col(E, f"Se{k}")) - col(E, "m_h")
        print(f"   k={k:2d}: median deviation {np.nanmedian(dev)*1e4:7.1f} bp, median ratio to signal "
              f"deviation {np.nanmedian(dev / col(E, 'd_h')):.2f}")
