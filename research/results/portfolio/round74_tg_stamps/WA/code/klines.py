"""Stream WA: Binance USDT-M perp 1-minute klines (BTCUSDT, ETHUSDT) 2020-01..2024-12 from data.binance.vision.
Monthly zips land in an empty tmp folder, are parsed (numbers only) and deleted. Output research/data/whale_alert/
k1m_<SYM>.npz with t (open time ms, int64), o, c (float64). Nothing on or after 2025-01-01 is requested.
Requests logged to research/data/whale_alert/requests.log. Run with python -I."""
import io, os, sys, time, zipfile, urllib.request, urllib.error, datetime as dt
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/whale_alert"
TMP = os.path.join(D, "tmp_klines"); os.makedirs(TMP, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
END = 1735689600000


def log(url, s, n):
    LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t{s}\t{n}\n")


def get(url):
    for att in range(5):
        time.sleep(0.3)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60)
            b = r.read(); log(url, r.status, len(b)); return b
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1)); continue
            return None
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0); time.sleep(5)
    return None


def main():
    for sym in ("BTCUSDT", "ETHUSDT"):
        out = os.path.join(D, f"k1m_{sym}.npz")
        if os.path.exists(out):
            continue
        parts = []
        for y in range(2020, 2025):
            for m in range(1, 13):
                url = f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip"
                b = get(url)
                if b is None:
                    print("MISS", url, flush=True); continue
                zp = os.path.join(TMP, "k.zip"); open(zp, "wb").write(b)
                with zipfile.ZipFile(zp) as z:
                    raw = z.read(z.namelist()[0])
                os.remove(zp)
                if not raw[:1].isdigit():
                    raw = raw[raw.index(b"\n") + 1:]
                a = np.loadtxt(io.BytesIO(raw), delimiter=",", usecols=(0, 1, 4), dtype=np.float64, ndmin=2)
                parts.append(a)
                print(sym, y, m, len(a), flush=True)
        a = np.concatenate(parts)
        t = a[:, 0].astype(np.int64)
        if t.max() > 1e14:
            t = t // 1000
        o = np.argsort(t, kind="stable"); t = t[o]; a = a[o]
        keep = (t < END) & np.r_[True, t[1:] != t[:-1]]
        np.savez_compressed(out, t=t[keep], o=a[keep, 1], c=a[keep, 2])
        print(sym, "saved", keep.sum(), flush=True)


if __name__ == "__main__":
    main()
