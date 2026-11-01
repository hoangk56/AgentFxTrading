"""Pull closed Polymarket market metadata (gamma) with endDate in 2022-11..2024-12, per half-month window.
Raw pages -> research/data/polymarket/raw_gamma/ (untrusted). Never requests endDate >= 2025-01-01."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/raw_gamma"
d = dt.date(2022, 11, 1)
end = dt.date(2025, 1, 1)
while d < end:
    nxt = (d + dt.timedelta(days=16)).replace(day=1) if d.day > 1 else d.replace(day=16)
    nxt = min(nxt, end)
    lo = d.isoformat() + "T00:00:00Z"
    hi = (nxt - dt.timedelta(days=1)).isoformat() + "T23:59:59Z"
    off = 0
    while True:
        fn = f"{OUT}/m_{d.isoformat()}_{off}.json"
        if not os.path.exists(fn):
            url = (f"https://gamma-api.polymarket.com/markets?limit=100&offset={off}&closed=true"
                   f"&end_date_min={lo}&end_date_max={hi}&include_tag=true&order=id&ascending=true")
            s, b = net.get(url)
            if s != 200:
                print("FAIL", s, url); sys.exit(1)
            open(fn, "wb").write(b)
        n = len(json.load(open(fn)))
        print(d, off, n, flush=True)
        if n < 100:
            break
        off += 100
    d = nxt
