"""Stream BX pull: Bybit linear 1h klines (and funding for symbols missing in research/data/bybit/funding) over merged
windows [entry - 48 h, exit + 48 h] of B's IS / VAL trades (../out/events.csv). Public REST, no key, >= 0.3 s between
requests, backs off on 429 / 503, stops on 403. End capped at 2024-12-31 23:59:59.999 UTC (HOLD never requested).
Usage: python -I pull.py <events.csv> <out-root>
Writes <out-root>/kline/<BINANCE_PERP>.csv (t,o,h,l,c,vol,turnover,bybit_symbol) and funding/<BINANCE_PERP>.csv (t,rate)."""
import csv, json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "agentfx-research-script/1.0"}
CAP = 1735689599999
H = 3600000
ev, root = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(root, "kline"), exist_ok=True)
os.makedirs(os.path.join(root, "funding"), exist_ok=True)
LOG = open(os.path.join(root, "requests.log"), "a", buffering=1)
HAVE_F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "data", "bybit", "funding")
last = [0.0]


def get(url):
    for attempt in range(6):
        dt = time.time() - last[0]
        if dt < 0.3:
            time.sleep(0.3 - dt)
        last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
                j = json.loads(body)
                rc = j.get("retCode")
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\tretCode={rc}\n")
                if rc != 0:
                    LOG.write(f"{ts}\tretMsg={str(j.get('retMsg'))[:80]}\n")
                    if rc == 10001 or attempt >= 2:
                        return j
                    time.sleep(10 * (attempt + 1)); continue
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


def windows():
    W = {}
    for r in csv.DictReader(open(ev)):
        a, b = int(r["e_ms"]) - 48 * H, min(int(r["x_ms"]) + 48 * H, CAP + 1)
        W.setdefault(r["perp"], []).append((a, b))
    out = {}
    for s, L in W.items():
        L.sort(); m = [list(L[0])]
        for a, b in L[1:]:
            if a <= m[-1][1]:
                m[-1][1] = max(m[-1][1], b)
            else:
                m.append([a, b])
        out[s] = m
    return out


def cands(p):
    base = p[:-4]
    c = [p]
    if base.startswith("1000"):
        c += [base[4:] + "1000USDT", base[4:] + "USDT"]
    return c


def klines(sym, a, b):
    rows, end = {}, b - 1
    while end >= a:
        start = max(a, end - 999 * H)
        j = get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=60&start={start}&end={end}&limit=1000")
        if j is None or j.get("retCode") != 0:
            return None if not rows else rows
        L = j["result"]["list"]
        for x in L:
            t = int(x[0])
            if a <= t <= CAP:
                rows[t] = x[1:7]
        end = start - 1
    return rows


def funding(sym, a, b):
    rows, end = {}, b - 1
    while end >= a:
        j = get(f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={sym}&startTime={a}&endTime={end}&limit=200")
        if j is None or j.get("retCode") != 0:
            break
        L = j["result"]["list"]
        if not L:
            break
        ts = [int(x["fundingRateTimestamp"]) for x in L]
        for x, t in zip(L, ts):
            if t <= CAP:
                rows[t] = x["fundingRate"]
        if min(ts) <= a or len(L) < 200:
            break
        end = min(ts) - 1
    return rows


for perp, W in sorted(windows().items()):
    kp = os.path.join(root, "kline", perp + ".csv")
    if os.path.exists(kp) or os.path.exists(kp + ".missing"):
        continue
    used, allrows = None, {}
    for sym in cands(perp):
        got = {}
        for a, b in W:
            r = klines(sym, a, b)
            if r is None:
                got = None; break
            got.update(r)
        if got:
            used, allrows = sym, got
            break
    if not used:
        open(kp + ".missing", "w").close()
        print(perp, "missing", flush=True)
        continue
    with open(kp, "w") as f:
        f.write("t,o,h,l,c,vol,turnover,sym\n")
        for t in sorted(allrows):
            f.write(",".join([str(t)] + list(allrows[t]) + [used]) + "\n")
    # funding only if not in the full-history folder (under the Binance name or the Bybit name)
    if not any(os.path.exists(os.path.join(HAVE_F, n + ".csv")) for n in (perp, used)):
        fr = {}
        for a, b in W:
            fr.update(funding(used, a - 8 * H, b))
        with open(os.path.join(root, "funding", perp + ".csv"), "w") as f:
            f.write("t,rate\n")
            for t in sorted(fr):
                f.write(f"{t},{fr[t]}\n")
    print(perp, used, len(allrows), flush=True)
print("done", flush=True)
