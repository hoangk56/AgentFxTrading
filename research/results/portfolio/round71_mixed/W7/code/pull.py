"""Stream W7: pull trade files for each hedgeable listing event and keep compact 1 s series.
Usage: python -I pull.py spot|bnperp|byperp
 - spot:   data.binance.vision spot daily aggTrades of the listing day and the next 1-2 days.
 - bnperp: data.binance.vision futures/um daily aggTrades of the Binance reference perp, same days.
 - byperp: public.bybit.com/trading daily dumps of the Bybit reference perp, same days.
Each zip / gz goes to an empty tmp folder, is parsed (python -I, text treated as data) and deleted.
Kept per (event, instrument) in research/data/listing_window/npz/<SYM>_<LDAY>_<leg>.npz, for the window
[day0 00:00, day0 + 2 d 00:00) cut at the window end and at ts < 2025-01-01, one row per second of:
  last  : last trade price in the second (NaN if none)
  fb/fs : first taker-buy / taker-sell price in the second (NaN if none)
  lb/ls : last taker-buy / taker-sell price in the second
  nb/ns : taker-buy / taker-sell quote notional in the second (float32)
plus t_first (ms of the first trade of the instrument in the window) and n_all.
Day 3 is pulled only when the listing clock is after 23:00 UTC (exit window crosses the second midnight)."""
import csv, gzip, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

D = net.D
OUT = os.path.join(D, "npz")
TMP = os.path.join(D, "tmp", sys.argv[1] if len(sys.argv) > 1 else "x")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
END = 1735689600000  # 2025-01-01 00:00 UTC: never requested, every series cut before it
DAYMS = 86400000
EV = os.path.join(D, "meta", "pull_list.csv")


def dstr(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


def download(url, path):
    for att in range(4):
        r, s = net.opener(url)
        if r is None:
            return None, s
        n = 0
        try:
            with open(path, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); n += len(b)
            r.close(); net.log(url, s, n, "GET")
            return path, s
        except Exception as ex:
            net.log(url, "ERR:" + type(ex).__name__, n, "GET partial")
            r.close()
            if os.path.exists(path):
                os.remove(path)
            time.sleep(10 * (att + 1))
    return None, "fail"


def parse_binance(path):
    """-> t ms (int64), price, qty, taker_buy (1 if the buyer was the taker)."""
    with zipfile.ZipFile(path) as z:
        raw = z.read(z.namelist()[0])
    os.remove(path)
    raw = raw.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    if not raw.strip():
        return None
    a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(1, 2, 5, 6), dtype=np.float64, ndmin=2)
    t = a[:, 2]
    if np.nanmax(t) > 1e14:
        t = np.floor(t / 1000)
    return t.astype(np.int64), a[:, 0], a[:, 1], (a[:, 3] < 0.5).astype(np.int8)


def parse_bybit(path):
    with gzip.open(path, "rb") as z:
        raw = z.read()
    os.remove(path)
    head, rest = raw.split(b"\n", 1)
    cols = head.decode().strip().split(",")
    i_t, i_s, i_q, i_p = cols.index("timestamp"), cols.index("side"), cols.index("size"), cols.index("price")
    rest = rest.replace(b",Buy,", b",1,").replace(b",Sell,", b",0,")
    a = np.loadtxt(io.BytesIO(rest), delimiter=",", usecols=(i_t, i_s, i_q, i_p), dtype=np.float64, ndmin=2)
    t = a[:, 0]
    t = np.floor(t * 1000) if np.nanmax(t) < 1e11 else (np.floor(t / 1000) if np.nanmax(t) > 1e14 else t)
    return t.astype(np.int64), a[:, 3], a[:, 2], (a[:, 1] > 0.5).astype(np.int8)


def per_second(t, p, q, tb, w0, nsec):
    o = np.argsort(t, kind="stable"); t, p, q, tb = t[o], p[o], q[o], tb[o]
    k = (t >= w0) & (t < w0 + nsec * 1000)
    t, p, q, tb = t[k], p[k], q[k], tb[k]
    sec = (t - w0) // 1000
    out = {}
    last = np.full(nsec, np.nan); last[sec] = p  # later writes win -> last trade of the second
    out["last"] = last
    for nm, m in (("b", tb == 1), ("s", tb == 0)):
        s_, p_ = sec[m], p[m]
        f = np.full(nsec, np.nan); f[s_[::-1]] = p_[::-1]  # first trade of the second
        l = np.full(nsec, np.nan); l[s_] = p_
        n = np.bincount(s_, weights=p_ * q[m], minlength=nsec).astype(np.float32)
        out["f" + nm], out["l" + nm], out["n" + nm] = f, l, n
    return out, (int(t[0]) if len(t) else -1), len(t)


def main():
    leg = sys.argv[1]
    rows = list(csv.DictReader(open(EV)))
    t0 = time.time()
    for k, e in enumerate(rows):
        if leg == "spot":
            sym = e["sym"]
        elif leg == "bnperp":
            sym = e["bn_perp"]
        else:
            sym = e["by_perp"]
        if not sym:
            continue
        d0 = int(np.datetime64(e["L_day"], "ms").astype(np.int64))
        ndays = 3 if e.get("late", "0") == "1" else 2
        w0 = d0; nsec = ndays * 86400
        assert d0 + ndays * DAYMS <= END + 0, e  # last requested day is <= 2024-12-31
        out = os.path.join(OUT, f"{e['sym']}_{e['L_day']}_{leg}.npz")
        if os.path.exists(out):
            continue
        T, P, Q, B = [], [], [], []
        miss = []
        for i in range(ndays):
            day = dstr(d0 + i * DAYMS)
            assert day <= "2024-12-31"
            if leg == "byperp":
                url = f"https://public.bybit.com/trading/{sym}/{sym}{day}.csv.gz"
                pth, s = download(url, os.path.join(TMP, f"{sym}{day}.csv.gz"))
                r = parse_bybit(pth) if pth else None
            else:
                base = "spot" if leg == "spot" else "futures/um"
                url = f"https://data.binance.vision/data/{base}/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
                pth, s = download(url, os.path.join(TMP, f"{sym}-{day}.zip"))
                r = parse_binance(pth) if pth else None
            if r is None:
                miss.append(day); continue
            T.append(r[0]); P.append(r[1]); Q.append(r[2]); B.append(r[3])
        if not T:
            print("MISS", leg, e["sym"], sym, miss, flush=True)
            np.savez_compressed(out, missing=1); continue
        t, p, q, b = (np.concatenate(x) for x in (T, P, Q, B))
        assert t.max() < END
        ser, tf, n = per_second(t, p, q, b, w0, nsec)
        np.savez_compressed(out, w0=w0, t_first=tf, n_all=n, missing_days=",".join(miss), sym=sym,
                            **{kk: (v.astype(np.float32) if kk.startswith("n") else v) for kk, v in ser.items()})
        print(f"{k + 1}/{len(rows)} {leg} {e['sym']} {sym} rows {n} miss {miss} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
