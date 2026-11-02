"""Stream Q: COIN-M funding before 2022-07 (data.binance.vision cm fundingRate starts 2022-07) from the public dapi
endpoint /dapi/v1/fundingRate (no key). End time fixed at 2022-07-01 00:00 UTC, far before HOLD.
Usage: python -I pull_dapi_funding.py <jobs_a.txt> <out-root>  -> <out-root>/cm_funding_dapi/<SYM>.csv (t,rate)"""
import json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "agentfx-research-script/1.0"}
START, END = 1593561600000, 1656633599999          # 2020-07-01 .. 2022-06-30 23:59:59.999 UTC
jobs, root = sys.argv[1], sys.argv[2]
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
od = os.path.join(root, "cm_funding_dapi"); os.makedirs(od, exist_ok=True)
last = [0.0]


def get(url):
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.6:
            time.sleep(0.6 - dt)
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


syms = sorted({l.split()[2] for l in open(jobs) if l.split()[1] == "klines"})
for sym in syms:
    path = os.path.join(od, sym + ".csv")
    if os.path.exists(path):
        continue
    res, t = [], START
    while t < END:
        js = get(f"https://dapi.binance.com/dapi/v1/fundingRate?symbol={sym}&startTime={t}&endTime={END}&limit=1000")
        if not js:
            break
        res += [(int(x["fundingTime"]), x["fundingRate"]) for x in js if int(x["fundingTime"]) <= END]
        t = int(js[-1]["fundingTime"]) + 1
        if len(js) < 1000:
            break
    with open(path + ".tmp", "w") as f:
        f.write("t,rate\n")
        for r in res:
            f.write(f"{r[0]},{r[1]}\n")
    os.replace(path + ".tmp", path)
    print(sym, len(res), flush=True)
print("finished", flush=True)
