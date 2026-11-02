"""Round 71 FS: daily quote volume + trade count (no prices kept) for candidate spot USDT pairs, 2019-11-01..2024-12-31,
from data-api.binance.vision /api/v3/klines (1d). Writes data/spot_wicks/vol1d.npz. Run with python -I."""
import json, os, sys, csv
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net, common

START, END = 1572566400000, 1735689599999
API = "https://data-api.binance.vision/api/v3/klines?symbol={s}&interval=1d&startTime={a}&endTime={b}&limit=1000"


def one(s):
    out = []; a = START
    while True:
        b = net.get(API.format(s=s, a=a, b=END), tries=4)
        if b is None or b == "FAIL":
            return s, None if not out else out, b
        try:
            rows = json.loads(b)
        except Exception:
            return s, None, "json"
        if not isinstance(rows, list):
            return s, None, "notlist"
        for r in rows:
            if int(r[0]) <= END:
                out.append((int(r[0]), float(r[7]), int(r[8])))
        if len(rows) < 1000:
            return s, out, "ok"
        a = int(rows[-1][0]) + 1


def main():
    cands = common.candidate_symbols()
    print("candidates", len(cands), flush=True)
    res = {}
    with ThreadPoolExecutor(3) as ex:
        for k, (s, out, st) in enumerate(ex.map(one, cands)):
            res[s] = (out, st)
            if k % 100 == 0:
                print(k, s, st, flush=True)
    syms = sorted(s for s in res if res[s][0])
    T = []; S = []; Q = []; N = []
    for i, s in enumerate(syms):
        for t, q, n in res[s][0]:
            T.append(t); S.append(i); Q.append(q); N.append(n)
    np.savez(os.path.join(net.DATA, "vol1d.npz"), syms=np.array(syms), sym=np.array(S, np.int32),
             t=np.array(T, np.int64), qv=np.array(Q), n=np.array(N, np.int64))
    bad = {s: res[s][1] for s in res if not res[s][0]}
    print("with data", len(syms), "no data", len(bad), list(bad.items())[:20])


if __name__ == "__main__":
    main()
