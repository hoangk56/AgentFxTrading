"""Stream A4: pull public.bybit.com daily trade dumps (alt and BTCUSDT) for each event's N day and L day. The
fetch / cut logic follows round66 A3/code/pull.py (only the source and the format differ). Each gz is streamed to an
empty tmp folder, parsed, and deleted. Kept per (symbol, day) in research/data/upbit_bybit_notice/npz: trades in
[N - 10 min, N + 30 min] and [L - 10 min, L + 5 min] (t ms, price, size, buy = 1 if the taker bought) plus a 1 s
last-price / count series of the day. Dump format checked on read (header, timestamp unit, side values). Run with -I."""
import csv, gzip, io, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz"); TMP = os.path.join(D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
EV = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A4/events.csv"
END = 1735689600000
FMT = open(os.path.join(D, "format_check.txt"), "a")


def day_of(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


def load_events():
    out = []
    for r in csv.DictReader(open(EV)):
        e = dict(r); e["N"] = int(r["N"]); e["L"] = int(r["L"])
        e["day"] = r["N_utc"][:10]; e["year"] = r["N_utc"][:4]; e["Lday"] = day_of(e["L"])
        assert e["N"] < END and e["L"] + 300000 < END
        out.append(e)
    return out


def fetch(sym, day):
    url = f"https://public.bybit.com/trading/{sym}/{sym}{day}.csv.gz"
    zp = os.path.join(TMP, f"{sym}-{day}.csv.gz")
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


def parse(zp, sym, day):
    with gzip.open(zp, "rb") as z:
        raw = z.read()
    os.remove(zp)
    head, rest = raw.split(b"\n", 1)
    cols = head.decode().strip().split(",")
    first = rest[:rest.index(b"\n")].decode()
    i_t, i_s, i_q, i_p = cols.index("timestamp"), cols.index("side"), cols.index("size"), cols.index("price")
    sides = set(rest[:2000000].split(b"\n")[0:1])
    rest = rest.replace(b",Buy,", b",1,").replace(b",Sell,", b",0,")
    a = np.loadtxt(io.BytesIO(rest), delimiter=",", usecols=(i_t, i_s, i_q, i_p), dtype=np.float64, ndmin=2,
                   converters=None)
    print(f"FORMAT {sym} {day} cols={cols} first={first} ts_range=({a[:,0].min()},{a[:,0].max()}) side_vals={sorted(set(np.unique(a[:,1]).tolist()))}", file=FMT, flush=True)
    return a


def main():
    evs = load_events()
    jobs = {}
    for e in evs:
        for day in sorted({e["day"], e["Lday"]}):
            for sym in (e["bsym"], "BTCUSDT"):
                jobs.setdefault((sym, day), []).append(e)
    t0 = time.time()
    for k, ((sym, day), ev) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))):
        out = os.path.join(OUT, f"{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        zp, s = fetch(sym, day)
        if zp is None:
            print("MISS", sym, day, s, flush=True); continue
        a = parse(zp, sym, day)
        t = a[:, 0]
        t = np.round(t * 1000) if t.max() < 1e11 else np.round(t)  # seconds -> ms
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        d0 = int(np.datetime64(day, "ms").astype(np.int64))
        assert t.min() >= d0 - 1000 and t.max() < d0 + 86400000 + 1000 and t.max() < END
        keep = np.zeros(len(t), bool)
        for e in ev:
            keep |= (t >= e["N"] - 600000) & (t <= e["N"] + 1800000)
            keep |= (t >= e["L"] - 600000) & (t <= e["L"] + 300000)
        sec = ((t - d0) // 1000).clip(0, 86399)
        cnt = np.bincount(sec, minlength=86400).astype(np.int32)
        last = np.full(86400, np.nan)
        ch = np.r_[sec[1:] != sec[:-1], True]
        last[sec[ch]] = a[ch, 3]
        idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
        last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
        np.savez_compressed(out, t=t[keep], p=a[keep, 3], q=a[keep, 2].astype(np.float64), buy=a[keep, 1].astype(np.int8),
                            sec_p=last.astype(np.float64), sec_n=cnt, d0=d0, n_all=len(t))
        print(f"{k+1}/{len(jobs)} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
