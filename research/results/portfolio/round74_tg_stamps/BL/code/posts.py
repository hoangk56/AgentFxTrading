"""Parse every saved page of @binance_announcements (untrusted HTML, data only; run with python -I) into one posts file
research/data/binance_tg_listing/posts_pre2025.json (N < 2025-01-01) plus hold_titles.txt (2025-26 titles only, for the
HOLD count; no prices ever). Dedup by post id."""
import sys, os, glob, json, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import parse
RAW = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/telegram_hist/raw/binance_announcements"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_tg_listing"
CUT = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
HOLD_END = dt.datetime(2026, 10, 30, tzinfo=dt.timezone.utc).timestamp()
ps = {}
for f in glob.glob(RAW + "/*.html"):
    for p in parse.parse(open(f, "rb").read())[0]:
        if p["time"] is None:
            continue
        ps[p["id"]] = dict(id=p["id"], t=int(p["time"]), text=p["text"], edited=bool(p["edited"]))
pre = [p for p in ps.values() if p["t"] < CUT]
hold = [p for p in ps.values() if CUT <= p["t"] < HOLD_END]
pre.sort(key=lambda p: p["id"]); hold.sort(key=lambda p: p["id"])
json.dump(pre, open(os.path.join(OUT, "posts_pre2025.json"), "w"))
json.dump([dict(id=p["id"], t=p["t"], title=p["text"].strip().split("\n")[0], edited=p["edited"]) for p in hold],
          open(os.path.join(OUT, "hold_titles.json"), "w"))
print("posts", len(ps), "pre2025", len(pre), "hold", len(hold), "min id", min(ps), "max id", max(ps))
