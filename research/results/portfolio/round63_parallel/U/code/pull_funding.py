"""Pull Binance USDT-M funding history (keyless fapi/v1/fundingRate) for event coins lacking a full funding file.
End time 2024-12-31 23:59:59.999 UTC. Output: research/data/token_unlocks/funding/<SYM>.csv (t,rate)."""
import json, os, sys, time, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
TU = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "token_unlocks")
END = 1735689599999
syms = sys.argv[1:]
os.makedirs(os.path.join(TU, "funding"), exist_ok=True)
log = open(os.path.join(TU, "requests.log"), "a")
for s in syms:
    rows, start = [], 1567296000000
    while True:
        url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=%s&startTime=%d&endTime=%d&limit=1000" % (s, start, END)
        req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                b = r.read(); st = r.status
        except urllib.error.HTTPError as e:
            b = b""; st = e.code
        log.write("%s %s %s %d\n" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), url, st, len(b)))
        log.flush()
        if st in (418, 429):
            time.sleep(60); continue
        if st != 200:
            print("fail", s, st); break
        a = json.loads(b)
        a = [x for x in a if int(x["fundingTime"]) <= END]
        rows += [(int(x["fundingTime"]), float(x["fundingRate"])) for x in a]
        if len(a) < 1000:
            break
        start = rows[-1][0] + 1
        time.sleep(0.5)
    with open(os.path.join(TU, "funding", s + ".csv"), "w") as f:
        f.write("t,rate\n")
        for t, r in rows:
            f.write("%d,%.8f\n" % (t, r))
    print(s, len(rows))
    time.sleep(0.5)
