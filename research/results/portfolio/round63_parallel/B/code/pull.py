"""Stream B pull: 1h klines (perp | spot) or funding for the universe60.csv windows. Public REST, no key.
Usage: python -I pull.py perp|spot|funding <universe.csv> <out-root>
Writes <out-root>/<kind>_1h/<SYM>.csv (t,o,h,l,c,vol,qvol,n) or funding/<SYM>.csv (t,rate); requests.log in out-root.
End capped at 2024-12-31 23:59:59.999 UTC (HOLD never requested). >= 0.3 s between requests; backs off on 418/429/503;
stops on 403."""
import csv, json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "agentfx-research-script/1.0"}
CAP = 1735689599999
H = 3600000
kind, ufile, root = sys.argv[1], sys.argv[2], sys.argv[3]
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
last = [0.0]


def get(url):
    for attempt in range(6):
        dt = time.time() - last[0]
        gap = 0.7 if kind == "funding" else 0.3
        if dt < gap:
            time.sleep(gap - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\n")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                sys.exit("403: stop")
            if e.code in (418, 429, 503):
                time.sleep(60 * (attempt + 1)); continue
            if e.code == 400:
                return None
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n")
            time.sleep(5)
    return None


rows = [r for r in csv.reader(open(ufile))]
out = os.path.join(root, {"perp": "perp_1h", "spot": "spot_1h", "funding": "funding"}[kind])
os.makedirs(out, exist_ok=True)
fund_have = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "data", "binance", "funding")
for perp, spot, fac, a, b in rows:
    a, b = int(a) - 8 * 24 * H, min(int(b) + 2 * 24 * H, CAP + 1)
    sym = spot if kind == "spot" else perp
    path = os.path.join(out, sym + ".csv")
    if os.path.exists(path):
        continue
    if kind == "funding" and os.path.exists(os.path.join(fund_have, perp + ".csv")):
        continue
    res = []
    t = a
    while t < b:
        if kind == "funding":
            url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={t}&endTime={min(b, CAP)}&limit=1000"
        elif kind == "perp":
            url = f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1h&startTime={t}&endTime={min(b - 1, CAP)}&limit=1500"
        else:
            url = f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1h&startTime={t}&endTime={min(b - 1, CAP)}&limit=1000"
        js = get(url)
        if not js:
            break
        if kind == "funding":
            res += [(int(x["fundingTime"]), x["fundingRate"]) for x in js]
            t = int(js[-1]["fundingTime"]) + 1
            if len(js) < 1000:
                break
        else:
            res += [(int(x[0]), x[1], x[2], x[3], x[4], x[5], x[7], x[8]) for x in js]
            t = int(js[-1][0]) + H
            if len(js) < (1500 if kind == "perp" else 1000):
                break
    res = [r for r in res if r[0] <= CAP]
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        w = csv.writer(f)
        w.writerow(["t", "rate"] if kind == "funding" else ["t", "o", "h", "l", "c", "vol", "qvol", "n"])
        w.writerows(res)
    os.replace(tmp, path)
    print(sym, len(res), flush=True)
