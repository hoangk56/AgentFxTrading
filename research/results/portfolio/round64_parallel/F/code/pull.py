"""Stream F: pull data.binance.vision USDT-M monthly 1m klines for pull_list.csv, convert each zip to a compact npz,
delete the zip. Run with python -I. Months <= 2024-12 only; rows with open_time >= 2025-01-01 are dropped (none exist).
Rate: 4 worker threads, >= 0.25 s between request starts (global), back off on 418/429/503, stop on 403.
npz: m (int32 minutes since epoch of open_time), o h l c (float32), qv (float32 quote volume), n (int32 trades).
"""
import csv, io, os, sys, threading, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks")
RAW = os.path.join(D, "raw"); NPZ = os.path.join(D, "npz")
END_MIN = 1735689600000 // 60000
BASE = "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1m/{s}-1m-{m}.zip"
lock = threading.Lock(); last = [0.0]; stop = [False]
logf = open(os.path.join(D, "requests.log"), "a")


def log(url, status, nbytes):
    with lock:
        logf.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{status},{nbytes}\n"); logf.flush()


def pace():
    while True:
        with lock:
            now = time.time()
            if now - last[0] >= 0.25:
                last[0] = now; return
        time.sleep(0.05)


def convert(zpath, out):
    with zipfile.ZipFile(zpath) as z:
        name = z.namelist()[0]
        txt = z.read(name).decode("ascii", "replace")
    lines = txt.splitlines()
    if lines and not lines[0][:1].isdigit():
        lines = lines[1:]
    a = np.loadtxt(io.StringIO("\n".join(lines)), delimiter=",", usecols=(0, 1, 2, 3, 4, 7, 8), ndmin=2)
    m = (a[:, 0] // 60000).astype(np.int64)
    k = m < END_MIN
    a, m = a[k], m[k]
    np.savez_compressed(out, m=m.astype(np.int32), o=a[:, 1].astype(np.float32), h=a[:, 2].astype(np.float32),
                        l=a[:, 3].astype(np.float32), c=a[:, 4].astype(np.float32), qv=a[:, 5].astype(np.float32),
                        n=a[:, 6].astype(np.int32))
    return len(m)


def fetch(s, m):
    out = os.path.join(NPZ, f"{s}_{m}.npz")
    if os.path.exists(out) or os.path.exists(out + ".404"):
        return "skip"
    url = BASE.format(s=s, m=m)
    zpath = os.path.join(RAW, f"{s}-1m-{m}.zip")
    for attempt in range(5):
        if stop[0]:
            return "stop"
        pace()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=40) as r:
                data = r.read()
            log(url, 200, len(data))
            with open(zpath, "wb") as f:
                f.write(data)
            n = convert(zpath, out)
            os.remove(zpath)
            return n
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code == 404:
                open(out + ".404", "w").close(); return 404
            if e.code == 403:
                stop[0] = True; return 403
            if e.code in (418, 429, 503):
                time.sleep(30 * (attempt + 1)); continue
            time.sleep(5)
        except Exception as e:  # timeouts, resets
            log(url, "ERR:" + type(e).__name__, 0)
            time.sleep(5)
    return "fail"


def main():
    rows = list(csv.DictReader(open(os.path.join(D, "pull_list.csv"))))
    todo = [(r["sym"], r["month"]) for r in rows if r["month"] <= "2024-12"]
    # order: odd calendar months first (Jan, Mar, ...) over all years, then even months, so a time cut keeps both eras
    todo.sort(key=lambda p: (int(p[1][5:]) % 2 == 0, p[1], p[0]))
    q = list(reversed(todo)); res = {}
    t0 = time.time()

    def worker():
        while True:
            with lock:
                if not q or stop[0]:
                    return
                s, m = q.pop()
            res[(s, m)] = fetch(s, m)
    th = [threading.Thread(target=worker) for _ in range(6)]
    for t in th: t.start()
    while any(t.is_alive() for t in th):
        time.sleep(30)
        print(f"{time.time() - t0:.0f}s done {len(res)}/{len(todo)}", flush=True)
    from collections import Counter
    print(Counter(type(v).__name__ if isinstance(v, int) and v not in (403, 404) else v for v in res.values()))


if __name__ == "__main__":
    main()
