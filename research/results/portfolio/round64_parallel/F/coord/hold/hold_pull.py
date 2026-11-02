"""Pull HOLD 1m USDT-M klines from data.binance.vision for hold pull_list.csv: monthly files 2025-01..2026-09,
daily files 2026-10-01..2026-10-29. Same converter / pacing as stream F pull.py (>= 0.25 s, back off 418/429/503,
stop on 403). npz per file in research/data/binance_1m_wicks_hold/npz. Run with python -I."""
import csv, io, os, threading, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks_hold"); RAW = os.path.join(D, "raw"); NPZ = os.path.join(D, "npz")
END_MIN = 1793318400000 // 60000
MON = "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1m/{s}-1m-{m}.zip"
DAYU = "https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{m}.zip"
lock = threading.Lock(); last = [0.0]; stop = [False]
os.makedirs(RAW, exist_ok=True); os.makedirs(NPZ, exist_ok=True)
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
        txt = z.read(z.namelist()[0]).decode("ascii", "replace")
    lines = txt.splitlines()
    if lines and not lines[0][:1].isdigit():
        lines = lines[1:]
    if not lines:
        np.savez_compressed(out, m=np.zeros(0, np.int32), o=np.zeros(0, np.float32), h=np.zeros(0, np.float32),
                            l=np.zeros(0, np.float32), c=np.zeros(0, np.float32), qv=np.zeros(0, np.float32), n=np.zeros(0, np.int32))
        return 0
    a = np.loadtxt(io.StringIO("\n".join(lines)), delimiter=",", usecols=(0, 1, 2, 3, 4, 7, 8), ndmin=2)
    t0 = a[:, 0]
    t0 = np.where(t0 > 1e14, t0 // 1000, t0)  # microsecond timestamps in newer files
    m = (t0 // 60000).astype(np.int64); k = m < END_MIN; a, m = a[k], m[k]
    np.savez_compressed(out, m=m.astype(np.int32), o=a[:, 1].astype(np.float32), h=a[:, 2].astype(np.float32),
                        l=a[:, 3].astype(np.float32), c=a[:, 4].astype(np.float32), qv=a[:, 5].astype(np.float32),
                        n=a[:, 6].astype(np.int32))
    return len(m)


def fetch(s, m, daily):
    out = os.path.join(NPZ, f"{s}_{m}.npz")
    if os.path.exists(out) or os.path.exists(out + ".404"):
        return "skip"
    url = (DAYU if daily else MON).format(s=s, m=m); zpath = os.path.join(RAW, f"{s}-1m-{m}.zip")
    for attempt in range(5):
        if stop[0]:
            return "stop"
        pace()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=40) as r:
                data = r.read()
            log(url, 200, len(data))
            open(zpath, "wb").write(data); n = convert(zpath, out); os.remove(zpath); return n
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code == 404:
                open(out + ".404", "w").close(); return 404
            if e.code == 403:
                stop[0] = True; return 403
            if e.code in (418, 429, 503):
                time.sleep(30 * (attempt + 1)); continue
            time.sleep(5)
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0); time.sleep(5)
    return "fail"


def main():
    rows = list(csv.DictReader(open(os.path.join(D, "pull_list.csv"))))
    todo = []
    for r in rows:
        if r["month"] <= "2026-09":
            todo.append((r["sym"], r["month"], False))
        elif r["month"] == "2026-10":
            for d in range(1, 30):
                todo.append((r["sym"], f"2026-10-{d:02d}", True))
    q = list(reversed(todo)); res = {}; t0 = time.time()

    def worker():
        while True:
            with lock:
                if not q or stop[0]:
                    return
                s, m, dly = q.pop()
            res[(s, m)] = fetch(s, m, dly)
    th = [threading.Thread(target=worker) for _ in range(4)]
    for t in th: t.start()
    while any(t.is_alive() for t in th):
        time.sleep(30); print(f"{time.time() - t0:.0f}s done {len(res)}/{len(todo)}", flush=True)
    from collections import Counter
    print(Counter(v if isinstance(v, str) or v in (403, 404) else "ok" for v in res.values()))


if __name__ == "__main__":
    main()
