"""Pull DefiLlama per-protocol emissions (documentedData) for protocols mapped to a Binance perp listed before 2025.
Keyless public dataset host; 0.6 s between requests; log to requests.log. Only reads perp first-kline dates."""
import json, os, sys, time, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
TU = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "token_unlocks")
PERP = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "binance", "perp_1d")
idx = {(x.get("protocolSlug") or x.get("name")): x for x in json.load(open(os.path.join(TU, "raw", "emissionsIndex_ds.json")))["data"]}
rows = json.load(open(os.path.join(TU, "protocol_map.json")))
os.makedirs(os.path.join(TU, "emissions"), exist_ok=True)
HOLD = 1735689600
todo = []
for slug, sym, gid, perps in rows:
    if not perps:
        continue
    first = []
    for p in perps.split("|"):
        with open(os.path.join(PERP, p + ".csv")) as f:
            next(f); line = f.readline()
        if line:
            first.append(int(float(line.split(",")[0])) // 1000)
    if not first or min(first) >= HOLD:
        continue
    ev = [e["timestamp"] for e in idx[slug]["unlockEvents"] if e["timestamp"] < HOLD]
    if not ev:
        continue
    todo.append(slug)
print(len(todo), "protocols to pull")
log = open(os.path.join(TU, "requests.log"), "a")
for slug in todo:
    out = os.path.join(TU, "emissions", slug + ".json")
    if os.path.exists(out):
        continue
    url = "https://defillama-datasets.llama.fi/emissions/" + slug
    req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            b = r.read(); st = r.status
    except urllib.error.HTTPError as e:
        b = b""; st = e.code
    log.write("%s %s %s %d\n" % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), url, st, len(b))); log.flush()
    if st == 200:
        open(out, "wb").write(b)
    elif st in (403, 402):
        print("stop", st, slug); break
    elif st in (418, 429, 503):
        time.sleep(30)
    time.sleep(0.6)
print("done")
