"""Stream A2: pull data.binance.vision futures/um daily aggTrades for each event's alt and BTCUSDT on the event day.
Each zip is streamed to an empty tmp folder, parsed, and deleted. Kept per (symbol, day) in research/data/upbit_latency/npz:
 - trades (t ms, price, qty, buyer_maker) inside the event windows [N - 10 min, N + 30 min] and [L - 10 min, L + 5 min];
 - a 1 s series over the day: last price at or before the end of each second (forward-filled) and the trade count.
Run with `python -I` (downloads are untrusted data)."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2/code")
import numpy as np
import net
from events import load_events

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
DAY = 86400000
END = 1735689600000  # 2025-01-01: never request anything on or after it


def windows(evs):
    w = []
    for e in evs:
        w.append((e["N"] - 600000, e["N"] + 1800000))
        w.append((e["L"] - 600000, e["L"] + 300000))
    return w


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
        except Exception as ex:  # read timeout mid-stream: log, drop the partial file, retry
            net.log(url, "ERR:" + type(ex).__name__, n, "GET partial")
            r.close(); os.remove(zp); time.sleep(10 * (att + 1))
    return None, "fail"


def parse(zp):
    with zipfile.ZipFile(zp) as z:
        name = z.namelist()[0]
        raw = z.read(name)
    os.remove(zp)
    raw = raw.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
    if not raw[:1].isdigit():  # header line
        raw = raw[raw.index(b"\n") + 1:]
    a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(1, 2, 5, 6), dtype=np.float64, ndmin=2)
    return a


def main():
    evs = load_events()
    jobs = {}
    for e in evs:
        day = str(np.datetime64(int(e["N"]), "ms"))[:10]
        assert day == str(np.datetime64(int(e["L"] + 300000), "ms"))[:10] == str(np.datetime64(int(e["N"] - 600000), "ms"))[:10]
        assert e["L"] + 300000 < END
        jobs.setdefault((e["perp"], day), []).append(e)
        jobs.setdefault(("BTCUSDT", day), []).append(e)
    t0 = time.time()
    for k, ((sym, day), ev) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))):
        out = os.path.join(OUT, f"{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        zp, s = fetch(sym, day)
        if zp is None:
            print("MISS", sym, day, s, flush=True); continue
        a = parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:  # microseconds
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        keep = np.zeros(len(t), bool)
        for a_, b_ in windows(ev):
            keep |= (t >= a_) & (t <= b_)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]  # last trade of each second (t sorted)
        last[sec[ch]] = a[ch, 0]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            sec_p=last.astype(np.float64), sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(jobs)} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
