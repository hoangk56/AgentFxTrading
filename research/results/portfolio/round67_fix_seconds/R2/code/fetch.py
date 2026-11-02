"""Stream R2: polite fapi 1m kline pull for (symbol, window) pairs not covered by binance_1m_wicks/npz.
3 threads, >= 0.3 s between request starts (shared lock), back off on 418 / 429 / 503, stop on 403. Every request is logged
(UTC time, URL, status, bytes) in research/data/upbit_rotation/requests.log. endTime < 2025-01-01 asserted.
Raw responses are saved under research/data/upbit_rotation/raw/ (untrusted data; parsed later with python -I)."""
import json, os, sys, time, urllib.request, urllib.error, datetime, threading
from concurrent.futures import ThreadPoolExecutor

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_rotation"
NPZ = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_1m_wicks/npz"
CUT = 1735689600000
LOG = os.path.join(OUT, "requests.log")
RAW = os.path.join(OUT, "raw")
UA = {"User-Agent": "research-script"}
MIN = 60000
PAUSE = [0.0]  # all threads wait until this time after a 418 / 429 / 503


def log(url, status, nbytes):
    with open(LOG, "a") as f:
        f.write("%s\t%s\t%s\t%d\n" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                       url, status, nbytes))


def get(url):
    back = 30
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                b = r.read()
                log(url, r.status, len(b))
                return 200, b
        except urllib.error.HTTPError as e:
            b = e.read() if hasattr(e, "read") else b""
            log(url, e.code, len(b))
            if e.code == 403:
                print("403 -> stop", url, flush=True); os._exit(3)
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After") if e.headers else None
                w = max(back, int(ra) if ra and ra.isdigit() else 0)
                print("backoff", e.code, w, flush=True); PAUSE[0] = time.time() + w; time.sleep(w); back *= 2
                continue
            return e.code, b
        except Exception as ex:  # timeouts, resets
            log(url, "ERR:" + type(ex).__name__, 0)
            time.sleep(5)
    return -1, b""


def mon(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).strftime("%Y-%m")


def main():
    os.makedirs(RAW, exist_ok=True)
    have = set(os.listdir(NPZ))
    if not os.path.exists(os.path.join(OUT, "robots_fapi.txt")):
        st, b = get("https://fapi.binance.com/robots.txt")
        open(os.path.join(OUT, "robots_fapi.txt"), "wb").write(b)
        print("robots", st, b[:300], flush=True)
    todo = []
    for line in open(os.path.join(OUT, "windows.csv")).readlines()[1:]:
        s, a, b = line.strip().split(","); a = int(a); b = int(b)
        if all((s + "_" + m + ".npz") in have for m in {mon(a), mon(b)}):
            continue
        todo.append((s, a, b))
    bad = set()
    print("todo", len(todo), flush=True)
    lock = threading.Lock(); last = [0.0]; cnt = [0]

    def one(item):
        s, a, b = item
        fn = os.path.join(RAW, "%s_%d.json" % (s, a))
        if os.path.exists(fn) or s in bad:
            return
        assert b < CUT
        lim = min(1500, (b - a) // MIN + 1)
        url = ("https://fapi.binance.com/fapi/v1/klines?symbol=%s&interval=1m&startTime=%d&endTime=%d&limit=%d"
               % (s, a, b, lim))
        with lock:  # >= 0.3 s between request starts, shared by all threads
            w = max(last[0] + 0.3, PAUSE[0]) - time.time()
            if w > 0:
                time.sleep(w)
            last[0] = time.time()
        st, body = get(url)
        if st == 200:
            open(fn, "wb").write(body)
        else:
            print("status", st, s, body[:200], flush=True)
            if b"-1121" in body:
                bad.add(s)
        with lock:
            cnt[0] += 1
            if cnt[0] % 200 == 0:
                print(cnt[0], s, st, flush=True)

    with ThreadPoolExecutor(3) as ex:
        list(ex.map(one, todo))
    json.dump(sorted(bad), open(os.path.join(OUT, "invalid_syms.json"), "w"))
    print("done; invalid", sorted(bad), flush=True)


if __name__ == "__main__":
    main()
