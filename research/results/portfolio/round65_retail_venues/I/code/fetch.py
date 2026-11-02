"""Polite fetcher for stream I. Usage: fetch.py <venue> <outname> <url>
Saves the body under research/data/retail_venues/<venue>/<outname>, logs UTC time, URL, status, bytes to
research/data/retail_venues/requests.log. >= 0.30 s between requests per host (state file), one retry after back-off
on 418 / 429 / 503, host blocked for the rest of the stream on 403. Plain UA, no personal data, no key."""
import json, os, sys, time, urllib.request, urllib.error

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/retail_venues"
UA = {"User-Agent": "agentfx-research-script/1.0", "Accept": "application/json, text/plain, */*"}
GAP = 0.30


def main(venue, name, url):
    host = url.split("/")[2]
    blocked_f = os.path.join(DATA, "blocked_hosts.txt")
    blocked = open(blocked_f).read().split() if os.path.exists(blocked_f) else []
    if host in blocked:
        print("BLOCKED host (403 earlier):", host); return 2
    st_f = os.path.join(DATA, ".last_req.json")
    st = json.load(open(st_f)) if os.path.exists(st_f) else {}
    dt = time.time() - st.get(host, 0.0)
    if dt < GAP:
        time.sleep(GAP - dt)
    os.makedirs(os.path.join(DATA, venue), exist_ok=True)
    log = open(os.path.join(DATA, "requests.log"), "a")
    for attempt in range(2):
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        st[host] = time.time(); json.dump(st, open(st_f, "w"))
        code, body = None, b""
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                code, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            code = e.code
            try:
                body = e.read()
            except Exception:
                body = b""
            if code in (418, 429, 503) and attempt == 0:
                log.write(f"{ts}\t{url}\t{code}\t{len(body)}\n"); log.flush()
                ra = e.headers.get("Retry-After")
                time.sleep(int(ra) if ra and ra.isdigit() and int(ra) < 120 else 20)
                continue
        except Exception as e:
            code = f"ERR {type(e).__name__}"
        log.write(f"{ts}\t{url}\t{code}\t{len(body)}\n"); log.flush()
        if code == 403:
            open(blocked_f, "a").write(host + "\n")
        out = os.path.join(DATA, venue, name)
        open(out, "wb").write(body)
        print(code, len(body), out)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
