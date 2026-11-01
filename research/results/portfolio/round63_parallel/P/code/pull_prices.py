"""Pull hourly CLOB prices-history for token 0 of every universe market, one window per market:
[E - 8 d, min(C + 1 h, E + 4 d, 2024-12-31 23:59:59)] (<= 12 d; the API refuses ~> 14 d at fidelity 60).
argv[1] = 'main' (token 0, all) or 'tok1' (token 1, seeded subsample of 400 for the 1 - p check)."""
import sys, os, json, random, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket"
OUT = DATA + "/raw_prices"
CUT = 1735689599  # 2024-12-31 23:59:59 UTC
net.MIN_GAP["clob.polymarket.com"] = 0.12

def eligible(r):
    return r["ob"] and len(r["tokens"]) == 2 and r["vol"] >= 1000 and r["closed"] > r["end"] - 7 * 86400 and r["closed"] <= CUT

def job(r, k):
    fn = f"{OUT}/{r['id']}_{k}.json"
    if os.path.exists(fn):
        return "skip"
    E = int(r["end"])
    st = E - 8 * 86400
    en = min(int(r["closed"]) + 3600, E + 4 * 86400, CUT)
    url = f"https://clob.polymarket.com/prices-history?market={r['tokens'][k]}&startTs={st}&endTs={en}&fidelity=60"
    s, b = net.get(url)
    if s != 200:
        return f"fail {s}"
    with open(fn, "wb") as f:
        f.write(b)
    return "ok"

def main():
    R = [r for r in json.load(open(DATA + "/markets.json")) if eligible(r)]
    k = 0
    if sys.argv[1] == "tok1":
        random.Random(63).shuffle(R)
        R, k = R[:400], 1
    print(len(R), "markets", flush=True)
    done = 0
    with cf.ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda r: job(r, k), R):
            done += 1
            if res.startswith("fail"):
                print(res, flush=True)
            if done % 500 == 0:
                print(done, flush=True)
    print("done", flush=True)

if __name__ == "__main__":
    try:
        main()
    except net.Stop as e:
        print("STOP", e, flush=True)
