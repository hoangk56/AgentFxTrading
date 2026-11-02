"""Stream Q pull from data.binance.vision (public bucket, no key). Monthly files only, months <= 2024-12 (HOLD never
requested). Usage: python -I pull_vision.py <jobs.txt> <out-root>
jobs.txt lines: market kind symbol interval   (market cm|um, kind klines|fundingRate, interval 1h|1m|-)
Writes <out-root>/<market>_<kind>_<interval>/<SYM>.csv; appends <out-root>/requests.log (time, URL, status, bytes).
>= 0.3 s between requests; back off on 418 / 429 / 503; stop on 403. Zips are parsed in memory as data only."""
import csv, io, os, re, sys, time, urllib.request, urllib.error, zipfile

UA = {"User-Agent": "agentfx-research-script/1.0"}
CUT = 1735689600000
LAST_MONTH = "2024-12"
jobs, root = sys.argv[1], sys.argv[2]
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


def months_listed(market, kind, sym, interval):
    pre = f"data/futures/{market}/monthly/{kind}/{sym}/" + (f"{interval}/" if kind == "klines" else "")
    keys, marker = [], ""
    while True:
        url = f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix={pre}" + (f"&marker={marker}" if marker else "")
        body = get(url)
        if body is None:
            return []
        txt = body.decode("utf-8", "replace")
        ks = re.findall(r"<Key>([^<]+)</Key>", txt)
        keys += ks
        if "<IsTruncated>true</IsTruncated>" in txt and ks:
            marker = ks[-1]
        else:
            break
    out = []
    for k in keys:
        m = re.search(r"-(\d{4}-\d{2})\.zip$", k)
        if m and m.group(1) <= LAST_MONTH:
            out.append((m.group(1), k))
    return sorted(out)


def parse(body, kind):
    rows = []
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        for nm in z.namelist():
            for x in csv.reader(io.TextIOWrapper(z.open(nm), encoding="utf-8", errors="replace")):
                if not x or not x[0].strip().isdigit():
                    continue
                t = int(x[0])
                if t > 10 ** 14:
                    t //= 1000
                if t >= CUT:
                    continue
                if kind == "klines":
                    rows.append((t, x[1], x[2], x[3], x[4], x[5], x[7], x[8]))
                else:
                    rows.append((t, x[-1]))
    return rows


for line in open(jobs):
    p = line.split()
    if len(p) != 4:
        continue
    market, kind, sym, interval = p
    od = os.path.join(root, f"{market}_{kind}_{interval}")
    os.makedirs(od, exist_ok=True)
    path = os.path.join(od, sym + ".csv")
    if os.path.exists(path):
        continue
    res = []
    for mon, key in months_listed(market, kind, sym, interval):
        body = get("https://data.binance.vision/" + key)
        if body:
            try:
                res += parse(body, kind)
            except zipfile.BadZipFile:
                LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{key}\tBADZIP\t0\n")
    res = sorted(set(res))
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        w = csv.writer(f)
        w.writerow(["t", "o", "h", "l", "c", "vol", "bvol", "n"] if kind == "klines" else ["t", "rate"])
        w.writerows(res)
    os.replace(tmp, path)
    print(time.strftime('%H:%M:%S'), market, kind, sym, interval, len(res), flush=True)
print("finished", flush=True)
