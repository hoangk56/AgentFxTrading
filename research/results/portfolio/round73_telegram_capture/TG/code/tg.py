"""Keyless fetcher for t.me (robots.txt and the public web preview t.me/s/<channel>) for round 73 stream TG.
Rules: >= 1.1 s between t.me requests (shared stamp file, so separate processes also keep the gap), default
Python-urllib UA (no browser disguise), no e-mail / contact headers, stop on 403, back off on 429.
Every request is logged to research/data/telegram_upbit/requests.log (UTC time, URL, status, bytes).
Usage: python -I tg.py robots | python -I tg.py page <channel> [before_id]"""
import os, sys, time, datetime as dt, http.client, fcntl
_conn = None
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_upbit"
RAW = os.path.join(D, "raw")
STAMP = os.path.join(D, ".last_req")
GAP = 1.1


class Stop(Exception):
    pass


def log(url, code, n, note=""):
    with open(os.path.join(D, "requests.log"), "a") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds')}\t{url}\t{code}\t{n}\t{note}\n")


def get(url, timeout=15):
    """Returns (body bytes or None, status, t_request_utc_epoch). Raises Stop on 403 / 429."""
    with open(STAMP, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        lk.seek(0); s = lk.read().strip()
        last = float(s) if s else 0.0
        w = last + GAP - time.time()
        if w > 0:
            time.sleep(w)
        t0 = time.time()
        lk.seek(0); lk.truncate(); lk.write(f"{t0:.3f}"); lk.flush()
        fcntl.flock(lk, fcntl.LOCK_UN)
    global _conn
    final = url
    try:
        # one keep-alive HTTPS connection to t.me (new TCP/TLS per request drew ~16 s stalls every ~15 requests)
        if _conn is None:
            _conn = http.client.HTTPSConnection("t.me", timeout=timeout)
        _conn.request("GET", url.split("t.me", 1)[1], headers={"User-Agent": "Python-urllib/3"})
        r = _conn.getresponse(); b = r.read(); c = r.status
        if (r.headers.get("connection") or "").lower() == "close":
            _conn.close(); _conn = None
    except Exception as e:  # network error
        _conn = None
        log(url, "ERR", 0, repr(e)[:120]); return None, -1, t0
    log(url, c, len(b or b""), "" if final == url else f"redirect->{final}")
    if c in (403, 429, 418, 503):
        raise Stop(f"{c} on {url}")
    return b, c, t0


if __name__ == "__main__":
    if sys.argv[1] == "robots":
        b, c, _ = get("https://t.me/robots.txt")
        os.makedirs(os.path.join(RAW, "robots"), exist_ok=True)
        open(os.path.join(RAW, "robots", "t.me_robots.txt"), "wb").write(b or b"")
        print(c, len(b or b""))
    elif sys.argv[1] == "page":
        ch = sys.argv[2]; bef = sys.argv[3] if len(sys.argv) > 3 else None
        url = f"https://t.me/s/{ch}" + (f"?before={bef}" if bef else "")
        b, c, t0 = get(url)
        os.makedirs(os.path.join(RAW, ch), exist_ok=True)
        fn = os.path.join(RAW, ch, f"b{bef or 'top'}.html")
        open(fn, "wb").write(b or b"")
        print(c, len(b or b""), fn)
