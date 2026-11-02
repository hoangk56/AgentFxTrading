"""Stream M8: pull data.binance.vision futures/um daily aggTrades BTCUSDT for each event day (<= 2024-12-31).
Each zip goes to an empty tmp folder, is parsed and deleted. Kept per day in research/data/btc_treasury_8k/npz:
 - trades (t ms, price, qty, buyer_maker) inside [T - 10 min, T + 70 min] of each event on that day;
 - a 1 s series over the day: last trade price at or before the end of each second (ffill) and the trade count.
Run with `python -I` (downloads are untrusted data). Input: research/data/btc_treasury_8k/events.csv (column T_ms)."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
END = 1735689600000  # 2025-01-01 00:00 UTC: nothing on or after it is requested
SYM = "BTCUSDT"


def fetch(day):
    url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{SYM}/{SYM}-aggTrades-{day}.zip"
    zp = os.path.join(TMP, f"{SYM}-{day}.zip")
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
    src = sys.argv[1] if len(sys.argv) > 1 else "events.csv"
    ev = [int(r["T_ms"]) for r in csv.DictReader(open(os.path.join(D, src)))]
    days = {}
    for T in ev:
        assert T + 70 * 60000 < END
        for t in (T - 600000, T + 70 * 60000):
            days.setdefault(str(np.datetime64(t, "ms"))[:10], set()).add(T)
    t0 = time.time()
    for k, day in enumerate(sorted(days)):
        out = os.path.join(OUT, f"{SYM}_{day}.npz")
        if os.path.exists(out):
            continue
        zp, s = fetch(day)
        if zp is None:
            print("MISS", day, s, flush=True); continue
        a = parse(zp)
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        keep = np.zeros(len(t), bool)
        for T in days[day]:
            keep |= (t >= T - 600000) & (t <= T + 70 * 60000)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]
        last[sec[ch]] = a[ch, 0]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            sec_p=last, sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(days)} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
