"""Forward capture logger for A2-D5L via Upbit's official Telegram channel (round 73 TG): polls the public web preview
https://t.me/s/upbit_news every PERIOD s on ONE keep-alive connection from one IP, keyless, and logs every post that
appears after start: post time (Telegram, whole seconds), first-seen time, and whether it is a KRW-listing notice.
End-to-end lag vs Upbit's stamp N = (post time - N, from TG's history: <= 1 s in 2026) + (seen - post time, measured
here). No account, no orders.

- 429 / 418 / 503: back off 30 s, doubling to 15 min (reset after 10 clean polls). 403 or a non-preview page (no posts
  parsed): write STOP and exit for good.
- Files in the working directory: seen.json, capture.csv, heartbeat.log (every 10 min: polls, errors, response time).
Usage: python3 -I tg_capture.py run [period] [until, e.g. 2026-11-09T00:00Z]   |   python3 -I tg_capture.py report"""
import csv, datetime as dt, http.client, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse  # copy of TG/code/parse.py (stdlib html.parser; the page is treated as data only)

CH = "upbit_news"
PERIOD = 1.5
FIELDS = ["post_id", "post_utc", "seen_utc", "seen_minus_post_s", "resp_s", "krw_listing", "text"]


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def krw_listing(t):
    return int(t.startswith("[거래]") and ("KRW" in t or "원화" in t) and "종료" not in t and "유의" not in t
               and any(k in t for k in ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")))


def run(period=None, until=None):
    per = float(period) if period else PERIOD
    end = dt.datetime.fromisoformat(until.replace("Z", "+00:00")).timestamp() if until else float("inf")
    if time.time() >= end:
        print("past end time; not polling"); return
    if os.path.exists("STOP"):
        print("STOP present; not polling"); return
    seen = set(json.load(open("seen.json"))) if os.path.exists("seen.json") else None
    newf = not os.path.exists("capture.csv")
    out = open("capture.csv", "a", newline="", buffering=1); w = csv.DictWriter(out, fieldnames=FIELDS)
    if newf:
        w.writeheader()
    hb = open("heartbeat.log", "a", buffering=1)
    hb.write(f"{iso(time.time())} start period {per}\n")
    conn = None; polls = errs = clean = 0; back = 0; resp = []; last_hb = time.time(); nxt = time.time()
    while time.time() < end:
        d = nxt - time.time()
        if d > 0:
            time.sleep(d)
        nxt = max(nxt + per, time.time())
        t0 = time.time()
        try:
            if conn is None:
                conn = http.client.HTTPSConnection("t.me", timeout=10)
            conn.request("GET", f"/s/{CH}", headers={"User-Agent": "research-script"})
            r = conn.getresponse(); body = r.read(); code = r.status
            if (r.headers.get("connection") or "").lower() == "close":
                conn.close(); conn = None
        except Exception as e:
            errs += 1; hb.write(f"{iso(time.time())} error {type(e).__name__}: {str(e)[:100]}\n")
            try:
                conn.close()
            except Exception:
                pass
            conn = None; continue
        t1 = time.time()
        if code in (418, 429, 503):
            errs += 1; clean = 0; back = min(900, back * 2 if back else 30)
            hb.write(f"{iso(t1)} HTTP {code}, backing off {back} s\n"); time.sleep(back); nxt = time.time(); continue
        if code == 403:
            open("STOP", "w").write(f"{iso(t1)} 403\n"); hb.write(f"{iso(t1)} HTTP 403, STOP\n"); return
        if code != 200:
            errs += 1; hb.write(f"{iso(t1)} HTTP {code}\n"); continue
        posts = parse.parse(body)[0]
        if not posts:
            open("STOP", "w").write(f"{iso(t1)} no posts parsed (login wall or layout change)\n")
            hb.write(f"{iso(t1)} no posts parsed, STOP\n"); return
        polls += 1; clean += 1; resp.append(t1 - t0)
        if clean >= 10:
            back = 0
        if seen is None:
            seen = {p["id"] for p in posts}
            hb.write(f"{iso(t1)} baseline {len(seen)} posts, newest {max(seen)}\n")
        else:
            for p in sorted(posts, key=lambda p: p["id"]):
                if p["id"] in seen:
                    continue
                seen.add(p["id"])
                txt = " ".join((p.get("text") or "").split())
                w.writerow(dict(post_id=p["id"], post_utc=iso(p["time"]) if p["time"] else "", seen_utc=iso(t1),
                                seen_minus_post_s=round(t1 - p["time"], 3) if p["time"] else "",
                                resp_s=round(t1 - t0, 3), krw_listing=krw_listing(txt), text=txt[:160]))
                json.dump(sorted(seen), open("seen.json.tmp", "w")); os.replace("seen.json.tmp", "seen.json")
        if time.time() - last_hb >= 600:
            hb.write(f"{iso(time.time())} polls {polls} errors {errs} resp_median_s "
                     f"{statistics.median(resp) if resp else 0:.3f}\n")
            polls = errs = 0; resp = []; last_hb = time.time()


def report():
    rows = list(csv.DictReader(open("capture.csv"))) if os.path.exists("capture.csv") else []
    lag = sorted(float(r["seen_minus_post_s"]) for r in rows if r["seen_minus_post_s"])
    if not lag:
        print("0 new posts"); return
    q = lambda p: lag[min(len(lag) - 1, int(p * len(lag)))]
    print(f"new posts {len(lag)} (KRW listing {sum(r['krw_listing'] == '1' for r in rows)}); seen - post time: "
          f"median {q(0.5):.2f} s, p80 {q(0.8):.2f}, p90 {q(0.9):.2f}, max {lag[-1]:.2f} "
          f"(post time is whole seconds: true delay is 0-1 s less)")
    for r in rows[-10:]:
        print(" ", r["seen_utc"], f"{float(r['seen_minus_post_s']):+.2f} s", r["krw_listing"], r["text"][:70])


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1] if len(sys.argv) > 1 else "report"](*sys.argv[2:4])
