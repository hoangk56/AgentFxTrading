"""Stream PX: pull data.binance.vision SPOT monthly PAXGUSDT 1m klines and aggTrades, months 2020-08..2024-12.
Run with python -I. Each zip -> compact npz, zip deleted. Rows with time >= 2025-01-01 dropped (none should exist).
klines npz: m (int32 minute of open_time), o h l c (float64), v (base vol), tb (taker-buy base vol), n (trades).
aggTrades npz: only weekend windows Fri 18:00 UTC .. Mon 08:00 UTC kept: t (int64 ms), p (float64), q (float64),
bm (int8 is_buyer_maker: 1 = seller was taker).
Rate: one request at a time, >= 0.5 s between requests; back off on 418/429/503; stop on 403.
"""
import io, os, sys, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np
D = sys.argv[1]
RAW = os.path.join(D, "raw"); NPZ = os.path.join(D, "npz")
os.makedirs(RAW, exist_ok=True); os.makedirs(NPZ, exist_ok=True)
END_MS = 1735689600000
KL = "https://data.binance.vision/data/spot/monthly/klines/PAXGUSDT/1m/PAXGUSDT-1m-{m}.zip"
AG = "https://data.binance.vision/data/spot/monthly/aggTrades/PAXGUSDT/PAXGUSDT-aggTrades-{m}.zip"
logf = open(os.path.join(D, "requests.log"), "a")
last = [0.0]


def log(url, status, nbytes):
    logf.write(f"{dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')},{url},{status},{nbytes}\n"); logf.flush()


def lines_of(zpath):
    with zipfile.ZipFile(zpath) as z:
        txt = z.read(z.namelist()[0]).decode("ascii", "replace")
    L = txt.splitlines()
    if L and not L[0][:1].isdigit():
        L = L[1:]
    return "\n".join(L)


def conv_kl(zpath, out):
    a = np.loadtxt(io.StringIO(lines_of(zpath)), delimiter=",", usecols=(0, 1, 2, 3, 4, 5, 8, 9), ndmin=2)
    a = a[a[:, 0] < END_MS]
    np.savez_compressed(out, m=(a[:, 0] // 60000).astype(np.int32), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4],
                        v=a[:, 5], n=a[:, 6].astype(np.int32), tb=a[:, 7])
    return len(a)


def conv_ag(zpath, out):
    txt = lines_of(zpath)
    t = np.loadtxt(io.StringIO(txt), delimiter=",", usecols=(5,), dtype=np.int64, ndmin=1)
    pq = np.loadtxt(io.StringIO(txt), delimiter=",", usecols=(1, 2), ndmin=2)
    bm = np.array([1 if ln.split(",")[6].strip().lower() == "true" else 0 for ln in txt.splitlines()], dtype=np.int8)
    # weekend windows only: weekday of t (Mon=0) ; keep Fri >= 18:00, Sat, Sun, Mon < 08:00
    days = t // 86400000
    wd = (days + 3) % 7  # 1970-01-01 was Thursday -> Thu=3
    hr = (t % 86400000) // 3600000
    k = ((wd == 4) & (hr >= 18)) | (wd == 5) | (wd == 6) | ((wd == 0) & (hr < 8))
    k &= t < END_MS
    np.savez_compressed(out, t=t[k], p=pq[k, 0], q=pq[k, 1], bm=bm[k])
    return int(k.sum())


def fetch(url, out, conv):
    if os.path.exists(out) or os.path.exists(out + ".404"):
        return "skip"
    zpath = os.path.join(RAW, os.path.basename(url))
    for attempt in range(5):
        while time.time() - last[0] < 0.5:
            time.sleep(0.05)
        last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60) as r:
                data = r.read()
            log(url, 200, len(data))
            with open(zpath, "wb") as f:
                f.write(data)
            n = conv(zpath, out)
            os.remove(zpath)
            return n
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code == 404:
                open(out + ".404", "w").close(); return 404
            if e.code == 403:
                print("403: stop", flush=True); sys.exit(1)
            if e.code in (418, 429, 503):
                time.sleep(30 * (attempt + 1)); continue
            time.sleep(5)
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0)
            time.sleep(5)
    return "fail"


def months():
    y, m = 2020, 8
    while (y, m) <= (2024, 12):
        yield f"{y}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


if __name__ == "__main__":
    for mo in months():
        r1 = fetch(KL.format(m=mo), os.path.join(NPZ, f"kl_{mo}.npz"), conv_kl)
        r2 = fetch(AG.format(m=mo), os.path.join(NPZ, f"ag_{mo}.npz"), conv_ag)
        print(mo, r1, r2, flush=True)
