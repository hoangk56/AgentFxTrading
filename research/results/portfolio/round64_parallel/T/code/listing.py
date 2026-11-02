"""Stream T step 1b: complete the event list from the data.binance.vision bucket listing (perp_1d lacks the pre-relist
history of perps that were delisted and later relisted). Only key names (dates) are read, never file contents.
For each USDT-M perp (no '_'): months with a 1d monthly file up to 2024-12; a delisting = a month m <= 2024-11 with
no file in m + 1 (gap or end); for perps with a 2024-12 monthly file, the 2024-12 daily keys decide a December end.
Usage: python -I listing.py <out-root>   (writes <out-root>/listing_events.csv, appends requests.log)"""
import os, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
root = sys.argv[1]
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
UA = {"User-Agent": "agentfx-research-script/1.0"}
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
last = [0.0]
def get(url):
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.3: time.sleep(0.3 - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                b = r.read()
            LOG.write(f"{ts}\t{url}\t200\t{len(b)}\n"); return b
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403: sys.exit("403: stop")
            if e.code in (418, 429, 503): time.sleep(60 * (attempt + 1)); continue
            return None
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n"); time.sleep(5)
    return None
def s3_list(prefix):
    keys, marker = [], ""
    while True:
        b = get(f"{S3}?delimiter=/&prefix={prefix}" + (f"&marker={marker}" if marker else ""))
        if b is None: return keys
        x = ET.fromstring(b)
        page = [e.find(NS + "Prefix").text for e in x.findall(NS + "CommonPrefixes")]
        page += [e.find(NS + "Key").text for e in x.findall(NS + "Contents")]
        keys += page
        if x.find(NS + "IsTruncated").text != "true" or not page: return keys
        nm = x.find(NS + "NextMarker")
        marker = nm.text if nm is not None else page[-1]
def nxt(m):
    y, mo = int(m[:4]), int(m[5:7]); mo += 1
    if mo == 13: y, mo = y + 1, 1
    return f"{y:04d}-{mo:02d}"
syms = [k.rstrip("/").split("/")[-1] for k in s3_list("data/futures/um/monthly/klines/")]
syms = [s for s in syms if s.endswith("USDT") and "_" not in s]
print(len(syms), "symbols", flush=True)
out = open(os.path.join(root, "listing_events.csv"), "w")
out.write("perp,first_month,end_month,end_day,kind\n")
for i, s in enumerate(syms):
    ks = s3_list(f"data/futures/um/monthly/klines/{s}/1d/")
    ms = sorted({k.split("-1d-")[1][:7] for k in ks if k.endswith(".zip") and "-1d-" in k})
    ms = [m for m in ms if m <= "2024-12"]
    if not ms: continue
    S = set(ms)
    for m in ms:
        if m <= "2024-11" and nxt(m) not in S and m >= "2020-01":
            dk = s3_list(f"data/futures/um/daily/klines/{s}/1d/{s}-1d-{m}-")
            days = sorted(k.split("-1d-")[1][:10] for k in dk if k.endswith(".zip"))
            out.write(f"{s},{ms[0]},{m},{days[-1] if days else ''},{'gap' if m != ms[-1] else 'end'}\n"); out.flush()
    if ms[-1] == "2024-12":
        dk = s3_list(f"data/futures/um/daily/klines/{s}/1d/{s}-1d-2024-12-")
        days = sorted(k.split("-1d-")[1][:10] for k in dk if k.endswith(".zip"))
        if days and days[-1] < "2024-12-30":
            out.write(f"{s},{ms[0]},2024-12,{days[-1]},dec\n"); out.flush()
    if i % 50 == 0: print(time.strftime('%H:%M:%S'), i, s, flush=True)
print("finished", flush=True)
