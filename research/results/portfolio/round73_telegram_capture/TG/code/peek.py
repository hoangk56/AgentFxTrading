"""Print a channel's posts between two UTC dates (text truncated). Usage: python -I peek.py <ch> <from> <to> [n]"""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze
a, b = (dt.datetime.fromisoformat(x).replace(tzinfo=dt.timezone.utc).timestamp() for x in sys.argv[2:4])
ps = [p for p in analyze.posts(sys.argv[1]) if a <= p["time"] < b]
for p in ps[: int(sys.argv[4]) if len(sys.argv) > 4 else 15]:
    print(p["id"], dt.datetime.fromtimestamp(p["time"], dt.timezone.utc).isoformat()[:19], repr(p["text"][:100]))
print(len(ps), "posts")
