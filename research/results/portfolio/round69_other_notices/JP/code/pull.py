"""Stream JP: pull data.binance.vision futures/um daily aggTrades (A2's pull.py logic) for each event's alt perp and
BTCUSDT on the notice day (window [N - 10 min, N + 30 min]) and on the trading-start day (window [L - 10 min, L + 5 min]).
Each zip is streamed to an empty tmp folder, parsed with numpy, and deleted; only window trades are kept in
research/data/jp_notices/npz/<SYM>_<day>.npz. Nothing on or after 2025-01-01 is ever requested. Run with `python -I`."""
import io, os, sys, time, zipfile
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
import net
from events import load_events

OUT = os.path.join(net.D, "npz"); TMP = os.path.join(net.D, "tmp")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
END = 1735689600000


def dstr(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


def _ts(raw, pos):  # transact_time of the first full line starting at or after byte pos
    if pos > 0:
        pos = raw.find(b"\n", pos - 1) + 1
    if pos <= 0 or pos >= len(raw):
        return pos, None
    e = raw.find(b"\n", pos)
    f = raw[pos:e if e > 0 else len(raw)].split(b",")
    v = int(f[5])
    return pos, (v // 1000 if v > 1e14 else v)


def offset(raw, T):  # byte offset of the first line with time >= T (rows are time-ordered by agg id)
    lo, hi = 0, len(raw)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        p, v = _ts(raw, mid)
        if v is None or v >= T:
            hi = mid
        else:
            lo = mid
    p, _ = _ts(raw, hi)
    return p


def parse(zp, win):
    """Only the window lines are parsed (A2 parsed whole days; same columns, same values)."""
    with zipfile.ZipFile(zp) as z:
        raw = z.read(z.namelist()[0])
    os.remove(zp)
    if not raw[:1].isdigit():
        raw = raw[raw.index(b"\n") + 1:]
    n_all = raw.count(b"\n")
    merged = []  # union of the windows, so overlapping windows (several events on a day) give no duplicate rows
    for a_, b_ in sorted(win):
        if merged and a_ - 2000 <= merged[-1][1] + 2000:
            merged[-1][1] = max(merged[-1][1], b_)
        else:
            merged.append([a_, b_])
    parts = []
    for a_, b_ in merged:
        s, e = offset(raw, a_ - 2000), offset(raw, b_ + 2000)
        chunk = raw[s:e].replace(b"true", b"1").replace(b"false", b"0").replace(b"True", b"1").replace(b"False", b"0")
        if chunk.strip():
            parts.append(np.loadtxt(io.BytesIO(chunk), delimiter=",", usecols=(1, 2, 5, 6), dtype=np.float64, ndmin=2))
    a = np.concatenate(parts) if parts else np.zeros((0, 4))
    return a, n_all


def main():
    jobs = {}
    for e in load_events():
        for a_, b_ in ((e["N"] - 600000, e["N"] + 1800000), (e["L"] - 600000, e["L"] + 300000)):
            assert dstr(a_) == dstr(b_) and b_ < END, (e["coin"], a_, b_)
            for sym in (e["perp"], "BTCUSDT"):
                jobs.setdefault((sym, dstr(a_)), []).append((a_, b_))
    t0 = time.time()
    for k, ((sym, day), win) in enumerate(sorted(jobs.items(), key=lambda x: (x[0][1], x[0][0]))):
        out = os.path.join(OUT, f"{sym}_{day}.npz")
        if os.path.exists(out):
            continue
        url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
        zp = os.path.join(TMP, f"{sym}-{day}.zip")
        s = net.stream(url, zp)
        if s != 200:
            print("MISS", sym, day, s, flush=True); continue
        a, n_all = parse(zp, win)
        t = a[:, 2]
        if len(t) and t.max() > 1e14:
            t = np.floor(t / 1000)
        o = np.argsort(t, kind="stable"); a = a[o]; t = t[o].astype(np.int64)
        keep = np.zeros(len(t), bool)
        for a_, b_ in win:
            keep |= (t >= a_) & (t <= b_)
        np.savez_compressed(out, t=t[keep], p=a[keep, 0], q=a[keep, 1].astype(np.float32), m=a[keep, 3].astype(np.int8),
                            n_all=n_all)
        print(f"{k+1}/{len(jobs)} {sym} {day} rows {len(t)} kept {keep.sum()} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
