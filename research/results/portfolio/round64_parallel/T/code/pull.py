"""Stream T step 2: data.binance.vision daily 1m klines (perp, spot, BTCUSDT perp) for [last_active - 8 d, last_active
+ 1 d] of each event, plus monthly fundingRate files. Only dates <= 2024-12-31. Usage: python -I pull.py <events.csv>
<out-root>. >= 0.3 s between requests, back off on 418 / 429 / 503, stop on 403. 404 = file not there (logged)."""
import csv, os, sys, time, urllib.request, urllib.error
UA = {"User-Agent": "agentfx-research-script/1.0"}
ev, root = sys.argv[1], sys.argv[2]
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
last = [0.0]
B = "https://data.binance.vision/data"
def get(url, path):
    if os.path.exists(path) or os.path.exists(path + ".404"):
        return
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.3: time.sleep(0.3 - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                body = r.read()
            LOG.write(f"{ts}\t{url}\t200\t{len(body)}\n")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path + ".tmp", "wb").write(body); os.replace(path + ".tmp", path)
            return
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403: sys.exit("403: stop")
            if e.code == 404:
                os.makedirs(os.path.dirname(path), exist_ok=True); open(path + ".404", "w").close(); return
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After")
                time.sleep(int(ra) if ra and ra.isdigit() else 60 * (attempt + 1)); continue
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n"); time.sleep(5)
CUTDAY = "2024-12-31"
for r in csv.DictReader(open(ev)):
    t0 = int(time.mktime(time.strptime(r["perp_last_active"], "%Y-%m-%d"))) - time.timezone
    days = [time.strftime('%Y-%m-%d', time.gmtime(t0 + k * 86400)) for k in range(-8, 2)]
    days = [d for d in days if d <= CUTDAY]
    months = sorted({d[:7] for d in days})
    p, s = r["perp"], r["spot"] + "USDT" if not r["spot"].endswith("USDT") else r["spot"]
    s = r["spot"]
    for d in days:
        get(f"{B}/futures/um/daily/klines/{p}/1m/{p}-1m-{d}.zip", os.path.join(root, "perp", p, f"{p}-1m-{d}.zip"))
        get(f"{B}/spot/daily/klines/{s}/1m/{s}-1m-{d}.zip", os.path.join(root, "spot", s, f"{s}-1m-{d}.zip"))
        get(f"{B}/futures/um/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{d}.zip", os.path.join(root, "perp", "BTCUSDT", f"BTCUSDT-1m-{d}.zip"))
    for m in months:
        for q in (p, "BTCUSDT"):
            get(f"{B}/futures/um/monthly/fundingRate/{q}/{q}-fundingRate-{m}.zip", os.path.join(root, "funding", q, f"{q}-fundingRate-{m}.zip"))
    print(time.strftime('%H:%M:%S'), p, "done", flush=True)
print("finished", flush=True)
