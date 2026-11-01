"""Cost check: taker prints around each primary-cell entry (VAL 2024 only; data-api keeps ~3 years).
For each entry (cond, t): data-api /trades?market=cond&end=min(t+6h, 2024-12-31)&limit=200 (takerOnly; newest first).
Only price / size / side / outcomeIndex / timestamp are kept; wallet, names and profile fields are discarded.
argv[1] = trades_primary.json, argv[2] = max entries per cell (seeded sample)."""
import sys, os, json, random, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/prints"
os.makedirs(OUT, exist_ok=True)
CUT = 1735689599
net.MIN_GAP["data-api.polymarket.com"] = 0.1

KEEP = ("price", "size", "side", "outcomeIndex", "timestamp")


def job(x):
    t = int(x["t"])
    fn = f"{OUT}/{x['id']}_{t}.json"
    if os.path.exists(fn):
        return "skip"
    en = min(t + 6 * 3600, CUT)
    url = f"https://data-api.polymarket.com/trades?market={x['cond']}&end={en}&limit=200&takerOnly=true"
    s, b = net.get(url)
    if s != 200:
        return f"fail {s}"
    try:
        d = json.loads(b)
    except Exception:
        return "badjson"
    rows = [{k: z.get(k) for k in KEEP} for z in d if isinstance(z, dict)]
    json.dump(rows, open(fn, "w"))
    return "ok"


def main():
    T = json.load(open(sys.argv[1]))
    k = int(sys.argv[2])
    by = {}
    for x in T:
        if 1704067200 <= x["closed"] < 1735689600:
            by.setdefault(x["cell"], []).append(x)
    todo = []
    for c, lst in by.items():
        random.Random(63).shuffle(lst)
        todo += lst[:k]
    print(len(todo), "entries", flush=True)
    with cf.ThreadPoolExecutor(3) as ex:
        res = list(ex.map(job, todo))
    import collections
    print(collections.Counter(r.split()[0] for r in res), flush=True)


if __name__ == "__main__":
    try:
        main()
    except net.Stop as e:
        print("STOP", e)
