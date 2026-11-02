"""Forward CAPTURE test for PREREG A2-D5L (promotion gate: notice detection <= 3 s after N on >= 80 % of live KRW-listing
notices). No orders, no account, keyless. Polls the public notice list the way a bot would and logs, for every notice
that appears after the logger started, the first time it was seen against its stamp N = first_listed_at.

- Endpoint: api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=all, one request every
  PERIOD s. Measured 2026-11-02: 1.5 s gets 429 after 15 requests from a residential IP and after 1-3 from the
  Hetzner VPS (also at 3 s and 5 s), so keyless polling cannot hold the <= 3 s gate; the logger runs slowly (20 s)
  only to check that notices appear at their stamp. Plain UA, no browser headers, no cookies kept.
- 418 / 429 / 503: back off 30 s, doubling to 15 min. 403: write STOP and exit for good (never work around it).
- Notices present at start are a baseline and are never graded. A notice whose id is new is graded once ("new"); a
  later change of listed_at is logged as "update" (not graded).
- The KRW-listing filter is the one fwd_a2.py uses (category 거래, listing keywords, KRW / 원화, not 종료 / 유의).
- Clock: the host must be NTP-synced (agentFx: systemd-timesyncd, checked 2026-11-02).

Files in the working directory: seen.json (state), capture.csv (one row per new / updated notice), heartbeat.log (one
line per 10 min: polls, errors, request time), STOP (only after a 403).
Usage: python3 -I capture_a2.py run      # loop forever (cron + flock restarts it)
       python3 -I capture_a2.py report   # summary of capture.csv"""
import csv, datetime as dt, json, os, statistics, sys, time, urllib.error, urllib.request

URL = "https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=all"
UA = "research-script"
PERIOD = 1.5
KEYS = ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")
FIELDS = ["kind", "id", "category", "krw_listing", "title", "first_listed_at", "listed_at", "seen_utc", "lag_s",
          "lag_listed_s", "http_date", "cf_cache", "rtt_ms"]


def krw_listing(n):
    t = n.get("title") or ""
    return int(n.get("category") == "거래" and any(k in t for k in KEYS) and ("KRW" in t or "원화" in t)
               and "종료" not in t and "유의" not in t)


def ts(s):
    return dt.datetime.fromisoformat(s).timestamp()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=5) as r:
        body = r.read()
        hdr = {"date": r.headers.get("date", ""), "cf": r.headers.get("cf-cache-status", "")}
    t1 = time.time()
    d = json.loads(body)["data"]
    return d.get("notices") or [], hdr, t0, t1


def run(period=None):
    global PERIOD
    PERIOD = float(period) if period else PERIOD
    if os.path.exists("STOP"):
        print("STOP present (403 seen earlier); not polling"); return
    seen = json.load(open("seen.json")) if os.path.exists("seen.json") else None
    new_file = not os.path.exists("capture.csv")
    out = open("capture.csv", "a", newline="", buffering=1)
    w = csv.DictWriter(out, fieldnames=FIELDS)
    if new_file:
        w.writeheader()
    hb = open("heartbeat.log", "a", buffering=1)
    polls = errs = 0; rtts = []; back = 0; clean = 0; last_hb = time.time(); dirty = False
    while True:
        start = time.time()
        try:
            ns, hdr, t0, t1 = fetch()
            polls += 1; rtts.append((t1 - t0) * 1000); clean += 1
            if clean >= 10:
                back = 0  # forget the backoff only after a clean streak
            # the response was produced somewhere inside [t0, t1]; t1 is what a bot would act on
            if seen is None:
                seen = {str(n["id"]): n.get("listed_at") for n in ns}; dirty = True
                hb.write(f"{iso(t1)} baseline {len(seen)} notices\n")
            for n in ns:
                i = str(n["id"])
                if i not in seen or seen[i] != n.get("listed_at"):
                    kind = "new" if i not in seen else "update"
                    if kind == "new" and t1 - ts(n["first_listed_at"]) > 3600:
                        kind = "old_resurfaced"  # an old notice outside the baseline page, moved up by an edit
                    seen[i] = n.get("listed_at"); dirty = True
                    w.writerow(dict(kind=kind, id=i, category=n.get("category"), krw_listing=krw_listing(n),
                                    title=n.get("title"), first_listed_at=n.get("first_listed_at"),
                                    listed_at=n.get("listed_at"), seen_utc=iso(t1),
                                    lag_s=round(t1 - ts(n["first_listed_at"]), 3),
                                    lag_listed_s=round(t1 - ts(n["listed_at"]), 3) if n.get("listed_at") else "",
                                    http_date=hdr["date"], cf_cache=hdr["cf"], rtt_ms=round((t1 - t0) * 1000)))
        except urllib.error.HTTPError as e:
            errs += 1
            hb.write(f"{iso(time.time())} HTTP {e.code} retry-after {e.headers.get('retry-after', '')} after {polls} polls\n")
            if e.code == 403:
                open("STOP", "w").write(iso(time.time()) + " 403\n"); return
            if e.code in (418, 429, 503):
                back = min(900, back * 2 if back else 30); clean = 0; time.sleep(back); continue
        except Exception as e:  # network / JSON: log and keep polling
            errs += 1
            hb.write(f"{iso(time.time())} error {type(e).__name__}: {str(e)[:120]}\n")
        if dirty:
            json.dump(seen, open("seen.json.tmp", "w")); os.replace("seen.json.tmp", "seen.json"); dirty = False
        if time.time() - last_hb >= 600:
            med = statistics.median(rtts) if rtts else 0
            hb.write(f"{iso(time.time())} polls {polls} errors {errs} rtt_median_ms {med:.0f}\n")
            polls = errs = 0; rtts = []; last_hb = time.time()
        time.sleep(max(0.0, PERIOD - (time.time() - start)))


def report():
    rows = [r for r in csv.DictReader(open("capture.csv")) if r["kind"] == "new"] if os.path.exists("capture.csv") else []
    def summ(rs, label):
        if not rs:
            print(f"{label}: 0 notices"); return
        lag = sorted(float(r["lag_s"]) for r in rs)
        ok = sum(1 for x in lag if x <= 3.0)
        q = lambda p: lag[min(len(lag) - 1, int(p * len(lag)))]
        print(f"{label}: n {len(lag)}, <= 3 s {ok} ({ok / len(lag):.0%}), median {q(0.5):.2f} s, p90 {q(0.9):.2f} s, "
              f"max {lag[-1]:.2f} s")
    summ(rows, "all new notices (diagnostic)")
    summ([r for r in rows if r["krw_listing"] == "1"], "KRW-listing notices (registered gate: >= 80 % within 3 s)")
    for r in rows[-10:]:
        print(" ", r["seen_utc"], r["category"], f"lag {float(r['lag_s']):+.2f} s", r["title"][:60])


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1] if len(sys.argv) > 1 else "report"](*sys.argv[2:3])
