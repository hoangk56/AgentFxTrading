"""Stream BY pull (Bybit public v5, no key). End of every price / funding request capped at 2024-12-31 23:59:59.999 UTC.
Usage (python -I):
  pull.py instruments <root>            -> instruments_linear.json, instruments_linear_closed.json, instruments_spot.json
  pull.py daily <root> <cands.csv>      -> linear_1d/<SYM>.csv, spot_1d/<SPOT>.csv  (cands: perp,spot)
  pull.py hourly <root> <windows.csv>   -> linear_1h/<SYM>.csv, spot_1h/<SPOT>.csv  (windows: perp,spot,a_ms,b_ms)
  pull.py funding <root> <syms.txt>     -> funding/<SYM>.csv
Kline CSV: t,o,h,l,c,vol,turnover. Logs every request to <root>/requests.log (time, url, status, bytes, retCode)."""
import csv, json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "agentfx-research-script/1.0"}
BASE = "https://api.bybit.com"
CAP = 1735689599999
H = 3600000
DAY = 86400000
SPACING = 0.15
last = [0.0]
LOG = None


def get(path):
    url = BASE + path
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < SPACING:
            time.sleep(SPACING - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
                j = json.loads(body)
                rc = j.get("retCode")
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\tretCode={rc}\n")
                if rc in (10006, 10016):
                    time.sleep(30 * (attempt + 1)); continue
                if rc != 0:
                    LOG.write(f"{ts}\tretMsg={str(j.get('retMsg'))[:80]}\n")
                return j
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                sys.exit("403: stop")
            if e.code in (418, 429, 503):
                time.sleep(60 * (attempt + 1)); continue
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n")
            time.sleep(5)
    return None


def instruments(root):
    for cat, extra, name in (("linear", "", "linear"), ("linear", "&status=Closed", "linear_closed"),
                             ("spot", "", "spot")):
        rows, cursor = [], ""
        for _ in range(20):
            j = get(f"/v5/market/instruments-info?category={cat}&limit=1000{extra}" + (f"&cursor={cursor}" if cursor else ""))
            if not j or j.get("retCode") != 0:
                break
            rows += j["result"]["list"]
            cursor = j["result"].get("nextPageCursor") or ""
            if not cursor:
                break
        json.dump(rows, open(os.path.join(root, f"instruments_{name}.json"), "w"))
        print(name, len(rows), flush=True)


def kline(cat, sym, interval, a, b, step):
    """All klines with start in [a, b] (b capped), newest-first pages of 1000."""
    b = min(b, CAP)
    out = {}
    end = b
    while end >= a:
        start = max(a, end - 999 * step)
        j = get(f"/v5/market/kline?category={cat}&symbol={sym}&interval={interval}&start={start}&end={end}&limit=1000")
        if not j or j.get("retCode") != 0:
            return None if not out else out
        L = j["result"]["list"]
        for r in L:
            t = int(r[0])
            if a <= t <= b:
                out[t] = r[1:7]
        end = start - 1
        if not L and interval == "D":
            # nothing earlier for a daily series: stop at the first empty page
            break
    return out


def write_k(path, d):
    with open(path, "w") as f:
        f.write("t,o,h,l,c,vol,turnover\n")
        for t in sorted(d):
            f.write(str(t) + "," + ",".join(d[t]) + "\n")


def daily(root, cands):
    os.makedirs(os.path.join(root, "linear_1d"), exist_ok=True)
    os.makedirs(os.path.join(root, "spot_1d"), exist_ok=True)
    a = 1577836800000 - 120 * DAY   # 2019-09-03
    done_s = set()
    for r in csv.DictReader(open(cands)):
        for cat, sym, sub in (("linear", r["perp"], "linear_1d"), ("spot", r["spot"], "spot_1d")):
            if not sym or (cat == "spot" and sym in done_s):
                continue
            p = os.path.join(root, sub, sym + ".csv")
            if os.path.exists(p) or os.path.exists(p + ".missing"):
                continue
            d = kline(cat, sym, "D", a, CAP, DAY)
            if d:
                write_k(p, d)
            else:
                open(p + ".missing", "w").close()
            if cat == "spot":
                done_s.add(sym)
        print("daily", r["perp"], flush=True)


def hourly(root, windows):
    os.makedirs(os.path.join(root, "linear_1h"), exist_ok=True)
    os.makedirs(os.path.join(root, "spot_1h"), exist_ok=True)
    for r in csv.DictReader(open(windows)):
        a, b = int(r["a_ms"]), min(int(r["b_ms"]), CAP)
        for cat, sym, sub in (("linear", r["perp"], "linear_1h"), ("spot", r["spot"], "spot_1h")):
            p = os.path.join(root, sub, sym + ".csv")
            if os.path.exists(p) or os.path.exists(p + ".missing"):
                continue
            d = kline(cat, sym, "60", a, b, H)
            if d:
                write_k(p, d)
            else:
                open(p + ".missing", "w").close()
        print("hourly", r["perp"], time.strftime('%H:%M:%S', time.gmtime()), flush=True)


def funding(root, syms):
    os.makedirs(os.path.join(root, "funding"), exist_ok=True)
    for s in open(syms).read().split():
        p = os.path.join(root, "funding", s + ".csv")
        if os.path.exists(p):
            continue
        out, end = {}, CAP
        for _ in range(60):
            j = get(f"/v5/market/funding/history?category=linear&symbol={s}&limit=200&endTime={end}")
            if not j or j.get("retCode") != 0:
                break
            L = j["result"]["list"]
            if not L:
                break
            for x in L:
                t = int(x["fundingRateTimestamp"])
                if t <= CAP:
                    out[t] = x["fundingRate"]
            mn = min(int(x["fundingRateTimestamp"]) for x in L)
            if mn >= end:
                break
            end = mn - 1
            if len(L) < 200:
                break
        with open(p, "w") as f:
            f.write("t,rate\n")
            for t in sorted(out):
                f.write(f"{t},{out[t]}\n")
        print("funding", s, len(out), flush=True)


if __name__ == "__main__":
    mode, root = sys.argv[1], sys.argv[2]
    os.makedirs(root, exist_ok=True)
    LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
    if mode == "instruments":
        instruments(root)
    elif mode == "daily":
        daily(root, sys.argv[3])
    elif mode == "hourly":
        hourly(root, sys.argv[3])
    elif mode == "funding":
        funding(root, sys.argv[3])
