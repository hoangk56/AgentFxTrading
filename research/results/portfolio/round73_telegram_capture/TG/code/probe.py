"""Live refresh probe of t.me/s/<channel>: one GET every <period> s, at most <n> requests, stop at the first
non-200 / 429. Records per poll: request time, status, bytes, newest post id + its time, cache headers.
Usage: python -I probe.py <channel> <period_s> <n>   Writes research/data/telegram_upbit/probe_<channel>_<utc>.csv"""
import os, sys, time, csv, datetime as dt, http.client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tg, parse

ch, period, n = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
fn = os.path.join(tg.D, f"probe_{ch}_{stamp}.csv")
rd = os.path.join(tg.RAW, "probe_" + ch); os.makedirs(rd, exist_ok=True)
seen = {}
with open(fn, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["i", "t_req_utc", "t_resp_s", "status", "bytes", "top_id", "top_time_utc",
                                   "new_ids", "cache_control", "age", "date_hdr"])
    nxt = time.time(); conn = None
    for i in range(n):
        dl = nxt - time.time()
        if dl > 0:
            time.sleep(dl)
        nxt += period
        t0 = time.time(); url = f"https://t.me/s/{ch}"
        try:
            # one persistent HTTPS connection (keep-alive), as a real poller would use; default Python UA
            if conn is None:
                conn = http.client.HTTPSConnection("t.me", timeout=20)
            conn.request("GET", f"/s/{ch}", headers={"User-Agent": "Python-urllib/3"})
            r = conn.getresponse(); b = r.read(); c = r.status; h = r.headers
            if (h.get("connection") or "").lower() == "close":
                conn.close(); conn = None
        except Exception as e:
            tg.log(url, "ERR", 0, "probe " + repr(e)[:100]); print("ERR", e); conn = None; break
        t1 = time.time()
        tg.log(url, c, len(b), f"probe {i}")
        if c != 200:
            w.writerow([i, dt.datetime.utcfromtimestamp(t0).isoformat(timespec="milliseconds"), round(t1 - t0, 3), c,
                        len(b), "", "", "", h.get("cache-control"), h.get("age"), h.get("date")])
            print("stop: status", c, "at request", i + 1); break
        ps = parse.parse(b)[0]
        new = [p["id"] for p in ps if p["id"] not in seen]
        for p in ps:
            seen.setdefault(p["id"], (p["time"], t0))
        if i > 0 and new:
            open(os.path.join(rd, f"{stamp}_{i}.html"), "wb").write(b)
        top = max(ps, key=lambda p: p["id"]) if ps else None
        w.writerow([i, dt.datetime.utcfromtimestamp(t0).isoformat(timespec="milliseconds"), round(t1 - t0, 3), c, len(b),
                    top["id"] if top else "", dt.datetime.utcfromtimestamp(top["time"]).isoformat() if top else "",
                    " ".join(map(str, new)) if i > 0 else "", h.get("cache-control"), h.get("age"), h.get("date")])
        f.flush()
print("wrote", fn)
