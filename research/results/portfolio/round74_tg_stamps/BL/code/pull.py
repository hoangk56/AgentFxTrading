"""Stream BL: pull one daily trade file per (source, symbol, day), keep trades in the event windows plus a per-second
day summary (first / high / low / last price, count), delete the download. Sources:
  bspot  data.binance.vision spot daily aggTrades     bum  data.binance.vision futures/um daily aggTrades
  bybit  public.bybit.com/trading daily dumps        okx  static.okx.com daily trade dumps
Downloads are untrusted data: parsed as numbers only, run with python -I. Nothing on or after 2025-01-01 is requested.
Usage (module): get(src, sym, day, windows) -> path of the npz (cached)."""
import gzip, io, os, sys, time, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

OUT = os.path.join(net.D, "npz"); TMP = os.path.join(net.D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
FMT = open(os.path.join(net.D, "format_check.txt"), "a", buffering=1)


def url_of(src, sym, day):
    if src == "bspot":
        return f"https://data.binance.vision/data/spot/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    if src == "bum":
        return f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    if src == "bybit":
        return f"https://public.bybit.com/trading/{sym}/{sym}{day}.csv.gz"
    if src == "okx":
        d = day.replace("-", "")
        return f"https://static.okx.com/cdn/okex/traderecords/trades/daily/{d}/{sym}-trades-{day}.zip"
    raise ValueError(src)


def download(url, fn):
    for att in range(4):
        r, s = net.opener(url)
        if r is None:
            return None, s
        n = 0
        try:
            with open(fn, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); n += len(b)
            r.close(); net.log(url, s, n, "GET")
            return fn, s
        except Exception as ex:
            net.log(url, "ERR:" + type(ex).__name__, n, "GET partial")
            r.close(); os.remove(fn); time.sleep(10 * (att + 1))
    return None, "fail"


def _num(raw):
    return raw.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")


def parse(src, fn, sym, day):
    """Returns array columns t_ms, price, qty, taker_buy (1 / 0)."""
    if src in ("bspot", "bum"):
        with zipfile.ZipFile(fn) as z:
            raw = z.read(z.namelist()[0])
        raw = _num(raw)
        if not raw[:1].isdigit():
            raw = raw[raw.index(b"\n") + 1:]
        a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(5, 1, 2, 6), dtype=np.float64, ndmin=2)
        t = a[:, 0]
        if t.max() > 1e14:
            t = np.floor(t / 1000)
        a[:, 0] = t; a[:, 3] = 1 - a[:, 3]  # buyer is maker -> taker sold
    elif src == "bybit":
        with gzip.open(fn, "rb") as z:
            raw = z.read()
        head, rest = raw.split(b"\n", 1)
        cols = head.decode().strip().split(",")
        it, isd, iq, ip = cols.index("timestamp"), cols.index("side"), cols.index("size"), cols.index("price")
        rest = rest.replace(b",Buy,", b",1,").replace(b",Sell,", b",0,")
        a = np.loadtxt(io.BytesIO(rest), delimiter=",", usecols=(it, ip, iq, isd), dtype=np.float64, ndmin=2)
        a[:, 0] = np.round(a[:, 0] * 1000) if a[:, 0].max() < 1e11 else np.round(a[:, 0])
        print(f"FORMAT bybit {sym} {day} cols={cols}", file=FMT)
    elif src == "okx":
        with zipfile.ZipFile(fn) as z:
            raw = z.read(z.namelist()[0])
        txt = raw.decode("utf-8", "replace").splitlines()
        head = txt[0].split(",")
        print(f"FORMAT okx {sym} {day} head={head} first={txt[1][:120] if len(txt) > 1 else ''}", file=FMT)
        low = [h.strip().lower() for h in head]
        def ix(*names):
            for nm in names:
                for k, h in enumerate(low):
                    if nm in h:
                        return k
            raise KeyError(names)
        it, ip, iq, isd = ix("created_time", "time", "ts"), ix("price", "px"), ix("size", "sz", "amount"), ix("side")
        rows = []
        for line in txt[1:]:
            c = line.split(",")
            if len(c) <= max(it, ip, iq, isd):
                continue
            rows.append((float(c[it]), float(c[ip]), float(c[iq]), 1.0 if c[isd].strip().lower() == "buy" else 0.0))
        a = np.array(rows, dtype=np.float64).reshape(-1, 4)
        if len(a) and a[:, 0].max() < 1e11:
            a[:, 0] *= 1000
    os.remove(fn)
    return a


def get(src, sym, day, windows):
    out = os.path.join(OUT, f"{src}_{sym}_{day}.npz")
    if os.path.exists(out):
        return out
    d0 = int(np.datetime64(day, "ms").astype(np.int64))
    if src == "okx":  # OKX daily files are UTC+8 days: [date - 8 h, date + 16 h) UTC
        d0 -= 8 * 3600000
    assert d0 + 86400000 <= net.END_MS, "HOLD guard"
    url = url_of(src, sym, day)
    fn, s = download(url, os.path.join(TMP, os.path.basename(url)))
    if fn is None:
        np.savez_compressed(out, missing=1, status=str(s)); return out
    a = parse(src, fn, sym, day)
    o = np.argsort(a[:, 0], kind="stable"); a = a[o]
    t = a[:, 0].astype(np.int64)
    if len(t):
        assert t.min() >= d0 - 2000 and t.max() < d0 + 86400000 + 2000, (sym, day, t.min(), t.max())
    keep = np.zeros(len(t), bool)
    for a_, b_ in windows:
        keep |= (t >= a_) & (t <= b_)
    sec = ((t - d0) // 1000).clip(0, 86399)
    n = np.bincount(sec, minlength=86400).astype(np.int32)
    hi = np.full(86400, np.nan); lo = np.full(86400, np.nan); fi = np.full(86400, np.nan); la = np.full(86400, np.nan)
    if len(t):
        np.fmax.at(hi, sec, a[:, 1]); np.fmin.at(lo, sec, a[:, 1])
        st = np.r_[True, sec[1:] != sec[:-1]]; en = np.r_[sec[1:] != sec[:-1], True]
        fi[sec[st]] = a[st, 1]; la[sec[en]] = a[en, 1]
    np.savez_compressed(out, t=t[keep], p=a[keep, 1], q=a[keep, 2], buy=a[keep, 3].astype(np.int8),
                        hi=hi, lo=lo, fi=fi, la=la, n=n, d0=d0, n_all=len(t), missing=0)
    return out
