"""Stream T step 1b (replaces listing.py, which was stopped: data.binance.vision keeps flat zero-trade monthly files
after a delisting, so month gaps do not mark delistings). Find perps in the bucket whose local perp_1d has no row
before 2025 (fapi drops the pre-relist history of relisted symbols), list their 1d monthly keys up to 2024-12 and
download those monthly 1d files (small) to find the last day with trades before a run of zero-trade days.
Usage: python -I listing2.py <out-root>; writes <out-root>/relisted_candidates.csv. Only keys / files <= 2024-12."""
import csv, io, os, sys, time, zipfile, urllib.request, urllib.error, xml.etree.ElementTree as ET
root = sys.argv[1]
P1D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance/perp_1d"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
UA = {"User-Agent": "agentfx-research-script/1.0"}
CUT = 1735689600000
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
        nm = x.find(NS + "NextMarker"); marker = nm.text if nm is not None else page[-1]
def has_pre2025(sym):
    p = os.path.join(P1D, sym + ".csv")
    if not os.path.exists(p): return False
    with open(p) as f:
        next(f); l = f.readline()
    return bool(l.strip()) and int(float(l.split(",")[0])) < CUT
syms = [k.rstrip("/").split("/")[-1] for k in s3_list("data/futures/um/monthly/klines/")]
syms = [s for s in syms if s.endswith("USDT") and "_" not in s and not has_pre2025(s)]
print(len(syms), "symbols without pre-2025 local history", flush=True)
out = open(os.path.join(root, "relisted_candidates.csv"), "w"); out.write("perp,first_day,last_trade_day,zero_days_after\n")
dd = os.path.join(root, "perp1d_monthly"); os.makedirs(dd, exist_ok=True)
for s in syms:
    ks = s3_list(f"data/futures/um/monthly/klines/{s}/1d/")
    ms = sorted(k for k in ks if k.endswith(".zip") and k.split("-1d-")[1][:7] <= "2024-12")
    if not ms: continue
    rows = []
    for k in ms:
        p = os.path.join(dd, k.split("/")[-1])
        if not os.path.exists(p):
            b = get(f"https://data.binance.vision/{k}")
            if b is None: continue
            open(p, "wb").write(b)
        with zipfile.ZipFile(p) as z:
            for nm in z.namelist():
                for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                    if x and x[0].isdigit() and int(x[0]) < CUT:
                        rows.append((int(x[0]), int(float(x[8]))))
    rows.sort()
    act = [t for t, n in rows if n > 0]
    if not act: continue
    d = lambda t: time.strftime('%Y-%m-%d', time.gmtime(t / 1000))
    # last trade day followed by >= 3 zero-trade days or by the end of the <= 2024 data
    for i, (t, n) in enumerate(rows):
        if n > 0 and (i + 1 == len(rows) or rows[i + 1][1] == 0):
            z = 0
            while i + 1 + z < len(rows) and rows[i + 1 + z][1] == 0: z += 1
            if (i + 1 + z == len(rows) and t < CUT - 3 * 86400000) or z >= 3:
                out.write(f"{s},{d(rows[0][0])},{d(t)},{z}\n"); out.flush()
    print(time.strftime('%H:%M:%S'), s, len(rows), flush=True)
print("finished", flush=True)
