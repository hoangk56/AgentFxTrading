"""Keyless freshness test of public t.me forms (round 74 TG2, for A2-D5L's @upbit_news capture). From the Mac only.

Rotates a list of routes `<channel>:<form>`, one request per tick (tick >= 3 s), through the SAME lock file as the
shared round-74 fetcher (coord/tg.py: >= 1.5 s between any two t.me requests from this Mac), one keep-alive
connection, plain `Python-urllib/3` UA, no other headers. Stops for good on 403 / 429 / 418 / 503.
Pages are untrusted data: parsed with coord/parse.py (stdlib html.parser), never executed or followed.

Forms (nxt = newest id this route has shown + 1; each route finds every post by itself):
  top     /s/<ch>                  the preview page the round-73 / agentFx poller reads
  embed   /<ch>/<nxt>?embed=1      the per-post widget of the next id (empty page until it exists)
  after   /s/<ch>?after=<nxt - 1>  the preview page of posts after the newest seen
  before  /s/<ch>?before=<nxt + 1>
  bcyc    /s/<ch>?before=<nxt + 1 + k>, k cycling 0..49: same page content, a URL not requested in the last ~20 min
          (tests whether the preview lag is a per-URL cache)
For each new post and route: the time of the previous request of that route that did not show it (prev_check) and the
first request that did (seen): the post became visible on that route in (prev_check, seen].

Files (research/data/telegram_hist/tg2/): requests.log (UTC, url, status, bytes, resp s, cache headers; also appended
to the shared telegram_hist/requests.log), firstseen.csv, state.json, poll*.out, STOP.
Usage:
  python3 -I tg2_poll.py probe [channel]
  python3 -I tg2_poll.py run <until ISO Z> <tick_s> <ch:form,ch:form,...>
  python3 -I tg2_poll.py report [agentFx capture.csv]"""
import csv, datetime as dt, fcntl, http.client, json, os, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "coord"))
import parse  # noqa: E402  (coord/parse.py)

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist"
OUT = os.path.join(D, "tg2")
STAMP = os.path.join(D, ".last_req")  # shared with coord/tg.py
GAP = 1.5
MIN_TICK = 3.0
UA = "Python-urllib/3"
FIELDS = ["route", "channel", "post_id", "post_utc", "prev_check_utc", "seen_utc", "seen_minus_post_s",
          "prev_check_minus_post_s", "resp_s"]
FORMS = ("top", "embed", "after", "before", "bcyc")
CYC = 50  # bcyc: before=<nxt + 1 + k>, k = 0..CYC-1 in turn, so a URL repeats only every CYC requests of the route
NEED_POSTS = ("top", "before", "bcyc")  # these pages always list posts; none parsed = layout change / wall -> STOP


class Stop(Exception):
    pass


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds")


def parse_routes(spec):
    out = []
    for x in spec.split(","):
        ch, form = x.strip().split(":")
        if form not in FORMS:
            raise ValueError(form)
        out.append((ch, form))
    return out


def route_path(ch, form, nxt, k=0):
    if form == "bcyc":
        return f"/s/{ch}?before={nxt + 1 + k % CYC}"
    if form == "top":
        return f"/s/{ch}"
    if form == "embed":
        return f"/{ch}/{nxt}?embed=1"
    if form == "after":
        return f"/s/{ch}?after={nxt - 1}"
    if form == "before":
        return f"/s/{ch}?before={nxt + 1}"
    raise ValueError(form)


def new_posts(posts, newest):
    """Posts with id > newest and a time, sorted by id."""
    return sorted((p for p in posts if p["id"] > newest and p.get("time")), key=lambda p: p["id"])


def seen_row(key, ch, p, prev_t, t0, t1):
    return dict(route=key, channel=ch, post_id=p["id"], post_utc=iso(p["time"]),
                prev_check_utc=iso(prev_t) if prev_t else "", seen_utc=iso(t1),
                seen_minus_post_s=round(t1 - p["time"], 3),
                prev_check_minus_post_s=round(prev_t - p["time"], 3) if prev_t else "", resp_s=round(t1 - t0, 3))


class Client:
    def __init__(self):
        self.conn = None
        os.makedirs(OUT, exist_ok=True)

    @staticmethod
    def _lock_gap():
        with open(STAMP, "a+") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            lk.seek(0)
            s = lk.read().strip()
            last = float(s) if s else 0.0
            w = last + GAP - time.time()
            if w > 0:
                time.sleep(w)
            t0 = time.time()
            lk.seek(0); lk.truncate(); lk.write(f"{t0:.3f}"); lk.flush()
            fcntl.flock(lk, fcntl.LOCK_UN)
        return t0

    def get(self, path):
        t0 = self._lock_gap()
        url = "https://t.me" + path
        try:
            if self.conn is None:
                self.conn = http.client.HTTPSConnection("t.me", timeout=10)
            self.conn.request("GET", path, headers={"User-Agent": UA})
            r = self.conn.getresponse(); b = r.read(); c = r.status
            hdr = {k.lower(): v for k, v in r.getheaders()}
            if (hdr.get("connection") or "").lower() == "close":
                self.conn.close(); self.conn = None
        except Exception as e:
            self.conn = None
            self.log(url, "ERR", 0, time.time() - t0, repr(e)[:120])
            return None, -1, t0, time.time(), {}
        t1 = time.time()
        cache = ";".join(f"{k}={hdr[k]}" for k in ("cache-control", "age", "x-cache", "expires", "last-modified",
                                                  "etag") if k in hdr)
        self.log(url, c, len(b or b""), t1 - t0, cache)
        if c in (403, 429, 418, 503):
            open(os.path.join(OUT, "STOP"), "w").write(f"{iso(t1)} {c} on {url}\n")
            raise Stop(f"{c} on {url}")
        return b, c, t0, t1, hdr

    @staticmethod
    def log(url, code, n, resp, note=""):
        line = f"{iso(time.time())}\t{url}\t{code}\t{n}\t{resp:.3f}\t{note}\n"
        for p in (os.path.join(OUT, "requests.log"), os.path.join(D, "requests.log")):
            with open(p, "a") as f:
                f.write(line)


def load_state():
    p = os.path.join(OUT, "state.json")
    return json.load(open(p)) if os.path.exists(p) else {"own": {}, "track_from": {}}


def save_state(st):
    p = os.path.join(OUT, "state.json")
    json.dump(st, open(p + ".tmp", "w")); os.replace(p + ".tmp", p)


def append_seen(row):
    p = os.path.join(OUT, "firstseen.csv")
    new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def probe(ch="upbit_news"):
    c = Client()
    b, code, t0, t1, h = c.get(route_path(ch, "top", 0))
    newest = max(p["id"] for p in parse.parse(b or b"")[0])
    print("top", code, len(b or b""), f"{t1 - t0:.3f}s", "newest", newest, h.get("cache-control"))
    for form in ("embed", "after", "before"):
        for nxt in (newest, newest + 1):
            b, code, t0, t1, h = c.get(route_path(ch, form, nxt))
            print(form, nxt, code, len(b or b""), f"{t1 - t0:.3f}s", "ids",
                  [p["id"] for p in parse.parse(b or b"")[0]][-4:], h.get("cache-control"))


def run(until, tick, spec):
    tick = max(MIN_TICK, float(tick))
    end = dt.datetime.fromisoformat(until.replace("Z", "+00:00")).timestamp()
    routes = parse_routes(spec)
    if os.path.exists(os.path.join(OUT, "STOP")):
        print("STOP present"); return
    c = Client()
    st = load_state()
    fs = os.path.join(OUT, "firstseen.csv")
    first = {(r["route"], int(r["post_id"])) for r in csv.DictReader(open(fs))} if os.path.exists(fs) else set()
    for ch in sorted({ch for ch, _ in routes}):
        if ch not in st["track_from"]:
            b, code, *_ = c.get(route_path(ch, "top", 0))
            st["track_from"][ch] = max(p["id"] for p in parse.parse(b)[0]) + 1
    for ch, form in routes:
        st["own"].setdefault(f"{ch}:{form}", st["track_from"][ch] - 1)
    save_state(st)
    prev = {}  # route -> time of its last request
    ncalls = {}
    print(iso(time.time()), "start", routes, "tick", tick, "track_from", st["track_from"], flush=True)
    i = 0; nxt_t = time.time(); polls = 0; last_hb = time.time()
    try:
        while time.time() < end:
            d = nxt_t - time.time()
            if d > 0:
                time.sleep(d)
            nxt_t = max(nxt_t + tick, time.time())
            ch, form = routes[i % len(routes)]; i += 1
            key = f"{ch}:{form}"
            ncalls[key] = ncalls.get(key, 0) + 1
            b, code, t0, t1, _ = c.get(route_path(ch, form, st["own"][key] + 1, ncalls[key]))
            polls += 1
            if code != 200 or not b:
                continue
            posts = parse.parse(b)[0]
            if form in NEED_POSTS and not posts:
                open(os.path.join(OUT, "STOP"), "w").write(f"{iso(t1)} no posts parsed on {key}\n")
                print(iso(t1), "no posts parsed, STOP", flush=True); return
            newest_all = max(st["own"][f"{c2}:{f2}"] for c2, f2 in routes if c2 == ch)
            for p in new_posts(posts, max(st["own"][key], st["track_from"][ch] - 1)):
                if (key, p["id"]) in first:
                    continue
                first.add((key, p["id"]))
                append_seen(seen_row(key, ch, p, prev.get(key), t0, t1))
                print(iso(t1), key, p["id"], f"+{t1 - p['time']:.2f}s", flush=True)
            top_id = max([p["id"] for p in posts], default=0)
            if top_id > st["own"][key]:
                st["own"][key] = top_id
            elif form == "embed" and not posts and newest_all > st["own"][key] + 1:
                st["own"][key] += 1  # id own+1 is missing (deleted / service) while later ids exist: skip it
            prev[key] = t0
            save_state(st)
            if time.time() - last_hb >= 600:
                print(iso(time.time()), "alive polls", polls, "own", st["own"], flush=True)
                polls = 0; last_hb = time.time()
    except Stop as e:
        print(iso(time.time()), "STOP", e, flush=True)
    save_state(st)
    print(iso(time.time()), "end", flush=True)


def table(rows, capture_rows=()):
    """{(channel, post_id): {route: (prev_check - post, seen - post)}}; agentFx top-page rows join as one route."""
    out = {}
    for r in rows:
        if not r["prev_check_utc"]:  # the route's first request (route added after the post): no bound, skipped
            continue
        lo = float(r["prev_check_minus_post_s"]) if r["prev_check_minus_post_s"] else None
        out.setdefault((r["channel"], int(r["post_id"])), {})[r["route"]] = (lo, float(r["seen_minus_post_s"]))
    for r in capture_rows:
        k = ("upbit_news", int(r["post_id"]))
        if k in out:
            out[k]["agentFx:top1.5s"] = (None, float(r["seen_minus_post_s"]))
    return out


def report(capture=None):
    fs = os.path.join(OUT, "firstseen.csv")
    rows = list(csv.DictReader(open(fs))) if os.path.exists(fs) else []
    cap = list(csv.DictReader(open(capture))) if capture and os.path.exists(capture) else []
    tb = table(rows, cap)
    routes = sorted({k for v in tb.values() for k in v})
    print("channel", "post", *routes, sep="\t")
    for k in sorted(tb):
        cells = []
        for r in routes:
            if r not in tb[k]:
                cells.append("-")
            else:
                lo, hi = tb[k][r]
                cells.append(f"({lo:.0f},{hi:.1f}]" if lo is not None else f"{hi:.1f}")
        print(*k, *cells, sep="\t")
    for r in routes:
        xs = [v[r][1] for v in tb.values() if r in v]
        if xs:
            print(r, "n", len(xs), "median seen-post", f"{statistics.median(xs):.1f}", "<=3s", sum(x <= 3 for x in xs))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "probe":
        probe(*sys.argv[2:3])
    elif cmd == "run":
        run(*sys.argv[2:5])
    else:
        report(*sys.argv[2:3])
