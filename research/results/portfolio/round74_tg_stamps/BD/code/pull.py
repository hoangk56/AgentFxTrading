"""Stream BD: per-second price arrays for (venue, symbol, day), built from tick files and kept compact.
 venue 'bu' = Binance USDT-M (data.binance.vision futures/um daily aggTrades), 'bs' = Binance spot (spot daily
 aggTrades), 'by' = Bybit linear (public.bybit.com/trading/<SYM>/<SYM><day>.csv.gz).
Saved: research/data/binance_delist_tg/sec/<venue>_<SYM>_<day>.npz with, per second of the UTC day,
 last (last trade price at or before the end of the second, ffilled), lo / hi (min / max trade price inside the
 second, NaN if none), n (trades). Zips are written to an empty tmp folder, parsed, and deleted.
Run with `python -I` (downloads are untrusted data). Every day requested is <= 2024-12-31 (net.guard)."""
import gzip, io, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

SEC = os.path.join(net.D, "sec"); TMP = os.path.join(net.D, "tmp")
os.makedirs(SEC, exist_ok=True); os.makedirs(TMP, exist_ok=True)


def url(v, sym, day):
    if v == "bu":
        return f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    if v == "bs":
        return f"https://data.binance.vision/data/spot/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    return f"https://public.bybit.com/trading/{sym}/{sym}{day}.csv.gz"


def path(v, sym, day):
    return os.path.join(SEC, f"{v}_{sym}_{day}.npz")


def exists(v, sym, day):
    """HEAD check; cached as an empty marker file when missing."""
    if os.path.exists(path(v, sym, day)) or os.path.exists(path(v, sym, day) + ".ok"):
        return True
    miss = path(v, sym, day) + ".miss"
    if os.path.exists(miss):
        return False
    r, s = net.opener(url(v, sym, day), method="HEAD")
    net.log(url(v, sym, day), s, 0, "HEAD")
    if r is not None:
        r.close(); open(path(v, sym, day) + ".ok", "w").close(); return True
    if s == 404:
        open(miss, "w").close()
    return False


def ticks(v, raw):
    """-> (t ms int64, price float64)"""
    if v == "by":
        txt = gzip.decompress(raw)
        lines = txt.split(b"\n")
        hdr = lines[0].split(b",")
        it, ip = hdr.index(b"timestamp"), hdr.index(b"price")
        a = np.loadtxt(io.BytesIO(b"\n".join(lines[1:])), delimiter=",", usecols=(it, ip), dtype=np.float64, ndmin=2)
        t = np.floor(a[:, 0] * 1000).astype(np.int64); p = a[:, 1]
    else:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            b = z.read(z.namelist()[0])
        b = b.replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
        if not b[:1].isdigit():
            b = b[b.index(b"\n") + 1:]
        a = np.loadtxt(io.BytesIO(b), delimiter=",", usecols=(1, 5), dtype=np.float64, ndmin=2)
        t = a[:, 1]
        if len(t) and t.max() > 1e14:
            t = np.floor(t / 1000)
        t = t.astype(np.int64); p = a[:, 0]
    o = np.argsort(t, kind="stable")
    return t[o], p[o]


def build(v, sym, day):
    out = path(v, sym, day)
    if os.path.exists(out):
        return True
    if os.path.exists(out + ".miss"):
        return False
    u = url(v, sym, day)
    for att in range(4):
        r, s = net.opener(u)
        if r is None:
            if s == 404:
                open(out + ".miss", "w").close()
            return False
        try:
            raw = r.read(); r.close(); net.log(u, s, len(raw), "GET"); break
        except Exception as ex:  # read timeout mid-stream: log and retry
            net.log(u, "ERR:" + type(ex).__name__, 0, "GET partial"); r.close(); raw = None
    if raw is None:
        return False
    t, p = ticks(v, raw); del raw
    d0 = int(np.datetime64(day, "ms").astype(np.int64))
    sec = ((t - d0) // 1000).clip(0, 86399)
    n = np.bincount(sec, minlength=86400).astype(np.int32)
    lo = np.full(86400, np.nan); hi = np.full(86400, np.nan); last = np.full(86400, np.nan)
    np.fmin.at(lo, sec, p); np.fmax.at(hi, sec, p)
    ch = np.r_[sec[1:] != sec[:-1], True]
    last[sec[ch]] = p[ch]
    idx = np.where(np.isfinite(last), np.arange(86400), 0); np.maximum.accumulate(idx, out=idx)
    last = np.where(np.isfinite(last[idx]), last[idx], np.nan)
    np.savez_compressed(out, last=last, lo=lo, hi=hi, n=n, d0=d0)
    return True


if __name__ == "__main__":
    v, sym, day = sys.argv[1:4]
    print(build(v, sym, day))
