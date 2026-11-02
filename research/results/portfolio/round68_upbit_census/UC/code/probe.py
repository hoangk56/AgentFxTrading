"""HEAD size probes on data.binance.vision daily aggTrades (sizes only, no content), logged."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
for a in sys.argv[1:]:
    sym, day = a.split(":")
    url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    r, s = net.opener(url, "HEAD")
    n = int(r.headers.get("Content-Length", 0)) if r else 0
    if r: r.close()
    net.log(url, s, n, "HEAD size probe")
    print(sym, day, s, round(n / 1e6, 1), "MB")
