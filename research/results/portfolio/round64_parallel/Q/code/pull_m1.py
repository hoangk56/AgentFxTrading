"""Stream Q: daily 1m klines from data.binance.vision for the (market, symbol, day) list of the trades (days <= 2024-12-31).
Usage: python -I pull_m1.py <need.txt> <out-root>    need.txt lines: market symbol YYYY-MM-DD
Writes <out-root>/m1/<market>/<SYM>/<day>.csv (t,o,c,n); a day that is not in the bucket gets an empty marker file.
Appends <out-root>/requests.log. >= 0.3 s between requests; back off on 418 / 429 / 503; stop on 403."""
import csv, io, os, sys, time, urllib.request, urllib.error, zipfile

UA = {"User-Agent": "agentfx-research-script/1.0"}
CUT = 1735689600000
need, root = sys.argv[1], sys.argv[2]
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
last = [0.0]


def get(url):
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.3:
            time.sleep(0.3 - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                body = r.read()
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\n")
                return body
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                sys.exit("403: stop")
            if e.code in (418, 429, 503):
                time.sleep(30 * (attempt + 1)); continue
            if e.code == 404:
                return None
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n")
            time.sleep(5)
    return None


done = 0
for line in open(need):
    p = line.split()
    if len(p) != 3:
        continue
    market, sym, day = p
    if day > "2024-12-31":
        continue
    od = os.path.join(root, "m1", market, sym)
    os.makedirs(od, exist_ok=True)
    path = os.path.join(od, day + ".csv")
    if os.path.exists(path):
        continue
    body = get(f"https://data.binance.vision/data/futures/{market}/daily/klines/{sym}/1m/{sym}-1m-{day}.zip")
    rows = []
    if body:
        try:
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                for nm in z.namelist():
                    for x in csv.reader(io.TextIOWrapper(z.open(nm), encoding="utf-8", errors="replace")):
                        if not x or not x[0].strip().isdigit():
                            continue
                        t = int(x[0])
                        if t > 10 ** 14:
                            t //= 1000
                        if t < CUT:
                            rows.append((t, x[1], x[4], x[8]))
        except zipfile.BadZipFile:
            LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{sym} {day}\tBADZIP\t0\n")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write("t,o,c,n\n")
        for r in sorted(rows):
            f.write(",".join(map(str, r)) + "\n")
    os.replace(tmp, path)
    done += 1
    if done % 200 == 0:
        print(time.strftime('%H:%M:%S'), done, market, sym, day, len(rows), flush=True)
print("finished", done, flush=True)
