"""Polite keyless GET with a request log (stream V, round 64).

Every request is logged to research/data/margin_venues/requests.log as
UTC time, URL, status, bytes. 403 stops the host for the rest of the process (and is
remembered in blocked_hosts.txt); 418 / 429 / 503 back off and retry. No key, no e-mail.
"""
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/margin_venues'
LOG = os.path.join(ROOT, 'requests.log')
BLOCKED = os.path.join(ROOT, 'blocked_hosts.txt')
UA = 'research-scout/1.0 (python-urllib)'
MIN_GAP = 0.3
_last = {}


def _blocked():
    if not os.path.exists(BLOCKED):
        return set()
    with open(BLOCKED) as f:
        return {x.strip() for x in f if x.strip()}


def _log(url, status, nbytes, note=''):
    t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with open(LOG, 'a') as f:
        f.write(f'{t}\t{url}\t{status}\t{nbytes}\t{note}\n')


def get(url, save_to=None, tries=4, timeout=30):
    """Return (status, bytes). Saves body to save_to (path) when status 200."""
    host = urllib.parse.urlparse(url).netloc
    if host in _blocked():
        return 'blocked', b''
    wait = 2.0
    for attempt in range(tries):
        dt = time.time() - _last.get(host, 0)
        if dt < MIN_GAP:
            time.sleep(MIN_GAP - dt)
        _last[host] = time.time()
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            body = e.read() or b''
            status = e.code
        except Exception as e:  # network error: log and retry
            _log(url, 'ERR', 0, type(e).__name__)
            time.sleep(wait)
            wait *= 2
            continue
        _log(url, status, len(body))
        if status == 403:
            with open(BLOCKED, 'a') as f:
                f.write(host + '\n')
            return 403, body
        if status in (418, 429, 503):
            time.sleep(max(wait, 10.0))
            wait *= 2
            continue
        if status == 200 and save_to:
            os.makedirs(os.path.dirname(save_to), exist_ok=True)
            with open(save_to, 'wb') as f:
                f.write(body)
        return status, body
    return 'gave_up', b''


if __name__ == '__main__':
    # usage: fetch.py URL [save_path]
    st, b = get(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(st, len(b))
    if len(sys.argv) <= 2:
        sys.stdout.write(b[:3000].decode('utf-8', 'replace') + '\n')
