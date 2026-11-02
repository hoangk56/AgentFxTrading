"""Posting-time pattern of a channel (how often posts land on hh:00 / hh:30 within 2 s; per UTC hour).
Usage: python -I posttimes.py <channel> <since YYYY-MM-DD>"""
import os, sys, datetime as dt, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze
ps = [p for p in analyze.posts(sys.argv[1]) if p["time"] >= dt.datetime.fromisoformat(sys.argv[2]).replace(tzinfo=dt.timezone.utc).timestamp()]
days = (ps[-1]["time"] - ps[0]["time"]) / 86400
print(len(ps), "posts in", round(days), "days ->", round(len(ps) / days, 2), "/day")
c = collections.Counter()
for p in ps:
    t = dt.datetime.fromtimestamp(p["time"], dt.timezone.utc)
    if t.minute in (0, 30) and t.second <= 2:
        c[f"{t.hour:02d}:{t.minute:02d}"] += 1
print("posts at hh:00/hh:30 (+<=2 s) by UTC slot:", sorted(c.items(), key=lambda kv: -kv[1])[:12], "total", sum(c.values()))
print("per UTC hour:", sorted(collections.Counter(dt.datetime.fromtimestamp(p["time"], dt.timezone.utc).hour for p in ps).items()))
