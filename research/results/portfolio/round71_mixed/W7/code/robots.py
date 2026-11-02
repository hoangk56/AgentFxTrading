import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
for u in [
          "https://public.bybit.com/robots.txt", "https://fapi.binance.com/robots.txt", "https://api.bybit.com/robots.txt"]:
    b, s = net.get(u, "robots")
    open(os.path.join(net.D, "raw", u.split("/")[2] + "_robots.txt"), "wb").write(b or str(s).encode())
    print(u, s, (b or b"")[:200])
