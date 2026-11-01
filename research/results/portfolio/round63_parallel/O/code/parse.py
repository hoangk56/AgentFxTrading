"""Stream O: parse the metrics zips into hourly arrays on the round 63 C hour axis (instant h = hours since H0).
Run with `python -I parse.py`. For instant t: OIh[t] = sum_open_interest at stamp t-5m; TPh / GAh / TKh = mean over the
12 stamps t-60m..t-5m of top-position L/S, global-account L/S and log(taker buy/sell) (>= 10 valid stamps).
Days >= 2025-01-01 are refused."""
import csv, io, os, sys, zipfile
from datetime import datetime, timezone
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import univ  # noqa: E402
from univ import xs  # noqa: E402

OUT = os.path.join(xs.R, "data", "binance_metrics")
RAW = os.path.join(OUT, "raw")
M5 = 300000


def fnum(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except ValueError:
        return np.nan


def main():
    syms = list(np.load(xs.CACHE)["syms"])
    n, NH = len(syms), xs.NH
    nm = (NH + 1) * 12
    oi = {}
    fields = {}
    cov = np.zeros((n, (xs.END - xs.H0) // xs.DAY), dtype=bool)
    OIh = np.full((n, NH + 1), np.nan)
    TPh = np.full((n, NH + 1), np.nan)
    GAh = np.full((n, NH + 1), np.nan)
    TKh = np.full((n, NH + 1), np.nan)
    bad = 0
    for s in sorted(os.listdir(RAW)):
        if s not in syms:
            continue
        i = syms.index(s)
        files = sorted(f for f in os.listdir(os.path.join(RAW, s)) if f.endswith(".zip"))
        if not files:
            continue
        a = np.full((4, nm), np.nan)   # oi, top position, global account, taker
        for fn in files:
            try:
                z = zipfile.ZipFile(os.path.join(RAW, s, fn))
                txt = z.read(z.namelist()[0]).decode("utf-8", "replace")
            except Exception:
                bad += 1
                continue
            rows = list(csv.reader(io.StringIO(txt)))
            for r in rows[1:]:
                if len(r) < 8:
                    continue
                try:
                    ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000
                except ValueError:
                    continue
                if ts >= xs.END or ts < xs.H0:
                    continue
                m = int(round((ts - xs.H0) / M5))
                if m >= nm:
                    continue
                a[0, m] = fnum(r[2])
                a[1, m] = fnum(r[5])
                a[2, m] = fnum(r[6])
                tk = fnum(r[7])
                a[3, m] = np.log(tk) if tk > 0 else np.nan
            d = int((datetime.strptime(fn[-14:-4], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000 - xs.H0) // xs.DAY)
            assert d < cov.shape[1]
            cov[i, d] = True
        OIh[i, 1:] = a[0, 11::12][:NH]           # stamp 12h-1 = instant h minus 5 min
        blk = a[1:, :].reshape(3, NH + 1, 12)   # block h = stamps 12h..12h+11 = instant h+1 window
        cnt = np.sum(~np.isnan(blk), axis=2)
        with np.errstate(invalid="ignore"):
            mean = np.nanmean(blk, axis=2)
        mean = np.where(cnt >= 10, mean, np.nan)
        TPh[i, 1:], GAh[i, 1:], TKh[i, 1:] = mean[0, :NH], mean[1, :NH], mean[2, :NH]
    np.savez_compressed(os.path.join(OUT, "hourly.npz"), OIh=OIh, TPh=TPh, GAh=GAh, TKh=TKh, cov=cov)
    print("parsed; bad zips", bad, "coin-days", int(cov.sum()))


if __name__ == "__main__":
    import warnings
    warnings.simplefilter("ignore")
    main()
