"""Stream UC: fetch Upbit notice bodies (api-manager.upbit.com, robots: no rules) for DWSUSP notices that name a coin
with a Binance perp (declared body re-labelling rule in HYPOTHESES_UC.md). >= 1.6 s between requests, logged in
research/data/upbit_census/requests.log, saved under research/data/upbit_census/raw/detail/ (untrusted, parse with -I)."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
UC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round68_upbit_census/UC"
OUT = os.path.join(net.D, "raw", "detail"); os.makedirs(OUT, exist_ok=True)
ids = sorted({int(r["nid"]) for r in csv.DictReader(open(os.path.join(UC, "events_all.csv"))) if r["cat"] == "DWSUSP" and r["perp"]})
for k, i in enumerate(ids):
    fn = os.path.join(OUT, f"{i}.json")
    if os.path.exists(fn):
        continue
    url = f"https://api-manager.upbit.com/api/v1/announcements/{i}"
    r, s = net.opener(url)
    if r is None:
        print("fail", i, s, flush=True); continue
    b = r.read(); r.close(); net.log(url, s, len(b), "GET")
    open(fn, "wb").write(b)
    if k % 25 == 0:
        print(k, len(ids), flush=True)
print("done", len(ids))
