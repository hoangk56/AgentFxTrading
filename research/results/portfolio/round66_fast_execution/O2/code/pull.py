"""Stream O2 pull (adapted from round65 A2/code/pull.py). data.binance.vision futures/um:
  daily aggTrades for each event's alt and BTCUSDT on the UTC days holding [N - 10 min, N + 30 min] and [X - 10 min, X + 5 min];
  monthly 1m klines (alt, BTCUSDT) for the event months (random benchmark).
Each zip goes to an empty tmp folder, is parsed and deleted. Kept per (symbol, day) in research/data/okx_bybit_notice/npz:
trades (t ms, price, qty, buyer_maker) inside the windows only. Klines: kl/<SYM>_<YYYY-MM>.npz (open time ms, open).
Usage: python -I pull.py alt|btc|klines   (downloads are untrusted data)."""
import csv, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); KL = os.path.join(D, "kl"); TMP = os.path.join(D, "tmp_" + (sys.argv[1] if len(sys.argv) > 1 else "x"))
for p in (OUT, KL, TMP):
    os.makedirs(p, exist_ok=True)
END = 1735689600000  # 2025-01-01: never request anything on or after it
EV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "events_s.csv")


def day(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


def load_events():
    ev = [e for e in csv.DictReader(open(EV)) if e["dup"] == "0"]
    for e in ev:
        e["N"] = int(e["N"]); e["X"] = int(e["X"])
        assert e["X"] + 300000 < END and e["N"] < END
    return ev


def windows(e):
    return [(e["N"] - 600000, e["N"] + 1800000), (e["X"] - 600000, e["X"] + 300000)]


def fetch(url, zp):
    for att in range(4):
        r, s = net.opener(url, gap=0.3)
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


def read_csv(zp, cols):
    with zipfile.ZipFile(zp) as z:
        raw = z.read(z.namelist()[0])
    os.remove(zp)
    raw = raw.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    return np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=cols, dtype=np.float64, ndmin=2)


def trades(which):
    ev = load_events(); jobs = {}
    for e in ev:
        sym = "BTCUSDT" if which == "btc" else e["perp"]
        for a, b in windows(e):
            for dd in {day(a), day(b)}:
                jobs.setdefault((sym, dd), []).append((a, b))
    t0 = time.time()
    for k, ((sym, dd), win) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))):
        out = os.path.join(OUT, f"{sym}_{dd}.npz")
        if os.path.exists(out):
            continue
        assert dd <= "2024-12-31"
        url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{dd}.zip"
        zp, s = fetch(url, os.path.join(TMP, f"{sym}-{dd}.zip"))
        if zp is None:
            print("MISS", sym, dd, s, flush=True); continue
        a = read_csv(zp, (1, 2, 5, 6))
        t = a[:, 2]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        keep = np.zeros(len(t), bool)
        for a_, b_ in win:
            keep |= (t >= a_) & (t <= b_)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8), n_all=len(t))
        print(f"{k+1}/{len(jobs)} {sym} {dd} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


def klines():
    ev = load_events(); jobs = set()
    for e in ev:
        m = day(e["N"])[:7]
        jobs.add((e["perp"], m)); jobs.add(("BTCUSDT", m))
    for k, (sym, m) in enumerate(sorted(jobs)):
        out = os.path.join(KL, f"{sym}_{m}.npz")
        if os.path.exists(out):
            continue
        assert m <= "2024-12"
        url = f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1m/{sym}-1m-{m}.zip"
        zp, s = fetch(url, os.path.join(TMP, f"{sym}-{m}.zip"))
        if zp is None:
            print("MISS", sym, m, s, flush=True); continue
        a = read_csv(zp, (0, 1))
        np.savez_compressed(out, t=a[:, 0].astype(np.int64), o=a[:, 1])
        print(f"kl {k+1}/{len(jobs)} {sym} {m} rows {len(a)}", flush=True)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "klines":
        klines()
    else:
        trades(w)
    os.rmdir(TMP) if not os.listdir(TMP) else None
