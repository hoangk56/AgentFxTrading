"""Logged GET: python -I fetch.py URL OUTFILE. Appends to research/data/kalshi_weather/requests.log."""
import sys, time, urllib.request, urllib.error, datetime, os
LOG = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/kalshi_weather/requests.log"
def get(url, out):
    req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0", "Accept": "application/json, text/plain, */*"})
    status, data = None, b""
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status, data = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, data = e.code, e.read()
    except Exception as e:
        status, data = "ERR:" + type(e).__name__, b""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f:
        f.write(f"{ts}\t{url}\t{status}\t{len(data)}\n")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    time.sleep(0.3)
    return status, len(data)
if __name__ == "__main__":
    print(get(sys.argv[1], sys.argv[2]))
