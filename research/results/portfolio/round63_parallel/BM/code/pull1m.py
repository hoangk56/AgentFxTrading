"""Stream BM step 3: 1m klines per trade of B's rule, window [T - 3 min, X + 20 min].
Usage: python -I pull1m.py perp|spot <trades_b.csv> <out-root>
Writes <out-root>/<kind>/<SYM>_<T>.csv (t,o,h,l,c,vol,n); appends requests.log (time, URL, status, bytes, weight).
Public REST, no key. >= 0.3 s between requests; pauses when the used weight nears the limit; backs off on
418 / 429 / 503; stops on 403. Spot pairs the API no longer serves (HTTP 400) fall back to data.binance.vision
daily 1m zips (cached under <out-root>/vision/)."""
import csv, io, json, os, sys, time, urllib.request, urllib.error, zipfile

UA = {"User-Agent": "agentfx-research-script/1.0"}
M = 60000
kind, tfile, root = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.join(root, kind), exist_ok=True)
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
last = [0.0]
WMAX = 1800 if kind == "perp" else 4500


def get(url, raw=False):
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.3:
            time.sleep(0.3 - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
                w = r.headers.get("X-MBX-USED-WEIGHT-1M") or r.headers.get("x-mbx-used-weight-1m") or ""
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\t{w}\n")
                if w and int(w) > WMAX:
                    time.sleep(61 - time.gmtime().tm_sec)
                return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\t\n")
            if e.code == 403:
                sys.exit("403: stop")
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After")
                time.sleep(int(ra) if ra and ra.isdigit() else 60 * (attempt + 1)); continue
            if e.code in (400, 404):
                return None
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\t\n")
            time.sleep(5)
    return None


def vision(sym, a, b):
    """Rows from data.binance.vision spot daily 1m zips covering [a, b)."""
    vd = os.path.join(root, "vision"); os.makedirs(vd, exist_ok=True)
    out = []
    d = a // 86400000
    while d * 86400000 < b:
        day = time.strftime('%Y-%m-%d', time.gmtime(d * 86400))
        p = os.path.join(vd, f"{sym}-1m-{day}.zip")
        if not os.path.exists(p):
            body = get(f"https://data.binance.vision/data/spot/daily/klines/{sym}/1m/{sym}-1m-{day}.zip", raw=True)
            if body is None:
                d += 1; continue
            open(p, "wb").write(body)
        with zipfile.ZipFile(p) as z:
            for nm in z.namelist():
                for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                    if not x or not x[0].isdigit():
                        continue
                    t = int(x[0])
                    if t > 10 ** 14:
                        t //= 1000
                    if a <= t < b:
                        out.append((t, x[1], x[2], x[3], x[4], x[5], x[8]))
        d += 1
    return out


rows = list(csv.DictReader(open(tfile)))
lim = 1500 if kind == "perp" else 1000
done = 0
for r in rows:
    sym = r["perp"] if kind == "perp" else r["spot"]
    a, b = int(r["T"]) - 3 * M, int(r["X"]) + 20 * M
    path = os.path.join(root, kind, f"{sym}_{r['T']}.csv")
    if os.path.exists(path):
        continue
    res, t, src = [], a, "api"
    while t < b:
        n = min(lim, (b - t) // M)
        if kind == "perp":
            url = f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={t}&endTime={b - 1}&limit={n}"
        else:
            url = f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1m&startTime={t}&endTime={b - 1}&limit={n}"
        js = get(url)
        if js is None:
            if kind == "spot" and not res:
                res, src = vision(sym, a, b), "vision"
            break
        if not js:
            break
        res += [(int(x[0]), x[1], x[2], x[3], x[4], x[5], x[8]) for x in js]
        t = int(js[-1][0]) + M
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write("t,o,h,l,c,vol,n\n")
        for x in res:
            f.write(",".join(map(str, x)) + "\n")
    os.replace(tmp, path)
    done += 1
    if done % 100 == 0:
        print(time.strftime('%H:%M:%S'), kind, done, sym, len(res), src, flush=True)
print("finished", kind, done, flush=True)
