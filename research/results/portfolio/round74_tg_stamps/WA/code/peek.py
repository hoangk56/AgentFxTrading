"""Print id, UTC time, edited flag and text head of saved pre-2025 pages (untrusted data, display only)."""
import sys, datetime as dt
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/coord")
import parse
H25 = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
for fn in sys.argv[1:]:
    ps, _ = parse.parse(open(fn, "rb").read())
    for p in ps:
        if p["time"] and p["time"] < H25:
            print(p["id"], dt.datetime.fromtimestamp(p["time"], dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), p["edited"], repr(p["text"][:160]))
