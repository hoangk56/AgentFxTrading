"""Stream CL: data.binance.vision futures/um daily aggTrades around each event (adapted from round65 A2/code/pull.py).
Events from CL/events.csv (built by events.py; every T < 2025-01-01). For each alt perp and every UTC day touched by
[T - 15 min, T + 65 min] the daily zip is streamed to an empty tmp folder, parsed, deleted. Kept per (symbol, day) in
research/data/tg_cl/npz: trades in the event windows plus the 1 s last-price / count series of the whole day.
BTCUSDT: a local futures-aggTrades npz with a 1 s series from an earlier round (non-HOLD folders) is reused when one
exists for that day, else the day is pulled the same way. Run with `python -I` (downloads are untrusted data)."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
DAY = 86400000
END = 1735689600000  # 2025-01-01: never request anything on or after it
EVF = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/CL/events.csv"
RD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
BTC_LOCAL = ["upbit_latency", "upbit_census", "btc_treasury_8k", "upbit_bybit_notice"]
W0, W1 = 15 * 60000, 65 * 60000


def btc_local(day):
    for d in BTC_LOCAL:
        p = os.path.join(RD, d, "npz", f"BTCUSDT_{day}.npz")
        if os.path.exists(p):
            return p
    return None


def load_events():
    E = list(csv.DictReader(open(EVF)))
    for e in E:
        e["T"] = int(e["T"]); assert e["T"] < END
    return E


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
            r.close(); net.log(url, s, n, "GET")
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


def days_of(T):
    a = str(np.datetime64(T - W0, "ms"))[:10]; b = str(np.datetime64(T + W1, "ms"))[:10]
    return sorted({a, b})


def main():
    evs = load_events()
    jobs = {}
    for e in evs:
        assert e["T"] + W1 < END
        for day in days_of(e["T"]):
            jobs.setdefault((e["perp"], day), []).append(e)
            if not btc_local(day):
                jobs.setdefault(("BTCUSDT", day), []).append(e)
    t0 = time.time(); todo = sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))
    print("jobs", len(todo), flush=True)
    for k, ((sym, day), ev) in enumerate(todo):
        out = os.path.join(OUT, f"{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        zp, s = fetch(sym, day)
        if zp is None:
            print("MISS", sym, day, s, flush=True); continue
        a = parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        keep = np.zeros(len(t), bool)
        for e in ev:
            keep |= (t >= e["T"] - W0) & (t <= e["T"] + W1)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]
        last[sec[ch]] = a[ch, 0]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            sec_p=last.astype(np.float64), sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(todo)} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
