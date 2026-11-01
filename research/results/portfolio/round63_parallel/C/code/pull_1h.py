"""Stream C: pull 1h USDT-M klines from data.binance.vision monthly zips (2019-11..2024-12) for data/binance_1h_full/symbols.csv.
Parsed in memory (zip never extracted); output research/data/binance_1h_full/1h/<SYM>.csv (t ms open, o,h,l,c,vol,qvol,n),
rows with open time < 2025-01-01 only. Global rate limit: >= 0.25 s between request starts. requests.log: time, URL, status, bytes."""
import csv, io, os, sys, threading, time, urllib.request, urllib.error, zipfile
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
OUT = os.path.join(R, "data/binance_1h_full")
os.makedirs(os.path.join(OUT, "1h"), exist_ok=True)
END = 1735689600000
UA = "research-script/1.0"
lock = threading.Lock(); last = [0.0]; loglock = threading.Lock()
logf = open(os.path.join(OUT, "requests.log"), "a")
stop = threading.Event()


def get(url):
    for attempt in range(5):
        if stop.is_set():
            return None, -1
        with lock:
            w = last[0] + 0.25 - time.time()
            if w > 0: time.sleep(w)
            last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read(); st = r.status
        except urllib.error.HTTPError as e:
            b, st = b"", e.code
        except Exception as e:
            b, st = b"", 0
        with loglock:
            logf.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{st},{len(b)}\n"); logf.flush()
        if st == 200: return b, st
        if st == 404: return None, st
        if st == 403:
            stop.set(); return None, st
        time.sleep(5 * (attempt + 1) * (6 if st in (418, 429) else 1))
    return None, st


def months(sym):
    rows = list(csv.reader(open(os.path.join(R, "data/binance/perp_1d", sym + ".csv"))))[1:]
    ms = set()
    for x in rows:
        t = int(float(x[0]))
        if 1572566400000 <= t < END:
            d = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc); ms.add((d.year, d.month))
    return sorted(ms)


def one(sym):
    path = os.path.join(OUT, "1h", sym + ".csv")
    if os.path.exists(path): return sym, "skip", 0
    rows = []; miss = []
    for y, m in months(sym):
        url = f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{y}-{m:02d}.zip"
        b, st = get(url)
        if b is None:
            miss.append(f"{y}-{m:02d}:{st}"); continue
        z = zipfile.ZipFile(io.BytesIO(b))
        for nm in z.namelist():
            for line in z.read(nm).decode().splitlines():
                p = line.split(",")
                if not p or not p[0][:1].isdigit(): continue
                t = int(p[0])
                if t >= END: continue
                rows.append((t, p[1], p[2], p[3], p[4], p[5], p[7], p[8]))
    if stop.is_set(): return sym, "stopped", 0
    rows.sort(); seen = set()
    with open(path + ".tmp", "w") as f:
        f.write("t,o,h,l,c,vol,qvol,n\n")
        for r in rows:
            if r[0] in seen: continue
            seen.add(r[0]); f.write(",".join(map(str, r)) + "\n")
    os.replace(path + ".tmp", path)
    if miss:
        with open(os.path.join(OUT, "missing_months.csv"), "a") as f:
            f.write(sym + "," + ";".join(miss) + "\n")
    return sym, len(seen), len(miss)


if __name__ == "__main__":
    syms = [r["sym"] for r in csv.DictReader(open(os.path.join(OUT, "symbols.csv")))]
    t0 = time.time()
    with ThreadPoolExecutor(6) as ex:
        for k, res in enumerate(ex.map(one, syms)):
            print(k, res, f"{time.time() - t0:.0f}s", flush=True)
    print("done", "403-stop" if stop.is_set() else "")
