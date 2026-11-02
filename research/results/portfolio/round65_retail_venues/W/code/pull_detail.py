"""Fetch the detail (body) of candidate notices (category 거래) from api-manager.upbit.com."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, RAW
out = os.path.join(RAW, "detail"); os.makedirs(out, exist_ok=True)
ids = [int(x) for x in sys.argv[1:]]
if not ids:
    ids = [r["id"] for r in json.load(open(os.path.join(RAW, "cand_titles.json"))) if r["category"] == "거래"]
for i in ids:
    fn = os.path.join(out, f"{i}.json")
    if os.path.exists(fn):
        continue
    b, c = get(f"https://api-manager.upbit.com/api/v1/announcements/{i}")
    if c == 403:
        print("403 stop"); break
    if b and c == 200:
        open(fn, "wb").write(b)
    else:
        print("fail", i, c)
print("done", len(ids))
