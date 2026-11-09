"""Probe: robots.txt of okx.com / static.okx.com and one HEAD of a 2023 OKX daily trade dump (no body read)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
for u in ["https://www.okx.com/robots.txt", "https://static.okx.com/robots.txt"]:
    b, s = net.get_small(u); print(u, s, (b or b"")[:600])
for u in ["https://static.okx.com/cdn/okex/traderecords/trades/daily/20230315/BTC-USDT-SWAP-trades-2023-03-15.zip",
          "https://www.okx.com/cdn/okex/traderecords/trades/daily/20230315/BTC-USDT-SWAP-trades-2023-03-15.zip"]:
    r, s = net.opener(u, method="HEAD")
    print(u, s, dict(r.headers) if r else None)
    net.log(u, s, 0, "HEAD")
