"""Pull the full Upbit announcement list (all categories) from api-manager.upbit.com (robots.txt: no rules)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, RAW
out = os.path.join(RAW, "list_all"); os.makedirs(out, exist_ok=True)
NP = int(sys.argv[1]) if len(sys.argv) > 1 else 298
for p in range(1, NP + 1):
    fn = os.path.join(out, f"p{p:04d}.json")
    if os.path.exists(fn):
        continue
    b, c = get(f"https://api-manager.upbit.com/api/v1/announcements?os=web&page={p}&per_page=20&category=all")
    if c == 403:
        print("403 stop"); break
    if b and c == 200:
        open(fn, "wb").write(b)
    else:
        print("fail", p, c)
print("done")
