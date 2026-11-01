"""Pull archived Kalshi daily-high events (markets + hourly candles), dates < 2025-01-01 only.
Usage: python -I kalshi_pull.py SERIES START(YYYY-MM-DD) END(YYYY-MM-DD) [STEP_DAYS] [OFFSET]
Saves research/data/kalshi_weather/events/<SERIES>/<EVENT>.json; resumable; logs every request."""
import sys, json, time, threading, urllib.request, urllib.error, datetime as dt, os, urllib.parse
BASE = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/kalshi_weather"
LOG = ROOT + "/requests.log"
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
KEEP = ["ticker", "event_ticker", "open_time", "close_time", "status", "result", "expiration_value",
        "strike_type", "floor_strike", "cap_strike", "yes_sub_title", "volume_fp", "settlement_ts", "rules_primary"]
_lock = threading.Lock(); _last = [0.0]
def _throttle(gap=0.25):
    with _lock:
        now = time.time(); wait = _last[0] + gap - now
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
_loglock = threading.Lock()
def get_json(url):
    for attempt in range(8):
        _throttle()
        req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
        status, data = None, b""
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                status, data = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, data = e.code, e.read()
        except Exception as e:
            status = "ERR:" + type(e).__name__
        ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with _loglock, open(LOG, "a") as f:
            f.write(f"{ts}\t{url}\t{status}\t{len(data)}\n")
        if status == 200:
            return json.loads(data)
        if status in (401, 403):
            raise SystemExit(f"stop: {status} {url}")
        if status == 404:
            return None
        time.sleep(5 * (attempt + 1))
    raise SystemExit("too many failures")
def iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
def event_ticker(series, d):
    return f"{series}-{d:%y}{MON[d.month-1]}{d:%d}"
def pull_event(series, d):
    ev = event_ticker(series, d)
    outdir = f"{ROOT}/events/{series}"; os.makedirs(outdir, exist_ok=True)
    path = f"{outdir}/{ev}.json"
    if os.path.exists(path) or os.path.exists(path + ".none"):
        return "cached"
    r = get_json(BASE + "/historical/markets?" + urllib.parse.urlencode({"event_ticker": ev, "limit": 100}))
    mk = [m for m in (r or {}).get("markets", []) if iso(m["close_time"]) < CUT]
    if not mk:
        open(path + ".none", "w").close(); return "none"
    out = {"event_ticker": ev, "date": d.isoformat(), "markets": []}
    for m in mk:
        rec = {k: m.get(k) for k in KEEP}
        st = int(iso(m["open_time"]).timestamp()); en = int(iso(m["close_time"]).timestamp()) + 3600
        c = get_json(BASE + f"/historical/markets/{m['ticker']}/candlesticks?" +
                     urllib.parse.urlencode({"start_ts": st, "end_ts": en, "period_interval": 60}))
        rows = []
        for x in (c or {}).get("candlesticks", []):
            if x["end_period_ts"] >= CUT.timestamp(): continue
            rows.append([x["end_period_ts"], x["yes_bid"].get("close"), x["yes_ask"].get("close"),
                         x["price"].get("close"), x["volume"], x["yes_bid"].get("low"), x["yes_ask"].get("high")])
        rec["candles"] = rows
        out["markets"].append(rec)
    with open(path, "w") as f: json.dump(out, f)
    return f"ok {len(mk)}"
if __name__ == "__main__":
    # Usage: python -I kalshi_pull.py JOBFILE NTHREADS ; jobfile lines: SERIES START END
    import queue
    jobs = queue.Queue()
    for line in open(sys.argv[1]):
        if not line.strip(): continue
        s, a, b = line.split()
        d = dt.date.fromisoformat(a); b = min(dt.date.fromisoformat(b), dt.date(2024, 12, 30))
        while d <= b:
            if d.toordinal() % 2 == 1: jobs.put((s, d))   # declared subsample: odd ordinal days only
            d += dt.timedelta(days=1)
    total = jobs.qsize(); done = [0]
    def worker():
        while True:
            try: s, d = jobs.get_nowait()
            except queue.Empty: return
            try: pull_event(s, d)
            except SystemExit as e: print("STOP", e, flush=True); os._exit(1)
            except Exception as e: print("ERR", s, d, e, flush=True)
            done[0] += 1
            if done[0] % 100 == 0: print(dt.datetime.utcnow().isoformat(), done[0], "/", total, flush=True)
    th = [threading.Thread(target=worker) for _ in range(int(sys.argv[2]))]
    [t.start() for t in th]; [t.join() for t in th]
    print("done", total, flush=True)
