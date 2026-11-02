"""Stream A3: pull data.binance.vision daily aggTrades (SPOT for the alt, futures/um for BTCUSDT) on each event day.
fetch / parse copied from round65 A2/code/pull.py (only the URL kind and folders differ). Each zip is streamed to an
empty tmp folder, parsed, and deleted. Kept per (symbol, kind, day) in research/data/upbit_spot_notice/npz:
trades in [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min] plus A2's 1 s day series. BTCUSDT futures days already
in research/data/upbit_latency/npz (A2, read-only) are reused, not re-downloaded. Run with `python -I`."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/code")
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
A2NPZ = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_latency/npz"
EV = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/events.csv"
END = 1735689600000


def load_events():
    out = []
    for r in csv.DictReader(open(EV)):
        e = dict(r); e["N"] = int(r["N"]); e["L"] = int(r["L"])
        e["day"] = r["N_utc"][:10]; e["year"] = r["N_utc"][:4]
        assert e["N"] < END and e["L"] + 300000 < END
        out.append(e)
    return out


def fetch(kind, sym, day):
    base = "spot" if kind == "spot" else "futures/um"
    url = f"https://data.binance.vision/data/{base}/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    zp = os.path.join(TMP, f"{kind}-{sym}-{day}.zip")
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
    evs = load_events()
    jobs = {}
    for e in evs:
        day = e["day"]
        assert day == str(np.datetime64(int(e["L"] + 300000), "ms"))[:10] == str(np.datetime64(int(e["N"] - 600000), "ms"))[:10]
        jobs.setdefault(("spot", e["spot"], day), []).append(e)
        jobs.setdefault(("perp", "BTCUSDT", day), []).append(e)
    t0 = time.time()
    for k, ((kind, sym, day), ev) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][2], x[0][0]))):
        out = os.path.join(OUT, f"{kind}_{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        if kind == "perp" and os.path.exists(os.path.join(A2NPZ, f"{sym}_{day}.npz")):
            print("reuse A2", sym, day, flush=True); continue
        zp, s = fetch(kind, sym, day)
        if zp is None:
            print("MISS", kind, sym, day, s, flush=True); continue
        a = parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        keep = np.zeros(len(t), bool)
        for e in ev:
            keep |= (t >= e["N"] - 600000) & (t <= e["N"] + 1800000)
            keep |= (t >= e["L"] - 600000) & (t <= e["L"] + 300000)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]
        last[sec[ch]] = a[ch, 0]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            sec_p=last.astype(np.float64), sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(jobs)} {kind} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
