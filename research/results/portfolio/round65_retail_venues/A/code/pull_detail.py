"""Fetch bodies of KRW-market listing notices (titles in A/listing_titles.json that mention KRW / 원화) from
api-manager.upbit.com at >= 1.5 s per request (robots.txt: no rules; logged). Reuses stream W's bodies read-only."""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, RAW
W = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw/detail"
out = os.path.join(RAW, "detail"); os.makedirs(out, exist_ok=True)
cand = json.load(open(os.path.join(os.path.dirname(__file__), "..", "listing_titles.json")))
ids = [r["id"] for r in cand if ("KRW" in r["title"] or "원화" in r["title"]) and "종료" not in r["title"] and "유의" not in r["title"]]
print(len(ids), "ids")
for i in ids:
    fn = os.path.join(out, f"{i}.json")
    if os.path.exists(fn):
        continue
    if os.path.exists(os.path.join(W, f"{i}.json")):
        shutil.copy(os.path.join(W, f"{i}.json"), fn); continue
    b, c = get(f"https://api-manager.upbit.com/api/v1/announcements/{i}")
    if c == 403:
        print("403 stop"); break
    if b and c == 200:
        open(fn, "wb").write(b)
    else:
        print("fail", i, c)
print("done")
