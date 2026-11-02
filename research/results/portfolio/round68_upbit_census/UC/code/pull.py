"""Stream UC: data.binance.vision futures/um daily aggTrades for each pulled event's alt and BTCUSDT (A2 pull.py logic;
windows changed). Every zip is streamed to an empty tmp folder, parsed and deleted. Kept per (symbol, day) in
research/data/upbit_census/npz/:
 - trades (t ms, price, qty, buyer_maker) inside [N - 10 min, N + 30 min] and [N + 3595 s, N + 3665 s] (the 60-min exit);
 - a 1 s last-price / trade-count series of the whole day (random benchmark).
Event order = the declared pull priority (pull_list.csv). Never requests a day >= 2025-01-01. Run with `python -I`."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
UC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round68_upbit_census/UC"
END = 1735689600000
DAYMS = 86400000
BUDGET = float(os.environ.get("BUDGET_MIN", "45")) * 60


def windows(N):
    return [(N - 600000, N + 1800000), (N + 3595000, N + 3665000)]


def days_of(N):
    a = (N - 600000) // DAYMS; b = (N + 3665000) // DAYMS
    return [str(np.datetime64(int(k * DAYMS), "ms"))[:10] for k in range(a, b + 1)]


def fetch(sym, day):
    url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    zp = os.path.join(TMP, f"{sym}-{day}.zip")
    for att in range(4):
        r, s = net.opener(url)
        if r is None:
            return None, s
        n = 0
        try:
            with open(zp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); n += len(b)
            r.close()
            net.log(url, s, n, "GET")
            return zp, s
        except Exception as ex:
            net.log(url, "ERR:" + type(ex).__name__, n, "GET partial")
            r.close(); os.remove(zp); time.sleep(10 * (att + 1))
    return None, "fail"


def parse(zp):
    with zipfile.ZipFile(zp) as z:
        raw = z.read(z.namelist()[0])
    os.remove(zp)
    raw = raw.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    return np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(1, 2, 5, 6), dtype=np.float64, ndmin=2)


def main():
    evs = list(csv.DictReader(open(os.path.join(UC, "pull_list.csv"))))
    jobs = {}
    for e in evs:
        N = int(e["N"])
        for day in days_of(N):
            assert day < "2025-01-01"
            for sym in (e["perp"], "BTCUSDT"):
                jobs.setdefault((sym, day), {"w": [], "first": len(jobs)})["w"] += windows(N)
    order = sorted(jobs.items(), key=lambda x: x[1]["first"])
    t0 = time.time()
    for k, ((sym, day), j) in enumerate(order):
        if time.time() - t0 > BUDGET:
            print("BUDGET STOP at job", k, flush=True); break
        out = os.path.join(OUT, f"{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        zp, s = fetch(sym, day)
        if zp is None:
            print("MISS", sym, day, s, flush=True)
            np.savez_compressed(out, miss=1); continue
        a = parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        keep = np.zeros(len(t), bool)
        for a_, b_ in j["w"]:
            keep |= (t >= a_) & (t <= b_)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]
        last[sec[ch]] = a[ch, 0]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            sec_p=last.astype(np.float64), sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(order)} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
