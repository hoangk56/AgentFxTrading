"""Round 71 FS: robots.txt + listing probe (saves bodies under data/spot_wicks/probe/)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
P = os.path.join(net.DATA, "probe")
for name, url in [("robots_dbv.txt", "https://data.binance.vision/robots.txt"),
                  ("list_dbv.html", "https://data.binance.vision/?prefix=data/spot/monthly/klines/&delimiter=/"),
                  ("robots_s3.txt", "https://s3-ap-northeast-1.amazonaws.com/robots.txt")]:
    b = net.get(url, tries=2)
    if isinstance(b, bytes):
        open(os.path.join(P, name), "wb").write(b)
    print(name, None if b is None else (len(b) if isinstance(b, bytes) else b))
