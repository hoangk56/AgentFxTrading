"""Round 71 FS: data.binance.vision SPOT monthly 1m klines for pull_list.csv -> compact npz (zip decoded in memory,
never written). Run with python -I. Months <= 2024-12 only; rows with open_time >= 2025-01-01 dropped (none exist).
npz: m (int32 minutes since epoch of open time), o h l c (float64), qv (float32), n (int32 trades).
Order: env FS_ORDER file (one 'sym,month' per line) if given, else pull_list order. Budget FS_BUDGET_S seconds.
"""
import csv, io, os, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import net  # noqa: E402

NPZ = os.path.join(net.DATA, "npz")
END_MIN = 1735689600000 // 60000
BASE = "https://data.binance.vision/data/spot/monthly/klines/{s}/1m/{s}-1m-{m}.zip"
BUDGET = float(os.environ.get("FS_BUDGET_S", 45 * 60))
T_START = time.time()


def convert(data, out):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        txt = z.read(z.namelist()[0]).decode("ascii", "replace")
    lines = [ln for ln in txt.splitlines() if ln[:1].isdigit()]
    if not lines:
        np.savez_compressed(out, m=np.zeros(0, np.int32), o=np.zeros(0), h=np.zeros(0), l=np.zeros(0), c=np.zeros(0),
                            qv=np.zeros(0, np.float32), n=np.zeros(0, np.int32))
        return 0
    a = np.loadtxt(io.StringIO("\n".join(lines)), delimiter=",", usecols=(0, 1, 2, 3, 4, 7, 8), ndmin=2)
    t = a[:, 0]
    t = np.where(t > 1e14, t / 1000, t)  # microsecond stamps (not expected <= 2024)
    m = (t // 60000).astype(np.int64)
    k = m < END_MIN
    a, m = a[k], m[k]
    np.savez_compressed(out, m=m.astype(np.int32), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4],
                        qv=a[:, 5].astype(np.float32), n=a[:, 6].astype(np.int32))
    return len(m)


def fetch(p):
    s, m = p
    out = os.path.join(NPZ, f"{s}_{m}.npz")
    if os.path.exists(out) or os.path.exists(out + ".404"):
        return p, "skip"
    if time.time() - T_START > BUDGET:
        return p, "budget"
    b = net.get(BASE.format(s=s, m=m), timeout=40, tries=5)
    if b is None:
        open(out + ".404", "w").close()
        return p, "404"
    if b == "FAIL":
        return p, "fail"
    return p, convert(b, out)


def main():
    os.makedirs(NPZ, exist_ok=True)
    if os.environ.get("FS_ORDER"):
        todo = [tuple(ln.strip().split(",")) for ln in open(os.environ["FS_ORDER"]) if ln.strip()]
    else:
        todo = [(r["sym"], r["month"]) for r in csv.DictReader(open(os.path.join(net.DATA, "pull_list.csv")))]
    todo = [p for p in todo if p[1] <= "2024-12"]
    res = {}
    try:
        with ThreadPoolExecutor(4) as ex:
            for k, (p, st) in enumerate(ex.map(fetch, todo)):
                res[p] = st
                if k % 100 == 0:
                    print(f"{time.time() - T_START:.0f}s {k}/{len(todo)} {p} {st}", flush=True)
    except net.Stop403 as e:
        print("403 STOP", e, flush=True)
        os._exit(3)
    from collections import Counter
    print("done", Counter(v if isinstance(v, str) else "ok" for v in res.values()), f"{time.time() - T_START:.0f}s",
          flush=True)


if __name__ == "__main__":
    main()
