"""Read and log robots.txt of the two hosts used (stream UC)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
for h in ("api-manager.upbit.com", "data.binance.vision"):
    url = f"https://{h}/robots.txt"
    r, s = net.opener(url)
    b = r.read() if r else b""
    if r: r.close()
    net.log(url, s, len(b), "GET robots")
    open(os.path.join(net.D, "raw", f"robots_{h}.txt"), "wb").write(b)
    print(h, s, b[:300])
