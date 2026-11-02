"""1m alt perp closes for every U trade (entry T+1h, T+1h+5m, T+2h; exits +24 h / +72 h), from public fapi 1m klines
(get() copied from K/coord/hold/k2rule.py, logging to research/data/upbit_vol/requests.log). Stream K's alt_1m cache is
read first (read-only). Cache: research/data/upbit_vol/alt_1m/<SYM>.csv (t, c), bars < 2025-01-01 only."""
import csv, json, os, sys, time, threading, urllib.request, urllib.error, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udata import *

D1 = os.path.join(UV, "alt_1m"); os.makedirs(D1, exist_ok=True)
LOG = open(os.path.join(UV, "requests.log"), "a", buffering=1)
LOCK = threading.Lock(); _last = {}


def get(url):
    host = url.split("/")[2]
    for att in range(6):
        with LOCK:
            w = 0.26 - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script", "Accept": "application/json"}), timeout=30) as r:
                body = r.read()
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t200\t{len(body)}\n")
            return json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                os._exit(3)
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1)); continue
            return None
        except Exception as e:
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None


def load(sym):
    out = {}
    for p in (os.path.join(UP, "binance", "alt_1m", sym + ".csv"), os.path.join(D1, sym + ".csv")):
        if os.path.exists(p):
            with open(p) as f:
                for t, c in csv.reader(f):
                    if int(t) < CUT:
                        out[int(t)] = float(c)
    return out


def price_at(cache, t, fallback=4):  # identical to K's fills.price_at / k2rule.px fallback
    for d in range(fallback + 1):
        v = cache.get(t + d * M)
        if v is not None and np.isfinite(v):
            return v
    return np.nan


OFF = (H, H + 5 * M, 2 * H)


def need():
    coins, hb, T = panel()
    nd = {}
    for k in (2, 4, 8):
        for ru in (0, 1):
            for hold in (24, 72):
                for ci, j in events(coins, T, k, ru, hold):
                    s = nd.setdefault(coins[ci]["sym"], set())
                    for off in OFF:
                        s.add(int(T[j] + off)); s.add(int(T[j] + off + hold * H))
    return nd


def fetch_sym(sym, ts, limit=99):
    have = load(sym)
    miss = sorted(t for t in ts if all((t + d * M) not in have for d in range(5)) and t < CUT)
    rows = []; k = 0
    while k < len(miss):
        st = miss[k]
        js = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={st}&limit={limit}")
        got = {int(x[0]): float(x[4]) for x in (js or []) if int(x[0]) < CUT}
        if not got:
            got = {st: float("nan")}
        rows += [(t, c) for t, c in got.items() if t not in have]
        have.update(got)
        end = st + limit * M
        while k < len(miss) and miss[k] < end:
            k += 1
    if rows:
        with open(os.path.join(D1, sym + ".csv"), "a", newline="") as f:
            csv.writer(f).writerows(rows)
    print("1m", sym, len(miss), "missing,", len(rows), "bars added", flush=True)


if __name__ == "__main__":
    nd = need()
    if sys.argv[1:] == ["count"]:
        tot = 0
        for s, ts in nd.items():
            have = load(s)
            miss = sorted(t for t in ts if all((t + d * M) not in have for d in range(5)))
            k = 0; n = 0
            while k < len(miss):
                end = miss[k] + 99 * M; n += 1
                while k < len(miss) and miss[k] < end:
                    k += 1
            tot += n
        print(len(nd), "syms", sum(len(v) for v in nd.values()), "minutes; requests needed", tot)
        sys.exit()
    syms = sorted(nd)
    q = list(syms)
    def worker():
        while True:
            with LOCK:
                if not q:
                    return
                s = q.pop(0)
            fetch_sym(s, nd[s])
    th = [threading.Thread(target=worker) for _ in range(4)]
    [t.start() for t in th]; [t.join() for t in th]
    print("done", flush=True)
