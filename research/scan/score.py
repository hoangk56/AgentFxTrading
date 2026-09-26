"""Score results/bank_stats.csv per symbol group: t per period, strict pass = mean > 0 and t >= 2 in P1, P2, P3."""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

GROUPS = {"FX": ["AUDUSD", "EURUSD", "GBPUSD", "USDCAD"], "JPY": ["AUDJPY", "EURJPY", "GBPJPY", "USDJPY"],
          "IDX": ["DE40", "UK100", "US30", "USTEC"], "XAU": ["XAUUSD"], "BTC": ["BTCUSD"], "ETH": ["ETHUSD"]}
GROUPS["FX8"] = GROUPS["FX"] + GROUPS["JPY"]
GROUPS["ALL"] = sorted({s for g in ("FX8", "IDX", "XAU", "BTC", "ETH") for s in GROUPS[g]})
for s in GROUPS["ALL"]:
    GROUPS.setdefault(s, [s])


def load(path):
    d = defaultdict(lambda: [0, 0.0, 0.0])
    with open(path) as fh:
        for row in csv.DictReader(fh):
            k = (row["config"], row["symbol"], row["period"])
            d[k] = [int(row["n"]), float(row["sum_r"]), float(row["sum_r2"])]
    return d


def tstat(n, s, s2):
    if n < 2:
        return (s / n if n else 0.0), 0.0
    mu = s / n
    var = (s2 - n * mu * mu) / (n - 1)
    return mu, (mu / math.sqrt(var / n) if var > 0 else 0.0)


def score(d, group):
    configs = sorted({k[0] for k in d})
    out = []
    for c in configs:
        cells = []
        for P in ("P1", "P2", "P3"):
            n = s = s2 = 0
            for sym in GROUPS[group]:
                x = d.get((c, sym, P))
                if x:
                    n += x[0]; s += x[1]; s2 += x[2]
            mu, t = tstat(n, s, s2)
            cells.append((n, mu, t))
        out.append((min(c_[2] for c_ in cells), c, cells))
    return sorted(out, reverse=True)


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "results" / (sys.argv[2] if len(sys.argv) > 2 else "bank_stats.csv")
    d = load(path)
    groups = sys.argv[1].split(",") if len(sys.argv) > 1 else ["ALL", "FX8", "FX", "JPY", "IDX", "XAU", "BTC", "ETH"]
    for g in groups:
        res = score(d, g)
        npass = sum(1 for r in res if r[0] >= 2)
        print(f"== {g}: {len(res)} configs, strict pass {npass}; top 8 by min t:")
        for mt, c, cells in res[:8]:
            print(f"  {c:48s} " + " | ".join(f"n{n:5d} {mu:+.3f} t{t:+5.1f}" for n, mu, t in cells))
