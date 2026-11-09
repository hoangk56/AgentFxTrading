"""Fetch the public.bybit.com/trading/ symbol index (robots.txt checked first) and save it (no prices)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
b, s = net.get_small("https://public.bybit.com/robots.txt"); print("robots", s, (b or b"")[:300])
b, s = net.get_small("https://public.bybit.com/trading/")
syms = sorted(set(re.findall(r'href="([A-Z0-9]+)/"', (b or b"").decode("utf-8", "replace"))))
json.dump(syms, open(os.path.join(net.D, "bybit_trading_syms.json"), "w"))
print(s, len(syms), syms[:10])
