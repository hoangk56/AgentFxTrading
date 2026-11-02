"""List Upbit notice titles (stream W's list pages, read-only) in category 거래 that look like new-market notices,
first_listed_at UTC in 2019-10-01 .. 2024-12-31 (hard cut ts < 2025-01-01). Output A/listing_titles.json."""
import json, glob, os, datetime as dt
SRC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_notices/raw/list_all"
OUT = os.path.join(os.path.dirname(__file__), "..", "listing_titles.json")
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
LO = dt.datetime(2019, 10, 1, tzinfo=dt.timezone.utc)
rows = {}
for f in sorted(glob.glob(os.path.join(SRC, "p*.json"))):
    for n in json.load(open(f))["data"]["notices"]:
        t = dt.datetime.fromisoformat(n["first_listed_at"]).astimezone(dt.timezone.utc)
        if not (LO <= t < CUT):
            continue
        rows[n["id"]] = dict(id=n["id"], t_utc=t.strftime("%Y-%m-%d %H:%M:%S"), cat=n["category"], title=n["title"])
rows = sorted(rows.values(), key=lambda r: r["t_utc"])
keys = ("추가", "마켓 오픈", "신규", "상장", "거래지원 개시", "거래 지원 개시")
cand = [r for r in rows if r["cat"] == "거래" and any(k in r["title"] for k in keys)]
json.dump(cand, open(OUT, "w"), ensure_ascii=False, indent=0)
import collections
print(len(rows), "notices in window;", collections.Counter(r["cat"] for r in rows))
print(len(cand), "candidates")
for r in cand:
    print(r["id"], r["t_utc"], r["title"])
