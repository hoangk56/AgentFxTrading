"""Round 66 N0: data.binance.vision futures/um monthly 1m klines for each listing (months covering launch day .. day 31,
never a month after 2024-12) and BTCUSDT 2020-01..2024-12. Run with `python -I`; zips decoded in memory, not saved.
Writes research/data/perp_launch/k1m/<SYM>.npz: ot (open time ms), o, h, l, c, n (trades); alts cut to
[launch day, launch day + 31 d) and < 2025-01-01."""
import io, json, os, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import net  # noqa: E402

DAY = 86400000
END = 1735689600000
OUT = os.path.join(net.DATA, "k1m")
BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
BUDGET = float(os.environ.get("N0_BUDGET_S", 30 * 60))


def months(a, b):
    m0 = np.datetime64(int(a), "ms").astype("datetime64[M]"); m1 = np.datetime64(int(b) - 1, "ms").astype("datetime64[M]")
    return [str(m) for m in np.arange(m0, m1 + 1) if str(m) <= "2024-12"]


def get_month(sym, m):
    url = f"{BASE}/{sym}/1m/{sym}-1m-{m}.zip"
    r = net.open_url(url, timeout=30)
    if r is None:
        net.log(url, 404, 0, "missing")
        return None
    try:
        b = r.read()
    finally:
        r.close()
    net.log(url, 200, len(b), "GET")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        raw = z.read(z.namelist()[0])
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    if not raw.strip():
        return np.zeros((0, 6))
    a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(0, 1, 2, 3, 4, 8), dtype=np.float64, ndmin=2)
    return a


def job(sym, lo, hi):
    fn = os.path.join(OUT, f"{sym}.npz")
    if os.path.exists(fn):
        return sym, "cached"
    parts = []
    for m in months(lo, hi):
        a = get_month(sym, m)
        if a is not None:
            parts.append(a)
    a = np.concatenate(parts) if parts else np.zeros((0, 6))
    if len(a) and a[:, 0].max() > 1e14:
        a[:, 0] //= 1000
    a = a[(a[:, 0] >= lo) & (a[:, 0] < min(hi, END))]
    a = a[np.argsort(a[:, 0], kind="stable")]
    tmp = fn + ".tmp.npz"
    np.savez_compressed(tmp, ot=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4],
                        n=a[:, 5].astype(np.int64))
    os.replace(tmp, fn)
    return sym, f"ok {len(a)}"


def main():
    import events
    os.makedirs(OUT, exist_ok=True)
    E = events.events()
    jobs = [("BTCUSDT", 1577836800000, END)] + [(e["sym"], e["day0"], e["day0"] + 31 * DAY) for e in E]
    t0 = time.time(); st = {}
    with ThreadPoolExecutor(2) as ex:
        futs = {}
        for j in jobs:
            futs[ex.submit(job, *j)] = j[0]
        for k, f in enumerate(futs):
            try:
                s, r = f.result()
            except net.Stop403 as x:
                print("403 STOP", x, flush=True); os._exit(3)
            except Exception as x:
                s, r = futs[f], "ERR " + repr(x)[:100]
                print(s, r, flush=True)
            st[s] = r
            if k % 25 == 0:
                print(f"{time.time() - t0:6.0f}s {k}/{len(jobs)} {s} {r}", flush=True)
            if time.time() - t0 > BUDGET:
                print("budget hit", flush=True); ex.shutdown(wait=False, cancel_futures=True); break
    json.dump(st, open(os.path.join(net.DATA, "progress_k1m.json"), "w"))
    print("done", len(st), time.time() - t0, flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
