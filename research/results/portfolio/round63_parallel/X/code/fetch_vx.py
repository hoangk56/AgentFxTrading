"""Fetch Cboe CFE daily VX futures files (one per monthly expiry), keyless.

URL: https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<YYYY-MM-DD>.csv
Candidate expiry = Wednesday 30 calendar days before the 3rd Friday of the following month; if that file is
missing (holiday shift) try the business day before / after. Raw files go to research/data/cboe_vx/raw/
(untrusted, never executed). Every request is logged to research/data/cboe_vx/requests.log
(UTC time, URL, status, bytes). Spacing >= 1.0 s. 403 -> stop.

Usage: python -I fetch_vx.py <first_year> <last_year_month YYYY-MM>
"""
import datetime as dt
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/cboe_vx'
RAW = os.path.join(ROOT, 'raw')
LOG = os.path.join(ROOT, 'requests.log')
BASE = 'https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{}.csv'
UA = 'research-script/1.0 (python urllib)'


def third_friday(y, m):
    d = dt.date(y, m, 1)
    off = (4 - d.weekday()) % 7
    return d + dt.timedelta(days=off + 14)


def candidate_expiry(y, m):
    """Expiry of the VX contract of month (y, m): 30 days before the 3rd Friday of month m+1."""
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return third_friday(ny, nm) - dt.timedelta(days=30)


def log(url, status, nbytes):
    with open(LOG, 'a') as f:
        f.write('{}\t{}\t{}\t{}\n'.format(dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                          url, status, nbytes))


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            log(url, r.status, len(data))
            return r.status, data
    except urllib.error.HTTPError as e:
        log(url, e.code, 0)
        return e.code, b''
    except Exception as e:  # noqa
        log(url, 'ERR ' + type(e).__name__, 0)
        return None, b''


def main():
    y0 = int(sys.argv[1])
    ylast, mlast = map(int, sys.argv[2].split('-'))
    os.makedirs(RAW, exist_ok=True)
    y, m = y0, 1
    while (y, m) <= (ylast, mlast):
        c = candidate_expiry(y, m)
        done = [f for f in os.listdir(RAW) if f.startswith('VX_%04d-%02d' % (c.year, c.month))]
        if not done:
            for shift in (0, -1, 1, -2):
                d = c + dt.timedelta(days=shift)
                url = BASE.format(d.isoformat())
                st, data = get(url)
                time.sleep(1.0)
                if st == 403:
                    # cdn.cboe.com is S3: a missing key answers 403 AccessDenied (robots.txt too). Try the next
                    # candidate date; if no candidate exists the month is reported MISSING and we stop.
                    continue
                if st in (429, 503, 418):
                    print('backoff', st)
                    time.sleep(30)
                if st == 200 and data:
                    with open(os.path.join(RAW, 'VX_%s.csv' % d.isoformat()), 'wb') as f:
                        f.write(data)
                    print('ok', d, len(data))
                    break
            else:
                print('MISSING', y, m, c, '-> stop (possible block)')
                return
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


if __name__ == '__main__':
    main()
